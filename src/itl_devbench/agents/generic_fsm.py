from __future__ import annotations

from itl_devbench.agents.base import Agent, center_cell, deterministic_patrol, visible_direction_to
from itl_devbench.core.types import Action, Observation, Prediction


class GenericFSMAgent(Agent):
    agent_id = "generic_fsm"
    agent_kind = "baseline"

    def __init__(self) -> None:
        super().__init__(variant="frozen")

    def predict(self, obs: Observation) -> Prediction:
        low_resources = obs.energy < 4 or obs.health < 4
        return Prediction(predicted_done=low_resources, confidence=0.2)

    def act(self, obs: Observation, prediction: Prediction) -> Action:
        current = center_cell(obs)
        if current.startswith("food"):
            return "eat"
        if current == "mystery" and obs.visible_cues.get("inspected_affordance_cue") == "beneficial":
            return "eat"
        if "mystery" in [cell for row in obs.local_view for cell in row] and obs.tick % 3 == 0:
            return "inspect"
        move_to_food = visible_direction_to(obs, ("food",))
        if move_to_food is not None:
            return move_to_food
        return deterministic_patrol(obs, offset=2)

