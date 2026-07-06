from __future__ import annotations

import importlib.util
from pathlib import Path
import re
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[2]
BATTERY_RUNNER = ROOT / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "s3d_battery_runner_line30.py"
REGATE_RUNNER = ROOT / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "s3d_part0_cputime_regate_runner.py"
OBS_DECODERS = ROOT / "src" / "fsp_pum_env" / "battery" / "obs_decoders.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixed_units() -> list[dict[str, object]]:
    return [
        {
            "component": "alpha",
            "measured_wall_seconds": 3600.0,
            "measured_process_cpu_seconds": 1800.0,
            "projected_units": 2.0,
            "note": "fixed alpha",
            "timing_source": "test",
            "null_env_units_included": 1.0,
        },
        {
            "component": "beta",
            "measured_wall_seconds": 900.0,
            "measured_process_cpu_seconds": 900.0,
            "projected_units": 4.0,
            "note": "fixed beta",
            "timing_source": "test",
            "null_env_units_included": 0.0,
        },
    ]


def test_t1_shared_projection_function_is_deterministic_and_regate_calls_same_routine(monkeypatch):
    battery = _load_module(BATTERY_RUNNER, "s3d_battery_runner_line30_t1")
    regate = _load_module(REGATE_RUNNER, "s3d_part0_cputime_regate_runner_t1")
    units = _fixed_units()

    direct = battery.project_s3d_part0_cpu_time_units(units, applied_line=30.0)

    assert direct["total_projected_process_cpu_seconds"] == 7200.0
    assert direct["total_projected_wall_seconds"] == 10800.0
    assert direct["total_projected_cpu_hours"] == 2.0
    assert direct["total_projected_wall_hours"] == 3.0
    assert direct["projected_cpu_hours"] == 2.0
    assert direct["gate_relation"] == "within_line"
    assert direct["line_relation"] == "within_line"
    assert direct["components"]["alpha"]["wall_cpu_ratio"] == 2.0
    assert direct["components"]["alpha"]["wall_cpu_ratio_flag_gt_1_25"] is True
    assert direct["wall_cpu_ratio_flag_components"] == ["alpha"]

    calls: list[str] = []
    original = battery.project_s3d_part0_cpu_time_units

    def spy(*args, **kwargs):
        calls.append("called")
        return original(*args, **kwargs)

    monkeypatch.setattr(battery, "project_s3d_part0_cpu_time_units", spy)
    monkeypatch.setattr(regate, "_load_battery_runner", lambda: battery)
    via_regate = regate._project_part0_timing_units(units, 30.0)

    assert calls == ["called"]
    assert via_regate == direct


def test_t2_b1_wall_over_line_cpu_within_line_does_not_stop_but_cpu_over_line_stops():
    battery = _load_module(BATTERY_RUNNER, "s3d_battery_runner_line30_t2")

    wall_over_cpu_within = [
        {
            "component": "contention_wall_inflated",
            "measured_wall_seconds": 31.0 * 3600.0,
            "measured_process_cpu_seconds": 22.0 * 3600.0,
            "projected_units": 1.0,
            "note": "wall exceeds L but process CPU does not",
            "timing_source": "test",
        }
    ]
    projection = battery.project_s3d_part0_cpu_time_units(wall_over_cpu_within, applied_line=30.0)

    assert projection["total_projected_wall_hours"] == 31.0
    assert projection["projected_cpu_hours"] == 22.0
    assert projection["gate_relation"] == "within_line"
    assert projection["decision"] == "s3d_part0_projection_within_signed_line"

    cpu_over = [
        {
            "component": "true_cpu_overrun",
            "measured_wall_seconds": 31.0 * 3600.0,
            "measured_process_cpu_seconds": 30.5 * 3600.0,
            "projected_units": 1.0,
            "note": "process CPU exceeds L",
            "timing_source": "test",
        }
    ]
    stop_projection = battery.project_s3d_part0_cpu_time_units(cpu_over, applied_line=30.0)

    assert stop_projection["total_projected_wall_hours"] == 31.0
    assert stop_projection["projected_cpu_hours"] == 30.5
    assert stop_projection["gate_relation"] == "exceeds_line"
    assert stop_projection["decision"] == "STOP_s3d_part0_projection_exceeds_signed_line"


def test_t3_run_part0_projection_line_records_process_cpu_for_every_projection_unit(monkeypatch, tmp_path):
    battery = _load_module(BATTERY_RUNNER, "s3d_battery_runner_line30_t3")

    specs = {
        "constant_none": SimpleNamespace(cell_id="constant_none", variant="constant_none", trajectory_spec={}),
        "camouflage_off": SimpleNamespace(cell_id="camouflage_off", variant="camouflage_off", trajectory_spec={}),
        "low_diversity": SimpleNamespace(cell_id="low_diversity", variant="low_diversity", trajectory_spec={}),
        "stable_facts": SimpleNamespace(cell_id="stable_facts", variant="stable_facts", trajectory_spec={}),
        "flat_theta": SimpleNamespace(cell_id="flat_theta", variant="flat_theta", trajectory_spec={}),
    }

    class FakePart0:
        def _measure_sklearn_selected(self, *args, **kwargs):
            return {
                "fit_plus_validation_wall_clock_seconds": 2.0,
                "cell_id": "camouflage_off",
                "member": "fake_sklearn",
            }

        def _measure_gru_selected(self, *args, **kwargs):
            return {
                "fit_plus_validation_wall_clock_seconds": 3.0,
                "cell_id": "camouflage_off",
                "member": kwargs.get("member_kind", "fake_gru"),
            }

        def _measure_bootstrap_unit(self):
            return {"wall_clock_seconds": 0.5, "cell_id": "bootstrap", "member": "bootstrap"}

    def fake_prefix_measure(part0, design, spec, member_classes, *, eval_user_id, run_id):
        return {
            "cell_id": spec.cell_id,
            "variant": spec.variant,
            "members": {
                member: {
                    "member": member,
                    "cell_id": spec.cell_id,
                    "variant": spec.variant,
                    "eval_user_id_measured": eval_user_id,
                    "projected_one_member_cell_wall_seconds": 4.0,
                    "projected_one_member_cell_process_cpu_seconds": 1.0,
                    "process_cpu_seconds": 1.0,
                    "wall_clock_seconds": 4.0,
                }
                for member in member_classes
            },
            "process_cpu_seconds": 1.0,
            "wall_clock_seconds": 4.0,
        }

    monkeypatch.setattr(battery, "load_frozen_design", lambda path: {"fake": "design"})
    monkeypatch.setattr(battery, "build_s3d_cert_set_specs", lambda design: list(specs.values()))
    monkeypatch.setattr(battery, "_single_thread_environment", lambda: {"single_thread_accounting": True})
    monkeypatch.setattr(battery, "_code_path_hash", lambda: "fake-code-hash")
    monkeypatch.setattr(battery, "_read_json", lambda path: {})
    monkeypatch.setattr(battery, "_selected_recipe_configs", lambda: {member: {} for member in battery.SELECTED_RECIPE_BY_MEMBER})
    monkeypatch.setattr(
        battery,
        "_selected_recipe_paths",
        lambda: {member: tmp_path / f"{member}.json" for member in battery.SELECTED_RECIPE_BY_MEMBER},
    )
    monkeypatch.setattr(battery, "_sha256", lambda path: "fake-sha256")
    monkeypatch.setattr(battery, "_load_original_part0_runner", lambda: FakePart0())
    monkeypatch.setattr(
        battery,
        "_measure_generation_cputime",
        lambda design, spec, run_id: {
            "unit": "one_cert_set_generation",
            "cell_id": spec.cell_id,
            "variant": spec.variant,
            "wall_clock_seconds": 1.0,
            "process_cpu_seconds": 0.5,
        },
    )
    monkeypatch.setattr(
        battery,
        "_measure_ideal_cputime",
        lambda design, spec, user_id, run_id: {
            "user_id": user_id,
            "cell_id": spec.cell_id,
            "variant": spec.variant,
            "wall_clock_seconds": 5.0,
            "process_cpu_seconds": 2.0,
        },
    )
    monkeypatch.setattr(battery, "_measure_prefix_family_one_eval_user_cputime", fake_prefix_measure)
    monkeypatch.setattr(battery, "_run_dominant_serial_remeasurements", lambda *args, **kwargs: {})

    projection = battery._run_part0_projection_line(30.0, tmp_path / "projection.json")
    measurements = projection["full_part0_measurements"]

    assert measurements["cert_set_generation"]["process_cpu_seconds"] >= 0.0
    assert measurements["ideal_per_user_one_cell"]["process_cpu_seconds"] >= 0.0
    for key in (
        "logreg_F1_selected",
        "logreg_F2_reference",
        "gbt_half_data_selected",
        "gru_selected",
        "seq_full_selected",
        "seq_W15_selected",
        "bootstrap",
    ):
        assert "process_cpu_seconds" in measurements[key]
    for family in ("table_family", "retrieval_family", "degenerate_family", "ls_online_family"):
        for member, record in measurements[family]["members"].items():
            assert "process_cpu_seconds" in record, member
            assert "projected_one_member_cell_process_cpu_seconds" in record, member

    component_names = set(projection["full_part0_projection"]["components"])
    assert "retrieval_family_nearest_neighbor_user_matching_cert_plus_NULL" in component_names
    assert "ls_online_family_discounted_LS_lambda_0.95_cert_plus_NULL" in component_names
    for component in projection["full_part0_projection"]["components"].values():
        assert "measured_process_cpu_seconds" in component


def test_t4_budget_decision_002a_parser_reads_signed_section6_line_and_firewall():
    battery = _load_module(BATTERY_RUNNER, "s3d_battery_runner_line30_t4")

    signed = battery._parse_signed_budget_decision()

    assert signed["source_path"].endswith("S3D-BUDGET-DECISION-002A.md")
    assert signed["zero_score_exposure_confirmed"] is True
    assert signed["resume_mode"] == "reuse-completed"
    assert signed["line_cpu_hours"] == 38.0
    assert signed["endgame_acknowledged"] is True
    assert signed["firewall_acknowledged"] is True
    assert signed["operator"] == "Leo"
    assert signed["date"] == "2026-07-05"


def test_t5_trace_reconstruction_persists_reusable_unit_result_with_input_hash(tmp_path, monkeypatch):
    battery = _load_module(BATTERY_RUNNER, "s3d_battery_runner_line30_t5")
    monkeypatch.setattr(battery, "UNIT_RESULTS_DIR", tmp_path)
    monkeypatch.setattr(battery, "_sha256", lambda path: "frozen-design-sha256")
    monkeypatch.setattr(
        battery,
        "_unit_input_record",
        lambda payload: {
            "unit_payload": dict(payload),
            "frozen_design_sha256": "frozen-design-sha256",
            "cell": {"master_seed": 123, "variant": "constant_none"},
        },
    )
    row = {
        "unit_id": "member::cert::predict_none::constant_none",
        "unit_type": "member",
        "phase": "cert",
        "member": "predict_none",
        "cell_id": "constant_none",
        "metric": 1.0,
        "recommend_turn_conditional_metric": None,
        "n_eval_points": 2,
        "wall_clock_seconds": 1.5,
        "process_cpu_seconds": 1.25,
        "wall_cpu_ratio": 1.2,
        "wall_cpu_ratio_flag_gt_1_25": False,
        "cumulative_contention_robust_cpu_hours": 0.01,
        "run_started_at": "2026-07-05T00:00:00Z",
        "run_finished_at": "2026-07-05T00:00:01Z",
        "heldout_users_800_999_touched": False,
        "future_observations_used": False,
        "per_user_confusion": [
            {
                "user_id": 640,
                "n": 2,
                "totals": [2] + [0] * 31,
                "correct": [2] + [0] * 31,
                "recommend_totals": [0] * 32,
                "recommend_correct": [0] * 32,
            }
        ],
    }
    row["metric_digest"] = battery._metric_digest(battery._score_payload_from_trace_row(row))

    persisted = battery._persist_reconstructed_unit_from_trace(row, void_code_path_hash="void-code-hash")

    assert persisted["unit_id"] == row["unit_id"]
    assert persisted["score_payload"]["code_path_hash"] == "void-code-hash"
    assert persisted["score_payload"]["input_hash"]
    assert persisted["score_payload"]["per_user_confusion_sha256"] == battery._sha256_json(row["per_user_confusion"])
    assert persisted["score_payload"]["metric_digest"] == row["metric_digest"]
    assert persisted["score_payload"]["classes_present"] == [0]
    assert persisted["score_payload"]["recommend_turn_count"] == 0
    assert (tmp_path / "member__cert__predict_none__constant_none.json").exists()


def test_t6_spot_check_gate_is_seeded_and_blocks_digest_or_confusion_mismatch(monkeypatch):
    battery = _load_module(BATTERY_RUNNER, "s3d_battery_runner_line30_t6")
    payloads = [
        {"unit_id": f"unit::{idx}", "unit_type": "member", "phase": "cert", "cell_id": "constant_none", "member": "predict_none"}
        for idx in range(5)
    ]
    persisted = {}
    for payload in payloads:
        score = {
            **payload,
            "metric": 1.0,
            "recommend_turn_conditional_metric": None,
            "n_eval_points": 1,
            "classes_present": [0],
            "class_count_present": 1,
            "per_user_confusion": [{"user_id": 640, "n": 1, "totals": [1] + [0] * 31, "correct": [1] + [0] * 31, "recommend_totals": [0] * 32, "recommend_correct": [0] * 32}],
            "per_user_confusion_sha256": "confusion-sha",
            "metric_digest": "digest-ok",
            "process_cpu_seconds": 0.25,
        }
        persisted[payload["unit_id"]] = {"score_payload": score, "input_hash": "input-hash", "code_path_hash": "void-code"}

    selected = battery._select_spot_check_unit_ids([p["unit_id"] for p in payloads], seed_text="fixed-seed", count=3)

    def exact_worker(payload):
        return {
            **persisted[payload["unit_id"]]["score_payload"],
            "metric_digest": "digest-ok",
            "per_user_confusion_sha256": "confusion-sha",
            "process_cpu_seconds": 0.5,
        }

    monkeypatch.setattr(battery, "_run_unit_worker", exact_worker)
    passed = battery._spot_check_reused_units(
        payloads,
        persisted,
        seed_text="fixed-seed",
        count=3,
    )
    assert passed["passed"] is True
    assert passed["selected_unit_ids"] == selected
    assert passed["spot_check_process_cpu_seconds"] == pytest.approx(1.5)

    def mismatch_worker(payload):
        result = exact_worker(payload)
        if payload["unit_id"] == selected[0]:
            result["metric_digest"] = "digest-mismatch"
        return result

    monkeypatch.setattr(battery, "_run_unit_worker", mismatch_worker)
    failed = battery._spot_check_reused_units(
        payloads,
        persisted,
        seed_text="fixed-seed",
        count=3,
    )
    assert failed["passed"] is False
    assert failed["mismatches"][0]["unit_id"] == selected[0]


def test_t7_gru_training_seeds_torch_from_existing_config_seed_before_model_construction():
    source = OBS_DECODERS.read_text(encoding="utf-8")

    function_body = re.search(
        r"def _fit_eval_gru_sequences\([\s\S]*?\n\n\ndef _empty_sweep_aggregators",
        source,
    )
    assert function_body is not None
    body = function_body.group(0)
    seed_call = 'torch.manual_seed(_derive_config_seed(design, str(config["config_id"])))'
    model_call = "model = _make_torch_next_symbol_gru("

    assert seed_call in body
    assert body.index(seed_call) < body.index(model_call)


def test_t8_repair_resume_plan_reuses_only_deterministic_completed_units_and_spot_check_002():
    battery = _load_module(BATTERY_RUNNER, "s3d_battery_runner_line30_t8")
    expected_ids = [
        "member::cert::obs_decoder_gru::camouflage_off",
        "member::null::obs_decoder_gru::NULL_env",
        "member::cert::seq_full_history_no_action_conditioning::constant_none",
        "member::null::seq_full_history_no_action_conditioning::NULL_env",
        "member::cert::seq_window_with_action_conditioning_W15_no_cross_session_persistence::low_diversity",
        "member::null::seq_window_with_action_conditioning_W15_no_cross_session_persistence::NULL_env",
        "member::cert::obs_decoder_gbt::camouflage_off",
        "member::null::obs_decoder_gbt::NULL_env",
        "member::cert::discounted_LS_lambda_0.95::flat_theta",
        "member::null::discounted_LS_lambda_0.95::NULL_env",
    ]
    completed_ids = [
        unit_id
        for unit_id in expected_ids
        if "discounted_LS_lambda_0.95" not in unit_id
    ]

    plan = battery._repair_resume_unit_plan(expected_ids, completed_ids)

    assert plan["spot_check_seed_text"] == "FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-RESUME-001A:spot-check:002"
    assert plan["reused_unit_ids"] == [
        "member::cert::obs_decoder_gbt::camouflage_off",
        "member::null::obs_decoder_gbt::NULL_env",
    ]
    assert plan["excluded_nondeterministic_completed_unit_ids"] == [
        "member::cert::obs_decoder_gru::camouflage_off",
        "member::null::obs_decoder_gru::NULL_env",
        "member::cert::seq_full_history_no_action_conditioning::constant_none",
        "member::null::seq_full_history_no_action_conditioning::NULL_env",
        "member::cert::seq_window_with_action_conditioning_W15_no_cross_session_persistence::low_diversity",
        "member::null::seq_window_with_action_conditioning_W15_no_cross_session_persistence::NULL_env",
    ]
    assert plan["fresh_unit_ids"] == [
        "member::cert::obs_decoder_gru::camouflage_off",
        "member::null::obs_decoder_gru::NULL_env",
        "member::cert::seq_full_history_no_action_conditioning::constant_none",
        "member::null::seq_full_history_no_action_conditioning::NULL_env",
        "member::cert::seq_window_with_action_conditioning_W15_no_cross_session_persistence::low_diversity",
        "member::null::seq_window_with_action_conditioning_W15_no_cross_session_persistence::NULL_env",
        "member::cert::discounted_LS_lambda_0.95::flat_theta",
        "member::null::discounted_LS_lambda_0.95::NULL_env",
    ]
