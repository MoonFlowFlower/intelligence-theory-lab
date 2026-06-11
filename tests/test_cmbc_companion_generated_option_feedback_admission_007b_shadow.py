import inspect
import json

from cmbc_companion.evals.generated_option_feedback_admission_007b_shadow import (
    ALLOWED_VERDICTS,
    run_generated_option_feedback_admission_007b_shadow,
)


REQUIRED_ARTIFACTS = {
    "GENERATED_OPTION_FEEDBACK_ADMISSION_007B_SHADOW_STATUS.md",
    "freeze_manifest.json",
    "pending_counterevidence_records.jsonl",
    "feedback_admission_state_trace.jsonl",
    "generated_option_feedback_update_ledger.jsonl",
    "admission_filtered_effect_vector_trace.jsonl",
    "selector_visible_effect_vector_contract_report.json",
    "admission_aware_replay.json",
    "behavior_only_replay.json",
    "renderer_isolation_report.md",
    "evidence_preservation_report.json",
    "generated_option_feedback_admission_007b_shadow_result.json",
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


def test_007b_shadow_blocks_pending_effect_updates_before_admission(tmp_path):
    result = run_generated_option_feedback_admission_007b_shadow(
        tmp_path, generated_option_count=24
    )

    assert result["suite_id"] == (
        "CMBC-COMPANION-GENERATED-OPTION-FEEDBACK-ADMISSION-007B-SHADOW"
    )
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "generated_option_feedback_admission_007b_shadow_bounded_pass"
    assert result["execution_scope"] == "bounded_shadow_implementation_only"
    assert result["full_007b_execution"] is False
    assert result["minimum_gates_satisfied"] is True
    assert result["stop_conditions"] == []

    metrics = result["metrics"]
    assert metrics["pending_counterevidence_record_count"] >= 1
    assert metrics["selector_visible_effect_update_allowed"] is False
    assert metrics["selector_visible_predicted_effect_vector_delta"] == 0.0
    assert metrics["uncertainty_delta"] > 0.0
    assert metrics["confidence_delta"] < 0.0
    assert metrics["selected_option_changed_due_to_pending"] is False
    assert metrics["behavior_only_replay_match_rate"] == 1.0
    assert metrics["admission_aware_replay_match_rate"] == 1.0
    assert metrics["renderer_action_change_rate"] == 0.0


def test_007b_shadow_allows_repeated_admitted_feedback_to_change_visible_effects(tmp_path):
    result = run_generated_option_feedback_admission_007b_shadow(
        tmp_path, generated_option_count=24
    )

    metrics = result["metrics"]
    admitted_delta = metrics["admitted_context_counterevidence_effect_delta"]
    assert metrics["repeated_feedback_admission_status"] == "admitted_context_counterevidence"
    assert admitted_delta
    assert any(abs(value) > 0.0 for value in admitted_delta.values())
    assert result["repeated_feedback_effect"]["selector_visible_effect_update_allowed"] is True
    assert result["repeated_feedback_effect"]["distribution_changed_after_admission"] is True

    pending = result["pending_feedback_effect"]
    assert pending["selector_visible_effect_update_allowed"] is False
    assert pending["selected_option_before"] == pending["selected_option_after_pending"]
    assert pending["action_distribution_kl"] == 0.0


def test_007b_shadow_writes_admission_aware_trace_and_blocks_selector_leaks(tmp_path):
    result = run_generated_option_feedback_admission_007b_shadow(
        tmp_path, generated_option_count=24
    )

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})

    traces = [
        json.loads(line)
        for line in (tmp_path / "admission_filtered_effect_vector_trace.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    pending_trace = next(
        trace
        for trace in traces
        if trace["feedback_admission_status"] == "pending_counterevidence"
    )
    admitted_trace = next(
        trace
        for trace in traces
        if trace["feedback_admission_status"] == "admitted_context_counterevidence"
    )

    assert pending_trace["effect_vector_visibility_status"] == "base_only_pending_hidden"
    assert pending_trace["pending_counterevidence_effect_delta"]
    assert pending_trace["selector_visible_predicted_effect_vector"] == pending_trace["base_effect_vector"]
    assert admitted_trace["effect_vector_visibility_status"] == "admitted_delta_visible"
    assert admitted_trace["selector_visible_predicted_effect_vector"] != admitted_trace["base_effect_vector"]

    replay = result["admission_aware_replay"]
    assert replay["passed"] is True
    assert replay["match_rate"] == 1.0
    assert replay["forbidden_fields_used"] == []

    selector_report = result["selector_visible_effect_vector_contract"]
    selector_blob = json.dumps(selector_report, ensure_ascii=False, sort_keys=True)
    for token in FORBIDDEN_SELECTOR_TOKENS:
        assert token not in selector_blob


def test_007b_shadow_preserves_boundaries_and_prior_evidence(tmp_path):
    result = run_generated_option_feedback_admission_007b_shadow(
        tmp_path, generated_option_count=24
    )

    assert result["selector_patched"] is False
    assert result["thresholds_changed"] is False
    assert result["rag_baseline_weakened"] is False
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["llm_action_selection"] is False
    assert result["claim_after_shadow"] == (
        "bounded generated-option feedback admission shadow evidence only; "
        "no full 007B execution or real companion readiness"
    )

    preservation = result["evidence_preservation"]
    assert preservation["preserve_003_as"] == "small-action-set free-input causal-probe evidence only"
    assert preservation["preserve_005_as"] == "N=7 shadow compatibility evidence only"
    assert preservation["preserve_006_as"] == "bounded N=24 prebuilt CandidateOption evidence only"
    assert preservation["preserve_007_shadow_as"] == "bounded generated-option shadow evidence only"
    assert preservation["preserve_007_execute_as"] == "failed generated-option execution evidence"
    assert preservation["rewrite_prior_evidence_as_007b_shadow_evidence"] is False


def test_007b_shadow_does_not_call_full_007b_execution_or_fixed_recipe_table():
    import cmbc_companion.evals.generated_option_feedback_admission_007b_shadow as module

    source = inspect.getsource(module)
    forbidden_snippets = [
        "ACTION_HANDLES = 20",
        "range(20)",
        "range(24)",
        "if generated_option_count == 20",
        "if generated_option_count == 24",
        "fixed_generated_options",
        "run_generated_option_feedback_admission_007b_execute",
        "run_candidate_option_generation_007_execute",
        "semantic_action_label",
        "natural_language_description",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in source
