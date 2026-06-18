"""Degeneracy-safe metrics for TLGP-001A (K3).

Primary metric is BALANCED accuracy (per-class recall averaged) on held-out queries, so a
constant / predict_all prediction scores at the chance floor 1/K rather than winning.
"""
from __future__ import annotations

from typing import Dict, List

import numpy as np

from . import preregistration as P


def balanced_accuracy(y_true: np.ndarray, y_pred: np.ndarray, n_classes: int = P.K) -> float:
    """Mean over present true-classes of per-class recall. Constant prediction -> ~1/n."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    recalls: List[float] = []
    for c in range(n_classes):
        mask = y_true == c
        if mask.sum() == 0:
            continue
        recalls.append(float((y_pred[mask] == c).mean()))
    return float(np.mean(recalls)) if recalls else 0.0


def mean_episode_score(per_episode: List[float]) -> float:
    return float(np.mean(per_episode)) if per_episode else 0.0


def headroom(ideal: float, fair_baselines: Dict[str, float]) -> float:
    """ideal - max(fair non-inference baselines). K2-correct separation form."""
    return float(ideal - max(fair_baselines.values())) if fair_baselines else float(ideal)


def margin_from_trivials(trivial_scores: Dict[str, float]) -> float:
    """Reported card margin = max(trivial baseline) + DELTA."""
    return float(max(trivial_scores.values()) + P.DELTA) if trivial_scores else float(P.FLOOR + P.DELTA)
