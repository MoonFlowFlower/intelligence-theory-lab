"""S3D-NULL-IDEAL-DIAG-001A standalone NULL-env ideal diagnostic.

This script is intentionally artifact-local.  It imports the existing
FSP-PUM simulator, FactoredExactFilter, trajectory-set, and S3d helper code,
but it does not edit source, frozen specs, runners, or banked artifacts.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
import time
from typing import Any, Iterable, Mapping, Sequence

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from src.fsp_pum_env.factored_filter import FactoredExactFilter
from src.fsp_pum_env.ideal_observer import PrefixEvent, independent_filter_seed
from src.fsp_pum_env.s3d_certificates import (
    NULL_MARGIN,
    build_s3d_cert_set_specs,
    macro_balanced_accuracy,
)
from src.fsp_pum_env.simulator import FspPumSimulator, SimulatorVariant
from src.fsp_pum_env.trajectory_sets import (
    TrajectorySetSpec,
    _iter_records_with_adjudicator,
    load_frozen_design,
)


TASK_ID = "S3D-NULL-IDEAL-DIAG-001A"
ARTIFACT_ROOT = ROOT / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A"
OUT_DIR = ARTIFACT_ROOT / "s3d_null_ideal_diag_001a"
FROZEN_DESIGN = ARTIFACT_ROOT / "frozen_design.json"
RESULT_PATH = OUT_DIR / "result.json"
TRACE_PATH = OUT_DIR / "trace.jsonl"
FINDINGS_PATH = OUT_DIR / "findings.md"
CHANCE = 1.0 / 32.0
NULL_LIMIT = CHANCE + NULL_MARGIN
REFERENCE_VOIDED_NULL_IDEAL = 0.07211008467764463


@dataclass(frozen=True)
class UserData:
    user_id: int
    records: tuple[dict[str, Any], ...]
    style_map: tuple[int, ...]


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, set):
        return sorted(_jsonable(v) for v in value)
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_json(payload: Any) -> str:
    encoded = json.dumps(_jsonable(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(encoded)


def _write_json_roundtrip(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(_jsonable(payload), handle, indent=2, sort_keys=True)
        handle.write("\n")
    with path.open("r", encoding="utf-8") as handle:
        json.load(handle)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        if not text.endswith("\n"):
            handle.write("\n")


def _code_path_hash() -> str:
    paths = [
        Path(__file__),
        ROOT / "src" / "fsp_pum_env" / "factored_filter.py",
        ROOT / "src" / "fsp_pum_env" / "simulator.py",
        ROOT / "src" / "fsp_pum_env" / "s3d_certificates.py",
        ROOT / "src" / "fsp_pum_env" / "trajectory_sets.py",
        ROOT / "src" / "fsp_pum_env" / "ideal_observer.py",
    ]
    h = hashlib.sha256()
    for path in paths:
        h.update(str(path.relative_to(ROOT)).encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _build_one_user_spec(spec: Any, user_id: int) -> TrajectorySetSpec:
    return TrajectorySetSpec(
        set_id=f"{spec.trajectory_spec.set_id}_diag_user_{int(user_id)}",
        master_seed=int(spec.master_seed),
        env_mode=str(spec.variant),
        partitions={"train": {"start_user_id": int(user_id), "count": 1}},
        turns_per_user=int(spec.trajectory_spec.turns_per_user),
        logging_policy=spec.trajectory_spec.logging_policy,
    )


def _load_user_data(design: Mapping[str, Any], spec: Any, user_id: int) -> UserData:
    if 800 <= int(user_id) <= 999:
        raise RuntimeError(f"heldout_user_forbidden:{user_id}")
    records: list[dict[str, Any]] = []
    style_map: tuple[int, ...] | None = None
    for _, _, record, adjudicator_record in _iter_records_with_adjudicator(
        design,
        _build_one_user_spec(spec, int(user_id)),
    ):
        records.append(record)
        current_style = tuple(int(value) for value in adjudicator_record["style_map"])
        if style_map is None:
            style_map = current_style
        elif current_style != style_map:
            raise RuntimeError(f"style_map_changed_within_user:{user_id}")
    if style_map is None:
        raise RuntimeError(f"no_records_for_user:{user_id}")
    return UserData(user_id=int(user_id), records=tuple(records), style_map=style_map)


def _wrong_style_map(true_style_map: Sequence[int]) -> tuple[int, ...]:
    alphabet = len(true_style_map)
    return tuple((int(value) + 1) % alphabet for value in true_style_map)


def _filter_for_user(
    design: Mapping[str, Any],
    spec: Any,
    user_id: int,
    style_map: Sequence[int],
    *,
    context_suffix: str = "",
) -> FactoredExactFilter:
    context = f"s3d_battery:{spec.cell_id}:{int(user_id)}{context_suffix}"
    return FactoredExactFilter(
        design,
        filter_seed=independent_filter_seed(int(spec.master_seed), context),
        true_environment_seed=int(spec.master_seed),
        variant=str(spec.variant),
        user_id=int(user_id),
        style_map=style_map,
        z_quadrature_points=3,
    )


def _scope_metrics(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    targets = [int(row["target"]) for row in rows]
    predictions = [int(row["prediction"]) for row in rows]
    actions = [str(row["action"]) for row in rows]
    recommend_indices = [index for index, action in enumerate(actions) if action == "recommend"]
    recommend_targets = [targets[index] for index in recommend_indices]
    recommend_predictions = [predictions[index] for index in recommend_indices]
    return {
        "overall": {
            "metric": float(macro_balanced_accuracy(targets, predictions, alphabet_size=32)),
            "n_eval_points": len(targets),
            "classes_present": sorted({int(value) for value in targets}),
            "class_count_present": len({int(value) for value in targets}),
        },
        "recommend_turn_conditional": {
            "metric": None
            if not recommend_indices
            else float(macro_balanced_accuracy(recommend_targets, recommend_predictions, alphabet_size=32)),
            "n_eval_points": len(recommend_indices),
            "classes_present": sorted({int(value) for value in recommend_targets}),
            "class_count_present": len({int(value) for value in recommend_targets}),
            "prediction_modes_present": sorted({int(value) for value in recommend_predictions}),
        },
        "aggregation_rule": "macro-balanced accuracy over classes with >=1 true occurrence; recommend scope filters logged action == recommend",
    }


def _per_user_metrics(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for user_id in sorted({int(row["user_id"]) for row in rows}):
        subset = [row for row in rows if int(row["user_id"]) == user_id]
        out.append({"user_id": user_id, "scope_metrics": _scope_metrics(subset)})
    return out


def _result_digest(rows: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    compact = [
        {
            "user_id": int(row["user_id"]),
            "step_index": int(row["step_index"]),
            "action": str(row["action"]),
            "prediction": int(row["prediction"]),
            "target": int(row["target"]),
        }
        for row in rows
    ]
    return {
        "turn_rows_sha256": _sha256_json(compact),
        "actions_sha256": _sha256_json([row["action"] for row in compact]),
        "predictions_sha256": _sha256_json([row["prediction"] for row in compact]),
        "targets_sha256": _sha256_json([row["target"] for row in compact]),
    }


def _score_ideal(
    design: Mapping[str, Any],
    spec: Any,
    users: Sequence[UserData],
    *,
    test_id: str,
    style_variant: str,
    trace_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    start = time.perf_counter()
    rows: list[dict[str, Any]] = []
    atom_count = None
    array_bytes = None
    style_map_digests: dict[str, str] = {}
    for user in users:
        style_map = user.style_map if style_variant == "true" else _wrong_style_map(user.style_map)
        style_map_digests[str(user.user_id)] = _sha256_json(style_map)
        filt = _filter_for_user(design, spec, user.user_id, style_map)
        atom_count = int(filt.atom_count)
        array_bytes = int(filt.array_bytes())
        for record in user.records:
            action = str(record["action"])
            distribution = filt.predict_distribution(action)
            prediction = int(np.argmax(np.asarray(distribution, dtype=float)))
            target = int(record["observation"]["symbol"])
            row = {
                "test_id": test_id,
                "user_id": int(user.user_id),
                "step_index": int(record["step_index"]),
                "session_index": int(record["session_index"]),
                "turn_in_session": int(record["turn_in_session"]),
                "action": action,
                "prediction": prediction,
                "target": target,
                "is_recommend_turn": action == "recommend",
                "distribution_sha256": _sha256_json([round(float(value), 17) for value in distribution]),
            }
            rows.append(row)
            trace_rows.append(row)
            filt.observe(PrefixEvent(action=action, symbol=target))
    return {
        "test_id": test_id,
        "producer_function": "s3d_null_ideal_diag_001a._score_ideal",
        "style_variant": style_variant,
        "input_artifacts": [str(FROZEN_DESIGN.relative_to(ROOT))],
        "run_user_ids": [int(user.user_id) for user in users],
        "seed_contexts": [
            f"independent_filter_seed({int(spec.master_seed)}, s3d_battery:{spec.cell_id}:{int(user.user_id)})"
            for user in users
        ],
        "episode_ids": [
            {"user_id": int(user.user_id), "turns": len(user.records), "step_index_range": [0, len(user.records) - 1]}
            for user in users
        ],
        "scope_metrics": _scope_metrics(rows),
        "per_user_metrics": _per_user_metrics(rows),
        "digests": _result_digest(rows),
        "style_map_sha256_by_user": style_map_digests,
        "atom_count": atom_count,
        "posterior_array_bytes": array_bytes,
        "wall_clock_seconds": time.perf_counter() - start,
    }


def _run_history_independence(
    design: Mapping[str, Any],
    spec: Any,
    users: Sequence[UserData],
) -> dict[str, Any]:
    start = time.perf_counter()
    rng = np.random.Generator(np.random.PCG64(2026070501))
    true_rows: list[dict[str, Any]] = []
    scrambled_rows: list[dict[str, Any]] = []
    distribution_max_abs_diff = 0.0
    prediction_mismatches = 0
    random_observation_rows: list[dict[str, Any]] = []
    random_equals_target = 0
    for user in users:
        true_filter = _filter_for_user(design, spec, user.user_id, user.style_map)
        scrambled_filter = _filter_for_user(design, spec, user.user_id, user.style_map, context_suffix=":scrambled_obs")
        for record in user.records:
            action = str(record["action"])
            true_distribution = true_filter.predict_distribution(action)
            scrambled_distribution = scrambled_filter.predict_distribution(action)
            distribution_max_abs_diff = max(
                distribution_max_abs_diff,
                float(
                    np.max(
                        np.abs(
                            np.asarray(true_distribution, dtype=float)
                            - np.asarray(scrambled_distribution, dtype=float)
                        )
                    )
                ),
            )
            true_prediction = int(np.argmax(np.asarray(true_distribution, dtype=float)))
            scrambled_prediction = int(np.argmax(np.asarray(scrambled_distribution, dtype=float)))
            prediction_mismatches += int(true_prediction != scrambled_prediction)
            target = int(record["observation"]["symbol"])
            random_symbol = int(rng.integers(0, 32))
            random_equals_target += int(random_symbol == target)
            base = {
                "test_id": "T2",
                "user_id": int(user.user_id),
                "step_index": int(record["step_index"]),
                "action": action,
                "target": target,
                "is_recommend_turn": action == "recommend",
            }
            true_rows.append({**base, "prediction": true_prediction})
            scrambled_rows.append({**base, "prediction": scrambled_prediction, "scrambled_observed_symbol": random_symbol})
            random_observation_rows.append(
                {
                    "user_id": int(user.user_id),
                    "step_index": int(record["step_index"]),
                    "action": action,
                    "target": target,
                    "scrambled_observed_symbol": random_symbol,
                }
            )
            true_filter.observe(PrefixEvent(action=action, symbol=target))
            scrambled_filter.observe(PrefixEvent(action=action, symbol=random_symbol))
    return {
        "test_id": "T2",
        "producer_function": "s3d_null_ideal_diag_001a._run_history_independence",
        "input_artifacts": [str(FROZEN_DESIGN.relative_to(ROOT))],
        "run_user_ids": [int(user.user_id) for user in users],
        "scrambled_observation_seed": 2026070501,
        "random_equals_target_count": int(random_equals_target),
        "random_observation_digest": _sha256_json(random_observation_rows),
        "prediction_mismatches": int(prediction_mismatches),
        "max_distribution_abs_diff": float(distribution_max_abs_diff),
        "predictions_unchanged": bool(prediction_mismatches == 0 and distribution_max_abs_diff <= 1e-12),
        "true_history_scope_metrics": _scope_metrics(true_rows),
        "scrambled_history_scope_metrics": _scope_metrics(scrambled_rows),
        "digests": {
            "true_history": _result_digest(true_rows),
            "scrambled_history": _result_digest(scrambled_rows),
        },
        "wall_clock_seconds": time.perf_counter() - start,
    }


def _run_posterior_independence(
    design: Mapping[str, Any],
    spec: Any,
    users: Sequence[UserData],
) -> dict[str, Any]:
    start = time.perf_counter()
    rng = np.random.Generator(np.random.PCG64(2026070502))
    rows_zero: list[dict[str, Any]] = []
    rows_after_true: list[dict[str, Any]] = []
    rows_after_random: list[dict[str, Any]] = []
    action_comparisons: list[dict[str, Any]] = []
    for user in users:
        zero_filter = _filter_for_user(design, spec, user.user_id, user.style_map)
        true_filter = _filter_for_user(design, spec, user.user_id, user.style_map, context_suffix=":after_true")
        random_filter = _filter_for_user(design, spec, user.user_id, user.style_map, context_suffix=":after_random")
        for record in user.records:
            action = str(record["action"])
            target = int(record["observation"]["symbol"])
            true_filter.observe(PrefixEvent(action=action, symbol=target))
            random_filter.observe(PrefixEvent(action=action, symbol=int(rng.integers(0, 32))))
        for action in zero_filter.simulator.all_actions:
            zero = zero_filter.predict_distribution(action)
            after_true = true_filter.predict_distribution(action)
            after_random = random_filter.predict_distribution(action)
            pred_zero = int(np.argmax(np.asarray(zero, dtype=float)))
            pred_after_true = int(np.argmax(np.asarray(after_true, dtype=float)))
            pred_after_random = int(np.argmax(np.asarray(after_random, dtype=float)))
            action_comparisons.append(
                {
                    "user_id": int(user.user_id),
                    "action": str(action),
                    "zero_prediction": pred_zero,
                    "after_true_prediction": pred_after_true,
                    "after_random_prediction": pred_after_random,
                    "zero_vs_after_true_max_abs_diff": float(
                        np.max(np.abs(np.asarray(zero, dtype=float) - np.asarray(after_true, dtype=float)))
                    ),
                    "zero_vs_after_random_max_abs_diff": float(
                        np.max(np.abs(np.asarray(zero, dtype=float) - np.asarray(after_random, dtype=float)))
                    ),
                }
            )
        for record in user.records:
            action = str(record["action"])
            target = int(record["observation"]["symbol"])
            for label, filt, sink in (
                ("zero_observations", zero_filter, rows_zero),
                ("after_true_history", true_filter, rows_after_true),
                ("after_random_history", random_filter, rows_after_random),
            ):
                distribution = filt.predict_distribution(action)
                sink.append(
                    {
                        "test_id": "T4",
                        "posterior_state": label,
                        "user_id": int(user.user_id),
                        "step_index": int(record["step_index"]),
                        "action": action,
                        "prediction": int(np.argmax(np.asarray(distribution, dtype=float))),
                        "target": target,
                        "is_recommend_turn": action == "recommend",
                    }
                )
    max_true = max(float(row["zero_vs_after_true_max_abs_diff"]) for row in action_comparisons)
    max_random = max(float(row["zero_vs_after_random_max_abs_diff"]) for row in action_comparisons)
    prediction_mismatches_true = sum(
        int(row["zero_prediction"] != row["after_true_prediction"]) for row in action_comparisons
    )
    prediction_mismatches_random = sum(
        int(row["zero_prediction"] != row["after_random_prediction"]) for row in action_comparisons
    )
    return {
        "test_id": "T4",
        "producer_function": "s3d_null_ideal_diag_001a._run_posterior_independence",
        "input_artifacts": [str(FROZEN_DESIGN.relative_to(ROOT))],
        "run_user_ids": [int(user.user_id) for user in users],
        "actions_compared_per_user": len(users[0].records) if False else len(action_comparisons) // max(len(users), 1),
        "max_zero_vs_after_true_distribution_abs_diff": float(max_true),
        "max_zero_vs_after_random_distribution_abs_diff": float(max_random),
        "prediction_mismatches_zero_vs_after_true": int(prediction_mismatches_true),
        "prediction_mismatches_zero_vs_after_random": int(prediction_mismatches_random),
        "posterior_independent": bool(
            max_true <= 1e-12
            and max_random <= 1e-12
            and prediction_mismatches_true == 0
            and prediction_mismatches_random == 0
        ),
        "action_comparison_digest": _sha256_json(action_comparisons),
        "zero_observations_scope_metrics": _scope_metrics(rows_zero),
        "after_true_history_scope_metrics": _scope_metrics(rows_after_true),
        "after_random_history_scope_metrics": _scope_metrics(rows_after_random),
        "digests": {
            "zero_observations": _result_digest(rows_zero),
            "after_true_history": _result_digest(rows_after_true),
            "after_random_history": _result_digest(rows_after_random),
        },
        "wall_clock_seconds": time.perf_counter() - start,
    }


def _expected_macro_from_distributions(items: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    totals = np.zeros(32, dtype=float)
    correct = np.zeros(32, dtype=float)
    micro_numerator = 0.0
    for item in items:
        distribution = np.asarray(item["distribution"], dtype=float)
        prediction = int(item["prediction"])
        totals += distribution
        correct[prediction] += float(distribution[prediction])
        micro_numerator += float(distribution[prediction])
    present = totals > 0.0
    return {
        "expected_macro_balanced_accuracy": 0.0 if not bool(np.any(present)) else float(np.mean(correct[present] / totals[present])),
        "expected_micro_accuracy": 0.0 if not items else float(micro_numerator / len(items)),
        "expected_totals_present_classes": int(np.sum(present)),
    }


def _analytic_items_for_users(
    design: Mapping[str, Any],
    spec: Any,
    users: Sequence[UserData],
    *,
    style_variant: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    simulator = FspPumSimulator(design, master_seed=int(spec.master_seed), variant=str(spec.variant))
    internal_recommend_center = int((simulator.all_actions.index("recommend") * 5) % simulator.alphabet_size)
    all_items: list[dict[str, Any]] = []
    recommend_items: list[dict[str, Any]] = []
    centers: dict[str, int] = {}
    for user in users:
        prediction_style = user.style_map if style_variant == "true" else _wrong_style_map(user.style_map)
        centers[str(user.user_id)] = int(prediction_style[internal_recommend_center])
        for record in user.records:
            action = str(record["action"])
            base = np.asarray(simulator._action_only_distribution(action), dtype=float)
            true_surface = np.zeros(simulator.alphabet_size, dtype=float)
            prediction_surface = np.zeros(simulator.alphabet_size, dtype=float)
            for internal_symbol, probability in enumerate(base):
                true_surface[user.style_map[internal_symbol]] = float(probability)
                prediction_surface[prediction_style[internal_symbol]] = float(probability)
            prediction = int(np.argmax(prediction_surface))
            item = {
                "user_id": int(user.user_id),
                "step_index": int(record["step_index"]),
                "action": action,
                "prediction": prediction,
                "distribution": true_surface.tolist(),
            }
            all_items.append(item)
            if action == "recommend":
                recommend_items.append(item)
    return all_items, recommend_items, centers


def _analytic_metric_block(
    design: Mapping[str, Any],
    spec: Any,
    users: Sequence[UserData],
    *,
    style_variant: str,
    label: str,
) -> dict[str, Any]:
    all_items, recommend_items, centers = _analytic_items_for_users(
        design,
        spec,
        users,
        style_variant=style_variant,
    )
    return {
        "label": label,
        "style_variant": style_variant,
        "user_count": len(users),
        "run_user_ids": [int(user.user_id) for user in users],
        "overall_expected": _expected_macro_from_distributions(all_items),
        "recommend_turn_conditional_expected": _expected_macro_from_distributions(recommend_items),
        "recommend_turn_count": len(recommend_items),
        "recommend_surface_centers_by_user": centers,
        "distinct_recommend_surface_center_count": len(set(centers.values())),
        "distinct_recommend_surface_centers": sorted(set(centers.values())),
        "analytic_items_digest": {
            "overall": _sha256_json(
                [
                    {k: v for k, v in item.items() if k != "distribution"}
                    for item in all_items
                ]
            ),
            "recommend": _sha256_json(
                [
                    {k: v for k, v in item.items() if k != "distribution"}
                    for item in recommend_items
                ]
            ),
        },
    }


def _run_analytic_quantification(
    design: Mapping[str, Any],
    spec: Any,
    users: Sequence[UserData],
    t1_scope_metrics: Mapping[str, Any],
) -> dict[str, Any]:
    start = time.perf_counter()
    simulator = FspPumSimulator(design, master_seed=int(spec.master_seed), variant=str(spec.variant))
    internal_recommend_centers: dict[str, int] = {}
    for action in simulator.recommend_actions:
        internal_recommend_centers[str(action)] = int((simulator.all_actions.index(action) * 5) % simulator.alphabet_size)

    selected_true = _analytic_metric_block(
        design,
        spec,
        users,
        style_variant="true",
        label="selected_users_true_style",
    )
    selected_wrong = _analytic_metric_block(
        design,
        spec,
        users,
        style_variant="wrong_derangement",
        label="selected_users_wrong_derangement",
    )

    eval_range_users = [
        _load_user_data(design, spec, user_id)
        for user_id in range(int(spec.eval_user_range[0]), int(spec.eval_user_range[1]) + 1)
    ]
    eval_range_true = _analytic_metric_block(
        design,
        spec,
        eval_range_users,
        style_variant="true",
        label="eval_range_640_799_true_style_schedule_analytic",
    )
    eval_range_wrong = _analytic_metric_block(
        design,
        spec,
        eval_range_users,
        style_variant="wrong_derangement",
        label="eval_range_640_799_wrong_derangement_schedule_analytic",
    )

    eval_range_center_histogram: Counter[int] = Counter()
    for value in eval_range_true["recommend_surface_centers_by_user"].values():
        eval_range_center_histogram[int(value)] += 1
    overall_expected = selected_true["overall_expected"]
    recommend_expected = selected_true["recommend_turn_conditional_expected"]
    actual_overall = float(t1_scope_metrics["overall"]["metric"])
    actual_recommend = t1_scope_metrics["recommend_turn_conditional"]["metric"]
    return {
        "test_id": "T5",
        "producer_function": "s3d_null_ideal_diag_001a._run_analytic_quantification",
        "input_artifacts": [str(FROZEN_DESIGN.relative_to(ROOT))],
        "run_user_ids": [int(user.user_id) for user in users],
        "predictor_definition": "argmax of NULL_env _action_only_distribution(action) after true per-user style_map surface remap",
        "scope_metrics": {
            "overall_expected": overall_expected,
            "recommend_turn_conditional_expected": recommend_expected,
            "actual_t1_overall_metric": actual_overall,
            "actual_t1_recommend_turn_conditional_metric": actual_recommend,
            "t1_minus_expected_overall_macro": float(actual_overall - overall_expected["expected_macro_balanced_accuracy"]),
            "t1_minus_expected_recommend_macro": None
            if actual_recommend is None
            else float(float(actual_recommend) - recommend_expected["expected_macro_balanced_accuracy"]),
            "style_variant_expected_metrics": {
                "selected_users_true_style": selected_true,
                "selected_users_wrong_derangement": selected_wrong,
                "eval_range_640_799_true_style_schedule_analytic": eval_range_true,
                "eval_range_640_799_wrong_derangement_schedule_analytic": eval_range_wrong,
            },
            "reference_voided_null_ideal_minus_eval_range_true_expected_overall": float(
                REFERENCE_VOIDED_NULL_IDEAL
                - eval_range_true["overall_expected"]["expected_macro_balanced_accuracy"]
            ),
        },
        "recommend_action_variant_enumeration": {
            "recommend_action_variant_count": len(simulator.recommend_actions),
            "recommend_actions": list(simulator.recommend_actions),
            "internal_centers_by_action": internal_recommend_centers,
            "selected_user_surface_centers_by_user": selected_true["recommend_surface_centers_by_user"],
            "selected_user_distinct_surface_center_count": selected_true["distinct_recommend_surface_center_count"],
            "selected_user_distinct_surface_centers": selected_true["distinct_recommend_surface_centers"],
            "eval_range_640_799_style_only_distinct_surface_center_count": len(eval_range_center_histogram),
            "eval_range_640_799_style_only_surface_center_histogram": {
                str(k): int(v) for k, v in sorted(eval_range_center_histogram.items())
            },
            "single_mode_wrinkle_resolution": (
                "There is one internal recommend action center, but the true per-user style_map remaps "
                "that internal center to different surface symbols across users; the pooled scorer is "
                "therefore not a single posterior-independent surface-mode predictor."
            ),
        },
        "wall_clock_seconds": time.perf_counter() - start,
    }


def _decide_verdict(t2: Mapping[str, Any], t3: Mapping[str, Any], t4: Mapping[str, Any], t5: Mapping[str, Any]) -> dict[str, Any]:
    t3_overall = float(t3["scope_metrics"]["overall"]["metric"])
    t3_recommend = t3["scope_metrics"]["recommend_turn_conditional"]["metric"]
    t2_ok = bool(t2["predictions_unchanged"])
    t4_ok = bool(t4["posterior_independent"])
    analytic_gap = abs(float(t5["scope_metrics"]["t1_minus_expected_overall_macro"]))
    t3_overall_chance = t3_overall <= NULL_LIMIT
    if t3_overall_chance and t2_ok and t4_ok:
        verdict = "RESIDUAL_ACTION_STRUCTURE_VIA_STYLEMAP"
        branch = "wrong-style overall chance and history/posterior independent"
    elif (not t3_overall_chance) or (not t2_ok) or (not t4_ok):
        verdict = "GENUINE_LEAKAGE_PATH"
        branch = "wrong-style overall above chance or history/posterior dependence"
    else:
        verdict = "UNEXPLAINED_RESIDUAL"
        branch = "decision table not cleanly satisfied"
    return {
        "verdict": verdict,
        "decision_branch": branch,
        "decision_scope": "canonical NULL overall metric; recommend-turn-conditional reported separately because small selected-user samples can be finite-support inflated",
        "chance": CHANCE,
        "chance_plus_margin": NULL_LIMIT,
        "t3_wrong_style_overall_metric": t3_overall,
        "t3_wrong_style_overall_at_or_below_chance_plus_margin": bool(t3_overall_chance),
        "t3_wrong_style_recommend_metric": t3_recommend,
        "t2_predictions_unchanged": t2_ok,
        "t4_posterior_independent": t4_ok,
        "t5_t1_minus_expected_overall_abs": analytic_gap,
        "t5_overall_large_gap_flag": bool(analytic_gap > 0.02),
    }


def _findings_md(result: Mapping[str, Any]) -> str:
    decision = result["decision"]
    t1 = result["tests"]["T1_reproduce_true_style"]
    t2 = result["tests"]["T2_history_independence"]
    t3 = result["tests"]["T3_wrong_style_map"]
    t4 = result["tests"]["T4_posterior_independence"]
    t5 = result["tests"]["T5_analytic_quantification"]
    t5_variants = t5["scope_metrics"]["style_variant_expected_metrics"]
    full_true = t5_variants["eval_range_640_799_true_style_schedule_analytic"]
    full_wrong = t5_variants["eval_range_640_799_wrong_derangement_schedule_analytic"]
    return f"""# {TASK_ID} findings

Verdict: `{decision["verdict"]}`.

Branch fired: {decision["decision_branch"]}.  Decision scope: {decision["decision_scope"]}.

Numbers:
- T1 TRUE style_map overall = {t1["scope_metrics"]["overall"]["metric"]:.12f}; recommend = {t1["scope_metrics"]["recommend_turn_conditional"]["metric"]}.
- T3 WRONG style_map overall = {t3["scope_metrics"]["overall"]["metric"]:.12f}; recommend = {t3["scope_metrics"]["recommend_turn_conditional"]["metric"]}.
- T2 history-independence max distribution diff = {t2["max_distribution_abs_diff"]:.3g}; prediction mismatches = {t2["prediction_mismatches"]}.
- T4 posterior-independence max zero-vs-after-true diff = {t4["max_zero_vs_after_true_distribution_abs_diff"]:.3g}; max zero-vs-after-random diff = {t4["max_zero_vs_after_random_distribution_abs_diff"]:.3g}.
- T5 expected overall macro = {t5["scope_metrics"]["overall_expected"]["expected_macro_balanced_accuracy"]:.12f}; T1-minus-expected overall = {t5["scope_metrics"]["t1_minus_expected_overall_macro"]:.12f}.
- T5 eval-range analytic TRUE style overall/recommend = {full_true["overall_expected"]["expected_macro_balanced_accuracy"]:.12f} / {full_true["recommend_turn_conditional_expected"]["expected_macro_balanced_accuracy"]:.12f}.
- T5 eval-range analytic WRONG style overall/recommend = {full_wrong["overall_expected"]["expected_macro_balanced_accuracy"]:.12f} / {full_wrong["recommend_turn_conditional_expected"]["expected_macro_balanced_accuracy"]:.12f}.

Scope resolution: T5 found {t5["recommend_action_variant_enumeration"]["recommend_action_variant_count"]} internal recommend action variant with internal center {t5["recommend_action_variant_enumeration"]["internal_centers_by_action"]}.  The selected users had surface centers {t5["recommend_action_variant_enumeration"]["selected_user_surface_centers_by_user"]}; style-only enumeration over eval users 640..799 had {t5["recommend_action_variant_enumeration"]["eval_range_640_799_style_only_distinct_surface_center_count"]} distinct surface centers.  Thus the pooled recommend scorer is not a single fixed surface-mode predictor even though the posterior is independent.

Fix class only, not implemented here: A) env-response-uniform would remove NULL_env action-conditioned residual structure; B) guard-floor-redefine would redefine the NULL guard floor to allow action-conditioned style_map privilege.  This diagnostic does not choose or implement either fix.
"""


def main() -> int:
    run_started_at = _utc_timestamp()
    start = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    design = load_frozen_design(FROZEN_DESIGN)
    spec = next(item for item in build_s3d_cert_set_specs(design) if item.cell_id == "NULL_env")

    primary_user = _load_user_data(design, spec, 640)
    primary_recommend_count = sum(1 for record in primary_user.records if str(record["action"]) == "recommend")
    selected_user_ids = [640]
    user_selection_reason = "primary eval user 640"
    if primary_recommend_count < 10:
        selected_user_ids = [640, 641, 642]
        user_selection_reason = (
            "eval user 640 has only "
            f"{primary_recommend_count} recommend turns, so 641 and 642 were added to avoid an underpowered "
            "recommend-turn scope diagnostic; no heldout users 800-999 are touched"
        )
    users_by_id = {640: primary_user}
    for user_id in selected_user_ids:
        if user_id not in users_by_id:
            users_by_id[user_id] = _load_user_data(design, spec, user_id)
    users = [users_by_id[user_id] for user_id in selected_user_ids]

    trace_rows: list[dict[str, Any]] = []
    t1 = _score_ideal(design, spec, users, test_id="T1", style_variant="true", trace_rows=trace_rows)
    t3 = _score_ideal(design, spec, users, test_id="T3", style_variant="wrong_derangement", trace_rows=trace_rows)
    t2 = _run_history_independence(design, spec, users)
    t4 = _run_posterior_independence(design, spec, users)
    t5 = _run_analytic_quantification(design, spec, users, t1["scope_metrics"])
    t6 = {
        "test_id": "T6",
        "status": "skipped",
        "reason": "optional member-with-style_map diagnostic not needed after T2/T3/T4/T5 isolated the channel",
    }

    decision = _decide_verdict(t2, t3, t4, t5)
    code_hash = _code_path_hash()
    result = {
        "task_id": TASK_ID,
        "layer": "instrument diagnostic",
        "cell": "NULL_env",
        "variant": str(spec.variant),
        "run_id": f"{TASK_ID}:{run_started_at}",
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "wall_clock_seconds": time.perf_counter() - start,
        "input_artifacts": [str(FROZEN_DESIGN.relative_to(ROOT))],
        "source_files_imported": [
            "src/fsp_pum_env/factored_filter.py",
            "src/fsp_pum_env/simulator.py",
            "src/fsp_pum_env/s3d_certificates.py",
            "src/fsp_pum_env/trajectory_sets.py",
            "src/fsp_pum_env/ideal_observer.py",
        ],
        "producer_function": "s3d_null_ideal_diag_001a.main",
        "code_path_hash": code_hash,
        "chance": CHANCE,
        "chance_plus_margin": NULL_LIMIT,
        "reference_voided_null_ideal_metric": REFERENCE_VOIDED_NULL_IDEAL,
        "selected_user_ids": selected_user_ids,
        "user_selection_reason": user_selection_reason,
        "heldout_users_800_999_touched": False,
        "frozen_spec_or_runner_or_src_edited": False,
        "tests": {
            "T1_reproduce_true_style": t1,
            "T2_history_independence": t2,
            "T3_wrong_style_map": t3,
            "T4_posterior_independence": t4,
            "T5_analytic_quantification": t5,
            "T6_member_with_style_map": t6,
        },
        "decision": decision,
        "claim_ceiling": "NULL-env ideal false-headroom diagnostic only; no S3d fix, no gate pass, no mechanism-validity, no EGO mainline, no agency, no consciousness claim",
    }

    for key, payload in result["tests"].items():
        if isinstance(payload, dict):
            payload.setdefault("code_path_hash", code_hash)

    with TRACE_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        for row in trace_rows:
            handle.write(json.dumps(_jsonable(row), sort_keys=True, separators=(",", ":")) + "\n")
    result["trace_jsonl"] = {
        "path": str(TRACE_PATH.relative_to(ROOT)),
        "row_count": len(trace_rows),
        "sha256": _sha256_bytes(TRACE_PATH.read_bytes()),
        "contains_tests": ["T1", "T3"],
    }
    _write_json_roundtrip(RESULT_PATH, result)
    _write_text(FINDINGS_PATH, _findings_md(result))
    print(json.dumps({"verdict": decision["verdict"], "result": str(RESULT_PATH), "trace": str(TRACE_PATH)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
