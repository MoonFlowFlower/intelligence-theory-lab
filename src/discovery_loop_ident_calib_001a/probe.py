"""DISCOVERY-LOOP-IDENT-CALIB-001A. Calibrate the discovery loop's OBSERVATIONAL identifiability
discrimination in 4 ground-truth-known binary-sequence worlds. Candidate-free; tool calibration.
Mechanism-under-test = EM HMM (latent predictor). Baseline = strongest held-out order-k count table.
Metric = causal one-step held-out predictive log-loss (nats/symbol), past-only. See task card.
"""
import json, hashlib, csv, os, re, sys
from collections import defaultdict
import numpy as np

PREREG = {
    "task_id": "DISCOVERY-LOOP-IDENT-CALIB-001A",
    "schema_version": "discovery-loop-ident-calib-001a.evidence.v1",
    "research_layer": "engineering_implementation+mechanism_hypothesis",
    "alphabet_M": 2, "L_train": 3000, "L_heldout": 2000, "max_order_K": 4,
    "orders": [0, 1, 2, 3, 4], "hmm_n_states": [2, 3],
    "em_restarts": 3, "em_iters": 40, "em_tol": 1e-4, "n_states_selection": "bic_full_train",
    "seeds": list(range(10)), "consistency_min": 8, "eps_nats": 0.01,
    "regimes": ["latent_necessary", "latent_redundant", "positive_control", "negative_control"],
    "world_params": {
        "latent_necessary": {"kind": "hmm2", "p_stay": 0.95, "e1_s1": 0.80, "e1_s0": 0.20},
        "latent_redundant": {"kind": "markov1", "p1_given0": 0.25, "p1_given1": 0.75},
        "positive_control": {"kind": "hmm2", "p_stay": 0.97, "e1_s1": 0.75, "e1_s0": 0.25},
        "negative_control": {"kind": "iid", "p1": 0.50},
    },
    "claim_ceiling": (
        "Bounded calibration of the discovery loop's OBSERVATIONAL identifiability discrimination "
        "on 4 synthetic ground-truth-known binary-sequence worlds. PASS = loop separates an "
        "identifiable latent mechanism and reports equivalence for a redundant one, label-blind "
        "and future-blind. NOT consciousness/subjectivity/emotion/autonomy/agency/AGI/companion. "
        "NOT interventional identifiability (observational only). NOT a proof about any specific "
        "past lab target."
    ),
    "what_this_does_not_prove": [
        "Not consciousness/subjective experience/real emotion/autonomy/agency/self-awareness/AGI.",
        "Not companion-readiness.",
        "Not interventional (do-calculus) identifiability; this run is observational only.",
        "Not that any specific past lab target was non-identifiable.",
        "Not non-identifiability for nonlinear / large-alphabet / longer-memory worlds.",
    ],
}
WORLD_BASE = {"latent_necessary": 1000, "latent_redundant": 2000,
              "positive_control": 3000, "negative_control": 4000}
N_BOOT = 1000   # EXPLORATORY (non-prereg) bootstrap; frozen verdict stays absolute-eps.


def _rng(seed):
    return np.random.default_rng(int(seed))


def _boot_ci(d, n_boot, seed):
    """Paired bootstrap CI of mean(d) over held-out positions. Exploratory only."""
    d = np.asarray(d, float); g = _rng(seed); n = len(d)
    means = d[g.integers(0, n, size=(n_boot, n))].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi)


# ---- generators (KNOWN ground truth) ----
def gen_sequence(regime, n, seed):
    wp = PREREG["world_params"][regime]; g = _rng(WORLD_BASE[regime] + seed)
    o = np.zeros(n, dtype=np.int64)
    if wp["kind"] == "iid":
        return (g.random(n) < wp["p1"]).astype(np.int64)
    if wp["kind"] == "markov1":
        p = [wp["p1_given0"], wp["p1_given1"]]
        o[0] = 1 if g.random() < 0.5 else 0
        for t in range(1, n):
            o[t] = 1 if g.random() < p[o[t - 1]] else 0
        return o
    if wp["kind"] == "hmm2":
        e1 = [wp["e1_s0"], wp["e1_s1"]]; s = 0 if g.random() < 0.5 else 1
        for t in range(n):
            o[t] = 1 if g.random() < e1[s] else 0
            if g.random() >= wp["p_stay"]:
                s = 1 - s
        return o
    raise ValueError(regime)


# ---- observation-only baseline (order-k count table) ----
def count_table_losses(train, test, k, M, offset):
    counts = defaultdict(lambda: np.zeros(M))
    for t in range(k, len(train)):
        counts[tuple(train[t - k:t].tolist())][train[t]] += 1.0
    losses = []
    for t in range(offset, len(test)):
        c = counts.get(tuple(test[t - k:t].tolist()))
        v = (c + 1.0) if c is not None else np.ones(M)
        p = v / v.sum()
        losses.append(float(-np.log(p[test[t]] + 1e-300)))
    return float(np.mean(losses)), losses


def best_baseline(train, test, orders, M, offset):
    """Strongest observation-only baseline = best held-out order k (pro-baseline / conservative)."""
    per_k = {k: count_table_losses(train, test, k, M, offset) for k in orders}
    best_k = min(per_k, key=lambda kk: per_k[kk][0])
    mean, losses = per_k[best_k]
    return best_k, mean, losses, {k: round(per_k[k][0], 6) for k in orders}


# ---- EM HMM (numpy only) ----
def _fb_scaled(obs, pi, A, E):
    T, K = len(obs), len(pi)
    Eo = E[:, obs].T
    alpha = np.empty((T, K)); c = np.empty(T)
    a = pi * Eo[0]; c[0] = a.sum() + 1e-300; alpha[0] = a / c[0]
    for t in range(1, T):
        a = (alpha[t - 1] @ A) * Eo[t]; s = a.sum() + 1e-300; c[t] = s; alpha[t] = a / s
    beta = np.empty((T, K)); beta[T - 1] = 1.0
    for t in range(T - 2, -1, -1):
        beta[t] = (A @ (Eo[t + 1] * beta[t + 1])) / c[t + 1]
    gamma = alpha * beta; gamma /= (gamma.sum(axis=1, keepdims=True) + 1e-300)
    la = alpha[:-1]; bo = Eo[1:] * beta[1:]; cc = c[1:][:, None] + 1e-300
    xi_sum = A * (la.T @ (bo / cc))
    return float(np.sum(np.log(c))), gamma, xi_sum


def _em_once(obs, K, M, rng, iters, tol):
    pi = rng.dirichlet(np.ones(K)); A = rng.dirichlet(np.ones(K) * 2.0, size=K)
    E = rng.dirichlet(np.ones(M), size=K); prev = -np.inf
    for it in range(iters):
        ll, gamma, xi_sum = _fb_scaled(obs, pi, A, E)
        pi = gamma[0] + 1e-12; pi /= pi.sum()
        A = xi_sum + 1e-12; A /= A.sum(axis=1, keepdims=True)
        En = np.zeros((K, M))
        for m_ in range(M):
            En[:, m_] = gamma[obs == m_].sum(axis=0)
        En += 1e-12; En /= En.sum(axis=1, keepdims=True); E = En
        if it > 0 and (ll - prev) < tol:
            prev = ll; break
        prev = ll
    return pi, A, E, prev


def fit_hmm(obs, K, M, restarts, iters, tol, base_seed):
    """Best of `restarts` inits by TRAIN loglik. Returns (pi, A, E, train_loglik)."""
    best = None
    for r in range(restarts):
        cand = _em_once(obs, K, M, _rng(base_seed + r * 7 + K * 1000), iters, tol)
        if best is None or cand[3] > best[3]:
            best = cand
    return best


def hmm_losses(test, pi, A, E, offset, leak=False):
    """Causal one-step held-out predictive log-loss. leak=True: oracle (scorer sees target)."""
    pred = pi.copy(); losses = []
    for t in range(len(test)):
        p_o = pred @ E; p_o = p_o / (p_o.sum() + 1e-300)
        loss = 0.0 if leak else float(-np.log(p_o[test[t]] + 1e-300))
        if t >= offset:
            losses.append(loss)
        num = pred * E[:, test[t]]; filt = num / (num.sum() + 1e-300); pred = filt @ A
    return float(np.mean(losses)), losses


def select_and_fit_hmm(train, M):
    """Select n_states by BIC on full-train fits (MDL; TRAIN-likelihood only, no held-out peek)."""
    P = PREREG; T = len(train); cands = []
    for K in P["hmm_n_states"]:
        pi, A, E, ll = fit_hmm(train, K, M, P["em_restarts"], P["em_iters"], P["em_tol"], 88000 + K)
        n_params = (K - 1) + K * (K - 1) + K * (M - 1)
        cands.append((-2.0 * ll + n_params * float(np.log(T)), K, pi, A, E))
    cands.sort(key=lambda x: (round(x[0], 6), x[1]))
    _, K, pi, A, E = cands[0]
    return K, pi, A, E


# ---- one (regime, seed) cell ----
def run_cell(regime, seed, leak=False):
    P = PREREG; M, offset = P["alphabet_M"], P["max_order_K"]
    train = gen_sequence(regime, P["L_train"], seed)
    test = gen_sequence(regime, P["L_heldout"], seed + 500)   # disjoint sample, same world
    best_k, base_mean, base_steps, per_k = best_baseline(train, test, P["orders"], M, offset)
    K, pi, A, E = select_and_fit_hmm(train, M)
    hmm_mean, hmm_steps = hmm_losses(test, pi, A, E, offset, leak=leak)
    gap = base_mean - hmm_mean
    d = np.asarray(base_steps) - np.asarray(hmm_steps)
    ci_lo, ci_hi = _boot_ci(d, N_BOOT, 20000 + WORLD_BASE[regime] + int(seed))
    row = {
        "regime": regime, "seed": int(seed), "best_base_order": int(best_k),
        "base_logloss": round(base_mean, 6), "hmm_n_states": int(K),
        "hmm_logloss": round(hmm_mean, 6), "gap": round(gap, 6),
        "separates": bool(gap >= P["eps_nats"]),        # FROZEN absolute-eps rule
        "equivalent": bool(abs(gap) < P["eps_nats"]),   # FROZEN absolute-eps rule
        "gap_ci_low": round(ci_lo, 6), "gap_ci_high": round(ci_hi, 6),   # exploratory
        "sig_pos": bool(ci_lo > 0.0), "sig_neg": bool(ci_hi < 0.0),       # exploratory
        "base_order_losses": per_k,
    }
    return row, base_steps, hmm_steps


# ---- verdicts ----
def _world_verdict(rows):
    cmin = PREREG["consistency_min"]
    sep = sum(1 for r in rows if r["separates"]); equ = sum(1 for r in rows if r["equivalent"])
    v = "separates" if sep >= cmin else ("equivalent" if equ >= cmin else "indeterminate")
    return v, sep, equ


def compute_verdict(by_regime):
    """FROZEN pre-registered verdict (absolute-eps rule). Gates in order; fail-able."""
    detail, wv = {}, {}
    for regime in PREREG["regimes"]:
        v, sep, equ = _world_verdict(by_regime[regime]); wv[regime] = v
        detail[regime] = {"world_verdict": v, "separates_seeds": sep, "equivalent_seeds": equ,
                          "n_seeds": len(by_regime[regime])}
    detail["eps_nats"] = PREREG["eps_nats"]; detail["consistency_min"] = PREREG["consistency_min"]
    if wv["positive_control"] != "separates":
        return "check_underpowered_loop_blind", detail
    if wv["negative_control"] == "separates":
        return "check_invalid_false_separation", detail
    if wv["latent_necessary"] == "separates" and wv["latent_redundant"] == "equivalent":
        return "loop_calibrated__separates_identifiable_reports_equivalent_when_redundant", detail
    if wv["latent_necessary"] == "separates" and wv["latent_redundant"] != "equivalent":
        return "loop_separates_but_redundant_not_clean", detail
    if wv["latent_necessary"] != "separates":
        return "loop_misses_identifiable_latent", detail
    return "indeterminate", detail


def compute_sig_view(by_regime):
    """EXPLORATORY (NOT pre-registered) significance view via paired bootstrap CIs."""
    cmin = PREREG["consistency_min"]; out, wv = {}, {}
    for regime in PREREG["regimes"]:
        rows = by_regime[regime]
        sp = sum(1 for r in rows if r["sig_pos"]); sn = sum(1 for r in rows if r["sig_neg"])
        eq = sum(1 for r in rows if not r["sig_pos"] and not r["sig_neg"])
        v = "separates_sig" if sp >= cmin else ("equivalent_sig" if eq >= cmin else "indeterminate_sig")
        wv[regime] = v
        out[regime] = {"sig_world_verdict": v, "sig_pos_seeds": sp, "sig_neg_seeds": sn,
                       "ci_contains_zero_seeds": eq, "n_seeds": len(rows)}
    if wv["positive_control"] != "separates_sig":
        meta = "exploratory_underpowered"
    elif wv["negative_control"] == "separates_sig":
        meta = "exploratory_false_separation"
    elif wv["latent_necessary"] == "separates_sig" and wv["latent_redundant"] == "equivalent_sig":
        meta = "exploratory_loop_calibrated"
    else:
        meta = "exploratory_mixed"
    out["exploratory_meta"] = meta
    out["label"] = ("POST-SMOKE EXPLORATORY, NOT PRE-REGISTERED. Primary verdict = frozen "
                    "absolute-eps rule (result.verdict). Bootstrap-CI power diagnostic only.")
    return out


def replay_verdict_from_trace(trace_csv):
    by = {r: [] for r in PREREG["regimes"]}; eps = PREREG["eps_nats"]
    with open(trace_csv, newline="") as f:
        for row in csv.DictReader(f):
            gap = float(row["gap"])
            by[row["regime"]].append({"separates": gap >= eps, "equivalent": abs(gap) < eps})
    return compute_verdict(by)


def _sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _secret_scan(path):
    pat = re.compile(r"(ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})")
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        hits = pat.findall(f.read())
    return {"clean": len(hits) == 0, "n_findings": len(hits)}


def run_all():
    by_regime = {r: [] for r in PREREG["regimes"]}; perstep0 = []
    for regime in PREREG["regimes"]:
        for seed in PREREG["seeds"]:
            row, bs, hs = run_cell(regime, seed, leak=False)
            by_regime[regime].append(row)
            if seed == 0:
                K = PREREG["max_order_K"]
                for i, (b, h) in enumerate(zip(bs, hs)):
                    perstep0.append({"regime": regime, "seed": 0, "t": K + i,
                                     "base_logloss_t": round(b, 6), "hmm_logloss_t": round(h, 6)})
    return by_regime, perstep0


def write_all_artifacts(out_dir, by_regime, perstep0):
    os.makedirs(out_dir, exist_ok=True)
    code_path_hash = _sha256_file(os.path.abspath(__file__))
    prereg_sha256 = hashlib.sha256(json.dumps(PREREG, sort_keys=True).encode()).hexdigest()
    secret = _secret_scan(os.path.abspath(__file__))

    trace_csv = os.path.join(out_dir, "trace.csv")
    fields = ["regime", "seed", "best_base_order", "base_logloss", "hmm_n_states", "hmm_logloss",
              "gap", "separates", "equivalent", "gap_ci_low", "gap_ci_high", "sig_pos", "sig_neg"]
    with open(trace_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for regime in PREREG["regimes"]:
            for r in by_regime[regime]:
                w.writerow({k: r[k] for k in fields})
    with open(os.path.join(out_dir, "trace.jsonl"), "w") as f:
        for rec in perstep0:
            f.write(json.dumps(rec) + "\n")

    verdict, detail = compute_verdict(by_regime)
    sig_view = compute_sig_view(by_regime)
    replay_verdict, replay_detail = replay_verdict_from_trace(trace_csv)

    spot = {}
    for regime in PREREG["regimes"]:
        steps = [r for r in perstep0 if r["regime"] == regime]
        b = float(np.mean([s["base_logloss_t"] for s in steps]))
        h = float(np.mean([s["hmm_logloss_t"] for s in steps]))
        gap_csv = next(r["gap"] for r in by_regime[regime] if r["seed"] == 0)
        spot[regime] = {"gap_from_steps": round(b - h, 6), "gap_in_trace_csv": gap_csv,
                        "match": abs((b - h) - gap_csv) < 1e-6}
    if not secret["clean"]:
        verdict = "BLOCK_secret_present"

    def regstats(regime):
        rs = by_regime[regime]
        return {
            "base_logloss_mean": round(float(np.mean([r["base_logloss"] for r in rs])), 6),
            "hmm_logloss_mean": round(float(np.mean([r["hmm_logloss"] for r in rs])), 6),
            "gap_mean": round(float(np.mean([r["gap"] for r in rs])), 6),
            "gap_min": round(float(np.min([r["gap"] for r in rs])), 6),
            "gap_max": round(float(np.max([r["gap"] for r in rs])), 6),
            "separates_seeds": int(sum(r["separates"] for r in rs)),
            "equivalent_seeds": int(sum(r["equivalent"] for r in rs)),
            "sig_pos_seeds": int(sum(r["sig_pos"] for r in rs)),
            "sig_neg_seeds": int(sum(r["sig_neg"] for r in rs)),
            "best_base_order_mode": int(np.bincount([r["best_base_order"] for r in rs]).argmax()),
        }
    baseline_comparison = {
        "mechanism_under_test": "em_hmm_latent_state_predictor",
        "baseline": "order_k_count_table_observation_only (strongest held-out k)",
        "access_parity": "same train/held-out, scored on identical positions t>=max_order_K; only model class differs",
        "metric": "causal one-step held-out predictive log-loss (nats/symbol), past-only",
        "eps_nats": PREREG["eps_nats"],
        "per_regime": {r: regstats(r) for r in PREREG["regimes"]},
    }
    ablation_report = {
        "positive_control": {"purpose": "sensitivity: loop MUST separate a guaranteed-identifiable world",
                             "world_verdict": detail["positive_control"]["world_verdict"],
                             "separates_seeds": detail["positive_control"]["separates_seeds"],
                             "passed": detail["positive_control"]["world_verdict"] == "separates"},
        "negative_control": {"purpose": "specificity: loop MUST NOT separate a no-structure (i.i.d.) world",
                             "world_verdict": detail["negative_control"]["world_verdict"],
                             "separates_seeds": detail["negative_control"]["separates_seeds"],
                             "passed": detail["negative_control"]["world_verdict"] != "separates"},
        "substantive": {"latent_necessary_verdict": detail["latent_necessary"]["world_verdict"],
                        "latent_redundant_verdict": detail["latent_redundant"]["world_verdict"]},
        "leakage_probe_note": "tests exercise hmm_losses(leak=True): oracle leak MUST flip negative_control to separates -> check_invalid_false_separation",
    }
    replay_report = {
        "replay_verdict": replay_verdict, "result_verdict": verdict,
        "match": replay_verdict == verdict, "replay_detail": replay_detail,
        "per_step_spot_check_seed0": spot,
        "per_step_spot_check_all_match": all(v["match"] for v in spot.values()),
        "method": "recompute frozen verdict from trace.csv gaps only; plus recompute seed-0 gaps from per-step trace.jsonl",
    }
    result = {
        "task_id": PREREG["task_id"], "run_id": "local_discovery_loop_ident_calib_001a",
        "preregistration": PREREG, "prereg_sha256": prereg_sha256, "code_path_hash": code_path_hash,
        "secret_scan": {"run_path": os.path.abspath(__file__), **secret},
        "verdict": verdict, "verdict_detail": detail, "exploratory_significance_view": sig_view,
        "per_seed_rows": {r: by_regime[r] for r in PREREG["regimes"]},
        "claim_ceiling": PREREG["claim_ceiling"],
        "what_this_does_not_prove": PREREG["what_this_does_not_prove"],
        "artifacts": ["result.json", "trace.csv", "trace.jsonl", "baseline_comparison.json",
                      "ablation_report.json", "replay_report.json", "claim_ceiling.txt"],
    }
    for name, obj in [("result.json", result), ("baseline_comparison.json", baseline_comparison),
                      ("ablation_report.json", ablation_report), ("replay_report.json", replay_report)]:
        with open(os.path.join(out_dir, name), "w") as f:
            json.dump(obj, f, indent=2)
    with open(os.path.join(out_dir, "claim_ceiling.txt"), "w") as f:
        f.write(PREREG["claim_ceiling"] + "\n")
    if verdict in ("check_underpowered_loop_blind", "check_invalid_false_separation",
                   "BLOCK_secret_present") or not replay_report["match"] \
            or not replay_report["per_step_spot_check_all_match"]:
        with open(os.path.join(out_dir, "failure_manifest.json"), "w") as f:
            json.dump({"verdict": verdict, "replay_match": replay_report["match"],
                       "spot_check_all_match": replay_report["per_step_spot_check_all_match"],
                       "detail": detail}, f, indent=2)

    print(json.dumps({
        "verdict": verdict, "replay_match": replay_report["match"],
        "spot_check_all_match": replay_report["per_step_spot_check_all_match"],
        "world_verdicts": {r: detail[r]["world_verdict"] for r in PREREG["regimes"]},
        "exploratory_sig_world": {r: sig_view[r]["sig_world_verdict"] for r in PREREG["regimes"]},
        "exploratory_meta": sig_view["exploratory_meta"],
        "gaps_mean": {r: baseline_comparison["per_regime"][r]["gap_mean"] for r in PREREG["regimes"]},
        "prereg_sha256": prereg_sha256[:12], "code_path_hash": code_path_hash[:12],
        "secret_clean": secret["clean"],
    }, indent=2))
    return result


def main(out_dir):
    by_regime, perstep0 = run_all()
    return write_all_artifacts(out_dir, by_regime, perstep0)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "artifacts/DISCOVERY-LOOP-IDENT-CALIB-001A")
