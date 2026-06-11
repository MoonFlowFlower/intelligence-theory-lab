from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path | str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            rows.append(json.loads(line))
    return rows


def score_behavior_traces(traces: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(traces)
    successes = sum(
        1
        for trace in traces
        if trace["candidate"]["selected_action"] in trace["public_outcome"]["acceptable_actions"]
    )
    replay_matches = sum(
        1
        for trace in traces
        if trace["candidate"]["selected_action"] == trace["behavior_replay"]["reconstructed_action"]
    )
    template_counts: dict[str, int] = {}
    template_successes: dict[str, int] = {}
    for trace in traces:
        template = trace["public_outcome"]["template_handle"]
        template_counts[template] = template_counts.get(template, 0) + 1
        if trace["candidate"]["selected_action"] in trace["public_outcome"]["acceptable_actions"]:
            template_successes[template] = template_successes.get(template, 0) + 1
    per_template_success_rate = {
        template: round(template_successes.get(template, 0) / count, 6)
        for template, count in sorted(template_counts.items())
    }
    return {
        "overall_success_rate": round(successes / total, 6) if total else 0.0,
        "per_template_success_rate": per_template_success_rate,
        "min_template_success_rate": min(per_template_success_rate.values()) if per_template_success_rate else 0.0,
        "behavior_only_replay_match": replay_matches == total,
        "reconstructed_decisions": replay_matches,
        "total_decisions": total,
    }


def score_trace_file(path: Path | str) -> dict[str, Any]:
    return score_behavior_traces(load_jsonl(path))
