import inspect
import json

from cmbc_companion.evals.candidate_option_generation_007_rca import (
    ALLOWED_VERDICTS,
    run_candidate_option_generation_007_rca,
)


REQUIRED_ARTIFACTS = {
    "CANDIDATE_OPTION_GENERATION_007_RCA_STATUS.md",
    "failed_probe_trace.json",
    "single_contradiction_audit.json",
    "option_lineage_bypass_audit.json",
    "context_scope_audit.json",
    "weak_evidence_high_confidence_audit.json",
    "outcome_update_ordering_audit.json",
    "replay_sufficiency_audit.json",
    "RCA_RESULT.json",
}


def test_007_rca_localizes_single_contradiction_failure_without_rerun(tmp_path):
    result = run_candidate_option_generation_007_rca(tmp_path)

    assert result["suite_id"] == "CMBC-COMPANION-CANDIDATE-OPTION-GENERATION-007-RCA"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "outcome_update_ordering_bug_confirmed"
    assert "feedback_admission_not_applied_to_generated_options" in result["secondary_findings"]
    assert "weak_evidence_high_confidence_confirmed" in result["secondary_findings"]
    assert "selector_scoring_not_primary_blocker" in result["secondary_findings"]
    assert result["source_failure"]["source_verdict"] == (
        "candidate_option_generation_execute_causal_probe_failed"
    )
    assert result["source_failure"]["source_stop_conditions"] == [
        "feedback_admission_single_contradiction_failed"
    ]
    assert result["recommended_next_task"] == (
        "CMBC-COMPANION-GENERATED-OPTION-FEEDBACK-ADMISSION-007B-CONTRACT"
    )


def test_007_rca_single_contradiction_audit_reports_pending_effect_leak(tmp_path):
    result = run_candidate_option_generation_007_rca(tmp_path)
    audit = result["single_contradiction_audit"]

    assert audit["probe_type"] == "feedback_admission_single_contradiction"
    assert audit["actual_status_reported_pending"] is True
    assert audit["should_have_remained_pending_counterevidence"] is True
    assert audit["pending_counterevidence_still_reached_selector_effect_vector"] is True
    assert audit["selected_option_before"] == "generated_option_08_of_24"
    assert audit["selected_option_after"] == "generated_option_04_of_24"
    assert audit["selected_option_changed"] is True
    assert audit["selected_option_rank_before"] == 1
    assert audit["selected_option_rank_after"] == 6
    assert audit["anonymous_option_flip_occurred"] is True
    assert audit["family_level_flip_assessable"] is False

    delta = audit["contradiction_feedback_record"]["selector_visible_effect_delta"]
    assert delta == {
        "interruption_risk": 0.08,
        "trust_delta": -0.02,
    }


def test_007_rca_rules_out_new_option_lineage_bypass_but_finds_missing_counterevidence(tmp_path):
    result = run_candidate_option_generation_007_rca(tmp_path)
    lineage = result["option_lineage_bypass_audit"]

    assert lineage["same_option_id_set_before_after"] is True
    assert lineage["near_duplicate_new_option_bypass_detected"] is False
    assert lineage["new_option_ids_after_single_contradiction"] == []
    assert lineage["changed_existing_option_ids"] == ["generated_option_08_of_24"]
    assert lineage["changed_options_have_lineage"]["generated_option_08_of_24"] is True
    assert lineage["counterevidence_inherited_by_lineage"] is False


def test_007_rca_context_confidence_and_update_ordering_findings(tmp_path):
    result = run_candidate_option_generation_007_rca(tmp_path)
    scope = result["context_scope_audit"]
    weak = result["weak_evidence_high_confidence_audit"]
    ordering = result["outcome_update_ordering_audit"]
    localization = result["failure_localization"]

    assert scope["context_scope_leak_confirmed"] is False
    assert scope["context_scope_missing_for_feedback_admission"] is True
    assert scope["options_modified_count"] == 1

    assert weak["single_contradiction_status"] == "pending_counterevidence"
    assert weak["effect_vector_changed"] is True
    assert weak["confidence_before"] == weak["confidence_after"]
    assert weak["weak_evidence_high_confidence_confirmed"] is True
    assert weak["single_pending_feedback_created_new_high_confidence_option"] is False
    assert weak["single_pending_feedback_modified_existing_high_confidence_option"] is True

    assert ordering["pending_counterevidence_status_recorded"] is True
    assert ordering["selector_visible_effect_vector_changed_before_admission"] is True
    assert ordering["outcome_update_changed_future_distribution_before_filter"] is True
    assert ordering["outcome_update_ordering_bug_confirmed"] is True

    assert localization["future_option_distribution_update"] == (
        "primary_blocker_update_applied_before_admission_filter"
    )
    assert localization["selector_scoring"] == (
        "not_primary_blocker_selector_followed_selector_visible_effect_vector"
    )


def test_007_rca_replay_sufficiency_and_required_artifacts(tmp_path):
    result = run_candidate_option_generation_007_rca(tmp_path)
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})

    replay = result["replay_sufficiency_audit"]
    assert replay["behavior_only_replay_match_rate"] == 1.0
    assert replay["behavior_only_replay_forbidden_fields_used"] == []
    assert replay["reconstructs_final_action_distribution"] is True
    assert replay["reconstructs_selected_action"] is True
    assert replay["trace_sufficient_for_generated_feedback_admission"] is False
    assert replay["full_artifact_set_contains_proposals"] is True
    assert replay["full_artifact_set_contains_admission_decisions"] is True
    assert replay["full_artifact_set_contains_lineage"] is True
    assert "replay_trace_insufficient_for_generated_feedback_admission" in result["secondary_findings"]

    persisted = json.loads((tmp_path / "RCA_RESULT.json").read_text(encoding="utf-8"))
    assert persisted["verdict"] == result["verdict"]


def test_007_rca_does_not_retry_execute_or_patch_runtime():
    import cmbc_companion.evals.candidate_option_generation_007_rca as module

    source = inspect.getsource(module)
    forbidden_snippets = [
        "run_candidate_option_generation_007_execute(",
        "build_result(",
        "patch_selector",
        "thresholds_changed = True",
        "rag_baseline_weakened = True",
        "EGO migration = " + "go",
        "llm_action_selection = " + "True",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in source
