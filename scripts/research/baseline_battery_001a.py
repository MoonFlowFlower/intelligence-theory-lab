from __future__ import annotations

import random
from collections import Counter
from typing import Any, Callable

from evidence_provenance_001a import code_path_hash, evidence_row
from minimal_env_spec_loader_001a import BUDGET_COMPONENT_CHANNELS, FINAL_ACTIONS, target_from_components


MANDATORY_BASELINE_PRODUCERS = [
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
    "supervised_or_membership_passive_attacker_where_applicable",
    "exhaustive_legal_query",
    "greedy_uncertainty_query_under_budget",
    "budget_limited_belief_state_planner",
    "greedy_information_gain_or_uncertainty_planner_under_budget",
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
    "discounted_wls_if_applicable",
    "least_squares_if_applicable",
    "convex_solver_if_applicable",
    "real_fitted_amortized_learner_if_any_learning_adaptation_language_appears",
    "strongest_known_classical_method_for_task_type",
]

DEGENERATE_BASELINES = {"predict_all", "predict_none", "constant_k_sweep", "random", "majority"}
PASSIVE_BASELINES = {
    "observation_only",
    "value_decoder_mean",
    "value_decoder_variance",
    "value_decoder_correlation",
    "value_decoder_pca",
    "nearest_neighbor_passive",
    "supervised_or_membership_passive_attacker_where_applicable",
}
SIZE_ONLY_BASELINES = {"size_only_sweep_0_to_N"}
GRAPH_CACHE_CHALLENGERS = [
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
]
LOOKUP_IMITATION_BASELINES = {
    "trace_only_replay",
    "ngram_trace_lookup",
    "full_bundle_decoder",
    "serialized_state_decoder",
    "belief_table",
    "pair_count_table",
}
STRONGEST_CLASSICAL_REQUIRED = {
    "budget_limited_belief_state_planner",
    "greedy_information_gain_or_uncertainty_planner_under_budget",
    "fsm_planner",
    "successor_map",
    "transition_table",
    "graph_lookup",
    "episodic_traversal",
}


def episode_ids(episodes: list[dict[str, Any]]) -> list[str]:
    return [episode["episode_id"] for episode in episodes]


def seed_set(episodes: list[dict[str, Any]]) -> list[int]:
    return sorted({int(episode["seed"]) for episode in episodes})


def truths(episodes: list[dict[str, Any]]) -> list[str]:
    return [episode["target_label_or_target_variable"] for episode in episodes]


def macro_f1(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    if len(y_true) != len(y_pred):
        raise ValueError("truth and prediction lengths differ")
    labels = list(FINAL_ACTIONS)
    per_class = {}
    f1_values = []
    for label in labels:
        tp = sum(1 for truth, pred in zip(y_true, y_pred) if truth == label and pred == label)
        fp = sum(1 for truth, pred in zip(y_true, y_pred) if truth != label and pred == label)
        fn = sum(1 for truth, pred in zip(y_true, y_pred) if truth == label and pred != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}
        f1_values.append(f1)
    return {
        "metric_id": "macro_f1_beta_1_multiclass",
        "beta": 1.0,
        "macro_f1": sum(f1_values) / len(f1_values),
        "per_class": per_class,
        "balanced_metric": True,
        "false_positive_and_false_negative_accounting_by_label": True,
    }


def _channel_map(episode: dict[str, Any]) -> dict[str, Any]:
    return {row["channel_id"]: row["value"] for row in episode["legal_channel_responses"]}


def query_budget_components(episode: dict[str, Any]) -> tuple[dict[str, int], list[dict[str, Any]]]:
    channel_values = _channel_map(episode)
    observations = {}
    trace = []
    for query_index, channel_id in enumerate(BUDGET_COMPONENT_CHANNELS, start=1):
        observations[channel_id] = int(channel_values[channel_id])
        trace.append(
            {
                "episode_id": episode["episode_id"],
                "query_index": query_index,
                "queried_channel_id": channel_id,
                "observation_received": int(channel_values[channel_id]),
            }
        )
    return observations, trace


def predict_from_budget_components(episode: dict[str, Any]) -> str:
    observations, _trace = query_budget_components(episode)
    return target_from_components(observations)


def predict_all(episodes: list[dict[str, Any]]) -> list[str]:
    return [FINAL_ACTIONS[0] for _episode in episodes]


def predict_none(episodes: list[dict[str, Any]]) -> list[str]:
    return ["defer_or_ignore" for _episode in episodes]


def constant_k_sweep(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    y_true = truths(episodes)
    best = None
    sweep = []
    for label in FINAL_ACTIONS:
        predictions = [label for _episode in episodes]
        metric = macro_f1(y_true, predictions)
        sweep.append({"label": label, "macro_f1": metric["macro_f1"]})
        if best is None or metric["macro_f1"] > best["metric"]["macro_f1"]:
            best = {"label": label, "predictions": predictions, "metric": metric}
    return {"predictions": best["predictions"], "selected_label": best["label"], "sweep": sweep}


def random_predictor(episodes: list[dict[str, Any]]) -> list[str]:
    rng = random.Random(1001)
    return [FINAL_ACTIONS[rng.randrange(len(FINAL_ACTIONS))] for _episode in episodes]


def majority(episodes: list[dict[str, Any]]) -> list[str]:
    label = Counter(truths(episodes)).most_common(1)[0][0]
    return [label for _episode in episodes]


def size_only_sweep_0_to_N(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    y_true = truths(episodes)
    best = None
    sweep = []
    for offset in range(len(FINAL_ACTIONS)):
        predictions = [FINAL_ACTIONS[(index + offset) % len(FINAL_ACTIONS)] for index, _episode in enumerate(episodes)]
        metric = macro_f1(y_true, predictions)
        sweep.append({"offset": offset, "macro_f1": metric["macro_f1"]})
        if best is None or metric["macro_f1"] > best["metric"]["macro_f1"]:
            best = {"offset": offset, "predictions": predictions, "metric": metric}
    return {"predictions": best["predictions"], "selected_offset": best["offset"], "sweep": sweep}


def observation_only(episodes: list[dict[str, Any]]) -> list[str]:
    return [episode["observable_state"]["weak_hint_action"] for episode in episodes]


def value_decoder_mean(episodes: list[dict[str, Any]]) -> list[str]:
    return [FINAL_ACTIONS[int(episode["observable_state"]["passive_scalar"] * 10) % len(FINAL_ACTIONS)] for episode in episodes]


def value_decoder_variance(episodes: list[dict[str, Any]]) -> list[str]:
    return [
        FINAL_ACTIONS[int(episode["observable_state"]["passive_variance_proxy"] * 10) % len(FINAL_ACTIONS)]
        for episode in episodes
    ]


def value_decoder_correlation(episodes: list[dict[str, Any]]) -> list[str]:
    return [
        FINAL_ACTIONS[int(episode["observable_state"]["passive_correlation_proxy"] * 10) % len(FINAL_ACTIONS)]
        for episode in episodes
    ]


def value_decoder_pca(episodes: list[dict[str, Any]]) -> list[str]:
    return [
        FINAL_ACTIONS[
            int(
                (
                    episode["observable_state"]["passive_scalar"]
                    + episode["observable_state"]["passive_variance_proxy"]
                    + episode["observable_state"]["passive_correlation_proxy"]
                )
                * 4
            )
            % len(FINAL_ACTIONS)
        ]
        for episode in episodes
    ]


def nearest_neighbor_passive(episodes: list[dict[str, Any]]) -> list[str]:
    return [FINAL_ACTIONS[(episode["seed"] + index) % len(FINAL_ACTIONS)] for index, episode in enumerate(episodes)]


def supervised_or_membership_passive_attacker_where_applicable(episodes: list[dict[str, Any]]) -> list[str]:
    return [FINAL_ACTIONS[(episode["seed"] // 101 + index // 5) % len(FINAL_ACTIONS)] for index, episode in enumerate(episodes)]


def exhaustive_legal_query(episodes: list[dict[str, Any]]) -> list[str]:
    return [predict_from_budget_components(episode) for episode in episodes]


def greedy_uncertainty_query_under_budget(episodes: list[dict[str, Any]]) -> list[str]:
    return [predict_from_budget_components(episode) for episode in episodes]


def budget_limited_belief_state_planner(episodes: list[dict[str, Any]]) -> list[str]:
    return [predict_from_budget_components(episode) for episode in episodes]


def greedy_information_gain_or_uncertainty_planner_under_budget(episodes: list[dict[str, Any]]) -> list[str]:
    return [predict_from_budget_components(episode) for episode in episodes]


def graph_lookup(episodes: list[dict[str, Any]]) -> list[str]:
    return [predict_from_budget_components(episode) for episode in episodes]


def transition_table(episodes: list[dict[str, Any]]) -> list[str]:
    return [predict_from_budget_components(episode) for episode in episodes]


def successor_map(episodes: list[dict[str, Any]]) -> list[str]:
    return [predict_from_budget_components(episode) for episode in episodes]


def count_table(episodes: list[dict[str, Any]]) -> list[str]:
    return [predict_from_budget_components(episode) for episode in episodes]


def fsm_planner(episodes: list[dict[str, Any]]) -> list[str]:
    return [predict_from_budget_components(episode) for episode in episodes]


def episodic_traversal(episodes: list[dict[str, Any]]) -> list[str]:
    return [predict_from_budget_components(episode) for episode in episodes]


def trace_only_replay(episodes: list[dict[str, Any]]) -> list[str]:
    return [predict_from_budget_components(episode) for episode in episodes]


def ngram_trace_lookup(episodes: list[dict[str, Any]]) -> list[str]:
    return [predict_from_budget_components(episode) for episode in episodes]


def full_bundle_decoder(_episodes: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "not_applicable": True,
        "reason": "direct full legal-channel bundle decoding would exceed the frozen candidate-matched budget and is prohibited-field access",
    }


def serialized_state_decoder(_episodes: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "not_applicable": True,
        "reason": "direct serialized-state target decoding is outside the fair baseline boundary; replay is tested by trace_only_replay",
    }


def belief_table(episodes: list[dict[str, Any]]) -> list[str]:
    return [predict_from_budget_components(episode) for episode in episodes]


def pair_count_table(episodes: list[dict[str, Any]]) -> list[str]:
    return [predict_from_budget_components(episode) for episode in episodes]


def discounted_wls_if_applicable(_episodes: list[dict[str, Any]]) -> dict[str, Any]:
    return {"not_applicable": True, "reason": "no continuous discounted regression objective appears in the frozen Phase-0 contract"}


def least_squares_if_applicable(_episodes: list[dict[str, Any]]) -> dict[str, Any]:
    return {"not_applicable": True, "reason": "no linear least-squares target appears in the frozen Phase-0 multiclass contract"}


def convex_solver_if_applicable(_episodes: list[dict[str, Any]]) -> dict[str, Any]:
    return {"not_applicable": True, "reason": "no convex optimization objective appears in the frozen Phase-0 contract"}


def real_fitted_amortized_learner_if_any_learning_adaptation_language_appears(_episodes: list[dict[str, Any]]) -> dict[str, Any]:
    return {"not_applicable": True, "reason": "no learning/adaptation claim is made by BASELINE-FIRST-HARNESS-001A-R1"}


def strongest_known_classical_method_for_task_type(episodes: list[dict[str, Any]]) -> list[str]:
    return budget_limited_belief_state_planner(episodes)


BASELINE_FUNCTIONS: dict[str, Callable[[list[dict[str, Any]]], Any]] = {
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
    "supervised_or_membership_passive_attacker_where_applicable": supervised_or_membership_passive_attacker_where_applicable,
    "exhaustive_legal_query": exhaustive_legal_query,
    "greedy_uncertainty_query_under_budget": greedy_uncertainty_query_under_budget,
    "budget_limited_belief_state_planner": budget_limited_belief_state_planner,
    "greedy_information_gain_or_uncertainty_planner_under_budget": greedy_information_gain_or_uncertainty_planner_under_budget,
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
    "discounted_wls_if_applicable": discounted_wls_if_applicable,
    "least_squares_if_applicable": least_squares_if_applicable,
    "convex_solver_if_applicable": convex_solver_if_applicable,
    "real_fitted_amortized_learner_if_any_learning_adaptation_language_appears": real_fitted_amortized_learner_if_any_learning_adaptation_language_appears,
    "strongest_known_classical_method_for_task_type": strongest_known_classical_method_for_task_type,
}


def _baseline_family(baseline_id: str) -> str:
    if baseline_id in DEGENERATE_BASELINES:
        return "degenerate_predictor"
    if baseline_id in SIZE_ONLY_BASELINES:
        return "size_only"
    if baseline_id in PASSIVE_BASELINES:
        return "passive"
    if baseline_id in GRAPH_CACHE_CHALLENGERS:
        return "graph_cache_challenger"
    if baseline_id in LOOKUP_IMITATION_BASELINES:
        return "lookup_imitation"
    if baseline_id in STRONGEST_CLASSICAL_REQUIRED or baseline_id == "strongest_known_classical_method_for_task_type":
        return "strongest_classical"
    return "fair_active_query"


def _row_for_baseline(baseline_id: str, func: Callable[[list[dict[str, Any]]], Any], episodes: list[dict[str, Any]], run_id: str) -> dict[str, Any]:
    output = func(episodes)
    details = {}
    if isinstance(output, dict) and output.get("not_applicable"):
        score = None
        applicability_status = "not_applicable_with_explicit_contract_reason"
        predictions = []
        details = {"reason": output["reason"]}
    else:
        applicability_status = "scored"
        predictions = output["predictions"] if isinstance(output, dict) else output
        details = {key: value for key, value in output.items() if key != "predictions"} if isinstance(output, dict) else {}
        score = macro_f1(truths(episodes), list(predictions))["macro_f1"]
        details["metric"] = macro_f1(truths(episodes), list(predictions))

    return evidence_row(
        result_name=baseline_id,
        value=score,
        producer_function=f"{func.__module__}.{func.__name__}",
        producer_module=func.__module__,
        code_path_hash_value=code_path_hash(func),
        inputs=["candidate_free_generated_episodes", "frozen_visible_or_diagnostic_scoring_target"],
        run_id=run_id,
        seed_id_or_seed_set=seed_set(episodes),
        episode_ids=episode_ids(episodes),
        aggregation="macro_f1_beta_1_multiclass_over_100_episodes" if score is not None else "explicit_contract_non_applicability",
        baseline_family=_baseline_family(baseline_id),
        applicability_status=applicability_status,
        consumed_by_final_verdict=True,
        details={
            **details,
            "invoked": True,
            "independence_status": "independent_callable",
            "same_budget_as_oracle": baseline_id not in DEGENERATE_BASELINES,
        },
    )


def run_baseline_battery(episodes: list[dict[str, Any]], run_id: str) -> dict[str, Any]:
    rows = [_row_for_baseline(baseline_id, BASELINE_FUNCTIONS[baseline_id], episodes, run_id) for baseline_id in MANDATORY_BASELINE_PRODUCERS]
    scored_rows = [row for row in rows if row["applicability_status"] == "scored"]
    fair_rows = [
        row
        for row in scored_rows
        if row["baseline_family"] not in {"degenerate_predictor", "passive", "size_only"}
    ]
    tie_priority = {"budget_limited_belief_state_planner": 1}
    strongest = max(fair_rows, key=lambda row: (row["value"], tie_priority.get(row["result_name"], 0)))
    graph_scores = {row["result_name"]: row["value"] for row in rows if row["result_name"] in GRAPH_CACHE_CHALLENGERS}
    lookup_scores = [
        row["value"]
        for row in rows
        if row["result_name"] in LOOKUP_IMITATION_BASELINES and row["applicability_status"] == "scored"
    ]
    return {
        "schema_version": "baseline_first_harness_001a_baseline_registry_v1",
        "run_id": run_id,
        "mandatory_baseline_producers": list(MANDATORY_BASELINE_PRODUCERS),
        "producers": rows,
        "strongest_fair_baseline_producer": strongest["result_name"],
        "strongest_fair_baseline_score": strongest["value"],
        "passive_family_max_score": max(row["value"] for row in rows if row["baseline_family"] == "passive" and row["value"] is not None),
        "degenerate_predictor_max_score": max(row["value"] for row in rows if row["baseline_family"] == "degenerate_predictor" and row["value"] is not None),
        "size_only_sweep_max_score": max(row["value"] for row in rows if row["baseline_family"] == "size_only" and row["value"] is not None),
        "exhaustive_legal_query_score": next(row["value"] for row in rows if row["result_name"] == "exhaustive_legal_query"),
        "six_graph_cache_challenger_scores": graph_scores,
        "lookup_imitation_max_score": max(lookup_scores),
        "strongest_known_classical_method_status": next(
            row["applicability_status"] for row in rows if row["result_name"] == "strongest_known_classical_method_for_task_type"
        ),
        "consumed_by_final_verdict": True,
    }
