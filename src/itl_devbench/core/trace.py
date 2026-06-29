from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable

from itl_devbench.core.hashing import sha256_json
from itl_devbench.core.types import Observation, StepRecord

GENESIS_EVENT_HASH = "0" * 64


def make_env_result(obs_after: Observation, reward: float, done: bool, info: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "obs_after": obs_after.to_dict(),
        "reward": reward,
        "done": done,
        "info": info,
    }


def compute_event_hash(event_without_hash: Dict[str, Any]) -> str:
    payload = dict(event_without_hash)
    payload.pop("event_hash", None)
    return sha256_json(payload)


def make_event(record_values: Dict[str, Any], prev_event_hash: str) -> Dict[str, Any]:
    event_without_hash = dict(record_values)
    event_without_hash["prev_event_hash"] = prev_event_hash
    event_without_hash["event_hash"] = ""
    event_hash = compute_event_hash(event_without_hash)
    event_without_hash["event_hash"] = event_hash
    return StepRecord(**event_without_hash).to_dict()


def validate_hash_chain(events: Iterable[Dict[str, Any]]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    prev_hash = GENESIS_EVENT_HASH
    for index, event in enumerate(events):
        if event.get("event_index") != index:
            errors.append(f"event_index_mismatch:{index}")
        if event.get("prev_event_hash") != prev_hash:
            errors.append(f"prev_hash_mismatch:{index}")
        expected_hash = compute_event_hash(event)
        if event.get("event_hash") != expected_hash:
            errors.append(f"event_hash_mismatch:{index}")
        prev_hash = str(event.get("event_hash", ""))
    return not errors, errors


def write_jsonl(path: str | Path, events: Iterable[Dict[str, Any]]) -> None:
    with Path(path).open("w", encoding="utf-8", newline="\n") as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")


def read_jsonl(path: str | Path) -> list[Dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]

