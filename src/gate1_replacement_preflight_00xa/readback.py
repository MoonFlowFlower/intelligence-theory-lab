from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable


SURFACE_SPEC_PATH = "docs/research/gate1_replacement_surface_spec_00xa.md"
SURFACE_FREEZE_PATH = "docs/research/gate1_replacement_surface_spec_00xa.freeze.json"
GENERATOR_SOURCE_PATH = "src/gate1_replacement_preflight_00xa/spec_loader.py"
EXPECTED_SURFACE_SPEC_SHA256 = "fca7e5ebcd5b1042cda57d88790347f487eaad33182aa91f00640621014fa9c9"

REQUIRED_SOURCE_PINS = [
    "artifacts/CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-PREFLIGHT-00XA-RUN-001A-HOSTILE-AUDIT-001A/audit_result.json",
    "artifacts/CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-PREFLIGHT-00XA-RUN-001A-HOSTILE-AUDIT-001A/audit_report.md",
    "docs/codex/tasks/GATE1-REPLACEMENT-PREFLIGHT-00XA.md",
    "artifacts/CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-PREFLIGHT-00XA-IMPLEMENTATION-CARD-HOSTILE-AUDIT-001A/audit_result.json",
    "artifacts/CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-PREFLIGHT-00XA-IMPLEMENTATION-CARD-HOSTILE-AUDIT-001A/audit_report.md",
    SURFACE_SPEC_PATH,
    SURFACE_FREEZE_PATH,
    GENERATOR_SOURCE_PATH,
    "artifacts/gate1_replacement_preflight_00xa_run_001a/final_verdict.json",
    "artifacts/gate1_replacement_preflight_00xa_run_001a/source_readback.json",
    "artifacts/CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-SURFACE-SPEC-00XA-CORE-HOSTILE-AUDIT-001A/audit_result.json",
    "artifacts/CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-SURFACE-SPEC-00XA-CORE-HOSTILE-AUDIT-001A/audit_report.md",
    "artifacts/gate1_replacement_readback_or_preflight_selection_001a/selected_verdict.json",
    "artifacts/gate1_replacement_readback_or_preflight_selection_001a/gate1_failure_readback.json",
    "artifacts/gate1_replacement_readback_or_preflight_selection_001a/gate_dependency_readback.json",
    "docs/research/GATE1-FAILED-GRAPH-CACHE-RECONCILIATION-001A.md",
    "artifacts/post_freeze_gate0_3_sequential_repair_queue_001a_gate1_failed_graph_cache_reconciliation/baseline_comparison.json",
    "docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md",
    "docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.registry.json",
    "artifacts/CLAUDE-INDEPENDENT-GATE-EVIDENCE-PROVENANCE-VERIFIER-001A-HOSTILE-AUDIT-001A/audit_result.json",
]

MUTATION_BANNED_PATHS = {SURFACE_SPEC_PATH, SURFACE_FREEZE_PATH}


def normalize_repo_path(path: str | Path) -> str:
    return Path(path).as_posix().lstrip("./").lower()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _row_for_path(repo_root: Path, rel_path: str, run_id: str) -> dict:
    path = repo_root / rel_path
    row = {
        "path": rel_path,
        "run_id": run_id,
        "readback_channel": "canonical_file_api_read_bytes",
        "exists": path.exists(),
        "input_artifacts": [rel_path],
        "producer_function": "gate1_replacement_preflight_00xa.readback._row_for_path",
        "aggregation_rule": "sha256_of_exact_file_bytes",
        "consumed_by_final_verdict": True,
    }
    if path.exists():
        data = path.read_bytes()
        row.update({"sha256": hashlib.sha256(data).hexdigest(), "byte_count": len(data)})
    else:
        row.update({"sha256": None, "byte_count": 0})
    return row


def read_source_pins(
    repo_root: str | Path,
    run_id: str,
    required_pins: Iterable[str] = REQUIRED_SOURCE_PINS,
) -> dict:
    root = Path(repo_root)
    source_pins = [_row_for_path(root, rel_path, run_id) for rel_path in required_pins]
    missing = [row["path"] for row in source_pins if not row["exists"]]
    hash_conflicts = []
    for row in source_pins:
        if row["path"] == SURFACE_SPEC_PATH and row["sha256"] != EXPECTED_SURFACE_SPEC_SHA256:
            hash_conflicts.append(
                {
                    "path": row["path"],
                    "expected_sha256": EXPECTED_SURFACE_SPEC_SHA256,
                    "actual_sha256": row["sha256"],
                }
            )
    return {
        "schema_version": "gate1_replacement_preflight_00xa_source_readback_v1",
        "run_id": run_id,
        "producer_function": "gate1_replacement_preflight_00xa.readback.read_source_pins",
        "input_artifacts": list(required_pins),
        "readback_channel": "canonical_file_api_read_bytes",
        "source_pins": source_pins,
        "missing": missing,
        "all_present": not missing,
        "hash_conflicts": hash_conflicts,
        "fail_closed_on_missing_or_conflict": True,
        "consumed_by_final_verdict": True,
    }


def verify_surface_spec_hash(
    repo_root: str | Path,
    implementer_touched_paths: Iterable[str | Path] | None = None,
) -> dict:
    touched = {normalize_repo_path(path) for path in (implementer_touched_paths or [])}
    banned = {normalize_repo_path(path) for path in MUTATION_BANNED_PATHS}
    if touched & banned:
        return {
            "ok": False,
            "verdict": "blocked_candidate_authored_or_mutated_surface_spec",
            "mutation_detected": True,
            "touched_banned_paths": sorted(touched & banned),
            "expected_sha256": EXPECTED_SURFACE_SPEC_SHA256,
            "readback_channel": "canonical_file_api_read_bytes",
            "consumed_by_final_verdict": True,
        }

    path = Path(repo_root) / SURFACE_SPEC_PATH
    if not path.exists():
        return {
            "ok": False,
            "verdict": "blocked_missing_candidate_free_surface_spec",
            "mutation_detected": False,
            "path": SURFACE_SPEC_PATH,
            "expected_sha256": EXPECTED_SURFACE_SPEC_SHA256,
            "actual_sha256": None,
            "readback_channel": "canonical_file_api_read_bytes",
            "consumed_by_final_verdict": True,
        }

    actual = file_sha256(path)
    ok = actual == EXPECTED_SURFACE_SPEC_SHA256
    return {
        "ok": ok,
        "verdict": "surface_spec_hash_verified" if ok else "blocked_candidate_authored_or_mutated_surface_spec",
        "mutation_detected": not ok,
        "path": SURFACE_SPEC_PATH,
        "expected_sha256": EXPECTED_SURFACE_SPEC_SHA256,
        "actual_sha256": actual,
        "readback_channel": "canonical_file_api_read_bytes",
        "consumed_by_final_verdict": True,
    }
