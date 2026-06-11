import json

from cmbc_companion.demos.free_input_live_lab_003_reexecute import (
    ALLOWED_VERDICTS,
    run_free_input_live_lab_003_reexecute,
)


REQUIRED_ARTIFACTS = {
    "FREE_INPUT_LIVE_LAB_003_REEXECUTE_STATUS.md",
    "freeze_manifest.json",
    "source_free_input_transcript.jsonl",
    "source_outcome_coding_ledger.jsonl",
    "causal_probe_pack_003B_used.json",
    "causal_probe_results.json",
    "baseline_comparison_report.json",
    "supporting_prior_deletion_report.json",
    "outcome_perturbation_report.json",
    "renderer_isolation_report.md",
    "behavior_only_replay.json",
    "developer_trace.jsonl",
    "free_input_live_lab_003_reexecute_result.json",
}


def test_free_input_live_lab_003_reexecute_passes_minimum_causal_probe_gates(tmp_path):
    result = run_free_input_live_lab_003_reexecute(tmp_path)

    assert result["suite_id"] == "CMBC-COMPANION-FREE-INPUT-LIVE-LAB-003-REEXECUTE"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "free_input_causal_probe_bounded_pass"
    assert result["stop_conditions"] == []
    assert result["minimum_gates_satisfied"] is True

    metrics = result["metrics"]
    assert metrics["free_input_turn_count"] == 20
    assert metrics["outcome_coding_ledger_count"] == 20
    assert metrics["causal_probe_case_count"] >= 8
    assert metrics["causal_probe_pass_rate"] >= 0.85
    assert metrics["rag_causal_probe_match_rate"] < 0.5
    assert metrics["strong_heuristic_causal_probe_match_rate"] < 0.5
    assert metrics["expanded_contextual_heuristic_causal_probe_match_rate"] < 0.5
    assert metrics["behavior_only_replay_match_rate"] == 1.0
    assert metrics["renderer_action_change_rate"] == 0.0
    assert metrics["supporting_prior_deletion_effect"] is True
    assert metrics["outcome_perturbation_effect"] is True


def test_free_input_live_lab_003_reexecute_uses_frozen_sources_and_boundaries(tmp_path):
    result = run_free_input_live_lab_003_reexecute(tmp_path)

    assert result["source_inputs"]["transcript_path"].endswith("user_supplied_free_input_2026-06-07.jsonl")
    assert result["source_inputs"]["outcome_ledger_path"].endswith("outcome_coding_ledger.jsonl")
    assert result["source_inputs"]["probe_pack_path"].endswith("causal_probe_pack_003B.json")
    assert result["freeze_integrity"]["code_hashes_unchanged_after_execution"] is True
    assert result["probe_pack_integrity"]["post_result_probe_selection"] is False
    assert result["probe_pack_integrity"]["synthetic_user_turn_counted_as_free_input"] is False
    assert result["probe_pack_integrity"]["all_probe_anchors_valid"] is True

    assert result["execution_authorized"] == "bounded_reexecute_only"
    assert result["implementation_authorized"] is False
    assert result["selector_patched"] is False
    assert result["thresholds_changed"] is False
    assert result["rag_baseline_weakened"] is False
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["llm_action_selection"] is False


def test_free_input_live_lab_003_reexecute_probe_results_preserve_pack_coverage(tmp_path):
    result = run_free_input_live_lab_003_reexecute(tmp_path)
    results = result["causal_probe_results"]
    probe_types = {case["probe_type"] for case in results["cases"]}

    assert results["probe_count"] == result["metrics"]["causal_probe_case_count"]
    assert results["candidate_passed_probe_count"] == results["probe_count"]
    assert results["all_required_probe_types_covered"] is True
    assert {
        "same_text_different_causal_history",
        "same_history_different_feedback_outcome",
        "supporting_prior_deletion",
        "predicted_outcome_perturbation",
        "feedback_admission_single_contradiction",
        "feedback_admission_repeated_feedback",
        "later_correction_context_narrowing",
        "renderer_adversarial_isolation",
    }.issubset(probe_types)
    assert all(case["anchor_turn_valid"] for case in results["cases"])
    assert all(not case["new_user_turn_counted_as_free_input"] for case in results["cases"])


def test_free_input_live_lab_003_reexecute_replay_renderer_and_artifacts(tmp_path):
    result = run_free_input_live_lab_003_reexecute(tmp_path)

    assert result["behavior_only_replay"]["passed"] is True
    assert result["behavior_only_replay"]["match_rate"] == 1.0
    assert result["behavior_only_replay"]["forbidden_fields_used"] == []
    assert result["renderer_isolation"]["passed"] is True
    assert result["renderer_isolation"]["adversarial_renderer_action_change_rate"] == 0.0
    assert result["renderer_isolation"]["renderer_used_for_action_selection"] is False

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    with (tmp_path / "free_input_live_lab_003_reexecute_result.json").open("r", encoding="utf-8") as fh:
        verdict = json.load(fh)
    assert verdict["verdict"] == result["verdict"]
    assert verdict["metrics"]["causal_probe_case_count"] == result["metrics"]["causal_probe_case_count"]
    assert verdict["authorization_boundary"]["ego_migration"] == "no_go"
