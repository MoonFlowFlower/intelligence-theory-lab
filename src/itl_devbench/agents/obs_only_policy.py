from __future__ import annotations

from itl_devbench.agents.base import Agent, center_cell, deterministic_patrol, visible_direction_to
from itl_devbench.core.types import Action, Observation, Prediction


class ObsOnlyPolicyAgent(Agent):
    agent_id = "obs_only_policy"
    agent_kind = "baseline"

    def __init__(self) -> None:
        super().__init__(variant="frozen")

    def predict(self, obs: Observation) -> Prediction:
        return Prediction(confidence=0.1)

    def act(self, obs: Observation, prediction: Prediction) -> Action:
        if center_cell(obs).startswith("food"):
            return "eat"
        move_to_food = visible_direction_to(obs, ("food",))
        if move_to_food is not None:
            return move_to_food
        if "mystery" in [cell for row in obs.local_view for cell in row]:
            return "inspect"
        return deterministic_patrol(obs, offset=1)

