from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from itl_devbench.core.hashing import sha256_file, sha256_json


def compute_graph_cache_saturation_report(
    family_metric_summary: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    generator_cfg = config.get("task_family_generator_001c", {})
    threshold_cfg = generator_cfg.get("graph_cache_saturation_threshold", {})
    max_saturated = int(threshold_cfg.get("max_saturated_target_families", 2))
    gap_threshold = float(threshold_cfg.get("saturation_gap_to_oracle", 1.0))

    saturated = []
    for row in family_metric_summary.get("families", []):
        gap = row.get("graph_cache_gap_to_oracle")
        if gap is not None and float(gap) <= gap_threshold:
            saturated.append(
                {
                    "family_id": row["family_id"],
                    "oracle_score": row.get("oracle_score"),
                    "graph_cache_score": row.get("graph_cache_score"),
                    "graph_cache_gap_to_oracle": gap,
                    "target_pressure": row.get("target_pressure", []),
                }
            )

    too_many = len(saturated) > max_saturated
    report = {
        "producer_function": "itl_devbench.eval.saturation.compute_graph_cache_saturation_report",
        "graph_cache_cache_scope": "per_episode",
        "graph_cache_scope_contract": {
            "may_store": "observed_observation_action_outcome_tuples",
            "hidden_state_access": "forbidden",
            "future_outcome_access": "forbidden",
            "cross_seed_or_rule_seed_cache_sharing": "forbidden",
            "cross_split_cache_sharing": "forbidden",
            "scope_label": "per_episode",
        },
        "saturation_gap_to_oracle": gap_threshold,
        "max_saturated_target_families": max_saturated,
        "saturated_target_family_count": len(saturated),
        "saturated_families": saturated,
        "too_many_saturated": too_many,
        "verdict": (
            "graph_cache_saturation_exceeds_threshold"
            if too_many
            else "graph_cache_saturation_within_threshold"
        ),
        "code_path_hash": sha256_file(Path(__file__)),
    }
    report["report_hash"] = sha256_json(report)
    return report


def write_saturation_report(path: str | Path, payload: Dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
