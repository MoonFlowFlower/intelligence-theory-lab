import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_replay_recomputes_candidate_behavior_from_state_and_observation(tmp_path):
    from acp_bv_distribution_harness_001b import candidate, generator, replay

    dataset = generator.generate_distribution(seed=1009, heldout_count=128)
    fitted = candidate.fit_candidate(dataset["train"])
    outputs = candidate.run_candidate(fitted, dataset["heldout"])

    report = replay.recompute_candidate_outputs(
        serialized_state=fitted,
        episodes=dataset["heldout"],
        candidate_outputs=outputs,
        run_id="pytest-replay",
        output_artifact_path=tmp_path / "replay_results.json",
    )

    assert report["verdict"] == "replay_recomputed"
    assert report["behavior_recomputed"] is True
    assert report["hash_only"] is False
    assert report["used_serialized_state"] is True
    assert report["used_observation"] is True
    assert report["mismatch_count"] == 0
    assert report["negative_control"]["actual_flip"] is True
    assert report["negative_control"]["verdict_after_intervention"] == "blocked_by_replay_recomputation_failure"


def test_runner_persists_replay_negative_control(tmp_path):
    from acp_bv_distribution_harness_001b import runner

    out = tmp_path / "run"
    runner.run_harness(repo_root=ROOT, output_dir=out, run_id="pytest-replay-runner")
    replay_report = _load_json(out / "replay_results.json")

    assert replay_report["verdict"] == "replay_recomputed"
    assert replay_report["negative_control"]["expected_flip"] is True
    assert replay_report["negative_control"]["actual_flip"] is True
    assert replay_report["negative_control"]["accepted_hash_only"] is False
