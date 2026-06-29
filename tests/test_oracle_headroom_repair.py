import json

from itl_devbench.eval.metrics import METRIC_ORIENTATION
from itl_devbench.eval.run_matrix import REQUIRED_BASELINES, run_benchmark


def test_metric_orientation_declares_primary_objective_and_all_metrics():
    assert METRIC_ORIENTATION["total_reward"]["orientation"] == "higher"
    assert METRIC_ORIENTATION["total_reward"]["primary"] is True
    for metric_name in [
        "survival_ticks",
        "energy_final",
        "health_final",
        "prediction_error_mean",
        "adaptation_lag_after_rule_shift",
        "memory_size",
        "action_count",
        "collision_count",
        "oracle_gap",
    ]:
        assert metric_name in METRIC_ORIENTATION
        assert METRIC_ORIENTATION[metric_name]["orientation"] in {"higher", "lower", "bounded"}


def test_smoke_run_emits_stage_headroom_and_graph_cache_audit_outputs(tmp_path):
    run_dir = run_benchmark(
        config={"width": 7, "height": 7, "max_ticks": 12, "smoke_seeds": [0]},
        smoke=True,
        output_root=tmp_path,
    )

    for name in [
        "baseline_scores_by_stage.json",
        "oracle_headroom_report.json",
        "leakage_audit_graph_cache.json",
        "diagnosis_oracle_headroom.md",
    ]:
        assert (run_dir / name).exists(), name

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    for key in [
        "baseline_scores_by_stage_path",
        "oracle_headroom_report_path",
        "leakage_audit_graph_cache_path",
        "diagnosis_oracle_headroom_path",
        "metric_orientation",
    ]:
        assert key in manifest


def test_oracle_is_not_worse_than_frozen_baselines_by_stage_and_aggregate_on_smoke(tmp_path):
    run_dir = run_benchmark(
        config={"width": 7, "height": 7, "max_ticks": 20, "smoke_seeds": [0, 1]},
        smoke=True,
        output_root=tmp_path,
    )
    headroom = json.loads((run_dir / "oracle_headroom_report.json").read_text(encoding="utf-8"))

    assert headroom["primary_metric"] == "total_reward"
    assert headroom["primary_metric_orientation"] == "higher"
    assert headroom["aggregate"]["oracle_upper_bound_valid"] is True
    for stage_record in headroom["by_stage"]:
        assert stage_record["oracle_upper_bound_valid"] is True
        for baseline in REQUIRED_BASELINES:
            assert baseline in stage_record["baseline_scores"]
            assert stage_record["oracle_score"] >= stage_record["baseline_scores"][baseline]


def test_graph_cache_access_contract_audit_reports_no_hidden_or_future_access(tmp_path):
    run_dir = run_benchmark(
        config={"width": 7, "height": 7, "max_ticks": 12, "smoke_seeds": [0]},
        smoke=True,
        output_root=tmp_path,
    )
    graph_audit = json.loads((run_dir / "leakage_audit_graph_cache.json").read_text(encoding="utf-8"))

    assert graph_audit["verdict"] == "graph_cache_access_contract_ok"
    assert graph_audit["checks"]["hidden_state_access"]["ok"] is True
    assert graph_audit["checks"]["future_outcome_access"]["ok"] is True
    assert graph_audit["checks"]["cache_reset_scope"]["ok"] is True
    assert graph_audit["checks"]["cross_seed_rule_seed_contamination"]["ok"] is True
