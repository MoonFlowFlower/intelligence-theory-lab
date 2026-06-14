from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001B"
TASK_SLUG = "next_surface_admission_manifest_instantiation_001b"
CLAIM_CEILING = "surface-admission authorization hygiene only"
LAYER = "engineering-governance / authorization manifest instantiation only"
MAINLINE_INTEGRATION = "none"
ENABLED_STATUS = "local offline validator invocation only"
PROPOSED_DIRECTION = (
    "Minimal non-candidate surface-admission preflight for a future "
    "mechanism-family direction"
)
DECISION_BLOCKED = "later_task_card_drafting_not_authorized"
DECISION_AUTHORIZED = "later_task_card_drafting_authorized_only"
BLOCKED_VERDICT = "blocked_validator_gap_repair_dependency_ablation_authorized"
AUTHORIZED_VERDICT = "authorized_later_task_card_drafting_only"
GAP_REPAIR_TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001A"
TEMPLATE_TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-TEMPLATE-001A"
HARDENING_TASK_ID = "SURFACE-ADMISSION-CONTRACT-HARDENING-001A"
ENFORCEMENT_TASK_ID = "SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A"
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
INVALID_EVIDENCE_SURFACES = [
    "COMPOSITE-CTSR pass-chain",
    "CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A",
    "ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A",
]
DEPENDENCY_SPECS = {
    HARDENING_TASK_ID: {
        "artifact_id": "surface_admission_contract_hardening_001a",
        "result_path": "artifacts/surface_admission_contract_hardening_001a/result.json",
        "readback_path": "artifacts/surface_admission_contract_hardening_001a/readback.json",
        "required_verdict": "contract_hardened_pass",
        "dependency_type": "pre_execution_contract",
        "tag": "remote-anchor-surface-admission-contract-hardening-001a-verdict-enum-reconciliation-001a-915d4c5",
    },
    ENFORCEMENT_TASK_ID: {
        "artifact_id": "surface_admission_contract_enforcement_001a",
        "result_path": "artifacts/surface_admission_contract_enforcement_001a/result.json",
        "readback_path": "artifacts/surface_admission_contract_enforcement_001a/readback.json",
        "required_verdict": "contract_enforcement_pass",
        "dependency_type": "pre_execution_authorization_checker",
        "tag": "remote-anchor-surface-admission-contract-enforcement-001a-22d8a09",
    },
    TEMPLATE_TASK_ID: {
        "artifact_id": "future_surface_admission_authorization_template_001a",
        "result_path": "artifacts/future_surface_admission_authorization_template_001a/result.json",
        "readback_path": "artifacts/future_surface_admission_authorization_template_001a/readback.json",
        "template_path": (
            "artifacts/future_surface_admission_authorization_template_001a/"
            "authorization_manifest_template.json"
        ),
        "required_verdict": "future_surface_admission_authorization_template_001a_pass",
        "dependency_type": "pre_execution_authorization_manifest_template",
        "tag": "remote-anchor-future-surface-admission-authorization-template-001a-d23a2ba",
    },
    GAP_REPAIR_TASK_ID: {
        "artifact_id": "future_surface_admission_authorization_validator_gap_repair_001a",
        "result_path": (
            "artifacts/future_surface_admission_authorization_validator_gap_repair_001a/"
            "repair_result.json"
        ),
        "readback_path": (
            "artifacts/future_surface_admission_authorization_validator_gap_repair_001a/"
            "validator_gap_inventory.json"
        ),
        "trace_path": (
            "artifacts/future_surface_admission_authorization_validator_gap_repair_001a/"
            "repair_trace.jsonl"
        ),
        "required_verdict": (
            "future_surface_admission_authorization_validator_gap_repair_001a_pass"
        ),
        "dependency_type": "sealed_validator_gap_repair_boundary",
        "tag": "remote-anchor-future-surface-admission-authorization-validator-gap-repair-001a-b4d7c08",
    },
}


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


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _canonical_artifact_rel(output_dir: Path, filename: str, repo_root: Path) -> str:
    path = output_dir / filename
    try:
        return str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        return f"artifacts/{TASK_SLUG}/{filename}"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _write_trace_jsonl(path: Path, events: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(event, sort_keys=True, ensure_ascii=True) + "\n" for event in events),
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


def _hash_payload(payload: Any) -> str:
    return _hash_bytes(json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8"))


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


def _artifact_verdict(repo_root: Path, spec: dict[str, Any]) -> str | None:
    result_path = repo_root / spec["result_path"]
    if not result_path.exists():
        return None
    payload = _load_json(result_path)
    return payload.get("verdict") or payload.get("authorization_validator_decision")


def _dependency_readback(repo_root: Path) -> dict[str, Any]:
    dependencies: dict[str, Any] = {}
    for task_id, spec in DEPENDENCY_SPECS.items():
        tag = spec["tag"]
        result_path = repo_root / spec["result_path"]
        readback_path = repo_root / spec["readback_path"]
        dependencies[task_id] = {
            "task_id": task_id,
            "artifact_id": spec["artifact_id"],
            "dependency_type": spec["dependency_type"],
            "required": True,
            "required_verdict": spec["required_verdict"],
            "observed_verdict": _artifact_verdict(repo_root, spec),
            "tag": tag,
            "local_tag_commit": _git_stdout(repo_root, ["rev-parse", f"{tag}^{{commit}}"]),
            "result_path": spec["result_path"],
            "result_sha256": _hash_file(result_path),
            "readback_path": spec["readback_path"],
            "readback_sha256": _hash_file(readback_path),
        }
        if "template_path" in spec:
            template_path = repo_root / spec["template_path"]
            dependencies[task_id]["template_path"] = spec["template_path"]
            dependencies[task_id]["template_sha256"] = _hash_file(template_path)
        if "trace_path" in spec:
            trace_path = repo_root / spec["trace_path"]
            dependencies[task_id]["trace_path"] = spec["trace_path"]
            dependencies[task_id]["trace_sha256"] = _hash_file(trace_path)
    return {
        "producer_function": "dependency_readback",
        "repo": {
            "branch": _git_stdout(repo_root, ["branch", "--show-current"]),
            "head": _git_stdout(repo_root, ["rev-parse", "HEAD"]),
            "status_short": _git_stdout(repo_root, ["status", "--porcelain=v1"]),
            "ahead_behind": _git_stdout(repo_root, ["rev-list", "--left-right", "--count", "HEAD...@{upstream}"]),
        },
        "dependencies": dependencies,
    }


def _dependency_manifest(task_id: str, readback: dict[str, Any]) -> dict[str, Any]:
    dep = readback["dependencies"][task_id]
    payload = {
        "task_id": task_id,
        "artifact_id": dep["artifact_id"],
        "required_verdict": dep["required_verdict"],
        "observed_verdict": dep["observed_verdict"],
        "dependency_type": dep["dependency_type"],
        "required": True,
        "tag": dep["tag"],
        "commit": dep["local_tag_commit"],
        "result_path": dep["result_path"],
        "readback_path": dep["readback_path"],
        "result_sha256": dep["result_sha256"],
        "readback_sha256": dep["readback_sha256"],
    }
    for optional in ["template_path", "template_sha256", "trace_path", "trace_sha256"]:
        if optional in dep:
            payload[optional] = dep[optional]
    return payload


def _build_manifest(
    repo_root: Path,
    output_dir: Path,
    validator: Any,
    template: dict[str, Any],
    dependency_readback: dict[str, Any],
) -> dict[str, Any]:
    manifest = copy.deepcopy(template["example_authorized_manifest"])
    manifest["task_id"] = TASK_ID
    manifest["current_layer"] = LAYER
    manifest["claim_ceiling"] = CLAIM_CEILING
    manifest["proposed_surface_admission_direction"] = PROPOSED_DIRECTION
    manifest["purpose"] = (
        "Admit only the right to draft a later concrete surface-admission task "
        "card for a future mechanism-family direction."
    )
    manifest["scope_lock"] = "later_task_card_drafting_only"
    manifest["explicit_non_scope"] = [
        "No CTSR redesign.",
        "No ACTION-CONDITIONED repair.",
        "No Gate4 candidate.",
        "No Gate5.",
        "No bridge.",
        "No runtime.",
        "No tournament.",
        "No EGO-mainline.",
        "No companion readiness.",
        "No stable user benefit.",
        "No mechanism deployment.",
        "No candidate behavior execution.",
    ]
    manifest["invalid_evidence_ban"] = {
        "banned_as_mechanism_evidence": INVALID_EVIDENCE_SURFACES,
        "may_be_referenced_only_as": "negative_or_invalid_harness_evidence",
    }
    manifest["required_proposed_direction_preconditions"] = {
        "independent_callable_baseline": True,
        "real_ablation_path": True,
        "leakage_positive_control": True,
        "replay_recomputation_path": True,
        "no_old_invalid_evidence_dependency": True,
        "no_mechanism_score_or_readiness_claim_before_admission": True,
    }
    manifest["scope"].update(
        {
            "surface_admission_authorization_only": True,
            "later_task_card_only": True,
            "execution_scope_opened": False,
            "creates_candidate_behavior": False,
            "opens_gate5": False,
            "opens_bridge": False,
            "opens_runtime": False,
            "opens_tournament": False,
            "opens_ego_mainline": False,
            "produces_mechanism_score": False,
        }
    )
    manifest["execution_scope_opened"] = False
    manifest["later_task_card_only"] = True
    manifest["candidate_scope_opened"] = False
    manifest["gate5_scope_opened"] = False
    manifest["bridge_scope_opened"] = False
    manifest["runtime_scope_opened"] = False
    manifest["tournament_scope_opened"] = False
    manifest["ego_mainline_scope_opened"] = False
    manifest["manifest_instantiation_before_execution"] = True
    manifest["authorization_validator_invocation_before_execution"] = True
    manifest["validator_readback_before_execution"] = True
    manifest["test_evidence"]["claims_full_suite_pass"] = False
    manifest["test_evidence"]["full_pytest_status"] = "not_claimed_by_001b_manifest"
    manifest["outputs_requested"] = [
        "authorization_decision",
        "validator_readback.json",
        "trace.json",
        "claim_ceiling.txt",
    ]
    manifest["claims"] = [CLAIM_CEILING]
    manifest["evidence_citations"] = [
        {
            "artifact_id": HARDENING_TASK_ID,
            "claim": "pre-execution hardening dependency only",
        },
        {
            "artifact_id": ENFORCEMENT_TASK_ID,
            "claim": "pre-execution authorization checker dependency only",
        },
        {
            "artifact_id": TEMPLATE_TASK_ID,
            "claim": "pre-execution authorization manifest template dependency only",
        },
        {
            "artifact_id": GAP_REPAIR_TASK_ID,
            "claim": "sealed validator gap-repair dependency only",
        },
        {
            "artifact_id": "COMPOSITE-CROSS-TASK-STATE-REUSE",
            "claim": "negative_or_invalid_harness_evidence_only",
        },
        {
            "artifact_id": "CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A",
            "claim": "negative_or_invalid_harness_evidence_only",
        },
        {
            "artifact_id": "ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A",
            "claim": "negative_or_invalid_harness_evidence_only",
        },
    ]
    manifest["dependencies"] = [
        _dependency_manifest(HARDENING_TASK_ID, dependency_readback),
        _dependency_manifest(ENFORCEMENT_TASK_ID, dependency_readback),
        _dependency_manifest(TEMPLATE_TASK_ID, dependency_readback),
        _dependency_manifest(GAP_REPAIR_TASK_ID, dependency_readback),
    ]
    manifest["source_template"] = {
        "task_id": TEMPLATE_TASK_ID,
        "path": DEPENDENCY_SPECS[TEMPLATE_TASK_ID]["template_path"],
        "commit": dependency_readback["dependencies"][TEMPLATE_TASK_ID]["local_tag_commit"],
        "tag": DEPENDENCY_SPECS[TEMPLATE_TASK_ID]["tag"],
    }
    manifest["authorization_validator"] = {
        "checker_module": "future_surface_admission_authorization_template_001a.validator",
        "checker_function": "validate_authorization_manifest",
        "invocation_required": True,
        "invocation_recorded": True,
        "readback_required": True,
        "readback_path": _canonical_artifact_rel(output_dir, "validator_readback.json", repo_root),
        "trace_path": _canonical_artifact_rel(output_dir, "trace.jsonl", repo_root),
        "code_path_hash": validator._source_hash(),
        "manifest_hash": "",
    }
    validator._refresh_manifest_hash(manifest)
    return manifest


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

    def add(ablation_id: str, mutated: dict[str, Any], refresh_hash: bool = True) -> None:
        ablations.append(
            _decision_row(
                "ablation_id",
                ablation_id,
                _invoke_manifest(validator, mutated, template, enforcement, refresh_hash),
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
    no_direction["proposed_surface_admission_direction_status"] = "missing_concrete_surface_direction"
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


def _build_trace_events(
    run_id: str,
    output_dir: Path,
    repo_root: Path,
    manifest_hash: str,
    validator_code_path_hash: str,
    decision: dict[str, Any],
    negative_controls: dict[str, Any],
    ablations: dict[str, Any],
    stop_conditions: list[str],
) -> list[dict[str, Any]]:
    events = [
        {
            "event": "manifest_instantiated",
            "producer_function": "build_next_surface_admission_manifest_001b",
            "run_id": run_id,
            "manifest_path": _rel(output_dir / "manifest.json", repo_root),
            "manifest_hash": manifest_hash,
            "claim_ceiling": CLAIM_CEILING,
        },
        {
            "event": "validator_invoked",
            "producer_function": "validate_authorization_manifest",
            "run_id": run_id,
            "manifest_hash": manifest_hash,
            "validator_code_path_hash": validator_code_path_hash,
            "authorization_decision": decision["authorization_decision"],
            "reasons_fired": decision["reasons_fired"],
            "claim_ceiling": CLAIM_CEILING,
        },
    ]
    for control in negative_controls["controls"]:
        events.append(
            {
                "event": "negative_control_invoked",
                "run_id": run_id,
                **control,
                "claim_ceiling": CLAIM_CEILING,
            }
        )
    for ablation in ablations["ablations"]:
        events.append(
            {
                "event": "ablation_invoked",
                "run_id": run_id,
                **ablation,
                "claim_ceiling": CLAIM_CEILING,
            }
        )
    for stop_condition in stop_conditions:
        events.append(
            {
                "event": "stop_condition_triggered",
                "run_id": run_id,
                "stop_condition": stop_condition,
                "claim_ceiling": CLAIM_CEILING,
            }
        )
    return events


def _write_report(repo_root: Path, result: dict[str, Any]) -> None:
    path = _doc_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = f"""# {TASK_ID}

## Validator gap blocker

Verdict: `{result["verdict"]}`.

Layer: {LAYER}.

Mainline integration: {MAINLINE_INTEGRATION}.

Enabled status: {ENABLED_STATUS}.

Real trigger evidence: `validate_authorization_manifest` was invoked on
`artifacts/{TASK_SLUG}/manifest.json`; manifest hash
`{result["manifest_hash"]}`; validator code path hash
`{result["validator_code_path_hash"]}`.

The concrete manifest itself was authorized, but the ablation
`remove_validator_gap_repair_dependency` was also authorized by the sealed
validator. Because this task requires dependency on
`{GAP_REPAIR_TASK_ID}` and forbids validator repair in this task, this is a
blocker. A later concrete surface-admission task card may not be drafted from
this result.

## Decision

The later concrete surface-admission task card may not be drafted.

## Claim ceiling

{CLAIM_CEILING}.

## Stop condition

- `validator_returned_unexpected_authorization_for_validator_gap_repair_dependency_ablation`

## Artifact readback

- Manifest: `artifacts/{TASK_SLUG}/manifest.json`
- Validator readback: `artifacts/{TASK_SLUG}/validator_readback.json`
- Negative controls: `artifacts/{TASK_SLUG}/negative_controls.json`
- Ablations: `artifacts/{TASK_SLUG}/ablation_results.json`
- Trace: `artifacts/{TASK_SLUG}/trace.json`
- Claim ceiling: `artifacts/{TASK_SLUG}/claim_ceiling.txt`

## What this does not prove

This does not prove mechanism validity, Gate validity, candidate behavior,
agency, autonomy, consciousness, emotion, subjectivity, EGO readiness, runtime
readiness, companion readiness, stable user benefit, or mainline effect.
"""
    path.write_text(text, encoding="utf-8")


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
    dependency_readback = _dependency_readback(root)
    enforcement = validator.validate_enforcement_artifacts(root)
    template = validator.build_authorization_manifest_template(root)
    manifest = _build_manifest(root, out, validator, template, dependency_readback)

    _write_json(out / "manifest.json", manifest)
    manifest_hash = validator._manifest_integrity_hash(manifest)
    validator_code_path_hash = validator._source_hash()
    validator_decision = validator.validate_authorization_manifest(
        manifest,
        template,
        enforcement,
    )
    negative_controls = _negative_controls(validator, manifest, template, enforcement)
    ablations = _ablations(validator, manifest, template, enforcement)
    unexpected_ablations = [
        ablation["ablation_id"]
        for ablation in ablations["ablations"]
        if ablation["unexpected_authorization"]
    ]
    stop_conditions: list[str] = []
    if validator_decision["authorization_decision"] != "authorized":
        stop_conditions.append("validator_did_not_authorize_concrete_non_forbidden_manifest")
    if not negative_controls["all_controls_blocked"]:
        stop_conditions.append("validator_returned_unexpected_authorization_for_invalid_control")
    if "remove_validator_gap_repair_dependency" in unexpected_ablations:
        stop_conditions.append(
            "validator_returned_unexpected_authorization_for_validator_gap_repair_dependency_ablation"
        )
    for ablation_id in unexpected_ablations:
        if ablation_id != "remove_validator_gap_repair_dependency":
            stop_conditions.append(f"validator_returned_unexpected_authorization_for_{ablation_id}")

    verdict = BLOCKED_VERDICT if stop_conditions else AUTHORIZED_VERDICT
    task_decision = DECISION_BLOCKED if stop_conditions else DECISION_AUTHORIZED
    trace_events = _build_trace_events(
        run_id,
        out,
        root,
        manifest_hash,
        validator_code_path_hash,
        validator_decision,
        negative_controls,
        ablations,
        stop_conditions,
    )
    trace = {
        "task_id": TASK_ID,
        "producer_function": "build_manifest_instantiation_trace_001b",
        "run_id": run_id,
        "events": trace_events,
        "jsonl_trace_path": _rel(out / "trace.jsonl", root),
        "claim_ceiling": CLAIM_CEILING,
    }
    validator_readback = {
        "task_id": TASK_ID,
        "producer_function": "validate_authorization_manifest",
        "run_id": run_id,
        "serialized_manifest_path": _rel(out / "manifest.json", root),
        "manifest_hash": manifest_hash,
        "validator_code_path_hash": validator_code_path_hash,
        "validator_decision": validator_decision,
        "dependency_readback": dependency_readback,
        "scope_readback": {
            "later_task_card_only": manifest["scope"]["later_task_card_only"],
            "execution_scope_opened": manifest["scope"]["execution_scope_opened"],
            "creates_candidate_behavior": manifest["scope"]["creates_candidate_behavior"],
            "opens_gate5": manifest["scope"]["opens_gate5"],
            "opens_bridge": manifest["scope"]["opens_bridge"],
            "opens_runtime": manifest["scope"]["opens_runtime"],
            "opens_tournament": manifest["scope"]["opens_tournament"],
            "opens_ego_mainline": manifest["scope"]["opens_ego_mainline"],
            "produces_mechanism_score": manifest["scope"]["produces_mechanism_score"],
        },
        "recomputation_chain": [
            "serialized_manifest",
            "validate_authorization_manifest",
            "validator_code_path_hash",
            "run_id",
            "validator verdict and reasons",
        ],
        "claim_ceiling": CLAIM_CEILING,
    }
    result = {
        "task_id": TASK_ID,
        "verdict": verdict,
        "decision": task_decision,
        "current_layer": LAYER,
        "layer": LAYER,
        "mainline_integration": False,
        "mainline_integration_status": MAINLINE_INTEGRATION,
        "enabled_status": ENABLED_STATUS,
        "real_trigger_evidence": (
            "validate_authorization_manifest invoked on concrete manifest; "
            "negative controls and ablations preserved"
        ),
        "producer_function": "validate_authorization_manifest",
        "run_id": run_id,
        "manifest_hash": manifest_hash,
        "manifest_file_hash": _hash_file(out / "manifest.json"),
        "validator_code_path_hash": validator_code_path_hash,
        "input_manifest_path": _rel(out / "manifest.json", root),
        "validator_result_path": _rel(out / "validator_readback.json", root),
        "trace_path": _rel(out / "trace.json", root),
        "claim_ceiling": CLAIM_CEILING,
        "mechanism_execution": False,
        "candidate_scope_opened": False,
        "gate5_scope_opened": False,
        "bridge_scope_opened": False,
        "runtime_scope_opened": False,
        "tournament_scope_opened": False,
        "ego_mainline_scope_opened": False,
        "validator_authorization_decision": validator_decision["authorization_decision"],
        "validator_reasons_fired": validator_decision["reasons_fired"],
        "negative_controls_all_blocked": negative_controls["all_controls_blocked"],
        "ablation_controls_all_blocked": ablations["all_required_ablations_blocked"],
        "unexpected_authorized_ablations": unexpected_ablations,
        "stop_conditions_triggered": stop_conditions,
        "dependency_readback": dependency_readback,
        "auto_remote_anchor": {
            "decision": "conditional_not_completed" if stop_conditions else "conditional_pending_commit_gate",
            "permitted": not stop_conditions,
            "reason": (
                "stop condition triggered by validator-gap-repair dependency ablation"
                if stop_conditions
                else "requires post-commit clean status and exact remote readback"
            ),
            "claim_ceiling_if_performed": "remote-anchor publication and verification only",
        },
        "next_minimal_closed_loop_action": (
            "Create a separately authorized validator-gap repair task card if the "
            "gap-repair dependency must become a hard validator requirement."
        ),
        "what_this_does_not_prove": WHAT_THIS_DOES_NOT_PROVE,
    }

    _write_json(out / "validator_readback.json", validator_readback)
    _write_json(out / "negative_controls.json", negative_controls)
    _write_json(out / "ablation_results.json", ablations)
    _write_json(out / "trace.json", trace)
    _write_trace_jsonl(out / "trace.jsonl", trace_events)
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
