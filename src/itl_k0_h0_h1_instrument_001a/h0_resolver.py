from __future__ import annotations

from collections.abc import Iterable, Sequence

from .h0_schema import (
    CausalObservationRecord,
    CausalOutcome,
    ComparatorObservationRecord,
    ComparatorOutcome,
    ComparatorState,
    ComponentId,
    EvidenceState,
    PanelKind,
)


def resolve_component_evidence(
    *,
    component_id: ComponentId,
    mandatory_arm_ids: Sequence[str],
    observations: Iterable[CausalObservationRecord],
) -> EvidenceState:
    """Total full-scan reducer; input order cannot select a first-hit verdict."""
    rows = tuple(observations)
    if any(row.component_id is not component_id for row in rows):
        return EvidenceState.INVALID_INSTRUMENT
    expected = set(mandatory_arm_ids)
    by_arm = {row.arm_id: row for row in rows}
    if not expected or set(by_arm) != expected or len(by_arm) != len(rows):
        return EvidenceState.INVALID_INSTRUMENT
    outcomes = {row.outcome for row in rows}
    if CausalOutcome.INVALID in outcomes or CausalOutcome.UNDERPOWERED in outcomes:
        return EvidenceState.INVALID_INSTRUMENT
    if CausalOutcome.NO_CONTRIBUTION in outcomes or CausalOutcome.WRONG_SIGN in outcomes:
        return EvidenceState.ABSENT
    if CausalOutcome.NOT_STARTED in outcomes:
        return EvidenceState.NOT_TESTED
    if outcomes == {CausalOutcome.EXPECTED_SIGN}:
        return EvidenceState.PRESENT_BOUNDED
    return EvidenceState.INVALID_INSTRUMENT


def resolve_comparator_panel(
    *,
    component_id: ComponentId,
    panel: PanelKind,
    required_arm_ids: Sequence[str],
    observations: Iterable[ComparatorObservationRecord],
) -> ComparatorState:
    if panel not in (PanelKind.CONTROL, PanelKind.RIVAL):
        return ComparatorState.INCONCLUSIVE
    rows = tuple(observations)
    if any(row.component_id is not component_id or row.panel is not panel for row in rows):
        return ComparatorState.INCONCLUSIVE
    expected = set(required_arm_ids)
    by_arm = {row.arm_id: row for row in rows}
    if not rows or not expected or set(by_arm) != expected or len(by_arm) != len(rows):
        return ComparatorState.NOT_RUN
    outcomes = {row.outcome for row in rows}
    if ComparatorOutcome.COMPARATOR_SUPERIOR in outcomes:
        return ComparatorState.DOMINATED
    if ComparatorOutcome.PARITY in outcomes:
        return ComparatorState.EQUIVALENT if panel is PanelKind.CONTROL else ComparatorState.SATURATED
    if ComparatorOutcome.CEILING in outcomes:
        return ComparatorState.EQUIVALENT if panel is PanelKind.CONTROL else ComparatorState.SATURATED
    if ComparatorOutcome.INVALID in outcomes or ComparatorOutcome.UNDERPOWERED in outcomes:
        return ComparatorState.INCONCLUSIVE
    if ComparatorOutcome.NOT_RUN in outcomes:
        return ComparatorState.NOT_RUN
    if outcomes == {ComparatorOutcome.CANDIDATE_SUPERIOR}:
        return ComparatorState.SEPARATED
    return ComparatorState.INCONCLUSIVE


def resolve_specialness_admissibility(
    *,
    component_states: dict[ComponentId, EvidenceState],
    integrity_valid: bool,
    control_states: dict[ComponentId, ComparatorState],
    rival_states: dict[ComponentId, ComparatorState],
) -> tuple[bool, str]:
    if set(component_states) != set(ComponentId):
        return False, "component_set_incomplete"
    if any(state is not EvidenceState.PRESENT_BOUNDED for state in component_states.values()):
        return False, "component_not_present_bounded"
    if not integrity_valid:
        return False, "integrity_invalid"
    if set(control_states) != set(ComponentId) or any(state is not ComparatorState.SEPARATED for state in control_states.values()):
        return False, "control_not_separated"
    if set(rival_states) != set(ComponentId) or any(state is not ComparatorState.SEPARATED for state in rival_states.values()):
        return False, "rival_not_separated"
    return True, "admissible_bounded"
