"""Single-family frozen adjudicator for the rung3 powered learner deviation.

This module is intentionally separate from ``src.tlgp_001b_r2.verdict`` because
that banked adjudicator is scoped to two preregistered primary families.  The
Phase A rung3 powered learner substitutes one validated retrieval family and
therefore needs a narrower, explicit H0/H1 decision surface.
"""
from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from typing import Any

from src.tlgp_001b_r2 import preregistration as P

TERMINALS = {
    "invalid_integrity_or_governance",
    "invalid_rung0_reference_missing",
    "invalid_no_rung1_eligibility",
    "invalid_discriminativeness_or_ablation",
    "baseline_saturation",
    "h0_amortized",
    "h1_headroom_survives",
    "invalid_inconclusive_underpowered",
}


def lcb(values: list[float]) -> float:
    if not values:
        return float("-inf")
    mean = sum(float(v) for v in values) / len(values)
    variance = sum((float(v) - mean) ** 2 for v in values) / len(values)
    return float(mean - 2.0 * math.sqrt(variance) / math.sqrt(len(values)))


def _close_count(values: list[float], delta: float) -> int:
    return sum(1 for value in values if float(value) <= float(delta))


def compute_verdict(recorded: dict[str, Any]) -> dict[str, Any]:
    """Compute the scoped retrieval-family H0/H1 verdict from recorded fields.

    Required fields are deliberately simple and replayable:
    ``rung0_pass``, ``rung1_pass``, context-ablation booleans,
    ``rung3_headroom_vs_meta`` per seed, ``rung3_ideal_mean``, and
    ``rung3_fair_max``.  The H0/H1 statistic is the prereg statistic with the
    two-primary-family clause removed and explicitly scoped to retrieval only.
    """
    delta = float(P.DELTA())
    need = int(P.close_fraction_min())
    expected_n = int(P.N_SEEDS())
    headroom = [float(v) for v in recorded.get("rung3_headroom_vs_meta", [])]
    observed_n = len(headroom)
    close = _close_count(headroom, delta)
    lcb_value = lcb(headroom)
    integrity = dict(recorded.get("integrity", {}))
    replay_exact_by_rung = dict(integrity.get("replay_exact_by_rung", {}))
    integrity_invalid = bool(
        integrity.get("planted_leak_uncaught", False)
        or integrity.get("clean_false_flag", False)
        or integrity.get("protected_source_guard_failed", False)
        or integrity.get("family_substitution_not_declared", False)
        or any(not bool(v) for v in replay_exact_by_rung.values())
    )
    rung0_pass = bool(recorded.get("rung0_pass", False))
    rung1_pass = bool(recorded.get("rung1_pass", False))
    context_collapse = bool(recorded.get("context_ablation_collapse", False))
    shuffle_collapse = bool(recorded.get("shuffle_adapt_collapse", False))
    no_adapt_collapse = bool(recorded.get("no_adapt_collapse", False))
    ideal = recorded.get("rung3_ideal_mean")
    fair_max = recorded.get("rung3_fair_max")
    bar = None
    baseline_saturates = False
    if ideal is not None and fair_max is not None:
        bar = float(ideal) - delta
        baseline_saturates = bool(float(fair_max) >= bar)

    if integrity_invalid:
        terminal = "invalid_integrity_or_governance"
        reason = "integrity, replay, source, or declared-substitution guard failed"
    elif not rung0_pass:
        terminal = "invalid_rung0_reference_missing"
        reason = "rung0 retrieval reference pass was not present"
    elif not rung1_pass:
        terminal = "invalid_no_rung1_eligibility"
        reason = "retrieval family did not meet rung1 eligibility"
    elif not (context_collapse and shuffle_collapse and no_adapt_collapse):
        terminal = "invalid_discriminativeness_or_ablation"
        reason = "required context-ablation collapse did not hold"
    elif baseline_saturates:
        terminal = "baseline_saturation"
        reason = "fair or graph-cache panel reaches the rung3 bar; do not report H1"
    elif observed_n < expected_n:
        terminal = "invalid_inconclusive_underpowered"
        reason = f"observed {observed_n} seed(s), expected {expected_n}"
    elif close >= need:
        terminal = "h0_amortized"
        reason = "retrieval closes to ideal under the prereg close-count statistic"
    elif lcb_value > delta:
        terminal = "h1_headroom_survives"
        reason = "LCB(headroom_vs_meta) is above DELTA for the scoped retrieval family"
    else:
        terminal = "invalid_inconclusive_underpowered"
        reason = "CI/statistic straddles DELTA or neither H0 nor H1 is met"

    return {
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a."
            "rung3_single_family_adjudicator.compute_verdict"
        ),
        "verdict": terminal,
        "reason": reason,
        "detail": {
            "DELTA": delta,
            "close_fraction_min": need,
            "expected_model_seeds": expected_n,
            "observed_model_seeds": observed_n,
            "close_count_headroom_lte_delta": close,
            "lcb_headroom_vs_meta": lcb_value,
            "rung3_ideal_mean": ideal,
            "rung3_fair_max": fair_max,
            "rung3_bar_ideal_minus_delta": bar,
            "baseline_saturates": baseline_saturates,
            "rung0_pass": rung0_pass,
            "rung1_pass": rung1_pass,
            "context_ablation_collapse": context_collapse,
            "shuffle_adapt_collapse": shuffle_collapse,
            "no_adapt_collapse": no_adapt_collapse,
            "integrity_invalid": integrity_invalid,
            "family_scope": "single retrieval_model family",
            "claim_ceiling": (
                "Scoped retrieval-family decision only; no mechanism, agency, "
                "self, subjectivity, AGI, EGO, or runtime readiness claim."
            ),
        },
    }


def _base_fixture() -> dict[str, Any]:
    return {
        "integrity": {
            "planted_leak_uncaught": False,
            "clean_false_flag": False,
            "protected_source_guard_failed": False,
            "family_substitution_not_declared": False,
            "replay_exact_by_rung": {"rung1": True, "rung3": True},
        },
        "rung0_pass": True,
        "rung1_pass": True,
        "context_ablation_collapse": True,
        "shuffle_adapt_collapse": True,
        "no_adapt_collapse": True,
        "rung3_ideal_mean": 0.95,
        "rung3_fair_max": 0.22,
        "rung3_headroom_vs_meta": [P.DELTA() + 0.2] * P.N_SEEDS(),
    }


def synthetic_terminal_coverage() -> dict[str, Any]:
    fixtures: dict[str, dict[str, Any]] = {}
    fixtures["h1_fixture"] = _base_fixture()

    h0 = deepcopy(_base_fixture())
    h0["rung3_headroom_vs_meta"] = [P.DELTA() - 0.01] * P.close_fraction_min() + [P.DELTA() + 0.2]
    fixtures["h0_fixture"] = h0

    integrity = deepcopy(_base_fixture())
    integrity["integrity"]["planted_leak_uncaught"] = True
    fixtures["integrity_failure_fixture"] = integrity

    rung0 = deepcopy(_base_fixture())
    rung0["rung0_pass"] = False
    fixtures["rung0_missing_fixture"] = rung0

    rung1 = deepcopy(_base_fixture())
    rung1["rung1_pass"] = False
    fixtures["rung1_eligibility_failure_fixture"] = rung1

    ablation = deepcopy(_base_fixture())
    ablation["shuffle_adapt_collapse"] = False
    fixtures["ablation_failure_fixture"] = ablation

    baseline = deepcopy(_base_fixture())
    baseline["rung3_fair_max"] = baseline["rung3_ideal_mean"] - P.DELTA()
    fixtures["baseline_saturation_fixture"] = baseline

    underpowered = deepcopy(_base_fixture())
    underpowered["rung3_headroom_vs_meta"] = [P.DELTA() + 0.05]
    fixtures["underpowered_fixture"] = underpowered

    outcomes: dict[str, Any] = {}
    covered: set[str] = set()
    for name, fixture in fixtures.items():
        result = compute_verdict(fixture)
        terminal = str(result["verdict"])
        covered.add(terminal)
        outcomes[name] = {
            "terminal": terminal,
            "reason": result["reason"],
        }
    return {
        "evidential": False,
        "official_verdict": "NOT_EMITTED",
        "producer_function": (
            "src.tlgp_capability_witness_preflight_001a."
            "rung3_single_family_adjudicator.synthetic_terminal_coverage"
        ),
        "uses_synthetic_fixtures_only": True,
        "fixtures": outcomes,
        "terminal_keys_covered": sorted(covered),
        "expected_terminal_keys": sorted(TERMINALS),
        "terminal_coverage_count": len(covered),
        "expected_terminal_count": len(TERMINALS),
        "all_terminals_covered": covered == TERMINALS,
        "claim_ceiling": "adjudicator branch-coverage self-test only; not TLGP evidence",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if not args.self_test:
        parser.error("use --self-test")
    report = synthetic_terminal_coverage()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_terminals_covered"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
