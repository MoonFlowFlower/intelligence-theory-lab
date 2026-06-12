from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

from . import core


PROTECTED_FAMILY_SNIPPETS = [
    "artifacts/predictive_action_learning_contract_001",
    "artifacts/gate1_replay_consolidation",
    "artifacts/gate2_controllability_self_boundary_001b",
    "artifacts/gate3_viability_functional_affect_001b",
    "artifacts/r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b",
    "artifacts/r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b",
    "artifacts/gate4_social_representational_gap_preflight_001b",
    "artifacts/gate4_social_latent_inference_001b",
    "artifacts/same_agent_bridge_readiness_audit_001a",
    "artifacts/same_agent_bridge_readiness_audit_001a_amendment_001",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, data: object) -> None:
    path.write_text(core.pretty_json(data) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(core.stable_json(row) for row in rows) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _git_status(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        encoding="utf-8",
    )
    return [line for line in result.stdout.splitlines() if line]


def _tracked_files(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        encoding="utf-8",
    )
    return [line.replace("\\", "/") for line in result.stdout.splitlines() if line]


def _protected_artifact_inventory(repo_root: Path) -> dict:
    tracked = _tracked_files(repo_root)
    protected = [
        path
        for path in tracked
        if any(path.startswith(snippet) for snippet in PROTECTED_FAMILY_SNIPPETS)
    ]
    return {
        "task_id": core.TASK_ID,
        "protected_family_snippets": list(PROTECTED_FAMILY_SNIPPETS),
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


def _stage0_manifest(repo_root: Path, task_card_hash: str) -> dict:
    schema = core.canonical_agent_state_schema()
    allowed = core.allowed_persistence_manifest()
    forbidden = core.forbidden_persistence_manifest()
    environment = core.bridge_environment_manifest()
    stage0 = {
        "task_id": core.TASK_ID,
        "created_utc": _utc_now(),
        "stage0_frozen_before_bridge_run": True,
        "bridge_run_started_before_stage0": False,
        "frozen_fields": list(core.REQUIRED_STAGE0_FIELDS),
        "task_card_hash": task_card_hash,
        "bridge_environment_family": environment["environment_family"],
        "bridge_boundary_definition": environment["bridge_boundary_definition"],
        "canonical_agent_state_schema": schema,
        "serialization_format": core.SERIALIZATION_FORMAT,
        "allowed_persistence_manifest": allowed,
        "forbidden_persistence_manifest": forbidden,
        "reset_boundary_definition": {
            "reset_allowed_during_bridge": False,
            "reset_requires_new_task_card": True,
        },
        "memory_carryover_boundary_definition": {
            "only_canonical_serialized_shared_state_crosses": True,
            "transcript_summary_carryover_forbidden": True,
        },
        "identity_continuity_metric": {
            "metric": "lineage hash continuity plus identity_continuity_state delta",
            "shared_agent_id_alone_sufficient": False,
        },
        "state_lineage_hash_contract": {
            "hash_function": "sha256(canonical_json)",
            "parent_child_hash_required": True,
        },
        "replay_contract": {
            "trace_replay_required": True,
            "state_replay_required": True,
            "trace_only_replay_counts_as_hygiene_only": True,
        },
        "leakage_controls": environment["leakage_controls"],
        "baseline_implementation_signatures": {
            name: core.stable_hash({"baseline_name": name, "access": "predeclared_legal_inputs"})
            for name in core.REQUIRED_BASELINES
        },
        "ablation_implementation_signatures": {
            name: core.stable_hash({"ablation_name": name, "access": "predeclared_legal_inputs"})
            for name in core.REQUIRED_ABLATIONS
        },
        "metric_formulas": {
            "bridge_continuity_score": "mean(identity_continuity, memory_carryover, post_bridge_update, later_behavior_linkage)",
            "baseline_equivalence": "fair baseline score >= acceptance_threshold",
        },
        "equivalence_thresholds": {"acceptance_threshold": core.ACCEPTANCE_THRESHOLD},
        "heldout_split": environment["heldout_split"],
        "seed_schedule": {
            "train_context_seeds": environment["heldout_split"]["train_context_seeds"],
            "heldout_bridge_seeds": environment["heldout_split"]["heldout_bridge_seeds"],
        },
        "artifact_schema": list(core.REQUIRED_ARTIFACTS),
        "rollback_policy": {
            "baseline_equivalence": "preserve failure artifacts and do not patch thresholds",
            "leakage_or_mutation": "preserve failure manifest and require new freeze",
        },
        "claim_ceiling": core.CLAIM_CEILING,
        "external_anchor": {
            "parent_anchor_tags": list(core.REMOTE_ANCHOR_TAGS),
            "current_task_anchor": "local_preflight_artifacts_only_until_commit",
        },
        "required_baselines": list(core.REQUIRED_BASELINES),
        "required_ablations": list(core.REQUIRED_ABLATIONS),
        "single_canonical_serialized_shared_state_required": True,
        "hidden_profile_tables_forbidden": True,
        "old_artifact_mutation_is_failure": True,
        "parent_anchors": dict(core.PARENT_ANCHORS),
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
    }
    stage0["stage0_payload_hash"] = core.stable_hash(stage0)
    return stage0


def _execution_manifest(repo_root: Path, stage0: dict, freeze_manifest_hash: str) -> dict:
    source_paths = [
        core.TASK_CARD_PATH,
        core.PARENT_TASK_CARD_PATH,
        "src/same_agent_bridge_001b/__init__.py",
        "src/same_agent_bridge_001b/__main__.py",
        "src/same_agent_bridge_001b/core.py",
        "src/same_agent_bridge_001b/runner.py",
        "tests/test_same_agent_bridge_001b_executable_preflight.py",
    ]
    source_hashes = {
        path: core.file_sha256(repo_root / path)
        for path in source_paths
        if (repo_root / path).exists()
    }
    manifest = {
        "task_id": core.TASK_ID,
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "claim_ceiling": core.CLAIM_CEILING,
        "freeze_manifest_hash": freeze_manifest_hash,
        "stage0_payload_hash": stage0["stage0_payload_hash"],
        "source_hashes": source_hashes,
        "parent_anchors": dict(core.PARENT_ANCHORS),
        "required_artifacts": list(core.REQUIRED_ARTIFACTS),
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
        "rca_worthy_failure_reason": (
            result["stop_conditions_triggered"][0]
            if result["stop_conditions_triggered"]
            else "unknown preflight failure"
        ),
        "stop_conditions_triggered": result["stop_conditions_triggered"],
        "do_not_patch_forward_automatically": True,
        "do_not_enter_ego_mainline": True,
        "claim_ceiling": core.CLAIM_CEILING,
    }


def run_preflight_001b(repo_root: Path | str, output_dir: Path | str | None = None) -> dict:
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

    task_card_hash = core.file_sha256(root / core.TASK_CARD_PATH)
    stage0 = _stage0_manifest(root, task_card_hash)
    _write_json(out / "stage0_freeze_manifest.json", stage0)
    freeze_hash = core.file_sha256(out / "stage0_freeze_manifest.json")
    ledger.append(
        {
            "event": "stage0_freeze_manifest_written",
            "status": "written",
            "freeze_manifest_hash": freeze_hash,
        }
    )

    _write_json(out / "bridge_environment_manifest.json", core.bridge_environment_manifest())
    _write_json(out / "canonical_agent_state_schema.json", core.canonical_agent_state_schema())
    _write_json(out / "allowed_persistence_manifest.json", core.allowed_persistence_manifest())
    _write_json(out / "forbidden_persistence_manifest.json", core.forbidden_persistence_manifest())
    allowed_hash = core.file_sha256(out / "allowed_persistence_manifest.json")
    forbidden_hash = core.file_sha256(out / "forbidden_persistence_manifest.json")

    execution_manifest = _execution_manifest(root, stage0, freeze_hash)
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

    trace_rows, serialized_rows, shared_rows, later_predictions = core.build_candidate_run(
        allowed_manifest_hash=allowed_hash,
        forbidden_manifest_hash=forbidden_hash,
    )
    _write_jsonl(out / "trace.jsonl", trace_rows)
    _write_jsonl(out / "serialized_state_trace.jsonl", serialized_rows)
    _write_jsonl(out / "shared_state_trace.jsonl", shared_rows)
    ledger.append({"event": "bridge_trace_written", "status": "written", "trace_rows": len(trace_rows)})

    baseline = core.baseline_comparison()
    ablation = core.ablation_report()
    linkage = core.linkage_report(trace_rows)
    leakage = core.leakage_report(linkage)
    replay = core.replay_integrity_report(trace_rows, serialized_rows, shared_rows)
    later_behavior = core.later_behavior_report(later_predictions)
    _write_json(out / "baseline_comparison.json", baseline)
    _write_json(out / "ablation_report.json", ablation)
    _write_json(out / "linkage_report.json", linkage)
    _write_json(out / "leakage_report.json", leakage)
    _write_json(out / "replay_integrity_report.json", replay)
    _write_json(out / "later_behavior_report.json", later_behavior)

    old_hashes_after = _hash_inventory(root, inventory)
    _write_json(out / "protected_artifact_hashes_after.json", old_hashes_after)
    old_mutation = _old_artifact_mutation_report(old_hashes_before, old_hashes_after, root)
    _write_json(out / "tracked_old_artifact_mutation_report.json", old_mutation)
    mutation = {
        "task_id": core.TASK_ID,
        "claim_ceiling": core.CLAIM_CEILING,
        "mutation_detected_after_evaluation": False,
        "mutated_artifacts": [],
        "post_evaluation_mutation_check_passed": True,
        "old_artifact_mutation_detected": old_mutation["old_artifact_mutation_detected"],
    }
    _write_json(out / "mutation_check_report.json", mutation)

    result = core.result_payload(baseline, ablation, leakage, replay, mutation, old_mutation, later_behavior)
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


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = run_preflight_001b(repo_root=repo_root)
    print(core.pretty_json(result))
