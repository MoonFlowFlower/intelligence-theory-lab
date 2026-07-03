from pathlib import Path

from src.fsp_pum_env.battery.base import PrefixEvent, load_design, validate_prediction
from src.fsp_pum_env.battery.seq_models import (
    SeqFullHistoryNoActionConditioningPredictor,
    SeqWindowActionW15NoPersistencePredictor,
    build_full_history_symbol_sequence,
    build_w15_action_conditioned_sequence,
    sequence_grid,
)


FROZEN = Path(__file__).resolve().parents[2] / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "frozen_design.json"


def _event(action, symbol, step, session, turn):
    return PrefixEvent(
        action=action,
        observation={"symbol": symbol},
        session_index=session,
        turn_in_session=turn,
        step_index=step,
        session_boundary="start" if turn == 0 else "none",
    )


def test_seq_full_member_is_action_invariant_by_construction():
    design = load_design(FROZEN)
    actions = tuple(design["evaluation"]["counterfactual_action_set_per_query"])
    predictor = SeqFullHistoryNoActionConditioningPredictor.from_design(design)
    for event in (
        _event("task_topic_0", 1, 0, 0, 0),
        _event("probe_0", 2, 1, 0, 1),
        _event("task_topic_5", 3, 2, 0, 2),
    ):
        predictor.observe(event)

    prediction = predictor.predict(actions)

    validate_prediction(prediction, design, actions)
    first = prediction[actions[0]]
    assert all(distribution == first for distribution in prediction.values())
    assert build_full_history_symbol_sequence(predictor.prefix_events) == [1, 2, 3]


def test_w15_action_conditioned_sequence_resets_at_session_boundary():
    before_a = [
        _event("task_topic_0", 1, 0, 0, 0),
        _event("probe_0", 2, 1, 0, 1),
        _event("task_topic_1", 3, 15, 1, 0),
        _event("probe_2", 4, 16, 1, 1),
    ]
    before_b = [
        _event("task_topic_7", 30, 0, 0, 0),
        _event("probe_3", 31, 1, 0, 1),
        _event("task_topic_1", 3, 15, 1, 0),
        _event("probe_2", 4, 16, 1, 1),
    ]

    assert build_w15_action_conditioned_sequence(before_a) == build_w15_action_conditioned_sequence(before_b)


def test_w15_predictor_prediction_format_and_frozen_grid():
    design = load_design(FROZEN)
    actions = tuple(design["evaluation"]["counterfactual_action_set_per_query"])
    predictor = SeqWindowActionW15NoPersistencePredictor.from_design(design)
    predictor.observe(_event("task_topic_1", 3, 15, 1, 0))
    predictor.observe(_event("probe_2", 4, 16, 1, 1))

    prediction = predictor.predict(actions)

    validate_prediction(prediction, design, actions)
    assert len(sequence_grid("seq_full_history_no_action_conditioning")) == 8
    assert len(sequence_grid("seq_window_with_action_conditioning_W15_no_cross_session_persistence")) == 8
