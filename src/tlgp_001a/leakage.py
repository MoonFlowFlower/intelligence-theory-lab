"""Statistical (MI-based) leakage detector + planted positive controls (K6).

A channel is flagged if it carries the latent rule OR the held-out answer:
    flag(channel) := MI(channel; rule_id)  >= MI_FRAC * H(rule_id)
                  OR MI(channel; answer)   >= MI_FRAC * H(answer)

Detection is purely statistical (mutual information over values), so a RENAMED leak channel
is caught regardless of its innocuous name. Clean channels (raw effects, query props) carry
neither target above threshold and must NOT be flagged. The controls below make the detector
FAIL-ABLE: if a planted leak is not caught, the verdict goes invalid.
"""
from __future__ import annotations

import math
from typing import Dict, List

import numpy as np
from sklearn.metrics import mutual_info_score

from . import preregistration as P
from .world import Episode

_LN2 = math.log(2.0)


def _bits(x):
    return x / _LN2


def entropy_bits(arr: np.ndarray) -> float:
    return _bits(mutual_info_score(arr, arr))


def mi_bits(a: np.ndarray, b: np.ndarray) -> float:
    return _bits(mutual_info_score(a, b))


def targets(episodes: List[Episode]) -> Dict[str, np.ndarray]:
    rule_id = np.array([ep.rule_id for ep in episodes], dtype=int)
    answer = np.array([int(ep.query_e[0]) for ep in episodes], dtype=int)  # canonical held-out answer
    return {"rule_id": rule_id, "answer": answer}


def clean_channels(episodes: List[Episode]) -> Dict[str, np.ndarray]:
    return {
        "adapt_eff_0": np.array([int(ep.adapt_e[0]) for ep in episodes], dtype=int),
        "adapt_eff_1": np.array([int(ep.adapt_e[1]) for ep in episodes], dtype=int),
        "adapt_eff_2": np.array([int(ep.adapt_e[2]) for ep in episodes], dtype=int),
        "query0_prop0": np.array([int(ep.query_x[0, 0]) for ep in episodes], dtype=int),
        "n_distinct_adapt_eff": np.array([len(np.unique(ep.adapt_e)) for ep in episodes], dtype=int),
    }


def planted_channels(episodes: List[Episode], tgt: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """Three planted leaks; the 2nd is a RENAMED copy of the rule-id leak."""
    return {
        "rule_id_channel": tgt["rule_id"].copy(),          # control (i): rule leak
        "telemetry_7": tgt["rule_id"].copy(),              # control (i) renamed: must still flag
        "calib_value": tgt["answer"].copy(),               # control (ii): held-out answer leak
    }


def detect(channels: Dict[str, np.ndarray], tgt: Dict[str, np.ndarray],
           mi_frac: float = P.MI_FRAC) -> Dict[str, dict]:
    h_rule = entropy_bits(tgt["rule_id"])
    h_ans = entropy_bits(tgt["answer"])
    thr_rule = mi_frac * h_rule
    thr_ans = mi_frac * h_ans
    report: Dict[str, dict] = {}
    for name, ch in channels.items():
        mi_r = mi_bits(ch, tgt["rule_id"])
        mi_a = mi_bits(ch, tgt["answer"])
        flagged = bool(mi_r >= thr_rule or mi_a >= thr_ans)
        report[name] = {
            "mi_rule_bits": round(mi_r, 4), "thr_rule_bits": round(thr_rule, 4),
            "mi_answer_bits": round(mi_a, 4), "thr_answer_bits": round(thr_ans, 4),
            "flagged": flagged,
        }
    return report


def positive_control_report(episodes: List[Episode]) -> dict:
    tgt = targets(episodes)
    clean = detect(clean_channels(episodes), tgt)
    planted = detect(planted_channels(episodes, tgt), tgt)

    clean_false_flags = [n for n, r in clean.items() if r["flagged"]]
    planted_missed = [n for n, r in planted.items() if not r["flagged"]]

    return {
        "H_rule_bits": round(entropy_bits(tgt["rule_id"]), 4),
        "H_answer_bits": round(entropy_bits(tgt["answer"]), 4),
        "clean_report": clean,
        "planted_report": planted,
        "clean_false_flags": clean_false_flags,
        "planted_missed": planted_missed,
        "all_planted_caught": len(planted_missed) == 0,
        "no_clean_false_flag": len(clean_false_flags) == 0,
        "renamed_leak_caught": bool(planted["telemetry_7"]["flagged"]),
        "detector_valid": len(planted_missed) == 0 and len(clean_false_flags) == 0,
    }
