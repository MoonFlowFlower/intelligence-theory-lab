"""Frozen pure adjudicator for TLGP rung3 identifiability probe 001A."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

PREREG_PATH = Path(__file__).resolve().parents[2] / "artifacts" / "TLGP-001B-R2" / "prereg.json"
FROZEN_PREREG_SHA256 = "6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7"

TERMINAL_CEILING = "route_closed_identifiability_ceiling"
TERMINAL_HEADROOM = "rung3_headroom_exists_authorize_powered_learner"
TERMINAL_REDUNDANT = "route_needs_world_rung_redesign"
TERMINAL_INCONCLUSIVE = "inconclusive_underpowered"
TERMINAL_LEAKAGE = "invalid_leakage"


def _canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def load_prereg(verify: bool = True) -> tuple[dict[str, Any], str]:
    obj = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    sha = _canonical_sha256(obj)
    if verify and sha != FROZEN_PREREG_SHA256:
        raise RuntimeError(f"prereg canonical sha mismatch: computed={sha} expected={FROZEN_PREREG_SHA256}")
    return obj, sha


def _headroom_stats(values: list[float]) -> dict[str, Any]:
    arr = np.array([float(v) for v in values], dtype=float)
    if arr.size == 0:
        return {"mean": 0.0, "std": 0.0, "lcb": 0.0, "n": 0}
    mean = float(np.mean(arr))
    std = float(np.std(arr))
    lcb = float(mean - 2.0 * std / math.sqrt(int(arr.size)))
    return {"mean": mean, "std": std, "lcb": lcb, "n": int(arr.size)}


def compute_route_decision(
    recorded: dict[str, Any],
    prereg: dict[str, Any] | None = None,
    prereg_sha: str | None = None,
) -> dict[str, Any]:
    """Return exactly one terminal from recorded candidate-free probe metrics."""
    if prereg is None or prereg_sha is None:
        prereg, prereg_sha = load_prereg()
    delta = float(prereg["DELTA"])
    floor = float(prereg["FLOOR"])
    need = int(prereg["close_fraction_min"])
    n_required = int(prereg["N_SEEDS"])

    per_seed_headroom = [float(v) for v in recorded.get("per_seed_headroom", [])]
    stats = _headroom_stats(per_seed_headroom)
    n_observed = int(recorded.get("n_seeds", stats["n"]))
    fair_saturation_seed_count = int(
        recorded.get(
            "fair_saturation_seed_count",
            sum(1 for v in per_seed_headroom if float(v) <= delta),
        )
    )
    controls_passed = bool(recorded.get("controls_passed", False))
    leakage_clean = bool(recorded.get("leakage_clean", False))
    ideal_degenerate = bool(recorded.get("ideal_degenerate", False))
    no_adaptation_matches_ideal = bool(recorded.get("no_adaptation_matches_ideal", False))
    predict_all_or_majority_match_ideal = bool(recorded.get("predict_all_or_majority_match_ideal", False))
    ci_straddles = bool(recorded.get("ci_straddles_epsilon", False))
    control_role = str(recorded.get("control_role", ""))

    detail = {
        "task_id": recorded.get("task_id"),
        "split": recorded.get("split"),
        "DELTA": delta,
        "FLOOR": floor,
        "close_fraction_min": need,
        "N_SEEDS": n_required,
        "n_seeds_observed": n_observed,
        "per_seed_headroom": per_seed_headroom,
        "mean_headroom": stats["mean"],
        "std_headroom": stats["std"],
        "lcb_headroom": stats["lcb"],
        "fair_saturation_seed_count": fair_saturation_seed_count,
        "controls_passed": controls_passed,
        "leakage_clean": leakage_clean,
        "ideal_degenerate": ideal_degenerate,
        "no_adaptation_matches_ideal": no_adaptation_matches_ideal,
        "predict_all_or_majority_match_ideal": predict_all_or_majority_match_ideal,
        "ci_straddles_epsilon": ci_straddles,
        "control_role": control_role,
        "prereg_sha256": prereg_sha,
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a.rung3_identifiability_adjudicator"
            ".compute_route_decision"
        ),
    }

    if not leakage_clean:
        route, reason = TERMINAL_LEAKAGE, "leakage detector not clean on an agent input channel"
    elif control_role == "negative_no_signal" and (ideal_degenerate or no_adaptation_matches_ideal):
        route, reason = TERMINAL_INCONCLUSIVE, "deliberate negative control has no usable signal"
    elif ideal_degenerate or no_adaptation_matches_ideal:
        route, reason = TERMINAL_REDUNDANT, "ideal degenerate or no_adaptation matches ideal within DELTA"
    elif not controls_passed:
        route, reason = TERMINAL_INCONCLUSIVE, "instrument controls did not pass cleanly"
    elif fair_saturation_seed_count >= need or predict_all_or_majority_match_ideal:
        route, reason = TERMINAL_CEILING, "fair panel saturates the ideal headroom on enough seeds"
    elif n_observed < n_required or ci_straddles:
        route, reason = TERMINAL_INCONCLUSIVE, "seed count underpowered or confidence interval straddles DELTA"
    elif stats["lcb"] > delta:
        route, reason = TERMINAL_HEADROOM, "LCB(headroom) exceeds DELTA with controls and leakage clean"
    else:
        route, reason = TERMINAL_INCONCLUSIVE, "not saturated, but LCB(headroom) does not clear DELTA"

    return {"route": route, "reason": reason, "detail": detail}


def self_test() -> dict[str, Any]:
    prereg, prereg_sha = load_prereg()
    cases = {
        TERMINAL_LEAKAGE: {
            "controls_passed": True,
            "leakage_clean": False,
            "per_seed_headroom": [0.2] * 10,
        },
        TERMINAL_REDUNDANT: {
            "controls_passed": True,
            "leakage_clean": True,
            "ideal_degenerate": True,
            "per_seed_headroom": [0.2] * 10,
        },
        TERMINAL_INCONCLUSIVE: {
            "controls_passed": True,
            "leakage_clean": True,
            "per_seed_headroom": [0.08, 0.09, 0.11, 0.12],
            "fair_saturation_seed_count": 2,
            "n_seeds": 4,
        },
        TERMINAL_CEILING: {
            "controls_passed": True,
            "leakage_clean": True,
            "per_seed_headroom": [0.05] * 9 + [0.2],
            "fair_saturation_seed_count": 9,
        },
        TERMINAL_HEADROOM: {
            "controls_passed": True,
            "leakage_clean": True,
            "per_seed_headroom": [0.2] * 10,
            "fair_saturation_seed_count": 0,
        },
    }
    observed: dict[str, str] = {}
    for expected, record in cases.items():
        decision = compute_route_decision(record, prereg=prereg, prereg_sha=prereg_sha)
        observed[expected] = str(decision["route"])
        if decision["route"] != expected:
            raise RuntimeError(f"adjudicator self-test failed: expected {expected}, got {decision['route']}")
    return {
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a.rung3_identifiability_adjudicator.self_test"
        ),
        "prereg_sha256": prereg_sha,
        "reachable_terminals": list(observed.values()),
        "cases": observed,
    }
