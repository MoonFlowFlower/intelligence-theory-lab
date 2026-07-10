from __future__ import annotations

from itl_k0_h0_h1_instrument_001a.h0_registry import all_atomic_specs, build_registry, panel_for
from itl_k0_h0_h1_instrument_001a.h0_schema import ComponentId, PanelKind
from itl_k0_h0_h1_instrument_001a.h0_validation import validate_registry_payload


def test_atomic_specs_are_generated_one_to_one_from_real_panel_arms():
    registry = build_registry()
    specs = all_atomic_specs(registry)
    tuples = {(row.component, row.panel, row.arm) for row in specs}
    expected = {
        (component, panel, arm.arm)
        for component in ComponentId
        for panel in PanelKind
        for arm in panel_for(registry, component, panel).arms
    }
    assert tuples == expected
    assert len(specs) == len(expected)
    assert len({row.atomic_contrast_id for row in specs}) == len(specs)


def test_atomic_specs_have_resolved_non_placeholder_execution_fields():
    specs = all_atomic_specs(build_registry())
    for row in specs:
        payload = row.to_dict()
        assert all(payload[key] for key in (
            "full_arm", "intervention_arm", "reference_arm", "family_id", "protocol_id",
            "estimand", "expected_sign", "success_signature", "failure_signature",
            "ambiguous_signature", "seed_block_id", "blast_radius", "resolver_id",
        ))
        assert "placeholder" not in str(payload).lower()
    assert validate_registry_payload(build_registry().to_dict())["accepted"] is True


def test_atomic_count_is_computed_not_a_frozen_ninety_literal():
    registry = build_registry()
    computed = sum(len(panel.arms) for component in registry.components for panel in component.panels)
    assert len(all_atomic_specs(registry)) == computed
    assert computed > 0
