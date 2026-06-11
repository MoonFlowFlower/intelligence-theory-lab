import json

from cmbc_companion.demos.blind_human_trial_002 import (
    ALLOWED_VERDICTS,
    run_blind_human_trial_002,
)


def test_blind_trial_002_scope_freeze_and_boundaries(tmp_path):
    result = run_blind_human_trial_002(tmp_path)

    assert result["suite_id"] == "CMBC-COMPANION-BLIND-HUMAN-TRIAL-002"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["claim_boundary"] == "causal-probe-enriched blind/offline human-trial evidence only"
    assert result["trial_summary"]["mode"] == "frozen_offline_causal_probe_enriched_blind_trial"
    assert result["trial_summary"]["input_source"] == "blind_prompt_sheet_with_predeclared_causal_probes_not_live_human"
    assert result["freeze_integrity"]["candidate_frozen_before_prompt_sheet"] is True
    assert result["freeze_integrity"]["prompt_sheet_generated_after_freeze"] is True
    assert result["freeze_integrity"]["code_hashes_unchanged_after_trial"] is True
    assert result["selector_patched"] is False
    assert result["thresholds_changed"] is False
    assert result["rag_baseline_weakened"] is False
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["llm_action_selection"] is False


def test_visible_and_causal_probe_scorecards(tmp_path):
    result = run_blind_human_trial_002(tmp_path)

    visible = result["visible_decision_scorecard"]
    assert visible["turn_count"] >= 20
    assert visible["visible_decision_pass_rate"] >= 0.85
    assert visible["context_collision_disambiguation"] is True
    assert visible["rag_visible_action_match_rate"] >= 0.85

    causal = result["causal_probe_scorecard"]
    assert causal["probe_count"] >= 6
    assert causal["causal_probe_pass_rate"] >= 0.85
    assert causal["rag_causal_probe_match_rate"] < 0.95
    assert causal["strong_heuristic_causal_probe_match_rate"] < 0.95
    assert causal["supporting_prior_deletion_effect"] is True
    assert causal["perturbation_sensitivity"] is True
    assert causal["same_text_different_causal_history_distinguished"] is True
    assert causal["same_history_different_feedback_outcome_distinguished"] is True


def test_feedback_admission_and_renderer_replay_gates(tmp_path):
    result = run_blind_human_trial_002(tmp_path)

    feedback = result["feedback_admission_scorecard"]
    assert feedback["single_bad_timing_status"] == "pending_counterevidence"
    assert feedback["single_bad_timing_no_family_flip"] is True
    assert feedback["repeated_feedback_status"] == "admitted_context_counterevidence"
    assert feedback["repeated_feedback_admits_context_counterevidence"] is True
    assert feedback["later_correction_context_narrows"] is True

    renderer = result["renderer_isolation"]
    assert renderer["passed"] is True
    assert renderer["adversarial_renderer_action_change_rate"] == 0.0
    assert renderer["renderer_used_for_action_selection"] is False
    assert renderer["llm_action_selection"] is False

    replay = result["behavior_only_replay"]
    assert replay["passed"] is True
    assert replay["match_rate"] == 1.0
    assert replay["forbidden_fields_used"] == []


def test_verdict_artifacts_and_claim_boundary(tmp_path):
    result = run_blind_human_trial_002(tmp_path)

    assert result["verdict"] == "cmbc_beats_rag_under_causal_probes_bounded"
    assert result["claim_after_trial"] == "bounded causal-probe-enriched blind/offline human-trial evidence only"
    assert result["stop_conditions"] == []
    assert result["not_authorized"] == [
        "EGO migration",
        "real companion implementation",
        "real proactive messages",
        "background autonomy",
        "LLM action selection",
        "selector patch",
        "RAG baseline weakening",
        "threshold change",
        "real companion readiness claim",
    ]
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
        "BLIND_HUMAN_TRIAL_002_STATUS.md",
        "blind_human_trial_002_config.json",
        "freeze_manifest.json",
        "causal_probe_blind_prompt_sheet.json",
        "trial_transcript.json",
        "trial_transcript.md",
        "causal_probe_results.json",
        "baseline_causal_probe_report.json",
        "behavior_only_replay.json",
        "renderer_isolation_report.md",
        "developer_trace.jsonl",
        "feedback_outcomes.jsonl",
        "CMBC_COMPANION_BLIND_HUMAN_TRIAL_002_RESULT.md",
        "cmbc_companion_blind_human_trial_002_result.json",
    }
    assert required.issubset({path.name for path in tmp_path.iterdir()})
    with (tmp_path / "cmbc_companion_blind_human_trial_002_result.json").open(
        "r", encoding="utf-8"
    ) as fh:
        verdict = json.load(fh)
    assert verdict["verdict"] == result["verdict"]
    assert verdict["claim_after_trial"] == result["claim_after_trial"]
    assert verdict["rag_causal_probe_match_rate"] == result["causal_probe_scorecard"]["rag_causal_probe_match_rate"]
