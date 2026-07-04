"""Host-side S3d PART 0 projection extension runner.

This file is task-local provenance for FSP-PUM-ENV-IDPROBE-001A S3d PART 0.
It extends the already-written lower-bound `run_s3d_part0_projection` artifact
only when that lower bound is within the frozen 12 CPU-h line.

Claim ceiling: compute-projection evidence only.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Callable, Iterable, Mapping, Sequence

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
from src.fsp_pum_env.s3d_certificates import (
    S3D_CPU_HOUR_LIMIT,
    build_s3d_cert_set_specs,
    macro_balanced_accuracy,
)
from src.fsp_pum_env.trajectory_sets import _iter_records_with_adjudicator, load_frozen_design


TASK_ID = "FSP-PUM-ENV-IDPROBE-001A"
ARTIFACT_ROOT = ROOT / "artifacts" / TASK_ID
FROZEN_DESIGN = ARTIFACT_ROOT / "frozen_design.json"
VOCABULARY = ARTIFACT_ROOT / "s3c_models" / "f2_ngram_vocabulary.json"
PROJECTION = ARTIFACT_ROOT / "s3d_compute_projection.json"
PREFIT_V1 = ARTIFACT_ROOT / "s3d_compute_projection_v1.json"
FAILURE_MANIFEST = ARTIFACT_ROOT / "s3d_part0_projection_failure_manifest.json"


def run_full_projection_extension() -> dict[str, Any]:
    run_started_at = _utc_timestamp()
    start = time.perf_counter()
    environment = _single_thread_environment()
    design = load_frozen_design(FROZEN_DESIGN)
    initial_projection = _read_json(PREFIT_V1 if PREFIT_V1.exists() else PROJECTION)

    if float(initial_projection["projection_lower_bound_cpu_hours"]) > S3D_CPU_HOUR_LIMIT:
        final = dict(initial_projection)
        final["full_part0_extension_skipped"] = "lower_bound_already_exceeded_12_cpu_hours"
        _write_json(PROJECTION, final)
        _write_json(
            FAILURE_MANIFEST,
            _failure_manifest(
                "STOP_s3d_part0_projection_exceeds_12_cpu_hours",
                final,
                "PART 0 lower bound exceeds 12.0 CPU-h",
            ),
        )
        return final

    specs = {spec.cell_id: spec for spec in build_s3d_cert_set_specs(design)}
    vocabulary = _read_json(VOCABULARY)

    selected_recipes = {
        "obs_decoder_logreg": _read_json(ARTIFACT_ROOT / "s3c_models" / "obs_decoder_logreg_selected_recipe.json"),
        "obs_decoder_gbt": _read_json(ARTIFACT_ROOT / "s3c_models" / "obs_decoder_gbt_selected_recipe.json"),
        "obs_decoder_gru": _read_json(ARTIFACT_ROOT / "s3c_models" / "obs_decoder_gru_selected_recipe.json"),
        "seq_full_history_no_action_conditioning": _read_json(
            ARTIFACT_ROOT / "s3c_models" / "seq_full_history_no_action_conditioning_selected_recipe.json"
        ),
        "seq_window_with_action_conditioning_W15_no_cross_session_persistence": _read_json(
            ARTIFACT_ROOT
            / "s3c_models"
            / "seq_window_with_action_conditioning_W15_no_cross_session_persistence_selected_recipe.json"
        ),
    }
    selected_recipe_hashes = {name: _sha256(path) for name, path in _selected_recipe_paths().items()}

    measurements: dict[str, Any] = {}
    measurements["logreg_F1_selected"] = _measure_sklearn_selected(
        design,
        specs["camouflage_off"],
        selected_recipes["obs_decoder_logreg"]["selected_config"]["config"],
        features="F1",
    )
    measurements["logreg_F2_reference"] = _measure_sklearn_selected(
        design,
        specs["camouflage_off"],
        obs_decoders.decoder_grid("obs_decoder_logreg")[4],
        features="F2",
        vocabulary=vocabulary,
    )
    measurements["gbt_half_data_selected"] = _measure_sklearn_selected(
        design,
        specs["camouflage_off"],
        selected_recipes["obs_decoder_gbt"]["selected_config"]["config"],
        features="F2",
        vocabulary=vocabulary,
        fit_user_filter=set(obs_decoders.gbt_fit_user_ids()),
    )
    measurements["gru_selected"] = _measure_gru_selected(
        design,
        specs["camouflage_off"],
        selected_recipes["obs_decoder_gru"]["selected_config"]["config"],
        member_kind="obs_decoder_gru",
    )
    measurements["seq_full_selected"] = _measure_gru_selected(
        design,
        specs["constant_none"],
        selected_recipes["seq_full_history_no_action_conditioning"]["selected_config"]["config"],
        member_kind="seq_full_history_no_action_conditioning",
    )
    measurements["seq_W15_selected"] = _measure_gru_selected(
        design,
        specs["low_diversity"],
        selected_recipes["seq_window_with_action_conditioning_W15_no_cross_session_persistence"]["selected_config"]["config"],
        member_kind="seq_window_with_action_conditioning_W15_no_cross_session_persistence",
    )

    # Prefix families are measured as fit-on-640-users plus score-one-eval-user units,
    # then projected to 160 eval users per member-cell. This avoids launching the full
    # certificate battery while still measuring each family on the real callable path.
    measurements["table_family"] = _measure_prefix_family_one_eval_user(
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
    )
    measurements["retrieval_family"] = _measure_prefix_family_one_eval_user(
        design,
        specs["stable_facts"],
        {
            "rag_k5_episode_retrieval": RagK5EpisodeRetrievalPredictor,
            "nearest_neighbor_user_matching": NearestNeighborUserMatchingPredictor,
        },
        eval_user_id=640,
    )
    measurements["degenerate_family"] = _measure_prefix_family_one_eval_user(
        design,
        specs["constant_none"],
        {
            "predict_all": PredictAllPredictor,
            "predict_none": PredictNonePredictor,
            "majority": MajorityPredictor,
            "global_prior": GlobalPriorPredictor,
        },
        eval_user_id=640,
    )
    measurements["ls_online_family"] = _measure_prefix_family_one_eval_user(
        design,
        specs["flat_theta"],
        {
            "discounted_LS_lambda_0.95": DiscountedLeastSquaresPredictor,
            "running_average_preference_regressor": RunningAveragePreferenceRegressor,
        },
        eval_user_id=640,
    )
    measurements["bootstrap"] = _measure_bootstrap_unit()

    projection = _project_total(initial_projection, measurements)
    decision = (
        "STOP_s3d_part0_projection_exceeds_12_cpu_hours"
        if projection["total_projected_cpu_hours"] > S3D_CPU_HOUR_LIMIT
        else "s3d_part0_projection_within_12_cpu_hours_STOP_for_operator_review"
    )
    final = {
        **initial_projection,
        "artifact": "s3d_compute_projection",
        "part": "PART 0 full projection",
        "claim_ceiling": (
            "PART 0 compute projection only; no certificate, NULL, environment-validity, "
            "baseline-power, gap, mechanism, learning-capability, agency, or EGO claim"
        ),
        "single_thread_environment": environment,
        "selected_recipe_sha256": selected_recipe_hashes,
        "full_part0_measurements": measurements,
        "full_part0_projection": projection,
        "projected_cpu_hours": projection["total_projected_cpu_hours"],
        "projection_cpu_hours": projection["total_projected_cpu_hours"],
        "projection_total_cpu_hours": projection["total_projected_cpu_hours"],
        "decision": decision,
        "runtime_guard_decision": decision,
        "producer_function": (
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_projection_runner.py::"
            "run_full_projection_extension"
        ),
        "initial_lower_bound_artifact": str(PREFIT_V1.relative_to(ROOT)),
        "input_artifacts": [
            str(FROZEN_DESIGN.relative_to(ROOT)),
            str(PREFIT_V1.relative_to(ROOT)),
            str(VOCABULARY.relative_to(ROOT)),
            *[str(path.relative_to(ROOT)) for path in _selected_recipe_paths().values()],
        ],
        "run_id": f"s3d-part0-full-projection-{run_started_at}",
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "wall_clock_seconds": time.perf_counter() - start,
        "code_path_hash": _code_path_hash(),
    }
    _write_json(PROJECTION, final)
    if projection["total_projected_cpu_hours"] > S3D_CPU_HOUR_LIMIT:
        _write_json(
            FAILURE_MANIFEST,
            _failure_manifest(
                "STOP_s3d_part0_projection_exceeds_12_cpu_hours",
                final,
                "PART 0 full projected CPU-h exceeds 12.0 CPU-h",
            ),
        )
    return final


def _measure_sklearn_selected(
    design: Mapping[str, Any],
    spec: Any,
    config: Mapping[str, Any],
    *,
    features: str,
    vocabulary: Mapping[str, Any] | None = None,
    fit_user_filter: set[int] | None = None,
) -> dict[str, Any]:
    measurement = obs_decoders._measure_sklearn_one_set(
        design,
        spec.trajectory_spec,
        config,
        features=features,
        vocabulary=vocabulary,
        fit_user_filter=fit_user_filter,
    )
    measurement["cell_id"] = spec.cell_id
    measurement["variant"] = spec.variant
    measurement["selected_recipe_measurement"] = True
    return measurement


def _measure_gru_selected(
    design: Mapping[str, Any],
    spec: Any,
    config: Mapping[str, Any],
    *,
    member_kind: str,
) -> dict[str, Any]:
    measurement = obs_decoders._measure_gru_one_set(
        design,
        spec.trajectory_spec,
        config,
        member_kind=member_kind,
    )
    measurement["cell_id"] = spec.cell_id
    measurement["variant"] = spec.variant
    measurement["selected_recipe_measurement"] = True
    return measurement


def _measure_prefix_family_one_eval_user(
    design: Mapping[str, Any],
    spec: Any,
    member_classes: Mapping[str, Callable[..., Any]],
    *,
    eval_user_id: int,
) -> dict[str, Any]:
    start = time.perf_counter()
    records_by_user = _records_by_user(design, spec.trajectory_spec)
    fit_records = [record for user_id in range(0, 640) for record in records_by_user[user_id]]
    eval_records = records_by_user[int(eval_user_id)]
    collect_seconds = time.perf_counter() - start
    members: dict[str, Any] = {}
    for member, cls in member_classes.items():
        member_start = time.perf_counter()
        predictor = cls.from_design(design)
        fit_start = time.perf_counter()
        if hasattr(predictor, "fit"):
            predictor.fit(fit_records)
        else:
            for record in fit_records:
                predictor.observe(record)
        fit_seconds = time.perf_counter() - fit_start
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
        members[member] = {
            "member": member,
            "cell_id": spec.cell_id,
            "variant": spec.variant,
            "fit_users": 640,
            "eval_user_id_measured": int(eval_user_id),
            "eval_users_projected_per_member_cell": 160,
            "fit_records": len(fit_records),
            "eval_records_one_user": len(eval_records),
            "fit_wall_clock_seconds": fit_seconds,
            "score_one_eval_user_wall_clock_seconds": score_seconds,
            "projected_one_member_cell_seconds": fit_seconds + (score_seconds * 160.0),
            "one_eval_user_macro_balanced_accuracy": macro_balanced_accuracy(y_true, y_pred, alphabet_size=response_alphabet_size(design)),
            "producer_function": (
                "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_projection_runner.py::"
                "_measure_prefix_family_one_eval_user"
            ),
            "wall_clock_seconds": time.perf_counter() - member_start,
        }
    return {
        "cell_id": spec.cell_id,
        "variant": spec.variant,
        "members": members,
        "record_collection_wall_clock_seconds": collect_seconds,
        "projection_unit": "fit_640_users_plus_score_one_eval_user_scaled_to_160_eval_users",
        "heldout_users_800_999_touched": False,
        "producer_function": (
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_projection_runner.py::"
            "_measure_prefix_family_one_eval_user"
        ),
        "wall_clock_seconds": time.perf_counter() - start,
    }


def _records_by_user(design: Mapping[str, Any], spec: Any) -> dict[int, list[PrefixEvent]]:
    by_user: dict[int, list[PrefixEvent]] = {}
    start_user = int(spec.partitions["train"]["start_user_id"])
    for _, trajectory_ordinal, record, _ in _iter_records_with_adjudicator(design, spec):
        user_id = start_user + int(trajectory_ordinal)
        if not 0 <= user_id <= 799:
            raise ValueError(f"S3d PART 0 prefix measurement touched forbidden user_id {user_id}")
        by_user.setdefault(user_id, []).append(event_from_mapping(record))
    missing = [user_id for user_id in range(0, 800) if user_id not in by_user]
    if missing:
        raise RuntimeError(f"missing generated users in S3d cert-set measurement: {missing[:5]}")
    return by_user


def _measure_bootstrap_unit() -> dict[str, Any]:
    start = time.perf_counter()
    rng = np.random.default_rng(20260718)
    per_user_hits = rng.binomial(300, 0.5, size=160) / 300.0
    resampled = []
    for _ in range(1000):
        indices = rng.integers(0, len(per_user_hits), size=len(per_user_hits))
        resampled.append(float(np.mean(per_user_hits[indices])))
    ci = [float(np.percentile(resampled, 2.5)), float(np.percentile(resampled, 97.5))]
    seconds = time.perf_counter() - start
    return {
        "unit": "1000_resamples_over_160_eval_users_one_member_cell",
        "bootstrap_resamples": 1000,
        "eval_users": 160,
        "ci95": ci,
        "wall_clock_seconds": seconds,
        "producer_function": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_projection_runner.py::_measure_bootstrap_unit",
    }


def _project_total(initial: Mapping[str, Any], measurements: Mapping[str, Any]) -> dict[str, Any]:
    generation_seconds = float(initial["measurements"]["cert_set_generation"]["wall_clock_seconds"])
    ideal_one_user_seconds = float(initial["measurements"]["ideal_per_user_one_cell"]["wall_clock_seconds"])
    components: dict[str, Any] = {}

    def add(name: str, seconds: float, units: float, note: str, *, null_units: float = 0.0) -> None:
        projected = float(seconds) * float(units)
        components[name] = {
            "measured_seconds": float(seconds),
            "projected_units": float(units),
            "projected_seconds": projected,
            "projected_cpu_hours": projected / 3600.0,
            "null_env_units_included": float(null_units),
            "note": note,
        }

    add("generation_all_7_cert_sets", generation_seconds, 7.0, "one measured cert-set generation x 7 S3d cells", null_units=1.0)
    add(
        "ideal_all_7_cells_160_eval_users",
        ideal_one_user_seconds,
        7.0 * 160.0,
        "one measured S2 ideal eval user x 160 eval users x 7 cells including NULL_env",
        null_units=160.0,
    )
    add(
        "logreg_F1_selected_cert_plus_NULL",
        float(measurements["logreg_F1_selected"]["fit_plus_validation_wall_clock_seconds"]),
        2.0,
        "obs_decoder_logreg selected F1 config on camouflage_off plus NULL_env",
        null_units=1.0,
    )
    add(
        "logreg_F2_reference_measured_not_counted",
        float(measurements["logreg_F2_reference"]["fit_plus_validation_wall_clock_seconds"]),
        0.0,
        "measured because PART 0 names F1/F2; not counted because selected logreg recipe is F1",
    )
    add(
        "gbt_half_data_selected_cert_plus_NULL",
        float(measurements["gbt_half_data_selected"]["fit_plus_validation_wall_clock_seconds"]),
        2.0,
        "obs_decoder_gbt selected F2 half-data config on camouflage_off plus NULL_env",
        null_units=1.0,
    )
    add(
        "gru_selected_cert_plus_NULL",
        float(measurements["gru_selected"]["fit_plus_validation_wall_clock_seconds"]),
        2.0,
        "obs_decoder_gru selected config on camouflage_off plus NULL_env",
        null_units=1.0,
    )
    add(
        "seq_full_selected_cert_plus_NULL",
        float(measurements["seq_full_selected"]["fit_plus_validation_wall_clock_seconds"]),
        2.0,
        "seq_full selected config on constant_none plus NULL_env",
        null_units=1.0,
    )
    add(
        "seq_W15_selected_cert_plus_NULL",
        float(measurements["seq_W15_selected"]["fit_plus_validation_wall_clock_seconds"]),
        2.0,
        "seq_W15 selected config on low_diversity plus NULL_env",
        null_units=1.0,
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
            measured = measurements[family_name]["members"][member]["projected_one_member_cell_seconds"]
            add(
                f"{family_name}_{member}_cert_plus_NULL",
                measured,
                units,
                f"{member}: projected one member-cell x favorable cert cell plus NULL_env",
                null_units=1.0,
            )

    add(
        "bootstrap_18_certificate_member_rows",
        float(measurements["bootstrap"]["wall_clock_seconds"]),
        18.0,
        "rho bootstrap CI for 18 certificate member rows; NULL table has no rho CI",
    )
    total_seconds = float(sum(item["projected_seconds"] for item in components.values()))
    null_seconds = float(
        sum(
            item["measured_seconds"] * item["null_env_units_included"]
            for item in components.values()
            if item["null_env_units_included"]
        )
    )
    return {
        "cpu_hour_limit": S3D_CPU_HOUR_LIMIT,
        "components": components,
        "total_projected_seconds": total_seconds,
        "total_projected_cpu_hours": total_seconds / 3600.0,
        "null_env_projected_seconds_included": null_seconds,
        "null_env_projected_cpu_hours_included": null_seconds / 3600.0,
        "linear_projection_assumptions": [
            "cert-set generation scales linearly across the 7 S3d cells",
            "S2 ideal cost scales from one eval user to 160 eval users per cell across 7 cells",
            "sklearn/GRU selected-recipe measurements are one full fit+validation member-cell units",
            "prefix-family measurements are fit_640 plus one eval user scoring, scaled to 160 eval users per member-cell",
            "each measured member-cell is counted once for its favorable certificate cell and once for NULL_env",
            "logreg_F2 is measured for named PART 0 coverage but not counted because the banked selected logreg recipe is F1",
        ],
    }


def _single_thread_environment() -> dict[str, Any]:
    for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[key] = "1"
    env = obs_decoders.configure_s3c_single_thread_cpu_environment()
    env["env_threads"] = {
        key: os.environ.get(key, "")
        for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS")
    }
    env["single_thread_accounting"] = True
    return env


def _selected_recipe_paths() -> dict[str, Path]:
    return {
        "obs_decoder_logreg": ARTIFACT_ROOT / "s3c_models" / "obs_decoder_logreg_selected_recipe.json",
        "obs_decoder_gbt": ARTIFACT_ROOT / "s3c_models" / "obs_decoder_gbt_selected_recipe.json",
        "obs_decoder_gru": ARTIFACT_ROOT / "s3c_models" / "obs_decoder_gru_selected_recipe.json",
        "seq_full_history_no_action_conditioning": ARTIFACT_ROOT
        / "s3c_models"
        / "seq_full_history_no_action_conditioning_selected_recipe.json",
        "seq_window_with_action_conditioning_W15_no_cross_session_persistence": ARTIFACT_ROOT
        / "s3c_models"
        / "seq_window_with_action_conditioning_W15_no_cross_session_persistence_selected_recipe.json",
    }


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


def _failure_manifest(verdict: str, payload: Mapping[str, Any], stop_condition: str) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "stage": "S3d",
        "artifact": "s3d_part0_projection_failure_manifest",
        "verdict": verdict,
        "stop_condition": stop_condition,
        "preserved_failure": True,
        "payload_artifact": payload.get("artifact"),
        "payload_decision": payload.get("decision") or payload.get("verdict"),
        "claim_ceiling": (
            "S3d PART 0 STOP/failure boundary only; no certificate, NULL, environment-validity, "
            "baseline-power, gap, mechanism, learning-capability, agency, or EGO claim"
        ),
        "producer_function": (
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_projection_runner.py::_failure_manifest"
        ),
        "code_path_hash": _code_path_hash(),
        "run_started_at": _utc_timestamp(),
        "run_finished_at": _utc_timestamp(),
    }


def _sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _code_path_hash() -> str:
    paths = [
        Path(__file__),
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
    h = hashlib.sha256()
    for path in paths:
        h.update(str(path.relative_to(ROOT)).encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def main() -> int:
    try:
        if PROJECTION.exists() and not PREFIT_V1.exists():
            PREFIT_V1.write_bytes(PROJECTION.read_bytes())
        result = run_full_projection_extension()
        print(
            json.dumps(
                {
                    "projection_path": str(PROJECTION.relative_to(ROOT)),
                    "prefit_v1_path": str(PREFIT_V1.relative_to(ROOT)),
                    "decision": result.get("decision"),
                    "projection_total_cpu_hours": result.get("projection_total_cpu_hours"),
                    "cpu_hour_limit": result.get("cpu_hour_limit"),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except Exception as exc:
        payload = {
            "artifact": "s3d_compute_projection",
            "decision": "STOP_s3d_part0_projection_runner_exception",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        _write_json(
            FAILURE_MANIFEST,
            _failure_manifest(
                "STOP_s3d_part0_projection_runner_exception",
                payload,
                "PART 0 projection runner raised before a complete projection could be emitted",
            ),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
