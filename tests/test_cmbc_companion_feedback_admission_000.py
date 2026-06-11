import json

from cmbc_companion.evals.feedback_admission_000 import (
    ALLOWED_VERDICTS,
    run_feedback_admission_gate,
)


def test_feedback_admission_scope_boundaries_and_verdict(tmp_path):
    result = run_feedback_admission_gate(tmp_path)

    assert result["suite_id"] == "CMBC-COMPANION-FEEDBACK-ADMISSION-000"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["claim_boundary"] == "bounded feedback admission gate only"
    assert result["selector_patched"] is False
    assert result["thresholds_changed"] is False
    assert result["affection_score_added"] is False
    assert result["long_term_memory_weight_added"] is False
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["llm_action_selection"] is False
    assert result["implementation_authorized"] is False


def test_single_contradictory_feedback_becomes_pending_not_prior_overwrite(tmp_path):
    result = run_feedback_admission_gate(tmp_path)

    gate = result["single_contradiction_gate"]
    assert gate["feedback_label"] == "bad_timing"
    assert gate["assigned_failure_mode"] == "timing_interruption"
    assert gate["admission_status"] == "pending_counterevidence"
    assert gate["admitted"] is False
    assert gate["pending_counterevidence_count"] == 1
    assert gate["uncertainty_delta"] > 0
    assert gate["context_scope"] == "feedback_focus_context"
    assert gate["source_prior_id"] == "prior_act_2"
    assert gate["prior_source_count_after_gate"] == gate["prior_source_count_before_gate"]
    assert "single_bad_timing_counterevidence" not in gate["prior_source_episode_ids_after_gate"]
    assert gate["raw_unfiltered_selected_action"] == "act_4"
    assert gate["admission_filtered_selected_action"] == "act_2"
    assert gate["existing_prior_preserved"] is True


def test_repeated_or_high_confidence_feedback_required_before_admission(tmp_path):
    result = run_feedback_admission_gate(tmp_path)

    repeated = result["repeated_consistent_feedback_gate"]
    assert repeated["admission_status"] == "admitted_context_counterevidence"
    assert repeated["admitted"] is True
    assert repeated["admitted_evidence_count"] == 3
    assert repeated["admission_reason"] == "repeated_consistent_context_evidence"
    assert repeated["context_scope"] == "feedback_focus_context"
    assert repeated["original_action_prior_preserved"] is True
    assert repeated["admitted_record"]["failure_mode"] == "timing_interruption"
    assert repeated["admitted_record"]["target_action"] == "act_2"
    assert repeated["admitted_record"]["source_feedback_ids"] == [
        "repeated_bad_timing_0",
        "repeated_bad_timing_1",
        "repeated_bad_timing_2",
    ]

    high_confidence = result["high_confidence_feedback_gate"]
    assert high_confidence["admission_status"] == "admitted_context_counterevidence"
    assert high_confidence["admitted"] is True
    assert high_confidence["admitted_evidence_count"] == 1
    assert high_confidence["admission_reason"] == "high_confidence_explicit_correction"
    assert high_confidence["confidence"] >= 0.95
    assert high_confidence["original_action_prior_preserved"] is True


def test_context_specificity_and_failure_mode_mapping(tmp_path):
    result = run_feedback_admission_gate(tmp_path)

    scope = result["context_specificity_audit"]
    assert scope["context_specificity_passed"] is True
    assert scope["single_feedback_context_scope"] == "feedback_focus_context"
    assert scope["focus_context_pending_count"] == 1
    assert scope["light_checkin_context_pending_count"] == 0
    assert scope["support_context_pending_count"] == 0
    assert scope["safety_boundary_context_pending_count"] == 0
    assert scope["bad_timing_mapped_to_boundary_or_safety"] is False
    assert scope["failure_mode_by_label"]["bad_timing"] == "timing_interruption"
    assert scope["failure_mode_by_label"]["too_much"] == "intensity_mismatch"
    assert scope["failure_mode_by_label"]["boundary_respected"] == "safety_boundary_success"


def test_admission_trace_replay_and_counterfactual_effect(tmp_path):
    result = run_feedback_admission_gate(tmp_path)

    replay = result["admission_trace_replay"]
    assert replay["passed"] is True
    assert replay["match_rate"] == 1.0
    assert replay["forbidden_fields_used"] == []
    assert replay["used_fields"] == [
        "feedback_label",
        "outcome_vector",
        "target_action",
        "context_scope",
        "source_prior_id",
        "pending_counterevidence",
        "admitted_context_counterevidence",
        "admission_status",
    ]

    effect = result["counterfactual_admission_effect"]
    assert effect["raw_unfiltered_selected_action"] == "act_4"
    assert effect["admission_filtered_selected_action"] == "act_2"
    assert effect["single_feedback_prevented_action_family_flip"] is True
    assert effect["single_feedback_target_probability_drop"] == 0.0
    assert effect["repeated_admission_changes_admission_state"] is True


def test_required_artifacts_and_claim_boundary(tmp_path):
    result = run_feedback_admission_gate(tmp_path)

    assert result["verdict"] == "feedback_admission_bounded_pass"
    assert result["claim_after_gate"] == "bounded feedback admission gate evidence only"
    assert result["not_proven"] == [
        "open-ended mixed feedback robustness",
        "real companion agent readiness",
        "real proactive messaging safety",
        "longitudinal human relationship stability",
        "consciousness",
        "subjective experience",
        "true self-awareness",
        "AGI",
        "life",
        "real emotion",
        "real love",
        "EGO readiness",
    ]

    required = {
        "FEEDBACK_ADMISSION_000_STATUS.md",
        "feedback_admission_config.json",
        "single_contradiction_gate.json",
        "repeated_consistent_feedback_gate.json",
        "high_confidence_feedback_gate.json",
        "context_specificity_audit.json",
        "counterfactual_admission_effect.json",
        "admission_trace_replay.json",
        "admission_trace.jsonl",
        "CMBC_COMPANION_FEEDBACK_ADMISSION_000_RESULT.md",
        "cmbc_companion_feedback_admission_000_result.json",
    }
    assert required.issubset({path.name for path in tmp_path.iterdir()})
    with (tmp_path / "cmbc_companion_feedback_admission_000_result.json").open(
        "r", encoding="utf-8"
    ) as fh:
        verdict = json.load(fh)
    assert verdict["verdict"] == result["verdict"]
    assert verdict["claim_after_gate"] == result["claim_after_gate"]
