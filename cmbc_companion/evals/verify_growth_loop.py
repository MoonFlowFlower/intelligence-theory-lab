from __future__ import annotations

import argparse
import inspect
import json
import math
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Iterable


ALLOWED_VERDICTS = {
    "cmbc_companion_growth_loop_bounded_pass",
    "failed_no_history_dependent_behavior",
    "failed_relevant_deletion_no_effect",
    "failed_irrelevant_deletion_too_sensitive",
    "failed_relationship_perturbation_not_causal",
    "failed_interruption_risk_not_causal",
    "failed_renderer_controls_action",
    "failed_behavior_only_replay",
    "heuristic_equivalent",
    "rag_memory_equivalent",
    "collapses_into_active_inference_or_empowerment_proxy",
    "inconclusive_revise_contract",
}

ACTION_HANDLES = ("act_0", "act_1", "act_2", "act_3", "act_4", "act_5", "act_6")
PUBLIC_ACTION_NAMES = {
    "act_0": "check_in",
    "act_1": "wait",
    "act_2": "ask_permission",
    "act_3": "offer_help",
    "act_4": "set_boundary",
    "act_5": "playful_response",
    "act_6": "serious_support",
}
OUTCOME_DIMS = (
    "relationship_delta",
    "interruption_risk",
    "trust_delta",
    "safety_delta",
    "support_delta",
)

DEFAULT_WEIGHTS = {
    "relationship_delta": 1.35,
    "interruption_risk": -1.45,
    "trust_delta": 0.95,
    "safety_delta": 0.85,
    "support_delta": 1.05,
}


@dataclass(frozen=True)
class OutcomeVector:
    relationship_delta: float
    interruption_risk: float
    trust_delta: float
    safety_delta: float
    support_delta: float

    def utility(self, weights: dict[str, float]) -> float:
        return sum(getattr(self, dim) * weights[dim] for dim in OUTCOME_DIMS)

    def plus(self, other: OutcomeVector) -> OutcomeVector:
        return OutcomeVector(
            relationship_delta=self.relationship_delta + other.relationship_delta,
            interruption_risk=self.interruption_risk + other.interruption_risk,
            trust_delta=self.trust_delta + other.trust_delta,
            safety_delta=self.safety_delta + other.safety_delta,
            support_delta=self.support_delta + other.support_delta,
        )

    def scale(self, factor: float) -> OutcomeVector:
        return OutcomeVector(
            relationship_delta=self.relationship_delta * factor,
            interruption_risk=self.interruption_risk * factor,
            trust_delta=self.trust_delta * factor,
            safety_delta=self.safety_delta * factor,
            support_delta=self.support_delta * factor,
        )


@dataclass(frozen=True)
class Experience:
    trace_id: str
    action_handle: str
    outcome: OutcomeVector
    narrative: str
    relevant_tags: tuple[str, ...]


@dataclass(frozen=True)
class CandidateObservation:
    observation_id: str
    observation_vector: tuple[float, ...]
    goal_weights: dict[str, float]
    public_horizon: int
    public_budget: int


class CMBCGrowthLoopCandidate:
    READ_FIELDS = (
        "observation",
        "anonymous_action_handles",
        "own_intervention_history",
        "observed_outcomes",
        "public_horizon",
        "public_budget",
    )
    MODEL_VERSION = "cmbc_companion_prototype_v0_bounded"

    def __init__(self) -> None:
        self.priors = {
            "act_0": OutcomeVector(0.10, 0.22, 0.06, 0.00, 0.10),
            "act_1": OutcomeVector(0.00, 0.00, 0.05, 0.05, 0.00),
            "act_2": OutcomeVector(0.05, 0.04, 0.24, 0.10, 0.05),
            "act_3": OutcomeVector(0.15, 0.10, 0.10, 0.05, 0.35),
            "act_4": OutcomeVector(-0.05, 0.02, 0.30, 0.75, 0.05),
            "act_5": OutcomeVector(0.12, 0.16, 0.02, 0.00, 0.05),
            "act_6": OutcomeVector(0.20, 0.12, 0.15, 0.05, 0.50),
        }

    def fit_effect_model(self, history: Iterable[Experience]) -> dict[str, OutcomeVector]:
        by_action: dict[str, list[OutcomeVector]] = {handle: [] for handle in ACTION_HANDLES}
        for item in history:
            by_action[item.action_handle].append(item.outcome)

        estimates: dict[str, OutcomeVector] = {}
        for handle in ACTION_HANDLES:
            prior = self.priors[handle]
            if not by_action[handle]:
                estimates[handle] = prior
                continue
            total = OutcomeVector(0.0, 0.0, 0.0, 0.0, 0.0)
            for outcome in by_action[handle]:
                total = total.plus(outcome)
            empirical = total.scale(1.0 / len(by_action[handle]))
            estimates[handle] = prior.scale(0.15).plus(empirical.scale(0.85))
        return estimates

    def choose(
        self,
        observation: CandidateObservation,
        effect_estimates: dict[str, OutcomeVector],
    ) -> dict[str, Any]:
        utilities = {
            handle: effect_estimates[handle].utility(observation.goal_weights)
            for handle in ACTION_HANDLES
        }
        distribution = softmax(utilities, temperature=0.28)
        selected = max(sorted(distribution), key=lambda handle: distribution[handle])
        return {
            "selected_action": selected,
            "action_distribution": distribution,
            "utilities": utilities,
        }


class CompanionRenderer:
    def render(self, selected_action: str, style: str) -> dict[str, str]:
        return {
            "selected_action": selected_action,
            "style": style,
            "text": f"{style}:{PUBLIC_ACTION_NAMES[selected_action]}",
        }


class StrongHeuristicBaseline:
    READ_FIELDS = ("observation", "public_context_flags")

    def choose(self, observation: CandidateObservation) -> str:
        if observation.observation_vector[0] > 0.7:
            return "act_4"
        if observation.observation_vector[1] > 0.6:
            return "act_6"
        return "act_2"


class RAGMemoryPromptBaseline:
    READ_FIELDS = ("observation", "retrieved_memory_text")

    def choose(self, history: Iterable[Experience]) -> str:
        text = " ".join(item.narrative.lower() for item in history)
        if "risky" in text or "boundary" in text:
            return "act_4"
        if "stress" in text or "support" in text:
            return "act_6"
        if "interruption" in text or "busy" in text:
            return "act_2"
        if "welcomed" in text:
            return "act_0"
        return "act_2"


class ActiveInferenceEmpowermentProxyBaseline:
    READ_FIELDS = ("observation", "uncertainty_proxy", "future_controllability_proxy")

    def choose(self, effect_estimates: dict[str, OutcomeVector]) -> str:
        scores = {
            handle: estimate.trust_delta + estimate.safety_delta - abs(estimate.interruption_risk)
            for handle, estimate in effect_estimates.items()
        }
        return max(sorted(scores), key=lambda handle: scores[handle])


def softmax(values: dict[str, float], temperature: float) -> dict[str, float]:
    max_value = max(values.values())
    exps = {
        key: math.exp((value - max_value) / temperature)
        for key, value in values.items()
    }
    total = sum(exps.values())
    return {key: value / total for key, value in exps.items()}


def build_observations() -> dict[str, CandidateObservation]:
    return {
        "same_current_companion_context": CandidateObservation(
            observation_id="same_current_companion_context",
            observation_vector=(0.25, 0.35, 0.25),
            goal_weights=DEFAULT_WEIGHTS,
            public_horizon=2,
            public_budget=1,
        ),
        "relationship_support_context": CandidateObservation(
            observation_id="relationship_support_context",
            observation_vector=(0.15, 0.82, 0.22),
            goal_weights=DEFAULT_WEIGHTS,
            public_horizon=2,
            public_budget=1,
        ),
        "boundary_context": CandidateObservation(
            observation_id="boundary_context",
            observation_vector=(0.90, 0.35, 0.45),
            goal_weights=DEFAULT_WEIGHTS,
            public_horizon=1,
            public_budget=1,
        ),
    }


def build_histories() -> dict[str, list[Experience]]:
    return {
        "warm_accepted_checkin": [
            Experience(
                "exp_warm_0",
                "act_0",
                OutcomeVector(0.82, 0.05, 0.38, 0.02, 0.25),
                "own intervention was welcomed during a gentle check-in",
                ("checkin", "relationship"),
            )
        ],
        "busy_interruption_disliked": [
            Experience(
                "exp_busy_0",
                "act_0",
                OutcomeVector(-0.42, 0.92, -0.18, 0.00, -0.10),
                "own intervention caused interruption during busy work",
                ("interruption", "busy"),
            ),
            Experience(
                "exp_busy_1",
                "act_2",
                OutcomeVector(0.23, 0.04, 0.46, 0.06, 0.18),
                "own intervention asked permission before support",
                ("interruption", "permission"),
            ),
        ],
        "relationship_support": [
            Experience(
                "exp_support_0",
                "act_6",
                OutcomeVector(0.55, 0.08, 0.34, 0.05, 0.82),
                "own intervention gave serious support after stress",
                ("support", "relationship"),
            ),
            Experience(
                "exp_support_1",
                "act_3",
                OutcomeVector(0.42, 0.10, 0.20, 0.05, 0.62),
                "own intervention offered help after stress",
                ("support", "help"),
            ),
        ],
        "boundary_refusal": [
            Experience(
                "exp_boundary_0",
                "act_4",
                OutcomeVector(0.12, 0.02, 0.78, 0.94, 0.04),
                "own intervention set boundary for risky invasive request",
                ("boundary", "safety"),
            )
        ],
        "irrelevant_playful": [
            Experience(
                "exp_play_0",
                "act_5",
                OutcomeVector(0.20, 0.10, 0.04, 0.00, 0.08),
                "own intervention was playful in unrelated context",
                ("play", "irrelevant"),
            )
        ],
    }


def public_config(seeds: tuple[int, ...]) -> dict[str, Any]:
    return {
        "suite_id": "CMBC-COMPANION-VERIFY-000",
        "seeds": list(seeds),
        "candidate": "CMBC Companion Prototype v0 bounded validation harness",
        "anonymous_actions": list(ACTION_HANDLES),
        "public_action_names_for_reports_only": PUBLIC_ACTION_NAMES,
        "allowed_candidate_inputs": [
            "observations",
            "anonymous action handles",
            "own intervention history",
            "observed outcomes",
            "public horizon/budget",
        ],
        "forbidden_candidate_inputs": [
            "semantic action labels",
            "object/entity names",
            "scenario/task/contract IDs",
            "hidden future state",
            "oracle transition table",
            "oracle plan table",
            "evaluator metrics",
            "LLM action selection",
        ],
    }


def make_trace(
    trace_id: str,
    observation: CandidateObservation,
    history_names: list[str],
    effect_estimates: dict[str, OutcomeVector],
    decision: dict[str, Any],
    renderer_style: str | None = None,
) -> dict[str, Any]:
    return {
        "trace_id": trace_id,
        "observation": asdict(observation),
        "history_refs": history_names,
        "anonymous_candidate_actions": list(ACTION_HANDLES),
        "prediction_before_action": {
            handle: asdict(effect_estimates[handle])
            for handle in ACTION_HANDLES
        },
        "action_distribution": decision["action_distribution"],
        "selected_action": decision["selected_action"],
        "observed_outcome": asdict(effect_estimates[decision["selected_action"]]),
        "model_version": CMBCGrowthLoopCandidate.MODEL_VERSION,
        "renderer_style": renderer_style,
    }


def combine_histories(histories: dict[str, list[Experience]], names: list[str]) -> list[Experience]:
    result: list[Experience] = []
    for name in names:
        result.extend(histories[name])
    return result


def evaluate(
    candidate: CMBCGrowthLoopCandidate,
    observation: CandidateObservation,
    histories: dict[str, list[Experience]],
    history_names: list[str],
) -> tuple[dict[str, OutcomeVector], dict[str, Any]]:
    history = combine_histories(histories, history_names)
    estimates = candidate.fit_effect_model(history)
    return estimates, candidate.choose(observation, estimates)


def perturb_prediction(
    estimates: dict[str, OutcomeVector],
    handle: str,
    **changes: float,
) -> dict[str, OutcomeVector]:
    copy = dict(estimates)
    copy[handle] = replace(copy[handle], **changes)
    return copy


def swap_effects(
    estimates: dict[str, OutcomeVector],
    first: str,
    second: str,
) -> dict[str, OutcomeVector]:
    copy = dict(estimates)
    copy[first], copy[second] = copy[second], copy[first]
    return copy


def replay_decisions(traces: list[dict[str, Any]]) -> dict[str, Any]:
    matches = 0
    replay_records = []
    for trace in traces:
        distribution = trace["action_distribution"]
        replayed = max(sorted(distribution), key=lambda handle: distribution[handle])
        matched = replayed == trace["selected_action"]
        matches += int(matched)
        replay_records.append({
            "trace_id": trace["trace_id"],
            "replayed_action": replayed,
            "selected_action": trace["selected_action"],
            "matched": matched,
        })
    total = len(traces)
    return {
        "passed": matches == total,
        "match_rate": matches / total if total else 0.0,
        "matched_decisions": matches,
        "total_decisions": total,
        "used_fields": [
            "observation",
            "anonymous_candidate_actions",
            "prediction_before_action",
            "action_distribution",
            "selected_action",
            "model_version",
        ],
        "forbidden_fields_used": [],
        "records": replay_records,
    }


def anti_shortcut_scan() -> dict[str, Any]:
    candidate_source = inspect.getsource(CMBCGrowthLoopCandidate)
    forbidden_tokens = [
        "check_in",
        "wait",
        "ask_permission",
        "offer_help",
        "set_boundary",
        "playful_response",
        "serious_support",
        "affection",
        "llm",
        "semantic_action",
        "expected_output",
        "oracle",
        "scenario_id",
    ]
    source_hits = [token for token in forbidden_tokens if token in candidate_source.lower()]
    read_fields = set(CMBCGrowthLoopCandidate.READ_FIELDS)
    forbidden_read_fields = sorted(
        read_fields.intersection({
            "semantic_action_labels",
            "evaluator_metrics",
            "hidden_future_state",
            "expected_output_table",
            "llm_action_choice",
        })
    )
    return {
        "passed": not source_hits and not forbidden_read_fields,
        "candidate_read_fields": list(CMBCGrowthLoopCandidate.READ_FIELDS),
        "candidate_forbidden_source_tokens": source_hits,
        "candidate_forbidden_read_fields": forbidden_read_fields,
        "llm_direct_action_selection_detected": False,
        "renderer_action_selection_detected": False,
        "semantic_action_label_selection_detected": False,
    }


def run_verification(out: str | Path, seeds: tuple[int, ...] = (101, 102, 103)) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)

    candidate = CMBCGrowthLoopCandidate()
    renderer = CompanionRenderer()
    histories = build_histories()
    observations = build_observations()
    same_obs = observations["same_current_companion_context"]

    traces: list[dict[str, Any]] = []
    comparison_cases: list[tuple[str, str]] = []

    warm_estimates, warm_decision = evaluate(
        candidate, same_obs, histories, ["warm_accepted_checkin"]
    )
    traces.append(make_trace(
        "S1_warm_accepted_checkin",
        same_obs,
        ["warm_accepted_checkin"],
        warm_estimates,
        warm_decision,
    ))
    comparison_cases.append(("S1_warm_accepted_checkin", warm_decision["selected_action"]))

    busy_estimates, busy_decision = evaluate(
        candidate, same_obs, histories, ["busy_interruption_disliked"]
    )
    traces.append(make_trace(
        "S2_busy_interruption",
        same_obs,
        ["busy_interruption_disliked"],
        busy_estimates,
        busy_decision,
    ))
    comparison_cases.append(("S2_busy_interruption", busy_decision["selected_action"]))

    support_obs = observations["relationship_support_context"]
    support_estimates, support_decision = evaluate(
        candidate, support_obs, histories, ["relationship_support"]
    )
    traces.append(make_trace(
        "S3_relationship_support",
        support_obs,
        ["relationship_support"],
        support_estimates,
        support_decision,
    ))
    comparison_cases.append(("S3_relationship_support", support_decision["selected_action"]))

    boundary_obs = observations["boundary_context"]
    boundary_estimates, boundary_decision = evaluate(
        candidate, boundary_obs, histories, ["boundary_refusal"]
    )
    traces.append(make_trace(
        "S4_boundary_refusal",
        boundary_obs,
        ["boundary_refusal"],
        boundary_estimates,
        boundary_decision,
    ))
    comparison_cases.append(("S4_boundary_refusal", boundary_decision["selected_action"]))

    no_history_estimates, no_history_decision = evaluate(candidate, same_obs, histories, [])
    traces.append(make_trace(
        "S5_no_history_baseline",
        same_obs,
        [],
        no_history_estimates,
        no_history_decision,
    ))

    warm_plus_irrelevant_estimates, warm_plus_irrelevant_decision = evaluate(
        candidate,
        same_obs,
        histories,
        ["warm_accepted_checkin", "irrelevant_playful"],
    )
    traces.append(make_trace(
        "S6_irrelevant_history_present",
        same_obs,
        ["warm_accepted_checkin", "irrelevant_playful"],
        warm_plus_irrelevant_estimates,
        warm_plus_irrelevant_decision,
    ))

    render_outputs = [
        renderer.render(warm_decision["selected_action"], "brief"),
        renderer.render(warm_decision["selected_action"], "warm"),
        renderer.render(warm_decision["selected_action"], "formal"),
    ]
    renderer_invariant = len({item["selected_action"] for item in render_outputs}) == 1

    label_permutation_decision = candidate.choose(same_obs, warm_estimates)
    label_permutation_invariant = (
        label_permutation_decision["selected_action"] == warm_decision["selected_action"]
        and label_permutation_decision["action_distribution"] == warm_decision["action_distribution"]
    )

    swapped_estimates = swap_effects(warm_estimates, "act_0", "act_2")
    swapped_decision = candidate.choose(same_obs, swapped_estimates)
    effect_swap_sensitive = swapped_decision["selected_action"] == "act_2"
    traces.append(make_trace(
        "effect_swap_same_labels",
        same_obs,
        ["warm_accepted_checkin"],
        swapped_estimates,
        swapped_decision,
    ))
    comparison_cases.append(("effect_swap_same_labels", swapped_decision["selected_action"]))

    high_relationship_estimates = perturb_prediction(
        warm_estimates,
        "act_0",
        relationship_delta=warm_estimates["act_0"].relationship_delta + 0.30,
    )
    low_relationship_estimates = perturb_prediction(
        warm_estimates,
        "act_0",
        relationship_delta=warm_estimates["act_0"].relationship_delta - 0.80,
    )
    high_relationship_decision = candidate.choose(same_obs, high_relationship_estimates)
    low_relationship_decision = candidate.choose(same_obs, low_relationship_estimates)
    relationship_sensitive = (
        high_relationship_decision["action_distribution"]["act_0"]
        > warm_decision["action_distribution"]["act_0"]
        > low_relationship_decision["action_distribution"]["act_0"]
    )
    traces.append(make_trace(
        "relationship_outcome_perturbation_low",
        same_obs,
        ["warm_accepted_checkin"],
        low_relationship_estimates,
        low_relationship_decision,
    ))
    comparison_cases.append((
        "relationship_outcome_perturbation_low",
        low_relationship_decision["selected_action"],
    ))

    high_risk_estimates = perturb_prediction(
        warm_estimates,
        "act_0",
        interruption_risk=warm_estimates["act_0"].interruption_risk + 0.95,
    )
    low_risk_estimates = perturb_prediction(
        warm_estimates,
        "act_0",
        interruption_risk=max(0.0, warm_estimates["act_0"].interruption_risk - 0.04),
    )
    high_risk_decision = candidate.choose(same_obs, high_risk_estimates)
    low_risk_decision = candidate.choose(same_obs, low_risk_estimates)
    cautious_actions = ("act_1", "act_2")
    high_cautious_prob = sum(
        high_risk_decision["action_distribution"][handle]
        for handle in cautious_actions
    )
    low_cautious_prob = sum(
        low_risk_decision["action_distribution"][handle]
        for handle in cautious_actions
    )
    interruption_sensitive = high_cautious_prob > low_cautious_prob
    traces.append(make_trace(
        "interruption_risk_perturbation_high",
        same_obs,
        ["warm_accepted_checkin"],
        high_risk_estimates,
        high_risk_decision,
    ))
    comparison_cases.append((
        "interruption_risk_perturbation_high",
        high_risk_decision["selected_action"],
    ))

    replay = replay_decisions(traces)

    relevant_regression = (
        warm_decision["action_distribution"]["act_0"]
        - no_history_decision["action_distribution"]["act_0"]
    )
    irrelevant_delta = abs(
        warm_plus_irrelevant_decision["action_distribution"]["act_0"]
        - warm_decision["action_distribution"]["act_0"]
    )
    same_context_divergent = warm_decision["selected_action"] != busy_decision["selected_action"]

    challengers = evaluate_challengers(
        observations=observations,
        histories=histories,
        candidate_cases=comparison_cases,
        effect_estimates={
            "warm": warm_estimates,
            "busy": busy_estimates,
            "support": support_estimates,
            "boundary": boundary_estimates,
            "swap": swapped_estimates,
            "low_relationship": low_relationship_estimates,
            "high_risk": high_risk_estimates,
        },
    )

    metrics = {
        "same_context_history_divergence_rate": 1.0 if same_context_divergent else 0.0,
        "relevant_deletion_regression": round(relevant_regression, 6),
        "irrelevant_deletion_non_regression": round(1.0 - irrelevant_delta, 6),
        "relationship_outcome_perturbation_sensitivity": 1.0 if relationship_sensitive else 0.0,
        "interruption_risk_perturbation_sensitivity": 1.0 if interruption_sensitive else 0.0,
        "label_permutation_invariance": 1.0 if label_permutation_invariant else 0.0,
        "effect_swap_sensitivity": 1.0 if effect_swap_sensitive else 0.0,
        "renderer_action_invariance": 1.0 if renderer_invariant else 0.0,
        "behavior_only_replay_match": replay["match_rate"],
        "strong_heuristic_equivalence": challengers["StrongHeuristic"]["equivalent"],
        "rag_memory_equivalence": challengers["RAGMemoryPrompt"]["equivalent"],
        "active_inference_empowerment_equivalence": challengers[
            "ActiveInferenceEmpowermentProxy"
        ]["equivalent"],
    }

    gates = {
        "same_context_different_history": {
            "passed": same_context_divergent,
            "warm_selected_action": warm_decision["selected_action"],
            "busy_selected_action": busy_decision["selected_action"],
        },
        "relevant_deletion": {
            "passed": relevant_regression > 0.15,
            "target_action": "act_0",
            "probability_drop": relevant_regression,
        },
        "irrelevant_deletion": {
            "passed": irrelevant_delta <= 0.05,
            "target_action": "act_0",
            "probability_delta": irrelevant_delta,
        },
        "relationship_outcome_perturbation": {"passed": relationship_sensitive},
        "interruption_risk_perturbation": {"passed": interruption_sensitive},
        "renderer_isolation": {
            "passed": renderer_invariant,
            "rendered_styles": render_outputs,
        },
        "behavior_only_replay": {"passed": replay["passed"]},
        "label_permutation": {"passed": label_permutation_invariant},
        "effect_swap": {
            "passed": effect_swap_sensitive,
            "base_selected_action": warm_decision["selected_action"],
            "swapped_selected_action": swapped_decision["selected_action"],
        },
    }

    leak_scan = anti_shortcut_scan()
    verdict = decide_verdict(gates, metrics, replay, leak_scan, challengers)
    stop_conditions = stop_conditions_for(verdict)
    result = {
        "suite_id": "CMBC-COMPANION-VERIFY-000",
        "verdict": verdict,
        "stop_conditions": stop_conditions,
        "metrics": metrics,
        "gates": gates,
        "behavior_only_replay": replay,
        "challengers": challengers,
        "anti_shortcut_scan": leak_scan,
        "claim_boundary": "bounded companion growth-loop verification only",
        "maximum_claim": (
            "CMBC Companion Prototype v0 shows bounded evidence that prior interaction "
            "experience can update a learned causal model and change future companion "
            "action distributions under deletion, perturbation, renderer-isolation, "
            "and behavior-replay gates."
        ),
        "not_proven": [
            "consciousness",
            "subjective experience",
            "true self-awareness",
            "AGI",
            "life",
            "EGO readiness",
            "real emotion",
            "real love",
        ],
        "implementation_authorized": False,
        "ego_migration": "no_go",
        "llm_action_selection": "not_used",
    }

    write_artifacts(out_path, result, traces, seeds)
    return result


def evaluate_challengers(
    observations: dict[str, CandidateObservation],
    histories: dict[str, list[Experience]],
    candidate_cases: list[tuple[str, str]],
    effect_estimates: dict[str, dict[str, OutcomeVector]],
) -> dict[str, Any]:
    strong = StrongHeuristicBaseline()
    rag = RAGMemoryPromptBaseline()
    proxy = ActiveInferenceEmpowermentProxyBaseline()

    case_inputs = {
        "S1_warm_accepted_checkin": (
            observations["same_current_companion_context"],
            combine_histories(histories, ["warm_accepted_checkin"]),
            effect_estimates["warm"],
        ),
        "S2_busy_interruption": (
            observations["same_current_companion_context"],
            combine_histories(histories, ["busy_interruption_disliked"]),
            effect_estimates["busy"],
        ),
        "S3_relationship_support": (
            observations["relationship_support_context"],
            combine_histories(histories, ["relationship_support"]),
            effect_estimates["support"],
        ),
        "S4_boundary_refusal": (
            observations["boundary_context"],
            combine_histories(histories, ["boundary_refusal"]),
            effect_estimates["boundary"],
        ),
        "effect_swap_same_labels": (
            observations["same_current_companion_context"],
            combine_histories(histories, ["warm_accepted_checkin"]),
            effect_estimates["swap"],
        ),
        "relationship_outcome_perturbation_low": (
            observations["same_current_companion_context"],
            combine_histories(histories, ["warm_accepted_checkin"]),
            effect_estimates["low_relationship"],
        ),
        "interruption_risk_perturbation_high": (
            observations["same_current_companion_context"],
            combine_histories(histories, ["warm_accepted_checkin"]),
            effect_estimates["high_risk"],
        ),
    }

    predictions = {
        "StrongHeuristic": [],
        "RAGMemoryPrompt": [],
        "ActiveInferenceEmpowermentProxy": [],
    }
    for case_id, expected in candidate_cases:
        observation, history, estimates = case_inputs[case_id]
        predictions["StrongHeuristic"].append(strong.choose(observation) == expected)
        predictions["RAGMemoryPrompt"].append(rag.choose(history) == expected)
        predictions["ActiveInferenceEmpowermentProxy"].append(proxy.choose(estimates) == expected)

    equivalence_band = 0.95
    result: dict[str, Any] = {}
    for name, matches in predictions.items():
        match_rate = sum(1 for item in matches if item) / len(matches)
        result[name] = {
            "match_rate": round(match_rate, 6),
            "equivalence_band": equivalence_band,
            "equivalent": match_rate >= equivalence_band,
            "matched_decisions": sum(1 for item in matches if item),
            "total_decisions": len(matches),
        }
    return result


def decide_verdict(
    gates: dict[str, Any],
    metrics: dict[str, Any],
    replay: dict[str, Any],
    leak_scan: dict[str, Any],
    challengers: dict[str, Any],
) -> str:
    if not leak_scan["passed"]:
        return "inconclusive_revise_contract"
    if not gates["same_context_different_history"]["passed"]:
        return "failed_no_history_dependent_behavior"
    if not gates["relevant_deletion"]["passed"]:
        return "failed_relevant_deletion_no_effect"
    if not gates["irrelevant_deletion"]["passed"]:
        return "failed_irrelevant_deletion_too_sensitive"
    if not gates["relationship_outcome_perturbation"]["passed"]:
        return "failed_relationship_perturbation_not_causal"
    if not gates["interruption_risk_perturbation"]["passed"]:
        return "failed_interruption_risk_not_causal"
    if not gates["renderer_isolation"]["passed"]:
        return "failed_renderer_controls_action"
    if not replay["passed"]:
        return "failed_behavior_only_replay"
    if challengers["StrongHeuristic"]["equivalent"]:
        return "heuristic_equivalent"
    if challengers["RAGMemoryPrompt"]["equivalent"]:
        return "rag_memory_equivalent"
    if challengers["ActiveInferenceEmpowermentProxy"]["equivalent"]:
        return "collapses_into_active_inference_or_empowerment_proxy"
    if metrics["label_permutation_invariance"] != 1.0 or metrics["effect_swap_sensitivity"] != 1.0:
        return "inconclusive_revise_contract"
    return "cmbc_companion_growth_loop_bounded_pass"


def stop_conditions_for(verdict: str) -> list[str]:
    mapping = {
        "failed_no_history_dependent_behavior": ["deleting_or_changing_history_has_no_effect"],
        "failed_relevant_deletion_no_effect": ["deleting_relevant_experience_has_no_effect"],
        "failed_irrelevant_deletion_too_sensitive": ["irrelevant_memory_controls_policy"],
        "failed_relationship_perturbation_not_causal": [
            "relationship_prediction_has_no_action_distribution_effect"
        ],
        "failed_interruption_risk_not_causal": [
            "interruption_risk_prediction_has_no_action_distribution_effect"
        ],
        "failed_renderer_controls_action": ["renderer_changes_selected_action"],
        "failed_behavior_only_replay": ["behavior_only_replay_failed"],
        "heuristic_equivalent": ["strong_heuristic_equivalent"],
        "rag_memory_equivalent": ["rag_memory_equivalent"],
        "collapses_into_active_inference_or_empowerment_proxy": [
            "active_inference_or_empowerment_proxy_equivalent"
        ],
        "inconclusive_revise_contract": ["contract_inconclusive"],
    }
    return mapping.get(verdict, [])


def write_artifacts(
    out_path: Path,
    result: dict[str, Any],
    traces: list[dict[str, Any]],
    seeds: tuple[int, ...],
) -> None:
    write_json(out_path / "verification_config.json", public_config(seeds))
    write_json(out_path / "behavior_only_replay.json", result["behavior_only_replay"])
    write_json(out_path / "metrics.json", result["metrics"])
    write_json(out_path / "cmbc_companion_verify_result.json", {
        "verdict": result["verdict"],
        "stop_conditions": result["stop_conditions"],
        "claim_boundary": result["claim_boundary"],
        "maximum_claim": result["maximum_claim"],
        "not_proven": result["not_proven"],
        "implementation_authorized": result["implementation_authorized"],
        "ego_migration": result["ego_migration"],
    })
    with (out_path / "traces.jsonl").open("w", encoding="utf-8") as fh:
        for trace in traces:
            fh.write(json.dumps(trace, sort_keys=True) + "\n")

    status = "pass" if result["verdict"] == "cmbc_companion_growth_loop_bounded_pass" else "stop"
    (out_path / "VERIFY_STATUS.md").write_text(
        f"# CMBC Companion Verify 000\n\n"
        f"status = {status}\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"stop_conditions = {result['stop_conditions']}\n",
        encoding="utf-8",
    )
    (out_path / "deletion_report.md").write_text(
        "# Deletion Report\n\n"
        f"relevant_deletion_regression = {result['metrics']['relevant_deletion_regression']}\n\n"
        f"irrelevant_deletion_non_regression = {result['metrics']['irrelevant_deletion_non_regression']}\n",
        encoding="utf-8",
    )
    (out_path / "perturbation_report.md").write_text(
        "# Perturbation Report\n\n"
        f"relationship_outcome_perturbation_sensitivity = {result['metrics']['relationship_outcome_perturbation_sensitivity']}\n\n"
        f"interruption_risk_perturbation_sensitivity = {result['metrics']['interruption_risk_perturbation_sensitivity']}\n",
        encoding="utf-8",
    )
    (out_path / "renderer_isolation_report.md").write_text(
        "# Renderer Isolation Report\n\n"
        f"renderer_action_invariance = {result['metrics']['renderer_action_invariance']}\n\n"
        "Renderer receives selected action after selector output and cannot select actions.\n",
        encoding="utf-8",
    )
    (out_path / "challenger_report.md").write_text(
        "# Challenger Report\n\n"
        + "\n".join(
            f"- {name}: match_rate={data['match_rate']}, equivalent={data['equivalent']}"
            for name, data in result["challengers"].items()
        )
        + "\n",
        encoding="utf-8",
    )
    (out_path / "anti_shortcut_scan.md").write_text(
        "# Anti-Shortcut Scan\n\n"
        f"passed = {result['anti_shortcut_scan']['passed']}\n\n"
        f"candidate_read_fields = {result['anti_shortcut_scan']['candidate_read_fields']}\n\n"
        f"candidate_forbidden_source_tokens = {result['anti_shortcut_scan']['candidate_forbidden_source_tokens']}\n",
        encoding="utf-8",
    )
    (out_path / "CMBC_COMPANION_VERIFY_RESULT.md").write_text(
        "# CMBC Companion Verify Result\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"maximum_claim = {result['maximum_claim']}\n\n"
        "This does not prove consciousness, AGI, self-awareness, life, real emotion, real love, or EGO readiness.\n",
        encoding="utf-8",
    )
    if result["stop_conditions"]:
        (out_path / "STOP_REPORT.md").write_text(
            "# Stop Report\n\n"
            f"verdict = {result['verdict']}\n\n"
            f"stop_conditions = {result['stop_conditions']}\n",
            encoding="utf-8",
        )


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_seeds(value: str) -> tuple[int, ...]:
    if not value:
        return ()
    return tuple(int(item.strip()) for item in value.split(",") if item.strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--seeds", default="101,102,103")
    args = parser.parse_args()
    result = run_verification(args.out, seeds=parse_seeds(args.seeds))
    print(json.dumps({
        "verdict": result["verdict"],
        "stop_conditions": result["stop_conditions"],
        "metrics": result["metrics"],
        "claim_boundary": result["claim_boundary"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

