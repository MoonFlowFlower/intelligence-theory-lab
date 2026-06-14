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
INPUT_PATH = ARTIFACT_DIR / "repo_document_inventory.json"
INVALID_FIXTURE_PATH = ARTIFACT_DIR / "malformed_positive_control_fixture.json"
OUTPUT_PATH = ARTIFACT_DIR / "document_inventory_metrics.json"

KIND_VALUES = {
    "task_card",
    "execution_report",
    "audit_report",
    "negative_evidence",
    "routing_record",
    "process_policy",
    "policy_enforcement",
    "theory_landscape",
    "artifact_dir",
    "root_navigation",
    "unknown",
}

EVIDENCE_CATEGORY_VALUES = {
    "new_mechanism_signal",
    "negative_signal",
    "governance_only",
    "hygiene_only",
    "theater_risk",
    "navigation_only",
    "unknown_requires_manual_review",
}

CANONICAL_STATUS_VALUES = {
    "canonical_current",
    "canonical_boundary",
    "superseded",
    "historical",
    "closed_negative_evidence",
    "draft_only",
    "unknown",
}

DOWNSTREAM_USE_VALUES = {
    "source_boundary",
    "negative_evidence_only",
    "policy_reference",
    "navigation_reference",
    "historical_context",
    "do_not_cite_without_review",
}

REQUIRED_FIELDS = {
    "path",
    "kind",
    "title_or_task_id",
    "verdict_or_status",
    "layer",
    "mainline_integration_status",
    "enabled_status",
    "evidence_category",
    "canonical_status",
    "downstream_use",
    "remote_anchor_or_commit_if_known",
    "source_excerpt_or_summary",
    "claim_ceiling",
    "move_or_delete_recommendation",
    "needs_followup_review",
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


def resolve_repo_path(raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return REPO_ROOT / candidate


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

        path_value = row.get("path")
        if not isinstance(path_value, str) or not path_value.strip():
            errors.append(f"row {index}: path must be a non-empty string")
        else:
            resolved = resolve_repo_path(path_value)
            if not resolved.exists():
                errors.append(f"row {index}: path does not exist: {path_value}")

        if row.get("kind") not in KIND_VALUES:
            errors.append(f"row {index}: invalid kind {row.get('kind')!r}")

        if row.get("evidence_category") not in EVIDENCE_CATEGORY_VALUES:
            errors.append(
                f"row {index}: invalid evidence_category {row.get('evidence_category')!r}"
            )

        if row.get("canonical_status") not in CANONICAL_STATUS_VALUES:
            errors.append(
                f"row {index}: invalid canonical_status {row.get('canonical_status')!r}"
            )

        if row.get("downstream_use") not in DOWNSTREAM_USE_VALUES:
            errors.append(f"row {index}: invalid downstream_use {row.get('downstream_use')!r}")

        if row.get("move_or_delete_recommendation") != "do_not_move_or_delete_in_001a":
            errors.append(
                f"row {index}: move_or_delete_recommendation must be "
                "do_not_move_or_delete_in_001a"
            )

        if not isinstance(row.get("needs_followup_review"), bool):
            errors.append(f"row {index}: needs_followup_review must be boolean")

        for field in (
            "title_or_task_id",
            "verdict_or_status",
            "layer",
            "mainline_integration_status",
            "enabled_status",
            "source_excerpt_or_summary",
            "claim_ceiling",
        ):
            if not isinstance(row.get(field), str) or not row.get(field).strip():
                errors.append(f"row {index}: {field} must be a non-empty string")

        remote_anchor = row.get("remote_anchor_or_commit_if_known")
        if remote_anchor is not None and not isinstance(remote_anchor, str):
            errors.append(f"row {index}: remote_anchor_or_commit_if_known must be string or null")

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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_path_hash() -> str:
    return sha256(Path(__file__))


def validate_invalid_fixture() -> tuple[bool, str]:
    try:
        validate_inventory(load_json(INVALID_FIXTURE_PATH))
    except InventoryValidationError as exc:
        return True, str(exc)
    return False, "malformed positive-control fixture unexpectedly passed validation"


def build_metrics(rows: list[dict[str, Any]], invalid_fixture_failed: bool) -> dict[str, Any]:
    generated_at = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
    return {
        "producer_function": "compute_document_inventory_metrics",
        "script_path": relative_path(Path(__file__)),
        "inputs": [
            {
                "path": relative_path(INPUT_PATH),
                "sha256": sha256(INPUT_PATH),
            },
            {
                "path": relative_path(INVALID_FIXTURE_PATH),
                "sha256": sha256(INVALID_FIXTURE_PATH),
            },
        ],
        "run_id": (
            "repo_governance_document_architecture_inventory_001a_"
            f"{generated_at.replace(':', '').replace('-', '')}_{uuid.uuid4().hex[:12]}"
        ),
        "current_head": current_git_head(),
        "code_path_hash": code_path_hash(),
        "generated_at_utc": generated_at,
        "kind_counts": dict(sorted(Counter(row["kind"] for row in rows).items())),
        "evidence_category_counts": dict(
            sorted(Counter(row["evidence_category"] for row in rows).items())
        ),
        "canonical_status_counts": dict(
            sorted(Counter(row["canonical_status"] for row in rows).items())
        ),
        "downstream_use_counts": dict(
            sorted(Counter(row["downstream_use"] for row in rows).items())
        ),
        "needs_followup_review_count": sum(1 for row in rows if row["needs_followup_review"]),
        "invalid_fixture_failed_as_expected": invalid_fixture_failed,
        "final_verdict": "pass" if invalid_fixture_failed else "blocked",
    }


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
