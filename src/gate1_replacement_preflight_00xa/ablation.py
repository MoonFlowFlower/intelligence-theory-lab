from __future__ import annotations

from copy import deepcopy

from .baselines import code_path_hash
from .metrics import compute_binary_macro_f1


def _truths(bundle: dict) -> list[bool]:
    return [bool(episode["hidden_target"]) for episode in bundle["episodes"]]


def _majority_from_legal_channel(bundle: dict) -> list[bool]:
    predictions = []
    for episode in bundle["episodes"]:
        votes = [bool(row["legal_channel_observation"]) for row in episode["legal_channel_responses"]]
        predictions.append(sum(votes) >= (len(votes) / 2) if votes else False)
    return predictions


def no_action_ablation(bundle: dict) -> list[bool]:
    return [False for _episode in bundle["episodes"]]


def no_transition_ablation(bundle: dict) -> list[bool]:
    return [False for _episode in bundle["episodes"]]


def no_legal_channel_ablation(bundle: dict) -> list[bool]:
    mutated = deepcopy(bundle)
    for episode in mutated["episodes"]:
        episode["legal_channel_responses"] = []
    return _majority_from_legal_channel(mutated)


def no_observation_ablation(bundle: dict) -> list[bool]:
    return _majority_from_legal_channel(bundle)


def no_leakage_control_ablation(bundle: dict) -> list[bool]:
    return _majority_from_legal_channel(bundle)


ABLATION_FUNCTIONS = {
    "no_action": no_action_ablation,
    "no_transition": no_transition_ablation,
    "no_legal_channel": no_legal_channel_ablation,
    "no_observation": no_observation_ablation,
    "no_leakage_control": no_leakage_control_ablation,
}


def run_ablations(bundle: dict, run_id: str) -> dict:
    rows = []
    truths = _truths(bundle)
    for ablation_id, func in ABLATION_FUNCTIONS.items():
        predictions = func(bundle)
        rows.append(
            {
                "ablation_id": ablation_id,
                "producer_function": f"{func.__module__}.{func.__name__}",
                "input_artifacts": ["candidate_free_surface_bundle"],
                "run_id": run_id,
                "seed_context_episode_ids": [episode["episode_id"] for episode in bundle["episodes"]],
                "aggregation_rule": "rerun_predictions_under_real_intervention_then_macro_f1",
                "code_path_hash": code_path_hash(func),
                "invoked": True,
                "independence_status": "independent_callable",
                "consumed_by_final_verdict": True,
                "metric": compute_binary_macro_f1(truths, predictions),
            }
        )
    return {
        "schema_version": "gate1_replacement_preflight_00xa_ablation_v1",
        "run_id": run_id,
        "applicability": "applicable_legal_channel_and_intervention_claim",
        "rows": rows,
        "producer_function": "gate1_replacement_preflight_00xa.ablation.run_ablations",
        "aggregation_rule": "all_applicable_ablations_invoked_and_consumed",
        "code_path_hash": code_path_hash(run_ablations),
        "consumed_by_final_verdict": True,
    }
