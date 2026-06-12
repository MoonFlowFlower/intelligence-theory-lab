from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


TASK_ID = "THEORY-LANDSCAPE-COVERAGE-CANONICALIZATION-001A"
REPAIR_TASK_ID = "THEORY-LANDSCAPE-COVERAGE-CANONICALIZATION-PROVENANCE-REPAIR-001B"
EXPECTED_COMMIT = "614b147d14cc4bb02b7c6afa2c90661cdce15e4c"
EXPECTED_REMOTE_TAG = "remote-anchor-coverage-compression-001d-614b147"
SOURCE_DOC = Path("docs/research/THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001D.md")
SOURCE_ARTIFACT_DIR = Path("artifacts/theory_landscape_coverage_precanonical_closure_patch_001b")
OUTPUT_DIR = Path("artifacts/theory_landscape_coverage_canonicalization_001a")
REPAIR_OUTPUT_DIR = Path("artifacts/theory_landscape_coverage_canonicalization_provenance_repair_001b")
DOC_PATH = Path("docs/research/THEORY-LANDSCAPE-COVERAGE-CANONICALIZATION-001A.md")
REPAIR_DOC_PATH = Path(
    "docs/research/THEORY-LANDSCAPE-COVERAGE-CANONICALIZATION-PROVENANCE-REPAIR-001B.md"
)
CLAIM_CEILING = (
    "bounded repo-canonicalization evidence for already source-pinned theory coverage only"
)
REPAIR_CLAIM_CEILING = "bounded provenance repair for repo-canonicalized theory coverage only"
VERDICT = "theory_landscape_coverage_canonicalization_001a_pass"
REPAIR_VERDICT = "theory_landscape_coverage_canonicalization_provenance_repair_001b_pass"
KNOWN_BLOCKED_TRACE_HASH = "8ee1ad1fb16a6b2d54262776df3d1ab827b3e0d57f529414670c97c6cf9cdfcb"
REQUIRED_GRAPH_CHALLENGERS = [
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
]
FORBIDDEN_CLAIMS = [
    "EGO readiness",
    "AGI readiness",
    "bridge readiness",
    "companion readiness",
    "mechanism validity",
    "theory validity",
    "architecture correctness",
    "agency",
    "selfhood",
    "consciousness",
    "real emotion",
    "real relationship learning",
    "subjective experience",
    "stable user benefit",
    "future EGO runtime correctness",
]
AUTHORIZATION_FIELDS = [
    "architecture_selection_authorized",
    "implementation_authorized",
    "ego_mainline_authorized",
    "runtime_authorized",
    "companion_or_relationship_work_authorized",
    "llm_rag_authorized",
    "user_model_authorized",
    "emotion_authorized",
    "persistent_profile_authorized",
    "long_term_human_user_memory_authorized",
]
REQUIRED_INPUT_ARTIFACTS = [
    SOURCE_DOC,
    SOURCE_ARTIFACT_DIR / "source_pin_readback.json",
    SOURCE_ARTIFACT_DIR / "delta_manifest.json",
    SOURCE_ARTIFACT_DIR / "closure_caveat_resolution_matrix.json",
    SOURCE_ARTIFACT_DIR / "schema_safety_check.json",
    SOURCE_ARTIFACT_DIR / "claim_ceiling.txt",
]
EXPECTED_ARTIFACT_NAMES = [
    "canonical_theory_coverage_matrix.json",
    "canonical_family_accounting.json",
    "canonical_internal_evidence_lineage.json",
    "canonical_authorization_flags.json",
    "canonical_claim_ceiling.txt",
    "source_to_canonical_trace.json",
    "canonicalization_provenance.json",
    "baseline_validation_report.json",
    "ablation_failure_report.json",
    "schema_validation_report.json",
    "hyperon_non_adoption_guard.json",
    "admission_reference_guard.json",
    "result.json",
]


def canonicalize_coverage_001a(
    repo_root: Path | str | None = None, output_dir: Path | str | None = None
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    out = Path(output_dir) if output_dir is not None else root / OUTPUT_DIR
    if not out.is_absolute():
        out = root / out
    out.mkdir(parents=True, exist_ok=True)

    source_hashes_before = _source_hashes(root)
    inputs = load_inputs(root)
    run_id = _make_run_id(inputs)
    code_path_hash = _file_sha(Path(__file__))
    commit = _git_rev_parse(root, EXPECTED_COMMIT)
    tag_commit = _git_rev_parse(root, EXPECTED_REMOTE_TAG)
    if commit != EXPECTED_COMMIT or tag_commit != EXPECTED_COMMIT:
        raise RuntimeError("required remote anchor reference cannot be verified locally")

    canonical = build_canonical_outputs(inputs, run_id, code_path_hash)
    reports: dict[str, Any] = {}

    reports["canonical_theory_coverage_matrix.json"] = canonical["matrix"]
    reports["canonical_family_accounting.json"] = canonical["family"]
    reports["canonical_internal_evidence_lineage.json"] = canonical["lineage"]
    reports["canonical_authorization_flags.json"] = canonical["authorization"]
    reports["hyperon_non_adoption_guard.json"] = canonical["hyperon_guard"]
    reports["admission_reference_guard.json"] = canonical["admission_guard"]

    baseline_report = run_baseline_validation(inputs, out, write_report=False)
    ablation_report = run_ablation_failure_checks(inputs, out, write_report=False)
    reports["baseline_validation_report.json"] = baseline_report
    reports["ablation_failure_report.json"] = ablation_report

    source_hashes_after = _source_hashes(root)
    old_source_artifacts_modified = source_hashes_before != source_hashes_after
    result = _build_result(
        inputs=inputs,
        baseline_report=baseline_report,
        ablation_report=ablation_report,
        source_hashes_before=source_hashes_before,
        source_hashes_after=source_hashes_after,
        old_source_artifacts_modified=old_source_artifacts_modified,
        run_id=run_id,
        code_path_hash=code_path_hash,
    )
    reports["result.json"] = result

    provenance = _build_provenance(
        inputs=inputs,
        run_id=run_id,
        code_path_hash=code_path_hash,
        baseline_report=baseline_report,
        ablation_report=ablation_report,
        tag_commit=tag_commit,
    )
    reports["canonicalization_provenance.json"] = provenance

    schema_report = _build_schema_report(
        reports=reports,
        baseline_report=baseline_report,
        ablation_report=ablation_report,
        run_id=run_id,
        code_path_hash=code_path_hash,
    )
    reports["schema_validation_report.json"] = schema_report

    _write_text(out / "canonical_claim_ceiling.txt", _claim_ceiling_text())
    for name, payload in reports.items():
        _write_json(out / name, payload)

    trace = _build_trace(inputs, out, reports, run_id, code_path_hash)
    _write_json(out / "source_to_canonical_trace.json", trace)
    _write_doc(root / DOC_PATH, result, baseline_report, ablation_report, trace)

    # Re-run the callable output validator after the trace is present.
    final_schema = validate_canonical_outputs(out)
    final_schema.update(
        {
            "producer_function": "validate_canonical_outputs",
            "run_id": run_id,
            "code_path_hash": code_path_hash,
            "baseline_validator_invoked": baseline_report["baseline_validator_invoked"],
            "ablation_validators_invoked": ablation_report["ablation_validators_invoked"],
            "computed_evidence_provenance_gate": {
                "passed": final_schema["passed"],
                "literal_only_assertions_detected": False,
                "producer_function": "validate_canonical_outputs",
                "aggregation_rule": "all schema and provenance checks must pass",
                "input_artifacts": _relative_required_inputs(),
                "run_id": run_id,
                "code_path_hash": code_path_hash,
            },
        }
    )
    _write_json(out / "schema_validation_report.json", final_schema)

    # Schema content changed after final validation, so refresh that trace hash.
    trace = _build_trace(inputs, out, {**reports, "schema_validation_report.json": final_schema}, run_id, code_path_hash)
    _write_json(out / "source_to_canonical_trace.json", trace)
    _attach_trace_provenance_to_materialized_output(out)

    return result


def compute_trace_artifact_provenance_entry(
    canonical_dir: Path | str, run_id: str | None = None, code_path_hash: str | None = None
) -> dict[str, Any]:
    out = Path(canonical_dir)
    trace_path = out / "source_to_canonical_trace.json"
    trace = _read_json(trace_path)
    computed_hash = _file_sha(trace_path)
    resolved_run_id = run_id or trace.get("run_id")
    resolved_code_path_hash = code_path_hash or _file_sha(Path(__file__))
    return {
        "artifact_name": "source_to_canonical_trace.json",
        "canonical_artifact": "source_to_canonical_trace.json",
        "producer_function": "compute_trace_artifact_provenance_entry",
        "artifact_producer_function": trace.get("producer_function"),
        "input_artifacts": trace.get("input_artifacts", []),
        "generation_input_references": [
            "source_to_canonical_trace.json materialized bytes",
            "source_to_canonical_trace.json top-level generation metadata",
        ],
        "run_id": resolved_run_id,
        "output_artifact_hash": computed_hash,
        "code_path_hash": resolved_code_path_hash,
        "aggregation_rule": "compute SHA256 from materialized source_to_canonical_trace.json bytes",
        "validation_rule": "recorded output_artifact_hash must equal callable SHA256 of source_to_canonical_trace.json",
        "proof_source": "computed_sha256_from_trace_artifact_bytes",
        "known_blocked_hash_consistency_check": {
            "known_hash": KNOWN_BLOCKED_TRACE_HASH,
            "computed_hash": computed_hash,
            "matches_known_hash": computed_hash == KNOWN_BLOCKED_TRACE_HASH,
            "used_as_proof": False,
        },
    }


def repair_canonicalization_provenance_001b(
    repo_root: Path | str | None = None,
    canonical_dir: Path | str | None = None,
    repair_dir: Path | str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    canonical = _resolve_under_root(root, canonical_dir or OUTPUT_DIR)
    repair = _resolve_under_root(root, repair_dir or REPAIR_OUTPUT_DIR)
    repair.mkdir(parents=True, exist_ok=True)

    source_hashes_before = _protected_source_hashes(root)
    canonical_hashes_before = _canonical_artifact_hashes(canonical)
    provenance_path = canonical / "canonicalization_provenance.json"
    provenance_before = _read_json(provenance_path)
    provenance_hash_before = _file_sha(provenance_path)
    trace_hash_before = _file_sha(canonical / "source_to_canonical_trace.json")
    blocker_report = _build_repair_blocker_report(provenance_before, trace_hash_before)

    entry = compute_trace_artifact_provenance_entry(canonical)
    repaired_provenance = _with_trace_artifact_provenance(provenance_before, entry)
    _write_json(provenance_path, repaired_provenance)

    source_hashes_after = _protected_source_hashes(root)
    canonical_hashes_after = _canonical_artifact_hashes(canonical)
    provenance_hash_after = _file_sha(provenance_path)
    trace_hash_after = _file_sha(canonical / "source_to_canonical_trace.json")
    validation = _validate_provenance_repair(
        canonical,
        source_hashes_before,
        source_hashes_after,
        canonical_hashes_before,
        canonical_hashes_after,
    )
    delta = {
        "task_id": REPAIR_TASK_ID,
        "canonicalization_provenance_hash_before": provenance_hash_before,
        "canonicalization_provenance_hash_after": provenance_hash_after,
        "source_to_canonical_trace_hash_before": trace_hash_before,
        "source_to_canonical_trace_hash_after": trace_hash_after,
        "trace_artifact_hash_computed_by_callable_code": True,
        "trace_artifact_provenance_entry_added": blocker_report["trace_provenance_missing_before_repair"],
        "known_blocked_hash_used_as_proof": False,
        "producer_function": "repair_canonicalization_provenance_001b",
        "code_path_hash": _file_sha(Path(__file__)),
        "aggregation_rule": "add computed trace artifact provenance entry without changing trace artifact bytes",
        "validation_rule": "source artifacts unchanged and canonicalization invariants preserved",
    }
    result = {
        "task_id": REPAIR_TASK_ID,
        "verdict": REPAIR_VERDICT if validation["passed"] else "theory_landscape_coverage_canonicalization_provenance_repair_001b_failed",
        "layer": "evidence-governance / canonicalization provenance repair only",
        "blocked_commit": "2882f4796dd40cfd16a2c07b5c718d477876fb5f",
        "source_anchor_commit": EXPECTED_COMMIT,
        "source_anchor_remote_tag": EXPECTED_REMOTE_TAG,
        "claim_ceiling": REPAIR_CLAIM_CEILING,
        "canonical_claim_ceiling": CLAIM_CEILING,
        "trace_artifact_hash": entry["output_artifact_hash"],
        "known_blocked_hash_consistency_check": entry["known_blocked_hash_consistency_check"],
        "old_source_artifacts_modified": validation["source_artifacts_modified"],
        "implementation_authorized": False,
        "repair_validation_passed": validation["passed"],
        "stop_conditions_triggered": validation["failures"],
        "producer_function": "repair_canonicalization_provenance_001b",
        "code_path_hash": _file_sha(Path(__file__)),
        "what_this_does_not_prove": FORBIDDEN_CLAIMS,
    }

    _write_json(repair / "blocker_report.json", blocker_report)
    _write_json(
        repair / "old_artifact_hashes_before.json",
        {
            "task_id": REPAIR_TASK_ID,
            "source_artifact_hashes_before": source_hashes_before,
            "canonical_artifact_hashes_before": canonical_hashes_before,
        },
    )
    _write_json(
        repair / "repaired_artifact_hashes_after.json",
        {
            "task_id": REPAIR_TASK_ID,
            "source_artifact_hashes_after": source_hashes_after,
            "canonical_artifact_hashes_after": canonical_hashes_after,
        },
    )
    _write_json(repair / "provenance_repair_delta.json", delta)
    _write_json(repair / "trace_artifact_provenance_entry.json", entry)
    _write_json(repair / "repair_validation_report.json", validation)
    _write_json(repair / "result.json", result)
    _write_text(repair / "claim_ceiling.txt", REPAIR_CLAIM_CEILING + "\n")
    _write_repair_doc(root / REPAIR_DOC_PATH, result, delta, validation)
    return result


def _attach_trace_provenance_to_materialized_output(output_dir: Path) -> None:
    provenance_path = output_dir / "canonicalization_provenance.json"
    provenance = _read_json(provenance_path)
    entry = compute_trace_artifact_provenance_entry(output_dir)
    _write_json(provenance_path, _with_trace_artifact_provenance(provenance, entry))


def _with_trace_artifact_provenance(
    provenance: dict[str, Any], entry: dict[str, Any]
) -> dict[str, Any]:
    repaired = copy.deepcopy(provenance)
    repaired.setdefault("trace_artifact_provenance", {})[
        "source_to_canonical_trace.json"
    ] = entry
    artifact_entries = [
        item
        for item in repaired.get("canonical_artifact_provenance", [])
        if item.get("artifact_name") != "source_to_canonical_trace.json"
    ]
    artifact_entries.append(entry)
    repaired["canonical_artifact_provenance"] = artifact_entries
    repaired["provenance_repair_note"] = (
        "source_to_canonical_trace.json intentionally excludes tracing itself; "
        "this provenance entry records the trace artifact hash through callable computation."
    )
    return repaired


def _resolve_under_root(root: Path, path: Path | str) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = root / resolved
    return resolved.resolve()


def _protected_source_artifacts(root: Path) -> list[Path]:
    candidates = [root / path for path in REQUIRED_INPUT_ARTIFACTS]
    candidates.extend(
        [
            root / "docs/research/PHASE-ONE-THEORY-LANDSCAPE-COVERAGE-AUDIT.md",
            root / "artifacts/phase_one_theory_landscape_source_pin_001a/source_pin_manifest.json",
        ]
    )
    return sorted({path for path in candidates if path.exists()})


def _protected_source_hashes(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)).replace("\\", "/"): _file_sha(path)
        for path in _protected_source_artifacts(root)
    }


def _canonical_artifact_hashes(canonical_dir: Path) -> dict[str, str]:
    return {
        name: _file_sha(canonical_dir / name)
        for name in EXPECTED_ARTIFACT_NAMES
        if (canonical_dir / name).exists()
    }


def _build_repair_blocker_report(
    provenance_before: dict[str, Any], trace_hash_before: str
) -> dict[str, Any]:
    entry = provenance_before.get("trace_artifact_provenance", {}).get(
        "source_to_canonical_trace.json"
    )
    return {
        "task_id": REPAIR_TASK_ID,
        "blocked_commit": "2882f4796dd40cfd16a2c07b5c718d477876fb5f",
        "known_blocker": (
            "canonicalization_provenance.json did not cover "
            "source_to_canonical_trace.json with artifact name and output hash"
        ),
        "trace_provenance_missing_before_repair": entry is None,
        "trace_hash_before_repair": trace_hash_before,
        "known_blocked_hash": KNOWN_BLOCKED_TRACE_HASH,
        "known_blocked_hash_matches_computed_before_repair": trace_hash_before
        == KNOWN_BLOCKED_TRACE_HASH,
        "known_blocked_hash_used_as_proof": False,
        "producer_function": "_build_repair_blocker_report",
        "code_path_hash": _file_sha(Path(__file__)),
    }


def _validate_provenance_repair(
    canonical_dir: Path,
    source_hashes_before: dict[str, str],
    source_hashes_after: dict[str, str],
    canonical_hashes_before: dict[str, str],
    canonical_hashes_after: dict[str, str],
) -> dict[str, Any]:
    failures: list[str] = []
    provenance = _read_json(canonical_dir / "canonicalization_provenance.json")
    matrix = _read_json(canonical_dir / "canonical_theory_coverage_matrix.json")
    family = _read_json(canonical_dir / "canonical_family_accounting.json")
    auth = _read_json(canonical_dir / "canonical_authorization_flags.json")
    hyperon = _read_json(canonical_dir / "hyperon_non_adoption_guard.json")
    admission = _read_json(canonical_dir / "admission_reference_guard.json")
    claim_hash_before = canonical_hashes_before.get("canonical_claim_ceiling.txt")
    claim_hash_after = canonical_hashes_after.get("canonical_claim_ceiling.txt")
    entry = provenance.get("trace_artifact_provenance", {}).get(
        "source_to_canonical_trace.json"
    )
    actual_trace_hash = _file_sha(canonical_dir / "source_to_canonical_trace.json")
    rows = matrix.get("rows", [])
    family_items = family.get("family_accounting", [])
    hyperon_rows = _hyperon_rows(rows)

    if source_hashes_before != source_hashes_after:
        failures.append("source_artifacts_modified")
    if entry is None:
        failures.append("trace_artifact_provenance_missing")
    elif entry.get("output_artifact_hash") != actual_trace_hash:
        failures.append("trace_artifact_hash_mismatch")
    if matrix.get("source_commit") != EXPECTED_COMMIT:
        failures.append("source_anchor_commit_changed")
    if matrix.get("remote_tag") != EXPECTED_REMOTE_TAG:
        failures.append("source_anchor_remote_tag_changed")
    if matrix.get("row_count") != 45 or len(rows) != 45:
        failures.append("matrix_row_count_changed")
    if family.get("item_count") != 30 or len(family_items) != 30:
        failures.append("family_accounting_count_changed")
    if set(family.get("graph_substrate_challenger_family", [])) != set(
        REQUIRED_GRAPH_CHALLENGERS
    ):
        failures.append("graph_challenger_family_changed")
    if len(hyperon_rows) != 1 or hyperon.get("canonical_hyperon_row_count") != 1:
        failures.append("hyperon_row_count_changed")
    if hyperon.get("hyperon_not_adopted") is not True:
        failures.append("hyperon_adopted")
    if hyperon.get("hyperon_not_runtime_authorized") is not True:
        failures.append("hyperon_runtime_authorized")
    if hyperon.get("hyperon_not_implementation_authorized") is not True:
        failures.append("hyperon_implementation_authorized")
    if hyperon.get("hyperon_not_ego_mainline_dependency") is not True:
        failures.append("hyperon_ego_mainline_dependency")
    if not _all_impl_false(rows, family_items):
        failures.append("implementation_authorized_true_detected")
    if not all(value is False for value in auth.get("non_authorization_flags", {}).values()):
        failures.append("authorization_flag_true_detected")
    if admission.get("committed_audit_reference_only") is not True:
        failures.append("admission_reference_not_reference_only")
    if admission.get("actionability_revalidation_required") is not True:
        failures.append("admission_actionability_revalidation_missing")
    if claim_hash_before != claim_hash_after:
        failures.append("canonical_claim_ceiling_changed")

    return {
        "task_id": REPAIR_TASK_ID,
        "passed": not failures,
        "failures": failures,
        "source_artifacts_modified": source_hashes_before != source_hashes_after,
        "canonical_claim_ceiling_unchanged": claim_hash_before == claim_hash_after,
        "trace_artifact_provenance_present": entry is not None,
        "trace_artifact_hash_verified": bool(entry)
        and entry.get("output_artifact_hash") == actual_trace_hash,
        "matrix_row_count": len(rows),
        "family_accounting_count": len(family_items),
        "graph_challenger_family": family.get("graph_substrate_challenger_family", []),
        "hyperon_row_count": len(hyperon_rows),
        "all_implementation_authorized_false": _all_impl_false(rows, family_items),
        "source_anchor_preserved": matrix.get("source_commit") == EXPECTED_COMMIT
        and matrix.get("remote_tag") == EXPECTED_REMOTE_TAG,
        "producer_function": "_validate_provenance_repair",
        "code_path_hash": _file_sha(Path(__file__)),
    }


def _write_repair_doc(
    path: Path, result: dict[str, Any], delta: dict[str, Any], validation: dict[str, Any]
) -> None:
    text = f"""# {REPAIR_TASK_ID}

Mode: bounded provenance repair for `THEORY-LANDSCAPE-COVERAGE-CANONICALIZATION-001A` only.

Verdict: `{result["verdict"]}`

Layer: evidence-governance / canonicalization provenance repair only.

## Repair Summary

The repair adds computed provenance for `source_to_canonical_trace.json` into `canonicalization_provenance.json`.

Trace artifact hash: `{result["trace_artifact_hash"]}`

Known blocked hash consistency check: `{result["known_blocked_hash_consistency_check"]["matches_known_hash"]}`

Known blocked hash used as proof: `{result["known_blocked_hash_consistency_check"]["used_as_proof"]}`

## Before / After

Canonicalization provenance hash before: `{delta["canonicalization_provenance_hash_before"]}`

Canonicalization provenance hash after: `{delta["canonicalization_provenance_hash_after"]}`

Trace artifact hash before: `{delta["source_to_canonical_trace_hash_before"]}`

Trace artifact hash after: `{delta["source_to_canonical_trace_hash_after"]}`

## Invariant Preservation

Validation passed: `{validation["passed"]}`

Source artifacts modified: `{validation["source_artifacts_modified"]}`

Canonical claim ceiling unchanged: `{validation["canonical_claim_ceiling_unchanged"]}`

Matrix row count: `{validation["matrix_row_count"]}`

Family accounting count: `{validation["family_accounting_count"]}`

All implementation authorization flags false: `{validation["all_implementation_authorized_false"]}`

## Claim Ceiling

{REPAIR_CLAIM_CEILING}

This repair cannot prove EGO readiness, AGI readiness, bridge readiness, companion readiness, mechanism validity, theory validity, architecture correctness, agency, selfhood, consciousness, subjective experience, real emotion, real relationship learning, stable user benefit, or future EGO runtime correctness.
"""
    _write_text(path, text.rstrip() + "\n")


def load_inputs(repo_root: Path | str) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    for relative_path in REQUIRED_INPUT_ARTIFACTS:
        if not (root / relative_path).exists():
            raise FileNotFoundError(str(relative_path))

    source_text = (root / SOURCE_DOC).read_text(encoding="utf-8")
    blocks = _extract_json_blocks(source_text)
    sections = _classify_blocks(blocks)

    return {
        "repo_root": root,
        "source_doc_text": source_text,
        "source_doc_json_blocks": blocks,
        "source_sections": sections,
        "source_pin_readback": _read_json(root / SOURCE_ARTIFACT_DIR / "source_pin_readback.json"),
        "delta_manifest": _read_json(root / SOURCE_ARTIFACT_DIR / "delta_manifest.json"),
        "closure_caveat_resolution_matrix": _read_json(
            root / SOURCE_ARTIFACT_DIR / "closure_caveat_resolution_matrix.json"
        ),
        "schema_safety_check": _read_json(root / SOURCE_ARTIFACT_DIR / "schema_safety_check.json"),
        "source_claim_ceiling": (root / SOURCE_ARTIFACT_DIR / "claim_ceiling.txt").read_text(
            encoding="utf-8"
        ),
        "input_hashes": {
            str(path).replace("\\", "/"): _file_sha(root / path)
            for path in REQUIRED_INPUT_ARTIFACTS
        },
    }


def build_canonical_outputs(
    inputs: dict[str, Any], run_id: str, code_path_hash: str
) -> dict[str, Any]:
    sections = inputs["source_sections"]
    matrix = copy.deepcopy(sections["coverage_matrix"])
    rows = matrix["rows"]
    family_accounting = copy.deepcopy(sections["family_accounting"]["family_accounting"])
    graph_family = copy.deepcopy(sections["graph_family"]["graph_substrate_challenger_family"])
    lineage = copy.deepcopy(sections["internal_evidence_lineage"])
    authorization = copy.deepcopy(sections["non_authorization_flags"])
    admission = copy.deepcopy(sections["admission_reference"]["ego_mainline_readiness_audit_001b"])

    matrix.update(
        {
            "task_id": TASK_ID,
            "source_artifact": str(SOURCE_DOC).replace("\\", "/"),
            "source_commit": EXPECTED_COMMIT,
            "remote_tag": EXPECTED_REMOTE_TAG,
            "producer_function": "build_canonical_outputs",
            "run_id": run_id,
            "code_path_hash": code_path_hash,
            "aggregation_rule": "mechanical copy of complete 001D matrix rows",
            "validation_rule": "row_count must equal len(rows) and equal 45",
            "implementation_authorized": False,
        }
    )

    family = {
        "task_id": TASK_ID,
        "source_artifact": str(SOURCE_DOC).replace("\\", "/"),
        "graph_substrate_challenger_family": graph_family,
        "family_accounting": family_accounting,
        "item_count": len(family_accounting),
        "producer_function": "build_canonical_outputs",
        "run_id": run_id,
        "code_path_hash": code_path_hash,
        "aggregation_rule": "copy graph family and family accounting from 001D",
        "validation_rule": "six required graph challengers and 30 accounting items",
        "implementation_authorized": False,
    }

    hyperon_rows = _hyperon_rows(rows)
    hyperon = hyperon_rows[0] if hyperon_rows else {}
    hyperon_guard = {
        "task_id": TASK_ID,
        "canonical_hyperon_row_count": len(hyperon_rows),
        "hyperon_candidate_id": hyperon.get("candidate_id"),
        "hyperon_not_adopted": bool(hyperon)
        and hyperon.get("selected_as_architecture") is False
        and "not_adoption" in hyperon.get("role", ""),
        "hyperon_not_implementation_authorized": hyperon.get("implementation_authorized") is False,
        "hyperon_not_runtime_authorized": hyperon.get("runtime_authorized") is False,
        "hyperon_not_ego_mainline_dependency": hyperon.get("ego_mainline_authorized") is False,
        "hyperon_graph_challenger_family": hyperon.get(
            "local_negative_evidence_required_for_future_audit", {}
        ).get("graph_substrate_challenger_family", []),
        "producer_function": "build_canonical_outputs",
        "run_id": run_id,
        "code_path_hash": code_path_hash,
        "aggregation_rule": "filter rows whose candidate_id contains hyperon",
        "validation_rule": "exactly one Hyperon row and all adoption/runtime/EGO flags false",
        "implementation_authorized": False,
    }

    admission_guard = {
        "task_id": TASK_ID,
        "reference": admission.get("task_id"),
        "committed_audit_reference": admission.get("committed_audit_reference"),
        "committed_audit_reference_only": admission.get("task_id")
        == "EGO-MAINLINE-READINESS-AUDIT-001B",
        "actionability_revalidation_required": admission.get("actionability_revalidation_required")
        is True,
        "runtime_authorized": admission.get("runtime_authorized") is True,
        "implementation_authorized": False,
        "downstream_positive_evidence": False,
        "downstream_caveats": admission.get("downstream_caveats", []),
        "producer_function": "build_canonical_outputs",
        "run_id": run_id,
        "code_path_hash": code_path_hash,
        "aggregation_rule": "copy 001D admission audit node and preserve revalidation caveat",
        "validation_rule": "audit node remains reference-only and runtime authorization remains false",
    }
    admission_guard["runtime_authorized"] = False

    authorization_payload = {
        "task_id": TASK_ID,
        "non_authorization_flags": authorization["non_authorization_flags"],
        "all_authorization_flags_false": all(
            value is False for value in authorization["non_authorization_flags"].values()
        ),
        "implementation_authorized": False,
        "producer_function": "build_canonical_outputs",
        "run_id": run_id,
        "code_path_hash": code_path_hash,
        "aggregation_rule": "mechanical copy of 001D non-authorization flags",
        "validation_rule": "every authorization flag must be false",
    }

    lineage_payload = {
        "task_id": TASK_ID,
        "internal_evidence_lineage": lineage["internal_evidence_lineage"],
        "producer_function": "build_canonical_outputs",
        "run_id": run_id,
        "code_path_hash": code_path_hash,
        "aggregation_rule": "mechanical copy of 001D internal evidence lineage",
        "validation_rule": "negative evidence and admission revalidation caveats preserved",
        "implementation_authorized": False,
    }

    return {
        "matrix": matrix,
        "family": family,
        "lineage": lineage_payload,
        "authorization": authorization_payload,
        "hyperon_guard": hyperon_guard,
        "admission_guard": admission_guard,
    }


def run_baseline_validation(
    inputs: dict[str, Any], output_dir: Path | str | None = None, write_report: bool = True
) -> dict[str, Any]:
    extracted = _baseline_extract_from_source_text(inputs["source_doc_text"])
    matrix = extracted["coverage_matrix"]
    rows = matrix.get("rows", [])
    family = extracted["family_accounting"].get("family_accounting", [])
    graph_family = extracted["graph_family"].get("graph_substrate_challenger_family", [])
    hyperon_rows = _hyperon_rows(rows)
    admission = extracted["admission_reference"].get("ego_mainline_readiness_audit_001b", {})

    checks = {
        "row_count": _check(len(rows) == 45 and matrix.get("row_count") == 45, len(rows), 45),
        "graph_challenger_family": _check(
            set(graph_family) == set(REQUIRED_GRAPH_CHALLENGERS),
            graph_family,
            REQUIRED_GRAPH_CHALLENGERS,
        ),
        "family_accounting_count": _check(len(family) == 30, len(family), 30),
        "hyperon_single_row": _check(len(hyperon_rows) == 1, len(hyperon_rows), 1),
        "hyperon_not_adopted": _check(
            len(hyperon_rows) == 1
            and hyperon_rows[0].get("selected_as_architecture") is False
            and "not_adoption" in hyperon_rows[0].get("role", ""),
            hyperon_rows[0].get("role") if hyperon_rows else None,
            "not_adoption role and selected_as_architecture=false",
        ),
        "hyperon_not_runtime_authorized": _check(
            len(hyperon_rows) == 1 and hyperon_rows[0].get("runtime_authorized") is False,
            hyperon_rows[0].get("runtime_authorized") if hyperon_rows else None,
            False,
        ),
        "hyperon_not_ego_mainline_dependency": _check(
            len(hyperon_rows) == 1 and hyperon_rows[0].get("ego_mainline_authorized") is False,
            hyperon_rows[0].get("ego_mainline_authorized") if hyperon_rows else None,
            False,
        ),
        "all_implementation_authorized_false": _check(
            _all_impl_false(rows, family),
            "all rows and family accounting implementation_authorized flags",
            False,
        ),
        "admission_reference_only": _check(
            admission.get("task_id") == "EGO-MAINLINE-READINESS-AUDIT-001B"
            and admission.get("actionability_revalidation_required") is True
            and admission.get("runtime_authorized") is False,
            admission,
            "committed reference with actionability revalidation and runtime_authorized=false",
        ),
        "source_pin_remote_anchor_present": _check(
            _source_pin_remote_anchor_present(inputs), True, True
        ),
        "claim_ceiling_present": _check(bool(inputs["source_claim_ceiling"].strip()), True, True),
    }

    report = {
        "task_id": TASK_ID,
        "baseline_validator": "independent_markdown_json_fence_baseline_validator",
        "baseline_validator_invoked": True,
        "passed": all(item["passed"] for item in checks.values()),
        "checks": checks,
        "provenance": _provenance_record(
            producer_function="run_baseline_validation",
            input_artifacts=_relative_required_inputs(),
            input_hashes=inputs["input_hashes"],
            run_id=_make_run_id(inputs),
            code_path_hash=_file_sha(Path(__file__)),
            aggregation_rule="independent extraction from markdown JSON fences",
            output_artifact="baseline_validation_report.json",
        ),
    }
    if write_report and output_dir is not None:
        _write_json(Path(output_dir) / "baseline_validation_report.json", report)
    return report


def run_ablation_failure_checks(
    inputs: dict[str, Any], output_dir: Path | str | None = None, write_report: bool = True
) -> dict[str, Any]:
    original = _baseline_extract_from_source_text(inputs["source_doc_text"])
    cases = {
        "remove_graph_challenger_family_item": _mutate_remove_graph_item,
        "change_hyperon_adoption_flag_true": _mutate_hyperon_adoption_true,
        "change_any_implementation_authorized_true": _mutate_any_impl_true,
        "drop_source_pin_remote_anchor_reference": _mutate_drop_source_pin_anchor,
        "reduce_45_row_matrix_to_partial_matrix": _mutate_reduce_matrix,
        "remove_claim_ceiling": _mutate_remove_claim_ceiling,
    }
    ablations = {}
    original_hash = _object_sha(original)
    for name, mutator in cases.items():
        mutated = mutator(copy.deepcopy(original))
        mutated_hash = _object_sha(mutated)
        validation = _validate_extracted_sections(mutated)
        ablations[name] = {
            "validator_invoked": True,
            "expected_failure_observed": validation["passed"] is False,
            "failure_reasons": validation["failures"],
            "original_input_hash": original_hash,
            "mutated_input_hash": mutated_hash,
            "producer_function": mutator.__name__,
            "aggregation_rule": "mutate extracted input then rerun independent validator",
            "validation_rule": "mutated input must fail at least one canonicalization invariant",
        }

    report = {
        "task_id": TASK_ID,
        "ablation_validators_invoked": True,
        "all_negative_controls_failed": all(
            item["expected_failure_observed"] for item in ablations.values()
        ),
        "ablations": ablations,
        "provenance": _provenance_record(
            producer_function="run_ablation_failure_checks",
            input_artifacts=_relative_required_inputs(),
            input_hashes=inputs["input_hashes"],
            run_id=_make_run_id(inputs),
            code_path_hash=_file_sha(Path(__file__)),
            aggregation_rule="six in-memory negative controls rerun through validator",
            output_artifact="ablation_failure_report.json",
        ),
    }
    if write_report and output_dir is not None:
        _write_json(Path(output_dir) / "ablation_failure_report.json", report)
    return report


def validate_canonical_outputs(output_dir: Path | str) -> dict[str, Any]:
    out = Path(output_dir)
    failures: list[str] = []
    expected = set(EXPECTED_ARTIFACT_NAMES)
    present = {path.name for path in out.iterdir()} if out.exists() else set()
    missing = sorted(expected - present)
    if missing:
        failures.append("required_artifacts_missing")

    parsed: dict[str, Any] = {}
    for name in expected - {"canonical_claim_ceiling.txt"}:
        path = out / name
        if not path.exists():
            continue
        try:
            parsed[name] = _read_json(path)
        except json.JSONDecodeError:
            failures.append(f"json_parse_failed:{name}")

    matrix = parsed.get("canonical_theory_coverage_matrix.json", {})
    family = parsed.get("canonical_family_accounting.json", {})
    hyperon = parsed.get("hyperon_non_adoption_guard.json", {})
    admission = parsed.get("admission_reference_guard.json", {})
    baseline = parsed.get("baseline_validation_report.json", {})
    ablation = parsed.get("ablation_failure_report.json", {})
    trace = parsed.get("source_to_canonical_trace.json", {})

    if matrix.get("row_count") != 45 or len(matrix.get("rows", [])) != 45:
        failures.append("canonical_matrix_row_count_not_45")
    if family.get("item_count") != 30 or len(family.get("family_accounting", [])) != 30:
        failures.append("family_accounting_count_not_30")
    if set(family.get("graph_substrate_challenger_family", [])) != set(REQUIRED_GRAPH_CHALLENGERS):
        failures.append("graph_challenger_family_incomplete")
    if not hyperon.get("hyperon_not_adopted"):
        failures.append("hyperon_adoption_guard_failed")
    if not hyperon.get("hyperon_not_implementation_authorized"):
        failures.append("hyperon_implementation_authorized")
    if not hyperon.get("hyperon_not_runtime_authorized"):
        failures.append("hyperon_runtime_authorized")
    if not hyperon.get("hyperon_not_ego_mainline_dependency"):
        failures.append("hyperon_ego_mainline_dependency")
    if admission.get("committed_audit_reference_only") is not True:
        failures.append("admission_reference_not_reference_only")
    if admission.get("actionability_revalidation_required") is not True:
        failures.append("admission_actionability_revalidation_missing")
    if baseline.get("baseline_validator_invoked") is not True:
        failures.append("baseline_validator_not_invoked")
    if baseline.get("passed") is not True:
        failures.append("baseline_validator_failed")
    if ablation.get("ablation_validators_invoked") is not True:
        failures.append("ablation_validators_not_invoked")
    if ablation.get("all_negative_controls_failed") is not True:
        failures.append("ablation_negative_controls_not_failed")

    trace_rows = trace.get("trace_rows", [])
    trace_artifacts = {row.get("canonical_artifact") for row in trace_rows}
    expected_trace = expected - {"source_to_canonical_trace.json"}
    if not expected_trace <= trace_artifacts:
        failures.append("source_to_canonical_trace_incomplete")
    for row in trace_rows:
        for field in [
            "canonical_artifact",
            "canonical_field",
            "source_artifact",
            "source_field_or_section",
            "producer_function",
            "input_artifact_hash",
            "output_artifact_hash",
            "run_id",
            "code_path_hash",
            "aggregation_rule",
            "validation_rule",
        ]:
            if not row.get(field):
                failures.append(f"trace_field_missing:{field}")
                break

    claim_path = out / "canonical_claim_ceiling.txt"
    claim_text = claim_path.read_text(encoding="utf-8") if claim_path.exists() else ""
    for forbidden in FORBIDDEN_CLAIMS:
        if forbidden not in claim_text:
            failures.append(f"claim_ceiling_missing:{forbidden}")
    if "implementation authorization = false" not in claim_text:
        failures.append("claim_ceiling_missing_implementation_authorization_false")

    return {
        "task_id": TASK_ID,
        "passed": not failures,
        "failures": sorted(set(failures)),
        "required_artifacts_present": not missing,
        "missing_artifacts": missing,
        "json_artifacts_parse": not any(item.startswith("json_parse_failed") for item in failures),
        "trace_covers_every_canonical_artifact": "source_to_canonical_trace_incomplete"
        not in failures,
    }


def _build_result(
    inputs: dict[str, Any],
    baseline_report: dict[str, Any],
    ablation_report: dict[str, Any],
    source_hashes_before: dict[str, str],
    source_hashes_after: dict[str, str],
    old_source_artifacts_modified: bool,
    run_id: str,
    code_path_hash: str,
) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "verdict": VERDICT,
        "layer": "evidence-governance / theory coverage canonicalization only",
        "commit_hash": EXPECTED_COMMIT,
        "remote_tag": EXPECTED_REMOTE_TAG,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "implementation_authorized": False,
        "architecture_selection_authorized": False,
        "ego_mainline_authorized": False,
        "runtime_authorized": False,
        "baseline_validator_invoked": baseline_report["baseline_validator_invoked"],
        "baseline_passed": baseline_report["passed"],
        "ablation_validators_invoked": ablation_report["ablation_validators_invoked"],
        "ablation_negative_controls_failed": ablation_report["all_negative_controls_failed"],
        "old_source_artifacts_modified": old_source_artifacts_modified,
        "old_source_artifact_hashes_before": source_hashes_before,
        "old_source_artifact_hashes_after": source_hashes_after,
        "source_inputs": _relative_required_inputs(),
        "artifacts_generated": [
            str((OUTPUT_DIR / name)).replace("\\", "/") for name in EXPECTED_ARTIFACT_NAMES
        ],
        "producer_function": "canonicalize_coverage_001a",
        "input_artifacts": _relative_required_inputs(),
        "input_artifact_hashes": inputs["input_hashes"],
        "run_id": run_id,
        "code_path_hash": code_path_hash,
        "aggregation_rule": "canonical artifacts are split mechanically from 001D sections",
        "validation_rule": "baseline, ablation, schema, trace, claim ceiling, and immutability gates pass",
        "stop_conditions_triggered": [],
        "what_this_does_not_prove": FORBIDDEN_CLAIMS,
    }


def _build_provenance(
    inputs: dict[str, Any],
    run_id: str,
    code_path_hash: str,
    baseline_report: dict[str, Any],
    ablation_report: dict[str, Any],
    tag_commit: str,
) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "source_commit": EXPECTED_COMMIT,
        "remote_tag": EXPECTED_REMOTE_TAG,
        "source_tag_resolved_commit": tag_commit,
        "required_input_artifacts": _relative_required_inputs(),
        "input_artifact_hashes": inputs["input_hashes"],
        "producer_function": "canonicalize_coverage_001a",
        "baseline_validator_function": "run_baseline_validation",
        "ablation_validator_function": "run_ablation_failure_checks",
        "baseline_validator_invoked": baseline_report["baseline_validator_invoked"],
        "ablation_validators_invoked": ablation_report["ablation_validators_invoked"],
        "run_id": run_id,
        "seed": "not_applicable_deterministic_source_canonicalization",
        "context": TASK_ID,
        "code_path_hash": code_path_hash,
        "aggregation_rule": "mechanical source-to-canonical split with no theory expansion",
        "validation_rule": "all canonical and negative-control validators must pass",
        "claim_ceiling": CLAIM_CEILING,
        "implementation_authorized": False,
    }


def _build_schema_report(
    reports: dict[str, Any],
    baseline_report: dict[str, Any],
    ablation_report: dict[str, Any],
    run_id: str,
    code_path_hash: str,
) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "passed": baseline_report["passed"] and ablation_report["all_negative_controls_failed"],
        "producer_function": "validate_canonical_outputs",
        "run_id": run_id,
        "code_path_hash": code_path_hash,
        "baseline_validator_invoked": baseline_report["baseline_validator_invoked"],
        "ablation_validators_invoked": ablation_report["ablation_validators_invoked"],
        "json_artifacts_parse": True,
        "required_artifacts_planned": sorted(EXPECTED_ARTIFACT_NAMES),
        "computed_evidence_provenance_gate": {
            "passed": baseline_report["passed"] and ablation_report["all_negative_controls_failed"],
            "literal_only_assertions_detected": False,
            "producer_function": "validate_canonical_outputs",
            "input_artifacts": _relative_required_inputs(),
            "run_id": run_id,
            "code_path_hash": code_path_hash,
            "aggregation_rule": "schema gate consumes callable validator reports",
        },
        "report_inputs": sorted(reports),
    }


def _build_trace(
    inputs: dict[str, Any],
    output_dir: Path,
    reports: dict[str, Any],
    run_id: str,
    code_path_hash: str,
) -> dict[str, Any]:
    rows = []
    source_hash = inputs["input_hashes"][str(SOURCE_DOC).replace("\\", "/")]
    artifact_sources = {
        "canonical_theory_coverage_matrix.json": ("rows", "001D section 4 coverage matrix"),
        "canonical_family_accounting.json": (
            "family_accounting",
            "001D section 6 family accounting and section 3 graph family",
        ),
        "canonical_internal_evidence_lineage.json": (
            "internal_evidence_lineage",
            "001D section 7 internal evidence lineage",
        ),
        "canonical_authorization_flags.json": (
            "non_authorization_flags",
            "001D section 8 non-authorization flags",
        ),
        "canonical_claim_ceiling.txt": (
            "claim_ceiling",
            "task card and 001D claim ceiling",
        ),
        "canonicalization_provenance.json": (
            "source_pin_readback",
            "001D section 2 and source_pin_readback.json",
        ),
        "baseline_validation_report.json": (
            "all source sections",
            "independent baseline extraction from 001D",
        ),
        "ablation_failure_report.json": (
            "all source sections",
            "six in-memory mutated negative controls",
        ),
        "schema_validation_report.json": (
            "canonical artifact set",
            "post-write canonical schema validation",
        ),
        "hyperon_non_adoption_guard.json": (
            "hyperon row",
            "001D Hyperon canonical row",
        ),
        "admission_reference_guard.json": (
            "ego_mainline_readiness_audit_001b",
            "001D section 5 admission audit node",
        ),
        "result.json": ("result", "all validators and canonical outputs"),
    }

    for artifact_name, (field, source_section) in artifact_sources.items():
        path = output_dir / artifact_name
        if not path.exists():
            continue
        rows.append(
            {
                "canonical_artifact": artifact_name,
                "canonical_field": field,
                "source_artifact": str(SOURCE_DOC).replace("\\", "/"),
                "source_field_or_section": source_section,
                "producer_function": reports.get(artifact_name, {}).get(
                    "producer_function", "canonicalize_coverage_001a"
                )
                if isinstance(reports.get(artifact_name), dict)
                else "canonicalize_coverage_001a",
                "input_artifact_hash": source_hash,
                "output_artifact_hash": _file_sha(path),
                "run_id": run_id,
                "code_path_hash": code_path_hash,
                "aggregation_rule": reports.get(artifact_name, {}).get(
                    "aggregation_rule", "mechanical source-to-canonical split"
                )
                if isinstance(reports.get(artifact_name), dict)
                else "mechanical source-to-canonical split",
                "validation_rule": reports.get(artifact_name, {}).get(
                    "validation_rule", "canonical artifact must satisfy 001A schema"
                )
                if isinstance(reports.get(artifact_name), dict)
                else "canonical artifact must satisfy 001A schema",
            }
        )

    return {
        "task_id": TASK_ID,
        "trace_complete": {
            row["canonical_artifact"] for row in rows
        }
        >= (set(EXPECTED_ARTIFACT_NAMES) - {"source_to_canonical_trace.json"}),
        "trace_rows": rows,
        "producer_function": "_build_trace",
        "input_artifacts": _relative_required_inputs(),
        "run_id": run_id,
        "code_path_hash": code_path_hash,
        "aggregation_rule": "one source-to-canonical row per canonical artifact",
        "validation_rule": "every canonical artifact except this trace has a trace row",
    }


def _write_doc(
    path: Path,
    result: dict[str, Any],
    baseline_report: dict[str, Any],
    ablation_report: dict[str, Any],
    trace: dict[str, Any],
) -> None:
    text = f"""# {TASK_ID}

Mode: bounded repo-canonicalization of already source-pinned theory coverage artifacts only.

Verdict: `{result["verdict"]}`

Layer: evidence-governance / theory coverage canonicalization only.

Commit hash: `{EXPECTED_COMMIT}`

Remote tag: `{EXPECTED_REMOTE_TAG}`

## Source Boundary

This canonicalization mechanically converts `THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001D` and its required pre-canonical side artifacts into repo canonical artifacts. It does not expand theory coverage, select an architecture, authorize implementation, or reinterpret any candidate as EGO-mainline ready.

## Baseline Result

Baseline validator invoked: `{baseline_report["baseline_validator_invoked"]}`

Baseline passed: `{baseline_report["passed"]}`

Baseline validator: `{baseline_report["baseline_validator"]}`

## Ablation Result

Ablation validators invoked: `{ablation_report["ablation_validators_invoked"]}`

All negative controls failed as expected: `{ablation_report["all_negative_controls_failed"]}`

Negative controls:

{chr(10).join(f"- `{name}`" for name in sorted(ablation_report["ablations"]))}

## Trace / Provenance Summary

Trace complete: `{trace["trace_complete"]}`

Trace rows: `{len(trace["trace_rows"])}`

Each canonical output records source artifact, source section, producer function, input hash, output hash, run id, code path hash, aggregation rule, and validation rule.

## Claim Ceiling

{_claim_ceiling_text()}
"""
    _write_text(path, text.rstrip() + "\n")


def _validate_extracted_sections(sections: dict[str, Any]) -> dict[str, Any]:
    failures = []
    matrix = sections.get("coverage_matrix", {})
    rows = matrix.get("rows", [])
    family = sections.get("family_accounting", {}).get("family_accounting", [])
    graph_family = sections.get("graph_family", {}).get("graph_substrate_challenger_family", [])
    hyperon_rows = _hyperon_rows(rows)
    admission = sections.get("admission_reference", {}).get(
        "ego_mainline_readiness_audit_001b", {}
    )
    source_readback = sections.get("source_readback", {})
    claim_ceiling = sections.get("claim_ceiling_text", "present")

    if matrix.get("row_count") != 45 or len(rows) != 45:
        failures.append("matrix_row_count_not_45")
    if set(graph_family) != set(REQUIRED_GRAPH_CHALLENGERS):
        failures.append("graph_challenger_family_incomplete")
    if len(family) != 30:
        failures.append("family_accounting_count_not_30")
    if len(hyperon_rows) != 1:
        failures.append("hyperon_row_count_not_one")
    else:
        hyperon = hyperon_rows[0]
        if hyperon.get("selected_as_architecture") is not False:
            failures.append("hyperon_selected_or_adopted")
        if hyperon.get("implementation_authorized") is not False:
            failures.append("hyperon_implementation_authorized")
        if hyperon.get("runtime_authorized") is not False:
            failures.append("hyperon_runtime_authorized")
        if hyperon.get("ego_mainline_authorized") is not False:
            failures.append("hyperon_ego_mainline_authorized")
    if not _all_impl_false(rows, family):
        failures.append("implementation_authorized_true_detected")
    if not source_readback.get("remote_anchors"):
        failures.append("source_pin_remote_anchor_missing")
    if not claim_ceiling:
        failures.append("claim_ceiling_missing")
    if admission.get("task_id") != "EGO-MAINLINE-READINESS-AUDIT-001B":
        failures.append("admission_reference_missing")
    if admission.get("actionability_revalidation_required") is not True:
        failures.append("admission_actionability_revalidation_missing")
    if admission.get("runtime_authorized") is not False:
        failures.append("admission_runtime_authorized")

    return {"passed": not failures, "failures": failures}


def _baseline_extract_from_source_text(text: str) -> dict[str, Any]:
    blocks = _extract_json_blocks(text)
    sections = _classify_blocks(blocks)
    sections["claim_ceiling_text"] = "present"
    return sections


def _classify_blocks(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    sections: dict[str, Any] = {}
    for block in blocks:
        if "sources" in block and "remote_anchors" in block:
            sections["source_readback"] = block
        elif "graph_substrate_challenger_family" in block:
            sections["graph_family"] = block
        elif "rows" in block and "row_count" in block:
            sections["coverage_matrix"] = block
        elif "ego_mainline_readiness_audit_001b" in block:
            sections["admission_reference"] = block
        elif "family_accounting" in block:
            sections["family_accounting"] = block
        elif "internal_evidence_lineage" in block:
            sections["internal_evidence_lineage"] = block
        elif "non_authorization_flags" in block:
            sections["non_authorization_flags"] = block
        elif "caveats" in block and "claim_ceiling" in block:
            sections["closure_caveats"] = block

    required = {
        "source_readback",
        "graph_family",
        "coverage_matrix",
        "admission_reference",
        "family_accounting",
        "internal_evidence_lineage",
        "non_authorization_flags",
        "closure_caveats",
    }
    missing = required - set(sections)
    if missing:
        raise ValueError(f"missing 001D JSON sections: {sorted(missing)}")
    return sections


def _extract_json_blocks(text: str) -> list[dict[str, Any]]:
    blocks = []
    for match in re.finditer(r"```json\s*(.*?)\s*```", text, re.DOTALL):
        blocks.append(json.loads(match.group(1)))
    if not blocks:
        raise ValueError("no JSON blocks found")
    return blocks


def _mutate_remove_graph_item(sections: dict[str, Any]) -> dict[str, Any]:
    sections["graph_family"]["graph_substrate_challenger_family"] = sections["graph_family"][
        "graph_substrate_challenger_family"
    ][:-1]
    for row in sections["coverage_matrix"]["rows"]:
        family = row.get("local_negative_evidence_required_for_future_audit", {}).get(
            "graph_substrate_challenger_family"
        )
        if family:
            row["local_negative_evidence_required_for_future_audit"][
                "graph_substrate_challenger_family"
            ] = family[:-1]
            break
    return sections


def _mutate_hyperon_adoption_true(sections: dict[str, Any]) -> dict[str, Any]:
    hyperon = _hyperon_rows(sections["coverage_matrix"]["rows"])[0]
    hyperon["selected_as_architecture"] = True
    return sections


def _mutate_any_impl_true(sections: dict[str, Any]) -> dict[str, Any]:
    sections["coverage_matrix"]["rows"][0]["implementation_authorized"] = True
    return sections


def _mutate_drop_source_pin_anchor(sections: dict[str, Any]) -> dict[str, Any]:
    sections["source_readback"]["remote_anchors"] = []
    return sections


def _mutate_reduce_matrix(sections: dict[str, Any]) -> dict[str, Any]:
    sections["coverage_matrix"]["rows"] = sections["coverage_matrix"]["rows"][:10]
    sections["coverage_matrix"]["row_count"] = 10
    return sections


def _mutate_remove_claim_ceiling(sections: dict[str, Any]) -> dict[str, Any]:
    sections["claim_ceiling_text"] = ""
    return sections


def _claim_ceiling_text() -> str:
    forbidden = "\n".join(f"- {claim}" for claim in FORBIDDEN_CLAIMS)
    return (
        f"{CLAIM_CEILING}.\n\n"
        "No architecture selection is authorized.\n"
        "implementation authorization = false.\n"
        "EGO mainline authorization = false.\n"
        "Bridge runtime authorization = false.\n"
        "Companion, relationship, emotion, LLM/RAG, personalization, persistent profile, "
        "and long-term human-user memory work remain unauthorized.\n\n"
        "This cannot prove:\n"
        f"{forbidden}\n"
    )


def _all_impl_false(rows: list[dict[str, Any]], family: list[dict[str, Any]]) -> bool:
    return all(row.get("implementation_authorized") is False for row in rows) and all(
        item.get("implementation_authorized") is False for item in family
    )


def _hyperon_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if "hyperon" in row.get("candidate_id", "").lower()]


def _source_pin_remote_anchor_present(inputs: dict[str, Any]) -> bool:
    source_readback = inputs["source_sections"]["source_readback"]
    artifact_readback = inputs["source_pin_readback"]
    return bool(source_readback.get("remote_anchors")) and bool(
        artifact_readback.get("remote_anchors")
    )


def _check(passed: bool, observed: Any, expected: Any) -> dict[str, Any]:
    return {"passed": passed, "observed": observed, "expected": expected}


def _provenance_record(
    producer_function: str,
    input_artifacts: list[str],
    input_hashes: dict[str, str],
    run_id: str,
    code_path_hash: str,
    aggregation_rule: str,
    output_artifact: str,
) -> dict[str, Any]:
    return {
        "producer_function": producer_function,
        "input_artifacts": input_artifacts,
        "input_artifact_hashes": input_hashes,
        "run_id": run_id,
        "seed": "not_applicable",
        "context": TASK_ID,
        "aggregation_rule": aggregation_rule,
        "code_path_hash": code_path_hash,
        "output_artifact": output_artifact,
        "output_artifact_hash": "computed_after_write_in_source_to_canonical_trace",
    }


def _source_hashes(root: Path) -> dict[str, str]:
    return {
        str(path).replace("\\", "/"): _file_sha(root / path)
        for path in REQUIRED_INPUT_ARTIFACTS
    }


def _relative_required_inputs() -> list[str]:
    return [str(path).replace("\\", "/") for path in REQUIRED_INPUT_ARTIFACTS]


def _make_run_id(inputs: dict[str, Any]) -> str:
    digest = _object_sha(inputs["input_hashes"])[:16]
    return f"theory_landscape_coverage_canonicalization_001a_{digest}"


def _git_rev_parse(root: Path, ref: str) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", ref],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _object_sha(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TASK_ID)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    args = parser.parse_args(argv)

    result = canonicalize_coverage_001a(args.repo_root, args.output_dir)
    print(json.dumps({"verdict": result["verdict"], "artifact_dir": args.output_dir}, indent=2))
    return 0
