import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from process_intervention_hard_distribution_001b.runner import run_preflight_001b


ARTIFACT_DIR = ROOT / "artifacts" / "process_intervention_hard_distribution_001b"
TASK_CARD = ROOT / "docs" / "codex" / "tasks" / "PROCESS-INTERVENTION-HARD-DISTRIBUTION-001B-EXECUTABLE-PREFLIGHT.md"
REQUIRED_ARTIFACTS = {
    "result.json",
    "control_comparison.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "replay_report.json",
    "heldout_report.json",
    "trace.jsonl",
    "frozen_inputs.json",
    "claim_ceiling.txt",
}
REQUIRED_CONTROLS = {
    "online_count_statistic",
    "count_table",
    "graph_cache",
    "transition_table",
    "successor_map",
    "trace_only_replay",
    "behavior_only_replay",
    "summary_retrieval",
}
ALLOWED_VERDICTS = {
    "process_intervention_hard_distribution_001b_failed_fair_control_match",
    "process_intervention_hard_distribution_001b_failed_witness_underpowered",
    "process_intervention_hard_distribution_001b_invalid_execution_leakage_or_freeze_violation",
    "process_intervention_hard_distribution_001b_bounded_pass",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_hard_distribution_001b_run_emits_required_artifacts(tmp_path):
    assert TASK_CARD.exists()

    result = run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    assert result["task_id"] == "PROCESS-INTERVENTION-HARD-DISTRIBUTION-001B-EXECUTABLE-PREFLIGHT"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["claim_ceiling"] == "bounded hard-distribution process-intervention preflight evidence only"
    assert result["witness_executed"] is True
    assert result["frozen_input_hashes_verified"] is True
    assert all(value is False for value in result["authorization_flags"].values())
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    assert (tmp_path / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == result["claim_ceiling"]


def test_hard_distribution_001b_controls_and_failure_boundary(tmp_path):
    result = run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)
    controls = _read_json(tmp_path / "control_comparison.json")

    assert set(controls["controls"]) == REQUIRED_CONTROLS
    assert controls["fair_controls_weakened_or_removed"] is False
    assert controls["thresholds_changed_after_results"] is False
    assert controls["all_controls_executed_under_predeclared_budget"] is True

    for control in controls["controls"].values():
        assert control["executed"] is True
        assert control["predeclared"] is True
        assert control["uses_forbidden_access"] is False
        assert control["resource_budget_within_limit"] is True

    if result["verdict"] == "process_intervention_hard_distribution_001b_failed_fair_control_match":
        failure = _read_json(tmp_path / "failure_manifest.json")
        assert failure["failure_type"] == "fair_control_matched_witness"
        assert failure["matched_controls"] == controls["matching_controls"]
        assert failure["do_not_patch_into_pass"] is True
    else:
        assert "failure_manifest.json" not in {path.name for path in tmp_path.iterdir()}


def test_hard_distribution_001b_trace_replay_and_artifact_boundaries(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    trace = _read_jsonl(tmp_path / "trace.jsonl")
    replay = _read_json(tmp_path / "replay_report.json")
    frozen = _read_json(tmp_path / "frozen_inputs.json")

    assert len(trace) == 12
    assert trace[0]["previous_trace_hash"] == "GENESIS"
    for previous, current in zip(trace, trace[1:]):
        assert current["previous_trace_hash"] == previous["current_trace_hash"]
    assert replay["hash_chain_valid"] is True
    assert replay["allowed_update_path_replay_valid"] is True
    assert replay["trace_only_replay_match_rate"] == 1.0
    assert replay["trace_only_replay_treated_as_mechanism_evidence"] is False
    assert frozen["hard_distribution_001a_inputs_verified_against_git_head"] is True
    assert frozen["old_001b_or_rca_artifacts_edited"] is False


def test_hard_distribution_001b_reports_hard_cases_and_ablations(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    heldout = _read_json(tmp_path / "heldout_report.json")
    ablation = _read_json(tmp_path / "ablation_report.json")
    result = _read_json(tmp_path / "result.json")

    assert heldout["heldout_composition_report_exists"] is True
    assert heldout["heldout_evaluated_posthoc"] is False
    assert heldout["heldout_case_count"] == 4
    assert heldout["observable_key_conflict_cases_evaluated_separately"] is True
    assert heldout["delayed_effect_cases_evaluated"] is True
    assert heldout["partial_observability_cases_evaluated"] is True

    hooks = {hook["hook_id"]: hook for hook in ablation["ablations"]}
    assert hooks["learning_freeze"]["executed"] is True
    assert hooks["learning_freeze"]["changed_expected_process_sensitive_behavior"] is True
    assert hooks["history_replacement"]["executed"] is True
    assert hooks["history_replacement"]["changed_expected_behavior"] is True
    assert hooks["counterfactual_action_contrast"]["executed"] is True
    assert hooks["counterfactual_action_contrast"]["contrast_detected"] is True
    assert hooks["outcome_perturbation"]["executed"] is False
    assert hooks["outcome_perturbation"]["skip_reason"] == "not_predeclared_in_001a_ablation_hooks"
    assert result["ablation_results_show_predicted_change"] is True


def test_hard_distribution_001b_committed_artifacts_exist_after_run():
    result_path = ARTIFACT_DIR / "result.json"
    assert result_path.exists(), "run python -m process_intervention_hard_distribution_001b first"

    result = _read_json(result_path)
    controls = _read_json(ARTIFACT_DIR / "control_comparison.json")
    heldout = _read_json(ARTIFACT_DIR / "heldout_report.json")

    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["claim_ceiling"] == "bounded hard-distribution process-intervention preflight evidence only"
    assert set(controls["controls"]) == REQUIRED_CONTROLS
    assert heldout["heldout_case_count"] == 4
