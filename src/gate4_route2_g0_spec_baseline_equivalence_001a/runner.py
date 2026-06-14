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


VERDICT_CLOSED = "gate4_route2_g0_spec_baseline_equivalence_001a_route2_closed_by_baseline_equivalence"
VERDICT_BLOCKED_UNDERSPECIFIED = (
    "gate4_route2_g0_spec_baseline_equivalence_001a_route2_blocked_by_underspecification"
)
VERDICT_SURVIVES = "gate4_route2_g0_spec_baseline_equivalence_001a_route2_survives_spec_level_only"
VERDICT_POSITIVE_CONTROL_FAILURE = (
    "gate4_route2_g0_spec_baseline_equivalence_001a_blocked_by_positive_control_failure"
)
VERDICT_FORBIDDEN_ACTION = "gate4_route2_g0_spec_baseline_equivalence_001a_blocked_by_forbidden_action"

BASELINE_IDS = [
    "dyna_q",
    "prioritized_sweeping",
    "pomdp_belief_control",
    "causal_bandit",
    "model_predictive_control",
    "retrieval_table_lookup",
    "static_rule_formula_decoder",
    "independent_module_ensemble",
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
    "dyna_q": {
        "required": {"model_learning", "simulated_replay", "value_update"},
        "description": "Model learning plus simulated replay for value update.",
    },
    "prioritized_sweeping": {
        "required": {"priority_by_prediction_error", "replay_queue", "value_update"},
        "description": "Replay prioritized by prediction error or value impact.",
    },
    "pomdp_belief_control": {
        "required": {"belief_state_update", "policy_from_belief"},
        "description": "Hidden belief-state update with control from the belief state.",
    },
    "causal_bandit": {
        "required": {"intervention_effect_estimation", "expected_reward_action_selection"},
        "description": "Intervention reward-effect estimation followed by value-maximizing action.",
    },
    "model_predictive_control": {
        "required": {"roll_forward_model", "action_sequence_optimization"},
        "description": "Rolling forward a model and selecting the best action sequence.",
    },
    "retrieval_table_lookup": {
        "required": {"nearest_trace_retrieval", "table_lookup", "cached_episode_selection"},
        "description": "Behavior selected from a nearest trace, cached episode, ID, table, or trace order.",
    },
    "static_rule_formula_decoder": {
        "required": {"static_rule", "static_formula_decoder"},
        "description": "Static rule or formula decoder with no update-sensitive mechanism.",
    },
    "independent_module_ensemble": {
        "required": {"independent_modules", "no_shared_latent_state"},
        "description": "Independent modules without shared latent state or cross-context update transfer.",
    },
}

REQUIRED_SPEC_FIELDS = [
    "state_variables",
    "prediction_target",
    "action_selection_dependency",
    "feedback_signal",
    "update_rule",
    "replay_consolidation_role",
    "self_boundary_or_context_boundary",
    "viability_value_relevance",
    "social_inference_relevance",
    "prediction_error_update_effect",
    "downstream_behavior_change",
    "not_cached_retrieval_rationale",
]

REQUIRED_BASELINE_CONTRASTS = set(BASELINE_IDS)
LEAKAGE_FORBIDDEN_TERMS = {
    "row_id",
    "partner_id",
    "context_id",
    "trace_order",
    "target_field",
    "static_formula",
    "table_lookup",
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

NEGATIVE_EVIDENCE_PATH = Path(
    "artifacts/gate4_replacement_discriminative_social_latent_execution_card_001a/negative_evidence_inheritance.json"
)


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


def _safe_git(args: list[str]) -> str:
    try:
        return _git(args)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


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


def _has_label_terms_without_computation_change(spec: dict[str, Any]) -> bool:
    novelty_terms = {str(term).lower() for term in spec.get("novelty_terms", [])}
    features = _features(spec)
    if not novelty_terms.intersection(LABEL_ONLY_TERMS):
        return False
    concrete_features = features.difference({"label_renaming", "replay_label", "self_label"})
    return not concrete_features


def _has_forbidden_shortcut(spec: dict[str, Any]) -> bool:
    features = _features(spec)
    if features.intersection(FORBIDDEN_SHORTCUT_FEATURES):
        return True
    shortcut_access = spec.get("shortcut_access", [])
    if isinstance(shortcut_access, str):
        shortcut_access = [shortcut_access]
    return bool({str(item) for item in shortcut_access}.intersection(LEAKAGE_FORBIDDEN_TERMS))


def _has_non_table_shared_state(spec: dict[str, Any]) -> bool:
    if spec.get("shared_internal_state_type") == "non_table_shared_latent_state":
        return True
    text = _canonical_text(spec.get("state_variables", "")) + " " + _canonical_text(
        spec.get("shared_internal_state", "")
    )
    lowered = text.lower()
    if not lowered.strip():
        return False
    forbidden = ["table", "trace cache", "cached", "lookup", "pomdp belief label", "belief label"]
    return "shared" in lowered and not any(term in lowered for term in forbidden)


def _has_cross_context_observable(spec: dict[str, Any]) -> bool:
    text = (
        _canonical_text(spec.get("prediction_error_update_effect", ""))
        + " "
        + _canonical_text(spec.get("cross_context_action_selection_observable", ""))
    ).lower()
    return all(term in text for term in ["support-disjoint", "context", "action selection"])


def _replay_changes_future_action_without_leakage(spec: dict[str, Any]) -> bool:
    text = _canonical_text(spec.get("replay_consolidation_role", "")).lower()
    return "future action selection" in text and "without direct target leakage" in text


def _has_complete_baseline_contrast(spec: dict[str, Any]) -> bool:
    contrasts = spec.get("baseline_contrasts", {})
    return isinstance(contrasts, dict) and REQUIRED_BASELINE_CONTRASTS.issubset(set(contrasts))


def _has_future_observable(spec: dict[str, Any]) -> bool:
    text = _canonical_text(spec.get("minimal_future_observable", "")).lower()
    return "anti-lookup" in text and "heldout" in text and "observable" in text


def _has_required_ablation(spec: dict[str, Any]) -> bool:
    text = _canonical_text(spec.get("required_ablation", "")).lower()
    return all(term in text for term in ["remove", "route2-specific", "collapse"])


def _has_leakage_check(spec: dict[str, Any]) -> bool:
    check = spec.get("leakage_check", {})
    if not isinstance(check, dict):
        return False
    forbidden = {str(item) for item in check.get("forbidden_fields", [])}
    return LEAKAGE_FORBIDDEN_TERMS.issubset(forbidden) and check.get("positive_control_required") is True


def _has_replay_recomputation_requirement(spec: dict[str, Any]) -> bool:
    text = _canonical_text(spec.get("replay_recomputation_requirement", "")).lower()
    return (
        "serialized state" in text
        and "new observation" in text
        and "stored answer" in text
        and "forbidden" in text
    )


def evaluate_non_equivalence_requirements(spec: dict[str, Any]) -> dict[str, Any]:
    criteria = [
        (
            "shared_internal_state_not_table_cache_or_belief_label",
            _has_non_table_shared_state(spec),
            "missing_shared_internal_state",
        ),
        (
            "prediction_error_update_changes_support_disjoint_action_selection",
            _has_cross_context_observable(spec),
            "missing_cross_context_action_selection_observable",
        ),
        (
            "replay_changes_future_action_selection_without_target_leakage",
            _replay_changes_future_action_without_leakage(spec),
            "missing_replay_action_effect_or_target_leakage_guard",
        ),
        ("baseline_contrast_covers_all_required_families", _has_complete_baseline_contrast(spec), "missing_baseline_contrast"),
        ("minimal_future_observable_under_anti_lookup_protocol", _has_future_observable(spec), "missing_future_observable"),
        ("required_route2_specific_ablation", _has_required_ablation(spec), "missing_required_ablation"),
        ("leakage_check_forbids_required_shortcuts", _has_leakage_check(spec), "missing_leakage_check_terms"),
        ("replay_recomputes_from_serialized_state_plus_new_observation", _has_replay_recomputation_requirement(spec), "missing_replay_recomputation_requirement"),
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
        extra_non_label_features = features.difference(signature).difference({"label_renaming", "replay_label", "self_label"})
        if not extra_non_label_features:
            classification = "equivalent"
        else:
            classification = "subset_of_baseline"
        reason = f"Spec computational steps are covered by {baseline_id}: {BASELINE_SIGNATURES[baseline_id]['description']}"
    elif baseline_id == "retrieval_table_lookup" and _has_forbidden_shortcut(spec):
        classification = "baseline_subsumes_spec"
        reason = "Spec exposes lookup, identity, target, trace-order, cached episode, table, or static shortcut material."
    elif baseline_id == "static_rule_formula_decoder" and features.intersection({"static_formula_decoder", "static_rule"}):
        classification = "baseline_subsumes_spec"
        reason = "Spec can be represented as a static rule or formula decoder."
    elif baseline_id == "independent_module_ensemble" and "independent_modules" in features and "shared_internal_state" not in features:
        classification = "baseline_subsumes_spec"
        reason = "Spec composes independent modules without a shared latent state."
    elif _has_label_terms_without_computation_change(spec):
        classification = "underspecified"
        reason = "Spec uses Route2 labels without a computation-changing observable."
    elif missing:
        classification = "underspecified"
        reason = "Spec omits required bounded computation fields."
    elif requirement_report["passed"] and not _has_forbidden_shortcut(spec):
        classification = "non_equivalent_with_required_observable"
        reason = "Spec includes the required support-disjoint cross-context observable, baseline contrast, ablation, leakage, and replay recomputation contract."
    else:
        classification = "not_distinguishable_from_baseline"
        reason = "Spec does not provide enough observable contrast to distinguish it from faithful baseline implementations."

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
        "context_ids": [],
        "episode_ids": [],
        "aggregation_rule": "single spec-level classification by callable baseline-family adjudicator",
    }


def adjudicate_dyna_q(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "dyna_q", "adjudicate_dyna_q")


def adjudicate_prioritized_sweeping(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "prioritized_sweeping", "adjudicate_prioritized_sweeping")


def adjudicate_pomdp_belief_control(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "pomdp_belief_control", "adjudicate_pomdp_belief_control")


def adjudicate_causal_bandit(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "causal_bandit", "adjudicate_causal_bandit")


def adjudicate_model_predictive_control(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "model_predictive_control", "adjudicate_model_predictive_control")


def adjudicate_retrieval_table_lookup(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "retrieval_table_lookup", "adjudicate_retrieval_table_lookup")


def adjudicate_static_rule_formula_decoder(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "static_rule_formula_decoder", "adjudicate_static_rule_formula_decoder")


def adjudicate_independent_module_ensemble(spec: dict[str, Any]) -> dict[str, Any]:
    return _baseline_classification(spec, "independent_module_ensemble", "adjudicate_independent_module_ensemble")


BASELINE_ADJUDICATORS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "dyna_q": adjudicate_dyna_q,
    "prioritized_sweeping": adjudicate_prioritized_sweeping,
    "pomdp_belief_control": adjudicate_pomdp_belief_control,
    "causal_bandit": adjudicate_causal_bandit,
    "model_predictive_control": adjudicate_model_predictive_control,
    "retrieval_table_lookup": adjudicate_retrieval_table_lookup,
    "static_rule_formula_decoder": adjudicate_static_rule_formula_decoder,
    "independent_module_ensemble": adjudicate_independent_module_ensemble,
}


def resolve_baseline_adjudicator(producer_function: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
    producers = {
        "adjudicate_dyna_q": adjudicate_dyna_q,
        "adjudicate_prioritized_sweeping": adjudicate_prioritized_sweeping,
        "adjudicate_pomdp_belief_control": adjudicate_pomdp_belief_control,
        "adjudicate_causal_bandit": adjudicate_causal_bandit,
        "adjudicate_model_predictive_control": adjudicate_model_predictive_control,
        "adjudicate_retrieval_table_lookup": adjudicate_retrieval_table_lookup,
        "adjudicate_static_rule_formula_decoder": adjudicate_static_rule_formula_decoder,
        "adjudicate_independent_module_ensemble": adjudicate_independent_module_ensemble,
    }
    return producers[producer_function]


def _strongest_classification(rows: dict[str, dict[str, Any]]) -> str:
    classifications = {row["classification"] for row in rows.values()}
    for classification in CLASSIFICATION_PRIORITY:
        if classification in classifications:
            return classification
    return "underspecified"


def adjudicate_route2_spec(spec: dict[str, Any]) -> dict[str, Any]:
    rows = {baseline_id: adjudicator(spec) for baseline_id, adjudicator in BASELINE_ADJUDICATORS.items()}
    missing = missing_required_spec_fields(spec)
    requirement_report = evaluate_non_equivalence_requirements(spec)
    blocking_reasons = []
    if missing:
        blocking_reasons.append("missing_required_spec_fields")
    if _has_label_terms_without_computation_change(spec):
        blocking_reasons.append("label_terms_without_computation_change")
    if _has_forbidden_shortcut(spec):
        blocking_reasons.append("forbidden_lookup_or_identity_shortcut")
    blocking_reasons.extend(requirement_report["blocking_reasons"])
    baseline_equivalence = any(
        row["classification"] in {"equivalent", "subset_of_baseline", "baseline_subsumes_spec"}
        for row in rows.values()
    )
    survives = not baseline_equivalence and not missing and requirement_report["passed"] and not _has_label_terms_without_computation_change(spec)
    if survives:
        verdict = VERDICT_SURVIVES
        next_allowed_action = "separate_future_anti_lookup_generative_heldout_surface_design_task_only"
    elif baseline_equivalence:
        verdict = VERDICT_CLOSED
        next_allowed_action = "route_to_composite_cross_task_state_reuse_framing_as_separate_route_design_task"
    else:
        verdict = VERDICT_BLOCKED_UNDERSPECIFIED
        next_allowed_action = "route_to_composite_cross_task_state_reuse_framing_as_separate_route_design_task"

    return {
        "producer_function": "adjudicate_route2_spec",
        "spec_id": spec.get("spec_id", ""),
        "verdict": verdict,
        "survives": survives,
        "baseline_equivalence_or_subsumption": baseline_equivalence,
        "baseline_rows": rows,
        "strongest_classification": _strongest_classification(rows),
        "required_observable_present": requirement_report["passed"],
        "non_equivalence_requirements": requirement_report,
        "missing_required_spec_fields": missing,
        "blocking_reasons": sorted(set(blocking_reasons)),
        "candidate_code_executed": False,
        "candidate_score_produced": False,
        "tournament_execution_attempted": False,
        "gate4_replacement_design_created": False,
        "runtime_or_mainline_path_created": False,
        "bridge_or_admission_path_created": False,
        "next_allowed_action": next_allowed_action,
        "claim_ceiling": CLAIM_CEILING,
    }


def _base_spec(spec_id: str) -> dict[str, Any]:
    return {
        "spec_id": spec_id,
        "task_id": TASK_CARD_ID,
        "source_artifact": "callable_positive_control_fixture",
        "state_variables": "finite task state",
        "prediction_target": "next value-relevant outcome",
        "action_selection_dependency": "action selected from current computed estimate",
        "feedback_signal": "prediction error or reward feedback",
        "update_rule": "update current estimate from feedback",
        "replay_consolidation_role": "local replay changes same-task estimates only",
        "self_boundary_or_context_boundary": "task-local context boundary",
        "viability_value_relevance": "reward or expected value relevance",
        "social_inference_relevance": "none",
        "prediction_error_update_effect": "updates the same context estimate",
        "downstream_behavior_change": "same context action may change",
        "not_cached_retrieval_rationale": "",
        "baseline_contrasts": {},
        "minimal_future_observable": "",
        "required_ablation": "",
        "leakage_check": {"forbidden_fields": [], "positive_control_required": False},
        "replay_recomputation_requirement": "",
        "computational_steps": [],
        "novelty_terms": [],
    }


def build_dyna_q_positive_control() -> dict[str, Any]:
    spec = _base_spec("positive_control_dyna_q_rename")
    spec.update(
        {
            "computational_steps": ["model_learning", "simulated_replay", "value_update"],
            "replay_consolidation_role": "simulated replay updates value estimates exactly as Dyna-Q.",
            "not_cached_retrieval_rationale": "renamed Route2 replay, no extra observable",
        }
    )
    return spec


def build_prioritized_sweeping_positive_control() -> dict[str, Any]:
    spec = _base_spec("positive_control_prioritized_sweeping_rename")
    spec.update(
        {
            "computational_steps": ["priority_by_prediction_error", "replay_queue", "value_update"],
            "replay_consolidation_role": "prediction-error priority queue controls replay order.",
        }
    )
    return spec


def build_pomdp_positive_control() -> dict[str, Any]:
    spec = _base_spec("positive_control_pomdp_belief_control")
    spec.update(
        {
            "computational_steps": ["belief_state_update", "policy_from_belief"],
            "state_variables": "POMDP belief state over hidden partner mode",
            "action_selection_dependency": "policy from belief state",
        }
    )
    return spec


def build_causal_bandit_positive_control() -> dict[str, Any]:
    spec = _base_spec("positive_control_causal_bandit")
    spec.update(
        {
            "computational_steps": ["intervention_effect_estimation", "expected_reward_action_selection"],
            "prediction_target": "intervention reward effect",
            "action_selection_dependency": "expected reward maximization",
        }
    )
    return spec


def build_mpc_positive_control() -> dict[str, Any]:
    spec = _base_spec("positive_control_mpc")
    spec.update(
        {
            "computational_steps": ["roll_forward_model", "action_sequence_optimization"],
            "prediction_target": "rolled-forward future state sequence",
            "action_selection_dependency": "best scored action sequence",
        }
    )
    return spec


def build_retrieval_positive_control() -> dict[str, Any]:
    spec = _base_spec("positive_control_retrieval_table_lookup")
    spec.update(
        {
            "computational_steps": [
                "nearest_trace_retrieval",
                "table_lookup",
                "cached_episode_selection",
                "row_id_lookup",
                "partner_id_lookup",
                "trace_order_lookup",
            ],
            "state_variables": "trace cache, row ID, partner ID, context ID, and table lookup keys",
            "action_selection_dependency": "nearest previous trace or cached table entry",
            "not_cached_retrieval_rationale": "",
        }
    )
    return spec


def build_label_renaming_positive_control() -> dict[str, Any]:
    return {
        "spec_id": "positive_control_label_renaming_novelty",
        "task_id": TASK_CARD_ID,
        "source_artifact": "callable_positive_control_fixture",
        "state_variables": "self latent viability consolidation words",
        "prediction_target": "",
        "action_selection_dependency": "",
        "feedback_signal": "",
        "update_rule": "",
        "replay_consolidation_role": "replay is named consolidation",
        "self_boundary_or_context_boundary": "self-boundary label",
        "viability_value_relevance": "viability label",
        "social_inference_relevance": "social inference label",
        "prediction_error_update_effect": "",
        "downstream_behavior_change": "",
        "not_cached_retrieval_rationale": "",
        "baseline_contrasts": {},
        "minimal_future_observable": "",
        "required_ablation": "",
        "leakage_check": {"forbidden_fields": [], "positive_control_required": False},
        "replay_recomputation_requirement": "",
        "computational_steps": ["label_renaming", "replay_label", "self_label"],
        "novelty_terms": ["self", "viability", "latent", "consolidation", "social inference"],
    }


def build_minimal_route2_like_spec() -> dict[str, Any]:
    contrasts = {
        baseline_id: f"{baseline_id} should fail without the shared support-disjoint Route2-specific state update."
        for baseline_id in BASELINE_IDS
    }
    return {
        "spec_id": "minimal_non_equivalence_fixture_route2_spec_level_only",
        "task_id": TASK_CARD_ID,
        "source_artifact": "callable_non_equivalence_fixture_not_candidate_code",
        "state_variables": "shared latent state vector across support-disjoint contexts, not a table, trace cache, lookup, or POMDP belief label",
        "shared_internal_state_type": "non_table_shared_latent_state",
        "shared_internal_state": "shared latent state updated by prediction error across contexts",
        "prediction_target": "future action-relevant response under a new support-disjoint context",
        "action_selection_dependency": "action selection reads the updated shared state rather than a context-local table",
        "feedback_signal": "prediction error between expected and observed context response",
        "update_rule": "prediction-error update modifies the shared state before later support-disjoint action selection",
        "replay_consolidation_role": "replay/consolidation changes future action selection without direct target leakage",
        "self_boundary_or_context_boundary": "explicit context boundary separating source update context from heldout action context",
        "viability_value_relevance": "value relevance enters only through the post-update action-selection objective",
        "social_inference_relevance": "social inference relevance is limited to future testable partner-behavior observable",
        "prediction_error_update_effect": "prediction-error update in source context changes action selection in a support-disjoint heldout context",
        "cross_context_action_selection_observable": "support-disjoint context action selection changes after source-context prediction error update",
        "downstream_behavior_change": "heldout action selection changes after replay without revealing target labels",
        "not_cached_retrieval_rationale": "requires support-disjoint transfer from shared state, not cached retrieval, row ID, trace order, or table lookup",
        "baseline_contrasts": contrasts,
        "minimal_future_observable": "observable under the anti-lookup generative heldout protocol: source-context prediction error changes heldout action selection while lookup baselines fail",
        "required_ablation": "remove the Route2-specific cross-context consolidation step and require collapse of the support-disjoint transfer effect",
        "leakage_check": {
            "forbidden_fields": sorted(LEAKAGE_FORBIDDEN_TERMS),
            "positive_control_required": True,
        },
        "replay_recomputation_requirement": "recompute behavior from serialized state plus new observation; stored answer replay is forbidden",
        "computational_steps": [
            "shared_internal_state",
            "prediction_error_update",
            "support_disjoint_cross_context_transfer",
            "route2_specific_consolidation",
            "future_action_selection_change",
        ],
        "novelty_terms": [],
    }


def build_positive_control_specs() -> dict[str, dict[str, Any]]:
    return {
        "dyna_q_rename_control": build_dyna_q_positive_control(),
        "prioritized_sweeping_rename_control": build_prioritized_sweeping_positive_control(),
        "pomdp_belief_control": build_pomdp_positive_control(),
        "causal_bandit_control": build_causal_bandit_positive_control(),
        "mpc_control": build_mpc_positive_control(),
        "retrieval_control": build_retrieval_positive_control(),
        "label_renaming_novelty_control": build_label_renaming_positive_control(),
    }


def discover_prior_route2_references() -> list[dict[str, Any]]:
    raw = _safe_git(["grep", "-n", "-i", "route2", "HEAD", "--", "docs", "src", "tests", "artifacts"])
    ignored_markers = {
        TASK_ID.lower(),
        TASK_CARD_ID.lower(),
        REPORT_NAME.lower(),
    }
    references = []
    for line in raw.splitlines():
        if not line.startswith("HEAD:"):
            continue
        rest = line[len("HEAD:") :]
        parts = rest.split(":", 2)
        if len(parts) != 3:
            continue
        path, line_number, text = parts
        lowered_path = path.lower().replace("\\", "/")
        if any(marker.lower() in lowered_path for marker in ignored_markers):
            continue
        references.append({"path": path, "line": int(line_number), "text": text[:240]})
    return references


def build_current_route2_candidate_step_spec(run_id: str = "") -> dict[str, Any]:
    prior_references = discover_prior_route2_references()
    return {
        "spec_id": "current_repo_route2_candidate_step_readback",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "source_artifact": "current_repo_git_grep_route2_readback_excluding_current_task_paths",
        "spec_status": "no_concrete_route2_candidate_step_found" if not prior_references else "route2_mentions_found_without_bounded_candidate_step_spec",
        "prior_route2_references": prior_references,
        "state_variables": "",
        "prediction_target": "",
        "action_selection_dependency": "",
        "feedback_signal": "",
        "update_rule": "",
        "replay_consolidation_role": "",
        "self_boundary_or_context_boundary": "",
        "viability_value_relevance": "",
        "social_inference_relevance": "",
        "prediction_error_update_effect": "",
        "downstream_behavior_change": "",
        "not_cached_retrieval_rationale": "",
        "baseline_contrasts": {},
        "minimal_future_observable": "",
        "required_ablation": "",
        "leakage_check": {"forbidden_fields": [], "positive_control_required": False},
        "replay_recomputation_requirement": "",
        "computational_steps": [],
        "novelty_terms": [],
        "claim_ceiling": CLAIM_CEILING,
    }


def run_positive_controls() -> dict[str, Any]:
    expected_families = {
        "dyna_q_rename_control": "dyna_q",
        "prioritized_sweeping_rename_control": "prioritized_sweeping",
        "pomdp_belief_control": "pomdp_belief_control",
        "causal_bandit_control": "causal_bandit",
        "mpc_control": "model_predictive_control",
        "retrieval_control": "retrieval_table_lookup",
        "label_renaming_novelty_control": "label_renaming",
    }
    control_results = {}
    for control_id, spec in build_positive_control_specs().items():
        adjudication = adjudicate_route2_spec(spec)
        expected_family = expected_families[control_id]
        rejected = adjudication["survives"] is False
        if expected_family == "label_renaming":
            family_rejected = "label_terms_without_computation_change" in adjudication["blocking_reasons"]
        else:
            family_rejected = adjudication["baseline_rows"][expected_family]["classification"] in {
                "equivalent",
                "subset_of_baseline",
                "baseline_subsumes_spec",
            }
        control_results[control_id] = {
            "control_id": control_id,
            "spec": spec,
            "expected_rejection_family": expected_family,
            "survives": adjudication["survives"],
            "verdict": adjudication["verdict"],
            "strongest_classification": adjudication["strongest_classification"],
            "required_observable_present": adjudication["required_observable_present"],
            "baseline_rows": adjudication["baseline_rows"],
            "blocking_reasons": adjudication["blocking_reasons"],
            "rejected_as_expected": rejected and family_rejected,
            "candidate_code_executed": False,
        }
    return {
        "producer_function": "run_positive_controls",
        "task_id": TASK_CARD_ID,
        "control_results": control_results,
        "all_positive_controls_rejected": all(row["rejected_as_expected"] for row in control_results.values()),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_baseline_equivalence_matrix(candidate_adjudication: dict[str, Any], positive_controls: dict[str, Any]) -> dict[str, Any]:
    return {
        "producer_function": "build_baseline_equivalence_matrix",
        "task_id": TASK_CARD_ID,
        "candidate_spec_id": candidate_adjudication["spec_id"],
        "candidate_spec_rows": candidate_adjudication["baseline_rows"],
        "candidate_verdict": candidate_adjudication["verdict"],
        "positive_control_summary": {
            control_id: {
                "survives": row["survives"],
                "verdict": row["verdict"],
                "strongest_classification": row["strongest_classification"],
                "expected_rejection_family": row["expected_rejection_family"],
                "rejected_as_expected": row["rejected_as_expected"],
            }
            for control_id, row in positive_controls["control_results"].items()
        },
        "adjudication_classes": list(CLASSIFICATION_PRIORITY),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_non_equivalence_requirements(candidate_spec: dict[str, Any]) -> dict[str, Any]:
    candidate_report = evaluate_non_equivalence_requirements(candidate_spec)
    minimal_fixture = build_minimal_route2_like_spec()
    fixture_report = evaluate_non_equivalence_requirements(minimal_fixture)
    return {
        "producer_function": "build_non_equivalence_requirements",
        "task_id": TASK_CARD_ID,
        "required_non_equivalence_criteria": [
            "shared internal state not merely table, trace cache, or POMDP belief label",
            "prediction-error update in one context changes action selection in a support-disjoint context",
            "replay/consolidation changes future action selection without direct target leakage",
            "baseline contrasts cover Dyna-Q, prioritized sweeping, POMDP, causal bandit, MPC, retrieval/table lookup, static formula, and independent ensemble",
            "minimal future observable under anti-lookup generative heldout protocol",
            "required ablation removes the Route2-specific step and should collapse cross-context transfer",
            "leakage check forbids row ID, partner ID, context ID, trace order, target field, static formula, and table lookup shortcuts",
            "replay recomputes from serialized state plus new observation, not stored answer replay",
        ],
        "candidate_spec_evaluation": candidate_report,
        "minimal_non_equivalence_fixture_evaluation": fixture_report,
        "minimal_non_equivalence_fixture_is_not_candidate_code": True,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_claim_ceiling() -> dict[str, Any]:
    return {
        "producer_function": "build_claim_ceiling",
        "task_id": TASK_CARD_ID,
        "claim_ceiling": CLAIM_CEILING,
        "allowed_claims": [
            "callable spec-level baseline-equivalence adjudication",
            "positive-control rejection at spec level",
            "current Route2 blocked or closed at governance level",
            "future observable requirements only",
        ],
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
    }


def build_inherited_negative_evidence_readback() -> dict[str, Any]:
    path = repo_root() / NEGATIVE_EVIDENCE_PATH
    if not path.exists():
        return {
            "producer_function": "build_inherited_negative_evidence_readback",
            "source_path": str(NEGATIVE_EVIDENCE_PATH).replace("\\", "/"),
            "source_exists": False,
            "stream_keyed_count_table_collapse_preserved": False,
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    gate4 = payload.get("gate4_001c_001e_negative_evidence", {})
    return {
        "producer_function": "build_inherited_negative_evidence_readback",
        "source_path": str(NEGATIVE_EVIDENCE_PATH).replace("\\", "/"),
        "source_exists": True,
        "inherited_task_id": payload.get("task_id"),
        "negative_evidence_commit": gate4.get("commit"),
        "candidate_score_prior_negative_evidence_only": gate4.get("candidate_score_prior_negative_evidence_only"),
        "stream_keyed_count_table_challenger_score_prior_negative_evidence_only": gate4.get(
            "stream_keyed_count_table_challenger_score_prior_negative_evidence_only"
        ),
        "candidate_advantage_collapsed": gate4.get("candidate_advantage_collapsed"),
        "strongest_surviving_explanation": gate4.get("strongest_surviving_explanation"),
        "stream_keyed_count_table_collapse_preserved": gate4.get("candidate_advantage_collapsed") is True
        and gate4.get("stream_keyed_count_table_challenger_score_prior_negative_evidence_only") == 1.0,
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
    return {
        "producer_function": "build_forbidden_action_guard",
        "task_id": TASK_CARD_ID,
        "changed_or_new_paths": paths,
        "forbidden_files_modified": forbidden_paths,
        "candidate_code_created": False,
        "candidate_score_produced": False,
        "tournament_execution_attempted": False,
        "gate4_replacement_design_created": False,
        "gate4_repair_or_rerun_attempted": False,
        "runtime_or_mainline_path_created": False,
        "bridge_or_admission_path_created": False,
        "llm_rag_ui_companion_path_created": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_future_surface_requirements(candidate_adjudication: dict[str, Any]) -> dict[str, Any]:
    if candidate_adjudication["verdict"] == VERDICT_SURVIVES:
        next_action = "separate future task to design an anti-lookup generative heldout surface"
    else:
        next_action = "route to composite cross-task state reuse framing as a separate route-design task; do not repair replay in-place"
    return {
        "producer_function": "build_future_surface_requirements",
        "task_id": TASK_CARD_ID,
        "candidate_verdict": candidate_adjudication["verdict"],
        "next_minimal_closed_loop_action": next_action,
        "if_route2_survives_only_allowed_next_action": "separate future task to design an anti-lookup generative heldout surface",
        "if_route2_killed_or_blocked_next_action": "route to composite cross-task state reuse framing as a separate route-design task",
        "candidate_implementation_authorized": False,
        "harness_authorized": False,
        "tournament_execution_authorized": False,
        "gate4_replacement_authorized": False,
        "runtime_or_ego_mainline_authorized": False,
        "bridge_or_admission_authorized": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def compute_result(
    *,
    candidate_adjudication: dict[str, Any],
    positive_controls: dict[str, Any],
    inherited: dict[str, Any],
    forbidden_guard: dict[str, Any],
    future_surface_requirements: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    stop_conditions = []
    if not positive_controls["all_positive_controls_rejected"]:
        stop_conditions.append("positive_control_failure")
    if not inherited["stream_keyed_count_table_collapse_preserved"]:
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
    if candidate_adjudication["verdict"] == VERDICT_BLOCKED_UNDERSPECIFIED:
        stop_conditions.append("route2_candidate_step_spec_underspecified")

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
    else:
        verdict = candidate_adjudication["verdict"]

    return {
        "producer_function": "compute_result",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "verdict": verdict,
        "current_layer": "engineering-governance / route-spec baseline-equivalence preflight only",
        "mainline_integration_status": "not integrated",
        "enabled_status": "no runtime, no bridge/admission, no Gate4 replacement, no candidate implementation, no tournament execution, no trigger path",
        "real_trigger_evidence": "Callable spec-level adjudicators executed against current repository Route2 readback and required positive controls; no candidate code or tournament path executed.",
        "claim_ceiling": CLAIM_CEILING,
        "stop_conditions_triggered": sorted(set(stop_conditions)),
        "positive_controls_all_rejected": positive_controls["all_positive_controls_rejected"],
        "equivalence_adjudicators_callable": all(
            row["callable_invoked"] for row in candidate_adjudication["baseline_rows"].values()
        ),
        "route2_survives_spec_level_only": candidate_adjudication["verdict"] == VERDICT_SURVIVES,
        "route2_closed_by_baseline_equivalence": candidate_adjudication["verdict"] == VERDICT_CLOSED,
        "route2_blocked_by_underspecification": candidate_adjudication["verdict"] == VERDICT_BLOCKED_UNDERSPECIFIED,
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
    candidate_spec = build_current_route2_candidate_step_spec(run_id=run_id)
    candidate_adjudication = adjudicate_route2_spec(candidate_spec)
    positive_controls = run_positive_controls()
    inherited = build_inherited_negative_evidence_readback()
    matrix = build_baseline_equivalence_matrix(candidate_adjudication, positive_controls)
    non_equivalence_requirements = build_non_equivalence_requirements(candidate_spec)
    future_surface_requirements = build_future_surface_requirements(candidate_adjudication)
    claim_ceiling = build_claim_ceiling()
    forbidden_guard = build_forbidden_action_guard()
    result = compute_result(
        candidate_adjudication=candidate_adjudication,
        positive_controls=positive_controls,
        inherited=inherited,
        forbidden_guard=forbidden_guard,
        future_surface_requirements=future_surface_requirements,
        run_id=run_id,
    )
    run = {
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "result": result,
        "route2_candidate_step_spec": candidate_spec,
        "route2_candidate_adjudication": candidate_adjudication,
        "baseline_equivalence_matrix": matrix,
        "positive_controls": positive_controls,
        "non_equivalence_requirements": non_equivalence_requirements,
        "future_surface_requirements": future_surface_requirements,
        "claim_ceiling": claim_ceiling,
        "inherited_negative_evidence_readback": inherited,
        "forbidden_action_guard": forbidden_guard,
    }
    if persist_artifacts:
        write_artifacts(_resolve_output_dir(output_dir), run)
    return run


def write_artifacts(out: Path, run: dict[str, Any]) -> None:
    artifact_map = {
        "result.json": run["result"],
        "baseline_equivalence_matrix.json": run["baseline_equivalence_matrix"],
        "route2_candidate_step_spec.json": run["route2_candidate_step_spec"],
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
    inherited = run["inherited_negative_evidence_readback"]
    controls = run["positive_controls"]["control_results"]
    candidate = run["route2_candidate_adjudication"]
    lines = [
        "# GATE4-ROUTE2-G0-SPEC-BASELINE-EQUIVALENCE-001A",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        "Layer: engineering-governance / route-spec baseline-equivalence preflight only.",
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
        "- Real objective: determine whether a proposed Route2 computation step is baseline-equivalent, underspecified, or spec-level non-equivalent before any harness, candidate, tournament, Gate4 replacement, runtime, or bridge work.",
        "- Strongest baseline explanation: Route2 is a renamed Dyna-Q, prioritized sweeping, POMDP belief-control, causal bandit, MPC, retrieval/table lookup, static decoder, or independent ensemble route.",
        "- Strongest reason the task may be invalid: no concrete Route2 computation spec exists in current repository evidence outside this task.",
        "- Falsifier for current framing: a bounded Route2 spec with a support-disjoint cross-context action-selection observable, full baseline contrast, ablation, leakage guard, and replay recomputation requirement.",
        "- Evidence still insufficient: any spec-level survival without a later generated heldout surface, executable baseline preflight, ablation rerun, leakage-positive control, and replay recomputation.",
        "- Mechanism status: this tests spec-level baseline distinguishability only, not mechanism validity.",
        "",
        "## Bounded Task Card",
        "",
        f"- Task id: `{TASK_CARD_ID}`",
        "- Problem definition: Route2 may be only replay/consolidation wording for known baselines.",
        "- Current stage/layer: engineering-governance / route-spec baseline-equivalence preflight.",
        "- Mainline target: none; not integrated.",
        "- Enabled-state requirement: no runtime, bridge/admission, Gate4 replacement, candidate implementation, tournament execution, or trigger path.",
        "- Real-trigger evidence requirement: callable adjudicators must execute on the current Route2 spec readback and required positive controls.",
        "- Hypothesis: a valid Route2 spec must include a concrete cross-context observable that faithful baselines should fail without adding the disputed mechanism.",
        "- Strongest baseline: Dyna-Q, prioritized sweeping, POMDP belief-state update/control, causal bandit, MPC, retrieval/table lookup, static decoder, and independent module ensemble.",
        "- Ablation requirement: remove the Route2-specific cross-context consolidation step and require collapse of cross-context transfer.",
        "- Trace/replay requirement: replay must recompute from serialized state plus new observation, not stored answer replay.",
        "- Computed-evidence provenance gate: each baseline-family row records producer function, input artifact, run id, aggregation rule, and code path hash.",
        "- Acceptance gate: positive controls rejected; adjudicators callable; Route2 closed, blocked, or spec-level survives; forbidden paths remain false.",
        f"- Claim ceiling: {CLAIM_CEILING}",
        "- Stop condition: positive-control failure, forbidden action, prior negative-evidence readback failure, baseline equivalence, or underspecified candidate step.",
        "- Rollback plan: remove only the isolated source package, focused test, report, and artifact directory for this task.",
        f"- Expected changed files: `src/{TASK_ID}/`, `tests/test_{TASK_ID}.py`, `artifacts/{TASK_ID}/`, and `docs/research/{REPORT_NAME}`.",
        "- Forbidden changes: candidate model code, candidate score, harness, tournament execution, Gate4 replacement design, runtime, bridge/admission, EGO-mainline, LLM/RAG/UI/companion paths.",
        "- Auto-Remote-Anchor decision: conditional.",
        "",
        "## Inherited Negative Evidence",
        "",
        f"- Source path: `{inherited['source_path']}`",
        f"- Source exists: `{inherited['source_exists']}`",
        f"- Candidate score, prior negative evidence only: `{inherited.get('candidate_score_prior_negative_evidence_only')}`",
        f"- stream-keyed count-table challenger score, prior negative evidence only: `{inherited.get('stream_keyed_count_table_challenger_score_prior_negative_evidence_only')}`",
        f"- Candidate advantage collapsed: `{inherited.get('candidate_advantage_collapsed')}`",
        f"- Strongest surviving explanation: `{inherited.get('strongest_surviving_explanation')}`",
        "",
        "## Current Route2 Spec Readback",
        "",
        f"- Spec status: `{run['route2_candidate_step_spec']['spec_status']}`",
        f"- Prior Route2 references found outside current task paths: `{len(run['route2_candidate_step_spec']['prior_route2_references'])}`",
        f"- Candidate adjudication verdict: `{candidate['verdict']}`",
        f"- Candidate blocking reasons: `{candidate['blocking_reasons']}`",
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
            "- If Route2 survives in a future spec, the only allowed next action is a separate future anti-lookup generative heldout surface design task.",
            "- If Route2 remains killed or blocked, route to composite cross-task state reuse framing as a separate route-design task.",
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
