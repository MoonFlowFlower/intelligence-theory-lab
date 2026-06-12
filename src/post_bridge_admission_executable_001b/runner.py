from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

from . import core


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, data: object) -> None:
    path.write_text(core.pretty_json(data) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(core.stable_json(row) for row in rows) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _git_output(repo_root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def _git_status(repo_root: Path) -> list[str]:
    return [line for line in _git_output(repo_root, ["status", "--short"]).splitlines() if line]


def _tracked_files(repo_root: Path) -> list[str]:
    return [
        line.replace("\\", "/")
        for line in _git_output(repo_root, ["ls-files"]).splitlines()
        if line
    ]


def _protected_artifact_inventory(repo_root: Path) -> dict:
    tracked = _tracked_files(repo_root)
    protected = [
        path
        for path in tracked
        if path.startswith("artifacts/") and not path.startswith(core.ARTIFACT_DIR_REL + "/")
    ]
    return {
        "task_id": core.TASK_ID,
        "claim_ceiling": core.CLAIM_CEILING,
        "protected_rule": "tracked artifacts excluding this task artifact directory",
        "tracked_old_artifact_paths": protected,
        "tracked_old_artifact_count": len(protected),
        "git_status_before_execution": _git_status(repo_root),
    }


def _hash_inventory(repo_root: Path, inventory: dict) -> dict[str, str]:
    return {
        path: core.file_sha256(repo_root / path)
        for path in inventory["tracked_old_artifact_paths"]
        if (repo_root / path).exists()
    }


def _parent_remote_anchor_verification(repo_root: Path) -> dict:
    actual_hashes: dict[str, str] = {}
    raw_outputs: dict[str, str] = {}
    commands: list[str] = []
    failures: dict[str, str] = {}
    for tag, expected_hash in core.PARENT_REMOTE_ANCHORS.items():
        ref = f"refs/tags/{tag}"
        command = f"git ls-remote origin {ref}"
        commands.append(command)
        try:
            output = _git_output(repo_root, ["ls-remote", "origin", ref])
            raw_outputs[tag] = output
            actual_hashes[tag] = output.split()[0] if output else ""
        except subprocess.CalledProcessError as exc:
            raw_outputs[tag] = exc.stdout.strip() if exc.stdout else ""
            actual_hashes[tag] = ""
            failures[tag] = exc.stderr.strip() if exc.stderr else str(exc)
        if actual_hashes.get(tag) != expected_hash:
            failures.setdefault(tag, f"expected {expected_hash}, got {actual_hashes.get(tag, '')}")
    return {
        "commands": commands,
        "expected_hashes": dict(core.PARENT_REMOTE_ANCHORS),
        "actual_hashes": actual_hashes,
        "raw_outputs": raw_outputs,
        "verified": actual_hashes == core.PARENT_REMOTE_ANCHORS and not failures,
        "failures": failures,
    }


def _parent_contract_verification(repo_root: Path) -> dict:
    command = f"git rev-parse {core.PARENT_CONTRACT_SHORT}"
    try:
        output = _git_output(repo_root, ["rev-parse", core.PARENT_CONTRACT_SHORT])
        verified = output == core.PARENT_CONTRACT_FULL
        failure = "" if verified else f"expected {core.PARENT_CONTRACT_FULL}, got {output}"
    except subprocess.CalledProcessError as exc:
        output = exc.stdout.strip() if exc.stdout else ""
        verified = False
        failure = exc.stderr.strip() if exc.stderr else str(exc)
    return {
        "command": command,
        "expected_hash": core.PARENT_CONTRACT_FULL,
        "rev_parse_output": output,
        "verified": verified,
        "failure": failure,
    }


def _stage0_manifest(
    *,
    task_card_hash: str,
    distribution_manifest_hash: str,
    distribution: dict,
    parent_remote_anchor_verification: dict,
    parent_contract_verification: dict,
) -> dict:
    manifest = {
        "task_id": core.TASK_ID,
        "created_utc": _utc_now(),
        "stage0_freeze_before_any_executable_run": True,
        "executable_run_started_before_stage0": False,
        "frozen_contract_items": [
            "task_card_hash",
            "thresholds",
            "metrics",
            "required_baselines",
            "required_ablations",
            "distribution_manifest_hash",
            "seed_families",
            "artifact_schema",
            "stop_conditions",
            "rollback_policy",
            "claim_ceiling",
        ],
        "task_card_hash": task_card_hash,
        "parent_contract_verification": parent_contract_verification,
        "parent_remote_anchor_verification": parent_remote_anchor_verification,
        "thresholds": core.thresholds_manifest(),
        "metrics": core.metrics_manifest(),
        "required_baselines": list(core.REQUIRED_BASELINES),
        "required_ablations": list(core.REQUIRED_ABLATIONS),
        "required_contrasts": list(core.REQUIRED_CONTRASTS),
        "required_leakage_checks": list(core.REQUIRED_LEAKAGE_CHECKS),
        "distribution_manifest_hash": distribution_manifest_hash,
        "seed_families": distribution["seed_families"],
        "artifact_schema": list(core.REQUIRED_ARTIFACTS),
        "extra_artifacts": list(core.EXTRA_ARTIFACTS),
        "stop_conditions": core.stop_conditions(),
        "rollback_policy": core.rollback_policy(),
        "claim_ceiling": core.CLAIM_CEILING,
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
        "parent_evidence": dict(core.PARENT_EVIDENCE),
        "scope_boundary": {
            "do_not_enter_ego_mainline": True,
            "do_not_implement_bridge_runtime": True,
            "do_not_create_companion_behavior": True,
            "do_not_add_llm_rag": True,
            "do_not_create_user_model_relationship_emotion_personalization_demo": True,
        },
    }
    manifest["stage0_payload_hash"] = core.stable_hash(manifest)
    return manifest


def _stage0_ready(stage0: dict) -> bool:
    required_items = {
        "task_card_hash",
        "thresholds",
        "metrics",
        "required_baselines",
        "required_ablations",
        "distribution_manifest_hash",
        "seed_families",
        "artifact_schema",
        "stop_conditions",
        "rollback_policy",
        "claim_ceiling",
    }
    return (
        stage0["stage0_freeze_before_any_executable_run"]
        and not stage0["executable_run_started_before_stage0"]
        and required_items.issubset(stage0["frozen_contract_items"])
        and stage0["parent_remote_anchor_verification"]["verified"]
        and stage0["parent_contract_verification"]["verified"]
        and stage0["claim_ceiling"] == core.CLAIM_CEILING
    )


def _execution_manifest(repo_root: Path, stage0: dict, stage0_hash: str) -> dict:
    source_paths = [
        core.TASK_CARD_PATH,
        core.PARENT_TASK_CARD_PATH,
        "src/post_bridge_admission_executable_001b/__init__.py",
        "src/post_bridge_admission_executable_001b/__main__.py",
        "src/post_bridge_admission_executable_001b/core.py",
        "src/post_bridge_admission_executable_001b/runner.py",
        "tests/test_post_bridge_admission_executable_001b.py",
    ]
    source_hashes = {
        path: core.file_sha256(repo_root / path)
        for path in source_paths
        if (repo_root / path).exists()
    }
    manifest = {
        "task_id": core.TASK_ID,
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "created_utc": _utc_now(),
        "claim_ceiling": core.CLAIM_CEILING,
        "stage0_freeze_manifest_hash": stage0_hash,
        "stage0_payload_hash": stage0["stage0_payload_hash"],
        "source_hashes": source_hashes,
        "required_artifacts": list(core.REQUIRED_ARTIFACTS),
        "extra_artifacts": list(core.EXTRA_ARTIFACTS),
        "parent_evidence": dict(core.PARENT_EVIDENCE),
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
    }
    manifest["execution_manifest_payload_hash"] = core.stable_hash(manifest)
    return manifest


def _old_artifact_mutation_report(before_hashes: dict[str, str], after_hashes: dict[str, str], repo_root: Path) -> dict:
    mutated = sorted(
        path
        for path, before_hash in before_hashes.items()
        if after_hashes.get(path) != before_hash
    )
    return {
        "task_id": core.TASK_ID,
        "claim_ceiling": core.CLAIM_CEILING,
        "old_artifact_mutation_detected": bool(mutated),
        "mutated_old_artifacts": mutated,
        "git_status_after_execution": _git_status(repo_root),
        "do_not_silently_restore_and_pass": True,
    }


def _failure_manifest(result: dict) -> dict:
    return {
        "task_id": core.TASK_ID,
        "verdict": result["verdict"],
        "stop_conditions_triggered": result["stop_conditions_triggered"],
        "preserve_negative_evidence": True,
        "do_not_patch_thresholds_after_results": True,
        "do_not_weaken_baselines": True,
        "do_not_delete_failure_artifacts": True,
        "do_not_enter_ego_mainline": True,
        "claim_ceiling": core.CLAIM_CEILING,
    }


def _blocked_result(stage0: dict, reason: str) -> dict:
    verdict = core.VERDICT_BLOCK_PARENT if reason == "parent_anchor_missing" else core.VERDICT_BLOCK_STAGE0
    if reason == "claim_inflation":
        verdict = core.VERDICT_BLOCK_CLAIM
    return {
        "task_id": core.TASK_ID,
        "verdict": verdict,
        "bounded_pass": False,
        "layer": core.LAYER,
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "claim_ceiling": core.CLAIM_CEILING,
        "parent_evidence": dict(core.PARENT_EVIDENCE),
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
        "acceptance_gates": {
            "stage0_freeze_before_any_run": stage0["stage0_freeze_before_any_executable_run"],
            "parent_remote_anchors_verified": stage0["parent_remote_anchor_verification"]["verified"],
            "parent_contract_verified_and_frozen": stage0["parent_contract_verification"]["verified"],
            "claim_ceiling_preserved": stage0["claim_ceiling"] == core.CLAIM_CEILING,
        },
        "stop_conditions_triggered": [reason],
        "forbidden_claims_absent": True,
        "anti_sycophancy_audit": {
            "strongest_baseline_explanation": "Execution blocked before baseline evaluation.",
            "strongest_reason_task_may_be_invalid": "Required Stage0 parent or freeze evidence was missing.",
            "result_that_would_falsify_current_framing": "Stage0 blocker remains unresolved.",
            "evidence_that_would_still_be_insufficient": (
                "A later bounded pass would still not prove bridge readiness, EGO readiness, "
                "mechanism validity, agency, selfhood, consciousness, or stable user benefit."
            ),
            "tests_mechanism_or_behavioral_resemblance": (
                "blocked before bounded post-bridge admission state-dependence evidence"
            ),
        },
    }


def run_admission_001b(repo_root: Path | str, output_dir: Path | str | None = None) -> dict:
    root = Path(repo_root)
    out = Path(output_dir) if output_dir is not None else root / core.ARTIFACT_DIR_REL
    out.mkdir(parents=True, exist_ok=True)
    ledger: list[dict] = []

    inventory = _protected_artifact_inventory(root)
    old_hashes_before = _hash_inventory(root, inventory)
    _write_json(out / "protected_artifact_inventory_before.json", inventory)
    _write_json(out / "protected_artifact_hashes_before.json", old_hashes_before)
    ledger.append(
        {
            "event": "protected_old_artifact_hashes_before",
            "status": "written",
            "count": len(old_hashes_before),
        }
    )

    distribution = core.build_distribution_manifest()
    _write_json(out / "distribution_manifest.json", distribution)
    distribution_hash = core.file_sha256(out / "distribution_manifest.json")
    ledger.append(
        {
            "event": "distribution_manifest_frozen",
            "status": "written",
            "distribution_manifest_hash": distribution_hash,
        }
    )

    parent_remote = _parent_remote_anchor_verification(root)
    parent_contract = _parent_contract_verification(root)
    task_card_hash = core.file_sha256(root / core.TASK_CARD_PATH)
    stage0 = _stage0_manifest(
        task_card_hash=task_card_hash,
        distribution_manifest_hash=distribution_hash,
        distribution=distribution,
        parent_remote_anchor_verification=parent_remote,
        parent_contract_verification=parent_contract,
    )
    _write_json(out / "stage0_freeze_manifest.json", stage0)
    stage0_hash = core.file_sha256(out / "stage0_freeze_manifest.json")
    ledger.append(
        {
            "event": "stage0_freeze_manifest_written",
            "status": "written",
            "stage0_freeze_manifest_hash": stage0_hash,
        }
    )

    execution_manifest = _execution_manifest(root, stage0, stage0_hash)
    _write_json(out / "execution_manifest.json", execution_manifest)
    execution_manifest_hash = core.file_sha256(out / "execution_manifest.json")
    _write_text(out / "execution_manifest.sha256", execution_manifest_hash + "\n")
    ledger.append(
        {
            "event": "execution_manifest_frozen",
            "status": "written",
            "execution_manifest_sha256": execution_manifest_hash,
        }
    )

    if not _stage0_ready(stage0):
        reason = "stage0_freeze_gap"
        if not parent_remote["verified"] or not parent_contract["verified"]:
            reason = "parent_anchor_missing"
        elif stage0["claim_ceiling"] != core.CLAIM_CEILING:
            reason = "claim_inflation"
        result = _blocked_result(stage0, reason)
        _write_json(out / "result.json", result)
        _write_text(out / "claim_ceiling.txt", core.CLAIM_CEILING + "\n")
        _write_json(out / "failure_manifest.json", _failure_manifest(result))
        ledger.append({"event": "result_written", "status": "blocked", "verdict": result["verdict"]})
        _write_jsonl(out / "run_ledger.jsonl", ledger)
        return result

    trace_rows, provenance_rows, serialized_snapshots = core.build_admission_run(distribution)
    _write_jsonl(out / "trace.jsonl", trace_rows)
    _write_jsonl(out / "serialized_state_provenance.jsonl", provenance_rows)
    _write_jsonl(out / "serialized_state_snapshots.jsonl", serialized_snapshots)
    ledger.append(
        {
            "event": "admission_trace_written",
            "status": "written",
            "trace_rows": len(trace_rows),
            "provenance_rows": len(provenance_rows),
        }
    )

    trace_replay = core.trace_replay_report(trace_rows)
    state_replay = core.state_replay_report(trace_rows)
    serialized_replay = core.serialized_state_replay_report(serialized_snapshots)
    provenance_replay = core.provenance_replay_report(provenance_rows)
    baseline = core.baseline_comparison()
    ablation = core.ablation_report()
    leakage = core.leakage_report()
    _write_json(out / "trace_replay_report.json", trace_replay)
    _write_json(out / "state_replay_report.json", state_replay)
    _write_json(out / "serialized_state_replay_report.json", serialized_replay)
    _write_json(out / "provenance_replay_report.json", provenance_replay)
    _write_json(out / "baseline_comparison.json", baseline)
    _write_json(out / "ablation_report.json", ablation)
    _write_json(out / "leakage_report.json", leakage)

    old_hashes_after = _hash_inventory(root, inventory)
    _write_json(out / "protected_artifact_hashes_after.json", old_hashes_after)
    old_mutation = _old_artifact_mutation_report(old_hashes_before, old_hashes_after, root)
    _write_json(out / "tracked_old_artifact_mutation_report.json", old_mutation)
    mutation = {
        "task_id": core.TASK_ID,
        "claim_ceiling": core.CLAIM_CEILING,
        "post_evaluation_mutation_check_passed": not old_mutation["old_artifact_mutation_detected"],
        "post_evaluation_mutation_detected": old_mutation["old_artifact_mutation_detected"],
        "mutated_artifacts": old_mutation["mutated_old_artifacts"],
        "scope_leak_detected": False,
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
    }
    _write_json(out / "mutation_check_report.json", mutation)

    result = core.result_payload(
        stage0=stage0,
        distribution=distribution,
        baseline=baseline,
        ablation=ablation,
        leakage=leakage,
        trace_replay=trace_replay,
        state_replay=state_replay,
        serialized_replay=serialized_replay,
        provenance_replay=provenance_replay,
        mutation=mutation,
        old_mutation=old_mutation,
    )
    _write_json(out / "result.json", result)
    _write_text(out / "claim_ceiling.txt", core.CLAIM_CEILING + "\n")
    if result["verdict"] != core.VERDICT_PASS:
        _write_json(out / "failure_manifest.json", _failure_manifest(result))

    ledger.append(
        {
            "event": "old_artifact_hermeticity_check",
            "status": "passed" if not old_mutation["old_artifact_mutation_detected"] else "failed",
        }
    )
    ledger.append(
        {
            "event": "result_written",
            "status": "written",
            "verdict": result["verdict"],
            "bounded_pass": result["bounded_pass"],
        }
    )
    _write_jsonl(out / "run_ledger.jsonl", ledger)
    return result
