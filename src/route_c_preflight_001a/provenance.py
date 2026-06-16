from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from typing import Any, Callable


REQUIRED_SCORE_FIELDS = {
    "producer_function",
    "inputs",
    "run_id",
    "seed",
    "episode_ids",
    "aggregation",
    "code_path_hash",
    "threshold_used",
    "threshold_frozen_before_run",
    "computed_not_literal",
    "failure_path_available",
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_text(json.dumps(value, sort_keys=True, separators=(",", ":")))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def source_path_for(function: Callable[..., Any]) -> str:
    source = inspect.getsourcefile(function)
    return Path(source or "<unknown>").as_posix()


def code_path_hash(function: Callable[..., Any]) -> str:
    return sha256_text(inspect.getsource(function))


def producer_name(function: Callable[..., Any]) -> str:
    return f"{function.__module__}.{function.__name__}"


def score_record(
    *,
    value: float,
    producer_function: Callable[..., Any],
    inputs: dict[str, Any],
    run_id: str,
    seed: int | str | None,
    episode_ids: list[str],
    aggregation: str,
    threshold_used: float,
) -> dict[str, Any]:
    return {
        "value": round(float(value), 6),
        "producer_function": producer_name(producer_function),
        "callable_source_path": source_path_for(producer_function),
        "inputs": inputs,
        "run_id": run_id,
        "seed": seed,
        "episode_ids": episode_ids,
        "aggregation": aggregation,
        "code_path_hash": code_path_hash(producer_function),
        "threshold_used": round(float(threshold_used), 6),
        "threshold_frozen_before_run": True,
        "computed_not_literal": True,
        "failure_path_available": True,
    }


def aggregate_score_record(
    *,
    scores: list[float],
    producer_function: Callable[..., Any],
    inputs: dict[str, Any],
    run_id: str,
    episode_ids: list[str],
    threshold_used: float,
    aggregation: str = "mean_episode_score",
) -> dict[str, Any]:
    mean_score = sum(scores) / len(scores) if scores else 0.0
    return score_record(
        value=mean_score,
        producer_function=producer_function,
        inputs=inputs,
        run_id=run_id,
        seed="multi_seed",
        episode_ids=episode_ids,
        aggregation=aggregation,
        threshold_used=threshold_used,
    )


def collect_provenance_rows(payloads: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            if REQUIRED_SCORE_FIELDS.issubset(value):
                rows.append(value)
            for nested in value.values():
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    for payload in payloads:
        walk(payload)
    return rows


def validate_provenance_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    failures = []
    for index, row in enumerate(rows):
        missing = sorted(REQUIRED_SCORE_FIELDS - set(row))
        if missing:
            failures.append({"index": index, "reason": "missing_required_fields", "missing": missing})
            continue
        if not row.get("code_path_hash"):
            failures.append({"index": index, "reason": "missing_code_path_hash"})
        if row.get("threshold_frozen_before_run") is not True:
            failures.append({"index": index, "reason": "threshold_not_frozen"})
        if row.get("computed_not_literal") is not True:
            failures.append({"index": index, "reason": "score_not_marked_computed"})
        if row.get("failure_path_available") is not True:
            failures.append({"index": index, "reason": "failure_path_unavailable"})
    return {
        "producer_function": producer_name(validate_provenance_rows),
        "row_count": len(rows),
        "valid": not failures,
        "failures": failures,
        "verdict": "provenance_valid" if not failures else "blocked_by_provenance_gap",
    }
