"""S3c observation-decoder battery members and compute projection helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import inspect
import json
from pathlib import Path
import time
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from scipy import sparse
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
TRAIN_FIT_USER_MAX = 639
INTERNAL_VALIDATION_USER_MIN = 640
TRAIN_USER_MAX = 799


@dataclass
class _PrefixFeatureState:
    alphabet_size: int
    prefix_len: int = 0
    counts: np.ndarray = field(init=False)
    session_counts: np.ndarray = field(init=False)
    transitions: dict[tuple[int, int], int] = field(default_factory=dict)
    last_symbol: int | None = None

    def __post_init__(self) -> None:
        self.counts = np.zeros(self.alphabet_size, dtype=np.float64)
        self.session_counts = np.zeros(self.alphabet_size, dtype=np.float64)

    def observe(self, event: PrefixEvent) -> None:
        symbol = int(event.observation["symbol"])
        if event.session_boundary == "start":
            self.session_counts = np.zeros(self.alphabet_size, dtype=np.float64)
            self.last_symbol = None
        if self.last_symbol is not None:
            key = (int(self.last_symbol), symbol)
            self.transitions[key] = self.transitions.get(key, 0) + 1
        self.counts[symbol] += 1.0
        self.session_counts[symbol] += 1.0
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
    ngram_dimension = alphabet_size + alphabet_size * alphabet_size + alphabet_size**3
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
                "within_session_ngram_counts_n_le_3",
            ],
            "dimension": int(f1_dimension + ngram_dimension),
            "ngram_dimension": int(ngram_dimension),
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


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
