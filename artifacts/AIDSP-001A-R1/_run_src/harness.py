"""AIDSP-001A-R1 orchestration. (Canonical == src/aidsp_001a_r1/harness.py)

Order (the triviality probe GATES everything):
  0. freeze preregistration + static secret scan
  1. leakage positive controls (scanner must be fail-able)
  2. triviality probe -> derive band; PF1/PF2/PF3; fail => invalid_metric_degenerate STOP
  3. fair baselines + candidate + ablations + challenger controls
  4. COMPUTE verdict from artifacts
  5. replay the deciding verdict path from trace
  6. emit all evidence-contract artifacts

The verdict is COMPUTED here from numbers, never written as a header literal.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from dataclasses import asdict
from typing import Dict

import numpy as np

from . import prereg as P
from . import baselines as B
from . import provenance as PROV
from .candidate_efe import run_efe_episode
from .metrics import compute_M1, compute_M2_episode, tvd, dwell_fractions
from .leakage import run_positive_controls

PKG = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(PKG))
ARTIFACT_DIR = os.path.join(REPO, "artifacts", "AIDSP-001A-R1")

CUE_USING_FAIR = {"homeostatic_rl", "behavior_tree_softmax",
                  "observation_only_lookup", "count_based_rl"}


def _fair_baseline_runners(homeo_q, count_q):
    return {
        "homeostatic_rl": lambda s, ab=False: B.run_homeostatic(s, homeo_q, ab),
        "behavior_tree_softmax": lambda s, ab=False: B.run_behavior_tree(s, ab),
        "random_policy": lambda s, ab=False: B.run_trivial("random_walk", s, ab),
        "observation_only_lookup": lambda s, ab=False: B.run_obs_only(s, ab),
        "count_based_rl": lambda s, ab=False: B.run_count_based(s, count_q, ab),
        "exhaustive_sweep": lambda s, ab=False: B.run_trivial("exhaustive_sweep", s, ab),
        "systematic_coverage": lambda s, ab=False: B.run_trivial("systematic_coverage", s, ab),
    }


def _agg_M1(runs):
    return float(np.mean([compute_M1(r.observations) for r in runs]))


def _agg_M2(run_fn, seeds):
    vals = []
    for s in seeds:
        vals.append(compute_M2_episode(run_fn(s, False), run_fn(s, True)))
    return float(np.mean(vals))


def _agg_dwell(runs):
    dr = float(np.mean([dwell_fractions(r)[0] for r in runs]))
    tv = float(np.mean([dwell_fractions(r)[1] for r in runs]))
    return dr, tv


def _trace_rows(strategy, mode, runs, seeds):
    rows = []
    for s, run in zip(seeds, runs):
        for st in run.steps:
            rows.append({"strategy": strategy, "mode": mode, "seed": s,
                         "food_groundtruth": run.food, "t": st.t, "pos": st.pos,
                         "action": st.action, "action_dist": st.action_dist,
                         "cue": st.cue, "at_food": st.at_food,
                         "in_dark_room": st.in_dark_room, "in_noisy_tv": st.in_noisy_tv})
    return rows


def run_triviality_probe(seeds, collect_trace=False) -> Dict:
    trivial_M1, trivial_M2 = {}, {}
    trace_rows = []
    for name in B.TRIVIAL_BATTERY:
        present = [B.run_trivial(name, s) for s in seeds]
        ablated = [B.run_trivial(name, s, True) for s in seeds]
        trivial_M1[name] = _agg_M1(present)
        trivial_M2[name] = float(np.mean([compute_M2_episode(p, a)
                                          for p, a in zip(present, ablated)]))
        if collect_trace:
            trace_rows += _trace_rows(name, "present", present, seeds)
            trace_rows += _trace_rows(name, "ablated", ablated, seeds)
    trivial_M1["predict_all_uniform"] = 0.0
    trivial_M2["predict_all_uniform"] = 0.0

    max_trivial = max(trivial_M1.values())
    band = max(max_trivial * (1.0 + P.DELTA_REL), max_trivial + P.DELTA_ABS_FLOOR)

    oracle_present = [B.run_oracle(s) for s in seeds]
    oracle_ablated = [B.run_oracle(s, True) for s in seeds]
    oracle_M1 = _agg_M1(oracle_present)
    oracle_M2 = float(np.mean([compute_M2_episode(p, a)
                               for p, a in zip(oracle_present, oracle_ablated)]))
    if collect_trace:
        trace_rows += _trace_rows("oracle_probe", "present", oracle_present, seeds)
        trace_rows += _trace_rows("oracle_probe", "ablated", oracle_ablated, seeds)

    pf1_violations = {n: v for n, v in trivial_M2.items() if v > P.TAU_M2_FLOOR}
    pf1_fail = len(pf1_violations) > 0
    pf2_fail = oracle_M1 < band
    pf3_fail = oracle_M2 < P.TAU_M2_USE
    degenerate = bool(pf1_fail or pf2_fail or pf3_fail)
    return {
        "trivial_M1": trivial_M1, "trivial_M2": trivial_M2,
        "max_trivial_M1": max_trivial, "band": band,
        "band_rule": "max(max_trivial*(1+DELTA_REL), max_trivial+DELTA_ABS_FLOOR)",
        "delta_rel": P.DELTA_REL, "oracle_M1": oracle_M1, "oracle_M2": oracle_M2,
        "PF1_m2_validity_fail": pf1_fail, "PF1_violations": pf1_violations,
        "PF2_m1_headroom_fail": pf2_fail, "PF3_m2_detectability_fail": pf3_fail,
        "metric_degenerate": degenerate,
        "note": ("oracle is a PROBE INSTRUMENT (headroom ceiling), NOT a fair "
                 "baseline and NOT part of the candidate verdict comparison."),
        "_trace_rows": (trace_rows if collect_trace else None),
    }


def evaluate_family(seeds, homeo_q, count_q) -> Dict:
    fair = _fair_baseline_runners(homeo_q, count_q)
    out = {"baselines": {}, "candidate": {}, "ablations": {}}
    for name, fn in fair.items():
        runs = [fn(s, False) for s in seeds]
        m1 = _agg_M1(runs)
        m2 = (_agg_M2(fn, seeds) if name in CUE_USING_FAIR else 0.0)
        dr, tv = _agg_dwell(runs)
        out["baselines"][name] = {
            "M1": m1, "M2": m2, "dwell_dark": dr, "dwell_tv": tv,
            "architecture": ("model_free_learned" if name.endswith("_rl")
                             else "model_free_reactive")}

    cand_runs = [run_efe_episode(s, "full") for s in seeds]
    cdr, ctv = _agg_dwell(cand_runs)
    out["candidate"] = {
        "M1": _agg_M1(cand_runs),
        "M2": _agg_M2(lambda s, ab: run_efe_episode(s, "full", cue_ablated=ab), seeds),
        "dwell_dark": cdr, "dwell_tv": ctv,
        "architecture": "model_based_active_inference_pymdp_legacy"}

    epi = [run_efe_episode(s, "epistemic_ablation") for s in seeds]
    notr = [run_efe_episode(s, "no_transition") for s in seeds]
    out["ablations"] = {
        "epistemic_ablation": {
            "M1": _agg_M1(epi),
            "M2": _agg_M2(lambda s, ab: run_efe_episode(s, "epistemic_ablation", cue_ablated=ab), seeds)},
        "no_transition": {
            "M1": _agg_M1(notr),
            "M2": _agg_M2(lambda s, ab: run_efe_episode(s, "no_transition", cue_ablated=ab), seeds)},
    }
    return out


def compute_verdict(probe, famA, famB, pos_controls, secret) -> Dict:
    if not secret["run_path_clean"]:
        return {"verdict": "invalid_due_to_leakage_or_contract_failure",
                "reason": "secret present in run path"}
    if not pos_controls["summary"]["scanner_failable"]:
        return {"verdict": "invalid_due_to_leakage_or_contract_failure",
                "reason": "leakage scanner not fail-able / planted leak not caught"}
    if probe["metric_degenerate"]:
        return {"verdict": "invalid_metric_degenerate",
                "reason": {"PF1": probe["PF1_m2_validity_fail"],
                           "PF2": probe["PF2_m1_headroom_fail"],
                           "PF3": probe["PF3_m2_detectability_fail"]}}

    def admit_for(fam):
        cand = fam["candidate"]
        fair_M1 = [b["M1"] for b in fam["baselines"].values()]
        threshold = (1.0 + P.DELTA_REL) * max(max(fair_M1), probe["max_trivial_M1"])
        m1_beats_all = cand["M1"] >= threshold
        m2_pass = cand["M2"] >= P.TAU_M2_USE
        ref_dark = max(fam["baselines"]["random_policy"]["dwell_dark"],
                       fam["baselines"]["homeostatic_rl"]["dwell_dark"])
        ref_tv = max(fam["baselines"]["random_policy"]["dwell_tv"],
                     fam["baselines"]["homeostatic_rl"]["dwell_tv"])
        challenger_pass = (cand["dwell_dark"] <= ref_dark + P.CHALLENGER_DWELL_TOL and
                           cand["dwell_tv"] <= ref_tv + P.CHALLENGER_DWELL_TOL)
        ablation_removes = fam["ablations"]["epistemic_ablation"]["M1"] < threshold
        return {
            "threshold_M1": threshold, "candidate_M1": cand["M1"],
            "m1_beats_all_fair_by_band": m1_beats_all, "m2_pass": m2_pass,
            "challenger_pass": challenger_pass,
            "ref_dwell_dark": ref_dark, "ref_dwell_tv": ref_tv,
            "cand_dwell_dark": cand["dwell_dark"], "cand_dwell_tv": cand["dwell_tv"],
            "epistemic_ablation_removes_advantage": ablation_removes}

    aA, aB = admit_for(famA), admit_for(famB)
    challenger_fail = (not aA["challenger_pass"]) or (not aB["challenger_pass"])
    admit_both = all([aA["m1_beats_all_fair_by_band"], aB["m1_beats_all_fair_by_band"],
                      aA["m2_pass"], aB["m2_pass"],
                      aA["challenger_pass"], aB["challenger_pass"],
                      aA["epistemic_ablation_removes_advantage"],
                      aB["epistemic_ablation_removes_advantage"]])
    if admit_both:
        verdict = "admit_non_redundant"
    elif challenger_fail:
        verdict = "known_failure_mode_reproduced"
    else:
        verdict = "baseline_equivalence_or_no_separation"
    return {"verdict": verdict, "family_A_admit_check": aA, "family_B_admit_check": aB,
            "multi_seed_consistent": (aA["m1_beats_all_fair_by_band"] ==
                                      aB["m1_beats_all_fair_by_band"])}


def write_candidate_trace(seeds, path):
    with open(path, "w") as fh:
        for s in seeds:
            run = run_efe_episode(s, "full")
            for st in run.steps:
                row = {"agent": "candidate_efe", "seed": s,
                       "food_groundtruth": run.food, **asdict(st)}
                fh.write(json.dumps(row, default=float) + "\n")


def replay_candidate_from_trace(path, reported_M1) -> Dict:
    by_seed = defaultdict(list)
    with open(path) as fh:
        for line in fh:
            r = json.loads(line)
            by_seed[r["seed"]].append(r)
    m1s = []
    for seed, rows in by_seed.items():
        rows.sort(key=lambda x: x["t"])
        m1s.append(compute_M1([(x["cue"], x["pos"], x["at_food"]) for x in rows]))
    replay_M1 = float(np.mean(m1s))
    det_ok = True
    for seed in list(by_seed.keys())[:5]:
        rerun = run_efe_episode(seed, "full")
        ta = [x["action"] for x in sorted(by_seed[seed], key=lambda x: x["t"])]
        ra = [st.action for st in rerun.steps]
        if ta != ra:
            det_ok = False
    return {"replay_candidate_M1_famA": replay_M1, "reported_candidate_M1_famA": reported_M1,
            "M1_match": bool(abs(replay_M1 - reported_M1) < 1e-9),
            "action_determinism_ok": det_ok,
            "reconstructed_from": "trace.jsonl (cue,pos,at_food per step) via independent estimator"}


def replay_probe_from_trace(path, probe) -> Dict:
    groups = defaultdict(lambda: defaultdict(list))
    with open(path) as fh:
        for line in fh:
            r = json.loads(line)
            groups[r["strategy"]][(r["mode"], r["seed"])].append(r)

    def m1_of(strategy):
        vals = []
        for (mode, seed), rows in groups[strategy].items():
            if mode != "present":
                continue
            rows.sort(key=lambda x: x["t"])
            vals.append(compute_M1([(x["cue"], x["pos"], x["at_food"]) for x in rows]))
        return float(np.mean(vals)) if vals else 0.0

    def m2_of(strategy):
        seeds = set(s for (m, s) in groups[strategy] if m == "present")
        vals = []
        for seed in seeds:
            pres = sorted(groups[strategy][("present", seed)], key=lambda x: x["t"])
            abl = sorted(groups[strategy][("ablated", seed)], key=lambda x: x["t"])
            n = min(len(pres), len(abl))
            vals.append(float(np.mean([tvd(pres[t]["action_dist"], abl[t]["action_dist"])
                                       for t in range(n)])) if n else 0.0)
        return float(np.mean(vals)) if vals else 0.0

    strategies = [s for s in groups if s != "oracle_probe"]
    rep_trivial_M1 = {s: m1_of(s) for s in strategies}
    rep_trivial_M2 = {s: m2_of(s) for s in strategies}
    rep_trivial_M1["predict_all_uniform"] = 0.0
    max_trivial = max(rep_trivial_M1.values())
    band = max(max_trivial * (1.0 + P.DELTA_REL), max_trivial + P.DELTA_ABS_FLOOR)
    oracle_M1 = m1_of("oracle_probe")
    oracle_M2 = m2_of("oracle_probe")
    pf1 = any(v > P.TAU_M2_FLOOR for v in rep_trivial_M2.values())
    pf2 = oracle_M1 < band
    pf3 = oracle_M2 < P.TAU_M2_USE
    degen = bool(pf1 or pf2 or pf3)
    return {
        "reconstructed_from": "trace.jsonl (per-strategy present/ablated steps)",
        "replay_trivial_M2": rep_trivial_M2,
        "replay_max_trivial_M1": max_trivial, "reported_max_trivial_M1": probe["max_trivial_M1"],
        "replay_band": band, "reported_band": probe["band"],
        "replay_oracle_M1": oracle_M1, "reported_oracle_M1": probe["oracle_M1"],
        "replay_oracle_M2": oracle_M2, "reported_oracle_M2": probe["oracle_M2"],
        "replay_PF1": pf1, "replay_PF2": pf2, "replay_PF3": pf3,
        "replay_metric_degenerate": degen,
        "matches_reported": bool(
            abs(oracle_M1 - probe["oracle_M1"]) < 1e-9 and
            abs(band - probe["band"]) < 1e-9 and
            degen == probe["metric_degenerate"])}


def _dump(obj, name, artifact_dir=None):
    d = artifact_dir or ARTIFACT_DIR
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name), "w") as fh:
        json.dump(obj, fh, indent=2, default=float)


def main(seedsA=None, seedsB=None, artifact_dir=None):
    global ARTIFACT_DIR
    if artifact_dir:
        ARTIFACT_DIR = artifact_dir
    rid = PROV.run_id()
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    seedsA = seedsA or P.SEED_FAMILY_A
    seedsB = seedsB or P.SEED_FAMILY_B

    secret = PROV.secret_scan(extra_paths=[os.path.join(REPO, "scripts", "push.py"),
                                           os.path.join(REPO, "scripts", "push.sh")])
    pos_controls = run_positive_controls()
    _dump(pos_controls, "positive_control_report.json")

    probe = run_triviality_probe(seedsA, collect_trace=True)
    probe_trace_rows = probe.pop("_trace_rows")
    probe["provenance"] = PROV.provenance(
        "run_triviality_probe",
        {"trivial_battery": list(B.TRIVIAL_BATTERY), "oracle": "map_rollout_horizon=L"},
        seedsA, "mean over family A", rid)
    _dump(probe, "triviality_probe_report.json")

    stop_conditions = []
    failure = {}
    trace_path = os.path.join(ARTIFACT_DIR, "trace.jsonl")

    if probe["metric_degenerate"]:
        stop_conditions.append("triviality_probe_failed -> invalid_metric_degenerate")
        verdict_block = compute_verdict(probe, None, None, pos_controls, secret)
        with open(trace_path, "w") as fh:
            for row in probe_trace_rows:
                fh.write(json.dumps(row, default=float) + "\n")
        replay = replay_probe_from_trace(trace_path, probe)
        replay["provenance"] = PROV.provenance("replay_probe_from_trace",
                                               {"trace": "trace.jsonl"}, seedsA, "mean", rid)
        _dump(replay, "replay_report.json")
        if not replay["matches_reported"]:
            stop_conditions.append("probe replay mismatch")
        failure = {"stage": "triviality_probe",
                   "probe": {"PF1": probe["PF1_m2_validity_fail"],
                             "PF2": probe["PF2_m1_headroom_fail"],
                             "PF3": probe["PF3_m2_detectability_fail"],
                             "band": probe["band"], "oracle_M1": probe["oracle_M1"],
                             "max_trivial_M1": probe["max_trivial_M1"],
                             "oracle_M2": probe["oracle_M2"]},
                   "stop_conditions": stop_conditions}
        _dump(failure, "failure_manifest.json")
        _dump({"skipped": "triviality probe failed; candidate NOT evaluated (gated). "
               "See triviality_probe_report.json + replay_report.json.",
               "verdict": verdict_block["verdict"]}, "baseline_comparison.json")
        _dump({"skipped": "triviality probe failed; ablations not run (candidate gated)."},
              "ablation_report.json")
    else:
        homeo_q = B.train_homeostatic_q()
        count_q = B.train_count_based_q()
        famA = evaluate_family(seedsA, homeo_q, count_q)
        famB = evaluate_family(seedsB, homeo_q, count_q)
        verdict_block = compute_verdict(probe, famA, famB, pos_controls, secret)

        baseline_cmp = {
            "family_A": famA, "family_B": famB,
            "architectural_asymmetries_logged": [
                "candidate is model-based (given true likelihood A,B; food location "
                "NOT given) -- legitimate per card; baselines are model-free.",
                "homeostatic_rl & count_based_rl are REAL tabular-Q learners trained "
                "on disjoint TRAIN_SEEDS (5000..5399); not stubs.",
                "oracle is a probe instrument only (multi-step info ceiling); excluded."],
            "access_parity": "identical env instances/obs interface/action space/budget/"
                             "seeds; no privileged food/dark/tv labels to any agent.",
            "provenance": PROV.provenance("evaluate_family", {"families": ["A", "B"]},
                                          seedsA + seedsB, "mean per family", rid)}
        _dump(baseline_cmp, "baseline_comparison.json")
        _dump({"family_A": famA["ablations"], "family_B": famB["ablations"],
               "interpretation": {
                   "epistemic_ablation_removes_advantage_A":
                       verdict_block.get("family_A_admit_check", {}).get("epistemic_ablation_removes_advantage"),
                   "no_transition_is_causal_control": True},
               "provenance": PROV.provenance("evaluate_family.ablations", {}, seedsA, "mean", rid)},
              "ablation_report.json")

        write_candidate_trace(seedsA, trace_path)
        replay = replay_candidate_from_trace(trace_path, famA["candidate"]["M1"])
        probe_trace_path = os.path.join(ARTIFACT_DIR, "probe_trace.jsonl")
        with open(probe_trace_path, "w") as fh:
            for row in probe_trace_rows:
                fh.write(json.dumps(row, default=float) + "\n")
        replay["probe_replay"] = replay_probe_from_trace(probe_trace_path, probe)
        replay["provenance"] = PROV.provenance("replay_candidate_from_trace",
                                               {"trace": "trace.jsonl"}, seedsA, "mean family A", rid)
        _dump(replay, "replay_report.json")

        if not replay["M1_match"] or not replay["action_determinism_ok"]:
            stop_conditions.append("replay mismatch")
        if verdict_block["verdict"] == "known_failure_mode_reproduced":
            stop_conditions.append("challenger trap -> known_failure_mode_reproduced")
        if stop_conditions:
            _dump({"stage": "post_evaluation", "stop_conditions": stop_conditions,
                   "verdict": verdict_block["verdict"]}, "failure_manifest.json")

    result = {
        "task_id": P.TASK_ID, "run_id": rid,
        "preregistration": P.preregistration_block(),
        "prereg_sha256": P.prereg_hash(),
        "code_path_hash": PROV.code_path_hash(),
        "secret_scan": secret,
        "verdict": verdict_block["verdict"], "verdict_detail": verdict_block,
        "triviality_probe_gate": {
            "metric_degenerate": probe["metric_degenerate"], "band": probe["band"],
            "oracle_M1": probe["oracle_M1"], "max_trivial_M1": probe["max_trivial_M1"],
            "oracle_M2": probe["oracle_M2"]},
        "stop_conditions_triggered": stop_conditions,
        "claim_ceiling": P.CLAIM_CEILING,
        "what_this_does_not_prove": P.WHAT_THIS_DOES_NOT_PROVE,
        "artifacts": ["result.json", "trace.jsonl", "baseline_comparison.json",
                      "ablation_report.json", "triviality_probe_report.json",
                      "positive_control_report.json", "replay_report.json"]
                     + (["failure_manifest.json"] if (failure or stop_conditions) else []),
    }
    _dump(result, "result.json")
    print("VERDICT:", verdict_block["verdict"])
    print("artifact_dir:", ARTIFACT_DIR)
    return result


if __name__ == "__main__":
    main()
