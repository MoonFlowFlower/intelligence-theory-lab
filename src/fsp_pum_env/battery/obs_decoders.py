"""S3c observation-decoder battery members and compute projection helpers."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import hashlib
import inspect
import json
import os
from pathlib import Path
import time
from typing import Any, Iterable, Mapping, Sequence

for _S3C_THREAD_ENV_VAR in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_S3C_THREAD_ENV_VAR] = "1"

import numpy as np
from scipy import sparse
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score

from src.fsp_pum_env import trajectory_sets as trajectory_sets_module
from src.fsp_pum_env.trajectory_sets import TrajectorySetSpec

from .base import (
    PrefixEvent,
    Prediction,
    distribution_from_counts,
    event_from_mapping,
    frozen_action_list,
    prediction_for_all_actions,
    response_alphabet_size,
)


DECODER_MEMBER_NAMES = ["obs_decoder_logreg", "obs_decoder_gbt", "obs_decoder_gru"]
S3C_CPU_HOUR_LIMIT = 24.0
S3C_R3_CPU_HOUR_LIMIT = 30.0
TRAIN_FIT_USER_MAX = 639
INTERNAL_VALIDATION_USER_MIN = 640
TRAIN_USER_MAX = 799
F2_NGRAM_MIN_COUNT = 100
F2_NGRAM_VOCABULARY_SIZE = 1024
S3C_COST_CLASSES = ("logreg_F1", "logreg_F2", "gbt", "gru", "seq_full", "seq_W15")
S3C_R2_CONFIG_COUNTS_BY_CLASS = {
    "logreg_F1": 4,
    "logreg_F2": 4,
    "gbt": 8,
    "gru": 8,
    "seq_full": 8,
    "seq_W15": 8,
}
S3C_THREAD_ENV_VARS = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS")
_S3C_THREADPOOL_LIMIT_CONTEXT: Any | None = None


@dataclass
class _PrefixFeatureState:
    alphabet_size: int
    prefix_len: int = 0
    counts: np.ndarray = field(init=False)
    session_counts: np.ndarray = field(init=False)
    transitions: dict[tuple[int, int], int] = field(default_factory=dict)
    ngram_counts: Counter[tuple[int, ...]] = field(default_factory=Counter)
    session_symbols: list[int] = field(default_factory=list)
    last_symbol: int | None = None

    def __post_init__(self) -> None:
        self.counts = np.zeros(self.alphabet_size, dtype=np.float64)
        self.session_counts = np.zeros(self.alphabet_size, dtype=np.float64)

    def observe(self, event: PrefixEvent) -> None:
        symbol = int(event.observation["symbol"])
        if event.session_boundary == "start":
            self.session_counts = np.zeros(self.alphabet_size, dtype=np.float64)
            self.session_symbols = []
            self.last_symbol = None
        if self.last_symbol is not None:
            key = (int(self.last_symbol), symbol)
            self.transitions[key] = self.transitions.get(key, 0) + 1
        self.counts[symbol] += 1.0
        self.session_counts[symbol] += 1.0
        self.session_symbols.append(symbol)
        for ngram_size in (1, 2, 3):
            if len(self.session_symbols) >= ngram_size:
                self.ngram_counts[tuple(self.session_symbols[-ngram_size:])] += 1
        self.prefix_len += 1
        self.last_symbol = symbol


class ObsDecoderLogRegPredictor:
    name = "obs_decoder_logreg"

    def __init__(self, alphabet_size: int):
        self.alphabet_size = int(alphabet_size)
        self.prefix_events: list[PrefixEvent] = []
        self._counts = [0.0] * self.alphabet_size

    @classmethod
    def from_design(cls, design: Mapping[str, Any]) -> "ObsDecoderLogRegPredictor":
        _require_member(design, cls.name)
        return cls(response_alphabet_size(design))

    def observe(self, event: PrefixEvent | Mapping[str, Any]) -> None:
        parsed = event_from_mapping(event)
        self.prefix_events.append(parsed)
        self._counts[int(parsed.observation["symbol"])] += 1.0

    def predict(self, counterfactual_actions: Sequence[str]) -> Prediction:
        distribution = distribution_from_counts(self._counts)
        return prediction_for_all_actions(counterfactual_actions, distribution)


class ObsDecoderGbtPredictor(ObsDecoderLogRegPredictor):
    name = "obs_decoder_gbt"


class ObsDecoderGruPredictor(ObsDecoderLogRegPredictor):
    name = "obs_decoder_gru"


def s3c_split_for_user(user_id: int) -> str:
    uid = int(user_id)
    if 0 <= uid <= TRAIN_FIT_USER_MAX:
        return "fit"
    if INTERNAL_VALIDATION_USER_MIN <= uid <= TRAIN_USER_MAX:
        return "internal_validation"
    raise ValueError(f"heldout user_id {uid} is forbidden for S3c fitting, tuning, early stopping, and selection")


def validate_s3c_training_user_id(user_id: int, *, phase: str) -> None:
    split = s3c_split_for_user(user_id)
    if phase == "fit" and split != "fit":
        raise ValueError(f"user_id {int(user_id)} belongs to {split}, not fit")
    if phase in {"internal_validation", "validation"} and split != "internal_validation":
        raise ValueError(f"user_id {int(user_id)} belongs to {split}, not internal_validation")
    if phase not in {"fit", "internal_validation", "validation", "any_train"}:
        raise ValueError(f"unsupported S3c phase: {phase}")


def gbt_fit_user_ids() -> tuple[int, ...]:
    return tuple(range(0, TRAIN_FIT_USER_MAX + 1, 2))


def configure_s3c_single_thread_cpu_environment() -> dict[str, Any]:
    global _S3C_THREADPOOL_LIMIT_CONTEXT
    for key in S3C_THREAD_ENV_VARS:
        os.environ[key] = "1"
    threadpool_info_payload: list[dict[str, Any]] = []
    try:
        from threadpoolctl import threadpool_info, threadpool_limits

        if _S3C_THREADPOOL_LIMIT_CONTEXT is None:
            _S3C_THREADPOOL_LIMIT_CONTEXT = threadpool_limits(limits=1)
            _S3C_THREADPOOL_LIMIT_CONTEXT.__enter__()
        threadpool_info_payload = [
            {
                "user_api": str(item.get("user_api", "")),
                "internal_api": str(item.get("internal_api", "")),
                "num_threads": int(item.get("num_threads", -1)),
                "prefix": str(item.get("prefix", "")),
            }
            for item in threadpool_info()
        ]
    except Exception as exc:  # pragma: no cover - environment-specific guard detail
        threadpool_info_payload = [{"threadpoolctl_error": str(exc)}]
    import torch

    torch.set_num_threads(1)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        # PyTorch may reject changing interop threads after parallel work has started.
        # The sweep still records the observed value and keeps CPU device explicit.
        pass
    device = torch.device("cpu")
    if str(device) != "cpu":
        raise RuntimeError("S3c sweep must run on torch device=cpu")
    return {
        "single_thread_accounting": True,
        "env_threads": {key: os.environ.get(key, "") for key in S3C_THREAD_ENV_VARS},
        "torch_num_threads": int(torch.get_num_threads()),
        "torch_num_interop_threads": int(torch.get_num_interop_threads()),
        "torch_device": str(device),
        "threadpool_info": threadpool_info_payload,
        "cpu_hour_limit": S3C_CPU_HOUR_LIMIT,
        "r3_runtime_cpu_hour_limit": S3C_R3_CPU_HOUR_LIMIT,
    }


def build_f2_ngram_vocabulary(design: Mapping[str, Any], trajectory_manifest: Mapping[str, Any]) -> dict[str, Any]:
    counts: Counter[tuple[int, ...]] = Counter()
    sets_consumed: list[str] = []
    for entry in trajectory_manifest["sets"]:
        spec = _fit_only_spec_from_entry(entry)
        sets_consumed.append(str(entry.get("set_id", spec.set_id)))
        active_user: int | None = None
        session_symbols: list[int] = []
        start_user = int(spec.partitions["train"]["start_user_id"])
        for _, trajectory_ordinal, record, _ in trajectory_sets_module._iter_records_with_adjudicator(design, spec):
            user_id = start_user + int(trajectory_ordinal)
            validate_s3c_training_user_id(user_id, phase="fit")
            parsed = event_from_mapping(record)
            if active_user != user_id or parsed.session_boundary == "start":
                active_user = user_id
                session_symbols = []
            symbol = int(parsed.observation["symbol"])
            session_symbols.append(symbol)
            for ngram_size in (1, 2, 3):
                if len(session_symbols) >= ngram_size:
                    counts[tuple(session_symbols[-ngram_size:])] += 1

    ranked = [
        (ngram, count)
        for ngram, count in counts.items()
        if int(count) >= F2_NGRAM_MIN_COUNT
    ]
    ranked.sort(key=lambda item: (-int(item[1]), _ngram_key(item[0])))
    selected = ranked[:F2_NGRAM_VOCABULARY_SIZE]
    if len(selected) != F2_NGRAM_VOCABULARY_SIZE:
        raise RuntimeError(
            f"001B F2 vocabulary requires {F2_NGRAM_VOCABULARY_SIZE} n-grams with pooled fit count >= "
            f"{F2_NGRAM_MIN_COUNT}; found {len(selected)}"
        )
    payload = {
        "artifact": "f2_ngram_vocabulary",
        "task_id": "FSP-PUM-ENV-IDPROBE-001A",
        "stage": "S3c-R2",
        "spec": "FSP-PUM-ENV-IDPROBE-001A-S3C-BATTERY-SPEC-001B Amendment 1",
        "fit_user_range": [0, TRAIN_FIT_USER_MAX],
        "excluded_user_ranges": {
            "internal_validation": [INTERNAL_VALIDATION_USER_MIN, TRAIN_USER_MAX],
            "heldout": [TRAIN_USER_MAX + 1, 999],
        },
        "sets_consumed": sets_consumed,
        "min_pooled_fit_count": F2_NGRAM_MIN_COUNT,
        "max_vocabulary_size": F2_NGRAM_VOCABULARY_SIZE,
        "ranking": "pooled fit count descending; tie-break lexicographic n-gram key",
        "ngrams": [
            {
                "index": index,
                "key": _ngram_key(ngram),
                "symbols": [int(symbol) for symbol in ngram],
                "pooled_fit_count": int(count),
            }
            for index, (ngram, count) in enumerate(selected)
        ],
        "claim_ceiling": "F2 vocabulary construction only; no tuning, heldout, environment-validity, baseline-power, mechanism, learning-capability, agency, or EGO claim",
    }
    payload["sha256"] = _payload_sha256(payload)
    return payload


def write_f2_ngram_vocabulary(
    frozen_design_path: str | Path,
    trajectory_manifest_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    start = time.perf_counter()
    run_started_at = _utc_timestamp()
    design = _read_json(frozen_design_path)
    manifest = _read_json(trajectory_manifest_path)
    payload = build_f2_ngram_vocabulary(design, manifest)
    payload["producer_function"] = "src.fsp_pum_env.battery.obs_decoders.write_f2_ngram_vocabulary"
    payload["input_artifacts"] = [str(frozen_design_path), str(trajectory_manifest_path)]
    payload["code_path_hash"] = s3c_code_hash()
    payload["run_id"] = f"s3c-f2-vocabulary-{run_started_at}"
    payload["run_started_at"] = run_started_at
    payload["run_finished_at"] = _utc_timestamp()
    payload["build_wall_clock_seconds"] = time.perf_counter() - start
    payload["sha256"] = _payload_sha256(payload)
    _write_json(output_path, payload)
    return payload


def decoder_grid(member_name: str) -> list[dict[str, Any]]:
    if member_name == "obs_decoder_logreg":
        rows = []
        for features in ("F1", "F2"):
            for c_value in (0.01, 0.1, 1.0, 10.0):
                rows.append(
                    {
                        "member": member_name,
                        "config_index": len(rows),
                        "config_id": f"{member_name}_cfg{len(rows):02d}",
                        "framework": "sklearn.linear_model.LogisticRegression",
                        "features": features,
                        "solver": "lbfgs",
                        "max_iter": 200,
                        "C": float(c_value),
                    }
                )
        return rows
    if member_name == "obs_decoder_gbt":
        rows = []
        for learning_rate in (0.05, 0.1):
            for max_iter in (100, 300):
                for max_leaf_nodes in (31, 63):
                    rows.append(
                        {
                            "member": member_name,
                            "config_index": len(rows),
                            "config_id": f"{member_name}_cfg{len(rows):02d}",
                            "framework": "sklearn.ensemble.HistGradientBoostingClassifier",
                            "features": "F2",
                            "learning_rate": float(learning_rate),
                            "max_iter": int(max_iter),
                            "max_leaf_nodes": int(max_leaf_nodes),
                        }
                    )
        return rows
    if member_name == "obs_decoder_gru":
        return _gru_grid(member_name)
    raise ValueError(f"unknown S3c decoder member: {member_name}")


def feature_map_summary(design: Mapping[str, Any]) -> dict[str, Any]:
    alphabet_size = response_alphabet_size(design)
    action_count = len(frozen_action_list(design))
    f1_dimension = alphabet_size + alphabet_size + alphabet_size * alphabet_size + alphabet_size + action_count
    return {
        "F1": {
            "families": [
                "prefix_symbol_counts",
                "prefix_symbol_rates",
                "first_order_transition_counts",
                "last_symbol_one_hot",
                "candidate_action_one_hot",
            ],
            "dimension": int(f1_dimension),
            "sparse": True,
        },
        "F2": {
            "families": [
                "F1",
                "thresholded_within_session_ngram_counts_n_le_3",
            ],
            "dimension": int(f1_dimension + F2_NGRAM_VOCABULARY_SIZE),
            "ngram_dimension": int(F2_NGRAM_VOCABULARY_SIZE),
            "definition": "001B Amendment 1: pooled FIT-user count >=100, ranked by count, top 1024, lexicographic tie-break",
            "sparse_for_logreg": True,
            "dense_required_by_hist_gradient_boosting": True,
        },
    }


def write_s3c_compute_projection(
    frozen_design_path: str | Path,
    trajectory_manifest_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    run_started_at = _utc_timestamp()
    start = time.perf_counter()
    design = _read_json(frozen_design_path)
    manifest = _read_json(trajectory_manifest_path)
    _require_frameworks()
    measurement = _measure_cheapest_logreg_one_set(design, manifest)
    feature_maps = feature_map_summary(design)
    weights = _projection_weights(feature_maps)
    projected_seconds = float(measurement["fit_plus_validation_wall_clock_seconds"]) * float(weights["total_equivalent_one_set_multiplier"])
    projected_cpu_hours = projected_seconds / 3600.0
    report = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S3c",
        "artifact": "s3c_compute_projection",
        "claim_ceiling": "PART 0 compute projection only; no tuning, scoring, baseline-power, gap, headroom, mechanism, learning-capability, agency, or EGO claim",
        "decision_rule": "projection_cpu_hours <= 24.0 permits the frozen S3c sweep; >24.0 triggers STOP",
        "decision": "stop_projection_exceeds_24_cpu_hours" if projected_cpu_hours > S3C_CPU_HOUR_LIMIT else "projection_within_24_cpu_hours",
        "cpu_hour_limit": S3C_CPU_HOUR_LIMIT,
        "projection_cpu_hours": projected_cpu_hours,
        "projection_seconds": projected_seconds,
        "measured_cheapest_config": measurement,
        "projection_weights": weights,
        "feature_maps": feature_maps,
        "framework_versions": framework_versions(),
        "input_artifacts": [str(frozen_design_path), str(trajectory_manifest_path)],
        "producer_function": "src.fsp_pum_env.battery.obs_decoders.write_s3c_compute_projection",
        "code_path_hash": s3c_code_hash(),
        "run_id": f"s3c-compute-projection-{run_started_at}",
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "wall_clock_seconds": time.perf_counter() - start,
    }
    _write_json(output_path, report)
    return report


def write_s3c_compute_projection_v2(
    frozen_design_path: str | Path,
    trajectory_manifest_path: str | Path,
    vocabulary_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    run_started_at = _utc_timestamp()
    start = time.perf_counter()
    environment = configure_s3c_single_thread_cpu_environment()
    design = _read_json(frozen_design_path)
    manifest = _read_json(trajectory_manifest_path)
    _require_frameworks()
    vocabulary = _read_json(vocabulary_path)
    one_time_costs = {
        "vocabulary_build_seconds": float(vocabulary.get("build_wall_clock_seconds", 0.0)),
        "data_materialization_seconds": 0.0,
    }
    measurements = {
        cost_class: measure_s3c_cost_class_one_set(design, manifest, cost_class, vocabulary)
        for cost_class in S3C_COST_CLASSES
    }
    projection = project_s3c_r2_from_measurements(measurements, one_time_costs)
    report = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S3c-R2",
        "artifact": "s3c_compute_projection_v2",
        "claim_ceiling": "PART 0 v2 compute projection only; no tuning scores, heldout numbers, environment-validity, baseline-power, gap, headroom, mechanism, learning-capability, agency, or EGO claim",
        "decision_rule": "projection_cpu_hours <= 24.0 permits the frozen S3c sweep; >24.0 triggers STOP",
        "cpu_hour_limit": S3C_CPU_HOUR_LIMIT,
        "single_thread_environment": environment,
        "measurements": measurements,
        "one_time_costs": one_time_costs,
        "projection": projection,
        "projection_cpu_hours": projection["projection_cpu_hours"],
        "projection_seconds": projection["projection_seconds"],
        "decision": projection["decision"],
        "framework_versions": framework_versions(),
        "input_artifacts": [str(frozen_design_path), str(trajectory_manifest_path), str(vocabulary_path)],
        "producer_function": "src.fsp_pum_env.battery.obs_decoders.write_s3c_compute_projection_v2",
        "code_path_hash": s3c_code_hash(),
        "run_id": f"s3c-compute-projection-v2-{run_started_at}",
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "wall_clock_seconds": time.perf_counter() - start,
    }
    _write_json(output_path, report)
    return report


def project_s3c_r2_from_measurements(
    measurements: Mapping[str, Mapping[str, Any]],
    one_time_costs: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    missing = [cost_class for cost_class in S3C_COST_CLASSES if cost_class not in measurements]
    if missing:
        raise ValueError(f"missing S3c R2 measurement classes: {missing}")
    per_class_projection_seconds: dict[str, float] = {}
    for cost_class in S3C_COST_CLASSES:
        measured_seconds = float(measurements[cost_class]["fit_plus_validation_wall_clock_seconds"])
        per_class_projection_seconds[cost_class] = (
            measured_seconds * float(S3C_R2_CONFIG_COUNTS_BY_CLASS[cost_class]) * 10.0
        )
    one_time_total = float(sum(float(value) for value in (one_time_costs or {}).values()))
    projection_seconds = float(sum(per_class_projection_seconds.values()) + one_time_total)
    projection_cpu_hours = projection_seconds / 3600.0
    return {
        "cost_classes": list(S3C_COST_CLASSES),
        "config_counts_by_class": dict(S3C_R2_CONFIG_COUNTS_BY_CLASS),
        "fit_sets": 10,
        "linear_in_sets_scaling_assumption": True,
        "one_time_costs": {str(key): float(value) for key, value in (one_time_costs or {}).items()},
        "per_class_projection_seconds": per_class_projection_seconds,
        "projection_seconds": projection_seconds,
        "projection_cpu_hours": projection_cpu_hours,
        "cpu_hour_limit": S3C_CPU_HOUR_LIMIT,
        "decision": "stop_projection_exceeds_24_cpu_hours"
        if projection_cpu_hours > S3C_CPU_HOUR_LIMIT
        else "projection_within_24_cpu_hours",
    }


def s3c_sweep_config_specs() -> list[dict[str, Any]]:
    return [
        *decoder_grid("obs_decoder_logreg"),
        *decoder_grid("obs_decoder_gbt"),
        *_gru_grid("obs_decoder_gru"),
        *_gru_grid("seq_full_history_no_action_conditioning"),
        *_gru_grid("seq_window_with_action_conditioning_W15_no_cross_session_persistence"),
    ]


def build_s3c_r3_runtime_trace(
    per_config: Sequence[Mapping[str, Any]],
    *,
    wall_clock_seconds: float,
    cpu_hour_limit: float = S3C_R3_CPU_HOUR_LIMIT,
) -> dict[str, Any]:
    cumulative_seconds = 0.0
    trace: list[dict[str, Any]] = []
    for item in per_config:
        config_seconds = float(item["wall_clock_seconds"])
        cumulative_seconds += config_seconds
        cumulative_cpu_hours = cumulative_seconds / 3600.0
        trace.append(
            {
                "member": str(item["member"]),
                "config_id": str(item["config_id"]),
                "config_index": int(item["config_index"]),
                "config_wall_clock_seconds": config_seconds,
                "config_cpu_hours": config_seconds / 3600.0,
                "cumulative_cpu_hours": cumulative_cpu_hours,
                "cpu_hour_limit": float(cpu_hour_limit),
                "limit_exceeded_after_this_config": cumulative_cpu_hours > float(cpu_hour_limit),
            }
        )
    total_cpu_hours = cumulative_seconds / 3600.0
    return {
        "single_thread_accounting": True,
        "cpu_hour_limit": float(cpu_hour_limit),
        "wall_clock_seconds": float(wall_clock_seconds),
        "wall_clock_hours": float(wall_clock_seconds) / 3600.0,
        "total_sweep_wall_clock_seconds": cumulative_seconds,
        "total_sweep_cpu_hours": total_cpu_hours,
        "decision": "stop_runtime_exceeds_30_cpu_hours"
        if total_cpu_hours > float(cpu_hour_limit)
        else "runtime_within_30_cpu_hours",
        "cumulative_cpu_hours_trace": trace,
    }


def _run_s3c_configs_for_tuning(
    frozen_design_path: str | Path,
    trajectory_manifest_path: str | Path,
    vocabulary_path: str | Path,
    *,
    max_workers: int,
    start_time: float,
    runtime_failure_manifest_path: str | Path,
) -> list[dict[str, Any]]:
    worker_payloads = [
        (str(frozen_design_path), str(trajectory_manifest_path), str(vocabulary_path), str(config["config_id"]))
        for config in s3c_sweep_config_specs()
    ]
    completed: list[dict[str, Any]] = []
    if int(max_workers) <= 1:
        for payload in worker_payloads:
            completed.append(_run_s3c_config_worker(payload))
            _raise_if_r3_runtime_exceeded(completed, start_time, runtime_failure_manifest_path)
        return completed

    from concurrent.futures import ProcessPoolExecutor, as_completed

    with ProcessPoolExecutor(max_workers=int(max_workers)) as executor:
        futures = [executor.submit(_run_s3c_config_worker, payload) for payload in worker_payloads]
        for future in as_completed(futures):
            completed.append(future.result())
            _raise_if_r3_runtime_exceeded(completed, start_time, runtime_failure_manifest_path)
    return completed


def _run_s3c_config_worker(payload: tuple[str, str, str, str]) -> dict[str, Any]:
    frozen_design_path, trajectory_manifest_path, vocabulary_path, config_id = payload
    configure_s3c_single_thread_cpu_environment()
    design = _read_json(frozen_design_path)
    manifest = _read_json(trajectory_manifest_path)
    vocabulary = _read_json(vocabulary_path)
    config = _s3c_config_by_id(config_id)
    aggregators = _empty_sweep_aggregators()
    config_aggregator = {config_id: aggregators[config_id]}
    actions = frozen_action_list(design)
    alphabet_size = response_alphabet_size(design)
    for entry in manifest["sets"]:
        spec = _train_only_spec_from_entry(entry)
        events_by_split = _collect_train_events_one_set(design, spec)
        result, counts = _fit_eval_s3c_config_on_events(
            design,
            config,
            events_by_split,
            actions,
            alphabet_size=alphabet_size,
            vocabulary=vocabulary,
        )
        _update_sweep_aggregator(config_aggregator, config, result, counts, spec.set_id)
    return _finalize_sweep_config(config_aggregator[config_id])


def _fit_eval_s3c_config_on_events(
    design: Mapping[str, Any],
    config: Mapping[str, Any],
    events_by_split: Mapping[str, Mapping[int, Sequence[PrefixEvent]]],
    actions: Sequence[str],
    *,
    alphabet_size: int,
    vocabulary: Mapping[str, Any],
) -> tuple[dict[str, Any], Mapping[str, Any]]:
    config_start = time.perf_counter()
    member = str(config["member"])
    if member in {"obs_decoder_logreg", "obs_decoder_gbt"}:
        fit_user_filter = set(gbt_fit_user_ids()) if member == "obs_decoder_gbt" else None
        x_fit, y_fit, x_val, y_val, counts = _build_feature_matrices_from_user_events(
            events_by_split,
            actions,
            alphabet_size=alphabet_size,
            features=str(config["features"]),
            vocabulary=vocabulary if str(config["features"]) == "F2" else None,
            fit_user_filter=fit_user_filter,
        )
        result = _fit_eval_sklearn_config(design, config, x_fit, y_fit, x_val, y_val)
        result["model_fit_predict_wall_clock_seconds"] = float(result["fit_and_predict_wall_clock_seconds"])
        result["fit_plus_validation_wall_clock_seconds"] = time.perf_counter() - config_start
        return result, counts

    fit_sequences, val_sequences = _sequences_from_user_events(events_by_split, member)
    result = _fit_eval_gru_sequences(design, config, member, fit_sequences, val_sequences)
    result["model_fit_predict_wall_clock_seconds"] = float(result["fit_and_predict_wall_clock_seconds"])
    result["fit_plus_validation_wall_clock_seconds"] = time.perf_counter() - config_start
    return result, {}


def _s3c_config_by_id(config_id: str) -> dict[str, Any]:
    for config in s3c_sweep_config_specs():
        if str(config["config_id"]) == str(config_id):
            return dict(config)
    raise ValueError(f"unknown S3c sweep config_id: {config_id}")


def _raise_if_r3_runtime_exceeded(
    completed: Sequence[Mapping[str, Any]],
    start_time: float,
    runtime_failure_manifest_path: str | Path,
) -> None:
    trace = build_s3c_r3_runtime_trace(completed, wall_clock_seconds=time.perf_counter() - start_time)
    if trace["decision"] == "runtime_within_30_cpu_hours":
        return
    manifest = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S3c-R3",
        "artifact": "s3c_runtime_guard_failure_manifest_r3",
        "verdict": "STOP",
        "stop_condition": "cumulative measured CPU-h exceeded 30.0 after a completed config",
        "runtime_guard": trace,
        "completed_config_count": len(completed),
        "preserved_failure": True,
        "claim_ceiling": "S3c-R3 runtime guard failure only; no heldout numbers, environment-validity, baseline-power, gap, headroom, mechanism, learning-capability, agency, or EGO claim",
        "producer_function": "src.fsp_pum_env.battery.obs_decoders._raise_if_r3_runtime_exceeded",
        "code_path_hash": s3c_code_hash(),
        "run_started_at": _utc_timestamp(),
        "run_finished_at": _utc_timestamp(),
    }
    _write_json(runtime_failure_manifest_path, manifest)
    raise RuntimeError(f"STOP_RUNTIME_GUARD_EXCEEDED: wrote {runtime_failure_manifest_path}")


def _s3c_set_summaries_from_per_config(per_config: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_set: dict[str, dict[str, Any]] = {}
    for item in per_config:
        for result in item["set_results"]:
            set_id = str(result["set_id"])
            summary = by_set.setdefault(set_id, {"set_id": set_id, "configs": [], "wall_clock_seconds": 0.0})
            summary["configs"].append(
                {
                    "set_id": set_id,
                    "member": str(item["member"]),
                    "config_id": str(item["config_id"]),
                    "config_index": int(item["config_index"]),
                    "wall_clock_seconds": float(result["wall_clock_seconds"]),
                    "fit_examples": int(result["fit_examples"]),
                    "internal_validation_examples": int(result["internal_validation_examples"]),
                    "offline_compute_units": int(result["offline_compute_units"]),
                }
            )
            summary["wall_clock_seconds"] += float(result["wall_clock_seconds"])
    return [by_set[key] for key in sorted(by_set)]


def write_s3c_decoder_tuning_report(
    frozen_design_path: str | Path,
    trajectory_manifest_path: str | Path,
    vocabulary_path: str | Path,
    output_path: str | Path,
    model_dir: str | Path,
    *,
    max_workers: int = 1,
    runtime_failure_manifest_path: str | Path | None = None,
) -> dict[str, Any]:
    run_started_at = _utc_timestamp()
    start = time.perf_counter()
    environment = configure_s3c_single_thread_cpu_environment()
    per_config_completion_order = _run_s3c_configs_for_tuning(
        frozen_design_path,
        trajectory_manifest_path,
        vocabulary_path,
        max_workers=max_workers,
        start_time=start,
        runtime_failure_manifest_path=runtime_failure_manifest_path
        or Path(output_path).with_name("s3c_runtime_guard_failure_manifest_r3.json"),
    )
    config_order = {str(config["config_id"]): index for index, config in enumerate(s3c_sweep_config_specs())}
    per_config = sorted(per_config_completion_order, key=lambda item: config_order[str(item["config_id"])])
    runtime_trace = build_s3c_r3_runtime_trace(per_config_completion_order, wall_clock_seconds=time.perf_counter() - start)
    selected_configs = _select_s3c_configs(per_config)
    model_artifacts = write_s3c_model_recipes(model_dir, selected_configs, frozen_design_path, trajectory_manifest_path, vocabulary_path)
    report = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S3c-R3",
        "artifact": "s3c_decoder_tuning_report",
        "claim_ceiling": "S3c internal-validation tuning procedure only; no heldout numbers, environment-validity, baseline-power, gap, headroom, mechanism, learning-capability, agency, or EGO claim",
        "selection_rule": "highest aggregated internal-validation macro-balanced accuracy on logged-action next-symbol prediction; ties use lower config_index",
        "heldout_numbers_present": False,
        "single_thread_environment": environment,
        "runtime_guard": runtime_trace,
        "cpu_hour_limit": runtime_trace["cpu_hour_limit"],
        "total_sweep_cpu_hours": runtime_trace["total_sweep_cpu_hours"],
        "wall_clock_hours": runtime_trace["wall_clock_hours"],
        "runtime_guard_decision": runtime_trace["decision"],
        "cumulative_cpu_hours_trace": runtime_trace["cumulative_cpu_hours_trace"],
        "config_completion_order": [
            {"member": item["member"], "config_id": item["config_id"], "config_index": item["config_index"]}
            for item in per_config_completion_order
        ],
        "max_workers": int(max_workers),
        "f2_definition": "001B Amendment 1 thresholded top-1024 fit-user-only n-gram vocabulary",
        "gbt_data_budget": "fit users restricted to user_id % 2 == 0; internal validation unchanged",
        "per_config_internal_validation": sorted(per_config, key=lambda item: (item["member"], item["config_index"])),
        "selected_configs": selected_configs,
        "model_artifacts": model_artifacts,
        "set_summaries": _s3c_set_summaries_from_per_config(per_config),
        "framework_versions": framework_versions(),
        "input_artifacts": [str(frozen_design_path), str(trajectory_manifest_path), str(vocabulary_path)],
        "producer_function": "src.fsp_pum_env.battery.obs_decoders.write_s3c_decoder_tuning_report",
        "code_path_hash": s3c_code_hash(),
        "run_id": f"s3c-decoder-tuning-{run_started_at}",
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "wall_clock_seconds": time.perf_counter() - start,
    }
    _write_json(output_path, report)
    return report


def write_s3c_model_recipes(
    model_dir: str | Path,
    selected_configs: Mapping[str, Mapping[str, Any]],
    frozen_design_path: str | Path,
    trajectory_manifest_path: str | Path,
    vocabulary_path: str | Path,
) -> dict[str, Any]:
    target_dir = Path(model_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, Any] = {}
    for member, selected in selected_configs.items():
        path = target_dir / f"{member}_selected_recipe.json"
        payload = {
            "artifact": f"{member}_selected_recipe",
            "member": member,
            "selected_config": selected,
            "persistence_type": "deterministic_training_recipe",
            "reason_parameters_not_persisted": "selected multi-set fitted parameter family is treated as over the 50 MB persistence line; recipe records exact sources, config, seeds, and code hash",
            "fit_contract": "train fit users 0..639 for all ten S3a trajectory sets; GBT uses user_id % 2 == 0 fit budget",
            "input_artifacts": [str(frozen_design_path), str(trajectory_manifest_path), str(vocabulary_path)],
            "code_path_hash": s3c_code_hash(),
            "config_seed": _derive_config_seed(_read_json(frozen_design_path), str(selected["config_id"])),
            "claim_ceiling": "deterministic recipe persistence only; no model-quality or mechanism claim",
        }
        payload["sha256"] = _payload_sha256(payload)
        _write_json(path, payload)
        artifacts[member] = {"path": str(path), "sha256": payload["sha256"], "persistence_type": "deterministic_training_recipe"}
    return artifacts


def write_s3c_projection_failure_manifest(projection: Mapping[str, Any], output_path: str | Path) -> dict[str, Any]:
    manifest = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S3c",
        "artifact": "s3c_projection_failure_manifest",
        "verdict": "STOP",
        "stop_condition": "Projection > 24 CPU-h",
        "projection_cpu_hours": float(projection["projection_cpu_hours"]),
        "cpu_hour_limit": float(projection["cpu_hour_limit"]),
        "preserved_failure": True,
        "claim_ceiling": "Projection stop only; no tuning sweep, environment-validity, baseline-power, gap, headroom, mechanism, learning-capability, agency, or EGO claim",
        "input_artifacts": [str(projection.get("artifact", "s3c_compute_projection"))],
        "producer_function": "src.fsp_pum_env.battery.obs_decoders.write_s3c_projection_failure_manifest",
        "code_path_hash": s3c_code_hash(),
        "run_started_at": _utc_timestamp(),
        "run_finished_at": _utc_timestamp(),
    }
    _write_json(output_path, manifest)
    return manifest


def write_s3c_projection_failure_manifest_v2(projection: Mapping[str, Any], output_path: str | Path) -> dict[str, Any]:
    manifest = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S3c-R2",
        "artifact": "s3c_projection_failure_manifest_v2",
        "verdict": "STOP",
        "stop_condition": "Projection > 24 CPU-h",
        "projection_cpu_hours": float(projection["projection_cpu_hours"]),
        "cpu_hour_limit": float(projection["cpu_hour_limit"]),
        "preserved_failure": True,
        "prior_stop_artifacts_preserved": [
            "s3c_failure_manifest.json",
            "s3c_compute_projection.json",
            "s3c_projection_failure_manifest.json",
        ],
        "claim_ceiling": "S3c-R2 projection stop only; no tuning sweep, environment-validity, baseline-power, gap, headroom, mechanism, learning-capability, agency, or EGO claim",
        "input_artifacts": [str(projection.get("artifact", "s3c_compute_projection_v2"))],
        "producer_function": "src.fsp_pum_env.battery.obs_decoders.write_s3c_projection_failure_manifest_v2",
        "code_path_hash": s3c_code_hash(),
        "run_started_at": _utc_timestamp(),
        "run_finished_at": _utc_timestamp(),
    }
    _write_json(output_path, manifest)
    return manifest


def s3c_battery_manifest_payload(
    frozen_design_path: str | Path,
    selected_configs: Mapping[str, Any] | None = None,
    model_artifacts: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    design = _read_json(frozen_design_path)
    implemented_members = DECODER_MEMBER_NAMES + [
        "seq_full_history_no_action_conditioning",
        "seq_window_with_action_conditioning_W15_no_cross_session_persistence",
    ]
    missing = [name for name in implemented_members if name not in design["battery_membership"]["members"]]
    if missing:
        raise ValueError(f"implemented S3c member missing from frozen battery_membership: {missing}")
    return {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S3c",
        "artifact": "s3c_battery_manifest",
        "implemented_members": implemented_members,
        "fitting_contract": {
            "sets": "set_00..set_09 from S3a trajectory recipes",
            "fit_users": "user_id 0..639 within each train partition",
            "internal_validation_users": "user_id 640..799 within each train partition",
            "heldout_users": "user_id 800..999 never touched by S3c",
            "selection_rule": "highest internal-validation macro-balanced accuracy on logged-action next-symbol prediction; ties use lower config_index",
            "governing_spec": "S3C-BATTERY-SPEC-001A as amended by S3C-BATTERY-SPEC-001B and operator budget decision S3C-BATTERY-SPEC-001C",
            "f2_definition": "001B Amendment 1 thresholded top-1024 n-gram vocabulary from fit users only",
            "gbt_fit_budget": "001B Amendment 2 deterministic half of fit users, user_id % 2 == 0",
            "single_thread_accounting": True,
            "torch_device": "cpu",
            "r3_runtime_cpu_hour_limit": S3C_R3_CPU_HOUR_LIMIT,
        },
        "feature_maps": feature_map_summary(design),
        "decoder_grids": {name: decoder_grid(name) for name in DECODER_MEMBER_NAMES},
        "sequence_grids": {
            "seq_full_history_no_action_conditioning": _gru_grid("seq_full_history_no_action_conditioning"),
            "seq_window_with_action_conditioning_W15_no_cross_session_persistence": _gru_grid(
                "seq_window_with_action_conditioning_W15_no_cross_session_persistence"
            ),
        },
        "sequence_conventions": {
            "seq_full_history_no_action_conditioning": "symbol sequence only; no action fields; full user history across sessions",
            "seq_window_with_action_conditioning_W15_no_cross_session_persistence": "last 15 in-session (symbol, action) pairs; hidden state reset at every session boundary",
            "padding": "zero-embedding padding for short prefixes",
            "training": "teacher-forced one pass per user-sequence per epoch; no per-example prefix re-encoding",
        },
        "framework_versions": framework_versions(),
        "selected_configs": dict(selected_configs or {}),
        "model_artifacts": dict(model_artifacts or {}),
        "component_code_hashes": {
            "obs_decoders": _file_hash(Path(__file__)),
            "seq_models": _file_hash(Path(__file__).with_name("seq_models.py")),
            "base": _file_hash(Path(__file__).with_name("base.py")),
        },
        "code_path_hash": s3c_code_hash(),
        "claim_ceiling": "S3c instrument code and tuning-procedure metadata only; no environment-validity, baseline-power, gap, headroom, mechanism, learning-capability, agency, or EGO claim",
    }


def write_s3c_battery_manifest(
    frozen_design_path: str | Path,
    output_path: str | Path,
    selected_configs: Mapping[str, Any] | None = None,
    model_artifacts: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()
    run_started_at = _utc_timestamp()
    manifest = s3c_battery_manifest_payload(frozen_design_path, selected_configs, model_artifacts)
    manifest["producer_function"] = "src.fsp_pum_env.battery.obs_decoders.write_s3c_battery_manifest"
    manifest["run_id"] = f"s3c-battery-manifest-{run_started_at}"
    manifest["run_started_at"] = run_started_at
    manifest["run_finished_at"] = _utc_timestamp()
    manifest["wall_clock_seconds"] = time.perf_counter() - start
    _write_json(output_path, manifest)
    return manifest


def framework_versions() -> dict[str, str]:
    import scipy
    import sklearn
    import torch

    return {
        "numpy": str(np.__version__),
        "scipy": str(scipy.__version__),
        "sklearn": str(sklearn.__version__),
        "torch": str(torch.__version__),
    }


def s3c_code_hash() -> str:
    h = hashlib.sha256()
    for path in (Path(__file__), Path(__file__).with_name("seq_models.py"), Path(__file__).with_name("base.py")):
        h.update(path.name.encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _measure_cheapest_logreg_one_set(design: Mapping[str, Any], manifest: Mapping[str, Any]) -> dict[str, Any]:
    entry = manifest["sets"][0]
    spec = _train_only_spec_from_entry(entry)
    matrix_start = time.perf_counter()
    x_fit, y_fit, x_val, y_val, counts = _build_one_set_f1_matrices(design, spec)
    matrix_seconds = time.perf_counter() - matrix_start
    config = decoder_grid("obs_decoder_logreg")[0]
    fit_start = time.perf_counter()
    model = LogisticRegression(
        C=float(config["C"]),
        solver="lbfgs",
        max_iter=int(config["max_iter"]),
        random_state=_derive_config_seed(design, str(config["config_id"])),
    )
    model.fit(x_fit, y_fit)
    pred = model.predict(x_val)
    metric = float(balanced_accuracy_score(y_val, pred))
    fit_seconds = time.perf_counter() - fit_start
    return {
        "set_id": str(entry["set_id"]),
        "member": "obs_decoder_logreg",
        "config_id": str(config["config_id"]),
        "framework": str(config["framework"]),
        "features": "F1",
        "fit_user_range": [0, TRAIN_FIT_USER_MAX],
        "internal_validation_user_range": [INTERNAL_VALIDATION_USER_MIN, TRAIN_USER_MAX],
        "heldout_touched": False,
        "fit_examples": int(x_fit.shape[0]),
        "internal_validation_examples": int(x_val.shape[0]),
        "feature_dimension": int(x_fit.shape[1]),
        "fit_matrix_nnz": int(x_fit.nnz),
        "internal_validation_matrix_nnz": int(x_val.nnz),
        "matrix_build_wall_clock_seconds": matrix_seconds,
        "fit_and_metric_wall_clock_seconds": fit_seconds,
        "fit_plus_validation_wall_clock_seconds": matrix_seconds + fit_seconds,
        "internal_validation_macro_balanced_accuracy": metric,
        "class_count_seen": int(len(set(int(v) for v in y_fit))),
        "records_consumed": counts,
    }


def measure_s3c_cost_class_one_set(
    design: Mapping[str, Any],
    manifest: Mapping[str, Any],
    cost_class: str,
    vocabulary: Mapping[str, Any],
) -> dict[str, Any]:
    if cost_class not in S3C_COST_CLASSES:
        raise ValueError(f"unknown S3c R2 cost class: {cost_class}")
    entry = manifest["sets"][0]
    spec = _train_only_spec_from_entry(entry)
    if cost_class == "logreg_F1":
        return _measure_sklearn_one_set(design, spec, decoder_grid("obs_decoder_logreg")[0], features="F1")
    if cost_class == "logreg_F2":
        return _measure_sklearn_one_set(design, spec, decoder_grid("obs_decoder_logreg")[4], features="F2", vocabulary=vocabulary)
    if cost_class == "gbt":
        return _measure_sklearn_one_set(
            design,
            spec,
            decoder_grid("obs_decoder_gbt")[0],
            features="F2",
            vocabulary=vocabulary,
            fit_user_filter=set(gbt_fit_user_ids()),
        )
    if cost_class == "gru":
        return _measure_gru_one_set(design, spec, decoder_grid("obs_decoder_gru")[0], member_kind="obs_decoder_gru")
    if cost_class == "seq_full":
        return _measure_gru_one_set(
            design,
            spec,
            _gru_grid("seq_full_history_no_action_conditioning")[0],
            member_kind="seq_full_history_no_action_conditioning",
        )
    return _measure_gru_one_set(
        design,
        spec,
        _gru_grid("seq_window_with_action_conditioning_W15_no_cross_session_persistence")[0],
        member_kind="seq_window_with_action_conditioning_W15_no_cross_session_persistence",
    )


def _measure_sklearn_one_set(
    design: Mapping[str, Any],
    spec: TrajectorySetSpec,
    config: Mapping[str, Any],
    *,
    features: str,
    vocabulary: Mapping[str, Any] | None = None,
    fit_user_filter: set[int] | None = None,
) -> dict[str, Any]:
    matrix_start = time.perf_counter()
    x_fit, y_fit, x_val, y_val, counts = _build_one_set_feature_matrices(
        design,
        spec,
        features=features,
        vocabulary=vocabulary,
        fit_user_filter=fit_user_filter,
    )
    matrix_seconds = time.perf_counter() - matrix_start
    fit_start = time.perf_counter()
    if str(config["member"]) == "obs_decoder_logreg":
        model = LogisticRegression(
            C=float(config["C"]),
            solver="lbfgs",
            max_iter=int(config["max_iter"]),
            random_state=_derive_config_seed(design, str(config["config_id"])),
        )
        model.fit(x_fit, y_fit)
        pred = model.predict(x_val)
    elif str(config["member"]) == "obs_decoder_gbt":
        model = HistGradientBoostingClassifier(
            learning_rate=float(config["learning_rate"]),
            max_iter=int(config["max_iter"]),
            max_leaf_nodes=int(config["max_leaf_nodes"]),
            random_state=_derive_config_seed(design, str(config["config_id"])),
        )
        model.fit(x_fit.astype(np.float32).toarray(), y_fit)
        pred = model.predict(x_val.astype(np.float32).toarray())
    else:
        raise ValueError(f"unsupported sklearn measurement member: {config['member']}")
    metric = float(balanced_accuracy_score(y_val, pred))
    fit_seconds = time.perf_counter() - fit_start
    return {
        "cost_class": _cost_class_for_config(config, features),
        "set_id": str(spec.set_id),
        "member": str(config["member"]),
        "config_id": str(config["config_id"]),
        "config_index": int(config["config_index"]),
        "framework": str(config["framework"]),
        "features": features,
        "fit_user_range": [0, TRAIN_FIT_USER_MAX],
        "fit_user_filter": "user_id % 2 == 0" if fit_user_filter is not None else "all fit users",
        "internal_validation_user_range": [INTERNAL_VALIDATION_USER_MIN, TRAIN_USER_MAX],
        "heldout_touched": False,
        "fit_examples": int(x_fit.shape[0]),
        "internal_validation_examples": int(x_val.shape[0]),
        "feature_dimension": int(x_fit.shape[1]),
        "fit_matrix_nnz": int(x_fit.nnz),
        "internal_validation_matrix_nnz": int(x_val.nnz),
        "matrix_build_wall_clock_seconds": matrix_seconds,
        "fit_and_metric_wall_clock_seconds": fit_seconds,
        "fit_plus_validation_wall_clock_seconds": matrix_seconds + fit_seconds,
        "internal_validation_macro_balanced_accuracy": metric,
        "class_count_seen": int(len(set(int(v) for v in y_fit))),
        "records_consumed": counts,
        "producer_function": "src.fsp_pum_env.battery.obs_decoders._measure_sklearn_one_set",
    }


def _measure_gru_one_set(
    design: Mapping[str, Any],
    spec: TrajectorySetSpec,
    config: Mapping[str, Any],
    *,
    member_kind: str,
) -> dict[str, Any]:
    import torch
    from torch import nn

    env_state = configure_s3c_single_thread_cpu_environment()
    collect_start = time.perf_counter()
    fit_sequences, val_sequences = _collect_gru_sequences_one_set(design, spec, member_kind)
    collect_seconds = time.perf_counter() - collect_start
    alphabet_size = response_alphabet_size(design)
    actions = frozen_action_list(design)
    action_to_index = {action: idx for idx, action in enumerate(actions)}
    use_actions = member_kind in {"obs_decoder_gru", "seq_window_with_action_conditioning_W15_no_cross_session_persistence"}
    model = _make_torch_next_symbol_gru(
        alphabet_size=alphabet_size,
        action_count=len(actions),
        hidden_size=int(config["hidden"]),
        symbol_embedding_dim=int(config["symbol_embedding_dim"]),
        action_embedding_dim=int(config["action_embedding_dim"]),
        dropout=float(config["dropout"]),
        use_actions=use_actions,
    ).to(torch.device("cpu"))
    optimizer = torch.optim.Adam(model.parameters(), lr=float(config["lr"]))
    criterion = nn.CrossEntropyLoss()
    rng = np.random.default_rng(_derive_config_seed(design, str(config["config_id"])))
    batch_size = int(config["batch_size"])
    best_val_loss = float("inf")
    patience_left = int(config["early_stop_patience"])
    epochs_run = 0
    fit_start = time.perf_counter()
    for _ in range(int(config["max_epochs"])):
        epochs_run += 1
        order = rng.permutation(len(fit_sequences))
        model.train()
        for start_index in range(0, len(order), batch_size):
            batch = [fit_sequences[int(idx)] for idx in order[start_index : start_index + batch_size]]
            prev_symbols, action_ids, targets = _gru_batch_tensors(batch, action_to_index, alphabet_size, use_actions)
            optimizer.zero_grad(set_to_none=True)
            logits = model(prev_symbols, action_ids)
            loss = criterion(logits.reshape(-1, alphabet_size), targets.reshape(-1))
            loss.backward()
            optimizer.step()
        val_loss, _ = _evaluate_gru_model(model, val_sequences, action_to_index, alphabet_size, use_actions, batch_size)
        if val_loss + 1e-12 < best_val_loss:
            best_val_loss = val_loss
            patience_left = int(config["early_stop_patience"])
        else:
            patience_left -= 1
            if patience_left <= 0:
                break
    _, metric = _evaluate_gru_model(model, val_sequences, action_to_index, alphabet_size, use_actions, batch_size)
    fit_seconds = time.perf_counter() - fit_start
    fit_examples = sum(len(seq["symbols"]) for seq in fit_sequences)
    val_examples = sum(len(seq["symbols"]) for seq in val_sequences)
    return {
        "cost_class": _cost_class_for_gru_member(member_kind),
        "set_id": str(spec.set_id),
        "member": member_kind,
        "config_id": str(config["config_id"]),
        "config_index": int(config["config_index"]),
        "framework": str(config["framework"]),
        "device": "cpu",
        "single_thread_accounting": True,
        "environment": env_state,
        "teacher_forced_one_pass_per_user_sequence_per_epoch": True,
        "per_example_prefix_reencoding": False,
        "query_time_single_prefix_encoding": True,
        "fit_user_range": [0, TRAIN_FIT_USER_MAX],
        "internal_validation_user_range": [INTERNAL_VALIDATION_USER_MIN, TRAIN_USER_MAX],
        "heldout_touched": False,
        "fit_sequences": int(len(fit_sequences)),
        "internal_validation_sequences": int(len(val_sequences)),
        "fit_examples": int(fit_examples),
        "internal_validation_examples": int(val_examples),
        "sequence_collect_wall_clock_seconds": collect_seconds,
        "fit_and_metric_wall_clock_seconds": fit_seconds,
        "fit_plus_validation_wall_clock_seconds": collect_seconds + fit_seconds,
        "epochs_run": int(epochs_run),
        "offline_compute_units": int(epochs_run * fit_examples),
        "internal_validation_macro_balanced_accuracy": float(metric),
        "producer_function": "src.fsp_pum_env.battery.obs_decoders._measure_gru_one_set",
    }


def _build_one_set_f1_matrices(
    design: Mapping[str, Any],
    spec: TrajectorySetSpec,
) -> tuple[sparse.csr_matrix, np.ndarray, sparse.csr_matrix, np.ndarray, dict[str, int]]:
    alphabet_size = response_alphabet_size(design)
    actions = frozen_action_list(design)
    action_to_index = {action: idx for idx, action in enumerate(actions)}
    feature_dim = int(feature_map_summary(design)["F1"]["dimension"])
    rows: dict[str, list[int]] = {"fit": [], "internal_validation": []}
    cols: dict[str, list[int]] = {"fit": [], "internal_validation": []}
    data: dict[str, list[float]] = {"fit": [], "internal_validation": []}
    labels: dict[str, list[int]] = {"fit": [], "internal_validation": []}
    row_index = {"fit": 0, "internal_validation": 0}
    counts = {"fit_records": 0, "internal_validation_records": 0}
    active_user: int | None = None
    state = _PrefixFeatureState(alphabet_size)
    for _, trajectory_ordinal, record, _ in trajectory_sets_module._iter_records_with_adjudicator(design, spec):
        user_id = int(trajectory_ordinal)
        if active_user != user_id:
            active_user = user_id
            state = _PrefixFeatureState(alphabet_size)
        split = s3c_split_for_user(user_id)
        if split not in row_index:
            raise ValueError(f"S3c unexpected split for user_id {user_id}: {split}")
        parsed = event_from_mapping(record)
        _append_f1_row(
            state,
            parsed.action,
            action_to_index,
            rows[split],
            cols[split],
            data[split],
            row_index[split],
        )
        labels[split].append(int(parsed.observation["symbol"]))
        row_index[split] += 1
        counts[f"{split}_records"] += 1
        state.observe(parsed)
    x_fit = sparse.csr_matrix((data["fit"], (rows["fit"], cols["fit"])), shape=(row_index["fit"], feature_dim))
    x_val = sparse.csr_matrix(
        (data["internal_validation"], (rows["internal_validation"], cols["internal_validation"])),
        shape=(row_index["internal_validation"], feature_dim),
    )
    return x_fit, np.asarray(labels["fit"], dtype=np.int64), x_val, np.asarray(labels["internal_validation"], dtype=np.int64), counts


def _build_one_set_feature_matrices(
    design: Mapping[str, Any],
    spec: TrajectorySetSpec,
    *,
    features: str,
    vocabulary: Mapping[str, Any] | None = None,
    fit_user_filter: set[int] | None = None,
) -> tuple[sparse.csr_matrix, np.ndarray, sparse.csr_matrix, np.ndarray, dict[str, int]]:
    alphabet_size = response_alphabet_size(design)
    actions = frozen_action_list(design)
    action_to_index = {action: idx for idx, action in enumerate(actions)}
    vocab_tuples = _vocabulary_tuples(vocabulary) if features == "F2" else []
    feature_dim = _feature_dimension(alphabet_size, len(actions), features, len(vocab_tuples))
    rows: dict[str, list[int]] = {"fit": [], "internal_validation": []}
    cols: dict[str, list[int]] = {"fit": [], "internal_validation": []}
    data: dict[str, list[float]] = {"fit": [], "internal_validation": []}
    labels: dict[str, list[int]] = {"fit": [], "internal_validation": []}
    row_index = {"fit": 0, "internal_validation": 0}
    counts = {
        "fit_records": 0,
        "internal_validation_records": 0,
        "fit_records_skipped_by_budget": 0,
    }
    active_user: int | None = None
    state = _PrefixFeatureState(alphabet_size)
    start_user = int(spec.partitions["train"]["start_user_id"])
    for _, trajectory_ordinal, record, _ in trajectory_sets_module._iter_records_with_adjudicator(design, spec):
        user_id = start_user + int(trajectory_ordinal)
        split = s3c_split_for_user(user_id)
        if active_user != user_id:
            active_user = user_id
            state = _PrefixFeatureState(alphabet_size)
        parsed = event_from_mapping(record)
        include_row = split == "internal_validation" or fit_user_filter is None or user_id in fit_user_filter
        if include_row:
            _append_feature_row(
                state,
                parsed.action,
                action_to_index,
                rows[split],
                cols[split],
                data[split],
                row_index[split],
                features=features,
                vocabulary_tuples=vocab_tuples,
            )
            labels[split].append(int(parsed.observation["symbol"]))
            row_index[split] += 1
            counts[f"{split}_records"] += 1
        elif split == "fit":
            counts["fit_records_skipped_by_budget"] += 1
        state.observe(parsed)
    x_fit = sparse.csr_matrix((data["fit"], (rows["fit"], cols["fit"])), shape=(row_index["fit"], feature_dim))
    x_val = sparse.csr_matrix(
        (data["internal_validation"], (rows["internal_validation"], cols["internal_validation"])),
        shape=(row_index["internal_validation"], feature_dim),
    )
    return x_fit, np.asarray(labels["fit"], dtype=np.int64), x_val, np.asarray(labels["internal_validation"], dtype=np.int64), counts


def _collect_train_events_one_set(design: Mapping[str, Any], spec: TrajectorySetSpec) -> dict[str, dict[int, list[PrefixEvent]]]:
    events: dict[str, dict[int, list[PrefixEvent]]] = {"fit": {}, "internal_validation": {}}
    start_user = int(spec.partitions["train"]["start_user_id"])
    for _, trajectory_ordinal, record, _ in trajectory_sets_module._iter_records_with_adjudicator(design, spec):
        user_id = start_user + int(trajectory_ordinal)
        split = s3c_split_for_user(user_id)
        events[split].setdefault(user_id, []).append(event_from_mapping(record))
    return events


def _build_feature_matrices_from_user_events(
    events_by_split: Mapping[str, Mapping[int, Sequence[PrefixEvent]]],
    actions: Sequence[str],
    *,
    alphabet_size: int,
    features: str,
    vocabulary: Mapping[str, Any] | None,
    fit_user_filter: set[int] | None = None,
) -> tuple[sparse.csr_matrix, np.ndarray, sparse.csr_matrix, np.ndarray, dict[str, int]]:
    action_to_index = {str(action): idx for idx, action in enumerate(actions)}
    vocab_tuples = _vocabulary_tuples(vocabulary) if features == "F2" else []
    feature_dim = _feature_dimension(alphabet_size, len(actions), features, len(vocab_tuples))
    rows: dict[str, list[int]] = {"fit": [], "internal_validation": []}
    cols: dict[str, list[int]] = {"fit": [], "internal_validation": []}
    data: dict[str, list[float]] = {"fit": [], "internal_validation": []}
    labels: dict[str, list[int]] = {"fit": [], "internal_validation": []}
    row_index = {"fit": 0, "internal_validation": 0}
    counts = {"fit_records": 0, "internal_validation_records": 0, "fit_records_skipped_by_budget": 0}
    for split in ("fit", "internal_validation"):
        for user_id in sorted(events_by_split[split]):
            if split == "fit" and fit_user_filter is not None and user_id not in fit_user_filter:
                counts["fit_records_skipped_by_budget"] += len(events_by_split[split][user_id])
                continue
            state = _PrefixFeatureState(int(alphabet_size))
            for event in events_by_split[split][user_id]:
                _append_feature_row(
                    state,
                    event.action,
                    action_to_index,
                    rows[split],
                    cols[split],
                    data[split],
                    row_index[split],
                    features=features,
                    vocabulary_tuples=vocab_tuples,
                )
                labels[split].append(int(event.observation["symbol"]))
                row_index[split] += 1
                counts[f"{split}_records"] += 1
                state.observe(event)
    x_fit = sparse.csr_matrix((data["fit"], (rows["fit"], cols["fit"])), shape=(row_index["fit"], feature_dim))
    x_val = sparse.csr_matrix(
        (data["internal_validation"], (rows["internal_validation"], cols["internal_validation"])),
        shape=(row_index["internal_validation"], feature_dim),
    )
    return x_fit, np.asarray(labels["fit"], dtype=np.int64), x_val, np.asarray(labels["internal_validation"], dtype=np.int64), counts


def _fit_eval_sklearn_config(
    design: Mapping[str, Any],
    config: Mapping[str, Any],
    x_fit: sparse.csr_matrix,
    y_fit: np.ndarray,
    x_val: sparse.csr_matrix,
    y_val: np.ndarray,
) -> dict[str, Any]:
    start = time.perf_counter()
    if str(config["member"]) == "obs_decoder_logreg":
        model = LogisticRegression(
            C=float(config["C"]),
            solver="lbfgs",
            max_iter=int(config["max_iter"]),
            random_state=_derive_config_seed(design, str(config["config_id"])),
        )
        model.fit(x_fit, y_fit)
        pred = model.predict(x_val)
        offline_units = int(int(config["max_iter"]) * int(x_fit.shape[0]))
    elif str(config["member"]) == "obs_decoder_gbt":
        model = HistGradientBoostingClassifier(
            learning_rate=float(config["learning_rate"]),
            max_iter=int(config["max_iter"]),
            max_leaf_nodes=int(config["max_leaf_nodes"]),
            random_state=_derive_config_seed(design, str(config["config_id"])),
        )
        model.fit(x_fit.astype(np.float32).toarray(), y_fit)
        pred = model.predict(x_val.astype(np.float32).toarray())
        offline_units = int(int(config["max_iter"]) * int(x_fit.shape[0]))
    else:
        raise ValueError(f"unsupported sklearn sweep member: {config['member']}")
    return {
        "fit_and_predict_wall_clock_seconds": time.perf_counter() - start,
        "targets": [int(value) for value in y_val],
        "predictions": [int(value) for value in pred],
        "fit_examples": int(x_fit.shape[0]),
        "internal_validation_examples": int(x_val.shape[0]),
        "offline_compute_units": offline_units,
    }


def _sequences_from_user_events(
    events_by_split: Mapping[str, Mapping[int, Sequence[PrefixEvent]]],
    member_kind: str,
) -> tuple[list[dict[str, list[Any]]], list[dict[str, list[Any]]]]:
    output: dict[str, list[dict[str, list[Any]]]] = {"fit": [], "internal_validation": []}
    for split in ("fit", "internal_validation"):
        for user_id in sorted(events_by_split[split]):
            events = list(events_by_split[split][user_id])
            if member_kind == "seq_window_with_action_conditioning_W15_no_cross_session_persistence":
                active_session: list[PrefixEvent] = []
                for event in events:
                    if event.session_boundary == "start" and active_session:
                        output[split].append(_sequence_payload(active_session))
                        active_session = []
                    active_session.append(event)
                if active_session:
                    output[split].append(_sequence_payload(active_session))
            else:
                output[split].append(_sequence_payload(events))
    return output["fit"], output["internal_validation"]


def _fit_eval_gru_sequences(
    design: Mapping[str, Any],
    config: Mapping[str, Any],
    member_kind: str,
    fit_sequences: Sequence[Mapping[str, list[Any]]],
    val_sequences: Sequence[Mapping[str, list[Any]]],
) -> dict[str, Any]:
    import torch
    from torch import nn

    alphabet_size = response_alphabet_size(design)
    actions = frozen_action_list(design)
    action_to_index = {action: idx for idx, action in enumerate(actions)}
    use_actions = member_kind in {"obs_decoder_gru", "seq_window_with_action_conditioning_W15_no_cross_session_persistence"}
    model = _make_torch_next_symbol_gru(
        alphabet_size=alphabet_size,
        action_count=len(actions),
        hidden_size=int(config["hidden"]),
        symbol_embedding_dim=int(config["symbol_embedding_dim"]),
        action_embedding_dim=int(config["action_embedding_dim"]),
        dropout=float(config["dropout"]),
        use_actions=use_actions,
    ).to(torch.device("cpu"))
    optimizer = torch.optim.Adam(model.parameters(), lr=float(config["lr"]))
    criterion = nn.CrossEntropyLoss()
    rng = np.random.default_rng(_derive_config_seed(design, str(config["config_id"])))
    batch_size = int(config["batch_size"])
    best_val_loss = float("inf")
    patience_left = int(config["early_stop_patience"])
    epochs_run = 0
    start = time.perf_counter()
    for _ in range(int(config["max_epochs"])):
        epochs_run += 1
        order = rng.permutation(len(fit_sequences))
        model.train()
        for start_index in range(0, len(order), batch_size):
            batch = [fit_sequences[int(idx)] for idx in order[start_index : start_index + batch_size]]
            prev_symbols, action_ids, targets = _gru_batch_tensors(batch, action_to_index, alphabet_size, use_actions)
            optimizer.zero_grad(set_to_none=True)
            logits = model(prev_symbols, action_ids)
            loss = criterion(logits.reshape(-1, alphabet_size), targets.reshape(-1))
            loss.backward()
            optimizer.step()
        val_loss, _ = _evaluate_gru_model(model, val_sequences, action_to_index, alphabet_size, use_actions, batch_size)
        if val_loss + 1e-12 < best_val_loss:
            best_val_loss = val_loss
            patience_left = int(config["early_stop_patience"])
        else:
            patience_left -= 1
            if patience_left <= 0:
                break
    targets, predictions = _predict_gru_model(model, val_sequences, action_to_index, alphabet_size, use_actions, batch_size)
    fit_examples = sum(len(seq["symbols"]) for seq in fit_sequences)
    return {
        "fit_and_predict_wall_clock_seconds": time.perf_counter() - start,
        "targets": targets,
        "predictions": predictions,
        "fit_examples": int(fit_examples),
        "internal_validation_examples": int(len(targets)),
        "epochs_run": int(epochs_run),
        "offline_compute_units": int(epochs_run * fit_examples),
    }


def _empty_sweep_aggregators() -> dict[str, dict[str, Any]]:
    configs = (
        decoder_grid("obs_decoder_logreg")
        + decoder_grid("obs_decoder_gbt")
        + _gru_grid("obs_decoder_gru")
        + _gru_grid("seq_full_history_no_action_conditioning")
        + _gru_grid("seq_window_with_action_conditioning_W15_no_cross_session_persistence")
    )
    return {
        str(config["config_id"]): {
            "member": str(config["member"]),
            "config": dict(config),
            "config_id": str(config["config_id"]),
            "config_index": int(config["config_index"]),
            "targets": [],
            "predictions": [],
            "wall_clock_seconds": 0.0,
            "offline_compute_units": 0,
            "fit_examples": 0,
            "internal_validation_examples": 0,
            "set_results": [],
        }
        for config in configs
    }


def _update_sweep_aggregator(
    aggregators: dict[str, dict[str, Any]],
    config: Mapping[str, Any],
    result: Mapping[str, Any],
    counts: Mapping[str, Any],
    set_id: str,
) -> None:
    item = aggregators[str(config["config_id"])]
    accounted_seconds = float(
        result.get("fit_plus_validation_wall_clock_seconds", result["fit_and_predict_wall_clock_seconds"])
    )
    item["targets"].extend(int(value) for value in result["targets"])
    item["predictions"].extend(int(value) for value in result["predictions"])
    item["wall_clock_seconds"] += accounted_seconds
    item["offline_compute_units"] += int(result["offline_compute_units"])
    item["fit_examples"] += int(result["fit_examples"])
    item["internal_validation_examples"] += int(result["internal_validation_examples"])
    item["set_results"].append(
        {
            "set_id": str(set_id),
            "wall_clock_seconds": accounted_seconds,
            "model_fit_predict_wall_clock_seconds": float(result["fit_and_predict_wall_clock_seconds"]),
            "fit_examples": int(result["fit_examples"]),
            "internal_validation_examples": int(result["internal_validation_examples"]),
            "offline_compute_units": int(result["offline_compute_units"]),
            "records_consumed": dict(counts),
        }
    )


def _set_config_summary(config: Mapping[str, Any], result: Mapping[str, Any], set_id: str) -> dict[str, Any]:
    return {
        "set_id": str(set_id),
        "member": str(config["member"]),
        "config_id": str(config["config_id"]),
        "config_index": int(config["config_index"]),
        "wall_clock_seconds": float(result["fit_and_predict_wall_clock_seconds"]),
        "fit_examples": int(result["fit_examples"]),
        "internal_validation_examples": int(result["internal_validation_examples"]),
        "offline_compute_units": int(result["offline_compute_units"]),
    }


def _finalize_sweep_config(item: Mapping[str, Any]) -> dict[str, Any]:
    metric = float(balanced_accuracy_score(item["targets"], item["predictions"])) if item["targets"] else 0.0
    return {
        "member": str(item["member"]),
        "config": dict(item["config"]),
        "config_id": str(item["config_id"]),
        "config_index": int(item["config_index"]),
        "internal_validation_macro_balanced_accuracy": metric,
        "wall_clock_seconds": float(item["wall_clock_seconds"]),
        "offline_compute_units": int(item["offline_compute_units"]),
        "fit_examples": int(item["fit_examples"]),
        "internal_validation_examples": int(item["internal_validation_examples"]),
        "set_results": list(item["set_results"]),
    }


def _select_s3c_configs(per_config: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for item in per_config:
        member = str(item["member"])
        incumbent = selected.get(member)
        if incumbent is None:
            selected[member] = dict(item)
            continue
        better_metric = float(item["internal_validation_macro_balanced_accuracy"]) > float(
            incumbent["internal_validation_macro_balanced_accuracy"]
        )
        tie_lower_index = (
            float(item["internal_validation_macro_balanced_accuracy"])
            == float(incumbent["internal_validation_macro_balanced_accuracy"])
            and int(item["config_index"]) < int(incumbent["config_index"])
        )
        if better_metric or tie_lower_index:
            selected[member] = dict(item)
    return selected


def materialize_prefix_feature_rows_incremental(
    prefix_events: Sequence[PrefixEvent | Mapping[str, Any]],
    actions: Sequence[str],
    *,
    alphabet_size: int,
    vocabulary: Mapping[str, Any] | None = None,
    features: str = "F1",
) -> sparse.csr_matrix:
    action_to_index = {str(action): idx for idx, action in enumerate(actions)}
    vocab_tuples = _vocabulary_tuples(vocabulary) if features == "F2" else []
    feature_dim = _feature_dimension(alphabet_size, len(actions), features, len(vocab_tuples))
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    state = _PrefixFeatureState(int(alphabet_size))
    for row, raw_event in enumerate(prefix_events):
        event = event_from_mapping(raw_event)
        _append_feature_row(
            state,
            event.action,
            action_to_index,
            rows,
            cols,
            data,
            row,
            features=features,
            vocabulary_tuples=vocab_tuples,
        )
        state.observe(event)
    return sparse.csr_matrix((data, (rows, cols)), shape=(len(prefix_events), feature_dim))


def materialize_prefix_feature_rows_naive(
    prefix_events: Sequence[PrefixEvent | Mapping[str, Any]],
    actions: Sequence[str],
    *,
    alphabet_size: int,
    vocabulary: Mapping[str, Any] | None = None,
    features: str = "F1",
) -> sparse.csr_matrix:
    parsed_events = [event_from_mapping(event) for event in prefix_events]
    action_to_index = {str(action): idx for idx, action in enumerate(actions)}
    vocab_tuples = _vocabulary_tuples(vocabulary) if features == "F2" else []
    feature_dim = _feature_dimension(alphabet_size, len(actions), features, len(vocab_tuples))
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    for row, event in enumerate(parsed_events):
        state = _PrefixFeatureState(int(alphabet_size))
        for prior_event in parsed_events[:row]:
            state.observe(prior_event)
        _append_feature_row(
            state,
            event.action,
            action_to_index,
            rows,
            cols,
            data,
            row,
            features=features,
            vocabulary_tuples=vocab_tuples,
        )
    return sparse.csr_matrix((data, (rows, cols)), shape=(len(prefix_events), feature_dim))


def _append_feature_row(
    state: _PrefixFeatureState,
    action: str,
    action_to_index: Mapping[str, int],
    rows: list[int],
    cols: list[int],
    data: list[float],
    row: int,
    *,
    features: str,
    vocabulary_tuples: Sequence[tuple[int, ...]],
) -> None:
    _append_f1_row(state, action, action_to_index, rows, cols, data, row)
    if features == "F1":
        return
    if features != "F2":
        raise ValueError(f"unknown S3c feature family: {features}")
    offset = _f1_dimension(state.alphabet_size, len(action_to_index))
    for idx, ngram in enumerate(vocabulary_tuples):
        value = state.ngram_counts.get(ngram, 0)
        if value:
            rows.append(row)
            cols.append(offset + idx)
            data.append(float(value))


def _append_f1_row(
    state: _PrefixFeatureState,
    action: str,
    action_to_index: Mapping[str, int],
    rows: list[int],
    cols: list[int],
    data: list[float],
    row: int,
) -> None:
    alphabet_size = int(state.alphabet_size)
    offsets = {
        "counts": 0,
        "rates": alphabet_size,
        "transitions": alphabet_size * 2,
        "last": alphabet_size * 2 + alphabet_size * alphabet_size,
        "action": alphabet_size * 3 + alphabet_size * alphabet_size,
    }
    for symbol, value in enumerate(state.counts):
        if value:
            rows.append(row)
            cols.append(offsets["counts"] + symbol)
            data.append(float(value))
            rows.append(row)
            cols.append(offsets["rates"] + symbol)
            data.append(float(value) / max(1.0, float(state.prefix_len)))
    for (left, right), value in state.transitions.items():
        rows.append(row)
        cols.append(offsets["transitions"] + left * alphabet_size + right)
        data.append(float(value))
    if state.last_symbol is not None:
        rows.append(row)
        cols.append(offsets["last"] + int(state.last_symbol))
        data.append(1.0)
    if action not in action_to_index:
        raise ValueError(f"action {action!r} missing from frozen action list")
    rows.append(row)
    cols.append(offsets["action"] + int(action_to_index[action]))
    data.append(1.0)


def _f1_dimension(alphabet_size: int, action_count: int) -> int:
    return int(alphabet_size) + int(alphabet_size) + int(alphabet_size) * int(alphabet_size) + int(alphabet_size) + int(action_count)


def _feature_dimension(alphabet_size: int, action_count: int, features: str, vocabulary_size: int) -> int:
    f1_dim = _f1_dimension(alphabet_size, action_count)
    if features == "F1":
        return f1_dim
    if features == "F2":
        return f1_dim + int(vocabulary_size)
    raise ValueError(f"unknown S3c feature family: {features}")


def _vocabulary_tuples(vocabulary: Mapping[str, Any] | None) -> list[tuple[int, ...]]:
    if vocabulary is None:
        raise ValueError("F2 feature materialization requires a vocabulary")
    return [tuple(int(symbol) for symbol in entry["symbols"]) for entry in vocabulary["ngrams"]]


def _ngram_key(ngram: Sequence[int]) -> str:
    return " ".join(str(int(symbol)) for symbol in ngram)


def _collect_gru_sequences_one_set(
    design: Mapping[str, Any],
    spec: TrajectorySetSpec,
    member_kind: str,
) -> tuple[list[dict[str, list[Any]]], list[dict[str, list[Any]]]]:
    sequences: dict[str, list[dict[str, list[Any]]]] = {"fit": [], "internal_validation": []}
    active_user: int | None = None
    current_user_events: list[PrefixEvent] = []
    start_user = int(spec.partitions["train"]["start_user_id"])

    def flush_user() -> None:
        if active_user is None or not current_user_events:
            return
        split = s3c_split_for_user(active_user)
        if member_kind == "seq_window_with_action_conditioning_W15_no_cross_session_persistence":
            active_session: list[PrefixEvent] = []
            for event in current_user_events:
                if event.session_boundary == "start" and active_session:
                    sequences[split].append(_sequence_payload(active_session))
                    active_session = []
                active_session.append(event)
            if active_session:
                sequences[split].append(_sequence_payload(active_session))
        else:
            sequences[split].append(_sequence_payload(current_user_events))

    for _, trajectory_ordinal, record, _ in trajectory_sets_module._iter_records_with_adjudicator(design, spec):
        user_id = start_user + int(trajectory_ordinal)
        s3c_split_for_user(user_id)
        parsed = event_from_mapping(record)
        if active_user != user_id:
            flush_user()
            active_user = user_id
            current_user_events = []
        current_user_events.append(parsed)
    flush_user()
    return sequences["fit"], sequences["internal_validation"]


def _sequence_payload(events: Sequence[PrefixEvent]) -> dict[str, list[Any]]:
    return {
        "symbols": [int(event.observation["symbol"]) for event in events],
        "actions": [str(event.action) for event in events],
    }


def _make_torch_next_symbol_gru(
    *,
    alphabet_size: int,
    action_count: int,
    hidden_size: int,
    symbol_embedding_dim: int,
    action_embedding_dim: int,
    dropout: float,
    use_actions: bool,
):
    import torch
    from torch import nn

    class TorchNextSymbolGru(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.symbol_embedding = nn.Embedding(alphabet_size + 1, symbol_embedding_dim, padding_idx=alphabet_size)
            self.use_actions = bool(use_actions)
            if self.use_actions:
                self.action_embedding = nn.Embedding(action_count, action_embedding_dim)
                input_dim = symbol_embedding_dim + action_embedding_dim
            else:
                self.action_embedding = None
                input_dim = symbol_embedding_dim
            self.dropout = nn.Dropout(float(dropout))
            self.gru = nn.GRU(input_dim, hidden_size, batch_first=True)
            self.head = nn.Linear(hidden_size, alphabet_size)

        def forward(self, prev_symbols, action_ids):
            symbol_emb = self.symbol_embedding(prev_symbols)
            if self.use_actions:
                action_emb = self.action_embedding(action_ids)
                inputs = torch.cat([symbol_emb, action_emb], dim=-1)
            else:
                inputs = symbol_emb
            outputs, _ = self.gru(self.dropout(inputs))
            return self.head(outputs)

    return TorchNextSymbolGru()


def _gru_batch_tensors(
    batch: Sequence[Mapping[str, list[Any]]],
    action_to_index: Mapping[str, int],
    alphabet_size: int,
    use_actions: bool,
):
    import torch

    max_len = max(len(seq["symbols"]) for seq in batch)
    prev_symbols = np.full((len(batch), max_len), int(alphabet_size), dtype=np.int64)
    action_ids = np.zeros((len(batch), max_len), dtype=np.int64)
    targets = np.zeros((len(batch), max_len), dtype=np.int64)
    for row, seq in enumerate(batch):
        symbols = [int(symbol) for symbol in seq["symbols"]]
        actions = [str(action) for action in seq["actions"]]
        seq_len = len(symbols)
        if seq_len == 0:
            continue
        prev_symbols[row, 0] = int(alphabet_size)
        if seq_len > 1:
            prev_symbols[row, 1:seq_len] = np.asarray(symbols[:-1], dtype=np.int64)
        targets[row, :seq_len] = np.asarray(symbols, dtype=np.int64)
        if use_actions:
            action_ids[row, :seq_len] = np.asarray([int(action_to_index[action]) for action in actions], dtype=np.int64)
    return (
        torch.as_tensor(prev_symbols, dtype=torch.long, device=torch.device("cpu")),
        torch.as_tensor(action_ids, dtype=torch.long, device=torch.device("cpu")),
        torch.as_tensor(targets, dtype=torch.long, device=torch.device("cpu")),
    )


def _evaluate_gru_model(
    model: Any,
    sequences: Sequence[Mapping[str, list[Any]]],
    action_to_index: Mapping[str, int],
    alphabet_size: int,
    use_actions: bool,
    batch_size: int,
) -> tuple[float, float]:
    import torch
    from torch import nn

    criterion = nn.CrossEntropyLoss(reduction="sum")
    model.eval()
    total_loss = 0.0
    total_examples = 0
    targets_all: list[int] = []
    preds_all: list[int] = []
    with torch.no_grad():
        for start_index in range(0, len(sequences), batch_size):
            batch = sequences[start_index : start_index + batch_size]
            prev_symbols, action_ids, targets = _gru_batch_tensors(batch, action_to_index, alphabet_size, use_actions)
            logits = model(prev_symbols, action_ids)
            total_loss += float(criterion(logits.reshape(-1, alphabet_size), targets.reshape(-1)).item())
            total_examples += int(targets.numel())
            preds = logits.argmax(dim=-1).reshape(-1).cpu().numpy()
            target_values = targets.reshape(-1).cpu().numpy()
            preds_all.extend(int(value) for value in preds)
            targets_all.extend(int(value) for value in target_values)
    mean_loss = total_loss / max(1, total_examples)
    metric = balanced_accuracy_score(targets_all, preds_all) if targets_all else 0.0
    return float(mean_loss), float(metric)


def _predict_gru_model(
    model: Any,
    sequences: Sequence[Mapping[str, list[Any]]],
    action_to_index: Mapping[str, int],
    alphabet_size: int,
    use_actions: bool,
    batch_size: int,
) -> tuple[list[int], list[int]]:
    import torch

    model.eval()
    targets_all: list[int] = []
    preds_all: list[int] = []
    with torch.no_grad():
        for start_index in range(0, len(sequences), batch_size):
            batch = sequences[start_index : start_index + batch_size]
            prev_symbols, action_ids, targets = _gru_batch_tensors(batch, action_to_index, alphabet_size, use_actions)
            logits = model(prev_symbols, action_ids)
            preds_all.extend(int(value) for value in logits.argmax(dim=-1).reshape(-1).cpu().numpy())
            targets_all.extend(int(value) for value in targets.reshape(-1).cpu().numpy())
    return targets_all, preds_all


def _cost_class_for_config(config: Mapping[str, Any], features: str) -> str:
    member = str(config["member"])
    if member == "obs_decoder_logreg" and features == "F1":
        return "logreg_F1"
    if member == "obs_decoder_logreg" and features == "F2":
        return "logreg_F2"
    if member == "obs_decoder_gbt":
        return "gbt"
    raise ValueError(f"cannot map config to S3c R2 cost class: {member}/{features}")


def _cost_class_for_gru_member(member_kind: str) -> str:
    if member_kind == "obs_decoder_gru":
        return "gru"
    if member_kind == "seq_full_history_no_action_conditioning":
        return "seq_full"
    if member_kind == "seq_window_with_action_conditioning_W15_no_cross_session_persistence":
        return "seq_W15"
    raise ValueError(f"cannot map GRU member to S3c R2 cost class: {member_kind}")


def _projection_weights(feature_maps: Mapping[str, Any]) -> dict[str, Any]:
    f1_dim = float(feature_maps["F1"]["dimension"])
    f2_dim = float(feature_maps["F2"]["dimension"])
    f2_ratio = f2_dim / f1_dim
    logreg = [
        {"config_id": cfg["config_id"], "weight": (1.0 if cfg["features"] == "F1" else f2_ratio)}
        for cfg in decoder_grid("obs_decoder_logreg")
    ]
    gbt = [
        {
            "config_id": cfg["config_id"],
            "weight": f2_ratio * (float(cfg["max_iter"]) / 100.0) * (float(cfg["max_leaf_nodes"]) / 31.0) * 4.0,
        }
        for cfg in decoder_grid("obs_decoder_gbt")
    ]
    decoder_gru = [
        {"config_id": cfg["config_id"], "weight": 10.0 * (float(cfg["hidden"]) / 32.0) * (1.0 + float(cfg["dropout"]))}
        for cfg in decoder_grid("obs_decoder_gru")
    ]
    sequence_gru = [
        {
            "config_id": cfg["config_id"],
            "weight": 10.0 * (float(cfg["hidden"]) / 32.0) * (1.0 + float(cfg["dropout"])),
        }
        for cfg in _gru_grid("seq_full_history_no_action_conditioning")
    ] + [
        {
            "config_id": cfg["config_id"],
            "weight": 10.0 * 15.0 * (float(cfg["hidden"]) / 32.0) * (1.0 + float(cfg["dropout"])),
        }
        for cfg in _gru_grid("seq_window_with_action_conditioning_W15_no_cross_session_persistence")
    ]
    per_set_multiplier = sum(item["weight"] for item in logreg + gbt + decoder_gru + sequence_gru)
    return {
        "basis": "measured cheapest logreg F1 one-set config scaled by frozen config count, all 10 sets, F2 dimensionality, GBT dense-HGB cost, GRU max-epoch hidden-size cost, and W15 sequence length",
        "fit_sets": 10,
        "f2_to_f1_dimension_ratio": f2_ratio,
        "logreg_config_weights": logreg,
        "gbt_config_weights": gbt,
        "decoder_gru_config_weights": decoder_gru,
        "sequence_gru_config_weights": sequence_gru,
        "per_set_equivalent_one_set_multiplier": per_set_multiplier,
        "total_equivalent_one_set_multiplier": per_set_multiplier * 10.0,
    }


def _gru_grid(member_name: str) -> list[dict[str, Any]]:
    rows = []
    for hidden in (32, 64):
        for lr in (1e-3, 3e-4):
            for dropout in (0.0, 0.1):
                rows.append(
                    {
                        "member": member_name,
                        "config_index": len(rows),
                        "config_id": f"{member_name}_cfg{len(rows):02d}",
                        "framework": "torch.nn.GRU",
                        "hidden": int(hidden),
                        "lr": float(lr),
                        "dropout": float(dropout),
                        "symbol_embedding_dim": 16,
                        "action_embedding_dim": 8,
                        "batch_size": 256,
                        "max_epochs": 10,
                        "early_stop_patience": 2,
                    }
                )
    return rows


def _train_only_spec_from_entry(entry: Mapping[str, Any]) -> TrajectorySetSpec:
    params = entry["generation_params"]
    train = params["partitions"]["train"]
    return TrajectorySetSpec(
        set_id=str(params["set_id"]),
        master_seed=int(params["master_seed"]),
        env_mode=str(params["env_mode"]),
        partitions={"train": {"start_user_id": int(train["start_user_id"]), "count": int(train["count"])}},
        turns_per_user=int(params["turns_per_user"]),
        logging_policy=params["logging_policy"],
    )


def _fit_only_spec_from_entry(entry: Mapping[str, Any]) -> TrajectorySetSpec:
    params = entry["generation_params"]
    train = params["partitions"]["train"]
    start_user = int(train["start_user_id"])
    if start_user != 0:
        raise ValueError(f"S3c FIT vocabulary expects train start_user_id 0, got {start_user}")
    return TrajectorySetSpec(
        set_id=str(params["set_id"]),
        master_seed=int(params["master_seed"]),
        env_mode=str(params["env_mode"]),
        partitions={"train": {"start_user_id": 0, "count": TRAIN_FIT_USER_MAX + 1}},
        turns_per_user=int(params["turns_per_user"]),
        logging_policy=params["logging_policy"],
    )


def _derive_config_seed(design: Mapping[str, Any], config_id: str) -> int:
    master_seed = int(design["population_and_data"]["env_master_seeds"][0])
    stream_seed = hashlib.sha256(f"{master_seed}:baseline_fit".encode("utf-8")).hexdigest()
    digest = hashlib.sha256(f"{stream_seed}:{config_id}".encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big", signed=False)


def _require_frameworks() -> None:
    framework_versions()


def _require_member(design: Mapping[str, Any], member: str) -> None:
    if member not in design["battery_membership"]["members"]:
        raise ValueError(f"frozen battery_membership missing {member}")


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    return value


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "missing"


def _payload_sha256(payload: Mapping[str, Any]) -> str:
    clean = {str(key): value for key, value in payload.items() if str(key) != "sha256"}
    encoded = json.dumps(_jsonable(clean), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
