from __future__ import annotations

from typing import Any, Dict

from itl_devbench.agents.base import Agent, center_cell, deterministic_patrol, visible_direction_to
from itl_devbench.core.types import Action, Observation, Prediction


class MinimalLoopAgent(Agent):
    """
    Factorial candidate:
      pe_update: bool
      memory: bool
      planner_reads_model: bool

    This is not a persona or language renderer.
    """

    agent_id = "minimal_loop"
    agent_kind = "candidate"

    def __init__(self, pe_update: bool, memory: bool, planner_reads_model: bool):
        variant = f"{int(pe_update)}{int(memory)}{int(planner_reads_model)}"
        super().__init__(variant=variant)
        self.pe_update = pe_update
        self.memory_enabled = memory
        self.planner_reads_model = planner_reads_model
        self.memory: list[Dict[str, Any]] = []
        self.model: Dict[str, float] = {
            "expected_energy_delta_eat": 0.0,
            "expected_health_delta": 0.0,
            "collision_rate": 0.0,
        }

    def reset(self, seed: int, stage: int, episode: int) -> None:
        super().reset(seed, stage, episode)
        self.memory = []
        self.model = {
            "expected_energy_delta_eat": 0.0,
            "expected_health_delta": 0.0,
            "collision_rate": 0.0,
        }

    def predict(self, obs: Observation) -> Prediction:
        if self.planner_reads_model:
            return Prediction(
                predicted_delta_energy=int(round(self.model.get("expected_energy_delta_eat", 0.0))),
                predicted_delta_health=int(round(self.model.get("expected_health_delta", 0.0))),
                predicted_collision=False,
                predicted_done=False,
                confidence=0.5,
            )
        return Prediction(confidence=0.0)

    def act(self, obs: Observation, prediction: Prediction) -> Action:
        current = center_cell(obs)
        if current.startswith("food"):
            if self.planner_reads_model and prediction.predicted_delta_energy < 0:
                return "inspect"
            return "eat"
        if current == "mystery" and obs.visible_cues.get("inspected_affordance_cue") == "beneficial":
            return "eat"
        if "mystery" in [cell for row in obs.local_view for cell in row] and obs.tick % 4 == 0:
            return "inspect"
        move_to_food = visible_direction_to(obs, ("food",))
        if move_to_food is not None:
            return move_to_food
        if obs.energy < 3:
            return "wait"
        return deterministic_patrol(obs, offset=5)

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
        actual_energy_delta = obs_after.energy - obs_before.energy
        actual_health_delta = obs_after.health - obs_before.health

        pe_energy = actual_energy_delta - prediction.predicted_delta_energy
        pe_health = actual_health_delta - prediction.predicted_delta_health
        pe_total = abs(pe_energy) + abs(pe_health)

        before_model = dict(self.model)
        memory_size_before = len(self.memory)

        if self.memory_enabled:
            self.memory.append(
                {
                    "stage": obs_before.stage,
                    "action": action,
                    "predicted_energy_delta": prediction.predicted_delta_energy,
                    "actual_energy_delta": actual_energy_delta,
                    "predicted_health_delta": prediction.predicted_delta_health,
                    "actual_health_delta": actual_health_delta,
                    "pe_total": pe_total,
                }
            )

        if self.pe_update:
            lr = 0.2
            if action == "eat":
                self.model["expected_energy_delta_eat"] = (
                    (1 - lr) * self.model["expected_energy_delta_eat"] + lr * actual_energy_delta
                )
            self.model["expected_health_delta"] = (
                (1 - lr) * self.model["expected_health_delta"] + lr * actual_health_delta
            )
            self.model["collision_rate"] = (
                (1 - lr) * self.model["collision_rate"] + lr * float(bool(info.get("collision", False)))
            )

        self.state.transition_model = dict(self.model)
        self.state.memory_size = len(self.memory)
        self.state.last_prediction_error = float(pe_total)

        return {
            "prediction_error": {
                "energy": pe_energy,
                "health": pe_health,
                "total": pe_total,
            },
            "model_before": before_model,
            "model_after": dict(self.model),
            "memory_size_before": memory_size_before,
            "memory_size_after": len(self.memory),
            "pe_update_enabled": self.pe_update,
            "memory_enabled": self.memory_enabled,
            "planner_reads_model": self.planner_reads_model,
        }

