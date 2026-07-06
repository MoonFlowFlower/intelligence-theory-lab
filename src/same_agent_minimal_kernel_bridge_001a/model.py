from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any


TASK_ID = "SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A"
RUN_ID = "same_agent_minimal_kernel_bridge_001a_tiny_cpu_001"
SCHEMA_VERSION = "same_agent_minimal_kernel_bridge_001a.v1"
BASE_SEED = 20260706
N = 4
L = 5
G = 2
EQUIVALENCE_BAND = 0.01
DEGRADATION_MIN = 0.20
ARTIFACT_DIR_REL = "artifacts/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A"
CLAIM_CEILING = (
    "bounded offline minimal runtime-kernel contrast evidence only; no mechanism "
    "validity, no agency, no autonomy, no subjectivity, no consciousness, no EGO "
    "readiness, and no mainline effect"
)

TRAIN_SLICES_BY_EPISODE: tuple[tuple[tuple[int, int], ...], ...] = (
    ((0, 0), (1, 0), (1, 1)),
    ((0, 0), (1, 0), (1, 1)),
    ((0, 0), (2, 1), (2, 2), (3, 2), (3, 3), (0, 3)),
    ((0, 0), (2, 1), (2, 2), (3, 2), (3, 3), (0, 3)),
)
REGIME_SEQUENCE: tuple[int, ...] = (0, 1, 0, 1)
HELDOUT_CELLS: tuple[tuple[int, int], ...] = ((0, 1), (1, 2), (2, 3), (3, 0))
ANCHOR_CELL = (0, 0)


@dataclass(frozen=True)
class RegimeCode:
    a: tuple[int, ...]
    b: tuple[int, ...]


def stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: Any) -> str:
    return hashlib.sha256(stable_json(data).encode("utf-8")).hexdigest()


def derive_seed(*parts: Any, base_seed: int = BASE_SEED) -> int:
    digest = hashlib.sha256(str(base_seed).encode("utf-8"))
    for part in parts:
        digest.update(b"\0")
        digest.update(repr(part).encode("utf-8"))
    return int.from_bytes(digest.digest()[:8], "big") % (2**32)


def _random_code(rng: random.Random) -> RegimeCode:
    return RegimeCode(
        a=tuple(rng.randrange(L) for _ in range(N)),
        b=tuple(rng.randrange(L) for _ in range(N)),
    )


def build_regime_codes(seed: int = BASE_SEED) -> tuple[RegimeCode, ...]:
    """Build latent additive codes; codes are audit-only and never candidate inputs."""

    rng = random.Random(derive_seed("regime_codes", seed))
    codes: list[RegimeCode] = []
    anchor_outcomes: set[int] = set()
    attempts = 0
    while len(codes) < G:
        attempts += 1
        if attempts > 10_000:
            raise RuntimeError("could not derive distinct anchor outcomes")
        code = _random_code(rng)
        anchor = outcome_for_code(code, *ANCHOR_CELL)
        if anchor in anchor_outcomes:
            continue
        codes.append(code)
        anchor_outcomes.add(anchor)
    return tuple(codes)


def outcome_for_code(code: RegimeCode, row: int, col: int) -> int:
    return (int(code.a[int(row)]) + int(code.b[int(col)])) % L


def candidate_observation(row: int, col: int, episode_id: str, step_index: int) -> dict[str, Any]:
    return {
        "schema_version": "same_agent_minimal_kernel_observation.v1",
        "episode_id": episode_id,
        "step_index": int(step_index),
        "row_factor": int(row),
        "col_factor": int(col),
        "phase": "train",
    }


def build_deployment(seed: int = BASE_SEED) -> dict[str, Any]:
    codes = build_regime_codes(seed)
    episodes: list[dict[str, Any]] = []
    for episode_index, regime_index in enumerate(REGIME_SEQUENCE):
        episode_id = f"episode_{episode_index:02d}"
        cells = TRAIN_SLICES_BY_EPISODE[episode_index]
        observations = []
        for step_index, (row, col) in enumerate(cells):
            observations.append(
                {
                    "observation": candidate_observation(row, col, episode_id, step_index),
                    "feedback": {"outcome": outcome_for_code(codes[regime_index], row, col)},
                    "cell": [int(row), int(col)],
                }
            )
        episodes.append(
            {
                "episode_id": episode_id,
                "episode_index": episode_index,
                "observations": observations,
                "audit_regime_index": regime_index,
            }
        )
    context_keys = {
        str(regime_index): context_key_from_anchor(outcome_for_code(code, *ANCHOR_CELL))
        for regime_index, code in enumerate(codes)
    }
    heldout_cases: list[dict[str, Any]] = []
    for regime_index, code in enumerate(codes):
        for row, col in HELDOUT_CELLS:
            heldout_cases.append(
                {
                    "case_id": f"regime_{regime_index}_heldout_{row}_{col}",
                    "context_key": context_keys[str(regime_index)],
                    "context_feedback": {"anchor_outcome": outcome_for_code(code, *ANCHOR_CELL)},
                    "observation": {
                        "schema_version": "same_agent_minimal_kernel_observation.v1",
                        "row_factor": int(row),
                        "col_factor": int(col),
                        "phase": "heldout",
                    },
                    "outcome": outcome_for_code(code, row, col),
                    "audit_regime_index": regime_index,
                }
            )
    return {
        "task_id": TASK_ID,
        "schema_version": SCHEMA_VERSION,
        "seed": seed,
        "n": N,
        "l": L,
        "g": G,
        "episodes": episodes,
        "heldout_cases": heldout_cases,
        "context_keys": context_keys,
        "audit_regime_code_hashes": [stable_hash({"a": code.a, "b": code.b}) for code in codes],
    }


def context_key_from_anchor(anchor_outcome: int) -> str:
    return f"anchor_feedback:{int(anchor_outcome)}"


def initial_state() -> dict[str, Any]:
    return {
        "schema_version": "same_agent_minimal_kernel_state.v1",
        "active_context_key": None,
        "memory_events": [],
        "consolidated_models": {},
        "prediction_error_state": {"last_error": None, "cumulative_abs_error": 0},
        "update_counter": 0,
        "last_replay_event_id": None,
    }


def serialize_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "serialization_schema": "same_agent_minimal_kernel_serialized_state.v1",
        "state": json.loads(stable_json(state)),
        "state_hash": stable_hash(state),
    }


def solve_additive_model(events: list[dict[str, Any]], *, model_id_prefix: str) -> dict[str, Any]:
    row_values: dict[int, int] = {}
    col_values: dict[int, int] = {}
    contradictions: list[dict[str, int]] = []
    if not events:
        return {
            "model_id": stable_hash({"prefix": model_id_prefix, "events": []}),
            "row_values": {},
            "col_values": {},
            "event_ids": [],
            "connected": False,
            "contradiction_count": 0,
        }

    first = events[0]
    row_values[int(first["row_factor"])] = 0
    changed = True
    while changed:
        changed = False
        for event in events:
            row = int(event["row_factor"])
            col = int(event["col_factor"])
            y = int(event["outcome"])
            if row in row_values and col not in col_values:
                col_values[col] = (y - row_values[row]) % L
                changed = True
            if col in col_values and row not in row_values:
                row_values[row] = (y - col_values[col]) % L
                changed = True
            if row in row_values and col in col_values and (row_values[row] + col_values[col]) % L != y:
                contradictions.append({"row": row, "col": col, "outcome": y})

    event_ids = [str(event["memory_event_id"]) for event in events]
    payload = {
        "prefix": model_id_prefix,
        "row_values": row_values,
        "col_values": col_values,
        "event_ids": event_ids,
        "contradiction_count": len(contradictions),
    }
    return {
        "model_id": stable_hash(payload),
        "row_values": {str(key): value for key, value in sorted(row_values.items())},
        "col_values": {str(key): value for key, value in sorted(col_values.items())},
        "event_ids": event_ids,
        "connected": len(row_values) == N and len(col_values) == N,
        "contradiction_count": len(contradictions),
    }


def predict_from_model(model: dict[str, Any] | None, row: int, col: int) -> int:
    if not model:
        return 0
    row_values = model.get("row_values", {})
    col_values = model.get("col_values", {})
    if str(int(row)) not in row_values or str(int(col)) not in col_values:
        return 0
    return (int(row_values[str(int(row))]) + int(col_values[str(int(col))])) % L
