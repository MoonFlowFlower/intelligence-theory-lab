from __future__ import annotations

from typing import Any

from .common import THRESHOLDS


def difficulty_source(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for episode in episodes:
        observation = episode["observation"]
        difficulty = 1.0 + (0.2 * int(observation["topology"])) + (0.1 * int(observation["risk"]))
        rows.append(
            {
                "episode_id": episode["episode_id"],
                "context_id": episode["context_id"],
                "difficulty": round(difficulty, 4),
                "source": "repo_owned_environment_metadata",
            }
        )
    return {
        "producer_function": "difficulty_source",
        "candidate_authored_fields_used": [],
        "difficulty_rows": rows,
    }


def difficulty_normalizer(raw_score: float, difficulty_metadata: dict[str, Any]) -> float:
    if any(row.get("source") != "repo_owned_environment_metadata" for row in difficulty_metadata["difficulty_rows"]):
        raise ValueError("blocked_by_unverified_difficulty_source")
    return round(raw_score, 6)


def threshold_bands() -> dict[str, float]:
    return dict(THRESHOLDS)


def threshold_distribution_input_rule() -> dict[str, Any]:
    return {
        "default_bands_immutable": True,
        "post_hoc_threshold_change_forbidden": True,
        "baseline_error_distribution_recalibrated": False,
        "candidate_influenced_thresholds": False,
        "thresholds": threshold_bands(),
    }
