"""R1 baseline-immunity repair tests. Verify FAILURE paths, not only happy paths."""
import importlib.util, inspect, json, pathlib, tempfile

_root = pathlib.Path(__file__).resolve().parents[2]
_p = _root / "src" / "lrgg_candidate_free_tier0_2_001b_r1" / "runner_r1.py"
_spec = importlib.util.spec_from_file_location("lrgg001b_r1_runner", _p)
R1 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R1)
B = R1.B
EPS = R1.EPS


def _run():
    return R1.run_r1(tempfile.mkdtemp(), persist=False)


def test_active_interventional_baseline_equal_access_measured():
    out = _run()
    a = out["active"]
    assert a["mean_score"] == out["result"]["oracle_mean"]   # computed, equal-access
    assert a["max_budget_used"] <= B.B                        # within legal probe budget


def test_active_interventional_baseline_not_oracle_callable():
    assert R1.active_interventional_baseline is not B.budget_faithful_visible_channel_oracle
    assert "budget_faithful_visible_channel_oracle" not in inspect.getsource(R1.active_interventional_baseline)


def test_active_interventional_baseline_forbidden_access_scan():
    fa = _run()["active"]["forbidden_access_scan"]
    assert fa["evaluation_only_read"] is False
    assert fa["target_actions_read"] is False
    assert fa["oracle_callable_called"] is False
    assert fa["direct_truth_map_read"] is False
    assert fa["uses_legal_probe_interface"] is True


def test_active_saturation_blocks_headroom_claim():
    res = _run()["result"]
    assert res["verdict"] == "invalid_001b_equal_access_active_baseline_saturates"
    assert res["active_minus_oracle_gap"] < EPS
    assert res["stop_condition_triggered"]


def test_transitive_call_graph_detects_rule_target_reachability():
    tr = _run()["transitive"]
    dp = next(r for r in tr["baselines"] if r["baseline"] == "DP")
    assert "rule_target" in dp["reaches_public_answer_core"]          # transitive scan sees it
    assert "rule_target" not in inspect.getsource(B.DP)               # direct-source scan would MISS it


def test_existing_wrapper_baselines_are_not_counted_independent():
    tr = _run()["transitive"]
    assert tr["any_reaches_public_answer_core"] is True               # not independent of the public answer core


def test_baseline_independence_requires_transitive_clean_graph():
    _, names = R1.reachable_symbols(B.DP, B)
    assert {"_union", "_twin", "rule_target"} <= names                # helper chain is traversed


def test_attacker_family_detects_collapsed_single_implementation():
    af = _run()["attacker"]
    assert af["collapsed_single_attacker"] is True
    assert af["distinct_code_paths"] == 1
    assert af["r4_powered_family_claim_supported"] is False


def test_attacker_transform_parameter_not_cosmetic():
    # in 001B the transform IS cosmetic; the repair must DETECT that.
    af = _run()["attacker"]
    assert af["transform_parameter_cosmetic"] is True


def test_positive_controls_fail_when_scan_rows_disabled():
    pc = _run()["positive_control"]
    assert pc["scanner_disabled_alarm_count"] < pc["normal_positive_controls_alarm_count"]
    assert pc["scanner_disabled_alarm_count"] == 0


def test_positive_controls_fail_when_value_decoder_stubbed():
    pc = _run()["positive_control"]
    assert pc["value_decoder_disabled_alarm_count"] < pc["normal_positive_controls_alarm_count"]


def test_name_only_scanner_cannot_pass_value_leak():
    rows = B.generate_rows(plant=False)
    for row in rows:
        row["observation"]["aux_feature_07"] = row["evaluation_only"]["g_lo"]
    assert R1.name_only_scanner(rows)["passed"] is True     # name-only MISSES it
    assert B.scan_rows(rows)["passed"] is False             # real value-level CATCHES it


def test_no_generator_tuning_after_active_baseline_result():
    res = _run()["result"]
    assert res["generator_tuned_after_stop"] is False
    # frozen generator constants are unchanged from 001B
    assert (B.N_ROWS, B.H_MIN_BITS, B.ACTION_COUNT, B.B) == (300, 12.0, 96, 8)


def test_official_run_001a_untouched():
    p = B.repo_root() / "artifacts/LRGG-CANDIDATE-FREE-TIER0-2/OFFICIAL_RUN_001A/result.json"
    assert json.loads(p.read_text(encoding="utf-8"))["verdict"] == "rejected_baseline_saturated"


def test_001b_original_artifacts_untouched():
    p = B.repo_root() / "artifacts/LRGG-CANDIDATE-FREE-TIER0-2/REDESIGN_PRECHECK_001B/precheck_result.json"
    assert json.loads(p.read_text(encoding="utf-8"))["verdict"] == "redesign_precheck_ready_for_independent_reaudit"


def test_claim_ceiling_blocks_headroom_and_official_rerun():
    res = _run()["result"]
    cc = res["claim_ceiling"]
    assert "candidate-free headroom" in cc and "official Tier 0-2 result" in cc
    forbidden = {"pass", "ready", "integrated", "live", "mechanism-valid", "EGO-ready",
                 "admissible_for_candidate_preflight", "001C-authorized"}
    assert res["verdict"] not in forbidden
