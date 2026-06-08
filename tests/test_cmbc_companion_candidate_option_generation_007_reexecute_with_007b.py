import inspect
import json

from cmbc_companion.demos.candidate_option_generation_007_reexecute_with_007b import (
    ALLOWED_VERDICTS,
    run_candidate_option_generation_007_reexecute_with_007b,
)


REQUIRED_ARTIFACTS = {
    "CANDIDATE_OPTION_GENERATION_007_REEXECUTE_WITH_007B_STATUS.md",
    "freeze_manifest.json",
    "candidate_option_proposals.jsonl",
    "option_admission_decisions.jsonl",
    "admitted_candidate_options.json",
    "option_lineage_traces.jsonl",
    "parametric_selector_input_trace.jsonl",
    "prediction_before_action_trace.jsonl",
    "action_distribution_trace.jsonl",
    "causal_probe_results.json",
    "pending_counterevidence_records.jsonl",
    "feedback_admission_state_trace.jsonl",
    "generated_option_feedback_update_ledger.jsonl",
    "admission_filtered_effect_vector_trace.jsonl",
    "selector_visible_effect_vector_contract_report.json",
    "supporting_prior_deletion_report.json",
    "outcome_perturbation_report.json",
    "behavior_only_replay.json",
    "admission_aware_replay.json",
    "baseline_comparison_report.json",
    "renderer_isolation_report.md",
    "semantic_leak_scan.json",
    "evidence_preservation_report.json",
    "candidate_option_generation_007_reexecute_with_007b_result.json",
}


def test_007_reexecute_with_007b_passes_causal_probe_suite(tmp_path):
    result = run_candidate_option_generation_007_reexecute_with_007b(
        tmp_path, generated_option_count=24
    )

    assert result["suite_id"] == (
        "CMBC-COMPANION-CANDIDATE-OPTION-GENERATION-007-REEXECUTE-WITH-007B"
    )
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "candidate_option_generation_007_reexecute_with_007b_bounded_pass"
    assert result["execution_scope"] == "bounded_reexecution_only"
    assert result["minimum_gates_satisfied"] is True
    assert result["stop_conditions"] == []

    metrics = result["metrics"]
    assert metrics["generated_option_count"] == 24
    assert metrics["admitted_option_count"] == 24
    assert metrics["causal_probe_case_count"] == 9
    assert metrics["causal_probe_pass_rate"] == 1.0
    assert metrics["generator_selected_action"] is False
    assert metrics["generator_ranked_final_actions"] is False
    assert metrics["selector_receives_only_admitted_options"] is True
    assert metrics["feedback_admission_single_contradiction_passed"] is True
    assert metrics["selected_option_changed_due_to_pending"] is False
    assert metrics["repeated_feedback_admission_status"] == "admitted_context_counterevidence"
    assert metrics["repeated_feedback_changes_distribution"] is True


def test_007_reexecute_with_007b_keeps_pending_hidden_and_replay_passes(tmp_path):
    result = run_candidate_option_generation_007_reexecute_with_007b(
        tmp_path, generated_option_count=24
    )

    metrics = result["metrics"]
    assert metrics["pending_counterevidence_record_count"] >= 1
    assert metrics["selector_visible_effect_update_allowed"] is False
    assert metrics["selector_visible_predicted_effect_vector_delta"] == 0.0
    assert metrics["uncertainty_delta"] > 0.0
    assert metrics["confidence_delta"] < 0.0
    assert metrics["behavior_only_replay_match_rate"] == 1.0
    assert metrics["admission_aware_replay_match_rate"] == 1.0
    assert result["behavior_only_replay"]["passed"] is True
    assert result["admission_aware_replay"]["passed"] is True
    assert result["admission_aware_replay"]["forbidden_fields_used"] == []

    records = [
        json.loads(line)
        for line in (tmp_path / "admission_filtered_effect_vector_trace.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    pending = next(
        record
        for record in records
        if record["feedback_admission_status"] == "pending_counterevidence"
    )
    assert pending["effect_vector_visibility_status"] == "base_only_pending_hidden"
    assert pending["selector_visible_predicted_effect_vector"] == pending["base_effect_vector"]


def test_007_reexecute_with_007b_baselines_renderer_and_leaks_remain_clean(tmp_path):
    result = run_candidate_option_generation_007_reexecute_with_007b(
        tmp_path, generated_option_count=24
    )

    metrics = result["metrics"]
    assert metrics["rag_causal_probe_match_rate"] < 0.5
    assert metrics["strong_heuristic_causal_probe_match_rate"] < 0.5
    assert metrics["expanded_action_nearest_neighbor_match_rate"] < 0.5
    assert metrics["generator_baseline_action_match_rate"] < 0.5
    assert metrics["baselines_receive_same_anonymous_options"] is True
    assert metrics["baselines_weakened_or_incomparable"] is False
    assert metrics["renderer_action_change_rate"] == 0.0
    assert metrics["semantic_label_visible_to_selector"] is False
    assert metrics["natural_language_description_visible_to_selector"] is False

    assert result["renderer_isolation"]["renderer_used_for_action_selection"] is False
    assert result["renderer_isolation"]["llm_action_selection"] is False
    assert result["semantic_leak_scan"]["passed"] is True


def test_007_reexecute_with_007b_preserves_failed_007_as_negative_evidence(tmp_path):
    result = run_candidate_option_generation_007_reexecute_with_007b(
        tmp_path, generated_option_count=24
    )

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    preservation = result["evidence_preservation"]
    assert preservation["source_failed_007_execute_verdict"] == (
        "candidate_option_generation_execute_causal_probe_failed"
    )
    assert preservation["source_failed_007_execute_stop_conditions"] == [
        "feedback_admission_single_contradiction_failed"
    ]
    assert preservation["preserve_failed_007_execute_as"] == (
        "failed generated-option execution evidence"
    )
    assert preservation["record_this_as_new_reexecution_result"] is True
    assert preservation["rewrite_failed_007_execute_as_pass"] is False
    assert preservation["rewrite_prior_evidence_as_reexecution_evidence"] is False

    assert result["selector_patched"] is False
    assert result["thresholds_changed"] is False
    assert result["rag_baseline_weakened"] is False
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["llm_action_selection"] is False
    assert result["claim_after_reexecute"] == (
        "bounded 007 generated CandidateOption re-execution with 007B admission "
        "ordering evidence only; not real companion readiness"
    )


def test_007_reexecute_with_007b_does_not_call_failed_007_execute_or_fixed_table():
    import cmbc_companion.demos.candidate_option_generation_007_reexecute_with_007b as module

    source = inspect.getsource(module)
    forbidden_snippets = [
        "ACTION_HANDLES = 20",
        "range(20)",
        "range(24)",
        "if generated_option_count == 20",
        "if generated_option_count == 24",
        "fixed_generated_options",
        "run_candidate_option_generation_007_execute",
        "semantic_action_label",
        "natural_language_description",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in source
