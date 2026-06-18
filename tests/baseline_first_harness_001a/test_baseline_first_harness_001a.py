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
    "predict_all_sweep",
    "observation_only",
    "nearest_neighbor_passive",
    "exhaustive_legal_query",
    "greedy_uncertainty_query_under_budget",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "trace_only_replay",
    "ngram_trace_lookup",
    "full_bundle_decoder",
    "serialized_state_decoder",
    "strongest_known_classical_method",
}

REQUIRED_ABLATION_CONTROLS = {
    "remove_legal_observation_fields",
    "remove_legal_query_budget",
    "force_strongest_baseline_equals_visible_oracle",
    "inject_leakage_positive_control",
    "tamper_replay_state",
    "omit_source_generator_provenance",
}

REQUIRED_PROVENANCE_IDS = (
    REQUIRED_BASELINES
    | {
        "visible_channel_oracle",
        "candidate_free_episode_generator",
        "frozen_spec_hash_readback",
        "leakage_scan",
        "replay_recomputation",
        "ablation_controls",
        "final_verdict_derivation",
    }
)


def _runner():
    from baseline_first_harness_001a import runner

    return runner


def test_candidate_free_harness_measures_no_headroom_against_full_battery(tmp_path):
    runner = _runner()

    run = runner.run_harness(output_dir=tmp_path / "run", persist_artifacts=False)
    result = run["result"]
    comparison = run["baseline_comparison"]

    assert result["verdict"] == "no_headroom_baseline_saturated"
    assert result["candidate_mechanism_run"] is False
    assert result["baseline_battery_run"] is True
    assert result["phase3_opened"] is False
    assert result["spec_hash_matches_freeze"] is True
    assert result["visible_channel_oracle_macro_f1"] >= 0.90
    assert result["strongest_fair_baseline_macro_f1"] == comparison["strongest_fair_baseline"]["macro_f1"]
    assert comparison["strongest_fair_baseline"]["macro_f1"] >= (
        result["visible_channel_oracle_macro_f1"] - result["equivalence_band"]
    )
    assert set(comparison["baseline_ids"]) == REQUIRED_BASELINES
    assert comparison["strongest_fair_baseline"]["baseline_id"] in REQUIRED_BASELINES
    assert comparison["strongest_fair_is_max_over_full_battery"] is True


def test_controls_provenance_leakage_and_replay_are_fail_able(tmp_path):
    runner = _runner()

    run = runner.run_harness(output_dir=tmp_path / "run", persist_artifacts=False)

    assert run["leakage_report"]["positive_controls_passed"] is True
    assert run["leakage_report"]["clean_scan_passed_after_positive_controls"] is True
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
    assert run["leakage_report"]["clean_scan_scanned_generated_artifacts"] is True
    assert run["leakage_report"]["illegal_leak_findings"] == []
    assert set(run["leakage_report"]["positive_control_ids"]) >= {
        "filename_label_leak",
        "action_name_label_leak",
        "metadata_answer_map",
        "source_pin_path_label_leak",
    }

    provenance = run["computed_evidence_provenance"]
    assert runner.verify_provenance(provenance)["passed"] is True
    assert {row["producer_id"] for row in provenance["records"]} >= REQUIRED_PROVENANCE_IDS
    assert all(row["consumed_by_final_verdict"] is True for row in provenance["records"])

    missing = runner.run_harness(
        output_dir=tmp_path / "missing",
        persist_artifacts=False,
        disabled_baselines=("graph_lookup",),
    )
    assert missing["result"]["verdict"] == "blocked_missing_required_baseline"
    assert "missing_required_baseline:graph_lookup" in missing["failure_manifest"]["blocking_reasons"]

    leaked = runner.run_harness(
        output_dir=tmp_path / "leak",
        persist_artifacts=False,
        disable_leakage_positive_control="filename_label_leak",
    )
    assert leaked["result"]["verdict"] == "blocked_leakage_positive_control_failure"
    assert "positive_control_not_detected:filename_label_leak" in leaked["failure_manifest"]["blocking_reasons"]

    replay_failed = runner.run_harness(
        output_dir=tmp_path / "replay",
        persist_artifacts=False,
        tamper_replay=True,
    )
    assert replay_failed["result"]["verdict"] == "blocked_replay_recompute_failure"
    assert "replay_tamper_negative_control_failed" in replay_failed["failure_manifest"]["blocking_reasons"]

    missing_provenance = runner.run_harness(
        output_dir=tmp_path / "provenance",
        persist_artifacts=False,
        omit_source_generator_provenance=True,
    )
    assert missing_provenance["result"]["verdict"] == "blocked_provenance_failure"
    assert (
        "missing_required_provenance:candidate_free_episode_generator"
        in missing_provenance["failure_manifest"]["blocking_reasons"]
    )


def test_persisted_artifacts_parse_and_preserve_claim_ceiling(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"

    run = runner.run_harness(output_dir=out, persist_artifacts=True)

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
    assert all(json.loads(line)["candidate_decision"] is None for line in trace_lines)

    claim = (out / "claim_ceiling.txt").read_text(encoding="utf-8")
    assert "no baseline headroom" in claim
    assert "no mechanism validity" in claim
    assert "no EGO readiness" in claim
