from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import numpy as np

from . import BASE_SEED

ENV_NAME = "E_bandit"
K_ARMS = 10
P_BEST = 0.6
P_OTHERS = 0.5
HORIZON = 100


def derive_seed(*parts: object, base_seed: int = BASE_SEED) -> int:
    payload = json.dumps([base_seed, *parts], separators=(",", ":"), sort_keys=True)
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


@dataclass(frozen=True)
class BanditEpisode:
    env: str
    seed_index: int
    best_arm: int
    arm_probabilities: np.ndarray
    reward_table: np.ndarray
    horizon: int = HORIZON

    def reward(self, t: int, arm: int) -> int:
        if t not in range(self.horizon):
            raise ValueError(f"t outside [0,{self.horizon - 1}]: {t}")
        if arm not in range(K_ARMS):
            raise ValueError(f"arm outside [0,{K_ARMS - 1}]: {arm}")
        return int(self.reward_table[t, arm])


class BanditEnv:
    def __init__(self, base_seed: int = BASE_SEED):
        self.base_seed = base_seed

    def sample_episode(self, seed_index: int) -> BanditEpisode:
        best_rng = np.random.default_rng(
            derive_seed(ENV_NAME, seed_index, "best-arm", base_seed=self.base_seed)
        )
        best_arm = int(best_rng.integers(low=0, high=K_ARMS))
        probabilities = np.full(K_ARMS, P_OTHERS, dtype=float)
        probabilities[best_arm] = P_BEST
        reward_rng = np.random.default_rng(
            derive_seed(ENV_NAME, seed_index, "rewards", base_seed=self.base_seed)
        )
        reward_table = reward_rng.binomial(
            n=1,
            p=np.broadcast_to(probabilities, (HORIZON, K_ARMS)),
        ).astype(np.int8)
        return BanditEpisode(
            env=ENV_NAME,
            seed_index=seed_index,
            best_arm=best_arm,
            arm_probabilities=probabilities,
            reward_table=reward_table,
        )

