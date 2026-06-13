from __future__ import annotations

import copy
import hashlib
import inspect
from typing import Any

from .schemas import Action, CandidateState, EpisodeRecord, Feedback, Observation


POLICY_PATH = "gate4_replacement_discriminative_social_latent_001b.candidate.choose_final_action"
UPDATE_PATH = "gate4_replacement_discriminative_social_latent_001b.candidate.update_from_feedback"


def initial_state() -> CandidateState:
    return CandidateState()


def belief_key(observation: Observation) -> str:
    return f"{observation.observable_partner}|{observation.observable_context}"


def choose_active_query(state: CandidateState, observation: Observation) -> Action:
    key = belief_key(observation)
    if key not in state.beliefs and observation.prompt_features.get("query_available") is True:
        return Action(action_type="active_query", value="ask_preference", confidence=0.55)
    return Action(action_type="active_query", value="skip_query", confidence=0.85)


def update_from_feedback(state: CandidateState, observation: Observation, feedback: Feedback) -> CandidateState:
    key = belief_key(observation)
    beliefs = dict(state.beliefs)
    uncertainty = dict(state.uncertainty)
    if feedback.feedback_type == "preference" and feedback.value.startswith("prefers:"):
        beliefs[key] = feedback.value.split(":", 1)[1]
        uncertainty[key] = 0.05
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
        return Action(action_type="final", value=state.beliefs[key], confidence=0.95)
    fallback = str(observation.prompt_features.get("baseline_hint", "direct_response"))
    return Action(action_type="final", value=fallback, confidence=0.25 + min(reads, 1) * 0.05)


def run_candidate_on_episode(
    episode: EpisodeRecord,
    intervention_id: str | None = None,
    run_label: str = "candidate",
) -> dict[str, Any]:
    state = initial_state()
    observation = episode.observation
    serialized_before = state.to_json_dict()
    query_action = choose_active_query(state, observation)
    feedback_value = episode.query_feedback
    if intervention_id in {"no_active_query", "no_feedback", "no_action"}:
        feedback = Feedback(feedback_type="none", value="none")
    elif intervention_id == "shuffled_feedback":
        feedback = Feedback(feedback_type="preference", value=episode.counterfactual_feedback)
    elif intervention_id == "counterfactual_transition":
        feedback = Feedback(feedback_type="preference", value=episode.counterfactual_feedback)
    else:
        feedback = Feedback(feedback_type="preference", value=feedback_value)

    if intervention_id == "no_state":
        updated = state
    elif intervention_id == "no_feedback":
        updated = update_from_feedback(state, observation, Feedback(feedback_type="none", value="none"))
    elif intervention_id == "no_action":
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
        "action_policy_path": POLICY_PATH,
        "update_path": UPDATE_PATH,
        "score": score,
        "active_query_changed_feedback": feedback.value != "none",
        "state_update_recomputed_required": True,
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
        "code_path_hash": code_path_hash(run_candidate_on_episode),
    }


def rerun_with_intervention(episode: EpisodeRecord, intervention_id: str) -> dict[str, Any]:
    return run_candidate_on_episode(
        copy.deepcopy(episode),
        intervention_id=intervention_id,
        run_label=f"candidate_{intervention_id}",
    )


def code_path_hash(func: Any) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()

