from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, Callable

from .common import entrypoint, relpath, sha256_file, source_path


def _resolve(path: Path) -> Path:
    return path.expanduser().resolve()


def _is_under(path: Path, root: Path) -> bool:
    path = _resolve(path)
    root = _resolve(root)
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _in_any_root(path: Path, roots: list[Path]) -> bool:
    return any(_is_under(path, root) for root in roots)


def _influence_present(influence: dict[str, Any] | None, names: list[str]) -> bool:
    if not influence:
        return False
    return any(name in influence and influence[name] not in (None, False, {}, [], "") for name in names)


def verify_callable_source_boundary(
    callable_obj: Callable[..., Any],
    *,
    repo_root: Path,
    candidate_writable_roots: list[Path],
    candidate_artifact_roots: list[Path],
    generated_output_roots: list[Path] | None = None,
    influence: dict[str, Any] | None = None,
    expected_source_hash: str | None = None,
) -> dict[str, Any]:
    """Derive callable ownership from real source path boundaries."""
    generated_output_roots = generated_output_roots or []
    repo_root = _resolve(repo_root)
    repo_source_root = repo_root / "src" / "acp_bv_harness_001a"
    block_reasons: list[str] = []

    source_file = inspect.getsourcefile(callable_obj)
    if source_file is None:
        resolved = None
        source_hash = None
        block_reasons.append("missing_source_file")
    else:
        resolved = _resolve(Path(source_file))
        source_hash = sha256_file(resolved)

    repo_source_root_match = bool(resolved and _is_under(resolved, repo_source_root))
    candidate_writable_root_match = bool(resolved and _in_any_root(resolved, candidate_writable_roots))
    candidate_artifact_root_match = bool(resolved and _in_any_root(resolved, candidate_artifact_roots))
    generated_output_root_match = bool(resolved and _in_any_root(resolved, generated_output_roots))

    if not repo_source_root_match:
        block_reasons.append("not_repo_source_owned")
    if candidate_writable_root_match:
        block_reasons.append("candidate_writable_source")
    if candidate_artifact_root_match:
        block_reasons.append("candidate_artifact_source")
    if generated_output_root_match:
        block_reasons.append("generated_code_source")
    if expected_source_hash and source_hash != expected_source_hash:
        block_reasons.append("source_hash_mismatch")

    candidate_config_influence = _influence_present(influence, ["candidate_config"])
    candidate_serialized_state_influence = _influence_present(influence, ["candidate_serialized_state"])
    candidate_policy_map_influence = _influence_present(influence, ["candidate_policy_map"])
    candidate_label_or_logit_influence = _influence_present(
        influence,
        ["candidate_label", "candidate_labels", "candidate_logit", "candidate_logits"],
    )
    candidate_score_or_verdict_influence = _influence_present(
        influence,
        ["candidate_score", "candidate_verdict", "candidate_confidence", "candidate_error"],
    )
    if candidate_config_influence:
        block_reasons.append("candidate_config_influence")
    if candidate_serialized_state_influence:
        block_reasons.append("candidate_serialized_state_influence")
    if candidate_policy_map_influence:
        block_reasons.append("candidate_policy_map_influence")
    if candidate_label_or_logit_influence:
        block_reasons.append("candidate_label_or_logit_influence")
    if candidate_score_or_verdict_influence:
        block_reasons.append("candidate_score_or_verdict_influence")

    candidate_inaccessible = (
        repo_source_root_match
        and not candidate_writable_root_match
        and not candidate_artifact_root_match
        and not generated_output_root_match
        and not candidate_config_influence
        and not candidate_serialized_state_influence
        and not candidate_policy_map_influence
        and not candidate_label_or_logit_influence
        and not candidate_score_or_verdict_influence
    )
    verdict = "source_boundary_pass" if repo_source_root_match and candidate_inaccessible and not block_reasons else "source_boundary_blocked"

    return {
        "callable_entrypoint": entrypoint(callable_obj),
        "resolved_source_path": relpath(resolved, repo_root) if resolved else None,
        "normalized_realpath": str(resolved) if resolved else None,
        "source_hash": source_hash,
        "repo_source_root_match": repo_source_root_match,
        "candidate_writable_root_match": candidate_writable_root_match,
        "candidate_artifact_root_match": candidate_artifact_root_match,
        "generated_output_root_match": generated_output_root_match,
        "candidate_config_influence_detected": candidate_config_influence,
        "candidate_serialized_state_influence_detected": candidate_serialized_state_influence,
        "candidate_policy_map_influence_detected": candidate_policy_map_influence,
        "candidate_label_or_logit_influence_detected": candidate_label_or_logit_influence,
        "candidate_score_or_verdict_influence_detected": candidate_score_or_verdict_influence,
        "repo_source_owned_derived": repo_source_root_match,
        "candidate_inaccessible_derived": candidate_inaccessible,
        "self_declared_ownership_accepted": False,
        "boundary_verdict": verdict,
        "block_reasons": sorted(set(block_reasons)),
    }


def verify_many(
    callables: dict[str, Callable[..., Any]],
    *,
    repo_root: Path,
    candidate_writable_roots: list[Path],
    candidate_artifact_roots: list[Path],
    expected_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    expected_hashes = expected_hashes or {}
    checks = {
        role: verify_callable_source_boundary(
            callable_obj,
            repo_root=repo_root,
            candidate_writable_roots=candidate_writable_roots,
            candidate_artifact_roots=candidate_artifact_roots,
            expected_source_hash=expected_hashes.get(role),
        )
        for role, callable_obj in callables.items()
    }
    return {
        "checks": checks,
        "all_passed": all(check["boundary_verdict"] == "source_boundary_pass" for check in checks.values()),
        "self_declared_ownership_accepted": False,
    }


def callable_source_hash(callable_obj: Callable[..., Any]) -> str:
    return sha256_file(source_path(callable_obj))
