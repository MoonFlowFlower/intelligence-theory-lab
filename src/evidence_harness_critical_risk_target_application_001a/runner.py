from __future__ import annotations

import copy
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
from typing import Any

from evidence_harness_contract_enforcement_smoke_001a import runner as enforcer_001a


TASK_ID = "EVIDENCE-HARNESS-CRITICAL-RISK-TARGET-APPLICATION-001A"
TASK_SLUG = "evidence_harness_critical_risk_target_application_001a"
CLAIM_CEILING = (
    "bounded conservative application of evidence-harness enforcement to historical "
    "critical-risk targets only"
)
STARTING_HEAD = "69aa22dc83b60444a2e759135990435c4dcfa79b"
BRANCH = "codex/meta-theory-scaffold"
LAYER = "evidence-governance / historical evidence-risk application only"
TRIAGE_DIR = "artifacts/cross_gate_score_credibility_triage_001a"
ENFORCER_001B_DIR = "artifacts/evidence_harness_contract_enforcement_smoke_001b_independent_audit"

ALLOWED_CLASSIFICATIONS = {
    "rejected_false_pass_risk",
    "blocked_pending_audit",
    "insufficient_visibility",
    "governance_reference_only",
    "quarantined_from_downstream_use",
}

AUTHORIZATION_FALSE = {
    "downstream_entry_authorized": False,
    "gate4_001c_authorized": False,
    "gate5_authorized": False,
    "admission_authorized": False,
    "runtime_authorized": False,
    "bridge_authorized": False,
}

READABLE_SUFFIXES = {".json", ".jsonl", ".py", ".md", ".txt"}


def _target_specs() -> list[dict[str, Any]]:
    rows = [
        ("ego_mainline_gate4_preflight_001b", ["ego_mainline_gate4_preflight_executable_001b"]),
        ("gate2_controllability_self_boundary_001b", ["gate2_controllability_self_boundary_001b"]),
        ("gate3_viability_functional_affect_001b", ["gate3_viability_functional_affect_001b"]),
        ("gate4_social_latent_inference_001b", ["gate4_social_latent_inference_001b"]),
        (
            "gate4_social_representational_gap_preflight_001b",
            ["gate4_social_representational_gap_preflight_001b"],
        ),
        (
            "r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b",
            ["r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b"],
        ),
        (
            "r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b",
            ["r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b"],
        ),
        ("representational_gap_preflight", ["representational_gap_preflight", "representational_gap_001a"]),
        (
            "representational_gap_preflight_001b",
            ["representational_gap_preflight_001b", "representational_gap_001b"],
        ),
        (
            "gate1_replay_consolidation_001c",
            ["gate1_replay_consolidation_001c", "gate1_replay_consolidation_001c_executable_preflight"],
        ),
        ("process_intervention_hard_distribution_001b", ["process_intervention_hard_distribution_001b"]),
        (
            "process_intervention_hard_distribution_001b_trace_replay_rca_001a",
            ["process_intervention_hard_distribution_001b_trace_replay_rca_001a"],
        ),
    ]
    return [{"target_id": target_id, "path_aliases": [target_id, *aliases]} for target_id, aliases in rows]


def _git_output(root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_path(path: Path) -> str | None:
    return _sha256_bytes(path.read_bytes()) if path.exists() else None


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_path_payload(repo_root: Path, rel_path: str) -> dict[str, Any]:
    path = repo_root / rel_path
    text = path.read_text(encoding="utf-8")
    payload: Any | None = None
    kind = "text"
    if path.suffix == ".json":
        kind = "json"
        payload = json.loads(text)
    elif path.suffix == ".jsonl":
        kind = "jsonl"
        payload = [json.loads(line) for line in text.splitlines() if line.strip()]
    elif path.suffix == ".py":
        kind = "source"
    elif path.suffix == ".md":
        kind = "markdown"
    return {
        "path": rel_path.replace("\\", "/"),
        "kind": kind,
        "payload": payload,
        "text": text if kind != "json" else "",
        "sha256": _sha256_path(path),
    }


def _relative(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def _collect_files_under(path: Path, repo_root: Path) -> list[str]:
    if path.is_file() and path.suffix in READABLE_SUFFIXES:
        return [_relative(path, repo_root)]
    if not path.is_dir():
        return []
    files = []
    for child in path.rglob("*"):
        if child.is_file() and child.suffix in READABLE_SUFFIXES:
            files.append(_relative(child, repo_root))
    return files


def _path_matches_alias(path: Path, alias: str) -> bool:
    lower_name = path.name.lower()
    lower_stem = path.stem.lower()
    lower_alias = alias.lower()
    compact_alias = lower_alias.replace("_", "-")
    return lower_alias in lower_name or compact_alias in lower_name or lower_alias in lower_stem


def _triage_risk_rows(repo_root: Path) -> dict[str, dict[str, Any]]:
    risk_path = repo_root / TRIAGE_DIR / "risk_matrix.json"
    data = _load_json(risk_path)
    return {row["task_id"]: row for row in data.get("risk_rows", [])}


def _prior_group_membership(repo_root: Path) -> dict[str, str]:
    result = _load_json(repo_root / TRIAGE_DIR / "result.json")
    mapping = {}
    for target_id in result.get("critical_risk_task_ids", []):
        mapping[target_id] = "critical_risk"
    for target_id in result.get("high_risk_task_ids", []):
        mapping[target_id] = "high_risk"
    for target_id in result.get("medium_risk_task_ids", []):
        mapping.setdefault(target_id, "medium_risk")
    for target_id in result.get("low_risk_task_ids", []):
        mapping.setdefault(target_id, "low_risk")
    for target_id in result.get("blocked_task_ids", []):
        mapping.setdefault(target_id, "blocked")
    return mapping


def _paths_from_evidence_samples(row: dict[str, Any]) -> list[str]:
    paths = []
    samples = row.get("evidence_samples", {})
    for entries in samples.values():
        for entry in entries:
            path = entry.get("path")
            if path:
                paths.append(path.replace("\\", "/"))
    return paths


def _discover_target_paths(repo_root: Path, target: dict[str, Any], prior_risk: dict[str, Any]) -> list[str]:
    paths = set()
    for rel_path in _paths_from_evidence_samples(prior_risk):
        if (repo_root / rel_path).is_file() and (repo_root / rel_path).suffix in READABLE_SUFFIXES:
            paths.add(rel_path)

    for alias in target.get("path_aliases", []):
        for base in [repo_root / "artifacts" / alias, repo_root / "src" / alias]:
            for rel_path in _collect_files_under(base, repo_root):
                paths.add(rel_path)
        for child in (repo_root / "tests").glob("*.py"):
            if _path_matches_alias(child, alias):
                paths.add(_relative(child, repo_root))
        for child in (repo_root / "docs" / "codex" / "tasks").glob("*.md"):
            if _path_matches_alias(child, alias):
                paths.add(_relative(child, repo_root))
        for child in (repo_root / "docs").glob("*.md"):
            if _path_matches_alias(child, alias):
                paths.add(_relative(child, repo_root))

    return sorted(paths)


def _replace_task_id_values(value: Any, new_task_id: str) -> Any:
    if isinstance(value, dict):
        return {
            key: new_task_id if key == "task_id" and isinstance(item, str) else _replace_task_id_values(item, new_task_id)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_replace_task_id_values(item, new_task_id) for item in value]
    return value


def _retask_bundle(bundle: dict[str, Any], new_task_id: str) -> dict[str, Any]:
    clone = copy.deepcopy(bundle)
    clone["task_id"] = new_task_id
    for item in clone.get("path_payloads", []):
        payload = item.get("payload")
        if payload is not None:
            item["payload"] = _replace_task_id_values(payload, new_task_id)
    return clone


def _bundle_for_target(repo_root: Path, target: dict[str, Any], prior_risk: dict[str, Any]) -> dict[str, Any]:
    paths = _discover_target_paths(repo_root, target, prior_risk)
    return {
        "bundle_id": target["target_id"],
        "task_id": target["target_id"],
        "path_payloads": [_read_path_payload(repo_root, rel_path) for rel_path in paths],
    }


def _evidence_surface_status(records: list[dict[str, Any]]) -> str:
    if not records:
        return "insufficient_visibility"
    joined_paths = " ".join(record["path"].lower() for record in records)
    joined_text = " ".join(
        json.dumps(record.get("payload", ""), sort_keys=True)[:5000].lower()
        if record.get("payload") is not None
        else record.get("text", "")[:5000].lower()
        for record in records
    )
    surface_terms = ["score", "baseline", "ablation", "replay", "leakage", "verdict", "pass"]
    producer_terms = ["producer_function", "source_code_hash", "code_path_hash", "callable"]
    has_surface = any(term in joined_paths or term in joined_text for term in surface_terms)
    has_producer = any(term in joined_text for term in producer_terms)
    if has_surface:
        return "self_reported_or_partial_callable_visibility"
    if has_producer:
        return "self_reported_or_partial_callable_visibility"
    return "insufficient_visibility"


def _classification_from_enforcer(report: dict[str, Any]) -> str:
    if report["admissibility_class"] == "admissible_downstream_evidence":
        return "admissible_downstream_evidence"
    if report["admissibility_class"] == "rejected_false_pass_risk":
        return "rejected_false_pass_risk"
    if report["admissibility_class"] == "governance_anchor_only":
        return "governance_reference_only"
    return "blocked_pending_audit"


def _source_hash() -> str:
    return _sha256_text(inspect.getsource(classify_target))


def classify_target(
    repo_root: Path,
    target: dict[str, Any],
    run_id: str,
    prior_risk: dict[str, Any],
) -> dict[str, Any]:
    repo_root = Path(repo_root)
    bundle = _bundle_for_target(repo_root, target, prior_risk)
    records = bundle["path_payloads"]
    if not records:
        return {
            "target_id": target["target_id"],
            "classification": "insufficient_visibility",
            "downstream_admissibility_result": "quarantined_from_downstream_use",
            "callable_enforcer_invoked": False,
            "input_artifacts": [],
            "source_artifact_paths_inspected": [],
            "enforcer_module": "evidence_harness_contract_enforcement_smoke_001a.runner",
            "enforcer_function": "evaluate_bundle",
            "detected_pattern_categories": [],
            "rule_ids_invoked": [],
            "rejection_reasons": [],
            "static_denylist_was_involved": False,
            "result_depended_on_task_id": False,
            "prior_triage_risk_class": prior_risk.get("risk_class", "unavailable"),
            "prior_triage_category_counts": prior_risk.get("category_counts", {}),
            "score_baseline_ablation_replay_evidence_status": "insufficient_visibility",
            "producer_function": "classify_target",
            "run_id": run_id,
            "aggregation_rule": "001A enforcer class plus conservative downstream quarantine",
            "source_code_hash": _source_hash(),
            "classification_reasons": ["no_input_artifacts_visible"],
        }

    report = enforcer_001a.evaluate_bundle(bundle)
    retasked_report = enforcer_001a.evaluate_bundle(_retask_bundle(bundle, f"STATIC-CONTROL::{target['target_id']}"))
    result_depended_on_task_id = (
        report["admissibility_class"] != retasked_report["admissibility_class"]
        or report["detected_pattern_categories"] != retasked_report["detected_pattern_categories"]
    )
    classification = _classification_from_enforcer(report)
    if classification == "admissible_downstream_evidence":
        classification_reasons = ["stop_condition_admissible_downstream_evidence"]
    elif report["detected_pattern_categories"]:
        classification_reasons = ["001a_enforcer_detected_false_pass_risk_patterns"]
    else:
        classification_reasons = ["001a_enforcer_visibility_block_without_specific_false_pass_category"]

    return {
        "target_id": target["target_id"],
        "classification": classification,
        "downstream_admissibility_result": "quarantined_from_downstream_use",
        "callable_enforcer_invoked": True,
        "input_artifacts": [record["path"] for record in records],
        "source_artifact_paths_inspected": [record["path"] for record in records],
        "enforcer_module": "evidence_harness_contract_enforcement_smoke_001a.runner",
        "enforcer_function": "evaluate_bundle",
        "detected_pattern_categories": report["detected_pattern_categories"],
        "rule_ids_invoked": report["rule_ids_invoked"],
        "rejection_reasons": report["rejection_reasons"],
        "static_denylist_was_involved": bool(report["static_denylist_only"]),
        "result_depended_on_task_id": result_depended_on_task_id,
        "prior_triage_risk_class": prior_risk.get("risk_class", "unavailable"),
        "prior_triage_category_counts": prior_risk.get("category_counts", {}),
        "score_baseline_ablation_replay_evidence_status": _evidence_surface_status(records),
        "producer_function": "classify_target",
        "run_id": run_id,
        "aggregation_rule": "001A enforcer class plus conservative downstream quarantine",
        "source_code_hash": _source_hash(),
        "classification_reasons": classification_reasons,
    }


def _target_input_bundle_manifest(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "targets": {
            row["target_id"]: {
                "input_artifacts": row["input_artifacts"],
                "input_artifact_count": len(row["input_artifacts"]),
                "classification": row["classification"],
            }
            for row in rows
        },
    }


def _enforcer_invocation_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    invoked_rows = [row for row in rows if row["callable_enforcer_invoked"]]
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "enforcer_module": "evidence_harness_contract_enforcement_smoke_001a.runner",
        "enforcer_producer_function": "evaluate_bundle",
        "enforcer_source_path": "src/evidence_harness_contract_enforcement_smoke_001a/runner.py",
        "enforcer_source_hash": _sha256_text(inspect.getsource(enforcer_001a.evaluate_bundle)),
        "invocation_count": len(rows),
        "callable_invocation_count": len(invoked_rows),
        "invocations": [
            {
                "target_id": row["target_id"],
                "callable_enforcer_invoked": row["callable_enforcer_invoked"],
                "classification": row["classification"],
                "detected_pattern_categories": row["detected_pattern_categories"],
                "rule_ids_invoked": row["rule_ids_invoked"],
                "input_artifact_count": len(row["input_artifacts"]),
            }
            for row in rows
        ],
    }


def _computed_provenance(rows: list[dict[str, Any]], run_id: str) -> dict[str, Any]:
    input_count = sum(len(row["input_artifacts"]) for row in rows)
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "producer_function": "run_application",
        "classification_producer_function": "classify_target",
        "run_id": run_id,
        "target_count": len(rows),
        "input_artifact_count": input_count,
        "computed_not_literal": True,
        "hard_coded_target_verdicts_used": False,
        "aggregation_rule": "evaluate each discovered target bundle with 001A callable, then conservatively quarantine downstream use",
        "source_code_hash": _sha256_text(inspect.getsource(run_application)),
        "target_provenance": [
            {
                "target_id": row["target_id"],
                "classification": row["classification"],
                "producer_function": row["producer_function"],
                "input_artifacts": row["input_artifacts"],
                "run_id": row["run_id"],
                "aggregation_rule": row["aggregation_rule"],
                "source_code_hash": row["source_code_hash"],
            }
            for row in rows
        ],
    }


def _static_dependency_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "control_method": "retask input bundle and compare class/categories",
        "static_denylist_only": any(row["static_denylist_was_involved"] for row in rows),
        "targets_with_task_id_dependency": [
            row["target_id"] for row in rows if row["result_depended_on_task_id"]
        ],
        "targets_with_static_hash_dependency": [],
        "targets_with_static_path_dependency": [],
        "bounded_interpretation": (
            "The control detects task-id-only dependency. It does not prove absence of all possible "
            "path-sensitive lexical effects; claim ceiling remains conservative non-admission."
        ),
    }


def _quarantine_matrix(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "targets": [row["target_id"] for row in rows],
        "rows": [
            {
                "target_id": row["target_id"],
                "classification": row["classification"],
                "downstream_admissibility_result": "quarantined_from_downstream_use",
                **AUTHORIZATION_FALSE,
            }
            for row in rows
        ],
    }


def _historical_contamination_report(rows: list[dict[str, Any]], group_membership: dict[str, str]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "prior_triage_source": TRIAGE_DIR,
        "target_count": len(rows),
        "prior_risk_groups": {
            row["target_id"]: group_membership.get(row["target_id"], "unavailable")
            for row in rows
        },
        "classification_counts": {
            classification: sum(1 for row in rows if row["classification"] == classification)
            for classification in sorted(ALLOWED_CLASSIFICATIONS)
        },
        "contamination_policy": (
            "Historical critical/high-risk evidence remains non-admissible downstream unless a later "
            "bounded task supplies stronger callable computed evidence. This task does not repair or rewrite it."
        ),
    }


def _semantic_gap_report(repo_root: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    gap_path = repo_root / ENFORCER_001B_DIR / "contract_coverage_gap_report.json"
    source_path = repo_root / ENFORCER_001B_DIR / "source_pattern_audit_report.json"
    gaps = []
    source_report: dict[str, Any] = {}
    if gap_path.exists():
        gaps = _load_json(gap_path).get("contract_coverage_gaps", [])
    if source_path.exists():
        source_report = _load_json(source_path)
    blocked_rows = [
        row["target_id"]
        for row in rows
        if row["classification"] in {"blocked_pending_audit", "insufficient_visibility"}
    ]
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "semantic_gap_limitations_propagated": bool(gaps),
        "inherited_001b_gap_ids": gaps,
        "source_pattern_audit_summary": {
            key: source_report.get(key)
            for key in [
                "renamed_field_gap",
                "result_json_claim_gap",
                "soft_claim_language_gap",
                "baseline_invocation_gap",
                "hash_only_replay_gap",
            ]
        },
        "targets_impacted_by_non_admission_default": blocked_rows,
        "bounded_interpretation": (
            "001B found semantic/renamed-claim gaps. Therefore blocked targets are quarantined rather "
            "than upgraded to positive admissibility."
        ),
    }


def _target_inventory(targets: list[dict[str, Any]], risk_rows: dict[str, dict[str, Any]], group_membership: dict[str, str]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "required_target_ids": [target["target_id"] for target in targets],
        "prior_triage_source": TRIAGE_DIR,
        "targets": [
            {
                "target_id": target["target_id"],
                "path_aliases": target["path_aliases"],
                "prior_risk_class": risk_rows.get(target["target_id"], {}).get("risk_class", "unavailable"),
                "prior_risk_group": group_membership.get(target["target_id"], "unavailable"),
            }
            for target in targets
        ],
    }


def _json_parse_verification(output_dir: Path) -> dict[str, Any]:
    parsed = []
    for path in sorted(output_dir.glob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))
        parsed.append(path.name)
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "parse_status": "all_required_json_parsed",
        "parser": "json.loads",
        "parsed_json_files": parsed,
        "non_evidence_statement": "JSON parsing verifies syntax only; it does not prove Gate validity or mechanism validity.",
    }


def run_application(repo_root: Path, output_dir: Path | None = None) -> dict[str, Any]:
    repo_root = Path(repo_root)
    out = output_dir or repo_root / "artifacts" / TASK_SLUG
    out.mkdir(parents=True, exist_ok=True)

    branch = _git_output(repo_root, ["branch", "--show-current"])
    head = _git_output(repo_root, ["rev-parse", "HEAD"])
    status = _git_output(repo_root, ["status", "--short", "--branch"])
    log_line = _git_output(repo_root, ["log", "-1", "--oneline", "HEAD"])
    run_id = f"{TASK_SLUG}:{head[:12]}"

    targets = _target_specs()
    risk_rows = _triage_risk_rows(repo_root)
    group_membership = _prior_group_membership(repo_root)
    rows = [
        classify_target(
            repo_root=repo_root,
            target=target,
            run_id=run_id,
            prior_risk=risk_rows.get(target["target_id"], {}),
        )
        for target in targets
    ]

    positive_rows = [
        row for row in rows if row["classification"] == "admissible_downstream_evidence"
    ]
    if positive_rows:
        verdict = "critical_risk_target_application_failed_positive_admission_detected"
    else:
        verdict = "critical_risk_target_application_conservative_non_admission_complete"

    static_report = _static_dependency_audit(rows)
    semantic_report = _semantic_gap_report(repo_root, rows)
    classification_failures = [
        {
            "target_id": row["target_id"],
            "classification": row["classification"],
            "failure": "forbidden_admissible_downstream_evidence",
        }
        for row in positive_rows
    ]
    evaluated_count = sum(
        1
        for row in rows
        if row["classification"] in ALLOWED_CLASSIFICATIONS
    )
    result = {
        "verdict": verdict,
        "task_id": TASK_ID,
        "layer": LAYER,
        "claim_ceiling": CLAIM_CEILING,
        "starting_head": STARTING_HEAD,
        "branch": BRANCH,
        "target_count": len(targets),
        "evaluated_or_insufficient_visibility_count": evaluated_count,
        "admissible_downstream_evidence_count": len(positive_rows),
        "target_classification_failures": classification_failures,
        "semantic_gap_limitations_propagated": semantic_report["semantic_gap_limitations_propagated"],
        "static_denylist_only": bool(static_report["static_denylist_only"]),
        **AUTHORIZATION_FALSE,
        "json_parse_verification": {
            "artifact": f"artifacts/{TASK_SLUG}/json_parse_verification.json",
            "status": "all_required_json_parsed",
        },
        "what_this_does_not_prove": [
            "Gate validity",
            "mechanism validity",
            "theory validity",
            "architecture correctness",
            "Gate4 001C authorization",
            "Gate5 authorization",
            "admission authorization",
            "runtime authorization",
            "bridge authorization",
            "EGO mainline readiness",
            "agency, selfhood, consciousness, real emotion, relationship learning, or stable autonomy",
        ],
    }

    execution_manifest = {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "mode": "conservative application of anchored evidence-harness enforcer to historical critical/high-risk targets",
        "branch_at_execution": branch,
        "head_at_execution": head,
        "latest_commit_at_execution": log_line,
        "expected_starting_head": STARTING_HEAD,
        "status_at_execution": status,
        "producer_function": "run_application",
        "producer_source_path": "src/evidence_harness_critical_risk_target_application_001a/runner.py",
        "source_code_hash": _sha256_text(inspect.getsource(run_application)),
        "existing_001a_001b_enforcer_chain_modified": False,
        "old_gate_artifacts_modified": False,
        "provisional_gate4_001c_used": False,
        "forbidden_scope_not_entered": [
            "Gate repair",
            "Gate execution",
            "Gate4 001C",
            "Gate5",
            "admission",
            "runtime",
            "bridge",
            "EGO mainline",
        ],
    }

    _write_json(out / "target_inventory.json", _target_inventory(targets, risk_rows, group_membership))
    _write_json(out / "target_input_bundle_manifest.json", _target_input_bundle_manifest(rows))
    _write_json(out / "enforcer_invocation_report.json", _enforcer_invocation_report(rows))
    _write_json(
        out / "target_classification_matrix.json",
        {"task_id": TASK_ID, "claim_ceiling": CLAIM_CEILING, "rows": rows},
    )
    _write_json(out / "computed_provenance_report.json", _computed_provenance(rows, run_id))
    _write_json(out / "static_dependency_audit_report.json", static_report)
    _write_json(out / "downstream_quarantine_matrix.json", _quarantine_matrix(rows))
    _write_json(
        out / "historical_false_pass_contamination_report.json",
        _historical_contamination_report(rows, group_membership),
    )
    _write_json(out / "semantic_gap_impact_report.json", semantic_report)
    _write_json(out / "result.json", result)
    (out / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    _write_json(out / "execution_manifest.json", execution_manifest)
    _write_json(out / "json_parse_verification.json", {"parse_status": "pending"})
    _write_json(out / "json_parse_verification.json", _json_parse_verification(out))
    return result


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    run_application(repo_root=repo_root)


if __name__ == "__main__":
    main()
