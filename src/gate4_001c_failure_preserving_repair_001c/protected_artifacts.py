from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from . import core


PROTECTED_NAME_TOKENS = [
    "gate0",
    "gate1",
    "gate2",
    "gate3",
    "gate4",
    "evidence_harness",
    "admission",
]

EXPLICIT_PROTECTED_PATHS = [
    "artifacts/ego_mainline_gate4_preflight_executable_001b",
    "artifacts/gate4_001c_failure_preserving_repair_task_card_001a",
    "artifacts/gate4_001c_failure_preserving_repair_task_card_001b_amendment",
    "artifacts/evidence_harness_critical_risk_target_application_001a",
    "artifacts/evidence_harness_contract_enforcement_smoke_001a",
    "docs/research/AUDIT-GATE4-001C-FAILURE-PRESERVING-REPAIR-TASK-CARD-001A-CLAUDE-001.md",
    "docs/research/AUDIT-GATE4-001C-FAILURE-PRESERVING-REPAIR-TASK-CARD-001B-AMENDMENT-CLAUDE-001.md",
    "docs/codex/tasks/GATE4-001C-FAILURE-PRESERVING-REPAIR-TASK-CARD-001A.md",
    "docs/codex/tasks/GATE4-001C-FAILURE-PRESERVING-REPAIR-TASK-CARD-001B-AMENDMENT.md",
    "docs/codex/tasks/GATE4-001C-EXECUTION-TASK-CARD-001A.md",
]


def _iter_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    if path.is_file():
        return [path]
    return sorted(item for item in path.rglob("*") if item.is_file())


def protected_roots(repo_root: Path) -> list[Path]:
    roots: dict[str, Path] = {}
    artifacts = repo_root / "artifacts"
    if artifacts.exists():
        for child in artifacts.iterdir():
            if not child.is_dir() or child.name == core.TASK_SLUG:
                continue
            if any(token in child.name.lower() for token in PROTECTED_NAME_TOKENS):
                roots[child.resolve().as_posix()] = child
    for rel in EXPLICIT_PROTECTED_PATHS:
        path = repo_root / rel
        if path.exists():
            roots[path.resolve().as_posix()] = path
    return sorted(roots.values(), key=lambda item: item.as_posix())


def build_hash_inventory(phase: str, config_path: Path, repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or core.repo_root()
    config = core.load_config(config_path)
    files: dict[str, str] = {}
    missing_roots = []
    roots = protected_roots(root)
    for protected_root in roots:
        if not protected_root.exists():
            missing_roots.append(core.rel_path(protected_root, root))
            continue
        for file_path in _iter_files(protected_root):
            files[core.rel_path(file_path, root)] = core.sha256_file(file_path)
    return {
        "task_id": core.TASK_ID,
        "phase": phase,
        "created_at_utc": core.utc_now(),
        "config_task_id": config["task_id"],
        "protected_root_count": len(roots),
        "protected_file_count": len(files),
        "missing_roots": missing_roots,
        "files": files,
    }


def compare_hash_inventories(before: dict[str, Any], after: dict[str, Any], repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or core.repo_root()
    before_files = before.get("files", {})
    after_files = after.get("files", {})
    added = sorted(set(after_files) - set(before_files))
    removed = sorted(set(before_files) - set(after_files))
    changed = sorted(path for path in set(before_files) & set(after_files) if before_files[path] != after_files[path])
    count = len(added) + len(removed) + len(changed)
    provenance = core.make_provenance(
        producer_function="compare_hash_inventories",
        input_artifacts=[
            f"artifacts/{core.TASK_SLUG}/protected_artifact_hashes_before.json",
            f"artifacts/{core.TASK_SLUG}/protected_artifact_hashes_after.json",
        ],
        run_id="protected_artifact_compare_run",
        aggregation_rule="count added, removed, or changed protected files",
        threshold_rule="protected artifact mutation violations must equal 0",
        root=root,
    )
    return {
        "task_id": core.TASK_ID,
        "created_at_utc": core.utc_now(),
        "before_phase": before.get("phase"),
        "after_phase": after.get("phase"),
        "added_protected_files": added,
        "removed_protected_files": removed,
        "changed_protected_files": changed,
        "mutation_violation_count": core.metric_value(count, provenance),
        "verdict": "protected_artifacts_unchanged" if count == 0 else "failed_old_artifact_mutation",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["before", "after", "compare"], required=True)
    parser.add_argument("--config")
    parser.add_argument("--out", required=True)
    parser.add_argument("--before")
    parser.add_argument("--after")
    args = parser.parse_args()

    out = Path(args.out)
    if args.phase in {"before", "after"}:
        if not args.config:
            raise SystemExit("--config is required for before/after phases")
        payload = build_hash_inventory(args.phase, Path(args.config))
    else:
        if not args.before or not args.after:
            raise SystemExit("--before and --after are required for compare phase")
        payload = compare_hash_inventories(core.read_json(Path(args.before)), core.read_json(Path(args.after)))
    core.write_json(out, payload)
    print(payload["verdict"] if "verdict" in payload else f"{args.phase}_hash_inventory_written")


if __name__ == "__main__":
    main()
