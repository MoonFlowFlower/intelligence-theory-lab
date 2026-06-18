"""Metrics. ALL computed on the INDEPENDENT estimator / ground truth, never on any
agent's internal belief (anti-tautology)."""
from __future__ import annotations

from typing import List, Tuple

import numpy as np

from . import prereg as P
from .environment import FoodPosteriorEstimator
from .runtypes import EpisodeRun


def entropy_trajectory(observations: List[Tuple[int, int, int]]) -> List[float]:
    """H_0..H_T from a fresh independent estimator fed the observation stream."""
    est = FoodPosteriorEstimator()
    H = [est.entropy_bits()]
    for (cue, pos, at_food) in observations:
        est.update(cue, pos, at_food)
        H.append(est.entropy_bits())
    return H


def compute_M1(observations: List[Tuple[int, int, int]]) -> float:
    """M1 = sum_{t=1..T} (H_{t-1}-H_t)/cost_t ; cost_t = cumulative cost = t.

    Rewards EARLY (cheap) entropy reduction. Brute coverage reduces H mostly at
    high cumulative cost -> low M1 (the card's stated intent)."""
    H = entropy_trajectory(observations)
    m1 = 0.0
    for t in range(1, len(H)):
        cost_t = t * P.PER_ACTION_COST
        m1 += (H[t - 1] - H[t]) / cost_t
    return float(m1)


def tvd(p: List[float], q: List[float]) -> float:
    p = np.asarray(p, float); q = np.asarray(q, float)
    return float(0.5 * np.abs(p - q).sum())


def compute_M2_episode(present: EpisodeRun, ablated: EpisodeRun) -> float:
    """Mean TVD between per-step action distributions (cue-present vs cue-ablated).
    Cue-ignoring policy -> 0 exactly; cue-user -> > 0."""
    pa = present.action_dists()
    ab = ablated.action_dists()
    n = min(len(pa), len(ab))
    if n == 0:
        return 0.0
    return float(np.mean([tvd(pa[t], ab[t]) for t in range(n)]))


def dwell_fractions(run: EpisodeRun) -> Tuple[float, float]:
    steps = run.steps
    if not steps:
        return 0.0, 0.0
    dr = np.mean([s.in_dark_room for s in steps])
    tv = np.mean([s.in_noisy_tv for s in steps])
    return float(dr), float(tv)


def aggregate_M1(runs: List[EpisodeRun]) -> float:
    return float(np.mean([compute_M1(r.observations) for r in runs]))


def aggregate_dwell(runs: List[EpisodeRun]) -> Tuple[float, float]:
    drs, tvs = zip(*[dwell_fractions(r) for r in runs])
    return float(np.mean(drs)), float(np.mean(tvs))
