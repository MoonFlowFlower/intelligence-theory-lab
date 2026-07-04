"""S3d PART 0 per-user timing variance probe.

Task-local runner for
FSP-PUM-ENV-IDPROBE-001A-S3D-PART0-VARIANCE-PROBE-001A.

Claim ceiling: PART 0 compute-projection refinement / per-user timing variance
only.  This script does not launch the S3d certificate battery, does not launch
NULL-env, and does not modify frozen specs, thresholds, cert cells, NULL MDE, or
the 12 CPU-h decision line.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import statistics
import sys
import time
from typing import Any, Callable, Mapping, Sequence


for _THREAD_KEY in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_THREAD_KEY] = "1"

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.fsp_pum_env.battery.base import event_from_mapping, response_alphabet_size
from src.fsp_pum_env.s3d_certificates import (
    S3D_CPU_HOUR_LIMIT,
    build_s3d_cert_set_specs,
    macro_balanced_accuracy,
    measure_s3d_ideal_one_eval_user,
)
from src.fsp_pum_env.trajectory_sets import load_frozen_design


TASK_ID = "FSP-PUM-ENV-IDPROBE-001A"
TASK_CARD_ID = "FSP-PUM-ENV-IDPROBE-001A-S3D-PART0-VARIANCE-PROBE-001A"
ARTIFACT_ROOT = ROOT / "artifacts" / TASK_ID
FROZEN_DESIGN = ARTIFACT_ROOT / "frozen_design.json"
PROJECTION = ARTIFACT_ROOT / "s3d_compute_projection.json"
ORIGINAL_RUNNER = ARTIFACT_ROOT / "s3d_part0_projection_runner.py"
RESULT = ARTIFACT_ROOT / "s3d_part0_variance_probe.json"
TRACE = ARTIFACT_ROOT / "s3d_part0_variance_probe_trace.csv"
FAILURE_MANIFEST = ARTIFACT_ROOT / "s3d_part0_variance_probe_failure_manifest.json"
BANK_OPS = ARTIFACT_ROOT / "s3d_part0_variance_probe_bank_ops.ps1"

FRACTIONAL_INDICES = (0.0, 0.25, 0.5, 0.75, 1.0)
REFERENCE_USER_ID = 640
WALL_CPU_HOUR_LIMIT = 12.0
THREAD_ENV_KEYS = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS")

TERM_IDEAL = "ideal_one_cell_camouflage_off"
TERM_LS = "discounted_LS_lambda_0.95_score_flat_theta"
TERM_NN = "nearest_neighbor_user_matching_score_stable_facts"

TARGET_COMPONENTS = {
    TERM_IDEAL: "ideal_all_7_cells_160_eval_users",
    TERM_LS: "ls_online_family_discounted_LS_lambda_0.95_cert_plus_NULL",
    TERM_NN: "retrieval_family_nearest_neighbor_user_matching_cert_plus_NULL",
}

CLAIM_CEILING = (
    "PART 0 compute-projection refinement / single-user timing variance only; "
    "no certificate, NULL, environment-validity, baseline-power, headroom, gap, "
    "mechanism, learning, agency, EGO-mainline, or banked-STOP upgrade claim"
)


def run_variance_probe() -> dict[str, Any]:
    run_started_at = _utc_timestamp()
    perf_start = time.perf_counter()
    environment = _single_thread_environment()
    thread_env = _thread_env_label(environment)
    trace_rows: list[dict[str, Any]] = []
    failure_reasons: list[str] = []

    try:
        _assert_single_thread_environment(environment)
        _assert_forbidden_reports_absent()
        design = load_frozen_design(FROZEN_DESIGN)
        projection = _read_json(PROJECTION)
        specs = {spec.cell_id: spec for spec in build_s3d_cert_set_specs(design)}
        selected_users_by_term = {
            TERM_IDEAL: _selected_eval_user_ids(specs["camouflage_off"].eval_user_range),
            TERM_LS: _selected_eval_user_ids(specs["flat_theta"].eval_user_range),
            TERM_NN: _selected_eval_user_ids(specs["stable_facts"].eval_user_range),
        }
        _assert_no_heldout_users(selected_users_by_term)

        projection_runner = _load_projection_runner()
        measurements: dict[str, Any] = {}

        ideal_measurements = []
        for user_id in selected_users_by_term[TERM_IDEAL]:
            _assert_wall_limit(perf_start)
            measurement = measure_s3d_ideal_one_eval_user(design, specs["camouflage_off"], user_id=user_id)
            wall = float(measurement["wall_clock_seconds"])
            _assert_finite(wall, f"{TERM_IDEAL}:{user_id}")
            ideal_measurements.append(measurement)
            trace_rows.append(_trace_row(user_id, TERM_IDEAL, wall, thread_env))

        measurements[TERM_IDEAL] = _ideal_payload(
            ideal_measurements,
            selected_users_by_term[TERM_IDEAL],
            environment,
        )

        measurements[TERM_LS] = _measure_prefix_member_variance(
            projection_runner=projection_runner,
            design=design,
            spec=specs["flat_theta"],
            member_name="discounted_LS_lambda_0.95",
            predictor_cls=projection_runner.DiscountedLeastSquaresPredictor,
            selected_user_ids=selected_users_by_term[TERM_LS],
            term=TERM_LS,
            trace_rows=trace_rows,
            thread_env=thread_env,
            perf_start=perf_start,
        )
        measurements[TERM_NN] = _measure_prefix_member_variance(
            projection_runner=projection_runner,
            design=design,
            spec=specs["stable_facts"],
            member_name="nearest_neighbor_user_matching",
            predictor_cls=projection_runner.NearestNeighborUserMatchingPredictor,
            selected_user_ids=selected_users_by_term[TERM_NN],
            term=TERM_NN,
            trace_rows=trace_rows,
            thread_env=thread_env,
            perf_start=perf_start,
        )

        revised_projection = _revised_projection(projection, measurements)
        if not _projection_is_finite(revised_projection):
            failure_reasons.append("non_finite_revised_projection")
        if failure_reasons:
            raise RuntimeError(";".join(failure_reasons))

        run_finished_at = _utc_timestamp()
        result = {
            "task_id": TASK_ID,
            "task_card_id": TASK_CARD_ID,
            "stage": "S3d PART 0 projection refinement",
            "artifact": "s3d_part0_variance_probe",
            "verdict": "measurement_emitted",
            "claim_ceiling": CLAIM_CEILING,
            "baseline": "N/A by task-card design; timing-measurement addendum only",
            "ablation": "N/A by task-card design; timing-measurement addendum only",
            "heldout_users_800_999_touched": False,
            "certificate_battery_started": False,
            "null_env_started": False,
            "forbidden_reports_absent": {
                "s3d_certificate_report.json": not (ARTIFACT_ROOT / "s3d_certificate_report.json").exists(),
                "s3d_null_env_report.json": not (ARTIFACT_ROOT / "s3d_null_env_report.json").exists(),
            },
            "pre_registered_sampling": {
                "k": 5,
                "fractional_indices": list(FRACTIONAL_INDICES),
                "selection_rule": "sort eval-user ids ascending; index = round(fraction * (n - 1)); preserve ascending resolved ids",
                "reference_user_id": REFERENCE_USER_ID,
                "heldout_range_forbidden": [800, 999],
                "resolved_user_ids_by_term": selected_users_by_term,
            },
            "single_thread_environment": environment,
            "measurements": measurements,
            "reference_user_640": {
                term: _reference_payload(payload)
                for term, payload in measurements.items()
            },
            "revised_projection": revised_projection,
            "trace_artifact": str(TRACE.relative_to(ROOT)),
            "trace_schema": ["user_id", "term", "wall_seconds", "thread_env"],
            "replay_structure": {
                "absolute_timings_machine_dependent": True,
                "replay_requirement": "rerun this script with the recorded selected_user_ids_by_term and single-thread environment; selection and callable paths must reproduce",
                "callable_paths": {
                    TERM_IDEAL: "src.fsp_pum_env.s3d_certificates.measure_s3d_ideal_one_eval_user",
                    TERM_LS: (
                        "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_projection_runner.py::_records_by_user "
                        "+ isolated fit-once score loop matching _measure_prefix_family_one_eval_user"
                    ),
                    TERM_NN: (
                        "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_projection_runner.py::_records_by_user "
                        "+ isolated fit-once score loop matching _measure_prefix_family_one_eval_user"
                    ),
                },
            },
            "producer_function": (
                "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe_runner.py::run_variance_probe"
            ),
            "input_artifacts": [
                str(FROZEN_DESIGN.relative_to(ROOT)),
                str(PROJECTION.relative_to(ROOT)),
                str(ORIGINAL_RUNNER.relative_to(ROOT)),
            ],
            "run_id": f"s3d-part0-variance-probe-{run_started_at}",
            "run_started_at": run_started_at,
            "run_finished_at": run_finished_at,
            "wall_clock_seconds": time.perf_counter() - perf_start,
            "aggregation_rule": (
                "population mean/std/min/max over k=5 pre-registered users; prefix projections use one fit wall plus "
                "aggregate score wall * 160, then original full-projection component units"
            ),
            "seed_context_episode_ids": {
                "cells": {
                    TERM_IDEAL: specs["camouflage_off"].cell_id,
                    TERM_LS: specs["flat_theta"].cell_id,
                    TERM_NN: specs["stable_facts"].cell_id,
                },
                "master_seeds": {
                    TERM_IDEAL: int(specs["camouflage_off"].master_seed),
                    TERM_LS: int(specs["flat_theta"].master_seed),
                    TERM_NN: int(specs["stable_facts"].master_seed),
                },
                "selected_user_ids_by_term": selected_users_by_term,
            },
            "source_code_hashes": _source_code_hashes(),
            "code_path_hash": _code_path_hash(),
        }
        _write_trace(trace_rows)
        _write_json(RESULT, result)
        _write_bank_ops_script()
        return result
    except Exception as exc:
        run_finished_at = _utc_timestamp()
        manifest = {
            "task_id": TASK_ID,
            "task_card_id": TASK_CARD_ID,
            "stage": "S3d PART 0 projection refinement",
            "artifact": "s3d_part0_variance_probe_failure_manifest",
            "verdict": "STOP",
            "preserved_failure": True,
            "stop_condition": str(exc),
            "heldout_users_800_999_touched": _heldout_touched_in_trace(trace_rows),
            "trace_rows_emitted_before_stop": len(trace_rows),
            "claim_ceiling": CLAIM_CEILING,
            "producer_function": (
                "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe_runner.py::run_variance_probe"
            ),
            "input_artifacts": [
                str(FROZEN_DESIGN.relative_to(ROOT)),
                str(PROJECTION.relative_to(ROOT)),
                str(ORIGINAL_RUNNER.relative_to(ROOT)),
            ],
            "run_started_at": run_started_at,
            "run_finished_at": run_finished_at,
            "wall_clock_seconds": time.perf_counter() - perf_start,
            "source_code_hashes": _source_code_hashes(),
            "code_path_hash": _code_path_hash(),
        }
        if trace_rows:
            _write_trace(trace_rows)
        _write_json(FAILURE_MANIFEST, manifest)
        _write_bank_ops_script()
        raise


def _ideal_payload(
    measurements: Sequence[Mapping[str, Any]],
    selected_user_ids: Sequence[int],
    environment: Mapping[str, Any],
) -> dict[str, Any]:
    walls = [float(item["wall_clock_seconds"]) for item in measurements]
    stats = _stats(walls)
    per_user = [
        {
            "user_id": int(item["user_id"]),
            "wall_seconds": float(item["wall_clock_seconds"]),
            "metric": float(item["metric"]),
            "turns": int(item["turns"]),
            "atom_count": int(item["atom_count"]),
        }
        for item in measurements
    ]
    projection_seconds = {
        key: float(value) * 1120.0
        for key, value in {
            "mean": stats["mean"],
            "min": stats["min"],
            "max": stats["max"],
        }.items()
    }
    return {
        "term": TERM_IDEAL,
        "cell_id": "camouflage_off",
        "member": "FactoredExactFilter",
        "measurement_kind": "ideal_one_cell_per_eval_user_wall",
        "selected_user_ids": [int(user_id) for user_id in selected_user_ids],
        "per_user": per_user,
        "per_user_wall_seconds": stats,
        "reference_user_640": _reference_from_per_user(per_user),
        "fit_once_wall_clock_seconds": None,
        "projection_rule": "mean_per_user_wall_seconds * 1120 (7 S3d cells * 160 eval users)",
        "projection_units": 1120.0,
        "projection_seconds": projection_seconds,
        "projection_cpu_hours": {key: value / 3600.0 for key, value in projection_seconds.items()},
        "single_thread_accounting": bool(environment.get("single_thread_accounting")),
        "producer_function": "src.fsp_pum_env.s3d_certificates.measure_s3d_ideal_one_eval_user",
        "aggregation_rule": "population mean/std/min/max over k=5 pre-registered eval users",
    }


def _measure_prefix_member_variance(
    *,
    projection_runner: Any,
    design: Mapping[str, Any],
    spec: Any,
    member_name: str,
    predictor_cls: Callable[..., Any],
    selected_user_ids: Sequence[int],
    term: str,
    trace_rows: list[dict[str, Any]],
    thread_env: str,
    perf_start: float,
) -> dict[str, Any]:
    family_start = time.perf_counter()
    records_by_user = projection_runner._records_by_user(design, spec.trajectory_spec)
    generated_user_ids = sorted(int(user_id) for user_id in records_by_user)
    if any(800 <= user_id <= 999 for user_id in generated_user_ids):
        raise RuntimeError(f"heldout_user_touched_in_{term}")
    fit_records = [record for user_id in range(0, 640) for record in records_by_user[user_id]]

    predictor = predictor_cls.from_design(design)
    fit_start = time.perf_counter()
    if hasattr(predictor, "fit"):
        predictor.fit(fit_records)
    else:
        for record in fit_records:
            predictor.observe(record)
    fit_seconds = time.perf_counter() - fit_start
    _assert_finite(fit_seconds, f"{term}:fit_once")

    per_user = []
    for user_id in selected_user_ids:
        _assert_wall_limit(perf_start)
        if int(user_id) not in records_by_user:
            raise RuntimeError(f"selected_user_missing:{term}:{user_id}")
        eval_records = records_by_user[int(user_id)]
        score_start = time.perf_counter()
        query_predictor = copy.deepcopy(predictor)
        y_true: list[int] = []
        y_pred: list[int] = []
        for record in eval_records:
            parsed = event_from_mapping(record)
            prediction = query_predictor.predict([parsed.action])
            distribution = prediction[str(parsed.action)]
            y_pred.append(int(np.argmax(np.asarray(distribution, dtype=float))))
            y_true.append(int(parsed.observation["symbol"]))
            query_predictor.observe(parsed)
        score_seconds = time.perf_counter() - score_start
        _assert_finite(score_seconds, f"{term}:{user_id}")
        per_user.append(
            {
                "user_id": int(user_id),
                "score_wall_seconds": float(score_seconds),
                "eval_records": len(eval_records),
                "macro_balanced_accuracy": macro_balanced_accuracy(
                    y_true,
                    y_pred,
                    alphabet_size=response_alphabet_size(design),
                ),
            }
        )
        trace_rows.append(_trace_row(user_id, term, score_seconds, thread_env))

    score_stats = _stats([float(item["score_wall_seconds"]) for item in per_user])
    one_member_cell_projection_seconds = {
        key: float(fit_seconds) + (float(value) * 160.0)
        for key, value in {
            "mean": score_stats["mean"],
            "min": score_stats["min"],
            "max": score_stats["max"],
        }.items()
    }
    return {
        "term": term,
        "cell_id": spec.cell_id,
        "variant": spec.variant,
        "member": member_name,
        "measurement_kind": "prefix_family_fit_once_score_per_eval_user",
        "selected_user_ids": [int(user_id) for user_id in selected_user_ids],
        "fit_once_wall_clock_seconds": float(fit_seconds),
        "fit_users": 640,
        "fit_records": len(fit_records),
        "record_collection_wall_clock_seconds": time.perf_counter() - family_start,
        "per_user": per_user,
        "score_wall_seconds": score_stats,
        "reference_user_640": _reference_from_per_user(per_user),
        "projection_rule": "fit_once_wall_clock_seconds + aggregate_score_wall_seconds * 160",
        "eval_users_projected_per_member_cell": 160,
        "one_member_cell_projection_seconds": one_member_cell_projection_seconds,
        "one_member_cell_projection_cpu_hours": {
            key: value / 3600.0 for key, value in one_member_cell_projection_seconds.items()
        },
        "producer_function": (
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe_runner.py::_measure_prefix_member_variance"
        ),
        "reused_original_runner_functions": [
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_projection_runner.py::_records_by_user",
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_projection_runner.py::_single_thread_environment",
        ],
        "original_runner_measurement_loop_mirrored": (
            "fit/observe train users 0..639 once, deepcopy fitted predictor per eval user, then predict/observe eval prefix"
        ),
        "aggregation_rule": "population mean/std/min/max over k=5 pre-registered eval users",
    }


def _revised_projection(projection: Mapping[str, Any], measurements: Mapping[str, Any]) -> dict[str, Any]:
    components = projection["full_part0_projection"]["components"]
    original_total_seconds = float(projection["full_part0_projection"]["total_projected_seconds"])
    original_target_seconds = {
        term: float(components[component_name]["projected_seconds"])
        for term, component_name in TARGET_COMPONENTS.items()
    }
    static_seconds = original_total_seconds - sum(original_target_seconds.values())

    term_contributions: dict[str, Any] = {}
    for term, payload in measurements.items():
        component_name = TARGET_COMPONENTS[term]
        original_component = components[component_name]
        if term == TERM_IDEAL:
            component_units = 1.0
            projection_seconds = dict(payload["projection_seconds"])
        else:
            component_units = float(original_component["projected_units"])
            projection_seconds = {
                key: float(value) * component_units
                for key, value in payload["one_member_cell_projection_seconds"].items()
            }
        term_contributions[term] = {
            "original_component": component_name,
            "original_projected_seconds": float(original_component["projected_seconds"]),
            "original_projected_cpu_hours": float(original_component["projected_cpu_hours"]),
            "full_projection_component_units": component_units,
            "revised_component_projection_seconds": projection_seconds,
            "revised_component_projection_cpu_hours": {
                key: value / 3600.0 for key, value in projection_seconds.items()
            },
        }

    revised_total_seconds = static_seconds + sum(
        float(item["revised_component_projection_seconds"]["mean"])
        for item in term_contributions.values()
    )
    min_total_seconds = static_seconds + sum(
        float(item["revised_component_projection_seconds"]["min"])
        for item in term_contributions.values()
    )
    max_total_seconds = static_seconds + sum(
        float(item["revised_component_projection_seconds"]["max"])
        for item in term_contributions.values()
    )
    band = [min_total_seconds / 3600.0, max_total_seconds / 3600.0]
    if band[1] < S3D_CPU_HOUR_LIMIT:
        relation = "entire_min_max_band_below_12_0"
    elif band[0] > S3D_CPU_HOUR_LIMIT:
        relation = "entire_min_max_band_above_12_0"
    else:
        relation = "min_max_band_crosses_12_0"
    return {
        "original_total_projected_seconds": original_total_seconds,
        "original_total_projected_cpu_hours": float(projection["full_part0_projection"]["total_projected_cpu_hours"]),
        "static_non_target_projected_seconds": static_seconds,
        "static_non_target_projected_cpu_hours": static_seconds / 3600.0,
        "term_contributions": term_contributions,
        "revised_total_projected_seconds": revised_total_seconds,
        "revised_total_projected_cpu_hours": revised_total_seconds / 3600.0,
        "min_max_band_seconds": [min_total_seconds, max_total_seconds],
        "min_max_band_cpu_hours": band,
        "band_crosses_12_0_cpu_hours": bool(band[0] <= S3D_CPU_HOUR_LIMIT <= band[1]),
        "band_relation_to_12_0_cpu_hours": relation,
        "cpu_hour_line_unchanged": S3D_CPU_HOUR_LIMIT,
        "projection_formula": (
            "original full projection with the three target components replaced by k=5 mean/min/max timing; "
            "non-target components kept from s3d_compute_projection.json"
        ),
        "does_not_overturn_or_strengthen_banked_stop": True,
    }


def _selected_eval_user_ids(eval_user_range: tuple[int, int]) -> list[int]:
    start, end = int(eval_user_range[0]), int(eval_user_range[1])
    users = list(range(start, end + 1))
    selected = [users[int(round(fraction * (len(users) - 1)))] for fraction in FRACTIONAL_INDICES]
    selected = sorted(dict.fromkeys(selected))
    if len(selected) != len(FRACTIONAL_INDICES):
        raise RuntimeError(f"pre_registered_selection_duplicate:{selected}")
    return selected


def _stats(values: Sequence[float]) -> dict[str, float]:
    if not values:
        raise RuntimeError("cannot aggregate empty timing vector")
    for value in values:
        _assert_finite(value, "timing_vector")
    return {
        "count": float(len(values)),
        "mean": float(statistics.fmean(values)),
        "std": float(statistics.pstdev(values)),
        "min": float(min(values)),
        "max": float(max(values)),
    }


def _reference_payload(payload: Mapping[str, Any]) -> Mapping[str, Any] | None:
    return payload.get("reference_user_640")


def _reference_from_per_user(per_user: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    for item in per_user:
        if int(item["user_id"]) == REFERENCE_USER_ID:
            return dict(item)
    return None


def _trace_row(user_id: int, term: str, wall_seconds: float, thread_env: str) -> dict[str, Any]:
    return {
        "user_id": int(user_id),
        "term": term,
        "wall_seconds": float(wall_seconds),
        "thread_env": thread_env,
    }


def _write_trace(rows: Sequence[Mapping[str, Any]]) -> None:
    TRACE.parent.mkdir(parents=True, exist_ok=True)
    with TRACE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["user_id", "term", "wall_seconds", "thread_env"])
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "user_id": int(row["user_id"]),
                    "term": str(row["term"]),
                    "wall_seconds": f"{float(row['wall_seconds']):.12f}",
                    "thread_env": str(row["thread_env"]),
                }
            )


def _load_projection_runner() -> Any:
    spec = importlib.util.spec_from_file_location("s3d_part0_projection_runner_for_variance", ORIGINAL_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load original runner: {ORIGINAL_RUNNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _single_thread_environment() -> dict[str, Any]:
    projection_runner = _load_projection_runner()
    env = projection_runner._single_thread_environment()
    env["variance_probe_env_threads"] = {key: os.environ.get(key, "") for key in THREAD_ENV_KEYS}
    env["variance_probe_single_thread_accounting"] = True
    return env


def _assert_single_thread_environment(environment: Mapping[str, Any]) -> None:
    env_threads = environment.get("env_threads", {})
    variance_threads = environment.get("variance_probe_env_threads", {})
    for key in THREAD_ENV_KEYS:
        if str(env_threads.get(key, "")) != "1" or str(variance_threads.get(key, "")) != "1":
            raise RuntimeError(f"single_thread_env_not_1:{key}")
    if environment.get("torch_device") != "cpu":
        raise RuntimeError("torch_device_not_cpu")
    if int(environment.get("torch_num_threads", -1)) != 1:
        raise RuntimeError("torch_num_threads_not_1")
    if int(environment.get("torch_num_interop_threads", -1)) != 1:
        raise RuntimeError("torch_num_interop_threads_not_1")


def _thread_env_label(environment: Mapping[str, Any]) -> str:
    env_threads = environment.get("env_threads", {})
    fields = [f"{key}={env_threads.get(key, '')}" for key in THREAD_ENV_KEYS]
    fields.append(f"torch_num_threads={environment.get('torch_num_threads')}")
    fields.append(f"torch_num_interop_threads={environment.get('torch_num_interop_threads')}")
    fields.append(f"torch_device={environment.get('torch_device')}")
    return ";".join(fields)


def _assert_forbidden_reports_absent() -> None:
    forbidden = [ARTIFACT_ROOT / "s3d_certificate_report.json", ARTIFACT_ROOT / "s3d_null_env_report.json"]
    present = [str(path.relative_to(ROOT)) for path in forbidden if path.exists()]
    if present:
        raise RuntimeError(f"forbidden_report_present:{present}")


def _assert_no_heldout_users(selected_users_by_term: Mapping[str, Sequence[int]]) -> None:
    touched = [
        int(user_id)
        for users in selected_users_by_term.values()
        for user_id in users
        if 800 <= int(user_id) <= 999
    ]
    if touched:
        raise RuntimeError(f"heldout_users_800_999_selected:{touched}")


def _heldout_touched_in_trace(trace_rows: Sequence[Mapping[str, Any]]) -> bool:
    return any(800 <= int(row["user_id"]) <= 999 for row in trace_rows)


def _assert_wall_limit(perf_start: float) -> None:
    if (time.perf_counter() - perf_start) / 3600.0 > WALL_CPU_HOUR_LIMIT:
        raise RuntimeError("variance_probe_runtime_exceeded_12_cpu_hours")


def _assert_finite(value: float, label: str) -> None:
    if not math.isfinite(float(value)):
        raise RuntimeError(f"non_finite_timing:{label}")


def _projection_is_finite(payload: Any) -> bool:
    if isinstance(payload, Mapping):
        return all(_projection_is_finite(value) for value in payload.values())
    if isinstance(payload, list):
        return all(_projection_is_finite(value) for value in payload)
    if isinstance(payload, float):
        return math.isfinite(payload)
    return True


def _write_bank_ops_script() -> None:
    try:
        expected_head = _read_git_head_without_git()
    except Exception as exc:  # pragma: no cover - filesystem-specific fallback
        expected_head = f"UNAVAILABLE_NO_GIT_COMMAND_USED:{type(exc).__name__}:{exc}"
    allowlist = [
        "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe_runner.py",
        "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe.json",
        "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe_trace.csv",
        "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe_failure_manifest.json",
        "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe_bank_ops.ps1",
    ]
    rendered_allowlist = "\n".join(f"  '{item}'" for item in allowlist)
    script = f"""# Proposed operator-only bank ops for {TASK_CARD_ID}
# Codex generated this script but did not run it.  It performs no push.
$ErrorActionPreference = 'Stop'
$ExpectedHead = '{expected_head}'
$CommitMessage = 'bank {TASK_CARD_ID} variance probe artifacts'
$Allowlist = @(
{rendered_allowlist}
)

$ActualHead = (git rev-parse HEAD).Trim()
if ($ActualHead -ne $ExpectedHead) {{
  throw \"HEAD pin mismatch: expected $ExpectedHead got $ActualHead\"
}}

git reset --

$ExistingAllowlist = @()
foreach ($Path in $Allowlist) {{
  if (Test-Path -LiteralPath $Path) {{
    $ExistingAllowlist += $Path
  }}
}}
if ($ExistingAllowlist.Count -lt 4) {{
  throw \"Too few variance-probe files exist for scoped banking: $($ExistingAllowlist.Count)\"
}}

git add -- $ExistingAllowlist

$Staged = @(git diff --cached --name-only)
if ($Staged.Count -ne $ExistingAllowlist.Count) {{
  throw \"Staged count mismatch: expected $($ExistingAllowlist.Count) got $($Staged.Count): $($Staged -join ', ')\"
}}

$Unexpected = @($Staged | Where-Object {{ $Allowlist -notcontains $_ }})
if ($Unexpected.Count -ne 0) {{
  throw \"Unexpected staged paths: $($Unexpected -join ', ')\"
}}

$Deleted = @(git diff --cached --name-status | Where-Object {{ $_ -match '^D\\s' }})
if ($Deleted.Count -ne 0) {{
  throw \"Zero-deletion gate failed: $($Deleted -join '; ')\"
}}

foreach ($Path in $ExistingAllowlist) {{
  Get-FileHash -Algorithm SHA256 -LiteralPath $Path | Format-List
}}

git commit -m $CommitMessage -- $ExistingAllowlist

Write-Host 'Banked scoped variance-probe commit locally. No push was performed by this script.'
"""
    BANK_OPS.write_text(script, encoding="utf-8")


def _read_git_head_without_git() -> str:
    git_dir = ROOT / ".git"
    head_text = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
    if head_text.startswith("ref:"):
        ref = head_text.split(" ", 1)[1].strip()
        ref_path = git_dir / ref
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8").strip()
        packed_refs = git_dir / "packed-refs"
        if packed_refs.exists():
            for line in packed_refs.read_text(encoding="utf-8").splitlines():
                if not line or line.startswith("#") or line.startswith("^"):
                    continue
                sha, packed_ref = line.split(" ", 1)
                if packed_ref.strip() == ref:
                    return sha.strip()
        raise RuntimeError(f"git ref not found: {ref}")
    return head_text


def _source_code_hashes() -> dict[str, str]:
    paths = _code_paths()
    return {str(path.relative_to(ROOT)): _sha256(path) for path in paths}


def _code_path_hash() -> str:
    h = hashlib.sha256()
    for path in _code_paths():
        h.update(str(path.relative_to(ROOT)).encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _code_paths() -> list[Path]:
    return [
        Path(__file__),
        ORIGINAL_RUNNER,
        ROOT / "src" / "fsp_pum_env" / "s3d_certificates.py",
        ROOT / "src" / "fsp_pum_env" / "trajectory_sets.py",
        ROOT / "src" / "fsp_pum_env" / "simulator.py",
        ROOT / "src" / "fsp_pum_env" / "factored_filter.py",
        ROOT / "src" / "fsp_pum_env" / "battery" / "base.py",
        ROOT / "src" / "fsp_pum_env" / "battery" / "obs_decoders.py",
        ROOT / "src" / "fsp_pum_env" / "battery" / "seq_models.py",
        ROOT / "src" / "fsp_pum_env" / "battery" / "graph_cache.py",
        ROOT / "src" / "fsp_pum_env" / "battery" / "rag_nn.py",
        ROOT / "src" / "fsp_pum_env" / "battery" / "degenerates.py",
        ROOT / "src" / "fsp_pum_env" / "battery" / "ls_regressors.py",
    ]


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, Path):
        return str(value)
    return value


def _sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def main() -> int:
    result = run_variance_probe()
    print(
        json.dumps(
            {
                "result_path": str(RESULT.relative_to(ROOT)),
                "trace_path": str(TRACE.relative_to(ROOT)),
                "bank_ops_path": str(BANK_OPS.relative_to(ROOT)),
                "revised_total_projected_cpu_hours": result["revised_projection"][
                    "revised_total_projected_cpu_hours"
                ],
                "min_max_band_cpu_hours": result["revised_projection"]["min_max_band_cpu_hours"],
                "band_relation_to_12_0_cpu_hours": result["revised_projection"][
                    "band_relation_to_12_0_cpu_hours"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
