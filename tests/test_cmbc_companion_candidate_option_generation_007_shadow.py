import inspect
import json

from cmbc_companion.evals.candidate_option_generation_007_shadow import (
    ALLOWED_VERDICTS,
    build_candidate_option_proposals,
    run_candidate_option_generation_007_shadow,
)


REQUIRED_ARTIFACTS = {
    "CANDIDATE_OPTION_GENERATION_007_SHADOW_STATUS.md",
    "freeze_manifest.json",
    "candidate_option_proposals.jsonl",
    "option_admission_decisions.jsonl",
    "admitted_candidate_options.json",
    "option_lineage_traces.jsonl",
    "option_deduplication_report.json",
    "option_retirement_report.json",
    "option_replay_traces.jsonl",
    "generated_option_replay.json",
    "generator_selector_boundary_report.json",
    "baseline_comparison_report.json",
    "outcome_update_effect_report.json",
    "renderer_isolation_report.md",
    "evidence_preservation_report.json",
    "semantic_leak_scan.json",
    "candidate_option_generation_007_shadow_result.json",
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


def test_007_shadow_generates_admits_and_reports_required_metrics(tmp_path):
    result = run_candidate_option_generation_007_shadow(tmp_path, generated_option_count=24)

    assert result["suite_id"] == "CMBC-COMPANION-CANDIDATE-OPTION-GENERATION-007-SHADOW"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "candidate_option_generation_shadow_bounded_pass"
    assert result["execution_scope"] == "bounded_shadow_implementation_only"

    metrics = result["metrics"]
    assert metrics["generated_option_count"] == 24
    assert metrics["admitted_option_count"] >= 20
    assert metrics["generator_selected_action"] is False
    assert metrics["semantic_label_visible_to_selector"] is False
    assert metrics["natural_language_description_visible_to_selector"] is False
    assert metrics["option_lineage_coverage_rate"] == 1.0
    assert metrics["option_replay_match_rate"] == 1.0
    assert metrics["generator_baseline_action_match_rate"] < 0.5
    assert metrics["rag_causal_probe_match_rate"] < 0.5
    assert metrics["strong_heuristic_causal_probe_match_rate"] < 0.5
    assert metrics["expanded_action_nearest_neighbor_match_rate"] < 0.5
    assert metrics["renderer_action_change_rate"] == 0.0
    assert metrics["outcome_update_changes_future_option_distribution"] is True
    assert result["minimum_gates_satisfied"] is True
    assert result["stop_conditions"] == []


def test_007_shadow_proposals_keep_generator_text_out_of_selector_input(tmp_path):
    result = run_candidate_option_generation_007_shadow(tmp_path, generated_option_count=24)

    proposals = [
        json.loads(line)
        for line in (tmp_path / "candidate_option_proposals.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(proposals) == result["metrics"]["generated_option_count"]
    assert all("generator_visible_description" in proposal for proposal in proposals)
    assert all("selector_visible_payload" in proposal for proposal in proposals)

    replay_lines = (tmp_path / "option_replay_traces.jsonl").read_text(encoding="utf-8").splitlines()
    first_trace = json.loads(replay_lines[0])
    selector_blob = json.dumps(first_trace["selector_input"], ensure_ascii=False, sort_keys=True)
    for token in FORBIDDEN_SELECTOR_TOKENS:
        assert token not in selector_blob

    boundary = result["generator_selector_boundary"]
    assert boundary["generator_may_propose"] is True
    assert boundary["generator_selected_action"] is False
    assert boundary["selector_receives_only_admitted_options"] is True
    assert boundary["proposal_text_visible_to_selector"] is False
    assert boundary["rag_text_visible_to_selector"] is False
    assert boundary["renderer_text_visible_to_selector"] is False
    assert boundary["llm_output_visible_to_selector"] is False


def test_007_shadow_lineage_admission_replay_and_outcome_update_are_auditable(tmp_path):
    result = run_candidate_option_generation_007_shadow(tmp_path, generated_option_count=24)

    admitted = json.loads((tmp_path / "admitted_candidate_options.json").read_text(encoding="utf-8"))
    lineage = [
        json.loads(line)
        for line in (tmp_path / "option_lineage_traces.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    replay = result["generated_option_replay"]
    update = result["outcome_update_effect"]

    assert len(admitted) == result["metrics"]["admitted_option_count"]
    assert len(lineage) == len(admitted)
    assert all(option["lineage_trace_ref"] for option in admitted)
    assert all(option["evidence_support_ref"] for option in admitted)
    assert all("uncertainty" in option for option in admitted)
    assert all(trace["source_context_refs"] for trace in lineage)
    assert all(trace["source_outcome_refs"] for trace in lineage)

    assert replay["passed"] is True
    assert replay["match_rate"] == 1.0
    assert replay["replay_rule"] == "max probability over admitted generated-option distribution"
    assert replay["forbidden_fields_used"] == []

    assert update["outcome_update_changes_future_option_distribution"] is True
    assert update["admission_status_changed"] is True
    assert update["scoring_changed"] is True
    assert update["pre_update_selected_option_id"] != update["post_update_selected_option_id"]


def test_007_shadow_baselines_renderer_and_evidence_boundaries(tmp_path):
    result = run_candidate_option_generation_007_shadow(tmp_path, generated_option_count=24)

    baselines = result["baseline_comparison"]
    assert baselines["receive_same_admitted_anonymous_options"] is True
    assert baselines["generator_baseline"]["action_match_rate"] < 0.5
    assert baselines["rag_summary_memory"]["causal_probe_match_rate"] < 0.5
    assert baselines["strong_human_like_heuristic"]["causal_probe_match_rate"] < 0.5
    assert baselines["expanded_action_nearest_neighbor"]["match_rate"] < 0.5
    assert baselines["baseline_outputs_visible_to_selector"] is False

    renderer = result["renderer_isolation"]
    assert renderer["renderer_runs_after_selection"] is True
    assert renderer["renderer_used_for_action_selection"] is False
    assert renderer["adversarial_renderer_action_change_rate"] == 0.0
    assert renderer["llm_action_selection"] is False

    preservation = result["evidence_preservation"]
    assert preservation["preserve_003_as"] == "small-action-set free-input causal-probe evidence only"
    assert preservation["preserve_005_as"] == "N=7 shadow compatibility evidence only"
    assert preservation["preserve_006_as"] == "bounded N=24 prebuilt CandidateOption evidence only"
    assert preservation["rewrite_prior_evidence_as_generated_option_evidence"] is False


def test_007_shadow_writes_artifacts_and_preserves_no_patch_boundaries(tmp_path):
    result = run_candidate_option_generation_007_shadow(tmp_path, generated_option_count=24)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    persisted = json.loads(
        (tmp_path / "candidate_option_generation_007_shadow_result.json").read_text(encoding="utf-8")
    )
    assert persisted["verdict"] == result["verdict"]
    assert persisted["metrics"]["generated_option_count"] == 24

    assert result["selector_patched"] is False
    assert result["thresholds_changed"] is False
    assert result["rag_baseline_weakened"] is False
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["llm_action_selection"] is False
    assert result["claim_after_shadow"] == (
        "bounded generated CandidateOption shadow evidence only; not real companion readiness"
    )


def test_007_shadow_generation_is_variable_count_not_fixed_recipe_table():
    proposals_24 = build_candidate_option_proposals(24)
    proposals_31 = build_candidate_option_proposals(31)

    assert len(proposals_24) == 24
    assert len(proposals_31) == 31
    assert [proposal["proposed_option_id"] for proposal in proposals_24] != [
        proposal["proposed_option_id"] for proposal in proposals_31
    ]

    import cmbc_companion.evals.candidate_option_generation_007_shadow as module

    source = inspect.getsource(module)
    forbidden_snippets = [
        "ACTION_HANDLES = 20",
        "range(20)",
        "range(24)",
        "if generated_option_count == 20",
        "if generated_option_count == 24",
        "if option_count == 20",
        "if option_count == 24",
        "fixed_generated_options",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in source
