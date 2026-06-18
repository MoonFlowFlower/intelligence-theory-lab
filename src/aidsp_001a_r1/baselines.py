"""Fair baselines (1-7) + triviality battery + oracle probe instrument.
(Canonical == src/aidsp_001a_r1/baselines.py)"""
from __future__ import annotations

from typing import Dict, List

import numpy as np

from . import prereg as P
from .environment import (AIDSPEnv, cue_likelihood, at_food_likelihood,
                          N_ACTIONS, A_CCW, A_CW, A_STAY)
from .runtypes import StepRecord, EpisodeRun


def _run_policy(agent: str, seed: int, policy, cue_ablated: bool,
                rng_salt: int = 0, reset_state=None) -> EpisodeRun:
    env = AIDSPEnv()
    obs = env.reset(seed=seed, cue_ablated=cue_ablated)
    rng = np.random.default_rng(seed ^ rng_salt)
    run = EpisodeRun(agent=agent, seed=seed, food=env.food, mode="baseline")
    state = reset_state() if reset_state else None
    done = False
    while not done:
        act_dist, state = policy(obs, state, env.t)
        act_dist = np.asarray(act_dist, float)
        act_dist = act_dist / act_dist.sum()
        action = int(rng.choice(N_ACTIONS, p=act_dist))
        obs_next, info, done = env.step(action)
        run.observations.append((obs_next.cue, obs_next.proprioception, obs_next.at_food))
        run.steps.append(StepRecord(
            t=info["t"], pos=info["pos"], action=action,
            action_dist=[float(x) for x in act_dist],
            cue=obs_next.cue, at_food=obs_next.at_food, energy=obs_next.energy,
            in_dark_room=info["in_dark_room"], in_noisy_tv=info["in_noisy_tv"],
            cum_cost=info["cum_cost"]))
        obs = obs_next
    return run


def _pi_random(obs, state, t):
    return np.ones(N_ACTIONS) / N_ACTIONS, state

def _pi_stay(obs, state, t):
    d = np.zeros(N_ACTIONS); d[A_STAY] = 1.0; return d, state

def _pi_sweep_cw(obs, state, t):
    d = np.zeros(N_ACTIONS); d[A_CW] = 1.0; return d, state

def _pi_sweep_ccw(obs, state, t):
    d = np.zeros(N_ACTIONS); d[A_CCW] = 1.0; return d, state

def _pi_pingpong(obs, state, t):
    d = np.zeros(N_ACTIONS)
    d[A_CW if (t < P.RING_SIZE) else A_CCW] = 1.0
    return d, state


def _pi_obs_only_lookup(obs, state, t):
    d = np.zeros(N_ACTIONS)
    d[A_CW if obs.cue == P.CUE_CW else A_CCW] = 1.0
    return d, state

def _pi_behavior_tree(obs, state, t, temp=0.5):
    util = np.array([0.0, 0.0, -0.2])
    if obs.cue == P.CUE_CW:
        util[A_CW] += 1.0
    else:
        util[A_CCW] += 1.0
    if obs.at_food == 1:
        util[A_STAY] += 1.5
    z = np.exp(util / temp)
    return z / z.sum(), state


def _drive(energy: int) -> float:
    return float(P.ENERGY_SETPOINT - energy)


class TabularQ:
    def __init__(self, n_states: int, n_actions: int = N_ACTIONS):
        self.Q = np.zeros((n_states, n_actions))

    def act_greedy(self, s: int) -> np.ndarray:
        a = int(np.argmax(self.Q[s]))
        d = np.zeros(self.Q.shape[1]); d[a] = 1.0
        return d


def _homeo_state(pos, energy, cue):
    return (pos * P.ENERGY_LEVELS + energy) * P.N_CUE + cue

def _count_state(pos, cue):
    return pos * P.N_CUE + cue


def train_homeostatic_q() -> TabularQ:
    q = TabularQ(P.RING_SIZE * P.ENERGY_LEVELS * P.N_CUE)
    rng = np.random.default_rng(424242)
    for seed in P.TRAIN_SEEDS:
        env = AIDSPEnv(); obs = env.reset(seed=seed)
        s = _homeo_state(obs.proprioception, obs.energy, obs.cue)
        done = False
        while not done:
            a = int(rng.integers(N_ACTIONS)) if rng.random() < P.Q_LEARN_EPS else int(np.argmax(q.Q[s]))
            d_before = _drive(obs.energy)
            obs2, info, done = env.step(a)
            r = d_before - _drive(obs2.energy)
            s2 = _homeo_state(obs2.proprioception, obs2.energy, obs2.cue)
            q.Q[s, a] += P.Q_LEARN_ALPHA * (r + P.Q_LEARN_GAMMA * np.max(q.Q[s2]) - q.Q[s, a])
            s, obs = s2, obs2
    return q


def train_count_based_q() -> TabularQ:
    q = TabularQ(P.RING_SIZE * P.N_CUE)
    counts = np.zeros(P.RING_SIZE * P.N_CUE)
    rng = np.random.default_rng(525252)
    for seed in P.TRAIN_SEEDS:
        env = AIDSPEnv(); obs = env.reset(seed=seed)
        s = _count_state(obs.proprioception, obs.cue)
        done = False
        while not done:
            a = int(rng.integers(N_ACTIONS)) if rng.random() < P.Q_LEARN_EPS else int(np.argmax(q.Q[s]))
            obs2, info, done = env.step(a)
            s2 = _count_state(obs2.proprioception, obs2.cue)
            counts[s2] += 1
            r = P.COUNT_BONUS_BETA / np.sqrt(counts[s2]) + (1.0 if info["ate"] else 0.0)
            q.Q[s, a] += P.Q_LEARN_ALPHA * (r + P.Q_LEARN_GAMMA * np.max(q.Q[s2]) - q.Q[s, a])
            s, obs = s2, obs2
    return q


def run_homeostatic(seed, q: TabularQ, cue_ablated=False) -> EpisodeRun:
    def pol(obs, state, t):
        return q.act_greedy(_homeo_state(obs.proprioception, obs.energy, obs.cue)), state
    return _run_policy("homeostatic_rl", seed, pol, cue_ablated, rng_salt=0xA1)

def run_count_based(seed, q: TabularQ, cue_ablated=False) -> EpisodeRun:
    def pol(obs, state, t):
        return q.act_greedy(_count_state(obs.proprioception, obs.cue)), state
    return _run_policy("count_based_rl", seed, pol, cue_ablated, rng_salt=0xB2)


def _entropy(p: np.ndarray) -> float:
    nz = p[p > 0]
    return float(-(nz * np.log2(nz)).sum())

def _expected_info_gain(belief: np.ndarray, pos: int) -> float:
    H0 = _entropy(belief)
    exp_H = 0.0
    for c in range(P.N_CUE):
        for d in range(P.N_AT_FOOD):
            joint = np.array([belief[f] * cue_likelihood(f, pos)[c] * at_food_likelihood(f, pos)[d]
                              for f in range(P.RING_SIZE)])
            m = joint.sum()
            if m <= 0:
                continue
            exp_H += m * _entropy(joint / m)
    return H0 - exp_H

def _bayes(belief, pos, cue, at_food):
    b = belief.copy()
    for f in range(P.RING_SIZE):
        b[f] *= cue_likelihood(f, pos)[cue] * at_food_likelihood(f, pos)[at_food]
    s = b.sum()
    return b / s if s > 0 else belief

def _map_update(belief: np.ndarray, pos: int) -> np.ndarray:
    best_p, best_c, best_d = -1.0, 0, 0
    for c in range(P.N_CUE):
        for d in range(P.N_AT_FOOD):
            m = sum(belief[f] * cue_likelihood(f, pos)[c] * at_food_likelihood(f, pos)[d]
                    for f in range(P.RING_SIZE))
            if m > best_p:
                best_p, best_c, best_d = m, c, d
    return _bayes(belief, pos, best_c, best_d)

def _map_rollout_value(belief, start_pos, first_action, horizon):
    from .environment import ACTION_DELTA
    b = belief.copy(); pos = start_pos; total = 0.0
    for k in range(horizon):
        if k == 0:
            a = first_action
        else:
            best, a = -1.0, A_STAY
            for aa in range(N_ACTIONS):
                np_ = (pos + ACTION_DELTA[aa]) % P.RING_SIZE
                ig = _expected_info_gain(b, np_)
                if ig > best:
                    best, a = ig, aa
        pos = (pos + ACTION_DELTA[a]) % P.RING_SIZE
        total += _expected_info_gain(b, pos) / (k + 1)
        b = _map_update(b, pos)
    return total


def run_oracle(seed, cue_ablated=False, horizon=None) -> EpisodeRun:
    if horizon is None:
        horizon = P.RING_SIZE
    env = AIDSPEnv(); obs = env.reset(seed=seed, cue_ablated=cue_ablated)
    belief = np.zeros(P.RING_SIZE)
    for c in P.normal_cells():
        belief[c] = 1.0
    belief /= belief.sum()
    belief = _bayes(belief, obs.proprioception, obs.cue, obs.at_food)
    run = EpisodeRun(agent="oracle_probe", seed=seed, food=env.food, mode="probe")
    done = False
    while not done:
        pos = obs.proprioception
        vals = [_map_rollout_value(belief, pos, a, horizon) for a in range(N_ACTIONS)]
        a = int(np.argmax(vals))
        d = np.zeros(N_ACTIONS); d[a] = 1.0
        obs2, info, done = env.step(a)
        belief = _bayes(belief, obs2.proprioception, obs2.cue, obs2.at_food)
        run.observations.append((obs2.cue, obs2.proprioception, obs2.at_food))
        run.steps.append(StepRecord(
            t=info["t"], pos=info["pos"], action=a, action_dist=[float(x) for x in d],
            cue=obs2.cue, at_food=obs2.at_food, energy=obs2.energy,
            in_dark_room=info["in_dark_room"], in_noisy_tv=info["in_noisy_tv"],
            cum_cost=info["cum_cost"]))
        obs = obs2
    return run


TRIVIAL_BATTERY = {
    "random_walk": _pi_random,
    "stay_still": _pi_stay,
    "exhaustive_sweep": _pi_sweep_cw,
    "systematic_coverage": _pi_sweep_ccw,
    "cue_ignoring_greedy": _pi_pingpong,
}

def run_trivial(name, seed, cue_ablated=False) -> EpisodeRun:
    return _run_policy(name, seed, TRIVIAL_BATTERY[name], cue_ablated, rng_salt=hash(name) & 0xFFFF)

def run_obs_only(seed, cue_ablated=False) -> EpisodeRun:
    return _run_policy("observation_only_lookup", seed, _pi_obs_only_lookup, cue_ablated, rng_salt=0xC3)

def run_behavior_tree(seed, cue_ablated=False) -> EpisodeRun:
    return _run_policy("behavior_tree_softmax", seed,
                       lambda o, s, t: _pi_behavior_tree(o, s, t), cue_ablated, rng_salt=0xD4)
