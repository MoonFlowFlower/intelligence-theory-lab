import json

from cmbc_companion.evals.parametric_action_interface_005_shadow import (
    ALLOWED_VERDICTS,
    run_parametric_action_interface_005_shadow,
)


REQUIRED_ARTIFACTS = {
    "PARAMETRIC_ACTION_INTERFACE_005_SHADOW_STATUS.md",
    "shadow_manifest.json",
    "old_003_lineage_manifest.json",
    "option_id_mapping.json",
    "parametric_replay_traces.jsonl",
    "replay_comparison_report.json",
    "distribution_delta_report.json",
    "semantic_leak_scan.json",
    "renderer_adapter_shadow_report.md",
    "expanded_baseline_shadow_report.json",
    "shadow_result.json",
}


def test_005_shadow_reproduces_old_003_replay_with_n7_only(tmp_path):
    result = run_parametric_action_interface_005_shadow(tmp_path)

    assert result["suite_id"] == "CMBC-COMPANION-PARAMETRIC-ACTION-INTERFACE-005-SHADOW-IMPLEMENT"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "parametric_shadow_n7_compatibility_pass"
    assert result["execution_scope"] == "n7_shadow_compatibility_only"
    assert result["candidate_option_count"] == 7
    assert result["n_gte_20_executed"] is False
    assert result["old_003_lineage"]["source_verdict"] == "free_input_causal_probe_bounded_pass"
    assert result["old_003_lineage"]["relabel_old_003_as_parametric_evidence"] is False

    replay = result["replay_comparison"]
    assert replay["old_replay_match_rate"] == 1.0
    assert replay["parametric_replay_match_rate"] == 1.0
    assert replay["selected_action_mismatch_count"] == 0
    assert replay["decision_count"] == 10


def test_005_shadow_uses_opaque_options_without_selector_label_leaks(tmp_path):
    result = run_parametric_action_interface_005_shadow(tmp_path)

    mapping = result["option_mapping"]
    assert sorted(mapping["old_action_handles"]) == [
        "act_0",
        "act_1",
        "act_2",
        "act_3",
        "act_4",
        "act_5",
        "act_6",
    ]
    assert all(option_id.startswith("option_") for option_id in mapping["opaque_option_ids"])
    assert mapping["semantic_labels_visible_to_selector"] is False
    assert mapping["public_action_names_visible_to_selector"] is False
    assert mapping["rendered_text_visible_to_selector"] is False

    leak = result["semantic_leak_scan"]
    assert leak["passed"] is True
    assert leak["forbidden_fields_used"] == []
    assert leak["selector_visible_field_names"] == [
        "observation",
        "candidate_options",
        "own_intervention_history",
        "observed_outcomes",
        "goal_constraint_vector",
        "public_horizon",
        "public_budget",
    ]

    first_trace = json.loads((tmp_path / "parametric_replay_traces.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert first_trace["selected_option_id"].startswith("option_")
    serialized_selector_input = json.dumps(first_trace["candidate_options"], ensure_ascii=False)
    assert "act_" not in serialized_selector_input
    assert "PUBLIC_ACTION_NAMES" not in serialized_selector_input
    assert "rendered_text" not in serialized_selector_input


def test_005_shadow_reports_distribution_delta_renderer_and_baseline_boundaries(tmp_path):
    result = run_parametric_action_interface_005_shadow(tmp_path)

    distribution = result["distribution_delta_report"]
    assert distribution["distribution_delta_reported"] is True
    assert distribution["max_probability_abs_delta"] == 0.0
    assert distribution["max_distribution_kl"] == 0.0
    assert distribution["selected_rank_mismatch_count"] == 0

    renderer = result["renderer_adapter_shadow"]
    assert renderer["renderer_runs_after_selection"] is True
    assert renderer["renderer_used_for_action_selection"] is False
    assert renderer["adversarial_renderer_action_change_rate"] == 0.0

    baselines = result["expanded_baseline_shadow"]
    assert baselines["baselines_receive_same_anonymous_options"] is True
    assert baselines["baseline_outputs_visible_to_selector"] is False
    assert baselines["semantic_labels_visible_to_baselines"] is False
    assert baselines["executed_for_equivalence"] is False
    assert baselines["not_run_reason"] == "n7_shadow_checks_interface_compatibility_not_baseline_equivalence"


def test_005_shadow_preserves_boundaries_and_writes_required_artifacts(tmp_path):
    result = run_parametric_action_interface_005_shadow(tmp_path)

    assert result["selector_patched"] is False
    assert result["action_handles_patched"] is False
    assert result["thresholds_changed"] is False
    assert result["rag_baseline_weakened"] is False
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["llm_action_selection"] is False
    assert result["claim_after_shadow"] == (
        "parametric interface N=7 shadow compatibility evidence only; no expanded action-space evidence"
    )

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    persisted = json.loads((tmp_path / "shadow_result.json").read_text(encoding="utf-8"))
    assert persisted["verdict"] == result["verdict"]
    assert persisted["n_gte_20_executed"] is False
