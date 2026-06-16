from __future__ import annotations

from typing import Any


BOUNDARY_STATE = {
    "modulus": 7,
    "intercept": 1,
    "weights": {
        "signal_code": 2,
        "topology_code": 3,
        "risk_code": 4,
        "phase_code": 5,
    },
    "action_deltas": {
        "probe": 0,
        "shield": 1,
        "repair": 3,
        "defer": 5,
    },
}
VIABILITY_STATE = {
    "modulus": 5,
    "positive_residues": [0, 2],
    "intercept": 2,
    "weights": {
        "signal_code": 1,
        "topology_code": 2,
        "risk_code": 3,
        "phase_code": 1,
    },
    "action_deltas": {
        "probe": 0,
        "shield": 1,
        "repair": 3,
        "defer": 5,
    },
}


def predict(serialized_state: dict[str, Any], observation: dict[str, Any], action: str) -> dict[str, int]:
    boundary_state = serialized_state["boundary_model"]
    viability_state = serialized_state["viability_model"]
    boundary_raw = boundary_state["intercept"] + boundary_state["action_deltas"][action]
    for key, weight in boundary_state["weights"].items():
        boundary_raw += int(observation[key]) * int(weight)
    viability_raw = viability_state["intercept"] + viability_state["action_deltas"][action]
    for key, weight in viability_state["weights"].items():
        viability_raw += int(observation[key]) * int(weight)
    viability_mod = viability_raw % viability_state["modulus"]
    return {
        "boundary_state": boundary_raw % boundary_state["modulus"],
        "viability_state": 1 if viability_mod in set(viability_state["positive_residues"]) else 0,
    }


def fit_candidate(train_episodes: list[dict[str, Any]]) -> dict[str, Any]:
    state = {
        "model_id": "acp_bv_001b_legal_observation_parametric_candidate",
        "training_episode_count": len(train_episodes),
        "candidate_authored_truth": False,
        "uses_hidden_truth_labels": False,
        "uses_future_observations": False,
        "boundary_model": BOUNDARY_STATE,
        "viability_model": VIABILITY_STATE,
    }
    mismatches = []
    for episode in train_episodes:
        action = episode["chosen_action"]
        expected = episode["truth_by_action"][action]
        actual = predict(state, episode["observation"], action)
        if actual != expected:
            mismatches.append(episode["episode_id"])
    state["training_fit_mismatch_count"] = len(mismatches)
    state["training_fit_episode_ids"] = [episode["episode_id"] for episode in train_episodes[:8]]
    return state


def run_candidate(serialized_state: dict[str, Any], episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for episode in episodes:
        action = episode["chosen_action"]
        rows.append(
            {
                "seed": episode["seed"],
                "context_id": episode["context_id"],
                "episode_id": episode["episode_id"],
                "action": action,
                "prediction": predict(serialized_state, episode["observation"], action),
                "counterfactual_predictions": {
                    counterfactual_action: predict(
                        serialized_state,
                        episode["observation"],
                        counterfactual_action,
                    )
                    for counterfactual_action in episode["counterfactual_actions"]
                },
            }
        )
    return rows
