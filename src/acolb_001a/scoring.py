from .config import EQUIV_BAND, SCORE_SCALE
from .linear import rmse
from .provenance import build_metric_provenance, code_path_hash
from .schemas import Episode


def score_episode_predictions(episode: Episode, predictions: dict[str, float], producer: str) -> dict:
    errors = []
    rows = []
    truth_by_q = {query.q_id: query.truth_outcome for query in episode.queries}
    for q_id, truth in truth_by_q.items():
        pred = float(predictions[q_id])
        errors.append(pred - truth)
        rows.append({"q_id": q_id, "predicted": pred, "actual": truth, "abs_error": abs(pred - truth)})
    value = max(0.0, 1.0 - rmse(errors) / SCORE_SCALE)
    return {
        "score": value,
        "rmse": rmse(errors),
        "rows": rows,
        "producer": producer,
        "provenance": build_metric_provenance(
            metric_id=f"{producer}_{episode.episode_id}_score",
            metric_name=f"{producer} episode score",
            producer_function=producer,
            producer_module="acolb_001a.scoring",
            code_path_hash=code_path_hash(score_episode_predictions),
            run_id=f"score-{producer}-{episode.episode_id}",
            seed_ids=[episode.seed],
            episode_ids=[episode.episode_id],
            input_artifact_paths=["trace.jsonl"],
            output_artifact_path="result.json",
            output_row_ids=[f"{producer}-{episode.episode_id}"],
            aggregation_rule="rmse_scaled_score",
            threshold_used=EQUIV_BAND,
            computed_not_literal_evidence="score recomputed from per-query prediction errors",
            failure_path_evidence="prediction perturbation changes rmse_scaled_score",
        ),
    }


def aggregate_episode_scores(scores: list[dict], producer: str) -> dict:
    if not scores:
        value = 0.0
    else:
        value = sum(row["score"] for row in scores) / len(scores)
    return {
        "producer": producer,
        "score": value,
        "episode_ids": [episode_id for score in scores for episode_id in score["provenance"]["episode_ids"]],
        "per_episode": scores,
    }
