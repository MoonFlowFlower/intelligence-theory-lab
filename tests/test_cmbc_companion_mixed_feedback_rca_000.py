import json

from cmbc_companion.evals.mixed_feedback_rca_000 import ALLOWED_VERDICTS, run_rca


def test_rca_freezes_human_trial_redteam_failure_artifacts(tmp_path):
    result = run_rca(tmp_path)

    manifest = result["frozen_failure_manifest"]
    assert manifest["source_suite"] == "CMBC-COMPANION-HUMAN-TRIAL-REDTEAM-001"
    assert manifest["source_verdict"] == "contradictory_feedback_overfit"
    assert manifest["source_stop_conditions"] == ["contradictory_feedback_overfit"]
    assert len(manifest["frozen_artifacts"]) >= 5
    assert (tmp_path / "frozen_failure_manifest.json").exists()


def test_rca_extracts_pre_post_contradiction_causal_path(tmp_path):
    result = run_rca(tmp_path)

    comparison = result["pre_post_contradiction_comparison"]
    assert comparison["pre"]["selected_action"] == "act_2"
    assert comparison["post"]["selected_action"] == "act_4"
    assert comparison["contradiction"]["feedback_label"] == "bad_timing"
    assert comparison["contradiction"]["target_action"] == "act_2"
    assert comparison["contradiction"]["outcome_vector"]["interruption_risk"] > 0.7
    assert comparison["pre"]["prior_for_target"]["action_handle"] == "act_2"
    assert comparison["post"]["prior_for_target"]["action_handle"] == "act_2"
    assert comparison["post"]["prior_for_target"]["source_action_count"] == (
        comparison["pre"]["prior_for_target"]["source_action_count"] + 1
    )
    assert comparison["post"]["action_distribution"]["act_2"] < comparison["pre"]["action_distribution"]["act_2"]
    assert comparison["post"]["action_distribution"]["act_4"] > comparison["pre"]["action_distribution"]["act_4"]


def test_rca_separates_score_delta_from_distribution_delta(tmp_path):
    result = run_rca(tmp_path)

    score = result["score_vs_distribution_delta"]
    assert score["selected_action_changed"] is True
    assert score["target_action"] == "act_2"
    assert score["replacement_action"] == "act_4"
    assert score["utility_delta_by_action"]["act_2"] < 0
    assert score["utility_delta_by_action"]["act_4"] == 0
    assert score["probability_delta_by_action"]["act_2"] < 0
    assert score["probability_delta_by_action"]["act_4"] > 0
    assert score["act4_rose_due_to_act2_drop_not_boundary_update"] is True


def test_rca_audits_credit_assignment_and_action_family_transition(tmp_path):
    result = run_rca(tmp_path)

    credit = result["credit_assignment_audit"]
    assert credit["bad_timing_attribution"]["action_identity"] is True
    assert credit["bad_timing_attribution"]["context_timing"] is False
    assert credit["bad_timing_attribution"]["response_intensity"] is False
    assert credit["prior_scope"] == "action_level_only"
    assert credit["feedback_admission_gate_present"] is False
    assert credit["uncertainty_state_present"] is False

    transition = result["action_family_transition_audit"]
    assert transition["transition"] == "ask_permission_to_set_boundary"
    assert transition["timing_feedback_directly_caused_boundary_family"] is True
    assert transition["safety_or_boundary_context_present"] is False
    assert transition["transition_valid_without_safety_context"] is False


def test_rca_compares_negative_feedback_scenarios(tmp_path):
    result = run_rca(tmp_path)

    scenarios = result["negative_feedback_scenarios"]
    assert scenarios["single_noisy_negative_feedback"]["selected_action_changed"] is True
    assert scenarios["multi_sample_negative_feedback"]["selected_action"] == "act_4"
    assert scenarios["context_specific_negative_feedback"]["represented_as_context_specific"] is False
    assert scenarios["context_specific_negative_feedback"]["selected_action"] == "act_4"
    assert scenarios["global_negative_feedback"]["selected_action"] == "act_4"
    assert scenarios["context_specificity_missing"] is True


def test_rca_verdict_and_boundaries(tmp_path):
    result = run_rca(tmp_path)

    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "negative_feedback_credit_assignment_too_coarse"
    assert "feedback_admission_missing" in result["secondary_findings"]
    assert "uncertainty_not_updated_before_policy_flip" in result["secondary_findings"]
    assert "context_specificity_missing" in result["secondary_findings"]
    assert result["runtime_code_changed"] is False
    assert result["selector_patched"] is False
    assert result["thresholds_changed"] is False
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["claim_after_rca"] == "scripted lab harness evidence only"


def test_rca_required_artifacts_are_written(tmp_path):
    result = run_rca(tmp_path)

    required = {
        "RCA_STATUS.md",
        "frozen_failure_manifest.json",
        "pre_post_contradiction_comparison.json",
        "causal_path_trace.jsonl",
        "credit_assignment_audit.json",
        "score_vs_distribution_delta.json",
        "action_family_transition_audit.json",
        "action_family_transition_audit.md",
        "negative_feedback_scenarios.json",
        "CMBC_COMPANION_MIXED_FEEDBACK_RCA_RESULT.md",
        "cmbc_companion_mixed_feedback_rca_result.json",
    }
    assert required.issubset({path.name for path in tmp_path.iterdir()})

    with (tmp_path / "cmbc_companion_mixed_feedback_rca_result.json").open(
        "r", encoding="utf-8"
    ) as fh:
        verdict = json.load(fh)
    assert verdict["verdict"] == result["verdict"]
    assert verdict["claim_after_rca"] == result["claim_after_rca"]
