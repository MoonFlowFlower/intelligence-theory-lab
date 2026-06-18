from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from typing import Any, Callable


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: str | Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def stable_json_hash(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return sha256_bytes(data)


def code_path_hash(func: Callable[..., Any]) -> str:
    try:
        source = inspect.getsource(func)
    except (OSError, TypeError):
        source = repr(func)
    return sha256_bytes(source.encode("utf-8"))


def write_json(path: str | Path, payload: Any) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    text = "".join(json.dumps(row, sort_keys=True, default=str) + "\n" for row in rows)
    Path(path).write_text(text, encoding="utf-8")


def evidence_row(
    *,
    result_name: str,
    value: Any,
    producer_function: str,
    producer_module: str,
    code_path_hash_value: str,
    inputs: list[str],
    run_id: str,
    seed_id_or_seed_set: Any,
    episode_ids: list[str],
    aggregation: str,
    baseline_family: str,
    applicability_status: str,
    consumed_by_final_verdict: bool = True,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "result_name": result_name,
        "value": value,
        "producer_function": producer_function,
        "producer_module": producer_module,
        "code_path_hash": code_path_hash_value,
        "inputs": inputs,
        "run_id": run_id,
        "seed_id_or_seed_set": seed_id_or_seed_set,
        "episode_ids": episode_ids,
        "aggregation": aggregation,
        "baseline_family": baseline_family,
        "applicability_status": applicability_status,
        "consumed_by_final_verdict": consumed_by_final_verdict,
        "details": details or {},
    }
