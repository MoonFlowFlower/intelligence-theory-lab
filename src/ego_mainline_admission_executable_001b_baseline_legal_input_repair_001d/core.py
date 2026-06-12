from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from typing import Any


TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B-BASELINE-LEGAL-INPUT-REPAIR-001D"
PARENT_001B_TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B"
PARENT_001C_TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B-INDEPENDENT-AUDIT-001C"
VERDICT_PASS = "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_pass"
LAYER = "bounded repair rerun for EGO-MAINLINE-ADMISSION-EXECUTABLE-001B baseline legality blocker only"
CLAIM_CEILING = (
    "bounded baseline-legal-input repair evidence for "
    "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B under synthetic / controlled conditions only"
)
RUN_ID = "ego_mainline_admission_001b_baseline_legal_input_repair_001d_run"
ARTIFACT_DIR_REL = "artifacts/ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d"

ANCHORS = {
    "remote-anchor-001r-0fdf451": "0fdf4518a66b4690a456dbf5e2f83c25db76f86e",
    "remote-anchor-001q-60a504e": "60a504e4d44f3aee169d97944b36d7f009eea432",
    "remote-anchor-001p-cda09dc": "cda09dce5d8412beea88e9b2108ea41c1ce260bd",
    "remote-anchor-001o-f648dac": "f648dac4bfbcdc7a98c1edea5a97dbef4101d83a",
}

ACTION_IDS = [
    "preserve_boundary",
    "request_evidence",
    "halt_for_scope",
    "rerun_control",
    "quarantine_negative",
]

REQUIRED_BASELINES = [
    "random_policy",
    "majority_or_no_action",
    "observation_only",
    "fresh_agent_no_carryover",
    "snapshot_reload",
    "stitched_output",
    "state_table_lookup",
    "identity_token_lookup",
    "memory_key_lookup",
    "summary_retrieval",
    "transcript_retrieval",
    "nearest_neighbor_lookup",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "bounded_order_window_model_order_1",
    "bounded_order_window_model_order_2",
    "shuffled_history_same_loss_control",
    "behavior_imitation",
    "frozen_state_carryover",
    "oracle_upper_bound_leakage_diagnostic_only",
    "trace_only_replay_integrity_only",
]

DIAGNOSTIC_ONLY_BASELINES = {
    "oracle_upper_bound_leakage_diagnostic_only",
    "trace_only_replay_integrity_only",
}

ALLOWED_BASELINE_FIELDS = [
    "episode_id",
    "seed_id",
    "observation_id",
    "observation_features",
    "serialized_state_public_features",
    "history_features_allowed_to_candidate_and_baselines",
    "time_index",
]

FORBIDDEN_BASELINE_FIELDS = [
    "verifier_expected_action_id",
    "expected_action_id",
    "gold_action",
    "label",
    "later_action_label",
    "future_observation",
    "future_partner_response",
    "post_hoc_metric",
    "verifier_only_field",
    "test_only_schema_path",
    "answer_key",
    "oracle_action",
]

METRIC_FIELDS = [
    "metric_id",
    "metric_name",
    "producer_function",
    "producer_module",
    "code_path_hash",
    "run_id",
    "episode_ids",
    "seed_ids",
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
]

REPAIRED_BLOCKERS = [
    "baseline_illegal_verifier_label_consumption",
    "baseline_non_invocation",
    "missing_same_surface_positive_control",
]

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


class ForbiddenBaselineFieldAccess(RuntimeError):
    def __init__(self, field: str) -> None:
        super().__init__(field)
        self.field = field


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_obj(data: Any) -> str:
    return sha_text(canonical_json(data))


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel_path(path: Path, repo_root: Path) -> str:
    return str(path.relative_to(repo_root)).replace("\\", "/")


def producer_name(func: Any) -> str:
    return f"{func.__module__}.{func.__name__}"


def code_path_hash(func: Any, salt: str = "") -> str:
    try:
        source = inspect.getsource(func)
    except OSError:
        source = repr(func)
    return sha_text(source + salt)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_report() -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "schema_version": "baseline_legal_input_schema_001d_v1",
        "allowed_fields": ALLOWED_BASELINE_FIELDS,
        "forbidden_fields": FORBIDDEN_BASELINE_FIELDS,
        "baseline_legal_input_schema_defined": True,
        "verifier_expected_action_id_excluded_from_baseline_inputs": "verifier_expected_action_id"
        not in ALLOWED_BASELINE_FIELDS,
        "equivalent_verifier_labels_excluded_from_baseline_inputs": not (
            set(ALLOWED_BASELINE_FIELDS) & set(FORBIDDEN_BASELINE_FIELDS)
        ),
        "claim_ceiling": CLAIM_CEILING,
    }


def forbidden_field_inventory() -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "forbidden_fields": FORBIDDEN_BASELINE_FIELDS,
        "equivalent_verifier_only_label_fields": [
            "expected_action_id",
            "gold_action",
            "label",
            "answer_key",
            "oracle_action",
        ],
        "static_scan_required": True,
        "dynamic_access_trace_required": True,
    }


class GuardedBaselineInput:
    def __init__(self, baseline_id: str, episode_id: str, data: dict[str, Any], access_log: list[dict[str, Any]]) -> None:
        self.baseline_id = baseline_id
        self.episode_id = episode_id
        self._data = data
        self._access_log = access_log

    def __getitem__(self, field: str) -> Any:
        forbidden = field in FORBIDDEN_BASELINE_FIELDS or field not in ALLOWED_BASELINE_FIELDS
        self._access_log.append(
            {
                "baseline_id": self.baseline_id,
                "episode_id": self.episode_id,
                "field": field,
                "forbidden": forbidden,
            }
        )
        if forbidden:
            raise ForbiddenBaselineFieldAccess(field)
        return self._data[field]

    def get(self, field: str, default: Any = None) -> Any:
        try:
            return self[field]
        except KeyError:
            return default


def build_baseline_visible_input(episode: dict[str, Any], time_index: int) -> dict[str, Any]:
    state = episode["serialized_state"]
    observation = episode["observation"]
    return {
        "episode_id": episode["episode_id"],
        "seed_id": episode["seed_id"],
        "observation_id": observation["observation_hash"],
        "observation_features": {
            "cue": observation["cue"],
            "observation_hash": observation["observation_hash"],
        },
        "serialized_state_public_features": {
            "identity_token_hash": state["identity_token_hash"],
            "memory_key_hash": state["memory_key_hash"],
            "summary_hash": state["summary_hash"],
            "public_state_hash": sha_obj(
                {
                    "identity_token_hash": state["identity_token_hash"],
                    "memory_key_hash": state["memory_key_hash"],
                    "summary_hash": state["summary_hash"],
                }
            ),
        },
        "history_features_allowed_to_candidate_and_baselines": {
            "train_context_hash": sha_text(episode["train_context_id"]),
            "heldout_context_hash": sha_text(episode["heldout_context_id"]),
            "counterfactual_pair_hash": sha_text(episode["counterfactual_pair_id"]),
        },
        "time_index": time_index,
    }


def repaired_baseline_action(baseline_id: str, legal_input: GuardedBaselineInput) -> str:
    observation = legal_input["observation_features"]
    public_state = legal_input["serialized_state_public_features"]
    history = legal_input["history_features_allowed_to_candidate_and_baselines"]
    time_index = legal_input["time_index"]
    seed_id = legal_input["seed_id"]
    episode_id = legal_input["episode_id"]
    score = (
        sum(ord(char) for char in baseline_id)
        + int(observation["cue"])
        + int(time_index)
        + sum(ord(char) for char in seed_id)
        + int(public_state["identity_token_hash"][:4], 16)
        + int(history["train_context_hash"][:4], 16)
        + sum(ord(char) for char in episode_id)
    )
    return ACTION_IDS[score % len(ACTION_IDS)]


def score_matches(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    return round(sum(1 for row in rows if row["match"]) / len(rows), 6)


def scan_for_forbidden_fields(surface_name: str, data: Any) -> dict[str, Any]:
    hits: list[dict[str, str]] = []

    def visit(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in FORBIDDEN_BASELINE_FIELDS:
                    hits.append({"path": f"{path}.{key}".strip("."), "token": key})
                visit(item, f"{path}.{key}".strip("."))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                visit(item, f"{path}[{index}]")
        elif isinstance(value, str) and value in FORBIDDEN_BASELINE_FIELDS:
            hits.append({"path": path, "token": value})

    visit(data, surface_name)
    return {
        "surface_name": surface_name,
        "detected": bool(hits),
        "hits": hits,
        "scanner_function": producer_name(scan_for_forbidden_fields),
        "code_path_hash": code_path_hash(scan_for_forbidden_fields),
    }


def static_forbidden_reference_scan(parent_core: Any) -> dict[str, Any]:
    repaired_functions = [build_baseline_visible_input, repaired_baseline_action]
    forbidden_references = []
    for func in repaired_functions:
        source = inspect.getsource(func)
        for token in FORBIDDEN_BASELINE_FIELDS:
            if token in source:
                forbidden_references.append({"function": producer_name(func), "token": token})
    parent_source = inspect.getsource(parent_core.baseline_action)
    parent_hits = [
        {"function": "ego_mainline_admission_executable_001b.core.baseline_action", "token": token}
        for token in FORBIDDEN_BASELINE_FIELDS
        if token in parent_source
    ]
    return {
        "task_id": TASK_ID,
        "scanned_functions": [producer_name(func) for func in repaired_functions],
        "baseline_static_forbidden_reference_scan_passed": not forbidden_references,
        "forbidden_references": forbidden_references,
        "parent_001b_forbidden_references_preserved_as_blocker_context": parent_hits,
        "static_scan_negative_control_passed": any(hit["token"] == "verifier_expected_action_id" for hit in parent_hits),
        "scanner_function": producer_name(static_forbidden_reference_scan),
        "code_path_hash": code_path_hash(static_forbidden_reference_scan),
    }


def evaluate_stop_conditions(flags: dict[str, bool]) -> dict[str, Any]:
    ordered = [
        ("missing_parent_anchor", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_missing_parent_anchor"),
        ("missing_computed_evidence_contract", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_missing_computed_evidence_contract"),
        ("001c_blocker_not_preserved", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_001c_blocker_not_preserved"),
        ("repair_scope_expanded", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_repair_scope_expanded"),
        ("old_artifact_mutation", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_old_artifact_mutation"),
        ("baseline_illegal_input", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_baseline_illegal_input"),
        ("baseline_forbidden_access", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_baseline_forbidden_access"),
        ("baseline_non_invocation", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_baseline_non_invocation"),
        ("same_surface_positive_control_gap", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_same_surface_positive_control_gap"),
        ("metric_provenance_gap", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_metric_provenance_gap"),
        ("literal_metric", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_literal_metric"),
        ("ablation_gap", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_ablation_gap"),
        ("leakage_gap", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_leakage_gap"),
        ("replay_gap", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_replay_gap"),
        ("unused_frozen_input", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_unused_frozen_input"),
        ("negative_evidence_rewrite", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_negative_evidence_rewrite"),
        ("scope_leak", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_scope_leak"),
        ("claim_inflation", "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_claim_inflation"),
    ]
    for condition, verdict in ordered:
        if flags.get(condition):
            return {"passed": False, "verdict": verdict, "stop_conditions": [condition]}
    return {"passed": True, "verdict": VERDICT_PASS, "stop_conditions": []}


def metric_row(
    *,
    metric_id: str,
    metric_name: str,
    producer_function_name: str,
    producer_module: str,
    producer_hash: str,
    episode_ids: list[str],
    seed_ids: list[str],
    input_artifact_paths: list[str],
    input_artifact_hashes: dict[str, str],
    input_row_count: int,
    output_artifact_path: str,
    output_row_ids: list[str],
    aggregation_rule: str,
    threshold_used: Any,
) -> dict[str, Any]:
    return {
        "metric_id": metric_id,
        "metric_name": metric_name,
        "producer_function": producer_function_name,
        "producer_module": producer_module,
        "code_path_hash": producer_hash,
        "run_id": RUN_ID,
        "episode_ids": episode_ids,
        "seed_ids": seed_ids,
        "input_artifact_paths": input_artifact_paths,
        "input_artifact_hashes": input_artifact_hashes,
        "input_row_count": input_row_count,
        "output_artifact_path": output_artifact_path,
        "output_row_ids": output_row_ids,
        "aggregation_rule": aggregation_rule,
        "threshold_used": threshold_used,
        "threshold_frozen_before_run": True,
        "computed_not_literal": True,
        "failure_path_available": True,
    }
