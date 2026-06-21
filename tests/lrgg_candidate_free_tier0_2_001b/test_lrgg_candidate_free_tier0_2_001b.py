"""Regression tests for the LRGG Tier 0-2 REDESIGN PRECHECK 001B harness.

Each test is designed to FAIL against the invalidated OFFICIAL_RUN_001A design
(latent copied into observation; oracle == baselines == truth fn; stub attackers;
name-only scanner; fake positive controls).
"""
import inspect
import json
import os
import tempfile

import importlib.util, pathlib
_p = pathlib.Path(__file__).resolve().parents[2] / "src" / "lrgg_candidate_free_tier0_2_001b" / "runner.py"
_spec = importlib.util.spec_from_file_location("lrgg001b_runner", _p)
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)

ALLOWED_OBS_KEYS = {"passive_vector", "coarse_bucket", "legal_action_count", "query_budget"}


def _run(**kw):
    return R.run_precheck(tempfile.mkdtemp(), persist=False, **kw)


def test_latent_not_copied_into_observation():
    rows = R.generate_rows(plant=False)
    for row in rows:
        assert set(row["observation"]) <= ALLOWED_OBS_KEYS
        assert set(row["serialized_state"]) <= (ALLOWED_OBS_KEYS | {"row_id"})
    run = _run()
    C = run["result"]["oracle_mean"]
    assert run["result"]["raw_decoder_family_max_mean"] < C - R.EPS_EQUIV
    planted = _run(plant_latent=True)
    assert planted["result"]["planted_attacker_family_max_mean"] >= C - R.EPS_EQUIV


def test_oracle_not_same_callable_as_baselines():
    o = R.budget_faithful_visible_channel_oracle
    for fn in R.BASELINES.values():
        assert fn is not o
        assert inspect.getsource(fn) != inspect.getsource(o)


def test_baselines_not_shared_public_rule_wrappers():
    run = _run()
    C = run["result"]["oracle_mean"]
    assert run["family_max"]["mean"] < C - R.EPS_EQUIV
    assert run["result"]["checks"]["distinct_baseline_pred_vectors"] > 1
    for fn in R.BASELINES.values():
        src = inspect.getsource(fn)
        for forbidden in ("evaluation_only", "target_actions", "probe_response", "g_lo"):
            assert forbidden not in src


def test_value_attackers_read_real_rows_not_stubs():
    rows = R.generate_rows(plant=False)
    fam = R.value_attacker_family(R.public_rows(rows), R._truth(rows))
    pl = R.generate_rows(plant=True)
    famp = R.value_attacker_family(R.public_rows(pl), R._truth(pl))
    assert fam["family_max_mean"] != famp["family_max_mean"]
    assert all(a["reads_real_rows"] for a in fam["attackers"])
    assert fam["family_max_mean"] < 1.0 - R.EPS_EQUIV
    assert famp["family_max_mean"] >= 1.0 - R.EPS_EQUIV


def test_positive_controls_use_real_scanner_path():
    pos = R.run_positive_controls(R.generate_rows())
    assert pos["uses_real_scanner_path"] and pos["all_planted_controls_alarm"]
    assert "scan_rows" in inspect.getsource(R.run_positive_controls)


def test_name_only_scanner_cannot_pass_value_leak():
    rows = R.generate_rows(plant=False)
    for row in rows:
        row["observation"]["aux_feature_07"] = row["evaluation_only"]["g_lo"]
    res = R.scan_rows(rows)
    assert not res["passed"]
    assert any(f["channel"] == "value_g_lo" and f["key"] == "aux_feature_07" for f in res["findings"])
    namebad = ("topology", "remap", "hidden_rule", "target", "g_lo", "membership")
    assert not any(t in "aux_feature_07" for t in namebad)


def test_decodability_gate_fires_when_latent_planted():
    run = _run(plant_latent=True)
    assert run["result"]["verdict"] == "invalid_redesign_latent_still_decodable"


def test_twin_pair_passive_indistinguishable_intervention_separable():
    tp = R.twin_pair_report(R.generate_rows())
    assert tp["passed"] and tp["passive_indistinguishable"] and tp["intervention_separable"]
    ex = tp["example"]
    assert ex["targets_differ"] and ex["probe_response_g0"] != ex["probe_response_g1"]


def test_no_stale_official_run_overwrite():
    p = R.repo_root() / "artifacts/LRGG-CANDIDATE-FREE-TIER0-2/OFFICIAL_RUN_001A/result.json"
    assert p.exists()
    assert json.loads(p.read_text(encoding="utf-8"))["verdict"] == "rejected_baseline_saturated"


def test_31_frozen_values_respected():
    fz = R.check_frozen()
    assert fz["respected"], fz["mismatches"]
    assert (R.N_SEED, R.N_CTX, R.N_ROWS, R.H_MIN_BITS, R.B) == (10, 30, 300, 12.0, 8)
    assert R.N_ENUM_LATENT >= 3000 and R.ACTION_COUNT >= 80 and R.COVERAGE <= 0.10
