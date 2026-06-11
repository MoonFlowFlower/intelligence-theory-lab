"""Baseline / ablation / perturbation execution tests and fake-pass-route
detection for PREDICTIVE-ACTION-LEARNING-CONTRACT-001 (task card 16.13).

Directional assertions use short runs and test-only seeds; the real gates are
evaluated on the full pre-declared suite. Thresholds are never derived here."""

import os

import pytest

from predictive_action_learning_contract_001 import config as cfg
from predictive_action_learning_contract_001.runner import run_episode
from predictive_action_learning_contract_001.suite import _base, compute_run_metrics
from predictive_action_learning_contract_001.validator import validate_run_dir

TS = cfg.SEEDS["test_seed_base"]


def run(tmp, run_id, **kw):
    s = _base(run_id, "test", kw.pop("seed", TS + 10), kw.pop("steps", 400),
              kw.pop("rule", "AS-CYCLE-001"), **kw)
    s["config_manifest_hash"] = "test_config_manifest_hash"
    d = os.path.join(str(tmp), run_id)
    records = run_episode(s, d)
    return compute_run_metrics(records), records, d


BASELINE_PREDICTORS = [
    ("passive", {}),
    ("action_token", {}),
    ("retrieval", {}),
    ("hardcoded", {}),
    ("oracle", {}),
    ("skeleton", {"action_input_mode": "shuffled", "shuffle_seed": 9001}),
    ("skeleton", {"theta_update_enabled": False}),
    ("skeleton", {"theta_freeze_at_t": 50}),
]


@pytest.mark.parametrize("ptype,params", BASELINE_PREDICTORS)
def test_baselines_execute_and_produce_comparable_trace_metrics(tmp_path, ptype, params):
    m, records, d = run(tmp_path, f"b_{ptype}_{len(params)}", steps=60,
                        predictor={"type": ptype, "params": params},
                        declared_retrieval_enabled=(ptype == "retrieval"))
    assert m["nll_eval_window"] is not None
    assert m["jsd_raw_eval_window"] is not None
    pres = [r for r in records if r["event_type"] == "PRE_STEP"]
    assert all("raw_pred_obs_by_action" in p for p in pres)
    assert all(len(p["raw_pred_obs_by_action"]) == cfg.N_A for p in pres)


def test_main_beats_passive_and_shuffled_in_action_sensitive_regime(tmp_path):
    main, _r, _d = run(tmp_path, "main_as")
    passive, _r, _d = run(tmp_path, "passive_as", predictor={"type": "passive", "params": {}})
    shuffled, _r, _d = run(tmp_path, "shuffled_as",
                           predictor={"type": "skeleton",
                                      "params": {"action_input_mode": "shuffled",
                                                 "shuffle_seed": 9002}})
    assert passive["nll_eval_window"] > main["nll_eval_window"] + 0.05
    assert shuffled["nll_eval_window"] > main["nll_eval_window"] + 0.05


def test_action_separation_in_as_and_collapse_in_null(tmp_path):
    as_m, _r, _d = run(tmp_path, "sep_as", steps=600)
    null_m, _r, _d = run(tmp_path, "sep_null", steps=600, rule="NULL-001",
                         seed=TS + 11)
    assert as_m["jsd_raw_eval_window"] >= cfg.THRESHOLDS["sep_min_jsd_nats"]
    assert null_m["jsd_raw_eval_window"] <= cfg.THRESHOLDS["collapse_max_jsd_nats"]
    assert null_m["jsd_raw_eval_window"] < as_m["jsd_raw_eval_window"]


def test_oracle_leak_is_flagged_as_impossible_and_main_is_not(tmp_path):
    oracle, _r, _d = run(tmp_path, "oracle", steps=200,
                         predictor={"type": "oracle", "params": {}})
    main, _r, _d = run(tmp_path, "main_floor", steps=200)
    floor = cfg.THRESHOLDS["oracle_leak_nll_floor_nats"]
    assert oracle["nll_eval_window"] < floor          # leak detector fires
    assert main["nll_eval_window"] > floor            # legitimate learner does not


def test_frozen_theta_fails_to_adapt_after_reversal(tmp_path):
    seed = TS + 12
    kw = dict(steps=1200, rule="SHIFT-REVERSAL-001", shift_t=300, seed=seed)
    adaptive, _ra, _d = run(tmp_path, "adapt", **kw)
    frozen, _rf, _d = run(tmp_path, "frozen", predictor={
        "type": "skeleton", "params": {"theta_freeze_at_t": 250}}, **kw)
    hard, _r, _d = run(tmp_path, "hard", predictor={"type": "hardcoded", "params": {}}, **kw)
    assert frozen["nll_eval_window"] > adaptive["nll_eval_window"] + 0.05
    assert hard["nll_eval_window"] > adaptive["nll_eval_window"] + 0.05
    # directional theta adaptation: mass moves onto the new rule (frozen: ~0)
    from predictive_action_learning_contract_001.gates import newrule_mass_gain
    ga = newrule_mass_gain(_ra, "SHIFT-REVERSAL-001", 300)
    gf = newrule_mass_gain(_rf, "SHIFT-REVERSAL-001", 300)
    assert ga["mean_gain"] >= cfg.THRESHOLDS["theta_newrule_mass_gain_min"]
    assert abs(gf["mean_gain"]) <= cfg.THRESHOLDS["frozen_newrule_mass_gain_max"]


def test_ablations_remove_action_and_freeze_belief_degrade(tmp_path):
    main, _r, _d = run(tmp_path, "abl_main")
    noact, _r, _d = run(tmp_path, "abl_noact", predictor={
        "type": "skeleton", "params": {"action_input_mode": "none"}})
    nobel, _r, _d = run(tmp_path, "abl_nobel", predictor={
        "type": "skeleton", "params": {"belief_update_enabled": False}})
    notheta, _r, _d = run(tmp_path, "abl_notheta", predictor={
        "type": "skeleton", "params": {"theta_update_enabled": False}})
    for abl in (noact, nobel, notheta):
        assert abl["nll_eval_window"] > main["nll_eval_window"] + 0.05
    assert noact["jsd_raw_eval_window"] == pytest.approx(0.0, abs=1e-12)


def test_obs_noise_perturbation_raises_uncertainty(tmp_path):
    low, _r, _d = run(tmp_path, "noise_low", eps_O=cfg.OBS_NOISE_LOW, seed=TS + 13)
    high, _r, _d = run(tmp_path, "noise_high", eps_O=cfg.OBS_NOISE_HIGH, seed=TS + 13)
    assert high["entropy_eval_window"] > low["entropy_eval_window"] + \
        cfg.THRESHOLDS["entropy_perturbation_min_increase_nats"]
    assert high["nll_eval_window"] > low["nll_eval_window"]


def test_ambiguous_obs_shift_raises_entropy(tmp_path):
    # matched-seed control: identical streams until the ambiguity onset
    m, _r, _d = run(tmp_path, "ambig", steps=700, rule="AMBIG-001", ambig_t=350,
                    seed=TS + 14)
    c, _r, _d = run(tmp_path, "ambig_ctl", steps=700, rule="AS-CYCLE-001",
                    seed=TS + 14)
    assert m["entropy_eval_window"] - c["entropy_eval_window"] > \
        cfg.THRESHOLDS["entropy_perturbation_min_increase_nats"]
    assert m["nll_eval_window"] > c["nll_eval_window"]


def test_trap_token_baseline_shows_spurious_separation_main_resists(tmp_path):
    seed = TS + 15
    kw = dict(steps=600, rule="TRAP-001", policy="trap", seed=seed)
    main, _r, _d = run(tmp_path, "trap_main", **kw)
    token, _r, _d = run(tmp_path, "trap_token",
                        predictor={"type": "action_token", "params": {}}, **kw)
    # the data-level spurious correlation exists and fools the token predictor
    assert token["jsd_raw_eval_window"] >= cfg.THRESHOLDS["collapse_max_jsd_nats"]
    # the main learner shows no CONFIDENT action separation (collapse gate metric)
    assert main["jsd_confident_eval_window"] <= cfg.THRESHOLDS["collapse_max_jsd_nats"]
    assert token["jsd_raw_eval_window"] > main["jsd_confident_eval_window"]


def test_rule_swap_regime_learnable(tmp_path):
    swap, _r, _d = run(tmp_path, "swap", steps=600, rule="AS-SWAP-001", seed=TS + 16)
    as_m, _r, _d = run(tmp_path, "swap_ref", steps=600, seed=TS + 16)
    assert abs(swap["nll_eval_window"] - as_m["nll_eval_window"]) <= \
        cfg.THRESHOLDS["rule_swap_nll_match_margin_nats"]


def test_audit_attestation_zero_external_access(tmp_path):
    _m, records, d = run(tmp_path, "attest", steps=60)
    posts = [r for r in records if r["event_type"] == "POST_STEP"]
    assert all(p["external_memory_access_count"] == 0 for p in posts)
    assert validate_run_dir(d)["ok"]
