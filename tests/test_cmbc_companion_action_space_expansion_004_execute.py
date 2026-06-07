import json

from cmbc_companion.demos.action_space_expansion_004_execute import (
    ALLOWED_VERDICTS,
    run_action_space_expansion_004_execute,
)


REQUIRED_ARTIFACTS = {
    "ACTION_SPACE_EXPANSION_004_STATUS.md",
    "freeze_manifest.json",
    "expanded_action_space_manifest.json",
    "anonymous_action_handle_permutation.json",
    "semantic_label_leak_scan.json",
    "label_permutation_report.json",
    "effect_swap_report.json",
    "causal_probe_results.json",
    "action_distribution_entropy_report.json",
    "dominant_action_rate_report.json",
    "baseline_comparison_report.json",
    "renderer_isolation_report.md",
    "behavior_only_replay.json",
    "action_space_expansion_004_result.json",
    "STOP_REPORT.md",
}


def test_action_space_expansion_004_execute_stops_cleanly_on_small_frozen_selector(tmp_path):
    result = run_action_space_expansion_004_execute(tmp_path)

    assert result["suite_id"] == "CMBC-COMPANION-ACTION-SPACE-EXPANSION-004-EXECUTE"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "small_action_set_only"
    assert result["minimum_gates_satisfied"] is False
    assert "candidate_action_count < 20" in result["stop_conditions"]
    assert "frozen_selector_not_parametric_over_action_space" in result["stop_conditions"]

    metrics = result["metrics"]
    assert metrics["requested_candidate_action_count"] == 20
    assert metrics["selector_visible_candidate_action_count"] == 7
    assert metrics["candidate_action_count"] == 7
    assert metrics["semantic_label_visible_to_selector"] is False
    assert metrics["rendered_text_visible_to_selector"] is False
    assert metrics["public_action_name_visible_to_selector"] is False
    assert metrics["label_permutation_change_rate"] is None
    assert metrics["effect_swap_change_rate"] is None
    assert metrics["behavior_only_replay_match_rate"] is None
    assert metrics["renderer_action_change_rate"] == 0.0


def test_action_space_expansion_004_execute_preserves_freeze_and_boundaries(tmp_path):
    result = run_action_space_expansion_004_execute(tmp_path)

    assert result["freeze_integrity"]["code_hashes_unchanged_after_execution"] is True
    assert result["execution_scope"] == "bounded_execution_only"
    assert result["implementation_authorized"] is False
    assert result["selector_patched"] is False
    assert result["thresholds_changed"] is False
    assert result["rag_baseline_weakened"] is False
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["llm_action_selection"] is False


def test_action_space_expansion_004_execute_records_attempted_expansion_without_label_leak(tmp_path):
    result = run_action_space_expansion_004_execute(tmp_path)
    action_space = result["expanded_action_space"]

    assert action_space["requested_candidate_action_count"] == 20
    assert len(action_space["requested_anonymous_action_handles"]) == 20
    assert action_space["selector_visible_candidate_action_count"] == 7
    assert action_space["expanded_action_space_executable_by_frozen_selector"] is False
    assert action_space["semantic_labels_exposed_to_selector"] is False
    assert action_space["rendered_text_exposed_to_selector"] is False
    assert action_space["public_action_names_exposed_to_selector"] is False
    assert action_space["natural_language_descriptions_exposed_to_selector"] is False
    assert action_space["action_family_names_exposed_to_selector"] is False

    leak_scan = result["semantic_label_leak_scan"]
    assert leak_scan["passed"] is True
    assert leak_scan["forbidden_fields_used"] == []


def test_action_space_expansion_004_execute_writes_required_failure_artifacts(tmp_path):
    result = run_action_space_expansion_004_execute(tmp_path)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    with (tmp_path / "action_space_expansion_004_result.json").open("r", encoding="utf-8") as fh:
        verdict = json.load(fh)
    assert verdict["verdict"] == result["verdict"]
    assert verdict["stop_conditions"] == result["stop_conditions"]
    assert verdict["authorization_boundary"] == {
        "ego_migration": "no_go",
        "real_companion_implementation": "not_authorized",
        "proactive_messages": "not_authorized",
        "llm_action_selection": False,
        "selector_patched": False,
        "thresholds_changed": False,
        "rag_baseline_weakened": False,
    }
