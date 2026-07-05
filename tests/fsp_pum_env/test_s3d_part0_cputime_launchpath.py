from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[2]
BATTERY_RUNNER = ROOT / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "s3d_battery_runner_line30.py"
REGATE_RUNNER = ROOT / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "s3d_part0_cputime_regate_runner.py"


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
