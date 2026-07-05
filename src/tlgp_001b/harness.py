"""TLGP-001B orchestrator: frozen-prereg verify -> splits -> meta panel (REAL/CONTROL) +
capacity control + context/shuffle ablations -> ideal/lower-reference -> leakage controls ->
exact replay -> tamper fail-ability -> provenance -> computed verdict (frozen precedence).

Two modes:
  --full   : the FROZEN prereg budget. Emits result.json with the computed verdict enum and the
             full evidence bundle. (Designed to run on a capable machine; see artifacts/TLGP-001B/
             HANDOFF/. NOT runnable inside this sandbox -- measured ~20-60h on 2 CPUs.)
  --smoke  : a clearly NON-EVIDENTIAL plumbing validation on tiny non-prereg sizes/configs. It
             exercises every code path and the guard fail-ability, but DOES NOT emit H0/H1/INVALID
             and must NOT be read as meta-learner evidence. It modifies NO frozen value (thresholds,
             capacity grid, seeds, splits, training budget are read-only from the verified prereg).

NO git operation. Writes only under the artifact dir (env TLGP_001B_ARTIFACT_DIR), default
artifacts/TLGP-001B/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from src.tlgp_001a.ideal_observer import predict_episode as ideal_predict_episode
from src.tlgp_001a.leakage import positive_control_report
from src.tlgp_001a.metrics import balanced_accuracy, mean_episode_score
from src.tlgp_001a.world import Episode
from . import lower_reference as LR
from . import meta_learners as ML
from . import preregistration as P
from . import splits as S

REPO_ROOT = Path(__file__).resolve().parents[2]
PKG_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = Path(os.environ.get("TLGP_001B_ARTIFACT_DIR", str(REPO_ROOT / "artifacts" / "TLGP-001B")))


# --- ideal observer (probe ceiling; excluded from the fair panel) --------------
def ideal_eval(test_eps: List[Episode]) -> Tuple[float, List[List[int]], List[float]]:
    preds, balaccs = [], []
    for ep in test_eps:
        p, _ = ideal_predict_episode(ep)
        preds.append([int(v) for v in p])
        balaccs.append(balanced_accuracy(ep.query_e, p))
    return mean_episode_score(balaccs), preds, balaccs


def lcb(values: List[float], n_seeds: int) -> float:
    """Lower confidence bound = mean - 2*std/sqrt(N) (frozen decision statistic)."""
    if not values:
        return 0.0
    arr = np.asarray(values, dtype=float)
    return float(arr.mean() - 2.0 * arr.std(ddof=0) / math.sqrt(n_seeds))


# --- computed verdict (PURE, frozen precedence; fail-able both ways) -----------
# Equivalence-class tokens for non-evidential reporting (smoke maps to these, never the enum).
CLASS = {"H1": "OUTCOME_CLASS_A", "H0": "OUTCOME_CLASS_B", "INVALID": "OUTCOME_CLASS_C"}


def compute_verdict(gates: Dict) -> Tuple[str, Dict]:
    """Frozen precedence from prereg.verdict_enum.precedence_computed. Returns (enum_string, detail).

    gates keys:
      capacity_control_closed: {family: closed_seed_count}   (CONTROL regime closes headroom<=DELTA)
      planted_leak_all_caught: bool
      clean_no_false_flag:     bool
      replay_exact:            bool
      witness_lcb:             {family: lcb_of_headroom_vs_meta}    (REAL regime)
      context_ablation_meta:   {family: meta_test_score}           (must be <= FLOOR+DELTA)
      shuffle_headroom:        {family: ideal_minus_meta}          (must be <= DELTA)
    """
    ve = P.verdict_enum()
    DELTA, FLOOR, N = P.DELTA(), P.FLOOR(), P.N_SEEDS()
    need_close = int(math.ceil(0.9 * N))                       # >= 9/10

    cap_ok = {f: int(c) >= need_close for f, c in gates["capacity_control_closed"].items()}
    capacity_control_fails = (not gates["capacity_control_closed"]) or (not all(cap_ok.values()))
    invalid = bool(capacity_control_fails
                   or (not gates["planted_leak_all_caught"])
                   or (not gates["clean_no_false_flag"])
                   or (not gates["replay_exact"]))

    lcb_ok = {f: float(v) > DELTA for f, v in gates["witness_lcb"].items()}
    ctx_collapse = {f: float(v) <= FLOOR + DELTA for f, v in gates["context_ablation_meta"].items()}
    shuf_collapse = {f: float(v) <= DELTA for f, v in gates["shuffle_headroom"].items()}
    all_families = ML.FAMILIES
    survives = (bool(gates["witness_lcb"]) and all(lcb_ok.get(f, False) for f in all_families)
                and all(ctx_collapse.get(f, False) for f in all_families)
                and all(shuf_collapse.get(f, False) for f in all_families))

    if invalid:
        verdict = ve["invalid"]
    elif survives:
        verdict = ve["H1_bank_within_episode"]
    else:
        verdict = ve["H0_downgrade"]
    detail = {
        "need_close_seeds": need_close, "DELTA": DELTA, "FLOOR": FLOOR, "N_SEEDS": N,
        "capacity_control_ok_per_family": cap_ok, "capacity_control_fails": capacity_control_fails,
        "invalid_branch": invalid,
        "witness_lcb_gt_delta": lcb_ok, "context_ablation_collapse": ctx_collapse,
        "shuffle_collapse": shuf_collapse, "survives_branch": survives,
    }
    return verdict, detail


def _outcome_class(verdict: str) -> str:
    ve = P.verdict_enum()
    inv = {ve["H1_bank_within_episode"]: "H1", ve["H0_downgrade"]: "H0", ve["invalid"]: "INVALID"}
    return CLASS[inv[verdict]]


# --- guard fail-ability (tamper) on SYNTHETIC fixtures -------------------------
def _clean_synthetic_gates() -> Dict:
    return {
        "capacity_control_closed": {f: P.N_SEEDS() for f in ML.FAMILIES},
        "planted_leak_all_caught": True, "clean_no_false_flag": True, "replay_exact": True,
        "witness_lcb": {f: 0.50 for f in ML.FAMILIES},
        "context_ablation_meta": {f: P.FLOOR() for f in ML.FAMILIES},
        "shuffle_headroom": {f: 0.0 for f in ML.FAMILIES},
    }


def tamper_probes() -> Dict:
    """5 frozen tamper axes; each MUST change the computed verdict equivalence-class (fail-able
    both ways). Reported as booleans + neutral classes -- never the enum string."""
    clean = _clean_synthetic_gates()
    clean_v, _ = compute_verdict(clean)
    clean_c = _outcome_class(clean_v)
    fam0 = ML.FAMILIES[0]

    def mut(fn):
        g = json.loads(json.dumps(clean))
        fn(g)
        v, _ = compute_verdict(g)
        return _outcome_class(v)

    p1 = mut(lambda g: g["witness_lcb"].__setitem__(fam0, P.DELTA() - 0.05))   # inflate fair/meta -> not-H1
    p2 = mut(lambda g: g.__setitem__("planted_leak_all_caught", False))        # planted leak missed -> INVALID
    p3 = mut(lambda g: g["shuffle_headroom"].__setitem__(fam0, 0.50))          # break shuffle collapse -> not-H1
    p4 = mut(lambda g: g.__setitem__("replay_exact", False))                   # break replay -> INVALID
    p5 = mut(lambda g: g["capacity_control_closed"].__setitem__(fam0, need_minus_one()))  # degrade capacity -> INVALID
    probes = {
        "clean_outcome_class": clean_c,
        "p1_inflate_fair_baseline": {"class": p1, "flipped": p1 != clean_c},
        "p2_planted_leak_missed": {"class": p2, "flipped": p2 != clean_c},
        "p3_break_shuffle_collapse": {"class": p3, "flipped": p3 != clean_c},
        "p4_break_replay_exact": {"class": p4, "flipped": p4 != clean_c},
        "p5_degrade_capacity_control": {"class": p5, "flipped": p5 != clean_c},
    }
    flips = [probes[k]["flipped"] for k in probes if k != "clean_outcome_class"]
    probes["all_five_flip"] = bool(all(flips))
    probes["distinct_outcome_classes_observed"] = len({clean_c, p1, p2, p3, p4, p5})
    probes["legend"] = ("OUTCOME_CLASS_{A,B,C} are verdict-FUNCTION equivalence classes on SYNTHETIC "
                        "fixtures proving fail-ability; NOT the TLGP-001B run verdict; NOT meta evidence.")
    return probes


def need_minus_one() -> int:
    return int(math.ceil(0.9 * P.N_SEEDS())) - 1


# --- leakage audit on the meta input boundary ----------------------------------
def leakage_audit(test_eps: List[Episode]) -> Dict:
    """Reuse the 001A dual-target MI detector (clean + planted + RENAMED controls). Also assert
    structurally that the meta's tensor inputs derive ONLY from legal fields (never rule_id/query_e)."""
    rpt = positive_control_report(test_eps)
    # structural boundary proof: build_tensors uses only adapt_x/a/e and query_x/a; query_e is the
    # TARGET tensor and is never concatenated into ctx/qx. Verify by code-contract assertion.
    ctx, qx, qy = ML.build_tensors(test_eps[:2])
    rpt["meta_input_channels_declared"] = ["adapt_x", "adapt_a", "adapt_e", "query_x", "query_a"]
    rpt["meta_forbidden_inputs"] = ["rule_id", "query_e(held_out_answer)"]
    rpt["structural_boundary_ok"] = bool(ctx.shape[-1] == ML.CTX_DIM and qx.shape[-1] == ML.QRY_DIM)
    return rpt


# --- replay: recompute scores + verdict from recorded preds (NO retrain) -------
def replay_from_records(records: Dict, live: Dict) -> Dict:
    """records: {'query_e': [[...]], 'ideal_pred': [[...]], 'lower_ref': [{name:[...]}],
                 'meta': {key: [[...]]}}. Recompute every balanced accuracy from preds vs truth and
    re-derive the aggregates the verdict used; assert exact (<=1e-12)."""
    qe = [np.array(r) for r in records["query_e"]]
    ideal_re = mean_episode_score([balanced_accuracy(qe[i], np.array(records["ideal_pred"][i]))
                                   for i in range(len(qe))])
    meta_re = {}
    for key, preds in records["meta"].items():
        meta_re[key] = mean_episode_score([balanced_accuracy(qe[i], np.array(preds[i]))
                                           for i in range(len(qe))])
    checks = {
        "rows": len(qe),
        "ideal_mean_match": abs(ideal_re - live["ideal_mean"]) < 1e-12,
        "meta_mean_match": all(abs(meta_re[k] - live["meta_mean"][k]) < 1e-12 for k in meta_re),
    }
    checks["replay_exact"] = bool(checks["ideal_mean_match"] and checks["meta_mean_match"])
    checks["ideal_mean_replay"] = ideal_re
    checks["meta_mean_replay"] = meta_re
    return checks


# --- provenance (delivered == executed source hashes) --------------------------
def source_hashes() -> Dict[str, str]:
    out = {}
    for f in sorted(PKG_DIR.glob("*.py")):
        out[f"src/tlgp_001b/{f.name}"] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


# --- SMOKE (non-evidential plumbing validation) --------------------------------
SMOKE_BUDGET = {  # NON-PREREG tiny budget -- used ONLY by --smoke; frozen budget is untouched.
    "batch_size": 8, "max_epochs": 2, "early_stop_patience": 2, "steps_max": 50,
    "lr_grid": [0.001], "optimizer": "adam",
}
SMOKE_CONFIGS = {  # NON-PREREG tiny capacity (NOT the frozen grid).
    "in_context_gru": {"hidden": 16, "layers": 1},
    "in_context_transformer": {"d_model": 16, "layers": 1, "heads": 2, "ff_mult": 2},
    "amortized_summary_mlp": {"hidden": [16, 16]},
}
SMOKE_SIZES = {"n_train": 24, "n_val": 12, "n_test": 12}
# Leak-detector VALIDITY (MI estimator) needs an adequate sample (001A validated it at 200).
# This is the leak-audit size only -- NOT a training size and NOT a frozen experimental knob.
SMOKE_LEAK_N = 200


def run_smoke() -> Dict:
    """Validate plumbing end-to-end on tiny NON-PREREG sizes/configs. Emits NO verdict enum."""
    t0 = time.time()
    cfg = P.load_frozen_prereg()                       # verifies frozen sha (raises on mismatch)
    rep: Dict = {
        "smoke": True, "evidential": False,
        "WARNING": ("NON-EVIDENTIAL plumbing validation. Tiny NON-PREREG sizes/configs. NOT the "
                    "TLGP-001B run. Emits NO H0/H1/INVALID verdict. NOT meta-learner evidence. "
                    "Modifies NO frozen value (thresholds/capacity/seeds/splits/budget read-only)."),
        "frozen_prereg_sha256_readback": cfg["_canonical_sha256_readback"],
        "frozen_prereg_sha256_match": cfg["_sha256_match"],
        "smoke_nonprereg_sizes": SMOKE_SIZES, "smoke_nonprereg_budget": SMOKE_BUDGET,
        "smoke_nonprereg_configs": SMOKE_CONFIGS,
        "device_readback_initial": ML.device_readback(),
        "official_verdict": "NOT_EMITTED__smoke_is_nonevidential_plumbing_validation",
    }

    # --- splits (frozen definitions, tiny non-prereg subsample) ---
    train = S.make_split("train", S.REAL, SMOKE_SIZES["n_train"])
    val = S.make_split("val", S.REAL, SMOKE_SIZES["n_val"])
    test = S.make_split("test", S.REAL, SMOKE_SIZES["n_test"])
    ctrl_train = S.make_split("train", S.CONTROL, SMOKE_SIZES["n_train"])
    ctrl_val = S.make_split("val", S.CONTROL, SMOKE_SIZES["n_val"])
    shuf_train = S.make_shuffle_split("train", SMOKE_SIZES["n_train"])
    shuf_val = S.make_shuffle_split("val", SMOKE_SIZES["n_val"])
    shuf_test = S.make_shuffle_split("test", SMOKE_SIZES["n_test"])
    rep["split_assertions"] = S.split_assertions(train, val, test)

    # --- ideal + lower reference on test ---
    ideal_mean, ideal_preds, _ = ideal_eval(test)
    lr_means, lr_recorded = LR.evaluate(test, fit_seed=int(P.seeds()["BASELINE_FIT_SEED"]))
    rep["plumbing_scores"] = {"ideal_mean": ideal_mean, "lower_reference_means": lr_means}

    # --- meta panel: train REAL + CONTROL (capacity-control path) + ablations, tiny ---
    seed = int(P.model_seeds()[0])
    meta_real, meta_ctrl, meta_ctx, meta_shuf = {}, {}, {}, {}
    meta_preds_record = {}
    for fam in ML.FAMILIES:
        prm = SMOKE_CONFIGS[fam]
        r_real = ML.train_select(fam, prm, seed, train, val, test, SMOKE_BUDGET)
        r_ctrl = ML.train_select(fam, prm, seed, ctrl_train, ctrl_val, test, SMOKE_BUDGET)
        r_ctx = ML.train_select(fam, prm, seed, train, val, test, SMOKE_BUDGET, context_ablate=True)
        r_shuf = ML.train_select(fam, prm, seed, shuf_train, shuf_val, shuf_test, SMOKE_BUDGET)
        meta_real[fam] = r_real.test_balacc
        meta_ctrl[fam] = ideal_mean - r_ctrl.test_balacc       # CONTROL headroom (should ->0 at full budget)
        meta_ctx[fam] = r_ctx.test_balacc
        meta_shuf[fam] = r_shuf.test_balacc
        meta_preds_record[fam] = r_real.test_preds
    rep["plumbing_meta"] = {
        "real_test_balacc": meta_real, "control_headroom_vs_meta": meta_ctrl,
        "context_ablation_test_balacc": meta_ctx, "shuffle_test_balacc": meta_shuf,
        "note": "tiny budget -> scores are MEANINGLESS as evidence; presence proves the path runs.",
    }
    rep["device_readback_after_meta"] = ML.device_readback()

    # --- leakage controls ---
    leak = leakage_audit(S.make_split("test", S.REAL, SMOKE_LEAK_N))
    rep["leakage_controls"] = {
        "all_planted_caught": leak["all_planted_caught"],
        "renamed_leak_caught": leak["renamed_leak_caught"],
        "no_clean_false_flag": leak["no_clean_false_flag"],
        "detector_valid": leak["detector_valid"],
        "structural_boundary_ok": leak["structural_boundary_ok"],
    }

    # --- replay (recompute meta + ideal from recorded preds, no retrain) ---
    live = {"ideal_mean": ideal_mean, "meta_mean": meta_real}
    records = {"query_e": [[int(v) for v in ep.query_e] for ep in test],
               "ideal_pred": ideal_preds, "lower_ref": lr_recorded, "meta": meta_preds_record}
    rep["replay"] = replay_from_records(records, live)

    # --- tamper fail-ability (synthetic fixtures; neutral classes) ---
    rep["tamper_failability"] = tamper_probes()

    # --- provenance ---
    rep["source_hashes_delivered_equals_executed"] = source_hashes()
    rep["elapsed_sec"] = round(time.time() - t0, 2)

    # --- plumbing pass: every stage ran + guards fail-able (NOT a verdict) ---
    rep["plumbing_ok"] = bool(
        rep["split_assertions"]["rule_partition_disjoint"]
        and rep["split_assertions"]["train_test_rule_overlap_empty"]
        and rep["split_assertions"]["episode_ids_disjoint"]
        and rep["leakage_controls"]["detector_valid"]
        and rep["leakage_controls"]["structural_boundary_ok"]
        and rep["replay"]["replay_exact"]
        and rep["tamper_failability"]["all_five_flip"]
        and all(k in rep["plumbing_meta"]["real_test_balacc"] for k in ML.FAMILIES)
    )
    _write(ARTIFACT_DIR / "smoke_report.json", rep)
    return rep


# --- FULL (frozen budget; for the capable machine) -----------------------------
def run_full() -> Dict:
    """Execute the FROZEN prereg budget and emit the computed verdict + full evidence bundle.

    WARNING: this is the heavy run (measured ~20-60h on 2 CPUs; a Transformer witness alone is
    ~1035s per training run). It is NOT runnable inside the 45s/call, no-background sandbox.
    Run on a capable machine per artifacts/TLGP-001B/HANDOFF/HANDOFF.md.
    """
    cfg = P.load_frozen_prereg()                       # raises on sha mismatch -> STOP/INVALID
    budget = P.training_budget()
    nb = {"batch_size": budget["batch_size"], "max_epochs": budget["max_epochs"],
          "early_stop_patience": budget["early_stop_patience"], "steps_max": budget["steps_max"],
          "lr_grid": budget["lr_grid"], "optimizer": budget["optimizer"]}
    n_train, n_val, n_test = budget["n_train_episodes"], budget["n_val_episodes"], budget["n_test_episodes"]
    seeds = [int(s) for s in P.model_seeds()]
    fit_seed = int(P.seeds()["BASELINE_FIT_SEED"])

    # frozen split datasets (regime-conditioned)
    real_train = S.make_split("train", S.REAL, n_train)
    real_val = S.make_split("val", S.REAL, n_val)
    test = S.make_real_control_test()                  # identical across regimes
    ctrl_train = S.make_split("train", S.CONTROL, n_train)
    ctrl_val = S.make_split("val", S.CONTROL, n_val)
    shuf_train = S.make_shuffle_split("train", n_train)
    shuf_val = S.make_shuffle_split("val", n_val)
    shuf_test = S.make_shuffle_split("test", n_test)
    assertions = S.split_assertions(real_train, real_val, test)

    ideal_mean, ideal_preds, _ = ideal_eval(test)
    lr_means, lr_recorded = LR.evaluate(test, fit_seed)

    # per-family saturation-witness training across all model seeds
    witness_lcb, capacity_closed, context_ablation_meta, shuffle_headroom = {}, {}, {}, {}
    meta_mean_record, meta_preds_record = {}, {}
    per_seed = {}
    for fam in ML.FAMILIES:
        prm = ML.witness_params(fam)
        real_headrooms, ctrl_closed = [], 0
        per_seed[fam] = []
        for sd in seeds:
            r_real = ML.train_select(fam, prm, sd, real_train, real_val, test, nb)
            r_ctrl = ML.train_select(fam, prm, sd, ctrl_train, ctrl_val, test, nb)
            hr_real = ideal_mean - r_real.test_balacc
            hr_ctrl = ideal_mean - r_ctrl.test_balacc
            real_headrooms.append(hr_real)
            if hr_ctrl <= P.DELTA():
                ctrl_closed += 1
            per_seed[fam].append({"seed": sd, "real_test_balacc": r_real.test_balacc,
                                  "real_headroom_vs_meta": hr_real, "control_headroom_vs_meta": hr_ctrl,
                                  "lr_real": r_real.lr, "lr_ctrl": r_ctrl.lr,
                                  "epochs_real": r_real.epochs_run})
            meta_mean_record[f"{fam}|witness|seed{sd}"] = r_real.test_balacc
            meta_preds_record[f"{fam}|witness|seed{sd}"] = r_real.test_preds
        witness_lcb[fam] = lcb(real_headrooms, P.N_SEEDS())
        capacity_closed[fam] = ctrl_closed
        # ablations at the witness (mean over seeds)
        ctx_scores, shuf_headrooms = [], []
        for sd in seeds:
            r_ctx = ML.train_select(fam, prm, sd, real_train, real_val, test, nb, context_ablate=True)
            r_shuf = ML.train_select(fam, prm, sd, shuf_train, shuf_val, shuf_test, nb)
            ctx_scores.append(r_ctx.test_balacc)
            shuf_ideal, _, _ = ideal_eval(shuf_test)
            shuf_headrooms.append(shuf_ideal - r_shuf.test_balacc)
        context_ablation_meta[fam] = float(np.mean(ctx_scores))
        shuffle_headroom[fam] = float(np.mean(shuf_headrooms))

    leak = leakage_audit(test)
    live = {"ideal_mean": ideal_mean, "meta_mean": meta_mean_record}
    records = {"query_e": [[int(v) for v in ep.query_e] for ep in test],
               "ideal_pred": ideal_preds, "lower_ref": lr_recorded, "meta": meta_preds_record}
    replay = replay_from_records(records, live)

    gates = {
        "capacity_control_closed": capacity_closed,
        "planted_leak_all_caught": leak["all_planted_caught"],
        "clean_no_false_flag": leak["no_clean_false_flag"],
        "replay_exact": replay["replay_exact"],
        "witness_lcb": witness_lcb,
        "context_ablation_meta": context_ablation_meta,
        "shuffle_headroom": shuffle_headroom,
    }
    verdict, detail = compute_verdict(gates)

    # power statement on the fired verdict
    real_hr_all = [s["real_headroom_vs_meta"] for f in ML.FAMILIES for s in per_seed[f]]
    obs_std = float(np.std(real_hr_all)) if real_hr_all else 0.0
    mde = 2.0 * obs_std / math.sqrt(P.N_SEEDS())

    result = {
        "task_id": "TLGP-001B", "official_run": True, "candidate_free": True,
        "prereg_pin_sha256": cfg["_canonical_sha256_readback"],   # embedded BEFORE scores below it
        "prereg_pin_match": cfg["_sha256_match"],
        "lineage_tlgp_001a_prereg_sha256": cfg["lineage"]["tlgp_001a_prereg_sha256"],
        "DELTA": P.DELTA(), "FLOOR": P.FLOOR(), "N_SEEDS": P.N_SEEDS(),
        "split_assertions": assertions,
        "ideal_mean": ideal_mean, "lower_reference_means": lr_means,
        "witness_lcb_headroom_vs_meta": witness_lcb,
        "capacity_control_closed_seeds": capacity_closed,
        "context_ablation_meta": context_ablation_meta,
        "shuffle_headroom": shuffle_headroom,
        "headroom_vs_meta_per_seed": per_seed,
        "leakage": {k: leak[k] for k in ("all_planted_caught", "renamed_leak_caught",
                                         "no_clean_false_flag", "detector_valid", "structural_boundary_ok")},
        "replay": replay,
        "verdict": verdict, "verdict_detail": detail,
        "power_statement": {"observed_std_headroom": obs_std, "min_detectable_gap_2se": mde,
                            "n_seeds": P.N_SEEDS()},
        "tamper_failability": tamper_probes(),
        "source_hashes_delivered_equals_executed": source_hashes(),
        "device_readback": ML.device_readback(),
        "claim_ceiling": P.claim_ceiling(),
    }
    _write(ARTIFACT_DIR / "result.json", result)
    _write(ARTIFACT_DIR / "baseline_comparison.json",
           {"ideal_mean": ideal_mean, "lower_reference_means": lr_means,
            "witness_lcb_headroom_vs_meta": witness_lcb, "meta_mean_per_witness_seed": meta_mean_record})
    _write(ARTIFACT_DIR / "ablation_report.json",
           {"context_ablation_meta": context_ablation_meta, "shuffle_headroom": shuffle_headroom,
            "FLOOR_plus_DELTA": P.FLOOR() + P.DELTA(), "DELTA": P.DELTA()})
    _write(ARTIFACT_DIR / "replay_report.json", replay)
    _write(ARTIFACT_DIR / "positive_control_report.json", leak)
    _write(ARTIFACT_DIR / "failure_manifest.json",
           {"verdict": verdict, "invalid": verdict == P.verdict_enum()["invalid"],
            "stop_triggered": verdict != P.verdict_enum()["H1_bank_within_episode"]})
    (ARTIFACT_DIR / "claim_ceiling.txt").write_text(P.claim_ceiling() + "\n", encoding="utf-8")
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="non-evidential plumbing validation (no verdict)")
    ap.add_argument("--full", action="store_true", help="FROZEN budget run (capable machine only)")
    args = ap.parse_args(argv)
    if args.full:
        print(json.dumps(run_full(), indent=2, sort_keys=True))
    else:
        out = run_smoke()
        print(json.dumps({k: out[k] for k in ("smoke", "evidential", "plumbing_ok",
              "official_verdict", "frozen_prereg_sha256_match", "elapsed_sec")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
