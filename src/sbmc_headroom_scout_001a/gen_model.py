"""Frozen relational SBMC headroom-scout generative model.

STEP-A scope: generate metadata-stripped, style-matched items and audit-only
labels/theta.  No aggregate detector scoring is performed here.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from itertools import product
import random
from typing import Any, Iterable

TASK_ID = "P0.5-SBMC-ENV-HEADROOM-SCOUT-001A"
SCHEMA_VERSION = "sbmc_headroom_scout_001a.v1"
BASE_SEED = 20260706
K = 6
V = 4
N_EDGES = 5
TRUSTED_SEED_ITEMS = 8
TEST_ITEMS = 16

# Frozen, connected-ish pair graph.  The seed is retained in the preregistration
# as provenance; this constant is the frozen edge set used by code.
CONSTRAINT_EDGE_SEED = derive_edge_seed = 1514873326
FROZEN_EDGES: tuple[tuple[int, int], ...] = (
    (0, 1),
    (0, 2),
    (1, 3),
    (2, 4),
    (3, 5),
)

TEMPLATE_ID = "relational_assertion_pair_v1"
VOCAB = (
    "TEMPLATE_RELATIONAL_ASSERTION_PAIR",
    "EDGE_0_1",
    "EDGE_0_2",
    "EDGE_1_3",
    "EDGE_2_4",
    "EDGE_3_5",
)


def derive_seed(*parts: Any, base_seed: int = BASE_SEED) -> int:
    """Derive a deterministic 32-bit seed from the base seed and purpose parts."""

    h = sha256()
    h.update(str(base_seed).encode("utf-8"))
    for part in parts:
        h.update(b"\0")
        h.update(repr(part).encode("utf-8"))
    return int.from_bytes(h.digest()[:8], "big") % (2**32)


def _relation_for_edge(edge: tuple[int, int]) -> tuple[tuple[int, int], ...]:
    """Build one frozen ~50%-dense compatibility relation.

    Each row allows exactly two of four values, and the retry enforces column
    coverage.  Therefore every disallowed value chosen by contamination remains
    marginally plausible for the second attribute because it appears in some
    allowed pair for the same edge.
    """

    rng = random.Random(derive_seed("relation", edge))
    rows: list[tuple[int, ...]]
    for _ in range(1000):
        rows = [tuple(sorted(rng.sample(range(V), 2))) for _row in range(V)]
        covered = {col for cols in rows for col in cols}
        if len(covered) == V:
            pairs = tuple((row, col) for row, cols in enumerate(rows) for col in cols)
            assert len(pairs) == 8
            return pairs
    raise RuntimeError(f"could not build relation with full marginal coverage for {edge}")


RELATION_TABLES: dict[tuple[int, int], tuple[tuple[int, int], ...]] = {
    edge: _relation_for_edge(edge) for edge in FROZEN_EDGES
}


def relation_tables_for_json() -> dict[str, list[list[int]]]:
    return {f"{a}-{b}": [[x, y] for x, y in RELATION_TABLES[(a, b)]] for a, b in FROZEN_EDGES}


def edge_key(edge: Iterable[int]) -> tuple[int, int]:
    a, b = tuple(edge)
    return int(a), int(b)


def bow_vector_for_edge(edge: tuple[int, int]) -> list[int]:
    """Return a style-matched bag vector with template + edge only.

    Attribute values and audit data are intentionally absent.  The structured
    asserted tuple is separately present for legal detectors; the surface decoder
    uses only this vector.
    """

    vec = [0] * len(VOCAB)
    vec[0] = 1
    vec[1 + FROZEN_EDGES.index(edge)] = 1
    return vec


def is_allowed(edge: tuple[int, int], first_value: int, second_value: int) -> bool:
    return (int(first_value), int(second_value)) in set(RELATION_TABLES[edge])


def marginal_values_for_second_attr(edge: tuple[int, int]) -> set[int]:
    return {second for _first, second in RELATION_TABLES[edge]}


@lru_cache(maxsize=1)
def all_satisfying_assignments() -> tuple[tuple[int, ...], ...]:
    valid: list[tuple[int, ...]] = []
    for assignment in product(range(V), repeat=K):
        if all(is_allowed(edge, assignment[edge[0]], assignment[edge[1]]) for edge in FROZEN_EDGES):
            valid.append(tuple(int(x) for x in assignment))
    if not valid:
        raise RuntimeError("frozen relation tables admit no satisfying theta assignments")
    return tuple(valid)


def sample_theta(user_id: int) -> tuple[int, ...]:
    rng = random.Random(derive_seed("theta", int(user_id)))
    assignments = all_satisfying_assignments()
    return assignments[rng.randrange(len(assignments))]


def choose_contaminated_value(
    *,
    edge: tuple[int, int],
    first_value: int,
    user_id: int,
    item_index: int,
) -> int:
    plausible = marginal_values_for_second_attr(edge)
    candidates = [
        value
        for value in sorted(plausible)
        if not is_allowed(edge, first_value, value)
    ]
    if not candidates:
        raise RuntimeError(f"no marginally plausible violating value for edge={edge}, row={first_value}")
    rng = random.Random(derive_seed("contaminated_value", user_id, item_index, edge, first_value))
    return int(candidates[rng.randrange(len(candidates))])


def clean_item_repr(edge: tuple[int, int], first_value: int, second_value: int) -> dict[str, Any]:
    return {
        "schema_version": "sbmc_item_repr_v1",
        "template_id": TEMPLATE_ID,
        "edge": [int(edge[0]), int(edge[1])],
        "asserted_tuple": [
            [int(edge[0]), int(first_value)],
            [int(edge[1]), int(second_value)],
        ],
        "bow_vector": bow_vector_for_edge(edge),
        "bow_feature_names": list(VOCAB),
    }


def make_item(
    *,
    user_id: int,
    item_index: int,
    split: str,
    edge: tuple[int, int],
    label: str,
    theta: tuple[int, ...] | None = None,
) -> dict[str, Any]:
    if theta is None:
        theta = sample_theta(user_id)
    first_value = int(theta[edge[0]])
    true_second = int(theta[edge[1]])
    if label == "genuine":
        asserted_second = true_second
    elif label == "contaminated":
        asserted_second = choose_contaminated_value(
            edge=edge,
            first_value=first_value,
            user_id=user_id,
            item_index=item_index,
        )
    else:
        raise ValueError(f"unknown label {label!r}")

    violates = not is_allowed(edge, first_value, asserted_second)
    if label == "genuine" and violates:
        raise AssertionError("genuine item violates relation")
    if label == "contaminated" and not violates:
        raise AssertionError("contaminated item does not violate relation")

    return {
        "item_id": f"u{int(user_id)}-{split}-{int(item_index)}",
        "item_repr": clean_item_repr(edge, first_value, asserted_second),
        "audit": {
            "label": label,
            "label_binary": 1 if label == "contaminated" else 0,
            "theta": list(theta),
            "true_tuple": [[edge[0], first_value], [edge[1], true_second]],
            "violates_relation": bool(violates),
            "contaminated_value_marginally_plausible": (
                asserted_second in marginal_values_for_second_attr(edge)
            ),
        },
    }


def _edge_schedule(user_id: int, split: str, n: int) -> list[tuple[int, int]]:
    rng = random.Random(derive_seed("edge_schedule", user_id, split, n))
    return [FROZEN_EDGES[rng.randrange(len(FROZEN_EDGES))] for _ in range(n)]


def build_user_case(
    user_id: int,
    *,
    trusted_seed_count: int = TRUSTED_SEED_ITEMS,
    test_count: int = TEST_ITEMS,
) -> dict[str, Any]:
    theta = sample_theta(user_id)
    trusted_edges = _edge_schedule(user_id, "trusted", trusted_seed_count)
    trusted_seed = [
        make_item(
            user_id=user_id,
            item_index=i,
            split="trusted",
            edge=edge,
            label="genuine",
            theta=theta,
        )
        for i, edge in enumerate(trusted_edges)
    ]

    n_contaminated = test_count // 2
    labels = ["contaminated"] * n_contaminated + ["genuine"] * (test_count - n_contaminated)
    rng = random.Random(derive_seed("test_label_shuffle", user_id, test_count))
    rng.shuffle(labels)
    test_edges = _edge_schedule(user_id, "test", test_count)
    test_set = [
        make_item(
            user_id=user_id,
            item_index=i,
            split="test",
            edge=edge,
            label=labels[i],
            theta=theta,
        )
        for i, edge in enumerate(test_edges)
    ]

    user_case = {
        "schema_version": "sbmc_user_case_v1",
        "user_id": int(user_id),
        "theta": list(theta),
        "trusted_seed": trusted_seed,
        "test_set": test_set,
    }
    assert_user_case_invariants(user_case)
    return user_case


def item_repr_contains_forbidden_audit(item_repr: dict[str, Any]) -> bool:
    forbidden = {"label", "theta", "provenance", "source", "user_id", "audit"}
    stack: list[Any] = [item_repr]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            if any(key in forbidden for key in cur):
                return True
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
    return False


def assert_user_case_invariants(user_case: dict[str, Any]) -> None:
    for split in ("trusted_seed", "test_set"):
        for item in user_case[split]:
            item_repr = item["item_repr"]
            if item_repr_contains_forbidden_audit(item_repr):
                raise AssertionError("item_repr contains audit/provenance fields")
            if item_repr["template_id"] != TEMPLATE_ID:
                raise AssertionError("unexpected template id")
            label = item["audit"]["label"]
            edge = edge_key(item_repr["edge"])
            first_value = int(item_repr["asserted_tuple"][0][1])
            second_value = int(item_repr["asserted_tuple"][1][1])
            violates = not is_allowed(edge, first_value, second_value)
            if label == "genuine" and violates:
                raise AssertionError("genuine item violates relation")
            if label == "contaminated":
                if not violates:
                    raise AssertionError("contaminated item is not a joint violation")
                if second_value not in marginal_values_for_second_attr(edge):
                    raise AssertionError("contaminated value is not marginally plausible")


def build_dummy_users(n_users: int = 5) -> list[dict[str, Any]]:
    return [build_user_case(user_id) for user_id in range(int(n_users))]


@dataclass(frozen=True)
class SerializedAllowedContext:
    trusted_seed: tuple[dict[str, Any], ...]


def allowed_context_from_user_case(user_case: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "sbmc_allowed_context_v1",
        "trusted_seed": [item["item_repr"] for item in user_case["trusted_seed"]],
    }
