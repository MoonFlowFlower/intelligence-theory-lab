from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict

from itl_devbench.core.hashing import sha256_file, sha256_json
from itl_devbench.core.trace import read_jsonl
from itl_devbench.envs.families import REQUIRED_FAMILY_IDS


def aggregate_scores_by_family(metrics: Dict[str, Any]) -> Dict[str, Any]:
    grouped: dict[tuple[str, str, str, str], list[Dict[str, Any]]] = defaultdict(list)
    for metric in metrics["episode_metrics"]:
        grouped[
            (
                str(metric.get("family_id", "legacy_stage")),
                str(metric["agent_id"]),
                str(metric["variant"]),
                str(metric["agent_kind"]),
            )
        ].append(metric)

    rows: list[Dict[str, Any]] = []
    for (family_id, agent_id, variant, agent_kind), values in sorted(grouped.items()):
        rows.append(_aggregate_metric_rows(values, family_id, agent_id, variant, agent_kind))

    return {
        "producer_function": "itl_devbench.eval.family_metrics.aggregate_scores_by_family",
        "scores": rows,
        "code_path_hash": sha256_file(Path(__file__)),
        "report_hash": sha256_json(rows),
    }


def aggregate_scores_by_dimension(metrics: Dict[str, Any]) -> Dict[str, Any]:
    grouped: dict[tuple[str, str, str, str, str], list[Dict[str, Any]]] = defaultdict(list)
    for metric in metrics["episode_metrics"]:
        dimension_key = "|".join(str(value) for value in metric.get("dimension_combo", []))
        grouped[
            (
                dimension_key,
                str(metric["agent_id"]),
                str(metric["variant"]),
                str(metric["agent_kind"]),
                str(metric.get("family_id", "legacy_stage")),
            )
        ].append(metric)

    rows: list[Dict[str, Any]] = []
    for (dimension_key, agent_id, variant, agent_kind, family_id), values in sorted(grouped.items()):
        row = _aggregate_metric_rows(values, family_id, agent_id, variant, agent_kind)
        row["dimension_combo_key"] = dimension_key
        row["dimension_combo"] = list(values[0].get("dimension_combo", []))
        rows.append(row)

    return {
        "producer_function": "itl_devbench.eval.family_metrics.aggregate_scores_by_dimension",
        "scores": rows,
        "code_path_hash": sha256_file(Path(__file__)),
        "report_hash": sha256_json(rows),
    }


def compute_family_metric_summary(
    metrics: Dict[str, Any],
    baseline_scores_by_family: Dict[str, Any],
    trace_path: str | Path,
) -> Dict[str, Any]:
    events = read_jsonl(trace_path)
    rows_by_family: dict[str, list[Dict[str, Any]]] = defaultdict(list)
    for row in baseline_scores_by_family["scores"]:
        rows_by_family[str(row["family_id"])].append(row)

    events_by_family: dict[str, list[Dict[str, Any]]] = defaultdict(list)
    for event in events:
        events_by_family[str(event.get("family_id", "legacy_stage"))].append(event)

    families: list[Dict[str, Any]] = []
    for family_id in REQUIRED_FAMILY_IDS:
        rows = rows_by_family.get(family_id, [])
        score_map = _score_map(rows)
        oracle_score = score_map.get(("oracle", "hidden_state_headroom"))
        graph_score = score_map.get(("graph_cache", "frozen"))
        random_score = score_map.get(("random_policy", "frozen"))
        obs_score = score_map.get(("obs_only_policy", "frozen"))
        fsm_score = score_map.get(("generic_fsm", "frozen"))
        baseline_values = [
            value
            for value in [random_score, obs_score, fsm_score, graph_score]
            if value is not None
        ]
        oracle_gap = None if oracle_score is None or not baseline_values else oracle_score - max(baseline_values)
        family_events = events_by_family.get(family_id, [])
        minimal_loop_scores = {
            variant: score
            for (agent_id, variant), score in score_map.items()
            if agent_id == "minimal_loop"
        }
        family_row = {
            "producer_function": "itl_devbench.eval.family_metrics.compute_family_metric_summary",
            "family_id": family_id,
            "target_pressure": _target_pressure_from_events(family_events),
            "oracle_score": oracle_score,
            "random_score": random_score,
            "obs_only_score": obs_score,
            "generic_fsm_score": fsm_score,
            "graph_cache_score": graph_score,
            "minimal_loop_variant_scores": minimal_loop_scores,
            "oracle_gap": oracle_gap,
            "graph_cache_gap_to_oracle": _gap(oracle_score, graph_score),
            "obs_only_gap_to_oracle": _gap(oracle_score, obs_score),
            "fsm_gap_to_oracle": _gap(oracle_score, fsm_score),
            "saturated_by": _saturated_by(oracle_score, rows),
            "valid_headroom": _valid_headroom(oracle_score, [random_score, obs_score, fsm_score, graph_score]),
            **_family_specific_metrics(family_id, family_events),
        }
        families.append(family_row)

    result = {
        "producer_function": "itl_devbench.eval.family_metrics.compute_family_metric_summary",
        "input_artifacts": list(metrics.get("input_artifacts", [])) + [Path(trace_path).name],
        "families": families,
        "code_path_hash": sha256_file(Path(__file__)),
    }
    result["report_hash"] = sha256_json(families)
    return result


def write_family_json(path: str | Path, payload: Dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _aggregate_metric_rows(
    rows: list[Dict[str, Any]],
    family_id: str,
    agent_id: str,
    variant: str,
    agent_kind: str,
) -> Dict[str, Any]:
    return {
        "producer_function": "itl_devbench.eval.family_metrics._aggregate_metric_rows",
        "family_id": family_id,
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
        "splits": sorted({str(row.get("split", "legacy")) for row in rows}),
        "run_ids": sorted({str(row["run_id"]) for row in rows}),
        "seed_stage_episode_ids": [
            {
                "seed": row["seed"],
                "split": row.get("split", "legacy"),
                "family_id": row.get("family_id", family_id),
                "stage": row["stage"],
                "episode": row["episode"],
            }
            for row in rows
        ],
        "aggregation_rule": "mean_by_family_agent_variant_kind",
        "code_path_hash": rows[0].get("code_path_hash"),
    }


def _score_map(rows: list[Dict[str, Any]]) -> dict[tuple[str, str], float]:
    return {(str(row["agent_id"]), str(row["variant"])): float(row["mean_total_reward"]) for row in rows}


def _gap(oracle_score: float | None, score: float | None) -> float | None:
    if oracle_score is None or score is None:
        return None
    return oracle_score - score


def _valid_headroom(oracle_score: float | None, scores: list[float | None]) -> bool:
    if oracle_score is None or any(score is None for score in scores):
        return False
    return all(float(score) <= oracle_score for score in scores if score is not None)


def _saturated_by(oracle_score: float | None, rows: list[Dict[str, Any]]) -> list[str]:
    if oracle_score is None:
        return []
    saturated = []
    for row in rows:
        if row["agent_id"] == "oracle":
            continue
        if float(row["mean_total_reward"]) >= oracle_score:
            saturated.append(f"{row['agent_id']}:{row['variant']}")
    return sorted(saturated)


def _target_pressure_from_events(events: list[Dict[str, Any]]) -> list[str]:
    for event in events:
        pressure = event.get("target_pressure")
        if pressure:
            return list(pressure)
    return []


def _family_specific_metrics(family_id: str, events: list[Dict[str, Any]]) -> Dict[str, Any]:
    if family_id == "delayed_poison_v1":
        return _delayed_metrics(events)
    if family_id == "rule_reversal_return_v1":
        return _rule_reversal_metrics(events)
    if family_id == "info_risk_tradeoff_v1":
        return _info_risk_metrics(events)
    if family_id == "aliased_food_v1":
        return _aliasing_metrics(events)
    return {
        "adaptation_lag": None,
        "old_rule_return_recovery": None,
        "forgetting_index": None,
        "delayed_credit_assignment_score": None,
        "information_value_efficiency": None,
        "perceptual_aliasing_failure_rate": None,
    }


def _delayed_metrics(events: list[Dict[str, Any]]) -> Dict[str, Any]:
    delayed_events = [
        event
        for event in events
        if event["env_result"]["info"].get("delayed_effect_event_id") is not None
    ]
    valid_delayed = [
        event
        for event in delayed_events
        if int(event["env_result"]["info"].get("delay_ticks") or 0) >= 7
        and event["env_result"]["info"].get("cause_event_id") is not None
        and event["env_result"]["info"].get("source_object_id")
    ]
    cause_events = [
        event
        for event in events
        if event["env_result"]["info"].get("source_object_id") == "delayed_food"
        and event["env_result"]["info"].get("ate")
    ]
    score = len(valid_delayed) / max(1, len(cause_events))
    return {
        "adaptation_lag": None,
        "old_rule_return_recovery": None,
        "forgetting_index": None,
        "delayed_credit_assignment_score": score,
        "information_value_efficiency": None,
        "perceptual_aliasing_failure_rate": None,
    }


def _rule_reversal_metrics(events: list[Dict[str, Any]]) -> Dict[str, Any]:
    phase_events = [
        event
        for event in events
        if event["env_result"]["info"].get("chosen_rule_object") in {"red", "blue"}
    ]
    by_phase: dict[str, list[Dict[str, Any]]] = defaultdict(list)
    for event in phase_events:
        by_phase[str(event["env_result"]["info"].get("rule_phase"))].append(event)

    lag_values = []
    for phase in ["B", "C", "A_prime"]:
        phase_rows = by_phase.get(phase, [])
        first_correct = next(
            (
                index
                for index, event in enumerate(phase_rows)
                if event["env_result"]["info"].get("chosen_rule_object")
                == event["env_result"]["info"].get("good_rule_object")
            ),
            None,
        )
        if first_correct is not None:
            lag_values.append(first_correct)
    a_rows = by_phase.get("A", [])
    aprime_rows = by_phase.get("A_prime", [])
    a_accuracy = _phase_accuracy(a_rows)
    aprime_accuracy = _phase_accuracy(aprime_rows)
    return {
        "adaptation_lag": sum(lag_values) / len(lag_values) if lag_values else None,
        "old_rule_return_recovery": aprime_accuracy,
        "forgetting_index": None if a_accuracy is None or aprime_accuracy is None else a_accuracy - aprime_accuracy,
        "delayed_credit_assignment_score": None,
        "information_value_efficiency": None,
        "perceptual_aliasing_failure_rate": None,
    }


def _info_risk_metrics(events: list[Dict[str, Any]]) -> Dict[str, Any]:
    experiment_events = [
        event
        for event in events
        if event["A_t"] in {"inspect", "sample_small_bite"}
        and float(event["env_result"]["info"].get("information_gain") or 0.0) > 0.0
    ]
    gain = sum(float(event["env_result"]["info"].get("information_gain") or 0.0) for event in experiment_events)
    cost = sum(abs(min(0.0, float(event["reward"]))) for event in experiment_events)
    eat_events = [event for event in events if event["A_t"] == "eat"]
    inspect_events = [event for event in events if event["A_t"] == "inspect"]
    return {
        "adaptation_lag": None,
        "old_rule_return_recovery": None,
        "forgetting_index": None,
        "delayed_credit_assignment_score": None,
        "information_value_efficiency": gain / max(1.0, cost),
        "risk_adjusted_reward": sum(float(event["reward"]) for event in events) / max(1, len(events)),
        "unnecessary_inspect_rate": len(inspect_events) / max(1, len(events)),
        "reckless_eat_rate": sum(1 for event in eat_events if float(event["reward"]) < 0.0) / max(1, len(eat_events)),
        "perceptual_aliasing_failure_rate": None,
    }


def _aliasing_metrics(events: list[Dict[str, Any]]) -> Dict[str, Any]:
    eat_events = [event for event in events if event["A_t"] == "eat"]
    bad_eats = [event for event in eat_events if float(event["reward"]) < 0.0]
    return {
        "adaptation_lag": None,
        "old_rule_return_recovery": None,
        "forgetting_index": None,
        "delayed_credit_assignment_score": None,
        "information_value_efficiency": None,
        "perceptual_aliasing_failure_rate": len(bad_eats) / max(1, len(eat_events)),
    }


def _phase_accuracy(events: list[Dict[str, Any]]) -> float | None:
    if not events:
        return None
    return sum(
        1
        for event in events
        if event["env_result"]["info"].get("chosen_rule_object")
        == event["env_result"]["info"].get("good_rule_object")
    ) / len(events)
