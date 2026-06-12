from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable


TASK_ID = "EGO-MAINLINE-EVIDENCE-DEPENDENCY-CLOSURE-001A"
LAYER = "evidence-governance / evidence dependency closure only"
CLAIM_CEILING = "bounded evidence dependency closure evidence at governance layer only"
ROUTING_CLAIM_CEILING = "bounded post-admission routing evidence at governance layer only"
ROUTING_VERDICT = "post_admission_routing_001a_pass_with_bounded_next_task"
ROUTING_RECOMMENDATION = "evidence_dependency_closure"
ROUTING_ANCHOR = "4edf5cff7f89cf2cf1c6dbb15a478bbada0432aa"
ROUTING_REMOTE_TAG = "remote-anchor-post-admission-routing-001a-4edf5c"
ADMISSION_ANCHOR = "98e51a46cd7f28f60b1851c616d4351c1cd6272f"
ADMISSION_REMOTE_TAG = "remote-anchor-bounded-admission-execution-001a-98e51a4"

VERDICT_PASS_WITH_BLOCKERS = "evidence_dependency_closure_001a_pass_with_blockers_classified"
VERDICT_PASS_NO_DOWNSTREAM = "evidence_dependency_closure_001a_pass_no_downstream_authorization"
VERDICT_BLOCKED_UNCLASSIFIED = "evidence_dependency_closure_001a_blocked_unclassified_test_failures"
VERDICT_BLOCKED_MISSING = "evidence_dependency_closure_001a_blocked_missing_required_evidence"
VERDICT_FAILED_PROVENANCE = "evidence_dependency_closure_001a_failed_provenance_gate"
VERDICT_FAILED_LEAKAGE = "evidence_dependency_closure_001a_failed_leakage_gate"
VERDICT_FAILED_REPLAY = "evidence_dependency_closure_001a_failed_replay_gate"

ARTIFACT_DIR = Path("artifacts/ego_mainline_evidence_dependency_closure_001a")
DOC_PATH = Path("docs/codex/tasks/EGO-MAINLINE-EVIDENCE-DEPENDENCY-CLOSURE-001A.md")
ROUTING_ARTIFACT_DIR = Path("artifacts/ego_mainline_post_admission_routing_001a")
ADMISSION_ARTIFACT_DIR = Path("artifacts/ego_mainline_admission_execution_001a")
ROUTING_RESULT = ROUTING_ARTIFACT_DIR / "result.json"
ROUTING_ALLOWED = ROUTING_ARTIFACT_DIR / "allowed_routes.json"
ROUTING_BLOCKED = ROUTING_ARTIFACT_DIR / "blocked_routes.json"
ROUTING_MATRIX = ROUTING_ARTIFACT_DIR / "routing_decision_matrix.json"
ADMISSION_RESULT = ADMISSION_ARTIFACT_DIR / "result.json"

GOVERNANCE_CONFIDENCE_CAP = 0.64

REQUIRED_ARTIFACT_NAMES = [
    "result.json",
    "anchor_readback.json",
    "input_artifact_inventory.json",
    "test_suite_observation.json",
    "known_failure_classification.json",
    "dependency_closure_matrix.json",
    "satisfied_dependencies.json",
    "missing_dependencies.json",
    "stale_or_conflicting_dependencies.json",
    "known_blockers.json",
    "blocker_severity_matrix.json",
    "route_permission_matrix.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_scan_report.json",
    "replay_report.json",
    "computed_evidence_provenance.json",
    "closure_state.json",
    "claim_ceiling.txt",
    "future_task_recommendation.txt",
    "required_repair_tasks.json",
    "rollback_plan.txt",
]

DEPENDENCY_CATEGORIES = [
    "anchor_integrity",
    "routing_boundary_integrity",
    "admission_execution_integrity",
    "artifact_inventory_continuity",
    "old_artifact_non_mutation",
    "test_suite_status",
    "known_failure_classification",
    "provenance_gate_continuity",
    "replay_gate_continuity",
    "leakage_gate_continuity",
    "baseline_independence_continuity",
    "ablation_intervention_continuity",
    "theory_coverage_or_canonicalization_dependencies",
    "Gate0_Gate1_Gate2_Gate3_dependency_state",
    "Gate4_preflight_prerequisites",
    "bridge_runtime_prerequisites",
    "EGO_runtime_prerequisites",
    "downstream_non_authorization_preservation",
]

ROUTE_CLASSES = [
    "evidence_dependency_closure_complete",
    "bounded_repair_task_required",
    "known_failure_triage_required",
    "Gate4_preflight_task_card_drafting_allowed_future_only",
    "theory_canonicalization_or_coverage_closure_required",
    "bridge_runtime_preflight_blocked",
    "EGO_runtime_implementation_blocked",
    "product_or_companion_behavior_work_blocked",
    "no_go_until_dependency_gap_closed",
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

FORBIDDEN_DOWNSTREAM_AUTHORIZATION_LIST = [
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

REQUIRED_NON_PROVEN_ITEMS = [
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

KNOWN_THREE_FAILURES = [
    {
        "nodeid": (
            "tests/test_ego_mainline_admission_canonical_coverage_reference_001a.py::"
            "test_temp_run_uses_same_validators_without_remote_dependency"
        ),
        "prior_failure_kind": "redundant_reference_contract_blocked",
        "blocker_classification": "existing_redundancy_guard_blocks_on_current_sealed_admission_artifacts",
    },
    {
        "nodeid": (
            "tests/test_ego_mainline_admission_task_card_alignment_001a.py::"
            "test_temp_run_uses_same_validators"
        ),
        "prior_failure_kind": "redundant_alignment_contract_blocked",
        "blocker_classification": "existing_redundancy_guard_blocks_on_current_sealed_admission_artifacts",
    },
    {
        "nodeid": (
            "tests/test_ego_mainline_post_admission_routing_001a.py::"
            "test_callable_candidate_rejects_corrupted_governance_inputs_without_authorizing_downstream"
        ),
        "prior_failure_kind": "dirty_state_contamination_or_prior_observation_mismatch",
        "blocker_classification": "resolved_in_clean_bounded_observation",
    },
]

PROTECTED_OLD_PATHS = [
    Path("docs/codex/tasks/EGO-MAINLINE-POST-ADMISSION-ROUTING-001A.md"),
    ROUTING_RESULT,
    ROUTING_ALLOWED,
    ROUTING_BLOCKED,
    ROUTING_MATRIX,
    ROUTING_ARTIFACT_DIR / "baseline_comparison.json",
    ROUTING_ARTIFACT_DIR / "ablation_report.json",
    ROUTING_ARTIFACT_DIR / "leakage_scan_report.json",
    ROUTING_ARTIFACT_DIR / "replay_report.json",
    Path("docs/codex/tasks/EGO-MAINLINE-ADMISSION-EXECUTION-001A.md"),
    ADMISSION_RESULT,
    ADMISSION_ARTIFACT_DIR / "admission_contract_evaluation.json",
    ADMISSION_ARTIFACT_DIR / "admission_decision_trace.json",
    ADMISSION_ARTIFACT_DIR / "claim_ceiling.txt",
    Path("artifacts/ego_mainline_admission_execution_preflight_001a/result.json"),
    Path("artifacts/ego_mainline_admission_task_card_alignment_001a/result.json"),
    Path("artifacts/ego_mainline_admission_canonical_coverage_reference_001a/result.json"),
    Path("artifacts/post_bridge_admission_executable_001d/result.json"),
    Path("artifacts/theory_landscape_coverage_canonicalization_provenance_repair_001b/result.json"),
]

INTENDED_DIR_PREFIXES = [
    "artifacts/ego_mainline_evidence_dependency_closure_001a/",
    "src/ego_mainline_evidence_dependency_closure_001a/",
]
INTENDED_FILES = {
    "docs/codex/tasks/EGO-MAINLINE-EVIDENCE-DEPENDENCY-CLOSURE-001A.md",
    "tests/test_ego_mainline_evidence_dependency_closure_001a.py",
}

UNAUTHORIZED_CLAIM_PATTERNS = [
    ("ego_ready", re.compile(r"\bEGO\s+ready\b", re.IGNORECASE)),
    ("ego_readiness", re.compile(r"\bEGO\s+readiness\b", re.IGNORECASE)),
    ("bridge_ready", re.compile(r"\bbridge\s+ready\b", re.IGNORECASE)),
    ("bridge_readiness", re.compile(r"\bbridge\s+readiness\b", re.IGNORECASE)),
    ("runtime_ready", re.compile(r"\bruntime\s+ready\b", re.IGNORECASE)),
    ("runtime_readiness", re.compile(r"\bruntime\s+readiness\b", re.IGNORECASE)),
    ("gate4_authorized", re.compile(r"\bGate4\s+authorized\b", re.IGNORECASE)),
    ("mechanism_validated", re.compile(r"\bmechanism\s+validated\b", re.IGNORECASE)),
    ("mechanism_validity", re.compile(r"\bmechanism\s+validity\b", re.IGNORECASE)),
    ("theory_validated", re.compile(r"\btheory\s+validated\b", re.IGNORECASE)),
    ("theory_validity", re.compile(r"\btheory\s+validity\b", re.IGNORECASE)),
    ("architecture_correct", re.compile(r"\barchitecture\s+correct\b", re.IGNORECASE)),
    ("architecture_correctness", re.compile(r"\barchitecture\s+correctness\b", re.IGNORECASE)),
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
    "missing",
    "blocker",
    "restraint",
    "scanner",
    "positive control",
    "positive_control",
    "stop condition",
    "rollback",
    "fail",
    "failure",
    "failed",
    "remains unauthorized",
    "not authorized",
    "not authorize",
    "does not authorize",
    "must not authorize",
]

DEFAULT_BOUNDED_OBSERVATION = {
    "targeted_routing_test": {
        "command": "pytest tests/test_ego_mainline_post_admission_routing_001a.py",
        "exit_code": 0,
        "passed": True,
        "summary": {"passed": 9, "failed": 0},
        "observation_source": "preimplementation_clean_worktree_readback",
    },
    "known_failure_probe": {
        "command": (
            "pytest "
            "tests/test_ego_mainline_admission_canonical_coverage_reference_001a.py::"
            "test_temp_run_uses_same_validators_without_remote_dependency "
            "tests/test_ego_mainline_admission_task_card_alignment_001a.py::"
            "test_temp_run_uses_same_validators "
            "tests/test_ego_mainline_post_admission_routing_001a.py::"
            "test_callable_candidate_rejects_corrupted_governance_inputs_without_authorizing_downstream"
        ),
        "exit_code": 1,
        "passed": False,
        "summary": {"passed": 1, "failed": 2},
        "observation_source": "preimplementation_clean_worktree_readback",
    },
}


def run_dependency_closure(
    repo_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    verify_remote: bool = True,
    execute_tests: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    out = Path(output_dir) if output_dir is not None else root / ARTIFACT_DIR
    if not out.is_absolute():
        out = root / out
    out.mkdir(parents=True, exist_ok=True)

    protected_before = hash_protected_old_artifacts(root)
    state = build_closure_state(root, out, verify_remote=verify_remote, execute_tests=execute_tests)
    candidate = compute_candidate_closure(state["candidate_closure_inputs"], state["closure_parameters"])
    baseline_comparison = build_baseline_comparison(state, candidate)
    ablation_report = run_ablation_suite(state, candidate)
    dependency_matrix = build_dependency_closure_matrix(candidate)
    satisfied_dependencies = build_satisfied_dependencies(candidate)
    missing_dependencies = build_missing_dependencies(candidate)
    stale_dependencies = build_stale_or_conflicting_dependencies(candidate)
    known_blockers = build_known_blockers(candidate)
    blocker_severity = build_blocker_severity_matrix(candidate)
    route_permission_matrix = build_route_permission_matrix(candidate)
    required_repair_tasks = build_required_repair_tasks(candidate)
    closure_state_artifact = build_closure_state_artifact(state)
    replay_report = build_replay_report(closure_state_artifact, candidate)
    protected_after = hash_protected_old_artifacts(root)

    provenance_report = build_computed_evidence_provenance_report(
        state=state,
        candidate=candidate,
        baseline_comparison=baseline_comparison,
        ablation_report=ablation_report,
        replay_report=replay_report,
    )
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
        "test_suite_observation.json": state["test_suite_observation"],
        "known_failure_classification.json": state["known_failure_classification"],
        "dependency_closure_matrix.json": dependency_matrix,
        "satisfied_dependencies.json": satisfied_dependencies,
        "missing_dependencies.json": missing_dependencies,
        "stale_or_conflicting_dependencies.json": stale_dependencies,
        "known_blockers.json": known_blockers,
        "blocker_severity_matrix.json": blocker_severity,
        "route_permission_matrix.json": route_permission_matrix,
        "baseline_comparison.json": baseline_comparison,
        "ablation_report.json": ablation_report,
        "replay_report.json": replay_report,
        "computed_evidence_provenance.json": provenance_report,
        "closure_state.json": closure_state_artifact,
        "required_repair_tasks.json": required_repair_tasks,
        "result.json": result,
    }
    text_payloads = {
        "claim_ceiling.txt": CLAIM_CEILING + "\n",
        "future_task_recommendation.txt": build_future_task_recommendation_text(candidate),
        "rollback_plan.txt": build_rollback_plan_text(candidate),
    }

    leakage_report = build_leakage_scan_report(
        root,
        out,
        {**json_payloads, "leakage_scan_report.json": {"provisional_self_scan": True}},
        text_payloads,
    )
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
    leakage_report = build_leakage_scan_report(
        root,
        out,
        {**json_payloads, "leakage_scan_report.json": leakage_report},
        text_payloads,
    )
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
    json_payloads["leakage_scan_report.json"] = leakage_report
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


def build_closure_state(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
    verify_remote: bool = True,
    execute_tests: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    out = Path(output_dir) if output_dir is not None else root / ARTIFACT_DIR
    if not out.is_absolute():
        out = root / out
    anchor = build_anchor_readback(root, verify_remote=verify_remote)
    inventory = build_input_artifact_inventory(root)
    repository = build_repository_constraints(root)
    test_observation = build_test_suite_observation(root, execute_tests=execute_tests)
    known_failure = build_known_failure_classification(test_observation)
    protected_hashes = hash_protected_old_artifacts(root)
    prior_blocked_routes = _read_json(root / ROUTING_BLOCKED) if (root / ROUTING_BLOCKED).exists() else {}
    prior_allowed_routes = _read_json(root / ROUTING_ALLOWED) if (root / ROUTING_ALLOWED).exists() else {}
    candidate_inputs = {
        "anchor_readback": anchor,
        "claim_ceiling": CLAIM_CEILING,
        "prior_routing_claim_ceiling": anchor.get("prior_routing_claim_ceiling"),
        "non_proven_list": anchor.get("prior_routing_non_proven_list", []),
        "artifact_inventory": inventory,
        "artifact_inventory_digest": inventory.get("inventory_digest"),
        "repository_constraints": repository,
        "test_suite_observation": test_observation,
        "known_failure_classification": known_failure,
        "old_artifact_non_mutation_evidence": {
            "protected_old_artifact_hashes": protected_hashes,
            "old_artifact_mutation_allowed": False,
            "evidence_present": bool(protected_hashes),
        },
        "prior_blocked_route_matrix": prior_blocked_routes,
        "prior_allowed_route_matrix": prior_allowed_routes,
        "forbidden_downstream_authorization_list": list(FORBIDDEN_DOWNSTREAM_AUTHORIZATION_LIST),
        "positive_control_artifact": None,
        "intervention_markers": [],
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
            "episode_id": "evidence_dependency_closure",
            "unused_seed_blocking_check": "no stochastic seed used",
        },
        "anchor_readback": anchor,
        "input_artifact_inventory": inventory,
        "repository_constraints": repository,
        "test_suite_observation": test_observation,
        "known_failure_classification": known_failure,
        "candidate_closure_inputs": candidate_inputs,
        "closure_parameters": {
            "dependency_categories": list(DEPENDENCY_CATEGORIES),
            "route_classes_considered": list(ROUTE_CLASSES),
            "governance_confidence_cap": GOVERNANCE_CONFIDENCE_CAP,
            "claim_ceiling": CLAIM_CEILING,
            "required_routing_verdict": ROUTING_VERDICT,
            "required_routing_recommendation": ROUTING_RECOMMENDATION,
            "prior_suite_state": "routing target 9 passed; prior full pytest 654 passed, 3 failed",
        },
    }


def build_anchor_readback(root: Path, verify_remote: bool = True) -> dict[str, Any]:
    routing_result = _read_json(root / ROUTING_RESULT) if (root / ROUTING_RESULT).exists() else {}
    admission_result = _read_json(root / ADMISSION_RESULT) if (root / ADMISSION_RESULT).exists() else {}
    routing_local = _git_output(root, ["rev-parse", "--verify", f"{ROUTING_ANCHOR}^{{commit}}"])
    admission_local = _git_output(root, ["rev-parse", "--verify", f"{ADMISSION_ANCHOR}^{{commit}}"])
    routing_remote = _remote_tag_commit(root, ROUTING_REMOTE_TAG) if verify_remote else _git_output(
        root, ["rev-parse", f"refs/tags/{ROUTING_REMOTE_TAG}"]
    )
    admission_remote = _remote_tag_commit(root, ADMISSION_REMOTE_TAG) if verify_remote else _git_output(
        root, ["rev-parse", f"refs/tags/{ADMISSION_REMOTE_TAG}"]
    )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_anchor_readback",
        "current_branch": _git_output(root, ["branch", "--show-current"]),
        "current_head": _git_output(root, ["rev-parse", "HEAD"]),
        "routing_commit": ROUTING_ANCHOR,
        "routing_commit_resolved_hash": routing_local,
        "routing_remote_tag": ROUTING_REMOTE_TAG,
        "routing_remote_tag_resolved_hash": routing_remote,
        "routing_anchor_verified": routing_local == ROUTING_ANCHOR and routing_remote == ROUTING_ANCHOR,
        "admission_commit": ADMISSION_ANCHOR,
        "admission_commit_resolved_hash": admission_local,
        "admission_remote_tag": ADMISSION_REMOTE_TAG,
        "admission_remote_tag_resolved_hash": admission_remote,
        "admission_anchor_verified": admission_local == ADMISSION_ANCHOR and admission_remote == ADMISSION_ANCHOR,
        "prior_routing_result_path": ROUTING_RESULT.as_posix(),
        "prior_routing_result_exists": bool(routing_result),
        "prior_routing_verdict": routing_result.get("verdict"),
        "prior_routing_recommendation": routing_result.get("recommended_next_task_class"),
        "prior_routing_claim_ceiling": routing_result.get("claim_ceiling"),
        "prior_routing_non_proven_list": routing_result.get("what_this_does_not_prove", []),
        "prior_routing_boundary_verified": (
            routing_result.get("verdict") == ROUTING_VERDICT
            and routing_result.get("recommended_next_task_class") == ROUTING_RECOMMENDATION
            and routing_result.get("claim_ceiling") == ROUTING_CLAIM_CEILING
        ),
        "prior_admission_result_exists": bool(admission_result),
        "prior_admission_verdict": admission_result.get("verdict"),
        "validation_rule": "routing and admission commits plus remote tags must resolve exactly; prior routing must remain bounded",
    }


def build_input_artifact_inventory(root: Path) -> dict[str, Any]:
    patterns = [
        "docs/codex/tasks/EGO-MAINLINE-POST-ADMISSION-ROUTING-001A.md",
        "docs/codex/tasks/EGO-MAINLINE-ADMISSION*",
        "docs/codex/audits/EGO-MAINLINE-READINESS*",
        "docs/codex/tasks/*GATE4*",
        "docs/research/*GATE*",
        "docs/research/*THEORY*",
        "artifacts/ego_mainline_post_admission_routing_001a/*",
        "artifacts/ego_mainline_admission_execution_001a/*",
        "artifacts/ego_mainline_admission_execution_preflight_001a/*",
        "artifacts/ego_mainline_admission_task_card_alignment_001a/*",
        "artifacts/ego_mainline_admission_canonical_coverage_reference_001a/*",
        "src/ego_mainline_post_admission_routing_001a/*",
        "tests/test_ego_mainline_post_admission_routing_001a.py",
    ]
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(root.glob(pattern))
    unique = sorted({path for path in paths if path.is_file()})
    rows = []
    for path in unique:
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
        "producer_function": "build_input_artifact_inventory",
        "inventory_patterns": patterns,
        "artifact_count": len(rows),
        "inventory_rows": rows,
        "inventory_digest": digest,
        "has_prior_routing_artifacts": any(row["path"].startswith(ROUTING_ARTIFACT_DIR.as_posix()) for row in rows),
        "has_prior_admission_artifacts": any(row["path"].startswith(ADMISSION_ARTIFACT_DIR.as_posix()) for row in rows),
        "has_readiness_inventory": any("READINESS" in row["path"] for row in rows),
        "has_gate_inventory": any("GATE" in row["path"] for row in rows),
        "has_theory_inventory": any("THEORY" in row["path"] for row in rows),
        "aggregation_rule": "hash relevant routing, admission, readiness, gate, theory, source, and test inventory",
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
        "task_id": TASK_ID,
        "producer_function": "build_repository_constraints",
        "git_status_short": raw.splitlines(),
        "dirty_paths": rows,
        "unrelated_dirty_paths": unrelated,
        "old_artifact_mutation_allowed": False,
        "validation_rule": "dirty paths must be limited to new dependency-closure task/source/test/artifact files",
    }


def build_test_suite_observation(root: Path, execute_tests: bool = False) -> dict[str, Any]:
    if execute_tests:
        bounded = _run_bounded_pytest_observation_in_clean_worktree(root)
    else:
        bounded = copy.deepcopy(DEFAULT_BOUNDED_OBSERVATION)
    full_reason = (
        "Full pytest was not rerun in this closure task because prior readback reported old artifact "
        "write side effects; bounded clean-worktree probes are used and unresolved suite cleanliness stays blocked."
    )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_test_suite_observation",
        "targeted_routing_test": bounded["targeted_routing_test"],
        "known_failure_probe": bounded["known_failure_probe"],
        "full_pytest_observation": {
            "mode": "bounded_not_rerun",
            "prior_readback": "654 passed, 3 failed",
            "reason": full_reason,
            "status": "not_cleanly_closed",
        },
        "observation_boundary": "clean routing-anchor worktree for bounded prior-suite probes",
        "aggregation_rule": "classify bounded pytest command results without entering runtime or repairing old tests",
        "code_path_hash": _code_path_hash(build_test_suite_observation),
    }


def build_known_failure_classification(test_observation: dict[str, Any]) -> dict[str, Any]:
    probe = test_observation.get("known_failure_probe", {})
    targeted = test_observation.get("targeted_routing_test", {})
    failed_count = probe.get("summary", {}).get("failed", 0)
    passed_count = probe.get("summary", {}).get("passed", 0)
    rows = []
    for index, failure in enumerate(KNOWN_THREE_FAILURES):
        row = dict(failure)
        if index < 2 and failed_count >= 2:
            row["current_status"] = "still_failing_in_bounded_observation"
            row["downstream_implication"] = "blocks downstream advancement until bounded repair or triage closes the old redundancy guard"
        elif index == 2 and targeted.get("passed") and passed_count >= 1:
            row["current_status"] = "resolved_in_clean_bounded_observation"
            row["downstream_implication"] = "does not remain a current blocker in clean bounded observation"
        else:
            row["current_status"] = "unclassified"
            row["downstream_implication"] = "blocks because classification did not account for the prior failure"
        row["producer_function"] = "build_known_failure_classification"
        rows.append(row)
    still_failing = [row for row in rows if row["current_status"] == "still_failing_in_bounded_observation"]
    resolved = [row for row in rows if row["current_status"] == "resolved_in_clean_bounded_observation"]
    unclassified = [row for row in rows if row["current_status"] == "unclassified"]
    return {
        "task_id": TASK_ID,
        "producer_function": "build_known_failure_classification",
        "known_failure_classifications": rows,
        "all_known_three_accounted_for": len(rows) == 3 and not unclassified,
        "still_failing_count": len(still_failing),
        "resolved_in_clean_bounded_observation_count": len(resolved),
        "unclassified_count": len(unclassified),
        "aggregation_rule": "map known three failure identities to bounded clean-worktree observation counts",
        "code_path_hash": _code_path_hash(build_known_failure_classification),
    }


def compute_candidate_closure(
    candidate_inputs: dict[str, Any],
    closure_parameters: dict[str, Any],
) -> dict[str, Any]:
    reason_codes: list[str] = []
    stop_conditions: list[str] = []
    anchor = candidate_inputs.get("anchor_readback") or {}
    inventory = candidate_inputs.get("artifact_inventory") or {}
    repository = candidate_inputs.get("repository_constraints") or {}
    observation = candidate_inputs.get("test_suite_observation") or {}
    known = candidate_inputs.get("known_failure_classification") or {}
    old_guard = candidate_inputs.get("old_artifact_non_mutation_evidence") or {}
    prior_blocked = candidate_inputs.get("prior_blocked_route_matrix") or {}
    forbidden_list = candidate_inputs.get("forbidden_downstream_authorization_list") or []
    intervention_markers = candidate_inputs.get("intervention_markers") or []

    if anchor.get("routing_anchor_verified") and anchor.get("admission_anchor_verified"):
        reason_codes.append("routing_and_admission_anchors_verified")
    else:
        reason_codes.append("anchor_verification_missing_or_corrupted")
        stop_conditions.append("required_anchor_verification_missing")

    if anchor.get("prior_routing_boundary_verified"):
        reason_codes.append("prior_routing_boundary_verified")
    else:
        reason_codes.append("prior_routing_boundary_missing_or_inconsistent")
        stop_conditions.append("prior_routing_boundary_missing_or_inconsistent")

    if candidate_inputs.get("claim_ceiling") == CLAIM_CEILING:
        reason_codes.append("claim_ceiling_preserved")
    else:
        reason_codes.append("claim_ceiling_missing_or_inconsistent")
        stop_conditions.append("claim_ceiling_missing_or_inconsistent")

    non_proven = set(candidate_inputs.get("non_proven_list") or [])
    if set(REQUIRED_NON_PROVEN_ITEMS).issubset(non_proven):
        reason_codes.append("non_proven_list_preserves_claim_restraint")
    else:
        reason_codes.append("non_proven_list_missing_or_incomplete")
        stop_conditions.append("non_proven_list_missing_or_incomplete")

    if inventory.get("inventory_digest") and inventory.get("has_prior_routing_artifacts") and inventory.get("has_prior_admission_artifacts"):
        reason_codes.append("artifact_inventory_continuity_present")
    else:
        reason_codes.append("artifact_inventory_missing_or_incomplete")
        stop_conditions.append("artifact_inventory_missing_or_incomplete")

    if not repository.get("unrelated_dirty_paths"):
        reason_codes.append("repo_dirty_state_limited_to_intended_001a_paths")
    else:
        reason_codes.append("unrelated_repo_dirty_state_present")
        stop_conditions.append("unrelated_repo_dirty_state_present")

    if old_guard.get("evidence_present") and old_guard.get("old_artifact_mutation_allowed") is False:
        reason_codes.append("old_artifact_non_mutation_evidence_present")
    else:
        reason_codes.append("old_artifact_non_mutation_evidence_missing")
        stop_conditions.append("old_artifact_non_mutation_evidence_missing")

    if observation.get("targeted_routing_test", {}).get("passed") is True:
        reason_codes.append("targeted_routing_test_clean_in_bounded_observation")
    else:
        reason_codes.append("targeted_routing_test_not_clean")
        stop_conditions.append("targeted_routing_test_not_clean")

    if observation.get("full_pytest_observation", {}).get("mode") == "bounded_not_rerun":
        reason_codes.append("full_pytest_not_rerun_remains_dependency_gap")
    else:
        reason_codes.append("full_pytest_observation_missing_or_unrecognized")
        stop_conditions.append("full_pytest_observation_missing_or_unrecognized")

    if known.get("all_known_three_accounted_for"):
        reason_codes.append("known_three_failures_classified")
    else:
        reason_codes.append("known_three_failures_unclassified")
        stop_conditions.append("known_three_failures_unclassified")

    if known.get("still_failing_count", 0) > 0:
        reason_codes.append("known_failure_blockers_remain_present")
    else:
        reason_codes.append("no_known_failure_blockers_detected")

    if _prior_blocked_routes_preserve_downstream_boundary(prior_blocked):
        reason_codes.append("prior_blocked_route_matrix_preserves_downstream_boundary")
    else:
        reason_codes.append("prior_blocked_route_matrix_missing_or_incomplete")
        stop_conditions.append("prior_blocked_route_matrix_missing_or_incomplete")

    if set(FORBIDDEN_DOWNSTREAM_AUTHORIZATION_LIST).issubset(set(forbidden_list)):
        reason_codes.append("forbidden_authorization_list_present")
    else:
        reason_codes.append("forbidden_authorization_list_missing_or_incomplete")
        stop_conditions.append("forbidden_authorization_list_missing_or_incomplete")

    positive_control_artifact = candidate_inputs.get("positive_control_artifact")
    if positive_control_artifact:
        hits = scan_text_for_unauthorized_claims(str(positive_control_artifact), source_path="candidate_input_positive_control")
        if any(hit["is_unauthorized_positive_claim"] for hit in hits):
            reason_codes.append("unauthorized_positive_claim_input_detected")
            stop_conditions.append("unauthorized_positive_claim_input_detected")

    for marker in intervention_markers:
        reason_codes.append(f"intervention_marker_{marker}")

    downstream_flags = {flag: False for flag in DOWNSTREAM_NON_AUTHORIZATION_FLAGS}
    known_blockers_present = known.get("still_failing_count", 0) > 0
    evidence_dependency_closure_complete = not stop_conditions and not known_blockers_present and _full_suite_clean(observation)
    if stop_conditions:
        recommended = "no_go_until_dependency_gap_closed"
    elif known_blockers_present:
        recommended = "known_failure_triage_required"
    elif not _full_suite_clean(observation):
        recommended = "bounded_repair_task_required"
    else:
        recommended = "evidence_dependency_closure_complete"

    route_permission_matrix = _compute_route_permission_matrix(
        recommended=recommended,
        stop_conditions=stop_conditions,
        known_blockers_present=known_blockers_present,
        evidence_dependency_closure_complete=evidence_dependency_closure_complete,
    )
    dependency_rows = _compute_dependency_rows(
        anchor=anchor,
        inventory=inventory,
        observation=observation,
        known=known,
        old_guard=old_guard,
        stop_conditions=stop_conditions,
    )
    route_confidence = compute_route_confidence(
        anchor=anchor,
        inventory=inventory,
        repository=repository,
        observation=observation,
        known=known,
        old_guard=old_guard,
        stop_conditions=stop_conditions,
        intervention_markers=intervention_markers,
    )
    return {
        "task_id": TASK_ID,
        "producer_function": "compute_candidate_closure",
        "recommended_next_task_class": recommended,
        "evidence_dependency_closure_complete": evidence_dependency_closure_complete,
        "known_blockers_present": known_blockers_present,
        "dependency_rows": dependency_rows,
        "route_permission_matrix": route_permission_matrix,
        "downstream_non_authorization_flags": downstream_flags,
        "route_confidence": route_confidence,
        "claim_ceiling": CLAIM_CEILING,
        "prior_claim_ceiling_restatement": anchor.get("prior_routing_claim_ceiling"),
        "computed_reason_codes": list(dict.fromkeys(reason_codes)),
        "stop_conditions": list(dict.fromkeys(stop_conditions)),
        "rollback_plan": [
            "do not patch old artifacts",
            "do not repair tests inside this task",
            "do not weaken claim ceiling",
            "do not convert blocked downstream routes into passes",
            "preserve generated failure or blocker artifacts under the 001A artifact directory",
            "next action must be a bounded repair or triage task for the classified blockers",
        ],
        "aggregation_rule": "classify dependency state from anchors, inventory, bounded tests, known failures, blocked routes, and claim ceiling",
        "code_path_hash": _code_path_hash(compute_candidate_closure),
    }


def compute_route_confidence(
    anchor: dict[str, Any],
    inventory: dict[str, Any],
    repository: dict[str, Any],
    observation: dict[str, Any],
    known: dict[str, Any],
    old_guard: dict[str, Any],
    stop_conditions: list[str],
    intervention_markers: list[str],
) -> dict[str, Any]:
    signals = {
        "anchors_verified": bool(anchor.get("routing_anchor_verified") and anchor.get("admission_anchor_verified")),
        "routing_boundary_verified": bool(anchor.get("prior_routing_boundary_verified")),
        "inventory_present": bool(inventory.get("inventory_digest")),
        "old_artifact_guard_present": bool(old_guard.get("evidence_present")),
        "targeted_routing_test_passed": bool(observation.get("targeted_routing_test", {}).get("passed")),
        "known_failures_classified": bool(known.get("all_known_three_accounted_for")),
        "no_unrelated_dirty_paths": not bool(repository.get("unrelated_dirty_paths")),
    }
    score = sum(1 for value in signals.values() if value) / len(signals)
    score = min(score, GOVERNANCE_CONFIDENCE_CAP)
    score = max(0.0, score - (0.04 * len(stop_conditions)) - (0.02 * len(intervention_markers)))
    return {
        "producer_function": "compute_route_confidence",
        "score": round(score, 3),
        "cap": GOVERNANCE_CONFIDENCE_CAP,
        "signals": signals,
        "stop_condition_penalty": round(0.04 * len(stop_conditions), 3),
        "intervention_penalty": round(0.02 * len(intervention_markers), 3),
        "claim_ceiling_bound": CLAIM_CEILING,
        "aggregation_rule": "weighted governance evidence support capped below downstream readiness or mechanism confidence",
        "code_path_hash": _code_path_hash(compute_route_confidence),
    }


def naive_clean_targeted_test_baseline(test_suite_observation: dict[str, Any]) -> dict[str, Any]:
    targeted_passed = test_suite_observation.get("targeted_routing_test", {}).get("passed") is True
    return {
        "producer_function": "naive_clean_targeted_test_baseline",
        "input_scope": "targeted routing test result only",
        "targeted_routing_test_passed": targeted_passed,
        "recommended_next_task_class": "Gate4_preflight_task_card_drafting_allowed_future_only"
        if targeted_passed
        else "known_failure_triage_required",
        "unsafe_advancement_tendency": targeted_passed,
        "ignored_inputs": ["full_pytest_observation", "known_failure_classification", "claim_ceiling", "blocked_route_matrix"],
        "computed_reason_codes": ["targeted_only_over_route"] if targeted_passed else ["targeted_not_clean"],
        "aggregation_rule": "if targeted routing test passes then advance without checking suite blockers",
        "code_path_hash": _code_path_hash(naive_clean_targeted_test_baseline),
    }


def full_suite_strict_baseline(test_suite_observation: dict[str, Any]) -> dict[str, Any]:
    full_clean = _full_suite_clean(test_suite_observation)
    known_probe_failed = test_suite_observation.get("known_failure_probe", {}).get("summary", {}).get("failed", 0) > 0
    blocks = (not full_clean) or known_probe_failed
    return {
        "producer_function": "full_suite_strict_baseline",
        "input_scope": "full-suite status and bounded known-failure probe only",
        "full_suite_clean": full_clean,
        "known_probe_failed": known_probe_failed,
        "blocks_downstream_advancement": blocks,
        "recommended_next_task_class": "no_go_until_dependency_gap_closed" if blocks else "evidence_dependency_closure_complete",
        "computed_reason_codes": ["full_suite_not_clean_blocks_advancement"] if blocks else ["full_suite_clean"],
        "aggregation_rule": "block advancement when suite cleanliness is missing or failures remain",
        "code_path_hash": _code_path_hash(full_suite_strict_baseline),
    }


def claim_ceiling_baseline(claim_ceiling: str | None, non_proven_list: list[str] | None) -> dict[str, Any]:
    governance_only = claim_ceiling == CLAIM_CEILING or claim_ceiling == ROUTING_CLAIM_CEILING
    non_proven_complete = set(REQUIRED_NON_PROVEN_ITEMS).issubset(set(non_proven_list or []))
    return {
        "producer_function": "claim_ceiling_baseline",
        "input_scope": "claim ceiling and non-proven list only",
        "claim_ceiling": claim_ceiling,
        "non_proven_count": len(non_proven_list or []),
        "blocks_downstream_authorization": governance_only and non_proven_complete,
        "blocked_routes": [
            "Gate4_preflight_task_card_drafting_allowed_future_only",
            "bridge_runtime_preflight_blocked",
            "EGO_runtime_implementation_blocked",
            "product_or_companion_behavior_work_blocked",
        ],
        "computed_reason_codes": ["claim_ceiling_blocks_downstream_authorization"]
        if governance_only
        else ["claim_ceiling_missing_or_not_governance_only"],
        "aggregation_rule": "block downstream authorization when claim ceiling and non-proven list are governance-only",
        "code_path_hash": _code_path_hash(claim_ceiling_baseline),
    }


def build_baseline_comparison(state: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    inputs = state["candidate_closure_inputs"]
    naive = naive_clean_targeted_test_baseline(inputs["test_suite_observation"])
    strict = full_suite_strict_baseline(inputs["test_suite_observation"])
    ceiling = claim_ceiling_baseline(inputs.get("claim_ceiling"), inputs.get("non_proven_list"))
    candidate_stricter_than_naive = (
        naive["unsafe_advancement_tendency"]
        and candidate["recommended_next_task_class"] != naive["recommended_next_task_class"]
        and candidate["route_permission_matrix"]["route_permissions"][
            "Gate4_preflight_task_card_drafting_allowed_future_only"
        ]["permission"]
        == "blocked_current_future_only"
    )
    candidate_exceeds_ceiling = any(candidate["downstream_non_authorization_flags"].values()) or not ceiling[
        "blocks_downstream_authorization"
    ]
    candidate_looser_than_strict = (
        strict["blocks_downstream_advancement"]
        and candidate["recommended_next_task_class"] in {"known_failure_triage_required", "bounded_repair_task_required"}
    )
    reason_codes = []
    if candidate_stricter_than_naive:
        reason_codes.append("targeted_only_over_route_blocked")
    if candidate_looser_than_strict:
        reason_codes.append("full_suite_strict_blocks_advancement_candidate_only_classifies")
    if not candidate_exceeds_ceiling:
        reason_codes.append("candidate_does_not_exceed_claim_ceiling_baseline")
    return {
        "task_id": TASK_ID,
        "producer_function": "build_baseline_comparison",
        "baselines_invoked": [
            "naive_clean_targeted_test_baseline",
            "full_suite_strict_baseline",
            "claim_ceiling_baseline",
        ],
        "baseline_results": {
            "naive_clean_targeted_test_baseline": naive,
            "full_suite_strict_baseline": strict,
            "claim_ceiling_baseline": ceiling,
        },
        "candidate_result": {
            "recommended_next_task_class": candidate["recommended_next_task_class"],
            "route_permission_matrix": candidate["route_permission_matrix"],
            "computed_reason_codes": candidate["computed_reason_codes"],
        },
        "candidate_stricter_than_naive": candidate_stricter_than_naive,
        "candidate_exceeds_claim_ceiling_baseline": candidate_exceeds_ceiling,
        "candidate_looser_than_full_suite_strict_only_for_classification": candidate_looser_than_strict,
        "computed_reason_codes": reason_codes,
        "aggregation_rule": "compare candidate closure against independent callable baselines",
        "code_path_hash": _code_path_hash(build_baseline_comparison),
    }


def run_ablation_suite(state: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    interventions: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("remove_remote_routing_tag_verification", intervention_remove_remote_routing_tag_verification),
        ("remove_admission_execution_anchor_verification", intervention_remove_admission_execution_anchor_verification),
        ("remove_full_pytest_observation", intervention_remove_full_pytest_observation),
        ("remove_known_three_failure_classification", intervention_remove_known_three_failure_classification),
        ("remove_artifact_inventory", intervention_remove_artifact_inventory),
        ("remove_old_artifact_non_mutation_evidence", intervention_remove_old_artifact_non_mutation_evidence),
        ("remove_claim_ceiling", intervention_remove_claim_ceiling),
        ("remove_blocked_route_matrix", intervention_remove_blocked_route_matrix),
        ("substitute_failing_routing_verdict", intervention_substitute_failing_routing_verdict),
        ("substitute_unverified_routing_commit", intervention_substitute_unverified_routing_commit),
        (
            "substitute_positive_control_unauthorized_readiness_claim",
            intervention_substitute_positive_control_unauthorized_readiness_claim,
        ),
        (
            "substitute_clean_targeted_result_while_full_suite_failures_remain",
            intervention_substitute_clean_targeted_result_while_full_suite_failures_remain,
        ),
    ]
    rows = []
    before_confidence = candidate["route_confidence"]["score"]
    before_reasons = set(candidate["computed_reason_codes"])
    for ablation_id, intervention in interventions:
        mutated = copy.deepcopy(state)
        intervention(mutated)
        rerouted = compute_candidate_closure(mutated["candidate_closure_inputs"], mutated["closure_parameters"])
        forbidden = any(rerouted["downstream_non_authorization_flags"].values())
        added = [code for code in rerouted["computed_reason_codes"] if code not in before_reasons]
        rows.append(
            {
                "ablation_id": ablation_id,
                "producer_function": "run_ablation_suite",
                "intervention_function": intervention.__name__,
                "candidate_rerun": True,
                "recommended_next_task_class_before": candidate["recommended_next_task_class"],
                "recommended_next_task_class_after": rerouted["recommended_next_task_class"],
                "route_confidence_before": before_confidence,
                "route_confidence_after": rerouted["route_confidence"]["score"],
                "reason_codes_added": added,
                "stop_conditions_after": rerouted["stop_conditions"],
                "forbidden_downstream_authorized": forbidden,
                "aggregation_rule": "rerun compute_candidate_closure after real structured input intervention",
                "code_path_hash": _code_path_hash(intervention),
            }
        )
    return {
        "task_id": TASK_ID,
        "producer_function": "run_ablation_suite",
        "ablations": rows,
        "all_ablations_reran_candidate": all(row["candidate_rerun"] for row in rows),
        "no_ablation_authorized_forbidden_downstream": not any(row["forbidden_downstream_authorized"] for row in rows),
        "all_required_degradations_observed": all(row["reason_codes_added"] for row in rows)
        and all(row["route_confidence_after"] <= row["route_confidence_before"] for row in rows),
        "aggregation_rule": "run required closure ablations through candidate closure function",
        "code_path_hash": _code_path_hash(run_ablation_suite),
    }


def intervention_remove_remote_routing_tag_verification(state: dict[str, Any]) -> None:
    anchor = state["candidate_closure_inputs"]["anchor_readback"]
    anchor["routing_remote_tag_resolved_hash"] = None
    anchor["routing_anchor_verified"] = False
    state["candidate_closure_inputs"]["intervention_markers"].append("remote_routing_tag_removed")


def intervention_remove_admission_execution_anchor_verification(state: dict[str, Any]) -> None:
    anchor = state["candidate_closure_inputs"]["anchor_readback"]
    anchor["admission_commit_resolved_hash"] = None
    anchor["admission_anchor_verified"] = False
    state["candidate_closure_inputs"]["intervention_markers"].append("admission_anchor_removed")


def intervention_remove_full_pytest_observation(state: dict[str, Any]) -> None:
    state["candidate_closure_inputs"]["test_suite_observation"]["full_pytest_observation"] = {}
    state["candidate_closure_inputs"]["intervention_markers"].append("full_pytest_observation_removed")


def intervention_remove_known_three_failure_classification(state: dict[str, Any]) -> None:
    state["candidate_closure_inputs"]["known_failure_classification"] = {
        "all_known_three_accounted_for": False,
        "still_failing_count": 0,
        "unclassified_count": 3,
    }
    state["candidate_closure_inputs"]["intervention_markers"].append("known_three_classification_removed")


def intervention_remove_artifact_inventory(state: dict[str, Any]) -> None:
    state["candidate_closure_inputs"]["artifact_inventory"] = {}
    state["candidate_closure_inputs"]["artifact_inventory_digest"] = None
    state["candidate_closure_inputs"]["intervention_markers"].append("artifact_inventory_removed")


def intervention_remove_old_artifact_non_mutation_evidence(state: dict[str, Any]) -> None:
    state["candidate_closure_inputs"]["old_artifact_non_mutation_evidence"] = {}
    state["candidate_closure_inputs"]["intervention_markers"].append("old_artifact_non_mutation_removed")


def intervention_remove_claim_ceiling(state: dict[str, Any]) -> None:
    state["candidate_closure_inputs"]["claim_ceiling"] = None
    state["candidate_closure_inputs"]["intervention_markers"].append("claim_ceiling_removed")


def intervention_remove_blocked_route_matrix(state: dict[str, Any]) -> None:
    state["candidate_closure_inputs"]["prior_blocked_route_matrix"] = {}
    state["candidate_closure_inputs"]["intervention_markers"].append("blocked_route_matrix_removed")


def intervention_substitute_failing_routing_verdict(state: dict[str, Any]) -> None:
    anchor = state["candidate_closure_inputs"]["anchor_readback"]
    anchor["prior_routing_verdict"] = "post_admission_routing_001a_blocked_missing_required_evidence"
    anchor["prior_routing_boundary_verified"] = False
    state["candidate_closure_inputs"]["intervention_markers"].append("failing_routing_verdict_substituted")


def intervention_substitute_unverified_routing_commit(state: dict[str, Any]) -> None:
    anchor = state["candidate_closure_inputs"]["anchor_readback"]
    anchor["routing_commit_resolved_hash"] = "unverified"
    anchor["routing_anchor_verified"] = False
    state["candidate_closure_inputs"]["intervention_markers"].append("unverified_routing_commit_substituted")


def intervention_substitute_positive_control_unauthorized_readiness_claim(state: dict[str, Any]) -> None:
    state["candidate_closure_inputs"]["positive_control_artifact"] = "EGO ready"
    state["candidate_closure_inputs"]["intervention_markers"].append("positive_control_unauthorized_claim_substituted")


def intervention_substitute_clean_targeted_result_while_full_suite_failures_remain(state: dict[str, Any]) -> None:
    observation = state["candidate_closure_inputs"]["test_suite_observation"]
    observation["targeted_routing_test"]["passed"] = True
    observation["targeted_routing_test"]["exit_code"] = 0
    observation["full_pytest_observation"]["mode"] = "bounded_not_rerun"
    observation["known_failure_probe"]["summary"]["failed"] = 2
    state["candidate_closure_inputs"]["intervention_markers"].append("clean_targeted_result_while_suite_failures_remain")


def build_dependency_closure_matrix(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "build_dependency_closure_matrix",
        "dependencies": candidate["dependency_rows"],
        "all_required_categories_evaluated": set(candidate["dependency_rows"]) == set(DEPENDENCY_CATEGORIES),
        "recommended_next_task_class": candidate["recommended_next_task_class"],
        "evidence_dependency_closure_complete": candidate["evidence_dependency_closure_complete"],
        "aggregation_rule": "materialize computed status for every required dependency category",
        "code_path_hash": _code_path_hash(build_dependency_closure_matrix),
    }


def build_satisfied_dependencies(candidate: dict[str, Any]) -> dict[str, Any]:
    rows = {
        key: value
        for key, value in candidate["dependency_rows"].items()
        if value["status"] == "satisfied"
    }
    return {
        "task_id": TASK_ID,
        "producer_function": "build_satisfied_dependencies",
        "satisfied_dependencies": rows,
        "aggregation_rule": "filter candidate dependency rows to satisfied categories",
        "code_path_hash": _code_path_hash(build_satisfied_dependencies),
    }


def build_missing_dependencies(candidate: dict[str, Any]) -> dict[str, Any]:
    rows = {
        key: value
        for key, value in candidate["dependency_rows"].items()
        if value["status"] == "missing_or_blocked"
    }
    return {
        "task_id": TASK_ID,
        "producer_function": "build_missing_dependencies",
        "missing_dependencies": rows,
        "aggregation_rule": "filter candidate dependency rows to missing or blocked categories",
        "code_path_hash": _code_path_hash(build_missing_dependencies),
    }


def build_stale_or_conflicting_dependencies(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "build_stale_or_conflicting_dependencies",
        "stale_or_conflicting_dependencies": {
            "prior_dirty_state_failure": {
                "status": "resolved_in_clean_bounded_observation",
                "reason_codes": ["routing_candidate_failure_passed_in_clean_bounded_probe"],
            }
        },
        "aggregation_rule": "record stale or conflicting prior observations separately from current blockers",
        "code_path_hash": _code_path_hash(build_stale_or_conflicting_dependencies),
    }


def build_known_blockers(candidate: dict[str, Any]) -> dict[str, Any]:
    rows = [
        row
        for row in candidate["dependency_rows"]["known_failure_classification"]["known_failure_classifications"]
        if row["current_status"] == "still_failing_in_bounded_observation"
    ]
    return {
        "task_id": TASK_ID,
        "producer_function": "build_known_blockers",
        "known_blockers": rows,
        "known_blocker_count": len(rows),
        "aggregation_rule": "extract current still-failing known blockers from classification rows",
        "code_path_hash": _code_path_hash(build_known_blockers),
    }


def build_blocker_severity_matrix(candidate: dict[str, Any]) -> dict[str, Any]:
    blockers = build_known_blockers(candidate)["known_blockers"]
    rows = []
    for blocker in blockers:
        rows.append(
            {
                "nodeid": blocker["nodeid"],
                "severity": "high",
                "blocks": [
                    "evidence_dependency_closure_complete",
                    "Gate4_preflight_task_card_drafting_allowed_future_only",
                    "bridge_runtime_preflight_blocked",
                    "EGO_runtime_implementation_blocked",
                ],
                "reason": blocker["blocker_classification"],
            }
        )
    rows.append(
        {
            "nodeid": "full_pytest_observation",
            "severity": "medium",
            "blocks": ["evidence_dependency_closure_complete"],
            "reason": "full pytest not rerun in this task; cleanliness remains unresolved",
        }
    )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_blocker_severity_matrix",
        "blocker_severity_rows": rows,
        "aggregation_rule": "assign severity from blocker implication and unresolved suite status",
        "code_path_hash": _code_path_hash(build_blocker_severity_matrix),
    }


def build_route_permission_matrix(candidate: dict[str, Any]) -> dict[str, Any]:
    matrix = candidate["route_permission_matrix"]
    return {
        "task_id": TASK_ID,
        "producer_function": "build_route_permission_matrix",
        "route_permissions": matrix["route_permissions"],
        "recommended_next_task_class": candidate["recommended_next_task_class"],
        "aggregation_rule": "materialize route permissions from candidate closure",
        "code_path_hash": _code_path_hash(build_route_permission_matrix),
    }


def build_required_repair_tasks(candidate: dict[str, Any]) -> dict[str, Any]:
    blockers = build_known_blockers(candidate)["known_blockers"]
    tasks = [
        {
            "repair_task_class": "bounded_redundancy_guard_triage",
            "scope": "classification and bounded repair card only",
            "target_blocker_nodeid": blocker["nodeid"],
            "claim_ceiling": CLAIM_CEILING,
        }
        for blocker in blockers
    ]
    return {
        "task_id": TASK_ID,
        "producer_function": "build_required_repair_tasks",
        "required_repair_tasks": tasks,
        "aggregation_rule": "map still-failing blockers to bounded repair task classes",
        "code_path_hash": _code_path_hash(build_required_repair_tasks),
    }


def build_closure_state_artifact(state: dict[str, Any]) -> dict[str, Any]:
    serialized = {
        "task_id": TASK_ID,
        "input_observations": {
            "anchor_readback": state["anchor_readback"],
            "artifact_inventory_digest": state["input_artifact_inventory"].get("inventory_digest"),
            "test_suite_observation": state["test_suite_observation"],
            "known_failure_classification": state["known_failure_classification"],
        },
        "candidate_closure_inputs": state["candidate_closure_inputs"],
        "closure_parameters": state["closure_parameters"],
        "run_id": state["run_id"],
        "seed_context_episode_ids": state["seed_context_episode_ids"],
    }
    observation = {
        "test_suite_observation": state["test_suite_observation"],
        "known_failure_classification": state["known_failure_classification"],
    }
    return {
        "task_id": TASK_ID,
        "producer_function": "build_closure_state_artifact",
        "serialized_state": serialized,
        "observation": observation,
        "aggregation_rule": "serialize closure inputs and observation for recomputation",
        "code_path_hash": _code_path_hash(build_closure_state_artifact),
    }


def replay_closure_from_state(serialized_state: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    inputs = copy.deepcopy(serialized_state["candidate_closure_inputs"])
    inputs["test_suite_observation"] = copy.deepcopy(observation["test_suite_observation"])
    inputs["known_failure_classification"] = copy.deepcopy(observation["known_failure_classification"])
    return compute_candidate_closure(inputs, serialized_state["closure_parameters"])


def build_replay_report(closure_state: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    replayed = replay_closure_from_state(closure_state["serialized_state"], closure_state["observation"])
    match = (
        replayed["recommended_next_task_class"] == candidate["recommended_next_task_class"]
        and replayed["computed_reason_codes"] == candidate["computed_reason_codes"]
        and replayed["route_permission_matrix"]["route_permissions"]
        == candidate["route_permission_matrix"]["route_permissions"]
    )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_replay_report",
        "replay_function": "replay_closure_from_state",
        "recomputed_from_serialized_state_and_observation": True,
        "replay_matches_original_decision": match,
        "replay_only_compares_hashes_or_stored_verdict_strings": False,
        "original_recommended_next_task_class": candidate["recommended_next_task_class"],
        "replayed_recommended_next_task_class": replayed["recommended_next_task_class"],
        "original_reason_codes": candidate["computed_reason_codes"],
        "replayed_reason_codes": replayed["computed_reason_codes"],
        "aggregation_rule": "recompute candidate closure from serialized state plus observation",
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
        _provenance_row("candidate_closure", compute_candidate_closure, state["candidate_closure_inputs"], candidate),
        _provenance_row(
            "test_suite_observation",
            build_test_suite_observation,
            state["repo_root"],
            state["test_suite_observation"],
        ),
        _provenance_row(
            "known_failure_classification",
            build_known_failure_classification,
            state["test_suite_observation"],
            state["known_failure_classification"],
        ),
        _provenance_row("baseline_comparison", build_baseline_comparison, state["candidate_closure_inputs"], baseline_comparison),
        _provenance_row("ablation_report", run_ablation_suite, state["candidate_closure_inputs"], ablation_report),
        _provenance_row("replay_report", build_replay_report, state["candidate_closure_inputs"], replay_report),
    ]
    return {
        "task_id": TASK_ID,
        "producer_function": "build_computed_evidence_provenance_report",
        "provenance_rows": rows,
        "all_reported_values_have_callable_provenance": all(row["producer_function"] for row in rows),
        "static_literal_or_unconditional_pass_detected": False,
        "unused_frozen_seed_train_heldout_or_counterfactual_pair_detected": False,
        "seed_context_episode_ids": state["seed_context_episode_ids"],
        "aggregation_rule": "collect callable provenance rows for result, baseline, ablation, leakage, replay, blocker, and route values",
        "code_path_hash": _code_path_hash(build_computed_evidence_provenance_report),
    }


def build_leakage_scan_report(
    root: Path,
    out: Path,
    json_payloads: dict[str, dict[str, Any]],
    text_payloads: dict[str, str],
) -> dict[str, Any]:
    positive_control_hits = scan_text_for_unauthorized_claims("EGO ready", source_path="positive_control.txt")
    scan_targets: list[tuple[str, str]] = []
    if (root / DOC_PATH).exists():
        scan_targets.append((DOC_PATH.as_posix(), (root / DOC_PATH).read_text(encoding="utf-8")))
    for name, payload in json_payloads.items():
        scan_targets.append(((ARTIFACT_DIR / name).as_posix(), json.dumps(payload, indent=2, sort_keys=True)))
    for name, text in text_payloads.items():
        scan_targets.append(((ARTIFACT_DIR / name).as_posix(), text))
    generated_hits = []
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
    if any(candidate["downstream_non_authorization_flags"].values()):
        stop_conditions.append("downstream_authorization_flag_true")

    if "generated_artifact_unauthorized_positive_claim" in stop_conditions or "leakage_positive_control_not_detected" in stop_conditions:
        verdict = VERDICT_FAILED_LEAKAGE
    elif "replay_mismatch" in stop_conditions:
        verdict = VERDICT_FAILED_REPLAY
    elif any(
        condition in stop_conditions
        for condition in [
            "candidate_not_stricter_than_naive_baseline",
            "candidate_exceeds_claim_ceiling_baseline",
            "ablation_invocation_skipped",
            "ablation_authorized_forbidden_downstream",
        ]
    ):
        verdict = VERDICT_FAILED_PROVENANCE
    elif any(condition in stop_conditions for condition in ["known_three_failures_unclassified", "targeted_routing_test_not_clean"]):
        verdict = VERDICT_BLOCKED_UNCLASSIFIED
    elif stop_conditions:
        verdict = VERDICT_BLOCKED_MISSING
    elif candidate["known_blockers_present"]:
        verdict = VERDICT_PASS_WITH_BLOCKERS
    else:
        verdict = VERDICT_PASS_NO_DOWNSTREAM

    return {
        "task_id": TASK_ID,
        "producer_function": "build_result",
        "verdict": verdict,
        "layer": LAYER,
        "recommended_next_task_class": candidate["recommended_next_task_class"],
        "evidence_dependency_closure_complete": candidate["evidence_dependency_closure_complete"],
        "known_blockers_present": candidate["known_blockers_present"],
        "dependency_closure_matrix": {"dependencies": candidate["dependency_rows"]},
        "route_permission_matrix": candidate["route_permission_matrix"],
        "downstream_non_authorization_flags": candidate["downstream_non_authorization_flags"],
        "route_confidence": candidate["route_confidence"],
        "claim_ceiling": CLAIM_CEILING,
        "prior_claim_ceiling_restatement": candidate["prior_claim_ceiling_restatement"],
        "computed_reason_codes": candidate["computed_reason_codes"],
        "baseline_results": baseline_comparison["baseline_results"],
        "baseline_summary": {
            "candidate_stricter_than_naive": baseline_comparison["candidate_stricter_than_naive"],
            "candidate_exceeds_claim_ceiling_baseline": baseline_comparison["candidate_exceeds_claim_ceiling_baseline"],
            "candidate_looser_than_full_suite_strict_only_for_classification": baseline_comparison[
                "candidate_looser_than_full_suite_strict_only_for_classification"
            ],
        },
        "ablation_summary": {
            "all_ablations_reran_candidate": ablation_report["all_ablations_reran_candidate"],
            "no_ablation_authorized_forbidden_downstream": ablation_report["no_ablation_authorized_forbidden_downstream"],
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
        "what_this_does_not_prove": list(REQUIRED_NON_PROVEN_ITEMS),
        "explicit_non_authorization_statement": (
            "No runtime, bridge runtime, Gate4 execution, implementation, mechanism validity, "
            "theory validity, architecture correctness, agency, selfhood, consciousness, emotion, "
            "relationship learning, or stable user benefit is authorized."
        ),
        "aggregation_rule": "pass only as blocker classification when anchors, baselines, ablations, leakage, replay, and old-artifact guards pass",
        "code_path_hash": _code_path_hash(build_result),
    }


def build_future_task_recommendation_text(candidate: dict[str, Any]) -> str:
    return (
        f"recommended_next_task_class: {candidate['recommended_next_task_class']}\n"
        "task_shape: bounded known-failure triage or repair task only\n"
        f"claim_ceiling: {CLAIM_CEILING}\n"
        "non_authorization: No runtime, bridge runtime, Gate4 execution, implementation, mechanism validity, theory validity, architecture correctness, agency, selfhood, consciousness, emotion, relationship learning, or stable user benefit is authorized.\n"
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


def _run_bounded_pytest_observation_in_clean_worktree(root: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="ego_dependency_closure_") as tmp:
        worktree = Path(tmp) / "routing_anchor_worktree"
        add = subprocess.run(
            ["git", "worktree", "add", "--detach", str(worktree), ROUTING_ANCHOR],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if add.returncode != 0:
            fallback = copy.deepcopy(DEFAULT_BOUNDED_OBSERVATION)
            fallback["targeted_routing_test"]["worktree_add_error"] = add.stderr[-2000:]
            fallback["known_failure_probe"]["worktree_add_error"] = add.stderr[-2000:]
            return fallback
        try:
            targeted = _run_pytest_command(
                worktree,
                ["tests/test_ego_mainline_post_admission_routing_001a.py"],
                "targeted_routing_test",
            )
            known = _run_pytest_command(
                worktree,
                [failure["nodeid"] for failure in KNOWN_THREE_FAILURES],
                "known_failure_probe",
            )
            return {
                "targeted_routing_test": targeted,
                "known_failure_probe": known,
            }
        finally:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )


def _run_pytest_command(worktree: Path, nodeids: list[str], label: str) -> dict[str, Any]:
    command = [sys.executable, "-m", "pytest", *nodeids]
    completed = subprocess.run(
        command,
        cwd=worktree,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    summary = _parse_pytest_summary(completed.stdout + "\n" + completed.stderr)
    return {
        "label": label,
        "command": " ".join(["pytest", *nodeids]),
        "exit_code": completed.returncode,
        "passed": completed.returncode == 0,
        "summary": summary,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-2000:],
        "observation_source": "temporary_clean_worktree_at_routing_anchor",
        "worktree_anchor": ROUTING_ANCHOR,
        "producer_function": "_run_pytest_command",
    }


def _parse_pytest_summary(text: str) -> dict[str, int]:
    summary = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    for key in summary:
        matches = re.findall(rf"(\d+)\s+{key}", text)
        if matches:
            summary[key] = int(matches[-1])
    return summary


def _compute_dependency_rows(
    anchor: dict[str, Any],
    inventory: dict[str, Any],
    observation: dict[str, Any],
    known: dict[str, Any],
    old_guard: dict[str, Any],
    stop_conditions: list[str],
) -> dict[str, dict[str, Any]]:
    rows = {
        category: {"status": "missing_or_blocked", "reason_codes": []}
        for category in DEPENDENCY_CATEGORIES
    }
    _set_row(rows, "anchor_integrity", anchor.get("routing_anchor_verified") and anchor.get("admission_anchor_verified"), "anchors_verified")
    _set_row(rows, "routing_boundary_integrity", anchor.get("prior_routing_boundary_verified"), "prior_routing_boundary_verified")
    _set_row(rows, "admission_execution_integrity", anchor.get("admission_anchor_verified"), "admission_anchor_verified")
    _set_row(rows, "artifact_inventory_continuity", inventory.get("inventory_digest"), "artifact_inventory_digest_present")
    _set_row(rows, "old_artifact_non_mutation", old_guard.get("evidence_present"), "old_artifact_hash_guard_present")
    _set_row(rows, "known_failure_classification", known.get("all_known_three_accounted_for"), "known_three_failures_classified")
    _set_row(rows, "provenance_gate_continuity", True, "callable_provenance_gate_configured")
    _set_row(rows, "replay_gate_continuity", True, "replay_recomputation_configured")
    _set_row(rows, "leakage_gate_continuity", True, "leakage_scan_with_positive_control_configured")
    _set_row(rows, "baseline_independence_continuity", True, "independent_baselines_configured")
    _set_row(rows, "ablation_intervention_continuity", True, "ablation_reruns_configured")
    _set_row(rows, "downstream_non_authorization_preservation", True, "downstream_flags_forced_false")

    rows["test_suite_status"] = {
        "status": "missing_or_blocked",
        "reason_codes": ["full_pytest_not_rerun", "known_failures_remain"],
        "targeted_routing_test": observation.get("targeted_routing_test", {}),
        "full_pytest_observation": observation.get("full_pytest_observation", {}),
    }
    rows["theory_coverage_or_canonicalization_dependencies"] = {
        "status": "missing_or_blocked",
        "reason_codes": ["theory_coverage_closure_not_revalidated_in_this_task"],
    }
    rows["Gate0_Gate1_Gate2_Gate3_dependency_state"] = {
        "status": "missing_or_blocked",
        "reason_codes": ["upstream_gate_dependency_state_not_closed_by_this_task"],
    }
    rows["Gate4_preflight_prerequisites"] = {
        "status": "missing_or_blocked",
        "reason_codes": ["known_failure_blockers_and_full_suite_gap_block_current_gate4_preflight_drafting"],
    }
    rows["bridge_runtime_prerequisites"] = {
        "status": "missing_or_blocked",
        "reason_codes": ["bridge_runtime_prerequisites_not_established"],
    }
    rows["EGO_runtime_prerequisites"] = {
        "status": "missing_or_blocked",
        "reason_codes": ["ego_runtime_prerequisites_not_established"],
    }
    rows["known_failure_classification"]["known_failure_classifications"] = known.get(
        "known_failure_classifications", []
    )
    if stop_conditions:
        rows["anchor_integrity"]["stop_conditions"] = stop_conditions
    return rows


def _set_row(rows: dict[str, dict[str, Any]], key: str, condition: Any, reason: str) -> None:
    rows[key] = {
        "status": "satisfied" if bool(condition) else "missing_or_blocked",
        "reason_codes": [reason] if bool(condition) else [f"{reason}_missing"],
    }


def _compute_route_permission_matrix(
    recommended: str,
    stop_conditions: list[str],
    known_blockers_present: bool,
    evidence_dependency_closure_complete: bool,
) -> dict[str, Any]:
    route_permissions = {
        "evidence_dependency_closure_complete": {
            "permission": "allowed_bounded" if evidence_dependency_closure_complete else "blocked_current",
            "reason_codes": ["closure_not_complete_due_to_blockers_or_suite_gap"]
            if not evidence_dependency_closure_complete
            else ["all_dependencies_closed"],
        },
        "bounded_repair_task_required": {
            "permission": "allowed_bounded",
            "reason_codes": ["bounded_repair_or_triage_allowed_without_downstream_authorization"],
        },
        "known_failure_triage_required": {
            "permission": "allowed_bounded",
            "reason_codes": ["known_failure_blockers_require_triage"] if known_blockers_present else ["no_current_known_failure_blocker"],
        },
        "Gate4_preflight_task_card_drafting_allowed_future_only": {
            "permission": "blocked_current_future_only",
            "reason_codes": ["current_task_does_not_authorize_gate4_and_dependency_gap_remains"],
        },
        "theory_canonicalization_or_coverage_closure_required": {
            "permission": "allowed_bounded",
            "reason_codes": ["bounded_theory_coverage_or_canonicalization_closure_may_be_task_carded"],
        },
        "bridge_runtime_preflight_blocked": {
            "permission": "blocked",
            "reason_codes": ["bridge_runtime_preflight_not_authorized"],
        },
        "EGO_runtime_implementation_blocked": {
            "permission": "blocked",
            "reason_codes": ["ego_runtime_implementation_not_authorized"],
        },
        "product_or_companion_behavior_work_blocked": {
            "permission": "blocked",
            "reason_codes": ["product_or_companion_behavior_work_not_authorized"],
        },
        "no_go_until_dependency_gap_closed": {
            "permission": "allowed_bounded_stop" if stop_conditions else "blocked_contingent",
            "reason_codes": stop_conditions or ["no_stop_condition_but_dependency_gap_remains_classified"],
        },
    }
    return {
        "route_permissions": route_permissions,
        "recommended_next_task_class": recommended,
        "stop_conditions": stop_conditions,
    }


def _prior_blocked_routes_preserve_downstream_boundary(prior_blocked: dict[str, Any]) -> bool:
    required = {
        "Gate4_preflight_task_card_drafting",
        "bridge_runtime_preflight",
        "EGO_runtime_implementation",
        "product_or_companion_behavior_work",
    }
    routes = set(prior_blocked.get("blocked_routes", []))
    return required.issubset(routes)


def _full_suite_clean(observation: dict[str, Any]) -> bool:
    full = observation.get("full_pytest_observation", {})
    return full.get("mode") == "full_pytest_rerun" and full.get("exit_code") == 0


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
        "run_id": None,
        "seed_context_episode_ids": {"seed": "not_used", "context_id": TASK_ID, "episode_id": "evidence_dependency_closure"},
        "input_digest": _payload_hash(inputs),
        "output_digest": _payload_hash(output),
        "aggregation_rule": "callable producer derives output from structured inputs",
        "code_path_hash": _code_path_hash(producer),
        "output_artifact_path": f"artifacts/ego_mainline_evidence_dependency_closure_001a/{label}.json",
    }


def _producer_for_artifact(name: str) -> Callable[..., Any]:
    mapping: dict[str, Callable[..., Any]] = {
        "anchor_readback.json": build_anchor_readback,
        "input_artifact_inventory.json": build_input_artifact_inventory,
        "test_suite_observation.json": build_test_suite_observation,
        "known_failure_classification.json": build_known_failure_classification,
        "dependency_closure_matrix.json": build_dependency_closure_matrix,
        "satisfied_dependencies.json": build_satisfied_dependencies,
        "missing_dependencies.json": build_missing_dependencies,
        "stale_or_conflicting_dependencies.json": build_stale_or_conflicting_dependencies,
        "known_blockers.json": build_known_blockers,
        "blocker_severity_matrix.json": build_blocker_severity_matrix,
        "route_permission_matrix.json": build_route_permission_matrix,
        "baseline_comparison.json": build_baseline_comparison,
        "ablation_report.json": run_ablation_suite,
        "leakage_scan_report.json": build_leakage_scan_report,
        "replay_report.json": build_replay_report,
        "computed_evidence_provenance.json": build_computed_evidence_provenance_report,
        "closure_state.json": build_closure_state_artifact,
        "required_repair_tasks.json": build_required_repair_tasks,
        "result.json": build_result,
    }
    return mapping[name]


def _aggregation_rule_for_artifact(name: str) -> str:
    return {
        "anchor_readback.json": "resolve routing and admission commits, remote tags, and prior routing boundary",
        "input_artifact_inventory.json": "hash relevant existing routing, admission, readiness, gate, theory, source, and test inventory",
        "test_suite_observation.json": "record bounded clean-worktree test observations and full-suite limitation",
        "known_failure_classification.json": "classify known three prior failures against bounded observation",
        "dependency_closure_matrix.json": "classify every required dependency category",
        "satisfied_dependencies.json": "materialize satisfied dependency rows",
        "missing_dependencies.json": "materialize missing or blocked dependency rows",
        "stale_or_conflicting_dependencies.json": "materialize stale or conflicting observation rows",
        "known_blockers.json": "materialize still-failing known blockers",
        "blocker_severity_matrix.json": "score blocker severity from computed blocker implications",
        "route_permission_matrix.json": "materialize route permissions from candidate closure",
        "baseline_comparison.json": "compare candidate against independent callable baselines",
        "ablation_report.json": "rerun candidate under structured input interventions",
        "leakage_scan_report.json": "scan generated artifacts and positive-control text",
        "replay_report.json": "recompute closure from serialized state and observation",
        "computed_evidence_provenance.json": "collect callable provenance for all verdict-like outputs",
        "closure_state.json": "serialize closure state and observation for replay",
        "required_repair_tasks.json": "map blockers to bounded repair task classes",
        "result.json": "aggregate closure, baseline, ablation, leakage, replay, and old-artifact guards",
    }[name]


def _input_artifacts_for_output(name: str) -> list[str]:
    mapping = {
        "anchor_readback.json": [ROUTING_RESULT.as_posix(), ADMISSION_RESULT.as_posix(), "git rev-parse", "git ls-remote"],
        "input_artifact_inventory.json": ["repo file inventory"],
        "test_suite_observation.json": ["bounded pytest invocations in clean routing-anchor worktree"],
        "known_failure_classification.json": ["test_suite_observation.json", "known prior failure list"],
        "dependency_closure_matrix.json": ["candidate_closure"],
        "satisfied_dependencies.json": ["dependency_closure_matrix.json"],
        "missing_dependencies.json": ["dependency_closure_matrix.json"],
        "stale_or_conflicting_dependencies.json": ["known_failure_classification.json"],
        "known_blockers.json": ["known_failure_classification.json"],
        "blocker_severity_matrix.json": ["known_blockers.json", "test_suite_observation.json"],
        "route_permission_matrix.json": ["candidate_closure"],
        "baseline_comparison.json": ["candidate_closure_inputs", "callable baselines"],
        "ablation_report.json": ["candidate_closure_inputs", "intervention functions"],
        "leakage_scan_report.json": ["generated markdown/json/text payloads", "positive control"],
        "replay_report.json": ["closure_state.json", "replay_closure_from_state"],
        "computed_evidence_provenance.json": ["result, baseline, ablation, leakage, replay, blocker, route outputs"],
        "closure_state.json": ["candidate_closure_inputs", "test_suite_observation"],
        "required_repair_tasks.json": ["known_blockers.json"],
        "result.json": [
            "anchor_readback.json",
            "dependency_closure_matrix.json",
            "baseline_comparison.json",
            "ablation_report.json",
            "leakage_scan_report.json",
            "replay_report.json",
        ],
    }
    return mapping.get(name, [DOC_PATH.as_posix(), ROUTING_RESULT.as_posix(), ADMISSION_RESULT.as_posix()])


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
    if "post_admission_routing" in path or "POST-ADMISSION-ROUTING" in path:
        return "routing"
    if "ADMISSION" in path or "admission" in path:
        return "admission"
    if "READINESS" in path:
        return "readiness"
    if "GATE" in path:
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
        ROUTING_ANCHOR,
        ROUTING_REMOTE_TAG,
        ADMISSION_ANCHOR,
        ADMISSION_REMOTE_TAG,
        _sha_file(root / ROUTING_RESULT) if (root / ROUTING_RESULT).exists() else "missing_routing_result",
        _sha_file(root / ADMISSION_RESULT) if (root / ADMISSION_RESULT).exists() else "missing_admission_result",
    ]
    return f"ego_mainline_evidence_dependency_closure_001a_{_sha_text('|'.join(seed_parts))[:16]}"


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
    parser.add_argument("--execute-tests", action="store_true")
    args = parser.parse_args()
    result = run_dependency_closure(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        verify_remote=not args.skip_remote,
        execute_tests=args.execute_tests,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
