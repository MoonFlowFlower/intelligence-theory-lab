from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
from typing import Any, Callable


TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTION-PREFLIGHT-001A"
ARTIFACT_DIR = Path("artifacts/ego_mainline_admission_execution_preflight_001a")
DOC_PATH = Path("docs/codex/tasks/EGO-MAINLINE-ADMISSION-EXECUTION-PREFLIGHT-001A.md")
VERDICT_PASS = "pass_admission_execution_may_be_tasked_separately"
VERDICT_BLOCKED = "blocked_admission_execution_preflight"
LAYER = "evidence-governance / admission execution readiness planning only"
CLAIM_CEILING = "bounded admission execution readiness preflight only"

ALIGNMENT_001A_COMMIT = "095a1fcb644dc21e5f59636f9cf5a183e6989537"
ALIGNMENT_001A_TAG = "remote-anchor-admission-alignment-001a-095a1fc"
COVERAGE_REFERENCE_001A_COMMIT = "c5b067faea764657bd24cd75415a6ceb59905dab"
COVERAGE_REFERENCE_001A_TAG = "remote-anchor-admission-coverage-reference-001a-c5b067f"
CANONICALIZATION_REPAIR_001B_COMMIT = "df6ad31ed58d2e3772e3f53b35ad926ab995d582"
CANONICALIZATION_REPAIR_001B_TAG = "remote-anchor-coverage-canonicalization-repair-001b-df6ad31"
COVERAGE_COMPRESSION_001D_COMMIT = "614b147d14cc4bb02b7c6afa2c90661cdce15e4c"
COVERAGE_COMPRESSION_001D_TAG = "remote-anchor-coverage-compression-001d-614b147"
POST_BRIDGE_001D_COMMIT = "c2f6c5184a119202dd0a7efc23d3bfe3317af890"
POST_BRIDGE_001D_TAG = "remote-anchor-001n-c2f6c51"
PRIOR_READINESS_AUDIT_COMMIT = "f648dac4bfbcdc7a98c1edea5a97dbef4101d83a"
BLOCKED_OLD_CANONICALIZATION_001A_COMMIT = "2882f4796dd40cfd16a2c07b5c718d477876fb5f"

ALIGNMENT_DOC = Path("docs/codex/tasks/EGO-MAINLINE-ADMISSION-TASK-CARD-ALIGNMENT-001A.md")
ALIGNMENT_ARTIFACT_DIR = Path("artifacts/ego_mainline_admission_task_card_alignment_001a")
ALIGNMENT_RESULT = ALIGNMENT_ARTIFACT_DIR / "result.json"
ALIGNMENT_PARENT_MANIFEST = ALIGNMENT_ARTIFACT_DIR / "parent_evidence_boundary_manifest.json"
ALIGNMENT_ACTIONABILITY = ALIGNMENT_ARTIFACT_DIR / "actionability_revalidation_matrix.json"
ALIGNMENT_COMPUTED_GATE = ALIGNMENT_ARTIFACT_DIR / "computed_evidence_gate_contract.json"
ALIGNMENT_NEGATIVE = ALIGNMENT_ARTIFACT_DIR / "negative_evidence_handling_contract.json"
ALIGNMENT_AUTHORIZATION = ALIGNMENT_ARTIFACT_DIR / "authorization_guard.json"
ALIGNMENT_SCHEMA = ALIGNMENT_ARTIFACT_DIR / "schema_duplication_guard.json"

COVERAGE_REFERENCE_DOC = Path("docs/research/EGO-MAINLINE-ADMISSION-CANONICAL-COVERAGE-REFERENCE-001A.md")
COVERAGE_REFERENCE_RESULT = Path("artifacts/ego_mainline_admission_canonical_coverage_reference_001a/result.json")
COVERAGE_REFERENCE_CONTRACT = Path("artifacts/ego_mainline_admission_canonical_coverage_reference_001a/reference_contract.json")
CANONICALIZATION_REPAIR_DOC = Path("docs/research/THEORY-LANDSCAPE-COVERAGE-CANONICALIZATION-PROVENANCE-REPAIR-001B.md")
CANONICALIZATION_REPAIR_RESULT = Path(
    "artifacts/theory_landscape_coverage_canonicalization_provenance_repair_001b/result.json"
)
COVERAGE_COMPRESSION_DOC = Path("docs/research/THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001D.md")
POST_BRIDGE_001D_DOC = Path("docs/codex/tasks/POST-BRIDGE-ADMISSION-EXECUTABLE-001D.md")
POST_BRIDGE_001D_RESULT = Path("artifacts/post_bridge_admission_executable_001d/result.json")
PRIOR_READINESS_AUDIT_DOC = Path("docs/codex/audits/EGO-MAINLINE-READINESS-AUDIT-001B.md")
PRIOR_READINESS_AUDIT_RESULT = Path("artifacts/ego_mainline_readiness_audit_001b/result.json")

REQUIRED_ARTIFACT_NAMES = [
    "result.json",
    "parent_boundary_readback.json",
    "post_bridge_001d_readback.json",
    "alignment_contract_readback.json",
    "actionability_revalidation_preconditions.json",
    "computed_evidence_preconditions.json",
    "negative_evidence_preconditions.json",
    "forbidden_claims_and_actions.json",
    "authorization_flags.json",
    "claim_ceiling.txt",
]

PROTECTED_INPUTS = [
    ALIGNMENT_DOC,
    ALIGNMENT_RESULT,
    ALIGNMENT_PARENT_MANIFEST,
    ALIGNMENT_ACTIONABILITY,
    ALIGNMENT_COMPUTED_GATE,
    ALIGNMENT_NEGATIVE,
    ALIGNMENT_AUTHORIZATION,
    ALIGNMENT_SCHEMA,
    COVERAGE_REFERENCE_DOC,
    COVERAGE_REFERENCE_RESULT,
    COVERAGE_REFERENCE_CONTRACT,
    CANONICALIZATION_REPAIR_DOC,
    CANONICALIZATION_REPAIR_RESULT,
    COVERAGE_COMPRESSION_DOC,
    POST_BRIDGE_001D_DOC,
    POST_BRIDGE_001D_RESULT,
    PRIOR_READINESS_AUDIT_DOC,
    PRIOR_READINESS_AUDIT_RESULT,
]
PROTECTED_INPUTS_AS_POSIX = [path.as_posix() for path in PROTECTED_INPUTS]

FORBIDDEN_CLAIMS = [
    "admission success",
    "EGO readiness",
    "bridge readiness",
    "runtime readiness",
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
    "runtime authorization",
]

FORBIDDEN_ACTIONS = [
    "admission execution",
    "runtime authorization",
    "Gate4 execution",
    "bridge runtime",
    "EGO runtime",
    "companion behavior",
    "LLM/RAG",
    "user-model",
    "relationship",
    "emotion",
    "personalization",
    "architecture implementation",
    "mechanism validation",
]

AUTHORIZATION_FALSE_FIELDS = [
    "implementation_authorized",
    "runtime_authorized",
    "bridge_authorized",
    "bridge_runtime_authorized",
    "companion_authorized",
    "companion_behavior_authorized",
    "ego_mainline_runtime_authorized",
    "ego_mainline_authorized",
    "gate4_authorized",
    "llm_rag_authorized",
    "user_model_authorized",
    "relationship_authorized",
    "emotion_authorized",
    "personalization_authorized",
    "architecture_selected",
    "architecture_implementation_authorized",
    "mechanism_validation_authorized",
]


def run_preflight(
    repo_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    verify_remote: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    out = Path(output_dir) if output_dir is not None else root / ARTIFACT_DIR
    if not out.is_absolute():
        out = root / out
    out.mkdir(parents=True, exist_ok=True)

    state = build_preflight_state(root, out, verify_remote=verify_remote)
    validators = validate_preflight_state(state)
    negative_controls = run_negative_controls(state)
    protected_after = hash_protected_inputs(root)
    result = build_result(state, validators, negative_controls, protected_after)

    artifacts = {
        "parent_boundary_readback.json": state["parent_boundary_readback"],
        "post_bridge_001d_readback.json": state["post_bridge_001d_readback"],
        "alignment_contract_readback.json": state["alignment_contract_readback"],
        "actionability_revalidation_preconditions.json": state["actionability_revalidation_preconditions"],
        "computed_evidence_preconditions.json": state["computed_evidence_preconditions"],
        "negative_evidence_preconditions.json": state["negative_evidence_preconditions"],
        "forbidden_claims_and_actions.json": state["forbidden_claims_and_actions"],
        "authorization_flags.json": state["authorization_flags"],
        "result.json": result,
    }
    ref_rows = _input_ref_rows(state)
    for name, payload in artifacts.items():
        _write_json(
            out / name,
            _with_metadata(
                artifact_name=name,
                payload=payload,
                producer=_producer_for_artifact(name),
                input_artifacts=state["input_artifacts_by_output"].get(name, []),
                input_refs_tags_commits=ref_rows,
                run_id=state["run_id"],
                aggregation_rule=_aggregation_rule_for_artifact(name),
            ),
        )
    _write_text(out / "claim_ceiling.txt", CLAIM_CEILING + "\n")
    return result


def build_preflight_state(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
    verify_remote: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    out = Path(output_dir) if output_dir is not None else root / ARTIFACT_DIR
    if not out.is_absolute():
        out = root / out

    parent_boundary_readback = build_parent_boundary_readback(root, verify_remote)
    post_bridge = build_post_bridge_001d_readback(root)
    alignment = build_alignment_contract_readback(root)
    actionability = build_actionability_revalidation_preconditions(alignment)
    computed = build_computed_evidence_preconditions(alignment)
    negative = build_negative_evidence_preconditions(alignment)
    forbidden = build_forbidden_claims_and_actions()
    authorization = build_authorization_flags(alignment, post_bridge)
    schema_duplication = build_schema_duplication_state(root, out, alignment)

    return {
        "task_id": TASK_ID,
        "run_id": _run_id(root),
        "repo_root": root.as_posix(),
        "output_dir": out.as_posix(),
        "verify_remote": verify_remote,
        "parent_boundary_readback": parent_boundary_readback,
        "post_bridge_001d_readback": post_bridge,
        "alignment_contract_readback": alignment,
        "actionability_revalidation_preconditions": actionability,
        "computed_evidence_preconditions": computed,
        "negative_evidence_preconditions": negative,
        "forbidden_claims_and_actions": forbidden,
        "authorization_flags": authorization,
        "schema_duplication": schema_duplication,
        "callable_gate_logic_executed": True,
        "static_pass_result": False,
        "protected_parent_hashes_before": hash_protected_inputs(root),
        "input_artifacts_by_output": {
            "parent_boundary_readback.json": PROTECTED_INPUTS_AS_POSIX,
            "post_bridge_001d_readback.json": [POST_BRIDGE_001D_DOC.as_posix(), POST_BRIDGE_001D_RESULT.as_posix()],
            "alignment_contract_readback.json": [
                ALIGNMENT_DOC.as_posix(),
                ALIGNMENT_RESULT.as_posix(),
                ALIGNMENT_PARENT_MANIFEST.as_posix(),
                ALIGNMENT_ACTIONABILITY.as_posix(),
                ALIGNMENT_COMPUTED_GATE.as_posix(),
                ALIGNMENT_NEGATIVE.as_posix(),
                ALIGNMENT_AUTHORIZATION.as_posix(),
                ALIGNMENT_SCHEMA.as_posix(),
            ],
            "actionability_revalidation_preconditions.json": [ALIGNMENT_ACTIONABILITY.as_posix()],
            "computed_evidence_preconditions.json": [ALIGNMENT_COMPUTED_GATE.as_posix()],
            "negative_evidence_preconditions.json": [ALIGNMENT_NEGATIVE.as_posix()],
            "forbidden_claims_and_actions.json": [DOC_PATH.as_posix(), "AGENTS.md"],
            "authorization_flags.json": [ALIGNMENT_AUTHORIZATION.as_posix(), POST_BRIDGE_001D_RESULT.as_posix()],
            "result.json": REQUIRED_ARTIFACT_NAMES[1:9],
        },
    }


def build_parent_boundary_readback(root: Path, verify_remote: bool) -> dict[str, Any]:
    rows = [
        _boundary_row(
            root,
            "alignment_001a",
            "EGO-MAINLINE-ADMISSION-TASK-CARD-ALIGNMENT-001A",
            ALIGNMENT_001A_COMMIT,
            ALIGNMENT_001A_TAG,
            [ALIGNMENT_DOC, ALIGNMENT_RESULT],
            verify_remote,
            "sealed admission execution alignment contract",
        ),
        _boundary_row(
            root,
            "admission_coverage_reference_001a",
            "EGO-MAINLINE-ADMISSION-CANONICAL-COVERAGE-REFERENCE-001A",
            COVERAGE_REFERENCE_001A_COMMIT,
            COVERAGE_REFERENCE_001A_TAG,
            [COVERAGE_REFERENCE_DOC, COVERAGE_REFERENCE_RESULT],
            verify_remote,
            "sealed admission-side reference-only contract",
        ),
        _boundary_row(
            root,
            "canonicalization_provenance_repair_001b",
            "THEORY-LANDSCAPE-COVERAGE-CANONICALIZATION-PROVENANCE-REPAIR-001B",
            CANONICALIZATION_REPAIR_001B_COMMIT,
            CANONICALIZATION_REPAIR_001B_TAG,
            [CANONICALIZATION_REPAIR_DOC, CANONICALIZATION_REPAIR_RESULT],
            verify_remote,
            "sealed canonicalization provenance repair",
        ),
        _boundary_row(
            root,
            "coverage_compression_001d",
            "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001D",
            COVERAGE_COMPRESSION_001D_COMMIT,
            COVERAGE_COMPRESSION_001D_TAG,
            [COVERAGE_COMPRESSION_DOC],
            verify_remote,
            "sealed source-pinned / pre-canonicalization closure patch",
        ),
        _boundary_row(
            root,
            "post_bridge_admission_executable_001d",
            "POST-BRIDGE-ADMISSION-EXECUTABLE-001D",
            POST_BRIDGE_001D_COMMIT,
            POST_BRIDGE_001D_TAG,
            [POST_BRIDGE_001D_DOC, POST_BRIDGE_001D_RESULT],
            verify_remote=False,
            status="caveated, not mechanism proof, not runtime authorization",
        ),
        _boundary_row(
            root,
            "prior_readiness_audit_reference_only",
            "prior readiness audit reference only",
            PRIOR_READINESS_AUDIT_COMMIT,
            None,
            [PRIOR_READINESS_AUDIT_DOC],
            verify_remote=False,
            status="reference-only prior readiness audit / admission task-card drafting context",
        ),
    ]
    by_id = {row["boundary_id"]: copy.deepcopy(row) for row in rows}
    blocked_old_used = any(row["expected_commit"] == BLOCKED_OLD_CANONICALIZATION_001A_COMMIT for row in rows)
    return {
        "task_id": TASK_ID,
        "parent_boundaries": rows,
        "parent_boundaries_by_id": by_id,
        "blocked_old_canonicalization_001a": {
            "commit": BLOCKED_OLD_CANONICALIZATION_001A_COMMIT,
            "used_as_parent": blocked_old_used,
            "status": "blocked and explicitly excluded",
        },
        "all_required_boundaries_resolved": all(row["resolved_exactly"] for row in rows) and not blocked_old_used,
        "all_required_remote_anchors_verified": all(
            row["remote_verified"] for row in rows if row.get("remote_tag_required")
        ),
        "validation_rule": "required parent boundaries must resolve by git tags, remote tags, and repo paths",
    }


def build_post_bridge_001d_readback(root: Path) -> dict[str, Any]:
    result_path = root / POST_BRIDGE_001D_RESULT
    doc_path = root / POST_BRIDGE_001D_DOC
    if not result_path.exists() or not doc_path.exists():
        return {
            "task_id": "POST-BRIDGE-ADMISSION-EXECUTABLE-001D",
            "resolved": False,
            "blocked_reason": "missing_post_bridge_001d_doc_or_result",
        }
    result = _read_json(result_path)
    anti = result.get("anti_sycophancy_audit", {})
    caveats = [
        anti.get("strongest_reason_task_may_be_invalid", ""),
        anti.get("evidence_that_would_still_be_insufficient", ""),
        "001D is caveated bounded post-bridge evidence, not mechanism proof.",
        "001D does not authorize runtime, bridge readiness, EGO readiness, or companion behavior.",
    ]
    caveats = [row for row in caveats if row]
    authorization_flags = result.get("authorization_flags", {})
    return {
        "task_id": "POST-BRIDGE-ADMISSION-EXECUTABLE-001D",
        "resolved": True,
        "blocked_reason": None,
        "artifact_path": POST_BRIDGE_001D_RESULT.as_posix(),
        "task_card_path": POST_BRIDGE_001D_DOC.as_posix(),
        "commit": _path_last_commit(root, [POST_BRIDGE_001D_DOC, POST_BRIDGE_001D_RESULT]) or POST_BRIDGE_001D_COMMIT,
        "verdict": result.get("verdict"),
        "bounded_pass": result.get("bounded_pass"),
        "claim_ceiling": result.get("claim_ceiling"),
        "caveats": caveats,
        "what_this_does_not_prove": result.get("what_this_does_not_prove", []),
        "authorization_flags": authorization_flags,
        "treat_as_mechanism_proof": False,
        "runtime_authorized": False,
        "validation_rule": "post-bridge 001D verdict, caveats, artifact path, and claim ceiling must be re-read from repo state",
    }


def build_alignment_contract_readback(root: Path) -> dict[str, Any]:
    required = [
        ALIGNMENT_RESULT,
        ALIGNMENT_PARENT_MANIFEST,
        ALIGNMENT_ACTIONABILITY,
        ALIGNMENT_COMPUTED_GATE,
        ALIGNMENT_NEGATIVE,
        ALIGNMENT_AUTHORIZATION,
        ALIGNMENT_SCHEMA,
    ]
    missing = [path.as_posix() for path in required if not (root / path).exists()]
    if missing:
        return {
            "task_id": "EGO-MAINLINE-ADMISSION-TASK-CARD-ALIGNMENT-001A",
            "resolved": False,
            "missing_inputs": missing,
        }
    result = _read_json(root / ALIGNMENT_RESULT)
    parent_manifest = _read_json(root / ALIGNMENT_PARENT_MANIFEST)
    actionability = _read_json(root / ALIGNMENT_ACTIONABILITY)
    computed = _read_json(root / ALIGNMENT_COMPUTED_GATE)
    negative = _read_json(root / ALIGNMENT_NEGATIVE)
    authorization = _read_json(root / ALIGNMENT_AUTHORIZATION)
    schema = _read_json(root / ALIGNMENT_SCHEMA)
    post_bridge_row = _find_row(
        parent_manifest.get("parent_boundaries", []),
        "boundary_id",
        "post_bridge_admission_executable_001d",
    )
    return {
        "task_id": "EGO-MAINLINE-ADMISSION-TASK-CARD-ALIGNMENT-001A",
        "resolved": True,
        "verdict": result.get("verdict"),
        "commit": _path_last_commit(root, [ALIGNMENT_DOC, ALIGNMENT_RESULT]) or ALIGNMENT_001A_COMMIT,
        "actionability_revalidation_required": actionability.get("actionability_revalidation_required") is True
        and result.get("actionability_revalidation_required") is True,
        "computed_evidence_gate_required_for_future_execution": computed.get(
            "computed_evidence_gate_required_for_future_execution"
        )
        is True,
        "static_or_literal_verdicts_allowed": computed.get("static_or_literal_verdicts_allowed"),
        "negative_evidence_handling_required": negative.get("negative_evidence_handling_required") is True,
        "schema_duplication_allowed": schema.get("duplicate_schema_created") is True
        or schema.get("matrix_duplication_allowed") is True,
        "copied_45_row_matrix_detected": schema.get("copied_45_row_matrix_detected") is True,
        "post_bridge_001d_mechanism_proof_allowed": post_bridge_row.get("mechanism_proof_allowed", False) is True,
        "authorization_flags": authorization.get("authorization_flags", {}),
        "actionability_source": actionability,
        "computed_source": computed,
        "negative_source": negative,
        "schema_source": schema,
        "validation_rule": "alignment 001A must require actionability revalidation, computed-evidence gates, negative-evidence preservation, and schema duplication blocks",
    }


def build_actionability_revalidation_preconditions(alignment: dict[str, Any]) -> dict[str, Any]:
    rows = alignment.get("actionability_source", {}).get("revalidation_rows", [])
    preconditions = [
        {
            "boundary_id": row.get("boundary_id"),
            "required": row.get("required") is True,
            "revalidation_required_before": row.get("revalidation_required_before"),
            "revalidation_rule": row.get("revalidation_rule"),
        }
        for row in rows
    ]
    return {
        "task_id": TASK_ID,
        "source_task_id": "EGO-MAINLINE-ADMISSION-TASK-CARD-ALIGNMENT-001A",
        "all_preconditions_required": bool(preconditions) and all(row["required"] for row in preconditions),
        "preconditions": preconditions,
        "validation_rule": "future admission execution remains blocked until every actionability row is revalidated",
    }


def build_computed_evidence_preconditions(alignment: dict[str, Any]) -> dict[str, Any]:
    computed = alignment.get("computed_source", {})
    return {
        "task_id": TASK_ID,
        "source_task_id": "EGO-MAINLINE-ADMISSION-TASK-CARD-ALIGNMENT-001A",
        "computed_evidence_gate_required_for_future_execution": computed.get(
            "computed_evidence_gate_required_for_future_execution"
        )
        is True,
        "static_or_literal_verdicts_allowed": computed.get("static_or_literal_verdicts_allowed"),
        "required_metadata_fields": computed.get("required_metadata_fields", []),
        "future_execution_must_include": computed.get("future_execution_must_include", []),
        "validation_rule": "future admission execution verdicts must derive from callable computation paths",
    }


def build_negative_evidence_preconditions(alignment: dict[str, Any]) -> dict[str, Any]:
    negative = alignment.get("negative_source", {})
    rows = negative.get("negative_evidence_rows", [])
    return {
        "task_id": TASK_ID,
        "source_task_id": "EGO-MAINLINE-ADMISSION-TASK-CARD-ALIGNMENT-001A",
        "negative_evidence_handling_required": negative.get("negative_evidence_handling_required") is True,
        "negative_evidence_rows": rows,
        "negative_001b_001c_positive_downstream_use_allowed": any(
            row.get("task_id") in {"POST-BRIDGE-ADMISSION-EXECUTABLE-001B", "POST-BRIDGE-ADMISSION-EXECUTABLE-001C"}
            and row.get("positive_evidence_allowed") is True
            for row in rows
        ),
        "validation_rule": "001B/001C negative or suspended evidence must not become positive downstream evidence",
    }


def build_forbidden_claims_and_actions() -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "allowed_verdicts": [VERDICT_PASS, VERDICT_BLOCKED],
        "forbidden_verdicts": [
            "EGO ready",
            "bridge ready",
            "runtime ready",
            "mechanism proven",
            "architecture valid",
            "Gate4 authorized",
            "companion authorized",
            "admission executed",
        ],
        "validation_rule": "preflight may only authorize creation of a separate bounded task, not runtime or admission execution",
    }


def build_authorization_flags(alignment: dict[str, Any], post_bridge: dict[str, Any]) -> dict[str, Any]:
    flags = {field: False for field in AUTHORIZATION_FALSE_FIELDS}
    for source in [alignment.get("authorization_flags", {}), post_bridge.get("authorization_flags", {})]:
        for key, value in source.items():
            if key in flags:
                flags[key] = value is True
            elif "authorized" in key or key.endswith("_authorization"):
                flags[key] = value is True
    return {
        "task_id": TASK_ID,
        "authorization_flags": flags,
        "all_authorization_flags_false": all(value is False for value in flags.values()),
        "generated_from_resolved_state": alignment.get("resolved") is True and post_bridge.get("resolved") is True,
        "validation_rule": "authorization flags are generated from resolved alignment and post-bridge state and must remain false",
    }


def build_schema_duplication_state(root: Path, output_dir: Path, alignment: dict[str, Any]) -> dict[str, Any]:
    generated_paths = [DOC_PATH, *[ARTIFACT_DIR / name for name in REQUIRED_ARTIFACT_NAMES]]
    existing_generated = [root / path for path in generated_paths if (root / path).exists()]
    scan_hits = []
    for path in existing_generated:
        if path.suffix.lower() == ".json":
            try:
                payload = _read_json(path)
            except json.JSONDecodeError:
                continue
            scan_hits.extend(_copied_matrix_hits(payload, _rel(path, root)))
    schema_source = alignment.get("schema_source", {})
    return {
        "task_id": TASK_ID,
        "duplicate_admission_schema_created": schema_source.get("duplicate_schema_created") is True,
        "copied_45_row_matrix_detected": schema_source.get("copied_45_row_matrix_detected") is True or bool(scan_hits),
        "matrix_scan_hits": scan_hits,
        "generated_output_dir": output_dir.as_posix(),
        "validation_rule": "new preflight must not create duplicate admission schema or copy the 45-row matrix",
    }


def validate_preflight_state(state: dict[str, Any]) -> list[dict[str, Any]]:
    validators = [
        validate_parent_boundaries,
        validate_post_bridge_001d_readback,
        validate_alignment_contract_readback,
        validate_actionability_preconditions,
        validate_computed_evidence_preconditions,
        validate_negative_evidence_preconditions,
        validate_forbidden_claims_and_actions,
        validate_authorization_flags,
        validate_duplicate_schema_and_matrix,
        validate_computed_verdict_source,
    ]
    return [validator(state) for validator in validators]


def validate_parent_boundaries(state: dict[str, Any]) -> dict[str, Any]:
    failures = []
    readback = state.get("parent_boundary_readback", {})
    rows = readback.get("parent_boundaries_by_id", {})
    required = {
        "alignment_001a": ALIGNMENT_001A_COMMIT,
        "admission_coverage_reference_001a": COVERAGE_REFERENCE_001A_COMMIT,
        "canonicalization_provenance_repair_001b": CANONICALIZATION_REPAIR_001B_COMMIT,
        "coverage_compression_001d": COVERAGE_COMPRESSION_001D_COMMIT,
        "post_bridge_admission_executable_001d": POST_BRIDGE_001D_COMMIT,
        "prior_readiness_audit_reference_only": PRIOR_READINESS_AUDIT_COMMIT,
    }
    for boundary_id, expected in required.items():
        row = rows.get(boundary_id)
        if not row:
            failures.append(f"missing_parent_boundary:{boundary_id}")
            continue
        if row.get("expected_commit") != expected:
            failures.append(f"expected_commit_mismatch:{boundary_id}")
        if row.get("path_last_commit") != expected:
            failures.append(f"path_commit_mismatch:{boundary_id}")
        if row.get("remote_tag") and row.get("remote_resolved_commit") != expected:
            failures.append(f"remote_anchor_mismatch:{boundary_id}")
        if row.get("remote_tag") and row.get("local_tag_resolved_commit") != expected:
            failures.append(f"local_tag_mismatch:{boundary_id}")
    blocked = readback.get("blocked_old_canonicalization_001a", {})
    if blocked.get("used_as_parent") is not False:
        failures.append("blocked_old_canonicalization_001a_used_as_parent")
    if readback.get("all_required_boundaries_resolved") is not True:
        failures.append("all_required_boundaries_not_resolved")
    return _validator_result("validate_parent_boundaries", failures)


def validate_post_bridge_001d_readback(state: dict[str, Any]) -> dict[str, Any]:
    post_bridge = state.get("post_bridge_001d_readback", {})
    failures = []
    if post_bridge.get("resolved") is not True:
        failures.append("post_bridge_001d_unresolved")
    if post_bridge.get("artifact_path") != POST_BRIDGE_001D_RESULT.as_posix():
        failures.append("post_bridge_001d_artifact_path_mismatch")
    if post_bridge.get("commit") != POST_BRIDGE_001D_COMMIT:
        failures.append("post_bridge_001d_commit_mismatch")
    if post_bridge.get("verdict") != "post_bridge_admission_executable_001d_pass":
        failures.append("post_bridge_001d_verdict_missing_or_mismatch")
    if not post_bridge.get("claim_ceiling"):
        failures.append("post_bridge_001d_claim_ceiling_unresolved")
    if not post_bridge.get("caveats"):
        failures.append("post_bridge_001d_caveats_unresolved")
    if post_bridge.get("treat_as_mechanism_proof") is not False:
        failures.append("post_bridge_001d_treated_as_mechanism_proof")
    if post_bridge.get("runtime_authorized") is not False:
        failures.append("post_bridge_001d_runtime_authorized")
    return _validator_result("validate_post_bridge_001d_readback", failures)


def validate_alignment_contract_readback(state: dict[str, Any]) -> dict[str, Any]:
    alignment = state.get("alignment_contract_readback", {})
    failures = []
    if alignment.get("resolved") is not True:
        failures.append("alignment_001a_unresolved")
    if alignment.get("commit") != ALIGNMENT_001A_COMMIT:
        failures.append("alignment_001a_commit_mismatch")
    if alignment.get("actionability_revalidation_required") is not True:
        failures.append("alignment_actionability_revalidation_missing")
    if alignment.get("computed_evidence_gate_required_for_future_execution") is not True:
        failures.append("alignment_computed_evidence_gate_missing")
    if alignment.get("static_or_literal_verdicts_allowed") is not False:
        failures.append("alignment_static_or_literal_verdicts_allowed")
    if alignment.get("negative_evidence_handling_required") is not True:
        failures.append("alignment_negative_evidence_handling_missing")
    if alignment.get("schema_duplication_allowed") is not False:
        failures.append("alignment_schema_duplication_allowed")
    if alignment.get("copied_45_row_matrix_detected") is not False:
        failures.append("alignment_copied_45_row_matrix_detected")
    if alignment.get("post_bridge_001d_mechanism_proof_allowed") is not False:
        failures.append("alignment_post_bridge_001d_mechanism_proof_allowed")
    return _validator_result("validate_alignment_contract_readback", failures)


def validate_actionability_preconditions(state: dict[str, Any]) -> dict[str, Any]:
    actionability = state.get("actionability_revalidation_preconditions", {})
    failures = []
    rows = actionability.get("preconditions", [])
    if actionability.get("all_preconditions_required") is not True:
        failures.append("actionability_preconditions_not_all_required")
    if not rows:
        failures.append("actionability_preconditions_missing")
    for row in rows:
        if row.get("required") is not True:
            failures.append(f"actionability_row_not_required:{row.get('boundary_id')}")
    return _validator_result("validate_actionability_preconditions", failures)


def validate_computed_evidence_preconditions(state: dict[str, Any]) -> dict[str, Any]:
    computed = state.get("computed_evidence_preconditions", {})
    failures = []
    if computed.get("computed_evidence_gate_required_for_future_execution") is not True:
        failures.append("computed_evidence_gate_missing")
    if computed.get("static_or_literal_verdicts_allowed") is not False:
        failures.append("static_or_literal_verdicts_allowed")
    required = set(computed.get("required_metadata_fields", []))
    for field in ["producer_function", "input_artifacts", "run_id", "aggregation_rule", "code_path_hash"]:
        if field not in required:
            failures.append(f"computed_metadata_field_missing:{field}")
    return _validator_result("validate_computed_evidence_preconditions", failures)


def validate_negative_evidence_preconditions(state: dict[str, Any]) -> dict[str, Any]:
    negative = state.get("negative_evidence_preconditions", {})
    failures = []
    if negative.get("negative_evidence_handling_required") is not True:
        failures.append("negative_evidence_handling_missing")
    rows = {row.get("task_id"): row for row in negative.get("negative_evidence_rows", [])}
    for task_id in ["POST-BRIDGE-ADMISSION-EXECUTABLE-001B", "POST-BRIDGE-ADMISSION-EXECUTABLE-001C"]:
        if task_id not in rows:
            failures.append(f"negative_evidence_row_missing:{task_id}")
        elif rows[task_id].get("positive_evidence_allowed") is not False:
            failures.append(f"negative_evidence_treated_as_positive:{task_id}")
    row_001d = rows.get("POST-BRIDGE-ADMISSION-EXECUTABLE-001D")
    if not row_001d:
        failures.append("post_bridge_001d_negative_handling_row_missing")
    elif row_001d.get("mechanism_proof_allowed") is not False:
        failures.append("post_bridge_001d_mechanism_proof_allowed")
    if negative.get("negative_001b_001c_positive_downstream_use_allowed") is not False:
        failures.append("negative_001b_001c_positive_downstream_use_allowed")
    return _validator_result("validate_negative_evidence_preconditions", failures)


def validate_forbidden_claims_and_actions(state: dict[str, Any]) -> dict[str, Any]:
    forbidden = state.get("forbidden_claims_and_actions", {})
    failures = []
    claims = set(forbidden.get("forbidden_claims", []))
    actions = set(forbidden.get("forbidden_actions", []))
    for claim in FORBIDDEN_CLAIMS:
        if claim not in claims:
            failures.append(f"forbidden_claim_missing:{claim}")
    for action in ["admission execution", "runtime authorization", "Gate4 execution"]:
        if action not in actions:
            failures.append(f"forbidden_action_missing:{action}")
    if VERDICT_PASS not in forbidden.get("allowed_verdicts", []):
        failures.append("allowed_pass_verdict_missing")
    return _validator_result("validate_forbidden_claims_and_actions", failures)


def validate_authorization_flags(state: dict[str, Any]) -> dict[str, Any]:
    auth = state.get("authorization_flags", {})
    failures = []
    if auth.get("generated_from_resolved_state") is not True:
        failures.append("authorization_flags_not_generated_from_resolved_state")
    flags = auth.get("authorization_flags", {})
    if not flags:
        failures.append("authorization_flags_missing")
    for key, value in flags.items():
        if value is not False:
            failures.append(f"authorization_flag_true:{key}")
    if auth.get("all_authorization_flags_false") is not True:
        failures.append("all_authorization_flags_false_not_true")
    return _validator_result("validate_authorization_flags", failures)


def validate_duplicate_schema_and_matrix(state: dict[str, Any]) -> dict[str, Any]:
    schema = state.get("schema_duplication", {})
    failures = []
    if schema.get("duplicate_admission_schema_created") is not False:
        failures.append("duplicate_admission_schema_created")
    if schema.get("copied_45_row_matrix_detected") is not False:
        failures.append("copied_45_row_matrix_detected")
    for path, value in _walk(schema):
        if (
            isinstance(value, list)
            and len(value) == 45
            and all(isinstance(item, dict) and "candidate_id" in item for item in value)
        ):
            failures.append(f"copied_45_row_matrix:{path}")
    return _validator_result("validate_duplicate_schema_and_matrix", failures)


def validate_computed_verdict_source(state: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if state.get("callable_gate_logic_executed") is not True:
        failures.append("callable_gate_logic_not_executed")
    if state.get("static_pass_result") is not False:
        failures.append("static_pass_result_detected")
    return _validator_result("validate_computed_verdict_source", failures)


def run_negative_controls(state: dict[str, Any]) -> dict[str, Any]:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None], str]] = [
        (
            "missing_alignment_001a_anchor",
            lambda s: s["parent_boundary_readback"]["parent_boundaries_by_id"]["alignment_001a"].__setitem__(
                "remote_resolved_commit", None
            ),
            "validate_parent_boundaries",
        ),
        (
            "missing_post_bridge_001d_verdict_caveat_claim_ceiling",
            _mutate_missing_post_bridge,
            "validate_post_bridge_001d_readback",
        ),
        (
            "blocked_old_canonicalization_001a_used_as_parent",
            _mutate_blocked_old_canonicalization,
            "validate_parent_boundaries",
        ),
        (
            "authorization_flag_true",
            lambda s: s["authorization_flags"]["authorization_flags"].__setitem__("runtime_authorized", True),
            "validate_authorization_flags",
        ),
        (
            "static_pass_without_callable_gate_logic",
            _mutate_static_pass,
            "validate_computed_verdict_source",
        ),
        (
            "copied_45_row_matrix_or_duplicate_schema",
            _mutate_duplicate_schema_and_matrix,
            "validate_duplicate_schema_and_matrix",
        ),
        (
            "negative_001b_001c_treated_as_positive_downstream_evidence",
            _mutate_negative_as_positive,
            "validate_negative_evidence_preconditions",
        ),
    ]
    controls = []
    for mutation_id, mutate, expected_validator in mutations:
        mutated = copy.deepcopy(state)
        mutate(mutated)
        results = validate_preflight_state(mutated)
        failing = [row["validator"] for row in results if not row["passed"]]
        controls.append(
            {
                "mutation_id": mutation_id,
                "expected_validator": expected_validator,
                "validation_failed": expected_validator in failing,
                "failing_validators": failing,
                "producer_function": "run_negative_controls",
                "aggregation_rule": "each negative mutation must fail through its expected callable validator",
            }
        )
    return {
        "task_id": TASK_ID,
        "controls": controls,
        "all_negative_controls_failed": all(row["validation_failed"] for row in controls),
        "aggregation_rule": "all required negative-path checks must fail through callable validators",
    }


def build_result(
    state: dict[str, Any],
    validators: list[dict[str, Any]],
    negative_controls: dict[str, Any],
    protected_after: dict[str, str],
) -> dict[str, Any]:
    gate_outcomes = validators
    stop_conditions = []
    for row in validators:
        if not row["passed"]:
            stop_conditions.extend(row["failures"])
    if not negative_controls["all_negative_controls_failed"]:
        stop_conditions.append("negative_control_failed_to_fail")
    protected_modified = state["protected_parent_hashes_before"] != protected_after
    if protected_modified:
        stop_conditions.append("sealed_or_parent_artifact_modified")
    result = {
        "task_id": TASK_ID,
        "verdict": VERDICT_PASS if not stop_conditions else VERDICT_BLOCKED,
        "producer_function": "build_result",
        "layer": LAYER,
        "claim_ceiling": CLAIM_CEILING,
        "callable_gate_logic_executed": state.get("callable_gate_logic_executed") is True,
        "static_pass_result": state.get("static_pass_result") is True,
        "all_gates_passed": all(row["passed"] for row in gate_outcomes) and not stop_conditions,
        "gate_outcomes": gate_outcomes,
        "failure_reasons": stop_conditions,
        "stop_conditions_triggered": stop_conditions,
        "negative_controls": negative_controls,
        "parent_boundaries_resolved": state["parent_boundary_readback"]["all_required_boundaries_resolved"],
        "alignment_001a_remote_anchor_exact": state["parent_boundary_readback"]["parent_boundaries_by_id"][
            "alignment_001a"
        ]["remote_resolved_commit"]
        == ALIGNMENT_001A_COMMIT,
        "post_bridge_001d_resolved": state["post_bridge_001d_readback"].get("resolved") is True,
        "actionability_revalidation_required": state["alignment_contract_readback"].get(
            "actionability_revalidation_required"
        )
        is True,
        "computed_evidence_gate_required": state["alignment_contract_readback"].get(
            "computed_evidence_gate_required_for_future_execution"
        )
        is True,
        "negative_evidence_non_positive": state["negative_evidence_preconditions"].get(
            "negative_001b_001c_positive_downstream_use_allowed"
        )
        is False,
        "authorization_flags": state["authorization_flags"]["authorization_flags"],
        "protected_parent_artifacts_modified": protected_modified,
        "protected_parent_hashes_before": state["protected_parent_hashes_before"],
        "protected_parent_hashes_after": protected_after,
        "duplicate_admission_schema_created": state["schema_duplication"].get("duplicate_admission_schema_created"),
        "copied_45_row_matrix_detected": state["schema_duplication"].get("copied_45_row_matrix_detected"),
        "pre_commit_git_status_scope": {
            "final_clean_status_must_be_verified_after_commit": True,
            "protected_parent_paths_monitored": PROTECTED_INPUTS_AS_POSIX,
        },
        "input_artifacts": state["input_artifacts_by_output"]["result.json"],
        "input_refs_tags_commits": _input_ref_rows(state),
        "run_id": state["run_id"],
        "aggregation_rule": "PASS only when every callable validator passes, every negative control fails, and protected parent hashes are unchanged",
        "code_path_hash": _code_path_hash(build_result),
        "artifacts_generated": [str(ARTIFACT_DIR / name) for name in REQUIRED_ARTIFACT_NAMES],
        "what_this_does_not_prove": FORBIDDEN_CLAIMS,
    }
    return result


def hash_protected_inputs(root: str | Path) -> dict[str, str]:
    root_path = Path(root).resolve()
    hashes = {}
    for path in PROTECTED_INPUTS:
        full = root_path / path
        if full.exists():
            hashes[path.as_posix()] = _sha_file(full)
    return hashes


def _boundary_row(
    root: Path,
    boundary_id: str,
    task_id: str,
    expected_commit: str,
    remote_tag: str | None,
    paths: list[Path],
    verify_remote: bool,
    status: str,
) -> dict[str, Any]:
    local_tag = _git_output(root, ["rev-parse", f"refs/tags/{remote_tag}"]) if remote_tag else None
    remote_commit = _remote_tag_commit(root, remote_tag) if remote_tag and verify_remote else local_tag
    path_commit = _path_last_commit(root, paths)
    remote_tag_required = remote_tag is not None and verify_remote
    local_verified = local_tag == expected_commit if remote_tag else True
    remote_verified = remote_commit == expected_commit if remote_tag else True
    path_verified = path_commit == expected_commit
    return {
        "boundary_id": boundary_id,
        "task_id": task_id,
        "status": status,
        "expected_commit": expected_commit,
        "remote_tag": remote_tag,
        "remote_tag_required": remote_tag_required,
        "local_tag_resolved_commit": local_tag,
        "remote_resolved_commit": remote_commit,
        "path_last_commit": path_commit,
        "paths": [path.as_posix() for path in paths],
        "local_verified": local_verified,
        "remote_verified": remote_verified,
        "path_verified": path_verified,
        "resolved_exactly": local_verified and remote_verified and path_verified,
        "producer_function": "_boundary_row",
        "validation_rule": "local tag, remote tag when checked, and path last commit must match expected sealed commit",
    }


def _mutate_missing_post_bridge(state: dict[str, Any]) -> None:
    post_bridge = state["post_bridge_001d_readback"]
    post_bridge["verdict"] = None
    post_bridge["claim_ceiling"] = ""
    post_bridge["caveats"] = []


def _mutate_blocked_old_canonicalization(state: dict[str, Any]) -> None:
    readback = state["parent_boundary_readback"]
    readback["blocked_old_canonicalization_001a"]["used_as_parent"] = True
    row = readback["parent_boundaries_by_id"]["canonicalization_provenance_repair_001b"]
    row["expected_commit"] = BLOCKED_OLD_CANONICALIZATION_001A_COMMIT


def _mutate_static_pass(state: dict[str, Any]) -> None:
    state["callable_gate_logic_executed"] = False
    state["static_pass_result"] = True


def _mutate_duplicate_schema_and_matrix(state: dict[str, Any]) -> None:
    schema = state["schema_duplication"]
    schema["duplicate_admission_schema_created"] = True
    schema["copied_45_row_matrix_detected"] = True
    schema["copied_matrix_positive_control"] = [{"candidate_id": f"row_{index:02d}"} for index in range(45)]


def _mutate_negative_as_positive(state: dict[str, Any]) -> None:
    negative = state["negative_evidence_preconditions"]
    for row in negative["negative_evidence_rows"]:
        if row.get("task_id") in {"POST-BRIDGE-ADMISSION-EXECUTABLE-001B", "POST-BRIDGE-ADMISSION-EXECUTABLE-001C"}:
            row["positive_evidence_allowed"] = True
    negative["negative_001b_001c_positive_downstream_use_allowed"] = True


def _producer_for_artifact(name: str) -> Callable[..., Any]:
    mapping: dict[str, Callable[..., Any]] = {
        "parent_boundary_readback.json": build_parent_boundary_readback,
        "post_bridge_001d_readback.json": build_post_bridge_001d_readback,
        "alignment_contract_readback.json": build_alignment_contract_readback,
        "actionability_revalidation_preconditions.json": build_actionability_revalidation_preconditions,
        "computed_evidence_preconditions.json": build_computed_evidence_preconditions,
        "negative_evidence_preconditions.json": build_negative_evidence_preconditions,
        "forbidden_claims_and_actions.json": build_forbidden_claims_and_actions,
        "authorization_flags.json": build_authorization_flags,
        "result.json": build_result,
    }
    return mapping[name]


def _aggregation_rule_for_artifact(name: str) -> str:
    return {
        "parent_boundary_readback.json": "resolve parent commits from git refs, remote tags, and path history",
        "post_bridge_001d_readback.json": "parse 001D result and task card from repo state",
        "alignment_contract_readback.json": "parse alignment 001A artifacts for required future-execution preconditions",
        "actionability_revalidation_preconditions.json": "copy only compact actionability requirements from alignment 001A",
        "computed_evidence_preconditions.json": "copy only computed-evidence gate requirements from alignment 001A",
        "negative_evidence_preconditions.json": "preserve negative-evidence rows without upgrading 001B/001C",
        "forbidden_claims_and_actions.json": "enumerate forbidden claims and actions under the preflight claim ceiling",
        "authorization_flags.json": "derive authorization flags from resolved alignment and post-bridge state",
        "result.json": "aggregate callable validators, negative controls, and protected parent hashes",
    }[name]


def _input_ref_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in state["parent_boundary_readback"]["parent_boundaries"]:
        rows.append(
            {
                "boundary_id": row["boundary_id"],
                "task_id": row["task_id"],
                "expected_commit": row["expected_commit"],
                "remote_tag": row["remote_tag"],
                "remote_resolved_commit": row["remote_resolved_commit"],
                "path_last_commit": row["path_last_commit"],
            }
        )
    return rows


def _with_metadata(
    artifact_name: str,
    payload: dict[str, Any],
    producer: Callable[..., Any],
    input_artifacts: list[str],
    input_refs_tags_commits: list[dict[str, Any]],
    run_id: str,
    aggregation_rule: str,
) -> dict[str, Any]:
    payload_copy = copy.deepcopy(payload)
    payload_hash = _payload_hash(payload_copy)
    payload_copy["computed_evidence_provenance"] = {
        "artifact_name": artifact_name,
        "producer_function": producer.__name__,
        "input_artifacts": input_artifacts,
        "input_refs_tags_commits": input_refs_tags_commits,
        "run_id": run_id,
        "aggregation_rule": aggregation_rule,
        "code_path_hash": _code_path_hash(producer),
        "output_artifact_hash": payload_hash,
        "output_hash_scope": "canonical JSON payload before computed_evidence_provenance envelope",
    }
    return payload_copy


def _validator_result(name: str, failures: list[str]) -> dict[str, Any]:
    return {
        "validator": name,
        "passed": not failures,
        "failures": failures,
        "producer_function": name,
        "code_path_hash": _code_path_hash(globals()[name]),
        "aggregation_rule": "collect explicit validation failures",
        "validation_rule": "validator passes only when no failures are emitted",
    }


def _copied_matrix_hits(value: Any, path: str = "$") -> list[str]:
    hits = []
    if (
        isinstance(value, list)
        and len(value) == 45
        and all(isinstance(item, dict) and "candidate_id" in item for item in value)
    ):
        hits.append(path)
    elif isinstance(value, dict):
        for key, item in value.items():
            hits.extend(_copied_matrix_hits(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            hits.extend(_copied_matrix_hits(item, f"{path}[{index}]"))
    return hits


def _walk(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    rows = [(path, value)]
    if isinstance(value, dict):
        for key, item in value.items():
            rows.extend(_walk(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(_walk(item, f"{path}[{index}]"))
    return rows


def _find_row(rows: list[dict[str, Any]], key: str, expected: str) -> dict[str, Any]:
    for row in rows:
        if row.get(key) == expected:
            return row
    return {}


def _run_id(root: Path) -> str:
    seed_parts = [
        TASK_ID,
        ALIGNMENT_001A_COMMIT,
        COVERAGE_REFERENCE_001A_COMMIT,
        CANONICALIZATION_REPAIR_001B_COMMIT,
        COVERAGE_COMPRESSION_001D_COMMIT,
        POST_BRIDGE_001D_COMMIT,
        _sha_file(root / POST_BRIDGE_001D_RESULT) if (root / POST_BRIDGE_001D_RESULT).exists() else "missing",
        _sha_file(root / ALIGNMENT_RESULT) if (root / ALIGNMENT_RESULT).exists() else "missing",
    ]
    return f"ego_mainline_admission_execution_preflight_001a_{_sha_text('|'.join(seed_parts))[:16]}"


def _path_last_commit(root: Path, paths: list[Path]) -> str | None:
    existing = [path.as_posix() for path in paths if (root / path).exists()]
    if not existing:
        return None
    return _git_output(root, ["log", "-1", "--format=%H", "--", *existing]) or None


def _remote_tag_commit(root: Path, tag: str | None) -> str | None:
    if not tag:
        return None
    output = _git_output(root, ["ls-remote", "origin", f"refs/tags/{tag}"])
    if not output:
        return None
    return output.split()[0]


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


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--skip-remote", action="store_true")
    args = parser.parse_args()
    result = run_preflight(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        verify_remote=not args.skip_remote,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
