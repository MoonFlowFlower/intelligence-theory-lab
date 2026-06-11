import json

from cmbc_companion.demos.blind_human_trial_001 import (
    ALLOWED_VERDICTS,
    run_blind_human_trial_001,
)


def test_blind_trial_scope_freeze_and_boundaries(tmp_path):
    result = run_blind_human_trial_001(tmp_path)

    assert result["suite_id"] == "CMBC-COMPANION-BLIND-HUMAN-TRIAL-001"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["claim_boundary"] == "bounded blind prompt-sheet offline human-trial evidence only"
    assert result["trial_summary"]["mode"] == "frozen_offline_blind_prompt_sheet_trial"
    assert result["trial_summary"]["input_source"] == "blind_prompt_sheet_not_live_human"
    assert result["freeze_integrity"]["candidate_frozen_before_prompt_sheet"] is True
    assert result["freeze_integrity"]["prompt_sheet_generated_after_freeze"] is True
    assert result["freeze_integrity"]["code_hashes_unchanged_after_trial"] is True
    assert result["freeze_integrity"]["selector_hash_before"] == result["freeze_integrity"]["selector_hash_after"]
    assert result["freeze_integrity"]["admission_hash_before"] == result["freeze_integrity"]["admission_hash_after"]
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["background_autonomy"] is False
    assert result["llm_action_selection"] is False
    assert result["selector_patched"] is False
    assert result["thresholds_changed"] is False
    assert result["affection_score_added"] is False
    assert result["long_term_memory_weight_added"] is False


def test_turn_collection_and_blind_input_gates(tmp_path):
    result = run_blind_human_trial_001(tmp_path)

    trial = result["trial_summary"]
    assert 20 <= trial["turn_count"] <= 40
    assert trial["fixture_labels_exposed_to_candidate"] is False
    assert trial["generated_new_scenarios_after_seeing_input"] is False

    blind = result["blind_input_generalization"]
    assert blind["passed"] is True
    assert blind["paraphrase_pass_rate"] >= 0.85
    assert blind["context_collision_disambiguation"] is True
    assert blind["ambiguous_input_count"] >= 4
    assert blind["distinct_selected_actions"] >= 4


def test_feedback_and_prior_causality_gates(tmp_path):
    result = run_blind_human_trial_001(tmp_path)

    feedback = result["feedback_dynamics"]
    assert feedback["feedback_encoded_as_outcome"] is True
    assert feedback["raw_text_memory_only"] is False
    assert feedback["single_contradiction_no_family_flip"] is True
    assert feedback["single_contradiction_status"] == "pending_counterevidence"
    assert feedback["repeated_feedback_status"] == "admitted_context_counterevidence"
    assert feedback["feedback_changes_later_action_distribution"] is True
    assert feedback["target_action_probability_delta"] > 0.05

    deletion = result["supporting_prior_deletion"]
    assert deletion["deleted_actual_supporting_prior"] is True
    assert deletion["selected_action_changed"] or deletion["final_action_probability_drop"] > 0.20
    assert deletion["final_action_probability_drop"] > 0.20


def test_renderer_replay_and_strong_baselines(tmp_path):
    result = run_blind_human_trial_001(tmp_path)

    renderer = result["renderer_isolation"]
    assert renderer["passed"] is True
    assert renderer["adversarial_renderer_action_change_rate"] == 0.0
    assert renderer["renderer_used_for_action_selection"] is False
    assert renderer["llm_action_selection"] is False
    assert renderer["real_llm_called"] is False

    replay = result["behavior_only_replay"]
    assert replay["passed"] is True
    assert replay["match_rate"] == 1.0
    assert replay["forbidden_fields_used"] == []

    baselines = result["strong_baselines"]
    assert baselines["strong_human_like_heuristic"]["match_rate"] < 0.95
    assert baselines["strong_human_like_heuristic"]["equivalent"] is False
    assert baselines["rag_summary_memory"]["match_rate"] == 1.0
    assert baselines["rag_summary_memory"]["equivalent"] is True
    assert baselines["forbidden_fields_used"] == []


def test_artifacts_and_claim_boundary(tmp_path):
    result = run_blind_human_trial_001(tmp_path)

    assert result["verdict"] == "heuristic_or_rag_equivalent"
    assert result["claim_after_trial"] == "bounded offline human-trial generalization evidence only"
    assert result["stop_conditions"] == ["rag_summary_memory_equivalent"]
    assert "not_live_human_input" in result["residual_risks"]
    assert "rag_summary_memory_near_or_full_equivalence_risk" in result["residual_risks"]
    assert result["not_proven"] == [
        "live human trial robustness",
        "open-ended mixed feedback robustness",
        "real companion agent readiness",
        "real proactive messaging safety",
        "LLM renderer safety in production",
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
        "BLIND_HUMAN_TRIAL_001_STATUS.md",
        "blind_human_trial_001_config.json",
        "freeze_manifest.json",
        "blind_prompt_sheet.json",
        "trial_transcript.md",
        "trial_transcript.json",
        "developer_trace.jsonl",
        "feedback_outcomes.jsonl",
        "behavior_only_replay.json",
        "supporting_prior_deletion_report.json",
        "strong_baseline_report.json",
        "renderer_isolation_report.md",
        "CMBC_COMPANION_BLIND_HUMAN_TRIAL_001_RESULT.md",
        "cmbc_companion_blind_human_trial_001_result.json",
        "STOP_REPORT.md",
    }
    assert required.issubset({path.name for path in tmp_path.iterdir()})
    with (tmp_path / "cmbc_companion_blind_human_trial_001_result.json").open(
        "r", encoding="utf-8"
    ) as fh:
        verdict = json.load(fh)
    assert verdict["verdict"] == result["verdict"]
    assert verdict["claim_after_trial"] == result["claim_after_trial"]
