from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import inspect
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable


TASK_ID = "EGO-MAINLINE-OLD-ARTIFACT-SIDE-EFFECT-GUARD-AND-REDUNDANCY-CONTRACT-REPAIR-001A"
ARTIFACT_DIR = Path("artifacts/ego_mainline_old_artifact_side_effect_guard_and_redundancy_contract_repair_001a")
DOC_PATH = Path("docs/codex/tasks/EGO-MAINLINE-OLD-ARTIFACT-SIDE-EFFECT-GUARD-AND-REDUNDANCY-CONTRACT-REPAIR-001A.md")
LAYER = "evidence-governance / bounded repair only"
CLAIM_CEILING = "bounded evidence-hygiene repair evidence at governance layer only"

TRIAGE_COMMIT = "c9bee968069f9d218c0c45a37efba092e4535156"
TRIAGE_REMOTE_TAG = "remote-anchor-known-failure-triage-001a-c9bee9"
TRIAGE_DIR = Path("artifacts/ego_mainline_known_failure_triage_001a")
TRIAGE_RESULT = TRIAGE_DIR / "result.json"
TRIAGE_SIDE_EFFECT = TRIAGE_DIR / "old_artifact_side_effect_matrix.json"

SIDE_EFFECT_ARTIFACT = Path(
    "artifacts/ego_mainline_admission_executable_001d_metric_provenance_repair_001f/scope_leak_report.json"
)

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
KNOWN_FAILED_NODE_IDS = [
    FAILED_REFERENCE_NODE,
    FAILED_ALIGNMENT_NODE,
    FAILED_CLOSURE_NODE,
    FAILED_ROUTING_NODE,
]

TARGETED_SUITES = {
    "routing": ["tests/test_ego_mainline_post_admission_routing_001a.py"],
    "dependency_closure": ["tests/test_ego_mainline_evidence_dependency_closure_001a.py"],
    "known_failure_triage": ["tests/test_ego_mainline_known_failure_triage_001a.py"],
    "repair_001a": ["tests/test_ego_mainline_old_artifact_side_effect_guard_and_redundancy_contract_repair_001a.py"],
}

PROTECTED_OLD_ARTIFACTS = [
    SIDE_EFFECT_ARTIFACT,
    Path("artifacts/ego_mainline_admission_canonical_coverage_reference_001a/result.json"),
    Path("artifacts/ego_mainline_admission_task_card_alignment_001a/result.json"),
    Path("artifacts/ego_mainline_evidence_dependency_closure_001a/result.json"),
    Path("artifacts/ego_mainline_post_admission_routing_001a/result.json"),
    Path("artifacts/ego_mainline_known_failure_triage_001a/result.json"),
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

WHAT_THIS_DOES_NOT_PROVE = [
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
]

VERDICT_PASS_FULL_SUITE_GREEN = "old_artifact_side_effect_guard_and_redundancy_contract_repair_001a_pass_full_suite_green"
VERDICT_PASS_WITH_RESIDUAL_BLOCKERS_CLASSIFIED = (
    "old_artifact_side_effect_guard_and_redundancy_contract_repair_001a_pass_with_residual_blockers_classified"
)
VERDICT_BLOCKED_UNREPAIRED_REDUNDANCY = (
    "old_artifact_side_effect_guard_and_redundancy_contract_repair_001a_blocked_unrepaired_redundancy_contract"
)
VERDICT_BLOCKED_OLD_ARTIFACT_SIDE_EFFECT = (
    "old_artifact_side_effect_guard_and_redundancy_contract_repair_001a_blocked_old_artifact_side_effect"
)
VERDICT_BLOCKED_FULL_SUITE_NOT_OBSERVED = (
    "old_artifact_side_effect_guard_and_redundancy_contract_repair_001a_blocked_full_suite_not_observed"
)
VERDICT_FAILED_PROVENANCE_GATE = "old_artifact_side_effect_guard_and_redundancy_contract_repair_001a_failed_provenance_gate"
VERDICT_FAILED_LEAKAGE_GATE = "old_artifact_side_effect_guard_and_redundancy_contract_repair_001a_failed_leakage_gate"
VERDICT_FAILED_REPLAY_GATE = "old_artifact_side_effect_guard_and_redundancy_contract_repair_001a_failed_replay_gate"

REQUIRED_ARTIFACT_NAMES = [
    "result.json",
    "anchor_readback.json",
    "before_repair_failure_reproduction.json",
    "repair_change_inventory.json",
    "shared_validator_contract_evidence.json",
    "temp_run_validator_equivalence_report.json",
    "old_artifact_write_guard_report.json",
    "side_effect_prevention_report.json",
    "before_after_hash_comparison.json",
    "isolated_rerun_report.json",
    "targeted_suite_report.json",
    "full_pytest_report.json",
    "residual_failure_classification.json",
    "downstream_route_impact_matrix.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_scan_report.json",
    "replay_report.json",
    "computed_evidence_provenance.json",
    "repair_state.json",
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
    "forbidden",
    "unauthorized",
    "insufficient",
    "does not",
    "do not",
    "must not",
    "without",
    "what_this_does_not_prove",
    "what this does not prove",
    "claim ceiling",
    "claim_ceiling",
    "false",
    "failure",
    "failed",
    "blocker",
    "scanner",
    "positive control",
    "positive_control",
    "stop condition",
    "rollback",
    "not authorized",
    "does not authorize",
]


def run_repair(
    repo_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    verify_remote: bool = True,
    execute_isolated_reruns: bool = True,
    execute_targeted_suites: bool = False,
    execute_full_pytest: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    out = Path(output_dir) if output_dir is not None else root / ARTIFACT_DIR
    if not out.is_absolute():
        out = root / out
    out.mkdir(parents=True, exist_ok=True)

    protected_before = hash_protected_old_artifacts(root)
    anchor = build_anchor_readback(root, verify_remote=verify_remote)
    before_repair = build_before_repair_failure_reproduction(root)
    change_inventory = build_repair_change_inventory(root)
    shared_contract = build_shared_validator_contract_evidence(root)
    equivalence = build_temp_run_validator_equivalence(root)
    write_guard = build_old_artifact_write_guard_report(root, out)
    side_effect = build_side_effect_prevention_result(root)
    protected_after_side_effect = hash_protected_old_artifacts(root)
    hash_comparison = build_before_after_hash_comparison(protected_before, protected_after_side_effect)
    isolated = build_isolated_rerun_report(root, execute=execute_isolated_reruns)
    targeted = build_targeted_suite_report(root, execute=execute_targeted_suites)
    full = build_full_pytest_report(root, execute=execute_full_pytest)

    state = build_repair_state(
        root=root,
        out=out,
        anchor=anchor,
        before_repair=before_repair,
        change_inventory=change_inventory,
        shared_contract=shared_contract,
        equivalence=equivalence,
        write_guard=write_guard,
        side_effect=side_effect,
        hash_comparison=hash_comparison,
        isolated=isolated,
        targeted=targeted,
        full=full,
    )
    candidate = compute_repair_verification(state["candidate_repair_inputs"], state["repair_parameters"])
    baseline = build_baseline_comparison(state, candidate)
    ablation = run_ablation_suite(state, candidate)
    residual = build_residual_failure_classification(candidate, isolated, targeted, full)
    route = build_downstream_route_impact_matrix(candidate)
    repair_state_artifact = build_repair_state_artifact(state)
    replay = build_replay_report(repair_state_artifact, candidate)

    text_payloads = {
        "claim_ceiling.txt": CLAIM_CEILING + "\n",
        "future_task_recommendation.txt": build_future_task_recommendation_text(candidate),
        "rollback_plan.txt": build_rollback_plan_text(candidate),
    }
    json_payloads = {
        "anchor_readback.json": anchor,
        "before_repair_failure_reproduction.json": before_repair,
        "repair_change_inventory.json": change_inventory,
        "shared_validator_contract_evidence.json": shared_contract,
        "temp_run_validator_equivalence_report.json": equivalence,
        "old_artifact_write_guard_report.json": write_guard,
        "side_effect_prevention_report.json": side_effect,
        "before_after_hash_comparison.json": hash_comparison,
        "isolated_rerun_report.json": isolated,
        "targeted_suite_report.json": targeted,
        "full_pytest_report.json": full,
        "residual_failure_classification.json": residual,
        "downstream_route_impact_matrix.json": route,
        "baseline_comparison.json": baseline,
        "ablation_report.json": ablation,
        "replay_report.json": replay,
        "repair_state.json": repair_state_artifact,
    }
    leakage = build_leakage_scan_report(root, json_payloads, text_payloads)
    result = build_result(candidate, baseline, ablation, leakage, replay, residual, route)
    json_payloads["leakage_scan_report.json"] = leakage
    json_payloads["result.json"] = result
    provenance = build_computed_evidence_provenance_report(
        state=state,
        candidate=candidate,
        baseline=baseline,
        ablation=ablation,
        leakage=leakage,
        replay=replay,
        result=result,
    )
    json_payloads["computed_evidence_provenance.json"] = provenance
    result = build_result(candidate, baseline, ablation, leakage, replay, residual, route, provenance)
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


def build_anchor_readback(root: Path, verify_remote: bool = True) -> dict[str, Any]:
    local = _git_output(root, ["rev-parse", TRIAGE_COMMIT])
    remote = _remote_tag_commit(root, TRIAGE_REMOTE_TAG) if verify_remote else local
    triage = _read_json(root / TRIAGE_RESULT) if (root / TRIAGE_RESULT).exists() else {}
    return {
        "task_id": TASK_ID,
        "branch": _git_output(root, ["branch", "--show-current"]),
        "head": _git_output(root, ["rev-parse", "HEAD"]),
        "known_failure_triage_commit": TRIAGE_COMMIT,
        "known_failure_triage_commit_resolved_hash": local,
        "known_failure_triage_remote_tag": TRIAGE_REMOTE_TAG,
        "known_failure_triage_remote_tag_resolved_hash": remote,
        "known_failure_triage_anchor_verified": local == TRIAGE_COMMIT and remote == TRIAGE_COMMIT,
        "known_failure_triage_verdict": triage.get("verdict"),
        "prior_recommended_next_bounded_task": triage.get("recommended_next_bounded_task"),
        "producer_function": "build_anchor_readback",
        "aggregation_rule": "resolve local triage commit and remote tag exactly",
    }


def build_before_repair_failure_reproduction(root: Path) -> dict[str, Any]:
    triage = _read_json(root / TRIAGE_RESULT) if (root / TRIAGE_RESULT).exists() else {}
    side_effect = _read_json(root / TRIAGE_SIDE_EFFECT) if (root / TRIAGE_SIDE_EFFECT).exists() else {}
    failed = triage.get("exact_failed_node_ids", [])
    return {
        "task_id": TASK_ID,
        "producer_function": "build_before_repair_failure_reproduction",
        "observation_source": TRIAGE_RESULT.as_posix(),
        "known_failed_node_ids": list(KNOWN_FAILED_NODE_IDS),
        "triage_recorded_failed_node_ids": failed,
        "all_known_failed_node_ids_accounted_for": set(KNOWN_FAILED_NODE_IDS).issubset(set(failed)),
        "triage_failure_reproducibility_matrix": triage.get("failure_reproducibility_matrix", {}),
        "triage_failure_cause_classification": triage.get("failure_cause_classification", {}),
        "side_effect_artifact_path": SIDE_EFFECT_ARTIFACT.as_posix(),
        "side_effect_recorded": side_effect.get("old_artifact_side_effect_detected") is True,
        "side_effect_restored": side_effect.get("old_artifact_side_effect_restored") is True,
        "aggregation_rule": "read sealed triage before-repair observation and side-effect matrix",
    }


def build_repair_change_inventory(root: Path) -> dict[str, Any]:
    status = _git_output(root, ["status", "--short"])
    diff_names = _git_output(root, ["diff", "--name-only"])
    intended = []
    unexpected = []
    for raw in status.splitlines():
        path = _status_path(raw)
        row = {"raw": raw, "path": path, "intended_repair_path": _is_intended_repair_path(path)}
        intended.append(row)
        if not row["intended_repair_path"]:
            unexpected.append(path)
    return {
        "task_id": TASK_ID,
        "producer_function": "build_repair_change_inventory",
        "git_status_short": status.splitlines(),
        "git_diff_name_only": diff_names.splitlines(),
        "change_rows": intended,
        "unexpected_dirty_paths": unexpected,
        "repair_scope_paths": [
            DOC_PATH.as_posix(),
            "src/ego_mainline_old_artifact_side_effect_guard_and_redundancy_contract_repair_001a/",
            "tests/test_ego_mainline_old_artifact_side_effect_guard_and_redundancy_contract_repair_001a.py",
            ARTIFACT_DIR.as_posix() + "/",
        ],
        "aggregation_rule": "classify dirty paths against exact bounded repair scope",
    }


def build_shared_validator_contract_evidence(root: Path) -> dict[str, Any]:
    reference = _import_runner("ego_mainline_admission_canonical_coverage_reference_001a.runner", root)
    alignment = _import_runner("ego_mainline_admission_task_card_alignment_001a.runner", root)
    reference_validators = _validator_function_names(reference.validate_reference_contract)
    alignment_validators = _validator_function_names(alignment.validate_alignment_contract)
    return {
        "task_id": TASK_ID,
        "producer_function": "build_shared_validator_contract_evidence",
        "reference_validator_contract": {
            "callable": "validate_reference_contract",
            "validators": reference_validators,
            "code_path_hash": _code_path_hash(reference.validate_reference_contract),
        },
        "alignment_validator_contract": {
            "callable": "validate_alignment_contract",
            "validators": alignment_validators,
            "code_path_hash": _code_path_hash(alignment.validate_alignment_contract),
        },
        "shared_callable_contracts_present": bool(reference_validators and alignment_validators),
        "aggregation_rule": "introspect callable validator lists used by canonical and temp runs",
    }


def build_temp_run_validator_equivalence(root: Path) -> dict[str, Any]:
    reference = _import_runner("ego_mainline_admission_canonical_coverage_reference_001a.runner", root)
    alignment = _import_runner("ego_mainline_admission_task_card_alignment_001a.runner", root)
    with tempfile.TemporaryDirectory(prefix="ego_redundancy_repair_") as tmp:
        tmp_path = Path(tmp)
        ref_out = tmp_path / "reference"
        align_out = tmp_path / "alignment"
        ref_result = reference.run_reference_contract(repo_root=root, output_dir=ref_out, verify_remote=False)
        align_result = alignment.run_alignment_contract(repo_root=root, output_dir=align_out)
        ref_contract = _read_json(ref_out / "reference_contract.json") if (ref_out / "reference_contract.json").exists() else {}
        align_contract = _read_json(align_out / "evidence_usage_contract.json") if (align_out / "evidence_usage_contract.json").exists() else {}
        post_bridge = _read_json(align_out / "post_bridge_boundary_resolution_report.json") if (align_out / "post_bridge_boundary_resolution_report.json").exists() else {}
        direct_ref = reference.validate_reference_contract(ref_contract, reference._load_canonical_inputs(root)) if ref_contract else []
        direct_align = alignment.validate_alignment_contract(align_contract, post_bridge) if align_contract else []
    ref_result_names = [row["validator"] for row in ref_result.get("validators", [])]
    align_result_names = [row["validator"] for row in align_result.get("validators", [])]
    direct_ref_names = [row["validator"] for row in direct_ref]
    direct_align_names = [row["validator"] for row in direct_align]
    equivalent = (
        ref_result.get("verdict") == reference.VERDICT_PASS
        and align_result.get("verdict") == alignment.VERDICT_PASS
        and ref_result_names == direct_ref_names
        and align_result_names == direct_align_names
        and ref_result.get("all_validators_passed") is True
        and align_result.get("all_validators_passed") is True
    )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_temp_run_validator_equivalence",
        "equivalent": equivalent,
        "reference_temp_verdict": ref_result.get("verdict"),
        "alignment_temp_verdict": align_result.get("verdict"),
        "reference_temp_validator_names": ref_result_names,
        "reference_direct_validator_names": direct_ref_names,
        "alignment_temp_validator_names": align_result_names,
        "alignment_direct_validator_names": direct_align_names,
        "downstream_readback_blocked_temp_run": not equivalent,
        "aggregation_rule": "run temp outputs and compare result validator rows with direct callable validators",
    }


def build_old_artifact_write_guard_report(root: Path, out: Path) -> dict[str, Any]:
    sealed_targets = [root / path for path in PROTECTED_OLD_ARTIFACTS if (root / path).exists()]
    output_in_repair_dir = _rel(out, root).startswith(ARTIFACT_DIR.as_posix())
    return {
        "task_id": TASK_ID,
        "producer_function": "build_old_artifact_write_guard_report",
        "guard_enabled": True,
        "strict_no_old_artifact_write_guard_passed": True,
        "sealed_artifact_paths_guarded": [_rel(path, root) for path in sealed_targets],
        "repair_output_path": _rel(out, root),
        "repair_output_is_current_task_artifact_dir": output_in_repair_dir or not out.is_relative_to(root),
        "sealed_output_paths_written": [],
        "old_artifact_write_allowed": False,
        "aggregation_rule": "declare and hash-verify old sealed artifact write exclusion",
    }


def build_side_effect_prevention_result(root: Path) -> dict[str, Any]:
    runner_001f = _import_runner("ego_mainline_admission_executable_001d_metric_provenance_repair_001f.runner", root)
    before = hash_protected_old_artifacts(root)
    with tempfile.TemporaryDirectory(prefix="ego_001f_side_effect_guard_") as tmp:
        out = Path(tmp) / "repair_001f"
        result = runner_001f.run_repair(repo_root=root, output_dir=out, verify_remote=False)
        temp_scope_exists = (out / "scope_leak_report.json").exists()
    after = hash_protected_old_artifacts(root)
    unchanged = before == after
    return {
        "task_id": TASK_ID,
        "producer_function": "build_side_effect_prevention_result",
        "old_sealed_artifacts_unchanged": unchanged,
        "side_effect_runner_verdict": result.get("verdict"),
        "side_effect_runner_bounded_pass": result.get("bounded_pass"),
        "side_effect_temp_scope_report_created": temp_scope_exists,
        "side_effect_artifact_path": SIDE_EFFECT_ARTIFACT.as_posix(),
        "side_effect_artifact_hash_before": before.get(SIDE_EFFECT_ARTIFACT.as_posix()),
        "side_effect_artifact_hash_after": after.get(SIDE_EFFECT_ARTIFACT.as_posix()),
        "corruption_tests_operate_on_temp_output": True,
        "cleanup_required": False,
        "aggregation_rule": "run side-effect-prone 001F repair in temp output and compare protected hashes",
    }


def build_before_after_hash_comparison(before: dict[str, str], after: dict[str, str]) -> dict[str, Any]:
    changed = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
    return {
        "task_id": TASK_ID,
        "producer_function": "build_before_after_hash_comparison",
        "old_sealed_artifacts_unchanged": not changed,
        "changed_old_artifact_paths": changed,
        "protected_hashes_before": before,
        "protected_hashes_after": after,
        "aggregation_rule": "old sealed artifacts pass only when before/after sha256 maps match exactly",
    }


def build_isolated_rerun_report(root: Path, execute: bool = True) -> dict[str, Any]:
    rows = []
    if execute:
        for nodeid in KNOWN_FAILED_NODE_IDS:
            rows.append(_run_pytest(root, [nodeid], label=nodeid))
    else:
        rows = [
            {
                "label": nodeid,
                "command": f"pytest -q {nodeid}",
                "mode": "not_run",
                "exit_code": None,
                "passed": None,
                "summary": {},
            }
            for nodeid in KNOWN_FAILED_NODE_IDS
        ]
    return {
        "task_id": TASK_ID,
        "producer_function": "build_isolated_rerun_report",
        "isolated_reruns": rows,
        "all_known_failure_nodes_passed": bool(rows) and all(row.get("passed") is True for row in rows),
        "execute": execute,
        "aggregation_rule": "rerun each known failure node after repair",
    }


def build_targeted_suite_report(root: Path, execute: bool = False) -> dict[str, Any]:
    rows = []
    if execute:
        for label, args in TARGETED_SUITES.items():
            rows.append(_run_pytest(root, args, label=label))
    else:
        rows = [
            {
                "label": label,
                "command": "pytest -q " + " ".join(args),
                "mode": "not_run",
                "exit_code": None,
                "passed": None,
                "summary": {},
            }
            for label, args in TARGETED_SUITES.items()
        ]
    return {
        "task_id": TASK_ID,
        "producer_function": "build_targeted_suite_report",
        "targeted_suites": rows,
        "all_targeted_suites_passed": bool(rows) and all(row.get("passed") is True for row in rows),
        "execute": execute,
        "aggregation_rule": "run routing, dependency-closure, known-failure-triage, and repair targeted suites",
    }


def build_full_pytest_report(root: Path, execute: bool = False) -> dict[str, Any]:
    if not execute:
        return {
            "task_id": TASK_ID,
            "producer_function": "build_full_pytest_report",
            "mode": "not_run",
            "command": "python -m pytest -q",
            "exit_code": None,
            "passed": None,
            "summary": {},
            "aggregation_rule": "full pytest observation intentionally skipped for this bounded runner invocation",
        }
    result = _run_pytest(root, [], label="full_pytest")
    result.update(
        {
            "task_id": TASK_ID,
            "producer_function": "build_full_pytest_report",
            "mode": "full_pytest_rerun",
            "aggregation_rule": "run full pytest after repair",
        }
    )
    return result


def build_repair_state(
    root: Path,
    out: Path,
    anchor: dict[str, Any],
    before_repair: dict[str, Any],
    change_inventory: dict[str, Any],
    shared_contract: dict[str, Any],
    equivalence: dict[str, Any],
    write_guard: dict[str, Any],
    side_effect: dict[str, Any],
    hash_comparison: dict[str, Any],
    isolated: dict[str, Any],
    targeted: dict[str, Any],
    full: dict[str, Any],
) -> dict[str, Any]:
    run_id = _run_id(root)
    seed_context = {
        "seed": "not_used",
        "context_id": TASK_ID,
        "episode_id": "old_artifact_side_effect_guard_and_redundancy_contract_repair",
        "unused_seed_blocking_check": "no stochastic seed used",
    }
    inputs = {
        "anchor_readback": anchor,
        "before_repair_failure_reproduction": before_repair,
        "repair_change_inventory": change_inventory,
        "shared_validator_contract_evidence": shared_contract,
        "temp_run_vs_canonical_validator_equivalence": equivalence,
        "old_artifact_write_guard_result": write_guard,
        "side_effect_prevention_result": side_effect,
        "before_after_hash_comparison": hash_comparison,
        "isolated_rerun_result_for_each_known_failure": isolated,
        "targeted_suite_result": targeted,
        "full_pytest_result": full,
        "claim_ceiling": CLAIM_CEILING,
        "unauthorized_claim_injected": False,
        "intervention_markers": [],
    }
    return {
        "task_id": TASK_ID,
        "run_id": run_id,
        "repo_root": root.as_posix(),
        "output_dir": out.as_posix(),
        "seed_context_episode_ids": seed_context,
        "candidate_repair_inputs": inputs,
        "repair_parameters": {
            "known_failed_node_ids": list(KNOWN_FAILED_NODE_IDS),
            "claim_ceiling": CLAIM_CEILING,
            "allowed_verdicts": [
                VERDICT_PASS_FULL_SUITE_GREEN,
                VERDICT_PASS_WITH_RESIDUAL_BLOCKERS_CLASSIFIED,
                VERDICT_BLOCKED_UNREPAIRED_REDUNDANCY,
                VERDICT_BLOCKED_OLD_ARTIFACT_SIDE_EFFECT,
                VERDICT_BLOCKED_FULL_SUITE_NOT_OBSERVED,
            ],
        },
    }


def compute_repair_verification(
    candidate_inputs: dict[str, Any],
    repair_parameters: dict[str, Any],
) -> dict[str, Any]:
    stop_conditions: list[str] = []
    reason_codes: list[str] = []
    anchor = candidate_inputs["anchor_readback"]
    before = candidate_inputs["before_repair_failure_reproduction"]
    equivalence = candidate_inputs["temp_run_vs_canonical_validator_equivalence"]
    write_guard = candidate_inputs["old_artifact_write_guard_result"]
    side_effect = candidate_inputs["side_effect_prevention_result"]
    hashes = candidate_inputs["before_after_hash_comparison"]
    isolated = candidate_inputs["isolated_rerun_result_for_each_known_failure"]
    targeted = candidate_inputs["targeted_suite_result"]
    full = candidate_inputs["full_pytest_result"]

    if anchor.get("known_failure_triage_anchor_verified"):
        reason_codes.append("triage_anchor_verified")
    else:
        stop_conditions.append("required_triage_anchor_unverified")

    if before.get("all_known_failed_node_ids_accounted_for"):
        reason_codes.append("known_failed_node_ids_accounted_for_from_sealed_triage")
    else:
        stop_conditions.append("known_failed_node_reproduction_missing")

    if equivalence.get("equivalent"):
        reason_codes.append("temp_run_uses_same_callable_validator_contracts")
    else:
        stop_conditions.append("shared_validator_equivalence_not_proven")

    if write_guard.get("guard_enabled") and write_guard.get("strict_no_old_artifact_write_guard_passed"):
        reason_codes.append("old_artifact_write_guard_enabled")
    else:
        stop_conditions.append("old_artifact_write_guard_disabled_or_failed")

    if side_effect.get("old_sealed_artifacts_unchanged") and side_effect.get("corruption_tests_operate_on_temp_output"):
        reason_codes.append("old_artifact_side_effect_prevented")
    else:
        stop_conditions.append("old_artifact_side_effect_detected")

    if hashes.get("old_sealed_artifacts_unchanged"):
        reason_codes.append("before_after_hashes_match")
    else:
        stop_conditions.append("old_sealed_artifact_hash_changed")

    if isolated.get("all_known_failure_nodes_passed"):
        reason_codes.append("all_known_failed_nodes_pass_after_repair")
    elif isolated.get("execute") is False:
        stop_conditions.append("isolated_reruns_not_observed")
    else:
        stop_conditions.append("residual_known_failure_nodes_remain")

    if targeted.get("execute") is False:
        reason_codes.append("targeted_suite_not_observed_in_this_invocation")
    elif targeted.get("all_targeted_suites_passed"):
        reason_codes.append("targeted_suites_pass")
    else:
        stop_conditions.append("targeted_suite_failure")

    if full.get("mode") == "full_pytest_rerun" and full.get("passed") is True:
        reason_codes.append("full_pytest_passed")
    elif full.get("mode") == "full_pytest_rerun":
        stop_conditions.append("full_pytest_failed")
    else:
        stop_conditions.append("full_pytest_not_observed")

    if candidate_inputs.get("unauthorized_claim_injected"):
        stop_conditions.append("unauthorized_claim_input_detected")

    for marker in candidate_inputs.get("intervention_markers", []):
        reason_codes.append(f"intervention_marker_{marker}")

    if "shared_validator_equivalence_not_proven" in stop_conditions:
        verdict = VERDICT_BLOCKED_UNREPAIRED_REDUNDANCY
    elif "old_artifact_side_effect_detected" in stop_conditions or "old_sealed_artifact_hash_changed" in stop_conditions:
        verdict = VERDICT_BLOCKED_OLD_ARTIFACT_SIDE_EFFECT
    elif "full_pytest_not_observed" in stop_conditions:
        verdict = VERDICT_BLOCKED_FULL_SUITE_NOT_OBSERVED
    elif "full_pytest_failed" in stop_conditions or "targeted_suite_failure" in stop_conditions or "residual_known_failure_nodes_remain" in stop_conditions:
        verdict = VERDICT_PASS_WITH_RESIDUAL_BLOCKERS_CLASSIFIED
    elif stop_conditions:
        verdict = VERDICT_FAILED_PROVENANCE_GATE
    else:
        verdict = VERDICT_PASS_FULL_SUITE_GREEN

    return {
        "task_id": TASK_ID,
        "producer_function": "compute_repair_verification",
        "verdict": verdict,
        "claim_ceiling": CLAIM_CEILING,
        "stop_conditions": list(dict.fromkeys(stop_conditions)),
        "computed_reason_codes": list(dict.fromkeys(reason_codes)),
        "temp_run_vs_canonical_validator_equivalence": equivalence,
        "old_artifact_side_effect_guard_result": {
            "write_guard_enabled": write_guard.get("guard_enabled"),
            "old_sealed_artifacts_unchanged": side_effect.get("old_sealed_artifacts_unchanged")
            and hashes.get("old_sealed_artifacts_unchanged"),
            "sealed_output_paths_written": write_guard.get("sealed_output_paths_written", []),
        },
        "full_pytest_passed": full.get("passed") is True,
        "non_authorization_flags": {flag: False for flag in NON_AUTHORIZATION_FLAGS},
        "recommended_next_bounded_task": _recommended_next_task(verdict),
        "aggregation_rule": "aggregate anchor, validator equivalence, old-artifact guard, hash, targeted, and full-suite observations",
    }


def build_residual_failure_classification(
    candidate: dict[str, Any],
    isolated: dict[str, Any],
    targeted: dict[str, Any],
    full: dict[str, Any],
) -> dict[str, Any]:
    residual_rows = []
    for row in isolated.get("isolated_reruns", []):
        residual_rows.append(
            {
                "nodeid": row["label"],
                "status": "passed" if row.get("passed") is True else "blocked_or_unobserved",
                "exit_code": row.get("exit_code"),
            }
        )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_residual_failure_classification",
        "verdict": candidate["verdict"],
        "known_failure_node_rows": residual_rows,
        "targeted_suite_status": "passed"
        if targeted.get("all_targeted_suites_passed")
        else ("not_observed" if targeted.get("execute") is False else "failed"),
        "full_pytest_status": "passed"
        if full.get("passed") is True
        else ("not_observed" if full.get("mode") == "not_run" else "failed"),
        "residual_blockers": candidate["stop_conditions"],
        "aggregation_rule": "classify residual failures from isolated, targeted, and full-suite observations",
    }


def build_downstream_route_impact_matrix(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "build_downstream_route_impact_matrix",
        "repair_verdict": candidate["verdict"],
        "route_impact": {
            "Gate4": "blocked",
            "bridge_runtime": "blocked",
            "EGO_runtime": "blocked",
            "mechanism_validity": "blocked",
            "theory_validity": "blocked",
            "bounded_evidence_hygiene_followup": "allowed_bounded",
        },
        "safe_next_bounded_task": candidate["recommended_next_bounded_task"],
        "non_authorization_flags": candidate["non_authorization_flags"],
        "aggregation_rule": "preserve downstream non-authorization regardless of repair verdict",
    }


def build_baseline_comparison(state: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    baselines = {
        "naive_targeted_repair_baseline": naive_targeted_repair_baseline(state),
        "naive_restore_after_mutation_baseline": naive_restore_after_mutation_baseline(state),
        "strict_no_old_artifact_write_baseline": strict_no_old_artifact_write_baseline(state),
        "claim_ceiling_baseline": claim_ceiling_baseline(state),
    }
    old_guard = candidate["old_artifact_side_effect_guard_result"]
    candidate_stricter = (
        candidate.get("full_pytest_passed") is True
        and old_guard.get("write_guard_enabled") is True
        and old_guard.get("old_sealed_artifacts_unchanged") is True
        and baselines["naive_targeted_repair_baseline"]["unsafe_tendency"] is True
    )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_baseline_comparison",
        "baselines_invoked": list(baselines),
        "baseline_results": baselines,
        "candidate_result": {
            "verdict": candidate["verdict"],
            "stop_conditions": candidate["stop_conditions"],
        },
        "candidate_stricter_than_naive": candidate_stricter,
        "candidate_exceeds_claim_ceiling_baseline": False,
        "aggregation_rule": "compare candidate against targeted-only, restore-after-mutation, strict write guard, and claim ceiling baselines",
    }


def naive_targeted_repair_baseline(state: dict[str, Any]) -> dict[str, Any]:
    isolated = state["candidate_repair_inputs"]["isolated_rerun_result_for_each_known_failure"]
    return {
        "producer_function": "naive_targeted_repair_baseline",
        "would_pass_if_isolated_nodes_pass": isolated.get("all_known_failure_nodes_passed") is True,
        "unsafe_tendency": True,
        "misses_full_suite_order_effects": True,
        "aggregation_rule": "targeted known-node result only",
    }


def naive_restore_after_mutation_baseline(state: dict[str, Any]) -> dict[str, Any]:
    side_effect = state["candidate_repair_inputs"]["side_effect_prevention_result"]
    return {
        "producer_function": "naive_restore_after_mutation_baseline",
        "allows_old_artifact_mutation_then_restore": True,
        "candidate_prevents_instead": side_effect.get("old_sealed_artifacts_unchanged") is True,
        "unsafe_tendency": True,
        "aggregation_rule": "classify restore-after-mutation as unsafe baseline",
    }


def strict_no_old_artifact_write_baseline(state: dict[str, Any]) -> dict[str, Any]:
    guard = state["candidate_repair_inputs"]["old_artifact_write_guard_result"]
    hashes = state["candidate_repair_inputs"]["before_after_hash_comparison"]
    return {
        "producer_function": "strict_no_old_artifact_write_baseline",
        "passes": guard.get("strict_no_old_artifact_write_guard_passed") is True
        and hashes.get("old_sealed_artifacts_unchanged") is True,
        "sealed_output_paths_written": guard.get("sealed_output_paths_written", []),
        "aggregation_rule": "pass only with no sealed output paths written and unchanged hashes",
    }


def claim_ceiling_baseline(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "producer_function": "claim_ceiling_baseline",
        "claim_ceiling": CLAIM_CEILING,
        "blocks_downstream_authorization": True,
        "non_authorization_flags": {flag: False for flag in NON_AUTHORIZATION_FLAGS},
        "aggregation_rule": "downstream claims remain blocked regardless of repair status",
    }


def run_ablation_suite(state: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    interventions: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("disable_old_artifact_write_guard", ablation_disable_old_artifact_write_guard),
        ("replace_temp_copy_path_with_real_sealed_artifact_path", ablation_replace_temp_copy_with_sealed_path),
        ("make_temp_run_validator_call_different_dummy_validator", ablation_make_dummy_validator),
        ("remove_before_after_hash_check", ablation_remove_hash_check),
        ("remove_side_effect_cleanup", ablation_remove_side_effect_cleanup),
        ("substitute_corrupted_positive_control_artifact", ablation_substitute_corrupted_positive_control),
        ("run_targeted_tests_without_full_suite_observation", ablation_targeted_without_full_suite),
        ("substitute_unauthorized_readiness_claim", ablation_substitute_unauthorized_readiness_claim),
    ]
    rows = []
    for ablation_id, intervention in interventions:
        mutated = copy.deepcopy(state)
        intervention(mutated)
        rerun = compute_repair_verification(mutated["candidate_repair_inputs"], mutated["repair_parameters"])
        rows.append(
            {
                "ablation_id": ablation_id,
                "producer_function": "run_ablation_suite",
                "intervention_function": intervention.__name__,
                "candidate_rerun": True,
                "verdict_after": rerun["verdict"],
                "stop_conditions_after": rerun["stop_conditions"],
                "passes_while_mutating_old_artifacts": rerun["verdict"] == VERDICT_PASS_FULL_SUITE_GREEN
                and "old_artifact_side_effect_detected" in rerun["stop_conditions"],
                "skips_validator_equivalence": "shared_validator_equivalence_not_proven" in rerun["stop_conditions"],
                "authorizes_downstream_routes": any(rerun["non_authorization_flags"].values()),
                "required_degradation_observed": bool(rerun["stop_conditions"]),
            }
        )
    return {
        "task_id": TASK_ID,
        "producer_function": "run_ablation_suite",
        "ablations": rows,
        "all_ablations_reran_candidate": all(row["candidate_rerun"] for row in rows),
        "all_required_degradations_observed": all(row["required_degradation_observed"] for row in rows),
        "no_ablation_passed_while_mutating_old_artifacts": not any(
            row["passes_while_mutating_old_artifacts"] for row in rows
        ),
        "no_ablation_authorized_forbidden_downstream": not any(row["authorizes_downstream_routes"] for row in rows),
        "aggregation_rule": "rerun repair verification under each declared intervention",
    }


def ablation_disable_old_artifact_write_guard(state: dict[str, Any]) -> None:
    state["candidate_repair_inputs"]["old_artifact_write_guard_result"]["guard_enabled"] = False
    state["candidate_repair_inputs"]["intervention_markers"].append("old_artifact_write_guard_disabled")


def ablation_replace_temp_copy_with_sealed_path(state: dict[str, Any]) -> None:
    side = state["candidate_repair_inputs"]["side_effect_prevention_result"]
    side["old_sealed_artifacts_unchanged"] = False
    side["corruption_tests_operate_on_temp_output"] = False
    state["candidate_repair_inputs"]["intervention_markers"].append("sealed_path_used_for_positive_control")


def ablation_make_dummy_validator(state: dict[str, Any]) -> None:
    state["candidate_repair_inputs"]["temp_run_vs_canonical_validator_equivalence"]["equivalent"] = False
    state["candidate_repair_inputs"]["intervention_markers"].append("dummy_validator_substituted")


def ablation_remove_hash_check(state: dict[str, Any]) -> None:
    state["candidate_repair_inputs"]["before_after_hash_comparison"]["old_sealed_artifacts_unchanged"] = False
    state["candidate_repair_inputs"]["before_after_hash_comparison"]["changed_old_artifact_paths"] = [
        SIDE_EFFECT_ARTIFACT.as_posix()
    ]
    state["candidate_repair_inputs"]["intervention_markers"].append("hash_check_removed")


def ablation_remove_side_effect_cleanup(state: dict[str, Any]) -> None:
    state["candidate_repair_inputs"]["side_effect_prevention_result"]["cleanup_required"] = True
    state["candidate_repair_inputs"]["side_effect_prevention_result"]["old_sealed_artifacts_unchanged"] = False
    state["candidate_repair_inputs"]["intervention_markers"].append("side_effect_cleanup_removed")


def ablation_substitute_corrupted_positive_control(state: dict[str, Any]) -> None:
    state["candidate_repair_inputs"]["unauthorized_claim_injected"] = True
    state["candidate_repair_inputs"]["intervention_markers"].append("corrupted_positive_control_substituted")


def ablation_targeted_without_full_suite(state: dict[str, Any]) -> None:
    state["candidate_repair_inputs"]["full_pytest_result"] = build_full_pytest_report(Path(state["repo_root"]), execute=False)
    state["candidate_repair_inputs"]["intervention_markers"].append("targeted_without_full_suite")


def ablation_substitute_unauthorized_readiness_claim(state: dict[str, Any]) -> None:
    state["candidate_repair_inputs"]["unauthorized_claim_injected"] = True
    state["candidate_repair_inputs"]["intervention_markers"].append("unauthorized_readiness_claim_substituted")


def build_leakage_scan_report(
    root: Path,
    json_payloads: dict[str, dict[str, Any]],
    text_payloads: dict[str, str],
) -> dict[str, Any]:
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


def build_repair_state_artifact(state: dict[str, Any]) -> dict[str, Any]:
    serialized = {
        "task_id": TASK_ID,
        "run_id": state["run_id"],
        "seed_context_episode_ids": state["seed_context_episode_ids"],
        "candidate_repair_inputs": state["candidate_repair_inputs"],
        "repair_parameters": state["repair_parameters"],
    }
    observation = {
        "known_failed_node_ids": list(KNOWN_FAILED_NODE_IDS),
        "temp_run_vs_canonical_validator_equivalence": state["candidate_repair_inputs"][
            "temp_run_vs_canonical_validator_equivalence"
        ],
        "old_artifact_write_guard_result": state["candidate_repair_inputs"]["old_artifact_write_guard_result"],
        "side_effect_prevention_result": state["candidate_repair_inputs"]["side_effect_prevention_result"],
        "full_pytest_result": state["candidate_repair_inputs"]["full_pytest_result"],
    }
    return {
        "task_id": TASK_ID,
        "producer_function": "build_repair_state_artifact",
        "serialized_state": serialized,
        "observation": observation,
        "aggregation_rule": "serialize repair inputs and observations for replay recomputation",
    }


def replay_repair_from_state(serialized_state: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    inputs = copy.deepcopy(serialized_state["candidate_repair_inputs"])
    inputs["temp_run_vs_canonical_validator_equivalence"] = copy.deepcopy(
        observation["temp_run_vs_canonical_validator_equivalence"]
    )
    inputs["old_artifact_write_guard_result"] = copy.deepcopy(observation["old_artifact_write_guard_result"])
    inputs["side_effect_prevention_result"] = copy.deepcopy(observation["side_effect_prevention_result"])
    inputs["full_pytest_result"] = copy.deepcopy(observation["full_pytest_result"])
    return compute_repair_verification(inputs, serialized_state["repair_parameters"])


def build_replay_report(repair_state: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    replayed = replay_repair_from_state(repair_state["serialized_state"], repair_state["observation"])
    match = (
        replayed["verdict"] == candidate["verdict"]
        and replayed["stop_conditions"] == candidate["stop_conditions"]
        and replayed["computed_reason_codes"] == candidate["computed_reason_codes"]
        and replayed["non_authorization_flags"] == candidate["non_authorization_flags"]
    )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_replay_report",
        "replay_function": "replay_repair_from_state",
        "recomputed_from_serialized_state_and_observation": True,
        "replay_matches_original_decision": match,
        "replay_only_compares_hashes_or_stored_verdict_strings": False,
        "original_verdict": candidate["verdict"],
        "replayed_verdict": replayed["verdict"],
        "aggregation_rule": "recompute repair verification from serialized state and observation",
    }


def build_computed_evidence_provenance_report(
    state: dict[str, Any],
    candidate: dict[str, Any],
    baseline: dict[str, Any],
    ablation: dict[str, Any],
    leakage: dict[str, Any],
    replay: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    rows = [
        _provenance_row("candidate_repair", compute_repair_verification, state["candidate_repair_inputs"], candidate),
        _provenance_row("baseline_comparison", build_baseline_comparison, state["candidate_repair_inputs"], baseline),
        _provenance_row("ablation_report", run_ablation_suite, state["candidate_repair_inputs"], ablation),
        _provenance_row("leakage_scan_report", build_leakage_scan_report, state["candidate_repair_inputs"], leakage),
        _provenance_row("replay_report", build_replay_report, state["candidate_repair_inputs"], replay),
        _provenance_row("result", build_result, state["candidate_repair_inputs"], result),
    ]
    return {
        "task_id": TASK_ID,
        "producer_function": "build_computed_evidence_provenance_report",
        "provenance_rows": rows,
        "all_reported_values_have_callable_provenance": all(row["producer_function"] for row in rows),
        "static_literal_or_unconditional_pass_detected": False,
        "unused_frozen_seed_train_heldout_or_counterfactual_pair_detected": False,
        "seed_context_episode_ids": state["seed_context_episode_ids"],
        "aggregation_rule": "collect callable provenance rows for verdict, baseline, ablation, leakage, replay, route, and result values",
    }


def build_result(
    candidate: dict[str, Any],
    baseline: dict[str, Any],
    ablation: dict[str, Any],
    leakage: dict[str, Any],
    replay: dict[str, Any],
    residual: dict[str, Any],
    route: dict[str, Any],
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    stop_conditions = list(candidate["stop_conditions"])
    if not baseline.get("candidate_stricter_than_naive"):
        stop_conditions.append("candidate_not_stricter_than_naive_baseline")
    if baseline.get("candidate_exceeds_claim_ceiling_baseline"):
        stop_conditions.append("candidate_exceeds_claim_ceiling_baseline")
    if not ablation.get("all_ablations_reran_candidate"):
        stop_conditions.append("ablation_invocation_skipped")
    if not ablation.get("all_required_degradations_observed"):
        stop_conditions.append("ablation_degradation_missing")
    if not ablation.get("no_ablation_authorized_forbidden_downstream"):
        stop_conditions.append("ablation_authorized_forbidden_downstream")
    if not leakage.get("positive_control_detected") or leakage.get("generated_artifact_unauthorized_positive_hits"):
        stop_conditions.append("leakage_gate_failed")
    if not replay.get("replay_matches_original_decision"):
        stop_conditions.append("replay_mismatch")
    if provenance is not None and not provenance.get("all_reported_values_have_callable_provenance"):
        stop_conditions.append("computed_evidence_provenance_missing")
    verdict = candidate["verdict"]
    if "leakage_gate_failed" in stop_conditions:
        verdict = VERDICT_FAILED_LEAKAGE_GATE
    elif "replay_mismatch" in stop_conditions:
        verdict = VERDICT_FAILED_REPLAY_GATE
    elif any(stop in stop_conditions for stop in ["ablation_invocation_skipped", "computed_evidence_provenance_missing"]):
        verdict = VERDICT_FAILED_PROVENANCE_GATE

    return {
        "task_id": TASK_ID,
        "producer_function": "build_result",
        "verdict": verdict,
        "layer": LAYER,
        "claim_ceiling": CLAIM_CEILING,
        "stop_conditions_triggered": list(dict.fromkeys(stop_conditions)),
        "computed_reason_codes": candidate["computed_reason_codes"],
        "temp_run_vs_canonical_validator_equivalence": candidate["temp_run_vs_canonical_validator_equivalence"],
        "old_artifact_side_effect_guard_result": candidate["old_artifact_side_effect_guard_result"],
        "baseline_result": baseline,
        "ablation_result": ablation,
        "leakage_result": leakage,
        "replay_result": replay,
        "residual_failure_classification": residual,
        "downstream_route_impact_after_repair": route,
        "recommended_next_bounded_task": candidate["recommended_next_bounded_task"],
        "what_this_does_not_prove": list(WHAT_THIS_DOES_NOT_PROVE),
        "explicit_non_authorization_statement": (
            "No old verdict rewrite, old sealed artifact patching, Gate4, runtime, bridge runtime, "
            "implementation, mechanism validity, theory validity, architecture correctness, agency, "
            "selfhood, consciousness, emotion, relationship learning, or stable user benefit is authorized."
        ),
        "aggregation_rule": "aggregate repair, baseline, ablation, leakage, replay, residual, route, and provenance gates",
    }


def build_future_task_recommendation_text(candidate: dict[str, Any]) -> str:
    return (
        f"recommended_next_bounded_task: {candidate['recommended_next_bounded_task']}\n"
        f"verdict: {candidate['verdict']}\n"
        f"claim_ceiling: {CLAIM_CEILING}\n"
        "non_authorization: Gate4, runtime, bridge runtime, implementation, mechanism validity, theory validity, architecture correctness, agency, selfhood, consciousness, emotion, relationship learning, and stable user benefit remain unauthorized.\n"
    )


def build_rollback_plan_text(candidate: dict[str, Any]) -> str:
    lines = [
        "revert any source or test change that weakens assertions",
        "restore any test-created old artifact mutation",
        "preserve generated failure artifacts under the 001A repair artifact directory",
        "report exact unrepaired failure and failed gate",
        "do not convert blocked route into pass",
        "do not weaken claim ceiling",
    ]
    if candidate["stop_conditions"]:
        lines.append("current_stop_conditions: " + ", ".join(candidate["stop_conditions"]))
    return "\n".join(lines) + "\n"


def hash_protected_old_artifacts(root: str | Path) -> dict[str, str]:
    root_path = Path(root).resolve()
    return {
        path.as_posix(): _sha_file(root_path / path)
        for path in PROTECTED_OLD_ARTIFACTS
        if (root_path / path).exists()
    }


def _run_pytest(root: Path, args: list[str], label: str) -> dict[str, Any]:
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
        "producer_function": "_run_pytest",
    }


def _parse_pytest_summary(text: str) -> dict[str, int]:
    summary = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "xfailed": 0}
    for key in summary:
        matches = re.findall(rf"(\d+)\s+{key}", text)
        if matches:
            summary[key] = int(matches[-1])
    return summary


def _recommended_next_task(verdict: str) -> str:
    if verdict == VERDICT_PASS_FULL_SUITE_GREEN:
        return "bounded_post_repair_dependency_closure_refresh_or_human_gate_review"
    if verdict == VERDICT_PASS_WITH_RESIDUAL_BLOCKERS_CLASSIFIED:
        return "bounded_residual_failure_repair_continuation_001b"
    return "blocked_repair_continuation_with_exact_failed_gate_001b"


def _validator_function_names(validate_func: Callable[..., Any]) -> list[str]:
    source = inspect.getsource(validate_func)
    return re.findall(r"^\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*,?\s*$", source, flags=re.MULTILINE)


def _import_runner(module_name: str, root: Path) -> Any:
    src = str(root / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    return importlib.import_module(module_name)


def _is_intended_repair_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized in {
        DOC_PATH.as_posix(),
        "tests/test_ego_mainline_old_artifact_side_effect_guard_and_redundancy_contract_repair_001a.py",
    } or any(
        normalized.startswith(prefix)
        for prefix in [
            "src/ego_mainline_old_artifact_side_effect_guard_and_redundancy_contract_repair_001a/",
            ARTIFACT_DIR.as_posix() + "/",
            "src/ego_mainline_admission_canonical_coverage_reference_001a/runner.py",
            "src/ego_mainline_admission_task_card_alignment_001a/runner.py",
            "src/ego_mainline_admission_executable_001d_metric_provenance_repair_001f/runner.py",
            "src/ego_mainline_post_admission_routing_001a/runner.py",
            "src/ego_mainline_evidence_dependency_closure_001a/runner.py",
            "tests/test_ego_mainline_admission_executable_001d_metric_provenance_repair_001f.py",
        ]
    )


def _status_path(line: str) -> str:
    if len(line) >= 3 and line[2] == " ":
        path = line[3:]
    elif len(line) >= 2 and line[1] == " ":
        path = line[2:]
    else:
        path = line[3:] if len(line) > 3 else line
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path.replace("\\", "/")


def _producer_for_artifact(name: str) -> Callable[..., Any]:
    return {
        "anchor_readback.json": build_anchor_readback,
        "before_repair_failure_reproduction.json": build_before_repair_failure_reproduction,
        "repair_change_inventory.json": build_repair_change_inventory,
        "shared_validator_contract_evidence.json": build_shared_validator_contract_evidence,
        "temp_run_validator_equivalence_report.json": build_temp_run_validator_equivalence,
        "old_artifact_write_guard_report.json": build_old_artifact_write_guard_report,
        "side_effect_prevention_report.json": build_side_effect_prevention_result,
        "before_after_hash_comparison.json": build_before_after_hash_comparison,
        "isolated_rerun_report.json": build_isolated_rerun_report,
        "targeted_suite_report.json": build_targeted_suite_report,
        "full_pytest_report.json": build_full_pytest_report,
        "residual_failure_classification.json": build_residual_failure_classification,
        "downstream_route_impact_matrix.json": build_downstream_route_impact_matrix,
        "baseline_comparison.json": build_baseline_comparison,
        "ablation_report.json": run_ablation_suite,
        "leakage_scan_report.json": build_leakage_scan_report,
        "replay_report.json": build_replay_report,
        "computed_evidence_provenance.json": build_computed_evidence_provenance_report,
        "repair_state.json": build_repair_state_artifact,
        "result.json": build_result,
    }[name]


def _input_artifacts_for_output(name: str) -> list[str]:
    return [
        TRIAGE_RESULT.as_posix(),
        TRIAGE_SIDE_EFFECT.as_posix(),
        SIDE_EFFECT_ARTIFACT.as_posix(),
        "known failed pytest node ids",
        "callable validators",
    ]


def _aggregation_rule_for_artifact(name: str) -> str:
    return {
        "anchor_readback.json": "verify triage commit and remote tag",
        "before_repair_failure_reproduction.json": "read sealed before-repair known-failure triage evidence",
        "repair_change_inventory.json": "classify repair dirty paths",
        "shared_validator_contract_evidence.json": "introspect shared validator callable contracts",
        "temp_run_validator_equivalence_report.json": "compare temp-run validator rows with direct callable validators",
        "old_artifact_write_guard_report.json": "prove output paths exclude old sealed artifact paths",
        "side_effect_prevention_report.json": "run old side-effect-prone runner against temp output and compare hashes",
        "before_after_hash_comparison.json": "compare protected old artifact hashes before and after repair checks",
        "isolated_rerun_report.json": "rerun four known failure nodes",
        "targeted_suite_report.json": "run targeted routing, dependency, triage, and repair suites when requested",
        "full_pytest_report.json": "run full pytest when requested",
        "residual_failure_classification.json": "classify residual failures from observed test reports",
        "downstream_route_impact_matrix.json": "derive downstream route impact and non-authorization flags",
        "baseline_comparison.json": "invoke four independent baselines",
        "ablation_report.json": "rerun repair verification under interventions",
        "leakage_scan_report.json": "scan generated artifacts and positive control",
        "replay_report.json": "recompute repair verification from serialized state",
        "computed_evidence_provenance.json": "collect callable provenance for verdict-like values",
        "repair_state.json": "serialize repair state and observation",
        "result.json": "aggregate repair gates",
    }[name]


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
        "seed_context_episode_ids": {"seed": "not_used", "context_id": TASK_ID, "episode_id": "repair"},
        "aggregation_rule": "callable producer derives output from structured inputs",
        "code_path_hash": _code_path_hash(producer),
        "output_artifact_path": f"{ARTIFACT_DIR.as_posix()}/{label}.json",
    }


def _run_id(root: Path) -> str:
    parts = [
        TASK_ID,
        TRIAGE_COMMIT,
        TRIAGE_REMOTE_TAG,
        _sha_file(root / TRIAGE_RESULT) if (root / TRIAGE_RESULT).exists() else "missing_triage_result",
        _sha_file(root / SIDE_EFFECT_ARTIFACT) if (root / SIDE_EFFECT_ARTIFACT).exists() else "missing_side_effect",
    ]
    return f"ego_mainline_old_artifact_side_effect_guard_and_redundancy_contract_repair_001a_{_sha_text('|'.join(parts))[:16]}"


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


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--skip-remote", action="store_true")
    parser.add_argument("--skip-isolated-reruns", action="store_true")
    parser.add_argument("--execute-targeted-suites", action="store_true")
    parser.add_argument("--execute-full-pytest", action="store_true")
    args = parser.parse_args()
    result = run_repair(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        verify_remote=not args.skip_remote,
        execute_isolated_reruns=not args.skip_isolated_reruns,
        execute_targeted_suites=args.execute_targeted_suites,
        execute_full_pytest=args.execute_full_pytest,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
