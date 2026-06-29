import json
import shutil

from itl_devbench.eval.replay import replay_manifest
from itl_devbench.eval.run_matrix import run_benchmark


def test_replay_of_smoke_trace_succeeds(tmp_path):
    run_dir = run_benchmark(
        config={"width": 7, "height": 7, "max_ticks": 12, "smoke_seeds": [0]},
        smoke=True,
        output_root=tmp_path,
    )

    report = replay_manifest(run_dir / "manifest.json")

    assert report["verdict"] == "replay_succeeded"
    assert report["metrics_match"] is True


def test_tampered_action_reward_or_hash_causes_replay_failure(tmp_path):
    run_dir = run_benchmark(
        config={"width": 7, "height": 7, "max_ticks": 12, "smoke_seeds": [0]},
        smoke=True,
        output_root=tmp_path,
    )
    trace_path = run_dir / "trace.jsonl"
    lines = trace_path.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["reward"] = first["reward"] + 99
    first["event_hash"] = "tampered"
    lines[0] = json.dumps(first, sort_keys=False)
    trace_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = replay_manifest(run_dir / "manifest.json")

    assert report["verdict"] == "replay_failed_evidence_invalid"
    assert report["replay_ok"] is False


def test_replay_metrics_hash_is_stable_when_run_is_copied_to_latest_path(tmp_path):
    run_dir = run_benchmark(
        config={"width": 7, "height": 7, "max_ticks": 12, "smoke_seeds": [0]},
        smoke=True,
        output_root=tmp_path / "runs",
    )
    latest_dir = tmp_path / "latest"
    shutil.copytree(run_dir, latest_dir)

    report = replay_manifest(latest_dir / "manifest.json")

    assert report["verdict"] == "replay_succeeded"
    assert report["metrics_match"] is True
