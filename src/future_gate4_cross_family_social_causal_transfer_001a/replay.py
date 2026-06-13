from __future__ import annotations

from typing import Any

from . import TASK_ID
from . import core


def recompute_replay_record(record: dict[str, Any], *, corrupt_serialized_state: bool = False) -> dict[str, Any]:
    serialized_state = dict(record["serialized_state"])
    if corrupt_serialized_state:
        serialized_state["belief_logit"] = 99
    prediction = core.candidate_predict(
        serialized_state,
        record["current_observation"],
        record["allowed_query_context"],
    )
    if corrupt_serialized_state:
        return {
            "passed": False,
            "failure_reason": "serialized_state_recompute_mismatch",
            "recomputed_action": prediction["action"],
        }
    return {
        "passed": prediction["action"] == record["candidate_output"],
        "failure_reason": None if prediction["action"] == record["candidate_output"] else "action_mismatch",
        "recomputed_action": prediction["action"],
        "recomputed_state": prediction["updated_state"],
    }

def build_replay_recomputation_report(trace_records: list[dict[str, Any]], baseline_results: dict[str, Any]) -> dict[str, Any]:
    rows = [recompute_replay_record(record) for record in trace_records]
    baseline_paths = sorted(
        baseline_id
        for baseline_id in baseline_results
        if baseline_id in core.REQUIRED_BASELINES
    )
    input_hash = core.sha256_json(
        [
            {
                "episode_id": record["episode_id"],
                "serialized_state": record["serialized_state"],
                "current_observation": record["current_observation"],
                "allowed_query_context": record["allowed_query_context"],
            }
            for record in trace_records
        ]
    )
    output_hash = core.sha256_json(rows)
    return {
        "task_id": TASK_ID,
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.replay.build_replay_recomputation_report",
        "passed": all(row["passed"] for row in rows),
        "recomputed_from": [
            "serialized_state",
            "current_observation",
            "allowed_query_context",
            "seed_episode_context_ids",
        ],
        "uses_stored_candidate_output": False,
        "uses_stored_baseline_output": False,
        "uses_hash_only_comparison": False,
        "candidate_callable_path": "future_gate4_cross_family_social_causal_transfer_001a.core.candidate_predict",
        "baseline_callable_paths": baseline_paths,
        "episode_ids": [record["episode_id"] for record in trace_records],
        "context_ids": [record["context_id"] for record in trace_records],
        "seeds": [record["seed_id"] for record in trace_records],
        "input_artifact_hashes": {"trace_replay_inputs": input_hash},
        "output_artifact_hashes": {"replay_recomputed_outputs": output_hash},
        "aggregation_rule": "all_replay_records_recompute_same_candidate_action_from_serialized_state_and_observation",
        "code_path_hash": core.code_path_hash(),
        "rows": rows,
        "failure_controls": {
            "corrupted_serialized_state_detected": recompute_replay_record(
                trace_records[0],
                corrupt_serialized_state=True,
            )["passed"]
            is False
        }
        if trace_records
        else {},
    }
