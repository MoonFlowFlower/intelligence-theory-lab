"""Unrun STEP-B scoring harness definitions for SBMC headroom scout.

STEP-A may import and self-test definitions, but must not call the aggregate
headroom gate or write result.json.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Mapping

from . import detectors as D
from . import gen_model as GM

TASK_ID = GM.TASK_ID


def code_path_hash() -> str:
    h = sha256()
    for rel in ("gen_model.py", "detectors.py", "harness.py"):
        h.update((Path(__file__).resolve().parent / rel).read_bytes())
    return h.hexdigest()


def run_guarded_non_ideal_detector(
    detector: Callable[[Mapping[str, Any], Mapping[str, Any], int], int],
    item_repr: Mapping[str, Any],
    user_context: Mapping[str, Any],
    seed: int,
) -> int:
    guarded_item = D.guard_payload(item_repr)
    guarded_context = D.guard_payload(user_context)
    return int(detector(guarded_item, guarded_context, int(seed)))


def detector_scores_for_item(item: dict[str, Any], user_case: dict[str, Any], seed: int) -> dict[str, int]:
    item_repr = item["item_repr"]
    allowed_context = GM.allowed_context_from_user_case(user_case)
    scores: dict[str, int] = {}
    scores["ideal"] = int(D.ideal(item_repr, {"theta": user_case["theta"]}, seed))
    for name, detector in D.NON_IDEAL_DETECTORS.items():
        scores[name] = run_guarded_non_ideal_detector(detector, item_repr, allowed_context, seed)
    return scores


def trace_for_user(user_case: dict[str, Any], *, seed: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in user_case["test_set"]:
        rows.append(
            {
                "user_id": int(user_case["user_id"]),
                "edge": item["item_repr"]["edge"],
                "asserted_tuple": item["item_repr"]["asserted_tuple"],
                "item_bow": item["item_repr"]["bow_vector"],
                "label": item["audit"]["label"],
                "label_binary": item["audit"]["label_binary"],
                "theta": list(user_case["theta"]),
                "detector_scores": detector_scores_for_item(item, user_case, seed),
            }
        )
    return rows


def macro_f1_binary(labels: list[int], predictions: list[int]) -> float:
    """Balanced macro-F1 definition for STEP-B.  Not called by preregistration."""

    f1_values: list[float] = []
    for positive_class in (0, 1):
        tp = sum(1 for y, p in zip(labels, predictions) if y == positive_class and p == positive_class)
        fp = sum(1 for y, p in zip(labels, predictions) if y != positive_class and p == positive_class)
        fn = sum(1 for y, p in zip(labels, predictions) if y == positive_class and p != positive_class)
        denom = 2 * tp + fp + fn
        f1_values.append(0.0 if denom == 0 else (2 * tp) / denom)
    return float(sum(f1_values) / len(f1_values))


def run_scoring_harness(
    *,
    eval_user_ids: list[int],
    surface_train_user_ids: list[int],
    seed: int = GM.BASE_SEED,
) -> dict[str, Any]:
    """STEP-B callable scoring path; forbidden to call in STEP-A."""

    if not set(eval_user_ids).isdisjoint(surface_train_user_ids):
        raise ValueError("surface train and eval users must be disjoint")
    eval_cases = [GM.build_user_case(user_id) for user_id in eval_user_ids]
    trace_rows = [row for case in eval_cases for row in trace_for_user(case, seed=seed)]
    labels = [int(row["label_binary"]) for row in trace_rows]
    detector_names = list(D.DETECTORS)
    metrics: dict[str, Any] = {}
    for name in detector_names:
        preds = [int(row["detector_scores"][name]) for row in trace_rows]
        metrics[f"{name}_macroF1"] = macro_f1_binary(labels, preds)
    return {
        "task_id": TASK_ID,
        "producer_function": "run_scoring_harness",
        "run_id": f"{TASK_ID}-STEPB-UNRUN-DEFINITION",
        "seed": int(seed),
        "eval_user_ids": list(eval_user_ids),
        "surface_train_user_ids": list(surface_train_user_ids),
        "aggregation_rule": "balanced macro-F1 per detector over eval items, averaged over users by pooled trace rows",
        "code_path_hash": code_path_hash(),
        "metrics": metrics,
    }


def replay_non_ideal_from_serialized(serialized_user_case: dict[str, Any], expected_rows: list[dict[str, Any]], seed: int) -> dict[str, Any]:
    """Recompute non-ideal detectors from serialized item_repr + trusted_seed context."""

    allowed_context = {
        "schema_version": "sbmc_allowed_context_v1",
        "trusted_seed": [item["item_repr"] for item in serialized_user_case["trusted_seed"]],
    }
    recomputed: list[dict[str, Any]] = []
    for item, expected in zip(serialized_user_case["test_set"], expected_rows):
        item_repr = item["item_repr"]
        scores = {
            name: run_guarded_non_ideal_detector(detector, item_repr, allowed_context, seed)
            for name, detector in D.NON_IDEAL_DETECTORS.items()
        }
        recomputed.append({"item_id": item["item_id"], "non_ideal_detector_scores": scores})
    expected_non_ideal = [
        {
            name: int(row["detector_scores"][name])
            for name in D.NON_IDEAL_DETECTORS
        }
        for row in expected_rows
    ]
    observed_non_ideal = [row["non_ideal_detector_scores"] for row in recomputed]
    return {
        "producer_function": "replay_non_ideal_from_serialized",
        "uses_theta": False,
        "uses_label": False,
        "match": observed_non_ideal == expected_non_ideal,
        "recomputed": recomputed,
    }


def run_leakage_positive_control(
    *,
    train_user_ids: range | list[int] = range(10_000, 10_020),
    eval_user_ids: range | list[int] = range(20_000, 20_020),
    seed: int = GM.BASE_SEED,
) -> dict[str, Any]:
    train_ids = [int(x) for x in train_user_ids]
    eval_ids = [int(x) for x in eval_user_ids]
    train_cases = [GM.build_user_case(user_id) for user_id in train_ids]
    eval_cases = [GM.build_user_case(user_id) for user_id in eval_ids]
    report = D.run_surface_decoder_positive_control(train_cases=train_cases, eval_cases=eval_cases, seed=seed)
    return {
        "producer_function": report.producer_function,
        "metric": report.metric,
        "clean_accuracy": report.clean_accuracy,
        "canary_accuracy": report.canary_accuracy,
        "clean_scanner_fires": report.clean_scanner_fires,
        "canary_scanner_fires": report.canary_scanner_fires,
        "train_user_ids": report.train_user_ids,
        "eval_user_ids": report.eval_user_ids,
        "train_eval_disjoint": report.train_eval_disjoint,
        "positive_control_fires": bool(
            report.train_eval_disjoint
            and not report.clean_scanner_fires
            and report.canary_scanner_fires
            and report.canary_accuracy >= report.clean_accuracy + 0.20
            and report.canary_accuracy >= 0.70
        ),
    }


def evaluate_headroom_gate(metrics: dict[str, float], thresholds: dict[str, float]) -> dict[str, Any]:
    """Frozen STEP-B decision table.  Defined in STEP-A; not invoked by preregistration."""

    cheap_names = ("embedding_outlier", "frequency_marginal", "predict_all", "predict_none", "majority")
    cheap_max = max(float(metrics[f"{name}_macroF1"]) for name in cheap_names)
    ideal = float(metrics["ideal_macroF1"])
    fair = float(metrics["fair_inference_macroF1"])
    ideal_pass = ideal >= 0.50 + float(thresholds["H"])
    headroom_pass = (ideal - cheap_max) >= float(thresholds["G"])
    reachable = (fair - cheap_max) >= float(thresholds["G_reach"])
    if not (ideal_pass and headroom_pass):
        decision = "ideal_gate_fails"
    elif reachable:
        decision = "ideal_gate_passes_and_fair_inference_reachable"
    else:
        decision = "ideal_gate_passes_but_fair_inference_floor"
    return {
        "producer_function": "evaluate_headroom_gate",
        "ideal_macroF1": ideal,
        "cheap_max_macroF1": cheap_max,
        "fair_inference_macroF1": fair,
        "ideal_gate_pass": bool(ideal_pass),
        "headroom_pass": bool(headroom_pass),
        "fair_reachability_pass": bool(reachable),
        "decision": decision,
    }


def feasibility_build_dummy_users(n_users: int = 5) -> dict[str, Any]:
    start = perf_counter()
    users = GM.build_dummy_users(n_users)
    elapsed = perf_counter() - start
    return {
        "producer_function": "feasibility_build_dummy_users",
        "n_users": int(n_users),
        "elapsed_seconds": float(elapsed),
        "metric_aggregation_performed": False,
        "user_ids": [int(u["user_id"]) for u in users],
    }


def assert_no_step_a_scoring_artifacts(repo_root: Path | None = None) -> None:
    root = repo_root or Path(__file__).resolve().parents[2]
    forbidden = root / "artifacts" / TASK_ID / "result.json"
    if forbidden.exists():
        raise AssertionError(f"STEP-A must not create {forbidden}")


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))
