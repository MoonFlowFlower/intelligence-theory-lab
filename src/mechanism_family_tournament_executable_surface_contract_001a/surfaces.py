from __future__ import annotations

from typing import Any


class SurfaceContractViolation(ValueError):
    def __init__(self, reason: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.details = details or {}


COMMON_FORBIDDEN_VISIBLE_FIELDS = {
    "target",
    "target_label",
    "answer",
    "answer_key",
    "gold",
    "label",
    "heldout_label",
    "target_source",
    "generator_target",
    "oracle_target",
    "score",
}


def _visible_observation(record: dict[str, Any]) -> dict[str, Any]:
    observation = record.get("observation")
    if not isinstance(observation, dict):
        raise SurfaceContractViolation("observation_not_object")
    return observation


def enforce_visible_boundary(
    record: dict[str, Any],
    forbidden_fields: list[str] | tuple[str, ...] | set[str],
) -> None:
    observation = _visible_observation(record)
    forbidden = COMMON_FORBIDDEN_VISIBLE_FIELDS | set(forbidden_fields)
    visible_forbidden = sorted(field for field in observation if field in forbidden)
    if visible_forbidden:
        raise SurfaceContractViolation(
            "forbidden_target_derived_field_visible",
            {"visible_forbidden_fields": visible_forbidden},
        )


def _target_source(record: dict[str, Any], key: str) -> str:
    source = record.get("target_source")
    if not isinstance(source, dict):
        raise SurfaceContractViolation("target_source_not_object")
    value = source.get(key)
    if not isinstance(value, str) or not value:
        raise SurfaceContractViolation("target_source_missing_value", {"key": key})
    return value


def resolve_causal_world_model_control_target(record: dict[str, Any]) -> str:
    enforce_visible_boundary(
        record,
        {
            "intervention_consequence_class",
            "consequence_label",
            "state_action_answer_key",
            "transition_target",
        },
    )
    return _target_source(record, "intervention_consequence_class")


def resolve_jepa_like_latent_prediction_target(record: dict[str, Any]) -> str:
    enforce_visible_boundary(
        record,
        {
            "future_transition_class",
            "future_state_id",
            "latent_answer_key",
            "transition_label",
        },
    )
    return _target_source(record, "future_transition_class")


def resolve_replay_consolidation_adaptation_target(record: dict[str, Any]) -> str:
    enforce_visible_boundary(
        record,
        {
            "post_replay_behavior_class",
            "stored_answer_hash",
            "replay_answer_key",
            "episode_target",
        },
    )
    return _target_source(record, "post_replay_behavior_class")


def resolve_self_boundary_controllability_model_target(record: dict[str, Any]) -> str:
    enforce_visible_boundary(
        record,
        {
            "controllability_attribution_class",
            "self_other_label",
            "role_label",
            "boundary_answer_key",
        },
    )
    return _target_source(record, "controllability_attribution_class")


def resolve_viability_value_gated_prediction_action_loop_target(record: dict[str, Any]) -> str:
    enforce_visible_boundary(
        record,
        {
            "delayed_viability_action_class",
            "viability_label",
            "risk_label",
            "reward_answer_key",
        },
    )
    return _target_source(record, "delayed_viability_action_class")


def resolve_social_latent_inference_without_partner_id_lookup_target(record: dict[str, Any]) -> str:
    enforce_visible_boundary(
        record,
        {
            "latent_response_class",
            "partner_id",
            "partner_key",
            "anonymized_partner_key",
            "profile_id",
            "preference_table",
            "social_answer_key",
        },
    )
    return _target_source(record, "latent_response_class")


def exact_match_accuracy(predictions: list[str], targets: list[str]) -> float:
    if not predictions or len(predictions) != len(targets):
        raise SurfaceContractViolation("metric_input_length_mismatch")
    matches = sum(1 for predicted, target in zip(predictions, targets) if predicted == target)
    return matches / len(targets)
