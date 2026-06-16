"""Isolated local ACP-BV 001B distribution harness."""

from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from typing import Any, Callable


TASK_ID = "ACP-BV-DISTRIBUTION-HARNESS-001B-EXECUTION-001A"
CURRENT_LAYER = "engineering implementation / local ACP-BV 001B harness execution only"
CLAIM_CEILING = "ACP-BV 001B local harness implementation and computed-evidence artifact generation only"
START_COMMIT = "55e79259203f0544e9256befcc0c82ea668d2381"
START_TAG = "remote-anchor-acp-bv-001b-implementation-task-card-revision-001a-55e7925"
SEEDS = [1009, 2027, 3037, 4049, 5051]
EQUIVALENCE_BAND = 0.02
EFFECT_THRESHOLD = 0.05

WHAT_THIS_DOES_NOT_PROVE = [
    "ACP-BV validity",
    "mechanism validity",
    "harness validity beyond local implementation evidence",
    "Gate validity",
    "bridge, admission, runtime, scheduler, live, or mainline readiness",
    "agency, consciousness, emotion, autonomy, stable user benefit, or EGO readiness",
]


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


def provenance_for(
    function: Callable[..., Any],
    *,
    inputs: dict[str, Any],
    run_id: str,
    seed: int | str | None,
    context_episode_ids: list[str],
    aggregation_method: str,
    output_artifact_path: Path,
) -> dict[str, Any]:
    return {
        "producer_function": f"{function.__module__}.{function.__name__}",
        "callable_source_path": source_path_for(function),
        "inputs": inputs,
        "run_id": run_id,
        "seed": seed,
        "context_episode_ids": context_episode_ids,
        "aggregation_method": aggregation_method,
        "code_path_hash": code_path_hash(function),
        "source_blob_hash_or_git_object_pin": code_path_hash(function),
        "output_artifact_path": output_artifact_path.as_posix(),
    }


def classify_b3_delta(delta: float) -> str:
    if abs(delta) <= EQUIVALENCE_BAND:
        return "baseline_equivalent"
    if delta >= EFFECT_THRESHOLD:
        return "candidate_exits_equivalence_band"
    return "inconclusive"


def episode_ids(episodes: list[dict[str, Any]]) -> list[str]:
    return [str(episode["episode_id"]) for episode in episodes]
