"""S3d PART-0 line-30 CPU-time re-gate runner.

Task-local artifact generator for:
FSP-PUM-ENV-IDPROBE-001A-S3D-PART0-CPUTIME-REGATE-001A

This runner fixes only the PART-0 line/gate metric basis.  It records
per-unit process CPU-time (user+sys via time.process_time) alongside wall-clock
time and stops after the re-gate.  It does not launch the S3d should-win or
NULL-env battery and does not change any fit/score/certificate/NULL metric
logic.
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
import shutil
import statistics
import sys
import time
import traceback
from typing import Any, Callable, Mapping, Sequence


THREAD_ENV_KEYS = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS")
for _KEY in THREAD_ENV_KEYS:
    os.environ[_KEY] = "1"

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.fsp_pum_env.battery.base import event_from_mapping, response_alphabet_size
from src.fsp_pum_env.s3d_certificates import build_s3d_cert_set_specs, macro_balanced_accuracy
from src.fsp_pum_env.trajectory_sets import load_frozen_design


TASK_ID = "FSP-PUM-ENV-IDPROBE-001A"
TASK_CARD_ID = "FSP-PUM-ENV-IDPROBE-001A-S3D-PART0-CPUTIME-REGATE-001A"
ARTIFACT_ROOT = ROOT / "artifacts" / TASK_ID
BATTERY_RUNNER_PATH = ARTIFACT_ROOT / "s3d_battery_runner_line30.py"
ORIGINAL_PART0_RUNNER_PATH = ARTIFACT_ROOT / "s3d_part0_projection_runner.py"
FROZEN_DESIGN = ARTIFACT_ROOT / "frozen_design.json"
OUTPUT = ARTIFACT_ROOT / "s3d_compute_projection_line30.0_cputime_regate.json"
RESULT = ARTIFACT_ROOT / "result.json"
FAILURE_MANIFEST = ARTIFACT_ROOT / "failure_manifest.json"
CLAIM_CEILING_PATH = ARTIFACT_ROOT / "claim_ceiling"
BANK_OPS = ARTIFACT_ROOT / "s3d_operator_bank_ops_proposal_cputime_regate.ps1"
FIX_CARD = ROOT / "docs" / "codex" / "tasks" / "FSP-PUM-ENV-IDPROBE-001A-S3D-PART0-CPUTIME-REGATE-001A.md"

LINE_CPU_HOURS = 30.0
DOMINANT_REMEASURE_USERS = (640, 720, 799)

CLAIM_CEILING = (
    "line-30, 001B frozen-contract S3d metric-compliant PART-0 gate result only; "
    "no battery, certificate, NULL-env, environment-validity, gap, mechanism, learning, agency, EGO, or readiness claim"
)

WALL_GATE_ARTIFACTS = (
    "result.json",
    "failure_manifest.json",
    "s3d_compute_projection_line30.0.json",
    "s3d_certificate_report.json",
    "s3d_null_env_report.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "replay_report.json",
    "trace.jsonl",
    "trace.csv",
)

PROTECTED_BYTE_UNCHANGED = (
    ARTIFACT_ROOT / "frozen_design.json",
    ARTIFACT_ROOT / "s3d_compute_projection.json",
    ARTIFACT_ROOT / "s3d_compute_projection_line30.0.json",
    ARTIFACT_ROOT / "s3d_part0_projection_runner.py",
    ARTIFACT_ROOT / "s3d_part0_variance_probe.json",
    ARTIFACT_ROOT / "s3d_part0_variance_probe_trace.csv",
    ARTIFACT_ROOT / "s3d_part0_variance_probe_runner.py",
    ARTIFACT_ROOT / "s3d_001b_impl_report.json",
    ARTIFACT_ROOT / "s3d_001b_impl_trace.jsonl",
    ROOT / "docs" / "codex" / "tasks" / "FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-EXEC-001A.md",
    ROOT / "docs" / "codex" / "tasks" / "FSP-PUM-ENV-IDPROBE-001A-S3D-SHOULD-WIN-NULL-ENV-SPEC-001B.md",
    ROOT / "docs" / "codex" / "tasks" / "FSP-PUM-ENV-IDPROBE-001A-S3D-BUDGET-DECISION-001A.md",
)


def main() -> int:
    payload = run()
    print(
        json.dumps(
            {
                "artifact": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
                "verdict": payload.get("verdict"),
                "line_relation": payload.get("line_relation"),
                "final_cpu_projected_hours": payload.get("final_cpu_time_projection", {}).get("total_projected_cpu_hours"),
                "claim_ceiling": CLAIM_CEILING,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def run() -> dict[str, Any]:
    run_started_at = _utc_timestamp()
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    run_id = f"s3d-part0-cputime-regate-line30.0-{run_started_at}"
    battery = _load_battery_runner()
    part0 = _load_original_part0_runner()
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

    protected_before = _hash_paths(PROTECTED_BYTE_UNCHANGED)
    wall_preservation = _preserve_wall_gate_artifacts()
    cert_null_before = _certificate_null_snapshot()

    common: dict[str, Any] = {
        "task_id": TASK_ID,
        "task_card_id": TASK_CARD_ID,
        "stage": "S3d",
        "part": "PART-0 CPU-time re-gate under signed line",
        "artifact": OUTPUT.name.removesuffix(".json"),
        "claim_ceiling": CLAIM_CEILING,
        "run_id": run_id,
        "run_started_at": run_started_at,
        "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_cputime_regate_runner.py::run",
        "input_artifacts": [
            _rel(FROZEN_DESIGN),
            "docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-EXEC-001A.md",
            "docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-SHOULD-WIN-NULL-ENV-SPEC-001B.md",
            "docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-BUDGET-DECISION-001A.md",
            _rel(ARTIFACT_ROOT / "s3d_compute_projection_line30.0.json"),
        ],
        "code_path_hash": _code_path_hash(battery),
        "line_cpu_hours": LINE_CPU_HOURS,
        "wall_gate_preservation": wall_preservation,
    }

    try:
        precondition = battery._verify_preconditions()
        common["precondition"] = precondition
        if not bool(precondition.get("passed")):
            payload = {
                **common,
                "verdict": "STOP_PRECONDITION_UNMET",
                "line_relation": "not_evaluated_precondition_failed",
                "stop_condition": "S3d CPU-time re-gate preconditions failed before measurement",
                "failure_manifest_required": True,
                "protected_artifacts_after": _hash_paths(PROTECTED_BYTE_UNCHANGED),
                "banked_artifacts_byte_unchanged": False,
                "certificate_null_metric_bitwise_unchanged": _certificate_null_unchanged(cert_null_before),
                "run_finished_at": _utc_timestamp(),
                "wall_clock_seconds": time.perf_counter() - wall_start,
                "process_cpu_seconds": time.process_time() - cpu_start,
            }
            _write_failure_manifest(payload, "STOP_PRECONDITION_UNMET", payload["stop_condition"])
            _write_result(payload)
            _write_claim_ceiling()
            _write_bank_ops(payload)
            _write_json(OUTPUT, payload)
            return payload

        applied_line = float(precondition["signed_budget"]["line_cpu_hours"])
        if applied_line != LINE_CPU_HOURS:
            raise RuntimeError(f"unexpected_signed_line:{applied_line}")

        design = load_frozen_design(FROZEN_DESIGN)
        environment = battery._single_thread_environment()
        specs = {spec.cell_id: spec for spec in build_s3d_cert_set_specs(design)}
        selected_recipes = battery._selected_recipe_configs()
        selected_recipe_hashes = {name: _sha256(path) for name, path in battery._selected_recipe_paths().items()}
        vocabulary = battery._read_json(battery.VOCABULARY)

        measurements: dict[str, Any] = {}
        measurements["cert_set_generation"] = _measure_generation_cputime(battery, design, specs["constant_none"], run_id)
        measurements["ideal_per_user_one_cell"] = _measure_ideal_cputime(
            battery, design, specs["camouflage_off"], user_id=640, run_id=run_id
        )
        measurements["logreg_F1_selected"] = _timed_selected_measurement(
            "logreg_F1_selected",
            lambda: part0._measure_sklearn_selected(
                design,
                specs["camouflage_off"],
                selected_recipes["obs_decoder_logreg"],
                features="F1",
            ),
            run_id=run_id,
            projected_seconds_key="fit_plus_validation",
        )
        measurements["logreg_F2_reference"] = _timed_selected_measurement(
            "logreg_F2_reference",
            lambda: part0._measure_sklearn_selected(
                design,
                specs["camouflage_off"],
                battery.obs_decoders.decoder_grid("obs_decoder_logreg")[4],
                features="F2",
                vocabulary=vocabulary,
            ),
            run_id=run_id,
            projected_seconds_key="fit_plus_validation",
        )
        measurements["gbt_half_data_selected"] = _timed_selected_measurement(
            "gbt_half_data_selected",
            lambda: part0._measure_sklearn_selected(
                design,
                specs["camouflage_off"],
                selected_recipes["obs_decoder_gbt"],
                features="F2",
                vocabulary=vocabulary,
                fit_user_filter=set(battery.obs_decoders.gbt_fit_user_ids()),
            ),
            run_id=run_id,
            projected_seconds_key="fit_plus_validation",
        )
        measurements["gru_selected"] = _timed_selected_measurement(
            "gru_selected",
            lambda: part0._measure_gru_selected(
                design,
                specs["camouflage_off"],
                selected_recipes["obs_decoder_gru"],
                member_kind="obs_decoder_gru",
            ),
            run_id=run_id,
            projected_seconds_key="fit_plus_validation",
        )
        measurements["seq_full_selected"] = _timed_selected_measurement(
            "seq_full_selected",
            lambda: part0._measure_gru_selected(
                design,
                specs["constant_none"],
                selected_recipes["seq_full_history_no_action_conditioning"],
                member_kind="seq_full_history_no_action_conditioning",
            ),
            run_id=run_id,
            projected_seconds_key="fit_plus_validation",
        )
        measurements["seq_W15_selected"] = _timed_selected_measurement(
            "seq_W15_selected",
            lambda: part0._measure_gru_selected(
                design,
                specs["low_diversity"],
                selected_recipes["seq_window_with_action_conditioning_W15_no_cross_session_persistence"],
                member_kind="seq_window_with_action_conditioning_W15_no_cross_session_persistence",
            ),
            run_id=run_id,
            projected_seconds_key="fit_plus_validation",
        )
        measurements["table_family"] = _measure_prefix_family_one_eval_user_cputime(
            part0,
            design,
            specs["low_diversity"],
            {
                "successor_map": battery.SuccessorMapPredictor,
                "transition_table": battery.TransitionTablePredictor,
                "count_table": battery.CountTablePredictor,
                "fsm_planner": battery.FsmPlannerPredictor,
                "episodic_traversal": battery.EpisodicTraversalPredictor,
            },
            eval_user_id=640,
            run_id=run_id,
        )
        measurements["retrieval_family"] = _measure_prefix_family_one_eval_user_cputime(
            part0,
            design,
            specs["stable_facts"],
            {
                "rag_k5_episode_retrieval": battery.RagK5EpisodeRetrievalPredictor,
                "nearest_neighbor_user_matching": battery.NearestNeighborUserMatchingPredictor,
            },
            eval_user_id=640,
            run_id=run_id,
        )
        measurements["degenerate_family"] = _measure_prefix_family_one_eval_user_cputime(
            part0,
            design,
            specs["constant_none"],
            {
                "predict_all": battery.PredictAllPredictor,
                "predict_none": battery.PredictNonePredictor,
                "majority": battery.MajorityPredictor,
                "global_prior": battery.GlobalPriorPredictor,
            },
            eval_user_id=640,
            run_id=run_id,
        )
        measurements["ls_online_family"] = _measure_prefix_family_one_eval_user_cputime(
            part0,
            design,
            specs["flat_theta"],
            {
                "discounted_LS_lambda_0.95": battery.DiscountedLeastSquaresPredictor,
                "running_average_preference_regressor": battery.RunningAveragePreferenceRegressor,
            },
            eval_user_id=640,
            run_id=run_id,
        )
        measurements["bootstrap"] = _timed_selected_measurement(
            "bootstrap",
            lambda: part0._measure_bootstrap_unit(),
            run_id=run_id,
            projected_seconds_key="wall_clock",
        )

        initial_projection = _project_total_cputime(measurements, applied_line, replacements=None)
        serial_remeasurements = _run_dominant_serial_remeasurements(battery, part0, design, specs, run_id)
        final_projection = _project_total_cputime(measurements, applied_line, replacements=serial_remeasurements)
        wall_gate_ablation = _wall_gate_ablation()
        replay = _replay_projection(final_projection, applied_line, wall_gate_ablation)

        protected_after = _hash_paths(PROTECTED_BYTE_UNCHANGED)
        banked_unchanged = protected_before == protected_after
        cert_null_unchanged = _certificate_null_unchanged(cert_null_before)
        heldout_touched = _heldout_touched(measurements, serial_remeasurements)
        line_relation = (
            "within_line"
            if float(final_projection["total_projected_cpu_hours"]) <= applied_line
            else "exceeds_line"
        )
        verdict = (
            "S3D_PART0_CPUTIME_REGATE_WITHIN_LINE_PENDING_AUDIT"
            if line_relation == "within_line"
            else "STOP_s3d_part0_cputime_projection_exceeds_line"
        )
        stop_condition = None
        if line_relation != "within_line":
            stop_condition = (
                f"PART-0 CPU-time projection {final_projection['total_projected_cpu_hours']} CPU-h "
                f"exceeded signed line {applied_line}"
            )
        if heldout_touched:
            verdict = "STOP_HELDOUT_800_999_TOUCHED"
            line_relation = "invalid_heldout_touched"
            stop_condition = "heldout users 800-999 were touched during re-gate"
        if not banked_unchanged:
            verdict = "STOP_PROTECTED_ARTIFACT_MUTATION"
            line_relation = "invalid_protected_artifact_mutation"
            stop_condition = "protected/banked artifact byte hash changed during re-gate"
        if not cert_null_unchanged["unchanged"]:
            verdict = "STOP_CERTIFICATE_NULL_METRIC_MUTATION"
            line_relation = "invalid_certificate_null_metric_mutation"
            stop_condition = "certificate or NULL metric artifact changed during re-gate"

        unit_timings = _flatten_unit_timings(measurements, initial_projection, serial_remeasurements)
        payload = {
            **common,
            "verdict": verdict,
            "line_relation": line_relation,
            "stop_condition": stop_condition,
            "applied_cpu_hour_limit": applied_line,
            "rule_source": "001B",
            "single_thread_environment": environment,
            "selected_recipe_sha256": selected_recipe_hashes,
            "measurements": measurements,
            "initial_cpu_time_projection_before_dominant_remeasure": initial_projection,
            "dominant_serial_remeasurements": serial_remeasurements,
            "final_cpu_time_projection": final_projection,
            "cpu_hour_projection_total": float(final_projection["total_projected_cpu_hours"]),
            "wall_clock_based_cpu_hours_disclosed": float(final_projection["total_projected_wall_hours"]),
            "wall_clock_ablation_baseline": wall_gate_ablation,
            "replay": replay,
            "unit_timings": unit_timings,
            "wall_cpu_ratio_flag_count": len(unit_timings["wall_cpu_ratio_flags_gt_1_25"]),
            "wall_cpu_ratio_flags_gt_1_25": unit_timings["wall_cpu_ratio_flags_gt_1_25"],
            "certificate_null_metric_bitwise_unchanged": cert_null_unchanged,
            "protected_artifacts_before": protected_before,
            "protected_artifacts_after": protected_after,
            "banked_artifacts_byte_unchanged": banked_unchanged,
            "heldout_users_800_999_touched": heldout_touched,
            "heldout_users_800_999_not_touched_assertion": not heldout_touched,
            "fit_score_metric_logic_changed": False,
            "battery_launched": False,
            "run_finished_at": _utc_timestamp(),
            "wall_clock_seconds": time.perf_counter() - wall_start,
            "process_cpu_seconds": time.process_time() - cpu_start,
            "aggregation_rule": (
                "Initial projection uses measured process CPU seconds for each unit; final gate replaces the "
                "three dominant components (ideal, nearest_neighbor_user_matching, discounted_LS_lambda_0.95) "
                "with serial-isolation mean process CPU seconds over eval users 640, 720, and 799."
            ),
        }
        _write_json(OUTPUT, payload)
        _write_claim_ceiling()
        _write_result(payload)
        if line_relation == "within_line":
            _normalize_historical_wall_failure_manifest(payload)
        else:
            _write_failure_manifest(payload, verdict, str(stop_condition))
        _write_bank_ops(payload)
        return payload
    except BaseException as exc:
        protected_after = _hash_paths(PROTECTED_BYTE_UNCHANGED)
        payload = {
            **common,
            "verdict": "STOP_UNEXPECTED_EXCEPTION",
            "line_relation": "invalid_exception",
            "stop_condition": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
            "protected_artifacts_after": protected_after,
            "banked_artifacts_byte_unchanged": protected_before == protected_after,
            "certificate_null_metric_bitwise_unchanged": _certificate_null_unchanged(cert_null_before),
            "run_finished_at": _utc_timestamp(),
            "wall_clock_seconds": time.perf_counter() - wall_start,
            "process_cpu_seconds": time.process_time() - cpu_start,
        }
        _write_json(OUTPUT, payload)
        _write_failure_manifest(payload, "STOP_UNEXPECTED_EXCEPTION", payload["stop_condition"])
        _write_result(payload)
        _write_claim_ceiling()
        _write_bank_ops(payload)
        raise


def _measure_generation_cputime(battery: Any, design: Mapping[str, Any], spec: Any, run_id: str) -> dict[str, Any]:
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    member_sha, adjudicator_sha, member_bytes, adjudicator_bytes, record_count = battery._hash_spec_streams(
        design,
        spec.trajectory_spec,
    )
    wall_seconds = time.perf_counter() - wall_start
    cpu_seconds = time.process_time() - cpu_start
    ratio = _ratio(wall_seconds, cpu_seconds)
    return {
        "unit": "one_cert_set_generation",
        "cell_id": spec.cell_id,
        "variant": spec.variant,
        "member_view_sha256": member_sha,
        "adjudicator_only_sha256": adjudicator_sha,
        "member_view_record_count": int(record_count),
        "member_view_estimated_raw_bytes": int(member_bytes),
        "adjudicator_only_estimated_raw_bytes": int(adjudicator_bytes),
        "wall_clock_seconds": wall_seconds,
        "process_cpu_seconds": cpu_seconds,
        "wall_cpu_ratio": ratio,
        "wall_cpu_ratio_flag_gt_1_25": bool(ratio > 1.25),
        "producer_function": "src.fsp_pum_env.trajectory_sets._hash_spec_streams",
        "timing_producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_cputime_regate_runner.py::_measure_generation_cputime",
        "run_id": run_id,
        "aggregation_rule": "one measured cert-set generation multiplied by seven S3d cells",
    }


def _measure_ideal_cputime(
    battery: Any,
    design: Mapping[str, Any],
    spec: Any,
    *,
    user_id: int,
    run_id: str,
) -> dict[str, Any]:
    if not 640 <= int(user_id) <= 799:
        raise RuntimeError(f"forbidden_ideal_eval_user:{user_id}")
    from src.fsp_pum_env.s3d_certificates import measure_s3d_ideal_one_eval_user

    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    measurement = measure_s3d_ideal_one_eval_user(design, spec, user_id=int(user_id))
    outer_wall = time.perf_counter() - wall_start
    cpu_seconds = time.process_time() - cpu_start
    ratio = _ratio(float(measurement["wall_clock_seconds"]), cpu_seconds)
    measurement["process_cpu_seconds"] = cpu_seconds
    measurement["process_cpu_hours"] = cpu_seconds / 3600.0
    measurement["legacy_cpu_hours_field_basis"] = "wall_clock_seconds/3600 from src.fsp_pum_env.s3d_certificates.measure_s3d_ideal_one_eval_user"
    measurement["outer_wall_clock_seconds"] = outer_wall
    measurement["wall_cpu_ratio"] = ratio
    measurement["wall_cpu_ratio_flag_gt_1_25"] = bool(ratio > 1.25)
    measurement["timing_producer_function"] = "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_cputime_regate_runner.py::_measure_ideal_cputime"
    measurement["run_id"] = run_id
    measurement["aggregation_rule"] = "one ideal eval user for one cell multiplied by seven cells and 160 eval users per cell"
    return measurement


def _timed_selected_measurement(
    label: str,
    call: Callable[[], dict[str, Any]],
    *,
    run_id: str,
    projected_seconds_key: str,
) -> dict[str, Any]:
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    measurement = call()
    outer_wall = time.perf_counter() - wall_start
    cpu_seconds = time.process_time() - cpu_start
    if projected_seconds_key == "fit_plus_validation":
        wall_for_ratio = float(measurement["fit_plus_validation_wall_clock_seconds"])
        measurement["fit_plus_validation_process_cpu_seconds"] = cpu_seconds
    elif projected_seconds_key == "wall_clock":
        wall_for_ratio = float(measurement["wall_clock_seconds"])
        measurement["process_cpu_seconds"] = cpu_seconds
    else:
        raise ValueError(projected_seconds_key)
    ratio = _ratio(wall_for_ratio, cpu_seconds)
    measurement["outer_wall_clock_seconds"] = outer_wall
    measurement["outer_process_cpu_seconds"] = cpu_seconds
    measurement["process_cpu_seconds"] = cpu_seconds
    measurement["wall_cpu_ratio"] = ratio
    measurement["wall_cpu_ratio_flag_gt_1_25"] = bool(ratio > 1.25)
    measurement["timing_label"] = label
    measurement["timing_producer_function"] = "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_cputime_regate_runner.py::_timed_selected_measurement"
    measurement["run_id"] = run_id
    measurement["aggregation_rule"] = "selected sklearn/GRU/bootstrap measurement call bracketed by time.process_time without changing fit/score logic"
    return measurement


def _measure_prefix_family_one_eval_user_cputime(
    part0: Any,
    design: Mapping[str, Any],
    spec: Any,
    member_classes: Mapping[str, Callable[..., Any]],
    *,
    eval_user_id: int,
    run_id: str,
) -> dict[str, Any]:
    if not 640 <= int(eval_user_id) <= 799:
        raise RuntimeError(f"forbidden_prefix_eval_user:{eval_user_id}")
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    collect_wall_start = time.perf_counter()
    collect_cpu_start = time.process_time()
    records_by_user = part0._records_by_user(design, spec.trajectory_spec)
    fit_records = [record for user_id in range(0, 640) for record in records_by_user[user_id]]
    eval_records = records_by_user[int(eval_user_id)]
    collect_wall_seconds = time.perf_counter() - collect_wall_start
    collect_cpu_seconds = time.process_time() - collect_cpu_start
    members: dict[str, Any] = {}
    for member, cls in member_classes.items():
        member_wall_start = time.perf_counter()
        member_cpu_start = time.process_time()
        predictor = cls.from_design(design)
        fit_wall_start = time.perf_counter()
        fit_cpu_start = time.process_time()
        if hasattr(predictor, "fit"):
            predictor.fit(fit_records)
        else:
            for record in fit_records:
                predictor.observe(record)
        fit_wall_seconds = time.perf_counter() - fit_wall_start
        fit_cpu_seconds = time.process_time() - fit_cpu_start
        score_wall_start = time.perf_counter()
        score_cpu_start = time.process_time()
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
        score_wall_seconds = time.perf_counter() - score_wall_start
        score_cpu_seconds = time.process_time() - score_cpu_start
        projected_wall = fit_wall_seconds + (score_wall_seconds * 160.0)
        projected_cpu = fit_cpu_seconds + (score_cpu_seconds * 160.0)
        ratio = _ratio(projected_wall, projected_cpu)
        members[member] = {
            "member": member,
            "cell_id": spec.cell_id,
            "variant": spec.variant,
            "fit_users": 640,
            "eval_user_id_measured": int(eval_user_id),
            "eval_users_projected_per_member_cell": 160,
            "fit_records": len(fit_records),
            "eval_records_one_user": len(eval_records),
            "fit_wall_clock_seconds": fit_wall_seconds,
            "fit_process_cpu_seconds": fit_cpu_seconds,
            "score_one_eval_user_wall_clock_seconds": score_wall_seconds,
            "score_one_eval_user_process_cpu_seconds": score_cpu_seconds,
            "projected_one_member_cell_seconds": projected_wall,
            "projected_one_member_cell_wall_seconds": projected_wall,
            "projected_one_member_cell_process_cpu_seconds": projected_cpu,
            "one_eval_user_macro_balanced_accuracy": macro_balanced_accuracy(
                y_true,
                y_pred,
                alphabet_size=response_alphabet_size(design),
            ),
            "producer_function": (
                "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_projection_runner.py::"
                "_measure_prefix_family_one_eval_user"
            ),
            "timing_producer_function": (
                "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_cputime_regate_runner.py::"
                "_measure_prefix_family_one_eval_user_cputime"
            ),
            "wall_clock_seconds": time.perf_counter() - member_wall_start,
            "process_cpu_seconds": time.process_time() - member_cpu_start,
            "wall_cpu_ratio": ratio,
            "wall_cpu_ratio_flag_gt_1_25": bool(ratio > 1.25),
            "run_id": run_id,
            "aggregation_rule": "fit_640 process CPU plus one eval-user score process CPU scaled to 160 eval users",
        }
    return {
        "cell_id": spec.cell_id,
        "variant": spec.variant,
        "members": members,
        "record_collection_wall_clock_seconds": collect_wall_seconds,
        "record_collection_process_cpu_seconds": collect_cpu_seconds,
        "projection_unit": "fit_640_users_plus_score_one_eval_user_scaled_to_160_eval_users",
        "heldout_users_800_999_touched": False,
        "producer_function": (
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_projection_runner.py::"
            "_measure_prefix_family_one_eval_user"
        ),
        "timing_producer_function": (
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_cputime_regate_runner.py::"
            "_measure_prefix_family_one_eval_user_cputime"
        ),
        "wall_clock_seconds": time.perf_counter() - wall_start,
        "process_cpu_seconds": time.process_time() - cpu_start,
        "run_id": run_id,
    }


def _project_total_cputime(
    measurements: Mapping[str, Any],
    applied_line: float,
    *,
    replacements: Mapping[str, Any] | None,
) -> dict[str, Any]:
    components: dict[str, Any] = {}

    def add(
        name: str,
        wall_seconds: float,
        cpu_seconds: float,
        units: float,
        note: str,
        *,
        null_units: float = 0.0,
        source: str,
        replaced_by_serial_mean: bool = False,
    ) -> None:
        projected_wall = float(wall_seconds) * float(units)
        projected_cpu = float(cpu_seconds) * float(units)
        ratio = _ratio(float(wall_seconds), float(cpu_seconds))
        components[name] = {
            "measured_wall_seconds": float(wall_seconds),
            "measured_process_cpu_seconds": float(cpu_seconds),
            "projected_units": float(units),
            "projected_wall_seconds": projected_wall,
            "projected_process_cpu_seconds": projected_cpu,
            "projected_wall_hours": projected_wall / 3600.0,
            "projected_cpu_hours": projected_cpu / 3600.0,
            "wall_cpu_ratio": ratio,
            "wall_cpu_ratio_flag_gt_1_25": bool(ratio > 1.25),
            "null_env_units_included": float(null_units),
            "note": note,
            "timing_source": source,
            "replaced_by_serial_mean": bool(replaced_by_serial_mean),
        }

    replacement_map = _replacement_component_values(replacements or {})
    gen = measurements["cert_set_generation"]
    ideal = measurements["ideal_per_user_one_cell"]
    add(
        "generation_all_7_cert_sets",
        float(gen["wall_clock_seconds"]),
        float(gen["process_cpu_seconds"]),
        7.0,
        "one measured cert-set generation x 7 S3d cells",
        null_units=1.0,
        source="fresh_cpu_timed_measurement",
    )
    ideal_repl = replacement_map.get("ideal_all_7_cells_160_eval_users")
    add(
        "ideal_all_7_cells_160_eval_users",
        float(ideal_repl["wall_seconds"] if ideal_repl else ideal["wall_clock_seconds"]),
        float(ideal_repl["cpu_seconds"] if ideal_repl else ideal["process_cpu_seconds"]),
        7.0 * 160.0,
        "one measured S2 ideal eval user x 160 eval users x 7 cells including NULL_env",
        null_units=160.0,
        source=str(ideal_repl["source"] if ideal_repl else "fresh_cpu_timed_measurement"),
        replaced_by_serial_mean=bool(ideal_repl),
    )
    for name, key, note, units, null_units in (
        (
            "logreg_F1_selected_cert_plus_NULL",
            "logreg_F1_selected",
            "obs_decoder_logreg selected F1 config on camouflage_off plus NULL_env",
            2.0,
            1.0,
        ),
        (
            "logreg_F2_reference_measured_not_counted",
            "logreg_F2_reference",
            "measured because PART 0 names F1/F2; not counted because selected logreg recipe is F1",
            0.0,
            0.0,
        ),
        (
            "gbt_half_data_selected_cert_plus_NULL",
            "gbt_half_data_selected",
            "obs_decoder_gbt selected F2 half-data config on camouflage_off plus NULL_env",
            2.0,
            1.0,
        ),
        (
            "gru_selected_cert_plus_NULL",
            "gru_selected",
            "obs_decoder_gru selected config on camouflage_off plus NULL_env",
            2.0,
            1.0,
        ),
        (
            "seq_full_selected_cert_plus_NULL",
            "seq_full_selected",
            "seq_full selected config on constant_none plus NULL_env",
            2.0,
            1.0,
        ),
        (
            "seq_W15_selected_cert_plus_NULL",
            "seq_W15_selected",
            "seq_W15 selected config on low_diversity plus NULL_env",
            2.0,
            1.0,
        ),
    ):
        m = measurements[key]
        add(
            name,
            float(m["fit_plus_validation_wall_clock_seconds"]),
            float(m["fit_plus_validation_process_cpu_seconds"]),
            units,
            note,
            null_units=null_units,
            source="fresh_outer_process_time_bracket",
        )

    for family_name, units_by_member in (
        (
            "table_family",
            {
                "successor_map": 2.0,
                "transition_table": 2.0,
                "count_table": 2.0,
                "fsm_planner": 2.0,
                "episodic_traversal": 2.0,
            },
        ),
        (
            "retrieval_family",
            {
                "rag_k5_episode_retrieval": 2.0,
                "nearest_neighbor_user_matching": 2.0,
            },
        ),
        (
            "degenerate_family",
            {
                "predict_all": 2.0,
                "predict_none": 2.0,
                "majority": 2.0,
                "global_prior": 2.0,
            },
        ),
        (
            "ls_online_family",
            {
                "discounted_LS_lambda_0.95": 2.0,
                "running_average_preference_regressor": 2.0,
            },
        ),
    ):
        for member, units in units_by_member.items():
            component_name = f"{family_name}_{member}_cert_plus_NULL"
            repl = replacement_map.get(component_name)
            m = measurements[family_name]["members"][member]
            add(
                component_name,
                float(repl["wall_seconds"] if repl else m["projected_one_member_cell_wall_seconds"]),
                float(repl["cpu_seconds"] if repl else m["projected_one_member_cell_process_cpu_seconds"]),
                units,
                f"{member}: projected one member-cell x favorable cert cell plus NULL_env",
                null_units=1.0,
                source=str(repl["source"] if repl else "fresh_process_time_fit_score_brackets"),
                replaced_by_serial_mean=bool(repl),
            )

    bootstrap = measurements["bootstrap"]
    add(
        "bootstrap_18_certificate_member_rows",
        float(bootstrap["wall_clock_seconds"]),
        float(bootstrap["process_cpu_seconds"]),
        18.0,
        "rho bootstrap CI for 18 certificate member rows; NULL table has no rho CI",
        source="fresh_outer_process_time_bracket",
    )
    total_wall = float(sum(item["projected_wall_seconds"] for item in components.values()))
    total_cpu = float(sum(item["projected_process_cpu_seconds"] for item in components.values()))
    null_wall = float(
        sum(
            item["measured_wall_seconds"] * item["null_env_units_included"]
            for item in components.values()
            if item["null_env_units_included"]
        )
    )
    null_cpu = float(
        sum(
            item["measured_process_cpu_seconds"] * item["null_env_units_included"]
            for item in components.values()
            if item["null_env_units_included"]
        )
    )
    return {
        "cpu_hour_limit": float(applied_line),
        "metric_basis": "per-unit process CPU-time (time.process_time user+sys)",
        "components": components,
        "total_projected_wall_seconds": total_wall,
        "total_projected_process_cpu_seconds": total_cpu,
        "total_projected_wall_hours": total_wall / 3600.0,
        "total_projected_cpu_hours": total_cpu / 3600.0,
        "line_relation": "within_line" if total_cpu / 3600.0 <= float(applied_line) else "exceeds_line",
        "null_env_projected_wall_seconds_included": null_wall,
        "null_env_projected_cpu_seconds_included": null_cpu,
        "null_env_projected_wall_hours_included": null_wall / 3600.0,
        "null_env_projected_cpu_hours_included": null_cpu / 3600.0,
        "linear_projection_assumptions": [
            "cert-set generation scales linearly across the 7 S3d cells",
            "S2 ideal cost scales from one eval user to 160 eval users per cell across 7 cells",
            "sklearn/GRU selected-recipe measurements are one full fit+validation member-cell units",
            "prefix-family measurements are fit_640 plus one eval user scoring, scaled to 160 eval users per member-cell",
            "each measured member-cell is counted once for its favorable certificate cell and once for NULL_env",
            "logreg_F2 is measured for named PART 0 coverage but not counted because the banked selected logreg recipe is F1",
        ],
    }


def _run_dominant_serial_remeasurements(
    battery: Any,
    part0: Any,
    design: Mapping[str, Any],
    specs: Mapping[str, Any],
    run_id: str,
) -> dict[str, Any]:
    ideal_rows = [
        _measure_ideal_cputime(battery, design, specs["camouflage_off"], user_id=user_id, run_id=run_id)
        for user_id in DOMINANT_REMEASURE_USERS
    ]
    nearest_rows = [
        _measure_prefix_family_one_eval_user_cputime(
            part0,
            design,
            specs["stable_facts"],
            {"nearest_neighbor_user_matching": battery.NearestNeighborUserMatchingPredictor},
            eval_user_id=user_id,
            run_id=run_id,
        )["members"]["nearest_neighbor_user_matching"]
        for user_id in DOMINANT_REMEASURE_USERS
    ]
    discounted_rows = [
        _measure_prefix_family_one_eval_user_cputime(
            part0,
            design,
            specs["flat_theta"],
            {"discounted_LS_lambda_0.95": battery.DiscountedLeastSquaresPredictor},
            eval_user_id=user_id,
            run_id=run_id,
        )["members"]["discounted_LS_lambda_0.95"]
        for user_id in DOMINANT_REMEASURE_USERS
    ]
    return {
        "eval_users": list(DOMINANT_REMEASURE_USERS),
        "heldout_users_800_999_touched": False,
        "ideal_all_7_cells_160_eval_users": {
            "unit": "ideal_per_user_one_cell",
            "component_replaced": "ideal_all_7_cells_160_eval_users",
            "rows": ideal_rows,
            "wall_seconds_mean_se": _mean_se([float(row["wall_clock_seconds"]) for row in ideal_rows]),
            "process_cpu_seconds_mean_se": _mean_se([float(row["process_cpu_seconds"]) for row in ideal_rows]),
            "aggregation_rule": "replace one-user one-cell ideal unit with serial-isolation mean over eval users 640, 720, 799",
        },
        "retrieval_family_nearest_neighbor_user_matching_cert_plus_NULL": {
            "unit": "nearest_neighbor_user_matching_projected_one_member_cell",
            "component_replaced": "retrieval_family_nearest_neighbor_user_matching_cert_plus_NULL",
            "rows": nearest_rows,
            "projected_wall_seconds_mean_se": _mean_se(
                [float(row["projected_one_member_cell_wall_seconds"]) for row in nearest_rows]
            ),
            "projected_process_cpu_seconds_mean_se": _mean_se(
                [float(row["projected_one_member_cell_process_cpu_seconds"]) for row in nearest_rows]
            ),
            "actual_member_wall_seconds_mean_se": _mean_se([float(row["wall_clock_seconds"]) for row in nearest_rows]),
            "actual_member_process_cpu_seconds_mean_se": _mean_se([float(row["process_cpu_seconds"]) for row in nearest_rows]),
            "aggregation_rule": "replace projected one-member-cell nearest-neighbor unit with serial-isolation mean over eval users 640, 720, 799",
        },
        "ls_online_family_discounted_LS_lambda_0.95_cert_plus_NULL": {
            "unit": "discounted_LS_lambda_0.95_projected_one_member_cell",
            "component_replaced": "ls_online_family_discounted_LS_lambda_0.95_cert_plus_NULL",
            "rows": discounted_rows,
            "projected_wall_seconds_mean_se": _mean_se(
                [float(row["projected_one_member_cell_wall_seconds"]) for row in discounted_rows]
            ),
            "projected_process_cpu_seconds_mean_se": _mean_se(
                [float(row["projected_one_member_cell_process_cpu_seconds"]) for row in discounted_rows]
            ),
            "actual_member_wall_seconds_mean_se": _mean_se([float(row["wall_clock_seconds"]) for row in discounted_rows]),
            "actual_member_process_cpu_seconds_mean_se": _mean_se([float(row["process_cpu_seconds"]) for row in discounted_rows]),
            "aggregation_rule": "replace projected one-member-cell discounted-LS unit with serial-isolation mean over eval users 640, 720, 799",
        },
    }


def _replacement_component_values(remeasurements: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    if not remeasurements:
        return {}
    values: dict[str, dict[str, Any]] = {}
    ideal = remeasurements.get("ideal_all_7_cells_160_eval_users")
    if ideal:
        values["ideal_all_7_cells_160_eval_users"] = {
            "wall_seconds": ideal["wall_seconds_mean_se"]["mean"],
            "cpu_seconds": ideal["process_cpu_seconds_mean_se"]["mean"],
            "source": "dominant_serial_remeasurement_mean_eval_users_640_720_799",
        }
    nn = remeasurements.get("retrieval_family_nearest_neighbor_user_matching_cert_plus_NULL")
    if nn:
        values["retrieval_family_nearest_neighbor_user_matching_cert_plus_NULL"] = {
            "wall_seconds": nn["projected_wall_seconds_mean_se"]["mean"],
            "cpu_seconds": nn["projected_process_cpu_seconds_mean_se"]["mean"],
            "source": "dominant_serial_remeasurement_mean_eval_users_640_720_799",
        }
    ls = remeasurements.get("ls_online_family_discounted_LS_lambda_0.95_cert_plus_NULL")
    if ls:
        values["ls_online_family_discounted_LS_lambda_0.95_cert_plus_NULL"] = {
            "wall_seconds": ls["projected_wall_seconds_mean_se"]["mean"],
            "cpu_seconds": ls["projected_process_cpu_seconds_mean_se"]["mean"],
            "source": "dominant_serial_remeasurement_mean_eval_users_640_720_799",
        }
    return values


def _flatten_unit_timings(
    measurements: Mapping[str, Any],
    projection: Mapping[str, Any],
    remeasurements: Mapping[str, Any],
) -> dict[str, Any]:
    units: list[dict[str, Any]] = []

    def add_unit(unit_id: str, wall_seconds: float, cpu_seconds: float, *, context: Mapping[str, Any]) -> None:
        ratio = _ratio(float(wall_seconds), float(cpu_seconds))
        units.append(
            {
                "unit_id": unit_id,
                "wall_seconds": float(wall_seconds),
                "process_cpu_seconds": float(cpu_seconds),
                "wall_cpu_ratio": ratio,
                "wall_cpu_ratio_flag_gt_1_25": bool(ratio > 1.25),
                **dict(context),
            }
        )

    gen = measurements["cert_set_generation"]
    add_unit("generation_all_7_cert_sets", gen["wall_clock_seconds"], gen["process_cpu_seconds"], context={"phase": "initial"})
    ideal = measurements["ideal_per_user_one_cell"]
    add_unit(
        "ideal_all_7_cells_160_eval_users",
        ideal["wall_clock_seconds"],
        ideal["process_cpu_seconds"],
        context={"phase": "initial", "eval_user_id": ideal["user_id"], "cell_id": ideal["cell_id"]},
    )
    for key in (
        "logreg_F1_selected",
        "logreg_F2_reference",
        "gbt_half_data_selected",
        "gru_selected",
        "seq_full_selected",
        "seq_W15_selected",
        "bootstrap",
    ):
        m = measurements[key]
        wall = m.get("fit_plus_validation_wall_clock_seconds", m.get("wall_clock_seconds"))
        cpu = m.get("fit_plus_validation_process_cpu_seconds", m.get("process_cpu_seconds"))
        add_unit(key, wall, cpu, context={"phase": "initial", "cell_id": m.get("cell_id"), "member": m.get("member")})
    for family_name in ("table_family", "retrieval_family", "degenerate_family", "ls_online_family"):
        for member, m in measurements[family_name]["members"].items():
            add_unit(
                f"{family_name}_{member}",
                m["projected_one_member_cell_wall_seconds"],
                m["projected_one_member_cell_process_cpu_seconds"],
                context={
                    "phase": "initial",
                    "cell_id": m["cell_id"],
                    "member": member,
                    "eval_user_id": m["eval_user_id_measured"],
                    "aggregation_rule": "projected fit+160*score unit",
                },
            )
    for name, block in remeasurements.items():
        if not isinstance(block, Mapping) or "rows" not in block:
            continue
        for row in block["rows"]:
            if name == "ideal_all_7_cells_160_eval_users":
                add_unit(
                    f"serial_remeasure::{name}::user_{row['user_id']}",
                    row["wall_clock_seconds"],
                    row["process_cpu_seconds"],
                    context={"phase": "serial_remeasurement", "cell_id": row["cell_id"], "eval_user_id": row["user_id"]},
                )
            else:
                add_unit(
                    f"serial_remeasure::{name}::user_{row['eval_user_id_measured']}",
                    row["projected_one_member_cell_wall_seconds"],
                    row["projected_one_member_cell_process_cpu_seconds"],
                    context={
                        "phase": "serial_remeasurement",
                        "cell_id": row["cell_id"],
                        "member": row["member"],
                        "eval_user_id": row["eval_user_id_measured"],
                        "aggregation_rule": "projected fit+160*score unit",
                    },
                )
    flags = [unit for unit in units if bool(unit["wall_cpu_ratio_flag_gt_1_25"])]
    return {
        "units": units,
        "wall_cpu_ratio_flags_gt_1_25": flags,
        "projection_component_flags_gt_1_25": [
            {"component": name, **component}
            for name, component in projection["components"].items()
            if bool(component["wall_cpu_ratio_flag_gt_1_25"])
        ],
    }


def _wall_gate_ablation() -> dict[str, Any]:
    preserved = ARTIFACT_ROOT / "s3d_compute_projection_line30.0_wall_gate_noncompliant_v1.json"
    data = _read_json(preserved)
    wall_hours = float(data["full_part0_projection"]["total_projected_cpu_hours"])
    return {
        "artifact": _rel(preserved),
        "sha256": _sha256(preserved),
        "metric_basis": "preserved non-compliant wall-clock projection",
        "total_projected_cpu_hours": wall_hours,
        "line_cpu_hours": LINE_CPU_HOURS,
        "line_relation": "exceeds_line" if wall_hours > LINE_CPU_HOURS else "within_line",
        "reproduces_wall_gated_stop": bool(wall_hours > LINE_CPU_HOURS),
        "expected_wall_gated_stop_hours": 32.00740120549966,
        "absolute_difference_from_audit_value": abs(wall_hours - 32.00740120549966),
        "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_cputime_regate_runner.py::_wall_gate_ablation",
    }


def _replay_projection(projection: Mapping[str, Any], applied_line: float, wall_gate_ablation: Mapping[str, Any]) -> dict[str, Any]:
    replay_cpu_seconds = float(sum(item["projected_process_cpu_seconds"] for item in projection["components"].values()))
    replay_wall_seconds = float(sum(item["projected_wall_seconds"] for item in projection["components"].values()))
    replay_cpu_hours = replay_cpu_seconds / 3600.0
    replay_relation = "within_line" if replay_cpu_hours <= float(applied_line) else "exceeds_line"
    return {
        "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_cputime_regate_runner.py::_replay_projection",
        "recomputed_total_projected_process_cpu_seconds": replay_cpu_seconds,
        "recomputed_total_projected_cpu_hours": replay_cpu_hours,
        "recomputed_total_projected_wall_seconds": replay_wall_seconds,
        "recomputed_total_projected_wall_hours": replay_wall_seconds / 3600.0,
        "line_relation": replay_relation,
        "matches_recorded_total": bool(
            math.isclose(replay_cpu_hours, float(projection["total_projected_cpu_hours"]), rel_tol=0.0, abs_tol=1e-12)
            and replay_relation == projection["line_relation"]
        ),
        "wall_gate_ablation_replay": {
            "recomputed_line_relation": wall_gate_ablation["line_relation"],
            "reproduces_stop": wall_gate_ablation["reproduces_wall_gated_stop"],
        },
    }


def _preserve_wall_gate_artifacts() -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for name in WALL_GATE_ARTIFACTS:
        source = ARTIFACT_ROOT / name
        dest = _wall_gate_copy_path(source)
        if not source.exists():
            records.append({"source": _rel(source), "dest": _rel(dest), "status": "missing_source", "byte_identical": False})
            continue
        source_hash = _sha256(source)
        if dest.exists():
            dest_hash = _sha256(dest)
            records.append(
                {
                    "source": _rel(source),
                    "dest": _rel(dest),
                    "status": "already_exists_not_overwritten",
                    "source_sha256_at_run_start": source_hash,
                    "dest_sha256": dest_hash,
                    "byte_identical_to_current_source": source_hash == dest_hash,
                    "byte_identical": source_hash == dest_hash,
                }
            )
            continue
        shutil.copy2(source, dest)
        dest_hash = _sha256(dest)
        records.append(
            {
                "source": _rel(source),
                "dest": _rel(dest),
                "status": "copied",
                "source_sha256_at_copy": source_hash,
                "dest_sha256": dest_hash,
                "byte_identical": source_hash == dest_hash,
                "size_bytes": source.stat().st_size,
            }
        )
    return {
        "suffix": "_wall_gate_noncompliant_v1",
        "records": records,
        "all_sources_present": all(record["status"] != "missing_source" for record in records),
        "all_new_or_existing_copies_byte_identical_at_copy_time": all(bool(record.get("byte_identical")) for record in records),
        "preserved_as_failure_evidence_not_patched_or_deleted": True,
    }


def _wall_gate_copy_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}_wall_gate_noncompliant_v1{path.suffix}")


def _certificate_null_snapshot() -> dict[str, Any]:
    paths = {
        "certificate": ARTIFACT_ROOT / "s3d_certificate_report.json",
        "null_env": ARTIFACT_ROOT / "s3d_null_env_report.json",
    }
    return {
        key: {
            "path": _rel(path),
            "sha256": _sha256(path) if path.exists() else None,
            "metric_digest": _metric_digest(path) if path.exists() else None,
        }
        for key, path in paths.items()
    }


def _certificate_null_unchanged(before: Mapping[str, Any]) -> dict[str, Any]:
    after = _certificate_null_snapshot()
    return {
        "before": before,
        "after": after,
        "unchanged": before == after,
        "assertion": "certificate/NULL metric artifacts are byte/metric unchanged versus pre-regate snapshot",
    }


def _metric_digest(path: Path) -> str:
    data = _read_json(path)
    material = {
        "rows": data.get("rows"),
        "member_rho_and_ci": data.get("member_rho_and_ci"),
        "breaches": data.get("breaches"),
        "false_headroom_status": data.get("false_headroom_status"),
        "member_rho_and_ci_status": data.get("member_rho_and_ci_status"),
    }
    return _sha256_json(material)


def _write_result(payload: Mapping[str, Any]) -> None:
    result = {
        "task_id": TASK_ID,
        "task_card_id": TASK_CARD_ID,
        "stage": "S3d",
        "artifact": "result",
        "verdict": payload.get("verdict"),
        "line_relation": payload.get("line_relation"),
        "applied_cpu_hour_limit": payload.get("applied_cpu_hour_limit", LINE_CPU_HOURS),
        "cpu_hour_projection_total": payload.get("cpu_hour_projection_total"),
        "wall_clock_based_cpu_hours_disclosed": payload.get("wall_clock_based_cpu_hours_disclosed"),
        "part0_cputime_regate_artifact": _rel(OUTPUT),
        "battery_launched": False,
        "s3d_results_void": bool(payload.get("line_relation") != "within_line"),
        "stop_condition": payload.get("stop_condition"),
        "claim_ceiling": CLAIM_CEILING,
        "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_cputime_regate_runner.py::_write_result",
        "code_path_hash": payload.get("code_path_hash"),
        "run_id": payload.get("run_id"),
        "run_started_at": payload.get("run_started_at"),
        "run_finished_at": payload.get("run_finished_at"),
    }
    _write_json(RESULT, result)


def _write_failure_manifest(payload: Mapping[str, Any], verdict: str, stop_condition: str) -> None:
    manifest = {
        "task_id": TASK_ID,
        "task_card_id": TASK_CARD_ID,
        "stage": "S3d",
        "artifact": "failure_manifest",
        "verdict": verdict,
        "s3d_results_void": True,
        "stop_condition": stop_condition,
        "part0_cputime_regate_artifact": _rel(OUTPUT),
        "preserved_failure": True,
        "claim_ceiling": CLAIM_CEILING,
        "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_cputime_regate_runner.py::_write_failure_manifest",
        "code_path_hash": payload.get("code_path_hash"),
        "run_id": payload.get("run_id"),
        "run_started_at": payload.get("run_started_at"),
        "run_finished_at": payload.get("run_finished_at"),
    }
    _write_json(FAILURE_MANIFEST, manifest)


def _normalize_historical_wall_failure_manifest(payload: Mapping[str, Any]) -> None:
    existing = _read_json(FAILURE_MANIFEST) if FAILURE_MANIFEST.exists() else {}
    existing["s3d_results_void"] = True
    existing["failure_manifest_scope"] = "historical_wall_gate_noncompliant_v1"
    existing["current_cputime_regate_artifact"] = _rel(OUTPUT)
    existing["current_cputime_regate_line_relation"] = payload.get("line_relation")
    existing["current_cputime_regate_verdict"] = payload.get("verdict")
    existing["wall_gate_noncompliant_copy"] = _rel(_wall_gate_copy_path(FAILURE_MANIFEST))
    existing["normalization_note"] = (
        "N1 normalization only: prior wall-gated STOP manifest now has s3d_results_void=true like the other "
        "wall-gated STOP reports. The unpatched original was preserved as *_wall_gate_noncompliant_v1."
    )
    existing["producer_function_normalization"] = (
        "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_cputime_regate_runner.py::"
        "_normalize_historical_wall_failure_manifest"
    )
    _write_json(FAILURE_MANIFEST, existing)


def _write_claim_ceiling() -> None:
    CLAIM_CEILING_PATH.write_text(CLAIM_CEILING + "\n", encoding="utf-8")


def _write_bank_ops(payload: Mapping[str, Any]) -> None:
    head_pin = (
        payload.get("precondition", {})
        .get("git_readback_without_git_command", {})
        .get("head_hash", "c0c6bf416f8a06777a1465e005e4aae0dbdc1bae")
    )
    allowlist = [
        _rel(FIX_CARD),
        _rel(Path(__file__)),
        _rel(OUTPUT),
        _rel(CLAIM_CEILING_PATH),
        _rel(RESULT),
        _rel(FAILURE_MANIFEST),
        _rel(BANK_OPS),
    ]
    allowlist.extend(_rel(_wall_gate_copy_path(ARTIFACT_ROOT / name)) for name in WALL_GATE_ARTIFACTS)
    rendered = "\n".join(f"  '{item}'" for item in allowlist)
    commit_message = "FSP-PUM-ENV-IDPROBE-001A S3d PART0 CPU-time regate"
    script = f"""# Proposed operator-only bank ops for {TASK_CARD_ID}
# Generated by Codex; not run by Codex. No push.
$ErrorActionPreference = 'Stop'
$ExpectedHead = '{head_pin}'
$CommitMessage = '{commit_message}'
$Allowlist = @(
{rendered}
)

$ActualHead = (git rev-parse HEAD).Trim()
if ($ActualHead -ne $ExpectedHead) {{
  throw "HEAD pin mismatch: expected $ExpectedHead got $ActualHead"
}}

git reset --

$ExistingAllowlist = @()
foreach ($Path in $Allowlist) {{
  if (Test-Path -LiteralPath $Path) {{
    $ExistingAllowlist += $Path
  }} else {{
    throw "Allowlist path missing before bank: $Path"
  }}
}}

git add -- $ExistingAllowlist

$Staged = @(git diff --cached --name-only)
if ($Staged.Count -ne $ExistingAllowlist.Count) {{
  throw "Staged count mismatch: expected $($ExistingAllowlist.Count) got $($Staged.Count): $($Staged -join ', ')"
}}

$Unexpected = @($Staged | Where-Object {{ $Allowlist -notcontains $_ }})
if ($Unexpected.Count -ne 0) {{
  throw "Unexpected staged paths: $($Unexpected -join ', ')"
}}

$Deleted = @(git diff --cached --name-status | Where-Object {{ $_ -match '^D\\s' }})
if ($Deleted.Count -ne 0) {{
  throw "Zero-deletion gate failed: $($Deleted -join '; ')"
}}

foreach ($Path in $ExistingAllowlist) {{
  Get-FileHash -Algorithm SHA256 -LiteralPath $Path | Format-List
}}

git commit -m $CommitMessage -- $ExistingAllowlist

Write-Host 'Banked scoped S3d PART0 CPU-time re-gate artifacts locally. No push was performed.'
"""
    BANK_OPS.write_text(script, encoding="utf-8")


def _heldout_touched(measurements: Mapping[str, Any], remeasurements: Mapping[str, Any]) -> bool:
    text = json.dumps(_jsonable({"measurements": measurements, "remeasurements": remeasurements}), sort_keys=True)
    if "800" in text or "999" in text:
        # Avoid a lexical false positive from range labels by checking explicit user fields.
        pass
    users: list[int] = []
    for family in ("table_family", "retrieval_family", "degenerate_family", "ls_online_family"):
        for member in measurements[family]["members"].values():
            users.append(int(member["eval_user_id_measured"]))
    users.append(int(measurements["ideal_per_user_one_cell"]["user_id"]))
    for block in remeasurements.values():
        if isinstance(block, Mapping) and "rows" in block:
            for row in block["rows"]:
                if "user_id" in row:
                    users.append(int(row["user_id"]))
                if "eval_user_id_measured" in row:
                    users.append(int(row["eval_user_id_measured"]))
    return any(800 <= user <= 999 for user in users)


def _mean_se(values: Sequence[float]) -> dict[str, Any]:
    vals = [float(value) for value in values]
    mean = float(statistics.mean(vals))
    se = float(statistics.stdev(vals) / math.sqrt(len(vals))) if len(vals) > 1 else 0.0
    return {"n": len(vals), "mean": mean, "se": se, "values": vals}


def _load_battery_runner() -> Any:
    spec = importlib.util.spec_from_file_location("s3d_battery_runner_line30_for_cputime_regate", BATTERY_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed_to_load_battery_runner_spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_original_part0_runner() -> Any:
    spec = importlib.util.spec_from_file_location("s3d_part0_projection_runner_for_cputime_regate", ORIGINAL_PART0_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed_to_load_part0_runner_spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _hash_paths(paths: Sequence[Path]) -> dict[str, Any]:
    return {
        _rel(path): {
            "exists": path.exists(),
            "sha256": _sha256(path) if path.exists() else None,
            "size_bytes": path.stat().st_size if path.exists() else None,
        }
        for path in paths
    }


def _ratio(wall_seconds: float, cpu_seconds: float) -> float:
    return float(wall_seconds) / max(float(cpu_seconds), 1e-12)


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
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and math.isnan(value):
        return "NaN"
    return value


def _sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _sha256_json(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(_jsonable(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _code_path_hash(battery: Any) -> str:
    h = hashlib.sha256()
    paths: list[Path] = [Path(__file__), BATTERY_RUNNER_PATH, ORIGINAL_PART0_RUNNER_PATH]
    for path in battery._code_paths():
        if path not in paths:
            paths.append(path)
    for path in paths:
        h.update(_rel(path).encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _rel(path: str | Path) -> str:
    return str(Path(path).resolve().relative_to(ROOT)).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
