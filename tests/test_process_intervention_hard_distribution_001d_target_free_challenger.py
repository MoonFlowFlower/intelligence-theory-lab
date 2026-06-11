import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from process_intervention_hard_distribution_001d.runner import run_preflight_001d


ARTIFACT_DIR = ROOT / "artifacts" / "process_intervention_hard_distribution_001d_target_free_generative_replay_challenger"
TASK_CARD = (
    ROOT
    / "docs"
    / "codex"
    / "tasks"
    / "PROCESS-INTERVENTION-HARD-DISTRIBUTION-001D-TARGET-FREE-GENERATIVE-REPLAY-CHALLENGER.md"
)

CLAIM_CEILING = "bounded target-free generative replay challenger preflight evidence only"
FREEZE_ANCHOR = "afeff65"
REQUIRED_ARTIFACTS = {
    "result.json",
    "prediction_commit.json",
    "prediction_commit.sha256",
    "access_log.json",
    "evaluation_report.json",
    "preserved_controls.json",
    "old_artifact_anchor_verification.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "replay_report.json",
    "claim_ceiling.txt",
}
ALLOWED_VERDICTS = {
    "process_intervention_hard_distribution_001d_failed_target_free_replay_challenger_match",
    "process_intervention_hard_distribution_001d_failed_witness_or_ablation",
    "process_intervention_hard_distribution_001d_bounded_replay_gate_pass",
    "process_intervention_hard_distribution_001d_invalid_access_leakage",
}
PHASE_A_ALLOWED_INPUTS = {
    "allowed_prefix",
    "support_split",
    "permitted_history",
}
PHASE_A_FORBIDDEN_INPUTS = {
    "heldout_outcomes",
    "target_future_behavior",
    "witness_trace_rows_for_target_cases",
    "process_signatures",
    "post_ablation_target_results",
    "failure_manifests",
    "control_comparison_target_results",
}
REQUIRED_CONTROLS = {
    "online_count_statistic",
    "count_table",
    "graph_cache",
    "transition_table",
    "successor_map",
    "behavior_only_replay",
    "summary_retrieval",
    "trace_only_replay",
}
REQUIRED_EVAL_METRICS = {
    "intervention_response_match_rate",
    "later_behavior_match_rate",
    "update_process_signature_match_rate",
    "heldout_composition_match_rate",
    "delayed_effect_match_rate",
    "observable_key_conflict_match_rate",
    "partial_observability_match_rate",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head_sha(relative_path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"HEAD:{relative_path}"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    return hashlib.sha256(result.stdout).hexdigest()


def _git_show_sha(relative_path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{FREEZE_ANCHOR}:{relative_path}"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    return hashlib.sha256(result.stdout).hexdigest()


def test_001d_run_emits_required_artifacts_and_bounded_verdict(tmp_path):
    assert TASK_CARD.exists()

    result = run_preflight_001d(repo_root=ROOT, output_dir=tmp_path)

    assert result["task_id"] == "PROCESS-INTERVENTION-HARD-DISTRIBUTION-001D-TARGET-FREE-GENERATIVE-REPLAY-CHALLENGER"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["freeze_anchor_commit"] == FREEZE_ANCHOR
    assert all(value is False for value in result["authorization_flags"].values())
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    assert (tmp_path / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING


def test_phase_a_access_firewall_is_allowlist_based_and_blocks_target_leakage(tmp_path):
    run_preflight_001d(repo_root=ROOT, output_dir=tmp_path)

    access_log = _read_json(tmp_path / "access_log.json")
    commit = _read_json(tmp_path / "prediction_commit.json")

    phase_a = access_log["phase_a"]
    assert phase_a["access_firewall_enforced"] is True
    assert set(phase_a["allowed_inputs_read"]) == PHASE_A_ALLOWED_INPUTS
    assert set(phase_a["forbidden_inputs_blocked"]) == PHASE_A_FORBIDDEN_INPUTS
    assert phase_a["forbidden_access_used"] is False
    assert phase_a["target_trace_rows_read"] == 0
    assert phase_a["target_heldout_outcomes_read"] == 0
    assert phase_a["target_future_behaviors_read"] == 0
    assert phase_a["target_process_signatures_read"] == 0

    assert commit["phase"] == "A_target_free_prediction_commit"
    assert commit["access_contract"]["allowed_inputs"] == [
        "allowed_prefix",
        "support_split",
        "permitted_history",
    ]
    assert commit["access_contract"]["forbidden_access_used"] is False
    for prediction in commit["predictions"]:
        assert set(prediction) == {
            "case_id",
            "split",
            "predicted_intervention_response",
            "predicted_later_behavior",
            "predicted_process_signature_hash",
            "confidence",
            "prediction_basis",
        }
        assert prediction["split"] == "heldout"


def test_prediction_commit_is_hash_frozen_before_reveal_and_phase_b_cannot_rewrite(tmp_path):
    run_preflight_001d(repo_root=ROOT, output_dir=tmp_path)

    expected_hash = (tmp_path / "prediction_commit.sha256").read_text(encoding="utf-8").strip()
    actual_hash = _sha256(tmp_path / "prediction_commit.json")
    access_log = _read_json(tmp_path / "access_log.json")
    evaluation = _read_json(tmp_path / "evaluation_report.json")

    assert expected_hash == actual_hash
    assert access_log["phase_order"] == [
        "phase_a_prediction_commit_written",
        "phase_a_prediction_commit_hash_frozen",
        "phase_b_reveal_started",
        "phase_b_evaluation_written",
    ]
    assert access_log["phase_a"]["prediction_commit_hash_frozen_before_reveal"] is True
    assert access_log["phase_b"]["target_reveal_after_hash_freeze"] is True
    assert access_log["phase_b"]["may_write_phase_a_prediction_commit"] is False
    assert access_log["phase_b"]["phase_a_prediction_commit_rewritten"] is False
    assert evaluation["prediction_commit_sha256_verification"]["before_reveal_sha256"] == expected_hash
    assert evaluation["prediction_commit_sha256_verification"]["after_evaluation_sha256"] == expected_hash
    assert evaluation["prediction_commit_sha256_verification"]["hash_unchanged_after_phase_b"] is True


def test_phase_b_evaluates_required_target_free_challenger_metrics(tmp_path):
    result = run_preflight_001d(repo_root=ROOT, output_dir=tmp_path)
    evaluation = _read_json(tmp_path / "evaluation_report.json")

    assert evaluation["phase"] == "B_reveal_and_evaluate"
    assert evaluation["evaluated_after_reveal"] is True
    assert evaluation["target_free_challenger_evaluated"] is True
    assert evaluation["evaluation_scope"] == "heldout_target_cases"
    assert set(evaluation["metrics"]) == REQUIRED_EVAL_METRICS
    assert evaluation["case_sets"]["heldout_composition_case_count"] == 4
    assert evaluation["case_sets"]["delayed_effect_case_count"] == 4
    assert evaluation["case_sets"]["observable_key_conflict_case_count"] == 4
    assert evaluation["case_sets"]["partial_observability_case_count"] == 4
    assert evaluation["metrics"]["intervention_response_match_rate"] < 0.95
    assert evaluation["metrics"]["later_behavior_match_rate"] < 0.95
    assert evaluation["metrics"]["update_process_signature_match_rate"] < 0.90
    assert result["target_free_challenger_match_blocks_gate"] is False
    assert result["verdict"] == "process_intervention_hard_distribution_001d_bounded_replay_gate_pass"


def test_controls_are_preserved_and_trace_only_replay_is_hygiene_only(tmp_path):
    run_preflight_001d(repo_root=ROOT, output_dir=tmp_path)

    controls = _read_json(tmp_path / "preserved_controls.json")
    replay = _read_json(tmp_path / "replay_report.json")
    baseline = _read_json(tmp_path / "baseline_comparison.json")

    assert set(controls["preserved_controls"]) == REQUIRED_CONTROLS
    assert controls["non_replay_fair_controls_preserved"] is True
    assert controls["fair_controls_weakened_or_removed"] is False
    assert controls["trace_only_replay"]["classification"] == "trace_integrity_hygiene"
    assert controls["trace_only_replay"]["counts_as_mechanism_evidence"] is False
    assert controls["trace_only_replay"]["may_block_mechanism_evidence_when_successful"] is False
    assert replay["trace_only_replay_treated_as_mechanism_evidence"] is False
    assert baseline["historical_001b_verdict_preserved"] is True
    assert baseline["historical_001b_pass_status"] == "not_pass"


def test_old_001b_rca_001c_artifacts_match_afeff65_anchor(tmp_path):
    run_preflight_001d(repo_root=ROOT, output_dir=tmp_path)

    verification = _read_json(tmp_path / "old_artifact_anchor_verification.json")
    assert verification["freeze_anchor_commit"] == FREEZE_ANCHOR
    assert verification["old_artifacts_unchanged_from_anchor"] is True
    assert verification["old_001b_artifacts_edited"] is False
    assert verification["old_rca_artifacts_edited"] is False
    assert verification["old_001c_artifacts_edited"] is False
    for relative_path, record in verification["artifact_hashes"].items():
        assert record["current_sha256"] == record["anchor_sha256"]
        assert record["current_sha256"] == _git_show_sha(relative_path)
        assert record["current_sha256"] == _git_head_sha(relative_path)
        assert record["worktree_clean_against_head"] is True


def test_committed_001d_artifacts_exist_after_run():
    result_path = ARTIFACT_DIR / "result.json"
    assert result_path.exists(), "run python -m process_intervention_hard_distribution_001d first"

    result = _read_json(result_path)
    evaluation = _read_json(ARTIFACT_DIR / "evaluation_report.json")
    access_log = _read_json(ARTIFACT_DIR / "access_log.json")

    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert evaluation["target_free_challenger_evaluated"] is True
    assert access_log["phase_a"]["prediction_commit_hash_frozen_before_reveal"] is True
