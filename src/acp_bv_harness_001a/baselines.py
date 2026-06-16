from __future__ import annotations

from inspect import getsource
from pathlib import Path
from typing import Any, Callable

from . import environment
from .common import classify_delta, provenance_for, seed_ids, sha256_text, source_hash
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


def observation_action_key(episode: dict[str, Any], action: str) -> tuple[str, int, int, str]:
    observation = episode["observation"]
    return (
        str(observation["signal"]),
        int(observation["topology"]),
        int(observation["risk"]),
        str(action),
    )


def _all_episode_actions(episode: dict[str, Any]) -> list[str]:
    return list(dict.fromkeys([episode["chosen_action"], *episode["harness_selected_counterfactual_actions"]]))


def _full_access_lookup_table(train_episodes: list[dict[str, Any]]) -> dict[tuple[str, int, int, str], dict[str, Any]]:
    table: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for episode in train_episodes:
        for action in _all_episode_actions(episode):
            table[observation_action_key(episode, action)] = environment.held_out_truth_generator(
                episode,
                action,
            )
    return table


def graph_cache_transition_table(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _rows_from_predictor(episodes, lambda episode, action: _partial_truth(episode, action, ignore_topology=True))


def full_access_lookup_baseline(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lookup = _full_access_lookup_table(environment.generate_episodes("train"))
    return _rows_from_predictor(
        episodes,
        lambda episode, action: lookup[observation_action_key(episode, action)],
    )


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
    "full_access_lookup_baseline": full_access_lookup_baseline,
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
    comparison_classification = classify_delta(delta)
    overlap = detect_train_heldout_overlap()
    full_access = next(row for row in rows if row["baseline_id"] == "full_access_lookup_baseline")
    return {
        "producer_function": "run_baseline_matrix",
        "candidate_score": candidate_score,
        "baselines": rows,
        "strongest_baseline": strongest,
        "strongest_baseline_comparison": {
            "candidate_score": candidate_score,
            "baseline_score": strongest["score"],
            "delta": delta,
            "classification": comparison_classification,
        },
        "full_access_lookup_evidence": {
            "train_key_schema": ["signal", "topology", "risk", "action"],
            "heldout_key_schema": ["signal", "topology", "risk", "action"],
            "train_observation_action_key_count": overlap["train_key_count"],
            "heldout_observation_action_key_count": overlap["heldout_key_count"],
            "overlap_count": overlap["overlap_count"],
            "missing_heldout_key_count": overlap["missing_heldout_key_count"],
            "baseline_score": full_access["score"],
            "candidate_score": candidate_score,
            "delta": round(candidate_score - full_access["score"], 6),
            "b3_classification": classify_delta(round(candidate_score - full_access["score"], 6)),
        },
        "train_heldout_overlap": overlap,
        "candidate_truth_coupling": detect_candidate_truth_coupling(),
        "blocked_by_baseline_equivalence": comparison_classification == "baseline_equivalent",
        "thresholds": {
            "equivalence_lt": 0.02,
            "inconclusive_gte": 0.02,
            "inconclusive_lt": 0.05,
            "mechanism_relevant_effect_gte": 0.05,
        },
        "baseline_equivalent_is_pass": False,
        "weak_baseline_only": False,
    }


def _key_set(episodes: list[dict[str, Any]]) -> set[tuple[str, int, int, str]]:
    return {
        observation_action_key(episode, action)
        for episode in episodes
        for action in _all_episode_actions(episode)
    }


def detect_train_heldout_overlap(sample_limit: int = 8) -> dict[str, Any]:
    train_keys = _key_set(environment.generate_episodes("train"))
    heldout_keys = _key_set(environment.generate_episodes("heldout"))
    overlap = train_keys & heldout_keys
    missing = heldout_keys - train_keys
    train_key_payload = sorted(map(repr, train_keys))
    heldout_key_payload = sorted(map(repr, heldout_keys))
    overlap_ratio = round(len(overlap) / len(heldout_keys), 6) if heldout_keys else 0.0
    return {
        "producer_function": "detect_train_heldout_overlap",
        "train_key_schema": ["signal", "topology", "risk", "action"],
        "heldout_key_schema": ["signal", "topology", "risk", "action"],
        "train_key_count": len(train_keys),
        "heldout_key_count": len(heldout_keys),
        "overlap_count": len(overlap),
        "missing_heldout_key_count": len(missing),
        "overlap_ratio": overlap_ratio,
        "train_key_set_hash": sha256_text("\n".join(train_key_payload)),
        "heldout_key_set_hash": sha256_text("\n".join(heldout_key_payload)),
        "overlapping_key_samples": sorted(map(repr, overlap))[:sample_limit],
        "heldout_contains_unseen_keys": bool(missing),
        "memory_lookup_can_be_complete_policy": bool(heldout_keys) and not missing,
    }


def detect_candidate_truth_coupling() -> dict[str, Any]:
    episodes = [*environment.generate_episodes("train"), *environment.generate_episodes("heldout")]
    state = environment.clean_serialized_state()
    mismatches = []
    for episode in episodes:
        for action in _all_episode_actions(episode):
            candidate = environment.reference_candidate_predict(state, episode["observation"], action)
            truth = environment.held_out_truth_generator(episode, action)
            if candidate != truth:
                mismatches.append({"episode_id": episode["episode_id"], "action": action})
    candidate_source = getsource(environment.reference_candidate_predict)
    truth_source = getsource(environment.held_out_truth_generator)
    formula_equivalent = not mismatches
    return {
        "producer_function": "detect_candidate_truth_coupling",
        "candidate_function": "reference_candidate_predict",
        "truth_generator": "held_out_truth_generator",
        "candidate_function_source_hash": source_hash(environment.reference_candidate_predict),
        "truth_generator_source_hash": source_hash(environment.held_out_truth_generator),
        "shared_helper_source_dependency_analysis": {
            "same_module": environment.reference_candidate_predict.__module__
            == environment.held_out_truth_generator.__module__,
            "shared_signal_value_table": "SIGNAL_VALUE" in candidate_source and "SIGNAL_VALUE" in truth_source,
            "shared_action_delta_table": "ACTION_DELTA" in candidate_source and "ACTION_DELTA" in truth_source,
            "episode_action_mismatch_count": len(mismatches),
        },
        "formula_equivalence_detected": formula_equivalent,
        "classification": "oracle_like_reference_candidate_scaffolding_only"
        if formula_equivalent
        else "not_formula_equivalent_by_current_probe",
        "claim_downgrade": "no_candidate_mechanism_relevance_claim_permitted"
        if formula_equivalent
        else "coupling_not_detected_by_current_probe",
    }
