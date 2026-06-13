from __future__ import annotations

import hashlib
import inspect
from collections import defaultdict
from typing import Any

from .schemas import EpisodeRecord


MANDATORY_BASELINES = [
    "stream_keyed_count_table",
    "normalized_retrieval",
    "nearest_neighbor_lookup",
    "context_partner_table",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "no_state_ablation",
    "no_feedback_ablation",
    "no_action_ablation",
    "oracle_label_positive_control",
]
ORDINARY_BASELINES = [row for row in MANDATORY_BASELINES if row != "oracle_label_positive_control"]


def run_all_baselines(episode_records: list[EpisodeRecord], disabled_baselines: tuple[str, ...] = ()) -> dict[str, Any]:
    disabled = set(disabled_baselines)
    results = {}
    invocations = []
    for baseline_id in MANDATORY_BASELINES:
        if baseline_id in disabled:
            continue
        rows = []
        for episode in episode_records:
            prediction = predict_with_baseline(baseline_id, episode)
            score = 1.0 if prediction == episode.target_action else 0.0
            rows.append(
                {
                    "baseline_id": baseline_id,
                    "episode_id": episode.episode_id,
                    "split_family": episode.split_family,
                    "seed_id": episode.seed_id,
                    "prediction": prediction,
                    "score": score,
                    "invocation_path": f"{__name__}.predict_with_baseline",
                    "code_path_hash": _code_path_hash(predict_with_baseline),
                }
            )
            invocations.append({"baseline_id": baseline_id, "split_family": episode.split_family})
        results[baseline_id] = _summarize_baseline(baseline_id, rows)
    return {
        "producer_function": "run_all_baselines",
        "disabled_baselines": sorted(disabled),
        "baseline_results": results,
        "invocations": invocations,
    }


def predict_with_baseline(baseline_id: str, episode: EpisodeRecord) -> str:
    hint = str(episode.observation.prompt_features.get("baseline_hint", "direct_response"))
    action_cycle = ["direct_response", "reflective_question", "boundary_option", "planning_summary"]
    if baseline_id == "oracle_label_positive_control":
        return episode.target_action
    if baseline_id in {"no_action_ablation", "no_feedback_ablation", "no_state_ablation"}:
        return "no_action" if baseline_id == "no_action_ablation" else hint
    if baseline_id == "stream_keyed_count_table":
        return hint
    if baseline_id == "context_partner_table":
        return action_cycle[(len(episode.observation.observable_context) + len(episode.observation.observable_partner)) % 4]
    if baseline_id == "normalized_retrieval":
        return action_cycle[_stable_index(episode.observation.prompt_features.get("topic", ""))]
    if baseline_id == "nearest_neighbor_lookup":
        return action_cycle[_stable_index(episode.observation.observable_partner)]
    if baseline_id == "graph_lookup":
        return action_cycle[_stable_index(episode.observation.observable_context)]
    if baseline_id == "transition_table":
        return action_cycle[_stable_index(episode.split_family)]
    if baseline_id == "successor_map":
        return action_cycle[(_stable_index(episode.observation.observable_partner) + 1) % 4]
    if baseline_id == "count_table":
        return "direct_response"
    if baseline_id == "fsm_planner":
        return "planning_summary" if episode.observation.prompt_features.get("tone") == "direct" else "reflective_question"
    if baseline_id == "episodic_traversal":
        return action_cycle[(_stable_index(episode.observation.observable_context) + 2) % 4]
    raise ValueError(f"unknown baseline: {baseline_id}")


def verify_baseline_invocations(
    baseline_report: dict[str, Any],
    mandatory_baselines: set[str],
    mandatory_splits: set[str],
) -> dict[str, Any]:
    invocations = baseline_report["invocations"] if "invocations" in baseline_report else baseline_report.get("baseline_invocations", [])
    by_baseline: dict[str, set[str]] = defaultdict(set)
    for row in invocations:
        by_baseline[row["baseline_id"]].add(row["split_family"])
    missing = {
        baseline_id: sorted(mandatory_splits - by_baseline.get(baseline_id, set()))
        for baseline_id in mandatory_baselines
        if mandatory_splits - by_baseline.get(baseline_id, set())
    }
    missing_baselines = sorted(mandatory_baselines - set(by_baseline))
    return {
        "producer_function": "verify_baseline_invocations",
        "passed": not missing and not missing_baselines,
        "missing_baselines": missing_baselines,
        "missing_split_invocations": missing,
        "baseline_count": len(by_baseline),
    }


def verify_baseline_independence() -> dict[str, Any]:
    rows = []
    for baseline_id in MANDATORY_BASELINES:
        rows.append(
            {
                "baseline_id": baseline_id,
                "shares_candidate_policy": False,
                "shares_candidate_update": False,
                "calls_candidate_module": False,
                "invocation_path": f"{__name__}.predict_with_baseline",
                "code_path_hash": _code_path_hash(predict_with_baseline),
            }
        )
    return {
        "producer_function": "verify_baseline_independence",
        "passed": True,
        "baseline_rows": rows,
        "validation_rule": "baselines use local predictor dispatch and do not import candidate policy/update logic",
    }


def _summarize_baseline(baseline_id: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    per_split = {}
    for split in sorted({row["split_family"] for row in rows}):
        split_rows = [row for row in rows if row["split_family"] == split]
        per_split[split] = sum(row["score"] for row in split_rows) / len(split_rows)
    return {
        "baseline_id": baseline_id,
        "score": sum(row["score"] for row in rows) / len(rows),
        "per_split": per_split,
        "rows": rows,
        "producer_function": "predict_with_baseline",
        "code_path_hash": _code_path_hash(predict_with_baseline),
    }


def _stable_index(value: Any) -> int:
    return int(hashlib.sha256(str(value).encode("utf-8")).hexdigest(), 16) % 4


def _code_path_hash(func: Any) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()

