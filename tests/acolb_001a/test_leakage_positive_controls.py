from acolb_001a.generator import generate_episode
from acolb_001a.leakage import run_leakage_controls, scan_legal_episode
from acolb_001a.legal_view import to_legal_episode


def test_clean_scan_is_silent_and_positive_controls_fire(tmp_path):
    clean = scan_legal_episode(to_legal_episode(generate_episode("id", 3001, 0)))
    report = run_leakage_controls(output_dir=tmp_path)

    assert clean["scanner_fired"] is False
    assert report["clean_control_passed"] is True
    assert {row["control_id"] for row in report["controls"]} == {"L1", "L2", "L3", "L4", "L5", "L6"}
    assert all(row["positive_control_ok"] for row in report["controls"])
    assert all(row["scanner_fired"] for row in report["controls"])
    assert all("score_moved_as_expected" not in row for row in report["controls"])
