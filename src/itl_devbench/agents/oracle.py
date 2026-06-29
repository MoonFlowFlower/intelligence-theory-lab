from __future__ import annotations

from collections import deque
from typing import Any, Dict

from itl_devbench.agents.base import Agent, center_cell
from itl_devbench.core.types import Action, Observation, Prediction


class OracleAgent(Agent):
    agent_id = "oracle"
    agent_kind = "oracle"

    def __init__(self) -> None:
        super().__init__(variant="hidden_state_headroom")

    def predict(self, obs: Observation) -> Prediction:
        return Prediction(confidence=1.0)

    def act(self, obs: Observation, prediction: Prediction) -> Action:
        return "wait"

    def act_with_hidden(self, obs: Observation, prediction: Prediction, hidden: Dict[str, Any]) -> Action:
        if "oracle_action" in hidden:
            return hidden["oracle_action"]
        current = center_cell(obs)
        rules = hidden.get("hidden_rules", {})
        if _consumable_immediate_reward(current, rules) > 0:
            return "eat"

        plan = _best_positive_net_reward_path(hidden)
        if plan:
            return plan[0]
        return "wait"


def _best_positive_net_reward_path(hidden: Dict[str, Any]) -> list[Action]:
    ax, ay = hidden.get("agent_pos", [0, 0])
    rules = hidden.get("hidden_rules", {})
    grid = hidden.get("grid", [])
    best: tuple[int, list[Action]] | None = None
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            immediate_reward = _consumable_immediate_reward(cell, rules)
            if immediate_reward <= 0:
                continue
            path = _shortest_safe_path(grid, (int(ax), int(ay)), (x, y))
            if path is None:
                continue
            # Movement actions each cost one reward point; the final eat reward
            # is already net of the eat action's energy cost.
            net_reward = immediate_reward - len(path)
            if net_reward > 0 and (best is None or net_reward > best[0] or len(path) < len(best[1])):
                best = (net_reward, path)
    return best[1] if best is not None else []


def _shortest_safe_path(grid: list[list[str]], start: tuple[int, int], target: tuple[int, int]) -> list[Action] | None:
    if start == target:
        return []
    queue: deque[tuple[tuple[int, int], list[Action]]] = deque([(start, [])])
    seen = {start}
    moves: list[tuple[Action, tuple[int, int]]] = [
        ("up", (0, -1)),
        ("down", (0, 1)),
        ("left", (-1, 0)),
        ("right", (1, 0)),
    ]
    while queue:
        (x, y), path = queue.popleft()
        for action, (dx, dy) in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) in seen:
                continue
            if ny < 0 or ny >= len(grid) or nx < 0 or nx >= len(grid[ny]):
                continue
            cell = grid[ny][nx]
            if cell == "wall" or cell.startswith("hazard"):
                continue
            next_path = [*path, action]
            if (nx, ny) == target:
                return next_path
            seen.add((nx, ny))
            queue.append(((nx, ny), next_path))
    return None


def _consumable_immediate_reward(cell: str, rules: Dict[str, Any]) -> int:
    if cell == "food_a":
        return int(rules.get("food_a_energy", 0)) - 1
    if cell == "food_b":
        return int(rules.get("food_b_energy", 0)) - 1
    if cell == "mystery":
        return int(rules.get("mystery_energy", 0)) - 1
    return 0
