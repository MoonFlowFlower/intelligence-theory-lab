from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
from typing import Any, Callable


TASK_ID = "EGO-MAINLINE-ADMISSION-CANONICAL-COVERAGE-REFERENCE-001A"
VERDICT_PASS = "ego_mainline_admission_canonical_coverage_reference_001a_pass"
VERDICT_BLOCKED_EQUIVALENT = "redundant_reference_contract_blocked"
LAYER = "evidence-governance / admission-planning reference contract only"
CLAIM_CEILING = "bounded admission-side reference integration for sealed canonical theory coverage only"

SEALED_COVERAGE_COMMIT = "df6ad31ed58d2e3772e3f53b35ad926ab995d582"
SEALED_COVERAGE_REMOTE_TAG = "remote-anchor-coverage-canonicalization-repair-001b-df6ad31"
UNDERLYING_SOURCE_COMMIT = "614b147d14cc4bb02b7c6afa2c90661cdce15e4c"
UNDERLYING_SOURCE_REMOTE_TAG = "remote-anchor-coverage-compression-001d-614b147"
PRIOR_ADMISSION_AUDIT_COMMIT = "f648dac4bfbcdc7a98c1edea5a97dbef4101d83a"
PRIOR_ADMISSION_AUDIT_STATUS = (
    "committed audit reference only; authorizes admission task-card drafting only; "
    "does not authorize runtime, bridge runtime, companion behavior, or implementation"
)

ARTIFACT_DIR = Path("artifacts/ego_mainline_admission_canonical_coverage_reference_001a")
DOC_PATH = Path("docs/research/EGO-MAINLINE-ADMISSION-CANONICAL-COVERAGE-REFERENCE-001A.md")
CANONICAL_DIR = Path("artifacts/theory_landscape_coverage_canonicalization_001a")
REPAIR_DIR = Path("artifacts/theory_landscape_coverage_canonicalization_provenance_repair_001b")
PRIOR_ADMISSION_DIR = Path("artifacts/ego_mainline_readiness_audit_001b")
PRIOR_ADMISSION_DOC = Path("docs/codex/audits/EGO-MAINLINE-READINESS-AUDIT-001B.md")
SOURCE_DOC_001D = Path("docs/research/THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001D.md")
PHASE_ONE_SOURCE_DOC = Path("docs/research/PHASE-ONE-THEORY-LANDSCAPE-COVERAGE-AUDIT.md")

REQUIRED_ARTIFACT_NAMES = [
    "result.json",
    "reference_contract.json",
    "sealed_input_anchor_manifest.json",
    "downstream_usage_matrix.json",
    "forbidden_claims_matrix.json",
    "implementation_authorization_guard.json",
    "hyperon_non_adoption_guard.json",
    "admission_actionability_revalidation_guard.json",
    "duplication_prevention_report.json",
    "existing_reference_search_report.json",
    "source_trace_report.json",
    "claim_ceiling.txt",
]

ALLOWED_DOWNSTREAM_USE = [
    "reference-only theory coverage boundary",
    "source-pinned candidate landscape",
    "risk/caveat inventory",
    "negative authorization guard",
    "input to future admission task-card drafting",
    "constraint source for future actionability revalidation",
]

FORBIDDEN_DOWNSTREAM_USE = [
    "EGO readiness evidence",
    "AGI readiness evidence",
    "bridge readiness evidence",
    "companion readiness evidence",
    "runtime authorization",
    "implementation authorization",
    "Hyperon adoption",
    "architecture selection",
    "architecture correctness evidence",
    "mechanism validity evidence",
    "theory validity evidence",
    "agency evidence",
    "selfhood evidence",
    "consciousness evidence",
    "subjective experience evidence",
    "real emotion evidence",
    "real relationship learning evidence",
    "stable user benefit evidence",
    "future EGO runtime correctness evidence",
]

REQUIRED_FORBIDDEN_CLAIMS = [
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
    "subjective experience",
    "real emotion",
    "real relationship learning",
    "stable user benefit",
    "future EGO runtime correctness",
]

AUTHORIZATION_FALSE_FIELDS = [
    "implementation_authorized",
    "runtime_authorized",
    "bridge_authorized",
    "companion_authorized",
    "architecture_adopted",
    "hyperon_adopted",
]

PROTECTED_INPUTS = [
    SOURCE_DOC_001D,
    PHASE_ONE_SOURCE_DOC,
    Path("artifacts/phase_one_theory_landscape_source_pin_001a/source_pin_manifest.json"),
    Path("artifacts/theory_landscape_coverage_precanonical_closure_patch_001b/source_pin_readback.json"),
    Path("artifacts/theory_landscape_coverage_precanonical_closure_patch_001b/delta_manifest.json"),
    Path("artifacts/theory_landscape_coverage_precanonical_closure_patch_001b/closure_caveat_resolution_matrix.json"),
    Path("artifacts/theory_landscape_coverage_precanonical_closure_patch_001b/schema_safety_check.json"),
    Path("artifacts/theory_landscape_coverage_precanonical_closure_patch_001b/claim_ceiling.txt"),
    CANONICAL_DIR / "canonical_theory_coverage_matrix.json",
    CANONICAL_DIR / "canonical_family_accounting.json",
    CANONICAL_DIR / "canonical_authorization_flags.json",
    CANONICAL_DIR / "canonicalization_provenance.json",
    CANONICAL_DIR / "admission_reference_guard.json",
    CANONICAL_DIR / "hyperon_non_adoption_guard.json",
    CANONICAL_DIR / "canonical_claim_ceiling.txt",
    CANONICAL_DIR / "source_to_canonical_trace.json",
    REPAIR_DIR / "result.json",
    REPAIR_DIR / "trace_artifact_provenance_entry.json",
    REPAIR_DIR / "repair_validation_report.json",
    PRIOR_ADMISSION_DOC,
    PRIOR_ADMISSION_DIR / "result.json",
    PRIOR_ADMISSION_DIR / "downstream_authorization_matrix.json",
]


def run_reference_contract(
    repo_root: Path | str | None = None,
    output_dir: Path | str | None = None,
    verify_remote: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    out = Path(output_dir) if output_dir is not None else root / ARTIFACT_DIR
    if not out.is_absolute():
        out = root / out
    out.mkdir(parents=True, exist_ok=True)

    input_hashes_before = _hash_paths(root, PROTECTED_INPUTS)
    run_id = _run_id(root)

    existing_reference = search_existing_reference_contract(root)
    if existing_reference["equivalent_reference_contract_found"]:
        result = _blocked_result(existing_reference, run_id)
        _write_json(out / "existing_reference_search_report.json", _with_metadata(
            "existing_reference_search_report.json",
            existing_reference,
            search_existing_reference_contract,
            [str(DOC_PATH), str(ARTIFACT_DIR)],
            run_id,
            "scan existing docs/artifacts for an equivalent admission-side canonical coverage reference contract",
            "if an equivalent reference contract exists, block duplicate schema creation",
        ))
        _write_json(out / "result.json", _with_metadata(
            "result.json",
            result,
            _blocked_result,
            ["existing_reference_search_report.json"],
            run_id,
            "return redundant reference blocker without creating a second schema",
            "duplicate schema creation must be blocked",
        ))
        return result

    canonical = _load_canonical_inputs(root)
    anchor_manifest = build_sealed_input_anchor_manifest(root, verify_remote=verify_remote)
    reference_contract = build_reference_contract(canonical, anchor_manifest)
    validator_results = validate_reference_contract(reference_contract, canonical)
    ablation_report = run_ablation_negative_controls(reference_contract, canonical)

    artifacts: dict[str, dict[str, Any]] = {}
    artifacts["reference_contract.json"] = _with_metadata(
        "reference_contract.json",
        reference_contract,
        build_reference_contract,
        _contract_inputs(),
        run_id,
        "compose reference-only admission contract from sealed anchors and prior admission audit",
        "contract must preserve reference-only semantics and block implementation/runtime adoption",
    )
    artifacts["sealed_input_anchor_manifest.json"] = _with_metadata(
        "sealed_input_anchor_manifest.json",
        anchor_manifest,
        build_sealed_input_anchor_manifest,
        _contract_inputs(),
        run_id,
        "resolve local and optional remote refs for sealed coverage, source, and prior admission references",
        "required anchors must be recorded exactly",
    )
    artifacts["downstream_usage_matrix.json"] = _with_metadata(
        "downstream_usage_matrix.json",
        build_downstream_usage_matrix(reference_contract),
        build_downstream_usage_matrix,
        ["reference_contract.json"],
        run_id,
        "split allowed and forbidden downstream use without upgrading evidence",
        "allowed use must remain reference-only and forbidden use must stay blocked",
    )
    artifacts["forbidden_claims_matrix.json"] = _with_metadata(
        "forbidden_claims_matrix.json",
        build_forbidden_claims_matrix(reference_contract),
        build_forbidden_claims_matrix,
        ["reference_contract.json"],
        run_id,
        "materialize required forbidden claims as explicit blocked rows",
        "all required forbidden claims must be blocked",
    )
    artifacts["implementation_authorization_guard.json"] = _with_metadata(
        "implementation_authorization_guard.json",
        build_implementation_authorization_guard(reference_contract, validator_results),
        build_implementation_authorization_guard,
        ["reference_contract.json"],
        run_id,
        "evaluate non-authorization fields through callable validators",
        "implementation, runtime, bridge, companion, and architecture authorization must remain false",
    )
    artifacts["hyperon_non_adoption_guard.json"] = _with_metadata(
        "hyperon_non_adoption_guard.json",
        build_hyperon_non_adoption_guard(canonical, reference_contract),
        build_hyperon_non_adoption_guard,
        ["reference_contract.json", str(CANONICAL_DIR / "hyperon_non_adoption_guard.json")],
        run_id,
        "copy only Hyperon non-adoption guard facts, not the coverage matrix",
        "Hyperon must remain non-adopted and non-authorized",
    )
    artifacts["admission_actionability_revalidation_guard.json"] = _with_metadata(
        "admission_actionability_revalidation_guard.json",
        build_actionability_revalidation_guard(canonical, reference_contract),
        build_actionability_revalidation_guard,
        ["reference_contract.json", str(CANONICAL_DIR / "admission_reference_guard.json"), str(PRIOR_ADMISSION_DOC)],
        run_id,
        "preserve prior admission audit as reference-only and require future actionability revalidation",
        "future admission must require actionability revalidation",
    )
    artifacts["duplication_prevention_report.json"] = _with_metadata(
        "duplication_prevention_report.json",
        build_duplication_prevention_report(reference_contract, artifacts),
        build_duplication_prevention_report,
        ["reference_contract.json", str(CANONICAL_DIR / "canonical_theory_coverage_matrix.json")],
        run_id,
        "scan new reference payloads for copied canonical matrix rows",
        "new artifacts must not copy the 45-row canonical coverage matrix",
    )
    artifacts["existing_reference_search_report.json"] = _with_metadata(
        "existing_reference_search_report.json",
        existing_reference,
        search_existing_reference_contract,
        [str(DOC_PATH), str(ARTIFACT_DIR)],
        run_id,
        "scan existing docs/artifacts before creating this contract",
        "no equivalent reference contract may already exist",
    )

    result_payload = build_result(
        reference_contract=reference_contract,
        anchor_manifest=anchor_manifest,
        validator_results=validator_results,
        ablation_report=ablation_report,
        existing_reference=existing_reference,
        artifacts=artifacts,
        input_hashes_before=input_hashes_before,
        input_hashes_after=_hash_paths(root, PROTECTED_INPUTS),
    )
    artifacts["result.json"] = _with_metadata(
        "result.json",
        result_payload,
        build_result,
        sorted(name for name in artifacts),
        run_id,
        "aggregate callable validators, negative controls, and source immutability checks",
        "accept only when reference contract is bounded, non-duplicative, and all mutation controls fail",
    )

    for name, payload in artifacts.items():
        _write_json(out / name, payload)

    _write_text(out / "claim_ceiling.txt", CLAIM_CEILING + "\n")
    source_trace = build_source_trace_report(root, out, artifacts, run_id)
    _write_json(out / "source_trace_report.json", _with_metadata(
        "source_trace_report.json",
        source_trace,
        build_source_trace_report,
        sorted(name for name in artifacts) + ["claim_ceiling.txt"],
        run_id,
        "trace every new reference artifact to the sealed coverage boundary, source anchor, and prior admission audit",
        "each required artifact must have trace rows to the sealed boundary and source anchor",
    ))
    _write_doc(root / DOC_PATH, result_payload, reference_contract, existing_reference, ablation_report)
    return result_payload


def build_reference_contract(canonical: dict[str, Any], anchor_manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_id": TASK_ID,
        "layer": LAYER,
        "sealed_coverage_commit": SEALED_COVERAGE_COMMIT,
        "sealed_coverage_remote_tag": SEALED_COVERAGE_REMOTE_TAG,
        "sealed_coverage_remote_tag_verified": anchor_manifest["sealed_coverage_anchor"]["remote_verified"],
        "underlying_source_commit": UNDERLYING_SOURCE_COMMIT,
        "underlying_source_remote_tag": UNDERLYING_SOURCE_REMOTE_TAG,
        "underlying_source_remote_tag_verified": anchor_manifest["underlying_source_anchor"]["remote_verified"],
        "prior_admission_audit_commit": PRIOR_ADMISSION_AUDIT_COMMIT,
        "prior_admission_audit_status": PRIOR_ADMISSION_AUDIT_STATUS,
        "prior_admission_audit_reference": str(PRIOR_ADMISSION_DOC),
        "prior_admission_audit_authorizes": ["admission task-card drafting only"],
        "prior_admission_audit_does_not_authorize": [
            "EGO runtime",
            "bridge runtime",
            "companion behavior",
            "implementation",
        ],
        "allowed_downstream_use": list(ALLOWED_DOWNSTREAM_USE),
        "forbidden_downstream_use": list(FORBIDDEN_DOWNSTREAM_USE),
        "implementation_authorized": False,
        "runtime_authorized": False,
        "bridge_authorized": False,
        "companion_authorized": False,
        "architecture_adopted": False,
        "hyperon_adopted": False,
        "hyperon_implementation_authorized": False,
        "hyperon_runtime_authorized": False,
        "hyperon_ego_mainline_dependency": False,
        "actionability_revalidation_required": True,
        "matrix_duplication_allowed": False,
        "theory_expansion_allowed": False,
        "new_deep_research_allowed": False,
        "new_theory_audit_allowed": False,
        "claim_ceiling_reference": CLAIM_CEILING,
        "canonical_coverage_claim_ceiling_reference": canonical["canonicalization_provenance"]["claim_ceiling"],
        "canonical_matrix_reference": {
            "artifact": str(CANONICAL_DIR / "canonical_theory_coverage_matrix.json"),
            "row_count": canonical["matrix"]["row_count"],
            "usage": "referenced by path and hash only; rows are not copied into this contract",
            "matrix_duplication_allowed": False,
        },
    }


def build_sealed_input_anchor_manifest(root: Path, verify_remote: bool = True) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "layer": LAYER,
        "sealed_coverage_anchor": _verify_anchor(
            root,
            "sealed_coverage_repair",
            SEALED_COVERAGE_COMMIT,
            SEALED_COVERAGE_REMOTE_TAG,
            verify_remote,
        ),
        "underlying_source_anchor": _verify_anchor(
            root,
            "underlying_source_coverage_compression",
            UNDERLYING_SOURCE_COMMIT,
            UNDERLYING_SOURCE_REMOTE_TAG,
            verify_remote,
        ),
        "prior_admission_audit": {
            "boundary": "EGO-MAINLINE-READINESS-AUDIT-001B",
            "commit": PRIOR_ADMISSION_AUDIT_COMMIT,
            "local_commit_exists": _git_success(root, ["cat-file", "-e", f"{PRIOR_ADMISSION_AUDIT_COMMIT}^{{commit}}"]),
            "status": PRIOR_ADMISSION_AUDIT_STATUS,
            "reference_only": True,
            "runtime_authorized": False,
            "implementation_authorized": False,
            "doc_path": str(PRIOR_ADMISSION_DOC),
        },
        "validation_rule": "sealed coverage repair, underlying source, and prior admission references must be recorded exactly",
    }


def build_downstream_usage_matrix(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "allowed_downstream_use": [
            {"use": item, "allowed": True, "claim_ceiling": CLAIM_CEILING}
            for item in contract["allowed_downstream_use"]
        ],
        "forbidden_downstream_use": [
            {"use": item, "allowed": False, "blocked_reason": "sealed coverage is reference-only"}
            for item in contract["forbidden_downstream_use"]
        ],
        "reference_only_semantics_explicit": True,
        "implementation_authorized": contract["implementation_authorized"],
        "runtime_authorized": contract["runtime_authorized"],
        "validation_rule": "allowed rows are reference-only; forbidden rows must remain blocked",
    }


def build_forbidden_claims_matrix(contract: dict[str, Any]) -> dict[str, Any]:
    forbidden_text = "\n".join(contract.get("forbidden_downstream_use", []))
    return {
        "task_id": TASK_ID,
        "claim_ceiling": contract["claim_ceiling_reference"],
        "forbidden_claims": [
            {
                "claim": claim,
                "blocked": claim in forbidden_text or claim in contract["claim_ceiling_reference"],
                "blocked_as": "not supported by sealed canonical coverage reference",
            }
            for claim in REQUIRED_FORBIDDEN_CLAIMS
        ],
        "validation_rule": "every required forbidden claim must be explicitly blocked",
    }


def build_implementation_authorization_guard(
    contract: dict[str, Any], validator_results: list[dict[str, Any]]
) -> dict[str, Any]:
    auth = next(row for row in validator_results if row["validator"] == "validate_authorization_guards")
    return {
        "task_id": TASK_ID,
        "authorization_fields": {
            field: contract.get(field)
            for field in AUTHORIZATION_FALSE_FIELDS
        },
        "implementation_authorized": contract["implementation_authorized"],
        "runtime_authorized": contract["runtime_authorized"],
        "bridge_authorized": contract["bridge_authorized"],
        "companion_authorized": contract["companion_authorized"],
        "all_authorization_guards_passed": auth["passed"],
        "validator_failures": auth["failures"],
        "validation_rule": "all authorization/adoption fields must remain false",
    }


def build_hyperon_non_adoption_guard(
    canonical: dict[str, Any], contract: dict[str, Any]
) -> dict[str, Any]:
    guard = canonical["hyperon_guard"]
    return {
        "task_id": TASK_ID,
        "source_guard_artifact": str(CANONICAL_DIR / "hyperon_non_adoption_guard.json"),
        "canonical_hyperon_row_count": guard["canonical_hyperon_row_count"],
        "hyperon_candidate_id": guard["hyperon_candidate_id"],
        "hyperon_adopted": contract["hyperon_adopted"],
        "hyperon_implementation_authorized": contract["hyperon_implementation_authorized"],
        "hyperon_runtime_authorized": contract["hyperon_runtime_authorized"],
        "hyperon_ego_mainline_dependency": contract["hyperon_ego_mainline_dependency"],
        "hyperon_not_adopted": guard["hyperon_not_adopted"] and not contract["hyperon_adopted"],
        "hyperon_not_implementation_authorized": guard["hyperon_not_implementation_authorized"]
        and not contract["hyperon_implementation_authorized"],
        "hyperon_not_runtime_authorized": guard["hyperon_not_runtime_authorized"]
        and not contract["hyperon_runtime_authorized"],
        "hyperon_not_ego_mainline_dependency": guard["hyperon_not_ego_mainline_dependency"]
        and not contract["hyperon_ego_mainline_dependency"],
        "matrix_duplication_allowed": contract["matrix_duplication_allowed"],
        "validation_rule": "Hyperon remains exactly one referenced canonical row and is not adopted or authorized",
    }


def build_actionability_revalidation_guard(
    canonical: dict[str, Any], contract: dict[str, Any]
) -> dict[str, Any]:
    admission = canonical["admission_guard"]
    return {
        "task_id": TASK_ID,
        "prior_admission_audit": "EGO-MAINLINE-READINESS-AUDIT-001B",
        "prior_admission_audit_commit": contract["prior_admission_audit_commit"],
        "prior_admission_audit_status": contract["prior_admission_audit_status"],
        "committed_audit_reference_only": admission["committed_audit_reference_only"],
        "canonical_admission_reference_only": admission["downstream_positive_evidence"] is False,
        "actionability_revalidation_required": contract["actionability_revalidation_required"],
        "runtime_authorized": contract["runtime_authorized"],
        "implementation_authorized": contract["implementation_authorized"],
        "validation_rule": "prior admission audit remains reference-only and future actionability revalidation remains required",
    }


def build_duplication_prevention_report(
    contract: dict[str, Any], artifacts: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    row_like_lists = []
    for name, payload in artifacts.items():
        for path, value in _walk(payload):
            if (
                isinstance(value, list)
                and len(value) >= 40
                and all(isinstance(item, dict) and "candidate_id" in item for item in value)
            ):
                row_like_lists.append({"artifact": name, "path": path, "row_count": len(value)})
    return {
        "task_id": TASK_ID,
        "matrix_duplication_allowed": contract["matrix_duplication_allowed"],
        "canonical_matrix_row_count_referenced": contract["canonical_matrix_reference"]["row_count"],
        "copied_45_row_matrix_detected": bool(row_like_lists),
        "row_like_lists": row_like_lists,
        "matrix_reference_method": "path/hash/row-count reference only; no row payload copied",
        "validation_rule": "new artifacts must not contain a copied 45-row canonical matrix",
    }


def build_result(
    reference_contract: dict[str, Any],
    anchor_manifest: dict[str, Any],
    validator_results: list[dict[str, Any]],
    ablation_report: dict[str, Any],
    existing_reference: dict[str, Any],
    artifacts: dict[str, dict[str, Any]],
    input_hashes_before: dict[str, str],
    input_hashes_after: dict[str, str],
) -> dict[str, Any]:
    validators_passed = all(row["passed"] for row in validator_results)
    negative_controls_passed = ablation_report["all_negative_controls_failed"]
    old_inputs_modified = input_hashes_before != input_hashes_after
    stop_conditions = []
    if existing_reference["equivalent_reference_contract_found"]:
        stop_conditions.append("equivalent_reference_contract_exists")
    if not validators_passed:
        stop_conditions.append("reference_contract_validation_failed")
    if not negative_controls_passed:
        stop_conditions.append("ablation_negative_control_failed_to_fail")
    if old_inputs_modified:
        stop_conditions.append("sealed_source_or_canonical_artifact_modified")
    return {
        "task_id": TASK_ID,
        "verdict": VERDICT_PASS if not stop_conditions else "blocked_or_failed",
        "layer": LAYER,
        "claim_ceiling": CLAIM_CEILING,
        "existing_reference_contract_found": existing_reference["equivalent_reference_contract_found"],
        "sealed_coverage_commit": reference_contract["sealed_coverage_commit"],
        "sealed_coverage_remote_tag": reference_contract["sealed_coverage_remote_tag"],
        "underlying_source_commit": reference_contract["underlying_source_commit"],
        "underlying_source_remote_tag": reference_contract["underlying_source_remote_tag"],
        "prior_admission_audit_commit": reference_contract["prior_admission_audit_commit"],
        "prior_admission_audit_status": reference_contract["prior_admission_audit_status"],
        "implementation_authorized": False,
        "runtime_authorized": False,
        "bridge_authorized": False,
        "companion_authorized": False,
        "architecture_adopted": False,
        "hyperon_adopted": False,
        "actionability_revalidation_required": True,
        "matrix_duplication_allowed": False,
        "theory_expansion_allowed": False,
        "new_deep_research_allowed": False,
        "validators": validator_results,
        "all_validators_passed": validators_passed,
        "ablation_negative_controls": ablation_report,
        "sealed_source_or_canonical_artifacts_modified": old_inputs_modified,
        "protected_input_hashes_before": input_hashes_before,
        "protected_input_hashes_after": input_hashes_after,
        "artifacts_generated": [str(ARTIFACT_DIR / name) for name in REQUIRED_ARTIFACT_NAMES],
        "artifact_payload_hashes": {
            name: payload["computed_evidence_provenance"]["output_artifact_hash"]
            for name, payload in artifacts.items()
        },
        "stop_conditions_triggered": stop_conditions,
        "what_this_does_not_prove": REQUIRED_FORBIDDEN_CLAIMS,
    }


def build_source_trace_report(
    root: Path, output_dir: Path, artifacts: dict[str, dict[str, Any]], run_id: str
) -> dict[str, Any]:
    artifact_names = sorted(set(REQUIRED_ARTIFACT_NAMES) - {"claim_ceiling.txt", "source_trace_report.json"})
    rows = []
    for name in artifact_names:
        path = output_dir / name
        materialized_hash = _sha_file(path) if path.exists() else None
        output_payload_hash = (
            artifacts[name]["computed_evidence_provenance"]["output_artifact_hash"]
            if name in artifacts
            else None
        )
        for boundary, commit, tag, input_reference in [
            (
                "sealed_coverage_repair",
                SEALED_COVERAGE_COMMIT,
                SEALED_COVERAGE_REMOTE_TAG,
                str(REPAIR_DIR / "result.json"),
            ),
            (
                "underlying_source_coverage_compression",
                UNDERLYING_SOURCE_COMMIT,
                UNDERLYING_SOURCE_REMOTE_TAG,
                str(SOURCE_DOC_001D),
            ),
            (
                "prior_admission_audit",
                PRIOR_ADMISSION_AUDIT_COMMIT,
                None,
                str(PRIOR_ADMISSION_DOC),
            ),
        ]:
            rows.append(
                {
                    "artifact": str(ARTIFACT_DIR / name),
                    "referenced_boundary": boundary,
                    "referenced_commit": commit,
                    "referenced_tag": tag,
                    "producer_function": "build_source_trace_report",
                    "input_reference": input_reference,
                    "output_artifact_hash": output_payload_hash,
                    "materialized_artifact_hash": materialized_hash,
                    "run_id": run_id,
                    "code_path_hash": _code_path_hash(build_source_trace_report),
                    "validation_rule": "artifact must trace back to sealed coverage repair, underlying source, and prior admission audit where applicable",
                }
            )
    rows.append(
        {
            "artifact": str(ARTIFACT_DIR / "claim_ceiling.txt"),
            "referenced_boundary": "claim_ceiling",
            "referenced_commit": SEALED_COVERAGE_COMMIT,
            "referenced_tag": SEALED_COVERAGE_REMOTE_TAG,
            "producer_function": "run_reference_contract",
            "input_reference": CLAIM_CEILING,
            "output_artifact_hash": _sha_text(CLAIM_CEILING + "\n"),
            "materialized_artifact_hash": _sha_file(output_dir / "claim_ceiling.txt")
            if (output_dir / "claim_ceiling.txt").exists()
            else None,
            "run_id": run_id,
            "code_path_hash": _code_path_hash(run_reference_contract),
            "validation_rule": "claim ceiling text must stay bounded to admission-side reference integration",
        }
    )
    report = {
        "task_id": TASK_ID,
        "trace_rows": rows,
        "artifacts_traced": sorted({row["artifact"] for row in rows}),
        "sealed_coverage_commit": SEALED_COVERAGE_COMMIT,
        "sealed_coverage_remote_tag": SEALED_COVERAGE_REMOTE_TAG,
        "underlying_source_commit": UNDERLYING_SOURCE_COMMIT,
        "underlying_source_remote_tag": UNDERLYING_SOURCE_REMOTE_TAG,
        "prior_admission_audit_commit": PRIOR_ADMISSION_AUDIT_COMMIT,
        "validation_rule": "every new reference artifact has source trace rows",
    }
    self_payload_hash = _payload_hash(report)
    for boundary, commit, tag, input_reference in [
        (
            "sealed_coverage_repair",
            SEALED_COVERAGE_COMMIT,
            SEALED_COVERAGE_REMOTE_TAG,
            str(REPAIR_DIR / "result.json"),
        ),
        (
            "underlying_source_coverage_compression",
            UNDERLYING_SOURCE_COMMIT,
            UNDERLYING_SOURCE_REMOTE_TAG,
            str(SOURCE_DOC_001D),
        ),
        (
            "prior_admission_audit",
            PRIOR_ADMISSION_AUDIT_COMMIT,
            None,
            str(PRIOR_ADMISSION_DOC),
        ),
    ]:
        rows.append(
            {
                "artifact": str(ARTIFACT_DIR / "source_trace_report.json"),
                "referenced_boundary": boundary,
                "referenced_commit": commit,
                "referenced_tag": tag,
                "producer_function": "build_source_trace_report",
                "input_reference": input_reference,
                "output_artifact_hash": self_payload_hash,
                "output_hash_scope": "source_trace_report payload before self-trace rows and computed_evidence_provenance envelope",
                "materialized_artifact_hash": None,
                "run_id": run_id,
                "code_path_hash": _code_path_hash(build_source_trace_report),
                "validation_rule": "source trace report self-row records its pre-envelope payload hash to avoid circular hash recursion",
            }
        )
    report["trace_rows"] = rows
    report["artifacts_traced"] = sorted({row["artifact"] for row in rows})
    return report


def search_existing_reference_contract(root: Path) -> dict[str, Any]:
    candidate_paths = []
    search_roots = [root / "docs", root / "artifacts"]
    for search_root in search_roots:
        if not search_root.exists():
            continue
        for path in search_root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".txt"}:
                continue
            rel = _rel(path, root)
            if rel.startswith(str(DOC_PATH).replace("\\", "/")):
                continue
            if rel.startswith(str(ARTIFACT_DIR).replace("\\", "/")):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            lowered = text.lower()
            if (
                SEALED_COVERAGE_COMMIT in text
                or SEALED_COVERAGE_REMOTE_TAG in text
                or ("canonical coverage" in lowered and "admission" in lowered)
                or ("sealed canonical" in lowered and "admission" in lowered)
            ):
                candidate_paths.append(
                    {
                        "path": rel,
                        "references_sealed_commit": SEALED_COVERAGE_COMMIT in text,
                        "references_sealed_remote_tag": SEALED_COVERAGE_REMOTE_TAG in text,
                        "references_prior_admission_audit": "EGO-MAINLINE-READINESS-AUDIT-001B" in text,
                        "preserves_claim_ceiling": CLAIM_CEILING in text
                        or "bounded" in lowered and "reference" in lowered,
                        "blocks_implementation_authorization": "implementation_authorized" in text
                        and "false" in lowered,
                        "prevents_matrix_duplication": "matrix_duplication" in text
                        or "do not duplicate" in lowered,
                        "requires_actionability_revalidation": "actionability_revalidation_required" in text,
                    }
                )
    equivalent = [
        row
        for row in candidate_paths
        if row["references_sealed_commit"]
        and row["references_sealed_remote_tag"]
        and row["blocks_implementation_authorization"]
        and row["prevents_matrix_duplication"]
        and row["requires_actionability_revalidation"]
    ]
    return {
        "task_id": TASK_ID,
        "equivalent_reference_contract_found": bool(equivalent),
        "equivalent_reference_contracts": equivalent,
        "candidate_reference_files": candidate_paths,
        "search_scope": ["docs/**/*.md,json,txt", "artifacts/**/*.md,json,txt"],
        "excluded_paths": [str(DOC_PATH), str(ARTIFACT_DIR)],
        "validation_rule": "equivalent contract requires sealed commit/tag, implementation block, matrix duplication block, and actionability revalidation",
    }


def validate_reference_contract(
    contract: dict[str, Any], canonical: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    canonical = canonical or {}
    validators: list[Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]] = [
        validate_sealed_anchor_reference,
        validate_source_anchor_reference,
        validate_prior_admission_audit_reference,
        validate_no_matrix_duplication,
        validate_authorization_guards,
        validate_hyperon_non_adoption,
        validate_claim_ceiling,
        validate_actionability_revalidation_required,
    ]
    return [validator(contract, canonical) for validator in validators]


def validate_sealed_anchor_reference(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if contract.get("sealed_coverage_commit") != SEALED_COVERAGE_COMMIT:
        failures.append("sealed_coverage_commit_missing_or_wrong")
    if contract.get("sealed_coverage_remote_tag") != SEALED_COVERAGE_REMOTE_TAG:
        failures.append("sealed_coverage_remote_tag_missing_or_wrong")
    return _validator_result("validate_sealed_anchor_reference", failures)


def validate_source_anchor_reference(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if contract.get("underlying_source_commit") != UNDERLYING_SOURCE_COMMIT:
        failures.append("underlying_source_commit_missing_or_wrong")
    if contract.get("underlying_source_remote_tag") != UNDERLYING_SOURCE_REMOTE_TAG:
        failures.append("underlying_source_remote_tag_missing_or_wrong")
    return _validator_result("validate_source_anchor_reference", failures)


def validate_prior_admission_audit_reference(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if contract.get("prior_admission_audit_commit") != PRIOR_ADMISSION_AUDIT_COMMIT:
        failures.append("prior_admission_audit_commit_missing_or_wrong")
    status = contract.get("prior_admission_audit_status", "")
    if "reference only" not in status:
        failures.append("prior_admission_audit_not_reference_only")
    if "runtime" not in " ".join(contract.get("prior_admission_audit_does_not_authorize", [])):
        failures.append("prior_admission_runtime_block_missing")
    return _validator_result("validate_prior_admission_audit_reference", failures)


def validate_no_matrix_duplication(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if contract.get("matrix_duplication_allowed") is not False:
        failures.append("matrix_duplication_allowed_not_false")
    for path, value in _walk(contract):
        if (
            isinstance(value, list)
            and len(value) >= 40
            and all(isinstance(item, dict) and "candidate_id" in item for item in value)
        ):
            failures.append(f"copied_matrix_rows_detected:{path}")
    return _validator_result("validate_no_matrix_duplication", failures)


def validate_authorization_guards(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    failures = [
        f"{field}_not_false"
        for field in AUTHORIZATION_FALSE_FIELDS
        if contract.get(field) is not False
    ]
    return _validator_result("validate_authorization_guards", failures)


def validate_hyperon_non_adoption(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "hyperon_adopted": False,
        "hyperon_implementation_authorized": False,
        "hyperon_runtime_authorized": False,
        "hyperon_ego_mainline_dependency": False,
    }
    failures = [f"{field}_not_false" for field, expected in checks.items() if contract.get(field) is not expected]
    return _validator_result("validate_hyperon_non_adoption", failures)


def validate_claim_ceiling(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if contract.get("claim_ceiling_reference") != CLAIM_CEILING:
        failures.append("claim_ceiling_reference_missing_or_wrong")
    forbidden = "\n".join(contract.get("forbidden_downstream_use", []))
    if not contract.get("forbidden_downstream_use"):
        failures.append("forbidden_claim_list_missing")
    for claim in REQUIRED_FORBIDDEN_CLAIMS:
        if claim not in forbidden and claim not in CLAIM_CEILING:
            failures.append(f"forbidden_claim_missing:{claim}")
    return _validator_result("validate_claim_ceiling", failures)


def validate_actionability_revalidation_required(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if contract.get("actionability_revalidation_required") is not True:
        failures.append("actionability_revalidation_required_not_true")
    return _validator_result("validate_actionability_revalidation_required", failures)


def run_ablation_negative_controls(
    contract: dict[str, Any], canonical: dict[str, Any]
) -> dict[str, Any]:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None], str]] = [
        (
            "implementation_authorized_true",
            lambda data: data.__setitem__("implementation_authorized", True),
            "validate_authorization_guards",
        ),
        (
            "runtime_authorized_true",
            lambda data: data.__setitem__("runtime_authorized", True),
            "validate_authorization_guards",
        ),
        (
            "hyperon_adopted_true",
            lambda data: data.__setitem__("hyperon_adopted", True),
            "validate_hyperon_non_adoption",
        ),
        (
            "sealed_coverage_commit_removed",
            lambda data: data.pop("sealed_coverage_commit", None),
            "validate_sealed_anchor_reference",
        ),
        (
            "sealed_remote_tag_removed",
            lambda data: data.pop("sealed_coverage_remote_tag", None),
            "validate_sealed_anchor_reference",
        ),
        (
            "matrix_duplication_allowed_true",
            lambda data: data.__setitem__("matrix_duplication_allowed", True),
            "validate_no_matrix_duplication",
        ),
        (
            "actionability_revalidation_removed",
            lambda data: data.pop("actionability_revalidation_required", None),
            "validate_actionability_revalidation_required",
        ),
        (
            "forbidden_claim_list_removed",
            lambda data: data.__setitem__("forbidden_downstream_use", []),
            "validate_claim_ceiling",
        ),
    ]
    rows = []
    for mutation_id, mutate, expected_validator in mutations:
        mutated = copy.deepcopy(contract)
        mutate(mutated)
        results = validate_reference_contract(mutated, canonical)
        failing_validators = [row["validator"] for row in results if not row["passed"]]
        rows.append(
            {
                "mutation_id": mutation_id,
                "expected_validator": expected_validator,
                "validation_failed": expected_validator in failing_validators,
                "failing_validators": failing_validators,
                "producer_function": "run_ablation_negative_controls",
                "validation_rule": "mutated invalid contract must fail through callable validators",
            }
        )
    return {
        "task_id": TASK_ID,
        "negative_controls": rows,
        "all_negative_controls_failed": all(row["validation_failed"] for row in rows),
        "aggregation_rule": "each declared mutation must trigger its expected validator failure",
        "validation_rule": "negative controls must fail, not pass as clean reports",
    }


def _load_canonical_inputs(root: Path) -> dict[str, Any]:
    return {
        "matrix": _read_json(root / CANONICAL_DIR / "canonical_theory_coverage_matrix.json"),
        "hyperon_guard": _read_json(root / CANONICAL_DIR / "hyperon_non_adoption_guard.json"),
        "admission_guard": _read_json(root / CANONICAL_DIR / "admission_reference_guard.json"),
        "canonicalization_provenance": _read_json(root / CANONICAL_DIR / "canonicalization_provenance.json"),
        "repair_result": _read_json(root / REPAIR_DIR / "result.json"),
        "prior_admission_result": _read_json(root / PRIOR_ADMISSION_DIR / "result.json"),
    }


def _verify_anchor(
    root: Path, boundary: str, expected_commit: str, tag: str, verify_remote: bool
) -> dict[str, Any]:
    local_ok, local_hash = _git(root, ["rev-parse", expected_commit])
    tag_ok, tag_hash = _git(root, ["rev-parse", tag])
    remote_hash = ""
    remote_ok = not verify_remote
    if verify_remote:
        remote_status, remote_out = _git(root, ["ls-remote", "origin", f"refs/tags/{tag}"])
        remote_hash = remote_out.split()[0] if remote_out else ""
        remote_ok = remote_status and remote_hash == expected_commit
    return {
        "boundary": boundary,
        "expected_commit": expected_commit,
        "remote_tag": tag,
        "local_commit_hash": local_hash,
        "local_commit_verified": local_ok and local_hash == expected_commit,
        "local_tag_hash": tag_hash,
        "local_tag_verified": tag_ok and tag_hash == expected_commit,
        "remote_hash": remote_hash,
        "remote_verified": remote_ok,
        "remote_verification_skipped": not verify_remote,
    }


def _blocked_result(existing_reference: dict[str, Any], run_id: str) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "verdict": VERDICT_BLOCKED_EQUIVALENT,
        "run_id": run_id,
        "layer": LAYER,
        "claim_ceiling": CLAIM_CEILING,
        "existing_reference_contract_found": True,
        "existing_reference_contracts": existing_reference["equivalent_reference_contracts"],
        "stop_conditions_triggered": ["equivalent_reference_contract_exists"],
        "what_this_does_not_prove": REQUIRED_FORBIDDEN_CLAIMS,
    }


def _validator_result(name: str, failures: list[str]) -> dict[str, Any]:
    return {
        "validator": name,
        "passed": not failures,
        "failures": failures,
        "producer_function": name,
        "code_path_hash": _code_path_hash(globals()[name]),
        "aggregation_rule": "collect explicit validation failures",
        "validation_rule": "validator passes only with zero failures",
    }


def _with_metadata(
    artifact_name: str,
    payload: dict[str, Any],
    producer: Callable[..., Any],
    input_artifacts: list[str],
    run_id: str,
    aggregation_rule: str,
    validation_rule: str,
) -> dict[str, Any]:
    payload_copy = copy.deepcopy(payload)
    payload_hash = _payload_hash(payload_copy)
    payload_copy["computed_evidence_provenance"] = {
        "artifact_name": artifact_name,
        "producer_function": producer.__name__,
        "input_artifacts": input_artifacts,
        "run_id": run_id,
        "code_path_hash": _code_path_hash(producer),
        "aggregation_rule": aggregation_rule,
        "validation_rule": validation_rule,
        "output_artifact_hash": payload_hash,
        "output_hash_scope": "canonical JSON payload before computed_evidence_provenance envelope",
    }
    return payload_copy


def _contract_inputs() -> list[str]:
    return [
        str(REPAIR_DIR / "result.json"),
        str(REPAIR_DIR / "trace_artifact_provenance_entry.json"),
        str(CANONICAL_DIR / "canonicalization_provenance.json"),
        str(CANONICAL_DIR / "hyperon_non_adoption_guard.json"),
        str(CANONICAL_DIR / "admission_reference_guard.json"),
        str(PRIOR_ADMISSION_DOC),
        str(PRIOR_ADMISSION_DIR / "result.json"),
    ]


def _run_id(root: Path) -> str:
    seed = "|".join(
        [
            TASK_ID,
            SEALED_COVERAGE_COMMIT,
            SEALED_COVERAGE_REMOTE_TAG,
            UNDERLYING_SOURCE_COMMIT,
            PRIOR_ADMISSION_AUDIT_COMMIT,
            _sha_file(root / REPAIR_DIR / "result.json"),
        ]
    )
    return f"ego_mainline_admission_canonical_coverage_reference_001a_{_sha_text(seed)[:16]}"


def _hash_paths(root: Path, paths: list[Path]) -> dict[str, str]:
    return {
        _rel(root / path, root): _sha_file(root / path)
        for path in paths
        if (root / path).exists()
    }


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _payload_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _code_path_hash(func: Callable[..., Any]) -> str:
    return _sha_text(inspect.getsource(func))


def _git(root: Path, args: list[str]) -> tuple[bool, str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    output = (completed.stdout or completed.stderr).strip()
    return completed.returncode == 0, output


def _git_success(root: Path, args: list[str]) -> bool:
    return _git(root, args)[0]


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _walk(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    rows = [(path, value)]
    if isinstance(value, dict):
        for key, item in value.items():
            rows.extend(_walk(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(_walk(item, f"{path}[{index}]"))
    return rows


def _write_doc(
    path: Path,
    result: dict[str, Any],
    contract: dict[str, Any],
    existing_reference: dict[str, Any],
    ablation_report: dict[str, Any],
) -> None:
    text = f"""# {TASK_ID}

## Verdict

`{result["verdict"]}`

This document creates an admission-side reference-only contract for the sealed
canonical theory coverage boundary.

## Layer

{LAYER}

This is not admission execution, EGO mainline work, bridge runtime work,
architecture selection, theory validation, or mechanism validation.

## Sealed Coverage Reference

- Sealed coverage repair commit: `{SEALED_COVERAGE_COMMIT}`
- Sealed coverage repair remote tag: `{SEALED_COVERAGE_REMOTE_TAG}`
- Underlying source commit: `{UNDERLYING_SOURCE_COMMIT}`
- Underlying source remote tag: `{UNDERLYING_SOURCE_REMOTE_TAG}`
- Prior admission audit commit: `{PRIOR_ADMISSION_AUDIT_COMMIT}`
- Prior admission audit status: {PRIOR_ADMISSION_AUDIT_STATUS}

## Existing Reference Search

Equivalent reference contract found: `{str(existing_reference["equivalent_reference_contract_found"]).lower()}`.

If a future contract is found that already records the sealed commit and tag,
blocks implementation authorization, blocks matrix duplication, and requires
actionability revalidation, this task must not create a duplicate schema.

## Allowed Downstream Use

{_bullets(contract["allowed_downstream_use"])}

## Forbidden Downstream Use

{_bullets(contract["forbidden_downstream_use"])}

## Authorization Guard

- implementation_authorized: `{str(contract["implementation_authorized"]).lower()}`
- runtime_authorized: `{str(contract["runtime_authorized"]).lower()}`
- bridge_authorized: `{str(contract["bridge_authorized"]).lower()}`
- companion_authorized: `{str(contract["companion_authorized"]).lower()}`
- architecture_adopted: `{str(contract["architecture_adopted"]).lower()}`
- hyperon_adopted: `{str(contract["hyperon_adopted"]).lower()}`
- actionability_revalidation_required: `{str(contract["actionability_revalidation_required"]).lower()}`
- matrix_duplication_allowed: `{str(contract["matrix_duplication_allowed"]).lower()}`

The 45-row canonical matrix is referenced by path/hash boundary only and is not
copied into this contract.

## Negative Controls

All required mutated-input negative controls failed through callable validators:
`{str(ablation_report["all_negative_controls_failed"]).lower()}`.

## Claim Ceiling

{CLAIM_CEILING}

## What This Does Not Prove

{_bullets(REQUIRED_FORBIDDEN_CLAIMS)}
"""
    _write_text(path, text)


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--skip-remote", action="store_true")
    args = parser.parse_args()
    result = run_reference_contract(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        verify_remote=not args.skip_remote,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
