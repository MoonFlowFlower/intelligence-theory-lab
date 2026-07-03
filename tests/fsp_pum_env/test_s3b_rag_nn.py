from pathlib import Path

from src.fsp_pum_env.battery.base import PrefixEvent, load_design, validate_prediction
from src.fsp_pum_env.battery.rag_nn import (
    NearestNeighborUserMatchingPredictor,
    RagK5EpisodeRetrievalPredictor,
    retrieval_conventions,
)


FROZEN = Path(__file__).resolve().parents[2] / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "frozen_design.json"


def _event(action, symbol, step):
    return PrefixEvent(
        action=action,
        observation={"symbol": symbol},
        session_index=step // 3,
        turn_in_session=step % 3,
        step_index=step,
        session_boundary="start" if step % 3 == 0 else "none",
    )


def test_rag_k5_episode_retrieval_uses_nearest_prefix_episodes():
    design = load_design(FROZEN)
    actions = tuple(design["evaluation"]["counterfactual_action_set_per_query"])
    predictor = RagK5EpisodeRetrievalPredictor.from_design(design)
    for event in (
        _event("task_topic_0", 1, 0),
        _event("probe_0", 2, 1),
        _event("task_topic_0", 11, 2),
        _event("task_topic_0", 9, 3),
        _event("probe_0", 8, 4),
        _event("task_topic_0", 14, 5),
    ):
        predictor.observe(event)
    query = RagK5EpisodeRetrievalPredictor.from_design(design)
    for event in (_event("task_topic_0", 1, 0), _event("probe_0", 2, 1)):
        query.observe(event)
    query.fit(predictor.training_records)

    prediction = query.predict(actions)

    validate_prediction(prediction, design, actions)
    assert prediction["task_topic_0"][11] > prediction["task_topic_0"][14]
    assert retrieval_conventions()["rag_k5_episode_retrieval"]["k"] == 5


def test_nearest_neighbor_user_matching_predicts_from_matching_user_profile():
    design = load_design(FROZEN)
    actions = tuple(design["evaluation"]["counterfactual_action_set_per_query"])
    train = [
        _event("task_topic_0", 3, 0),
        _event("task_topic_2", 4, 1),
        _event("task_topic_0", 3, 2),
        _event("task_topic_0", 20, 0),
        _event("task_topic_2", 21, 1),
        _event("task_topic_0", 20, 2),
    ]
    predictor = NearestNeighborUserMatchingPredictor.from_design(design)
    predictor.fit(train)
    for event in (_event("task_topic_0", 20, 0), _event("task_topic_2", 21, 1)):
        predictor.observe(event)

    prediction = predictor.predict(actions)

    validate_prediction(prediction, design, actions)
    assert prediction["task_topic_0"][20] > prediction["task_topic_0"][3]
    assert predictor.fitted_user_count == 2
