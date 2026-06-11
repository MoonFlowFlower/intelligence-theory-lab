import inspect
import json

from cmbc_companion.demos.candidate_option_generation_007_redteam_execute import (
    ALLOWED_VERDICTS,
    run_candidate_option_generation_007_redteam_execute,
)


REQUIRED_ARTIFACTS = {
    "CANDIDATE_OPTION_GENERATION_007_REDTEAM_EXECUTE_STATUS.md",
    "freeze_manifest.json",
    "redteam_case_results.jsonl",
    "redteam_family_summary.json",
    "fixed_recipe_generator_audit.json",
    "generator_hidden_selector_audit.json",
    "admission_gate_redteam_report.json",
    "weak_evidence_high_confidence_audit.json",
    "semantic_leak_scan.json",
    "lineage_falsification_audit.json",
    "near_duplicate_bypass_audit.json",
    "generated_option_baseline_redteam_report.json",
    "replay_sufficiency_redteam_report.json",
    "deletion_perturbation_lineage_report.json",
    "renderer_isolation_redteam_report.md",
    "evidence_preservation_report.json",
    "candidate_option_generation_007_redteam_execute_result.json",
}


def test_007_redteam_execute_runs_all_contract_families(tmp_path):
    result = run_candidate_option_generation_007_redteam_execute(tmp_path)

    assert result["suite_id"] == "CMBC-COMPANION-CANDIDATE-OPTION-GENERATION-007-REDTEAM-EXECUTE"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "generated_option_007_redteam_bounded_pass"
    assert result["execution_scope"] == "bounded_execution_only"
    assert result["minimum_gates_satisfied"] is True
    assert result["stop_conditions"] == []

    metrics = result["metrics"]
    assert metrics["redteam_family_count"] == 12
    assert metrics["redteam_family_coverage_rate"] == 1.0
    assert metrics["redteam_case_count"] >= 36
    assert metrics["passed_case_count"] == metrics["redteam_case_count"]
    assert metrics["failed_case_count"] == 0
    assert metrics["generated_option_count"] >= 20
    assert metrics["admitted_option_count"] >= 20


def test_007_redteam_execute_blocks_fake_generator_and_hidden_selector(tmp_path):
    result = run_candidate_option_generation_007_redteam_execute(tmp_path)
    metrics = result["metrics"]

    assert metrics["fixed_recipe_detected"] is False
    assert metrics["option_fingerprint_changes_with_allowed_history"] is True
    assert metrics["metadata_mutation_changes_generation"] is False
    assert metrics["generator_selected_action"] is False
    assert metrics["generator_ranked_final_actions"] is False
    assert metrics["generator_recommendation_visible_to_selector"] is False
    assert metrics["proposal_order_shuffle_changes_selected_action"] is False
    assert metrics["generator_baseline_action_match_rate"] < 0.5

    hidden = result["generator_hidden_selector_audit"]
    assert hidden["passed"] is True
    assert hidden["generator_selected_action"] is False
    assert hidden["generator_ranked_final_actions"] is False
    assert hidden["selector_receives_only_admitted_options"] is True


def test_007_redteam_execute_admission_lineage_and_replay_are_causal(tmp_path):
    result = run_candidate_option_generation_007_redteam_execute(tmp_path)
    metrics = result["metrics"]

    assert metrics["admission_always_pass_detected"] is False
    assert metrics["admission_always_reject_detected"] is False
    assert metrics["weak_evidence_high_confidence_rate"] == 0.0
    assert metrics["single_contradiction_status"] == "pending_counterevidence"
    assert metrics["repeated_feedback_status"] == "admitted_context_counterevidence"
    assert metrics["near_duplicate_bypass_rate"] == 0.0
    assert metrics["lineage_coverage_rate"] == 1.0
    assert metrics["falsified_lineage_detected"] is True
    assert metrics["missing_source_rejected_or_flagged"] is True
    assert metrics["behavior_only_replay_match_rate"] == 1.0
    assert metrics["admission_aware_replay_match_rate"] == 1.0
    assert metrics["generated_option_perturbation_replay_match_rate"] == 1.0
    assert metrics["supporting_prior_deletion_effect"] is True
    assert metrics["outcome_perturbation_effect"] is True


def test_007_redteam_execute_leaks_baselines_renderer_and_boundaries(tmp_path):
    result = run_candidate_option_generation_007_redteam_execute(tmp_path)
    metrics = result["metrics"]

    assert metrics["semantic_label_visible_to_selector"] is False
    assert metrics["natural_language_description_visible_to_selector"] is False
    assert metrics["renderer_text_visible_to_selector"] is False
    assert metrics["rag_text_visible_to_selector"] is False
    assert metrics["llm_output_visible_to_selector"] is False
    assert metrics["rag_hidden_shortcut_match_rate"] < 0.5
    assert metrics["strong_generated_option_heuristic_match_rate"] < 0.5
    assert metrics["expanded_nearest_neighbor_match_rate"] < 0.5
    assert metrics["frequency_baseline_match_rate"] < 0.5
    assert metrics["recency_baseline_match_rate"] < 0.5
    assert metrics["renderer_action_change_rate"] == 0.0
    assert metrics["baselines_weakened_or_incomparable"] is False

    boundary = result["authorization_boundary"]
    assert boundary["selector_patched"] is False
    assert boundary["thresholds_changed"] is False
    assert boundary["rag_baseline_weakened"] is False
    assert boundary["probe_mutation_after_results"] is False
    assert boundary["ego_migration"] == "no_go"
    assert boundary["real_companion_implementation"] == "not_authorized"
    assert boundary["proactive_messages"] == "not_authorized"
    assert boundary["llm_action_selection"] is False


def test_007_redteam_execute_artifacts_and_evidence_preservation(tmp_path):
    result = run_candidate_option_generation_007_redteam_execute(tmp_path)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    preservation = result["evidence_preservation"]
    assert preservation["preserve_003_as"] == "small-action-set free-input causal-probe evidence only"
    assert preservation["preserve_005_as"] == "N=7 shadow compatibility evidence only"
    assert preservation["preserve_006_as"] == "bounded N=24 prebuilt CandidateOption evidence only"
    assert preservation["preserve_007_shadow_as"] == "bounded generated-option shadow evidence only"
    assert preservation["preserve_failed_007_execute_as"] == "failed generated-option execution evidence"
    assert preservation["preserve_007_reexecute_with_007b_as"] == "bounded re-execution evidence only"
    assert preservation["rewrite_failed_007_execute_as_pass"] is False
    assert preservation["rewrite_prior_evidence_as_redteam_evidence"] is False

    persisted = json.loads(
        (tmp_path / "candidate_option_generation_007_redteam_execute_result.json").read_text(
            encoding="utf-8"
        )
    )
    assert persisted["verdict"] == result["verdict"]
    assert persisted["claim_ceiling"] == (
        "bounded generated-option 007 redteam execution evidence only; not real companion readiness"
    )


def test_007_redteam_execute_does_not_use_fixed_tables_or_failed_runner():
    import cmbc_companion.demos.candidate_option_generation_007_redteam_execute as module

    source = inspect.getsource(module)
    forbidden_snippets = [
        "ACTION_HANDLES = 20",
        "range(20)",
        "range(24)",
        "if generated_option_count == 20",
        "if generated_option_count == 24",
        "fixed_generated_options",
        "run_candidate_option_generation_007_execute",
        "semantic_action_label",
        "natural_language_description",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in source
