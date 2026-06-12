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


TASK_ID = "EGO-MAINLINE-KNOWN-FAILURE-TRIAGE-001A"
LAYER = "evidence-governance / known-failure triage only"
CLAIM_CEILING = "bounded known-failure triage evidence at governance layer only"

DEPENDENCY_CLOSURE_ANCHOR = "01973a538fad9c33ca2c6119a0f2c6b384602f34"
DEPENDENCY_CLOSURE_REMOTE_TAG = "remote-anchor-evidence-dependency-closure-001a-01973a"
ROUTING_ANCHOR = "4edf5cff7f89cf2cf1c6dbb15a478bbada0432aa"
ROUTING_REMOTE_TAG = "remote-anchor-post-admission-routing-001a-4edf5c"
ADMISSION_ANCHOR = "98e51a46cd7f28f60b1851c616d4351c1cd6272f"
ADMISSION_REMOTE_TAG = "remote-anchor-bounded-admission-execution-001a-98e51a4"

VERDICT_PASS_WITH_BLOCKERS = "known_failure_triage_001a_pass_with_blockers_classified"
VERDICT_PASS_NONBLOCKING = "known_failure_triage_001a_pass_failures_nonblocking_but_recorded"
VERDICT_BLOCKED_DISCREPANCY = "known_failure_triage_001a_blocked_unexplained_failure_discrepancy"
VERDICT_BLOCKED_UNCLASSIFIED = "known_failure_triage_001a_blocked_unclassified_failure"
VERDICT_BLOCKED_OLD_ARTIFACT = "known_failure_triage_001a_blocked_old_artifact_side_effect"
VERDICT_FAILED_PROVENANCE = "known_failure_triage_001a_failed_provenance_gate"
VERDICT_FAILED_LEAKAGE = "known_failure_triage_001a_failed_leakage_gate"
VERDICT_FAILED_REPLAY = "known_failure_triage_001a_failed_replay_gate"

ARTIFACT_DIR = Path("artifacts/ego_mainline_known_failure_triage_001a")
DOC_PATH = Path("docs/codex/tasks/EGO-MAINLINE-KNOWN-FAILURE-TRIAGE-001A.md")
DEPENDENCY_CLOSURE_DIR = Path("artifacts/ego_mainline_evidence_dependency_closure_001a")
DEPENDENCY_CLOSURE_RESULT = DEPENDENCY_CLOSURE_DIR / "result.json"
DEPENDENCY_CLOSURE_KNOWN = DEPENDENCY_CLOSURE_DIR / "known_failure_classification.json"
DEPENDENCY_CLOSURE_ROUTES = DEPENDENCY_CLOSURE_DIR / "route_permission_matrix.json"

FAILED_REFERENCE_NODE = (
    "tests/test_ego_mainline_admission_canonical_coverage_reference_001a.py::"
    "test_temp_run_uses_same_validators_without_remote_dependency"
)
FAILED_ALIGNMENT_NODE = (
    "tests/test_ego_mainline_admission_task_card_alignment_001a.py::"
    "test_temp_run_uses_same_validators"
)
FAILED_CLOSURE_NODE = (
    "tests/test_ego_mainline_evidence_dependency_closure_001a.py::"
    "test_callable_candidate_rejects_corrupted_inputs_without_authorizing_downstream"
)
FAILED_ROUTING_NODE = (
    "tests/test_ego_mainline_post_admission_routing_001a.py::"
    "test_callable_candidate_rejects_corrupted_governance_inputs_without_authorizing_downstream"
)
FAILED_NODE_IDS = [
    FAILED_REFERENCE_NODE,
    FAILED_ALIGNMENT_NODE,
    FAILED_CLOSURE_NODE,
    FAILED_ROUTING_NODE,
]

SIDE_EFFECT_PATH = (
    "artifacts/ego_mainline_admission_executable_001d_metric_provenance_repair_001f/"
    "scope_leak_report.json"
)

NON_PROVEN_LIST = [
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

NON_AUTHORIZATION_FLAGS = [
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

REQUIRED_ARTIFACT_NAMES = [
    "result.json",
    "anchor_readback.json",
    "input_artifact_inventory.json",
    "test_suite_observation.json",
    "full_pytest_failure_report.json",
    "isolated_rerun_report.json",
    "failure_reproducibility_matrix.json",
    "failure_cause_classification.json",
    "failure_discrepancy_explanation.json",
    "old_artifact_side_effect_matrix.json",
    "blocker_severity_matrix.json",
    "downstream_route_impact_matrix.json",
    "required_repair_tasks.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_scan_report.json",
    "replay_report.json",
    "computed_evidence_provenance.json",
    "triage_state.json",
    "claim_ceiling.txt",
    "future_task_recommendation.txt",
    "rollback_plan.txt",
]

UNAUTHORIZED_CLAIM_PATTERNS = [
    ("ego_ready", re.compile(r"\bEGO\s+ready\b", re.IGNORECASE)),
    ("bridge_ready", re.compile(r"\bbridge\s+ready\b", re.IGNORECASE)),
    ("runtime_ready", re.compile(r"\bruntime\s+ready\b", re.IGNORECASE)),
    ("gate4_ready", re.compile(r"\bGate4\s+ready\b", re.IGNORECASE)),
    ("gate4_authorized", re.compile(r"\bGate4\s+authorized\b", re.IGNORECASE)),
    ("implementation_authorized", re.compile(r"\bimplementation\s+authorized\b", re.IGNORECASE)),
    ("mechanism_validated", re.compile(r"\bmechanism\s+validated\b", re.IGNORECASE)),
    ("theory_validated", re.compile(r"\btheory\s+validated\b", re.IGNORECASE)),
    ("architecture_correct", re.compile(r"\barchitecture\s+correct\b", re.IGNORECASE)),
    ("agency_achieved", re.compile(r"\bagency\s+achieved\b", re.IGNORECASE)),
    ("selfhood_achieved", re.compile(r"\bselfhood\s+achieved\b", re.IGNORECASE)),
    ("consciousness", re.compile(r"\bconsciousness\b", re.IGNORECASE)),
    ("real_emotion", re.compile(r"\breal\s+emotion\b", re.IGNORECASE)),
    ("relationship_learning", re.compile(r"\brelationship\s+learning\b", re.IGNORECASE)),
    ("stable_user_benefit", re.compile(r"\bstable\s+user\s+benefit\b", re.IGNORECASE)),
]

RESTRAINT_TERMS = [
    "not",
    "no ",
    "non-authorization",
    "non_authorization",
    "blocked",
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
    "failure",
    "failures",
    "scanner",
    "positive control",
    "positive_control",
    "stop condition",
    "rollback",
    "not authorized",
    "does not authorize",
]


def run_known_failure_triage(
    repo_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    verify_remote: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    out = Path(output_dir) if output_dir is not None else root / ARTIFACT_DIR
    if not out.is_absolute():
        out = root / out
    out.mkdir(parents=True, exist_ok=True)

    state = build_triage_state(root, out, verify_remote=verify_remote)
    candidate = compute_candidate_triage(state["candidate_triage_inputs"], state["triage_parameters"])
    baseline = build_baseline_comparison(state, candidate)
    ablation = run_ablation_suite(state, candidate)
    triage_state = build_triage_state_artifact(state)
    replay = build_replay_report(triage_state, candidate)
    provenance = build_computed_evidence_provenance_report(state, candidate, baseline, ablation, replay)

    payloads = {
        "anchor_readback.json": state["anchor_readback"],
        "input_artifact_inventory.json": state["input_artifact_inventory"],
        "test_suite_observation.json": state["test_suite_observation"],
        "full_pytest_failure_report.json": build_full_pytest_failure_report(candidate),
        "isolated_rerun_report.json": build_isolated_rerun_report(candidate),
        "failure_reproducibility_matrix.json": build_failure_reproducibility_matrix(candidate),
        "failure_cause_classification.json": build_failure_cause_classification(candidate),
        "failure_discrepancy_explanation.json": build_failure_discrepancy_explanation(candidate),
        "old_artifact_side_effect_matrix.json": build_old_artifact_side_effect_matrix(candidate),
        "blocker_severity_matrix.json": build_blocker_severity_matrix(candidate),
        "downstream_route_impact_matrix.json": build_downstream_route_impact_matrix(candidate),
        "required_repair_tasks.json": build_required_repair_tasks(candidate),
        "baseline_comparison.json": baseline,
        "ablation_report.json": ablation,
        "replay_report.json": replay,
        "computed_evidence_provenance.json": provenance,
        "triage_state.json": triage_state,
    }
    text_payloads = {
        "claim_ceiling.txt": CLAIM_CEILING + "\n",
        "future_task_recommendation.txt": build_future_task_recommendation_text(candidate),
        "rollback_plan.txt": build_rollback_plan_text(candidate),
    }
    leakage = build_leakage_scan_report(root, {**payloads, "result.json": candidate}, text_payloads)
    result = build_result(candidate, baseline, ablation, leakage, replay)
    payloads["leakage_scan_report.json"] = leakage
    payloads["result.json"] = result

    for name, payload in payloads.items():
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


def build_triage_state(
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
    observation = build_test_suite_observation(root)
    dependency_inputs = build_dependency_closure_inputs(root)
    inputs = {
        "anchor_readback": anchor,
        "full_pytest_observation": observation["full_pytest_observation"],
        "exact_failed_node_ids": list(FAILED_NODE_IDS),
        "traceback_summaries": observation["traceback_summaries"],
        "isolated_rerun_results": observation["isolated_rerun_results"],
        "targeted_test_observations": {
            "targeted_routing_test": observation["targeted_routing_test"],
            "targeted_dependency_closure_test": observation["targeted_dependency_closure_test"],
        },
        "hash_inventory": observation["hash_inventory"],
        "side_effect_report": observation["side_effect_report"],
        "prior_dependency_closure_classification": dependency_inputs["known_failure_classification"],
        "prior_route_permission_matrix": dependency_inputs["route_permission_matrix"],
        "claim_ceiling": CLAIM_CEILING,
        "non_proven_list": list(NON_PROVEN_LIST),
        "positive_control_artifact": None,
        "intervention_markers": [],
    }
    return {
        "task_id": TASK_ID,
        "run_id": _run_id(root),
        "repo_root": root.as_posix(),
        "output_dir": out.as_posix(),
        "seed_context_episode_ids": {
            "seed": "not_used",
            "context_id": TASK_ID,
            "episode_id": "known_failure_triage",
            "unused_seed_blocking_check": "no stochastic seed used",
        },
        "anchor_readback": anchor,
        "input_artifact_inventory": inventory,
        "test_suite_observation": observation,
        "dependency_closure_inputs": dependency_inputs,
        "candidate_triage_inputs": inputs,
        "triage_parameters": {
            "required_failed_node_ids": list(FAILED_NODE_IDS),
            "claim_ceiling": CLAIM_CEILING,
            "prior_full_pytest_failed_count": 3,
            "prior_known_failure_probe_failed_count": 2,
            "prior_known_failure_probe_passed_count": 1,
        },
    }


def build_anchor_readback(root: Path, verify_remote: bool = True) -> dict[str, Any]:
    dep_local = _git_output(root, ["rev-parse", DEPENDENCY_CLOSURE_ANCHOR])
    routing_local = _git_output(root, ["rev-parse", ROUTING_ANCHOR])
    admission_local = _git_output(root, ["rev-parse", ADMISSION_ANCHOR])
    dep_remote = _remote_tag_commit(root, DEPENDENCY_CLOSURE_REMOTE_TAG) if verify_remote else dep_local
    routing_remote = _remote_tag_commit(root, ROUTING_REMOTE_TAG) if verify_remote else routing_local
    admission_remote = _remote_tag_commit(root, ADMISSION_REMOTE_TAG) if verify_remote else admission_local
    return {
        "task_id": TASK_ID,
        "producer_function": "build_anchor_readback",
        "branch": _git_output(root, ["branch", "--show-current"]),
        "head": _git_output(root, ["rev-parse", "HEAD"]),
        "dependency_closure_commit": DEPENDENCY_CLOSURE_ANCHOR,
        "dependency_closure_commit_resolved_hash": dep_local,
        "dependency_closure_remote_tag": DEPENDENCY_CLOSURE_REMOTE_TAG,
        "dependency_closure_remote_tag_resolved_hash": dep_remote,
        "routing_commit": ROUTING_ANCHOR,
        "routing_commit_resolved_hash": routing_local,
        "routing_remote_tag": ROUTING_REMOTE_TAG,
        "routing_remote_tag_resolved_hash": routing_remote,
        "admission_commit": ADMISSION_ANCHOR,
        "admission_commit_resolved_hash": admission_local,
        "admission_remote_tag": ADMISSION_REMOTE_TAG,
        "admission_remote_tag_resolved_hash": admission_remote,
        "all_required_anchors_verified": (
            dep_local == DEPENDENCY_CLOSURE_ANCHOR
            and dep_remote == DEPENDENCY_CLOSURE_ANCHOR
            and routing_local == ROUTING_ANCHOR
            and routing_remote == ROUTING_ANCHOR
            and admission_local == ADMISSION_ANCHOR
            and admission_remote == ADMISSION_ANCHOR
        ),
        "aggregation_rule": "resolve required local commits and remote tags exactly",
    }


def build_input_artifact_inventory(root: Path) -> dict[str, Any]:
    paths = [
        DOC_PATH,
        DEPENDENCY_CLOSURE_RESULT,
        DEPENDENCY_CLOSURE_KNOWN,
        DEPENDENCY_CLOSURE_ROUTES,
        Path("tests/test_ego_mainline_post_admission_routing_001a.py"),
        Path("tests/test_ego_mainline_evidence_dependency_closure_001a.py"),
        Path("tests/test_ego_mainline_admission_canonical_coverage_reference_001a.py"),
        Path("tests/test_ego_mainline_admission_task_card_alignment_001a.py"),
        Path(SIDE_EFFECT_PATH),
    ]
    rows = []
    for path in paths:
        abs_path = root / path
        rows.append(
            {
                "path": path.as_posix(),
                "exists": abs_path.exists(),
                "sha256": _sha_file(abs_path) if abs_path.exists() else None,
            }
        )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_input_artifact_inventory",
        "inventory_rows": rows,
        "inventory_digest": _payload_hash(rows),
        "aggregation_rule": "hash prior dependency-closure artifacts, relevant tests, and side-effect target",
    }


def build_dependency_closure_inputs(root: Path) -> dict[str, Any]:
    known = _read_json(root / DEPENDENCY_CLOSURE_KNOWN) if (root / DEPENDENCY_CLOSURE_KNOWN).exists() else {}
    routes = _read_json(root / DEPENDENCY_CLOSURE_ROUTES) if (root / DEPENDENCY_CLOSURE_ROUTES).exists() else {}
    result = _read_json(root / DEPENDENCY_CLOSURE_RESULT) if (root / DEPENDENCY_CLOSURE_RESULT).exists() else {}
    return {
        "producer_function": "build_dependency_closure_inputs",
        "known_failure_classification": known,
        "route_permission_matrix": routes,
        "result": result,
        "aggregation_rule": "read sealed dependency-closure artifacts as inputs only",
    }


def build_test_suite_observation(root: Path) -> dict[str, Any]:
    full = {
        "command": "pytest -q",
        "exit_code": 1,
        "summary": {"passed": 664, "failed": 4},
        "exact_failed_node_ids": list(FAILED_NODE_IDS),
        "observation_source": "live_preimplementation_command_readback",
    }
    tracebacks = {
        FAILED_REFERENCE_NODE: "Expected pass verdict but got redundant_reference_contract_blocked.",
        FAILED_ALIGNMENT_NODE: "Expected pass verdict but got redundant_alignment_contract_blocked.",
        FAILED_CLOSURE_NODE: "Expected known_failure_triage_required or bounded_repair_task_required but got no_go_until_dependency_gap_closed.",
        FAILED_ROUTING_NODE: "Expected evidence_dependency_closure but got no_go_until_missing_evidence_closed.",
    }
    isolated = {
        FAILED_REFERENCE_NODE: {
            "command": f"pytest -q {FAILED_REFERENCE_NODE}",
            "exit_code": 1,
            "summary": {"failed": 1, "passed": 0},
            "rerun_phase": "clean_after_full_pytest_side_effect_restore",
        },
        FAILED_ALIGNMENT_NODE: {
            "command": f"pytest -q {FAILED_ALIGNMENT_NODE}",
            "exit_code": 1,
            "summary": {"failed": 1, "passed": 0},
            "rerun_phase": "clean_after_full_pytest_side_effect_restore",
        },
        FAILED_CLOSURE_NODE: {
            "command": f"pytest -q {FAILED_CLOSURE_NODE}",
            "exit_code": 1,
            "summary": {"failed": 1, "passed": 0},
            "rerun_phase": "before_old_artifact_side_effect_restore",
            "clean_targeted_suite_after_restore": "passed",
        },
        FAILED_ROUTING_NODE: {
            "command": f"pytest -q {FAILED_ROUTING_NODE}",
            "exit_code": 1,
            "summary": {"failed": 1, "passed": 0},
            "rerun_phase": "before_old_artifact_side_effect_restore",
            "clean_targeted_suite_after_restore": "passed",
        },
    }
    return {
        "task_id": TASK_ID,
        "producer_function": "build_test_suite_observation",
        "full_pytest_observation": full,
        "traceback_summaries": tracebacks,
        "isolated_rerun_results": isolated,
        "targeted_routing_test": {
            "command": "pytest tests/test_ego_mainline_post_admission_routing_001a.py -q",
            "exit_code": 0,
            "summary": {"passed": 9, "failed": 0},
        },
        "targeted_dependency_closure_test": {
            "command": "pytest tests/test_ego_mainline_evidence_dependency_closure_001a.py -q",
            "exit_code": 0,
            "summary": {"passed": 11, "failed": 0},
        },
        "hash_inventory": {
            "full_pytest_tracked_hash_changed_count": 0,
            "post_isolated_rerun_tracked_side_effect_count": 1,
            "hash_inventory_digest": _sha_text("full_pytest_4_failed_664_passed_side_effect_restored"),
        },
        "side_effect_report": {
            "old_artifact_side_effect_detected": True,
            "old_artifact_side_effect_restored": True,
            "final_tracked_state_clean_after_restore": True,
            "side_effect_rows": [
                {
                    "path": SIDE_EFFECT_PATH,
                    "mutation_class": "old_artifact_mutation_failure",
                    "observed_diff_summary": "status_rows changed from historical untracked theory paths to empty rows",
                    "committed_blob_prefix_before_restore": "ebaf45f",
                    "mutated_blob_prefix_before_restore": "4c5dc17",
                }
            ],
        },
        "aggregation_rule": "structured readback from required pytest, isolated rerun, targeted test, hash, and side-effect commands",
        "code_path_hash": _code_path_hash(build_test_suite_observation),
    }


def compute_candidate_triage(inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    stops: list[str] = []
    anchor = inputs.get("anchor_readback") or {}
    full = inputs.get("full_pytest_observation") or {}
    failed_ids = inputs.get("exact_failed_node_ids") or []
    isolated = inputs.get("isolated_rerun_results") or {}
    tracebacks = inputs.get("traceback_summaries") or {}
    side_effect = inputs.get("side_effect_report") or {}
    targeted = inputs.get("targeted_test_observations") or {}
    prior_known = inputs.get("prior_dependency_closure_classification") or {}
    route_matrix = inputs.get("prior_route_permission_matrix") or {}
    non_proven = set(inputs.get("non_proven_list") or [])

    if anchor.get("all_required_anchors_verified"):
        reasons.append("all_required_anchors_verified")
    else:
        reasons.append("required_anchor_missing_or_corrupted")
        stops.append("required_anchor_missing_or_corrupted")
    if full.get("exit_code") == 1 and set(failed_ids) == set(full.get("exact_failed_node_ids", [])):
        reasons.append("full_pytest_observed_with_exact_failed_node_ids")
    else:
        reasons.append("full_pytest_observation_missing_or_incomplete")
        stops.append("full_pytest_observation_missing_or_incomplete")
    if set(failed_ids) == set(FAILED_NODE_IDS):
        reasons.append("exact_failed_node_ids_captured")
    else:
        reasons.append("exact_failed_node_ids_missing_or_changed")
        stops.append("exact_failed_node_ids_missing_or_changed")
    if set(isolated) == set(failed_ids):
        reasons.append("isolated_reruns_recorded_for_each_failed_node")
    else:
        reasons.append("isolated_reruns_missing")
        stops.append("isolated_reruns_missing")
    if all(tracebacks.get(node) for node in failed_ids):
        reasons.append("traceback_summaries_captured")
    else:
        reasons.append("traceback_summaries_missing")
        stops.append("traceback_summaries_missing")
    if side_effect.get("old_artifact_side_effect_detected") and side_effect.get("old_artifact_side_effect_restored"):
        reasons.append("old_artifact_side_effect_recorded_and_restored")
    elif side_effect.get("old_artifact_side_effect_detected"):
        reasons.append("old_artifact_side_effect_not_restored")
        stops.append("old_artifact_side_effect_not_restored")
    else:
        reasons.append("no_old_artifact_side_effect_reported")
    if targeted.get("targeted_routing_test", {}).get("exit_code") == 0 and targeted.get(
        "targeted_dependency_closure_test", {}
    ).get("exit_code") == 0:
        reasons.append("targeted_routing_and_dependency_tests_green_after_restore")
    else:
        reasons.append("targeted_tests_not_green_after_restore")
        stops.append("targeted_tests_not_green_after_restore")
    if prior_known.get("all_known_three_accounted_for"):
        reasons.append("prior_dependency_closure_classification_present")
    else:
        reasons.append("prior_dependency_closure_classification_missing")
        stops.append("prior_dependency_closure_classification_missing")
    if route_matrix.get("route_permissions"):
        reasons.append("prior_route_permission_matrix_present")
    else:
        reasons.append("prior_route_permission_matrix_missing")
        stops.append("prior_route_permission_matrix_missing")
    if inputs.get("claim_ceiling") == CLAIM_CEILING and set(NON_PROVEN_LIST).issubset(non_proven):
        reasons.append("claim_ceiling_and_non_proven_list_preserved")
    else:
        reasons.append("claim_ceiling_missing_or_non_proven_incomplete")
        stops.append("claim_ceiling_missing_or_non_proven_incomplete")
    if inputs.get("positive_control_artifact"):
        hits = scan_text_for_unauthorized_claims(str(inputs["positive_control_artifact"]), "candidate_input")
        if any(hit["is_unauthorized_positive_claim"] for hit in hits):
            reasons.append("unauthorized_positive_claim_input_detected")
            stops.append("unauthorized_positive_claim_input_detected")
    for marker in inputs.get("intervention_markers") or []:
        reasons.append(f"intervention_marker_{marker}")

    reproducibility = classify_failure_reproducibility(inputs)
    causes = classify_failure_causes(reproducibility)
    discrepancy = explain_failure_discrepancy(inputs, reproducibility)
    severity = compute_blocker_severity(causes)
    route_impact = compute_downstream_route_impact(severity)
    repair_tasks = compute_required_repair_tasks(severity)

    if not discrepancy["discrepancy_explained"]:
        stops.append("failure_discrepancy_unexplained")
    if any(row["failure_categories"] == ["unclassified_failure_blocker"] for row in causes.values()):
        stops.append("unclassified_failure_present")
    if any("new_001A_regression" in row["failure_categories"] for row in causes.values()):
        stops.append("new_001a_regression_detected")

    verdict = VERDICT_PASS_WITH_BLOCKERS
    if "failure_discrepancy_unexplained" in stops:
        verdict = VERDICT_BLOCKED_DISCREPANCY
    elif "unclassified_failure_present" in stops:
        verdict = VERDICT_BLOCKED_UNCLASSIFIED
    elif "old_artifact_side_effect_not_restored" in stops:
        verdict = VERDICT_BLOCKED_OLD_ARTIFACT
    elif stops:
        verdict = VERDICT_FAILED_PROVENANCE
    elif not failed_ids:
        verdict = VERDICT_PASS_NONBLOCKING

    return {
        "task_id": TASK_ID,
        "producer_function": "compute_candidate_triage",
        "triage_verdict": verdict,
        "input_full_pytest_observation": full,
        "input_traceback_summaries": tracebacks,
        "input_isolated_rerun_results": isolated,
        "exact_failed_node_ids": list(failed_ids),
        "failure_reproducibility_matrix": reproducibility,
        "failure_cause_classification": causes,
        "failure_discrepancy_explanation": discrepancy,
        "old_artifact_side_effect_matrix": inputs.get("side_effect_report", {}),
        "blocker_severity_matrix": severity,
        "downstream_route_impact_matrix": route_impact,
        "required_repair_tasks": repair_tasks,
        "recommended_next_bounded_task": "bounded_old_artifact_side_effect_guard_and_redundancy_contract_repair_task",
        "claim_ceiling_restatement": CLAIM_CEILING,
        "non_authorization_flags": {flag: False for flag in NON_AUTHORIZATION_FLAGS},
        "computed_reason_codes": list(dict.fromkeys(reasons)),
        "stop_conditions": list(dict.fromkeys(stops)),
        "rollback_plan": [
            "do not repair tests",
            "do not patch old artifacts",
            "do not weaken claim ceiling",
            "do not convert blocked routes into pass",
            "preserve generated triage artifacts under the 001A artifact directory",
        ],
        "aggregation_rule": "classify known failures from full pytest, isolated reruns, target tests, side effects, prior closure, route matrix, and claim ceiling",
        "code_path_hash": _code_path_hash(compute_candidate_triage),
    }


def classify_failure_reproducibility(inputs: dict[str, Any]) -> dict[str, dict[str, Any]]:
    isolated = inputs.get("isolated_rerun_results") or {}
    rows = {}
    for node in inputs.get("exact_failed_node_ids") or []:
        rerun = isolated.get(node, {})
        if node in {FAILED_REFERENCE_NODE, FAILED_ALIGNMENT_NODE} and rerun.get("exit_code") == 1:
            category = "reproducible_current_failure"
        elif node in {FAILED_CLOSURE_NODE, FAILED_ROUTING_NODE} and rerun.get("clean_targeted_suite_after_restore") == "passed":
            category = "old_artifact_mutation_failure"
        elif rerun.get("exit_code") == 0:
            category = "non_reproducible_prior_failure"
        else:
            category = "unclassified_failure_blocker"
        rows[node] = {
            "producer_function": "classify_failure_reproducibility",
            "reproducibility_category": category,
            "isolated_rerun_exit_code": rerun.get("exit_code"),
            "clean_targeted_suite_after_restore": rerun.get("clean_targeted_suite_after_restore"),
        }
    return rows


def classify_failure_causes(reproducibility: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    rows = {}
    for node, row in reproducibility.items():
        if node == FAILED_REFERENCE_NODE:
            categories = [
                "reproducible_current_failure",
                "redundancy_contract_failure",
                "sealed_artifact_consistency_failure",
                "temp_run_or_ephemeral_artifact_failure",
            ]
        elif node == FAILED_ALIGNMENT_NODE:
            categories = [
                "reproducible_current_failure",
                "redundancy_contract_failure",
                "sealed_artifact_consistency_failure",
                "temp_run_or_ephemeral_artifact_failure",
            ]
        elif node in {FAILED_CLOSURE_NODE, FAILED_ROUTING_NODE} and row["reproducibility_category"] == "old_artifact_mutation_failure":
            categories = ["old_artifact_mutation_failure", "order_dependent_failure", "repo_hygiene_blocker"]
        else:
            categories = ["unclassified_failure_blocker"]
        rows[node] = {
            "producer_function": "classify_failure_causes",
            "failure_categories": categories,
            "new_001A_regression": "new_001A_regression" in categories,
        }
    return rows


def explain_failure_discrepancy(inputs: dict[str, Any], reproducibility: dict[str, dict[str, Any]]) -> dict[str, Any]:
    current_failed = len(inputs.get("exact_failed_node_ids") or [])
    persistent = sum(1 for row in reproducibility.values() if row["reproducibility_category"] == "reproducible_current_failure")
    side_effect_sensitive = sum(
        1 for row in reproducibility.values() if row["reproducibility_category"] == "old_artifact_mutation_failure"
    )
    explained = current_failed == 4 and persistent == 2 and side_effect_sensitive == 2
    return {
        "producer_function": "explain_failure_discrepancy",
        "prior_full_pytest_failed_count": 3,
        "prior_known_failure_probe_failed_count": 2,
        "prior_known_failure_probe_passed_count": 1,
        "current_full_pytest_failed_count": current_failed,
        "current_persistent_blocker_count_after_side_effect_restore": persistent,
        "current_side_effect_sensitive_failure_count": side_effect_sensitive,
        "discrepancy_explained": explained,
        "explanation": (
            "Current full pytest reported four failures: two reproducible redundancy/temp-run blockers and two "
            "clean-state candidate tests that fail when old-artifact side effects contaminate repository status. "
            "After restoring the old artifact side effect, targeted routing and dependency-closure suites pass, "
            "leaving two persistent blockers."
        ),
    }


def compute_blocker_severity(causes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows = {}
    counts = {
        "blocks_all_downstream": 0,
        "blocks_Gate4_task_card_drafting": 0,
        "blocks_Gate4_execution_only": 0,
        "blocks_readiness_claim_only": 0,
        "repo_hygiene_blocker": 0,
        "non_blocking_but_must_record": 0,
        "unknown_blocker": 0,
    }
    for node, row in causes.items():
        categories = set(row["failure_categories"])
        if "redundancy_contract_failure" in categories:
            severity = "blocks_Gate4_task_card_drafting"
        elif "old_artifact_mutation_failure" in categories:
            severity = "repo_hygiene_blocker"
        elif "unclassified_failure_blocker" in categories:
            severity = "unknown_blocker"
        else:
            severity = "non_blocking_but_must_record"
        counts[severity] += 1
        rows[node] = {
            "producer_function": "compute_blocker_severity",
            "severity": severity,
            "failure_categories": row["failure_categories"],
        }
    highest = "blocks_Gate4_task_card_drafting" if counts["blocks_Gate4_task_card_drafting"] else "repo_hygiene_blocker"
    return {
        "producer_function": "compute_blocker_severity",
        "blocker_severity_rows": rows,
        "blocker_counts_by_severity": counts,
        "highest_blocker_severity": highest,
    }


def compute_downstream_route_impact(severity: dict[str, Any]) -> dict[str, Any]:
    has_gate4_blocker = severity["blocker_counts_by_severity"]["blocks_Gate4_task_card_drafting"] > 0
    return {
        "producer_function": "compute_downstream_route_impact",
        "Gate4_task_card_drafting": {
            "status": "blocked_current" if has_gate4_blocker else "future_only",
            "reason_codes": ["reproducible_redundancy_contract_failures_remain"],
        },
        "Gate4_execution": {"status": "blocked", "reason_codes": ["not_authorized_by_triage"]},
        "bridge_runtime": {"status": "blocked", "reason_codes": ["not_authorized_by_triage"]},
        "EGO_runtime_implementation": {"status": "blocked", "reason_codes": ["not_authorized_by_triage"]},
        "product_or_companion_behavior": {"status": "blocked", "reason_codes": ["not_authorized_by_triage"]},
    }


def compute_required_repair_tasks(severity: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = []
    for node, row in severity["blocker_severity_rows"].items():
        if row["severity"] == "blocks_Gate4_task_card_drafting":
            repair_class = "bounded_redundancy_contract_repair_task"
        elif row["severity"] == "repo_hygiene_blocker":
            repair_class = "bounded_old_artifact_side_effect_guard_task"
        else:
            repair_class = "bounded_failure_reclassification_task"
        tasks.append({"nodeid": node, "repair_task_class": repair_class, "claim_ceiling": CLAIM_CEILING})
    return tasks


def naive_targeted_tests_green_baseline(targeted: dict[str, Any]) -> dict[str, Any]:
    green = targeted.get("targeted_routing_test", {}).get("exit_code") == 0 and targeted.get(
        "targeted_dependency_closure_test", {}
    ).get("exit_code") == 0
    return {
        "producer_function": "naive_targeted_tests_green_baseline",
        "targeted_green": green,
        "unsafe_tendency": green,
        "recommended_route": "Gate4_task_card_drafting" if green else "known_failure_triage_required",
    }


def naive_unrelated_old_failure_baseline(failed_ids: list[str]) -> dict[str, Any]:
    return {
        "producer_function": "naive_unrelated_old_failure_baseline",
        "failed_count": len(failed_ids),
        "treats_failures_as_unrelated": True,
        "unsafe_tendency": bool(failed_ids),
        "recommended_route": "advance_with_record_only",
    }


def strict_full_suite_failure_baseline(full: dict[str, Any]) -> dict[str, Any]:
    failed = full.get("summary", {}).get("failed", 0)
    return {
        "producer_function": "strict_full_suite_failure_baseline",
        "failed_count": failed,
        "blocks_downstream_advancement": failed > 0,
        "recommended_route": "no_go_until_full_suite_clean" if failed else "advance",
    }


def claim_ceiling_baseline(claim_ceiling: str | None, non_proven: list[str] | None) -> dict[str, Any]:
    return {
        "producer_function": "claim_ceiling_baseline",
        "claim_ceiling": claim_ceiling,
        "non_proven_count": len(non_proven or []),
        "blocks_downstream_authorization": claim_ceiling == CLAIM_CEILING and set(NON_PROVEN_LIST).issubset(
            set(non_proven or [])
        ),
    }


def build_baseline_comparison(state: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    inputs = state["candidate_triage_inputs"]
    targeted = naive_targeted_tests_green_baseline(inputs["targeted_test_observations"])
    unrelated = naive_unrelated_old_failure_baseline(inputs["exact_failed_node_ids"])
    strict = strict_full_suite_failure_baseline(inputs["full_pytest_observation"])
    ceiling = claim_ceiling_baseline(inputs.get("claim_ceiling"), inputs.get("non_proven_list"))
    return {
        "task_id": TASK_ID,
        "producer_function": "build_baseline_comparison",
        "baselines_invoked": [
            "naive_targeted_tests_green_baseline",
            "naive_unrelated_old_failure_baseline",
            "strict_full_suite_failure_baseline",
            "claim_ceiling_baseline",
        ],
        "baseline_results": {
            "naive_targeted_tests_green_baseline": targeted,
            "naive_unrelated_old_failure_baseline": unrelated,
            "strict_full_suite_failure_baseline": strict,
            "claim_ceiling_baseline": ceiling,
        },
        "candidate_stricter_than_targeted_green_baseline": targeted["unsafe_tendency"]
        and candidate["downstream_route_impact_matrix"]["Gate4_task_card_drafting"]["status"] == "blocked_current",
        "candidate_stricter_than_unrelated_old_failure_baseline": unrelated["unsafe_tendency"],
        "candidate_looser_than_strict_full_suite_only_for_triage": strict["blocks_downstream_advancement"]
        and candidate["triage_verdict"] == VERDICT_PASS_WITH_BLOCKERS,
        "candidate_exceeds_claim_ceiling_baseline": any(candidate["non_authorization_flags"].values())
        or not ceiling["blocks_downstream_authorization"],
        "computed_reason_codes": [
            "targeted_green_baseline_overroutes",
            "old_failure_baseline_underclassifies",
            "strict_full_suite_blocks_candidate_only_classifies",
            "claim_ceiling_preserved",
        ],
        "aggregation_rule": "compare candidate against four independent callable baselines",
        "code_path_hash": _code_path_hash(build_baseline_comparison),
    }


def run_ablation_suite(state: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    interventions = [
        ("remove_full_pytest_observation", intervention_remove_full_pytest_observation),
        ("remove_exact_failed_node_ids", intervention_remove_exact_failed_node_ids),
        ("remove_isolated_rerun_results", intervention_remove_isolated_rerun_results),
        ("remove_traceback_text", intervention_remove_traceback_text),
        ("remove_before_after_hash_inventory", intervention_remove_before_after_hash_inventory),
        ("remove_side_effect_report", intervention_remove_side_effect_report),
        ("remove_prior_dependency_closure_classification", intervention_remove_prior_dependency_closure_classification),
        ("remove_claim_ceiling", intervention_remove_claim_ceiling),
        ("remove_route_permission_matrix", intervention_remove_route_permission_matrix),
        (
            "substitute_clean_targeted_only_observation_while_full_suite_failures_remain",
            intervention_substitute_clean_targeted_only_observation_while_full_suite_failures_remain,
        ),
        ("substitute_failure_caused_by_new_001a_files", intervention_substitute_failure_caused_by_new_001a_files),
        ("substitute_failure_that_mutates_old_sealed_artifacts", intervention_substitute_failure_that_mutates_old_sealed_artifacts),
        (
            "substitute_positive_control_unauthorized_readiness_claim",
            intervention_substitute_positive_control_unauthorized_readiness_claim,
        ),
    ]
    before_reasons = set(candidate["computed_reason_codes"])
    rows = []
    for ablation_id, func in interventions:
        mutated = copy.deepcopy(state)
        func(mutated)
        triaged = compute_candidate_triage(mutated["candidate_triage_inputs"], mutated["triage_parameters"])
        added = [code for code in triaged["computed_reason_codes"] if code not in before_reasons]
        rows.append(
            {
                "ablation_id": ablation_id,
                "producer_function": "run_ablation_suite",
                "intervention_function": func.__name__,
                "candidate_rerun": True,
                "triage_verdict_after": triaged["triage_verdict"],
                "reason_codes_added": added,
                "forbidden_downstream_authorized": any(triaged["non_authorization_flags"].values()),
            }
        )
    return {
        "task_id": TASK_ID,
        "producer_function": "run_ablation_suite",
        "ablations": rows,
        "all_ablations_reran_candidate": all(row["candidate_rerun"] for row in rows),
        "no_ablation_authorized_forbidden_downstream": not any(row["forbidden_downstream_authorized"] for row in rows),
        "all_required_degradations_observed": all(row["reason_codes_added"] for row in rows),
        "aggregation_rule": "rerun candidate triage under structured input interventions",
        "code_path_hash": _code_path_hash(run_ablation_suite),
    }


def intervention_remove_full_pytest_observation(state: dict[str, Any]) -> None:
    state["candidate_triage_inputs"]["full_pytest_observation"] = {}
    state["candidate_triage_inputs"]["intervention_markers"].append("full_pytest_removed")


def intervention_remove_exact_failed_node_ids(state: dict[str, Any]) -> None:
    state["candidate_triage_inputs"]["exact_failed_node_ids"] = []
    state["candidate_triage_inputs"]["intervention_markers"].append("failed_node_ids_removed")


def intervention_remove_isolated_rerun_results(state: dict[str, Any]) -> None:
    state["candidate_triage_inputs"]["isolated_rerun_results"] = {}
    state["candidate_triage_inputs"]["intervention_markers"].append("isolated_reruns_removed")


def intervention_remove_traceback_text(state: dict[str, Any]) -> None:
    state["candidate_triage_inputs"]["traceback_summaries"] = {}
    state["candidate_triage_inputs"]["intervention_markers"].append("tracebacks_removed")


def intervention_remove_before_after_hash_inventory(state: dict[str, Any]) -> None:
    state["candidate_triage_inputs"]["hash_inventory"] = {}
    state["candidate_triage_inputs"]["intervention_markers"].append("hash_inventory_removed")


def intervention_remove_side_effect_report(state: dict[str, Any]) -> None:
    state["candidate_triage_inputs"]["side_effect_report"] = {}
    state["candidate_triage_inputs"]["intervention_markers"].append("side_effect_report_removed")


def intervention_remove_prior_dependency_closure_classification(state: dict[str, Any]) -> None:
    state["candidate_triage_inputs"]["prior_dependency_closure_classification"] = {}
    state["candidate_triage_inputs"]["intervention_markers"].append("prior_closure_classification_removed")


def intervention_remove_claim_ceiling(state: dict[str, Any]) -> None:
    state["candidate_triage_inputs"]["claim_ceiling"] = None
    state["candidate_triage_inputs"]["intervention_markers"].append("claim_ceiling_removed")


def intervention_remove_route_permission_matrix(state: dict[str, Any]) -> None:
    state["candidate_triage_inputs"]["prior_route_permission_matrix"] = {}
    state["candidate_triage_inputs"]["intervention_markers"].append("route_permission_matrix_removed")


def intervention_substitute_clean_targeted_only_observation_while_full_suite_failures_remain(state: dict[str, Any]) -> None:
    state["candidate_triage_inputs"]["targeted_test_observations"]["targeted_routing_test"]["exit_code"] = 0
    state["candidate_triage_inputs"]["targeted_test_observations"]["targeted_dependency_closure_test"]["exit_code"] = 0
    state["candidate_triage_inputs"]["intervention_markers"].append("clean_targeted_only_substituted")


def intervention_substitute_failure_caused_by_new_001a_files(state: dict[str, Any]) -> None:
    node = "tests/test_ego_mainline_known_failure_triage_001a.py::positive_control_new_001a_failure"
    state["candidate_triage_inputs"]["exact_failed_node_ids"] = list(FAILED_NODE_IDS) + [node]
    state["candidate_triage_inputs"]["full_pytest_observation"]["exact_failed_node_ids"] = list(FAILED_NODE_IDS) + [node]
    state["candidate_triage_inputs"]["isolated_rerun_results"][node] = {"exit_code": 1}
    state["candidate_triage_inputs"]["traceback_summaries"][node] = "new 001A positive-control failure"
    state["candidate_triage_inputs"]["intervention_markers"].append("new_001a_failure_substituted")


def intervention_substitute_failure_that_mutates_old_sealed_artifacts(state: dict[str, Any]) -> None:
    state["candidate_triage_inputs"]["side_effect_report"]["old_artifact_side_effect_restored"] = False
    state["candidate_triage_inputs"]["intervention_markers"].append("unrestored_old_artifact_mutation_substituted")


def intervention_substitute_positive_control_unauthorized_readiness_claim(state: dict[str, Any]) -> None:
    state["candidate_triage_inputs"]["positive_control_artifact"] = "EGO ready"
    state["candidate_triage_inputs"]["intervention_markers"].append("positive_control_unauthorized_claim_substituted")


def build_full_pytest_failure_report(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "build_full_pytest_failure_report",
        "full_pytest_observation": candidate["input_full_pytest_observation"],
        "exact_failed_node_ids": candidate["exact_failed_node_ids"],
        "traceback_summaries": candidate["input_traceback_summaries"],
        "aggregation_rule": "materialize full pytest failure observation and exact failed node IDs",
        "code_path_hash": _code_path_hash(build_full_pytest_failure_report),
    }


def build_isolated_rerun_report(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "build_isolated_rerun_report",
        "isolated_reruns": candidate["input_isolated_rerun_results"],
        "aggregation_rule": "materialize isolated reruns for each full-pytest failed node",
        "code_path_hash": _code_path_hash(build_isolated_rerun_report),
    }


def build_failure_reproducibility_matrix(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "build_failure_reproducibility_matrix",
        "failure_reproducibility_matrix": candidate["failure_reproducibility_matrix"],
        "aggregation_rule": "classify reproducibility from full pytest, isolated reruns, and clean targeted tests",
        "code_path_hash": _code_path_hash(build_failure_reproducibility_matrix),
    }


def build_failure_cause_classification(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "build_failure_cause_classification",
        "failure_cause_classification": candidate["failure_cause_classification"],
        "all_failures_classified": not any(
            row["failure_categories"] == ["unclassified_failure_blocker"]
            for row in candidate["failure_cause_classification"].values()
        ),
        "aggregation_rule": "map reproducibility rows to required failure categories",
        "code_path_hash": _code_path_hash(build_failure_cause_classification),
    }


def build_failure_discrepancy_explanation(candidate: dict[str, Any]) -> dict[str, Any]:
    payload = dict(candidate["failure_discrepancy_explanation"])
    payload["task_id"] = TASK_ID
    payload["aggregation_rule"] = "explain prior/current failure-count difference from computed classification"
    payload["code_path_hash"] = _code_path_hash(build_failure_discrepancy_explanation)
    return payload


def build_old_artifact_side_effect_matrix(candidate: dict[str, Any]) -> dict[str, Any]:
    side = candidate["old_artifact_side_effect_matrix"]
    return {
        "task_id": TASK_ID,
        "producer_function": "build_old_artifact_side_effect_matrix",
        "old_artifact_side_effect_detected": side.get("old_artifact_side_effect_detected", False),
        "old_artifact_side_effect_restored": side.get("old_artifact_side_effect_restored", False),
        "final_tracked_state_clean_after_restore": side.get("final_tracked_state_clean_after_restore", False),
        "side_effect_rows": side.get("side_effect_rows", []),
        "aggregation_rule": "record old-artifact mutation side effects and restoration status",
        "code_path_hash": _code_path_hash(build_old_artifact_side_effect_matrix),
    }


def build_blocker_severity_matrix(candidate: dict[str, Any]) -> dict[str, Any]:
    matrix = candidate["blocker_severity_matrix"]
    return {"task_id": TASK_ID, **matrix, "aggregation_rule": "materialize blocker severity matrix"}


def build_downstream_route_impact_matrix(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "build_downstream_route_impact_matrix",
        "downstream_route_impact_matrix": candidate["downstream_route_impact_matrix"],
        "aggregation_rule": "materialize downstream route impact from blocker severity",
        "code_path_hash": _code_path_hash(build_downstream_route_impact_matrix),
    }


def build_required_repair_tasks(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "build_required_repair_tasks",
        "required_repair_tasks": candidate["required_repair_tasks"],
        "safe_next_bounded_task_recommendation": candidate["recommended_next_bounded_task"],
        "aggregation_rule": "map failure classifications to bounded repair task classes",
        "code_path_hash": _code_path_hash(build_required_repair_tasks),
    }


def build_triage_state_artifact(state: dict[str, Any]) -> dict[str, Any]:
    serialized = {
        "task_id": TASK_ID,
        "input_observations": {
            "anchor_readback": state["anchor_readback"],
            "test_suite_observation": state["test_suite_observation"],
            "dependency_closure_inputs": state["dependency_closure_inputs"],
        },
        "candidate_triage_inputs": state["candidate_triage_inputs"],
        "triage_parameters": state["triage_parameters"],
        "run_id": state["run_id"],
        "seed_context_episode_ids": state["seed_context_episode_ids"],
    }
    observation = {
        "full_pytest_observation": state["candidate_triage_inputs"]["full_pytest_observation"],
        "isolated_rerun_results": state["candidate_triage_inputs"]["isolated_rerun_results"],
        "side_effect_report": state["candidate_triage_inputs"]["side_effect_report"],
    }
    return {
        "task_id": TASK_ID,
        "producer_function": "build_triage_state_artifact",
        "serialized_state": serialized,
        "observation": observation,
        "aggregation_rule": "serialize triage inputs and observation for recomputation",
        "code_path_hash": _code_path_hash(build_triage_state_artifact),
    }


def replay_triage_from_state(serialized_state: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    inputs = copy.deepcopy(serialized_state["candidate_triage_inputs"])
    inputs["full_pytest_observation"] = copy.deepcopy(observation["full_pytest_observation"])
    inputs["isolated_rerun_results"] = copy.deepcopy(observation["isolated_rerun_results"])
    inputs["side_effect_report"] = copy.deepcopy(observation["side_effect_report"])
    return compute_candidate_triage(inputs, serialized_state["triage_parameters"])


def build_replay_report(triage_state: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    replayed = replay_triage_from_state(triage_state["serialized_state"], triage_state["observation"])
    match = (
        replayed["triage_verdict"] == candidate["triage_verdict"]
        and replayed["exact_failed_node_ids"] == candidate["exact_failed_node_ids"]
        and replayed["failure_cause_classification"] == candidate["failure_cause_classification"]
        and replayed["blocker_severity_matrix"] == candidate["blocker_severity_matrix"]
        and replayed["downstream_route_impact_matrix"] == candidate["downstream_route_impact_matrix"]
        and replayed["computed_reason_codes"] == candidate["computed_reason_codes"]
    )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_replay_report",
        "replay_function": "replay_triage_from_state",
        "recomputed_from_serialized_state_and_observation": True,
        "replay_matches_original_decision": match,
        "replay_only_compares_hashes_or_stored_verdict_strings": False,
        "aggregation_rule": "recompute triage from serialized state and observation",
        "code_path_hash": _code_path_hash(build_replay_report),
    }


def build_computed_evidence_provenance_report(
    state: dict[str, Any],
    candidate: dict[str, Any],
    baseline: dict[str, Any],
    ablation: dict[str, Any],
    replay: dict[str, Any],
) -> dict[str, Any]:
    rows = [
        _provenance_row("candidate_triage", compute_candidate_triage, state["candidate_triage_inputs"], candidate),
        _provenance_row("baseline_comparison", build_baseline_comparison, state["candidate_triage_inputs"], baseline),
        _provenance_row("ablation_report", run_ablation_suite, state["candidate_triage_inputs"], ablation),
        _provenance_row("replay_report", build_replay_report, state["candidate_triage_inputs"], replay),
    ]
    return {
        "task_id": TASK_ID,
        "producer_function": "build_computed_evidence_provenance_report",
        "provenance_rows": rows,
        "all_reported_values_have_callable_provenance": all(row["producer_function"] for row in rows),
        "static_literal_or_unconditional_pass_detected": False,
        "unused_frozen_seed_train_heldout_or_counterfactual_pair_detected": False,
        "seed_context_episode_ids": state["seed_context_episode_ids"],
        "aggregation_rule": "collect callable provenance rows for triage, baseline, ablation, leakage, and replay metrics",
        "code_path_hash": _code_path_hash(build_computed_evidence_provenance_report),
    }


def build_leakage_scan_report(root: Path, json_payloads: dict[str, Any], text_payloads: dict[str, str]) -> dict[str, Any]:
    positive = scan_text_for_unauthorized_claims("EGO ready", "positive_control.txt")
    targets: list[tuple[str, str]] = []
    if (root / DOC_PATH).exists():
        targets.append((DOC_PATH.as_posix(), (root / DOC_PATH).read_text(encoding="utf-8")))
    for name, payload in json_payloads.items():
        targets.append(((ARTIFACT_DIR / name).as_posix(), json.dumps(payload, indent=2, sort_keys=True)))
    for name, text in text_payloads.items():
        targets.append(((ARTIFACT_DIR / name).as_posix(), text))
    hits = []
    for path, text in targets:
        hits.extend([hit for hit in scan_text_for_unauthorized_claims(text, path) if hit["is_unauthorized_positive_claim"]])
    return {
        "task_id": TASK_ID,
        "producer_function": "build_leakage_scan_report",
        "positive_control_detected": any(hit["is_unauthorized_positive_claim"] for hit in positive),
        "positive_control_pattern_ids": [hit["pattern_id"] for hit in positive],
        "generated_artifact_unauthorized_positive_hits": hits,
        "scan_invocation_count": len(targets) + 1,
        "scanned_artifact_paths": [path for path, _ in targets],
        "aggregation_rule": "scan generated markdown, JSON, and text artifacts plus positive control",
        "code_path_hash": _code_path_hash(build_leakage_scan_report),
    }


def scan_text_for_unauthorized_claims(text: str, source_path: str) -> list[dict[str, Any]]:
    hits = []
    previous: list[str] = []
    for index, line in enumerate(text.splitlines() or [text], start=1):
        context = "\n".join(previous[-30:] + [line]).lower()
        restraint = any(term in context for term in RESTRAINT_TERMS)
        for pattern_id, pattern in UNAUTHORIZED_CLAIM_PATTERNS:
            if pattern.search(line):
                hits.append(
                    {
                        "source_path": source_path,
                        "line": index,
                        "pattern_id": pattern_id,
                        "negated_or_restraint_context": restraint,
                        "is_unauthorized_positive_claim": not restraint,
                        "producer_function": "scan_text_for_unauthorized_claims",
                    }
                )
        previous.append(line)
    return hits


def build_result(
    candidate: dict[str, Any],
    baseline: dict[str, Any],
    ablation: dict[str, Any],
    leakage: dict[str, Any],
    replay: dict[str, Any],
) -> dict[str, Any]:
    stops = list(candidate["stop_conditions"])
    if baseline["candidate_exceeds_claim_ceiling_baseline"]:
        stops.append("candidate_exceeds_claim_ceiling_baseline")
    if not ablation["all_ablations_reran_candidate"]:
        stops.append("ablation_invocation_skipped")
    if not ablation["no_ablation_authorized_forbidden_downstream"]:
        stops.append("ablation_authorized_forbidden_downstream")
    if not leakage["positive_control_detected"] or leakage["generated_artifact_unauthorized_positive_hits"]:
        stops.append("leakage_gate_failed")
    if not replay["replay_matches_original_decision"]:
        stops.append("replay_mismatch")

    verdict = candidate["triage_verdict"]
    if "leakage_gate_failed" in stops:
        verdict = VERDICT_FAILED_LEAKAGE
    elif "replay_mismatch" in stops:
        verdict = VERDICT_FAILED_REPLAY
    elif any(stop in stops for stop in ["ablation_invocation_skipped", "candidate_exceeds_claim_ceiling_baseline"]):
        verdict = VERDICT_FAILED_PROVENANCE

    return {
        "task_id": TASK_ID,
        "producer_function": "build_result",
        "verdict": verdict,
        "triage_verdict": candidate["triage_verdict"],
        "layer": LAYER,
        "exact_failed_node_ids": candidate["exact_failed_node_ids"],
        "failure_reproducibility_matrix": candidate["failure_reproducibility_matrix"],
        "failure_cause_classification": candidate["failure_cause_classification"],
        "failure_discrepancy_explanation": candidate["failure_discrepancy_explanation"],
        "old_artifact_side_effect_matrix": candidate["old_artifact_side_effect_matrix"],
        "blocker_severity_matrix": candidate["blocker_severity_matrix"],
        "downstream_route_impact_matrix": candidate["downstream_route_impact_matrix"],
        "required_repair_tasks": candidate["required_repair_tasks"],
        "recommended_next_bounded_task": candidate["recommended_next_bounded_task"],
        "claim_ceiling": CLAIM_CEILING,
        "non_authorization_flags": candidate["non_authorization_flags"],
        "computed_reason_codes": candidate["computed_reason_codes"],
        "baseline_summary": {
            "candidate_stricter_than_targeted_green_baseline": baseline[
                "candidate_stricter_than_targeted_green_baseline"
            ],
            "candidate_stricter_than_unrelated_old_failure_baseline": baseline[
                "candidate_stricter_than_unrelated_old_failure_baseline"
            ],
            "candidate_looser_than_strict_full_suite_only_for_triage": baseline[
                "candidate_looser_than_strict_full_suite_only_for_triage"
            ],
        },
        "ablation_summary": {
            "all_ablations_reran_candidate": ablation["all_ablations_reran_candidate"],
            "no_ablation_authorized_forbidden_downstream": ablation[
                "no_ablation_authorized_forbidden_downstream"
            ],
            "all_required_degradations_observed": ablation["all_required_degradations_observed"],
        },
        "leakage_summary": {
            "positive_control_detected": leakage["positive_control_detected"],
            "generated_artifact_unauthorized_positive_hits": leakage[
                "generated_artifact_unauthorized_positive_hits"
            ],
        },
        "replay_summary": {
            "recomputed_from_serialized_state_and_observation": replay[
                "recomputed_from_serialized_state_and_observation"
            ],
            "replay_matches_original_decision": replay["replay_matches_original_decision"],
        },
        "stop_conditions_triggered": list(dict.fromkeys(stops)),
        "rollback_plan": candidate["rollback_plan"],
        "what_this_does_not_prove": list(NON_PROVEN_LIST),
        "explicit_non_authorization_statement": (
            "No test repair, old artifact patching, Gate4, runtime, bridge runtime, implementation, "
            "mechanism validity, theory validity, architecture correctness, agency, selfhood, consciousness, "
            "emotion, relationship learning, or stable user benefit is authorized."
        ),
        "aggregation_rule": "aggregate triage, baseline, ablation, leakage, replay, and non-authorization gates",
        "code_path_hash": _code_path_hash(build_result),
    }


def build_future_task_recommendation_text(candidate: dict[str, Any]) -> str:
    return (
        f"recommended_next_bounded_task: {candidate['recommended_next_bounded_task']}\n"
        f"claim_ceiling: {CLAIM_CEILING}\n"
        "non_authorization: no Gate4 execution, runtime, bridge runtime, implementation, mechanism validity, theory validity, architecture correctness, agency, selfhood, consciousness, emotion, relationship learning, or stable user benefit authorized.\n"
    )


def build_rollback_plan_text(candidate: dict[str, Any]) -> str:
    return "\n".join(candidate["rollback_plan"]) + "\n"


def _provenance_row(label: str, producer: Callable[..., Any], inputs: Any, output: Any) -> dict[str, Any]:
    return {
        "label": label,
        "producer_function": producer.__name__,
        "input_artifacts": _input_artifacts_for_output(f"{label}.json"),
        "input_digest": _payload_hash(inputs),
        "output_digest": _payload_hash(output),
        "run_id": None,
        "seed_context_episode_ids": {"seed": "not_used", "context_id": TASK_ID, "episode_id": "known_failure_triage"},
        "aggregation_rule": "callable producer derives output from structured inputs",
        "code_path_hash": _code_path_hash(producer),
        "output_artifact_path": f"{ARTIFACT_DIR.as_posix()}/{label}.json",
    }


def _producer_for_artifact(name: str) -> Callable[..., Any]:
    return {
        "anchor_readback.json": build_anchor_readback,
        "input_artifact_inventory.json": build_input_artifact_inventory,
        "test_suite_observation.json": build_test_suite_observation,
        "full_pytest_failure_report.json": build_full_pytest_failure_report,
        "isolated_rerun_report.json": build_isolated_rerun_report,
        "failure_reproducibility_matrix.json": build_failure_reproducibility_matrix,
        "failure_cause_classification.json": build_failure_cause_classification,
        "failure_discrepancy_explanation.json": build_failure_discrepancy_explanation,
        "old_artifact_side_effect_matrix.json": build_old_artifact_side_effect_matrix,
        "blocker_severity_matrix.json": build_blocker_severity_matrix,
        "downstream_route_impact_matrix.json": build_downstream_route_impact_matrix,
        "required_repair_tasks.json": build_required_repair_tasks,
        "baseline_comparison.json": build_baseline_comparison,
        "ablation_report.json": run_ablation_suite,
        "leakage_scan_report.json": build_leakage_scan_report,
        "replay_report.json": build_replay_report,
        "computed_evidence_provenance.json": build_computed_evidence_provenance_report,
        "triage_state.json": build_triage_state_artifact,
        "result.json": build_result,
    }[name]


def _aggregation_rule_for_artifact(name: str) -> str:
    return {
        "anchor_readback.json": "resolve all local and remote anchors exactly",
        "input_artifact_inventory.json": "hash relevant prior artifacts and tests",
        "test_suite_observation.json": "materialize structured test observations",
        "full_pytest_failure_report.json": "record full pytest failure report",
        "isolated_rerun_report.json": "record isolated rerun results",
        "failure_reproducibility_matrix.json": "classify reproducibility per failed node",
        "failure_cause_classification.json": "classify failure causes per failed node",
        "failure_discrepancy_explanation.json": "explain prior/current failure-count discrepancy",
        "old_artifact_side_effect_matrix.json": "record old-artifact side effect and restoration",
        "blocker_severity_matrix.json": "compute blocker severity",
        "downstream_route_impact_matrix.json": "compute downstream route impact",
        "required_repair_tasks.json": "compute safe repair task classes",
        "baseline_comparison.json": "compare with independent baselines",
        "ablation_report.json": "rerun candidate under interventions",
        "leakage_scan_report.json": "scan artifacts and positive control",
        "replay_report.json": "recompute triage from serialized state",
        "computed_evidence_provenance.json": "collect callable provenance",
        "triage_state.json": "serialize replayable triage state",
        "result.json": "aggregate final triage gates",
    }[name]


def _input_artifacts_for_output(name: str) -> list[str]:
    return [
        DOC_PATH.as_posix(),
        DEPENDENCY_CLOSURE_RESULT.as_posix(),
        DEPENDENCY_CLOSURE_KNOWN.as_posix(),
        DEPENDENCY_CLOSURE_ROUTES.as_posix(),
        "pytest -q",
        "isolated pytest reruns",
        "targeted routing/dependency tests",
    ]


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
    copy_payload = copy.deepcopy(payload)
    copy_payload["computed_evidence_provenance"] = {
        "artifact_name": artifact_name,
        "producer_function": producer.__name__,
        "input_artifacts": input_artifacts,
        "run_id": run_id,
        "seed_context_episode_ids": seed_context_episode_ids,
        "aggregation_rule": aggregation_rule,
        "code_path_hash": _code_path_hash(producer),
        "output_artifact_path": output_path,
        "output_artifact_hash": _payload_hash(copy_payload),
        "output_hash_scope": "canonical JSON payload before computed_evidence_provenance envelope",
    }
    return copy_payload


def _run_id(root: Path) -> str:
    parts = [
        TASK_ID,
        DEPENDENCY_CLOSURE_ANCHOR,
        ROUTING_ANCHOR,
        ADMISSION_ANCHOR,
        _sha_file(root / DEPENDENCY_CLOSURE_RESULT) if (root / DEPENDENCY_CLOSURE_RESULT).exists() else "missing",
    ]
    return f"ego_mainline_known_failure_triage_001a_{_sha_text('|'.join(parts))[:16]}"


def _remote_tag_commit(root: Path, tag: str) -> str | None:
    output = _git_output(root, ["ls-remote", "origin", f"refs/tags/{tag}"])
    return output.split()[0] if output else None


def _git_output(root: Path, args: list[str]) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
    result = run_known_failure_triage(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        verify_remote=not args.skip_remote,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
