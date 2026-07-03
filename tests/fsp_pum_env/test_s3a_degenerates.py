import json
from pathlib import Path

import pytest

from src.fsp_pum_env.battery.base import PrefixEvent, load_design, validate_prediction
from src.fsp_pum_env.battery.degenerates import (
    GlobalPriorPredictor,
    MajorityPredictor,
    PredictAllPredictor,
    PredictNonePredictor,
    degenerate_conventions,
    write_battery_manifest,
)


FROZEN = Path(__file__).resolve().parents[2] / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "frozen_design.json"


def _actions(design):
    return tuple(design["evaluation"]["counterfactual_action_set_per_query"])


def _event(action, symbol, step=0):
    return PrefixEvent(
        action=action,
        observation={"symbol": symbol},
        session_index=0,
        turn_in_session=step,
        step_index=step,
        session_boundary="none" if step else "start",
    )


def test_predict_all_and_predict_none_emit_declared_one_hot_distribution_format():
    design = load_design(FROZEN)
    actions = _actions(design)

    all_prediction = PredictAllPredictor.from_design(design).predict(actions)
    none_prediction = PredictNonePredictor.from_design(design).predict(actions)

    validate_prediction(all_prediction, design, actions)
    validate_prediction(none_prediction, design, actions)
    assert all(dist[-1] == 1.0 and sum(dist) == 1.0 for dist in all_prediction.values())
    assert all(dist[0] == 1.0 and sum(dist) == 1.0 for dist in none_prediction.values())


def test_majority_and_global_prior_use_only_observed_prefix_symbols():
    design = load_design(FROZEN)
    actions = _actions(design)

    majority = MajorityPredictor.from_design(design)
    prior = GlobalPriorPredictor.from_design(design)
    for event in (
        _event("task_topic_0", 7, 0),
        _event("probe_0", 7, 1),
        _event("task_topic_1", 2, 2),
    ):
        majority.observe(event)
        prior.observe(event)

    majority_prediction = majority.predict(actions)
    prior_prediction = prior.predict(actions)

    validate_prediction(majority_prediction, design, actions)
    validate_prediction(prior_prediction, design, actions)
    assert all(dist[7] == 1.0 for dist in majority_prediction.values())
    assert all(dist[7] == pytest.approx(2 / 3) for dist in prior_prediction.values())
    assert all(dist[2] == pytest.approx(1 / 3) for dist in prior_prediction.values())


def test_prefix_event_rejects_future_or_latent_fields():
    with pytest.raises(ValueError, match="forbidden"):
        PrefixEvent(
            action="task_topic_0",
            observation={"symbol": 1, "theta": [1.5]},
            session_index=0,
            turn_in_session=0,
            step_index=0,
            session_boundary="start",
        )

    with pytest.raises(ValueError, match="forbidden"):
        PrefixEvent(
            action="task_topic_0",
            observation={"symbol": 1},
            session_index=0,
            turn_in_session=0,
            step_index=0,
            session_boundary="start",
            extra={"future_observation": {"symbol": 2}},
        )


def test_battery_manifest_declares_degenerate_conventions_from_manifest_alone(tmp_path):
    design = load_design(FROZEN)
    manifest_path = tmp_path / "s3a_battery_manifest.json"

    manifest = write_battery_manifest(FROZEN, manifest_path)

    assert manifest["implemented_members"] == [
        "predict_all",
        "predict_none",
        "majority",
        "global_prior",
        "discounted_LS_lambda_0.95",
        "running_average_preference_regressor",
    ]
    assert manifest["prediction_format"]["prediction_target"] == design["evaluation"]["prediction_target"]
    assert manifest["degenerate_conventions"] == degenerate_conventions(design)
    assert set(manifest["degenerate_conventions"]) == {"predict_all", "predict_none", "majority", "global_prior"}
    assert json.loads(manifest_path.read_text(encoding="utf-8")) == manifest
