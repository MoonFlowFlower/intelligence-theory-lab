from __future__ import annotations

from copy import deepcopy

import pytest

from itl_k0_h0_h1_instrument_001a.h0_registry import build_registry
from itl_k0_h0_h1_instrument_001a.h0_schema import ComponentId, H0Registry, PanelKind


def test_registry_typed_round_trip_preserves_five_components_and_four_panels():
    registry = build_registry()
    restored = H0Registry.from_dict(registry.to_dict())
    assert {row.component_id for row in restored.components} == set(ComponentId)
    assert all({panel.panel for panel in row.panels} == set(PanelKind) for row in restored.components)
    assert restored.v_special_mode == "derived_claim_admissibility_predicate_not_evidence_axis"


def test_missing_normative_atomic_field_fails_typed_parse():
    payload = build_registry().to_dict()
    del payload["components"][0]["panels"][0]["arms"][0]["estimand"]
    with pytest.raises(ValueError):
        H0Registry.from_dict(payload)


def test_set_like_arm_order_is_not_schema_order_dependent():
    payload = deepcopy(build_registry().to_dict())
    payload["components"][0]["panels"][0]["arms"].reverse()
    assert H0Registry.from_dict(payload).to_dict()["components"][0]["panels"][0]["arms"]
