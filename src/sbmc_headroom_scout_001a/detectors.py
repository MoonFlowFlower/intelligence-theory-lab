"""Detector definitions for the SBMC headroom scout.

Only ``ideal`` is allowed theta access.  Non-ideal detectors are written against
metadata-stripped item representations plus trusted-seed context.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
from sklearn.linear_model import LogisticRegression

from . import gen_model as GM

FORBIDDEN_AUDIT_KEYS = frozenset({"theta", "label", "label_binary", "audit", "provenance", "source", "user_id"})


class GuardViolation(RuntimeError):
    pass


class GuardedMapping(Mapping):
    """Read-only mapping that raises when a forbidden audit/provenance key is read."""

    def __init__(self, data: Mapping[str, Any], *, forbidden: set[str] | frozenset[str] = FORBIDDEN_AUDIT_KEYS):
        self._data = dict(data)
        self._forbidden = set(forbidden)

    def __getitem__(self, key: str) -> Any:
        if key in self._forbidden:
            raise GuardViolation(f"non-ideal detector attempted to read forbidden key: {key}")
        return guard_payload(self._data[key], forbidden=self._forbidden)

    def __iter__(self):
        return (key for key in self._data if key not in self._forbidden)

    def __len__(self) -> int:
        return len([key for key in self._data if key not in self._forbidden])

    def get(self, key: str, default: Any = None) -> Any:
        if key in self._forbidden:
            raise GuardViolation(f"non-ideal detector attempted to read forbidden key: {key}")
        if key not in self._data:
            return default
        return guard_payload(self._data[key], forbidden=self._forbidden)

    def __contains__(self, key: object) -> bool:
        if isinstance(key, str) and key in self._forbidden:
            raise GuardViolation(f"non-ideal detector attempted to probe forbidden key: {key}")
        return key in self._data


def guard_payload(data: Any, *, forbidden: set[str] | frozenset[str] = FORBIDDEN_AUDIT_KEYS) -> Any:
    if isinstance(data, Mapping):
        return GuardedMapping(data, forbidden=forbidden)
    if isinstance(data, list):
        return [guard_payload(v, forbidden=forbidden) for v in data]
    if isinstance(data, tuple):
        return tuple(guard_payload(v, forbidden=forbidden) for v in data)
    return data


def asserted_edge_and_values(item_repr: Mapping[str, Any]) -> tuple[tuple[int, int], int, int]:
    edge = GM.edge_key(item_repr["edge"])
    asserted = item_repr["asserted_tuple"]
    return edge, int(asserted[0][1]), int(asserted[1][1])


def ideal(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    """Upper-bound reference detector; theta access is explicit and audit-only."""

    _ = seed
    theta = user_context["theta"]
    edge, first_value, second_value = asserted_edge_and_values(item_repr)
    if int(theta[edge[0]]) != first_value:
        return 1
    return int(not GM.is_allowed(edge, first_value, second_value))


def fair_inference(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    """Estimate per-user pair consistency from trusted genuine items only."""

    _ = seed
    observed: dict[tuple[int, int], set[tuple[int, int]]] = defaultdict(set)
    for trusted in user_context["trusted_seed"]:
        edge, first_value, second_value = asserted_edge_and_values(trusted)
        observed[edge].add((first_value, second_value))
    edge, first_value, second_value = asserted_edge_and_values(item_repr)
    if edge not in observed:
        return 0
    return int((first_value, second_value) not in observed[edge])


def embedding_outlier(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    """Simple kNN/density floor over style-matched bag vectors."""

    _ = seed
    trusted = np.asarray([trusted_item["bow_vector"] for trusted_item in user_context["trusted_seed"]], dtype=float)
    x = np.asarray(item_repr["bow_vector"], dtype=float)
    if len(trusted) == 0:
        return 0
    distances = np.linalg.norm(trusted - x, axis=1)
    trusted_centroid = trusted.mean(axis=0)
    trusted_self = np.linalg.norm(trusted - trusted_centroid, axis=1)
    threshold = float(trusted_self.max(initial=0.0) + 1e-12)
    return int(float(distances.min(initial=0.0)) > threshold)


def frequency_marginal(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    """Flag values not observed in the user's trusted genuine corpus."""

    _ = seed
    counts: dict[int, Counter[int]] = defaultdict(Counter)
    for trusted in user_context["trusted_seed"]:
        for attr, value in trusted["asserted_tuple"]:
            counts[int(attr)][int(value)] += 1
    for attr, value in item_repr["asserted_tuple"]:
        attr_i = int(attr)
        value_i = int(value)
        if counts[attr_i] and counts[attr_i][value_i] == 0:
            return 1
    return 0


def predict_all(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    _ = item_repr, user_context, seed
    return 1


def predict_none(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    _ = item_repr, user_context, seed
    return 0


def majority(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    """Trusted seed is known genuine, so the legal no-test-label majority is genuine."""

    _ = item_repr, user_context, seed
    return 0


NON_IDEAL_DETECTORS: dict[str, Callable[[Mapping[str, Any], Mapping[str, Any], int], int]] = {
    "fair_inference": fair_inference,
    "embedding_outlier": embedding_outlier,
    "frequency_marginal": frequency_marginal,
    "predict_all": predict_all,
    "predict_none": predict_none,
    "majority": majority,
}

DETECTORS: dict[str, Callable[[Mapping[str, Any], Mapping[str, Any], int], int]] = {
    "ideal": ideal,
    **NON_IDEAL_DETECTORS,
}


def _rows_from_cases(cases: list[dict[str, Any]], *, canary: bool) -> tuple[np.ndarray, np.ndarray, list[str]]:
    rows: list[list[float]] = []
    labels: list[int] = []
    feature_names: list[str] | None = None
    for case in cases:
        theta = case["theta"]
        for item in case["test_set"]:
            item_repr = item["item_repr"]
            base = [float(x) for x in item_repr["bow_vector"]]
            names = list(item_repr["bow_feature_names"])
            if canary:
                edge = GM.edge_key(item_repr["edge"])
                asserted_second = int(item_repr["asserted_tuple"][1][1])
                theta_second = int(theta[edge[1]])
                pair_features = [0.0] * (GM.V * GM.V)
                pair_features[theta_second * GM.V + asserted_second] = 1.0
                base.extend(pair_features)
                names.extend([f"theta_canary_second_{t}_asserted_{a}" for t in range(GM.V) for a in range(GM.V)])
            rows.append(base)
            labels.append(int(item["audit"]["label_binary"]))
            if feature_names is None:
                feature_names = names
    if feature_names is None:
        feature_names = list(GM.VOCAB)
    return np.asarray(rows, dtype=float), np.asarray(labels, dtype=int), feature_names


def scan_feature_names_for_leakage(feature_names: list[str]) -> dict[str, Any]:
    patterns = ("theta", "label", "provenance", "source", "user_id")
    hits = [name for name in feature_names for pattern in patterns if pattern in name.lower()]
    return {
        "scanner_function": "scan_feature_names_for_leakage",
        "patterns": list(patterns),
        "hits": sorted(set(hits)),
        "fires": bool(hits),
    }


@dataclass(frozen=True)
class SurfaceDecoderReport:
    clean_accuracy: float
    canary_accuracy: float
    clean_scanner_fires: bool
    canary_scanner_fires: bool
    train_user_ids: list[int]
    eval_user_ids: list[int]
    train_eval_disjoint: bool
    producer_function: str = "run_surface_decoder_positive_control"
    metric: str = "plain_accuracy_for_leakage_positive_control_not_macro_f1"


def run_surface_decoder_positive_control(
    *,
    train_cases: list[dict[str, Any]],
    eval_cases: list[dict[str, Any]],
    seed: int,
) -> SurfaceDecoderReport:
    """Fit clean and theta-canary surface decoders for leakage failability.

    This is a STEP-A self-test/positive-control only.  It reports plain accuracy,
    not detector F1 and not the headroom gate.
    """

    train_user_ids = [int(case["user_id"]) for case in train_cases]
    eval_user_ids = [int(case["user_id"]) for case in eval_cases]
    disjoint = set(train_user_ids).isdisjoint(eval_user_ids)

    x_train, y_train, clean_names = _rows_from_cases(train_cases, canary=False)
    x_eval, y_eval, _ = _rows_from_cases(eval_cases, canary=False)
    clean_model = LogisticRegression(solver="lbfgs", random_state=seed, max_iter=200)
    clean_model.fit(x_train, y_train)
    clean_accuracy = float(clean_model.score(x_eval, y_eval))

    x_train_c, y_train_c, canary_names = _rows_from_cases(train_cases, canary=True)
    x_eval_c, y_eval_c, _ = _rows_from_cases(eval_cases, canary=True)
    canary_model = LogisticRegression(solver="lbfgs", random_state=seed, max_iter=200)
    canary_model.fit(x_train_c, y_train_c)
    canary_accuracy = float(canary_model.score(x_eval_c, y_eval_c))

    clean_scan = scan_feature_names_for_leakage(clean_names)
    canary_scan = scan_feature_names_for_leakage(canary_names)
    return SurfaceDecoderReport(
        clean_accuracy=clean_accuracy,
        canary_accuracy=canary_accuracy,
        clean_scanner_fires=bool(clean_scan["fires"]),
        canary_scanner_fires=bool(canary_scan["fires"]),
        train_user_ids=train_user_ids,
        eval_user_ids=eval_user_ids,
        train_eval_disjoint=disjoint,
    )
