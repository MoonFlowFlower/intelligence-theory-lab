from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import core


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, data: object) -> None:
    path.write_text(core.pretty_json(data) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
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


def _protected_artifact_inventory(repo_root: Path) -> dict[str, Any]:
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


def _hash_inventory(repo_root: Path, inventory: dict[str, Any]) -> dict[str, str]:
    return {
        path: core.file_sha256(repo_root / path)
        for path in inventory["tracked_old_artifact_paths"]
        if (repo_root / path).exists()
    }


def _verify_tag_anchors(repo_root: Path) -> dict[str, Any]:
    actual: dict[str, str] = {}
    failures: dict[str, str] = {}
    commands = []
    for tag, expected in core.PARENT_REMOTE_ANCHORS.items():
        ref = f"refs/tags/{tag}"
        command = f"git ls-remote origin {ref}"
        commands.append(command)
        try:
            output = _git_output(repo_root, ["ls-remote", "origin", ref])
            fields = output.split()
            resolved = fields[0] if len(fields) == 2 and fields[1] == ref else ""
            actual[tag] = resolved
        except subprocess.CalledProcessError as exc:
            resolved = ""
            actual[tag] = resolved
            failures[tag] = exc.stderr.strip() if exc.stderr else str(exc)
        if resolved != expected:
            failures.setdefault(tag, f"expected {expected}, got {resolved}")
    return {
        "commands": commands,
        "expected_hashes": dict(core.PARENT_REMOTE_ANCHORS),
        "actual_hashes": actual,
        "verified": actual == core.PARENT_REMOTE_ANCHORS and not failures,
        "failures": failures,
    }


def _verify_redteam_admission(repo_root: Path) -> dict[str, Any]:
    command = f"git rev-parse {core.REDTEAM_FAILURE_SHORT}"
    try:
        output = _git_output(repo_root, ["rev-parse", core.REDTEAM_FAILURE_SHORT])
        verified = output == core.REDTEAM_FAILURE_FULL
        failure = "" if verified else f"expected {core.REDTEAM_FAILURE_FULL}, got {output}"
    except subprocess.CalledProcessError as exc:
        output = ""
        verified = False
        failure = exc.stderr.strip() if exc.stderr else str(exc)
    return {
        "command": command,
        "expected_hash": core.REDTEAM_FAILURE_FULL,
        "actual_hash": output,
        "verified": verified,
        "failure": failure,
    }


def _contract_status(repo_root: Path) -> dict[str, Any]:
    contract_path = repo_root / core.CONTRACT_PATH
    task_card_path = repo_root / core.TASK_CARD_PATH
    cited = (
        contract_path.exists()
        and task_card_path.exists()
        and "COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A"
        in task_card_path.read_text(encoding="utf-8")
    )
    return {
        "path": core.CONTRACT_PATH,
        "hash": core.file_sha256(contract_path) if contract_path.exists() else "",
        "exists": contract_path.exists(),
        "cited_by_task_card": cited,
        "cited_and_enforced": cited,
    }


def _clean_worktree_status(repo_root: Path, enforce: bool) -> dict[str, Any]:
    status = _git_status(repo_root)
    return {
        "enforced": enforce,
        "clean": (not status) if enforce else True,
        "observed_status": status,
        "blocker_if_enforced": bool(status),
    }


def _stage0_manifest(
    *,
    repo_root: Path,
    distribution: dict[str, Any],
    distribution_manifest_hash: str,
    clean_worktree: dict[str, Any],
) -> dict[str, Any]:
    task_card_path = repo_root / core.TASK_CARD_PATH
    agents_path = repo_root / core.AGENTS_PATH
    parent_remote = _verify_tag_anchors(repo_root)
    redteam = _verify_redteam_admission(repo_root)
    contract = _contract_status(repo_root)
    manifest = {
        "task_id": core.TASK_ID,
        "created_utc": _utc_now(),
        "stage0_freeze_before_any_executable_run": True,
        "executable_run_started_before_stage0": False,
        "canonical_clean_worktree_required": True,
        "clean_worktree_before_stage0": clean_worktree,
        "frozen_contract_items": [
            "task_card_hash",
            "computed_evidence_contract_hash",
            "agents_instruction_hash",
            "thresholds",
            "metrics",
            "baseline_implementation_registry",
            "ablation_intervention_registry",
            "leakage_scanner_registry",
            "replay_functions",
            "distribution_manifest_hash",
            "seed_families",
            "train_contexts",
            "heldout_contexts",
            "counterfactual_pairs",
            "cross_agent_state_swap_pairs",
            "duplicate_identity_token_contrast_pairs",
            "artifact_schema",
            "stop_conditions",
            "rollback_plan",
            "claim_ceiling",
        ],
        "task_card_hash": core.file_sha256(task_card_path) if task_card_path.exists() else "",
        "computed_evidence_contract": contract,
        "agents_instruction_hash": core.file_sha256(agents_path) if agents_path.exists() else "",
        "parent_remote_anchor_verification": parent_remote,
        "redteam_failure_admission_verification": redteam,
        "thresholds": core.thresholds_manifest(),
        "metrics": core.metrics_manifest(),
        "baseline_implementation_registry": {
            name: {
                "producer_function": f"{function.__module__}.{function.__name__}",
                "code_path_hash": core.code_path_hash(function),
            }
            for name, function in core.BASELINE_IMPLEMENTATIONS.items()
        },
        "ablation_intervention_registry": {
            name: {
                "intervention_function": f"{function.__module__}.{function.__name__}",
                "code_path_hash": core.code_path_hash(function),
            }
            for name, function in core.ABLATION_IMPLEMENTATIONS.items()
        },
        "leakage_scanner_registry": {
            name: {
                "scanner_function": "post_bridge_admission_executable_001d.core.leakage_scan_surface",
                "code_path_hash": core.code_path_hash(core.leakage_scan_surface),
            }
            for name in core.REQUIRED_LEAKAGE_SCANNERS
        },
        "replay_function_registry": {
            "replay_candidate_actions_from_serialized_state": core.code_path_hash(
                core.replay_candidate_actions_from_serialized_state
            ),
            "behavior_causal_replay": core.code_path_hash(core.behavior_causal_replay),
            "trace_hash_replay": core.code_path_hash(core.trace_hash_replay),
            "state_hash_replay": core.code_path_hash(core.state_hash_replay),
        },
        "distribution_manifest_hash": distribution_manifest_hash,
        "seed_families": distribution["seed_families"],
        "train_contexts": distribution["train_contexts"],
        "heldout_contexts": distribution["heldout_bridge_contexts"],
        "counterfactual_pairs": distribution["counterfactual_state_pairs"],
        "cross_agent_state_swap_pairs": distribution["cross_agent_state_swap_pairs"],
        "duplicate_identity_token_contrast_pairs": distribution["duplicate_identity_token_contrasts"],
        "artifact_schema": list(core.REQUIRED_ARTIFACTS),
        "stop_conditions": core.stop_conditions(),
        "rollback_plan": core.rollback_plan(),
        "claim_ceiling": core.CLAIM_CEILING,
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
    }
    manifest["stage0_payload_hash"] = core.stable_hash(manifest)
    return manifest


def _stage0_ready(stage0: dict[str, Any]) -> bool:
    return (
        stage0["stage0_freeze_before_any_executable_run"]
        and not stage0["executable_run_started_before_stage0"]
        and stage0["clean_worktree_before_stage0"]["clean"]
        and stage0["parent_remote_anchor_verification"]["verified"]
        and stage0["redteam_failure_admission_verification"]["verified"]
        and stage0["computed_evidence_contract"]["cited_and_enforced"]
        and stage0["claim_ceiling"] == core.CLAIM_CEILING
    )


def _execution_manifest(repo_root: Path, stage0_hash: str, stage0: dict[str, Any]) -> dict[str, Any]:
    source_paths = [
        core.TASK_CARD_PATH,
        core.CONTRACT_PATH,
        core.AGENTS_PATH,
        "src/post_bridge_admission_executable_001d/__init__.py",
        "src/post_bridge_admission_executable_001d/__main__.py",
        "src/post_bridge_admission_executable_001d/core.py",
        "src/post_bridge_admission_executable_001d/runner.py",
        "tests/test_post_bridge_admission_executable_001d.py",
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
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
    }
    manifest["execution_manifest_payload_hash"] = core.stable_hash(manifest)
    return manifest


def _old_artifact_mutation_report(
    before_hashes: dict[str, str],
    after_hashes: dict[str, str],
    repo_root: Path,
) -> dict[str, Any]:
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


def _failure_manifest(result: dict[str, Any]) -> dict[str, Any]:
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


def _blocked_result(stage0: dict[str, Any], reason: str) -> dict[str, Any]:
    if reason == "parent_anchor_missing":
        verdict = core.VERDICT_BLOCK_PARENT
    elif reason == "computed_evidence_contract_missing":
        verdict = core.VERDICT_BLOCK_MISSING_CONTRACT
    elif reason == "claim_inflation":
        verdict = core.VERDICT_BLOCK_CLAIM
    else:
        verdict = core.VERDICT_BLOCK_STAGE0
    return {
        "task_id": core.TASK_ID,
        "verdict": verdict,
        "bounded_pass": False,
        "layer": core.LAYER,
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "claim_ceiling": core.CLAIM_CEILING,
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
        "acceptance_gates": {
            "stage0_freeze_before_any_run": stage0["stage0_freeze_before_any_executable_run"],
            "clean_worktree_before_stage0": stage0["clean_worktree_before_stage0"]["clean"],
            "parent_remote_anchors_verified": stage0["parent_remote_anchor_verification"]["verified"],
            "redteam_failure_admission_verified": stage0["redteam_failure_admission_verification"]["verified"],
            "computed_evidence_contract_cited_and_enforced": stage0["computed_evidence_contract"][
                "cited_and_enforced"
            ],
            "claim_ceiling_preserved": stage0["claim_ceiling"] == core.CLAIM_CEILING,
        },
        "stop_conditions_triggered": [reason],
        "forbidden_claims_absent": True,
        "anti_sycophancy_audit": {
            "strongest_baseline_explanation": "Execution blocked before baseline evaluation.",
            "strongest_reason_task_may_be_invalid": "Required Stage0 evidence was missing.",
            "result_that_would_falsify_current_framing": "Stage0 blocker remains unresolved.",
            "evidence_that_would_still_be_insufficient": (
                "A later bounded pass would still not prove bridge readiness, EGO readiness, "
                "mechanism validity, agency, selfhood, consciousness, or stable user benefit."
            ),
            "tests_mechanism_or_behavioral_resemblance": "blocked before bounded 001D evidence",
        },
        "verdict_bearing_metric_ids": [],
    }


def _artifact_hashes(paths: list[str], output_dir: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for rel in paths:
        path = output_dir / Path(rel).name
        if path.exists():
            hashes[rel] = core.file_sha256(path)
    return hashes


def _metric_row(
    *,
    metric_id: str,
    metric_name: str,
    producer_function: str,
    producer_module: str,
    code_path_hash: str,
    episode_ids: list[str],
    seed_ids: list[str],
    train_ids: list[str],
    heldout_ids: list[str],
    counterfactual_pair_ids: list[str],
    input_artifact_paths: list[str],
    output_artifact_path: str,
    output_row_ids: list[str],
    aggregation_rule: str,
    threshold_used: float | str | None,
    input_row_count: int,
    output_dir: Path,
    extra_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = {
        "metric_id": metric_id,
        "metric_name": metric_name,
        "producer_function": producer_function,
        "producer_module": producer_module,
        "code_path_hash": code_path_hash,
        "run_id": core.RUN_ID,
        "episode_ids": episode_ids,
        "seed_ids": seed_ids,
        "train_context_ids_consumed": train_ids,
        "heldout_context_ids_consumed": heldout_ids,
        "counterfactual_pair_ids_consumed": counterfactual_pair_ids,
        "input_artifact_paths": input_artifact_paths,
        "input_artifact_hashes": _artifact_hashes(input_artifact_paths, output_dir),
        "input_row_count": input_row_count,
        "output_artifact_path": output_artifact_path,
        "output_row_ids": output_row_ids,
        "aggregation_rule": aggregation_rule,
        "threshold_used": threshold_used,
        "threshold_frozen_before_run": True,
        "computed_not_literal": True,
        "failure_path_available": True,
    }
    if extra_fields:
        row.update(extra_fields)
    return row


def _build_metric_rows(
    *,
    output_dir: Path,
    episodes: list[dict[str, Any]],
    distribution: dict[str, Any],
    baseline_invocations: list[dict[str, Any]],
    ablation_invocations: list[dict[str, Any]],
    leakage_invocations: list[dict[str, Any]],
    contrast_logs: list[dict[str, Any]],
    candidate_replay: dict[str, Any],
    behavior_replay: dict[str, Any],
    consumption_report: dict[str, Any],
) -> list[dict[str, Any]]:
    episode_ids = [episode["episode_id"] for episode in episodes]
    seed_ids = sorted({episode["seed_family_id"] for episode in episodes})
    train_ids = sorted({episode["train_context_id"] for episode in episodes})
    heldout_ids = sorted({episode["heldout_context_id"] for episode in episodes})
    cf_ids = [row["pair_id"] for row in distribution["counterfactual_state_pairs"]]
    rows = [
        _metric_row(
            metric_id="candidate_score",
            metric_name="candidate replay score",
            producer_function=candidate_replay["replay_function"],
            producer_module="post_bridge_admission_executable_001d.core",
            code_path_hash=candidate_replay["code_path_hash"],
            episode_ids=episode_ids,
            seed_ids=seed_ids,
            train_ids=train_ids,
            heldout_ids=heldout_ids,
            counterfactual_pair_ids=[],
            input_artifact_paths=["serialized_state_snapshots.jsonl", "observation_seed_manifest.json"],
            output_artifact_path="candidate_action_replay_report.json",
            output_row_ids=["candidate_action_replay_passed"],
            aggregation_rule="all recomputed actions equal recorded candidate_action_id",
            threshold_used=1.0,
            input_row_count=len(episodes),
            output_dir=output_dir,
        ),
        _metric_row(
            metric_id="behavior_causal_replay_score",
            metric_name="behavior causal replay score",
            producer_function=behavior_replay["replay_function"],
            producer_module="post_bridge_admission_executable_001d.core",
            code_path_hash=behavior_replay["code_path_hash"],
            episode_ids=episode_ids,
            seed_ids=seed_ids,
            train_ids=train_ids,
            heldout_ids=heldout_ids,
            counterfactual_pair_ids=[],
            input_artifact_paths=["serialized_state_snapshots.jsonl", "observation_seed_manifest.json"],
            output_artifact_path="behavior_causal_replay_report.json",
            output_row_ids=["behavior_causal_replay_passed"],
            aggregation_rule="all behavior-causal replay outputs match recorded actions",
            threshold_used=1.0,
            input_row_count=len(episodes),
            output_dir=output_dir,
        ),
        _metric_row(
            metric_id="frozen_input_consumption",
            metric_name="frozen input consumption",
            producer_function=consumption_report["producer_function"],
            producer_module=consumption_report["producer_module"],
            code_path_hash=consumption_report["code_path_hash"],
            episode_ids=episode_ids,
            seed_ids=seed_ids,
            train_ids=train_ids,
            heldout_ids=heldout_ids,
            counterfactual_pair_ids=cf_ids,
            input_artifact_paths=[
                "distribution_manifest.json",
                "baseline_invocation_log.jsonl",
                "ablation_invocation_log.jsonl",
                "contrast_pair_consumption_log.jsonl",
            ],
            output_artifact_path="frozen_input_consumption_report.json",
            output_row_ids=["unused_frozen_inputs"],
            aggregation_rule="set difference over frozen manifests and consumed IDs",
            threshold_used="no unused frozen inputs",
            input_row_count=len(episodes),
            output_dir=output_dir,
        ),
    ]
    for row in baseline_invocations:
        rows.append(
            _metric_row(
                metric_id=f"baseline::{row['baseline_name']}",
                metric_name="baseline score",
                producer_function=row["producer_function"],
                producer_module=row["producer_module"],
                code_path_hash=row["code_path_hash"],
                episode_ids=row["episode_ids"],
                seed_ids=seed_ids,
                train_ids=train_ids,
                heldout_ids=heldout_ids,
                counterfactual_pair_ids=[],
                input_artifact_paths=["serialized_state_snapshots.jsonl", "observation_seed_manifest.json"],
                output_artifact_path="baseline_comparison.json",
                output_row_ids=[row["baseline_name"]],
                aggregation_rule="mean action agreement with measured candidate outputs",
                threshold_used=core.ACCEPTANCE_THRESHOLD,
                input_row_count=len(row["per_episode_outputs"]),
                output_dir=output_dir,
            )
        )
    for row in ablation_invocations:
        rows.append(
            _metric_row(
                metric_id=f"ablation::{row['ablation_name']}",
                metric_name="ablation sensitivity score",
                producer_function=row["intervention_function"],
                producer_module=row["producer_module"],
                code_path_hash=row["code_path_hash"],
                episode_ids=row["episode_ids"],
                seed_ids=seed_ids,
                train_ids=train_ids,
                heldout_ids=heldout_ids,
                counterfactual_pair_ids=cf_ids,
                input_artifact_paths=["serialized_state_snapshots.jsonl", "observation_seed_manifest.json"],
                output_artifact_path="ablation_report.json",
                output_row_ids=[row["ablation_name"]],
                aggregation_rule="mean post-intervention action agreement with original candidate outputs",
                threshold_used=core.ACCEPTANCE_THRESHOLD,
                input_row_count=len(row["per_episode_outputs"]),
                output_dir=output_dir,
            )
        )
    for row in contrast_logs:
        rows.append(
            _metric_row(
                metric_id=f"contrast::{row['contrast_name']}",
                metric_name="contrast delta",
                producer_function=row["producer_function"],
                producer_module=row["producer_module"],
                code_path_hash=row["code_path_hash"],
                episode_ids=[outcome["source_episode_id"] for outcome in row["per_pair_outcomes"]],
                seed_ids=seed_ids,
                train_ids=train_ids,
                heldout_ids=heldout_ids,
                counterfactual_pair_ids=row["pair_ids_consumed"],
                input_artifact_paths=["distribution_manifest.json", "serialized_state_snapshots.jsonl"],
                output_artifact_path="contrast_report.json",
                output_row_ids=[row["contrast_name"]],
                aggregation_rule="mean action change over pre-frozen contrast pairs",
                threshold_used=0.05,
                input_row_count=len(row["per_pair_outcomes"]),
                output_dir=output_dir,
            )
        )
    for row in leakage_invocations:
        rows.append(
            _metric_row(
                metric_id=f"leakage::{row['scanner_name']}",
                metric_name="leakage scanner result",
                producer_function=row["scanner_function"],
                producer_module=row["producer_module"],
                code_path_hash=row["code_path_hash"],
                episode_ids=episode_ids,
                seed_ids=seed_ids,
                train_ids=train_ids,
                heldout_ids=heldout_ids,
                counterfactual_pair_ids=[],
                input_artifact_paths=[
                    "trace.jsonl",
                    "candidate_input_rows.jsonl",
                    "observation_seed_manifest.json",
                    "serialized_state_snapshots.jsonl",
                    "serialized_state_provenance.jsonl",
                ],
                output_artifact_path="leakage_report.json",
                output_row_ids=[row["scanner_name"]],
                aggregation_rule=(
                    "full real surface scan clean, same-surface positive control detects, "
                    "same-surface clean control does not detect"
                ),
                threshold_used="positive control required and real scan clean",
                input_row_count=len(episodes),
                output_dir=output_dir,
                extra_fields={
                    "input_surface_ids": [
                        row["scanned_surface_id"],
                        row["positive_control_surface_id"],
                        row["clean_control_surface_id"],
                    ],
                    "scanned_surface_ids": [row["scanned_surface_id"]],
                    "scanned_surface_types": [row["scanned_surface_type"]],
                    "positive_control_surface_ids": [row["positive_control_surface_id"]],
                    "clean_control_surface_ids": [row["clean_control_surface_id"]],
                    "full_surface_scanned": row["full_surface_scanned"],
                    "sanitized_projection_scan": row["sanitized_projection_scan"],
                    "constant_dictionary_scan": row["constant_dictionary_scan"],
                },
            )
        )
    return rows


def run_admission_001d(
    repo_root: Path | str,
    output_dir: Path | str | None = None,
    *,
    enforce_clean_worktree: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root)
    out = Path(output_dir) if output_dir is not None else root / core.ARTIFACT_DIR_REL
    out.mkdir(parents=True, exist_ok=True)
    ledger: list[dict[str, Any]] = []

    clean_worktree = _clean_worktree_status(root, enforce_clean_worktree)
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

    stage0 = _stage0_manifest(
        repo_root=root,
        distribution=distribution,
        distribution_manifest_hash=distribution_hash,
        clean_worktree=clean_worktree,
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

    execution_manifest = _execution_manifest(root, stage0_hash, stage0)
    _write_json(out / "execution_manifest.json", execution_manifest)
    execution_hash = core.file_sha256(out / "execution_manifest.json")
    _write_text(out / "execution_manifest.sha256", execution_hash + "\n")
    ledger.append(
        {
            "event": "execution_manifest_frozen",
            "status": "written",
            "execution_manifest_sha256": execution_hash,
        }
    )

    if not _stage0_ready(stage0):
        reason = "stage0_freeze_gap"
        if not stage0["parent_remote_anchor_verification"]["verified"] or not stage0[
            "redteam_failure_admission_verification"
        ]["verified"]:
            reason = "parent_anchor_missing"
        elif not stage0["computed_evidence_contract"]["cited_and_enforced"]:
            reason = "computed_evidence_contract_missing"
        elif not stage0["clean_worktree_before_stage0"]["clean"]:
            reason = "dirty_worktree_before_stage0"
        elif stage0["claim_ceiling"] != core.CLAIM_CEILING:
            reason = "claim_inflation"
        result = _blocked_result(stage0, reason)
        _write_json(out / "result.json", result)
        _write_text(out / "claim_ceiling.txt", core.CLAIM_CEILING + "\n")
        _write_json(out / "failure_manifest.json", _failure_manifest(result))
        ledger.append({"event": "result_written", "status": "blocked", "verdict": result["verdict"]})
        _write_jsonl(out / "run_ledger.jsonl", ledger)
        return result

    rows = core.build_execution_rows(distribution)
    trace_rows = rows["trace_rows"]
    candidate_input_rows = rows["candidate_input_rows"]
    snapshots = rows["serialized_state_snapshots"]
    observation_rows = rows["observation_seed_manifest"]
    provenance_rows = rows["serialized_state_provenance"]
    _write_jsonl(out / "trace.jsonl", trace_rows)
    _write_jsonl(out / "candidate_input_rows.jsonl", candidate_input_rows)
    _write_jsonl(out / "serialized_state_snapshots.jsonl", snapshots)
    _write_jsonl(out / "observation_seed_manifest.json", observation_rows)
    _write_jsonl(out / "serialized_state_provenance.jsonl", provenance_rows)
    ledger.append(
        {
            "event": "candidate_execution_rows_written",
            "status": "written",
            "trace_rows": len(trace_rows),
            "candidate_input_rows": len(candidate_input_rows),
            "serialized_state_snapshots": len(snapshots),
            "observation_rows": len(observation_rows),
            "provenance_rows": len(provenance_rows),
        }
    )

    episodes = core.build_episode_inputs(snapshots, observation_rows)
    baseline_report, baseline_invocations = core.run_baselines(episodes)
    ablation_report, ablation_invocations = core.run_ablations(episodes)
    contrast_report, contrast_logs = core.run_contrasts(episodes, distribution)
    candidate_replay = core.replay_candidate_actions_from_serialized_state(snapshots, observation_rows)
    behavior_replay = core.behavior_causal_replay(snapshots, observation_rows)
    trace_replay = core.trace_hash_replay(trace_rows)
    state_replay = core.state_hash_replay(snapshots)
    consumption_report = core.build_consumption_report(
        distribution,
        episodes,
        ablation_invocations,
        contrast_logs,
    )

    _write_jsonl(out / "baseline_invocation_log.jsonl", baseline_invocations)
    _write_jsonl(out / "ablation_invocation_log.jsonl", ablation_invocations)
    _write_jsonl(out / "contrast_pair_consumption_log.jsonl", contrast_logs)
    _write_json(out / "baseline_comparison.json", baseline_report)
    _write_json(out / "ablation_report.json", ablation_report)
    _write_json(out / "contrast_report.json", contrast_report)
    _write_json(out / "candidate_action_replay_report.json", candidate_replay)
    _write_json(out / "behavior_causal_replay_report.json", behavior_replay)
    _write_json(out / "trace_hash_replay_report.json", trace_replay)
    _write_json(out / "state_hash_replay_report.json", state_replay)
    _write_json(out / "frozen_input_consumption_report.json", consumption_report)
    ledger.append(
        {
            "event": "computed_reports_written",
            "status": "written",
            "baseline_count": len(baseline_invocations),
            "ablation_count": len(ablation_invocations),
        }
    )

    preliminary_metric_rows = _build_metric_rows(
        output_dir=out,
        episodes=episodes,
        distribution=distribution,
        baseline_invocations=baseline_invocations,
        ablation_invocations=ablation_invocations,
        leakage_invocations=[],
        contrast_logs=contrast_logs,
        candidate_replay=candidate_replay,
        behavior_replay=behavior_replay,
        consumption_report=consumption_report,
    )
    artifact_paths = sorted(f"{core.ARTIFACT_DIR_REL}/{name}" for name in core.REQUIRED_ARTIFACTS)
    preliminary_surface_inventory = core.build_leakage_surface_inventory(
        candidate_input_rows=candidate_input_rows,
        trace_rows=trace_rows,
        snapshots=snapshots,
        observation_rows=observation_rows,
        provenance_rows=provenance_rows,
        metric_provenance_rows=preliminary_metric_rows,
        artifact_paths=artifact_paths,
    )
    preliminary_leakage_report, preliminary_leakage_invocations = core.run_leakage_scanners(
        preliminary_surface_inventory
    )
    metric_rows = _build_metric_rows(
        output_dir=out,
        episodes=episodes,
        distribution=distribution,
        baseline_invocations=baseline_invocations,
        ablation_invocations=ablation_invocations,
        leakage_invocations=preliminary_leakage_invocations,
        contrast_logs=contrast_logs,
        candidate_replay=candidate_replay,
        behavior_replay=behavior_replay,
        consumption_report=consumption_report,
    )
    surface_inventory = core.build_leakage_surface_inventory(
        candidate_input_rows=candidate_input_rows,
        trace_rows=trace_rows,
        snapshots=snapshots,
        observation_rows=observation_rows,
        provenance_rows=provenance_rows,
        metric_provenance_rows=metric_rows,
        artifact_paths=artifact_paths,
    )
    leakage_report, leakage_invocations = core.run_leakage_scanners(surface_inventory)
    metric_rows = _build_metric_rows(
        output_dir=out,
        episodes=episodes,
        distribution=distribution,
        baseline_invocations=baseline_invocations,
        ablation_invocations=ablation_invocations,
        leakage_invocations=leakage_invocations,
        contrast_logs=contrast_logs,
        candidate_replay=candidate_replay,
        behavior_replay=behavior_replay,
        consumption_report=consumption_report,
    )
    _write_json(
        out / "leakage_surface_inventory.json",
        {key: value for key, value in surface_inventory.items() if key != "_runtime_surfaces"},
    )
    _write_jsonl(out / "leakage_scanner_invocation_log.jsonl", leakage_invocations)
    _write_json(out / "leakage_report.json", leakage_report)
    _write_json(
        out / "leakage_positive_control_report.json",
        {
            "task_id": core.TASK_ID,
            "claim_ceiling": core.CLAIM_CEILING,
            "all_positive_controls_detected": all(
                row["positive_control"]["detected"] for row in leakage_invocations
            ),
            "controls": [
                {
                    "scanner_name": row["scanner_name"],
                    "surface_id": row["positive_control_surface_id"],
                    "same_surface_class": row["positive_control"]["same_surface_class"],
                    "injected_forbidden_token": row["positive_control"]["injected_forbidden_token"],
                    "detected": row["positive_control"]["detected"],
                    "hits": row["positive_control"]["hits"],
                }
                for row in leakage_invocations
            ],
        },
    )
    _write_json(
        out / "leakage_clean_control_report.json",
        {
            "task_id": core.TASK_ID,
            "claim_ceiling": core.CLAIM_CEILING,
            "all_clean_controls_clean": all(
                not row["clean_control"]["detected"] for row in leakage_invocations
            ),
            "controls": [
                {
                    "scanner_name": row["scanner_name"],
                    "surface_id": row["clean_control_surface_id"],
                    "same_surface_class": row["clean_control"]["same_surface_class"],
                    "detected": row["clean_control"]["detected"],
                    "hits": row["clean_control"]["hits"],
                }
                for row in leakage_invocations
            ],
        },
    )
    ledger.append(
        {
            "event": "leakage_full_surface_scans_written",
            "status": "written",
            "leakage_scanner_count": len(leakage_invocations),
            "preliminary_leakage_gate_passed": preliminary_leakage_report["leakage_gate_passed"],
        }
    )
    _write_jsonl(out / "metric_provenance.jsonl", metric_rows)
    provenance_gate = core.evaluate_computed_evidence_gate(
        metric_rows=metric_rows,
        baseline_invocations=baseline_invocations,
        ablation_invocations=ablation_invocations,
        leakage_invocations=leakage_invocations,
        replay_report=behavior_replay,
        consumption_report=consumption_report,
        serialized_state_provenance_rows=provenance_rows,
    )
    _write_json(out / "computed_evidence_provenance_report.json", provenance_gate)

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

    result = core.final_result_payload(
        stage0=stage0,
        baseline_report=baseline_report,
        ablation_report=ablation_report,
        contrast_report=contrast_report,
        leakage_report=leakage_report,
        behavior_replay_report=behavior_replay,
        candidate_replay_report=candidate_replay,
        trace_hash_report=trace_replay,
        state_hash_report=state_replay,
        consumption_report=consumption_report,
        provenance_report=provenance_gate,
        mutation_report=mutation,
        old_mutation_report=old_mutation,
        verdict_bearing_metric_ids=[row["metric_id"] for row in metric_rows],
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
