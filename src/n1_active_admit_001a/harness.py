from __future__ import annotations

import hashlib
import inspect
import random
import time
from collections.abc import Callable, Iterable
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression

from . import BASE_SEED, TASK_ID
from .env_bandit import BanditEnv
from .env_causal import CausalEnv, CausalEpisode, CausalStructure, enumerate_structures
from .policies import build_policy_registry, candidate


def code_path_hash(func: Callable[..., Any]) -> str:
    source = inspect.getsource(func)
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


TRACE_SCHEMA_FIELDS = [
    "t",
    "env",
    "seed_index",
    "structure_id",
    "observation",
    "allowed_memory",
    "b_before",
    "slot_selected",
    "cf_predictions_per_structure",
    "outcome_actual",
    "b_after",
    "Y_star_true",
    "Y_star_pred_per_agent",
    "baseline_slot_choices",
]


def _episode_context_memory(episode: CausalEpisode) -> dict[str, Any]:
    # Observational-equivalence class for this episode: both m values for the
    # true diagnostic slot j*. This reveals the distinguishing intervention
    # target, not the answer m, and is shared with every policy.
    j_star = episode.structure.j
    pair = [
        CausalStructure(structure_id=-2, m=0, j=j_star),
        CausalStructure(structure_id=-1, m=1, j=j_star),
    ]
    return {
        "structure_family": pair,
        "train_diagnostic_counts": {0: 2, 1: 2, 2: 0, 3: 0},
        "ucb_stats": {},
        "ucb_learned_best_slot": None,
        "graph_cache_default_prediction": 0,
    }


def _serialize_memory(memory: dict[str, Any]) -> dict[str, Any]:
    serialized: dict[str, Any] = {}
    for key, value in memory.items():
        if key == "structure_family":
            serialized[key] = [
                {"structure_id": item.structure_id, "m": item.m, "j": item.j}
                for item in value
            ]
        else:
            serialized[key] = value
    return serialized


def produce_episode_trace_row(
    t: int,
    seed_index: int,
    structure_index: int,
    policy_registry: dict[str, Callable[[np.ndarray, dict[str, Any], dict[str, int] | None], dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    env = CausalEnv()
    episode = env.sample_episode(structure_index=structure_index, seed_index=seed_index)
    memory = _episode_context_memory(episode)
    policies = policy_registry or build_policy_registry()
    candidate_before = policies["candidate"](episode.observation, memory, None)
    selected_slot = int(candidate_before["slot_selected"])
    outcome = env.intervene(episode, selected_slot)
    observed = {"slot": selected_slot, "outcome": outcome}
    predictions: dict[str, int] = {}
    baseline_slots: dict[str, int | None] = {}
    for name, policy in policies.items():
        result = policy(episode.observation, memory, observed)
        if "Y_star_pred" in result:
            predictions[name] = int(result["Y_star_pred"])
        if name != "candidate":
            slot_value = result.get("slot_selected")
            baseline_slots[name] = None if slot_value is None else int(slot_value)
    candidate_after = policies["candidate"](episode.observation, memory, observed)
    return {
        "t": t,
        "env": "E_causal",
        "seed_index": seed_index,
        "structure_id": episode.structure_id,
        "observation": episode.observation.astype(int).tolist(),
        "allowed_memory": _serialize_memory(memory),
        "b_before": candidate_before["b_before"],
        "slot_selected": selected_slot,
        "cf_predictions_per_structure": candidate_before["cf_predictions_per_structure"],
        "outcome_actual": outcome,
        "b_after": candidate_after.get("b_after"),
        "Y_star_true": episode.y_star,
        "Y_star_pred_per_agent": predictions,
        "baseline_slot_choices": baseline_slots,
    }


def replay_trace_row(row: dict[str, Any]) -> dict[str, Any]:
    forbidden = {"m", "j", "structure_id", "Y_star_true"}
    memory = dict(row["allowed_memory"])
    if forbidden & set(memory):
        raise ValueError(f"forbidden replay memory keys present: {sorted(forbidden & set(memory))}")
    if "structure_family" in memory:
        from .env_causal import CausalStructure

        memory["structure_family"] = [
            CausalStructure(
                structure_id=int(item["structure_id"]),
                m=int(item["m"]),
                j=int(item["j"]),
            )
            for item in memory["structure_family"]
        ]
    observation = np.asarray(row["observation"], dtype=np.int8)
    observed = {"slot": int(row["slot_selected"]), "outcome": int(row["outcome_actual"])}
    policies = build_policy_registry()
    replayed = {
        name: policy(observation, memory, observed)
        for name, policy in policies.items()
    }
    return {
        "task_id": TASK_ID,
        "replay_function": "src.n1_active_admit_001a.harness:replay_trace_row",
        "code_path_hash": code_path_hash(replay_trace_row),
        "recomputed": replayed,
        "future_info_assertion": "replay consumed observation, allowed_memory, and observed_outcome only",
    }


def score_predictions(trace_rows: Iterable[dict[str, Any]], agent_name: str) -> dict[str, Any]:
    rows = list(trace_rows)
    if not rows:
        raise ValueError("cannot score empty trace")
    correct = [
        int(row["Y_star_pred_per_agent"][agent_name] == row["Y_star_true"])
        for row in rows
    ]
    return {
        "producer_function": "src.n1_active_admit_001a.harness:score_predictions",
        "code_path_hash": code_path_hash(score_predictions),
        "agent": agent_name,
        "n": len(correct),
        "correct": sum(correct),
        "accuracy": sum(correct) / len(correct),
        "aggregation_rule": "mean(correct_prediction)",
    }


def aggregate_accuracy(score_rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(score_rows)
    if not rows:
        raise ValueError("cannot aggregate empty score rows")
    total_n = sum(int(row["n"]) for row in rows)
    total_correct = sum(int(row["correct"]) for row in rows)
    return {
        "producer_function": "src.n1_active_admit_001a.harness:aggregate_accuracy",
        "code_path_hash": code_path_hash(aggregate_accuracy),
        "n": total_n,
        "correct": total_correct,
        "accuracy": total_correct / total_n,
        "aggregation_rule": "sum(correct)/sum(n)",
    }


def evaluate_acceptance_gate(metrics: dict[str, float], thresholds: dict[str, float]) -> dict[str, Any]:
    weak_max = max(
        metrics["passive_lookup_heldout_acc"],
        metrics["ucb_heldout_acc"],
        metrics["myopic_ig_heldout_acc"],
    )
    causal_margin = metrics["candidate_heldout_acc"] - weak_max
    bandit_condition = (
        metrics["candidate_bandit_normreward"]
        <= metrics["ucb_bandit_normreward"] + thresholds["epsilon_bandit_noninferior"]
    )
    saturation_invalid = (
        metrics["ucb_bandit_normreward"] >= 0.95
        and metrics["candidate_bandit_normreward"] >= 0.95
    )
    return {
        "producer_function": "src.n1_active_admit_001a.harness:evaluate_acceptance_gate",
        "code_path_hash": code_path_hash(evaluate_acceptance_gate),
        "causal_margin": causal_margin,
        "candidate_min_gate": metrics["candidate_heldout_acc"]
        >= thresholds["candidate_min_heldout_acc"],
        "causal_margin_gate": causal_margin >= thresholds["delta_causal_margin"],
        "bandit_noninferior_gate": bandit_condition,
        "bandit_saturation_invalid": saturation_invalid,
        "aggregation_rule": "frozen STEP-A threshold conjunction",
    }


def _decoder_score(
    X: np.ndarray,
    y: np.ndarray,
    random_state: int,
) -> float:
    rng = np.random.default_rng(random_state)
    indices = rng.permutation(len(y))
    train_count = max(1, int(0.6 * len(y)))
    train_idx = indices[:train_count]
    test_idx = indices[train_count:]
    model = LogisticRegression(solver="lbfgs", random_state=random_state, max_iter=1000)
    model.fit(X[train_idx], y[train_idx])
    return float(model.score(X[test_idx], y[test_idx]))


def leakage_scanner(
    X: np.ndarray,
    y: np.ndarray,
    chance: float,
    threshold_margin: float,
    random_state: int,
    decoder_target: str,
) -> dict[str, Any]:
    score = _decoder_score(X, y, random_state=random_state)
    threshold = chance + threshold_margin
    return {
        "scanner_function": "src.n1_active_admit_001a.harness:leakage_scanner",
        "code_path_hash": code_path_hash(leakage_scanner),
        "decoder_target": decoder_target,
        "score": score,
        "chance": chance,
        "threshold": threshold,
        "elevated_decodability_flagged": score > threshold,
        "positive_control_available": True,
    }


def synthetic_canary_leakage_positive_control(
    n_rows_per_class: int,
    random_state: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(random_state)
    labels = np.repeat(np.arange(4), n_rows_per_class)
    noise = rng.binomial(n=1, p=0.5, size=(len(labels), 64 * 4))
    canary = labels.reshape(-1, 1)
    X = np.hstack([noise, canary])
    report = leakage_scanner(
        X=X,
        y=labels,
        chance=0.25,
        threshold_margin=0.10,
        random_state=random_state,
        decoder_target="j",
    )
    report["positive_control_triggered"] = bool(report["elevated_decodability_flagged"])
    report["control_type"] = "synthetic_canary_extra_feature"
    return report


def run_feasibility_probe(n_dummy_episodes: int = 5) -> dict[str, Any]:
    started = time.perf_counter()
    causal = CausalEnv()
    bandit = BanditEnv()
    chooser = random.Random(BASE_SEED)
    causal_rows: list[dict[str, Any]] = []
    bandit_rows: list[dict[str, Any]] = []
    for index in range(n_dummy_episodes):
        causal_episode = causal.sample_episode(
            structure_index=index % len(causal.structures),
            seed_index=index,
        )
        slot = chooser.randrange(0, 4)
        causal_rows.append(
            {
                "env": "E_causal",
                "seed_index": index,
                "slot": slot,
                "outcome": causal.intervene(causal_episode, slot),
            }
        )
        bandit_episode = bandit.sample_episode(seed_index=index)
        arm = chooser.randrange(0, 10)
        bandit_rows.append(
            {
                "env": "E_bandit",
                "seed_index": index,
                "arm": arm,
                "reward": bandit_episode.reward(index % bandit_episode.horizon, arm),
            }
        )
    return {
        "producer_function": "src.n1_active_admit_001a.harness:run_feasibility_probe",
        "code_path_hash": code_path_hash(run_feasibility_probe),
        "dummy_episodes": n_dummy_episodes,
        "metric_aggregation_executed": False,
        "candidate_baseline_accuracy_computed": False,
        "wall_clock_seconds": time.perf_counter() - started,
        "causal_rows": causal_rows,
        "bandit_rows": bandit_rows,
    }


def candidate_symmetry_audit_note() -> dict[str, Any]:
    structures = enumerate_structures()
    belief = {structure.structure_id: 1.0 / len(structures) for structure in structures}
    slot_scores = candidate(
        np.zeros((64, 4), dtype=np.int8),
        {"structure_family": structures, "belief": belief},
        None,
    )["slot_scores"]
    return {
        "audit_function": "src.n1_active_admit_001a.harness:candidate_symmetry_audit_note",
        "code_path_hash": code_path_hash(candidate_symmetry_audit_note),
        "slot_scores_under_uniform_prior": slot_scores,
        "interpretation": (
            "pre-outcome selection is symmetric under the STEP-A all-8 memory; "
            "STEP-A2 replaces that instrument with the per-episode equivalence-class context"
        ),
        "score_claim": "none",
    }
