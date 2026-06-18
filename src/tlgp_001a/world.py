"""Minimal compositional world for TLGP-001A.

Real world : effect = (sum_i w_i * x_i + c * a) mod K, rule (w, c) resampled per episode.
Shuffle    : effect = T[(x, a)] for a per-episode random table T (non-compositional).

Adaptation interactions use property values in TRAIN_VALUES only. Held-out queries use
property values in HELDOUT_VALUES only (never seen during adaptation) -> extrapolation.

Nothing here reads a candidate's output. Ground-truth rule is recorded in the trace for
scoring/replay but is NEVER passed to any agent (except the planted-leak controls in
leakage.py, which is the point of those controls).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Dict, List, Tuple

import numpy as np

from . import preregistration as P

Vec = Tuple[int, ...]


@dataclass(frozen=True)
class Rule:
    w: Vec          # length D, each in 0..K-1
    c: int          # action coefficient, 0..K-1

    def effect(self, x: Vec, a: int) -> int:
        return (int(np.dot(self.w, x)) + self.c * a) % P.K


@dataclass
class Episode:
    episode_id: int
    rule_id: int                       # index into enumerate_rules(); ground truth (hidden)
    rule: Rule                         # ground truth (hidden from agents)
    adapt_x: np.ndarray                # (n_adapt, D) ints
    adapt_a: np.ndarray                # (n_adapt,)   ints
    adapt_e: np.ndarray                # (n_adapt,)   ints  (observed effects)
    query_x: np.ndarray                # (n_query, D) ints
    query_a: np.ndarray                # (n_query,)   ints
    query_e: np.ndarray                # (n_query,)   ints  (ground-truth held-out effects)
    is_shuffle: bool = False
    table: Dict[Tuple[Vec, int], int] = field(default_factory=dict)  # shuffle only


# --- rule family enumeration ---------------------------------------------------
_RULES: List[Rule] | None = None


def enumerate_rules() -> List[Rule]:
    """All K^(D+1) linear-mod rules, in a fixed canonical order."""
    global _RULES
    if _RULES is None:
        rules: List[Rule] = []
        for combo in product(range(P.K), repeat=P.D + 1):
            rules.append(Rule(w=tuple(combo[:P.D]), c=combo[P.D]))
        _RULES = rules
    return _RULES


def rule_index(rule: Rule) -> int:
    base = P.K
    idx = 0
    for v in rule.w:
        idx = idx * base + v
    idx = idx * base + rule.c
    return idx


# --- sampling helpers ----------------------------------------------------------
def _sample_x(rng: np.random.Generator, values: Tuple[int, ...], n: int) -> np.ndarray:
    return rng.choice(np.array(values), size=(n, P.D), replace=True).astype(int)


def _sample_a(rng: np.random.Generator, n: int) -> np.ndarray:
    return rng.integers(0, P.ACTION_CARD, size=n).astype(int)


# --- real world ----------------------------------------------------------------
def make_episode(episode_id: int, rng: np.random.Generator) -> Episode:
    rules = enumerate_rules()
    ridx = int(rng.integers(0, len(rules)))
    rule = rules[ridx]

    adapt_x = _sample_x(rng, P.TRAIN_VALUES, P.N_ADAPT)
    adapt_a = _sample_a(rng, P.N_ADAPT)
    adapt_e = np.array([rule.effect(tuple(x), int(a)) for x, a in zip(adapt_x, adapt_a)], dtype=int)

    query_x = _sample_x(rng, P.HELDOUT_VALUES, P.N_QUERY)
    query_a = _sample_a(rng, P.N_QUERY)
    query_e = np.array([rule.effect(tuple(x), int(a)) for x, a in zip(query_x, query_a)], dtype=int)

    return Episode(episode_id, ridx, rule, adapt_x, adapt_a, adapt_e,
                   query_x, query_a, query_e)


def make_dataset(n_episodes: int, seed: int) -> List[Episode]:
    rng = np.random.default_rng(seed)
    return [make_episode(i, rng) for i in range(n_episodes)]


# --- shuffle-structure ablation world -----------------------------------------
def make_shuffle_episode(episode_id: int, rng: np.random.Generator) -> Episode:
    """Non-compositional: each (x, a) cell gets an independent uniform effect.

    Held-out cells are independent of adaptation cells, so NO observer (including the
    linear-family ideal observer) can predict them above chance -> headroom must collapse.
    A 'rule_id' is still drawn (for the leak detector to have a latent), but effects do
    NOT follow it; the table is the true generator.
    """
    rules = enumerate_rules()
    ridx = int(rng.integers(0, len(rules)))
    table: Dict[Tuple[Vec, int], int] = {}

    def eff(x: Vec, a: int) -> int:
        key = (tuple(int(v) for v in x), int(a))
        if key not in table:
            table[key] = int(rng.integers(0, P.K))
        return table[key]

    adapt_x = _sample_x(rng, P.TRAIN_VALUES, P.N_ADAPT)
    adapt_a = _sample_a(rng, P.N_ADAPT)
    adapt_e = np.array([eff(tuple(x), int(a)) for x, a in zip(adapt_x, adapt_a)], dtype=int)

    query_x = _sample_x(rng, P.HELDOUT_VALUES, P.N_QUERY)
    query_a = _sample_a(rng, P.N_QUERY)
    query_e = np.array([eff(tuple(x), int(a)) for x, a in zip(query_x, query_a)], dtype=int)

    return Episode(episode_id, ridx, rules[ridx], adapt_x, adapt_a, adapt_e,
                   query_x, query_a, query_e, is_shuffle=True, table=dict(table))


def make_shuffle_dataset(n_episodes: int, seed: int) -> List[Episode]:
    rng = np.random.default_rng(seed)
    return [make_shuffle_episode(i, rng) for i in range(n_episodes)]


# --- feature helpers for fitted baselines (numeric; NO one-hot starvation) -----
def features_xa(x: np.ndarray, a: np.ndarray) -> np.ndarray:
    """Numeric design matrix [x_0..x_{D-1}, a] so a baseline CAN, in principle,
    learn a linear/flexible map and attempt extrapolation. (K4 fairness.)"""
    a = np.asarray(a).reshape(-1, 1)
    return np.concatenate([np.asarray(x), a], axis=1).astype(float)
