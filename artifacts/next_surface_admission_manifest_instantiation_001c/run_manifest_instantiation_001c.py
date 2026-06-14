from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001C"
TASK_SLUG = "next_surface_admission_manifest_instantiation_001c"
CLAIM_CEILING = "surface-admission authorization hygiene only"
LAYER = "engineering-governance / authorization manifest instantiation only"
MAINLINE_INTEGRATION = "none"
ENABLED_STATUS = "local offline validator invocation only"
PROPOSED_DIRECTION = (
    "Minimal non-candidate surface-admission preflight for a future "
    "mechanism-family direction"
)

HARDENING_TASK_ID = "SURFACE-ADMISSION-CONTRACT-HARDENING-001A"
ENFORCEMENT_TASK_ID = "SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A"
TEMPLATE_TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-TEMPLATE-001A"
GAP_REPAIR_001A_TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001A"
PARENT_BLOCKER_TASK = "NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001B"
PARENT_REPAIR_TASK = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001B"
PARENT_REPAIR_COMMIT = "5a5442d318620f97ee3029a2a6898cffbf465f2d"
PARENT_REPAIR_TAG = (
    "remote-anchor-future-surface-admission-authorization-validator-gap-repair-001b-5a5442d"
)
ORIGINAL_001B_MANIFEST_HASH = (
    "860c4b6203338cbda9684a1a712f668dc46ffb274e12381082050e2c21185175"
)
BEFORE_VALIDATOR_CODE_PATH_HASH = (
    "a6cd3ca24459e212ce8fd80a37978fa9b99214cf5740899ea0c42122dff25e6b"
)
EXPECTED_REPAIRED_VALIDATOR_CODE_PATH_HASH = (
    "67f7c2e08a9ec95176bbaf9c98c2c88a8e1a13e06355cff3211dd7ffb1cebb01"
)

AUTHORIZED_DECISION = "later_surface_admission_task_card_may_be_drafted"
BLOCKED_DECISION = "later_surface_admission_task_card_may_not_be_drafted"
AUTHORIZED_VERDICT = "authorized_later_surface_admission_task_card_drafting_only"
BLOCKED_VERDICT = "blocked_validator_gap_repair_001b_dependency_not_enforced"

INVALID_EVIDENCE_SURFACES = [
    "COMPOSITE-CTSR pass-chain",
    "CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A",
    "ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A",
]
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
    GAP_REPAIR_001A_TASK_ID: {
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
        "required_verdict": "future_surface_admission_authorization_validator_gap_repair_001a_pass",
        "dependency_type": "sealed_validator_gap_repair_boundary",
        "tag": "remote-anchor-future-surface-admission-authorization-validator-gap-repair-001a-b4d7c08",
    },
    PARENT_BLOCKER_TASK: {
        "artifact_id": "next_surface_admission_manifest_instantiation_001b",
        "result_path": "artifacts/next_surface_admission_manifest_instantiation_001b/result.json",
        "readback_path": (
            "artifacts/next_surface_admission_manifest_instantiation_001b/"
            "validator_readback.json"
        ),
        "trace_path": "artifacts/next_surface_admission_manifest_instantiation_001b/trace.json",
        "manifest_path": "artifacts/next_surface_admission_manifest_instantiation_001b/manifest.json",
        "required_verdict": "blocked_validator_gap_repair_dependency_ablation_authorized",
        "dependency_type": "observed_validator_gap_blocker_source",
        "tag": None,
    },
    PARENT_REPAIR_TASK: {
        "artifact_id": "future_surface_admission_authorization_validator_gap_repair_001b",
        "result_path": (
            "artifacts/future_surface_admission_authorization_validator_gap_repair_001b/"
            "result.json"
        ),
        "readback_path": (
            "artifacts/future_surface_admission_authorization_validator_gap_repair_001b/"
            "readback.json"
        ),
        "trace_path": (
            "artifacts/future_surface_admission_authorization_validator_gap_repair_001b/"
            "trace.json"
        ),
        "required_verdict": "future_surface_admission_authorization_validator_gap_repair_001b_pass",
        "dependency_type": "sealed_validator_gap_repair_boundary",
        "tag": PARENT_REPAIR_TAG,
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


def _artifact_rel(output_dir: Path, filename: str, repo_root: Path) -> str:
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


def _remote_tag_hash(repo_root: Path, tag: str) -> str | None:
    result = _run_git(repo_root, ["ls-remote", "--tags", "origin", f"refs/tags/{tag}"])
    if result["returncode"] != 0 or not result["stdout"]:
        return None
    return result["stdout"].split()[0]


def _artifact_verdict(repo_root: Path, spec: dict[str, Any]) -> str | None:
    result_path = repo_root / spec["result_path"]
    if not result_path.exists():
        return None
    payload = _load_json(result_path)
    return (
        payload.get("verdict")
        or payload.get("authorization_validator_decision")
        or payload.get("decision")
    )


def _canonical_state_readback(repo_root: Path) -> dict[str, Any]:
    local_head = _git_stdout(repo_root, ["rev-parse", "HEAD"])
    remote_branch_hash = _git_stdout(
        repo_root,
        ["rev-parse", "--verify", "origin/codex/meta-theory-scaffold"],
    )
    local_tag_hash = _git_stdout(repo_root, ["rev-parse", f"{PARENT_REPAIR_TAG}^{{commit}}"])
    remote_tag_hash = _remote_tag_hash(repo_root, PARENT_REPAIR_TAG)
    return {
        "producer_function": "canonical_state_readback",
        "branch": _git_stdout(repo_root, ["branch", "--show-current"]),
        "head": local_head,
        "status_short": _git_stdout(repo_root, ["status", "--short", "--branch"]),
        "ahead_behind": _git_stdout(
            repo_root,
            ["rev-list", "--left-right", "--count", "HEAD...@{upstream}"],
        ),
        "parent_repair_commit": PARENT_REPAIR_COMMIT,
        "parent_repair_commit_type": _git_stdout(repo_root, ["cat-file", "-t", PARENT_REPAIR_COMMIT]),
        "parent_repair_tag": PARENT_REPAIR_TAG,
        "parent_repair_local_tag_hash": local_tag_hash,
        "parent_repair_remote_tag_hash": remote_tag_hash,
        "parent_repair_remote_branch_hash": remote_branch_hash,
        "parent_repair_exact_match": (
            local_head == PARENT_REPAIR_COMMIT
            and remote_branch_hash == PARENT_REPAIR_COMMIT
            and local_tag_hash == PARENT_REPAIR_COMMIT
            and remote_tag_hash == PARENT_REPAIR_COMMIT
        ),
        "repaired_validator_path_exists": (
            repo_root / "src" / "future_surface_admission_authorization_template_001a" / "validator.py"
        ).exists(),
        "blocker_001b_artifacts_exist": (
            repo_root / "artifacts" / "next_surface_admission_manifest_instantiation_001b"
        ).exists(),
        "repair_001b_artifacts_exist": (
            repo_root / "artifacts" / "future_surface_admission_authorization_validator_gap_repair_001b"
        ).exists(),
    }


def _dependency_readback(repo_root: Path, canonical_state: dict[str, Any]) -> dict[str, Any]:
    dependencies: dict[str, Any] = {}
    for task_id, spec in DEPENDENCY_SPECS.items():
        result_path = repo_root / spec["result_path"]
        readback_path = repo_root / spec["readback_path"]
        tag = spec.get("tag")
        dependencies[task_id] = {
            "task_id": task_id,
            "artifact_id": spec["artifact_id"],
            "dependency_type": spec["dependency_type"],
            "required": True,
            "required_verdict": spec["required_verdict"],
            "observed_verdict": _artifact_verdict(repo_root, spec),
            "tag": tag,
            "local_tag_commit": (
                _git_stdout(repo_root, ["rev-parse", f"{tag}^{{commit}}"]) if tag else None
            ),
            "remote_tag_commit": _remote_tag_hash(repo_root, tag) if tag else None,
            "result_path": spec["result_path"],
            "result_sha256": _hash_file(result_path),
            "readback_path": spec["readback_path"],
            "readback_sha256": _hash_file(readback_path),
        }
        for optional in ["template_path", "trace_path", "manifest_path"]:
            if optional in spec:
                optional_path = repo_root / spec[optional]
                dependencies[task_id][optional] = spec[optional]
                dependencies[task_id][f"{optional}_sha256"] = _hash_file(optional_path)
    return {
        "producer_function": "dependency_readback",
        "repo": canonical_state,
        "dependencies": dependencies,
    }


def _dependency_manifest(task_id: str, readback: dict[str, Any]) -> dict[str, Any]:
    dependency = readback["dependencies"][task_id]
    payload = {
        "task_id": task_id,
        "artifact_id": dependency["artifact_id"],
        "required_verdict": dependency["required_verdict"],
        "observed_verdict": dependency["observed_verdict"],
        "dependency_type": dependency["dependency_type"],
        "required": True,
        "tag": dependency["tag"],
        "commit": dependency["local_tag_commit"],
        "remote_tag_commit": dependency["remote_tag_commit"],
        "result_path": dependency["result_path"],
        "readback_path": dependency["readback_path"],
        "result_sha256": dependency["result_sha256"],
        "readback_sha256": dependency["readback_sha256"],
    }
    for optional in [
        "template_path",
        "template_path_sha256",
        "trace_path",
        "trace_path_sha256",
        "manifest_path",
        "manifest_path_sha256",
    ]:
        if optional in dependency:
            payload[optional] = dependency[optional]
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
    manifest["parent_blocker_task"] = PARENT_BLOCKER_TASK
    manifest["parent_repair_task"] = PARENT_REPAIR_TASK
    manifest["parent_repair_commit"] = PARENT_REPAIR_COMMIT
    manifest["parent_repair_tag"] = PARENT_REPAIR_TAG
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
    manifest["test_evidence"]["full_pytest_status"] = "not_claimed_by_001c_manifest"
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
            "artifact_id": GAP_REPAIR_001A_TASK_ID,
            "claim": "sealed validator gap-repair dependency only",
        },
        {
            "artifact_id": PARENT_BLOCKER_TASK,
            "claim": "observed validator-gap blocker source only",
        },
        {
            "artifact_id": PARENT_REPAIR_TASK,
            "claim": "sealed validator-gap repair boundary only",
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
        _dependency_manifest(GAP_REPAIR_001A_TASK_ID, dependency_readback),
        _dependency_manifest(PARENT_BLOCKER_TASK, dependency_readback),
        _dependency_manifest(PARENT_REPAIR_TASK, dependency_readback),
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
        "readback_path": _artifact_rel(output_dir, "validator_readback.json", repo_root),
        "trace_path": _artifact_rel(output_dir, "trace.jsonl", repo_root),
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
            "manifest_proposing_gate5",
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
            "manifest_proposing_bridge_runtime_tournament_ego_mainline",
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
        (GAP_REPAIR_001A_TASK_ID, "remove_validator_gap_repair_001a_dependency"),
        (PARENT_REPAIR_TASK, "remove_validator_gap_repair_001b_dependency"),
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
    add("open_no_candidate_gate5_bridge_runtime_tournament_ego_mainline_scope", forbidden_scope)

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

    alias = copy.deepcopy(manifest)
    for dependency in alias["dependencies"]:
        if dependency.get("task_id") == PARENT_REPAIR_TASK:
            dependency["task_id"] = f"{PARENT_REPAIR_TASK}-ALIAS"
    add("validator_gap_repair_001b_dependency_alias", alias)

    free_text = copy.deepcopy(manifest)
    free_text["dependencies"] = [
        dependency
        for dependency in free_text["dependencies"]
        if dependency.get("task_id") != PARENT_REPAIR_TASK
    ]
    free_text["notes"] = (
        "Narrative-only mention of "
        "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001B."
    )
    add("validator_gap_repair_001b_dependency_free_text_only", free_text)

    metadata_only = copy.deepcopy(manifest)
    metadata_only["dependencies"] = [
        dependency
        for dependency in metadata_only["dependencies"]
        if dependency.get("task_id") != PARENT_REPAIR_TASK
    ]
    metadata_only["non_enforced_metadata"] = {
        "task_id": PARENT_REPAIR_TASK,
        "required": False,
        "claim": "metadata-only reference",
    }
    add("validator_gap_repair_001b_dependency_non_enforced_metadata_only", metadata_only)

    replaced = copy.deepcopy(manifest)
    replaced["dependencies"] = [
        dependency
        for dependency in replaced["dependencies"]
        if dependency.get("task_id") != PARENT_REPAIR_TASK
    ]
    add("validator_gap_repair_001b_replaced_with_001a_only", replaced)

    unexpected = [control for control in controls if control["unexpected_authorization"]]
    return {
        "task_id": TASK_ID,
        "producer_function": (
            "run_dependency_structure_controls_through_validate_authorization_manifest"
        ),
        "controls": controls,
        "blocked_control_count": sum(1 for control in controls if control["blocked"]),
        "all_controls_blocked": all(control["blocked"] for control in controls),
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
    dependency_controls: dict[str, Any],
    stop_conditions: list[str],
) -> list[dict[str, Any]]:
    events = [
        {
            "event": "manifest_instantiated",
            "producer_function": "build_next_surface_admission_manifest_001c",
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
    for control in dependency_controls["controls"]:
        events.append(
            {
                "event": "dependency_structure_control_invoked",
                "run_id": run_id,
                **control,
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
`{result["actual_validator_code_path_hash"]}`.

The concrete 001C manifest includes dependency on
`{PARENT_REPAIR_TASK}` and was authorized by the repaired local validator.
However, callable ablation and dependency-structure controls that remove,
alias, or demote the same 001B repair dependency were also authorized. Because
this task forbids validator repair and does not permit mechanism execution,
this is preserved as a blocker. A later concrete surface-admission task card
may not be drafted from this result.

## Parent references

- Parent blocker: `{PARENT_BLOCKER_TASK}`
- Parent repair: `{PARENT_REPAIR_TASK}`
- Parent repair commit: `{PARENT_REPAIR_COMMIT}`
- Parent repair tag: `{PARENT_REPAIR_TAG}`

## Control readback

- Negative controls blocked: `{result["negative_controls_blocked_count"]}/6`
- Ablations blocked: `{result["ablation_controls_blocked_count"]}/10`
- Dependency-structure controls blocked:
  `{result["dependency_structure_controls_blocked_count"]}/4`

## Decision

The later concrete surface-admission task card may not be drafted.

## Claim ceiling

{CLAIM_CEILING}.

## Stop conditions

{chr(10).join(f"- `{item}`" for item in result["stop_conditions_triggered"])}

## Artifact readback

- Manifest: `artifacts/{TASK_SLUG}/manifest.json`
- Validator readback: `artifacts/{TASK_SLUG}/validator_readback.json`
- Negative controls: `artifacts/{TASK_SLUG}/negative_controls.json`
- Ablations: `artifacts/{TASK_SLUG}/ablation_results.json`
- Dependency-structure controls:
  `artifacts/{TASK_SLUG}/dependency_structure_controls.json`
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

    canonical_state = _canonical_state_readback(root)
    dependency_readback = _dependency_readback(root, canonical_state)
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
    dependency_controls = _dependency_structure_controls(
        validator,
        manifest,
        template,
        enforcement,
    )

    unexpected_ablations = [
        ablation["ablation_id"]
        for ablation in ablations["ablations"]
        if ablation["unexpected_authorization"]
    ]
    unexpected_dependency_controls = [
        control["control_id"]
        for control in dependency_controls["controls"]
        if control["unexpected_authorization"]
    ]
    stop_conditions: list[str] = []
    if validator_decision["authorization_decision"] != "authorized":
        stop_conditions.append("validator_did_not_authorize_concrete_non_forbidden_manifest")
    if not negative_controls["all_controls_blocked"]:
        stop_conditions.append("validator_returned_unexpected_authorization_for_invalid_control")
    if "remove_validator_gap_repair_001b_dependency" in unexpected_ablations:
        stop_conditions.append(
            "validator_returned_unexpected_authorization_for_validator_gap_repair_001b_dependency_ablation"
        )
    for ablation_id in unexpected_ablations:
        if ablation_id != "remove_validator_gap_repair_001b_dependency":
            stop_conditions.append(f"validator_returned_unexpected_authorization_for_{ablation_id}")
    if unexpected_dependency_controls:
        stop_conditions.append(
            "validator_returned_unexpected_authorization_for_validator_gap_repair_001b_dependency_structure_controls"
        )

    verdict = BLOCKED_VERDICT if stop_conditions else AUTHORIZED_VERDICT
    task_decision = BLOCKED_DECISION if stop_conditions else AUTHORIZED_DECISION
    trace_events = _build_trace_events(
        run_id,
        out,
        root,
        manifest_hash,
        validator_code_path_hash,
        validator_decision,
        negative_controls,
        ablations,
        dependency_controls,
        stop_conditions,
    )
    trace = {
        "task_id": TASK_ID,
        "producer_function": "build_manifest_instantiation_trace_001c",
        "run_id": run_id,
        "events": trace_events,
        "claim_ceiling": CLAIM_CEILING,
    }
    validator_readback = {
        "task_id": TASK_ID,
        "producer_function": "validate_authorization_manifest",
        "run_id": run_id,
        "serialized_manifest_path": _rel(out / "manifest.json", root),
        "manifest_hash": manifest_hash,
        "actual_validator_code_path_hash": validator_code_path_hash,
        "expected_repaired_validator_code_path_hash": EXPECTED_REPAIRED_VALIDATOR_CODE_PATH_HASH,
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
        "negative_controls_path": _rel(out / "negative_controls.json", root),
        "ablation_results_path": _rel(out / "ablation_results.json", root),
        "dependency_structure_controls_path": _rel(
            out / "dependency_structure_controls.json",
            root,
        ),
        "recomputation_chain": [
            "serialized_manifest",
            "validate_authorization_manifest",
            "actual_validator_code_path_hash",
            "run_id",
            "validator verdict and reasons",
            "dependency readback",
            "scope readback",
            "control and ablation results",
        ],
        "claim_ceiling": CLAIM_CEILING,
    }
    result = {
        "task_id": TASK_ID,
        "verdict": verdict,
        "producer_function": "validate_authorization_manifest",
        "parent_blocker_task": PARENT_BLOCKER_TASK,
        "parent_repair_task": PARENT_REPAIR_TASK,
        "parent_repair_commit": PARENT_REPAIR_COMMIT,
        "parent_repair_tag": PARENT_REPAIR_TAG,
        "original_001b_manifest_hash": ORIGINAL_001B_MANIFEST_HASH,
        "before_validator_code_path_hash": BEFORE_VALIDATOR_CODE_PATH_HASH,
        "expected_repaired_validator_code_path_hash": EXPECTED_REPAIRED_VALIDATOR_CODE_PATH_HASH,
        "actual_validator_code_path_hash": validator_code_path_hash,
        "run_id": run_id,
        "input_manifest_path": _rel(out / "manifest.json", root),
        "manifest_hash": manifest_hash,
        "manifest_file_hash": _hash_file(out / "manifest.json"),
        "validator_result_path": _rel(out / "validator_readback.json", root),
        "trace_path": _rel(out / "trace.json", root),
        "trace_jsonl_path": _rel(out / "trace.jsonl", root),
        "negative_controls_path": _rel(out / "negative_controls.json", root),
        "ablation_results_path": _rel(out / "ablation_results.json", root),
        "dependency_structure_controls_path": _rel(
            out / "dependency_structure_controls.json",
            root,
        ),
        "decision": task_decision,
        "current_layer": LAYER,
        "layer": LAYER,
        "mainline_integration": False,
        "mainline_integration_status": MAINLINE_INTEGRATION,
        "enabled_status": ENABLED_STATUS,
        "real_trigger_evidence": (
            "validate_authorization_manifest invoked on concrete 001C manifest; "
            "negative controls, ablations, and dependency-structure controls preserved"
        ),
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
        "negative_controls_blocked_count": negative_controls["blocked_control_count"],
        "ablation_controls_all_blocked": ablations["all_required_ablations_blocked"],
        "ablation_controls_blocked_count": ablations["blocked_ablation_count"],
        "dependency_structure_controls_all_blocked": dependency_controls["all_controls_blocked"],
        "dependency_structure_controls_blocked_count": dependency_controls[
            "blocked_control_count"
        ],
        "unexpected_authorized_ablations": unexpected_ablations,
        "unexpected_authorized_dependency_structure_controls": unexpected_dependency_controls,
        "stop_conditions_triggered": stop_conditions,
        "dependency_readback": dependency_readback,
        "auto_remote_anchor": {
            "decision": "conditional_not_completed" if stop_conditions else "conditional_pending_commit_gate",
            "permitted": not stop_conditions,
            "reason": (
                "stop condition triggered by validator-gap-repair-001b dependency controls"
                if stop_conditions
                else "requires post-commit clean status and exact remote readback"
            ),
            "claim_ceiling_if_performed": "remote-anchor publication and verification only",
        },
        "next_minimal_closed_loop_action": (
            "Draft a separately authorized validator-gap repair task card if 001C "
            "must require FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001B "
            "as an enforced structural dependency."
        ),
        "what_this_does_not_prove": WHAT_THIS_DOES_NOT_PROVE,
    }

    _write_json(out / "validator_readback.json", validator_readback)
    _write_json(out / "negative_controls.json", negative_controls)
    _write_json(out / "ablation_results.json", ablations)
    _write_json(out / "dependency_structure_controls.json", dependency_controls)
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
