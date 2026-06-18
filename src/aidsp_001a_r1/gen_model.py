"""pymdp.legacy generative model for the candidate (and ablations).

The candidate is model-based: it is given the TRUE likelihood structure (the
"physics") via A, and action-conditioned transitions via B, but NOT the
per-episode food location (D over food is uniform). This model-based vs
model-free asymmetry is LEGITIMATE and declared per the task card; it is logged
in baseline_comparison.json.
"""
from __future__ import annotations

import numpy as np
from pymdp.legacy import utils

from . import prereg as P
from .environment import (cue_likelihood, at_food_likelihood, N_ACTIONS,
                          ACTION_DELTA)

# factor / modality indexing
F_FOOD, F_POS = 0, 1
M_PROPRIO, M_CUE, M_ATFOOD = 0, 1, 2

NUM_STATES = [P.RING_SIZE, P.RING_SIZE]
NUM_OBS = [P.RING_SIZE, P.N_CUE, P.N_AT_FOOD]
NUM_CONTROLS = [1, N_ACTIONS]          # food uncontrollable; pos has 3 moves


def build_A():
    A = utils.obj_array(3)
    L = P.RING_SIZE
    # proprioception: observe position exactly, independent of food
    A0 = np.zeros((L, L, L))
    for f in range(L):
        for s in range(L):
            A0[s, f, s] = 1.0
    A[M_PROPRIO] = A0
    # cue: noisy bearing P(cue | food, pos)
    A1 = np.zeros((P.N_CUE, L, L))
    for f in range(L):
        for s in range(L):
            A1[:, f, s] = cue_likelihood(f, s)
    A[M_CUE] = A1
    # at-food detector
    A2 = np.zeros((P.N_AT_FOOD, L, L))
    for f in range(L):
        for s in range(L):
            A2[:, f, s] = at_food_likelihood(f, s)
    A[M_ATFOOD] = A2
    return A


def build_B(no_transition_ablation: bool = False):
    """B[F_FOOD] identity (food static). B[F_POS] action-conditioned ring move.

    no_transition_ablation: agent's position transition is made action-INDEPENDENT
    (all actions map to identity), so EFE cannot use action-conditioning to plan
    active sensing. Tests that action-conditioning is load-bearing.
    """
    L = P.RING_SIZE
    B = utils.obj_array(2)
    Bf = np.zeros((L, L, 1))
    Bf[:, :, 0] = np.eye(L)
    B[F_FOOD] = Bf
    Bp = np.zeros((L, L, N_ACTIONS))
    for a in range(N_ACTIONS):
        for cur in range(L):
            nxt = cur if no_transition_ablation else (cur + ACTION_DELTA[a]) % L
            Bp[nxt, cur, a] = 1.0
    B[F_POS] = Bp
    return B


def build_C(at_food_pref: float = 2.0):
    """Pragmatic preference: prefer the at-food detector firing (eating proxy)."""
    C = utils.obj_array(3)
    C[M_PROPRIO] = np.zeros(P.RING_SIZE)
    C[M_CUE] = np.zeros(P.N_CUE)
    c2 = np.zeros(P.N_AT_FOOD)
    c2[1] = at_food_pref
    C[M_ATFOOD] = c2
    return C


def build_D():
    """Prior: food uniform over NORMAL cells; position delta at start."""
    L = P.RING_SIZE
    D = utils.obj_array(2)
    df = np.zeros(L)
    for c in P.normal_cells():
        df[c] = 1.0
    df /= df.sum()
    D[F_FOOD] = df
    dp = np.zeros(L)
    dp[P.AGENT_START_CELL] = 1.0
    D[F_POS] = dp
    return D
