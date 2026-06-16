from __future__ import annotations

import hashlib
import inspect
import json
import subprocess
from pathlib import Path
from typing import Any, Callable, Iterable


THRESHOLDS = {
    "equivalence_lt": 0.02,
    "inconclusive_gte": 0.02,
    "inconclusive_lt": 0.05,
    "mechanism_relevant_effect_gte": 0.05,
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_source_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes().replace(b"\r\n", b"\n"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def source_path(callable_obj: Callable[..., Any]) -> Path:
    path = inspect.getsourcefile(callable_obj)
    if path is None:
        raise ValueError(f"callable has no source file: {callable_obj!r}")
    return Path(path).resolve()


def source_hash(callable_obj: Callable[..., Any]) -> str:
    return sha256_source_file(source_path(callable_obj))


def entrypoint(callable_obj: Callable[..., Any]) -> str:
    return f"{callable_obj.__module__}:{callable_obj.__name__}"


def relpath(path: Path, repo_root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def git_value(repo_root: Path, args: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return completed.stdout.strip()


def git_readback(repo_root: Path) -> dict[str, Any]:
    branch = git_value(repo_root, ["branch", "--show-current"])
    head = git_value(repo_root, ["rev-parse", "HEAD"])
    status = git_value(repo_root, ["status", "--short", "--branch"])
    diff_name_status = git_value(repo_root, ["diff", "--name-status"])
    return {
        "branch": branch,
        "head": head,
        "status_short_branch": status,
        "diff_name_status": diff_name_status or "",
    }


def provenance_for(
    callable_obj: Callable[..., Any],
    *,
    repo_root: Path,
    inputs: dict[str, Any],
    run_id: str,
    seed_context_episode_ids: list[dict[str, str]],
    aggregation_method: str,
    output_artifact_path: Path,
) -> dict[str, Any]:
    src = source_path(callable_obj)
    src_hash = sha256_source_file(src)
    input_digest = sha256_text(json.dumps(inputs, sort_keys=True, default=str))
    return {
        "producer_function": callable_obj.__name__,
        "producer_entrypoint": entrypoint(callable_obj),
        "source_path": relpath(src, repo_root),
        "source_hash": src_hash,
        "inputs": inputs,
        "input_artifact_hash": input_digest,
        "run_id": run_id,
        "seed_context_episode_ids": seed_context_episode_ids,
        "aggregation_method": aggregation_method,
        "output_artifact_path": relpath(output_artifact_path, repo_root),
        "code_path_hash": src_hash,
    }


def classify_delta(delta: float) -> str:
    if delta < THRESHOLDS["equivalence_lt"]:
        return "baseline_equivalent"
    if delta < THRESHOLDS["inconclusive_lt"]:
        return "inconclusive"
    return "mechanism_relevant_effect_candidate"


def seed_ids(episodes: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "seed": str(episode["seed"]),
            "context_id": str(episode["context_id"]),
            "episode_id": str(episode["episode_id"]),
        }
        for episode in episodes
    ]


def stable_run_command(module: str, output_dir: Path, run_id: str) -> str:
    return f"python -m {module} --output-dir {output_dir.as_posix()} --run-id {run_id}"
