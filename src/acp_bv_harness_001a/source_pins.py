from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from . import START_COMMIT
from . import boundary
from .common import entrypoint, git_value, relpath, sha256_file, source_path, write_json


def bootstrap_check_verifier_source_pin(verifier_source_path: Path, expected_hash: str) -> dict[str, Any]:
    actual_hash = sha256_file(verifier_source_path)
    return {
        "bootstrap_checker_entrypoint": entrypoint(bootstrap_check_verifier_source_pin),
        "verifier_source_path": str(verifier_source_path.resolve()),
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
        "passed": actual_hash == expected_hash,
    }


def _callable_record(role: str, callable_obj: Callable[..., Any], repo_root: Path) -> dict[str, Any]:
    path = source_path(callable_obj)
    source_hash = sha256_file(path)
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
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    verifier = boundary.verify_callable_source_boundary
    verifier_path = source_path(verifier)
    verifier_hash = sha256_file(verifier_path)
    bootstrap_path = source_path(bootstrap_check_verifier_source_pin)
    bootstrap_hash = sha256_file(bootstrap_path)
    load_bearing_callables = load_bearing_callables or {"boundary_verifier": verifier}
    callable_records = {
        role: _callable_record(role, callable_obj, repo_root)
        for role, callable_obj in load_bearing_callables.items()
    }
    bootstrap = bootstrap_check_verifier_source_pin(verifier_path, verifier_hash)
    manifest = {
        "run_id": run_id,
        "git_commit": git_value(repo_root, ["rev-parse", "HEAD"]) or START_COMMIT,
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
    current_verifier_hash = sha256_file(verifier_path)
    current_bootstrap_hash = sha256_file(bootstrap_path)
    verifier_match = current_verifier_hash == manifest["verifier_source_hash"]
    bootstrap_match = current_bootstrap_hash == manifest["bootstrap_checker_source_hash"]
    bootstrap_check = bootstrap_check_verifier_source_pin(
        verifier_path,
        manifest["verifier_source_hash"],
    )
    passed = verifier_match and bootstrap_match and bootstrap_check["passed"]
    return {
        "passed": passed,
        "block_reason": None if passed else "blocked_by_unpinned_boundary_verifier",
        "verifier_hash_match": verifier_match,
        "bootstrap_hash_match": bootstrap_match,
        "bootstrap_check": bootstrap_check,
        "current_verifier_source_hash": current_verifier_hash,
        "expected_verifier_source_hash": manifest["verifier_source_hash"],
        "current_bootstrap_checker_source_hash": current_bootstrap_hash,
        "expected_bootstrap_checker_source_hash": manifest["bootstrap_checker_source_hash"],
    }
