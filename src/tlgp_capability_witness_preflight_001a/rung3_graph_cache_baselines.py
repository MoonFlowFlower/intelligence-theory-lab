"""Equal-access graph-cache-family challenger for the rung3 identifiability probe."""
from __future__ import annotations

from typing import Any

import numpy as np

from src.tlgp_001a.metrics import balanced_accuracy, mean_episode_score
from src.tlgp_001a.world import Episode
from src.tlgp_001b_r2 import lower_reference as LR
from src.tlgp_001b_r2 import preregistration as P

GRAPH_CACHE_NAME = "graph_cache"
DEFAULT_VALUE = 0


def _key(x: np.ndarray, a: int) -> tuple[tuple[int, ...], int]:
    return (tuple(int(v) for v in x), int(a))


def build_successor_map(ep: Episode) -> dict[tuple[tuple[int, ...], int], int]:
    """Build an input-cell -> effect cache from adapt examples only."""
    table: dict[tuple[tuple[int, ...], int], int] = {}
    for x, a, e in zip(ep.adapt_x, ep.adapt_a, ep.adapt_e):
        table[_key(x, int(a))] = int(e)
    return table


def successor_map(ep: Episode, default_value: int = DEFAULT_VALUE) -> np.ndarray:
    """Predict by exact cached cell hits; unseen cells use a fixed cache default.

    The backoff is intentionally structure-blind and is never read from query_e.
    """
    table = build_successor_map(ep)
    return np.array(
        [table.get(_key(x, int(a)), int(default_value)) for x, a in zip(ep.query_x, ep.query_a)],
        dtype=int,
    )


def transition_table(ep: Episode, default_value: int = DEFAULT_VALUE) -> np.ndarray:
    """Alias within the graph-cache family, not to an LR baseline."""
    return successor_map(ep, default_value=default_value)


def query_hit_mask(ep: Episode) -> list[bool]:
    table = build_successor_map(ep)
    return [_key(x, int(a)) in table for x, a in zip(ep.query_x, ep.query_a)]


def query_hit_fraction(ep: Episode) -> float:
    mask = query_hit_mask(ep)
    return float(sum(1 for v in mask if v) / len(mask)) if mask else 0.0


def predict_episode(ep: Episode) -> dict[str, list[int]]:
    return {GRAPH_CACHE_NAME: [int(v) for v in successor_map(ep)]}


def graph_cache_is_alias(ep: Episode) -> bool:
    pred = successor_map(ep)
    return bool(np.array_equal(pred, LR.lookup(ep)) or np.array_equal(pred, LR.count_table(ep)))


def alias_report(episodes: list[Episode]) -> dict[str, Any]:
    total = len(episodes)
    equal_lookup = 0
    equal_count = 0
    any_diff_lookup = False
    any_diff_count = False
    hit_fractions: list[float] = []
    for ep in episodes:
        pred = successor_map(ep)
        same_lookup = bool(np.array_equal(pred, LR.lookup(ep)))
        same_count = bool(np.array_equal(pred, LR.count_table(ep)))
        equal_lookup += int(same_lookup)
        equal_count += int(same_count)
        any_diff_lookup = any_diff_lookup or not same_lookup
        any_diff_count = any_diff_count or not same_count
        hit_fractions.append(query_hit_fraction(ep))
    return {
        "graph_cache_name": GRAPH_CACHE_NAME,
        "default_value": DEFAULT_VALUE,
        "episodes": total,
        "equal_lookup_episodes": equal_lookup,
        "equal_count_table_episodes": equal_count,
        "all_equal_lookup": bool(total > 0 and equal_lookup == total),
        "all_equal_count_table": bool(total > 0 and equal_count == total),
        "implementation_alias": bool(total > 0 and (equal_lookup == total or equal_count == total)),
        "has_non_alias_witness": bool(any_diff_lookup and any_diff_count),
        "query_hit_fraction_mean": mean_episode_score(hit_fractions),
        "backoff_source": "fixed DEFAULT_VALUE independent of query_e",
    }


def evaluate(episodes: list[Episode], seed: int | None = None) -> tuple[dict[str, float], list[dict[str, list[int]]]]:
    del seed
    scores: list[float] = []
    records: list[dict[str, list[int]]] = []
    for ep in episodes:
        pred = successor_map(ep)
        records.append({GRAPH_CACHE_NAME: [int(v) for v in pred]})
        scores.append(balanced_accuracy(ep.query_e, pred, n_classes=P.K))
    return {GRAPH_CACHE_NAME: mean_episode_score(scores)}, records
