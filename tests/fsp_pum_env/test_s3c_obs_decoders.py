from pathlib import Path

import numpy as np
import pytest

from src.fsp_pum_env.battery.base import PrefixEvent, load_design, validate_prediction
from src.fsp_pum_env.battery.obs_decoders import (
    DECODER_MEMBER_NAMES,
    F2_NGRAM_VOCABULARY_SIZE,
    S3C_COST_CLASSES,
    S3C_CPU_HOUR_LIMIT,
    S3C_R3_CPU_HOUR_LIMIT,
    build_s3c_r3_runtime_trace,
    build_f2_ngram_vocabulary,
    configure_s3c_single_thread_cpu_environment,
    decoder_grid,
    feature_map_summary,
    gbt_fit_user_ids,
    materialize_prefix_feature_rows_incremental,
    materialize_prefix_feature_rows_naive,
    project_s3c_r2_from_measurements,
    s3c_sweep_config_specs,
    s3c_split_for_user,
    validate_s3c_training_user_id,
    ObsDecoderLogRegPredictor,
    _empty_sweep_aggregators,
    _update_sweep_aggregator,
)
from src.fsp_pum_env.trajectory_sets import TrajectorySetSpec


FROZEN = Path(__file__).resolve().parents[2] / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "frozen_design.json"


def _event(action="task_topic_0", symbol=3, step=0):
    return PrefixEvent(
        action=action,
        observation={"symbol": symbol},
        session_index=0,
        turn_in_session=step,
        step_index=step,
        session_boundary="start" if step == 0 else "none",
    )


def test_s3c_split_rejects_heldout_users_for_all_training_phases():
    assert s3c_split_for_user(0) == "fit"
    assert s3c_split_for_user(639) == "fit"
    assert s3c_split_for_user(640) == "internal_validation"
    assert s3c_split_for_user(799) == "internal_validation"

    with pytest.raises(ValueError, match="heldout"):
        s3c_split_for_user(800)
    with pytest.raises(ValueError, match="heldout"):
        validate_s3c_training_user_id(999, phase="fit")


def test_decoder_grids_match_frozen_addendum_counts_and_names():
    assert DECODER_MEMBER_NAMES == ["obs_decoder_logreg", "obs_decoder_gbt", "obs_decoder_gru"]
    assert len(decoder_grid("obs_decoder_logreg")) == 8
    assert len(decoder_grid("obs_decoder_gbt")) == 8
    assert len(decoder_grid("obs_decoder_gru")) == 8
    assert decoder_grid("obs_decoder_logreg")[0]["features"] == "F1"
    assert decoder_grid("obs_decoder_gbt")[0]["features"] == "F2"


def test_obs_decoder_prefix_only_prediction_format_and_action_conditioning():
    design = load_design(FROZEN)
    actions = tuple(design["evaluation"]["counterfactual_action_set_per_query"])
    predictor = ObsDecoderLogRegPredictor.from_design(design)
    predictor.observe(_event("task_topic_0", 7, 0))
    predictor.observe(_event("probe_0", 11, 1))

    prediction = predictor.predict(actions)

    validate_prediction(prediction, design, actions)
    assert set(prediction) == set(actions)
    assert prediction["task_topic_0"] is not prediction["probe_0"]


def test_f2_vocabulary_is_thresholded_top1024_and_fit_users_only(monkeypatch):
    design = load_design(FROZEN)
    seen_specs = []

    def fake_iter_records(fake_design, spec):
        assert fake_design is design
        seen_specs.append(spec)
        partition = spec.partitions["train"]
        assert partition == {"start_user_id": 0, "count": 640}
        for user_id in range(partition["count"]):
            for step in range(300):
                yield (
                    "train",
                    user_id,
                    {
                        "step_index": step,
                        "session_index": step // 25,
                        "turn_in_session": step % 25,
                        "session_boundary": "start" if step % 25 == 0 else "none",
                        "action": "task_topic_0",
                        "observation": {"symbol": (user_id * 17 + step * 5 + step * step) % 32},
                    },
                    {"user_id": user_id},
                )

    from src.fsp_pum_env.battery import obs_decoders

    monkeypatch.setattr(obs_decoders.trajectory_sets_module, "_iter_records_with_adjudicator", fake_iter_records)
    manifest = {
        "sets": [
            {
                "set_id": "set_00",
                "generation_params": {
                    "set_id": "set_00",
                    "master_seed": 123,
                    "env_mode": "real",
                    "turns_per_user": 300,
                    "logging_policy": {},
                    "partitions": {"train": {"start_user_id": 0, "count": 1000}},
                },
            }
        ]
    }

    vocabulary = build_f2_ngram_vocabulary(design, manifest)

    assert len(seen_specs) == 1
    assert len(vocabulary["ngrams"]) == F2_NGRAM_VOCABULARY_SIZE
    assert vocabulary["fit_user_range"] == [0, 639]
    assert vocabulary["excluded_user_ranges"] == {"internal_validation": [640, 799], "heldout": [800, 999]}
    counts = [entry["pooled_fit_count"] for entry in vocabulary["ngrams"]]
    assert counts == sorted(counts, reverse=True)
    assert min(counts) >= 100


def test_incremental_prefix_features_match_naive_reference_for_f1_and_f2():
    design = load_design(FROZEN)
    actions = tuple(design["evaluation"]["counterfactual_action_set_per_query"])
    alphabet_size = 32
    events = [
        PrefixEvent(
            action=actions[idx % len(actions)],
            observation={"symbol": (idx * 7) % alphabet_size},
            session_index=idx // 30,
            turn_in_session=idx % 30,
            step_index=idx,
            session_boundary="start" if idx % 30 == 0 else "none",
        )
        for idx in range(60)
    ]
    vocabulary = {
        "ngrams": [
            {"key": "1", "symbols": [1], "pooled_fit_count": 120},
            {"key": "1 8", "symbols": [1, 8], "pooled_fit_count": 110},
            {"key": "1 8 15", "symbols": [1, 8, 15], "pooled_fit_count": 100},
        ],
        "sha256": "test-only",
    }

    for features in ("F1", "F2"):
        incremental = materialize_prefix_feature_rows_incremental(
            events,
            actions,
            alphabet_size=alphabet_size,
            vocabulary=vocabulary,
            features=features,
        )
        naive = materialize_prefix_feature_rows_naive(
            events,
            actions,
            alphabet_size=alphabet_size,
            vocabulary=vocabulary,
            features=features,
        )

        np.testing.assert_array_equal(incremental.toarray(), naive.toarray())


def test_feature_map_uses_001b_top1024_f2_dimension():
    design = load_design(FROZEN)
    summary = feature_map_summary(design)
    assert summary["F1"]["dimension"] == 1133
    assert summary["F2"]["ngram_dimension"] == F2_NGRAM_VOCABULARY_SIZE
    assert summary["F2"]["dimension"] == 1133 + F2_NGRAM_VOCABULARY_SIZE


def test_gbt_fit_budget_uses_deterministic_even_half_of_fit_users():
    assert gbt_fit_user_ids() == tuple(range(0, 640, 2))
    assert len(gbt_fit_user_ids()) == 320
    assert 639 not in gbt_fit_user_ids()


def test_projection_v2_uses_six_measured_classes_and_one_time_costs():
    measurements = {
        "logreg_F1": {"fit_plus_validation_wall_clock_seconds": 1.0},
        "logreg_F2": {"fit_plus_validation_wall_clock_seconds": 2.0},
        "gbt": {"fit_plus_validation_wall_clock_seconds": 3.0},
        "gru": {"fit_plus_validation_wall_clock_seconds": 4.0},
        "seq_full": {"fit_plus_validation_wall_clock_seconds": 5.0},
        "seq_W15": {"fit_plus_validation_wall_clock_seconds": 6.0},
    }
    projection = project_s3c_r2_from_measurements(measurements, {"vocabulary_build_seconds": 7.0})

    assert tuple(projection["cost_classes"]) == S3C_COST_CLASSES
    assert projection["config_counts_by_class"] == {
        "logreg_F1": 4,
        "logreg_F2": 4,
        "gbt": 8,
        "gru": 8,
        "seq_full": 8,
        "seq_W15": 8,
    }
    expected_seconds = 10.0 * (4 * 1.0 + 4 * 2.0 + 8 * 3.0 + 8 * 4.0 + 8 * 5.0 + 8 * 6.0) + 7.0
    assert projection["projection_seconds"] == expected_seconds
    assert projection["projection_cpu_hours"] == expected_seconds / 3600.0
    assert projection["decision"] == "projection_within_24_cpu_hours"


def test_r3_runtime_trace_uses_operator_signed_30_cpu_hour_line():
    trace = build_s3c_r3_runtime_trace(
        [
            {
                "member": "obs_decoder_logreg",
                "config_id": "obs_decoder_logreg_cfg00",
                "config_index": 0,
                "wall_clock_seconds": 3600.0,
            },
            {
                "member": "obs_decoder_gbt",
                "config_id": "obs_decoder_gbt_cfg00",
                "config_index": 0,
                "wall_clock_seconds": 29.1 * 3600.0,
            },
        ],
        wall_clock_seconds=7200.0,
    )

    assert S3C_R3_CPU_HOUR_LIMIT == 30.0
    assert trace["cpu_hour_limit"] == 30.0
    assert trace["total_sweep_cpu_hours"] == pytest.approx(30.1)
    assert trace["wall_clock_hours"] == pytest.approx(2.0)
    assert trace["single_thread_accounting"] is True
    assert trace["decision"] == "stop_runtime_exceeds_30_cpu_hours"
    assert trace["cumulative_cpu_hours_trace"][-1]["cumulative_cpu_hours"] == pytest.approx(30.1)


def test_r3_sweep_config_specs_cover_forty_frozen_configs():
    configs = s3c_sweep_config_specs()

    assert len(configs) == 40
    assert len({config["config_id"] for config in configs}) == 40
    assert [config["member"] for config in configs].count("obs_decoder_logreg") == 8
    assert [config["member"] for config in configs].count("obs_decoder_gbt") == 8
    assert [config["member"] for config in configs].count("obs_decoder_gru") == 8
    assert [config["member"] for config in configs].count("seq_full_history_no_action_conditioning") == 8
    assert (
        [config["member"] for config in configs].count(
            "seq_window_with_action_conditioning_W15_no_cross_session_persistence"
        )
        == 8
    )


def test_sweep_aggregator_accounts_full_config_wall_clock_when_available():
    config = decoder_grid("obs_decoder_logreg")[0]
    aggregators = _empty_sweep_aggregators()
    result = {
        "targets": [0, 1],
        "predictions": [0, 1],
        "fit_and_predict_wall_clock_seconds": 2.0,
        "fit_plus_validation_wall_clock_seconds": 5.0,
        "fit_examples": 10,
        "internal_validation_examples": 2,
        "offline_compute_units": 20,
    }

    _update_sweep_aggregator(aggregators, config, result, {"fit_records": 10}, "set_00")

    item = aggregators[config["config_id"]]
    assert item["wall_clock_seconds"] == 5.0
    assert item["set_results"][0]["wall_clock_seconds"] == 5.0
    assert item["set_results"][0]["model_fit_predict_wall_clock_seconds"] == 2.0


def test_single_thread_cpu_environment_is_asserted_in_sweep_entry_path(monkeypatch):
    for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        monkeypatch.delenv(key, raising=False)

    state = configure_s3c_single_thread_cpu_environment()

    assert state["single_thread_accounting"] is True
    assert state["torch_device"] == "cpu"
    assert state["env_threads"] == {
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
    }
    assert state["cpu_hour_limit"] == S3C_CPU_HOUR_LIMIT
