"""EFE active-inference candidate via pymdp.legacy. (Canonical == src/aidsp_001a_r1/candidate_efe.py)

Modes: full | epistemic_ablation | no_transition. Full per-step trace with
epistemic & pragmatic EFE components; seeded action sampling for replay.
"""
from __future__ import annotations

import numpy as np
from pymdp.legacy import utils
from pymdp.legacy.control import (
    construct_policies, update_posterior_policies, get_expected_states,
    get_expected_obs, calc_expected_utility, calc_states_info_gain,
)

from . import prereg as P
from . import gen_model as GM
from .environment import (AIDSPEnv, cue_likelihood, at_food_likelihood, N_ACTIONS)
from .runtypes import StepRecord, EpisodeRun

MODES = ("full", "epistemic_ablation", "no_transition")


def _policies():
    return construct_policies(GM.NUM_STATES, GM.NUM_CONTROLS, policy_len=P.EFE_POLICY_LEN)


def run_efe_episode(seed: int, mode: str = "full", cue_ablated: bool = False,
                    gamma: float = P.EFE_GAMMA, at_food_pref: float = 2.0) -> EpisodeRun:
    assert mode in MODES, mode
    use_info_gain = (mode != "epistemic_ablation")
    no_trans = (mode == "no_transition")

    A = GM.build_A()
    B = GM.build_B(no_transition_ablation=no_trans)
    C = GM.build_C(at_food_pref=at_food_pref)
    D = GM.build_D()
    policies = _policies()
    action_of_policy = [int(pol[0, GM.F_POS]) for pol in policies]

    env = AIDSPEnv()
    obs = env.reset(seed=seed, cue_ablated=cue_ablated)
    rng = np.random.default_rng(seed ^ 0x5EFE)

    food_belief = D[GM.F_FOOD].copy()
    # condition on the FREE reset observation at the start cell (same for all
    # agents; excluded from the M1 estimator stream so it credits no one).
    for f in range(P.RING_SIZE):
        food_belief[f] *= (cue_likelihood(f, obs.proprioception)[obs.cue]
                           * at_food_likelihood(f, obs.proprioception)[obs.at_food])
    s0 = food_belief.sum()
    if s0 > 0:
        food_belief /= s0
    run = EpisodeRun(agent="candidate_efe", seed=seed, food=env.food, mode=mode)

    done = False
    while not done:
        pos = obs.proprioception
        qs = utils.obj_array(2)
        qs[GM.F_FOOD] = food_belief.copy()
        qpos = np.zeros(P.RING_SIZE); qpos[pos] = 1.0
        qs[GM.F_POS] = qpos
        belief_before = food_belief.copy()

        prag, epis = [], []
        for pol in policies:
            qs_pi = get_expected_states(qs, B, pol)
            qo_pi = get_expected_obs(qs_pi, A)
            prag.append(float(calc_expected_utility(qo_pi, C)))
            epis.append(float(calc_states_info_gain(A, qs_pi)) if use_info_gain else 0.0)

        q_pi, G = update_posterior_policies(
            qs, A, B, C, policies, use_utility=True,
            use_states_info_gain=use_info_gain, use_param_info_gain=False, gamma=gamma)
        q_pi = np.asarray(q_pi, dtype=float)
        q_pi = q_pi / q_pi.sum()

        act_dist = np.zeros(N_ACTIONS)
        for i, a in enumerate(action_of_policy):
            act_dist[a] += q_pi[i]
        act_dist = act_dist / act_dist.sum()
        action = int(rng.choice(N_ACTIONS, p=act_dist))

        chosen_pol = policies[action_of_policy.index(action)] if action in action_of_policy else policies[0]
        qs_pi_chosen = get_expected_states(qs, B, chosen_pol)
        qo_pi_chosen = get_expected_obs(qs_pi_chosen, A)
        pred_cue = np.asarray(qo_pi_chosen[0][GM.M_CUE], dtype=float)
        pred_cue = pred_cue / pred_cue.sum()

        obs_next, info, done = env.step(action)
        actual_cue = obs_next.cue
        pred_error = float(-np.log2(max(pred_cue[actual_cue], 1e-12)))

        fb = food_belief.copy()
        for f in range(P.RING_SIZE):
            pc = cue_likelihood(f, obs_next.proprioception)[actual_cue]
            pa = at_food_likelihood(f, obs_next.proprioception)[obs_next.at_food]
            fb[f] = fb[f] * pc * pa
        s = fb.sum()
        food_belief = fb / s if s > 0 else food_belief

        run.observations.append((obs_next.cue, obs_next.proprioception, obs_next.at_food))
        run.steps.append(StepRecord(
            t=info["t"], pos=info["pos"], action=action,
            action_dist=[float(x) for x in act_dist],
            cue=obs_next.cue, at_food=obs_next.at_food, energy=obs_next.energy,
            in_dark_room=info["in_dark_room"], in_noisy_tv=info["in_noisy_tv"],
            cum_cost=info["cum_cost"],
            belief_food_before=[float(x) for x in belief_before],
            efe_pragmatic=prag, efe_epistemic=epis,
            neg_efe_G=[float(x) for x in (-np.asarray(G))],
            pred_cue_dist=[float(x) for x in pred_cue], pred_error=pred_error,
            belief_food_after=[float(x) for x in food_belief]))
        obs = obs_next
    return run
