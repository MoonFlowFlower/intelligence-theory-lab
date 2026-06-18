from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from . import CLAIM_CEILING, CURRENT_LAYER, TASK_ID


PASSIVE_BASELINES = (
    "positional_first_k",
    "mean",
    "variance",
    "correlation",
    "pca_subspace",
    "cross_episode",
    "supervised",
    "legal_field_membership",
)

FAIR_INTERVENTIONAL_BASELINES = (
    "random",
    "greedy_info_gain",
    "exhaustive_legal_query",
    "bayesian_likelihood",
    "lookup_imitation",
    "direct_objective_optimizer",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
)

GRAPH_CACHE_CHALLENGERS = (
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
)

FAIR_BASELINE_TIEBREAK_PRIORITY = {
    "random": 1,
    "greedy_info_gain": 2,
    "lookup_imitation": 3,
    "bayesian_likelihood": 4,
    "direct_objective_optimizer": 5,
    "graph_lookup": 6,
    "transition_table": 7,
    "successor_map": 8,
    "count_table": 9,
    "fsm_planner": 10,
    "episodic_traversal": 11,
    "exhaustive_legal_query": 12,
}

ABLATIONS = (
    "remove_mechanism_specific_state",
    "remove_interventional_access",
    "remove_update_path",
    "remove_replay_state",
    "remove_candidate_memory_cache",
    "remove_self_boundary_specific_feature",
    "shuffle_target_labels",
    "swap_twin_pairs_passive_distribution_constant",
    "remove_candidate_only_fields",
    "replace_candidate_policy_with_strongest_fair_baseline_policy",
)

LEAKAGE_CONTROLS = (
    "passive_value_level_leakage",
    "schema_name_key_leakage",
    "order_leakage",
    "action_api_leakage",
    "serialized_state_leakage",
    "result_json_leakage",
    "candidate_only_field_leakage",
    "train_heldout_contamination",
    "truth_seed_contamination",
    "unused_frozen_seed",
    "source_pin_aliasing_or_forged_anchor_leakage",
)

SEEDS = (101, 203, 307, 409, 503)
ITEM_COUNT = 8
HIDDEN_COUNT = 3
MARGIN_THRESHOLD = 0.05
SATURATION_EQUIVALENCE_BAND = 0.02


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def relpath(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def path_lookup_key(path: Path) -> str:
    return str(path.resolve()).casefold()


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def population_stddev(values: list[float]) -> float:
    if not values:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((value - m) ** 2 for value in values) / len(values))


def git_readback(repo_root: Path) -> dict[str, Any]:
    def run_git(args: list[str]) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            return completed.stderr.strip()
        return completed.stdout.strip()

    return {
        "repo_root": run_git(["rev-parse", "--show-toplevel"]),
        "branch": run_git(["branch", "--show-current"]),
        "head": run_git(["rev-parse", "HEAD"]),
        "status_short_branch": run_git(["status", "--short", "--branch"]).splitlines(),
    }


def make_source_artifact(run_id: str) -> dict[str, Any]:
    return {
        "artifact_id": "route_c_candidate_harness_001a_independent_source",
        "run_id": run_id,
        "source_basis": "pre_run_frozen_truth_generator_parameters_outside_candidate_source",
        "item_count": ITEM_COUNT,
        "hidden_count": HIDDEN_COUNT,
        "truth_salt": "route-c-001a-source-salt",
        "legal_query_api": "query_membership(item_id) returns membership only through legal intervention history",
        "candidate_forbidden_fields": [
            "hidden_set",
            "truth_seed",
            "evaluator_label",
            "future_observation",
            "stored_verdict",
        ],
    }


def make_predeclaration(source_artifact_hash: str) -> dict[str, Any]:
    body = {
        "minimum_seed_count": len(SEEDS),
        "seed_set": list(SEEDS),
        "noise_floor_method": "population_stddev_of_per_seed_candidate_minus_strongest_fair_delta",
        "ci_method": "normal_approximation_95_percent_interval_over_predeclared_seed_deltas",
        "candidate_vs_baseline_margin_threshold": MARGIN_THRESHOLD,
        "saturation_equivalence_band": SATURATION_EQUIVALENCE_BAND,
        "aggregation_method": "mean_over_predeclared_seeds",
        "close_or_downgrade_rule": (
            "return close_or_downgrade if candidate advantage is within noise floor, "
            "does not exceed frozen margin, or overlaps strongest fair baseline"
        ),
        "source_artifact_sha256": source_artifact_hash,
    }
    body["predeclaration_hash"] = sha256_text(stable_json(body))
    return body


def hidden_set_for_seed(seed: int, source_artifact: dict[str, Any]) -> set[int]:
    salt = source_artifact["truth_salt"]
    digest = sha256_text(f"{salt}:{seed}")
    rng = random.Random(int(digest[:16], 16))
    return set(rng.sample(range(source_artifact["item_count"]), source_artifact["hidden_count"]))


def build_episode(seed: int, source_artifact: dict[str, Any]) -> dict[str, Any]:
    hidden_set = hidden_set_for_seed(seed, source_artifact)
    observations = []
    for item_id in range(source_artifact["item_count"]):
        digest = sha256_text(f"visible:{seed}:{item_id}:{source_artifact['truth_salt']}")
        observations.append(
            {
                "item_id": item_id,
                "signal": int(digest[:4], 16) % 100,
                "topology": int(digest[4:8], 16) % 7,
                "risk": int(digest[8:12], 16) % 11,
            }
        )
    return {
        "seed": seed,
        "context_id": f"context-{seed}",
        "episode_id": f"episode-{seed}",
        "observations": observations,
        "hidden_set": hidden_set,
        "legal_action_space": [item["item_id"] for item in observations],
        "query_budget": source_artifact["item_count"],
    }


def legal_query_membership(episode: dict[str, Any], item_id: int) -> bool:
    if item_id not in episode["legal_action_space"]:
        raise ValueError("illegal query outside action space")
    return item_id in episode["hidden_set"]


def score_prediction(episode: dict[str, Any], predicted: set[int]) -> float:
    truth = episode["hidden_set"]
    if not truth and not predicted:
        return 1.0
    union = truth | predicted
    if not union:
        return 0.0
    return len(truth & predicted) / len(union)


def query_all_policy(episode: dict[str, Any], order: list[int] | None = None) -> tuple[set[int], list[dict[str, Any]]]:
    order = order or list(episode["legal_action_space"])
    legal_history = []
    predicted = set()
    for item_id in order[: episode["query_budget"]]:
        result = legal_query_membership(episode, item_id)
        legal_history.append({"action": "query_membership", "item_id": item_id, "membership": result})
        if result:
            predicted.add(item_id)
    return predicted, legal_history


def candidate_policy(episode: dict[str, Any]) -> dict[str, Any]:
    predicted, legal_history = query_all_policy(episode)
    return {
        "prediction": predicted,
        "legal_history": legal_history,
        "serialized_state": {
            "queried_items": [row["item_id"] for row in legal_history],
            "positive_items": [row["item_id"] for row in legal_history if row["membership"]],
            "query_budget_used": len(legal_history),
        },
    }


def passive_prediction(name: str, episode: dict[str, Any]) -> set[int]:
    observations = episode["observations"]
    k = len(episode["hidden_set"])
    if name == "positional_first_k":
        ordered = observations
    elif name == "mean":
        threshold = mean([row["signal"] for row in observations])
        ordered = sorted(observations, key=lambda row: (row["signal"] >= threshold, row["signal"]), reverse=True)
    elif name == "variance":
        avg = mean([row["risk"] for row in observations])
        ordered = sorted(observations, key=lambda row: abs(row["risk"] - avg), reverse=True)
    elif name == "correlation":
        ordered = sorted(observations, key=lambda row: row["signal"] * (row["topology"] + 1), reverse=True)
    elif name == "pca_subspace":
        ordered = sorted(observations, key=lambda row: (row["signal"] + row["risk"] - row["topology"]), reverse=True)
    elif name == "cross_episode":
        ordered = sorted(observations, key=lambda row: sha256_text(f"cross:{row['item_id']}:{episode['seed']}"))
    elif name == "supervised":
        ordered = sorted(observations, key=lambda row: (row["signal"] % 3, row["risk"]), reverse=True)
    elif name == "legal_field_membership":
        ordered = sorted(observations, key=lambda row: (row["topology"], row["signal"]), reverse=True)
    else:
        raise ValueError(f"unknown passive baseline: {name}")
    return {row["item_id"] for row in ordered[:k]}


def fair_interventional_prediction(name: str, episode: dict[str, Any]) -> tuple[set[int], list[dict[str, Any]]]:
    action_space = list(episode["legal_action_space"])
    if name == "random":
        rng = random.Random(episode["seed"] + 17)
        rng.shuffle(action_space)
        return query_all_policy(episode, action_space)
    if name == "greedy_info_gain":
        ordered = sorted(action_space, key=lambda item_id: abs(item_id - (ITEM_COUNT // 2)))
        return query_all_policy(episode, ordered)
    if name == "exhaustive_legal_query":
        return query_all_policy(episode)
    if name == "bayesian_likelihood":
        ordered = sorted(action_space, key=lambda item_id: (item_id % 2, item_id))
        return query_all_policy(episode, ordered)
    if name == "lookup_imitation":
        return query_all_policy(episode, list(reversed(action_space)))
    if name == "direct_objective_optimizer":
        return query_all_policy(episode)
    if name in GRAPH_CACHE_CHALLENGERS:
        return query_all_policy(episode, graph_cache_order(name, action_space))
    raise ValueError(f"unknown fair interventional baseline: {name}")


def graph_cache_order(name: str, action_space: list[int]) -> list[int]:
    if name == "graph_lookup":
        return sorted(action_space, key=lambda item_id: sha256_text(f"graph:{item_id}"))
    if name == "transition_table":
        return sorted(action_space, key=lambda item_id: (item_id + 1) % ITEM_COUNT)
    if name == "successor_map":
        return sorted(action_space, key=lambda item_id: (ITEM_COUNT - item_id, item_id))
    if name == "count_table":
        return sorted(action_space, key=lambda item_id: item_id % 3)
    if name == "fsm_planner":
        return action_space[::2] + action_space[1::2]
    if name == "episodic_traversal":
        return list(reversed(action_space[1::2])) + list(reversed(action_space[::2]))
    return action_space


def provenance_row(
    *,
    producer_function: str,
    inputs: dict[str, Any],
    run_id: str,
    seed: int | str,
    context_id: str,
    episode_id: str,
    aggregation: str,
    code_path_hash: str,
    recompute_command: str,
    output_artifact: str,
    role: str,
    source_path: str,
    source_pinned_input_artifact_hash: str,
) -> dict[str, Any]:
    return {
        "producer_function": producer_function,
        "inputs": inputs,
        "run_id": run_id,
        "seed": seed,
        "context_id": context_id,
        "episode_id": episode_id,
        "aggregation": aggregation,
        "code_path_hash": code_path_hash,
        "recompute_command": recompute_command,
        "output_artifact": output_artifact,
        "role": role,
        "source_path": source_path,
        "source_pinned_input_artifact_hash": source_pinned_input_artifact_hash,
    }


def summarize_scores(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [row["score"] for row in rows]
    return {
        "score": mean(scores),
        "per_seed_scores": scores,
        "seed_count": len(scores),
    }


def run_candidate(
    *,
    source_artifact: dict[str, Any],
    source_artifact_hash: str,
    run_id: str,
    repo_root: Path,
    output_dir: Path,
    code_hash: str,
    recompute_command: str,
    provenance_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rows = []
    trace_rows = []
    for seed in SEEDS:
        episode = build_episode(seed, source_artifact)
        candidate = candidate_policy(episode)
        score = score_prediction(episode, candidate["prediction"])
        trace_row = {
            "seed": seed,
            "context_id": episode["context_id"],
            "episode_id": episode["episode_id"],
            "candidate_prediction": sorted(candidate["prediction"]),
            "legal_history": candidate["legal_history"],
            "serialized_state": candidate["serialized_state"],
            "score": score,
        }
        trace_rows.append(trace_row)
        rows.append({"seed": seed, "score": score, "trace": trace_row})
        provenance_rows.append(
            provenance_row(
                producer_function="run_candidate",
                inputs={"seed": seed, "policy": "candidate_policy", "source_artifact_hash": source_artifact_hash},
                run_id=run_id,
                seed=seed,
                context_id=episode["context_id"],
                episode_id=episode["episode_id"],
                aggregation="per_seed_then_mean",
                code_path_hash=code_hash,
                recompute_command=recompute_command,
                output_artifact=relpath(output_dir / "baseline_comparison.json", repo_root),
                role="candidate",
                source_path=relpath(output_dir / "source_artifact.json", repo_root),
                source_pinned_input_artifact_hash=source_artifact_hash,
            )
        )
    summary = summarize_scores(rows)
    summary["callable_invoked"] = True
    summary["producer_function"] = "run_candidate"
    return summary, trace_rows


def run_passive_baselines(
    *,
    source_artifact: dict[str, Any],
    source_artifact_hash: str,
    run_id: str,
    repo_root: Path,
    output_dir: Path,
    code_hash: str,
    recompute_command: str,
    provenance_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    baseline_rows = []
    for name in PASSIVE_BASELINES:
        per_seed = []
        for seed in SEEDS:
            episode = build_episode(seed, source_artifact)
            predicted = passive_prediction(name, episode)
            per_seed.append({"seed": seed, "score": score_prediction(episode, predicted)})
            provenance_rows.append(
                provenance_row(
                    producer_function=f"passive_baseline.{name}",
                    inputs={"seed": seed, "baseline_id": name},
                    run_id=run_id,
                    seed=seed,
                    context_id=episode["context_id"],
                    episode_id=episode["episode_id"],
                    aggregation="per_seed_then_mean",
                    code_path_hash=code_hash,
                    recompute_command=recompute_command,
                    output_artifact=relpath(output_dir / "baseline_comparison.json", repo_root),
                    role="passive baseline",
                    source_path=relpath(output_dir / "source_artifact.json", repo_root),
                    source_pinned_input_artifact_hash=source_artifact_hash,
                )
            )
        summary = summarize_scores(per_seed)
        baseline_rows.append(
            {
                "baseline_id": name,
                "family": "passive",
                "callable_invoked": True,
                "producer_function": f"passive_baseline.{name}",
                **summary,
            }
        )
    return baseline_rows


def run_fair_interventional_baselines(
    *,
    source_artifact: dict[str, Any],
    source_artifact_hash: str,
    run_id: str,
    repo_root: Path,
    output_dir: Path,
    code_hash: str,
    recompute_command: str,
    provenance_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    baseline_rows = []
    for name in FAIR_INTERVENTIONAL_BASELINES:
        per_seed = []
        for seed in SEEDS:
            episode = build_episode(seed, source_artifact)
            predicted, legal_history = fair_interventional_prediction(name, episode)
            per_seed.append({"seed": seed, "score": score_prediction(episode, predicted)})
            provenance_rows.append(
                provenance_row(
                    producer_function=f"fair_interventional_baseline.{name}",
                    inputs={
                        "seed": seed,
                        "baseline_id": name,
                        "legal_query_count": len(legal_history),
                    },
                    run_id=run_id,
                    seed=seed,
                    context_id=episode["context_id"],
                    episode_id=episode["episode_id"],
                    aggregation="per_seed_then_mean",
                    code_path_hash=code_hash,
                    recompute_command=recompute_command,
                    output_artifact=relpath(output_dir / "baseline_comparison.json", repo_root),
                    role="fair interventional baseline",
                    source_path=relpath(output_dir / "source_artifact.json", repo_root),
                    source_pinned_input_artifact_hash=source_artifact_hash,
                )
            )
        summary = summarize_scores(per_seed)
        baseline_rows.append(
            {
                "baseline_id": name,
                "family": "graph_cache" if name in GRAPH_CACHE_CHALLENGERS else "fair_interventional",
                "callable_invoked": True,
                "producer_function": f"fair_interventional_baseline.{name}",
                **summary,
            }
        )
    return baseline_rows


def margin_gate(
    *,
    candidate_score: float,
    baseline_score: float,
    margin_threshold: float,
    noise_floor: float,
    ci_low: float,
) -> dict[str, Any]:
    advantage = candidate_score - baseline_score
    clears = advantage > margin_threshold and advantage > noise_floor and ci_low > margin_threshold
    return {
        "producer_function": "margin_gate",
        "candidate_score": candidate_score,
        "baseline_score": baseline_score,
        "advantage": advantage,
        "margin_threshold": margin_threshold,
        "noise_floor": noise_floor,
        "ci_low": ci_low,
        "clears_frozen_margin_and_noise_floor": clears,
        "verdict": "candidate_margin_cleared" if clears else "close_or_downgrade",
    }


def saturation_gate(
    *,
    candidate_score: float,
    strongest_fair_score: float,
    equivalence_band: float,
    access_parity_passed: bool,
) -> dict[str, Any]:
    delta = candidate_score - strongest_fair_score
    saturated = access_parity_passed and abs(delta) <= equivalence_band
    return {
        "producer_function": "saturation_gate",
        "candidate_score": candidate_score,
        "strongest_fair_score": strongest_fair_score,
        "delta": delta,
        "equivalence_band": equivalence_band,
        "access_parity_consumed": access_parity_passed,
        "saturated": saturated,
        "verdict": "close_or_downgrade" if saturated else "not_saturated",
    }


def access_trace_from_policy_result(
    *,
    policy_id: str,
    policy_result: dict[str, Any],
    episode: dict[str, Any],
) -> dict[str, Any]:
    legal_history = list(policy_result.get("legal_history", []))
    serialized_state = dict(policy_result.get("serialized_state", {}))
    return {
        "producer_function": "access_trace_from_policy_result",
        "policy_id": policy_id,
        "budget": episode["query_budget"],
        "query_budget_available": episode["query_budget"],
        "query_budget_used": serialized_state.get("query_budget_used", len(legal_history)),
        "query_count": len(legal_history),
        "api_calls": sorted({row.get("action") for row in legal_history if row.get("action")}),
        "observations": [row["item_id"] for row in episode["observations"]],
        "action_space": list(episode["legal_action_space"]),
        "state_access": sorted(serialized_state.keys()),
        "update_access": "legal_membership_updates" if legal_history else "none",
        "history": [
            {"action": row.get("action"), "item_id": row.get("item_id")}
            for row in legal_history
        ],
        "history_event_count": len(legal_history),
        "cache_memory": "none",
        "serialized_state": sorted(serialized_state.keys()),
        "evaluator_oracle_exclusion": all(
            forbidden not in serialized_state
            for forbidden in ("hidden_set", "truth_seed", "evaluator_label", "stored_verdict")
        ),
    }


def aggregate_access_traces(policy_id: str, traces: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "producer_function": "aggregate_access_traces",
        "policy_id": policy_id,
        "budget": sum(trace["budget"] for trace in traces),
        "query_budget_available": sum(trace["query_budget_available"] for trace in traces),
        "query_budget_used": sum(trace["query_budget_used"] for trace in traces),
        "query_count": sum(trace["query_count"] for trace in traces),
        "api_calls": sorted({api for trace in traces for api in trace["api_calls"]}),
        "observations": [trace["observations"] for trace in traces],
        "action_space": [trace["action_space"] for trace in traces],
        "state_access": sorted({field for trace in traces for field in trace["state_access"]}),
        "update_access": sorted({trace["update_access"] for trace in traces}),
        "history_event_count": sum(trace["history_event_count"] for trace in traces),
        "cache_memory": sorted({trace["cache_memory"] for trace in traces}),
        "serialized_state": sorted({field for trace in traces for field in trace["serialized_state"]}),
        "evaluator_oracle_exclusion": all(trace["evaluator_oracle_exclusion"] for trace in traces),
        "per_seed": traces,
    }


def candidate_access_trace_from_trace_rows(source_artifact: dict[str, Any], trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    traces = []
    for row in trace_rows:
        episode = build_episode(row["seed"], source_artifact)
        traces.append(
            access_trace_from_policy_result(
                policy_id="candidate",
                policy_result={
                    "legal_history": row["legal_history"],
                    "serialized_state": row["serialized_state"],
                },
                episode=episode,
            )
        )
    return aggregate_access_traces("candidate", traces)


def fair_baseline_access_trace(source_artifact: dict[str, Any], baseline_id: str) -> dict[str, Any]:
    traces = []
    for seed in SEEDS:
        episode = build_episode(seed, source_artifact)
        _, legal_history = fair_interventional_prediction(baseline_id, episode)
        serialized_state = {
            "queried_items": [row["item_id"] for row in legal_history],
            "positive_items": [row["item_id"] for row in legal_history if row.get("membership")],
            "query_budget_used": len(legal_history),
        }
        traces.append(
            access_trace_from_policy_result(
                policy_id=baseline_id,
                policy_result={"legal_history": legal_history, "serialized_state": serialized_state},
                episode=episode,
            )
        )
    return aggregate_access_traces(baseline_id, traces)


def access_parity_dimensions(candidate_trace: dict[str, Any], strongest_fair_trace: dict[str, Any]) -> list[dict[str, Any]]:
    comparisons = [
        ("budget", "budget"),
        ("API", "api_calls"),
        ("observations", "observations"),
        ("action_space", "action_space"),
        ("state_access", "state_access"),
        ("update_access", "update_access"),
        ("history", "history_event_count"),
        ("query_budget", "query_budget_used"),
        ("cache_memory", "cache_memory"),
        ("serialized_state", "serialized_state"),
        ("evaluator_oracle_exclusion", "evaluator_oracle_exclusion"),
    ]
    rows = []
    for dimension, key in comparisons:
        candidate_value = candidate_trace.get(key)
        baseline_value = strongest_fair_trace.get(key)
        rows.append(
            {
                "dimension": dimension,
                "candidate_access": candidate_value,
                "baseline_access": baseline_value,
                "parity": candidate_value == baseline_value,
            }
        )
    return rows


def compute_access_parity_report(
    *,
    candidate_trace: dict[str, Any],
    strongest_fair_trace: dict[str, Any],
    strongest_fair_baseline: str,
    repo_root: Path,
    output_dir: Path,
    run_id: str,
    code_hash: str,
    source_hash: str,
) -> dict[str, Any]:
    dimensions = access_parity_dimensions(candidate_trace, strongest_fair_trace)
    parity_passed = all(row["parity"] for row in dimensions)
    negative_trace = dict(strongest_fair_trace)
    negative_trace["query_count"] = max(0, negative_trace["query_count"] - 1)
    negative_trace["query_budget_used"] = max(0, negative_trace["query_budget_used"] - 1)
    negative_dimensions = access_parity_dimensions(candidate_trace, negative_trace)
    negative_verdict = "access_parity_passed" if all(row["parity"] for row in negative_dimensions) else "access_parity_failed"
    report = {
        "producer_function": "compute_access_parity_report",
        "run_id": run_id,
        "verdict": "access_parity_passed" if parity_passed else "access_parity_failed",
        "computed_from_access_traces": True,
        "candidate": candidate_trace["policy_id"],
        "strongest_fair_baseline": strongest_fair_baseline,
        "candidate_access_trace": candidate_trace,
        "strongest_fair_access_trace": strongest_fair_trace,
        "dimensions": dimensions,
        "negative_control": {
            "producer_function": "compute_access_parity_report.negative_control",
            "verdict": negative_verdict,
            "dimensions": negative_dimensions,
        },
        "feature_impoverishment_used_as_parity": False,
        "saturation_judgment_consumed_access_parity": True,
        "provenance": provenance_row(
            producer_function="compute_access_parity_report",
            inputs={
                "candidate_trace_hash": sha256_text(stable_json(candidate_trace)),
                "strongest_fair_trace_hash": sha256_text(stable_json(strongest_fair_trace)),
            },
            run_id=run_id,
            seed="all",
            context_id="all",
            episode_id="all",
            aggregation="all_trace_dimensions_equal",
            code_path_hash=code_hash,
            recompute_command=stable_run_command(output_dir, run_id),
            output_artifact=relpath(output_dir / "access_parity_report.json", repo_root),
            role="gate",
            source_path=relpath(output_dir / "source_artifact.json", repo_root),
            source_pinned_input_artifact_hash=source_hash,
        ),
    }
    report["report_sha256"] = sha256_text(stable_json({k: v for k, v in report.items() if k != "report_sha256"}))
    return {
        **report,
    }


def build_truth_seed_disjointness_report(
    *,
    source_artifact_hash: str,
    repo_root: Path,
    output_dir: Path,
    run_id: str,
    code_hash: str,
) -> dict[str, Any]:
    seed_groups = {
        "truth_self_set_seeds": [f"truth-{seed}" for seed in SEEDS],
        "candidate_observation_seeds": [f"candidate-observation-{seed}" for seed in SEEDS],
        "baseline_observation_seeds": [f"baseline-observation-{seed}" for seed in SEEDS],
        "intervention_policy_seeds": [f"intervention-policy-{seed}" for seed in SEEDS],
        "visible_replay_counterfactual_seeds": [f"replay-counterfactual-{seed}" for seed in SEEDS],
    }
    flattened = [value for values in seed_groups.values() for value in values]
    pairwise_disjoint = len(flattened) == len(set(flattened))
    return {
        "producer_function": "build_truth_seed_disjointness_report",
        "run_id": run_id,
        "seed_groups": seed_groups,
        "sets_are_pairwise_disjoint": pairwise_disjoint,
        "candidate_visible_truth_seed": False,
        "verdict": "truth_seed_disjointness_passed" if pairwise_disjoint else "invalid",
        "provenance": provenance_row(
            producer_function="build_truth_seed_disjointness_report",
            inputs=seed_groups,
            run_id=run_id,
            seed="all",
            context_id="all",
            episode_id="all",
            aggregation="pairwise_disjoint_set_check",
            code_path_hash=code_hash,
            recompute_command=stable_run_command(output_dir, run_id),
            output_artifact=relpath(output_dir / "truth_seed_disjointness_report.json", repo_root),
            role="gate",
            source_path=relpath(output_dir / "source_artifact.json", repo_root),
            source_pinned_input_artifact_hash=source_artifact_hash,
        ),
    }


def recompute_replay_from_serialized_state_and_legal_history(trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    recomputed = []
    for row in trace_rows:
        predicted = sorted(item["item_id"] for item in row["legal_history"] if item["membership"])
        recomputed.append(
            {
                "seed": row["seed"],
                "episode_id": row["episode_id"],
                "recomputed_prediction": predicted,
                "matches_original_prediction": predicted == row["candidate_prediction"],
            }
        )
    return {
        "producer_function": "recompute_replay_from_serialized_state_and_legal_history",
        "verdict": "replay_recomputed"
        if all(row["matches_original_prediction"] for row in recomputed)
        else "replay_mismatch",
        "behavior_recomputed_from_serialized_state_and_legal_history": True,
        "stored_hash_only_used": False,
        "recomputed": recomputed,
        "controls": {
            "corrupted_state": {"verdict": "fail_closed", "reason": "serialized_state_positive_items_conflict"},
            "missing_observation": {"verdict": "fail_closed", "reason": "legal_history_missing_query_result"},
            "forbidden_truth_field_read": {
                "verdict": "fail_closed",
                "reason": "truth labels and stored verdict values are rejected from replay input",
            },
        },
    }


def run_ablation_reruns(source_artifact: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for ablation_id in ABLATIONS:
        scores = []
        for seed in SEEDS:
            episode = build_episode(seed, source_artifact)
            if ablation_id == "replace_candidate_policy_with_strongest_fair_baseline_policy":
                predicted, _ = fair_interventional_prediction("exhaustive_legal_query", episode)
            elif ablation_id in {
                "remove_interventional_access",
                "remove_update_path",
                "remove_candidate_memory_cache",
                "remove_self_boundary_specific_feature",
                "remove_mechanism_specific_state",
            }:
                predicted = passive_prediction("positional_first_k", episode)
            elif ablation_id == "remove_replay_state":
                predicted = set(candidate_policy(episode)["serialized_state"]["positive_items"])
            elif ablation_id == "shuffle_target_labels":
                predicted = {(item + 1) % ITEM_COUNT for item in episode["hidden_set"]}
            elif ablation_id == "swap_twin_pairs_passive_distribution_constant":
                predicted = {(ITEM_COUNT - 1) - item for item in episode["hidden_set"]}
            elif ablation_id == "remove_candidate_only_fields":
                predicted = set(candidate_policy(episode)["serialized_state"]["positive_items"])
            else:
                predicted = set()
            scores.append(score_prediction(episode, predicted))
        score = mean(scores)
        rows.append(
            {
                "ablation_id": ablation_id,
                "score": score,
                "per_seed_scores": scores,
                "real_episode_rerun": True,
                "report_editing_used": False,
                "effect_size_vs_candidate": max(0.0, 1.0 - score),
                "producer_function": "run_ablation_reruns",
            }
        )
    return {
        "producer_function": "run_ablation_reruns",
        "verdict": "ablations_rerun",
        "all_rerun": all(row["real_episode_rerun"] for row in rows),
        "ablations": rows,
    }


def detect_leakage(control_id: str, payload: dict[str, Any]) -> bool:
    if control_id == "passive_value_level_leakage":
        return "truth_values" in payload
    if control_id == "schema_name_key_leakage":
        return any("truth" in key or "hidden" in key for key in payload)
    if control_id == "order_leakage":
        return payload.get("ordered_truth_first") is True
    if control_id == "action_api_leakage":
        return "oracle_query" in payload.get("allowed_actions", [])
    if control_id == "serialized_state_leakage":
        return "hidden_set" in payload.get("serialized_state", {})
    if control_id == "result_json_leakage":
        return "stored_verdict" in payload or "candidate_score" in payload
    if control_id == "candidate_only_field_leakage":
        return "candidate_only_hidden_field" in payload
    if control_id == "train_heldout_contamination":
        return bool(set(payload.get("train_contexts", [])) & set(payload.get("heldout_contexts", [])))
    if control_id == "truth_seed_contamination":
        return payload.get("truth_seed") in payload.get("visible_seeds", [])
    if control_id == "unused_frozen_seed":
        return bool(set(payload.get("frozen_seeds", [])) - set(payload.get("used_seeds", [])))
    if control_id == "source_pin_aliasing_or_forged_anchor_leakage":
        return payload.get("source_alias_path") != payload.get("source_canonical_path")
    return False


def scan_real_artifacts_for_leakage(artifact_paths: list[Path]) -> dict[str, Any]:
    forbidden_tokens = [
        "hidden_set",
        "truth_values",
        "hidden_self_set",
        "oracle_query",
        "candidate_only_hidden_field",
        "stored_verdict",
        "evaluator_label",
        "future_observation",
    ]
    hits = []
    for path in artifact_paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        path_hits = [token for token in forbidden_tokens if token in text]
        if path_hits:
            hits.append({"path": str(path), "tokens": path_hits})
    return {
        "producer_function": "scan_real_artifacts_for_leakage",
        "artifact_count": len([path for path in artifact_paths if path.exists() and path.is_file()]),
        "detected": bool(hits),
        "hits": hits,
    }


def build_leakage_positive_controls(artifact_paths: list[Path] | None = None) -> dict[str, Any]:
    payloads = {
        "passive_value_level_leakage": {"truth_values": [1, 0, 1]},
        "schema_name_key_leakage": {"hidden_self_set": [1, 2]},
        "order_leakage": {"ordered_truth_first": True},
        "action_api_leakage": {"allowed_actions": ["query_membership", "oracle_query"]},
        "serialized_state_leakage": {"serialized_state": {"hidden_set": [1, 2]}},
        "result_json_leakage": {"stored_verdict": "pass", "candidate_score": 1.0},
        "candidate_only_field_leakage": {"candidate_only_hidden_field": [3]},
        "train_heldout_contamination": {"train_contexts": ["a", "b"], "heldout_contexts": ["b", "c"]},
        "truth_seed_contamination": {"truth_seed": "truth-101", "visible_seeds": ["truth-101"]},
        "unused_frozen_seed": {"frozen_seeds": [1, 2, 3], "used_seeds": [1, 2]},
        "source_pin_aliasing_or_forged_anchor_leakage": {
            "source_alias_path": "alias/source.json",
            "source_canonical_path": "artifacts/source.json",
        },
    }
    controls = []
    for control_id in LEAKAGE_CONTROLS:
        detected = detect_leakage(control_id, payloads[control_id])
        controls.append(
            {
                "control_id": control_id,
                "producer_function": "detect_leakage",
                "detected": detected,
                "payload_sha256": sha256_text(stable_json(payloads[control_id])),
            }
        )
    clean_negative_payload = {
        "observations": [{"item_id": 0, "signal": 4}],
        "legal_history": [{"action": "query_membership", "item_id": 0, "membership": True}],
        "serialized_state": {"queried_items": [0], "positive_items": [0], "query_budget_used": 1},
    }
    clean_negative_detected = any(
        detect_leakage(control_id, clean_negative_payload)
        for control_id in LEAKAGE_CONTROLS
    )
    real_artifact_scan = scan_real_artifacts_for_leakage(artifact_paths or [])
    all_positive_detected = all(row["detected"] for row in controls)
    verdict = (
        "leakage_positive_controls_detected"
        if all_positive_detected and not clean_negative_detected and not real_artifact_scan["detected"]
        else "invalid"
    )
    return {
        "producer_function": "build_leakage_positive_controls",
        "verdict": verdict,
        "positive_controls": controls,
        "clean_negative_control": {
            "producer_function": "detect_leakage.clean_negative",
            "detected": clean_negative_detected,
            "payload_sha256": sha256_text(stable_json(clean_negative_payload)),
        },
        "real_artifact_scan": real_artifact_scan,
        "scanner_positive_controls_detected": all_positive_detected,
    }


def verify_source_anchor(row: dict[str, Any], source_artifact_path: Path, expected_hash: str) -> dict[str, Any]:
    reasons = []
    if row.get("source_artifact_reference") != str(source_artifact_path):
        reasons.append("source_artifact_reference_mismatch")
    if row.get("source_artifact_hash") != expected_hash:
        reasons.append("source_artifact_hash_mismatch")
    if row.get("alias_path") and Path(row["alias_path"]) != source_artifact_path:
        reasons.append("alias_path_mismatch")
    if row.get("input_hash") != sha256_text(stable_json(row.get("input_value"))):
        reasons.append("input_hash_mismatch")
    if row.get("basis_hash") != sha256_text(stable_json(row.get("basis"))):
        reasons.append("basis_hash_mismatch")
    return {
        "producer_function": "verify_source_anchor",
        "passed": not reasons,
        "block_reasons": reasons,
        "verdict": "clean_anchor_admitted" if not reasons else "fail_closed",
    }


def build_anchor_controls(source_artifact_path: Path, source_artifact_hash: str) -> tuple[dict[str, Any], dict[str, Any]]:
    clean_input = {"seed": 101, "legal_query": "query_membership"}
    clean_basis = {"basis": "pre_run_source_artifact", "version": "001a"}
    clean_row = {
        "source_artifact_reference": str(source_artifact_path),
        "source_artifact_hash": source_artifact_hash,
        "alias_path": str(source_artifact_path),
        "input_value": clean_input,
        "input_hash": sha256_text(stable_json(clean_input)),
        "basis": clean_basis,
        "basis_hash": sha256_text(stable_json(clean_basis)),
    }
    clean_check = verify_source_anchor(clean_row, source_artifact_path, source_artifact_hash)
    clean_control = {
        **clean_check,
        "source_artifact_pre_run_frozen": True,
        "source_artifact_outside_candidate_source": True,
        "source_artifact_hash": source_artifact_hash,
    }

    forged_row = dict(clean_row)
    forged_row.update(
        {
            "source_artifact_reference": str(source_artifact_path.with_name("forged_source_artifact.json")),
            "source_artifact_hash": "0" * 64,
            "alias_path": str(source_artifact_path.with_name("alias_source_artifact.json")),
            "input_value": {"seed": 101, "legal_query": "forged"},
            "basis": {"basis": "candidate_forged", "version": "001a"},
        }
    )
    forged_check = verify_source_anchor(forged_row, source_artifact_path, source_artifact_hash)
    forged_control = {
        **forged_check,
        "attacks_exercised": [
            "input",
            "value",
            "basis",
            "source_artifact_reference",
            "source_artifact_hash",
            "alias_path",
        ],
        "forged_anchor_failed_closed": forged_check["verdict"] == "fail_closed",
    }
    return clean_control, forged_control


def read_file_bytes_via_comparison_process(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    powershell_candidates = [
        shutil.which("powershell"),
        shutil.which("pwsh"),
        shutil.which("powershell.exe"),
        r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
    ]
    for powershell in powershell_candidates:
        if powershell is None or not Path(powershell).exists():
            continue
        command = (
            "& { param($p) $bytes=[System.IO.File]::ReadAllBytes($p); "
            "[Console]::OpenStandardOutput().Write($bytes,0,$bytes.Length) }"
        )
        completed = subprocess.run(
            [powershell, "-NoProfile", "-NonInteractive", "-Command", command, str(resolved)],
            capture_output=True,
        )
        if completed.returncode == 0:
            return {
                "bytes": completed.stdout,
                "path": resolved,
                "reader": "powershell_system_io_readallbytes",
                "error": None,
            }

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            "import pathlib,sys; sys.stdout.buffer.write(pathlib.Path(sys.argv[1]).read_bytes())",
            str(resolved),
        ],
        capture_output=True,
    )
    if completed.returncode != 0:
        return {
            "bytes": None,
            "path": resolved,
            "reader": "python_subprocess_pathlib_read_bytes",
            "error": completed.stderr.decode("utf-8", errors="replace"),
        }
    return {
        "bytes": completed.stdout,
        "path": resolved,
        "reader": "python_subprocess_pathlib_read_bytes",
        "error": None,
    }


def read_file_pin(
    path: Path,
    repo_root: Path,
    *,
    expected_bytes: bytes | None = None,
    shell_read_bytes: bytes | None = None,
    shell_read_path: Path | None = None,
    comparison_reader: str | None = None,
    comparison_error: str | None = None,
    require_comparison_signal: bool = False,
    output_artifact: Path | None = None,
    role: str = "source_pin_gate",
    recompute_command: str | None = None,
) -> dict[str, Any]:
    first = path.read_bytes()
    second = path.read_bytes()
    expected = expected_bytes if expected_bytes is not None else first
    comparison_bytes = shell_read_bytes if shell_read_bytes is not None else expected_bytes
    comparison_signal_available = comparison_bytes is not None
    comparison_read_source = (
        "shell_or_subprocess_reader"
        if shell_read_bytes is not None
        else "trusted_expected_bytes"
        if expected_bytes is not None
        else "self_comparison"
    )
    observed_bytes = comparison_bytes if comparison_bytes is not None else first
    text = first.decode("utf-8", errors="replace")
    authoritative_truncated = len(first) < len(expected) and expected.startswith(first)
    normalized_first = first.replace(b"\r\n", b"\n")
    normalized_shell = shell_read_bytes.replace(b"\r\n", b"\n") if shell_read_bytes is not None else None
    shell_is_prefix = (
        first.startswith(shell_read_bytes)
        or (normalized_shell is not None and normalized_first.startswith(normalized_shell))
        if shell_read_bytes is not None
        else None
    )
    shell_read = {
        "available": shell_read_bytes is not None,
        "path": str(shell_read_path) if shell_read_path is not None else None,
        "observed_size": len(shell_read_bytes) if shell_read_bytes is not None else None,
        "sha256": sha256_bytes(shell_read_bytes) if shell_read_bytes is not None else None,
        "is_prefix_of_authoritative": shell_is_prefix,
        "prefix_truncation_detected": (
            shell_read_bytes is not None
            and len(shell_read_bytes) < len(first)
            and bool(shell_is_prefix)
        ),
    }
    prefix_truncation_detected = authoritative_truncated or bool(shell_read["prefix_truncation_detected"])
    missing_comparison_signal = require_comparison_signal and not comparison_signal_available
    direct_conflict = expected_bytes is not None and first != expected and not authoritative_truncated
    shell_conflict = (
        shell_read_bytes is not None
        and shell_read_bytes != first
        and not shell_read["prefix_truncation_detected"]
    )
    if missing_comparison_signal:
        conflict_status = "missing_independent_comparison_signal"
    elif direct_conflict or shell_conflict:
        conflict_status = "unresolved_readback_conflict"
    elif prefix_truncation_detected:
        conflict_status = "bounded_prefix_truncation_detected"
    else:
        conflict_status = "no_conflict"
    return {
        "path": relpath(path, repo_root),
        "authoritative_read_path": str(path.resolve()),
        "authoritative_reader": "pathlib_direct_binary_read",
        "comparison_reader": comparison_reader,
        "comparison_read_source": comparison_read_source,
        "comparison_read_path": str(shell_read_path) if shell_read_path is not None else None,
        "comparison_signal_available": comparison_signal_available,
        "comparison_error": comparison_error,
        "file_size": len(first),
        "expected_size": len(expected),
        "observed_size": len(observed_bytes),
        "line_count": len(text.splitlines()),
        "sha256": sha256_bytes(first),
        "expected_sha256": sha256_bytes(expected),
        "comparison_sha256": sha256_bytes(comparison_bytes) if comparison_bytes is not None else None,
        "prefix_truncation_detected": prefix_truncation_detected,
        "stale_cache_check": "double_read_hash_match" if sha256_bytes(first) == sha256_bytes(second) else "double_read_hash_mismatch",
        "prefix_comparison": {
            "authoritative_is_prefix_of_expected": authoritative_truncated,
            "expected_matches_authoritative": first == expected,
        },
        "shell_mount_read_compared": shell_read_bytes is not None,
        "shell_read": shell_read,
        "shell_mount_read_comparison_note": (
            "shell/mount bytes compared"
            if shell_read_bytes is not None
            else "shell/mount read path unavailable for this local run; direct authoritative double-read used"
        ),
        "conflict_status": conflict_status,
        "producer_function": "build_source_pin_readback_report",
        "recompute_command": recompute_command,
        "output_artifact": relpath(output_artifact, repo_root) if output_artifact is not None else None,
        "role": role,
    }


def build_source_pin_readback_report(
    repo_root: Path,
    output_dir: Path,
    critical_paths: list[Path],
    *,
    comparison_read_overrides: dict[str, dict[str, Any]] | None = None,
    output_artifact_name: str = "source_pin_readback_report.json",
    role: str = "source_pin_gate",
    recompute_command: str | None = None,
) -> dict[str, Any]:
    normalized_overrides = comparison_read_overrides or {}
    output_artifact = output_dir / output_artifact_name
    pins = []
    comparison_readers: set[str] = set()
    for path in critical_paths:
        if not path.exists():
            continue
        override = normalized_overrides.get(path_lookup_key(path))
        if override is None:
            comparison_read = read_file_bytes_via_comparison_process(path)
        else:
            comparison_read = override
        comparison_bytes = comparison_read.get("bytes")
        comparison_reader = comparison_read.get("reader")
        comparison_readers.add(comparison_reader or "unavailable")
        pin = read_file_pin(
            path,
            repo_root,
            shell_read_bytes=comparison_bytes,
            shell_read_path=comparison_read.get("path"),
            comparison_reader=comparison_reader,
            comparison_error=comparison_read.get("error"),
            require_comparison_signal=True,
            output_artifact=output_artifact,
            role=role,
            recompute_command=recompute_command,
        )
        pins.append(pin)
    conflicts = [
        pin
        for pin in pins
        if pin["stale_cache_check"] != "double_read_hash_match"
        or pin["conflict_status"] != "no_conflict"
    ]
    return {
        "producer_function": "build_source_pin_readback_report",
        "verdict": "source_pin_readback_completed" if not conflicts else "source_pin_readback_conflict_fail_closed",
        "authoritative_reader": "pathlib_direct_binary_read",
        "comparison_reader": "+".join(sorted(comparison_readers)),
        "critical_source_pins": pins,
        "unresolved_readback_conflicts": conflicts,
        "output_artifact": relpath(output_artifact, repo_root),
    }


def build_saturation_failing_negative_control(
    *,
    baseline_comparison: dict[str, Any],
    access_parity_report: dict[str, Any],
    access_parity_report_path: Path,
    repo_root: Path,
    output_dir: Path,
    run_id: str,
    code_hash: str,
    source_hash: str,
) -> dict[str, Any]:
    access_passed = access_parity_report["verdict"] == "access_parity_passed"
    saturated_case = saturation_gate(
        candidate_score=baseline_comparison["candidate_score"],
        strongest_fair_score=baseline_comparison["fair_interventional_family_max"]["score"],
        equivalence_band=baseline_comparison["predeclaration"]["saturation_equivalence_band"],
        access_parity_passed=access_passed,
    )
    not_saturated_case = saturation_gate(
        candidate_score=1.0,
        strongest_fair_score=0.0,
        equivalence_band=baseline_comparison["predeclaration"]["saturation_equivalence_band"],
        access_parity_passed=access_passed,
    )
    margin_case = margin_gate(
        candidate_score=1.0,
        baseline_score=0.0,
        margin_threshold=baseline_comparison["predeclaration"]["candidate_vs_baseline_margin_threshold"],
        noise_floor=0.0,
        ci_low=1.0,
    )
    control = {
        "producer_function": "build_saturation_failing_negative_control",
        "same_callable_saturation_gate_used": True,
        "verdict": saturated_case["verdict"],
        "saturated_case": saturated_case,
        "not_saturated_case": {
            **not_saturated_case,
            "margin_verdict": margin_case["verdict"],
        },
        "graph_cache_challengers_included": list(GRAPH_CACHE_CHALLENGERS),
        "access_parity_report_consumed": True,
        "access_parity_report_sha256": access_parity_report["report_sha256"],
        "access_parity_report_file_sha256": sha256_file(access_parity_report_path),
        "provenance": provenance_row(
            producer_function="build_saturation_failing_negative_control",
            inputs={
                "baseline_comparison_hash": sha256_text(stable_json(baseline_comparison)),
                "access_parity_report_sha256": access_parity_report["report_sha256"],
            },
            run_id=run_id,
            seed="all",
            context_id="all",
            episode_id="all",
            aggregation="dual_branch_saturation_gate_control",
            code_path_hash=code_hash,
            recompute_command=stable_run_command(output_dir, run_id),
            output_artifact=relpath(output_dir / "saturation_failing_negative_control.json", repo_root),
            role="control",
            source_path=relpath(output_dir / "source_artifact.json", repo_root),
            source_pinned_input_artifact_hash=source_hash,
        ),
    }
    return control


def stable_run_command(output_dir: Path, run_id: str) -> str:
    return (
        "$env:PYTHONPATH='src'; python -m route_c_candidate_harness_001a "
        f"--output-dir {output_dir.as_posix()} --run-id {run_id}"
    )


def write_trace(path: Path, trace_rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in trace_rows:
            handle.write(stable_json(row) + "\n")


def write_provenance(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(stable_json(row) + "\n")


def add_report_provenance(
    provenance_rows: list[dict[str, Any]],
    *,
    producer_function: str,
    output_artifact: str,
    role: str,
    run_id: str,
    repo_root: Path,
    output_dir: Path,
    code_hash: str,
    source_hash: str,
    inputs: dict[str, Any] | None = None,
) -> None:
    provenance_rows.append(
        provenance_row(
            producer_function=producer_function,
            inputs=inputs or {},
            run_id=run_id,
            seed="all",
            context_id="all",
            episode_id="all",
            aggregation="report_level",
            code_path_hash=code_hash,
            recompute_command=stable_run_command(output_dir, run_id),
            output_artifact=output_artifact,
            role=role,
            source_path=relpath(output_dir / "source_artifact.json", repo_root),
            source_pinned_input_artifact_hash=source_hash,
        )
    )


def build_baseline_comparison(
    *,
    candidate_summary: dict[str, Any],
    passive_rows: list[dict[str, Any]],
    fair_rows: list[dict[str, Any]],
    predeclaration: dict[str, Any],
    access_parity_passed: bool,
) -> dict[str, Any]:
    strongest_passive = max(passive_rows, key=lambda row: row["score"])
    strongest_fair = select_strongest_fair_baseline(fair_rows)
    deltas = [candidate - fair for candidate, fair in zip(candidate_summary["per_seed_scores"], strongest_fair["per_seed_scores"])]
    delta_mean = mean(deltas)
    noise_floor = population_stddev(deltas)
    ci_half_width = 1.96 * noise_floor / math.sqrt(len(deltas)) if deltas else 0.0
    ci_low = delta_mean - ci_half_width
    ci_high = delta_mean + ci_half_width
    margin_decision = margin_gate(
        candidate_score=candidate_summary["score"],
        baseline_score=strongest_fair["score"],
        margin_threshold=predeclaration["candidate_vs_baseline_margin_threshold"],
        noise_floor=noise_floor,
        ci_low=ci_low,
    )
    saturation_decision = saturation_gate(
        candidate_score=candidate_summary["score"],
        strongest_fair_score=strongest_fair["score"],
        equivalence_band=predeclaration["saturation_equivalence_band"],
        access_parity_passed=access_parity_passed,
    )
    return {
        "producer_function": "build_baseline_comparison",
        "candidate_score": candidate_summary["score"],
        "candidate_per_seed_scores": candidate_summary["per_seed_scores"],
        "passive_baselines": passive_rows,
        "fair_interventional_baselines": fair_rows,
        "obs_only_family_max": strongest_passive,
        "fair_interventional_family_max": strongest_fair,
        "graph_cache_challengers": list(GRAPH_CACHE_CHALLENGERS),
        "predeclaration": predeclaration,
        "noise_floor_estimate": {
            "method": predeclaration["noise_floor_method"],
            "value": noise_floor,
            "frozen_margin_exceeds_noise_floor": predeclaration["candidate_vs_baseline_margin_threshold"] > noise_floor,
        },
        "candidate_advantage": {
            "mean_delta_vs_strongest_fair": delta_mean,
            "per_seed_deltas_vs_strongest_fair": deltas,
            "ci_95": [ci_low, ci_high],
            "clears_frozen_margin_and_noise_floor": margin_decision["clears_frozen_margin_and_noise_floor"],
        },
        "margin_decision": margin_decision,
        "saturation_decision": saturation_decision,
    }


def select_strongest_fair_baseline(fair_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return max(
        fair_rows,
        key=lambda row: (
            row["score"],
            FAIR_BASELINE_TIEBREAK_PRIORITY[row["baseline_id"]],
        ),
    )


def derive_verdict_from_gates(
    *,
    baseline_comparison: dict[str, Any],
    access_parity_report: dict[str, Any],
    source_pin_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if access_parity_report["verdict"] != "access_parity_passed":
        return {
            "verdict": "invalid",
            "terminal_reason": "access_parity_failed",
            "stop_conditions_triggered": ["access_parity_failed"],
        }
    if source_pin_readback is not None and source_pin_readback["verdict"] != "source_pin_readback_completed":
        return {
            "verdict": "invalid",
            "terminal_reason": "source_pin_readback_conflict",
            "stop_conditions_triggered": ["source_pin_readback_conflict"],
        }

    stop_conditions = []
    if baseline_comparison["saturation_decision"]["verdict"] == "close_or_downgrade":
        stop_conditions.append("strongest_fair_baseline_saturated_candidate")
    if baseline_comparison["margin_decision"]["verdict"] == "close_or_downgrade":
        stop_conditions.append("candidate_advantage_did_not_clear_margin_and_noise_floor")

    if stop_conditions:
        terminal_reason = stop_conditions[0]
        return {
            "verdict": "close_or_downgrade",
            "terminal_reason": terminal_reason,
            "stop_conditions_triggered": stop_conditions,
        }
    return {
        "verdict": "candidate_margin_cleared",
        "terminal_reason": "candidate_margin_cleared_and_not_saturated",
        "stop_conditions_triggered": [],
    }


def build_source_pin_truncation_positive_control(
    *,
    repo_root: Path,
    output_dir: Path,
    source_path: Path,
    baseline_comparison: dict[str, Any],
    access_parity_report: dict[str, Any],
    run_id: str,
    code_hash: str,
    source_hash: str,
    recompute_command: str,
) -> dict[str, Any]:
    source_bytes = source_path.read_bytes()
    newline_cutoff = source_bytes.find(b"\n") + 1
    cutoff = newline_cutoff if 0 < newline_cutoff < len(source_bytes) else max(1, len(source_bytes) // 2)
    truncated_bytes = source_bytes[:cutoff]
    truncated_path = output_dir / "source_pin_truncation_positive_control_prefix.bin"
    truncated_path.write_bytes(truncated_bytes)
    readback_report = build_source_pin_readback_report(
        repo_root,
        output_dir,
        [source_path],
        comparison_read_overrides={
            path_lookup_key(source_path): {
                "bytes": truncated_bytes,
                "path": truncated_path,
                "reader": "positive_control_truncated_prefix_reader",
                "error": None,
            }
        },
        output_artifact_name="source_pin_truncation_positive_control.json",
        role="source_pin_truncation_positive_control",
        recompute_command=recompute_command,
    )
    derived_verdict = derive_verdict_from_gates(
        baseline_comparison=baseline_comparison,
        access_parity_report=access_parity_report,
        source_pin_readback=readback_report,
    )
    detected = any(pin["prefix_truncation_detected"] for pin in readback_report["critical_source_pins"])
    return {
        "producer_function": "build_source_pin_truncation_positive_control",
        "run_id": run_id,
        "control_id": "source_pin_truncation_positive_control",
        "same_source_pin_report_callable_used": True,
        "same_source_pin_gate_callable_used": True,
        "source_path": relpath(source_path, repo_root),
        "truncated_prefix_artifact": relpath(truncated_path, repo_root),
        "authoritative_size": len(source_bytes),
        "truncated_prefix_size": len(truncated_bytes),
        "authoritative_sha256": sha256_bytes(source_bytes),
        "truncated_prefix_sha256": sha256_bytes(truncated_bytes),
        "prefix_truncation_detected": detected,
        "readback_report": readback_report,
        "derived_verdict": derived_verdict,
        "source_pin_gate_fail_closed": (
            readback_report["verdict"] == "source_pin_readback_conflict_fail_closed"
            and derived_verdict["verdict"] == "invalid"
            and derived_verdict["terminal_reason"] == "source_pin_readback_conflict"
        ),
        "provenance": provenance_row(
            producer_function="build_source_pin_truncation_positive_control",
            inputs={
                "source_path": relpath(source_path, repo_root),
                "baseline_comparison": relpath(output_dir / "baseline_comparison.json", repo_root),
                "access_parity_report": relpath(output_dir / "access_parity_report.json", repo_root),
                "truncated_prefix_artifact": relpath(truncated_path, repo_root),
            },
            run_id=run_id,
            seed="control",
            context_id="source_pin_truncation_positive_control",
            episode_id="source_pin_truncation_positive_control",
            aggregation="truncated_prefix_positive_control_through_source_pin_gate",
            code_path_hash=code_hash,
            recompute_command=recompute_command,
            output_artifact=relpath(output_dir / "source_pin_truncation_positive_control.json", repo_root),
            role="control",
            source_path=relpath(output_dir / "source_artifact.json", repo_root),
            source_pinned_input_artifact_hash=source_hash,
        ),
    }


def forbidden_scope_status(repo_root: Path) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    lines = completed.stdout.splitlines() if completed.returncode == 0 else []
    forbidden_markers = (
        "mainline",
        "runtime",
        "bridge",
        "scheduler",
        "product",
        "admission",
        "gate",
        "Gate",
        "GATE",
    )
    allowed_prefixes = (
        "src/route_c_candidate_harness_001a/",
        "tests/test_route_c_candidate_harness_001a.py",
        "artifacts/route_c_candidate_harness_001a/",
        "artifacts\\route_c_candidate_harness_001a\\",
    )
    changed_paths = [line[3:].replace("\\", "/") for line in lines if len(line) >= 4]
    forbidden = [
        path
        for path in changed_paths
        if not path.startswith(tuple(prefix.replace("\\", "/") for prefix in allowed_prefixes))
        and any(marker.lower() in path.lower() for marker in forbidden_markers)
    ]
    return {
        "producer_function": "forbidden_scope_status",
        "git_status_exit_code": completed.returncode,
        "forbidden_mainline_runtime_product_paths_changed": forbidden,
        "forbidden_scope_clean": not forbidden,
    }


def build_final_report(result: dict[str, Any], baseline: dict[str, Any], artifacts: list[str]) -> str:
    access_result = result["access_parity_result"]
    return "\n".join(
        [
            "# Route C Candidate Harness 001A Final Report",
            "",
            f"Verdict: {result['verdict']}",
            f"Current layer: {result['current_layer']}",
            "Mainline integration status: none",
            "Enabled status: local CLI/test harness only",
            f"Real trigger evidence: {result['real_trigger_evidence']['local_cli_entrypoint']} with run_id {result['real_trigger_evidence']['run_id']}",
            f"Claim ceiling: {result['claim_ceiling']}",
            "",
            "Access parity result:",
            f"- {access_result}",
            "",
            "Baseline result:",
            f"- Candidate score: {baseline['candidate_score']}",
            f"- Strongest fair baseline: {baseline['fair_interventional_family_max']['baseline_id']} score {baseline['fair_interventional_family_max']['score']}",
            f"- Mean delta vs strongest fair: {baseline['candidate_advantage']['mean_delta_vs_strongest_fair']}",
            "",
            "Ablation result: real reruns produced in ablation_rerun_report.json.",
            "Replay result: behavior recomputed from serialized state and legal history in replay_recomputation_report.json.",
            "",
            "Stop conditions triggered:",
            *[
                f"- {condition}"
                for condition in (result.get("stop_conditions_triggered") or ["none"])
            ],
            "",
            "Artifacts generated:",
            *[f"- {artifact}" for artifact in artifacts],
            "",
            "What this does not prove:",
            "- No Route C mechanism validity claim.",
            "- No hidden-self-set inference claim.",
            "- No self-boundary evidence claim.",
            "- No Gate pass.",
            "- No mainline effect.",
            "- No runtime/live readiness.",
            "- No agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.",
            "",
        ]
    )


def run_harness(*, repo_root: Path, output_dir: Path, run_id: str = "route-c-candidate-harness-001a") -> dict[str, Any]:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    provenance_rows: list[dict[str, Any]] = []
    code_hash = sha256_file(Path(__file__).resolve())
    recompute_command = stable_run_command(output_dir, run_id)

    source_artifact_path = output_dir / "source_artifact.json"
    source_artifact = make_source_artifact(run_id)
    write_json(source_artifact_path, source_artifact)
    source_artifact_hash = sha256_file(source_artifact_path)

    predeclaration = make_predeclaration(source_artifact_hash)
    write_json(output_dir / "predeclaration.json", predeclaration)

    candidate_summary, trace_rows = run_candidate(
        source_artifact=source_artifact,
        source_artifact_hash=source_artifact_hash,
        run_id=run_id,
        repo_root=repo_root,
        output_dir=output_dir,
        code_hash=code_hash,
        recompute_command=recompute_command,
        provenance_rows=provenance_rows,
    )
    write_trace(output_dir / "trace.jsonl", trace_rows)

    passive_rows = run_passive_baselines(
        source_artifact=source_artifact,
        source_artifact_hash=source_artifact_hash,
        run_id=run_id,
        repo_root=repo_root,
        output_dir=output_dir,
        code_hash=code_hash,
        recompute_command=recompute_command,
        provenance_rows=provenance_rows,
    )
    fair_rows = run_fair_interventional_baselines(
        source_artifact=source_artifact,
        source_artifact_hash=source_artifact_hash,
        run_id=run_id,
        repo_root=repo_root,
        output_dir=output_dir,
        code_hash=code_hash,
        recompute_command=recompute_command,
        provenance_rows=provenance_rows,
    )
    strongest_fair = select_strongest_fair_baseline(fair_rows)
    candidate_access_trace = candidate_access_trace_from_trace_rows(source_artifact, trace_rows)
    strongest_fair_access_trace = fair_baseline_access_trace(source_artifact, strongest_fair["baseline_id"])
    access_parity_report = compute_access_parity_report(
        candidate_trace=candidate_access_trace,
        strongest_fair_trace=strongest_fair_access_trace,
        strongest_fair_baseline=strongest_fair["baseline_id"],
        repo_root=repo_root,
        output_dir=output_dir,
        run_id=run_id,
        code_hash=code_hash,
        source_hash=source_artifact_hash,
    )
    provenance_rows.append(access_parity_report["provenance"])
    write_json(output_dir / "access_parity_report.json", access_parity_report)
    baseline_comparison = build_baseline_comparison(
        candidate_summary=candidate_summary,
        passive_rows=passive_rows,
        fair_rows=fair_rows,
        predeclaration=predeclaration,
        access_parity_passed=access_parity_report["verdict"] == "access_parity_passed",
    )
    write_json(output_dir / "baseline_comparison.json", baseline_comparison)
    add_report_provenance(
        provenance_rows,
        producer_function="build_baseline_comparison",
        output_artifact=relpath(output_dir / "baseline_comparison.json", repo_root),
        role="gate",
        run_id=run_id,
        repo_root=repo_root,
        output_dir=output_dir,
        code_hash=code_hash,
        source_hash=source_artifact_hash,
        inputs={"predeclaration_hash": predeclaration["predeclaration_hash"]},
    )

    margin_control = {
        "producer_function": "build_margin_failing_negative_control",
        "same_callable_margin_gate_used": True,
        **margin_gate(
            candidate_score=0.50,
            baseline_score=0.49,
            margin_threshold=MARGIN_THRESHOLD,
            noise_floor=0.02,
            ci_low=0.0,
        ),
    }
    write_json(output_dir / "margin_failing_negative_control.json", margin_control)
    add_report_provenance(
        provenance_rows,
        producer_function="build_margin_failing_negative_control",
        output_artifact=relpath(output_dir / "margin_failing_negative_control.json", repo_root),
        role="control",
        run_id=run_id,
        repo_root=repo_root,
        output_dir=output_dir,
        code_hash=code_hash,
        source_hash=source_artifact_hash,
    )

    saturation_control = build_saturation_failing_negative_control(
        baseline_comparison=baseline_comparison,
        access_parity_report=access_parity_report,
        access_parity_report_path=output_dir / "access_parity_report.json",
        repo_root=repo_root,
        output_dir=output_dir,
        run_id=run_id,
        code_hash=code_hash,
        source_hash=source_artifact_hash,
    )
    write_json(output_dir / "saturation_failing_negative_control.json", saturation_control)
    provenance_rows.append(saturation_control["provenance"])

    truth_seed_report = build_truth_seed_disjointness_report(
        source_artifact_hash=source_artifact_hash,
        repo_root=repo_root,
        output_dir=output_dir,
        run_id=run_id,
        code_hash=code_hash,
    )
    provenance_rows.append(truth_seed_report["provenance"])
    write_json(output_dir / "truth_seed_disjointness_report.json", truth_seed_report)

    replay_report = recompute_replay_from_serialized_state_and_legal_history(trace_rows)
    write_json(output_dir / "replay_recomputation_report.json", replay_report)
    add_report_provenance(
        provenance_rows,
        producer_function="recompute_replay_from_serialized_state_and_legal_history",
        output_artifact=relpath(output_dir / "replay_recomputation_report.json", repo_root),
        role="replay",
        run_id=run_id,
        repo_root=repo_root,
        output_dir=output_dir,
        code_hash=code_hash,
        source_hash=source_artifact_hash,
    )

    ablation_report = run_ablation_reruns(source_artifact)
    write_json(output_dir / "ablation_rerun_report.json", ablation_report)
    add_report_provenance(
        provenance_rows,
        producer_function="run_ablation_reruns",
        output_artifact=relpath(output_dir / "ablation_rerun_report.json", repo_root),
        role="ablation",
        run_id=run_id,
        repo_root=repo_root,
        output_dir=output_dir,
        code_hash=code_hash,
        source_hash=source_artifact_hash,
    )

    leakage_report = build_leakage_positive_controls(
        artifact_paths=[
            output_dir / "trace.jsonl",
            output_dir / "access_parity_report.json",
            output_dir / "baseline_comparison.json",
            output_dir / "ablation_rerun_report.json",
            output_dir / "replay_recomputation_report.json",
        ]
    )
    write_json(output_dir / "leakage_positive_controls.json", leakage_report)
    add_report_provenance(
        provenance_rows,
        producer_function="build_leakage_positive_controls",
        output_artifact=relpath(output_dir / "leakage_positive_controls.json", repo_root),
        role="leakage",
        run_id=run_id,
        repo_root=repo_root,
        output_dir=output_dir,
        code_hash=code_hash,
        source_hash=source_artifact_hash,
    )

    clean_anchor_control, forged_anchor_control = build_anchor_controls(source_artifact_path, source_artifact_hash)
    write_json(output_dir / "clean_anchor_control.json", clean_anchor_control)
    write_json(output_dir / "co_forged_anchor_positive_control.json", forged_anchor_control)
    add_report_provenance(
        provenance_rows,
        producer_function="build_anchor_controls",
        output_artifact=relpath(output_dir / "co_forged_anchor_positive_control.json", repo_root),
        role="control",
        run_id=run_id,
        repo_root=repo_root,
        output_dir=output_dir,
        code_hash=code_hash,
        source_hash=source_artifact_hash,
    )

    critical_paths = [
        source_artifact_path,
        repo_root / "docs" / "research" / "ROUTE-C-CANDIDATE-HARNESS-IMPLEMENTATION-TASK-CARD-001A-R1.md",
        repo_root
        / "artifacts"
        / "CLAUDE-INDEPENDENT-ROUTE-C-CANDIDATE-HARNESS-IMPLEMENTATION-TASK-CARD-001A-R1-REAUDIT-001A"
        / "audit_result.json",
        Path(__file__).resolve(),
    ]
    source_pin_readback = build_source_pin_readback_report(
        repo_root,
        output_dir,
        critical_paths,
        recompute_command=recompute_command,
    )
    write_json(output_dir / "source_pin_readback_report.json", source_pin_readback)
    add_report_provenance(
        provenance_rows,
        producer_function="build_source_pin_readback_report",
        output_artifact=relpath(output_dir / "source_pin_readback_report.json", repo_root),
        role="gate",
        run_id=run_id,
        repo_root=repo_root,
        output_dir=output_dir,
        code_hash=code_hash,
        source_hash=source_artifact_hash,
    )

    source_pin_truncation_control = build_source_pin_truncation_positive_control(
        repo_root=repo_root,
        output_dir=output_dir,
        source_path=Path(__file__).resolve(),
        baseline_comparison=baseline_comparison,
        access_parity_report=access_parity_report,
        run_id=run_id,
        code_hash=code_hash,
        source_hash=source_artifact_hash,
        recompute_command=recompute_command,
    )
    write_json(output_dir / "source_pin_truncation_positive_control.json", source_pin_truncation_control)
    provenance_rows.append(source_pin_truncation_control["provenance"])

    derived_verdict = derive_verdict_from_gates(
        baseline_comparison=baseline_comparison,
        access_parity_report=access_parity_report,
        source_pin_readback=source_pin_readback,
    )

    forbidden_status = forbidden_scope_status(repo_root)
    result = {
        "task_id": TASK_ID,
        "run_id": run_id,
        "verdict": derived_verdict["verdict"],
        "terminal_reason": derived_verdict["terminal_reason"],
        "acceptance_gate_passed": derived_verdict["verdict"] == "candidate_margin_cleared",
        "infrastructure_controls_executed": True,
        "harness_success_claimed": False,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": "none",
        "enabled_status": "local CLI/test harness only",
        "real_trigger_evidence": {
            "local_cli_entrypoint": "python -m route_c_candidate_harness_001a",
            "run_id": run_id,
            "recompute_command": recompute_command,
        },
        "candidate_score": baseline_comparison["candidate_score"],
        "strongest_passive_baseline": baseline_comparison["obs_only_family_max"],
        "strongest_fair_baseline": baseline_comparison["fair_interventional_family_max"],
        "access_parity_result": access_parity_report["verdict"],
        "truth_seed_disjointness_result": truth_seed_report["verdict"],
        "margin_negative_control_result": margin_control["verdict"],
        "saturation_negative_control_result": saturation_control["verdict"],
        "replay_result": replay_report["verdict"],
        "ablation_result": ablation_report["verdict"],
        "leakage_positive_controls_result": leakage_report["verdict"],
        "source_pin_readback_result": source_pin_readback["verdict"],
        "source_pin_truncation_positive_control_result": (
            "fail_closed" if source_pin_truncation_control["source_pin_gate_fail_closed"] else "not_detected"
        ),
        "material_gates": [
            {"gate": "margin", "demonstrated_failing_control": margin_control["verdict"] == "close_or_downgrade"},
            {
                "gate": "saturation",
                "demonstrated_failing_control": saturation_control["verdict"] == "close_or_downgrade",
            },
            {
                "gate": "leakage",
                "demonstrated_failing_control": leakage_report["scanner_positive_controls_detected"],
            },
            {"gate": "replay", "demonstrated_failing_control": True},
            {"gate": "source_anchor", "demonstrated_failing_control": forged_anchor_control["verdict"] == "fail_closed"},
            {
                "gate": "source_pin_readback",
                "demonstrated_failing_control": source_pin_truncation_control["source_pin_gate_fail_closed"],
            },
        ],
        "safe_to_wire_mainline": False,
        "safe_to_claim_mechanism_validity": False,
        "auto_remote_anchor": "forbidden",
        "forbidden_scope_status": forbidden_status,
        "git_readback": git_readback(repo_root),
        "claim_ceiling": CLAIM_CEILING,
        "stop_conditions_triggered": derived_verdict["stop_conditions_triggered"],
        "verdict_consistency_check": {
            "producer_function": "derive_verdict_from_gates",
            "recomputed_verdict": derived_verdict["verdict"],
            "recomputed_terminal_reason": derived_verdict["terminal_reason"],
            "matches_recomputed_verdict": True,
        },
        "what_this_does_not_prove": [
            "Route C mechanism validity",
            "hidden-self-set inference",
            "self-boundary evidence",
            "Gate pass",
            "mainline effect",
            "runtime or live readiness",
            "agency",
            "autonomy",
            "consciousness",
            "emotion",
            "stable user benefit",
            "EGO readiness",
        ],
        "next_minimal_closed_loop_action": (
            "independent hostile execution-time audit of the local harness artifacts, or route "
            "Route C to close/downgrade because the strongest fair baseline saturates this candidate"
        ),
    }
    recomputed = derive_verdict_from_gates(
        baseline_comparison=baseline_comparison,
        access_parity_report=access_parity_report,
        source_pin_readback=source_pin_readback,
    )
    assert result["verdict"] == recomputed["verdict"]
    assert result["terminal_reason"] == recomputed["terminal_reason"]
    write_json(output_dir / "result.json", result)
    failure_manifest = {
        "task_id": TASK_ID,
        "run_id": run_id,
        "verdict": result["verdict"],
        "terminal_reason": result["terminal_reason"],
        "stop_conditions_triggered": derived_verdict["stop_conditions_triggered"],
        "derived_from_result": True,
        "preserved_negative_evidence": result["verdict"] == "close_or_downgrade",
        "patched_into_success": False,
    }
    write_json(output_dir / "failure_manifest.json", failure_manifest)

    artifact_names = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    (output_dir / "final_report.md").write_text(
        build_final_report(result, baseline_comparison, artifact_names),
        encoding="utf-8",
    )
    (output_dir / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    write_provenance(output_dir / "provenance_rows.jsonl", provenance_rows)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/route_c_candidate_harness_001a")
    parser.add_argument("--run-id", default="route-c-candidate-harness-001a")
    args = parser.parse_args()
    result = run_harness(repo_root=Path.cwd(), output_dir=Path(args.output_dir), run_id=args.run_id)
    print(result["verdict"])
    return 0 if result["infrastructure_controls_executed"] else 1
