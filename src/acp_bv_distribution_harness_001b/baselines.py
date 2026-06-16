from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
from itertools import product
from math import inf
from pathlib import Path
from typing import Any, Callable

from . import classify_b3_delta, episode_ids, provenance_for
from . import generator


PredictionFn = Callable[[list[dict[str, Any]], list[dict[str, Any]]], list[dict[str, Any]]]


def score_outputs(episodes: list[dict[str, Any]], outputs: list[dict[str, Any]]) -> float:
    total = 0
    correct = 0
    by_episode = {row["episode_id"]: row for row in outputs}
    for episode in episodes:
        output = by_episode[episode["episode_id"]]
        expected = episode["truth_by_action"][output["action"]]
        total += 1
        correct += int(output["prediction"] == expected)
        for action, prediction in output.get("counterfactual_predictions", {}).items():
            total += 1
            correct += int(prediction == episode["truth_by_action"][action])
    return round(correct / total, 6) if total else 0.0


def _truth_tuple(value: dict[str, int]) -> tuple[int, int]:
    return int(value["boundary_state"]), int(value["viability_state"])


def _from_tuple(value: tuple[int, int]) -> dict[str, int]:
    return {"boundary_state": int(value[0]), "viability_state": int(value[1])}


def _majority(train: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(_truth_tuple(episode["truth_by_action"][episode["chosen_action"]]) for episode in train)
    if not counts:
        return {"boundary_state": 0, "viability_state": 0}
    return _from_tuple(counts.most_common(1)[0][0])


def _row(episode: dict[str, Any], predictor: Callable[[dict[str, Any], str], dict[str, int]]) -> dict[str, Any]:
    action = episode["chosen_action"]
    return {
        "seed": episode["seed"],
        "context_id": episode["context_id"],
        "episode_id": episode["episode_id"],
        "action": action,
        "prediction": predictor(episode, action),
        "counterfactual_predictions": {
            counterfactual: predictor(episode, counterfactual)
            for counterfactual in episode["counterfactual_actions"]
        },
    }


def _rows(episodes: list[dict[str, Any]], predictor: Callable[[dict[str, Any], str], dict[str, int]]) -> list[dict[str, Any]]:
    return [_row(episode, predictor) for episode in episodes]


def _key(episode: dict[str, Any], action: str, fields: tuple[str, ...]) -> tuple[Any, ...]:
    observation = episode["observation"]
    return tuple([observation[field] for field in fields] + [action])


def _lookup(train: list[dict[str, Any]], fields: tuple[str, ...]) -> tuple[dict[tuple[Any, ...], dict[str, int]], dict[str, int]]:
    table: dict[tuple[Any, ...], dict[str, int]] = {}
    fallback = _majority(train)
    for episode in train:
        action = episode["chosen_action"]
        table[_key(episode, action, fields)] = episode["truth_by_action"][action]
    return table, fallback


def full_access_lookup_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    table, fallback = _lookup(train, ("signal_code", "topology_code", "risk_code", "phase_code"))
    return _rows(heldout, lambda episode, action: table.get(_key(episode, action, ("signal_code", "topology_code", "risk_code", "phase_code")), fallback))


def exact_key_memory_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return full_access_lookup_baseline(train, heldout)


def factorized_lookup_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    table, fallback = _lookup(train, ("signal_code", "risk_code"))
    return _rows(heldout, lambda episode, action: table.get(_key(episode, action, ("signal_code", "risk_code")), fallback))


def per_component_lookup_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fallback = _majority(train)
    boundary_by_signal: dict[tuple[int, str], int] = {}
    viability_by_risk: dict[tuple[int, str], int] = {}
    for episode in train:
        obs = episode["observation"]
        action = episode["chosen_action"]
        truth = episode["truth_by_action"][action]
        boundary_by_signal[(obs["signal_code"], action)] = truth["boundary_state"]
        viability_by_risk[(obs["risk_code"], action)] = truth["viability_state"]
    return _rows(
        heldout,
        lambda episode, action: {
            "boundary_state": boundary_by_signal.get((episode["observation"]["signal_code"], action), fallback["boundary_state"]),
            "viability_state": viability_by_risk.get((episode["observation"]["risk_code"], action), fallback["viability_state"]),
        },
    )


def partial_key_lookup_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    table, fallback = _lookup(train, ("topology_code", "phase_code"))
    return _rows(heldout, lambda episode, action: table.get(_key(episode, action, ("topology_code", "phase_code")), fallback))


def topology_only_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    table, fallback = _lookup(train, ("topology_code",))
    return _rows(heldout, lambda episode, action: table.get(_key(episode, action, ("topology_code",)), fallback))


def risk_only_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    table, fallback = _lookup(train, ("risk_code",))
    return _rows(heldout, lambda episode, action: table.get(_key(episode, action, ("risk_code",)), fallback))


def signal_action_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    table, fallback = _lookup(train, ("signal_code",))
    return _rows(heldout, lambda episode, action: table.get(_key(episode, action, ("signal_code",)), fallback))


def _distance(left: dict[str, Any], right: dict[str, Any]) -> int:
    return sum(
        abs(int(left[key]) - int(right[key]))
        for key in ("signal_code", "topology_code", "risk_code", "phase_code")
    )


def action_conditioned_nearest_neighbor_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fallback = _majority(train)

    def predict(episode: dict[str, Any], action: str) -> dict[str, int]:
        best_distance = inf
        best_truth = fallback
        for train_episode in train:
            if train_episode["chosen_action"] != action:
                continue
            distance = _distance(episode["observation"], train_episode["observation"])
            if distance < best_distance:
                best_distance = distance
                best_truth = train_episode["truth_by_action"][action]
        return best_truth

    return _rows(heldout, predict)


def transition_table_graph_cache_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return partial_key_lookup_baseline(train, heldout)


def successor_map_graph_cache_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return topology_only_baseline(train, heldout)


def count_table_graph_cache_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return risk_only_baseline(train, heldout)


def episodic_traversal_graph_cache_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return action_conditioned_nearest_neighbor_baseline(train, heldout)


def fsm_planner_graph_cache_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return factorized_lookup_baseline(train, heldout)


def query_capable_imitation_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return action_conditioned_nearest_neighbor_baseline(train, heldout)


def catch_all_fair_memory_lookup_hook(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return full_access_lookup_baseline(train, heldout)


def _feature_row(episode: dict[str, Any], action: str, modulus: int) -> tuple[int, ...]:
    observation = episode["observation"]
    return (
        1,
        int(observation["signal_code"]) % modulus,
        int(observation["topology_code"]) % modulus,
        int(observation["risk_code"]) % modulus,
        int(observation["phase_code"]) % modulus,
        1 if action == "shield" else 0,
        1 if action == "repair" else 0,
        1 if action == "defer" else 0,
    )


def _mod_inverse(value: int, modulus: int) -> int:
    return pow(value % modulus, -1, modulus)


def _solve_modular_system(rows: list[tuple[tuple[int, ...], int]], modulus: int, variable_count: int) -> tuple[int, ...] | None:
    matrix = [[*features, target % modulus] for features, target in rows]
    pivot_row = 0
    pivots: list[int] = []
    for column in range(variable_count):
        pivot = None
        for row_index in range(pivot_row, len(matrix)):
            if matrix[row_index][column] % modulus:
                pivot = row_index
                break
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        inverse = _mod_inverse(matrix[pivot_row][column], modulus)
        matrix[pivot_row] = [(value * inverse) % modulus for value in matrix[pivot_row]]
        for row_index in range(len(matrix)):
            if row_index == pivot_row:
                continue
            factor = matrix[row_index][column] % modulus
            if factor:
                matrix[row_index] = [
                    (value - factor * pivot_value) % modulus
                    for value, pivot_value in zip(matrix[row_index], matrix[pivot_row])
                ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    for row in matrix:
        if all(value % modulus == 0 for value in row[:variable_count]) and row[-1] % modulus:
            return None
    solution = [0] * variable_count
    for row_index, column in enumerate(pivots):
        solution[column] = matrix[row_index][-1] % modulus
    return tuple(solution)


def _train_signature(train: list[dict[str, Any]]) -> tuple[tuple[int, int, int, int, str, int, int], ...]:
    rows = []
    for episode in train:
        action = episode["chosen_action"]
        truth = episode["truth_by_action"][action]
        observation = episode["observation"]
        rows.append(
            (
                int(observation["signal_code"]),
                int(observation["topology_code"]),
                int(observation["risk_code"]),
                int(observation["phase_code"]),
                str(action),
                int(truth["boundary_state"]),
                int(truth["viability_state"]),
            )
        )
    return tuple(rows)


def _fit_boundary(rows: tuple[tuple[int, int, int, int, str, int, int], ...]) -> dict[str, Any] | None:
    equations = []
    for signal, topology, risk, phase, action, boundary, _viability in rows:
        episode = {"observation": {"signal_code": signal, "topology_code": topology, "risk_code": risk, "phase_code": phase}}
        equations.append((_feature_row(episode, action, 7), boundary))
    solution = _solve_modular_system(equations, 7, 8)
    if solution is None:
        return None
    return {
        "modulus": 7,
        "intercept": solution[0],
        "weights": {
            "signal_code": solution[1],
            "topology_code": solution[2],
            "risk_code": solution[3],
            "phase_code": solution[4],
        },
        "action_deltas": {
            "probe": 0,
            "shield": solution[5],
            "repair": solution[6],
            "defer": solution[7],
        },
    }


def _score_viability_coefficients(
    rows: tuple[tuple[int, int, int, int, str, int, int], ...],
    coefficients: tuple[int, ...],
    action_deltas: dict[str, int],
) -> tuple[int, int, tuple[int, ...]]:
    counts = [[0, 0] for _ in range(5)]
    for signal, topology, risk, phase, action, _boundary, viability in rows:
        features = (1, signal % 5, topology % 5, risk % 5, phase % 5)
        residue = (
            sum(feature * coefficient for feature, coefficient in zip(features, coefficients))
            + action_deltas[action]
        ) % 5
        counts[residue][int(viability)] += 1
    correct = sum(max(row) for row in counts)
    margin = sum(abs(row[1] - row[0]) for row in counts)
    positives = tuple(index for index, row in enumerate(counts) if row[1] > row[0])
    return correct, margin, positives


@lru_cache(maxsize=64)
def _fit_parametric_state_from_signature(rows: tuple[tuple[int, int, int, int, str, int, int], ...]) -> dict[str, Any]:
    if not rows:
        return {
            "model_id": "parametric_modular_linear_baseline_empty_degenerate",
            "degenerate": True,
            "fallback": {"boundary_state": 0, "viability_state": 0},
            "training_episode_count": 0,
        }
    boundary = _fit_boundary(rows)
    boundary_action_deltas = (
        {action: int(delta) % 5 for action, delta in boundary["action_deltas"].items()}
        if boundary is not None
        else {action: 0 for action in generator.ACTIONS}
    )
    best_coefficients: tuple[int, ...] | None = None
    best_positives: tuple[int, ...] = ()
    best_key: tuple[int, int, int, tuple[int, ...]] | None = None
    for coefficients in product(range(5), repeat=5):
        correct, margin, positives = _score_viability_coefficients(rows, coefficients, boundary_action_deltas)
        key = (correct, margin, -sum(coefficients), tuple(-value for value in coefficients))
        if best_key is None or key > best_key:
            best_key = key
            best_coefficients = coefficients
            best_positives = positives
    if boundary is None or best_coefficients is None:
        return {
            "model_id": "parametric_modular_linear_baseline_degenerate_unsolved",
            "degenerate": True,
            "fallback": _from_tuple(Counter((row[5], row[6]) for row in rows).most_common(1)[0][0]),
            "training_episode_count": len(rows),
        }
    return {
        "model_id": "parametric_modular_linear_baseline",
        "degenerate": False,
        "training_episode_count": len(rows),
        "boundary_model": boundary,
        "viability_model": {
            "modulus": 5,
            "intercept": best_coefficients[0],
            "weights": {
                "signal_code": best_coefficients[1],
                "topology_code": best_coefficients[2],
                "risk_code": best_coefficients[3],
                "phase_code": best_coefficients[4],
            },
            "action_deltas": boundary_action_deltas,
            "positive_residues": list(best_positives),
        },
    }


def fit_parametric_modular_linear_model(train: list[dict[str, Any]]) -> dict[str, Any]:
    return _fit_parametric_state_from_signature(_train_signature(train))


def predict_parametric_modular_linear(state: dict[str, Any], observation: dict[str, Any], action: str) -> dict[str, int]:
    if state.get("degenerate"):
        return dict(state["fallback"])
    boundary_state = state["boundary_model"]
    viability_state = state["viability_model"]
    boundary_raw = boundary_state["intercept"] + boundary_state["action_deltas"][action]
    viability_raw = viability_state["intercept"] + viability_state["action_deltas"][action]
    for key, weight in boundary_state["weights"].items():
        boundary_raw += int(observation[key]) * int(weight)
    for key, weight in viability_state["weights"].items():
        viability_raw += int(observation[key]) * int(weight)
    viability_mod = viability_raw % viability_state["modulus"]
    return {
        "boundary_state": boundary_raw % boundary_state["modulus"],
        "viability_state": 1 if viability_mod in set(viability_state["positive_residues"]) else 0,
    }


def parametric_modular_linear_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    state = fit_parametric_modular_linear_model(train)
    return _rows(heldout, lambda episode, action: predict_parametric_modular_linear(state, episode["observation"], action))


BASELINE_FUNCTIONS: dict[str, PredictionFn] = {
    "parametric_modular_linear_baseline": parametric_modular_linear_baseline,
    "full_access_lookup_baseline": full_access_lookup_baseline,
    "exact_key_memory_baseline": exact_key_memory_baseline,
    "factorized_lookup_baseline": factorized_lookup_baseline,
    "per_component_lookup_baseline": per_component_lookup_baseline,
    "partial_key_lookup_baseline": partial_key_lookup_baseline,
    "topology_only_baseline": topology_only_baseline,
    "risk_only_baseline": risk_only_baseline,
    "signal_action_baseline": signal_action_baseline,
    "action_conditioned_nearest_neighbor_baseline": action_conditioned_nearest_neighbor_baseline,
    "transition_table_graph_cache_baseline": transition_table_graph_cache_baseline,
    "successor_map_graph_cache_baseline": successor_map_graph_cache_baseline,
    "count_table_graph_cache_baseline": count_table_graph_cache_baseline,
    "episodic_traversal_graph_cache_baseline": episodic_traversal_graph_cache_baseline,
    "fsm_planner_graph_cache_baseline": fsm_planner_graph_cache_baseline,
    "query_capable_imitation_baseline": query_capable_imitation_baseline,
    "catch_all_fair_memory_lookup_hook": catch_all_fair_memory_lookup_hook,
}


def run_baseline_matrix(
    *,
    datasets: list[dict[str, Any]],
    candidate_scores_by_seed: dict[int, float],
    run_id: str,
    output_artifact_path: Path,
) -> dict[str, Any]:
    aggregate: dict[str, list[float]] = defaultdict(list)
    per_seed_rows = []
    output_samples: dict[str, list[dict[str, Any]]] = {}
    for dataset in datasets:
        seed = int(dataset["seed"])
        seed_rows = []
        for baseline_id, baseline_fn in BASELINE_FUNCTIONS.items():
            outputs = baseline_fn(dataset["train"], dataset["heldout"])
            score = score_outputs(dataset["heldout"], outputs)
            aggregate[baseline_id].append(score)
            output_samples.setdefault(baseline_id, outputs[:5])
            delta = round(candidate_scores_by_seed[seed] - score, 6)
            seed_rows.append(
                {
                    "baseline_id": baseline_id,
                    "score": score,
                    "candidate_score": candidate_scores_by_seed[seed],
                    "delta": delta,
                    "b3_classification": classify_b3_delta(delta),
                    "provenance": provenance_for(
                        baseline_fn,
                        inputs={"seed": seed, "heldout_count": len(dataset["heldout"])},
                        run_id=f"{run_id}-{seed}-{baseline_id}",
                        seed=seed,
                        context_episode_ids=episode_ids(dataset["heldout"]),
                        aggregation_method="mean_exact_prediction_and_counterfactual_accuracy",
                        output_artifact_path=output_artifact_path,
                    ),
                }
            )
        per_seed_rows.append({"seed": seed, "baselines": seed_rows})
    rows = []
    for baseline_id, scores in aggregate.items():
        score = round(sum(scores) / len(scores), 6)
        candidate_score = round(sum(candidate_scores_by_seed.values()) / len(candidate_scores_by_seed), 6)
        delta = round(candidate_score - score, 6)
        baseline_fn = BASELINE_FUNCTIONS[baseline_id]
        rows.append(
            {
                "baseline_id": baseline_id,
                "score": score,
                "candidate_score": candidate_score,
                "delta": delta,
                "b3_classification": classify_b3_delta(delta),
                "provenance": provenance_for(
                    baseline_fn,
                    inputs={"seed_count": len(datasets), "baseline_id": baseline_id},
                    run_id=f"{run_id}-aggregate-{baseline_id}",
                    seed="multi_seed",
                    context_episode_ids=[str(dataset["seed"]) for dataset in datasets],
                    aggregation_method="mean_over_seed_scores",
                    output_artifact_path=output_artifact_path,
                ),
            }
        )
    strongest = max(rows, key=lambda row: (row["score"], row["baseline_id"]))
    factorized_rows = [row for row in rows if row["baseline_id"] == "factorized_lookup_baseline"]
    factorized_equivalent = any(row["b3_classification"] == "baseline_equivalent" for row in factorized_rows)
    return {
        "producer_function": "run_baseline_matrix",
        "baselines": rows,
        "per_seed": per_seed_rows,
        "baseline_output_samples": output_samples,
        "strongest_baseline": strongest,
        "strongest_baseline_selection_rule": "deterministic_argmax_score_preserve_most_damaging_tie",
        "blocked_by_baseline_equivalence": strongest["b3_classification"] == "baseline_equivalent",
        "blocked_by_factorized_lookup_equivalence": factorized_equivalent,
        "thresholds": {
            "equivalence_abs_delta_lte": 0.02,
            "mechanism_relevant_effect_delta_gte": 0.05,
        },
        "all_required_baselines_ran": set(BASELINE_FUNCTIONS) == {row["baseline_id"] for row in rows},
    }


def _axis_key(episode: dict[str, Any], fields: tuple[str, ...], action: str) -> tuple[Any, ...]:
    observation = episode["observation"]
    return tuple(observation[field] for field in fields) + (action,)


def _axis_scan(dataset: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    train_keys = {
        _axis_key(episode, fields, action)
        for episode in dataset["train"]
        for action in generator.ACTIONS
    }
    heldout_keys = [
        _axis_key(episode, fields, episode["chosen_action"])
        for episode in dataset["heldout"]
    ]
    complete_count = sum(1 for key in heldout_keys if key in train_keys)
    ratio = round(complete_count / len(heldout_keys), 6) if heldout_keys else 1.0
    return {
        "fields": list(fields),
        "lookup_complete_heldout_count": complete_count,
        "heldout_count": len(heldout_keys),
        "lookup_complete_heldout_ratio": ratio,
        "lookup_complete": ratio > 0.75,
    }


def _prediction_agreement(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> float:
    if not left:
        return 0.0
    by_episode = {row["episode_id"]: row for row in right}
    matches = 0
    total = 0
    for row in left:
        other = by_episode[row["episode_id"]]
        total += 1
        matches += int(row["prediction"] == other["prediction"])
        for action, prediction in row.get("counterfactual_predictions", {}).items():
            total += 1
            matches += int(prediction == other.get("counterfactual_predictions", {}).get(action))
    return round(matches / total, 6) if total else 0.0


def factorization_report(
    datasets: list[dict[str, Any]],
    candidate_outputs_by_seed: dict[int, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    manifests = [generator.distribution_manifest(dataset) for dataset in datasets]
    single_axis = []
    pair_axis = []
    fields = tuple(family["observation_key"] for family in generator.FACTOR_FAMILIES.values())
    for dataset in datasets:
        seed = int(dataset["seed"])
        for field in fields:
            row = _axis_scan(dataset, (field,))
            row["seed"] = seed
            single_axis.append(row)
        for left_index, left in enumerate(fields):
            for right in fields[left_index + 1 :]:
                row = _axis_scan(dataset, (left, right))
                row["seed"] = seed
                pair_axis.append(row)
    candidate_agreements = []
    if candidate_outputs_by_seed:
        for dataset in datasets:
            seed = int(dataset["seed"])
            factorized_outputs = factorized_lookup_baseline(dataset["train"], dataset["heldout"])
            candidate_outputs = candidate_outputs_by_seed[seed]
            candidate_agreements.append(
                {
                    "seed": seed,
                    "candidate_vs_factorized_agreement": _prediction_agreement(candidate_outputs, factorized_outputs),
                }
            )
    lookup_complete = any(row["lookup_complete_heldout_ratio"] > 0.75 for row in manifests)
    undeclared_axis = any(row["lookup_complete"] for row in single_axis + pair_axis)
    factorized_agreement = any(
        row["candidate_vs_factorized_agreement"] >= 0.98
        for row in candidate_agreements
    )
    blocked = lookup_complete or undeclared_axis or factorized_agreement
    return {
        "producer_function": "factorization_report",
        "predeclared_factorization_families": sorted(generator.FACTOR_FAMILIES),
        "single_axis_scans": single_axis,
        "pair_axis_scans": pair_axis,
        "candidate_vs_factorized_agreement_by_seed": candidate_agreements,
        "no_undeclared_lookup_complete_axis_detected": not undeclared_axis,
        "lookup_complete_heldout_ratio_by_seed": {
            row["seed"]: row["lookup_complete_heldout_ratio"] for row in manifests
        },
        "blocked_by_factorized_lookup_equivalence": blocked,
        "blocking_reasons": {
            "lookup_complete_distribution": lookup_complete,
            "undeclared_lookup_complete_axis": undeclared_axis,
            "candidate_factorized_agreement": factorized_agreement,
        },
    }
