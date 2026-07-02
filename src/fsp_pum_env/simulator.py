"""Sealed simulator for FSP-PUM-ENV-IDPROBE-001A S1.

The public turn surface emits symbolic observations and accounting metadata
only. Latent theta and z state stay inside this module.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


class SimulatorVariant(str, Enum):
    BASE = "base"
    NULL_ENV = "NULL_env"
    CAMOUFLAGE_OFF = "camouflage_off"
    PROBE_CHANNEL_OFF = "probe_channel_off"
    FLAT_THETA = "flat_theta"
    TRUST_COST_OFF = "trust_cost_off"
    GRAPH_CACHE_SHOULD_WIN_LOW_DIVERSITY_TEMPLATES = "graph_cache_should_win_low_diversity_templates"
    RAG_SHOULD_WIN_STABLE_FACTS = "rag_should_win_stable_facts"
    SURFACE_REMAP_FRESH_RENDERER = "surface_remap_fresh_renderer"


_LATENT_KEYS = {
    "theta",
    "z",
    "latent",
    "latents",
    "latent_state",
    "session_state",
    "user_state",
}


@dataclass(frozen=True)
class _Theta:
    topic_values: tuple[float, ...]
    sensitivity_flags: tuple[int, int]
    trust_gain_alpha: float
    trust_decay_beta: float
    disclosure_threshold_d: float


@dataclass
class _SessionState:
    valence: float
    arousal: float
    stress: float


@dataclass
class _UserState:
    user_id: int
    theta: _Theta
    style_map: tuple[int, ...]
    trust: float
    z_state: _SessionState
    stable_fact_symbol: int
    session_index: int = 0
    turn_in_session: int = 0
    turn_index: int = 0


@dataclass(frozen=True)
class StepResult:
    observation: dict[str, int]
    cost_metering: dict[str, float]

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "observation": dict(self.observation),
            "cost_metering": dict(self.cost_metering),
        }


def contains_latent_leak(payload: Any) -> bool:
    """Return True when a structured payload exposes latent fields."""

    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if str(key).lower() in _LATENT_KEYS:
                return True
            if contains_latent_leak(value):
                return True
        return False
    if isinstance(payload, (list, tuple, set, frozenset)):
        return any(contains_latent_leak(value) for value in payload)
    if isinstance(payload, (_Theta, _SessionState, _UserState)):
        return True
    if is_dataclass(payload):
        return contains_latent_leak(asdict(payload))
    return False


def _derive_seed(master_seed: int, stream_name: str) -> int:
    digest = hashlib.sha256(f"{master_seed}:{stream_name}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


def _softmax(logits: np.ndarray) -> np.ndarray:
    centered = logits - float(np.max(logits))
    exp = np.exp(centered)
    return exp / float(exp.sum())


class FspPumSimulator:
    """One sealed generator surface parameterized by frozen-design variants."""

    def __init__(self, design: Mapping[str, Any], *, master_seed: int, variant: SimulatorVariant | str = SimulatorVariant.BASE):
        self.design = design
        self.master_seed = int(master_seed)
        self.variant = SimulatorVariant(variant)

        env = design["env_parameters"]
        action_set = env["action_set"]
        theta = env["theta_structure"]
        renderer = env["renderer"]
        episodes = env["episodes"]

        self.alphabet_size = int(renderer["response_alphabet_size"])
        self.sessions_per_user = int(episodes["N_sessions_per_user"])
        self.turns_per_session = int(episodes["T_turns_per_session"])
        self.task_actions = tuple(action_set["task_actions"])
        self.recommend_actions = tuple(action_set["recommend_actions"])
        self.probe_actions = tuple(item["name"] for item in action_set["probe_actions"])
        self.all_actions = self.task_actions + self.recommend_actions + self.probe_actions
        self._probe_specs = {item["name"]: item for item in action_set["probe_actions"]}

        self.theta_topic_levels = tuple(float(v) for v in theta["topic_preference_dims"]["grid_levels"])
        self._sensitivity_levels = tuple(int(v) for v in theta["sensitivity_flags"]["grid_levels"])
        self._alpha_levels = tuple(float(v) for v in theta["trust_gain_alpha"]["grid_levels"])
        self._beta_levels = tuple(float(v) for v in theta["trust_decay_beta"]["grid_levels"])
        self._d_levels = tuple(float(v) for v in theta["disclosure_threshold_d"]["grid_levels"])
        self.interaction_pairs = tuple(
            tuple(int(name.rsplit("_", 1)[1]) for name in pair["pair"])
            for pair in env["preregistered_interaction_pairs"]
        )
        self._interaction_gamma = {
            tuple(int(name.rsplit("_", 1)[1]) for name in pair["pair"]): float(pair["gamma"])
            for pair in env["preregistered_interaction_pairs"]
        }
        self._probe_only_topic_indices = tuple(
            int(name.rsplit("_", 1)[1])
            for name in env["theta_probe_subset"]["dims"]
            if name.startswith("topic_")
        )

        z_design = env["z_session_state"]
        self._z_rho = {key: float(value) for key, value in z_design["ar1_rho"].items()}
        self._z_sigma = float(z_design["innovation_sigma"])
        self._trust_init = float(env["trust_dynamics"]["init"])

    @classmethod
    def from_frozen_design(
        cls,
        path: str | Path,
        *,
        master_seed: int,
        variant: SimulatorVariant | str = SimulatorVariant.BASE,
    ) -> "FspPumSimulator":
        design = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        return cls(design, master_seed=master_seed, variant=variant)

    def start_user(
        self,
        user_id: int,
        *,
        controlled_theta: Mapping[str, Sequence[float | int]] | None = None,
        style_map: Sequence[int] | None = None,
    ) -> _UserState:
        rng = self._rng(f"user_sample:{int(user_id)}")
        theta = self._sample_theta(rng, controlled_theta)
        style = tuple(style_map) if style_map is not None else self._style_map_for_user(int(user_id))
        if sorted(style) != list(range(self.alphabet_size)):
            raise ValueError("style_map must be a permutation of the response alphabet")

        fact_rng = self._rng(f"stable_fact:{int(user_id)}")
        stable_fact_symbol = int(fact_rng.integers(0, self.alphabet_size))
        return _UserState(
            user_id=int(user_id),
            theta=theta,
            style_map=style,
            trust=self._trust_init,
            z_state=self._initial_z_state(int(user_id), session_index=0),
            stable_fact_symbol=stable_fact_symbol,
        )

    def response_distribution(self, user: _UserState, action: str) -> list[float]:
        self._validate_action(action)
        self._ensure_session_started(user)
        if self.variant is SimulatorVariant.GRAPH_CACHE_SHOULD_WIN_LOW_DIVERSITY_TEMPLATES:
            base = self._low_diversity_template_distribution(action)
        elif self.variant is SimulatorVariant.RAG_SHOULD_WIN_STABLE_FACTS and action == "recommend":
            base = self._peaked_distribution(user.stable_fact_symbol, strength=3.2)
        elif self.variant is SimulatorVariant.NULL_ENV:
            base = self._action_only_distribution(action)
        elif action in self.probe_actions:
            base = self._probe_distribution(user, action)
        else:
            base = self._passive_distribution(user, action)

        degraded = self._apply_low_trust(base, user)
        surface = np.zeros(self.alphabet_size, dtype=float)
        for internal_symbol, probability in enumerate(degraded):
            surface[user.style_map[internal_symbol]] = probability
        return surface.tolist()

    def step(self, user: _UserState, action: str) -> StepResult:
        distribution = self.response_distribution(user, action)
        rng = self._rng(f"renderer:{user.user_id}:{user.turn_index}")
        symbol = int(rng.choice(self.alphabet_size, p=np.asarray(distribution, dtype=float)))

        probe_cost = self._probe_trust_cost(action)
        self._update_trust(user, action, probe_cost)
        self._update_z(user)
        user.turn_in_session += 1
        user.turn_index += 1

        return StepResult(
            observation={"symbol": symbol},
            cost_metering={
                "tokens_per_turn_proxy": 1.0,
                "probe_trust_cost": float(probe_cost),
                "memory_read_ops": 0.0,
                "memory_write_ops": 0.0,
            },
        )

    def _sample_theta(self, rng: np.random.Generator, controlled_theta: Mapping[str, Sequence[float | int]] | None) -> _Theta:
        topics = tuple(float(rng.choice(self.theta_topic_levels)) for _ in range(8))
        flags = tuple(int(rng.choice(self._sensitivity_levels)) for _ in range(2))
        alpha = float(rng.choice(self._alpha_levels))
        beta = float(rng.choice(self._beta_levels))
        disclosure_threshold = float(rng.choice(self._d_levels))

        if controlled_theta is not None:
            if "topic_values" in controlled_theta:
                topics = tuple(float(value) for value in controlled_theta["topic_values"])
            if "sensitivity_flags" in controlled_theta:
                flags = tuple(int(value) for value in controlled_theta["sensitivity_flags"])
            if "trust_gain_alpha" in controlled_theta:
                alpha = float(controlled_theta["trust_gain_alpha"])  # type: ignore[arg-type]
            if "trust_decay_beta" in controlled_theta:
                beta = float(controlled_theta["trust_decay_beta"])  # type: ignore[arg-type]
            if "disclosure_threshold_d" in controlled_theta:
                disclosure_threshold = float(controlled_theta["disclosure_threshold_d"])  # type: ignore[arg-type]
            if len(topics) != 8 or len(flags) != 2:
                raise ValueError("controlled_theta must provide 8 topics and 2 sensitivity flags when present")

        if self.variant is SimulatorVariant.FLAT_THETA:
            topics = tuple(0.0 for _ in range(8))
            flags = (0, 0)

        return _Theta(
            topic_values=topics,
            sensitivity_flags=(int(flags[0]), int(flags[1])),
            trust_gain_alpha=alpha,
            trust_decay_beta=beta,
            disclosure_threshold_d=disclosure_threshold,
        )

    def _style_map_for_user(self, user_id: int) -> tuple[int, ...]:
        if self.variant is SimulatorVariant.CAMOUFLAGE_OFF:
            return tuple(range(self.alphabet_size))
        stream = "surface_remap_renderer" if self.variant is SimulatorVariant.SURFACE_REMAP_FRESH_RENDERER else "renderer"
        rng = self._rng(f"{stream}:style:{user_id}")
        return tuple(int(value) for value in rng.permutation(self.alphabet_size))

    def _initial_z_state(self, user_id: int, *, session_index: int) -> _SessionState:
        rng = self._rng(f"session_state:init:{user_id}:{int(session_index)}")

        def draw(dim: str) -> float:
            rho = self._z_rho[dim]
            stationary_sigma = self._z_sigma / np.sqrt(1.0 - rho * rho)
            return float(rng.normal(0.0, stationary_sigma))

        return _SessionState(valence=draw("valence"), arousal=draw("arousal"), stress=draw("stress"))

    def _passive_distribution(self, user: _UserState, action: str) -> np.ndarray:
        if action in self.task_actions:
            topic_index = int(action.rsplit("_", 1)[1])
            topic_value = 0.0 if topic_index in self._probe_only_topic_indices else user.theta.topic_values[topic_index]
            interaction = self._interaction_for_topic(user.theta, topic_index)
            z_term = 0.35 * user.z_state.valence - 0.15 * user.z_state.stress
            center = int((topic_index * 3 + 8) % self.alphabet_size)
            strength = 1.35 + 0.55 * topic_value + 0.15 * interaction + z_term
            return self._peaked_distribution(center, strength=strength)

        non_probe_topics = [
            value for index, value in enumerate(user.theta.topic_values)
            if index not in self._probe_only_topic_indices
        ]
        preference = float(np.mean(non_probe_topics)) if non_probe_topics else 0.0
        z_term = 0.2 * user.z_state.valence + 0.1 * user.z_state.arousal
        center = int((13 + round(2 * preference)) % self.alphabet_size)
        return self._peaked_distribution(center, strength=1.1 + 0.35 * preference + z_term)

    def _probe_distribution(self, user: _UserState, action: str) -> np.ndarray:
        if self.variant is SimulatorVariant.PROBE_CHANNEL_OFF:
            return self._action_only_distribution(action)

        spec = self._probe_specs[action]
        targets = tuple(spec["targets"])
        if "sensitivity_flag_0" in targets and "sensitivity_flag_1" not in targets:
            center = 2 + int(user.theta.sensitivity_flags[0])
            return self._peaked_distribution(center, strength=2.7)
        if "sensitivity_flag_1" in targets and "sensitivity_flag_0" not in targets:
            center = 6 + int(user.theta.sensitivity_flags[1])
            return self._peaked_distribution(center, strength=2.7)
        if targets == ("topic_7",):
            center = 10 + self._topic_level_index(user.theta.topic_values[7])
            return self._peaked_distribution(center, strength=2.9)

        topic_component = self._topic_level_index(user.theta.topic_values[7])
        flag_component = 2 * int(user.theta.sensitivity_flags[0]) + int(user.theta.sensitivity_flags[1])
        center = 16 + ((topic_component + flag_component) % 8)
        return self._peaked_distribution(center, strength=1.75)

    def _action_only_distribution(self, action: str) -> np.ndarray:
        action_index = self.all_actions.index(action)
        return self._peaked_distribution((action_index * 5) % self.alphabet_size, strength=0.9)

    def _low_diversity_template_distribution(self, action: str) -> np.ndarray:
        if action in self.probe_actions:
            center = 4
        elif action == "recommend":
            center = 8
        else:
            center = int(action.rsplit("_", 1)[1]) % 2
        return self._peaked_distribution(center, strength=3.0)

    def _interaction_for_topic(self, theta: _Theta, topic_index: int) -> float:
        total = 0.0
        for pair, gamma in self._interaction_gamma.items():
            if topic_index in pair:
                total += gamma * theta.topic_values[pair[0]] * theta.topic_values[pair[1]]
        return total

    def _peaked_distribution(self, center: int, *, strength: float) -> np.ndarray:
        logits = np.zeros(self.alphabet_size, dtype=float)
        logits[int(center) % self.alphabet_size] = float(strength)
        neighbor = (int(center) + 1) % self.alphabet_size
        logits[neighbor] = float(strength) * 0.35
        return _softmax(logits)

    def _apply_low_trust(self, distribution: np.ndarray, user: _UserState) -> np.ndarray:
        if self.variant is SimulatorVariant.NULL_ENV:
            return distribution
        threshold = max(user.theta.disclosure_threshold_d, 1e-12)
        if user.trust >= threshold:
            return distribution
        uniform = np.full(self.alphabet_size, 1.0 / self.alphabet_size, dtype=float)
        weight = (threshold - user.trust) / threshold
        return (1.0 - weight) * distribution + weight * uniform

    def _update_trust(self, user: _UserState, action: str, probe_cost: float) -> None:
        theta = user.theta
        if action in self.probe_actions:
            next_trust = theta.trust_decay_beta * user.trust - probe_cost
        else:
            next_trust = theta.trust_decay_beta * user.trust + theta.trust_gain_alpha * (1.0 - user.trust)
        user.trust = float(np.clip(next_trust, 0.0, 1.0))

    def _update_z(self, user: _UserState) -> None:
        rng = self._rng(f"session_state:step:{user.user_id}:{user.session_index}:{user.turn_in_session}")
        for dim in ("valence", "arousal", "stress"):
            current = getattr(user.z_state, dim)
            updated = self._z_rho[dim] * current + float(rng.normal(0.0, self._z_sigma))
            setattr(user.z_state, dim, updated)

    def _ensure_session_started(self, user: _UserState) -> None:
        if user.turn_in_session < self.turns_per_session:
            return
        next_session = user.session_index + 1
        if next_session >= self.sessions_per_user:
            raise ValueError("episode is complete; no additional session is available")
        user.session_index = next_session
        user.turn_in_session = 0
        user.z_state = self._initial_z_state(user.user_id, session_index=next_session)

    def _probe_trust_cost(self, action: str) -> float:
        if action not in self.probe_actions or self.variant is SimulatorVariant.TRUST_COST_OFF:
            return 0.0
        return float(self._probe_specs[action]["trust_cost"])

    def _topic_level_index(self, value: float) -> int:
        distances = [abs(float(value) - level) for level in self.theta_topic_levels]
        return int(np.argmin(distances))

    def _rng(self, stream_name: str) -> np.random.Generator:
        return np.random.Generator(np.random.PCG64(_derive_seed(self.master_seed, stream_name)))

    def _validate_action(self, action: str) -> None:
        if action not in self.all_actions:
            raise ValueError(f"unknown action: {action}")
