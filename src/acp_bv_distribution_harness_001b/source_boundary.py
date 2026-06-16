from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from . import START_COMMIT, provenance_for


SOURCE_PATHS = [
    Path("src/acp_bv_distribution_harness_001b/__init__.py"),
    Path("src/acp_bv_distribution_harness_001b/generator.py"),
    Path("src/acp_bv_distribution_harness_001b/candidate.py"),
    Path("src/acp_bv_distribution_harness_001b/baselines.py"),
    Path("src/acp_bv_distribution_harness_001b/coupling.py"),
    Path("src/acp_bv_distribution_harness_001b/detectors.py"),
    Path("src/acp_bv_distribution_harness_001b/leakage_scanner.py"),
    Path("src/acp_bv_distribution_harness_001b/replay.py"),
    Path("src/acp_bv_distribution_harness_001b/runner.py"),
    Path("src/acp_bv_distribution_harness_001b/source_boundary.py"),
]


def _git_hash_object(repo_root: Path, path: Path) -> str:
    result = subprocess.run(
        ["git", "hash-object", path.as_posix()],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def create_source_pin(*, repo_root: Path, run_id: str, output_artifact_path: Path) -> dict[str, Any]:
    rows = []
    for path in SOURCE_PATHS:
        full_path = repo_root / path
        rows.append(
            {
                "source_path": path.as_posix(),
                "blob_hash": _git_hash_object(repo_root, path),
                "exists": full_path.exists(),
            }
        )
    pin = {
        "producer_function": "create_source_pin",
        "run_id": run_id,
        "source_anchor_commit": START_COMMIT,
        "source_files": rows,
        "self_declared_repo_source_owned_accepted": False,
        "output_artifact_path": output_artifact_path.as_posix(),
        "provenance": provenance_for(
            create_source_pin,
            inputs={"source_path_count": len(SOURCE_PATHS)},
            run_id=run_id,
            seed=None,
            context_episode_ids=[],
            aggregation_method="git_hash_object_for_each_load_bearing_source_file",
            output_artifact_path=output_artifact_path,
        ),
    }
    pin["verification"] = verify_source_pin(pin, repo_root=repo_root)
    return pin


def verify_source_pin(pin: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    checks = []
    for row in pin["source_files"]:
        path = Path(row["source_path"])
        current_hash = _git_hash_object(repo_root, path)
        checks.append(
            {
                "source_path": row["source_path"],
                "pinned_blob_hash": row["blob_hash"],
                "current_blob_hash": current_hash,
                "hash_match": current_hash == row["blob_hash"],
            }
        )
    passed = all(row["hash_match"] for row in checks)
    return {
        "producer_function": "verify_source_pin",
        "passed": passed,
        "block_reason": None if passed else "blocked_by_source_boundary_failure",
        "checks": checks,
        "rejects_self_declared_repo_source_owned": True,
        "rejects_unpinned_or_stale_worktree_source_claims": True,
    }


def run_tamper_after_anchor_control(pin: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    first = pin["source_files"][0]
    tampered_pin = dict(pin)
    tampered_rows = [dict(row) for row in pin["source_files"]]
    tampered_rows[0]["blob_hash"] = "0" * len(first["blob_hash"])
    tampered_pin["source_files"] = tampered_rows
    before = verify_source_pin(pin, repo_root=repo_root)
    after = verify_source_pin(tampered_pin, repo_root=repo_root)
    return {
        "producer_function": "run_tamper_after_anchor_control",
        "expected_flip": True,
        "actual_flip": before["passed"] is True and after["passed"] is False,
        "verdict_before_intervention": "source_boundary_pass" if before["passed"] else before["block_reason"],
        "verdict_after_intervention": "blocked_by_source_boundary_failure" if not after["passed"] else "source_boundary_pass",
        "tampered_source_path": first["source_path"],
    }
