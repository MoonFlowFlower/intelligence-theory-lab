import csv
import json

from cmbc_companion.evals.blind_human_trial_rca_001 import (
    ALLOWED_VERDICTS,
    run_blind_human_trial_rca_001,
)


def test_blind_rca_scope_and_frozen_failure(tmp_path):
    result = run_blind_human_trial_rca_001(tmp_path)

    assert result["suite_id"] == "CMBC-COMPANION-BLIND-RCA-001"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["source_failure"]["suite_id"] == "CMBC-COMPANION-BLIND-HUMAN-TRIAL-001"
    assert result["source_failure"]["verdict"] == "heuristic_or_rag_equivalent"
    assert result["source_failure"]["stop_condition"] == "rag_summary_memory_equivalent"
    assert result["claim_boundary"] == "RCA only; bounded offline human-trial generalization evidence retained"
    assert result["selector_patched"] is False
    assert result["thresholds_changed"] is False
    assert result["rag_baseline_weakened"] is False
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["llm_action_selection"] is False


def test_turn_by_turn_comparison_and_classification(tmp_path):
    result = run_blind_human_trial_rca_001(tmp_path)

    comparison = result["turn_match_comparison"]
    assert comparison["turn_count"] == 24
    assert comparison["rag_match_count"] == 24
    assert comparison["rag_match_rate"] == 1.0
    assert comparison["strong_heuristic_match_rate"] == 0.9166666666666666
    assert comparison["all_rag_matches_have_supporting_prior_ids"] is True

    classifications = result["decision_classification"]
    assert classifications["classified_turn_count"] == 24
    assert classifications["counts"]["surface_context_sufficient"] >= 20
    assert classifications["counts"]["memory_summary_sufficient"] >= 20
    assert classifications["counts"]["causal_prior_required_but_not_tested"] >= 1
    assert classifications["counts"]["deletion_probe_missing"] >= 1
    assert classifications["counts"]["perturbation_probe_missing"] >= 1
    assert classifications["counts"]["feedback_admission_probe_missing"] >= 1
    assert set(classifications["allowed_labels"]) == {
        "surface_context_sufficient",
        "memory_summary_sufficient",
        "causal_prior_required_but_not_tested",
        "deletion_probe_missing",
        "perturbation_probe_missing",
        "feedback_admission_probe_missing",
    }


def test_posthoc_causal_probes_distinguish_cmbc_from_rag(tmp_path):
    result = run_blind_human_trial_rca_001(tmp_path)

    probes = result["posthoc_causal_probes"]
    assert probes["probe_count"] >= 5
    assert probes["rag_behavior_equivalent_on_original_turns"] is True
    assert probes["rag_remains_equivalent_under_causal_probes"] is False
    assert probes["candidate_rag_probe_match_rate"] < 0.95
    assert probes["supporting_prior_deletion"]["candidate_action_changed"] is True
    assert probes["supporting_prior_deletion"]["rag_action_changed"] is False
    assert probes["rag_summary_sentence_deletion"]["rag_action_changed"] is False
    assert probes["effect_perturbation"]["candidate_distribution_changed"] is True
    assert probes["effect_perturbation"]["rag_action_changed"] is False
    assert probes["same_prompt_different_causal_history"]["candidate_action_changed"] is True
    assert probes["same_prompt_different_causal_history"]["rag_action_changed"] is False
    assert probes["feedback_outcome_swap_same_text"]["candidate_action_changed_or_distribution_shift"] is True
    assert probes["feedback_admission_probe"]["rag_has_admission_state"] is False


def test_rca_verdict_and_artifacts(tmp_path):
    result = run_blind_human_trial_rca_001(tmp_path)

    assert result["verdict"] == "rag_equivalent_on_behavior_but_not_causal_probes"
    assert result["claim_after_rca"] == "bounded offline human-trial generalization evidence only"
    assert "blind_prompt_sheet_too_surface_level" in result["secondary_findings"]
    assert "strong_heuristic_near_equivalence_due_to_weak_prompt_distribution" in result["secondary_findings"]
    assert result["not_authorized"] == [
        "EGO migration",
        "real companion implementation",
        "proactive messages",
        "LLM action selection",
        "selector patch",
        "RAG baseline weakening",
        "threshold change",
        "open-ended robustness claim",
    ]

    required = {
        "RCA_STATUS.md",
        "frozen_failure_manifest.json",
        "turn_match_comparison.csv",
        "turn_match_comparison.json",
        "decision_classification_summary.md",
        "decision_classification_summary.json",
        "causal_probe_report.md",
        "causal_probe_report.json",
        "rag_equivalence_rca_result.json",
    }
    assert required.issubset({path.name for path in tmp_path.iterdir()})
    with (tmp_path / "turn_match_comparison.csv").open("r", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 24
    with (tmp_path / "rag_equivalence_rca_result.json").open("r", encoding="utf-8") as fh:
        verdict = json.load(fh)
    assert verdict["verdict"] == result["verdict"]
    assert verdict["claim_after_rca"] == result["claim_after_rca"]
    assert verdict["authorization_boundary"] == {
        "ego_migration": "no_go",
        "real_companion_implementation": "not_authorized",
        "proactive_messages": "not_authorized",
        "llm_action_selection": False,
        "selector_patched": False,
        "thresholds_changed": False,
        "rag_baseline_weakened": False,
    }
