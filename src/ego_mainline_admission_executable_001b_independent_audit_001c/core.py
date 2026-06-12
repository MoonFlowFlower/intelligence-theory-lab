from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B-INDEPENDENT-AUDIT-001C"
PARENT_TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B"
LAYER = "bounded independent audit / red-team audit of EGO-MAINLINE-ADMISSION-EXECUTABLE-001B only"
CLAIM_CEILING = (
    "bounded independent audit evidence for EGO-MAINLINE-ADMISSION-EXECUTABLE-001B "
    "under synthetic / controlled conditions only"
)
ARTIFACT_DIR_REL = "artifacts/ego_mainline_admission_executable_001b_independent_audit_001c"
PARENT_ARTIFACT_DIR_REL = "artifacts/ego_mainline_admission_executable_001b"
PARENT_SOURCE_DIR_REL = "src/ego_mainline_admission_executable_001b"

VERDICT_PASS = "ego_mainline_admission_executable_001b_independent_audit_001c_pass"
VERDICT_BLOCK_BASELINE = "ego_mainline_admission_executable_001b_independent_audit_001c_block_baseline_gap"
VERDICT_BLOCK_FAILURE_PATH = (
    "ego_mainline_admission_executable_001b_independent_audit_001c_block_failure_path_gap"
)
VERDICT_BLOCK_PARENT = (
    "ego_mainline_admission_executable_001b_independent_audit_001c_block_missing_parent_anchor"
)

ANCHORS = {
    "remote-anchor-001q-60a504e": "60a504e4d44f3aee169d97944b36d7f009eea432",
    "remote-anchor-001p-cda09dc": "cda09dce5d8412beea88e9b2108ea41c1ce260bd",
    "remote-anchor-001o-f648dac": "f648dac4bfbcdc7a98c1edea5a97dbef4101d83a",
}

REQUIRED_ARTIFACTS = [
    "result.json",
    "parent_anchor_verification.json",
    "contract_coverage_matrix.json",
    "metric_provenance_audit.json",
    "baseline_independence_audit.json",
    "baseline_invocation_audit.json",
    "ablation_rerun_audit.json",
    "ablation_sensitivity_audit.json",
    "leakage_surface_audit.json",
    "leakage_positive_control_audit.json",
    "manual_injection_independence_audit.json",
    "metadata_whitelist_scope_audit.json",
    "behavior_causal_replay_audit.json",
    "frozen_input_consumption_audit.json",
    "source_artifact_integrity_audit.json",
    "old_artifact_mutation_audit.json",
    "failure_path_test_audit.json",
    "negative_evidence_preservation_audit.json",
    "claim_ceiling_audit.json",
    "scope_leak_audit.json",
    "audit_finding_inventory.json",
    "claim_ceiling.txt",
]

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

REQUIRED_SURFACES = {
    "candidate_inputs",
    "trace_rows",
    "observation_rows",
    "serialized_state_snapshots",
    "serialized_state_provenance_rows",
    "metric_provenance_rows",
    "artifact_path_inventory",
    "fixture_names",
    "labels",
    "verifier_only_fields",
    "future_observations",
    "future_partner_responses",
    "later_action_labels",
    "post_hoc_metrics",
    "test_only_schema_paths",
    "renderer_visible_behavior_where_applicable",
}

REQUIRED_FAILURE_CONTROLS = {
    "literal_metric",
    "static_baseline_dictionary",
    "baseline_non_invocation",
    "ablation_not_rerun",
    "copied_ablation_output",
    "scanner_not_fail_able",
    "missing_same_surface_positive_control",
    "global_metadata_whitelist",
    "hash_only_replay_for_behavior_claim",
    "unused_frozen_input",
    "001B_positive_evidence_leak",
    "001C_positive_evidence_leak",
    "001D_caveat_missing",
    "scope_leak",
    "claim_inflation",
    "Ego_repo_modification",
}

PARENT_FAILURE_CONTROL_ALIASES = {
    "literal_metric": {"literal_metric_detected"},
    "static_baseline_dictionary": {"static_baseline_dictionary_detected"},
    "baseline_non_invocation": {"baseline_invocation_missing"},
    "ablation_not_rerun": {"ablation_not_rerun"},
    "copied_ablation_output": {"ablation_output_copied"},
    "scanner_not_fail_able": {"scanner_not_fail_able"},
    "missing_same_surface_positive_control": {"same_surface_positive_control_missing"},
    "global_metadata_whitelist": {"metadata_whitelist_not_surface_scoped"},
    "hash_only_replay_for_behavior_claim": {"hash_only_replay_for_behavior_claim"},
    "unused_frozen_input": {"unused_frozen_input"},
    "001B_positive_evidence_leak": {"001b_positive_evidence_leak"},
    "001C_positive_evidence_leak": {"001c_positive_evidence_leak"},
    "001D_caveat_missing": {"001d_caveat_missing"},
    "scope_leak": {"scope_leak"},
    "claim_inflation": {"claim_inflation"},
    "Ego_repo_modification": {"ego_repository_modification"},
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
    "runtime_or_product_work_authorized": False,
}


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
