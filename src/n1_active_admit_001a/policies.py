from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

import numpy as np

from .env_causal import DIAG_OUTCOME, K_SLOTS, NONDIAG_OUTCOME, CausalStructure, enumerate_structures

PolicyResult = dict[str, Any]
PolicyFn = Callable[[np.ndarray, dict[str, Any], dict[str, int] | None], PolicyResult]


def _structures(allowed_memory: dict[str, Any]) -> list[CausalStructure]:
    return list(allowed_memory.get("structure_family", enumerate_structures()))


def _uniform_belief(structures: list[CausalStructure]) -> dict[int, float]:
    weight = 1.0 / len(structures)
    return {structure.structure_id: weight for structure in structures}


def _belief_from_memory(allowed_memory: dict[str, Any], structures: list[CausalStructure]) -> dict[int, float]:
    raw_belief = allowed_memory.get("belief")
    if raw_belief is None:
        return _uniform_belief(structures)
    belief = {int(k): float(v) for k, v in raw_belief.items()}
    total = sum(max(v, 0.0) for v in belief.values())
    if total <= 0:
        return _uniform_belief(structures)
    return {sid: max(value, 0.0) / total for sid, value in belief.items()}


def _p_outcome_one(structure: CausalStructure, slot: int) -> float:
    if slot == structure.j:
        return DIAG_OUTCOME[structure.m]
    return NONDIAG_OUTCOME


def _likelihood(structure: CausalStructure, slot: int, outcome: int) -> float:
    p_one = _p_outcome_one(structure, slot)
    return p_one if outcome == 1 else 1.0 - p_one


def _posterior(
    structures: list[CausalStructure],
    belief: dict[int, float],
    slot: int,
    outcome: int,
) -> dict[int, float]:
    weights = {
        structure.structure_id: belief.get(structure.structure_id, 0.0)
        * _likelihood(structure, slot, outcome)
        for structure in structures
    }
    normalizer = sum(weights.values())
    if normalizer <= 0:
        return _uniform_belief(structures)
    return {sid: weight / normalizer for sid, weight in weights.items()}


def _m_probability(structures: list[CausalStructure], belief: dict[int, float], m_value: int) -> float:
    return sum(belief.get(structure.structure_id, 0.0) for structure in structures if structure.m == m_value)


def _map_m(structures: list[CausalStructure], belief: dict[int, float]) -> int:
    p_one = _m_probability(structures, belief, 1)
    return int(p_one >= 0.5)


def _expected_m_separation(
    structures: list[CausalStructure],
    belief: dict[int, float],
    slot: int,
) -> float:
    expected = 0.0
    for outcome in (0, 1):
        p_outcome = sum(
            belief.get(structure.structure_id, 0.0) * _likelihood(structure, slot, outcome)
            for structure in structures
        )
        if p_outcome <= 0:
            continue
        updated = _posterior(structures, belief, slot, outcome)
        p_m1 = _m_probability(structures, updated, 1)
        expected += p_outcome * abs(p_m1 - (1.0 - p_m1))
    return expected


def _counterfactual_predictions(
    structures: list[CausalStructure],
) -> list[dict[str, float | int]]:
    rows: list[dict[str, float | int]] = []
    for structure in structures:
        for slot in range(K_SLOTS):
            rows.append(
                {
                    "structure_id": structure.structure_id,
                    "slot": slot,
                    "p_outcome_1": _p_outcome_one(structure, slot),
                    "p_outcome_0": 1.0 - _p_outcome_one(structure, slot),
                }
            )
    return rows


def candidate(O: np.ndarray, allowed_memory: dict[str, Any], observed_outcome_if_any: dict[str, int] | None) -> PolicyResult:
    structures = _structures(allowed_memory)
    belief = _belief_from_memory(allowed_memory, structures)
    slot_scores = {
        slot: _expected_m_separation(structures, belief, slot)
        for slot in range(K_SLOTS)
    }
    selected_slot = min(slot_scores, key=lambda slot: (-slot_scores[slot], slot))
    result: PolicyResult = {
        "agent": "candidate",
        "slot_selected": selected_slot,
        "b_before": belief,
        "slot_scores": slot_scores,
        "cf_predictions_per_structure": _counterfactual_predictions(structures),
    }
    if observed_outcome_if_any is not None:
        slot = int(observed_outcome_if_any["slot"])
        outcome = int(observed_outcome_if_any["outcome"])
        updated = _posterior(structures, belief, slot, outcome)
        result["b_after"] = updated
        result["Y_star_pred"] = _map_m(structures, updated)
    return result


def passive_lookup(O: np.ndarray, allowed_memory: dict[str, Any], observed_outcome_if_any: dict[str, int] | None) -> PolicyResult:
    prediction = int(float(np.mean(O)) >= 0.5)
    return {"agent": "passive_lookup", "slot_selected": None, "Y_star_pred": prediction}


def nearest_neighbor(O: np.ndarray, allowed_memory: dict[str, Any], observed_outcome_if_any: dict[str, int] | None) -> PolicyResult:
    prediction = int(float(np.mean(O[:, 0])) >= 0.5)
    return {"agent": "nearest_neighbor", "slot_selected": None, "Y_star_pred": prediction}


def graph_cache(O: np.ndarray, allowed_memory: dict[str, Any], observed_outcome_if_any: dict[str, int] | None) -> PolicyResult:
    prediction = int(allowed_memory.get("graph_cache_default_prediction", 0))
    return {"agent": "graph_cache", "slot_selected": None, "Y_star_pred": prediction}


def ucb(O: np.ndarray, allowed_memory: dict[str, Any], observed_outcome_if_any: dict[str, int] | None) -> PolicyResult:
    stats = allowed_memory.get("ucb_stats", {})
    if allowed_memory.get("ucb_learned_best_slot") is not None:
        selected_slot = int(allowed_memory["ucb_learned_best_slot"])
    elif not stats:
        selected_slot = 0
    else:
        total_pulls = sum(max(1, int(row.get("pulls", 0))) for row in stats.values())
        scores = {}
        for slot in range(K_SLOTS):
            row = stats.get(slot, {})
            pulls = max(1, int(row.get("pulls", 0)))
            mean_reward = float(row.get("reward", 0.0)) / pulls
            scores[slot] = mean_reward + math.sqrt(2.0 * math.log(max(total_pulls, 2)) / pulls)
        selected_slot = min(scores, key=lambda slot: (-scores[slot], slot))
    prediction = 0
    if observed_outcome_if_any is not None:
        prediction = int(observed_outcome_if_any["outcome"])
    return {"agent": "ucb", "slot_selected": selected_slot, "Y_star_pred": prediction}


def myopic_ig(O: np.ndarray, allowed_memory: dict[str, Any], observed_outcome_if_any: dict[str, int] | None) -> PolicyResult:
    prediction = 0
    if observed_outcome_if_any is not None:
        prediction = int(observed_outcome_if_any["outcome"])
    return {
        "agent": "myopic_ig",
        "slot_selected": 0,
        "Y_star_pred": prediction,
        "selection_reason": "observational_entropy_uniform",
    }


def evi_oracle(O: np.ndarray, allowed_memory: dict[str, Any], observed_outcome_if_any: dict[str, int] | None) -> PolicyResult:
    structures = _structures(allowed_memory)
    belief = _belief_from_memory(allowed_memory, structures)
    slot_scores = {
        slot: _expected_m_separation(structures, belief, slot)
        for slot in range(K_SLOTS)
    }
    selected_slot = min(slot_scores, key=lambda slot: (-slot_scores[slot], slot))
    result: PolicyResult = {
        "agent": "evi_oracle",
        "slot_selected": selected_slot,
        "slot_scores": slot_scores,
        "upper_bound_reference_only": True,
    }
    if observed_outcome_if_any is not None:
        result["Y_star_pred"] = _map_m(
            structures,
            _posterior(
                structures,
                belief,
                int(observed_outcome_if_any["slot"]),
                int(observed_outcome_if_any["outcome"]),
            ),
        )
    else:
        result["Y_star_pred"] = _map_m(structures, belief)
    return result


def fixed_amem(O: np.ndarray, allowed_memory: dict[str, Any], observed_outcome_if_any: dict[str, int] | None) -> PolicyResult:
    counts = allowed_memory.get("train_diagnostic_counts", {0: 1, 1: 1, 2: 0, 3: 0})
    selected_slot = min(range(K_SLOTS), key=lambda slot: (-int(counts.get(slot, 0)), slot))
    prediction = 0
    if observed_outcome_if_any is not None:
        prediction = int(observed_outcome_if_any["outcome"])
    return {"agent": "fixed_amem", "slot_selected": selected_slot, "Y_star_pred": prediction}


def obs_decoder(O: np.ndarray, allowed_memory: dict[str, Any], observed_outcome_if_any: dict[str, int] | None) -> PolicyResult:
    flattened = np.asarray(O).reshape(1, -1)
    decoder_m = allowed_memory.get("obs_decoder_m")
    decoder_j = allowed_memory.get("obs_decoder_j")
    pred_m = int(decoder_m.predict(flattened)[0]) if decoder_m is not None else 0
    pred_j = int(decoder_j.predict(flattened)[0]) if decoder_j is not None else 0
    return {
        "agent": "obs_decoder",
        "slot_selected": None,
        "Y_star_pred": pred_m,
        "j_pred_diagnostic_only": pred_j,
    }


def build_policy_registry() -> dict[str, PolicyFn]:
    return {
        "candidate": candidate,
        "passive_lookup": passive_lookup,
        "nearest_neighbor": nearest_neighbor,
        "graph_cache": graph_cache,
        "ucb": ucb,
        "myopic_ig": myopic_ig,
        "evi_oracle": evi_oracle,
        "fixed_amem": fixed_amem,
        "obs_decoder": obs_decoder,
    }

