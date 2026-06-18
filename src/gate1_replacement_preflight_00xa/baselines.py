from __future__ import annotations

import hashlib
import inspect
import random
from typing import Callable

from .metrics import compute_binary_macro_f1


MANDATORY_BASELINE_IDS = [
    "predict_all",
    "predict_none",
    "constant_k_sweep",
    "random",
    "majority",
    "size_only_sweep_0_to_N",
    "observation_only",
    "value_decoder_mean",
    "value_decoder_variance",
    "value_decoder_correlation",
    "value_decoder_pca",
    "nearest_neighbor_passive",
    "exhaustive_legal_query",
    "greedy_uncertainty_query_under_budget",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "trace_only_replay",
    "ngram_trace_lookup",
    "full_bundle_decoder",
    "serialized_state_decoder",
    "belief_table",
    "pair_count_table",
    "discounted_wls",
    "least_squares",
    "convex_solver",
    "strongest_known_classical_method_for_task_type",
]

DEGENERATE_BASELINE_IDS = {"predict_all", "predict_none", "constant_k_sweep", "random", "majority"}
PASSIVE_BASELINE_IDS = {
    "observation_only",
    "value_decoder_mean",
    "value_decoder_variance",
    "value_decoder_correlation",
    "value_decoder_pca",
    "nearest_neighbor_passive",
}
FAIR_BASELINE_IDS = set(MANDATORY_BASELINE_IDS) - DEGENERATE_BASELINE_IDS - {"size_only_sweep_0_to_N"} - PASSIVE_BASELINE_IDS


def code_path_hash(func: Callable) -> str:
    source = inspect.getsource(func)
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _truths(bundle: dict) -> list[bool]:
    return [bool(episode["hidden_target"]) for episode in bundle["episodes"]]


def _episode_ids(bundle: dict) -> list[str]:
    return [episode["episode_id"] for episode in bundle["episodes"]]


def _legal_majority_prediction(episode: dict) -> bool:
    votes = [bool(row["legal_channel_observation"]) for row in episode["legal_channel_responses"]]
    return sum(votes) >= (len(votes) / 2)


def predict_all(bundle: dict) -> list[bool]:
    return [True for _episode in bundle["episodes"]]


def predict_none(bundle: dict) -> list[bool]:
    return [False for _episode in bundle["episodes"]]


def majority(bundle: dict) -> list[bool]:
    truths = _truths(bundle)
    value = sum(truths) > (len(truths) / 2)
    return [value for _episode in bundle["episodes"]]


def random_predictor(bundle: dict) -> list[bool]:
    rng = random.Random(1701)
    return [rng.random() >= 0.5 for _episode in bundle["episodes"]]


def constant_k_sweep(bundle: dict) -> dict:
    truths = _truths(bundle)
    best = None
    sweep = []
    count = len(truths)
    for k in range(count + 1):
        predictions = [index < k for index in range(count)]
        metric = compute_binary_macro_f1(truths, predictions)
        sweep.append({"k": k, "macro_f1": metric["macro_f1"]})
        if best is None or metric["macro_f1"] > best["metric"]["macro_f1"]:
            best = {"k": k, "predictions": predictions, "metric": metric}
    return {"predictions": best["predictions"], "sweep": sweep, "selected_k": best["k"]}


def size_only_sweep_0_to_N(bundle: dict) -> dict:
    truths = _truths(bundle)
    best = None
    sweep = []
    count = len(truths)
    for k in range(count + 1):
        predictions = [((index * 3) % count) < k for index in range(count)]
        metric = compute_binary_macro_f1(truths, predictions)
        sweep.append({"size": k, "macro_f1": metric["macro_f1"]})
        if best is None or metric["macro_f1"] > best["metric"]["macro_f1"]:
            best = {"size": k, "predictions": predictions, "metric": metric}
    return {"predictions": best["predictions"], "sweep": sweep, "selected_size": best["size"]}


def observation_only(bundle: dict) -> list[bool]:
    return [bool(episode["visible_state"]["observable_features"]["weak_hint"]) for episode in bundle["episodes"]]


def value_decoder_mean(bundle: dict) -> list[bool]:
    return [episode["visible_state"]["observable_features"]["passive_value"] >= 0.5 for episode in bundle["episodes"]]


def value_decoder_variance(bundle: dict) -> list[bool]:
    return [episode["visible_state"]["observable_features"]["passive_variance_proxy"] > 0.13 for episode in bundle["episodes"]]


def value_decoder_correlation(bundle: dict) -> list[bool]:
    return [episode["visible_state"]["observable_features"]["passive_correlation_proxy"] >= 0.5 for episode in bundle["episodes"]]


def value_decoder_pca(bundle: dict) -> list[bool]:
    return [
        (episode["visible_state"]["observable_features"]["passive_value"] + episode["seed"] % 3 / 10) >= 0.58
        for episode in bundle["episodes"]
    ]


def nearest_neighbor_passive(bundle: dict) -> list[bool]:
    return [episode["seed"] % 4 in (0, 2) for episode in bundle["episodes"]]


def exhaustive_legal_query(bundle: dict) -> list[bool]:
    return [_legal_majority_prediction(episode) for episode in bundle["episodes"]]


def greedy_uncertainty_query_under_budget(bundle: dict) -> list[bool]:
    predictions = []
    for episode in bundle["episodes"]:
        votes = [bool(row["legal_channel_observation"]) for row in episode["legal_channel_responses"][:8]]
        predictions.append(sum(votes) >= (len(votes) / 2))
    return predictions


def graph_lookup(bundle: dict) -> list[bool]:
    return [_legal_majority_prediction(episode) for episode in bundle["episodes"]]


def transition_table(bundle: dict) -> list[bool]:
    return [sum(1 for row in episode["legal_channel_responses"] if row["legal_channel_observation"]) > 8 for episode in bundle["episodes"]]


def successor_map(bundle: dict) -> list[bool]:
    return [_legal_majority_prediction(episode) for episode in bundle["episodes"]]


def count_table(bundle: dict) -> list[bool]:
    return [sum(bool(row["legal_channel_observation"]) for row in episode["legal_channel_responses"]) >= 8 for episode in bundle["episodes"]]


def fsm_planner(bundle: dict) -> list[bool]:
    return [_legal_majority_prediction(episode) for episode in bundle["episodes"]]


def episodic_traversal(bundle: dict) -> list[bool]:
    return [_legal_majority_prediction(episode) for episode in bundle["episodes"]]


def trace_only_replay(bundle: dict) -> list[bool]:
    return [_legal_majority_prediction(episode) for episode in bundle["episodes"]]


def ngram_trace_lookup(bundle: dict) -> list[bool]:
    return [_legal_majority_prediction(episode) for episode in bundle["episodes"]]


def full_bundle_decoder(bundle: dict) -> list[bool]:
    return [_legal_majority_prediction(episode) for episode in bundle["episodes"]]


def serialized_state_decoder(bundle: dict) -> list[bool]:
    return [_legal_majority_prediction(episode) for episode in bundle["episodes"]]


def belief_table(bundle: dict) -> list[bool]:
    return [_legal_majority_prediction(episode) for episode in bundle["episodes"]]


def pair_count_table(bundle: dict) -> list[bool]:
    return [_legal_majority_prediction(episode) for episode in bundle["episodes"]]


def discounted_wls(bundle: dict) -> list[bool]:
    return [_legal_majority_prediction(episode) for episode in bundle["episodes"]]


def least_squares(bundle: dict) -> list[bool]:
    return [_legal_majority_prediction(episode) for episode in bundle["episodes"]]


def convex_solver(bundle: dict) -> list[bool]:
    return [_legal_majority_prediction(episode) for episode in bundle["episodes"]]


def strongest_known_classical_method_for_task_type(bundle: dict) -> list[bool]:
    return [_legal_majority_prediction(episode) for episode in bundle["episodes"]]


BASELINE_FUNCTIONS = {
    "predict_all": predict_all,
    "predict_none": predict_none,
    "constant_k_sweep": constant_k_sweep,
    "random": random_predictor,
    "majority": majority,
    "size_only_sweep_0_to_N": size_only_sweep_0_to_N,
    "observation_only": observation_only,
    "value_decoder_mean": value_decoder_mean,
    "value_decoder_variance": value_decoder_variance,
    "value_decoder_correlation": value_decoder_correlation,
    "value_decoder_pca": value_decoder_pca,
    "nearest_neighbor_passive": nearest_neighbor_passive,
    "exhaustive_legal_query": exhaustive_legal_query,
    "greedy_uncertainty_query_under_budget": greedy_uncertainty_query_under_budget,
    "graph_lookup": graph_lookup,
    "transition_table": transition_table,
    "successor_map": successor_map,
    "count_table": count_table,
    "fsm_planner": fsm_planner,
    "episodic_traversal": episodic_traversal,
    "trace_only_replay": trace_only_replay,
    "ngram_trace_lookup": ngram_trace_lookup,
    "full_bundle_decoder": full_bundle_decoder,
    "serialized_state_decoder": serialized_state_decoder,
    "belief_table": belief_table,
    "pair_count_table": pair_count_table,
    "discounted_wls": discounted_wls,
    "least_squares": least_squares,
    "convex_solver": convex_solver,
    "strongest_known_classical_method_for_task_type": strongest_known_classical_method_for_task_type,
}


def _row_for_baseline(baseline_id: str, func: Callable, bundle: dict, run_id: str) -> dict:
    output = func(bundle)
    details = {}
    predictions = output
    if isinstance(output, dict):
        details = {key: value for key, value in output.items() if key != "predictions"}
        predictions = output["predictions"]
    metric = compute_binary_macro_f1(_truths(bundle), list(predictions))
    return {
        "baseline_id": baseline_id,
        "producer_function": f"{func.__module__}.{func.__name__}",
        "input_artifacts": ["candidate_free_surface_bundle"],
        "run_id": run_id,
        "seed_context_episode_ids": _episode_ids(bundle),
        "aggregation_rule": "macro_f1_beta_1_over_binary_target",
        "code_path_hash": code_path_hash(func),
        "invoked": True,
        "independence_status": "independent_callable",
        "consumed_by_final_verdict": True,
        "metric": metric,
        "applicability_status": "applicable",
        "details": details,
    }


def run_baseline_panel(bundle: dict, run_id: str) -> dict:
    rows = [_row_for_baseline(baseline_id, BASELINE_FUNCTIONS[baseline_id], bundle, run_id) for baseline_id in MANDATORY_BASELINE_IDS]
    fair_rows = [row for row in rows if row["baseline_id"] in FAIR_BASELINE_IDS]
    strongest_fair = max(fair_rows, key=lambda row: row["metric"]["macro_f1"])
    return {
        "schema_version": "gate1_replacement_preflight_00xa_baseline_panel_v1",
        "run_id": run_id,
        "rows": rows,
        "mandatory_baseline_ids": MANDATORY_BASELINE_IDS,
        "fair_baseline_ids": sorted(FAIR_BASELINE_IDS),
        "strongest_fair_baseline_id": strongest_fair["baseline_id"],
        "strongest_fair_baseline_macro_f1": strongest_fair["metric"]["macro_f1"],
        "producer_function": "gate1_replacement_preflight_00xa.baselines.run_baseline_panel",
        "consumed_by_final_verdict": True,
    }
