from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001D-INDEPENDENT-AUDIT-001E"
PARENT_001D_TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B-BASELINE-LEGAL-INPUT-REPAIR-001D"
PARENT_001C_TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B-INDEPENDENT-AUDIT-001C"
PARENT_001B_TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B"
LAYER = "bounded independent audit / red-team audit of EGO-MAINLINE-ADMISSION-EXECUTABLE-001B-BASELINE-LEGAL-INPUT-REPAIR-001D only"
CLAIM_CEILING = (
    "bounded independent audit evidence for 001D baseline-legal-input repair "
    "under synthetic / controlled conditions only"
)
ARTIFACT_DIR_REL = "artifacts/ego_mainline_admission_executable_001d_independent_audit_001e"
PARENT_001D_ARTIFACT_DIR_REL = "artifacts/ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d"
PARENT_001C_ARTIFACT_DIR_REL = "artifacts/ego_mainline_admission_executable_001b_independent_audit_001c"
PARENT_001B_ARTIFACT_DIR_REL = "artifacts/ego_mainline_admission_executable_001b"
PARENT_001D_SOURCE_DIR_REL = "src/ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d"

VERDICT_PASS = "ego_mainline_admission_executable_001d_independent_audit_001e_pass"
VERDICT_PASS_WITH_CAVEATS = "ego_mainline_admission_executable_001d_independent_audit_001e_pass_with_caveats"
VERDICT_BLOCK_PARENT = "ego_mainline_admission_executable_001d_independent_audit_001e_block_missing_parent_anchor"
VERDICT_BLOCK_001C = "ego_mainline_admission_executable_001d_independent_audit_001e_block_001c_not_preserved"
VERDICT_BLOCK_REPAIR_SCOPE = "ego_mainline_admission_executable_001d_independent_audit_001e_block_repair_scope_expanded"
VERDICT_BLOCK_BASELINE_LEGAL = "ego_mainline_admission_executable_001d_independent_audit_001e_block_baseline_legal_input_gap"
VERDICT_BLOCK_EQUIVALENT_LABEL = "ego_mainline_admission_executable_001d_independent_audit_001e_block_equivalent_label_leakage"
VERDICT_BLOCK_RUNTIME_GUARD = "ego_mainline_admission_executable_001d_independent_audit_001e_block_runtime_guard_gap"
VERDICT_BLOCK_STATIC_SCAN = "ego_mainline_admission_executable_001d_independent_audit_001e_block_baseline_static_scan_gap"
VERDICT_BLOCK_INVOCATION = "ego_mainline_admission_executable_001d_independent_audit_001e_block_baseline_invocation_gap"
VERDICT_BLOCK_INDEPENDENCE = "ego_mainline_admission_executable_001d_independent_audit_001e_block_baseline_independence_gap"
VERDICT_BLOCK_FAILURE_PATH = "ego_mainline_admission_executable_001d_independent_audit_001e_block_failure_path_gap"
VERDICT_BLOCK_METRIC = "ego_mainline_admission_executable_001d_independent_audit_001e_block_metric_provenance_gap"
VERDICT_BLOCK_ABLATION = "ego_mainline_admission_executable_001d_independent_audit_001e_block_ablation_gap"
VERDICT_BLOCK_LEAKAGE = "ego_mainline_admission_executable_001d_independent_audit_001e_block_leakage_gap"
VERDICT_BLOCK_REPLAY = "ego_mainline_admission_executable_001d_independent_audit_001e_block_replay_gap"
VERDICT_BLOCK_UNUSED_FROZEN = "ego_mainline_admission_executable_001d_independent_audit_001e_block_unused_frozen_input"
VERDICT_BLOCK_OLD_MUTATION = "ego_mainline_admission_executable_001d_independent_audit_001e_block_old_artifact_mutation"
VERDICT_BLOCK_NEGATIVE = "ego_mainline_admission_executable_001d_independent_audit_001e_block_negative_evidence_rewrite"
VERDICT_BLOCK_SCOPE = "ego_mainline_admission_executable_001d_independent_audit_001e_block_scope_leak"
VERDICT_BLOCK_CLAIM = "ego_mainline_admission_executable_001d_independent_audit_001e_block_claim_inflation"

ANCHORS = {
    "remote-anchor-001s-3d90e1a": "3d90e1adf342c1e889e99c18ef27d2071e352151",
    "remote-anchor-001r-0fdf451": "0fdf4518a66b4690a456dbf5e2f83c25db76f86e",
    "remote-anchor-001q-60a504e": "60a504e4d44f3aee169d97944b36d7f009eea432",
    "remote-anchor-001p-cda09dc": "cda09dce5d8412beea88e9b2108ea41c1ce260bd",
    "remote-anchor-001o-f648dac": "f648dac4bfbcdc7a98c1edea5a97dbef4101d83a",
}

REPAIRED_BLOCKERS = [
    "baseline_illegal_verifier_label_consumption",
    "baseline_non_invocation",
    "missing_same_surface_positive_control",
]

FORBIDDEN_BASELINE_FIELDS = {
    "verifier_expected_action_id",
    "expected_action_id",
    "gold_action",
    "label",
    "oracle_action",
    "answer_key",
    "later_action_label",
    "future_observation",
    "future_partner_response",
    "post_hoc_metric",
    "verifier_only_field",
    "test_only_schema_path",
}

REQUIRED_METRIC_FIELDS = {
    "metric_id",
    "metric_name",
    "producer_function",
    "producer_module",
    "code_path_hash",
    "run_id",
    "episode_ids",
    "seed_ids",
    "train_context_ids_consumed",
    "heldout_context_ids_consumed",
    "counterfactual_pair_ids_consumed",
    "input_artifact_paths",
    "input_artifact_hashes",
    "input_row_count",
    "output_artifact_path",
    "output_row_ids",
    "aggregation_rule",
    "threshold_used",
    "threshold_frozen_before_run",
    "computed_not_literal",
    "failure_path_available",
}

AUTHORIZATION_FLAGS = {
    "ego_repository_modification_authorized": False,
    "ego_mainline_runtime_authorized": False,
    "bridge_runtime_authorized": False,
    "companion_behavior_authorized": False,
    "llm_rag_authorized": False,
    "user_model_authorized": False,
    "relationship_authorized": False,
    "emotion_authorized": False,
    "personalization_product_demo_authorized": False,
    "romance_attachment_authorized": False,
    "persistent_profile_authorized": False,
    "long_term_human_user_memory_authorized": False,
    "real_user_data_authorized": False,
    "runtime_or_product_work_authorized": False,
}

STOP_ORDER = [
    ("missing_parent_anchor", VERDICT_BLOCK_PARENT),
    ("001c_not_preserved", VERDICT_BLOCK_001C),
    ("repair_scope_expanded", VERDICT_BLOCK_REPAIR_SCOPE),
    ("baseline_legal_input_gap", VERDICT_BLOCK_BASELINE_LEGAL),
    ("equivalent_label_leakage", VERDICT_BLOCK_EQUIVALENT_LABEL),
    ("runtime_guard_gap", VERDICT_BLOCK_RUNTIME_GUARD),
    ("baseline_static_scan_gap", VERDICT_BLOCK_STATIC_SCAN),
    ("baseline_invocation_gap", VERDICT_BLOCK_INVOCATION),
    ("baseline_independence_gap", VERDICT_BLOCK_INDEPENDENCE),
    ("failure_path_gap", VERDICT_BLOCK_FAILURE_PATH),
    ("metric_provenance_gap", VERDICT_BLOCK_METRIC),
    ("ablation_gap", VERDICT_BLOCK_ABLATION),
    ("leakage_gap", VERDICT_BLOCK_LEAKAGE),
    ("replay_gap", VERDICT_BLOCK_REPLAY),
    ("unused_frozen_input", VERDICT_BLOCK_UNUSED_FROZEN),
    ("old_artifact_mutation", VERDICT_BLOCK_OLD_MUTATION),
    ("negative_evidence_rewrite", VERDICT_BLOCK_NEGATIVE),
    ("scope_leak", VERDICT_BLOCK_SCOPE),
    ("claim_inflation", VERDICT_BLOCK_CLAIM),
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel_path(path: Path, repo_root: Path) -> str:
    return str(path.relative_to(repo_root)).replace("\\", "/")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def evaluate_verdict(stop_flags: dict[str, bool]) -> tuple[str, list[str]]:
    triggered = [condition for condition, _verdict in STOP_ORDER if stop_flags.get(condition)]
    for condition, verdict in STOP_ORDER:
        if stop_flags.get(condition):
            return verdict, triggered
    return VERDICT_PASS, []
