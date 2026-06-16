from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Callable

from . import START_COMMIT
from . import boundary
from .common import entrypoint, git_value, relpath, sha256_bytes, sha256_source_file, source_path, write_json


def bootstrap_check_verifier_source_pin(verifier_source_path: Path, expected_hash: str) -> dict[str, Any]:
    actual_hash = sha256_source_file(verifier_source_path)
    return {
        "bootstrap_checker_entrypoint": entrypoint(bootstrap_check_verifier_source_pin),
        "verifier_source_path": str(verifier_source_path.resolve()),
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
        "passed": actual_hash == expected_hash,
    }


def git_object_file_hash(repo_root: Path, source_anchor_commit: str, source_path: Path) -> str:
    rel_source_path = source_path.as_posix()
    completed = subprocess.run(
        ["git", "cat-file", "blob", f"{source_anchor_commit}:{rel_source_path}"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return sha256_bytes(completed.stdout)


def create_frozen_source_anchor(
    *,
    repo_root: Path,
    source_anchor_commit: str,
    source_paths: list[Path],
) -> dict[str, Any]:
    files = {}
    for source_path in source_paths:
        normalized = source_path.as_posix()
        files[normalized] = {
            "git_object_spec": f"{source_anchor_commit}:{normalized}",
            "expected_hash": git_object_file_hash(repo_root, source_anchor_commit, source_path),
            "hash_source": "git_object",
        }
    return {
        "source_anchor_commit": source_anchor_commit,
        "anchor_source": "git_object",
        "files": files,
    }


def verify_frozen_source_anchor(anchor: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    file_checks = {}
    for source_path, pinned in anchor.get("files", {}).items():
        live_path = repo_root / source_path
        current_hash = sha256_source_file(live_path)
        expected_hash = pinned["expected_hash"]
        file_checks[source_path] = {
            "current_hash": current_hash,
            "expected_hash": expected_hash,
            "hash_match": current_hash == expected_hash,
            "hash_source": pinned.get("hash_source"),
            "git_object_spec": pinned.get("git_object_spec"),
        }
    passed = all(check["hash_match"] for check in file_checks.values()) and bool(file_checks)
    return {
        "passed": passed,
        "block_reason": None if passed else "blocked_by_unpinned_boundary_verifier",
        "source_anchor_commit": anchor.get("source_anchor_commit"),
        "anchor_source": anchor.get("anchor_source"),
        "file_checks": file_checks,
    }


def _callable_record(role: str, callable_obj: Callable[..., Any], repo_root: Path) -> dict[str, Any]:
    path = source_path(callable_obj)
    source_hash = sha256_source_file(path)
    return {
        "role": role,
        "entrypoint": entrypoint(callable_obj),
        "source_path": relpath(path, repo_root),
        "source_hash": source_hash,
        "code_path_hash": source_hash,
    }


def create_source_pin_manifest(
    *,
    repo_root: Path,
    run_id: str,
    output_path: Path | None = None,
    load_bearing_callables: dict[str, Callable[..., Any]] | None = None,
    source_anchor_commit: str | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    verifier = boundary.verify_callable_source_boundary
    verifier_path = source_path(verifier)
    verifier_hash = sha256_source_file(verifier_path)
    bootstrap_path = source_path(bootstrap_check_verifier_source_pin)
    bootstrap_hash = sha256_source_file(bootstrap_path)
    load_bearing_callables = load_bearing_callables or {"boundary_verifier": verifier}
    callable_records = {
        role: _callable_record(role, callable_obj, repo_root)
        for role, callable_obj in load_bearing_callables.items()
    }
    source_paths = {
        Path(record["source_path"])
        for record in callable_records.values()
        if not Path(record["source_path"]).is_absolute()
    }
    source_paths.add(Path("src/acp_bv_harness_001a/boundary.py"))
    source_paths.add(Path("src/acp_bv_harness_001a/source_pins.py"))
    frozen_anchor = None
    if source_anchor_commit:
        frozen_anchor = create_frozen_source_anchor(
            repo_root=repo_root,
            source_anchor_commit=source_anchor_commit,
            source_paths=sorted(source_paths, key=lambda item: item.as_posix()),
        )
        verifier_hash = frozen_anchor["files"]["src/acp_bv_harness_001a/boundary.py"]["expected_hash"]
        bootstrap_hash = frozen_anchor["files"]["src/acp_bv_harness_001a/source_pins.py"]["expected_hash"]
        for role, record in callable_records.items():
            pinned = frozen_anchor["files"].get(record["source_path"])
            if pinned:
                record["source_hash"] = pinned["expected_hash"]
                record["code_path_hash"] = pinned["expected_hash"]
                record["hash_source"] = "git_object"
    bootstrap = bootstrap_check_verifier_source_pin(verifier_path, verifier_hash)
    manifest = {
        "run_id": run_id,
        "git_commit": source_anchor_commit or git_value(repo_root, ["rev-parse", "HEAD"]) or START_COMMIT,
        "source_pin_mode": "git_object_frozen_anchor" if source_anchor_commit else "live_source_manifest",
        "frozen_source_anchor": frozen_anchor,
        "verifier_source_path": relpath(verifier_path, repo_root),
        "verifier_source_hash": verifier_hash,
        "verifier_callable_entrypoint": entrypoint(verifier),
        "bootstrap_checker_entrypoint": entrypoint(bootstrap_check_verifier_source_pin),
        "bootstrap_checker_source_path": relpath(bootstrap_path, repo_root),
        "bootstrap_checker_source_hash": bootstrap_hash,
        "bootstrap_check": bootstrap,
        "load_bearing_callables": callable_records,
    }
    if output_path is not None:
        write_json(output_path, manifest)
    return manifest


def expected_hashes_by_role(manifest: dict[str, Any]) -> dict[str, str]:
    return {
        role: record["source_hash"]
        for role, record in manifest.get("load_bearing_callables", {}).items()
    }


def verify_source_pin_manifest(manifest: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    verifier_path = repo_root / manifest["verifier_source_path"]
    bootstrap_path = repo_root / manifest["bootstrap_checker_source_path"]
    current_verifier_hash = sha256_source_file(verifier_path)
    current_bootstrap_hash = sha256_source_file(bootstrap_path)
    verifier_match = current_verifier_hash == manifest["verifier_source_hash"]
    bootstrap_match = current_bootstrap_hash == manifest["bootstrap_checker_source_hash"]
    bootstrap_check = bootstrap_check_verifier_source_pin(
        verifier_path,
        manifest["verifier_source_hash"],
    )
    frozen_anchor_check = None
    if manifest.get("frozen_source_anchor"):
        frozen_anchor_check = verify_frozen_source_anchor(
            manifest["frozen_source_anchor"],
            repo_root=repo_root,
        )
    passed = (
        verifier_match
        and bootstrap_match
        and bootstrap_check["passed"]
        and (frozen_anchor_check is None or frozen_anchor_check["passed"])
    )
    return {
        "passed": passed,
        "block_reason": None if passed else "blocked_by_unpinned_boundary_verifier",
        "source_pin_mode": manifest.get("source_pin_mode", "live_source_manifest"),
        "frozen_source_anchor_check": frozen_anchor_check,
        "verifier_hash_match": verifier_match,
        "bootstrap_hash_match": bootstrap_match,
        "bootstrap_check": bootstrap_check,
        "current_verifier_source_hash": current_verifier_hash,
        "expected_verifier_source_hash": manifest["verifier_source_hash"],
        "current_bootstrap_checker_source_hash": current_bootstrap_hash,
        "expected_bootstrap_checker_source_hash": manifest["bootstrap_checker_source_hash"],
    }
