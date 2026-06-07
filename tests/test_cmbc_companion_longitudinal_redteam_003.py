import json

from cmbc_companion.evals.longitudinal_redteam_003 import (
    ALLOWED_VERDICTS,
    run_longitudinal_redteam,
)


def test_expanded_contextual_heuristic_gate_is_decisive(tmp_path):
    result = run_longitudinal_redteam(tmp_path)

    baseline = result["expanded_contextual_heuristic"]
    assert baseline["allowed_fields"] == [
        "observation_vector",
        "goal_weights",
        "recent_outcome_summary",
        "session_index",
        "public_risk_features",
    ]
    assert baseline["forbidden_fields_used"] == []
    if baseline["match_rate"] >= baseline["equivalence_band"]:
        assert result["verdict"] == "contextual_heuristic_equivalent"
    else:
        assert baseline["match_rate"] < baseline["equivalence_band"]
        assert baseline["near_equivalence_risk"] is False


def test_adversarial_context_variants_cover_history_context_and_misleading_cues(tmp_path):
    result = run_longitudinal_redteam(tmp_path)

    variants = result["adversarial_context_variants"]
    required = {
        "same_context_different_causal_history",
        "same_history_different_context",
        "misleading_context_cue",
        "prior_conflict_with_context_cue",
        "heuristic_failure_causal_prior_success",
    }
    assert required.issubset(set(variants["case_types"]))
    assert variants["case_count"] >= 10
    assert variants["candidate_success_rate"] >= 0.80
    assert variants["heuristic_failure_case_count"] >= 2
    assert variants["same_context_different_history_action_divergence"] is True


def test_selected_action_flip_stress_tracks_margin_bands(tmp_path):
    result = run_longitudinal_redteam(tmp_path)

    stress = result["selected_action_flip_stress"]
    assert set(stress["bands"]) == {"low_margin", "medium_margin", "high_margin"}
    assert stress["low_margin"]["selected_action_changed"] is True
    assert stress["medium_margin"]["selected_action_changed"] is True
    assert stress["high_margin"]["probability_drop"] > 0.20
    assert stress["high_margin"]["distribution_kl"] > 0.05
    assert stress["high_margin"]["saturation_reported"] is True


def test_distribution_vs_decision_reporting_matches_verdict(tmp_path):
    result = run_longitudinal_redteam(tmp_path)

    report = result["distribution_vs_decision"]
    assert report["no_distribution_movement"] is False
    assert report["unchanged_selected_action_cases"] >= 1
    assert report["unchanged_selected_action_not_auto_fail"] is True
    if report["all_deletions_saturated_without_flip"]:
        assert result["verdict"] == "selected_action_saturation_only"
    else:
        assert result["verdict"] in {
            "longitudinal_redteam_bounded_pass",
            "contextual_heuristic_equivalent",
        }


def test_behavior_replay_renderer_and_boundaries(tmp_path):
    result = run_longitudinal_redteam(tmp_path)

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
    renderer = result["renderer_isolation"]
    assert renderer["adversarial_renderer_action_change_rate"] == 0.0
    assert renderer["renderer_used_for_action_selection"] is False
    assert result["selector_patched"] is False
    assert result["long_term_memory_weight_added"] is False
    assert result["affection_score_added"] is False
    assert result["ego_migration"] == "no_go"
    assert result["implementation_authorized"] is False


def test_longitudinal_redteam_verdict_artifacts_and_claim_boundary(tmp_path):
    result = run_longitudinal_redteam(tmp_path)

    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["claim_boundary"] == "bounded longitudinal redteam only"

    required = {
        "LONGITUDINAL_REDTEAM_003_STATUS.md",
        "redteam_003_config.json",
        "expanded_contextual_heuristic.json",
        "adversarial_context_variants.json",
        "selected_action_flip_stress.json",
        "distribution_vs_decision.json",
        "baseline_equivalence_report.md",
        "renderer_isolation_report.md",
        "behavior_only_replay.json",
        "decision_trace.jsonl",
        "CMBC_COMPANION_LONGITUDINAL_REDTEAM_003_RESULT.md",
        "cmbc_companion_longitudinal_redteam_003_result.json",
    }
    assert required.issubset({path.name for path in tmp_path.iterdir()})
    with (tmp_path / "cmbc_companion_longitudinal_redteam_003_result.json").open(
        "r", encoding="utf-8"
    ) as fh:
        verdict = json.load(fh)
    assert verdict["verdict"] == result["verdict"]
    assert verdict["claim_boundary"] == "bounded longitudinal redteam only"
