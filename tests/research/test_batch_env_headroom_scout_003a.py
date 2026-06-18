import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_RESEARCH = ROOT / "scripts" / "research"
if str(SCRIPTS_RESEARCH) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_RESEARCH))


REQUIRED_ARTIFACTS = {
    "sketch_registry.json",
    "lineage_source_readback.json",
    "independent_static_kill_scan.json",
    "dependency_analysis.json",
    "oracle_as_baseline_report.json",
    "oracle_vs_planner_separation_report.json",
    "planner_family_report.json",
    "micro_probe_results.json",
    "baseline_independence_report.json",
    "fitted_legal_channel_learner_report.json",
    "hard_failure_family_report.json",
    "cross_batch_stop_report.json",
    "failability_probe_report.json",
    "promoted_full_harness_candidates.json",
    "rejected_sketches.json",
    "final_verdict.json",
    "final_report.md",
}


def test_run_writes_required_artifacts_and_consumes_cross_batch_stop_rules(tmp_path):
    from batch_env_headroom_scout_003a import ALLOWED_FINAL_VERDICTS, run_batch_scout

    result = run_batch_scout(out_dir=tmp_path, run_id="pytest-003a-run", repo_root=ROOT)

    assert result["final_verdict"] in ALLOWED_FINAL_VERDICTS
    assert result["current_layer"] == "engineering-governance / Phase-0 constrained environment portfolio scouting"
    assert result["mainline_integration_status"] == "none"
    assert result["enabled_status"] == "no runtime/mainline/admission/bridge path enabled"
    assert result["candidate_implementation_authorized"] is False
    assert result["route_tournament_authorized"] is False
    assert {path.name for path in tmp_path.iterdir() if path.is_file()} == REQUIRED_ARTIFACTS

    for artifact_name in REQUIRED_ARTIFACTS - {"final_report.md"}:
        json.loads((tmp_path / artifact_name).read_text(encoding="utf-8"))

    cross_batch = json.loads((tmp_path / "cross_batch_stop_report.json").read_text(encoding="utf-8"))
    final_verdict = json.loads((tmp_path / "final_verdict.json").read_text(encoding="utf-8"))
    assert cross_batch["cross_batch_stop_rules_consumed_by_final_verdict"] is True
    assert final_verdict["cross_batch_stop_report_consumed"] is True
    assert cross_batch["004a_blocked_pending_route_level_review"] is True


def test_complete_battery_includes_a10_active_planner_rows_and_rows_are_consumed(tmp_path):
    from batch_env_headroom_scout_003a import MANDATORY_BASELINE_PRODUCERS, PLANNER_FAMILY, run_batch_scout

    run_batch_scout(out_dir=tmp_path, run_id="pytest-003a-battery", repo_root=ROOT)
    micro_probe = json.loads((tmp_path / "micro_probe_results.json").read_text(encoding="utf-8"))
    planner_report = json.loads((tmp_path / "planner_family_report.json").read_text(encoding="utf-8"))

    assert micro_probe["results"]
    for row in micro_probe["results"]:
        producers = {baseline["producer_function"] for baseline in row["baseline_rows"]}
        consumed = {baseline["producer_function"] for baseline in row["baseline_rows"] if baseline["consumed_by_final_verdict"]}
        assert set(MANDATORY_BASELINE_PRODUCERS) <= producers
        assert set(MANDATORY_BASELINE_PRODUCERS) <= consumed
        assert set(PLANNER_FAMILY) <= producers
        for baseline in row["baseline_rows"]:
            if baseline["producer_function"] in PLANNER_FAMILY:
                assert baseline["planner_budget_trace"]
                assert baseline["planner_strategy_signature"]
                assert baseline["baseline_family"] == "active_planner"

    for row in planner_report["results"]:
        assert row["consumed_by_final_verdict"] is True
        assert "active_planner_saturation" in row["explicit_named_risk"]


def test_planner_family_max_in_oracle_band_rejects_sketch():
    from batch_env_headroom_scout_003a import make_active_planner_saturated_sketch, micro_probe_sketch

    probe = micro_probe_sketch(make_active_planner_saturated_sketch(), run_id="pytest-003a-planner")

    assert probe["per_sketch_verdict"] == "reject_active_planner_saturated"
    assert probe["hard_failure_family_code"] == "A10_ACTIVE_PLANNER_SATURATION"
    assert probe["planner_family_max"] >= probe["visible_oracle_score"] - probe["equivalence_band"]
    assert probe["oracle_vs_planner_separation_status"] == "falsified_by_planner_results"


def test_missing_planner_rows_or_oracle_vs_planner_argument_blocks_promotion():
    from batch_env_headroom_scout_003a import (
        final_verdict_context_for_test,
        make_separation_missing_sketch,
        micro_probe_sketch,
        produce_callable_final_verdict,
    )

    missing_planner = final_verdict_context_for_test(remove_baselines=["strongest_active_planner_for_task_type"])
    assert produce_callable_final_verdict(missing_planner)["final_verdict"] == "blocked_planner_family_missing_or_stubbed"

    probe = micro_probe_sketch(make_separation_missing_sketch(), run_id="pytest-003a-separation-missing")
    assert probe["per_sketch_verdict"] == "blocked_missing_oracle_vs_planner_separation_argument"
    assert probe["hard_failure_family_code"] == "A10_ACTIVE_PLANNER_SATURATION"


def test_all_hard_family_rejection_batch_triggers_grammar_stop_verdict():
    from batch_env_headroom_scout_003a import run_batch_scout

    result = run_batch_scout(out_dir=None, run_id="pytest-003a-hard-stop", repo_root=ROOT)

    assert result["final_verdict"] in {
        "blocked_no_valid_environment_design_grammar",
        "all_rejected_static_or_microprobe_with_hard_failure_stop",
    }
    assert result["cross_batch_stop_report"]["grammar_stop_triggered"] is True
    assert result["cross_batch_stop_report"]["004a_blocked_pending_route_level_review"] is True


def test_required_failability_probes_flip_or_block_as_expected():
    from batch_env_headroom_scout_003a import REQUIRED_FAILABILITY_PROBES, run_failability_probes

    report = run_failability_probes(run_id="pytest-003a-failability")
    by_id = {row["probe_id"]: row for row in report["results"]}

    assert set(REQUIRED_FAILABILITY_PROBES) <= set(by_id)
    assert by_id["lowering_all_fair_baselines_below_oracle_flips_from_saturation"]["observed_flip"] is True
    assert by_id["planner_family_max_into_oracle_band_rejects"]["observed_verdict"] == "reject_active_planner_saturated"
    assert by_id["removing_planner_rows_blocks_promotion"]["observed_final_verdict"] == "blocked_planner_family_missing_or_stubbed"
    assert by_id["missing_oracle_vs_planner_separation_argument_blocks_promotion"]["observed_verdict"] == "blocked_missing_oracle_vs_planner_separation_argument"
    assert by_id["answer_key_oracle_cannot_support_promotion"]["observed_verdict"] == "reject_oracle_not_budget_faithful"
    assert by_id["direct_legal_channel_compute_rejects"]["observed_verdict"] == "reject_direct_decode"
    assert by_id["fitted_learner_reaching_oracle_band_rejects"]["observed_verdict"] == "reject_no_headroom_likely"
    assert by_id["graph_cache_reaching_oracle_band_rejects"]["observed_verdict"] == "reject_graph_cache_saturated"
    assert by_id["passive_leak_rejects"]["observed_verdict"] == "reject_passive_decodable"
    assert by_id["degenerate_predictor_rejects"]["observed_verdict"] == "reject_metric_degenerate"
    assert by_id["all_rejected_hard_family_batch_triggers_grammar_stop"]["observed_final_verdict"] == "blocked_no_valid_environment_design_grammar"


def test_no_forbidden_candidate_or_runtime_authorization_strings_outside_claim_context(tmp_path):
    from batch_env_headroom_scout_003a import run_batch_scout

    run_batch_scout(out_dir=tmp_path, run_id="pytest-003a-forbidden-scan", repo_root=ROOT)
    combined = "\n".join(path.read_text(encoding="utf-8") for path in tmp_path.iterdir() if path.is_file())

    assert "headroom_confirmed" not in combined
    assert "candidate_authorized" not in combined
    assert "runtime_mainline_authorized" not in combined
    assert "full_harness_executed: true" not in combined
