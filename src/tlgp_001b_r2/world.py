"""R2 world helpers around the frozen TLGP-001A mod-5 world."""
from __future__ import annotations

from typing import Iterable

import numpy as np

from src.tlgp_001a.ideal_observer import predict_episode as ideal_predict_episode
from src.tlgp_001a.metrics import balanced_accuracy, mean_episode_score
from src.tlgp_001a.world import Episode, Rule, enumerate_rules, features_xa, make_shuffle_dataset
from . import preregistration as P


def sample_x(rng: np.random.Generator, values: Iterable[int], n: int | None = None) -> np.ndarray:
    count = P.N_ADAPT if n is None else int(n)
    return rng.choice(np.array(tuple(values), dtype=int), size=(count, P.D), replace=True).astype(int)


def sample_a(rng: np.random.Generator, n: int) -> np.ndarray:
    return rng.integers(0, P.ACTION_CARD, size=int(n)).astype(int)


def make_episode_for_rule(
    episode_id: int,
    rule_id: int,
    rng: np.random.Generator,
    adapt_values: Iterable[int],
    query_values: Iterable[int],
    n_adapt: int | None = None,
    n_query: int | None = None,
) -> Episode:
    rules = enumerate_rules()
    rule = rules[int(rule_id)]
    na = P.N_ADAPT if n_adapt is None else int(n_adapt)
    nq = P.N_QUERY if n_query is None else int(n_query)
    adapt_x = sample_x(rng, tuple(adapt_values), na)
    adapt_a = sample_a(rng, na)
    adapt_e = np.array([rule.effect(tuple(int(v) for v in x), int(a)) for x, a in zip(adapt_x, adapt_a)], dtype=int)
    query_x = sample_x(rng, tuple(query_values), nq)
    query_a = sample_a(rng, nq)
    query_e = np.array([rule.effect(tuple(int(v) for v in x), int(a)) for x, a in zip(query_x, query_a)], dtype=int)
    return Episode(int(episode_id), int(rule_id), rule, adapt_x, adapt_a, adapt_e, query_x, query_a, query_e)


def ideal_predictions(episodes: list[Episode]) -> tuple[float, list[list[int]], list[float]]:
    preds: list[list[int]] = []
    scores: list[float] = []
    for ep in episodes:
        pred, _ = ideal_predict_episode(ep)
        preds.append([int(v) for v in pred])
        scores.append(balanced_accuracy(ep.query_e, pred))
    return mean_episode_score(scores), preds, scores


def query_truth_rows(episodes: list[Episode]) -> list[list[int]]:
    return [[int(v) for v in ep.query_e] for ep in episodes]

