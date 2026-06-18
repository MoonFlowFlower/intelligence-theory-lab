import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


REQUIRED_BASELINES = {
    "random",
    "majority",
    "constant",
    "observation_only",
    "nearest_neighbor_passive",
    "supervised_passive",
    "count_table",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "fsm_planner",
    "episodic_traversal",
    "exhaustive_legal_query",
    "greedy_uncertainty_query",
    "trace_only_replay",
    "ngram_trace_lookup",
    "full_bundle_decoder_boundary",
    "serialized_state_decoder",
    "strongest_known_classical_method",
}

REQUIRED_ABLATION_CONTROLS = {
    "remove_legal_observation_fields",
    "remove_legal_interaction_history",
    "remove_legal_query_budget",
    "inject_answer_map_positive_control",
    "inject_target_field_positive_control",
    "inject_final_score_positive_control",
    "inject_semantic_action_label_positive_control",
    "inject_full_bundle_positive_control",
    "inject_source_path_target_positive_control",
    "force_strongest_baseline_equals_visible_oracle",
    "tamper_replay_state",
    "omit_source_generator_provenance",
}

REQUIRED_LEAKAGE_POSITIVE_CONTROLS = {
    "target_label",
    "final_action_score",
    "answer_map",
    "semantic_action_label_leak",
    "full_legal_response_bundle",
    "full_legal_response_bundles",
    "source_path_target_leak",
    "fixture_name_target_leak",
}

REQUIRED_PROVENANCE_IDS = REQUIRED_BASELINES | {
    "phase2b_episode_generator",
    "visible_channel_oracle",
    "source_spec_hash_readback",
    "freeze_manifest_hash_readback",
    "leakage_scan",
    "replay_recomputation",
    "ablation_controls",
    "final_verdict_derivation",
}


def _runner():
    from phase2b_candidate_free_headroom_001a import runner

    return runner


def test_candidate_free_headroom_harness_records_no_headroom_against_full_battery(tmp_path):
    runner = _runner()

    run = runner.run_harness(output_dir=tmp_path / "run", persist_artifacts=False)
    result = run["result"]
    comparison = run["baseline_comparison"]

    assert result["verdict"] == "no_headroom_baseline_saturated"
    assert result["candidate_mechanism_run"] is False
    assert result["baseline_battery_run"] is True
    assert result["phase3_opened"] is False
    assert result["spec_hash_matches_freeze"] is True
    assert comparison["missing_baseline_ids"] == []
    assert set(comparison["baseline_ids"]) == REQUIRED_BASELINES
    assert comparison["strongest_fair_is_max_over_full_battery"] is True
    assert result["strongest_fair_baseline_macro_f1"] == comparison["strongest_fair_baseline"]["macro_f1"]
    assert comparison["strongest_fair_baseline"]["macro_f1"] >= (
        result["visible_channel_oracle_macro_f1"] - result["equivalence_band"]
    )


def test_controls_provenance_leakage_and_replay_are_fail_able(tmp_path):
    runner = _runner()

    run = runner.run_harness(output_dir=tmp_path / "run", persist_artifacts=False)

    assert run["leakage_report"]["positive_controls_passed"] is True
    assert set(run["leakage_report"]["positive_control_ids"]) >= REQUIRED_LEAKAGE_POSITIVE_CONTROLS
    assert set(run["leakage_report"]["detected_positive_control_ids"]) >= REQUIRED_LEAKAGE_POSITIVE_CONTROLS
    assert run["leakage_report"]["clean_scan_passed_after_positive_controls"] is True
    assert run["leakage_report"]["clean_scan_scanned_generated_artifacts"] is True
    assert run["leakage_report"]["illegal_leak_findings"] == []

    assert run["replay_report"]["passed"] is True
    assert run["replay_report"]["uses_hash_only_comparison"] is False
    assert run["replay_report"]["uses_stored_outputs_only"] is False
    assert run["replay_report"]["observed_input_reads"] == {
        "serialized_state": True,
        "current_observation": True,
        "legal_action_or_query_schema": True,
        "budget_state": True,
    }
    assert run["replay_report"]["tamper_negative_control_detected"] is True

    assert run["ablation_report"]["all_controls_consumed_by_final_verdict"] is True
    assert {row["control_id"] for row in run["ablation_report"]["controls"]} == REQUIRED_ABLATION_CONTROLS
    assert all(row["callable_invoked"] is True for row in run["ablation_report"]["controls"])
    assert all(row["detected_expected_failure"] is True for row in run["ablation_report"]["controls"])

    provenance = run["computed_evidence_provenance"]
    assert runner.verify_provenance(provenance)["passed"] is True
    assert {row["producer_id"] for row in provenance["records"]} >= REQUIRED_PROVENANCE_IDS
    assert all(row["consumed_by_final_verdict"] is True for row in provenance["records"])

    missing = runner.run_harness(
        output_dir=tmp_path / "missing",
        persist_artifacts=False,
        disabled_baselines=("graph_lookup",),
    )
    assert missing["result"]["verdict"] == "invalid_evidence_path"
    assert "missing_required_baseline:graph_lookup" in missing["failure_manifest"]["blocking_reasons"]

    leaked = runner.run_harness(
        output_dir=tmp_path / "leak",
        persist_artifacts=False,
        disable_leakage_positive_control="answer_map",
    )
    assert leaked["result"]["verdict"] == "invalid_evidence_path"
    assert "positive_control_not_detected:answer_map" in leaked["failure_manifest"]["blocking_reasons"]

    replay_failed = runner.run_harness(
        output_dir=tmp_path / "replay",
        persist_artifacts=False,
        tamper_replay=True,
    )
    assert replay_failed["result"]["verdict"] == "invalid_evidence_path"
    assert "replay_tamper_negative_control_detected" in replay_failed["failure_manifest"]["blocking_reasons"]

    missing_provenance = runner.run_harness(
        output_dir=tmp_path / "provenance",
        persist_artifacts=False,
        omit_source_generator_provenance=True,
    )
    assert missing_provenance["result"]["verdict"] == "invalid_evidence_path"
    assert (
        "missing_required_provenance:phase2b_episode_generator"
        in missing_provenance["failure_manifest"]["blocking_reasons"]
    )


def test_persisted_artifacts_parse_and_preserve_claim_ceiling(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    campaign = tmp_path / "campaign.json"

    run = runner.run_harness(output_dir=out, campaign_artifact_path=campaign, persist_artifacts=True)

    required = {
        "result.json",
        "trace.jsonl",
        "baseline_comparison.json",
        "ablation_report.json",
        "replay_report.json",
        "leakage_report.json",
        "computed_evidence_provenance.json",
        "failure_manifest.json",
        "claim_ceiling.txt",
    }
    assert required <= {path.name for path in out.iterdir()}

    for name in required - {"trace.jsonl", "claim_ceiling.txt"}:
        json.loads((out / name).read_text(encoding="utf-8"))

    trace_lines = (out / "trace.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(trace_lines) == run["result"]["episode_count"]
    parsed_trace = [json.loads(line) for line in trace_lines]
    assert all(row["candidate_decision"] is None for row in parsed_trace)
    assert all("target_final_action" not in row["candidate_visible"] for row in parsed_trace)
    assert all("target_score_by_action" not in row["candidate_visible"] for row in parsed_trace)
    assert all("answer_map" not in row["candidate_visible"] for row in parsed_trace)

    claim = (out / "claim_ceiling.txt").read_text(encoding="utf-8")
    assert "candidate-free baseline-first headroom evidence only" in claim
    assert "does not prove mechanism validity" in claim
    assert "EGO readiness" in claim

    campaign_payload = json.loads(campaign.read_text(encoding="utf-8"))
    assert campaign_payload["summary"]["verdict"] == "no_headroom_baseline_saturated"
    assert campaign_payload["summary"]["candidate_mechanism_run"] is False
