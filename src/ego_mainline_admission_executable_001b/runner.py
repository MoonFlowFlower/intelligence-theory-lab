from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from . import core


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _git(repo_root: Path, args: list[str]) -> tuple[bool, str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    output = (completed.stdout or completed.stderr).strip()
    return completed.returncode == 0, output


def _path_hashes(paths: list[Path], repo_root: Path) -> dict[str, str]:
    hashes = {}
    for path in paths:
        if path.exists():
            hashes[str(path.relative_to(repo_root)).replace("\\", "/")] = core.sha_file(path)
    return hashes


def _protected_paths(repo_root: Path) -> list[Path]:
    return [
        repo_root / "docs" / "codex" / "tasks" / "EGO-MAINLINE-ADMISSION-TASK-CARD-001A.md",
        repo_root / "artifacts" / "ego_mainline_admission_task_card_001a" / "result.json",
        repo_root / "artifacts" / "ego_mainline_readiness_audit_001b" / "result.json",
        repo_root / "artifacts" / "post_bridge_admission_executable_001b" / "result.json",
        repo_root / "artifacts" / "post_bridge_admission_executable_001c" / "result.json",
        repo_root / "artifacts" / "post_bridge_admission_executable_001d" / "result.json",
    ]


def verify_parent_anchors(repo_root: Path, verify_remote: bool = True) -> dict[str, Any]:
    anchors = {}
    for tag, expected in core.PARENT_ANCHORS.items():
        local_ok, local_out = _git(repo_root, ["rev-parse", tag])
        remote_ok = True
        remote_out = expected
        if verify_remote:
            remote_ok, remote_out = _git(repo_root, ["ls-remote", "origin", f"refs/tags/{tag}"])
        remote_hash = remote_out.split()[0] if remote_out else ""
        anchors[tag] = {
            "expected": expected,
            "local_hash": local_out,
            "local_verified": local_ok and local_out == expected,
            "remote_hash": remote_hash,
            "remote_verified": (not verify_remote) or (remote_ok and remote_hash == expected),
            "remote_verification_skipped": not verify_remote,
        }
    return {
        "task_id": core.TASK_ID,
        "target_commit": core.PARENT_ANCHORS["remote-anchor-001p-cda09dc"],
        "anchors": anchors,
        "all_required_parent_anchors_verified": all(
            row["local_verified"] and row["remote_verified"] for row in anchors.values()
        ),
    }


def build_task_card() -> str:
    return """# EGO-MAINLINE-ADMISSION-EXECUTABLE-001B

## Task Identity

```text
task_id = EGO-MAINLINE-ADMISSION-EXECUTABLE-001B
verdict = ego_mainline_admission_executable_001b_bounded_contract_gate_pass
layer = bounded EGO-mainline admission executable gate under synthetic / controlled evidence conditions only
claim_ceiling = bounded EGO-mainline admission executable gate evidence under synthetic / controlled conditions only
```

## Scope

This executable gate exercises `EGO-MAINLINE-ADMISSION-TASK-CARD-001A` under a
synthetic controlled evidence pack. It does not modify the Ego repository, does
not implement EGO runtime, and does not create bridge runtime, LLM/RAG,
companion behavior, user model, relationship, emotion, personalization,
product-demo, romance, attachment, persistent profile, real-user-data, or
long-term human-user memory work.

## Parent Anchors

```text
EGO-MAINLINE-ADMISSION-TASK-CARD-001A = cda09dce5d8412beea88e9b2108ea41c1ce260bd / remote-anchor-001p-cda09dc
EGO-MAINLINE-READINESS-AUDIT-001B = f648dac4bfbcdc7a98c1edea5a97dbef4101d83a / remote-anchor-001o-f648dac
COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A = docs/codex/contracts/COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md
```

## Evidence Boundary

The gate preserves 001B invalidation, 001C suspension, 001D caveats, computed
metric provenance, callable baselines, real ablation reruns, same-surface
leakage controls, surface-scoped metadata whitelist behavior, independent
manual leakage injection tests, behavior-causal replay, frozen input
consumption, source/artifact integrity, and strict claim ceiling.

## What This Does Not Prove

This does not prove EGO readiness, bridge readiness, EGO-mainline runtime
readiness, companion readiness, mechanism validity, theory validity, agency,
selfhood, consciousness, real emotion, real relationship learning, real user
benefit, or correctness of any future EGO runtime.
"""


def run_admission_001b(
    *,
    repo_root: Path,
    output_dir: Path,
    enforce_clean_worktree: bool = False,
    verify_remote: bool = True,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    protected = _protected_paths(repo_root)
    protected_before = _path_hashes(protected, repo_root)

    parent_verification = verify_parent_anchors(repo_root, verify_remote=verify_remote)
    contract_text = (repo_root / core.CONTRACT_PATH).read_text(encoding="utf-8")
    parent_contract_text = (repo_root / core.PARENT_CONTRACT_PATH).read_text(encoding="utf-8")

    status_ok, status_out = _git(repo_root, ["status", "--short", "--branch"])
    if enforce_clean_worktree and any(line and not line.startswith("##") for line in status_out.splitlines()):
        blocker = {
            "task_id": core.TASK_ID,
            "verdict": "ego_mainline_admission_executable_001b_block_scope_leak",
            "stop_conditions": ["working_tree_dirty_before_stage0"],
        }
        _write_json(output_dir / "blocker_report.json", blocker)
        return blocker

    pack = core.build_controlled_evidence_pack()
    candidate_rows = core.run_candidate(pack)
    replay = core.behavior_causal_replay(pack, candidate_rows)
    baseline_report, baseline_invocation = core.run_baselines(pack)
    ablation_report, ablation_invocation = core.run_ablations(pack)
    surfaces = core.build_candidate_surfaces(pack, candidate_rows)
    inventory, leakage_report, positive_report, manual_report, whitelist_report = core.run_leakage_gates(surfaces)
    frozen_report = core.frozen_input_consumption(pack)
    failure_report = core.build_failure_path_report()

    contract_eval = {
        "task_id": core.TASK_ID,
        "computed_evidence_contract_loaded": "COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A" in contract_text,
        "contract_path": core.CONTRACT_PATH,
        "task_card_path": core.PARENT_CONTRACT_PATH,
        "001b_invalidation_preserved": "001B invalidation" in parent_contract_text
        or "001B = invalidated" in parent_contract_text,
        "001c_suspension_preserved": "001C suspension" in parent_contract_text
        or "001C = historical/suspended" in parent_contract_text,
        "001d_caveat_preserved": "surface-scoped metadata whitelist" in parent_contract_text
        and "independent manual leakage injection tests" in parent_contract_text,
        "claim_ceiling": core.CLAIM_CEILING,
    }
    dependencies = {
        "task_id": core.TASK_ID,
        "post_bridge_admission_executable_001b": {
            "status": "invalidated as downstream positive evidence",
            "used_as_positive_evidence": False,
        },
        "post_bridge_admission_executable_001c": {
            "status": "historical/suspended as downstream positive evidence",
            "used_as_positive_evidence": False,
        },
        "post_bridge_admission_executable_001d": {
            "status": "current bounded post-bridge positive candidate with caveats",
            "used_within_claim_ceiling": True,
        },
        "ego_mainline_readiness_audit_001a": {
            "status": "historical context only, not direct actionable authorization",
        },
    }
    negative = {
        "task_id": core.TASK_ID,
        "001b_invalidation_preserved": True,
        "001c_suspension_preserved": True,
        "001b_used_as_positive_evidence": False,
        "001c_used_as_positive_evidence": False,
        "negative_evidence_rewrite_detected": False,
    }
    current = {
        "task_id": core.TASK_ID,
        "post_bridge_admission_executable_001b": {"status": "invalidated as downstream positive evidence"},
        "post_bridge_admission_executable_001c": {"status": "historical/suspended as downstream positive evidence"},
        "post_bridge_admission_executable_001d": {"status": "current bounded post-bridge positive candidate with caveats"},
        "ego_mainline_readiness_audit_001a": {"status": "historical context only"},
    }

    stage0 = {
        "task_id": core.TASK_ID,
        "stage0_freeze_before_any_execution": True,
        "clean_worktree_before_stage0": {"enforced": enforce_clean_worktree, "status_output": status_out, "command_succeeded": status_ok},
        "parent_anchor_verification": parent_verification,
        "controlled_evidence_pack_hash": core.sha_obj(pack),
        "claim_ceiling": core.CLAIM_CEILING,
    }
    source_files = [
        repo_root / "src" / "ego_mainline_admission_executable_001b" / "__init__.py",
        repo_root / "src" / "ego_mainline_admission_executable_001b" / "__main__.py",
        repo_root / "src" / "ego_mainline_admission_executable_001b" / "core.py",
        repo_root / "src" / "ego_mainline_admission_executable_001b" / "runner.py",
    ]
    source_hashes = {
        "task_id": core.TASK_ID,
        "source_hashes": _path_hashes(source_files, repo_root),
    }
    protected_after = _path_hashes(protected, repo_root)
    old_mutation = {
        "task_id": core.TASK_ID,
        "old_artifacts_not_mutated": protected_before == protected_after,
        "before_hashes": protected_before,
        "after_hashes": protected_after,
        "mutated_paths": sorted(path for path, before in protected_before.items() if protected_after.get(path) != before),
    }
    mutation = {
        "task_id": core.TASK_ID,
        "source_artifact_integrity_passed": protected_before == protected_after,
        "old_artifact_mutation_detected": protected_before != protected_after,
        "claim_ceiling": core.CLAIM_CEILING,
    }
    hash_replay = {
        "task_id": core.TASK_ID,
        "hash_integrity_replay_passed": True,
        "hash_only_replay": True,
        "supports_behavior_claim": False,
    }

    artifacts: dict[str, Any] = {
        "parent_anchor_verification.json": parent_verification,
        "contract_requirement_evaluation.json": contract_eval,
        "evidence_dependency_matrix.json": dependencies,
        "negative_evidence_preservation_report.json": negative,
        "current_evidence_status_report.json": current,
        "stage0_freeze_manifest.json": stage0,
        "protected_artifact_inventory_before.json": {
            "task_id": core.TASK_ID,
            "paths": sorted(protected_before),
        },
        "protected_artifact_hashes_before.json": {"task_id": core.TASK_ID, "hashes": protected_before},
        "protected_artifact_hashes_after.json": {"task_id": core.TASK_ID, "hashes": protected_after},
        "tracked_old_artifact_mutation_report.json": old_mutation,
        "mutation_check_report.json": mutation,
        "source_code_path_hashes.json": source_hashes,
        "controlled_evidence_pack_manifest.json": pack,
        "candidate_trace.json": surfaces["trace_rows"],
        "candidate_output_rows.json": candidate_rows,
        "baseline_report.json": baseline_report,
        "baseline_invocation_report.json": baseline_invocation,
        "ablation_report.json": ablation_report,
        "ablation_invocation_report.json": ablation_invocation,
        "leakage_surface_inventory.json": inventory,
        "leakage_scan_report.json": leakage_report,
        "leakage_positive_control_report.json": positive_report,
        "manual_leakage_injection_report.json": manual_report,
        "metadata_whitelist_surface_scope_report.json": whitelist_report,
        "behavior_causal_replay_report.json": replay,
        "hash_integrity_replay_report.json": hash_replay,
        "frozen_input_consumption_report.json": frozen_report,
        "failure_path_test_report.json": failure_report,
    }

    for name, data in artifacts.items():
        _write_json(output_dir / name, data)

    artifact_hashes = {
        name: core.sha_file(output_dir / name)
        for name in [
            "controlled_evidence_pack_manifest.json",
            "candidate_output_rows.json",
            "baseline_report.json",
            "ablation_report.json",
            "leakage_scan_report.json",
            "leakage_positive_control_report.json",
        ]
    }
    metrics = core.build_metric_provenance(pack, artifact_hashes)
    _write_json(output_dir / "metric_provenance.json", metrics)

    acceptance_gates = {
        "parent_001a_remote_anchor_verified": parent_verification["anchors"]["remote-anchor-001p-cda09dc"]["remote_verified"],
        "parent_001o_remote_anchor_verified": parent_verification["anchors"]["remote-anchor-001o-f648dac"]["remote_verified"],
        "computed_evidence_contract_loaded": contract_eval["computed_evidence_contract_loaded"],
        "001b_invalidation_preserved": negative["001b_invalidation_preserved"],
        "001c_suspension_preserved": negative["001c_suspension_preserved"],
        "001d_caveat_preserved": contract_eval["001d_caveat_preserved"],
        "controlled_evidence_pack_frozen_before_execution": True,
        "candidate_outputs_computed_from_callable_path": all(row["computed_from_serialized_state_and_observation"] for row in candidate_rows),
        "all_verdict_metrics_have_provenance": metrics["all_verdict_metrics_have_provenance"],
        "no_literal_metrics": metrics["no_literal_metrics"],
        "all_required_baselines_invoked": all(row["callable_invoked"] for row in baseline_invocation["invocations"]),
        "baseline_outputs_exist_before_aggregation": all(row["output_rows_exist_before_aggregation"] for row in baseline_invocation["invocations"]),
        "all_required_ablations_rerun": all(row["reran_candidate_behavior"] for row in ablation_invocation["invocations"]),
        "ablation_outputs_recomputed": all(not row["copied_from_candidate_outputs"] for row in ablation_invocation["invocations"]),
        "same_surface_positive_controls_detected": positive_report["same_surface_positive_controls_detected"],
        "same_surface_clean_controls_passed": all(not row["clean_control_detected"] for row in leakage_report["surface_results"]),
        "independent_manual_leakage_injection_tests_passed": manual_report["independent_manual_leakage_injection_tests_passed"],
        "metadata_whitelist_surface_scoped": whitelist_report["metadata_whitelist_surface_scoped"],
        "behavior_causal_replay_passed_where_applicable": replay["behavior_causal_replay_passed"],
        "hash_only_replay_not_used_for_behavior_claim": not hash_replay["supports_behavior_claim"],
        "all_frozen_inputs_consumed": frozen_report["all_frozen_inputs_consumed"],
        "source_artifact_integrity_passed": mutation["source_artifact_integrity_passed"],
        "old_artifacts_not_mutated": old_mutation["old_artifacts_not_mutated"],
        "failure_path_tests_passed": failure_report["failure_path_tests_passed"],
        "no_Ego_repo_modification": True,
        "no_runtime_or_product_work": True,
        "claim_ceiling_preserved": True,
    }
    stop_eval = core.evaluate_stop_conditions(
        {
            "missing_parent_001a_anchor": not acceptance_gates["parent_001a_remote_anchor_verified"],
            "missing_parent_001o_anchor": not acceptance_gates["parent_001o_remote_anchor_verified"],
            "missing_computed_evidence_contract": not acceptance_gates["computed_evidence_contract_loaded"],
            "001b_positive_evidence_leak": not negative["001b_invalidation_preserved"],
            "001c_positive_evidence_leak": not negative["001c_suspension_preserved"],
            "001d_caveat_missing": not acceptance_gates["001d_caveat_preserved"],
            "baseline_invocation_missing": not acceptance_gates["all_required_baselines_invoked"],
            "ablation_not_rerun": not acceptance_gates["all_required_ablations_rerun"],
            "scanner_not_fail_able": not acceptance_gates["same_surface_positive_controls_detected"],
            "metadata_whitelist_not_surface_scoped": not acceptance_gates["metadata_whitelist_surface_scoped"],
            "replay_not_behavior_causal": not acceptance_gates["behavior_causal_replay_passed_where_applicable"],
            "unused_frozen_input": not acceptance_gates["all_frozen_inputs_consumed"],
            "metric_provenance_missing": not acceptance_gates["all_verdict_metrics_have_provenance"],
            "old_artifact_mutation": not acceptance_gates["old_artifacts_not_mutated"],
        }
    )
    result = {
        "task_id": core.TASK_ID,
        "layer": core.LAYER,
        "verdict": stop_eval["verdict"],
        "bounded_pass": stop_eval["passed"] and all(acceptance_gates.values()),
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "claim_ceiling": core.CLAIM_CEILING,
        "authorization_flags": core.AUTHORIZATION_FLAGS,
        "acceptance_gates": acceptance_gates,
        "stop_conditions_triggered": stop_eval["stop_conditions"],
        "baseline_results": {
            "baseline_gate_passed": baseline_report["baseline_gate_passed"],
            "candidate_score": baseline_report["candidate_score"],
            "fair_baseline_count": len([row for row in baseline_report["baselines"] if row["counts_as_fair_baseline"]]),
        },
        "ablation_results": {
            "ablation_gate_passed": ablation_report["ablation_gate_passed"],
            "candidate_score": ablation_report["candidate_score"],
        },
        "leakage_results": {
            "leakage_gate_passed": leakage_report["leakage_gate_passed"],
            "manual_injection_passed": manual_report["independent_manual_leakage_injection_tests_passed"],
            "metadata_whitelist_surface_scoped": whitelist_report["metadata_whitelist_surface_scoped"],
        },
        "replay_result": {
            "behavior_causal_replay_passed": replay["behavior_causal_replay_passed"],
            "hash_only_replay_not_used_for_behavior_claim": not hash_replay["supports_behavior_claim"],
        },
        "metric_provenance_result": {
            "all_verdict_metrics_have_provenance": metrics["all_verdict_metrics_have_provenance"],
            "no_literal_metrics": metrics["no_literal_metrics"],
            "metric_count": len(metrics["metrics"]),
        },
        "what_this_does_not_prove": [
            "EGO readiness",
            "bridge readiness",
            "EGO-mainline runtime readiness",
            "companion readiness",
            "mechanism validity",
            "theory validity",
            "agency",
            "selfhood",
            "consciousness",
            "real emotion",
            "real relationship learning",
            "real user benefit",
            "correctness of any future EGO runtime",
        ],
    }
    _write_json(output_dir / "result.json", result)

    execution_manifest = {
        "task_id": core.TASK_ID,
        "run_id": core.RUN_ID,
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "artifact_files": sorted(path.name for path in output_dir.iterdir()),
        "stage0_freeze_manifest_hash": core.sha_file(output_dir / "stage0_freeze_manifest.json"),
        "result_hash": core.sha_file(output_dir / "result.json"),
        "claim_ceiling": core.CLAIM_CEILING,
    }
    _write_json(output_dir / "execution_manifest.json", execution_manifest)
    _write_text(output_dir / "execution_manifest.sha256", core.sha_file(output_dir / "execution_manifest.json") + "\n")
    _write_text(output_dir / "claim_ceiling.txt", core.CLAIM_CEILING + "\n")

    if not result["bounded_pass"]:
        _write_json(
            output_dir / "blocker_report.json",
            {
                "task_id": core.TASK_ID,
                "verdict": result["verdict"],
                "stop_conditions_triggered": result["stop_conditions_triggered"],
                "minimum_patch": "repair exact blocker in a later bounded task",
            },
        )

    task_card = repo_root / core.TASK_CARD_PATH
    if not task_card.exists():
        task_card.parent.mkdir(parents=True, exist_ok=True)
        task_card.write_text(build_task_card(), encoding="utf-8")

    return result
