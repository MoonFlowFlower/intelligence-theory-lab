import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


REQUIRED_BASELINES = {
    "random",
    "majority",
    "observation_only",
    "lookup",
    "count_table",
    "transition_table",
    "graph_cache",
    "successor_map",
    "nearest_neighbor",
    "fsm_planner",
    "episodic_traversal",
    "trace_only_replay",
    "exhaustive_legal_query",
}

REQUIRED_ARTIFACTS = {
    "result.json",
    "trace.jsonl",
    "baseline_comparison.json",
    "ablation_report.json",
    "replay_report.json",
    "leakage_report.json",
    "computed_evidence_provenance.json",
    "failure_manifest.json",
}


def _runner():
    from phase2c_candidate_free_baseline_stress_001a import runner

    return runner


def test_stress_contract_uses_required_seed_family_episode_counts():
    runner = _runner()

    config = runner.default_stress_config()

    assert len(config["seeds"]) >= 5
    assert config["train_family_count"] >= 3
    assert config["heldout_family_count"] >= 3
    assert config["episodes_per_family"] >= 4
    assert runner.expected_trace_rows(config) >= 5 * (3 + 3) * 4


def test_run_stress_produces_candidate_free_artifacts_and_aggregate_baselines(tmp_path):
    runner = _runner()
    output_dir = tmp_path / "stress_output"

    run = runner.run_stress(output_dir, persist_artifacts=True)

    assert run["result"]["task_id"] == runner.TASK_ID
    assert run["result"]["candidate_mechanism_run"] is False
    assert run["result"]["phase3_opened"] is False
    assert run["result"]["route_tournament_authorized"] is False
    assert run["result"]["stress_execution_claim"] is True
    assert run["result"]["seed_count"] >= 5
    assert run["result"]["trace_row_count"] == runner.expected_trace_rows(run["config"])
    assert run["result"]["trace_row_count"] == len(run["trace"]) >= 120
    assert run["result"]["oracle_macro_accuracy"] == 1.0
    assert run["result"]["strongest_fair_baseline_id"]
    assert 0.0 <= run["result"]["strongest_fair_baseline_macro_accuracy"] <= 1.0

    assert set(run["baseline_comparison"]["baseline_ids"]) == REQUIRED_BASELINES
    assert run["baseline_comparison"]["missing_baseline_ids"] == []
    assert run["baseline_comparison"]["strongest_fair_is_max_over_full_battery"] is True
    assert len(run["baseline_comparison"]["per_seed_reports"]) == run["result"]["seed_count"]
    assert all(row["callable_invoked"] is True for row in run["baseline_comparison"]["aggregate_results"])

    assert run["leakage_report"]["positive_controls_passed"] is True
    assert run["leakage_report"]["clean_scan_passed_after_positive_controls"] is True
    assert run["replay_report"]["passed"] is True
    assert run["replay_report"]["uses_hash_only_comparison"] is False
    assert run["replay_report"]["uses_stored_outputs_only"] is False
    assert run["ablation_report"]["all_controls_consumed_by_final_verdict"] is True
    assert run["computed_evidence_provenance"]["records"]
    assert all(
        row["consumed_by_final_verdict"] is True
        for row in run["computed_evidence_provenance"]["records"]
    )
    assert run["failure_manifest"]["has_blocking_failure"] is False

    assert {path.name for path in output_dir.iterdir()} == REQUIRED_ARTIFACTS
    persisted_result = json.loads((output_dir / "result.json").read_text(encoding="utf-8"))
    assert persisted_result == run["result"]

    trace_rows = [
        json.loads(line)
        for line in (output_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(trace_rows) == run["result"]["trace_row_count"]
    for row in trace_rows:
        visible_text = json.dumps(row["candidate_visible"], sort_keys=True).lower()
        assert "hidden_rule" not in visible_text
        assert "target_action" not in visible_text
        assert "answer_map" not in visible_text
