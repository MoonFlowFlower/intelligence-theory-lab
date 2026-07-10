from __future__ import annotations

from .h0_schema import (
    ArmRole,
    AtomicContrastSpec,
    ComponentId,
    ComponentSpec,
    H0Registry,
    PANEL_ROLES,
    PanelKind,
    PanelSpec,
    PowerSpec,
)


COMPONENT_FAMILIES = {
    ComponentId.MODEL: "delayed_consequence_source_reliability",
    ComponentId.ONLINE: "online_feedback_adaptation",
    ComponentId.REPLAY: "matched_replay_contribution",
    ComponentId.MEMORY: "source_memory_lineage",
    ComponentId.TRANSFER: "heldout_carrier_transfer",
}

COMMON_INTEGRITY = (
    "access_parity_audit",
    "provenance_lineage_check",
    "global_leakage_positive_control",
    "rng_registry_audit",
    "interface_capability_audit",
)

COMPONENT_PANEL_ARMS: dict[ComponentId, dict[PanelKind, tuple[str, ...]]] = {
    ComponentId.MODEL: {
        PanelKind.CAUSAL: ("planner_bypass", "checkpoint_swap", "prediction_counterfactual"),
        PanelKind.CONTROL: (
            "observation_only", "window_history", "exact_lookup", "nearest_neighbor",
            "graph_lookup", "transition_table", "successor_map", "count_table",
            "fsm_planner", "episodic_traversal", "candidate_own_rule_amortized",
        ),
        PanelKind.RIVAL: ("tabular_transition_rival", "online_compositional_rival", "drift_aware_replay_rival"),
        PanelKind.INTEGRITY: COMMON_INTEGRITY,
    },
    ComponentId.ONLINE: {
        PanelKind.CAUSAL: ("no_update", "shuffled_outcome"),
        PanelKind.CONTROL: ("candidate_own_rule_batched", "candidate_own_rule_amortized", "same_feedback_budget_table_history_learner"),
        PanelKind.RIVAL: ("online_compositional_rival", "drift_aware_replay_rival"),
        PanelKind.INTEGRITY: COMMON_INTEGRITY,
    },
    ComponentId.REPLAY: {
        PanelKind.CAUSAL: ("matched_replay_off",),
        PanelKind.CONTROL: (
            "window_history", "episodic_traversal", "graph_lookup", "transition_table",
            "successor_map", "count_table", "fsm_planner", "matched_no_replay_amortized_learner",
        ),
        PanelKind.RIVAL: ("drift_aware_replay_rival",),
        PanelKind.INTEGRITY: ("corrupted_replay_detector",) + COMMON_INTEGRITY,
    },
    ComponentId.MEMORY: {
        PanelKind.CAUSAL: ("memory_read_off", "memory_zero", "source_deletion", "history_replacement"),
        PanelKind.CONTROL: (
            "recency", "summary", "rag", "exact_lookup", "nearest_neighbor", "window_history",
            "graph_lookup", "transition_table", "successor_map", "count_table", "fsm_planner",
            "episodic_traversal",
        ),
        PanelKind.RIVAL: ("tabular_transition_rival", "online_compositional_rival", "drift_aware_replay_rival"),
        PanelKind.INTEGRITY: COMMON_INTEGRITY,
    },
    ComponentId.TRANSFER: {
        PanelKind.CAUSAL: ("fresh_init", "from_scratch", "checkpoint_only", "replay_reset", "memory_reset", "full_carryover"),
        PanelKind.CONTROL: ("equal_budget_persistent_history_carrier", "equal_budget_persistent_cache_carrier", "equal_budget_persistent_batched_carrier"),
        PanelKind.RIVAL: ("online_compositional_rival", "drift_aware_replay_rival"),
        PanelKind.INTEGRITY: COMMON_INTEGRITY,
    },
}


def _signatures(panel: PanelKind, component: ComponentId, arm_id: str) -> tuple[str, str, str, str]:
    prefix = f"{component.value}:{arm_id}"
    if panel is PanelKind.CAUSAL:
        return (
            "expected_sign_contribution",
            f"{prefix}:powered_effect_matches_frozen_expected_sign",
            f"{prefix}:powered_no_contribution_or_wrong_sign",
            f"{prefix}:invalid_underpowered_or_not_started",
        )
    if panel in (PanelKind.CONTROL, PanelKind.RIVAL):
        return (
            "candidate_superior",
            f"{prefix}:powered_candidate_superiority",
            f"{prefix}:powered_parity_ceiling_or_comparator_superiority",
            f"{prefix}:missing_invalid_or_underpowered",
        )
    return (
        "integrity_valid",
        f"{prefix}:audit_valid",
        f"{prefix}:audit_invalid",
        f"{prefix}:audit_missing_or_underpowered",
    )


def _atomic(component: ComponentId, panel: PanelKind, arm_id: str) -> AtomicContrastSpec:
    expected, success, failure, ambiguous = _signatures(panel, component, arm_id)
    family = COMPONENT_FAMILIES[component]
    protocol = f"{family}::{panel.value}::{arm_id}::protocol_v1"
    seed_block = f"seed::{component.value.lower()}::{panel.value}::{arm_id}::001"
    full_arm = f"{component.value}::candidate_full"
    intervention_arm = f"{component.value}::{arm_id}::intervention"
    reference_arm = f"{component.value}::{arm_id}::reference"
    resolver = {
        PanelKind.CAUSAL: "resolve_component_evidence.v1",
        PanelKind.CONTROL: "resolve_comparator_panel.control.v1",
        PanelKind.RIVAL: "resolve_comparator_panel.rival.v1",
        PanelKind.INTEGRITY: "resolve_integrity_dependency.v1",
    }[panel]
    return AtomicContrastSpec(
        atomic_contrast_id=f"atomic::{component.value}::{panel.value}::{arm_id}",
        component=component,
        panel=panel,
        arm=arm_id,
        role=PANEL_ROLES[panel],
        full_arm=full_arm,
        intervention_arm=intervention_arm,
        reference_arm=reference_arm,
        family_id=family,
        protocol_id=protocol,
        estimand=f"delta::{component.value}::{panel.value}::{arm_id}",
        expected_sign=expected,
        success_signature=success,
        failure_signature=failure,
        ambiguous_signature=ambiguous,
        power_spec=PowerSpec(0.1, 0.8, 32, seed_block),
        seed_block_id=seed_block,
        blast_radius="global_integrity" if arm_id in {"global_leakage_positive_control", "provenance_lineage_check"} else f"component::{component.value}",
        resolver_id=resolver,
    )


def build_registry() -> H0Registry:
    components: list[ComponentSpec] = []
    for component in ComponentId:
        panels = tuple(
            PanelSpec(
                panel=panel,
                mandatory=True,
                arms=tuple(_atomic(component, panel, arm_id) for arm_id in COMPONENT_PANEL_ARMS[component][panel]),
            )
            for panel in PanelKind
        )
        components.append(ComponentSpec(component, panels))
    return H0Registry(
        schema_version="itl.k0.h0.code_first_prebank.001a.v1",
        registry_id="ITL-K0-H0-CODE-FIRST-PREBANK-001A::canonical-registry",
        components=tuple(components),
        v_special_mode="derived_claim_admissibility_predicate_not_evidence_axis",
        metadata={"note": "non-semantic human-readable registry annotation"},
    )


def all_atomic_specs(registry: H0Registry | None = None) -> tuple[AtomicContrastSpec, ...]:
    source = registry or build_registry()
    return tuple(arm for component in source.components for panel in component.panels for arm in panel.arms)


def panel_for(registry: H0Registry, component_id: ComponentId, panel: PanelKind) -> PanelSpec:
    component = next(row for row in registry.components if row.component_id is component_id)
    return next(row for row in component.panels if row.panel is panel)
