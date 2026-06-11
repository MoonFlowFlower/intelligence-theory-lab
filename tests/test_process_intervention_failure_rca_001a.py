import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "process_intervention_failure_rca_001a" / "result.json"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_rca_artifact_is_json_parseable_and_bounded():
    result = _read_json(ARTIFACT)

    assert result["task_id"] == "PROCESS-INTERVENTION-FAILURE-RCA-001A"
    assert result["layer"] == "bounded failure attribution only"
    assert result["claim_ceiling"] == "bounded process-intervention 001B failure attribution only"
    assert result["most_likely_failure_class"] == "task_distribution_weak"
    assert "implementation_underpowered" in result["plausible_alternative_failure_classes"]
    assert result["predecessor_failure_summary"]["bounded_pass"] is False
    assert result["predecessor_failure_summary"]["verdict"] == (
        "process_intervention_preflight_001b_failed_control_separation_statistic_match"
    )


def test_rca_authorizes_nothing_and_preserves_negative_evidence_boundary():
    result = _read_json(ARTIFACT)

    assert all(value is False for value in result["authorization_flags"].values())
    assert result["conditional_next_step_recommendation"]["authorization_granted_by_this_rca"] is False
    assert "Gate1 authorization" in result["conditional_next_step_recommendation"]["forbidden_as_next_step_from_this_artifact"]
    assert "new mechanism implementation" in result["conditional_next_step_recommendation"]["forbidden_as_next_step_from_this_artifact"]
    assert "mechanism validity" in result["what_this_does_not_prove"]
    assert "model-class reset necessity" in result["what_this_does_not_prove"]


def test_rca_identifies_matched_controls_and_failure_channels():
    result = _read_json(ARTIFACT)

    matched = {row["control_name"]: row for row in result["matched_fair_controls"]}
    assert set(matched) == {
        "online_count_statistic",
        "count_table",
        "graph_cache",
        "transition_table",
        "successor_map",
        "trace_only_replay",
        "behavior_only_replay",
    }
    for row in matched.values():
        assert row["match_rate"] == 1.0
        assert row["update_trace_match_rate"] == 1.0
        assert row["later_behavior_match_rate"] == 1.0
        assert row["separation_margin"] == 0.0

    channels = result["failure_channel_attribution"]
    assert channels["primary_driver"] == "statistic_count_shortcut"
    assert channels["behavior_level_equivalence"]["present"] is True
    assert channels["intervention_response_equivalence"]["present"] is True
    assert channels["statistic_count_shortcut"]["present"] is True
    assert channels["state_delta_or_update_trace_equivalence"]["present"] == "metric-level only"


def test_rca_matrix_covers_all_candidate_failure_classes():
    result = _read_json(ARTIFACT)

    matrix = {row["candidate_failure_class"]: row for row in result["rca_matrix"]}
    assert set(matrix) == {
        "mechanism_absent",
        "implementation_underpowered",
        "task_distribution_weak",
        "evidence_gate_mismatch",
        "mixed_or_ambiguous",
    }
    assert matrix["task_distribution_weak"]["classification"] == "most_likely"
    assert matrix["implementation_underpowered"]["classification"] == "plausible_alternative"
    assert matrix["mechanism_absent"]["classification"] == "not_established"


def test_rca_defines_distinguishing_evidence_without_authorization():
    result = _read_json(ARTIFACT)

    distinguishing = result["distinguishing_evidence_needed"]
    assert set(distinguishing) == {
        "model_class_reset",
        "implementation_revision",
        "harder_task_distribution",
    }
    for branch in distinguishing.values():
        assert branch["authorization_status"] == "not_authorized"
        assert branch["would_require"]
        assert branch["insufficient_evidence"]


def test_frozen_001b_and_support_pack_inputs_remain_byte_identical():
    result = _read_json(ARTIFACT)

    for relative_path, expected_hash in result["frozen_input_sha256"].items():
        assert _sha256(ROOT / relative_path) == expected_hash
