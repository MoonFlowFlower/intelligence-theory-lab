"""Callable lower-reference baselines and Rung-1 scanner for R2."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

import numpy as np

from src.tlgp_001a.metrics import balanced_accuracy, mean_episode_score
from src.tlgp_001a.world import Episode
from . import preregistration as P
from . import splits as S
from .world import ideal_predictions

LOWER_REFERENCE = ["lookup", "count_table", "predict_all", "majority", "no_adaptation"]


def _episode_majority(ep: Episode) -> int:
    vals, counts = np.unique(ep.adapt_e, return_counts=True)
    return int(vals[int(np.argmax(counts))])


def predict_all(ep: Episode) -> np.ndarray:
    return np.full(ep.query_x.shape[0], _episode_majority(ep), dtype=int)


def majority(ep: Episode) -> np.ndarray:
    return np.full(ep.query_x.shape[0], _episode_majority(ep), dtype=int)


def lookup(ep: Episode) -> np.ndarray:
    table: dict[tuple[tuple[int, ...], int], int] = {}
    for x, a, e in zip(ep.adapt_x, ep.adapt_a, ep.adapt_e):
        table[(tuple(int(v) for v in x), int(a))] = int(e)
    fallback = _episode_majority(ep)
    return np.array([
        table.get((tuple(int(v) for v in x), int(a)), fallback)
        for x, a in zip(ep.query_x, ep.query_a)
    ], dtype=int)


def count_table(ep: Episode) -> np.ndarray:
    cells: dict[tuple[tuple[int, ...], int], Counter] = defaultdict(Counter)
    for x, a, e in zip(ep.adapt_x, ep.adapt_a, ep.adapt_e):
        cells[(tuple(int(v) for v in x), int(a))][int(e)] += 1
    fallback = _episode_majority(ep)
    out = []
    for x, a in zip(ep.query_x, ep.query_a):
        key = (tuple(int(v) for v in x), int(a))
        out.append(cells[key].most_common(1)[0][0] if key in cells else fallback)
    return np.array(out, dtype=int)


def no_adaptation(ep: Episode, rng: np.random.Generator) -> np.ndarray:
    return rng.integers(0, P.K, size=ep.query_x.shape[0]).astype(int)


def predict_episode(ep: Episode, seed: int) -> dict[str, list[int]]:
    rng = np.random.default_rng(int(seed) + 8171 + int(ep.episode_id))
    preds = {
        "lookup": lookup(ep),
        "count_table": count_table(ep),
        "predict_all": predict_all(ep),
        "majority": majority(ep),
        "no_adaptation": no_adaptation(ep, rng),
    }
    return {name: [int(v) for v in values] for name, values in preds.items()}


def evaluate(episodes: list[Episode], seed: int) -> tuple[dict[str, float], list[dict[str, list[int]]]]:
    per: dict[str, list[float]] = {name: [] for name in LOWER_REFERENCE}
    records: list[dict[str, list[int]]] = []
    for ep in episodes:
        pred = predict_episode(ep, seed)
        records.append(pred)
        for name in LOWER_REFERENCE:
            per[name].append(balanced_accuracy(ep.query_e, np.array(pred[name], dtype=int)))
    return {name: mean_episode_score(scores) for name, scores in per.items()}, records


def direct_lookup_solve_rate(episodes: list[Episode]) -> float:
    correct = 0
    total = 0
    for ep in episodes:
        pred = lookup(ep)
        correct += int(np.sum(pred == ep.query_e))
        total += int(ep.query_e.size)
    return float(correct / total) if total else 0.0


def rung1_scanner(
    episodes: list[Episode],
    lower_means: dict[str, float] | None = None,
    no_context_meta_balacc: float | None = None,
) -> dict[str, Any]:
    if lower_means is None:
        lower_means, _ = evaluate(episodes, int(P.seeds()["BASELINE_FIT_SEED"]))
    ideal_seen1, _, _ = ideal_predictions(episodes)
    overlap = [S.query_adapt_overlap_fraction(ep) for ep in episodes]
    no_context = P.FLOOR() if no_context_meta_balacc is None else float(no_context_meta_balacc)
    ceiling = ideal_seen1 - P.DELTA()
    cheap_scores = {
        "lookup": float(lower_means["lookup"]),
        "count_table": float(lower_means["count_table"]),
        "predict_all": float(lower_means["predict_all"]),
        "majority": float(lower_means["majority"]),
        "no_context_meta": no_context,
    }
    return {
        "query_adapt_cell_overlap_fraction_mean": mean_episode_score(overlap),
        "query_adapt_cell_overlap_fraction_per_episode": [float(v) for v in overlap],
        "direct_lookup_solve_rate_rung1": direct_lookup_solve_rate(episodes),
        "rung1_balacc": cheap_scores,
        "ideal_seen1": float(ideal_seen1),
        "cheap_baseline_saturation_threshold": float(ceiling),
        "cheap_baseline_saturation": any(v >= ceiling for v in cheap_scores.values()),
    }

