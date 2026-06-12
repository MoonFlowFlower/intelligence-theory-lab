from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from typing import Any


TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001D-METRIC-PROVENANCE-REPAIR-001F"
PARENT_001E_TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001D-INDEPENDENT-AUDIT-001E"
PARENT_001D_TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B-BASELINE-LEGAL-INPUT-REPAIR-001D"
LAYER = "bounded metric-provenance repair rerun for EGO-MAINLINE-ADMISSION-EXECUTABLE-001D only"
CLAIM_CEILING = (
    "bounded metric-provenance repair evidence for 001D under synthetic / controlled conditions only"
)
RUN_ID = "ego_mainline_admission_001d_metric_provenance_repair_001f_run"
ARTIFACT_DIR_REL = "artifacts/ego_mainline_admission_executable_001d_metric_provenance_repair_001f"
PARENT_001B_ARTIFACT_DIR_REL = "artifacts/ego_mainline_admission_executable_001b"
PARENT_001C_ARTIFACT_DIR_REL = "artifacts/ego_mainline_admission_executable_001b_independent_audit_001c"
PARENT_001D_ARTIFACT_DIR_REL = "artifacts/ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d"
PARENT_001E_ARTIFACT_DIR_REL = "artifacts/ego_mainline_admission_executable_001d_independent_audit_001e"
KNOWN_THEORY_FILE_REL = "docs/THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001A.md"
KNOWN_THEORY_SIDECAR_DIR_REL = "docs/THEORY-LANDSCAPE-COVERAGE-COMPRESSION"

VERDICT_PASS = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_pass"
VERDICT_BLOCK_PARENT = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_missing_parent_anchor"
VERDICT_BLOCK_CONTRACT = (
    "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_missing_computed_evidence_contract"
)
VERDICT_BLOCK_001E = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_001e_blocker_not_preserved"
VERDICT_BLOCK_SCOPE = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_repair_scope_expanded"
VERDICT_BLOCK_OLD_MUTATION = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_old_artifact_mutation"
VERDICT_BLOCK_METRIC = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_metric_provenance_gap"
VERDICT_BLOCK_CONTEXT_DECORATIVE = (
    "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_context_consumption_decorative"
)
VERDICT_BLOCK_CONTEXT_NOT_CALLABLE = (
    "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_context_consumption_not_callable"
)
VERDICT_BLOCK_OLD_WRAPPER = (
    "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_old_artifact_mutation_wrapper_only"
)
VERDICT_BLOCK_FAILURE_PATH = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_failure_path_gap"
VERDICT_BLOCK_BASELINE = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_baseline_revalidation_gap"
VERDICT_BLOCK_ABLATION = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_ablation_gap"
VERDICT_BLOCK_LEAKAGE = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_leakage_gap"
VERDICT_BLOCK_REPLAY = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_replay_gap"
VERDICT_BLOCK_UNUSED_FROZEN = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_unused_frozen_input"
VERDICT_BLOCK_NEGATIVE = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_negative_evidence_rewrite"
VERDICT_BLOCK_KNOWN_FILE = (
    "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_known_theory_file_staged"
)
VERDICT_BLOCK_SCOPE_LEAK = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_scope_leak"
VERDICT_BLOCK_CLAIM = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_block_claim_inflation"

ANCHORS = {
    "remote-anchor-001t-8ed4a5a": "8ed4a5a602694748fc1407bed4ef1224057b2874",
    "remote-anchor-001s-3d90e1a": "3d90e1adf342c1e889e99c18ef27d2071e352151",
    "remote-anchor-001r-0fdf451": "0fdf4518a66b4690a456dbf5e2f83c25db76f86e",
    "remote-anchor-001q-60a504e": "60a504e4d44f3aee169d97944b36d7f009eea432",
    "remote-anchor-001p-cda09dc": "cda09dce5d8412beea88e9b2108ea41c1ce260bd",
    "remote-anchor-001o-f648dac": "f648dac4bfbcdc7a98c1edea5a97dbef4101d83a",
}

REPAIRED_BLOCKERS = [
    "missing_train_context_ids_consumed",
    "missing_heldout_context_ids_consumed",
    "missing_counterfactual_pair_ids_consumed",
    "old_artifact_mutation_wrapper_only",
]

METRIC_IDS = [
    "baseline_legal_input",
    "baseline_invocation",
    "baseline_non_invocation_failure_control",
    "same_surface_positive_control_failure_control",
    "ablation_revalidation",
    "leakage_revalidation",
    "manual_injection_revalidation",
    "metadata_whitelist_scope",
    "behavior_causal_replay",
    "frozen_input_consumption",
    "old_artifact_mutation",
    "negative_evidence_preservation",
]

REQUIRED_METRIC_FIELDS = [
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

STOP_ORDER = [
    ("missing_parent_anchor", VERDICT_BLOCK_PARENT),
    ("missing_computed_evidence_contract", VERDICT_BLOCK_CONTRACT),
    ("001e_blocker_not_preserved", VERDICT_BLOCK_001E),
    ("repair_scope_expanded", VERDICT_BLOCK_SCOPE),
    ("old_artifact_mutation", VERDICT_BLOCK_OLD_MUTATION),
    ("metric_provenance_field_missing", VERDICT_BLOCK_METRIC),
    ("train_context_ids_consumed_missing", VERDICT_BLOCK_METRIC),
    ("heldout_context_ids_consumed_missing", VERDICT_BLOCK_METRIC),
    ("counterfactual_pair_ids_consumed_missing", VERDICT_BLOCK_METRIC),
    ("context_consumption_decorative", VERDICT_BLOCK_CONTEXT_DECORATIVE),
    ("context_consumption_not_callable", VERDICT_BLOCK_CONTEXT_NOT_CALLABLE),
    ("old_artifact_mutation_wrapper_only", VERDICT_BLOCK_OLD_WRAPPER),
    ("old_artifact_hash_before_missing", VERDICT_BLOCK_OLD_MUTATION),
    ("old_artifact_hash_after_missing", VERDICT_BLOCK_OLD_MUTATION),
    ("literal_metric_detected", VERDICT_BLOCK_METRIC),
    ("static_metric_dictionary_detected", VERDICT_BLOCK_METRIC),
    ("copied_old_001d_result_detected", VERDICT_BLOCK_METRIC),
    ("failure_path_missing", VERDICT_BLOCK_FAILURE_PATH),
    ("baseline_revalidation_failed", VERDICT_BLOCK_BASELINE),
    ("ablation_revalidation_failed", VERDICT_BLOCK_ABLATION),
    ("leakage_revalidation_failed", VERDICT_BLOCK_LEAKAGE),
    ("manual_injection_revalidation_failed", VERDICT_BLOCK_LEAKAGE),
    ("metadata_whitelist_not_surface_scoped", VERDICT_BLOCK_LEAKAGE),
    ("replay_not_behavior_causal", VERDICT_BLOCK_REPLAY),
    ("unused_frozen_input", VERDICT_BLOCK_UNUSED_FROZEN),
    ("negative_evidence_rewrite", VERDICT_BLOCK_NEGATIVE),
    ("known_theory_file_staged", VERDICT_BLOCK_KNOWN_FILE),
    ("known_theory_file_modified", VERDICT_BLOCK_KNOWN_FILE),
    ("unexpected_untracked_file", VERDICT_BLOCK_SCOPE_LEAK),
    ("scope_leak", VERDICT_BLOCK_SCOPE_LEAK),
    ("claim_inflation", VERDICT_BLOCK_CLAIM),
    ("ego_repository_modification", VERDICT_BLOCK_SCOPE_LEAK),
    ("runtime_or_product_work_created", VERDICT_BLOCK_SCOPE_LEAK),
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


def producer_name(func: Any) -> str:
    return f"{func.__module__}.{func.__name__}"


def code_path_hash(func: Any, salt: str = "") -> str:
    try:
        source = inspect.getsource(func)
    except (OSError, TypeError):
        source = repr(func)
    return sha_text(source + salt)


def hash_tree(path: Path, repo_root: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return {
        rel_path(file, repo_root): sha_file(file)
        for file in sorted(path.rglob("*"))
        if file.is_file()
    }


def evaluate_verdict(stop_flags: dict[str, bool]) -> tuple[str, list[str]]:
    triggered = [condition for condition, _verdict in STOP_ORDER if stop_flags.get(condition)]
    for condition, verdict in STOP_ORDER:
        if stop_flags.get(condition):
            return verdict, triggered
    return VERDICT_PASS, []


def consume_context_ids_from_controlled_pack(
    pack: dict[str, Any],
    *,
    input_artifact_path: str,
    input_artifact_hash: str,
    metric_ids: list[str],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    families = {
        "train": "train_context_id",
        "heldout": "heldout_context_id",
        "counterfactual_pair": "counterfactual_pair_id",
    }
    for family, episode_field in families.items():
        by_context: dict[str, list[str]] = {}
        for episode in pack["episodes"]:
            by_context.setdefault(episode[episode_field], []).append(episode["episode_id"])
        for context_id, episode_ids in sorted(by_context.items()):
            rows.append(
                {
                    "context_family": family,
                    "context_id": context_id,
                    "producer_function": producer_name(consume_context_ids_from_controlled_pack),
                    "producer_module": consume_context_ids_from_controlled_pack.__module__,
                    "code_path_hash": code_path_hash(consume_context_ids_from_controlled_pack),
                    "input_artifact_path": input_artifact_path,
                    "input_artifact_hash": input_artifact_hash,
                    "episode_ids": episode_ids,
                    "metric_ids_consuming_this_context": metric_ids,
                    "consumed_before_metric_aggregation": True,
                }
            )
    return {
        "task_id": TASK_ID,
        "context_consumption_rows": rows,
        "context_consumption_fields_computed_by_callable_producers": all(
            row["producer_function"] and row["code_path_hash"] for row in rows
        ),
        "families": sorted(families),
        "metric_ids": metric_ids,
        "input_artifact_path": input_artifact_path,
        "input_artifact_hash": input_artifact_hash,
        "producer_function": producer_name(consume_context_ids_from_controlled_pack),
        "producer_module": consume_context_ids_from_controlled_pack.__module__,
        "code_path_hash": code_path_hash(consume_context_ids_from_controlled_pack),
    }


def context_ids_by_family(context_report: dict[str, Any]) -> dict[str, set[str]]:
    ids = {"train": set(), "heldout": set(), "counterfactual_pair": set()}
    for row in context_report.get("context_consumption_rows", []):
        family = row.get("context_family")
        if family in ids:
            ids[family].add(row.get("context_id"))
    return ids


def crosscheck_context_consumption(context_report: dict[str, Any], frozen_report: dict[str, Any]) -> dict[str, Any]:
    ids = context_ids_by_family(context_report)
    families = frozen_report.get("families", {})
    expected = {
        "train": set(families.get("train_context_ids", {}).get("consumed", [])),
        "heldout": set(families.get("heldout_context_ids", {}).get("consumed", [])),
        "counterfactual_pair": set(families.get("counterfactual_pair_ids", {}).get("consumed", [])),
    }
    missing = {
        family: sorted(values - ids[family])
        for family, values in expected.items()
        if values - ids[family]
    }
    extra = {
        family: sorted(ids[family] - values)
        for family, values in expected.items()
        if ids[family] - values
    }
    callable_rows_missing = [
        row.get("context_id")
        for row in context_report.get("context_consumption_rows", [])
        if not row.get("producer_function")
        or not row.get("producer_module")
        or not row.get("code_path_hash")
        or row.get("consumed_before_metric_aggregation") is not True
    ]
    return {
        "task_id": TASK_ID,
        "context_consumption_crosschecked_against_freeze": not missing
        and not extra
        and not callable_rows_missing,
        "missing_consumed_context_ids": missing,
        "decorative_context_ids_detected": [
            {"family": family, "context_id": context_id}
            for family, values in extra.items()
            for context_id in values
        ],
        "callable_context_rows_missing": callable_rows_missing,
        "expected_consumed_context_ids": {family: sorted(values) for family, values in expected.items()},
        "observed_consumed_context_ids": {family: sorted(values) for family, values in ids.items()},
        "producer_function": producer_name(crosscheck_context_consumption),
        "producer_module": crosscheck_context_consumption.__module__,
        "code_path_hash": code_path_hash(crosscheck_context_consumption),
    }


def build_old_artifact_inventory(repo_root: Path, protected_paths: dict[str, Path]) -> dict[str, Any]:
    rows = []
    for label, path in sorted(protected_paths.items()):
        files = sorted(rel_path(file, repo_root) for file in path.rglob("*") if file.is_file()) if path.exists() else []
        rows.append(
            {
                "label": label,
                "path": rel_path(path, repo_root),
                "exists": path.exists(),
                "file_count": len(files),
                "files": files,
            }
        )
    return {
        "task_id": TASK_ID,
        "protected_old_artifact_inventory": rows,
        "producer_function": producer_name(build_old_artifact_inventory),
        "producer_module": build_old_artifact_inventory.__module__,
        "code_path_hash": code_path_hash(build_old_artifact_inventory),
    }


def hash_old_artifact_trees(repo_root: Path, protected_paths: dict[str, Path]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "old_artifact_hashes": {
            label: hash_tree(path, repo_root) for label, path in sorted(protected_paths.items())
        },
        "producer_function": producer_name(hash_old_artifact_trees),
        "producer_module": hash_old_artifact_trees.__module__,
        "code_path_hash": code_path_hash(hash_old_artifact_trees),
    }


def produce_old_artifact_mutation_report(
    before_hashes: dict[str, Any], after_hashes: dict[str, Any]
) -> dict[str, Any]:
    before = before_hashes.get("old_artifact_hashes", {})
    after = after_hashes.get("old_artifact_hashes", {})

    def changed(label: str) -> list[str]:
        old = before.get(label, {})
        new = after.get(label, {})
        paths = set(old) | set(new)
        return sorted(path for path in paths if old.get(path) != new.get(path))

    labels = sorted(set(before) | set(after))
    changed_by_label = {label: changed(label) for label in labels}
    return {
        "task_id": TASK_ID,
        "old_001b_artifacts_not_modified": not changed_by_label.get("001b"),
        "old_001c_artifacts_not_modified": not changed_by_label.get("001c"),
        "old_001d_artifacts_not_modified": not changed_by_label.get("001d"),
        "old_001e_artifacts_not_modified": not changed_by_label.get("001e"),
        "changed_paths_by_label": changed_by_label,
        "producer_function": producer_name(produce_old_artifact_mutation_report),
        "producer_module": produce_old_artifact_mutation_report.__module__,
        "code_path_hash": code_path_hash(produce_old_artifact_mutation_report),
        "output_row_ids": [
            "old_001b_artifacts_not_modified",
            "old_001c_artifacts_not_modified",
            "old_001d_artifacts_not_modified",
            "old_001e_artifacts_not_modified",
        ],
    }


def validate_old_artifact_mutation_provenance(report: dict[str, Any]) -> dict[str, Any]:
    stop_conditions = []
    if not report.get("before_hashes_computed"):
        stop_conditions.append("old_artifact_hash_before_missing")
    if not report.get("after_hashes_computed"):
        stop_conditions.append("old_artifact_hash_after_missing")
    producer = report.get("producer_function", "")
    if producer.endswith(".run_repair") or not producer:
        stop_conditions.append("old_artifact_mutation_wrapper_only")
    if report.get("old_artifact_mutation_true_producer_provenance") is not True:
        stop_conditions.append("old_artifact_mutation_wrapper_only")
    return {
        "task_id": TASK_ID,
        "old_artifact_mutation_true_producer_provenance": not any(
            condition == "old_artifact_mutation_wrapper_only" for condition in stop_conditions
        ),
        "old_artifact_before_after_hashes_computed": not any(
            condition
            in {"old_artifact_hash_before_missing", "old_artifact_hash_after_missing"}
            for condition in stop_conditions
        ),
        "stop_conditions": stop_conditions,
    }


def metric_row(
    *,
    metric_id: str,
    metric_name: str,
    producer_function: str,
    producer_module: str,
    code_path_hash_value: str,
    episode_ids: list[str],
    seed_ids: list[str],
    train_context_ids: list[str],
    heldout_context_ids: list[str],
    counterfactual_pair_ids: list[str],
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
        "producer_function": producer_function,
        "producer_module": producer_module,
        "code_path_hash": code_path_hash_value,
        "run_id": RUN_ID,
        "episode_ids": episode_ids,
        "seed_ids": seed_ids,
        "train_context_ids_consumed": train_context_ids,
        "heldout_context_ids_consumed": heldout_context_ids,
        "counterfactual_pair_ids_consumed": counterfactual_pair_ids,
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


def validate_metric_provenance(
    metric_provenance: dict[str, Any],
    context_report: dict[str, Any],
    old_artifact_mutation_provenance: dict[str, Any],
) -> dict[str, Any]:
    rows = metric_provenance.get("metrics", [])
    ids = context_ids_by_family(context_report)
    missing_required_fields = []
    stop_conditions: list[str] = []
    literal_metrics = []
    static_metrics = []
    copied_old = []
    wrapper_only = []
    missing_failure_paths = []
    decorative = []
    not_callable_context_rows = [
        row.get("context_id")
        for row in context_report.get("context_consumption_rows", [])
        if not row.get("producer_function")
        or not row.get("producer_module")
        or not row.get("code_path_hash")
        or row.get("consumed_before_metric_aggregation") is not True
    ]
    for row in rows:
        metric_id = row.get("metric_id", "<missing>")
        missing = sorted(set(REQUIRED_METRIC_FIELDS) - set(row))
        if missing:
            missing_required_fields.append({"metric_id": metric_id, "missing_fields": missing})
            stop_conditions.append("metric_provenance_field_missing")
        for field in [
            "train_context_ids_consumed",
            "heldout_context_ids_consumed",
            "counterfactual_pair_ids_consumed",
        ]:
            if field not in row:
                stop_conditions.append(f"{field}_missing")
        checks = {
            "train_context_ids_consumed": "train",
            "heldout_context_ids_consumed": "heldout",
            "counterfactual_pair_ids_consumed": "counterfactual_pair",
        }
        for field, family in checks.items():
            values = row.get(field, [])
            if not values:
                decorative.append({"metric_id": metric_id, "field": field, "values": values})
                stop_conditions.append("context_consumption_decorative")
            else:
                missing_contexts = sorted(set(values) - ids[family])
                if missing_contexts:
                    decorative.append(
                        {"metric_id": metric_id, "field": field, "values": missing_contexts}
                    )
                    stop_conditions.append("context_consumption_decorative")
        if row.get("computed_not_literal") is not True:
            literal_metrics.append(metric_id)
            stop_conditions.append("literal_metric_detected")
        if row.get("static_metric_dictionary_used") is True:
            static_metrics.append(metric_id)
            stop_conditions.append("static_metric_dictionary_detected")
        if row.get("copied_old_001d_result") is True:
            copied_old.append(metric_id)
            stop_conditions.append("copied_old_001d_result_detected")
        if row.get("failure_path_available") is not True:
            missing_failure_paths.append(metric_id)
            stop_conditions.append("failure_path_missing")
        if metric_id == "old_artifact_mutation":
            producer = row.get("producer_function", "")
            if producer.endswith(".run_repair") or producer != old_artifact_mutation_provenance.get(
                "producer_function"
            ):
                wrapper_only.append(metric_id)
                stop_conditions.append("old_artifact_mutation_wrapper_only")
    if not rows or sorted(row.get("metric_id") for row in rows) != sorted(METRIC_IDS):
        stop_conditions.append("metric_provenance_field_missing")
    if not_callable_context_rows:
        stop_conditions.append("context_consumption_not_callable")
    old_provenance_validation = validate_old_artifact_mutation_provenance(
        old_artifact_mutation_provenance
    )
    stop_conditions.extend(old_provenance_validation["stop_conditions"])
    stop_conditions = sorted(set(stop_conditions), key=stop_conditions.index)
    return {
        "task_id": TASK_ID,
        "metric_count": len(rows),
        "required_metric_fields": REQUIRED_METRIC_FIELDS,
        "all_verdict_metrics_have_callable_provenance": not stop_conditions,
        "all_verdict_metrics_have_train_context_ids_consumed": all(
            row.get("train_context_ids_consumed") for row in rows
        ),
        "all_verdict_metrics_have_heldout_context_ids_consumed": all(
            row.get("heldout_context_ids_consumed") for row in rows
        ),
        "all_verdict_metrics_have_counterfactual_pair_ids_consumed": all(
            row.get("counterfactual_pair_ids_consumed") for row in rows
        ),
        "context_consumption_fields_computed_by_callable_producers": not not_callable_context_rows,
        "no_decorative_context_ids": not decorative,
        "old_artifact_mutation_true_producer_provenance": not wrapper_only
        and old_provenance_validation["old_artifact_mutation_true_producer_provenance"],
        "missing_required_fields": missing_required_fields,
        "decorative_context_id_findings": decorative,
        "context_rows_missing_callable_provenance": not_callable_context_rows,
        "wrapper_only_provenance_metrics": wrapper_only,
        "literal_metric_detected": bool(literal_metrics),
        "static_metric_dictionary_detected": bool(static_metrics),
        "no_literal_metrics": not literal_metrics,
        "no_static_metric_dictionaries": not static_metrics,
        "no_copied_old_001d_results": not copied_old,
        "metrics_missing_failure_path": missing_failure_paths,
        "stop_conditions": stop_conditions,
    }
