"""TLGP-001A orchestrator: prereg -> probe -> eval -> shuffle ablation -> leakage controls
-> computed fail-able verdict -> artifacts -> replay.

Run:  python3 -m src.tlgp_001a.harness            (official, frozen N_EPISODES)
      python3 -m src.tlgp_001a.harness --smoke 20 (fast non-official smoke)

NO git commit/push/tag/anchor. Writes only under artifacts/TLGP-001A/ (or TLGP_ARTIFACT_DIR).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

from . import preregistration as P
from .baselines import _fit_predict, _lookup, _no_adaptation, _predict_all, single_step_decoder
from .ideal_observer import predict_episode
from .leakage import positive_control_report
from .metrics import balanced_accuracy, headroom, margin_from_trivials, mean_episode_score
from .world import Episode, features_xa, make_dataset, make_shuffle_dataset

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = Path(os.environ.get("TLGP_ARTIFACT_DIR", str(REPO_ROOT / "artifacts" / "TLGP-001A")))

AGENTS = ["ideal", "predict_all", "no_adaptation", "lookup", "knn1", "logistic", "mlp", "random_forest"]
FAIR = ["predict_all", "no_adaptation", "lookup", "knn1", "logistic", "mlp", "random_forest"]
TRIVIAL_KEYS = ["predict_all", "no_adaptation", "lookup", "knn1"]


def _episode_scores(ep: Episode, seed: int):
    """ONE pass over an episode (deterministic, position-independent so chunking is exact).
    no_adaptation is seeded per episode_id; fitted models use the frozen fit seed."""
    rng = np.random.default_rng(P.MASTER_SEED + 90000 + ep.episode_id)
    Xtr, ytr = features_xa(ep.adapt_x, ep.adapt_a), ep.adapt_e
    Xte, yte = features_xa(ep.query_x, ep.query_a), ep.query_e
    ideal_pred, nc = predict_episode(ep)
    scores = {
        "ideal": balanced_accuracy(yte, ideal_pred),
        "predict_all": balanced_accuracy(yte, _predict_all(ep)),
        "no_adaptation": balanced_accuracy(yte, _no_adaptation(ep, rng)),
        "lookup": balanced_accuracy(yte, _lookup(ep)),
        "knn1": balanced_accuracy(yte, _fit_predict(KNeighborsClassifier(n_neighbors=1), Xtr, ytr, Xte)),
        "logistic": balanced_accuracy(yte, _fit_predict(LogisticRegression(max_iter=2000), Xtr, ytr, Xte)),
        "mlp": balanced_accuracy(yte, _fit_predict(
            MLPClassifier(hidden_layer_sizes=(64, 64), max_iter=600, random_state=seed), Xtr, ytr, Xte)),
        "random_forest": balanced_accuracy(yte, _fit_predict(
            RandomForestClassifier(n_estimators=80, random_state=seed), Xtr, ytr, Xte)),
    }
    return scores, [int(v) for v in ideal_pred], nc


def score_records(episodes: List[Episode], seed: int):
    """Per-agent per-episode score lists + ideal preds + n_consistent (chunk-friendly)."""
    per_agent: Dict[str, List[float]] = {a: [] for a in AGENTS}
    ideal_preds: List[List[int]] = []
    n_consistent: List[int] = []
    for ep in episodes:
        scores, preds, nc = _episode_scores(ep, seed)
        for a in AGENTS:
            per_agent[a].append(scores[a])
        ideal_preds.append(preds)
        n_consistent.append(nc)
    return per_agent, ideal_preds, n_consistent


def aggregate(per_agent: Dict[str, List[float]], ideal_preds, n_consistent) -> Dict:
    agg = {a: mean_episode_score(per_agent[a]) for a in AGENTS}
    fair = {a: agg[a] for a in FAIR}
    return {
        "agg": agg,
        "fair_baselines": fair,
        "ideal_mean": agg["ideal"],
        "max_fair_baseline": max(fair.values()),
        "headroom": headroom(agg["ideal"], fair),
        "per_agent": per_agent,
        "ideal_preds": ideal_preds,
        "n_consistent": n_consistent,
    }


def evaluate(episodes: List[Episode], seed: int) -> Dict:
    """Single source of truth (single-call path)."""
    return aggregate(*score_records(episodes, seed))


# --- verdict (computed from booleans; fail-able both ways) ---------------------
def compute_verdict(m: Dict, replay_exact: bool) -> Dict:
    floor, delta = P.FLOOR, P.DELTA
    checks = {
        "headroom_ok": bool(m["real"]["headroom"] > delta),
        "baselines_fail": bool(m["real"]["max_fair_baseline"] <= floor + delta),
        "single_step_floor": bool(m["single_step"]["clean"] <= floor + delta),
        "ideal_high": bool(m["real"]["ideal_mean"] >= floor + 2 * delta),
        "shuffle_collapse": bool(m["shuffle"]["headroom"] <= delta),
        "replay_exact": bool(replay_exact),
    }
    validity = {
        "leak_detector_valid": bool(m["leakage"]["detector_valid"]),
        "decoder_capable": bool(m["single_step"]["leaked_rule"] >= floor + 2 * delta),
    }
    if not (validity["leak_detector_valid"] and validity["decoder_capable"]):
        verdict = P.VERDICT_INVALID
    elif all(checks.values()):
        verdict = P.VERDICT_PASS
    else:
        verdict = P.VERDICT_WEAK
    return {"verdict": verdict, "checks": checks, "validity": validity}


# --- trace + replay ------------------------------------------------------------
def write_trace(path: Path, episodes: List[Episode], real: Dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        for k, ep in enumerate(episodes):
            row = {
                "episode_id": ep.episode_id,
                "rule_id": ep.rule_id,
                "rule_w": list(ep.rule.w),
                "rule_c": ep.rule.c,
                "n_consistent": real["n_consistent"][k],
                "adapt_x": ep.adapt_x.tolist(),
                "adapt_a": ep.adapt_a.tolist(),
                "adapt_e": ep.adapt_e.tolist(),
                "query_x": ep.query_x.tolist(),
                "query_a": ep.query_a.tolist(),
                "query_e": ep.query_e.tolist(),
                "ideal_pred": real["ideal_preds"][k],
                "ideal_balacc": real["per_agent"]["ideal"][k],
                "agent_balacc": {a: real["per_agent"][a][k] for a in AGENTS},
            }
            f.write(json.dumps(row) + "\n")


def replay_from_trace(path: Path, m: Dict) -> Dict:
    """Reconstruct each agent's mean from trace; recompute ideal score from recorded preds vs
    ground truth (no hidden future info); verify aggregates match result + recompute verdict."""
    ideal_recomputed: List[float] = []
    per_agent_replay: Dict[str, List[float]] = {a: [] for a in AGENTS}
    rows = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            rows += 1
            qe, pred = np.array(r["query_e"]), np.array(r["ideal_pred"])
            ideal_recomputed.append(balanced_accuracy(qe, pred))
            for a in AGENTS:
                per_agent_replay[a].append(r["agent_balacc"][a])

    ideal_from_preds = mean_episode_score(ideal_recomputed)
    agg_replay = {a: mean_episode_score(per_agent_replay[a]) for a in AGENTS}
    fair_replay = {a: agg_replay[a] for a in FAIR}
    headroom_replay = headroom(agg_replay["ideal"], fair_replay)

    ideal_recompute_match = bool(np.allclose(ideal_recomputed, m["real"]["per_agent"]["ideal"], atol=1e-12)
                                 and abs(ideal_from_preds - m["real"]["ideal_mean"]) < 1e-12)
    agg_match = all(abs(agg_replay[a] - m["real"]["agg"][a]) < 1e-12 for a in AGENTS)
    headroom_match = abs(headroom_replay - m["real"]["headroom"]) < 1e-12
    return {
        "rows": rows,
        "ideal_mean_replay_from_preds": ideal_from_preds,
        "ideal_mean_result": m["real"]["ideal_mean"],
        "ideal_recompute_match": ideal_recompute_match,
        "aggregate_match": bool(agg_match),
        "headroom_replay": headroom_replay,
        "headroom_match": bool(headroom_match),
        "replay_exact": bool(ideal_recompute_match and agg_match and headroom_match),
    }


# --- main ----------------------------------------------------------------------
def run(n_episodes=None) -> Dict:
    official = n_episodes is None
    n_eps = P.N_EPISODES if official else n_episodes
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    real_eps = make_dataset(n_eps, seed=P.SEED_REAL)
    shuffle_eps = make_shuffle_dataset(n_eps, seed=P.SEED_SHUFFLE)

    real = evaluate(real_eps, seed=P.SEED_BASELINE_FIT)
    shuffle = evaluate(shuffle_eps, seed=P.SEED_BASELINE_FIT)
    ss = single_step_decoder(real_eps, seed=P.SEED_BASELINE_FIT)
    leak = positive_control_report(make_dataset(n_eps, seed=P.SEED_LEAK))

    trivial_scores = {k: real["fair_baselines"][k] for k in TRIVIAL_KEYS}
    trivial_scores["single_step_clean"] = ss["clean"]

    m = {"real": real, "shuffle": shuffle, "single_step": ss, "leakage": leak,
         "margin_reported": margin_from_trivials(trivial_scores)}

    trace_path = ARTIFACT_DIR / "trace.jsonl"
    write_trace(trace_path, real_eps, real)
    replay = replay_from_trace(trace_path, m)
    v = compute_verdict(m, replay_exact=replay["replay_exact"])

    _write_artifacts(m, v, replay, trivial_scores, official, n_eps)
    return {"verdict": v["verdict"], "checks": v["checks"], "validity": v["validity"],
            "official": official, "n_episodes": n_eps,
            "ideal": real["ideal_mean"], "max_fair_baseline": real["max_fair_baseline"],
            "headroom": real["headroom"], "shuffle_headroom": shuffle["headroom"],
            "single_step": ss}


def _write_artifacts(m, v, replay, trivial_scores, official, n_eps) -> None:
    floor, delta = P.FLOOR, P.DELTA
    real, shuffle = m["real"], m["shuffle"]
    _dump(ARTIFACT_DIR / "result.json", {
        "task_id": "TLGP-001A",
        "official_run": official,
        "n_episodes": n_eps,
        "preregistration": P.prereg_dict(),
        "preregistration_sha256": P.prereg_sha256(),
        "floor": floor, "delta": delta,
        "ideal_observer_heldout": real["ideal_mean"],
        "max_fair_baseline_heldout": real["max_fair_baseline"],
        "headroom_heldout": real["headroom"],
        "margin_reported": m["margin_reported"],
        "single_step_decoder": m["single_step"],
        "shuffle_headroom": shuffle["headroom"],
        "verdict": v["verdict"],
        "checks": v["checks"],
        "validity": v["validity"],
        "claim_ceiling": P.CLAIM_CEILING,
    })
    _dump(ARTIFACT_DIR / "baseline_comparison.json", {
        "floor": floor, "delta": delta,
        "ideal_observer": real["ideal_mean"],
        "fair_baselines_real": real["fair_baselines"],
        "max_fair_baseline": real["max_fair_baseline"],
        "headroom_real": real["headroom"],
        "fair_baselines_shuffle": shuffle["fair_baselines"],
        "ideal_observer_shuffle": shuffle["ideal_mean"],
        "headroom_shuffle": shuffle["headroom"],
        "note": "all fitted baselines use numeric features (no one-hot starvation); held-out = unseen property values (extrapolation)",
    })
    _dump(ARTIFACT_DIR / "triviality_probe_report.json", {
        "floor": floor, "delta": delta,
        "trivial_scores_heldout": trivial_scores,
        "max_trivial": max(trivial_scores.values()),
        "any_trivial_closes_headroom": bool(max(trivial_scores.values()) > floor + delta),
        "margin_reported": m["margin_reported"],
    })
    _dump(ARTIFACT_DIR / "ablation_report.json", {
        "ablation": "shuffle-structure (random table replaces linear-mod rule)",
        "ideal_real": real["ideal_mean"], "headroom_real": real["headroom"],
        "ideal_shuffle": shuffle["ideal_mean"], "headroom_shuffle": shuffle["headroom"],
        "collapses": bool(shuffle["headroom"] <= delta),
        "interpretation": "headroom must come from compositional structure; on a structureless world the linear-family ideal observer finds no consistent hypothesis and collapses to floor",
    })
    _dump(ARTIFACT_DIR / "positive_control_report.json", m["leakage"])
    _dump(ARTIFACT_DIR / "replay_report.json", replay)

    _dump(ARTIFACT_DIR / "failure_manifest.json", {
        "verdict": v["verdict"],
        "failed_checks": [k for k, ok in v["checks"].items() if not ok],
        "validity": v["validity"],
        "invalid": v["verdict"] == P.VERDICT_INVALID,
        "stop_triggered": v["verdict"] != P.VERDICT_PASS,
        "note": ("STOP triggered; banked negative/invalid bounded to this world"
                 if v["verdict"] != P.VERDICT_PASS else
                 "no STOP; verdict=PASS; manifest written for completeness (no failures)"),
    })
    (ARTIFACT_DIR / "claim_ceiling.txt").write_text(P.CLAIM_CEILING + "\n", encoding="utf-8")


def _dump(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", type=int, default=0, help="fast non-official smoke with N episodes")
    args = ap.parse_args(argv)
    print(json.dumps(run(n_episodes=args.smoke if args.smoke > 0 else None), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
