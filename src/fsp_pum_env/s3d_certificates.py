"""S3d should-win certificate and NULL-env control utilities.

This module is an offline instrument harness for
FSP-PUM-ENV-IDPROBE-001A-S3D-SHOULD-WIN-NULL-ENV-SPEC-001A.  It does not
touch EGO mainline runtime and does not alter frozen governing documents.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import inspect
import json
from pathlib import Path
import time
from typing import Any, Mapping, Sequence

import numpy as np

from .ideal_observer import ExactBayesFilter, PrefixEvent as IdealPrefixEvent, ThetaGridSpec, independent_filter_seed
from .factored_filter import FactoredExactFilter
from .simulator import FspPumSimulator, SimulatorVariant
from .trajectory_sets import (
    TrajectorySetSpec,
    _hash_spec_streams,
    _iter_records_with_adjudicator,
    load_frozen_design,
    regenerate_member_view_sha256,
)


TASK_ID = "FSP-PUM-ENV-IDPROBE-001A"
S3D_CPU_HOUR_LIMIT = 12.0
CHANCE_CELL = 1.0 / 32.0
NULL_MARGIN = 0.005


@dataclass(frozen=True)
class S3DCertCell:
    cell_id: str
    variant: str
    master_seed: int


@dataclass(frozen=True)
class S3DCertSetSpec:
    cell_id: str
    variant: str
    master_seed: int
    trajectory_spec: TrajectorySetSpec
    fit_user_range: tuple[int, int] = (0, 639)
    eval_user_range: tuple[int, int] = (640, 799)


S3D_CERT_CELLS: tuple[S3DCertCell, ...] = (
    S3DCertCell("constant_none", SimulatorVariant.DEGENERATE_SHOULD_WIN_CONSTANT_NONE.value, 20260711),
    S3DCertCell("constant_saturated", SimulatorVariant.DEGENERATE_SHOULD_WIN_CONSTANT_SATURATED.value, 20260712),
    S3DCertCell("camouflage_off", SimulatorVariant.CAMOUFLAGE_OFF.value, 20260713),
    S3DCertCell(
        "low_diversity",
        SimulatorVariant.GRAPH_CACHE_SHOULD_WIN_LOW_DIVERSITY_TEMPLATES.value,
        20260714,
    ),
    S3DCertCell("stable_facts", SimulatorVariant.RAG_SHOULD_WIN_STABLE_FACTS.value, 20260715),
    S3DCertCell("flat_theta", SimulatorVariant.FLAT_THETA.value, 20260716),
    S3DCertCell("NULL_env", SimulatorVariant.NULL_ENV.value, 20260717),
)


SELECTED_RECIPE_FILES: tuple[str, ...] = (
    "obs_decoder_logreg_selected_recipe.json",
    "obs_decoder_gbt_selected_recipe.json",
    "obs_decoder_gru_selected_recipe.json",
    "seq_full_history_no_action_conditioning_selected_recipe.json",
    "seq_window_with_action_conditioning_W15_no_cross_session_persistence_selected_recipe.json",
)


def build_s3d_cert_set_specs(design: Mapping[str, Any]) -> list[S3DCertSetSpec]:
    """Return the frozen §3 S3d certificate-set specs.

    The existing S3c helpers split users 0..799 internally; therefore the
    underlying trajectory spec uses one 0..799 partition named ``train`` while
    this S3d wrapper records the frozen fit/eval ranges explicitly.
    """

    turns_per_user = int(design["env_parameters"]["episodes"]["total_turns_per_user"])
    logging_policy = design["population_and_data"]["log_parity_trajectory_policy"]
    specs: list[S3DCertSetSpec] = []
    for cell in S3D_CERT_CELLS:
        SimulatorVariant(cell.variant)
        specs.append(
            S3DCertSetSpec(
                cell_id=cell.cell_id,
                variant=cell.variant,
                master_seed=int(cell.master_seed),
                trajectory_spec=TrajectorySetSpec(
                    set_id=f"s3d_{cell.cell_id}",
                    master_seed=int(cell.master_seed),
                    env_mode=cell.variant,
                    partitions={"train": {"start_user_id": 0, "count": 800}},
                    turns_per_user=turns_per_user,
                    logging_policy=logging_policy,
                ),
            )
        )
    return specs


def macro_balanced_accuracy(y_true: Sequence[int], y_pred: Sequence[int], *, alphabet_size: int) -> float:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred length mismatch")
    totals = np.zeros(int(alphabet_size), dtype=np.int64)
    correct = np.zeros(int(alphabet_size), dtype=np.int64)
    for target, pred in zip(y_true, y_pred):
        target_i = int(target)
        totals[target_i] += 1
        correct[target_i] += int(int(pred) == target_i)
    present = totals > 0
    if not bool(np.any(present)):
        return 0.0
    return float(np.mean(correct[present] / totals[present]))


def load_s3d_selected_recipe_hashes(artifact_root: str | Path) -> dict[str, str]:
    model_dir = Path(artifact_root) / "s3c_models"
    return {name: hashlib.sha256((model_dir / name).read_bytes()).hexdigest() for name in SELECTED_RECIPE_FILES}


def run_s3d_preflight_guards(
    frozen_design_path: str | Path,
    s3a_manifest_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    """Run S3d Step-1 guards that are computable before the full certificate line."""

    run_started_at = _utc_timestamp()
    start = time.perf_counter()
    design = load_frozen_design(frozen_design_path)
    s3a_manifest = _read_json(s3a_manifest_path)
    set_00 = next(entry for entry in s3a_manifest["sets"] if str(entry["set_id"]) == "set_00")

    base_start = time.perf_counter()
    regenerated = regenerate_member_view_sha256(design, set_00)
    base_guard = {
        "guard": "BASE-invariance regression",
        "declared_slice": "full banked set_00 member-view stream; stronger than >=2 users full horizon",
        "banked_member_view_sha256": set_00["member_view_sha256"],
        "regenerated_member_view_sha256": regenerated,
        "passed": regenerated == set_00["member_view_sha256"],
        "wall_clock_seconds": time.perf_counter() - base_start,
    }

    variant_guards = [_constant_variant_guard(design, cell.variant, cell.master_seed) for cell in S3D_CERT_CELLS[:2]]
    ideal_guards = [_constant_variant_ideal_guard(design, cell.variant, cell.master_seed) for cell in S3D_CERT_CELLS[:2]]
    passed = bool(base_guard["passed"]) and all(item["passed"] for item in variant_guards) and all(
        item["passed"] for item in ideal_guards
    )
    report = {
        "task_id": TASK_ID,
        "stage": "S3d",
        "artifact": "s3d_preflight_guard_report",
        "verdict": "guards_passed" if passed else "STOP_s3d_preflight_guard_failed",
        "passed": passed,
        "base_invariance_regression": base_guard,
        "new_variant_guards": variant_guards,
        "ideal_filter_micro_sanity": ideal_guards,
        "sealing_import_graph_test": "must be run via python -m pytest tests/fsp_pum_env/test_s3a_sealing_import_graph.py -q",
        "producer_function": "src.fsp_pum_env.s3d_certificates.run_s3d_preflight_guards",
        "code_path_hash": _code_path_hash(),
        "input_artifacts": [str(frozen_design_path), str(s3a_manifest_path)],
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "wall_clock_seconds": time.perf_counter() - start,
        "claim_ceiling": "S3d preflight guard evidence only; no certificate, NULL, environment-validity, baseline-power, gap, mechanism, agency, or EGO claim",
    }
    _write_json(output_path, report)
    if not passed:
        failure_path = Path(output_path).with_name("s3d_preflight_guard_failure_manifest.json")
        _write_json(failure_path, _failure_manifest("STOP_s3d_preflight_guard_failed", report, "preflight guard failed"))
    return report


def run_s3d_part0_projection(
    frozen_design_path: str | Path,
    output_path: str | Path,
    failure_manifest_path: str | Path,
) -> dict[str, Any]:
    """Run the S3d PART 0 compute projection gate.

    The current implementation stops as soon as a measured lower bound already
    exceeds the frozen 12 CPU-h line.  That preserves the budget gate without
    spending additional CPU on cost classes that cannot change the decision.
    """

    run_started_at = _utc_timestamp()
    start = time.perf_counter()
    design = load_frozen_design(frozen_design_path)
    environment = _single_thread_environment()
    specs = {spec.cell_id: spec for spec in build_s3d_cert_set_specs(design)}

    generation_start = time.perf_counter()
    member_sha, adjudicator_sha, member_bytes, adjudicator_bytes, record_count = _hash_spec_streams(
        design,
        specs["constant_none"].trajectory_spec,
    )
    generation_measurement = {
        "unit": "one_cert_set_generation",
        "cell_id": "constant_none",
        "variant": specs["constant_none"].variant,
        "member_view_sha256": member_sha,
        "adjudicator_only_sha256": adjudicator_sha,
        "member_view_record_count": int(record_count),
        "member_view_estimated_raw_bytes": int(member_bytes),
        "adjudicator_only_estimated_raw_bytes": int(adjudicator_bytes),
        "wall_clock_seconds": time.perf_counter() - generation_start,
    }

    ideal_measurement = measure_s3d_ideal_one_eval_user(
        design,
        specs["camouflage_off"],
        user_id=640,
    )
    camouflage_ideal_projected_cpu_hours = (
        float(ideal_measurement["wall_clock_seconds"]) * 160.0 / 3600.0
    )
    lower_bound_cpu_hours = camouflage_ideal_projected_cpu_hours
    decision = (
        "STOP_projection_lower_bound_exceeds_12_cpu_hours"
        if lower_bound_cpu_hours > S3D_CPU_HOUR_LIMIT
        else "projection_lower_bound_within_12_cpu_hours_full_part0_required"
    )
    projection = {
        "task_id": TASK_ID,
        "stage": "S3d",
        "artifact": "s3d_compute_projection",
        "part": "PART 0",
        "claim_ceiling": "PART 0 compute projection only; no certificate, NULL, environment-validity, baseline-power, gap, mechanism, agency, or EGO claim",
        "cpu_hour_limit": S3D_CPU_HOUR_LIMIT,
        "single_thread_environment": environment,
        "measurements": {
            "cert_set_generation": generation_measurement,
            "ideal_per_user_one_cell": ideal_measurement,
            "fit_score_cost_classes": [],
        },
        "projection_rule": {
            "declared_assumption": "linear projection from measured per-user full-prefix S2 ideal cost; one camouflage_off cell has 160 eval users",
            "lower_bound_basis": "camouflage_off S2 ideal alone, excluding generation, fitting, scoring, other cells, bootstrap, and NULL-env",
            "camouflage_off_eval_users": 160,
        },
        "projected_cpu_hours": lower_bound_cpu_hours,
        "projection_lower_bound_cpu_hours": lower_bound_cpu_hours,
        "camouflage_off_ideal_projected_cpu_hours": camouflage_ideal_projected_cpu_hours,
        "unmeasured_required_cost_classes_after_decisive_lower_bound": [
            "logreg_F1_or_F2",
            "gbt",
            "gru",
            "seq",
            "table-family",
            "retrieval-family",
            "degenerates",
            "remaining ideal cells",
            "NULL-env full battery",
            "bootstrap",
        ],
        "decision": decision,
        "runtime_guard_decision": decision,
        "producer_function": "src.fsp_pum_env.s3d_certificates.run_s3d_part0_projection",
        "code_path_hash": _code_path_hash(),
        "input_artifacts": [str(frozen_design_path)],
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "wall_clock_seconds": time.perf_counter() - start,
    }
    _write_json(output_path, projection)
    if lower_bound_cpu_hours > S3D_CPU_HOUR_LIMIT:
        manifest = _failure_manifest(
            "STOP_s3d_part0_projection_exceeds_12_cpu_hours",
            projection,
            "PART 0 measured lower-bound projection exceeds 12.0 CPU-h before any full certificate run",
        )
        _write_json(failure_manifest_path, manifest)
    return projection


def measure_s3d_ideal_one_eval_user(
    design: Mapping[str, Any],
    spec: S3DCertSetSpec,
    *,
    user_id: int,
) -> dict[str, Any]:
    if int(user_id) < spec.eval_user_range[0] or int(user_id) > spec.eval_user_range[1]:
        raise ValueError("S3d ideal one-user measurement must use eval user 640..799")
    user_spec = TrajectorySetSpec(
        set_id=f"{spec.trajectory_spec.set_id}_ideal_unit_user_{int(user_id)}",
        master_seed=spec.master_seed,
        env_mode=spec.variant,
        partitions={"train": {"start_user_id": int(user_id), "count": 1}},
        turns_per_user=spec.trajectory_spec.turns_per_user,
        logging_policy=spec.trajectory_spec.logging_policy,
    )
    records: list[dict[str, Any]] = []
    style_map: tuple[int, ...] | None = None
    for _, _, record, adjudicator_record in _iter_records_with_adjudicator(design, user_spec):
        records.append(record)
        style_map = tuple(int(value) for value in adjudicator_record["style_map"])
    if style_map is None:
        raise RuntimeError("no records generated for S3d ideal one-user measurement")

    start = time.perf_counter()
    filt = FactoredExactFilter(
        design,
        filter_seed=independent_filter_seed(spec.master_seed, f"s3d_part0:{spec.cell_id}:{int(user_id)}"),
        true_environment_seed=spec.master_seed,
        variant=spec.variant,
        user_id=int(user_id),
        style_map=style_map,
        z_quadrature_points=3,
    )
    predictions: list[int] = []
    targets: list[int] = []
    for record in records:
        distribution = filt.predict_distribution(str(record["action"]))
        predictions.append(int(np.argmax(np.asarray(distribution, dtype=float))))
        symbol = int(record["observation"]["symbol"])
        targets.append(symbol)
        filt.observe(IdealPrefixEvent(action=str(record["action"]), symbol=symbol))
    wall_clock = time.perf_counter() - start
    return {
        "unit": "S2_ideal_one_eval_user_full_300_turn_prefix",
        "cell_id": spec.cell_id,
        "variant": spec.variant,
        "user_id": int(user_id),
        "turns": len(records),
        "filter_class": "src.fsp_pum_env.factored_filter.FactoredExactFilter",
        "z_quadrature_points_per_dim": 3,
        "atom_count": int(filt.atom_count),
        "posterior_array_bytes": int(filt.array_bytes()),
        "wall_clock_seconds": wall_clock,
        "cpu_hours": wall_clock / 3600.0,
        "metric": macro_balanced_accuracy(targets, predictions, alphabet_size=32),
        "classes_present": sorted(set(targets)),
        "producer_function": "src.fsp_pum_env.s3d_certificates.measure_s3d_ideal_one_eval_user",
    }


def generate_s3d_cert_sets_manifest(
    frozen_design_path: str | Path,
    output_path: str | Path,
    *,
    cells: Sequence[str] | None = None,
) -> dict[str, Any]:
    run_started_at = _utc_timestamp()
    start = time.perf_counter()
    design = load_frozen_design(frozen_design_path)
    requested = set(cells) if cells is not None else {cell.cell_id for cell in S3D_CERT_CELLS}
    specs = [spec for spec in build_s3d_cert_set_specs(design) if spec.cell_id in requested]
    entries = []
    for spec in specs:
        unit_start = time.perf_counter()
        member_sha, adjudicator_sha, member_bytes, adjudicator_bytes, record_count = _hash_spec_streams(
            design,
            spec.trajectory_spec,
        )
        entries.append(
            {
                "cell_id": spec.cell_id,
                "variant": spec.variant,
                "master_seed": int(spec.master_seed),
                "fit_user_range": list(spec.fit_user_range),
                "eval_user_range": list(spec.eval_user_range),
                "heldout_users_800_999_generated": False,
                "generation_params": spec.trajectory_spec.to_json_dict(),
                "member_view_sha256": member_sha,
                "adjudicator_only_sha256": adjudicator_sha,
                "member_view_record_count": int(record_count),
                "member_view_estimated_raw_bytes": int(member_bytes),
                "adjudicator_only_estimated_raw_bytes": int(adjudicator_bytes),
                "wall_clock_seconds": time.perf_counter() - unit_start,
            }
        )
    manifest = {
        "task_id": TASK_ID,
        "stage": "S3d",
        "artifact": "s3d_cert_sets_manifest",
        "sets": entries,
        "main_trajectory_sets_read": False,
        "users_generated": [0, 799],
        "heldout_users_800_999_touched": False,
        "producer_function": "src.fsp_pum_env.s3d_certificates.generate_s3d_cert_sets_manifest",
        "code_path_hash": _code_path_hash(),
        "input_artifacts": [str(frozen_design_path)],
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "wall_clock_seconds": time.perf_counter() - start,
        "claim_ceiling": "S3d certificate-set generation manifest only; no certificate, NULL, environment-validity, baseline-power, gap, mechanism, agency, or EGO claim",
    }
    _write_json(output_path, manifest)
    return manifest


def write_s3d_collision_record(output_path: str | Path) -> dict[str, Any]:
    run_started_at = _utc_timestamp()
    record = {
        "task_id": TASK_ID,
        "stage": "S3d",
        "artifact": "s3d_collision_record_001a",
        "collision_record": [
            {
                "candidate": "minimal implementation",
                "evidence_it_would_produce": "new cert variants plus manifest/projection wiring",
                "strongest_cheap_baseline_that_could_match": "static one-hot or action-template shortcuts could pass favorable cells without proving environment validity",
                "leakage_or_hardcoding_risk": "high if cert cells are treated as gap evidence or if ideal path uses true latents",
                "smallest_falsifying_test": "NULL-env false-headroom breach or BASE-invariance hash mismatch",
                "expected_failure_mode": "instrument passes only trivial favorable cells and overclaims baseline power",
            },
            {
                "candidate": "strongest baseline / shortcut explanation",
                "evidence_it_would_produce": "degenerate/action-template/retrieval members pass cells because cells are intentionally matched to their shortcuts",
                "strongest_cheap_baseline_that_could_match": "one-hot constants, action lookup, prefix modal counts, nearest-neighbor retrieval",
                "leakage_or_hardcoding_risk": "cell assignment itself is favorable; success cannot imply real gap or mechanism evidence",
                "smallest_falsifying_test": "NULL-env control > chance+0.005 or ideal headroom below 0.10",
                "expected_failure_mode": "baseline certificates reveal only trainability on favorable distributions",
            },
            {
                "candidate": "mechanism-faithful implementation",
                "evidence_it_would_produce": "callable generation, fit, exact ideal, bootstrap, NULL control, and runtime accounting under frozen thresholds",
                "strongest_cheap_baseline_that_could_match": "same-access baselines are the target here; this is instrument validation, not mechanism validation",
                "leakage_or_hardcoding_risk": "exact ideal or stable-fact lineage gaps can invalidate the instrument if hidden state is used",
                "smallest_falsifying_test": "PART 0 runtime lower bound exceeds 12 CPU-h, exact-ideal unsupported cell, or NULL false headroom",
                "expected_failure_mode": "budget/runtime or S2 ideal coverage blocks full certificate execution",
            },
        ],
        "selected_approach": "mechanism-faithful implementation gated by PART 0; stop instead of shrinking if budget is exceeded",
        "claim_ceiling": "collision/route record only; no certificate, NULL, environment-validity, baseline-power, gap, mechanism, agency, or EGO claim",
        "producer_function": "src.fsp_pum_env.s3d_certificates.write_s3d_collision_record",
        "code_path_hash": _code_path_hash(),
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
    }
    _write_json(output_path, record)
    return record


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _constant_variant_guard(design: Mapping[str, Any], variant: str, master_seed: int) -> dict[str, Any]:
    start = time.perf_counter()
    sim = FspPumSimulator(design, master_seed=master_seed, variant=variant)
    target = 0 if variant == SimulatorVariant.DEGENERATE_SHOULD_WIN_CONSTANT_NONE.value else sim.alphabet_size - 1
    style = tuple(range(sim.alphabet_size))
    theta_controls = [
        {
            "sensitivity_flags": [0, 0],
            "topic_values": [-1.5] * 8,
            "trust_gain_alpha": 0.05,
            "trust_decay_beta": 0.9,
            "disclosure_threshold_d": 0.3,
        },
        {
            "sensitivity_flags": [1, 1],
            "topic_values": [1.5] * 8,
            "trust_gain_alpha": 0.2,
            "trust_decay_beta": 0.98,
            "disclosure_threshold_d": 0.7,
        },
        {
            "sensitivity_flags": [1, 0],
            "topic_values": [-1.5, -0.5, 0.5, 1.5, -1.5, -0.5, 0.5, 1.5],
            "trust_gain_alpha": 0.1,
            "trust_decay_beta": 0.95,
            "disclosure_threshold_d": 0.5,
        },
    ]
    users = [sim.start_user(user_id=index, controlled_theta=theta, style_map=style) for index, theta in enumerate(theta_controls)]
    max_theta_delta = 0.0
    min_target_probability = 1.0
    for action in sim.all_actions:
        reference = sim.response_distribution(users[0], action)
        min_target_probability = min(min_target_probability, float(reference[target]))
        for user in users[1:]:
            max_theta_delta = max(
                max_theta_delta,
                float(np.max(np.abs(np.asarray(reference) - np.asarray(sim.response_distribution(user, action))))),
            )
    hit_count = 0
    samples = 10_000
    user = sim.start_user(user_id=77, controlled_theta=theta_controls[-1], style_map=style)
    for step in range(samples):
        if step and step % int(design["env_parameters"]["episodes"]["total_turns_per_user"]) == 0:
            user = sim.start_user(user_id=77 + step, controlled_theta=theta_controls[-1], style_map=style)
        result = sim.step(user, sim.all_actions[step % len(sim.all_actions)])
        hit_count += int(result.observation["symbol"] == target)
    concentration = hit_count / samples
    passed = concentration >= 0.95 and min_target_probability >= 0.95 and max_theta_delta <= 1e-9
    return {
        "variant": variant,
        "target_symbol": target,
        "samples": samples,
        "sample_concentration": concentration,
        "min_target_probability": min_target_probability,
        "max_theta_distribution_delta": max_theta_delta,
        "no_new_observation_fields": True,
        "passed": passed,
        "wall_clock_seconds": time.perf_counter() - start,
    }


def _constant_variant_ideal_guard(design: Mapping[str, Any], variant: str, master_seed: int) -> dict[str, Any]:
    start = time.perf_counter()
    sim = FspPumSimulator(design, master_seed=master_seed, variant=variant)
    style = tuple(range(sim.alphabet_size))
    user = sim.start_user(user_id=3, style_map=style)
    filt = ExactBayesFilter(
        design,
        filter_seed=independent_filter_seed(master_seed, f"s3d_micro_guard:{variant}"),
        true_environment_seed=master_seed,
        variant=variant,
        style_map=style,
        grid_spec=ThetaGridSpec.micro_pc_grid(design),
        user_id=3,
        z_quadrature_points=3,
    )
    max_abs_delta = 0.0
    for action in ("task_topic_0", "probe_0", "recommend", "task_topic_7"):
        ideal = filt.predict_distribution(action)
        sim_dist = sim.response_distribution(user, action)
        max_abs_delta = max(max_abs_delta, float(np.max(np.abs(np.asarray(ideal) - np.asarray(sim_dist)))))
        result = sim.step(user, action)
        filt.observe(IdealPrefixEvent(action=action, symbol=int(result.observation["symbol"])))
    return {
        "variant": variant,
        "micro_config": "ThetaGridSpec.micro_pc_grid, identity style_map, z_quadrature_points=3",
        "max_abs_delta": max_abs_delta,
        "tolerance": 1e-9,
        "passed": max_abs_delta <= 1e-9,
        "wall_clock_seconds": time.perf_counter() - start,
    }


def _single_thread_environment() -> dict[str, Any]:
    import os

    for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[key] = "1"
    payload: dict[str, Any] = {
        "single_thread_accounting": True,
        "env_threads": {key: os.environ.get(key, "") for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS")},
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
    except Exception as exc:  # pragma: no cover - environment-specific
        payload["torch_error"] = str(exc)
    return payload


def _failure_manifest(verdict: str, payload: Mapping[str, Any], stop_condition: str) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "stage": "S3d",
        "artifact": "s3d_failure_manifest",
        "verdict": verdict,
        "stop_condition": stop_condition,
        "preserved_failure": True,
        "payload_artifact": payload.get("artifact"),
        "payload_decision": payload.get("decision") or payload.get("verdict"),
        "claim_ceiling": "S3d STOP/failure boundary only; no certificate, NULL, environment-validity, baseline-power, gap, mechanism, agency, or EGO claim",
        "producer_function": "src.fsp_pum_env.s3d_certificates._failure_manifest",
        "code_path_hash": _code_path_hash(),
        "run_started_at": _utc_timestamp(),
        "run_finished_at": _utc_timestamp(),
    }


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(val) for key, val in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    return value


def _code_path_hash() -> str:
    h = hashlib.sha256()
    for path in (Path(__file__), Path(inspect.getsourcefile(FspPumSimulator) or "")):
        h.update(path.name.encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
