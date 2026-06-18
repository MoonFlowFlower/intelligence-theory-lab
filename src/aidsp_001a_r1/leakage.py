"""Leakage scanner + planted positive controls. (Canonical == src/aidsp_001a_r1/leakage.py)

Binding test is a NAME-INDEPENDENT statistical MI test vs the per-episode hidden
food location (demonstrated fail-able by a RENAMED full-food leak). Name BLACKLIST
(no whitelist) catches explicitly-labeled forbidden channels.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from . import prereg as P
from .environment import AIDSPEnv, N_ACTIONS


def entropy_bits(counts: np.ndarray) -> float:
    p = counts / counts.sum()
    nz = p[p > 0]
    return float(-(nz * np.log2(nz)).sum())


def mutual_info_bits(x: List[int], y: List[int]) -> float:
    x = np.asarray(x); y = np.asarray(y)
    xs = np.unique(x); ys = np.unique(y)
    n = len(x)
    if n == 0:
        return 0.0
    joint = np.zeros((len(xs), len(ys)))
    xi = {v: i for i, v in enumerate(xs)}
    yi = {v: i for i, v in enumerate(ys)}
    for a, b in zip(x, y):
        joint[xi[a], yi[b]] += 1
    joint /= n
    px = joint.sum(1, keepdims=True)
    py = joint.sum(0, keepdims=True)
    mi = 0.0
    for i in range(len(xs)):
        for j in range(len(ys)):
            if joint[i, j] > 0:
                mi += joint[i, j] * np.log2(joint[i, j] / (px[i, 0] * py[0, j]))
    return float(mi)


def H_food_bits() -> float:
    return float(np.log2(len(P.normal_cells())))


def collect_channel_samples(leak_food_oracle=False, leak_special_label=False,
                            seeds=None, rename_oracle_to: str = None
                            ) -> Tuple[Dict[str, List[int]], List[int]]:
    if seeds is None:
        seeds = P.SEED_FAMILY_A
    channels: Dict[str, List[int]] = {}
    foods: List[int] = []
    for seed in seeds:
        env = AIDSPEnv(leak_food_oracle=leak_food_oracle, leak_special_label=leak_special_label)
        obs = env.reset(seed=seed)
        rng = np.random.default_rng(seed ^ 0x1EAC)
        done = False
        while not done:
            a = int(rng.integers(N_ACTIONS))
            obs, info, done = env.step(a)
            for k, v in obs.channels().items():
                key = rename_oracle_to if (k == "food_loc_oracle" and rename_oracle_to) else k
                channels.setdefault(key, []).append(int(v))
            foods.append(info["food"])
    return channels, foods


def scan(channels: Dict[str, List[int]], foods: List[int]) -> Dict:
    Hf = H_food_bits()
    thresh = P.LEAK_MI_FRAC * Hf
    per_channel = {}
    any_flag = False
    for name, vals in channels.items():
        mi = mutual_info_bits(vals, foods)
        name_flag = any(sub in name.lower() for sub in P.FORBIDDEN_CHANNEL_NAME_SUBSTR)
        stat_flag = mi >= thresh
        flagged = bool(name_flag or stat_flag)
        any_flag = any_flag or flagged
        per_channel[name] = {"mi_food_bits": round(mi, 4), "mi_threshold_bits": round(thresh, 4),
                             "statistical_flag": bool(stat_flag), "name_flag": bool(name_flag),
                             "flagged": flagged}
    return {"H_food_bits": round(Hf, 4), "per_channel": per_channel, "blocked": bool(any_flag)}


def run_positive_controls(seeds=None) -> Dict:
    if seeds is None:
        seeds = P.SEED_FAMILY_A
    report = {}

    ch, fo = collect_channel_samples(seeds=seeds)
    clean = scan(ch, fo)
    report["clean_interface"] = clean
    clean_ok = (not clean["blocked"])

    ch, fo = collect_channel_samples(leak_food_oracle=True, seeds=seeds)
    leak_named = scan(ch, fo)
    caught_named = leak_named["per_channel"].get("food_loc_oracle", {}).get("flagged", False)
    report["leak_food_oracle_named"] = leak_named

    ch, fo = collect_channel_samples(leak_food_oracle=True, seeds=seeds, rename_oracle_to="aux_sensor_7")
    leak_renamed = scan(ch, fo)
    aux = leak_renamed["per_channel"].get("aux_sensor_7", {})
    caught_renamed_stat = bool(aux.get("statistical_flag", False))
    caught_renamed_not_by_name = (not aux.get("name_flag", True))
    report["leak_food_oracle_renamed"] = leak_renamed

    ch, fo = collect_channel_samples(leak_special_label=True, seeds=seeds)
    leak_special = scan(ch, fo)
    caught_special = leak_special["per_channel"].get("special_label", {}).get("flagged", False)
    report["leak_special_label"] = leak_special

    scanner_failable = bool(clean_ok and caught_named and caught_renamed_stat
                            and caught_renamed_not_by_name and caught_special)
    report["summary"] = {
        "clean_interface_passes": clean_ok,
        "caught_food_oracle_named": bool(caught_named),
        "caught_food_oracle_renamed_statistically": caught_renamed_stat,
        "renamed_leak_not_caught_by_name_only": caught_renamed_not_by_name,
        "caught_special_label": bool(caught_special),
        "scanner_failable": scanner_failable,
    }
    return report
