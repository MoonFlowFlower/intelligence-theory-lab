"""NoisyCueRing POMDP environment + independent posterior estimator.
(Canonical == src/aidsp_001a_r1/environment.py)

ONE source of truth for the cue / at-food likelihoods. Likelihood tensors are
precomputed once at import (memoization) for speed; values are bit-identical to
the elementwise definition. Food location is the only hidden per-episode
parameter and is never exposed to the estimator or any agent (except the planted
leakage positive controls, which the scanner must catch).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from . import prereg as P

A_CCW, A_CW, A_STAY = 0, 1, 2
N_ACTIONS = 3
ACTION_DELTA = {A_CCW: -1, A_CW: +1, A_STAY: 0}
ACTION_NAMES = {A_CCW: "ccw", A_CW: "cw", A_STAY: "stay"}


def ring_shortest_dir(pos: int, food: int, L: int) -> Optional[int]:
    if pos == food:
        return None
    dist_cw = (food - pos) % L
    dist_ccw = (pos - food) % L
    if dist_cw < dist_ccw:
        return P.CUE_CW
    if dist_ccw < dist_cw:
        return P.CUE_CCW
    return None


def _cue_likelihood_compute(food: int, pos: int) -> np.ndarray:
    p = np.zeros(P.N_CUE)
    if pos == P.DARK_ROOM_CELL:
        p[P.DARK_ROOM_CONST_CUE] = 1.0
        return p
    if pos == P.NOISY_TV_CELL:
        p[:] = 1.0 / P.N_CUE
        return p
    true_dir = ring_shortest_dir(pos, food, P.RING_SIZE)
    if true_dir is None:
        p[:] = 1.0 / P.N_CUE
        return p
    eps = P.terrain_eps(pos)
    p[true_dir] = 1.0 - eps
    p[1 - true_dir] = eps
    return p


def _at_food_likelihood_compute(food: int, pos: int) -> np.ndarray:
    p_one = P.P_AT_FOOD_DETECT if pos == food else P.P_AT_FOOD_FALSEPOS
    return np.array([1.0 - p_one, p_one])


# precompute tensors [food, pos, outcome] once
_CUE_LIK = np.zeros((P.RING_SIZE, P.RING_SIZE, P.N_CUE))
_ATFOOD_LIK = np.zeros((P.RING_SIZE, P.RING_SIZE, P.N_AT_FOOD))
for _f in range(P.RING_SIZE):
    for _s in range(P.RING_SIZE):
        _CUE_LIK[_f, _s] = _cue_likelihood_compute(_f, _s)
        _ATFOOD_LIK[_f, _s] = _at_food_likelihood_compute(_f, _s)


def cue_likelihood(food: int, pos: int) -> np.ndarray:
    return _CUE_LIK[food, pos]


def at_food_likelihood(food: int, pos: int) -> np.ndarray:
    return _ATFOOD_LIK[food, pos]


@dataclass
class Observation:
    proprioception: int
    cue: int
    at_food: int
    energy: int
    food_loc_oracle: Optional[int] = None
    special_label: Optional[int] = None

    def channels(self) -> dict:
        d = {"proprioception": self.proprioception, "cue": self.cue,
             "at_food": self.at_food, "energy": self.energy}
        if self.food_loc_oracle is not None:
            d["food_loc_oracle"] = self.food_loc_oracle
        if self.special_label is not None:
            d["special_label"] = self.special_label
        return d


class AIDSPEnv:
    def __init__(self, leak_food_oracle: bool = False, leak_special_label: bool = False):
        self.L = P.RING_SIZE
        self.leak_food_oracle = leak_food_oracle
        self.leak_special_label = leak_special_label
        self._rng = None
        self.food = -1
        self.pos = -1
        self.energy = P.ENERGY_SETPOINT
        self.t = 0
        self.cum_cost = 0.0
        self.cue_ablated = False

    def reset(self, seed: int, cue_ablated: bool = False) -> Observation:
        self._rng = np.random.default_rng(seed)
        self.cue_ablated = cue_ablated
        self.food = int(self._rng.choice(P.normal_cells()))
        self.pos = P.AGENT_START_CELL
        self.energy = P.ENERGY_SETPOINT
        self.t = 0
        self.cum_cost = 0.0
        return self._observe()

    def _sample_cue(self) -> int:
        if self.cue_ablated:
            return int(self._rng.integers(P.N_CUE))
        return int(self._rng.choice(P.N_CUE, p=cue_likelihood(self.food, self.pos)))

    def _sample_at_food(self) -> int:
        return int(self._rng.choice(2, p=at_food_likelihood(self.food, self.pos)))

    def _observe(self) -> Observation:
        return Observation(
            proprioception=self.pos, cue=self._sample_cue(), at_food=self._sample_at_food(),
            energy=self.energy,
            food_loc_oracle=(self.food if self.leak_food_oracle else None),
            special_label=(self._special_label() if self.leak_special_label else None))

    def _special_label(self) -> int:
        if self.pos == P.DARK_ROOM_CELL:
            return 1
        if self.pos == P.NOISY_TV_CELL:
            return 2
        return 0

    def step(self, action: int):
        assert action in ACTION_DELTA, f"bad action {action}"
        self.pos = (self.pos + ACTION_DELTA[action]) % self.L
        self.t += 1
        self.cum_cost += P.PER_ACTION_COST
        self.energy = max(0, self.energy - P.ENERGY_DECAY_PER_STEP)
        ate = (self.pos == self.food)
        if ate:
            self.energy = P.ENERGY_ON_EAT
        obs = self._observe()
        info = {"t": self.t, "food": self.food, "pos": self.pos,
                "cum_cost": self.cum_cost, "ate": ate,
                "in_dark_room": self.pos == P.DARK_ROOM_CELL,
                "in_noisy_tv": self.pos == P.NOISY_TV_CELL,
                "terrain_eps": (None if self.pos in (P.DARK_ROOM_CELL, P.NOISY_TV_CELL)
                                else P.terrain_eps(self.pos))}
        done = self.t >= P.STEP_BUDGET
        return obs, info, done


class FoodPosteriorEstimator:
    """Bayes filter over food location from OBSERVATIONS ONLY (metric instrument)."""

    def __init__(self):
        cells = P.normal_cells()
        self.support = np.array(cells, dtype=int)
        self.logp = np.zeros(len(cells))

    def _renorm(self):
        m = self.logp.max()
        w = np.exp(self.logp - m)
        w /= w.sum()
        self.logp = np.log(np.clip(w, 1e-300, None))

    def posterior(self) -> np.ndarray:
        m = self.logp.max()
        w = np.exp(self.logp - m)
        return w / w.sum()

    def entropy_bits(self) -> float:
        p = self.posterior()
        nz = p[p > 0]
        return float(-(nz * np.log2(nz)).sum())

    def update(self, cue: int, pos: int, at_food: int):
        pc = _CUE_LIK[self.support, pos, cue]
        pa = _ATFOOD_LIK[self.support, pos, at_food]
        self.logp += np.log(np.clip(pc, 1e-300, None)) + np.log(np.clip(pa, 1e-300, None))
        self._renorm()
