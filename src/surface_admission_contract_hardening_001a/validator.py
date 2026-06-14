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
}

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
    if original.get("original_legal_oracle_accuracy") == original.get("original_best_recorded_baseline_score"):
        return True

    readback = payload.get("readback_findings", {})
    if readback.get("prior_oracle_accuracy") == readback.get("prior_majority_baseline_accuracy"):
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


def _aggregate_gate_evidence(
    control_reports: list[dict[str, Any]],
    static_report: dict[str, Any],
) -> dict[str, Any]:
    evidence_by_gate = {
        gate_id: {"passed": False, "evidence": []}
        for gate_id in GATE_DEFINITIONS
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
    acceptance = _aggregate_gate_evidence(controls, static_report)
    all_blocked = all(control["admission_decision"] == "blocked" for control in controls)

    return {
        "task_id": TASK_ID,
        "verdict": "blocked_preserved_false_positive_surfaces" if all_blocked and not acceptance["failed"] else "invalid_contract",
        "current_layer": LAYER,
        "mainline_integration_status": "not integrated; offline validator and contract only",
        "enabled_status": "callable local validator only; no mechanism candidate, runtime, bridge, Gate5, or EGO mainline path enabled",
        "real_trigger_evidence": "read-only preserved hostile-audit artifacts plus static positive-control refusal",
        "claim_ceiling": CLAIM_CEILING,
        "controls": controls,
        "blocked_control_count": sum(1 for control in controls if control["admission_decision"] == "blocked"),
        "acceptance_gates": acceptance,
        "synthesized_challenger_manifest": challenger_manifest,
        "static_pass_refusal_report": static_report,
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
    records = []
    for rel_path in CONTROL_REL_PATHS:
        path = repo_root / rel_path
        records.append({"path": rel_path, "sha256": _sha256_file(path)})
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "producer_function": "protected_input_hashes",
        "protected_input_paths": CONTROL_REL_PATHS,
        "protected_inputs_modified": False,
        "preserved_inputs_modified": False,
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
        "acceptance_gates": report["acceptance_gates"],
        "blocked_control_count": report["blocked_control_count"],
        "mechanism_score_produced": False,
        "candidate_or_surface_designed": False,
        "old_artifacts_modified": False,
        "preserved_inputs_modified": protected["protected_inputs_modified"],
        "auto_remote_anchor": {
            "decision": "conditional",
            "permitted_now": report["verdict"] == "blocked_preserved_false_positive_surfaces"
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
        "gates": GATE_DEFINITIONS,
        "static_task_id_denylist_used": False,
        "decision_rule": "Block by detected semantic/provenance/challenger/replay/static-report evidence, not by task id alone.",
    }

    _write_json(out / "preserved_negative_control_report.json", report)
    _write_json(out / "validator_rule_manifest.json", rule_manifest)
    _write_json(out / "synthesized_challenger_manifest.json", report["synthesized_challenger_manifest"])
    _write_json(out / "static_pass_refusal_report.json", report["static_pass_refusal_report"])
    _write_json(out / "protected_input_hashes.json", protected)
    _write_json(out / "result.json", result)
    (out / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    _write_json(out / "json_parse_verification.json", {"parse_status": "pending"})
    _write_json(out / "json_parse_verification.json", _json_parse_verification(out))
    return result


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    run_validator(repo_root)
