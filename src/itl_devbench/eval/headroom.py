from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from itl_devbench.core.hashing import sha256_file, sha256_json
from itl_devbench.eval.metrics import METRIC_ORIENTATION


def compute_oracle_headroom_report(
    baseline_scores: Dict[str, Any],
    baseline_scores_by_stage: Dict[str, Any],
    required_baselines: list[str],
) -> Dict[str, Any]:
    primary_metric = _primary_metric()
    orientation = METRIC_ORIENTATION[primary_metric]["orientation"]
    aggregate = _compare_score_rows(baseline_scores["scores"], required_baselines, primary_metric)
    by_stage = []
    stages = sorted({int(row["stage"]) for row in baseline_scores_by_stage["scores"]})
    for stage in stages:
        rows = [row for row in baseline_scores_by_stage["scores"] if int(row["stage"]) == stage]
        stage_report = _compare_score_rows(rows, required_baselines, primary_metric)
        stage_report["stage"] = stage
        by_stage.append(stage_report)

    result = {
        "producer_function": "itl_devbench.eval.headroom.compute_oracle_headroom_report",
        "primary_metric": primary_metric,
        "primary_metric_orientation": orientation,
        "metric_orientation": METRIC_ORIENTATION,
        "required_baselines": required_baselines,
        "aggregate": aggregate,
        "by_stage": by_stage,
    }
    result["report_hash"] = sha256_json(result)
    result["code_path_hash"] = sha256_file(Path(__file__))
    return result


def write_oracle_headroom_report(path: str | Path, report: Dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


def _primary_metric() -> str:
    primaries = [name for name, spec in METRIC_ORIENTATION.items() if spec.get("primary")]
    if len(primaries) != 1:
        raise ValueError(f"expected_one_primary_metric:{primaries}")
    return primaries[0]


def _compare_score_rows(rows: list[Dict[str, Any]], required_baselines: list[str], primary_metric: str) -> Dict[str, Any]:
    score_key = f"mean_{primary_metric}"
    oracle_rows = [row for row in rows if row["agent_id"] == "oracle"]
    if len(oracle_rows) != 1:
        return {
            "oracle_upper_bound_valid": False,
            "reason": f"expected_one_oracle_row_found_{len(oracle_rows)}",
            "oracle_score": None,
            "baseline_scores": {},
            "violations": required_baselines,
        }
    oracle_score = float(oracle_rows[0][score_key])
    baseline_scores: dict[str, float] = {}
    violations: list[str] = []
    for baseline in required_baselines:
        baseline_rows = [row for row in rows if row["agent_id"] == baseline]
        if len(baseline_rows) != 1:
            violations.append(baseline)
            continue
        score = float(baseline_rows[0][score_key])
        baseline_scores[baseline] = score
        if score > oracle_score:
            violations.append(baseline)
    return {
        "oracle_upper_bound_valid": not violations,
        "reason": "oracle_not_worse_than_required_baselines" if not violations else "baseline_exceeded_oracle",
        "oracle_score": oracle_score,
        "baseline_scores": baseline_scores,
        "violations": violations,
    }
