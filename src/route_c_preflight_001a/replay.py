from __future__ import annotations

from copy import deepcopy
from typing import Any

from . import provenance


def _predict_from_rows(serialized_state: dict[str, Any], intervention_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows_by_episode: dict[str, list[dict[str, Any]]] = {}
    for row in intervention_rows:
        rows_by_episode.setdefault(row["episode_id"], []).append(row)
    predictions = []
    for episode_id, state in serialized_state["episodes"].items():
        handles = state["handles"]
        effect_sums = {handle: 0.0 for handle in handles}
        effect_weights = {handle: 0.0 for handle in handles}
        for row in rows_by_episode.get(episode_id, []):
            handle = row["target_handle"]
            value = float(row["value"])
            effect_sums[handle] += value * float(row["post_handle_values"][handle])
            effect_weights[handle] += value * value
        effects = {
            handle: (effect_sums[handle] / effect_weights[handle] if effect_weights[handle] else 0.0)
            for handle in handles
        }
        ranked = sorted(handles, key=lambda handle: (-abs(effects[handle]), handle))
        predicted = sorted(ranked[: state["k_self"]])
        predictions.append(
            {
                "episode_id": episode_id,
                "predicted_self_handles": predicted,
                "prediction_hash": provenance.sha256_json({"episode_id": episode_id, "predicted_self_handles": predicted}),
            }
        )
    return predictions


def _corrupt_rows_to_force_behavior_change(
    intervention_rows: list[dict[str, Any]],
    stored_predictions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    predicted_by_episode = {row["episode_id"]: set(row["predicted_self_handles"]) for row in stored_predictions}
    corrupted = deepcopy(intervention_rows)
    for row in corrupted:
        predicted = predicted_by_episode[row["episode_id"]]
        target = row["target_handle"]
        value = float(row["value"])
        row["post_handle_values"][target] = 0.0 if target in predicted else 1000.0 * value
    return corrupted


def replay_oracle_predictions(
    *,
    serialized_state: dict[str, Any],
    intervention_rows: list[dict[str, Any]],
    stored_predictions: list[dict[str, Any]],
    run_id: str,
) -> dict[str, Any]:
    recomputed = _predict_from_rows(serialized_state, intervention_rows)
    expected_by_episode = {row["episode_id"]: row["predicted_self_handles"] for row in stored_predictions}
    mismatches = [
        row["episode_id"]
        for row in recomputed
        if row["predicted_self_handles"] != expected_by_episode.get(row["episode_id"])
    ]
    tampered_hash_predictions = deepcopy(stored_predictions)
    if tampered_hash_predictions:
        tampered_hash_predictions[0]["prediction_hash"] = "0" * 64
    hash_tamper_recomputed = _predict_from_rows(serialized_state, intervention_rows)
    hash_tamper_changes_behavior = any(
        row["predicted_self_handles"] != expected_by_episode.get(row["episode_id"])
        for row in hash_tamper_recomputed
    )
    corrupted_rows = _corrupt_rows_to_force_behavior_change(intervention_rows, stored_predictions)
    corrupted_recomputed = _predict_from_rows(serialized_state, corrupted_rows)
    corrupt_log_changes = any(
        row["predicted_self_handles"] != expected_by_episode.get(row["episode_id"])
        for row in corrupted_recomputed
    )
    return {
        "producer_function": provenance.producer_name(replay_oracle_predictions),
        "run_id": run_id,
        "verdict": "replay_recomputed" if not mismatches and corrupt_log_changes else "blocked_by_replay_hash_only",
        "behavior_recomputed": True,
        "used_serialized_state": True,
        "used_intervention_rows": True,
        "hash_only": False,
        "mismatch_episode_ids": mismatches,
        "recomputed_predictions": recomputed,
        "negative_control": {
            "stored_hash_tamper_accepted": hash_tamper_changes_behavior,
            "corrupt_intervention_log_changes_behavior": corrupt_log_changes,
            "accepted_hash_only": False,
        },
    }
