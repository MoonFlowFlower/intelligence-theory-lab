"""Smoke checks on placeholder data (seed 9001) — no candidate-vs-control
comparative metrics. Calls the same public functions as the main runner."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

from gate1_preflight import core


def test_kernel_rows_normalize():
    T = core.true_kernel(core.D_PHASE1)
    assert np.allclose(T.sum(axis=2), 1.0)


def test_heldout_never_in_stream():
    rng = np.random.default_rng(9001)
    stream = core.generate_stream(rng, core.D_PHASE1, 500)
    assert all((s, a) not in core.HELDOUT for (s, a, _x) in stream)


def test_obs_map_not_lumpable():
    # next-observation class must NOT be determined by current class+action
    for d in core.D_PHASE1:
        determined = True
        for o in range(core.N_OBS):
            alias = [s for s in range(core.N_STATES) if core.obs_of(s) == o]
            nxt = {core.obs_of((s + d) % core.N_STATES) for s in alias}
            if len(nxt) != 1:
                determined = False
        assert not determined


def test_A_model_probs_and_update():
    m = core.CompositionalSlowModel(9001)
    p = m.probs(0, 0)
    assert abs(p.sum() - 1) < 1e-9
    nll0 = m.item_nll(0, 0, 1)
    for _ in range(50):
        m.sgd_step(0, 0, 1)
    assert m.item_nll(0, 0, 1) < nll0


def test_B_belief_update_and_multistep():
    m = core.BeliefPredictor(9001)
    b = np.full(core.N_STATES, 1.0 / core.N_STATES)
    p, _ = m.predict_obs(b, 0)
    assert abs(p.sum() - 1) < 1e-9
    loss = m.multistep_loss_and_update(b, [0, 1, 2], [0, 1, 2])
    assert loss > 0
    b2 = m.belief_update(b, 0, 0)
    assert abs(b2.sum() - 1) < 1e-9


def test_B_replay_deterministic_recompute():
    rng = np.random.default_rng(9001)
    stream = core.generate_stream(rng, core.D_PHASE1, 60)
    chunks = [stream[i:i + 30] for i in range(0, 60, 30)]

    def run():
        m = core.BeliefPredictor(9001)
        for ch in chunks:
            b = np.full(core.N_STATES, 1.0 / core.N_STATES)
            for t, (s, a, s2) in enumerate(ch):
                o2 = core.obs_of(s2)
                if t < 5:
                    b = m.belief_update(b, a, o2)
                    continue
                h = min(3, len(ch) - t)
                m.multistep_loss_and_update(
                    b, [ch[t + j][1] for j in range(h)],
                    [core.obs_of(ch[t + j][2]) for j in range(h)])
                b = m.belief_update(b, a, o2)
        return m.theta

    assert np.array_equal(run(), run())
