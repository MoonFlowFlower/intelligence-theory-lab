from __future__ import annotations

import hashlib
import inspect
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A"
TASK_SLUG = "surface_admission_contract_enforcement_001a"
HARDENING_TASK_ID = "SURFACE-ADMISSION-CONTRACT-HARDENING-001A"
HARDENING_SLUG = "surface_admission_contract_hardening_001a"
HARDENING_TAG = (
    "remote-anchor-surface-admission-contract-hardening-001a-"
    "verdict-enum-reconciliation-001a-915d4c5"
)
HARDENING_VERDICT = "contract_hardened_pass"
LAYER = "engineering-governance / contract enforcement / no mechanism surface"
MAINLINE_STATUS = "none; offline local checker and artifact contract only"
ENABLED_STATUS = "local checker / artifact contract only"
REAL_TRIGGER_EVIDENCE = "read-only hardening artifact/readback plus synthetic future-manifest bypass controls"
CLAIM_CEILING = "engineering-governance / task-authorization hygiene only"
ALLOWED_VERDICTS = {
    "contract_enforcement_pass",
    "contract_enforcement_refused",
    "invalid_enforcement_harness",
}
REQUIRED_GATES = [f"G{index}" for index in range(1, 15)]
REQUIRED_ACCEPTANCE = [f"E{index}" for index in range(1, 19)]
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
    "stable user benefit",
)


def _default_result_path(repo_root: Path) -> Path:
    return repo_root / "artifacts" / HARDENING_SLUG / "result.json"


def _default_readback_path(repo_root: Path) -> Path:
    return repo_root / "artifacts" / HARDENING_SLUG / "readback.json"


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


def _source_hash() -> str:
    functions = [
        validate_hardening_artifacts,
        validate_future_manifest,
        build_synthetic_control_report,
        run_enforcement,
    ]
    source = "\n".join(inspect.getsource(function) for function in functions)
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


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


def _evaluate_hardening_payloads(
    repo_root: Path,
    result_payload: dict[str, Any] | None,
    readback_payload: dict[str, Any] | None,
    result_parse: dict[str, Any],
    readback_parse: dict[str, Any],
    files_read: list[dict[str, Any]],
) -> dict[str, Any]:
    reasons: list[str] = []
    invocation_log: list[dict[str, Any]] = []

    result_parsed = result_parse.get("parse_status") == "parsed" and isinstance(result_payload, dict)
    readback_parsed = readback_parse.get("parse_status") == "parsed" and isinstance(readback_payload, dict)
    if not result_parsed:
        reasons.append("hardening_result_parse_failed")
    if not readback_parsed:
        reasons.append("hardening_readback_parse_failed")

    result_verdict = result_payload.get("verdict") if result_parsed else None
    verdict_ok = result_verdict == HARDENING_VERDICT
    if result_parsed and not verdict_ok:
        reasons.append("hardening_verdict_not_contract_hardened_pass")
    _append_invocation(
        invocation_log,
        "check_hardening_verdict",
        verdict_ok,
        [] if verdict_ok else ["hardening_verdict_not_contract_hardened_pass"],
        [result_parse["path"]],
    )

    gates = readback_payload.get("gates", {}) if readback_parsed else {}
    present_passed = [
        gate_id
        for gate_id in REQUIRED_GATES
        if isinstance(gates.get(gate_id), dict) and gates[gate_id].get("passed") is True
    ]
    missing_or_failed = [gate_id for gate_id in REQUIRED_GATES if gate_id not in present_passed]
    gates_ok = readback_parsed and not missing_or_failed
    if readback_parsed and not gates_ok:
        reasons.append("missing_or_failed_g1_g14_readback")
    _append_invocation(
        invocation_log,
        "check_g1_g14_readback",
        gates_ok,
        [] if gates_ok else ["missing_or_failed_g1_g14_readback"],
        [readback_parse["path"]],
    )

    anti = readback_payload.get("anti_blacklist", {}) if readback_parsed else {}
    anti_ok = (
        readback_parsed
        and isinstance(anti, dict)
        and anti.get("passed") is True
        and anti.get("static_task_id_denylist_used") is False
    )
    if readback_parsed and not anti_ok:
        reasons.append("anti_blacklist_readback_missing_or_failed")
    _append_invocation(
        invocation_log,
        "check_anti_blacklist_readback",
        anti_ok,
        [] if anti_ok else ["anti_blacklist_readback_missing_or_failed"],
        [readback_parse["path"]],
    )

    reason_controls = readback_payload.get("reason_specific_controls", {}) if readback_parsed else {}
    reason_ok = (
        readback_parsed
        and isinstance(reason_controls, dict)
        and reason_controls.get("passed") is True
        and reason_controls.get("positive_control_count", 0) >= 9
        and reason_controls.get("counter_control_count", 0) >= 9
    )
    if readback_parsed and not reason_ok:
        reasons.append("reason_specific_controls_missing_or_failed")
    _append_invocation(
        invocation_log,
        "check_reason_specific_controls",
        reason_ok,
        [] if reason_ok else ["reason_specific_controls_missing_or_failed"],
        [readback_parse["path"]],
    )

    scope = readback_payload.get("scope_guards", {}) if readback_parsed else {}
    scope_ok = (
        readback_parsed
        and readback_payload.get("no_mechanism_score") is True
        and readback_payload.get("no_candidate") is True
        and readback_payload.get("no_new_mechanism_surface") is True
        and isinstance(scope, dict)
        and scope.get("no_mechanism_score") is True
        and scope.get("no_candidate") is True
        and scope.get("no_new_mechanism_surface") is True
        and scope.get("old_preserved_artifacts_unchanged") is True
    )
    if readback_parsed and not scope_ok:
        reasons.append("mechanism_surface_candidate_or_score_present")
    _append_invocation(
        invocation_log,
        "check_no_mechanism_surface",
        scope_ok,
        [] if scope_ok else ["mechanism_surface_candidate_or_score_present"],
        [readback_parse["path"]],
    )

    local_tag_hash = _run_git(repo_root, ["rev-parse", f"{HARDENING_TAG}^{{commit}}"])
    current_head = _run_git(repo_root, ["rev-parse", "HEAD"])
    return {
        "task_id": TASK_ID,
        "producer_function": "validate_hardening_artifacts",
        "hardening_result": {
            "path": result_parse["path"],
            "parse_status": result_parse["parse_status"],
            "verdict": result_verdict,
            "task_id": result_payload.get("task_id") if result_parsed else None,
        },
        "hardening_readback": {
            "path": readback_parse["path"],
            "parse_status": readback_parse["parse_status"],
            "task_id": readback_payload.get("task_id") if readback_parsed else None,
        },
        "gate_readback": {
            "present_passed_gates": present_passed,
            "missing_or_failed_gates": missing_or_failed,
        },
        "anti_blacklist": {
            "passed": anti_ok,
            "producer_function": anti.get("producer_function") if isinstance(anti, dict) else None,
        },
        "reason_specific_controls": {
            "passed": reason_ok,
            "producer_function": (
                reason_controls.get("producer_function") if isinstance(reason_controls, dict) else None
            ),
            "positive_control_count": (
                reason_controls.get("positive_control_count") if isinstance(reason_controls, dict) else None
            ),
            "counter_control_count": (
                reason_controls.get("counter_control_count") if isinstance(reason_controls, dict) else None
            ),
        },
        "scope_guards": {
            "no_mechanism_score": scope_ok and readback_payload.get("no_mechanism_score") is True,
            "no_candidate": scope_ok and readback_payload.get("no_candidate") is True,
            "no_new_mechanism_surface": scope_ok and readback_payload.get("no_new_mechanism_surface") is True,
            "old_preserved_artifacts_unchanged": bool(scope.get("old_preserved_artifacts_unchanged")) if isinstance(scope, dict) else False,
        },
        "referenced_anchor": {
            "tag": HARDENING_TAG,
            "local_tag_hash": local_tag_hash,
            "current_head": current_head,
            "exact_local_head_tag_match": bool(local_tag_hash and current_head and local_tag_hash == current_head),
        },
        "files_read": files_read,
        "invocation_log": [
            {
                "producer_function": result_parse["producer_function"],
                "passed": result_parsed,
                "reasons_fired": [] if result_parsed else ["hardening_result_parse_failed"],
                "inputs": [result_parse["path"]],
            },
            {
                "producer_function": readback_parse["producer_function"],
                "passed": readback_parsed,
                "reasons_fired": [] if readback_parsed else ["hardening_readback_parse_failed"],
                "inputs": [readback_parse["path"]],
            },
            *invocation_log,
        ],
        "reasons_fired": sorted(set(reasons)),
        "passed": not reasons,
        "claim_ceiling": CLAIM_CEILING,
    }


def validate_hardening_artifacts(
    repo_root: str | Path,
    result_path: str | Path | None = None,
    readback_path: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    result = Path(result_path) if result_path is not None else _default_result_path(root)
    readback = Path(readback_path) if readback_path is not None else _default_readback_path(root)
    result_payload, result_parse = _parse_json_file(result, "parse_hardening_result")
    readback_payload, readback_parse = _parse_json_file(readback, "parse_hardening_readback")
    files_read = [
        {
            "path": result_parse["path"],
            "exists": result_parse["exists"],
            "parse_status": result_parse["parse_status"],
        },
        {
            "path": readback_parse["path"],
            "exists": readback_parse["exists"],
            "parse_status": readback_parse["parse_status"],
        },
    ]
    return _evaluate_hardening_payloads(
        root,
        result_payload if isinstance(result_payload, dict) else None,
        readback_payload if isinstance(readback_payload, dict) else None,
        result_parse,
        readback_parse,
        files_read,
    )


def build_valid_future_manifest(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    return {
        "task_id": "SURFACE-ADMISSION-FUTURE-AUTHORIZATION-CONTROL",
        "current_layer": LAYER,
        "hardened_contract_dependency": {
            "task_id": HARDENING_TASK_ID,
            "artifact_id": HARDENING_SLUG,
            "result_path": str(_default_result_path(root).relative_to(root)).replace("\\", "/"),
            "readback_path": str(_default_readback_path(root).relative_to(root)).replace("\\", "/"),
            "required_verdict": HARDENING_VERDICT,
            "required_gates": REQUIRED_GATES,
            "required_tag": HARDENING_TAG,
        },
        "pre_execution_requirements": [
            {
                "requirement": "run_or_cite_hardened_validator_readback",
                "validator_module": "surface_admission_contract_hardening_001a.validator",
                "readback_path": str(_default_readback_path(root).relative_to(root)).replace("\\", "/"),
            }
        ],
        "scope": {
            "surface_admission_authorization_only": True,
            "creates_new_surface": False,
            "creates_new_mechanism_surface": False,
            "creates_candidate_behavior": False,
            "opens_gate5": False,
            "opens_bridge": False,
            "opens_runtime": False,
            "opens_tournament": False,
            "opens_ego_mainline": False,
            "produces_mechanism_score": False,
        },
        "outputs_requested": [
            "authorization_decision",
            "result.json",
            "readback.json",
        ],
        "test_evidence": {
            "focused_tests_passed": True,
            "full_pytest_status": "timed_out_after_120s",
            "claims_full_suite_pass": False,
        },
        "evidence_citations": [
            {
                "artifact_id": HARDENING_TASK_ID,
                "claim": "artifact-backed contract dependency only",
            }
        ],
        "claims": [CLAIM_CEILING],
    }


def _json_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True).lower()


def _walk_json(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    rows = [(path, value)]
    if isinstance(value, dict):
        for key, item in value.items():
            rows.extend(_walk_json(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(_walk_json(item, f"{path}[{index}]"))
    return rows


def _has_validator_readback_precondition(manifest: dict[str, Any]) -> bool:
    requirements = manifest.get("pre_execution_requirements")
    if not isinstance(requirements, list):
        return False
    for requirement in requirements:
        if isinstance(requirement, dict):
            req_name = str(requirement.get("requirement", "")).lower()
            readback_path = str(requirement.get("readback_path", "")).lower()
            if "hardened" in req_name and "readback" in req_name and readback_path.endswith("readback.json"):
                return True
        elif isinstance(requirement, str):
            text = requirement.lower()
            if "hardened" in text and "validator" in text and "readback" in text:
                return True
    return False


def _check_hardened_contract_dependency(manifest: dict[str, Any]) -> list[str]:
    dependency = manifest.get("hardened_contract_dependency")
    if not isinstance(dependency, dict):
        return ["missing_hardened_contract_dependency"]
    required_gates = dependency.get("required_gates", [])
    if (
        dependency.get("task_id") != HARDENING_TASK_ID
        or dependency.get("artifact_id") != HARDENING_SLUG
        or dependency.get("required_verdict") != HARDENING_VERDICT
        or not dependency.get("result_path")
        or not dependency.get("readback_path")
        or not set(REQUIRED_GATES).issubset(set(required_gates))
    ):
        return ["missing_hardened_contract_dependency"]
    return []


def _check_no_mechanism_score_request(manifest: dict[str, Any]) -> list[str]:
    for json_path, value in _walk_json(manifest):
        leaf = json_path.rsplit(".", 1)[-1].lower()
        if "mechanism_score" in leaf and value not in (False, None):
            return ["mechanism_score_requested_or_produced"]
        if isinstance(value, str) and value.lower() == "mechanism_score":
            return ["mechanism_score_requested_or_produced"]
    return []


def _check_no_candidate_runtime_mainline(manifest: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    scope = manifest.get("scope", {})
    if not isinstance(scope, dict):
        return ["candidate_behavior_requested"]
    if scope.get("creates_candidate_behavior") is True:
        reasons.append("candidate_behavior_requested")
    if any(
        scope.get(key) is True
        for key in [
            "opens_gate5",
            "opens_bridge",
            "opens_runtime",
            "opens_tournament",
            "opens_ego_mainline",
        ]
    ):
        reasons.append("gate5_bridge_runtime_or_mainline_requested")
    if scope.get("creates_new_mechanism_surface") is True:
        reasons.append("new_mechanism_surface_requested")
    return reasons


def _check_false_full_suite_claim(manifest: dict[str, Any]) -> list[str]:
    evidence = manifest.get("test_evidence", {})
    if not isinstance(evidence, dict):
        return []
    status = str(evidence.get("full_pytest_status", "")).lower()
    if evidence.get("claims_full_suite_pass") is True and status not in {"passed", "full_suite_passed"}:
        return ["false_full_suite_pass_claim"]
    return []


def _check_preserved_invalid_surface_citations(manifest: dict[str, Any]) -> list[str]:
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
    text = _json_text(manifest.get("claims", []))
    if any(marker in text for marker in CLAIM_INFLATION_MARKERS):
        return ["claim_ceiling_inflation"]
    return []


def validate_future_manifest(
    manifest: dict[str, Any],
    hardening_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reasons: list[str] = []
    invocation_log: list[dict[str, Any]] = []

    if hardening_report is not None and hardening_report.get("passed") is not True:
        reasons.append("hardening_artifacts_not_valid")

    dependency_reasons = _check_hardened_contract_dependency(manifest)
    reasons.extend(dependency_reasons)
    _append_invocation(
        invocation_log,
        "check_hardened_contract_dependency",
        not dependency_reasons,
        dependency_reasons,
    )

    precondition_reasons = []
    if not _has_validator_readback_precondition(manifest):
        precondition_reasons.append("missing_hardened_validator_or_readback_precondition")
    reasons.extend(precondition_reasons)
    _append_invocation(
        invocation_log,
        "check_validator_readback_precondition",
        not precondition_reasons,
        precondition_reasons,
    )

    full_suite_reasons = _check_false_full_suite_claim(manifest)
    reasons.extend(full_suite_reasons)
    _append_invocation(
        invocation_log,
        "check_false_full_suite_claim",
        not full_suite_reasons,
        full_suite_reasons,
    )

    score_reasons = _check_no_mechanism_score_request(manifest)
    reasons.extend(score_reasons)
    _append_invocation(
        invocation_log,
        "check_no_mechanism_score_request",
        not score_reasons,
        score_reasons,
    )

    scope_reasons = _check_no_candidate_runtime_mainline(manifest)
    reasons.extend(scope_reasons)
    _append_invocation(
        invocation_log,
        "check_no_candidate_runtime_mainline",
        not scope_reasons,
        scope_reasons,
    )

    citation_reasons = _check_preserved_invalid_surface_citations(manifest)
    reasons.extend(citation_reasons)
    _append_invocation(
        invocation_log,
        "check_preserved_invalid_surface_citations",
        not citation_reasons,
        citation_reasons,
    )

    claim_reasons = _check_claim_ceiling(manifest)
    reasons.extend(claim_reasons)
    _append_invocation(
        invocation_log,
        "check_claim_ceiling",
        not claim_reasons,
        claim_reasons,
    )

    scope = manifest.get("scope", {}) if isinstance(manifest.get("scope"), dict) else {}
    return {
        "task_id": TASK_ID,
        "manifest_task_id": manifest.get("task_id"),
        "authorization_decision": "blocked" if reasons else "authorized",
        "reasons_fired": sorted(set(reasons)),
        "no_candidate": not bool(scope.get("creates_candidate_behavior")),
        "no_runtime": not bool(scope.get("opens_runtime")),
        "no_mainline": not bool(scope.get("opens_ego_mainline")),
        "no_mechanism_score": "mechanism_score_requested_or_produced" not in reasons,
        "invocation_log": invocation_log,
        "producer_function": "validate_future_manifest",
        "claim_ceiling": CLAIM_CEILING,
    }


def _mutated_hardening_report(
    repo_root: Path,
    result_payload: dict[str, Any] | None,
    readback_payload: dict[str, Any] | None,
    result_status: str = "parsed",
    readback_status: str = "parsed",
) -> dict[str, Any]:
    result_parse = {
        "producer_function": "parse_hardening_result",
        "path": "synthetic/hardening_result.json",
        "exists": result_payload is not None,
        "parse_status": result_status,
    }
    readback_parse = {
        "producer_function": "parse_hardening_readback",
        "path": "synthetic/hardening_readback.json",
        "exists": readback_payload is not None,
        "parse_status": readback_status,
    }
    return _evaluate_hardening_payloads(
        repo_root,
        result_payload,
        readback_payload,
        result_parse,
        readback_parse,
        [
            {"path": result_parse["path"], "exists": result_parse["exists"], "parse_status": result_parse["parse_status"]},
            {"path": readback_parse["path"], "exists": readback_parse["exists"], "parse_status": readback_parse["parse_status"]},
        ],
    )


def _control_row(control_id: str, decision_or_report: dict[str, Any]) -> dict[str, Any]:
    if "authorization_decision" in decision_or_report:
        reasons = decision_or_report.get("reasons_fired", [])
        blocked = decision_or_report.get("authorization_decision") == "blocked"
    else:
        reasons = decision_or_report.get("reasons_fired", [])
        blocked = decision_or_report.get("passed") is False
    return {
        "control_id": control_id,
        "blocked": blocked,
        "reasons_fired": reasons,
        "producer_function": decision_or_report.get("producer_function"),
    }


def build_synthetic_control_report(
    repo_root: str | Path,
    hardening_report: dict[str, Any],
) -> dict[str, Any]:
    root = Path(repo_root)
    valid = build_valid_future_manifest(root)
    hardening_result = _load_json(_default_result_path(root))
    hardening_readback = _load_json(_default_readback_path(root))
    controls: list[dict[str, Any]] = []

    controls.append(
        _control_row(
            "superficial_contract_mention_only",
            validate_future_manifest(
                {
                    "task_id": "SURFACE-ADMISSION-FUTURE-SUPERFICIAL",
                    "summary": f"Mentions {HARDENING_TASK_ID} but has no structured dependency.",
                },
                hardening_report,
            ),
        )
    )

    wrong_verdict = dict(hardening_result)
    wrong_verdict["verdict"] = "contract_refused"
    controls.append(
        _control_row(
            "wrong_top_level_verdict_enum",
            _mutated_hardening_report(root, wrong_verdict, hardening_readback),
        )
    )

    controls.append(
        _control_row(
            "missing_or_corrupt_readback",
            _mutated_hardening_report(root, hardening_result, None, readback_status="parse_error"),
        )
    )

    missing_gates = json.loads(json.dumps(hardening_readback))
    missing_gates.get("gates", {}).pop("G13", None)
    missing_gates.get("gates", {}).pop("G14", None)
    controls.append(
        _control_row(
            "missing_g13_g14_controls",
            _mutated_hardening_report(root, hardening_result, missing_gates),
        )
    )

    missing_anti = json.loads(json.dumps(hardening_readback))
    missing_anti.pop("anti_blacklist", None)
    controls.append(
        _control_row(
            "missing_anti_blacklist_requirement",
            _mutated_hardening_report(root, hardening_result, missing_anti),
        )
    )

    missing_reason = json.loads(json.dumps(hardening_readback))
    missing_reason.pop("reason_specific_controls", None)
    controls.append(
        _control_row(
            "missing_reason_specific_positive_counter_controls",
            _mutated_hardening_report(root, hardening_result, missing_reason),
        )
    )

    no_precondition = json.loads(json.dumps(valid))
    no_precondition["pre_execution_requirements"] = []
    no_precondition["scope"]["creates_new_surface"] = True
    controls.append(
        _control_row(
            "new_surface_without_hardened_validator_precondition",
            validate_future_manifest(no_precondition, hardening_report),
        )
    )

    candidate_runtime = json.loads(json.dumps(valid))
    candidate_runtime["scope"]["creates_candidate_behavior"] = True
    candidate_runtime["scope"]["opens_gate5"] = True
    candidate_runtime["scope"]["opens_bridge"] = True
    candidate_runtime["scope"]["opens_runtime"] = True
    candidate_runtime["scope"]["opens_ego_mainline"] = True
    controls.append(
        _control_row(
            "candidate_gate5_bridge_runtime_mainline_language",
            validate_future_manifest(candidate_runtime, hardening_report),
        )
    )

    mechanism_score = json.loads(json.dumps(valid))
    mechanism_score["outputs_requested"].append("mechanism_score")
    controls.append(
        _control_row(
            "mechanism_score_requested",
            validate_future_manifest(mechanism_score, hardening_report),
        )
    )

    false_suite = json.loads(json.dumps(valid))
    false_suite["test_evidence"]["claims_full_suite_pass"] = True
    controls.append(
        _control_row(
            "false_full_suite_pass_after_timeout",
            validate_future_manifest(false_suite, hardening_report),
        )
    )

    invalid_citation = json.loads(json.dumps(valid))
    invalid_citation["evidence_citations"] = [
        {
            "artifact_id": "COMPOSITE-CROSS-TASK-STATE-REUSE-SURFACE-DISCRIMINATIVENESS-PREFLIGHT-001A",
            "claim": "mechanism evidence",
        }
    ]
    controls.append(
        _control_row(
            "old_invalid_surface_cited_as_mechanism_evidence",
            validate_future_manifest(invalid_citation, hardening_report),
        )
    )

    inflated = json.loads(json.dumps(valid))
    inflated["claims"] = ["Gate4 validity", "Gate5 validity", "mechanism validity", "mainline readiness"]
    controls.append(
        _control_row(
            "hardening_result_treated_as_gate_or_readiness",
            validate_future_manifest(inflated, hardening_report),
        )
    )

    return {
        "task_id": TASK_ID,
        "producer_function": "build_synthetic_control_report",
        "controls": controls,
        "blocked_control_count": sum(1 for control in controls if control["blocked"]),
        "all_controls_blocked": all(control["blocked"] for control in controls),
        "claim_ceiling": CLAIM_CEILING,
    }


def _build_acceptance_gates(
    hardening: dict[str, Any],
    valid_decision: dict[str, Any],
    synthetic: dict[str, Any],
    result_parseable: bool,
    readback_parseable: bool,
) -> dict[str, Any]:
    controls_by_id = {control["control_id"]: control for control in synthetic["controls"]}
    passed = {
        "E1": hardening["hardening_result"]["parse_status"] == "parsed",
        "E2": hardening["hardening_readback"]["parse_status"] == "parsed",
        "E3": hardening["hardening_result"]["verdict"] == HARDENING_VERDICT,
        "E4": not hardening["gate_readback"]["missing_or_failed_gates"],
        "E5": hardening["anti_blacklist"]["passed"] is True,
        "E6": hardening["reason_specific_controls"]["passed"] is True,
        "E7": controls_by_id["superficial_contract_mention_only"]["blocked"] is True,
        "E8": controls_by_id["missing_or_corrupt_readback"]["blocked"] is True,
        "E9": controls_by_id["wrong_top_level_verdict_enum"]["blocked"] is True,
        "E10": controls_by_id["candidate_gate5_bridge_runtime_mainline_language"]["blocked"] is True,
        "E11": controls_by_id["mechanism_score_requested"]["blocked"] is True,
        "E12": controls_by_id["false_full_suite_pass_after_timeout"]["blocked"] is True,
        "E13": controls_by_id["old_invalid_surface_cited_as_mechanism_evidence"]["blocked"] is True,
        "E14": hardening["scope_guards"]["old_preserved_artifacts_unchanged"] is True,
        "E15": valid_decision["authorization_decision"] == "authorized",
        "E16": valid_decision["no_candidate"] is True,
        "E17": valid_decision["no_mechanism_score"] is True,
        "E18": result_parseable and readback_parseable,
    }
    evidence = {
        "E1": "reconciled hardening result.json parses",
        "E2": "reconciled hardening readback.json parses",
        "E3": "hardening verdict is contract_hardened_pass",
        "E4": "G1-G14 readback gates are all present and passed",
        "E5": "anti-blacklist readback present and passed",
        "E6": "reason-specific positive/counter controls present and passed",
        "E7": "superficial contract mention synthetic control blocked",
        "E8": "missing/corrupt readback synthetic control blocked",
        "E9": "wrong verdict enum synthetic control blocked",
        "E10": "candidate/Gate5/bridge/runtime/mainline synthetic control blocked",
        "E11": "mechanism_score request synthetic control blocked",
        "E12": "false full-suite pass claim synthetic control blocked",
        "E13": "old invalid surface mechanism-evidence citation blocked",
        "E14": "old frozen artifacts reported unchanged by hardening readback",
        "E15": "valid parseable future manifest remains authorizable under governance-only constraints",
        "E16": "valid manifest creates no candidate behavior",
        "E17": "valid manifest requests no mechanism score",
        "E18": "new result.json and readback.json are parseable",
    }
    return {
        "passed": [gate_id for gate_id in REQUIRED_ACCEPTANCE if passed[gate_id]],
        "failed": [gate_id for gate_id in REQUIRED_ACCEPTANCE if not passed[gate_id]],
        "evidence_by_gate": {
            gate_id: {"passed": passed[gate_id], "evidence": [evidence[gate_id]]}
            for gate_id in REQUIRED_ACCEPTANCE
        },
    }


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


def _build_trace_rows(
    hardening: dict[str, Any],
    valid_decision: dict[str, Any],
    synthetic: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in hardening["files_read"]:
        rows.append({"event": "file_read", **item})
    for entry in hardening["invocation_log"] + valid_decision["invocation_log"]:
        rows.append({"event": "check_invoked", **entry})
    for control in synthetic["controls"]:
        rows.append(
            {
                "event": "synthetic_control_evaluated",
                "control_id": control["control_id"],
                "blocked": control["blocked"],
                "reasons_fired": control["reasons_fired"],
            }
        )
    return rows


def _write_trace_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def run_enforcement(repo_root: str | Path, output_dir: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root)
    out = Path(output_dir) if output_dir is not None else _artifact_dir(root)
    out.mkdir(parents=True, exist_ok=True)
    run_id = f"{TASK_SLUG}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    hardening = validate_hardening_artifacts(root)
    valid_manifest = build_valid_future_manifest(root)
    valid_decision = validate_future_manifest(valid_manifest, hardening)
    synthetic = build_synthetic_control_report(root, hardening)
    acceptance = _build_acceptance_gates(
        hardening,
        valid_decision,
        synthetic,
        result_parseable=True,
        readback_parseable=True,
    )
    verdict = "contract_enforcement_pass" if not acceptance["failed"] else "contract_enforcement_refused"
    if (
        hardening["hardening_result"]["parse_status"] != "parsed"
        or hardening["hardening_readback"]["parse_status"] != "parsed"
    ):
        verdict = "invalid_enforcement_harness"

    report = {
        "task_id": TASK_ID,
        "producer_function": "run_enforcement",
        "run_id": run_id,
        "inputs": {
            "hardening_result": hardening["hardening_result"]["path"],
            "hardening_readback": hardening["hardening_readback"]["path"],
            "valid_future_manifest": valid_manifest,
        },
        "referenced_artifact_ids": [HARDENING_TASK_ID, HARDENING_SLUG],
        "referenced_anchor": hardening["referenced_anchor"],
        "aggregation": "contract_enforcement_pass iff E1-E18 pass and all hostile synthetic controls are blocked",
        "code_path_hash": _source_hash(),
        "hardening_artifact_report": hardening,
        "valid_future_manifest_decision": valid_decision,
        "synthetic_control_summary": {
            "blocked_control_count": synthetic["blocked_control_count"],
            "all_controls_blocked": synthetic["all_controls_blocked"],
        },
        "acceptance_gates": acceptance,
        "claim_ceiling": CLAIM_CEILING,
    }
    result = {
        "task_id": TASK_ID,
        "verdict": verdict,
        "current_layer": LAYER,
        "mainline_integration_status": MAINLINE_STATUS,
        "enabled_status": ENABLED_STATUS,
        "real_trigger_evidence": REAL_TRIGGER_EVIDENCE,
        "claim_ceiling": CLAIM_CEILING,
        "acceptance_gates": acceptance,
        "producer_function": "run_enforcement",
        "run_id": run_id,
        "inputs": report["inputs"],
        "referenced_artifact_ids": report["referenced_artifact_ids"],
        "referenced_anchor": hardening["referenced_anchor"],
        "aggregation": report["aggregation"],
        "code_path_hash": report["code_path_hash"],
        "mechanism_score_produced": False,
        "candidate_or_surface_designed": False,
        "new_mechanism_surface_designed": False,
        "auto_remote_anchor": {
            "decision": "conditional",
            "permitted_now": verdict == "contract_enforcement_pass" and not acceptance["failed"],
            "claim_ceiling_if_performed": "remote-anchor publication and verification only",
        },
        "next_minimal_closed_loop_action": "Require this enforcement checker before future surface-admission task authorization.",
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
        "producer_function": "build_enforcement_readback",
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
        "synthetic_controls": synthetic,
        "files_read": hardening["files_read"],
        "checks_run": hardening["invocation_log"] + valid_decision["invocation_log"],
        "reasons_fired": sorted(
            set(hardening["reasons_fired"] + valid_decision["reasons_fired"])
        ),
        "no_mechanism_score": True,
        "no_candidate": True,
        "no_new_mechanism_surface": True,
        "claim_ceiling": CLAIM_CEILING,
    }

    _write_json(out / "result.json", result)
    _write_json(out / "enforcement_report.json", report)
    _write_json(out / "synthetic_control_report.json", synthetic)
    _write_json(out / "readback.json", readback)
    _write_trace_jsonl(out / "enforcement_trace.jsonl", _build_trace_rows(hardening, valid_decision, synthetic))
    (out / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
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
    run_enforcement(repo_root)
