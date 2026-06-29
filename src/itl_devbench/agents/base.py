from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from itl_devbench.core.types import ACTIONS, Action, AgentState, Observation, Prediction


class Agent(ABC):
    agent_id: str
    agent_kind = "candidate"

    def __init__(self, variant: str = ""):
        self.variant = variant
        self.state = AgentState()

    def reset(self, seed: int, stage: int, episode: int) -> None:
        self.state = AgentState()

    @abstractmethod
    def predict(self, obs: Observation) -> Prediction:
        """Must be called and logged before act/env.step."""
        raise NotImplementedError

    @abstractmethod
    def act(self, obs: Observation, prediction: Prediction) -> Action:
        raise NotImplementedError

    def update(
        self,
        obs_before: Observation,
        action: Action,
        prediction: Prediction,
        obs_after: Observation,
        reward: float,
        done: bool,
        info: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {}

    def snapshot(self) -> Dict[str, Any]:
        return self.state.to_dict()


def center_cell(obs: Observation) -> str:
    ax, ay = obs.visible_cues.get("agent_view_index", [len(obs.local_view[0]) // 2, len(obs.local_view) // 2])
    return obs.local_view[int(ay)][int(ax)]


def legal_actions_from_observation(obs: Observation) -> list[Action]:
    legal: list[Action] = ["wait", "inspect", "eat"]
    if obs.visible_cues.get("family_id"):
        legal.extend(["move", "sample_small_bite"])
    ax, ay = obs.visible_cues.get("agent_view_index", [len(obs.local_view[0]) // 2, len(obs.local_view) // 2])
    moves: dict[Action, tuple[int, int]] = {
        "up": (0, -1),
        "down": (0, 1),
        "left": (-1, 0),
        "right": (1, 0),
    }
    for action, (dx, dy) in moves.items():
        x = int(ax) + dx
        y = int(ay) + dy
        if 0 <= y < len(obs.local_view) and 0 <= x < len(obs.local_view[y]) and obs.local_view[y][x] != "wall":
            legal.append(action)
    return legal


def visible_direction_to(obs: Observation, prefixes: tuple[str, ...]) -> Action | None:
    ax, ay = obs.visible_cues.get("agent_view_index", [len(obs.local_view[0]) // 2, len(obs.local_view) // 2])
    best: tuple[int, Action] | None = None
    for y, row in enumerate(obs.local_view):
        for x, cell in enumerate(row):
            if any(cell.startswith(prefix) for prefix in prefixes):
                dx = x - int(ax)
                dy = y - int(ay)
                if dx == 0 and dy == 0:
                    return "eat"
                if abs(dx) >= abs(dy):
                    action: Action = "right" if dx > 0 else "left"
                else:
                    action = "down" if dy > 0 else "up"
                if action in legal_actions_from_observation(obs):
                    distance = abs(dx) + abs(dy)
                    if best is None or distance < best[0]:
                        best = (distance, action)
    return best[1] if best else None


def deterministic_patrol(obs: Observation, offset: int = 0) -> Action:
    options = [action for action in ACTIONS if action in legal_actions_from_observation(obs) and action not in ("eat",)]
    if not options:
        return "wait"
    return options[(obs.tick + offset) % len(options)]
