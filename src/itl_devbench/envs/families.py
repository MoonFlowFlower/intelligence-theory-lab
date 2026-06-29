from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

REQUIRED_FAMILY_IDS = [
    "aliased_food_v1",
    "delayed_poison_v1",
    "contextual_hazard_v1",
    "rule_reversal_return_v1",
    "info_risk_tradeoff_v1",
]

DIMENSION_SPACE: Dict[str, list[str]] = {
    "D0_layout": ["fixed", "procedural", "heldout_layout"],
    "D1_observability": ["full", "local", "aliased_local"],
    "D2_latent_affordance": [
        "none",
        "hidden_object_property",
        "context_dependent_property",
        "compositional_property",
    ],
    "D3_delay": ["immediate", "short_delay_3", "long_delay_7_15"],
    "D4_rule_shift": ["none", "episode_shift", "mid_episode_shift", "old_rule_return"],
    "D5_resource_tradeoff": ["none", "energy_health_tradeoff", "risk_information_tradeoff"],
    "D6_active_experiment": ["none", "inspect_required", "safe_probe_required", "hypothesis_test_required"],
    "D7_composition": ["single_object", "two_object_interaction", "object_terrain_context"],
}

FAMILY_DIMENSIONS: Dict[str, Dict[str, str]] = {
    "aliased_food_v1": {
        "D0_layout": "procedural",
        "D1_observability": "aliased_local",
        "D2_latent_affordance": "hidden_object_property",
        "D3_delay": "immediate",
        "D4_rule_shift": "none",
        "D5_resource_tradeoff": "energy_health_tradeoff",
        "D6_active_experiment": "inspect_required",
        "D7_composition": "single_object",
    },
    "delayed_poison_v1": {
        "D0_layout": "procedural",
        "D1_observability": "local",
        "D2_latent_affordance": "hidden_object_property",
        "D3_delay": "long_delay_7_15",
        "D4_rule_shift": "none",
        "D5_resource_tradeoff": "energy_health_tradeoff",
        "D6_active_experiment": "safe_probe_required",
        "D7_composition": "single_object",
    },
    "contextual_hazard_v1": {
        "D0_layout": "procedural",
        "D1_observability": "local",
        "D2_latent_affordance": "context_dependent_property",
        "D3_delay": "immediate",
        "D4_rule_shift": "episode_shift",
        "D5_resource_tradeoff": "risk_information_tradeoff",
        "D6_active_experiment": "inspect_required",
        "D7_composition": "object_terrain_context",
    },
    "rule_reversal_return_v1": {
        "D0_layout": "procedural",
        "D1_observability": "local",
        "D2_latent_affordance": "context_dependent_property",
        "D3_delay": "immediate",
        "D4_rule_shift": "old_rule_return",
        "D5_resource_tradeoff": "energy_health_tradeoff",
        "D6_active_experiment": "hypothesis_test_required",
        "D7_composition": "two_object_interaction",
    },
    "info_risk_tradeoff_v1": {
        "D0_layout": "procedural",
        "D1_observability": "aliased_local",
        "D2_latent_affordance": "hidden_object_property",
        "D3_delay": "short_delay_3",
        "D4_rule_shift": "none",
        "D5_resource_tradeoff": "risk_information_tradeoff",
        "D6_active_experiment": "safe_probe_required",
        "D7_composition": "single_object",
    },
}

TARGET_PRESSURE: Dict[str, list[str]] = {
    "aliased_food_v1": ["partial_observability", "perceptual_aliasing", "obs_only_killer", "graph_cache_stress"],
    "delayed_poison_v1": ["delayed_consequence", "temporal_credit_assignment", "short_horizon_cache_stress"],
    "contextual_hazard_v1": ["context_dependent_affordance", "generic_fsm_killer", "object_context_interaction"],
    "rule_reversal_return_v1": ["adaptation_lag", "backward_retention", "old_rule_return"],
    "info_risk_tradeoff_v1": ["active_experimentation", "uncertainty_reduction", "resource_tradeoff"],
}


@dataclass(frozen=True)
class TaskFamilyInstance:
    family_id: str
    split: str
    seed: int
    rule_seed: int
    stage_index: int
    instance_id: str
    dimensions: Dict[str, str]
    target_pressure: list[str]
    public_observation: Dict[str, Any]
    observation_signature: str
    hidden_rule: Dict[str, Any]
    oracle_script: list[str]

    def to_event_fields(self) -> Dict[str, Any]:
        return {
            "split": self.split,
            "family_id": self.family_id,
            "family_instance_id": self.instance_id,
            "dimension_combo": [self.dimensions[key] for key in sorted(self.dimensions)],
            "target_pressure": list(self.target_pressure),
        }

    def to_spec_record(self) -> Dict[str, Any]:
        return {
            **self.to_event_fields(),
            "seed": self.seed,
            "rule_seed": self.rule_seed,
            "stage_index": self.stage_index,
            "dimensions": dict(self.dimensions),
            "public_observation": self.public_observation,
            "observation_signature": self.observation_signature,
        }
