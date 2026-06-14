from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001B"
TASK_SLUG = "future_surface_admission_authorization_validator_gap_repair_001b"
PARENT_BLOCKER_TASK = "NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001B"
PARENT_BLOCKER_SLUG = "next_surface_admission_manifest_instantiation_001b"
PARENT_BLOCKER_COMMIT = "c59f85f794f5e4acb0be031f03860da54e806af7"
OBSERVED_GAP = "remove_validator_gap_repair_dependency_authorized"
ORIGINAL_MANIFEST_HASH = "860c4b6203338cbda9684a1a712f668dc46ffb274e12381082050e2c21185175"
BEFORE_VALIDATOR_CODE_PATH_HASH = (
    "a6cd3ca24459e212ce8fd80a37978fa9b99214cf5740899ea0c42122dff25e6b"
)
CLAIM_CEILING = "surface-admission authorization hygiene only"
LAYER = "engineering-governance / authorization-validator gap repair only"
MAINLINE_INTEGRATION = "none"
ENABLED_STATUS = "local offline validator and tests only"
PASS_VERDICT = "future_surface_admission_authorization_validator_gap_repair_001b_pass"
BLOCKED_VERDICT = "future_surface_admission_authorization_validator_gap_repair_001b_blocked"

HARDENING_TASK_ID = "SURFACE-ADMISSION-CONTRACT-HARDENING-001A"
ENFORCEMENT_TASK_ID = "SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A"
TEMPLATE_TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-TEMPLATE-001A"
GAP_REPAIR_TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001A"

WHAT_THIS_DOES_NOT_PROVE = [
    "mechanism validity",
    "Gate validity",
    "candidate behavior",
    "agency",
    "autonomy",
    "consciousness",
    "emotion",
    "subjectivity",
    "EGO readiness",
    "runtime readiness",
    "companion readiness",
    "stable user benefit",
    "mainline effect",
]


def _ensure_src_path(repo_root: Path) -> None:
    src = repo_root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def _load_validator(repo_root: Path):
    _ensure_src_path(repo_root)
    from future_surface_admission_authorization_template_001a import validator

    return validator


def _output_dir(repo_root: Path) -> Path:
    return repo_root / "artifacts" / TASK_SLUG


def _doc_path(repo_root: Path) -> Path:
    return repo_root / "docs" / "research" / f"{TASK_ID}.md"


def _parent_manifest_path(repo_root: Path) -> Path:
    return repo_root / "artifacts" / PARENT_BLOCKER_SLUG / "manifest.json"


def _parent_ablation_path(repo_root: Path) -> Path:
    return repo_root / "artifacts" / PARENT_BLOCKER_SLUG / "ablation_results.json"


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return _hash_bytes(path.read_bytes())


def _run_git(repo_root: Path, args: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "command": ["git", *args],
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
        }
    return {
        "command": ["git", *args],
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _git_stdout(repo_root: Path, args: list[str]) -> str | None:
    result = _run_git(repo_root, args)
    if result["returncode"] != 0:
        return None
    return result["stdout"]


def _refresh_for_repaired_validator(
    manifest: dict[str, Any],
    validator: Any,
) -> dict[str, Any]:
    repaired = copy.deepcopy(manifest)
    repaired["authorization_validator"]["code_path_hash"] = validator._source_hash()
    validator._refresh_manifest_hash(repaired)
    return repaired


def _decision_row(
    identifier_key: str,
    identifier: str,
    decision: dict[str, Any],
    expected_blocked: bool = True,
) -> dict[str, Any]:
    blocked = decision["authorization_decision"] == "blocked"
    return {
        identifier_key: identifier,
        "producer_function": decision["producer_function"],
        "validator_decision": decision["authorization_decision"],
        "reasons_fired": decision["reasons_fired"],
        "blocked": blocked,
        "expected_blocked": expected_blocked,
        "unexpected_authorization": expected_blocked and not blocked,
    }


def _invoke_manifest(
    validator: Any,
    manifest: dict[str, Any],
    template: dict[str, Any],
    enforcement: dict[str, Any],
    refresh_hash: bool = True,
) -> dict[str, Any]:
    if refresh_hash:
        validator._refresh_manifest_hash(manifest)
    return validator.validate_authorization_manifest(manifest, template, enforcement)


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
            "control_id",
            "missing_concrete_proposed_direction",
            _invoke_manifest(validator, missing_direction, template, enforcement),
        )
    )

    gate5 = copy.deepcopy(manifest)
    gate5["proposed_surface_admission_direction"] = "Gate5 admission proposal"
    controls.append(
        _decision_row(
            "control_id",
            "gate5_proposed_direction",
            _invoke_manifest(validator, gate5, template, enforcement),
        )
    )

    execution_family = copy.deepcopy(manifest)
    execution_family["proposed_surface_admission_direction"] = (
        "bridge runtime tournament EGO-mainline proposal"
    )
    controls.append(
        _decision_row(
            "control_id",
            "bridge_runtime_tournament_ego_mainline_proposed_direction",
            _invoke_manifest(validator, execution_family, template, enforcement),
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
            "control_id",
            "old_invalid_surfaces_cited_as_mechanism_evidence",
            _invoke_manifest(validator, invalid_evidence, template, enforcement),
        )
    )

    score = copy.deepcopy(manifest)
    score["outputs_requested"].append("mechanism_score")
    controls.append(
        _decision_row(
            "control_id",
            "mechanism_score_before_admission",
            _invoke_manifest(validator, score, template, enforcement),
        )
    )

    repair_as_execution = copy.deepcopy(manifest)
    repair_as_execution["stored_authorization_decision"] = (
        "candidate authorized for runtime mainline-effective execution"
    )
    repair_as_execution["scope"]["opens_runtime"] = True
    controls.append(
        _decision_row(
            "control_id",
            "validator_repair_treated_as_mechanism_execution_authorization",
            _invoke_manifest(validator, repair_as_execution, template, enforcement),
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

    def add(ablation_id: str, mutated: dict[str, Any]) -> None:
        ablations.append(
            _decision_row(
                "ablation_id",
                ablation_id,
                _invoke_manifest(validator, mutated, template, enforcement),
            )
        )

    for task_id, ablation_id in [
        (HARDENING_TASK_ID, "remove_hardening_dependency"),
        (ENFORCEMENT_TASK_ID, "remove_enforcement_dependency"),
        (TEMPLATE_TASK_ID, "remove_future_authorization_template_dependency"),
        (GAP_REPAIR_TASK_ID, "remove_validator_gap_repair_dependency"),
    ]:
        mutated = copy.deepcopy(manifest)
        mutated["dependencies"] = [
            dependency
            for dependency in mutated["dependencies"]
            if dependency.get("task_id") != task_id
        ]
        add(ablation_id, mutated)

    no_direction = copy.deepcopy(manifest)
    no_direction["proposed_surface_admission_direction"] = None
    no_direction["proposed_surface_admission_direction_status"] = (
        "missing_concrete_surface_direction"
    )
    add("remove_concrete_proposed_direction", no_direction)

    no_later_lock = copy.deepcopy(manifest)
    no_later_lock["later_task_card_only"] = False
    no_later_lock["scope"]["later_task_card_only"] = False
    add("remove_later_task_card_only_scope_lock", no_later_lock)

    no_score_rule = copy.deepcopy(manifest)
    no_score_rule["required_rules"]["no_mechanism_score_before_admission"] = False
    add("remove_no_mechanism_score_clause", no_score_rule)

    no_invalid_ban = copy.deepcopy(manifest)
    no_invalid_ban["required_rules"]["old_invalid_surface_citation_ban"] = False
    add("remove_invalid_evidence_ban", no_invalid_ban)

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
    add("open_forbidden_scope", forbidden_scope)

    unexpected = [ablation for ablation in ablations if ablation["unexpected_authorization"]]
    return {
        "task_id": TASK_ID,
        "producer_function": "run_ablations_through_validate_authorization_manifest",
        "ablations": ablations,
        "blocked_ablation_count": sum(1 for ablation in ablations if ablation["blocked"]),
        "all_required_ablations_blocked": all(ablation["blocked"] for ablation in ablations),
        "unexpected_authorizations": unexpected,
        "claim_ceiling": CLAIM_CEILING,
    }


def _dependency_structure_controls(
    validator: Any,
    manifest: dict[str, Any],
    template: dict[str, Any],
    enforcement: dict[str, Any],
) -> dict[str, Any]:
    controls: list[dict[str, Any]] = []

    def add(control_id: str, mutated: dict[str, Any]) -> None:
        controls.append(
            _decision_row(
                "control_id",
                control_id,
                _invoke_manifest(validator, mutated, template, enforcement),
            )
        )

    narrative_only = copy.deepcopy(manifest)
    narrative_only["dependencies"] = [
        dependency
        for dependency in narrative_only["dependencies"]
        if dependency.get("task_id") != GAP_REPAIR_TASK_ID
    ]
    narrative_only["notes"] = (
        "Narrative-only mention of "
        "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001A"
    )
    add("validator_gap_repair_dependency_free_text_only", narrative_only)

    alias = copy.deepcopy(manifest)
    for dependency in alias["dependencies"]:
        if dependency.get("task_id") == GAP_REPAIR_TASK_ID:
            dependency["task_id"] = f"{GAP_REPAIR_TASK_ID}-ALIAS"
    add("validator_gap_repair_dependency_alias_id", alias)

    non_enforced = copy.deepcopy(manifest)
    for dependency in non_enforced["dependencies"]:
        if dependency.get("task_id") == GAP_REPAIR_TASK_ID:
            dependency["required"] = False
    add("validator_gap_repair_dependency_non_enforced", non_enforced)

    mutated_type = copy.deepcopy(manifest)
    for dependency in mutated_type["dependencies"]:
        if dependency.get("task_id") == GAP_REPAIR_TASK_ID:
            dependency["dependency_type"] = "narrative_reference_only"
    add("validator_gap_repair_dependency_mutated_type", mutated_type)

    return {
        "task_id": TASK_ID,
        "producer_function": "run_dependency_structure_controls",
        "controls": controls,
        "blocked_control_count": sum(1 for control in controls if control["blocked"]),
        "all_controls_blocked": all(control["blocked"] for control in controls),
        "claim_ceiling": CLAIM_CEILING,
    }


def _before_gap_result(repo_root: Path) -> dict[str, Any]:
    ablations = _load_json(_parent_ablation_path(repo_root))
    for ablation in ablations.get("ablations", []):
        if ablation.get("ablation_id") == "remove_validator_gap_repair_dependency":
            return {
                "source_path": _rel(_parent_ablation_path(repo_root), repo_root),
                "producer_function": ablation.get("producer_function"),
                "validator_decision": ablation.get("validator_decision"),
                "blocked": ablation.get("blocked"),
                "reasons_fired": ablation.get("reasons_fired", []),
                "unexpected_authorization": ablation.get("unexpected_authorization"),
                "validator_code_path_hash": BEFORE_VALIDATOR_CODE_PATH_HASH,
            }
    return {
        "source_path": _rel(_parent_ablation_path(repo_root), repo_root),
        "validator_decision": "missing",
        "blocked": None,
        "reasons_fired": ["parent_gap_ablation_not_found"],
        "unexpected_authorization": None,
        "validator_code_path_hash": BEFORE_VALIDATOR_CODE_PATH_HASH,
    }


def _after_gap_result(ablations: dict[str, Any], after_hash: str) -> dict[str, Any]:
    for ablation in ablations["ablations"]:
        if ablation["ablation_id"] == "remove_validator_gap_repair_dependency":
            return {
                "producer_function": ablation["producer_function"],
                "validator_decision": ablation["validator_decision"],
                "blocked": ablation["blocked"],
                "reasons_fired": ablation["reasons_fired"],
                "unexpected_authorization": ablation["unexpected_authorization"],
                "validator_code_path_hash": after_hash,
            }
    return {
        "validator_decision": "missing",
        "blocked": None,
        "reasons_fired": ["repaired_gap_ablation_not_found"],
        "unexpected_authorization": None,
        "validator_code_path_hash": after_hash,
    }


def _build_trace(
    run_id: str,
    repo_root: Path,
    repaired_manifest_hash: str,
    after_hash: str,
    valid_decision: dict[str, Any],
    negative_controls: dict[str, Any],
    ablations: dict[str, Any],
    structure_controls: dict[str, Any],
    gap_closed: bool,
) -> dict[str, Any]:
    events: list[dict[str, Any]] = [
        {
            "event": "parent_manifest_loaded",
            "producer_function": "load_parent_manifest",
            "run_id": run_id,
            "input_manifest_path": _rel(_parent_manifest_path(repo_root), repo_root),
            "original_manifest_hash": ORIGINAL_MANIFEST_HASH,
            "claim_ceiling": CLAIM_CEILING,
        },
        {
            "event": "validator_invoked",
            "producer_function": "validate_authorization_manifest",
            "run_id": run_id,
            "repaired_manifest_hash": repaired_manifest_hash,
            "validator_code_path_hash": after_hash,
            "authorization_decision": valid_decision["authorization_decision"],
            "reasons_fired": valid_decision["reasons_fired"],
            "claim_ceiling": CLAIM_CEILING,
        },
    ]
    for control in negative_controls["controls"]:
        events.append({"event": "negative_control_invoked", "run_id": run_id, **control})
    for ablation in ablations["ablations"]:
        events.append({"event": "ablation_invoked", "run_id": run_id, **ablation})
    for control in structure_controls["controls"]:
        events.append({"event": "dependency_structure_control_invoked", "run_id": run_id, **control})
    events.append(
        {
            "event": "repair_decision",
            "producer_function": "run_validator_gap_repair_001b",
            "run_id": run_id,
            "repair_result": "closed" if gap_closed else "not_closed",
            "claim_ceiling": CLAIM_CEILING,
        }
    )
    return {
        "task_id": TASK_ID,
        "producer_function": "build_authorization_recomputation_trace",
        "run_id": run_id,
        "events": events,
        "claim_ceiling": CLAIM_CEILING,
    }


def _write_report(repo_root: Path, result: dict[str, Any]) -> None:
    path = _doc_path(repo_root)
    text = f"""# {TASK_ID}

## Validator Gap Repair

Current layer: {LAYER}.

Mainline integration status: {MAINLINE_INTEGRATION}.

Enabled status: {ENABLED_STATUS}.

Real trigger evidence: `validate_authorization_manifest` recomputed the 001B
manifest under repaired validator code path hash
`{result["after_validator_code_path_hash"]}`. Original 001B manifest hash:
`{result["original_manifest_hash"]}`.

Observed validator gap: `{OBSERVED_GAP}`.

Before repair: `remove_validator_gap_repair_dependency` ->
`{result["before_after_gap_contrast"]["before"]["validator_decision"]}`.

After repair: `remove_validator_gap_repair_dependency` ->
`{result["before_after_gap_contrast"]["after"]["validator_decision"]}`.

Negative controls: {result["negative_controls_blocked_count"]}/6 blocked.

Ablations: {result["ablation_controls_blocked_count"]}/9 blocked.

Dependency-structure controls:
{result["dependency_structure_controls_blocked_count"]}/4 blocked.

Repair result: {result["repair_result"]}.

Claim ceiling: {CLAIM_CEILING}.

Decision: only whether the validator gap is closed. This document does not
authorize mechanism work.

## Artifact Readback

- Result: `artifacts/{TASK_SLUG}/result.json`
- Readback: `artifacts/{TASK_SLUG}/readback.json`
- Trace: `artifacts/{TASK_SLUG}/trace.json`
- Ablations: `artifacts/{TASK_SLUG}/ablation_results.json`
- Negative controls: `artifacts/{TASK_SLUG}/negative_controls.json`
- Before/after contrast: `artifacts/{TASK_SLUG}/before_after_gap_contrast.json`
- Claim ceiling: `artifacts/{TASK_SLUG}/claim_ceiling.txt`

## Stop Condition Check

Stop conditions triggered: {json.dumps(result["stop_conditions_triggered"], ensure_ascii=True)}.

## What This Does Not Prove

This does not prove mechanism validity, Gate validity, candidate behavior,
agency, autonomy, consciousness, emotion, subjectivity, EGO readiness, runtime
readiness, companion readiness, stable user benefit, or mainline effect.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
    write_report: bool | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    out = Path(output_dir) if output_dir is not None else _output_dir(root)
    out.mkdir(parents=True, exist_ok=True)
    should_write_report = output_dir is None if write_report is None else write_report
    validator = _load_validator(root)
    run_id = f"{TASK_SLUG}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"

    original_manifest = _load_json(_parent_manifest_path(root))
    repaired_manifest = _refresh_for_repaired_validator(original_manifest, validator)
    template = validator.build_authorization_manifest_template(root)
    enforcement = validator.validate_enforcement_artifacts(root)
    valid_decision = validator.validate_authorization_manifest(
        repaired_manifest,
        template,
        enforcement,
    )
    after_hash = validator._source_hash()
    repaired_manifest_hash = validator._manifest_integrity_hash(repaired_manifest)
    negative_controls = _negative_controls(validator, repaired_manifest, template, enforcement)
    ablations = _ablations(validator, repaired_manifest, template, enforcement)
    structure_controls = _dependency_structure_controls(
        validator,
        repaired_manifest,
        template,
        enforcement,
    )
    contrast = {
        "task_id": TASK_ID,
        "producer_function": "build_before_after_gap_contrast",
        "observed_gap": OBSERVED_GAP,
        "before": _before_gap_result(root),
        "after": _after_gap_result(ablations, after_hash),
        "claim_ceiling": CLAIM_CEILING,
    }

    stop_conditions: list[str] = []
    if ORIGINAL_MANIFEST_HASH != original_manifest.get("authorization_validator", {}).get(
        "manifest_hash"
    ):
        stop_conditions.append("original_manifest_hash_mismatch")
    if valid_decision["authorization_decision"] != "authorized":
        stop_conditions.append("repaired_validator_blocked_valid_001b_manifest")
    if not negative_controls["all_controls_blocked"]:
        stop_conditions.append("negative_control_authorized_after_repair")
    if not ablations["all_required_ablations_blocked"]:
        stop_conditions.append("required_ablation_authorized_after_repair")
    if not structure_controls["all_controls_blocked"]:
        stop_conditions.append("dependency_structure_control_authorized_after_repair")
    if contrast["before"]["validator_decision"] != "authorized":
        stop_conditions.append("before_gap_contrast_not_authorized")
    if contrast["after"]["validator_decision"] != "blocked":
        stop_conditions.append("after_gap_contrast_not_blocked")
    if repaired_manifest_hash == ORIGINAL_MANIFEST_HASH:
        stop_conditions.append("repaired_manifest_hash_did_not_change_with_validator_hash")

    gap_closed = not stop_conditions
    trace = _build_trace(
        run_id,
        root,
        repaired_manifest_hash,
        after_hash,
        valid_decision,
        negative_controls,
        ablations,
        structure_controls,
        gap_closed,
    )
    readback = {
        "task_id": TASK_ID,
        "producer_function": "validate_authorization_manifest",
        "parent_blocker_task": PARENT_BLOCKER_TASK,
        "parent_blocker_commit": PARENT_BLOCKER_COMMIT,
        "observed_gap": OBSERVED_GAP,
        "original_manifest_hash": ORIGINAL_MANIFEST_HASH,
        "before_validator_code_path_hash": BEFORE_VALIDATOR_CODE_PATH_HASH,
        "after_validator_code_path_hash": after_hash,
        "run_id": run_id,
        "input_manifest_path": _rel(_parent_manifest_path(root), root),
        "validator_result_path": _rel(out / "readback.json", root),
        "trace_path": _rel(out / "trace.json", root),
        "negative_controls_path": _rel(out / "negative_controls.json", root),
        "ablation_results_path": _rel(out / "ablation_results.json", root),
        "serialized_manifest": repaired_manifest,
        "repaired_manifest_hash": repaired_manifest_hash,
        "validator_decision": valid_decision,
        "dependency_readback": {
            "dependencies": repaired_manifest.get("dependencies", []),
            "dependency_task_ids": [
                dependency.get("task_id")
                for dependency in repaired_manifest.get("dependencies", [])
                if isinstance(dependency, dict) and dependency.get("required") is True
            ],
        },
        "scope_readback": repaired_manifest.get("scope", {}),
        "control_result_paths": {
            "negative_controls": _rel(out / "negative_controls.json", root),
            "ablations": _rel(out / "ablation_results.json", root),
            "before_after_gap_contrast": _rel(out / "before_after_gap_contrast.json", root),
        },
        "claim_ceiling": CLAIM_CEILING,
        "mechanism_execution": False,
        "mainline_integration": False,
        "enabled_status": ENABLED_STATUS,
        "repo_readback": {
            "branch": _git_stdout(root, ["branch", "--show-current"]),
            "head": _git_stdout(root, ["rev-parse", "HEAD"]),
            "status_short": _git_stdout(root, ["status", "--porcelain=v1"]),
            "ahead_behind": _git_stdout(root, ["rev-list", "--left-right", "--count", "HEAD...@{upstream}"]),
        },
    }
    result = {
        "task_id": TASK_ID,
        "verdict": PASS_VERDICT if gap_closed else BLOCKED_VERDICT,
        "repair_result": "closed" if gap_closed else "not_closed",
        "decision": "validator_gap_closed" if gap_closed else "validator_gap_not_closed",
        "current_layer": LAYER,
        "layer": LAYER,
        "mainline_integration": False,
        "mainline_integration_status": MAINLINE_INTEGRATION,
        "enabled_status": ENABLED_STATUS,
        "real_trigger_evidence": (
            "validate_authorization_manifest recomputed the 001B manifest, "
            "negative controls, ablations, and dependency-structure controls"
        ),
        "producer_function": "validate_authorization_manifest",
        "parent_blocker_task": PARENT_BLOCKER_TASK,
        "parent_blocker_commit": PARENT_BLOCKER_COMMIT,
        "observed_gap": OBSERVED_GAP,
        "original_manifest_hash": ORIGINAL_MANIFEST_HASH,
        "before_validator_code_path_hash": BEFORE_VALIDATOR_CODE_PATH_HASH,
        "after_validator_code_path_hash": after_hash,
        "run_id": run_id,
        "input_manifest_path": _rel(_parent_manifest_path(root), root),
        "validator_result_path": _rel(out / "readback.json", root),
        "trace_path": _rel(out / "trace.json", root),
        "negative_controls_path": _rel(out / "negative_controls.json", root),
        "ablation_results_path": _rel(out / "ablation_results.json", root),
        "before_after_gap_contrast": contrast,
        "negative_controls_all_blocked": negative_controls["all_controls_blocked"],
        "negative_controls_blocked_count": negative_controls["blocked_control_count"],
        "ablation_controls_all_blocked": ablations["all_required_ablations_blocked"],
        "ablation_controls_blocked_count": ablations["blocked_ablation_count"],
        "dependency_structure_controls_all_blocked": structure_controls["all_controls_blocked"],
        "dependency_structure_controls_blocked_count": structure_controls["blocked_control_count"],
        "stop_conditions_triggered": stop_conditions,
        "claim_ceiling": CLAIM_CEILING,
        "mechanism_execution": False,
        "mainline_integration_status_detail": MAINLINE_INTEGRATION,
        "auto_remote_anchor": {
            "decision": "conditional",
            "permitted": gap_closed,
            "claim_ceiling_if_performed": "remote-anchor publication and verification only",
        },
        "artifacts": {
            "result": _rel(out / "result.json", root),
            "readback": _rel(out / "readback.json", root),
            "trace": _rel(out / "trace.json", root),
            "ablation_results": _rel(out / "ablation_results.json", root),
            "negative_controls": _rel(out / "negative_controls.json", root),
            "before_after_gap_contrast": _rel(out / "before_after_gap_contrast.json", root),
            "claim_ceiling": _rel(out / "claim_ceiling.txt", root),
        },
        "next_minimal_closed_loop_action": (
            "Use the repaired validator only to rerun surface-admission authorization "
            "hygiene; do not enter mechanism execution from this result."
        ),
        "what_this_does_not_prove": WHAT_THIS_DOES_NOT_PROVE,
    }

    _write_json(out / "negative_controls.json", negative_controls)
    _write_json(out / "ablation_results.json", ablations)
    _write_json(out / "before_after_gap_contrast.json", contrast)
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
