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


def test_state_and_closure_enums_are_exact():
    state_machine, _ = _validator()

    assert state_machine.ROUTE_STATES == EXPECTED_ROUTE_STATES
    assert state_machine.CLOSURE_TYPES == EXPECTED_CLOSURE_TYPES


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
