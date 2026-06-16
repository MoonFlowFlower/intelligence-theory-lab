from acolb_001a.generator import generate_episode
from acolb_001a.leakage import scan_import_boundaries, scan_legal_episode
from acolb_001a.legal_view import LEGAL_KEYS, to_legal_episode


def test_legal_view_has_closed_key_set():
    legal = to_legal_episode(generate_episode("id", 3001, 0))

    for row in legal["probes"] + legal["queries"]:
        assert set(row) <= LEGAL_KEYS


def test_clean_legal_episode_has_no_forbidden_or_answer_bearing_fields():
    legal = to_legal_episode(generate_episode("ood", 5001, 0))
    report = scan_legal_episode(legal)

    assert report["scanner_fired"] is False
    assert report["hits"] == []


def test_candidate_baseline_and_replay_do_not_import_generator_truth_path():
    report = scan_import_boundaries()

    assert report["scanner_fired"] is False
    assert report["hits"] == []
