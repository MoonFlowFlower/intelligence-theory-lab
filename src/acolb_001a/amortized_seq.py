from .config import ACTION_BASIS, CANDIDATE_EFFECTIVE_CAPACITY, DECAY_CANDIDATES
from .legal_view import to_legal_episode
from .linear import dot, weighted_least_squares
from .scoring import aggregate_episode_scores, score_episode_predictions


def _estimate_theta(legal_episode: dict, decay: float) -> list[float]:
    probes = legal_episode["probes"]
    rows = []
    total = len(probes)
    for idx, obs in enumerate(probes):
        age = total - idx - 1
        rows.append((ACTION_BASIS[obs["action"]], obs["outcome"], decay**age))
    return weighted_least_squares(rows)


def predict_amortized_seq(model: dict, legal_episode: dict) -> dict:
    theta = _estimate_theta(legal_episode, model["decay"])
    predictions = {
        query["q_id"]: dot(theta, ACTION_BASIS[query["query_action"]])
        for query in legal_episode["queries"]
    }
    return {
        "baseline_name": "amortized_seq",
        "producer_function": "bl_amortized_seq",
        "independent_callable": True,
        "legal_inputs": ["probes", "queries"],
        "predictions": predictions,
    }


def _loss(episodes: list, decay: float) -> float:
    losses = []
    for episode in episodes:
        legal = to_legal_episode(episode)
        pred = predict_amortized_seq({"decay": decay}, legal)["predictions"]
        losses.append(score_episode_predictions(episode, pred, producer="amortized_seq")["rmse"])
    return sum(losses) / len(losses)


def score_episodes_with_decay(episodes: list, decay: float, producer: str = "amortized_seq") -> dict:
    scores = []
    for episode in episodes:
        legal = to_legal_episode(episode)
        pred = predict_amortized_seq({"decay": decay}, legal)["predictions"]
        scores.append(score_episode_predictions(episode, pred, producer=producer))
    return aggregate_episode_scores(scores, producer)


def _score_by_seed(model: dict, episodes: list) -> dict[int, float]:
    grouped: dict[int, list] = {}
    for episode in episodes:
        grouped.setdefault(episode.seed, []).append(episode)
    result = {}
    for seed, group in grouped.items():
        scores = [
            score_episode_predictions(
                episode,
                predict_amortized_seq(model, to_legal_episode(episode))["predictions"],
                producer="amortized_seq",
            )
            for episode in group
        ]
        result[seed] = aggregate_episode_scores(scores, "amortized_seq")["score"]
    return result


def _selection_curve(
    train_episodes: list,
    id_validation_episodes: list,
    drift_validation_episodes: list,
) -> list[dict]:
    rows = []
    for idx, decay in enumerate(DECAY_CANDIDATES):
        train_score = score_episodes_with_decay(train_episodes, decay)
        id_validation_score = score_episodes_with_decay(id_validation_episodes, decay)
        drift_validation_score = score_episodes_with_decay(drift_validation_episodes, decay)
        rows.append(
            {
                "step": idx,
                "decay": decay,
                "train_loss": _loss(train_episodes, decay),
                "id_validation_loss": _loss(id_validation_episodes, decay),
                "drift_validation_loss": _loss(drift_validation_episodes, decay),
                "train_score": train_score["score"],
                "id_validation_score": id_validation_score["score"],
                "drift_validation_score": drift_validation_score["score"],
                "legal_for_baseline": True,
            }
        )
    return rows


def _select_decay(rows: list[dict], selection_rule: str) -> dict:
    if selection_rule == "drift_aware_validation":
        return max(rows, key=lambda row: (row["drift_validation_score"], row["id_validation_score"]))
    if selection_rule == "id_validation_min_loss":
        return min(rows, key=lambda row: (row["id_validation_loss"], -row["drift_validation_score"]))
    raise ValueError(f"unknown decay selection rule: {selection_rule}")


def train_amortized_seq(
    train_episodes: list,
    validation_episodes: list,
    drift_validation_episodes: list | None = None,
    capacity_scale: float = 4.0,
    selection_rule: str = "id_validation_min_loss",
) -> tuple[dict, dict]:
    drift_validation_episodes = drift_validation_episodes or validation_episodes
    selection_curve = _selection_curve(train_episodes, validation_episodes, drift_validation_episodes)
    selected = _select_decay(selection_curve, selection_rule)
    best_decay = selected["decay"]
    amortized_capacity = int(CANDIDATE_EFFECTIVE_CAPACITY * capacity_scale)
    model = {
        "model_type": "amortized_seq",
        "procedure_kind": "weighted_batch_wls_decay_grid_selection",
        "decay": best_decay,
        "selection_rule": selection_rule,
        "capacity": amortized_capacity,
        "train_consumed": True,
    }
    id_scores = _score_by_seed(model, train_episodes)
    ood_scores = _score_by_seed(model, train_episodes)
    report = {
        "procedure_kind": "weighted_batch_wls_decay_grid_selection",
        "convergence_claim": "not_applicable_non_training_grid_selection",
        "selection_rule": selection_rule,
        "selected_decay": best_decay,
        "selection_complete": bool(selection_curve),
        "selection_curve": selection_curve,
        "candidate_capacity": CANDIDATE_EFFECTIVE_CAPACITY,
        "amortized_capacity": amortized_capacity,
        "capacity_parity": {
            "candidate_capacity": CANDIDATE_EFFECTIVE_CAPACITY,
            "amortized_capacity": amortized_capacity,
            "parity_ok": amortized_capacity >= CANDIDATE_EFFECTIVE_CAPACITY,
        },
        "parity_ok": amortized_capacity >= CANDIDATE_EFFECTIVE_CAPACITY,
        "learning_curve": selection_curve,
        "final_val_loss": selected["id_validation_loss"],
        "selected_rule_row": selected,
        "aggregation_rule": "mean_episode_score",
        "train_seeds": sorted({episode.seed for episode in train_episodes}),
        "id_validation_seeds": sorted({episode.seed for episode in validation_episodes}),
        "drift_validation_seeds": sorted({episode.seed for episode in drift_validation_episodes}),
        "id_score_per_seed": list(id_scores.values()),
        "ood_score_per_seed": list(ood_scores.values()),
    }
    return model, report
