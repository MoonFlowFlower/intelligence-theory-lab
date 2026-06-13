from __future__ import annotations

from typing import Any

from . import candidate
from .schemas import EpisodeRecord


INTERVENTIONS = [
    "no_state",
    "no_feedback",
    "no_action",
    "no_active_query",
    "shuffled_feedback",
    "counterfactual_transition",
]


def run_ablation_suite(
    episode_records: list[EpisodeRecord],
    candidate_summary: dict[str, Any],
) -> dict[str, Any]:
    candidate_score = candidate_summary["score"]
    candidate_episode_run_ids = [f"candidate:{row['episode_id']}" for row in candidate_summary["rows"]]
    interventions = {}
    drops = {}
    for intervention in INTERVENTIONS:
        rows = [candidate.rerun_with_intervention(episode, intervention) for episode in episode_records]
        score = sum(row["score"] for row in rows) / len(rows)
        drops[intervention] = candidate_score - score
        interventions[intervention] = {
            "intervention_id": intervention,
            "producer_function": "run_ablation_suite",
            "rerun_performed": True,
            "post_hoc_score_edit": False,
            "score": score,
            "drop": drops[intervention],
            "episode_run_ids": [row["trace"]["trace_id"] for row in rows],
            "rows": rows,
        }
    return {
        "producer_function": "run_ablation_suite",
        "candidate_episode_run_ids": candidate_episode_run_ids,
        "interventions": interventions,
        "drops": drops,
        "passed": (
            drops["no_active_query"] >= 0.20
            and drops["shuffled_feedback"] >= 0.20
            and drops["counterfactual_transition"] >= 0.15
        ),
    }

