"""Pure route-decision adjudicator for TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A.

Consumes a RECORDED results dict (numbers produced by the preflight sweep — this
module trains nothing, runs no environment, imports no candidate, and uses no
future observation) and emits exactly ONE route terminal per frozen, prereg-bound
rules.

DELTA / close_fraction_min / N_SEEDS / FLOOR are READ from the frozen TLGP-001B-R2
prereg (canonical sha 6e61a831...). They are never redefined or recomputed here.
The function is deterministic and replayable from the recorded dict alone.

Terminals (see TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A.md, C3-tightened):
  route_open_capability_witness_feasible
  route_closed_identifiability_ceiling
  route_inconclusive_optimization_or_family_limited
  inconclusive_underpowered
  route_needs_world_rung_redesign
  invalid_leakage
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

PREREG_PATH = Path(__file__).resolve().parents[2] / "artifacts" / "TLGP-001B-R2" / "prereg.json"
FROZEN_PREREG_SHA256 = "6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7"

PASS_FUNCTION_REF = (
    "prereg rung pass_rule via src/tlgp_001b_r2/verdict.py: "
    "balacc >= (ideal - DELTA) on >= close_fraction_min/N_SEEDS seeds, per primary family"
)


def _canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def load_prereg(verify: bool = True) -> tuple[dict, str]:
    obj = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    sha = _canonical_sha256(obj)
    if verify and sha != FROZEN_PREREG_SHA256:
        raise RuntimeError(
            f"prereg canonical sha mismatch: computed={sha} expected={FROZEN_PREREG_SHA256}"
        )
    return obj, sha


def _seed_pass_count(per_seed: list[float], bar: float) -> int:
    return sum(1 for v in per_seed if float(v) >= bar)


def compute_route_decision(recorded: dict, prereg: dict | None = None, prereg_sha: str | None = None) -> dict:
    """Adjudicate one witness rung.

    recorded schema:
      {
        "rung": "rung0" | "rung1",
        "ideal_balacc": float,
        "fair_baseline_balacc": {name: float, ...},   # MUST include graph_cache + lookup + count_table + predict_all + majority
        "learner_per_seed_balacc": {family: [float per seed]},  # primary families only
        "n_seeds": int,
        "leakage_clean": bool,
        "headroom_power": {family: {"mde": float, "power": float, "passes_power": bool}},   # optional
        "ci_straddles_bar": bool,                       # optional
        "admissible_upper_bound_no_learner_advantage": bool   # optional
      }
    """
    if prereg is None or prereg_sha is None:
        prereg, prereg_sha = load_prereg()
    DELTA = float(prereg["DELTA"])
    FLOOR = float(prereg["FLOOR"])
    need = int(prereg["close_fraction_min"])
    N = int(prereg["N_SEEDS"])

    ideal = float(recorded["ideal_balacc"])
    bar = ideal - DELTA
    fair = {k: float(v) for k, v in recorded.get("fair_baseline_balacc", {}).items()}
    learners = {k: [float(x) for x in v] for k, v in recorded.get("learner_per_seed_balacc", {}).items()}
    n_seeds = int(recorded.get("n_seeds", N))
    leakage_clean = bool(recorded.get("leakage_clean", False))
    power = recorded.get("headroom_power", {})
    ci_straddles = bool(recorded.get("ci_straddles_bar", False))
    ub_no_adv = bool(recorded.get("admissible_upper_bound_no_learner_advantage", False))

    fair_max = max(fair.values()) if fair else None
    per_family_pass = {f: _seed_pass_count(s, bar) for f, s in learners.items()}
    all_primary_pass = bool(learners) and all(c >= need for c in per_family_pass.values())

    def _powered(family: str) -> bool:
        p = power.get(family)
        return bool(p and p.get("passes_power"))

    all_primary_powered = bool(learners) and all(_powered(f) for f in learners)

    detail = {
        "rung": recorded.get("rung"),
        "ideal_balacc": ideal,
        "bar": bar,
        "DELTA": DELTA,
        "FLOOR": FLOOR,
        "need_seeds": need,
        "N_SEEDS": N,
        "n_seeds_observed": n_seeds,
        "fair_baseline_balacc": fair,
        "fair_max": fair_max,
        "per_family_seed_pass_count": per_family_pass,
        "all_primary_pass_seed_rule": all_primary_pass,
        "all_primary_powered_headroom": all_primary_powered,
        "leakage_clean": leakage_clean,
        "ci_straddles_bar": ci_straddles,
        "admissible_upper_bound_no_learner_advantage": ub_no_adv,
        "prereg_sha256": prereg_sha,
        "bar_source": "artifacts/TLGP-001B-R2/prereg.json",
        "pass_function_ref": PASS_FUNCTION_REF,
    }

    # --- precedence (each branch is reachable; see self-test) ---
    if not leakage_clean:
        route, reason = "invalid_leakage", "leakage detector not clean on a meta input channel"
    elif ideal < FLOOR + DELTA:
        route, reason = ("route_needs_world_rung_redesign",
                         f"ideal_balacc {ideal:.3f} < FLOOR+DELTA {FLOOR + DELTA:.3f}; rung degenerate / bar not meaningful")
    elif (fair_max is not None and fair_max >= bar) or ub_no_adv:
        route, reason = ("route_closed_identifiability_ceiling",
                         "a fair/graph-cache baseline reaches the attainable bar (or an admissible upper bound shows no learner advantage)")
    elif n_seeds < N or ci_straddles:
        route, reason = ("inconclusive_underpowered",
                         f"n_seeds {n_seeds} < N_SEEDS {N}" if n_seeds < N else "CI straddles the bar at N_SEEDS")
    elif all_primary_pass and all_primary_powered:
        route, reason = ("route_open_capability_witness_feasible",
                         "every primary family passes the prereg seed rule with power-backed headroom over fair+graph-cache baselines")
    else:
        route, reason = ("route_inconclusive_optimization_or_family_limited",
                         "ideal passes and fair baseline does not saturate, but no primary family passes under the declared budget (not a ceiling, not merely CI-straddling)")

    return {"route": route, "reason": reason, "detail": detail}


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: route_decision.py <recorded_results.json> [out_route_decision.json]", file=sys.stderr)
        return 2
    recorded = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    out = compute_route_decision(recorded)
    out["producer_function"] = "src.tlgp_capability_witness_preflight_001a.route_decision.compute_route_decision"
    text = json.dumps(out, indent=2, sort_keys=True)
    if len(argv) >= 3:
        Path(argv[2]).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
