import inspect
import json

from cmbc_companion.demos.generated_option_feedback_admission_007b_execute import (
    ALLOWED_VERDICTS,
    run_generated_option_feedback_admission_007b_execute,
)


REQUIRED_ARTIFACTS = {
    "GENERATED_OPTION_FEEDBACK_ADMISSION_007B_EXECUTE_STATUS.md",
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
    "generated_option_feedback_admission_007b_execute_result.json",
}


FORBIDDEN_SELECTOR_TOKENS = [
    "generator_visible_description",
    "natural_language_description",
    "semantic_action_label",
    "public_action_name",
    "action_family_name",
    "rag_text",
    "renderer_text",
    "rendered_text",
    "llm_output",
    "oracle_effect",
    "evaluator_metric",
    "baseline_output",
]


def test_007b_execute_runs_generated_option_gates_with_admission_filter(tmp_path):
    result = run_generated_option_feedback_admission_007b_execute(
        tmp_path, generated_option_count=24
    )

    assert result["suite_id"] == (
        "CMBC-COMPANION-GENERATED-OPTION-FEEDBACK-ADMISSION-007B-EXECUTE"
    )
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "generated_option_feedback_admission_007b_execute_bounded_pass"
    assert result["execution_scope"] == "bounded_execution_only"
    assert result["minimum_gates_satisfied"] is True
    assert result["stop_conditions"] == []

    metrics = result["metrics"]
    assert metrics["generated_option_count"] == 24
    assert metrics["admitted_option_count"] >= 20
    assert metrics["generator_selected_action"] is False
    assert metrics["semantic_label_visible_to_selector"] is False
    assert metrics["natural_language_description_visible_to_selector"] is False
    assert metrics["pending_counterevidence_record_count"] >= 1
    assert metrics["selector_visible_effect_update_allowed"] is False
    assert metrics["selector_visible_predicted_effect_vector_delta"] == 0.0
    assert metrics["uncertainty_delta"] > 0.0
    assert metrics["confidence_delta"] < 0.0
    assert metrics["selected_option_changed_due_to_pending"] is False
    assert metrics["feedback_admission_single_contradiction_passed"] is True
    assert metrics["repeated_feedback_admission_status"] == "admitted_context_counterevidence"
    assert metrics["repeated_feedback_changes_distribution"] is True
    assert metrics["causal_probe_pass_rate"] == 1.0


def test_007b_execute_replay_renderer_and_baselines_are_intact(tmp_path):
    result = run_generated_option_feedback_admission_007b_execute(
        tmp_path, generated_option_count=24
    )

    metrics = result["metrics"]
    assert metrics["behavior_only_replay_match_rate"] == 1.0
    assert metrics["admission_aware_replay_match_rate"] == 1.0
    assert metrics["renderer_action_change_rate"] == 0.0
    assert metrics["rag_causal_probe_match_rate"] < 0.5
    assert metrics["strong_heuristic_causal_probe_match_rate"] < 0.5
    assert metrics["expanded_action_nearest_neighbor_match_rate"] < 0.5
    assert metrics["generator_baseline_action_match_rate"] < 0.5
    assert metrics["baselines_receive_same_anonymous_options"] is True
    assert metrics["baselines_weakened_or_incomparable"] is False

    replay = result["behavior_only_replay"]
    assert replay["passed"] is True
    assert replay["forbidden_fields_used"] == []
    admission_replay = result["admission_aware_replay"]
    assert admission_replay["passed"] is True
    assert admission_replay["forbidden_fields_used"] == []

    renderer = result["renderer_isolation"]
    assert renderer["renderer_used_for_action_selection"] is False
    assert renderer["adversarial_renderer_action_change_rate"] == 0.0
    assert renderer["llm_action_selection"] is False


def test_007b_execute_artifacts_and_admission_traces_show_pending_hidden(tmp_path):
    result = run_generated_option_feedback_admission_007b_execute(
        tmp_path, generated_option_count=24
    )

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})

    effect_records = [
        json.loads(line)
        for line in (tmp_path / "admission_filtered_effect_vector_trace.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    pending = next(
        row for row in effect_records if row["feedback_admission_status"] == "pending_counterevidence"
    )
    admitted = next(
        row
        for row in effect_records
        if row["feedback_admission_status"] == "admitted_context_counterevidence"
    )
    assert pending["effect_vector_visibility_status"] == "base_only_pending_hidden"
    assert pending["selector_visible_predicted_effect_vector"] == pending["base_effect_vector"]
    assert pending["pending_counterevidence_effect_delta"]
    assert admitted["effect_vector_visibility_status"] == "admitted_delta_visible"
    assert admitted["selector_visible_predicted_effect_vector"] != admitted["base_effect_vector"]

    selector_trace = json.loads(
        (tmp_path / "parametric_selector_input_trace.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()[0]
    )
    selector_blob = json.dumps(selector_trace["selector_input"], ensure_ascii=False, sort_keys=True)
    for token in FORBIDDEN_SELECTOR_TOKENS:
        assert token not in selector_blob


def test_007b_execute_preserves_prior_evidence_and_boundaries(tmp_path):
    result = run_generated_option_feedback_admission_007b_execute(
        tmp_path, generated_option_count=24
    )

    preservation = result["evidence_preservation"]
    assert preservation["preserve_003_as"] == "small-action-set free-input causal-probe evidence only"
    assert preservation["preserve_005_as"] == "N=7 shadow compatibility evidence only"
    assert preservation["preserve_006_as"] == "bounded N=24 prebuilt CandidateOption evidence only"
    assert preservation["preserve_007_shadow_as"] == "bounded generated-option shadow evidence only"
    assert preservation["preserve_failed_007_execute_as"] == "failed generated-option execution evidence"
    assert preservation["rewrite_prior_evidence_as_007b_execute_evidence"] is False

    assert result["selector_patched"] is False
    assert result["thresholds_changed"] is False
    assert result["rag_baseline_weakened"] is False
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["llm_action_selection"] is False
    assert result["claim_after_execute"] == (
        "bounded generated-option feedback admission execution evidence only; "
        "not real companion readiness"
    )


def test_007b_execute_does_not_reuse_failed_007_execute_or_fixed_table():
    import cmbc_companion.demos.generated_option_feedback_admission_007b_execute as module

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
