from __future__ import annotations

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


def _file_sha(root: Path, relative_path: str) -> str:
    return core.file_sha256(root / relative_path)


def _stage0_freeze_manifest(repo_root: Path) -> dict:
    stage0 = {
        "task_id": core.TASK_ID,
        "layer": "bounded Gate3 viability / functional-affect executable preflight only",
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
        "shared_state_schema_id": core.STATE_SCHEMA_ID,
        "required_baselines": list(core.REQUIRED_BASELINES),
        "graph_cache_family_variants": list(core.GRAPH_CACHE_VARIANTS),
        "required_ablations": list(core.REQUIRED_ABLATIONS),
        "required_artifacts": list(core.REQUIRED_ARTIFACTS),
        "acceptance_threshold": core.ACCEPTANCE_THRESHOLD,
        "predeclared_viability_to_priority_link_required": True,
        "claim_ceiling": core.CLAIM_CEILING,
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
    }
    stage0["stage0_payload_hash"] = core.stable_hash(stage0)
    return stage0


def _execution_manifest(stage0: dict, freeze_manifest_hash: str, repo_root: Path) -> dict:
    source_paths = [
        core.EXECUTABLE_TASK_CARD_PATH,
        "src/gate3_viability_functional_affect_001b/__init__.py",
        "src/gate3_viability_functional_affect_001b/__main__.py",
        "src/gate3_viability_functional_affect_001b/core.py",
        "src/gate3_viability_functional_affect_001b/runner.py",
        "tests/test_gate3_viability_functional_affect_001b_executable.py",
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


def run_preflight_001b(
    repo_root: Path | str,
    output_dir: Path | str | None = None,
) -> dict:
    root = Path(repo_root)
    out = Path(output_dir) if output_dir is not None else root / core.ARTIFACT_DIR_REL
    out.mkdir(parents=True, exist_ok=True)
    ledger: list[dict] = []

    stage0 = _stage0_freeze_manifest(root)
    _write_json(out / "stage0_freeze_manifest.json", stage0)
    freeze_manifest_hash = core.file_sha256(out / "stage0_freeze_manifest.json")
    ledger.append(
        {
            "event": "stage0_freeze_manifest_written",
            "status": "written",
            "freeze_manifest_hash": freeze_manifest_hash,
        }
    )

    execution_manifest = _execution_manifest(stage0, freeze_manifest_hash, root)
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

    trace_rows, shared_rows, viability_rows, later_predictions = core.build_candidate_run()
    _write_jsonl(out / "trace.jsonl", trace_rows)
    _write_jsonl(out / "shared_state_trace.jsonl", shared_rows)
    _write_jsonl(out / "viability_state_trace.jsonl", viability_rows)
    ledger.append(
        {
            "event": "candidate_gate3_trace_written",
            "status": "written",
            "trace_rows": len(trace_rows),
            "shared_state_rows": len(shared_rows),
            "viability_state_rows": len(viability_rows),
        }
    )

    baseline = core.baseline_comparison()
    ablation = core.ablation_report()
    linkage = core.linkage_report(trace_rows)
    leakage = core.leakage_report(linkage)
    replay = core.replay_integrity_report(trace_rows, shared_rows, viability_rows)
    later_evaluation = core.evaluate_later_actions(later_predictions)

    _write_json(out / "linkage_report.json", linkage)
    _write_json(out / "baseline_comparison.json", baseline)
    _write_json(out / "ablation_report.json", ablation)
    _write_json(out / "leakage_report.json", leakage)
    _write_json(out / "replay_integrity_report.json", replay)
    _write_json(out / "later_action_evaluation.json", later_evaluation)
    ledger.append(
        {
            "event": "reports_written",
            "status": "written",
            "best_fair_baseline_score": baseline["best_fair_baseline"]["viability_to_later_action_score"],
            "ablation_gate_passed": ablation["ablation_gate_passed"],
            "leakage_gate_passed": leakage["leakage_gate_passed"],
        }
    )

    protected = [
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
    ]
    before_hashes = _protected_hashes(out, protected)
    after_hashes = _protected_hashes(out, protected)
    mutated = [
        name
        for name in protected
        if before_hashes.get(name) != after_hashes.get(name)
    ]
    mutation = {
        "task_id": core.TASK_ID,
        "claim_ceiling": core.CLAIM_CEILING,
        "protected_artifact_sha256_before_evaluation": before_hashes,
        "protected_artifact_sha256_after_evaluation": after_hashes,
        "mutation_detected_after_evaluation": bool(mutated),
        "mutated_artifacts": mutated,
        "post_evaluation_mutation_check_passed": not mutated,
    }
    _write_json(out / "mutation_check_report.json", mutation)

    result = core.result_payload(
        baseline=baseline,
        ablation=ablation,
        leakage=leakage,
        replay=replay,
        mutation=mutation,
        later_evaluation=later_evaluation,
    )
    _write_json(out / "result.json", result)
    _write_text(out / "claim_ceiling.txt", core.CLAIM_CEILING + "\n")
    if result["verdict"] != core.VERDICT_PASS:
        _write_json(out / "failure_manifest.json", _failure_manifest(result))

    ledger.append(
        {
            "event": "mutation_check_after_evaluation",
            "status": "passed" if mutation["post_evaluation_mutation_check_passed"] else "failed",
            "mutated_artifacts": mutated,
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


if __name__ == "__main__":
    main()
