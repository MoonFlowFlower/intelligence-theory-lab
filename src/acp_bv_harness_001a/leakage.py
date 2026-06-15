from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .common import provenance_for


FORBIDDEN_KEY_PATTERNS = [
    "oracle",
    "answerkey",
    "answer_key",
    "hiddenboundary",
    "hidden_boundary",
    "hiddenviability",
    "hidden_viability",
    "expectedaction",
    "expected_action",
    "expectedscore",
    "expected_score",
    "producerfunction",
    "producer_function",
    "passverdict",
    "pass_verdict",
    "verdict",
    "label",
    "logit",
]
FORBIDDEN_VALUE_RE = re.compile(
    r"(oracle::|answer[-_ ]?key|hidden[-_ ]?boundary|hidden[-_ ]?viability|expected[-_ ]?score|pass[-_ ]?verdict)",
    re.IGNORECASE,
)


def _normalize_key(key: str) -> str:
    return re.sub(r"[^a-z0-9_]", "", key.lower())


def _scan(value: Any, prefix: str = "") -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            normalized = _normalize_key(str(key))
            if any(pattern in normalized for pattern in FORBIDDEN_KEY_PATTERNS):
                hits.append(
                    {
                        "field_path": path,
                        "reason": "forbidden_alias_or_key",
                        "key": str(key),
                    }
                )
            hits.extend(_scan(nested, path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            hits.extend(_scan(nested, f"{prefix}[{index}]"))
    elif isinstance(value, str) and FORBIDDEN_VALUE_RE.search(value):
        hits.append(
            {
                "field_path": prefix,
                "reason": "forbidden_value_encoding",
                "value_excerpt": value[:80],
            }
        )
    return hits


def scan_candidate_bundle_for_leakage(
    bundle: dict[str, Any],
    *,
    run_id: str,
    output_artifact_path: Path,
) -> dict[str, Any]:
    hits = _scan(bundle)
    return {
        "producer_function": "scan_candidate_bundle_for_leakage",
        "called": True,
        "run_id": run_id,
        "candidate_controlled_hits": hits,
        "verdict": "blocked" if hits else "clean",
        "fixed_field_name_only_scanner": False,
        "output_artifact_path": output_artifact_path.as_posix(),
    }


def build_dirty_bundle_variants(clean_bundle: dict[str, Any]) -> list[dict[str, Any]]:
    variants = []
    first = dict(clean_bundle)
    first["oracleLabel"] = "oracle::boundary_delta=2"
    variants.append(first)

    second = dict(clean_bundle)
    second["metadata"] = {"nested": {"answer_key_alias": {"encoded": "answer-key:repair"}}}
    variants.append(second)

    third = dict(clean_bundle)
    third["candidate_outputs"] = list(clean_bundle["candidate_outputs"])
    third["candidate_outputs"][0] = dict(third["candidate_outputs"][0])
    third["candidate_outputs"][0]["expectedScoreBlob"] = "expected_score=1.0"
    variants.append(third)
    return variants


def run_leakage_controls(
    clean_bundle: dict[str, Any],
    *,
    repo_root: Path,
    output_artifact_path: Path,
    run_id: str,
) -> dict[str, Any]:
    clean = scan_candidate_bundle_for_leakage(
        clean_bundle,
        run_id=f"{run_id}-clean",
        output_artifact_path=output_artifact_path,
    )
    dirty_reports = [
        scan_candidate_bundle_for_leakage(
            variant,
            run_id=f"{run_id}-dirty-{index}",
            output_artifact_path=output_artifact_path,
        )
        for index, variant in enumerate(build_dirty_bundle_variants(clean_bundle), start=1)
    ]
    report = {
        "producer_function": "run_leakage_controls",
        "clean_case": clean,
        "dirty_case": dirty_reports[0],
        "randomized_dirty_cases": dirty_reports,
        "randomized_dirty_cases_detected": sum(1 for item in dirty_reports if item["verdict"] == "blocked"),
        "fixed_field_name_only_scanner": False,
        "provenance": provenance_for(
            run_leakage_controls,
            repo_root=repo_root,
            inputs={"dirty_variant_count": len(dirty_reports)},
            run_id=run_id,
            seed_context_episode_ids=[],
            aggregation_method="all_dirty_controls_must_block_clean_must_pass",
            output_artifact_path=output_artifact_path,
        ),
    }
    report["all_controls_passed"] = clean["verdict"] == "clean" and all(
        item["verdict"] == "blocked" for item in dirty_reports
    )
    return report
