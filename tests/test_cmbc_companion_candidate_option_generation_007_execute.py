import inspect
import json

from cmbc_companion.demos.candidate_option_generation_007_execute import (
    ALLOWED_VERDICTS,
    run_candidate_option_generation_007_execute,
)
from cmbc_companion.evals.candidate_option_generation_007_shadow import (
    build_candidate_option_proposals,
)


REQUIRED_ARTIFACTS = {
    "CANDIDATE_OPTION_GENERATION_007_EXECUTE_STATUS.md",
    "freeze_manifest.json",
    "candidate_option_proposals.jsonl",
    "option_admission_decisions.jsonl",
    "admitted_candidate_options.json",
    "option_lineage_traces.jsonl",
    "parametric_selector_input_trace.jsonl",
    "prediction_before_action_trace.jsonl",
    "action_distribution_trace.jsonl",
    "causal_probe_results.json",
    "supporting_prior_deletion_report.json",
    "outcome_perturbation_report.json",
    "outcome_update_effect_report.json",
    "behavior_only_replay.json",
    "generator_selector_boundary_report.json",
    "baseline_comparison_report.json",
    "renderer_isolation_report.md",
    "semantic_leak_scan.json",
    "evidence_preservation_report.json",
    "candidate_option_generation_007_execute_result.json",
}


FORBIDDEN_SELECTOR_TOKENS = [
    "generator_visible_description",
    "natural_language_description",
    "semantic_action_label",
    "public_action_name",
    "action_family_name",
    "rag_text",
    "renderer_text",
    "rendered_text",
    "llm_output",
    "oracle_effect",
    "evaluator_metric",
    "baseline_output",
]


def test_007_execute_runs_generated_options_through_causal_probe_gates(tmp_path):
    result = run_candidate_option_generation_007_execute(tmp_path, generated_option_count=24)

    assert result["suite_id"] == "CMBC-COMPANION-CANDIDATE-OPTION-GENERATION-007-EXECUTE"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "candidate_option_generation_execute_causal_probe_failed"
    assert result["execution_scope"] == "bounded_execution_only"
    assert result["minimum_gates_satisfied"] is False
    assert result["stop_conditions"] == ["feedback_admission_single_contradiction_failed"]

    metrics = result["metrics"]
    assert metrics["generated_option_count"] == 24
    assert metrics["admitted_option_count"] >= 20
    assert metrics["generator_selected_action"] is False
    assert metrics["semantic_label_visible_to_selector"] is False
    assert metrics["natural_language_description_visible_to_selector"] is False
    assert metrics["option_lineage_coverage_rate"] == 1.0
    assert metrics["option_replay_match_rate"] == 1.0
    assert metrics["behavior_only_replay_match_rate"] == 1.0
    assert metrics["generator_baseline_action_match_rate"] < 0.5
    assert metrics["rag_causal_probe_match_rate"] < 0.5
    assert metrics["strong_heuristic_causal_probe_match_rate"] < 0.5
    assert metrics["expanded_action_nearest_neighbor_match_rate"] < 0.5
    assert metrics["renderer_action_change_rate"] == 0.0
    assert metrics["outcome_update_changes_future_option_distribution"] is True
    assert metrics["supporting_prior_deletion_effect"] is True
    assert metrics["outcome_perturbation_effect"] is True
    assert metrics["feedback_admission_single_contradiction_passed"] is False


def test_007_execute_selector_uses_only_admitted_anonymous_options(tmp_path):
    result = run_candidate_option_generation_007_execute(tmp_path, generated_option_count=24)

    proposals = [
        json.loads(line)
        for line in (tmp_path / "candidate_option_proposals.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    admitted = json.loads((tmp_path / "admitted_candidate_options.json").read_text(encoding="utf-8"))
    assert len(proposals) == result["metrics"]["generated_option_count"]
    assert len(admitted) == result["metrics"]["admitted_option_count"]
    assert all("generator_visible_description" in proposal for proposal in proposals)

    first_trace = json.loads(
        (tmp_path / "parametric_selector_input_trace.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    selector_blob = json.dumps(first_trace["selector_input"], ensure_ascii=False, sort_keys=True)
    for token in FORBIDDEN_SELECTOR_TOKENS:
        assert token not in selector_blob

    boundary = result["generator_selector_boundary"]
    assert boundary["generator_selected_action"] is False
    assert boundary["generator_ranked_final_actions"] is False
    assert boundary["selector_receives_only_admitted_options"] is True
    assert boundary["proposal_text_visible_to_selector"] is False
    assert boundary["rag_text_visible_to_selector"] is False
    assert boundary["renderer_text_visible_to_selector"] is False
    assert boundary["llm_output_visible_to_selector"] is False


def test_007_execute_replay_deletion_perturbation_and_baselines(tmp_path):
    result = run_candidate_option_generation_007_execute(tmp_path, generated_option_count=24)

    replay = result["behavior_only_replay"]
    assert replay["passed"] is True
    assert replay["match_rate"] == 1.0
    assert replay["replay_rule"] == "max probability over full generated CandidateOption distribution"
    assert replay["forbidden_fields_used"] == []

    deletion = result["supporting_prior_deletion"]
    perturbation = result["outcome_perturbation"]
    assert deletion["effect"] is True
    assert deletion["selected_action_changed"] or deletion["target_probability_drop"] > 0.0
    assert perturbation["effect"] is True
    assert perturbation["selected_action_changed"] or perturbation["distribution_changed"] is True

    baselines = result["baseline_comparison"]
    assert baselines["receive_same_admitted_anonymous_options"] is True
    assert baselines["baseline_outputs_visible_to_selector"] is False
    assert baselines["generator_baseline"]["action_match_rate"] < 0.5
    assert baselines["rag_summary_memory"]["causal_probe_match_rate"] < 0.5
    assert baselines["strong_human_like_heuristic"]["causal_probe_match_rate"] < 0.5
    assert baselines["expanded_action_nearest_neighbor"]["match_rate"] < 0.5


def test_007_execute_renderer_evidence_boundaries_and_artifacts(tmp_path):
    result = run_candidate_option_generation_007_execute(tmp_path, generated_option_count=24)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})

    renderer = result["renderer_isolation"]
    assert renderer["renderer_runs_after_selection"] is True
    assert renderer["renderer_used_for_action_selection"] is False
    assert renderer["adversarial_renderer_action_change_rate"] == 0.0
    assert renderer["llm_action_selection"] is False

    preservation = result["evidence_preservation"]
    assert preservation["preserve_003_as"] == "small-action-set free-input causal-probe evidence only"
    assert preservation["preserve_005_as"] == "N=7 shadow compatibility evidence only"
    assert preservation["preserve_006_as"] == "bounded N=24 prebuilt CandidateOption evidence only"
    assert preservation["preserve_007_shadow_as"] == "bounded generated-option shadow evidence only"
    assert preservation["rewrite_prior_evidence_as_generated_option_evidence"] is False

    persisted = json.loads(
        (tmp_path / "candidate_option_generation_007_execute_result.json").read_text(encoding="utf-8")
    )
    assert persisted["verdict"] == result["verdict"]
    assert persisted["claim_after_execute"] == (
        "bounded generated CandidateOption execution attempted; causal-probe gate failed"
    )


def test_007_execute_preserves_no_patch_authorization_boundaries(tmp_path):
    result = run_candidate_option_generation_007_execute(tmp_path, generated_option_count=24)

    assert result["selector_patched"] is False
    assert result["thresholds_changed"] is False
    assert result["rag_baseline_weakened"] is False
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["llm_action_selection"] is False
    assert result["claim_after_execute"] == (
        "bounded generated CandidateOption execution attempted; causal-probe gate failed"
    )


def test_007_execute_does_not_use_fixed_generated_recipe_table():
    proposals_24 = build_candidate_option_proposals(24)
    proposals_31 = build_candidate_option_proposals(31)
    assert len(proposals_24) == 24
    assert len(proposals_31) == 31
    assert [proposal["proposed_option_id"] for proposal in proposals_24] != [
        proposal["proposed_option_id"] for proposal in proposals_31
    ]

    import cmbc_companion.demos.candidate_option_generation_007_execute as module

    source = inspect.getsource(module)
    forbidden_snippets = [
        "ACTION_HANDLES = 20",
        "range(20)",
        "range(24)",
        "if generated_option_count == 20",
        "if generated_option_count == 24",
        "fixed_generated_options",
        "semantic_action_label",
        "natural_language_description",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in source
