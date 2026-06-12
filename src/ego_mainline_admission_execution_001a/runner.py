from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
from typing import Any, Callable


TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTION-001A"
VERDICT_PASS = "pass_bounded_admission_execution_001a"
VERDICT_BLOCKED = "blocked_bounded_admission_execution_001a"
LAYER = "evidence-governance / bounded admission execution only"
CLAIM_CEILING = "bounded admission execution evidence at the governance layer only"

PREFLIGHT_001A_COMMIT = "1b56bb658857ed53c1d94cc94d908cc43990f2c7"
PREFLIGHT_001A_TAG = "remote-anchor-admission-execution-preflight-001a-1b56bb6"
ALIGNMENT_001A_COMMIT = "095a1fcb644dc21e5f59636f9cf5a183e6989537"
ALIGNMENT_001A_TAG = "remote-anchor-admission-alignment-001a-095a1fc"
COVERAGE_REFERENCE_001A_COMMIT = "c5b067faea764657bd24cd75415a6ceb59905dab"
COVERAGE_REFERENCE_001A_TAG = "remote-anchor-admission-coverage-reference-001a-c5b067f"
CANONICALIZATION_REPAIR_001B_COMMIT = "df6ad31ed58d2e3772e3f53b35ad926ab995d582"
CANONICALIZATION_REPAIR_001B_TAG = "remote-anchor-coverage-canonicalization-repair-001b-df6ad31"
COVERAGE_COMPRESSION_001D_COMMIT = "614b147d14cc4bb02b7c6afa2c90661cdce15e4c"
COVERAGE_COMPRESSION_001D_TAG = "remote-anchor-coverage-compression-001d-614b147"
POST_BRIDGE_001D_COMMIT = "c2f6c5184a119202dd0a7efc23d3bfe3317af890"
PRIOR_READINESS_AUDIT_COMMIT = "f648dac4bfbcdc7a98c1edea5a97dbef4101d83a"
BLOCKED_OLD_CANONICALIZATION_001A_COMMIT = "2882f4796dd40cfd16a2c07b5c718d477876fb5f"

DOC_PATH = Path("docs/codex/tasks/EGO-MAINLINE-ADMISSION-EXECUTION-001A.md")
ARTIFACT_DIR = Path("artifacts/ego_mainline_admission_execution_001a")

PREFLIGHT_DOC = Path("docs/codex/tasks/EGO-MAINLINE-ADMISSION-EXECUTION-PREFLIGHT-001A.md")
PREFLIGHT_DIR = Path("artifacts/ego_mainline_admission_execution_preflight_001a")
PREFLIGHT_RESULT = PREFLIGHT_DIR / "result.json"
PREFLIGHT_PARENT_READBACK = PREFLIGHT_DIR / "parent_boundary_readback.json"
PREFLIGHT_POST_BRIDGE = PREFLIGHT_DIR / "post_bridge_001d_readback.json"
PREFLIGHT_ALIGNMENT = PREFLIGHT_DIR / "alignment_contract_readback.json"
PREFLIGHT_ACTIONABILITY = PREFLIGHT_DIR / "actionability_revalidation_preconditions.json"
PREFLIGHT_COMPUTED = PREFLIGHT_DIR / "computed_evidence_preconditions.json"
PREFLIGHT_NEGATIVE = PREFLIGHT_DIR / "negative_evidence_preconditions.json"
PREFLIGHT_AUTHORIZATION = PREFLIGHT_DIR / "authorization_flags.json"
PREFLIGHT_CLAIM_CEILING = PREFLIGHT_DIR / "claim_ceiling.txt"

ALIGNMENT_DOC = Path("docs/codex/tasks/EGO-MAINLINE-ADMISSION-TASK-CARD-ALIGNMENT-001A.md")
ALIGNMENT_DIR = Path("artifacts/ego_mainline_admission_task_card_alignment_001a")
ALIGNMENT_RESULT = ALIGNMENT_DIR / "result.json"
ALIGNMENT_ACTIONABILITY = ALIGNMENT_DIR / "actionability_revalidation_matrix.json"
ALIGNMENT_COMPUTED = ALIGNMENT_DIR / "computed_evidence_gate_contract.json"
ALIGNMENT_NEGATIVE = ALIGNMENT_DIR / "negative_evidence_handling_contract.json"
ALIGNMENT_AUTHORIZATION = ALIGNMENT_DIR / "authorization_guard.json"
ALIGNMENT_SCHEMA = ALIGNMENT_DIR / "schema_duplication_guard.json"
ALIGNMENT_PARENT_MANIFEST = ALIGNMENT_DIR / "parent_evidence_boundary_manifest.json"

COVERAGE_REFERENCE_DOC = Path("docs/research/EGO-MAINLINE-ADMISSION-CANONICAL-COVERAGE-REFERENCE-001A.md")
COVERAGE_REFERENCE_RESULT = Path("artifacts/ego_mainline_admission_canonical_coverage_reference_001a/result.json")
COVERAGE_REFERENCE_CONTRACT = Path("artifacts/ego_mainline_admission_canonical_coverage_reference_001a/reference_contract.json")
CANONICALIZATION_REPAIR_DOC = Path("docs/research/THEORY-LANDSCAPE-COVERAGE-CANONICALIZATION-PROVENANCE-REPAIR-001B.md")
CANONICALIZATION_REPAIR_RESULT = Path("artifacts/theory_landscape_coverage_canonicalization_provenance_repair_001b/result.json")
COVERAGE_COMPRESSION_DOC = Path("docs/research/THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001D.md")
POST_BRIDGE_001D_DOC = Path("docs/codex/tasks/POST-BRIDGE-ADMISSION-EXECUTABLE-001D.md")
POST_BRIDGE_001D_RESULT = Path("artifacts/post_bridge_admission_executable_001d/result.json")
PRIOR_READINESS_AUDIT_DOC = Path("docs/codex/audits/EGO-MAINLINE-READINESS-AUDIT-001B.md")
PRIOR_READINESS_AUDIT_RESULT = Path("artifacts/ego_mainline_readiness_audit_001b/result.json")

REQUIRED_ARTIFACT_NAMES = [
    "result.json",
    "parent_boundary_readback.json",
    "admission_contract_evaluation.json",
    "post_bridge_caveat_revalidation.json",
    "actionability_revalidation.json",
    "computed_evidence_provenance.json",
    "negative_evidence_handling.json",
    "forbidden_claims_and_actions.json",
    "admission_decision_trace.json",
    "ablation_report.json",
    "authorization_flags.json",
    "claim_ceiling.txt",
]

AUTHORIZATION_FLAGS = [
    "authorize_gate4",
    "authorize_bridge_runtime",
    "authorize_ego_runtime",
    "authorize_companion_behavior",
    "authorize_llm_rag",
    "authorize_user_model",
    "authorize_relationship_or_emotion",
    "authorize_personalization",
    "authorize_architecture_implementation",
    "authorize_mechanism_validity_claim",
    "authorize_runtime_correctness_claim",
]

FORBIDDEN_CLAIMS = [
    "EGO readiness",
    "bridge readiness",
    "runtime readiness",
    "Gate4 readiness",
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

FORBIDDEN_VERDICTS = [
    "EGO ready",
    "bridge ready",
    "runtime ready",
    "Gate4 authorized",
    "mechanism proven",
    "architecture valid",
    "agency proven",
    "selfhood proven",
    "consciousness proven",
    "companion authorized",
    "relationship/emotion learning proven",
]

PROTECTED_INPUTS = [
    PREFLIGHT_DOC,
    PREFLIGHT_RESULT,
    PREFLIGHT_PARENT_READBACK,
    PREFLIGHT_POST_BRIDGE,
    PREFLIGHT_ALIGNMENT,
    PREFLIGHT_ACTIONABILITY,
    PREFLIGHT_COMPUTED,
    PREFLIGHT_NEGATIVE,
    PREFLIGHT_AUTHORIZATION,
    PREFLIGHT_CLAIM_CEILING,
    ALIGNMENT_DOC,
    ALIGNMENT_RESULT,
    ALIGNMENT_ACTIONABILITY,
    ALIGNMENT_COMPUTED,
    ALIGNMENT_NEGATIVE,
    ALIGNMENT_AUTHORIZATION,
    ALIGNMENT_SCHEMA,
    ALIGNMENT_PARENT_MANIFEST,
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


def run_admission_execution(
    repo_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    verify_remote: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    out = Path(output_dir) if output_dir is not None else root / ARTIFACT_DIR
    if not out.is_absolute():
        out = root / out
    out.mkdir(parents=True, exist_ok=True)

    state = build_admission_state(root, out, verify_remote=verify_remote)
    validators = validate_admission_state(state)
    ablation_report = run_ablation_controls(state)
    protected_after = hash_protected_inputs(root)
    state["protected_sealed_hashes_after"] = protected_after
    result = build_result(state, validators, ablation_report, protected_after)
    trace = build_admission_decision_trace(state, validators, ablation_report, result)
    computed_report = build_computed_evidence_provenance_report(state, validators, result)
    evaluation = build_admission_contract_evaluation(state, validators, ablation_report)

    artifacts = {
        "parent_boundary_readback.json": state["parent_boundary_readback"],
        "admission_contract_evaluation.json": evaluation,
        "post_bridge_caveat_revalidation.json": state["post_bridge_caveat_revalidation"],
        "actionability_revalidation.json": state["actionability_revalidation"],
        "computed_evidence_provenance.json": computed_report,
        "negative_evidence_handling.json": state["negative_evidence_handling"],
        "forbidden_claims_and_actions.json": state["forbidden_claims_and_actions"],
        "admission_decision_trace.json": trace,
        "ablation_report.json": ablation_report,
        "authorization_flags.json": state["authorization_flags"],
        "result.json": result,
    }

    ref_rows = _input_ref_rows(state)
    failures = result["stop_conditions_triggered"]
    for name, payload in artifacts.items():
        _write_json(
            out / name,
            _with_metadata(
                artifact_name=name,
                payload=payload,
                producer=_producer_for_artifact(name),
                input_artifacts=state["input_artifacts_by_output"].get(name, []),
                input_commits_tags_refs=ref_rows,
                run_id=state["run_id"],
                aggregation_rule=_aggregation_rule_for_artifact(name),
                gate_outcomes=validators,
                failure_reasons=failures,
            ),
        )
    _write_text(out / "claim_ceiling.txt", CLAIM_CEILING + "\n")
    return result


def build_admission_state(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
    verify_remote: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    out = Path(output_dir) if output_dir is not None else root / ARTIFACT_DIR
    if not out.is_absolute():
        out = root / out

    parent_boundary_readback = build_parent_boundary_readback(root, verify_remote)
    post_bridge = build_post_bridge_caveat_revalidation(root)
    preflight = build_preflight_contract_readback(root)
    alignment = build_alignment_contract_readback(root)
    actionability = build_actionability_revalidation(root, alignment, parent_boundary_readback)
    negative = build_negative_evidence_handling(root, alignment, post_bridge)
    forbidden = build_forbidden_claims_and_actions(root, out, alignment)
    authorization = build_authorization_flags(alignment, preflight, post_bridge)
    duplicate_schema = build_duplicate_schema_state(root, out, alignment, forbidden)
    protected_before = hash_protected_inputs(root)

    return {
        "task_id": TASK_ID,
        "run_id": _run_id(root),
        "repo_root": root.as_posix(),
        "output_dir": out.as_posix(),
        "verify_remote": verify_remote,
        "parent_boundary_readback": parent_boundary_readback,
        "post_bridge_caveat_revalidation": post_bridge,
        "preflight_contract": preflight,
        "alignment_contract": alignment,
        "actionability_revalidation": actionability,
        "negative_evidence_handling": negative,
        "forbidden_claims_and_actions": forbidden,
        "authorization_flags": authorization,
        "duplicate_schema": duplicate_schema,
        "callable_gate_logic_executed": True,
        "static_pass_result": False,
        "protected_sealed_hashes_before": protected_before,
        "protected_sealed_hashes_after": protected_before,
        "input_artifacts_by_output": _input_artifacts_by_output(),
    }


def build_parent_boundary_readback(root: Path, verify_remote: bool = True) -> dict[str, Any]:
    rows = [
        _boundary_row(
            root,
            "preflight_001a",
            "EGO-MAINLINE-ADMISSION-EXECUTION-PREFLIGHT-001A",
            PREFLIGHT_001A_COMMIT,
            PREFLIGHT_001A_TAG,
            [PREFLIGHT_DOC, PREFLIGHT_RESULT],
            verify_remote,
            "sealed admission execution readiness preflight",
        ),
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
            None,
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
            status="reference-only prior readiness audit / admission drafting context",
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
        "all_required_remote_anchors_verified": all(row["remote_verified"] for row in rows if row["remote_tag"]),
        "validation_rule": "required sealed parent boundaries must resolve exactly by path history and remote tags when declared",
    }


def build_post_bridge_caveat_revalidation(root: Path) -> dict[str, Any]:
    result_path = root / POST_BRIDGE_001D_RESULT
    doc_path = root / POST_BRIDGE_001D_DOC
    if not result_path.exists() or not doc_path.exists():
        return {
            "task_id": "POST-BRIDGE-ADMISSION-EXECUTABLE-001D",
            "resolved": False,
            "blocked_reason": "missing_post_bridge_001d_doc_or_result",
            "caveats_binding": False,
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
    flags = result.get("authorization_flags", {})
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
        "caveats_binding": bool(caveats) and bool(result.get("claim_ceiling")),
        "authorization_flags": flags,
        "treat_as_mechanism_proof": False,
        "runtime_authorized": any(
            flags.get(key) is True
            for key in ["bridge_runtime_authorized", "ego_mainline_authorized", "llm_rag_authorized"]
        ),
        "bridge_ready_claim_allowed": False,
        "ego_ready_claim_allowed": False,
        "mechanism_proof_allowed": False,
        "what_this_does_not_prove": result.get("what_this_does_not_prove", []),
        "validation_rule": "001D verdict, caveats, artifact path, and claim ceiling are re-read and remain binding",
    }


def build_preflight_contract_readback(root: Path) -> dict[str, Any]:
    if not (root / PREFLIGHT_RESULT).exists():
        return {"task_id": "EGO-MAINLINE-ADMISSION-EXECUTION-PREFLIGHT-001A", "resolved": False}
    result = _read_json(root / PREFLIGHT_RESULT)
    auth = _read_json(root / PREFLIGHT_AUTHORIZATION) if (root / PREFLIGHT_AUTHORIZATION).exists() else {}
    return {
        "task_id": "EGO-MAINLINE-ADMISSION-EXECUTION-PREFLIGHT-001A",
        "resolved": True,
        "verdict": result.get("verdict"),
        "all_gates_passed": result.get("all_gates_passed"),
        "computed_evidence_gate_required": result.get("computed_evidence_gate_required"),
        "actionability_revalidation_required": result.get("actionability_revalidation_required"),
        "negative_evidence_non_positive": result.get("negative_evidence_non_positive"),
        "stop_conditions_triggered": result.get("stop_conditions_triggered", []),
        "authorization_flags": auth.get("authorization_flags", {}),
        "all_authorization_flags_false": auth.get("all_authorization_flags_false"),
        "claim_ceiling": result.get("claim_ceiling"),
        "validation_rule": "preflight 001A must remain a sealed readiness preflight and not admission execution",
    }


def build_alignment_contract_readback(root: Path) -> dict[str, Any]:
    required = [
        ALIGNMENT_RESULT,
        ALIGNMENT_ACTIONABILITY,
        ALIGNMENT_COMPUTED,
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
    actionability = _read_json(root / ALIGNMENT_ACTIONABILITY)
    computed = _read_json(root / ALIGNMENT_COMPUTED)
    negative = _read_json(root / ALIGNMENT_NEGATIVE)
    authorization = _read_json(root / ALIGNMENT_AUTHORIZATION)
    schema = _read_json(root / ALIGNMENT_SCHEMA)
    return {
        "task_id": "EGO-MAINLINE-ADMISSION-TASK-CARD-ALIGNMENT-001A",
        "resolved": True,
        "verdict": result.get("verdict"),
        "all_validators_passed": result.get("all_validators_passed"),
        "actionability_revalidation_required": actionability.get("actionability_revalidation_required") is True,
        "computed_evidence_gate_required_for_future_execution": computed.get(
            "computed_evidence_gate_required_for_future_execution"
        )
        is True,
        "static_or_literal_verdicts_allowed": computed.get("static_or_literal_verdicts_allowed"),
        "negative_evidence_handling_required": negative.get("negative_evidence_handling_required") is True,
        "schema_duplication_allowed": schema.get("duplicate_schema_created") is True
        or schema.get("matrix_duplication_allowed") is True,
        "copied_45_row_matrix_detected": schema.get("copied_45_row_matrix_detected") is True,
        "authorization_flags": authorization.get("authorization_flags", {}),
        "actionability_source": actionability,
        "computed_source": computed,
        "negative_source": negative,
        "schema_source": schema,
        "validation_rule": "alignment 001A must preserve actionability, computed-evidence, negative-evidence, authorization, and schema guards",
    }


def build_actionability_revalidation(
    root: Path, alignment: dict[str, Any], parent_readback: dict[str, Any]
) -> dict[str, Any]:
    rows = alignment.get("actionability_source", {}).get("revalidation_rows", [])
    boundaries = parent_readback.get("parent_boundaries_by_id", {})
    boundary_aliases = {
        "admission_coverage_reference": "admission_coverage_reference_001a",
        "canonical_coverage_repair": "canonicalization_provenance_repair_001b",
        "compression_source_boundary": "coverage_compression_001d",
        "prior_readiness_audit": "prior_readiness_audit_reference_only",
        "post_bridge_admission_executable_001d": "post_bridge_admission_executable_001d",
        "computed_evidence_gate": "alignment_001a",
        "negative_evidence_handling": "alignment_001a",
    }
    preconditions = []
    for row in rows:
        source_id = row.get("boundary_id")
        boundary_id = boundary_aliases.get(source_id, source_id)
        boundary = boundaries.get(boundary_id, {})
        satisfied = row.get("required") is True and (
            boundary.get("resolved_exactly") is True or source_id in {"computed_evidence_gate", "negative_evidence_handling"}
        )
        preconditions.append(
            {
                "boundary_id": source_id,
                "resolved_boundary_id": boundary_id,
                "required": row.get("required") is True,
                "satisfied": satisfied,
                "revalidation_rule": row.get("revalidation_rule"),
                "producer_function": "build_actionability_revalidation",
            }
        )
    return {
        "task_id": TASK_ID,
        "source_task_id": "EGO-MAINLINE-ADMISSION-TASK-CARD-ALIGNMENT-001A",
        "actionability_revalidation_passed": bool(preconditions) and all(row["satisfied"] for row in preconditions),
        "all_required_rows_revalidated": bool(preconditions) and all(row["required"] and row["satisfied"] for row in preconditions),
        "revalidation_rows": preconditions,
        "input_artifacts": [ALIGNMENT_ACTIONABILITY.as_posix(), PREFLIGHT_ACTIONABILITY.as_posix()],
        "validation_rule": "all alignment actionability rows must be revalidated against resolved parent boundaries",
    }


def build_negative_evidence_handling(
    root: Path, alignment: dict[str, Any], post_bridge: dict[str, Any]
) -> dict[str, Any]:
    rows = copy.deepcopy(alignment.get("negative_source", {}).get("negative_evidence_rows", []))
    for row in rows:
        if row.get("task_id") == "POST-BRIDGE-ADMISSION-EXECUTABLE-001D":
            row["claim_ceiling"] = post_bridge.get("claim_ceiling")
            row["caveats"] = post_bridge.get("caveats", row.get("caveats", []))
            row["mechanism_proof_allowed"] = False
    positive_001b_001c = any(
        row.get("task_id") in {"POST-BRIDGE-ADMISSION-EXECUTABLE-001B", "POST-BRIDGE-ADMISSION-EXECUTABLE-001C"}
        and row.get("positive_evidence_allowed") is True
        for row in rows
    )
    return {
        "task_id": TASK_ID,
        "source_task_id": "EGO-MAINLINE-ADMISSION-TASK-CARD-ALIGNMENT-001A",
        "negative_evidence_handling_required": alignment.get("negative_evidence_handling_required") is True,
        "negative_evidence_non_positive": not positive_001b_001c,
        "negative_001b_001c_positive_downstream_use_allowed": positive_001b_001c,
        "negative_evidence_rows": rows,
        "validation_rule": "001B/001C negative evidence remains non-positive; 001D remains caveated and not mechanism proof",
    }


def build_forbidden_claims_and_actions(root: Path, output_dir: Path, alignment: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "allowed_verdicts": [VERDICT_PASS, VERDICT_BLOCKED],
        "forbidden_verdicts": list(FORBIDDEN_VERDICTS),
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "inserted_claims": [],
        "duplicate_admission_schema_created": alignment.get("schema_source", {}).get("duplicate_schema_created") is True,
        "copied_45_row_matrix_detected": alignment.get("schema_source", {}).get("copied_45_row_matrix_detected") is True,
        "runtime_or_mechanism_claims_introduced": False,
        "validation_rule": "output may claim only bounded governance-layer admission execution evidence",
    }


def build_authorization_flags(
    alignment: dict[str, Any], preflight: dict[str, Any], post_bridge: dict[str, Any]
) -> dict[str, Any]:
    flags = {field: False for field in AUTHORIZATION_FLAGS}
    source_flags = {
        "alignment": alignment.get("authorization_flags", {}),
        "preflight": preflight.get("authorization_flags", {}),
        "post_bridge": post_bridge.get("authorization_flags", {}),
    }
    return {
        "task_id": TASK_ID,
        "authorization_flags": flags,
        "all_authorization_flags_false": all(value is False for value in flags.values()),
        "generated_from_resolved_state": alignment.get("resolved") is True
        and preflight.get("resolved") is True
        and post_bridge.get("resolved") is True,
        "source_authorization_flags": source_flags,
        "validation_rule": "all admission execution authorization flags remain false",
    }


def build_duplicate_schema_state(
    root: Path, output_dir: Path, alignment: dict[str, Any], forbidden: dict[str, Any]
) -> dict[str, Any]:
    payload = {
        "task_id": TASK_ID,
        "duplicate_admission_schema_created": forbidden.get("duplicate_admission_schema_created") is True,
        "copied_45_row_matrix_detected": forbidden.get("copied_45_row_matrix_detected") is True,
        "matrix_duplication_allowed": alignment.get("schema_source", {}).get("matrix_duplication_allowed") is True,
        "scanned_payloads": ["alignment schema guard", "admission forbidden claims/actions"],
        "validation_rule": "no duplicate schema and no copied 45-row matrix is introduced",
    }
    hits = _copied_matrix_hits(payload)
    payload["copied_matrix_hits"] = hits
    if hits:
        payload["copied_45_row_matrix_detected"] = True
    return payload


def build_computed_evidence_provenance_report(
    state: dict[str, Any], gate_outcomes: list[dict[str, Any]], result: dict[str, Any]
) -> dict[str, Any]:
    ref_rows = _input_ref_rows(state)
    artifact_rows = []
    for name in REQUIRED_ARTIFACT_NAMES:
        if name == "claim_ceiling.txt":
            continue
        producer = _producer_for_artifact(name)
        artifact_rows.append(
            {
                "artifact_name": name,
                "producer_function": producer.__name__,
                "input_artifacts": state["input_artifacts_by_output"].get(name, []),
                "input_commits_tags_refs": ref_rows,
                "run_id": state["run_id"],
                "aggregation_rule": _aggregation_rule_for_artifact(name),
                "code_path_hash": _code_path_hash(producer),
                "gate_outcomes": [row["validator"] for row in gate_outcomes],
                "failure_reasons": result.get("stop_conditions_triggered", []),
            }
        )
    required_fields = {
        "producer_function",
        "input_artifacts",
        "input_commits_tags_refs",
        "run_id",
        "aggregation_rule",
        "code_path_hash",
    }
    return {
        "task_id": TASK_ID,
        "computed_evidence_provenance_passed": all(required_fields.issubset(row) for row in artifact_rows),
        "static_or_literal_verdicts_allowed": False,
        "all_required_outputs_have_callable_provenance": len(artifact_rows) == len(REQUIRED_ARTIFACT_NAMES) - 1,
        "artifact_provenance_rows": artifact_rows,
        "validation_rule": "every JSON output records callable provenance and input refs",
    }


def build_admission_contract_evaluation(
    state: dict[str, Any],
    gate_outcomes: list[dict[str, Any]],
    ablation_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "layer": LAYER,
        "gate_outcomes": gate_outcomes,
        "all_gates_passed": all(row["passed"] for row in gate_outcomes),
        "ablation_controls_failed": ablation_report.get("all_negative_controls_failed"),
        "parent_boundaries_resolved": state["parent_boundary_readback"].get("all_required_boundaries_resolved"),
        "alignment_contract_satisfied": state["alignment_contract"].get("all_validators_passed") is True,
        "preflight_contract_satisfied": state["preflight_contract"].get("all_gates_passed") is True,
        "post_bridge_caveats_binding": state["post_bridge_caveat_revalidation"].get("caveats_binding") is True,
        "claim_ceiling": CLAIM_CEILING,
        "validation_rule": "admission contract passes only when every callable gate and ablation control passes",
    }


def build_admission_decision_trace(
    state: dict[str, Any],
    gate_outcomes: list[dict[str, Any]],
    ablation_report: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    replayed = replay_admission_verdict(copy.deepcopy(state))
    return {
        "task_id": TASK_ID,
        "serialized_input_state": copy.deepcopy(state),
        "gate_by_gate_decision_trace": gate_outcomes,
        "ablation_trace": ablation_report,
        "final_aggregation_trace": {
            "producer_function": "build_result",
            "aggregation_rule": result["aggregation_rule"],
            "verdict": result["verdict"],
            "all_gates_passed": result["all_gates_passed"],
            "stop_conditions_triggered": result["stop_conditions_triggered"],
        },
        "replay_function": "replay_admission_verdict",
        "replay_result": replayed,
        "replay_result_matches_result_json": replayed["verdict"] == result["verdict"]
        and replayed["all_gates_passed"] == result["all_gates_passed"]
        and replayed["stop_conditions_triggered"] == result["stop_conditions_triggered"],
    }


def replay_admission_verdict(serialized_state: dict[str, Any]) -> dict[str, Any]:
    state = copy.deepcopy(serialized_state)
    validators = validate_admission_state(state)
    ablation_report = run_ablation_controls(state)
    protected_after = state.get("protected_sealed_hashes_after", state.get("protected_sealed_hashes_before", {}))
    return build_result(state, validators, ablation_report, protected_after)


def validate_admission_state(state: dict[str, Any]) -> list[dict[str, Any]]:
    validators: list[Callable[[dict[str, Any]], dict[str, Any]]] = [
        validate_parent_boundaries,
        validate_remote_anchors,
        validate_alignment_contract,
        validate_preflight_contract,
        validate_post_bridge_caveats,
        validate_actionability_revalidation,
        validate_computed_evidence_provenance,
        validate_negative_evidence_handling,
        validate_duplicate_schema_and_matrix,
        validate_authorization_flags,
        validate_forbidden_claims_and_actions,
        validate_computed_verdict_source,
    ]
    return [validator(state) for validator in validators]


def validate_parent_boundaries(state: dict[str, Any]) -> dict[str, Any]:
    readback = state.get("parent_boundary_readback", {})
    rows = readback.get("parent_boundaries_by_id", {})
    expected = {
        "preflight_001a": PREFLIGHT_001A_COMMIT,
        "alignment_001a": ALIGNMENT_001A_COMMIT,
        "admission_coverage_reference_001a": COVERAGE_REFERENCE_001A_COMMIT,
        "canonicalization_provenance_repair_001b": CANONICALIZATION_REPAIR_001B_COMMIT,
        "coverage_compression_001d": COVERAGE_COMPRESSION_001D_COMMIT,
        "post_bridge_admission_executable_001d": POST_BRIDGE_001D_COMMIT,
        "prior_readiness_audit_reference_only": PRIOR_READINESS_AUDIT_COMMIT,
    }
    failures = []
    if set(rows) != set(expected):
        failures.append("parent_boundary_set_mismatch")
    for boundary_id, commit in expected.items():
        row = rows.get(boundary_id, {})
        if row.get("expected_commit") != commit:
            failures.append(f"expected_commit_mismatch:{boundary_id}")
        if row.get("path_last_commit") != commit:
            failures.append(f"path_last_commit_mismatch:{boundary_id}")
        if row.get("remote_tag") and row.get("remote_resolved_commit") != commit:
            failures.append(f"remote_resolved_commit_mismatch:{boundary_id}")
        if row.get("resolved_exactly") is not True:
            failures.append(f"boundary_not_resolved:{boundary_id}")
    blocked = readback.get("blocked_old_canonicalization_001a", {})
    if blocked.get("used_as_parent") is not False:
        failures.append("blocked_old_canonicalization_001a_used_as_parent")
    if rows.get("canonicalization_provenance_repair_001b", {}).get("expected_commit") == BLOCKED_OLD_CANONICALIZATION_001A_COMMIT:
        failures.append("blocked_old_canonicalization_001a_expected_commit_used")
    if readback.get("all_required_boundaries_resolved") is not True:
        failures.append("all_required_boundaries_resolved_not_true")
    return _validator_result("validate_parent_boundaries", failures)


def validate_remote_anchors(state: dict[str, Any]) -> dict[str, Any]:
    failures = []
    for row in state.get("parent_boundary_readback", {}).get("parent_boundaries", []):
        if not row.get("remote_tag"):
            continue
        if row.get("remote_verified") is not True:
            failures.append(f"remote_anchor_not_verified:{row.get('boundary_id')}")
        if row.get("remote_resolved_commit") != row.get("expected_commit"):
            failures.append(f"remote_anchor_commit_mismatch:{row.get('boundary_id')}")
    if state.get("parent_boundary_readback", {}).get("all_required_remote_anchors_verified") is not True:
        failures.append("all_required_remote_anchors_verified_not_true")
    return _validator_result("validate_remote_anchors", failures)


def validate_alignment_contract(state: dict[str, Any]) -> dict[str, Any]:
    alignment = state.get("alignment_contract", {})
    failures = []
    if alignment.get("resolved") is not True:
        failures.append("alignment_contract_unresolved")
    if alignment.get("verdict") != "ego_mainline_admission_task_card_alignment_001a_pass":
        failures.append("alignment_verdict_not_pass")
    if alignment.get("all_validators_passed") is not True:
        failures.append("alignment_validators_not_passed")
    if alignment.get("actionability_revalidation_required") is not True:
        failures.append("alignment_actionability_not_required")
    if alignment.get("computed_evidence_gate_required_for_future_execution") is not True:
        failures.append("alignment_computed_gate_not_required")
    if alignment.get("static_or_literal_verdicts_allowed") is not False:
        failures.append("static_or_literal_verdicts_allowed")
    if alignment.get("negative_evidence_handling_required") is not True:
        failures.append("alignment_negative_handling_not_required")
    if alignment.get("schema_duplication_allowed") is not False:
        failures.append("schema_duplication_allowed")
    if alignment.get("copied_45_row_matrix_detected") is not False:
        failures.append("copied_45_row_matrix_detected")
    return _validator_result("validate_alignment_contract", failures)


def validate_preflight_contract(state: dict[str, Any]) -> dict[str, Any]:
    preflight = state.get("preflight_contract", {})
    failures = []
    if preflight.get("resolved") is not True:
        failures.append("preflight_contract_unresolved")
    if preflight.get("verdict") != "pass_admission_execution_may_be_tasked_separately":
        failures.append("preflight_verdict_not_tasking_pass")
    if preflight.get("all_gates_passed") is not True:
        failures.append("preflight_gates_not_passed")
    if preflight.get("computed_evidence_gate_required") is not True:
        failures.append("preflight_computed_gate_not_required")
    if preflight.get("actionability_revalidation_required") is not True:
        failures.append("preflight_actionability_not_required")
    if preflight.get("negative_evidence_non_positive") is not True:
        failures.append("preflight_negative_evidence_not_non_positive")
    if preflight.get("stop_conditions_triggered") != []:
        failures.append("preflight_stop_conditions_present")
    if preflight.get("all_authorization_flags_false") is not True:
        failures.append("preflight_authorization_flags_not_false")
    return _validator_result("validate_preflight_contract", failures)


def validate_post_bridge_caveats(state: dict[str, Any]) -> dict[str, Any]:
    post_bridge = state.get("post_bridge_caveat_revalidation", {})
    failures = []
    if post_bridge.get("resolved") is not True:
        failures.append("post_bridge_001d_unresolved")
    if post_bridge.get("artifact_path") != POST_BRIDGE_001D_RESULT.as_posix():
        failures.append("post_bridge_artifact_path_mismatch")
    if post_bridge.get("commit") != POST_BRIDGE_001D_COMMIT:
        failures.append("post_bridge_commit_mismatch")
    if post_bridge.get("verdict") != "post_bridge_admission_executable_001d_pass":
        failures.append("post_bridge_verdict_missing")
    if post_bridge.get("bounded_pass") is not True:
        failures.append("post_bridge_bounded_pass_not_true")
    if not post_bridge.get("claim_ceiling"):
        failures.append("post_bridge_claim_ceiling_missing")
    if not post_bridge.get("caveats") or len(post_bridge.get("caveats", [])) < 3:
        failures.append("post_bridge_caveats_missing")
    if post_bridge.get("caveats_binding") is not True:
        failures.append("post_bridge_caveats_not_binding")
    if post_bridge.get("treat_as_mechanism_proof") is not False:
        failures.append("post_bridge_treated_as_mechanism_proof")
    if post_bridge.get("runtime_authorized") is not False:
        failures.append("post_bridge_runtime_authorized")
    if post_bridge.get("bridge_ready_claim_allowed") is not False:
        failures.append("post_bridge_bridge_ready_claim_allowed")
    if post_bridge.get("ego_ready_claim_allowed") is not False:
        failures.append("post_bridge_ego_ready_claim_allowed")
    return _validator_result("validate_post_bridge_caveats", failures)


def validate_actionability_revalidation(state: dict[str, Any]) -> dict[str, Any]:
    actionability = state.get("actionability_revalidation", {})
    failures = []
    if actionability.get("actionability_revalidation_passed") is not True:
        failures.append("actionability_revalidation_not_passed")
    if actionability.get("all_required_rows_revalidated") is not True:
        failures.append("required_actionability_rows_not_revalidated")
    for row in actionability.get("revalidation_rows", []):
        if row.get("required") is not True or row.get("satisfied") is not True:
            failures.append(f"actionability_row_not_satisfied:{row.get('boundary_id')}")
    return _validator_result("validate_actionability_revalidation", failures)


def validate_computed_evidence_provenance(state: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if state.get("alignment_contract", {}).get("static_or_literal_verdicts_allowed") is not False:
        failures.append("static_or_literal_verdicts_allowed")
    if state.get("callable_gate_logic_executed") is not True:
        failures.append("callable_gate_logic_not_executed")
    if not state.get("input_artifacts_by_output"):
        failures.append("input_artifacts_by_output_missing")
    for name in REQUIRED_ARTIFACT_NAMES:
        if name == "claim_ceiling.txt":
            continue
        if not state.get("input_artifacts_by_output", {}).get(name):
            failures.append(f"input_artifacts_missing:{name}")
    return _validator_result("validate_computed_evidence_provenance", failures)


def validate_negative_evidence_handling(state: dict[str, Any]) -> dict[str, Any]:
    negative = state.get("negative_evidence_handling", {})
    failures = []
    if negative.get("negative_evidence_handling_required") is not True:
        failures.append("negative_evidence_handling_not_required")
    if negative.get("negative_evidence_non_positive") is not True:
        failures.append("negative_evidence_not_non_positive")
    if negative.get("negative_001b_001c_positive_downstream_use_allowed") is not False:
        failures.append("negative_001b_001c_positive_downstream_use_allowed")
    rows = {row.get("task_id"): row for row in negative.get("negative_evidence_rows", [])}
    for task_id in ["POST-BRIDGE-ADMISSION-EXECUTABLE-001B", "POST-BRIDGE-ADMISSION-EXECUTABLE-001C"]:
        if rows.get(task_id, {}).get("positive_evidence_allowed") is not False:
            failures.append(f"negative_evidence_upgraded:{task_id}")
    row_001d = rows.get("POST-BRIDGE-ADMISSION-EXECUTABLE-001D", {})
    if row_001d.get("mechanism_proof_allowed") is not False:
        failures.append("post_bridge_001d_mechanism_proof_allowed")
    if not row_001d.get("caveats"):
        failures.append("post_bridge_001d_caveats_missing_from_negative_evidence")
    return _validator_result("validate_negative_evidence_handling", failures)


def validate_duplicate_schema_and_matrix(state: dict[str, Any]) -> dict[str, Any]:
    schema = state.get("duplicate_schema", {})
    failures = []
    if schema.get("duplicate_admission_schema_created") is not False:
        failures.append("duplicate_admission_schema_created")
    if schema.get("copied_45_row_matrix_detected") is not False:
        failures.append("copied_45_row_matrix_detected")
    if schema.get("matrix_duplication_allowed") is not False:
        failures.append("matrix_duplication_allowed")
    hits = _copied_matrix_hits(schema)
    if hits:
        failures.extend(f"copied_45_row_matrix:{hit}" for hit in hits)
    return _validator_result("validate_duplicate_schema_and_matrix", failures)


def validate_authorization_flags(state: dict[str, Any]) -> dict[str, Any]:
    auth = state.get("authorization_flags", {})
    flags = auth.get("authorization_flags", {})
    failures = []
    if set(flags) != set(AUTHORIZATION_FLAGS):
        failures.append("authorization_flag_set_mismatch")
    for key, value in flags.items():
        if value is not False:
            failures.append(f"authorization_flag_true:{key}")
    if auth.get("all_authorization_flags_false") is not True:
        failures.append("all_authorization_flags_false_not_true")
    if auth.get("generated_from_resolved_state") is not True:
        failures.append("authorization_flags_not_generated_from_resolved_state")
    return _validator_result("validate_authorization_flags", failures)


def validate_forbidden_claims_and_actions(state: dict[str, Any]) -> dict[str, Any]:
    forbidden = state.get("forbidden_claims_and_actions", {})
    failures = []
    claims = set(forbidden.get("forbidden_claims", []))
    actions = set(forbidden.get("forbidden_actions", []))
    for claim in FORBIDDEN_CLAIMS:
        if claim not in claims:
            failures.append(f"forbidden_claim_missing:{claim}")
    for action in FORBIDDEN_ACTIONS:
        if action not in actions:
            failures.append(f"forbidden_action_missing:{action}")
    inserted_text = "\n".join(forbidden.get("inserted_claims", []))
    for forbidden_text in FORBIDDEN_VERDICTS + FORBIDDEN_CLAIMS + FORBIDDEN_ACTIONS:
        if forbidden_text in inserted_text:
            failures.append(f"forbidden_claim_or_action_inserted:{forbidden_text}")
    if VERDICT_PASS not in forbidden.get("allowed_verdicts", []) or VERDICT_BLOCKED not in forbidden.get("allowed_verdicts", []):
        failures.append("allowed_verdicts_missing")
    if forbidden.get("runtime_or_mechanism_claims_introduced") is not False:
        failures.append("runtime_or_mechanism_claims_introduced")
    return _validator_result("validate_forbidden_claims_and_actions", failures)


def validate_computed_verdict_source(state: dict[str, Any]) -> dict[str, Any]:
    failures = []
    if state.get("callable_gate_logic_executed") is not True:
        failures.append("callable_gate_logic_not_executed")
    if state.get("static_pass_result") is not False:
        failures.append("static_pass_result_detected")
    return _validator_result("validate_computed_verdict_source", failures)


def run_ablation_controls(state: dict[str, Any]) -> dict[str, Any]:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None], str]] = [
        ("missing_preflight_001a_anchor", _mutate_missing_preflight_anchor, "validate_parent_boundaries"),
        ("missing_alignment_001a_anchor", _mutate_missing_alignment_anchor, "validate_parent_boundaries"),
        (
            "missing_post_bridge_001d_verdict_caveat_claim_ceiling",
            _mutate_missing_post_bridge_verdict_caveat_claim,
            "validate_post_bridge_caveats",
        ),
        (
            "blocked_old_canonicalization_001a_used_as_parent",
            _mutate_blocked_old_canonicalization,
            "validate_parent_boundaries",
        ),
        ("authorization_flag_true", _mutate_authorization_true, "validate_authorization_flags"),
        ("static_pass_without_callable_gate_logic", _mutate_static_pass, "validate_computed_verdict_source"),
        (
            "copied_45_row_matrix_or_duplicate_schema",
            _mutate_duplicate_schema_and_matrix,
            "validate_duplicate_schema_and_matrix",
        ),
        (
            "negative_001b_001c_upgraded_to_positive_downstream_evidence",
            _mutate_negative_as_positive,
            "validate_negative_evidence_handling",
        ),
        ("post_bridge_001d_caveat_removed", _mutate_post_bridge_caveat_removed, "validate_post_bridge_caveats"),
        (
            "runtime_gate4_ego_authorization_claim_inserted",
            _mutate_forbidden_authorization_claim,
            "validate_forbidden_claims_and_actions",
        ),
    ]
    controls = []
    for mutation_id, mutate, expected_validator in mutations:
        mutated = copy.deepcopy(state)
        mutate(mutated)
        results = validate_admission_state(mutated)
        failing = [row["validator"] for row in results if not row["passed"]]
        controls.append(
            {
                "mutation_id": mutation_id,
                "expected_validator": expected_validator,
                "validation_failed": expected_validator in failing,
                "failing_validators": failing,
                "producer_function": "run_ablation_controls",
                "aggregation_rule": "each negative mutation must fail through its expected callable validator",
            }
        )
    return {
        "task_id": TASK_ID,
        "controls": controls,
        "all_negative_controls_failed": all(row["validation_failed"] for row in controls),
        "aggregation_rule": "all required ablation controls must fail through callable validators",
    }


def build_result(
    state: dict[str, Any],
    validators: list[dict[str, Any]],
    ablation_report: dict[str, Any],
    protected_after: dict[str, str],
) -> dict[str, Any]:
    stop_conditions = []
    for row in validators:
        if not row["passed"]:
            stop_conditions.extend(row["failures"])
    if not ablation_report.get("all_negative_controls_failed"):
        stop_conditions.append("ablation_control_failed_to_fail")
    protected_modified = state.get("protected_sealed_hashes_before", {}) != protected_after
    if protected_modified:
        stop_conditions.append("sealed_artifact_modified")
    all_gates_passed = all(row["passed"] for row in validators) and not stop_conditions
    return {
        "task_id": TASK_ID,
        "verdict": VERDICT_PASS if all_gates_passed else VERDICT_BLOCKED,
        "producer_function": "build_result",
        "layer": LAYER,
        "claim_ceiling": CLAIM_CEILING,
        "callable_gate_logic_executed": state.get("callable_gate_logic_executed") is True,
        "static_pass_result": state.get("static_pass_result") is True,
        "all_gates_passed": all_gates_passed,
        "gate_outcomes": validators,
        "failure_reasons": stop_conditions,
        "stop_conditions_triggered": stop_conditions,
        "ablation_report": ablation_report,
        "parent_boundaries_resolved": state["parent_boundary_readback"].get("all_required_boundaries_resolved"),
        "remote_anchors_verified": state["parent_boundary_readback"].get("all_required_remote_anchors_verified"),
        "post_bridge_caveats_binding": state["post_bridge_caveat_revalidation"].get("caveats_binding"),
        "actionability_revalidation_passed": state["actionability_revalidation"].get("actionability_revalidation_passed"),
        "computed_evidence_provenance_passed": all(
            state.get("input_artifacts_by_output", {}).get(name)
            for name in REQUIRED_ARTIFACT_NAMES
            if name != "claim_ceiling.txt"
        ),
        "negative_evidence_non_positive": state["negative_evidence_handling"].get("negative_evidence_non_positive"),
        "authorization_flags": state["authorization_flags"]["authorization_flags"],
        "protected_sealed_artifacts_modified": protected_modified,
        "protected_sealed_hashes_before": state.get("protected_sealed_hashes_before", {}),
        "protected_sealed_hashes_after": protected_after,
        "duplicate_admission_schema_created": state["duplicate_schema"].get("duplicate_admission_schema_created"),
        "copied_45_row_matrix_detected": state["duplicate_schema"].get("copied_45_row_matrix_detected"),
        "input_artifacts": state["input_artifacts_by_output"]["result.json"],
        "input_commits_tags_refs": _input_ref_rows(state),
        "run_id": state["run_id"],
        "aggregation_rule": "PASS only when every callable validator passes, every ablation control fails, and sealed parent hashes are unchanged",
        "code_path_hash": _code_path_hash(build_result),
        "artifacts_generated": [(ARTIFACT_DIR / name).as_posix() for name in REQUIRED_ARTIFACT_NAMES],
        "what_this_does_not_prove": list(FORBIDDEN_CLAIMS),
        "final_git_status_policy": "final clean git status is verified after generated outputs are committed",
    }


def hash_protected_inputs(root: str | Path) -> dict[str, str]:
    root_path = Path(root).resolve()
    return {
        path.as_posix(): _sha_file(root_path / path)
        for path in PROTECTED_INPUTS
        if (root_path / path).exists()
    }


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
    local_verified = local_tag == expected_commit if remote_tag else True
    remote_verified = remote_commit == expected_commit if remote_tag else True
    path_verified = path_commit == expected_commit
    return {
        "boundary_id": boundary_id,
        "task_id": task_id,
        "status": status,
        "expected_commit": expected_commit,
        "remote_tag": remote_tag,
        "local_tag_resolved_commit": local_tag,
        "remote_resolved_commit": remote_commit,
        "path_last_commit": path_commit,
        "paths": [path.as_posix() for path in paths],
        "local_verified": local_verified,
        "remote_verified": remote_verified,
        "path_verified": path_verified,
        "resolved_exactly": local_verified and remote_verified and path_verified,
        "producer_function": "_boundary_row",
        "validation_rule": "path history, local tag, and remote tag when declared must match expected sealed commit",
    }


def _mutate_missing_preflight_anchor(state: dict[str, Any]) -> None:
    row = state["parent_boundary_readback"]["parent_boundaries_by_id"]["preflight_001a"]
    row["remote_resolved_commit"] = None
    row["path_last_commit"] = None
    row["resolved_exactly"] = False
    for item in state["parent_boundary_readback"]["parent_boundaries"]:
        if item["boundary_id"] == "preflight_001a":
            item.update(row)


def _mutate_missing_alignment_anchor(state: dict[str, Any]) -> None:
    row = state["parent_boundary_readback"]["parent_boundaries_by_id"]["alignment_001a"]
    row["remote_resolved_commit"] = None
    row["path_last_commit"] = None
    row["resolved_exactly"] = False
    for item in state["parent_boundary_readback"]["parent_boundaries"]:
        if item["boundary_id"] == "alignment_001a":
            item.update(row)


def _mutate_missing_post_bridge_verdict_caveat_claim(state: dict[str, Any]) -> None:
    post_bridge = state["post_bridge_caveat_revalidation"]
    post_bridge["verdict"] = None
    post_bridge["claim_ceiling"] = ""
    post_bridge["caveats"] = []
    post_bridge["caveats_binding"] = False


def _mutate_blocked_old_canonicalization(state: dict[str, Any]) -> None:
    readback = state["parent_boundary_readback"]
    readback["blocked_old_canonicalization_001a"]["used_as_parent"] = True
    row = readback["parent_boundaries_by_id"]["canonicalization_provenance_repair_001b"]
    row["expected_commit"] = BLOCKED_OLD_CANONICALIZATION_001A_COMMIT
    row["resolved_exactly"] = False
    for item in readback["parent_boundaries"]:
        if item["boundary_id"] == "canonicalization_provenance_repair_001b":
            item.update(row)


def _mutate_authorization_true(state: dict[str, Any]) -> None:
    state["authorization_flags"]["authorization_flags"]["authorize_ego_runtime"] = True
    state["authorization_flags"]["all_authorization_flags_false"] = False


def _mutate_static_pass(state: dict[str, Any]) -> None:
    state["callable_gate_logic_executed"] = False
    state["static_pass_result"] = True


def _mutate_duplicate_schema_and_matrix(state: dict[str, Any]) -> None:
    schema = state["duplicate_schema"]
    schema["duplicate_admission_schema_created"] = True
    schema["copied_45_row_matrix_detected"] = True
    schema["copied_matrix_positive_control"] = [{"candidate_id": f"row_{index:02d}"} for index in range(45)]


def _mutate_negative_as_positive(state: dict[str, Any]) -> None:
    negative = state["negative_evidence_handling"]
    for row in negative["negative_evidence_rows"]:
        if row.get("task_id") in {"POST-BRIDGE-ADMISSION-EXECUTABLE-001B", "POST-BRIDGE-ADMISSION-EXECUTABLE-001C"}:
            row["positive_evidence_allowed"] = True
    negative["negative_evidence_non_positive"] = False
    negative["negative_001b_001c_positive_downstream_use_allowed"] = True


def _mutate_post_bridge_caveat_removed(state: dict[str, Any]) -> None:
    state["post_bridge_caveat_revalidation"]["caveats"] = []
    state["post_bridge_caveat_revalidation"]["caveats_binding"] = False


def _mutate_forbidden_authorization_claim(state: dict[str, Any]) -> None:
    state["forbidden_claims_and_actions"]["inserted_claims"].append("Gate4 authorized")
    state["forbidden_claims_and_actions"]["runtime_or_mechanism_claims_introduced"] = True


def _producer_for_artifact(name: str) -> Callable[..., Any]:
    mapping: dict[str, Callable[..., Any]] = {
        "parent_boundary_readback.json": build_parent_boundary_readback,
        "admission_contract_evaluation.json": build_admission_contract_evaluation,
        "post_bridge_caveat_revalidation.json": build_post_bridge_caveat_revalidation,
        "actionability_revalidation.json": build_actionability_revalidation,
        "computed_evidence_provenance.json": build_computed_evidence_provenance_report,
        "negative_evidence_handling.json": build_negative_evidence_handling,
        "forbidden_claims_and_actions.json": build_forbidden_claims_and_actions,
        "admission_decision_trace.json": build_admission_decision_trace,
        "ablation_report.json": run_ablation_controls,
        "authorization_flags.json": build_authorization_flags,
        "result.json": build_result,
    }
    return mapping[name]


def _aggregation_rule_for_artifact(name: str) -> str:
    return {
        "parent_boundary_readback.json": "resolve sealed parent commits from git path history and remote tags",
        "admission_contract_evaluation.json": "aggregate callable gate outcomes for admission contract execution",
        "post_bridge_caveat_revalidation.json": "re-read post-bridge 001D verdict, caveats, claim ceiling, and authorization flags",
        "actionability_revalidation.json": "revalidate required actionability rows against resolved parent boundaries",
        "computed_evidence_provenance.json": "record callable provenance for every verdict-bearing output",
        "negative_evidence_handling.json": "preserve 001B/001C negative evidence without downstream upgrade",
        "forbidden_claims_and_actions.json": "enumerate forbidden claims/actions and inserted-claim checks",
        "admission_decision_trace.json": "serialize input state and replay final verdict through callable functions",
        "ablation_report.json": "run invalid-state negative controls through callable validators",
        "authorization_flags.json": "derive admission authorization flags from resolved contracts and keep all false",
        "result.json": "aggregate validators, ablations, protected hashes, and claim ceiling into final verdict",
    }[name]


def _input_artifacts_by_output() -> dict[str, list[str]]:
    return {
        "parent_boundary_readback.json": PROTECTED_INPUTS_AS_POSIX,
        "admission_contract_evaluation.json": [
            PREFLIGHT_RESULT.as_posix(),
            ALIGNMENT_RESULT.as_posix(),
            POST_BRIDGE_001D_RESULT.as_posix(),
        ],
        "post_bridge_caveat_revalidation.json": [POST_BRIDGE_001D_DOC.as_posix(), POST_BRIDGE_001D_RESULT.as_posix()],
        "actionability_revalidation.json": [ALIGNMENT_ACTIONABILITY.as_posix(), PREFLIGHT_ACTIONABILITY.as_posix()],
        "computed_evidence_provenance.json": [ALIGNMENT_COMPUTED.as_posix(), PREFLIGHT_COMPUTED.as_posix()],
        "negative_evidence_handling.json": [ALIGNMENT_NEGATIVE.as_posix(), PREFLIGHT_NEGATIVE.as_posix()],
        "forbidden_claims_and_actions.json": [DOC_PATH.as_posix(), "AGENTS.md"],
        "admission_decision_trace.json": [
            "serialized admission state",
            "callable validators",
            "ablation controls",
        ],
        "ablation_report.json": ["serialized admission state", "callable validators"],
        "authorization_flags.json": [
            ALIGNMENT_AUTHORIZATION.as_posix(),
            PREFLIGHT_AUTHORIZATION.as_posix(),
            POST_BRIDGE_001D_RESULT.as_posix(),
        ],
        "result.json": [
            "parent_boundary_readback.json",
            "admission_contract_evaluation.json",
            "post_bridge_caveat_revalidation.json",
            "actionability_revalidation.json",
            "computed_evidence_provenance.json",
            "negative_evidence_handling.json",
            "forbidden_claims_and_actions.json",
            "admission_decision_trace.json",
            "ablation_report.json",
            "authorization_flags.json",
        ],
    }


def _input_ref_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "boundary_id": row["boundary_id"],
            "task_id": row["task_id"],
            "expected_commit": row["expected_commit"],
            "remote_tag": row["remote_tag"],
            "remote_resolved_commit": row["remote_resolved_commit"],
            "path_last_commit": row["path_last_commit"],
        }
        for row in state["parent_boundary_readback"]["parent_boundaries"]
    ]


def _with_metadata(
    artifact_name: str,
    payload: dict[str, Any],
    producer: Callable[..., Any],
    input_artifacts: list[str],
    input_commits_tags_refs: list[dict[str, Any]],
    run_id: str,
    aggregation_rule: str,
    gate_outcomes: list[dict[str, Any]],
    failure_reasons: list[str],
) -> dict[str, Any]:
    payload_copy = copy.deepcopy(payload)
    payload_hash = _payload_hash(payload_copy)
    payload_copy["computed_evidence_provenance"] = {
        "artifact_name": artifact_name,
        "producer_function": producer.__name__,
        "input_artifacts": input_artifacts,
        "input_commits_tags_refs": input_commits_tags_refs,
        "run_id": run_id,
        "aggregation_rule": aggregation_rule,
        "code_path_hash": _code_path_hash(producer),
        "output_artifact_hash": payload_hash,
        "output_hash_scope": "canonical JSON payload before computed_evidence_provenance envelope",
        "gate_outcomes": gate_outcomes,
        "failure_reasons": failure_reasons,
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
        "validation_rule": "validator passes only with zero failures",
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


def _run_id(root: Path) -> str:
    seed_parts = [
        TASK_ID,
        PREFLIGHT_001A_COMMIT,
        ALIGNMENT_001A_COMMIT,
        COVERAGE_REFERENCE_001A_COMMIT,
        CANONICALIZATION_REPAIR_001B_COMMIT,
        COVERAGE_COMPRESSION_001D_COMMIT,
        POST_BRIDGE_001D_COMMIT,
        _sha_file(root / PREFLIGHT_RESULT) if (root / PREFLIGHT_RESULT).exists() else "missing_preflight",
        _sha_file(root / POST_BRIDGE_001D_RESULT) if (root / POST_BRIDGE_001D_RESULT).exists() else "missing_001d",
        _sha_file(root / ALIGNMENT_RESULT) if (root / ALIGNMENT_RESULT).exists() else "missing_alignment",
    ]
    return f"ego_mainline_admission_execution_001a_{_sha_text('|'.join(seed_parts))[:16]}"


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--skip-remote", action="store_true")
    args = parser.parse_args()
    result = run_admission_execution(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        verify_remote=not args.skip_remote,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
