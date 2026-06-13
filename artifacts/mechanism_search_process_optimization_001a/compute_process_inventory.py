from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import uuid
from collections import Counter
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
REPO_ROOT = ARTIFACT_DIR.parents[1]
INPUT_PATH = ARTIFACT_DIR / "reviewed_task_inventory.json"
INVALID_FIXTURE_PATH = ARTIFACT_DIR / "invalid_inventory_fixture.json"
OUTPUT_PATH = ARTIFACT_DIR / "process_inventory_metrics.json"

ALLOWED_CATEGORIES = {
    "new_mechanism_signal",
    "negative_signal",
    "governance_only",
    "hygiene_only",
    "theater_risk",
    "unknown_requires_repo_readback",
}

REQUIRED_FIELDS = {
    "task_id",
    "source_doc_path",
    "source_artifact_path_or_null",
    "source_commit_or_tag_if_known",
    "layer",
    "verdict",
    "route_effect",
    "evidence_category",
    "cheap_baseline_issue_present",
    "same_family_repair_risk",
    "downstream_decision_changed",
    "support_excerpt_or_summary",
    "claim_ceiling",
}


class InventoryValidationError(Exception):
    pass


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def resolve_repo_path(raw_path: str | None) -> Path | None:
    if raw_path is None:
        return None
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    return candidate


def validate_inventory(rows: Any) -> list[dict[str, Any]]:
    if not isinstance(rows, list) or not rows:
        raise InventoryValidationError("inventory must be a non-empty list")

    errors: list[str] = []
    validated: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"row {index}: row must be an object")
            continue

        missing = sorted(REQUIRED_FIELDS - set(row))
        if missing:
            errors.append(f"row {index}: missing fields {missing}")
            continue

        task_id = row.get("task_id")
        if not isinstance(task_id, str) or not task_id.strip():
            errors.append(f"row {index}: task_id must be a non-empty string")

        doc_path = resolve_repo_path(row.get("source_doc_path"))
        if doc_path is None or not doc_path.exists():
            errors.append(f"row {index}: source_doc_path missing on disk")

        artifact_path = resolve_repo_path(row.get("source_artifact_path_or_null"))
        if artifact_path is not None and not artifact_path.exists():
            errors.append(f"row {index}: source_artifact_path_or_null missing on disk")

        verdict = row.get("verdict")
        if not isinstance(verdict, str) or not verdict.strip():
            errors.append(f"row {index}: verdict must be a non-empty string")

        claim_ceiling = row.get("claim_ceiling")
        if not isinstance(claim_ceiling, str) or not claim_ceiling.strip():
            errors.append(f"row {index}: claim_ceiling must be a non-empty string")

        category = row.get("evidence_category")
        if category not in ALLOWED_CATEGORIES:
            errors.append(f"row {index}: invalid evidence_category {category!r}")

        for bool_field in (
            "cheap_baseline_issue_present",
            "same_family_repair_risk",
            "downstream_decision_changed",
        ):
            if not isinstance(row.get(bool_field), bool):
                errors.append(f"row {index}: {bool_field} must be boolean")

        summary = row.get("support_excerpt_or_summary")
        if not isinstance(summary, str) or not summary.strip():
            errors.append(f"row {index}: support_excerpt_or_summary must be non-empty")

        validated.append(row)

    if errors:
        raise InventoryValidationError("; ".join(errors))

    return validated


def current_git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def code_path_hash() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def build_metrics(rows: list[dict[str, Any]], invalid_fixture_failed: bool) -> dict[str, Any]:
    generated_at = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    script_hash = code_path_hash()
    category_counts = dict(sorted(Counter(row["evidence_category"] for row in rows).items()))
    return {
        "producer_function": "compute_process_inventory",
        "script_path": relative_path(Path(__file__)),
        "input_path": relative_path(INPUT_PATH),
        "run_id": f"mechanism_search_process_optimization_001a_{generated_at.replace(':', '').replace('-', '')}_{uuid.uuid4().hex[:12]}",
        "current_head": current_git_head(),
        "aggregation": {
            "category_counts": "count rows by evidence_category",
            "downstream_decision_changed_count": "count rows where downstream_decision_changed is true",
            "cheap_baseline_issue_count": "count rows where cheap_baseline_issue_present is true",
            "same_family_repair_risk_count": "count rows where same_family_repair_risk is true"
        },
        "code_path_hash": script_hash,
        "generated_at_utc": generated_at,
        "category_counts": category_counts,
        "downstream_decision_changed_count": sum(1 for row in rows if row["downstream_decision_changed"]),
        "cheap_baseline_issue_count": sum(1 for row in rows if row["cheap_baseline_issue_present"]),
        "same_family_repair_risk_count": sum(1 for row in rows if row["same_family_repair_risk"]),
        "invalid_fixture_path": relative_path(INVALID_FIXTURE_PATH),
        "invalid_fixture_failed_as_expected": invalid_fixture_failed
    }


def validate_invalid_fixture() -> tuple[bool, str]:
    try:
        validate_inventory(load_json(INVALID_FIXTURE_PATH))
    except InventoryValidationError as exc:
        return True, str(exc)
    return False, "invalid fixture unexpectedly passed validation"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-invalid-fixture-only", action="store_true")
    args = parser.parse_args(argv)

    if args.validate_invalid_fixture_only:
        failed, message = validate_invalid_fixture()
        if failed:
            print(f"invalid fixture rejected as expected: {message}", file=sys.stderr)
            return 1
        print(message, file=sys.stderr)
        return 2

    rows = validate_inventory(load_json(INPUT_PATH))
    invalid_failed, invalid_message = validate_invalid_fixture()
    if not invalid_failed:
        raise InventoryValidationError(invalid_message)

    metrics = build_metrics(rows, invalid_failed)
    OUTPUT_PATH.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": relative_path(OUTPUT_PATH), "invalid_fixture": invalid_message}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except InventoryValidationError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
