"""Adapters for the Phase-A borrow-first headroom probe.

Adapters expose the frozen ``(O, y, y*)`` record interface.  Official control
and borrowed-env scoring is intentionally not invoked by Phase-A tests.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import random
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class ProbeRecord:
    record_id: str
    split: str
    group_id: str
    O: dict[str, Any]
    y: tuple[str, ...]
    y_star: tuple[str, ...]

    def to_json_obj(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "split": self.split,
            "group_id": self.group_id,
            "O": self.O,
            "y": list(self.y),
            "y_star": list(self.y_star),
        }


@dataclass(frozen=True)
class AdapterSpec:
    env_id: str
    source: str
    status: str
    build_records: Callable[[int], list[ProbeRecord]]


def _label(value: int | str) -> tuple[str, ...]:
    return (str(value),)


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def record_digest(records: Iterable[ProbeRecord]) -> str:
    payload = [record.to_json_obj() for record in records]
    return sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def build_unit_synthetic_records(seed: int = 0) -> list[ProbeRecord]:
    """Tiny synthetic fixture for tests and fresh-process plumbing only."""

    rng = random.Random(int(seed))
    records: list[ProbeRecord] = []
    for split in ("train", "eval"):
        for idx in range(6):
            value = idx % 3
            target = "good" if value == 0 else "bad"
            records.append(
                ProbeRecord(
                    record_id=f"unit-{split}-{idx}",
                    split=split,
                    group_id="unit",
                    O={
                        "schema_version": "env_headroom_probe.observation.v1",
                        "unit_value": value,
                        "cache_key": f"k{value}",
                        "lookup_key": f"k{value}",
                        "frequency_value": f"v{value}",
                        "jitter": rng.randrange(10_000),
                    },
                    y=(target,),
                    y_star=(target,),
                )
            )
    return records


def build_pos_internal_estar_records(seed: int = 20260708) -> list[ProbeRecord]:
    """Build the internal E* positive-control record interface.

    This encodes the R4 E* additive Latin-square structure as legal observations
    with latent row/column codes absent.  Fair cache-like baselines see only
    row/column factor ids and train examples; the ideal/oracle receives y*.
    """

    rng = random.Random(int(seed))
    n = 5
    L = 5
    a_code = list(range(L))
    b_code = [2, 4, 1, 3, 0]
    train_cells = {(r, 0) for r in range(n)} | {(0, k) for k in range(n)}
    records: list[ProbeRecord] = []
    for r in range(n):
        for k in range(n):
            split = "train" if (r, k) in train_cells else "eval"
            y = (a_code[r] + b_code[k]) % L
            # No relation table, no latent code, no answer-bearing filename.
            obs = {
                "schema_version": "env_headroom_probe.observation.v1",
                "env_family": "R4_ESTAR_ADDITIVE_LATIN",
                "row_factor": r,
                "col_factor": k,
                "cache_key": f"cell:{r}:{k}",
                "lookup_key": f"cell:{r}:{k}",
                "frequency_value": f"row:{r}",
                "one_factor_signature": f"row:{r}" if rng.random() < 0.5 else f"col:{k}",
            }
            records.append(
                ProbeRecord(
                    record_id=f"estar-{split}-r{r}-k{k}",
                    split=split,
                    group_id="estar",
                    O=obs,
                    y=_label(y),
                    y_star=_label(y),
                )
            )
    return records


def build_neg_5a846d5_scout_records(seed: int = 20260706) -> list[ProbeRecord]:
    """Adapt the lookup-solvable 5a846d5 scout into the common interface.

    The current source tree for ``src/sbmc_headroom_scout_001a`` has no source
    diff against commit ``5a846d5`` for the package files.  This adapter imports
    that frozen generator shape read-only and converts records.  It does not
    write artifacts.
    """

    from src.sbmc_headroom_scout_001a import gen_model as GM

    records: list[ProbeRecord] = []
    user_ids = [100, 101, 102, 103]
    for user_id in user_ids:
        case = GM.build_user_case(user_id)
        for split_name, items in (("train", case["trusted_seed"]), ("eval", case["test_set"])):
            for item in items:
                item_repr = item["item_repr"]
                edge = tuple(int(x) for x in item_repr["edge"])
                asserted = item_repr["asserted_tuple"]
                pair = (int(asserted[0][1]), int(asserted[1][1]))
                label = "contaminated" if item["audit"]["label_binary"] else "genuine"
                obs = {
                    "schema_version": "env_headroom_probe.observation.v1",
                    "env_family": "P0.5_SBMC_SCOUT_5a846d5",
                    "user_id": int(user_id),
                    "edge": list(edge),
                    "asserted_tuple": asserted,
                    "lookup_key": f"u{user_id}:edge{edge}:first{pair[0]}",
                    "cache_key": f"edge{edge}:pair{pair}",
                    "frequency_value": f"attr{asserted[1][0]}:value{asserted[1][1]}",
                    "relation_pairs": [list(p) for p in GM.RELATION_TABLES[edge]],
                }
                records.append(
                    ProbeRecord(
                        record_id=f"5a846d5-{item['item_id']}",
                        split=split_name,
                        group_id=f"user:{user_id}",
                        O=obs,
                        y=(label,),
                        y_star=(label,),
                    )
                )
    _ = seed
    return records


ADAPTERS: dict[str, AdapterSpec] = {
    "UNIT_SYNTHETIC": AdapterSpec(
        env_id="UNIT_SYNTHETIC",
        source="unit-test synthetic fixture; not an official control or candidate env",
        status="phase_a_unit_only",
        build_records=build_unit_synthetic_records,
    ),
    "POS_INTERNAL_ESTAR": AdapterSpec(
        env_id="POS_INTERNAL_ESTAR",
        source="docs/codex/tasks/SAME-AGENT-KERNEL-R4-CONCRETE-ENV-ARGUMENT-001A.md",
        status="phase_a_registered_control_unscored_until_phase_b_authorized",
        build_records=build_pos_internal_estar_records,
    ),
    "NEG_5A846D5_SCOUT": AdapterSpec(
        env_id="NEG_5A846D5_SCOUT",
        source="git commit 5a846d51e / src/sbmc_headroom_scout_001a",
        status="phase_a_registered_control_unscored_until_phase_b_authorized",
        build_records=build_neg_5a846d5_scout_records,
    ),
}
