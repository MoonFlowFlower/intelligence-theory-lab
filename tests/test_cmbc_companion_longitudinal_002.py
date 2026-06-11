import json

from cmbc_companion.evals.longitudinal_002 import (
    ALLOWED_VERDICTS,
    run_longitudinal_growth_gate,
)


def test_multi_session_rollout_builds_traceable_priors(tmp_path):
    result = run_longitudinal_growth_gate(tmp_path)

    rollout = result["multi_session_rollout"]
    assert rollout["session_count"] >= 4
    assert rollout["episode_count"] >= 16
    assert rollout["consolidated_prior_count"] >= 4
    assert rollout["multi_session_prior_ids"] >= 3
    assert result["final_action_support"]["supporting_prior_id"].startswith("prior_")
    assert result["final_action_support"]["source_session_count"] >= 2


def test_cross_context_transfer_uses_priors_not_scene_lookup(tmp_path):
    result = run_longitudinal_growth_gate(tmp_path)

    transfer = result["cross_context_transfer"]
    assert transfer["transfer_context_count"] >= 4
    assert transfer["transfer_success_rate"] >= 0.75
    assert transfer["scene_lookup_baseline"]["equivalent"] is False
    assert transfer["selected_by_context"]["office_focus_context"] == "act_2"
    assert transfer["selected_by_context"]["evening_support_context"] == "act_6"


def test_prior_conflict_arbitration_is_context_sensitive(tmp_path):
    result = run_longitudinal_growth_gate(tmp_path)

    conflict = result["prior_conflict_arbitration"]
    assert conflict["conflict_context_count"] >= 4
    assert conflict["distinct_selected_actions"] >= 3
    assert conflict["fixed_priority_baseline"]["equivalent"] is False
    assert conflict["selected_by_context"]["free_checkin_context"] == "act_0"
    assert conflict["selected_by_context"]["class_interruption_context"] == "act_2"
    assert conflict["selected_by_context"]["safety_boundary_context"] == "act_4"


def test_consolidated_prior_deletion_corruption_and_source_deletion(tmp_path):
    result = run_longitudinal_growth_gate(tmp_path)

    perturb = result["prior_deletion_corruption"]
    assert perturb["deleted_prior_id"] == result["final_action_support"]["supporting_prior_id"]
    assert perturb["delete_final_prior_probability_drop"] > 0.20
    assert (
        perturb["delete_final_prior_changes_action"]
        or perturb["delete_final_prior_probability_drop"] > 0.50
    )
    assert perturb["corrupt_final_prior_changes_action"] is True
    assert perturb["corrupt_irrelevant_prior_changes_action"] is False

    source = result["source_deletion_audit"]
    assert source["deleted_actual_prior_sources"] is True
    assert source["prior_confidence_drop"] > 0.20
    assert source["final_action_probability_drop"] > 0.20


def test_strong_baselines_renderer_and_replay_do_not_explain_gate(tmp_path):
    result = run_longitudinal_growth_gate(tmp_path)

    baselines = result["baseline_equivalence"]
    for name in [
        "RecencyOnlyBaseline",
        "RAGSummaryBaseline",
        "StrongContextualHeuristicBaseline",
    ]:
        if baselines[name]["equivalent"]:
            assert result["verdict"] in {
                "recency_dominates_longitudinal_memory",
                "rag_summary_equivalent",
                "strong_contextual_heuristic_equivalent",
            }
        else:
            assert baselines[name]["match_rate"] < baselines[name]["equivalence_band"]

    renderer = result["renderer_isolation"]
    assert renderer["adversarial_renderer_action_change_rate"] == 0.0
    assert renderer["renderer_used_for_action_selection"] is False

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


def test_longitudinal_002_verdict_artifacts_and_boundaries(tmp_path):
    result = run_longitudinal_growth_gate(tmp_path)

    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "longitudinal_growth_bounded_pass"
    assert result["claim_boundary"] == "bounded longitudinal growth gate only"
    assert result["selector_patched"] is False
    assert result["long_term_memory_weight_added"] is False
    assert result["affection_score_added"] is False
    assert result["ego_migration"] == "no_go"
    assert result["implementation_authorized"] is False

    required = {
        "LONGITUDINAL_002_STATUS.md",
        "longitudinal_002_config.json",
        "multi_session_rollout.json",
        "cross_context_transfer.json",
        "prior_conflict_arbitration.json",
        "prior_deletion_corruption.json",
        "source_deletion_audit.json",
        "baseline_equivalence_report.md",
        "renderer_isolation_report.md",
        "behavior_only_replay.json",
        "decision_trace.jsonl",
        "prior_source_trace.jsonl",
        "CMBC_COMPANION_LONGITUDINAL_002_RESULT.md",
        "cmbc_companion_longitudinal_002_result.json",
    }
    assert required.issubset({path.name for path in tmp_path.iterdir()})
    with (tmp_path / "cmbc_companion_longitudinal_002_result.json").open(
        "r", encoding="utf-8"
    ) as fh:
        verdict = json.load(fh)
    assert verdict["verdict"] == result["verdict"]
    assert verdict["claim_boundary"] == "bounded longitudinal growth gate only"
