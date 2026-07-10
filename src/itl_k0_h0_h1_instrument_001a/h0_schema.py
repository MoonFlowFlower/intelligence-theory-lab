from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ComponentId(str, Enum):
    MODEL = "V_model"
    ONLINE = "V_online"
    REPLAY = "V_replay"
    MEMORY = "V_memory"
    TRANSFER = "V_transfer"


class PanelKind(str, Enum):
    CAUSAL = "causal"
    CONTROL = "control"
    RIVAL = "rival"
    INTEGRITY = "integrity"


class ArmRole(str, Enum):
    CAUSAL_ABLATION = "CAUSAL_ABLATION"
    SHORTCUT_CONTROL = "SHORTCUT_CONTROL"
    RIVAL = "RIVAL"
    INTEGRITY_CONTROL = "INTEGRITY_CONTROL"


class EvidenceState(str, Enum):
    NOT_TESTED = "NOT_TESTED"
    INVALID_INSTRUMENT = "INVALID_INSTRUMENT"
    ABSENT = "ABSENT"
    PRESENT_BOUNDED = "PRESENT_BOUNDED"


class ComparatorState(str, Enum):
    NOT_RUN = "NOT_RUN"
    INCONCLUSIVE = "INCONCLUSIVE"
    DOMINATED = "DOMINATED"
    EQUIVALENT = "EQUIVALENT"
    SATURATED = "SATURATED"
    SEPARATED = "SEPARATED"


class CausalOutcome(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    INVALID = "INVALID"
    UNDERPOWERED = "UNDERPOWERED"
    EXPECTED_SIGN = "EXPECTED_SIGN"
    NO_CONTRIBUTION = "NO_CONTRIBUTION"
    WRONG_SIGN = "WRONG_SIGN"


class ComparatorOutcome(str, Enum):
    NOT_RUN = "NOT_RUN"
    INVALID = "INVALID"
    UNDERPOWERED = "UNDERPOWERED"
    CANDIDATE_SUPERIOR = "CANDIDATE_SUPERIOR"
    PARITY = "PARITY"
    CEILING = "CEILING"
    COMPARATOR_SUPERIOR = "COMPARATOR_SUPERIOR"


PANEL_ROLES = {
    PanelKind.CAUSAL: ArmRole.CAUSAL_ABLATION,
    PanelKind.CONTROL: ArmRole.SHORTCUT_CONTROL,
    PanelKind.RIVAL: ArmRole.RIVAL,
    PanelKind.INTEGRITY: ArmRole.INTEGRITY_CONTROL,
}


def _required(mapping: dict[str, Any], key: str, expected_type: type | tuple[type, ...]) -> Any:
    if key not in mapping or not isinstance(mapping[key], expected_type):
        label = " or ".join(item.__name__ for item in expected_type) if isinstance(expected_type, tuple) else expected_type.__name__
        raise ValueError(f"{key} must be {label}")
    return mapping[key]


@dataclass(frozen=True)
class PowerSpec:
    sesoi: float
    target_power: float
    fixed_seed_count: int
    seed_block_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "sesoi": self.sesoi,
            "target_power": self.target_power,
            "fixed_seed_count": self.fixed_seed_count,
            "seed_block_id": self.seed_block_id,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PowerSpec":
        if set(payload) != {"sesoi", "target_power", "fixed_seed_count", "seed_block_id"}:
            raise ValueError("power_spec fields are incomplete or unexpected")
        sesoi = _required(payload, "sesoi", (int, float))
        target = _required(payload, "target_power", (int, float))
        count = _required(payload, "fixed_seed_count", int)
        block = _required(payload, "seed_block_id", str)
        if isinstance(sesoi, bool) or isinstance(target, bool) or count <= 0:
            raise ValueError("power_spec numeric fields are invalid")
        if float(sesoi) <= 0 or not 0 < float(target) <= 1 or not block:
            raise ValueError("power_spec bounds are invalid")
        return cls(float(sesoi), float(target), count, block)


@dataclass(frozen=True)
class AtomicContrastSpec:
    atomic_contrast_id: str
    component: ComponentId
    panel: PanelKind
    arm: str
    role: ArmRole
    full_arm: str
    intervention_arm: str
    reference_arm: str
    family_id: str
    protocol_id: str
    estimand: str
    expected_sign: str
    success_signature: str
    failure_signature: str
    ambiguous_signature: str
    power_spec: PowerSpec
    seed_block_id: str
    blast_radius: str
    resolver_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "atomic_contrast_id": self.atomic_contrast_id,
            "component": self.component.value,
            "panel": self.panel.value,
            "arm": self.arm,
            "role": self.role.value,
            "full_arm": self.full_arm,
            "intervention_arm": self.intervention_arm,
            "reference_arm": self.reference_arm,
            "family_id": self.family_id,
            "protocol_id": self.protocol_id,
            "estimand": self.estimand,
            "expected_sign": self.expected_sign,
            "success_signature": self.success_signature,
            "failure_signature": self.failure_signature,
            "ambiguous_signature": self.ambiguous_signature,
            "power_spec": self.power_spec.to_dict(),
            "seed_block_id": self.seed_block_id,
            "blast_radius": self.blast_radius,
            "resolver_id": self.resolver_id,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AtomicContrastSpec":
        expected = {
            "atomic_contrast_id", "component", "panel", "arm", "role", "full_arm",
            "intervention_arm", "reference_arm", "family_id", "protocol_id", "estimand",
            "expected_sign", "success_signature", "failure_signature", "ambiguous_signature",
            "power_spec", "seed_block_id", "blast_radius", "resolver_id",
        }
        if set(payload) != expected:
            raise ValueError("atomic spec fields are incomplete or unexpected")
        strings = {key: _required(payload, key, str) for key in expected - {"power_spec"}}
        if any(not value for value in strings.values()):
            raise ValueError("atomic spec strings must be non-empty")
        component = ComponentId(strings["component"])
        panel = PanelKind(strings["panel"])
        role = ArmRole(strings["role"])
        if role is not PANEL_ROLES[panel]:
            raise ValueError("atomic spec role does not match panel")
        return cls(
            atomic_contrast_id=strings["atomic_contrast_id"],
            component=component,
            panel=panel,
            arm=strings["arm"],
            role=role,
            full_arm=strings["full_arm"],
            intervention_arm=strings["intervention_arm"],
            reference_arm=strings["reference_arm"],
            family_id=strings["family_id"],
            protocol_id=strings["protocol_id"],
            estimand=strings["estimand"],
            expected_sign=strings["expected_sign"],
            success_signature=strings["success_signature"],
            failure_signature=strings["failure_signature"],
            ambiguous_signature=strings["ambiguous_signature"],
            power_spec=PowerSpec.from_dict(_required(payload, "power_spec", dict)),
            seed_block_id=strings["seed_block_id"],
            blast_radius=strings["blast_radius"],
            resolver_id=strings["resolver_id"],
        )


@dataclass(frozen=True)
class PanelSpec:
    panel: PanelKind
    mandatory: bool
    arms: tuple[AtomicContrastSpec, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"panel": self.panel.value, "mandatory": self.mandatory, "arms": [a.to_dict() for a in self.arms]}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PanelSpec":
        if set(payload) != {"panel", "mandatory", "arms"}:
            raise ValueError("panel fields are incomplete or unexpected")
        panel = PanelKind(_required(payload, "panel", str))
        mandatory = _required(payload, "mandatory", bool)
        arms_payload = _required(payload, "arms", list)
        if not arms_payload:
            raise ValueError("panel arms must be non-empty")
        arms = tuple(AtomicContrastSpec.from_dict(_required(row, "atomic_spec", dict)) if set(row) == {"atomic_spec"} else AtomicContrastSpec.from_dict(row) for row in arms_payload)
        if any(arm.panel is not panel for arm in arms):
            raise ValueError("panel contains an arm from another panel")
        return cls(panel, mandatory, arms)


@dataclass(frozen=True)
class ComponentSpec:
    component_id: ComponentId
    panels: tuple[PanelSpec, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"component_id": self.component_id.value, "panels": [p.to_dict() for p in self.panels]}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ComponentSpec":
        if set(payload) != {"component_id", "panels"}:
            raise ValueError("component fields are incomplete or unexpected")
        component = ComponentId(_required(payload, "component_id", str))
        panels = tuple(PanelSpec.from_dict(row) for row in _required(payload, "panels", list))
        if {panel.panel for panel in panels} != set(PanelKind):
            raise ValueError("component must contain all four panels exactly once")
        if any(arm.component is not component for panel in panels for arm in panel.arms):
            raise ValueError("component contains a foreign atomic spec")
        return cls(component, panels)


@dataclass(frozen=True)
class H0Registry:
    schema_version: str
    registry_id: str
    components: tuple[ComponentSpec, ...]
    v_special_mode: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "registry_id": self.registry_id,
            "components": [component.to_dict() for component in self.components],
            "v_special_mode": self.v_special_mode,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "H0Registry":
        if set(payload) != {"schema_version", "registry_id", "components", "v_special_mode", "metadata"}:
            raise ValueError("registry fields are incomplete or unexpected")
        schema = _required(payload, "schema_version", str)
        registry_id = _required(payload, "registry_id", str)
        mode = _required(payload, "v_special_mode", str)
        metadata = _required(payload, "metadata", dict)
        components = tuple(ComponentSpec.from_dict(row) for row in _required(payload, "components", list))
        if schema != "itl.k0.h0.code_first_prebank.001a.v1" or not registry_id:
            raise ValueError("registry identity is invalid")
        if {c.component_id for c in components} != set(ComponentId) or len(components) != len(ComponentId):
            raise ValueError("registry must contain the exact five components")
        if mode != "derived_claim_admissibility_predicate_not_evidence_axis":
            raise ValueError("V_special mode is invalid")
        return cls(schema, registry_id, components, mode, metadata)


@dataclass(frozen=True)
class CausalObservationRecord:
    component_id: ComponentId
    arm_id: str
    outcome: CausalOutcome


@dataclass(frozen=True)
class ComparatorObservationRecord:
    component_id: ComponentId
    panel: PanelKind
    arm_id: str
    outcome: ComparatorOutcome
