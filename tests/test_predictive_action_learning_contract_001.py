"""Unit tests for PREDICTIVE-ACTION-LEARNING-CONTRACT-001 (task card 16.13).

Tests assert on trace evidence (records, hashes, receipts, chronology, replay),
not only on behavior (stop condition 21)."""

import copy
import json
import math
import os

import pytest

from predictive_action_learning_contract_001 import config as cfg
from predictive_action_learning_contract_001 import metrics as M
from predictive_action_learning_contract_001.runner import run_episode
from predictive_action_learning_contract_001.skeleton import FrozenSkeleton
from predictive_action_learning_contract_001.suite import (
    _base, compare_record_streams, compute_run_metrics)
from predictive_action_learning_contract_001.trace import load_trace
from predictive_action_learning_contract_001.validator import (
    replay_skeleton_run, split_records, validate_attestation, validate_chronology,
    validate_hashes, validate_replay_guard, validate_run_dir, validate_schema)

TEST_HASH = "test_config_manifest_hash"


def spec(run_id, tmp, **kw):
    s = _base(run_id, "test", kw.pop("seed", cfg.SEEDS["test_seed_base"]),
              kw.pop("steps", 60), kw.pop("rule", "AS-CYCLE-001"), **kw)
    s["config_manifest_hash"] = TEST_HASH
    return s, os.path.join(str(tmp), run_id)


def run(tmp, run_id, **kw):
    s, d = spec(run_id, tmp, **kw)
    records = run_episode(s, d)
    return s, d, records


# ----------------------------------------------------------------- skeleton math

def make_handcrafted_skeleton():
    sk = FrozenSkeleton(3, 3, 3, alpha=1.0, eta=1.0, log_eps=1e-12)
    sk.b = [1.0, 0.0, 0.0]
    sk.C_T[0][0] = [8.0, 1.0, 1.0]
    sk.C_O = [[8.0, 1.0, 1.0], [1.0, 8.0, 1.0], [1.0, 1.0, 8.0]]
    return sk


def test_prediction_matches_hand_computation():
    sk = make_handcrafted_skeleton()
    bhat, pobs = sk.predict_all_actions()
    assert bhat[0] == pytest.approx([0.8, 0.1, 0.1], abs=1e-12)
    assert pobs[0] == pytest.approx([0.66, 0.17, 0.17], abs=1e-12)
    assert sum(pobs[0]) == pytest.approx(1.0, abs=1e-12)


def test_belief_update_matches_hand_computation():
    sk = make_handcrafted_skeleton()
    upd = sk.update(0, 1, t=0)
    # xi ∝ [0.8*0.1, 0.1*0.8, 0.1*0.1] = [.08,.08,.01], z=.17
    assert upd["xi"][0] == pytest.approx([8/17, 8/17, 1/17], abs=1e-12)
    assert upd["belief_post"] == pytest.approx([8/17, 8/17, 1/17], abs=1e-12)
    assert sum(sum(r) for r in upd["xi"]) == pytest.approx(1.0, abs=1e-12)


def test_pseudocount_update_matches_hand_computation():
    sk = make_handcrafted_skeleton()
    sk.update(0, 1, t=0)
    assert sk.C_T[0][0] == pytest.approx([8 + 8/17, 1 + 8/17, 1 + 1/17], abs=1e-12)
    assert sk.C_O[0][1] == pytest.approx(1 + 8/17, abs=1e-12)
    assert sk.C_O[1][1] == pytest.approx(8 + 8/17, abs=1e-12)


def test_freeze_flags_block_updates():
    sk = FrozenSkeleton(3, 3, 3, 1.0, 1.0, 1e-12, theta_update_enabled=False)
    before = copy.deepcopy(sk.C_T)
    sk.update(0, 1, t=0)
    assert sk.C_T == before
    sk2 = FrozenSkeleton(3, 3, 3, 1.0, 1.0, 1e-12, belief_update_enabled=False)
    b_before = list(sk2.b)
    sk2.update(0, 1, t=0)
    assert sk2.b == b_before


# ------------------------------------------------------- trace protocol evidence

def test_trace_schema_chronology_hashes_and_commitments(tmp_path):
    _s, d, records = run(tmp_path, "core_like", steps=50)
    assert validate_schema(records) == []
    assert validate_chronology(records) == []
    assert validate_hashes(records) == []
    rep = validate_run_dir(d)
    assert rep["ok"], rep
    # commitment strictly precedes reveal, per step, from raw trace records
    _m, pres, posts, _ = split_records(records)
    by_t = {p["t"]: p for p in posts}
    for pre in pres:
        rcpt = pre["pre_commit_receipt"]
        assert rcpt["commit_monotonic_ns"] < by_t[pre["t"]]["obs_reveal_monotonic_ns"]
        assert rcpt["payload_sha256"] == pre["pre_step_hash"]
    # commit log on disk matches receipts
    log = [json.loads(x) for x in open(os.path.join(d, "commits.log.jsonl"))]
    assert [e["payload_sha256"] for e in log] == [p["pre_step_hash"] for p in pres]


def test_forced_replay_step_triggers_protocol_blocked(tmp_path):
    _s, d, records = run(tmp_path, "forced_replay", steps=40, force_replay_at=10)
    guard = validate_replay_guard(records)
    assert guard["protocol_verdict"] == "protocol_blocked"
    assert guard["reason"] == "replay_contamination"
    assert not validate_run_dir(d)["ok"]


def test_missing_raw_predictions_rejected(tmp_path):
    _s, d, _r = run(tmp_path, "drop_raw", steps=30,
                    drop_fields=["raw_pred_obs_by_action", "raw_pred_belief_by_action"])
    rep = validate_run_dir(d)
    assert any("raw_pred_obs_by_action" in e for e in rep["schema_errors"])
    assert not rep["ok"]


def test_missing_uncertainty_rejected(tmp_path):
    _s, d, _r = run(tmp_path, "drop_unc", steps=30, drop_fields=["uncertainty_pre"])
    rep = validate_run_dir(d)
    assert any("uncertainty_pre" in e for e in rep["schema_errors"])
    assert not rep["ok"]


def test_tampered_trace_caught_by_hash_chain(tmp_path):
    _s, d, _r = run(tmp_path, "tamper", steps=30)
    path = os.path.join(d, "trace.jsonl")
    lines = open(path).read().splitlines()
    rec = json.loads(lines[6])
    assert rec["event_type"] == "POST_STEP"
    rec["nll_error"] = 0.0  # post-hoc beautification attempt
    lines[6] = json.dumps(rec, sort_keys=True, separators=(",", ":"))
    open(path, "w").write("\n".join(lines) + "\n")
    rep = validate_run_dir(d)
    assert rep["hash_errors"]
    assert not rep["ok"]


def test_disabled_precommit_flagged(tmp_path):
    _s, d, _r = run(tmp_path, "no_commit", steps=30, commit="disabled")
    rep = validate_run_dir(d)
    assert rep["commitment_errors"]


def test_retrieval_replacement_with_false_flag_caught(tmp_path):
    s, d = spec("retr_lie", tmp_path, steps=30)
    s["predictor"] = {"type": "retrieval_replaced", "params": {}}
    s["declared_retrieval_enabled"] = False  # the lie
    records = run_episode(s, d)
    errs = validate_attestation(records)
    assert any("retrieval" in e for e in errs)
    assert not validate_run_dir(d)["ok"]


# ----------------------------------------------------------------- replay evidence

def test_full_trace_replay_reconstructs_everything(tmp_path):
    _s, _d, records = run(tmp_path, "replay_ok", steps=80)
    rep = replay_skeleton_run(records)
    assert rep["applicable"] and rep["passed"], rep
    assert rep["max_abs_diff"] <= cfg.THRESHOLDS["replay_abs_tolerance"]


def test_replay_detects_corrupted_state(tmp_path):
    _s, _d, records = run(tmp_path, "replay_bad", steps=40)
    bad = copy.deepcopy(records)
    posts = [r for r in bad if r["event_type"] == "POST_STEP"]
    posts[20]["belief_post"] = [0.5, 0.25, 0.25]  # state not derivable from trace
    rep = replay_skeleton_run(bad)
    assert rep["passed"] is False


def test_memdel_reconstruction_equals_uninterrupted_twin(tmp_path):
    seed = cfg.SEEDS["test_seed_base"] + 1
    _s1, _d1, twin = run(tmp_path, "twin", steps=240, seed=seed)
    _s2, _d2, flushed = run(tmp_path, "flush", steps=240, seed=seed,
                            memdel_at=120, memdel_mode="reconstruct")
    cmpres = compare_record_streams(flushed, twin)
    assert cmpres["identical"], cmpres


def test_coldstart_duplicate_runs_identical(tmp_path):
    seed = cfg.SEEDS["test_seed_base"] + 2
    _s1, _d1, ra = run(tmp_path, "dup_a", steps=120, seed=seed)
    _s2, _d2, rb = run(tmp_path, "dup_b", steps=120, seed=seed)
    cmpres = compare_record_streams(ra, rb)
    assert cmpres["identical"], cmpres


def test_memdel_reset_degrades_prediction(tmp_path):
    seed = cfg.SEEDS["test_seed_base"] + 3
    _s, _d, records = run(tmp_path, "memreset", steps=700, seed=seed,
                          memdel_at=500, memdel_mode="reset")
    m = compute_run_metrics(records)
    a = m["memdel_analysis"]
    assert a["nll_after_window"] - a["nll_before_window"] > \
        cfg.THRESHOLDS["ablation_necessity_min_degradation_nats"]
