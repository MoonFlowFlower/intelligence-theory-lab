"""DISCOVERY-LOOP-MDE-POWER-CURVE-001A.

Builds the agreed fix (#4): a power statement = minimum detectable effect (MDE) for the 001A
discovery loop, then (#5) charts MDE vs training budget. The loop (order-k count-table baseline +
EM-HMM + causal one-step held-out log-loss + eps=0.01) is imported UNCHANGED from 001A.

true_gap (effect size) is an ORACLE quantity (true generative params, large held-out) used only to
LABEL the x-axis; it never reaches the fitted model under test. n_states fixed to 2 (001A's BIC
selection chose K=2 in 40/40 cells). Claim ceiling: bounded power analysis on a 2-state-HMM family.
"""
import json, hashlib, csv, os, re, sys
from collections import defaultdict
import numpy as np

# 001A loop primitives (identical baseline / HMM / scorer)
from discovery_loop_ident_calib_001a.probe import best_baseline, fit_hmm, hmm_losses

PREREG = {
    "task_id": "DISCOVERY-LOOP-MDE-POWER-CURVE-001A",
    "schema_version": "discovery-loop-mde-power-curve-001a.evidence.v1",
    "research_layer": "engineering_implementation+mechanism_hypothesis",
    "M": 2, "max_order_K": 4, "orders": [0, 1, 2, 3, 4],
    "e1_s1": 0.80, "e1_s0": 0.20,                 # emission fixed (001A latent_necessary family)
    "p_stay_worlds": [0.85, 0.92, 0.95, 0.97, 0.99],
    "L_train_budgets": [1500, 3000, 6000], "L_heldout": 3000,
    "hmm_n_states_fixed": 2, "em_restarts": 3, "em_iters": 40, "em_tol": 1e-4,
    "eps_nats": 0.01, "seeds": list(range(10)), "power_threshold": 0.8,
    "oracle_big_L": 20000, "c2_tol": 0.002,
    "claim_ceiling": (
        "Bounded power analysis of the 001A discovery loop on a 2-state-HMM effect-size family "
        "(binary alphabet, emission 0.8/0.2). Produces MDE(L) = minimum true latent advantage the "
        "loop detects at budget L (power>=0.8), and a reusable power-statement primitive. NOT "
        "consciousness/subjectivity/emotion/autonomy/agency/AGI. NOT interventional. MDE values are "
        "specific to this alphabet/model/family."
    ),
    "what_this_does_not_prove": [
        "Not consciousness/subjectivity/emotion/autonomy/agency/AGI/companion-readiness.",
        "Not interventional identifiability.",
        "Not a general MDE for other alphabets/models/effect families.",
        "Not that any specific past lab target's effect was above or below this MDE.",
    ],
}


def _wbase(p_stay):
    return 500000 + int(round(p_stay * 100)) * 1000


def gen_hmm2(p_stay, e1_s1, e1_s0, n, seed):
    g = np.random.default_rng(int(seed)); o = np.zeros(n, dtype=np.int64)
    e1 = [e1_s0, e1_s1]; s = 0 if g.random() < 0.5 else 1
    for t in range(n):
        o[t] = 1 if g.random() < e1[s] else 0
        if g.random() >= p_stay:
            s = 1 - s
    return o


def true_params(p_stay, e1_s1, e1_s0):
    pi = np.array([0.5, 0.5])
    A = np.array([[p_stay, 1 - p_stay], [1 - p_stay, p_stay]])
    E = np.array([[1 - e1_s0, e1_s0], [1 - e1_s1, e1_s1]])   # E[s,o] = P(o|s)
    return pi, A, E


def oracle_true_gap(p_stay):
    """Effect size: asymptotic latent advantage (best count table - true HMM) on large held-out.
    Uses TRUE params; this DEFINES the effect size and never reaches the fitted model."""
    P = PREREG; M, off, big, base = P["M"], P["max_order_K"], P["oracle_big_L"], _wbase(p_stay)
    tr = gen_hmm2(p_stay, P["e1_s1"], P["e1_s0"], big, base + 99999)
    te = gen_hmm2(p_stay, P["e1_s1"], P["e1_s0"], big, base + 88888)
    _, base_mean, _, _ = best_baseline(tr, te, P["orders"], M, off)
    pi, A, E = true_params(p_stay, P["e1_s1"], P["e1_s0"])
    hmm_mean, _ = hmm_losses(te, pi, A, E, off, leak=False)
    return round(base_mean - hmm_mean, 6)


def run_fitted_cell(p_stay, L_train, seed):
    """Fitted loop (identical to 001A, K=2): does it separate this world at this budget?"""
    P = PREREG; M, off, base = P["M"], P["max_order_K"], _wbase(p_stay)
    train = gen_hmm2(p_stay, P["e1_s1"], P["e1_s0"], int(L_train), base + seed)
    test = gen_hmm2(p_stay, P["e1_s1"], P["e1_s0"], P["L_heldout"], base + seed + 500)
    bk, base_mean, _, _ = best_baseline(train, test, P["orders"], M, off)
    pi, A, E, _ = fit_hmm(train, P["hmm_n_states_fixed"], M, P["em_restarts"], P["em_iters"],
                          P["em_tol"], base + seed + 700000 + int(L_train))
    hmm_mean, _ = hmm_losses(test, pi, A, E, off, leak=False)
    gap = base_mean - hmm_mean
    return {"p_stay": p_stay, "L_train": int(L_train), "seed": int(seed),
            "base_logloss": round(base_mean, 6), "hmm_logloss": round(hmm_mean, 6),
            "gap": round(gap, 6), "separates": bool(gap >= P["eps_nats"]),
            "best_base_order": int(bk)}


def compute_power_curve(by_cell, oracle_gaps):
    P = PREREG; thr = P["power_threshold"]; Ls = P["L_train_budgets"]
    ps = sorted(P["p_stay_worlds"])
    worlds_by_gap = sorted(ps, key=lambda p: oracle_gaps[p])
    power = {}
    for L in Ls:
        power[L] = {}
        for p in ps:
            rows = by_cell[p][L]
            power[L][p] = round(sum(r["separates"] for r in rows) / len(rows), 3)
    mde = {}
    for L in Ls:
        detected = [p for p in worlds_by_gap if power[L][p] >= thr]
        if not detected:
            mde[L] = {"mde": None, "bound": ">max_true_gap=%.5f" % oracle_gaps[worlds_by_gap[-1]]}
        elif len(detected) == len(ps):
            mde[L] = {"mde": oracle_gaps[worlds_by_gap[0]], "bound": "<=min_true_gap_tested"}
        else:
            pdet = min(detected, key=lambda p: oracle_gaps[p])
            mde[L] = {"mde": oracle_gaps[pdet], "p_stay": pdet}
    c1_inv = {}
    c1_ok = True
    for L in Ls:
        seq = [power[L][p] for p in worlds_by_gap]
        inv = sum(1 for i in range(len(seq) - 1) for j in range(i + 1, len(seq)) if seq[i] > seq[j] + 1e-9)
        c1_inv[L] = inv
        if inv > 1:
            c1_ok = False

    def mval(L):
        m = mde[L]["mde"]; return m if m is not None else 1e9
    c2_ok = all(mval(Ls[i + 1]) <= mval(Ls[i]) + P["c2_tol"] for i in range(len(Ls) - 1))
    if not c1_ok:
        verdict = "check_effect_knob_not_monotone"
    elif not c2_ok:
        verdict = "check_power_curve_nonmonotone"
    else:
        verdict = "power_curve_estimated__mde_decreases_with_budget"
    detail = {"power": {str(L): power[L] for L in Ls}, "mde": {str(L): mde[L] for L in Ls},
              "oracle_true_gaps": oracle_gaps, "worlds_by_gap": worlds_by_gap,
              "c1_inversions": {str(L): c1_inv[L] for L in Ls}, "c1_ok": c1_ok, "c2_ok": c2_ok,
              "power_threshold": thr, "L_budgets": Ls}
    return verdict, detail


def power_statement(L, detail):
    """Reusable fix (#4): turn a negative/equivalence verdict at budget L into a power statement."""
    m = detail["mde"].get(str(L))
    if m is None:
        return "no MDE for budget %s" % L
    if m["mde"] is None:
        return ("At L_train=%s the loop detected NO tested effect with power>=%.2f; equivalence "
                "rules out nothing within tested range (%s)." % (L, detail["power_threshold"], m["bound"]))
    return ("At L_train=%s the loop's minimum detectable latent advantage is ~%.4f nats/symbol "
            "(power>=%.2f). An 'equivalence' verdict here only rules out true latent advantages "
            "ABOVE ~%.4f; smaller real effects are indistinguishable from equivalence."
            % (L, m["mde"], detail["power_threshold"], m["mde"]))


def replay_from_trace(trace_csv):
    by_cell = defaultdict(lambda: defaultdict(list)); oracle = {}
    with open(trace_csv, newline="") as f:
        for row in csv.DictReader(f):
            p = float(row["p_stay"]); L = int(row["L_train"])
            by_cell[p][L].append({"separates": row["separates"] == "True"})
            oracle[p] = float(row["true_gap"])
    return compute_power_curve(by_cell, oracle)


def _sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _secret_scan(path):
    pat = re.compile(r"(ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})")
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        hits = pat.findall(f.read())
    return {"clean": len(hits) == 0, "n_findings": len(hits)}


def write_all_artifacts(out_dir, cells, oracle_gaps):
    os.makedirs(out_dir, exist_ok=True)
    code_path_hash = _sha256_file(os.path.abspath(__file__))
    prereg_sha256 = hashlib.sha256(json.dumps(PREREG, sort_keys=True).encode()).hexdigest()
    secret = _secret_scan(os.path.abspath(__file__))

    by_cell = defaultdict(lambda: defaultdict(list))
    for r in cells:
        by_cell[r["p_stay"]][r["L_train"]].append(r)

    trace_csv = os.path.join(out_dir, "trace.csv")
    fields = ["p_stay", "L_train", "seed", "true_gap", "base_logloss", "hmm_logloss", "gap",
              "separates", "best_base_order"]
    with open(trace_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in sorted(cells, key=lambda x: (x["p_stay"], x["L_train"], x["seed"])):
            row = dict(r); row["true_gap"] = oracle_gaps[r["p_stay"]]
            w.writerow({k: row[k] for k in fields})

    verdict, detail = compute_power_curve(by_cell, oracle_gaps)
    replay_verdict, replay_detail = replay_from_trace(trace_csv)
    if not secret["clean"]:
        verdict = "BLOCK_secret_present"

    Ls = PREREG["L_train_budgets"]
    statements = {str(L): power_statement(L, detail) for L in Ls}
    # tie-back to 001A at L=3000
    tieback = {}
    if 3000 in PREREG["L_train_budgets"]:
        for p in (0.95, 0.97):
            if p in PREREG["p_stay_worlds"]:
                tieback["p_stay_%s_power_at_3000" % p] = detail["power"]["3000"][p]

    result = {
        "task_id": PREREG["task_id"], "run_id": "local_mde_power_curve_001a",
        "preregistration": PREREG, "prereg_sha256": prereg_sha256, "code_path_hash": code_path_hash,
        "secret_scan": {"run_path": os.path.abspath(__file__), **secret},
        "verdict": verdict, "power_curve_detail": detail, "power_statements": statements,
        "tieback_001a": tieback, "per_cell_rows": cells,
        "claim_ceiling": PREREG["claim_ceiling"],
        "what_this_does_not_prove": PREREG["what_this_does_not_prove"],
        "artifacts": ["result.json", "trace.csv", "power_curve.json", "baseline_comparison.json",
                      "ablation_report.json", "replay_report.json", "claim_ceiling.txt"],
    }
    power_curve = {"oracle_true_gaps": oracle_gaps, "worlds_by_gap": detail["worlds_by_gap"],
                   "power": detail["power"], "mde_by_budget": detail["mde"],
                   "power_threshold": detail["power_threshold"], "power_statements": statements}
    baseline_comparison = {
        "mechanism_under_test": "em_hmm_latent_state_predictor (K=2, identical to 001A loop)",
        "baseline": "order_k_count_table_observation_only (strongest held-out k)",
        "effect_size_axis": "ORACLE true_gap = best count table - true HMM on large held-out (true params)",
        "metric": "causal one-step held-out predictive log-loss (nats/symbol), past-only",
        "eps_nats": PREREG["eps_nats"],
        "per_world_oracle_true_gap": oracle_gaps,
        "per_budget_power": detail["power"],
    }
    ablation_report = {
        "C1_monotone_in_effect": {"purpose": "power must be non-decreasing in true_gap at each budget",
                                  "inversions_per_budget": detail["c1_inversions"], "passed": detail["c1_ok"]},
        "C2_monotone_in_budget": {"purpose": "MDE must be non-increasing as L_train grows (tol %.4f)" % PREREG["c2_tol"],
                                  "mde_by_budget": detail["mde"], "passed": detail["c2_ok"]},
        "oracle_sanity": {"min_world_gap": oracle_gaps[detail["worlds_by_gap"][0]],
                          "max_world_gap": oracle_gaps[detail["worlds_by_gap"][-1]],
                          "ordered": oracle_gaps[detail["worlds_by_gap"][-1]] > oracle_gaps[detail["worlds_by_gap"][0]]},
    }
    replay_report = {"replay_verdict": replay_verdict, "result_verdict": verdict,
                     "match": replay_verdict == verdict,
                     "replay_mde": replay_detail["mde"], "result_mde": detail["mde"],
                     "mde_match": replay_detail["mde"] == detail["mde"],
                     "method": "recompute power + MDE + verdict from trace.csv (separates + true_gap) only"}
    for name, obj in [("result.json", result), ("power_curve.json", power_curve),
                      ("baseline_comparison.json", baseline_comparison),
                      ("ablation_report.json", ablation_report), ("replay_report.json", replay_report)]:
        with open(os.path.join(out_dir, name), "w") as f:
            json.dump(obj, f, indent=2)
    with open(os.path.join(out_dir, "claim_ceiling.txt"), "w") as f:
        f.write(PREREG["claim_ceiling"] + "\n")
    if verdict.startswith("check_") or verdict.startswith("BLOCK_") or not replay_report["match"]:
        with open(os.path.join(out_dir, "failure_manifest.json"), "w") as f:
            json.dump({"verdict": verdict, "replay_match": replay_report["match"], "detail": detail}, f, indent=2)

    print(json.dumps({"verdict": verdict, "replay_match": replay_report["match"],
                      "mde_match": replay_report["mde_match"],
                      "mde_by_budget": {str(L): detail["mde"][str(L)] for L in Ls},
                      "oracle_true_gaps": oracle_gaps, "tieback_001a": tieback,
                      "prereg_sha256": prereg_sha256[:12], "code_path_hash": code_path_hash[:12],
                      "secret_clean": secret["clean"]}, indent=2))
    return result


def main(out_dir):
    cells = []
    for p in PREREG["p_stay_worlds"]:
        for L in PREREG["L_train_budgets"]:
            for s in PREREG["seeds"]:
                cells.append(run_fitted_cell(p, L, s))
    oracle_gaps = {p: oracle_true_gap(p) for p in PREREG["p_stay_worlds"]}
    return write_all_artifacts(out_dir, cells, oracle_gaps)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "artifacts/DISCOVERY-LOOP-MDE-POWER-CURVE-001A")
