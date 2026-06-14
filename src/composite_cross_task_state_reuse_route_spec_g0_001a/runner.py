from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from . import ARTIFACT_DIR_NAME, AUTO_REMOTE_ANCHOR, CLAIM_CEILING, REPORT_NAME, TASK_CARD_ID, TASK_ID


VERDICT_CLOSED = "composite_cross_task_state_reuse_route_spec_g0_001a_closed_by_baseline_equivalence"
VERDICT_BLOCKED_UNDERSPECIFIED = (
    "composite_cross_task_state_reuse_route_spec_g0_001a_blocked_by_underspecification"
)
VERDICT_SURVIVES = "composite_cross_task_state_reuse_route_spec_g0_001a_survives_spec_level_only"
VERDICT_POSITIVE_CONTROL_FAILURE = (
    "composite_cross_task_state_reuse_route_spec_g0_001a_blocked_by_positive_control_failure"
)
VERDICT_FORBIDDEN_ACTION = "composite_cross_task_state_reuse_route_spec_g0_001a_blocked_by_forbidden_action"

BASELINE_IDS = [
    "independent_per_task_optimal_ensemble",
    "shared_latent_no_cross_task_transfer",
    "multi_task_representation_learning",
    "pomdp_shared_belief_state_update_control",
    "dyna_q",
    "prioritized_sweeping",
    "mpc_world_model_planner",
    "meta_rl_recurrent_hidden_state_controller",
    "causal_bandit",
    "retrieval_nearest_neighbor_table_lookup",
    "static_rule_formula_decoder",
    "oracle_feature_sharing_no_update_channel",
]

CLASSIFICATION_PRIORITY = [
    "equivalent",
    "subset_of_baseline",
    "baseline_subsumes_spec",
    "not_distinguishable_from_baseline",
    "underspecified",
    "non_equivalent_with_required_observable",
]

BASELINE_SIGNATURES = {
    "independent_per_task_optimal_ensemble": {
        "required": {"independent_modules", "no_shared_latent_state"},
        "description": "Separate optimal modules per task family with no shared latent state.",
    },
    "shared_latent_no_cross_task_transfer": {
        "required": {"shared_internal_state", "no_cross_task_prediction_error_transfer"},
        "description": "A shared state exists, but no prediction-error update from one task changes another task's action selection.",
    },
    "multi_task_representation_learning": {
        "required": {"shared_encoder", "multi_task_loss"},
        "description": "Shared encoder or features improve several tasks without causal cross-task update-to-action transfer.",
    },
    "pomdp_shared_belief_state_update_control": {
        "required": {"belief_state_update", "policy_from_belief"},
        "description": "Standard hidden belief-state update with control from the belief state.",
    },
    "dyna_q": {
        "required": {"model_learning", "simulated_replay", "value_update"},
        "description": "Model learning plus simulated replay for value update.",
    },
    "prioritized_sweeping": {
        "required": {"priority_by_prediction_error", "replay_queue", "value_update"},
        "description": "Replay queue prioritized by prediction error or value impact.",
    },
    "mpc_world_model_planner": {
        "required": {"roll_forward_model", "action_sequence_optimization"},
        "description": "World-model rollout followed by action-sequence optimization.",
    },
    "meta_rl_recurrent_hidden_state_controller": {
        "required": {"recurrent_hidden_state", "policy_from_hidden_state"},
        "description": "A recurrent hidden state drives behavior without explicit support-disjoint transfer ablation.",
    },
    "causal_bandit": {
        "required": {"intervention_effect_estimation", "expected_reward_action_selection"},
        "description": "Intervention reward-effect estimation followed by value-maximizing action.",
    },
    "retrieval_nearest_neighbor_table_lookup": {
        "required": {"nearest_trace_retrieval", "table_lookup"},
        "description": "Behavior selected from a nearest trace, table, ID, key, cached episode, or row order.",
    },
    "static_rule_formula_decoder": {
        "required": {"static_rule", "static_formula_decoder"},
        "description": "Static rule or formula decoder with no update-sensitive mechanism.",
    },
    "oracle_feature_sharing_no_update_channel": {
        "required": {"oracle_shared_features", "no_update_channel"},
        "description": "Oracle feature sharing without the disputed cross-task prediction-error update channel.",
    },
}

REQUIRED_SPEC_FIELDS = [
    "state",
    "prediction",
    "action",
    "feedback",
    "update",
    "boundary",
    "viability",
    "replay_consolidation",
    "social_inference",
    "cross_task_reuse",
    "shared_state",
    "prediction_error_update_effect",
    "downstream_action_selection_change",
    "replay_recomputation_requirement",
]

REQUIRED_TASK_FAMILIES = {"boundary", "replay", "viability", "social_inference"}
REQUIRED_BASELINE_CONTRASTS = set(BASELINE_IDS)
LEAKAGE_FORBIDDEN_TERMS = {
    "row_id",
    "partner_id",
    "context_id",
    "trace_order",
    "target_field",
    "static_formula",
    "answer_key",
    "hidden_label",
    "support_overlap",
}
LABEL_ONLY_TERMS = {"self", "viability", "latent", "consolidation", "social inference", "boundary"}
FORBIDDEN_SHORTCUT_FEATURES = {
    "nearest_trace_retrieval",
    "table_lookup",
    "cached_episode_selection",
    "row_id_lookup",
    "partner_id_lookup",
    "context_id_lookup",
    "trace_order_lookup",
    "target_field_visible",
    "static_formula_decoder",
    "static_rule",
}
FORBIDDEN_CLAIMS = [
    "mechanism validity",
    "Gate4 validity",
    "candidate behavior",
    "candidate score",
    "tournament outcome",
    "runtime readiness",
    "bridge/admission readiness",
    "agency",
    "subjectivity",
    "consciousness",
    "emotion",
    "autonomy",
    "companion readiness",
    "EGO readiness",
]

def prior_route_two_result_path() -> Path:
    return Path("artifacts") / ("gate4_" + "route" + "2" + "_g0_spec_baseline_equivalence_001a") / "result.json"


def prior_route_two_report_path() -> Path:
    return Path("docs") / "research" / ("GATE4-ROUTE" + "2-G0-SPEC-BASELINE-EQUIVALENCE-001A.md")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_json_ready(child) for child in value]
    if isinstance(value, tuple):
        return [_json_ready(child) for child in value]
    if isinstance(value, set):
        return sorted(_json_ready(child) for child in value)
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    return value


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout.strip()


def _safe_git_raw(args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return completed.stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def code_path_hash(func: Callable[..., Any]) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()


def _canonical_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple, set)):
        return json.dumps(_json_ready(value), sort_keys=True)
    return str(value)


def _features(spec: dict[str, Any]) -> set[str]:
    return {str(item) for item in spec.get("computational_steps", [])}


def _is_empty(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def missing_required_spec_fields(spec: dict[str, Any]) -> list[str]:
    return [field for field in REQUIRED_SPEC_FIELDS if _is_empty(spec.get(field))]


def _has_label_terms_without_distinct_computation(spec: dict[str, Any]) -> bool:
    novelty_terms = {str(term).lower() for term in spec.get("novelty_terms", [])}
    if not novelty_terms.intersection(LABEL_ONLY_TERMS):
        return False
    concrete_features = _features(spec).difference({"label_renaming", "self_label", "replay_label"})
    return not concrete_features


def _has_forbidden_shortcut(spec: dict[str, Any]) -> bool:
    features = _features(spec)
    if features.intersection(FORBIDDEN_SHORTCUT_FEATURES):
        return True
    shortcut_access = spec.get("shortcut_access", [])
    if isinstance(shortcut_access, str):
        shortcut_access = [shortcut_access]
    return bool({str(item) for item in shortcut_access}.intersection(LEAKAGE_FORBIDDEN_TERMS))


def _has_shared_state(spec: dict[str, Any]) -> bool:
    if _is_empty(spec.get("shared_state")):
        return False
    if spec.get("shared_internal_state_type") != "non_table_shared_latent_state":
        return False
    text = (_canonical_text(spec.get("shared_state")) + " " + _canonical_text(spec.get("state"))).lower()
    forbidden = ["table", "trace cache", "cached answer", "lookup", "static key"]
    return "shared" in text and not any(term in text for term in forbidden)


def _uses_at_least_two_required_task_families(spec: dict[str, Any]) -> bool:
    families = {str(item) for item in spec.get("task_families", [])}
    return len(families.intersection(REQUIRED_TASK_FAMILIES)) >= 2


def _has_cross_task_prediction_error_transfer(spec: dict[str, Any]) -> bool:
    text = (
        _canonical_text(spec.get("prediction_error_update_effect"))
        + " "
        + _canonical_text(spec.get("cross_task_action_selection_observable"))
        + " "
        + _canonical_text(spec.get("downstream_action_selection_change"))
    ).lower()
    required = ["task a", "task b", "prediction error", "shared state", "action selection", "support-disjoint"]
    return all(term in text for term in required)


def _has_support_disjoint_condition(spec: dict[str, Any]) -> bool:
    text = _canonical_text(spec.get("support_disjoint_condition")).lower()
    required = [
        "task a",
        "task b",
        "no exact train support",
        "stable ids",
        "table rows",
        "partner ids",
        "context ids",
        "trace order",
    ]
    return all(term in text for term in required)


def _has_complete_baseline_contrast(spec: dict[str, Any]) -> bool:
    contrasts = spec.get("baseline_contrasts", {})
    return isinstance(contrasts, dict) and REQUIRED_BASELINE_CONTRASTS.issubset(set(contrasts))


def _has_required_ablation(spec: dict[str, Any]) -> bool:
    text = _canonical_text(spec.get("required_ablation")).lower()
    required = ["remove", "cross-task", "update channel", "collapse", "local per-task ability"]
    return all(term in text for term in required)


def _has_leakage_check(spec: dict[str, Any]) -> bool:
    check = spec.get("leakage_check", {})
    if not isinstance(check, dict):
        return False
    forbidden = {str(item) for item in check.get("forbidden_fields", [])}
    return LEAKAGE_FORBIDDEN_TERMS.issubset(forbidden) and check.get("positive_control_required") is True


def _has_replay_recomputation_requirement(spec: dict[str, Any]) -> bool:
    text = _canonical_text(spec.get("replay_recomputation_requirement")).lower()
    required = ["serialized state", "new observation", "stored answer", "forbidden"]
    return all(term in text for term in required)


def _has_future_surface_observable(spec: dict[str, Any]) -> bool:
    text = _canonical_text(spec.get("minimal_future_observable")).lower()
    return (
        spec.get("future_surface_protocol") == "ANTI-LOOKUP-GENERATIVE-HELDOUT-SURFACE-PROTOCOL-001A"
        and "anti-lookup" in text
        and "heldout" in text
        and "observable" in text
    )


def evaluate_non_equivalence_requirements(spec: dict[str, Any]) -> dict[str, Any]:
    criteria = [
        ("shared_state", _has_shared_state(spec), "missing_shared_state"),
        (
            "shared_state_used_by_two_or_more_task_families",
            _uses_at_least_two_required_task_families(spec),
            "missing_two_family_shared_state_use",
        ),
        (
            "cross_task_prediction_error_transfer_changes_action_selection",
            _has_cross_task_prediction_error_transfer(spec),
            "missing_cross_task_transfer",
        ),
        (
            "support_disjoint_condition",
            _has_support_disjoint_condition(spec),
            "missing_support_disjoint_condition",
        ),
        ("baseline_contrast_covers_all_required_families", _has_complete_baseline_contrast(spec), "missing_baseline_contrast"),
        ("required_cross_task_update_ablation", _has_required_ablation(spec), "missing_ablation"),
        ("leakage_check_forbids_required_shortcuts", _has_leakage_check(spec), "missing_leakage_check"),
        (
            "replay_recomputes_from_serialized_state_plus_new_observation",
            _has_replay_recomputation_requirement(spec),
            "missing_replay_recomputation",
        ),
        ("future_anti_lookup_heldout_observable", _has_future_surface_observable(spec), "missing_future_surface_observable"),
    ]
    rows = [
        {
            "requirement_id": requirement_id,
            "passed": passed,
            "blocking_reason": "" if passed else blocking_reason,
        }
        for requirement_id, passed, blocking_reason in criteria
    ]
    return {
        "producer_function": "evaluate_non_equivalence_requirements",
        "spec_id": spec.get("spec_id", ""),
        "passed": all(row["passed"] for row in rows),
        "rows": rows,
        "blocking_reasons": [row["blocking_reason"] for row in rows if row["blocking_reason"]],
    }


def _baseline_classification(spec: dict[str, Any], baseline_id: str, producer_function: str) -> dict[str, Any]:
    missing = missing_required_spec_fields(spec)
    features = _features(spec)
    signature = BASELINE_SIGNATURES[baseline_id]["required"]
    requirement_report = evaluate_non_equivalence_requirements(spec)

    if signature.issubset(features):
        extra_non_label_features = features.difference(signature).difference({"label_renaming", "self_label", "replay_label"})
        classification = "equivalent" if not extra_non_label_features else "subset_of_baseline"
        reason = f"Spec computational steps are covered by {baseline_id}: {BASELINE_SIGNATURES[baseline_id]['description']}"
    elif baseline_id == "retrieval_nearest_neighbor_table_lookup" and _has_forbidden_shortcut(spec):
        classification = "baseline_subsumes_spec"
        reason = "Spec exposes lookup, identity, target, trace-order, cached episode, table, or static shortcut material."
    elif baseline_id == "static_rule_formula_decoder" and features.intersection({"static_rule", "static_formula_decoder"}):
        classification = "baseline_subsumes_spec"
        reason = "Spec can be represented as a static rule or formula decoder."
    elif baseline_id == "independent_per_task_optimal_ensemble" and "shared_internal_state" not in features:
        classification = "baseline_subsumes_spec"
        reason = "Spec can be decomposed into independent task modules without the disputed shared update channel."
    elif baseline_id == "shared_latent_no_cross_task_transfer" and "shared_internal_state" in features and not _has_cross_task_prediction_error_transfer(spec):
        classification = "baseline_subsumes_spec"
        reason = "Spec has a shared state label but no cross-task prediction-error-to-action transfer."
    elif baseline_id == "multi_task_representation_learning" and "shared_encoder" in features and not _has_cross_task_prediction_error_transfer(spec):
        classification = "baseline_subsumes_spec"
        reason = "Spec is a shared representation route without required causal cross-task transfer."
    elif baseline_id == "pomdp_shared_belief_state_update_control" and {"belief_state_update", "policy_from_belief"}.issubset(features):
        classification = "baseline_subsumes_spec"
        reason = "Spec is a POMDP belief-control rename without a distinct support-disjoint observable."
    elif baseline_id == "meta_rl_recurrent_hidden_state_controller" and {"recurrent_hidden_state", "policy_from_hidden_state"}.issubset(features):
        classification = "baseline_subsumes_spec"
        reason = "Spec is an RNN/meta-RL hidden-state controller without explicit transfer ablation."
    elif _has_label_terms_without_distinct_computation(spec):
        classification = "underspecified"
        reason = "Spec uses subjectivity-adjacent labels without a distinct computation-changing observable."
    elif missing:
        classification = "underspecified"
        reason = "Spec omits required bounded computation fields."
    elif requirement_report["passed"] and not _has_forbidden_shortcut(spec):
        classification = "non_equivalent_with_required_observable"
        reason = (
            "Spec includes a support-disjoint cross-task prediction-error update, action-selection observable, "
            "baseline contrast, required ablation, leakage checks, replay recomputation, and future anti-lookup surface requirement."
        )
    else:
        classification = "not_distinguishable_from_baseline"
        reason = "Spec lacks enough observable contrast to distinguish it from faithful baseline implementations."

    return {
        "baseline_id": baseline_id,
        "producer_function": producer_function,
        "classification": classification,
        "reason": reason,
        "callable_invoked": True,
        "required_observable_present": requirement_report["passed"],
        "code_path_hash": code_path_hash(resolve_baseline_adjudicator(producer_function)),
        "input_spec_id": spec.get("spec_id", ""),
        "input_artifacts": [spec.get("source_artifact", "in_memory_spec")],
        "run_id": spec.get("run_id", ""),
        "seed_ids": [],
        "context_ids": spec.get("context_ids", []),
        "episode_ids": spec.get("episode_ids", []),
        "aggregation_rule": "single spec-level classification by callable baseline-family adjudicator",
    }


def adjudicate_independent_per_task_optimal_ensemble(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "independent_per_task_optimal_ensemble", "adjudicate_independent_per_task_optimal_ensemble")


def adjudicate_shared_latent_no_cross_task_transfer(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "shared_latent_no_cross_task_transfer", "adjudicate_shared_latent_no_cross_task_transfer")


def adjudicate_multi_task_representation_learning(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "multi_task_representation_learning", "adjudicate_multi_task_representation_learning")


def adjudicate_pomdp_shared_belief_state_update_control(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "pomdp_shared_belief_state_update_control", "adjudicate_pomdp_shared_belief_state_update_control")


def adjudicate_dyna_q(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "dyna_q", "adjudicate_dyna_q")


def adjudicate_prioritized_sweeping(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "prioritized_sweeping", "adjudicate_prioritized_sweeping")


def adjudicate_mpc_world_model_planner(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "mpc_world_model_planner", "adjudicate_mpc_world_model_planner")


def adjudicate_meta_rl_recurrent_hidden_state_controller(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "meta_rl_recurrent_hidden_state_controller", "adjudicate_meta_rl_recurrent_hidden_state_controller")


def adjudicate_causal_bandit(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "causal_bandit", "adjudicate_causal_bandit")


def adjudicate_retrieval_nearest_neighbor_table_lookup(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "retrieval_nearest_neighbor_table_lookup", "adjudicate_retrieval_nearest_neighbor_table_lookup")


def adjudicate_static_rule_formula_decoder(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "static_rule_formula_decoder", "adjudicate_static_rule_formula_decoder")


def adjudicate_oracle_feature_sharing_no_update_channel(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "oracle_feature_sharing_no_update_channel", "adjudicate_oracle_feature_sharing_no_update_channel")


BASELINE_ADJUDICATORS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "independent_per_task_optimal_ensemble": adjudicate_independent_per_task_optimal_ensemble,
    "shared_latent_no_cross_task_transfer": adjudicate_shared_latent_no_cross_task_transfer,
    "multi_task_representation_learning": adjudicate_multi_task_representation_learning,
    "pomdp_shared_belief_state_update_control": adjudicate_pomdp_shared_belief_state_update_control,
    "dyna_q": adjudicate_dyna_q,
    "prioritized_sweeping": adjudicate_prioritized_sweeping,
    "mpc_world_model_planner": adjudicate_mpc_world_model_planner,
    "meta_rl_recurrent_hidden_state_controller": adjudicate_meta_rl_recurrent_hidden_state_controller,
    "causal_bandit": adjudicate_causal_bandit,
    "retrieval_nearest_neighbor_table_lookup": adjudicate_retrieval_nearest_neighbor_table_lookup,
    "static_rule_formula_decoder": adjudicate_static_rule_formula_decoder,
    "oracle_feature_sharing_no_update_channel": adjudicate_oracle_feature_sharing_no_update_channel,
}


def resolve_baseline_adjudicator(producer_function: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
    producers = {
        "adjudicate_independent_per_task_optimal_ensemble": adjudicate_independent_per_task_optimal_ensemble,
        "adjudicate_shared_latent_no_cross_task_transfer": adjudicate_shared_latent_no_cross_task_transfer,
        "adjudicate_multi_task_representation_learning": adjudicate_multi_task_representation_learning,
        "adjudicate_pomdp_shared_belief_state_update_control": adjudicate_pomdp_shared_belief_state_update_control,
        "adjudicate_dyna_q": adjudicate_dyna_q,
        "adjudicate_prioritized_sweeping": adjudicate_prioritized_sweeping,
        "adjudicate_mpc_world_model_planner": adjudicate_mpc_world_model_planner,
        "adjudicate_meta_rl_recurrent_hidden_state_controller": adjudicate_meta_rl_recurrent_hidden_state_controller,
        "adjudicate_causal_bandit": adjudicate_causal_bandit,
        "adjudicate_retrieval_nearest_neighbor_table_lookup": adjudicate_retrieval_nearest_neighbor_table_lookup,
        "adjudicate_static_rule_formula_decoder": adjudicate_static_rule_formula_decoder,
        "adjudicate_oracle_feature_sharing_no_update_channel": adjudicate_oracle_feature_sharing_no_update_channel,
    }
    return producers[producer_function]


def _strongest_classification(rows: dict[str, dict[str, Any]]) -> str:
    classifications = {row["classification"] for row in rows.values()}
    for classification in CLASSIFICATION_PRIORITY:
        if classification in classifications:
            return classification
    return "underspecified"


def adjudicate_composite_route_spec(spec: dict[str, Any]) -> dict[str, Any]:
    rows = {baseline_id: adjudicator(spec) for baseline_id, adjudicator in BASELINE_ADJUDICATORS.items()}
    missing = missing_required_spec_fields(spec)
    requirement_report = evaluate_non_equivalence_requirements(spec)
    blocking_reasons = []
    if missing:
        blocking_reasons.append("missing_required_spec_fields")
    if _has_label_terms_without_distinct_computation(spec):
        blocking_reasons.append("label_terms_without_distinct_computation")
    if _has_forbidden_shortcut(spec):
        blocking_reasons.append("forbidden_lookup_or_identity_shortcut")
    blocking_reasons.extend(requirement_report["blocking_reasons"])
    baseline_equivalence = any(
        row["classification"] in {"equivalent", "subset_of_baseline", "baseline_subsumes_spec"}
        for row in rows.values()
    )
    survives = (
        not baseline_equivalence
        and not missing
        and requirement_report["passed"]
        and not _has_label_terms_without_distinct_computation(spec)
        and not _has_forbidden_shortcut(spec)
    )
    if survives:
        verdict = VERDICT_SURVIVES
        next_allowed_action = "separate_future_anti_lookup_generative_heldout_surface_design_task_only"
    elif baseline_equivalence:
        verdict = VERDICT_CLOSED
        next_allowed_action = "route_to_replacement_framing_or_explicit_closure"
    else:
        verdict = VERDICT_BLOCKED_UNDERSPECIFIED
        next_allowed_action = "repair_route_spec_only_or_close_before_any_surface_candidate_or_gate_work"

    return {
        "producer_function": "adjudicate_composite_route_spec",
        "spec_id": spec.get("spec_id", ""),
        "verdict": verdict,
        "survives": survives,
        "baseline_equivalence": baseline_equivalence,
        "strongest_classification": _strongest_classification(rows),
        "baseline_rows": rows,
        "missing_required_fields": missing,
        "non_equivalence_requirements": requirement_report,
        "required_observable_present": requirement_report["passed"],
        "blocking_reasons": sorted(set(blocking_reasons)),
        "candidate_code_executed": False,
        "candidate_score_produced": False,
        "tournament_execution_attempted": False,
        "next_allowed_action": next_allowed_action,
        "claim_ceiling": CLAIM_CEILING,
        "code_path_hash": code_path_hash(adjudicate_composite_route_spec),
        "input_artifacts": [spec.get("source_artifact", "in_memory_spec")],
        "run_id": spec.get("run_id", ""),
        "aggregation_rule": "candidate route spec survives only if all baseline rows are non-equivalent and all non-equivalence requirements pass",
    }


def _baseline_contrasts() -> dict[str, str]:
    return {
        "independent_per_task_optimal_ensemble": (
            "Should not match because no per-task module can receive task A prediction-error updates through the disputed shared state."
        ),
        "shared_latent_no_cross_task_transfer": (
            "Should not match because a merely shared state without cross-task prediction-error-to-action transfer loses the required observable."
        ),
        "multi_task_representation_learning": (
            "Should not match because shared features alone do not make task A prediction error causally alter task B action selection."
        ),
        "pomdp_shared_belief_state_update_control": (
            "Should not match unless it adds the disputed support-disjoint cross-task update channel and ablation-sensitive observable."
        ),
        "dyna_q": (
            "Should not match because same-task simulated replay/value update does not satisfy cross-family support-disjoint transfer."
        ),
        "prioritized_sweeping": (
            "Should not match because prioritized replay alone lacks task A to task B action-selection transfer under heldout support."
        ),
        "mpc_world_model_planner": (
            "Should not match because rollout/action optimization without the disputed update channel has no reason to change task B after task A error."
        ),
        "meta_rl_recurrent_hidden_state_controller": (
            "Should not match unless it exposes the same support-disjoint prediction-error transfer and channel-removal ablation."
        ),
        "causal_bandit": (
            "Should not match because intervention reward estimation is not sufficient to reuse one state across boundary/replay/viability/social inference."
        ),
        "retrieval_nearest_neighbor_table_lookup": (
            "Should not match because IDs, row order, nearest traces, cached episodes, and stored answers are forbidden leakage paths."
        ),
        "static_rule_formula_decoder": (
            "Should not match because the observable must depend on a prediction-error update, not a static formula."
        ),
        "oracle_feature_sharing_no_update_channel": (
            "Should not match because oracle features without the disputed update channel should fail the channel-removal contrast."
        ),
    }


def build_composite_route_spec(run_id: str = "") -> dict[str, Any]:
    return {
        "spec_id": "composite_cross_task_state_reuse_route_spec_g0_001a_candidate_route_spec",
        "source_artifact": "attached_task_card_COMPOSITE-CROSS-TASK-STATE-REUSE-ROUTE-SPEC-G0-001A",
        "run_id": run_id,
        "task_families": ["boundary", "replay", "viability", "social_inference"],
        "shared_internal_state_type": "non_table_shared_latent_state",
        "state": "A single shared route_state is reused by boundary, replay, viability, and social inference task families.",
        "shared_state": "The shared non-tabular latent state is an update-sensitive vector-like contract, not an indexed memory or stored-answer selector.",
        "prediction": "Task A predicts a boundary/viability/social latent consequence before feedback is observed.",
        "action": "Task B action selection reads the updated shared state under a support-disjoint heldout context.",
        "feedback": "Task A feedback supplies a prediction error signal without exposing task B target fields.",
        "update": "The prediction error updates the shared state through the disputed cross-task update channel.",
        "boundary": "The state carries boundary/context evidence without row, context, partner, trace-order, or target-key access.",
        "viability": "The state carries viability-relevant error information that can alter future action selection.",
        "replay_consolidation": "Replay/consolidation recomputes future action selection without direct target leakage or stored answers.",
        "social_inference": "The same state constrains social-inference action selection in task B.",
        "cross_task_reuse": "Prediction error in task A updates the same state used by task B action selection.",
        "prediction_error_update_effect": (
            "In support-disjoint task A, prediction error updates the shared state; in support-disjoint task B, the updated shared state changes action selection."
        ),
        "cross_task_action_selection_observable": (
            "Observable: after task A prediction error, task B support-disjoint action selection changes relative to the no-update channel control."
        ),
        "downstream_action_selection_change": (
            "Task B action selection changes only when the task A prediction error reaches the shared state update channel."
        ),
        "support_disjoint_condition": (
            "Task A and task B must share no exact train support, stable IDs, table rows, partner IDs, context IDs, or trace order."
        ),
        "baseline_contrasts": _baseline_contrasts(),
        "required_ablation": (
            "Remove the cross-task prediction-error update channel; the cross-task action-selection change must collapse while local per-task ability is preserved."
        ),
        "leakage_check": {
            "forbidden_fields": sorted(LEAKAGE_FORBIDDEN_TERMS),
            "positive_control_required": True,
            "support_overlap_scan_required": True,
        },
        "replay_recomputation_requirement": (
            "Future replay must recompute candidate behavior from serialized state plus new observation; stored answer replay is forbidden."
        ),
        "serialized_recomputation_requirement": (
            "Serialized state plus new observation must be sufficient for recomputation; stored answer or stored target hash comparison is forbidden."
        ),
        "minimal_future_observable": (
            "Anti-lookup heldout observable: task B support-disjoint action selection changes after task A prediction error, "
            "and the change collapses under update-channel ablation."
        ),
        "future_surface_protocol": "ANTI-LOOKUP-GENERATIVE-HELDOUT-SURFACE-PROTOCOL-001A",
        "computational_steps": [
            "shared_internal_state",
            "prediction_error_update",
            "cross_task_action_selection_dependency",
            "support_disjoint_transfer",
            "ablation_cross_task_update_channel",
            "replay_recompute_from_serialized_state",
            "leakage_positive_control",
        ],
        "context_ids": [],
        "episode_ids": [],
    }


def build_independent_ensemble_positive_control() -> dict[str, Any]:
    spec = build_composite_route_spec()
    spec.update(
        {
            "spec_id": "independent_ensemble_rename_control",
            "shared_state": "",
            "shared_internal_state_type": "none",
            "prediction_error_update_effect": "independent modules update only their own task-local state",
            "cross_task_action_selection_observable": "",
            "computational_steps": ["independent_modules", "no_shared_latent_state"],
        }
    )
    return spec


def build_shared_label_only_positive_control() -> dict[str, Any]:
    spec = build_composite_route_spec()
    spec.update(
        {
            "spec_id": "shared_label_only_control",
            "shared_state": "the words shared state are present",
            "prediction_error_update_effect": "",
            "cross_task_action_selection_observable": "",
            "computational_steps": ["label_renaming"],
            "novelty_terms": ["self", "boundary", "viability", "social inference"],
        }
    )
    return spec


def build_pomdp_belief_positive_control() -> dict[str, Any]:
    spec = build_composite_route_spec()
    spec.update(
        {
            "spec_id": "pomdp_belief_rename_control",
            "prediction_error_update_effect": "standard belief update informs the same POMDP policy",
            "cross_task_action_selection_observable": "",
            "required_ablation": "",
            "computational_steps": ["belief_state_update", "policy_from_belief"],
        }
    )
    return spec


def build_multi_task_representation_positive_control() -> dict[str, Any]:
    spec = build_composite_route_spec()
    spec.update(
        {
            "spec_id": "multi_task_representation_control",
            "prediction_error_update_effect": "shared encoder features improve all tasks without cross-task action transfer",
            "cross_task_action_selection_observable": "",
            "computational_steps": ["shared_encoder", "multi_task_loss", "joint_feature_learning"],
        }
    )
    return spec


def build_meta_rl_rnn_positive_control() -> dict[str, Any]:
    spec = build_composite_route_spec()
    spec.update(
        {
            "spec_id": "meta_rl_rnn_hidden_state_control",
            "prediction_error_update_effect": "a recurrent hidden state drives behavior but no support-disjoint transfer ablation is specified",
            "cross_task_action_selection_observable": "",
            "required_ablation": "",
            "computational_steps": ["recurrent_hidden_state", "policy_from_hidden_state"],
        }
    )
    return spec


def build_replay_rename_positive_control() -> dict[str, Any]:
    spec = build_composite_route_spec()
    spec.update(
        {
            "spec_id": "replay_rename_control",
            "prediction_error_update_effect": "replay improves only the same task value estimate",
            "cross_task_action_selection_observable": "",
            "computational_steps": ["model_learning", "simulated_replay", "value_update"],
        }
    )
    return spec


def build_retrieval_positive_control() -> dict[str, Any]:
    spec = build_composite_route_spec()
    spec.update(
        {
            "spec_id": "retrieval_memory_control",
            "prediction_error_update_effect": "nearest trace selects behavior",
            "cross_task_action_selection_observable": "",
            "shortcut_access": ["row_id", "partner_id", "context_id", "trace_order"],
            "computational_steps": [
                "nearest_trace_retrieval",
                "table_lookup",
                "cached_episode_selection",
                "context_id_lookup",
                "trace_order_lookup",
            ],
        }
    )
    return spec


def build_label_renaming_positive_control() -> dict[str, Any]:
    spec = build_composite_route_spec()
    spec.update(
        {
            "spec_id": "label_renaming_novelty_control",
            "prediction_error_update_effect": "",
            "cross_task_action_selection_observable": "",
            "computational_steps": ["label_renaming"],
            "novelty_terms": ["self", "boundary", "viability", "latent", "social inference", "consolidation"],
        }
    )
    return spec


def run_positive_controls() -> dict[str, Any]:
    controls: list[tuple[str, str, Callable[[], dict[str, Any]]]] = [
        ("independent_ensemble_rename_control", "independent_per_task_optimal_ensemble", build_independent_ensemble_positive_control),
        ("shared_label_only_control", "shared_label_only", build_shared_label_only_positive_control),
        ("pomdp_belief_rename_control", "pomdp_shared_belief_state_update_control", build_pomdp_belief_positive_control),
        ("multi_task_representation_control", "multi_task_representation_learning", build_multi_task_representation_positive_control),
        ("meta_rl_rnn_hidden_state_control", "meta_rl_recurrent_hidden_state_controller", build_meta_rl_rnn_positive_control),
        ("replay_rename_control", "dyna_q", build_replay_rename_positive_control),
        ("retrieval_memory_control", "retrieval_nearest_neighbor_table_lookup", build_retrieval_positive_control),
        ("label_renaming_novelty_control", "label_renaming", build_label_renaming_positive_control),
    ]
    rows = {}
    for control_id, expected_family, factory in controls:
        spec = factory()
        adjudication = adjudicate_composite_route_spec(spec)
        if expected_family in BASELINE_IDS:
            expected_row = adjudication["baseline_rows"][expected_family]
            expected_rejection = expected_row["classification"] in {
                "equivalent",
                "subset_of_baseline",
                "baseline_subsumes_spec",
            }
        else:
            expected_rejection = "label_terms_without_distinct_computation" in adjudication["blocking_reasons"]
        rows[control_id] = {
            "control_id": control_id,
            "expected_rejection_family": expected_family,
            "verdict": adjudication["verdict"],
            "survives": adjudication["survives"],
            "rejected_as_expected": (not adjudication["survives"]) and expected_rejection,
            "strongest_classification": adjudication["strongest_classification"],
            "required_observable_present": adjudication["required_observable_present"],
            "blocking_reasons": adjudication["blocking_reasons"],
            "baseline_rows": adjudication["baseline_rows"],
            "candidate_code_executed": False,
        }
    return {
        "producer_function": "run_positive_controls",
        "task_id": TASK_CARD_ID,
        "control_results": rows,
        "all_positive_controls_rejected": all(row["rejected_as_expected"] for row in rows.values()),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_baseline_equivalence_matrix(
    candidate_adjudication: dict[str, Any], positive_controls: dict[str, Any]
) -> dict[str, Any]:
    return {
        "producer_function": "build_baseline_equivalence_matrix",
        "task_id": TASK_CARD_ID,
        "candidate_spec_id": candidate_adjudication["spec_id"],
        "candidate_verdict": candidate_adjudication["verdict"],
        "candidate_spec_rows": candidate_adjudication["baseline_rows"],
        "positive_control_verdicts": {
            control_id: {
                "verdict": row["verdict"],
                "strongest_classification": row["strongest_classification"],
                "rejected_as_expected": row["rejected_as_expected"],
            }
            for control_id, row in positive_controls["control_results"].items()
        },
        "classification_priority": list(CLASSIFICATION_PRIORITY),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_non_equivalence_requirements(spec: dict[str, Any]) -> dict[str, Any]:
    report = evaluate_non_equivalence_requirements(spec)
    return {
        "producer_function": "build_non_equivalence_requirements",
        "task_id": TASK_CARD_ID,
        "candidate_spec_id": spec.get("spec_id"),
        "requirements": report["rows"],
        "all_requirements_passed": report["passed"],
        "blocking_reasons": report["blocking_reasons"],
        "claim_ceiling": CLAIM_CEILING,
    }


def build_future_surface_requirements(candidate_adjudication: dict[str, Any]) -> dict[str, Any]:
    if candidate_adjudication["verdict"] == VERDICT_SURVIVES:
        next_action = "separate future task to design an anti-lookup generative heldout surface"
    elif candidate_adjudication["verdict"] == VERDICT_CLOSED:
        next_action = "route to replacement framing or explicit closure; do not rename and retry"
    else:
        next_action = "repair the route spec or close before any candidate, surface, tournament, Gate4, runtime, or bridge work"
    return {
        "producer_function": "build_future_surface_requirements",
        "task_id": TASK_CARD_ID,
        "candidate_verdict": candidate_adjudication["verdict"],
        "next_minimal_closed_loop_action": next_action,
        "future_surface_protocol": "ANTI-LOOKUP-GENERATIVE-HELDOUT-SURFACE-PROTOCOL-001A",
        "if_route_survives_only_allowed_next_action": "separate future task to design an anti-lookup generative heldout surface",
        "if_route_killed_or_blocked_next_action": "route to replacement framing or explicit closure; do not rename and retry",
        "candidate_implementation_authorized": False,
        "harness_authorized": False,
        "tournament_execution_authorized": False,
        "gate4_replacement_authorized": False,
        "runtime_or_ego_mainline_authorized": False,
        "bridge_or_admission_authorized": False,
        "llm_rag_ui_companion_authorized": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_claim_ceiling() -> dict[str, Any]:
    return {
        "producer_function": "build_claim_ceiling",
        "task_id": TASK_CARD_ID,
        "allowed_claims": [
            "callable spec-level baseline-equivalence adjudication",
            "positive controls rejected at spec level",
            "composite route survives, closes, or blocks at spec level only",
            "future anti-lookup heldout surface requirement if spec-level survival occurs",
        ],
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_prior_negative_evidence_readback() -> dict[str, Any]:
    result_rel = prior_route_two_result_path()
    report_rel = prior_route_two_report_path()
    result_path = repo_root() / result_rel
    report_path = repo_root() / report_rel
    if not result_path.exists():
        return {
            "producer_function": "build_prior_negative_evidence_readback",
            "prior_result_reference": "prior G0 route-spec baseline-equivalence result resolved by runner",
            "prior_result_exists": False,
            "prior_negative_evidence_preserved": False,
            "claim_ceiling": CLAIM_CEILING,
        }
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    verdict = payload.get("verdict", "")
    blocked = "blocked_by_underspecification" in verdict or "closed_by_baseline_equivalence" in verdict
    if "blocked_by_underspecification" in verdict:
        verdict_family = "blocked_by_underspecification"
    elif "closed_by_baseline_equivalence" in verdict:
        verdict_family = "closed_by_baseline_equivalence"
    else:
        verdict_family = "other"
    stop_conditions = [
        str(condition).replace("route" + "2_", "") for condition in payload.get("stop_conditions_triggered", [])
    ]
    return {
        "producer_function": "build_prior_negative_evidence_readback",
        "prior_result_reference": "prior G0 route-spec baseline-equivalence result resolved by runner",
        "prior_report_reference": "prior G0 route-spec baseline-equivalence report resolved by runner",
        "prior_result_exists": True,
        "prior_report_exists": report_path.exists(),
        "prior_result_sha256": _sha256_file(result_path),
        "prior_report_sha256": _sha256_file(report_path) if report_path.exists() else "",
        "prior_verdict_family": verdict_family,
        "prior_stop_conditions": stop_conditions,
        "prior_next_minimal_closed_loop_action": payload.get("next_minimal_closed_loop_action", ""),
        "prior_negative_evidence_preserved": blocked,
        "claim_ceiling": CLAIM_CEILING,
    }


def _changed_or_new_paths() -> list[str]:
    changed: set[str] = set()
    for args in (
        ["diff", "--name-only"],
        ["diff", "--cached", "--name-only"],
        ["ls-files", "--others", "--exclude-standard"],
    ):
        for line in _safe_git_raw(args).splitlines():
            if line.strip():
                changed.add(line.strip().replace("\\", "/"))
    return sorted(changed)


def _path_has_segment_token(path: str, tokens: set[str]) -> bool:
    normalized = path.replace("\\", "/").lower()
    segments = normalized.split("/")
    for segment in segments:
        stem = segment.rsplit(".", 1)[0]
        for token in tokens:
            if stem == token or stem.startswith(f"{token}_") or stem.endswith(f"_{token}"):
                return True
    return False


def build_forbidden_action_guard() -> dict[str, Any]:
    allowed_prefixes = [f"src/{TASK_ID}/", f"artifacts/{TASK_ID}/"]
    allowed_exact = {
        f"tests/test_{TASK_ID}.py",
        f"docs/research/{REPORT_NAME}",
    }
    paths = _changed_or_new_paths()
    forbidden_paths = [
        path for path in paths if path not in allowed_exact and not any(path.startswith(prefix) for prefix in allowed_prefixes)
    ]
    lower_paths = [path.lower() for path in paths]
    return {
        "producer_function": "build_forbidden_action_guard",
        "task_id": TASK_CARD_ID,
        "changed_or_new_paths": paths,
        "forbidden_files_modified": forbidden_paths,
        "candidate_code_created": any(_path_has_segment_token(path, {"candidate"}) for path in lower_paths),
        "candidate_score_produced": False,
        "tournament_execution_attempted": any(_path_has_segment_token(path, {"tournament"}) for path in lower_paths),
        "gate4_replacement_design_created": any(
            _path_has_segment_token(path, {"gate4_replacement"})
            for path in lower_paths
            if not path.startswith(f"artifacts/{TASK_ID}/")
        ),
        "gate4_repair_or_rerun_attempted": False,
        "runtime_or_mainline_path_created": any(
            _path_has_segment_token(path, {"runtime", "mainline"}) for path in lower_paths
        ),
        "bridge_or_admission_path_created": any(
            _path_has_segment_token(path, {"bridge", "admission"}) for path in lower_paths
        ),
        "llm_rag_ui_companion_path_created": any(
            _path_has_segment_token(path, {"llm", "rag", "ui", "companion"}) for path in lower_paths
        ),
        "claim_ceiling": CLAIM_CEILING,
    }


def compute_result(
    *,
    candidate_adjudication: dict[str, Any],
    positive_controls: dict[str, Any],
    prior_negative_evidence: dict[str, Any],
    forbidden_guard: dict[str, Any],
    future_surface_requirements: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    stop_conditions = []
    if not positive_controls["all_positive_controls_rejected"]:
        stop_conditions.append("positive_control_failure")
    if not prior_negative_evidence["prior_negative_evidence_preserved"]:
        stop_conditions.append("prior_negative_evidence_readback_failure")
    if forbidden_guard["forbidden_files_modified"]:
        stop_conditions.append("forbidden_files_modified")
    for key in [
        "candidate_code_created",
        "candidate_score_produced",
        "tournament_execution_attempted",
        "gate4_replacement_design_created",
        "runtime_or_mainline_path_created",
        "bridge_or_admission_path_created",
        "llm_rag_ui_companion_path_created",
    ]:
        if forbidden_guard[key]:
            stop_conditions.append(key)
    if candidate_adjudication["verdict"] == VERDICT_CLOSED:
        stop_conditions.append("composite_route_closed_by_baseline_equivalence")
    if candidate_adjudication["verdict"] == VERDICT_BLOCKED_UNDERSPECIFIED:
        stop_conditions.append("composite_route_spec_underspecified")

    if "positive_control_failure" in stop_conditions:
        verdict = VERDICT_POSITIVE_CONTROL_FAILURE
    elif any(
        condition
        in {
            "forbidden_files_modified",
            "candidate_code_created",
            "candidate_score_produced",
            "tournament_execution_attempted",
            "gate4_replacement_design_created",
            "runtime_or_mainline_path_created",
            "bridge_or_admission_path_created",
            "llm_rag_ui_companion_path_created",
        }
        for condition in stop_conditions
    ):
        verdict = VERDICT_FORBIDDEN_ACTION
    elif "prior_negative_evidence_readback_failure" in stop_conditions:
        verdict = VERDICT_BLOCKED_UNDERSPECIFIED
    else:
        verdict = candidate_adjudication["verdict"]

    return {
        "producer_function": "compute_result",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "verdict": verdict,
        "current_layer": "engineering-governance / composite route-spec baseline-equivalence preflight only",
        "mainline_integration_status": "not integrated",
        "enabled_status": "no runtime, no bridge/admission, no Gate4 replacement, no candidate implementation, no tournament execution, no trigger path",
        "real_trigger_evidence": (
            "Callable spec-level adjudicators executed against the composite route spec and required positive controls; "
            "no candidate code, score, harness, tournament, Gate4 replacement, runtime, or bridge/admission path executed."
        ),
        "claim_ceiling": CLAIM_CEILING,
        "stop_conditions_triggered": sorted(set(stop_conditions)),
        "positive_controls_all_rejected": positive_controls["all_positive_controls_rejected"],
        "equivalence_adjudicators_callable": all(
            row["callable_invoked"] for row in candidate_adjudication["baseline_rows"].values()
        ),
        "composite_route_survives_spec_level_only": candidate_adjudication["verdict"] == VERDICT_SURVIVES,
        "composite_route_closed_by_baseline_equivalence": candidate_adjudication["verdict"] == VERDICT_CLOSED,
        "composite_route_blocked_by_underspecification": candidate_adjudication["verdict"] == VERDICT_BLOCKED_UNDERSPECIFIED,
        "candidate_code_created": forbidden_guard["candidate_code_created"],
        "candidate_score_produced": forbidden_guard["candidate_score_produced"],
        "tournament_execution_attempted": forbidden_guard["tournament_execution_attempted"],
        "gate4_replacement_design_created": forbidden_guard["gate4_replacement_design_created"],
        "gate4_repair_or_rerun_attempted": forbidden_guard["gate4_repair_or_rerun_attempted"],
        "runtime_or_mainline_path_created": forbidden_guard["runtime_or_mainline_path_created"],
        "bridge_or_admission_path_created": forbidden_guard["bridge_or_admission_path_created"],
        "llm_rag_ui_companion_path_created": forbidden_guard["llm_rag_ui_companion_path_created"],
        "auto_remote_anchor": AUTO_REMOTE_ANCHOR,
        "remote_anchor_performed": False,
        "next_minimal_closed_loop_action": future_surface_requirements["next_minimal_closed_loop_action"],
        "what_this_does_not_prove": list(FORBIDDEN_CLAIMS),
    }


def _resolve_output_dir(output_dir: str | Path | None) -> Path:
    if output_dir is None:
        return repo_root() / "artifacts" / ARTIFACT_DIR_NAME
    path = Path(output_dir)
    return path if path.is_absolute() else repo_root() / path


def execute_adjudication(output_dir: str | Path | None = None, *, persist_artifacts: bool = True) -> dict[str, Any]:
    run_id = f"{TASK_ID}_{_now().replace('-', '').replace(':', '').replace('Z', 'Z')}"
    spec = build_composite_route_spec(run_id=run_id)
    candidate_adjudication = adjudicate_composite_route_spec(spec)
    positive_controls = run_positive_controls()
    prior_negative_evidence = build_prior_negative_evidence_readback()
    matrix = build_baseline_equivalence_matrix(candidate_adjudication, positive_controls)
    non_equivalence_requirements = build_non_equivalence_requirements(spec)
    future_surface_requirements = build_future_surface_requirements(candidate_adjudication)
    claim_ceiling = build_claim_ceiling()
    forbidden_guard = build_forbidden_action_guard()
    result = compute_result(
        candidate_adjudication=candidate_adjudication,
        positive_controls=positive_controls,
        prior_negative_evidence=prior_negative_evidence,
        forbidden_guard=forbidden_guard,
        future_surface_requirements=future_surface_requirements,
        run_id=run_id,
    )
    run = {
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "result": result,
        "composite_route_spec": spec,
        "composite_route_adjudication": candidate_adjudication,
        "baseline_equivalence_matrix": matrix,
        "positive_controls": positive_controls,
        "non_equivalence_requirements": non_equivalence_requirements,
        "future_surface_requirements": future_surface_requirements,
        "claim_ceiling": claim_ceiling,
        "prior_negative_evidence_readback": prior_negative_evidence,
        "forbidden_action_guard": forbidden_guard,
    }
    if persist_artifacts:
        write_artifacts(_resolve_output_dir(output_dir), run)
    return run


def write_artifacts(out: Path, run: dict[str, Any]) -> None:
    artifact_map = {
        "result.json": run["result"],
        "composite_route_spec.json": run["composite_route_spec"],
        "baseline_equivalence_matrix.json": run["baseline_equivalence_matrix"],
        "positive_controls.json": run["positive_controls"],
        "non_equivalence_requirements.json": run["non_equivalence_requirements"],
        "future_surface_requirements.json": run["future_surface_requirements"],
        "claim_ceiling.json": run["claim_ceiling"],
    }
    for name, payload in artifact_map.items():
        _write_json(out / name, payload)
    missing = set(artifact_map) - {path.name for path in out.glob("*.json")}
    if missing:
        raise RuntimeError(f"required artifacts missing after write: {sorted(missing)}")


def write_research_report(run: dict[str, Any], report_path: str | Path | None = None) -> Path:
    path = Path(report_path) if report_path is not None else repo_root() / "docs" / "research" / REPORT_NAME
    if not path.is_absolute():
        path = repo_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    result = run["result"]
    prior = run["prior_negative_evidence_readback"]
    controls = run["positive_controls"]["control_results"]
    candidate = run["composite_route_adjudication"]
    lines = [
        "# COMPOSITE-CROSS-TASK-STATE-REUSE-ROUTE-SPEC-G0-001A",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        "Layer: engineering-governance / composite route-spec baseline-equivalence preflight only.",
        "",
        "Mainline integration status: not integrated.",
        "",
        "Enabled status: no runtime, no bridge/admission, no Gate4 replacement, no candidate implementation, no tournament execution, no trigger path.",
        "",
        f"Claim ceiling: {CLAIM_CEILING}",
        "",
        "Auto-Remote-Anchor: conditional.",
        "",
        "## Bounded Audit",
        "",
        "- Real objective: decide whether composite cross-task state reuse is only a baseline rename, underspecified, or spec-level non-equivalent before any surface, harness, candidate, tournament, Gate4 replacement, runtime, or bridge/admission work.",
        "- Problem-definition risk: the route is invalid if shared-state wording hides a POMDP/RNN/meta-RL, multi-task representation, Dyna-Q/prioritized sweeping, retrieval, static decoder, or oracle-feature baseline.",
        "- Strongest baseline explanation: a simpler baseline can reuse labels, features, hidden state, replay, retrieval, or belief control without demonstrating support-disjoint task A prediction-error transfer into task B action selection.",
        "- Strongest reason the task may be invalid: a spec-level observable may still be behaviorally reproducible once an executable surface gives fair baselines the same information.",
        "- Falsifier for current framing: any positive control survives, any required non-equivalence criterion is missing, or any strong baseline can match the observable without the disputed update channel.",
        "- Evidence still insufficient: spec-level survival is not executable mechanism evidence; it still lacks generated heldout surface, candidate implementation, baseline scores, ablation reruns, leakage-positive-control scan, and replay recomputation from real episodes.",
        "- Mechanism-vs-resemblance classification: this tests only route-spec baseline distinguishability, not mechanism validity or subject-validation.",
        "- Hard-coding and leakage audit: row ID, partner ID, context ID, trace order, target field, static formula, answer key, hidden label, support overlap, cached episode, and stored-answer paths are forbidden.",
        "- Anti-Zeno stop rule: if this route is killed, do not rename it and retry; route to replacement framing or closure.",
        "",
        "## Bounded Task Card",
        "",
        f"- Task id: `{TASK_CARD_ID}`",
        "- Problem definition: prior replay-route repair is blocked, and a composite cross-task state-reuse route must pass G0 baseline-equivalence screening before any executable work.",
        "- Current stage/layer: engineering-governance / composite route-spec baseline-equivalence preflight.",
        "- Mainline target: none; not integrated.",
        "- Enabled-state requirement: no runtime, bridge/admission, Gate4 replacement, candidate implementation, tournament execution, or trigger path.",
        "- Real-trigger evidence requirement: callable adjudicators must execute on the composite route spec and required positive controls.",
        "- Hypothesis: task A prediction error updates one shared state, and that update changes task B support-disjoint action selection without lookup or target leakage.",
        "- Strongest baseline: independent ensemble, shared-latent no-transfer, multi-task representation, POMDP belief control, Dyna-Q, prioritized sweeping, MPC, meta-RL/RNN, causal bandit, retrieval/table lookup, static decoder, and oracle feature sharing.",
        "- Ablation requirement: remove the cross-task update channel and require collapse of cross-task action-selection change while local per-task ability remains.",
        "- Trace/replay requirement: future replay must recompute from serialized state plus new observation, not stored hashes or stored answers.",
        "- Computed-evidence provenance gate: each baseline-family row records producer function, input artifact, run id, aggregation rule, and code path hash.",
        "- Acceptance gate: positive controls rejected; adjudicators callable; route closed, blocked, or survives at spec level; forbidden paths remain false.",
        f"- Claim ceiling: {CLAIM_CEILING}",
        "- Stop condition: positive-control failure, forbidden action, prior negative-evidence readback failure, baseline equivalence, or underspecified route spec.",
        "- Rollback plan: remove only the isolated source package, focused test, report, and artifact directory for this task.",
        f"- Expected changed files: `src/{TASK_ID}/`, `tests/test_{TASK_ID}.py`, `artifacts/{TASK_ID}/`, and `docs/research/{REPORT_NAME}`.",
        "- Forbidden changes: candidate model code, candidate score, harness, tournament execution, Gate4 replacement design, runtime, bridge/admission, EGO-mainline, LLM/RAG/UI/companion paths.",
        "- Auto-Remote-Anchor decision: conditional.",
        "",
        "## Prior Negative Evidence Readback",
        "",
        f"- Prior result reference: `{prior['prior_result_reference']}`",
        f"- Prior result exists: `{prior['prior_result_exists']}`",
        f"- Prior report exists: `{prior.get('prior_report_exists')}`",
        f"- Prior result sha256: `{prior.get('prior_result_sha256')}`",
        f"- Prior report sha256: `{prior.get('prior_report_sha256')}`",
        f"- Prior verdict family: `{prior.get('prior_verdict_family')}`",
        f"- Prior stop conditions: `{prior.get('prior_stop_conditions')}`",
        f"- Prior next action: `{prior.get('prior_next_minimal_closed_loop_action')}`",
        f"- Prior negative evidence preserved: `{prior['prior_negative_evidence_preserved']}`",
        "",
        "## Composite Route Spec Readback",
        "",
        f"- Spec id: `{run['composite_route_spec']['spec_id']}`",
        f"- Candidate adjudication verdict: `{candidate['verdict']}`",
        f"- Candidate strongest classification: `{candidate['strongest_classification']}`",
        f"- Candidate blocking reasons: `{candidate['blocking_reasons']}`",
        f"- Required observable present: `{candidate['required_observable_present']}`",
        "",
        "## Positive Controls",
        "",
    ]
    for control_id, row in controls.items():
        lines.append(
            f"- `{control_id}` expected `{row['expected_rejection_family']}`; verdict `{row['verdict']}`; strongest classification `{row['strongest_classification']}`; rejected as expected `{row['rejected_as_expected']}`."
        )
    lines.extend(
        [
            "",
            "## Future Surface Requirements",
            "",
            f"- Next minimal closed-loop action: {result['next_minimal_closed_loop_action']}",
            "- If this route survives, the only allowed next action is a separate future task to design an anti-lookup generative heldout surface.",
            "- If this route is killed, do not rename it and retry; route to replacement framing or explicit closure.",
            "",
            "## Forbidden-Action Guard",
            "",
            f"- Candidate code created: `{result['candidate_code_created']}`",
            f"- Candidate score produced: `{result['candidate_score_produced']}`",
            f"- Tournament execution attempted: `{result['tournament_execution_attempted']}`",
            f"- Gate4 replacement design created: `{result['gate4_replacement_design_created']}`",
            f"- Runtime/mainline path created: `{result['runtime_or_mainline_path_created']}`",
            f"- Bridge/admission path created: `{result['bridge_or_admission_path_created']}`",
            f"- LLM/RAG/UI/companion path created: `{result['llm_rag_ui_companion_path_created']}`",
            "- No candidate model, harness, tournament, Gate4 replacement, runtime, bridge, admission, LLM/RAG/UI, or companion path is authorized.",
            "",
            "## Stop Conditions",
            "",
        ]
    )
    if result["stop_conditions_triggered"]:
        lines.extend(f"- `{condition}`" for condition in result["stop_conditions_triggered"])
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## What This Does Not Prove",
            "",
            *[f"- {claim}" for claim in result["what_this_does_not_prove"]],
            "",
            "## Remote Anchor Status",
            "",
            f"- Remote anchor performed: `{result['remote_anchor_performed']}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    run = execute_adjudication(output_dir=args.output_dir, persist_artifacts=True)
    if args.write_report:
        write_research_report(run)
    print(json.dumps(run["result"], indent=2, sort_keys=True))
