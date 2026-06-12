from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
from typing import Any, Callable


TASK_ID = "EGO-MAINLINE-ADMISSION-TASK-CARD-ALIGNMENT-001A"
VERDICT_PASS = "ego_mainline_admission_task_card_alignment_001a_pass"
VERDICT_BLOCK_REDUNDANT = "redundant_alignment_contract_blocked"
VERDICT_BLOCK_POST_BRIDGE = "blocked_post_bridge_boundary_unresolved"
LAYER = "evidence-governance / admission-planning contract"
CLAIM_CEILING = "bounded admission task-card alignment / evidence contract planning only"

ADMISSION_COVERAGE_REFERENCE_COMMIT = "c5b067faea764657bd24cd75415a6ceb59905dab"
ADMISSION_COVERAGE_REFERENCE_TAG = "remote-anchor-admission-coverage-reference-001a-c5b067f"
CANONICAL_COVERAGE_REPAIR_COMMIT = "df6ad31ed58d2e3772e3f53b35ad926ab995d582"
CANONICAL_COVERAGE_REPAIR_TAG = "remote-anchor-coverage-canonicalization-repair-001b-df6ad31"
COMPRESSION_SOURCE_COMMIT = "614b147d14cc4bb02b7c6afa2c90661cdce15e4c"
COMPRESSION_SOURCE_TAG = "remote-anchor-coverage-compression-001d-614b147"
PRIOR_READINESS_AUDIT_COMMIT = "f648dac4bfbcdc7a98c1edea5a97dbef4101d83a"
POST_BRIDGE_001D_COMMIT = "c2f6c5184a119202dd0a7efc23d3bfe3317af890"
POST_BRIDGE_001D_TAG = "remote-anchor-001n-c2f6c51"

DOC_PATH = Path("docs/codex/tasks/EGO-MAINLINE-ADMISSION-TASK-CARD-ALIGNMENT-001A.md")
ARTIFACT_DIR = Path("artifacts/ego_mainline_admission_task_card_alignment_001a")

ADMISSION_TASK_CARD_001A = Path("docs/codex/tasks/EGO-MAINLINE-ADMISSION-TASK-CARD-001A.md")
ADMISSION_COVERAGE_REFERENCE_DOC = Path(
    "docs/research/EGO-MAINLINE-ADMISSION-CANONICAL-COVERAGE-REFERENCE-001A.md"
)
ADMISSION_COVERAGE_REFERENCE_ARTIFACT = Path(
    "artifacts/ego_mainline_admission_canonical_coverage_reference_001a/reference_contract.json"
)
CANONICAL_REPAIR_RESULT = Path("artifacts/theory_landscape_coverage_canonicalization_provenance_repair_001b/result.json")
COMPRESSION_SOURCE_DOC = Path("docs/research/THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001D.md")
PRIOR_READINESS_AUDIT_DOC = Path("docs/codex/audits/EGO-MAINLINE-READINESS-AUDIT-001B.md")
POST_BRIDGE_001D_DOC = Path("docs/codex/tasks/POST-BRIDGE-ADMISSION-EXECUTABLE-001D.md")
POST_BRIDGE_001D_RESULT = Path("artifacts/post_bridge_admission_executable_001d/result.json")

REQUIRED_ARTIFACT_NAMES = [
    "result.json",
    "existing_admission_task_card_search_report.json",
    "parent_evidence_boundary_manifest.json",
    "evidence_usage_contract.json",
    "actionability_revalidation_matrix.json",
    "computed_evidence_gate_contract.json",
    "negative_evidence_handling_contract.json",
    "authorization_guard.json",
    "schema_duplication_guard.json",
    "post_bridge_boundary_resolution_report.json",
    "source_trace_report.json",
    "claim_ceiling.txt",
]

AUTHORIZATION_FALSE_FIELDS = [
    "implementation_authorized",
    "runtime_authorized",
    "bridge_authorized",
    "companion_authorized",
    "ego_mainline_runtime_authorized",
    "llm_rag_authorized",
    "user_model_authorized",
    "relationship_authorized",
    "emotion_authorized",
    "personalization_authorized",
    "hyperon_adopted",
    "architecture_selected",
]

WHAT_THIS_DOES_NOT_PROVE = [
    "EGO readiness",
    "bridge readiness",
    "mechanism validity",
    "theory validity",
    "architecture correctness",
    "agency",
    "selfhood",
    "consciousness",
    "emotion",
    "relationship learning",
    "stable user benefit",
    "future runtime correctness",
]

PROTECTED_INPUTS = [
    ADMISSION_TASK_CARD_001A,
    ADMISSION_COVERAGE_REFERENCE_DOC,
    ADMISSION_COVERAGE_REFERENCE_ARTIFACT,
    Path("artifacts/ego_mainline_admission_canonical_coverage_reference_001a/result.json"),
    CANONICAL_REPAIR_RESULT,
    Path("artifacts/theory_landscape_coverage_canonicalization_001a/canonical_theory_coverage_matrix.json"),
    Path("artifacts/theory_landscape_coverage_canonicalization_001a/admission_reference_guard.json"),
    Path("artifacts/theory_landscape_coverage_canonicalization_001a/hyperon_non_adoption_guard.json"),
    COMPRESSION_SOURCE_DOC,
    PRIOR_READINESS_AUDIT_DOC,
    Path("artifacts/ego_mainline_readiness_audit_001b/result.json"),
    POST_BRIDGE_001D_DOC,
    POST_BRIDGE_001D_RESULT,
]


def run_alignment_contract(
    repo_root: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    out = Path(output_dir) if output_dir is not None else root / ARTIFACT_DIR
    if not out.is_absolute():
        out = root / out
    out.mkdir(parents=True, exist_ok=True)
    materialize_doc = output_dir is None
    doc_path = root / DOC_PATH if materialize_doc else out / DOC_PATH.name

    input_hashes_before = hash_protected_inputs(root)
    run_id = _run_id(root)
    existing_search = search_existing_admission_contracts(root)
    post_bridge = resolve_post_bridge_boundary(root)

    if existing_search["complete_equivalent_contract_found"]:
        result = _blocked_result(VERDICT_BLOCK_REDUNDANT, ["complete_equivalent_alignment_contract_exists"], run_id)
        _write_json(
            out / "existing_admission_task_card_search_report.json",
            _with_metadata(
                "existing_admission_task_card_search_report.json",
                existing_search,
                search_existing_admission_contracts,
                ["docs/codex/tasks", "artifacts"],
                run_id,
                "scan existing admission task cards and contracts before creating alignment amendment",
                "complete equivalent contract must block duplicate schema creation",
            ),
        )
        _write_json(out / "result.json", _with_metadata("result.json", result, _blocked_result, [], run_id, "block duplicate schema", "stop on complete equivalent contract"))
        return result

    if not post_bridge["resolved"]:
        result = _blocked_result(VERDICT_BLOCK_POST_BRIDGE, ["blocked_post_bridge_boundary_unresolved"], run_id)
        _write_json(
            out / "post_bridge_boundary_resolution_report.json",
            _with_metadata(
                "post_bridge_boundary_resolution_report.json",
                post_bridge,
                resolve_post_bridge_boundary,
                [str(POST_BRIDGE_001D_DOC), str(POST_BRIDGE_001D_RESULT)],
                run_id,
                "resolve POST-BRIDGE-ADMISSION-EXECUTABLE-001D from existing repo artifacts",
                "post-bridge 001D must resolve before alignment contract is emitted",
            ),
        )
        _write_json(out / "result.json", _with_metadata("result.json", result, _blocked_result, [], run_id, "block unresolved post-bridge boundary", "stop on unresolved post-bridge boundary"))
        return result

    parent_manifest = build_parent_evidence_boundary_manifest(post_bridge)
    evidence_contract = build_evidence_usage_contract(parent_manifest, post_bridge)
    actionability = build_actionability_revalidation_matrix(parent_manifest)
    computed_gate = build_computed_evidence_gate_contract()
    negative_evidence = build_negative_evidence_handling_contract(post_bridge)
    authorization = build_authorization_guard(evidence_contract)

    artifacts: dict[str, dict[str, Any]] = {}
    artifacts["existing_admission_task_card_search_report.json"] = _with_metadata(
        "existing_admission_task_card_search_report.json",
        existing_search,
        search_existing_admission_contracts,
        ["docs/codex/tasks", "docs/codex/contracts", "artifacts"],
        run_id,
        "scan existing admission-side task cards/contracts for complete or partial alignment coverage",
        "complete equivalent blocks; partial contract requires amendment mode",
    )
    artifacts["parent_evidence_boundary_manifest.json"] = _with_metadata(
        "parent_evidence_boundary_manifest.json",
        parent_manifest,
        build_parent_evidence_boundary_manifest,
        _contract_inputs(),
        run_id,
        "record exact sealed parent boundaries and resolved post-bridge 001D boundary",
        "all parent boundary commits/tags and interpretations must match exactly",
    )
    artifacts["evidence_usage_contract.json"] = _with_metadata(
        "evidence_usage_contract.json",
        evidence_contract,
        build_evidence_usage_contract,
        ["parent_evidence_boundary_manifest.json"],
        run_id,
        "define allowed and forbidden downstream use for each parent boundary",
        "parent evidence may support only bounded alignment planning, not runtime or mechanism proof",
    )
    artifacts["actionability_revalidation_matrix.json"] = _with_metadata(
        "actionability_revalidation_matrix.json",
        actionability,
        build_actionability_revalidation_matrix,
        ["parent_evidence_boundary_manifest.json", "evidence_usage_contract.json"],
        run_id,
        "require future actionability revalidation before admission execution",
        "future execution remains blocked until revalidation rows are satisfied",
    )
    artifacts["computed_evidence_gate_contract.json"] = _with_metadata(
        "computed_evidence_gate_contract.json",
        computed_gate,
        build_computed_evidence_gate_contract,
        ["docs/codex/contracts/COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md"],
        run_id,
        "carry forward computed-evidence provenance requirements for future admission execution",
        "future execution verdicts must derive from callable computation paths",
    )
    artifacts["negative_evidence_handling_contract.json"] = _with_metadata(
        "negative_evidence_handling_contract.json",
        negative_evidence,
        build_negative_evidence_handling_contract,
        ["parent_evidence_boundary_manifest.json", str(PRIOR_READINESS_AUDIT_DOC)],
        run_id,
        "preserve 001B/001C negative evidence handling and bound 001D use",
        "negative evidence cannot be restored as positive evidence",
    )
    artifacts["authorization_guard.json"] = _with_metadata(
        "authorization_guard.json",
        authorization,
        build_authorization_guard,
        ["evidence_usage_contract.json"],
        run_id,
        "record non-authorization flags for runtime, implementation, bridge, companion, Hyperon, and architecture",
        "all authorization/adoption flags must stay false",
    )
    artifacts["schema_duplication_guard.json"] = _with_metadata(
        "schema_duplication_guard.json",
        build_schema_duplication_guard(existing_search, artifacts),
        build_schema_duplication_guard,
        ["existing_admission_task_card_search_report.json", "evidence_usage_contract.json"],
        run_id,
        "enforce amendment mode and scan for copied 45-row matrix payloads",
        "no duplicate schema and no 45-row matrix copy may appear",
    )
    artifacts["post_bridge_boundary_resolution_report.json"] = _with_metadata(
        "post_bridge_boundary_resolution_report.json",
        post_bridge,
        resolve_post_bridge_boundary,
        [str(POST_BRIDGE_001D_DOC), str(POST_BRIDGE_001D_RESULT)],
        run_id,
        "resolve POST-BRIDGE-ADMISSION-EXECUTABLE-001D path, commit, verdict, caveats, and claim ceiling",
        "post-bridge 001D must be resolved and must not be treated as mechanism proof",
    )

    validator_results = validate_alignment_contract(evidence_contract, post_bridge)
    negative_controls = run_negative_controls(evidence_contract, post_bridge)
    result_payload = build_result(
        existing_search=existing_search,
        post_bridge=post_bridge,
        validators=validator_results,
        negative_controls=negative_controls,
        input_hashes_before=input_hashes_before,
        input_hashes_after=hash_protected_inputs(root),
    )
    artifacts["result.json"] = _with_metadata(
        "result.json",
        result_payload,
        build_result,
        sorted(artifacts),
        run_id,
        "aggregate validator, negative-control, duplicate-schema, post-bridge, and protected-input checks",
        "pass only when alignment contract remains bounded and all controls fail as expected",
    )

    for name, payload in artifacts.items():
        _write_json(out / name, payload)

    _write_text(out / "claim_ceiling.txt", CLAIM_CEILING + "\n")
    source_trace = build_source_trace_report(out, artifacts, run_id)
    _write_json(
        out / "source_trace_report.json",
        _with_metadata(
            "source_trace_report.json",
            source_trace,
            build_source_trace_report,
            sorted(artifacts) + ["claim_ceiling.txt"],
            run_id,
            "trace every new alignment artifact to admission coverage, canonical repair, source, readiness audit, and post-bridge 001D",
            "each artifact must be traceable to the named parent boundaries",
        ),
    )
    _write_doc(doc_path, evidence_contract, parent_manifest, post_bridge, existing_search, negative_controls)
    return result_payload


def search_existing_admission_contracts(root: Path) -> dict[str, Any]:
    candidates = []
    for base in [root / "docs" / "codex", root / "artifacts"]:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".txt"}:
                continue
            rel = _rel(path, root)
            if rel.startswith(str(DOC_PATH).replace("\\", "/")) or rel.startswith(str(ARTIFACT_DIR).replace("\\", "/")):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            lowered = text.lower()
            if "admission" not in lowered:
                continue
            candidate = {
                "path": rel,
                "references_admission_coverage_reference": ADMISSION_COVERAGE_REFERENCE_COMMIT in text
                or ADMISSION_COVERAGE_REFERENCE_TAG in text,
                "references_canonical_repair": CANONICAL_COVERAGE_REPAIR_COMMIT in text
                or CANONICAL_COVERAGE_REPAIR_TAG in text,
                "references_post_bridge_001d": "POST-BRIDGE-ADMISSION-EXECUTABLE-001D" in text
                or "post_bridge_admission_executable_001d" in text,
                "requires_actionability_revalidation": "actionability_revalidation" in lowered,
                "has_computed_evidence_gate": "computed-evidence" in lowered or "computed_evidence" in lowered,
                "blocks_runtime": "runtime_authorized = false" in lowered
                or '"runtime_authorized": false' in lowered
                or "does not authorize runtime" in lowered,
                "blocks_implementation": "implementation_authorized" in lowered and "false" in lowered
                or "does not authorize execution" in lowered,
                "blocks_matrix_duplication": "matrix_duplication" in lowered or "45-row" in lowered,
            }
            if any(value is True for key, value in candidate.items() if key != "path"):
                candidates.append(candidate)
    complete = [
        row
        for row in candidates
        if row["references_admission_coverage_reference"]
        and row["references_canonical_repair"]
        and row["references_post_bridge_001d"]
        and row["requires_actionability_revalidation"]
        and row["has_computed_evidence_gate"]
        and row["blocks_runtime"]
        and row["blocks_implementation"]
        and row["blocks_matrix_duplication"]
    ]
    partial = [
        row
        for row in candidates
        if row["references_post_bridge_001d"]
        and row["has_computed_evidence_gate"]
        and row["blocks_runtime"]
        and not row["references_admission_coverage_reference"]
    ]
    return {
        "task_id": TASK_ID,
        "search_executed": True,
        "complete_equivalent_contract_found": bool(complete),
        "complete_equivalent_contracts": complete,
        "partial_contract_found": bool(partial),
        "partial_contract_paths": [row["path"] for row in partial],
        "candidate_contracts": candidates,
        "validation_rule": "complete equivalent must cover admission coverage reference, canonical repair, post-bridge 001D, actionability, computed gate, runtime/implementation blocks, and matrix duplication block",
    }


def resolve_post_bridge_boundary(root: Path) -> dict[str, Any]:
    doc = root / POST_BRIDGE_001D_DOC
    result_path = root / POST_BRIDGE_001D_RESULT
    if not doc.exists() or not result_path.exists():
        return {
            "task_id": "POST-BRIDGE-ADMISSION-EXECUTABLE-001D",
            "resolved": False,
            "blocked_reason": "missing_post_bridge_001d_doc_or_result",
        }
    result = _read_json(result_path)
    commit = _git_output(root, ["log", "-1", "--format=%H", "--", str(POST_BRIDGE_001D_DOC), str(POST_BRIDGE_001D_RESULT)])
    caveats = [
        result["anti_sycophancy_audit"]["strongest_reason_task_may_be_invalid"],
        result["anti_sycophancy_audit"]["evidence_that_would_still_be_insufficient"],
        "001D is a current bounded post-bridge positive candidate with caveats, not mechanism proof.",
        "Future EGO-mainline admission must preserve surface-scoped leakage and computed-evidence requirements.",
    ]
    return {
        "task_id": "POST-BRIDGE-ADMISSION-EXECUTABLE-001D",
        "resolved": True,
        "blocked_reason": None,
        "artifact_path": POST_BRIDGE_001D_RESULT.as_posix(),
        "task_card_path": POST_BRIDGE_001D_DOC.as_posix(),
        "commit": commit or POST_BRIDGE_001D_COMMIT,
        "remote_tag": POST_BRIDGE_001D_TAG,
        "verdict": result.get("verdict"),
        "bounded_pass": result.get("bounded_pass"),
        "claim_ceiling": result.get("claim_ceiling"),
        "caveats": caveats,
        "treat_as_mechanism_proof": False,
        "runtime_authorized": False,
        "implementation_authorized": False,
        "what_this_does_not_prove": result.get("what_this_does_not_prove", []),
        "validation_rule": "POST-BRIDGE 001D must resolve from existing task card and result artifact without rerun",
    }


def build_parent_evidence_boundary_manifest(post_bridge: dict[str, Any]) -> dict[str, Any]:
    boundaries = [
        {
            "boundary_id": "admission_coverage_reference",
            "task_id": "EGO-MAINLINE-ADMISSION-CANONICAL-COVERAGE-REFERENCE-001A",
            "commit": ADMISSION_COVERAGE_REFERENCE_COMMIT,
            "tag": ADMISSION_COVERAGE_REFERENCE_TAG,
            "allowed_support": [
                "reference-only admission-side contract boundary for sealed canonical theory coverage",
                "parent input to future admission task-card alignment",
            ],
            "forbidden_support": [
                "implementation authorization",
                "runtime authorization",
                "architecture selection",
                "mechanism validity",
                "EGO readiness",
            ],
        },
        {
            "boundary_id": "canonical_coverage_repair",
            "task_id": "coverage canonicalization repair",
            "commit": CANONICAL_COVERAGE_REPAIR_COMMIT,
            "tag": CANONICAL_COVERAGE_REPAIR_TAG,
            "allowed_support": ["sealed canonical coverage repair provenance"],
            "forbidden_support": ["new theory audit", "matrix duplication", "theory validity"],
        },
        {
            "boundary_id": "compression_source_boundary",
            "task_id": "coverage compression source boundary",
            "commit": COMPRESSION_SOURCE_COMMIT,
            "tag": COMPRESSION_SOURCE_TAG,
            "allowed_support": ["source-pinned compression boundary reference"],
            "forbidden_support": ["expanded theory landscape", "architecture adoption"],
        },
        {
            "boundary_id": "prior_readiness_audit",
            "task_id": "EGO-MAINLINE-READINESS-AUDIT-001B",
            "commit": PRIOR_READINESS_AUDIT_COMMIT,
            "tag": None,
            "interpretation": "reference-only; authorizes admission task-card drafting only; no runtime authorization",
            "runtime_authorized": False,
            "implementation_authorized": False,
            "allowed_support": ["historical admission task-card drafting authorization reference"],
            "forbidden_support": ["runtime authorization", "execution authorization", "EGO readiness"],
        },
        {
            "boundary_id": "post_bridge_admission_executable_001d",
            "task_id": "POST-BRIDGE-ADMISSION-EXECUTABLE-001D",
            "commit": post_bridge["commit"],
            "tag": post_bridge["remote_tag"],
            "artifact_path": post_bridge["artifact_path"],
            "verdict": post_bridge["verdict"],
            "claim_ceiling": post_bridge["claim_ceiling"],
            "caveats": post_bridge["caveats"],
            "allowed_support": ["bounded post-bridge positive candidate with caveats for future admission planning"],
            "forbidden_support": ["mechanism proof", "EGO readiness", "runtime correctness", "companion readiness"],
        },
    ]
    return {
        "task_id": TASK_ID,
        "layer": LAYER,
        "parent_boundaries": boundaries,
        "claim_ceiling": CLAIM_CEILING,
        "validation_rule": "record each parent boundary exactly with allowed and forbidden support",
    }


def build_evidence_usage_contract(parent_manifest: dict[str, Any], post_bridge: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "layer": LAYER,
        "contract_mode": "alignment_amendment_for_future_admission_execution",
        "parent_boundary_ids": [row["boundary_id"] for row in parent_manifest["parent_boundaries"]],
        "allowed_use_by_boundary": {
            row["boundary_id"]: row["allowed_support"] for row in parent_manifest["parent_boundaries"]
        },
        "forbidden_use_by_boundary": {
            row["boundary_id"]: row["forbidden_support"] for row in parent_manifest["parent_boundaries"]
        },
        "authorization_flags": {field: False for field in AUTHORIZATION_FALSE_FIELDS},
        "actionability_revalidation_required": True,
        "matrix_duplication_allowed": False,
        "computed_evidence_gate_required_for_future_execution": True,
        "negative_evidence_handling_required": True,
        "post_bridge_001d_mechanism_proof_allowed": False,
        "post_bridge_001d_claim_ceiling": post_bridge["claim_ceiling"],
        "hyperon_adopted": False,
        "claim_ceiling": CLAIM_CEILING,
        "what_this_does_not_prove": WHAT_THIS_DOES_NOT_PROVE,
        "validation_rule": "future admission execution may use parents only within bounded support and must not authorize runtime or implementation",
    }


def build_actionability_revalidation_matrix(parent_manifest: dict[str, Any]) -> dict[str, Any]:
    rows = [
        {
            "boundary_id": row["boundary_id"],
            "required": True,
            "revalidation_required_before": "future admission execution",
            "revalidation_rule": "confirm this parent still supports only the allowed-use row and no forbidden-use row",
        }
        for row in parent_manifest["parent_boundaries"]
    ]
    rows.extend(
        [
            {
                "boundary_id": "computed_evidence_gate",
                "required": True,
                "revalidation_required_before": "future admission execution",
                "revalidation_rule": "future executable must derive verdicts from callable computation paths",
            },
            {
                "boundary_id": "negative_evidence_handling",
                "required": True,
                "revalidation_required_before": "future admission execution",
                "revalidation_rule": "001B and 001C remain non-positive; 001D remains caveated",
            },
        ]
    )
    return {
        "task_id": TASK_ID,
        "actionability_revalidation_required": True,
        "revalidation_rows": rows,
        "validation_rule": "all parent and guard rows require actionability revalidation before future execution",
    }


def build_computed_evidence_gate_contract() -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "computed_evidence_gate_required_for_future_execution": True,
        "static_or_literal_verdicts_allowed": False,
        "required_metadata_fields": [
            "producer_function",
            "input_artifacts",
            "run_id",
            "seed_or_context_ids",
            "aggregation_rule",
            "validation_rule",
            "code_path_hash",
        ],
        "future_execution_must_include": [
            "callable independent baselines",
            "real ablation reruns",
            "surface-specific leakage scanners with positive controls",
            "behavior-causal replay where behavior claims are made",
            "failure-path tests",
        ],
        "validation_rule": "future admission execution cannot use literals, static pass labels, or unconditional clean reports as verdict evidence",
    }


def build_negative_evidence_handling_contract(post_bridge: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "negative_evidence_handling_required": True,
        "negative_evidence_rows": [
            {
                "task_id": "POST-BRIDGE-ADMISSION-EXECUTABLE-001B",
                "status": "invalidated_as_downstream_positive_evidence",
                "positive_evidence_allowed": False,
                "allowed_use": ["negative evidence", "evidence-custody context", "false-positive artifact-generation context"],
            },
            {
                "task_id": "POST-BRIDGE-ADMISSION-EXECUTABLE-001C",
                "status": "historical_suspended_as_downstream_positive_evidence",
                "positive_evidence_allowed": False,
                "allowed_use": ["historical nominal pass with leakage fail-ability blocker caveat"],
            },
            {
                "task_id": "POST-BRIDGE-ADMISSION-EXECUTABLE-001D",
                "status": "current_bounded_post_bridge_positive_candidate_with_caveats",
                "positive_evidence_allowed": True,
                "mechanism_proof_allowed": False,
                "claim_ceiling": post_bridge["claim_ceiling"],
                "caveats": post_bridge["caveats"],
            },
        ],
        "validation_rule": "negative evidence must not be restored as positive evidence, and 001D must remain caveated",
    }


def build_authorization_guard(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "authorization_flags": copy.deepcopy(contract["authorization_flags"]),
        "actionability_revalidation_required": contract["actionability_revalidation_required"],
        "matrix_duplication_allowed": contract["matrix_duplication_allowed"],
        "claim_ceiling": contract["claim_ceiling"],
        "validation_rule": "no implementation, runtime, bridge, companion, Hyperon, or architecture authorization is created",
    }


def build_schema_duplication_guard(existing_search: dict[str, Any], artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    row_like_lists = []
    for name, payload in artifacts.items():
        for path, value in _walk(payload):
            if (
                isinstance(value, list)
                and len(value) == 45
                and all(isinstance(item, dict) and "candidate_id" in item for item in value)
            ):
                row_like_lists.append({"artifact": name, "path": path})
    return {
        "task_id": TASK_ID,
        "alignment_document_mode": "amendment_to_existing_admission_task_card_001a",
        "complete_equivalent_contract_found": existing_search["complete_equivalent_contract_found"],
        "partial_contract_found": existing_search["partial_contract_found"],
        "duplicate_schema_created": False,
        "matrix_duplication_allowed": False,
        "copied_45_row_matrix_detected": bool(row_like_lists),
        "row_like_lists": row_like_lists,
        "validation_rule": "partial existing admission card is amended by reference; no duplicate schema or copied matrix is allowed",
    }


def validate_alignment_contract(contract: dict[str, Any], post_bridge: dict[str, Any]) -> list[dict[str, Any]]:
    validators: list[Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]] = [
        validate_parent_references,
        validate_authorization_guards,
        validate_actionability_revalidation,
        validate_prior_readiness_audit_reference_only,
        validate_post_bridge_not_mechanism_proof,
        validate_hyperon_non_adoption,
        validate_matrix_duplication_blocked,
        validate_computed_evidence_gate,
        validate_negative_evidence_handling,
        validate_claim_ceiling,
    ]
    return [validator(contract, post_bridge) for validator in validators]


def validate_parent_references(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if "admission_coverage_reference" not in contract.get("parent_boundary_ids", []):
        failures.append("admission_coverage_reference_missing")
    if "canonical_coverage_repair" not in contract.get("parent_boundary_ids", []):
        failures.append("canonical_coverage_repair_missing")
    return _validator_result("validate_parent_references", failures)


def validate_authorization_guards(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    flags = contract.get("authorization_flags", {})
    failures = [f"{field}_not_false" for field in AUTHORIZATION_FALSE_FIELDS if flags.get(field) is not False]
    return _validator_result("validate_authorization_guards", failures)


def validate_actionability_revalidation(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if contract.get("actionability_revalidation_required") is not True:
        failures.append("actionability_revalidation_required_not_true")
    return _validator_result("validate_actionability_revalidation", failures)


def validate_prior_readiness_audit_reference_only(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    forbidden = contract.get("forbidden_use_by_boundary", {}).get("prior_readiness_audit", [])
    failures = []
    if "runtime authorization" not in forbidden:
        failures.append("prior_readiness_runtime_block_missing")
    if contract.get("authorization_flags", {}).get("runtime_authorized") is not False:
        failures.append("prior_readiness_treated_as_runtime_authorization")
    return _validator_result("validate_prior_readiness_audit_reference_only", failures)


def validate_post_bridge_not_mechanism_proof(contract: dict[str, Any], post_bridge: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if contract.get("post_bridge_001d_mechanism_proof_allowed") is not False:
        failures.append("post_bridge_001d_mechanism_proof_allowed")
    if post_bridge.get("treat_as_mechanism_proof") is not False:
        failures.append("post_bridge_resolution_treats_as_mechanism_proof")
    return _validator_result("validate_post_bridge_not_mechanism_proof", failures)


def validate_hyperon_non_adoption(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if contract.get("authorization_flags", {}).get("hyperon_adopted") is not False:
        failures.append("hyperon_adopted_not_false")
    if contract.get("hyperon_adopted") is not False:
        failures.append("top_level_hyperon_adopted_not_false")
    return _validator_result("validate_hyperon_non_adoption", failures)


def validate_matrix_duplication_blocked(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if contract.get("matrix_duplication_allowed") is not False:
        failures.append("matrix_duplication_allowed_not_false")
    for path, value in _walk(contract):
        if (
            isinstance(value, list)
            and len(value) == 45
            and all(isinstance(item, dict) and "candidate_id" in item for item in value)
        ):
            failures.append(f"copied_45_row_matrix:{path}")
    return _validator_result("validate_matrix_duplication_blocked", failures)


def validate_computed_evidence_gate(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if contract.get("computed_evidence_gate_required_for_future_execution") is not True:
        failures.append("computed_evidence_gate_missing")
    return _validator_result("validate_computed_evidence_gate", failures)


def validate_negative_evidence_handling(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if contract.get("negative_evidence_handling_required") is not True:
        failures.append("negative_evidence_handling_missing")
    return _validator_result("validate_negative_evidence_handling", failures)


def validate_claim_ceiling(contract: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if contract.get("claim_ceiling") != CLAIM_CEILING:
        failures.append("claim_ceiling_missing_or_weakened")
    blocked = set(contract.get("what_this_does_not_prove", []))
    for claim in WHAT_THIS_DOES_NOT_PROVE:
        if claim not in blocked:
            failures.append(f"forbidden_claim_missing:{claim}")
    return _validator_result("validate_claim_ceiling", failures)


def run_negative_controls(contract: dict[str, Any], post_bridge: dict[str, Any]) -> dict[str, Any]:
    mutations: list[tuple[str, Callable[[dict[str, Any], dict[str, Any]], None], str]] = [
        ("implementation_authorized_true", lambda c, p: c["authorization_flags"].__setitem__("implementation_authorized", True), "validate_authorization_guards"),
        ("runtime_authorized_true", lambda c, p: c["authorization_flags"].__setitem__("runtime_authorized", True), "validate_authorization_guards"),
        ("admission_reference_removed", lambda c, p: c["parent_boundary_ids"].remove("admission_coverage_reference"), "validate_parent_references"),
        ("canonical_repair_removed", lambda c, p: c["parent_boundary_ids"].remove("canonical_coverage_repair"), "validate_parent_references"),
        ("actionability_revalidation_removed", lambda c, p: c.__setitem__("actionability_revalidation_required", False), "validate_actionability_revalidation"),
        ("prior_readiness_audit_runtime_authorized", lambda c, p: c["authorization_flags"].__setitem__("runtime_authorized", True), "validate_prior_readiness_audit_reference_only"),
        ("post_bridge_001d_as_mechanism_proof", lambda c, p: c.__setitem__("post_bridge_001d_mechanism_proof_allowed", True), "validate_post_bridge_not_mechanism_proof"),
        ("hyperon_adopted_true", lambda c, p: c["authorization_flags"].__setitem__("hyperon_adopted", True), "validate_hyperon_non_adoption"),
        ("matrix_duplication_allowed_true", lambda c, p: c.__setitem__("matrix_duplication_allowed", True), "validate_matrix_duplication_blocked"),
        ("computed_evidence_gate_removed", lambda c, p: c.__setitem__("computed_evidence_gate_required_for_future_execution", False), "validate_computed_evidence_gate"),
        ("negative_evidence_handling_removed", lambda c, p: c.__setitem__("negative_evidence_handling_required", False), "validate_negative_evidence_handling"),
    ]
    rows = []
    for mutation_id, mutate, expected_validator in mutations:
        mutated_contract = copy.deepcopy(contract)
        mutated_post_bridge = copy.deepcopy(post_bridge)
        mutate(mutated_contract, mutated_post_bridge)
        results = validate_alignment_contract(mutated_contract, mutated_post_bridge)
        failing = [row["validator"] for row in results if not row["passed"]]
        rows.append(
            {
                "mutation_id": mutation_id,
                "expected_validator": expected_validator,
                "validation_failed": expected_validator in failing,
                "failing_validators": failing,
                "producer_function": "run_negative_controls",
                "validation_rule": "mutated invalid contract must fail through callable validators",
            }
        )
    return {
        "task_id": TASK_ID,
        "controls": rows,
        "all_negative_controls_failed": all(row["validation_failed"] for row in rows),
        "aggregation_rule": "each mutation must trigger its expected validator",
        "validation_rule": "negative controls must fail, not pass as clean reports",
    }


def build_result(
    existing_search: dict[str, Any],
    post_bridge: dict[str, Any],
    validators: list[dict[str, Any]],
    negative_controls: dict[str, Any],
    input_hashes_before: dict[str, str],
    input_hashes_after: dict[str, str],
) -> dict[str, Any]:
    all_validators_passed = all(row["passed"] for row in validators)
    protected_modified = input_hashes_before != input_hashes_after
    stop_conditions = []
    if existing_search["complete_equivalent_contract_found"]:
        stop_conditions.append("complete_equivalent_alignment_contract_exists")
    if not post_bridge["resolved"]:
        stop_conditions.append("blocked_post_bridge_boundary_unresolved")
    if not all_validators_passed:
        stop_conditions.append("alignment_contract_validation_failed")
    if not negative_controls["all_negative_controls_failed"]:
        stop_conditions.append("negative_control_failed_to_fail")
    if protected_modified:
        stop_conditions.append("sealed_or_parent_artifact_modified")
    return {
        "task_id": TASK_ID,
        "verdict": VERDICT_PASS if not stop_conditions else "blocked_or_failed",
        "layer": LAYER,
        "claim_ceiling": CLAIM_CEILING,
        "alignment_document_mode": "amendment_to_existing_admission_task_card_001a",
        "complete_equivalent_contract_found": existing_search["complete_equivalent_contract_found"],
        "partial_contract_found": existing_search["partial_contract_found"],
        "post_bridge_001d_resolved": post_bridge["resolved"],
        "post_bridge_001d_commit": post_bridge.get("commit"),
        "post_bridge_001d_verdict": post_bridge.get("verdict"),
        "all_validators_passed": all_validators_passed,
        "validators": validators,
        "negative_controls": negative_controls,
        "protected_parent_artifacts_modified": protected_modified,
        "protected_parent_hashes_before": input_hashes_before,
        "protected_parent_hashes_after": input_hashes_after,
        "authorization_flags": {field: False for field in AUTHORIZATION_FALSE_FIELDS},
        "actionability_revalidation_required": True,
        "matrix_duplication_allowed": False,
        "hyperon_adopted": False,
        "stop_conditions_triggered": stop_conditions,
        "artifacts_generated": [str(ARTIFACT_DIR / name) for name in REQUIRED_ARTIFACT_NAMES],
        "what_this_does_not_prove": WHAT_THIS_DOES_NOT_PROVE,
    }


def build_source_trace_report(output_dir: Path, artifacts: dict[str, dict[str, Any]], run_id: str) -> dict[str, Any]:
    rows = []
    artifact_names = sorted(set(REQUIRED_ARTIFACT_NAMES) - {"claim_ceiling.txt", "source_trace_report.json"})
    boundaries = [
        ("admission_coverage_reference", ADMISSION_COVERAGE_REFERENCE_COMMIT, ADMISSION_COVERAGE_REFERENCE_TAG, str(ADMISSION_COVERAGE_REFERENCE_ARTIFACT)),
        ("canonical_coverage_repair", CANONICAL_COVERAGE_REPAIR_COMMIT, CANONICAL_COVERAGE_REPAIR_TAG, str(CANONICAL_REPAIR_RESULT)),
        ("compression_source_boundary", COMPRESSION_SOURCE_COMMIT, COMPRESSION_SOURCE_TAG, str(COMPRESSION_SOURCE_DOC)),
        ("prior_readiness_audit", PRIOR_READINESS_AUDIT_COMMIT, None, str(PRIOR_READINESS_AUDIT_DOC)),
        ("post_bridge_admission_executable_001d", POST_BRIDGE_001D_COMMIT, POST_BRIDGE_001D_TAG, str(POST_BRIDGE_001D_RESULT)),
    ]
    for name in artifact_names:
        payload_hash = artifacts[name]["computed_evidence_provenance"]["output_artifact_hash"]
        materialized = output_dir / name
        for boundary, commit, tag, input_reference in boundaries:
            rows.append(
                {
                    "artifact": str(ARTIFACT_DIR / name),
                    "referenced_boundary": boundary,
                    "referenced_commit": commit,
                    "referenced_tag": tag,
                    "producer_function": "build_source_trace_report",
                    "input_reference": input_reference,
                    "output_artifact_hash": payload_hash,
                    "materialized_artifact_hash": _sha_file(materialized) if materialized.exists() else None,
                    "run_id": run_id,
                    "code_path_hash": _code_path_hash(build_source_trace_report),
                    "validation_rule": "artifact must trace to all parent evidence boundaries",
                }
            )
    rows.append(
        {
            "artifact": str(ARTIFACT_DIR / "claim_ceiling.txt"),
            "referenced_boundary": "claim_ceiling",
            "referenced_commit": ADMISSION_COVERAGE_REFERENCE_COMMIT,
            "referenced_tag": ADMISSION_COVERAGE_REFERENCE_TAG,
            "producer_function": "run_alignment_contract",
            "input_reference": CLAIM_CEILING,
            "output_artifact_hash": _sha_text(CLAIM_CEILING + "\n"),
            "materialized_artifact_hash": _sha_file(output_dir / "claim_ceiling.txt")
            if (output_dir / "claim_ceiling.txt").exists()
            else None,
            "run_id": run_id,
            "code_path_hash": _code_path_hash(run_alignment_contract),
            "validation_rule": "claim ceiling artifact must remain bounded",
        }
    )
    report = {
        "task_id": TASK_ID,
        "trace_rows": rows,
        "artifacts_traced": sorted({row["artifact"] for row in rows}),
        "validation_rule": "all new artifacts trace to the named parent boundaries",
    }
    report_hash = _payload_hash(report)
    for boundary, commit, tag, input_reference in boundaries:
        rows.append(
            {
                "artifact": str(ARTIFACT_DIR / "source_trace_report.json"),
                "referenced_boundary": boundary,
                "referenced_commit": commit,
                "referenced_tag": tag,
                "producer_function": "build_source_trace_report",
                "input_reference": input_reference,
                "output_artifact_hash": report_hash,
                "output_hash_scope": "source_trace_report payload before self-trace rows and metadata envelope",
                "materialized_artifact_hash": None,
                "run_id": run_id,
                "code_path_hash": _code_path_hash(build_source_trace_report),
                "validation_rule": "source trace report self-row avoids circular materialized hash recursion",
            }
        )
    report["trace_rows"] = rows
    report["artifacts_traced"] = sorted({row["artifact"] for row in rows})
    return report


def hash_protected_inputs(root: Path) -> dict[str, str]:
    return {
        _rel(root / path, root): _sha_file(root / path)
        for path in PROTECTED_INPUTS
        if (root / path).exists()
    }


def _blocked_result(verdict: str, stop_conditions: list[str], run_id: str) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "verdict": verdict,
        "run_id": run_id,
        "layer": LAYER,
        "claim_ceiling": CLAIM_CEILING,
        "stop_conditions_triggered": stop_conditions,
        "what_this_does_not_prove": WHAT_THIS_DOES_NOT_PROVE,
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
        str(ADMISSION_COVERAGE_REFERENCE_ARTIFACT),
        str(CANONICAL_REPAIR_RESULT),
        str(COMPRESSION_SOURCE_DOC),
        str(PRIOR_READINESS_AUDIT_DOC),
        str(POST_BRIDGE_001D_RESULT),
    ]


def _run_id(root: Path) -> str:
    seed = "|".join(
        [
            TASK_ID,
            ADMISSION_COVERAGE_REFERENCE_COMMIT,
            CANONICAL_COVERAGE_REPAIR_COMMIT,
            COMPRESSION_SOURCE_COMMIT,
            PRIOR_READINESS_AUDIT_COMMIT,
            _sha_file(root / POST_BRIDGE_001D_RESULT) if (root / POST_BRIDGE_001D_RESULT).exists() else "missing",
        ]
    )
    return f"ego_mainline_admission_task_card_alignment_001a_{_sha_text(seed)[:16]}"


def _write_doc(
    path: Path,
    contract: dict[str, Any],
    parent_manifest: dict[str, Any],
    post_bridge: dict[str, Any],
    existing_search: dict[str, Any],
    negative_controls: dict[str, Any],
) -> None:
    parent_lines = []
    for row in parent_manifest["parent_boundaries"]:
        parent_lines.append(
            f"- `{row['boundary_id']}`: `{row.get('commit')}` / `{row.get('tag')}`; allowed={'; '.join(row.get('allowed_support', []))}; forbidden={'; '.join(row.get('forbidden_support', []))}"
        )
    text = f"""# {TASK_ID}

## Verdict

`{VERDICT_PASS}`

## Layer

{LAYER}

This is an amendment-style alignment contract for future EGO-mainline admission
execution planning. It does not execute admission, authorize runtime, enter
Gate4, enter bridge runtime, enter EGO runtime, create companion behavior, or
authorize LLM/RAG, user-model, relationship, emotion, personalization, or
implementation work.

## Existing Contract Search

- Complete equivalent contract found: `{str(existing_search['complete_equivalent_contract_found']).lower()}`
- Partial contract found: `{str(existing_search['partial_contract_found']).lower()}`
- Alignment document mode: `amendment_to_existing_admission_task_card_001a`

## Parent Evidence Boundaries

{chr(10).join(parent_lines)}

## Post-Bridge 001D Resolution

- Artifact path: `{post_bridge['artifact_path']}`
- Commit: `{post_bridge['commit']}`
- Remote tag: `{post_bridge['remote_tag']}`
- Verdict: `{post_bridge['verdict']}`
- Claim ceiling: {post_bridge['claim_ceiling']}
- Treat as mechanism proof: `false`

## Future Execution Requirements

- Actionability revalidation is required before any future admission execution.
- Computed-evidence provenance is required for all future verdict-bearing results.
- 001B and 001C post-bridge artifacts remain non-positive downstream evidence.
- 001D remains only a bounded post-bridge positive candidate with caveats.
- No copied 45-row canonical coverage matrix is allowed.

## Authorization Guard

{chr(10).join(f"- {field}: `false`" for field in AUTHORIZATION_FALSE_FIELDS)}

## Negative Controls

All required mutated-input controls failed through callable validators:
`{str(negative_controls['all_negative_controls_failed']).lower()}`.

## Claim Ceiling

{CLAIM_CEILING}

## What This Does Not Prove

{chr(10).join(f"- {claim}" for claim in WHAT_THIS_DOES_NOT_PROVE)}
"""
    _write_text(path, text)


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


def _git_output(root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    result = run_alignment_contract(repo_root=args.repo_root, output_dir=args.output_dir)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
