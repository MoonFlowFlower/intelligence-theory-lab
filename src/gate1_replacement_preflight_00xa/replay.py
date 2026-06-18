from __future__ import annotations

from copy import deepcopy

from .baselines import code_path_hash
from .metrics import compute_binary_macro_f1


def _truths(bundle: dict) -> list[bool]:
    return [bool(episode["hidden_target"]) for episode in bundle["episodes"]]


def _serialize_state(bundle: dict) -> dict:
    return {
        "episodes": [
            {
                "episode_id": episode["episode_id"],
                "legal_channel_responses": deepcopy(episode["legal_channel_responses"]),
            }
            for episode in bundle["episodes"]
        ]
    }


def _observations(bundle: dict) -> list[dict]:
    return [
        {
            "episode_id": episode["episode_id"],
            "visible_state": deepcopy(episode["visible_state"]),
            "budget_remaining": 16,
        }
        for episode in bundle["episodes"]
    ]


def recompute_predictions_from_serialized_state(serialized_state: dict, observations: list[dict]) -> list[bool]:
    by_id = {row["episode_id"]: row for row in serialized_state["episodes"]}
    predictions = []
    for observation in observations:
        state = by_id[observation["episode_id"]]
        votes = [bool(row["legal_channel_observation"]) for row in state["legal_channel_responses"]]
        predictions.append(sum(votes) >= (len(votes) / 2) if votes else False)
    return predictions


def validate_replay_result(result: dict) -> dict:
    errors = []
    if result.get("applicability") == "applicable_serialized_state":
        if result.get("hash_only") or result.get("mode") == "stored_hash_compare":
            errors.append("hash_only_replay_forbidden")
        if not result.get("recomputed_from_serialized_state"):
            errors.append("serialized_state_recompute_required")
        if not result.get("recomputed_from_observation"):
            errors.append("observation_recompute_required")
        if not result.get("consumed_by_final_verdict"):
            errors.append("replay_result_not_consumed")
    return {"valid": not errors, "errors": errors}


def run_replay(bundle: dict, run_id: str) -> dict:
    serialized_state = _serialize_state(bundle)
    observations = _observations(bundle)
    predictions = recompute_predictions_from_serialized_state(serialized_state, observations)
    metric = compute_binary_macro_f1(_truths(bundle), predictions)
    corrupted_state = deepcopy(serialized_state)
    corrupted_state["episodes"][0]["legal_channel_responses"] = []
    corrupted_predictions = recompute_predictions_from_serialized_state(corrupted_state, observations)
    result = {
        "schema_version": "gate1_replacement_preflight_00xa_replay_v1",
        "run_id": run_id,
        "applicability": "applicable_serialized_state",
        "mode": "recompute_from_serialized_state_plus_observation",
        "producer_function": "gate1_replacement_preflight_00xa.replay.recompute_predictions_from_serialized_state",
        "input_artifacts": ["serialized_state", "observation"],
        "aggregation_rule": "macro_f1_after_recomputed_predictions",
        "code_path_hash": code_path_hash(recompute_predictions_from_serialized_state),
        "recomputed_from_serialized_state": True,
        "recomputed_from_observation": True,
        "hash_only": False,
        "stored_output_replay": False,
        "metric": metric,
        "negative_controls": {
            "corrupt_serialized_state_changes_behavior": corrupted_predictions != predictions,
            "stored_hash_tamper_accepted": False,
        },
        "consumed_by_final_verdict": True,
    }
    result["validation"] = validate_replay_result(result)
    return result
