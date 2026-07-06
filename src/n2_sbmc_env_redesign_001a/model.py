from __future__ import annotations

import hashlib
import random
from typing import Any


TASK_ID = "N2-SBMC-ENV-REDESIGN-001A"
EXECUTION_TASK_ID = "N2-SBMC-ENV-REDESIGN-001A-STEP-A-STEP-B-001A"
SCHEMA_VERSION = "n2_sbmc_env_redesign_001a.v1"
BASE_SEED = 20260706
DOMAIN_SIZE = 4
COVERED_ATTRS = (0, 1)
UNCOVERED_ATTRS = (2, 3)
EDGES = ((0, 2), (1, 3))
EDGE_OFFSETS = {(0, 2): 1, (1, 3): 2}
TEST_ITEMS_PER_USER = 16
EVAL_USER_IDS = tuple(range(100, 140))
LEAKAGE_TRAIN_USER_IDS = tuple(range(10_000, 10_020))
LEAKAGE_EVAL_USER_IDS = tuple(range(20_000, 20_020))


def derive_seed(*parts: Any, base_seed: int = BASE_SEED) -> int:
    digest = hashlib.sha256(str(base_seed).encode("utf-8"))
    for part in parts:
        digest.update(b"\0")
        digest.update(repr(part).encode("utf-8"))
    return int.from_bytes(digest.digest()[:8], "big") % (2**32)


def relation_tables() -> dict[str, list[list[int]]]:
    tables: dict[str, list[list[int]]] = {}
    for edge in EDGES:
        offset = EDGE_OFFSETS[edge]
        tables[edge_id(edge)] = [[parent, (parent + offset) % DOMAIN_SIZE] for parent in range(DOMAIN_SIZE)]
    return tables


def shifted_relation_tables() -> dict[str, list[list[int]]]:
    tables: dict[str, list[list[int]]] = {}
    for edge in EDGES:
        offset = (EDGE_OFFSETS[edge] + 1) % DOMAIN_SIZE
        tables[edge_id(edge)] = [[parent, (parent + offset) % DOMAIN_SIZE] for parent in range(DOMAIN_SIZE)]
    return tables


def edge_id(edge: tuple[int, int] | list[int]) -> str:
    return f"{int(edge[0])}-{int(edge[1])}"


def theta_for_user(user_id: int) -> dict[int, int]:
    rng = random.Random(derive_seed("theta", int(user_id)))
    covered = {
        0: rng.randrange(DOMAIN_SIZE),
        1: rng.randrange(DOMAIN_SIZE),
    }
    return {
        0: covered[0],
        1: covered[1],
        2: (covered[0] + EDGE_OFFSETS[(0, 2)]) % DOMAIN_SIZE,
        3: (covered[1] + EDGE_OFFSETS[(1, 3)]) % DOMAIN_SIZE,
    }


def feature_names() -> list[str]:
    edge_names = [f"edge_{edge_id(edge)}" for edge in EDGES]
    target_names = [f"target_attr_{attr}" for attr in UNCOVERED_ATTRS]
    value_names = [f"asserted_value_{value}" for value in range(DOMAIN_SIZE)]
    return ["template_relational_claim_v1", *edge_names, *target_names, *value_names]


def item_vector(edge: tuple[int, int], target_attr: int, asserted_value: int) -> list[int]:
    names = feature_names()
    active = {
        "template_relational_claim_v1",
        f"edge_{edge_id(edge)}",
        f"target_attr_{int(target_attr)}",
        f"asserted_value_{int(asserted_value)}",
    }
    return [1 if name in active else 0 for name in names]


def trusted_seed_for_theta(theta: dict[int, int]) -> list[dict[str, Any]]:
    return [
        {
            "schema_version": "n2_sbmc_trusted_observation_v1",
            "attr": int(attr),
            "value": int(theta[attr]),
        }
        for attr in COVERED_ATTRS
    ]


def item_repr(edge: tuple[int, int], asserted_value: int) -> dict[str, Any]:
    parent, target = edge
    return {
        "schema_version": "n2_sbmc_item_repr_v1",
        "template_id": "relational_claim_missing_anchor_value_v1",
        "edge": [int(parent), int(target)],
        "target_attr": int(target),
        "asserted_value": int(asserted_value),
        "feature_names": feature_names(),
        "feature_vector": item_vector(edge, target, asserted_value),
    }


def contaminated_value(true_value: int, *, user_id: int, item_index: int, edge: tuple[int, int]) -> int:
    rng = random.Random(derive_seed("contaminated", int(user_id), int(item_index), edge))
    candidates = [value for value in range(DOMAIN_SIZE) if value != int(true_value)]
    return int(candidates[rng.randrange(len(candidates))])


def build_item(user_id: int, item_index: int, edge: tuple[int, int], label: str, theta: dict[int, int]) -> dict[str, Any]:
    target = edge[1]
    true_value = int(theta[target])
    if label == "genuine":
        asserted = true_value
    elif label == "contaminated":
        asserted = contaminated_value(true_value, user_id=user_id, item_index=item_index, edge=edge)
    else:
        raise ValueError(f"unknown label {label!r}")
    return {
        "item_id": f"u{int(user_id)}-i{int(item_index)}",
        "item_repr": item_repr(edge, asserted),
        "audit": {
            "label": label,
            "label_binary": 1 if label == "contaminated" else 0,
            "theta": {str(k): int(v) for k, v in theta.items()},
            "true_target_value": true_value,
            "contaminated_value_marginally_plausible": bool(asserted in range(DOMAIN_SIZE)),
        },
    }


def build_user_case(user_id: int, *, test_items: int = TEST_ITEMS_PER_USER) -> dict[str, Any]:
    theta = theta_for_user(user_id)
    labels = ["genuine", "contaminated"] * (test_items // 2)
    if len(labels) < test_items:
        labels.append("genuine")
    rng = random.Random(derive_seed("label_shuffle", int(user_id), int(test_items)))
    rng.shuffle(labels)
    items = [
        build_item(int(user_id), index, EDGES[index % len(EDGES)], labels[index], theta)
        for index in range(test_items)
    ]
    case = {
        "schema_version": "n2_sbmc_user_case_v1",
        "user_id": int(user_id),
        "trusted_seed": trusted_seed_for_theta(theta),
        "test_set": items,
        "audit": {"theta": {str(k): int(v) for k, v in theta.items()}},
    }
    assert_case_invariants(case)
    return case


def item_repr_contains_forbidden_audit(item: dict[str, Any]) -> bool:
    forbidden = {"theta", "label", "label_binary", "audit", "provenance", "source", "user_id"}
    stack: list[Any] = [item]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            if any(key in forbidden for key in current):
                return True
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return False


def assert_case_invariants(case: dict[str, Any]) -> None:
    covered = {int(row["attr"]) for row in case["trusted_seed"]}
    if covered != set(COVERED_ATTRS):
        raise AssertionError("trusted seed does not contain exactly covered attributes")
    for item in case["test_set"]:
        rep = item["item_repr"]
        if item_repr_contains_forbidden_audit(rep):
            raise AssertionError("item_repr leaks audit-only fields")
        target = int(rep["target_attr"])
        if target in covered:
            raise AssertionError("sparse coverage failed: test target is in trusted seed")
        if int(rep["asserted_value"]) not in range(DOMAIN_SIZE):
            raise AssertionError("asserted value is not marginally plausible")


def allowed_context_from_case(case: dict[str, Any], *, include_covered: bool = True) -> dict[str, Any]:
    return {
        "schema_version": "n2_sbmc_allowed_context_v1",
        "trusted_seed": list(case["trusted_seed"]) if include_covered else [],
        "relation_tables": relation_tables(),
    }
