from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from . import provenance_for
from . import candidate


def recompute_candidate_outputs(
    *,
    serialized_state: dict[str, Any],
    episodes: list[dict[str, Any]],
    candidate_outputs: list[dict[str, Any]],
    run_id: str,
    output_artifact_path: Path,
) -> dict[str, Any]:
    mismatches = []
    rows = []
    by_episode = {row["episode_id"]: row for row in candidate_outputs}
    for episode in episodes:
        output = by_episode[episode["episode_id"]]
        recomputed = candidate.predict(serialized_state, episode["observation"], output["action"])
        counterfactual_recomputed = {
            action: candidate.predict(serialized_state, episode["observation"], action)
            for action in output.get("counterfactual_predictions", {})
        }
        matches = recomputed == output["prediction"] and counterfactual_recomputed == output.get("counterfactual_predictions", {})
        if not matches:
            mismatches.append(episode["episode_id"])
        rows.append(
            {
                "episode_id": episode["episode_id"],
                "action": output["action"],
                "stored_prediction": output["prediction"],
                "recomputed_prediction": recomputed,
                "stored_counterfactual_predictions": output.get("counterfactual_predictions", {}),
                "recomputed_counterfactual_predictions": counterfactual_recomputed,
                "matches": matches,
            }
        )
    tampered_outputs = deepcopy(candidate_outputs)
    tampered_outputs[0] = dict(tampered_outputs[0])
    tampered_outputs[0]["prediction"] = {"boundary_state": -1, "viability_state": -1}
    tampered_mismatch = candidate.predict(
        serialized_state,
        episodes[0]["observation"],
        tampered_outputs[0]["action"],
    ) != tampered_outputs[0]["prediction"]
    return {
        "producer_function": "recompute_candidate_outputs",
        "verdict": "replay_recomputed" if not mismatches else "blocked_by_replay_recomputation_failure",
        "behavior_recomputed": True,
        "used_serialized_state": True,
        "used_observation": True,
        "hash_only": False,
        "mismatch_count": len(mismatches),
        "mismatch_episode_ids": mismatches,
        "rows": rows[:16],
        "negative_control": {
            "expected_flip": True,
            "actual_flip": tampered_mismatch,
            "verdict_before_intervention": "replay_recomputed",
            "verdict_after_intervention": "blocked_by_replay_recomputation_failure"
            if tampered_mismatch
            else "replay_recomputed",
            "accepted_hash_only": False,
        },
        "provenance": provenance_for(
            recompute_candidate_outputs,
            inputs={"episode_count": len(episodes), "candidate_output_count": len(candidate_outputs)},
            run_id=run_id,
            seed=episodes[0]["seed"] if episodes else None,
            context_episode_ids=[episode["episode_id"] for episode in episodes],
            aggregation_method="recompute_each_prediction_from_serialized_state_and_observation",
            output_artifact_path=output_artifact_path,
        ),
    }
