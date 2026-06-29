from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Literal, Optional

Action = Literal["up", "down", "left", "right", "move", "wait", "inspect", "sample_small_bite", "eat"]
ACTIONS: tuple[Action, ...] = ("up", "down", "left", "right", "move", "wait", "inspect", "sample_small_bite", "eat")


@dataclass(frozen=True)
class Observation:
    stage: int
    tick: int
    agent_pos: tuple[int, int]
    energy: int
    health: int
    local_view: tuple[tuple[str, ...], ...]
    last_action_result: Dict[str, Any] = field(default_factory=dict)
    visible_cues: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage,
            "tick": self.tick,
            "agent_pos": list(self.agent_pos),
            "energy": self.energy,
            "health": self.health,
            "local_view": [list(row) for row in self.local_view],
            "last_action_result": _json_ready(self.last_action_result),
            "visible_cues": _json_ready(self.visible_cues),
        }


@dataclass
class AgentState:
    # Keep explicit and auditable. No persona fields.
    transition_model: Dict[str, Any] = field(default_factory=dict)
    uncertainty: Dict[str, float] = field(default_factory=dict)
    memory_size: int = 0
    last_prediction_error: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return _json_ready(asdict(self))


@dataclass
class Prediction:
    predicted_delta_energy: int = 0
    predicted_delta_health: int = 0
    predicted_collision: bool = False
    predicted_done: bool = False
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return _json_ready(asdict(self))


@dataclass
class StepRecord:
    run_id: str
    event_index: int
    split: str
    family_id: str
    family_instance_id: str
    dimension_combo: list[str]
    target_pressure: list[str]
    agent_kind: str
    agent_id: str
    variant: str
    seed: int
    rule_seed: int
    stage: int
    episode: int
    tick: int

    S_before: Dict[str, Any]
    O_t: Dict[str, Any]
    pre_action_prediction: Dict[str, Any]
    A_t: str

    env_result: Dict[str, Any]
    reward: float
    done: bool

    prediction_error: Dict[str, Any]
    U_t: Dict[str, Any]
    M_diff: Dict[str, Any]
    S_after: Dict[str, Any]

    prev_event_hash: str
    event_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "event_index": self.event_index,
            "split": self.split,
            "family_id": self.family_id,
            "family_instance_id": self.family_instance_id,
            "dimension_combo": self.dimension_combo,
            "target_pressure": self.target_pressure,
            "agent_kind": self.agent_kind,
            "agent_id": self.agent_id,
            "variant": self.variant,
            "seed": self.seed,
            "rule_seed": self.rule_seed,
            "stage": self.stage,
            "episode": self.episode,
            "tick": self.tick,
            "S_before": _json_ready(self.S_before),
            "O_t": _json_ready(self.O_t),
            "pre_action_prediction": _json_ready(self.pre_action_prediction),
            "A_t": self.A_t,
            "env_result": _json_ready(self.env_result),
            "reward": self.reward,
            "done": self.done,
            "prediction_error": _json_ready(self.prediction_error),
            "U_t": _json_ready(self.U_t),
            "M_diff": _json_ready(self.M_diff),
            "S_after": _json_ready(self.S_after),
            "prev_event_hash": self.prev_event_hash,
            "event_hash": self.event_hash,
        }


def _json_ready(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    return value
