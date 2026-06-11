import inspect
import json

from cmbc_companion.demos.longitudinal_generated_options_008_execute import (
    ALLOWED_VERDICTS,
    run_longitudinal_generated_options_008_execute,
)


REQUIRED_ARTIFACTS = {
    "LONGITUDINAL_GENERATED_OPTIONS_008_EXECUTE_STATUS.md",
    "freeze_manifest.json",
    "longitudinal_session_trace.jsonl",
    "generated_option_lifecycle_events.jsonl",
    "admitted_option_snapshots.jsonl",
    "longitudinal_case_results.jsonl",
    "longitudinal_family_summary.json",
    "feedback_inheritance_report.json",
    "source_deletion_report.json",
    "outcome_perturbation_report.json",
    "near_duplicate_prevention_report.json",
    "option_retirement_report.json",
    "option_composition_report.json",
    "baseline_comparison_report.json",
    "behavior_only_replay.json",
    "admission_aware_replay.json",
    "option_lifecycle_replay.json",
    "renderer_isolation_report.md",
    "semantic_leak_scan.json",
    "evidence_preservation_report.json",
    "longitudinal_generated_options_008_result.json",
}


def test_008_execute_runs_bounded_longitudinal_lifecycle(tmp_path):
    result = run_longitudinal_generated_options_008_execute(tmp_path)

    assert result["suite_id"] == "CMBC-COMPANION-LONGITUDINAL-GENERATED-OPTIONS-008-EXECUTE"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "longitudinal_generated_options_008_bounded_pass"
    assert result["execution_scope"] == "bounded_execution_only"
    assert result["minimum_gates_satisfied"] is True
    assert result["stop_conditions"] == []

    metrics = result["metrics"]
    assert metrics["session_count"] >= 4
    assert metrics["total_turn_count"] >= 24
    assert metrics["generated_option_count_cumulative"] >= 20
    assert metrics["admitted_option_count_current"] >= 20
    assert metrics["option_creation_event_count"] >= 4
    assert metrics["option_retirement_event_count"] >= 2
    assert metrics["retired_option_reactivation_traceable"] is True


def test_008_execute_lifecycle_feedback_and_causal_probes_pass(tmp_path):
    result = run_longitudinal_generated_options_008_execute(tmp_path)
    metrics = result["metrics"]

    assert metrics["option_lineage_coverage_rate"] == 1.0
    assert metrics["feedback_inheritance_coverage_rate"] == 1.0
    assert metrics["context_scoped_feedback_admission_rate"] == 1.0
    assert metrics["near_duplicate_bypass_rate"] == 0.0
    assert metrics["retired_option_selected_rate"] == 0.0
    assert metrics["source_deletion_effect"] is True
    assert metrics["outcome_perturbation_effect"] is True

    inheritance = result["feedback_inheritance_report"]
    assert inheritance["descendant_inherits_pending_counterevidence"] is True
    assert inheritance["descendant_inherits_admitted_counterevidence"] is True
    assert inheritance["unrelated_option_inherits_context_local_feedback"] is False

    retirement = result["option_retirement_report"]
    assert retirement["retired_option_selected_rate"] == 0.0
    assert retirement["retired_option_reactivation_traceable"] is True


def test_008_execute_resists_longitudinal_baselines_and_renderer(tmp_path):
    result = run_longitudinal_generated_options_008_execute(tmp_path)
    metrics = result["metrics"]

    assert metrics["rag_longitudinal_match_rate"] < 0.5
    assert metrics["expanded_nearest_neighbor_longitudinal_match_rate"] < 0.5
    assert metrics["frequency_longitudinal_match_rate"] < 0.5
    assert metrics["recency_longitudinal_match_rate"] < 0.5
    assert metrics["strong_generated_option_heuristic_longitudinal_match_rate"] < 0.5
    assert metrics["baselines_weakened_or_incomparable"] is False
    assert metrics["renderer_action_change_rate"] == 0.0

    baseline = result["baseline_comparison"]
    assert baseline["baselines_receive_same_anonymous_options"] is True
    assert baseline["baseline_outputs_visible_to_selector"] is False


def test_008_execute_replay_and_artifacts_are_complete(tmp_path):
    result = run_longitudinal_generated_options_008_execute(tmp_path)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    assert result["metrics"]["behavior_only_replay_match_rate"] == 1.0
    assert result["metrics"]["admission_aware_replay_match_rate"] == 1.0
    assert result["metrics"]["option_lifecycle_replay_match_rate"] == 1.0

    persisted = json.loads(
        (tmp_path / "longitudinal_generated_options_008_result.json").read_text(
            encoding="utf-8"
        )
    )
    assert persisted["verdict"] == result["verdict"]
    assert persisted["claim_ceiling"] == (
        "bounded longitudinal generated-options 008 execution evidence only; "
        "not real companion readiness"
    )


def test_008_execute_preserves_authorization_and_prior_evidence_boundaries(tmp_path):
    result = run_longitudinal_generated_options_008_execute(tmp_path)

    boundary = result["authorization_boundary"]
    assert boundary["selector_patched"] is False
    assert boundary["thresholds_changed"] is False
    assert boundary["rag_baseline_weakened"] is False
    assert boundary["probe_mutation_after_results"] is False
    assert boundary["ego_migration"] == "no_go"
    assert boundary["real_companion_implementation"] == "not_authorized"
    assert boundary["proactive_messages"] == "not_authorized"
    assert boundary["llm_action_selection"] is False

    preservation = result["evidence_preservation"]
    assert preservation["preserve_003_as"] == "small-action-set free-input causal-probe evidence only"
    assert preservation["preserve_005_as"] == "N=7 parametric shadow compatibility evidence only"
    assert preservation["preserve_006_as"] == "bounded N=24 prebuilt CandidateOption evidence only"
    assert preservation["preserve_failed_007_execute_as"] == "failed generated-option execution evidence"
    assert preservation["preserve_007_redteam_execute_as"] == (
        "bounded generated-option redteam evidence only"
    )
    assert preservation["rewrite_prior_evidence_as_008_evidence"] is False


def test_008_execute_does_not_use_forbidden_shortcuts():
    import cmbc_companion.demos.longitudinal_generated_options_008_execute as module

    source = inspect.getsource(module)
    forbidden_snippets = [
        "ACTION_HANDLES = 20",
        "range(20)",
        "if session_count == 4",
        "if generated_option_count == 20",
        "fixed_longitudinal_recipe",
        "semantic_action_label",
        "natural_language_description",
        "run_candidate_option_generation_007_execute",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in source
