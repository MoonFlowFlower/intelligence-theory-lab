import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_source_pin_records_blob_hashes_and_tamper_after_anchor_blocks(tmp_path):
    from acp_bv_distribution_harness_001b import source_boundary

    pin = source_boundary.create_source_pin(
        repo_root=ROOT,
        run_id="pytest-source-pin",
        output_artifact_path=tmp_path / "source_pin.json",
    )
    verification = source_boundary.verify_source_pin(pin, repo_root=ROOT)
    tamper = source_boundary.run_tamper_after_anchor_control(pin, repo_root=ROOT)

    assert pin["source_anchor_commit"] == "55e79259203f0544e9256befcc0c82ea668d2381"
    assert verification["passed"] is True
    assert verification["rejects_self_declared_repo_source_owned"] is True
    assert all(row["blob_hash"] for row in pin["source_files"])
    assert all(row["source_path"].startswith("src/acp_bv_distribution_harness_001b/") for row in pin["source_files"])
    assert tamper["actual_flip"] is True
    assert tamper["verdict_after_intervention"] == "blocked_by_source_boundary_failure"


def test_runner_persists_source_boundary_and_forbidden_scope_scan(tmp_path):
    from acp_bv_distribution_harness_001b import runner

    out = tmp_path / "run"
    runner.run_harness(repo_root=ROOT, output_dir=out, run_id="pytest-source-boundary")

    source_pin = _load_json(out / "source_pin.json")
    boundary = _load_json(out / "source_boundary.json")
    forbidden_scope_scan = (out / "forbidden_scope_scan.txt").read_text(encoding="utf-8")

    assert source_pin["verification"]["passed"] is True
    assert boundary["source_boundary_verdict"] == "source_boundary_pass"
    assert boundary["tamper_after_anchor_control"]["actual_flip"] is True
    assert boundary["self_declared_repo_source_owned_accepted"] is False
    assert "forbidden_scope_violation=false" in forbidden_scope_scan
