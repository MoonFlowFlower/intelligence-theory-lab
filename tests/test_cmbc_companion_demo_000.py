import json

from cmbc_companion.demos.lab_console_000 import ALLOWED_VERDICTS, run_lab_demo


def test_same_input_different_history_changes_visible_behavior(tmp_path):
    result = run_lab_demo(tmp_path)

    growth = result["observable_growth"]
    same_input = growth["same_input_different_history"]
    assert same_input["shared_user_event"] == "I had a hard day. Check in if it helps."
    assert same_input["base_history"]["selected_action"] != same_input["changed_history"]["selected_action"]
    assert same_input["base_history"]["visible_reply"] != same_input["changed_history"]["visible_reply"]
    assert same_input["base_history"]["supporting_prior_id"] != same_input["changed_history"]["supporting_prior_id"]
    assert growth["human_observable_growth_signal"] is True


def test_feedback_updates_next_similar_action_distribution(tmp_path):
    result = run_lab_demo(tmp_path)

    update = result["feedback_update"]
    assert update["feedback_written_as_outcome"] is True
    assert update["before_selected_action"] != update["after_selected_action"]
    assert update["target_action_probability_delta"] > 0.20
    assert update["distribution_kl"] > 0.05
    assert update["raw_text_memory_only"] is False


def test_supporting_prior_deletion_regresses_reply_strategy(tmp_path):
    result = run_lab_demo(tmp_path)

    deletion = result["prior_deletion"]
    assert deletion["deleted_actual_supporting_prior"] is True
    assert deletion["selected_action_changed"] is True
    assert deletion["supporting_prior_id"].startswith("prior_")
    assert deletion["deleted_visible_reply"] != deletion["baseline_visible_reply"]
    assert deletion["final_action_probability_drop"] > 0.20


def test_trace_schema_behavior_replay_and_renderer_isolation(tmp_path):
    result = run_lab_demo(tmp_path)

    replay = result["behavior_only_replay"]
    assert replay["passed"] is True
    assert replay["match_rate"] == 1.0
    assert replay["used_fields"] == [
        "observation",
        "anonymous_candidate_actions",
        "consolidated_prior_records",
        "prediction_before_action",
        "action_distribution",
        "selected_action",
        "prior_support_refs",
    ]
    assert replay["forbidden_fields_used"] == []

    renderer = result["renderer_isolation"]
    assert renderer["adversarial_renderer_action_change_rate"] == 0.0
    assert renderer["renderer_used_for_action_selection"] is False
    assert renderer["llm_action_selection"] is False

    required_trace_keys = {
        "observation",
        "anonymous_candidate_actions",
        "prediction_before_action",
        "action_distribution",
        "selected_action",
        "renderer_input",
        "supporting_prior",
    }
    for turn in result["demo_transcript"]:
        assert turn["visible_reply"]
        assert required_trace_keys.issubset(turn["developer_trace"])


def test_demo_covers_three_lab_scenarios_and_readable_explanations(tmp_path):
    result = run_lab_demo(tmp_path)

    scenarios = result["scenario_coverage"]
    assert scenarios["covered"] == [
        "proactive_wait_permission",
        "support_response_style",
        "boundary_refusal_alternative",
    ]
    assert scenarios["all_have_readable_reason"] is True
    for item in scenarios["examples"]:
        assert item["selected_action"] in item["reason"]
        assert item["supporting_prior_id"] in item["reason"]


def test_demo_artifacts_verdict_and_boundaries(tmp_path):
    result = run_lab_demo(tmp_path)

    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "demo_000_lab_only_bounded_pass"
    assert result["claim_boundary"] == "lab-only human-observable prototype cut"
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["llm_action_selection"] is False
    assert result["selector_patched"] is False
    assert result["implementation_authorized"] is False

    required = {
        "DEMO_000_STATUS.md",
        "demo_000_config.json",
        "demo_transcript.md",
        "demo_transcript.json",
        "developer_trace.jsonl",
        "behavior_only_replay.json",
        "prior_deletion_report.md",
        "renderer_isolation_report.md",
        "CMBC_COMPANION_DEMO_000_RESULT.md",
        "cmbc_companion_demo_000_result.json",
    }
    assert required.issubset({path.name for path in tmp_path.iterdir()})
    with (tmp_path / "cmbc_companion_demo_000_result.json").open("r", encoding="utf-8") as fh:
        verdict = json.load(fh)
    assert verdict["verdict"] == result["verdict"]
    assert verdict["claim_boundary"] == result["claim_boundary"]
