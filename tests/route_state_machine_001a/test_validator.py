from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest


EXPECTED_ROUTE_STATES = (
    "PROPOSED",
    "REGISTERED",
    "READY_TO_IMPLEMENT",
    "IMPLEMENTING",
    "RUN_ATTEMPTED",
    "EVIDENCE_PACKET_READY",
    "CLOSURE_REVIEW_REQUIRED",
    "ADJUDICATED",
    "NEXT_FRONTIER_ASSIGNED",
    "REDESIGN_REQUIRED",
    "RERUN_REQUIRED",
    "OPS_FIX_REQUIRED",
    "TOMBSTONED",
)

EXPECTED_CLOSURE_TYPES = (
    "THEORY_PRESSURE",
    "INSTRUMENT_INVALID",
    "BASELINE_EQUIVALENCE",
    "IMPLEMENTATION_DEFECT",
    "OPERATION_ERROR",
    "LEAKAGE_OR_CHEATING",
    "METRIC_DEGENERACY",
    "UNDERPOWERED",
    "GOVERNANCE_STOP",
    "INCONCLUSIVE",
    "SCOPE_MISMATCH",
    "ARTIFACT_ONLY",
)


def _validator():
    from route_state_machine_001a import state_machine, validator

    return state_machine, validator


def _valid_state(current_state: str = "TOMBSTONED") -> dict:
    return {
        "route_id": "PUM-ENV-v0",
        "current_state": current_state,
        "route_family": "FSP-PUM-ENV-IDPROBE-001A",
        "updated_at_utc": "2026-07-06T00:00:00Z",
        "source_readback": {
            "ledger_path": "docs/research/FSP-STAGE-LEDGER.md",
            "ledger_entry": "L-005 and L-011",
            "tombstone_card": "docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-V0-TOMBSTONE-001A.md",
            "closure_record": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_v0_closure_record.json",
        },
    }


def _valid_n2_frontier_state(current_state: str = "REGISTERED") -> dict:
    return {
        "route_id": "N2-SBMC-ENV-REDESIGN-001A",
        "current_state": current_state,
        "route_family": "N2-SBMC",
        "frontier_scope": "design_pre_registration_current_frontier",
        "updated_at_utc": "2026-07-06T00:00:00Z",
        "authorizations": {
            "mechanism_validity": False,
            "theory_pressure": False,
            "scoring": False,
            "experiment_execution": False,
        },
        "source_readback": {
            "ledger_entries": [
                {
                    "entry": "L-014",
                    "path": "docs/research/FSP-STAGE-LEDGER.md",
                    "readback": (
                        "N2-SBMC-ENV-REDESIGN-001A banked as "
                        "design/pre-registration; candidate-free preflight; "
                        "NO code/scoring in this bank."
                    ),
                }
            ]
        },
    }


def _valid_k0_parent_state() -> dict:
    state_machine, _ = _validator()
    return {
        "route_id": state_machine.K0_PARENT_ROUTE_ID,
        "current_state": "REGISTERED",
        "route_family": "K0-DUAL-TRACK",
        "updated_at_utc": "2026-07-09T00:00:00Z",
        "authorizations": {
            key: False for key in state_machine.K0_PARENT_REQUIRED_FALSE_AUTHORIZATIONS
        },
        "implementation_authorized": False,
        "allowed_next_actions": list(state_machine.K0_PARENT_ALLOWED_ACTIONS),
        "source_readback": {
            "ledger": {
                "path": state_machine.K0_PARENT_LEDGER_PATH,
                "required_entry_prefix": state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX,
            }
        },
    }


def _valid_k0_ready_state() -> dict:
    state_machine, _ = _validator()
    state = _valid_k0_parent_state()
    state["current_state"] = "READY_TO_IMPLEMENT"
    state["phase"] = state_machine.K0_READY_PHASE
    state["implementation_authorized"] = True
    state["allowed_next_actions"] = list(state_machine.K0_READY_ALLOWED_ACTIONS)
    state["authorized_implementation_targets"] = list(
        state_machine.K0_READY_AUTHORIZED_IMPLEMENTATION_TARGETS
    )
    state["child_authorizations"] = deepcopy(state_machine.K0_READY_CHILD_AUTHORIZATIONS)
    state["red_field_addendum_pin"] = deepcopy(state_machine.K0_RED_FIELD_ADDENDUM_PIN)
    state["red_field_correction_pin"] = deepcopy(state_machine.K0_RED_FIELD_CORRECTION_PIN)
    state["h0_admission_contract_pin"] = deepcopy(state_machine.K0_H0_ADMISSION_PIN)
    state["effective_h0_authority"] = deepcopy(state_machine.K0_H0_EFFECTIVE_AUTHORITY)
    state["authorizations"] = {
        key: key in state_machine.K0_READY_REQUIRED_TRUE_AUTHORIZATIONS
        for key in state_machine.K0_PARENT_REQUIRED_FALSE_AUTHORIZATIONS
    }
    state["source_readback"] = {
        "child_card_banks": deepcopy(state_machine.K0_READY_CHILD_CARD_BANKS),
        "banked_card_objects": deepcopy(list(state_machine.K0_READY_BANKED_CARD_OBJECTS)),
        "transition_card": state_machine.K0_READY_TRANSITION_CARD_PATH,
        "ledger": {
            "path": state_machine.K0_PARENT_LEDGER_PATH,
            "required_entry_prefix": state_machine.K0_H0_ADMISSION_LEDGER_ENTRY_PREFIX,
            "preserved_entry_prefixes": [
                state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX,
                state_machine.K0_READY_LEDGER_ENTRY_PREFIX,
                state_machine.K0_RED_FIELD_LEDGER_ENTRY_PREFIX,
                state_machine.K0_RED_FIELD_CORRECTION_LEDGER_ENTRY_PREFIX,
            ],
            "preserved_entry_sha256": deepcopy(state_machine.K0_RED_FIELD_PRESERVED_LEDGER_HASHES),
        },
    }
    return state


def _valid_k0_red_field_event() -> dict:
    state_machine, _ = _validator()
    return {
        "event": "red_field_addendum_banked_and_enforced",
        "route_id": state_machine.K0_PARENT_ROUTE_ID,
        "current_state": "READY_TO_IMPLEMENT",
        "phase": state_machine.K0_RED_FIELD_ADDENDUM_PHASE,
        "red_field_addendum_pin": deepcopy(state_machine.K0_RED_FIELD_ADDENDUM_PIN),
        "foundation_authorized": True,
        "h0_authorized_only_under_addendum": True,
        "preserved_false_targets": [
            "EGO-K0-REFERENCE-KERNEL-001A",
            "ITL-K0-H0-H1-INSTRUMENT-001A:H1",
            "K0-IMMUTABLE-FREEZE-001A",
            "ITL-K0-FORMAL-EVIDENCE-001A",
        ],
    }


def _valid_k0_red_field_correction_event() -> dict:
    state_machine, _ = _validator()
    return {
        "event": "red_field_semantic_correction_banked_and_enforced",
        "route_id": state_machine.K0_PARENT_ROUTE_ID,
        "current_state": "READY_TO_IMPLEMENT",
        "phase": state_machine.K0_RED_FIELD_CORRECTION_PHASE,
        "red_field_addendum_pin": deepcopy(state_machine.K0_RED_FIELD_ADDENDUM_PIN),
        "red_field_correction_pin": deepcopy(state_machine.K0_RED_FIELD_CORRECTION_PIN),
        "foundation_authorized": True,
        "h0_authorized_only_under_both_red_gates": True,
        "preserved_false_targets": [
            "EGO-K0-REFERENCE-KERNEL-001A",
            "ITL-K0-H0-H1-INSTRUMENT-001A:H1",
            "K0-IMMUTABLE-FREEZE-001A",
            "ITL-K0-FORMAL-EVIDENCE-001A",
        ],
    }


def _valid_k0_h0_admission_event() -> dict:
    state_machine, _ = _validator()
    return {
        "event": state_machine.K0_H0_ADMISSION_EVENT,
        "route_id": state_machine.K0_PARENT_ROUTE_ID,
        "current_state": "READY_TO_IMPLEMENT",
        "phase": state_machine.K0_READY_PHASE,
        "h0_admission_contract_pin": deepcopy(state_machine.K0_H0_ADMISSION_PIN),
        "effective_h0_authority": deepcopy(state_machine.K0_H0_EFFECTIVE_AUTHORITY),
        "foundation_authorized": True,
        "h0_authorized": False,
        "downstream_children_authorized": False,
    }


def _red_field_contract() -> dict:
    _, validator = _validator()
    repo_root = Path(__file__).resolve().parents[2]
    return validator.load_json(
        repo_root
        / "artifacts"
        / "K0-DUAL-TRACK-RED-FIELD-ADDENDUM-001A"
        / "red_field_contract.json"
    )


def _red_field_correction_contract() -> dict:
    _, validator = _validator()
    repo_root = Path(__file__).resolve().parents[2]
    return validator.load_json(
        repo_root
        / "artifacts"
        / "K0-DUAL-TRACK-RED-FIELD-CORRECTION-001A"
        / "red_field_correction_contract.json"
    )


def _effective_h0_contract() -> dict:
    _, validator = _validator()
    repo_root = Path(__file__).resolve().parents[2]
    return validator.load_json(
        repo_root
        / "artifacts"
        / "ITL-K0-H0-ADMISSION-CONTRACT-002A"
        / "effective_h0_contract.json"
    )


def _valid_program_state() -> dict:
    return {
        "task_id": "ROUTE-STATE-MACHINE-001A",
        "current_frontier_route_id": "N2-SBMC-ENV-REDESIGN-001A",
        "allowed_next_actions": [
            "preserve_current_frontier_registration",
            "draft_bounded_task_card_before_any_future_code",
        ],
        "forbidden_next_actions": [
            "run_scoring",
            "run_mechanism_experiment",
            "claim_mechanism_validity",
            "claim_theory_pressure",
        ],
        "claim_ceiling": {
            "max": "local route-governance validation only",
            "forbidden_claims": [
                "mechanism_validity",
                "theory_pressure",
                "scoring_authorization",
                "experiment_execution",
            ],
        },
        "updated_at_utc": "2026-07-06T00:00:00Z",
    }


def _valid_closure(closure_type: str = "INSTRUMENT_INVALID") -> dict:
    return {
        "route_id": "PUM-ENV-v0",
        "closure_type": closure_type,
        "allowed_next_actions": [
            "preserve_historical_negative_evidence",
            "design_fresh_certified_environment",
        ],
        "forbidden_next_actions": [
            "infer_theory_failure",
            "infer_mechanism_invalidity",
            "reuse_pum_env_v0_as_certified_environment",
            "start_new_mechanism_route_on_pum_env_v0",
        ],
        "claim_ceiling": {
            "max": "historical instrument-invalid route packet only",
            "forbidden_claims": [
                "mechanism_validity",
                "theory_pressure",
                "agency",
                "autonomy",
                "subjectivity",
                "consciousness",
                "ego_readiness",
                "companion_readiness",
            ],
        },
        "evidence_status": {
            "baseline": "unknown",
            "ablation": "unknown",
            "replay": "unknown",
            "provenance": "present",
        },
        "theory_pressure_authorized": False,
        "mechanism_evidence_authorized": False,
    }


def _error_codes(result: dict) -> set[str]:
    return {error["code"] for error in result["validation_errors"]}


def _write_valid_route_artifacts(tmp_path, *, include_program_state: bool = True) -> None:
    _, validator = _validator()
    artifact_dir = tmp_path / "artifacts" / "ROUTE-STATE-MACHINE-001A"
    pum_route_dir = artifact_dir / "routes" / "PUM-ENV-v0"
    pum_route_dir.mkdir(parents=True)
    validator.write_json(pum_route_dir / "state.json", _valid_state())
    validator.write_json(pum_route_dir / "closure.json", _valid_closure())
    (pum_route_dir / "events.jsonl").write_text(
        '{"event":"closure_packet_created","route_id":"PUM-ENV-v0"}\n',
        encoding="utf-8",
    )

    n2_route_dir = artifact_dir / "routes" / "N2-SBMC-ENV-REDESIGN-001A"
    n2_route_dir.mkdir(parents=True)
    validator.write_json(n2_route_dir / "state.json", _valid_n2_frontier_state())
    (n2_route_dir / "events.jsonl").write_text(
        '{"event":"current_frontier_registered","route_id":"N2-SBMC-ENV-REDESIGN-001A"}\n',
        encoding="utf-8",
    )

    if include_program_state:
        validator.write_json(artifact_dir / "program_state.json", _valid_program_state())


def _build_report_for_tmp_tree(tmp_path) -> dict:
    _, validator = _validator()
    return validator.build_validation_report(tmp_path, changed_files=[], authorized_paths=[])


def test_state_and_closure_enums_are_exact():
    state_machine, _ = _validator()

    assert state_machine.ROUTE_STATES == EXPECTED_ROUTE_STATES
    assert state_machine.CLOSURE_TYPES == EXPECTED_CLOSURE_TYPES


def test_k0_parent_route_paths_are_explicitly_authorized():
    state_machine, _ = _validator()

    assert "docs/codex/tasks/K0-DUAL-TRACK-SUPERSESSION-001A.md" in state_machine.AUTHORIZED_TASK_PATHS
    assert (
        "artifacts/ROUTE-STATE-MACHINE-001A/routes/K0-DUAL-TRACK-SUPERSESSION-001A/state.json"
        in state_machine.AUTHORIZED_TASK_PATHS
    )
    assert state_machine.K0_RED_FIELD_ADDENDUM_CARD_PATH in state_machine.AUTHORIZED_TASK_PATHS
    assert state_machine.K0_RED_FIELD_CONTRACT_PATH in state_machine.AUTHORIZED_TASK_PATHS
    assert state_machine.K0_RED_FIELD_CORRECTION_CARD_PATH in state_machine.AUTHORIZED_TASK_PATHS
    assert state_machine.K0_RED_FIELD_CORRECTION_CONTRACT_PATH in state_machine.AUTHORIZED_TASK_PATHS


@pytest.mark.parametrize(
    "authorization_key",
    (
        "agency",
        "autonomy",
        "consciousness",
        "ego_mainline_runtime",
        "experiment_execution",
        "formal_run",
        "foundation_implementation",
        "freeze",
        "h1_implementation",
        "k0_reference_implementation",
        "mechanism_validity",
        "remote_anchor",
        "scoring",
        "subjectivity",
        "theory_pressure",
        "ui_llm_deployment",
    ),
)
def test_k0_registered_parent_rejects_every_forbidden_authorization(authorization_key):
    _, validator = _validator()
    state = _valid_k0_parent_state()
    state["authorizations"][authorization_key] = True

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )

    assert "k0_registered_parent_forbidden_authorization" in _error_codes(result)


def test_k0_registered_parent_rejects_root_implementation_authorization():
    _, validator = _validator()
    state = _valid_k0_parent_state()
    state["implementation_authorized"] = True

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )

    assert "k0_registered_parent_implementation_not_explicitly_false" in _error_codes(result)


def test_k0_registered_parent_rejects_closure_packet_and_missing_ledger():
    _, validator = _validator()
    state = _valid_k0_parent_state()
    del state["source_readback"]["ledger"]

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=_valid_closure(),
        changed_files=[],
    )

    codes = _error_codes(result)
    assert "k0_parent_has_unexpected_closure" in codes
    assert "k0_parent_ledger_declaration_missing" in codes


@pytest.mark.parametrize(
    "current_state",
    tuple(state for state in EXPECTED_ROUTE_STATES if state not in ("REGISTERED", "READY_TO_IMPLEMENT")),
)
def test_k0_parent_rejects_state_outside_registered_and_ready_contract(current_state):
    _, validator = _validator()
    state = _valid_k0_parent_state()
    state["current_state"] = current_state

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )

    assert "k0_parent_state_outside_authorized_contract" in _error_codes(result)


def test_valid_k0_ready_first_pair_contract_passes():
    _, validator = _validator()

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=_valid_k0_ready_state(),
        closure_payload=None,
        changed_files=[],
    )

    assert result["verdict"] == "pass"
    assert result["validation_errors"] == []


def test_h0_c1_c4_collision_resolves_once_without_component_erasure():
    _, validator = _validator()
    component_states = {
        component_id: "PRESENT_BOUNDED"
        for component_id in validator.state_machine.K0_H0_EVIDENCE_COMPONENT_IDS
    }

    result = validator.resolve_h0_terminal_bundle(
        component_states=component_states,
        integrity_valid=True,
        control_state="CONTROL_EQUIVALENT",
        rival_state="RIVAL_SEPARATED",
    )

    assert result["component_evidence"] == component_states
    assert result["specialness_claim"] == {
        "admissible": False,
        "reason": "control_not_separated",
    }
    assert "evidence_state" not in result["specialness_claim"]


@pytest.mark.parametrize("proof_kind", ("CAUSAL_NO_CONTRIBUTION", "CAUSAL_WRONG_SIGN"))
def test_h0_powered_causal_absence_proof_kinds_resolve_absent(proof_kind):
    _, validator = _validator()
    result = validator.resolve_component_terminal_state(
        required_run_started=True,
        integrity_valid=True,
        causal_comparisons=[{"power_target_met": True, "proof_kind": proof_kind}],
    )
    assert result["evidence_state"] == "ABSENT"


def test_h0_causal_underpower_resolves_invalid_instrument():
    _, validator = _validator()
    result = validator.resolve_component_terminal_state(
        required_run_started=True,
        integrity_valid=True,
        causal_comparisons=[
            {"power_target_met": False, "proof_kind": "CAUSAL_NO_CONTRIBUTION"}
        ],
    )
    assert result == {
        "evidence_state": "INVALID_INSTRUMENT",
        "reason": "causal_comparison_underpowered",
    }


@pytest.mark.parametrize(
    ("panel_kind", "expected"),
    (("control", "CONTROL_INCONCLUSIVE"), ("rival", "RIVAL_INCONCLUSIVE")),
)
def test_h0_comparison_underpower_is_inconclusive_only(panel_kind, expected):
    _, validator = _validator()
    assert (
        validator.resolve_comparison_terminal_state(
            panel_kind=panel_kind,
            run_started=True,
            power_target_met=False,
            relation="powered_parity",
        )
        == expected
    )


@pytest.mark.parametrize("mutation", ("delete", "duplicate", "aggregate_only"))
def test_h0_atomic_tuple_bijection_rejects_missing_duplicate_and_aggregate_only(mutation):
    _, validator = _validator()
    contract = _effective_h0_contract()
    panels = deepcopy(contract["component_panels"])
    specs = validator._build_atomic_bijection_witness(panels)
    if mutation == "delete":
        specs.pop()
    elif mutation == "duplicate":
        duplicate = deepcopy(specs[0])
        duplicate["atomic_contrast_id"] += "::duplicate"
        specs.append(duplicate)
    else:
        panels[0]["causal"]["arm_ids"] = []
    result = validator.validate_atomic_contrast_bijection(
        panels,
        specs,
        required_fields=contract["atomic_contrast_bijection"]["required_atomic_spec_fields"],
    )
    codes = _error_codes(result)
    assert codes & {
        "h0_atomic_tuple_missing",
        "h0_atomic_tuple_duplicate",
        "h0_atomic_aggregate_only_coverage",
        "h0_atomic_tuple_orphan",
    }


@pytest.mark.parametrize(
    "filename",
    (
        "control_signature_contract.json",
        "control_signature_simulation.json",
        "determinism_contract.json",
        "control_signature_coverage_report.json",
    ),
)
def test_h0_effective_path_authority_rejects_each_missing_added_artifact(filename):
    _, validator = _validator()
    contract = _effective_h0_contract()
    contract["path_authority"]["repo_write_allowlist"].remove(
        f"artifacts/ITL-K0-H0-H1-INSTRUMENT-001A/h0/{filename}"
    )
    result = validator.validate_effective_h0_path_authority(contract)
    assert "h0_path_authority_allowlist_mismatch" in _error_codes(result)


def test_h0_effective_path_authority_rejects_unlisted_filename():
    _, validator = _validator()
    result = validator.validate_effective_h0_path_authority(
        _effective_h0_contract(),
        candidate_paths=[
            "artifacts/ITL-K0-H0-H1-INSTRUMENT-001A/h0/unlisted_result.json"
        ],
    )
    assert "h0_path_authority_unauthorized_path" in _error_codes(result)


def test_h0_true_while_admission_review_required_fails():
    _, validator = _validator()
    state = _valid_k0_ready_state()
    state["child_authorizations"]["ITL-K0-H0-H1-INSTRUMENT-001A:H0"] = True
    state["authorizations"]["h0_implementation"] = True
    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )
    codes = _error_codes(result)
    assert "k0_h0_true_while_admission_review_required" in codes
    assert "k0_ready_child_authorizations_mismatch" in codes


@pytest.mark.parametrize(
    "child_id",
    (
        "EGO-K0-REFERENCE-KERNEL-001A",
        "ITL-K0-H0-H1-INSTRUMENT-001A:H1",
        "K0-IMMUTABLE-FREEZE-001A",
        "ITL-K0-FORMAL-EVIDENCE-001A",
    ),
)
def test_h0_admission_review_required_rejects_each_downstream_child(child_id):
    _, validator = _validator()
    state = _valid_k0_ready_state()
    state["child_authorizations"][child_id] = True
    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )
    assert "k0_ready_child_authorizations_mismatch" in _error_codes(result)


@pytest.mark.parametrize("field", ("bank_commit", "card_blob", "contract_blob", "contract_sha256"))
def test_h0_admission_new_object_pin_drift_fails(field):
    _, validator = _validator()
    state = _valid_k0_ready_state()
    state["h0_admission_contract_pin"][field] = "0" * len(
        state["h0_admission_contract_pin"][field]
    )
    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )
    assert "k0_h0_admission_pin_mismatch" in _error_codes(result)


def test_h0_admission_l024_declaration_drift_fails():
    _, validator = _validator()
    state = _valid_k0_ready_state()
    state["source_readback"]["ledger"]["required_entry_prefix"] = (
        validator.state_machine.K0_RED_FIELD_CORRECTION_LEDGER_ENTRY_PREFIX
    )
    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )
    assert "k0_parent_ledger_prefix_mismatch" in _error_codes(result)


def test_h0_admission_claim_ceilings_cannot_be_swapped_or_expanded():
    _, validator = _validator()
    swapped = _effective_h0_contract()
    swapped["claim_ceilings"]["admission_task"]["exact"], swapped["claim_ceilings"][
        "future_h0"
    ]["exact"] = (
        swapped["claim_ceilings"]["future_h0"]["exact"],
        swapped["claim_ceilings"]["admission_task"]["exact"],
    )
    assert "h0_effective_claim_ceilings_invalid" in _error_codes(
        validator.validate_effective_h0_contract(swapped)
    )

    expanded = _effective_h0_contract()
    expanded["claim_ceilings"]["admission_task"]["exact"] += " plus H0 readiness"
    assert "h0_effective_claim_ceilings_invalid" in _error_codes(
        validator.validate_effective_h0_contract(expanded)
    )


def test_h0_admission_contract_rejects_deleted_historical_pin():
    _, validator = _validator()
    contract = _effective_h0_contract()
    contract["historical_provenance"]["objects"].pop()
    assert "h0_effective_historical_pins_invalid" in _error_codes(
        validator.validate_effective_h0_contract(contract)
    )


@pytest.mark.parametrize(
    "child_id",
    (
        "EGO-K0-REFERENCE-KERNEL-001A",
        "ITL-K0-H0-H1-INSTRUMENT-001A:H1",
        "K0-IMMUTABLE-FREEZE-001A",
        "ITL-K0-FORMAL-EVIDENCE-001A",
    ),
)
def test_k0_ready_rejects_each_downstream_child_authorization(child_id):
    _, validator = _validator()
    state = _valid_k0_ready_state()
    state["child_authorizations"][child_id] = True

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )

    assert "k0_ready_child_authorizations_mismatch" in _error_codes(result)


@pytest.mark.parametrize(
    ("field", "expected_code"),
    (
        ("phase", "k0_ready_phase_mismatch"),
        ("authorized_implementation_targets", "k0_ready_implementation_targets_mismatch"),
    ),
)
def test_k0_ready_rejects_phase_or_target_drift(field, expected_code):
    _, validator = _validator()
    state = _valid_k0_ready_state()
    state[field] = (
        "drifted"
        if field == "phase"
        else ["EGO-K0-FOUNDATION-001A", "ITL-K0-H0-H1-INSTRUMENT-001A:H0"]
    )

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )

    assert expected_code in _error_codes(result)


def test_k0_ready_rejects_child_commit_pin_drift():
    _, validator = _validator()
    state = _valid_k0_ready_state()
    state["source_readback"]["child_card_banks"]["ego_foundation"] = "0" * 40

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )

    assert "k0_ready_child_card_commit_pins_mismatch" in _error_codes(result)


def test_k0_ready_rejects_banked_card_blob_drift():
    _, validator = _validator()
    state = _valid_k0_ready_state()
    state["source_readback"]["banked_card_objects"][0]["blob"] = "0" * 40

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )

    assert "k0_ready_banked_card_object_readback_mismatch" in _error_codes(result)


def test_k0_ready_rejects_generic_authorization_drift():
    _, validator = _validator()
    state = _valid_k0_ready_state()
    state["authorizations"]["formal_run"] = True

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )

    assert "k0_ready_authorizations_mismatch" in _error_codes(result)


def test_k0_ready_rejects_missing_red_field_addendum_pin():
    _, validator = _validator()
    state = _valid_k0_ready_state()
    del state["red_field_addendum_pin"]

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )

    codes = _error_codes(result)
    assert "k0_red_field_addendum_pin_missing" in codes


@pytest.mark.parametrize(
    "field",
    ("bank_commit", "card_blob", "contract_blob", "contract_sha256"),
)
def test_k0_ready_rejects_each_red_field_object_pin_drift(field):
    _, validator = _validator()
    state = _valid_k0_ready_state()
    state["red_field_addendum_pin"][field] = "0" * len(state["red_field_addendum_pin"][field])

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )

    assert "k0_red_field_addendum_pin_mismatch" in _error_codes(result)


def test_k0_ready_rejects_h0_true_when_red_field_gate_not_enforced():
    _, validator = _validator()
    state = _valid_k0_ready_state()
    state["red_field_addendum_pin"]["red_field_gate_status"] = "BANKED_ONLY"

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )

    codes = _error_codes(result)
    assert "k0_red_field_addendum_pin_mismatch" in codes


def test_k0_ready_rejects_missing_red_field_correction_pin():
    _, validator = _validator()
    state = _valid_k0_ready_state()
    del state["red_field_correction_pin"]

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )

    codes = _error_codes(result)
    assert "k0_red_field_correction_pin_missing" in codes


@pytest.mark.parametrize(
    "field",
    ("bank_commit", "card_blob", "contract_blob", "contract_sha256"),
)
def test_k0_ready_rejects_each_red_field_correction_object_pin_drift(field):
    _, validator = _validator()
    state = _valid_k0_ready_state()
    state["red_field_correction_pin"][field] = "0" * len(state["red_field_correction_pin"][field])

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )

    assert "k0_red_field_correction_pin_mismatch" in _error_codes(result)


def test_k0_ready_rejects_h0_true_when_correction_gate_not_enforced():
    _, validator = _validator()
    state = _valid_k0_ready_state()
    state["red_field_correction_pin"]["red_field_correction_gate_status"] = "BANKED_ONLY"

    result = validator.validate_route_payload(
        route_id="K0-DUAL-TRACK-SUPERSESSION-001A",
        state_payload=state,
        closure_payload=None,
        changed_files=[],
    )

    codes = _error_codes(result)
    assert "k0_red_field_correction_pin_mismatch" in codes


def test_valid_committed_red_field_addendum_repository_contract_passes():
    _, validator = _validator()
    repo_root = Path(__file__).resolve().parents[2]

    result = validator.validate_red_field_addendum_repository(
        repo_root=repo_root,
        route_state_payload=_valid_k0_ready_state(),
    )

    assert result["verdict"] == "pass"
    assert result["validation_errors"] == []


def test_valid_committed_red_field_correction_repository_contract_passes():
    _, validator = _validator()
    repo_root = Path(__file__).resolve().parents[2]

    result = validator.validate_red_field_correction_repository(
        repo_root=repo_root,
        route_state_payload=_valid_k0_ready_state(),
    )

    assert result["verdict"] == "pass"
    assert result["validation_errors"] == []


def test_valid_committed_h0_admission_repository_contract_passes():
    _, validator = _validator()
    repo_root = Path(__file__).resolve().parents[2]
    result = validator.validate_h0_admission_repository(
        repo_root=repo_root,
        route_state_payload=_valid_k0_ready_state(),
    )
    assert result["verdict"] == "pass"
    assert result["truth_table_scenarios"] == 73728
    assert result["atomic_tuple_count"] > 0


def test_h0_admission_repository_rejects_non_ancestor_bank(monkeypatch):
    _, validator = _validator()
    repo_root = Path(__file__).resolve().parents[2]
    original = validator._git_is_ancestor

    def selective_ancestry(root, ancestor, descendant="HEAD"):
        if ancestor == validator.state_machine.K0_H0_ADMISSION_PIN["bank_commit"]:
            return False
        return original(root, ancestor, descendant)

    monkeypatch.setattr(validator, "_git_is_ancestor", selective_ancestry)
    result = validator.validate_h0_admission_repository(
        repo_root=repo_root,
        route_state_payload=_valid_k0_ready_state(),
    )
    assert "h0_admission_bank_commit_not_ancestor" in _error_codes(result)


def test_h0_admission_repository_rejects_modified_historical_bytes(monkeypatch):
    _, validator = _validator()
    repo_root = Path(__file__).resolve().parents[2]
    original_read_bytes = Path.read_bytes

    def altered_read_bytes(path):
        data = original_read_bytes(path)
        if path.as_posix().endswith(
            "artifacts/K0-DUAL-TRACK-RED-FIELD-ADDENDUM-001A/red_field_contract.json"
        ):
            return data + b"drift"
        return data

    monkeypatch.setattr(Path, "read_bytes", altered_read_bytes)
    result = validator.validate_h0_admission_repository(
        repo_root=repo_root,
        route_state_payload=_valid_k0_ready_state(),
    )
    assert "h0_admission_historical_object_drift" in _error_codes(result)


def test_red_field_correction_repository_rejects_non_ancestor_bank(monkeypatch):
    _, validator = _validator()
    repo_root = Path(__file__).resolve().parents[2]
    monkeypatch.setattr(validator, "_git_is_ancestor", lambda *_args, **_kwargs: False)

    result = validator.validate_red_field_correction_repository(
        repo_root=repo_root,
        route_state_payload=_valid_k0_ready_state(),
    )

    assert "red_field_correction_bank_commit_not_ancestor" in _error_codes(result)


def test_red_field_correction_repository_rejects_removed_original_addendum_pin():
    _, validator = _validator()
    repo_root = Path(__file__).resolve().parents[2]
    state = _valid_k0_ready_state()
    del state["red_field_addendum_pin"]

    result = validator.validate_red_field_correction_repository(
        repo_root=repo_root,
        route_state_payload=state,
    )

    assert "red_field_correction_original_addendum_pin_missing_or_drifted" in _error_codes(result)


def test_red_field_repository_rejects_non_ancestor_bank(monkeypatch):
    _, validator = _validator()
    repo_root = Path(__file__).resolve().parents[2]
    monkeypatch.setattr(validator, "_git_is_ancestor", lambda *_args, **_kwargs: False)

    result = validator.validate_red_field_addendum_repository(
        repo_root=repo_root,
        route_state_payload=_valid_k0_ready_state(),
    )

    assert "red_field_bank_commit_not_ancestor" in _error_codes(result)


def test_red_field_correction_c1_rejects_v_special_terminal_drift():
    _, validator = _validator()
    correction = _red_field_correction_contract()
    correction["v_special_terminal_mapping"]["inconclusive_maps_to_absent_or_present"] = True

    result = validator.validate_red_field_correction_contract(correction, _red_field_contract())

    assert "red_field_correction_c1_v_special_invalid" in _error_codes(result)


def test_red_field_correction_c2_rejects_missing_mandatory_contrast():
    _, validator = _validator()
    correction = _red_field_correction_contract()
    correction["component_verdict_formulas"][0]["mandatory_causal_contrast_ids"].remove(
        "contrast_planner_bypass"
    )
    correction["component_verdict_formulas"][5]["mandatory_causal_contrast_ids"].remove(
        "contrast_planner_bypass"
    )

    result = validator.validate_red_field_correction_contract(correction, _red_field_contract())

    codes = _error_codes(result)
    assert "red_field_correction_c2_component_formulas_invalid" in codes
    assert "red_field_correction_c2_unused_or_unresolved_contrast" in codes


def test_red_field_correction_c3_rejects_dominated_terminal_drift():
    _, validator = _validator()
    correction = _red_field_correction_contract()
    correction["effective_terminal_schema"]["control_comparison_state"].remove("CONTROL_DOMINATED")

    result = validator.validate_red_field_correction_contract(correction, _red_field_contract())

    assert "red_field_correction_c3_terminal_schema_invalid" in _error_codes(result)


def test_red_field_correction_c4_rejects_unpowered_absence():
    _, validator = _validator()
    correction = _red_field_correction_contract()
    correction["causal_absence_contract"]["failure_to_reject_effect_is_absence"] = True

    result = validator.validate_red_field_correction_contract(correction, _red_field_contract())

    assert "red_field_correction_c4_powered_absence_invalid" in _error_codes(result)


def test_red_field_correction_c5_rejects_non_exhaustive_signature_coverage():
    _, validator = _validator()
    correction = _red_field_correction_contract()
    correction["exhaustive_signature_coverage"]["all_component_mapped_arms_must_be_covered"] = False

    result = validator.validate_red_field_correction_contract(correction, _red_field_contract())

    assert "red_field_correction_c5_exhaustive_coverage_invalid" in _error_codes(result)


def test_red_field_correction_c6_rejects_rng_record_drift():
    _, validator = _validator()
    correction = _red_field_correction_contract()
    correction["rng_evidence_contract"]["distinct_fresh_process_recompute_records_required"] = 1

    result = validator.validate_red_field_correction_contract(correction, _red_field_contract())

    assert "red_field_correction_c6_rng_evidence_invalid" in _error_codes(result)


def test_red_field_correction_c7_rejects_ambiguous_seed_design():
    _, validator = _validator()
    correction = _red_field_correction_contract()
    correction["power_design_provenance"]["exactly_one_seed_design_required"] = False

    result = validator.validate_red_field_correction_contract(correction, _red_field_contract())

    assert "red_field_correction_c7_power_design_invalid" in _error_codes(result)


def test_red_field_correction_c8_rejects_machine_or_card_claim_ceiling_drift():
    _, validator = _validator()
    correction = _red_field_correction_contract()
    correction["claim_ceiling"]["allowed"].append("learned_model")

    result = validator.validate_red_field_correction_contract(
        correction,
        _red_field_contract(),
        card_claim_ceiling={"allowed": ["drift"], "forbidden": []},
    )

    assert "red_field_correction_c8_claim_ceiling_invalid" in _error_codes(result)


def test_red_field_contract_rejects_control_equivalent_in_evidence_state():
    _, validator = _validator()
    contract = _red_field_contract()
    contract["evidence_axes"]["evidence_state"].append("CONTROL_EQUIVALENT")

    result = validator.validate_red_field_contract(contract)

    codes = _error_codes(result)
    assert "red_field_contract_evidence_state_invalid" in codes
    assert "red_field_control_equivalent_in_evidence_state" in codes


@pytest.mark.parametrize(
    ("axis", "inconclusive", "expected_code"),
    (
        ("control_comparison_state", "CONTROL_INCONCLUSIVE", "red_field_contract_control_comparison_state_invalid"),
        ("comparison_state", "RIVAL_INCONCLUSIVE", "red_field_contract_comparison_state_invalid"),
    ),
)
def test_red_field_contract_rejects_missing_inconclusive_axis_value(axis, inconclusive, expected_code):
    _, validator = _validator()
    contract = _red_field_contract()
    contract["evidence_axes"][axis].remove(inconclusive)

    result = validator.validate_red_field_contract(contract)

    assert expected_code in _error_codes(result)


def test_red_field_contract_rejects_missing_control_axis():
    _, validator = _validator()
    contract = _red_field_contract()
    del contract["evidence_axes"]["control_comparison_state"]

    result = validator.validate_red_field_contract(contract)

    assert "red_field_contract_control_comparison_state_invalid" in _error_codes(result)


def test_red_field_contract_rejects_missing_window_history():
    _, validator = _validator()
    contract = _red_field_contract()
    contract["component_control_mapping"][0]["shortcut_control_arm_ids"].remove("window_history")

    result = validator.validate_red_field_contract(contract)

    assert "red_field_window_history_mapping_missing" in _error_codes(result)


def test_red_field_contract_rejects_incomplete_graph_cache_mapping():
    _, validator = _validator()
    contract = _red_field_contract()
    contract["component_control_mapping"][2]["shortcut_control_arm_ids"].remove("successor_map")

    result = validator.validate_red_field_contract(contract)

    assert "red_field_graph_cache_mapping_missing" in _error_codes(result)


def test_red_field_contract_rejects_missing_required_causal_arm():
    _, validator = _validator()
    contract = _red_field_contract()
    contract["component_control_mapping"][0]["causal_arm_ids"].remove("planner_bypass")

    result = validator.validate_red_field_contract(contract)

    assert "red_field_required_component_arm_missing" in _error_codes(result)


def test_red_field_contract_rejects_arm_role_overlap():
    _, validator = _validator()
    contract = _red_field_contract()
    contract["arm_role_contract"]["assignments"].append(
        {"arm_id": "matched_replay_off", "arm_role": "INTEGRITY_CONTROL"}
    )

    result = validator.validate_red_field_contract(contract)

    assert "red_field_arm_role_overlap_or_invalid" in _error_codes(result)


def test_red_field_contract_rejects_missing_strong_negative_simulation():
    _, validator = _validator()
    contract = _red_field_contract()
    contract["control_signature_contract"]["candidate_independent_simulation_cases"].remove(
        "strong_negative"
    )

    result = validator.validate_red_field_contract(contract)

    assert "red_field_control_signature_contract_invalid" in _error_codes(result)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("fresh_processes_required", 1),
        ("launcher_sets_pythonhashseed_before_interpreter_start", False),
        ("rng_registry", ["python_random"]),
    ),
)
def test_red_field_contract_rejects_determinism_drift(field, value):
    _, validator = _validator()
    contract = _red_field_contract()
    contract["determinism_contract"][field] = value

    result = validator.validate_red_field_contract(contract)

    assert "red_field_determinism_contract_invalid" in _error_codes(result)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("post_result_seed_addition_forbidden", False),
        ("not_rejecting_difference_is_equivalence", True),
        ("underpowered_mapping", "CONTROL_EQUIVALENT"),
    ),
)
def test_red_field_contract_rejects_power_mde_or_equivalence_drift(field, value):
    _, validator = _validator()
    contract = _red_field_contract()
    contract["power_mde_equivalence_contract"][field] = value

    result = validator.validate_red_field_contract(contract)

    assert "red_field_power_mde_equivalence_contract_invalid" in _error_codes(result)


def test_red_field_contract_rejects_unconditional_replay_failure_propagation():
    _, validator = _validator()
    contract = _red_field_contract()
    contract["integrity_blast_radius"]["unconditional_replay_failure_global_propagation_forbidden"] = False

    result = validator.validate_red_field_contract(contract)

    assert "red_field_integrity_blast_radius_invalid" in _error_codes(result)


def test_k0_red_field_event_rejects_missing_or_duplicate(tmp_path):
    _, validator = _validator()
    events_path = tmp_path / "events.jsonl"
    events_path.write_text('{"event":"first_pair_ready_to_implement"}\n', encoding="utf-8")
    missing = validator.validate_k0_red_field_event(events_path)
    assert "k0_red_field_event_missing_or_duplicate" in _error_codes(missing)

    import json

    line = json.dumps(_valid_k0_red_field_event(), sort_keys=True)
    events_path.write_text(f"{line}\n{line}\n", encoding="utf-8")
    duplicate = validator.validate_k0_red_field_event(events_path)
    assert "k0_red_field_event_missing_or_duplicate" in _error_codes(duplicate)


def test_k0_red_field_correction_event_rejects_missing_or_duplicate(tmp_path):
    _, validator = _validator()
    import json

    events_path = tmp_path / "events.jsonl"
    old_line = json.dumps(_valid_k0_red_field_event(), sort_keys=True)
    events_path.write_text(f"{old_line}\n", encoding="utf-8")
    missing = validator.validate_k0_red_field_event(events_path)
    assert "k0_red_field_correction_event_missing_or_duplicate" in _error_codes(missing)

    correction_line = json.dumps(_valid_k0_red_field_correction_event(), sort_keys=True)
    events_path.write_text(
        f"{old_line}\n{correction_line}\n{correction_line}\n",
        encoding="utf-8",
    )
    duplicate = validator.validate_k0_red_field_event(events_path)
    assert "k0_red_field_correction_event_missing_or_duplicate" in _error_codes(duplicate)


def test_h0_admission_event_is_unique_and_exact(tmp_path):
    _, validator = _validator()
    import json

    repo_root = Path(__file__).resolve().parents[2]
    live_path = (
        repo_root
        / "artifacts"
        / "ROUTE-STATE-MACHINE-001A"
        / "routes"
        / "K0-DUAL-TRACK-SUPERSESSION-001A"
        / "events.jsonl"
    )
    lines = live_path.read_text(encoding="utf-8").splitlines()
    assert validator.validate_k0_red_field_event(live_path)["verdict"] == "pass"

    missing_path = tmp_path / "missing.jsonl"
    missing_path.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    assert "k0_h0_admission_event_missing_or_duplicate" in _error_codes(
        validator.validate_k0_red_field_event(missing_path)
    )

    duplicate_path = tmp_path / "duplicate.jsonl"
    duplicate_path.write_text("\n".join(lines + [lines[-1]]) + "\n", encoding="utf-8")
    assert "k0_h0_admission_event_missing_or_duplicate" in _error_codes(
        validator.validate_k0_red_field_event(duplicate_path)
    )

    drifted = json.loads(lines[-1])
    drifted["h0_authorized"] = True
    drift_path = tmp_path / "drift.jsonl"
    drift_path.write_text(
        "\n".join(lines[:-1] + [json.dumps(drifted, sort_keys=True)]) + "\n",
        encoding="utf-8",
    )
    assert "k0_h0_admission_event_contract_mismatch" in _error_codes(
        validator.validate_k0_red_field_event(drift_path)
    )


def test_valid_pum_env_v0_closure_packet_passes():
    _, validator = _validator()

    result = validator.validate_route_payload(
        route_id="PUM-ENV-v0",
        state_payload=_valid_state(),
        closure_payload=_valid_closure(),
        changed_files=[],
    )

    assert result["verdict"] == "pass"
    assert result["validation_errors"] == []


def test_invalid_state_fails():
    _, validator = _validator()
    state = _valid_state(current_state="NOT_A_STATE")

    result = validator.validate_route_payload(
        route_id="PUM-ENV-v0",
        state_payload=state,
        closure_payload=_valid_closure(),
        changed_files=[],
    )

    assert "invalid_current_state" in _error_codes(result)
    assert result["verdict"] == "fail"


def test_missing_closure_for_closure_review_required_fails():
    _, validator = _validator()

    result = validator.validate_route_payload(
        route_id="PUM-ENV-v0",
        state_payload=_valid_state(current_state="CLOSURE_REVIEW_REQUIRED"),
        closure_payload=None,
        changed_files=[],
    )

    assert "closure_review_required_missing_closure_json" in _error_codes(result)
    assert result["verdict"] == "fail"


def test_missing_allowed_actions_fails():
    _, validator = _validator()
    closure = _valid_closure()
    closure["allowed_next_actions"] = []

    result = validator.validate_route_payload(
        route_id="PUM-ENV-v0",
        state_payload=_valid_state(),
        closure_payload=closure,
        changed_files=[],
    )

    assert "missing_non_empty_allowed_next_actions" in _error_codes(result)


def test_missing_forbidden_actions_fails():
    _, validator = _validator()
    closure = _valid_closure()
    closure["forbidden_next_actions"] = []

    result = validator.validate_route_payload(
        route_id="PUM-ENV-v0",
        state_payload=_valid_state(),
        closure_payload=closure,
        changed_files=[],
    )

    assert "missing_non_empty_forbidden_next_actions" in _error_codes(result)


def test_missing_claim_ceiling_fails():
    _, validator = _validator()
    closure = _valid_closure()
    closure["claim_ceiling"] = {}

    result = validator.validate_route_payload(
        route_id="PUM-ENV-v0",
        state_payload=_valid_state(),
        closure_payload=closure,
        changed_files=[],
    )

    assert "missing_claim_ceiling_max" in _error_codes(result)


@pytest.mark.parametrize("missing_key", ["baseline", "ablation", "replay", "provenance"])
def test_theory_pressure_without_required_evidence_fails(missing_key: str):
    _, validator = _validator()
    closure = _valid_closure(closure_type="THEORY_PRESSURE")
    closure["evidence_status"] = {
        "baseline": "present",
        "ablation": "present",
        "replay": "present",
        "provenance": "present",
    }
    closure["evidence_status"][missing_key] = "unknown"

    result = validator.validate_route_payload(
        route_id="PUM-ENV-v0",
        state_payload=_valid_state(),
        closure_payload=closure,
        changed_files=[],
    )

    assert "theory_pressure_missing_required_evidence" in _error_codes(result)


def test_instrument_invalid_with_theory_pressure_authorization_fails():
    _, validator = _validator()
    closure = _valid_closure(closure_type="INSTRUMENT_INVALID")
    closure["theory_pressure_authorized"] = True

    result = validator.validate_route_payload(
        route_id="PUM-ENV-v0",
        state_payload=_valid_state(),
        closure_payload=closure,
        changed_files=[],
    )

    assert "instrument_invalid_authorizes_theory_pressure" in _error_codes(result)


def test_artifact_only_with_mechanism_evidence_authorization_fails():
    _, validator = _validator()
    closure = _valid_closure(closure_type="ARTIFACT_ONLY")
    closure["mechanism_evidence_authorized"] = True

    result = validator.validate_route_payload(
        route_id="PUM-ENV-v0",
        state_payload=_valid_state(),
        closure_payload=closure,
        changed_files=[],
    )

    assert "artifact_only_authorizes_mechanism_evidence" in _error_codes(result)


def test_implementation_defect_allowing_new_mechanism_route_fails():
    _, validator = _validator()
    closure = _valid_closure(closure_type="IMPLEMENTATION_DEFECT")
    closure["allowed_next_actions"] = [
        "fix_implementation_defect",
        "start_new_mechanism_route",
    ]

    result = validator.validate_route_payload(
        route_id="PUM-ENV-v0",
        state_payload=_valid_state(),
        closure_payload=closure,
        changed_files=[],
    )

    assert "implementation_defect_allows_new_mechanism_route" in _error_codes(result)


def test_unresolved_closure_plus_simulated_roadmap_like_changed_file_fails():
    _, validator = _validator()

    result = validator.validate_route_payload(
        route_id="PUM-ENV-v0",
        state_payload=_valid_state(current_state="CLOSURE_REVIEW_REQUIRED"),
        closure_payload=_valid_closure(),
        changed_files=["docs/research/NEXT-MECHANISM-ROADMAP-001A.md"],
    )

    assert "unresolved_closure_with_roadmap_like_changed_file" in _error_codes(result)


def test_authorized_task_path_does_not_trigger_roadmap_like_block():
    _, validator = _validator()

    result = validator.validate_route_payload(
        route_id="PUM-ENV-v0",
        state_payload=_valid_state(current_state="CLOSURE_REVIEW_REQUIRED"),
        closure_payload=_valid_closure(),
        changed_files=["docs/research/ROUTE-STATE-MACHINE-001A.md"],
        authorized_paths=["docs/research/ROUTE-STATE-MACHINE-001A.md"],
    )

    assert "unresolved_closure_with_roadmap_like_changed_file" not in _error_codes(result)


def test_route_tree_validation_reads_real_artifacts(tmp_path):
    _, validator = _validator()
    route_dir = tmp_path / "routes" / "PUM-ENV-v0"
    route_dir.mkdir(parents=True)
    validator.write_json(route_dir / "state.json", _valid_state())
    validator.write_json(route_dir / "closure.json", _valid_closure())
    (route_dir / "events.jsonl").write_text(
        '{"event":"closure_packet_created","route_id":"PUM-ENV-v0"}\n',
        encoding="utf-8",
    )

    report = validator.validate_routes_tree(
        routes_dir=tmp_path / "routes",
        changed_files=[],
        authorized_paths=[],
    )

    assert report["verdict"] == "pass"
    assert report["route_count"] == 1
    assert report["input_artifacts"] == [
        "PUM-ENV-v0/closure.json",
        "PUM-ENV-v0/events.jsonl",
        "PUM-ENV-v0/state.json",
    ]


def test_missing_closure_type_fails():
    _, validator = _validator()
    closure = deepcopy(_valid_closure())
    del closure["closure_type"]

    result = validator.validate_route_payload(
        route_id="PUM-ENV-v0",
        state_payload=_valid_state(),
        closure_payload=closure,
        changed_files=[],
    )

    assert "missing_closure_type" in _error_codes(result)


def test_valid_program_state_plus_n2_current_frontier_passes(tmp_path):
    _write_valid_route_artifacts(tmp_path)

    report = _build_report_for_tmp_tree(tmp_path)

    assert report["verdict"] == "pass"
    assert report["current_frontier_route_id"] == "N2-SBMC-ENV-REDESIGN-001A"
    assert report["route_count"] == 2


def test_declared_current_frontier_ledger_entry_is_fail_closed(tmp_path):
    state_machine, validator = _validator()
    _write_valid_route_artifacts(tmp_path)
    artifact_dir = tmp_path / "artifacts" / "ROUTE-STATE-MACHINE-001A"
    route_dir = artifact_dir / "routes" / "K0-DUAL-TRACK-SUPERSESSION-001A"
    route_dir.mkdir(parents=True)
    validator.write_json(route_dir / "state.json", _valid_k0_parent_state())
    program_state = _valid_program_state()
    program_state["current_frontier_route_id"] = "K0-DUAL-TRACK-SUPERSESSION-001A"
    program_state["allowed_next_actions"] = ["bank_ordered_child_cards"]
    validator.write_json(artifact_dir / "program_state.json", program_state)

    missing_report = _build_report_for_tmp_tree(tmp_path)

    assert "current_frontier_ledger_missing" in _error_codes(missing_report)

    ledger_path = tmp_path / "docs" / "research" / "FSP-STAGE-LEDGER.md"
    ledger_path.parent.mkdir(parents=True)
    ledger_path.write_text(f"{state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX} details\n", encoding="utf-8")

    present_report = _build_report_for_tmp_tree(tmp_path)

    assert present_report["verdict"] == "pass"
    assert "docs/research/FSP-STAGE-LEDGER.md" in present_report["input_artifacts"]

    ledger_path.write_text(
        f"{state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX} first\n"
        f"{state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX} duplicate\n",
        encoding="utf-8",
    )

    duplicate_report = _build_report_for_tmp_tree(tmp_path)

    assert "current_frontier_k0_ledger_entry_not_unique" in _error_codes(duplicate_report)


def test_ready_current_frontier_requires_ready_and_preserved_ledger_entries(tmp_path):
    state_machine, validator = _validator()
    _write_valid_route_artifacts(tmp_path)
    artifact_dir = tmp_path / "artifacts" / "ROUTE-STATE-MACHINE-001A"
    route_dir = artifact_dir / "routes" / "K0-DUAL-TRACK-SUPERSESSION-001A"
    route_dir.mkdir(parents=True)
    validator.write_json(route_dir / "state.json", _valid_k0_ready_state())
    import json

    (route_dir / "events.jsonl").write_text(
        json.dumps(_valid_k0_red_field_event(), sort_keys=True)
        + "\n"
        + json.dumps(_valid_k0_red_field_correction_event(), sort_keys=True)
        + "\n"
        + json.dumps(_valid_k0_h0_admission_event(), sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    program_state = _valid_program_state()
    program_state["current_frontier_route_id"] = "K0-DUAL-TRACK-SUPERSESSION-001A"
    program_state["allowed_next_actions"] = list(state_machine.K0_READY_ALLOWED_ACTIONS)
    program_state["authorized_implementation_targets"] = list(
        state_machine.K0_READY_AUTHORIZED_IMPLEMENTATION_TARGETS
    )
    program_state["child_authorizations"] = deepcopy(state_machine.K0_READY_CHILD_AUTHORIZATIONS)
    program_state["red_field_addendum_pin"] = deepcopy(state_machine.K0_RED_FIELD_ADDENDUM_PIN)
    program_state["red_field_correction_pin"] = deepcopy(state_machine.K0_RED_FIELD_CORRECTION_PIN)
    program_state["h0_admission_contract_pin"] = deepcopy(state_machine.K0_H0_ADMISSION_PIN)
    program_state["effective_h0_authority"] = deepcopy(state_machine.K0_H0_EFFECTIVE_AUTHORITY)
    program_state["current_route_posture"] = "foundation_ready_h0_admission_002a_review_required"
    validator.write_json(artifact_dir / "program_state.json", program_state)
    ledger_path = tmp_path / "docs" / "research" / "FSP-STAGE-LEDGER.md"
    ledger_path.parent.mkdir(parents=True)
    repo_root = Path(__file__).resolve().parents[2]
    live_ledger_lines = (repo_root / "docs" / "research" / "FSP-STAGE-LEDGER.md").read_text(
        encoding="utf-8"
    ).splitlines()
    l020 = next(line for line in live_ledger_lines if line.startswith(state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX))
    l021 = next(line for line in live_ledger_lines if line.startswith(state_machine.K0_READY_LEDGER_ENTRY_PREFIX))
    l022 = next(line for line in live_ledger_lines if line.startswith(state_machine.K0_RED_FIELD_LEDGER_ENTRY_PREFIX))
    l023 = next(
        line
        for line in live_ledger_lines
        if line.startswith(state_machine.K0_RED_FIELD_CORRECTION_LEDGER_ENTRY_PREFIX)
    )
    ledger_path.write_text(
        f"{l020}\n"
        f"{l021}\n"
        f"{l022}\n"
        f"{l023}\n"
        f"{state_machine.K0_H0_ADMISSION_LEDGER_ENTRY_PREFIX} admission\n",
        encoding="utf-8",
    )

    present_report = _build_report_for_tmp_tree(tmp_path)

    present_codes = _error_codes(present_report)
    assert "current_frontier_ledger_entry_missing" not in present_codes
    assert "current_frontier_k0_preserved_ledger_line_drift" not in present_codes

    for rewritten_index in range(4):
        preserved_lines = [l020, l021, l022, l023]
        preserved_lines[rewritten_index] += " rewritten"
        ledger_path.write_text(
            "\n".join(preserved_lines)
            + f"\n{state_machine.K0_H0_ADMISSION_LEDGER_ENTRY_PREFIX} admission\n",
            encoding="utf-8",
        )
        rewritten_report = _build_report_for_tmp_tree(tmp_path)
        assert "current_frontier_k0_preserved_ledger_line_drift" in _error_codes(rewritten_report)

    ledger_path.write_text(
        f"{l020}\n{l021}\n{l022}\n{l023}\n",
        encoding="utf-8",
    )

    missing_ready_report = _build_report_for_tmp_tree(tmp_path)

    assert "current_frontier_ledger_entry_missing" in _error_codes(missing_ready_report)

    ledger_path.write_text(
        f"{l020}\n{l021}\n{l022}\n{l023}\n"
        f"{state_machine.K0_H0_ADMISSION_LEDGER_ENTRY_PREFIX} first\n"
        f"{state_machine.K0_H0_ADMISSION_LEDGER_ENTRY_PREFIX} duplicate\n",
        encoding="utf-8",
    )
    duplicate_report = _build_report_for_tmp_tree(tmp_path)
    assert "current_frontier_k0_ledger_entry_not_unique" in _error_codes(duplicate_report)


def test_missing_program_state_fails(tmp_path):
    _write_valid_route_artifacts(tmp_path, include_program_state=False)

    report = _build_report_for_tmp_tree(tmp_path)

    assert "missing_program_state_json" in _error_codes(report)
    assert report["verdict"] == "fail"


def test_missing_current_frontier_route_id_fails(tmp_path):
    _, validator = _validator()
    _write_valid_route_artifacts(tmp_path)
    program_state_path = tmp_path / "artifacts" / "ROUTE-STATE-MACHINE-001A" / "program_state.json"
    program_state = _valid_program_state()
    del program_state["current_frontier_route_id"]
    validator.write_json(program_state_path, program_state)

    report = _build_report_for_tmp_tree(tmp_path)

    assert "missing_current_frontier_route_id" in _error_codes(report)
    assert report["verdict"] == "fail"


def test_current_frontier_route_missing_fails(tmp_path):
    _, validator = _validator()
    _write_valid_route_artifacts(tmp_path)
    n2_route_dir = tmp_path / "artifacts" / "ROUTE-STATE-MACHINE-001A" / "routes" / "N2-SBMC-ENV-REDESIGN-001A"
    for child in n2_route_dir.iterdir():
        child.unlink()
    n2_route_dir.rmdir()

    report = _build_report_for_tmp_tree(tmp_path)

    assert "missing_current_frontier_route_directory" in _error_codes(report)
    assert report["verdict"] == "fail"


def test_current_frontier_tombstoned_fails(tmp_path):
    _, validator = _validator()
    _write_valid_route_artifacts(tmp_path)
    n2_state_path = (
        tmp_path
        / "artifacts"
        / "ROUTE-STATE-MACHINE-001A"
        / "routes"
        / "N2-SBMC-ENV-REDESIGN-001A"
        / "state.json"
    )
    validator.write_json(n2_state_path, _valid_n2_frontier_state(current_state="TOMBSTONED"))

    report = _build_report_for_tmp_tree(tmp_path)

    assert "current_frontier_route_tombstoned" in _error_codes(report)
    assert report["verdict"] == "fail"


def test_program_state_missing_allowed_next_actions_fails(tmp_path):
    _, validator = _validator()
    _write_valid_route_artifacts(tmp_path)
    program_state_path = tmp_path / "artifacts" / "ROUTE-STATE-MACHINE-001A" / "program_state.json"
    program_state = _valid_program_state()
    program_state["allowed_next_actions"] = []
    validator.write_json(program_state_path, program_state)

    report = _build_report_for_tmp_tree(tmp_path)

    assert "program_state_missing_allowed_next_actions" in _error_codes(report)
    assert report["verdict"] == "fail"


def test_program_state_missing_forbidden_next_actions_fails(tmp_path):
    _, validator = _validator()
    _write_valid_route_artifacts(tmp_path)
    program_state_path = tmp_path / "artifacts" / "ROUTE-STATE-MACHINE-001A" / "program_state.json"
    program_state = _valid_program_state()
    program_state["forbidden_next_actions"] = []
    validator.write_json(program_state_path, program_state)

    report = _build_report_for_tmp_tree(tmp_path)

    assert "program_state_missing_forbidden_next_actions" in _error_codes(report)
    assert report["verdict"] == "fail"


def test_program_state_missing_claim_ceiling_fails(tmp_path):
    _, validator = _validator()
    _write_valid_route_artifacts(tmp_path)
    program_state_path = tmp_path / "artifacts" / "ROUTE-STATE-MACHINE-001A" / "program_state.json"
    program_state = _valid_program_state()
    program_state["claim_ceiling"] = {}
    validator.write_json(program_state_path, program_state)

    report = _build_report_for_tmp_tree(tmp_path)

    assert "program_state_missing_claim_ceiling_max" in _error_codes(report)
    assert report["verdict"] == "fail"


@pytest.mark.parametrize(
    "authorization_key",
    ["mechanism_validity", "theory_pressure", "scoring", "experiment_execution"],
)
def test_registered_current_frontier_authorizing_forbidden_capability_fails(tmp_path, authorization_key: str):
    _, validator = _validator()
    _write_valid_route_artifacts(tmp_path)
    n2_state_path = (
        tmp_path
        / "artifacts"
        / "ROUTE-STATE-MACHINE-001A"
        / "routes"
        / "N2-SBMC-ENV-REDESIGN-001A"
        / "state.json"
    )
    n2_state = _valid_n2_frontier_state()
    n2_state["authorizations"][authorization_key] = True
    validator.write_json(n2_state_path, n2_state)

    report = _build_report_for_tmp_tree(tmp_path)

    assert "registered_current_frontier_authorizes_forbidden_capability" in _error_codes(report)
    assert report["verdict"] == "fail"


def test_n2_current_frontier_without_l014_source_evidence_fails(tmp_path):
    _, validator = _validator()
    _write_valid_route_artifacts(tmp_path)
    n2_state_path = (
        tmp_path
        / "artifacts"
        / "ROUTE-STATE-MACHINE-001A"
        / "routes"
        / "N2-SBMC-ENV-REDESIGN-001A"
        / "state.json"
    )
    n2_state = _valid_n2_frontier_state()
    n2_state["source_readback"] = {
        "ledger_entries": [
            {
                "entry": "L-013",
                "path": "docs/research/FSP-STAGE-LEDGER.md",
                "readback": "Frontier reuse scan only.",
            }
        ]
    }
    validator.write_json(n2_state_path, n2_state)

    report = _build_report_for_tmp_tree(tmp_path)

    assert "n2_frontier_missing_l014_source_readback" in _error_codes(report)
    assert report["verdict"] == "fail"
