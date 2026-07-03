"""S3a degenerate prefix-only battery members."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time
from typing import Any, Mapping, Sequence

from .base import (
    PrefixEvent,
    Prediction,
    distribution_from_counts,
    event_from_mapping,
    load_design,
    one_hot,
    prediction_for_all_actions,
    response_alphabet_size,
    uniform,
)


IMPLEMENTED_MEMBERS = [
    "predict_all",
    "predict_none",
    "majority",
    "global_prior",
    "discounted_LS_lambda_0.95",
    "running_average_preference_regressor",
]


class PredictAllPredictor:
    name = "predict_all"

    def __init__(self, alphabet_size: int):
        self.alphabet_size = int(alphabet_size)

    @classmethod
    def from_design(cls, design: Mapping[str, Any]) -> "PredictAllPredictor":
        return cls(response_alphabet_size(design))

    def observe(self, event: PrefixEvent | Mapping[str, Any]) -> None:
        event_from_mapping(event)

    def predict(self, counterfactual_actions: Sequence[str]) -> Prediction:
        return prediction_for_all_actions(counterfactual_actions, one_hot(self.alphabet_size, self.alphabet_size - 1))


class PredictNonePredictor:
    name = "predict_none"

    def __init__(self, alphabet_size: int):
        self.alphabet_size = int(alphabet_size)

    @classmethod
    def from_design(cls, design: Mapping[str, Any]) -> "PredictNonePredictor":
        return cls(response_alphabet_size(design))

    def observe(self, event: PrefixEvent | Mapping[str, Any]) -> None:
        event_from_mapping(event)

    def predict(self, counterfactual_actions: Sequence[str]) -> Prediction:
        return prediction_for_all_actions(counterfactual_actions, one_hot(self.alphabet_size, 0))


class MajorityPredictor:
    name = "majority"

    def __init__(self, alphabet_size: int):
        self.alphabet_size = int(alphabet_size)
        self.counts = [0.0] * self.alphabet_size

    @classmethod
    def from_design(cls, design: Mapping[str, Any]) -> "MajorityPredictor":
        return cls(response_alphabet_size(design))

    def observe(self, event: PrefixEvent | Mapping[str, Any]) -> None:
        parsed = event_from_mapping(event)
        self.counts[int(parsed.observation["symbol"])] += 1.0

    def predict(self, counterfactual_actions: Sequence[str]) -> Prediction:
        symbol = max(range(self.alphabet_size), key=lambda index: (self.counts[index], -index))
        return prediction_for_all_actions(counterfactual_actions, one_hot(self.alphabet_size, symbol))


class GlobalPriorPredictor:
    name = "global_prior"

    def __init__(self, alphabet_size: int):
        self.alphabet_size = int(alphabet_size)
        self.counts = [0.0] * self.alphabet_size

    @classmethod
    def from_design(cls, design: Mapping[str, Any]) -> "GlobalPriorPredictor":
        return cls(response_alphabet_size(design))

    def observe(self, event: PrefixEvent | Mapping[str, Any]) -> None:
        parsed = event_from_mapping(event)
        self.counts[int(parsed.observation["symbol"])] += 1.0

    def predict(self, counterfactual_actions: Sequence[str]) -> Prediction:
        distribution = distribution_from_counts(self.counts, empty="uniform")
        return prediction_for_all_actions(counterfactual_actions, distribution)


def degenerate_conventions(design: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    alphabet_size = response_alphabet_size(design)
    return {
        "predict_all": {
            "type": "one_hot",
            "symbol": alphabet_size - 1,
            "description": f"emits a point mass on response symbol {alphabet_size - 1} for every counterfactual action",
        },
        "predict_none": {
            "type": "one_hot",
            "symbol": 0,
            "description": "emits a point mass on response symbol 0 for every counterfactual action",
        },
        "majority": {
            "type": "prefix_modal_symbol_one_hot",
            "empty_prefix_fallback_symbol": 0,
            "tie_break": "lowest response symbol index",
            "description": "emits a point mass on the modal observed prefix symbol; empty prefix falls back to symbol 0",
        },
        "global_prior": {
            "type": "prefix_empirical_symbol_distribution",
            "empty_prefix_fallback": "uniform over frozen response alphabet",
            "description": "emits the empirical response-symbol frequencies from the observed prefix for every counterfactual action",
        },
    }


def write_battery_manifest(frozen_design_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    run_started_at = _utc_timestamp()
    start = time.perf_counter()
    design = load_design(frozen_design_path)
    frozen_members = set(design["battery_membership"]["members"])
    missing = [name for name in IMPLEMENTED_MEMBERS if name not in frozen_members]
    if missing:
        raise ValueError(f"implemented S3a member missing from frozen battery_membership: {missing}")
    manifest = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S3a",
        "artifact": "s3a_battery_manifest",
        "implemented_members": list(IMPLEMENTED_MEMBERS),
        "prediction_format": {
            "prediction_target": design["evaluation"]["prediction_target"],
            "response_alphabet_size": response_alphabet_size(design),
            "counterfactual_action_set_per_query": list(design["evaluation"]["counterfactual_action_set_per_query"]),
            "format": "mapping from counterfactual action name to a full probability distribution over the frozen response alphabet",
        },
        "degenerate_conventions": degenerate_conventions(design),
        "prefix_only_contract": "inputs are past actions, observations, session boundaries, and step indices only; no future observations or simulator internals",
        "not_in_s3a": ["gap scoring", "headroom numbers", "should-win certificates"],
        "producer_function": "src.fsp_pum_env.battery.degenerates.write_battery_manifest",
        "code_path_hash": _battery_code_hash(),
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "wall_clock_seconds": time.perf_counter() - start,
        "claim_ceiling": "S3a battery member interface and manifest only; no baseline-power or gap claim",
    }
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def _battery_code_hash() -> str:
    h = hashlib.sha256()
    for name in ("base.py", "degenerates.py", "ls_regressors.py", "__init__.py"):
        path = Path(__file__).with_name(name)
        h.update(name.encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
