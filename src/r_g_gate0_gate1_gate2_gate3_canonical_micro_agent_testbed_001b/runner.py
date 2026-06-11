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
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, data: object) -> None:
    path.write_text(core.pretty_json(data) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(core.stable_json(row) for row in rows) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _file_sha(root: Path, relative_path: str) -> str:
    return core.file_sha256(root / relative_path)


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
        path: _file_sha(repo_root, path)
        for path in inventory["tracked_old_artifact_paths"]
        if (repo_root / path).exists()
    }


def _stage0_manifest(repo_root: Path) -> dict:
    stage0 = {
        "task_id": core.TASK_ID,
        "layer": "bounded Gate0/Gate1/Gate2/Gate3 canonical micro-agent integration executable preflight only",
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "created_utc": _utc_now(),
        "stage0_frozen_before_candidate_or_control_runs": True,
        "candidate_or_control_runs_started_before_stage0": False,
        "parent_anchors": dict(core.PARENT_ANCHORS),
        "parent_task_card_path": core.PARENT_TASK_CARD_PATH,
        "parent_task_card_sha256": _file_sha(repo_root, core.PARENT_TASK_CARD_PATH),
        "executable_task_card_path": core.EXECUTABLE_TASK_CARD_PATH,
        "executable_task_card_sha256": _file_sha(repo_root, core.EXECUTABLE_TASK_CARD_PATH),
        "required_loop": list(core.REQUIRED_LOOP),
        "required_shared_state_fields": list(core.REQUIRED_SHARED_STATE_FIELDS),
        "required_baselines": list(core.REQUIRED_BASELINES),
        "graph_cache_family_variants": list(core.GRAPH_CACHE_VARIANTS),
        "required_ablations": list(core.REQUIRED_ABLATIONS),
        "required_artifacts": list(core.REQUIRED_ARTIFACTS),
        "single_canonical_shared_state_required": True,
        "old_artifact_mutation_is_failure": True,
        "claim_ceiling": core.CLAIM_CEILING,
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
    }
    stage0["stage0_payload_hash"] = core.stable_hash(stage0)
    return stage0


def _execution_manifest(stage0: dict, freeze_manifest_hash: str, repo_root: Path) -> dict:
    source_paths = [
        core.EXECUTABLE_TASK_CARD_PATH,
        "src/r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b/__init__.py",
        "src/r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b/__main__.py",
        "src/r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b/core.py",
        "src/r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b/runner.py",
        "tests/test_r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b_executable.py",
    ]
    source_hashes = {
        path: _file_sha(repo_root, path)
        for path in source_paths
        if (repo_root / path).exists()
    }
    manifest = {
        "task_id": core.TASK_ID,
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "claim_ceiling": core.CLAIM_CEILING,
        "freeze_manifest_hash": freeze_manifest_hash,
        "stage0_payload_hash": stage0["stage0_payload_hash"],
        "parent_anchors": dict(core.PARENT_ANCHORS),
        "shared_state_schema_id": core.STATE_SCHEMA_ID,
        "required_loop": list(core.REQUIRED_LOOP),
        "required_shared_state_fields": list(core.REQUIRED_SHARED_STATE_FIELDS),
        "required_artifacts": list(core.REQUIRED_ARTIFACTS),
        "source_hashes": source_hashes,
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
    }
    manifest["execution_manifest_payload_hash"] = core.stable_hash(manifest)
    return manifest


def _protected_hashes(output_dir: Path, names: list[str]) -> dict[str, str]:
    return {name: core.file_sha256(output_dir / name) for name in names}


def _old_artifact_mutation_report(repo_root: Path, before_hashes: dict[str, str], after_hashes: dict[str, str]) -> dict:
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
        "do_not_start_gate4": True,
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
    ledger.append({"event": "protected_old_artifact_hashes_before", "status": "written", "count": len(old_hashes_before)})

    stage0 = _stage0_manifest(root)
    _write_json(out / "stage0_freeze_manifest.json", stage0)
    freeze_hash = core.file_sha256(out / "stage0_freeze_manifest.json")
    ledger.append({"event": "stage0_freeze_manifest_written", "status": "written", "freeze_manifest_hash": freeze_hash})

    execution_manifest = _execution_manifest(stage0, freeze_hash, root)
    _write_json(out / "execution_manifest.json", execution_manifest)
    execution_manifest_hash = core.file_sha256(out / "execution_manifest.json")
    _write_text(out / "execution_manifest.sha256", execution_manifest_hash + "\n")
    ledger.append({"event": "execution_manifest_frozen", "status": "written", "execution_manifest_sha256": execution_manifest_hash})

    trace_rows, shared_rows, viability_rows, later_predictions = core.build_candidate_run()
    _write_jsonl(out / "trace.jsonl", trace_rows)
    _write_jsonl(out / "shared_state_trace.jsonl", shared_rows)
    _write_jsonl(out / "viability_state_trace.jsonl", viability_rows)
    ledger.append({"event": "candidate_integrated_trace_written", "status": "written", "trace_rows": len(trace_rows)})

    baseline = core.baseline_comparison()
    ablation = core.ablation_report()
    linkage = core.linkage_report(trace_rows)
    leakage = core.leakage_report(linkage)
    replay = core.replay_integrity_report(trace_rows, shared_rows, viability_rows)
    later_eval = core.evaluate_later_actions(later_predictions)
    _write_json(out / "baseline_comparison.json", baseline)
    _write_json(out / "ablation_report.json", ablation)
    _write_json(out / "linkage_report.json", linkage)
    _write_json(out / "leakage_report.json", leakage)
    _write_json(out / "replay_integrity_report.json", replay)
    _write_json(out / "later_action_evaluation.json", later_eval)

    protected_new = [
        "stage0_freeze_manifest.json",
        "execution_manifest.json",
        "execution_manifest.sha256",
        "trace.jsonl",
        "shared_state_trace.jsonl",
        "viability_state_trace.jsonl",
        "linkage_report.json",
        "baseline_comparison.json",
        "ablation_report.json",
        "leakage_report.json",
        "replay_integrity_report.json",
        "later_action_evaluation.json",
        "protected_artifact_inventory_before.json",
        "protected_artifact_hashes_before.json",
    ]
    before_new_hashes = _protected_hashes(out, protected_new)
    old_hashes_after = _hash_inventory(root, inventory)
    _write_json(out / "protected_artifact_hashes_after.json", old_hashes_after)
    old_mutation = _old_artifact_mutation_report(root, old_hashes_before, old_hashes_after)
    _write_json(out / "tracked_old_artifact_mutation_report.json", old_mutation)
    protected_new.extend(["protected_artifact_hashes_after.json", "tracked_old_artifact_mutation_report.json"])
    after_new_hashes = _protected_hashes(out, protected_new)
    mutated_new = [
        name
        for name, before_hash in before_new_hashes.items()
        if after_new_hashes.get(name) != before_hash
    ]
    mutation = {
        "task_id": core.TASK_ID,
        "claim_ceiling": core.CLAIM_CEILING,
        "protected_artifact_sha256_before_evaluation": before_new_hashes,
        "protected_artifact_sha256_after_evaluation": after_new_hashes,
        "mutation_detected_after_evaluation": bool(mutated_new),
        "mutated_artifacts": sorted(mutated_new),
        "post_evaluation_mutation_check_passed": not mutated_new,
    }
    _write_json(out / "mutation_check_report.json", mutation)

    result = core.result_payload(baseline, ablation, leakage, replay, mutation, old_mutation, later_eval)
    _write_json(out / "result.json", result)
    _write_text(out / "claim_ceiling.txt", core.CLAIM_CEILING + "\n")
    if result["verdict"] != core.VERDICT_PASS:
        _write_json(out / "failure_manifest.json", _failure_manifest(result))

    ledger.append({"event": "old_artifact_hermeticity_check", "status": "passed" if not old_mutation["old_artifact_mutation_detected"] else "failed"})
    ledger.append({"event": "result_written", "status": "written", "verdict": result["verdict"], "bounded_pass": result["bounded_pass"]})
    _write_jsonl(out / "run_ledger.jsonl", ledger)
    return result


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = run_preflight_001b(repo_root=repo_root)
    print(core.pretty_json(result))


if __name__ == "__main__":
    main()
