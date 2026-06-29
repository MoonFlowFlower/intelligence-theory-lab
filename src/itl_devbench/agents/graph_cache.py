from __future__ import annotations

from typing import Any, Dict

from itl_devbench.agents.base import Agent, deterministic_patrol
from itl_devbench.core.hashing import sha256_json
from itl_devbench.core.types import Action, Observation, Prediction


class GraphCacheAgent(Agent):
    agent_id = "graph_cache"
    agent_kind = "baseline"

    def __init__(self) -> None:
        super().__init__(variant="frozen")
        self.cache: Dict[str, Dict[str, float]] = {}

    def reset(self, seed: int, stage: int, episode: int) -> None:
        super().reset(seed, stage, episode)
        self.cache = {}

    def predict(self, obs: Observation) -> Prediction:
        key = _obs_key(obs)
        best = max(self.cache.get(key, {}).values(), default=0.0)
        return Prediction(predicted_delta_energy=int(round(best)), confidence=0.3 if key in self.cache else 0.0)

    def act(self, obs: Observation, prediction: Prediction) -> Action:
        key = _obs_key(obs)
        if key in self.cache and self.cache[key]:
            return max(self.cache[key].items(), key=lambda item: item[1])[0]  # type: ignore[return-value]
        return deterministic_patrol(obs, offset=3)

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
        key = _obs_key(obs_before)
        before_size = sum(len(actions) for actions in self.cache.values())
        self.cache.setdefault(key, {})
        previous = self.cache[key].get(action, reward)
        self.cache[key][action] = (previous + reward) / 2.0
        after_size = sum(len(actions) for actions in self.cache.values())
        self.state.transition_model = {"cache_states": len(self.cache)}
        self.state.memory_size = after_size
        return {
            "prediction_error": {"energy": 0, "health": 0, "total": abs(reward - prediction.predicted_delta_energy)},
            "model_before": {"cache_entries": before_size},
            "model_after": {"cache_entries": after_size},
            "memory_size_before": before_size,
            "memory_size_after": after_size,
        }


def _obs_key(obs: Observation) -> str:
    return sha256_json(
        {
            "stage": obs.stage,
            "agent_pos": obs.agent_pos,
            "energy_bucket": obs.energy // 2,
            "health_bucket": obs.health // 2,
            "local_view": obs.local_view,
            "visible_cues": obs.visible_cues,
        }
    )

