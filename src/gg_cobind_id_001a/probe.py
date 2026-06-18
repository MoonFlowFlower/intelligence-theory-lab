"""GG-COBIND-ID-001A: co-binding identifiability probe (candidate-free).

Isolates the K2 blocker from GROUNDING-GATE-K1-K2-PREFLIGHT-FEASIBILITY-001A.md:
is "do(L=v) -> all 3 channels change coherently" identifiable as evidence of a SHARED latent,
or reproduced by INDEPENDENT per-channel regressors with no shared latent?

Candidate-free: generator + independent-ridge baseline + shared rank-1 score model + positive
and negative controls. NOT the proposed grounding-gate mechanism.

Claim ceiling: bounded statement about LINEAR interventional co-binding identifiability in ONE
toy world. NOT self/agency/emotion/subjectivity. Does NOT prove non-identifiability for
nonlinear mechanisms.
"""
import json
import hashlib
import csv
import os
import re
import sys
import numpy as np

PREREG = {
    "task_id": "GG-COBIND-ID-001A",
    "schema_version": "gg-cobind-id-001a.evidence.v1",
    "research_layer": "engineering_implementation+mechanism_hypothesis",
    "d_L": 6,
    "n_channels": 3,
    "rank_hypothesis": 1,
    "n_ample": 400,
    "n_poor": 15,
    "n_poor_pc": 8,
    "n_heldout": 2000,
    "noise_sd": 0.3,
    "ridge_lambda_grid": [1e-3, 1e-2, 1e-1, 1.0, 10.0],
    "seeds": list(range(10)),
    "DELTA_R2": 0.05,
    "consistency_min": 8,
    "eval_target": "noise_free_signal",
    "regimes": ["balanced_ample", "imbalanced", "positive_control", "negative_control"],
    "claim_ceiling": (
        "Bounded identifiability statement for LINEAR interventional co-binding in ONE toy "
        "world. NOT self, agency, emotion, autonomy, subjectivity, companion-readiness. Does "
        "NOT prove non-identifiability for nonlinear mechanisms; informs grounding-gate "
        "gate-to-draft decision only."
    ),
    "what_this_does_not_prove": [
        "Not self.", "Not agency.", "Not emotion.", "Not autonomy.", "Not subjectivity.",
        "Not companion-readiness.",
        "Not non-identifiability for nonlinear mechanisms.",
        "Not that the grounding gate is impossible in every world.",
    ],
}


def _rng(seed):
    return np.random.default_rng(int(seed))


def make_world(seed, shared=True):
    """Generative params B (d x k). shared=True: rank-1 (one shared score drives all channels).
    shared=False (negative control): disjoint drivers (channel j uses L[2j:2j+2] only -> no
    single shared score)."""
    g = _rng(seed)
    d, k = PREREG["d_L"], PREREG["n_channels"]
    if shared:
        u = g.standard_normal(d)
        u /= (np.linalg.norm(u) + 1e-12)
        v = g.standard_normal(k)
        B = np.outer(u, v)          # rank-1: every channel proportional to score (L.u)
    else:
        B = np.zeros((d, k))
        for j in range(k):
            w = np.zeros(d)
            w[2 * j:2 * j + 2] = g.standard_normal(2)
            B[:, j] = w             # disjoint subspaces -> rank ~ k, no shared score
    return B


def gen_samples(B, n, seed, noise_sd):
    g = _rng(seed)
    L = g.standard_normal((n, B.shape[0]))
    signal = L @ B
    y = signal + g.standard_normal(signal.shape) * noise_sd
    return L, y, signal


def ridge_fit(X, y, lam):
    d = X.shape[1]
    return np.linalg.solve(X.T @ X + lam * np.eye(d), X.T @ y)


def _r2(pred, target):
    ss_res = float(np.sum((target - pred) ** 2))
    ss_tot = float(np.sum((target - np.mean(target)) ** 2)) + 1e-12
    return 1.0 - ss_res / ss_tot


def select_lambda(X, y, grid, seed):
    """Fair per-channel ridge lambda selection on a validation split."""
    g = _rng(seed + 777)
    n = X.shape[0]
    idx = g.permutation(n)
    cut = max(2, int(0.7 * n))
    tr, va = idx[:cut], idx[cut:]
    if len(va) == 0:
        return grid[len(grid) // 2]
    best, best_lam = -np.inf, grid[0]
    for lam in grid:
        w = ridge_fit(X[tr], y[tr], lam)
        score = _r2(X[va] @ w, y[va])
        if score > best:
            best, best_lam = score, lam
    return best_lam


def fit_independent(L_by_ch, y_by_ch, grid, seed):
    """Independent ridge per channel (competent regularized baseline; no shared latent)."""
    W = []
    for k in range(len(y_by_ch)):
        lam = select_lambda(L_by_ch[k], y_by_ch[k], grid, seed + k)
        W.append(ridge_fit(L_by_ch[k], y_by_ch[k], lam))
    return W


def fit_shared(L_by_ch, y_by_ch, grid, seed):
    """Shared rank-1 score model: one shared direction u (from the data-richest channel), then a
    per-channel scalar loading. The literal 'one latent score co-binds all channels' hypothesis."""
    rich = int(np.argmax([len(y) for y in y_by_ch]))
    lam = select_lambda(L_by_ch[rich], y_by_ch[rich], grid, seed)
    w_rich = ridge_fit(L_by_ch[rich], y_by_ch[rich], lam)
    u = w_rich / (np.linalg.norm(w_rich) + 1e-12)
    A = []
    for k in range(len(y_by_ch)):
        s = L_by_ch[k] @ u
        A.append(float(np.sum(s * y_by_ch[k]) / (np.sum(s * s) + 1e-9)))
    return u, np.array(A)


def predict_independent(W, L):
    return np.stack([L @ W[k] for k in range(len(W))], axis=1)


def predict_shared(u, A, L):
    s = L @ u
    return np.stack([A[k] * s for k in range(len(A))], axis=1)


def run_regime(regime, seed):
    shared_world = (regime != "negative_control")
    B = make_world(seed, shared=shared_world)
    k, grid, noise = PREREG["n_channels"], PREREG["ridge_lambda_grid"], PREREG["noise_sd"]
    if regime == "balanced_ample":
        ns = [PREREG["n_ample"]] * k
    elif regime == "positive_control":
        ns = [PREREG["n_ample"]] + [PREREG["n_poor_pc"]] * (k - 1)
    else:  # imbalanced, negative_control
        ns = [PREREG["n_ample"]] + [PREREG["n_poor"]] * (k - 1)

    L_by_ch, y_by_ch = [], []
    for ch in range(k):
        Lc, yc, _ = gen_samples(B, ns[ch], seed * 100 + ch + 1, noise)
        L_by_ch.append(Lc)
        y_by_ch.append(yc[:, ch])
    Lh, _, sigh = gen_samples(B, PREREG["n_heldout"], seed * 100 + 999, noise)

    W = fit_independent(L_by_ch, y_by_ch, grid, seed)
    u, A = fit_shared(L_by_ch, y_by_ch, grid, seed)
    pred_i = predict_independent(W, Lh)
    pred_s = predict_shared(u, A, Lh)

    rows = []
    for ch in range(k):
        r2i = _r2(pred_i[:, ch], sigh[:, ch])
        r2s = _r2(pred_s[:, ch], sigh[:, ch])
        rows.append({
            "regime": regime, "seed": int(seed), "channel": ch, "n_train": int(ns[ch]),
            "independent_r2": round(r2i, 6), "shared_r2": round(r2s, 6),
            "delta_shared_minus_independent": round(r2s - r2i, 6),
        })
    return rows


def _poor_channel_win_seeds(rows, delta):
    """# of seeds where mean(shared-independent) over POOR channels (ch>=1) >= delta."""
    per_seed = {}
    for r in rows:
        if r["channel"] >= 1:
            per_seed.setdefault(r["seed"], []).append(r["delta_shared_minus_independent"])
    wins = sum(1 for ds in per_seed.values() if float(np.mean(ds)) >= delta)
    return wins, len(per_seed)


def _balanced_independent_reproduces_seeds(rows, delta):
    """# of seeds where, over ALL channels, shared does NOT beat independent by band (tie/indep>=)."""
    per_seed = {}
    for r in rows:
        per_seed.setdefault(r["seed"], []).append(r["delta_shared_minus_independent"])
    cnt = sum(1 for ds in per_seed.values() if float(np.mean(ds)) < delta)
    return cnt, len(per_seed)


def compute_verdict(by_regime):
    delta, cmin = PREREG["DELTA_R2"], PREREG["consistency_min"]
    pc_wins, pc_tot = _poor_channel_win_seeds(by_regime["positive_control"], delta)
    nc_wins, nc_tot = _poor_channel_win_seeds(by_regime["negative_control"], delta)
    im_wins, im_tot = _poor_channel_win_seeds(by_regime["imbalanced"], delta)
    ba_rep, ba_tot = _balanced_independent_reproduces_seeds(by_regime["balanced_ample"], delta)

    detail = {
        "positive_control_win_seeds": [pc_wins, pc_tot],
        "negative_control_win_seeds": [nc_wins, nc_tot],
        "imbalanced_win_seeds": [im_wins, im_tot],
        "balanced_independent_reproduces_seeds": [ba_rep, ba_tot],
        "DELTA_R2": delta, "consistency_min": cmin,
    }
    if pc_wins < cmin:
        return "check_underpowered_invalid", detail
    if nc_wins >= cmin:
        return "check_invalid_false_transfer", detail
    if ba_rep >= cmin:
        if im_wins >= cmin:
            return "co_binding_non_identifiable__only_transfer_headroom", detail
        return "co_binding_non_identifiable__no_headroom", detail
    return "headroom_co_binding_identifiable_surprising", detail


def replay_from_trace(trace_path):
    by_regime = {r: [] for r in PREREG["regimes"]}
    with open(trace_path, newline="") as f:
        for row in csv.DictReader(f):
            by_regime[row["regime"]].append({
                "regime": row["regime"], "seed": int(row["seed"]),
                "channel": int(row["channel"]), "n_train": int(row["n_train"]),
                "independent_r2": float(row["independent_r2"]),
                "shared_r2": float(row["shared_r2"]),
                "delta_shared_minus_independent": float(row["delta_shared_minus_independent"]),
            })
    return compute_verdict(by_regime)


def _sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _secret_scan(path):
    pat = re.compile(r"(ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})")
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        hits = pat.findall(f.read())
    return {"clean": len(hits) == 0, "n_findings": len(hits)}


def _agg(rows):
    by = {}
    for r in rows:
        by.setdefault(r["channel"], {"indep": [], "shared": []})
        by[r["channel"]]["indep"].append(r["independent_r2"])
        by[r["channel"]]["shared"].append(r["shared_r2"])
    out = {}
    for ch, d in by.items():
        out[f"channel_{ch}"] = {
            "independent_r2_mean": round(float(np.mean(d["indep"])), 6),
            "independent_r2_std": round(float(np.std(d["indep"])), 6),
            "shared_r2_mean": round(float(np.mean(d["shared"])), 6),
            "shared_r2_std": round(float(np.std(d["shared"])), 6),
            "delta_mean": round(float(np.mean(d["shared"]) - np.mean(d["indep"])), 6),
        }
    return out


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    code_path_hash = _sha256_file(os.path.abspath(__file__))
    prereg_sha256 = hashlib.sha256(
        json.dumps(PREREG, sort_keys=True).encode()).hexdigest()
    secret = _secret_scan(os.path.abspath(__file__))

    all_rows, by_regime = [], {r: [] for r in PREREG["regimes"]}
    for regime in PREREG["regimes"]:
        for seed in PREREG["seeds"]:
            rows = run_regime(regime, seed)
            by_regime[regime].extend(rows)
            all_rows.extend(rows)

    # trace.csv
    trace_path = os.path.join(out_dir, "trace.csv")
    with open(trace_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)

    verdict, detail = compute_verdict(by_regime)
    replay_verdict, replay_detail = replay_from_trace(trace_path)

    # qualitative co-change: both models move all channels under do(L=v) vs do(L=v')
    g = _rng(123456)
    Bq = make_world(0, shared=True)
    Lr, yr, _ = gen_samples(Bq, PREREG["n_ample"], 1, PREREG["noise_sd"])
    Wq = fit_independent([Lr, Lr, Lr], [yr[:, 0], yr[:, 1], yr[:, 2]],
                         PREREG["ridge_lambda_grid"], 0)
    v1 = g.standard_normal((1, PREREG["d_L"]))
    v2 = g.standard_normal((1, PREREG["d_L"]))
    indep_delta = (predict_independent(Wq, v1) - predict_independent(Wq, v2))[0]
    co_change = {
        "independent_model_intervention_delta_per_channel": [round(float(x), 6) for x in indep_delta],
        "all_three_channels_change": bool(np.all(np.abs(indep_delta) > 1e-6)),
        "note": "independent heads (no shared latent) reproduce 'intervene -> all channels change'",
    }

    result = {
        "task_id": PREREG["task_id"],
        "run_id": "local_gg_cobind_id_001a",
        "preregistration": PREREG,
        "prereg_sha256": prereg_sha256,
        "code_path_hash": code_path_hash,
        "secret_scan": {"run_path": os.path.abspath(__file__), **secret},
        "verdict": verdict,
        "verdict_detail": detail,
        "qualitative_co_change": co_change,
        "claim_ceiling": PREREG["claim_ceiling"],
        "what_this_does_not_prove": PREREG["what_this_does_not_prove"],
        "artifacts": ["result.json", "trace.csv", "baseline_comparison.json",
                      "ablation_report.json", "positive_control_report.json",
                      "replay_report.json", "claim_ceiling.txt"],
    }
    if not secret["clean"]:
        result["verdict"] = "BLOCK_secret_present"

    with open(os.path.join(out_dir, "result.json"), "w") as f:
        json.dump(result, f, indent=2)

    baseline_comparison = {
        "baseline": "independent_per_channel_ridge",
        "candidate_analog": "shared_rank1_score_model",
        "access_parity": "identical X(=L), held-out, lambda grid; only model class differs (logged)",
        "metric": "held-out signal R2 vs noise-free channel signal",
        "per_regime": {r: _agg(by_regime[r]) for r in PREREG["regimes"]},
    }
    with open(os.path.join(out_dir, "baseline_comparison.json"), "w") as f:
        json.dump(baseline_comparison, f, indent=2)

    ablation_report = {
        "positive_control": {
            "purpose": "sensitivity: shared MUST beat independent on poor channels",
            "win_seeds": detail["positive_control_win_seeds"],
            "passed": detail["positive_control_win_seeds"][0] >= PREREG["consistency_min"],
        },
        "negative_control": {
            "purpose": "specificity: shared MUST NOT beat independent without a shared latent",
            "win_seeds": detail["negative_control_win_seeds"],
            "passed": detail["negative_control_win_seeds"][0] < PREREG["consistency_min"],
        },
        "regime_ablation": {
            "balanced_ample_independent_reproduces_seeds": detail["balanced_independent_reproduces_seeds"],
            "imbalanced_shared_win_seeds": detail["imbalanced_win_seeds"],
        },
    }
    with open(os.path.join(out_dir, "ablation_report.json"), "w") as f:
        json.dump(ablation_report, f, indent=2)

    with open(os.path.join(out_dir, "positive_control_report.json"), "w") as f:
        json.dump({
            "positive_control": ablation_report["positive_control"],
            "negative_control": ablation_report["negative_control"],
        }, f, indent=2)

    replay_report = {
        "replay_verdict": replay_verdict,
        "result_verdict": verdict,
        "match": replay_verdict == verdict,
        "replay_detail": replay_detail,
        "method": "recompute verdict from trace.csv rows only; no hidden state, no future info",
    }
    with open(os.path.join(out_dir, "replay_report.json"), "w") as f:
        json.dump(replay_report, f, indent=2)

    with open(os.path.join(out_dir, "claim_ceiling.txt"), "w") as f:
        f.write(PREREG["claim_ceiling"] + "\n")

    if verdict in ("check_underpowered_invalid", "check_invalid_false_transfer",
                   "BLOCK_secret_present"):
        with open(os.path.join(out_dir, "failure_manifest.json"), "w") as f:
            json.dump({"verdict": verdict, "detail": detail}, f, indent=2)

    print(json.dumps({
        "verdict": verdict,
        "replay_match": replay_report["match"],
        "detail": detail,
        "co_change_all_three": co_change["all_three_channels_change"],
        "prereg_sha256": prereg_sha256[:12],
        "code_path_hash": code_path_hash[:12],
        "secret_clean": secret["clean"],
    }, indent=2))
    return result


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "artifacts/GG-COBIND-ID-001A"
    main(out)
