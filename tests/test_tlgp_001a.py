"""TLGP-001A tests: correctness + FAIL-ABILITY probes (the gate must swing both ways)."""
from __future__ import annotations

import json

import numpy as np
import pytest

from src.tlgp_001a import preregistration as P
from src.tlgp_001a import harness as H
from src.tlgp_001a.ideal_observer import predict_episode
from src.tlgp_001a.leakage import (clean_channels, detect, planted_channels,
                                    positive_control_report, targets)
from src.tlgp_001a.metrics import balanced_accuracy
from src.tlgp_001a.world import (Episode, Rule, enumerate_rules, features_xa,
                                  make_dataset, make_shuffle_dataset, rule_index)

FLOOR, DELTA = P.FLOOR, P.DELTA


def test_prereg_sha_deterministic():
    assert P.prereg_sha256() == P.prereg_sha256()
    assert len(P.prereg_sha256()) == 64


def test_rule_enumeration_complete_and_indexable():
    rules = enumerate_rules()
    assert len(rules) == P.K ** (P.D + 1) == 625
    for i in (0, 1, 7, 123, 624):
        assert rule_index(rules[i]) == i


def test_heldout_values_disjoint_from_train():
    assert set(P.TRAIN_VALUES).isdisjoint(P.HELDOUT_VALUES)


def test_balanced_accuracy_predict_all_is_floor():
    y = np.tile(np.arange(P.K), 40)
    const = np.zeros_like(y)
    assert abs(balanced_accuracy(y, const) - FLOOR) < 1e-9


def test_ideal_recovers_identifiable_rule_exactly():
    ds = make_dataset(30, seed=P.SEED_REAL)
    scores = [balanced_accuracy(ep.query_e, predict_episode(ep)[0]) for ep in ds]
    assert np.mean(scores) >= FLOOR + 2 * DELTA


def test_ideal_never_sees_heldout_effects():
    ds = make_dataset(5, seed=P.SEED_REAL)
    ep = ds[0]
    p1, _ = predict_episode(ep)
    ep2 = Episode(ep.episode_id, ep.rule_id, ep.rule, ep.adapt_x, ep.adapt_a, ep.adapt_e,
                  ep.query_x, ep.query_a, np.zeros_like(ep.query_e))
    p2, _ = predict_episode(ep2)
    assert np.array_equal(p1, p2)


def test_single_step_clean_at_floor_but_ruleid_leak_jumps():
    from src.tlgp_001a.baselines import single_step_decoder
    ds = make_dataset(60, seed=P.SEED_REAL)
    out = single_step_decoder(ds, seed=P.SEED_BASELINE_FIT)
    assert out["clean"] <= FLOOR + DELTA, f"latent appears single-step decodable: {out}"
    assert out["leaked_rule"] >= FLOOR + 2 * DELTA, f"K1 control not capable: {out}"


def test_leakage_controls_caught_clean_not_flagged_renamed_caught():
    rep = positive_control_report(make_dataset(P.N_EPISODES, seed=P.SEED_LEAK))
    assert rep["all_planted_caught"], rep["planted_missed"]
    assert rep["no_clean_false_flag"], rep["clean_false_flags"]
    assert rep["renamed_leak_caught"]
    assert rep["detector_valid"]


def test_clean_channel_alone_is_not_flagged():
    ds = make_dataset(P.N_EPISODES, seed=P.SEED_LEAK)
    tgt = targets(ds)
    rep = detect(clean_channels(ds), tgt)
    assert not any(r["flagged"] for r in rep.values())


def _m(headroom_real, maxfair, ss_clean, ideal, shuf_head, leak_valid=True, ss_leaked=0.9):
    return {
        "real": {"headroom": headroom_real, "max_fair_baseline": maxfair, "ideal_mean": ideal},
        "shuffle": {"headroom": shuf_head},
        "single_step": {"clean": ss_clean, "leaked_rule": ss_leaked},
        "leakage": {"detector_valid": leak_valid},
    }


def test_verdict_pass_reachable():
    m = _m(0.7, FLOOR + 0.02, FLOOR, 0.95, 0.0)
    assert H.compute_verdict(m, replay_exact=True)["verdict"] == P.VERDICT_PASS


def test_verdict_weak_when_baseline_saturates():
    m = _m(0.05, 0.9, FLOOR, 0.95, 0.0)
    assert H.compute_verdict(m, replay_exact=True)["verdict"] == P.VERDICT_WEAK


def test_verdict_invalid_when_leak_uncaught():
    m = _m(0.7, FLOOR, FLOOR, 0.95, 0.0, leak_valid=False)
    assert H.compute_verdict(m, replay_exact=True)["verdict"] == P.VERDICT_INVALID


def test_verdict_invalid_when_decoder_not_capable():
    m = _m(0.7, FLOOR, FLOOR, 0.95, 0.0, ss_leaked=FLOOR)
    assert H.compute_verdict(m, replay_exact=True)["verdict"] == P.VERDICT_INVALID


def test_verdict_weak_when_replay_fails():
    m = _m(0.7, FLOOR, FLOOR, 0.95, 0.0)
    assert H.compute_verdict(m, replay_exact=False)["verdict"] == P.VERDICT_WEAK


def _leaky_heldout_dataset(n, seed):
    base = make_dataset(n, seed=seed)
    out = []
    rng = np.random.default_rng(seed + 99)
    for ep in base:
        qx = rng.choice(np.array(P.TRAIN_VALUES), size=(P.N_QUERY, P.D)).astype(int)
        qa = rng.integers(0, P.ACTION_CARD, size=P.N_QUERY).astype(int)
        qe = np.array([ep.rule.effect(tuple(x), int(a)) for x, a in zip(qx, qa)], dtype=int)
        out.append(Episode(ep.episode_id, ep.rule_id, ep.rule, ep.adapt_x, ep.adapt_a,
                           ep.adapt_e, qx, qa, qe))
    return out


def test_baseline_saturation_world_does_not_pass():
    ds = _leaky_heldout_dataset(40, seed=P.SEED_REAL)
    ev = H.evaluate(ds, seed=P.SEED_BASELINE_FIT)
    assert ev["max_fair_baseline"] > FLOOR + DELTA, ev["fair_baselines"]


def test_shuffle_structure_collapses_ideal_headroom():
    sh = make_shuffle_dataset(40, seed=P.SEED_SHUFFLE)
    ev = H.evaluate(sh, seed=P.SEED_BASELINE_FIT)
    assert ev["ideal_mean"] <= FLOOR + DELTA, ev["ideal_mean"]
    assert ev["headroom"] <= DELTA, ev["headroom"]


def test_replay_detects_corrupted_trace(tmp_path):
    ds = make_dataset(15, seed=P.SEED_REAL)
    real = H.evaluate(ds, seed=P.SEED_BASELINE_FIT)
    p = tmp_path / "trace.jsonl"
    H.write_trace(p, ds, real)
    m = {"real": real}
    assert H.replay_from_trace(p, m)["replay_exact"]

    lines = p.read_text().splitlines()
    row = json.loads(lines[0]); row["ideal_pred"] = [(v + 1) % P.K for v in row["ideal_pred"]]
    lines[0] = json.dumps(row); p.write_text("\n".join(lines) + "\n")
    assert not H.replay_from_trace(p, m)["replay_exact"]
