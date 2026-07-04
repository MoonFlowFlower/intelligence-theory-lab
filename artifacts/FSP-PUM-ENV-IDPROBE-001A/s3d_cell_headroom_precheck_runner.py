"""S3d should-win cell-headroom precheck for FSP-PUM-ENV-IDPROBE-001A.

This diagnostic reuses the banked line30 battery runner's ideal scoring path
(`_score_ideal_cell`) and cert metric helpers.  It runs only the ideal observer
on the preregistered 15-user fractional-index sample for each should-win cell.

Claim ceiling: multi-user estimate of the S3d spec's 0.10 cell-headroom guard
only; not a formal 160-user certificate, NULL-env result, gap, mechanism,
learning, agency, or EGO claim.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import replace
import hashlib
import importlib.util
import inspect
import json
import math
import os
from pathlib import Path
import sys
import time
import traceback
from typing import Any, Iterator, Mapping, Sequence

import numpy as np


THREAD_ENV_KEYS = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS")
for _KEY in THREAD_ENV_KEYS:
    os.environ[_KEY] = "1"


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.fsp_pum_env.s3d_certificates import build_s3d_cert_set_specs
from src.fsp_pum_env.simulator import FspPumSimulator
from src.fsp_pum_env.trajectory_sets import TrajectorySetSpec, load_frozen_design


TASK_ID = "FSP-PUM-ENV-IDPROBE-001A"
TASK_CARD_ID = "FSP-PUM-ENV-IDPROBE-001A-S3D-CELL-HEADROOM-PRECHECK-001A"
ARTIFACT_ROOT = ROOT / "artifacts" / TASK_ID
FROZEN_DESIGN = ARTIFACT_ROOT / "frozen_design.json"
BANKED_RUNNER = ARTIFACT_ROOT / "s3d_battery_runner_line30.py"
TASK_CARD = ROOT / "docs" / "codex" / "tasks" / f"{TASK_CARD_ID}.md"
SPEC_CARD = ROOT / "docs" / "codex" / "tasks" / "FSP-PUM-ENV-IDPROBE-001A-S3D-SHOULD-WIN-NULL-ENV-SPEC-001A.md"
RESULT = ARTIFACT_ROOT / "s3d_cell_headroom_precheck.json"
TRACE = ARTIFACT_ROOT / "s3d_cell_headroom_precheck_trace.jsonl"
FAILURE_MANIFEST = ARTIFACT_ROOT / "s3d_cell_headroom_precheck_failure_manifest.json"
CLAIM_CEILING_PATH = ARTIFACT_ROOT / "s3d_cell_headroom_precheck_claim_ceiling.txt"

SHOULD_WIN_CELLS = (
    "constant_none",
    "constant_saturated",
    "camouflage_off",
    "low_diversity",
    "stable_facts",
    "flat_theta",
)
CELL_NAME_FROM_SPEC = {
    "constant_none": "degenerate_should_win_constant_none",
    "constant_saturated": "degenerate_should_win_constant_saturated",
    "camouflage_off": "camouflage_off",
    "low_diversity": "graph_cache_should_win_low_diversity_templates",
    "stable_facts": "rag_should_win_stable_facts",
    "flat_theta": "flat_theta",
}
METRIC_SCOPE_BY_CELL = {
    "constant_none": "overall",
    "constant_saturated": "overall",
    "camouflage_off": "overall",
    "low_diversity": "overall",
    "stable_facts": "recommend",
    "flat_theta": "overall",
}
GUARD_THRESHOLD = 0.10
K_USERS = 15
CLAIM_CEILING = (
    "按 S3d spec 0.10 guard 的多用户 cell-headroom 估计 only; "
    "not the formal 160-user cert-set adjudication; no cert/gap/mechanism/learning/agency/EGO claim"
)


def main() -> int:
    run_started_at = _utc_timestamp()
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    TRACE.write_text("", encoding="utf-8")
    CLAIM_CEILING_PATH.write_text(CLAIM_CEILING + "\n", encoding="utf-8")

    try:
        runner = _load_banked_runner()
        design = load_frozen_design(FROZEN_DESIGN)
        specs = {spec.cell_id: spec for spec in build_s3d_cert_set_specs(design)}
        missing = [cell for cell in SHOULD_WIN_CELLS if cell not in specs]
        if missing:
            raise RuntimeError(f"missing_should_win_specs:{missing}")
        if "NULL_env" in SHOULD_WIN_CELLS:
            raise RuntimeError("NULL_env_included_in_should_win_cells")

        environment = _single_thread_environment(runner)
        runner_sha256 = _sha256(BANKED_RUNNER)
        script_sha256 = _sha256(Path(__file__))
        filter_source_support = _filter_source_support(runner)
        run_id = f"{TASK_CARD_ID}-{run_started_at}"
        cell_rows: list[dict[str, Any]] = []
        total_scoring_cpu_seconds = 0.0
        total_mode_cpu_seconds = 0.0

        _trace(
            {
                "event": "run_start",
                "run_id": run_id,
                "task_id": TASK_ID,
                "task_card_id": TASK_CARD_ID,
                "run_started_at": run_started_at,
                "runner_sha256": runner_sha256,
                "script_sha256": script_sha256,
                "single_thread_environment": environment,
                "should_win_cells": list(SHOULD_WIN_CELLS),
                "null_env_excluded": True,
                "producer_function": "s3d_cell_headroom_precheck_runner.py::main",
            }
        )

        for cell_id in SHOULD_WIN_CELLS:
            spec = specs[cell_id]
            metric_scope = METRIC_SCOPE_BY_CELL[cell_id]
            selected = _select_fractional_eval_users(spec.eval_user_range, k=K_USERS)
            if any(800 <= user_id <= 999 for user_id in selected["resolved_user_ids"]):
                raise RuntimeError(f"heldout_user_selection:{cell_id}:{selected['resolved_user_ids']}")

            per_user_confusions: list[dict[str, Any]] = []
            per_user_scores: list[dict[str, Any]] = []
            mode_evidence_users: list[dict[str, Any]] = []
            for user_id in selected["resolved_user_ids"]:
                user_score, score_cpu = _score_selected_user_via_banked_ideal(
                    runner,
                    design,
                    spec,
                    user_id=int(user_id),
                )
                total_scoring_cpu_seconds += score_cpu
                per_user_confusions.extend(user_score["per_user_confusion"])
                per_user_scores.append(
                    {
                        "user_id": int(user_id),
                        "metric": float(user_score["metric"]),
                        "recommend_turn_conditional_metric": user_score.get("recommend_turn_conditional_metric"),
                        "n_eval_points": int(user_score["n_eval_points"]),
                        "classes_present": user_score["classes_present"],
                        "class_count_present": int(user_score["class_count_present"]),
                        "metric_digest": runner._metric_digest(user_score),
                        "process_cpu_seconds": float(score_cpu),
                    }
                )
                mode_evidence, mode_cpu = _argmax_vs_mode_evidence_for_user(
                    runner,
                    design,
                    spec,
                    user_id=int(user_id),
                    metric_scope=metric_scope,
                )
                total_mode_cpu_seconds += mode_cpu
                mode_evidence_users.append(mode_evidence)

            metric = runner._metric_from_resampled_users(
                per_user_confusions,
                list(range(len(per_user_confusions))),
                metric_scope,
            )
            overall_metric = runner._metric_from_resampled_users(
                per_user_confusions,
                list(range(len(per_user_confusions))),
                "overall",
            )
            recommend_metric = None
            if _scope_total_count(per_user_confusions, "recommend") > 0:
                recommend_metric = runner._metric_from_resampled_users(
                    per_user_confusions,
                    list(range(len(per_user_confusions))),
                    "recommend",
                )

            scoped_targets = _scope_targets_from_mode_evidence(mode_evidence_users, metric_scope)
            scoped_modes = _scope_modes_from_mode_evidence(mode_evidence_users, metric_scope)
            scoped_predictions = _scope_predictions_from_mode_evidence(mode_evidence_users, metric_scope)
            mode_metric = runner.macro_balanced_accuracy(scoped_targets, scoped_modes, alphabet_size=32)
            ideal_argmax_metric = runner.macro_balanced_accuracy(scoped_targets, scoped_predictions, alphabet_size=32)
            if not math.isclose(float(metric), float(ideal_argmax_metric), rel_tol=0.0, abs_tol=1e-12):
                raise RuntimeError(
                    f"pooled_metric_mismatch:{cell_id}:{metric}:{ideal_argmax_metric}; "
                    "banked per-user confusion and mode-evidence predictions diverged"
                )

            chance = float(runner.CHANCE_CELL)
            headroom = float(metric - chance)
            mode_headroom = float(mode_metric - chance)
            mode_summary = _summarize_mode_evidence(
                mode_evidence_users,
                metric_scope=metric_scope,
                mode_metric=mode_metric,
                mode_headroom=mode_headroom,
            )
            metric_artifact = _metric_artifact_check(
                class_count_present=int(mode_summary["target_distinct_class_count"]),
                metric_aggregation_rule="classes_with_at_least_one_true_occurrence",
                ideal_metric=float(metric),
                mode_metric=float(mode_metric),
                chance=float(chance),
            )
            verdict, reason = _cell_verdict(
                cell_id=cell_id,
                headroom=headroom,
                mode_headroom=mode_headroom,
                mode_agreement=float(mode_summary["ideal_argmax_vs_mode_agreement"]),
                filter_source_support=filter_source_support[cell_id],
                metric_artifact=metric_artifact,
            )
            row = {
                "cell_id": cell_id,
                "spec_cell_name": CELL_NAME_FROM_SPEC[cell_id],
                "variant": spec.variant,
                "master_seed": int(spec.master_seed),
                "metric_scope": metric_scope,
                "ideal_metric": float(metric),
                "overall_metric": float(overall_metric),
                "recommend_turn_conditional_metric": None if recommend_metric is None else float(recommend_metric),
                "chance_cell": chance,
                "headroom": headroom,
                "guard_threshold": GUARD_THRESHOLD,
                "guard_passed": bool(headroom >= GUARD_THRESHOLD),
                "verdict": verdict,
                "verdict_reason": reason,
                "mode_oracle_metric_same_scope": float(mode_metric),
                "mode_oracle_headroom_same_scope": mode_headroom,
                "filter_source_support_evidence": filter_source_support[cell_id],
                "metric_artifact_evidence": metric_artifact,
                "argmax_vs_mode_evidence": mode_summary,
                "resolved_eval_user_selection": selected,
                "resolved_user_ids": selected["resolved_user_ids"],
                "heldout_users_800_999_touched": False,
                "n_eval_users": len(selected["resolved_user_ids"]),
                "n_eval_points_scope": int(mode_summary["scope_turn_count"]),
                "n_eval_points_overall": int(_scope_total_count(per_user_confusions, "overall")),
                "target_distinct_class_count_scope": int(mode_summary["target_distinct_class_count"]),
                "target_classes_scope": mode_summary["target_classes"],
                "per_user_scores": per_user_scores,
                "per_user_confusion_sha256": _sha256_json(per_user_confusions),
                "producer_function": "s3d_cell_headroom_precheck_runner.py::main/_score_selected_user_via_banked_ideal",
                "reused_banked_producer_function": (
                    "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_score_ideal_cell"
                ),
                "metric_producer_functions": [
                    "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_metric_from_resampled_users",
                    "src.fsp_pum_env.s3d_certificates.macro_balanced_accuracy",
                ],
                "aggregation_rule": (
                    "macro-balanced accuracy over classes with >=1 true occurrence in eval slice"
                    if metric_scope == "overall"
                    else "same macro-balanced accuracy restricted to logged action == recommend"
                ),
                "input_artifacts": _input_artifacts(),
                "run_id": run_id,
                "seed_context_episode_ids": {
                    "cell_id": cell_id,
                    "master_seed": int(spec.master_seed),
                    "eval_user_ids": selected["resolved_user_ids"],
                    "trajectory_set_id": spec.trajectory_spec.set_id,
                    "turns_per_user": int(spec.trajectory_spec.turns_per_user),
                },
                "code_path_hash": _combined_code_path_hash(runner, script_sha256),
            }
            cell_rows.append(row)
            _trace(
                {
                    "event": "cell_scored",
                    "run_id": run_id,
                    "cell_id": cell_id,
                    "metric_scope": metric_scope,
                    "resolved_user_ids": selected["resolved_user_ids"],
                    "ideal_metric": float(metric),
                    "chance_cell": chance,
                    "headroom": headroom,
                    "guard_threshold": GUARD_THRESHOLD,
                    "verdict": verdict,
                    "argmax_vs_mode_agreement": mode_summary["ideal_argmax_vs_mode_agreement"],
                    "target_distinct_class_count": mode_summary["target_distinct_class_count"],
                    "process_cpu_seconds_scoring": float(sum(item["process_cpu_seconds"] for item in per_user_scores)),
                    "producer_function": "s3d_cell_headroom_precheck_runner.py::main",
                    "reused_banked_runner_sha256": runner_sha256,
                }
            )

        blocking = [
            {
                "cell_id": row["cell_id"],
                "spec_cell_name": row["spec_cell_name"],
                "verdict": row["verdict"],
                "reason": row["verdict_reason"],
                "headroom": row["headroom"],
            }
            for row in cell_rows
            if row["verdict"] != "CELL_VALID"
        ]
        result = {
            "task_id": TASK_ID,
            "task_card_id": TASK_CARD_ID,
            "artifact": "s3d_cell_headroom_precheck",
            "run_id": run_id,
            "verdict": "CELL_HEADROOM_PRECHECK_REPORTED",
            "overall_decision": "full_battery_would_be_blocked_by_listed_cells" if blocking else "all_checked_cells_pass_0_10_guard_estimate",
            "blocking_cells_for_full_battery": blocking,
            "cells": cell_rows,
            "cell_headroom_summary": {row["cell_id"]: row["headroom"] for row in cell_rows},
            "chance_cell": float(runner.CHANCE_CELL),
            "guard_threshold": GUARD_THRESHOLD,
            "k_eval_users_per_cell": K_USERS,
            "eval_user_selection_rule": "indices=floor(i*(n-1)/(k-1)+0.5), i=0..k-1 over ascending eval users",
            "heldout_users_800_999_touched": False,
            "null_env_excluded": True,
            "only_ideal_run": True,
            "members_run": False,
            "single_thread_environment": environment,
            "process_parallelism": {
                "enabled": False,
                "workers": 1,
                "threads_per_worker": 1,
                "oversubscription": False,
                "cpu_hour_accounting": "process_time_seconds/3600",
            },
            "process_cpu_seconds": float(time.process_time() - cpu_start),
            "scoring_process_cpu_seconds": float(total_scoring_cpu_seconds),
            "mode_evidence_process_cpu_seconds": float(total_mode_cpu_seconds),
            "process_cpu_hours": float((time.process_time() - cpu_start) / 3600.0),
            "wall_clock_seconds": float(time.perf_counter() - wall_start),
            "run_started_at": run_started_at,
            "run_finished_at": _utc_timestamp(),
            "utc_wall_clock_generated_at": _utc_timestamp(),
            "reused_runner_sha256": runner_sha256,
            "script_sha256": script_sha256,
            "code_path_hash": _combined_code_path_hash(runner, script_sha256),
            "producer_function": "s3d_cell_headroom_precheck_runner.py::main",
            "input_artifacts": _input_artifacts(),
            "trace_artifact": str(TRACE.relative_to(ROOT)).replace("\\", "/"),
            "claim_ceiling": CLAIM_CEILING,
        }
        _write_json(RESULT, result)
        _trace(
            {
                "event": "run_finished",
                "run_id": run_id,
                "result_path": str(RESULT.relative_to(ROOT)).replace("\\", "/"),
                "blocking_cell_count": len(blocking),
                "process_cpu_seconds": result["process_cpu_seconds"],
                "wall_clock_seconds": result["wall_clock_seconds"],
                "producer_function": "s3d_cell_headroom_precheck_runner.py::main",
            }
        )
        print(json.dumps({"result_path": str(RESULT.relative_to(ROOT)), "blocking_cells": blocking}, sort_keys=True))
        return 0
    except BaseException as exc:
        failure = {
            "task_id": TASK_ID,
            "task_card_id": TASK_CARD_ID,
            "artifact": "s3d_cell_headroom_precheck_failure_manifest",
            "verdict": "STOP_PRECHECK_EXECUTION_FAILURE",
            "stop_condition": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
            "heldout_users_800_999_touched": "heldout" in str(exc).lower(),
            "result_path": str(RESULT.relative_to(ROOT)).replace("\\", "/"),
            "trace_path": str(TRACE.relative_to(ROOT)).replace("\\", "/"),
            "run_started_at": run_started_at,
            "run_finished_at": _utc_timestamp(),
            "process_cpu_seconds": float(time.process_time() - cpu_start),
            "wall_clock_seconds": float(time.perf_counter() - wall_start),
            "producer_function": "s3d_cell_headroom_precheck_runner.py::main/except",
            "input_artifacts": _input_artifacts(),
            "claim_ceiling": CLAIM_CEILING,
            "note": "task-specific failure manifest; existing generic failure_manifest.json is not overwritten",
        }
        _write_json(FAILURE_MANIFEST, failure)
        _trace(
            {
                "event": "run_failed",
                "stop_condition": failure["stop_condition"],
                "failure_manifest": str(FAILURE_MANIFEST.relative_to(ROOT)).replace("\\", "/"),
            }
        )
        print(json.dumps({"failure_manifest": str(FAILURE_MANIFEST.relative_to(ROOT)), "error": str(exc)}, sort_keys=True))
        return 1


def _load_banked_runner() -> Any:
    spec = importlib.util.spec_from_file_location("s3d_battery_runner_line30_readonly", BANKED_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load banked runner: {BANKED_RUNNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _select_fractional_eval_users(eval_range: Sequence[int], *, k: int) -> dict[str, Any]:
    start, end = int(eval_range[0]), int(eval_range[1])
    eval_users = list(range(start, end + 1))
    n = len(eval_users)
    if k <= 0 or k > n:
        raise ValueError(f"invalid k={k} for eval user count {n}")
    if k == 1:
        fractional_positions = [(n - 1) / 2.0]
    else:
        fractional_positions = [i * (n - 1) / (k - 1) for i in range(k)]
    indices = [int(math.floor(pos + 0.5)) for pos in fractional_positions]
    if len(set(indices)) != len(indices):
        raise RuntimeError(f"fractional selection produced duplicate indices:{indices}")
    resolved = [eval_users[index] for index in indices]
    return {
        "k": int(k),
        "eval_user_range": [start, end],
        "eval_user_count": n,
        "fractional_positions": fractional_positions,
        "resolved_indices": indices,
        "resolved_user_ids": resolved,
        "ascending": resolved == sorted(resolved),
        "heldout_800_999_excluded": not any(800 <= user_id <= 999 for user_id in resolved),
    }


def _single_user_spec(spec: Any, *, user_id: int) -> Any:
    original = spec.trajectory_spec
    trajectory = TrajectorySetSpec(
        set_id=f"{original.set_id}_headroom_precheck_user_{int(user_id)}",
        master_seed=int(original.master_seed),
        env_mode=str(original.env_mode),
        partitions={"train": {"start_user_id": int(user_id), "count": 1}},
        turns_per_user=int(original.turns_per_user),
        logging_policy=original.logging_policy,
    )
    return replace(spec, trajectory_spec=trajectory, eval_user_range=(int(user_id), int(user_id)))


@contextmanager
def _patched_records_for_single_user(runner: Any, *, expected_user_id: int) -> Iterator[None]:
    original = runner._records_and_style_by_user

    def replacement(design: Mapping[str, Any], trajectory_spec: Any) -> tuple[dict[int, list[Any]], dict[int, tuple[int, ...]]]:
        by_user: dict[int, list[Any]] = {}
        style_by_user: dict[int, tuple[int, ...]] = {}
        for _, _, record, adjudicator_record in runner._iter_records_with_adjudicator(design, trajectory_spec):
            user_id = int(adjudicator_record["user_id"])
            if user_id != int(expected_user_id):
                raise RuntimeError(f"unexpected_user_generated:{expected_user_id}:{user_id}")
            if 800 <= user_id <= 999:
                raise RuntimeError(f"heldout_user_800_999_touched:{user_id}")
            by_user.setdefault(user_id, []).append(runner.event_from_mapping(record))
            style = tuple(int(value) for value in adjudicator_record["style_map"])
            if user_id in style_by_user and style_by_user[user_id] != style:
                raise RuntimeError(f"style_map_changed_within_user:{user_id}")
            style_by_user[user_id] = style
        if int(expected_user_id) not in by_user:
            raise RuntimeError(f"selected_user_not_generated:{expected_user_id}")
        return by_user, style_by_user

    runner._records_and_style_by_user = replacement
    try:
        yield
    finally:
        runner._records_and_style_by_user = original


def _score_selected_user_via_banked_ideal(
    runner: Any,
    design: Mapping[str, Any],
    spec: Any,
    *,
    user_id: int,
) -> tuple[dict[str, Any], float]:
    single_spec = _single_user_spec(spec, user_id=int(user_id))
    cpu_start = time.process_time()
    with _patched_records_for_single_user(runner, expected_user_id=int(user_id)):
        scored = runner._score_ideal_cell(design, single_spec)
    cpu_seconds = time.process_time() - cpu_start
    users = [int(item["user_id"]) for item in scored["per_user_confusion"]]
    if users != [int(user_id)]:
        raise RuntimeError(f"banked_ideal_returned_wrong_user:{user_id}:{users}")
    return scored, cpu_seconds


def _single_user_records_and_style(
    runner: Any,
    design: Mapping[str, Any],
    spec: Any,
    *,
    user_id: int,
) -> tuple[list[Any], tuple[int, ...], int]:
    single_spec = _single_user_spec(spec, user_id=int(user_id))
    records: list[Any] = []
    style_map: tuple[int, ...] | None = None
    stable_fact_symbol: int | None = None
    for _, _, record, adjudicator_record in runner._iter_records_with_adjudicator(design, single_spec.trajectory_spec):
        observed_user_id = int(adjudicator_record["user_id"])
        if observed_user_id != int(user_id):
            raise RuntimeError(f"unexpected_user_generated_for_mode:{user_id}:{observed_user_id}")
        if 800 <= observed_user_id <= 999:
            raise RuntimeError(f"heldout_user_800_999_touched_by_mode_evidence:{observed_user_id}")
        records.append(runner.event_from_mapping(record))
        style = tuple(int(value) for value in adjudicator_record["style_map"])
        if style_map is not None and style_map != style:
            raise RuntimeError(f"style_map_changed_within_mode_user:{user_id}")
        style_map = style
        stable_fact_symbol = int(adjudicator_record["stable_fact_symbol"])
    if style_map is None or stable_fact_symbol is None:
        raise RuntimeError(f"no_mode_records_generated:{user_id}")
    return records, style_map, stable_fact_symbol


def _argmax_vs_mode_evidence_for_user(
    runner: Any,
    design: Mapping[str, Any],
    spec: Any,
    *,
    user_id: int,
    metric_scope: str,
) -> tuple[dict[str, Any], float]:
    records, style_map, stable_fact_symbol = _single_user_records_and_style(
        runner,
        design,
        spec,
        user_id=int(user_id),
    )
    cpu_start = time.process_time()
    filt = runner.FactoredExactFilter(
        design,
        filter_seed=runner.independent_filter_seed(spec.master_seed, f"s3d_battery:{spec.cell_id}:{int(user_id)}"),
        true_environment_seed=spec.master_seed,
        variant=spec.variant,
        user_id=int(user_id),
        style_map=style_map,
        z_quadrature_points=3,
    )
    simulator = FspPumSimulator(design, master_seed=int(spec.master_seed), variant=spec.variant)
    true_user = simulator.start_user(user_id=int(user_id), style_map=style_map)
    scoped_turns: list[dict[str, Any]] = []
    sample_turns: list[dict[str, Any]] = []
    all_targets: list[int] = []
    all_predictions: list[int] = []
    all_modes: list[int] = []
    all_actions: list[str] = []
    replay_mismatches = []
    for turn_index, record in enumerate(records):
        action = str(record.action)
        ideal_distribution = filt.predict_distribution(action)
        ideal_argmax = int(np.argmax(np.asarray(ideal_distribution, dtype=float)))
        mode_distribution = simulator.response_distribution(true_user, action)
        generating_mode = int(np.argmax(np.asarray(mode_distribution, dtype=float)))
        target = int(record.observation["symbol"])
        all_targets.append(target)
        all_predictions.append(ideal_argmax)
        all_modes.append(generating_mode)
        all_actions.append(action)
        include = metric_scope == "overall" or (metric_scope == "recommend" and action == "recommend")
        if include:
            turn_payload = {
                "turn_index": int(turn_index),
                "action": action,
                "target": target,
                "ideal_argmax": ideal_argmax,
                "generating_mode_argmax": generating_mode,
                "ideal_argmax_matches_generating_mode": bool(ideal_argmax == generating_mode),
                "ideal_argmax_matches_target": bool(ideal_argmax == target),
                "generating_mode_matches_target": bool(generating_mode == target),
            }
            scoped_turns.append(turn_payload)
            if len(sample_turns) < 8:
                sample_turns.append(turn_payload)
        replayed = simulator.step(true_user, action)
        replayed_symbol = int(replayed.observation["symbol"])
        if replayed_symbol != target:
            replay_mismatches.append({"turn_index": int(turn_index), "target": target, "replayed": replayed_symbol})
        filt.observe(runner.IdealPrefixEvent(action=action, symbol=target))
    if replay_mismatches:
        raise RuntimeError(f"generator_replay_mismatch:{spec.cell_id}:{user_id}:{replay_mismatches[:3]}")
    scope_indices = [
        index
        for index, action in enumerate(all_actions)
        if metric_scope == "overall" or (metric_scope == "recommend" and action == "recommend")
    ]
    return (
        {
            "user_id": int(user_id),
            "style_map_sha256": _sha256_json(list(style_map)),
            "stable_fact_symbol": int(stable_fact_symbol),
            "scope": metric_scope,
            "scope_turn_count": len(scope_indices),
            "all_turn_count": len(all_actions),
            "targets_scope": [all_targets[index] for index in scope_indices],
            "ideal_argmax_scope": [all_predictions[index] for index in scope_indices],
            "generating_mode_scope": [all_modes[index] for index in scope_indices],
            "actions_scope": [all_actions[index] for index in scope_indices],
            "sample_turns": sample_turns,
            "generator_replay_exact": True,
            "producer_function": "s3d_cell_headroom_precheck_runner.py::_argmax_vs_mode_evidence_for_user",
        },
        time.process_time() - cpu_start,
    )


def _scope_targets_from_mode_evidence(evidence_users: Sequence[Mapping[str, Any]], scope: str) -> list[int]:
    del scope
    return [int(value) for user in evidence_users for value in user["targets_scope"]]


def _scope_predictions_from_mode_evidence(evidence_users: Sequence[Mapping[str, Any]], scope: str) -> list[int]:
    del scope
    return [int(value) for user in evidence_users for value in user["ideal_argmax_scope"]]


def _scope_modes_from_mode_evidence(evidence_users: Sequence[Mapping[str, Any]], scope: str) -> list[int]:
    del scope
    return [int(value) for user in evidence_users for value in user["generating_mode_scope"]]


def _summarize_mode_evidence(
    evidence_users: Sequence[Mapping[str, Any]],
    *,
    metric_scope: str,
    mode_metric: float,
    mode_headroom: float,
) -> dict[str, Any]:
    targets = _scope_targets_from_mode_evidence(evidence_users, metric_scope)
    predictions = _scope_predictions_from_mode_evidence(evidence_users, metric_scope)
    modes = _scope_modes_from_mode_evidence(evidence_users, metric_scope)
    if not targets:
        raise RuntimeError(f"empty_scope_for_mode_evidence:{metric_scope}")
    mode_matches = sum(int(pred == mode) for pred, mode in zip(predictions, modes))
    target_matches = sum(int(pred == target) for pred, target in zip(predictions, targets))
    mode_target_matches = sum(int(mode == target) for mode, target in zip(modes, targets))
    return {
        "metric_scope": metric_scope,
        "scope_turn_count": len(targets),
        "target_classes": sorted({int(value) for value in targets}),
        "target_distinct_class_count": len({int(value) for value in targets}),
        "ideal_argmax_classes": sorted({int(value) for value in predictions}),
        "generating_mode_classes": sorted({int(value) for value in modes}),
        "ideal_argmax_vs_mode_agreement": float(mode_matches / len(targets)),
        "ideal_argmax_vs_target_micro_accuracy": float(target_matches / len(targets)),
        "generating_mode_vs_target_micro_accuracy": float(mode_target_matches / len(targets)),
        "mode_oracle_metric_same_scope": float(mode_metric),
        "mode_oracle_headroom_same_scope": float(mode_headroom),
        "per_user_sample_turns": [
            {
                "user_id": int(user["user_id"]),
                "stable_fact_symbol": int(user["stable_fact_symbol"]),
                "sample_turns": list(user["sample_turns"]),
            }
            for user in evidence_users[:5]
        ],
        "all_user_evidence_sha256": _sha256_json(evidence_users),
        "generator_replay_exact_all_users": all(bool(user["generator_replay_exact"]) for user in evidence_users),
    }


def _scope_total_count(per_user_confusions: Sequence[Mapping[str, Any]], scope: str) -> int:
    key = "totals" if scope == "overall" else "recommend_totals"
    return int(sum(sum(int(value) for value in user[key]) for user in per_user_confusions))


def _metric_artifact_check(
    *,
    class_count_present: int,
    metric_aggregation_rule: str,
    ideal_metric: float,
    mode_metric: float,
    chance: float,
) -> dict[str, Any]:
    absent_class_macro_artifact = False
    reason = "runner metric averages only classes with >=1 true occurrence; absent 32-class dilution not present"
    if class_count_present <= 1 and ideal_metric <= chance + 1e-12 and mode_metric <= chance + 1e-12:
        absent_class_macro_artifact = True
        reason = "single-class target and both ideal/mode metrics are chance-scale under the reported metric"
    return {
        "target_distinct_class_count": int(class_count_present),
        "metric_aggregation_rule": metric_aggregation_rule,
        "absent_class_macro_dilution_detected": bool(absent_class_macro_artifact),
        "reason": reason,
    }


def _filter_source_support(runner: Any) -> dict[str, dict[str, Any]]:
    source = inspect.getsource(runner.FactoredExactFilter._compute_distribution_table)
    stable_source = inspect.getsource(runner.FactoredExactFilter._stable_facts_table)
    low_div_source = inspect.getsource(runner.FactoredExactFilter._low_diversity_table)
    flat_source = inspect.getsource(runner.FactoredExactFilter._flat_theta_table)
    support = {
        "constant_none": {
            "supported": "DEGENERATE_SHOULD_WIN_CONSTANT_NONE" in source,
            "evidence": "constant cert variant token absent from FactoredExactFilter._compute_distribution_table",
        },
        "constant_saturated": {
            "supported": "DEGENERATE_SHOULD_WIN_CONSTANT_SATURATED" in source,
            "evidence": "constant cert variant token absent from FactoredExactFilter._compute_distribution_table",
        },
        "camouflage_off": {
            "supported": True,
            "evidence": "camouflage_off uses default base distribution path with identity style_map from simulator",
        },
        "low_diversity": {
            "supported": "GRAPH_CACHE_SHOULD_WIN_LOW_DIVERSITY_TEMPLATES" in source and "_low_diversity_table" in source,
            "evidence": _short_hash(low_div_source),
        },
        "stable_facts": {
            "supported": "RAG_SHOULD_WIN_STABLE_FACTS" in source and "_stable_facts_table" in source,
            "evidence": _short_hash(stable_source),
        },
        "flat_theta": {
            "supported": "FLAT_THETA" in source and "_flat_theta_table" in source,
            "evidence": _short_hash(flat_source),
        },
    }
    return support


def _cell_verdict(
    *,
    cell_id: str,
    headroom: float,
    mode_headroom: float,
    mode_agreement: float,
    filter_source_support: Mapping[str, Any],
    metric_artifact: Mapping[str, Any],
) -> tuple[str, str]:
    if float(headroom) >= GUARD_THRESHOLD:
        return "CELL_VALID", "ideal_metric - chance_cell >= 0.10"
    if bool(metric_artifact["absent_class_macro_dilution_detected"]):
        return "METRIC_ARTIFACT", str(metric_artifact["reason"])
    if not bool(filter_source_support["supported"]) and float(mode_headroom) >= GUARD_THRESHOLD:
        return (
            "IDEAL_MISSPEC",
            "banked FactoredExactFilter source has no explicit support for this cert variant while generator mode has guard-scale headroom",
        )
    if float(mode_agreement) < 0.50 and cell_id in {"constant_none", "constant_saturated"}:
        return "IDEAL_MISSPEC", "ideal argmax does not track the constant generator mode on the constant cert cell"
    return (
        "CELL_DEFECTIVE",
        "banked ideal path is available for the cell, but ideal_metric - chance_cell is below the preregistered 0.10 guard",
    )


def _single_thread_environment(runner: Any) -> dict[str, Any]:
    for key in THREAD_ENV_KEYS:
        os.environ[key] = "1"
    try:
        from threadpoolctl import threadpool_limits

        threadpool_limits(limits=1)
    except Exception:
        pass
    payload = runner._single_thread_environment()
    payload["process_parallelism"] = "disabled_serial"
    payload["cpu_accounting"] = "process_time"
    return payload


def _combined_code_path_hash(runner: Any, script_sha256: str) -> str:
    material = {"runner_code_path_hash": runner._code_path_hash(), "script_sha256": script_sha256}
    return _sha256_json(material)


def _input_artifacts() -> list[dict[str, Any]]:
    return [
        _artifact_ref(TASK_CARD),
        _artifact_ref(BANKED_RUNNER),
        _artifact_ref(SPEC_CARD),
        _artifact_ref(ROOT / "src" / "fsp_pum_env" / "factored_filter.py"),
        _artifact_ref(ROOT / "src" / "fsp_pum_env" / "simulator.py"),
        _artifact_ref(FROZEN_DESIGN),
    ]


def _artifact_ref(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "exists": path.exists(),
        "sha256": _sha256(path) if path.exists() else None,
        "size_bytes": path.stat().st_size if path.exists() else None,
    }


def _trace(payload: Mapping[str, Any]) -> None:
    with TRACE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_jsonable(payload), sort_keys=True) + "\n")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, float) and math.isnan(value):
        return "NaN"
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_json(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(_jsonable(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _short_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


if __name__ == "__main__":
    raise SystemExit(main())
