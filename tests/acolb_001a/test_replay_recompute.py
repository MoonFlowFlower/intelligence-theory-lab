from acolb_001a.candidate import run_candidate
from acolb_001a.generator import generate_episode
from acolb_001a.legal_view import to_legal_episode
from acolb_001a.replay import replay_candidate_run


def test_replay_recomputes_posterior_and_predictions():
    legal = to_legal_episode(generate_episode("ood", 5001, 0))
    candidate_run = run_candidate(legal)
    report = replay_candidate_run(candidate_run, legal)

    assert report["trajectory_match"] is True
    assert report["query_match"] is True
    assert report["recomputed_not_hashed"] is True
    assert report["tamper_control"]["corrupted_state_replay_failed"] is True


def test_replay_fails_for_corrupted_serialized_state():
    legal = to_legal_episode(generate_episode("ood", 5002, 0))
    candidate_run = run_candidate(legal)
    candidate_run["serialized_state"]["posterior_mean"][0] += 99.0
    report = replay_candidate_run(candidate_run, legal, run_tamper_control=False)

    assert report["trajectory_match"] is False
    assert report["query_match"] is False
