"""Tests for AIDSP-001A-R1. Validate the fail-able properties the verdict relies on.

Fast (small seed counts). Run: pytest tests/test_aidsp_001a_r1.py
"""
import os
import sys

import numpy as np
import pytest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from aidsp_001a_r1 import prereg as P
from aidsp_001a_r1 import baselines as B
from aidsp_001a_r1 import gen_model as GM
from aidsp_001a_r1.environment import (
    AIDSPEnv, cue_likelihood, at_food_likelihood, FoodPosteriorEstimator)
from aidsp_001a_r1.candidate_efe import run_efe_episode
from aidsp_001a_r1.metrics import compute_M1, compute_M2_episode, entropy_trajectory
from aidsp_001a_r1.leakage import run_positive_controls, mutual_info_bits
from aidsp_001a_r1.harness import (run_triviality_probe, compute_verdict)

SEEDS = P.SEED_FAMILY_A[:10]


def test_seed_families_disjoint():
    assert set(P.SEED_FAMILY_A).isdisjoint(P.SEED_FAMILY_B)
    assert set(P.TRAIN_SEEDS).isdisjoint(P.SEED_FAMILY_A)
    assert set(P.TRAIN_SEEDS).isdisjoint(P.SEED_FAMILY_B)


def test_special_cells_uninformative():
    # dark-room cue is constant; noisy-TV cue is uniform; both independent of food
    for f in P.normal_cells():
        dr = cue_likelihood(f, P.DARK_ROOM_CELL)
        tv = cue_likelihood(f, P.NOISY_TV_CELL)
        assert dr[P.DARK_ROOM_CONST_CUE] == 1.0
        assert np.allclose(tv, np.ones(P.N_CUE) / P.N_CUE)


def test_cue_is_not_a_food_label():
    # MI(cue;food) over a random trajectory must be far below H(food)
    rep = run_positive_controls(seeds=P.SEED_FAMILY_A[:30])
    cue_mi = rep["clean_interface"]["per_channel"]["cue"]["mi_food_bits"]
    assert cue_mi < 0.9 * np.log2(len(P.normal_cells()))


def test_estimator_entropy_nonincreasing_in_expectation_and_independent():
    # the estimator uses ONLY observations; feed it a sweep's obs and check it
    # starts at full entropy and ends lower (information was acquired)
    run = B.run_trivial("exhaustive_sweep", SEEDS[0])
    H = entropy_trajectory(run.observations)
    assert abs(H[0] - np.log2(len(P.normal_cells()))) < 1e-9
    assert H[-1] <= H[0] + 1e-9


def test_cue_ignoring_strategies_have_zero_M2():
    # PF1 validity: cue-ignoring trivial strategies are invariant to cue ablation
    for name in ["random_walk", "stay_still", "exhaustive_sweep",
                 "systematic_coverage", "cue_ignoring_greedy"]:
        m2 = np.mean([compute_M2_episode(B.run_trivial(name, s),
                                         B.run_trivial(name, s, True)) for s in SEEDS])
        assert m2 <= P.TAU_M2_FLOOR, f"{name} M2={m2} should be ~0"


def test_cue_user_has_positive_M2():
    m2 = np.mean([compute_M2_episode(B.run_obs_only(s), B.run_obs_only(s, True))
                  for s in SEEDS])
    assert m2 > P.TAU_M2_FLOOR


def test_leakage_scanner_is_failable():
    rep = run_positive_controls(seeds=P.SEED_FAMILY_A[:40])
    s = rep["summary"]
    assert s["clean_interface_passes"] is True
    assert s["caught_food_oracle_named"] is True
    # the BINDING name-independent fail-ability: a renamed full-food leak is caught
    assert s["caught_food_oracle_renamed_statistically"] is True
    assert s["renamed_leak_not_caught_by_name_only"] is True
    assert s["caught_special_label"] is True
    assert s["scanner_failable"] is True


def test_epistemic_ablation_zeroes_infogain_terms():
    full = run_efe_episode(SEEDS[0], "full")
    abl = run_efe_episode(SEEDS[0], "epistemic_ablation")
    assert any(any(abs(x) > 0 for x in st.efe_epistemic) for st in full.steps)
    assert all(all(x == 0.0 for x in st.efe_epistemic) for st in abl.steps)


def test_no_transition_makes_actions_indistinguishable():
    # if the agent's model has action-independent transitions, EFE cannot prefer a
    # move for active sensing -> action distribution is ~uniform (myopic degeneracy)
    run = run_efe_episode(SEEDS[0], "no_transition")
    first = np.array(run.steps[0].action_dist)
    assert np.allclose(first, np.ones(len(first)) / len(first), atol=1e-6)


def test_replay_determinism():
    a = run_efe_episode(SEEDS[1], "full")
    b = run_efe_episode(SEEDS[1], "full")
    assert [s.action for s in a.steps] == [s.action for s in b.steps]


def test_M1_uses_estimator_not_candidate_belief():
    # M1 is a function of the observation stream only; permuting the candidate's
    # internal belief fields must not change M1 (compute_M1 takes observations).
    run = run_efe_episode(SEEDS[2], "full")
    m1_a = compute_M1(run.observations)
    for st in run.steps:           # corrupt candidate's self-reported belief
        st.belief_food_after = [0.0] * P.RING_SIZE
    m1_b = compute_M1(run.observations)
    assert m1_a == m1_b


def test_verdict_is_computed_function_of_inputs():
    # scanner-not-failable -> invalid; degenerate probe -> invalid_metric_degenerate
    bad_pc = {"summary": {"scanner_failable": False}}
    good_secret = {"run_path_clean": True}
    v = compute_verdict({"metric_degenerate": False}, None, None, bad_pc, good_secret)
    assert v["verdict"] == "invalid_due_to_leakage_or_contract_failure"
    good_pc = {"summary": {"scanner_failable": True}}
    v2 = compute_verdict({"metric_degenerate": True, "PF1_m2_validity_fail": False,
                          "PF2_m1_headroom_fail": True, "PF3_m2_detectability_fail": False},
                         None, None, good_pc, good_secret)
    assert v2["verdict"] == "invalid_metric_degenerate"


def test_band_derivation_rule():
    probe = run_triviality_probe(SEEDS)
    mt = probe["max_trivial_M1"]
    assert abs(probe["band"] - max(mt * (1 + P.DELTA_REL), mt + P.DELTA_ABS_FLOOR)) < 1e-12


def test_food_never_on_special_cells():
    for s in SEEDS:
        env = AIDSPEnv(); env.reset(seed=s)
        assert env.food in P.normal_cells()
