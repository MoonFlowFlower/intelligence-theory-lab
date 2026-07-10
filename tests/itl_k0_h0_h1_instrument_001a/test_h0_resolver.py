from __future__ import annotations

import itertools

from itl_k0_h0_h1_instrument_001a.h0_registry import build_registry, panel_for
from itl_k0_h0_h1_instrument_001a.h0_resolver import resolve_comparator_panel, resolve_component_evidence
from itl_k0_h0_h1_instrument_001a.h0_schema import (
    CausalObservationRecord, CausalOutcome, ComparatorObservationRecord,
    ComparatorOutcome, ComparatorState, ComponentId, EvidenceState, PanelKind,
)


def test_component_reducer_full_scan_gives_invalid_precedence_under_every_permutation():
    registry = build_registry()
    component = ComponentId.MODEL
    arms = [row.arm for row in panel_for(registry, component, PanelKind.CAUSAL).arms]
    mapping = {arms[0]: CausalOutcome.WRONG_SIGN, arms[1]: CausalOutcome.EXPECTED_SIGN, arms[2]: CausalOutcome.INVALID}
    results = set()
    for order in itertools.permutations(arms):
        rows = [CausalObservationRecord(component, arm, mapping[arm]) for arm in order]
        results.add(resolve_component_evidence(component_id=component, mandatory_arm_ids=arms, observations=rows))
    assert results == {EvidenceState.INVALID_INSTRUMENT}


def test_component_reducer_requires_exact_mandatory_arm_set():
    registry = build_registry()
    component = ComponentId.ONLINE
    arms = [row.arm for row in panel_for(registry, component, PanelKind.CAUSAL).arms]
    rows = [CausalObservationRecord(component, arms[0], CausalOutcome.EXPECTED_SIGN)]
    assert resolve_component_evidence(component_id=component, mandatory_arm_ids=arms, observations=rows) is EvidenceState.INVALID_INSTRUMENT


def test_comparator_reducer_is_component_local_and_order_invariant():
    registry = build_registry()
    component = ComponentId.MEMORY
    panel = PanelKind.CONTROL
    arms = [row.arm for row in panel_for(registry, component, panel).arms]
    mapping = {arm: ComparatorOutcome.CANDIDATE_SUPERIOR for arm in arms}
    mapping[arms[-1]] = ComparatorOutcome.COMPARATOR_SUPERIOR
    orders = (arms, list(reversed(arms)), arms[1:] + arms[:1])
    states = {
        resolve_comparator_panel(
            component_id=component,
            panel=panel,
            required_arm_ids=arms,
            observations=[ComparatorObservationRecord(component, panel, arm, mapping[arm]) for arm in order],
        )
        for order in orders
    }
    assert states == {ComparatorState.DOMINATED}
