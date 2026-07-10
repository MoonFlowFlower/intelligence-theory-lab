from __future__ import annotations

from copy import deepcopy

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
            "required_entry_prefix": state_machine.K0_READY_LEDGER_ENTRY_PREFIX,
            "preserved_entry_prefixes": [state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX],
        },
    }
    return state


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
    state[field] = "drifted" if field == "phase" else ["EGO-K0-FOUNDATION-001A"]

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
    program_state = _valid_program_state()
    program_state["current_frontier_route_id"] = "K0-DUAL-TRACK-SUPERSESSION-001A"
    program_state["allowed_next_actions"] = list(state_machine.K0_READY_ALLOWED_ACTIONS)
    validator.write_json(artifact_dir / "program_state.json", program_state)
    ledger_path = tmp_path / "docs" / "research" / "FSP-STAGE-LEDGER.md"
    ledger_path.parent.mkdir(parents=True)
    ledger_path.write_text(
        f"{state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX} parent\n"
        f"{state_machine.K0_READY_LEDGER_ENTRY_PREFIX} ready\n",
        encoding="utf-8",
    )

    present_report = _build_report_for_tmp_tree(tmp_path)

    assert present_report["verdict"] == "pass"

    ledger_path.write_text(
        f"{state_machine.K0_PARENT_LEDGER_ENTRY_PREFIX} parent\n",
        encoding="utf-8",
    )

    missing_ready_report = _build_report_for_tmp_tree(tmp_path)

    assert "current_frontier_ledger_entry_missing" in _error_codes(missing_ready_report)


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
