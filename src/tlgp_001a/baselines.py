"""Fair non-inference baselines + single-step decoder for TLGP-001A.

All "learned" baselines are REAL fitted sklearn models (.fit on the legal numeric inputs,
including the discriminating fields) -- never deterministic stubs rigged to score 0 (K4).
They receive numeric features [x_0..x_{D-1}, a] (NO one-hot starvation), so each CAN in
principle learn a map and attempt extrapolation; they fail on held-out unseen values only
because they lack the mod-K family prior, not because their input was crippled.

The single-step decoder is the K1 control (optimal 1-observation Bayesian decoder).
"""
from __future__ import annotations

from typing import Dict, List

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

from . import preregistration as P
from .metrics import balanced_accuracy, mean_episode_score
from .world import Episode, features_xa


# --- per-episode baselines -----------------------------------------------------
def _fit_predict(model, Xtr, ytr, Xte) -> np.ndarray:
    """Fit a sklearn classifier; if only one class present, predict it constant."""
    uniq = np.unique(ytr)
    if uniq.size < 2:
        return np.full(Xte.shape[0], int(uniq[0]), dtype=int)
    model.fit(Xtr, ytr)
    return model.predict(Xte).astype(int)


def _predict_all(ep: Episode) -> np.ndarray:
    vals, counts = np.unique(ep.adapt_e, return_counts=True)
    return np.full(ep.query_x.shape[0], int(vals[np.argmax(counts)]), dtype=int)


def _no_adaptation(ep: Episode, rng: np.random.Generator) -> np.ndarray:
    # ignores adaptation entirely: random uniform guess
    return rng.integers(0, P.K, size=ep.query_x.shape[0]).astype(int)


def _lookup(ep: Episode) -> np.ndarray:
    table: Dict[tuple, int] = {}
    for x, a, e in zip(ep.adapt_x, ep.adapt_a, ep.adapt_e):
        table[(tuple(int(v) for v in x), int(a))] = int(e)
    vals, counts = np.unique(ep.adapt_e, return_counts=True)
    fallback = int(vals[np.argmax(counts)])
    out = []
    for x, a in zip(ep.query_x, ep.query_a):
        out.append(table.get((tuple(int(v) for v in x), int(a)), fallback))
    return np.array(out, dtype=int)


def run_fair_baselines(episodes: List[Episode], seed: int) -> Dict[str, float]:
    """Mean (over episodes) per-episode balanced accuracy for every fair baseline."""
    rng = np.random.default_rng(seed)
    acc: Dict[str, List[float]] = {
        "predict_all": [], "no_adaptation": [], "lookup": [],
        "knn1": [], "logistic": [], "mlp": [], "random_forest": [],
    }
    for ep in episodes:
        Xtr = features_xa(ep.adapt_x, ep.adapt_a)
        ytr = ep.adapt_e
        Xte = features_xa(ep.query_x, ep.query_a)
        yte = ep.query_e

        acc["predict_all"].append(balanced_accuracy(yte, _predict_all(ep)))
        acc["no_adaptation"].append(balanced_accuracy(yte, _no_adaptation(ep, rng)))
        acc["lookup"].append(balanced_accuracy(yte, _lookup(ep)))
        acc["knn1"].append(balanced_accuracy(yte, _fit_predict(
            KNeighborsClassifier(n_neighbors=1), Xtr, ytr, Xte)))
        acc["logistic"].append(balanced_accuracy(yte, _fit_predict(
            LogisticRegression(max_iter=2000), Xtr, ytr, Xte)))
        acc["mlp"].append(balanced_accuracy(yte, _fit_predict(
            MLPClassifier(hidden_layer_sizes=(64, 64), max_iter=600,
                          random_state=seed), Xtr, ytr, Xte)))
        acc["random_forest"].append(balanced_accuracy(yte, _fit_predict(
            RandomForestClassifier(n_estimators=80, random_state=seed), Xtr, ytr, Xte)))

    return {k: mean_episode_score(v) for k, v in acc.items()}


# --- single-step decoder (K1) --------------------------------------------------
def single_step_decoder(episodes: List[Episode], seed: int) -> Dict[str, float]:
    """OPTIMAL 1-observation Bayesian decoder (the strongest possible single-step decoder
    within the rule family).

    clean         : ideal-observer machinery given ONLY ONE adaptation observation. One
                    linear constraint mod K leaves K^D consistent rules, so a held-out query
                    is undetermined -> posterior-predictive ~ uniform -> ~floor. This is the
                    K1 proof that the latent is NOT single-step decodable: if even the optimal
                    1-obs decoder is at floor, no obs-only model can do better.
    leaked_rule   : value-level decode positive control. The single observation is taken to
                    REVEAL the latent (consistent set forced to the true rule), so the SAME
                    prediction+metric pipeline returns the exact effect -> ~1.0. If this did
                    NOT lift, the decoder/metric would be a stub (caught by 'decoder_capable').
    The `seed` selects which single adaptation observation is used (deterministic).
    """
    from .ideal_observer import predict_core
    rng = np.random.default_rng(seed)
    clean_scores, leaked_scores = [], []
    for ep in episodes:
        j = int(rng.integers(0, ep.adapt_x.shape[0]))   # which single observation
        ax, aa, ae = ep.adapt_x[j:j + 1], ep.adapt_a[j:j + 1], ep.adapt_e[j:j + 1]
        clean_pred, _ = predict_core(ax, aa, ae, ep.query_x, ep.query_a)
        leaked_pred, _ = predict_core(ax, aa, ae, ep.query_x, ep.query_a,
                                      forced_rule_idx=ep.rule_id)
        clean_scores.append(balanced_accuracy(ep.query_e, clean_pred))
        leaked_scores.append(balanced_accuracy(ep.query_e, leaked_pred))
    return {"clean": mean_episode_score(clean_scores),
            "leaked_rule": mean_episode_score(leaked_scores)}
