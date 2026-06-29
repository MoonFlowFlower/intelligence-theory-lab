"""Frozen R2 rule/rung split construction."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.tlgp_001a.world import Episode, enumerate_rules, make_shuffle_dataset
from . import preregistration as P
from .world import make_episode_for_rule

RUNG0 = "rung0_learnability_floor"
RUNG1 = "rung1_seen_rule_capability"
RUNG2 = "rung2_seen_rule_value_extrapolation"
RUNG3 = "rung3_real_unseen_rule_unseen_value"

RUNG_ALIASES = {
    "rung0": RUNG0,
    "rung1": RUNG1,
    "rung2": RUNG2,
    "rung3": RUNG3,
    RUNG0: RUNG0,
    RUNG1: RUNG1,
    RUNG2: RUNG2,
    RUNG3: RUNG3,
}

EPISODE_ID_BASE = {
    (RUNG0, "train"): 10_000_000,
    (RUNG0, "heldout"): 11_000_000,
    (RUNG1, "train"): 20_000_000,
    (RUNG1, "val"): 21_000_000,
    (RUNG1, "test"): 22_000_000,
    (RUNG2, "test"): 30_000_000,
    (RUNG3, "train"): 40_000_000,
    (RUNG3, "val"): 41_000_000,
    (RUNG3, "test"): 42_000_000,
    ("shuffle", "train"): 50_000_000,
    ("shuffle", "val"): 51_000_000,
    ("shuffle", "test"): 52_000_000,
}


@dataclass(frozen=True)
class RungSpec:
    rung: str
    split: str
    rule_pool: str
    adapt_values: tuple[int, ...]
    query_values: tuple[int, ...]
    seed_key: str
    count_key: str | None


def _normalize_rung(rung: str) -> str:
    if rung not in RUNG_ALIASES:
        raise ValueError(f"unknown R2 rung: {rung}")
    return RUNG_ALIASES[rung]


def rule_split() -> tuple[np.ndarray, np.ndarray]:
    sc = P.split_construction()["rule_split"]
    n_train = int(sc["train_rules"])
    n_test = int(sc["test_rules"])
    total = len(enumerate_rules())
    if n_train + n_test != total:
        raise RuntimeError(f"bad R2 rule split size {n_train}+{n_test}!={total}")
    perm = np.random.default_rng(int(P.seeds()["RULE_SPLIT_SEED"])).permutation(total)
    train_idx = np.sort(perm[:n_train])
    test_idx = np.sort(perm[n_train:])
    if set(train_idx.tolist()) & set(test_idx.tolist()):
        raise RuntimeError("TRAIN_RULES and TEST_RULES overlap")
    return train_idx, test_idx


def r0_rule_indices() -> np.ndarray:
    train_idx, _ = rule_split()
    rng = np.random.default_rng(int(P.seeds()["R0_RULES_SELECT_SEED"]))
    count = int(P.cfg()["R0_RULES"]["count"])
    return np.sort(rng.choice(train_idx, size=count, replace=False).astype(int))


def _count_for(rung: str, split: str) -> tuple[str | None, int | None]:
    rc = P.rungs()[rung]
    key_by_split = {
        "train": "n_train_episodes",
        "val": "n_val_episodes",
        "test": "n_test_episodes",
        "heldout": "n_heldout_episodes",
    }
    key = key_by_split.get(split)
    if key and key in rc:
        return key, int(rc[key])
    return None, None


def rung_spec(rung: str, split: str) -> RungSpec:
    rung = _normalize_rung(rung)
    split = str(split)
    train_values = tuple(int(v) for v in P.TRAIN_VALUES)
    heldout_values = tuple(int(v) for v in P.HELDOUT_VALUES)
    full_values = tuple(sorted(set(train_values) | set(heldout_values)))
    if rung == RUNG0:
        seed_key = "RUNG0_TRAIN_EPISODES_SEED" if split == "train" else "RUNG0_HELDOUT_EPISODES_SEED"
        key, _ = _count_for(rung, "train" if split == "train" else "heldout")
        return RungSpec(rung, split, "R0_RULES", full_values, full_values, seed_key, key)
    if rung == RUNG1:
        seed_key = {
            "train": "RUNG1_TRAIN_EPISODES_SEED",
            "val": "RUNG1_VAL_EPISODES_SEED",
            "test": "RUNG1_TEST_EPISODES_SEED",
        }[split]
        key, _ = _count_for(rung, split)
        return RungSpec(rung, split, "TRAIN_RULES", train_values, train_values, seed_key, key)
    if rung == RUNG2:
        if split != "test":
            raise ValueError("rung2 is diagnostic test-only in R2")
        key, _ = _count_for(rung, split)
        return RungSpec(rung, split, "TRAIN_RULES", train_values, heldout_values, "RUNG2_TEST_EPISODES_SEED", key)
    if rung == RUNG3:
        seed_key = {
            "train": "RUNG3_TRAIN_EPISODES_SEED",
            "val": "RUNG3_VAL_EPISODES_SEED",
            "test": "RUNG3_TEST_EPISODES_SEED",
        }[split]
        rule_pool = "TEST_RULES" if split == "test" else "TRAIN_RULES"
        q_values = heldout_values if split == "test" else train_values
        key, _ = _count_for(rung, split)
        return RungSpec(rung, split, rule_pool, train_values, q_values, seed_key, key)
    raise AssertionError(rung)


def _rule_pool(spec: RungSpec) -> np.ndarray:
    train_idx, test_idx = rule_split()
    if spec.rule_pool == "TRAIN_RULES":
        return train_idx
    if spec.rule_pool == "TEST_RULES":
        return test_idx
    if spec.rule_pool == "R0_RULES":
        return r0_rule_indices()
    raise ValueError(spec.rule_pool)


def make_episodes(rung: str, split: str, n_episodes: int | None = None) -> list[Episode]:
    spec = rung_spec(rung, split)
    _, default_n = _count_for(spec.rung, "heldout" if spec.split == "heldout" else spec.split)
    n = int(default_n if n_episodes is None else n_episodes)
    pool = _rule_pool(spec)
    rng = np.random.default_rng(int(P.seeds()[spec.seed_key]))
    base = EPISODE_ID_BASE[(spec.rung, spec.split)]
    episodes: list[Episode] = []
    for i in range(n):
        rule_id = int(pool[rng.integers(0, len(pool))])
        episodes.append(make_episode_for_rule(
            base + i,
            rule_id,
            rng,
            spec.adapt_values,
            spec.query_values,
        ))
    return episodes


def make_shuffle_episodes(split: str, n_episodes: int) -> list[Episode]:
    seed_offset = {"train": 0, "val": 101, "test": 202}[split]
    episodes = make_shuffle_dataset(int(n_episodes), int(P.seeds()["SHUFFLE_SEED"]) + seed_offset)
    base = EPISODE_ID_BASE[("shuffle", split)]
    for i, ep in enumerate(episodes):
        ep.episode_id = base + i
    return episodes


def query_adapt_overlap_fraction(ep: Episode) -> float:
    adapt_cells = {(tuple(int(v) for v in x), int(a)) for x, a in zip(ep.adapt_x, ep.adapt_a)}
    if len(ep.query_a) == 0:
        return 0.0
    hits = sum(1 for x, a in zip(ep.query_x, ep.query_a) if (tuple(int(v) for v in x), int(a)) in adapt_cells)
    return float(hits / len(ep.query_a))


def split_assertions(datasets: dict[str, list[Episode]]) -> dict[str, object]:
    train_idx, test_idx = rule_split()
    train_set = set(int(v) for v in train_idx.tolist())
    test_set = set(int(v) for v in test_idx.tolist())
    r0_set = set(int(v) for v in r0_rule_indices().tolist())
    episode_sets = {name: {int(ep.episode_id) for ep in eps} for name, eps in datasets.items()}
    all_ids: set[int] = set()
    disjoint = True
    for ids in episode_sets.values():
        if all_ids & ids:
            disjoint = False
        all_ids |= ids
    rule_sets = {name: {int(ep.rule_id) for ep in eps} for name, eps in datasets.items()}
    return {
        "train_rules_count": len(train_set),
        "test_rules_count": len(test_set),
        "r0_rules_count": len(r0_set),
        "train_test_rule_overlap_empty": train_set.isdisjoint(test_set),
        "r0_rules_subset_of_train_rules": r0_set.issubset(train_set),
        "episode_ids_disjoint_across_supplied_sets": disjoint,
        "rung1_rules_subset_of_train": rule_sets.get("rung1_test", set()).issubset(train_set),
        "rung2_rules_subset_of_train": rule_sets.get("rung2_test", set()).issubset(train_set),
        "rung3_test_rules_subset_of_test": rule_sets.get("rung3_test", set()).issubset(test_set),
        "rung3_train_rules_subset_of_train": rule_sets.get("rung3_train", set()).issubset(train_set),
    }

