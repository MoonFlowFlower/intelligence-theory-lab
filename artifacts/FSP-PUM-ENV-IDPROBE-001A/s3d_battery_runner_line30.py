"""Execute S3d SHOULD-WIN + NULL-env battery under the signed line.

Task-local runner for:
FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-EXEC-001A

This file is an artifact-side callable computation path.  It reads the signed
operator line from the budget decision note, uses that single applied line for
PART-0 re-gate and runtime guard, and writes only new S3d battery artifacts.

Claim ceiling: bounded S3d should-win + NULL-env instrument evidence under the
frozen contract and signed compute line only.
"""

from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
import copy
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import statistics
import subprocess
import sys
import time
import traceback
from typing import Any, Callable, Iterable, Mapping, Sequence


THREAD_ENV_KEYS = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS")
for _KEY in THREAD_ENV_KEYS:
    os.environ[_KEY] = "1"

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.fsp_pum_env.battery import obs_decoders
from src.fsp_pum_env.battery.base import PrefixEvent, event_from_mapping, frozen_action_list, response_alphabet_size
from src.fsp_pum_env.battery.degenerates import (
    GlobalPriorPredictor,
    MajorityPredictor,
    PredictAllPredictor,
    PredictNonePredictor,
)
from src.fsp_pum_env.battery.graph_cache import (
    CountTablePredictor,
    EpisodicTraversalPredictor,
    FsmPlannerPredictor,
    SuccessorMapPredictor,
    TransitionTablePredictor,
)
from src.fsp_pum_env.battery.ls_regressors import (
    DiscountedLeastSquaresPredictor,
    RunningAveragePreferenceRegressor,
)
from src.fsp_pum_env.battery.rag_nn import (
    NearestNeighborUserMatchingPredictor,
    RagK5EpisodeRetrievalPredictor,
)
from src.fsp_pum_env.factored_filter import FactoredExactFilter
from src.fsp_pum_env.ideal_observer import PrefixEvent as IdealPrefixEvent, independent_filter_seed
from src.fsp_pum_env.s3d_certificates import (
    CHANCE_CELL,
    NULL_MARGIN,
    S3D_CERT_CELLS,
    build_s3d_cert_set_specs,
    generate_s3d_cert_sets_manifest,
    macro_balanced_accuracy,
    run_s3d_preflight_guards,
)
from src.fsp_pum_env.trajectory_sets import _hash_spec_streams, _iter_records_with_adjudicator, load_frozen_design


TASK_ID = "FSP-PUM-ENV-IDPROBE-001A"
TASK_CARD_ID = "FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-EXEC-001A"
ARTIFACT_ROOT = ROOT / "artifacts" / TASK_ID
FROZEN_DESIGN = ARTIFACT_ROOT / "frozen_design.json"
S3A_MANIFEST = ARTIFACT_ROOT / "s3a_trajectory_set_manifest.json"
VOCABULARY = ARTIFACT_ROOT / "s3c_models" / "f2_ngram_vocabulary.json"
EXEC_CARD = ROOT / "docs" / "codex" / "tasks" / "FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-EXEC-001A.md"
SPEC_CARD = ROOT / "docs" / "codex" / "tasks" / "FSP-PUM-ENV-IDPROBE-001A-S3D-SHOULD-WIN-NULL-ENV-SPEC-001B.md"
SPEC_CARD_001A_SUPERSEDED = ROOT / "docs" / "codex" / "tasks" / "FSP-PUM-ENV-IDPROBE-001A-S3D-SHOULD-WIN-NULL-ENV-SPEC-001A.md"
BUDGET_DECISION = ROOT / "docs" / "codex" / "tasks" / "FSP-PUM-ENV-IDPROBE-001A-S3D-BUDGET-DECISION-001A.md"
ORIGINAL_PART0_RUNNER = ARTIFACT_ROOT / "s3d_part0_projection_runner.py"
S3D_001B_IMPL_REPORT = ARTIFACT_ROOT / "s3d_001b_impl_report.json"

PROTECTED_BANKED_ARTIFACTS = (
    ARTIFACT_ROOT / "s3d_compute_projection_v1.json",
    ARTIFACT_ROOT / "s3d_compute_projection.json",
    ARTIFACT_ROOT / "s3d_part0_projection_failure_manifest.json",
    ARTIFACT_ROOT / "s3d_part0_projection_runner.py",
    ARTIFACT_ROOT / "s3d_part0_variance_probe.json",
    ARTIFACT_ROOT / "s3d_part0_variance_probe_trace.csv",
    ARTIFACT_ROOT / "s3d_part0_variance_probe_runner.py",
    ARTIFACT_ROOT / "s3d_part0_variance_probe_bank_ops.ps1",
)

CERT_SETS_MANIFEST = ARTIFACT_ROOT / "s3d_cert_sets_manifest.json"
CERTIFICATE_REPORT = ARTIFACT_ROOT / "s3d_certificate_report.json"
NULL_ENV_REPORT = ARTIFACT_ROOT / "s3d_null_env_report.json"
RESULT = ARTIFACT_ROOT / "result.json"
TRACE_JSONL = ARTIFACT_ROOT / "trace.jsonl"
TRACE_CSV = ARTIFACT_ROOT / "trace.csv"
BASELINE_COMPARISON = ARTIFACT_ROOT / "baseline_comparison.json"
ABLATION_REPORT = ARTIFACT_ROOT / "ablation_report.json"
REPLAY_REPORT = ARTIFACT_ROOT / "replay_report.json"
FAILURE_MANIFEST = ARTIFACT_ROOT / "failure_manifest.json"

CLAIM_CEILING = (
    "line L under the frozen contract: S3d should-win + NULL-env instrument evidence only; "
    "not environment-validity, gap, mechanism, learning, agency, EGO, companion, or readiness evidence"
)


PREFIX_MEMBER_CLASSES: dict[str, Callable[..., Any]] = {
    "predict_none": PredictNonePredictor,
    "majority": MajorityPredictor,
    "global_prior": GlobalPriorPredictor,
    "predict_all": PredictAllPredictor,
    "successor_map": SuccessorMapPredictor,
    "transition_table": TransitionTablePredictor,
    "count_table": CountTablePredictor,
    "fsm_planner": FsmPlannerPredictor,
    "episodic_traversal": EpisodicTraversalPredictor,
    "rag_k5_episode_retrieval": RagK5EpisodeRetrievalPredictor,
    "nearest_neighbor_user_matching": NearestNeighborUserMatchingPredictor,
    "discounted_LS_lambda_0.95": DiscountedLeastSquaresPredictor,
    "running_average_preference_regressor": RunningAveragePreferenceRegressor,
}

SELECTED_RECIPE_BY_MEMBER = {
    "obs_decoder_logreg": "obs_decoder_logreg_selected_recipe.json",
    "obs_decoder_gbt": "obs_decoder_gbt_selected_recipe.json",
    "obs_decoder_gru": "obs_decoder_gru_selected_recipe.json",
    "seq_full_history_no_action_conditioning": "seq_full_history_no_action_conditioning_selected_recipe.json",
    "seq_window_with_action_conditioning_W15_no_cross_session_persistence": (
        "seq_window_with_action_conditioning_W15_no_cross_session_persistence_selected_recipe.json"
    ),
}

CERT_MEMBER_SPECS: tuple[dict[str, Any], ...] = (
    {"member": "predict_none", "cell_id": "constant_none", "threshold": 0.90, "metric_scope": "overall"},
    {"member": "majority", "cell_id": "constant_none", "threshold": 0.90, "metric_scope": "overall"},
    {"member": "global_prior", "cell_id": "constant_none", "threshold": 0.90, "metric_scope": "overall"},
    {
        "member": "seq_full_history_no_action_conditioning",
        "cell_id": "constant_none",
        "threshold": 0.90,
        "metric_scope": "overall",
    },
    {"member": "predict_all", "cell_id": "constant_saturated", "threshold": 0.90, "metric_scope": "overall"},
    {"member": "obs_decoder_logreg", "cell_id": "camouflage_off", "threshold": 0.80, "metric_scope": "overall"},
    {"member": "obs_decoder_gbt", "cell_id": "camouflage_off", "threshold": 0.80, "metric_scope": "overall"},
    {"member": "obs_decoder_gru", "cell_id": "camouflage_off", "threshold": 0.80, "metric_scope": "overall"},
    {
        "member": "seq_window_with_action_conditioning_W15_no_cross_session_persistence",
        "cell_id": "low_diversity",
        "threshold": 0.50,
        "metric_scope": "overall",
    },
    {"member": "successor_map", "cell_id": "low_diversity", "threshold": 0.50, "metric_scope": "overall"},
    {"member": "transition_table", "cell_id": "low_diversity", "threshold": 0.50, "metric_scope": "overall"},
    {"member": "count_table", "cell_id": "low_diversity", "threshold": 0.50, "metric_scope": "overall"},
    {"member": "fsm_planner", "cell_id": "low_diversity", "threshold": 0.50, "metric_scope": "overall"},
    {
        "member": "episodic_traversal",
        "cell_id": "low_diversity",
        "threshold": 0.50,
        "metric_scope": "overall",
        "fallback_rate_max": 0.50,
    },
    {
        "member": "rag_k5_episode_retrieval",
        "cell_id": "stable_facts",
        "threshold": 0.50,
        "metric_scope": "recommend",
    },
    {
        "member": "nearest_neighbor_user_matching",
        "cell_id": "low_diversity",
        "threshold": 0.50,
        "metric_scope": "overall",
    },
    {"member": "discounted_LS_lambda_0.95", "cell_id": "flat_theta", "threshold": 0.80, "metric_scope": "overall"},
    {
        "member": "running_average_preference_regressor",
        "cell_id": "flat_theta",
        "threshold": 0.80,
        "metric_scope": "overall",
    },
)

NULL_MEMBER_NAMES: tuple[str, ...] = tuple(str(item["member"]) for item in CERT_MEMBER_SPECS)
S3D_001B_GUARD_K = 5.0
DOMINANT_REMEASURE_USERS = (640, 720, 799)
CANONICAL_SCORER_ID = (
    "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py"
    "::_score_payload/_metric_for_scope/_metric_from_resampled_users"
)
CANONICAL_SCORER_RECONCILIATION = {
    "canonical_scorer": CANONICAL_SCORER_ID,
    "canonical_fixture_function": "_canonical_scorer_fixture",
    "old_inline_diagnostic_value": 0.05864197530864198,
    "banked_runner_canonical_value": 0.1363095238095238,
    "difference_source": (
        "The 0.0586 value came from a non-canonical inline stable-facts diagnostic path over a k=10 "
        "fractional eval-user sample. The 0.1363 value came from the banked runner metric helpers over "
        "the preregistered k=15 headroom-precheck sample, using pooled recommend-turn-conditional "
        "macro-balanced accuracy from per-user confusion rows. The old inline diagnostic scorer is not "
        "used for adjudication."
    ),
    "old_inline_scorer_void_for_adjudication": True,
}


def run() -> dict[str, Any]:
    run_started_at = _utc_timestamp()
    perf_start = time.perf_counter()
    cpu_start = time.process_time()
    result_payload: dict[str, Any] = {
        "task_id": TASK_ID,
        "task_card_id": TASK_CARD_ID,
        "stage": "S3d",
        "claim_ceiling": CLAIM_CEILING,
        "run_started_at": run_started_at,
        "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::run",
        "code_path_hash": _code_path_hash(),
    }
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

    protected_before = _protected_artifact_hashes()
    try:
        precondition = _verify_preconditions()
        result_payload["precondition"] = precondition
        if not precondition["passed"]:
            manifest = _failure_manifest_payload(
                verdict="STOP_PRECONDITION_UNMET",
                stop_condition="S3d battery precondition failed before PART-0 re-gate",
                details=precondition,
                protected_before=protected_before,
            )
            precondition_artifacts = _write_precondition_stop_artifacts(precondition, manifest)
            _write_json(ARTIFACT_ROOT / "s3d_battery_precondition_failure_manifest.json", manifest)
            _write_json(FAILURE_MANIFEST, manifest)
            result_payload.update(
                {
                    "verdict": "STOP_PRECONDITION_UNMET",
                    "s3d_results_void": True,
                    "stop_condition": manifest["stop_condition"],
                    "protected_artifacts_after": _protected_artifact_hashes(),
                    "trace_artifacts": [_artifact_ref(TRACE_JSONL), _artifact_ref(TRACE_CSV)],
                    "certificate_report": _artifact_ref(CERTIFICATE_REPORT),
                    "null_env_report": _artifact_ref(NULL_ENV_REPORT),
                    "baseline_comparison": _artifact_ref(BASELINE_COMPARISON),
                    "ablation_report": _artifact_ref(ABLATION_REPORT),
                    "replay_report": _artifact_ref(REPLAY_REPORT),
                    "new_artifacts": precondition_artifacts,
                }
            )
            _write_json(RESULT, _finalize_result_payload(result_payload, perf_start, cpu_start))
            _write_operator_bank_ops(result_payload)
            return result_payload

        applied_line = float(precondition["signed_budget"]["line_cpu_hours"])
        line_label = _line_label(applied_line)
        projection_path = ARTIFACT_ROOT / f"s3d_compute_projection_line{line_label}.json"
        result_payload["applied_cpu_hour_limit"] = applied_line
        result_payload["applied_line_source"] = precondition["signed_budget"]
        result_payload["single_line_application"] = {
            "source": str(BUDGET_DECISION.relative_to(ROOT)),
            "line_number": int(precondition["signed_budget"]["line_number"]),
            "applied_to": ["PART-0 re-gate", "runtime guard"],
            "no_second_test_path": True,
        }

        projection = _run_part0_projection_line(applied_line, projection_path)
        result_payload["part0_projection_artifact"] = str(projection_path.relative_to(ROOT))
        result_payload["part0_projection_decision"] = projection["decision"]
        if float(projection["projected_cpu_hours"]) > applied_line:
            manifest = _failure_manifest_payload(
                verdict="STOP_s3d_part0_projection_exceeds_line",
                stop_condition=f"PART-0 projection {projection['projected_cpu_hours']} CPU-h exceeded signed line {applied_line}",
                details={"part0_projection": _artifact_ref(projection_path), "projection_decision": projection["decision"]},
                protected_before=protected_before,
            )
            _write_json(FAILURE_MANIFEST, manifest)
            result_payload.update(
                {
                    "verdict": manifest["verdict"],
                    "s3d_results_void": True,
                    "stop_condition": manifest["stop_condition"],
                    "protected_artifacts_after": _protected_artifact_hashes(),
                }
            )
            _write_json(RESULT, _finalize_result_payload(result_payload, perf_start, cpu_start))
            return result_payload

        ablation = run_s3d_preflight_guards(FROZEN_DESIGN, S3A_MANIFEST, ABLATION_REPORT)
        if not bool(ablation.get("passed")):
            manifest = _failure_manifest_payload(
                verdict="STOP_s3d_preflight_guard_failed",
                stop_condition="BASE-invariance or cert-only variant guard failed",
                details={"ablation_report": _artifact_ref(ABLATION_REPORT), "ablation_verdict": ablation.get("verdict")},
                protected_before=protected_before,
            )
            _write_json(FAILURE_MANIFEST, manifest)
            result_payload.update(
                {
                    "verdict": manifest["verdict"],
                    "s3d_results_void": True,
                    "stop_condition": manifest["stop_condition"],
                    "protected_artifacts_after": _protected_artifact_hashes(),
                }
            )
            _write_json(RESULT, _finalize_result_payload(result_payload, perf_start, cpu_start))
            return result_payload

        cert_sets_manifest = generate_s3d_cert_sets_manifest(FROZEN_DESIGN, CERT_SETS_MANIFEST)
        result_payload["cert_sets_manifest"] = _artifact_ref(CERT_SETS_MANIFEST)
        result_payload["ablation_report"] = _artifact_ref(ABLATION_REPORT)

        physical_cores = _physical_core_count()
        unit_payloads = _battery_unit_payloads()
        n_workers = min(int(physical_cores["physical_cores"]), len(unit_payloads))
        if n_workers < 1:
            n_workers = 1
        if n_workers > int(physical_cores["physical_cores"]):
            raise RuntimeError("worker_count_would_oversubscribe_physical_cores")
        parallelism = {
            **physical_cores,
            "n_workers": int(n_workers),
            "threads_per_worker": 1,
            "n_workers_times_threads": int(n_workers),
            "oversubscription": bool(int(n_workers) > int(physical_cores["physical_cores"])),
            "gpu_disabled": True,
        }
        result_payload["parallelism"] = parallelism

        trace_rows, unit_results, runtime_guard = _run_units_parallel(
            unit_payloads,
            max_workers=n_workers,
            applied_line=applied_line,
            initial_cpu_hours=float(projection["process_cpu_seconds"]) / 3600.0,
        )
        _write_trace_jsonl(TRACE_JSONL, trace_rows)
        _write_trace_csv(TRACE_CSV, trace_rows)

        if runtime_guard["decision"] != "runtime_within_signed_line":
            protected_after = _protected_artifact_hashes()
            manifest = _failure_manifest_payload(
                verdict="STOP_runtime_guard_exceeded_signed_line",
                stop_condition=str(runtime_guard.get("stop_reason")),
                details={"runtime_guard": runtime_guard, "trace_artifact": _artifact_ref(TRACE_JSONL)},
                protected_before=protected_before,
            )
            _write_json(FAILURE_MANIFEST, manifest)
            result_payload.update(
                {
                    "verdict": manifest["verdict"],
                    "s3d_results_void": True,
                    "stop_condition": manifest["stop_condition"],
                    "runtime_guard": runtime_guard,
                    "trace_artifacts": [_artifact_ref(TRACE_JSONL), _artifact_ref(TRACE_CSV)],
                    "protected_artifacts_before": protected_before,
                    "protected_artifacts_after": protected_after,
                    "banked_stop_probe_artifacts_byte_unchanged": _protected_hash_match(protected_before, protected_after),
                    "new_artifacts": _expected_new_artifact_paths(include_failure=True),
                }
            )
            _write_json(RESULT, _finalize_result_payload(result_payload, perf_start, cpu_start))
            _write_operator_bank_ops(result_payload)
            return result_payload

        serial_assertion = _serial_equivalence_assertion(unit_results)
        result_payload["serial_equivalence_assertion"] = serial_assertion

        reports = _build_reports(
            unit_results=unit_results,
            trace_rows=trace_rows,
            applied_line=applied_line,
            projection_path=projection_path,
            runtime_guard=runtime_guard,
            parallelism=parallelism,
            serial_assertion=serial_assertion,
            protected_before=protected_before,
        )
        certificate_report = reports["certificate_report"]
        null_report = reports["null_env_report"]
        baseline_report = reports["baseline_comparison"]
        replay_report = reports["replay_report"]
        final_verdict = reports["final_verdict"]

        _write_json(CERTIFICATE_REPORT, certificate_report)
        _write_json(NULL_ENV_REPORT, null_report)
        _write_json(BASELINE_COMPARISON, baseline_report)
        _write_json(REPLAY_REPORT, replay_report)

        if final_verdict["verdict"] != "s3d_all_certificates_green":
            _write_json(
                FAILURE_MANIFEST,
                _failure_manifest_payload(
                    verdict=str(final_verdict["verdict"]),
                    stop_condition=str(final_verdict["stop_condition"]),
                    details=final_verdict,
                    protected_before=protected_before,
                ),
            )

        protected_after = _protected_artifact_hashes()
        protected_match = _protected_hash_match(protected_before, protected_after)
        result_payload.update(
            {
                "verdict": final_verdict["verdict"],
                "stop_condition": final_verdict.get("stop_condition"),
                "s3d_results_void": bool(final_verdict.get("s3d_results_void", False)),
                "runtime_guard": runtime_guard,
                "trace_artifacts": [_artifact_ref(TRACE_JSONL), _artifact_ref(TRACE_CSV)],
                "certificate_report": _artifact_ref(CERTIFICATE_REPORT),
                "null_env_report": _artifact_ref(NULL_ENV_REPORT),
                "baseline_comparison": _artifact_ref(BASELINE_COMPARISON),
                "replay_report": _artifact_ref(REPLAY_REPORT),
                "protected_artifacts_before": protected_before,
                "protected_artifacts_after": protected_after,
                "banked_stop_probe_artifacts_byte_unchanged": protected_match,
                "heldout_users_800_999_touched": bool(any(row.get("heldout_users_800_999_touched") for row in trace_rows)),
                "future_observations_used": False,
                "torch_device": "cpu",
                "new_artifacts": _expected_new_artifact_paths(include_failure=FAILURE_MANIFEST.exists()),
            }
        )
        _write_json(RESULT, _finalize_result_payload(result_payload, perf_start, cpu_start))
        _write_operator_bank_ops(result_payload)
        return result_payload

    except BaseException as exc:  # preserve unexpected failures as artifacts
        protected_after = _protected_artifact_hashes()
        manifest = _failure_manifest_payload(
            verdict="STOP_UNEXPECTED_EXCEPTION",
            stop_condition=f"{type(exc).__name__}: {exc}",
            details={"traceback": traceback.format_exc()},
            protected_before=protected_before,
        )
        manifest["protected_artifacts_after"] = protected_after
        manifest["banked_stop_probe_artifacts_byte_unchanged"] = _protected_hash_match(protected_before, protected_after)
        _write_json(FAILURE_MANIFEST, manifest)
        result_payload.update(
            {
                "verdict": "STOP_UNEXPECTED_EXCEPTION",
                "s3d_results_void": True,
                "stop_condition": manifest["stop_condition"],
                "protected_artifacts_before": protected_before,
                "protected_artifacts_after": protected_after,
                "banked_stop_probe_artifacts_byte_unchanged": manifest["banked_stop_probe_artifacts_byte_unchanged"],
            }
        )
        _write_json(RESULT, _finalize_result_payload(result_payload, perf_start, cpu_start))
        _write_operator_bank_ops(result_payload)
        raise


def _verify_preconditions() -> dict[str, Any]:
    errors: list[str] = []
    signed = _parse_signed_budget_decision()
    signed_spec_001b = _parse_signed_spec_001b_decision()
    if not signed["option_b_checked"]:
        errors.append("BUDGET-DECISION §8 does not check Option B")
    if signed["line_cpu_hours"] is None:
        errors.append("BUDGET-DECISION §8 does not contain a concrete New line value")
    if not signed["operator"]:
        errors.append("BUDGET-DECISION §8 operator is missing")
    if not signed["date"]:
        errors.append("BUDGET-DECISION §8 date is missing")
    if signed_spec_001b["guard_basis"] != "2a":
        errors.append("001B §7 does not select guard basis 2a")
    if signed_spec_001b["k"] != 5.0:
        errors.append("001B §7 does not pin k=5")
    if not signed_spec_001b["anti_tuning_firewall_acknowledged"]:
        errors.append("001B §7 anti-tuning firewall acknowledgment is missing")
    if not signed_spec_001b["invariants_acknowledged"]:
        errors.append("001B §7 invariants acknowledgment is missing")
    if not signed_spec_001b["operator"]:
        errors.append("001B §7 operator is missing")
    if not signed_spec_001b["date"]:
        errors.append("001B §7 date is missing")

    git_readback = _read_git_state_without_git()
    if not git_readback.get("spec_001b_committed_at_head"):
        errors.append("signed 001B rule source is not identical to HEAD tree")
    if not git_readback.get("budget_note_committed_at_head"):
        errors.append("signed BUDGET-DECISION note is not identical to HEAD tree")
    if not git_readback.get("s3d_001b_impl_report_banked"):
        errors.append("001B implementation report is not present in HEAD tree")
    if not git_readback.get("variance_probe_banked"):
        errors.append("variance-probe artifact is not present in HEAD tree")
    if not git_readback.get("stop_commit_17cce05_in_history"):
        errors.append("12-line STOP commit 17cce05 is not in HEAD ancestry")

    return {
        "passed": not errors,
        "errors": errors,
        "signed_budget": signed,
        "signed_spec_001b": signed_spec_001b,
        "git_readback_without_git_command": git_readback,
        "read_only_rule_sources": [
            str(EXEC_CARD.relative_to(ROOT)),
            str(SPEC_CARD.relative_to(ROOT)),
            str(BUDGET_DECISION.relative_to(ROOT)),
        ],
        "superseded_historical_spec_source": str(SPEC_CARD_001A_SUPERSEDED.relative_to(ROOT)),
        "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_verify_preconditions",
        "run_started_at": _utc_timestamp(),
        "claim_ceiling": "precondition readback only",
    }


def _parse_signed_budget_decision() -> dict[str, Any]:
    text = BUDGET_DECISION.read_text(encoding="utf-8")
    lines = text.splitlines()
    section_start = next((idx for idx, line in enumerate(lines) if line.startswith("## 8.")), 0)
    section = "\n".join(lines[section_start:])
    option_b = bool(re.search(r"\[X\]\s*B\s+Raise line", section))
    operator_line_index = next((idx for idx, line in enumerate(lines, start=1) if "Operator:" in line and "New line" in line), -1)
    operator_line = lines[operator_line_index - 1] if operator_line_index > 0 else ""
    line_match = re.search(r"New line \(if B\):\s*_+\s*([0-9]+(?:\.[0-9]+)?)\s*_*\s*CPU-h", operator_line)
    operator_match = re.search(r"Operator:\s*_+([^_]+?)_+\s+Date:", operator_line)
    date_match = re.search(r"Date:\s*_+([^_]+?)_+\s+New line", operator_line)
    line_value = float(line_match.group(1)) if line_match else None
    return {
        "option_b_checked": option_b,
        "line_cpu_hours": line_value,
        "operator": operator_match.group(1).strip() if operator_match else "",
        "date": date_match.group(1).strip() if date_match else "",
        "line_number": int(operator_line_index),
        "signed_line_text": operator_line,
        "source_path": str(BUDGET_DECISION.relative_to(ROOT)),
    }


def _parse_signed_spec_001b_decision() -> dict[str, Any]:
    text = SPEC_CARD.read_text(encoding="utf-8")
    lines = text.splitlines()
    section_start = next((idx for idx, line in enumerate(lines) if line.startswith("## 7.")), 0)
    section = "\n".join(lines[section_start:])
    guard_line_index = next((idx for idx, line in enumerate(lines, start=1) if "Guard basis" in line), -1)
    operator_line_index = next((idx for idx, line in enumerate(lines, start=1) if "Operator:" in line and "Date:" in line), -1)
    guard_line = lines[guard_line_index - 1] if guard_line_index > 0 else ""
    operator_line = lines[operator_line_index - 1] if operator_line_index > 0 else ""
    guard_2a = bool(re.search(r"\[x\]\s*2a\s+k\s*=\s*__\s*5\s*__", guard_line, flags=re.IGNORECASE))
    k_match = re.search(r"\[x\]\s*2a\s+k\s*=\s*__\s*([0-9]+(?:\.[0-9]+)?)\s*__", guard_line, flags=re.IGNORECASE)
    anti_tuning = bool(re.search(r"Confirm anti-tuning firewall.*\[x\]\s*yes", section, flags=re.IGNORECASE))
    invariants = bool(re.search(r"Confirm invariants.*\[x\]\s*yes", section, flags=re.IGNORECASE))
    operator_match = re.search(r"Operator:\s*_+([^_]+?)_+\s+Date:", operator_line)
    date_match = re.search(r"Date:\s*_+([^_]+?)_+", operator_line)
    return {
        "guard_basis": "2a" if guard_2a else "",
        "k": float(k_match.group(1)) if k_match else None,
        "anti_tuning_firewall_acknowledged": anti_tuning,
        "invariants_acknowledged": invariants,
        "operator": operator_match.group(1).strip() if operator_match else "",
        "date": date_match.group(1).strip() if date_match else "",
        "guard_line_number": int(guard_line_index),
        "operator_line_number": int(operator_line_index),
        "guard_line_text": guard_line,
        "operator_line_text": operator_line,
        "source_path": str(SPEC_CARD.relative_to(ROOT)),
        "rule_source_status": "001B supersedes 001A for S3d execution",
    }


def _read_git_state_without_git() -> dict[str, Any]:
    """Read HEAD/history/index via dulwich; no git executable is invoked."""

    from dulwich import porcelain
    from dulwich.objects import Blob, Commit, Tree
    from dulwich.repo import Repo

    repo = Repo(str(ROOT))
    head_hash = repo.head().decode()
    head_ref = repo.refs.read_ref(b"HEAD").decode()
    store = repo.object_store

    def walk_commits(start: str) -> Iterable[tuple[str, Commit]]:
        seen: set[bytes] = set()
        stack = [start.encode()]
        while stack:
            item = stack.pop()
            if item in seen:
                continue
            seen.add(item)
            obj = store[item]
            if not isinstance(obj, Commit):
                continue
            yield item.decode(), obj
            stack.extend(obj.parents)

    def tree_lookup(tree_id: bytes, rel_path: str) -> tuple[int, bytes, Any] | None:
        cur = store[tree_id]
        parts = rel_path.replace("\\", "/").split("/")
        for index, part in enumerate(parts):
            if not isinstance(cur, Tree):
                return None
            found = None
            for name, mode, sha in cur.iteritems():
                if name.decode() == part:
                    found = (mode, sha, store[sha])
                    break
            if found is None:
                return None
            mode, sha, obj = found
            if index == len(parts) - 1:
                return mode, sha, obj
            cur = obj
        return None

    def blob_bytes_at(commit_hash: str, rel_path: str) -> bytes | None:
        commit = store[commit_hash.encode()]
        entry = tree_lookup(commit.tree, rel_path)
        if entry is None:
            return None
        _, _, obj = entry
        if not isinstance(obj, Blob):
            return None
        return obj.as_raw_string()

    spec_001b_rel = str(SPEC_CARD.relative_to(ROOT)).replace("\\", "/")
    impl_report_rel = str(S3D_001B_IMPL_REPORT.relative_to(ROOT)).replace("\\", "/")
    budget_rel = str(BUDGET_DECISION.relative_to(ROOT)).replace("\\", "/")
    spec_001b_blob = blob_bytes_at(head_hash, spec_001b_rel)
    budget_blob = blob_bytes_at(head_hash, budget_rel)
    impl_report_blob = blob_bytes_at(head_hash, impl_report_rel)
    variance_rel = "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe.json"
    variance_blob = blob_bytes_at(head_hash, variance_rel)
    variance_trace_blob = blob_bytes_at(head_hash, "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe_trace.csv")
    stop_projection_blob = blob_bytes_at(head_hash, "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_compute_projection.json")
    found_stop = [
        {"hash": commit_hash, "subject": (commit.message.decode(errors="replace").splitlines() or [""])[0]}
        for commit_hash, commit in walk_commits(head_hash)
        if commit_hash.startswith("17cce05")
    ]
    try:
        status = porcelain.status(repo)
        status_payload = {
            "staged": {key: [str(item) for item in value] for key, value in status.staged.items()},
            "unstaged_count": len(status.unstaged),
            "untracked_count": len(status.untracked),
            "fsp_relevant_unstaged": [
                _decode_status_path(item)
                for item in status.unstaged
                if "FSP-PUM-ENV-IDPROBE-001A" in _decode_status_path(item) or "fsp_pum_env" in _decode_status_path(item)
            ],
        }
    except Exception as exc:  # pragma: no cover - status readback fallback
        status_payload = {"status_error": f"{type(exc).__name__}: {exc}"}

    return {
        "repo_root": str(ROOT),
        "branch_ref": head_ref,
        "head_hash": head_hash,
        "status_without_git_command": status_payload,
        "spec_001b_committed_at_head": spec_001b_blob == SPEC_CARD.read_bytes(),
        "budget_note_committed_at_head": budget_blob == BUDGET_DECISION.read_bytes(),
        "s3d_001b_impl_report_banked": impl_report_blob is not None,
        "variance_probe_banked": variance_blob is not None and variance_trace_blob is not None,
        "stop_projection_banked": stop_projection_blob is not None,
        "stop_commit_17cce05_in_history": bool(found_stop),
        "stop_commit_matches": found_stop,
        "implementation": "dulwich object/index readback; no git executable invoked",
    }


def _decode_status_path(item: Any) -> str:
    if isinstance(item, bytes):
        return item.decode(errors="replace").replace("\\", "/")
    return str(item).replace("\\", "/")


def project_s3d_part0_cpu_time_units(units: Sequence[Mapping[str, Any]], applied_line: float) -> dict[str, Any]:
    """Shared S3d PART-0 projection gate from measured wall/process CPU seconds.

    This is the single projection multiplication/summation routine used by the
    canonical battery launch runner and by the standalone CPU-time re-gate runner.
    It deliberately accepts already-measured units so fit/score/certificate/NULL
    metric logic stays outside the cost-gate math.
    """

    components: dict[str, Any] = {}
    for unit in units:
        name = str(unit["component"])
        wall_seconds = float(unit["measured_wall_seconds"])
        cpu_seconds = float(unit["measured_process_cpu_seconds"])
        projected_units = float(unit["projected_units"])
        projected_wall = wall_seconds * projected_units
        projected_cpu = cpu_seconds * projected_units
        ratio = _ratio(wall_seconds, cpu_seconds)
        components[name] = {
            "measured_wall_seconds": wall_seconds,
            "measured_process_cpu_seconds": cpu_seconds,
            "projected_units": projected_units,
            "projected_wall_seconds": projected_wall,
            "projected_process_cpu_seconds": projected_cpu,
            "projected_wall_hours": projected_wall / 3600.0,
            "projected_cpu_hours": projected_cpu / 3600.0,
            "wall_cpu_ratio": ratio,
            "wall_cpu_ratio_flag_gt_1_25": bool(ratio > 1.25),
            "null_env_units_included": float(unit.get("null_env_units_included", 0.0)),
            "note": str(unit.get("note", "")),
            "timing_source": str(unit.get("timing_source", "")),
            "replaced_by_serial_mean": bool(unit.get("replaced_by_serial_mean", False)),
        }
        for optional_key in ("cell_id", "member", "eval_user_id_measured", "phase", "aggregation_rule"):
            if optional_key in unit:
                components[name][optional_key] = unit[optional_key]

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
    total_cpu_hours = total_cpu / 3600.0
    relation = "within_line" if total_cpu_hours <= float(applied_line) else "exceeds_line"
    decision = (
        "s3d_part0_projection_within_signed_line"
        if relation == "within_line"
        else "STOP_s3d_part0_projection_exceeds_signed_line"
    )
    flags = [name for name, item in components.items() if bool(item["wall_cpu_ratio_flag_gt_1_25"])]
    return {
        "cpu_hour_limit": float(applied_line),
        "metric_basis": "per-unit process CPU-time (time.process_time user+sys)",
        "components": components,
        "total_projected_wall_seconds": total_wall,
        "total_projected_process_cpu_seconds": total_cpu,
        "total_projected_wall_hours": total_wall / 3600.0,
        "total_projected_cpu_hours": total_cpu_hours,
        "projected_cpu_hours": total_cpu_hours,
        "projected_wall_hours_disclosed": total_wall / 3600.0,
        "gate_relation": relation,
        "line_relation": relation,
        "signed_line_relation": "within_signed_line" if relation == "within_line" else "exceeds_signed_line",
        "decision": decision,
        "wall_cpu_ratio_flag_count": len(flags),
        "wall_cpu_ratio_flag_components": flags,
        "null_env_projected_wall_seconds_included": null_wall,
        "null_env_projected_cpu_seconds_included": null_cpu,
        "null_env_projected_wall_hours_included": null_wall / 3600.0,
        "null_env_projected_cpu_hours_included": null_cpu / 3600.0,
        "producer_function": (
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::"
            "project_s3d_part0_cpu_time_units"
        ),
    }


def s3d_part0_projection_units_from_measurements(
    measurements: Mapping[str, Any],
    *,
    replacements: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    replacement_map = _replacement_component_values(replacements or {})
    units: list[dict[str, Any]] = []

    def add(
        name: str,
        wall_seconds: float,
        cpu_seconds: float,
        projected_units: float,
        note: str,
        *,
        null_units: float = 0.0,
        source: str,
        replaced_by_serial_mean: bool = False,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        units.append(
            {
                "component": name,
                "measured_wall_seconds": float(wall_seconds),
                "measured_process_cpu_seconds": float(cpu_seconds),
                "projected_units": float(projected_units),
                "note": note,
                "null_env_units_included": float(null_units),
                "timing_source": source,
                "replaced_by_serial_mean": bool(replaced_by_serial_mean),
                **dict(context or {}),
            }
        )

    gen = measurements["cert_set_generation"]
    add(
        "generation_all_7_cert_sets",
        float(gen["wall_clock_seconds"]),
        float(gen["process_cpu_seconds"]),
        7.0,
        "one measured cert-set generation x 7 S3d cells",
        null_units=1.0,
        source="fresh_cpu_timed_measurement",
        context={"cell_id": gen.get("cell_id"), "aggregation_rule": "one measured cert-set generation multiplied by seven S3d cells"},
    )
    ideal = measurements["ideal_per_user_one_cell"]
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
        context={
            "cell_id": ideal.get("cell_id"),
            "eval_user_id_measured": ideal.get("user_id"),
            "aggregation_rule": "one ideal eval user for one cell multiplied by seven cells and 160 eval users per cell",
        },
    )
    for name, key, note, projected_units, null_units in (
        ("logreg_F1_selected_cert_plus_NULL", "logreg_F1_selected", "obs_decoder_logreg selected F1 config on camouflage_off plus NULL_env", 2.0, 1.0),
        ("logreg_F2_reference_measured_not_counted", "logreg_F2_reference", "measured because PART 0 names F1/F2; not counted because selected logreg recipe is F1", 0.0, 0.0),
        ("gbt_half_data_selected_cert_plus_NULL", "gbt_half_data_selected", "obs_decoder_gbt selected F2 half-data config on camouflage_off plus NULL_env", 2.0, 1.0),
        ("gru_selected_cert_plus_NULL", "gru_selected", "obs_decoder_gru selected config on camouflage_off plus NULL_env", 2.0, 1.0),
        ("seq_full_selected_cert_plus_NULL", "seq_full_selected", "seq_full selected config on constant_none plus NULL_env", 2.0, 1.0),
        ("seq_W15_selected_cert_plus_NULL", "seq_W15_selected", "seq_W15 selected config on low_diversity plus NULL_env", 2.0, 1.0),
    ):
        m = measurements[key]
        add(
            name,
            float(m["fit_plus_validation_wall_clock_seconds"]),
            float(m["fit_plus_validation_process_cpu_seconds"]),
            projected_units,
            note,
            null_units=null_units,
            source="fresh_outer_process_time_bracket",
            context={"cell_id": m.get("cell_id"), "member": m.get("member"), "aggregation_rule": m.get("aggregation_rule", "")},
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
        ("retrieval_family", {"rag_k5_episode_retrieval": 2.0, "nearest_neighbor_user_matching": 2.0}),
        (
            "degenerate_family",
            {"predict_all": 2.0, "predict_none": 2.0, "majority": 2.0, "global_prior": 2.0},
        ),
        (
            "ls_online_family",
            {"discounted_LS_lambda_0.95": 2.0, "running_average_preference_regressor": 2.0},
        ),
    ):
        for member, projected_units in units_by_member.items():
            component_name = f"{family_name}_{member}_cert_plus_NULL"
            repl = replacement_map.get(component_name)
            m = measurements[family_name]["members"][member]
            add(
                component_name,
                float(repl["wall_seconds"] if repl else m["projected_one_member_cell_wall_seconds"]),
                float(repl["cpu_seconds"] if repl else m["projected_one_member_cell_process_cpu_seconds"]),
                projected_units,
                f"{member}: projected one member-cell x favorable cert cell plus NULL_env",
                null_units=1.0,
                source=str(repl["source"] if repl else "fresh_process_time_fit_score_brackets"),
                replaced_by_serial_mean=bool(repl),
                context={
                    "cell_id": m.get("cell_id"),
                    "member": member,
                    "eval_user_id_measured": m.get("eval_user_id_measured"),
                    "aggregation_rule": "projected fit+160*score unit",
                },
            )

    bootstrap = measurements["bootstrap"]
    add(
        "bootstrap_18_certificate_member_rows",
        float(bootstrap["wall_clock_seconds"]),
        float(bootstrap["process_cpu_seconds"]),
        18.0,
        "rho bootstrap CI for 18 certificate member rows; NULL table has no rho CI",
        source="fresh_outer_process_time_bracket",
        context={"cell_id": bootstrap.get("cell_id"), "member": bootstrap.get("member")},
    )
    return units


def _measure_generation_cputime(design: Mapping[str, Any], spec: Any, run_id: str) -> dict[str, Any]:
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    member_sha, adjudicator_sha, member_bytes, adjudicator_bytes, record_count = _hash_spec_streams(
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
        "timing_producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_measure_generation_cputime",
        "run_id": run_id,
        "aggregation_rule": "one measured cert-set generation multiplied by seven S3d cells",
    }


def _measure_ideal_cputime(
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
    measurement["timing_producer_function"] = "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_measure_ideal_cputime"
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
    measurement["timing_producer_function"] = "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_timed_selected_measurement"
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
                "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::"
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
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::"
            "_measure_prefix_family_one_eval_user_cputime"
        ),
        "wall_clock_seconds": time.perf_counter() - wall_start,
        "process_cpu_seconds": time.process_time() - cpu_start,
        "run_id": run_id,
    }


def _run_dominant_serial_remeasurements(
    part0: Any,
    design: Mapping[str, Any],
    specs: Mapping[str, Any],
    run_id: str,
) -> dict[str, Any]:
    ideal_rows = [
        _measure_ideal_cputime(design, specs["camouflage_off"], user_id=user_id, run_id=run_id)
        for user_id in DOMINANT_REMEASURE_USERS
    ]
    nearest_rows = [
        _measure_prefix_family_one_eval_user_cputime(
            part0,
            design,
            specs["stable_facts"],
            {"nearest_neighbor_user_matching": NearestNeighborUserMatchingPredictor},
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
            {"discounted_LS_lambda_0.95": DiscountedLeastSquaresPredictor},
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
            "projected_wall_seconds_mean_se": _mean_se([float(row["projected_one_member_cell_wall_seconds"]) for row in nearest_rows]),
            "projected_process_cpu_seconds_mean_se": _mean_se(
                [float(row["projected_one_member_cell_process_cpu_seconds"]) for row in nearest_rows]
            ),
            "aggregation_rule": "replace projected one-member-cell nearest-neighbor unit with serial-isolation mean over eval users 640, 720, 799",
        },
        "ls_online_family_discounted_LS_lambda_0.95_cert_plus_NULL": {
            "unit": "discounted_LS_lambda_0.95_projected_one_member_cell",
            "component_replaced": "ls_online_family_discounted_LS_lambda_0.95_cert_plus_NULL",
            "rows": discounted_rows,
            "projected_wall_seconds_mean_se": _mean_se([float(row["projected_one_member_cell_wall_seconds"]) for row in discounted_rows]),
            "projected_process_cpu_seconds_mean_se": _mean_se(
                [float(row["projected_one_member_cell_process_cpu_seconds"]) for row in discounted_rows]
            ),
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


def _mean_se(values: Sequence[float]) -> dict[str, Any]:
    vals = [float(value) for value in values]
    mean = float(statistics.mean(vals))
    se = float(statistics.stdev(vals) / math.sqrt(len(vals))) if len(vals) > 1 else 0.0
    return {"n": len(vals), "mean": mean, "se": se, "values": vals}


def _ratio(wall_seconds: float, cpu_seconds: float) -> float:
    return float(wall_seconds) / max(float(cpu_seconds), 1e-12)


def _run_part0_projection_line(applied_line: float, output_path: Path) -> dict[str, Any]:
    run_started_at = _utc_timestamp()
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    run_id = f"s3d-part0-line{_line_label(applied_line)}-{run_started_at}"
    design = load_frozen_design(FROZEN_DESIGN)
    environment = _single_thread_environment()
    specs = {spec.cell_id: spec for spec in build_s3d_cert_set_specs(design)}

    generation_measurement = _measure_generation_cputime(design, specs["constant_none"], run_id)
    ideal_measurement = _measure_ideal_cputime(design, specs["camouflage_off"], user_id=640, run_id=run_id)
    lower_bound_cpu_hours = float(ideal_measurement["process_cpu_seconds"]) * 160.0 / 3600.0
    initial_projection = {
        "task_id": TASK_ID,
        "stage": "S3d",
        "artifact": f"s3d_compute_projection_line{_line_label(applied_line)}",
        "part": "PART 0 lower-bound projection under signed line",
        "claim_ceiling": "PART 0 compute projection only; no certificate, NULL, environment-validity, gap, mechanism, agency, or EGO claim",
        "cpu_hour_limit": float(applied_line),
        "applied_line_source": str(BUDGET_DECISION.relative_to(ROOT)),
        "single_thread_environment": environment,
        "measurements": {
            "cert_set_generation": generation_measurement,
            "ideal_per_user_one_cell": ideal_measurement,
            "fit_score_cost_classes": [],
        },
        "projection_rule": {
            "declared_assumption": "linear projection from measured per-user full-prefix S2 ideal cost; one camouflage_off cell has 160 eval users",
            "lower_bound_basis": "camouflage_off S2 ideal process CPU-time alone, excluding generation, fitting, scoring, other cells, bootstrap, and NULL-env",
            "camouflage_off_eval_users": 160,
        },
        "projection_lower_bound_cpu_hours": lower_bound_cpu_hours,
        "camouflage_off_ideal_projected_cpu_hours": lower_bound_cpu_hours,
        "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_run_part0_projection_line",
        "input_artifacts": [str(FROZEN_DESIGN.relative_to(ROOT)), str(BUDGET_DECISION.relative_to(ROOT))],
        "run_id": run_id,
        "run_started_at": run_started_at,
        "code_path_hash": _code_path_hash(),
    }
    if lower_bound_cpu_hours > applied_line:
        final = {
            **initial_projection,
            "projected_cpu_hours": lower_bound_cpu_hours,
            "decision": "STOP_s3d_part0_projection_exceeds_signed_line",
            "runtime_guard_decision": "STOP_s3d_part0_projection_exceeds_signed_line",
            "run_finished_at": _utc_timestamp(),
            "wall_clock_seconds": time.perf_counter() - start_wall,
            "process_cpu_seconds": time.process_time() - start_cpu,
        }
        _write_json(output_path, final)
        return final

    projection_runner = _load_original_part0_runner()
    vocabulary = _read_json(VOCABULARY)
    selected_recipes = _selected_recipe_configs()
    selected_recipe_hashes = {name: _sha256(path) for name, path in _selected_recipe_paths().items()}

    measurements: dict[str, Any] = {
        "cert_set_generation": generation_measurement,
        "ideal_per_user_one_cell": ideal_measurement,
    }
    measurements["logreg_F1_selected"] = _timed_selected_measurement(
        "logreg_F1_selected",
        lambda: projection_runner._measure_sklearn_selected(
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
        lambda: projection_runner._measure_sklearn_selected(
            design,
            specs["camouflage_off"],
            obs_decoders.decoder_grid("obs_decoder_logreg")[4],
            features="F2",
            vocabulary=vocabulary,
        ),
        run_id=run_id,
        projected_seconds_key="fit_plus_validation",
    )
    measurements["gbt_half_data_selected"] = _timed_selected_measurement(
        "gbt_half_data_selected",
        lambda: projection_runner._measure_sklearn_selected(
            design,
            specs["camouflage_off"],
            selected_recipes["obs_decoder_gbt"],
            features="F2",
            vocabulary=vocabulary,
            fit_user_filter=set(obs_decoders.gbt_fit_user_ids()),
        ),
        run_id=run_id,
        projected_seconds_key="fit_plus_validation",
    )
    measurements["gru_selected"] = _timed_selected_measurement(
        "gru_selected",
        lambda: projection_runner._measure_gru_selected(
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
        lambda: projection_runner._measure_gru_selected(
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
        lambda: projection_runner._measure_gru_selected(
            design,
            specs["low_diversity"],
            selected_recipes["seq_window_with_action_conditioning_W15_no_cross_session_persistence"],
            member_kind="seq_window_with_action_conditioning_W15_no_cross_session_persistence",
        ),
        run_id=run_id,
        projected_seconds_key="fit_plus_validation",
    )
    measurements["table_family"] = _measure_prefix_family_one_eval_user_cputime(
        projection_runner,
        design,
        specs["low_diversity"],
        {
            "successor_map": SuccessorMapPredictor,
            "transition_table": TransitionTablePredictor,
            "count_table": CountTablePredictor,
            "fsm_planner": FsmPlannerPredictor,
            "episodic_traversal": EpisodicTraversalPredictor,
        },
        eval_user_id=640,
        run_id=run_id,
    )
    measurements["retrieval_family"] = _measure_prefix_family_one_eval_user_cputime(
        projection_runner,
        design,
        specs["stable_facts"],
        {
            "rag_k5_episode_retrieval": RagK5EpisodeRetrievalPredictor,
            "nearest_neighbor_user_matching": NearestNeighborUserMatchingPredictor,
        },
        eval_user_id=640,
        run_id=run_id,
    )
    measurements["degenerate_family"] = _measure_prefix_family_one_eval_user_cputime(
        projection_runner,
        design,
        specs["constant_none"],
        {
            "predict_all": PredictAllPredictor,
            "predict_none": PredictNonePredictor,
            "majority": MajorityPredictor,
            "global_prior": GlobalPriorPredictor,
        },
        eval_user_id=640,
        run_id=run_id,
    )
    measurements["ls_online_family"] = _measure_prefix_family_one_eval_user_cputime(
        projection_runner,
        design,
        specs["flat_theta"],
        {
            "discounted_LS_lambda_0.95": DiscountedLeastSquaresPredictor,
            "running_average_preference_regressor": RunningAveragePreferenceRegressor,
        },
        eval_user_id=640,
        run_id=run_id,
    )
    measurements["bootstrap"] = _timed_selected_measurement(
        "bootstrap",
        lambda: projection_runner._measure_bootstrap_unit(),
        run_id=run_id,
        projected_seconds_key="wall_clock",
    )

    initial_units = s3d_part0_projection_units_from_measurements(measurements, replacements=None)
    initial_cpu_projection = project_s3d_part0_cpu_time_units(initial_units, applied_line)
    dominant_serial_remeasurements = _run_dominant_serial_remeasurements(projection_runner, design, specs, run_id)
    final_units = s3d_part0_projection_units_from_measurements(measurements, replacements=dominant_serial_remeasurements)
    full_projection = project_s3d_part0_cpu_time_units(final_units, applied_line)
    full_projection["line_relation"] = full_projection["signed_line_relation"]
    full_projection["linear_projection_assumptions"] = [
        "cert-set generation scales linearly across the 7 S3d cells",
        "S2 ideal cost scales from one eval user to 160 eval users per cell across 7 cells",
        "sklearn/GRU selected-recipe measurements are one full fit+validation member-cell units",
        "prefix-family measurements are fit_640 plus one eval user scoring, scaled to 160 eval users per member-cell",
        "each measured member-cell is counted once for its favorable certificate cell and once for NULL_env",
        "logreg_F2 is measured for named PART 0 coverage but not counted because the banked selected logreg recipe is F1",
    ]

    decision = str(full_projection["decision"])
    final = {
        **initial_projection,
        "artifact": f"s3d_compute_projection_line{_line_label(applied_line)}",
        "part": "PART 0 full projection under signed line",
        "selected_recipe_sha256": selected_recipe_hashes,
        "full_part0_measurements": measurements,
        "initial_cpu_time_projection_before_dominant_remeasure": initial_cpu_projection,
        "dominant_serial_remeasurements": dominant_serial_remeasurements,
        "full_part0_projection": full_projection,
        "projected_cpu_hours": float(full_projection["total_projected_cpu_hours"]),
        "projection_cpu_hours": float(full_projection["total_projected_cpu_hours"]),
        "projection_total_cpu_hours": float(full_projection["total_projected_cpu_hours"]),
        "projected_wall_hours_disclosed": float(full_projection["total_projected_wall_hours"]),
        "decision": decision,
        "runtime_guard_decision": decision,
        "run_finished_at": _utc_timestamp(),
        "wall_clock_seconds": time.perf_counter() - start_wall,
        "process_cpu_seconds": time.process_time() - start_cpu,
        "wall_clock_based_cpu_hours_disclosed": float(full_projection["total_projected_wall_hours"]),
        "contention_robust_cpu_hours": float(full_projection["total_projected_cpu_hours"]),
    }
    _write_json(output_path, final)
    return final


def _battery_unit_payloads() -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for cell in S3D_CERT_CELLS:
        phase = "null" if cell.cell_id == "NULL_env" else "cert"
        payloads.append(
            {
                "unit_type": "ideal",
                "phase": phase,
                "cell_id": cell.cell_id,
                "member": "ideal",
                "unit_id": f"ideal::{phase}::{cell.cell_id}",
            }
        )
    for spec in CERT_MEMBER_SPECS:
        payloads.append(
            {
                "unit_type": "member",
                "phase": "cert",
                "cell_id": str(spec["cell_id"]),
                "member": str(spec["member"]),
                "unit_id": f"member::cert::{spec['member']}::{spec['cell_id']}",
            }
        )
    for member in NULL_MEMBER_NAMES:
        payloads.append(
            {
                "unit_type": "member",
                "phase": "null",
                "cell_id": "NULL_env",
                "member": member,
                "unit_id": f"member::null::{member}::NULL_env",
            }
        )
    return payloads


def _run_units_parallel(
    unit_payloads: Sequence[Mapping[str, Any]],
    *,
    max_workers: int,
    applied_line: float,
    initial_cpu_hours: float,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]]:
    run_started_at = _utc_timestamp()
    parallel_wall_start = time.perf_counter()
    trace_rows: list[dict[str, Any]] = []
    unit_results: dict[str, dict[str, Any]] = {}
    pending_iter = iter([dict(item) for item in unit_payloads])
    futures: dict[Any, dict[str, Any]] = {}
    cumulative_cpu_hours = float(initial_cpu_hours)
    stopped = False
    stop_reason = None

    TRACE_JSONL.write_text("", encoding="utf-8")
    with ProcessPoolExecutor(max_workers=int(max_workers)) as executor:
        for _ in range(int(max_workers)):
            try:
                payload = next(pending_iter)
            except StopIteration:
                break
            futures[executor.submit(_run_unit_worker, payload)] = payload
        while futures:
            done, _ = wait(tuple(futures), return_when=FIRST_COMPLETED)
            for future in done:
                payload = futures.pop(future)
                result = future.result()
                unit_id = str(result["unit_id"])
                unit_results[unit_id] = result
                cumulative_cpu_hours += float(result["process_cpu_seconds"]) / 3600.0
                row = _trace_row_from_unit(result, cumulative_cpu_hours)
                trace_rows.append(row)
                _append_trace_jsonl(TRACE_JSONL, row)
                if cumulative_cpu_hours > float(applied_line):
                    stopped = True
                    stop_reason = f"runtime_guard_exceeded_after_{unit_id}"
                    for pending in futures:
                        pending.cancel()
                    break
                try:
                    payload_next = next(pending_iter)
                except StopIteration:
                    continue
                futures[executor.submit(_run_unit_worker, payload_next)] = payload_next
            if stopped:
                break

    total_unit_wall_sum = sum(float(row["wall_clock_seconds"]) for row in trace_rows)
    total_unit_cpu_sum = sum(float(row["process_cpu_seconds"]) for row in trace_rows)
    wall_cpu_flags = [row for row in trace_rows if bool(row["wall_cpu_ratio_flag_gt_1_25"])]
    runtime_guard = {
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "parallel_elapsed_wall_clock_seconds": time.perf_counter() - parallel_wall_start,
        "applied_cpu_hour_limit": float(applied_line),
        "initial_part0_contention_robust_cpu_hours_included": float(initial_cpu_hours),
        "completed_unit_count": len(trace_rows),
        "expected_unit_count": len(unit_payloads),
        "contention_robust_cpu_hours": float(cumulative_cpu_hours),
        "battery_units_contention_robust_cpu_hours": float(total_unit_cpu_sum) / 3600.0,
        "wall_clock_based_cpu_hours_disclosed": (float(total_unit_wall_sum) / 3600.0) + float(initial_cpu_hours),
        "wall_cpu_ratio_flag_count": len(wall_cpu_flags),
        "wall_cpu_ratio_flag_unit_ids": [str(row["unit_id"]) for row in wall_cpu_flags],
        "decision": "STOP_runtime_guard_exceeded_signed_line" if stopped else "runtime_within_signed_line",
        "stop_reason": stop_reason,
        "trace_path": str(TRACE_JSONL.relative_to(ROOT)),
    }
    return trace_rows, unit_results, runtime_guard


def _run_unit_worker(payload: Mapping[str, Any]) -> dict[str, Any]:
    _configure_worker_environment()
    run_started_at = _utc_timestamp()
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    design = load_frozen_design(FROZEN_DESIGN)
    specs = {spec.cell_id: spec for spec in build_s3d_cert_set_specs(design)}
    cell_id = str(payload["cell_id"])
    unit_type = str(payload["unit_type"])
    if cell_id not in specs:
        raise ValueError(f"unknown S3d cell_id: {cell_id}")
    if unit_type == "ideal":
        scored = _score_ideal_cell(design, specs[cell_id])
    elif unit_type == "member":
        scored = _score_member_cell(design, specs[cell_id], str(payload["member"]))
    else:
        raise ValueError(f"unknown unit_type: {unit_type}")
    wall_seconds = time.perf_counter() - wall_start
    cpu_seconds = time.process_time() - cpu_start
    scored.update(
        {
            "unit_id": str(payload["unit_id"]),
            "unit_type": unit_type,
            "phase": str(payload["phase"]),
            "cell_id": cell_id,
            "member": str(payload["member"]),
            "wall_clock_seconds": float(wall_seconds),
            "process_cpu_seconds": float(cpu_seconds),
            "wall_cpu_ratio": float(wall_seconds / max(cpu_seconds, 1e-12)),
            "wall_cpu_ratio_flag_gt_1_25": bool(wall_seconds / max(cpu_seconds, 1e-12) > 1.25),
            "single_thread_environment": _single_thread_environment(),
            "run_started_at": run_started_at,
            "run_finished_at": _utc_timestamp(),
            "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_run_unit_worker",
            "code_path_hash": _code_path_hash(),
            "input_artifacts": [str(FROZEN_DESIGN.relative_to(ROOT))],
            "heldout_users_800_999_touched": False,
            "future_observations_used": False,
            "metric_digest": _metric_digest(scored),
        }
    )
    return scored


def _score_ideal_cell(design: Mapping[str, Any], spec: Any) -> dict[str, Any]:
    records_by_user, style_by_user = _records_and_style_by_user(design, spec.trajectory_spec)
    targets: list[int] = []
    predictions: list[int] = []
    actions: list[str] = []
    per_user: list[dict[str, Any]] = []
    atom_count = None
    array_bytes = None
    for user_id in range(spec.eval_user_range[0], spec.eval_user_range[1] + 1):
        if 800 <= user_id <= 999:
            raise RuntimeError(f"heldout_user_touched_by_ideal:{user_id}")
        filt = FactoredExactFilter(
            design,
            filter_seed=independent_filter_seed(spec.master_seed, f"s3d_battery:{spec.cell_id}:{int(user_id)}"),
            true_environment_seed=spec.master_seed,
            variant=spec.variant,
            user_id=int(user_id),
            style_map=style_by_user[int(user_id)],
            z_quadrature_points=3,
        )
        atom_count = int(filt.atom_count)
        array_bytes = int(filt.array_bytes())
        user_targets: list[int] = []
        user_predictions: list[int] = []
        user_actions: list[str] = []
        for record in records_by_user[int(user_id)]:
            action = str(record.action)
            distribution = filt.predict_distribution(action)
            pred = int(np.argmax(np.asarray(distribution, dtype=float)))
            target = int(record.observation["symbol"])
            user_predictions.append(pred)
            user_targets.append(target)
            user_actions.append(action)
            filt.observe(IdealPrefixEvent(action=action, symbol=target))
        targets.extend(user_targets)
        predictions.extend(user_predictions)
        actions.extend(user_actions)
        per_user.append(_per_user_confusion(user_id, user_targets, user_predictions, user_actions))
    return _score_payload(
        targets,
        predictions,
        actions,
        per_user,
        extra={
            "filter_class": "src.fsp_pum_env.factored_filter.FactoredExactFilter",
            "z_quadrature_points_per_dim": 3,
            "atom_count": atom_count,
            "posterior_array_bytes": array_bytes,
            "variant": spec.variant,
            "master_seed": int(spec.master_seed),
        },
    )


def _score_member_cell(design: Mapping[str, Any], spec: Any, member: str) -> dict[str, Any]:
    if member in SELECTED_RECIPE_BY_MEMBER:
        return _score_selected_s3c_member(design, spec, member)
    if member in PREFIX_MEMBER_CLASSES:
        return _score_prefix_member(design, spec, member, PREFIX_MEMBER_CLASSES[member])
    raise ValueError(f"unknown S3d battery member: {member}")


def _score_selected_s3c_member(design: Mapping[str, Any], spec: Any, member: str) -> dict[str, Any]:
    recipe_path = ARTIFACT_ROOT / "s3c_models" / SELECTED_RECIPE_BY_MEMBER[member]
    recipe = _read_json(recipe_path)
    config = recipe["selected_config"]["config"]
    actions = frozen_action_list(design)
    alphabet_size = response_alphabet_size(design)
    vocabulary = _read_json(VOCABULARY)
    collect_start = time.perf_counter()
    events_by_split = obs_decoders._collect_train_events_one_set(design, spec.trajectory_spec)
    collect_seconds = time.perf_counter() - collect_start
    result, counts = obs_decoders._fit_eval_s3c_config_on_events(
        design,
        config,
        events_by_split,
        actions,
        alphabet_size=alphabet_size,
        vocabulary=vocabulary,
    )
    eval_events = _validation_events_in_prediction_order(events_by_split, member)
    targets = [int(event.observation["symbol"]) for event in eval_events]
    predictions = [int(value) for value in result["predictions"]]
    if len(targets) != len(predictions):
        raise RuntimeError(f"prediction_target_length_mismatch:{member}:{len(predictions)}:{len(targets)}")
    actions_eval = [str(event.action) for event in eval_events]
    per_user = _confusion_by_user_from_events(eval_events, predictions)
    payload = _score_payload(
        targets,
        predictions,
        actions_eval,
        per_user,
        extra={
            "variant": spec.variant,
            "master_seed": int(spec.master_seed),
            "recipe_path": str(recipe_path.relative_to(ROOT)),
            "recipe_sha256": _sha256(recipe_path),
            "selected_config": config,
            "fit_eval_result": {
                key: value
                for key, value in result.items()
                if key not in {"targets", "predictions"}
            },
            "records_consumed": counts,
            "event_collect_wall_clock_seconds": collect_seconds,
        },
    )
    return payload


def _score_prefix_member(design: Mapping[str, Any], spec: Any, member: str, predictor_cls: Callable[..., Any]) -> dict[str, Any]:
    records_by_user, _ = _records_and_style_by_user(design, spec.trajectory_spec)
    fit_records = [record for user_id in range(spec.fit_user_range[0], spec.fit_user_range[1] + 1) for record in records_by_user[user_id]]
    predictor = predictor_cls.from_design(design)
    fit_start = time.perf_counter()
    if hasattr(predictor, "fit"):
        predictor.fit(fit_records)
    else:
        for record in fit_records:
            predictor.observe(record)
    fit_seconds = time.perf_counter() - fit_start

    targets: list[int] = []
    predictions: list[int] = []
    actions: list[str] = []
    per_user: list[dict[str, Any]] = []
    fallback_total = 0
    fallback_count = 0
    for user_id in range(spec.eval_user_range[0], spec.eval_user_range[1] + 1):
        if 800 <= user_id <= 999:
            raise RuntimeError(f"heldout_user_touched_by_member:{member}:{user_id}")
        query_predictor = copy.deepcopy(predictor)
        user_targets: list[int] = []
        user_predictions: list[int] = []
        user_actions: list[str] = []
        for record in records_by_user[int(user_id)]:
            parsed = event_from_mapping(record)
            if member == "episodic_traversal":
                fallback_total += 1
                fallback_count += int(_episodic_prediction_would_fallback(query_predictor, parsed.action))
            prediction = query_predictor.predict([parsed.action])
            distribution = prediction[str(parsed.action)]
            pred = int(np.argmax(np.asarray(distribution, dtype=float)))
            target = int(parsed.observation["symbol"])
            user_targets.append(target)
            user_predictions.append(pred)
            user_actions.append(str(parsed.action))
            query_predictor.observe(parsed)
        targets.extend(user_targets)
        predictions.extend(user_predictions)
        actions.extend(user_actions)
        per_user.append(_per_user_confusion(user_id, user_targets, user_predictions, user_actions))
    extra: dict[str, Any] = {
        "variant": spec.variant,
        "master_seed": int(spec.master_seed),
        "fit_users": int(spec.fit_user_range[1] - spec.fit_user_range[0] + 1),
        "fit_records": len(fit_records),
        "fit_wall_clock_seconds": fit_seconds,
        "predictor_class": f"{predictor_cls.__module__}.{predictor_cls.__name__}",
    }
    if member == "episodic_traversal":
        extra["fallback_rate_in_cell"] = float(fallback_count / max(fallback_total, 1))
        extra["fallback_count"] = int(fallback_count)
        extra["fallback_total"] = int(fallback_total)
    return _score_payload(targets, predictions, actions, per_user, extra=extra)


def _score_payload(
    targets: Sequence[int],
    predictions: Sequence[int],
    actions: Sequence[str],
    per_user: Sequence[Mapping[str, Any]],
    *,
    extra: Mapping[str, Any],
) -> dict[str, Any]:
    overall_metric = macro_balanced_accuracy(targets, predictions, alphabet_size=32)
    recommend_indices = [index for index, action in enumerate(actions) if str(action) == "recommend"]
    recommend_targets = [int(targets[index]) for index in recommend_indices]
    recommend_predictions = [int(predictions[index]) for index in recommend_indices]
    recommend_metric = (
        macro_balanced_accuracy(recommend_targets, recommend_predictions, alphabet_size=32)
        if recommend_indices
        else None
    )
    payload = {
        "n_eval_points": len(targets),
        "classes_present": sorted({int(value) for value in targets}),
        "class_count_present": len({int(value) for value in targets}),
        "metric": float(overall_metric),
        "recommend_turn_conditional_metric": None if recommend_metric is None else float(recommend_metric),
        "recommend_turn_count": len(recommend_indices),
        "per_user_confusion": list(per_user),
        "per_user_confusion_sha256": _sha256_json(per_user),
        "canonical_scorer_id": CANONICAL_SCORER_ID,
        "canonical_scorer_pinned": True,
        "metric_aggregation_rule": "macro-balanced accuracy over classes with >=1 true occurrence in eval slice",
        "recommend_metric_aggregation_rule": "same macro-balanced accuracy restricted to logged action == recommend",
    }
    payload.update(dict(extra))
    return payload


def _canonical_scorer_fixture() -> dict[str, Any]:
    targets = [0, 0, 1, 1, 2, 2]
    predictions = [0, 1, 1, 0, 2, 0]
    actions = ["recommend", "task_topic_0", "recommend", "task_topic_1", "recommend", "task_topic_2"]
    per_user = [_per_user_confusion(999001, targets, predictions, actions)]
    payload = _score_payload(
        targets,
        predictions,
        actions,
        per_user,
        extra={"fixture_id": "canonical_recommend_conditional_metric_fixture_001B"},
    )
    expected_overall = 0.5
    expected_recommend = 1.0
    return {
        "fixture_id": "canonical_recommend_conditional_metric_fixture_001B",
        "targets": targets,
        "predictions": predictions,
        "actions": actions,
        "expected_overall_macro_balanced_accuracy": expected_overall,
        "actual_overall_macro_balanced_accuracy": float(payload["metric"]),
        "expected_recommend_turn_conditional_macro_balanced_accuracy": expected_recommend,
        "actual_recommend_turn_conditional_macro_balanced_accuracy": float(
            payload["recommend_turn_conditional_metric"]
        ),
        "recommend_turn_count": int(payload["recommend_turn_count"]),
        "passed": bool(
            math.isclose(float(payload["metric"]), expected_overall, rel_tol=0.0, abs_tol=1e-12)
            and math.isclose(
                float(payload["recommend_turn_conditional_metric"]),
                expected_recommend,
                rel_tol=0.0,
                abs_tol=1e-12,
            )
            and int(payload["recommend_turn_count"]) == 3
        ),
        "canonical_scorer_id": CANONICAL_SCORER_ID,
        "producer_function": (
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_canonical_scorer_fixture"
        ),
    }


def _validation_events_in_prediction_order(
    events_by_split: Mapping[str, Mapping[int, Sequence[PrefixEvent]]],
    member: str,
) -> list[PrefixEvent]:
    events: list[PrefixEvent] = []
    for user_id in sorted(events_by_split["internal_validation"]):
        user_events = [event_from_mapping(event) for event in events_by_split["internal_validation"][user_id]]
        if member == "seq_window_with_action_conditioning_W15_no_cross_session_persistence":
            active_session: list[PrefixEvent] = []
            for event in user_events:
                if event.session_boundary == "start" and active_session:
                    events.extend(active_session)
                    active_session = []
                active_session.append(event)
            if active_session:
                events.extend(active_session)
        else:
            events.extend(user_events)
    return events


def _confusion_by_user_from_events(events: Sequence[PrefixEvent], predictions: Sequence[int]) -> list[dict[str, Any]]:
    by_user: dict[int, dict[str, list[Any]]] = {}
    # The event payload does not carry user_id; prediction order is sorted by user
    # and each S3d eval user has the frozen 300 turns.  Reconstruct by ordinal.
    if len(events) % 300 != 0:
        raise RuntimeError(f"unexpected_eval_event_count_not_multiple_of_300:{len(events)}")
    for index, (event, pred) in enumerate(zip(events, predictions)):
        user_id = 640 + (index // 300)
        entry = by_user.setdefault(user_id, {"targets": [], "predictions": [], "actions": []})
        entry["targets"].append(int(event.observation["symbol"]))
        entry["predictions"].append(int(pred))
        entry["actions"].append(str(event.action))
    return [
        _per_user_confusion(user_id, entry["targets"], entry["predictions"], entry["actions"])
        for user_id, entry in sorted(by_user.items())
    ]


def _per_user_confusion(user_id: int, targets: Sequence[int], predictions: Sequence[int], actions: Sequence[str]) -> dict[str, Any]:
    totals = [0] * 32
    correct = [0] * 32
    rec_totals = [0] * 32
    rec_correct = [0] * 32
    for target, pred, action in zip(targets, predictions, actions):
        target_i = int(target)
        totals[target_i] += 1
        correct[target_i] += int(int(pred) == target_i)
        if str(action) == "recommend":
            rec_totals[target_i] += 1
            rec_correct[target_i] += int(int(pred) == target_i)
    return {
        "user_id": int(user_id),
        "n": len(targets),
        "totals": totals,
        "correct": correct,
        "recommend_totals": rec_totals,
        "recommend_correct": rec_correct,
    }


def _records_and_style_by_user(design: Mapping[str, Any], trajectory_spec: Any) -> tuple[dict[int, list[PrefixEvent]], dict[int, tuple[int, ...]]]:
    by_user: dict[int, list[PrefixEvent]] = {}
    style_by_user: dict[int, tuple[int, ...]] = {}
    start_user = int(trajectory_spec.partitions["train"]["start_user_id"])
    for _, trajectory_ordinal, record, adjudicator_record in _iter_records_with_adjudicator(design, trajectory_spec):
        user_id = start_user + int(trajectory_ordinal)
        if 800 <= user_id <= 999:
            raise RuntimeError(f"heldout_user_800_999_touched:{user_id}")
        if not 0 <= user_id <= 799:
            raise RuntimeError(f"user_outside_s3d_cert_range:{user_id}")
        by_user.setdefault(user_id, []).append(event_from_mapping(record))
        style = tuple(int(value) for value in adjudicator_record["style_map"])
        if user_id in style_by_user and style_by_user[user_id] != style:
            raise RuntimeError(f"style_map_changed_within_user:{user_id}")
        style_by_user[user_id] = style
    missing = [user_id for user_id in range(0, 800) if user_id not in by_user]
    if missing:
        raise RuntimeError(f"missing_s3d_users:{missing[:5]}")
    return by_user, style_by_user


def _episodic_prediction_would_fallback(predictor: EpisodicTraversalPredictor, action: str) -> bool:
    if not getattr(predictor, "_prefix", None):
        return True
    context = predictor._next_context()
    key = predictor.key_for_prediction(str(action), context, predictor._prefix)
    counts = predictor._table.get(key)
    return counts is None or sum(counts) <= 0.0


def _build_reports(
    *,
    unit_results: Mapping[str, Mapping[str, Any]],
    trace_rows: Sequence[Mapping[str, Any]],
    applied_line: float,
    projection_path: Path,
    runtime_guard: Mapping[str, Any],
    parallelism: Mapping[str, Any],
    serial_assertion: Mapping[str, Any],
    protected_before: Mapping[str, Any],
) -> dict[str, Any]:
    ideal_by_cell = {
        str(result["cell_id"]): result
        for result in unit_results.values()
        if str(result["unit_type"]) == "ideal"
    }
    member_cert = {
        (str(result["member"]), str(result["cell_id"])): result
        for result in unit_results.values()
        if str(result["unit_type"]) == "member" and str(result["phase"]) == "cert"
    }
    member_null = {
        str(result["member"]): result
        for result in unit_results.values()
        if str(result["unit_type"]) == "member" and str(result["phase"]) == "null"
    }
    guard_scope_by_cell: dict[str, str] = {}
    for member_spec in CERT_MEMBER_SPECS:
        cell_id = str(member_spec["cell_id"])
        scope = str(member_spec["metric_scope"])
        existing = guard_scope_by_cell.get(cell_id)
        if existing is not None and existing != scope:
            raise RuntimeError(f"mixed_guard_metric_scopes_for_cell:{cell_id}:{existing}:{scope}")
        guard_scope_by_cell[cell_id] = scope
    cell_guard_by_cell = {
        cell_id: _cell_validity_guard_001b(ideal_by_cell[cell_id], scope)
        for cell_id, scope in sorted(guard_scope_by_cell.items())
    }
    cert_rows = []
    cell_headroom_defects = []
    cert_failures = []
    for member_spec in CERT_MEMBER_SPECS:
        member = str(member_spec["member"])
        cell_id = str(member_spec["cell_id"])
        threshold = float(member_spec["threshold"])
        scope = str(member_spec["metric_scope"])
        result = member_cert[(member, cell_id)]
        ideal = ideal_by_cell[cell_id]
        member_metric = _metric_for_scope(result, scope)
        ideal_metric = _metric_for_scope(ideal, scope)
        ideal_headroom = float(ideal_metric - CHANCE_CELL)
        guard = cell_guard_by_cell[cell_id]
        if not bool(guard["passed"]):
            cell_headroom_defects.append(cell_id)
        rho = (float(member_metric) - CHANCE_CELL) / ideal_headroom if ideal_headroom > 0.0 else math.nan
        ci = _bootstrap_rho_ci(result["per_user_confusion"], ideal["per_user_confusion"], scope, member, cell_id)
        pass_threshold = bool(math.isfinite(rho) and rho >= threshold)
        fallback_rate = result.get("fallback_rate_in_cell")
        fallback_pass = True
        if fallback_rate is not None:
            fallback_pass = bool(float(fallback_rate) < float(member_spec.get("fallback_rate_max", 1.0)))
        passed = bool(pass_threshold and fallback_pass and guard["passed"])
        if not passed:
            cert_failures.append(member)
        cert_rows.append(
            {
                "member": member,
                "cell_id": cell_id,
                "variant": result.get("variant"),
                "metric_scope": scope,
                "metric": float(result["metric"]),
                "recommend_turn_conditional_metric": result.get("recommend_turn_conditional_metric"),
                "metric_used_for_rho": float(member_metric),
                "ideal_cell": float(ideal["metric"]),
                "ideal_recommend_turn_conditional_metric": ideal.get("recommend_turn_conditional_metric"),
                "ideal_metric_used_for_rho": float(ideal_metric),
                "chance_cell": CHANCE_CELL,
                "ideal_headroom": ideal_headroom,
                "cell_validity_guard_basis": "001B: ideal_metric - chance_cell >= k * SE_cell",
                "cell_validity_guard_k": float(guard["k"]),
                "cell_validity_guard_n_cell": int(guard["n_cell"]),
                "cell_validity_guard_SE_cell": float(guard["SE_cell"]),
                "cell_validity_guard_k_times_SE_cell": float(guard["k_times_SE_cell"]),
                "cell_validity_guard_passed": bool(guard["passed"]),
                "cell_validity_guard_computed_from_ideal_only": True,
                "rho": float(rho),
                "rho_threshold": threshold,
                "bootstrap_95_ci_on_rho": ci,
                "n_eval_points": int(result["n_eval_points"]),
                "classes_present": result["classes_present"],
                "class_count_present": int(result["class_count_present"]),
                "fallback_rate_in_cell": fallback_rate,
                "fallback_pass": fallback_pass,
                "passed": passed,
                "unit_id": result["unit_id"],
                "per_user_confusion_sha256": result["per_user_confusion_sha256"],
                "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_build_reports",
            }
        )

    null_rows = []
    null_breaches = []
    null_limit = CHANCE_CELL + NULL_MARGIN
    ideal_null = ideal_by_cell["NULL_env"]
    all_null_results: list[tuple[str, Mapping[str, Any]]] = [("ideal", ideal_null)] + sorted(member_null.items(), key=lambda item: item[0])
    for member, result in all_null_results:
        metric = float(result["metric"])
        passed = bool(metric <= null_limit)
        if not passed:
            null_breaches.append(member)
        null_rows.append(
            {
                "member": member,
                "cell_id": "NULL_env",
                "metric": metric,
                "chance_cell": CHANCE_CELL,
                "null_limit_chance_plus_0_005": null_limit,
                "margin_vs_limit": float(metric - null_limit),
                "n_eval_points": int(result["n_eval_points"]),
                "classes_present": result["classes_present"],
                "class_count_present": int(result["class_count_present"]),
                "passed": passed,
                "unit_id": result["unit_id"],
                "per_user_confusion_sha256": result["per_user_confusion_sha256"],
            }
        )

    graph_family = [row for row in cert_rows if row["member"] in {"successor_map", "transition_table", "count_table", "fsm_planner", "episodic_traversal"}]
    obs_family = [row for row in cert_rows if str(row["member"]).startswith("obs_decoder_")]
    certificate_verdict = (
        "s3d_certificates_green"
        if not cert_failures and not cell_headroom_defects
        else ("s3d_cell_headroom_defect" if cell_headroom_defects else "FAIL_BASELINE_UNDERPOWERED")
    )
    null_verdict = "s3d_null_env_clean" if not null_breaches else "FAIL_NULL_FALSE_HEADROOM"
    if null_breaches:
        final_verdict = {
            "verdict": "FAIL_NULL_FALSE_HEADROOM",
            "stop_condition": "NULL false-headroom breach; all S3d should-win results void under spec §5",
            "s3d_results_void": True,
            "null_breaches": null_breaches,
        }
    elif cell_headroom_defects:
        final_verdict = {
            "verdict": "s3d_cell_headroom_defect",
            "stop_condition": "ideal_cell - chance_cell < k * SE_cell in at least one should-win cell",
            "s3d_results_void": True,
            "cell_headroom_defects": sorted(set(cell_headroom_defects)),
        }
    elif cert_failures:
        final_verdict = {
            "verdict": "FAIL_BASELINE_UNDERPOWERED",
            "stop_condition": "one or more S3d should-win certificate rows failed pre-registered rho/fallback criterion",
            "s3d_results_void": False,
            "certificate_failures": cert_failures,
        }
    elif runtime_guard.get("decision") != "runtime_within_signed_line":
        final_verdict = {
            "verdict": "STOP_runtime_guard_exceeded_signed_line",
            "stop_condition": str(runtime_guard.get("stop_reason")),
            "s3d_results_void": True,
        }
    else:
        final_verdict = {
            "verdict": "s3d_all_certificates_green",
            "stop_condition": None,
            "s3d_results_void": False,
        }

    common = {
        "task_id": TASK_ID,
        "stage": "S3d",
        "applied_cpu_hour_limit": float(applied_line),
        "part0_projection_artifact": str(projection_path.relative_to(ROOT)),
        "trace_artifact": str(TRACE_JSONL.relative_to(ROOT)),
        "runtime_guard": runtime_guard,
        "parallelism": parallelism,
        "serial_equivalence_assertion": serial_assertion,
        "cell_validity_guard": {
            "basis": "001B signed 2a statistical distinguishability guard",
            "k": S3D_001B_GUARD_K,
            "formula": "ideal_metric - chance_cell >= k * sqrt(chance_cell * (1 - chance_cell) / n_cell)",
            "computed_on": "ideal results only",
            "computed_before_member_adjudication_in_build_reports": True,
            "per_cell": cell_guard_by_cell,
        },
        "canonical_scorer_pin": {
            "canonical_scorer_id": CANONICAL_SCORER_ID,
            "fixture": _canonical_scorer_fixture(),
            "reconciliation": CANONICAL_SCORER_RECONCILIATION,
        },
        "run_finished_at": _utc_timestamp(),
        "code_path_hash": _code_path_hash(),
        "claim_ceiling": CLAIM_CEILING,
    }
    certificate_report = {
        **common,
        "artifact": "s3d_certificate_report",
        "verdict": certificate_verdict,
        "rows": cert_rows,
        "obs_decoder_family_max_rho": max((float(row["rho"]) for row in obs_family), default=math.nan),
        "graph_cache_family_max_rho": max((float(row["rho"]) for row in graph_family), default=math.nan),
        "cell_headroom_defects": sorted(set(cell_headroom_defects)),
        "failed_members": cert_failures,
        "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_build_reports/certificate",
    }
    null_report = {
        **common,
        "artifact": "s3d_null_env_report",
        "verdict": null_verdict,
        "null_limit": null_limit,
        "rows": null_rows,
        "breaches": null_breaches,
        "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_build_reports/null",
    }
    baseline_comparison = {
        **common,
        "artifact": "baseline_comparison",
        "verdict": final_verdict["verdict"],
        "chance_cell": CHANCE_CELL,
        "ideal_anchors": {
            cell_id: {
                "metric": float(result["metric"]),
                "recommend_turn_conditional_metric": result.get("recommend_turn_conditional_metric"),
                "ideal_headroom": float(result["metric"]) - CHANCE_CELL,
                "unit_id": result["unit_id"],
            }
            for cell_id, result in sorted(ideal_by_cell.items())
        },
        "certificate_rows": cert_rows,
        "null_rows": null_rows,
        "cert_failures": cert_failures,
        "null_breaches": null_breaches,
        "comparison_scope": "should-win favorable-cell member-vs-ideal rho plus NULL-env chance+0.005 control",
        "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_build_reports/baseline",
    }
    replay_report = _build_replay_report(certificate_report, null_report, final_verdict, trace_rows)
    return {
        "certificate_report": certificate_report,
        "null_env_report": null_report,
        "baseline_comparison": baseline_comparison,
        "replay_report": replay_report,
        "final_verdict": final_verdict,
    }


def _metric_for_scope(result: Mapping[str, Any], scope: str) -> float:
    if scope == "overall":
        return float(result["metric"])
    if scope == "recommend":
        value = result.get("recommend_turn_conditional_metric")
        if value is None:
            raise RuntimeError(f"recommend_metric_missing:{result.get('unit_id')}")
        return float(value)
    raise ValueError(f"unknown metric scope: {scope}")


def _n_cell_for_scope(result: Mapping[str, Any], scope: str) -> int:
    if scope == "overall":
        return int(result["n_eval_points"])
    if scope == "recommend":
        return int(result["recommend_turn_count"])
    raise ValueError(f"unknown metric scope: {scope}")


def _cell_validity_guard_001b(ideal_result: Mapping[str, Any], scope: str) -> dict[str, Any]:
    ideal_metric = _metric_for_scope(ideal_result, scope)
    n_cell = _n_cell_for_scope(ideal_result, scope)
    if n_cell <= 0:
        se_cell = math.inf
    else:
        se_cell = math.sqrt(CHANCE_CELL * (1.0 - CHANCE_CELL) / float(n_cell))
    k_times_se = S3D_001B_GUARD_K * se_cell
    ideal_headroom = float(ideal_metric - CHANCE_CELL)
    return {
        "cell_id": str(ideal_result["cell_id"]),
        "metric_scope": scope,
        "ideal_metric": float(ideal_metric),
        "chance_cell": float(CHANCE_CELL),
        "ideal_minus_chance": ideal_headroom,
        "n_cell": int(n_cell),
        "SE_cell": float(se_cell),
        "k": float(S3D_001B_GUARD_K),
        "k_times_SE_cell": float(k_times_se),
        "passed": bool(n_cell > 0 and ideal_headroom >= k_times_se),
        "producer_function": (
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_cell_validity_guard_001b"
        ),
    }


def _bootstrap_rho_ci(
    member_per_user: Sequence[Mapping[str, Any]],
    ideal_per_user: Sequence[Mapping[str, Any]],
    scope: str,
    member: str,
    cell_id: str,
) -> list[float]:
    if len(member_per_user) != len(ideal_per_user):
        raise RuntimeError(f"bootstrap_user_count_mismatch:{member}:{cell_id}")
    rng = np.random.default_rng(_seed_from_text(f"bootstrap:{member}:{cell_id}:{scope}"))
    values: list[float] = []
    n = len(member_per_user)
    for _ in range(1000):
        indices = rng.integers(0, n, size=n)
        m_metric = _metric_from_resampled_users(member_per_user, indices, scope)
        i_metric = _metric_from_resampled_users(ideal_per_user, indices, scope)
        denom = i_metric - CHANCE_CELL
        values.append(float((m_metric - CHANCE_CELL) / denom) if denom > 0 else math.nan)
    finite = [value for value in values if math.isfinite(value)]
    if not finite:
        return [math.nan, math.nan]
    return [float(np.percentile(finite, 2.5)), float(np.percentile(finite, 97.5))]


def _metric_from_resampled_users(per_user: Sequence[Mapping[str, Any]], indices: Sequence[int], scope: str) -> float:
    total_key = "totals" if scope == "overall" else "recommend_totals"
    correct_key = "correct" if scope == "overall" else "recommend_correct"
    totals = np.zeros(32, dtype=np.int64)
    correct = np.zeros(32, dtype=np.int64)
    for index in indices:
        item = per_user[int(index)]
        totals += np.asarray(item[total_key], dtype=np.int64)
        correct += np.asarray(item[correct_key], dtype=np.int64)
    present = totals > 0
    if not bool(np.any(present)):
        return 0.0
    return float(np.mean(correct[present] / totals[present]))


def _build_replay_report(
    certificate_report: Mapping[str, Any],
    null_report: Mapping[str, Any],
    final_verdict: Mapping[str, Any],
    trace_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    cert_failures = [
        str(row["member"])
        for row in certificate_report["rows"]
        if not bool(row["passed"])
    ]
    null_breaches = [
        str(row["member"])
        for row in null_report["rows"]
        if not bool(row["passed"])
    ]
    if null_breaches:
        replay_verdict = "FAIL_NULL_FALSE_HEADROOM"
    elif any(not bool(row["cell_validity_guard_passed"]) for row in certificate_report["rows"]):
        replay_verdict = "s3d_cell_headroom_defect"
    elif cert_failures:
        replay_verdict = "FAIL_BASELINE_UNDERPOWERED"
    else:
        replay_verdict = "s3d_all_certificates_green"
    trace_unit_ids = sorted(str(row["unit_id"]) for row in trace_rows)
    report_unit_ids = sorted(
        [str(row["unit_id"]) for row in certificate_report["rows"]]
        + [str(row["unit_id"]) for row in null_report["rows"]]
        + [str(certificate_report["runtime_guard"].get("trace_path", ""))]
    )
    return {
        "task_id": TASK_ID,
        "stage": "S3d",
        "artifact": "replay_report",
        "replay_scope": "verdict reconstruction from recorded trace/report metrics and thresholds; no hidden future observations",
        "recomputed_verdict": replay_verdict,
        "original_verdict": final_verdict["verdict"],
        "verdict_match": replay_verdict == final_verdict["verdict"],
        "certificate_failures_recomputed": cert_failures,
        "null_breaches_recomputed": null_breaches,
        "trace_unit_count": len(trace_rows),
        "trace_unit_ids_sha256": _sha256_json(trace_unit_ids),
        "report_unit_ids_sha256": _sha256_json(report_unit_ids),
        "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_build_replay_report",
        "input_artifacts": [
            str(TRACE_JSONL.relative_to(ROOT)),
            str(CERTIFICATE_REPORT.relative_to(ROOT)),
            str(NULL_ENV_REPORT.relative_to(ROOT)),
        ],
        "run_started_at": _utc_timestamp(),
        "run_finished_at": _utc_timestamp(),
        "code_path_hash": _code_path_hash(),
        "claim_ceiling": CLAIM_CEILING,
    }


def _serial_equivalence_assertion(unit_results: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    sample_payload = {
        "unit_type": "member",
        "phase": "cert",
        "cell_id": "constant_none",
        "member": "predict_none",
        "unit_id": "member::cert::predict_none::constant_none",
    }
    unit_id = sample_payload["unit_id"]
    parallel_result = unit_results[unit_id]
    serial_result = _run_unit_worker(sample_payload)
    metric_equal = float(parallel_result["metric"]) == float(serial_result["metric"])
    digest_equal = str(parallel_result["metric_digest"]) == str(serial_result["metric_digest"])
    return {
        "sample_unit_id": unit_id,
        "serial_recompute_metric": float(serial_result["metric"]),
        "parallel_metric": float(parallel_result["metric"]),
        "metric_full_precision_equal": bool(metric_equal),
        "metric_digest_equal": bool(digest_equal),
        "passed": bool(metric_equal and digest_equal),
        "serial_wall_clock_seconds": float(serial_result["wall_clock_seconds"]),
        "serial_process_cpu_seconds": float(serial_result["process_cpu_seconds"]),
        "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_serial_equivalence_assertion",
    }


def _trace_row_from_unit(result: Mapping[str, Any], cumulative_cpu_hours: float) -> dict[str, Any]:
    return {
        "unit_id": str(result["unit_id"]),
        "unit_type": str(result["unit_type"]),
        "phase": str(result["phase"]),
        "member": str(result["member"]),
        "cell_id": str(result["cell_id"]),
        "metric": float(result["metric"]),
        "recommend_turn_conditional_metric": result.get("recommend_turn_conditional_metric"),
        "n_eval_points": int(result["n_eval_points"]),
        "wall_clock_seconds": float(result["wall_clock_seconds"]),
        "process_cpu_seconds": float(result["process_cpu_seconds"]),
        "wall_cpu_ratio": float(result["wall_cpu_ratio"]),
        "wall_cpu_ratio_flag_gt_1_25": bool(result["wall_cpu_ratio_flag_gt_1_25"]),
        "cumulative_contention_robust_cpu_hours": float(cumulative_cpu_hours),
        "run_started_at": str(result["run_started_at"]),
        "run_finished_at": str(result["run_finished_at"]),
        "heldout_users_800_999_touched": bool(result["heldout_users_800_999_touched"]),
        "future_observations_used": bool(result["future_observations_used"]),
        "metric_digest": str(result["metric_digest"]),
        "per_user_confusion": result["per_user_confusion"],
    }


def _append_trace_jsonl(path: Path, row: Mapping[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_jsonable(row), sort_keys=True) + "\n")


def _write_trace_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(_jsonable(row), sort_keys=True) + "\n")


def _write_trace_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    fields = [
        "unit_id",
        "unit_type",
        "phase",
        "member",
        "cell_id",
        "metric",
        "recommend_turn_conditional_metric",
        "n_eval_points",
        "wall_clock_seconds",
        "process_cpu_seconds",
        "wall_cpu_ratio",
        "wall_cpu_ratio_flag_gt_1_25",
        "cumulative_contention_robust_cpu_hours",
        "run_started_at",
        "run_finished_at",
        "heldout_users_800_999_touched",
        "future_observations_used",
        "metric_digest",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def _load_original_part0_runner() -> Any:
    spec = importlib.util.spec_from_file_location("s3d_part0_projection_runner_readonly", ORIGINAL_PART0_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load original runner: {ORIGINAL_PART0_RUNNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _selected_recipe_configs() -> dict[str, Mapping[str, Any]]:
    return {
        member: _read_json(ARTIFACT_ROOT / "s3c_models" / filename)["selected_config"]["config"]
        for member, filename in SELECTED_RECIPE_BY_MEMBER.items()
    }


def _selected_recipe_paths() -> dict[str, Path]:
    return {member: ARTIFACT_ROOT / "s3c_models" / filename for member, filename in SELECTED_RECIPE_BY_MEMBER.items()}


def _single_thread_environment() -> dict[str, Any]:
    for key in THREAD_ENV_KEYS:
        os.environ[key] = "1"
    payload: dict[str, Any] = {
        "single_thread_accounting": True,
        "env_threads": {key: os.environ.get(key, "") for key in THREAD_ENV_KEYS},
        "torch_device": "not_imported",
    }
    try:
        import torch

        torch.set_num_threads(1)
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass
        payload["torch_num_threads"] = int(torch.get_num_threads())
        payload["torch_num_interop_threads"] = int(torch.get_num_interop_threads())
        payload["torch_device"] = str(torch.device("cpu"))
    except Exception as exc:  # pragma: no cover
        payload["torch_error"] = f"{type(exc).__name__}: {exc}"
    return payload


def _configure_worker_environment() -> None:
    for key in THREAD_ENV_KEYS:
        os.environ[key] = "1"
    try:
        from threadpoolctl import threadpool_limits

        threadpool_limits(limits=1)
    except Exception:
        pass
    try:
        import torch

        torch.set_num_threads(1)
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass
        if str(torch.device("cpu")) != "cpu":
            raise RuntimeError("torch_device_not_cpu")
    except ImportError:
        pass


def _physical_core_count() -> dict[str, Any]:
    logical = os.cpu_count() or 1
    method = "fallback_logical_div_2"
    physical = max(1, logical // 2)
    if os.name == "nt":
        try:
            output = subprocess.check_output(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfCores -Sum).Sum",
                ],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=20,
            ).strip()
            parsed = int(float(output))
            if parsed > 0:
                physical = parsed
                method = "Win32_Processor.NumberOfCores"
        except Exception as exc:  # pragma: no cover
            method = f"fallback_after_{type(exc).__name__}"
    return {"physical_cores": int(physical), "logical_cores": int(logical), "detection_method": method}


def _failure_manifest_payload(
    *,
    verdict: str,
    stop_condition: str,
    details: Mapping[str, Any],
    protected_before: Mapping[str, Any],
) -> dict[str, Any]:
    protected_after = _protected_artifact_hashes()
    return {
        "task_id": TASK_ID,
        "task_card_id": TASK_CARD_ID,
        "stage": "S3d",
        "artifact": "failure_manifest",
        "verdict": verdict,
        "stop_condition": stop_condition,
        "details": details,
        "preserved_failure": True,
        "s3d_results_void": verdict in {"FAIL_NULL_FALSE_HEADROOM", "STOP_PRECONDITION_UNMET", "s3d_cell_headroom_defect", "STOP_runtime_guard_exceeded_signed_line", "STOP_UNEXPECTED_EXCEPTION"},
        "protected_artifacts_before": protected_before,
        "protected_artifacts_after": protected_after,
        "banked_stop_probe_artifacts_byte_unchanged": _protected_hash_match(protected_before, protected_after),
        "claim_ceiling": "S3d STOP/failure boundary only; no environment-validity, gap, mechanism, learning, agency, EGO, or companion claim",
        "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_failure_manifest_payload",
        "code_path_hash": _code_path_hash(),
        "run_started_at": _utc_timestamp(),
        "run_finished_at": _utc_timestamp(),
    }


def _finalize_result_payload(payload: Mapping[str, Any], perf_start: float, cpu_start: float) -> dict[str, Any]:
    final = dict(payload)
    final["run_finished_at"] = _utc_timestamp()
    final["run_wall_clock_seconds"] = time.perf_counter() - perf_start
    final["run_process_cpu_seconds"] = time.process_time() - cpu_start
    final["producer_function"] = "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_finalize_result_payload"
    final["code_path_hash"] = _code_path_hash()
    final["claim_ceiling"] = CLAIM_CEILING
    return final


def _write_precondition_stop_artifacts(precondition: Mapping[str, Any], manifest: Mapping[str, Any]) -> list[str]:
    run_started_at = _utc_timestamp()
    common = {
        "task_id": TASK_ID,
        "task_card_id": TASK_CARD_ID,
        "stage": "S3d",
        "verdict": "STOP_PRECONDITION_UNMET",
        "stop_condition": manifest["stop_condition"],
        "s3d_results_void": True,
        "precondition": precondition,
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "producer_function": (
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py"
            "::_write_precondition_stop_artifacts"
        ),
        "code_path_hash": _code_path_hash(),
        "claim_ceiling": "precondition STOP evidence only; no S3d certificate, NULL-env, gap, mechanism, learning, agency, or EGO claim",
    }
    certificate_report = {
        **common,
        "artifact": "s3d_certificate_report",
        "rows": [],
        "not_run_reason": "precondition failed before PART-0 re-gate; no member or ideal cert cell was scored",
    }
    null_report = {
        **common,
        "artifact": "s3d_null_env_report",
        "rows": [],
        "breaches": [],
        "not_run_reason": "precondition failed before PART-0 re-gate; NULL-env was not scored",
    }
    baseline_report = {
        **common,
        "artifact": "baseline_comparison",
        "comparison_scope": "not run",
        "not_run_reason": "precondition failed before PART-0 re-gate",
    }
    ablation_report = {
        **common,
        "artifact": "ablation_report",
        "not_run_reason": "precondition failed before PART-0 re-gate; BASE-invariance and cert-only ablation were not rerun",
    }
    replay_report = {
        **common,
        "artifact": "replay_report",
        "replay_scope": "not run",
        "verdict_match": True,
        "not_run_reason": "precondition failed before PART-0 re-gate; no scored trace exists to replay",
    }
    trace_row = {
        **common,
        "artifact": "trace",
        "event_type": "precondition_stop",
        "unit_id": "precondition::STOP_PRECONDITION_UNMET",
        "unit_type": "precondition",
        "phase": "preflight",
        "member": "none",
        "cell_id": "none",
        "metric": None,
        "n_eval_points": 0,
        "heldout_users_800_999_touched": False,
        "future_observations_used": False,
    }
    _write_json(CERTIFICATE_REPORT, certificate_report)
    _write_json(NULL_ENV_REPORT, null_report)
    _write_json(BASELINE_COMPARISON, baseline_report)
    _write_json(ABLATION_REPORT, ablation_report)
    _write_json(REPLAY_REPORT, replay_report)
    with TRACE_JSONL.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(_jsonable(trace_row), sort_keys=True) + "\n")
    with TRACE_CSV.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "event_type",
            "unit_id",
            "unit_type",
            "phase",
            "member",
            "cell_id",
            "verdict",
            "stop_condition",
            "n_eval_points",
            "heldout_users_800_999_touched",
            "future_observations_used",
            "run_started_at",
            "run_finished_at",
            "producer_function",
            "code_path_hash",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow({field: trace_row.get(field) for field in fields})
    candidate_paths = [
        Path(__file__),
        RESULT,
        FAILURE_MANIFEST,
        ARTIFACT_ROOT / "s3d_battery_precondition_failure_manifest.json",
        TRACE_JSONL,
        TRACE_CSV,
        CERTIFICATE_REPORT,
        NULL_ENV_REPORT,
        BASELINE_COMPARISON,
        ABLATION_REPORT,
        REPLAY_REPORT,
        ARTIFACT_ROOT / "result_pre_ideal_repair_failure_v1.json",
        ARTIFACT_ROOT / "failure_manifest_pre_ideal_repair_failure_v1.json",
        ARTIFACT_ROOT / "trace_pre_ideal_repair_failure_v1.jsonl",
        ARTIFACT_ROOT / "trace_pre_ideal_repair_failure_v1.csv",
        ARTIFACT_ROOT / "s3d_compute_projection_line30.0_pre_ideal_repair_failure_v1.json",
        ARTIFACT_ROOT / "s3d_freshness_manifest_pre_ideal_repair_failure_v1.json",
    ]
    return [str(path.relative_to(ROOT)).replace("\\", "/") for path in candidate_paths if path.exists()]


def _write_operator_bank_ops(result_payload: Mapping[str, Any]) -> None:
    bank_ops = ARTIFACT_ROOT / "s3d_operator_bank_ops_proposal_line30.ps1"
    head_pin = result_payload.get("precondition", {}).get("git_readback_without_git_command", {}).get("head_hash", "UNKNOWN_HEAD_NO_GIT_COMMAND_USED")
    allowlist = list(result_payload.get("new_artifacts") or _expected_new_artifact_paths(include_failure=FAILURE_MANIFEST.exists()))
    allowlist.append(str(bank_ops.relative_to(ROOT)).replace("\\", "/"))
    rendered = "\n".join(f"  '{item}'" for item in allowlist)
    script = f"""# Proposed operator-only bank ops for {TASK_CARD_ID}
# Codex generated this script but did not run it. No push is performed.
$ErrorActionPreference = 'Stop'
$ExpectedHead = '{head_pin}'
$CommitMessage = 'bank {TASK_CARD_ID} line30 battery artifacts'
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

Write-Host 'Banked scoped S3d line30 battery artifacts locally. No push was performed.'
"""
    bank_ops.write_text(script, encoding="utf-8")


def _expected_new_artifact_paths(*, include_failure: bool) -> list[str]:
    paths = [
        f"artifacts/{TASK_ID}/s3d_battery_runner_line30.py",
        f"artifacts/{TASK_ID}/s3d_compute_projection_line30.0.json",
        f"artifacts/{TASK_ID}/s3d_cert_sets_manifest.json",
        f"artifacts/{TASK_ID}/s3d_certificate_report.json",
        f"artifacts/{TASK_ID}/s3d_null_env_report.json",
        f"artifacts/{TASK_ID}/result.json",
        f"artifacts/{TASK_ID}/trace.jsonl",
        f"artifacts/{TASK_ID}/trace.csv",
        f"artifacts/{TASK_ID}/baseline_comparison.json",
        f"artifacts/{TASK_ID}/ablation_report.json",
        f"artifacts/{TASK_ID}/replay_report.json",
    ]
    if include_failure:
        paths.append(f"artifacts/{TASK_ID}/failure_manifest.json")
    return paths


def _protected_artifact_hashes() -> dict[str, Any]:
    return {
        str(path.relative_to(ROOT)).replace("\\", "/"): {
            "exists": path.exists(),
            "sha256": _sha256(path) if path.exists() else None,
            "size_bytes": path.stat().st_size if path.exists() else None,
        }
        for path in PROTECTED_BANKED_ARTIFACTS
    }


def _protected_hash_match(before: Mapping[str, Any], after: Mapping[str, Any]) -> bool:
    return json.dumps(before, sort_keys=True) == json.dumps(after, sort_keys=True)


def _artifact_ref(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "exists": path.exists(),
        "sha256": _sha256(path) if path.exists() else None,
        "size_bytes": path.stat().st_size if path.exists() else None,
    }


def _metric_digest(payload: Mapping[str, Any]) -> str:
    material = {
        "metric": payload.get("metric"),
        "recommend_turn_conditional_metric": payload.get("recommend_turn_conditional_metric"),
        "per_user_confusion_sha256": payload.get("per_user_confusion_sha256"),
        "n_eval_points": payload.get("n_eval_points"),
        "classes_present": payload.get("classes_present"),
    }
    return _sha256_json(material)


def _seed_from_text(text: str) -> int:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


def _line_label(value: float) -> str:
    text = f"{float(value):.1f}"
    return text


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(_jsonable(payload), indent=2, sort_keys=True)
    target.write_text(text, encoding="utf-8")
    raw = target.read_bytes()
    if not raw:
        raise AssertionError(f"empty_json_write:{target}")
    if b"\x00" in raw:
        raise AssertionError(f"nul_byte_after_json_write:{target}")
    if raw[-1:] in b" \t\r\n":
        raise AssertionError(f"trailing_whitespace_after_json_write:{target}")
    json.loads(raw.decode("utf-8-sig"))


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
    return hashlib.sha256(json.dumps(_jsonable(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _code_path_hash() -> str:
    h = hashlib.sha256()
    for path in _code_paths():
        h.update(str(path.relative_to(ROOT)).replace("\\", "/").encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _code_paths() -> list[Path]:
    return [
        Path(__file__),
        ROOT / "src" / "fsp_pum_env" / "s3d_certificates.py",
        ROOT / "src" / "fsp_pum_env" / "trajectory_sets.py",
        ROOT / "src" / "fsp_pum_env" / "simulator.py",
        ROOT / "src" / "fsp_pum_env" / "factored_filter.py",
        ROOT / "src" / "fsp_pum_env" / "ideal_observer.py",
        ROOT / "src" / "fsp_pum_env" / "battery" / "base.py",
        ROOT / "src" / "fsp_pum_env" / "battery" / "obs_decoders.py",
        ROOT / "src" / "fsp_pum_env" / "battery" / "seq_models.py",
        ROOT / "src" / "fsp_pum_env" / "battery" / "graph_cache.py",
        ROOT / "src" / "fsp_pum_env" / "battery" / "rag_nn.py",
        ROOT / "src" / "fsp_pum_env" / "battery" / "degenerates.py",
        ROOT / "src" / "fsp_pum_env" / "battery" / "ls_regressors.py",
    ]


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def main() -> int:
    payload = run()
    print(
        json.dumps(
            {
                "result_path": str(RESULT.relative_to(ROOT)),
                "verdict": payload.get("verdict"),
                "applied_cpu_hour_limit": payload.get("applied_cpu_hour_limit"),
                "claim_ceiling": payload.get("claim_ceiling"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
