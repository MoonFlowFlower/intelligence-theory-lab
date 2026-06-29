from __future__ import annotations

import random

from itl_devbench.agents.base import Agent, legal_actions_from_observation
from itl_devbench.core.types import Action, Observation, Prediction


class RandomPolicyAgent(Agent):
    agent_id = "random_policy"
    agent_kind = "baseline"

    def __init__(self) -> None:
        super().__init__(variant="frozen")
        self.rng = random.Random(0)

    def reset(self, seed: int, stage: int, episode: int) -> None:
        super().reset(seed, stage, episode)
        self.rng = random.Random((seed * 1009) ^ (stage * 9176) ^ episode)

    def predict(self, obs: Observation) -> Prediction:
        return Prediction(confidence=0.0)

    def act(self, obs: Observation, prediction: Prediction) -> Action:
        return self.rng.choice(legal_actions_from_observation(obs))

