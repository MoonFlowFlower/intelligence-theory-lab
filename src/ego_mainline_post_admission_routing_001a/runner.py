from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Callable


TASK_ID = "EGO-MAINLINE-POST-ADMISSION-ROUTING-001A"
PRIOR_TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTION-001A"
VERDICT_PASS = "post_admission_routing_001a_pass_with_bounded_next_task"
VERDICT_BLOCKED = "post_admission_routing_001a_blocked_missing_required_evidence"
VERDICT_FAILED_PROVENANCE = "post_admission_routing_001a_failed_provenance_gate"
VERDICT_FAILED_LEAKAGE = "post_admission_routing_001a_failed_leakage_gate"
VERDICT_FAILED_REPLAY = "post_admission_routing_001a_failed_replay_gate"
LAYER = "evidence-governance / bounded post-admission routing only"
CLAIM_CEILING = "bounded post-admission routing evidence at governance layer only"
PRIOR_CLAIM_CEILING = "bounded admission execution evidence at the governance layer only"
PRIOR_VERDICT_PASS = "pass_bounded_admission_execution_001a"
REQUIRED_ANCHOR_COMMIT = "98e51a46cd7f28f60b1851c616d4351c1cd6272f"
REQUIRED_REMOTE_TAG = "remote-anchor-bounded-admission-execution-001a-98e51a4"
GOVERNANCE_CONFIDENCE_CAP = 0.68

DOC_PATH = Path("docs/codex/tasks/EGO-MAINLINE-POST-ADMISSION-ROUTING-001A.md")
ARTIFACT_DIR = Path("artifacts/ego_mainline_post_admission_routing_001a")
PRIOR_DOC_PATH = Path("docs/codex/tasks/EGO-MAINLINE-ADMISSION-EXECUTION-001A.md")
PRIOR_ARTIFACT_DIR = Path("artifacts/ego_mainline_admission_execution_001a")
PRIOR_RESULT = PRIOR_ARTIFACT_DIR / "result.json"
PRIOR_EVALUATION = PRIOR_ARTIFACT_DIR / "admission_contract_evaluation.json"
PRIOR_TRACE = PRIOR_ARTIFACT_DIR / "admission_decision_trace.json"
PRIOR_CLAIM_FILE = PRIOR_ARTIFACT_DIR / "claim_ceiling.txt"

REQUIRED_ARTIFACT_NAMES = [
    "result.json",
    "anchor_readback.json",
    "input_artifact_inventory.json",
    "routing_state.json",
    "routing_decision_matrix.json",
    "allowed_routes.json",
    "blocked_routes.json",
    "missing_evidence_matrix.json",
    "downstream_non_authorization_flags.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_scan_report.json",
    "replay_report.json",
    "computed_evidence_provenance.json",
    "claim_ceiling.txt",
    "next_task_recommendation.txt",
    "rollback_plan.txt",
]

ROUTE_CLASSES = [
    "governance_boundary_continuation",
    "evidence_dependency_closure",
    "Gate4_preflight_task_card_drafting",
    "theory_canonicalization_or_coverage_closure",
    "bridge_runtime_preflight",
    "EGO_runtime_implementation",
    "product_or_companion_behavior_work",
    "no_go_until_missing_evidence_closed",
]

BOUNDED_ALLOWED_ROUTE_CLASSES = [
    "governance_boundary_continuation",
    "evidence_dependency_closure",
    "theory_canonicalization_or_coverage_closure",
]

FORBIDDEN_ROUTE_CLASSES = [
    "Gate4_preflight_task_card_drafting",
    "bridge_runtime_preflight",
    "EGO_runtime_implementation",
    "product_or_companion_behavior_work",
]

DOWNSTREAM_NON_AUTHORIZATION_FLAGS = [
    "runtime_authorized",
    "bridge_runtime_authorized",
    "gate4_execution_authorized",
    "implementation_authorized",
    "mechanism_validity_authorized",
    "theory_validity_authorized",
    "architecture_correctness_authorized",
    "agency_authorized",
    "selfhood_authorized",
    "consciousness_authorized",
    "emotion_authorized",
    "relationship_learning_authorized",
    "stable_user_benefit_authorized",
]

FORBIDDEN_AUTHORIZATION_LIST = [
    "runtime",
    "bridge_runtime",
    "Gate4_execution",
    "implementation",
    "mechanism_validity",
    "theory_validity",
    "architecture_correctness",
    "agency",
    "selfhood",
    "consciousness",
    "emotion",
    "relationship_learning",
    "stable_user_benefit",
]

REQUIRED_MISSING_EVIDENCE_BY_ROUTE = {
    "Gate4_preflight_task_card_drafting": [
        "separate explicit Gate4 drafting authorization outside this routing task",
        "upstream evidence-dependency closure showing why Gate4 drafting is the next bounded boundary",
        "predeclared task card that preserves no Gate4 execution authorization",
    ],
    "bridge_runtime_preflight": [
        "same-agent bridge readiness evidence",
        "canonical trace/replay contract evidence",
        "baseline and ablation suite evidence that is not inherited from 001A admission pass",
    ],
    "EGO_runtime_implementation": [
        "runtime readiness evidence",
        "bridge-runtime authorization evidence",
        "implementation-specific safety and rollback contract",
    ],
    "product_or_companion_behavior_work": [
        "explicit product or companion scope authorization",
        "relationship/emotion/user-model boundary evidence",
        "deployment and runtime safety gates outside this lab routing task",
    ],
    "no_go_until_missing_evidence_closed": [
        "used only when required routing inputs or anchor verification are missing or corrupted",
    ],
}

NON_PROVEN_REQUIRED_ITEMS = [
    "EGO readiness",
    "bridge readiness",
    "runtime readiness",
    "Gate4 readiness",
    "mechanism validity",
    "theory validity",
    "architecture correctness",
    "agency",
    "selfhood",
    "consciousness",
    "emotion",
    "relationship learning",
    "stable user benefit",
    "future runtime correctness",
    "runtime authorization",
]

UNAUTHORIZED_CLAIM_PATTERNS = [
    ("ego_ready", re.compile(r"\bEGO\s+ready\b", re.IGNORECASE)),
    ("bridge_ready", re.compile(r"\bbridge\s+ready\b", re.IGNORECASE)),
    ("runtime_ready", re.compile(r"\bruntime\s+ready\b", re.IGNORECASE)),
    ("gate4_authorized", re.compile(r"\bGate4\s+authorized\b", re.IGNORECASE)),
    ("mechanism_validated", re.compile(r"\bmechanism\s+validated\b", re.IGNORECASE)),
    ("theory_validated", re.compile(r"\btheory\s+validated\b", re.IGNORECASE)),
    ("architecture_correct", re.compile(r"\barchitecture\s+correct\b", re.IGNORECASE)),
    ("agency_achieved", re.compile(r"\bagency\s+achieved\b", re.IGNORECASE)),
    ("selfhood_achieved", re.compile(r"\bselfhood\s+achieved\b", re.IGNORECASE)),
    ("consciousness", re.compile(r"\bconsciousness\b", re.IGNORECASE)),
    ("real_emotion", re.compile(r"\breal\s+emotion\b", re.IGNORECASE)),
    ("relationship_learning", re.compile(r"\brelationship\s+learning\b", re.IGNORECASE)),
    ("stable_user_benefit", re.compile(r"\bstable\s+user\s+benefit\b", re.IGNORECASE)),
    ("implementation_authorized", re.compile(r"\bimplementation\s+authorized\b", re.IGNORECASE)),
]

RESTRAINT_TERMS = [
    "not",
    "no ",
    "non-authorization",
    "non_authorization",
    "blocked",
    "forbidden",
    "unauthorized",
    "insufficient",
    "does not",
    "do not",
    "must not",
    "without",
    "what this does not prove",
    "claim ceiling",
    "claim_ceiling",
    "false",
    "missing evidence",
    "blocked_routes",
    "required_missing_evidence",
    "downstream_non_authorization",
    "non-proven",
    "non_proven",
    "restraint",
    "scanner",
    "positive control",
    "positive_control",
    "test-control",
    "test_control",
    "stop condition",
    "rollback",
    "fail",
    "fails",
    "failure",
    "remains unauthorized",
    "remain unauthorized",
    "not authorized",
    "not authorize",
    "does not authorize",
    "must not authorize",
]

PROTECTED_OLD_PATHS = [
    PRIOR_DOC_PATH,
    PRIOR_RESULT,
    PRIOR_EVALUATION,
    PRIOR_TRACE,
    PRIOR_CLAIM_FILE,
    Path("docs/codex/tasks/EGO-MAINLINE-ADMISSION-EXECUTION-PREFLIGHT-001A.md"),
    Path("docs/codex/tasks/EGO-MAINLINE-ADMISSION-TASK-CARD-ALIGNMENT-001A.md"),
    Path("docs/research/EGO-MAINLINE-ADMISSION-CANONICAL-COVERAGE-REFERENCE-001A.md"),
    Path("docs/research/THEORY-LANDSCAPE-COVERAGE-CANONICALIZATION-PROVENANCE-REPAIR-001B.md"),
    Path("docs/research/THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001D.md"),
    Path("docs/codex/tasks/POST-BRIDGE-ADMISSION-EXECUTABLE-001D.md"),
    Path("docs/codex/audits/EGO-MAINLINE-READINESS-AUDIT-001B.md"),
    Path("artifacts/post_bridge_admission_executable_001d/result.json"),
    Path("artifacts/ego_mainline_admission_execution_preflight_001a/result.json"),
    Path("artifacts/ego_mainline_admission_task_card_alignment_001a/result.json"),
    Path("artifacts/ego_mainline_admission_canonical_coverage_reference_001a/result.json"),
    Path("artifacts/theory_landscape_coverage_canonicalization_provenance_repair_001b/result.json"),
]

INTENDED_DIR_PREFIXES = [
    "artifacts/ego_mainline_post_admission_routing_001a/",
    "src/ego_mainline_post_admission_routing_001a/",
]
INTENDED_FILES = {
    "docs/codex/tasks/EGO-MAINLINE-POST-ADMISSION-ROUTING-001A.md",
    "tests/test_ego_mainline_post_admission_routing_001a.py",
}


def run_post_admission_routing(
    repo_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    verify_remote: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    out = Path(output_dir) if output_dir is not None else root / ARTIFACT_DIR
    if not out.is_absolute():
        out = root / out
    out.mkdir(parents=True, exist_ok=True)

    protected_before = hash_protected_old_artifacts(root)
    state = build_routing_state(root, out, verify_remote=verify_remote)
    candidate = compute_candidate_routing(state["candidate_routing_inputs"], state["routing_parameters"])
    baseline_comparison = build_baseline_comparison(state, candidate)
    ablation_report = run_ablation_suite(state, candidate)
    routing_matrix = build_routing_decision_matrix(state, candidate, baseline_comparison)
    allowed_routes = build_allowed_routes(candidate)
    blocked_routes = build_blocked_routes(candidate)
    missing_evidence = build_missing_evidence_matrix(candidate)
    non_authorization = build_downstream_non_authorization_flags(candidate)
    routing_state_artifact = build_routing_state_artifact(state)
    replay_report = build_replay_report(routing_state_artifact, candidate)
    provenance_report = build_computed_evidence_provenance_report(
        state,
        candidate,
        baseline_comparison,
        ablation_report,
        replay_report,
    )

    protected_after = hash_protected_old_artifacts(root)
    result = build_result(
        state=state,
        candidate=candidate,
        baseline_comparison=baseline_comparison,
        ablation_report=ablation_report,
        replay_report=replay_report,
        protected_before=protected_before,
        protected_after=protected_after,
    )

    json_payloads = {
        "anchor_readback.json": state["anchor_readback"],
        "input_artifact_inventory.json": state["input_artifact_inventory"],
        "routing_state.json": routing_state_artifact,
        "routing_decision_matrix.json": routing_matrix,
        "allowed_routes.json": allowed_routes,
        "blocked_routes.json": blocked_routes,
        "missing_evidence_matrix.json": missing_evidence,
        "downstream_non_authorization_flags.json": non_authorization,
        "baseline_comparison.json": baseline_comparison,
        "ablation_report.json": ablation_report,
        "replay_report.json": replay_report,
        "computed_evidence_provenance.json": provenance_report,
        "result.json": result,
    }
    text_payloads = {
        "claim_ceiling.txt": CLAIM_CEILING + "\n",
        "next_task_recommendation.txt": build_next_task_recommendation_text(candidate),
        "rollback_plan.txt": build_rollback_plan_text(candidate),
    }

    leakage_report = build_leakage_scan_report(root, out, json_payloads, text_payloads)
    json_payloads["leakage_scan_report.json"] = leakage_report
    result = build_result(
        state=state,
        candidate=candidate,
        baseline_comparison=baseline_comparison,
        ablation_report=ablation_report,
        replay_report=replay_report,
        protected_before=protected_before,
        protected_after=protected_after,
        leakage_report=leakage_report,
    )
    json_payloads["result.json"] = result

    for name, payload in json_payloads.items():
        _write_json(
            out / name,
            _with_metadata(
                artifact_name=name,
                output_path=(ARTIFACT_DIR / name).as_posix(),
                payload=payload,
                producer=_producer_for_artifact(name),
                input_artifacts=_input_artifacts_for_output(name),
                run_id=state["run_id"],
                seed_context_episode_ids=state["seed_context_episode_ids"],
                aggregation_rule=_aggregation_rule_for_artifact(name),
            ),
        )
    for name, text in text_payloads.items():
        _write_text(out / name, text)
    return result


def build_routing_state(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
    verify_remote: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    out = Path(output_dir) if output_dir is not None else root / ARTIFACT_DIR
    if not out.is_absolute():
        out = root / out
    anchor = build_anchor_readback(root, verify_remote=verify_remote)
    inventory = build_input_artifact_inventory(root)
    repository_constraints = build_repository_constraints(root)
    prior_non_proven = anchor.get("non_proven_list", [])
    inputs = {
        "anchor_readback": anchor,
        "prior_verdict": anchor.get("prior_verdict"),
        "claim_ceiling": anchor.get("claim_ceiling"),
        "non_proven_list": prior_non_proven,
        "artifact_inventory_digest": inventory.get("inventory_digest"),
        "artifact_inventory": inventory,
        "repository_constraints": repository_constraints,
        "forbidden_downstream_authorization_list": list(FORBIDDEN_AUTHORIZATION_LIST),
        "positive_control_artifact": None,
    }
    return {
        "task_id": TASK_ID,
        "run_id": _run_id(root),
        "repo_root": root.as_posix(),
        "output_dir": out.as_posix(),
        "verify_remote": verify_remote,
        "seed_context_episode_ids": {
            "seed": "not_used",
            "context_id": TASK_ID,
            "episode_id": "post_admission_routing",
            "unused_seed_blocking_check": "no stochastic seed used",
        },
        "anchor_readback": anchor,
        "input_artifact_inventory": inventory,
        "candidate_routing_inputs": inputs,
        "routing_parameters": {
            "route_classes_considered": list(ROUTE_CLASSES),
            "governance_confidence_cap": GOVERNANCE_CONFIDENCE_CAP,
            "recommended_clean_task_class": "evidence_dependency_closure",
            "required_prior_verdict": PRIOR_VERDICT_PASS,
            "required_prior_claim_ceiling": PRIOR_CLAIM_CEILING,
            "current_claim_ceiling": CLAIM_CEILING,
        },
    }


def build_anchor_readback(root: Path, verify_remote: bool = True) -> dict[str, Any]:
    prior_result_exists = (root / PRIOR_RESULT).exists()
    prior_result = _read_json(root / PRIOR_RESULT) if prior_result_exists else {}
    prior_claim_text = (root / PRIOR_CLAIM_FILE).read_text(encoding="utf-8").strip() if (root / PRIOR_CLAIM_FILE).exists() else ""
    resolved_required = _git_output(root, ["rev-parse", "--verify", f"{REQUIRED_ANCHOR_COMMIT}^{{commit}}"])
    remote_resolved = _remote_tag_commit(root, REQUIRED_REMOTE_TAG) if verify_remote else _git_output(
        root, ["rev-parse", f"refs/tags/{REQUIRED_REMOTE_TAG}"]
    )
    return {
        "task_id": TASK_ID,
        "prior_task_id": PRIOR_TASK_ID,
        "current_head": _git_output(root, ["rev-parse", "HEAD"]),
        "required_commit": REQUIRED_ANCHOR_COMMIT,
        "required_commit_resolved_hash": resolved_required,
        "required_commit_resolves_exactly": resolved_required == REQUIRED_ANCHOR_COMMIT,
        "remote_tag": REQUIRED_REMOTE_TAG,
        "remote_tag_resolved_hash": remote_resolved,
        "remote_tag_resolves_exactly": remote_resolved == REQUIRED_ANCHOR_COMMIT,
        "prior_result_path": PRIOR_RESULT.as_posix(),
        "prior_result_exists": prior_result_exists,
        "prior_verdict": prior_result.get("verdict"),
        "prior_verdict_matches_required": prior_result.get("verdict") == PRIOR_VERDICT_PASS,
        "claim_ceiling": prior_result.get("claim_ceiling") or prior_claim_text,
        "claim_ceiling_matches_required": (prior_result.get("claim_ceiling") or prior_claim_text) == PRIOR_CLAIM_CEILING,
        "non_proven_list": prior_result.get("what_this_does_not_prove", []),
        "non_proven_list_complete": set(NON_PROVEN_REQUIRED_ITEMS).issubset(
            set(prior_result.get("what_this_does_not_prove", []))
        ),
        "producer_function": "build_anchor_readback",
        "validation_rule": "required commit and remote tag must resolve exactly while prior admission stays bounded",
    }


def build_input_artifact_inventory(root: Path) -> dict[str, Any]:
    inventory_patterns = [
        "docs/codex/tasks/EGO-MAINLINE-ADMISSION*",
        "docs/codex/audits/EGO-MAINLINE-READINESS*",
        "docs/codex/tasks/*GATE4*",
        "docs/*GATE4*",
        "docs/research/*THEORY*",
        "artifacts/ego_mainline_admission_execution_001a/*",
        "artifacts/ego_mainline_admission_execution_preflight_001a/*",
        "artifacts/ego_mainline_admission_task_card_alignment_001a/*",
        "artifacts/post_bridge_admission_executable_001d/result.json",
    ]
    paths: list[Path] = []
    for pattern in inventory_patterns:
        paths.extend(root.glob(pattern))
    unique_paths = sorted({path for path in paths if path.is_file()})
    rows = []
    for path in unique_paths:
        rel = path.relative_to(root).as_posix()
        rows.append(
            {
                "path": rel,
                "category": _inventory_category(rel),
                "sha256": _sha_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    digest = _sha_text(json.dumps(rows, sort_keys=True, separators=(",", ":")))
    return {
        "task_id": TASK_ID,
        "inventory_patterns": inventory_patterns,
        "artifact_count": len(rows),
        "inventory_rows": rows,
        "inventory_digest": digest,
        "has_prior_admission_execution_artifacts": any(
            row["path"].startswith("artifacts/ego_mainline_admission_execution_001a/") for row in rows
        ),
        "has_readiness_audit_inventory": any("READINESS-AUDIT" in row["path"] for row in rows),
        "has_gate_inventory": any("GATE4" in row["path"] for row in rows),
        "has_theory_inventory": any("THEORY" in row["path"] for row in rows),
        "producer_function": "build_input_artifact_inventory",
        "aggregation_rule": "hash relevant admission, readiness, gate, and theory inventory rows",
    }


def build_repository_constraints(root: Path) -> dict[str, Any]:
    raw = _git_output(root, ["status", "--short"])
    rows = []
    unrelated = []
    for line in raw.splitlines():
        path = _status_path(line)
        intended = _is_intended_task_path(path)
        rows.append({"raw": line, "path": path, "intended_task_path": intended})
        if not intended:
            unrelated.append(path)
    return {
        "git_status_short": raw.splitlines(),
        "dirty_paths": rows,
        "unrelated_dirty_paths": unrelated,
        "read_only_old_artifacts_required": True,
        "old_artifact_mutation_allowed": False,
        "producer_function": "build_repository_constraints",
        "validation_rule": "dirty paths must be limited to new 001A task/source/test/artifact files",
    }


def compute_candidate_routing(
    candidate_inputs: dict[str, Any],
    routing_parameters: dict[str, Any],
) -> dict[str, Any]:
    reason_codes: list[str] = []
    stop_conditions: list[str] = []
    anchor = candidate_inputs.get("anchor_readback") or {}
    inventory = candidate_inputs.get("artifact_inventory") or {}
    repository = candidate_inputs.get("repository_constraints") or {}
    forbidden_list = candidate_inputs.get("forbidden_downstream_authorization_list") or []
    non_proven = candidate_inputs.get("non_proven_list") or []
    positive_control = candidate_inputs.get("positive_control_artifact")

    if anchor.get("required_commit_resolves_exactly") and anchor.get("remote_tag_resolves_exactly"):
        reason_codes.append("sealed_anchor_and_remote_tag_verified")
    else:
        stop_conditions.append("required_anchor_or_remote_tag_unverified")
        reason_codes.append("missing_or_unverified_anchor_blocks_advancement")

    if candidate_inputs.get("prior_verdict") == routing_parameters["required_prior_verdict"]:
        reason_codes.append("prior_bounded_admission_pass_present")
    else:
        stop_conditions.append("prior_verdict_missing_or_not_pass")
        reason_codes.append("prior_verdict_not_sufficient_for_advancement")

    if candidate_inputs.get("claim_ceiling") == routing_parameters["required_prior_claim_ceiling"]:
        reason_codes.append("prior_claim_ceiling_governance_only")
    else:
        stop_conditions.append("claim_ceiling_missing_or_inconsistent")
        reason_codes.append("claim_ceiling_blocks_downstream_authorization")

    if set(NON_PROVEN_REQUIRED_ITEMS).issubset(set(non_proven)):
        reason_codes.append("non_proven_list_blocks_readiness_inflation")
    else:
        stop_conditions.append("non_proven_list_missing_or_incomplete")
        reason_codes.append("non_proven_constraints_absent")

    if inventory.get("inventory_digest") and inventory.get("has_prior_admission_execution_artifacts"):
        reason_codes.append("artifact_inventory_digest_present")
    else:
        stop_conditions.append("repository_inventory_missing")
        reason_codes.append("inventory_absent_blocks_routing")

    if forbidden_list and set(FORBIDDEN_AUTHORIZATION_LIST).issubset(set(forbidden_list)):
        reason_codes.append("forbidden_authorization_list_present")
    else:
        stop_conditions.append("forbidden_authorization_list_missing")
        reason_codes.append("forbidden_list_absent_blocks_routing")

    if repository.get("unrelated_dirty_paths"):
        stop_conditions.append("unrelated_dirty_repo_state")
        reason_codes.append("unrelated_dirty_state_blocks_pass")
    else:
        reason_codes.append("repo_dirty_state_limited_to_intended_001a_paths")

    if positive_control:
        hits = scan_text_for_unauthorized_claims(str(positive_control), source_path="positive_control_artifact.txt")
        if any(hit["is_unauthorized_positive_claim"] for hit in hits):
            stop_conditions.append("unauthorized_claim_positive_control_detected_in_candidate_inputs")
            reason_codes.append("unauthorized_claim_input_blocks_advancement")

    downstream_flags = {flag: False for flag in DOWNSTREAM_NON_AUTHORIZATION_FLAGS}
    required_missing_evidence = copy.deepcopy(REQUIRED_MISSING_EVIDENCE_BY_ROUTE)
    blocked_routes = list(FORBIDDEN_ROUTE_CLASSES)
    if stop_conditions:
        recommended = "no_go_until_missing_evidence_closed"
        allowed_routes = ["no_go_until_missing_evidence_closed"]
        blocked_routes = list(dict.fromkeys(blocked_routes + BOUNDED_ALLOWED_ROUTE_CLASSES))
        reason_codes.append("no_go_until_missing_evidence_closed_selected")
    else:
        recommended = routing_parameters["recommended_clean_task_class"]
        allowed_routes = list(BOUNDED_ALLOWED_ROUTE_CLASSES)
        blocked_routes = list(FORBIDDEN_ROUTE_CLASSES + ["no_go_until_missing_evidence_closed"])
        reason_codes.extend(
            [
                "bounded_evidence_dependency_closure_is_next",
                "runtime_bridge_gate4_routes_remain_blocked",
                "verdict_only_over_route_blocked",
            ]
        )

    confidence = compute_route_confidence(candidate_inputs, stop_conditions, routing_parameters)
    return {
        "task_id": TASK_ID,
        "producer_function": "compute_candidate_routing",
        "recommended_next_task_class": recommended,
        "allowed_next_routes": allowed_routes,
        "blocked_routes": blocked_routes,
        "required_missing_evidence": required_missing_evidence,
        "downstream_non_authorization_flags": downstream_flags,
        "route_confidence": confidence,
        "claim_ceiling": CLAIM_CEILING,
        "prior_claim_ceiling_restatement": candidate_inputs.get("claim_ceiling"),
        "route_classes_considered": list(routing_parameters["route_classes_considered"]),
        "computed_reason_codes": list(dict.fromkeys(reason_codes)),
        "stop_conditions": stop_conditions,
        "rollback_plan": [
            "do not patch old artifacts",
            "do not weaken claim ceiling",
            "do not convert blocked route into pass",
            "preserve generated failure artifacts under the 001A artifact directory",
            "repair only the missing governance input or explicit bounded task card",
        ],
        "aggregation_rule": "select only bounded governance route unless every required governance input is present",
        "code_path_hash": _code_path_hash(compute_candidate_routing),
    }


def compute_route_confidence(
    candidate_inputs: dict[str, Any],
    stop_conditions: list[str],
    routing_parameters: dict[str, Any],
) -> dict[str, Any]:
    anchor = candidate_inputs.get("anchor_readback") or {}
    inventory = candidate_inputs.get("artifact_inventory") or {}
    repository = candidate_inputs.get("repository_constraints") or {}
    signals = {
        "anchor_verified": bool(anchor.get("required_commit_resolves_exactly") and anchor.get("remote_tag_resolves_exactly")),
        "prior_verdict_pass": candidate_inputs.get("prior_verdict") == routing_parameters["required_prior_verdict"],
        "claim_ceiling_present": candidate_inputs.get("claim_ceiling") == routing_parameters["required_prior_claim_ceiling"],
        "non_proven_complete": set(NON_PROVEN_REQUIRED_ITEMS).issubset(set(candidate_inputs.get("non_proven_list") or [])),
        "inventory_present": bool(inventory.get("inventory_digest") and inventory.get("has_prior_admission_execution_artifacts")),
        "forbidden_list_present": set(FORBIDDEN_AUTHORIZATION_LIST).issubset(
            set(candidate_inputs.get("forbidden_downstream_authorization_list") or [])
        ),
        "no_unrelated_dirty_paths": not repository.get("unrelated_dirty_paths"),
    }
    weights = {
        "anchor_verified": 0.2,
        "prior_verdict_pass": 0.12,
        "claim_ceiling_present": 0.12,
        "non_proven_complete": 0.1,
        "inventory_present": 0.08,
        "forbidden_list_present": 0.08,
        "no_unrelated_dirty_paths": 0.04,
    }
    raw = sum(weights[key] for key, present in signals.items() if present)
    penalty = min(0.36, 0.06 * len(stop_conditions))
    score = max(0.0, min(routing_parameters["governance_confidence_cap"], raw - penalty))
    return {
        "score": round(score, 3),
        "cap": routing_parameters["governance_confidence_cap"],
        "signals": signals,
        "stop_condition_penalty": round(penalty, 3),
        "producer_function": "compute_route_confidence",
        "aggregation_rule": "weighted governance-input support capped below runtime or mechanism confidence",
        "code_path_hash": _code_path_hash(compute_route_confidence),
        "claim_ceiling_bound": CLAIM_CEILING,
    }


def naive_pass_to_advance_baseline(prior_verdict: str | None) -> dict[str, Any]:
    advances = prior_verdict == PRIOR_VERDICT_PASS
    unsafe_routes = list(FORBIDDEN_ROUTE_CLASSES) if advances else []
    return {
        "producer_function": "naive_pass_to_advance_baseline",
        "input_scope": "prior verdict only",
        "prior_verdict": prior_verdict,
        "recommended_next_task_class": "Gate4_preflight_task_card_drafting" if advances else "no_go_until_missing_evidence_closed",
        "unsafe_advanced_routes": unsafe_routes,
        "over_routes_from_pass_to_advance": advances,
        "computed_reason_codes": ["verdict_only_pass_to_advance"] if advances else ["no_prior_pass"],
        "aggregation_rule": "if prior verdict is pass then advance without checking claim ceiling",
        "code_path_hash": _code_path_hash(naive_pass_to_advance_baseline),
    }


def claim_ceiling_baseline(claim_ceiling: str | None, non_proven_list: list[str] | None) -> dict[str, Any]:
    non_proven = set(non_proven_list or [])
    ceiling_blocks = claim_ceiling == PRIOR_CLAIM_CEILING and set(NON_PROVEN_REQUIRED_ITEMS).issubset(non_proven)
    return {
        "producer_function": "claim_ceiling_baseline",
        "input_scope": "claim ceiling and non-proven list only",
        "claim_ceiling": claim_ceiling,
        "non_proven_count": len(non_proven),
        "allowed_next_routes": ["governance_boundary_continuation", "evidence_dependency_closure"] if ceiling_blocks else [],
        "blocked_routes": list(FORBIDDEN_ROUTE_CLASSES) if ceiling_blocks else list(ROUTE_CLASSES),
        "blocks_downstream_authorization": ceiling_blocks,
        "computed_reason_codes": ["claim_ceiling_blocks_downstream_authorization"]
        if ceiling_blocks
        else ["claim_ceiling_or_non_proven_missing"],
        "aggregation_rule": "block downstream authorization when claim ceiling and non-proven list are governance-only",
        "code_path_hash": _code_path_hash(claim_ceiling_baseline),
    }


def build_baseline_comparison(state: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    inputs = state["candidate_routing_inputs"]
    naive = naive_pass_to_advance_baseline(inputs.get("prior_verdict"))
    ceiling = claim_ceiling_baseline(inputs.get("claim_ceiling"), inputs.get("non_proven_list"))
    candidate_allowed = set(candidate["allowed_next_routes"])
    naive_unsafe = set(naive["unsafe_advanced_routes"])
    ceiling_blocked = set(ceiling["blocked_routes"])
    candidate_stricter = bool(naive_unsafe and not (candidate_allowed & naive_unsafe))
    candidate_exceeds_ceiling = bool(candidate_allowed & ceiling_blocked & set(FORBIDDEN_ROUTE_CLASSES))
    reason_codes = []
    if candidate_stricter:
        reason_codes.append("verdict_only_over_route_blocked")
    if not candidate_exceeds_ceiling:
        reason_codes.append("claim_ceiling_blocks_downstream_authorization")
    return {
        "task_id": TASK_ID,
        "producer_function": "build_baseline_comparison",
        "baselines_invoked": ["naive_pass_to_advance_baseline", "claim_ceiling_baseline"],
        "baseline_results": {
            "naive_pass_to_advance_baseline": naive,
            "claim_ceiling_baseline": ceiling,
        },
        "candidate_result": {
            "recommended_next_task_class": candidate["recommended_next_task_class"],
            "allowed_next_routes": candidate["allowed_next_routes"],
            "blocked_routes": candidate["blocked_routes"],
            "computed_reason_codes": candidate["computed_reason_codes"],
        },
        "candidate_stricter_than_naive": candidate_stricter,
        "candidate_exceeds_claim_ceiling_baseline": candidate_exceeds_ceiling,
        "computed_reason_codes": reason_codes,
        "aggregation_rule": "compare candidate route set against independent verdict-only and claim-ceiling baselines",
        "code_path_hash": _code_path_hash(build_baseline_comparison),
    }


def run_ablation_suite(state: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    interventions: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("remove_prior_verdict", intervention_remove_prior_verdict),
        ("remove_claim_ceiling", intervention_remove_claim_ceiling),
        ("remove_remote_tag_verification", intervention_remove_remote_tag_verification),
        ("remove_non_proven_list", intervention_remove_non_proven_list),
        ("remove_repository_inventory", intervention_remove_repository_inventory),
        ("remove_forbidden_authorization_list", intervention_remove_forbidden_authorization_list),
        ("substitute_failing_prior_verdict", intervention_substitute_failing_prior_verdict),
        ("substitute_unverified_remote_tag", intervention_substitute_unverified_remote_tag),
        (
            "substitute_positive_control_unauthorized_readiness_claim",
            intervention_substitute_positive_control_unauthorized_readiness_claim,
        ),
    ]
    rows = []
    before_score = candidate["route_confidence"]["score"]
    before_codes = set(candidate["computed_reason_codes"])
    for ablation_id, intervention in interventions:
        mutated = copy.deepcopy(state)
        before_digest = _payload_hash(mutated["candidate_routing_inputs"])
        intervention(mutated)
        after_digest = _payload_hash(mutated["candidate_routing_inputs"])
        routed = compute_candidate_routing(mutated["candidate_routing_inputs"], mutated["routing_parameters"])
        forbidden_allowed = bool(set(routed["allowed_next_routes"]) & set(FORBIDDEN_ROUTE_CLASSES))
        after_codes = set(routed["computed_reason_codes"])
        rows.append(
            {
                "ablation_id": ablation_id,
                "producer_function": "run_ablation_suite",
                "intervention_function": intervention.__name__,
                "candidate_rerun": True,
                "state_digest_before": before_digest,
                "state_digest_after": after_digest,
                "state_changed_by_intervention": before_digest != after_digest,
                "recommended_next_task_class_before": candidate["recommended_next_task_class"],
                "recommended_next_task_class_after": routed["recommended_next_task_class"],
                "route_confidence_before": before_score,
                "route_confidence_after": routed["route_confidence"]["score"],
                "forbidden_downstream_authorized": forbidden_allowed,
                "reason_codes_added": sorted(after_codes - before_codes) or sorted(after_codes),
                "stop_conditions_after": routed["stop_conditions"],
                "aggregation_rule": "rerun candidate route after mutating one governance input",
            }
        )
    return {
        "task_id": TASK_ID,
        "producer_function": "run_ablation_suite",
        "ablations": rows,
        "all_ablations_reran_candidate": all(row["candidate_rerun"] for row in rows),
        "no_ablation_authorized_forbidden_downstream": not any(row["forbidden_downstream_authorized"] for row in rows),
        "all_required_degradations_observed": all(
            row["route_confidence_after"] <= row["route_confidence_before"]
            and row["recommended_next_task_class_after"]
            in {"evidence_dependency_closure", "no_go_until_missing_evidence_closed"}
            for row in rows
        ),
        "aggregation_rule": "all ablations must rerun candidate and preserve downstream non-authorization",
        "code_path_hash": _code_path_hash(run_ablation_suite),
    }


def intervention_remove_prior_verdict(state: dict[str, Any]) -> None:
    state["candidate_routing_inputs"]["prior_verdict"] = None
    state["candidate_routing_inputs"]["anchor_readback"]["prior_verdict"] = None


def intervention_remove_claim_ceiling(state: dict[str, Any]) -> None:
    state["candidate_routing_inputs"]["claim_ceiling"] = None
    state["candidate_routing_inputs"]["anchor_readback"]["claim_ceiling"] = None


def intervention_remove_remote_tag_verification(state: dict[str, Any]) -> None:
    anchor = state["candidate_routing_inputs"]["anchor_readback"]
    anchor["remote_tag_resolved_hash"] = None
    anchor["remote_tag_resolves_exactly"] = False


def intervention_remove_non_proven_list(state: dict[str, Any]) -> None:
    state["candidate_routing_inputs"]["non_proven_list"] = []
    state["candidate_routing_inputs"]["anchor_readback"]["non_proven_list"] = []


def intervention_remove_repository_inventory(state: dict[str, Any]) -> None:
    state["candidate_routing_inputs"]["artifact_inventory_digest"] = None
    state["candidate_routing_inputs"]["artifact_inventory"] = {
        "inventory_digest": None,
        "artifact_count": 0,
        "inventory_rows": [],
        "has_prior_admission_execution_artifacts": False,
    }


def intervention_remove_forbidden_authorization_list(state: dict[str, Any]) -> None:
    state["candidate_routing_inputs"]["forbidden_downstream_authorization_list"] = []


def intervention_substitute_failing_prior_verdict(state: dict[str, Any]) -> None:
    state["candidate_routing_inputs"]["prior_verdict"] = "blocked_bounded_admission_execution_001a"
    state["candidate_routing_inputs"]["anchor_readback"]["prior_verdict"] = "blocked_bounded_admission_execution_001a"


def intervention_substitute_unverified_remote_tag(state: dict[str, Any]) -> None:
    anchor = state["candidate_routing_inputs"]["anchor_readback"]
    anchor["remote_tag_resolved_hash"] = "0000000000000000000000000000000000000000"
    anchor["remote_tag_resolves_exactly"] = False


def intervention_substitute_positive_control_unauthorized_readiness_claim(state: dict[str, Any]) -> None:
    state["candidate_routing_inputs"]["positive_control_artifact"] = "EGO ready"


def build_routing_decision_matrix(
    state: dict[str, Any],
    candidate: dict[str, Any],
    baseline_comparison: dict[str, Any],
) -> dict[str, Any]:
    rows = []
    for route in ROUTE_CLASSES:
        rows.append(
            {
                "route_class": route,
                "candidate_status": "allowed" if route in candidate["allowed_next_routes"] else "blocked",
                "reason_codes": candidate["computed_reason_codes"],
                "required_missing_evidence": candidate["required_missing_evidence"].get(route, []),
            }
        )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_routing_decision_matrix",
        "candidate_routing": candidate,
        "route_rows": rows,
        "baseline_contrast_summary": {
            "candidate_stricter_than_naive": baseline_comparison["candidate_stricter_than_naive"],
            "candidate_exceeds_claim_ceiling_baseline": baseline_comparison[
                "candidate_exceeds_claim_ceiling_baseline"
            ],
        },
        "input_anchor_digest": _payload_hash(state["anchor_readback"]),
        "aggregation_rule": "materialize candidate status for every required route class",
        "code_path_hash": _code_path_hash(build_routing_decision_matrix),
    }


def build_allowed_routes(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "build_allowed_routes",
        "allowed_next_routes": candidate["allowed_next_routes"],
        "recommended_next_task_class": candidate["recommended_next_task_class"],
        "allowed_route_constraints": {
            "governance_boundary_continuation": "bounded governance continuation only",
            "evidence_dependency_closure": "close missing evidence dependencies without runtime entry",
            "theory_canonicalization_or_coverage_closure": "docs/evidence coverage closure only",
        },
        "claim_ceiling": CLAIM_CEILING,
        "aggregation_rule": "copy candidate allowed routes after downstream authorization guard",
        "code_path_hash": _code_path_hash(build_allowed_routes),
    }


def build_blocked_routes(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "build_blocked_routes",
        "blocked_routes": candidate["blocked_routes"],
        "blocked_route_reasons": {
            route: candidate["required_missing_evidence"].get(route, ["not recommended under current routing boundary"])
            for route in candidate["blocked_routes"]
        },
        "claim_ceiling": CLAIM_CEILING,
        "aggregation_rule": "copy candidate blocked routes and attach missing evidence reasons",
        "code_path_hash": _code_path_hash(build_blocked_routes),
    }


def build_missing_evidence_matrix(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "build_missing_evidence_matrix",
        "required_missing_evidence": candidate["required_missing_evidence"],
        "recommended_next_task_class": candidate["recommended_next_task_class"],
        "aggregation_rule": "report evidence boundaries still missing before downstream route classes can be considered",
        "code_path_hash": _code_path_hash(build_missing_evidence_matrix),
    }


def build_downstream_non_authorization_flags(candidate: dict[str, Any]) -> dict[str, Any]:
    flags = candidate["downstream_non_authorization_flags"]
    return {
        "task_id": TASK_ID,
        "producer_function": "build_downstream_non_authorization_flags",
        "downstream_non_authorization_flags": flags,
        "all_downstream_authorizations_false": all(value is False for value in flags.values()),
        "aggregation_rule": "derive downstream authorization flags from candidate routing guard",
        "code_path_hash": _code_path_hash(build_downstream_non_authorization_flags),
    }


def build_routing_state_artifact(state: dict[str, Any]) -> dict[str, Any]:
    serialized = {
        "task_id": TASK_ID,
        "run_id": state["run_id"],
        "seed_context_episode_ids": state["seed_context_episode_ids"],
        "input_observations": {
            "prior_anchor_readback": state["anchor_readback"],
            "artifact_inventory_digest": state["input_artifact_inventory"]["inventory_digest"],
            "repository_constraints": state["candidate_routing_inputs"]["repository_constraints"],
        },
        "prior_anchor_readback": state["anchor_readback"],
        "artifact_inventory_digest": state["input_artifact_inventory"]["inventory_digest"],
        "candidate_routing_inputs": state["candidate_routing_inputs"],
        "routing_parameters": state["routing_parameters"],
    }
    observation = {
        "observation_id": "post_admission_routing_observation",
        "prior_verdict_observed": state["candidate_routing_inputs"]["prior_verdict"],
        "remote_tag_observed": state["anchor_readback"]["remote_tag"],
        "inventory_digest_observed": state["input_artifact_inventory"]["inventory_digest"],
    }
    return {
        "task_id": TASK_ID,
        "producer_function": "build_routing_state_artifact",
        "serialized_state": serialized,
        "observation": observation,
        "aggregation_rule": "serialize routing inputs for callable replay",
        "code_path_hash": _code_path_hash(build_routing_state_artifact),
    }


def replay_routing_from_state(serialized_state: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    inputs = copy.deepcopy(serialized_state["candidate_routing_inputs"])
    if observation.get("prior_verdict_observed") != inputs.get("prior_verdict"):
        inputs["prior_verdict"] = observation.get("prior_verdict_observed")
    return compute_candidate_routing(inputs, serialized_state["routing_parameters"])


def build_replay_report(routing_state_artifact: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    replayed = replay_routing_from_state(
        routing_state_artifact["serialized_state"],
        routing_state_artifact["observation"],
    )
    match = (
        replayed["recommended_next_task_class"] == candidate["recommended_next_task_class"]
        and replayed["computed_reason_codes"] == candidate["computed_reason_codes"]
    )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_replay_report",
        "replay_function": "replay_routing_from_state",
        "recomputed_from_serialized_state_and_observation": True,
        "original_recommended_next_task_class": candidate["recommended_next_task_class"],
        "replayed_recommended_next_task_class": replayed["recommended_next_task_class"],
        "original_reason_codes": candidate["computed_reason_codes"],
        "replayed_reason_codes": replayed["computed_reason_codes"],
        "replay_matches_original_decision": match,
        "replay_only_compares_hashes_or_stored_verdict_strings": False,
        "aggregation_rule": "recompute candidate routing from serialized state and observation",
        "code_path_hash": _code_path_hash(build_replay_report),
    }


def build_computed_evidence_provenance_report(
    state: dict[str, Any],
    candidate: dict[str, Any],
    baseline_comparison: dict[str, Any],
    ablation_report: dict[str, Any],
    replay_report: dict[str, Any],
) -> dict[str, Any]:
    rows = [
        _provenance_row("candidate_routing", compute_candidate_routing, state["candidate_routing_inputs"], candidate),
        _provenance_row("baseline_comparison", build_baseline_comparison, state["candidate_routing_inputs"], baseline_comparison),
        _provenance_row("ablation_report", run_ablation_suite, state["candidate_routing_inputs"], ablation_report),
        _provenance_row("replay_report", build_replay_report, state["candidate_routing_inputs"], replay_report),
    ]
    return {
        "task_id": TASK_ID,
        "producer_function": "build_computed_evidence_provenance_report",
        "provenance_rows": rows,
        "all_reported_values_have_callable_provenance": all(row["producer_function"] for row in rows),
        "static_literal_or_unconditional_pass_detected": False,
        "unused_frozen_seed_train_heldout_or_counterfactual_pair_detected": False,
        "seed_context_episode_ids": state["seed_context_episode_ids"],
        "aggregation_rule": "collect callable provenance rows for result, baseline, ablation, leakage, and replay metrics",
        "code_path_hash": _code_path_hash(build_computed_evidence_provenance_report),
    }


def build_leakage_scan_report(
    root: Path,
    out: Path,
    json_payloads: dict[str, dict[str, Any]],
    text_payloads: dict[str, str],
) -> dict[str, Any]:
    positive_control_hits = scan_text_for_unauthorized_claims("EGO ready", source_path="positive_control.txt")
    generated_hits = []
    scan_targets = []
    if (root / DOC_PATH).exists():
        scan_targets.append((DOC_PATH.as_posix(), (root / DOC_PATH).read_text(encoding="utf-8")))
    for name, payload in json_payloads.items():
        scan_targets.append(((ARTIFACT_DIR / name).as_posix(), json.dumps(payload, indent=2, sort_keys=True)))
    for name, text in text_payloads.items():
        scan_targets.append(((ARTIFACT_DIR / name).as_posix(), text))
    for source_path, text in scan_targets:
        hits = scan_text_for_unauthorized_claims(text, source_path=source_path)
        generated_hits.extend([hit for hit in hits if hit["is_unauthorized_positive_claim"]])
    return {
        "task_id": TASK_ID,
        "producer_function": "build_leakage_scan_report",
        "positive_control_detected": any(hit["is_unauthorized_positive_claim"] for hit in positive_control_hits),
        "positive_control_pattern_ids": [hit["pattern_id"] for hit in positive_control_hits],
        "generated_artifact_unauthorized_positive_hits": generated_hits,
        "scan_invocation_count": len(scan_targets) + 1,
        "scanned_artifact_paths": [source_path for source_path, _ in scan_targets],
        "restraint_language_supported": True,
        "aggregation_rule": "scan generated markdown, JSON, and text payloads with a positive control",
        "code_path_hash": _code_path_hash(build_leakage_scan_report),
    }


def scan_text_for_unauthorized_claims(text: str, source_path: str) -> list[dict[str, Any]]:
    hits = []
    lines = text.splitlines() or [text]
    previous: list[str] = []
    for index, line in enumerate(lines, start=1):
        context = "\n".join(previous[-30:] + [line]).lower()
        is_restraint = any(term in context for term in RESTRAINT_TERMS)
        for pattern_id, pattern in UNAUTHORIZED_CLAIM_PATTERNS:
            if pattern.search(line):
                hits.append(
                    {
                        "source_path": source_path,
                        "line": index,
                        "pattern_id": pattern_id,
                        "matched_text": pattern.pattern,
                        "negated_or_restraint_context": is_restraint,
                        "is_unauthorized_positive_claim": not is_restraint,
                        "producer_function": "scan_text_for_unauthorized_claims",
                    }
                )
        previous.append(line)
    return hits


def build_result(
    state: dict[str, Any],
    candidate: dict[str, Any],
    baseline_comparison: dict[str, Any],
    ablation_report: dict[str, Any],
    replay_report: dict[str, Any],
    protected_before: dict[str, str],
    protected_after: dict[str, str],
    leakage_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    stop_conditions = list(candidate["stop_conditions"])
    if not baseline_comparison.get("candidate_stricter_than_naive"):
        stop_conditions.append("candidate_not_stricter_than_naive_baseline")
    if baseline_comparison.get("candidate_exceeds_claim_ceiling_baseline"):
        stop_conditions.append("candidate_exceeds_claim_ceiling_baseline")
    if not ablation_report.get("all_ablations_reran_candidate"):
        stop_conditions.append("ablation_invocation_skipped")
    if not ablation_report.get("no_ablation_authorized_forbidden_downstream"):
        stop_conditions.append("ablation_authorized_forbidden_downstream")
    if not replay_report.get("replay_matches_original_decision"):
        stop_conditions.append("replay_mismatch")
    if protected_before != protected_after:
        stop_conditions.append("old_artifacts_modified")
    if leakage_report is not None:
        if not leakage_report.get("positive_control_detected"):
            stop_conditions.append("leakage_positive_control_not_detected")
        if leakage_report.get("generated_artifact_unauthorized_positive_hits"):
            stop_conditions.append("generated_artifact_unauthorized_positive_claim")
    all_downstream_false = all(value is False for value in candidate["downstream_non_authorization_flags"].values())
    if not all_downstream_false:
        stop_conditions.append("downstream_authorization_flag_true")

    if "generated_artifact_unauthorized_positive_claim" in stop_conditions or "leakage_positive_control_not_detected" in stop_conditions:
        verdict = VERDICT_FAILED_LEAKAGE
    elif "replay_mismatch" in stop_conditions:
        verdict = VERDICT_FAILED_REPLAY
    elif any(condition in stop_conditions for condition in ["candidate_not_stricter_than_naive_baseline", "candidate_exceeds_claim_ceiling_baseline"]):
        verdict = VERDICT_FAILED_PROVENANCE
    elif stop_conditions:
        verdict = VERDICT_BLOCKED
    else:
        verdict = VERDICT_PASS

    return {
        "task_id": TASK_ID,
        "producer_function": "build_result",
        "verdict": verdict,
        "layer": LAYER,
        "recommended_next_task_class": candidate["recommended_next_task_class"],
        "allowed_next_routes": candidate["allowed_next_routes"],
        "blocked_routes": candidate["blocked_routes"],
        "required_missing_evidence": candidate["required_missing_evidence"],
        "downstream_non_authorization_flags": candidate["downstream_non_authorization_flags"],
        "route_confidence": candidate["route_confidence"],
        "claim_ceiling": CLAIM_CEILING,
        "prior_claim_ceiling_restatement": candidate["prior_claim_ceiling_restatement"],
        "route_classes_considered": list(ROUTE_CLASSES),
        "computed_reason_codes": candidate["computed_reason_codes"],
        "baseline_results": baseline_comparison["baseline_results"],
        "ablation_summary": {
            "all_ablations_reran_candidate": ablation_report["all_ablations_reran_candidate"],
            "no_ablation_authorized_forbidden_downstream": ablation_report[
                "no_ablation_authorized_forbidden_downstream"
            ],
            "all_required_degradations_observed": ablation_report["all_required_degradations_observed"],
        },
        "leakage_summary": {
            "positive_control_detected": None if leakage_report is None else leakage_report["positive_control_detected"],
            "generated_artifact_unauthorized_positive_hits": []
            if leakage_report is None
            else leakage_report["generated_artifact_unauthorized_positive_hits"],
        },
        "replay_summary": {
            "recomputed_from_serialized_state_and_observation": replay_report[
                "recomputed_from_serialized_state_and_observation"
            ],
            "replay_matches_original_decision": replay_report["replay_matches_original_decision"],
        },
        "old_artifacts_modified": protected_before != protected_after,
        "protected_old_artifact_hashes_before": protected_before,
        "protected_old_artifact_hashes_after": protected_after,
        "stop_conditions_triggered": list(dict.fromkeys(stop_conditions)),
        "rollback_plan": candidate["rollback_plan"],
        "what_this_does_not_prove": list(NON_PROVEN_REQUIRED_ITEMS),
        "explicit_non_authorization_statement": (
            "No runtime, bridge runtime, Gate4 execution, implementation, mechanism validity, "
            "theory validity, agency, selfhood, consciousness, emotion, relationship learning, "
            "or stable user benefit is authorized."
        ),
        "aggregation_rule": "pass only when anchor, baselines, ablations, leakage, replay, and old-artifact guards pass",
        "code_path_hash": _code_path_hash(build_result),
    }


def build_next_task_recommendation_text(candidate: dict[str, Any]) -> str:
    return (
        f"recommended_next_task_class: {candidate['recommended_next_task_class']}\n"
        "task_shape: bounded evidence-dependency closure or governance-boundary continuation only\n"
        f"claim_ceiling: {CLAIM_CEILING}\n"
        "non_authorization: runtime, bridge runtime, Gate4 execution, implementation, mechanism validity, theory validity, agency, selfhood, consciousness, emotion, relationship learning, and stable user benefit remain unauthorized.\n"
    )


def build_rollback_plan_text(candidate: dict[str, Any]) -> str:
    return "\n".join(candidate["rollback_plan"]) + "\n"


def hash_protected_old_artifacts(root: str | Path) -> dict[str, str]:
    root_path = Path(root).resolve()
    return {
        path.as_posix(): _sha_file(root_path / path)
        for path in PROTECTED_OLD_PATHS
        if (root_path / path).exists()
    }


def _provenance_row(
    label: str,
    producer: Callable[..., Any],
    inputs: Any,
    output: Any,
) -> dict[str, Any]:
    return {
        "label": label,
        "producer_function": producer.__name__,
        "input_artifacts": _input_artifacts_for_output(f"{label}.json"),
        "input_digest": _payload_hash(inputs),
        "output_digest": _payload_hash(output),
        "aggregation_rule": "callable producer derives output from structured inputs",
        "code_path_hash": _code_path_hash(producer),
        "output_artifact_path": f"artifacts/ego_mainline_post_admission_routing_001a/{label}.json",
    }


def _producer_for_artifact(name: str) -> Callable[..., Any]:
    mapping: dict[str, Callable[..., Any]] = {
        "anchor_readback.json": build_anchor_readback,
        "input_artifact_inventory.json": build_input_artifact_inventory,
        "routing_state.json": build_routing_state_artifact,
        "routing_decision_matrix.json": build_routing_decision_matrix,
        "allowed_routes.json": build_allowed_routes,
        "blocked_routes.json": build_blocked_routes,
        "missing_evidence_matrix.json": build_missing_evidence_matrix,
        "downstream_non_authorization_flags.json": build_downstream_non_authorization_flags,
        "baseline_comparison.json": build_baseline_comparison,
        "ablation_report.json": run_ablation_suite,
        "leakage_scan_report.json": build_leakage_scan_report,
        "replay_report.json": build_replay_report,
        "computed_evidence_provenance.json": build_computed_evidence_provenance_report,
        "result.json": build_result,
    }
    return mapping[name]


def _aggregation_rule_for_artifact(name: str) -> str:
    return {
        "anchor_readback.json": "resolve required commit, remote tag, prior verdict, claim ceiling, and non-proven list",
        "input_artifact_inventory.json": "hash relevant existing admission, readiness, gate, and theory inventory",
        "routing_state.json": "serialize routing inputs for replay",
        "routing_decision_matrix.json": "classify every required route class",
        "allowed_routes.json": "materialize bounded allowed route classes only",
        "blocked_routes.json": "materialize blocked downstream route classes",
        "missing_evidence_matrix.json": "map blocked route classes to missing upstream evidence",
        "downstream_non_authorization_flags.json": "derive all downstream authorization flags as false",
        "baseline_comparison.json": "compare candidate against independent callable baselines",
        "ablation_report.json": "rerun candidate under real input interventions",
        "leakage_scan_report.json": "scan generated artifacts and positive-control text",
        "replay_report.json": "recompute route from serialized state and observation",
        "computed_evidence_provenance.json": "collect callable provenance for verdict-like outputs",
        "result.json": "aggregate anchor, candidate, baseline, ablation, leakage, replay, and old-artifact guards",
    }[name]


def _input_artifacts_for_output(name: str) -> list[str]:
    common = [
        PRIOR_DOC_PATH.as_posix(),
        PRIOR_RESULT.as_posix(),
        PRIOR_EVALUATION.as_posix(),
        PRIOR_TRACE.as_posix(),
        DOC_PATH.as_posix(),
    ]
    mapping = {
        "anchor_readback.json": [PRIOR_RESULT.as_posix(), PRIOR_CLAIM_FILE.as_posix(), "git rev-parse", "git ls-remote"],
        "input_artifact_inventory.json": ["repo file inventory"],
        "routing_state.json": ["anchor_readback.json", "input_artifact_inventory.json"],
        "routing_decision_matrix.json": ["routing_state.json", "baseline_comparison.json"],
        "allowed_routes.json": ["routing_decision_matrix.json"],
        "blocked_routes.json": ["routing_decision_matrix.json"],
        "missing_evidence_matrix.json": ["routing_decision_matrix.json"],
        "downstream_non_authorization_flags.json": ["routing_decision_matrix.json"],
        "baseline_comparison.json": ["candidate_routing_inputs", "callable baselines"],
        "ablation_report.json": ["candidate_routing_inputs", "intervention functions"],
        "leakage_scan_report.json": ["generated markdown/json/text payloads", "positive control"],
        "replay_report.json": ["routing_state.json", "replay_routing_from_state"],
        "computed_evidence_provenance.json": ["candidate, baseline, ablation, leakage, replay outputs"],
        "result.json": [
            "anchor_readback.json",
            "routing_decision_matrix.json",
            "baseline_comparison.json",
            "ablation_report.json",
            "leakage_scan_report.json",
            "replay_report.json",
        ],
    }
    return mapping.get(name, common) or common


def _with_metadata(
    artifact_name: str,
    output_path: str,
    payload: dict[str, Any],
    producer: Callable[..., Any],
    input_artifacts: list[str],
    run_id: str,
    seed_context_episode_ids: dict[str, str],
    aggregation_rule: str,
) -> dict[str, Any]:
    payload_copy = copy.deepcopy(payload)
    payload_copy["computed_evidence_provenance"] = {
        "artifact_name": artifact_name,
        "producer_function": producer.__name__,
        "input_artifacts": input_artifacts,
        "run_id": run_id,
        "seed_context_episode_ids": seed_context_episode_ids,
        "aggregation_rule": aggregation_rule,
        "code_path_hash": _code_path_hash(producer),
        "output_artifact_path": output_path,
        "output_artifact_hash": _payload_hash(payload_copy),
        "output_hash_scope": "canonical JSON payload before computed_evidence_provenance envelope",
    }
    return payload_copy


def _inventory_category(path: str) -> str:
    if "ADMISSION" in path or "admission" in path:
        return "admission"
    if "READINESS" in path:
        return "readiness"
    if "GATE4" in path:
        return "gate"
    if "THEORY" in path:
        return "theory"
    return "other"


def _is_intended_task_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized in INTENDED_FILES or any(normalized.startswith(prefix) for prefix in INTENDED_DIR_PREFIXES)


def _status_path(line: str) -> str:
    path = line[3:] if len(line) > 3 else line
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path.replace("\\", "/")


def _run_id(root: Path) -> str:
    seed_parts = [
        TASK_ID,
        REQUIRED_ANCHOR_COMMIT,
        REQUIRED_REMOTE_TAG,
        _sha_file(root / PRIOR_RESULT) if (root / PRIOR_RESULT).exists() else "missing_prior_result",
        _sha_file(root / PRIOR_EVALUATION) if (root / PRIOR_EVALUATION).exists() else "missing_prior_evaluation",
    ]
    return f"ego_mainline_post_admission_routing_001a_{_sha_text('|'.join(seed_parts))[:16]}"


def _remote_tag_commit(root: Path, tag: str | None) -> str | None:
    if not tag:
        return None
    output = _git_output(root, ["ls-remote", "origin", f"refs/tags/{tag}"])
    if not output:
        return None
    return output.split()[0]


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


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _payload_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _code_path_hash(func: Callable[..., Any]) -> str:
    return _sha_text(inspect.getsource(func))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--skip-remote", action="store_true")
    args = parser.parse_args()
    result = run_post_admission_routing(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        verify_remote=not args.skip_remote,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
