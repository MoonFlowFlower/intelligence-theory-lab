import json

from cmbc_companion.evals.consolidation_000 import ALLOWED_VERDICTS, run_consolidation


def test_consolidated_prior_records_source_episode_support(tmp_path):
    result = run_consolidation(tmp_path)

    priors = result["consolidated_priors"]
    final_prior_id = result["final_action_support"]["supporting_prior_id"]
    assert final_prior_id in priors
    assert priors[final_prior_id]["action_handle"] == result["final_action_support"]["final_action"]
    assert len(priors[final_prior_id]["source_episode_ids"]) >= 3
    assert priors[final_prior_id]["source_action_count"] >= 3


def test_final_action_is_traced_to_consolidated_prior(tmp_path):
    result = run_consolidation(tmp_path)

    support = result["final_action_support"]
    assert support["final_action"] == support["supporting_action_handle"]
    assert support["supporting_prior_id"].startswith("prior_")
    assert support["prior_used_in_prediction"] is True
    assert support["prior_used_in_action_distribution"] is True


def test_relevant_deletion_targets_final_action_support(tmp_path):
    result = run_consolidation(tmp_path)

    relevant = result["deletion_comparison"]["consolidated_prior_deletion"]
    assert relevant["deleted_prior_action"] == result["final_action_support"]["final_action"]
    assert relevant["deleted_actual_final_action_support"] is True
    assert relevant["final_action_probability_drop"] > 0.20
    assert relevant["distribution_kl"] > 0.05


def test_irrelevant_and_raw_deletion_do_not_match_targeted_prior_deletion(tmp_path):
    result = run_consolidation(tmp_path)

    relevant = result["deletion_comparison"]["consolidated_prior_deletion"]
    irrelevant = result["deletion_comparison"]["irrelevant_prior_deletion"]
    raw = result["deletion_comparison"]["raw_episodic_deletion"]
    recency = result["deletion_comparison"]["recency_only_deletion"]
    assert irrelevant["final_action_probability_drop"] < relevant["final_action_probability_drop"]
    assert raw["deleted_actual_final_action_support"] is False
    assert raw["selected_action_changed"] is False
    assert recency["selected_action_changed"] is False


def test_behavior_only_replay_reconstructs_prior_to_distribution(tmp_path):
    result = run_consolidation(tmp_path)

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


def test_recency_only_baseline_not_equivalent_or_reports_verdict(tmp_path):
    result = run_consolidation(tmp_path)

    baseline = result["baselines"]["RecencyOnlyBaseline"]
    if baseline["equivalent"]:
        assert result["verdict"] == "recency_dominates_consolidation"
    else:
        assert baseline["match_rate"] < baseline["equivalence_band"]


def test_consolidation_verdict_and_artifacts(tmp_path):
    result = run_consolidation(tmp_path)

    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] in {
        "consolidation_bounded_pass",
        "action_distribution_saturated_but_regresses",
    }
    assert result["selector_patched"] is False
    assert result["long_term_memory_weight_added"] is False
    assert result["affection_score_added"] is False
    assert result["ego_migration"] == "no_go"
    assert result["implementation_authorized"] is False

    required = {
        "CONSOLIDATION_STATUS.md",
        "consolidation_config.json",
        "consolidated_priors.json",
        "prior_source_trace.jsonl",
        "decision_trace.jsonl",
        "deletion_comparison.json",
        "raw_vs_consolidated_deletion_report.md",
        "behavior_only_replay.json",
        "baseline_report.md",
        "CMBC_COMPANION_CONSOLIDATION_RESULT.md",
        "cmbc_companion_consolidation_result.json",
    }
    assert required.issubset({path.name for path in tmp_path.iterdir()})
    with (tmp_path / "cmbc_companion_consolidation_result.json").open(
        "r", encoding="utf-8"
    ) as fh:
        verdict = json.load(fh)
    assert verdict["verdict"] == result["verdict"]
    assert verdict["claim_boundary"] == "bounded consolidation gate only"

