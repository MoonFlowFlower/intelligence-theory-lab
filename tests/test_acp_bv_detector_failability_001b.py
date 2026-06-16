import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

DETECTORS = {
    "novelty_floor_detector",
    "baseline_tie_detector",
    "factorized_lookup_equivalence_detector",
    "multi_seed_stability_detector",
    "candidate_truth_coupling_detector",
    "leakage_detector",
    "source_boundary_detector",
    "replay_recomputation_detector",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_every_operational_detector_has_executed_expected_flip_control(tmp_path):
    from acp_bv_distribution_harness_001b import runner

    out = tmp_path / "run"
    runner.run_harness(repo_root=ROOT, output_dir=out, run_id="pytest-detectors")
    report = _load_json(out / "detector_failability.json")

    assert {row["detector_name"] for row in report["controls"]} == DETECTORS
    assert report["all_controls_executed"] is True
    assert report["all_actual_flips_match_predeclared"] is True
    assert report["all_controls_discriminated"] is True
    assert report["verdict_if_any_mismatch"] == "blocked_by_non_fail_able_detector"
    assert all(row["actual_flip"] == row["predeclared_expected_flip"] for row in report["controls"])
    assert all(row["real_detector_invoked"] is True for row in report["controls"])
    assert all(row["actual_verdict_before"] == row["expected_verdict_before"] for row in report["controls"])
    assert all(row["actual_verdict_after"] == row["expected_verdict_after"] for row in report["controls"])
    assert all(row["producer_function"] for row in report["controls"])
    assert all(row["code_path_hash"] for row in report["controls"])
    assert all(row["artifact_path"] for row in report["controls"])


def test_detector_failability_blocks_when_expected_flip_diverges():
    from acp_bv_distribution_harness_001b import detectors

    broken = [
        detectors.DetectorControl(
            detector_name="baseline_tie_detector",
            expected_intervention="force baseline tie",
            expected_verdict_before="clean",
            expected_verdict_after="blocked_by_baseline_equivalence",
            expected_flip=True,
            actual_verdict_before="clean",
            actual_verdict_after="clean",
            producer_function="pytest.synthetic_control",
            input_fixture_episode_ids=["ep.synthetic"],
            run_id="pytest-detector-divergence",
            seed=1009,
            source_path="tests/test_acp_bv_detector_failability_001b.py",
            code_path_hash="0" * 64,
            artifact_path="artifacts/synthetic.json",
        )
    ]

    report = detectors.summarize_detector_controls(broken)

    assert report["all_actual_flips_match_predeclared"] is False
    assert report["blocking_verdict"] == "blocked_by_non_fail_able_detector"
    assert report["controls"][0]["actual_flip"] is False
    assert report["controls"][0]["predeclared_expected_flip"] is True


def test_detector_failability_blocks_when_flip_happens_without_expected_discrimination():
    from acp_bv_distribution_harness_001b import detectors

    wrong_discrimination = [
        detectors.DetectorControl(
            detector_name="candidate_truth_coupling_detector",
            expected_intervention="swap in oracle stub",
            expected_verdict_before="clean",
            expected_verdict_after="blocked_by_candidate_truth_coupling",
            expected_flip=True,
            actual_verdict_before="blocked_by_candidate_truth_coupling",
            actual_verdict_after="clean",
            producer_function="pytest.synthetic_control",
            input_fixture_episode_ids=["ep.synthetic"],
            run_id="pytest-detector-wrong-discrimination",
            seed=1009,
            source_path="tests/test_acp_bv_detector_failability_001b.py",
            code_path_hash="1" * 64,
            artifact_path="artifacts/synthetic.json",
            real_detector_invoked=True,
        )
    ]

    report = detectors.summarize_detector_controls(wrong_discrimination)

    assert report["all_actual_flips_match_predeclared"] is True
    assert report["all_controls_discriminated"] is False
    assert report["blocking_verdict"] == "blocked_by_non_fail_able_detector"
