import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_RESEARCH = ROOT / "scripts" / "research"
if str(SCRIPTS_RESEARCH) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_RESEARCH))


REQUIRED_ARTIFACTS = {
    "sketch_registry.json",
    "author_claims.json",
    "independent_static_kill_scan.json",
    "dependency_analysis.json",
    "oracle_as_baseline_report.json",
    "micro_probe_results.json",
    "baseline_independence_report.json",
    "fitted_legal_channel_learner_report.json",
    "promoted_full_harness_candidates.json",
    "rejected_sketches.json",
    "final_report.md",
}


def test_static_scanner_derives_results_instead_of_echoing_author_claims():
    from batch_env_headroom_scout_002b import (
        STATIC_KILL_CRITERIA,
        make_direct_legal_compute_sketch,
        make_low_signal_surface_sketch,
        run_independent_static_kill_scan,
    )

    false_claims = {criterion: False for criterion in STATIC_KILL_CRITERIA}
    true_claims = {criterion: True for criterion in STATIC_KILL_CRITERIA}

    direct = make_direct_legal_compute_sketch(author_claims=false_claims)
    low_signal = make_low_signal_surface_sketch(author_claims=true_claims)
    scan = run_independent_static_kill_scan([direct, low_signal], run_id="pytest-static")
    by_id = {row["sketch_id"]: row for row in scan["results"]}

    assert by_id["direct_legal_channel_compute"]["per_sketch_verdict"] == "reject_direct_decode"
    assert "target_deterministic_from_le_budget_visible_channels" in by_id["direct_legal_channel_compute"]["derived_kill_reasons"]
    assert by_id["direct_legal_channel_compute"]["author_claims_used_as_evidence"] is False
    assert by_id["low_signal_underpowered_surface"]["static_verdict"] == "survived_static_kill"
    assert by_id["low_signal_underpowered_surface"]["derived_kill_reasons"] == []
    assert by_id["low_signal_underpowered_surface"]["author_claims_used_as_evidence"] is False


def test_run_writes_required_artifacts_and_forbidden_outputs_are_absent(tmp_path):
    from batch_env_headroom_scout_002b import ALLOWED_FINAL_VERDICTS, run_batch_scout

    result = run_batch_scout(out_dir=tmp_path, run_id="pytest-002b-run", repo_root=ROOT)

    assert result["final_verdict"] in ALLOWED_FINAL_VERDICTS
    assert result["current_layer"] == "engineering-governance / Phase-0 repaired environment portfolio scouting"
    assert result["mainline_integration_status"] == "none"
    assert result["enabled_status"] == "no runtime/mainline/admission/bridge path enabled"
    assert result["candidate_implementation_authorized"] is False
    assert result["route_tournament_authorized"] is False
    assert {path.name for path in tmp_path.iterdir() if path.is_file()} == REQUIRED_ARTIFACTS

    for artifact_name in REQUIRED_ARTIFACTS - {"final_report.md"}:
        json.loads((tmp_path / artifact_name).read_text(encoding="utf-8"))

    micro_probe = json.loads((tmp_path / "micro_probe_results.json").read_text(encoding="utf-8"))
    micro_probe_text = json.dumps(micro_probe)
    assert "headroom_confirmed" not in micro_probe_text
    assert "candidate_authorized" not in micro_probe_text
    assert "route_tournament_authorized" not in micro_probe_text


def test_oracle_as_baseline_symmetry_rejects_direct_legal_compute(tmp_path):
    from batch_env_headroom_scout_002b import run_batch_scout

    run_batch_scout(out_dir=tmp_path, run_id="pytest-oracle-baseline", repo_root=ROOT)
    rejected = json.loads((tmp_path / "rejected_sketches.json").read_text(encoding="utf-8"))
    oracle_report = json.loads((tmp_path / "oracle_as_baseline_report.json").read_text(encoding="utf-8"))

    direct_rejection = next(row for row in rejected["rejected"] if row["sketch_id"] == "direct_legal_channel_compute")
    direct_oracle = next(row for row in oracle_report["results"] if row["sketch_id"] == "direct_legal_channel_compute")

    assert direct_rejection["per_sketch_verdict"] == "reject_direct_decode"
    assert direct_oracle["visible_oracle_budget_faithful"] is True
    assert direct_oracle["oracle_registered_as_fair_baseline"] is True
    assert direct_oracle["oracle_score"] == direct_oracle["oracle_as_fair_baseline_score"]
    assert direct_oracle["symmetry_blocks_promotion"] is True


def test_complete_micro_probe_battery_is_consumed_for_static_survivors(tmp_path):
    from batch_env_headroom_scout_002b import (
        FULL_GRAPH_CACHE_FAMILY,
        MANDATORY_BASELINE_PRODUCERS,
        PASSIVE_DECODER_FAMILY,
        run_batch_scout,
    )

    run_batch_scout(out_dir=tmp_path, run_id="pytest-complete-battery", repo_root=ROOT)
    micro_probe = json.loads((tmp_path / "micro_probe_results.json").read_text(encoding="utf-8"))

    assert micro_probe["results"]
    for row in micro_probe["results"]:
        producers = {baseline["producer_function"] for baseline in row["baseline_rows"]}
        consumed = {baseline["producer_function"] for baseline in row["baseline_rows"] if baseline["consumed_by_final_verdict"]}
        assert set(MANDATORY_BASELINE_PRODUCERS) <= producers
        assert set(MANDATORY_BASELINE_PRODUCERS) <= consumed
        assert set(FULL_GRAPH_CACHE_FAMILY) <= producers
        assert set(PASSIVE_DECODER_FAMILY) <= producers


def test_missing_required_rows_and_unconsumed_rows_block_callable_final_verdict():
    from batch_env_headroom_scout_002b import (
        final_verdict_context_for_test,
        produce_callable_final_verdict,
    )

    missing_exhaustive = final_verdict_context_for_test(remove_baselines=["exhaustive_legal_query"])
    assert produce_callable_final_verdict(missing_exhaustive)["final_verdict"] == "blocked_baseline_battery_incomplete"

    missing_fitted = final_verdict_context_for_test(remove_baselines=["fitted_legal_channel_learner"])
    assert produce_callable_final_verdict(missing_fitted)["final_verdict"] == "blocked_compute_baseline_missing"

    missing_graph = final_verdict_context_for_test(remove_baselines=["count_table"])
    assert produce_callable_final_verdict(missing_graph)["final_verdict"] == "blocked_baseline_battery_incomplete"

    unconsumed = final_verdict_context_for_test(unconsumed_baselines=["exhaustive_legal_query"])
    assert produce_callable_final_verdict(unconsumed)["final_verdict"] == "blocked_baseline_battery_incomplete"


def test_baseline_aliasing_collapses_independence_and_blocks_promotion():
    from batch_env_headroom_scout_002b import (
        final_verdict_context_for_test,
        produce_callable_final_verdict,
    )

    context = final_verdict_context_for_test(alias_positive_rows=True)
    verdict = produce_callable_final_verdict(context)

    assert verdict["final_verdict"] == "blocked_baseline_aliasing_invalidates_promotion"
    assert verdict["baseline_independence_report"]["aliases_detected"] is True
    assert verdict["baseline_independence_report"]["promotion_blocking_aliasing"] is True
    assert "aliased_weak_family" in verdict["baseline_independence_report"]["collapsed_independence_families"]


def test_lookup_failure_on_disjoint_split_does_not_count_as_headroom():
    from batch_env_headroom_scout_002b import make_lookup_split_compute_sketch, micro_probe_sketch

    probe = micro_probe_sketch(make_lookup_split_compute_sketch(), run_id="pytest-lookup-split")

    assert probe["per_sketch_verdict"] == "reject_no_headroom_likely"
    assert probe["lookup_memorization_score"] < probe["visible_oracle_score"] - probe["equivalence_band"]
    assert probe["exhaustive_legal_query_score"] >= probe["visible_oracle_score"] - probe["equivalence_band"]
    assert probe["fitted_legal_channel_learner_score"] >= probe["visible_oracle_score"] - probe["equivalence_band"]
    assert probe["lookup_failure_supports_promotion"] is False


def test_graph_cache_family_saturation_gets_graph_cache_verdict():
    from batch_env_headroom_scout_002b import FULL_GRAPH_CACHE_FAMILY, make_graph_cache_surface_sketch, micro_probe_sketch

    probe = micro_probe_sketch(make_graph_cache_surface_sketch(), run_id="pytest-graph-cache")
    graph_rows = [row for row in probe["baseline_rows"] if row["producer_function"] in FULL_GRAPH_CACHE_FAMILY]

    assert probe["per_sketch_verdict"] == "reject_graph_cache_saturated"
    assert {row["producer_function"] for row in graph_rows} == set(FULL_GRAPH_CACHE_FAMILY)
    assert probe["graph_cache_family_max_score"] >= probe["visible_oracle_score"] - probe["equivalence_band"]


def test_underpowered_surface_gets_underpowered_verdict_before_generic_floor_failure():
    from batch_env_headroom_scout_002b import ORACLE_FLOOR, make_low_signal_surface_sketch, micro_probe_sketch

    probe = micro_probe_sketch(make_low_signal_surface_sketch(), run_id="pytest-underpowered")

    assert probe["visible_oracle_score"] < ORACLE_FLOOR
    assert probe["per_sketch_verdict"] == "reject_underpowered_surface"


def test_answer_key_oracle_cannot_support_promotion():
    from batch_env_headroom_scout_002b import make_answer_key_oracle_sketch, micro_probe_sketch

    probe = micro_probe_sketch(make_answer_key_oracle_sketch(), run_id="pytest-answer-key")

    assert probe["per_sketch_verdict"] == "reject_oracle_not_budget_faithful"
    assert probe["answer_key_diagnostic_oracle_score"] >= 0.99
    assert probe["visible_oracle_budget_faithful"] is False
    assert probe["answer_key_oracle_may_support_promotion"] is False


def test_predict_all_metric_degeneracy_gate_fires():
    from batch_env_headroom_scout_002b import make_metric_degenerate_sketch, micro_probe_sketch

    probe = micro_probe_sketch(make_metric_degenerate_sketch(), run_id="pytest-metric-degenerate")

    assert probe["per_sketch_verdict"] == "reject_metric_degenerate"
    assert probe["degenerate_family_max_score"] >= probe["degenerate_rejection_floor"]
    assert probe["per_class_floor_passed"] is False


def test_passive_value_leakage_gate_fires_with_full_passive_family():
    from batch_env_headroom_scout_002b import PASSIVE_DECODER_FAMILY, make_passive_value_leak_sketch, micro_probe_sketch

    probe = micro_probe_sketch(make_passive_value_leak_sketch(), run_id="pytest-passive-leak")
    passive_producers = {
        row["producer_function"]
        for row in probe["baseline_rows"]
        if row["baseline_family"] == "passive_decoder"
    }

    assert probe["per_sketch_verdict"] == "reject_passive_decodable"
    assert set(PASSIVE_DECODER_FAMILY) <= passive_producers
    assert probe["passive_family_max_score"] >= probe["passive_rejection_floor"]
    assert probe["value_level_leakage_scan"]["positive_control_detected"] is True


def test_fitted_legal_channel_learner_records_real_fit_evidence(tmp_path):
    from batch_env_headroom_scout_002b import run_batch_scout

    run_batch_scout(out_dir=tmp_path, run_id="pytest-fitted-report", repo_root=ROOT)
    fitted_report = json.loads((tmp_path / "fitted_legal_channel_learner_report.json").read_text(encoding="utf-8"))

    assert fitted_report["results"]
    for row in fitted_report["results"]:
        assert row["producer_function"] == "fitted_legal_channel_learner"
        assert row["fit_performed"] is True
        assert row["fit_evidence"]["train_rows_consumed"] > 0
        assert row["fit_evidence"]["ml_library_used"] == "stdlib_rule_search"
        assert row["fit_evidence"]["anti_stub_guard"]["constant_prediction_stub"] is False
