"""S2 exact-grid ideal-observer instrumentation for FSP-PUM-ENV-IDPROBE-001A.

This module is an oracle instrument, not a candidate mechanism. It consumes
public action/observation prefixes and updates a posterior over frozen-design
theta grid atoms through the sealed generator likelihood.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Any, Mapping, Sequence

import numpy as np

from .simulator import (
    FspPumSimulator,
    SimulatorVariant,
    _SessionState,
    _UserState,
    contains_latent_leak,
)


PC_IDEAL_SANITY_THRESHOLD = 0.95


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


class ExactBayesFilter:
    """Exact posterior over a finite theta grid using simulator likelihoods."""

    def __init__(
        self,
        design: Mapping[str, Any],
        *,
        master_seed: int,
        variant: SimulatorVariant | str,
        grid_spec: ThetaGridSpec | None = None,
        user_id: int = 0,
        style_map: Sequence[int] | None = None,
    ):
        self.design = design
        self.master_seed = int(master_seed)
        self.variant = SimulatorVariant(variant)
        self.grid_spec = grid_spec or ThetaGridSpec.from_design(design)
        self.user_id = int(user_id)
        self.simulator = FspPumSimulator(design, master_seed=self.master_seed, variant=self.variant)
        self.style_map = tuple(style_map) if style_map is not None else self._default_style_map()
        self.events: list[PrefixEvent] = []
        self._initial_theta_controls = list(self.grid_spec.iter_theta_controls())
        self._atoms: list[_WeightedAtom] = []
        self.reset()

    @classmethod
    def from_frozen_design(
        cls,
        path: str | Path,
        *,
        master_seed: int,
        variant: SimulatorVariant | str,
        grid_spec: ThetaGridSpec | None = None,
        user_id: int = 0,
        style_map: Sequence[int] | None = None,
    ) -> "ExactBayesFilter":
        design = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        return cls(
            design,
            master_seed=master_seed,
            variant=variant,
            grid_spec=grid_spec,
            user_id=user_id,
            style_map=style_map,
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
            distribution = self.simulator.response_distribution(atom.user, prefix_event.action)
            likelihood = max(float(distribution[prefix_event.symbol]), 1e-300)
            atom.log_weight += math.log(likelihood)
            _advance_without_sampling(self.simulator, atom.user, prefix_event.action)
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
            mixture += math.exp(atom.log_weight) * np.asarray(
                self.simulator.response_distribution(user_copy, action),
                dtype=float,
            )
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

    def _default_style_map(self) -> tuple[int, ...]:
        if self.variant is SimulatorVariant.CAMOUFLAGE_OFF:
            return tuple(range(self.simulator.alphabet_size))
        return self.simulator._style_map_for_user(self.user_id)


@dataclass
class S2VariantWrapper:
    name: str
    core: ExactBayesFilter
    history_limit: int | None = None
    policy_kind: str = "predictor"
    history: list[PrefixEvent] = field(default_factory=list)
    ucb_counts: dict[str, int] = field(default_factory=dict)
    ucb_rewards: dict[str, float] = field(default_factory=dict)

    def observe_prefix(self, events: Sequence[PrefixEvent | Mapping[str, Any]]) -> None:
        parsed = [event if isinstance(event, PrefixEvent) else PrefixEvent.from_mapping(event) for event in events]
        selected = parsed[-self.history_limit :] if self.history_limit is not None else parsed
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
            return _fixed_schedule_action(simulator, int(step_index))
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
    master_seed: int,
    grid_spec: ThetaGridSpec | None = None,
) -> dict[str, S2VariantWrapper]:
    truncation_b = int(design["env_parameters"]["episodes"]["T_turns_per_session"]) * 2
    declared_b = int(design["gap3_truncation"]["B"])
    if truncation_b != declared_b:
        truncation_b = declared_b

    def core_for(offset: int) -> ExactBayesFilter:
        return ExactBayesFilter(
            design,
            master_seed=master_seed + offset,
            variant=SimulatorVariant.CAMOUFLAGE_OFF,
            grid_spec=grid_spec,
        )

    return {
        "full_history": S2VariantWrapper("full_history", core_for(0), history_limit=None, policy_kind="full_history"),
        "truncation_B30": S2VariantWrapper("truncation_B30", core_for(1), history_limit=truncation_b, policy_kind="truncation"),
        "passive": S2VariantWrapper("passive", core_for(2), history_limit=None, policy_kind="passive"),
        "myopic_IG": S2VariantWrapper("myopic_IG", core_for(3), history_limit=None, policy_kind="myopic_IG"),
        "fixed_schedule_grid": S2VariantWrapper("fixed_schedule_grid", core_for(4), history_limit=None, policy_kind="fixed_schedule_grid"),
        "ucb1": S2VariantWrapper("ucb1", core_for(5), history_limit=None, policy_kind="ucb1"),
    }


def run_pc_ideal_sanity(
    frozen_design_path: str | Path,
    *,
    output_path: str | Path | None = None,
    master_seed: int = 20260710,
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

    correct = 0
    total = 0
    entropy_drops: list[float] = []
    case_ids: list[str] = []
    for case_index, theta_control in enumerate(grid.iter_theta_controls()):
        case_ids.append(f"micro_case_{case_index:02d}")
        true_user = true_sim.start_user(user_id=case_index, controlled_theta=theta_control, style_map=style_map)
        filt = ExactBayesFilter(
            design,
            master_seed=master_seed,
            variant=SimulatorVariant.CAMOUFLAGE_OFF,
            grid_spec=grid,
            user_id=case_index,
            style_map=style_map,
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


def _fixed_schedule_action(simulator: FspPumSimulator, step_index: int) -> str:
    if step_index % 5 == 0:
        return simulator.probe_actions[(step_index // 5) % len(simulator.probe_actions)]
    return simulator.task_actions[step_index % len(simulator.task_actions)]


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
        likelihoods.append(core.simulator.response_distribution(_clone_user(atom.user), action))
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


def _advance_without_sampling(simulator: FspPumSimulator, user: _UserState, action: str) -> None:
    probe_cost = simulator._probe_trust_cost(action)
    simulator._update_trust(user, action, probe_cost)
    simulator._update_z(user)
    user.turn_in_session += 1
    user.turn_index += 1


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
