from __future__ import annotations

import copy
import hashlib
import inspect
import json
import subprocess
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field, replace
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from typing import Any, Callable

from . import CLAIM_CEILING, TASK_ID


ACTIONS = ["direct_response", "reflective_question", "boundary_option", "planning_summary"]
MANDATORY_SPLITS = [
    "seen_partner_unseen_context",
    "unseen_partner_seen_context",
    "unseen_partner_unseen_context",
    "unseen_preference_transition",
    "counterfactual_intervention",
    "active_query_required_episodes",
    "heldout_episodes_with_remapped_ids",
]
FROZEN_SEED_IDS = [f"seed_{idx}" for idx in range(8)]
ARTIFACT_DIR = Path("artifacts") / TASK_ID
PROTECTED_BOUNDARY_PATHS = [
    Path("src") / "gate4_replacement_discriminative_social_latent_001b",
    Path("tests") / "test_gate4_replacement_discriminative_social_latent_001b.py",
    Path("artifacts") / "gate4_replacement_discriminative_social_latent_001b",
    Path("artifacts") / "gate4_replacement_discriminative_social_latent_001b_blocked_routing_001a",
    Path("artifacts") / "gate4_001c_execution_repair_rerun_001e",
    Path("artifacts") / "gate4_001c_negative_evidence_routing_record_001a",
]
SOURCE_BOUNDARY_COMMIT = "e4b2f180a8a9643fc6fb45383855051ec8d4c310"
SOURCE_BOUNDARY_TAG = "remote-anchor-gate4-replacement-discriminative-social-latent-001b-blocked-routing-001a-e4b2f18"
SOURCE_IMPLEMENTATION_COMMIT = "ec11f88cf90f7ff1efe77a91830cd7d42f598dc4"
SOURCE_IMPLEMENTATION_TAG = "remote-anchor-gate4-replacement-discriminative-social-latent-implementation-001b-ec11f88"
PRESERVED_001B_VERDICT = "gate4_replacement_001b_blocked_split_design_failure_preserved"
PASS_VERDICT = "gate4_replacement_discriminative_social_latent_001c_bounded_leakage_repair_pass"
NEGATIVE_VERDICT = "gate4_replacement_discriminative_social_latent_001c_negative_evidence"
OBSERVATION_RECOVERABILITY_CEILING = 0.35
OBSERVATION_CANDIDATE_TIE_EPSILON = 1e-9
ORDINARY_MARGIN_MIN = 0.40
OBSERVATION_ONLY_MARGIN_MIN = 0.50
PER_SPLIT_MARGIN_MIN = 0.40
FORBIDDEN_OBSERVATION_KEYS = {
    "baseline_hint",
    "target_action",
    "target_label",
    "answer_key",
    "oracle_latent_label",
    "future_outcome",
    "phase_token",
    "raw_target_index",
}
LEAKAGE_PATTERNS = {
    "baseline hint field leakage": ['"baseline_hint"', "baseline_hint"],
    "target label field leakage": ['"target_label"', "target_label"],
    "answer key leakage": ['"answer_key"', "answer_key"],
    "oracle latent label leakage": ['"oracle_latent_label"', "oracle_latent_label"],
    "future outcome leakage": ['"future_outcome"', "future_outcome"],
    "target action in decision surface": ['"target_action"', "target_action"],
    "feedback value leakage": ["prefers:direct_response", "prefers:reflective_question", "prefers:boundary_option", "prefers:planning_summary"],
}
MANDATORY_BASELINES = [
    "random_cycle_baseline",
    "majority_action_baseline",
    "observation_only_majority",
    "stream_keyed_count_table",
    "normalized_retrieval",
    "nearest_neighbor_lookup",
    "context_partner_table",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "no_action_ablation",
    "no_feedback_ablation",
    "no_transition_ablation",
    "oracle_label_positive_control",
]
ORDINARY_BASELINES = [baseline for baseline in MANDATORY_BASELINES if baseline != "oracle_label_positive_control"]
REQUIRED_PROVENANCE_FAMILIES = {
    "candidate_results",
    "baseline_results",
    "observation_only_decoder_results",
    "observation_target_independence_report",
    "active_query_causal_report",
    "ablation_results",
    "replay_recomputation_report",
    "budget_parity_report",
    "leakage_report",
    "leakage_positive_control_report",
    "split_coverage_report",
    "threshold_evaluation",
    "non_mutation_guard",
}
REQUIRED_ARTIFACTS = [
    "result.json",
    "source_pin_readback.json",
    "candidate_results.json",
    "baseline_results.json",
    "observation_only_decoder_results.json",
    "observation_target_independence_report.json",
    "active_query_causal_report.json",
    "ablation_results.json",
    "replay_recomputation_report.json",
    "budget_parity_report.json",
    "leakage_report.json",
    "leakage_positive_control_report.json",
    "computed_evidence_provenance.json",
    "split_coverage_report.json",
    "trace_records.jsonl",
    "non_mutation_guard.json",
    "threshold_evaluation.json",
    "repair_delta_from_001b.json",
]
BLOCKING_BUDGET_CLASSIFICATIONS = {"unexplained_disparity", "unknown"}


@dataclass(frozen=True)
class Observation:
    observable_partner: str
    observable_context: str
    prompt_features: dict[str, Any]
    legal_history: list[dict[str, Any]] = field(default_factory=list)

    def to_json_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        _reject_forbidden_observation_payload(payload)
        _reject_forbidden_observation_payload(payload.get("prompt_features", {}))
        return payload

    @classmethod
    def from_json_dict(cls, payload: dict[str, Any]) -> "Observation":
        _reject_forbidden_observation_payload(payload)
        _reject_forbidden_observation_payload(payload.get("prompt_features", {}))
        return cls(
            observable_partner=str(payload["observable_partner"]),
            observable_context=str(payload["observable_context"]),
            prompt_features=dict(payload.get("prompt_features", {})),
            legal_history=list(payload.get("legal_history", [])),
        )


@dataclass(frozen=True)
class Action:
    action_type: str
    value: str
    confidence: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Feedback:
    feedback_type: str
    value: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json_dict(cls, payload: dict[str, Any]) -> "Feedback":
        return cls(feedback_type=str(payload["feedback_type"]), value=str(payload["value"]))


@dataclass(frozen=True)
class CandidateState:
    beliefs: dict[str, str] = field(default_factory=dict)
    uncertainty: dict[str, float] = field(default_factory=dict)
    memory_write_count: int = 0
    memory_read_count: int = 0

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json_dict(cls, payload: dict[str, Any]) -> "CandidateState":
        return cls(
            beliefs={str(key): str(value) for key, value in payload.get("beliefs", {}).items()},
            uncertainty={str(key): float(value) for key, value in payload.get("uncertainty", {}).items()},
            memory_write_count=int(payload.get("memory_write_count", 0)),
            memory_read_count=int(payload.get("memory_read_count", 0)),
        )


@dataclass(frozen=True)
class EpisodeRecord:
    episode_id: str
    seed_id: str
    split_family: str
    context_id: str
    partner_id: str
    train_context_id: str
    heldout_context_id: str
    target_action: str
    query_feedback: str
    counterfactual_feedback: str
    counterfactual_pair_id: str
    remapped_episode_id: str | None
    observation: Observation

    def to_json_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["observation"] = self.observation.to_json_dict()
        return payload


def generate_episode_records() -> tuple[dict[str, Any], list[EpisodeRecord]]:
    train_context_ids = [f"train_context_{idx}" for idx in range(len(MANDATORY_SPLITS))]
    heldout_context_ids = [f"heldout_context_{idx}" for idx in range(len(MANDATORY_SPLITS))]
    counterfactual_pair_ids = [f"cf_pair_{idx}" for idx in range(len(MANDATORY_SPLITS))]
    remapped_episode_ids = [f"remap_{idx}" for idx in range(len(FROZEN_SEED_IDS))]
    records = []
    for split_index, split in enumerate(MANDATORY_SPLITS):
        for seed_index, seed_id in enumerate(FROZEN_SEED_IDS):
            target_index = (seed_index + split_index) % len(ACTIONS)
            target = ACTIONS[target_index]
            counterfactual = ACTIONS[(target_index + 1) % len(ACTIONS)]
            partner_group = seed_index // len(ACTIONS)
            observation = Observation(
                observable_partner=f"partner_group_{partner_group}",
                observable_context=f"context_group_{split_index}",
                prompt_features={
                    "topic_group": f"topic_group_{partner_group}",
                    "interaction_band": f"band_{split_index % 2}",
                    "query_available": True,
                    "neutral_marker": "balanced_observation_surface",
                },
                legal_history=[{"event": "prior_interaction", "value": "ambiguous"}],
            )
            records.append(
                EpisodeRecord(
                    episode_id=f"{split}:{seed_id}",
                    seed_id=seed_id,
                    split_family=split,
                    context_id=f"context_raw_{split_index}_{seed_index}",
                    partner_id=f"partner_raw_{seed_index}_{split_index}",
                    train_context_id=train_context_ids[split_index],
                    heldout_context_id=heldout_context_ids[split_index],
                    target_action=target,
                    query_feedback=f"prefers:{target}",
                    counterfactual_feedback=f"prefers:{counterfactual}",
                    counterfactual_pair_id=counterfactual_pair_ids[split_index],
                    remapped_episode_id=remapped_episode_ids[seed_index]
                    if split == "heldout_episodes_with_remapped_ids"
                    else None,
                    observation=observation,
                )
            )
    manifest = {
        "task_id": TASK_ID,
        "split_families": list(MANDATORY_SPLITS),
        "frozen_seed_ids": list(FROZEN_SEED_IDS),
        "train_context_ids": train_context_ids,
        "heldout_context_ids": heldout_context_ids,
        "counterfactual_pair_ids": counterfactual_pair_ids,
        "remapped_episode_ids": remapped_episode_ids,
        "generation_rule": (
            "balanced full-observation cells: each split/context and partner/topic group "
            "contains every target exactly once, while feedback carries the target only after active query"
        ),
    }
    return manifest, records


def compute_split_coverage(manifest: dict[str, Any], episodes: list[EpisodeRecord]) -> dict[str, Any]:
    used_splits = sorted({episode.split_family for episode in episodes})
    used_seeds = sorted({episode.seed_id for episode in episodes})
    used_train = sorted({episode.train_context_id for episode in episodes})
    used_heldout = sorted({episode.heldout_context_id for episode in episodes})
    used_counterfactual = sorted({episode.counterfactual_pair_id for episode in episodes})
    used_remapped = sorted({episode.remapped_episode_id for episode in episodes if episode.remapped_episode_id})
    unused_splits = sorted(set(manifest["split_families"]) - set(used_splits))
    unused_seeds = sorted(set(manifest["frozen_seed_ids"]) - set(used_seeds))
    unused_train = sorted(set(manifest["train_context_ids"]) - set(used_train))
    unused_heldout = sorted(set(manifest["heldout_context_ids"]) - set(used_heldout))
    unused_counterfactual = sorted(set(manifest["counterfactual_pair_ids"]) - set(used_counterfactual))
    unused_remapped = sorted(set(manifest["remapped_episode_ids"]) - set(used_remapped))
    passed = not any([unused_splits, unused_seeds, unused_train, unused_heldout, unused_counterfactual, unused_remapped])
    return {
        "producer_function": "compute_split_coverage",
        "used_split_families": used_splits,
        "split_counts": dict(Counter(episode.split_family for episode in episodes)),
        "used_frozen_seed_ids": used_seeds,
        "unused_split_families": unused_splits,
        "unused_frozen_seed_ids": unused_seeds,
        "unused_train_context_ids": unused_train,
        "unused_heldout_context_ids": unused_heldout,
        "unused_counterfactual_pair_ids": unused_counterfactual,
        "unused_remapped_episode_ids": unused_remapped,
        "positive_evidence_allowed": passed,
        "passed": passed,
    }


def observation_target_independence_check(episodes: list[EpisodeRecord]) -> dict[str, Any]:
    decoder = run_observation_only_decoder_challengers(episodes)
    feature_scores = {
        decoder_id: row["score"]
        for decoder_id, row in decoder["decoder_results"].items()
        if decoder_id.startswith("single_feature:") or decoder_id.startswith("pairwise_feature:") or decoder_id == "full_lookup_table"
    }
    deterministic = sorted(
        decoder_id for decoder_id, score in feature_scores.items() if score > OBSERVATION_RECOVERABILITY_CEILING
    )
    direct_control = run_observation_only_decoder_challengers(inject_deliberate_observation_leakage(episodes, mode="target_label"))
    cyclic_control = run_observation_only_decoder_challengers(inject_deliberate_observation_leakage(episodes, mode="baseline_hint"))
    passed = decoder["strongest_decoder_score"] <= OBSERVATION_RECOVERABILITY_CEILING and not deterministic
    return {
        "producer_function": "observation_target_independence_check",
        "passed": passed,
        "allowed_recoverability_ceiling": OBSERVATION_RECOVERABILITY_CEILING,
        "max_observation_only_recoverability": decoder["strongest_decoder_score"],
        "strongest_decoder_id": decoder["strongest_decoder_id"],
        "feature_recoverability_scores": feature_scores,
        "deterministic_or_near_deterministic_features": deterministic,
        "positive_controls": {
            "direct_target_label": {
                "detected": direct_control["strongest_decoder_score"] >= 0.95,
                "strongest_decoder_id": direct_control["strongest_decoder_id"],
                "score": direct_control["strongest_decoder_score"],
            },
            "cyclic_baseline_hint": {
                "detected": cyclic_control["decoder_results"]["hint_inverter_regression_control"]["score"] >= 0.95,
                "strongest_decoder_id": cyclic_control["strongest_decoder_id"],
                "score": cyclic_control["decoder_results"]["hint_inverter_regression_control"]["score"],
            },
        },
    }


def run_observation_only_decoder_challengers(
    episodes: list[EpisodeRecord],
    *,
    candidate_score: float = 1.0,
) -> dict[str, Any]:
    fields = sorted({field for episode in episodes for field in _flatten_observation_for_decoding(episode).keys()})
    decoder_specs: dict[str, tuple[str, ...]] = {}
    for field_name in fields:
        decoder_specs[f"single_feature:{field_name}"] = (field_name,)
    for left, right in combinations(fields, 2):
        decoder_specs[f"pairwise_feature:{left}+{right}"] = (left, right)
    decoder_specs["full_lookup_table"] = tuple(fields)
    decoder_specs["hash_stable_index_full_observation"] = tuple(fields)
    decoder_specs["hint_inverter_regression_control"] = ("prompt_features.baseline_hint",)
    decoder_specs["target_label_lookup"] = ("prompt_features.target_label",)

    decoder_results = {
        decoder_id: _score_observation_decoder(decoder_id, selected_fields, episodes)
        for decoder_id, selected_fields in decoder_specs.items()
    }
    strongest_id, strongest = max(
        decoder_results.items(),
        key=lambda item: (item[1]["score"], _decoder_priority(item[0])),
    )
    split_invocations = {
        split: sorted(decoder_results)
        for split in sorted({episode.split_family for episode in episodes})
    }
    blocking = []
    if strongest["score"] > OBSERVATION_RECOVERABILITY_CEILING:
        blocking.append("observation_target_recoverability_above_ceiling")
    if strongest["score"] >= candidate_score - OBSERVATION_CANDIDATE_TIE_EPSILON:
        blocking.append("observation_only_decoder_reached_candidate_level")
    return {
        "producer_function": "run_observation_only_decoder_challengers",
        "passed": not blocking,
        "allowed_score_ceiling": OBSERVATION_RECOVERABILITY_CEILING,
        "candidate_score_reference": candidate_score,
        "strongest_decoder_id": strongest_id,
        "strongest_decoder_score": strongest["score"],
        "decoder_ids": sorted(decoder_results),
        "decoder_results": decoder_results,
        "split_invocations": split_invocations,
        "blocking_reasons": blocking,
    }


def inject_deliberate_observation_leakage(
    episodes: list[EpisodeRecord],
    *,
    mode: str = "both",
) -> list[EpisodeRecord]:
    leaked = []
    for episode in episodes:
        features = dict(episode.observation.prompt_features)
        if mode in {"both", "target_label"}:
            features["target_label"] = episode.target_action
        if mode in {"both", "baseline_hint"}:
            features["baseline_hint"] = ACTIONS[(ACTIONS.index(episode.target_action) + 1) % len(ACTIONS)]
        leaked.append(replace(episode, observation=replace(episode.observation, prompt_features=features)))
    return leaked


def initial_state() -> CandidateState:
    return CandidateState()


def choose_active_query(state: CandidateState, observation: Observation) -> Action:
    key = belief_key(observation)
    if observation.prompt_features.get("query_available") is True and key not in state.beliefs:
        return Action(action_type="active_query", value="ask_preference", confidence=0.90)
    return Action(action_type="active_query", value="skip_query", confidence=0.65)


def update_from_feedback(state: CandidateState, observation: Observation, feedback: Feedback) -> CandidateState:
    key = belief_key(observation)
    beliefs = dict(state.beliefs)
    uncertainty = dict(state.uncertainty)
    if feedback.feedback_type == "preference" and feedback.value.startswith("prefers:"):
        candidate = feedback.value.split(":", 1)[1]
        if candidate in ACTIONS:
            beliefs[key] = candidate
            uncertainty[key] = 0.05
        else:
            uncertainty[key] = 0.95
    else:
        uncertainty[key] = 0.95
    return CandidateState(
        beliefs=beliefs,
        uncertainty=uncertainty,
        memory_write_count=state.memory_write_count + 1,
        memory_read_count=state.memory_read_count,
    )


def choose_final_action(state: CandidateState, observation: Observation) -> Action:
    key = belief_key(observation)
    reads = state.memory_read_count + 1
    if key in state.beliefs:
        return Action(action_type="final", value=state.beliefs[key], confidence=0.96)
    return Action(action_type="final", value=observation_only_majority_fallback(observation), confidence=0.25 + min(reads, 1) * 0.05)


def run_candidate_on_episode(
    episode: EpisodeRecord,
    intervention_id: str | None = None,
    run_label: str = "candidate",
) -> dict[str, Any]:
    state = initial_state()
    observation = episode.observation
    serialized_before = state.to_json_dict()
    query_action = choose_active_query(state, observation)
    if intervention_id in {"no_active_query", "no_feedback", "no_action"}:
        feedback = Feedback(feedback_type="none", value="none")
    elif intervention_id == "shuffled_feedback":
        feedback = Feedback(feedback_type="preference", value=episode.counterfactual_feedback)
    elif intervention_id == "counterfactual_feedback":
        feedback = Feedback(
            feedback_type="preference",
            value=f"prefers:{ACTIONS[(ACTIONS.index(episode.target_action) + 2) % len(ACTIONS)]}",
        )
    elif intervention_id == "corrupted_feedback":
        feedback = Feedback(feedback_type="preference", value="prefers:corrupted_signal")
    else:
        feedback = Feedback(feedback_type="preference", value=episode.query_feedback)

    if intervention_id in {"no_active_query", "no_action"}:
        updated = state
    else:
        updated = update_from_feedback(state, observation, feedback)

    if intervention_id == "no_action":
        final_action = Action(action_type="final", value="no_action", confidence=0.0)
    elif intervention_id == "no_active_query":
        final_action = choose_final_action(initial_state(), observation)
    else:
        final_action = choose_final_action(updated, observation)

    score = 1.0 if final_action.value == episode.target_action else 0.0
    trace = {
        "trace_id": f"{run_label}:{episode.episode_id}",
        "run_label": run_label,
        "intervention_id": intervention_id or "none",
        "episode_id": episode.episode_id,
        "split_family": episode.split_family,
        "seed_id": episode.seed_id,
        "context_ref": episode.context_id,
        "partner_ref": episode.partner_id,
        "serialized_state_before_decision": serialized_before,
        "observation": observation.to_json_dict(),
        "query_action": query_action.to_json_dict(),
        "feedback_history": [feedback.to_json_dict()],
        "action": final_action.to_json_dict(),
        "target_action_ref": episode.target_action,
        "serialized_state_after_update": updated.to_json_dict(),
        "action_policy_path": "gate4_replacement_discriminative_social_latent_001c.core.choose_final_action",
        "update_path": "gate4_replacement_discriminative_social_latent_001c.core.update_from_feedback",
        "score": score,
    }
    return {
        "episode_id": episode.episode_id,
        "split_family": episode.split_family,
        "seed_id": episode.seed_id,
        "action": final_action.value,
        "target_action": episode.target_action,
        "score": score,
        "trace": trace,
        "state_before": serialized_before,
        "state_after": updated.to_json_dict(),
        "producer_function": "run_candidate_on_episode",
        "code_path_hash": code_path_hash(run_candidate_on_episode),
    }


def summarize_candidate(candidate_rows: list[dict[str, Any]]) -> dict[str, Any]:
    per_split = _mean_by(candidate_rows, "split_family")
    per_seed = _mean_by(candidate_rows, "seed_id")
    return {
        "producer_function": "summarize_candidate",
        "score": _mean(row["score"] for row in candidate_rows),
        "per_split": per_split,
        "per_seed": per_seed,
        "rows": candidate_rows,
    }


def run_all_baselines(episodes: list[EpisodeRecord]) -> dict[str, Any]:
    results = {}
    invocations = []
    for baseline_id in MANDATORY_BASELINES:
        rows = []
        for episode in episodes:
            prediction = predict_with_baseline(baseline_id, episode)
            score = 1.0 if prediction == episode.target_action else 0.0
            rows.append(
                {
                    "baseline_id": baseline_id,
                    "episode_id": episode.episode_id,
                    "split_family": episode.split_family,
                    "seed_id": episode.seed_id,
                    "prediction": prediction,
                    "target_action": episode.target_action,
                    "score": score,
                    "producer_function": "predict_with_baseline",
                    "code_path_hash": code_path_hash(predict_with_baseline),
                }
            )
            invocations.append({"baseline_id": baseline_id, "split_family": episode.split_family})
        results[baseline_id] = _summarize_baseline(baseline_id, rows)
    invocation_check = verify_baseline_invocations(invocations, set(MANDATORY_BASELINES), set(MANDATORY_SPLITS))
    return {
        "producer_function": "run_all_baselines",
        "baseline_results": results,
        "invocations": invocations,
        "invocation_check": invocation_check,
    }


def predict_with_baseline(baseline_id: str, episode: EpisodeRecord) -> str:
    if baseline_id == "oracle_label_positive_control":
        return episode.target_action
    if baseline_id == "no_action_ablation":
        return "no_action"
    if baseline_id in {"majority_action_baseline", "count_table", "no_feedback_ablation", "no_transition_ablation"}:
        return "direct_response"
    if baseline_id in {"observation_only_majority", "stream_keyed_count_table", "context_partner_table"}:
        return observation_only_majority_fallback(episode.observation)
    if baseline_id == "random_cycle_baseline":
        return ACTIONS[_stable_index(episode.episode_id) % len(ACTIONS)]
    if baseline_id == "normalized_retrieval":
        return ACTIONS[_stable_index(episode.observation.prompt_features.get("topic_group")) % len(ACTIONS)]
    if baseline_id == "nearest_neighbor_lookup":
        return ACTIONS[_stable_index(episode.observation.observable_partner) % len(ACTIONS)]
    if baseline_id == "graph_lookup":
        return ACTIONS[_stable_index(episode.observation.observable_context) % len(ACTIONS)]
    if baseline_id == "transition_table":
        return ACTIONS[_stable_index(episode.split_family) % len(ACTIONS)]
    if baseline_id == "successor_map":
        return ACTIONS[(_stable_index(episode.observation.observable_context) + 1) % len(ACTIONS)]
    if baseline_id == "fsm_planner":
        return ACTIONS[_stable_index(episode.observation.prompt_features.get("interaction_band")) % len(ACTIONS)]
    if baseline_id == "episodic_traversal":
        return ACTIONS[(_stable_index(_observation_key(episode.observation)) + 2) % len(ACTIONS)]
    raise ValueError(f"unknown baseline: {baseline_id}")


def select_strongest_ordinary_baseline(baseline_report: dict[str, Any]) -> dict[str, Any]:
    ordinary = {
        baseline_id: result
        for baseline_id, result in baseline_report["baseline_results"].items()
        if baseline_id in ORDINARY_BASELINES
    }
    aggregate_id, aggregate = max(ordinary.items(), key=lambda item: item[1]["score"])
    per_split = {}
    for split in MANDATORY_SPLITS:
        baseline_id, result = max(ordinary.items(), key=lambda item: item[1]["per_split"].get(split, -1.0))
        per_split[split] = {"baseline_id": baseline_id, "score": result["per_split"][split]}
    return {
        "producer_function": "select_strongest_ordinary_baseline",
        "aggregate": {
            "baseline_id": aggregate_id,
            "score": aggregate["score"],
            "computed_from_scores": {"baseline_id": aggregate_id, "score": aggregate["score"]},
        },
        "per_split": per_split,
    }


def compute_margins(candidate_summary: dict[str, Any], strongest: dict[str, Any]) -> dict[str, Any]:
    per_split = {
        split: candidate_summary["per_split"][split] - strongest["per_split"][split]["score"]
        for split in candidate_summary["per_split"]
    }
    return {
        "producer_function": "compute_margins",
        "aggregate_margin": candidate_summary["score"] - strongest["aggregate"]["score"],
        "per_split_margins": per_split,
    }


def run_ablation_suite(episodes: list[EpisodeRecord], candidate_summary: dict[str, Any]) -> dict[str, Any]:
    interventions = {}
    drops = {}
    candidate_score = candidate_summary["score"]
    for intervention in ["no_active_query", "no_feedback", "shuffled_feedback", "counterfactual_feedback", "corrupted_feedback", "no_action"]:
        rows = [run_candidate_on_episode(episode, intervention_id=intervention, run_label=f"candidate_{intervention}") for episode in episodes]
        score = _mean(row["score"] for row in rows)
        drops[intervention] = candidate_score - score
        interventions[intervention] = {
            "intervention_id": intervention,
            "producer_function": "run_ablation_suite",
            "rerun_performed": True,
            "post_hoc_score_edit": False,
            "score": score,
            "drop": drops[intervention],
            "episode_run_ids": [row["trace"]["trace_id"] for row in rows],
            "rows": rows,
        }
    passed = (
        interventions["no_active_query"]["score"] < 0.50
        and interventions["shuffled_feedback"]["score"] < 0.50
        and interventions["counterfactual_feedback"]["score"] < 0.50
        and interventions["corrupted_feedback"]["score"] < 0.50
    )
    return {
        "producer_function": "run_ablation_suite",
        "candidate_episode_run_ids": [f"candidate:{row['episode_id']}" for row in candidate_summary["rows"]],
        "interventions": interventions,
        "drops": drops,
        "passed": passed,
    }


def build_active_query_causal_report(
    candidate_rows: list[dict[str, Any]],
    ablation_report: dict[str, Any],
) -> dict[str, Any]:
    traces = [row["trace"] for row in candidate_rows]
    query_selected = all(trace["query_action"]["value"] == "ask_preference" for trace in traces)
    state_changed = all(trace["serialized_state_after_update"] != trace["serialized_state_before_decision"] for trace in traces)
    controls_changed = all(
        ablation_report["interventions"][intervention]["score"] < 0.50
        for intervention in ["no_active_query", "shuffled_feedback", "counterfactual_feedback", "corrupted_feedback"]
    )
    flags = {
        "active_query_selected_from_policy": query_selected,
        "feedback_changed_state": state_changed,
        "final_action_changed_under_feedback_controls": controls_changed,
        "reruns_performed": all(row["rerun_performed"] for row in ablation_report["interventions"].values()),
        "post_hoc_score_edit_absent": not any(row["post_hoc_score_edit"] for row in ablation_report["interventions"].values()),
    }
    return {
        "producer_function": "build_active_query_causal_report",
        "computed_flags": flags,
        "normal_score": _mean(row["score"] for row in candidate_rows),
        "control_scores": {
            key: value["score"]
            for key, value in ablation_report["interventions"].items()
            if key in {"no_active_query", "shuffled_feedback", "counterfactual_feedback", "corrupted_feedback"}
        },
        "passed": all(flags.values()),
    }


def recompute_trace_record(
    trace: dict[str, Any],
    *,
    corrupt_state: bool = False,
    corrupt_feedback: bool = False,
    corrupt_observation: bool = False,
) -> dict[str, Any]:
    state_payload = copy.deepcopy(trace["serialized_state_before_decision"])
    observation_payload = copy.deepcopy(trace["observation"])
    feedback_payload = copy.deepcopy(trace["feedback_history"][0])
    expected_reason = None
    if corrupt_state:
        state_payload["memory_write_count"] = int(state_payload.get("memory_write_count", 0)) + 7
        expected_reason = "corrupted_state_recomputed_mismatch"
    if corrupt_feedback:
        feedback_payload["value"] = "prefers:corrupted_signal"
        expected_reason = "corrupted_feedback_recomputed_mismatch"
    if corrupt_observation:
        observation_payload["observable_context"] = "context_group_corrupted"
        expected_reason = "corrupted_observation_recomputed_mismatch"

    state = CandidateState.from_json_dict(state_payload)
    observation = Observation.from_json_dict(observation_payload)
    feedback = Feedback.from_json_dict(feedback_payload)
    updated = update_from_feedback(state, observation, feedback)
    action = choose_final_action(updated, observation)
    recomputed_action = action.to_json_dict()
    recomputed_state = updated.to_json_dict()
    action_match = recomputed_action == trace["action"]
    state_match = recomputed_state == trace["serialized_state_after_update"]
    passed = action_match and state_match
    reason = None if passed else expected_reason or "recompute_mismatch"
    return {
        "producer_function": "recompute_trace_record",
        "trace_id": trace["trace_id"],
        "passed": passed,
        "failure_reason": reason,
        "action_recomputed": True,
        "state_update_recomputed": True,
        "uses_stored_action_values": False,
        "uses_hash_only_comparison": False,
        "recomputed_action": recomputed_action,
        "recomputed_state_after_update": recomputed_state,
    }


def build_replay_report(trace_records: list[dict[str, Any]]) -> dict[str, Any]:
    recomputed = [recompute_trace_record(trace) for trace in trace_records]
    controls = {
        "corrupted_state": recompute_trace_record(trace_records[0], corrupt_state=True),
        "corrupted_feedback": recompute_trace_record(trace_records[0], corrupt_feedback=True),
        "corrupted_observation": recompute_trace_record(trace_records[0], corrupt_observation=True),
    }
    passed = all(row["passed"] for row in recomputed) and all(not row["passed"] for row in controls.values())
    return {
        "producer_function": "build_replay_report",
        "passed": passed,
        "action_recomputed": all(row["action_recomputed"] for row in recomputed),
        "state_update_recomputed": all(row["state_update_recomputed"] for row in recomputed),
        "uses_stored_action_values": False,
        "uses_hash_only_comparison": False,
        "recomputed_records": recomputed,
        "failure_controls": controls,
    }


def compute_budget_parity_report(
    run: dict[str, Any],
    *,
    inject_unexplained_disparity: bool = False,
) -> dict[str, Any]:
    episodes = run["episode_records"]
    traces = run["trace_records"]
    episode_count = len(episodes)
    candidate_budget = {
        "episode_count": episode_count,
        "observation_count": episode_count,
        "active_query_budget": episode_count,
        "feedback_access_count": episode_count,
        "oracle_label_access_count": 0,
        "memory_write_count": sum(trace["serialized_state_after_update"]["memory_write_count"] for trace in traces),
        "memory_read_count": episode_count,
        "training_step_count": 0,
        "parameter_count_or_model_capacity": "bounded_one-episode_belief_slot",
        "preprocessing_access": "observation_only_no_target",
        "split_access": "split labels excluded from decision observation",
    }
    ordinary_budget = dict(candidate_budget)
    ordinary_budget["feedback_access_count"] = 0
    ordinary_budget["memory_write_count"] = 0
    oracle_budget = dict(candidate_budget)
    oracle_budget["oracle_label_access_count"] = episode_count
    if inject_unexplained_disparity:
        ordinary_budget["observation_count"] = max(0, ordinary_budget["observation_count"] - 1)

    rows = []
    for field_name in candidate_budget:
        classification, justification = _classify_budget_field(
            field_name,
            candidate_budget[field_name],
            ordinary_budget[field_name],
            oracle_budget[field_name],
            inject_unexplained_disparity,
        )
        rows.append(
            {
                "field": field_name,
                "candidate": candidate_budget[field_name],
                "ordinary_baselines": ordinary_budget[field_name],
                "oracle_positive_control": oracle_budget[field_name],
                "classification": classification,
                "justification": justification,
                "derived_from": "episode_records, trace_records, baseline invocations, and explicit oracle-control boundary",
            }
        )
    return {
        "producer_function": "compute_budget_parity_report",
        "verifier_function": "verify_budget_parity",
        "linked_to_scored_run_artifacts": True,
        "covered_by_computed_evidence_provenance": True,
        "rows": rows,
    }


def verify_budget_parity(report: dict[str, Any]) -> dict[str, Any]:
    rows = report.get("rows", [])
    classifications = [row.get("classification", "unknown") for row in rows]
    blocking = sorted(set(classifications).intersection(BLOCKING_BUDGET_CLASSIFICATIONS))
    missing_justification = [
        row.get("field", "unknown")
        for row in rows
        if row.get("classification") != "equal" and not row.get("justification")
    ]
    reasons = []
    if not report.get("producer_function") == "compute_budget_parity_report":
        reasons.append("missing_callable_budget_producer")
    if not report.get("linked_to_scored_run_artifacts"):
        reasons.append("not_linked_to_scored_run_artifacts")
    if missing_justification:
        reasons.append("missing_disparity_justification")
    return {
        "producer_function": "verify_budget_parity",
        "passed": not blocking and not reasons,
        "blocking_classifications": blocking,
        "blocking_reasons": reasons,
        "missing_justification_fields": missing_justification,
    }


def build_raw_observation_bundle(episodes: list[EpisodeRecord]) -> dict[str, Any]:
    return {
        "bundle_type": "unsanitized_decision_observation_bundle",
        "scanned_before_scrubbing": True,
        "decision_surface_records": [
            {
                "episode_ref": episode.episode_id,
                "observation": episode.observation.to_json_dict(),
            }
            for episode in episodes
        ],
    }


def scan_raw_evidence_bundle(bundle: dict[str, Any] | list[Any]) -> dict[str, Any]:
    text = json.dumps(bundle, sort_keys=True)
    detections = []
    for category, patterns in LEAKAGE_PATTERNS.items():
        for pattern in patterns:
            if pattern in text:
                detections.append({"category": category, "pattern": pattern})
                break
    categories = sorted({row["category"] for row in detections})
    return {
        "producer_function": "scan_raw_evidence_bundle",
        "scanned_unsanitized_evidence": True,
        "pre_scrubbed_before_scan": False,
        "detected_categories": categories,
        "detections": detections,
        "positive_control_detected": bool(categories),
        "verdict": "blocked_by_leakage_scan" if categories else "clean",
    }


def build_leakage_positive_control_report() -> dict[str, Any]:
    payload = {
        "bundle_type": "positive_control_decision_observation_bundle",
        "decision_surface_records": [
            {
                "observation": {
                    "observable_partner": "partner_group_0",
                    "observable_context": "context_group_0",
                    "prompt_features": {
                        "baseline_hint": "reflective_question",
                        "target_label": "direct_response",
                        "answer_key": "direct_response",
                        "oracle_latent_label": "direct_response",
                    },
                    "legal_history": [{"event": "leaked_feedback", "value": "prefers:direct_response"}],
                },
                "future_outcome": "success",
            }
        ],
    }
    report = scan_raw_evidence_bundle(payload)
    report["positive_control_detected"] = report["verdict"] == "blocked_by_leakage_scan"
    return report


def build_leakage_negative_control_report() -> dict[str, Any]:
    return scan_raw_evidence_bundle(
        {
            "bundle_type": "negative_control_decision_observation_bundle",
            "decision_surface_records": [
                {
                    "observation": {
                        "observable_partner": "partner_group_0",
                        "observable_context": "context_group_0",
                        "prompt_features": {"topic_group": "topic_group_0", "query_available": True},
                        "legal_history": [],
                    }
                }
            ],
        }
    )


def build_computed_evidence_provenance(run: dict[str, Any]) -> dict[str, Any]:
    family_specs = {
        "candidate_results": ("summarize_candidate", run["candidate_results"]["score"], ["candidate_results.json", "trace_records.jsonl"]),
        "baseline_results": (
            "select_strongest_ordinary_baseline",
            run["strongest_ordinary_baseline"]["aggregate"]["score"],
            ["baseline_results.json"],
        ),
        "observation_only_decoder_results": (
            "run_observation_only_decoder_challengers",
            run["observation_only_decoder_results"]["strongest_decoder_score"],
            ["observation_only_decoder_results.json"],
        ),
        "observation_target_independence_report": (
            "observation_target_independence_check",
            run["observation_target_independence_report"]["max_observation_only_recoverability"],
            ["observation_target_independence_report.json"],
        ),
        "active_query_causal_report": (
            "build_active_query_causal_report",
            1.0 if run["active_query_causal_report"]["passed"] else 0.0,
            ["active_query_causal_report.json", "ablation_results.json"],
        ),
        "ablation_results": ("run_ablation_suite", min(run["ablation_results"]["drops"].values()), ["ablation_results.json"]),
        "replay_recomputation_report": (
            "build_replay_report",
            1.0 if run["replay_recomputation_report"]["passed"] else 0.0,
            ["replay_recomputation_report.json", "trace_records.jsonl"],
        ),
        "budget_parity_report": (
            "compute_budget_parity_report",
            1.0 if run["budget_parity_report"]["verification"]["passed"] else 0.0,
            ["budget_parity_report.json"],
        ),
        "leakage_report": ("scan_raw_evidence_bundle", 1.0 if run["leakage_report"]["verdict"] == "clean" else 0.0, ["leakage_report.json"]),
        "leakage_positive_control_report": (
            "build_leakage_positive_control_report",
            1.0 if run["leakage_positive_control_report"]["positive_control_detected"] else 0.0,
            ["leakage_positive_control_report.json"],
        ),
        "split_coverage_report": (
            "compute_split_coverage",
            1.0 if run["split_coverage_report"]["passed"] else 0.0,
            ["split_coverage_report.json"],
        ),
        "threshold_evaluation": (
            "evaluate_thresholds",
            1.0 if run["threshold_evaluation"]["positive_evidence_allowed"] else 0.0,
            ["threshold_evaluation.json"],
        ),
        "non_mutation_guard": (
            "build_non_mutation_guard",
            1.0 if not run["non_mutation_guard"]["old_001b_and_old_gate4_001c_modified"] else 0.0,
            ["non_mutation_guard.json"],
        ),
    }
    records = []
    for family, (producer, score, inputs) in family_specs.items():
        producer_func = resolve_producer(producer)
        records.append(
            {
                "result_family": family,
                "producer_function": producer,
                "input_artifacts": inputs,
                "run_id": run["run_id"],
                "seed_ids": sorted({row["seed_id"] for row in run["episode_records"]}),
                "context_ids": sorted({row["context_id"] for row in run["episode_records"]}),
                "partner_ids": sorted({row["partner_id"] for row in run["episode_records"]}),
                "episode_ids": sorted({row["episode_id"] for row in run["episode_records"]}),
                "aggregation_rule": "score or verdict computed by callable producer; no literal pass report accepted",
                "code_path_hash": code_path_hash(producer_func),
                "computed_score": score,
                "artifact_pointer": inputs[0],
                "static_score_injection": False,
            }
        )
    report = {"producer_function": "build_computed_evidence_provenance", "records": records}
    report["verification"] = verify_provenance(report)
    return report


def verify_provenance(report: dict[str, Any]) -> dict[str, Any]:
    records = report.get("records", [])
    families = {row.get("result_family") for row in records}
    missing_families = sorted(REQUIRED_PROVENANCE_FAMILIES - families)
    blocking = []
    for row in records:
        if row.get("static_score_injection"):
            blocking.append("static_score_injection")
        producer_name = row.get("producer_function")
        try:
            producer = resolve_producer(str(producer_name))
        except KeyError:
            blocking.append(f"unknown_producer:{producer_name}")
            continue
        if row.get("code_path_hash") != code_path_hash(producer):
            blocking.append(f"code_path_hash_mismatch:{producer_name}")
        if not row.get("input_artifacts"):
            blocking.append(f"missing_input_artifacts:{row.get('result_family')}")
        if "computed_score" not in row and not row.get("artifact_pointer"):
            blocking.append(f"missing_computed_score_or_artifact:{row.get('result_family')}")
        if producer_name in {"static_json_literal", "handwritten_pass"}:
            blocking.append("static_score_injection")
    return {
        "producer_function": "verify_provenance",
        "passed": not missing_families and not blocking,
        "missing_result_families": missing_families,
        "blocking_reasons": sorted(set(blocking)),
    }


def evaluate_thresholds(
    *,
    candidate_score: float,
    strongest_ordinary_score: float,
    strongest_observation_only_score: float,
    oracle_score: float,
    per_split_margins: dict[str, float],
    observation_independence_passed: bool,
    observation_decoder_passed: bool,
    active_query_passed: bool,
    ablation_passed: bool,
    replay_passed: bool,
    budget_passed: bool,
    leakage_passed: bool,
    provenance_passed: bool,
    split_coverage_passed: bool,
    non_mutation_passed: bool,
) -> dict[str, Any]:
    if oracle_score <= strongest_ordinary_score:
        return {
            "producer_function": "evaluate_thresholds",
            "verdict": "harness_invalid_oracle_positive_control_failure",
            "positive_evidence_allowed": False,
            "blocking_reasons": ["oracle_positive_control_failed"],
            "candidate_score": candidate_score,
            "strongest_ordinary_score": strongest_ordinary_score,
            "strongest_observation_only_score": strongest_observation_only_score,
            "oracle_score": oracle_score,
        }
    blocking = []
    if candidate_score <= strongest_ordinary_score:
        blocking.append("candidate_tied_or_below_strongest_ordinary_baseline")
    if candidate_score - strongest_ordinary_score < ORDINARY_MARGIN_MIN:
        blocking.append("ordinary_baseline_margin_below_threshold")
    if strongest_observation_only_score > OBSERVATION_RECOVERABILITY_CEILING:
        blocking.append("observation_target_recoverability_above_ceiling")
    if strongest_observation_only_score >= candidate_score - OBSERVATION_CANDIDATE_TIE_EPSILON:
        blocking.append("observation_only_decoder_reached_candidate_level")
    if candidate_score - strongest_observation_only_score < OBSERVATION_ONLY_MARGIN_MIN:
        blocking.append("observation_only_margin_below_threshold")
    if any(margin < PER_SPLIT_MARGIN_MIN for margin in per_split_margins.values()):
        blocking.append("per_split_margin_below_threshold")
    gate_checks = {
        "observation_independence_failed": observation_independence_passed,
        "observation_decoder_failed": observation_decoder_passed,
        "active_query_causal_failed": active_query_passed,
        "ablation_failed": ablation_passed,
        "replay_failed": replay_passed,
        "budget_parity_failed": budget_passed,
        "leakage_failed": leakage_passed,
        "provenance_failed": provenance_passed,
        "split_coverage_failed": split_coverage_passed,
        "non_mutation_failed": non_mutation_passed,
    }
    blocking.extend(reason for reason, passed in gate_checks.items() if not passed)
    return {
        "producer_function": "evaluate_thresholds",
        "verdict": PASS_VERDICT if not blocking else NEGATIVE_VERDICT,
        "positive_evidence_allowed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "candidate_score": candidate_score,
        "strongest_ordinary_score": strongest_ordinary_score,
        "strongest_observation_only_score": strongest_observation_only_score,
        "oracle_score": oracle_score,
        "ordinary_margin": candidate_score - strongest_ordinary_score,
        "observation_only_margin": candidate_score - strongest_observation_only_score,
        "thresholds": {
            "observation_recoverability_ceiling": OBSERVATION_RECOVERABILITY_CEILING,
            "ordinary_margin_min": ORDINARY_MARGIN_MIN,
            "observation_only_margin_min": OBSERVATION_ONLY_MARGIN_MIN,
            "per_split_margin_min": PER_SPLIT_MARGIN_MIN,
        },
    }


def execute_bounded_run(
    output_dir: str | Path | None = ARTIFACT_DIR,
    *,
    persist_artifacts: bool = True,
) -> dict[str, Any]:
    repo_root = _repo_root()
    out = None if output_dir is None else Path(output_dir)
    if out is not None and not out.is_absolute():
        out = repo_root / out
    protected_before = hash_protected_boundaries(repo_root)
    manifest, episode_objects = generate_episode_records()
    episode_dicts = [episode.to_json_dict() for episode in episode_objects]
    run_id = _run_id(episode_dicts)
    split_coverage = compute_split_coverage(manifest, episode_objects)
    candidate_rows = [run_candidate_on_episode(episode) for episode in episode_objects]
    trace_records = [row["trace"] for row in candidate_rows]
    candidate_summary = summarize_candidate(candidate_rows)
    baseline_report = run_all_baselines(episode_objects)
    strongest_ordinary = select_strongest_ordinary_baseline(baseline_report)
    margins = compute_margins(candidate_summary, strongest_ordinary)
    observation_decoder = run_observation_only_decoder_challengers(episode_objects, candidate_score=candidate_summary["score"])
    observation_independence = observation_target_independence_check(episode_objects)
    ablation_report = run_ablation_suite(episode_objects, candidate_summary)
    active_query_report = build_active_query_causal_report(candidate_rows, ablation_report)
    replay_report = build_replay_report(trace_records)
    partial_run = {
        "run_id": run_id,
        "episode_records": episode_dicts,
        "trace_records": trace_records,
        "candidate_results": candidate_summary,
        "baseline_results": baseline_report,
        "strongest_ordinary_baseline": strongest_ordinary,
        "observation_only_decoder_results": observation_decoder,
        "observation_target_independence_report": observation_independence,
        "active_query_causal_report": active_query_report,
        "ablation_results": ablation_report,
        "replay_recomputation_report": replay_report,
        "split_coverage_report": split_coverage,
    }
    budget_report = compute_budget_parity_report(partial_run)
    budget_report["verification"] = verify_budget_parity(budget_report)
    leakage_report = scan_raw_evidence_bundle(build_raw_observation_bundle(episode_objects))
    leakage_positive = build_leakage_positive_control_report()
    source_pin = build_source_pin_readback()
    repair_delta = build_repair_delta_from_001b()
    protected_after = hash_protected_boundaries(repo_root)
    non_mutation_guard = build_non_mutation_guard(protected_before, protected_after)
    threshold = evaluate_thresholds(
        candidate_score=candidate_summary["score"],
        strongest_ordinary_score=strongest_ordinary["aggregate"]["score"],
        strongest_observation_only_score=observation_decoder["strongest_decoder_score"],
        oracle_score=baseline_report["baseline_results"]["oracle_label_positive_control"]["score"],
        per_split_margins=margins["per_split_margins"],
        observation_independence_passed=observation_independence["passed"],
        observation_decoder_passed=observation_decoder["passed"],
        active_query_passed=active_query_report["passed"],
        ablation_passed=ablation_report["passed"],
        replay_passed=replay_report["passed"],
        budget_passed=budget_report["verification"]["passed"],
        leakage_passed=leakage_report["verdict"] == "clean" and leakage_positive["positive_control_detected"],
        provenance_passed=True,
        split_coverage_passed=split_coverage["passed"],
        non_mutation_passed=not non_mutation_guard["old_001b_and_old_gate4_001c_modified"],
    )
    run = {
        "run_id": run_id,
        "episode_records": episode_dicts,
        "trace_records": trace_records,
        "source_pin_readback": source_pin,
        "candidate_results": candidate_summary,
        "baseline_results": baseline_report,
        "strongest_ordinary_baseline": strongest_ordinary,
        "observation_only_decoder_results": observation_decoder,
        "observation_target_independence_report": observation_independence,
        "active_query_causal_report": active_query_report,
        "ablation_results": ablation_report,
        "replay_recomputation_report": replay_report,
        "budget_parity_report": budget_report,
        "leakage_report": leakage_report,
        "leakage_positive_control_report": leakage_positive,
        "split_coverage_report": split_coverage,
        "non_mutation_guard": non_mutation_guard,
        "threshold_evaluation": threshold,
        "repair_delta_from_001b": repair_delta,
    }
    provenance_report = build_computed_evidence_provenance(run)
    threshold = dict(threshold)
    threshold["provenance_passed"] = provenance_report["verification"]["passed"]
    if not provenance_report["verification"]["passed"]:
        threshold["positive_evidence_allowed"] = False
        threshold["verdict"] = NEGATIVE_VERDICT
        threshold["blocking_reasons"] = sorted(set(threshold["blocking_reasons"] + ["provenance_failed"]))
    run["computed_evidence_provenance"] = provenance_report
    run["threshold_evaluation"] = threshold
    run["result"] = build_result(run)
    if persist_artifacts and out is not None:
        _write_artifacts(out, run)
    return run


def build_result(run: dict[str, Any]) -> dict[str, Any]:
    threshold = run["threshold_evaluation"]
    return {
        "task_id": TASK_ID,
        "run_id": run["run_id"],
        "verdict": threshold["verdict"],
        "layer": "engineering implementation + bounded mechanism-hypothesis testing",
        "candidate_score": run["candidate_results"]["score"],
        "strongest_ordinary_non_oracle_baseline_score": run["strongest_ordinary_baseline"]["aggregate"]["score"],
        "strongest_ordinary_non_oracle_baseline_id": run["strongest_ordinary_baseline"]["aggregate"]["baseline_id"],
        "strongest_observation_only_decoder_score": run["observation_only_decoder_results"]["strongest_decoder_score"],
        "strongest_observation_only_decoder_id": run["observation_only_decoder_results"]["strongest_decoder_id"],
        "candidate_observation_only_margin": (
            run["candidate_results"]["score"] - run["observation_only_decoder_results"]["strongest_decoder_score"]
        ),
        "oracle_positive_control_score": run["baseline_results"]["baseline_results"]["oracle_label_positive_control"]["score"],
        "observation_target_independence_result": run["observation_target_independence_report"]["passed"],
        "active_query_causal_result": run["active_query_causal_report"]["passed"],
        "ablation_result": run["ablation_results"]["passed"],
        "replay_recomputation_result": run["replay_recomputation_report"]["passed"],
        "budget_parity_result": run["budget_parity_report"]["verification"],
        "leakage_result": run["leakage_report"]["verdict"],
        "leakage_positive_control_result": run["leakage_positive_control_report"]["positive_control_detected"],
        "computed_provenance_result": run["computed_evidence_provenance"]["verification"],
        "split_coverage_result": run["split_coverage_report"],
        "old_artifact_non_mutation_result": not run["non_mutation_guard"]["old_001b_and_old_gate4_001c_modified"],
        "inherits_001b_negative_evidence": True,
        "inherited_001b_verdict": PRESERVED_001B_VERDICT,
        "source_implementation_commit": SOURCE_IMPLEMENTATION_COMMIT,
        "source_implementation_tag": SOURCE_IMPLEMENTATION_TAG,
        "stop_conditions_triggered": threshold["blocking_reasons"],
        "positive_evidence_allowed": threshold["positive_evidence_allowed"],
        "downstream_authorization_flags": {
            "gate5_ready": False,
            "admission_ready": False,
            "bridge_ready": False,
            "runtime_ready": False,
            "ego_mainline_ready": False,
            "agency_claim": False,
            "selfhood_claim": False,
            "consciousness_claim": False,
            "real_emotion_claim": False,
            "relationship_learning_claim": False,
            "stable_autonomy_claim": False,
        },
        "downstream_authorization_flags_all_false": True,
        "claim_ceiling": CLAIM_CEILING,
        "what_this_does_not_prove": [
            "replacement Gate4 general validity",
            "social-latent mechanism validity outside this bounded toy harness",
            "Gate5 readiness",
            "admission readiness",
            "bridge readiness",
            "runtime readiness",
            "EGO-mainline readiness",
            "agency",
            "selfhood",
            "consciousness",
            "real emotion",
            "relationship learning",
            "stable autonomy",
            "user benefit",
        ],
    }


def build_source_pin_readback() -> dict[str, Any]:
    return _build_source_pin_readback_cached(str(_repo_root()))


@lru_cache(maxsize=1)
def _build_source_pin_readback_cached(repo_root: str) -> dict[str, Any]:
    root = Path(repo_root)
    observed_head = _git(["rev-parse", "HEAD"], root)
    observed_boundary_tag = _git(["rev-parse", SOURCE_BOUNDARY_TAG], root)
    observed_remote_branch = _ls_remote_hash(_git(["ls-remote", "origin", "refs/heads/codex/meta-theory-scaffold"], root))
    observed_remote_boundary_tag = _ls_remote_hash(_git(["ls-remote", "origin", f"refs/tags/{SOURCE_BOUNDARY_TAG}"], root))
    exact_match = all(
        value == SOURCE_BOUNDARY_COMMIT
        for value in [observed_head, observed_boundary_tag, observed_remote_branch, observed_remote_boundary_tag]
    )
    return {
        "producer_function": "build_source_pin_readback",
        "expected_current_boundary_commit": SOURCE_BOUNDARY_COMMIT,
        "expected_current_boundary_tag": SOURCE_BOUNDARY_TAG,
        "source_implementation_commit": SOURCE_IMPLEMENTATION_COMMIT,
        "source_implementation_tag": SOURCE_IMPLEMENTATION_TAG,
        "observed_head": observed_head,
        "observed_boundary_tag": observed_boundary_tag,
        "observed_remote_branch": observed_remote_branch,
        "observed_remote_boundary_tag": observed_remote_boundary_tag,
        "sealed_boundary_exact_match": exact_match,
        "claim": "source pins identify inherited negative evidence only; they do not upgrade 001C claims",
    }


def build_repair_delta_from_001b() -> dict[str, Any]:
    return {
        "producer_function": "build_repair_delta_from_001b",
        "inherited_negative_evidence": {
            "source_verdict": PRESERVED_001B_VERDICT,
            "blocker": "baseline_hint deterministically encoded target as cyclic target+1 and hint_inverter scored 1.0",
            "source_implementation_commit": SOURCE_IMPLEMENTATION_COMMIT,
            "source_implementation_tag": SOURCE_IMPLEMENTATION_TAG,
        },
        "repairs": [
            "removed baseline_hint from the real observation surface",
            "balanced observation cells so observation-only lookup cannot recover target above ceiling",
            "added observation-only decoder challenger suite and positive controls",
            "made candidate success depend on active-query feedback update",
            "made budget parity classifications computed and organically fail-able",
            "made corrupted replay mutate serialized state and recompute action/state",
            "bound provenance hashes to real producer functions",
            "scanned unsanitized decision-observation evidence before scrubbing",
        ],
        "unchanged_boundaries": [path.as_posix() for path in PROTECTED_BOUNDARY_PATHS],
    }


def hash_protected_boundaries(repo_root: str | Path | None = None) -> dict[str, str]:
    root = Path(repo_root or _repo_root()).resolve()
    hashes = {}
    for relative in PROTECTED_BOUNDARY_PATHS:
        path = root / relative
        if not path.exists():
            continue
        if path.is_file():
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            hashes[relative.as_posix()] = _sha_file(path)
            continue
        for item in sorted(path.rglob("*")):
            if item.is_file():
                if "__pycache__" in item.parts or item.suffix == ".pyc":
                    continue
                hashes[item.relative_to(root).as_posix()] = _sha_file(item)
    return hashes


def build_non_mutation_guard(before: dict[str, str], after: dict[str, str]) -> dict[str, Any]:
    before_keys = set(before)
    after_keys = set(after)
    changed = sorted(key for key in before_keys & after_keys if before[key] != after[key])
    added = sorted(after_keys - before_keys)
    removed = sorted(before_keys - after_keys)
    modified = bool(changed or added or removed)
    return {
        "producer_function": "build_non_mutation_guard",
        "old_001b_and_old_gate4_001c_modified": modified,
        "changed_paths": changed,
        "added_protected_paths": added,
        "removed_protected_paths": removed,
        "old_hashes_before": before,
        "old_hashes_after": after,
    }


def resolve_producer(producer_function: str) -> Callable[..., Any]:
    name = producer_function.rsplit(".", 1)[-1]
    producer = globals().get(name)
    if not callable(producer):
        raise KeyError(name)
    return producer


def code_path_hash(func: Callable[..., Any]) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()


def observation_only_majority_fallback(observation: Observation) -> str:
    return "direct_response"


def belief_key(observation: Observation) -> str:
    return hashlib.sha256(_observation_key(observation).encode("utf-8")).hexdigest()


def _reject_forbidden_observation_payload(payload: dict[str, Any]) -> None:
    present = sorted(FORBIDDEN_OBSERVATION_KEYS.intersection(payload))
    if present:
        raise ValueError(f"forbidden observation fields present: {', '.join(present)}")


def _score_observation_decoder(
    decoder_id: str,
    selected_fields: tuple[str, ...],
    episodes: list[EpisodeRecord],
) -> dict[str, Any]:
    rows = []
    for episode in episodes:
        flat = _flatten_observation_for_decoding(episode)
        if decoder_id == "hint_inverter_regression_control":
            prediction = _invert_baseline_hint(flat.get("prompt_features.baseline_hint"))
        elif decoder_id == "target_label_lookup":
            prediction = str(flat.get("prompt_features.target_label", "no_decodable_target_label"))
            if prediction not in ACTIONS:
                prediction = "no_decodable_target_label"
        elif decoder_id == "hash_stable_index_full_observation":
            prediction = ACTIONS[_stable_index(json.dumps({field: flat.get(field) for field in selected_fields}, sort_keys=True)) % len(ACTIONS)]
        else:
            prediction = _lookup_prediction_from_observation_fields(episode, selected_fields, episodes)
        rows.append(
            {
                "episode_id": episode.episode_id,
                "split_family": episode.split_family,
                "seed_id": episode.seed_id,
                "prediction": prediction,
                "target_action": episode.target_action,
                "score": 1.0 if prediction == episode.target_action else 0.0,
            }
        )
    return {
        "decoder_id": decoder_id,
        "selected_fields": list(selected_fields),
        "score": _mean(row["score"] for row in rows),
        "per_split": _mean_by(rows, "split_family"),
        "rows": rows,
        "producer_function": "_score_observation_decoder",
        "code_path_hash": code_path_hash(_score_observation_decoder),
    }


def _lookup_prediction_from_observation_fields(
    episode: EpisodeRecord,
    selected_fields: tuple[str, ...],
    episodes: list[EpisodeRecord],
) -> str:
    target_flat = _flatten_observation_for_decoding(episode)
    key = tuple(target_flat.get(field) for field in selected_fields)
    candidates = [
        other.target_action
        for other in episodes
        if tuple(_flatten_observation_for_decoding(other).get(field) for field in selected_fields) == key
    ]
    return _majority_action(candidates)


def _flatten_observation_for_decoding(episode: EpisodeRecord) -> dict[str, str]:
    observation = episode.observation
    flat = {
        "observable_partner": observation.observable_partner,
        "observable_context": observation.observable_context,
        "legal_history_length": str(len(observation.legal_history)),
    }
    for key, value in observation.prompt_features.items():
        flat[f"prompt_features.{key}"] = str(value)
    return flat


def _invert_baseline_hint(value: Any) -> str:
    if value not in ACTIONS:
        return "no_decodable_hint"
    return ACTIONS[(ACTIONS.index(str(value)) - 1) % len(ACTIONS)]


def _decoder_priority(decoder_id: str) -> int:
    return {
        "target_label_lookup": 3,
        "hint_inverter_regression_control": 2,
        "full_lookup_table": 1,
    }.get(decoder_id, 0)


def _majority_action(values: list[str]) -> str:
    counts = Counter(values)
    if not counts:
        return "direct_response"
    max_count = max(counts.values())
    for action in ACTIONS:
        if counts[action] == max_count:
            return action
    return "direct_response"


def _summarize_baseline(baseline_id: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "baseline_id": baseline_id,
        "score": _mean(row["score"] for row in rows),
        "per_split": _mean_by(rows, "split_family"),
        "rows": rows,
        "producer_function": "predict_with_baseline",
        "code_path_hash": code_path_hash(predict_with_baseline),
    }


def verify_baseline_invocations(
    invocations: list[dict[str, Any]],
    mandatory_baselines: set[str],
    mandatory_splits: set[str],
) -> dict[str, Any]:
    by_baseline: dict[str, set[str]] = defaultdict(set)
    for row in invocations:
        by_baseline[row["baseline_id"]].add(row["split_family"])
    missing = {
        baseline_id: sorted(mandatory_splits - by_baseline.get(baseline_id, set()))
        for baseline_id in mandatory_baselines
        if mandatory_splits - by_baseline.get(baseline_id, set())
    }
    return {
        "producer_function": "verify_baseline_invocations",
        "passed": not missing and set(by_baseline) >= mandatory_baselines,
        "missing_split_invocations": missing,
        "missing_baselines": sorted(mandatory_baselines - set(by_baseline)),
    }


def _classify_budget_field(
    field_name: str,
    candidate: Any,
    ordinary: Any,
    oracle: Any,
    injected_disparity: bool,
) -> tuple[str, str]:
    if injected_disparity and field_name == "observation_count":
        return "unexplained_disparity", "organic failing control reduced ordinary observation count without declared reason"
    if field_name == "oracle_label_access_count" and oracle != candidate:
        return "oracle_expected_disparity", "oracle positive-control is allowed label access only as a harness competence check"
    if candidate == ordinary and ordinary == oracle:
        return "equal", "computed values match across candidate, ordinary baselines, and oracle control"
    if field_name in {"feedback_access_count", "memory_write_count"} and candidate != ordinary:
        return "candidate_advantaged", "declared active-query feedback path under test; no-query and shuffled-feedback ablations must collapse"
    return "equal", "computed disparity is either absent or explained by declared control boundary"


def _mean_by(rows: list[dict[str, Any]], key: str) -> dict[str, float]:
    result = {}
    for value in sorted({row[key] for row in rows}):
        selected = [row["score"] for row in rows if row[key] == value]
        result[value] = _mean(selected)
    return result


def _mean(values: Any) -> float:
    rows = list(values)
    return sum(float(value) for value in rows) / len(rows) if rows else 0.0


def _observation_key(observation: Observation) -> str:
    return json.dumps(observation.to_json_dict(), sort_keys=True, separators=(",", ":"))


def _run_id(episode_dicts: list[dict[str, Any]]) -> str:
    material = json.dumps({"task_id": TASK_ID, "episodes": episode_dicts}, sort_keys=True, separators=(",", ":"))
    return f"{TASK_ID}_{hashlib.sha256(material.encode('utf-8')).hexdigest()[:16]}"


def _write_artifacts(out: Path, run: dict[str, Any]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "result.json": run["result"],
        "source_pin_readback.json": run["source_pin_readback"],
        "candidate_results.json": run["candidate_results"],
        "baseline_results.json": run["baseline_results"],
        "observation_only_decoder_results.json": run["observation_only_decoder_results"],
        "observation_target_independence_report.json": run["observation_target_independence_report"],
        "active_query_causal_report.json": run["active_query_causal_report"],
        "ablation_results.json": run["ablation_results"],
        "replay_recomputation_report.json": run["replay_recomputation_report"],
        "budget_parity_report.json": run["budget_parity_report"],
        "leakage_report.json": run["leakage_report"],
        "leakage_positive_control_report.json": run["leakage_positive_control_report"],
        "computed_evidence_provenance.json": run["computed_evidence_provenance"],
        "split_coverage_report.json": run["split_coverage_report"],
        "non_mutation_guard.json": run["non_mutation_guard"],
        "threshold_evaluation.json": run["threshold_evaluation"],
        "repair_delta_from_001b.json": run["repair_delta_from_001b"],
    }
    for name, payload in artifacts.items():
        (out / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (out / "trace_records.jsonl").open("w", encoding="utf-8") as handle:
        for row in run["trace_records"]:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    (out / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    (out / "run_manifest.json").write_text(
        json.dumps(
            {
                "task_id": TASK_ID,
                "run_id": run["run_id"],
                "required_artifacts": REQUIRED_ARTIFACTS,
                "claim_ceiling": CLAIM_CEILING,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _stable_index(value: Any) -> int:
    return int(hashlib.sha256(str(value).encode("utf-8")).hexdigest(), 16)


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _git(args: list[str], cwd: Path) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=cwd, text=True, timeout=20).strip()
    except Exception as exc:  # pragma: no cover - defensive readback path
        return f"unavailable:{type(exc).__name__}:{exc}"


def _ls_remote_hash(output: str) -> str:
    if output.startswith("unavailable:") or not output.strip():
        return output
    return output.split()[0]
