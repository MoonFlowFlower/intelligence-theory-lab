"""Frozen preregistration loader/verifier for TLGP-001B-R2.

The authoritative preregistration is:

    artifacts/TLGP-001B-R2/prereg.json

The canonical hash scheme is the freeze-report scheme:
json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).
No threshold, seed, split, budget, architecture, or verdict constant is
defined here independently; accessors expose values read from the verified JSON.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from src.tlgp_001a import preregistration as A

REPO_ROOT = Path(__file__).resolve().parents[2]
PREREG_JSON_PATH = REPO_ROOT / "artifacts" / "TLGP-001B-R2" / "prereg.json"
FROZEN_PREREG_SHA256 = "6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7"

K: int = A.K
D: int = A.D
M: int = A.M
ACTION_CARD: int = A.ACTION_CARD
N_ADAPT: int = A.N_ADAPT
N_QUERY: int = A.N_QUERY
TRAIN_VALUES = tuple(A.TRAIN_VALUES)
HELDOUT_VALUES = tuple(A.HELDOUT_VALUES)

_CACHE: dict[str, Any] | None = None


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def load_frozen_prereg(verify: bool = True) -> dict[str, Any]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not PREREG_JSON_PATH.exists():
        raise RuntimeError(f"R2 frozen prereg not found: {PREREG_JSON_PATH}")
    obj = json.loads(PREREG_JSON_PATH.read_text(encoding="utf-8"))
    sha = canonical_sha256(obj)
    if verify and sha != FROZEN_PREREG_SHA256:
        raise RuntimeError(
            "TLGP-001B-R2 prereg canonical SHA mismatch; stop before implementation/run. "
            f"computed={sha} expected={FROZEN_PREREG_SHA256}"
        )
    obj["_canonical_sha256_readback"] = sha
    obj["_sha256_match"] = bool(sha == FROZEN_PREREG_SHA256)
    _CACHE = obj
    return obj


def cfg() -> dict[str, Any]:
    return load_frozen_prereg()


def DELTA() -> float:
    return float(cfg()["DELTA"])


def FLOOR() -> float:
    return float(cfg()["FLOOR"])


def N_SEEDS() -> int:
    return int(cfg()["N_SEEDS"])


def close_fraction_min() -> int:
    return int(cfg()["close_fraction_min"])


def seeds() -> dict[str, Any]:
    return dict(cfg()["seed_list"])


def model_seeds() -> list[int]:
    return [int(v) for v in cfg()["seed_list"]["MODEL_SEEDS"]]


def training_budget() -> dict[str, Any]:
    return dict(cfg()["training_budget"])


def capacity_grid() -> dict[str, Any]:
    return dict(cfg()["capacity_grid"])


def family_roles() -> dict[str, Any]:
    return dict(cfg()["family_roles"])


def primary_families() -> list[str]:
    return list(cfg()["family_roles"]["primary_adjudicators"])


def diagnostic_families() -> list[str]:
    return list(cfg()["family_roles"]["diagnostic_only"])


def all_families() -> list[str]:
    return primary_families() + diagnostic_families()


def verdict_enum() -> dict[str, str]:
    raw = cfg()["verdict_enum"]
    return {k: v for k, v in raw.items() if isinstance(v, str) and k != "note"}


def claim_ceiling() -> str:
    return str(cfg()["claim_ceiling"])


def world_cfg() -> dict[str, Any]:
    return dict(cfg()["world"])


def rungs() -> dict[str, Any]:
    return dict(cfg()["rungs"])


def rung1_scanner_cfg() -> dict[str, Any]:
    return dict(cfg()["rung1_scanner"])


def split_construction() -> dict[str, Any]:
    return dict(cfg()["split_construction"])


if __name__ == "__main__":
    c = load_frozen_prereg()
    print(json.dumps({
        "path": str(PREREG_JSON_PATH),
        "canonical_sha256": c["_canonical_sha256_readback"],
        "match": c["_sha256_match"],
        "DELTA": DELTA(),
        "FLOOR": FLOOR(),
        "N_SEEDS": N_SEEDS(),
    }, indent=2, sort_keys=True))

