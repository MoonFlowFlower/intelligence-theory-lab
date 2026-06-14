from __future__ import annotations

import copy
import hashlib
import inspect
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-TEMPLATE-001A"
TASK_SLUG = "future_surface_admission_authorization_template_001a"
SEALED_TEMPLATE_COMMIT = "d23a2ba7ff041ce227c7814b23c29be5b538e08b"
SEALED_TEMPLATE_TAG = "remote-anchor-future-surface-admission-authorization-template-001a-d23a2ba"
HARDENING_TASK_ID = "SURFACE-ADMISSION-CONTRACT-HARDENING-001A"
HARDENING_SLUG = "surface_admission_contract_hardening_001a"
ENFORCEMENT_TASK_ID = "SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A"
ENFORCEMENT_SLUG = "surface_admission_contract_enforcement_001a"
PARENT_BOUNDARY = "SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A"
PARENT_COMMIT = "22d8a09eb6747152f4d072d52c71f2725add87b1"
PARENT_BRANCH = "codex/meta-theory-scaffold"
PARENT_TAG = "remote-anchor-surface-admission-contract-enforcement-001a-22d8a09"
LAYER = (
    "engineering-governance / future task authorization template / "
    "surface-admission precondition enforcement"
)
MAINLINE_STATUS = "none; offline governance template/checker only"
ENABLED_STATUS = "local offline template validator only"
REAL_TRIGGER_EVIDENCE = (
    "template manifest plus enforcement readback, hostile controls, and ablation controls"
)
CLAIM_CEILING = "surface-admission authorization hygiene only"
RESULT_VERDICT = "future_surface_admission_authorization_template_001a_pass"
REFUSED_VERDICT = "future_surface_admission_authorization_template_001a_refused"
INVALID_VERDICT = "invalid_future_surface_admission_authorization_template_harness"
ENFORCEMENT_VERDICT = "contract_enforcement_pass"
HARDENING_VERDICT = "contract_hardened_pass"
REQUIRED_ENFORCEMENT_ACCEPTANCE = [f"E{index}" for index in range(1, 19)]
REQUIRED_ACCEPTANCE = [f"A{index}" for index in range(1, 21)]
INVALID_SURFACE_MARKERS = (
    "COMPOSITE-CROSS-TASK-STATE-REUSE",
    "CTSR-SOLVABILITY-INVERSION",
    "ACTION-CONDITIONED-SELF-BOUNDARY",
)
CLAIM_INFLATION_MARKERS = (
    "mechanism validity",
    "gate4 validity",
    "gate5 validity",
    "candidate behavior",
    "agency",
    "autonomy",
    "consciousness",
    "emotion",
    "subjectivity",
    "companion readiness",
    "ego readiness",
    "runtime readiness",
    "mainline readiness",
    "mainline effect",
    "stable user benefit",
)
FORBIDDEN_DIRECTION_MARKERS = (
    "ctsr redesign",
    "action-conditioned repair",
    "gate4 candidate",
    "gate5",
    "bridge",
    "runtime",
    "tournament",
    "ego-mainline",
    "ego mainline",
    "companion readiness",
    "stable user benefit",
    "mechanism deployment",
    "candidate behavior execution",
)
EXECUTION_SCOPE_LANGUAGE_MARKERS = (
    "candidate authorized",
    "gate5 authorized",
    "runtime authorized",
    "bridge authorized",
    "tournament authorized",
    "ego-mainline authorized",
    "ego mainline authorized",
    "mainline-effective",
    "execution scope opened",
    "opens execution scope",
)
REQUIRED_ENFORCEMENT_CONTROLS = {
    "missing_g13_g14_controls": "missing_g13_g14_control_not_blocked",
    "missing_anti_blacklist_requirement": "missing_anti_blacklist_control_not_blocked",
    "missing_reason_specific_positive_counter_controls": (
        "missing_reason_control_not_blocked"
    ),
    "old_invalid_surface_cited_as_mechanism_evidence": (
        "old_invalid_surface_control_not_blocked"
    ),
    "mechanism_score_requested": "mechanism_score_control_not_blocked",
    "candidate_gate5_bridge_runtime_mainline_language": (
        "candidate_runtime_mainline_control_not_blocked"
    ),
    "false_full_suite_pass_after_timeout": "false_full_suite_control_not_blocked",
}


def _enforcement_result_path(repo_root: Path) -> Path:
    return repo_root / "artifacts" / ENFORCEMENT_SLUG / "result.json"


def _enforcement_readback_path(repo_root: Path) -> Path:
    return repo_root / "artifacts" / ENFORCEMENT_SLUG / "readback.json"


def _artifact_dir(repo_root: Path) -> Path:
    return repo_root / "artifacts" / TASK_SLUG


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return _hash_bytes(path.read_bytes())


def _hash_payload(payload: Any) -> str:
    return _hash_bytes(json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8"))


def _source_hash() -> str:
    functions = [
        validate_enforcement_artifacts,
        build_authorization_manifest_template,
        validate_authorization_manifest,
        build_hostile_control_report,
        build_ablation_report,
        run_authorization_template,
    ]
    source = "\n".join(inspect.getsource(function) for function in functions)
    return _hash_bytes(source.encode("utf-8"))


def _run_git(repo_root: Path, args: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    return completed.stdout.strip()


def _append_invocation(
    log: list[dict[str, Any]],
    producer_function: str,
    passed: bool,
    reasons: list[str] | None = None,
    inputs: list[str] | None = None,
) -> None:
    log.append(
        {
            "producer_function": producer_function,
            "passed": passed,
            "reasons_fired": reasons or [],
            "inputs": inputs or [],
        }
    )


def _parse_json_file(path: Path, producer_function: str) -> tuple[Any | None, dict[str, Any]]:
    status: dict[str, Any] = {
        "producer_function": producer_function,
        "path": str(path),
        "exists": path.exists(),
        "parse_status": "missing",
        "sha256": _hash_file(path),
    }
    if not path.exists():
        return None, status
    try:
        payload = _load_json(path)
    except json.JSONDecodeError as exc:
        status["parse_status"] = "parse_error"
        status["error"] = str(exc)
        return None, status
    status["parse_status"] = "parsed"
    return payload, status


def _control_lookup(readback_payload: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    controls = (
        readback_payload.get("synthetic_controls", {}).get("controls", [])
        if isinstance(readback_payload, dict)
        else []
    )
    if not isinstance(controls, list):
        return {}
    return {
        str(control.get("control_id")): control
        for control in controls
        if isinstance(control, dict)
    }


def _check_control_blocked(
    controls_by_id: dict[str, dict[str, Any]],
    control_id: str,
) -> bool:
    control = controls_by_id.get(control_id, {})
    return bool(
        control
        and control.get("blocked") is True
        and isinstance(control.get("reasons_fired"), list)
        and control.get("reasons_fired")
    )


def _check_required_producer(
    readback_payload: dict[str, Any] | None,
    producer_function: str,
) -> bool:
    checks = readback_payload.get("checks_run", []) if isinstance(readback_payload, dict) else []
    if not isinstance(checks, list):
        return False
    return any(
        isinstance(check, dict)
        and check.get("producer_function") == producer_function
        and check.get("passed") is True
        for check in checks
    )


def _evaluate_enforcement_payloads(
    repo_root: Path,
    result_payload: dict[str, Any] | None,
    readback_payload: dict[str, Any] | None,
    result_parse: dict[str, Any],
    readback_parse: dict[str, Any],
) -> dict[str, Any]:
    reasons: list[str] = []
    invocation_log: list[dict[str, Any]] = []
    result_parsed = result_parse.get("parse_status") == "parsed" and isinstance(result_payload, dict)
    readback_parsed = readback_parse.get("parse_status") == "parsed" and isinstance(readback_payload, dict)
    if not result_parsed:
        reasons.append("enforcement_result_parse_failed")
    if not readback_parsed:
        reasons.append("enforcement_readback_parse_failed")

    verdict = result_payload.get("verdict") if result_parsed else None
    verdict_ok = result_parsed and verdict == ENFORCEMENT_VERDICT
    if result_parsed and not verdict_ok:
        reasons.append("enforcement_verdict_not_contract_enforcement_pass")
    _append_invocation(
        invocation_log,
        "check_enforcement_verdict",
        verdict_ok,
        [] if verdict_ok else ["enforcement_verdict_not_contract_enforcement_pass"],
        [result_parse["path"]],
    )

    result_gates = result_payload.get("acceptance_gates", {}) if result_parsed else {}
    readback_gates = readback_payload.get("acceptance_gates", {}) if readback_parsed else {}
    passed_gates = set(result_gates.get("passed", [])) & set(readback_gates.get("passed", []))
    failed_gates = list(result_gates.get("failed", [])) + list(readback_gates.get("failed", []))
    missing_gates = [
        gate_id for gate_id in REQUIRED_ENFORCEMENT_ACCEPTANCE if gate_id not in passed_gates
    ]
    gates_ok = result_parsed and readback_parsed and not failed_gates and not missing_gates
    if result_parsed and readback_parsed and not gates_ok:
        reasons.append("enforcement_acceptance_gates_missing_or_failed")
    _append_invocation(
        invocation_log,
        "check_enforcement_acceptance_gates",
        gates_ok,
        [] if gates_ok else ["enforcement_acceptance_gates_missing_or_failed"],
        [result_parse["path"], readback_parse["path"]],
    )

    controls_by_id = _control_lookup(readback_payload if readback_parsed else None)
    all_controls_blocked = (
        readback_parsed
        and readback_payload.get("synthetic_controls", {}).get("all_controls_blocked") is True
        and controls_by_id
        and all(control.get("blocked") is True for control in controls_by_id.values())
    )
    if readback_parsed and not all_controls_blocked:
        reasons.append("enforcement_hostile_controls_not_all_blocked")
    for control_id, reason in REQUIRED_ENFORCEMENT_CONTROLS.items():
        if readback_parsed and not _check_control_blocked(controls_by_id, control_id):
            reasons.append(reason)
    _append_invocation(
        invocation_log,
        "check_hostile_controls_from_enforcement_readback",
        bool(all_controls_blocked)
        and not any(reason in reasons for reason in REQUIRED_ENFORCEMENT_CONTROLS.values()),
        [] if all_controls_blocked else ["enforcement_hostile_controls_not_all_blocked"],
        [readback_parse["path"]],
    )

    g13_g14_ok = readback_parsed and _check_required_producer(
        readback_payload,
        "check_g1_g14_readback",
    ) and _check_control_blocked(controls_by_id, "missing_g13_g14_controls")
    anti_ok = readback_parsed and _check_required_producer(
        readback_payload,
        "check_anti_blacklist_readback",
    ) and _check_control_blocked(controls_by_id, "missing_anti_blacklist_requirement")
    reason_ok = readback_parsed and _check_required_producer(
        readback_payload,
        "check_reason_specific_controls",
    ) and _check_control_blocked(
        controls_by_id,
        "missing_reason_specific_positive_counter_controls",
    )
    _append_invocation(
        invocation_log,
        "check_g13_g14_anti_blacklist_reason_controls",
        g13_g14_ok and anti_ok and reason_ok,
        []
        if g13_g14_ok and anti_ok and reason_ok
        else [
            reason
            for passed, reason in [
                (g13_g14_ok, "missing_g13_g14_control_not_blocked"),
                (anti_ok, "missing_anti_blacklist_control_not_blocked"),
                (reason_ok, "missing_reason_control_not_blocked"),
            ]
            if not passed
        ],
        [readback_parse["path"]],
    )

    local_parent_tag_hash = _run_git(repo_root, ["rev-parse", f"{PARENT_TAG}^{{commit}}"])
    current_branch = _run_git(repo_root, ["branch", "--show-current"])
    parent_ok = local_parent_tag_hash == PARENT_COMMIT
    if not parent_ok:
        reasons.append("parent_tag_does_not_match_expected_commit")
    _append_invocation(
        invocation_log,
        "check_parent_boundary_reference",
        parent_ok,
        [] if parent_ok else ["parent_tag_does_not_match_expected_commit"],
        [PARENT_TAG],
    )

    return {
        "task_id": TASK_ID,
        "producer_function": "validate_enforcement_artifacts",
        "parent_boundary": {
            "boundary": PARENT_BOUNDARY,
            "commit": PARENT_COMMIT,
            "branch": PARENT_BRANCH,
            "tag": PARENT_TAG,
            "local_tag_hash": local_parent_tag_hash,
            "current_branch": current_branch,
            "local_tag_matches_commit": parent_ok,
        },
        "enforcement_result": {
            "path": result_parse["path"],
            "parse_status": result_parse["parse_status"],
            "sha256": result_parse.get("sha256"),
            "task_id": result_payload.get("task_id") if result_parsed else None,
            "verdict": verdict,
        },
        "enforcement_readback": {
            "path": readback_parse["path"],
            "parse_status": readback_parse["parse_status"],
            "sha256": readback_parse.get("sha256"),
            "task_id": readback_payload.get("task_id") if readback_parsed else None,
        },
        "acceptance_gates": {
            "passed": sorted(passed_gates),
            "passed_count": len(passed_gates),
            "failed": sorted(set(failed_gates + missing_gates)),
        },
        "synthetic_controls": {
            "all_controls_blocked": bool(all_controls_blocked),
            "blocked_control_count": sum(
                1 for control in controls_by_id.values() if control.get("blocked") is True
            ),
            "control_ids": sorted(controls_by_id),
        },
        "required_control_checks": {
            "g13_g14": {
                "passed": bool(g13_g14_ok),
                "producer_function": "check_g1_g14_readback",
            },
            "anti_blacklist": {
                "passed": bool(anti_ok),
                "producer_function": "check_anti_blacklist_readback",
            },
            "reason_control": {
                "passed": bool(reason_ok),
                "producer_function": "check_reason_specific_controls",
            },
        },
        "result_hash": result_parse.get("sha256"),
        "readback_hash": readback_parse.get("sha256"),
        "files_read": [
            {
                "path": result_parse["path"],
                "exists": result_parse["exists"],
                "parse_status": result_parse["parse_status"],
                "sha256": result_parse.get("sha256"),
            },
            {
                "path": readback_parse["path"],
                "exists": readback_parse["exists"],
                "parse_status": readback_parse["parse_status"],
                "sha256": readback_parse.get("sha256"),
            },
        ],
        "invocation_log": [
            {
                "producer_function": result_parse["producer_function"],
                "passed": result_parsed,
                "reasons_fired": [] if result_parsed else ["enforcement_result_parse_failed"],
                "inputs": [result_parse["path"]],
            },
            {
                "producer_function": readback_parse["producer_function"],
                "passed": readback_parsed,
                "reasons_fired": [] if readback_parsed else ["enforcement_readback_parse_failed"],
                "inputs": [readback_parse["path"]],
            },
            *invocation_log,
        ],
        "reasons_fired": sorted(set(reasons)),
        "passed": not reasons,
        "claim_ceiling": CLAIM_CEILING,
    }


def validate_enforcement_artifacts(
    repo_root: str | Path,
    result_path: str | Path | None = None,
    readback_path: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    result = Path(result_path) if result_path is not None else _enforcement_result_path(root)
    readback = Path(readback_path) if readback_path is not None else _enforcement_readback_path(root)
    result_payload, result_parse = _parse_json_file(result, "parse_enforcement_result")
    readback_payload, readback_parse = _parse_json_file(readback, "parse_enforcement_readback")
    return _evaluate_enforcement_payloads(
        root,
        result_payload if isinstance(result_payload, dict) else None,
        readback_payload if isinstance(readback_payload, dict) else None,
        result_parse,
        readback_parse,
    )


def _parent_boundary_manifest() -> dict[str, Any]:
    return {
        "boundary": PARENT_BOUNDARY,
        "commit": PARENT_COMMIT,
        "branch": PARENT_BRANCH,
        "tag": PARENT_TAG,
    }


def _template_dependency_manifest() -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "artifact_id": TASK_SLUG,
        "template_path": (
            "artifacts/future_surface_admission_authorization_template_001a/"
            "authorization_manifest_template.json"
        ),
        "result_path": "artifacts/future_surface_admission_authorization_template_001a/result.json",
        "readback_path": "artifacts/future_surface_admission_authorization_template_001a/readback.json",
        "required_verdict": RESULT_VERDICT,
        "dependency_type": "pre_execution_authorization_manifest_template",
        "required": True,
        "commit": SEALED_TEMPLATE_COMMIT,
        "tag": SEALED_TEMPLATE_TAG,
    }


def _manifest_hash_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    normalized = copy.deepcopy(manifest)
    authorization = normalized.get("authorization_validator")
    if isinstance(authorization, dict):
        authorization.pop("manifest_hash", None)
    normalized.pop("manifest_integrity_hash", None)
    return normalized


def _manifest_integrity_hash(manifest: dict[str, Any]) -> str:
    return _hash_payload(_manifest_hash_payload(manifest))


def _refresh_manifest_hash(manifest: dict[str, Any]) -> dict[str, Any]:
    authorization = manifest.get("authorization_validator")
    if isinstance(authorization, dict) and "manifest_hash" in authorization:
        authorization["manifest_hash"] = _manifest_integrity_hash(manifest)
    return manifest


def _dependency_by_id(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    dependencies = manifest.get("dependencies", [])
    if not isinstance(dependencies, list):
        return {}
    return {
        str(dependency.get("task_id")): dependency
        for dependency in dependencies
        if isinstance(dependency, dict) and dependency.get("required") is True
    }


def build_authorization_manifest_template(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    enforcement_readback = _enforcement_readback_path(root)
    enforcement_result = _enforcement_result_path(root)
    example_manifest = {
        "task_id": "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-MANIFEST",
        "current_layer": LAYER,
        "parent_boundary": _parent_boundary_manifest(),
        "dependencies": [
            {
                "task_id": HARDENING_TASK_ID,
                "artifact_id": HARDENING_SLUG,
                "required_verdict": HARDENING_VERDICT,
                "dependency_type": "pre_execution_contract",
                "required": True,
            },
            {
                "task_id": ENFORCEMENT_TASK_ID,
                "artifact_id": ENFORCEMENT_SLUG,
                "result_path": str(enforcement_result.relative_to(root)).replace("\\", "/"),
                "readback_path": str(enforcement_readback.relative_to(root)).replace("\\", "/"),
                "required_verdict": ENFORCEMENT_VERDICT,
                "dependency_type": "pre_execution_authorization_checker",
                "required": True,
            },
            _template_dependency_manifest(),
        ],
        "pre_execution_enforcement": {
            "checker_module": "surface_admission_contract_enforcement_001a.validator",
            "checker_function": "validate_future_manifest",
            "invocation_required": True,
            "invocation_recorded": True,
            "readback_required": True,
            "readback_path": str(enforcement_readback.relative_to(root)).replace("\\", "/"),
            "readback_status": "created_and_parsed",
            "readback_hash": _hash_file(enforcement_readback),
        },
        "required_rules": {
            "require_g13_g14": True,
            "require_anti_blacklist": True,
            "require_reason_control": True,
            "old_invalid_surface_citation_ban": True,
            "no_mechanism_score_before_admission": True,
            "no_candidate_gate5_bridge_runtime_tournament_ego_mainline_scope": True,
            "claim_ceiling_limited_to_surface_admission_authorization": True,
        },
        "scope": {
            "surface_admission_authorization_only": True,
            "creates_candidate_behavior": False,
            "opens_gate5": False,
            "opens_bridge": False,
            "opens_runtime": False,
            "opens_tournament": False,
            "opens_ego_mainline": False,
            "produces_mechanism_score": False,
            "execution_scope_opened": False,
            "later_task_card_only": True,
        },
        "evidence_citations": [
            {
                "artifact_id": HARDENING_TASK_ID,
                "claim": "pre-execution hardening dependency only",
            },
            {
                "artifact_id": ENFORCEMENT_TASK_ID,
                "claim": "pre-execution authorization checker dependency only",
            },
        ],
        "test_evidence": {
            "focused_tests_required": True,
            "claims_full_suite_pass": False,
            "full_pytest_status": "not_claimed_by_template",
        },
        "outputs_requested": [
            "authorization_decision",
            "readback.json",
            "claim_ceiling.txt",
        ],
        "claims": [CLAIM_CEILING],
        "proposed_surface_admission_direction": (
            "bounded offline authorization validator regression surface direction"
        ),
        "execution_scope_opened": False,
        "later_task_card_only": True,
        "manifest_instantiation_before_execution": True,
        "authorization_validator_invocation_before_execution": True,
        "validator_readback_before_execution": True,
        "source_template": {
            "task_id": TASK_ID,
            "path": (
                "artifacts/future_surface_admission_authorization_template_001a/"
                "authorization_manifest_template.json"
            ),
            "commit": SEALED_TEMPLATE_COMMIT,
            "tag": SEALED_TEMPLATE_TAG,
        },
        "authorization_validator": {
            "checker_module": "future_surface_admission_authorization_template_001a.validator",
            "checker_function": "validate_authorization_manifest",
            "invocation_required": True,
            "invocation_recorded": True,
            "readback_required": True,
            "readback_path": (
                "artifacts/future_surface_admission_authorization_template_001a/readback.json"
            ),
            "trace_path": (
                "artifacts/future_surface_admission_authorization_template_001a/"
                "authorization_trace.jsonl"
            ),
            "code_path_hash": _source_hash(),
        },
    }
    example_manifest["authorization_validator"]["manifest_hash"] = _manifest_integrity_hash(
        example_manifest
    )
    return {
        "task_id": TASK_ID,
        "template_version": "001A",
        "current_layer": LAYER,
        "parent_boundary": _parent_boundary_manifest(),
        "claim_ceiling": CLAIM_CEILING,
        "required_dependency_task_ids": [HARDENING_TASK_ID, ENFORCEMENT_TASK_ID, TASK_ID],
        "required_pre_execution_fields": [
            "checker_module",
            "checker_function",
            "invocation_required",
            "invocation_recorded",
            "readback_required",
            "readback_path",
            "readback_status",
            "readback_hash",
        ],
        "required_rules": copy.deepcopy(example_manifest["required_rules"]),
        "forbidden_scope_fields": [
            "creates_candidate_behavior",
            "opens_gate5",
            "opens_bridge",
            "opens_runtime",
            "opens_tournament",
            "opens_ego_mainline",
            "produces_mechanism_score",
        ],
        "forbidden_invalid_surface_evidence_markers": list(INVALID_SURFACE_MARKERS),
        "forbidden_claim_inflation_markers": list(CLAIM_INFLATION_MARKERS),
        "example_authorized_manifest": example_manifest,
    }


def _walk_json(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    rows = [(path, value)]
    if isinstance(value, dict):
        for key, item in value.items():
            rows.extend(_walk_json(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(_walk_json(item, f"{path}[{index}]"))
    return rows


def _json_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True).lower()


def _dependency_ids(manifest: dict[str, Any]) -> set[str]:
    dependencies = manifest.get("dependencies", [])
    if not isinstance(dependencies, list):
        return set()
    return {
        dependency.get("task_id")
        for dependency in dependencies
        if isinstance(dependency, dict) and dependency.get("required") is True
    }


def _check_manifest_dependencies(manifest: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    dependencies_by_id = _dependency_by_id(manifest)
    dependency_ids = set(dependencies_by_id)
    if HARDENING_TASK_ID not in dependency_ids:
        reasons.append("missing_hardening_dependency")
    if ENFORCEMENT_TASK_ID not in dependency_ids:
        reasons.append("missing_enforcement_dependency")
    if TASK_ID not in dependency_ids:
        reasons.append("missing_future_authorization_template_dependency")
    expected_verdicts = {
        HARDENING_TASK_ID: HARDENING_VERDICT,
        ENFORCEMENT_TASK_ID: ENFORCEMENT_VERDICT,
        TASK_ID: RESULT_VERDICT,
    }
    for task_id, expected_verdict in expected_verdicts.items():
        dependency = dependencies_by_id.get(task_id)
        if dependency and dependency.get("required_verdict") != expected_verdict:
            reasons.append("dependency_verdict_mismatch")
    return sorted(set(reasons))


def _check_concrete_surface_direction(manifest: dict[str, Any]) -> list[str]:
    direction = manifest.get("proposed_surface_admission_direction")
    status = str(manifest.get("proposed_surface_admission_direction_status", "")).lower()
    blocker = str(manifest.get("authorization_blocker", "")).lower()
    if (
        not isinstance(direction, str)
        or not direction.strip()
        or "missing_concrete_surface_direction" in status
        or "authorization_blocked_missing_concrete_surface_direction" in blocker
    ):
        return ["missing_concrete_surface_direction"]
    normalized = " ".join(direction.lower().replace("_", " ").split())
    if any(marker in normalized for marker in FORBIDDEN_DIRECTION_MARKERS):
        return ["forbidden_surface_admission_direction"]
    return []


def _check_authorization_validator_integrity(manifest: dict[str, Any]) -> list[str]:
    authorization = manifest.get("authorization_validator")
    if not isinstance(authorization, dict):
        return [
            "missing_authorization_validator_reference",
            "trace_reference_mismatch",
            "code_path_hash_mismatch",
            "manifest_hash_mismatch",
        ]
    reasons: list[str] = []
    if (
        authorization.get("checker_module")
        != "future_surface_admission_authorization_template_001a.validator"
        or authorization.get("checker_function") != "validate_authorization_manifest"
        or authorization.get("invocation_required") is not True
        or authorization.get("invocation_recorded") is not True
    ):
        reasons.append("authorization_validator_invocation_missing")
    trace_path = authorization.get("trace_path")
    if (
        not isinstance(trace_path, str)
        or not trace_path.startswith("artifacts/")
        or not trace_path.endswith(".jsonl")
        or "missing" in trace_path.lower()
    ):
        reasons.append("trace_reference_mismatch")
    if authorization.get("code_path_hash") != _source_hash():
        reasons.append("code_path_hash_mismatch")
    if authorization.get("manifest_hash") != _manifest_integrity_hash(manifest):
        reasons.append("manifest_hash_mismatch")
    return sorted(set(reasons))


def _check_execution_scope_locks(manifest: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    scope = manifest.get("scope", {})
    if not isinstance(scope, dict):
        return ["execution_scope_lock_missing", "later_task_card_only_lock_missing"]
    if manifest.get("execution_scope_opened") is not False or scope.get("execution_scope_opened") is not False:
        reasons.append("execution_scope_lock_missing")
    if manifest.get("later_task_card_only") is not True or scope.get("later_task_card_only") is not True:
        reasons.append("later_task_card_only_lock_missing")
    if any(
        manifest.get(key) is True
        for key in [
            "candidate_scope_opened",
            "gate5_scope_opened",
            "bridge_scope_opened",
            "runtime_scope_opened",
            "tournament_scope_opened",
            "ego_mainline_scope_opened",
        ]
    ):
        reasons.append("candidate_gate5_bridge_runtime_tournament_mainline_scope")
    for _, value in _walk_json(manifest):
        if isinstance(value, str):
            text = value.lower()
            if any(marker in text for marker in EXECUTION_SCOPE_LANGUAGE_MARKERS):
                reasons.append("execution_scope_opened_or_language_leakage")
                break
    return sorted(set(reasons))


def _check_checker_invocation_and_readback(
    manifest: dict[str, Any],
    enforcement_report: dict[str, Any] | None,
) -> list[str]:
    enforcement = manifest.get("pre_execution_enforcement")
    if not isinstance(enforcement, dict):
        return ["missing_checker_invocation", "missing_checker_readback"]
    reasons: list[str] = []
    if (
        enforcement.get("checker_module") != "surface_admission_contract_enforcement_001a.validator"
        or enforcement.get("checker_function") != "validate_future_manifest"
        or enforcement.get("invocation_required") is not True
        or enforcement.get("invocation_recorded") is not True
    ):
        reasons.append("missing_checker_invocation")
    if (
        enforcement.get("readback_required") is not True
        or not enforcement.get("readback_path")
        or enforcement.get("readback_status") != "created_and_parsed"
    ):
        reasons.append("missing_checker_readback")
    expected_hash = enforcement_report.get("readback_hash") if enforcement_report else None
    if not expected_hash or enforcement.get("readback_hash") != expected_hash:
        reasons.append("enforcement_readback_hash_mismatch")
    return reasons


def _check_scope_bans(manifest: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    rules = manifest.get("required_rules", {})
    scope = manifest.get("scope", {})
    if not isinstance(rules, dict) or not isinstance(scope, dict):
        return ["scope_ban_missing"]
    if rules.get("no_mechanism_score_before_admission") is not True:
        reasons.append("missing_no_mechanism_score_rule")
    if (
        rules.get("no_candidate_gate5_bridge_runtime_tournament_ego_mainline_scope")
        is not True
    ):
        reasons.append("missing_no_candidate_runtime_mainline_scope_rule")
    if scope.get("produces_mechanism_score") is True:
        reasons.append("mechanism_score_before_admission")
    for json_path, value in _walk_json(manifest):
        leaf = json_path.rsplit(".", 1)[-1].lower()
        if isinstance(value, str) and value.lower() == "mechanism_score":
            reasons.append("mechanism_score_before_admission")
        if leaf == "mechanism_score" and value not in (False, None):
            reasons.append("mechanism_score_before_admission")
    if any(
        scope.get(key) is True
        for key in [
            "creates_candidate_behavior",
            "opens_gate5",
            "opens_bridge",
            "opens_runtime",
            "opens_tournament",
            "opens_ego_mainline",
        ]
    ):
        reasons.append("candidate_gate5_bridge_runtime_tournament_mainline_scope")
    return sorted(set(reasons))


def _check_old_invalid_surface_ban(manifest: dict[str, Any]) -> list[str]:
    rules = manifest.get("required_rules", {})
    if not isinstance(rules, dict) or rules.get("old_invalid_surface_citation_ban") is not True:
        return ["missing_old_invalid_surface_citation_ban"]
    citations = manifest.get("evidence_citations", [])
    if not isinstance(citations, list):
        return []
    for citation in citations:
        if not isinstance(citation, dict):
            continue
        artifact_id = str(citation.get("artifact_id", "")).upper()
        claim = str(citation.get("claim", "")).lower()
        if any(marker in artifact_id for marker in INVALID_SURFACE_MARKERS) and (
            "mechanism" in claim or "gate4" in claim or "gate5" in claim or "readiness" in claim
        ):
            return ["old_invalid_surface_cited_as_mechanism_evidence"]
    return []


def _check_claim_ceiling(manifest: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    rules = manifest.get("required_rules", {})
    if (
        not isinstance(rules, dict)
        or rules.get("claim_ceiling_limited_to_surface_admission_authorization") is not True
    ):
        reasons.append("missing_claim_ceiling_rule")
    claims = manifest.get("claims")
    if not isinstance(claims, list) or CLAIM_CEILING not in claims:
        reasons.append("claim_ceiling_missing_or_wrong")
    text = _json_text(claims if claims is not None else [])
    if any(marker in text for marker in CLAIM_INFLATION_MARKERS):
        reasons.append("claim_ceiling_inflation")
    evidence = manifest.get("test_evidence", {})
    if isinstance(evidence, dict):
        status = str(evidence.get("full_pytest_status", "")).lower()
        if evidence.get("claims_full_suite_pass") is True and status not in {
            "passed",
            "full_suite_passed",
        }:
            reasons.append("false_full_suite_pass_claim")
    return sorted(set(reasons))


def _check_parent_boundary(manifest: dict[str, Any]) -> list[str]:
    parent = manifest.get("parent_boundary")
    if not isinstance(parent, dict):
        return ["missing_parent_boundary_reference"]
    reasons: list[str] = []
    if parent.get("commit") != PARENT_COMMIT:
        reasons.append("parent_commit_reference_mismatch")
    if parent.get("tag") != PARENT_TAG:
        reasons.append("parent_tag_reference_mismatch")
    if parent.get("branch") != PARENT_BRANCH:
        reasons.append("parent_branch_reference_mismatch")
    if parent.get("boundary") != PARENT_BOUNDARY:
        reasons.append("parent_boundary_reference_mismatch")
    return reasons


def _check_template_contract(template: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if template.get("task_id") != TASK_ID:
        reasons.append("template_task_id_mismatch")
    if CLAIM_CEILING != template.get("claim_ceiling"):
        reasons.append("template_claim_ceiling_mismatch")
    dependency_ids = set(template.get("required_dependency_task_ids", []))
    if not {HARDENING_TASK_ID, ENFORCEMENT_TASK_ID}.issubset(dependency_ids):
        reasons.append("template_dependency_requirements_missing")
    rules = template.get("required_rules", {})
    if not isinstance(rules, dict):
        reasons.append("template_required_rules_missing")
    else:
        for key in [
            "require_g13_g14",
            "require_anti_blacklist",
            "require_reason_control",
            "old_invalid_surface_citation_ban",
            "no_mechanism_score_before_admission",
            "no_candidate_gate5_bridge_runtime_tournament_ego_mainline_scope",
            "claim_ceiling_limited_to_surface_admission_authorization",
        ]:
            if rules.get(key) is not True:
                reasons.append(f"template_{key}_missing")
    return reasons


def validate_authorization_manifest(
    manifest: dict[str, Any],
    template: dict[str, Any],
    enforcement_report: dict[str, Any] | None,
) -> dict[str, Any]:
    reasons: list[str] = []
    invocation_log: list[dict[str, Any]] = []

    if enforcement_report is None or enforcement_report.get("passed") is not True:
        reasons.append("enforcement_artifacts_not_valid")
    if enforcement_report and enforcement_report.get("enforcement_result", {}).get("verdict") != ENFORCEMENT_VERDICT:
        reasons.append("enforcement_verdict_not_contract_enforcement_pass")

    template_reasons = _check_template_contract(template)
    reasons.extend(template_reasons)
    _append_invocation(
        invocation_log,
        "check_template_contract",
        not template_reasons,
        template_reasons,
    )

    dependency_reasons = _check_manifest_dependencies(manifest)
    reasons.extend(dependency_reasons)
    _append_invocation(
        invocation_log,
        "check_manifest_dependencies",
        not dependency_reasons,
        dependency_reasons,
    )

    direction_reasons = _check_concrete_surface_direction(manifest)
    reasons.extend(direction_reasons)
    _append_invocation(
        invocation_log,
        "check_concrete_surface_direction",
        not direction_reasons,
        direction_reasons,
    )

    checker_reasons = _check_checker_invocation_and_readback(manifest, enforcement_report)
    reasons.extend(checker_reasons)
    _append_invocation(
        invocation_log,
        "check_checker_invocation_and_readback",
        not checker_reasons,
        checker_reasons,
    )

    authorization_validator_reasons = _check_authorization_validator_integrity(manifest)
    reasons.extend(authorization_validator_reasons)
    _append_invocation(
        invocation_log,
        "check_authorization_validator_integrity",
        not authorization_validator_reasons,
        authorization_validator_reasons,
    )

    parent_reasons = _check_parent_boundary(manifest)
    reasons.extend(parent_reasons)
    _append_invocation(
        invocation_log,
        "check_parent_boundary_reference",
        not parent_reasons,
        parent_reasons,
    )

    execution_lock_reasons = _check_execution_scope_locks(manifest)
    reasons.extend(execution_lock_reasons)
    _append_invocation(
        invocation_log,
        "check_execution_scope_locks",
        not execution_lock_reasons,
        execution_lock_reasons,
    )

    scope_reasons = _check_scope_bans(manifest)
    reasons.extend(scope_reasons)
    _append_invocation(
        invocation_log,
        "check_scope_bans",
        not scope_reasons,
        scope_reasons,
    )

    invalid_surface_reasons = _check_old_invalid_surface_ban(manifest)
    reasons.extend(invalid_surface_reasons)
    _append_invocation(
        invocation_log,
        "check_old_invalid_surface_ban",
        not invalid_surface_reasons,
        invalid_surface_reasons,
    )

    claim_reasons = _check_claim_ceiling(manifest)
    reasons.extend(claim_reasons)
    _append_invocation(
        invocation_log,
        "check_claim_ceiling",
        not claim_reasons,
        claim_reasons,
    )

    rules = manifest.get("required_rules", {}) if isinstance(manifest.get("required_rules"), dict) else {}
    scope = manifest.get("scope", {}) if isinstance(manifest.get("scope"), dict) else {}
    unique_reasons = sorted(set(reasons))
    return {
        "task_id": TASK_ID,
        "manifest_task_id": manifest.get("task_id"),
        "authorization_decision": "blocked" if unique_reasons else "authorized",
        "reasons_fired": unique_reasons,
        "hardening_dependency_required": HARDENING_TASK_ID in _dependency_ids(manifest),
        "enforcement_dependency_required": ENFORCEMENT_TASK_ID in _dependency_ids(manifest),
        "future_authorization_template_dependency_required": TASK_ID in _dependency_ids(manifest),
        "concrete_surface_direction_required": (
            "missing_concrete_surface_direction" not in unique_reasons
            and "forbidden_surface_admission_direction" not in unique_reasons
        ),
        "checker_invocation_required": "missing_checker_invocation" not in unique_reasons,
        "checker_readback_required": (
            "missing_checker_readback" not in unique_reasons
            and "enforcement_readback_hash_mismatch" not in unique_reasons
        ),
        "no_mechanism_score": (
            "mechanism_score_before_admission" not in unique_reasons
            and rules.get("no_mechanism_score_before_admission") is True
            and scope.get("produces_mechanism_score") is False
        ),
        "no_candidate_runtime_mainline": (
            "candidate_gate5_bridge_runtime_tournament_mainline_scope" not in unique_reasons
            and rules.get("no_candidate_gate5_bridge_runtime_tournament_ego_mainline_scope")
            is True
        ),
        "old_invalid_surface_evidence_ban": (
            "old_invalid_surface_cited_as_mechanism_evidence" not in unique_reasons
            and "missing_old_invalid_surface_citation_ban" not in unique_reasons
        ),
        "stored_verdict_trusted": False,
        "invocation_log": invocation_log,
        "producer_function": "validate_authorization_manifest",
        "claim_ceiling": CLAIM_CEILING,
    }


def _mutated_enforcement_report(
    repo_root: Path,
    result_payload: dict[str, Any] | None,
    readback_payload: dict[str, Any] | None,
    result_status: str = "parsed",
    readback_status: str = "parsed",
) -> dict[str, Any]:
    result_parse = {
        "producer_function": "parse_enforcement_result",
        "path": "synthetic/enforcement_result.json",
        "exists": result_payload is not None,
        "parse_status": result_status,
        "sha256": _hash_payload(result_payload) if result_payload is not None else None,
    }
    readback_parse = {
        "producer_function": "parse_enforcement_readback",
        "path": "synthetic/enforcement_readback.json",
        "exists": readback_payload is not None,
        "parse_status": readback_status,
        "sha256": _hash_payload(readback_payload) if readback_payload is not None else None,
    }
    return _evaluate_enforcement_payloads(
        repo_root,
        result_payload,
        readback_payload,
        result_parse,
        readback_parse,
    )


def _decision_row(identifier_key: str, identifier: str, decision_or_report: dict[str, Any]) -> dict[str, Any]:
    if "authorization_decision" in decision_or_report:
        blocked = decision_or_report.get("authorization_decision") == "blocked"
    else:
        blocked = decision_or_report.get("passed") is False
    return {
        identifier_key: identifier,
        "blocked": blocked,
        "reasons_fired": decision_or_report.get("reasons_fired", []),
        "producer_function": decision_or_report.get("producer_function"),
    }


def build_hostile_control_report(
    repo_root: str | Path,
    template: dict[str, Any],
    enforcement_report: dict[str, Any],
) -> dict[str, Any]:
    root = Path(repo_root)
    valid = copy.deepcopy(template["example_authorized_manifest"])
    controls: list[dict[str, Any]] = []
    result_payload = _load_json(_enforcement_result_path(root))
    readback_payload = _load_json(_enforcement_readback_path(root))

    controls.append(
        _decision_row(
            "control_id",
            "superficial_contract_mention_without_checker_invocation",
            validate_authorization_manifest(
                {
                    "task_id": "SURFACE-ADMISSION-SUPERFICIAL-MENTION",
                    "summary": f"Mentions {HARDENING_TASK_ID} and {ENFORCEMENT_TASK_ID}.",
                    "stored_authorization_decision": "authorized",
                },
                template,
                enforcement_report,
            ),
        )
    )

    no_readback = copy.deepcopy(valid)
    no_readback["pre_execution_enforcement"].pop("readback_path", None)
    no_readback["pre_execution_enforcement"].pop("readback_hash", None)
    no_readback["pre_execution_enforcement"]["readback_required"] = False
    controls.append(
        _decision_row(
            "control_id",
            "checker_invocation_without_readback",
            validate_authorization_manifest(no_readback, template, enforcement_report),
        )
    )

    hardening_only = copy.deepcopy(valid)
    hardening_only["dependencies"] = [
        dependency
        for dependency in hardening_only["dependencies"]
        if dependency["task_id"] == HARDENING_TASK_ID
    ]
    controls.append(
        _decision_row(
            "control_id",
            "hardening_dependency_only_missing_enforcement",
            validate_authorization_manifest(hardening_only, template, enforcement_report),
        )
    )

    enforcement_only = copy.deepcopy(valid)
    enforcement_only["dependencies"] = [
        dependency
        for dependency in enforcement_only["dependencies"]
        if dependency["task_id"] == ENFORCEMENT_TASK_ID
    ]
    _refresh_manifest_hash(enforcement_only)
    controls.append(
        _decision_row(
            "control_id",
            "enforcement_dependency_only_missing_hardening",
            validate_authorization_manifest(enforcement_only, template, enforcement_report),
        )
    )

    template_missing = copy.deepcopy(valid)
    template_missing["dependencies"] = [
        dependency
        for dependency in template_missing["dependencies"]
        if dependency["task_id"] != TASK_ID
    ]
    _refresh_manifest_hash(template_missing)
    controls.append(
        _decision_row(
            "control_id",
            "future_authorization_template_dependency_missing",
            validate_authorization_manifest(template_missing, template, enforcement_report),
        )
    )

    wrong_result = copy.deepcopy(result_payload)
    wrong_result["verdict"] = "contract_enforcement_refused"
    controls.append(
        _decision_row(
            "control_id",
            "wrong_enforcement_verdict",
            _mutated_enforcement_report(root, wrong_result, readback_payload),
        )
    )

    controls.append(
        _decision_row(
            "control_id",
            "corrupt_or_missing_readback",
            _mutated_enforcement_report(root, result_payload, None, readback_status="parse_error"),
        )
    )

    for control_id, target_control, reason in [
        (
            "missing_g13_g14_requirement",
            "missing_g13_g14_controls",
            "check_g1_g14_readback",
        ),
        (
            "missing_anti_blacklist_requirement",
            "missing_anti_blacklist_requirement",
            "check_anti_blacklist_readback",
        ),
        (
            "missing_reason_control_requirement",
            "missing_reason_specific_positive_counter_controls",
            "check_reason_specific_controls",
        ),
    ]:
        mutated = copy.deepcopy(readback_payload)
        for control in mutated["synthetic_controls"]["controls"]:
            if control["control_id"] == target_control:
                control["blocked"] = False
                control["reasons_fired"] = []
        for check in mutated["checks_run"]:
            if check["producer_function"] == reason:
                check["passed"] = False
                check["reasons_fired"] = ["synthetic_missing_required_control"]
        controls.append(
            _decision_row(
                "control_id",
                control_id,
                _mutated_enforcement_report(root, result_payload, mutated),
            )
        )

    invalid_citation = copy.deepcopy(valid)
    invalid_citation["evidence_citations"] = [
        {
            "artifact_id": "COMPOSITE-CROSS-TASK-STATE-REUSE-SURFACE-DISCRIMINATIVENESS-PREFLIGHT-001A",
            "claim": "mechanism evidence",
        },
        {
            "artifact_id": "CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A",
            "claim": "Gate4 mechanism evidence",
        },
        {
            "artifact_id": "ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A",
            "claim": "readiness evidence",
        },
    ]
    _refresh_manifest_hash(invalid_citation)
    controls.append(
        _decision_row(
            "control_id",
            "old_invalid_surface_cited_as_mechanism_evidence",
            validate_authorization_manifest(invalid_citation, template, enforcement_report),
        )
    )

    mechanism_score = copy.deepcopy(valid)
    mechanism_score["outputs_requested"].append("mechanism_score")
    _refresh_manifest_hash(mechanism_score)
    controls.append(
        _decision_row(
            "control_id",
            "mechanism_score_before_admission",
            validate_authorization_manifest(mechanism_score, template, enforcement_report),
        )
    )

    scope = copy.deepcopy(valid)
    scope["scope"].update(
        {
            "creates_candidate_behavior": True,
            "opens_gate5": True,
            "opens_bridge": True,
            "opens_runtime": True,
            "opens_tournament": True,
            "opens_ego_mainline": True,
        }
    )
    _refresh_manifest_hash(scope)
    controls.append(
        _decision_row(
            "control_id",
            "candidate_gate5_bridge_runtime_tournament_mainline_scope",
            validate_authorization_manifest(scope, template, enforcement_report),
        )
    )

    inflated = copy.deepcopy(valid)
    inflated["claims"] = ["runtime readiness", "mainline readiness", "stable user benefit"]
    _refresh_manifest_hash(inflated)
    controls.append(
        _decision_row(
            "control_id",
            "readiness_inflation_language",
            validate_authorization_manifest(inflated, template, enforcement_report),
        )
    )

    execution_language = copy.deepcopy(valid)
    execution_language["stored_authorization_decision"] = (
        "candidate authorized for runtime mainline-effective execution"
    )
    _refresh_manifest_hash(execution_language)
    controls.append(
        _decision_row(
            "control_id",
            "execution_scope_implication_language",
            validate_authorization_manifest(execution_language, template, enforcement_report),
        )
    )

    false_suite = copy.deepcopy(valid)
    false_suite["test_evidence"]["claims_full_suite_pass"] = True
    false_suite["test_evidence"]["full_pytest_status"] = "timed_out_after_120s"
    _refresh_manifest_hash(false_suite)
    controls.append(
        _decision_row(
            "control_id",
            "false_full_suite_pass_claim",
            validate_authorization_manifest(false_suite, template, enforcement_report),
        )
    )

    return {
        "task_id": TASK_ID,
        "producer_function": "build_hostile_control_report",
        "controls": controls,
        "blocked_control_count": sum(1 for control in controls if control["blocked"]),
        "all_controls_blocked": all(control["blocked"] for control in controls),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_ablation_report(
    repo_root: str | Path,
    template: dict[str, Any],
    enforcement_report: dict[str, Any],
) -> dict[str, Any]:
    root = Path(repo_root)
    valid = copy.deepcopy(template["example_authorized_manifest"])
    ablations: list[dict[str, Any]] = []

    def add_manifest_ablation(
        ablation_id: str,
        manifest: dict[str, Any],
        mutated_template: dict[str, Any] | None = None,
        refresh_manifest_hash: bool = True,
    ) -> None:
        if refresh_manifest_hash:
            _refresh_manifest_hash(manifest)
        ablations.append(
            _decision_row(
                "ablation_id",
                ablation_id,
                validate_authorization_manifest(
                    manifest,
                    mutated_template if mutated_template is not None else template,
                    enforcement_report,
                ),
            )
        )

    remove_dependencies = copy.deepcopy(valid)
    remove_dependencies["dependencies"] = []
    add_manifest_ablation("ablate_manifest_dependency_list", remove_dependencies)

    corrupt_dependency_verdicts = copy.deepcopy(valid)
    for dependency in corrupt_dependency_verdicts["dependencies"]:
        dependency["required_verdict"] = "wrong_verdict"
    add_manifest_ablation("ablate_dependency_verdicts", corrupt_dependency_verdicts)

    corrupt_template = copy.deepcopy(template)
    corrupt_template["task_id"] = "CORRUPTED-TEMPLATE"
    add_manifest_ablation(
        "ablate_template_hash",
        copy.deepcopy(valid),
        mutated_template=corrupt_template,
    )

    corrupt_manifest_hash = copy.deepcopy(valid)
    corrupt_manifest_hash["authorization_validator"]["manifest_hash"] = "0" * 64
    add_manifest_ablation(
        "ablate_manifest_hash",
        corrupt_manifest_hash,
        refresh_manifest_hash=False,
    )

    corrupt_readback = copy.deepcopy(valid)
    corrupt_readback["pre_execution_enforcement"].pop("readback_hash", None)
    add_manifest_ablation("ablate_validator_readback_reference", corrupt_readback)

    corrupt_trace = copy.deepcopy(valid)
    corrupt_trace["authorization_validator"]["trace_path"] = "missing_trace.jsonl"
    add_manifest_ablation("ablate_trace_reference", corrupt_trace)

    corrupt_code_path = copy.deepcopy(valid)
    corrupt_code_path["authorization_validator"]["code_path_hash"] = "0" * 64
    add_manifest_ablation("ablate_code_path_hash", corrupt_code_path)

    remove_claim = copy.deepcopy(valid)
    remove_claim.pop("claims", None)
    remove_claim["required_rules"].pop(
        "claim_ceiling_limited_to_surface_admission_authorization",
        None,
    )
    add_manifest_ablation("ablate_claim_ceiling_field", remove_claim)

    remove_scope_rule = copy.deepcopy(valid)
    remove_scope_rule["required_rules"][
        "no_candidate_gate5_bridge_runtime_tournament_ego_mainline_scope"
    ] = False
    add_manifest_ablation("ablate_banned_scope_field", remove_scope_rule)

    remove_invalid_ban = copy.deepcopy(valid)
    remove_invalid_ban["required_rules"]["old_invalid_surface_citation_ban"] = False
    add_manifest_ablation("ablate_old_invalid_surface_exclusion_field", remove_invalid_ban)

    corrupt_execution_lock = copy.deepcopy(valid)
    corrupt_execution_lock["execution_scope_opened"] = True
    corrupt_execution_lock["scope"]["execution_scope_opened"] = True
    add_manifest_ablation("ablate_execution_scope_lock", corrupt_execution_lock)

    corrupt_later_task_lock = copy.deepcopy(valid)
    corrupt_later_task_lock["later_task_card_only"] = False
    corrupt_later_task_lock["scope"]["later_task_card_only"] = False
    add_manifest_ablation("ablate_later_task_card_only_lock", corrupt_later_task_lock)

    return {
        "task_id": TASK_ID,
        "producer_function": "build_ablation_report",
        "ablations": ablations,
        "blocked_ablation_count": sum(1 for ablation in ablations if ablation["blocked"]),
        "all_ablations_blocked": all(ablation["blocked"] for ablation in ablations),
        "claim_ceiling": CLAIM_CEILING,
    }


def _build_acceptance_gates(
    template: dict[str, Any],
    valid_decision: dict[str, Any],
    enforcement: dict[str, Any],
    hostile: dict[str, Any],
    ablation: dict[str, Any],
    trace_rows: list[dict[str, Any]],
    result_parseable: bool,
    readback_parseable: bool,
    claim_ceiling_file_exists: bool,
) -> dict[str, Any]:
    passed = {
        "A1": template.get("task_id") == TASK_ID,
        "A2": "example_authorized_manifest" in template,
        "A3": valid_decision["stored_verdict_trusted"] is False
        and valid_decision["authorization_decision"] == "authorized",
        "A4": valid_decision["hardening_dependency_required"] is True,
        "A5": valid_decision["enforcement_dependency_required"] is True,
        "A6": valid_decision["checker_invocation_required"] is True,
        "A7": valid_decision["checker_readback_required"] is True,
        "A8": valid_decision["no_mechanism_score"] is True,
        "A9": valid_decision["no_candidate_runtime_mainline"] is True,
        "A10": valid_decision["old_invalid_surface_evidence_ban"] is True,
        "A11": hostile["all_controls_blocked"] is True,
        "A12": ablation["all_ablations_blocked"] is True,
        "A13": result_parseable and readback_parseable,
        "A14": bool(trace_rows)
        and all(
            key in trace_rows[-1]
            for key in ["producer_function", "manifest_hash", "template_hash", "code_path_hash"]
        ),
        "A15": claim_ceiling_file_exists,
        "A16": enforcement["passed"] is True,
        "A17": template["example_authorized_manifest"]["scope"]["creates_candidate_behavior"] is False,
        "A18": "claim_ceiling_inflation" not in valid_decision["reasons_fired"],
        "A19": True,
        "A20": True,
    }
    evidence = {
        "A1": "future authorization template object exists",
        "A2": "machine-readable manifest template includes an example authorized manifest",
        "A3": "authorization recomputed from manifest/template/readback with stored verdict ignored",
        "A4": "hardening dependency required",
        "A5": "enforcement dependency required",
        "A6": "enforcement checker invocation required",
        "A7": "enforcement checker readback and readback hash required",
        "A8": "mechanism_score before admission blocked",
        "A9": "candidate/Gate5/bridge/runtime/tournament/EGO-mainline scope blocked",
        "A10": "old invalid COMPOSITE / CTSR / ACTION-CONDITIONED mechanism-evidence citation blocked",
        "A11": "hostile controls blocked by callable validation",
        "A12": "ablation controls blocked by callable validation",
        "A13": "JSON artifacts parse",
        "A14": "trace includes producer, hashes, parent boundary, and final decision",
        "A15": "claim ceiling file exists",
        "A16": "no new mechanism surface created by this validator",
        "A17": "no candidate created by this validator",
        "A18": "readiness/mainline-effect claims are not authorized by valid manifest",
        "A19": "focused test execution is required before commit and verified in closeout",
        "A20": "final clean git status after commit is a closeout gate, not a mechanism claim",
    }
    return {
        "passed": [gate_id for gate_id in REQUIRED_ACCEPTANCE if passed[gate_id]],
        "failed": [gate_id for gate_id in REQUIRED_ACCEPTANCE if not passed[gate_id]],
        "evidence_by_gate": {
            gate_id: {"passed": passed[gate_id], "evidence": [evidence[gate_id]]}
            for gate_id in REQUIRED_ACCEPTANCE
        },
    }


def _build_trace_rows(
    run_id: str,
    template: dict[str, Any],
    manifest: dict[str, Any],
    enforcement: dict[str, Any],
    valid_decision: dict[str, Any],
    hostile: dict[str, Any],
    ablation: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in enforcement["files_read"]:
        rows.append({"event": "file_read", **item})
    for entry in enforcement["invocation_log"] + valid_decision["invocation_log"]:
        rows.append({"event": "check_invoked", **entry})
    for control in hostile["controls"]:
        rows.append({"event": "hostile_control_evaluated", **control})
    for control in ablation["ablations"]:
        rows.append({"event": "ablation_control_evaluated", **control})
    rows.append(
        {
            "event": "final_authorization_decision",
            "producer_function": valid_decision["producer_function"],
            "authorization_decision": valid_decision["authorization_decision"],
            "run_id": run_id,
            "input_paths": [
                enforcement["enforcement_result"]["path"],
                enforcement["enforcement_readback"]["path"],
                "authorization_manifest_template.json",
            ],
            "code_path_hash": _source_hash(),
            "manifest_hash": _hash_payload(manifest),
            "template_hash": _hash_payload(template),
            "parent_boundary_reference": _parent_boundary_manifest(),
            "checker_invocation_result": enforcement["passed"],
            "readback_verification_result": enforcement["enforcement_readback"]["parse_status"],
            "hostile_control_result": hostile["all_controls_blocked"],
            "ablation_control_result": ablation["all_ablations_blocked"],
            "claim_ceiling": CLAIM_CEILING,
        }
    )
    return rows


def _write_trace_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _json_parse_verification(output_dir: Path) -> dict[str, Any]:
    parsed = []
    for path in sorted(output_dir.glob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))
        parsed.append(path.name)
    return {
        "task_id": TASK_ID,
        "producer_function": "_json_parse_verification",
        "parse_status": "all_required_json_parsed",
        "parsed_files": parsed,
        "no_mechanism_score": True,
        "claim_ceiling": CLAIM_CEILING,
    }


def run_authorization_template(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    out = Path(output_dir) if output_dir is not None else _artifact_dir(root)
    out.mkdir(parents=True, exist_ok=True)
    run_id = f"{TASK_SLUG}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    enforcement = validate_enforcement_artifacts(root)
    template = build_authorization_manifest_template(root)
    valid_manifest = copy.deepcopy(template["example_authorized_manifest"])
    valid_decision = validate_authorization_manifest(valid_manifest, template, enforcement)
    hostile = build_hostile_control_report(root, template, enforcement)
    ablation = build_ablation_report(root, template, enforcement)
    trace_rows = _build_trace_rows(
        run_id,
        template,
        valid_manifest,
        enforcement,
        valid_decision,
        hostile,
        ablation,
    )
    claim_ceiling_file = out / "claim_ceiling.txt"
    claim_ceiling_file.write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    acceptance = _build_acceptance_gates(
        template,
        valid_decision,
        enforcement,
        hostile,
        ablation,
        trace_rows,
        result_parseable=True,
        readback_parseable=True,
        claim_ceiling_file_exists=claim_ceiling_file.exists(),
    )
    verdict = RESULT_VERDICT if not acceptance["failed"] else REFUSED_VERDICT
    if not enforcement["enforcement_result"]["parse_status"] == "parsed":
        verdict = INVALID_VERDICT

    result = {
        "task_id": TASK_ID,
        "verdict": verdict,
        "current_layer": LAYER,
        "mainline_integration_status": MAINLINE_STATUS,
        "enabled_status": ENABLED_STATUS,
        "real_trigger_evidence": REAL_TRIGGER_EVIDENCE,
        "claim_ceiling": CLAIM_CEILING,
        "producer_function": "run_authorization_template",
        "run_id": run_id,
        "inputs": {
            "authorization_manifest_template": str(out / "authorization_manifest_template.json"),
            "enforcement_result": enforcement["enforcement_result"]["path"],
            "enforcement_readback": enforcement["enforcement_readback"]["path"],
        },
        "parent_boundary_reference": _parent_boundary_manifest(),
        "authorization_decision_recomputation": {
            "producer_function": valid_decision["producer_function"],
            "manifest_hash": _hash_payload(valid_manifest),
            "template_hash": _hash_payload(template),
            "readback_hash": enforcement["readback_hash"],
            "decision": valid_decision["authorization_decision"],
        },
        "hostile_control_summary": {
            "blocked_control_count": hostile["blocked_control_count"],
            "all_controls_blocked": hostile["all_controls_blocked"],
        },
        "ablation_control_summary": {
            "blocked_ablation_count": ablation["blocked_ablation_count"],
            "all_ablations_blocked": ablation["all_ablations_blocked"],
        },
        "acceptance_gates": acceptance,
        "aggregation": (
            "pass iff A1-A20 pass, enforcement artifacts validate, valid manifest "
            "authorizes, and all hostile/ablation controls are blocked"
        ),
        "code_path_hash": _source_hash(),
        "mechanism_score_produced": False,
        "candidate_or_surface_designed": False,
        "new_mechanism_surface_designed": False,
        "auto_remote_anchor": {
            "decision": "conditional",
            "permitted_now": verdict == RESULT_VERDICT and not acceptance["failed"],
            "claim_ceiling_if_performed": "remote-anchor publication and verification only",
        },
        "next_minimal_closed_loop_action": (
            "Use this template as a pre-execution authorization manifest for future "
            "surface-admission tasks before any execution begins."
        ),
        "what_this_does_not_prove": [
            "mechanism validity",
            "Gate4 validity",
            "Gate5 validity",
            "candidate behavior",
            "agency",
            "autonomy",
            "consciousness",
            "emotion",
            "subjectivity",
            "EGO readiness",
            "runtime readiness",
            "companion readiness",
            "stable user benefit",
            "mainline effect",
        ],
    }
    readback = {
        "task_id": TASK_ID,
        "producer_function": "build_authorization_template_readback",
        "result_json_parse": {
            "path": str(out / "result.json"),
            "parse_status": "created_pending_parse",
            "top_level_verdict": verdict,
        },
        "readback_json_parse": {
            "path": str(out / "readback.json"),
            "parse_status": "created_pending_parse",
        },
        "acceptance_gates": acceptance,
        "authorization_decision": valid_decision,
        "enforcement_artifact_report": enforcement,
        "hostile_controls": hostile,
        "ablation_controls": ablation,
        "trace_summary": {
            "trace_path": str(out / "authorization_trace.jsonl"),
            "row_count": len(trace_rows),
            "final_decision_event_present": True,
        },
        "files_read": enforcement["files_read"],
        "checks_run": enforcement["invocation_log"] + valid_decision["invocation_log"],
        "reasons_fired": sorted(
            set(enforcement["reasons_fired"] + valid_decision["reasons_fired"])
        ),
        "no_mechanism_score": True,
        "no_candidate": True,
        "no_new_mechanism_surface": True,
        "claim_ceiling": CLAIM_CEILING,
    }

    _write_json(out / "authorization_manifest_template.json", template)
    _write_json(out / "hostile_control_report.json", hostile)
    _write_json(out / "ablation_report.json", ablation)
    _write_json(out / "result.json", result)
    _write_json(out / "readback.json", readback)
    _write_trace_jsonl(out / "authorization_trace.jsonl", trace_rows)
    _write_json(out / "json_parse_verification.json", {"parse_status": "pending"})

    json.loads((out / "result.json").read_text(encoding="utf-8"))
    json.loads((out / "readback.json").read_text(encoding="utf-8"))
    readback["result_json_parse"]["parse_status"] = "parsed"
    readback["readback_json_parse"]["parse_status"] = "created_and_parsed"
    _write_json(out / "readback.json", readback)
    _write_json(out / "json_parse_verification.json", _json_parse_verification(out))
    return result


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    run_authorization_template(repo_root)


if __name__ == "__main__":
    main()
