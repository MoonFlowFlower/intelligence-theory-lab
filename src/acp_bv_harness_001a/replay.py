from __future__ import annotations

from pathlib import Path
from typing import Any

from . import environment
from .common import provenance_for, seed_ids


def recompute_replay_from_state_observation(
    bundle: dict[str, Any],
    *,
    repo_root: Path,
    output_artifact_path: Path,
    run_id: str,
) -> dict[str, Any]:
    serialized_state = bundle["serialized_state"]
    mismatch_episode_ids: list[str] = []
    rows = []
    for episode, output in zip(bundle["episodes"], bundle["candidate_outputs"]):
        action = output["action"]
        recomputed = environment.reference_candidate_predict(
            serialized_state,
            episode["observation"],
            action,
        )
        matches = recomputed == output["prediction"]
        if not matches:
            mismatch_episode_ids.append(episode["episode_id"])
        rows.append(
            {
                "episode_id": episode["episode_id"],
                "action": action,
                "recomputed_prediction": recomputed,
                "stored_prediction": output["prediction"],
                "matches": matches,
            }
        )
    return {
        "producer_function": "recompute_replay_from_state_observation",
        "verdict": "replay_recomputed",
        "behavior_recomputed": True,
        "used_serialized_state": True,
        "used_observation": True,
        "repo_owned_truth_source_used": True,
        "stored_actions_reused": False,
        "hash_only": False,
        "mismatch_episode_ids": mismatch_episode_ids,
        "rows": rows,
        "hash_only_positive_control": {
            "verdict": "blocked_by_replay_hash_only",
            "stored_hash_only_accepted": False,
        },
        "provenance": provenance_for(
            recompute_replay_from_state_observation,
            repo_root=repo_root,
            inputs={"bundle_id": bundle["bundle_id"], "episode_count": len(bundle["episodes"])},
            run_id=run_id,
            seed_context_episode_ids=seed_ids(bundle["episodes"]),
            aggregation_method="recompute_each_prediction_from_state_observation",
            output_artifact_path=output_artifact_path,
        ),
    }


def reject_replay_hash_only_payload() -> dict[str, Any]:
    return {
        "producer_function": "reject_replay_hash_only_payload",
        "verdict": "blocked_by_replay_hash_only",
        "behavior_recomputed": False,
        "stored_hash_only_payload": True,
    }
