import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "gate1_task_card_001a_amendment_001_trace_replay_contract_patch"
DOC_REPORT = (
    ROOT
    / "docs"
    / "codex"
    / "tasks"
    / "GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A-AMENDMENT-001-TRACE-REPLAY-CONTRACT-PATCH.md"
)
ARTIFACT_REPORT = ARTIFACT_DIR / "GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A-AMENDMENT-001-TRACE-REPLAY-CONTRACT-PATCH.md"

TASK_ID = "GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A-AMENDMENT-001-TRACE-REPLAY-CONTRACT-PATCH"
VERDICT = "gate1_task_card_001a_amendment_001_trace_replay_contract_patch_pass"
CLAIM_CEILING = "bounded Gate1 task-card trace/replay contract amendment only"
BASE_TASK_CARD_ANCHOR = "b813651"
INDEPENDENT_AUDIT_ANCHOR = "4e3e9f2"

REQUIRED_ARTIFACTS = {
    "amendment_result.json",
    "trace_replay_contract_patch.json",
    "linkage_key_contract.json",
    "amended_task_card_manifest.json",
    "audit_blocker_resolution_matrix.json",
    "claim_ceiling.txt",
    "GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A-AMENDMENT-001-TRACE-REPLAY-CONTRACT-PATCH.md",
}
REQUIRED_TRACE_FIELDS = {
    "replay_event_id",
    "consolidation_event_id",
    "source_experience_ids",
    "target_case_id",
    "replay_start_time_or_step",
    "replay_end_time_or_step",
    "state_hash_before_replay",
    "state_hash_after_replay",
    "consolidation_state_hash_before",
    "consolidation_state_hash_after",
    "later_behavior_eval_id",
    "replay_to_behavior_linkage_key",
    "linkage_key_derivation_rule",
    "linkage_key_uniqueness_check",
    "linkage_key_collision_report",
    "replay_event_to_later_behavior_join_table",
    "hash_freeze_before_later_behavior_evaluation",
    "mutation_check_after_later_behavior_evaluation",
}
REQUIRED_FUTURE_ARTIFACTS = {
    "replay_event_log.json",
    "consolidation_trace.json",
    "state_hash_chain.json",
    "replay_behavior_linkage_table.json",
    "linkage_key_collision_report.json",
    "later_behavior_evaluation.json",
    "mutation_check_report.json",
}
FORBIDDEN_LINKAGE_INPUTS = {
    "heldout_outcome",
    "target_heldout_outcome",
    "future_behavior_label",
    "target_future_behavior_label",
    "witness_result",
    "witness_match_result",
    "post_evaluation_metric",
    "post_evaluation_metrics",
}
ALLOWED_VERDICTS = {
    "gate1_task_card_001a_amendment_001_trace_replay_contract_patch_pass",
    "gate1_task_card_001a_amendment_001_failed_missing_state_hash_contract",
    "gate1_task_card_001a_amendment_001_failed_missing_linkage_key",
    "gate1_task_card_001a_amendment_001_failed_linkage_leakage",
    "gate1_task_card_001a_amendment_001_failed_claim_inflation",
    "gate1_task_card_001a_amendment_001_invalid_artifact_mutation",
}
PROTECTED_FROM_B813651 = [
    "docs/codex/tasks/GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A.md",
    "artifacts/gate1_replay_consolidation_task_card_001a/GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A.md",
    "artifacts/gate1_replay_consolidation_task_card_001a/task_card_result.json",
]
PROTECTED_FROM_4E3E9F2 = [
    "docs/codex/tasks/GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001B-INDEPENDENT-AUDIT.md",
    "artifacts/gate1_replay_consolidation_task_card_001b_independent_audit/independent_audit_result.json",
    "artifacts/gate1_replay_consolidation_task_card_001b_independent_audit/audit_matrix.json",
    "artifacts/gate1_replay_consolidation_task_card_001b_independent_audit/missing_or_ambiguous_requirements.json",
    "artifacts/gate1_replay_consolidation_task_card_001b_independent_audit/execution_preflight_authorization.json",
]


def _read_json(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def _normalized_sha256_text(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def _git_show_text_sha(commit: str, relative_path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"],
        cwd=ROOT,
        capture_output=True,
        check=True,
        encoding="utf-8",
    )
    return _normalized_sha256_text(result.stdout)


def _current_text_sha(relative_path: str) -> str:
    return _normalized_sha256_text((ROOT / relative_path).read_text(encoding="utf-8"))


def test_amendment_artifacts_exist_parse_and_are_bounded():
    assert DOC_REPORT.exists()
    assert ARTIFACT_REPORT.exists()
    assert DOC_REPORT.read_text(encoding="utf-8") == ARTIFACT_REPORT.read_text(encoding="utf-8")
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})

    result = _read_json("amendment_result.json")
    assert result["task_id"] == TASK_ID
    assert result["layer"] == "bounded Gate1 task-card amendment only"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == VERDICT
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["base_task_card_anchor_commit"] == BASE_TASK_CARD_ANCHOR
    assert result["independent_audit_anchor_commit"] == INDEPENDENT_AUDIT_ANCHOR
    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING


def test_trace_replay_contract_requires_replay_boundary_hashes_and_linkage_table():
    patch = _read_json("trace_replay_contract_patch.json")

    assert set(patch["required_trace_replay_fields"]) == REQUIRED_TRACE_FIELDS
    assert patch["required_fields_status"]["state_hash_before_replay"] == "required"
    assert patch["required_fields_status"]["state_hash_after_replay"] == "required"
    assert patch["required_fields_status"]["replay_to_behavior_linkage_key"] == "required"
    assert patch["required_fields_status"]["replay_event_to_later_behavior_join_table"] == "required"
    assert patch["required_fields_status"]["linkage_key_collision_report"] == "required"
    assert set(patch["future_gate1_execution_required_artifacts"]) == REQUIRED_FUTURE_ARTIFACTS
    assert patch["hash_freeze_before_later_behavior_evaluation"] is True
    assert patch["mutation_check_after_later_behavior_evaluation"] is True


def test_linkage_key_is_deterministic_frozen_and_excludes_target_leakage():
    contract = _read_json("linkage_key_contract.json")

    assert contract["replay_to_behavior_linkage_key"]["required"] is True
    assert contract["replay_to_behavior_linkage_key"]["deterministic"] is True
    assert contract["replay_to_behavior_linkage_key"]["frozen_before_execution"] is True
    assert contract["replay_to_behavior_linkage_key"]["frozen_before_later_behavior_evaluation"] is True
    assert contract["replay_to_behavior_linkage_key"]["example_formula"] == (
        "sha256(gate1_run_id + target_case_id + replay_event_id + consolidation_event_id + later_behavior_eval_id)"
    )
    assert set(contract["replay_to_behavior_linkage_key"]["allowed_formula_inputs"]) == {
        "gate1_run_id",
        "target_case_id",
        "replay_event_id",
        "consolidation_event_id",
        "later_behavior_eval_id",
    }
    assert set(contract["replay_to_behavior_linkage_key"]["forbidden_formula_inputs"]) == FORBIDDEN_LINKAGE_INPUTS
    assert contract["linkage_key_uniqueness_check"]["required"] is True
    assert contract["linkage_key_collision_report"]["required"] is True


def test_audit_blocker_resolution_preserves_001b_failure_without_authorizing_execution():
    matrix = _read_json("audit_blocker_resolution_matrix.json")
    result = _read_json("amendment_result.json")
    manifest = _read_json("amended_task_card_manifest.json")

    blockers = {item["blocker_id"]: item for item in matrix["blockers"]}
    assert blockers["pre_post_replay_state_traces"]["resolved_by_amendment"] is True
    assert blockers["replay_to_behavior_linkage"]["resolved_by_amendment"] is True
    assert matrix["001b_historical_verdict_preserved"] == (
        "gate1_replay_consolidation_task_card_001b_failed_trace_replay_contract"
    )
    assert matrix["001b_artifacts_modified"] is False
    assert manifest["effective_task_card"] == "GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A plus AMENDMENT-001"
    assert manifest["base_001a_files_modified"] is False
    assert manifest["amendment_overlay_only"] is True
    assert manifest["gate1_execution_authorized"] is False
    assert result["gate1_execution_authorized"] is False
    assert result["gate1_execution_readiness_beyond_resolving_this_blocker"] is False
    assert all(value is False for value in result["authorization_flags"].values())


def test_anchor_artifacts_are_not_rewritten_by_the_amendment():
    for relative_path in PROTECTED_FROM_B813651:
        assert _current_text_sha(relative_path) == _git_show_text_sha(BASE_TASK_CARD_ANCHOR, relative_path)
    for relative_path in PROTECTED_FROM_4E3E9F2:
        assert _current_text_sha(relative_path) == _git_show_text_sha(INDEPENDENT_AUDIT_ANCHOR, relative_path)


def test_markdown_report_states_patch_scope_and_non_claims():
    text = DOC_REPORT.read_text(encoding="utf-8")

    assert VERDICT in text
    assert "state_hash_before_replay" in text
    assert "state_hash_after_replay" in text
    assert "replay_to_behavior_linkage_key" in text
    assert "Gate1 execution is not authorized" in text
    assert "001B failed audit verdict remains historical evidence" in text
    assert CLAIM_CEILING in text
    assert "This cannot prove Gate1 pass" in text
