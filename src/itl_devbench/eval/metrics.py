from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict

from itl_devbench.core.hashing import sha256_file, sha256_json
from itl_devbench.core.trace import read_jsonl

METRIC_ORIENTATION: Dict[str, Dict[str, Any]] = {
    "survival_ticks": {"orientation": "higher", "primary": False},
    "total_reward": {"orientation": "higher", "primary": True},
    "energy_final": {"orientation": "higher", "primary": False},
    "health_final": {"orientation": "higher", "primary": False},
    "prediction_error_mean": {"orientation": "lower", "primary": False},
    "adaptation_lag_after_rule_shift": {"orientation": "lower", "primary": False},
    "memory_size": {"orientation": "bounded", "primary": False},
    "action_count": {"orientation": "bounded", "primary": False},
    "collision_count": {"orientation": "lower", "primary": False},
    "oracle_gap": {"orientation": "higher", "primary": False},
}


def compute_metrics_from_trace(trace_path: str | Path) -> Dict[str, Any]:
    trace_path = Path(trace_path)
    trace_artifact_id = trace_path.name
    events = read_jsonl(trace_path)
    groups: dict[tuple[str, str, str, str, str, int, int, int], list[Dict[str, Any]]] = defaultdict(list)
    for event in events:
        key = (
            str(event.get("split", "legacy")),
            str(event.get("family_id", "legacy_stage")),
            str(event["agent_id"]),
            str(event["variant"]),
            str(event["agent_kind"]),
            int(event["seed"]),
            int(event["stage"]),
            int(event["episode"]),
        )
        groups[key].append(event)

    code_hash = sha256_file(Path(__file__))
    episode_metrics: list[Dict[str, Any]] = []
    for (split, family_id, agent_id, variant, agent_kind, seed, stage, episode), group in sorted(groups.items()):
        total_reward = sum(float(event["reward"]) for event in group)
        last = group[-1]
        final_obs = last["env_result"]["obs_after"]
        pe_values = [float(event.get("prediction_error", {}).get("total", 0.0)) for event in group]
        shift_index = next(
            (index for index, event in enumerate(group) if event["env_result"]["info"].get("rule_shift_occurred")),
            None,
        )
        adaptation_lag = None
        if shift_index is not None:
            for lag, event in enumerate(group[shift_index:], start=0):
                if float(event.get("prediction_error", {}).get("total", 0.0)) <= 1.0:
                    adaptation_lag = lag
                    break
        episode_metrics.append(
            {
                "producer_function": "itl_devbench.eval.metrics.compute_metrics_from_trace",
                "input_artifacts": [trace_artifact_id],
                "run_id": last["run_id"],
                "seed": seed,
                "split": split,
                "family_id": family_id,
                "family_instance_id": last.get("family_instance_id", f"legacy:{stage}:{seed}:{episode}"),
                "dimension_combo": list(last.get("dimension_combo", [])),
                "target_pressure": list(last.get("target_pressure", [])),
                "stage": stage,
                "episode": episode,
                "agent_id": agent_id,
                "agent_kind": agent_kind,
                "variant": variant,
                "survival_ticks": len(group),
                "total_reward": total_reward,
                "energy_final": int(final_obs["energy"]),
                "health_final": int(final_obs["health"]),
                "prediction_error_mean": sum(pe_values) / len(pe_values) if pe_values else 0.0,
                "adaptation_lag_after_rule_shift": adaptation_lag,
                "memory_size": int(last["S_after"].get("memory_size", 0)),
                "action_count": len(group),
                "collision_count": sum(1 for event in group if event["env_result"]["info"].get("collision")),
                "oracle_gap": None,
                "aggregation_rule": "group_by_agent_variant_kind_seed_stage_episode",
                "code_path_hash": code_hash,
            }
        )

    oracle_rewards = {
        (metric["split"], metric["family_id"], metric["seed"], metric["stage"]): metric["total_reward"]
        for metric in episode_metrics
        if metric["agent_id"] == "oracle"
    }
    for metric in episode_metrics:
        oracle_reward = oracle_rewards.get((metric["split"], metric["family_id"], metric["seed"], metric["stage"]))
        if oracle_reward is not None:
            metric["oracle_gap"] = oracle_reward - metric["total_reward"]

    result = {
        "producer_function": "itl_devbench.eval.metrics.compute_metrics_from_trace",
        "input_artifacts": [trace_artifact_id],
        "metric_orientation": METRIC_ORIENTATION,
        "episode_metrics": episode_metrics,
        "metrics_hash": sha256_json(episode_metrics),
        "code_path_hash": code_hash,
    }
    return result


def aggregate_baseline_scores(metrics: Dict[str, Any]) -> Dict[str, Any]:
    grouped: dict[tuple[str, str, str], list[Dict[str, Any]]] = defaultdict(list)
    for metric in metrics["episode_metrics"]:
        grouped[(metric["agent_id"], metric["variant"], metric["agent_kind"])].append(metric)

    aggregates: list[Dict[str, Any]] = []
    for (agent_id, variant, agent_kind), rows in sorted(grouped.items()):
        aggregates.append(
            {
                "producer_function": "itl_devbench.eval.metrics.aggregate_baseline_scores",
                "agent_id": agent_id,
                "agent_kind": agent_kind,
                "variant": variant,
                "episode_count": len(rows),
                "mean_survival_ticks": sum(row["survival_ticks"] for row in rows) / len(rows),
                "mean_total_reward": sum(row["total_reward"] for row in rows) / len(rows),
                "mean_prediction_error": sum(row["prediction_error_mean"] for row in rows) / len(rows),
                "mean_oracle_gap": (
                    sum(float(row["oracle_gap"]) for row in rows if row["oracle_gap"] is not None)
                    / max(1, sum(1 for row in rows if row["oracle_gap"] is not None))
                ),
                "input_artifacts": metrics.get("input_artifacts", []),
                "run_ids": sorted({row["run_id"] for row in rows}),
                "seed_stage_episode_ids": [
                    {
                        "seed": row["seed"],
                        "split": row.get("split", "legacy"),
                        "family_id": row.get("family_id", "legacy_stage"),
                        "stage": row["stage"],
                        "episode": row["episode"],
                    }
                    for row in rows
                ],
                "aggregation_rule": "mean_by_agent_variant_kind",
                "code_path_hash": metrics.get("code_path_hash"),
            }
        )
    return {"producer_function": "itl_devbench.eval.metrics.aggregate_baseline_scores", "scores": aggregates}


def aggregate_scores_by_stage(metrics: Dict[str, Any]) -> Dict[str, Any]:
    grouped: dict[tuple[int, str, str, str], list[Dict[str, Any]]] = defaultdict(list)
    for metric in metrics["episode_metrics"]:
        grouped[(metric["stage"], metric["agent_id"], metric["variant"], metric["agent_kind"])].append(metric)

    by_stage: list[Dict[str, Any]] = []
    for (stage, agent_id, variant, agent_kind), rows in sorted(grouped.items()):
        by_stage.append(
            {
                "producer_function": "itl_devbench.eval.metrics.aggregate_scores_by_stage",
                "stage": stage,
                "agent_id": agent_id,
                "agent_kind": agent_kind,
                "variant": variant,
                "episode_count": len(rows),
                "mean_survival_ticks": sum(row["survival_ticks"] for row in rows) / len(rows),
                "mean_total_reward": sum(row["total_reward"] for row in rows) / len(rows),
                "mean_prediction_error": sum(row["prediction_error_mean"] for row in rows) / len(rows),
                "mean_oracle_gap": (
                    sum(float(row["oracle_gap"]) for row in rows if row["oracle_gap"] is not None)
                    / max(1, sum(1 for row in rows if row["oracle_gap"] is not None))
                ),
                "input_artifacts": metrics.get("input_artifacts", []),
                "run_ids": sorted({row["run_id"] for row in rows}),
                "seed_stage_episode_ids": [
                    {
                        "seed": row["seed"],
                        "split": row.get("split", "legacy"),
                        "family_id": row.get("family_id", "legacy_stage"),
                        "stage": row["stage"],
                        "episode": row["episode"],
                    }
                    for row in rows
                ],
                "aggregation_rule": "mean_by_stage_agent_variant_kind",
                "code_path_hash": metrics.get("code_path_hash"),
            }
        )
    return {
        "producer_function": "itl_devbench.eval.metrics.aggregate_scores_by_stage",
        "metric_orientation": METRIC_ORIENTATION,
        "scores": by_stage,
    }


def write_metrics(path: str | Path, metrics: Dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
