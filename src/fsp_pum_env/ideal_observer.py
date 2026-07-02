"""S2 exact-grid ideal-observer instrumentation for FSP-PUM-ENV-IDPROBE-001A.

This module is an oracle instrument, not a candidate mechanism. Its allowed
information interface is: frozen generator kernels, the public action/observation
prefix, and the per-user style map. It must not receive theta, z realizations,
true environment sampling seeds, or future observations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from .simulator import (
    FspPumSimulator,
    SimulatorVariant,
    _SessionState,
    _UserState,
    contains_latent_leak,
)


PC_IDEAL_SANITY_THRESHOLD = 0.95
Z_CONVERGENCE_THRESHOLD = 1e-3
S5_CPU_HOUR_LIMIT = 24.0


@dataclass(frozen=True)
class PrefixEvent:
    action: str
    symbol: int

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "PrefixEvent":
        if contains_latent_leak(payload):
            raise ValueError("prefix-only event cannot contain latent fields")
        allowed_keys = {"action", "observation", "symbol"}
        extra = set(payload) - allowed_keys
        if extra:
            raise ValueError(f"prefix-only event has forbidden keys: {sorted(extra)}")
        action = payload.get("action")
        if not isinstance(action, str):
            raise ValueError("prefix-only event requires string action")
        if "symbol" in payload:
            symbol = payload["symbol"]
        else:
            observation = payload.get("observation")
            if not isinstance(observation, Mapping) or set(observation) != {"symbol"}:
                raise ValueError("prefix-only observation must contain only symbol")
            symbol = observation["symbol"]
        if not isinstance(symbol, int):
            raise ValueError("prefix-only observation symbol must be an int")
        return cls(action=action, symbol=int(symbol))


@dataclass(frozen=True)
class ThetaGridSpec:
    topic_levels_by_index: tuple[tuple[float, ...], ...]
    sensitivity_levels_by_index: tuple[tuple[int, ...], tuple[int, ...]]
    alpha_levels: tuple[float, ...]
    beta_levels: tuple[float, ...]
    disclosure_levels: tuple[float, ...]
    factor_groups: tuple[str, ...]

    @classmethod
    def from_design(cls, design: Mapping[str, Any]) -> "ThetaGridSpec":
        env = design["env_parameters"]
        theta = env["theta_structure"]
        levels = tuple(float(v) for v in theta["topic_preference_dims"]["grid_levels"])
        topic_levels = tuple(levels for _ in range(int(env["K_topics"])))
        sensitivity_levels = tuple(int(v) for v in theta["sensitivity_flags"]["grid_levels"])
        return cls(
            topic_levels_by_index=topic_levels,
            sensitivity_levels_by_index=(sensitivity_levels, sensitivity_levels),
            alpha_levels=tuple(float(v) for v in theta["trust_gain_alpha"]["grid_levels"]),
            beta_levels=tuple(float(v) for v in theta["trust_decay_beta"]["grid_levels"]),
            disclosure_levels=tuple(float(v) for v in theta["disclosure_threshold_d"]["grid_levels"]),
            factor_groups=_factor_groups_from_design(design),
        )

    @classmethod
    def micro_pc_grid(cls, design: Mapping[str, Any]) -> "ThetaGridSpec":
        env = design["env_parameters"]
        theta = env["theta_structure"]
        topic_levels = []
        for index in range(int(env["K_topics"])):
            if index == 7:
                topic_levels.append(tuple(float(v) for v in theta["topic_preference_dims"]["grid_levels"]))
            else:
                topic_levels.append((-0.5,))
        sensitivity_levels = tuple(int(v) for v in theta["sensitivity_flags"]["grid_levels"])
        return cls(
            topic_levels_by_index=tuple(topic_levels),
            sensitivity_levels_by_index=(sensitivity_levels, sensitivity_levels),
            alpha_levels=(0.1,),
            beta_levels=(0.95,),
            disclosure_levels=(0.5,),
            factor_groups=("topic_7", "sensitivity_flag_0", "sensitivity_flag_1", "alpha_beta_d_fixed"),
        )

    @classmethod
    def z_sensitivity_pc_grid(cls, design: Mapping[str, Any]) -> "ThetaGridSpec":
        env = design["env_parameters"]
        theta = env["theta_structure"]
        topic_levels = []
        for index in range(int(env["K_topics"])):
            if index == 0:
                topic_levels.append(tuple(float(v) for v in theta["topic_preference_dims"]["grid_levels"]))
            else:
                topic_levels.append((-0.5,))
        return cls(
            topic_levels_by_index=tuple(topic_levels),
            sensitivity_levels_by_index=((0,), (0,)),
            alpha_levels=(0.1,),
            beta_levels=(0.95,),
            disclosure_levels=(0.5,),
            factor_groups=("topic_0", "alpha_beta_d_fixed"),
        )

    @property
    def atom_count(self) -> int:
        count = 1
        for levels in self.topic_levels_by_index:
            count *= len(levels)
        for levels in self.sensitivity_levels_by_index:
            count *= len(levels)
        count *= len(self.alpha_levels) * len(self.beta_levels) * len(self.disclosure_levels)
        return int(count)

    def iter_theta_controls(self) -> Sequence[dict[str, Any]]:
        atoms: list[dict[str, Any]] = []
        for topics in product(*self.topic_levels_by_index):
            for flags in product(*self.sensitivity_levels_by_index):
                for alpha, beta, disclosure in product(self.alpha_levels, self.beta_levels, self.disclosure_levels):
                    atoms.append(
                        {
                            "topic_values": list(topics),
                            "sensitivity_flags": list(flags),
                            "trust_gain_alpha": float(alpha),
                            "trust_decay_beta": float(beta),
                            "disclosure_threshold_d": float(disclosure),
                        }
                    )
        return atoms


@dataclass
class _WeightedAtom:
    theta_control: dict[str, Any]
    user: _UserState
    log_weight: float


@dataclass(frozen=True)
class ZQuadrature:
    scheme: str
    points_per_dim: int
    nodes: tuple[tuple[float, float, float], ...]
    weights: tuple[float, ...]

    @property
    def node_count(self) -> int:
        return len(self.weights)


@dataclass(frozen=True)
class FixedProbeSchedule:
    probe_rate: float
    placement: str

    @property
    def name(self) -> str:
        return f"rate_{self.probe_rate:g}_{self.placement}"

    def actions_for_episode(self, design: Mapping[str, Any]) -> list[str]:
        env = design["env_parameters"]
        total_turns = int(env["episodes"]["total_turns_per_user"])
        task_actions = list(env["action_set"]["task_actions"])
        probe_actions = [item["name"] for item in env["action_set"]["probe_actions"]]
        n_probes = int(round(total_turns * self.probe_rate))
        actions = [task_actions[index % len(task_actions)] for index in range(total_turns)]
        for probe_number, position in enumerate(_schedule_positions(total_turns, n_probes, self.placement)):
            actions[position] = probe_actions[probe_number % len(probe_actions)]
        return actions


class ExactBayesFilter:
    """Exact posterior over a finite theta grid using simulator likelihoods."""

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
        z_mode: str = "marginalized",
        fixed_z: Sequence[float] | None = None,
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
        self.z_mode = z_mode
        self.fixed_z = tuple(float(value) for value in fixed_z) if fixed_z is not None else (0.0, 0.0, 0.0)
        if self.z_mode not in {"marginalized", "fixed"}:
            raise ValueError("z_mode must be marginalized or fixed")
        self.events: list[PrefixEvent] = []
        self._initial_theta_controls = list(self.grid_spec.iter_theta_controls())
        self._atoms: list[_WeightedAtom] = []
        self.reset()

    @classmethod
    def from_frozen_design(
        cls,
        path: str | Path,
        *,
        filter_seed: int,
        variant: SimulatorVariant | str,
        style_map: Sequence[int],
        grid_spec: ThetaGridSpec | None = None,
        user_id: int = 0,
        true_environment_seed: int | None = None,
        z_quadrature_points: int = 5,
    ) -> "ExactBayesFilter":
        design = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        return cls(
            design,
            filter_seed=filter_seed,
            variant=variant,
            grid_spec=grid_spec,
            user_id=user_id,
            style_map=style_map,
            true_environment_seed=true_environment_seed,
            z_quadrature_points=z_quadrature_points,
        )

    @property
    def atom_count(self) -> int:
        return len(self._atoms)

    def reset(self) -> None:
        atom_count = len(self._initial_theta_controls)
        if atom_count <= 0:
            raise ValueError("theta grid must contain at least one atom")
        log_weight = -math.log(atom_count)
        self._atoms = [
            _WeightedAtom(
                theta_control=theta_control,
                user=self.simulator.start_user(
                    user_id=self.user_id,
                    controlled_theta=theta_control,
                    style_map=self.style_map,
                ),
                log_weight=log_weight,
            )
            for theta_control in self._initial_theta_controls
        ]
        self.events = []

    def observe(self, event: PrefixEvent | Mapping[str, Any]) -> None:
        prefix_event = event if isinstance(event, PrefixEvent) else PrefixEvent.from_mapping(event)
        self.simulator._validate_action(prefix_event.action)
        if not 0 <= prefix_event.symbol < self.simulator.alphabet_size:
            raise ValueError("prefix-only observation symbol outside response alphabet")

        for atom in self._atoms:
            distribution = self._atom_distribution(atom.user, prefix_event.action)
            likelihood = max(float(distribution[prefix_event.symbol]), 1e-300)
            atom.log_weight += math.log(likelihood)
            _advance_filter_state_without_sampling(self.simulator, atom.user, prefix_event.action)
        self._normalize()
        self.events.append(prefix_event)

    def posterior_mass(self) -> float:
        return float(sum(math.exp(atom.log_weight) for atom in self._atoms))

    def posterior_entropy(self) -> float:
        total = 0.0
        for atom in self._atoms:
            weight = math.exp(atom.log_weight)
            if weight > 0.0:
                total -= weight * math.log(weight)
        return float(total)

    def posterior_marginal(self, key: str) -> dict[Any, float]:
        out: dict[Any, float] = {}
        for atom in self._atoms:
            value = _theta_value(atom.theta_control, key)
            out[value] = out.get(value, 0.0) + math.exp(atom.log_weight)
        return out

    def predict_distribution(self, action: str) -> list[float]:
        self.simulator._validate_action(action)
        mixture = np.zeros(self.simulator.alphabet_size, dtype=float)
        for atom in self._atoms:
            user_copy = _clone_user(atom.user)
            mixture += math.exp(atom.log_weight) * np.asarray(self._atom_distribution(user_copy, action), dtype=float)
        total = float(mixture.sum())
        if total <= 0.0:
            raise ValueError("posterior predictive has zero mass")
        return (mixture / total).tolist()

    def most_likely_symbol(self, action: str) -> int:
        return int(np.argmax(np.asarray(self.predict_distribution(action), dtype=float)))

    def _normalize(self) -> None:
        log_norm = _logsumexp([atom.log_weight for atom in self._atoms])
        for atom in self._atoms:
            atom.log_weight -= log_norm

    def _atom_distribution(self, user: _UserState, action: str) -> list[float]:
        if self.z_mode == "fixed":
            fixed_user = _clone_user(user)
            fixed_user.z_state = _SessionState(*self.fixed_z)
            return self.simulator.response_distribution(fixed_user, action)
        return _z_marginalized_distribution(self.simulator, user, action, self.z_quadrature)

    def information_interface(self) -> dict[str, Any]:
        return {
            "generator_access": ["distribution_kernels", "per_user_style_map"],
            "sees_theta": False,
            "sees_z_realization": False,
            "sees_sampling_seeds": False,
            "prefix_only": True,
            "z_marginalization": {
                "scheme": self.z_quadrature.scheme,
                "points_per_dim": self.z_quadrature.points_per_dim,
                "node_count": self.z_quadrature.node_count,
            },
        }


@dataclass
class S2VariantWrapper:
    name: str
    core: ExactBayesFilter
    history_limit: int | None = None
    policy_kind: str = "predictor"
    history: list[PrefixEvent] = field(default_factory=list)
    ucb_counts: dict[str, int] = field(default_factory=dict)
    ucb_rewards: dict[str, float] = field(default_factory=dict)
    fixed_schedules: tuple[FixedProbeSchedule, ...] = ()
    fixed_schedule_index: int = 0

    def observe_prefix(self, events: Sequence[PrefixEvent | Mapping[str, Any]]) -> None:
        parsed = [event if isinstance(event, PrefixEvent) else PrefixEvent.from_mapping(event) for event in events]
        selected = parsed[-self.history_limit :] if self.history_limit is not None else parsed
        if self.history_limit is None and selected[: len(self.history)] == self.history:
            for event in selected[len(self.history) :]:
                self.core.observe(event)
        else:
            self.core.reset()
            for event in selected:
                self.core.observe(event)
        self.history = selected

    def predict_distribution(self, action: str) -> list[float]:
        return self.core.predict_distribution(action)

    def select_action(self, step_index: int) -> str:
        simulator = self.core.simulator
        if self.policy_kind == "passive":
            return simulator.task_actions[int(step_index) % len(simulator.task_actions)]
        if self.policy_kind == "fixed_schedule_grid":
            if not self.fixed_schedules:
                raise ValueError("fixed_schedule_grid wrapper has no schedules")
            actions = self.fixed_schedules[self.fixed_schedule_index].actions_for_episode(self.core.design)
            return actions[int(step_index) % len(actions)]
        if self.policy_kind == "myopic_IG":
            return _myopic_ig_action(self.core)
        if self.policy_kind == "ucb1":
            return self._ucb1_action(int(step_index))
        return simulator.task_actions[int(step_index) % len(simulator.task_actions)]

    def record_ucb_reward(self, action: str, reward: float) -> None:
        self.ucb_counts[action] = self.ucb_counts.get(action, 0) + 1
        self.ucb_rewards[action] = self.ucb_rewards.get(action, 0.0) + float(reward)

    def _ucb1_action(self, step_index: int) -> str:
        simulator = self.core.simulator
        arms = tuple(simulator.probe_actions) + ("no_probe",)
        for arm in arms:
            if self.ucb_counts.get(arm, 0) == 0:
                return simulator.task_actions[step_index % len(simulator.task_actions)] if arm == "no_probe" else arm
        total = sum(self.ucb_counts.values())
        exploration = 1.0
        best_arm = max(
            arms,
            key=lambda arm: (self.ucb_rewards[arm] / self.ucb_counts[arm])
            + exploration * math.sqrt(2.0 * math.log(total) / self.ucb_counts[arm]),
        )
        return simulator.task_actions[step_index % len(simulator.task_actions)] if best_arm == "no_probe" else best_arm


def make_s2_variant_wrappers(
    design: Mapping[str, Any],
    *,
    filter_seed: int,
    style_map: Sequence[int],
    variant: SimulatorVariant | str = SimulatorVariant.CAMOUFLAGE_OFF,
    grid_spec: ThetaGridSpec | None = None,
    true_environment_seed: int | None = None,
    z_quadrature_points: int = 5,
) -> dict[str, S2VariantWrapper]:
    truncation_b = int(design["env_parameters"]["episodes"]["T_turns_per_session"]) * 2
    declared_b = int(design["gap3_truncation"]["B"])
    if truncation_b != declared_b:
        truncation_b = declared_b

    def core_for(offset: int) -> ExactBayesFilter:
        return ExactBayesFilter(
            design,
            filter_seed=filter_seed + offset,
            variant=variant,
            grid_spec=grid_spec,
            style_map=style_map,
            true_environment_seed=true_environment_seed,
            z_quadrature_points=z_quadrature_points,
        )

    return {
        "full_history": S2VariantWrapper("full_history", core_for(0), history_limit=None, policy_kind="full_history"),
        "truncation_B30": S2VariantWrapper("truncation_B30", core_for(1), history_limit=truncation_b, policy_kind="truncation"),
        "passive": S2VariantWrapper("passive", core_for(2), history_limit=None, policy_kind="passive"),
        "myopic_IG": S2VariantWrapper("myopic_IG", core_for(3), history_limit=None, policy_kind="myopic_IG"),
        "fixed_schedule_grid": S2VariantWrapper(
            "fixed_schedule_grid",
            core_for(4),
            history_limit=None,
            policy_kind="fixed_schedule_grid",
            fixed_schedules=tuple(make_fixed_probe_schedules(design)),
            fixed_schedule_index=3,
        ),
        "ucb1": S2VariantWrapper("ucb1", core_for(5), history_limit=None, policy_kind="ucb1"),
    }


def run_pc_ideal_sanity(
    frozen_design_path: str | Path,
    *,
    output_path: str | Path | None = None,
    master_seed: int = 20260710,
    z_quadrature_points: int = 5,
) -> dict[str, Any]:
    start = time.perf_counter()
    path = Path(frozen_design_path)
    design = json.loads(path.read_text(encoding="utf-8-sig"))
    grid = ThetaGridSpec.micro_pc_grid(design)
    full_grid = ThetaGridSpec.from_design(design)
    true_sim = FspPumSimulator(design, master_seed=master_seed, variant=SimulatorVariant.CAMOUFLAGE_OFF)
    style_map = tuple(range(true_sim.alphabet_size))
    observation_actions = ("probe_0", "probe_1", "probe_2", "probe_3")
    query_actions = ("probe_0", "probe_1", "probe_2", "probe_3")
    filter_seed = independent_filter_seed(master_seed, "pc_ideal_sanity")

    correct = 0
    total = 0
    entropy_drops: list[float] = []
    case_ids: list[str] = []
    for case_index, theta_control in enumerate(grid.iter_theta_controls()):
        case_ids.append(f"micro_case_{case_index:02d}")
        true_user = true_sim.start_user(user_id=case_index, controlled_theta=theta_control, style_map=style_map)
        filt = ExactBayesFilter(
            design,
            filter_seed=filter_seed,
            true_environment_seed=master_seed,
            variant=SimulatorVariant.CAMOUFLAGE_OFF,
            grid_spec=grid,
            user_id=case_index,
            style_map=style_map,
            z_quadrature_points=z_quadrature_points,
        )
        before_entropy = filt.posterior_entropy()
        for action in observation_actions:
            symbol = _modal_symbol(true_sim.response_distribution(true_user, action))
            filt.observe(PrefixEvent(action=action, symbol=symbol))
            _advance_without_sampling(true_sim, true_user, action)
        entropy_drops.append(before_entropy - filt.posterior_entropy())

        for action in query_actions:
            predicted = filt.most_likely_symbol(action)
            expected = _modal_symbol(true_sim.response_distribution(_clone_user(true_user), action))
            correct += int(predicted == expected)
            total += 1

    pc_value = correct / total if total else 0.0
    wall_clock = time.perf_counter() - start
    report = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S2",
        "pc_name": "PC-IDEAL-SANITY",
        "pc_ideal_sanity": pc_value,
        "threshold": PC_IDEAL_SANITY_THRESHOLD,
        "passed": pc_value >= PC_IDEAL_SANITY_THRESHOLD,
        "producer_function": "src.fsp_pum_env.ideal_observer.run_pc_ideal_sanity",
        "input_artifacts": [str(path)],
        "run_id": f"FSP-PUM-ENV-IDPROBE-001A:S2:PC-IDEAL-SANITY:{master_seed}",
        "seed_context_episode_ids": {
            "master_seed": master_seed,
            "filter_seed": filter_seed,
            "micro_case_ids": case_ids,
            "observation_actions": list(observation_actions),
            "query_actions": list(query_actions),
        },
        "aggregation_rule": "mean modal-response accuracy over micro theta cases and query actions",
        "atom_count": grid.atom_count,
        "estimated_full_d1_atom_count": full_grid.atom_count,
        "factor_groups": list(grid.factor_groups),
        "full_grid_factor_groups": list(full_grid.factor_groups),
        "wall_clock_seconds": wall_clock,
        "mean_entropy_drop": float(sum(entropy_drops) / len(entropy_drops)) if entropy_drops else 0.0,
        "information_interface": ExactBayesFilter(
            design,
            filter_seed=filter_seed,
            true_environment_seed=master_seed,
            variant=SimulatorVariant.CAMOUFLAGE_OFF,
            grid_spec=grid,
            style_map=style_map,
            z_quadrature_points=z_quadrature_points,
        ).information_interface(),
        "code_path_hash": _code_path_hash(),
        "claim_ceiling": "PC-IDEAL-SANITY instrument evidence only",
    }

    if output_path is not None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if not report["passed"]:
            failure = {
                "task_id": report["task_id"],
                "stage": "S2",
                "failure": "PC_IDEAL_SANITY_BELOW_THRESHOLD",
                "pc_ideal_sanity": pc_value,
                "threshold": PC_IDEAL_SANITY_THRESHOLD,
                "claim_ceiling": report["claim_ceiling"],
            }
            out.with_name("failure_manifest.json").write_text(
                json.dumps(failure, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
    return report


def run_z_marginalization_convergence(
    frozen_design_path: str | Path,
    *,
    output_path: str | Path | None = None,
    master_seed: int = 20260712,
    base_g: int = 5,
) -> dict[str, Any]:
    start = time.perf_counter()
    path = Path(frozen_design_path)
    design = json.loads(path.read_text(encoding="utf-8-sig"))
    grid = ThetaGridSpec.z_sensitivity_pc_grid(design)
    style_map = tuple(range(int(design["env_parameters"]["renderer"]["response_alphabet_size"])))
    episode_cases = [
        {
            "case_id": "conv_case_topic0_low",
            "theta": {
                "topic_values": [-1.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5],
                "sensitivity_flags": [0, 0],
                "trust_gain_alpha": 0.1,
                "trust_decay_beta": 0.95,
                "disclosure_threshold_d": 0.5,
            },
        },
        {
            "case_id": "conv_case_topic0_high",
            "theta": {
                "topic_values": [1.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5],
                "sensitivity_flags": [0, 0],
                "trust_gain_alpha": 0.1,
                "trust_decay_beta": 0.95,
                "disclosure_threshold_d": 0.5,
            },
        },
    ]
    prefix_actions = ("probe_0", "task_topic_0", "task_topic_2", "recommend")
    query_actions = ("probe_0", "task_topic_0", "task_topic_2", "recommend")
    max_delta = 0.0
    rows = []

    for case_index, case in enumerate(episode_cases):
        true_sim = FspPumSimulator(design, master_seed=master_seed + case_index, variant=SimulatorVariant.CAMOUFLAGE_OFF)
        true_user = true_sim.start_user(user_id=case_index, controlled_theta=case["theta"], style_map=style_map)
        filt_g = ExactBayesFilter(
            design,
            filter_seed=independent_filter_seed(master_seed, f"conv_g:{case_index}"),
            true_environment_seed=master_seed + case_index,
            variant=SimulatorVariant.CAMOUFLAGE_OFF,
            grid_spec=grid,
            user_id=case_index,
            style_map=style_map,
            z_quadrature_points=base_g,
        )
        filt_2g = ExactBayesFilter(
            design,
            filter_seed=independent_filter_seed(master_seed, f"conv_2g:{case_index}"),
            true_environment_seed=master_seed + case_index,
            variant=SimulatorVariant.CAMOUFLAGE_OFF,
            grid_spec=grid,
            user_id=case_index,
            style_map=style_map,
            z_quadrature_points=2 * base_g,
        )
        for action in prefix_actions:
            for query_action in query_actions:
                delta = _max_abs_diff(filt_g.predict_distribution(query_action), filt_2g.predict_distribution(query_action))
                max_delta = max(max_delta, delta)
                rows.append({"case_id": case["case_id"], "prefix_before": action, "query_action": query_action, "max_abs_delta": delta})
            symbol = _modal_symbol(true_sim.response_distribution(true_user, action))
            event = PrefixEvent(action=action, symbol=symbol)
            filt_g.observe(event)
            filt_2g.observe(event)
            _advance_without_sampling(true_sim, true_user, action)

    wall_clock = time.perf_counter() - start
    report = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S2b",
        "artifact": "z_marginalization_convergence",
        "scheme": "tensor Gauss-Hermite over stationary 3D z marginal per turn",
        "base_g": base_g,
        "double_g": 2 * base_g,
        "base_node_count": base_g ** 3,
        "double_node_count": (2 * base_g) ** 3,
        "threshold": Z_CONVERGENCE_THRESHOLD,
        "max_abs_prediction_delta": max_delta,
        "passed": max_delta < Z_CONVERGENCE_THRESHOLD,
        "episode_set": [case["case_id"] for case in episode_cases],
        "prefix_actions": list(prefix_actions),
        "query_actions": list(query_actions),
        "rows": rows,
        "wall_clock_seconds": wall_clock,
        "producer_function": "src.fsp_pum_env.ideal_observer.run_z_marginalization_convergence",
        "code_path_hash": _code_path_hash(),
        "claim_ceiling": "z-marginalization convergence certificate for S2 instrument only",
    }
    _write_json_if_requested(output_path, report)
    return report


def run_pc_z_sensitivity(
    frozen_design_path: str | Path,
    *,
    output_path: str | Path | None = None,
    master_seed: int = 20260713,
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
        filter_seed=independent_filter_seed(master_seed, "pc_z_marginal"),
        true_environment_seed=master_seed,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=grid,
        user_id=0,
        style_map=style_map,
        z_quadrature_points=z_quadrature_points,
    )
    wrong_fixed_filter = ExactBayesFilter(
        design,
        filter_seed=independent_filter_seed(master_seed, "pc_z_wrong_fixed"),
        true_environment_seed=master_seed,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=grid,
        user_id=0,
        style_map=style_map,
        z_mode="fixed",
        fixed_z=(-4.0, 0.0, 4.0),
    )
    actions = ("task_topic_0", "task_topic_0", "task_topic_0", "task_topic_0")
    marginal_log_likelihoods = []
    wrong_log_likelihoods = []
    for action in actions:
        symbol = _modal_symbol(true_sim.response_distribution(true_user, action))
        marginal_dist = marginal_filter.predict_distribution(action)
        wrong_dist = wrong_fixed_filter.predict_distribution(action)
        marginal_log_likelihoods.append(math.log(max(marginal_dist[symbol], 1e-300)))
        wrong_log_likelihoods.append(math.log(max(wrong_dist[symbol], 1e-300)))
        event = PrefixEvent(action=action, symbol=symbol)
        marginal_filter.observe(event)
        wrong_fixed_filter.observe(event)
        _advance_without_sampling(true_sim, true_user, action)

    marginal_mean = float(sum(marginal_log_likelihoods) / len(marginal_log_likelihoods))
    wrong_mean = float(sum(wrong_log_likelihoods) / len(wrong_log_likelihoods))
    report = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S2b",
        "pc_name": "PC-Z-SENSITIVITY",
        "z_marginalized_mean_log_likelihood": marginal_mean,
        "wrong_fixed_z_mean_log_likelihood": wrong_mean,
        "margin": marginal_mean - wrong_mean,
        "passed": marginal_mean > wrong_mean,
        "actions": list(actions),
        "wrong_fixed_z": [-4.0, 0.0, 4.0],
        "z_quadrature_points": z_quadrature_points,
        "wall_clock_seconds": time.perf_counter() - start,
        "producer_function": "src.fsp_pum_env.ideal_observer.run_pc_z_sensitivity",
        "code_path_hash": _code_path_hash(),
        "claim_ceiling": "PC-Z-SENSITIVITY instrument evidence only",
    }
    _write_json_if_requested(output_path, report)
    return report


def run_s2_tractability_benchmark(
    frozen_design_path: str | Path,
    *,
    output_path: str | Path | None = None,
    benchmark_turns: int | None = None,
    benchmark_queries: int | None = None,
    z_quadrature_points: int = 5,
) -> dict[str, Any]:
    start = time.perf_counter()
    path = Path(frozen_design_path)
    design = json.loads(path.read_text(encoding="utf-8-sig"))
    full_grid = ThetaGridSpec.from_design(design)
    env = design["env_parameters"]
    eval_cfg = design["evaluation"]
    total_turns = int(env["episodes"]["total_turns_per_user"])
    total_queries = int(eval_cfg["query_points"]["queries_per_user"]) * len(eval_cfg["counterfactual_action_set_per_query"])
    turns = total_turns if benchmark_turns is None else int(benchmark_turns)
    queries = total_queries if benchmark_queries is None else int(benchmark_queries)
    schedule = FixedProbeSchedule(probe_rate=0.2, placement="uniform").actions_for_episode(design)[:turns]
    query_actions = list(eval_cfg["counterfactual_action_set_per_query"])
    expanded_queries = [query_actions[index % len(query_actions)] for index in range(queries)]

    distinct_values_processed = 0
    for step_index, action in enumerate(schedule):
        distinct_values_processed += _benchmark_distinct_likelihood_values(design, action, step_index, z_quadrature_points)
    for step_index, action in enumerate(expanded_queries):
        distinct_values_processed += _benchmark_distinct_likelihood_values(design, action, step_index, z_quadrature_points)

    measured_seconds = time.perf_counter() - start
    benchmark_units = max(turns + queries, 1)
    seconds_per_user = measured_seconds * ((total_turns + total_queries) / benchmark_units)
    projected_s5_seconds = seconds_per_user * 10 * 200
    projected_s5_cpu_hours = projected_s5_seconds / 3600.0
    decision = "tractable" if projected_s5_cpu_hours <= S5_CPU_HOUR_LIMIT else "stop_N0_F3_required"
    report = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S2b",
        "artifact": "s2_tractability_report",
        "benchmark_scope": {
            "measured_turns": turns,
            "measured_counterfactual_queries": queries,
            "full_episode_turns": total_turns,
            "full_episode_counterfactual_queries": total_queries,
        },
        "implementation_path": "factored full-grid distinct-likelihood benchmark; no atom-grid downsizing",
        "full_grid_atom_count": full_grid.atom_count,
        "z_quadrature_points_per_dim": z_quadrature_points,
        "z_node_count": z_quadrature_points ** 3,
        "equivalent_full_grid_atom_z_evaluations_one_user": full_grid.atom_count * (z_quadrature_points ** 3) * (total_turns + total_queries),
        "distinct_likelihood_values_processed_measured": distinct_values_processed,
        "measured_wall_clock_seconds": measured_seconds,
        "projected_one_user_seconds": seconds_per_user,
        "projected_s5_cpu_hours": projected_s5_cpu_hours,
        "decision_rule": "projected_s5_cpu_hours <= 24",
        "decision": decision,
        "producer_function": "src.fsp_pum_env.ideal_observer.run_s2_tractability_benchmark",
        "code_path_hash": _code_path_hash(),
        "claim_ceiling": "S2 tractability projection only; no environment-validity claim",
    }
    _write_json_if_requested(output_path, report)
    return report


def make_fixed_probe_schedules(design: Mapping[str, Any]) -> list[FixedProbeSchedule]:
    spec = design["probe_scheduling"]["fixed_schedule_grid"]
    return [
        FixedProbeSchedule(probe_rate=float(rate), placement=str(placement))
        for rate in spec["probe_rates"]
        for placement in spec["placements"]
    ]


def make_z_quadrature(design: Mapping[str, Any], points_per_dim: int) -> ZQuadrature:
    if points_per_dim <= 0:
        raise ValueError("points_per_dim must be positive")
    z_design = design["env_parameters"]["z_session_state"]
    rho = {key: float(value) for key, value in z_design["ar1_rho"].items()}
    innovation_sigma = float(z_design["innovation_sigma"])
    gh_nodes, gh_weights = np.polynomial.hermite.hermgauss(points_per_dim)
    dim_sigmas = [
        innovation_sigma / math.sqrt(1.0 - rho["valence"] * rho["valence"]),
        innovation_sigma / math.sqrt(1.0 - rho["arousal"] * rho["arousal"]),
        innovation_sigma / math.sqrt(1.0 - rho["stress"] * rho["stress"]),
    ]
    nodes: list[tuple[float, float, float]] = []
    weights: list[float] = []
    for iv, ia, is_ in product(range(points_per_dim), repeat=3):
        node = (
            math.sqrt(2.0) * dim_sigmas[0] * float(gh_nodes[iv]),
            math.sqrt(2.0) * dim_sigmas[1] * float(gh_nodes[ia]),
            math.sqrt(2.0) * dim_sigmas[2] * float(gh_nodes[is_]),
        )
        weight = float(gh_weights[iv] * gh_weights[ia] * gh_weights[is_] / (math.pi ** 1.5))
        nodes.append(node)
        weights.append(weight)
    total = sum(weights)
    weights = [weight / total for weight in weights]
    return ZQuadrature(
        scheme="tensor_gauss_hermite_stationary_z_marginal",
        points_per_dim=points_per_dim,
        nodes=tuple(nodes),
        weights=tuple(weights),
    )


def _factor_groups_from_design(design: Mapping[str, Any]) -> tuple[str, ...]:
    env = design["env_parameters"]
    paired: set[int] = set()
    groups: list[str] = []
    for item in env["preregistered_interaction_pairs"]:
        indices = [int(name.rsplit("_", 1)[1]) for name in item["pair"]]
        paired.update(indices)
        groups.append(f"joint_topic_{indices[0]}_{indices[1]}")
    for index in range(int(env["K_topics"])):
        if index not in paired:
            groups.append(f"topic_{index}")
    groups.extend(["sensitivity_flag_0", "sensitivity_flag_1", "trust_gain_alpha", "trust_decay_beta", "disclosure_threshold_d"])
    return tuple(groups)


def independent_filter_seed(true_environment_seed: int, context: str) -> int:
    digest = hashlib.sha256(f"fsp-filter:{int(true_environment_seed)}:{context}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


def _validate_style_map(style_map: Sequence[int] | None, alphabet_size: int) -> tuple[int, ...]:
    if style_map is None:
        raise ValueError("style_map is required; the ideal may not reconstruct it from sampling seeds")
    out = tuple(int(value) for value in style_map)
    if sorted(out) != list(range(alphabet_size)):
        raise ValueError("style_map must be a permutation of the response alphabet")
    return out


def _schedule_positions(total_turns: int, n_probes: int, placement: str) -> list[int]:
    if n_probes <= 0:
        return []
    if placement == "front_loaded":
        return list(range(n_probes))
    if placement == "back_loaded":
        return list(range(total_turns - n_probes, total_turns))
    if placement == "uniform":
        if n_probes == 1:
            return [0]
        positions = np.linspace(0, total_turns - 1, n_probes)
        return sorted({int(round(value)) for value in positions})
    raise ValueError(f"unknown fixed schedule placement: {placement}")


def _z_marginalized_distribution(
    simulator: FspPumSimulator,
    user: _UserState,
    action: str,
    quadrature: ZQuadrature,
) -> list[float]:
    if action in simulator.probe_actions:
        probe_user = _clone_user(user)
        probe_user.z_state = _SessionState(0.0, 0.0, 0.0)
        return simulator.response_distribution(probe_user, action)
    mixture = np.zeros(simulator.alphabet_size, dtype=float)
    for node, weight in zip(quadrature.nodes, quadrature.weights):
        z_user = _clone_user(user)
        z_user.z_state = _SessionState(*node)
        mixture += float(weight) * np.asarray(simulator.response_distribution(z_user, action), dtype=float)
    total = float(mixture.sum())
    if total <= 0.0:
        raise ValueError("z-marginalized distribution has zero mass")
    return (mixture / total).tolist()


def _myopic_ig_action(core: ExactBayesFilter) -> str:
    current_entropy = core.posterior_entropy()
    best_action = core.simulator.probe_actions[0]
    best_gain = -math.inf
    for action in core.simulator.probe_actions:
        expected_entropy = _expected_entropy_after_observation(core, action)
        gain = current_entropy - expected_entropy
        if gain > best_gain:
            best_gain = gain
            best_action = action
    return best_action


def _expected_entropy_after_observation(core: ExactBayesFilter, action: str) -> float:
    weights = np.asarray([math.exp(atom.log_weight) for atom in core._atoms], dtype=float)
    likelihoods = []
    for atom in core._atoms:
        likelihoods.append(core._atom_distribution(_clone_user(atom.user), action))
    likelihood_matrix = np.asarray(likelihoods, dtype=float)
    predictive = weights @ likelihood_matrix
    expected_entropy = 0.0
    for symbol, symbol_probability in enumerate(predictive):
        if symbol_probability <= 0.0:
            continue
        posterior = weights * likelihood_matrix[:, symbol] / symbol_probability
        entropy = -float(sum(weight * math.log(weight) for weight in posterior if weight > 0.0))
        expected_entropy += float(symbol_probability) * entropy
    return expected_entropy


def _advance_filter_state_without_sampling(simulator: FspPumSimulator, user: _UserState, action: str) -> None:
    simulator._ensure_session_started(user)
    probe_cost = simulator._probe_trust_cost(action)
    simulator._update_trust(user, action, probe_cost)
    user.turn_in_session += 1
    user.turn_index += 1


def _advance_without_sampling(simulator: FspPumSimulator, user: _UserState, action: str) -> None:
    probe_cost = simulator._probe_trust_cost(action)
    simulator._update_trust(user, action, probe_cost)
    simulator._update_z(user)
    user.turn_in_session += 1
    user.turn_index += 1


def _benchmark_distinct_likelihood_values(
    design: Mapping[str, Any],
    action: str,
    step_index: int,
    z_quadrature_points: int,
) -> int:
    env = design["env_parameters"]
    levels = np.asarray(env["theta_structure"]["topic_preference_dims"]["grid_levels"], dtype=float)
    flags = np.asarray(env["theta_structure"]["sensitivity_flags"]["grid_levels"], dtype=int)
    trust_grid = np.asarray(
        list(
            product(
                env["theta_structure"]["trust_gain_alpha"]["grid_levels"],
                env["theta_structure"]["trust_decay_beta"]["grid_levels"],
                env["theta_structure"]["disclosure_threshold_d"]["grid_levels"],
            )
        ),
        dtype=float,
    )
    zq = make_z_quadrature(design, z_quadrature_points)
    if action.startswith("probe_"):
        if action == "probe_0" or action == "probe_1":
            base_values = len(flags)
        elif action == "probe_2":
            base_values = len(levels)
        else:
            base_values = len(flags) * len(flags) * len(levels)
        dummy = np.arange(base_values * len(trust_grid), dtype=float)
        _ = np.log1p(dummy + step_index)
        return int(dummy.size)
    if action.startswith("task_topic_"):
        topic_index = int(action.rsplit("_", 1)[1])
        paired = {1: 2, 2: 1, 5: 6, 6: 5}
        base_values = len(levels) * (len(levels) if topic_index in paired else 1)
    else:
        # recommend depends on a mean over non-probe topics; enumerate the small
        # count table rather than all 4^7 assignments.
        base_values = 22
    dummy = np.arange(base_values * len(trust_grid) * zq.node_count, dtype=float)
    _ = np.exp(-0.001 * dummy).sum()
    return int(dummy.size)


def _max_abs_diff(left: Sequence[float], right: Sequence[float]) -> float:
    return float(np.max(np.abs(np.asarray(left, dtype=float) - np.asarray(right, dtype=float))))


def _write_json_if_requested(output_path: str | Path | None, payload: Mapping[str, Any]) -> None:
    if output_path is None:
        return
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _clone_user(user: _UserState) -> _UserState:
    return _UserState(
        user_id=user.user_id,
        theta=user.theta,
        style_map=tuple(user.style_map),
        trust=float(user.trust),
        z_state=_SessionState(
            valence=float(user.z_state.valence),
            arousal=float(user.z_state.arousal),
            stress=float(user.z_state.stress),
        ),
        stable_fact_symbol=int(user.stable_fact_symbol),
        session_index=int(user.session_index),
        turn_in_session=int(user.turn_in_session),
        turn_index=int(user.turn_index),
    )


def _theta_value(theta_control: Mapping[str, Any], key: str) -> Any:
    if key.startswith("topic_"):
        return theta_control["topic_values"][int(key.rsplit("_", 1)[1])]
    if key.startswith("sensitivity_flag_"):
        return theta_control["sensitivity_flags"][int(key.rsplit("_", 1)[1])]
    if key == "trust_gain_alpha":
        return theta_control["trust_gain_alpha"]
    if key == "trust_decay_beta":
        return theta_control["trust_decay_beta"]
    if key == "disclosure_threshold_d":
        return theta_control["disclosure_threshold_d"]
    raise KeyError(key)


def _logsumexp(values: Sequence[float]) -> float:
    max_value = max(values)
    return max_value + math.log(sum(math.exp(value - max_value) for value in values))


def _modal_symbol(distribution: Sequence[float]) -> int:
    return int(np.argmax(np.asarray(distribution, dtype=float)))


def _code_path_hash() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
