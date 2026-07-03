from pathlib import Path

from src.fsp_pum_env.battery.base import PrefixEvent, load_design, validate_prediction
from src.fsp_pum_env.battery.ls_regressors import (
    DiscountedLeastSquaresPredictor,
    RunningAveragePreferenceRegressor,
)


FROZEN = Path(__file__).resolve().parents[2] / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "frozen_design.json"


def _event(action, symbol, step):
    return PrefixEvent(
        action=action,
        observation={"symbol": symbol},
        session_index=step // 15,
        turn_in_session=step % 15,
        step_index=step,
        session_boundary="start" if step % 15 == 0 else "none",
    )


def test_discounted_ls_lambda_095_is_online_prefix_only_and_prediction_format_valid():
    design = load_design(FROZEN)
    actions = tuple(design["evaluation"]["counterfactual_action_set_per_query"])
    prefix = [
        _event("task_topic_0", 4, 0),
        _event("task_topic_0", 6, 1),
        _event("probe_0", 2, 2),
    ]
    future = _event("task_topic_0", 31, 3)

    predictor = DiscountedLeastSquaresPredictor.from_design(design)
    same_prefix = DiscountedLeastSquaresPredictor.from_design(design)
    with_future = DiscountedLeastSquaresPredictor.from_design(design)
    for event in prefix:
        predictor.observe(event)
        same_prefix.observe(event)
        with_future.observe(event)

    before_future = predictor.predict(actions)
    same_prefix_prediction = same_prefix.predict(actions)
    with_future.observe(future)
    after_future = with_future.predict(actions)

    assert predictor.discount == 0.95
    validate_prediction(before_future, design, actions)
    assert before_future == same_prefix_prediction
    assert before_future != after_future


def test_running_average_preference_regressor_fits_action_local_symbol_averages():
    design = load_design(FROZEN)
    actions = tuple(design["evaluation"]["counterfactual_action_set_per_query"])
    predictor = RunningAveragePreferenceRegressor.from_design(design)

    for event in (
        _event("task_topic_0", 4, 0),
        _event("task_topic_0", 6, 1),
        _event("task_topic_7", 20, 2),
    ):
        predictor.observe(event)

    prediction = predictor.predict(actions)

    validate_prediction(prediction, design, actions)
    assert prediction["task_topic_0"].index(max(prediction["task_topic_0"])) == 5
    assert prediction["task_topic_7"].index(max(prediction["task_topic_7"])) == 20
