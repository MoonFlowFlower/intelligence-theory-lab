from __future__ import annotations

from copy import deepcopy
from typing import Any


ACTIONS = ["probe", "shield", "repair"]
SIGNAL_VALUE = {"low": 0, "mid": 1, "high": 2}
ACTION_DELTA = {"probe": 1, "shield": -1, "repair": 0}


def generate_episodes(split: str = "heldout") -> list[dict[str, Any]]:
    seeds = ["seed_a", "seed_b"] if split == "train" else ["seed_c", "seed_d"]
    contexts = [
        ("ctx_low_mesh", "low", 0, 1),
        ("ctx_mid_chain", "mid", 1, 2),
        ("ctx_high_mesh", "high", 0, 3),
        ("ctx_low_chain", "low", 1, 0),
        ("ctx_mid_mesh", "mid", 0, 2),
        ("ctx_high_chain", "high", 1, 1),
    ]
    episodes: list[dict[str, Any]] = []
    for seed_index, seed in enumerate(seeds):
        for context_index, (context, signal, topology, risk) in enumerate(contexts):
            action = ACTIONS[(seed_index + context_index) % len(ACTIONS)]
            counterfactuals = [candidate for candidate in ACTIONS if candidate != action][:2]
            episodes.append(
                {
                    "seed": seed,
                    "context_id": f"{split}_{context}_{seed_index}",
                    "episode_id": f"{split}_ep_{seed_index}_{context_index}",
                    "chosen_action": action,
                    "harness_selected_counterfactual_actions": counterfactuals,
                    "observation": {
                        "signal": signal,
                        "topology": topology,
                        "risk": risk,
                        "available_actions": list(ACTIONS),
                    },
                }
            )
    return episodes


def held_out_truth_generator(episode: dict[str, Any], action: str) -> dict[str, Any]:
    observation = episode["observation"]
    signal = SIGNAL_VALUE[observation["signal"]]
    topology = int(observation["topology"])
    risk = int(observation["risk"])
    action_delta = ACTION_DELTA[action]
    boundary = (signal + topology + action_delta) % 3
    viability = 1 if (risk + topology + action_delta) % 4 in {0, 3} else 0
    return {
        "boundary_delta": boundary,
        "viability_state": viability,
    }


def counterfactual_truth_generator(episode: dict[str, Any], action: str) -> dict[str, Any]:
    return held_out_truth_generator(episode, action)


def clean_serialized_state() -> dict[str, Any]:
    return {
        "model_family": "repo_owned_reference_acp_bv_control",
        "signal_weights": deepcopy(SIGNAL_VALUE),
        "action_deltas": deepcopy(ACTION_DELTA),
        "uses_action_conditioning": True,
        "uses_boundary_state": True,
        "uses_viability_state": True,
    }


def reference_candidate_predict(
    serialized_state: dict[str, Any],
    observation: dict[str, Any],
    action: str,
) -> dict[str, Any]:
    signal = serialized_state["signal_weights"][observation["signal"]]
    topology = int(observation["topology"])
    risk = int(observation["risk"])
    action_delta = serialized_state["action_deltas"][action]
    boundary = (signal + topology + action_delta) % 3
    viability = 1 if (risk + topology + action_delta) % 4 in {0, 3} else 0
    return {
        "boundary_delta": boundary,
        "viability_state": viability,
    }


def build_clean_candidate_bundle() -> dict[str, Any]:
    episodes = generate_episodes("heldout")
    serialized_state = clean_serialized_state()
    outputs = []
    for episode in episodes:
        action = episode["chosen_action"]
        outputs.append(
            {
                "seed": episode["seed"],
                "context_id": episode["context_id"],
                "episode_id": episode["episode_id"],
                "action": action,
                "prediction": reference_candidate_predict(serialized_state, episode["observation"], action),
                "counterfactual_predictions": {
                    counterfactual: reference_candidate_predict(
                        serialized_state,
                        episode["observation"],
                        counterfactual,
                    )
                    for counterfactual in episode["harness_selected_counterfactual_actions"]
                },
            }
        )
    return {
        "bundle_id": "clean_repo_owned_reference_candidate_control",
        "serialized_state": serialized_state,
        "episodes": episodes,
        "candidate_outputs": outputs,
    }


def build_easy_action_bundle() -> dict[str, Any]:
    bundle = build_clean_candidate_bundle()
    bundle["bundle_id"] = "easy_action_payload"
    for episode, output in zip(bundle["episodes"], bundle["candidate_outputs"]):
        easy_action = "probe"
        output["action"] = easy_action
        output["prediction"] = reference_candidate_predict(
            bundle["serialized_state"],
            episode["observation"],
            easy_action,
        )
        output["counterfactual_predictions"] = {}
    return bundle


def build_lookup_memorization_bundle() -> dict[str, Any]:
    bundle = build_clean_candidate_bundle()
    bundle["bundle_id"] = "lookup_memorization_payload"
    bundle["serialized_state"]["lookup_table"] = {
        output["context_id"]: output["prediction"]
        for output in bundle["candidate_outputs"][:3]
    }
    for output in bundle["candidate_outputs"][3:]:
        output["prediction"] = {"boundary_delta": 0, "viability_state": 0}
        output["counterfactual_predictions"] = {}
    return bundle
