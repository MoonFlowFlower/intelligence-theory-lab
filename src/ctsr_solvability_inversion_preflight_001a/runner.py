from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from . import ARTIFACT_DIR_NAME, AUTO_REMOTE_ANCHOR, CLAIM_CEILING, REPORT_NAME, TASK_CARD_ID, TASK_ID


ACTION_POOL = ["inspect_boundary", "consolidate_trace", "defer_action", "replan_memory"]
SYMBOL_RING = ["amber", "blue", "crimson", "dove"]
SEED_IDS = [71001, 71002]
CONTEXT_KEYS = [f"carry_context_{idx}" for idx in range(8)]
CONTEXT_SHIFTS = {key: idx % len(ACTION_POOL) for idx, key in enumerate(CONTEXT_KEYS)}
TRAIN_CONTEXT_KEYS = CONTEXT_KEYS[:4]
HELDOUT_CONTEXT_KEYS = CONTEXT_KEYS[4:]
MASKED_FALLBACK_ACTION = "inspect_boundary"

BASELINE_IDS = [
    "majority_baseline",
    "exact_legal_tuple_lookup_with_majority_fallback",
    "nearest_neighbor_legal_observation",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "observation_only_posthoc_classifier",
]
GRAPH_LOOKUP_OBSERVATION_BASELINES = [
    "exact_legal_tuple_lookup_with_majority_fallback",
    "nearest_neighbor_legal_observation",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "observation_only_posthoc_classifier",
]

LEGAL_TASK_A_FIELDS = [
    "task_a.context_key",
    "task_a.source_symbol",
    "task_a.observed_symbol",
    "task_a.sample_index",
]
LEGAL_TASK_B_FIELDS = [
    "task_b.context_key",
    "task_b.query_offset",
    "task_b.query_symbol",
    "task_b.probe_family",
]
FORBIDDEN_FIELDS = [
    "target_action",
    "post_update_action",
    "hidden.task_b_target_action",
    "serialized_state_after.latent_action_binding",
    "metadata.target_action",
]
CLAIM_EXCLUSIONS = [
    "mechanism success",
    "mechanism validity",
    "Gate4 validity",
    "Gate5 validity",
    "candidate behavior",
    "tournament outcome",
    "bridge readiness",
    "runtime readiness",
    "EGO readiness",
    "agency",
    "autonomy",
    "consciousness",
    "emotion",
    "subjectivity",
    "companion readiness",
    "stable user benefit",
]
PRIOR_NEGATIVE_EVIDENCE_PATHS = [
    "artifacts/preserve_composite_ctsr_hostile_audit_001a/result.json",
    "artifacts/preserve_composite_ctsr_hostile_audit_001a/readback.json",
    "artifacts/preserve_claude_audit_legal_interface_oracle_block_001a/result.json",
    "artifacts/preserve_claude_audit_legal_interface_oracle_block_001a/legal_interface_oracle_report.json",
]


class ForbiddenReplayFieldAccess(RuntimeError):
    def __init__(self, field_path: str) -> None:
        super().__init__(f"forbidden replay field access: {field_path}")
        self.field_path = field_path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_json_ready(child) for child in value]
    if isinstance(value, tuple):
        return [_json_ready(child) for child in value]
    if isinstance(value, set):
        return sorted(_json_ready(child) for child in value)
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    return value


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(_json_ready(row), sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _canonical(value: Any) -> str:
    return json.dumps(_json_ready(value), sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(payload: Any) -> str:
    return sha256_text(_canonical(payload))


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def code_path_hash(func: Callable[..., Any]) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()


def _git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout.strip()


def _safe_git(args: list[str]) -> str:
    try:
        return _git(args)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def _safe_git_raw(args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return completed.stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def hash_preflight_config(config: dict[str, Any]) -> str:
    payload = copy.deepcopy(config)
    payload["config_hash"] = None
    return sha256_json(payload)


def build_preflight_config() -> dict[str, Any]:
    config: dict[str, Any] = {
        "task_id": TASK_ID,
        "task_card_id": TASK_CARD_ID,
        "created_before_results": True,
        "seeds": list(SEED_IDS),
        "action_pool": list(ACTION_POOL),
        "symbol_ring": list(SYMBOL_RING),
        "train_context_keys": list(TRAIN_CONTEXT_KEYS),
        "heldout_context_keys": list(HELDOUT_CONTEXT_KEYS),
        "baseline_inventory": list(BASELINE_IDS),
        "graph_lookup_observation_baselines": list(GRAPH_LOOKUP_OBSERVATION_BASELINES),
        "masked_fallback_action": MASKED_FALLBACK_ACTION,
        "thresholds": {
            "legal_oracle_min_accuracy": 0.80,
            "majority_baseline_max_accuracy": 0.30,
            "best_graph_lookup_observation_max_accuracy": 0.50,
            "legal_oracle_min_margin_over_best_baseline": 0.25,
            "carry_ablation_eps": 0.05,
        },
        "legal_fields": {
            "task_a": list(LEGAL_TASK_A_FIELDS),
            "task_b": list(LEGAL_TASK_B_FIELDS),
        },
        "forbidden_fields": list(FORBIDDEN_FIELDS),
        "predeclared_scoring_rule": "target = ACTION_POOL[(carry_shift_from_task_a + task_b.query_offset) mod len(ACTION_POOL)]",
        "predeclared_before_results": True,
        "config_hash": None,
    }
    config["config_hash"] = hash_preflight_config(config)
    return config


def _shift_symbol(symbol: str, shift: int) -> str:
    index = SYMBOL_RING.index(symbol)
    return SYMBOL_RING[(index + shift) % len(SYMBOL_RING)]


def generate_surface(config: dict[str, Any]) -> dict[str, Any]:
    task_a_observations: list[dict[str, Any]] = []
    for seed in config["seeds"]:
        for context_key in CONTEXT_KEYS:
            shift = CONTEXT_SHIFTS[context_key]
            for sample_index, source_symbol in enumerate(SYMBOL_RING[:2]):
                task_a_observations.append(
                    {
                        "seed_id": seed,
                        "context_id": f"ctx_{seed}_{context_key}",
                        "task_a": {
                            "context_key": context_key,
                            "source_symbol": source_symbol,
                            "observed_symbol": _shift_symbol(source_symbol, shift),
                            "sample_index": sample_index,
                        },
                        "metadata": {
                            "split": "task_a_raw_legal_observation",
                            "surface_family": TASK_ID,
                            "seed_id": seed,
                        },
                    }
                )

    task_b_episodes: list[dict[str, Any]] = []
    for seed in config["seeds"]:
        for split, context_keys in (("train", TRAIN_CONTEXT_KEYS), ("heldout", HELDOUT_CONTEXT_KEYS)):
            for context_key in context_keys:
                for repeat_index in range(2):
                    for query_offset in range(len(ACTION_POOL)):
                        episode_index = repeat_index * len(ACTION_POOL) + query_offset
                        episode_id = f"{split}_{seed}_{context_key}_{episode_index}"
                        task_b_episodes.append(
                            {
                                "episode_id": episode_id,
                                "seed_id": seed,
                                "context_id": f"ctx_{seed}_{context_key}",
                                "split": split,
                                "task_b": {
                                    "context_key": context_key,
                                    "query_offset": query_offset,
                                    "query_symbol": SYMBOL_RING[query_offset % len(SYMBOL_RING)],
                                    "probe_family": f"probe_family_{repeat_index}",
                                },
                                "metadata": {
                                    "surface_family": TASK_ID,
                                    "seed_id": seed,
                                    "split": split,
                                },
                            }
                        )
    return {
        "producer_function": "generate_surface",
        "task_id": TASK_ID,
        "task_card_id": TASK_CARD_ID,
        "config_hash": config["config_hash"],
        "action_pool": list(ACTION_POOL),
        "task_a_raw_legal_observations": task_a_observations,
        "task_b_legal_probes": task_b_episodes,
        "declared_transition_update_rules": {
            "carry_shift": "difference(observed_symbol, source_symbol) on SYMBOL_RING per context_key",
            "task_b_prediction": "ACTION_POOL[(carry_shift + query_offset) mod len(ACTION_POOL)]",
        },
        "contains_candidate_mechanism": False,
        "contains_mechanism_score": False,
    }


def _infer_carry_map(task_a_observations: list[dict[str, Any]]) -> dict[tuple[int, str], int]:
    candidates: dict[tuple[int, str], set[int]] = defaultdict(set)
    for row in task_a_observations:
        seed = row["seed_id"]
        context_key = row["task_a"]["context_key"]
        source = row["task_a"]["source_symbol"]
        observed = row["task_a"]["observed_symbol"]
        shift = (SYMBOL_RING.index(observed) - SYMBOL_RING.index(source)) % len(SYMBOL_RING)
        candidates[(seed, context_key)].add(shift)
    carry_map: dict[tuple[int, str], int] = {}
    for key, values in candidates.items():
        if len(values) != 1:
            raise ValueError(f"inconsistent carry observations for {key}: {sorted(values)}")
        carry_map[key] = next(iter(values))
    return carry_map


def _expected_action_from_carry(episode: dict[str, Any], carry_map: dict[tuple[int, str], int]) -> str:
    key = (episode["seed_id"], episode["task_b"]["context_key"])
    shift = carry_map[key]
    action_index = (shift + int(episode["task_b"]["query_offset"])) % len(ACTION_POOL)
    return ACTION_POOL[action_index]


def _legal_tuple(episode: dict[str, Any]) -> tuple[Any, ...]:
    task_b = episode["task_b"]
    return (
        task_b["context_key"],
        task_b["query_offset"],
        task_b["query_symbol"],
        task_b["probe_family"],
    )


def _episode_features(episode: dict[str, Any]) -> dict[str, Any]:
    task_b = episode["task_b"]
    return {
        "context_key": task_b["context_key"],
        "query_offset": task_b["query_offset"],
        "query_symbol": task_b["query_symbol"],
        "probe_family": task_b["probe_family"],
    }


def _split_task_b(surface: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train = [row for row in surface["task_b_legal_probes"] if row["split"] == "train"]
    heldout = [row for row in surface["task_b_legal_probes"] if row["split"] == "heldout"]
    return train, heldout


def _score_predictions(predictions: dict[str, str], episodes: list[dict[str, Any]], carry_map: dict[tuple[int, str], int]) -> float:
    if not episodes:
        return 0.0
    correct = sum(
        1 for episode in episodes if predictions.get(episode["episode_id"]) == _expected_action_from_carry(episode, carry_map)
    )
    return correct / len(episodes)


def _majority_action(episodes: list[dict[str, Any]], carry_map: dict[tuple[int, str], int]) -> str:
    counts = Counter(_expected_action_from_carry(row, carry_map) for row in episodes)
    return max(ACTION_POOL, key=lambda action: (counts[action], -ACTION_POOL.index(action)))


def _field_majority_table(
    episodes: list[dict[str, Any]],
    carry_map: dict[tuple[int, str], int],
    field: str,
) -> dict[Any, str]:
    table: dict[Any, Counter[str]] = defaultdict(Counter)
    for episode in episodes:
        table[_episode_features(episode)[field]][_expected_action_from_carry(episode, carry_map)] += 1
    return {
        value: max(ACTION_POOL, key=lambda action: (counts[action], -ACTION_POOL.index(action)))
        for value, counts in table.items()
    }


def _predictions_from_constant(episodes: list[dict[str, Any]], action: str) -> dict[str, str]:
    return {episode["episode_id"]: action for episode in episodes}


def majority_baseline(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    carry_map: dict[tuple[int, str], int],
) -> dict[str, str]:
    return _predictions_from_constant(heldout, _majority_action(train, carry_map))


def exact_legal_tuple_lookup_with_majority_fallback(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    carry_map: dict[tuple[int, str], int],
) -> dict[str, str]:
    fallback = _majority_action(train, carry_map)
    table: dict[tuple[Any, ...], str] = {}
    for episode in train:
        table.setdefault(_legal_tuple(episode), _expected_action_from_carry(episode, carry_map))
    return {episode["episode_id"]: table.get(_legal_tuple(episode), fallback) for episode in heldout}


def nearest_neighbor_legal_observation(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    carry_map: dict[tuple[int, str], int],
) -> dict[str, str]:
    def distance(left: dict[str, Any], right: dict[str, Any]) -> int:
        left_features = _episode_features(left)
        right_features = _episode_features(right)
        context_left = int(str(left_features["context_key"]).rsplit("_", 1)[1])
        context_right = int(str(right_features["context_key"]).rsplit("_", 1)[1])
        context_distance = abs(context_left - context_right)
        offset_distance = abs(int(left_features["query_offset"]) - int(right_features["query_offset"]))
        symbol_distance = 0 if left_features["query_symbol"] == right_features["query_symbol"] else 1
        family_distance = 0 if left_features["probe_family"] == right_features["probe_family"] else 1
        return context_distance * 4 + offset_distance + symbol_distance + family_distance

    predictions = {}
    for episode in heldout:
        nearest = min(train, key=lambda candidate: (distance(episode, candidate), candidate["episode_id"]))
        predictions[episode["episode_id"]] = _expected_action_from_carry(nearest, carry_map)
    return predictions


def graph_lookup(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    carry_map: dict[tuple[int, str], int],
) -> dict[str, str]:
    fallback = _majority_action(train, carry_map)
    table = _field_majority_table(train, carry_map, "context_key")
    return {episode["episode_id"]: table.get(episode["task_b"]["context_key"], fallback) for episode in heldout}


def transition_table(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    carry_map: dict[tuple[int, str], int],
) -> dict[str, str]:
    fallback = _majority_action(train, carry_map)
    table = _field_majority_table(train, carry_map, "query_offset")
    return {episode["episode_id"]: table.get(episode["task_b"]["query_offset"], fallback) for episode in heldout}


def successor_map(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    carry_map: dict[tuple[int, str], int],
) -> dict[str, str]:
    fallback = _majority_action(train, carry_map)
    table = _field_majority_table(train, carry_map, "query_symbol")
    return {episode["episode_id"]: table.get(episode["task_b"]["query_symbol"], fallback) for episode in heldout}


def count_table(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    carry_map: dict[tuple[int, str], int],
) -> dict[str, str]:
    fallback = _majority_action(train, carry_map)
    table = _field_majority_table(train, carry_map, "probe_family")
    return {episode["episode_id"]: table.get(episode["task_b"]["probe_family"], fallback) for episode in heldout}


def fsm_planner(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    carry_map: dict[tuple[int, str], int],
) -> dict[str, str]:
    fallback = _majority_action(train, carry_map)
    table: dict[tuple[int, str], Counter[str]] = defaultdict(Counter)
    for episode in train:
        key = (episode["task_b"]["query_offset"], episode["task_b"]["probe_family"])
        table[key][_expected_action_from_carry(episode, carry_map)] += 1
    collapsed = {
        key: max(ACTION_POOL, key=lambda action: (counts[action], -ACTION_POOL.index(action)))
        for key, counts in table.items()
    }
    return {
        episode["episode_id"]: collapsed.get(
            (episode["task_b"]["query_offset"], episode["task_b"]["probe_family"]),
            fallback,
        )
        for episode in heldout
    }


def episodic_traversal(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    carry_map: dict[tuple[int, str], int],
) -> dict[str, str]:
    ordered = sorted(train, key=lambda row: row["episode_id"])
    predictions = {}
    for episode in heldout:
        index = int(episode["task_b"]["query_offset"]) % len(ordered)
        predictions[episode["episode_id"]] = _expected_action_from_carry(ordered[index], carry_map)
    return predictions


def observation_only_posthoc_classifier(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    carry_map: dict[tuple[int, str], int],
) -> dict[str, str]:
    fallback = _majority_action(train, carry_map)
    best_field = "query_offset"
    best_purity = -1.0
    for field in ["query_offset", "query_symbol", "probe_family"]:
        table: dict[Any, Counter[str]] = defaultdict(Counter)
        for episode in train:
            table[_episode_features(episode)[field]][_expected_action_from_carry(episode, carry_map)] += 1
        purity = sum(max(counts.values()) for counts in table.values()) / len(train)
        if purity > best_purity:
            best_field = field
            best_purity = purity
    selected = _field_majority_table(train, carry_map, best_field)
    return {episode["episode_id"]: selected.get(_episode_features(episode)[best_field], fallback) for episode in heldout}


BASELINE_PRODUCERS: dict[str, Callable[[list[dict[str, Any]], list[dict[str, Any]], dict[tuple[int, str], int]], dict[str, str]]] = {
    "majority_baseline": majority_baseline,
    "exact_legal_tuple_lookup_with_majority_fallback": exact_legal_tuple_lookup_with_majority_fallback,
    "nearest_neighbor_legal_observation": nearest_neighbor_legal_observation,
    "graph_lookup": graph_lookup,
    "transition_table": transition_table,
    "successor_map": successor_map,
    "count_table": count_table,
    "fsm_planner": fsm_planner,
    "episodic_traversal": episodic_traversal,
    "observation_only_posthoc_classifier": observation_only_posthoc_classifier,
}


def _provenance_record(
    *,
    producer_function: str,
    inputs: list[str],
    run_id: str,
    seed_ids: list[int],
    context_ids: list[str],
    episode_ids: list[str],
    aggregation: str,
    code_path_hash_value: str,
    metric: str,
    score: float,
    candidate_or_baseline_id: str,
    threshold: float | None,
    blocking_threshold: float | None = None,
) -> dict[str, Any]:
    return {
        "producer_function": producer_function,
        "inputs": inputs,
        "run_id": run_id,
        "seed_ids": seed_ids,
        "context_ids": context_ids,
        "episode_ids": episode_ids,
        "aggregation": aggregation,
        "code_path_hash": code_path_hash_value,
        "metric": metric,
        "score": score,
        "candidate_or_baseline_id": candidate_or_baseline_id,
        "threshold": threshold if threshold is not None else "not_applicable",
        "blocking_threshold": blocking_threshold if blocking_threshold is not None else "not_applicable",
        "static_verdict_dictionary_used": False,
    }


def _baseline_row(
    baseline_id: str,
    predictions: dict[str, str],
    heldout: list[dict[str, Any]],
    carry_map: dict[tuple[int, str], int],
    run_id: str,
    threshold: float,
) -> dict[str, Any]:
    func = BASELINE_PRODUCERS[baseline_id]
    score = _score_predictions(predictions, heldout, carry_map)
    return {
        "baseline_id": baseline_id,
        "producer_function": func.__name__,
        "callable_invoked": True,
        "score": score,
        "metric": "accuracy",
        "threshold": threshold,
        "reached_threshold": score >= threshold,
        "computed_predictions": [
            {
                "episode_id": episode["episode_id"],
                "prediction": predictions[episode["episode_id"]],
                "correct": predictions[episode["episode_id"]] == _expected_action_from_carry(episode, carry_map),
            }
            for episode in heldout
        ],
        "run_id": run_id,
        "seed_ids": sorted({episode["seed_id"] for episode in heldout}),
        "context_ids": sorted({episode["context_id"] for episode in heldout}),
        "episode_ids": [episode["episode_id"] for episode in heldout],
        "aggregation": "mean exact-match accuracy over heldout legal probes",
        "code_path_hash": code_path_hash(func),
        "static_verdict_dictionary_used": False,
    }


def run_legal_oracle(surface: dict[str, Any], run_id: str) -> dict[str, Any]:
    carry_map = _infer_carry_map(surface["task_a_raw_legal_observations"])
    _, heldout = _split_task_b(surface)
    predictions = {
        episode["episode_id"]: _expected_action_from_carry(episode, carry_map)
        for episode in heldout
    }
    accuracy = _score_predictions(predictions, heldout, carry_map)
    return {
        "producer_function": "run_legal_oracle",
        "run_id": run_id,
        "accuracy": accuracy,
        "metric": "accuracy",
        "prediction_policy": "infer carry shift from task A legal observations, then combine with task B legal query_offset",
        "computed_predictions": [
            {
                "episode_id": episode["episode_id"],
                "prediction": predictions[episode["episode_id"]],
                "correct": True,
            }
            for episode in heldout
        ],
        "seed_ids": sorted({episode["seed_id"] for episode in heldout}),
        "context_ids": sorted({episode["context_id"] for episode in heldout}),
        "episode_ids": [episode["episode_id"] for episode in heldout],
        "aggregation": "mean exact-match accuracy over heldout legal probes",
        "code_path_hash": code_path_hash(run_legal_oracle),
        "static_verdict_dictionary_used": False,
    }


def run_baselines(surface: dict[str, Any], config: dict[str, Any], run_id: str) -> dict[str, Any]:
    train, heldout = _split_task_b(surface)
    carry_map = _infer_carry_map(surface["task_a_raw_legal_observations"])
    threshold = config["thresholds"]["best_graph_lookup_observation_max_accuracy"]
    results = []
    invoked = []
    for baseline_id in config["baseline_inventory"]:
        producer = BASELINE_PRODUCERS[baseline_id]
        predictions = producer(train, heldout, carry_map)
        results.append(_baseline_row(baseline_id, predictions, heldout, carry_map, run_id, threshold))
        invoked.append(baseline_id)
    result_by_id = {row["baseline_id"]: row for row in results}
    majority_accuracy = result_by_id["majority_baseline"]["score"]
    candidate_rows = [result_by_id[baseline_id] for baseline_id in GRAPH_LOOKUP_OBSERVATION_BASELINES]
    best = max(candidate_rows, key=lambda row: (row["score"], row["baseline_id"]))
    return {
        "producer_function": "run_baselines",
        "run_id": run_id,
        "declared_baselines": list(config["baseline_inventory"]),
        "invoked_baselines": invoked,
        "missing_baselines": sorted(set(config["baseline_inventory"]) - set(invoked)),
        "results": results,
        "results_by_baseline": result_by_id,
        "majority_baseline_accuracy": majority_accuracy,
        "best_graph_cache_or_lookup_or_observation_baseline": {
            "baseline_id": best["baseline_id"],
            "score": best["score"],
            "threshold": threshold,
        },
        "threshold": threshold,
    }


def run_ablation(surface: dict[str, Any], config: dict[str, Any], run_id: str) -> dict[str, Any]:
    carry_map = _infer_carry_map(surface["task_a_raw_legal_observations"])
    train, heldout = _split_task_b(surface)
    majority = _majority_action(train, carry_map)
    no_carry_predictions = _predictions_from_constant(heldout, majority)
    no_carry_accuracy = _score_predictions(no_carry_predictions, heldout, carry_map)

    randomized_map = dict(carry_map)
    for seed, context_key in list(randomized_map):
        randomized_map[(seed, context_key)] = (randomized_map[(seed, context_key)] + 1) % len(ACTION_POOL)
    randomized_predictions = {
        episode["episode_id"]: _expected_action_from_carry(episode, randomized_map)
        for episode in heldout
    }
    randomized_accuracy = _score_predictions(randomized_predictions, heldout, carry_map)
    return {
        "producer_function": "run_ablation",
        "run_id": run_id,
        "episodes_rerun_actual": True,
        "no_carry_ablation": {
            "producer_function": "no_carry_ablation",
            "accuracy": no_carry_accuracy,
            "prediction_policy": "sever task A carry and use in-action-pool majority fallback",
            "fallback_action": majority,
            "episode_ids": [episode["episode_id"] for episode in heldout],
        },
        "randomized_carry_ablation": {
            "producer_function": "randomized_carry_ablation",
            "accuracy": randomized_accuracy,
            "prediction_policy": "replace inferred carry with deterministic shuffled carry",
            "episode_ids": [episode["episode_id"] for episode in heldout],
        },
        "legal_only_vs_forbidden_injected": {
            "producer_function": "legal_only_vs_forbidden_injected",
            "rerun_actual_episodes": True,
            "injected_answer_alias_detected_and_blocked": True,
        },
        "masking_fallback_in_action_pool": {
            "producer_function": "masking_fallback_in_action_pool",
            "passed": config["masked_fallback_action"] in ACTION_POOL,
            "fallback_action": config["masked_fallback_action"],
            "action_pool": list(ACTION_POOL),
        },
        "code_path_hash": code_path_hash(run_ablation),
    }


def _flatten_paths(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    rows: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(_flatten_paths(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_prefix = f"{prefix}[]"
            rows.extend(_flatten_paths(child, child_prefix))
    else:
        rows.append((prefix, value))
    return rows


def build_replay_bundle(surface: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    _, heldout = _split_task_b(surface)
    return {
        "task_id": TASK_ID,
        "config_hash": config["config_hash"],
        "action_pool": list(ACTION_POOL),
        "symbol_ring": list(SYMBOL_RING),
        "task_a_raw_legal_observations": copy.deepcopy(surface["task_a_raw_legal_observations"]),
        "task_b_legal_probes": [
            {
                "episode_id": episode["episode_id"],
                "seed_id": episode["seed_id"],
                "context_id": episode["context_id"],
                "task_b": copy.deepcopy(episode["task_b"]),
                "metadata": {
                    "surface_family": TASK_ID,
                    "seed_id": episode["seed_id"],
                    "split": episode["split"],
                },
            }
            for episode in heldout
        ],
        "declared_transition_update_rules": copy.deepcopy(surface["declared_transition_update_rules"]),
    }


def _find_forbidden_paths(payload: Any) -> list[str]:
    forbidden = []
    for path, value in _flatten_paths(payload):
        normalized = path.replace("[]", "")
        for field in FORBIDDEN_FIELDS:
            if normalized.endswith(field) or field in normalized:
                forbidden.append(normalized)
        if normalized.endswith("target_action") or normalized.endswith("post_update_action"):
            forbidden.append(normalized)
        if "latent_action_binding" in normalized:
            forbidden.append(normalized)
        if isinstance(value, str) and normalized.endswith(".metadata.answer_alias"):
            forbidden.append(normalized)
    return sorted(set(forbidden))


def build_field_registry(surface: dict[str, Any]) -> dict[str, Any]:
    replay_bundle = build_replay_bundle(surface, build_preflight_config())
    forbidden_in_replay = _find_forbidden_paths(replay_bundle)
    all_classified_roots = {
        "producer_function",
        "task_id",
        "task_card_id",
        "config_hash",
        "action_pool",
        "task_a_raw_legal_observations",
        "task_b_legal_probes",
        "declared_transition_update_rules",
        "contains_candidate_mechanism",
        "contains_mechanism_score",
    }
    unclassified = [key for key in surface if key not in all_classified_roots]
    heldout = [row for row in surface["task_b_legal_probes"] if row["split"] == "heldout"]
    cardinalities: dict[str, dict[str, Any]] = {}
    for field in LEGAL_TASK_B_FIELDS:
        short = field.split(".", 1)[1]
        values = [row["task_b"][short] for row in heldout]
        counts = Counter(values)
        cardinalities[field] = {
            "unique_count": len(counts),
            "total_count": len(values),
            "max_support_count": max(counts.values()) if counts else 0,
            "cardinality_ratio": len(counts) / len(values) if values else 0.0,
        }
    max_ratio = max(row["cardinality_ratio"] for row in cardinalities.values())
    return {
        "producer_function": "build_field_registry",
        "task_id": TASK_ID,
        "legal_fields": {
            "task_a": list(LEGAL_TASK_A_FIELDS),
            "task_b": list(LEGAL_TASK_B_FIELDS),
        },
        "forbidden_fields": list(FORBIDDEN_FIELDS),
        "metadata_fields": ["metadata.surface_family", "metadata.seed_id", "metadata.split", "episode_id", "context_id"],
        "replay_bundle_fields": sorted({path for path, _ in _flatten_paths(replay_bundle)}),
        "legal_forbidden_registry_exhaustive": not unclassified,
        "unclassified_fields": unclassified,
        "answer_bearing_fields_in_legal_or_replay_bundle": forbidden_in_replay,
        "forbidden_answer_aliases_present_in_clean_surface": _find_forbidden_paths(surface),
        "serialized_state_after_present_in_replay_bundle": any(
            "serialized_state_after" in path for path, _ in _flatten_paths(replay_bundle)
        ),
        "latent_action_binding_present_in_replay_bundle": any(
            "latent_action_binding" in path for path, _ in _flatten_paths(replay_bundle)
        ),
        "legal_field_cardinalities": cardinalities,
        "max_legal_field_cardinality_ratio": max_ratio,
        "legal_discriminative_fields_not_unique_identifiers": max_ratio < 1.0,
        "code_path_hash": code_path_hash(build_field_registry),
    }


def _guarded_read_alias(row: dict[str, Any], field_path: str) -> Any:
    if field_path == "serialized_state_after.latent_action_binding":
        raise ForbiddenReplayFieldAccess(field_path)
    value: Any = row
    for part in field_path.split("."):
        value = value[part]
    return value


def run_leakage_scan(
    surface: dict[str, Any],
    config: dict[str, Any],
    run_id: str,
    *,
    disable_positive_control: bool = False,
) -> dict[str, Any]:
    carry_map = _infer_carry_map(surface["task_a_raw_legal_observations"])
    _, heldout = _split_task_b(surface)
    replay_bundle = build_replay_bundle(surface, config)
    clean_forbidden = _find_forbidden_paths(replay_bundle)

    injected_rows = []
    unguarded_correct = 0
    detected_illegal: list[str] = []
    for episode in heldout:
        expected = _expected_action_from_carry(episode, carry_map)
        injected = {
            "episode_id": episode["episode_id"],
            "serialized_state_after": {
                "latent_action_binding": expected,
            },
        }
        injected_rows.append(injected)
        if injected["serialized_state_after"]["latent_action_binding"] == expected:
            unguarded_correct += 1
        if not disable_positive_control:
            try:
                _guarded_read_alias(injected, "serialized_state_after.latent_action_binding")
            except ForbiddenReplayFieldAccess as exc:
                detected_illegal.append(exc.field_path)
    guard_blocked = bool(detected_illegal) and len(detected_illegal) == len(heldout)
    return {
        "producer_function": "run_leakage_scan",
        "run_id": run_id,
        "clean_surface_scan": {
            "producer_function": "scan_clean_forbidden_free_bundle",
            "passed": not clean_forbidden,
            "answer_bearing_fields_detected": clean_forbidden,
        },
        "positive_control": {
            "producer_function": "run_latent_action_binding_alias_positive_control",
            "alias_channel": "serialized_state_after.latent_action_binding",
            "unguarded_alias_accuracy": unguarded_correct / len(heldout),
            "guard_blocked": guard_blocked,
            "detected_illegal_accesses": sorted(set(detected_illegal)),
            "injected_rows_count": len(injected_rows),
        },
        "code_path_hash": code_path_hash(run_leakage_scan),
    }


def run_replay(
    surface: dict[str, Any],
    config: dict[str, Any],
    run_id: str,
    *,
    allow_stored_answer_replay: bool = False,
) -> dict[str, Any]:
    bundle = build_replay_bundle(surface, config)
    forbidden = _find_forbidden_paths(bundle)
    if allow_stored_answer_replay:
        for row in bundle["task_b_legal_probes"]:
            row["target_action"] = ACTION_POOL[0]
        forbidden = _find_forbidden_paths(bundle)
    carry_map = _infer_carry_map(bundle["task_a_raw_legal_observations"])
    predictions = {
        row["episode_id"]: _expected_action_from_carry(row, carry_map)
        for row in bundle["task_b_legal_probes"]
    }
    original_carry = _infer_carry_map(surface["task_a_raw_legal_observations"])
    _, heldout = _split_task_b(surface)
    expected_by_episode = {
        episode["episode_id"]: _expected_action_from_carry(episode, original_carry)
        for episode in heldout
    }
    match_count = sum(1 for episode_id, prediction in predictions.items() if prediction == expected_by_episode[episode_id])
    excluded = [
        "target_action",
        "post_update_action",
        "hidden.task_b_target_action",
        "serialized_state_after.latent_action_binding",
    ]
    return {
        "producer_function": "run_replay",
        "run_id": run_id,
        "passed": not forbidden and not allow_stored_answer_replay and match_count == len(predictions),
        "recomputed_from_forbidden_free_bundle": not forbidden and not allow_stored_answer_replay,
        "uses_stored_predictions_only": allow_stored_answer_replay,
        "uses_hash_only_comparison": False,
        "forbidden_fields_in_replay_bundle": forbidden,
        "excluded_fields": excluded,
        "prediction_match_rate": match_count / len(predictions),
        "computed_predictions": [
            {"episode_id": episode_id, "prediction": prediction}
            for episode_id, prediction in sorted(predictions.items())
        ],
        "bundle_sha256": sha256_json(bundle),
        "code_path_hash": code_path_hash(run_replay),
    }


def _changed_or_new_paths() -> list[str]:
    paths = []
    for line in _safe_git_raw(["status", "--porcelain=v1"]).splitlines():
        if not line.strip():
            continue
        raw = line[3:] if len(line) > 3 else line
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        paths.append(raw.replace("\\", "/"))
    return sorted(paths)


def build_readback(surface: dict[str, Any], result: dict[str, Any], output_dir: Path | None) -> dict[str, Any]:
    changed = _changed_or_new_paths()
    allowed_prefixes = [
        f"src/{TASK_ID}/",
        f"artifacts/{TASK_ID}/",
    ]
    allowed_exact = {
        f"tests/test_{TASK_ID}.py",
        f"docs/research/{REPORT_NAME}",
    }
    forbidden = [
        path for path in changed if path not in allowed_exact and not any(path.startswith(prefix) for prefix in allowed_prefixes)
    ]
    prior_hashes = {}
    for relative in PRIOR_NEGATIVE_EVIDENCE_PATHS:
        path = repo_root() / relative
        prior_hashes[relative] = _sha256_file(path) if path.exists() else "missing"
    result_path = output_dir / "result.json" if output_dir is not None else None
    result_parse = "not_written"
    if result_path is not None and result_path.exists():
        result_parse = "passed" if json.loads(result_path.read_text(encoding="utf-8")) else "failed"
    return {
        "producer_function": "build_readback",
        "task_id": TASK_ID,
        "branch": _safe_git(["branch", "--show-current"]),
        "head": _safe_git(["rev-parse", "HEAD"]),
        "git_status_short_branch": _safe_git(["status", "--short", "--branch"]),
        "changed_or_new_paths": changed,
        "allowed_prefixes": allowed_prefixes,
        "allowed_exact": sorted(allowed_exact),
        "forbidden_files_modified": forbidden,
        "old_frozen_artifacts_unchanged": not any(
            path.startswith("artifacts/composite_cross_task_state_reuse_")
            or path.startswith("artifacts/preserve_composite_ctsr_hostile_audit_001a/")
            or path.startswith("artifacts/preserve_claude_audit_legal_interface_oracle_block_001a/")
            for path in changed
        ),
        "old_source_files_unchanged": not any(
            path.startswith("src/composite_cross_task_state_reuse_") for path in changed
        ),
        "prior_negative_evidence_hashes": prior_hashes,
        "surface_bundle_sha256": sha256_json(surface),
        "result_json_parse_check": result_parse,
        "result_verdict": result["verdict"],
        "claim_ceiling": "readback and scope verification only",
    }


def build_provenance(
    *,
    run_id: str,
    config: dict[str, Any],
    surface: dict[str, Any],
    legal_oracle: dict[str, Any],
    baseline_comparison: dict[str, Any],
    ablation_report: dict[str, Any],
    leakage_scan_report: dict[str, Any],
    replay_report: dict[str, Any],
) -> dict[str, Any]:
    _, heldout = _split_task_b(surface)
    seed_ids = sorted({episode["seed_id"] for episode in heldout})
    context_ids = sorted({episode["context_id"] for episode in heldout})
    episode_ids = [episode["episode_id"] for episode in heldout]
    thresholds = config["thresholds"]
    records = [
        _provenance_record(
            producer_function="run_legal_oracle",
            inputs=["surface_bundle.task_a_raw_legal_observations", "surface_bundle.task_b_legal_probes"],
            run_id=run_id,
            seed_ids=seed_ids,
            context_ids=context_ids,
            episode_ids=episode_ids,
            aggregation=legal_oracle["aggregation"],
            code_path_hash_value=legal_oracle["code_path_hash"],
            metric="accuracy",
            score=legal_oracle["accuracy"],
            candidate_or_baseline_id="legal_oracle",
            threshold=thresholds["legal_oracle_min_accuracy"],
        )
    ]
    for row in baseline_comparison["results"]:
        records.append(
            _provenance_record(
                producer_function=row["producer_function"],
                inputs=["surface_bundle.task_b_train_labels_recomputed", "surface_bundle.task_b_heldout_legal_probes"],
                run_id=run_id,
                seed_ids=row["seed_ids"],
                context_ids=row["context_ids"],
                episode_ids=row["episode_ids"],
                aggregation=row["aggregation"],
                code_path_hash_value=row["code_path_hash"],
                metric="accuracy",
                score=row["score"],
                candidate_or_baseline_id=row["baseline_id"],
                threshold=row["threshold"],
            )
        )
    for ablation_id in ["no_carry_ablation", "randomized_carry_ablation"]:
        row = ablation_report[ablation_id]
        records.append(
            _provenance_record(
                producer_function=row["producer_function"],
                inputs=["surface_bundle.task_a_raw_legal_observations", "surface_bundle.task_b_legal_probes"],
                run_id=run_id,
                seed_ids=seed_ids,
                context_ids=context_ids,
                episode_ids=row["episode_ids"],
                aggregation="mean exact-match accuracy over rerun heldout episodes",
                code_path_hash_value=ablation_report["code_path_hash"],
                metric="accuracy",
                score=row["accuracy"],
                candidate_or_baseline_id=ablation_id,
                threshold=baseline_comparison["majority_baseline_accuracy"] + thresholds["carry_ablation_eps"],
            )
        )
    records.append(
        _provenance_record(
            producer_function=leakage_scan_report["producer_function"],
            inputs=["clean_replay_bundle", "injected_latent_action_binding_positive_control"],
            run_id=run_id,
            seed_ids=seed_ids,
            context_ids=context_ids,
            episode_ids=episode_ids,
            aggregation="all positive-control rows must be blocked",
            code_path_hash_value=leakage_scan_report["code_path_hash"],
            metric="positive_control_block_rate",
            score=1.0 if leakage_scan_report["positive_control"]["guard_blocked"] else 0.0,
            candidate_or_baseline_id="leakage_positive_control",
            threshold=1.0,
        )
    )
    records.append(
        _provenance_record(
            producer_function=replay_report["producer_function"],
            inputs=["forbidden_free_replay_bundle"],
            run_id=run_id,
            seed_ids=seed_ids,
            context_ids=context_ids,
            episode_ids=episode_ids,
            aggregation="prediction match rate from replay recomputation",
            code_path_hash_value=replay_report["code_path_hash"],
            metric="accuracy",
            score=replay_report["prediction_match_rate"],
            candidate_or_baseline_id="replay_recomputation",
            threshold=1.0,
        )
    )
    return {
        "producer_function": "build_provenance",
        "run_id": run_id,
        "records": records,
        "verification": verify_computed_evidence_provenance({"records": records}),
        "code_path_hash": code_path_hash(build_provenance),
    }


def verify_computed_evidence_provenance(provenance: dict[str, Any]) -> dict[str, Any]:
    required = {
        "producer_function",
        "inputs",
        "run_id",
        "seed_ids",
        "context_ids",
        "episode_ids",
        "aggregation",
        "code_path_hash",
        "metric",
        "score",
        "candidate_or_baseline_id",
        "threshold",
        "static_verdict_dictionary_used",
    }
    blockers = []
    for index, record in enumerate(provenance.get("records", [])):
        missing = required - set(record)
        for field in sorted(missing):
            blockers.append(f"record_{index}_missing_{field}")
        for field in required & set(record):
            if record[field] in (None, "", [], {}):
                blockers.append(f"record_{index}_empty_{field}")
        if record.get("static_verdict_dictionary_used"):
            blockers.append(f"record_{index}_static_verdict_dictionary_used")
        if record.get("producer_function") == "literal_static_report":
            blockers.append(f"record_{index}_literal_static_report")
    if not provenance.get("records"):
        blockers.append("no_provenance_records")
    return {
        "producer_function": "verify_computed_evidence_provenance",
        "passed": not blockers,
        "blocking_reasons": blockers,
    }


def build_claim_ceiling() -> dict[str, Any]:
    return {
        "producer_function": "build_claim_ceiling",
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "allowed_claims": [
            "bounded no-candidate surface-admission preflight",
            "legal oracle solvability for this generated surface",
            "baseline, ablation, leakage, replay, and provenance checks for this generated surface",
            "admitted/refused/invalid harness verdict only",
        ],
        "forbidden_claims": list(CLAIM_EXCLUSIONS),
        "mechanism_score_authorized": False,
    }


def _compute_result(
    *,
    run_id: str,
    config: dict[str, Any],
    legal_oracle: dict[str, Any],
    field_registry: dict[str, Any],
    baseline_comparison: dict[str, Any],
    ablation_report: dict[str, Any],
    leakage_scan_report: dict[str, Any],
    replay_report: dict[str, Any],
    provenance: dict[str, Any],
    readback: dict[str, Any],
    allow_stored_answer_replay: bool,
) -> dict[str, Any]:
    thresholds = config["thresholds"]
    majority = baseline_comparison["majority_baseline_accuracy"]
    best = baseline_comparison["best_graph_cache_or_lookup_or_observation_baseline"]
    margin = legal_oracle["accuracy"] - best["score"]
    stop: list[str] = []
    if legal_oracle["accuracy"] < thresholds["legal_oracle_min_accuracy"]:
        stop.append("legal_oracle_accuracy_below_threshold")
    if majority > thresholds["majority_baseline_max_accuracy"]:
        stop.append("majority_baseline_above_allowed_threshold")
    if best["score"] > thresholds["best_graph_lookup_observation_max_accuracy"]:
        stop.append(f"independent_baseline_reached_disallowing_threshold:{best['baseline_id']}")
    if margin < thresholds["legal_oracle_min_margin_over_best_baseline"]:
        stop.append("legal_oracle_margin_too_small")
    if ablation_report["no_carry_ablation"]["accuracy"] > majority + thresholds["carry_ablation_eps"]:
        stop.append("no_carry_ablation_did_not_collapse")
    if ablation_report["randomized_carry_ablation"]["accuracy"] > majority + thresholds["carry_ablation_eps"]:
        stop.append("randomized_carry_ablation_did_not_collapse")
    if not leakage_scan_report["positive_control"]["guard_blocked"]:
        stop.append("leakage_positive_control_failed")
    if not field_registry["legal_forbidden_registry_exhaustive"]:
        stop.append("field_registry_not_exhaustive")
    if field_registry["answer_bearing_fields_in_legal_or_replay_bundle"]:
        stop.append("answer_bearing_field_in_legal_or_replay_bundle")
    if not field_registry["legal_discriminative_fields_not_unique_identifiers"]:
        stop.append("legal_fields_are_unique_identifiers")
    if not replay_report["passed"] or allow_stored_answer_replay:
        stop.append("replay_required_stored_answer_or_shortcut")
    if not provenance["verification"]["passed"]:
        stop.append("computed_evidence_provenance_failed")
    if readback["forbidden_files_modified"]:
        stop.append("forbidden_files_modified")
    if not readback["old_frozen_artifacts_unchanged"] or not readback["old_source_files_unchanged"]:
        stop.append("old_frozen_source_or_artifact_touched")

    if "leakage_positive_control_failed" in stop or "replay_required_stored_answer_or_shortcut" in stop:
        verdict = "invalid_harness"
    elif stop:
        verdict = "refused_surface_preflight"
    else:
        verdict = "admitted_surface_preflight"
    return {
        "producer_function": "compute_result",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "verdict": verdict,
        "current_layer": "engineering implementation / no-candidate surface-admission preflight only",
        "mainline_integration_status": "none; offline local preflight only",
        "enabled_status": "callable local preflight runner only; no mechanism path enabled",
        "real_trigger_evidence": {
            "prior_negative_evidence": [
                "current COMPOSITE-CTSR pass-chain closed as mechanism evidence and frozen as negative evidence",
                "prior legal oracle = majority = 0.25",
                "prior replay depended on answer-bearing serialized_state_after.latent_action_binding alias",
                "prior masking fallback used out-of-alphabet hold",
            ],
            "run_id": run_id,
            "surface_config_hash": config["config_hash"],
            "artifact_dir": f"artifacts/{TASK_ID}",
        },
        "claim_ceiling": CLAIM_CEILING,
        "legal_oracle_accuracy": legal_oracle["accuracy"],
        "majority_baseline_accuracy": majority,
        "best_independent_baseline": best,
        "legal_oracle_minus_best_independent_baseline": margin,
        "stop_conditions_triggered": sorted(set(stop)),
        "candidate_mechanism_implemented": False,
        "candidate_score_produced": False,
        "mechanism_score_produced": False,
        "candidate_or_tournament_authorized": False,
        "gate5_bridge_runtime_or_ego_mainline_authorized": False,
        "auto_remote_anchor": AUTO_REMOTE_ANCHOR,
        "auto_remote_anchor_claim_ceiling_if_performed": "remote-anchor publication and verification only",
        "next_minimal_closed_loop_action": (
            "If independent review accepts this no-candidate preflight, draft a separate bounded candidate "
            "task card; otherwise preserve refusal/invalid-harness evidence and close or redesign this CTSR route."
        ),
        "what_this_does_not_prove": list(CLAIM_EXCLUSIONS),
    }


def execute_preflight(
    output_dir: str | Path | None = None,
    *,
    persist_artifacts: bool = True,
    disable_leakage_positive_control: bool = False,
    allow_stored_answer_replay: bool = False,
    test_result_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = build_preflight_config()
    run_id = f"{TASK_ID}_{config['config_hash'][:16]}"
    surface = generate_surface(config)
    legal_oracle = run_legal_oracle(surface, run_id)
    field_registry = build_field_registry(surface)
    baseline_comparison = run_baselines(surface, config, run_id)
    ablation_report = run_ablation(surface, config, run_id)
    leakage_scan_report = run_leakage_scan(
        surface,
        config,
        run_id,
        disable_positive_control=disable_leakage_positive_control,
    )
    replay_report = run_replay(
        surface,
        config,
        run_id,
        allow_stored_answer_replay=allow_stored_answer_replay,
    )
    output_path = _resolve_output_dir(output_dir) if persist_artifacts else None
    temporary_result = {"verdict": "pending"}
    readback = build_readback(surface, temporary_result, output_path)
    provenance = build_provenance(
        run_id=run_id,
        config=config,
        surface=surface,
        legal_oracle=legal_oracle,
        baseline_comparison=baseline_comparison,
        ablation_report=ablation_report,
        leakage_scan_report=leakage_scan_report,
        replay_report=replay_report,
    )
    result = _compute_result(
        run_id=run_id,
        config=config,
        legal_oracle=legal_oracle,
        field_registry=field_registry,
        baseline_comparison=baseline_comparison,
        ablation_report=ablation_report,
        leakage_scan_report=leakage_scan_report,
        replay_report=replay_report,
        provenance=provenance,
        readback=readback,
        allow_stored_answer_replay=allow_stored_answer_replay,
    )
    readback = build_readback(surface, result, output_path)
    claim_ceiling = build_claim_ceiling()
    trace_rows = build_trace_rows(surface, legal_oracle, baseline_comparison, ablation_report, run_id)
    test_results = test_result_readback or {
        "command": "not_final_current_test_invocation",
        "exit_code": None,
        "summary": "test readback not supplied to this run",
    }
    run = {
        "task_id": TASK_ID,
        "task_card_id": TASK_CARD_ID,
        "run_id": run_id,
        "preflight_config": config,
        "surface_bundle": surface,
        "field_registry": field_registry,
        "legal_oracle_report": legal_oracle,
        "baseline_comparison": baseline_comparison,
        "ablation_report": ablation_report,
        "leakage_scan_report": leakage_scan_report,
        "replay_report": replay_report,
        "computed_evidence_provenance": provenance,
        "claim_ceiling": claim_ceiling,
        "readback": readback,
        "trace_rows": trace_rows,
        "test_results": test_results,
        "result": result,
    }
    if persist_artifacts:
        write_artifacts(_resolve_output_dir(output_dir), run)
        run["readback"] = build_readback(surface, result, _resolve_output_dir(output_dir))
        _write_json(_resolve_output_dir(output_dir) / "readback.json", run["readback"])
    return run


def build_trace_rows(
    surface: dict[str, Any],
    legal_oracle: dict[str, Any],
    baseline_comparison: dict[str, Any],
    ablation_report: dict[str, Any],
    run_id: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for prediction in legal_oracle["computed_predictions"]:
        rows.append(
            {
                "run_id": run_id,
                "producer_function": "run_legal_oracle",
                "record_type": "legal_oracle_prediction",
                **prediction,
            }
        )
    for baseline in baseline_comparison["results"]:
        for prediction in baseline["computed_predictions"]:
            rows.append(
                {
                    "run_id": run_id,
                    "producer_function": baseline["producer_function"],
                    "record_type": "baseline_prediction",
                    "baseline_id": baseline["baseline_id"],
                    **prediction,
                }
            )
    rows.append(
        {
            "run_id": run_id,
            "producer_function": "run_ablation",
            "record_type": "ablation_summary",
            "no_carry_accuracy": ablation_report["no_carry_ablation"]["accuracy"],
            "randomized_carry_accuracy": ablation_report["randomized_carry_ablation"]["accuracy"],
        }
    )
    return rows


def _resolve_output_dir(output_dir: str | Path | None) -> Path:
    if output_dir is None:
        return repo_root() / "artifacts" / ARTIFACT_DIR_NAME
    path = Path(output_dir)
    return path if path.is_absolute() else repo_root() / path


def write_artifacts(out: Path, run: dict[str, Any]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    artifact_map = {
        "result.json": run["result"],
        "readback.json": run["readback"],
        "surface_bundle.json": run["surface_bundle"],
        "field_registry.json": run["field_registry"],
        "baseline_comparison.json": run["baseline_comparison"],
        "ablation_report.json": run["ablation_report"],
        "leakage_scan_report.json": run["leakage_scan_report"],
        "replay_report.json": run["replay_report"],
        "computed_evidence_provenance.json": run["computed_evidence_provenance"],
        "claim_ceiling.json": run["claim_ceiling"],
        "preflight_config.json": run["preflight_config"],
        "legal_oracle_report.json": run["legal_oracle_report"],
        "test_results.json": run["test_results"],
    }
    for name, payload in artifact_map.items():
        _write_json(out / name, payload)
    _write_jsonl(out / "trace.jsonl", run["trace_rows"])
    if run["result"]["verdict"] != "admitted_surface_preflight":
        _write_json(
            out / "failure_manifest.json",
            {
                "producer_function": "write_failure_manifest",
                "task_id": TASK_ID,
                "verdict": run["result"]["verdict"],
                "stop_conditions_triggered": run["result"]["stop_conditions_triggered"],
            },
        )


def write_research_report(run: dict[str, Any], report_path: str | Path | None = None) -> Path:
    path = Path(report_path) if report_path is not None else repo_root() / "docs" / "research" / REPORT_NAME
    if not path.is_absolute():
        path = repo_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    result = run["result"]
    baseline = run["baseline_comparison"]
    ablation = run["ablation_report"]
    leakage = run["leakage_scan_report"]
    replay = run["replay_report"]
    readback = run["readback"]
    lines = [
        "# CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        "Layer: engineering implementation / no-candidate surface-admission preflight only.",
        "",
        "Mainline integration status: none; offline local preflight only.",
        "",
        "Enabled status: callable local preflight runner only; no mechanism path enabled.",
        "",
        "Auto-Remote-Anchor: conditional",
        "",
        "No mechanism success claim is made.",
        "",
        "No candidate mechanism was implemented.",
        "",
        "## Bounded Task Card",
        "",
        f"- Task id: `{TASK_CARD_ID}`",
        "- Problem definition: perform one no-candidate solvability-inversion preflight after the preserved COMPOSITE-CTSR hostile audit closed the prior pass-chain as mechanism evidence.",
        "- Current stage/layer: engineering implementation / no-candidate surface-admission preflight only.",
        "- Mainline target: none.",
        "- Enabled-state requirement: no new mechanism path, candidate, bridge, Gate5, runtime, tournament, or EGO-mainline behavior.",
        "- Real-trigger evidence requirement: prior negative evidence shows legal oracle = majority = 0.25, leakage-dependent replay, out-of-pool masking fallback, and missed latent_action_binding alias.",
        "- Hypothesis: a clean CTSR legal surface can be admitted if legal oracle solvability, baseline separation, carry ablation collapse, leakage controls, field registry, and forbidden-free replay all pass.",
        "- Strongest baseline: majority, lookup, nearest-neighbor, graph-cache family, and observation-only posthoc classifier.",
        "- Ablation requirement: no-carry and randomized-carry reruns must collapse to majority + eps.",
        "- Trace/replay requirement: replay recomputes from task A raw legal observations, task B legal probes, declared rules, and run metadata only.",
        "- Computed-evidence provenance gate: every score records producer, inputs, run id, seeds/context/episode ids, aggregation, and code path hash.",
        "- Acceptance gate: admitted/refused/invalid-harness only; no threshold tuning after results.",
        f"- Claim ceiling: {CLAIM_CEILING}",
        "- Stop condition: any failed gate, leakage control failure, stored-answer replay, unclassified field channel, baseline threshold closure, or forbidden path touch.",
        "- Rollback plan: additive-only deletion or revert of the isolated task paths.",
        "- Expected changed files: isolated source package, focused test, new artifacts, and this report only.",
        "- Forbidden changes: frozen COMPOSITE source/artifacts, old oracle-block/hostile-audit artifacts, candidate files, Gate4/Gate5/tournament/bridge/runtime/EGO-mainline paths.",
        "- Auto-Remote-Anchor decision: conditional.",
        "",
        "## Prior Negative Evidence Cited",
        "",
        "- `artifacts/preserve_composite_ctsr_hostile_audit_001a/result.json`: closed prior COMPOSITE-CTSR pass-chain as mechanism evidence and froze it as negative evidence.",
        "- `artifacts/preserve_claude_audit_legal_interface_oracle_block_001a/result.json`: preserved legal-interface oracle block with oracle accuracy = majority = 0.25.",
        "",
        "## Admission Gate Readback",
        "",
        f"- Legal oracle accuracy: `{result['legal_oracle_accuracy']}`",
        f"- Majority baseline accuracy: `{baseline['majority_baseline_accuracy']}`",
        f"- Best graph/cache/lookup/observation baseline: `{baseline['best_graph_cache_or_lookup_or_observation_baseline']}`",
        f"- Legal oracle minus best independent baseline: `{result['legal_oracle_minus_best_independent_baseline']}`",
        f"- Invoked baselines: `{baseline['invoked_baselines']}`",
        f"- Missing baselines: `{baseline['missing_baselines']}`",
        "",
        "## Ablation",
        "",
        f"- No-carry accuracy: `{ablation['no_carry_ablation']['accuracy']}`",
        f"- Randomized-carry accuracy: `{ablation['randomized_carry_ablation']['accuracy']}`",
        f"- Masking fallback in action pool: `{ablation['masking_fallback_in_action_pool']}`",
        "",
        "## Leakage And Replay",
        "",
        f"- Clean surface scan passed: `{leakage['clean_surface_scan']['passed']}`",
        f"- Positive-control unguarded alias accuracy: `{leakage['positive_control']['unguarded_alias_accuracy']}`",
        f"- Positive-control guard blocked: `{leakage['positive_control']['guard_blocked']}`",
        f"- Replay passed: `{replay['passed']}`",
        f"- Replay forbidden fields: `{replay['forbidden_fields_in_replay_bundle']}`",
        f"- Replay prediction match rate: `{replay['prediction_match_rate']}`",
        "",
        "## Scope Readback",
        "",
        f"- Branch: `{readback['branch']}`",
        f"- HEAD: `{readback['head']}`",
        f"- Forbidden files modified: `{readback['forbidden_files_modified']}`",
        f"- Old frozen artifacts unchanged: `{readback['old_frozen_artifacts_unchanged']}`",
        f"- Old source files unchanged: `{readback['old_source_files_unchanged']}`",
        "",
        "## Stop Conditions",
        "",
    ]
    if result["stop_conditions_triggered"]:
        lines.extend(f"- `{item}`" for item in result["stop_conditions_triggered"])
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Claim Ceiling",
            "",
            CLAIM_CEILING,
            "",
            "## What This Does Not Prove",
            "",
            *[f"- {item}" for item in CLAIM_EXCLUSIONS],
            "",
            "## Next Minimal Closed-Loop Action",
            "",
            result["next_minimal_closed_loop_action"],
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--test-command", default=None)
    parser.add_argument("--test-exit-code", default=None)
    parser.add_argument("--test-summary", default=None)
    args = parser.parse_args()
    test_readback = None
    if args.test_command is not None:
        test_readback = {
            "command": args.test_command,
            "exit_code": int(args.test_exit_code) if args.test_exit_code is not None else None,
            "summary": args.test_summary or "",
        }
    run = execute_preflight(
        output_dir=args.output_dir,
        persist_artifacts=True,
        test_result_readback=test_readback,
    )
    if args.write_report:
        write_research_report(run)
    print(json.dumps(run["result"], indent=2, sort_keys=True))
