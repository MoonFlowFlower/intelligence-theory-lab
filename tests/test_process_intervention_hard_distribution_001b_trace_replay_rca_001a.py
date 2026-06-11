import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "process_intervention_hard_distribution_001b_trace_replay_rca_001a"
TASK_CARD = (
    ROOT
    / "docs"
    / "codex"
    / "tasks"
    / "PROCESS-INTERVENTION-HARD-DISTRIBUTION-001B-TRACE-REPLAY-RCA-001A.md"
)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_trace_replay_rca_artifacts_exist_and_are_bounded():
    assert TASK_CARD.exists()
    result = _read_json(ARTIFACT_DIR / "replay_control_adjudication.json")

    assert result["task_id"] == "PROCESS-INTERVENTION-HARD-DISTRIBUTION-001B-TRACE-REPLAY-RCA-001A"
    assert result["layer"] == "bounded replay-control adjudication only"
    assert result["claim_ceiling"] == "bounded replay-control adjudication only"
    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == result["claim_ceiling"]
    assert all(value is False for value in result["authorization_flags"].values())


def test_trace_replay_rca_preserves_old_001b_artifacts_and_verdict():
    result = _read_json(ARTIFACT_DIR / "replay_control_adjudication.json")

    assert result["historical_001b_verdict_preserved"] is True
    assert result["historical_001b_verdict"] == "process_intervention_hard_distribution_001b_failed_fair_control_match"
    assert result["does_not_rewrite_001b_verdict"] is True
    assert result["does_not_remove_trace_only_replay_from_historical_failure_condition"] is True
    assert result["does_not_reinterpret_001b_as_pass"] is True

    for relative_path, expected_hash in result["frozen_001b_input_sha256"].items():
        assert _sha256(ROOT / relative_path) == expected_hash


def test_trace_only_replay_access_is_classified_as_trace_integrity_hygiene():
    result = _read_json(ARTIFACT_DIR / "replay_control_adjudication.json")
    trace_only = result["replay_control_classification"]["trace_only_replay"]

    assert trace_only["classification"] == "trace_integrity_hygiene"
    assert trace_only["used_committed_target_trace_records"] is True
    assert trace_only["used_target_outcomes"] is True
    assert trace_only["used_target_future_behaviors"] is True
    assert trace_only["used_target_process_signatures"] is True
    assert trace_only["made_heldout_generative_prediction_without_target_trace_access"] is False
    assert trace_only["valid_independent_mechanism_challenger"] is False
    assert trace_only["historical_failure_condition_preserved"] is True
    assert trace_only["match_rate"] == 1.0
    assert trace_only["heldout_match_rate"] == 1.0


def test_behavior_replay_and_non_replay_controls_are_distinguished():
    result = _read_json(ARTIFACT_DIR / "replay_control_adjudication.json")
    behavior = result["replay_control_classification"]["behavior_only_replay"]
    non_replay = result["non_replay_fair_control_summary"]

    assert behavior["classification"] == "behavioral_replay_baseline"
    assert behavior["used_observed_behavior_records"] is True
    assert behavior["update_trace_match_rate"] == 0.0
    assert behavior["valid_independent_mechanism_challenger"] is False

    assert non_replay["best_non_replay_control"] == "count_table"
    assert non_replay["best_non_replay_match_rate"] == 0.4166666666666667
    assert non_replay["best_non_replay_heldout_match_rate"] == 0.0
    assert non_replay["non_replay_controls_no_longer_perfectly_match"] is True


def test_future_gate_recommendation_is_conditional_only():
    result = _read_json(ARTIFACT_DIR / "replay_control_adjudication.json")
    recommendation = result["conditional_future_gate_recommendation"]

    assert recommendation["authorization_granted_by_this_rca"] is False
    assert recommendation["gate1_authorized"] is False
    assert recommendation["bridge_authorized"] is False
    assert recommendation["ego_authorized"] is False
    assert recommendation["model_class_reset_authorized"] is False
    assert recommendation["mechanism_implementation_authorized"] is False
    assert "generative_replay_challenger" in recommendation["future_gate_if_authorized"]
    assert result["acceptance_gate_status"]["future_gate_recommendation_conditional_only"] is True
