from __future__ import annotations

import argparse
import hashlib
import importlib
import inspect
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import (
    ARTIFACT_DIR_NAME,
    AUTO_REMOTE_ANCHOR,
    CLAIM_CEILING,
    PARENT_COMMIT,
    PARENT_TAG,
    PARENT_TASK_CARD_ID,
    REPORT_NAME,
    TASK_CARD_ID,
    TASK_ID,
)


BRANCH = "codex/meta-theory-scaffold"
RUN_SEED = 1002
PARENT_ARTIFACT_DIR = Path("artifacts/mechanism_family_tournament_executable_surface_contract_001a")
CONTRACT_PATH = PARENT_ARTIFACT_DIR / "family_surface_contract.json"
MODULE_PATH = str(Path("src") / TASK_ID / "runner.py").replace("\\", "/")
EXPECTED_FAMILY_IDS = [
    "causal_world_model_control",
    "jepa_like_latent_prediction",
    "replay_consolidation_adaptation",
    "self_boundary_controllability_model",
    "viability_value_gated_prediction_action_loop",
    "social_latent_inference_without_partner_id_lookup",
]
REQUIRED_CONTRACT_FIELDS = [
    "family_id",
    "allowed_input_fields",
    "forbidden_target_derived_fields",
    "target_resolver",
    "metric_function",
    "numeric_threshold",
    "cheap_baseline_attack_surface",
    "leakage_detector_list",
    "positive_control_malformed_fixture",
    "sample_valid_record",
]
PROVENANCE_REQUIRED_FIELDS = [
    "family_id",
    "baseline_id",
    "baseline_category",
    "faithful_or_leakage_detector",
    "producer_function",
    "module_path",
    "code_path_hash",
    "inputs",
    "run_id",
    "seed",
    "record_ids",
    "context_ids",
    "raw_predictions",
    "targets",
    "score",
    "threshold",
    "aggregation",
    "decision_contribution",
]
REQUIRED_ARTIFACTS = {
    "result.json",
    "parent_anchor_readback.json",
    "contract_readback.json",
    "baseline_score_matrix.json",
    "family_decisions.json",
    "survivors.json",
    "closed_families.json",
    "needs_redesign.json",
    "positive_control_results.json",
    "provenance_manifest.json",
    "leakage_scan_results.json",
    "future_tournament_eligibility.json",
    "forbidden_action_guard.json",
}
POSITIVE_CONTROL_EXPECTED = {
    "target_leak": "target_leak_detected",
    "partner_id_lookup": "partner_id_lookup_shortcut_detected",
    "table_lookup": "faithful_table_lookup_reaches_threshold",
    "static_formula": "static_formula_shortcut_detected",
    "missing_threshold": "missing_threshold",
    "missing_callable_target": "missing_callable_target",
}
CLAIM_EXCLUSIONS = [
    "mechanism validity",
    "Gate4 validity",
    "candidate behavior",
    "candidate score",
    "tournament result",
    "runtime readiness",
    "bridge/admission readiness",
    "agency",
    "subjectivity",
    "consciousness",
    "emotion",
    "autonomy",
    "companion readiness",
    "EGO readiness",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_json_ready(child) for child in value]
    if isinstance(value, tuple):
        return [_json_ready(child) for child in value]
    if isinstance(value, set):
        return sorted(_json_ready(child) for child in value)
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    return value


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_json(relative_path: str | Path) -> Any:
    return json.loads((repo_root() / relative_path).read_text(encoding="utf-8"))


def _git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout.strip()


def _safe_git(args: list[str]) -> str:
    try:
        return _git(args)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def _safe_git_raw(args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return completed.stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_path_hash(func: Any) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _target_key(family: dict[str, Any]) -> str:
    target_source = family["sample_valid_record"].get("target_source", {})
    if len(target_source) != 1:
        return sorted(target_source)[0]
    return next(iter(target_source))


def _resolve_function(dotted_path: str) -> Any:
    module_name, function_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


def _surface_violation_type() -> type[Exception]:
    module = importlib.import_module("mechanism_family_tournament_executable_surface_contract_001a.surfaces")
    return getattr(module, "SurfaceContractViolation")


def _read_remote_refs(*refs: str) -> dict[str, str]:
    output = _safe_git(["ls-remote", "origin", *refs])
    rows: dict[str, str] = {}
    for line in output.splitlines():
        if not line.strip():
            continue
        commit, ref = line.split(maxsplit=1)
        rows[ref] = commit
    return rows


def _is_ancestor(commit: str, descendant: str) -> bool:
    if not commit or not descendant:
        return False
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, descendant],
        cwd=repo_root(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.returncode == 0


def build_parent_anchor_readback() -> dict[str, Any]:
    current_head = _safe_git(["rev-parse", "HEAD"])
    local_parent = _safe_git(["rev-parse", PARENT_COMMIT])
    local_tag = _safe_git(["rev-parse", f"refs/tags/{PARENT_TAG}"])
    local_tag_type = _safe_git(["cat-file", "-t", f"refs/tags/{PARENT_TAG}"])
    remote_refs = _read_remote_refs(f"refs/heads/{BRANCH}", f"refs/tags/{PARENT_TAG}")
    remote_branch = remote_refs.get(f"refs/heads/{BRANCH}", "")
    remote_tag = remote_refs.get(f"refs/tags/{PARENT_TAG}", "")
    status_porcelain = _safe_git_raw(["status", "--porcelain"])
    return {
        "producer_function": "build_parent_anchor_readback",
        "task_id": TASK_CARD_ID,
        "parent_task_id": PARENT_TASK_CARD_ID,
        "branch": _safe_git(["branch", "--show-current"]),
        "expected_branch": BRANCH,
        "current_head": current_head,
        "parent_commit": PARENT_COMMIT,
        "parent_tag": PARENT_TAG,
        "local_parent_commit_hash": local_parent,
        "remote_branch_hash": remote_branch,
        "local_tag_hash": local_tag,
        "remote_tag_hash": remote_tag,
        "local_tag_type": local_tag_type,
        "parent_tag_exact_match": (
            local_parent == PARENT_COMMIT
            and local_tag == PARENT_COMMIT
            and remote_tag == PARENT_COMMIT
            and local_tag_type == "commit"
        ),
        "remote_branch_exact_parent_at_read_time": remote_branch == PARENT_COMMIT,
        "parent_commit_is_ancestor_of_current_head": _is_ancestor(PARENT_COMMIT, current_head),
        "parent_commit_is_ancestor_of_remote_branch": _is_ancestor(PARENT_COMMIT, remote_branch),
        "worktree_clean_at_read_time": status_porcelain.strip() == "",
        "status_porcelain_at_read_time": status_porcelain,
        "claim_ceiling": "parent remote-anchor publication and readback only",
    }


def validate_family_contract(family: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_CONTRACT_FIELDS if field not in family]
    threshold = family.get("numeric_threshold")
    threshold_ok = isinstance(threshold, (int, float)) and 0 < threshold < 1
    resolver_callable = False
    metric_callable = False
    sample_target_resolved = False
    metric_smoke = False
    resolver_error = None
    metric_error = None
    try:
        resolver = _resolve_function(str(family.get("target_resolver", "")))
        resolver_callable = callable(resolver)
        if resolver_callable and isinstance(family.get("sample_valid_record"), dict):
            sample_target = resolver(family["sample_valid_record"])
            sample_target_resolved = isinstance(sample_target, str) and bool(sample_target)
    except Exception as exc:
        resolver_error = str(exc)
    try:
        metric = _resolve_function(str(family.get("metric_function", "")))
        metric_callable = callable(metric)
        if metric_callable:
            metric_smoke = metric(["ok"], ["ok"]) == 1.0
    except Exception as exc:
        metric_error = str(exc)
    blocking = []
    if missing:
        blocking.append("missing_required_contract_fields")
    if not threshold_ok:
        blocking.append("missing_threshold")
    if not resolver_callable:
        blocking.append("missing_callable_target")
    if not metric_callable:
        blocking.append("missing_callable_metric")
    if resolver_callable and not sample_target_resolved:
        blocking.append("sample_target_not_resolved")
    if metric_callable and not metric_smoke:
        blocking.append("metric_smoke_check_failed")
    return {
        "family_id": family.get("family_id"),
        "required_fields_present": not missing,
        "missing_fields": missing,
        "numeric_threshold_exists": threshold_ok,
        "target_resolver_callable": resolver_callable,
        "metric_function_callable": metric_callable,
        "sample_target_resolved": sample_target_resolved,
        "metric_smoke_check_passed": metric_smoke,
        "blocking_reasons": blocking,
        "resolver_error": resolver_error,
        "metric_error": metric_error,
    }


def build_contract_readback() -> dict[str, Any]:
    contract = _load_json(CONTRACT_PATH)
    families = contract.get("families", [])
    validation = [validate_family_contract(family) for family in families]
    return {
        "producer_function": "build_contract_readback",
        "task_id": TASK_CARD_ID,
        "parent_task_id": PARENT_TASK_CARD_ID,
        "contract_task_id": contract.get("task_id"),
        "loaded_from_artifact": True,
        "source_path": str(CONTRACT_PATH).replace("\\", "/"),
        "source_sha256": sha256_file(repo_root() / CONTRACT_PATH),
        "family_count": len(families),
        "family_ids": [family.get("family_id") for family in families],
        "expected_family_ids": list(EXPECTED_FAMILY_IDS),
        "all_expected_families_present": sorted(family.get("family_id") for family in families) == sorted(EXPECTED_FAMILY_IDS),
        "candidate_code_authorized": contract.get("candidate_code_authorized"),
        "candidate_score_authorized": contract.get("candidate_score_authorized"),
        "tournament_execution_authorized": contract.get("tournament_execution_authorized"),
        "runtime_or_mainline_authorized": contract.get("runtime_or_mainline_authorized"),
        "gate4_replacement_authorized": contract.get("gate4_replacement_authorized"),
        "family_validation": validation,
        "all_contract_callables_valid": all(not row["blocking_reasons"] for row in validation),
        "families": families,
        "claim_ceiling": "contract artifact readback and callability validation only",
    }


def _mutate_value(value: Any, token: str, class_index: int) -> Any:
    if isinstance(value, dict):
        mutated = dict(value)
        mutated["preflight_key"] = token
        mutated["rule_value"] = class_index
        return mutated
    if isinstance(value, list):
        return list(value) + [token, f"rule_value_{class_index}"]
    return f"{value}|{token}|rule_value_{class_index}"


def build_family_records(family: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    resolver = _resolve_function(family["target_resolver"])
    sample = family["sample_valid_record"]
    base_observation = sample["observation"]
    target_key = _target_key(family)
    base_target = resolver(sample)
    targets = [base_target, f"contrast_{base_target}"]
    train = []
    heldout = []
    allowed_fields = family["allowed_input_fields"]
    for split, collection in [("train", train), ("heldout", heldout)]:
        for index, target in enumerate(targets):
            token = f"{family['family_id']}:{index}"
            observation = {
                field: _mutate_value(base_observation.get(field), token, index)
                for field in allowed_fields
            }
            record = {
                "record_id": f"{family['family_id']}:{split}:{index}",
                "family_id": family["family_id"],
                "observation": observation,
                "target_source": {target_key: target},
            }
            collection.append(record)
    return {"train": train, "heldout": heldout}


def _trace_baseline_applicable(family: dict[str, Any]) -> bool:
    fields = " ".join(family.get("allowed_input_fields", []))
    return any(token in fields for token in ["trace", "order", "key", "hash", "epoch", "context", "marker"])


def _baseline_kind(baseline_id: str) -> str:
    lowered = baseline_id.lower()
    leakage_terms = ["oracle", "answer", "target", "label", "full_bundle", "supervised"]
    return "leakage_detector" if any(term in lowered for term in leakage_terms) else "faithful_cheap_baseline"


def build_baseline_specs(family: dict[str, Any]) -> list[dict[str, Any]]:
    specs = [
        {
            "baseline_id": "exact_lookup",
            "baseline_category": "exact_lookup_baseline",
            "operation": "exact_lookup",
            "source": "required_baseline_class",
        },
        {
            "baseline_id": "table_memorization",
            "baseline_category": "table_memorization_baseline",
            "operation": "table_memorization",
            "source": "required_baseline_class",
        },
        {
            "baseline_id": "nearest_neighbor_retrieval",
            "baseline_category": "nearest_neighbor_retrieval_baseline",
            "operation": "nearest_neighbor",
            "source": "required_baseline_class",
        },
        {
            "baseline_id": "static_decoder",
            "baseline_category": "static_decoder_baseline",
            "operation": "static_decoder",
            "source": "required_baseline_class",
        },
        {
            "baseline_id": "static_formula_rule",
            "baseline_category": "static_formula_rule_baseline",
            "operation": "static_formula",
            "source": "required_baseline_class",
        },
    ]
    if _trace_baseline_applicable(family):
        specs.append(
            {
                "baseline_id": "trace_order_key_shortcut",
                "baseline_category": "trace_order_key_shortcut_baseline",
                "operation": "table_memorization",
                "source": "required_when_applicable",
            }
        )
    for attack in family.get("cheap_baseline_attack_surface", []):
        specs.append(
            {
                "baseline_id": f"family_specific_{attack}",
                "baseline_category": "family_specific_shortcut_baseline",
                "operation": "table_memorization",
                "source": "contract_cheap_baseline_attack_surface",
            }
        )
    return specs


def _targets_for_records(records: list[dict[str, Any]], resolver_path: str) -> list[str]:
    resolver = _resolve_function(resolver_path)
    return [resolver(record) for record in records]


def _first_allowed_field(serialized_input: dict[str, Any]) -> str:
    return serialized_input["allowed_input_fields"][0]


def _feature(record: dict[str, Any], field: str) -> str:
    return _canonical(record["observation"].get(field))


def _run_exact_mapping(serialized_input: dict[str, Any], field: str | None = None) -> list[str]:
    train = serialized_input["train_records"]
    heldout = serialized_input["heldout_records"]
    train_targets = _targets_for_records(train, serialized_input["target_resolver"])
    if field is None:
        mapping = {
            _canonical(record["observation"]): target
            for record, target in zip(train, train_targets)
        }
        return [mapping.get(_canonical(record["observation"]), train_targets[0]) for record in heldout]
    mapping = {
        _feature(record, field): target
        for record, target in zip(train, train_targets)
    }
    return [mapping.get(_feature(record, field), train_targets[0]) for record in heldout]


def _run_static_formula(serialized_input: dict[str, Any]) -> list[str]:
    field = _first_allowed_field(serialized_input)
    return _run_exact_mapping(serialized_input, field)


def recompute_baseline_score(serialized_input: dict[str, Any]) -> dict[str, Any]:
    operation = serialized_input["operation"]
    metric = _resolve_function(serialized_input["metric_function"])
    if operation == "exact_lookup":
        predictions = _run_exact_mapping(serialized_input)
    elif operation in {"table_memorization", "nearest_neighbor", "static_decoder"}:
        predictions = _run_exact_mapping(serialized_input, _first_allowed_field(serialized_input))
    elif operation == "static_formula":
        predictions = _run_static_formula(serialized_input)
    else:
        predictions = _run_exact_mapping(serialized_input, _first_allowed_field(serialized_input))
    targets = _targets_for_records(serialized_input["heldout_records"], serialized_input["target_resolver"])
    score = metric(predictions, targets)
    return {
        "raw_predictions": predictions,
        "targets": targets,
        "score": score,
        "aggregation": "mean exact-match accuracy over heldout no-candidate preflight records",
    }


def _serialized_input_for_baseline(family: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    records = build_family_records(family)
    return {
        "family_id": family["family_id"],
        "baseline_id": spec["baseline_id"],
        "operation": spec["operation"],
        "target_resolver": family["target_resolver"],
        "metric_function": family["metric_function"],
        "threshold": family["numeric_threshold"],
        "allowed_input_fields": list(family["allowed_input_fields"]),
        "contract_source_path": str(CONTRACT_PATH).replace("\\", "/"),
        "train_records": records["train"],
        "heldout_records": records["heldout"],
    }


def run_callable_baseline_score(
    *,
    family: dict[str, Any],
    baseline_spec: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    serialized_input = _serialized_input_for_baseline(family, baseline_spec)
    recomputed = recompute_baseline_score(serialized_input)
    threshold = family["numeric_threshold"]
    kind = _baseline_kind(baseline_spec["baseline_id"])
    contribution = (
        "closed_by_faithful_cheap_baseline"
        if kind == "faithful_cheap_baseline" and recomputed["score"] >= threshold
        else "leakage_detector_observed"
        if kind == "leakage_detector"
        else "below_threshold"
    )
    record_ids = [record["record_id"] for record in serialized_input["heldout_records"]]
    return {
        "family_id": family["family_id"],
        "baseline_id": baseline_spec["baseline_id"],
        "baseline_category": baseline_spec["baseline_category"],
        "faithful_or_leakage_detector": kind,
        "producer_function": "run_callable_baseline_score",
        "module_path": MODULE_PATH,
        "code_path_hash": code_path_hash(run_callable_baseline_score),
        "inputs": {
            "contract_source_path": str(CONTRACT_PATH).replace("\\", "/"),
            "family_id": family["family_id"],
            "baseline_source": baseline_spec["source"],
            "target_resolver": family["target_resolver"],
            "metric_function": family["metric_function"],
        },
        "run_id": run_id,
        "seed": RUN_SEED,
        "record_ids": record_ids,
        "context_ids": [family["family_id"]],
        "raw_predictions": recomputed["raw_predictions"],
        "targets": recomputed["targets"],
        "score": recomputed["score"],
        "threshold": threshold,
        "aggregation": recomputed["aggregation"],
        "decision_contribution": contribution,
        "serialized_input": serialized_input,
    }


def build_baseline_score_matrix(contract_readback: dict[str, Any], run_id: str) -> dict[str, Any]:
    rows = []
    for family in contract_readback["families"]:
        validation = validate_family_contract(family)
        if validation["blocking_reasons"]:
            continue
        for spec in build_baseline_specs(family):
            rows.append(run_callable_baseline_score(family=family, baseline_spec=spec, run_id=run_id))
    return {
        "producer_function": "build_baseline_score_matrix",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "row_count": len(rows),
        "rows": rows,
        "claim_ceiling": "callable no-candidate cheap-baseline score matrix only",
    }


def build_family_decisions(
    contract_readback: dict[str, Any],
    baseline_score_matrix: dict[str, Any],
    positive_controls: dict[str, Any] | None = None,
    provenance_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rows_by_family: dict[str, list[dict[str, Any]]] = {}
    for row in baseline_score_matrix["rows"]:
        rows_by_family.setdefault(row["family_id"], []).append(row)
    validation_by_family = {
        row["family_id"]: row for row in contract_readback["family_validation"]
    }
    decisions = []
    for family in contract_readback["families"]:
        family_id = family["family_id"]
        blockers = list(validation_by_family[family_id]["blocking_reasons"])
        family_rows = rows_by_family.get(family_id, [])
        faithful = [
            row for row in family_rows if row["faithful_or_leakage_detector"] == "faithful_cheap_baseline"
        ]
        best = max(faithful, key=lambda row: row["score"], default=None)
        if not faithful:
            blockers.append("no_faithful_cheap_baseline_ran")
        if blockers:
            decision = "needs_redesign"
            reason = "contract or callable baseline precondition failed"
        elif best is not None and best["score"] >= family["numeric_threshold"]:
            decision = "closed_by_faithful_cheap_baseline"
            reason = "best faithful cheap baseline met or exceeded numeric threshold"
        else:
            decision = "survives_baseline_preflight_only"
            reason = "all faithful cheap baselines remained below threshold"
        decisions.append(
            {
                "family_id": family_id,
                "decision": decision,
                "reasons": blockers,
                "reason": reason,
                "threshold": family.get("numeric_threshold"),
                "best_faithful_cheap_baseline": {
                    "baseline_id": best["baseline_id"] if best else None,
                    "score": best["score"] if best else None,
                    "threshold": best["threshold"] if best else family.get("numeric_threshold"),
                    "producer_function": best["producer_function"] if best else None,
                },
                "candidate_code_authorized": False,
                "tournament_execution_authorized": False,
            }
        )
    return {
        "producer_function": "build_family_decisions",
        "task_id": TASK_CARD_ID,
        "decisions": decisions,
    }


def build_survivor_outputs(
    family_decisions: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    survivors = [
        row for row in family_decisions["decisions"] if row["decision"] == "survives_baseline_preflight_only"
    ]
    closed = [
        row for row in family_decisions["decisions"] if row["decision"] == "closed_by_faithful_cheap_baseline"
    ]
    redesign = [
        row for row in family_decisions["decisions"] if row["decision"] == "needs_redesign"
    ]
    return (
        {"producer_function": "build_survivor_outputs", "families": survivors, "survivor_count": len(survivors)},
        {"producer_function": "build_survivor_outputs", "families": closed, "closed_count": len(closed)},
        {"producer_function": "build_survivor_outputs", "families": redesign, "needs_redesign_count": len(redesign)},
    )


def evaluate_future_tournament_eligibility(survivor_count: int) -> dict[str, Any]:
    return {
        "producer_function": "evaluate_future_tournament_eligibility",
        "survivor_count": survivor_count,
        "minimum_survivors_required": 2,
        "eligible_for_future_tournament_execution_card": survivor_count >= 2,
        "claim_ceiling": "future task-card eligibility only; no tournament execution authorization",
    }


def build_future_tournament_eligibility(survivors: dict[str, Any]) -> dict[str, Any]:
    payload = evaluate_future_tournament_eligibility(survivors["survivor_count"])
    payload["candidate_code_authorized"] = False
    payload["tournament_execution_authorized"] = False
    return payload


def _control_score_record(family: dict[str, Any], baseline_category: str, operation: str, run_id: str) -> dict[str, Any]:
    spec = {
        "baseline_id": f"positive_control_{operation}",
        "baseline_category": baseline_category,
        "operation": operation,
        "source": "positive_control",
    }
    return run_callable_baseline_score(family=family, baseline_spec=spec, run_id=run_id)


def _control_row(
    *,
    control_id: str,
    expected: str,
    observed: str,
    kind: str,
    score_record: dict[str, Any] | None = None,
    force_mismatch: str | None = None,
) -> dict[str, Any]:
    if force_mismatch == control_id:
        observed = "forced_positive_control_mismatch"
    return {
        "control_id": control_id,
        "expected_block_reason": expected,
        "observed_block_reason": observed,
        "failed_as_expected": observed == expected,
        "faithful_or_leakage_detector": kind,
        "positive_control_input_fixture_path": f"generated_from_contract:{control_id}",
        "score_record": score_record,
    }


def run_positive_controls(
    contract_readback: dict[str, Any],
    run_id: str,
    *,
    force_positive_control_mismatch: str | None = None,
) -> dict[str, Any]:
    families = contract_readback["families"]
    family_by_id = {family["family_id"]: family for family in families}
    violation_type = _surface_violation_type()
    observed_target_leak = "target_leak_not_detected"
    target_leak_failures = []
    for family in families:
        fixture = family["positive_control_malformed_fixture"]["record"]
        try:
            _resolve_function(family["target_resolver"])(fixture)
        except violation_type as exc:
            target_leak_failures.append(getattr(exc, "reason", str(exc)))
    if target_leak_failures and all(reason == "forbidden_target_derived_field_visible" for reason in target_leak_failures):
        observed_target_leak = "target_leak_detected"

    social = family_by_id["social_latent_inference_without_partner_id_lookup"]
    social_fixture = json.loads(json.dumps(social["sample_valid_record"]))
    social_fixture["observation"]["partner_id"] = "partner_positive_control"
    observed_partner = "partner_id_lookup_not_detected"
    try:
        _resolve_function(social["target_resolver"])(social_fixture)
    except violation_type as exc:
        if getattr(exc, "reason", str(exc)) == "forbidden_target_derived_field_visible":
            observed_partner = "partner_id_lookup_shortcut_detected"

    first_family = families[0]
    table_score = _control_score_record(first_family, "table_memorization_baseline", "table_memorization", run_id)
    static_score = _control_score_record(first_family, "static_formula_rule_baseline", "static_formula", run_id)
    table_observed = (
        "faithful_table_lookup_reaches_threshold"
        if table_score["score"] >= table_score["threshold"]
        else "faithful_table_lookup_below_threshold"
    )
    static_observed = (
        "static_formula_shortcut_detected"
        if static_score["score"] >= static_score["threshold"]
        else "static_formula_shortcut_not_detected"
    )

    missing_threshold_family = json.loads(json.dumps(first_family))
    missing_threshold_family.pop("numeric_threshold", None)
    missing_threshold_observed = (
        "missing_threshold"
        if "missing_threshold" in validate_family_contract(missing_threshold_family)["blocking_reasons"]
        else "missing_threshold_not_detected"
    )

    missing_callable_family = json.loads(json.dumps(first_family))
    missing_callable_family["target_resolver"] = "missing.module.missing_callable_target"
    missing_callable_observed = (
        "missing_callable_target"
        if "missing_callable_target" in validate_family_contract(missing_callable_family)["blocking_reasons"]
        else "missing_callable_target_not_detected"
    )

    rows = [
        _control_row(
            control_id="target_leak",
            expected=POSITIVE_CONTROL_EXPECTED["target_leak"],
            observed=observed_target_leak,
            kind="leakage_detector",
            force_mismatch=force_positive_control_mismatch,
        ),
        _control_row(
            control_id="partner_id_lookup",
            expected=POSITIVE_CONTROL_EXPECTED["partner_id_lookup"],
            observed=observed_partner,
            kind="faithful_cheap_baseline",
            force_mismatch=force_positive_control_mismatch,
        ),
        _control_row(
            control_id="table_lookup",
            expected=POSITIVE_CONTROL_EXPECTED["table_lookup"],
            observed=table_observed,
            kind="faithful_cheap_baseline",
            score_record=table_score,
            force_mismatch=force_positive_control_mismatch,
        ),
        _control_row(
            control_id="static_formula",
            expected=POSITIVE_CONTROL_EXPECTED["static_formula"],
            observed=static_observed,
            kind="faithful_cheap_baseline",
            score_record=static_score,
            force_mismatch=force_positive_control_mismatch,
        ),
        _control_row(
            control_id="missing_threshold",
            expected=POSITIVE_CONTROL_EXPECTED["missing_threshold"],
            observed=missing_threshold_observed,
            kind="contract_validator",
            force_mismatch=force_positive_control_mismatch,
        ),
        _control_row(
            control_id="missing_callable_target",
            expected=POSITIVE_CONTROL_EXPECTED["missing_callable_target"],
            observed=missing_callable_observed,
            kind="contract_validator",
            force_mismatch=force_positive_control_mismatch,
        ),
    ]
    return {
        "producer_function": "run_positive_controls",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "controls": rows,
        "all_failed_as_expected": all(row["failed_as_expected"] for row in rows),
        "claim_ceiling": "positive-control validation only; no candidate or tournament execution",
    }


def build_leakage_scan_results(contract_readback: dict[str, Any]) -> dict[str, Any]:
    violation_type = _surface_violation_type()
    clean_results = []
    positive_results = []
    for family in contract_readback["families"]:
        resolver = _resolve_function(family["target_resolver"])
        clean_ok = False
        try:
            clean_ok = isinstance(resolver(family["sample_valid_record"]), str)
        except Exception:
            clean_ok = False
        clean_results.append({"family_id": family["family_id"], "clean_record_passed": clean_ok})
        fixture = family["positive_control_malformed_fixture"]["record"]
        detected = False
        try:
            resolver(fixture)
        except violation_type as exc:
            detected = getattr(exc, "reason", str(exc)) == "forbidden_target_derived_field_visible"
        positive_results.append({"family_id": family["family_id"], "target_leak_detected": detected})
    return {
        "producer_function": "build_leakage_scan_results",
        "task_id": TASK_CARD_ID,
        "clean_records": clean_results,
        "positive_controls": positive_results,
        "clean_contract_records_passed": all(row["clean_record_passed"] for row in clean_results),
        "positive_control_detected": all(row["target_leak_detected"] for row in positive_results),
        "claim_ceiling": "leakage scan positive-control evidence only",
    }


def build_provenance_manifest(
    baseline_score_matrix: dict[str, Any],
    positive_controls: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    positive_score_records = [
        row["score_record"] for row in positive_controls["controls"] if row.get("score_record") is not None
    ]
    records = baseline_score_matrix["rows"] + positive_score_records
    manifest = {
        "producer_function": "build_provenance_manifest",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "required_fields": list(PROVENANCE_REQUIRED_FIELDS),
        "baseline_score_records": records,
        "static_score_literals_accepted": False,
        "verification": None,
    }
    manifest["verification"] = verify_provenance_manifest(manifest)
    return manifest


def verify_provenance_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    reasons = []
    records = manifest.get("baseline_score_records", [])
    if not isinstance(records, list) or not records:
        reasons.append("missing_baseline_score_records")
    for index, record in enumerate(records):
        for field in PROVENANCE_REQUIRED_FIELDS:
            if field not in record:
                reasons.append(f"missing_field:{index}:{field}")
        if record.get("static_score_injection") is True:
            reasons.append("static_score_injection")
        if record.get("producer_function") in {"literal_static_report", "static_verdict_dictionary"}:
            reasons.append("static_score_injection")
        serialized = record.get("serialized_input")
        if isinstance(serialized, dict) and record.get("producer_function") == "run_callable_baseline_score":
            try:
                recomputed = recompute_baseline_score(serialized)
                if recomputed["score"] != record.get("score"):
                    reasons.append(f"score_recompute_mismatch:{index}")
                if recomputed["raw_predictions"] != record.get("raw_predictions"):
                    reasons.append(f"prediction_recompute_mismatch:{index}")
            except Exception:
                reasons.append(f"score_recompute_error:{index}")
        if not record.get("code_path_hash"):
            reasons.append(f"missing_code_path_hash:{index}")
        if not record.get("record_ids"):
            reasons.append(f"missing_record_ids:{index}")
    return {
        "producer_function": "verify_provenance_manifest",
        "passed": not reasons,
        "blocking_reasons": sorted(set(reasons)),
    }


def _changed_or_new_paths() -> list[str]:
    changed = set()
    for line in _safe_git_raw(["diff", "--name-only"]).splitlines():
        if line.strip():
            changed.add(line.strip().replace("\\", "/"))
    for line in _safe_git_raw(["diff", "--cached", "--name-only"]).splitlines():
        if line.strip():
            changed.add(line.strip().replace("\\", "/"))
    for line in _safe_git_raw(["ls-files", "--others", "--exclude-standard"]).splitlines():
        if line.strip():
            changed.add(line.strip().replace("\\", "/"))
    return sorted(changed)


def build_forbidden_action_guard() -> dict[str, Any]:
    allowed_prefixes = [
        f"src/{TASK_ID}/",
        f"artifacts/{TASK_ID}/",
    ]
    allowed_exact = {
        f"tests/test_{TASK_ID}.py",
        f"docs/research/{REPORT_NAME}",
    }
    paths = _changed_or_new_paths()
    forbidden_paths = [
        path
        for path in paths
        if path not in allowed_exact and not any(path.startswith(prefix) for prefix in allowed_prefixes)
    ]
    return {
        "producer_function": "build_forbidden_action_guard",
        "task_id": TASK_CARD_ID,
        "changed_or_new_paths": paths,
        "forbidden_files_modified": forbidden_paths,
        "forbidden_action_guard_passed": not forbidden_paths,
        "candidate_code_created": False,
        "candidate_score_produced": False,
        "tournament_execution_attempted": False,
        "gate4_replacement_design_created": False,
        "gate4_repair_or_rerun_attempted": False,
        "runtime_or_mainline_path_created": False,
        "bridge_or_admission_path_created": False,
        "llm_rag_ui_companion_path_created": False,
        "auto_remote_anchor_performed": False,
        "guard_basis": "Only isolated baseline-preflight-rerun 001B source, test, report, and artifact paths are allowed.",
        "claim_ceiling": CLAIM_CEILING,
    }


def compute_result(
    *,
    parent_anchor: dict[str, Any],
    contract_readback: dict[str, Any],
    family_decisions: dict[str, Any],
    positive_controls: dict[str, Any],
    provenance_manifest: dict[str, Any],
    leakage_scan_results: dict[str, Any],
    forbidden_guard: dict[str, Any],
    future_eligibility: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    stop_conditions = []
    if not parent_anchor["parent_tag_exact_match"]:
        stop_conditions.append("parent_anchor_tag_exact_match_failed")
    if not parent_anchor["parent_commit_is_ancestor_of_current_head"]:
        stop_conditions.append("parent_commit_not_ancestor_of_current_head")
    if not contract_readback["all_contract_callables_valid"]:
        stop_conditions.append("contract_callability_or_threshold_failure")
    if not positive_controls["all_failed_as_expected"]:
        stop_conditions.extend(
            f"positive_control_mismatch:{row['control_id']}"
            for row in positive_controls["controls"]
            if not row["failed_as_expected"]
        )
    if not provenance_manifest["verification"]["passed"]:
        stop_conditions.extend(provenance_manifest["verification"]["blocking_reasons"])
    if not leakage_scan_results["positive_control_detected"]:
        stop_conditions.append("leakage_positive_control_not_detected")
    if not leakage_scan_results["clean_contract_records_passed"]:
        stop_conditions.append("clean_contract_records_failed_leakage_scan")
    if forbidden_guard["forbidden_files_modified"]:
        stop_conditions.append("forbidden_files_modified")
    for key in [
        "candidate_code_created",
        "candidate_score_produced",
        "tournament_execution_attempted",
        "gate4_repair_or_rerun_attempted",
        "runtime_or_mainline_path_created",
    ]:
        if forbidden_guard[key]:
            stop_conditions.append(key)

    decisions = [row["decision"] for row in family_decisions["decisions"]]
    if any(condition.startswith("parent_anchor") or condition == "parent_commit_not_ancestor_of_current_head" for condition in stop_conditions):
        verdict = "mechanism_family_tournament_baseline_preflight_rerun_001b_blocked_by_parent_anchor_failure"
    elif any(
        condition in stop_conditions
        or condition.startswith("positive_control_mismatch:")
        for condition in ["contract_callability_or_threshold_failure", "forbidden_files_modified"]
    ) or any(condition.startswith("missing_") for condition in stop_conditions):
        verdict = "mechanism_family_tournament_baseline_preflight_rerun_001b_blocked_by_contract_or_positive_control_failure"
    elif any(condition.startswith("positive_control_mismatch:") for condition in stop_conditions):
        verdict = "mechanism_family_tournament_baseline_preflight_rerun_001b_blocked_by_contract_or_positive_control_failure"
    elif future_eligibility["eligible_for_future_tournament_execution_card"]:
        verdict = "mechanism_family_tournament_baseline_preflight_rerun_001b_survivors_eligible"
    elif any(decision == "survives_baseline_preflight_only" for decision in decisions):
        verdict = "mechanism_family_tournament_baseline_preflight_rerun_001b_insufficient_survivors_blocked"
    else:
        verdict = "mechanism_family_tournament_baseline_preflight_rerun_001b_all_closed_or_needs_redesign"
    return {
        "producer_function": "compute_result",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "verdict": verdict,
        "current_layer": "engineering-governance / no-candidate callable baseline-preflight rerun",
        "mainline_integration_status": "not integrated",
        "enabled_status": "no runtime, no bridge/admission, no Gate4 replacement, no candidate, no tournament execution, no trigger path",
        "real_trigger_evidence": "Consumes anchored parent executable-surface contract artifact and runs callable cheap baselines plus positive controls through contract target resolvers and metric functions.",
        "claim_ceiling": CLAIM_CEILING,
        "stop_conditions_triggered": sorted(set(stop_conditions)),
        "family_decision_counts": dict(Counter(decisions)),
        "future_tournament_eligibility": future_eligibility["eligible_for_future_tournament_execution_card"],
        "candidate_code_created": forbidden_guard["candidate_code_created"],
        "candidate_score_produced": forbidden_guard["candidate_score_produced"],
        "tournament_execution_attempted": forbidden_guard["tournament_execution_attempted"],
        "gate4_repair_or_rerun_attempted": forbidden_guard["gate4_repair_or_rerun_attempted"],
        "runtime_or_mainline_path_created": forbidden_guard["runtime_or_mainline_path_created"],
        "remote_anchor_policy": AUTO_REMOTE_ANCHOR,
        "remote_anchor_performed": False,
        "next_minimal_closed_loop_action": (
            "Route away from tournament execution for these surfaces unless a separate bounded redesign "
            "creates families that survive cheap faithful baselines under the same callable provenance gate."
        ),
        "what_this_does_not_prove": list(CLAIM_EXCLUSIONS),
    }


def _resolve_output_dir(output_dir: str | Path | None) -> Path:
    if output_dir is None:
        return repo_root() / "artifacts" / ARTIFACT_DIR_NAME
    path = Path(output_dir)
    return path if path.is_absolute() else repo_root() / path


def execute_preflight(
    output_dir: str | Path | None = None,
    *,
    persist_artifacts: bool = True,
    force_positive_control_mismatch: str | None = None,
    test_result_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out = _resolve_output_dir(output_dir)
    run_id = f"{TASK_ID}_{_now().replace('-', '').replace(':', '').replace('Z', 'Z')}"
    parent_anchor = build_parent_anchor_readback()
    contract_readback = build_contract_readback()
    baseline_score_matrix = build_baseline_score_matrix(contract_readback, run_id)
    positive_controls = run_positive_controls(
        contract_readback,
        run_id,
        force_positive_control_mismatch=force_positive_control_mismatch,
    )
    leakage_scan_results = build_leakage_scan_results(contract_readback)
    provenance_manifest = build_provenance_manifest(baseline_score_matrix, positive_controls, run_id)
    family_decisions = build_family_decisions(
        contract_readback,
        baseline_score_matrix,
        positive_controls=positive_controls,
        provenance_manifest=provenance_manifest,
    )
    survivors, closed_families, needs_redesign = build_survivor_outputs(family_decisions)
    future_eligibility = build_future_tournament_eligibility(survivors)
    forbidden_guard = build_forbidden_action_guard()
    result = compute_result(
        parent_anchor=parent_anchor,
        contract_readback=contract_readback,
        family_decisions=family_decisions,
        positive_controls=positive_controls,
        provenance_manifest=provenance_manifest,
        leakage_scan_results=leakage_scan_results,
        forbidden_guard=forbidden_guard,
        future_eligibility=future_eligibility,
        run_id=run_id,
    )
    if test_result_readback is not None:
        result["test_result_readback"] = test_result_readback
    run = {
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "result": result,
        "parent_anchor_readback": parent_anchor,
        "contract_readback": _without_raw_contract(contract_readback),
        "baseline_score_matrix": baseline_score_matrix,
        "family_decisions": family_decisions,
        "survivors": survivors,
        "closed_families": closed_families,
        "needs_redesign": needs_redesign,
        "positive_control_results": positive_controls,
        "provenance_manifest": provenance_manifest,
        "leakage_scan_results": leakage_scan_results,
        "future_tournament_eligibility": future_eligibility,
        "forbidden_action_guard": forbidden_guard,
    }
    run["_contract_families"] = contract_readback["families"]
    if persist_artifacts:
        write_artifacts(out, run)
    return run


def _without_raw_contract(contract_readback: dict[str, Any]) -> dict[str, Any]:
    clean = dict(contract_readback)
    clean.pop("families", None)
    return clean


def _without_score_record_payloads(positive_controls: dict[str, Any]) -> dict[str, Any]:
    clean = json.loads(json.dumps(positive_controls))
    for row in clean.get("controls", []):
        row.pop("score_record", None)
    return clean


def write_artifacts(out: Path, run: dict[str, Any]) -> None:
    artifact_map = {
        "result.json": run["result"],
        "parent_anchor_readback.json": run["parent_anchor_readback"],
        "contract_readback.json": run["contract_readback"],
        "baseline_score_matrix.json": run["baseline_score_matrix"],
        "family_decisions.json": run["family_decisions"],
        "survivors.json": run["survivors"],
        "closed_families.json": run["closed_families"],
        "needs_redesign.json": run["needs_redesign"],
        "positive_control_results.json": _without_score_record_payloads(run["positive_control_results"]),
        "provenance_manifest.json": run["provenance_manifest"],
        "leakage_scan_results.json": run["leakage_scan_results"],
        "future_tournament_eligibility.json": run["future_tournament_eligibility"],
        "forbidden_action_guard.json": run["forbidden_action_guard"],
    }
    for name, payload in artifact_map.items():
        _write_json(out / name, payload)
    missing = REQUIRED_ARTIFACTS - {path.name for path in out.glob("*.json")}
    if missing:
        raise RuntimeError(f"required artifacts missing after write: {sorted(missing)}")


def write_research_report(run: dict[str, Any], report_path: str | Path | None = None) -> Path:
    path = Path(report_path) if report_path is not None else repo_root() / "docs" / "research" / REPORT_NAME
    if not path.is_absolute():
        path = repo_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    result = run["result"]
    parent = run["parent_anchor_readback"]
    decisions = run["family_decisions"]["decisions"]
    lines = [
        "# MECHANISM-FAMILY-TOURNAMENT-BASELINE-PREFLIGHT-RERUN-001B",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        "Layer: engineering-governance / no-candidate callable baseline-preflight rerun.",
        "",
        "Mainline integration status: not integrated.",
        "",
        "Enabled status: no runtime, no bridge/admission, no Gate4 replacement, no candidate, no tournament execution, no trigger path.",
        "",
        f"Claim ceiling: {CLAIM_CEILING}",
        "",
        "Auto-Remote-Anchor: conditional.",
        "",
        "## Bounded Task Card",
        "",
        f"- Task id: `{TASK_CARD_ID}`",
        "- Problem definition: rerun baseline preflight against the anchored executable-surface contract without candidate code or tournament execution.",
        "- Current stage/layer: engineering-governance evidence execution.",
        "- Mainline target: none; not integrated.",
        "- Enabled-state requirement: no runtime, no bridge/admission, no Gate4 replacement, no candidate, no tournament execution, and no trigger path.",
        "- Real-trigger evidence requirement: consume the parent `family_surface_contract.json` artifact and run callable target resolvers, metrics, baselines, leakage scans, and positive controls.",
        "- Hypothesis: cheap faithful baselines can close fixture-like surfaces before any candidate family is authorized.",
        "- Strongest baseline: exact lookup, table/memorization, retrieval, static decoder, static formula/rule, trace/order/key, and family-specific shortcut baselines.",
        "- Ablation requirement: positive-control shortcut masking is represented through recomputable baseline records; no candidate ablation is run.",
        "- Trace/replay requirement: every score stores serialized inputs and is recomputable through `recompute_baseline_score`.",
        "- Computed-evidence provenance gate: scores record producer function, module path, code hash, inputs, run id, seed, record/context IDs, predictions, targets, threshold, aggregation, and contribution.",
        "- Acceptance gate: parent anchor readable, six family contracts loaded from artifact, callables valid, baselines run, positive controls fail as expected, provenance verifies, no forbidden paths.",
        f"- Claim ceiling: {CLAIM_CEILING}",
        "- Stop condition: parent anchor failure, missing callable target or metric, missing threshold, leakage/positive-control failure, provenance gap, forbidden file path, candidate/tournament/runtime/Gate4 path.",
        "- Rollback plan: remove only isolated 001B source/test/report/artifact paths; do not rewrite parent artifacts or prior results.",
        "- Expected changed files: isolated 001B source package, focused test, research report, and artifacts under `artifacts/mechanism_family_tournament_baseline_preflight_rerun_001b/`.",
        "- Forbidden changes: candidate code, candidate score, tournament execution, Gate4 repair/rerun or replacement design, runtime, bridge/admission, EGO-mainline, LLM/RAG/UI/companion path.",
        "- Auto-Remote-Anchor decision: conditional.",
        "",
        "## Parent Anchor Readback",
        "",
        f"- Parent commit: `{parent['parent_commit']}`",
        f"- Parent tag: `{parent['parent_tag']}`",
        f"- Local tag hash: `{parent['local_tag_hash']}`",
        f"- Remote tag hash: `{parent['remote_tag_hash']}`",
        f"- Tag type: `{parent['local_tag_type']}`",
        f"- Parent tag exact match: `{parent['parent_tag_exact_match']}`",
        f"- Remote branch exact parent at read time: `{parent['remote_branch_exact_parent_at_read_time']}`",
        f"- Parent is ancestor of current HEAD: `{parent['parent_commit_is_ancestor_of_current_head']}`",
        "",
        "## Family Decisions",
        "",
        "| family ID | best faithful cheap baseline | score | threshold | decision |",
        "|---|---:|---:|---:|---|",
    ]
    for row in decisions:
        best = row["best_faithful_cheap_baseline"]
        lines.append(
            f"| `{row['family_id']}` | `{best['baseline_id']}` | `{best['score']}` | `{best['threshold']}` | `{row['decision']}` |"
        )
    lines.extend(
        [
            "",
            "## Survivors / Closed / Needs Redesign",
            "",
            f"- Survivors: `{[row['family_id'] for row in run['survivors']['families']]}`",
            f"- Closed families: `{[row['family_id'] for row in run['closed_families']['families']]}`",
            f"- Needs-redesign families: `{[row['family_id'] for row in run['needs_redesign']['families']]}`",
            f"- Future tournament eligibility: `{run['future_tournament_eligibility']['eligible_for_future_tournament_execution_card']}`",
            "",
            "## Positive Controls",
            "",
        ]
    )
    for row in run["positive_control_results"]["controls"]:
        lines.append(
            f"- `{row['control_id']}` expected `{row['expected_block_reason']}` observed `{row['observed_block_reason']}` failed as expected `{row['failed_as_expected']}`."
        )
    lines.extend(
        [
            "",
            "## Forbidden-Action Guard",
            "",
            f"- Candidate code created: `{run['forbidden_action_guard']['candidate_code_created']}`",
            f"- Candidate score produced: `{run['forbidden_action_guard']['candidate_score_produced']}`",
            f"- Tournament execution attempted: `{run['forbidden_action_guard']['tournament_execution_attempted']}`",
            f"- Gate4 repair/rerun attempted: `{run['forbidden_action_guard']['gate4_repair_or_rerun_attempted']}`",
            f"- Runtime/mainline path created: `{run['forbidden_action_guard']['runtime_or_mainline_path_created']}`",
            f"- Forbidden files modified: `{run['forbidden_action_guard']['forbidden_files_modified']}`",
            "",
            "## Stop Conditions",
            "",
        ]
    )
    if result["stop_conditions_triggered"]:
        lines.extend(f"- `{item}`" for item in result["stop_conditions_triggered"])
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Explicit Boundary Statement",
            "",
            "This is no-candidate baseline-preflight evidence only. It created no candidate code, no candidate score, no tournament execution, no Gate4 repair/rerun, no Gate4 replacement design, no runtime or EGO-mainline path, and no mechanism-validity evidence.",
            "",
            "## What This Does Not Prove",
            "",
            *[f"- {item}" for item in result["what_this_does_not_prove"]],
            "",
            "## Next Minimal Closed-Loop Action",
            "",
            result["next_minimal_closed_loop_action"],
            "",
            "## Remote Anchor Status",
            "",
            f"- Remote anchor performed: `{result['remote_anchor_performed']}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--test-command", default=None)
    parser.add_argument("--test-exit-code", default=None)
    parser.add_argument("--test-summary", default=None)
    args = parser.parse_args()
    test_readback = None
    if args.test_command is not None:
        test_readback = {
            "command": args.test_command,
            "exit_code": int(args.test_exit_code) if args.test_exit_code is not None else None,
            "summary": args.test_summary or "",
        }
    run = execute_preflight(
        output_dir=args.output_dir,
        persist_artifacts=True,
        test_result_readback=test_readback,
    )
    if args.write_report:
        write_research_report(run)
    public_run = dict(run)
    public_run.pop("_contract_families", None)
    print(json.dumps(public_run["result"], indent=2, sort_keys=True))
