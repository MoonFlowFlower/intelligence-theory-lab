"""Rule split + regime-conditioned episode generation for TLGP-001B.

Frozen split (from prereg.json, verified by preregistration.py):
  * rule_split: permute the 625 canonical-order linear-mod rules by RULE_SPLIT_SEED;
    TRAIN_RULES = first 500, TEST_RULES = last 125, disjoint.
  * episodes: train/val draw rules from TRAIN_RULES only; test draws from TEST_RULES only;
    episode_id ranges are disjoint across splits.
  * value regime (the ONLY permitted condition difference -- never compute/architecture):
      REAL_withheld : train/val adapt in {0,1,2} AND query in {0,1,2}  (meta never sees 3/4);
                      test = 001A protocol (adapt {0,1,2}, query {3,4}).
      CAPACITY_CONTROL: identical EXCEPT train/val QUERIES may also draw {3,4}
                      (adapt still {0,1,2}); test IDENTICAL to REAL.

Reuses (read-only import) the frozen 001A world: Rule, Episode, enumerate_rules,
features_xa, make_shuffle_dataset. Nothing here reads rule_id or query_e into any model
input; rule_id/query_e are recorded for scoring/replay/leak-audit only.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from src.tlgp_001a.world import Episode, Rule, enumerate_rules, make_shuffle_dataset
from . import preregistration as P

REAL = "REAL_withheld"
CONTROL = "CAPACITY_CONTROL"

# Disjoint episode-id namespaces per split (assertion-checked downstream).
EPISODE_ID_BASE = {"train": 0, "val": 1_000_000, "test": 2_000_000}


# --- frozen rule split ---------------------------------------------------------
def rule_split() -> Tuple[np.ndarray, np.ndarray]:
    """Return (train_rule_idx, test_rule_idx): a frozen disjoint permutation split of the
    625 canonical rules (500 train / 125 test) by RULE_SPLIT_SEED."""
    sc = P.split_construction()["rule_split"]
    n_train = int(sc["train_rules"])      # 500
    n_test = int(sc["test_rules"])        # 125
    n_total = len(enumerate_rules())      # 625
    assert n_train + n_test == n_total, f"rule split {n_train}+{n_test} != {n_total}"
    seed = int(P.seeds()["RULE_SPLIT_SEED"])
    perm = np.random.default_rng(seed).permutation(n_total)
    train_idx = np.sort(perm[:n_train])
    test_idx = np.sort(perm[n_train:])
    assert set(train_idx.tolist()).isdisjoint(test_idx.tolist()), "TRAIN_RULES ∩ TEST_RULES != empty"
    return train_idx, test_idx


# --- sampling helpers (mirror 001A world semantics; no private 001A names) -----
def _sample_x(rng: np.random.Generator, values: Tuple[int, ...], n: int) -> np.ndarray:
    return rng.choice(np.array(values), size=(n, P.D), replace=True).astype(int)


def _sample_a(rng: np.random.Generator, n: int) -> np.ndarray:
    return rng.integers(0, P.ACTION_CARD, size=n).astype(int)


def _make_episode(episode_id: int, rule_idx: int, rule: Rule, rng: np.random.Generator,
                  adapt_values: Tuple[int, ...], query_values: Tuple[int, ...]) -> Episode:
    adapt_x = _sample_x(rng, adapt_values, P.N_ADAPT)
    adapt_a = _sample_a(rng, P.N_ADAPT)
    adapt_e = np.array([rule.effect(tuple(int(v) for v in x), int(a))
                        for x, a in zip(adapt_x, adapt_a)], dtype=int)
    query_x = _sample_x(rng, query_values, P.N_QUERY)
    query_a = _sample_a(rng, P.N_QUERY)
    query_e = np.array([rule.effect(tuple(int(v) for v in x), int(a))
                        for x, a in zip(query_x, query_a)], dtype=int)
    return Episode(episode_id, rule_idx, rule, adapt_x, adapt_a, adapt_e,
                   query_x, query_a, query_e)


def _query_values(split: str, regime: str) -> Tuple[int, ...]:
    """The ONLY permitted condition difference: train/val query value-regime."""
    if split == "test":
        return P.HELDOUT_VALUES                      # test identical across regimes
    if regime == REAL:
        return P.TRAIN_VALUES                        # meta never sees 3/4 in REAL
    if regime == CONTROL:
        return tuple(sorted(set(P.TRAIN_VALUES) | set(P.HELDOUT_VALUES)))  # {0,1,2,3,4}
    raise ValueError(f"unknown regime {regime}")


def make_split(split: str, regime: str, n_episodes: int) -> List[Episode]:
    """Generate one split (train/val/test) under a regime, drawing rules from the frozen
    rule partition (train/val -> TRAIN_RULES, test -> TEST_RULES)."""
    assert split in ("train", "val", "test"), split
    train_idx, test_idx = rule_split()
    rule_pool = test_idx if split == "test" else train_idx
    rules = enumerate_rules()
    seed_key = {"train": "TRAIN_EPISODES_SEED", "val": "VAL_EPISODES_SEED",
                "test": "TEST_EPISODES_SEED"}[split]
    rng = np.random.default_rng(int(P.seeds()[seed_key]))
    adapt_values = P.TRAIN_VALUES                       # adapt always {0,1,2}
    query_values = _query_values(split, regime)
    base = EPISODE_ID_BASE[split]
    out: List[Episode] = []
    for i in range(n_episodes):
        ridx = int(rule_pool[rng.integers(0, len(rule_pool))])
        out.append(_make_episode(base + i, ridx, rules[ridx], rng, adapt_values, query_values))
    return out


def make_real_control_test() -> List[Episode]:
    """Test set (identical across REAL and CONTROL by construction)."""
    return make_split("test", REAL, P.training_budget()["n_test_episodes"])


def make_shuffle_split(split: str, n_episodes: int) -> List[Episode]:
    """Shuffle-structure world for the shuffle ablation (reuse 001A non-compositional world).
    Distinct per-split seed derived from SHUFFLE_SEED keeps episode sets disjoint."""
    offset = {"train": 0, "val": 101, "test": 202}[split]
    eps = make_shuffle_dataset(n_episodes, seed=int(P.seeds()["SHUFFLE_SEED"]) + offset)
    base = EPISODE_ID_BASE[split]
    for i, ep in enumerate(eps):       # renumber ids into the split's disjoint namespace
        ep.episode_id = base + i
    return eps


# --- split integrity assertions (logged into artifacts) ------------------------
def split_assertions(train: List[Episode], val: List[Episode], test: List[Episode]) -> Dict:
    train_idx, test_idx = rule_split()
    train_rule_ids = {ep.rule_id for ep in train} | {ep.rule_id for ep in val}
    test_rule_ids = {ep.rule_id for ep in test}
    train_eids = {ep.episode_id for ep in train}
    val_eids = {ep.episode_id for ep in val}
    test_eids = {ep.episode_id for ep in test}
    return {
        "train_rules_count": int(len(train_idx)),
        "test_rules_count": int(len(test_idx)),
        "rule_partition_disjoint": bool(set(train_idx.tolist()).isdisjoint(test_idx.tolist())),
        "train_episode_rules_subset_of_TRAIN_RULES": bool(train_rule_ids.issubset(set(train_idx.tolist()))),
        "test_episode_rules_subset_of_TEST_RULES": bool(test_rule_ids.issubset(set(test_idx.tolist()))),
        "train_test_rule_overlap_empty": bool(train_rule_ids.isdisjoint(test_rule_ids)),
        "episode_ids_disjoint": bool(train_eids.isdisjoint(val_eids) and train_eids.isdisjoint(test_eids)
                                     and val_eids.isdisjoint(test_eids)),
    }
