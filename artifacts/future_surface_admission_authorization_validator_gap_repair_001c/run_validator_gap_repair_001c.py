from __future__ import annotations

import copy
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001C"
TASK_SLUG = "future_surface_admission_authorization_validator_gap_repair_001c"
SOURCE_001C_TASK_ID = "NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001C"
SOURCE_001C_SLUG = "next_surface_admission_manifest_instantiation_001c"
REQUIRED_001A_TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001A"
REQUIRED_001B_TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001B"
SOURCE_001C_MANIFEST_HASH = "870b1eb33fdf3351d2beb31c98d102bb8ab7360fc92fb65d4cdfd130023c7dce"
BEFORE_VALIDATOR_CODE_PATH_HASH = "67f7c2e08a9ec95176bbaf9c98c2c88a8e1a13e06355cff3211dd7ffb1cebb01"
PASS_VERDICT = "future_surface_admission_authorization_validator_gap_repair_001c_pass"
BLOCKED_VERDICT = "blocked_future_surface_admission_authorization_validator_gap_repair_001c"
CLAIM_CEILING = "surface-admission authorization hygiene only"
LAYER = "engineering-governance / authorization-validator gap repair only"
MAINLINE_INTEGRATION_STATUS = "none"
ENABLED_STATUS = "local offline validator and tests only"
REAL_TRIGGER_EVIDENCE = (
    "validate_authorization_manifest invoked on the concrete 001C manifest structure and "
    "callable dependency-structure mutations for the 001B repair dependency"
)


def _ensure_src_path(repo_root: Path) -> None:
    src = repo_root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def _load_validator(repo_root: Path):
    _ensure_src_path(repo_root)
    from future_surface_admission_authorization_template_001a import validator

    return validator


def _default_output_dir(repo_root: Path) -> Path:
    return repo_root / "artifacts" / TASK_SLUG


def _doc_path(repo_root: Path) -> Path:
    return repo_root / "docs" / "research" / f"{TASK_ID}.md"


def _source_manifest_path(repo_root: Path) -> Path:
    return repo_root / "artifacts" / SOURCE_001C_SLUG / "manifest.json"


def _baseline_dir(repo_root: Path) -> Path:
    return repo_root / "artifacts" / TASK_SLUG / "baseline_pre_repair"


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _write_trace_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_payload(payload: Any) -> str:
    return _hash_bytes(json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8"))


def _hash_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return _hash_bytes(path.read_bytes())


def _source_manifest_for_current_validator(repo_root: Path, validator: Any) -> dict[str, Any]:
    manifest = _load_json(_source_manifest_path(repo_root))
    manifest["authorization_validator"]["code_path_hash"] = validator._source_hash()
    validator._refresh_manifest_hash(manifest)
    return manifest


def _dependency_ids(manifest: dict[str, Any]) -> set[str]:
    dependencies = manifest.get("dependencies", [])
    if not isinstance(dependencies, list):
        return set()
    return {
        dependency.get("task_id")
        for dependency in dependencies
        if isinstance(dependency, dict) and dependency.get("required") is True
    }


def _invoke_manifest(
    validator: Any,
    manifest: dict[str, Any],
    template: dict[str, Any],
    enforcement: dict[str, Any],
) -> dict[str, Any]:
    validator._refresh_manifest_hash(manifest)
    return validator.validate_authorization_manifest(manifest, template, enforcement)


def _decision_row(
    validator: Any,
    template: dict[str, Any],
    enforcement: dict[str, Any],
    identifier_key: str,
    identifier: str,
    mutation_function: str | None,
    manifest: dict[str, Any],
    expected_outcome: str,
    aggregation_path: str,
) -> dict[str, Any]:
    decision = _invoke_manifest(validator, manifest, template, enforcement)
    actual_outcome = decision["authorization_decision"]
    row = {
        identifier_key: identifier,
        "producer_function": decision["producer_function"],
        "mutation_function": mutation_function,
        "input_manifest_hash": validator._manifest_integrity_hash(manifest),
        "input_manifest_file_equivalent_hash": _hash_payload(manifest),
        "validator_code_path_hash": validator._source_hash(),
        "expected_outcome": expected_outcome,
        "actual_outcome": actual_outcome,
        "validator_decision": actual_outcome,
        "reasons_fired": decision["reasons_fired"],
        "blocked": actual_outcome == "blocked",
        "authorized": actual_outcome == "authorized",
        "unexpected_authorization": expected_outcome == "blocked" and actual_outcome != "blocked",
        "unexpected_block": expected_outcome == "authorized" and actual_outcome != "authorized",
        "aggregation_path": aggregation_path,
        "serialized_manifest": copy.deepcopy(manifest),
        "claim_ceiling": CLAIM_CEILING,
    }
    return row


def _remove_dependency(manifest: dict[str, Any], task_id: str) -> dict[str, Any]:
    mutated = copy.deepcopy(manifest)
    mutated["dependencies"] = [
        dependency
        for dependency in mutated.get("dependencies", [])
        if dependency.get("task_id") != task_id
    ]
    return mutated


def _negative_controls(
    validator: Any,
    manifest: dict[str, Any],
    template: dict[str, Any],
    enforcement: dict[str, Any],
) -> dict[str, Any]:
    controls: list[dict[str, Any]] = []

    missing_direction = copy.deepcopy(manifest)
    missing_direction["proposed_surface_admission_direction"] = ""
    missing_direction["proposed_surface_admission_direction_status"] = (
        "missing_concrete_surface_direction"
    )
    controls.append(
        _decision_row(
            validator,
            template,
            enforcement,
            "control_id",
            "missing_concrete_proposed_direction",
            "mutate_missing_concrete_proposed_direction",
            missing_direction,
            "blocked",
            "negative_controls",
        )
    )

    gate5 = copy.deepcopy(manifest)
    gate5["proposed_surface_admission_direction"] = "Gate5 admission proposal"
    controls.append(
        _decision_row(
            validator,
            template,
            enforcement,
            "control_id",
            "manifest_proposing_gate5",
            "mutate_forbidden_gate5_direction",
            gate5,
            "blocked",
            "negative_controls",
        )
    )

    execution_family = copy.deepcopy(manifest)
    execution_family["proposed_surface_admission_direction"] = (
        "bridge runtime tournament EGO-mainline proposal"
    )
    controls.append(
        _decision_row(
            validator,
            template,
            enforcement,
            "control_id",
            "manifest_proposing_bridge_runtime_tournament_ego_mainline",
            "mutate_forbidden_execution_family_direction",
            execution_family,
            "blocked",
            "negative_controls",
        )
    )

    invalid_evidence = copy.deepcopy(manifest)
    invalid_evidence["evidence_citations"] = [
        {
            "artifact_id": "COMPOSITE-CROSS-TASK-STATE-REUSE-SURFACE-DISCRIMINATIVENESS-PREFLIGHT-001A",
            "claim": "mechanism evidence",
        },
        {
            "artifact_id": "CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A",
            "claim": "Gate4 mechanism evidence",
        },
        {
            "artifact_id": "ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A",
            "claim": "readiness evidence",
        },
    ]
    controls.append(
        _decision_row(
            validator,
            template,
            enforcement,
            "control_id",
            "old_invalid_surfaces_cited_as_mechanism_evidence",
            "mutate_old_invalid_surface_citation",
            invalid_evidence,
            "blocked",
            "negative_controls",
        )
    )

    score = copy.deepcopy(manifest)
    score["outputs_requested"].append("mechanism_score")
    controls.append(
        _decision_row(
            validator,
            template,
            enforcement,
            "control_id",
            "mechanism_score_before_admission",
            "mutate_mechanism_score_output_request",
            score,
            "blocked",
            "negative_controls",
        )
    )

    repair_as_execution = copy.deepcopy(manifest)
    repair_as_execution["stored_authorization_decision"] = (
        "candidate authorized for runtime mainline-effective execution"
    )
    repair_as_execution["scope"]["opens_runtime"] = True
    controls.append(
        _decision_row(
            validator,
            template,
            enforcement,
            "control_id",
            "validator_repair_treated_as_mechanism_execution_authorization",
            "mutate_repair_as_execution_authorization",
            repair_as_execution,
            "blocked",
            "negative_controls",
        )
    )

    return {
        "task_id": TASK_ID,
        "producer_function": "run_negative_controls_through_validate_authorization_manifest",
        "controls": controls,
        "blocked_control_count": sum(1 for control in controls if control["blocked"]),
        "all_controls_blocked": all(control["blocked"] for control in controls),
        "claim_ceiling": CLAIM_CEILING,
    }


def _ablations(
    validator: Any,
    manifest: dict[str, Any],
    template: dict[str, Any],
    enforcement: dict[str, Any],
) -> dict[str, Any]:
    ablations: list[dict[str, Any]] = []

    for task_id, ablation_id in [
        ("SURFACE-ADMISSION-CONTRACT-HARDENING-001A", "remove_hardening_dependency"),
        ("SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A", "remove_enforcement_dependency"),
        (
            "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-TEMPLATE-001A",
            "remove_future_authorization_template_dependency",
        ),
        (REQUIRED_001A_TASK_ID, "remove_validator_gap_repair_001a_dependency"),
        (REQUIRED_001B_TASK_ID, "remove_validator_gap_repair_001b_dependency"),
    ]:
        ablations.append(
            _decision_row(
                validator,
                template,
                enforcement,
                "ablation_id",
                ablation_id,
                f"mutate_remove_dependency::{task_id}",
                _remove_dependency(manifest, task_id),
                "blocked",
                "ablation_controls",
            )
        )

    no_direction = copy.deepcopy(manifest)
    no_direction["proposed_surface_admission_direction"] = None
    no_direction["proposed_surface_admission_direction_status"] = (
        "missing_concrete_surface_direction"
    )
    ablations.append(
        _decision_row(
            validator,
            template,
            enforcement,
            "ablation_id",
            "remove_concrete_proposed_direction",
            "mutate_remove_concrete_proposed_direction",
            no_direction,
            "blocked",
            "ablation_controls",
        )
    )

    no_later_lock = copy.deepcopy(manifest)
    no_later_lock["later_task_card_only"] = False
    no_later_lock["scope"]["later_task_card_only"] = False
    ablations.append(
        _decision_row(
            validator,
            template,
            enforcement,
            "ablation_id",
            "remove_later_task_card_only_scope_lock",
            "mutate_remove_later_task_card_only_scope_lock",
            no_later_lock,
            "blocked",
            "ablation_controls",
        )
    )

    no_score_rule = copy.deepcopy(manifest)
    no_score_rule["required_rules"]["no_mechanism_score_before_admission"] = False
    ablations.append(
        _decision_row(
            validator,
            template,
            enforcement,
            "ablation_id",
            "remove_no_mechanism_score_clause",
            "mutate_remove_no_mechanism_score_clause",
            no_score_rule,
            "blocked",
            "ablation_controls",
        )
    )

    no_invalid_ban = copy.deepcopy(manifest)
    no_invalid_ban["required_rules"]["old_invalid_surface_citation_ban"] = False
    ablations.append(
        _decision_row(
            validator,
            template,
            enforcement,
            "ablation_id",
            "remove_invalid_evidence_ban",
            "mutate_remove_invalid_evidence_ban",
            no_invalid_ban,
            "blocked",
            "ablation_controls",
        )
    )

    forbidden_scope = copy.deepcopy(manifest)
    forbidden_scope["scope"].update(
        {
            "creates_candidate_behavior": True,
            "opens_gate5": True,
            "opens_bridge": True,
            "opens_runtime": True,
            "opens_tournament": True,
            "opens_ego_mainline": True,
        }
    )
    ablations.append(
        _decision_row(
            validator,
            template,
            enforcement,
            "ablation_id",
            "open_no_candidate_gate5_bridge_runtime_tournament_ego_mainline_scope",
            "mutate_open_forbidden_scope",
            forbidden_scope,
            "blocked",
            "ablation_controls",
        )
    )

    return {
        "task_id": TASK_ID,
        "producer_function": "run_ablations_through_validate_authorization_manifest",
        "ablations": ablations,
        "blocked_ablation_count": sum(1 for ablation in ablations if ablation["blocked"]),
        "all_required_ablations_blocked": all(ablation["blocked"] for ablation in ablations),
        "unexpected_authorizations": [
            ablation for ablation in ablations if ablation["unexpected_authorization"]
        ],
        "claim_ceiling": CLAIM_CEILING,
    }


def _dependency_structure_controls(
    validator: Any,
    manifest: dict[str, Any],
    template: dict[str, Any],
    enforcement: dict[str, Any],
) -> dict[str, Any]:
    controls: list[dict[str, Any]] = []

    alias = copy.deepcopy(manifest)
    for dependency in alias["dependencies"]:
        if dependency.get("task_id") == REQUIRED_001B_TASK_ID:
            dependency["task_id"] = f"{REQUIRED_001B_TASK_ID}-ALIAS"
    controls.append(
        _decision_row(
            validator,
            template,
            enforcement,
            "control_id",
            "validator_gap_repair_001b_dependency_alias",
            "mutate_alias_001b_dependency",
            alias,
            "blocked",
            "dependency_structure_controls",
        )
    )

    narrative = _remove_dependency(manifest, REQUIRED_001B_TASK_ID)
    narrative["notes"] = (
        "Narrative-only mention of "
        "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001B."
    )
    controls.append(
        _decision_row(
            validator,
            template,
            enforcement,
            "control_id",
            "validator_gap_repair_001b_dependency_free_text_only",
            "mutate_narrative_only_001b_dependency",
            narrative,
            "blocked",
            "dependency_structure_controls",
        )
    )

    metadata = _remove_dependency(manifest, REQUIRED_001B_TASK_ID)
    metadata["non_enforced_metadata"] = {
        "task_id": REQUIRED_001B_TASK_ID,
        "dependency_type": "sealed_validator_gap_repair_boundary",
        "required": True,
    }
    controls.append(
        _decision_row(
            validator,
            template,
            enforcement,
            "control_id",
            "validator_gap_repair_001b_dependency_non_enforced_metadata_only",
            "mutate_metadata_only_001b_dependency",
            metadata,
            "blocked",
            "dependency_structure_controls",
        )
    )

    replacement = _remove_dependency(manifest, REQUIRED_001B_TASK_ID)
    controls.append(
        _decision_row(
            validator,
            template,
            enforcement,
            "control_id",
            "validator_gap_repair_001b_replaced_with_001a_only",
            "mutate_replace_001b_with_001a_only",
            replacement,
            "blocked",
            "dependency_structure_controls",
        )
    )

    return {
        "task_id": TASK_ID,
        "producer_function": (
            "run_dependency_structure_controls_through_validate_authorization_manifest"
        ),
        "controls": controls,
        "blocked_control_count": sum(1 for control in controls if control["blocked"]),
        "all_controls_blocked": all(control["blocked"] for control in controls),
        "unexpected_authorizations": [
            control for control in controls if control["unexpected_authorization"]
        ],
        "claim_ceiling": CLAIM_CEILING,
    }


def _positive_controls(dependency_controls: dict[str, Any]) -> dict[str, Any]:
    controls: list[dict[str, Any]] = []
    metadata_control = next(
        control
        for control in dependency_controls["controls"]
        if control["control_id"]
        == "validator_gap_repair_001b_dependency_non_enforced_metadata_only"
    )
    dependency_ids = _dependency_ids(metadata_control["serialized_manifest"])
    passed = (
        metadata_control["blocked"] is True
        and REQUIRED_001B_TASK_ID not in dependency_ids
        and "missing_validator_gap_repair_dependency" in metadata_control["reasons_fired"]
    )
    controls.append(
        {
            "control_id": "dependency_structure_scanner_detects_metadata_only_001b",
            "producer_function": "positive_control_dependency_structure_scanner",
            "source_control_id": metadata_control["control_id"],
            "positive_control_passed": passed,
            "detected_malformed_dependency_placement": passed,
            "claim_ceiling": CLAIM_CEILING,
        }
    )
    return {
        "task_id": TASK_ID,
        "producer_function": "run_positive_controls_for_dependency_structure_scanner",
        "controls": controls,
        "passed_control_count": sum(1 for control in controls if control["positive_control_passed"]),
        "all_positive_controls_passed": all(
            control["positive_control_passed"] for control in controls
        ),
        "claim_ceiling": CLAIM_CEILING,
    }


def _baseline_evidence(repo_root: Path) -> dict[str, Any]:
    base = _baseline_dir(repo_root)
    result_path = base / "result.json"
    ablation_path = base / "ablation_results.json"
    dependency_path = base / "dependency_structure_controls.json"
    negative_path = base / "negative_controls.json"
    if not all(path.exists() for path in [result_path, ablation_path, dependency_path, negative_path]):
        return {
            "task_id": TASK_ID,
            "producer_function": "read_pre_repair_callable_baseline",
            "pre_repair": {"parse_status": "missing"},
            "baseline_available": False,
            "claim_ceiling": CLAIM_CEILING,
        }
    result = _load_json(result_path)
    ablations = _load_json(ablation_path)
    dependencies = _load_json(dependency_path)
    negatives = _load_json(negative_path)
    return {
        "task_id": TASK_ID,
        "producer_function": "read_pre_repair_callable_baseline",
        "baseline_available": True,
        "baseline_paths": {
            "result": _rel(result_path, repo_root),
            "ablation_results": _rel(ablation_path, repo_root),
            "dependency_structure_controls": _rel(dependency_path, repo_root),
            "negative_controls": _rel(negative_path, repo_root),
        },
        "pre_repair": {
            "producer_function": result.get("producer_function"),
            "run_id": result.get("run_id"),
            "validator_code_path_hash": result.get("actual_validator_code_path_hash"),
            "source_001c_manifest_hash": SOURCE_001C_MANIFEST_HASH,
            "input_manifest_hash": result.get("manifest_hash"),
            "validator_authorization_decision": result.get("validator_authorization_decision"),
            "verdict": result.get("verdict"),
            "negative_controls_blocked_count": negatives.get("blocked_control_count"),
            "ablation_controls_blocked_count": ablations.get("blocked_ablation_count"),
            "dependency_structure_controls_blocked_count": dependencies.get(
                "blocked_control_count"
            ),
            "unexpected_authorized_ablations": result.get("unexpected_authorized_ablations", []),
            "unexpected_authorized_dependency_structure_controls": result.get(
                "unexpected_authorized_dependency_structure_controls", []
            ),
        },
        "claim_ceiling": CLAIM_CEILING,
    }


def _trace_rows(
    run_id: str,
    valid_row: dict[str, Any],
    negative_controls: dict[str, Any],
    ablations: dict[str, Any],
    dependency_controls: dict[str, Any],
) -> list[dict[str, Any]]:
    all_rows = [
        ("valid_manifest", valid_row),
        *[("negative_control", control) for control in negative_controls["controls"]],
        *[("ablation", ablation) for ablation in ablations["ablations"]],
        *[("dependency_structure_control", control) for control in dependency_controls["controls"]],
    ]
    trace: list[dict[str, Any]] = []
    for event_type, row in all_rows:
        manifest_control_id = (
            row.get("manifest_id")
            or row.get("control_id")
            or row.get("ablation_id")
            or "valid_001c_manifest"
        )
        trace.append(
            {
                "task_id": TASK_ID,
                "run_id": run_id,
                "event": "validator_invocation",
                "event_type": event_type,
                "manifest_control_id": manifest_control_id,
                "input_manifest_hash": row["input_manifest_hash"],
                "validator_code_hash": row["validator_code_path_hash"],
                "producer_function": row["producer_function"],
                "mutation_function": row["mutation_function"],
                "expected_outcome": row["expected_outcome"],
                "actual_outcome": row["actual_outcome"],
                "rejection_reason": row["reasons_fired"] if row["actual_outcome"] == "blocked" else [],
                "authorization_reason": (
                    "no_reasons_fired" if row["actual_outcome"] == "authorized" else None
                ),
                "aggregation_path": row["aggregation_path"],
                "serialized_manifest": row["serialized_manifest"],
                "claim_ceiling": CLAIM_CEILING,
            }
        )
    return trace


def _replay_from_trace(
    repo_root: Path,
    trace_path: Path,
    validator: Any,
    template: dict[str, Any],
    enforcement: dict[str, Any],
) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    replay_rows: list[dict[str, Any]] = []
    for row in rows:
        manifest = row["serialized_manifest"]
        decision = validator.validate_authorization_manifest(manifest, template, enforcement)
        reasons_match = sorted(decision["reasons_fired"]) == sorted(row["rejection_reason"])
        outcome_match = decision["authorization_decision"] == row["actual_outcome"]
        replay_rows.append(
            {
                "manifest_control_id": row["manifest_control_id"],
                "producer_function": "replay_validate_authorization_manifest_from_serialized_input",
                "input_manifest_hash": validator._manifest_integrity_hash(manifest),
                "recorded_input_manifest_hash": row["input_manifest_hash"],
                "recorded_outcome": row["actual_outcome"],
                "recomputed_outcome": decision["authorization_decision"],
                "outcome_match": outcome_match,
                "reasons_match": reasons_match,
                "claim_ceiling": CLAIM_CEILING,
            }
        )
    return {
        "task_id": TASK_ID,
        "producer_function": "replay_trace_from_serialized_manifests",
        "trace_path": _rel(trace_path, repo_root),
        "replayed_count": len(replay_rows),
        "rows": replay_rows,
        "all_recomputed_outcomes_match": all(
            row["outcome_match"] and row["reasons_match"] for row in replay_rows
        ),
        "claim_ceiling": CLAIM_CEILING,
    }


def _write_report(repo_root: Path, result: dict[str, Any]) -> None:
    report = f"""# {TASK_ID}

Verdict: `{result["verdict"]}`.

Layer: `{result["current_layer"]}`.

Mainline integration status: `{result["mainline_integration_status"]}`.

Enabled status: `{result["enabled_status"]}`.

Real trigger evidence: `{result["real_trigger_evidence"]}`.

Validator hashes:

- Before: `{result["before_validator_code_path_hash"]}`
- After: `{result["after_validator_code_path_hash"]}`

001C manifest hash: `{result["source_001c_manifest_hash"]}`.

Callable results:

- Negative controls blocked: `{result["negative_controls_blocked_count"]}/6`
- Ablations blocked: `{result["ablation_controls_blocked_count"]}/10`
- Dependency-structure controls blocked: `{result["dependency_structure_controls_blocked_count"]}/4`
- Positive controls passed: `{result["positive_controls_passed_count"]}/1`
- Replay recomputation: `{result["replay_recomputation"]["all_recomputed_outcomes_match"]}`

Stop conditions triggered: `{result["stop_conditions_triggered"]}`.

Claim ceiling: `{result["claim_ceiling"]}`.

Remote-anchor status: `{result["auto_remote_anchor"]["decision"]}`.

What this does not prove: no mechanism, Gate, candidate, agency, autonomy,
consciousness, emotion, subjectivity, readiness, runtime, companion, stable
benefit, or mainline-effect claim is made by this repair.
"""
    _doc_path(repo_root).write_text(report, encoding="utf-8")


def run(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
    write_report: bool | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    out = Path(output_dir) if output_dir is not None else _default_output_dir(root)
    out.mkdir(parents=True, exist_ok=True)
    should_write_report = output_dir is None if write_report is None else write_report
    validator = _load_validator(root)
    run_id = f"{TASK_SLUG}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    template = validator.build_authorization_manifest_template(root)
    enforcement = validator.validate_enforcement_artifacts(root)
    manifest = _source_manifest_for_current_validator(root, validator)
    source_manifest_hash = validator._manifest_integrity_hash(_load_json(_source_manifest_path(root)))
    after_validator_hash = validator._source_hash()

    valid_row = _decision_row(
        validator,
        template,
        enforcement,
        "manifest_id",
        SOURCE_001C_TASK_ID,
        None,
        copy.deepcopy(manifest),
        "authorized",
        "valid_manifest_authorization",
    )
    negative_controls = _negative_controls(validator, manifest, template, enforcement)
    ablations = _ablations(validator, manifest, template, enforcement)
    dependency_controls = _dependency_structure_controls(validator, manifest, template, enforcement)
    positive_controls = _positive_controls(dependency_controls)
    baseline = _baseline_evidence(root)

    trace_rows = _trace_rows(
        run_id,
        valid_row,
        negative_controls,
        ablations,
        dependency_controls,
    )
    trace_path = out / "trace.jsonl"
    _write_trace_jsonl(trace_path, trace_rows)
    replay = _replay_from_trace(root, trace_path, validator, template, enforcement)

    stop_conditions: list[str] = []
    if valid_row["actual_outcome"] != "authorized":
        stop_conditions.append("valid_001c_manifest_no_longer_authorized")
    if not negative_controls["all_controls_blocked"]:
        stop_conditions.append("negative_controls_not_all_blocked")
    if ablations["blocked_ablation_count"] != 10 or not ablations["all_required_ablations_blocked"]:
        stop_conditions.append("ablations_not_10_of_10_blocked")
    if (
        dependency_controls["blocked_control_count"] != 4
        or not dependency_controls["all_controls_blocked"]
    ):
        stop_conditions.append("dependency_structure_controls_not_4_of_4_blocked")
    if not positive_controls["all_positive_controls_passed"]:
        stop_conditions.append("positive_control_failed")
    if not replay["all_recomputed_outcomes_match"]:
        stop_conditions.append("replay_recomputation_failed")
    if not baseline["baseline_available"]:
        stop_conditions.append("pre_repair_baseline_missing")
    pre_repair = baseline.get("pre_repair", {})
    if pre_repair.get("validator_code_path_hash") != BEFORE_VALIDATOR_CODE_PATH_HASH:
        stop_conditions.append("pre_repair_validator_hash_mismatch")
    if source_manifest_hash != SOURCE_001C_MANIFEST_HASH:
        stop_conditions.append("source_001c_manifest_hash_mismatch")

    verdict = PASS_VERDICT if not stop_conditions else BLOCKED_VERDICT
    result = {
        "task_id": TASK_ID,
        "verdict": verdict,
        "producer_function": "run_validator_gap_repair_001c",
        "run_id": run_id,
        "current_layer": LAYER,
        "layer": LAYER,
        "mainline_integration": False,
        "mainline_integration_status": MAINLINE_INTEGRATION_STATUS,
        "enabled_status": ENABLED_STATUS,
        "real_trigger_evidence": REAL_TRIGGER_EVIDENCE,
        "claim_ceiling": CLAIM_CEILING,
        "source_001c_task_id": SOURCE_001C_TASK_ID,
        "source_001c_manifest_path": _rel(_source_manifest_path(root), root),
        "source_001c_manifest_hash": source_manifest_hash,
        "before_validator_code_path_hash": BEFORE_VALIDATOR_CODE_PATH_HASH,
        "after_validator_code_path_hash": after_validator_hash,
        "baseline_evidence_path": _rel(out / "baseline_evidence.json", root),
        "valid_manifest_authorized": valid_row["actual_outcome"] == "authorized",
        "valid_manifest_reasons_fired": valid_row["reasons_fired"],
        "negative_controls_blocked_count": negative_controls["blocked_control_count"],
        "negative_controls_all_blocked": negative_controls["all_controls_blocked"],
        "ablation_controls_blocked_count": ablations["blocked_ablation_count"],
        "ablation_controls_all_blocked": ablations["all_required_ablations_blocked"],
        "dependency_structure_controls_blocked_count": dependency_controls[
            "blocked_control_count"
        ],
        "dependency_structure_controls_all_blocked": dependency_controls["all_controls_blocked"],
        "positive_controls_passed_count": positive_controls["passed_control_count"],
        "positive_controls_all_passed": positive_controls["all_positive_controls_passed"],
        "replay_recomputation": {
            "path": _rel(out / "replay_report.json", root),
            "all_recomputed_outcomes_match": replay["all_recomputed_outcomes_match"],
            "replayed_count": replay["replayed_count"],
        },
        "artifact_paths": {
            "result": _rel(out / "result.json", root),
            "readback": _rel(out / "readback.json", root),
            "trace": _rel(out / "trace.json", root),
            "trace_jsonl": _rel(trace_path, root),
            "negative_controls": _rel(out / "negative_controls.json", root),
            "ablation_results": _rel(out / "ablation_results.json", root),
            "dependency_structure_controls": _rel(
                out / "dependency_structure_controls.json",
                root,
            ),
            "positive_controls": _rel(out / "positive_controls.json", root),
            "replay_report": _rel(out / "replay_report.json", root),
        },
        "computed_evidence_provenance": {
            "producer_function": "run_validator_gap_repair_001c",
            "inputs": [
                _rel(_source_manifest_path(root), root),
                _rel(_baseline_dir(root), root),
                "src/future_surface_admission_authorization_template_001a/validator.py",
            ],
            "run_id": run_id,
            "manifest_control_ids": [
                row["manifest_control_id"] for row in trace_rows
            ],
            "aggregation_function": "stop_conditions_empty_and_counts_match_acceptance_gate",
            "validator_code_path_hash": after_validator_hash,
            "source_manifest_hash": source_manifest_hash,
            "runner_file_hash": _hash_file(Path(__file__)),
        },
        "stop_conditions_triggered": stop_conditions,
        "mechanism_execution": False,
        "mainline_effect": False,
        "candidate_scope_opened": False,
        "gate5_scope_opened": False,
        "bridge_scope_opened": False,
        "runtime_scope_opened": False,
        "tournament_scope_opened": False,
        "ego_mainline_scope_opened": False,
        "auto_remote_anchor": {
            "decision": (
                "conditional_pending_commit_gate" if not stop_conditions else "forbidden"
            ),
            "performed": False,
            "reason": (
                "requires post-commit clean status and exact remote readback"
                if not stop_conditions
                else "stop condition triggered"
            ),
            "claim_ceiling_if_performed": "remote-anchor publication and verification only",
        },
        "next_minimal_closed_loop_action": (
            "Run required checks, inspect changed-file allowlist, and decide whether the "
            "conditional remote-anchor gates are actually satisfiable."
        ),
        "what_this_does_not_prove": [
            "mechanism validity or downstream admission validity",
            "runtime or EGO mainline effect",
            "subject or user-benefit claims",
        ],
    }
    trace = {
        "task_id": TASK_ID,
        "producer_function": "build_validator_gap_repair_001c_trace",
        "run_id": run_id,
        "trace_jsonl_path": _rel(trace_path, root),
        "row_count": len(trace_rows),
        "claim_ceiling": CLAIM_CEILING,
    }
    readback = {
        "task_id": TASK_ID,
        "producer_function": "build_validator_gap_repair_001c_readback",
        "run_id": run_id,
        "result_path": _rel(out / "result.json", root),
        "source_001c_manifest_hash": source_manifest_hash,
        "before_validator_code_path_hash": BEFORE_VALIDATOR_CODE_PATH_HASH,
        "after_validator_code_path_hash": after_validator_hash,
        "valid_manifest_decision": valid_row,
        "negative_controls_summary": {
            "blocked": negative_controls["blocked_control_count"],
            "total": len(negative_controls["controls"]),
        },
        "ablation_summary": {
            "blocked": ablations["blocked_ablation_count"],
            "total": len(ablations["ablations"]),
        },
        "dependency_structure_summary": {
            "blocked": dependency_controls["blocked_control_count"],
            "total": len(dependency_controls["controls"]),
        },
        "positive_control_summary": {
            "passed": positive_controls["passed_control_count"],
            "total": len(positive_controls["controls"]),
        },
        "replay_recomputation": replay,
        "stop_conditions_triggered": stop_conditions,
        "claim_ceiling": CLAIM_CEILING,
    }

    _write_json(out / "baseline_evidence.json", baseline)
    _write_json(out / "negative_controls.json", negative_controls)
    _write_json(out / "ablation_results.json", ablations)
    _write_json(out / "dependency_structure_controls.json", dependency_controls)
    _write_json(out / "positive_controls.json", positive_controls)
    _write_json(out / "replay_report.json", replay)
    _write_json(out / "trace.json", trace)
    _write_json(out / "readback.json", readback)
    _write_json(out / "result.json", result)
    (out / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    if should_write_report:
        _write_report(root, result)
    return result


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    run(repo_root)


if __name__ == "__main__":
    main()
