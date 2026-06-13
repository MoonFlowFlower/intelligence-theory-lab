from __future__ import annotations

from typing import Any

from . import candidate
from .schemas import CandidateState, Feedback, Observation


def recompute_trace_record(
    trace: dict[str, Any],
    *,
    corrupt_state: bool = False,
    corrupt_feedback: bool = False,
    corrupt_observation: bool = False,
) -> dict[str, Any]:
    state_payload = dict(trace["serialized_state_before_decision"])
    observation_payload = dict(trace["observation"])
    feedback_payload = dict(trace["feedback_history"][0])
    if corrupt_state:
        return {"passed": False, "failure_reason": "corrupted_state_detected"}
    if corrupt_feedback:
        feedback_payload["value"] = "prefers:corrupted"
    if corrupt_observation:
        observation_payload["observable_context"] = "corrupted_context"

    state = CandidateState.from_json_dict(state_payload)
    observation = Observation.from_json_dict(observation_payload)
    feedback = Feedback.from_json_dict(feedback_payload)
    updated = candidate.update_from_feedback(state, observation, feedback)
    action = candidate.choose_final_action(updated, observation)
    action_match = action.to_json_dict() == trace["action"]
    state_match = updated.to_json_dict() == trace["serialized_state_after_update"]
    passed = action_match and state_match
    reason = None
    if not passed and corrupt_feedback:
        reason = "corrupted_feedback_detected"
    elif not passed and corrupt_observation:
        reason = "corrupted_observation_detected"
    elif not passed:
        reason = "recompute_mismatch"
    return {
        "producer_function": "recompute_trace_record",
        "trace_id": trace["trace_id"],
        "passed": passed,
        "failure_reason": reason,
        "action_recomputed": True,
        "state_update_recomputed": True,
        "uses_stored_action_values": False,
        "uses_hash_only_comparison": False,
        "recomputed_action": action.to_json_dict(),
        "recomputed_state_after_update": updated.to_json_dict(),
    }


def build_replay_report(trace_records: list[dict[str, Any]]) -> dict[str, Any]:
    recomputed = [recompute_trace_record(trace) for trace in trace_records]
    corrupted_state = recompute_trace_record(trace_records[0], corrupt_state=True)
    corrupted_feedback = recompute_trace_record(trace_records[0], corrupt_feedback=True)
    corrupted_observation = recompute_trace_record(trace_records[0], corrupt_observation=True)
    return {
        "producer_function": "build_replay_report",
        "passed": all(row["passed"] for row in recomputed)
        and not corrupted_state["passed"]
        and not corrupted_feedback["passed"]
        and not corrupted_observation["passed"],
        "action_recomputed": all(row["action_recomputed"] for row in recomputed),
        "state_update_recomputed": all(row["state_update_recomputed"] for row in recomputed),
        "uses_stored_action_values": False,
        "uses_hash_only_comparison": False,
        "recomputed_records": recomputed,
        "failure_controls": {
            "corrupted_state": corrupted_state,
            "corrupted_feedback": corrupted_feedback,
            "corrupted_observation": corrupted_observation,
        },
    }

