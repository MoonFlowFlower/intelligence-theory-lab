from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from . import code_path_hash, sha256_json, source_path_for
from . import generator


PredictFn = Callable[[dict[str, Any], dict[str, Any], str], dict[str, int]]
FitFn = Callable[[list[dict[str, Any]]], dict[str, Any]]
TruthFn = Callable[[dict[str, Any], str], dict[str, int]]

THETA_COUPLE = 1.0


def _probe_episode(*, seed: int, split: str, index: int, signal: int, topology: int, risk: int, phase: int) -> dict[str, Any]:
    observation = {
        "signal_code": signal,
        "topology_code": topology,
        "risk_code": risk,
        "phase_code": phase,
        "available_actions": list(generator.ACTIONS),
    }
    return {
        "seed": seed,
        "split": split,
        "context_id": f"{split}.coupling.ctx.{seed}.{index:04d}",
        "episode_id": f"{split}.coupling.ep.{seed}.{index:04d}",
        "observation": observation,
        "chosen_action": generator.ACTIONS[index % len(generator.ACTIONS)],
        "counterfactual_actions": [action for action in generator.ACTIONS if action != generator.ACTIONS[index % len(generator.ACTIONS)]],
    }


def _probe_grid(seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    seen = []
    extrapolation = []
    index = 0
    for signal in range(0, 6):
        for topology in range(0, 4):
            for risk in range(0, 5):
                for phase in range(0, 3):
                    seen.append(
                        _probe_episode(
                            seed=seed,
                            split="seen",
                            index=index,
                            signal=signal,
                            topology=topology,
                            risk=risk,
                            phase=phase,
                        )
                    )
                    index += 1
    for signal in range(6, 10):
        for topology in range(4, 6):
            for risk in range(5, 8):
                for phase in range(3, 5):
                    extrapolation.append(
                        _probe_episode(
                            seed=seed,
                            split="extrapolation",
                            index=index,
                            signal=signal,
                            topology=topology,
                            risk=risk,
                            phase=phase,
                        )
                    )
                    index += 1
    return seen, extrapolation


def _prediction_vector(predict_fn: PredictFn, state: dict[str, Any], episodes: list[dict[str, Any]]) -> list[tuple[int, int]]:
    vector = []
    for episode in episodes:
        for action in generator.ACTIONS:
            predicted = predict_fn(state, episode["observation"], action)
            vector.append((int(predicted["boundary_state"]), int(predicted["viability_state"])))
    return vector


def _truth_vector(truth_fn: TruthFn, episodes: list[dict[str, Any]]) -> list[tuple[int, int]]:
    vector = []
    for episode in episodes:
        for action in generator.ACTIONS:
            expected = truth_fn(episode, action)
            vector.append((int(expected["boundary_state"]), int(expected["viability_state"])))
    return vector


def _label_permuted_train(train: list[dict[str, Any]]) -> list[dict[str, Any]]:
    permuted = deepcopy(train)
    chosen_labels = [deepcopy(row["truth_by_action"][row["chosen_action"]]) for row in train]
    if chosen_labels:
        chosen_labels = chosen_labels[1:] + chosen_labels[:1]
    for row, replacement in zip(permuted, chosen_labels):
        row["truth_by_action"][row["chosen_action"]] = replacement
    return permuted


def _agreement(left: list[tuple[int, int]], right: list[tuple[int, int]]) -> float:
    if not left:
        return 0.0
    return round(sum(1 for candidate, expected in zip(left, right) if candidate == expected) / len(left), 6)


def _max_abs_divergence(left: list[tuple[int, int]], right: list[tuple[int, int]]) -> int:
    if not left:
        return 0
    return max(
        abs(candidate[0] - expected[0]) + abs(candidate[1] - expected[1])
        for candidate, expected in zip(left, right)
    )


def detect_candidate_truth_coupling(
    *,
    predict_fn: PredictFn,
    fit_fn: FitFn,
    truth_fn: TruthFn,
    datasets: list[dict[str, Any]],
    seed: int,
    tolerance: int = 0,
    run_id: str = "candidate-truth-coupling",
    output_artifact_path: Path | None = None,
) -> dict[str, Any]:
    dataset = next((row for row in datasets if int(row["seed"]) == int(seed)), datasets[0])
    train = dataset["train"]
    seen, extrapolation = _probe_grid(seed)
    probes = seen + extrapolation

    legal_state = fit_fn(train)
    empty_state = fit_fn([])
    permuted_state = fit_fn(_label_permuted_train(train))

    legal_seen = _prediction_vector(predict_fn, legal_state, seen)
    legal_extrapolation = _prediction_vector(predict_fn, legal_state, extrapolation)
    legal_all = legal_seen + legal_extrapolation
    expected_seen = _truth_vector(truth_fn, seen)
    expected_extrapolation = _truth_vector(truth_fn, extrapolation)
    expected_all = expected_seen + expected_extrapolation

    empty_all = _prediction_vector(predict_fn, empty_state, probes)
    permuted_all = _prediction_vector(predict_fn, permuted_state, probes)

    agreement_overall = _agreement(legal_all, expected_all)
    agreement_extrapolation = _agreement(legal_extrapolation, expected_extrapolation)
    invariant = legal_all == empty_all == permuted_all
    oracle_match = agreement_extrapolation >= THETA_COUPLE
    blocked = oracle_match or invariant

    evidence_payload = {
        "seed": seed,
        "tolerance": tolerance,
        "seen_predictions": legal_seen,
        "extrapolation_predictions": legal_extrapolation,
        "expected_seen": expected_seen,
        "expected_extrapolation": expected_extrapolation,
        "empty_predictions": empty_all,
        "permuted_predictions": permuted_all,
    }
    artifact_path = output_artifact_path.as_posix() if output_artifact_path else ""
    return {
        "producer_function": "detect_candidate_truth_coupling",
        "run_id": run_id,
        "seed": seed,
        "tolerance": tolerance,
        "n_probes": len(probes) * len(generator.ACTIONS),
        "probe_grid_spec": {
            "seen_cells": len(seen),
            "extrapolation_cells": len(extrapolation),
            "actions": list(generator.ACTIONS),
        },
        "agreement_rate_overall": agreement_overall,
        "agreement_rate_extrapolation": agreement_extrapolation,
        "max_abs_divergence": _max_abs_divergence(legal_all, expected_all),
        "training_response": {
            "fit_legal_vs_fit_empty_identical": legal_all == empty_all,
            "fit_legal_vs_fit_label_permuted_identical": legal_all == permuted_all,
            "predictions_invariant_to_training": invariant,
        },
        "trigger_A_oracle_match": oracle_match,
        "trigger_B_training_invariance": invariant,
        "verdict": "blocked_by_candidate_truth_coupling" if blocked else "candidate_truth_not_coupled",
        "thresholds": {"theta_couple": THETA_COUPLE},
        "evidence_hash": sha256_json(evidence_payload),
        "source_path": source_path_for(detect_candidate_truth_coupling),
        "code_path_hash": code_path_hash(detect_candidate_truth_coupling),
        "aggregation_method": "exact_prediction_vector_agreement_over_seen_and_extrapolation_probe_grid",
        "output_artifact_path": artifact_path,
    }
