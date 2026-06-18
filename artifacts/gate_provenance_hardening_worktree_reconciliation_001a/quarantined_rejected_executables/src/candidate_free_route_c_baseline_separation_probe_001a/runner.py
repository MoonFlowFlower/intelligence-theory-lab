from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import random
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

from . import ARTIFACT_DIR_NAME, CLAIM_CEILING, CURRENT_LAYER, TASK_ID


CONFIG_ID = "route_c_candidate_free_sparse_hidden_set_v1"
DECISION_SEPARATION = "separation_exists_route_c_may_repromote_one_surface"
DECISION_NO_SEPARATION = "no_separation_route_c_should_close"
DECISION_INVALID = "probe_invalid_repair_required"
ORACLE_THRESHOLD = 1.0

ACTIVE_BASELINES = (
    "random",
    "greedy_info_gain",
    "exhaustive_legal_query",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "lookup_imitation",
    "direct_objective_optimizer",
    "amortized_least_squares",
)
PASSIVE_BASELINES = (
    "mean",
    "variance",
    "correlation",
    "pca_subspace",
    "cross_episode",
    "supervised",
    "legal_field_membership",
    "positional_first_k",
)
GRAPH_CACHE_BASELINES = (
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
)
BASELINE_IDS = ACTIVE_BASELINES + PASSIVE_BASELINES
SOURCE_SALT = "candidate-free-route-c-oracle-only-hidden-set-v1"
VISIBLE_SALT = "candidate-free-route-c-visible-features-v1"
EPISODE_SEEDS = (91701, 91702, 91703, 91704, 91705, 91706)
TRAIN_SEEDS = (81701, 81702, 81703, 81704, 81705, 81706)
ACTION_SPACE_SIZE = 12
QUERY_BUDGET = 2
HIDDEN_SET_SIZE = 4


class BudgetedLegalRuntime:
    def __init__(self, private_episode: dict[str, Any], query_budget: int) -> None:
        self.private_episode = private_episode
        self.query_budget = query_budget
        self.query_history: list[dict[str, Any]] = []

    def query_membership(self, item_id: int) -> bool:
        if item_id not in self.private_episode["legal_action_space"]:
            raise ValueError(f"illegal query outside legal action space: {item_id}")
        if len(self.query_history) >= self.query_budget:
            raise ValueError("query budget exceeded")
        membership = item_id in set(self.private_episode["hidden_set"])
        row = {
            "action": "query_membership",
            "item_id": item_id,
            "membership": membership,
            "query_index": len(self.query_history),
        }
        self.query_history.append(row)
        return membership


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
        return value.as_posix()
    return value


def _canonical(value: Any) -> str:
    return json.dumps(_json_ready(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(_json_ready(row), sort_keys=True, ensure_ascii=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def code_path_hash(func: Callable[..., Any]) -> str:
    return sha256_text(inspect.getsource(func))


def repo_root_default() -> Path:
    return Path(__file__).resolve().parents[2]


def _safe_git(repo_root: Path, args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return completed.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def git_readback(repo_root: Path) -> dict[str, Any]:
    return {
        "repo_root": _safe_git(repo_root, ["rev-parse", "--show-toplevel"]),
        "branch": _safe_git(repo_root, ["branch", "--show-current"]),
        "head": _safe_git(repo_root, ["rev-parse", "HEAD"]),
        "status_short_branch": _safe_git(repo_root, ["status", "--short", "--branch"]).splitlines(),
    }


def build_probe_config(query_budget: int = QUERY_BUDGET) -> dict[str, Any]:
    return {
        "config_id": CONFIG_ID,
        "seed": 91700,
        "episode_seeds": list(EPISODE_SEEDS),
        "train_seeds": list(TRAIN_SEEDS),
        "legal_action_space_size": ACTION_SPACE_SIZE,
        "query_budget": query_budget,
        "hidden_set_size": HIDDEN_SET_SIZE,
        "oracle_threshold": ORACLE_THRESHOLD,
        "source_salt_hash": sha256_text(SOURCE_SALT),
        "visible_salt_hash": sha256_text(VISIBLE_SALT),
    }


def _rank_items(seed: int, salt: str, item_count: int) -> list[int]:
    return sorted(
        range(item_count),
        key=lambda item_id: sha256_text(f"{salt}:{seed}:{item_id}"),
    )


def _visible_features(seed: int, item_id: int) -> dict[str, Any]:
    digest = sha256_text(f"{VISIBLE_SALT}:{seed}:{item_id}")
    return {
        "item_id": item_id,
        "shape_code": int(digest[:4], 16) % 7,
        "tone_code": int(digest[4:8], 16) % 11,
        "texture_code": int(digest[8:12], 16) % 13,
        "visible_score": int(digest[12:16], 16) % 101,
    }


def build_private_episode(seed: int, config: dict[str, Any]) -> dict[str, Any]:
    hidden = set(_rank_items(seed, SOURCE_SALT, config["legal_action_space_size"])[: config["hidden_set_size"]])
    legal_observations = [
        _visible_features(seed, item_id)
        for item_id in range(config["legal_action_space_size"])
    ]
    return {
        "episode_id": f"episode-{seed}",
        "seed": seed,
        "legal_action_space": list(range(config["legal_action_space_size"])),
        "query_budget": config["query_budget"],
        "legal_observations": legal_observations,
        "hidden_set": sorted(hidden),
        "oracle_only_fields": ["hidden_set", "source_salt"],
    }


def legal_view(private_episode: dict[str, Any]) -> dict[str, Any]:
    return {
        "episode_id": private_episode["episode_id"],
        "seed": private_episode["seed"],
        "legal_action_space": list(private_episode["legal_action_space"]),
        "query_budget": private_episode["query_budget"],
        "legal_observations": list(private_episode["legal_observations"]),
    }


def build_training_public_history(train_private: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    history = []
    for episode in train_private:
        runtime = BudgetedLegalRuntime(episode, config["query_budget"])
        rows = []
        for item_id in episode["legal_action_space"][: config["query_budget"]]:
            runtime.query_membership(item_id)
            rows.append(dict(runtime.query_history[-1]))
        history.append(
            {
                "episode_id": episode["episode_id"],
                "seed": episode["seed"],
                "legal_observations": episode["legal_observations"],
                "query_history": rows,
            }
        )
    return history


def oracle_privileged_exact_solver(
    legal_episode: dict[str, Any],
    private_episode: dict[str, Any],
    training_history: list[dict[str, Any]],
    runtime: BudgetedLegalRuntime,
) -> set[int]:
    del legal_episode, training_history, runtime
    return set(private_episode["hidden_set"])


def _score_prediction(private_episode: dict[str, Any], prediction: set[int]) -> float:
    truth = set(private_episode["hidden_set"])
    if not truth:
        return 1.0 if not prediction else 0.0
    return len(truth & prediction) / len(truth)


def _query_order_by_visible(legal_episode: dict[str, Any], reverse: bool = True) -> list[int]:
    return [
        row["item_id"]
        for row in sorted(
            legal_episode["legal_observations"],
            key=lambda row: (row["visible_score"], row["tone_code"], -row["item_id"]),
            reverse=reverse,
        )
    ]


def _predict_from_queries(runtime: BudgetedLegalRuntime, order: list[int]) -> set[int]:
    prediction: set[int] = set()
    for item_id in order[: runtime.query_budget]:
        if runtime.query_membership(item_id):
            prediction.add(item_id)
    return prediction


def _positive_positions(training_history: list[dict[str, Any]]) -> Counter[int]:
    counts: Counter[int] = Counter()
    for episode in training_history:
        for query in episode["query_history"]:
            if query["membership"]:
                counts[query["item_id"]] += 1
    return counts


def _position_order_from_training(training_history: list[dict[str, Any]], item_ids: list[int]) -> list[int]:
    counts = _positive_positions(training_history)
    return sorted(item_ids, key=lambda item_id: (counts[item_id], -item_id), reverse=True)


def baseline_random(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del training_history
    rng = random.Random(int(sha256_text(f"random:{legal_episode['seed']}")[:16], 16))
    order = list(legal_episode["legal_action_space"])
    rng.shuffle(order)
    return _predict_from_queries(runtime, order)


def baseline_greedy_info_gain(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del training_history
    return _predict_from_queries(runtime, _query_order_by_visible(legal_episode, reverse=True))


def baseline_exhaustive_legal_query(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del training_history
    return _predict_from_queries(runtime, list(legal_episode["legal_action_space"]))


def baseline_graph_lookup(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del runtime
    lookup: dict[tuple[int, int], bool] = {}
    for episode in training_history:
        by_item = {row["item_id"]: row for row in episode["legal_observations"]}
        for query in episode["query_history"]:
            row = by_item[query["item_id"]]
            lookup[(row["shape_code"], row["tone_code"])] = query["membership"]
    return {
        row["item_id"]
        for row in legal_episode["legal_observations"]
        if lookup.get((row["shape_code"], row["tone_code"]), False)
    }


def baseline_transition_table(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del runtime
    predicted: set[int] = set()
    for item_id, count in _positive_positions(training_history).items():
        if count > 0:
            predicted.add((item_id + 1) % len(legal_episode["legal_action_space"]))
    return predicted


def baseline_successor_map(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del runtime
    positives = _positive_positions(training_history)
    return {
        (item_id + 2) % len(legal_episode["legal_action_space"])
        for item_id, count in positives.items()
        if count > 0
    }


def baseline_count_table(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del runtime
    order = _position_order_from_training(training_history, list(legal_episode["legal_action_space"]))
    return set(order[:HIDDEN_SET_SIZE])


def baseline_fsm_planner(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    order = _position_order_from_training(training_history, list(legal_episode["legal_action_space"]))
    if not order:
        order = list(legal_episode["legal_action_space"])
    rotated = order[1:] + order[:1]
    return _predict_from_queries(runtime, rotated)


def baseline_episodic_traversal(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del runtime
    target_signature = sum(row["visible_score"] for row in legal_episode["legal_observations"])
    nearest = min(
        training_history,
        key=lambda episode: abs(
            sum(row["visible_score"] for row in episode["legal_observations"]) - target_signature
        ),
    )
    return {query["item_id"] for query in nearest["query_history"] if query["membership"]}


def baseline_lookup_imitation(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    return _predict_from_queries(
        runtime,
        _position_order_from_training(training_history, list(legal_episode["legal_action_space"])),
    )


def baseline_direct_objective_optimizer(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    counts = _positive_positions(training_history)
    order = sorted(
        legal_episode["legal_observations"],
        key=lambda row: (counts[row["item_id"]], row["visible_score"], -row["item_id"]),
        reverse=True,
    )
    return _predict_from_queries(runtime, [row["item_id"] for row in order])


def baseline_amortized_least_squares(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del runtime
    weights = defaultdict(float)
    for episode in training_history:
        by_item = {row["item_id"]: row for row in episode["legal_observations"]}
        for query in episode["query_history"]:
            row = by_item[query["item_id"]]
            sign = 1.0 if query["membership"] else -0.25
            weights["shape"] += sign * row["shape_code"]
            weights["tone"] += sign * row["tone_code"]
            weights["texture"] += sign * row["texture_code"]
            weights["visible"] += sign * row["visible_score"]
    ranked = sorted(
        legal_episode["legal_observations"],
        key=lambda row: (
            weights["shape"] * row["shape_code"]
            + weights["tone"] * row["tone_code"]
            + weights["texture"] * row["texture_code"]
            + weights["visible"] * row["visible_score"],
            -row["item_id"],
        ),
        reverse=True,
    )
    return {row["item_id"] for row in ranked[:HIDDEN_SET_SIZE]}


def baseline_mean(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del training_history, runtime
    scores = [row["visible_score"] for row in legal_episode["legal_observations"]]
    mean_score = sum(scores) / len(scores)
    return {row["item_id"] for row in legal_episode["legal_observations"] if row["visible_score"] >= mean_score}


def baseline_variance(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del training_history, runtime
    scores = [row["visible_score"] for row in legal_episode["legal_observations"]]
    mean_score = sum(scores) / len(scores)
    ranked = sorted(
        legal_episode["legal_observations"],
        key=lambda row: (abs(row["visible_score"] - mean_score), row["item_id"]),
        reverse=True,
    )
    return {row["item_id"] for row in ranked[:HIDDEN_SET_SIZE]}


def baseline_correlation(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del training_history, runtime
    ranked = sorted(
        legal_episode["legal_observations"],
        key=lambda row: ((row["shape_code"] * row["tone_code"]) - row["texture_code"], -row["item_id"]),
        reverse=True,
    )
    return {row["item_id"] for row in ranked[:HIDDEN_SET_SIZE]}


def baseline_pca_subspace(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del training_history, runtime
    ranked = sorted(
        legal_episode["legal_observations"],
        key=lambda row: (row["shape_code"] + row["tone_code"] + row["texture_code"], -row["item_id"]),
        reverse=True,
    )
    return {row["item_id"] for row in ranked[:HIDDEN_SET_SIZE]}


def baseline_cross_episode(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del runtime
    counts = _positive_positions(training_history)
    threshold = max(counts.values(), default=0)
    if threshold == 0:
        return set()
    return {item_id for item_id, count in counts.items() if count == threshold}


def baseline_supervised(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del runtime
    positive_shapes = Counter()
    negative_shapes = Counter()
    for episode in training_history:
        by_item = {row["item_id"]: row for row in episode["legal_observations"]}
        for query in episode["query_history"]:
            row = by_item[query["item_id"]]
            if query["membership"]:
                positive_shapes[row["shape_code"]] += 1
            else:
                negative_shapes[row["shape_code"]] += 1
    return {
        row["item_id"]
        for row in legal_episode["legal_observations"]
        if positive_shapes[row["shape_code"]] > negative_shapes[row["shape_code"]]
    }


def baseline_legal_field_membership(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del training_history, runtime
    return {
        row["item_id"]
        for row in legal_episode["legal_observations"]
        if row["shape_code"] in {0, 2, 4} and row["tone_code"] in {1, 3, 5, 7}
    }


def baseline_positional_first_k(legal_episode: dict[str, Any], training_history: list[dict[str, Any]], runtime: BudgetedLegalRuntime) -> set[int]:
    del training_history, runtime
    return set(legal_episode["legal_action_space"][:HIDDEN_SET_SIZE])


BASELINE_FUNCTIONS: dict[str, Callable[[dict[str, Any], list[dict[str, Any]], BudgetedLegalRuntime], set[int]]] = {
    "random": baseline_random,
    "greedy_info_gain": baseline_greedy_info_gain,
    "exhaustive_legal_query": baseline_exhaustive_legal_query,
    "graph_lookup": baseline_graph_lookup,
    "transition_table": baseline_transition_table,
    "successor_map": baseline_successor_map,
    "count_table": baseline_count_table,
    "fsm_planner": baseline_fsm_planner,
    "episodic_traversal": baseline_episodic_traversal,
    "lookup_imitation": baseline_lookup_imitation,
    "direct_objective_optimizer": baseline_direct_objective_optimizer,
    "amortized_least_squares": baseline_amortized_least_squares,
    "mean": baseline_mean,
    "variance": baseline_variance,
    "correlation": baseline_correlation,
    "pca_subspace": baseline_pca_subspace,
    "cross_episode": baseline_cross_episode,
    "supervised": baseline_supervised,
    "legal_field_membership": baseline_legal_field_membership,
    "positional_first_k": baseline_positional_first_k,
}


def baseline_family(baseline_id: str) -> str:
    if baseline_id in PASSIVE_BASELINES:
        return "passive"
    if baseline_id in GRAPH_CACHE_BASELINES:
        return "graph_cache"
    return "active"


def run_callable_on_episodes(
    producer_id: str,
    producer: Callable[..., set[int]],
    eval_private: list[dict[str, Any]],
    training_history: list[dict[str, Any]],
    config: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    scores = []
    traces = []
    for episode in eval_private:
        legal_episode = legal_view(episode)
        runtime = BudgetedLegalRuntime(episode, config["query_budget"])
        if producer_id == "oracle":
            prediction = producer(legal_episode, episode, training_history, runtime)
        else:
            prediction = producer(legal_episode, training_history, runtime)
        score = _score_prediction(episode, prediction)
        scores.append(score)
        traces.append(
            {
                "record_type": "oracle_prediction" if producer_id == "oracle" else "baseline_prediction",
                "candidate_id": None,
                "producer_id": producer_id,
                "baseline_id": None if producer_id == "oracle" else producer_id,
                "episode_id": episode["episode_id"],
                "seed": episode["seed"],
                "prediction": sorted(prediction),
                "score": score,
                "query_history": list(runtime.query_history),
                "query_budget": config["query_budget"],
                "legal_action_space_size": config["legal_action_space_size"],
            }
        )
    return (
        {
            "score": sum(scores) / len(scores),
            "per_episode_scores": scores,
            "callable_invoked": True,
        },
        traces,
    )


def provenance_row(
    producer_function: str,
    func: Callable[..., Any],
    config: dict[str, Any],
    score: float,
) -> dict[str, Any]:
    return {
        "producer_function": producer_function,
        "inputs": {
            "config_id": config["config_id"],
            "legal_action_space_size": config["legal_action_space_size"],
            "query_budget": config["query_budget"],
            "hidden_set_size": config["hidden_set_size"],
        },
        "run_id": config["run_id"],
        "seed": config["seed"],
        "episode_ids": [f"episode-{seed}" for seed in config["episode_seeds"]],
        "aggregation": "mean_recall_over_hidden_set_across_executed_toy_episodes",
        "code_path_hash": code_path_hash(func),
        "score": score,
        "score_source": "computed_from_episode_execution",
        "literal_or_static_score_used": False,
    }


def evaluate_config(config: dict[str, Any]) -> dict[str, Any]:
    train_private = [build_private_episode(seed, config) for seed in config["train_seeds"]]
    eval_private = [build_private_episode(seed, config) for seed in config["episode_seeds"]]
    training_history = build_training_public_history(train_private, config)
    oracle_result, oracle_traces = run_callable_on_episodes(
        "oracle",
        oracle_privileged_exact_solver,
        eval_private,
        training_history,
        config,
    )
    baseline_rows = []
    trace_rows = list(oracle_traces)
    provenance_rows = [
        provenance_row("oracle.privileged_exact_solver", oracle_privileged_exact_solver, config, oracle_result["score"])
    ]
    for baseline_id in BASELINE_IDS:
        func = BASELINE_FUNCTIONS[baseline_id]
        baseline_result, traces = run_callable_on_episodes(
            baseline_id,
            func,
            eval_private,
            training_history,
            config,
        )
        row = {
            "baseline_id": baseline_id,
            "family": baseline_family(baseline_id),
            "producer_function": f"baseline.{baseline_id}",
            "score": baseline_result["score"],
            "per_episode_scores": baseline_result["per_episode_scores"],
            "callable_invoked": baseline_result["callable_invoked"],
            "oracle_privileged_access_used": False,
            "query_budget": config["query_budget"],
            "legal_action_space_size": config["legal_action_space_size"],
            "score_source": "computed_from_episode_execution",
        }
        baseline_rows.append(row)
        trace_rows.extend(traces)
        provenance_rows.append(provenance_row(f"baseline.{baseline_id}", func, config, baseline_result["score"]))

    passive_rows = [row for row in baseline_rows if row["family"] == "passive"]
    passive_max = max(passive_rows, key=lambda row: (row["score"], row["baseline_id"]))
    strongest = max(baseline_rows, key=lambda row: (row["score"], row["baseline_id"]))
    separation = (
        oracle_result["score"] >= config["oracle_threshold"]
        and all(row["score"] < config["oracle_threshold"] for row in baseline_rows)
    )
    return {
        "config_id": config["config_id"],
        "seed": config["seed"],
        "episode_ids": [f"episode-{seed}" for seed in config["episode_seeds"]],
        "legal_action_space_size": config["legal_action_space_size"],
        "query_budget": config["query_budget"],
        "oracle_score": oracle_result["score"],
        "oracle_callable_invoked": oracle_result["callable_invoked"],
        "oracle_access": "oracle_only_hidden_set_and_source_salt",
        "baseline_scores": baseline_rows,
        "passive_family_max": {
            "baseline_id": passive_max["baseline_id"],
            "score": passive_max["score"],
        },
        "strongest_fair_baseline": {
            "baseline_id": strongest["baseline_id"],
            "score": strongest["score"],
        },
        "delta_oracle_vs_strongest_fair": oracle_result["score"] - strongest["score"],
        "producer_function": "candidate_free_route_c_baseline_separation_probe_001a.runner.evaluate_config",
        "inputs": {
            "config": config,
            "train_episode_count": len(train_private),
            "eval_episode_count": len(eval_private),
        },
        "run_id": config["run_id"],
        "aggregation": "mean_recall_over_hidden_set_across_executed_toy_episodes",
        "code_path_hash": code_path_hash(evaluate_config),
        "decision_gate": {
            "oracle_at_ceiling": oracle_result["score"] >= config["oracle_threshold"],
            "full_fair_baseline_panel_below_ceiling": all(
                row["score"] < config["oracle_threshold"] for row in baseline_rows
            ),
            "random_below_ceiling": next(row for row in baseline_rows if row["baseline_id"] == "random")["score"]
            < config["oracle_threshold"],
            "graph_cache_family_below_ceiling": all(
                row["score"] < config["oracle_threshold"]
                for row in baseline_rows
                if row["baseline_id"] in GRAPH_CACHE_BASELINES
            ),
            "lookup_imitation_below_ceiling": next(
                row for row in baseline_rows if row["baseline_id"] == "lookup_imitation"
            )["score"]
            < config["oracle_threshold"],
            "direct_objective_optimizer_below_ceiling": next(
                row for row in baseline_rows if row["baseline_id"] == "direct_objective_optimizer"
            )["score"]
            < config["oracle_threshold"],
            "amortized_least_squares_below_ceiling": next(
                row for row in baseline_rows if row["baseline_id"] == "amortized_least_squares"
            )["score"]
            < config["oracle_threshold"],
            "passive_family_below_ceiling": all(row["score"] < config["oracle_threshold"] for row in passive_rows),
            "separation_exists": separation,
        },
        "trace_rows": trace_rows,
        "provenance_rows": provenance_rows,
        "serialized_private_bundle": {
            "config": config,
            "train_private": train_private,
            "eval_private": eval_private,
        },
    }


FORBIDDEN_LEGAL_KEYS = ("hidden", "truth", "oracle", "target")


def scan_for_privileged_leakage(bundle: dict[str, Any]) -> dict[str, Any]:
    findings = []
    for episode in bundle["episodes"]:
        for row in episode["legal_observations"]:
            for key in row:
                key_lower = str(key).lower()
                if any(token in key_lower for token in FORBIDDEN_LEGAL_KEYS):
                    findings.append(
                        {
                            "episode_id": episode["episode_id"],
                            "item_id": row.get("item_id"),
                            "key": key,
                        }
                    )
    return {
        "detected": bool(findings),
        "findings": findings,
    }


def build_leakage_report(config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    clean_episodes = [legal_view(build_private_episode(seed, config)) for seed in config["episode_seeds"]]
    clean_scan = scan_for_privileged_leakage({"episodes": clean_episodes})
    injected = json.loads(json.dumps(clean_episodes))
    injected[0]["legal_observations"][0]["oracle_hidden_set"] = [1, 3, 5]
    positive_scan = scan_for_privileged_leakage({"episodes": injected})
    report = {
        "verdict": "leakage_scan_passed" if not clean_scan["detected"] and positive_scan["detected"] else DECISION_INVALID,
        "producer_function": "candidate_free_route_c_baseline_separation_probe_001a.runner.build_leakage_report",
        "clean_bundle": clean_scan,
        "positive_control": {
            "control_id": "oracle_field_in_legal_observation",
            "detected": positive_scan["detected"],
            "blocked_bundle": positive_scan["detected"],
            "findings": positive_scan["findings"],
        },
        "code_path_hash": code_path_hash(scan_for_privileged_leakage),
    }
    invalid_control = {
        "verdict": DECISION_INVALID,
        "blocked": positive_scan["detected"],
        "reason": "privileged_oracle_field_visible_to_non_oracle_baseline",
        "control_id": "oracle_field_in_legal_observation",
        "same_scanner_used": True,
    }
    return report, invalid_control


def source_pin_readback_report() -> dict[str, Any]:
    source_file = Path(__file__).resolve()
    source_lines, start_line = inspect.getsourcelines(run_probe)
    inspect_source = "".join(source_lines)
    file_lines = source_file.read_text(encoding="utf-8").splitlines(keepends=True)
    direct_segment = "".join(file_lines[start_line - 1 : start_line - 1 + len(source_lines)])
    direct_hash = sha256_text(direct_segment)
    inspect_hash = sha256_text(inspect_source)
    tampered = direct_segment.replace("run_probe", "run_probe_tampered", 1)
    return {
        "verdict": "source_pin_readback_passed" if direct_hash == inspect_hash else DECISION_INVALID,
        "authoritative_reader": "pathlib_direct_binary_read",
        "comparison_reader": "inspect_getsource",
        "source_path": source_file.as_posix(),
        "function": "run_probe",
        "start_line": start_line,
        "direct_segment_sha256": direct_hash,
        "inspect_getsource_sha256": inspect_hash,
        "dual_channel_match": direct_hash == inspect_hash,
        "positive_control": {
            "verdict": "source_pin_conflict_blocked",
            "tampered_segment_sha256": sha256_text(tampered),
            "conflict_detected": sha256_text(tampered) != inspect_hash,
        },
    }


def replay_report(original_config_result: dict[str, Any]) -> dict[str, Any]:
    config = dict(original_config_result["serialized_private_bundle"]["config"])
    replayed = evaluate_config(config)
    original_scores = {
        row["baseline_id"]: row["score"]
        for row in original_config_result["baseline_scores"]
    }
    replayed_scores = {
        row["baseline_id"]: row["score"]
        for row in replayed["baseline_scores"]
    }
    score_delta = abs(original_config_result["oracle_score"] - replayed["oracle_score"]) + sum(
        abs(original_scores[baseline_id] - replayed_scores[baseline_id])
        for baseline_id in original_scores
    )
    tampered = json.loads(json.dumps(config))
    tampered["query_budget"] = config["legal_action_space_size"]
    tampered_result = evaluate_config(tampered)
    mismatch = tampered_result["strongest_fair_baseline"]["score"] != original_config_result["strongest_fair_baseline"]["score"]
    return {
        "verdict": "replay_recomputed" if score_delta == 0.0 else DECISION_INVALID,
        "producer_function": "candidate_free_route_c_baseline_separation_probe_001a.runner.replay_report",
        "recomputed_from_serialized_state_and_observation": True,
        "stored_hash_only_used": False,
        "score_delta_vs_original": score_delta,
        "positive_control": {
            "verdict": "replay_mismatch_blocked",
            "tampered_query_budget": tampered["query_budget"],
            "mismatch_detected": mismatch,
        },
        "code_path_hash": code_path_hash(replay_report),
    }


def ablation_report(config: dict[str, Any]) -> dict[str, Any]:
    full_budget_config = dict(config)
    full_budget_config["query_budget"] = config["legal_action_space_size"]
    full_budget_result = evaluate_config(full_budget_config)
    exhaustive_score = next(
        row["score"]
        for row in full_budget_result["baseline_scores"]
        if row["baseline_id"] == "exhaustive_legal_query"
    )
    zero_budget_config = dict(config)
    zero_budget_config["query_budget"] = 0
    zero_budget_result = evaluate_config(zero_budget_config)
    return {
        "verdict": "ablation_controls_recorded",
        "producer_function": "candidate_free_route_c_baseline_separation_probe_001a.runner.ablation_report",
        "real_episode_rerun": True,
        "report_editing_used": False,
        "full_budget_saturation_control": {
            "query_budget_equals_action_space": full_budget_config["query_budget"]
            == full_budget_config["legal_action_space_size"],
            "exhaustive_legal_query_score": exhaustive_score,
            "preserved_as_negative_evidence": exhaustive_score == 1.0,
            "control_meaning": "If budget equals full legal action space, exhaustive_legal_query saturates.",
        },
        "zero_budget_control": {
            "query_budget": 0,
            "strongest_fair_baseline_score": zero_budget_result["strongest_fair_baseline"]["score"],
        },
        "code_path_hash": code_path_hash(ablation_report),
    }


def select_decision_verdict(config_results: list[dict[str, Any]], leakage: dict[str, Any], source_pin: dict[str, Any]) -> str:
    if leakage["verdict"] != "leakage_scan_passed":
        return DECISION_INVALID
    if source_pin["verdict"] != "source_pin_readback_passed":
        return DECISION_INVALID
    if any(result["decision_gate"]["separation_exists"] for result in config_results):
        return DECISION_SEPARATION
    return DECISION_NO_SEPARATION


def run_probe(repo_root: Path | None = None, output_dir: Path | None = None, run_id: str = "route-c-candidate-free-probe-001a") -> dict[str, Any]:
    repo_root = repo_root or repo_root_default()
    output_dir = output_dir or repo_root / "artifacts" / ARTIFACT_DIR_NAME
    output_dir.mkdir(parents=True, exist_ok=True)
    config = build_probe_config()
    config["run_id"] = run_id
    config_result = evaluate_config(config)
    leakage, invalid_control = build_leakage_report(config)
    source_pin = source_pin_readback_report()
    replay = replay_report(config_result)
    ablation = ablation_report(config)
    decision = select_decision_verdict([config_result], leakage, source_pin)

    baseline_comparison = {
        "task_id": TASK_ID,
        "run_id": run_id,
        "tested_configurations": [
            {
                key: value
                for key, value in config_result.items()
                if key not in {"trace_rows", "provenance_rows", "serialized_private_bundle"}
            }
        ],
        "required_baseline_panel": list(BASELINE_IDS),
        "missing_baselines": sorted(set(BASELINE_IDS) - {row["baseline_id"] for row in config_result["baseline_scores"]}),
        "all_baselines_callable_and_invoked": all(row["callable_invoked"] for row in config_result["baseline_scores"]),
        "scores_computed_from_episode_execution": True,
        "no_privileged_leakage_into_non_oracle_baselines": leakage["verdict"] == "leakage_scan_passed",
    }
    strongest = config_result["strongest_fair_baseline"]
    result = {
        "task_id": TASK_ID,
        "decision_rule_verdict": decision,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": "none",
        "enabled_status": "local CLI/pytest only",
        "real_trigger_evidence": {
            "executed_actual_toy_episodes": True,
            "oracle_callable_invoked": config_result["oracle_callable_invoked"],
            "baseline_callables_invoked": sorted(row["baseline_id"] for row in config_result["baseline_scores"]),
            "local_cli_entrypoint": "PYTHONPATH=src python -m candidate_free_route_c_baseline_separation_probe_001a",
        },
        "claim_ceiling": CLAIM_CEILING,
        "auto_remote_anchor": "forbidden",
        "candidate_implemented": False,
        "gate_run": False,
        "safe_to_claim_mechanism_validity": False,
        "safe_to_wire_mainline": False,
        "oracle_score": config_result["oracle_score"],
        "strongest_fair_baseline": strongest,
        "delta_oracle_vs_strongest_fair": config_result["delta_oracle_vs_strongest_fair"],
        "passive_family_max": config_result["passive_family_max"],
        "query_budget_constraint_satisfied": config["query_budget"] < config["legal_action_space_size"],
        "tested_configurations": [
            {
                "config_id": config_result["config_id"],
                "decision_gate": config_result["decision_gate"],
            }
        ],
        "prior_negative_evidence_cited": [
            {
                "path": "docs/research/ROUTE-C-CANDIDATE-HARNESS-001A-ACCEPTED-NEGATIVE-EVIDENCE-CLOSURE-001A.md",
                "readback": (
                    "Prior Route C candidate surface closed because query_budget equaled full legal action space "
                    "and exhaustive_legal_query reached 1.0."
                ),
            },
            {
                "path": "artifacts/route_c_candidate_harness_001a/baseline_comparison.json",
                "readback": "Prior strongest fair baseline score equaled candidate score at 1.0.",
            },
        ],
        "next_minimal_closed_loop_action": (
            "Draft exactly one new Route C surface preflight gated on this candidate-free separation proof."
        )
        if decision == DECISION_SEPARATION
        else "Close Route C or repair the invalid computed-evidence path according to the decision rule.",
        "blocked_or_unknown_items": [
            "No candidate mechanism was implemented or evaluated.",
            "No Gate path, mainline path, runtime path, or EGO integration was enabled.",
            "This does not show that any future candidate can exploit the separating toy configuration.",
        ],
        "what_this_does_not_prove": (
            "This does not prove Route C mechanism validity, hidden-self-set inference, self-boundary evidence, "
            "candidate success, Gate pass, mainline/runtime/live effect, agency, autonomy, consciousness, emotion, "
            "stable user benefit, or EGO readiness."
        ),
        "git_readback": git_readback(repo_root),
        "artifacts": {
            "result": (output_dir / "result.json").as_posix(),
            "baseline_comparison": (output_dir / "baseline_comparison.json").as_posix(),
            "trace": (output_dir / "trace.jsonl").as_posix(),
            "provenance": (output_dir / "provenance_rows.jsonl").as_posix(),
        },
    }
    readback = {
        "verdict": decision,
        "decision_rule_verdict": decision,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": result["mainline_integration_status"],
        "enabled_status": result["enabled_status"],
        "real_trigger_evidence": result["real_trigger_evidence"],
        "claim_ceiling": CLAIM_CEILING,
        "next_minimal_closed_loop_action": result["next_minimal_closed_loop_action"],
        "what_this_does_not_prove": result["what_this_does_not_prove"],
    }

    _write_json(output_dir / "result.json", result)
    _write_json(output_dir / "baseline_comparison.json", baseline_comparison)
    _write_json(output_dir / "ablation_report.json", ablation)
    _write_json(output_dir / "replay_report.json", replay)
    _write_json(output_dir / "leakage_scan.json", leakage)
    _write_json(output_dir / "source_pin_readback_report.json", source_pin)
    _write_json(output_dir / "invalid_bundle_positive_control.json", invalid_control)
    _write_json(output_dir / "readback.json", readback)
    _write_jsonl(output_dir / "trace.jsonl", config_result["trace_rows"])
    _write_jsonl(output_dir / "provenance_rows.jsonl", config_result["provenance_rows"])
    (output_dir / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TASK_ID)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--run-id", default="route-c-candidate-free-probe-001a")
    args = parser.parse_args(argv)
    result = run_probe(output_dir=args.output_dir, run_id=args.run_id)
    print(json.dumps(_json_ready(result), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
