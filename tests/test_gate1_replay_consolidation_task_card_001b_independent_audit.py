import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "gate1_replay_consolidation_task_card_001b_independent_audit"
AUDIT_REPORT = ARTIFACT_DIR / "GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001B-INDEPENDENT-AUDIT.md"
DOC_REPORT = ROOT / "docs" / "codex" / "tasks" / "GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001B-INDEPENDENT-AUDIT.md"

TASK_ID = "GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001B-INDEPENDENT-AUDIT"
ANCHOR_COMMIT = "b813651"
CLAIM_CEILING = "bounded independent Gate1 task-card audit evidence only"
EXPECTED_VERDICT = "gate1_replay_consolidation_task_card_001b_failed_trace_replay_contract"

REQUIRED_ARTIFACTS = {
    "independent_audit_result.json",
    "audit_matrix.json",
    "missing_or_ambiguous_requirements.json",
    "execution_preflight_authorization.json",
    "claim_ceiling.txt",
    "GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001B-INDEPENDENT-AUDIT.md",
}
ALLOWED_VERDICTS = {
    "gate1_replay_consolidation_task_card_001b_independent_audit_pass",
    "gate1_replay_consolidation_task_card_001b_failed_scope_leak",
    "gate1_replay_consolidation_task_card_001b_failed_missing_baselines",
    "gate1_replay_consolidation_task_card_001b_failed_missing_ablations",
    "gate1_replay_consolidation_task_card_001b_failed_trace_replay_contract",
    "gate1_replay_consolidation_task_card_001b_failed_leakage_controls",
    "gate1_replay_consolidation_task_card_001b_failed_claim_inflation",
    "gate1_replay_consolidation_task_card_001b_invalid_artifact_mutation",
}
REQUIRED_BASELINES = {
    "retrieval / summary retrieval",
    "behavior-only replay",
    "trace-only replay as hygiene only",
    "online count/statistic controls",
    "transition table / successor map / graph cache controls",
    "target-free generative replay challenger",
    "frozen-history control",
    "no-consolidation control",
    "shuffled-replay control",
    "corrupted-replay control",
}
REQUIRED_ABLATIONS = {
    "learning freeze",
    "history replacement",
    "consolidation disabled",
    "replay order shuffled",
    "replay content corrupted",
    "heldout composition",
    "delayed-effect cases",
    "observable-key conflict cases",
    "partial-observability cases",
    "counterfactual action contrast",
}
TRACE_REQUIREMENTS = {
    "pre_post_replay_state_traces",
    "replay_event_logs",
    "consolidation_traces",
    "later_behavior_evaluation",
    "replay_to_behavior_linkage",
    "target_free_evaluation_separation",
    "hash_freeze_or_equivalent_artifact_integrity",
    "trace_only_replay_hygiene_only",
}
LEAKAGE_CONTROLS = {
    "target_trace_leakage_prevented",
    "heldout_outcome_leakage_prevented",
    "post_evaluation_mutation_prevented",
    "baseline_access_asymmetry_prevented",
    "replay_traces_not_used_as_mechanism_evidence",
    "old_failed_001b_not_used_as_pass_evidence",
}
ANCHOR_PROTECTED_PATHS = [
    "docs/codex/tasks/GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A.md",
    "artifacts/gate1_replay_consolidation_task_card_001a/task_card_result.json",
    "artifacts/gate1_replay_consolidation_task_card_001a/validation_matrix.json",
    "artifacts/gate1_replay_consolidation_task_card_001a/source_evidence_manifest.json",
    "artifacts/gate1_replay_consolidation_task_card_001a/claim_ceiling.txt",
    "artifacts/pi_hd_admission_001/admission_result.json",
    "artifacts/process_intervention_hard_distribution_001d_target_free_generative_replay_challenger/result.json",
]


def _read_json(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def _normalized_sha256_text(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def _git_show_text_sha(relative_path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ANCHOR_COMMIT}:{relative_path}"],
        cwd=ROOT,
        capture_output=True,
        check=True,
        encoding="utf-8",
    )
    return _normalized_sha256_text(result.stdout)


def test_independent_audit_artifacts_exist_parse_and_report_failed_trace_contract():
    assert DOC_REPORT.exists()
    assert AUDIT_REPORT.exists()
    assert AUDIT_REPORT.read_text(encoding="utf-8") == DOC_REPORT.read_text(encoding="utf-8")
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})

    result = _read_json("independent_audit_result.json")
    assert result["task_id"] == TASK_ID
    assert result["layer"] == "bounded independent task-card audit only"
    assert result["audited_task_card"] == "GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A"
    assert result["audit_anchor_commit"] == ANCHOR_COMMIT
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == EXPECTED_VERDICT
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING


def test_baseline_and_ablation_audits_are_complete_and_non_executing():
    matrix = _read_json("audit_matrix.json")
    checks = {item["check_id"]: item for item in matrix["checks"]}

    assert checks["baseline_audit"]["passed"] is True
    assert set(checks["baseline_audit"]["observed"]) == REQUIRED_BASELINES
    assert checks["baseline_audit"]["executed_any_baseline"] is False
    assert checks["ablation_audit"]["passed"] is True
    assert set(checks["ablation_audit"]["observed"]) == REQUIRED_ABLATIONS
    assert checks["ablation_audit"]["executed_any_ablation"] is False


def test_trace_replay_audit_records_exact_blockers_without_patching_001a():
    matrix = _read_json("audit_matrix.json")
    missing = _read_json("missing_or_ambiguous_requirements.json")
    checks = {item["check_id"]: item for item in matrix["checks"]}

    assert checks["trace_replay_requirement_audit"]["passed"] is False
    assert set(checks["trace_replay_requirement_audit"]["requirements"]) == TRACE_REQUIREMENTS
    assert checks["trace_replay_requirement_audit"]["failed_requirements"] == [
        "pre_post_replay_state_traces",
        "replay_to_behavior_linkage",
    ]
    assert missing["verdict"] == EXPECTED_VERDICT
    assert [item["requirement_id"] for item in missing["blocking_requirements"]] == [
        "pre_post_replay_state_traces",
        "replay_to_behavior_linkage",
    ]
    assert missing["inline_patch_allowed"] is False
    assert missing["requires_separate_minimal_amendment_task"] is True


def test_leakage_claim_and_scope_controls_remain_bounded():
    matrix = _read_json("audit_matrix.json")
    authorization = _read_json("execution_preflight_authorization.json")
    result = _read_json("independent_audit_result.json")
    checks = {item["check_id"]: item for item in matrix["checks"]}

    assert checks["access_leakage_audit"]["passed"] is True
    assert set(checks["access_leakage_audit"]["controls"]) == LEAKAGE_CONTROLS
    assert checks["scope_boundary_audit"]["passed"] is True
    assert checks["claim_ceiling_audit"]["passed"] is True
    assert result["gate1_executed"] is False
    assert result["gate1_runtime_implemented"] is False
    assert result["new_mechanism_code_added"] is False
    assert all(value is False for value in result["authorization_flags"].values())
    assert authorization["audit_passed"] is False
    assert authorization["gate1_executable_preflight_drafting_authorized"] is False
    assert authorization["gate1_executable_preflight_execution_authorized"] is False
    assert authorization["gate1_execution_authorized"] is False
    assert authorization["same_agent_bridge_authorized"] is False
    assert authorization["ego_mainline_authorized"] is False
    assert authorization["mechanism_validity_claim_authorized"] is False
    assert authorization["agency_claim_authorized"] is False
    assert authorization["consciousness_claim_authorized"] is False
    assert authorization["companion_readiness_claim_authorized"] is False


def test_001a_and_old_anchor_artifacts_are_unchanged_from_b813651():
    manifest = _read_json("independent_audit_result.json")["artifact_mutation_audit"]

    assert manifest["old_artifacts_modified"] is False
    assert manifest["001a_task_card_edited_during_audit"] is False
    assert manifest["protected_paths_checked"] == ANCHOR_PROTECTED_PATHS
    for relative_path in ANCHOR_PROTECTED_PATHS:
        assert _normalized_sha256_text((ROOT / relative_path).read_text(encoding="utf-8")) == _git_show_text_sha(
            relative_path
        )


def test_markdown_report_states_failure_without_claim_inflation_or_inline_fix():
    text = AUDIT_REPORT.read_text(encoding="utf-8")

    assert EXPECTED_VERDICT in text
    assert "Gate1 execution is not authorized" in text
    assert "No inline patch was applied to 001A" in text
    assert "trace_only_replay remains hygiene only" in text
    assert CLAIM_CEILING in text
    assert "This does not prove Gate1 pass" in text
