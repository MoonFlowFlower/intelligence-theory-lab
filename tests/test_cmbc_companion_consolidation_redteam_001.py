import json

from cmbc_companion.evals.consolidation_redteam_001 import (
    ALLOWED_VERDICTS,
    run_consolidation_redteam,
)


def test_conflicting_priors_are_context_sensitive_not_frequency_only(tmp_path):
    result = run_consolidation_redteam(tmp_path)

    conflict = result["conflicting_prior_audit"]
    assert conflict["contexts_tested"] >= 3
    assert conflict["distinct_selected_actions"] >= 3
    assert conflict["frequency_only_baseline"]["equivalent"] is False
    assert conflict["most_frequent_action"] != conflict["selected_by_context"]["boundary_context"]
    assert conflict["selected_by_context"]["support_context"] == "act_6"
    assert conflict["selected_by_context"]["checkin_context"] == "act_0"
    assert conflict["selected_by_context"]["boundary_context"] == "act_4"


def test_source_episode_deletion_reduces_prior_confidence_and_action_probability(tmp_path):
    result = run_consolidation_redteam(tmp_path)

    source_deletion = result["source_episode_deletion_audit"]
    assert source_deletion["deleted_source_action"] == result["final_action_support"]["final_action"]
    assert source_deletion["prior_confidence_drop"] > 0.20
    assert source_deletion["final_action_probability_drop"] > 0.20
    assert source_deletion["deleted_actual_prior_sources"] is True


def test_noisy_feedback_does_not_form_strong_prior(tmp_path):
    result = run_consolidation_redteam(tmp_path)

    noise = result["noisy_outcome_audit"]
    assert noise["spurious_prior_admitted"] is False
    assert noise["noisy_action_confidence"] < result["admission_thresholds"]["strong_prior_confidence"]
    assert noise["noisy_action_selected"] is False


def test_delayed_outcomes_are_attributed_to_source_actions(tmp_path):
    result = run_consolidation_redteam(tmp_path)

    delayed = result["delayed_outcome_audit"]
    assert delayed["delayed_sources_linked"] is True
    assert delayed["misattributed_to_recent_action_rate"] == 0.0
    assert delayed["delayed_prior_in_control_loop"] is True


def test_prior_corruption_and_renderer_isolation_do_not_fake_pass(tmp_path):
    result = run_consolidation_redteam(tmp_path)

    corruption = result["prior_corruption_audit"]
    renderer = result["renderer_isolation"]
    assert corruption["corrupting_final_prior_changes_action"] is True
    assert corruption["corrupting_irrelevant_prior_changes_action"] is False
    assert renderer["adversarial_renderer_action_change_rate"] == 0.0
    assert renderer["renderer_used_for_action_selection"] is False


def test_stronger_baselines_not_equivalent_or_report_downgrade(tmp_path):
    result = run_consolidation_redteam(tmp_path)

    baselines = result["baseline_equivalence"]
    for name in [
        "RecencyOnlyBaseline",
        "FrequencyOnlyBaseline",
        "ContextualHeuristicBaseline",
    ]:
        if baselines[name]["equivalent"]:
            assert result["verdict"] in {
                "recency_or_frequency_equivalent",
                "contextual_heuristic_equivalent",
            }
        else:
            assert baselines[name]["match_rate"] < baselines[name]["equivalence_band"]


def test_behavior_only_replay_and_claim_boundary(tmp_path):
    result = run_consolidation_redteam(tmp_path)

    replay = result["behavior_only_replay"]
    assert replay["passed"] is True
    assert replay["match_rate"] == 1.0
    assert replay["used_fields"] == [
        "observation",
        "anonymous_candidate_actions",
        "consolidated_prior_records",
        "prediction_before_action",
        "action_distribution",
        "selected_action",
        "prior_support_refs",
    ]
    assert result["selector_patched"] is False
    assert result["long_term_memory_weight_added"] is False
    assert result["affection_score_added"] is False
    assert result["ego_migration"] == "no_go"
    assert result["implementation_authorized"] is False


def test_redteam_verdict_and_required_artifacts(tmp_path):
    result = run_consolidation_redteam(tmp_path)

    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "consolidation_redteam_bounded_pass"
    assert result["claim_boundary"] == "bounded consolidation redteam only"

    required = {
        "REDTEAM_STATUS.md",
        "redteam_config.json",
        "fresh_history_sweep.json",
        "conflicting_prior_audit.json",
        "source_episode_deletion_audit.json",
        "noisy_outcome_audit.json",
        "delayed_outcome_audit.json",
        "prior_corruption_audit.json",
        "baseline_equivalence_report.md",
        "renderer_isolation_report.md",
        "behavior_only_replay.json",
        "CMBC_COMPANION_CONSOLIDATION_REDTEAM_001_RESULT.md",
        "cmbc_companion_consolidation_redteam_001_result.json",
    }
    assert required.issubset({path.name for path in tmp_path.iterdir()})
    with (tmp_path / "cmbc_companion_consolidation_redteam_001_result.json").open(
        "r", encoding="utf-8"
    ) as fh:
        verdict = json.load(fh)
    assert verdict["verdict"] == result["verdict"]
    assert verdict["claim_boundary"] == "bounded consolidation redteam only"
