from pathlib import Path

import pytest

from src.fsp_pum_env.battery.base import PrefixEvent, load_design, validate_prediction
from src.fsp_pum_env.battery.obs_decoders import (
    DECODER_MEMBER_NAMES,
    decoder_grid,
    s3c_split_for_user,
    validate_s3c_training_user_id,
    ObsDecoderLogRegPredictor,
)


FROZEN = Path(__file__).resolve().parents[2] / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "frozen_design.json"


def _event(action="task_topic_0", symbol=3, step=0):
    return PrefixEvent(
        action=action,
        observation={"symbol": symbol},
        session_index=0,
        turn_in_session=step,
        step_index=step,
        session_boundary="start" if step == 0 else "none",
    )


def test_s3c_split_rejects_heldout_users_for_all_training_phases():
    assert s3c_split_for_user(0) == "fit"
    assert s3c_split_for_user(639) == "fit"
    assert s3c_split_for_user(640) == "internal_validation"
    assert s3c_split_for_user(799) == "internal_validation"

    with pytest.raises(ValueError, match="heldout"):
        s3c_split_for_user(800)
    with pytest.raises(ValueError, match="heldout"):
        validate_s3c_training_user_id(999, phase="fit")


def test_decoder_grids_match_frozen_addendum_counts_and_names():
    assert DECODER_MEMBER_NAMES == ["obs_decoder_logreg", "obs_decoder_gbt", "obs_decoder_gru"]
    assert len(decoder_grid("obs_decoder_logreg")) == 8
    assert len(decoder_grid("obs_decoder_gbt")) == 8
    assert len(decoder_grid("obs_decoder_gru")) == 8
    assert decoder_grid("obs_decoder_logreg")[0]["features"] == "F1"
    assert decoder_grid("obs_decoder_gbt")[0]["features"] == "F2"


def test_obs_decoder_prefix_only_prediction_format_and_action_conditioning():
    design = load_design(FROZEN)
    actions = tuple(design["evaluation"]["counterfactual_action_set_per_query"])
    predictor = ObsDecoderLogRegPredictor.from_design(design)
    predictor.observe(_event("task_topic_0", 7, 0))
    predictor.observe(_event("probe_0", 11, 1))

    prediction = predictor.predict(actions)

    validate_prediction(prediction, design, actions)
    assert set(prediction) == set(actions)
    assert prediction["task_topic_0"] is not prediction["probe_0"]
