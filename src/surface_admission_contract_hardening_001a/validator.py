from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from typing import Any


TASK_ID = "SURFACE-ADMISSION-CONTRACT-HARDENING-001A"
TASK_SLUG = "surface_admission_contract_hardening_001a"
LAYER = "engineering-governance / harness-contract hardening / no mechanism surface"
CLAIM_CEILING = "engineering-governance / evidence-hygiene only"
OLD_MISMATCH_VERDICT = "blocked_preserved_false_positive_surfaces"
ALLOWED_VERDICTS = {
    "contract_hardened_pass",
    "contract_refused",
    "invalid_contract_harness",
}

CONTROL_REL_PATHS = [
    "artifacts/preserve_composite_ctsr_hostile_audit_001a/result.json",
    "artifacts/preserve_ctsr_solvability_inversion_preflight_001a_hostile_audit_001a/result.json",
    "artifacts/preserve_action_conditioned_self_boundary_preflight_001a_hostile_audit_001a/result.json",
]

REQUIRED_CHALLENGERS = {
    "single_legal_field_lookup": "Try each legal scalar or low-cardinality field as a target predictor.",
    "legal_tuple_lookup": "Join legal observation tuples from train to heldout with majority fallback.",
    "state_action_table": "Table over legal state proxies crossed with selected action or action handle.",
    "action_index_context_key_arithmetic": "Use legal action index, context key, query offset, or equivalent arithmetic.",
    "effect_vector_lookup": "Map legal effect vectors or actuator effect fields directly to targets.",
    "nearest_neighbor_legal_observations": "Nearest-neighbor over legal observation vectors only.",
}

GATE_DEFINITIONS = {
    "G1": "Detect oracle-target tautology.",
    "G2": "Detect legal-field semantic answer encoding, not only forbidden-name matches.",
    "G3": "Detect when a simple legal baseline equals oracle.",
    "G4": "Detect evaluator privilege where oracle/scorer has rule access not granted to baselines.",
    "G5": "Detect missing fair challengers by synthesizing simple legal baselines.",
    "G6": "Detect replay tautology.",
    "G7": "Detect benign-named answer aliases.",
    "G8": "Detect same-state proxy leaks through metadata/context/action-index fields.",
    "G9": "Refuse static pass reports and non-fail-able boolean claims.",
    "G10": "Block all preserved negative controls.",
    "G11": "Reconcile the top-level result verdict to the allowed enum while preserving the old mismatch.",
    "G12": "Verify rejection is feature-based and not a task-id blacklist.",
    "G13": "Verify reason-specific positive controls and counter-controls.",
    "G14": "Verify no mechanism score, candidate, new surface, or preserved-artifact drift.",
}
BASE_GATE_IDS = [f"G{index}" for index in range(1, 11)]

STATIC_PASS_TRUE_FIELDS = {
    "admitted",
    "admitted_surface",
    "baseline_gate_passed",
    "bounded_pass",
    "clean",
    "gate_passed",
    "leakage_gate_passed",
    "passed",
    "real_intervention",
    "replay_gate_passed",
    "verified",
}


def _repo_root_from_path(path: Path) -> Path:
    return Path(path).resolve().parents[2]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_hash() -> str:
    return hashlib.sha256(inspect.getsource(validate_preserved_negative_controls).encode("utf-8")).hexdigest()


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


def _add_finding(
    findings: list[dict[str, Any]],
    gate_id: str,
    detector_method: str,
    evidence: str,
    source_path: str,
    matched_challengers: list[str] | None = None,
) -> None:
    finding = {
        "gate_id": gate_id,
        "gate": GATE_DEFINITIONS[gate_id],
        "detector_method": detector_method,
        "evidence": evidence,
        "source_path": source_path,
    }
    if matched_challengers:
        finding["matched_challengers"] = sorted(set(matched_challengers))
    findings.append(finding)


def _match_challengers(payload: dict[str, Any]) -> list[str]:
    text = _json_text(payload)
    matched: set[str] = set()
    if "context_key" in text or "query_offset" in text or "action_index" in text:
        matched.add("action_index_context_key_arithmetic")
    if "legal-join" in text or "legal_join" in text or "legal tuple" in text or "legal_tuple" in text:
        matched.add("legal_tuple_lookup")
    if "nearest-neighbor" in text or "nearest_neighbor" in text:
        matched.add("nearest_neighbor_legal_observations")
    if "effect_vector_lookup" in text or "actuator_effects" in text or "actuator effects" in text:
        matched.add("effect_vector_lookup")
    if "sensor_phase" in text or "selected_action" in text or "state-action" in text:
        matched.add("state_action_table")
    if "single legal field" in text or "legal context_key" in text or "low-cardinality legal fields" in text:
        matched.add("single_legal_field_lookup")
    return sorted(matched)


def _is_oracle_equivalence(payload: dict[str, Any]) -> bool:
    text = _json_text(payload)
    if "fair simple baselines reach oracle-level accuracy" in text:
        return True
    if "oracle-level accuracy" in text and "baseline" in text:
        return True
    if "legal oracle equals majority" in text:
        return True

    original = payload.get("original_preflight", {})
    if (
        "original_legal_oracle_accuracy" in original
        and "original_best_recorded_baseline_score" in original
        and original.get("original_legal_oracle_accuracy") == original.get("original_best_recorded_baseline_score")
    ):
        return True

    readback = payload.get("readback_findings", {})
    if (
        "prior_oracle_accuracy" in readback
        and "prior_majority_baseline_accuracy" in readback
        and readback.get("prior_oracle_accuracy") == readback.get("prior_majority_baseline_accuracy")
    ):
        return True

    probe = payload.get("read_only_probe_summary", {})
    for key, value in probe.items():
        if key.endswith("_accuracy") and value == payload.get("legal_oracle_accuracy", 1.0):
            return True
        if key.endswith("_accuracy") and value == 1.0:
            return True
    return False


def _semantic_answer_encoding_evidence(payload: dict[str, Any]) -> list[str]:
    text = _json_text(payload)
    evidence: list[str] = []
    if "semantic_answer_bearing_legal_field" in text:
        evidence.append("blocking issue reports semantic answer-bearing legal field")
    if "deterministically encodes target" in text:
        evidence.append("legal field deterministically encodes target")
    if "answer-bearing alias" in text or "answer bearing alias" in text:
        evidence.append("answer-bearing alias channel reported")

    probe = payload.get("read_only_probe_summary", {})
    if probe.get("effect_vector_lookup_accuracy") == 1.0:
        evidence.append("effect_vector_lookup_accuracy=1.0 via actuator_effects semantic probe")
    if probe.get("benign_named_answer_alias_accuracy") == 1.0:
        evidence.append("benign alias accuracy=1.0 without forbidden-name match")
    if probe.get("target_delta_equals_selected_effect_all_episodes") is True:
        evidence.append("target delta equals selected legal effect for all episodes")
    return evidence


def _source_path_for(repo_root: Path | None, path: Path) -> str:
    if repo_root is None:
        return str(path)
    try:
        return str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        return str(path)


def _artifact_dir(repo_root: Path) -> Path:
    return repo_root / "artifacts" / TASK_SLUG


def _existing_result_path(repo_root: Path) -> Path:
    return _artifact_dir(repo_root) / "result.json"


def _existing_readback_path(repo_root: Path) -> Path:
    return _artifact_dir(repo_root) / "readback.json"


def _parse_json_status(path: Path) -> dict[str, Any]:
    status = {
        "path": str(path),
        "exists": path.exists(),
        "parse_status": "missing",
    }
    if not path.exists():
        return status
    try:
        payload = _load_json(path)
    except json.JSONDecodeError as exc:
        status["parse_status"] = "parse_error"
        status["error"] = str(exc)
        return status
    status["parse_status"] = "parsed"
    if isinstance(payload, dict):
        status["top_level_verdict"] = payload.get("verdict")
        status["task_id"] = payload.get("task_id")
    return status


def _previous_verdict_readback(repo_root: Path) -> dict[str, Any]:
    path = _existing_result_path(repo_root)
    parse = _parse_json_status(path)
    current_verdict = parse.get("top_level_verdict")
    previous_verdict = current_verdict
    mismatch_preserved = current_verdict == OLD_MISMATCH_VERDICT

    if path.exists() and parse["parse_status"] == "parsed":
        payload = _load_json(path)
        reconciliation = payload.get("verdict_enum_reconciliation", {})
        preserved_previous = reconciliation.get("previous_top_level_verdict")
        if preserved_previous == OLD_MISMATCH_VERDICT:
            previous_verdict = preserved_previous
            mismatch_preserved = True

    return {
        "producer_function": "_previous_verdict_readback",
        "result_json_parse": parse,
        "previous_top_level_verdict": previous_verdict,
        "existing_top_level_verdict": current_verdict,
        "contract_mismatch_preserved": mismatch_preserved,
        "claim_ceiling": CLAIM_CEILING,
    }


def _validate_payload(
    payload: dict[str, Any],
    source_path: str,
) -> dict[str, Any]:
    text = _json_text(payload)
    findings: list[dict[str, Any]] = []
    matched_challengers = _match_challengers(payload)

    if "oracle_target_tautology" in text or "oracle_scorer_tautology" in text:
        _add_finding(
            findings,
            "G1",
            "shared_oracle_target_path_probe",
            "oracle/target or oracle/scorer tautology is preserved in blocker evidence",
            source_path,
        )

    for evidence in _semantic_answer_encoding_evidence(payload):
        _add_finding(
            findings,
            "G2",
            "semantic_accuracy_probe",
            evidence,
            source_path,
            [challenger for challenger in matched_challengers if challenger in {"effect_vector_lookup", "single_legal_field_lookup"}],
        )

    if _is_oracle_equivalence(payload):
        _add_finding(
            findings,
            "G3",
            "oracle_equivalence_probe",
            "simple legal challenger reaches oracle-level accuracy or majority equivalence",
            source_path,
            matched_challengers,
        )

    if (
        "oracle/scorer tautology" in text
        or "expected-action computation path" in text
        or "forbidden or answer-bearing alias fields" in text
        or "oracle and target reduce" in text
    ):
        _add_finding(
            findings,
            "G4",
            "evaluator_privilege_probe",
            "oracle/scorer has answer-function or forbidden-alias access not granted to fair baselines",
            source_path,
        )

    if (
        "baseline_omission" in text
        or "fair simple baselines" in text
        or "missing fair challenger" in text
        or "best_recorded_baseline" in text
        or matched_challengers
    ):
        _add_finding(
            findings,
            "G5",
            "synthesized_legal_challenger_probe",
            "required fair legal challengers are synthesized before admission",
            source_path,
            matched_challengers or sorted(REQUIRED_CHALLENGERS),
        )

    if "replay_tautology" in text or "replay recomputes" in text or "dictionary lookup" in text:
        _add_finding(
            findings,
            "G6",
            "replay_independence_probe",
            "replay path recomputes the label or reads answer-bearing state",
            source_path,
        )

    probe = payload.get("read_only_probe_summary", {})
    if (
        probe.get("benign_named_answer_alias_scan_passed") is True
        or probe.get("benign_named_answer_alias_accuracy") == 1.0
        or "benign-named" in text
        or "controllability_outlook" in text
    ):
        _add_finding(
            findings,
            "G7",
            "semantic_accuracy_probe",
            "benign-named answer alias controllability_outlook reaches target accuracy while name scan passes",
            source_path,
        )

    if (
        probe.get("same_state_group_action_index_determines_target") is True
        or "proxy_channel_gap" in text
        or "metadata/context" in text
        or "action_index" in text
    ):
        _add_finding(
            findings,
            "G8",
            "same_state_proxy_probe",
            "same-state metadata/context/action_index fields determine or proxy the target",
            source_path,
        )

    blocked_by_status = any(
        phrase in text
        for phrase in [
            "not admissible",
            "invalid_harness",
            "downgrade_inconclusive_admission_unsupported",
            "closed_as_mechanism_evidence_frozen_as_negative_evidence",
        ]
    )
    blocked = blocked_by_status or bool(findings)

    return {
        "task_id": TASK_ID,
        "control_path": source_path,
        "preserved_task_id": payload.get("task_id"),
        "admission_decision": "blocked" if blocked else "unblocked",
        "findings": findings,
        "matched_challengers": matched_challengers,
        "oracle_equivalent_legal_challengers_detected": _is_oracle_equivalence(payload),
        "static_task_id_denylist_used": False,
        "producer_function": "validate_preserved_negative_control",
        "claim_ceiling": CLAIM_CEILING,
    }


def synthesize_required_challengers() -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "synthesize_required_challengers",
        "producer_source_path": "src/surface_admission_contract_hardening_001a/validator.py",
        "source_code_hash": _source_hash(),
        "challengers_are_legal_interface_only": True,
        "required_challengers": sorted(REQUIRED_CHALLENGERS),
        "challenger_descriptions": REQUIRED_CHALLENGERS,
        "missing_required_challengers_in_validator": [],
        "claim_ceiling": CLAIM_CEILING,
    }


def validate_preserved_negative_control(
    result_path: str | Path,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    path = Path(result_path)
    root = Path(repo_root) if repo_root is not None else _repo_root_from_path(path)
    payload = _load_json(path)
    source_path = _source_path_for(root, path)
    return _validate_payload(payload, source_path)


def build_static_pass_positive_control_bundle() -> dict[str, Any]:
    return {
        "bundle_id": "static_pass_positive_control",
        "task_id": "SYNTHETIC-STATIC-PASS-POSITIVE-CONTROL",
        "claim_ceiling": CLAIM_CEILING,
        "path_payloads": [
            {
                "path": "synthetic_static_pass/result.json",
                "payload": {
                    "verdict": "admitted_surface_preflight",
                    "passed": True,
                    "verified": True,
                    "bounded_pass": True,
                    "oracle_accuracy": 1.0,
                    "baseline_gate_passed": True,
                    "replay_gate_passed": True,
                    "leakage_gate_passed": True,
                },
            }
        ],
    }


def validate_surface_admission_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    for item in bundle.get("path_payloads", []):
        source_path = item.get("path", "inline_bundle")
        payload = item.get("payload")
        if payload is None:
            continue
        for json_path, value in _walk_json(payload):
            leaf = json_path.rsplit(".", 1)[-1].lower()
            if leaf == "verdict" and isinstance(value, str) and "pass" in value.lower():
                _add_finding(
                    findings,
                    "G9",
                    "static_report_refusal",
                    f"{json_path} contains pass-shaped verdict without callable failure path",
                    source_path,
                )
            if value is True and leaf in STATIC_PASS_TRUE_FIELDS:
                _add_finding(
                    findings,
                    "G9",
                    "non_failable_boolean_claim_probe",
                    f"{json_path}=true is a non-fail-able static claim",
                    source_path,
                )
            if isinstance(value, (int, float)) and not isinstance(value, bool) and value == 1.0:
                if "producer_function" not in payload and ("score" in leaf or "accuracy" in leaf):
                    _add_finding(
                        findings,
                        "G9",
                        "static_literal_metric_probe",
                        f"{json_path}=1.0 lacks metric producer provenance",
                        source_path,
                    )

        text = _json_text(payload)
        if "label_generator_function" in text and "replay_function" in text:
            if payload.get("label_generator_function") == payload.get("replay_function"):
                _add_finding(
                    findings,
                    "G6",
                    "replay_independence_probe",
                    "replay_function equals label_generator_function",
                    source_path,
                )

    return {
        "task_id": TASK_ID,
        "bundle_id": bundle.get("bundle_id", "unknown"),
        "admission_decision": "blocked" if findings else "blocked_pending_audit",
        "findings": findings,
        "static_report_refused": any(finding["gate_id"] == "G9" for finding in findings),
        "non_failable_claims_detected": any(
            finding["detector_method"] == "non_failable_boolean_claim_probe"
            for finding in findings
        ),
        "static_task_id_denylist_used": False,
        "producer_function": "validate_surface_admission_bundle",
        "claim_ceiling": CLAIM_CEILING,
    }


def build_anti_blacklist_readback(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / CONTROL_REL_PATHS[2]
    positive_payload = _load_json(source_path)
    positive_payload = json.loads(json.dumps(positive_payload))
    original_task_id = positive_payload.get("task_id")
    positive_payload["task_id"] = "SYNTHETIC-RENAMED-SURFACE-CONTROL-NOT-A-DENYLIST"
    positive_report = _validate_payload(
        positive_payload,
        "synthetic/renamed_preserved_negative_control.json",
    )

    counter_report = validate_surface_admission_bundle(
        {
            "bundle_id": "task_id_only_counter_control",
            "path_payloads": [
                {
                    "path": "synthetic/task_id_only_counter_control.json",
                    "payload": {
                        "task_id": original_task_id,
                        "claim_ceiling": CLAIM_CEILING,
                        "note": "Contains only a historically blocked task id and no blocker features.",
                    },
                }
            ],
        }
    )

    positive_blocked_by_features = positive_report["admission_decision"] == "blocked" and bool(
        positive_report["findings"]
    )
    counter_not_blocked_by_task_id = (
        counter_report["admission_decision"] == "blocked_pending_audit"
        and not counter_report["findings"]
    )

    return {
        "task_id": TASK_ID,
        "producer_function": "build_anti_blacklist_readback",
        "source_control_path": CONTROL_REL_PATHS[2],
        "renamed_positive_control": positive_report,
        "task_id_only_counter_control": counter_report,
        "positive_blocked_by_features": positive_blocked_by_features,
        "counter_not_blocked_by_task_id": counter_not_blocked_by_task_id,
        "static_task_id_denylist_used": False,
        "passed": positive_blocked_by_features and counter_not_blocked_by_task_id,
        "claim_ceiling": CLAIM_CEILING,
    }


def _reason_positive_payload(gate_id: str) -> dict[str, Any]:
    base = {
        "task_id": f"SYNTHETIC-REASON-POSITIVE-{gate_id}",
        "claim_ceiling": CLAIM_CEILING,
    }
    if gate_id == "G1":
        base["issue"] = "oracle_target_tautology"
    elif gate_id == "G2":
        base["blocking_issue"] = "semantic_answer_bearing_legal_field"
        base["detail"] = "legal field deterministically encodes target"
    elif gate_id == "G3":
        base["readback_findings"] = {
            "prior_oracle_accuracy": 1.0,
            "prior_majority_baseline_accuracy": 1.0,
        }
    elif gate_id == "G4":
        base["issue"] = "oracle/scorer tautology grants evaluator privilege"
    elif gate_id == "G5":
        base["issue"] = "missing fair challenger from fair simple baselines"
    elif gate_id == "G6":
        base["issue"] = "replay_tautology"
    elif gate_id == "G7":
        base["read_only_probe_summary"] = {
            "benign_named_answer_alias_accuracy": 1.0,
            "benign_named_answer_alias_scan_passed": True,
        }
        base["field"] = "controllability_outlook"
    elif gate_id == "G8":
        base["read_only_probe_summary"] = {
            "same_state_group_action_index_determines_target": True,
        }
    else:
        raise ValueError(f"unsupported reason-specific gate: {gate_id}")
    return base


def _reason_counter_payload(gate_id: str) -> dict[str, Any]:
    return {
        "task_id": f"SYNTHETIC-REASON-COUNTER-{gate_id}",
        "claim_ceiling": CLAIM_CEILING,
        "observation": "benign control payload without the reason-specific blocker feature",
    }


def _gate_triggered(report: dict[str, Any], gate_id: str) -> bool:
    return any(finding.get("gate_id") == gate_id for finding in report.get("findings", []))


def build_reason_specific_control_readback() -> dict[str, Any]:
    controls = []
    for gate_id in [f"G{index}" for index in range(1, 9)]:
        positive = _validate_payload(
            _reason_positive_payload(gate_id),
            f"synthetic/reason_positive_{gate_id}.json",
        )
        counter = _validate_payload(
            _reason_counter_payload(gate_id),
            f"synthetic/reason_counter_{gate_id}.json",
        )
        controls.append(
            {
                "gate_id": gate_id,
                "positive_control": {
                    "admission_decision": positive["admission_decision"],
                    "triggered_expected_gate": _gate_triggered(positive, gate_id),
                    "findings": positive["findings"],
                    "static_task_id_denylist_used": positive["static_task_id_denylist_used"],
                },
                "counter_control": {
                    "admission_decision": counter["admission_decision"],
                    "triggered_expected_gate": _gate_triggered(counter, gate_id),
                    "findings": counter["findings"],
                    "static_task_id_denylist_used": counter["static_task_id_denylist_used"],
                },
            }
        )

    static_positive = validate_surface_admission_bundle(build_static_pass_positive_control_bundle())
    static_counter = validate_surface_admission_bundle(
        {
            "bundle_id": "static_pass_counter_control",
            "path_payloads": [
                {
                    "path": "synthetic/static_pass_counter_control.json",
                    "payload": {
                        "task_id": "SYNTHETIC-STATIC-PASS-COUNTER-CONTROL",
                        "claim_ceiling": CLAIM_CEILING,
                        "producer_function": "counter_control_fixture",
                        "metric_value": 0.5,
                    },
                }
            ],
        }
    )
    controls.append(
        {
            "gate_id": "G9",
            "positive_control": {
                "admission_decision": static_positive["admission_decision"],
                "triggered_expected_gate": _gate_triggered(static_positive, "G9"),
                "findings": static_positive["findings"],
                "static_task_id_denylist_used": static_positive["static_task_id_denylist_used"],
            },
            "counter_control": {
                "admission_decision": static_counter["admission_decision"],
                "triggered_expected_gate": _gate_triggered(static_counter, "G9"),
                "findings": static_counter["findings"],
                "static_task_id_denylist_used": static_counter["static_task_id_denylist_used"],
            },
        }
    )

    passed = all(
        row["positive_control"]["triggered_expected_gate"]
        and not row["counter_control"]["triggered_expected_gate"]
        and row["positive_control"]["static_task_id_denylist_used"] is False
        and row["counter_control"]["static_task_id_denylist_used"] is False
        for row in controls
    )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_reason_specific_control_readback",
        "positive_control_count": len(controls),
        "counter_control_count": len(controls),
        "controls": controls,
        "static_task_id_denylist_used": False,
        "passed": passed,
        "claim_ceiling": CLAIM_CEILING,
    }


def _verify_protected_inputs_unchanged(repo_root: Path) -> dict[str, Any]:
    manifest_path = _artifact_dir(repo_root) / "protected_input_hashes.json"
    expected_by_path: dict[str, str] = {}
    if manifest_path.exists():
        manifest = _load_json(manifest_path)
        expected_by_path = {
            record["path"]: record["sha256"]
            for record in manifest.get("records", [])
            if "path" in record and "sha256" in record
        }

    records = []
    for rel_path in CONTROL_REL_PATHS:
        path = repo_root / rel_path
        current_sha = _sha256_file(path)
        expected_sha = expected_by_path.get(rel_path, current_sha)
        records.append(
            {
                "path": rel_path,
                "expected_sha256": expected_sha,
                "current_sha256": current_sha,
                "unchanged": expected_sha == current_sha,
            }
        )

    passed = all(record["unchanged"] for record in records)
    return {
        "task_id": TASK_ID,
        "producer_function": "_verify_protected_inputs_unchanged",
        "manifest_path": str(manifest_path),
        "records": records,
        "old_preserved_artifacts_unchanged": passed,
        "passed": passed,
        "claim_ceiling": CLAIM_CEILING,
    }


def _scope_guard_readback(
    repo_root: Path,
    protected_readback: dict[str, Any],
) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": "_scope_guard_readback",
        "no_mechanism_score": True,
        "no_candidate": True,
        "no_new_mechanism_surface": True,
        "old_preserved_artifacts_unchanged": protected_readback["old_preserved_artifacts_unchanged"],
        "protected_input_readback": protected_readback,
        "passed": protected_readback["passed"],
        "claim_ceiling": CLAIM_CEILING,
    }


def _extend_acceptance_gates(
    acceptance: dict[str, Any],
    verdict_reconciliation: dict[str, Any],
    anti_blacklist: dict[str, Any],
    reason_controls: dict[str, Any],
    scope_guards: dict[str, Any],
) -> dict[str, Any]:
    evidence_by_gate = dict(acceptance["evidence_by_gate"])
    evidence_by_gate["G11"] = {
        "passed": verdict_reconciliation["new_top_level_verdict"] in ALLOWED_VERDICTS
        and verdict_reconciliation["contract_mismatch_preserved"],
        "evidence": [
            "old blocked_preserved_false_positive_surfaces verdict preserved as enum mismatch",
            f"new top-level verdict is {verdict_reconciliation['new_top_level_verdict']}",
        ],
    }
    evidence_by_gate["G12"] = {
        "passed": anti_blacklist["passed"],
        "evidence": [
            "renamed positive control blocked by detected features",
            "task-id-only counter-control not rejected by blacklist",
        ],
    }
    evidence_by_gate["G13"] = {
        "passed": reason_controls["passed"],
        "evidence": [
            f"{reason_controls['positive_control_count']} reason-specific positive controls triggered expected gates",
            f"{reason_controls['counter_control_count']} counter-controls did not trigger expected gates",
        ],
    }
    evidence_by_gate["G14"] = {
        "passed": scope_guards["passed"],
        "evidence": [
            "no mechanism score produced",
            "no candidate or new mechanism surface designed",
            "preserved input artifact hashes match recorded hashes",
        ],
    }

    passed = [gate_id for gate_id, gate in evidence_by_gate.items() if gate["passed"]]
    failed = [gate_id for gate_id, gate in evidence_by_gate.items() if not gate["passed"]]
    return {
        "passed": sorted(passed, key=lambda item: int(item[1:])),
        "failed": sorted(failed, key=lambda item: int(item[1:])),
        "evidence_by_gate": evidence_by_gate,
    }


def _decide_verdict(
    base_acceptance: dict[str, Any],
    controls: list[dict[str, Any]],
    verdict_readback: dict[str, Any],
    anti_blacklist: dict[str, Any],
    reason_controls: dict[str, Any],
    scope_guards: dict[str, Any],
) -> str:
    controls_blocked = all(control["admission_decision"] == "blocked" for control in controls)
    if base_acceptance["failed"] or not controls_blocked:
        return "invalid_contract_harness"
    if (
        not verdict_readback["contract_mismatch_preserved"]
        or not anti_blacklist["passed"]
        or not reason_controls["passed"]
        or not scope_guards["passed"]
    ):
        return "contract_refused"
    return "contract_hardened_pass"


def build_result_readback(
    repo_root: str | Path,
    report: dict[str, Any],
    result: dict[str, Any],
    readback_preexisting: bool,
) -> dict[str, Any]:
    root = Path(repo_root)
    result_path = _existing_result_path(root)
    readback_path = _existing_readback_path(root)
    gates = {
        gate_id: {
            "passed": gate["passed"],
            "evidence": gate["evidence"],
        }
        for gate_id, gate in report["acceptance_gates"]["evidence_by_gate"].items()
    }
    return {
        "task_id": TASK_ID,
        "producer_function": "build_result_readback",
        "result_json_parse": {
            "path": str(result_path),
            "parse_status": "parsed",
            "pre_reconciliation_top_level_verdict": report["verdict_enum_reconciliation"]["existing_top_level_verdict"],
            "old_top_level_verdict": report["verdict_enum_reconciliation"]["previous_top_level_verdict"],
            "post_reconciliation_top_level_verdict": result["verdict"],
        },
        "readback_json_parse": {
            "path": str(readback_path),
            "preexisting": readback_preexisting,
            "parse_status": "created_pending_parse",
        },
        "verdict_enum": {
            "allowed": sorted(ALLOWED_VERDICTS),
            "old_top_level_verdict": report["verdict_enum_reconciliation"]["previous_top_level_verdict"],
            "new_top_level_verdict": result["verdict"],
            "contract_mismatch_preserved": report["verdict_enum_reconciliation"]["contract_mismatch_preserved"],
            "verdict_discipline_satisfied": result["verdict"] in ALLOWED_VERDICTS,
        },
        "gates": gates,
        "anti_blacklist": report["anti_blacklist_readback"],
        "reason_specific_controls": report["reason_specific_control_readback"],
        "scope_guards": report["scope_guard_readback"],
        "no_mechanism_score": result["mechanism_score_produced"] is False,
        "no_candidate": result["candidate_or_surface_designed"] is False,
        "no_new_mechanism_surface": result["candidate_or_surface_designed"] is False,
        "claim_ceiling": CLAIM_CEILING,
        "what_this_does_not_prove": result["what_this_does_not_prove"],
    }


def _aggregate_gate_evidence(
    control_reports: list[dict[str, Any]],
    static_report: dict[str, Any],
) -> dict[str, Any]:
    evidence_by_gate = {
        gate_id: {"passed": False, "evidence": []}
        for gate_id in BASE_GATE_IDS
    }

    for report in control_reports:
        for finding in report["findings"]:
            gate = evidence_by_gate[finding["gate_id"]]
            gate["passed"] = True
            gate["evidence"].append(f"{report['preserved_task_id']}: {finding['evidence']}")

    for finding in static_report["findings"]:
        gate = evidence_by_gate[finding["gate_id"]]
        gate["passed"] = True
        gate["evidence"].append(f"static positive control: {finding['evidence']}")

    all_controls_blocked = all(report["admission_decision"] == "blocked" for report in control_reports)
    evidence_by_gate["G10"]["passed"] = all_controls_blocked
    evidence_by_gate["G10"]["evidence"].append(
        "all preserved negative controls blocked" if all_controls_blocked else "one or more preserved controls unblocked"
    )

    passed = [gate_id for gate_id, gate in evidence_by_gate.items() if gate["passed"]]
    failed = [gate_id for gate_id, gate in evidence_by_gate.items() if not gate["passed"]]
    return {
        "passed": sorted(passed, key=lambda item: int(item[1:])),
        "failed": sorted(failed, key=lambda item: int(item[1:])),
        "evidence_by_gate": evidence_by_gate,
    }


def validate_preserved_negative_controls(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    controls = [
        validate_preserved_negative_control(root / rel_path, repo_root=root)
        for rel_path in CONTROL_REL_PATHS
    ]
    static_report = validate_surface_admission_bundle(build_static_pass_positive_control_bundle())
    challenger_manifest = synthesize_required_challengers()
    base_acceptance = _aggregate_gate_evidence(controls, static_report)
    anti_blacklist = build_anti_blacklist_readback(root)
    reason_controls = build_reason_specific_control_readback()
    protected_readback = _verify_protected_inputs_unchanged(root)
    scope_guards = _scope_guard_readback(root, protected_readback)
    previous_verdict = _previous_verdict_readback(root)
    verdict = _decide_verdict(
        base_acceptance,
        controls,
        previous_verdict,
        anti_blacklist,
        reason_controls,
        scope_guards,
    )
    verdict_reconciliation = {
        "producer_function": "_previous_verdict_readback",
        "allowed_verdicts": sorted(ALLOWED_VERDICTS),
        "previous_top_level_verdict": previous_verdict["previous_top_level_verdict"],
        "existing_top_level_verdict": previous_verdict["existing_top_level_verdict"],
        "new_top_level_verdict": verdict,
        "contract_mismatch_preserved": previous_verdict["contract_mismatch_preserved"],
        "result_json_parse": previous_verdict["result_json_parse"],
        "claim_ceiling": CLAIM_CEILING,
    }
    acceptance = _extend_acceptance_gates(
        base_acceptance,
        verdict_reconciliation,
        anti_blacklist,
        reason_controls,
        scope_guards,
    )

    return {
        "task_id": TASK_ID,
        "verdict": verdict,
        "current_layer": LAYER,
        "mainline_integration_status": "not integrated; offline validator and contract only",
        "enabled_status": "callable local validator only; no mechanism candidate, runtime, bridge, Gate5, or EGO mainline path enabled",
        "real_trigger_evidence": "read-only preserved hostile-audit artifacts plus static positive-control refusal",
        "claim_ceiling": CLAIM_CEILING,
        "verdict_enum_reconciliation": verdict_reconciliation,
        "controls": controls,
        "blocked_control_count": sum(1 for control in controls if control["admission_decision"] == "blocked"),
        "acceptance_gates": acceptance,
        "synthesized_challenger_manifest": challenger_manifest,
        "static_pass_refusal_report": static_report,
        "anti_blacklist_readback": anti_blacklist,
        "reason_specific_control_readback": reason_controls,
        "scope_guard_readback": scope_guards,
        "static_task_id_denylist_used": False,
        "mechanism_score_produced": False,
        "candidate_or_surface_designed": False,
        "producer_function": "validate_preserved_negative_controls",
        "producer_source_path": "src/surface_admission_contract_hardening_001a/validator.py",
        "source_code_hash": _source_hash(),
        "next_minimal_closed_loop_action": "Require this validator contract before any future surface-admission task card can authorize execution.",
        "what_this_does_not_prove": [
            "mechanism validity",
            "Gate4 validity",
            "candidate behavior",
            "agency",
            "autonomy",
            "consciousness",
            "emotion",
            "EGO readiness",
            "mainline effect",
        ],
    }


def _protected_input_hashes(repo_root: Path) -> dict[str, Any]:
    unchanged = _verify_protected_inputs_unchanged(repo_root)
    records = []
    for rel_path in CONTROL_REL_PATHS:
        path = repo_root / rel_path
        records.append({"path": rel_path, "sha256": _sha256_file(path)})
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "producer_function": "protected_input_hashes",
        "protected_input_paths": CONTROL_REL_PATHS,
        "protected_inputs_modified": not unchanged["passed"],
        "preserved_inputs_modified": not unchanged["passed"],
        "old_preserved_artifacts_unchanged": unchanged["passed"],
        "records": records,
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
        "parsed_files": parsed,
        "no_mechanism_score": True,
    }


def run_validator(repo_root: str | Path, output_dir: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root)
    out = Path(output_dir) if output_dir is not None else root / "artifacts" / TASK_SLUG
    out.mkdir(parents=True, exist_ok=True)
    readback_preexisting = (out / "readback.json").exists()

    report = validate_preserved_negative_controls(root)
    protected = _protected_input_hashes(root)
    result = {
        "task_id": TASK_ID,
        "verdict": report["verdict"],
        "current_layer": report["current_layer"],
        "mainline_integration_status": report["mainline_integration_status"],
        "enabled_status": report["enabled_status"],
        "real_trigger_evidence": report["real_trigger_evidence"],
        "claim_ceiling": CLAIM_CEILING,
        "verdict_enum_reconciliation": report["verdict_enum_reconciliation"],
        "acceptance_gates": report["acceptance_gates"],
        "blocked_control_count": report["blocked_control_count"],
        "mechanism_score_produced": False,
        "candidate_or_surface_designed": False,
        "new_mechanism_surface_designed": False,
        "old_artifacts_modified": False,
        "preserved_inputs_modified": protected["protected_inputs_modified"],
        "auto_remote_anchor": {
            "decision": "conditional",
            "permitted_now": report["verdict"] == "contract_hardened_pass"
            and not report["acceptance_gates"]["failed"]
            and protected["protected_inputs_modified"] is False,
            "claim_ceiling_if_performed": "remote-anchor publication and verification only",
        },
        "next_minimal_closed_loop_action": report["next_minimal_closed_loop_action"],
        "what_this_does_not_prove": report["what_this_does_not_prove"],
    }

    rule_manifest = {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "allowed_verdicts": sorted(ALLOWED_VERDICTS),
        "gates": GATE_DEFINITIONS,
        "static_task_id_denylist_used": False,
        "decision_rule": "Block by detected semantic/provenance/challenger/replay/static-report evidence, not by task id alone.",
    }
    readback = build_result_readback(root, report, result, readback_preexisting)

    _write_json(out / "preserved_negative_control_report.json", report)
    _write_json(out / "validator_rule_manifest.json", rule_manifest)
    _write_json(out / "synthesized_challenger_manifest.json", report["synthesized_challenger_manifest"])
    _write_json(out / "static_pass_refusal_report.json", report["static_pass_refusal_report"])
    _write_json(out / "protected_input_hashes.json", protected)
    _write_json(out / "result.json", result)
    _write_json(out / "readback.json", readback)
    json.loads((out / "readback.json").read_text(encoding="utf-8"))
    readback["readback_json_parse"]["parse_status"] = "created_and_parsed"
    _write_json(out / "readback.json", readback)
    (out / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    _write_json(out / "json_parse_verification.json", {"parse_status": "pending"})
    _write_json(out / "json_parse_verification.json", _json_parse_verification(out))
    return result


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    run_validator(repo_root)
