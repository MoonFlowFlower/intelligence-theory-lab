from __future__ import annotations

import random
from typing import Any, Dict

from itl_devbench.core.types import Action, Observation
from itl_devbench.envs.families import TaskFamilyInstance


class DevelopmentalGridEnv:
    """
    Deterministic symbolic developmental gridworld.

    Candidate agents must not access debug_hidden_state().
    Only oracle/audit may use it.
    """

    def __init__(self, config: Dict[str, Any], seed: int):
        self.config = config
        self.seed = seed
        self.rng = random.Random(seed)
        self.stage = 0
        self.rule_seed = 0
        self.tick = 0
        self.width = int(config.get("width", 7))
        self.height = int(config.get("height", 7))
        self.max_ticks = int(config.get("max_ticks", 100))
        self.agent_pos = (0, 0)
        self.energy = 10
        self.health = 10
        self._hidden_rules: Dict[str, Any] = {}
        self._grid: list[list[str]] = []
        self._pending_effects: list[Dict[str, Any]] = []
        self._last_action_result: Dict[str, Any] = {}
        self._last_visible_cues: Dict[str, Any] = {}
        self._family_instance: TaskFamilyInstance | None = None
        self._family_pending: list[Dict[str, Any]] = []
        self._family_uncertainty = 1.0
        self._family_consumed = False

    def reset(self, stage: int, rule_seed: int, family_instance: TaskFamilyInstance | None = None) -> Observation:
        self.stage = stage
        self.rule_seed = rule_seed
        self.tick = 0
        self._family_instance = family_instance
        self._family_pending = []
        self._family_uncertainty = 1.0
        self._family_consumed = False
        mixed_seed = (self.seed * 1000003) ^ (stage * 9176) ^ (rule_seed * 37)
        self.rng = random.Random(mixed_seed)
        self.agent_pos = (self.width // 2, self.height // 2)
        self.energy = 10
        self.health = 10
        self._pending_effects = []
        self._last_action_result = {}
        self._last_visible_cues = {}
        if self._family_instance is not None:
            return self._observe()
        self._generate_grid()
        self._generate_hidden_rules(rule_seed)
        return self._observe()

    def _generate_grid(self) -> None:
        self._grid = [["empty" for _ in range(self.width)] for _ in range(self.height)]

        for x in range(self.width):
            self._grid[0][x] = "wall"
            self._grid[self.height - 1][x] = "wall"
        for y in range(self.height):
            self._grid[y][0] = "wall"
            self._grid[y][self.width - 1] = "wall"

        inner_wall_count = min(max(1, self.stage + 1), max(1, (self.width * self.height) // 12))
        self._place_random("wall", count=inner_wall_count)

        if self.stage >= 1:
            self._place_random("food_a", count=3)
            self._place_random("food_b", count=2)
        if self.stage >= 2:
            self._place_random("hazard_a", count=2)
        if self.stage >= 4:
            self._place_random("mystery", count=2)

    def _generate_hidden_rules(self, rule_seed: int) -> None:
        rrng = random.Random(rule_seed)
        configured_shift = self.config.get("rule_shift_tick")
        shift_tick = int(configured_shift) if configured_shift is not None else 50
        if shift_tick >= self.max_ticks:
            shift_tick = max(2, self.max_ticks // 2)
        self._hidden_rules = {
            "food_a_energy": rrng.choice([2, 3, -2]) if self.stage >= 4 else 2,
            "food_b_energy": rrng.choice([1, -3]) if self.stage >= 4 else 1,
            "hazard_damage": rrng.choice([1, 2, 3]) if self.stage >= 2 else 0,
            "mystery_energy": rrng.choice([-2, 2, 4]) if self.stage >= 4 else 0,
            "delayed_poison": self.stage >= 5 and rrng.choice([True, False]),
            "rule_shift_tick": shift_tick if self.stage >= 6 else None,
            "rule_shift_applied": False,
        }

    def _place_random(self, obj: str, count: int) -> None:
        placed = 0
        attempts = 0
        while placed < count and attempts < 500:
            attempts += 1
            x = self.rng.randrange(1, self.width - 1)
            y = self.rng.randrange(1, self.height - 1)
            if (x, y) != self.agent_pos and self._grid[y][x] == "empty":
                self._grid[y][x] = obj
                placed += 1

    def _observe(self) -> Observation:
        if self._family_instance is not None:
            return self._observe_family()
        radius = 1 if self.stage >= 3 else max(self.width, self.height)
        ax, ay = self.agent_pos
        x0 = max(0, ax - radius)
        y0 = max(0, ay - radius)
        x1 = min(self.width, ax + radius + 1)
        y1 = min(self.height, ay + radius + 1)
        rows = []
        for y in range(y0, y1):
            row = []
            for x in range(x0, x1):
                row.append(self._grid[y][x])
            rows.append(tuple(row))

        visible_cues = {
            "view_origin": [x0, y0],
            "agent_view_index": [ax - x0, ay - y0],
            "local_radius": radius,
            **self._last_visible_cues,
        }
        return Observation(
            stage=self.stage,
            tick=self.tick,
            agent_pos=self.agent_pos,
            energy=self.energy,
            health=self.health,
            local_view=tuple(rows),
            last_action_result=dict(self._last_action_result),
            visible_cues=visible_cues,
        )

    def step(self, action: Action) -> tuple[Observation, float, bool, Dict[str, Any]]:
        if self._family_instance is not None:
            return self._step_family(action)
        self.tick += 1
        rule_shift_occurred = self._maybe_rule_shift()

        before = {
            "pos": list(self.agent_pos),
            "energy": self.energy,
            "health": self.health,
        }

        collision = False
        ate = None
        inspected = None
        self._last_visible_cues = {}

        if action in ("up", "down", "left", "right"):
            dx, dy = {
                "up": (0, -1),
                "down": (0, 1),
                "left": (-1, 0),
                "right": (1, 0),
            }[action]
            nx, ny = self.agent_pos[0] + dx, self.agent_pos[1] + dy
            if self._grid[ny][nx] == "wall":
                collision = True
            else:
                self.agent_pos = (nx, ny)
                if self._grid[ny][nx].startswith("hazard"):
                    self.health -= int(self._hidden_rules.get("hazard_damage", 0))

        elif action == "eat":
            x, y = self.agent_pos
            obj = self._grid[y][x]
            if obj.startswith("food") or obj == "mystery":
                ate = obj
                self._apply_consumable(obj)
                self._grid[y][x] = "empty"

        elif action == "inspect":
            inspected = self._inspect_current_or_adjacent()

        elif action == "wait":
            pass

        self._apply_pending_effects()

        self.energy -= 1 if action != "wait" else 0
        done = self.health <= 0 or self.energy <= 0 or self.tick >= self.max_ticks

        after = {
            "pos": list(self.agent_pos),
            "energy": self.energy,
            "health": self.health,
        }

        reward = float((after["energy"] - before["energy"]) + (after["health"] - before["health"]) * 2)

        self._last_action_result = {
            "collision": collision,
            "ate": ate,
            "inspected": inspected,
            "before": before,
            "after": after,
            "rule_shift_occurred": rule_shift_occurred,
        }

        info = {
            "tick": self.tick,
            "action": action,
            "collision": collision,
            "ate": ate,
            "inspected": inspected,
            "rule_shift_occurred": rule_shift_occurred,
            "rule_shift_tick": self._hidden_rules.get("rule_shift_tick"),
        }

        return self._observe(), reward, done, info

    def _apply_consumable(self, obj: str) -> None:
        if obj == "food_a":
            delta = int(self._hidden_rules["food_a_energy"])
        elif obj == "food_b":
            delta = int(self._hidden_rules["food_b_energy"])
        elif obj == "mystery":
            delta = int(self._hidden_rules["mystery_energy"])
        else:
            delta = 0

        self.energy += delta

        if self._hidden_rules.get("delayed_poison") and delta < 0:
            self._pending_effects.append({"delay": 3, "health_delta": -2})

    def _apply_pending_effects(self) -> None:
        remaining = []
        for effect in self._pending_effects:
            effect["delay"] -= 1
            if effect["delay"] <= 0:
                self.health += int(effect.get("health_delta", 0))
                self.energy += int(effect.get("energy_delta", 0))
            else:
                remaining.append(effect)
        self._pending_effects = remaining

    def _inspect_current_or_adjacent(self) -> str | None:
        ax, ay = self.agent_pos
        for x, y in [(ax, ay), (ax, ay - 1), (ax + 1, ay), (ax, ay + 1), (ax - 1, ay)]:
            obj = self._grid[y][x]
            if obj == "mystery":
                cue = "beneficial" if int(self._hidden_rules.get("mystery_energy", 0)) > 0 else "costly"
                self._last_visible_cues = {"inspected_object": "mystery", "inspected_affordance_cue": cue}
                return obj
        return None

    def _maybe_rule_shift(self) -> bool:
        shift_tick = self._hidden_rules.get("rule_shift_tick")
        if (
            shift_tick is not None
            and self.tick == shift_tick
            and not bool(self._hidden_rules.get("rule_shift_applied", False))
        ):
            self._hidden_rules["food_a_energy"] *= -1
            self._hidden_rules["rule_shift_applied"] = True
            return True
        return False

    def debug_hidden_state(self) -> Dict[str, Any]:
        if self._family_instance is not None:
            return self._debug_family_hidden_state()
        return {
            "grid": [list(row) for row in self._grid],
            "hidden_rules": dict(self._hidden_rules),
            "pending_effects": [dict(effect) for effect in self._pending_effects],
            "agent_pos": list(self.agent_pos),
            "energy": self.energy,
            "health": self.health,
        }

    def _observe_family(self) -> Observation:
        assert self._family_instance is not None
        public = self._family_instance.public_observation
        visible_cues = dict(public.get("visible_cues", {}))
        visible_cues.update(
            {
                "family_id": self._family_instance.family_id,
                "split": self._family_instance.split,
                "uncertainty": self._family_uncertainty,
            }
        )
        return Observation(
            stage=self.stage,
            tick=self.tick,
            agent_pos=(1, 1),
            energy=self.energy,
            health=self.health,
            local_view=tuple(tuple(row) for row in public["local_view"]),
            last_action_result=dict(self._last_action_result),
            visible_cues=visible_cues,
        )

    def _step_family(self, action: Action) -> tuple[Observation, float, bool, Dict[str, Any]]:
        assert self._family_instance is not None
        self.tick += 1
        family_id = self._family_instance.family_id
        before = {"pos": [1, 1], "energy": self.energy, "health": self.health}
        reward = 0.0
        info: Dict[str, Any] = {
            "tick": self.tick,
            "action": action,
            "family_id": family_id,
            "source_object_id": None,
            "cause_event_id": None,
            "delayed_effect_event_id": None,
            "delay_ticks": None,
            "rule_phase": self._rule_phase(),
        }
        collision = False
        ate = None
        inspected = None

        if family_id == "aliased_food_v1":
            reward, ate, inspected = self._step_aliased_food(action, info)
        elif family_id == "delayed_poison_v1":
            reward, ate, inspected = self._step_delayed_poison(action, info)
        elif family_id == "contextual_hazard_v1":
            reward, inspected = self._step_contextual_hazard(action, info)
        elif family_id == "rule_reversal_return_v1":
            reward = self._step_rule_reversal(action, info)
        elif family_id == "info_risk_tradeoff_v1":
            reward, ate, inspected = self._step_info_risk(action, info)
        else:
            raise ValueError(f"unknown_family_id:{family_id}")

        delayed_reward = self._apply_family_pending(info)
        reward += delayed_reward
        self.energy += int(reward)
        done = self.health <= 0 or self.energy <= 0 or self.tick >= self.max_ticks
        after = {"pos": [1, 1], "energy": self.energy, "health": self.health}
        self._last_action_result = {
            "collision": collision,
            "ate": ate,
            "inspected": inspected,
            "before": before,
            "after": after,
            "family_id": family_id,
            "rule_phase": info.get("rule_phase"),
        }
        info.update({"collision": collision, "ate": ate, "inspected": inspected})
        return self._observe(), float(reward), done, info

    def _step_aliased_food(self, action: Action, info: Dict[str, Any]) -> tuple[float, str | None, str | None]:
        assert self._family_instance is not None
        latent = self._family_instance.hidden_rule["latent_type"]
        if action == "inspect":
            self._family_uncertainty = 0.0
            info["information_gain"] = 1.0
            return -1.0, None, "food_alias"
        if action == "sample_small_bite":
            self._family_uncertainty = 0.2
            info["information_gain"] = 0.8
            return (1.0 if latent == "nutritive" else -3.0), None, "food_alias"
        if action == "eat" and not self._family_consumed:
            self._family_consumed = True
            info["source_object_id"] = "aliased_food"
            return (7.0 if latent == "nutritive" else -9.0), "food_alias", None
        if action in ("up", "down", "left", "right", "move"):
            return -1.0, None, None
        return 0.0, None, None

    def _step_delayed_poison(self, action: Action, info: Dict[str, Any]) -> tuple[float, str | None, str | None]:
        assert self._family_instance is not None
        latent = self._family_instance.hidden_rule["latent_type"]
        delay = int(self._family_instance.hidden_rule["delay_ticks"])
        if action == "eat" and not self._family_consumed:
            self._family_consumed = True
            info["source_object_id"] = "delayed_food"
            if latent == "delayed_poison":
                self._family_pending.append(
                    {
                        "remaining": delay,
                        "delay_ticks": delay,
                        "reward": -12.0,
                        "source_object_id": "delayed_food",
                        "cause_event_id": self.tick,
                    }
                )
                return 3.0, "food_delay", None
            return 5.0, "food_delay", None
        if action == "sample_small_bite":
            self._family_uncertainty = 0.3
            info["information_gain"] = 0.7
            return -2.0, None, "food_delay"
        if action in ("up", "down", "left", "right", "move"):
            return -1.0, None, None
        return 0.0, None, None

    def _step_contextual_hazard(self, action: Action, info: Dict[str, Any]) -> tuple[float, str | None]:
        assert self._family_instance is not None
        hidden = self._family_instance.hidden_rule
        dangerous = hidden["context"] == hidden["dangerous_context"]
        if action == "inspect":
            self._family_uncertainty = 0.0
            info["information_gain"] = 1.0
            return -1.0, "hazard_alias"
        if action in ("move", "up", "down", "left", "right"):
            return (-8.0 if dangerous else 4.0), None
        return 0.0, None

    def _step_rule_reversal(self, action: Action, info: Dict[str, Any]) -> float:
        phase = str(info.get("rule_phase", "A"))
        good = self._good_choice_for_phase(phase)
        chosen = "red" if action == "left" else "blue" if action == "right" else "none"
        info["chosen_rule_object"] = chosen
        info["good_rule_object"] = good
        if chosen == "none":
            return 0.0
        return 4.0 if chosen == good else -6.0

    def _step_info_risk(self, action: Action, info: Dict[str, Any]) -> tuple[float, str | None, str | None]:
        assert self._family_instance is not None
        latent = self._family_instance.hidden_rule["latent_type"]
        before_uncertainty = self._family_uncertainty
        info["uncertainty_before"] = before_uncertainty
        if action == "inspect":
            self._family_uncertainty = 0.0
            info["uncertainty_after"] = self._family_uncertainty
            info["information_gain"] = before_uncertainty
            return -1.0, None, "mystery"
        if action == "sample_small_bite":
            self._family_uncertainty = 0.25
            info["uncertainty_after"] = self._family_uncertainty
            info["information_gain"] = max(0.0, before_uncertainty - self._family_uncertainty)
            return (-2.0 if latent == "safe_cache" else -4.0), None, "mystery"
        if action == "eat" and not self._family_consumed:
            self._family_consumed = True
            info["source_object_id"] = "risky_cache"
            info["uncertainty_after"] = self._family_uncertainty
            return (8.0 if latent == "safe_cache" else -10.0), "mystery", None
        if action in ("up", "down", "left", "right", "move"):
            return -1.0, None, None
        info["uncertainty_after"] = self._family_uncertainty
        return 0.0, None, None

    def _apply_family_pending(self, info: Dict[str, Any]) -> float:
        remaining = []
        reward = 0.0
        for effect in self._family_pending:
            effect["remaining"] -= 1
            if effect["remaining"] <= 0:
                reward += float(effect["reward"])
                info["source_object_id"] = effect["source_object_id"]
                info["cause_event_id"] = effect["cause_event_id"]
                info["delayed_effect_event_id"] = self.tick
                info["delay_ticks"] = effect["delay_ticks"]
            else:
                remaining.append(effect)
        self._family_pending = remaining
        return reward

    def _rule_phase(self) -> str | None:
        if self._family_instance is None or self._family_instance.family_id != "rule_reversal_return_v1":
            return None
        for phase in self._family_instance.hidden_rule["phase_schedule"]:
            if int(phase["start"]) <= self.tick <= int(phase["end"]):
                return str(phase["phase"])
        return "A_prime"

    def _good_choice_for_phase(self, phase: str) -> str:
        if phase == "B":
            return "blue"
        if phase == "C":
            return "red" if self.tick % 2 == 0 else "blue"
        return "red"

    def _debug_family_hidden_state(self) -> Dict[str, Any]:
        assert self._family_instance is not None
        phase = self._rule_phase()
        hidden = {
            "family_id": self._family_instance.family_id,
            "split": self._family_instance.split,
            "hidden_rules": dict(self._family_instance.hidden_rule),
            "pending_effects": [dict(effect) for effect in self._family_pending],
            "agent_pos": [1, 1],
            "energy": self.energy,
            "health": self.health,
            "oracle_action": self._oracle_family_action(phase),
            "rule_phase": phase,
        }
        return hidden

    def _oracle_family_action(self, phase: str | None) -> Action:
        assert self._family_instance is not None
        family_id = self._family_instance.family_id
        hidden = self._family_instance.hidden_rule
        if family_id == "rule_reversal_return_v1":
            return "left" if self._good_choice_for_phase(str(phase)) == "red" else "right"
        if family_id == "info_risk_tradeoff_v1" and self._family_uncertainty > 0 and hidden["latent_type"] == "risky_cache":
            return "inspect"
        return self._family_instance.oracle_script[min(self.tick, len(self._family_instance.oracle_script) - 1)]  # type: ignore[return-value]
