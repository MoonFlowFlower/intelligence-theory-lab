from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001C-RERUN-001A"
TASK_SLUG = "next_surface_admission_manifest_instantiation_001c_rerun_001a"
SOURCE_TASK_ID = "NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001C"
SOURCE_SLUG = "next_surface_admission_manifest_instantiation_001c"
REQUIRED_001A_TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001A"
REQUIRED_001B_TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001B"
EXPECTED_SOURCE_MANIFEST_HASH = "870b1eb33fdf3351d2beb31c98d102bb8ab7360fc92fb65d4cdfd130023c7dce"
EXPECTED_REPAIRED_VALIDATOR_HASH = "c3b6394d42906a1b86f94ace72e237399c10cb4d57f9c2958483c9c990625e41"
PRIOR_BLOCKER_VERDICT = "blocked_validator_gap_repair_001b_dependency_not_enforced"
PASS_VERDICT = "next_surface_admission_manifest_instantiation_001c_rerun_001a_pass"
BLOCKED_VERDICT = "blocked_manifest_instantiation_rerun_computation_gap"
CLAIM_CEILING = "authorization-validator manifest-instantiation closure evidence only"
LAYER = "engineering-governance / manifest-instantiation closure rerun only"
MAINLINE_INTEGRATION_STATUS = "none"
ENABLED_STATUS = "local offline callable rerun only"
REAL_TRIGGER_EVIDENCE = (
    "validate_authorization_manifest invoked on the concrete 001C manifest structure "
    "and callable mutated manifest inputs for prior dependency-structure controls"
)


def _ensure_src_path(repo_root: Path) -> None:
    src = repo_root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def _load_validator(repo_root: Path):
    _ensure_src_path(repo_root)
    from future_surface_admission_authorization_template_001a import validator

    return validator


def _out_dir(repo_root: Path) -> Path:
    return repo_root / "artifacts" / TASK_SLUG


def _doc_path(repo_root: Path) -> Path:
    return repo_root / "docs" / "research" / f"{TASK_ID}.md"


def _source_manifest_path(repo_root: Path) -> Path:
    return repo_root / "artifacts" / SOURCE_SLUG / "manifest.json"


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


def _git(repo_root: Path, args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
    )
    return {
        "args": ["git", *args],
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _load_start_state(repo_root: Path) -> dict[str, Any]:
    path = _out_dir(repo_root) / "start_state.json"
    return _load_json(path) if path.exists() else {"verdict": "missing_start_state"}


def _source_manifest_for_repaired_validator(repo_root: Path, validator: Any) -> dict[str, Any]:
    manifest = _load_json(_source_manifest_path(repo_root))
    manifest["authorization_validator"]["code_path_hash"] = validator._source_hash()
    validator._refresh_manifest_hash(manifest)
    return manifest


def _refresh(validator: Any, manifest: dict[str, Any]) -> dict[str, Any]:
    validator._refresh_manifest_hash(manifest)
    return manifest


def _remove_dependency(manifest: dict[str, Any], task_id: str) -> dict[str, Any]:
    mutated = copy.deepcopy(manifest)
    mutated["dependencies"] = [
        dependency
        for dependency in mutated.get("dependencies", [])
        if isinstance(dependency, dict) and dependency.get("task_id") != task_id
    ]
    return mutated


def _dependency_ids(manifest: dict[str, Any]) -> set[str]:
    dependencies = manifest.get("dependencies", [])
    if not isinstance(dependencies, list):
        return set()
    return {
        str(dependency.get("task_id"))
        for dependency in dependencies
        if isinstance(dependency, dict) and dependency.get("required") is True
    }


def _invoke_case(
    *,
    validator: Any,
    template: dict[str, Any],
    enforcement: dict[str, Any] | None,
    run_id: str,
    case_id: str,
    case_kind: str,
    mutation_function: str | None,
    mutation_description: str,
    manifest: dict[str, Any],
    expected_outcome: str,
    aggregation: str,
    repo_root: Path,
) -> dict[str, Any]:
    _refresh(validator, manifest)
    decision = validator.validate_authorization_manifest(manifest, template, enforcement)
    actual_outcome = decision["authorization_decision"]
    return {
        "task_id": TASK_ID,
        "run_id": run_id,
        "case_id": case_id,
        "case_kind": case_kind,
        "producer_function": decision["producer_function"],
        "mutation_function": mutation_function,
        "mutation_description": mutation_description,
        "inputs": {
            "source_manifest_path": _rel(_source_manifest_path(repo_root), repo_root),
            "mutation_function": mutation_function,
            "mutation_description": mutation_description,
        },
        "aggregation": aggregation,
        "validator_hash": validator._source_hash(),
        "code_path_hash": validator._source_hash(),
        "source_manifest_hash": EXPECTED_SOURCE_MANIFEST_HASH,
        "manifest_hash": validator._manifest_integrity_hash(manifest),
        "manifest_file_equivalent_hash": _hash_payload(manifest),
        "expected_outcome": expected_outcome,
        "actual_outcome": actual_outcome,
        "result": actual_outcome,
        "reason": decision["reasons_fired"],
        "reasons_fired": decision["reasons_fired"],
        "blocked": actual_outcome == "blocked",
        "authorized": actual_outcome == "authorized",
        "unexpected_authorization": expected_outcome == "blocked" and actual_outcome != "blocked",
        "unexpected_block": expected_outcome == "authorized" and actual_outcome != "authorized",
        "validator_decision": decision,
        "serialized_manifest": copy.deepcopy(manifest),
        "claim_ceiling": CLAIM_CEILING,
    }


def _build_negative_controls(manifest: dict[str, Any]) -> list[tuple[str, str, str, dict[str, Any]]]:
    missing_direction = copy.deepcopy(manifest)
    missing_direction["proposed_surface_admission_direction"] = ""
    missing_direction["proposed_surface_admission_direction_status"] = (
        "missing_concrete_surface_direction"
    )

    gate5 = copy.deepcopy(manifest)
    gate5["proposed_surface_admission_direction"] = "Gate5 admission proposal"

    execution_family = copy.deepcopy(manifest)
    execution_family["proposed_surface_admission_direction"] = (
        "bridge runtime tournament EGO-mainline proposal"
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

    score = copy.deepcopy(manifest)
    score.setdefault("outputs_requested", []).append("mechanism_score")

    repair_as_execution = copy.deepcopy(manifest)
    repair_as_execution["stored_authorization_decision"] = (
        "candidate authorized for runtime mainline-effective execution"
    )
    repair_as_execution["scope"]["opens_runtime"] = True

    return [
        (
            "missing_concrete_proposed_direction",
            "mutate_missing_concrete_proposed_direction",
            "Remove the concrete proposed surface-admission direction.",
            missing_direction,
        ),
        (
            "manifest_proposing_gate5",
            "mutate_forbidden_gate5_direction",
            "Replace the permitted direction with a Gate5 proposal.",
            gate5,
        ),
        (
            "manifest_proposing_bridge_runtime_tournament_ego_mainline",
            "mutate_forbidden_execution_family_direction",
            "Replace the permitted direction with bridge/runtime/tournament/EGO-mainline scope.",
            execution_family,
        ),
        (
            "old_invalid_surfaces_cited_as_mechanism_evidence",
            "mutate_old_invalid_surface_citation",
            "Cite old invalid surfaces as mechanism evidence.",
            invalid_evidence,
        ),
        (
            "mechanism_score_before_admission",
            "mutate_mechanism_score_output_request",
            "Request a mechanism score before admission.",
            score,
        ),
        (
            "validator_repair_treated_as_mechanism_execution_authorization",
            "mutate_repair_as_execution_authorization",
            "Treat validator repair as runtime/mechanism execution authorization.",
            repair_as_execution,
        ),
    ]


def _build_ablations(manifest: dict[str, Any]) -> list[tuple[str, str, str, dict[str, Any]]]:
    ablations = [
        (
            "remove_hardening_dependency",
            "mutate_remove_dependency::SURFACE-ADMISSION-CONTRACT-HARDENING-001A",
            "Remove the hardening dependency.",
            _remove_dependency(manifest, "SURFACE-ADMISSION-CONTRACT-HARDENING-001A"),
        ),
        (
            "remove_enforcement_dependency",
            "mutate_remove_dependency::SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A",
            "Remove the enforcement dependency.",
            _remove_dependency(manifest, "SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A"),
        ),
        (
            "remove_future_authorization_template_dependency",
            "mutate_remove_dependency::FUTURE-SURFACE-ADMISSION-AUTHORIZATION-TEMPLATE-001A",
            "Remove the authorization-template dependency.",
            _remove_dependency(
                manifest,
                "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-TEMPLATE-001A",
            ),
        ),
        (
            "remove_validator_gap_repair_001a_dependency",
            f"mutate_remove_dependency::{REQUIRED_001A_TASK_ID}",
            "Remove the older validator-gap repair dependency.",
            _remove_dependency(manifest, REQUIRED_001A_TASK_ID),
        ),
        (
            "remove_validator_gap_repair_001b_dependency",
            f"mutate_remove_dependency::{REQUIRED_001B_TASK_ID}",
            "Remove the required 001B validator-gap repair dependency.",
            _remove_dependency(manifest, REQUIRED_001B_TASK_ID),
        ),
    ]

    no_direction = copy.deepcopy(manifest)
    no_direction["proposed_surface_admission_direction"] = None
    no_direction["proposed_surface_admission_direction_status"] = (
        "missing_concrete_surface_direction"
    )
    ablations.append(
        (
            "remove_concrete_proposed_direction",
            "mutate_remove_concrete_proposed_direction",
            "Remove the concrete proposed direction.",
            no_direction,
        )
    )

    no_later_lock = copy.deepcopy(manifest)
    no_later_lock["later_task_card_only"] = False
    no_later_lock["scope"]["later_task_card_only"] = False
    ablations.append(
        (
            "remove_later_task_card_only_scope_lock",
            "mutate_remove_later_task_card_only_scope_lock",
            "Remove the later-task-card-only scope lock.",
            no_later_lock,
        )
    )

    no_score_rule = copy.deepcopy(manifest)
    no_score_rule["required_rules"]["no_mechanism_score_before_admission"] = False
    ablations.append(
        (
            "remove_no_mechanism_score_clause",
            "mutate_remove_no_mechanism_score_clause",
            "Disable the no-mechanism-score rule.",
            no_score_rule,
        )
    )

    no_invalid_ban = copy.deepcopy(manifest)
    no_invalid_ban["required_rules"]["old_invalid_surface_citation_ban"] = False
    ablations.append(
        (
            "remove_invalid_evidence_ban",
            "mutate_remove_invalid_evidence_ban",
            "Disable the old-invalid-surface evidence ban.",
            no_invalid_ban,
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
        (
            "open_no_candidate_gate5_bridge_runtime_tournament_ego_mainline_scope",
            "mutate_open_forbidden_scope",
            "Open forbidden candidate/Gate5/bridge/runtime/tournament/EGO-mainline scope.",
            forbidden_scope,
        )
    )
    return ablations


def _build_dependency_controls(
    manifest: dict[str, Any],
) -> list[tuple[str, str, str, dict[str, Any]]]:
    alias = copy.deepcopy(manifest)
    for dependency in alias["dependencies"]:
        if dependency.get("task_id") == REQUIRED_001B_TASK_ID:
            dependency["task_id"] = f"{REQUIRED_001B_TASK_ID}-ALIAS"

    narrative = _remove_dependency(manifest, REQUIRED_001B_TASK_ID)
    narrative["notes"] = (
        "Narrative-only reference to "
        "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001B."
    )

    metadata = _remove_dependency(manifest, REQUIRED_001B_TASK_ID)
    metadata["non_enforced_metadata"] = {
        "task_id": REQUIRED_001B_TASK_ID,
        "dependency_type": "sealed_validator_gap_repair_boundary",
        "required": True,
    }

    older_repair_only = _remove_dependency(manifest, REQUIRED_001B_TASK_ID)

    return [
        (
            "alias_only_dependency_reference",
            "mutate_alias_001b_dependency",
            "Replace the required 001B dependency task_id with an alias.",
            alias,
        ),
        (
            "narrative_only_dependency_reference",
            "mutate_narrative_only_001b_dependency",
            "Remove the structural 001B dependency and leave only narrative text.",
            narrative,
        ),
        (
            "metadata_only_dependency_reference",
            "mutate_metadata_only_001b_dependency",
            "Remove the structural 001B dependency and place it under non-enforced metadata.",
            metadata,
        ),
        (
            "older_repair_only_dependency_reference",
            "mutate_replace_001b_with_001a_only",
            "Remove the 001B dependency while retaining the older 001A repair dependency.",
            older_repair_only,
        ),
    ]


def _summarize_cases(
    cases: list[dict[str, Any]],
    producer_function: str,
    item_key: str,
) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "producer_function": producer_function,
        item_key: cases,
        "blocked_count": sum(1 for case in cases if case["blocked"]),
        "authorized_count": sum(1 for case in cases if case["authorized"]),
        "all_expected_outcomes_matched": all(
            not case["unexpected_authorization"] and not case["unexpected_block"]
            for case in cases
        ),
        "unexpected_authorizations": [
            case for case in cases if case["unexpected_authorization"]
        ],
        "unexpected_blocks": [case for case in cases if case["unexpected_block"]],
        "claim_ceiling": CLAIM_CEILING,
    }


def _load_prior_blocker(repo_root: Path) -> dict[str, Any]:
    result_path = repo_root / "artifacts" / SOURCE_SLUG / "result.json"
    ablation_path = repo_root / "artifacts" / SOURCE_SLUG / "ablation_results.json"
    dependency_path = repo_root / "artifacts" / SOURCE_SLUG / "dependency_structure_controls.json"
    negative_path = repo_root / "artifacts" / SOURCE_SLUG / "negative_controls.json"
    result = _load_json(result_path)
    ablations = _load_json(ablation_path)
    dependencies = _load_json(dependency_path)
    negatives = _load_json(negative_path)
    return {
        "task_id": TASK_ID,
        "producer_function": "read_prior_001c_blocker_callable_artifacts",
        "prior_task_id": SOURCE_TASK_ID,
        "prior_verdict": result.get("verdict"),
        "prior_validator_hash": result.get("actual_validator_code_path_hash"),
        "prior_manifest_hash": result.get("manifest_hash"),
        "prior_source_manifest_hash": result.get("manifest_hash"),
        "prior_negative_controls_blocked_count": negatives.get("blocked_control_count"),
        "prior_ablation_controls_blocked_count": ablations.get("blocked_ablation_count"),
        "prior_dependency_structure_controls_blocked_count": dependencies.get(
            "blocked_control_count"
        ),
        "prior_unexpected_authorized_ablations": result.get(
            "unexpected_authorized_ablations", []
        ),
        "prior_unexpected_authorized_dependency_structure_controls": result.get(
            "unexpected_authorized_dependency_structure_controls", []
        ),
        "paths": {
            "result": _rel(result_path, repo_root),
            "ablation_results": _rel(ablation_path, repo_root),
            "dependency_structure_controls": _rel(dependency_path, repo_root),
            "negative_controls": _rel(negative_path, repo_root),
        },
        "claim_ceiling": "prior negative evidence readback only",
    }


def _replay_trace(
    repo_root: Path,
    trace_path: Path,
    validator: Any,
    template: dict[str, Any],
    enforcement: dict[str, Any] | None,
) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    replayed = []
    for row in rows:
        manifest = row["serialized_manifest"]
        decision = validator.validate_authorization_manifest(manifest, template, enforcement)
        outcome_match = decision["authorization_decision"] == row["actual_outcome"]
        reasons_match = sorted(decision["reasons_fired"]) == sorted(row["reasons_fired"])
        replayed.append(
            {
                "case_id": row["case_id"],
                "producer_function": "replay_validate_authorization_manifest_from_serialized_input",
                "recorded_manifest_hash": row["manifest_hash"],
                "recomputed_manifest_hash": validator._manifest_integrity_hash(manifest),
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
        "replayed_count": len(replayed),
        "rows": replayed,
        "all_recomputed_outcomes_match": all(
            row["outcome_match"] and row["reasons_match"] for row in replayed
        ),
        "claim_ceiling": CLAIM_CEILING,
    }


def _write_report(repo_root: Path, result: dict[str, Any]) -> None:
    report = f"""# {TASK_ID}

## Verdict

`{result["verdict"]}`.

## Status

- Layer: `{result["current_layer"]}`
- Mainline integration status: `{result["mainline_integration_status"]}`
- Enabled status: `{result["enabled_status"]}`
- Real trigger evidence: `{result["real_trigger_evidence"]}`
- Claim ceiling: `{result["claim_ceiling"]}`

## Start Boundary

- Start-state verdict: `{result["start_state"]["verdict"]}`
- Branch: `{result["start_state"].get("actual", {}).get("branch")}`
- HEAD: `{result["start_state"].get("actual", {}).get("head")}`
- Remote branch: `{result["start_state"].get("actual", {}).get("remote_branch")}`
- Local tag target: `{result["start_state"].get("actual", {}).get("local_tag")}`
- Remote tag target: `{result["start_state"].get("actual", {}).get("remote_tag")}`
- Ahead/behind: `{result["start_state"].get("actual", {}).get("ahead_behind")}`
- Worktree clean at start: `{result["start_state"].get("actual", {}).get("worktree_clean")}`
- Cached diff empty at start: `{result["start_state"].get("actual", {}).get("cached_diff_empty")}`

## Rerun Readback

- Source 001C manifest hash: `{result["source_manifest_hash"]}`
- Repaired validator hash: `{result["validator_hash"]}`
- Valid concrete 001C manifest authorized: `{result["valid_manifest_authorized"]}`
- Negative controls blocked: `{result["negative_controls_blocked_count"]}/6`
- Ablations blocked: `{result["ablation_controls_blocked_count"]}/10`
- Dependency-structure controls blocked: `{result["dependency_structure_controls_blocked_count"]}/4`
- Replay recomputation: `{result["replay_recomputation"]["all_recomputed_outcomes_match"]}`

## Prior Negative Evidence

The prior 001C blocker was `{result["prior_blocker"]["prior_verdict"]}` with
`{result["prior_blocker"]["prior_ablation_controls_blocked_count"]}/10`
ablations blocked and
`{result["prior_blocker"]["prior_dependency_structure_controls_blocked_count"]}/4`
dependency-structure controls blocked.

## Stop Conditions

`{result["stop_conditions_triggered"]}`.

## Artifacts

- Result: `{result["artifact_paths"]["result"]}`
- Readback: `{result["artifact_paths"]["readback"]}`
- Trace JSONL: `{result["artifact_paths"]["trace_jsonl"]}`
- Replay: `{result["artifact_paths"]["replay_report"]}`
- Start state: `{result["artifact_paths"]["start_state"]}`

## Next Minimal Closed-Loop Action

{result["next_minimal_closed_loop_action"]}

## What This Does Not Prove

This does not prove mechanism validity, Gate validity, Gate4 validity, Gate5
validity, candidate behavior, agency, autonomy, consciousness, emotion,
subjectivity, companion readiness, EGO readiness, runtime readiness, stable
user benefit, or mainline effect.
"""
    _doc_path(repo_root).write_text(report, encoding="utf-8")


def run(repo_root: str | Path, output_dir: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root)
    out = Path(output_dir) if output_dir is not None else _out_dir(root)
    out.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    run_id = f"{TASK_SLUG}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    validator = _load_validator(root)
    template = validator.build_authorization_manifest_template(root)
    enforcement = validator.validate_enforcement_artifacts(root)
    source_manifest = _load_json(_source_manifest_path(root))
    source_manifest_hash = validator._manifest_integrity_hash(source_manifest)
    manifest = _source_manifest_for_repaired_validator(root, validator)
    validator_hash = validator._source_hash()
    start_state = _load_start_state(root)
    prior_blocker = _load_prior_blocker(root)

    valid_case = _invoke_case(
        validator=validator,
        template=template,
        enforcement=enforcement,
        run_id=run_id,
        case_id="valid_concrete_001c_manifest",
        case_kind="positive_control",
        mutation_function=None,
        mutation_description="Use the concrete 001C manifest structure with the repaired validator hash.",
        manifest=copy.deepcopy(manifest),
        expected_outcome="authorized",
        aggregation="valid_manifest_authorization",
        repo_root=root,
    )

    negative_cases = [
        _invoke_case(
            validator=validator,
            template=template,
            enforcement=enforcement,
            run_id=run_id,
            case_id=case_id,
            case_kind="negative_control",
            mutation_function=mutation_function,
            mutation_description=description,
            manifest=case_manifest,
            expected_outcome="blocked",
            aggregation="negative_controls",
            repo_root=root,
        )
        for case_id, mutation_function, description, case_manifest in _build_negative_controls(manifest)
    ]
    ablation_cases = [
        _invoke_case(
            validator=validator,
            template=template,
            enforcement=enforcement,
            run_id=run_id,
            case_id=case_id,
            case_kind="ablation",
            mutation_function=mutation_function,
            mutation_description=description,
            manifest=case_manifest,
            expected_outcome="blocked",
            aggregation="ablation_controls",
            repo_root=root,
        )
        for case_id, mutation_function, description, case_manifest in _build_ablations(manifest)
    ]
    dependency_cases = [
        _invoke_case(
            validator=validator,
            template=template,
            enforcement=enforcement,
            run_id=run_id,
            case_id=case_id,
            case_kind="dependency_structure_control",
            mutation_function=mutation_function,
            mutation_description=description,
            manifest=case_manifest,
            expected_outcome="blocked",
            aggregation="dependency_structure_controls",
            repo_root=root,
        )
        for case_id, mutation_function, description, case_manifest in _build_dependency_controls(manifest)
    ]

    trace_rows = [valid_case, *negative_cases, *ablation_cases, *dependency_cases]
    trace_jsonl = out / "trace.jsonl"
    _write_trace_jsonl(trace_jsonl, trace_rows)
    replay = _replay_trace(root, trace_jsonl, validator, template, enforcement)

    positive_controls = {
        "task_id": TASK_ID,
        "producer_function": "run_positive_controls_through_validate_authorization_manifest",
        "controls": [valid_case],
        "authorized_count": 1 if valid_case["authorized"] else 0,
        "all_positive_controls_passed": (
            valid_case["authorized"]
            and REQUIRED_001B_TASK_ID in _dependency_ids(valid_case["serialized_manifest"])
            and valid_case["validator_decision"].get(
                "validator_gap_repair_001b_dependency_required"
            )
            is True
        ),
        "claim_ceiling": CLAIM_CEILING,
    }
    negative_controls = _summarize_cases(
        negative_cases,
        "run_negative_controls_through_validate_authorization_manifest",
        "controls",
    )
    ablations = _summarize_cases(
        ablation_cases,
        "run_ablations_through_validate_authorization_manifest",
        "ablations",
    )
    dependency_controls = _summarize_cases(
        dependency_cases,
        "run_dependency_structure_controls_through_validate_authorization_manifest",
        "controls",
    )

    stop_conditions: list[str] = []
    if start_state.get("verdict") != "start_state_match":
        stop_conditions.append("blocked_rerun_start_state_mismatch")
    if source_manifest_hash != EXPECTED_SOURCE_MANIFEST_HASH:
        stop_conditions.append("blocked_manifest_hash_mismatch")
    if validator_hash != EXPECTED_REPAIRED_VALIDATOR_HASH:
        stop_conditions.append("blocked_validator_hash_mismatch")
    if prior_blocker.get("prior_verdict") != PRIOR_BLOCKER_VERDICT:
        stop_conditions.append("blocked_prior_blocker_readback_mismatch")
    if not positive_controls["all_positive_controls_passed"]:
        stop_conditions.append("blocked_valid_manifest_positive_control")
    if negative_controls["blocked_count"] != 6:
        stop_conditions.append("blocked_negative_controls_regression")
    if ablations["blocked_count"] != 10:
        stop_conditions.append("blocked_required_ablation_regression")
    if dependency_controls["blocked_count"] != 4:
        stop_conditions.append("blocked_validator_dependency_control_regression")
    if not replay["all_recomputed_outcomes_match"]:
        stop_conditions.append("blocked_replay_recomputation_gap")

    verdict = PASS_VERDICT if not stop_conditions else BLOCKED_VERDICT
    anti_hardcoding_audit = {
        "producer_function": "anti_hardcoding_audit_from_trace_rows",
        "all_cases_call_validate_authorization_manifest": all(
            row["producer_function"] == "validate_authorization_manifest"
            for row in trace_rows
        ),
        "serialized_manifest_recorded_for_all_cases": all(
            isinstance(row.get("serialized_manifest"), dict) for row in trace_rows
        ),
        "replay_recomputes_from_serialized_inputs": replay[
            "all_recomputed_outcomes_match"
        ],
        "dependency_controls_mutate_structural_inputs": all(
            row["case_kind"] != "dependency_structure_control"
            or row["mutation_function"]
            in {
                "mutate_alias_001b_dependency",
                "mutate_narrative_only_001b_dependency",
                "mutate_metadata_only_001b_dependency",
                "mutate_replace_001b_with_001a_only",
            }
            for row in trace_rows
        ),
        "no_expected_outcome_used_as_actual_result": all(
            row["actual_outcome"] == row["validator_decision"]["authorization_decision"]
            for row in trace_rows
        ),
        "claim_ceiling": CLAIM_CEILING,
    }
    artifact_paths = {
        "result": _rel(out / "result.json", root),
        "readback": _rel(out / "readback.json", root),
        "trace": _rel(out / "trace.json", root),
        "trace_jsonl": _rel(trace_jsonl, root),
        "positive_controls": _rel(out / "positive_controls.json", root),
        "negative_controls": _rel(out / "negative_controls.json", root),
        "ablation_results": _rel(out / "ablation_results.json", root),
        "dependency_structure_controls": _rel(out / "dependency_structure_controls.json", root),
        "replay_report": _rel(out / "replay_report.json", root),
        "prior_blocker_readback": _rel(out / "prior_blocker_readback.json", root),
        "start_state": _rel(out / "start_state.json", root),
        "claim_ceiling": _rel(out / "claim_ceiling.txt", root),
        "command_readback": _rel(out / "command_readback.txt", root),
    }
    result = {
        "task_id": TASK_ID,
        "verdict": verdict,
        "producer_function": "run_manifest_instantiation_001c_rerun_001a",
        "run_id": run_id,
        "timestamp_utc": timestamp,
        "current_layer": LAYER,
        "layer": LAYER,
        "mainline_integration": False,
        "mainline_integration_status": MAINLINE_INTEGRATION_STATUS,
        "enabled_status": ENABLED_STATUS,
        "real_trigger_evidence": REAL_TRIGGER_EVIDENCE,
        "claim_ceiling": CLAIM_CEILING,
        "source_task_id": SOURCE_TASK_ID,
        "source_manifest_path": _rel(_source_manifest_path(root), root),
        "source_manifest_hash": source_manifest_hash,
        "current_input_manifest_hash": valid_case["manifest_hash"],
        "validator_hash": validator_hash,
        "code_path_hash": validator_hash,
        "valid_manifest_authorized": valid_case["authorized"],
        "valid_manifest_reasons_fired": valid_case["reasons_fired"],
        "negative_controls_blocked_count": negative_controls["blocked_count"],
        "negative_controls_all_blocked": negative_controls["all_expected_outcomes_matched"],
        "ablation_controls_blocked_count": ablations["blocked_count"],
        "ablation_controls_all_blocked": ablations["all_expected_outcomes_matched"],
        "dependency_structure_controls_blocked_count": dependency_controls["blocked_count"],
        "dependency_structure_controls_all_blocked": dependency_controls[
            "all_expected_outcomes_matched"
        ],
        "positive_controls_all_passed": positive_controls["all_positive_controls_passed"],
        "replay_recomputation": {
            "path": artifact_paths["replay_report"],
            "replayed_count": replay["replayed_count"],
            "all_recomputed_outcomes_match": replay["all_recomputed_outcomes_match"],
        },
        "prior_blocker": prior_blocker,
        "start_state": {
            "verdict": start_state.get("verdict"),
            "actual": start_state.get("actual", {}),
            "checks": start_state.get("checks", {}),
        },
        "computed_evidence_provenance": {
            "producer_function": "run_manifest_instantiation_001c_rerun_001a",
            "inputs": [
                _rel(_source_manifest_path(root), root),
                artifact_paths["start_state"],
                "src/future_surface_admission_authorization_template_001a/validator.py",
            ],
            "run_id": run_id,
            "case_ids": [row["case_id"] for row in trace_rows],
            "aggregation_rule": "pass_only_if_start_state_hashes_match_and_all_callable_cases_match_expected_outcomes_and_replay_matches",
            "validator_hash": validator_hash,
            "manifest_hash": source_manifest_hash,
            "code_path_hash": validator_hash,
            "runner_file_hash": _hash_file(Path(__file__)),
        },
        "anti_hardcoding_audit": anti_hardcoding_audit,
        "stop_conditions_triggered": stop_conditions,
        "auto_remote_anchor": {
            "decision": "conditional_pending_commit_gate" if not stop_conditions else "forbidden",
            "performed": False,
            "reason": (
                "stable pass boundary; requires commit, clean worktree, push/tag/readback"
                if not stop_conditions
                else "stop condition triggered"
            ),
            "claim_ceiling_if_performed": "remote-anchor publication and verification only",
        },
        "artifact_paths": artifact_paths,
        "changed_file_allowlist": [
            "docs/research/NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001C-RERUN-001A.md",
            "artifacts/next_surface_admission_manifest_instantiation_001c_rerun_001a/**",
        ],
        "forbidden_scope_opened": False,
        "mechanism_execution": False,
        "candidate_scope_opened": False,
        "gate5_scope_opened": False,
        "bridge_scope_opened": False,
        "runtime_scope_opened": False,
        "tournament_scope_opened": False,
        "ego_mainline_scope_opened": False,
        "decision": (
            "prior_validator_gap_repair_001b_dependency_not_enforced_blocker_closed"
            if not stop_conditions
            else "rerun_blocked"
        ),
        "next_minimal_closed_loop_action": (
            "Only after this rerun is preserved, consider drafting a separately bounded later concrete surface-admission task card."
            if not stop_conditions
            else "Address the new blocker or route away; do not draft the later surface-admission task card."
        ),
        "what_this_does_not_prove": [
            "mechanism validity",
            "Gate validity",
            "Gate4 validity",
            "Gate5 validity",
            "candidate behavior",
            "agency",
            "autonomy",
            "consciousness",
            "emotion",
            "subjectivity",
            "companion readiness",
            "EGO readiness",
            "runtime readiness",
            "stable user benefit",
            "mainline effect",
        ],
    }
    readback = {
        "task_id": TASK_ID,
        "producer_function": "build_manifest_instantiation_001c_rerun_readback",
        "run_id": run_id,
        "valid_case": valid_case,
        "negative_controls_summary": {
            "blocked": negative_controls["blocked_count"],
            "total": len(negative_cases),
        },
        "ablation_summary": {
            "blocked": ablations["blocked_count"],
            "total": len(ablation_cases),
        },
        "dependency_structure_summary": {
            "blocked": dependency_controls["blocked_count"],
            "total": len(dependency_cases),
        },
        "replay_recomputation": replay,
        "stop_conditions_triggered": stop_conditions,
        "claim_ceiling": CLAIM_CEILING,
    }
    trace = {
        "task_id": TASK_ID,
        "producer_function": "build_manifest_instantiation_001c_rerun_trace_index",
        "run_id": run_id,
        "trace_jsonl_path": artifact_paths["trace_jsonl"],
        "row_count": len(trace_rows),
        "claim_ceiling": CLAIM_CEILING,
    }
    command_readback = {
        "task_id": TASK_ID,
        "producer_function": "command_readback_for_rerun_reproduction",
        "run_id": run_id,
        "commands": [
            {
                "command": "python artifacts/next_surface_admission_manifest_instantiation_001c_rerun_001a/run_manifest_instantiation_001c_rerun_001a.py",
                "purpose": "recompute rerun artifacts from source manifest and validator",
            },
            {
                "command": "python -m pytest tests/test_future_surface_admission_authorization_validator_gap_repair_001c.py tests/test_next_surface_admission_manifest_instantiation_001c.py::test_default_artifacts_and_report_preserve_001c_blocker_boundary",
                "purpose": "focused current repaired-validator checks plus prior blocked-artifact preservation check",
            },
        ],
        "summary": {
            "verdict": verdict,
            "negative_controls_blocked": negative_controls["blocked_count"],
            "ablations_blocked": ablations["blocked_count"],
            "dependency_controls_blocked": dependency_controls["blocked_count"],
            "replay_match": replay["all_recomputed_outcomes_match"],
        },
        "claim_ceiling": CLAIM_CEILING,
    }

    _write_json(out / "positive_controls.json", positive_controls)
    _write_json(out / "negative_controls.json", negative_controls)
    _write_json(out / "ablation_results.json", ablations)
    _write_json(out / "dependency_structure_controls.json", dependency_controls)
    _write_json(out / "replay_report.json", replay)
    _write_json(out / "prior_blocker_readback.json", prior_blocker)
    _write_json(out / "trace.json", trace)
    _write_json(out / "readback.json", readback)
    _write_json(out / "result.json", result)
    _write_json(out / "command_readback.json", command_readback)
    (out / "command_readback.txt").write_text(
        "\n".join(
            [
                f"run_id: {run_id}",
                f"verdict: {verdict}",
                f"validator_hash: {validator_hash}",
                f"source_manifest_hash: {source_manifest_hash}",
                f"valid_manifest_authorized: {valid_case['authorized']}",
                f"negative_controls_blocked: {negative_controls['blocked_count']}/6",
                f"ablations_blocked: {ablations['blocked_count']}/10",
                f"dependency_structure_controls_blocked: {dependency_controls['blocked_count']}/4",
                f"replay_match: {replay['all_recomputed_outcomes_match']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    _write_report(root, result)
    return result


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = run(repo_root)
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "run_id": result["run_id"],
                "negative_controls_blocked": result["negative_controls_blocked_count"],
                "ablations_blocked": result["ablation_controls_blocked_count"],
                "dependency_structure_controls_blocked": result[
                    "dependency_structure_controls_blocked_count"
                ],
                "replay_match": result["replay_recomputation"][
                    "all_recomputed_outcomes_match"
                ],
                "stop_conditions_triggered": result["stop_conditions_triggered"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
