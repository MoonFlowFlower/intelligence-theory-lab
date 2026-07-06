from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Callable

from . import model


FORBIDDEN_AUDIT_KEYS = frozenset({"theta", "label", "label_binary", "audit", "provenance", "source", "user_id"})


class GuardViolation(RuntimeError):
    pass


class GuardedMapping(Mapping):
    def __init__(self, data: Mapping[str, Any], *, forbidden: frozenset[str] = FORBIDDEN_AUDIT_KEYS):
        self._data = dict(data)
        self._forbidden = forbidden

    def __getitem__(self, key: str) -> Any:
        if key in self._forbidden:
            raise GuardViolation(f"forbidden audit/provenance key read: {key}")
        return guard_payload(self._data[key], forbidden=self._forbidden)

    def __iter__(self):
        return (key for key in self._data if key not in self._forbidden)

    def __len__(self) -> int:
        return len([key for key in self._data if key not in self._forbidden])

    def get(self, key: str, default: Any = None) -> Any:
        if key in self._forbidden:
            raise GuardViolation(f"forbidden audit/provenance key read: {key}")
        if key not in self._data:
            return default
        return guard_payload(self._data[key], forbidden=self._forbidden)


def guard_payload(data: Any, *, forbidden: frozenset[str] = FORBIDDEN_AUDIT_KEYS) -> Any:
    if isinstance(data, Mapping):
        return GuardedMapping(data, forbidden=forbidden)
    if isinstance(data, list):
        return [guard_payload(item, forbidden=forbidden) for item in data]
    return data


def _trusted_values(context: Mapping[str, Any]) -> dict[int, int]:
    return {int(row["attr"]): int(row["value"]) for row in context.get("trusted_seed", [])}


def _allowed_child_value(parent_value: int, edge: tuple[int, int], relation_tables: Mapping[str, Any]) -> int | None:
    rows = relation_tables.get(model.edge_id(edge), [])
    for parent, child in rows:
        if int(parent) == int(parent_value):
            return int(child)
    return None


def ideal(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    _ = seed
    theta = {int(k): int(v) for k, v in user_context["theta"].items()}
    target = int(item_repr["target_attr"])
    return int(int(item_repr["asserted_value"]) != theta[target])


def graph_closure(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    _ = seed
    edge = (int(item_repr["edge"][0]), int(item_repr["edge"][1]))
    parent = edge[0]
    trusted = _trusted_values(user_context)
    if parent not in trusted:
        return 0
    allowed = _allowed_child_value(trusted[parent], edge, user_context["relation_tables"])
    if allowed is None:
        return 0
    return int(int(item_repr["asserted_value"]) != allowed)


def per_user_lookup_nn(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    _ = seed
    target = int(item_repr["target_attr"])
    trusted = _trusted_values(user_context)
    if target not in trusted:
        return 0
    return int(int(item_repr["asserted_value"]) != trusted[target])


def value_aware_embedding_outlier(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    _ = seed
    observed_values = {int(row["value"]) for row in user_context.get("trusted_seed", [])}
    if not observed_values:
        return 0
    return int(int(item_repr["asserted_value"]) not in observed_values)


def frequency_marginal(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    _ = seed
    target = int(item_repr["target_attr"])
    trusted_values = [int(row["value"]) for row in user_context.get("trusted_seed", []) if int(row["attr"]) == target]
    if not trusted_values:
        return 0
    return int(int(item_repr["asserted_value"]) not in trusted_values)


def predict_all(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    _ = item_repr, user_context, seed
    return 1


def predict_none(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    _ = item_repr, user_context, seed
    return 0


def majority(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    _ = item_repr, user_context, seed
    return 0


def structural_anomaly(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    """Metadata-stripped structural anomaly floor.

    The redesigned surface style-matches every item to a known edge/template, so
    this detector can only fire on malformed structure, not audit labels.
    """

    _ = user_context, seed
    edge = tuple(int(x) for x in item_repr["edge"])
    return int(edge not in model.EDGES or item_repr.get("template_id") != "relational_claim_missing_anchor_value_v1")


def semantic_anomaly_provenance(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    """Agent-Memory-Guard-style semantic/provenance floor.

    Provenance is intentionally absent from legal item representations; the
    detector is a real scanner over visible keys and collapses under stripping.
    """

    _ = user_context, seed
    visible_keys = {str(key).lower() for key in item_repr}
    return int(any(key in visible_keys for key in ("provenance", "source", "audit", "label")))


def provenance_hash_chain(item_repr: Mapping[str, Any], user_context: Mapping[str, Any], seed: int) -> int:
    """Engram-style provenance/hash-chain floor over legal visible fields."""

    _ = item_repr, seed
    return int(any("provenance" in str(key).lower() or "hash_chain" in str(key).lower() for key in user_context))


NON_IDEAL_DETECTORS: dict[str, Callable[[Mapping[str, Any], Mapping[str, Any], int], int]] = {
    "per_user_lookup_nn": per_user_lookup_nn,
    "graph_closure": graph_closure,
    "value_aware_embedding_outlier": value_aware_embedding_outlier,
    "frequency_marginal": frequency_marginal,
    "structural_anomaly": structural_anomaly,
    "semantic_anomaly_provenance": semantic_anomaly_provenance,
    "provenance_hash_chain": provenance_hash_chain,
    "predict_all": predict_all,
    "predict_none": predict_none,
    "majority": majority,
}

DETECTORS: dict[str, Callable[[Mapping[str, Any], Mapping[str, Any], int], int]] = {
    "ideal": ideal,
    **NON_IDEAL_DETECTORS,
}


def scan_feature_names_for_leakage(feature_names: list[str]) -> dict[str, Any]:
    patterns = ("theta", "label", "provenance", "source", "user_id", "audit")
    hits = sorted({name for name in feature_names for pattern in patterns if pattern in name.lower()})
    return {
        "producer_function": "n2_sbmc_env_redesign_001a.detectors.scan_feature_names_for_leakage",
        "patterns": list(patterns),
        "hits": hits,
        "fires": bool(hits),
    }
