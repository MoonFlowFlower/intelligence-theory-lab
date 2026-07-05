"""Lower-reference fair panel for TLGP-001B (per-episode, NO cross-episode amortization).

These are the prereg `panel.lower_reference` baselines + a `count_table` graph-cache witness.
They are RE-IMPLEMENTED here (001A's baselines.py is NOT in the read-only-import allowlist;
only world/ideal_observer/metrics/leakage are). Each is fit/applied PER TEST EPISODE on that
episode's adaptation data and predicts that episode's held-out queries -- exactly the
family-ignorant per-episode reference 001A used. They receive numeric features
[x_0..x_{D-1}, a] (NO one-hot starvation; K4 fairness) so each CAN attempt extrapolation and
fails on unseen held-out values only for lack of the mod-K family prior.

The graph-cache family (count_table here as the declared witness) is provably dominated by the
unseen-value split: held-out (x,a) cells never appear in adaptation, so any lookup/table model
falls back to its prior -> floor. Per prereg, this witness is coverage-by-construction, not
independent corroboration.

This panel is corroborating context. The 001B verdict keys on ideal-vs-META headroom, not on
these. Predictions are recorded so replay can recompute their scores without re-fitting.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

from src.tlgp_001a.metrics import balanced_accuracy, mean_episode_score
from src.tlgp_001a.world import Episode, features_xa
from . import preregistration as P

LOWER_REFERENCE = ["predict_all", "no_adaptation", "lookup", "knn1",
                   "logistic", "mlp", "random_forest", "count_table"]


def _fit_predict(model, Xtr, ytr, Xte) -> np.ndarray:
    uniq = np.unique(ytr)
    if uniq.size < 2:
        return np.full(Xte.shape[0], int(uniq[0]), dtype=int)
    model.fit(Xtr, ytr)
    return model.predict(Xte).astype(int)


def _predict_all(ep: Episode) -> np.ndarray:
    vals, counts = np.unique(ep.adapt_e, return_counts=True)
    return np.full(ep.query_x.shape[0], int(vals[np.argmax(counts)]), dtype=int)


def _no_adaptation(ep: Episode, rng: np.random.Generator) -> np.ndarray:
    return rng.integers(0, P.K, size=ep.query_x.shape[0]).astype(int)


def _lookup(ep: Episode) -> np.ndarray:
    table: Dict[tuple, int] = {}
    for x, a, e in zip(ep.adapt_x, ep.adapt_a, ep.adapt_e):
        table[(tuple(int(v) for v in x), int(a))] = int(e)
    vals, counts = np.unique(ep.adapt_e, return_counts=True)
    fallback = int(vals[np.argmax(counts)])
    return np.array([table.get((tuple(int(v) for v in x), int(a)), fallback)
                     for x, a in zip(ep.query_x, ep.query_a)], dtype=int)


def _count_table(ep: Episode) -> np.ndarray:
    """Graph-cache witness: most-frequent observed effect per (x,a) cell; held-out cells
    are unseen -> global most-frequent fallback (floor on the extrapolative split)."""
    from collections import Counter, defaultdict
    cells: Dict[tuple, Counter] = defaultdict(Counter)
    for x, a, e in zip(ep.adapt_x, ep.adapt_a, ep.adapt_e):
        cells[(tuple(int(v) for v in x), int(a))][int(e)] += 1
    vals, counts = np.unique(ep.adapt_e, return_counts=True)
    fallback = int(vals[np.argmax(counts)])
    out = []
    for x, a in zip(ep.query_x, ep.query_a):
        c = cells.get((tuple(int(v) for v in x), int(a)))
        out.append(c.most_common(1)[0][0] if c else fallback)
    return np.array(out, dtype=int)


def predict_episode(ep: Episode, fit_seed: int) -> Dict[str, List[int]]:
    """Per-episode predictions for every lower-reference baseline (recorded for replay)."""
    rng = np.random.default_rng(fit_seed + 90000 + int(ep.episode_id))
    Xtr, ytr = features_xa(ep.adapt_x, ep.adapt_a), ep.adapt_e
    Xte = features_xa(ep.query_x, ep.query_a)
    preds = {
        "predict_all": _predict_all(ep),
        "no_adaptation": _no_adaptation(ep, rng),
        "lookup": _lookup(ep),
        "count_table": _count_table(ep),
        "knn1": _fit_predict(KNeighborsClassifier(n_neighbors=1), Xtr, ytr, Xte),
        "logistic": _fit_predict(LogisticRegression(max_iter=2000), Xtr, ytr, Xte),
        "mlp": _fit_predict(MLPClassifier(hidden_layer_sizes=(64, 64), max_iter=600,
                                          random_state=fit_seed), Xtr, ytr, Xte),
        "random_forest": _fit_predict(RandomForestClassifier(n_estimators=80,
                                                             random_state=fit_seed), Xtr, ytr, Xte),
    }
    return {k: [int(v) for v in vp] for k, vp in preds.items()}


def evaluate(episodes: List[Episode], fit_seed: int) -> Tuple[Dict[str, float], List[Dict[str, List[int]]]]:
    """Return (mean per-episode balanced accuracy per baseline, recorded per-episode preds)."""
    per: Dict[str, List[float]] = {k: [] for k in LOWER_REFERENCE}
    recorded: List[Dict[str, List[int]]] = []
    for ep in episodes:
        preds = predict_episode(ep, fit_seed)
        recorded.append(preds)
        for k in LOWER_REFERENCE:
            per[k].append(balanced_accuracy(ep.query_e, np.array(preds[k])))
    return {k: mean_episode_score(v) for k, v in per.items()}, recorded
