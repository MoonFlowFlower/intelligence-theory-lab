from acolb_001a.candidate import run_candidate
from acolb_001a.config import EQUIV_BAND
from acolb_001a.generator import generate_episode
from acolb_001a.legal_view import to_legal_episode
from acolb_001a.scoring import score_episode_predictions


def _scored(variant="candidate"):
    episode = generate_episode("ood", 5001, 0)
    legal = to_legal_episode(episode)
    result = run_candidate(legal, variant=variant)
    score = score_episode_predictions(episode, result["predictions"], producer=variant)
    return result, score


def test_prediction_error_update_is_load_bearing():
    normal, normal_score = _scored("candidate")
    no_update, no_update_score = _scored("no_update")
    no_pe, no_pe_score = _scored("no_PE_correction")

    assert normal_score["score"] > no_update_score["score"] + EQUIV_BAND
    assert normal_score["score"] > no_pe_score["score"] + EQUIV_BAND
    assert normal["serialized_state"]["n_updates"] > no_update["serialized_state"]["n_updates"]


def test_action_conditioning_changes_predictions():
    normal, normal_score = _scored("candidate")
    no_action, no_action_score = _scored("no_action_conditioning")

    assert normal_score["score"] > no_action_score["score"] + EQUIV_BAND
    assert normal["predictions"] != no_action["predictions"]


def test_serialized_state_is_posterior_not_probe_lookup_table():
    result, _ = _scored("candidate")
    state = result["serialized_state"]

    assert "theta" not in state
    assert "truth_outcome" not in state
    assert "probe_history" not in state
    assert state["state_size_class"] == "O(d^2)"
    assert result["uses_future_observations"] is False
