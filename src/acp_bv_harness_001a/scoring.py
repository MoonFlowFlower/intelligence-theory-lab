from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from . import CLAIM_CEILING, TASK_ID
from . import boundary, difficulty, environment, leakage, replay, source_pins
from .common import provenance_for, seed_ids


def metric_aggregator(values: list[float]) -> float:
    if not values:
        raise ValueError("no metric values")
    return round(sum(values) / len(values), 6)


def score_prediction_rows(
    episodes: list[dict[str, Any]],
    prediction_rows: list[dict[str, Any]],
    truth_generator: Callable[[dict[str, Any], str], dict[str, Any]],
) -> float:
    scores: list[float] = []
    by_episode = {row["episode_id"]: row for row in prediction_rows}
    for episode in episodes:
        row = by_episode[episode["episode_id"]]
        truth = truth_generator(episode, row["action"])
        predicted = row["prediction"]
        scores.append(1.0 if predicted == truth else 0.0)
        for action in episode["harness_selected_counterfactual_actions"]:
            counterfactual_predictions = row.get("counterfactual_predictions", {})
            predicted_cf = counterfactual_predictions.get(action)
            truth_cf = truth_generator(episode, action)
            scores.append(1.0 if predicted_cf == truth_cf else 0.0)
    return metric_aggregator(scores)


def score_candidate_bundle(
    bundle: dict[str, Any],
    *,
    repo_root: Path,
    output_artifact_path: Path,
    run_id: str,
    source_pin_manifest: dict[str, Any],
    candidate_writable_roots: list[Path],
    candidate_artifact_roots: list[Path],
    truth_generator: Callable[[dict[str, Any], str], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    truth_generator = truth_generator or environment.held_out_truth_generator
    manifest_check = source_pins.verify_source_pin_manifest(source_pin_manifest, repo_root=repo_root)
    if not manifest_check["passed"]:
        return {
            "task_id": TASK_ID,
            "blocked": True,
            "block_reason": manifest_check["block_reason"],
            "manifest_verification": manifest_check,
        }

    expected_hashes = source_pins.expected_hashes_by_role(source_pin_manifest)
    truth_boundary = boundary.verify_callable_source_boundary(
        truth_generator,
        repo_root=repo_root,
        candidate_writable_roots=candidate_writable_roots,
        candidate_artifact_roots=candidate_artifact_roots,
        expected_source_hash=expected_hashes.get("held_out_truth_generator"),
    )
    if truth_boundary["boundary_verdict"] != "source_boundary_pass":
        return {
            "task_id": TASK_ID,
            "blocked": True,
            "block_reason": "blocked_by_runtime_mutation_or_temporal_boundary_gap",
            "truth_boundary": truth_boundary,
            "manifest_verification": manifest_check,
        }

    leak = leakage.scan_candidate_bundle_for_leakage(bundle, run_id=run_id, output_artifact_path=output_artifact_path)
    if leak["verdict"] == "blocked":
        return {
            "task_id": TASK_ID,
            "blocked": True,
            "block_reason": "blocked_by_leakage_detected",
            "leakage_result": leak,
            "manifest_verification": manifest_check,
        }

    replay_result = replay.recompute_replay_from_state_observation(
        bundle,
        repo_root=repo_root,
        output_artifact_path=output_artifact_path,
        run_id=run_id,
    )
    if replay_result["mismatch_episode_ids"]:
        return {
            "task_id": TASK_ID,
            "blocked": True,
            "block_reason": "blocked_by_replay_mismatch",
            "replay_result": replay_result,
            "manifest_verification": manifest_check,
        }

    episodes = bundle["episodes"]
    raw_score = score_prediction_rows(episodes, bundle["candidate_outputs"], truth_generator)
    metadata = difficulty.difficulty_source(episodes)
    normalized_score = difficulty.difficulty_normalizer(raw_score, metadata)
    provenance = provenance_for(
        score_prediction_rows,
        repo_root=repo_root,
        inputs={"bundle_id": bundle["bundle_id"], "episode_count": len(episodes)},
        run_id=run_id,
        seed_context_episode_ids=seed_ids(episodes),
        aggregation_method="mean_exact_prediction_and_counterfactual_accuracy",
        output_artifact_path=output_artifact_path,
    )
    return {
        "task_id": TASK_ID,
        "blocked": False,
        "score": normalized_score,
        "raw_score": raw_score,
        "difficulty_metadata": metadata,
        "threshold_rule": difficulty.threshold_distribution_input_rule(),
        "provenance": provenance,
        "manifest_verification": manifest_check,
        "truth_boundary": truth_boundary,
        "claim_ceiling": CLAIM_CEILING,
    }
