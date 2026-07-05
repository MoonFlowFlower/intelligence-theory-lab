"""Frozen pre-registration MIRROR + verifier for TLGP-001B.

This module is NOT the authoritative pre-registration. The authoritative artifact is the
frozen JSON at artifacts/TLGP-001B/prereg.json, whose CANONICAL sha256 (json.dumps with
sort_keys=True, separators=(",",":"), ensure_ascii=True) is:

    c9f4ba279b75cfc1753a6c6586f11708a9d561bbbff82e8db98859165c580d41

This module LOADS that JSON, recomputes the canonical sha256, and asserts it equals the
frozen constant before exposing any value. No threshold, capacity grid, seed, split, or
training-budget value is *defined* here -- every such value is READ from the frozen JSON,
so the experiment cannot be silently tuned by editing Python. World/size constants
(K, D, M, ACTION_CARD, N_ADAPT, N_QUERY) are sourced read-only from the frozen TLGP-001A
preregistration, which is the world this experiment inherits.

If the canonical sha256 does not match, load_frozen_prereg() raises -- the harness must
STOP and report INVALID (prereg hash mismatch) rather than run against an unverified spec.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

# Read-only import of the inherited 001A world/size constants (allowlisted module).
from src.tlgp_001a import preregistration as A

REPO_ROOT = Path(__file__).resolve().parents[2]
PREREG_JSON_PATH = REPO_ROOT / "artifacts" / "TLGP-001B" / "prereg.json"

# The single authorized frozen canonical sha256 (operator-supplied, matches PREREG_FREEZE_REPORT.md).
FROZEN_PREREG_SHA256 = "c9f4ba279b75cfc1753a6c6586f11708a9d561bbbff82e8db98859165c580d41"

# --- inherited world / size constants (read-only from 001A) --------------------
K: int = A.K                       # modulus AND number of effect classes (= 5)
D: int = A.D                       # number of symbol properties (= 3)
M: int = A.M                       # property cardinality (= 5)
ACTION_CARD: int = A.ACTION_CARD   # actions 0..ACTION_CARD-1 (= 5)
N_ADAPT: int = A.N_ADAPT           # adaptation interactions per episode (= 24)
N_QUERY: int = A.N_QUERY           # held-out queries per episode (= 30)
TRAIN_VALUES = tuple(A.TRAIN_VALUES)     # (0, 1, 2)
HELDOUT_VALUES = tuple(A.HELDOUT_VALUES)  # (3, 4)


def _canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(_canonical_bytes(obj)).hexdigest()


_CACHE: Dict[str, Any] | None = None


def load_frozen_prereg(verify: bool = True) -> Dict[str, Any]:
    """Load the frozen prereg JSON and verify its canonical sha256.

    Raises RuntimeError on mismatch (caller must STOP / report INVALID).
    """
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not PREREG_JSON_PATH.exists():
        raise RuntimeError(f"frozen prereg not found at {PREREG_JSON_PATH}")
    obj = json.loads(PREREG_JSON_PATH.read_text(encoding="utf-8"))
    sha = canonical_sha256(obj)
    if verify and sha != FROZEN_PREREG_SHA256:
        raise RuntimeError(
            "FROZEN PREREG HASH MISMATCH -> STOP (report INVALID). "
            f"computed canonical sha256={sha} expected={FROZEN_PREREG_SHA256}"
        )
    obj["_canonical_sha256_readback"] = sha
    obj["_sha256_match"] = bool(sha == FROZEN_PREREG_SHA256)
    _CACHE = obj
    return obj


# --- convenience typed accessors (all READ from the frozen JSON) ---------------
def cfg() -> Dict[str, Any]:
    return load_frozen_prereg()


def DELTA() -> float:
    return float(cfg()["DELTA"])


def FLOOR() -> float:
    return float(cfg()["FLOOR"])


def N_SEEDS() -> int:
    return int(cfg()["N_SEEDS"])


def seeds() -> Dict[str, Any]:
    return cfg()["seed_list"]


def model_seeds() -> list:
    return list(cfg()["seed_list"]["MODEL_SEEDS"])


def capacity_grid() -> Dict[str, Any]:
    return cfg()["capacity_grid"]


def saturation_witnesses() -> Dict[str, str]:
    return cfg()["capacity_grid"]["saturation_witnesses"]


def training_budget() -> Dict[str, Any]:
    return cfg()["training_budget"]


def verdict_enum() -> Dict[str, Any]:
    return cfg()["verdict_enum"]


def panel() -> Dict[str, Any]:
    return cfg()["panel"]


def split_construction() -> Dict[str, Any]:
    return cfg()["split_construction"]


def claim_ceiling() -> str:
    return str(cfg()["claim_ceiling"])


if __name__ == "__main__":
    c = load_frozen_prereg()
    print("frozen prereg canonical sha256 readback:", c["_canonical_sha256_readback"])
    print("matches authorized frozen sha256:", c["_sha256_match"])
    print("DELTA", DELTA(), "FLOOR", FLOOR(), "N_SEEDS", N_SEEDS())
    print("model seeds", model_seeds())
    print("witnesses", saturation_witnesses())
