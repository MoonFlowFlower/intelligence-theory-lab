"""Factored exact posterior updates for FSP-PUM S2 tractability checks.

The factorization here is only a likelihood-computation factorization. The
posterior remains one full joint log-weight vector over the enumerated theta
grid atoms.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import time
import tracemalloc
from typing import Any, Mapping, Sequence

import numpy as np

from .ideal_observer import (
    ExactBayesFilter,
    FixedProbeSchedule,
    PrefixEvent,
    S5_CPU_HOUR_LIMIT,
    ThetaGridSpec,
    Z_CONVERGENCE_THRESHOLD,
    _advance_without_sampling,
    _clone_user,
    _code_path_hash,
    _max_abs_diff,
    _modal_symbol,
    _validate_style_map,
    _write_json_if_requested,
    independent_filter_seed,
    make_z_quadrature,
    run_z_marginalization_convergence,
)
from .simulator import FspPumSimulator, SimulatorVariant, _SessionState


@dataclass(frozen=True)
class _ActionClassSpec:
    action: str
    theta_class_count: int
    kind: str


@dataclass
class _FactoredIndex:
    action_class_indices: dict[str, np.ndarray]
    action_specs: dict[str, _ActionClassSpec]
    topic_class_values: dict[int, np.ndarray]
    flag0_values: np.ndarray
    flag1_values: np.ndarray
    recommend_preferences: np.ndarray
    trust_class_indices: np.ndarray
    trust_alpha: np.ndarray
    trust_beta: np.ndarray
    trust_d: np.ndarray
    atom_count: int
    index_arrays_bytes: int


class FactoredExactFilter:
    """Exact full-grid Bayes filter with factored likelihood tables.

    The object keeps one unnormalized float64 log-weight per theta atom.
    Per-action equivalence class arrays only decide which likelihood-table row
    each atom receives.
    """

    def __init__(
        self,
        design: Mapping[str, Any],
        *,
        filter_seed: int,
        variant: SimulatorVariant | str,
        style_map: Sequence[int],
        grid_spec: ThetaGridSpec | None = None,
        user_id: int = 0,
        true_environment_seed: int | None = None,
        z_quadrature_points: int = 5,
    ):
        self.design = design
        self.filter_seed = int(filter_seed)
        if true_environment_seed is not None and int(true_environment_seed) == self.filter_seed:
            raise ValueError("filter_seed must be independent of the true environment seed")
        self.variant = SimulatorVariant(variant)
        self.grid_spec = grid_spec or ThetaGridSpec.from_design(design)
        self.user_id = int(user_id)
        self.simulator = FspPumSimulator(design, master_seed=self.filter_seed, variant=self.variant)
        self.style_map = _validate_style_map(style_map, self.simulator.alphabet_size)
        self.z_quadrature = make_z_quadrature(design, z_quadrature_points)
        self._index = _build_factored_index(design, self.grid_spec, self.simulator)
        self._trust_values = np.full(
            len(self._index.trust_alpha),
            float(design["env_parameters"]["trust_dynamics"]["init"]),
            dtype=np.float64,
        )
        self._initial_log_weight = -math.log(self._index.atom_count)
        self._log_weights = np.full(self._index.atom_count, self._initial_log_weight, dtype=np.float64)
        self._normalized_weight_scratch = np.empty(self._index.atom_count, dtype=np.float64)
        self._normalized_weights_valid = False
        self._cached_log_norm = math.nan
        self.events: list[PrefixEvent] = []
        self._table_cache: dict[str, np.ndarray] = {}

    @property
    def atom_count(self) -> int:
        return int(self._log_weights.size)

    @property
    def index_arrays_dtype(self) -> str:
        return "int32"

    @property
    def log_weights(self) -> np.ndarray:
        return self._log_weights

    @property
    def weights(self) -> np.ndarray:
        return self._ensure_normalized_weights()

    def reset(self) -> None:
        self._trust_values.fill(float(self.design["env_parameters"]["trust_dynamics"]["init"]))
        self._log_weights.fill(self._initial_log_weight)
        self._invalidate_normalized_weights()
        self.events = []
        self._table_cache.clear()

    def observe(self, event: PrefixEvent | Mapping[str, Any]) -> None:
        prefix_event = event if isinstance(event, PrefixEvent) else PrefixEvent.from_mapping(event)
        self.simulator._validate_action(prefix_event.action)
        if not 0 <= prefix_event.symbol < self.simulator.alphabet_size:
            raise ValueError("prefix-only observation symbol outside response alphabet")

        table = self._distribution_table(prefix_event.action)
        class_indices = self._index.action_class_indices[prefix_event.action]
        log_likelihood_by_class = np.log(np.maximum(table[:, prefix_event.symbol], 1e-300))
        self._log_weights += log_likelihood_by_class[class_indices]
        self._invalidate_normalized_weights()
        self._advance_trust(prefix_event.action)
        self.events.append(prefix_event)
        self._table_cache.clear()

    def predict_distribution(self, action: str) -> list[float]:
        self.simulator._validate_action(action)
        table = self._distribution_table(action)
        class_indices = self._index.action_class_indices[action]
        class_masses = np.bincount(class_indices, weights=self._ensure_normalized_weights(), minlength=table.shape[0])
        mixture = class_masses @ table
        total = float(mixture.sum())
        if total <= 0.0:
            raise ValueError("posterior predictive has zero mass")
        return (mixture / total).tolist()

    def posterior_mass(self) -> float:
        return float(self._ensure_normalized_weights().sum())

    def posterior_entropy(self) -> float:
        weights = self._ensure_normalized_weights()
        log_probabilities = self._log_weights - self._cached_log_norm
        return -float(np.dot(weights, log_probabilities))

    def expected_entropy_after_observation(self, action: str) -> float:
        self.simulator._validate_action(action)
        table = self._distribution_table(action)
        class_indices = self._index.action_class_indices[action]
        weights = self._ensure_normalized_weights()
        class_masses = np.bincount(class_indices, weights=weights, minlength=table.shape[0])

        weight_log_terms = weights * (self._log_weights - self._cached_log_norm)
        class_weight_log_sums = np.bincount(
            class_indices,
            weights=weight_log_terms,
            minlength=table.shape[0],
        )

        predictive = class_masses @ table
        table_log_terms = table * np.log(np.maximum(table, 1e-300))
        weighted_log_prior = class_weight_log_sums @ table
        weighted_log_likelihood = class_masses @ table_log_terms
        positive = predictive > 0.0
        expected_entropy = -float(
            np.sum(
                weighted_log_prior[positive]
                + weighted_log_likelihood[positive]
                - predictive[positive] * np.log(predictive[positive])
            )
        )
        return expected_entropy

    def array_bytes(self) -> int:
        return int(
            self._log_weights.nbytes
            + self._normalized_weight_scratch.nbytes
            + self._index.index_arrays_bytes
            + self._trust_values.nbytes
        )

    def scatter_kernel_certificate(self) -> dict[str, Any]:
        return {
            "posterior_storage": "unnormalized_float64_log_weight_vector",
            "posterior_representation": "full_joint_posterior_over_theta_atoms",
            "posterior_dtype": str(self._log_weights.dtype),
            "atom_count": self.atom_count,
            "update_kernel": "in-place log_weight_vector += log_likelihood_by_class[class_indices]",
            "normalization_policy": "query-time logsumexp shift; no per-observation normalization",
            "prediction_kernel": "np.bincount over precomputed per-action class indices using cached exp-shifted weights",
            "precomputed_class_index_dtype": self.index_arrays_dtype,
            "scratch_dtype": str(self._normalized_weight_scratch.dtype),
            "scratch_bytes": int(self._normalized_weight_scratch.nbytes),
            "overflow_bound": _log_domain_overflow_bound(),
            "approximation": "none",
        }

    def information_interface(self) -> dict[str, Any]:
        return {
            "generator_access": ["distribution_kernels", "per_user_style_map"],
            "sees_theta": False,
            "sees_z_realization": False,
            "sees_sampling_seeds": False,
            "prefix_only": True,
            "posterior_representation": "full_joint_log_weight_vector",
            "likelihood_factorization_only": True,
            "z_marginalization": {
                "scheme": self.z_quadrature.scheme,
                "points_per_dim": self.z_quadrature.points_per_dim,
                "node_count": self.z_quadrature.node_count,
            },
        }

    def _invalidate_normalized_weights(self) -> None:
        self._normalized_weights_valid = False
        self._cached_log_norm = math.nan

    def _ensure_normalized_weights(self) -> np.ndarray:
        if self._normalized_weights_valid:
            return self._normalized_weight_scratch
        max_log_weight = float(np.max(self._log_weights))
        if not math.isfinite(max_log_weight):
            raise ValueError("posterior log weights are not finite")
        np.subtract(self._log_weights, max_log_weight, out=self._normalized_weight_scratch)
        np.exp(self._normalized_weight_scratch, out=self._normalized_weight_scratch)
        total = float(self._normalized_weight_scratch.sum())
        if total <= 0.0:
            raise ValueError("posterior weights have zero mass")
        self._normalized_weight_scratch /= total
        self._cached_log_norm = max_log_weight + math.log(total)
        self._normalized_weights_valid = True
        return self._normalized_weight_scratch

    def _advance_trust(self, action: str) -> None:
        cost = self.simulator._probe_trust_cost(action)
        if action in self.simulator.probe_actions:
            next_trust = self._index.trust_beta * self._trust_values - cost
        else:
            next_trust = self._index.trust_beta * self._trust_values + self._index.trust_alpha * (1.0 - self._trust_values)
        self._trust_values = np.clip(next_trust, 0.0, 1.0)

    def _distribution_table(self, action: str) -> np.ndarray:
        cached = self._table_cache.get(action)
        if cached is not None:
            return cached
        table = self._compute_distribution_table(action)
        self._table_cache[action] = table
        return table

    def _compute_distribution_table(self, action: str) -> np.ndarray:
        if self.variant is SimulatorVariant.NULL_ENV:
            return self._action_only_table(action, low_trust=False)
        if self.variant is SimulatorVariant.GRAPH_CACHE_SHOULD_WIN_LOW_DIVERSITY_TEMPLATES:
            return self._low_diversity_table(action)
        if self.variant is SimulatorVariant.PROBE_CHANNEL_OFF and action in self.simulator.probe_actions:
            return self._action_only_table(action, low_trust=True)
        if self.variant in {SimulatorVariant.RAG_SHOULD_WIN_STABLE_FACTS, SimulatorVariant.FLAT_THETA}:
            raise ValueError(f"FactoredExactFilter does not support variant {self.variant.value}")

        if action in self.simulator.probe_actions:
            return self._probe_table(action)
        if action in self.simulator.task_actions:
            return self._task_table(action)
        if action in self.simulator.recommend_actions:
            return self._recommend_table()
        raise ValueError(f"unknown action: {action}")

    def _action_only_table(self, action: str, *, low_trust: bool) -> np.ndarray:
        spec = self._index.action_specs[action]
        center = (self.simulator.all_actions.index(action) * 5) % self.simulator.alphabet_size
        base = _peaked_distribution(np.full(spec.theta_class_count * len(self._trust_values), center), np.full(spec.theta_class_count * len(self._trust_values), 0.9), self.simulator.alphabet_size)
        base = base.reshape(spec.theta_class_count, len(self._trust_values), self.simulator.alphabet_size)
        if low_trust:
            base = self._apply_low_trust(base)
        return _apply_style_map(base.reshape(-1, self.simulator.alphabet_size), self.style_map)

    def _low_diversity_table(self, action: str) -> np.ndarray:
        spec = self._index.action_specs[action]
        if action in self.simulator.probe_actions:
            center = 4
        elif action in self.simulator.recommend_actions:
            center = 8
        else:
            center = int(action.rsplit("_", 1)[1]) % 2
        rows = spec.theta_class_count * len(self._trust_values)
        base = _peaked_distribution(
            np.full(rows, center, dtype=np.int32),
            np.full(rows, 3.0, dtype=np.float64),
            self.simulator.alphabet_size,
        ).reshape(spec.theta_class_count, len(self._trust_values), self.simulator.alphabet_size)
        return _apply_style_map(self._apply_low_trust(base).reshape(-1, self.simulator.alphabet_size), self.style_map)

    def _probe_table(self, action: str) -> np.ndarray:
        spec = self._index.action_specs[action]
        trust_count = len(self._trust_values)
        if action == "probe_0":
            centers = 2 + self._index.flag0_values.astype(np.int32)
            strength = np.full(centers.size, 2.7, dtype=np.float64)
        elif action == "probe_1":
            centers = 6 + self._index.flag1_values.astype(np.int32)
            strength = np.full(centers.size, 2.7, dtype=np.float64)
        elif action == "probe_2":
            centers = 10 + _global_topic_level_indices(self.simulator, self._index.topic_class_values[7])
            strength = np.full(centers.size, 2.9, dtype=np.float64)
        else:
            topic_components = _global_topic_level_indices(self.simulator, self._index.topic_class_values[7])
            flag_components = np.array(
                [2 * int(f0) + int(f1) for f0 in self._index.flag0_values for f1 in self._index.flag1_values],
                dtype=np.int32,
            )
            topic_tiled = np.tile(topic_components, len(flag_components))
            flag_repeated = np.repeat(flag_components, len(topic_components))
            centers = 16 + ((topic_tiled + flag_repeated) % 8)
            strength = np.full(centers.size, 1.75, dtype=np.float64)
        if centers.size != spec.theta_class_count:
            raise ValueError(f"class table mismatch for {action}")
        centers = np.repeat(centers, trust_count)
        strength = np.repeat(strength, trust_count)
        base = _peaked_distribution(centers, strength, self.simulator.alphabet_size)
        base = base.reshape(spec.theta_class_count, trust_count, self.simulator.alphabet_size)
        return _apply_style_map(self._apply_low_trust(base).reshape(-1, self.simulator.alphabet_size), self.style_map)

    def _task_table(self, action: str) -> np.ndarray:
        topic_index = int(action.rsplit("_", 1)[1])
        spec = self._index.action_specs[action]
        trust_count = len(self._trust_values)
        z_count = self.z_quadrature.node_count
        z_valence = np.asarray([node[0] for node in self.z_quadrature.nodes], dtype=np.float64)
        z_stress = np.asarray([node[2] for node in self.z_quadrature.nodes], dtype=np.float64)
        z_term = 0.35 * z_valence - 0.15 * z_stress
        topic_effect, interaction = _task_topic_effects(self.design, self._index, topic_index)
        centers = np.full(spec.theta_class_count, (topic_index * 3 + 8) % self.simulator.alphabet_size, dtype=np.int32)
        base_strength = 1.35 + 0.55 * topic_effect + 0.15 * interaction
        row_centers = np.repeat(centers, trust_count * z_count)
        row_strength = np.repeat(base_strength, trust_count * z_count) + np.tile(z_term, spec.theta_class_count * trust_count)
        base = _peaked_distribution(row_centers, row_strength, self.simulator.alphabet_size)
        base = base.reshape(spec.theta_class_count, trust_count, z_count, self.simulator.alphabet_size)
        degraded = self._apply_low_trust(base)
        weights = np.asarray(self.z_quadrature.weights, dtype=np.float64)
        marginalized = np.tensordot(degraded, weights, axes=([2], [0]))
        return _apply_style_map(marginalized.reshape(-1, self.simulator.alphabet_size), self.style_map)

    def _recommend_table(self) -> np.ndarray:
        spec = self._index.action_specs["recommend"]
        trust_count = len(self._trust_values)
        z_count = self.z_quadrature.node_count
        z_valence = np.asarray([node[0] for node in self.z_quadrature.nodes], dtype=np.float64)
        z_arousal = np.asarray([node[1] for node in self.z_quadrature.nodes], dtype=np.float64)
        z_term = 0.2 * z_valence + 0.1 * z_arousal
        preferences = self._index.recommend_preferences
        centers = np.asarray(
            [(13 + round(2.0 * float(preference))) % self.simulator.alphabet_size for preference in preferences],
            dtype=np.int32,
        )
        base_strength = 1.1 + 0.35 * preferences
        row_centers = np.repeat(centers, trust_count * z_count)
        row_strength = np.repeat(base_strength, trust_count * z_count) + np.tile(z_term, spec.theta_class_count * trust_count)
        base = _peaked_distribution(row_centers, row_strength, self.simulator.alphabet_size)
        base = base.reshape(spec.theta_class_count, trust_count, z_count, self.simulator.alphabet_size)
        degraded = self._apply_low_trust(base)
        weights = np.asarray(self.z_quadrature.weights, dtype=np.float64)
        marginalized = np.tensordot(degraded, weights, axes=([2], [0]))
        return _apply_style_map(marginalized.reshape(-1, self.simulator.alphabet_size), self.style_map)

    def _apply_low_trust(self, distribution: np.ndarray) -> np.ndarray:
        trust = self._trust_values
        threshold = np.maximum(self._index.trust_d, 1e-12)
        weight = np.maximum((threshold - trust) / threshold, 0.0)
        shape = [1, len(trust)] + [1] * (distribution.ndim - 2)
        trust_weight = weight.reshape(shape)
        uniform = 1.0 / self.simulator.alphabet_size
        return (1.0 - trust_weight) * distribution + trust_weight * uniform


def run_factored_equivalence_certificate(
    frozen_design_path: str | Path,
    *,
    output_path: str | Path | None = None,
    master_seed: int = 20260714,
    z_quadrature_points: int = 5,
) -> dict[str, Any]:
    start = time.perf_counter()
    path = Path(frozen_design_path)
    design = json.loads(path.read_text(encoding="utf-8-sig"))
    style_map = tuple(range(int(design["env_parameters"]["renderer"]["response_alphabet_size"])))
    cases = _equivalence_cases(design)
    action_sequence = _certificate_action_sequence()
    query_actions = list(action_sequence)
    max_delta = 0.0
    rows: list[dict[str, Any]] = []
    passed = True

    for case_index, case in enumerate(cases):
        true_seed = master_seed + 100 + case_index
        filter_seed = independent_filter_seed(true_seed, f"factored_equivalence:{case['case_id']}")
        true_sim = FspPumSimulator(design, master_seed=true_seed, variant=SimulatorVariant.CAMOUFLAGE_OFF)
        true_user = true_sim.start_user(user_id=case_index, controlled_theta=case["theta_control"], style_map=style_map)
        exact = ExactBayesFilter(
            design,
            filter_seed=filter_seed,
            true_environment_seed=true_seed,
            variant=SimulatorVariant.CAMOUFLAGE_OFF,
            grid_spec=case["grid_spec"],
            user_id=case_index,
            style_map=style_map,
            z_quadrature_points=z_quadrature_points,
        )
        factored = FactoredExactFilter(
            design,
            filter_seed=filter_seed,
            true_environment_seed=true_seed,
            variant=SimulatorVariant.CAMOUFLAGE_OFF,
            grid_spec=case["grid_spec"],
            user_id=case_index,
            style_map=style_map,
            z_quadrature_points=z_quadrature_points,
        )
        for turn_index, action in enumerate(query_actions):
            exact_dist = exact.predict_distribution(action)
            factored_dist = factored.predict_distribution(action)
            delta = _max_abs_diff(exact_dist, factored_dist)
            max_delta = max(max_delta, delta)
            rows.append(
                {
                    "case_id": case["case_id"],
                    "turn_index": turn_index,
                    "query_action": action,
                    "max_abs_prediction_delta": delta,
                }
            )
            if delta > 1e-12:
                passed = False
                break
            symbol = _modal_symbol(true_sim.response_distribution(true_user, action))
            event = PrefixEvent(action=action, symbol=symbol)
            exact.observe(event)
            factored.observe(event)
            _advance_without_sampling(true_sim, true_user, action)
        if not passed:
            break

    report = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S2c",
        "artifact": "factored_equivalence_certificate",
        "passed": passed,
        "threshold": 1e-12,
        "max_abs_prediction_delta": max_delta,
        "turn_count": len(action_sequence),
        "query_policy": "one preregistered predict_distribution call before each observed action; sequence covers probes, paired tasks, unpaired tasks, topic_7, and recommend",
        "cases": [
            {
                "case_id": case["case_id"],
                "atom_count": case["grid_spec"].atom_count,
                "description": case["description"],
            }
            for case in cases
        ],
        "rows": rows,
        "z_quadrature_points_per_dim": z_quadrature_points,
        "z_node_count": z_quadrature_points ** 3,
        "wall_clock_seconds": time.perf_counter() - start,
        "producer_function": "src.fsp_pum_env.ideal_observer.run_factored_equivalence_certificate",
        "input_artifacts": [str(path)],
        "code_path_hash": _factored_code_path_hash(),
        "claim_ceiling": "FactoredExactFilter equivalence to per-atom ExactBayesFilter on preregistered feasible sub-grids only",
    }
    _write_json_if_requested(output_path, report)
    return report


def run_z_quadrature_selection_certificate(
    frozen_design_path: str | Path,
    *,
    output_path: str | Path | None = None,
    master_seed: int = 20260717,
    candidate_g_values: Sequence[int] = (3, 4),
) -> dict[str, Any]:
    start = time.perf_counter()
    path = Path(frozen_design_path)
    candidate_runs = [
        run_z_marginalization_convergence(
            path,
            master_seed=master_seed,
            base_g=int(base_g),
        )
        for base_g in candidate_g_values
    ]
    passing = [
        run
        for run in candidate_runs
        if bool(run["passed"]) and float(run["max_abs_prediction_delta"]) < Z_CONVERGENCE_THRESHOLD
    ]
    selected = min(passing, key=lambda run: int(run["base_g"])) if passing else None
    report = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S2d",
        "artifact": "z_marginalization_convergence_s2d_g_selection",
        "scheme": "same g-vs-2g tensor Gauss-Hermite convergence method as z_marginalization_convergence.json",
        "candidate_g_values": [int(value) for value in candidate_g_values],
        "threshold": Z_CONVERGENCE_THRESHOLD,
        "candidate_runs": candidate_runs,
        "selected_g": int(selected["base_g"]) if selected is not None else None,
        "selected_node_count": int(selected["base_g"]) ** 3 if selected is not None else None,
        "selected_max_abs_prediction_delta": float(selected["max_abs_prediction_delta"]) if selected is not None else None,
        "passed": selected is not None,
        "wall_clock_seconds": time.perf_counter() - start,
        "producer_function": "src.fsp_pum_env.ideal_observer.run_z_quadrature_selection_certificate",
        "input_artifacts": [str(path)],
        "code_path_hash": _factored_code_path_hash(),
        "claim_ceiling": "S2d z-quadrature selection certificate only; theta grid and thresholds unchanged",
    }
    _write_json_if_requested(output_path, report)
    return report


def run_s2_tractability_benchmark_v2(
    frozen_design_path: str | Path,
    *,
    output_path: str | Path | None = None,
    master_seed: int = 20260715,
    z_quadrature_points: int = 5,
    benchmark_turns: int | None = None,
    benchmark_queries: int | None = None,
    grid_spec: ThetaGridSpec | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()
    path = Path(frozen_design_path)
    design = json.loads(path.read_text(encoding="utf-8-sig"))
    full_grid = ThetaGridSpec.from_design(design)
    measured_grid = grid_spec or full_grid
    env = design["env_parameters"]
    eval_cfg = design["evaluation"]
    total_turns = int(env["episodes"]["total_turns_per_user"])
    total_queries = int(eval_cfg["query_points"]["queries_per_user"]) * len(eval_cfg["counterfactual_action_set_per_query"])
    turns = total_turns if benchmark_turns is None else int(benchmark_turns)
    queries = total_queries if benchmark_queries is None else int(benchmark_queries)
    if turns > total_turns or queries > total_queries:
        raise ValueError("benchmark overrides cannot exceed the frozen full episode/query count")

    style_map = tuple(range(int(env["renderer"]["response_alphabet_size"])))
    true_seed = master_seed
    filter_seed = independent_filter_seed(true_seed, "s2_tractability_v2")
    true_sim = FspPumSimulator(design, master_seed=true_seed, variant=SimulatorVariant.CAMOUFLAGE_OFF)
    true_user = true_sim.start_user(user_id=0, style_map=style_map)

    tracemalloc.start()
    peak_rss = _current_rss_bytes()
    peak_trace = 0
    init_start = time.perf_counter()
    filt = FactoredExactFilter(
        design,
        filter_seed=filter_seed,
        true_environment_seed=true_seed,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=measured_grid,
        user_id=0,
        style_map=style_map,
        z_quadrature_points=z_quadrature_points,
    )
    init_seconds = time.perf_counter() - init_start
    peak_rss, peak_trace = _sample_memory_peaks(peak_rss, peak_trace)

    schedule = FixedProbeSchedule(probe_rate=0.2, placement="uniform").actions_for_episode(design)[:turns]
    query_actions = list(eval_cfg["counterfactual_action_set_per_query"])
    query_points = {
        (int(session), int(turn))
        for session in eval_cfg["query_points"]["sessions"]
        for turn in eval_cfg["query_points"]["turns_within_session"]
    }
    measured_query_count = 0
    prediction_checksum = 0.0
    update_seconds = 0.0
    query_seconds = 0.0

    for turn_index, action in enumerate(schedule):
        step_start = time.perf_counter()
        result = true_sim.step(true_user, action)
        filt.observe(PrefixEvent(action=action, symbol=int(result.observation["symbol"])))
        update_seconds += time.perf_counter() - step_start
        peak_rss, peak_trace = _sample_memory_peaks(peak_rss, peak_trace)

        session_number = turn_index // int(env["episodes"]["T_turns_per_session"]) + 1
        turn_within_session = turn_index % int(env["episodes"]["T_turns_per_session"]) + 1
        if (session_number, turn_within_session) in query_points:
            for query_action in query_actions:
                if measured_query_count >= queries:
                    break
                query_start = time.perf_counter()
                prediction = filt.predict_distribution(query_action)
                query_seconds += time.perf_counter() - query_start
                prediction_checksum += float(prediction[0])
                measured_query_count += 1
                peak_rss, peak_trace = _sample_memory_peaks(peak_rss, peak_trace)
        if measured_query_count >= queries:
            continue

    expanded_queries = [query_actions[index % len(query_actions)] for index in range(queries)]
    for query_action in expanded_queries[measured_query_count:]:
        query_start = time.perf_counter()
        prediction = filt.predict_distribution(query_action)
        query_seconds += time.perf_counter() - query_start
        prediction_checksum += float(prediction[0])
        measured_query_count += 1
        peak_rss, peak_trace = _sample_memory_peaks(peak_rss, peak_trace)

    current_trace, final_trace_peak = tracemalloc.get_traced_memory()
    peak_trace = max(peak_trace, final_trace_peak)
    tracemalloc.stop()
    measured_seconds = time.perf_counter() - start
    benchmark_units = max(turns + measured_query_count, 1)
    projected_one_user_seconds = measured_seconds * ((total_turns + total_queries) / benchmark_units)
    projected_s5_seconds = projected_one_user_seconds * 10 * 200
    projected_s5_cpu_hours = projected_s5_seconds / 3600.0
    oracle_policy_multiplier = 20
    projected_s5_policy_class_cpu_hours = projected_s5_cpu_hours * oracle_policy_multiplier
    decision = "tractable" if projected_s5_cpu_hours <= S5_CPU_HOUR_LIMIT else "stop_N0_F3_required"

    report = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S2c",
        "artifact": "s2_tractability_report_v2",
        "invalid_prior_artifact_preserved": "artifacts/FSP-PUM-ENV-IDPROBE-001A/s2_tractability_report.json",
        "implementation_path": "FactoredExactFilter full joint posterior vector with factored likelihood tables; no atom-grid downsizing; no mean-field posterior factorization",
        "benchmark_scope": {
            "full_episode_turns": total_turns,
            "full_episode_counterfactual_queries": total_queries,
            "measured_turns": turns,
            "measured_counterfactual_queries": measured_query_count,
            "fixed_schedule": "probe_rate=0.2, placement=uniform",
            "complete_full_grid_run": measured_grid.atom_count == full_grid.atom_count and turns == total_turns and measured_query_count == total_queries,
        },
        "full_grid_atom_count": full_grid.atom_count,
        "measured_grid_atom_count": measured_grid.atom_count,
        "posterior_vector": {
            "dtype": str(filt.log_weights.dtype),
            "bytes": int(filt.log_weights.nbytes),
            "shape": list(filt.log_weights.shape),
        },
        "precomputed_index_arrays": {
            "dtype": filt.index_arrays_dtype,
            "action_array_count": len(filt._index.action_class_indices),
            "bytes": int(filt._index.index_arrays_bytes),
        },
        "z_quadrature_points_per_dim": z_quadrature_points,
        "z_node_count": z_quadrature_points ** 3,
        "measured_wall_clock_seconds": measured_seconds,
        "initialization_seconds": init_seconds,
        "update_wall_clock_seconds": update_seconds,
        "query_wall_clock_seconds": query_seconds,
        "measured_updates": turns,
        "measured_counterfactual_queries": measured_query_count,
        "prediction_checksum": prediction_checksum,
        "projected_one_user_seconds": projected_one_user_seconds,
        "projected_s5_cpu_hours": projected_s5_cpu_hours,
        "policy_class_multiplier": {
            "fixed_schedule_grid": 15,
            "myopic_IG": 1,
            "ucb1": 1,
            "passive": 1,
            "ideal_with_probes": 1,
            "truncation_ideal_B30": 1,
            "naive_total_multiplier": oracle_policy_multiplier,
            "projected_s5_cpu_hours_if_all_policy_classes_run_naively": projected_s5_policy_class_cpu_hours,
        },
        "decision_rule": "projected_s5_cpu_hours <= 24",
        "decision_projection_basis": "single fixed 0.2-uniform policy workload requested for this benchmark; policy-class sweeps multiply separately",
        "decision": decision,
        "peak_memory": {
            "peak_observed_rss_bytes": peak_rss,
            "tracemalloc_peak_bytes": int(peak_trace),
            "filter_array_bytes": filt.array_bytes(),
            "measurement_note": "RSS sampled after initialization, every update, and every counterfactual query; transient native allocation peaks between samples may be missed.",
        },
        "producer_function": "src.fsp_pum_env.ideal_observer.run_s2_tractability_benchmark_v2",
        "input_artifacts": [str(path)],
        "code_path_hash": _factored_code_path_hash(),
        "claim_ceiling": "S2c FactoredExactFilter tractability evidence only; no S3, environment-validity, learning, agency, or EGO-mainline claim",
    }
    _write_json_if_requested(output_path, report)
    return report


def run_s2_tractability_benchmark_v3(
    frozen_design_path: str | Path,
    *,
    output_path: str | Path | None = None,
    master_seed: int = 20260715,
    z_quadrature_points: int = 3,
    benchmark_turns: int | None = None,
    benchmark_queries: int | None = None,
    grid_spec: ThetaGridSpec | None = None,
) -> dict[str, Any]:
    path = Path(frozen_design_path)
    report = run_s2_tractability_benchmark_v2(
        path,
        master_seed=master_seed,
        z_quadrature_points=z_quadrature_points,
        benchmark_turns=benchmark_turns,
        benchmark_queries=benchmark_queries,
        grid_spec=grid_spec,
    )
    design = json.loads(path.read_text(encoding="utf-8-sig"))
    measured_grid = grid_spec or ThetaGridSpec.from_design(design)
    env = design["env_parameters"]
    style_map = tuple(range(int(env["renderer"]["response_alphabet_size"])))
    policy_filter_start = time.perf_counter()
    policy_filter = FactoredExactFilter(
        design,
        filter_seed=independent_filter_seed(master_seed, "s2d_myopic_ig_cost_note"),
        true_environment_seed=master_seed,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=measured_grid,
        user_id=0,
        style_map=style_map,
        z_quadrature_points=z_quadrature_points,
    )
    policy_filter_init_seconds = time.perf_counter() - policy_filter_start
    policy_class_cost_note = _measure_myopic_ig_policy_class_cost(policy_filter)
    policy_class_cost_note["filter_initialization_seconds"] = policy_filter_init_seconds
    policy_class_cost_note["cost_note_scope"] = (
        "One myopic-IG action selection only: 4 probe actions times expected-entropy computation; "
        "not included in the fixed-schedule S5 decision projection."
    )

    report.update(
        {
            "stage": "S2d",
            "artifact": "s2_tractability_report_v3",
            "invalid_prior_artifact_preserved": [
                "artifacts/FSP-PUM-ENV-IDPROBE-001A/s2_tractability_report.json",
                "artifacts/FSP-PUM-ENV-IDPROBE-001A/s2_tractability_report_v2.json",
            ],
            "implementation_path": (
                "FactoredExactFilter full joint posterior vector with certificate-selected z quadrature "
                "and exact float64 scatter-kernel optimization; no atom-grid downsizing; no threshold movement; "
                "no mean-field posterior factorization"
            ),
            "posterior_vector": {
                "dtype": str(policy_filter.log_weights.dtype),
                "bytes": int(policy_filter.log_weights.nbytes),
                "shape": list(policy_filter.log_weights.shape),
                "storage": "unnormalized_float64_log_weight_vector",
            },
            "scatter_kernel": policy_filter.scatter_kernel_certificate(),
            "z_selection_contract": {
                "candidate_g_values": [3, 4],
                "selection_rule": "smallest g with g-vs-2g max_abs_prediction_delta < 1e-3",
                "selected_g_used_by_this_report": int(z_quadrature_points),
                "threshold": Z_CONVERGENCE_THRESHOLD,
            },
            "policy_class_cost_note": policy_class_cost_note,
            "producer_function": "src.fsp_pum_env.ideal_observer.run_s2_tractability_benchmark_v3",
            "code_path_hash": _factored_code_path_hash(),
            "claim_ceiling": "S2d FactoredExactFilter tractability evidence only; no S3, environment-validity, learning, agency, or EGO-mainline claim",
        }
    )
    _write_json_if_requested(output_path, report)
    return report


def run_s2_tractability_benchmark_v4(
    frozen_design_path: str | Path,
    *,
    output_path: str | Path | None = None,
    master_seed: int = 20260715,
    z_quadrature_points: int = 3,
    benchmark_turns: int | None = None,
    benchmark_queries: int | None = None,
    grid_spec: ThetaGridSpec | None = None,
    before_profile_path: str | Path | None = None,
) -> dict[str, Any]:
    path = Path(frozen_design_path)
    report = run_s2_tractability_benchmark_v2(
        path,
        master_seed=master_seed,
        z_quadrature_points=z_quadrature_points,
        benchmark_turns=benchmark_turns,
        benchmark_queries=benchmark_queries,
        grid_spec=grid_spec,
    )
    design = json.loads(path.read_text(encoding="utf-8-sig"))
    full_grid = ThetaGridSpec.from_design(design)
    measured_grid = grid_spec or full_grid
    env = design["env_parameters"]
    style_map = tuple(range(int(env["renderer"]["response_alphabet_size"])))
    policy_filter_start = time.perf_counter()
    policy_filter = FactoredExactFilter(
        design,
        filter_seed=independent_filter_seed(master_seed, "s2e_myopic_ig_cost_note"),
        true_environment_seed=master_seed,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=measured_grid,
        user_id=0,
        style_map=style_map,
        z_quadrature_points=z_quadrature_points,
    )
    policy_filter_init_seconds = time.perf_counter() - policy_filter_start
    policy_class_cost_note = _measure_myopic_ig_policy_class_cost(policy_filter)
    policy_class_cost_note["filter_initialization_seconds"] = policy_filter_init_seconds
    policy_class_cost_note["cost_note_scope"] = (
        "One myopic-IG action selection only: 4 probe actions times expected-entropy computation; "
        "optimized-kernel remeasure, not included in the fixed-schedule S5 decision projection."
    )

    before_path = Path(before_profile_path) if before_profile_path is not None else path.with_name("s2e_step0_profile_before.json")
    before_profile = _read_json_if_exists(before_path)
    after_profile = _profile_factored_update_step(
        design,
        grid_spec=full_grid,
        master_seed=master_seed,
        z_quadrature_points=z_quadrature_points,
        profile_id="s2e_step_profile_after",
    )

    report.update(
        {
            "stage": "S2e",
            "artifact": "s2_tractability_report_v4",
            "invalid_prior_artifact_preserved": [
                "artifacts/FSP-PUM-ENV-IDPROBE-001A/s2_tractability_report.json",
                "artifacts/FSP-PUM-ENV-IDPROBE-001A/s2_tractability_report_v2.json",
                "artifacts/FSP-PUM-ENV-IDPROBE-001A/s2_tractability_report_v3.json",
            ],
            "implementation_path": (
                "FactoredExactFilter full joint posterior vector with float64 log-domain updates, "
                "precomputed int32 class indices, query-time logsumexp normalization, certificate-selected "
                "z quadrature, no atom-grid downsizing, no threshold movement, and no mean-field posterior factorization"
            ),
            "posterior_vector": {
                "dtype": str(policy_filter.log_weights.dtype),
                "bytes": int(policy_filter.log_weights.nbytes),
                "shape": list(policy_filter.log_weights.shape),
                "storage": "unnormalized_float64_log_weight_vector",
            },
            "scatter_kernel": policy_filter.scatter_kernel_certificate(),
            "step_cost_breakdown": {
                "before_profile_path": str(before_path) if before_profile is not None else None,
                "before": before_profile,
                "after": after_profile,
            },
            "log_domain_overflow_bound": _log_domain_overflow_bound(),
            "single_thread_wall_clock_seconds": report["measured_wall_clock_seconds"],
            "single_thread_accounting": {
                "explicit_threads": 1,
                "numba_or_threading_used": False,
                "cpu_hour_line_counts_this_number": True,
            },
            "z_selection_contract": {
                "candidate_g_values": [3, 4],
                "selection_rule": "smallest g with g-vs-2g max_abs_prediction_delta < 1e-3",
                "selected_g_used_by_this_report": int(z_quadrature_points),
                "threshold": Z_CONVERGENCE_THRESHOLD,
            },
            "policy_class_cost_note": policy_class_cost_note,
            "producer_function": "src.fsp_pum_env.ideal_observer.run_s2_tractability_benchmark_v4",
            "code_path_hash": _factored_code_path_hash(),
            "claim_ceiling": "S2e log-domain FactoredExactFilter tractability evidence only; no S3, environment-validity, learning, agency, or EGO-mainline claim",
        }
    )
    _write_json_if_requested(output_path, report)
    return report


def run_pc_z_sensitivity_addendum(
    frozen_design_path: str | Path,
    *,
    output_path: str | Path | None = None,
    master_seed: int = 20260716,
    z_quadrature_points: int = 5,
) -> dict[str, Any]:
    start = time.perf_counter()
    path = Path(frozen_design_path)
    design = json.loads(path.read_text(encoding="utf-8-sig"))
    grid = ThetaGridSpec.z_sensitivity_pc_grid(design)
    style_map = tuple(range(int(design["env_parameters"]["renderer"]["response_alphabet_size"])))
    true_sim = FspPumSimulator(design, master_seed=master_seed, variant=SimulatorVariant.CAMOUFLAGE_OFF)
    theta_control = {
        "topic_values": [1.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5],
        "sensitivity_flags": [0, 0],
        "trust_gain_alpha": 0.1,
        "trust_decay_beta": 0.95,
        "disclosure_threshold_d": 0.5,
    }
    true_user = true_sim.start_user(user_id=0, controlled_theta=theta_control, style_map=style_map)
    true_user.z_state = _SessionState(valence=0.8, arousal=0.0, stress=-0.8)
    marginal_filter = ExactBayesFilter(
        design,
        filter_seed=independent_filter_seed(master_seed, "pc_z_addendum_marginal"),
        true_environment_seed=master_seed,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=grid,
        user_id=0,
        style_map=style_map,
        z_quadrature_points=z_quadrature_points,
    )
    z0_filter = ExactBayesFilter(
        design,
        filter_seed=independent_filter_seed(master_seed, "pc_z_addendum_z0"),
        true_environment_seed=master_seed,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=grid,
        user_id=0,
        style_map=style_map,
        z_mode="fixed",
        fixed_z=(0.0, 0.0, 0.0),
    )
    actions = ("task_topic_0", "task_topic_0", "task_topic_0", "task_topic_0")
    marginal_log_likelihoods: list[float] = []
    z0_log_likelihoods: list[float] = []
    rows: list[dict[str, Any]] = []
    for turn_index, action in enumerate(actions):
        symbol = _modal_symbol(true_sim.response_distribution(true_user, action))
        marginal_dist = marginal_filter.predict_distribution(action)
        z0_dist = z0_filter.predict_distribution(action)
        marginal_ll = math.log(max(marginal_dist[symbol], 1e-300))
        z0_ll = math.log(max(z0_dist[symbol], 1e-300))
        marginal_log_likelihoods.append(marginal_ll)
        z0_log_likelihoods.append(z0_ll)
        rows.append(
            {
                "turn_index": turn_index,
                "action": action,
                "symbol": symbol,
                "marginal_log_likelihood": marginal_ll,
                "z0_fixed_log_likelihood": z0_ll,
                "margin": marginal_ll - z0_ll,
            }
        )
        event = PrefixEvent(action=action, symbol=symbol)
        marginal_filter.observe(event)
        z0_filter.observe(event)
        _advance_without_sampling(true_sim, true_user, action)

    marginal_mean = float(sum(marginal_log_likelihoods) / len(marginal_log_likelihoods))
    z0_mean = float(sum(z0_log_likelihoods) / len(z0_log_likelihoods))
    report = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S2c",
        "pc_name": "PC-Z-SENSITIVITY-Z0-ADDENDUM",
        "z_marginalized_mean_log_likelihood": marginal_mean,
        "z0_fixed_mean_log_likelihood": z0_mean,
        "z0_control_margin": marginal_mean - z0_mean,
        "fixed_z_zero": [0.0, 0.0, 0.0],
        "actions": list(actions),
        "rows": rows,
        "z_quadrature_points": z_quadrature_points,
        "wall_clock_seconds": time.perf_counter() - start,
        "producer_function": "src.fsp_pum_env.ideal_observer.run_pc_z_sensitivity_addendum",
        "input_artifacts": [str(path)],
        "code_path_hash": _factored_code_path_hash(),
        "claim_ceiling": "PC-Z-SENSITIVITY addendum evidence only; z=0 comparator does not establish environment validity",
    }
    _write_json_if_requested(output_path, report)
    return report


def _build_factored_index(
    design: Mapping[str, Any],
    grid_spec: ThetaGridSpec,
    simulator: FspPumSimulator,
) -> _FactoredIndex:
    env = design["env_parameters"]
    topic_lengths = [len(levels) for levels in grid_spec.topic_levels_by_index]
    topic_shape = tuple(topic_lengths)
    topic_combo_count = int(np.prod(topic_lengths, dtype=np.int64))
    flag0_len = len(grid_spec.sensitivity_levels_by_index[0])
    flag1_len = len(grid_spec.sensitivity_levels_by_index[1])
    flag_count = flag0_len * flag1_len
    trust_params = list(product(grid_spec.alpha_levels, grid_spec.beta_levels, grid_spec.disclosure_levels))
    trust_count = len(trust_params)
    atom_count = topic_combo_count * flag_count * trust_count

    topic_positions = np.indices(topic_shape, dtype=np.int16).reshape(8, -1)
    flag_positions = np.indices((flag0_len, flag1_len), dtype=np.int16).reshape(2, -1)
    flag0_atom = np.tile(np.repeat(flag_positions[0], trust_count), topic_combo_count).astype(np.int32, copy=False)
    flag1_atom = np.tile(np.repeat(flag_positions[1], trust_count), topic_combo_count).astype(np.int32, copy=False)
    trust_class = np.tile(np.arange(trust_count, dtype=np.int32), topic_combo_count * flag_count)

    action_class_indices: dict[str, np.ndarray] = {}
    action_specs: dict[str, _ActionClassSpec] = {}

    def finish_action(action: str, theta_class_by_atom: np.ndarray, theta_class_count: int, kind: str) -> None:
        class_idx = theta_class_by_atom.astype(np.int32, copy=False) * trust_count + trust_class
        action_class_indices[action] = np.ascontiguousarray(class_idx, dtype=np.int32)
        action_specs[action] = _ActionClassSpec(action=action, theta_class_count=int(theta_class_count), kind=kind)

    topic_atom_cache: dict[int, np.ndarray] = {}

    def topic_atom(index: int) -> np.ndarray:
        cached = topic_atom_cache.get(index)
        if cached is None:
            cached = np.repeat(topic_positions[index], flag_count * trust_count).astype(np.int32, copy=False)
            topic_atom_cache[index] = cached
        return cached

    finish_action("probe_0", flag0_atom, flag0_len, "probe_flag0")
    finish_action("probe_1", flag1_atom, flag1_len, "probe_flag1")
    finish_action("probe_2", topic_atom(7), topic_lengths[7], "probe_topic7")
    probe3_theta = ((flag0_atom * flag1_len + flag1_atom) * topic_lengths[7] + topic_atom(7)).astype(np.int32, copy=False)
    finish_action("probe_3", probe3_theta, flag_count * topic_lengths[7], "probe3")

    pair_by_topic: dict[int, tuple[int, int]] = {}
    for pair in env["preregistered_interaction_pairs"]:
        left, right = (int(name.rsplit("_", 1)[1]) for name in pair["pair"])
        pair_by_topic[left] = (left, right)
        pair_by_topic[right] = (left, right)

    for action in simulator.task_actions:
        topic_index = int(action.rsplit("_", 1)[1])
        if topic_index in pair_by_topic:
            left, right = pair_by_topic[topic_index]
            pair_class = topic_atom(left) * topic_lengths[right] + topic_atom(right)
            finish_action(action, pair_class, topic_lengths[left] * topic_lengths[right], "task_pair")
        else:
            finish_action(action, topic_atom(topic_index), topic_lengths[topic_index], "task_single")

    probe_only = {
        int(name.rsplit("_", 1)[1])
        for name in env["theta_probe_subset"]["dims"]
        if name.startswith("topic_")
    }
    non_probe_indices = [index for index in range(int(env["K_topics"])) if index not in probe_only]
    combo_preferences = np.zeros(topic_combo_count, dtype=np.float64)
    for index in non_probe_indices:
        values = np.asarray(grid_spec.topic_levels_by_index[index], dtype=np.float64)
        combo_preferences += values[topic_positions[index]]
    combo_preferences /= float(len(non_probe_indices))
    unique_preferences, inverse = np.unique(combo_preferences, return_inverse=True)
    recommend_theta = np.repeat(inverse.astype(np.int32), flag_count * trust_count)
    finish_action("recommend", recommend_theta, len(unique_preferences), "recommend")

    topic_class_values = {
        index: np.asarray(grid_spec.topic_levels_by_index[index], dtype=np.float64)
        for index in range(int(env["K_topics"]))
    }
    trust_alpha = np.asarray([item[0] for item in trust_params], dtype=np.float64)
    trust_beta = np.asarray([item[1] for item in trust_params], dtype=np.float64)
    trust_d = np.asarray([item[2] for item in trust_params], dtype=np.float64)
    index_bytes = sum(array.nbytes for array in action_class_indices.values()) + trust_class.nbytes
    return _FactoredIndex(
        action_class_indices=action_class_indices,
        action_specs=action_specs,
        topic_class_values=topic_class_values,
        flag0_values=np.asarray(grid_spec.sensitivity_levels_by_index[0], dtype=np.int32),
        flag1_values=np.asarray(grid_spec.sensitivity_levels_by_index[1], dtype=np.int32),
        recommend_preferences=unique_preferences.astype(np.float64),
        trust_class_indices=trust_class,
        trust_alpha=trust_alpha,
        trust_beta=trust_beta,
        trust_d=trust_d,
        atom_count=atom_count,
        index_arrays_bytes=index_bytes,
    )


def _task_topic_effects(
    design: Mapping[str, Any],
    index: _FactoredIndex,
    topic_index: int,
) -> tuple[np.ndarray, np.ndarray]:
    env = design["env_parameters"]
    probe_only = {
        int(name.rsplit("_", 1)[1])
        for name in env["theta_probe_subset"]["dims"]
        if name.startswith("topic_")
    }
    for pair in env["preregistered_interaction_pairs"]:
        left, right = (int(name.rsplit("_", 1)[1]) for name in pair["pair"])
        if topic_index not in {left, right}:
            continue
        left_values = index.topic_class_values[left]
        right_values = index.topic_class_values[right]
        pairs = np.asarray(list(product(left_values, right_values)), dtype=np.float64)
        topic_values = pairs[:, 0] if topic_index == left else pairs[:, 1]
        topic_effect = np.zeros_like(topic_values) if topic_index in probe_only else topic_values
        interaction = float(pair["gamma"]) * pairs[:, 0] * pairs[:, 1]
        return topic_effect, interaction
    values = index.topic_class_values[topic_index]
    topic_effect = np.zeros_like(values) if topic_index in probe_only else values
    return topic_effect, np.zeros_like(values)


def _peaked_distribution(centers: np.ndarray, strengths: np.ndarray, alphabet_size: int) -> np.ndarray:
    centers = np.asarray(centers, dtype=np.int32) % int(alphabet_size)
    strengths = np.asarray(strengths, dtype=np.float64)
    logits = np.zeros((centers.size, int(alphabet_size)), dtype=np.float64)
    row_index = np.arange(centers.size)
    logits[row_index, centers] = strengths
    logits[row_index, (centers + 1) % int(alphabet_size)] = strengths * 0.35
    logits -= np.max(logits, axis=1, keepdims=True)
    exp_logits = np.exp(logits)
    return exp_logits / exp_logits.sum(axis=1, keepdims=True)


def _apply_style_map(distribution: np.ndarray, style_map: Sequence[int]) -> np.ndarray:
    out = np.empty_like(distribution)
    out[:, np.asarray(style_map, dtype=np.int32)] = distribution
    return out


def _global_topic_level_indices(simulator: FspPumSimulator, values: np.ndarray) -> np.ndarray:
    levels = np.asarray(simulator.theta_topic_levels, dtype=np.float64)
    distances = np.abs(values.reshape(-1, 1) - levels.reshape(1, -1))
    return np.argmin(distances, axis=1).astype(np.int32)


def _certificate_action_sequence() -> tuple[str, ...]:
    base = (
        "probe_0",
        "task_topic_1",
        "task_topic_2",
        "recommend",
        "probe_1",
        "task_topic_5",
        "task_topic_6",
        "task_topic_0",
        "probe_2",
        "task_topic_7",
        "probe_3",
        "task_topic_3",
        "recommend",
        "task_topic_4",
        "task_topic_1",
    )
    return base + base


def _equivalence_cases(design: Mapping[str, Any]) -> list[dict[str, Any]]:
    theta = design["env_parameters"]["theta_structure"]
    full_levels = tuple(float(value) for value in theta["topic_preference_dims"]["grid_levels"])
    fixed_topics = [(-0.5,) for _ in range(8)]
    flags = tuple(int(value) for value in theta["sensitivity_flags"]["grid_levels"])
    alpha = tuple(float(value) for value in theta["trust_gain_alpha"]["grid_levels"])
    beta = tuple(float(value) for value in theta["trust_decay_beta"]["grid_levels"])
    disclosure = tuple(float(value) for value in theta["disclosure_threshold_d"]["grid_levels"])

    topic7_topics = list(fixed_topics)
    topic7_topics[7] = full_levels
    pair_topics = list(fixed_topics)
    pair_topics[1] = full_levels
    pair_topics[2] = full_levels

    return [
        {
            "case_id": "topic7_flags_trust_432",
            "description": "topic_7 all four levels, both sensitivity flags, and all 27 trust alpha/beta/d settings",
            "grid_spec": ThetaGridSpec(
                topic_levels_by_index=tuple(topic7_topics),
                sensitivity_levels_by_index=(flags, flags),
                alpha_levels=alpha,
                beta_levels=beta,
                disclosure_levels=disclosure,
                factor_groups=("topic_7", "sensitivity_flag_0", "sensitivity_flag_1", "trust_gain_alpha", "trust_decay_beta", "disclosure_threshold_d"),
            ),
            "theta_control": {
                "topic_values": [-0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, 1.5],
                "sensitivity_flags": [1, 0],
                "trust_gain_alpha": 0.1,
                "trust_decay_beta": 0.95,
                "disclosure_threshold_d": 0.5,
            },
        },
        {
            "case_id": "paired_topic_1_2_trust_432",
            "description": "paired topic_1/topic_2 joint grid, fixed sensitivity flags, and all 27 trust alpha/beta/d settings",
            "grid_spec": ThetaGridSpec(
                topic_levels_by_index=tuple(pair_topics),
                sensitivity_levels_by_index=((0,), (1,)),
                alpha_levels=alpha,
                beta_levels=beta,
                disclosure_levels=disclosure,
                factor_groups=("joint_topic_1_2", "sensitivity_flags_fixed", "trust_gain_alpha", "trust_decay_beta", "disclosure_threshold_d"),
            ),
            "theta_control": {
                "topic_values": [-0.5, 1.5, -1.5, -0.5, -0.5, -0.5, -0.5, -0.5],
                "sensitivity_flags": [0, 1],
                "trust_gain_alpha": 0.2,
                "trust_decay_beta": 0.9,
                "disclosure_threshold_d": 0.7,
            },
        },
    ]


def _measure_myopic_ig_policy_class_cost(filt: FactoredExactFilter) -> dict[str, Any]:
    start = time.perf_counter()
    current_entropy = filt.posterior_entropy()
    rows: list[dict[str, Any]] = []
    best_action = filt.simulator.probe_actions[0]
    best_gain = -math.inf
    for action in filt.simulator.probe_actions:
        action_start = time.perf_counter()
        expected_entropy = filt.expected_entropy_after_observation(action)
        action_seconds = time.perf_counter() - action_start
        information_gain = current_entropy - expected_entropy
        rows.append(
            {
                "action": action,
                "expected_entropy": expected_entropy,
                "information_gain": information_gain,
                "wall_clock_seconds": action_seconds,
            }
        )
        if information_gain > best_gain:
            best_gain = information_gain
            best_action = action
    return {
        "policy_class": "myopic_IG",
        "probe_actions_evaluated": len(filt.simulator.probe_actions),
        "expected_entropy_computations": len(filt.simulator.probe_actions),
        "measured_grid_atom_count": filt.atom_count,
        "z_quadrature_points_per_dim": filt.z_quadrature.points_per_dim,
        "z_node_count": filt.z_quadrature.node_count,
        "current_entropy": current_entropy,
        "selected_action": best_action,
        "best_information_gain": best_gain,
        "rows": rows,
        "measured_wall_clock_seconds": time.perf_counter() - start,
        "producer_function": "src.fsp_pum_env.ideal_observer._measure_myopic_ig_policy_class_cost",
        "claim_ceiling": "S4 budgeting note only; no policy-class decision line and no tractability verdict change",
    }


def _profile_factored_update_step(
    design: Mapping[str, Any],
    *,
    grid_spec: ThetaGridSpec,
    master_seed: int,
    z_quadrature_points: int,
    profile_id: str,
) -> dict[str, Any]:
    env = design["env_parameters"]
    style_map = tuple(range(int(env["renderer"]["response_alphabet_size"])))
    true_sim = FspPumSimulator(design, master_seed=master_seed, variant=SimulatorVariant.CAMOUFLAGE_OFF)
    true_user = true_sim.start_user(user_id=0, style_map=style_map)
    init_start = time.perf_counter()
    filt = FactoredExactFilter(
        design,
        filter_seed=independent_filter_seed(master_seed, profile_id),
        true_environment_seed=master_seed,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=grid_spec,
        user_id=0,
        style_map=style_map,
        z_quadrature_points=z_quadrature_points,
    )
    init_seconds = time.perf_counter() - init_start
    schedule = FixedProbeSchedule(probe_rate=0.2, placement="uniform").actions_for_episode(design)
    action = schedule[0]
    result = true_sim.step(true_user, action)
    symbol = int(result.observation["symbol"])

    profile_start = time.perf_counter()
    step_start = time.perf_counter()
    table = filt._distribution_table(action)
    table_seconds = time.perf_counter() - step_start
    class_indices = filt._index.action_class_indices[action]
    step_start = time.perf_counter()
    log_likelihood_by_class = np.log(np.maximum(table[:, symbol], 1e-300))
    temporaries_seconds = time.perf_counter() - step_start
    step_start = time.perf_counter()
    filt.log_weights[:] += log_likelihood_by_class[class_indices]
    indexed_log_add_seconds = time.perf_counter() - step_start
    step_start = time.perf_counter()
    filt._invalidate_normalized_weights()
    filt._advance_trust(action)
    filt.events.append(PrefixEvent(action=action, symbol=symbol))
    filt._table_cache.clear()
    bookkeeping_seconds = time.perf_counter() - step_start
    manual_update_seconds = time.perf_counter() - profile_start

    query_action = "task_topic_0"
    step_start = time.perf_counter()
    query_table = filt._distribution_table(query_action)
    query_table_seconds = time.perf_counter() - step_start
    step_start = time.perf_counter()
    query_weights = filt._ensure_normalized_weights()
    query_exp_shift_seconds = time.perf_counter() - step_start
    step_start = time.perf_counter()
    query_classes = filt._index.action_class_indices[query_action]
    class_masses = np.bincount(query_classes, weights=query_weights, minlength=query_table.shape[0])
    query_bincount_seconds = time.perf_counter() - step_start
    step_start = time.perf_counter()
    mixture = class_masses @ query_table
    query_mix_seconds = time.perf_counter() - step_start
    step_start = time.perf_counter()
    query_total = float(mixture.sum())
    prediction = (mixture / query_total).tolist()
    query_normalize_seconds = time.perf_counter() - step_start

    return {
        "profile_scope": "one full-grid update step plus one class-aggregated query path after S2e log-domain optimization",
        "full_grid_atom_count": int(grid_spec.atom_count),
        "posterior_vector_bytes": int(filt.log_weights.nbytes),
        "class_indices_dtype": str(class_indices.dtype),
        "z_quadrature_points_per_dim": int(z_quadrature_points),
        "z_node_count": int(z_quadrature_points) ** 3,
        "action_profiled": action,
        "observed_symbol": symbol,
        "initialization_seconds": init_seconds,
        "update_breakdown_seconds": {
            "likelihood_table_build": table_seconds,
            "temporaries": temporaries_seconds,
            "indexed_log_add": indexed_log_add_seconds,
            "gather": 0.0,
            "multiply": 0.0,
            "normalize": 0.0,
            "advance_trust_and_bookkeeping": bookkeeping_seconds,
            "manual_update_total": manual_update_seconds,
        },
        "query_profile": {
            "query_action": query_action,
            "likelihood_table_build": query_table_seconds,
            "exp_shifted_weight_normalization": query_exp_shift_seconds,
            "class_bincount": query_bincount_seconds,
            "small_table_mix": query_mix_seconds,
            "normalize_distribution": query_normalize_seconds,
            "query_total": query_table_seconds
            + query_exp_shift_seconds
            + query_bincount_seconds
            + query_mix_seconds
            + query_normalize_seconds,
            "prediction_checksum": float(prediction[0]),
        },
        "atom_vector_pass_estimate": {
            "indexed_log_add_atom_vector_passes": "one advanced-index gather plus in-place log-vector add",
            "per_step_normalization_atom_vector_passes": 0,
            "query_time_exp_shift_atom_vector_passes": "only on first query after an update; cached for sibling query actions",
        },
        "producer_function": "src.fsp_pum_env.factored_filter._profile_factored_update_step",
        "code_path_hash": _factored_code_path_hash(),
        "claim_ceiling": "S2e post-change profile only; no tractability verdict and no environment-validity claim",
    }


def _read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _log_domain_overflow_bound() -> dict[str, Any]:
    min_log_likelihood = math.log(1e-300)
    max_turns = 300
    worst_case_log_weight_after_300 = -math.log(7_077_888) + max_turns * min_log_likelihood
    return {
        "max_turns": max_turns,
        "likelihood_floor": 1e-300,
        "min_log_likelihood_per_turn": min_log_likelihood,
        "initial_full_grid_log_weight": -math.log(7_077_888),
        "worst_case_log_weight_after_300_floor_hits": worst_case_log_weight_after_300,
        "float64_min_finite": float(np.finfo(np.float64).min),
        "float64_max_finite": float(np.finfo(np.float64).max),
        "query_exp_shift_max_exponent": 0.0,
        "float64_path_can_overflow": False,
        "argument": "Log weights only add finite log likelihoods; after logsumexp shifting, every exponent is <= 0, so exp cannot overflow over the frozen 300-step horizon.",
    }


def _factored_code_path_hash() -> str:
    h = hashlib.sha256()
    for path in (Path(__file__), Path(__file__).with_name("ideal_observer.py"), Path(__file__).with_name("simulator.py")):
        h.update(path.name.encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _current_rss_bytes() -> int | None:
    if os.name == "nt":
        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_ulong),
                ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
        kernel32 = ctypes.WinDLL("kernel32.dll")
        psapi = ctypes.WinDLL("psapi.dll")
        psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), ctypes.c_ulong]
        psapi.GetProcessMemoryInfo.restype = ctypes.c_bool
        handle = kernel32.GetCurrentProcess()
        ok = psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb)
        if ok:
            return int(counters.WorkingSetSize)
        return None
    try:
        import resource

        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(rss * 1024)
    except Exception:
        return None


def _sample_memory_peaks(current_rss_peak: int | None, current_trace_peak: int) -> tuple[int | None, int]:
    rss = _current_rss_bytes()
    if rss is not None:
        current_rss_peak = rss if current_rss_peak is None else max(current_rss_peak, rss)
    _, trace_peak = tracemalloc.get_traced_memory()
    return current_rss_peak, max(current_trace_peak, int(trace_peak))
