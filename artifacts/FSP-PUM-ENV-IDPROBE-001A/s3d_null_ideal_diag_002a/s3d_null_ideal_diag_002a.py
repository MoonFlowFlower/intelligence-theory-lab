"""S3D-NULL-IDEAL-DIAG-002A real-cell style-map privilege diagnostic.

Artifact-local only.  Reuses the 001A diagnostic harness functions for
trajectory loading, exact-filter construction, style-map derangement, metrics,
JSON hygiene, and source hashing.  It does not edit source, specs, the S3d
runner, or existing banked/void artifacts.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
from itertools import product
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Mapping, Sequence

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from src.fsp_pum_env.factored_filter import _peaked_distribution
from src.fsp_pum_env.ideal_observer import PrefixEvent, ThetaGridSpec, make_z_quadrature
from src.fsp_pum_env.s3d_certificates import NULL_MARGIN, build_s3d_cert_set_specs
from src.fsp_pum_env.simulator import FspPumSimulator, SimulatorVariant
from src.fsp_pum_env.trajectory_sets import load_frozen_design


TASK_ID = "S3D-NULL-IDEAL-DIAG-002A"
ARTIFACT_ROOT = ROOT / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A"
OUT_DIR = ARTIFACT_ROOT / "s3d_null_ideal_diag_002a"
HARNESS_001A = ARTIFACT_ROOT / "s3d_null_ideal_diag_001a" / "s3d_null_ideal_diag_001a.py"
FROZEN_DESIGN = ARTIFACT_ROOT / "frozen_design.json"
VOID_TRACE = ARTIFACT_ROOT / "trace_void_line30_v1.jsonl"
RUNNER = ARTIFACT_ROOT / "s3d_battery_runner_line30.py"
TASK_CARD = OUT_DIR / "task_card.md"
COLLISION_RECORD = OUT_DIR / "collision_record.md"
RESULT_PATH = OUT_DIR / "result.json"
TRACE_PATH = OUT_DIR / "trace.jsonl"
PER_USER_SUPPORT_CSV = OUT_DIR / "per_user_support.csv"
FINDINGS_PATH = OUT_DIR / "findings.md"
FAILURE_MANIFEST = OUT_DIR / "failure_manifest.json"

CHANCE = 1.0 / 32.0
NULL_LIMIT = CHANCE + NULL_MARGIN
REQUESTED_CELLS = ("low_diversity", "flat_theta")
EVAL_USERS = tuple(range(640, 800))
HEADROOM_RETENTION_NULL_LOCAL_MIN = 0.80

ASSIGNED_MEMBERS_BY_CELL: dict[str, tuple[str, ...]] = {
    "low_diversity": (
        "seq_window_with_action_conditioning_W15_no_cross_session_persistence",
        "successor_map",
        "transition_table",
        "count_table",
        "fsm_planner",
        "episodic_traversal",
        "nearest_neighbor_user_matching",
    ),
    "flat_theta": (
        "discounted_LS_lambda_0.95",
        "running_average_preference_regressor",
    ),
}


def _load_001a_harness() -> Any:
    spec = importlib.util.spec_from_file_location("s3d_null_ideal_diag_001a_reuse", HARNESS_001A)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot_load_001a_harness:{HARNESS_001A}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


HARNESS = _load_001a_harness()


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _jsonable(value: Any) -> Any:
    return HARNESS._jsonable(value)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _sha256_json(payload: Any) -> str:
    return HARNESS._sha256_json(payload)


def _write_json_roundtrip(path: Path, payload: Mapping[str, Any]) -> None:
    HARNESS._write_json_roundtrip(path, payload)


def _write_text(path: Path, text: str) -> None:
    HARNESS._write_text(path, text)


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _input_ref(path: Path) -> dict[str, Any]:
    return {
        "path": _relative(path),
        "sha256": _sha256_path(path),
        "bytes": int(path.stat().st_size),
    }


def _code_path_hash() -> str:
    paths = [
        Path(__file__),
        HARNESS_001A,
        ROOT / "src" / "fsp_pum_env" / "factored_filter.py",
        ROOT / "src" / "fsp_pum_env" / "simulator.py",
        ROOT / "src" / "fsp_pum_env" / "s3d_certificates.py",
        ROOT / "src" / "fsp_pum_env" / "trajectory_sets.py",
        ROOT / "src" / "fsp_pum_env" / "ideal_observer.py",
    ]
    h = hashlib.sha256()
    for path in paths:
        h.update(_relative(path).encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _safe_metric(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _headroom_retention(g1_metric: float, g2_metric: float) -> float:
    denom = float(g1_metric - CHANCE)
    if denom <= 0.0:
        return math.nan
    return float((g2_metric - CHANCE) / denom)


class _CollapsedTrustOracle:
    """Exact collapsed oracle for low_diversity and flat_theta cert cells.

    For these two requested variants the distribution tables in
    `FactoredExactFilter` are independent of non-trust theta coordinates.  This
    collapses the full 7,077,888-atom posterior to the trust-parameter marginal
    while preserving the same action-conditioned predictive/update equations.
    The G1 reproduction gate against the void exact-filter metrics is the
    admissibility check for this artifact-local acceleration.
    """

    def __init__(
        self,
        design: Mapping[str, Any],
        *,
        master_seed: int,
        variant: str,
        style_map: Sequence[int],
    ) -> None:
        self.design = design
        self.variant = SimulatorVariant(variant)
        if self.variant not in {
            SimulatorVariant.GRAPH_CACHE_SHOULD_WIN_LOW_DIVERSITY_TEMPLATES,
            SimulatorVariant.FLAT_THETA,
        }:
            raise ValueError(f"collapsed oracle does not support variant:{self.variant.value}")
        self.simulator = FspPumSimulator(design, master_seed=int(master_seed), variant=self.variant)
        self.alphabet_size = int(self.simulator.alphabet_size)
        self.style_map = self._validate_style_map(style_map)
        grid_spec = ThetaGridSpec.from_design(design)
        trust_params = list(product(grid_spec.alpha_levels, grid_spec.beta_levels, grid_spec.disclosure_levels))
        self.trust_alpha = np.asarray([item[0] for item in trust_params], dtype=np.float64)
        self.trust_beta = np.asarray([item[1] for item in trust_params], dtype=np.float64)
        self.trust_d = np.asarray([item[2] for item in trust_params], dtype=np.float64)
        self.trust_values = np.full(
            len(trust_params),
            float(design["env_parameters"]["trust_dynamics"]["init"]),
            dtype=np.float64,
        )
        self._initial_log_weight = -math.log(len(trust_params))
        self.log_weights = np.full(len(trust_params), self._initial_log_weight, dtype=np.float64)
        self.z_quadrature = make_z_quadrature(design, 3)
        self._table_cache: dict[str, np.ndarray] = {}

    def _validate_style_map(self, style_map: Sequence[int]) -> tuple[int, ...]:
        values = tuple(int(value) for value in style_map)
        if len(values) != self.alphabet_size or sorted(values) != list(range(self.alphabet_size)):
            raise ValueError("invalid style_map for collapsed oracle")
        return values

    @property
    def state_count(self) -> int:
        return int(self.log_weights.size)

    def array_bytes(self) -> int:
        return int(
            self.log_weights.nbytes
            + self.trust_values.nbytes
            + self.trust_alpha.nbytes
            + self.trust_beta.nbytes
            + self.trust_d.nbytes
        )

    def _weights(self) -> np.ndarray:
        shifted = self.log_weights - float(np.max(self.log_weights))
        weights = np.exp(shifted)
        total = float(weights.sum())
        if total <= 0.0:
            raise ValueError("collapsed posterior has zero mass")
        return weights / total

    def _apply_low_trust(self, distribution: np.ndarray) -> np.ndarray:
        threshold = np.maximum(self.trust_d, 1e-12)
        weight = np.maximum((threshold - self.trust_values) / threshold, 0.0)
        shape = (len(self.trust_values),) + (1,) * (distribution.ndim - 1)
        trust_weight = weight.reshape(shape)
        uniform = np.full_like(distribution, 1.0 / self.alphabet_size, dtype=np.float64)
        return (1.0 - trust_weight) * distribution + trust_weight * uniform

    def _apply_style_map(self, distribution: np.ndarray) -> np.ndarray:
        out = np.empty_like(distribution)
        out[:, np.asarray(self.style_map, dtype=np.int32)] = distribution
        return out

    def _advance_trust(self, action: str) -> None:
        cost = self.simulator._probe_trust_cost(action)
        if cost > 0.0:
            next_trust = self.trust_beta * self.trust_values - cost
        else:
            next_trust = self.trust_beta * self.trust_values + self.trust_alpha * (1.0 - self.trust_values)
        self.trust_values = np.clip(next_trust, 0.0, 1.0)
        self._table_cache.clear()

    def _distribution_table(self, action: str) -> np.ndarray:
        cached = self._table_cache.get(action)
        if cached is not None:
            return cached
        self.simulator._validate_action(action)
        if self.variant is SimulatorVariant.GRAPH_CACHE_SHOULD_WIN_LOW_DIVERSITY_TEMPLATES:
            table = self._low_diversity_table(action)
        elif self.variant is SimulatorVariant.FLAT_THETA:
            table = self._flat_theta_table(action)
        else:
            raise ValueError(f"unsupported collapsed variant:{self.variant.value}")
        self._table_cache[action] = table
        return table

    def _low_diversity_table(self, action: str) -> np.ndarray:
        if action in self.simulator.probe_actions:
            center = 4
        elif action in self.simulator.recommend_actions:
            center = 8
        else:
            center = int(action.rsplit("_", 1)[1]) % 2
        rows = len(self.trust_values)
        base = _peaked_distribution(
            np.full(rows, center, dtype=np.int32),
            np.full(rows, 3.0, dtype=np.float64),
            self.alphabet_size,
        )
        return self._apply_style_map(self._apply_low_trust(base))

    def _flat_theta_table(self, action: str) -> np.ndarray:
        if action in self.simulator.probe_actions:
            return self._flat_theta_probe_table(action)
        if action in self.simulator.task_actions:
            return self._flat_theta_task_table(action)
        if action in self.simulator.recommend_actions:
            return self._flat_theta_recommend_table()
        raise ValueError(f"unknown action:{action}")

    def _flat_theta_probe_table(self, action: str) -> np.ndarray:
        topic0_level = int(self.simulator._topic_level_index(0.0))
        if action == "probe_0":
            center = 2
            strength = 2.7
        elif action == "probe_1":
            center = 6
            strength = 2.7
        elif action == "probe_2":
            center = 10 + topic0_level
            strength = 2.9
        else:
            center = 16 + (topic0_level % 8)
            strength = 1.75
        rows = len(self.trust_values)
        base = _peaked_distribution(
            np.full(rows, center, dtype=np.int32),
            np.full(rows, strength, dtype=np.float64),
            self.alphabet_size,
        )
        return self._apply_style_map(self._apply_low_trust(base))

    def _flat_theta_task_table(self, action: str) -> np.ndarray:
        topic_index = int(action.rsplit("_", 1)[1])
        z_valence = np.asarray([node[0] for node in self.z_quadrature.nodes], dtype=np.float64)
        z_stress = np.asarray([node[2] for node in self.z_quadrature.nodes], dtype=np.float64)
        z_term = 0.35 * z_valence - 0.15 * z_stress
        center = (topic_index * 3 + 8) % self.alphabet_size
        return self._flat_theta_z_marginal_table(center=center, base_strength=1.35, z_term=z_term)

    def _flat_theta_recommend_table(self) -> np.ndarray:
        z_valence = np.asarray([node[0] for node in self.z_quadrature.nodes], dtype=np.float64)
        z_arousal = np.asarray([node[1] for node in self.z_quadrature.nodes], dtype=np.float64)
        z_term = 0.2 * z_valence + 0.1 * z_arousal
        return self._flat_theta_z_marginal_table(center=13 % self.alphabet_size, base_strength=1.1, z_term=z_term)

    def _flat_theta_z_marginal_table(self, *, center: int, base_strength: float, z_term: np.ndarray) -> np.ndarray:
        trust_count = len(self.trust_values)
        z_count = len(z_term)
        rows = trust_count * z_count
        base = _peaked_distribution(
            np.full(rows, int(center), dtype=np.int32),
            np.full(rows, float(base_strength), dtype=np.float64) + np.tile(z_term, trust_count),
            self.alphabet_size,
        ).reshape(trust_count, z_count, self.alphabet_size)
        degraded = self._apply_low_trust(base)
        weights = np.asarray(self.z_quadrature.weights, dtype=np.float64)
        marginalized = np.tensordot(degraded, weights, axes=([1], [0]))
        return self._apply_style_map(marginalized)

    def predict_distribution(self, action: str) -> list[float]:
        table = self._distribution_table(action)
        mixture = self._weights() @ table
        total = float(mixture.sum())
        if total <= 0.0:
            raise ValueError("collapsed posterior predictive has zero mass")
        return (mixture / total).tolist()

    def observe(self, action: str, symbol: int) -> None:
        if not 0 <= int(symbol) < self.alphabet_size:
            raise ValueError(f"symbol outside response alphabet:{symbol}")
        table = self._distribution_table(action)
        self.log_weights += np.log(np.maximum(table[:, int(symbol)], 1e-300))
        self._advance_trust(action)


def _score_ideal_cell_style(
    design: Mapping[str, Any],
    spec: Any,
    *,
    style_variant: str,
    test_id: str,
    trace_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    start = time.perf_counter()
    rows: list[dict[str, Any]] = []
    collapsed_state_count = None
    array_bytes = None
    style_map_digests: dict[str, str] = {}
    if style_variant not in {"true", "wrong_derangement"}:
        raise ValueError(f"unknown_style_variant:{style_variant}")
    for user_id in EVAL_USERS:
        if 800 <= int(user_id) <= 999:
            raise RuntimeError(f"heldout_user_forbidden:{user_id}")
        user = HARNESS._load_user_data(design, spec, int(user_id))
        style_map = user.style_map if style_variant == "true" else HARNESS._wrong_style_map(user.style_map)
        style_map_digests[str(user.user_id)] = _sha256_json(style_map)
        oracle = _CollapsedTrustOracle(
            design,
            master_seed=int(spec.master_seed),
            variant=str(spec.variant),
            style_map=style_map,
        )
        collapsed_state_count = int(oracle.state_count)
        array_bytes = int(oracle.array_bytes())
        for record in user.records:
            action = str(record["action"])
            distribution = oracle.predict_distribution(action)
            prediction = int(np.argmax(np.asarray(distribution, dtype=float)))
            target = int(record["observation"]["symbol"])
            row = {
                "test_id": test_id,
                "cell_id": str(spec.cell_id),
                "style_variant": style_variant,
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
            oracle.observe(action, target)
    return {
        "test_id": test_id,
        "producer_function": "s3d_null_ideal_diag_002a._score_ideal_cell_style",
        "oracle_implementation": "collapsed_trust_exact_for_low_diversity_and_flat_theta",
        "equivalence_admissibility_gate": "G1 true-style must reproduce trace_void_line30_v1 exact-filter ideal metric within abs_tol=1e-12",
        "reused_harness": _relative(HARNESS_001A),
        "cell_id": str(spec.cell_id),
        "variant": str(spec.variant),
        "style_variant": style_variant,
        "input_artifacts": [_relative(FROZEN_DESIGN)],
        "run_user_ids": [int(user_id) for user_id in EVAL_USERS],
        "seed_contexts": [
            f"independent_filter_seed({int(spec.master_seed)}, s3d_battery:{spec.cell_id}:{int(user_id)})"
            for user_id in EVAL_USERS
        ],
        "episode_ids": [
            {"user_id": int(user_id), "turns": 300, "step_index_range": [0, 299]}
            for user_id in EVAL_USERS
        ],
        "scope_metrics": HARNESS._scope_metrics(rows),
        "per_user_metrics": HARNESS._per_user_metrics(rows),
        "digests": HARNESS._result_digest(rows),
        "style_map_sha256_by_user": style_map_digests,
        "collapsed_state_count": collapsed_state_count,
        "posterior_array_bytes": array_bytes,
        "wall_clock_seconds": time.perf_counter() - start,
    }


def _load_void_reference_rows() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    with VOID_TRACE.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    ideal_by_cell: dict[str, dict[str, Any]] = {}
    member_rows_by_cell: dict[str, list[dict[str, Any]]] = {cell: [] for cell in REQUESTED_CELLS}
    for row in rows:
        cell = str(row.get("cell_id", ""))
        if cell not in REQUESTED_CELLS:
            continue
        if str(row.get("unit_type")) == "ideal":
            ideal_by_cell[cell] = row
        elif str(row.get("unit_type")) == "member":
            member = str(row.get("member"))
            if member in ASSIGNED_MEMBERS_BY_CELL[cell]:
                member_rows_by_cell[cell].append(row)

    per_cell: dict[str, dict[str, Any]] = {}
    for cell in REQUESTED_CELLS:
        available = sorted(member_rows_by_cell[cell], key=lambda item: str(item.get("member")))
        missing = [
            member for member in ASSIGNED_MEMBERS_BY_CELL[cell]
            if member not in {str(row.get("member")) for row in available}
        ]
        primary = None
        if available:
            primary = max(available, key=lambda item: float(item.get("metric", -math.inf)))
        per_cell[cell] = {
            "cell_id": cell,
            "void_ideal_row": ideal_by_cell.get(cell),
            "assigned_members": list(ASSIGNED_MEMBERS_BY_CELL[cell]),
            "available_void_reference_rows": available,
            "missing_assigned_members_in_void_trace": missing,
            "primary_g3_selection_rule": (
                "max metric among assigned should-win members available in trace_void_line30_v1.jsonl; "
                "void/reference-only, not a fresh 002A member run"
            ),
            "primary_g3_reference": primary,
        }
    return {
        "producer_function": "s3d_null_ideal_diag_002a._load_void_reference_rows",
        "input_artifacts": [_relative(VOID_TRACE)],
        "void_trace_sha256": _sha256_path(VOID_TRACE),
        "void_trace_row_count": len(rows),
        "per_cell": per_cell,
    }


def _g1_reproduction_gate(g1_by_cell: Mapping[str, Mapping[str, Any]], void_refs: Mapping[str, Any]) -> dict[str, Any]:
    rows = []
    passed = True
    for cell in REQUESTED_CELLS:
        g1_metric = float(g1_by_cell[cell]["scope_metrics"]["overall"]["metric"])
        void_row = void_refs["per_cell"][cell].get("void_ideal_row")
        void_metric = None if void_row is None else float(void_row["metric"])
        match = void_metric is not None and math.isclose(g1_metric, void_metric, rel_tol=0.0, abs_tol=1e-12)
        rows.append(
            {
                "cell_id": cell,
                "g1_true_style_metric": g1_metric,
                "void_trace_ideal_metric": void_metric,
                "abs_delta": None if void_metric is None else float(g1_metric - void_metric),
                "matched_within_abs_tol_1e_12": bool(match),
            }
        )
        passed = bool(passed and match)
    return {
        "producer_function": "s3d_null_ideal_diag_002a._g1_reproduction_gate",
        "passed": passed,
        "rows": rows,
    }


def _spot_check_collapsed_vs_full_atom(design: Mapping[str, Any], specs: Mapping[str, Any]) -> dict[str, Any]:
    """Check collapsed acceleration against full FactoredExactFilter on one eval user.

    This is not the headline metric path; it is an equivalence guard for both true
    and wrong style on the requested cells after the full-range G1 reproduction
    gate has made the aggregate exactness check.
    """

    rows = []
    passed = True
    for cell in REQUESTED_CELLS:
        spec = specs[cell]
        user = HARNESS._load_user_data(design, spec, 640)
        for style_variant in ("true", "wrong_derangement"):
            style_map = user.style_map if style_variant == "true" else HARNESS._wrong_style_map(user.style_map)
            full = HARNESS._filter_for_user(design, spec, user.user_id, style_map)
            collapsed = _CollapsedTrustOracle(
                design,
                master_seed=int(spec.master_seed),
                variant=str(spec.variant),
                style_map=style_map,
            )
            max_abs_diff = 0.0
            prediction_mismatches = 0
            full_rows = []
            collapsed_rows = []
            for record in user.records:
                action = str(record["action"])
                target = int(record["observation"]["symbol"])
                full_dist = full.predict_distribution(action)
                collapsed_dist = collapsed.predict_distribution(action)
                max_abs_diff = max(
                    max_abs_diff,
                    float(np.max(np.abs(np.asarray(full_dist, dtype=float) - np.asarray(collapsed_dist, dtype=float)))),
                )
                full_pred = int(np.argmax(np.asarray(full_dist, dtype=float)))
                collapsed_pred = int(np.argmax(np.asarray(collapsed_dist, dtype=float)))
                prediction_mismatches += int(full_pred != collapsed_pred)
                full_rows.append({"user_id": 640, "step_index": int(record["step_index"]), "action": action, "prediction": full_pred, "target": target})
                collapsed_rows.append({"user_id": 640, "step_index": int(record["step_index"]), "action": action, "prediction": collapsed_pred, "target": target})
                full.observe(PrefixEvent(action=action, symbol=target))
                collapsed.observe(action, target)
            full_metrics = HARNESS._scope_metrics(full_rows)
            collapsed_metrics = HARNESS._scope_metrics(collapsed_rows)
            row_passed = bool(max_abs_diff <= 1e-12 and prediction_mismatches == 0)
            rows.append(
                {
                    "cell_id": cell,
                    "style_variant": style_variant,
                    "user_id": 640,
                    "max_distribution_abs_diff": max_abs_diff,
                    "prediction_mismatches": int(prediction_mismatches),
                    "full_atom_overall_metric": full_metrics["overall"]["metric"],
                    "collapsed_overall_metric": collapsed_metrics["overall"]["metric"],
                    "full_atom_recommend_metric": full_metrics["recommend_turn_conditional"]["metric"],
                    "collapsed_recommend_metric": collapsed_metrics["recommend_turn_conditional"]["metric"],
                    "passed": row_passed,
                }
            )
            passed = bool(passed and row_passed)
    return {
        "producer_function": "s3d_null_ideal_diag_002a._spot_check_collapsed_vs_full_atom",
        "scope": "eval user 640, both requested cells, both true and wrong style",
        "passed": passed,
        "rows": rows,
    }


def _per_user_support_rows(results_by_cell: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for cell in REQUESTED_CELLS:
        g1_users = {
            int(item["user_id"]): item
            for item in results_by_cell[cell]["G1_true_style"]["per_user_metrics"]
        }
        g2_users = {
            int(item["user_id"]): item
            for item in results_by_cell[cell]["G2_wrong_style"]["per_user_metrics"]
        }
        for user_id in EVAL_USERS:
            g1 = g1_users[int(user_id)]["scope_metrics"]
            g2 = g2_users[int(user_id)]["scope_metrics"]
            g1_overall = float(g1["overall"]["metric"])
            g2_overall = float(g2["overall"]["metric"])
            g1_rec = _safe_metric(g1["recommend_turn_conditional"]["metric"])
            g2_rec = _safe_metric(g2["recommend_turn_conditional"]["metric"])
            out.append(
                {
                    "cell_id": cell,
                    "user_id": int(user_id),
                    "g1_overall_metric": g1_overall,
                    "g2_overall_metric": g2_overall,
                    "overall_delta_g2_minus_g1": float(g2_overall - g1_overall),
                    "overall_headroom_retention": _headroom_retention(g1_overall, g2_overall),
                    "g1_overall_n_eval_points": int(g1["overall"]["n_eval_points"]),
                    "g2_overall_n_eval_points": int(g2["overall"]["n_eval_points"]),
                    "g1_overall_class_count_present": int(g1["overall"]["class_count_present"]),
                    "g2_overall_class_count_present": int(g2["overall"]["class_count_present"]),
                    "g1_recommend_metric": g1_rec,
                    "g2_recommend_metric": g2_rec,
                    "recommend_delta_g2_minus_g1": None if g1_rec is None or g2_rec is None else float(g2_rec - g1_rec),
                    "recommend_headroom_retention": None
                    if g1_rec is None or g2_rec is None
                    else _headroom_retention(g1_rec, g2_rec),
                    "g1_recommend_n_eval_points": int(g1["recommend_turn_conditional"]["n_eval_points"]),
                    "g2_recommend_n_eval_points": int(g2["recommend_turn_conditional"]["n_eval_points"]),
                    "g1_recommend_class_count_present": int(g1["recommend_turn_conditional"]["class_count_present"]),
                    "g2_recommend_class_count_present": int(g2["recommend_turn_conditional"]["class_count_present"]),
                }
            )
    return out


def _write_per_user_support_csv(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    fieldnames = [
        "cell_id",
        "user_id",
        "g1_overall_metric",
        "g2_overall_metric",
        "overall_delta_g2_minus_g1",
        "overall_headroom_retention",
        "g1_overall_n_eval_points",
        "g2_overall_n_eval_points",
        "g1_overall_class_count_present",
        "g2_overall_class_count_present",
        "g1_recommend_metric",
        "g2_recommend_metric",
        "recommend_delta_g2_minus_g1",
        "recommend_headroom_retention",
        "g1_recommend_n_eval_points",
        "g2_recommend_n_eval_points",
        "g1_recommend_class_count_present",
        "g2_recommend_class_count_present",
    ]
    PER_USER_SUPPORT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with PER_USER_SUPPORT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})
    return {
        "path": _relative(PER_USER_SUPPORT_CSV),
        "row_count": len(rows),
        "sha256": _sha256_path(PER_USER_SUPPORT_CSV),
    }


def _support_summary(per_user_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for cell in REQUESTED_CELLS:
        subset = [row for row in per_user_rows if str(row["cell_id"]) == cell]
        overall_retentions = [float(row["overall_headroom_retention"]) for row in subset if math.isfinite(float(row["overall_headroom_retention"]))]
        recommend_retentions = [
            float(row["recommend_headroom_retention"])
            for row in subset
            if row.get("recommend_headroom_retention") not in (None, "")
            and math.isfinite(float(row["recommend_headroom_retention"]))
        ]
        summary[cell] = {
            "user_count": len(subset),
            "overall_headroom_retention_min": None if not overall_retentions else float(np.min(overall_retentions)),
            "overall_headroom_retention_median": None if not overall_retentions else float(np.median(overall_retentions)),
            "overall_headroom_retention_max": None if not overall_retentions else float(np.max(overall_retentions)),
            "recommend_headroom_retention_min": None if not recommend_retentions else float(np.min(recommend_retentions)),
            "recommend_headroom_retention_median": None if not recommend_retentions else float(np.median(recommend_retentions)),
            "recommend_headroom_retention_max": None if not recommend_retentions else float(np.max(recommend_retentions)),
            "per_user_rows_in_csv": len(subset),
        }
    return summary


def _decide(results_by_cell: Mapping[str, Mapping[str, Any]], void_refs: Mapping[str, Any]) -> dict[str, Any]:
    rows = []
    null_local_cells = []
    rho_wide_cells = []
    for cell in REQUESTED_CELLS:
        g1 = results_by_cell[cell]["G1_true_style"]["scope_metrics"]
        g2 = results_by_cell[cell]["G2_wrong_style"]["scope_metrics"]
        g1_overall = float(g1["overall"]["metric"])
        g2_overall = float(g2["overall"]["metric"])
        retention = _headroom_retention(g1_overall, g2_overall)
        g3 = void_refs["per_cell"][cell].get("primary_g3_reference")
        g3_metric = None if g3 is None else float(g3["metric"])
        g3_vs_g1 = None if g3_metric is None else float(g3_metric / max(g1_overall, 1e-12))
        null_local = bool(math.isfinite(retention) and retention >= HEADROOM_RETENTION_NULL_LOCAL_MIN)
        rho_wide = bool(g2_overall <= NULL_LIMIT and g3_metric is not None and g3_metric < g1_overall)
        if null_local:
            null_local_cells.append(cell)
        if rho_wide:
            rho_wide_cells.append(cell)
        rows.append(
            {
                "cell_id": cell,
                "decision_metric_scope": "overall",
                "g1_true_style_overall": g1_overall,
                "g2_wrong_style_overall": g2_overall,
                "g2_minus_g1_overall": float(g2_overall - g1_overall),
                "overall_headroom_retention": retention,
                "g2_at_or_below_chance_plus_null_margin": bool(g2_overall <= NULL_LIMIT),
                "g1_recommend": g1["recommend_turn_conditional"]["metric"],
                "g2_recommend": g2["recommend_turn_conditional"]["metric"],
                "g3_primary_reference_member": None if g3 is None else str(g3["member"]),
                "g3_primary_reference_metric": g3_metric,
                "g3_metric_divided_by_g1_overall": g3_vs_g1,
                "g3_reference_source": None if g3 is None else "trace_void_line30_v1.jsonl",
                "null_local_cell_condition": null_local,
                "rho_wide_cell_condition": rho_wide,
            }
        )
    if len(null_local_cells) == len(REQUESTED_CELLS):
        verdict = "PRIVILEGE_NULL_LOCAL"
        branch = "G2 retained >=80% of G1 overall headroom in both requested real cells"
    elif len(rho_wide_cells) == len(REQUESTED_CELLS):
        verdict = "PRIVILEGE_RHO_WIDE"
        branch = "G2 collapsed to chance+margin in both requested real cells while G3 reference stayed below G1"
    else:
        verdict = "INCONCLUSIVE_MIXED_STYLEMAP_EFFECT"
        branch = "requested cells did not satisfy either pre-registered binary branch"
    return {
        "producer_function": "s3d_null_ideal_diag_002a._decide",
        "verdict": verdict,
        "decision_branch": branch,
        "decision_basis": (
            "overall macro-balanced accuracy for low_diversity and flat_theta; recommend-conditional metrics "
            "reported separately as support"
        ),
        "chance": CHANCE,
        "chance_plus_null_margin": NULL_LIMIT,
        "headroom_retention_null_local_min": HEADROOM_RETENTION_NULL_LOCAL_MIN,
        "rows": rows,
    }


def _findings_md(result: Mapping[str, Any]) -> str:
    decision = result["decision"]
    lines = [
        f"# {TASK_ID} findings",
        "",
        f"Verdict: `{decision['verdict']}`.",
        "",
        f"Decision branch: {decision['decision_branch']}.",
        "",
        "Decision basis: canonical overall macro-balanced accuracy for the two requested real cert cells. "
        "Recommend-conditional metrics are reported but do not decide these two cells.",
        "",
        "## Numbers",
        "",
        "| cell | G1 true overall | G2 wrong overall | G2-G1 | headroom retention | "
        "G1 recommend | G2 recommend | G3 reference member | G3 reference overall |",
        "|---|---:|---:|---:|---:|---:|---:|---|---:|",
    ]
    for row in decision["rows"]:
        g1_rec = row["g1_recommend"]
        g2_rec = row["g2_recommend"]
        lines.append(
            "| {cell} | {g1:.12f} | {g2:.12f} | {delta:.12f} | {ret:.6f} | "
            "{g1r} | {g2r} | {g3m} | {g3v} |".format(
                cell=row["cell_id"],
                g1=float(row["g1_true_style_overall"]),
                g2=float(row["g2_wrong_style_overall"]),
                delta=float(row["g2_minus_g1_overall"]),
                ret=float(row["overall_headroom_retention"]),
                g1r="None" if g1_rec is None else f"{float(g1_rec):.12f}",
                g2r="None" if g2_rec is None else f"{float(g2_rec):.12f}",
                g3m=row["g3_primary_reference_member"],
                g3v="None" if row["g3_primary_reference_metric"] is None else f"{float(row['g3_primary_reference_metric']):.12f}",
            )
        )
    lines.extend(
        [
            "",
            "## Reproduction gate",
            "",
            f"G1 reproduction passed: `{result['g1_reproduction_gate']['passed']}`.",
            "",
            "| cell | G1 true overall | void ideal overall | delta | match |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for row in result["g1_reproduction_gate"]["rows"]:
        lines.append(
            "| {cell} | {g1:.12f} | {void:.12f} | {delta:.3g} | {match} |".format(
                cell=row["cell_id"],
                g1=float(row["g1_true_style_metric"]),
                void=float(row["void_trace_ideal_metric"]),
                delta=float(row["abs_delta"]),
                match=row["matched_within_abs_tol_1e_12"],
            )
        )
    lines.extend(
        [
            "",
            "## Collapsed-oracle equivalence spot-check",
            "",
            f"Passed: `{result['collapsed_equivalence_spot_check']['passed']}` "
            f"({result['collapsed_equivalence_spot_check']['scope']}).",
            "",
            "| cell | style | max distribution diff | prediction mismatches |",
            "|---|---|---:|---:|",
        ]
    )
    for row in result["collapsed_equivalence_spot_check"]["rows"]:
        lines.append(
            "| {cell} | {style} | {diff:.3g} | {mismatch} |".format(
                cell=row["cell_id"],
                style=row["style_variant"],
                diff=float(row["max_distribution_abs_diff"]),
                mismatch=int(row["prediction_mismatches"]),
            )
        )
    lines.extend(
        [
            "",
            "## Per-user support",
            "",
            f"Per-user support CSV: `{result['per_user_support_csv']['path']}` "
            f"({result['per_user_support_csv']['row_count']} rows, sha256 "
            f"`{result['per_user_support_csv']['sha256']}`).",
            "",
            "| cell | users | overall retention min/median/max | recommend retention min/median/max |",
            "|---|---:|---|---|",
        ]
    )
    for cell, summary in result["per_user_support_summary"].items():
        def fmt_trip(prefix: str) -> str:
            mn = summary[f"{prefix}_min"]
            md = summary[f"{prefix}_median"]
            mx = summary[f"{prefix}_max"]
            if mn is None:
                return "None"
            return f"{float(mn):.6f} / {float(md):.6f} / {float(mx):.6f}"

        lines.append(
            f"| {cell} | {summary['user_count']} | "
            f"{fmt_trip('overall_headroom_retention')} | "
            f"{fmt_trip('recommend_headroom_retention')} |"
        )
    lines.extend(
        [
            "",
            "## G3 void/reference rows",
            "",
            "G3 is reference-only and was read from `trace_void_line30_v1.jsonl`; no member fix or fresh "
            "member adjudication is claimed here.",
            "",
        ]
    )
    for cell in REQUESTED_CELLS:
        ref = result["g3_void_reference"]["per_cell"][cell]
        missing = ref["missing_assigned_members_in_void_trace"]
        lines.append(f"### {cell}")
        lines.append("")
        lines.append(f"Missing assigned members in void trace: `{missing}`.")
        lines.append("")
        lines.append("| member | metric | recommend metric | unit_id |")
        lines.append("|---|---:|---:|---|")
        for row in ref["available_void_reference_rows"]:
            rec = row.get("recommend_turn_conditional_metric")
            lines.append(
                "| {member} | {metric:.12f} | {rec} | `{unit}` |".format(
                    member=row["member"],
                    metric=float(row["metric"]),
                    rec="None" if rec is None else f"{float(rec):.12f}",
                    unit=row["unit_id"],
                )
            )
        lines.append("")
    lines.extend(
        [
            "## Claim ceiling",
            "",
            result["claim_ceiling"],
            "",
            "What this does not prove: no S3d gate pass, no fix sufficiency beyond this diagnostic branch, "
            "no environment validity, no mechanism validity, no EGO mainline effect, no agency, no consciousness.",
        ]
    )
    return "\n".join(lines) + "\n"


def _failure_payload(run_started_at: str, stop_condition: str, details: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "run_id": f"{TASK_ID}:{run_started_at}",
        "verdict": "STOP_DIAGNOSTIC_FAILED",
        "stop_condition": stop_condition,
        "details": _jsonable(details),
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "claim_ceiling": (
            "failed artifact-local diagnostic only; no S3d, mechanism, integration, agency, or "
            "consciousness claim"
        ),
    }


def main() -> int:
    run_started_at = _utc_timestamp()
    wall_start = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    code_hash = _code_path_hash()
    try:
        design = load_frozen_design(FROZEN_DESIGN)
        specs = {spec.cell_id: spec for spec in build_s3d_cert_set_specs(design)}
        for cell in REQUESTED_CELLS:
            if cell not in specs:
                raise RuntimeError(f"requested_cell_not_found:{cell}")
        trace_rows: list[dict[str, Any]] = []
        results_by_cell: dict[str, dict[str, Any]] = {}
        for cell in REQUESTED_CELLS:
            g1 = _score_ideal_cell_style(
                design,
                specs[cell],
                style_variant="true",
                test_id=f"G1_true_style::{cell}",
                trace_rows=trace_rows,
            )
            g2 = _score_ideal_cell_style(
                design,
                specs[cell],
                style_variant="wrong_derangement",
                test_id=f"G2_wrong_style::{cell}",
                trace_rows=trace_rows,
            )
            results_by_cell[cell] = {
                "G1_true_style": g1,
                "G2_wrong_style": g2,
            }

        g3_void_reference = _load_void_reference_rows()
        reproduction_gate = _g1_reproduction_gate(
            {cell: results_by_cell[cell]["G1_true_style"] for cell in REQUESTED_CELLS},
            g3_void_reference,
        )
        collapsed_equivalence_spot_check = _spot_check_collapsed_vs_full_atom(design, specs)
        if not bool(reproduction_gate["passed"]):
            failure = _failure_payload(
                run_started_at,
                "G1_true_style_failed_to_reproduce_void_trace_ideal_metric",
                {"g1_reproduction_gate": reproduction_gate},
            )
            _write_json_roundtrip(FAILURE_MANIFEST, failure)
            print(json.dumps({"verdict": failure["verdict"], "failure_manifest": _relative(FAILURE_MANIFEST)}, sort_keys=True))
            return 2
        if not bool(collapsed_equivalence_spot_check["passed"]):
            failure = _failure_payload(
                run_started_at,
                "collapsed_oracle_failed_full_atom_spot_check",
                {"collapsed_equivalence_spot_check": collapsed_equivalence_spot_check},
            )
            _write_json_roundtrip(FAILURE_MANIFEST, failure)
            print(json.dumps({"verdict": failure["verdict"], "failure_manifest": _relative(FAILURE_MANIFEST)}, sort_keys=True))
            return 2

        per_user_rows = _per_user_support_rows(results_by_cell)
        per_user_csv = _write_per_user_support_csv(per_user_rows)
        per_user_summary = _support_summary(per_user_rows)
        decision = _decide(results_by_cell, g3_void_reference)

        with TRACE_PATH.open("w", encoding="utf-8", newline="\n") as handle:
            for row in trace_rows:
                handle.write(json.dumps(_jsonable(row), sort_keys=True, separators=(",", ":")) + "\n")

        result = {
            "task_id": TASK_ID,
            "layer": "engineering implementation + mechanism-instrument diagnostic",
            "mainline_integration_status": "none; artifact-local diagnostic only",
            "enabled_status": "manual diagnostic script executed; no runtime path enabled",
            "real_trigger_evidence": "callable 002A script scored G1/G2 on eval users 640..799 for low_diversity and flat_theta",
            "run_id": f"{TASK_ID}:{run_started_at}",
            "run_started_at": run_started_at,
            "run_finished_at": _utc_timestamp(),
            "wall_clock_seconds": time.perf_counter() - wall_start,
            "requested_cells": list(REQUESTED_CELLS),
            "eval_user_range": [min(EVAL_USERS), max(EVAL_USERS)],
            "eval_user_count": len(EVAL_USERS),
            "heldout_users_800_999_touched": False,
            "frozen_spec_runner_src_or_banked_artifact_edited": False,
            "producer_function": "s3d_null_ideal_diag_002a.main",
            "code_path_hash": code_hash,
            "input_artifacts": [
                _input_ref(FROZEN_DESIGN),
                _input_ref(HARNESS_001A),
                _input_ref(VOID_TRACE),
                _input_ref(TASK_CARD),
                _input_ref(COLLISION_RECORD),
            ],
            "source_pins": {
                "current_runner_worktree": _input_ref(RUNNER),
                "factored_filter": _input_ref(ROOT / "src" / "fsp_pum_env" / "factored_filter.py"),
                "simulator": _input_ref(ROOT / "src" / "fsp_pum_env" / "simulator.py"),
                "s3d_certificates": _input_ref(ROOT / "src" / "fsp_pum_env" / "s3d_certificates.py"),
                "trajectory_sets": _input_ref(ROOT / "src" / "fsp_pum_env" / "trajectory_sets.py"),
                "ideal_observer": _input_ref(ROOT / "src" / "fsp_pum_env" / "ideal_observer.py"),
            },
            "chance": CHANCE,
            "chance_plus_null_margin": NULL_LIMIT,
            "results_by_cell": results_by_cell,
            "g1_reproduction_gate": reproduction_gate,
            "collapsed_equivalence_spot_check": collapsed_equivalence_spot_check,
            "g3_void_reference": g3_void_reference,
            "per_user_support_csv": per_user_csv,
            "per_user_support_summary": per_user_summary,
            "decision": decision,
            "trace_jsonl": {
                "path": _relative(TRACE_PATH),
                "row_count": len(trace_rows),
                "sha256": _sha256_path(TRACE_PATH),
                "contains_tests": [
                    f"G1_true_style::{cell}" for cell in REQUESTED_CELLS
                ] + [
                    f"G2_wrong_style::{cell}" for cell in REQUESTED_CELLS
                ],
            },
            "claim_ceiling": (
                "bounded S3D-NULL-IDEAL-DIAG-002A diagnostic evidence only: style-map privilege scope "
                "in low_diversity and flat_theta over eval users 640..799; no fix, no S3d gate pass, "
                "no environment-validity, no mechanism-validity, no EGO mainline, no agency, no consciousness claim"
            ),
        }
        for cell_payload in result["results_by_cell"].values():
            for payload in cell_payload.values():
                payload["code_path_hash"] = code_hash
        _write_json_roundtrip(RESULT_PATH, result)
        _write_text(FINDINGS_PATH, _findings_md(result))
        print(
            json.dumps(
                {
                    "verdict": decision["verdict"],
                    "result": _relative(RESULT_PATH),
                    "findings": _relative(FINDINGS_PATH),
                    "trace": _relative(TRACE_PATH),
                    "per_user_support": _relative(PER_USER_SUPPORT_CSV),
                },
                sort_keys=True,
            )
        )
        return 0
    except Exception as exc:
        failure = _failure_payload(run_started_at, "unhandled_exception", {"exception": repr(exc)})
        _write_json_roundtrip(FAILURE_MANIFEST, failure)
        print(json.dumps({"verdict": failure["verdict"], "failure_manifest": _relative(FAILURE_MANIFEST)}, sort_keys=True))
        raise


if __name__ == "__main__":
    raise SystemExit(main())
