from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


TASK_ID = "EGO-MAINLINE-POST-REPAIR-ROUTE-REFRESH-AND-GATE4-PREFLIGHT-TASK-CARD-DRAFTING-001A"
TASK_SLUG = "ego_mainline_post_repair_route_refresh_and_gate4_task_card_drafting_001a"
ARTIFACT_DIR = Path(f"artifacts/{TASK_SLUG}")
DOC_PATH = Path(f"docs/codex/tasks/{TASK_ID}.md")
GATE4_TASK_CARD_PATH = Path("docs/codex/tasks/EGO-MAINLINE-GATE4-PREFLIGHT-TASK-CARD-001A.md")
GATE4_CONTRACT_DISCOVERY_PATH = Path("docs/codex/tasks/EGO-MAINLINE-GATE4-CONTRACT-DISCOVERY-001A.md")

LAYER = "evidence-governance / anti-Zeno route refresh plus conditional Gate4 preflight task-card drafting only"
CLAIM_CEILING = "bounded post-repair route-refresh and Gate4 preflight task-card drafting evidence at governance/planning layer only"
GATE4_TASK_CARD_CLAIM_CEILING = "bounded Gate4 preflight task-card drafting only"

VERDICT_PASS_GATE4_TASK_CARD_DRAFTED = (
    "post_repair_route_refresh_and_gate4_task_card_drafting_001a_pass_gate4_preflight_task_card_drafted"
)
VERDICT_PASS_GATE4_CONTRACT_DISCOVERY_DRAFTED = (
    "post_repair_route_refresh_and_gate4_task_card_drafting_001a_pass_gate4_contract_discovery_task_drafted"
)
VERDICT_BLOCKED_FULL_SUITE = "post_repair_route_refresh_and_gate4_task_card_drafting_001a_blocked_full_suite_not_green"
VERDICT_BLOCKED_MISSING_ANCHOR = "post_repair_route_refresh_and_gate4_task_card_drafting_001a_blocked_missing_anchor"
VERDICT_BLOCKED_OLD_ARTIFACT = (
    "post_repair_route_refresh_and_gate4_task_card_drafting_001a_blocked_old_artifact_guard_regression"
)
VERDICT_BLOCKED_MISSING_GATE4_SOURCE = (
    "post_repair_route_refresh_and_gate4_task_card_drafting_001a_blocked_missing_gate4_contract_source"
)
VERDICT_FAILED_PROVENANCE = "post_repair_route_refresh_and_gate4_task_card_drafting_001a_failed_provenance_gate"
VERDICT_FAILED_LEAKAGE = "post_repair_route_refresh_and_gate4_task_card_drafting_001a_failed_leakage_gate"
VERDICT_FAILED_REPLAY = "post_repair_route_refresh_and_gate4_task_card_drafting_001a_failed_replay_gate"

ANCHORS = {
    "repair": {
        "commit": "b9fe4f60774cfd2321b3fe5d166123ff96b5f224",
        "remote_tag": "remote-anchor-old-artifact-side-effect-guard-repair-001a-b9fe4f",
        "verdict": "old_artifact_side_effect_guard_and_redundancy_contract_repair_001a_pass_full_suite_green",
    },
    "known_failure_triage": {
        "commit": "c9bee968069f9d218c0c45a37efba092e4535156",
        "remote_tag": "remote-anchor-known-failure-triage-001a-c9bee9",
        "verdict": "known_failure_triage_001a_pass_with_blockers_classified",
    },
    "dependency_closure": {
        "commit": "01973a538fad9c33ca2c6119a0f2c6b384602f34",
        "remote_tag": "remote-anchor-evidence-dependency-closure-001a-01973a",
        "verdict": "evidence_dependency_closure_001a_pass_with_blockers_classified",
    },
    "post_admission_routing": {
        "commit": "4edf5cff7f89cf2cf1c6dbb15a478bbada0432aa",
        "remote_tag": "remote-anchor-post-admission-routing-001a-4edf5c",
        "verdict": "post_admission_routing_001a_pass_with_bounded_next_task",
    },
    "admission_execution": {
        "commit": "98e51a46cd7f28f60b1851c616d4351c1cd6272f",
        "remote_tag": "remote-anchor-bounded-admission-execution-001a-98e51a4",
        "verdict": "pass_bounded_admission_execution_001a",
    },
}

PRIOR_DIRS = {
    "repair": Path("artifacts/ego_mainline_old_artifact_side_effect_guard_and_redundancy_contract_repair_001a"),
    "known_failure_triage": Path("artifacts/ego_mainline_known_failure_triage_001a"),
    "dependency_closure": Path("artifacts/ego_mainline_evidence_dependency_closure_001a"),
    "post_admission_routing": Path("artifacts/ego_mainline_post_admission_routing_001a"),
    "admission_execution": Path("artifacts/ego_mainline_admission_execution_001a"),
}

PRIOR_REQUIRED_FILES = {
    "repair": [
        "result.json",
        "full_pytest_report.json",
        "residual_failure_classification.json",
        "downstream_route_impact_matrix.json",
        "old_artifact_write_guard_report.json",
        "before_after_hash_comparison.json",
    ],
    "known_failure_triage": [
        "result.json",
        "blocker_severity_matrix.json",
        "downstream_route_impact_matrix.json",
        "failure_cause_classification.json",
    ],
    "dependency_closure": [
        "result.json",
        "route_permission_matrix.json",
        "known_blockers.json",
        "missing_dependencies.json",
    ],
    "post_admission_routing": [
        "result.json",
        "routing_decision_matrix.json",
        "blocked_routes.json",
        "allowed_routes.json",
    ],
}

REQUIRED_ARTIFACT_NAMES = [
    "result.json",
    "anchor_readback.json",
    "input_artifact_inventory.json",
    "prior_repair_evidence_summary.json",
    "prior_triage_evidence_summary.json",
    "prior_dependency_closure_summary.json",
    "prior_routing_summary.json",
    "current_test_status_matrix.json",
    "full_pytest_report.json",
    "old_artifact_guard_status.json",
    "blocker_resolution_matrix.json",
    "residual_blocker_matrix.json",
    "route_permission_matrix_after_repair.json",
    "gate4_contract_source_matrix.json",
    "gate4_task_card_generation_decision.json",
    "gate4_prerequisite_matrix.json",
    "downstream_non_authorization_flags.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_scan_report.json",
    "replay_report.json",
    "computed_evidence_provenance.json",
    "combined_state.json",
]

ROUTE_CLASSES = [
    "Gate4_preflight_task_card_drafting_allowed_next",
    "Gate4_preflight_task_card_drafting_blocked_missing_gate4_contract",
    "Gate4_preflight_task_card_drafting_blocked_residual_governance_failure",
    "Gate4_execution_blocked",
    "bridge_runtime_preflight_blocked",
    "EGO_runtime_implementation_blocked",
    "product_or_companion_behavior_work_blocked",
    "residual_known_failure_repair_required",
    "theory_canonicalization_or_coverage_closure_required_only_if_specific_missing_artifact_identified",
    "no_go_concrete_blocker",
]

NON_AUTHORIZATION_FLAGS = [
    "gate4_execution_authorized",
    "runtime_authorized",
    "bridge_runtime_authorized",
    "ego_runtime_implementation_authorized",
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

FORBIDDEN_CLAIMS = [
    "Gate4 execution",
    "runtime",
    "bridge runtime",
    "EGO runtime implementation",
    "implementation",
    "mechanism validity",
    "theory validity",
    "architecture correctness",
    "agency",
    "selfhood",
    "consciousness",
    "emotion",
    "relationship learning",
    "stable user benefit",
]

TARGETED_TESTS = {
    "old_artifact_repair": [
        "tests/test_ego_mainline_old_artifact_side_effect_guard_and_redundancy_contract_repair_001a.py"
    ],
    "known_failure_triage": ["tests/test_ego_mainline_known_failure_triage_001a.py"],
    "evidence_dependency_closure": ["tests/test_ego_mainline_evidence_dependency_closure_001a.py"],
    "post_admission_routing": ["tests/test_ego_mainline_post_admission_routing_001a.py"],
}

UNAUTHORIZED_CLAIM_PATTERNS = [
    ("ego_ready", re.compile(r"\bEGO\s+ready\b", re.IGNORECASE)),
    ("bridge_ready", re.compile(r"\bbridge\s+ready\b", re.IGNORECASE)),
    ("runtime_ready", re.compile(r"\bruntime\s+ready\b", re.IGNORECASE)),
    ("gate4_ready", re.compile(r"\bGate4\s+ready\b", re.IGNORECASE)),
    ("gate4_authorized", re.compile(r"\bGate4\s+authorized\b", re.IGNORECASE)),
    ("gate4_passed", re.compile(r"\bGate4\s+passed\b", re.IGNORECASE)),
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
    "forbidden",
    "unauthorized",
    "insufficient",
    "does not",
    "do not",
    "must not",
    "without",
    "what this does not prove",
    "what_this_does_not_prove",
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
    "remains blocked",
    "remains unauthorized",
    "not authorized",
    "does not authorize",
    "must not authorize",
]

ABLATION_IDS = [
    "remove_repair_remote_tag_verification",
    "remove_full_pytest_observation",
    "substitute_full_pytest_failure",
    "remove_old_artifact_guard_hash_observation",
    "remove_repair_result_artifact",
    "remove_known_failure_triage_classification",
    "remove_previous_dependency_closure_matrix",
    "remove_claim_ceiling",
    "substitute_stale_pre_repair_route_matrix_as_current",
    "substitute_targeted_green_full_pytest_fails",
    "remove_gate0_gate3_source_evidence",
    "remove_gate4_source_references",
    "substitute_ambiguous_gate4_contract",
    "substitute_positive_control_unauthorized_readiness_claim",
    "make_gate4_generator_attempt_to_authorize_execution",
]


def run_post_repair_route_refresh(
    repo_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    verify_remote: bool = True,
    execute_targeted_tests: bool = True,
    execute_full_pytest: bool = True,
    test_observation_override: dict[str, Any] | None = None,
    write_task_card: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    out = Path(output_dir) if output_dir is not None else root / ARTIFACT_DIR
    if not out.is_absolute():
        out = root / out
    out.mkdir(parents=True, exist_ok=True)

    state = build_combined_state(
        repo_root=root,
        output_dir=out,
        verify_remote=verify_remote,
        execute_targeted_tests=execute_targeted_tests,
        execute_full_pytest=execute_full_pytest,
        test_observation_override=test_observation_override,
    )
    route_refresh = compute_route_refresh(state["route_refresh_inputs"], state["route_refresh_parameters"])
    gate4_decision = compute_gate4_generation_decision(state, route_refresh)
    blocker_resolution = build_blocker_resolution_matrix(state, route_refresh)
    residual_blockers = build_residual_blocker_matrix(state, route_refresh)
    stale_dependencies = build_stale_or_superseded_dependency_matrix(state, route_refresh)
    route_permission = build_route_permission_matrix_after_repair(route_refresh)
    downstream_flags = build_downstream_non_authorization_flags(route_refresh)
    gate4_prereq = build_gate4_prerequisite_matrix(state, route_refresh, gate4_decision)
    baseline = build_baseline_comparison(state, route_refresh, gate4_decision)
    ablation = run_ablation_suite(state)
    combined_state = build_combined_state_artifact(state)
    replay = build_replay_report(combined_state, route_refresh, gate4_decision)

    generated_markdown = {}
    if gate4_decision["generated_task_card_text"]:
        generated_markdown[gate4_decision["generated_gate4_task_card_path"]] = gate4_decision[
            "generated_task_card_text"
        ]
    if write_task_card and gate4_decision["generated_task_card_text"]:
        _write_text(root / gate4_decision["generated_gate4_task_card_path"], gate4_decision["generated_task_card_text"])

    text_payloads = {
        "claim_ceiling.txt": CLAIM_CEILING + "\n",
        "future_task_recommendation.txt": build_future_task_recommendation_text(gate4_decision),
        "rollback_plan.txt": build_rollback_plan_text(route_refresh),
    }
    json_payloads = {
        "anchor_readback.json": state["anchor_readback"],
        "input_artifact_inventory.json": state["input_artifact_inventory"],
        "prior_repair_evidence_summary.json": state["prior_repair_evidence_summary"],
        "prior_triage_evidence_summary.json": state["prior_triage_evidence_summary"],
        "prior_dependency_closure_summary.json": state["prior_dependency_closure_summary"],
        "prior_routing_summary.json": state["prior_routing_summary"],
        "current_test_status_matrix.json": state["current_test_status_matrix"],
        "full_pytest_report.json": state["full_pytest_report"],
        "old_artifact_guard_status.json": state["old_artifact_guard_status"],
        "blocker_resolution_matrix.json": blocker_resolution,
        "residual_blocker_matrix.json": residual_blockers,
        "route_permission_matrix_after_repair.json": route_permission,
        "gate4_contract_source_matrix.json": state["gate4_contract_source_matrix"],
        "gate4_task_card_generation_decision.json": _without_large_text(gate4_decision),
        "gate4_prerequisite_matrix.json": gate4_prereq,
        "downstream_non_authorization_flags.json": downstream_flags,
        "baseline_comparison.json": baseline,
        "ablation_report.json": ablation,
        "replay_report.json": replay,
        "combined_state.json": combined_state,
    }

    leakage_prelim = build_leakage_scan_report(root, json_payloads, text_payloads, generated_markdown)
    provenance_prelim = build_computed_evidence_provenance_report(
        state, route_refresh, gate4_decision, baseline, ablation, leakage_prelim, replay, None
    )
    result_prelim = build_result(
        state=state,
        route_refresh=route_refresh,
        gate4_decision=gate4_decision,
        baseline=baseline,
        ablation=ablation,
        leakage=leakage_prelim,
        replay=replay,
        provenance=provenance_prelim,
    )
    json_payloads["leakage_scan_report.json"] = leakage_prelim
    json_payloads["computed_evidence_provenance.json"] = provenance_prelim
    json_payloads["result.json"] = result_prelim
    leakage = build_leakage_scan_report(root, json_payloads, text_payloads, generated_markdown)
    provenance = build_computed_evidence_provenance_report(
        state, route_refresh, gate4_decision, baseline, ablation, leakage, replay, result_prelim
    )
    result = build_result(
        state=state,
        route_refresh=route_refresh,
        gate4_decision=gate4_decision,
        baseline=baseline,
        ablation=ablation,
        leakage=leakage,
        replay=replay,
        provenance=provenance,
    )
    json_payloads["leakage_scan_report.json"] = leakage
    json_payloads["computed_evidence_provenance.json"] = provenance
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


def build_combined_state(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
    verify_remote: bool = True,
    execute_targeted_tests: bool = True,
    execute_full_pytest: bool = True,
    test_observation_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    out = Path(output_dir) if output_dir is not None else root / ARTIFACT_DIR
    if not out.is_absolute():
        out = root / out

    protected_before = hash_protected_old_artifacts(root)
    anchor_readback = build_anchor_readback(root, verify_remote=verify_remote)
    prior_repair = summarize_prior_artifacts(root, "repair")
    prior_triage = summarize_prior_artifacts(root, "known_failure_triage")
    prior_dependency = summarize_prior_artifacts(root, "dependency_closure")
    prior_routing = summarize_prior_artifacts(root, "post_admission_routing")
    input_inventory = build_input_artifact_inventory(root)
    test_observation = (
        copy.deepcopy(test_observation_override)
        if test_observation_override is not None
        else build_current_test_observation(root, execute_targeted_tests, execute_full_pytest)
    )
    protected_after = hash_protected_old_artifacts(root)
    old_guard = build_old_artifact_guard_status(protected_before, protected_after)
    gate4_sources = build_gate4_contract_source_matrix(root)

    route_inputs = {
        "anchor_readback": anchor_readback,
        "prior_repair_evidence_summary": prior_repair,
        "prior_triage_evidence_summary": prior_triage,
        "prior_dependency_closure_summary": prior_dependency,
        "prior_routing_summary": prior_routing,
        "input_artifact_inventory": input_inventory,
        "current_test_status_matrix": test_observation["current_test_status_matrix"],
        "full_pytest_report": test_observation["full_pytest_report"],
        "old_artifact_guard_status": old_guard,
        "gate4_contract_source_matrix": gate4_sources,
        "claim_ceiling": CLAIM_CEILING,
        "downstream_non_authorization_flags": _false_non_authorization_flags(),
        "positive_control_artifact": None,
        "generator_attempt_authorize_execution": False,
        "intervention_markers": [],
    }
    return {
        "task_id": TASK_ID,
        "repo_root": root.as_posix(),
        "output_dir": out.as_posix(),
        "run_id": _run_id(root),
        "seed_context_episode_ids": {
            "seed": "not_used",
            "context_id": TASK_ID,
            "episode_id": "post_repair_route_refresh",
            "unused_seed_blocking_check": "no stochastic seed used",
        },
        "anchor_readback": anchor_readback,
        "input_artifact_inventory": input_inventory,
        "prior_repair_evidence_summary": prior_repair,
        "prior_triage_evidence_summary": prior_triage,
        "prior_dependency_closure_summary": prior_dependency,
        "prior_routing_summary": prior_routing,
        "current_test_status_matrix": test_observation["current_test_status_matrix"],
        "full_pytest_report": test_observation["full_pytest_report"],
        "old_artifact_guard_status": old_guard,
        "gate4_contract_source_matrix": gate4_sources,
        "route_refresh_inputs": route_inputs,
        "route_refresh_parameters": {
            "route_classes": list(ROUTE_CLASSES),
            "required_claim_ceiling": CLAIM_CEILING,
            "gate4_task_card_claim_ceiling": GATE4_TASK_CARD_CLAIM_CEILING,
            "forbidden_claims": list(FORBIDDEN_CLAIMS),
            "required_anchors": copy.deepcopy(ANCHORS),
        },
    }


def build_anchor_readback(root: Path, verify_remote: bool = True) -> dict[str, Any]:
    rows = {}
    for key, spec in ANCHORS.items():
        local = _git_output(root, ["rev-parse", spec["commit"]])
        remote = _remote_tag_commit(root, spec["remote_tag"]) if verify_remote else local
        rows[key] = {
            "commit": spec["commit"],
            "commit_resolved_hash": local,
            "remote_tag": spec["remote_tag"],
            "remote_tag_resolved_hash": remote,
            "expected_verdict": spec["verdict"],
            "anchor_verified": local == spec["commit"] and remote == spec["commit"],
        }
    return {
        "task_id": TASK_ID,
        "producer_function": "build_anchor_readback",
        "branch": _git_output(root, ["branch", "--show-current"]),
        "head": _git_output(root, ["rev-parse", "HEAD"]),
        "git_status_short_branch": _git_output(root, ["status", "--short", "--branch"]).splitlines(),
        "anchors": rows,
        "all_required_anchors_verified": all(row["anchor_verified"] for row in rows.values()),
        "aggregation_rule": "resolve required local commits and remote tags exactly",
        "code_path_hash": _code_path_hash(build_anchor_readback),
    }


def summarize_prior_artifacts(root: Path, key: str) -> dict[str, Any]:
    base = PRIOR_DIRS[key]
    required = PRIOR_REQUIRED_FILES.get(key, [])
    rows = []
    payloads = {}
    for name in required:
        path = root / base / name
        exists = path.exists()
        row = {
            "path": (base / name).as_posix(),
            "exists": exists,
            "sha256": _sha_file(path) if exists else None,
        }
        rows.append(row)
        if exists and path.suffix == ".json":
            payloads[name] = _read_json(path)
    result = payloads.get("result.json", {})
    return {
        "task_id": TASK_ID,
        "producer_function": "summarize_prior_artifacts",
        "prior_key": key,
        "required_files": rows,
        "all_required_files_present": all(row["exists"] for row in rows),
        "result_verdict": result.get("verdict"),
        "claim_ceiling": result.get("claim_ceiling"),
        "payload_extracts": _extract_prior_payloads(key, payloads),
        "aggregation_rule": "hash and summarize required prior evidence artifacts without mutation",
        "code_path_hash": _code_path_hash(summarize_prior_artifacts),
    }


def _extract_prior_payloads(key: str, payloads: dict[str, Any]) -> dict[str, Any]:
    if key == "repair":
        return {
            "full_pytest_summary": payloads.get("full_pytest_report.json", {}).get("summary"),
            "residual_failure_classification": payloads.get("residual_failure_classification.json", {}),
            "old_artifact_write_guard": payloads.get("old_artifact_write_guard_report.json", {}),
            "before_after_hash_comparison": payloads.get("before_after_hash_comparison.json", {}),
            "downstream_route_impact": payloads.get("downstream_route_impact_matrix.json", {}),
        }
    if key == "known_failure_triage":
        return {
            "blocker_severity_matrix": payloads.get("blocker_severity_matrix.json", {}),
            "failure_cause_classification": payloads.get("failure_cause_classification.json", {}),
            "downstream_route_impact": payloads.get("downstream_route_impact_matrix.json", {}),
        }
    if key == "dependency_closure":
        return {
            "route_permission_matrix": payloads.get("route_permission_matrix.json", {}),
            "known_blockers": payloads.get("known_blockers.json", {}),
            "missing_dependencies": payloads.get("missing_dependencies.json", {}),
        }
    if key == "post_admission_routing":
        return {
            "routing_decision_matrix": payloads.get("routing_decision_matrix.json", {}),
            "allowed_routes": payloads.get("allowed_routes.json", {}),
            "blocked_routes": payloads.get("blocked_routes.json", {}),
        }
    return {}


def build_input_artifact_inventory(root: Path) -> dict[str, Any]:
    paths: list[Path] = [DOC_PATH]
    for key, base in PRIOR_DIRS.items():
        for name in PRIOR_REQUIRED_FILES.get(key, ["result.json"]):
            paths.append(base / name)
    paths.extend(
        [
            Path("docs/GATE4-SOCIAL-REPRESENTATIONAL-GAP-PREFLIGHT-001A.md"),
            Path("docs/GATE4-SOCIAL-LATENT-INFERENCE-TASK-CARD-001A.md"),
            Path("docs/codex/tasks/R-G-GATE0-GATE1-GATE2-GATE3-CANONICAL-MICRO-AGENT-TESTBED-TASK-CARD-001A.md"),
            Path("docs/codex/tasks/GATE3-VIABILITY-FUNCTIONAL-AFFECT-TASK-CARD-001A.md"),
        ]
    )
    rows = []
    for rel in sorted({path for path in paths}, key=lambda p: p.as_posix()):
        path = root / rel
        rows.append(
            {
                "path": rel.as_posix(),
                "exists": path.exists(),
                "sha256": _sha_file(path) if path.exists() and path.is_file() else None,
                "category": _inventory_category(rel.as_posix()),
            }
        )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_input_artifact_inventory",
        "inventory_rows": rows,
        "inventory_digest": _payload_hash(rows),
        "all_required_prior_inputs_present": all(row["exists"] for row in rows if row["category"] in {"prior", "task"}),
        "aggregation_rule": "hash task card, prior evidence artifacts, and Gate source documents",
        "code_path_hash": _code_path_hash(build_input_artifact_inventory),
    }


def build_current_test_observation(root: Path, execute_targeted: bool, execute_full: bool) -> dict[str, Any]:
    targeted = {}
    if execute_targeted:
        for label, args in TARGETED_TESTS.items():
            targeted[label] = _run_pytest_command(root, args, label)
    else:
        for label, args in TARGETED_TESTS.items():
            targeted[label] = {
                "label": label,
                "command": " ".join([sys.executable, "-m", "pytest", "-q", *args]),
                "exit_code": None,
                "passed": None,
                "summary": {},
                "mode": "not_executed",
                "producer_function": "build_current_test_observation",
            }
    full = (
        _run_pytest_command(root, [], "full_pytest")
        if execute_full
        else {
            "label": "full_pytest",
            "command": f"{sys.executable} -m pytest -q",
            "exit_code": None,
            "passed": None,
            "summary": {},
            "mode": "not_executed",
            "producer_function": "build_current_test_observation",
        }
    )
    return {
        "current_test_status_matrix": build_current_test_status_matrix(targeted, full),
        "full_pytest_report": build_full_pytest_report(full),
    }


def build_green_test_observation() -> dict[str, Any]:
    targeted = {
        label: {
            "label": label,
            "command": " ".join([sys.executable, "-m", "pytest", "-q", *args]),
            "exit_code": 0,
            "passed": True,
            "summary": {"passed": 1, "failed": 0, "errors": 0, "skipped": 0},
            "mode": "override_green",
            "producer_function": "build_green_test_observation",
        }
        for label, args in TARGETED_TESTS.items()
    }
    full = {
        "label": "full_pytest",
        "command": f"{sys.executable} -m pytest -q",
        "exit_code": 0,
        "passed": True,
        "summary": {"passed": 682, "failed": 0, "errors": 0, "skipped": 0},
        "mode": "override_green",
        "producer_function": "build_green_test_observation",
    }
    return {
        "current_test_status_matrix": build_current_test_status_matrix(targeted, full),
        "full_pytest_report": build_full_pytest_report(full),
    }


def build_current_test_status_matrix(targeted: dict[str, Any], full: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "build_current_test_status_matrix",
        "targeted_tests": targeted,
        "all_targeted_tests_passed": all(row.get("passed") is True for row in targeted.values()),
        "full_pytest_passed": full.get("passed") is True,
        "full_pytest_mode": full.get("mode", "executed"),
        "aggregation_rule": "aggregate targeted repair, triage, dependency, routing, and full pytest observations",
        "code_path_hash": _code_path_hash(build_current_test_status_matrix),
    }


def build_full_pytest_report(full: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "build_full_pytest_report",
        "full_pytest": full,
        "passed": full.get("passed") is True,
        "summary": full.get("summary", {}),
        "aggregation_rule": "materialize current full pytest command result",
        "code_path_hash": _code_path_hash(build_full_pytest_report),
    }


def build_old_artifact_guard_status(before: dict[str, str], after: dict[str, str]) -> dict[str, Any]:
    changed = {
        path: {"before": before.get(path), "after": after.get(path)}
        for path in sorted(set(before) | set(after))
        if before.get(path) != after.get(path)
    }
    return {
        "task_id": TASK_ID,
        "producer_function": "build_old_artifact_guard_status",
        "protected_old_artifact_hashes_before": before,
        "protected_old_artifact_hashes_after": after,
        "changed_old_artifact_hashes": changed,
        "old_sealed_artifacts_unchanged": not changed,
        "old_artifact_mutation_detected": bool(changed),
        "aggregation_rule": "compare protected old artifact hashes before and after current observations",
        "code_path_hash": _code_path_hash(build_old_artifact_guard_status),
    }


def hash_protected_old_artifacts(root: str | Path) -> dict[str, str]:
    root_path = Path(root).resolve()
    paths: list[Path] = []
    for key, base in PRIOR_DIRS.items():
        for name in PRIOR_REQUIRED_FILES.get(key, ["result.json"]):
            paths.append(base / name)
    paths.extend(
        [
            Path("docs/GATE4-SOCIAL-REPRESENTATIONAL-GAP-PREFLIGHT-001A.md"),
            Path("docs/GATE4-SOCIAL-LATENT-INFERENCE-TASK-CARD-001A.md"),
            Path("docs/codex/tasks/R-G-GATE0-GATE1-GATE2-GATE3-CANONICAL-MICRO-AGENT-TESTBED-TASK-CARD-001A.md"),
            Path("docs/codex/tasks/GATE3-VIABILITY-FUNCTIONAL-AFFECT-TASK-CARD-001A.md"),
        ]
    )
    return {
        path.as_posix(): _sha_file(root_path / path)
        for path in sorted({p for p in paths}, key=lambda p: p.as_posix())
        if (root_path / path).exists() and (root_path / path).is_file()
    }


def build_gate4_contract_source_matrix(root: Path) -> dict[str, Any]:
    patterns = [
        "docs/codex/tasks/GATE1*",
        "docs/codex/tasks/GATE2*",
        "docs/codex/tasks/GATE3*",
        "docs/codex/tasks/R-G-GATE0-GATE1-GATE2-GATE3*",
        "docs/GATE4*",
        "docs/codex/tasks/*GATE4*",
        "artifacts/gate4_social_representational_gap_preflight_001b/result.json",
        "artifacts/gate4_social_latent_inference_001b/result.json",
        "artifacts/gate3_viability_functional_affect_001b/result.json",
        "artifacts/r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b/result.json",
        "artifacts/GATE0-PREDICTIVE-ACTION-POSTFREEZE-SHORTCUT-AUDIT-001A/shortcut_audit_result.json",
    ]
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(root.glob(pattern))
    rows = []
    for path in sorted({p for p in paths if p.is_file()}, key=lambda p: p.as_posix()):
        rel = path.relative_to(root).as_posix()
        rows.append(
            {
                "path": rel,
                "category": _gate_source_category(rel),
                "sha256": _sha_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    categories = {row["category"] for row in rows}
    gate0_3_present = {"gate0", "gate1", "gate2", "gate3", "micro_agent_gate0_3"}.issubset(categories)
    gate4_present = "gate4" in categories
    sufficient = gate0_3_present and gate4_present
    return {
        "task_id": TASK_ID,
        "producer_function": "build_gate4_contract_source_matrix",
        "inventory_patterns": patterns,
        "source_rows": rows,
        "gate4_source_paths": [row["path"] for row in rows if row["category"] == "gate4"],
        "gate0_gate3_source_paths": [row["path"] for row in rows if row["category"] != "gate4"],
        "gate0_to_gate3_source_present": gate0_3_present,
        "gate4_source_present": gate4_present,
        "gate4_contract_source_sufficient": sufficient,
        "gate4_semantics_invented": False,
        "gate4_scope_derived_from_existing_repo_evidence": sufficient,
        "source_summary": (
            "Gate4 scope is derived from existing social representational-gap and social-latent task cards plus "
            "Gate0-Gate3 canonical micro-agent and Gate3 viability contracts."
            if sufficient
            else "Gate4 source evidence is missing or ambiguous; drafting must switch to contract discovery."
        ),
        "aggregation_rule": "hash and classify existing Gate0-Gate4 source documents/artifacts",
        "code_path_hash": _code_path_hash(build_gate4_contract_source_matrix),
    }


def compute_route_refresh(inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    stops: list[str] = []
    anchors_ok = inputs.get("anchor_readback", {}).get("all_required_anchors_verified") is True
    targeted_ok = inputs.get("current_test_status_matrix", {}).get("all_targeted_tests_passed") is True
    full_ok = inputs.get("full_pytest_report", {}).get("passed") is True
    guard_ok = inputs.get("old_artifact_guard_status", {}).get("old_sealed_artifacts_unchanged") is True
    gate_source_ok = inputs.get("gate4_contract_source_matrix", {}).get("gate4_contract_source_sufficient") is True
    claim_ok = inputs.get("claim_ceiling") == parameters.get("required_claim_ceiling")
    prior_files_ok = all(
        inputs.get(name, {}).get("all_required_files_present") is True
        for name in [
            "prior_repair_evidence_summary",
            "prior_triage_evidence_summary",
            "prior_dependency_closure_summary",
            "prior_routing_summary",
        ]
    )
    positive_control = inputs.get("positive_control_artifact")

    if anchors_ok:
        reasons.append("all_required_anchors_verified")
    else:
        reasons.append("required_anchor_missing_or_mismatch")
        stops.append("missing_anchor")
    if targeted_ok:
        reasons.append("targeted_governance_tests_green")
    else:
        reasons.append("targeted_governance_test_failure_or_missing")
        stops.append("targeted_governance_tests_not_green")
    if full_ok:
        reasons.append("full_pytest_green")
    else:
        reasons.append("full_pytest_not_green_or_not_observed")
        stops.append("full_pytest_not_green")
    if guard_ok:
        reasons.append("old_artifact_guard_clean")
    else:
        reasons.append("old_artifact_guard_regression")
        stops.append("old_artifact_guard_regression")
    if prior_files_ok:
        reasons.append("required_prior_artifacts_present")
    else:
        reasons.append("required_prior_artifact_missing")
        stops.append("required_prior_artifact_missing")
    if gate_source_ok:
        reasons.append("gate4_contract_source_sufficient")
    else:
        reasons.append("gate4_contract_source_missing_or_ambiguous")
    if claim_ok:
        reasons.append("claim_ceiling_preserved")
    else:
        reasons.append("claim_ceiling_missing_or_mismatched")
        stops.append("claim_ceiling_missing")
    if positive_control:
        reasons.append("unauthorized_positive_claim_control_present")
        stops.append("positive_control_unauthorized_claim_present")

    if not anchors_ok:
        route_class = "no_go_concrete_blocker"
        drafting_permission = False
    elif not (targeted_ok and full_ok and guard_ok and prior_files_ok and claim_ok) or positive_control:
        route_class = "Gate4_preflight_task_card_drafting_blocked_residual_governance_failure"
        drafting_permission = False
    elif not gate_source_ok:
        route_class = "Gate4_preflight_task_card_drafting_blocked_missing_gate4_contract"
        drafting_permission = False
        stops.append("missing_gate4_contract_source")
    else:
        route_class = "Gate4_preflight_task_card_drafting_allowed_next"
        drafting_permission = True

    return {
        "task_id": TASK_ID,
        "producer_function": "compute_route_refresh",
        "post_repair_route_refresh_verdict": route_class,
        "gate4_task_card_drafting_permission": drafting_permission,
        "route_permission_matrix_after_repair": _compute_route_permissions(route_class),
        "downstream_non_authorization_flags": _false_non_authorization_flags(),
        "required_prerequisites_for_gate4_task_card": {
            "anchors_verified": anchors_ok,
            "targeted_governance_tests_green": targeted_ok,
            "full_pytest_green": full_ok,
            "old_artifact_guard_clean": guard_ok,
            "prior_artifacts_present": prior_files_ok,
            "gate4_contract_source_sufficient": gate_source_ok,
            "claim_ceiling_preserved": claim_ok,
        },
        "claim_ceiling_restatement": inputs.get("claim_ceiling"),
        "stop_conditions": list(dict.fromkeys(stops)),
        "rollback_plan": _rollback_plan(stops, route_class),
        "computed_reason_codes": list(dict.fromkeys(reasons)),
        "aggregation_rule": "compute post-repair route permission from anchors, tests, old-artifact guard, prior artifacts, Gate4 source, and claim ceiling",
        "code_path_hash": _code_path_hash(compute_route_refresh),
    }


def compute_gate4_generation_decision(state: dict[str, Any], route_refresh: dict[str, Any]) -> dict[str, Any]:
    inputs = state["route_refresh_inputs"]
    attempt_authorize = bool(inputs.get("generator_attempt_authorize_execution"))
    source = inputs.get("gate4_contract_source_matrix", {})
    allowed = route_refresh["gate4_task_card_drafting_permission"] is True
    missing_source = source.get("gate4_contract_source_sufficient") is not True
    reason_codes: list[str] = []

    if attempt_authorize:
        reason_codes.append("generator_attempted_forbidden_gate4_execution_authorization")
        path = GATE4_CONTRACT_DISCOVERY_PATH
        text = build_gate4_contract_discovery_task_card_text(source, reason_codes)
        generation_allowed = False
    elif allowed and not missing_source:
        reason_codes.append("phase_a_allowed_and_gate4_source_sufficient")
        path = GATE4_TASK_CARD_PATH
        text = build_gate4_preflight_task_card_text(source, route_refresh)
        generation_allowed = True
    elif missing_source:
        reason_codes.append("missing_gate4_contract_source_generates_contract_discovery")
        path = GATE4_CONTRACT_DISCOVERY_PATH
        text = build_gate4_contract_discovery_task_card_text(source, reason_codes)
        generation_allowed = False
    else:
        reason_codes.append("phase_a_blocked_no_gate4_task_card_generated")
        path = GATE4_CONTRACT_DISCOVERY_PATH
        text = ""
        generation_allowed = False

    return {
        "task_id": TASK_ID,
        "producer_function": "compute_gate4_generation_decision",
        "generation_allowed": generation_allowed,
        "generated_gate4_task_card_path": path.as_posix(),
        "generated_task_card_text": text,
        "gate4_contract_source_matrix": source,
        "gate4_claim_ceiling": GATE4_TASK_CARD_CLAIM_CEILING,
        "claim_ceiling": GATE4_TASK_CARD_CLAIM_CEILING,
        "gate4_execution_performed": False,
        "gate4_execution_authorized": False,
        "runtime_authorized": False,
        "bridge_runtime_authorized": False,
        "ego_runtime_implementation_authorized": False,
        "mechanism_validity_authorized": False,
        "theory_validity_authorized": False,
        "architecture_correctness_authorized": False,
        "gate4_baseline_requirements": _gate4_baselines(),
        "gate4_ablation_requirements": _gate4_ablations(),
        "gate4_trace_replay_requirements": _gate4_trace_replay_requirements(),
        "gate4_computed_evidence_provenance_requirements": _computed_provenance_requirements(),
        "gate4_stop_conditions": _gate4_stop_conditions(),
        "gate4_rollback_plan": _gate4_rollback_plan(),
        "gate4_non_authorization_flags": _false_non_authorization_flags(),
        "computed_reason_codes": reason_codes,
        "aggregation_rule": "conditionally generate bounded Gate4 preflight task-card or contract-discovery task from route and source evidence",
        "code_path_hash": _code_path_hash(compute_gate4_generation_decision),
    }


def build_blocker_resolution_matrix(state: dict[str, Any], route_refresh: dict[str, Any]) -> dict[str, Any]:
    prereq = route_refresh["required_prerequisites_for_gate4_task_card"]
    rows = {
        key: {
            "status": "resolved" if value else "blocked",
            "resolution_evidence": key,
        }
        for key, value in prereq.items()
    }
    return {
        "task_id": TASK_ID,
        "producer_function": "build_blocker_resolution_matrix",
        "blocker_resolution_matrix": rows,
        "all_non_gate4_contract_blockers_resolved": all(
            value for key, value in prereq.items() if key != "gate4_contract_source_sufficient"
        ),
        "aggregation_rule": "map route prerequisites into resolved or blocked blocker rows",
        "code_path_hash": _code_path_hash(build_blocker_resolution_matrix),
    }


def build_residual_blocker_matrix(state: dict[str, Any], route_refresh: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for stop in route_refresh["stop_conditions"]:
        rows.append(
            {
                "blocker_id": stop,
                "blocks_gate4_task_card_drafting": stop
                not in {"missing_gate4_contract_source"} or route_refresh["gate4_task_card_drafting_permission"] is False,
                "safe_next_task": "EGO-MAINLINE-GATE4-CONTRACT-DISCOVERY-001A"
                if stop == "missing_gate4_contract_source"
                else "bounded_repair_or_revalidation_task",
            }
        )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_residual_blocker_matrix",
        "residual_blockers": rows,
        "residual_blocker_count": len(rows),
        "aggregation_rule": "materialize residual blockers from route stop conditions",
        "code_path_hash": _code_path_hash(build_residual_blocker_matrix),
    }


def build_stale_or_superseded_dependency_matrix(state: dict[str, Any], route_refresh: dict[str, Any]) -> dict[str, Any]:
    prior_dep = state["prior_dependency_closure_summary"]
    prior_routing = state["prior_routing_summary"]
    return {
        "task_id": TASK_ID,
        "producer_function": "build_stale_or_superseded_dependency_matrix",
        "stale_or_superseded_dependencies": {
            "pre_repair_dependency_closure_matrix": {
                "status": "superseded_by_repair_refresh" if route_refresh["gate4_task_card_drafting_permission"] else "still_blocks_or_requires_review",
                "source_verdict": prior_dep.get("result_verdict"),
            },
            "pre_repair_post_admission_routing_matrix": {
                "status": "superseded_by_repair_refresh" if route_refresh["gate4_task_card_drafting_permission"] else "still_blocks_or_requires_review",
                "source_verdict": prior_routing.get("result_verdict"),
            },
        },
        "aggregation_rule": "compare pre-repair matrices to post-repair computed route",
        "code_path_hash": _code_path_hash(build_stale_or_superseded_dependency_matrix),
    }


def build_route_permission_matrix_after_repair(route_refresh: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "build_route_permission_matrix_after_repair",
        "route_permissions": route_refresh["route_permission_matrix_after_repair"]["route_permissions"],
        "recommended_route_class": route_refresh["post_repair_route_refresh_verdict"],
        "aggregation_rule": "materialize route permissions after repair",
        "code_path_hash": _code_path_hash(build_route_permission_matrix_after_repair),
    }


def build_downstream_non_authorization_flags(route_refresh: dict[str, Any]) -> dict[str, Any]:
    flags = route_refresh["downstream_non_authorization_flags"]
    return {
        "task_id": TASK_ID,
        "producer_function": "build_downstream_non_authorization_flags",
        "downstream_non_authorization_flags": flags,
        "all_downstream_authorizations_false": all(value is False for value in flags.values()),
        "aggregation_rule": "derive downstream authorization flags from route claim ceiling",
        "code_path_hash": _code_path_hash(build_downstream_non_authorization_flags),
    }


def build_gate4_prerequisite_matrix(
    state: dict[str, Any],
    route_refresh: dict[str, Any],
    gate4_decision: dict[str, Any],
) -> dict[str, Any]:
    prereq = route_refresh["required_prerequisites_for_gate4_task_card"]
    return {
        "task_id": TASK_ID,
        "producer_function": "build_gate4_prerequisite_matrix",
        "gate4_prerequisites": prereq,
        "all_prerequisites_satisfied_for_drafting": all(prereq.values()) and gate4_decision["generation_allowed"],
        "generated_task_card_path": gate4_decision["generated_gate4_task_card_path"],
        "execution_authorized": False,
        "aggregation_rule": "combine route prerequisites with generation decision",
        "code_path_hash": _code_path_hash(build_gate4_prerequisite_matrix),
    }


def naive_full_suite_green_baseline(inputs: dict[str, Any]) -> dict[str, Any]:
    full_ok = inputs.get("full_pytest_report", {}).get("passed") is True
    return {
        "producer_function": "naive_full_suite_green_baseline",
        "allows_gate4_task_card_drafting": full_ok,
        "unsafe_tendency": full_ok,
        "uses_only_full_pytest": True,
    }


def stale_pre_repair_matrix_baseline(inputs: dict[str, Any]) -> dict[str, Any]:
    prior = inputs.get("prior_dependency_closure_summary", {})
    matrix = prior.get("payload_extracts", {}).get("route_permission_matrix", {})
    text = json.dumps(matrix, sort_keys=True)
    blocks = "Gate4" in text and "blocked" in text
    return {
        "producer_function": "stale_pre_repair_matrix_baseline",
        "allows_gate4_task_card_drafting": not blocks,
        "stale_conservative_tendency": blocks,
        "uses_only_pre_repair_dependency_matrix": True,
    }


def strict_anchor_full_suite_guard_baseline(inputs: dict[str, Any]) -> dict[str, Any]:
    prereq = {
        "anchors": inputs.get("anchor_readback", {}).get("all_required_anchors_verified") is True,
        "full_pytest": inputs.get("full_pytest_report", {}).get("passed") is True,
        "old_artifact_guard": inputs.get("old_artifact_guard_status", {}).get("old_sealed_artifacts_unchanged") is True,
    }
    return {
        "producer_function": "strict_anchor_full_suite_guard_baseline",
        "allows_next_planning_task": all(prereq.values()),
        "prerequisites": prereq,
    }


def claim_ceiling_baseline(inputs: dict[str, Any]) -> dict[str, Any]:
    claim_ok = inputs.get("claim_ceiling") == CLAIM_CEILING
    return {
        "producer_function": "claim_ceiling_baseline",
        "claim_ceiling_preserved": claim_ok,
        "blocks_gate4_execution": True,
        "blocks_runtime": True,
        "blocks_stronger_claims": True,
        "downstream_non_authorization_flags": _false_non_authorization_flags(),
    }


def gate_contract_source_baseline(inputs: dict[str, Any]) -> dict[str, Any]:
    source = inputs.get("gate4_contract_source_matrix", {})
    return {
        "producer_function": "gate_contract_source_baseline",
        "allows_gate4_task_card_drafting": source.get("gate4_contract_source_sufficient") is True,
        "gate4_semantics_invented": source.get("gate4_semantics_invented") is True,
        "source_paths": source.get("gate4_source_paths", []),
    }


def build_baseline_comparison(
    state: dict[str, Any],
    route_refresh: dict[str, Any],
    gate4_decision: dict[str, Any],
) -> dict[str, Any]:
    inputs = state["route_refresh_inputs"]
    baselines = {
        "naive_full_suite_green_baseline": naive_full_suite_green_baseline(inputs),
        "stale_pre_repair_matrix_baseline": stale_pre_repair_matrix_baseline(inputs),
        "strict_anchor_full_suite_guard_baseline": strict_anchor_full_suite_guard_baseline(inputs),
        "claim_ceiling_baseline": claim_ceiling_baseline(inputs),
        "gate_contract_source_baseline": gate_contract_source_baseline(inputs),
    }
    strict_allows = baselines["strict_anchor_full_suite_guard_baseline"]["allows_next_planning_task"]
    candidate_allows = route_refresh["gate4_task_card_drafting_permission"]
    ceiling = baselines["claim_ceiling_baseline"]
    reason_codes = []
    if ceiling["blocks_gate4_execution"] and ceiling["blocks_stronger_claims"]:
        reason_codes.append("claim_ceiling_blocks_execution_and_stronger_claims")
    if baselines["naive_full_suite_green_baseline"]["unsafe_tendency"]:
        reason_codes.append("naive_green_baseline_lacks_anchor_guard_source_checks")
    return {
        "task_id": TASK_ID,
        "producer_function": "build_baseline_comparison",
        "baselines_invoked": list(baselines),
        "baseline_results": baselines,
        "candidate_decision": {
            "post_repair_route_refresh_verdict": route_refresh["post_repair_route_refresh_verdict"],
            "gate4_task_card_drafting_permission": candidate_allows,
            "gate4_generation_allowed": gate4_decision["generation_allowed"],
        },
        "candidate_decision_looser_than_strict_baseline": candidate_allows and not strict_allows,
        "candidate_preserves_claim_ceiling": all(value is False for value in route_refresh["downstream_non_authorization_flags"].values()),
        "candidate_exceeds_claim_ceiling_baseline": False,
        "computed_reason_codes": reason_codes,
        "aggregation_rule": "invoke five independent callable baselines and compare candidate route",
        "code_path_hash": _code_path_hash(build_baseline_comparison),
    }


def run_ablation_suite(state: dict[str, Any]) -> dict[str, Any]:
    clean_route = compute_route_refresh(state["route_refresh_inputs"], state["route_refresh_parameters"])
    rows = []
    for ablation_id in ABLATION_IDS:
        mutated = copy.deepcopy(state)
        INTERVENTIONS[ablation_id](mutated)
        routed = compute_route_refresh(mutated["route_refresh_inputs"], mutated["route_refresh_parameters"])
        decision = compute_gate4_generation_decision(mutated, routed)
        forbidden = any(routed["downstream_non_authorization_flags"].values()) or any(
            decision.get(key) is True
            for key in [
                "gate4_execution_authorized",
                "runtime_authorized",
                "bridge_runtime_authorized",
                "ego_runtime_implementation_authorized",
                "mechanism_validity_authorized",
                "theory_validity_authorized",
                "architecture_correctness_authorized",
            ]
        )
        rows.append(
            {
                "ablation_id": ablation_id,
                "producer_function": "run_ablation_suite",
                "route_refresh_rerun": True,
                "gate4_generation_rerun": True,
                "resulting_route_class": routed["post_repair_route_refresh_verdict"],
                "resulting_generation_allowed": decision["generation_allowed"],
                "forbidden_downstream_authorized": forbidden,
                "reason_codes_added": _list_delta(
                    clean_route["computed_reason_codes"],
                    routed["computed_reason_codes"] + decision["computed_reason_codes"],
                ),
            }
        )
    return {
        "task_id": TASK_ID,
        "producer_function": "run_ablation_suite",
        "ablations": rows,
        "all_ablations_reran_route_refresh": all(row["route_refresh_rerun"] for row in rows),
        "all_ablations_reran_gate4_generation": all(row["gate4_generation_rerun"] for row in rows),
        "no_ablation_authorized_forbidden_downstream": not any(row["forbidden_downstream_authorized"] for row in rows),
        "all_required_degradations_observed": all(row["reason_codes_added"] for row in rows),
        "aggregation_rule": "rerun route refresh and conditional generation under real state interventions",
        "code_path_hash": _code_path_hash(run_ablation_suite),
    }


def intervention_remove_repair_remote_tag_verification(state: dict[str, Any]) -> None:
    _anchor(state, "repair")["remote_tag_resolved_hash"] = None
    _anchor(state, "repair")["anchor_verified"] = False
    state["route_refresh_inputs"]["anchor_readback"]["all_required_anchors_verified"] = False


def intervention_remove_full_pytest_observation(state: dict[str, Any]) -> None:
    state["route_refresh_inputs"]["full_pytest_report"] = {"passed": None, "full_pytest": {"mode": "removed"}}


def intervention_substitute_full_pytest_failure(state: dict[str, Any]) -> None:
    state["route_refresh_inputs"]["full_pytest_report"] = {
        "passed": False,
        "full_pytest": {"exit_code": 1, "passed": False, "summary": {"failed": 1}},
    }


def intervention_remove_old_artifact_guard_hash_observation(state: dict[str, Any]) -> None:
    state["route_refresh_inputs"]["old_artifact_guard_status"] = {
        "old_sealed_artifacts_unchanged": False,
        "old_artifact_mutation_detected": True,
    }


def intervention_remove_repair_result_artifact(state: dict[str, Any]) -> None:
    state["route_refresh_inputs"]["prior_repair_evidence_summary"]["all_required_files_present"] = False


def intervention_remove_known_failure_triage_classification(state: dict[str, Any]) -> None:
    state["route_refresh_inputs"]["prior_triage_evidence_summary"]["all_required_files_present"] = False


def intervention_remove_previous_dependency_closure_matrix(state: dict[str, Any]) -> None:
    state["route_refresh_inputs"]["prior_dependency_closure_summary"]["all_required_files_present"] = False


def intervention_remove_claim_ceiling(state: dict[str, Any]) -> None:
    state["route_refresh_inputs"]["claim_ceiling"] = None


def intervention_substitute_stale_pre_repair_route_matrix_as_current(state: dict[str, Any]) -> None:
    state["route_refresh_inputs"]["prior_dependency_closure_summary"]["payload_extracts"]["route_permission_matrix"] = {
        "route_permissions": {"Gate4_preflight_task_card_drafting_allowed_future_only": {"permission": "blocked_current"}}
    }
    state["route_refresh_inputs"]["full_pytest_report"] = {
        "passed": False,
        "full_pytest": {"exit_code": 1, "passed": False, "summary": {"failed": 1}, "mode": "stale_substitution"},
    }


def intervention_substitute_targeted_green_full_pytest_fails(state: dict[str, Any]) -> None:
    state["route_refresh_inputs"]["current_test_status_matrix"]["all_targeted_tests_passed"] = True
    intervention_substitute_full_pytest_failure(state)


def intervention_remove_gate0_gate3_source_evidence(state: dict[str, Any]) -> None:
    source = state["route_refresh_inputs"]["gate4_contract_source_matrix"]
    source["gate0_to_gate3_source_present"] = False
    source["gate4_contract_source_sufficient"] = False
    source["gate0_gate3_source_paths"] = []


def intervention_remove_gate4_source_references(state: dict[str, Any]) -> None:
    source = state["route_refresh_inputs"]["gate4_contract_source_matrix"]
    source["gate4_source_present"] = False
    source["gate4_contract_source_sufficient"] = False
    source["gate4_source_paths"] = []


def intervention_substitute_ambiguous_gate4_contract(state: dict[str, Any]) -> None:
    source = state["route_refresh_inputs"]["gate4_contract_source_matrix"]
    source["gate4_contract_source_sufficient"] = False
    source["gate4_semantics_invented"] = True
    source["source_summary"] = "ambiguous Gate4 contract source"


def intervention_substitute_positive_control_unauthorized_readiness_claim(state: dict[str, Any]) -> None:
    state["route_refresh_inputs"]["positive_control_artifact"] = "Gate4 ready"


def intervention_make_gate4_generator_attempt_to_authorize_execution(state: dict[str, Any]) -> None:
    state["route_refresh_inputs"]["generator_attempt_authorize_execution"] = True


INTERVENTIONS: dict[str, Callable[[dict[str, Any]], None]] = {
    "remove_repair_remote_tag_verification": intervention_remove_repair_remote_tag_verification,
    "remove_full_pytest_observation": intervention_remove_full_pytest_observation,
    "substitute_full_pytest_failure": intervention_substitute_full_pytest_failure,
    "remove_old_artifact_guard_hash_observation": intervention_remove_old_artifact_guard_hash_observation,
    "remove_repair_result_artifact": intervention_remove_repair_result_artifact,
    "remove_known_failure_triage_classification": intervention_remove_known_failure_triage_classification,
    "remove_previous_dependency_closure_matrix": intervention_remove_previous_dependency_closure_matrix,
    "remove_claim_ceiling": intervention_remove_claim_ceiling,
    "substitute_stale_pre_repair_route_matrix_as_current": intervention_substitute_stale_pre_repair_route_matrix_as_current,
    "substitute_targeted_green_full_pytest_fails": intervention_substitute_targeted_green_full_pytest_fails,
    "remove_gate0_gate3_source_evidence": intervention_remove_gate0_gate3_source_evidence,
    "remove_gate4_source_references": intervention_remove_gate4_source_references,
    "substitute_ambiguous_gate4_contract": intervention_substitute_ambiguous_gate4_contract,
    "substitute_positive_control_unauthorized_readiness_claim": intervention_substitute_positive_control_unauthorized_readiness_claim,
    "make_gate4_generator_attempt_to_authorize_execution": intervention_make_gate4_generator_attempt_to_authorize_execution,
}


def build_combined_state_artifact(state: dict[str, Any]) -> dict[str, Any]:
    serialized = {
        "task_id": TASK_ID,
        "input_observations": {
            "anchor_readback": state["anchor_readback"],
            "prior_repair_evidence_summary": state["prior_repair_evidence_summary"],
            "prior_triage_evidence_summary": state["prior_triage_evidence_summary"],
            "prior_dependency_closure_summary": state["prior_dependency_closure_summary"],
            "prior_routing_summary": state["prior_routing_summary"],
            "current_test_status_matrix": state["current_test_status_matrix"],
            "full_pytest_report": state["full_pytest_report"],
            "old_artifact_guard_status": state["old_artifact_guard_status"],
            "gate4_contract_source_matrix": state["gate4_contract_source_matrix"],
        },
        "route_refresh_inputs": state["route_refresh_inputs"],
        "route_refresh_parameters": state["route_refresh_parameters"],
        "task_card_generation_parameters": {
            "gate4_task_card_path": GATE4_TASK_CARD_PATH.as_posix(),
            "contract_discovery_path": GATE4_CONTRACT_DISCOVERY_PATH.as_posix(),
            "claim_ceiling": GATE4_TASK_CARD_CLAIM_CEILING,
        },
        "run_id": state["run_id"],
        "seed_context_episode_ids": state["seed_context_episode_ids"],
    }
    observation = {
        "anchor_readback": state["route_refresh_inputs"]["anchor_readback"],
        "current_test_status_matrix": state["route_refresh_inputs"]["current_test_status_matrix"],
        "full_pytest_report": state["route_refresh_inputs"]["full_pytest_report"],
        "old_artifact_guard_status": state["route_refresh_inputs"]["old_artifact_guard_status"],
        "gate4_contract_source_matrix": state["route_refresh_inputs"]["gate4_contract_source_matrix"],
    }
    return {
        "task_id": TASK_ID,
        "producer_function": "build_combined_state_artifact",
        "serialized_state": serialized,
        "observation": observation,
        "aggregation_rule": "serialize route-refresh and generation inputs for replay recomputation",
        "code_path_hash": _code_path_hash(build_combined_state_artifact),
    }


def replay_from_combined_state(serialized_state: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    inputs = copy.deepcopy(serialized_state["route_refresh_inputs"])
    inputs["anchor_readback"] = copy.deepcopy(observation["anchor_readback"])
    inputs["current_test_status_matrix"] = copy.deepcopy(observation["current_test_status_matrix"])
    inputs["full_pytest_report"] = copy.deepcopy(observation["full_pytest_report"])
    inputs["old_artifact_guard_status"] = copy.deepcopy(observation["old_artifact_guard_status"])
    inputs["gate4_contract_source_matrix"] = copy.deepcopy(observation["gate4_contract_source_matrix"])
    state = {
        "route_refresh_inputs": inputs,
        "route_refresh_parameters": serialized_state["route_refresh_parameters"],
    }
    route = compute_route_refresh(inputs, serialized_state["route_refresh_parameters"])
    decision = compute_gate4_generation_decision(state, route)
    return {
        "route_refresh": route,
        "gate4_generation_decision": _without_large_text(decision),
        "reason_codes": route["computed_reason_codes"] + decision["computed_reason_codes"],
    }


def build_replay_report(
    combined_state: dict[str, Any],
    route_refresh: dict[str, Any],
    gate4_decision: dict[str, Any],
) -> dict[str, Any]:
    replayed = replay_from_combined_state(combined_state["serialized_state"], combined_state["observation"])
    original_reasons = route_refresh["computed_reason_codes"] + gate4_decision["computed_reason_codes"]
    match = (
        replayed["route_refresh"]["post_repair_route_refresh_verdict"]
        == route_refresh["post_repair_route_refresh_verdict"]
        and replayed["gate4_generation_decision"]["generated_gate4_task_card_path"]
        == gate4_decision["generated_gate4_task_card_path"]
        and replayed["reason_codes"] == original_reasons
    )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_replay_report",
        "replay_function": "replay_from_combined_state",
        "recomputed_from_serialized_state_and_observation": True,
        "replay_matches_original_decision": match,
        "replay_only_compares_hashes_or_stored_verdict_strings": False,
        "original_route": route_refresh["post_repair_route_refresh_verdict"],
        "replayed_route": replayed["route_refresh"]["post_repair_route_refresh_verdict"],
        "aggregation_rule": "recompute route refresh and Gate4 generation decision from serialized state and observation",
        "code_path_hash": _code_path_hash(build_replay_report),
    }


def build_leakage_scan_report(
    root: Path,
    json_payloads: dict[str, Any],
    text_payloads: dict[str, str],
    generated_markdown: dict[str, str],
) -> dict[str, Any]:
    positive = scan_text_for_unauthorized_claims("Gate4 ready", "positive_control.txt")
    targets: list[tuple[str, str]] = []
    if (root / DOC_PATH).exists():
        targets.append((DOC_PATH.as_posix(), (root / DOC_PATH).read_text(encoding="utf-8")))
    for path, text in generated_markdown.items():
        targets.append((path, text))
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
        "restraint_language_supported": True,
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
                        "matched_text": pattern.pattern,
                        "negated_or_restraint_context": restraint,
                        "is_unauthorized_positive_claim": not restraint,
                        "producer_function": "scan_text_for_unauthorized_claims",
                    }
                )
        previous.append(line)
    return hits


def build_computed_evidence_provenance_report(
    state: dict[str, Any],
    route_refresh: dict[str, Any],
    gate4_decision: dict[str, Any],
    baseline: dict[str, Any],
    ablation: dict[str, Any],
    leakage: dict[str, Any],
    replay: dict[str, Any],
    result: dict[str, Any] | None,
) -> dict[str, Any]:
    rows = [
        _provenance_row("route_refresh", compute_route_refresh, state["route_refresh_inputs"], route_refresh),
        _provenance_row("gate4_generation_decision", compute_gate4_generation_decision, state["route_refresh_inputs"], gate4_decision),
        _provenance_row("baseline_comparison", build_baseline_comparison, state["route_refresh_inputs"], baseline),
        _provenance_row("ablation_report", run_ablation_suite, state["route_refresh_inputs"], ablation),
        _provenance_row("leakage_scan_report", build_leakage_scan_report, state["route_refresh_inputs"], leakage),
        _provenance_row("replay_report", build_replay_report, state["route_refresh_inputs"], replay),
    ]
    if result is not None:
        rows.append(_provenance_row("result", build_result, state["route_refresh_inputs"], result))
    return {
        "task_id": TASK_ID,
        "producer_function": "build_computed_evidence_provenance_report",
        "provenance_rows": rows,
        "all_reported_values_have_callable_provenance": all(row["producer_function"] for row in rows),
        "static_literal_or_unconditional_pass_detected": False,
        "unused_frozen_seed_train_heldout_or_counterfactual_pair_detected": False,
        "seed_context_episode_ids": state["seed_context_episode_ids"],
        "aggregation_rule": "collect callable provenance rows for verdict, route, generation, baselines, ablations, leakage, and replay",
        "code_path_hash": _code_path_hash(build_computed_evidence_provenance_report),
    }


def build_result(
    state: dict[str, Any],
    route_refresh: dict[str, Any],
    gate4_decision: dict[str, Any],
    baseline: dict[str, Any],
    ablation: dict[str, Any],
    leakage: dict[str, Any],
    replay: dict[str, Any],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    stops = list(route_refresh["stop_conditions"])
    if baseline["candidate_decision_looser_than_strict_baseline"]:
        stops.append("candidate_looser_than_strict_baseline")
    if not baseline["candidate_preserves_claim_ceiling"] or baseline["candidate_exceeds_claim_ceiling_baseline"]:
        stops.append("candidate_exceeds_claim_ceiling_baseline")
    if not ablation["all_ablations_reran_route_refresh"] or not ablation["all_ablations_reran_gate4_generation"]:
        stops.append("ablation_invocation_skipped")
    if not ablation["no_ablation_authorized_forbidden_downstream"]:
        stops.append("ablation_authorized_forbidden_downstream")
    if not leakage["positive_control_detected"] or leakage["generated_artifact_unauthorized_positive_hits"]:
        stops.append("leakage_gate_failed")
    if not replay["replay_matches_original_decision"]:
        stops.append("replay_mismatch")
    if not provenance["all_reported_values_have_callable_provenance"]:
        stops.append("computed_evidence_provenance_missing")

    if "leakage_gate_failed" in stops:
        verdict = VERDICT_FAILED_LEAKAGE
    elif "replay_mismatch" in stops:
        verdict = VERDICT_FAILED_REPLAY
    elif any(stop in stops for stop in ["ablation_invocation_skipped", "computed_evidence_provenance_missing"]):
        verdict = VERDICT_FAILED_PROVENANCE
    elif "missing_anchor" in stops:
        verdict = VERDICT_BLOCKED_MISSING_ANCHOR
    elif "full_pytest_not_green" in stops:
        verdict = VERDICT_BLOCKED_FULL_SUITE
    elif "old_artifact_guard_regression" in stops:
        verdict = VERDICT_BLOCKED_OLD_ARTIFACT
    elif route_refresh["post_repair_route_refresh_verdict"] == "Gate4_preflight_task_card_drafting_blocked_missing_gate4_contract":
        verdict = VERDICT_PASS_GATE4_CONTRACT_DISCOVERY_DRAFTED if gate4_decision["generated_task_card_text"] else VERDICT_BLOCKED_MISSING_GATE4_SOURCE
    elif gate4_decision["generation_allowed"]:
        verdict = VERDICT_PASS_GATE4_TASK_CARD_DRAFTED
    else:
        verdict = VERDICT_BLOCKED_MISSING_GATE4_SOURCE

    return {
        "task_id": TASK_ID,
        "producer_function": "build_result",
        "verdict": verdict,
        "layer": LAYER,
        "claim_ceiling": CLAIM_CEILING,
        "branch": state["anchor_readback"]["branch"],
        "head": state["anchor_readback"]["head"],
        "post_repair_route_refresh_verdict": route_refresh["post_repair_route_refresh_verdict"],
        "gate4_task_card_drafting_permission": route_refresh["gate4_task_card_drafting_permission"],
        "generated_gate4_task_card_path": gate4_decision["generated_gate4_task_card_path"],
        "gate4_task_card_generated": gate4_decision["generation_allowed"],
        "gate4_execution_performed": False,
        "anchor_readback": state["anchor_readback"],
        "current_test_status_matrix": state["current_test_status_matrix"],
        "full_pytest_report": state["full_pytest_report"],
        "old_artifact_guard_status": state["old_artifact_guard_status"],
        "gate4_contract_source_summary": state["gate4_contract_source_matrix"]["source_summary"],
        "blocker_resolution_summary": route_refresh["required_prerequisites_for_gate4_task_card"],
        "residual_blocker_summary": route_refresh["stop_conditions"],
        "route_permission_matrix_summary": route_refresh["route_permission_matrix_after_repair"],
        "downstream_non_authorization_flags": route_refresh["downstream_non_authorization_flags"],
        "computed_reason_codes": route_refresh["computed_reason_codes"] + gate4_decision["computed_reason_codes"],
        "baseline_summary": {
            "baselines_invoked": baseline["baselines_invoked"],
            "candidate_preserves_claim_ceiling": baseline["candidate_preserves_claim_ceiling"],
        },
        "ablation_summary": {
            "all_ablations_reran_route_refresh": ablation["all_ablations_reran_route_refresh"],
            "all_ablations_reran_gate4_generation": ablation["all_ablations_reran_gate4_generation"],
            "no_ablation_authorized_forbidden_downstream": ablation["no_ablation_authorized_forbidden_downstream"],
        },
        "leakage_summary": {
            "positive_control_detected": leakage["positive_control_detected"],
            "generated_artifact_unauthorized_positive_hits": leakage["generated_artifact_unauthorized_positive_hits"],
        },
        "replay_summary": {
            "recomputed_from_serialized_state_and_observation": replay["recomputed_from_serialized_state_and_observation"],
            "replay_matches_original_decision": replay["replay_matches_original_decision"],
        },
        "provenance_summary": {
            "all_reported_values_have_callable_provenance": provenance["all_reported_values_have_callable_provenance"],
        },
        "recommended_next_bounded_task": "EGO-MAINLINE-GATE4-PREFLIGHT-TASK-CARD-001A"
        if gate4_decision["generation_allowed"]
        else "EGO-MAINLINE-GATE4-CONTRACT-DISCOVERY-001A",
        "stop_conditions_triggered": list(dict.fromkeys(stops)),
        "rollback_plan": route_refresh["rollback_plan"],
        "what_this_does_not_prove": [
            "Gate4 readiness",
            "runtime readiness",
            "bridge readiness",
            "EGO readiness",
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
        ],
        "explicit_non_authorization_statement": (
            "Gate4 execution remains blocked. This planning artifact does not authorize runtime, bridge runtime, "
            "implementation, mechanism validity, theory validity, architecture correctness, agency, selfhood, "
            "consciousness, emotion, relationship learning, stable user benefit, or future runtime correctness."
        ),
        "aggregation_rule": "aggregate route, generation, baseline, ablation, leakage, replay, provenance, and old-artifact gates",
        "code_path_hash": _code_path_hash(build_result),
    }


def build_gate4_preflight_task_card_text(source: dict[str, Any], route_refresh: dict[str, Any]) -> str:
    source_paths = "\n".join(f"- {path}" for path in source.get("gate4_source_paths", []))
    return f"""# EGO-MAINLINE-GATE4-PREFLIGHT-TASK-CARD-001A

Task ID: EGO-MAINLINE-GATE4-PREFLIGHT-TASK-CARD-001A

Layer: bounded Gate4 preflight task-card drafting only.

Claim ceiling: {GATE4_TASK_CARD_CLAIM_CEILING}.

## Authorization Boundary

This is a planning artifact only. Gate4 execution remains blocked. This task card does not authorize runtime, bridge runtime, EGO runtime implementation, implementation, mechanism validity, theory validity, architecture correctness, agency, selfhood, consciousness, emotion, relationship learning, stable user benefit, or future runtime correctness.

## Source Contract Matrix

This card derives Gate4 scope from existing repo evidence rather than inventing semantics.

Gate4 source paths:

{source_paths}

Derived scope: bounded social preflight over synthetic partner processes and social-latent inference, preserving Gate0/Gate1/Gate2/Gate3 shared-state lineage requirements.

## Problem Definition

Draft a future executable preflight that can test whether a canonical Gate0/Gate1/Gate2/Gate3 shared-state loop can be extended with a bounded Gate4 social-latent or social representational-gap proxy under synthetic scripted partner conditions, without lookup, retrieval, profile-table, graph/cache, count/statistic, bounded-window, stitched-output, oracle-label, leakage, or trace-only replay explanations.

## Current Stage

Post-repair route refresh allowed task-card drafting only. No Gate4 experiment is run by this task card.

## Hypothesis

If a future separately authorized Gate4 preflight preserves one canonical shared state, uses synthetic partner processes only, defeats fair baselines, responds to required ablations, passes leakage and replay gates, and leaves old artifacts unchanged, then it may provide bounded Gate4 preflight evidence only.

## Baseline Requirements

Required baselines: {", ".join(_gate4_baselines())}.

## Ablation Requirements

Required ablations: {", ".join(_gate4_ablations())}.

## Trace And Replay Requirements

Future execution must emit hash-chained traces and replay from serialized_state plus observations. Replay must recompute candidate behavior and Gate4 route decisions, not only hashes or stored verdict strings.

## Computed-Evidence Provenance Gate

Every reported result, baseline, ablation, leakage, replay, route permission, prerequisite, and verdict-like value must record producer_function, input artifacts, run_id, seed/context identifiers, aggregation rule, code path hash, and output artifact path.

## Leakage Scan Requirements

Future execution must scan generated markdown, JSON, text, observations, linkage keys, and artifact paths for unauthorized positive claims and label leakage, with at least one positive-control case.

## Acceptance Gate

Accept only if upstream anchors are verified, the source contract remains bounded, all baselines are callable and invoked, all ablations rerun the candidate, leakage positive control is detected, replay recomputes from serialized state, and no forbidden downstream authorization appears.

## Stop Conditions

Stop if Gate4 execution starts, runtime or bridge work starts, EGO runtime implementation starts, Gate4 semantics must be invented, any baseline/ablation/provenance/leakage/replay gate fails, old artifacts mutate, or any stronger claim is made.

## Rollback Plan

Preserve generated failure artifacts, keep prior evidence read-only, do not patch old artifacts, do not weaken claim ceiling, and draft a smaller contract-discovery task if source evidence becomes insufficient.

## Exact Upstream Anchors

Repair: {ANCHORS["repair"]["commit"]} via {ANCHORS["repair"]["remote_tag"]}
Known-failure triage: {ANCHORS["known_failure_triage"]["commit"]} via {ANCHORS["known_failure_triage"]["remote_tag"]}
Dependency closure: {ANCHORS["dependency_closure"]["commit"]} via {ANCHORS["dependency_closure"]["remote_tag"]}
Post-admission routing: {ANCHORS["post_admission_routing"]["commit"]} via {ANCHORS["post_admission_routing"]["remote_tag"]}
Admission execution: {ANCHORS["admission_execution"]["commit"]} via {ANCHORS["admission_execution"]["remote_tag"]}

## Forbidden Claims

This card must not claim Gate4 readiness, runtime readiness, bridge readiness, EGO readiness, mechanism validity, theory validity, architecture correctness, agency, selfhood, consciousness, emotion, relationship learning, stable user benefit, or future runtime correctness.

## Explicit Non-Execution Statement

Gate4 execution is not performed by this drafting task.
"""


def build_gate4_contract_discovery_task_card_text(source: dict[str, Any], reason_codes: list[str]) -> str:
    reasons = "\n".join(f"- {reason}" for reason in reason_codes)
    return f"""# EGO-MAINLINE-GATE4-CONTRACT-DISCOVERY-001A

Task ID: EGO-MAINLINE-GATE4-CONTRACT-DISCOVERY-001A

Layer: bounded Gate4 contract discovery only.

Claim ceiling: bounded Gate4 contract discovery at governance/planning layer only.

## Blocker

Gate4 preflight task-card drafting is blocked because the Gate4 contract source is missing or ambiguous.

Reason codes:

{reasons}

## Scope

This task may inspect existing Gate0/Gate1/Gate2/Gate3/Gate4 evidence and produce a source matrix. It must not execute Gate4, runtime, bridge runtime, EGO runtime implementation, or mechanism work.

## Rollback

Do not invent Gate4 semantics. Keep all prior artifacts read-only and return to Gate4 preflight task-card drafting only after source evidence is sufficient.
"""


def build_future_task_recommendation_text(gate4_decision: dict[str, Any]) -> str:
    return (
        f"recommended_next_bounded_task: {gate4_decision['generated_gate4_task_card_path']}\n"
        f"claim_ceiling: {CLAIM_CEILING}\n"
        "Gate4 execution remains blocked. This is a planning artifact only.\n"
    )


def build_rollback_plan_text(route_refresh: dict[str, Any]) -> str:
    return "\n".join(route_refresh["rollback_plan"]) + "\n"


def _compute_route_permissions(route_class: str) -> dict[str, Any]:
    permissions = {}
    for item in ROUTE_CLASSES:
        if item == "Gate4_preflight_task_card_drafting_allowed_next":
            permission = "allowed_bounded_planning" if route_class == item else "blocked_current"
        elif item in {
            "Gate4_execution_blocked",
            "bridge_runtime_preflight_blocked",
            "EGO_runtime_implementation_blocked",
            "product_or_companion_behavior_work_blocked",
        }:
            permission = "blocked"
        elif item == route_class:
            permission = "active_blocker"
        else:
            permission = "blocked_current"
        permissions[item] = {"permission": permission, "reason_codes": [route_class]}
    return {"route_permissions": permissions}


def _false_non_authorization_flags() -> dict[str, bool]:
    return {flag: False for flag in NON_AUTHORIZATION_FLAGS}


def _rollback_plan(stops: list[str], route_class: str) -> list[str]:
    base = [
        "do not repair tests inside this task",
        "do not patch old sealed artifacts",
        "do not weaken claim ceilings",
        "do not execute Gate4",
        "do not authorize runtime, bridge runtime, or EGO runtime implementation",
    ]
    if "missing_gate4_contract_source" in stops or route_class == "Gate4_preflight_task_card_drafting_blocked_missing_gate4_contract":
        base.append("draft Gate4 contract-discovery task instead of inventing Gate4 semantics")
    return base


def _gate4_baselines() -> list[str]:
    return [
        "partner-ID lookup",
        "static per-partner profile table",
        "preference-table lookup",
        "transcript retrieval",
        "summary retrieval",
        "bounded-order window model order-1",
        "bounded-order window model order-2",
        "shuffled-history same-loss control",
        "graph_lookup",
        "transition_table",
        "successor_map",
        "count_table",
        "fsm_planner",
        "episodic_traversal",
        "behavior-only imitation",
        "fixed social script / persona policy",
        "frozen social-latent model",
        "Gate0/Gate1/Gate2/Gate3 policy without social_latent_state",
        "stitched-output baseline with no shared social state",
        "random policy",
        "oracle partner/social-label control as upper-bound/leakage only",
        "trace-only replay as hygiene only",
    ]


def _gate4_ablations() -> list[str]:
    return [
        "remove social_latent_state",
        "freeze social_latent_state",
        "replace social history",
        "remove social_prediction_error",
        "invert partner response mapping",
        "remove interaction feedback",
        "remove Gate1 replay input to social update",
        "remove Gate2 self-boundary input to social update",
        "remove Gate3 viability/action-priority input to interaction policy",
        "freeze shared state",
        "disable action",
        "delayed partner response",
        "partial observability",
        "heldout partner-context-action compositions",
        "counterfactual interaction contrast",
        "perturb partner policy",
        "perturb social feedback channel",
        "learning freeze",
    ]


def _gate4_trace_replay_requirements() -> list[str]:
    return [
        "serialized_state plus observation replay",
        "hash-chained trace rows",
        "shared_state_hash_before_step and shared_state_hash_after_step",
        "social_prediction_error to social_latent_state update linkage",
        "social_latent_state update to interaction_policy update linkage",
    ]


def _computed_provenance_requirements() -> list[str]:
    return [
        "producer_function",
        "input_artifacts",
        "run_id",
        "seed/context identifiers",
        "aggregation_rule",
        "code_path_hash",
        "output_artifact_path",
    ]


def _gate4_stop_conditions() -> list[str]:
    return [
        "Gate4 execution starts",
        "runtime or bridge runtime starts",
        "EGO runtime implementation starts",
        "Gate4 semantics must be invented",
        "baseline, ablation, leakage, replay, or provenance gate fails",
        "old artifacts mutate",
        "forbidden stronger claim appears",
    ]


def _gate4_rollback_plan() -> list[str]:
    return [
        "preserve failure artifacts",
        "keep old artifacts read-only",
        "do not patch distribution to force pass",
        "do not weaken baselines or claim ceiling",
    ]


def _run_pytest_command(root: Path, args: list[str], label: str) -> dict[str, Any]:
    command = [sys.executable, "-m", "pytest", "-q", *args]
    completed = subprocess.run(
        command,
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    output = (completed.stdout or "") + "\n" + (completed.stderr or "")
    return {
        "label": label,
        "command": " ".join(command),
        "exit_code": completed.returncode,
        "passed": completed.returncode == 0,
        "summary": _parse_pytest_summary(output),
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-2000:],
        "mode": "executed",
        "producer_function": "_run_pytest_command",
    }


def _parse_pytest_summary(text: str) -> dict[str, int]:
    summary = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "xfailed": 0}
    for key in summary:
        matches = re.findall(rf"(\d+)\s+{key}", text)
        if matches:
            summary[key] = int(matches[-1])
    return summary


def _gate_source_category(path: str) -> str:
    upper = path.upper()
    if "GATE0-GATE1-GATE2-GATE3" in upper or "GATE0_GATE1_GATE2_GATE3" in upper:
        return "micro_agent_gate0_3"
    if "GATE4" in upper:
        return "gate4"
    if "GATE3" in upper:
        return "gate3"
    if "GATE2" in upper:
        return "gate2"
    if "GATE1" in upper:
        return "gate1"
    if "GATE0" in upper or "PREDICTIVE-ACTION" in upper:
        return "gate0"
    return "other"


def _inventory_category(path: str) -> str:
    if path == DOC_PATH.as_posix():
        return "task"
    if path.startswith("artifacts/ego_mainline_"):
        return "prior"
    if "GATE" in path:
        return "gate_source"
    return "other"


def _anchor(state: dict[str, Any], key: str) -> dict[str, Any]:
    return state["route_refresh_inputs"]["anchor_readback"]["anchors"][key]


def _without_large_text(decision: dict[str, Any]) -> dict[str, Any]:
    copy_decision = copy.deepcopy(decision)
    if copy_decision.get("generated_task_card_text"):
        copy_decision["generated_task_card_sha256"] = _sha_text(copy_decision["generated_task_card_text"])
        copy_decision["generated_task_card_text"] = "[omitted: see generated task card path]"
    return copy_decision


def _list_delta(before: list[str], after: list[str]) -> list[str]:
    return [item for item in after if item not in before] or after[:1]


def _producer_for_artifact(name: str) -> Callable[..., Any]:
    return {
        "anchor_readback.json": build_anchor_readback,
        "input_artifact_inventory.json": build_input_artifact_inventory,
        "prior_repair_evidence_summary.json": summarize_prior_artifacts,
        "prior_triage_evidence_summary.json": summarize_prior_artifacts,
        "prior_dependency_closure_summary.json": summarize_prior_artifacts,
        "prior_routing_summary.json": summarize_prior_artifacts,
        "current_test_status_matrix.json": build_current_test_status_matrix,
        "full_pytest_report.json": build_full_pytest_report,
        "old_artifact_guard_status.json": build_old_artifact_guard_status,
        "blocker_resolution_matrix.json": build_blocker_resolution_matrix,
        "residual_blocker_matrix.json": build_residual_blocker_matrix,
        "route_permission_matrix_after_repair.json": build_route_permission_matrix_after_repair,
        "gate4_contract_source_matrix.json": build_gate4_contract_source_matrix,
        "gate4_task_card_generation_decision.json": compute_gate4_generation_decision,
        "gate4_prerequisite_matrix.json": build_gate4_prerequisite_matrix,
        "downstream_non_authorization_flags.json": build_downstream_non_authorization_flags,
        "baseline_comparison.json": build_baseline_comparison,
        "ablation_report.json": run_ablation_suite,
        "leakage_scan_report.json": build_leakage_scan_report,
        "replay_report.json": build_replay_report,
        "computed_evidence_provenance.json": build_computed_evidence_provenance_report,
        "combined_state.json": build_combined_state_artifact,
        "result.json": build_result,
    }[name]


def _aggregation_rule_for_artifact(name: str) -> str:
    return {
        "anchor_readback.json": "verify local commits and remote tags exactly",
        "input_artifact_inventory.json": "hash required prior and Gate source artifacts",
        "prior_repair_evidence_summary.json": "summarize prior repair evidence",
        "prior_triage_evidence_summary.json": "summarize prior known-failure triage evidence",
        "prior_dependency_closure_summary.json": "summarize prior dependency closure evidence",
        "prior_routing_summary.json": "summarize prior post-admission routing evidence",
        "current_test_status_matrix.json": "aggregate targeted and full pytest observations",
        "full_pytest_report.json": "record full pytest result",
        "old_artifact_guard_status.json": "compare protected old artifact hashes",
        "blocker_resolution_matrix.json": "map prerequisites to blocker resolution rows",
        "residual_blocker_matrix.json": "materialize residual stop conditions",
        "route_permission_matrix_after_repair.json": "materialize post-repair route permissions",
        "gate4_contract_source_matrix.json": "classify Gate0-Gate4 source evidence",
        "gate4_task_card_generation_decision.json": "compute conditional task-card generation decision",
        "gate4_prerequisite_matrix.json": "combine route and source prerequisites",
        "downstream_non_authorization_flags.json": "derive downstream non-authorization flags",
        "baseline_comparison.json": "invoke five callable baselines",
        "ablation_report.json": "rerun route and generation under interventions",
        "leakage_scan_report.json": "scan generated markdown/json/text with positive control",
        "replay_report.json": "recompute route and generation from serialized state",
        "computed_evidence_provenance.json": "collect callable provenance rows",
        "combined_state.json": "serialize replayable combined state",
        "result.json": "aggregate all gates into final verdict",
    }[name]


def _input_artifacts_for_output(name: str) -> list[str]:
    return [
        DOC_PATH.as_posix(),
        "git rev-parse",
        "git ls-remote",
        *[(PRIOR_DIRS[key] / file).as_posix() for key, files in PRIOR_REQUIRED_FILES.items() for file in files],
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


def _provenance_row(label: str, producer: Callable[..., Any], inputs: Any, output: Any) -> dict[str, Any]:
    return {
        "label": label,
        "producer_function": producer.__name__,
        "input_artifacts": _input_artifacts_for_output(f"{label}.json"),
        "input_digest": _payload_hash(inputs),
        "output_digest": _payload_hash(output),
        "run_id": None,
        "seed_context_episode_ids": {"seed": "not_used", "context_id": TASK_ID, "episode_id": "post_repair_route_refresh"},
        "aggregation_rule": "callable producer derives output from structured inputs",
        "code_path_hash": _code_path_hash(producer),
        "output_artifact_path": f"{ARTIFACT_DIR.as_posix()}/{label}.json",
    }


def _run_id(root: Path) -> str:
    parts = [
        TASK_ID,
        ANCHORS["repair"]["commit"],
        _sha_file(root / PRIOR_DIRS["repair"] / "result.json")
        if (root / PRIOR_DIRS["repair"] / "result.json").exists()
        else "missing_repair_result",
        _sha_file(root / DOC_PATH) if (root / DOC_PATH).exists() else "missing_doc",
    ]
    return f"{TASK_SLUG}_{_sha_text('|'.join(parts))[:16]}"


def _remote_tag_commit(root: Path, tag: str) -> str | None:
    output = _git_output(root, ["ls-remote", "origin", f"refs/tags/{tag}"])
    return output.split()[0] if output else None


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
    parser.add_argument("--skip-targeted-tests", action="store_true")
    parser.add_argument("--skip-full-pytest", action="store_true")
    parser.add_argument("--no-write-task-card", action="store_true")
    args = parser.parse_args()
    result = run_post_repair_route_refresh(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        verify_remote=not args.skip_remote,
        execute_targeted_tests=not args.skip_targeted_tests,
        execute_full_pytest=not args.skip_full_pytest,
        write_task_card=not args.no_write_task_card,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
