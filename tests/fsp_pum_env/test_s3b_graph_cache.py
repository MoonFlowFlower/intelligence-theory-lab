import json
from pathlib import Path

from src.fsp_pum_env.battery.base import PrefixEvent, load_design, validate_prediction
from src.fsp_pum_env.battery.graph_cache import (
    CountTablePredictor,
    EpisodicTraversalPredictor,
    FsmPlannerPredictor,
    SuccessorMapPredictor,
    TransitionTablePredictor,
    build_graph_cache_alias_report,
    graph_cache_conventions,
)
from src.fsp_pum_env.s3b_artifacts import write_s3b_battery_manifest


FROZEN = Path(__file__).resolve().parents[2] / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "frozen_design.json"


def _event(action, symbol, step):
    return PrefixEvent(
        action=action,
        observation={"symbol": symbol},
        session_index=step // 15,
        turn_in_session=step % 15,
        step_index=step,
        session_boundary="start" if step % 15 == 0 else "none",
    )


def test_graph_cache_family_fits_real_action_conditioned_tables():
    design = load_design(FROZEN)
    actions = tuple(design["evaluation"]["counterfactual_action_set_per_query"])
    train = [
        _event("task_topic_0", 4, 0),
        _event("probe_0", 7, 1),
        _event("task_topic_0", 9, 2),
        _event("task_topic_2", 3, 3),
        _event("task_topic_0", 9, 4),
    ]

    for cls in (
        SuccessorMapPredictor,
        TransitionTablePredictor,
        CountTablePredictor,
        FsmPlannerPredictor,
        EpisodicTraversalPredictor,
    ):
        predictor = cls.from_design(design)
        for event in train:
            predictor.observe(event)

        prediction = predictor.predict(actions)

        validate_prediction(prediction, design, actions)
        assert predictor.distinct_key_count > 0
        assert any(max(distribution) > (1.0 / predictor.alphabet_size) for distribution in prediction.values())


def test_graph_cache_alias_report_declares_key_coverage_without_fitting_heldout():
    design = load_design(FROZEN)
    train = [_event("task_topic_0", 4, 0), _event("probe_0", 7, 1), _event("task_topic_0", 9, 2)]
    heldout = [_event("task_topic_0", 4, 0), _event("probe_0", 8, 1), _event("task_topic_2", 9, 2)]
    predictor = SuccessorMapPredictor.from_design(design)
    for event in train:
        predictor.observe(event)

    report = build_graph_cache_alias_report("successor_map", predictor, train, heldout)

    assert report["member"] == "successor_map"
    assert report["fitting_data_contract"]["fit_partition"] == "train"
    assert report["distinct_key_count"] == predictor.distinct_key_count
    assert report["heldout_key_coverage"]["total_keys"] > 0
    assert report["heldout_records_used_for_fitting"] is False
    assert report["key_construction"] == graph_cache_conventions()["successor_map"]["key_construction"]
    json.dumps(report, sort_keys=True)


def test_s3b_battery_manifest_declares_per_member_fitting_contracts(tmp_path):
    manifest_path = tmp_path / "s3b_battery_manifest.json"

    manifest = write_s3b_battery_manifest(FROZEN, manifest_path)

    assert set(manifest["fitting_data_contracts"]) == set(manifest["implemented_members"])
    assert all(
        contract["fit_partition"] == "train" and contract["regime"] == "LOG-PARITY"
        for contract in manifest["fitting_data_contracts"].values()
    )
    assert json.loads(manifest_path.read_text(encoding="utf-8")) == manifest
