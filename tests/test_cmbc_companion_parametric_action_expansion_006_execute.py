import inspect
import json

from cmbc_companion.demos.parametric_action_expansion_006_execute import (
    ALLOWED_VERDICTS,
    build_candidate_options,
    run_parametric_action_expansion_006_execute,
)


REQUIRED_ARTIFACTS = {
    "PARAMETRIC_ACTION_EXPANSION_006_EXECUTE_STATUS.md",
    "freeze_manifest.json",
    "expanded_candidate_options.json",
    "parametric_selector_input_trace.jsonl",
    "prediction_before_action_trace.jsonl",
    "action_distribution_trace.jsonl",
    "label_permutation_report.json",
    "effect_swap_report.json",
    "causal_probe_results.json",
    "supporting_prior_deletion_report.json",
    "outcome_perturbation_report.json",
    "feedback_admission_report.json",
    "renderer_isolation_report.md",
    "behavior_only_replay.json",
    "baseline_comparison_report.json",
    "action_distribution_entropy_report.json",
    "dominant_action_rate_report.json",
    "semantic_leak_scan.json",
    "evidence_preservation_report.json",
    "parametric_action_expansion_006_result.json",
}


def test_006_execute_runs_bounded_n_gte_20_without_contract_violations(tmp_path):
    result = run_parametric_action_expansion_006_execute(tmp_path, candidate_option_count=24)

    assert result["suite_id"] == "CMBC-COMPANION-PARAMETRIC-ACTION-EXPANSION-006-EXECUTE"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "parametric_action_expansion_006_bounded_pass"
    assert result["execution_scope"] == "bounded_lab_only_execution"
    assert result["candidate_option_count"] == 24
    assert result["minimum_gates_satisfied"] is True
    assert result["stop_conditions"] == []

    expansion = result["expanded_action_space"]
    assert expansion["candidate_option_count_min_gate"] == 20
    assert expansion["candidate_option_count_max_gate"] == 50
    assert expansion["variable_n_path_used"] is True
    assert expansion["fixed_twenty_action_table_detected"] is False
    assert expansion["fixed_action_handles_20_detected"] is False
    assert expansion["n_specific_branch_detected"] is False


def test_006_execute_candidate_options_are_variable_n_and_anonymous():
    options_24 = build_candidate_options(24)
    options_31 = build_candidate_options(31)

    assert len(options_24) == 24
    assert len(options_31) == 31
    assert [option["option_id"] for option in options_24] != [
        option["option_id"] for option in options_31
    ]
    assert all(option["option_id"].startswith("option_") for option in options_24)

    serialized = json.dumps(options_24, ensure_ascii=False, sort_keys=True)
    forbidden_tokens = [
        "act_",
        "PUBLIC_ACTION_NAMES",
        "semantic",
        "action_family",
        "natural_language",
        "rendered_text",
        "renderer_text",
        "oracle",
        "evaluator_metric",
        "baseline_output",
    ]
    for token in forbidden_tokens:
        assert token not in serialized


def test_006_execute_meets_all_predeclared_metric_gates(tmp_path):
    result = run_parametric_action_expansion_006_execute(tmp_path, candidate_option_count=24)
    metrics = result["metrics"]

    assert metrics["candidate_option_count"] == 24
    assert metrics["semantic_label_visible_to_selector"] is False
    assert metrics["public_action_name_visible_to_selector"] is False
    assert metrics["rendered_text_visible_to_selector"] is False
    assert metrics["natural_language_description_visible_to_selector"] is False
    assert metrics["label_permutation_change_rate"] == 0.0
    assert metrics["effect_swap_change_rate"] >= 0.8
    assert metrics["rag_causal_probe_match_rate"] < 0.5
    assert metrics["strong_heuristic_causal_probe_match_rate"] < 0.5
    assert metrics["expanded_contextual_heuristic_causal_probe_match_rate"] < 0.5
    assert metrics["expanded_action_frequency_match_rate"] < 0.5
    assert metrics["expanded_action_nearest_neighbor_match_rate"] < 0.5
    assert metrics["behavior_only_replay_match_rate"] == 1.0
    assert metrics["renderer_action_change_rate"] == 0.0
    assert metrics["action_distribution_entropy_reported"] is True
    assert metrics["dominant_action_rate_reported"] is True
    assert metrics["supporting_prior_deletion_effect"] is True
    assert metrics["outcome_perturbation_effect"] is True


def test_006_execute_replays_full_n_distribution_and_writes_artifacts(tmp_path):
    result = run_parametric_action_expansion_006_execute(tmp_path, candidate_option_count=24)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})

    replay = result["behavior_only_replay"]
    assert replay["passed"] is True
    assert replay["match_rate"] == 1.0
    assert replay["replay_rule"] == "max probability over full N-option distribution"
    assert replay["candidate_option_count"] == 24
    assert replay["forbidden_fields_used"] == []

    first_trace = json.loads(
        (tmp_path / "action_distribution_trace.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    assert len(first_trace["action_distribution"]["distribution"]) == 24
    assert first_trace["selected_option_id"].startswith("option_")

    persisted = json.loads(
        (tmp_path / "parametric_action_expansion_006_result.json").read_text(encoding="utf-8")
    )
    assert persisted["verdict"] == result["verdict"]
    assert persisted["metrics"]["candidate_option_count"] == 24


def test_006_execute_baselines_share_same_anonymous_options_and_do_not_match(tmp_path):
    result = run_parametric_action_expansion_006_execute(tmp_path, candidate_option_count=24)
    baselines = result["baseline_comparison"]

    assert baselines["receive_same_anonymous_candidate_options"] is True
    assert baselines["baseline_outputs_visible_to_selector"] is False
    assert baselines["semantic_labels_visible_to_baselines"] is False
    assert baselines["rag_summary_memory"]["causal_probe_match_rate"] < 0.5
    assert baselines["strong_human_like_heuristic"]["causal_probe_match_rate"] < 0.5
    assert baselines["expanded_contextual_heuristic"]["causal_probe_match_rate"] < 0.5
    assert baselines["expanded_action_frequency"]["match_rate"] < 0.5
    assert baselines["expanded_action_nearest_neighbor"]["match_rate"] < 0.5


def test_006_execute_preserves_evidence_boundaries_and_no_patch_rules(tmp_path):
    result = run_parametric_action_expansion_006_execute(tmp_path, candidate_option_count=24)

    assert result["evidence_preservation"]["preserve_003_as"] == (
        "small-action-set free-input causal-probe evidence only"
    )
    assert result["evidence_preservation"]["preserve_005_shadow_as"] == (
        "N=7 shadow compatibility evidence only"
    )
    assert result["evidence_preservation"]["rewrite_003_or_005_as_expanded_evidence"] is False
    assert result["selector_patched"] is False
    assert result["thresholds_changed"] is False
    assert result["rag_baseline_weakened"] is False
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["llm_action_selection"] is False


def test_006_execute_source_has_no_fixed_twenty_or_n_specific_branches():
    import cmbc_companion.demos.parametric_action_expansion_006_execute as module

    source = inspect.getsource(module)
    forbidden_snippets = [
        "ACTION_HANDLES = 20",
        "range(20)",
        "if N == 20",
        "if N == 7",
        "if option_count == 20",
        "if option_count == 7",
        "if candidate_option_count == 20",
        "if candidate_option_count == 7",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in source
