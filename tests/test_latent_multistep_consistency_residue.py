"""Smoke checks on placeholder data (seed 9001) — no candidate-vs-control
comparative metrics."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

from latent_multistep_consistency_residue import core


def test_kernel_and_heldout():
    T = core.true_kernel()
    assert np.allclose(T.sum(axis=2), 1.0)
    rng = np.random.default_rng(9001)
    stream = core.generate_stream(rng, 400)
    assert all((s, a) not in core.HELDOUT for (s, a, _x) in stream)


def test_obs_map_not_lumpable():
    for d in core.D_MOTIF:
        determined = True
        for o in range(core.NO):
            alias = [s for s in range(core.N) if core.obs_of(s) == o]
            if len({core.obs_of((s + d) % core.N) for s in alias}) != 1:
                determined = False
        assert not determined


def test_belief_model_math():
    m = core.BeliefModel(9001)
    b = np.full(core.N, 1.0 / core.N)
    p, _ = m.predict_obs(b, 0)
    assert abs(p.sum() - 1) < 1e-9
    l0 = m.sgd_step_obs(b, 0, 2)
    for _ in range(40):
        last = m.sgd_step_obs(b, 0, 2)
    assert last < l0
    loss = m.multistep_loss_and_update(b, [0, 1, 2, 0], [1, 2, 3, 0])
    assert loss > 0
    assert abs(m.predict_h4(b, [0, 1, 2, 0]).sum() - 1) < 1e-9


def test_learned_obs_model_math():
    m = core.BeliefModelLearnedObs(9001)
    b = np.full(core.N, 1.0 / core.N)
    p, _ = m.predict_obs(b, 0)
    assert abs(p.sum() - 1) < 1e-9
    l0 = m.sgd_step_obs(b, 0, 2)
    for _ in range(60):
        last = m.sgd_step_obs(b, 0, 2)
    assert last < l0


def test_window_models_math():
    h = [(0, 1), (2, 0), (1, 2)]
    o2 = core.Order2WindowModel(9001)
    assert abs(o2.predict(h).sum() - 1) < 1e-9
    assert abs(o2.predict_h4(h, [0, 1, 2, 0]).sum() - 1) < 1e-9
    it = core.InterpWindowModel(9001)
    assert abs(it.predict(h).sum() - 1) < 1e-9
    assert abs(it.predict_h4(h, [0, 1, 2, 0]).sum() - 1) < 1e-9
    l0 = it.sgd(h, 3)
    for _ in range(60):
        last = it.sgd(h, 3)
    assert last < l0


def test_stores_and_h4_chaining():
    rng = np.random.default_rng(9001)
    stream = core.generate_stream(rng, 200)
    st = core.SeqStores(stream)
    hist = [(core.obs_of(s), a) for (s, a, _x) in stream[:12]]
    for fn in (st.hidden_state_cache, st.prefix_cache, st.sequence_lookup,
               st.episodic_retrieval, st.count_table, st.graph_lookup,
               lambda h: st.knn(h, 5), st.compressed_map()):
        p = fn(hist)
        assert abs(p.sum() - 1) < 1e-9
    cond = st.chain_conditional(laplace=True)
    q = core.store_h4(st.count_table, cond, hist, [0, 1, 2, 0])
    assert abs(q.sum() - 1) < 1e-9


def test_replay_deterministic_recompute():
    rng = np.random.default_rng(9001)
    stream = core.generate_stream(rng, 80)
    chunks = [stream[i:i + 40] for i in (0, 40)]

    def run():
        m = core.BeliefModel(9001)
        for ch in chunks:
            b = np.full(core.N, 1.0 / core.N)
            for t in range(len(ch)):
                s, a, s2 = ch[t]
                o2 = core.obs_of(s2)
                if t < core.BURN_IN:
                    b = m.belief_update(b, a, o2)
                    continue
                h = min(core.KDEPTH, len(ch) - t)
                m.multistep_loss_and_update(
                    b, [ch[t + j][1] for j in range(h)],
                    [core.obs_of(ch[t + j][2]) for j in range(h)])
                b = m.belief_update(b, a, o2)
        return m.theta

    assert np.array_equal(run(), run())
