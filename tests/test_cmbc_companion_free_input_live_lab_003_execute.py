import json
from pathlib import Path

from cmbc_companion.demos.free_input_live_lab_003_execute import (
    ALLOWED_VERDICTS,
    run_free_input_live_lab_003,
)


REQUIRED_ARTIFACTS = {
    "FREE_INPUT_LIVE_LAB_003_STATUS.md",
    "freeze_manifest.json",
    "free_input_transcript.jsonl",
    "outcome_coding_ledger.jsonl",
    "causal_probe_extraction_report.json",
    "causal_probe_results.json",
    "baseline_comparison_report.json",
    "supporting_prior_deletion_report.json",
    "outcome_perturbation_report.json",
    "renderer_isolation_report.md",
    "behavior_only_replay.json",
    "free_input_live_lab_003_result.json",
}


def test_free_input_live_lab_003_execute_stops_cleanly_without_human_input(tmp_path):
    result = run_free_input_live_lab_003(tmp_path)

    assert result["suite_id"] == "CMBC-COMPANION-FREE-INPUT-LIVE-LAB-003-EXECUTE"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "free_input_probe_extraction_failed"
    assert result["stop_conditions"] == ["free_input_cannot_form_stable_causal_probes"]
    assert result["free_input_capture"]["free_input_turn_count"] == 0
    assert result["free_input_capture"]["input_source"] == "missing_free_input_human_operator_transcript"
    assert result["causal_probe_extraction"]["causal_probe_case_count"] == 0
    assert result["causal_probe_extraction"]["stable_causal_probes_formed"] is False


def test_free_input_live_lab_003_execute_preserves_authorization_boundaries(tmp_path):
    result = run_free_input_live_lab_003(tmp_path)

    assert result["execution_scope"] == "bounded_execution_only"
    assert result["implementation_authorized"] is False
    assert result["selector_patched"] is False
    assert result["thresholds_changed"] is False
    assert result["rag_baseline_weakened"] is False
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["llm_action_selection"] is False
    assert result["claim_after_execution"] == (
        "bounded free-input live-lab execution attempted; no free-input evidence because no human transcript was available"
    )


def test_free_input_live_lab_003_execute_reports_required_metrics_as_unscored(tmp_path):
    result = run_free_input_live_lab_003(tmp_path)
    metrics = result["metrics"]

    assert metrics["free_input_turn_count"] == 0
    assert metrics["causal_probe_case_count"] == 0
    assert metrics["rag_visible_action_match_rate"] is None
    assert metrics["rag_causal_probe_match_rate"] is None
    assert metrics["strong_heuristic_causal_probe_match_rate"] is None
    assert metrics["expanded_contextual_heuristic_causal_probe_match_rate"] is None
    assert metrics["renderer_action_change_rate"] is None
    assert metrics["behavior_only_replay_match_rate"] is None
    assert metrics["supporting_prior_deletion_effect"] is None
    assert metrics["outcome_perturbation_effect"] is None
    assert result["minimum_gates_satisfied"] is False


def test_free_input_live_lab_003_execute_writes_required_artifacts(tmp_path):
    result = run_free_input_live_lab_003(tmp_path)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    with (tmp_path / "free_input_live_lab_003_result.json").open("r", encoding="utf-8") as fh:
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


def test_free_input_live_lab_003_execute_stops_when_user_text_has_no_outcome_coding(tmp_path):
    input_path = tmp_path / "free_input.jsonl"
    with input_path.open("w", encoding="utf-8") as fh:
        for idx in range(20):
            row = {
                "turn_id": f"free_{idx + 1:03d}",
                "free_input_text": f"user free input {idx + 1}",
                "input_source": "free_input_human_operator",
                "feedback_label": "unspecified",
                "context_hint": "unspecified",
            }
            fh.write(json.dumps(row, sort_keys=True) + "\n")

    result = run_free_input_live_lab_003(tmp_path, input_path)

    assert result["verdict"] == "outcome_coding_unstable"
    assert result["stop_conditions"] == ["outcome_coding_unstable"]
    assert result["free_input_capture"]["free_input_turn_count"] == 20
    assert result["free_input_capture"]["input_source"] == "free_input_human_operator"
    assert result["outcome_coding"]["outcome_coding_ledger_count"] == 0
    assert result["outcome_coding"]["outcome_coding_stable"] is False
    assert result["causal_probe_extraction"]["stable_causal_probes_formed"] is False
    assert result["causal_probe_extraction"]["failure_reason"] == "outcome_coding_unstable"
    assert result["claim_after_execution"] == (
        "bounded free-input live-lab execution attempted; no causal-probe evidence "
        "because feedback/outcome coding was unavailable or unstable"
    )

    with (tmp_path / "free_input_transcript.jsonl").open("r", encoding="utf-8") as fh:
        transcript_rows = [json.loads(line) for line in fh if line.strip()]
    assert len(transcript_rows) == 20


def test_free_input_live_lab_003_execute_treats_pending_feedback_as_uncoded(tmp_path):
    input_path = tmp_path / "pending_feedback_input.jsonl"
    with input_path.open("w", encoding="utf-8") as fh:
        for idx in range(20):
            row = {
                "turn_id": f"free_{idx + 1:03d}",
                "free_input_text": f"user free input {idx + 1}",
                "input_source": "free_input_human_operator",
                "feedback_label": "pending_outcome_coding",
                "feedback_status": "pending",
                "context_hint": "free_time",
            }
            fh.write(json.dumps(row, sort_keys=True) + "\n")

    result = run_free_input_live_lab_003(tmp_path, input_path)

    assert result["verdict"] == "outcome_coding_unstable"
    assert result["stop_conditions"] == ["outcome_coding_unstable"]
    assert result["outcome_coding"]["outcome_coding_ledger_count"] == 0
    assert result["outcome_coding"]["uncoded_turn_count"] == 20
    assert result["outcome_coding"]["outcome_coding_stable"] is False
