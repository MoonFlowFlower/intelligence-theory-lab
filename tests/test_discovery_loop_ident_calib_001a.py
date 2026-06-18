"""Tests for DISCOVERY-LOOP-IDENT-CALIB-001A.

Validity/plumbing tests + fail-able leakage probe. These do NOT assert the scientific outcome
(e.g. they do not require the loop to separate latent_necessary); they assert the harness is valid:
determinism, causality (no future leak), label-blind interfaces, that the leakage probe is reachable,
that the separation band comes from PREREG (no post-hoc threshold), and that the produced evidence
replays. Artifact-based checks read $DLIC_ARTIFACTS (default: the repo artifacts dir).
"""
import os
import sys
import json
import inspect
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/src")
try:
    from discovery_loop_ident_calib_001a import probe as P
except Exception:  # when run from a flattened /tmp copy
    import importlib
    P = importlib.import_module("discovery_loop_ident_calib_001a.probe")

ART = os.environ.get("DLIC_ARTIFACTS", "artifacts/DISCOVERY-LOOP-IDENT-CALIB-001A")


def _load(name):
    with open(os.path.join(ART, name)) as f:
        return json.load(f)


# ---- generator / determinism ----
def test_gen_sequence_deterministic():
    a = P.gen_sequence("latent_necessary", 200, 3)
    b = P.gen_sequence("latent_necessary", 200, 3)
    assert np.array_equal(a, b)
    assert not np.array_equal(a, P.gen_sequence("latent_necessary", 200, 4))


def test_run_cell_deterministic():
    r1, _, _ = P.run_cell("negative_control", 0)
    r2, _, _ = P.run_cell("negative_control", 0)
    assert r1["gap"] == r2["gap"] and r1["hmm_logloss"] == r2["hmm_logloss"]


# ---- causality: changing a FUTURE observation must not change earlier per-step losses ----
def test_causal_no_future_dependence():
    pi = np.array([0.5, 0.5])
    A = np.array([[0.9, 0.1], [0.1, 0.9]])
    E = np.array([[0.8, 0.2], [0.2, 0.8]])
    obs = np.array([0, 1, 0, 0, 1, 1, 0, 1, 0, 1])
    _, losses_a = P.hmm_losses(obs, pi, A, E, offset=0, leak=False)
    obs2 = obs.copy(); obs2[7] = 1 - obs2[7]   # flip a future position
    _, losses_b = P.hmm_losses(obs2, pi, A, E, offset=0, leak=False)
    # losses at t < 7 must be identical (no future leakage); at/after 7 may differ
    assert losses_a[:7] == losses_b[:7]
    assert losses_a[7:] != losses_b[7:]


# ---- leakage probe must be reachable: oracle leak flips a no-structure world to separation ----
def test_leak_causes_false_separation():
    clean, _, _ = P.run_cell("negative_control", 0, leak=False)
    leaked, _, _ = P.run_cell("negative_control", 0, leak=True)
    assert clean["separates"] is False
    assert leaked["separates"] is True and leaked["gap"] > 0.5


# ---- anti-tuning: separation decision is driven by PREREG eps, not a hidden constant ----
def test_separation_band_is_prereg():
    r, _, _ = P.run_cell("latent_necessary", 0)
    assert r["separates"] == (r["gap"] >= P.PREREG["eps_nats"])
    assert r["equivalent"] == (abs(r["gap"]) < P.PREREG["eps_nats"])


# ---- label-blind interfaces: fit/score functions never receive world identity or true params ----
def test_label_blind_signatures():
    for fn in (P.select_and_fit_hmm, P.hmm_losses, P.count_table_losses, P.fit_hmm):
        params = set(inspect.signature(fn).parameters)
        assert "regime" not in params and "world_params" not in params
        assert not (params & {"e1_s1", "e1_s0", "p_stay", "p1_given0", "p1_given1"})


# ---- verdict gating is fail-able both ways (constructed inputs) ----
def test_verdict_gates_failable():
    cmin = P.PREREG["consistency_min"]
    def rows(sep, equ, n=10):
        out = []
        for i in range(n):
            s = i < sep; e = (not s) and (i < sep + equ)
            out.append({"separates": s, "equivalent": e, "sig_pos": s, "sig_neg": False})
        return out
    # positive control fails to separate -> blind
    by = {"latent_necessary": rows(10, 0), "latent_redundant": rows(0, 10),
          "positive_control": rows(0, 10), "negative_control": rows(0, 10)}
    assert P.compute_verdict(by)[0] == "check_underpowered_loop_blind"
    # negative control separates -> false separation
    by["positive_control"] = rows(10, 0); by["negative_control"] = rows(10, 0)
    assert P.compute_verdict(by)[0] == "check_invalid_false_separation"
    # clean calibration
    by["negative_control"] = rows(0, 10)
    assert P.compute_verdict(by)[0].startswith("loop_calibrated")


# ---- artifact-backed validity checks (require the full run to have produced artifacts) ----
@pytest.mark.skipif(not os.path.exists(os.path.join(ART, "result.json")), reason="no artifacts yet")
def test_artifacts_specificity_and_replay():
    res = _load("result.json"); rep = _load("replay_report.json")
    # specificity invariant: a no-structure world must never be reported as separable
    assert res["verdict_detail"]["negative_control"]["world_verdict"] != "separates"
    # evidence must replay from trace and per-step spot-check must reconcile
    assert rep["match"] is True
    assert rep["per_step_spot_check_all_match"] is True
    assert res["secret_scan"]["clean"] is True
    assert res["verdict"] not in ("check_invalid_false_separation", "BLOCK_secret_present")
