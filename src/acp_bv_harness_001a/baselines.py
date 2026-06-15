from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from . import environment
from .common import classify_delta, provenance_for, seed_ids
from .scoring import score_prediction_rows


def _rows_from_predictor(
    episodes: list[dict[str, Any]],
    predictor: Callable[[dict[str, Any], str], dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for episode in episodes:
        action = episode["chosen_action"]
        rows.append(
            {
                "episode_id": episode["episode_id"],
                "action": action,
                "prediction": predictor(episode, action),
                "counterfactual_predictions": {
                    counterfactual: predictor(episode, counterfactual)
                    for counterfactual in episode["harness_selected_counterfactual_actions"]
                },
            }
        )
    return rows


def _partial_truth(episode: dict[str, Any], action: str, *, ignore_action: bool = False, ignore_topology: bool = False) -> dict[str, Any]:
    observation = dict(episode["observation"])
    if ignore_topology:
        observation["topology"] = 0
    action_to_use = "repair" if ignore_action else action
    proxy_episode = dict(episode)
    proxy_episode["observation"] = observation
    return environment.held_out_truth_generator(proxy_episode, action_to_use)


def graph_cache_transition_table(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _rows_from_predictor(episodes, lambda episode, action: _partial_truth(episode, action, ignore_topology=True))


def graph_cache_successor_map(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _rows_from_predictor(episodes, lambda episode, action: _partial_truth(episode, action, ignore_action=True))


def graph_cache_count_table(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _rows_from_predictor(
        episodes,
        lambda episode, action: {"boundary_delta": 1, "viability_state": 1 if episode["observation"]["risk"] % 2 == 0 else 0},
    )


def episodic_traversal_baseline(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _rows_from_predictor(episodes, lambda episode, action: _partial_truth(episode, action, ignore_topology=True))


def fsm_planner_baseline(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _rows_from_predictor(episodes, lambda episode, action: _partial_truth(episode, action, ignore_topology=True))


def graph_lookup_baseline(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _rows_from_predictor(episodes, lambda episode, action: _partial_truth(episode, action, ignore_action=True))


def observation_only_baseline(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _rows_from_predictor(episodes, lambda episode, action: _partial_truth(episode, action, ignore_action=True))


def action_independent_baseline(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _rows_from_predictor(episodes, lambda episode, action: _partial_truth(episode, "repair"))


def static_action_baseline(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _rows_from_predictor(episodes, lambda episode, action: _partial_truth(episode, "probe"))


def replay_hash_only_baseline(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return []


def candidate_self_consistency_baseline(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return []


def lookup_table_memorization_blocker(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _rows_from_predictor(episodes, lambda episode, action: {"boundary_delta": 0, "viability_state": 0})


BASELINE_FUNCTIONS: dict[str, Callable[[list[dict[str, Any]]], list[dict[str, Any]]]] = {
    "graph_cache_transition_table": graph_cache_transition_table,
    "graph_cache_successor_map": graph_cache_successor_map,
    "graph_cache_count_table": graph_cache_count_table,
    "episodic_traversal_baseline": episodic_traversal_baseline,
    "fsm_planner_baseline": fsm_planner_baseline,
    "graph_lookup_baseline": graph_lookup_baseline,
    "observation_only_baseline": observation_only_baseline,
    "action_independent_baseline": action_independent_baseline,
    "static_action_baseline": static_action_baseline,
    "replay_hash_only_baseline": replay_hash_only_baseline,
    "candidate_self_consistency_baseline": candidate_self_consistency_baseline,
    "lookup_table_memorization_blocker": lookup_table_memorization_blocker,
}


BLOCKING_BASELINES = {
    "replay_hash_only_baseline": "blocked_by_replay_hash_only",
    "candidate_self_consistency_baseline": "blocked_by_candidate_authored_self_consistency",
}


def run_baseline_matrix(
    *,
    repo_root: Path,
    output_artifact_path: Path,
    run_id: str,
    candidate_score: float,
) -> dict[str, Any]:
    episodes = environment.generate_episodes("heldout")
    rows = []
    for baseline_id, baseline_fn in BASELINE_FUNCTIONS.items():
        predictions = baseline_fn(episodes)
        blocked_reason = BLOCKING_BASELINES.get(baseline_id)
        if blocked_reason:
            score = None
            classification = blocked_reason
        else:
            score = score_prediction_rows(episodes, predictions, environment.held_out_truth_generator)
            delta = round(candidate_score - score, 6)
            classification = classify_delta(delta)
            if baseline_id == "lookup_table_memorization_blocker":
                classification = "lookup_memorization_classified"
        rows.append(
            {
                "baseline_id": baseline_id,
                "score": score,
                "classification": classification,
                "blocked_reason": blocked_reason,
                "provenance": provenance_for(
                    baseline_fn,
                    repo_root=repo_root,
                    inputs={"episode_count": len(episodes), "baseline_id": baseline_id},
                    run_id=f"{run_id}-{baseline_id}",
                    seed_context_episode_ids=seed_ids(episodes),
                    aggregation_method="same_scorer_mean_exact_prediction_and_counterfactual_accuracy",
                    output_artifact_path=output_artifact_path,
                ),
            }
        )
    scored = [row for row in rows if row["score"] is not None]
    strongest = max(scored, key=lambda row: row["score"])
    delta = round(candidate_score - strongest["score"], 6)
    return {
        "producer_function": "run_baseline_matrix",
        "candidate_score": candidate_score,
        "baselines": rows,
        "strongest_baseline": strongest,
        "strongest_baseline_comparison": {
            "candidate_score": candidate_score,
            "baseline_score": strongest["score"],
            "delta": delta,
            "classification": classify_delta(delta),
        },
        "thresholds": {
            "equivalence_lt": 0.02,
            "inconclusive_gte": 0.02,
            "inconclusive_lt": 0.05,
            "mechanism_relevant_effect_gte": 0.05,
        },
        "baseline_equivalent_is_pass": False,
        "weak_baseline_only": False,
    }
