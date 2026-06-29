"""Pure R2 seven-terminal verdict function and synthetic tamper coverage."""
from __future__ import annotations

import math
from copy import deepcopy
from typing import Any

import numpy as np

from . import preregistration as P

TERMINAL_KEY_BY_ENUM_KEY = {
    "H1_bank_within_episode": "h1_survives",
    "H0_downgrade": "h0_amortized",
    "invalid_leakage_or_replay": "invalid_integrity",
    "invalid_learnability_floor_failed": "invalid_learnability_floor",
    "invalid_no_capability_witness": "invalid_no_capability_witness",
    "invalid_discriminativeness_or_ablation": "invalid_discriminativeness_or_ablation",
    "invalid_inconclusive_underpowered": "invalid_inconclusive_underpowered",
}


def lcb(values: list[float]) -> float:
    if not values:
        return 0.0
    arr = np.asarray(values, dtype=float)
    return float(arr.mean() - 2.0 * arr.std(ddof=0) / math.sqrt(max(1, len(values))))


def _close_count(values: list[float]) -> int:
    return sum(1 for v in values if float(v) <= P.DELTA())


def compute_verdict(recorded: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Compute the frozen seven-terminal R2 verdict from recorded fields only.

    Required shape:
      integrity: planted_leak_uncaught, clean_false_flag, replay_exact_by_rung
      rung0_pass_by_family: {family: bool}
      rung1_pass_by_family: {family: bool}
      context_ablation_collapse_by_family: {family: bool}
      shuffle_collapse_by_family: {family: bool}
      rung3_headroom_by_family: {family: [per-seed headroom]}
    """
    enums = P.verdict_enum()
    primary = P.primary_families()
    integrity = recorded["integrity"]
    replay_exact_by_rung = dict(integrity.get("replay_exact_by_rung", {}))
    integrity_invalid = bool(
        integrity.get("planted_leak_uncaught", False)
        or integrity.get("clean_false_flag", False)
        or any(not bool(v) for v in replay_exact_by_rung.values())
    )
    rung0 = {f: bool(recorded["rung0_pass_by_family"].get(f, False)) for f in primary}
    rung1 = {f: bool(recorded["rung1_pass_by_family"].get(f, False)) for f in primary}
    eligible = [f for f in primary if rung0[f] and rung1[f]]
    ctx = {f: bool(recorded["context_ablation_collapse_by_family"].get(f, False)) for f in primary}
    shuf = {f: bool(recorded["shuffle_collapse_by_family"].get(f, False)) for f in primary}
    hr = {f: [float(v) for v in recorded["rung3_headroom_by_family"].get(f, [])] for f in primary}
    close_counts = {f: _close_count(hr[f]) for f in primary}
    need_close = int(P.close_fraction_min())
    lcb_by_family = {f: lcb(hr[f]) for f in primary}

    if integrity_invalid:
        enum_key = "invalid_leakage_or_replay"
        branch_index = 1
    elif not any(rung0.values()):
        enum_key = "invalid_learnability_floor_failed"
        branch_index = 2
    elif any(rung0.values()) and not eligible:
        enum_key = "invalid_no_capability_witness"
        branch_index = 3
    elif any((not ctx[f]) or (not shuf[f]) for f in eligible):
        enum_key = "invalid_discriminativeness_or_ablation"
        branch_index = 4
    elif any(close_counts[f] >= need_close for f in eligible):
        enum_key = "H0_downgrade"
        branch_index = 5
    elif (
        set(eligible) >= set(primary)
        and all(lcb_by_family[f] > P.DELTA() for f in primary)
        and all(ctx[f] and shuf[f] for f in primary)
    ):
        enum_key = "H1_bank_within_episode"
        branch_index = 6
    else:
        enum_key = "invalid_inconclusive_underpowered"
        branch_index = 7

    detail = {
        "branch_index": branch_index,
        "terminal_key": TERMINAL_KEY_BY_ENUM_KEY[enum_key],
        "eligible_primary_families": eligible,
        "rung0_pass_by_family": rung0,
        "rung1_pass_by_family": rung1,
        "context_ablation_collapse_by_family": ctx,
        "shuffle_collapse_by_family": shuf,
        "rung3_close_counts": close_counts,
        "rung3_lcb_by_family": lcb_by_family,
        "need_close": need_close,
        "DELTA": P.DELTA(),
        "FLOOR": P.FLOOR(),
    }
    return enums[enum_key], detail


def _base_h1_fixture() -> dict[str, Any]:
    primary = P.primary_families()
    return {
        "integrity": {
            "planted_leak_uncaught": False,
            "clean_false_flag": False,
            "replay_exact_by_rung": {"rung0": True, "rung1": True, "rung2": True, "rung3": True},
        },
        "rung0_pass_by_family": {f: True for f in primary},
        "rung1_pass_by_family": {f: True for f in primary},
        "context_ablation_collapse_by_family": {f: True for f in primary},
        "shuffle_collapse_by_family": {f: True for f in primary},
        "rung3_headroom_by_family": {f: [P.DELTA() + 0.15] * P.N_SEEDS() for f in primary},
    }


def synthetic_tamper_coverage() -> dict[str, Any]:
    primary = P.primary_families()

    fixtures: dict[str, dict[str, Any]] = {}
    fixtures["h1_fixture"] = _base_h1_fixture()

    h0 = deepcopy(_base_h1_fixture())
    h0["rung3_headroom_by_family"][primary[0]] = [P.DELTA() - 0.02] * P.close_fraction_min() + [P.DELTA() + 0.2]
    fixtures["h0_fixture"] = h0

    leak = deepcopy(_base_h1_fixture())
    leak["integrity"]["planted_leak_uncaught"] = True
    fixtures["planted_leak_missed_fixture"] = leak

    replay = deepcopy(_base_h1_fixture())
    replay["integrity"]["replay_exact_by_rung"]["rung2"] = False
    fixtures["replay_false_fixture"] = replay

    r0 = deepcopy(_base_h1_fixture())
    r0["rung0_pass_by_family"] = {f: False for f in primary}
    fixtures["rung0_degraded_fixture"] = r0

    r1 = deepcopy(_base_h1_fixture())
    r1["rung1_pass_by_family"] = {f: False for f in primary}
    fixtures["rung1_degraded_all_primary_fixture"] = r1

    ctx = deepcopy(_base_h1_fixture())
    ctx["context_ablation_collapse_by_family"][primary[0]] = False
    fixtures["context_ablation_failure_fixture"] = ctx

    shuf = deepcopy(_base_h1_fixture())
    shuf["shuffle_collapse_by_family"][primary[0]] = False
    fixtures["shuffle_failure_fixture"] = shuf

    inconc = deepcopy(_base_h1_fixture())
    inconc["rung3_headroom_by_family"][primary[0]] = [P.DELTA() + 0.03, P.DELTA() - 0.02] * (P.N_SEEDS() // 2)
    inconc["rung3_headroom_by_family"][primary[1]] = [P.DELTA() + 0.03, P.DELTA() - 0.02] * (P.N_SEEDS() // 2)
    fixtures["ci_straddles_delta_fixture"] = inconc

    outcomes: dict[str, Any] = {}
    terminal_keys: set[str] = set()
    for name, fixture in fixtures.items():
        _enum, detail = compute_verdict(fixture)
        terminal_key = detail["terminal_key"]
        terminal_keys.add(terminal_key)
        outcomes[name] = {
            "neutral_outcome_class": f"BRANCH_{detail['branch_index']}",
            "terminal_key": terminal_key,
            "branch_index": detail["branch_index"],
        }
    expected = set(TERMINAL_KEY_BY_ENUM_KEY.values())
    return {
        "evidential": False,
        "official_verdict": "NOT_EMITTED",
        "uses_synthetic_fixtures_only": True,
        "fixtures": outcomes,
        "terminal_keys_covered": sorted(terminal_keys),
        "terminal_coverage_count": len(terminal_keys),
        "expected_terminal_count": len(expected),
        "all_seven_terminals_covered": terminal_keys == expected,
        "note": "Synthetic branch coverage only; not TLGP evidence and not an official verdict.",
    }

