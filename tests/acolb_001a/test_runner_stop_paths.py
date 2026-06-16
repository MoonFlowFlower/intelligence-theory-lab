import json

from acolb_001a.runner import EXPECTED_ARTIFACTS, run


def test_runner_preserves_saturated_stop_as_failure_manifest(tmp_path):
    output_dir = tmp_path / "saturated"
    result = run(output_dir=output_dir, fixture="saturated")

    assert result["verdict"] == "saturated_close"
    assert result["mechanism_claim_admitted"] is False
    failure = json.loads((output_dir / "failure_manifest.json").read_text(encoding="utf-8"))
    assert "blocked_by_saturated_distribution" in failure["stop_conditions"]


def test_runner_default_writes_expected_artifacts_without_forbidden_paths(tmp_path):
    output_dir = tmp_path / "normal"
    result = run(output_dir=output_dir, fixture="normal")
    names = {path.name for path in output_dir.iterdir() if path.is_file()}
    parity = json.loads((output_dir / "parity_report.json").read_text(encoding="utf-8"))
    failure = json.loads((output_dir / "failure_manifest.json").read_text(encoding="utf-8"))
    ablation = json.loads((output_dir / "ablation_report.json").read_text(encoding="utf-8"))
    replay = json.loads((output_dir / "replay_report.json").read_text(encoding="utf-8"))
    leakage = json.loads((output_dir / "leakage_report.json").read_text(encoding="utf-8"))

    assert result["verdict"] == "saturated_close"
    assert set(EXPECTED_ARTIFACTS) | {"failure_manifest.json"} <= names
    assert "blocked_by_saturated_distribution" in failure["stop_conditions"]
    assert ablation["skipped"] is True
    assert replay["skipped"] is True
    assert leakage["skipped"] is True
    assert result["claim_ceiling"].startswith("Phase 0 blocker evidence only")
    assert all(str(path).startswith(str(output_dir)) for path in output_dir.rglob("*"))
    assert "fair_baseline_sensitivity.json" in names
    assert parity["aggregation_rule"] == "mean_episode_score"
