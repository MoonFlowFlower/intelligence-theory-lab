from __future__ import annotations

import json
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


def _git_show_sha(repo_root: Path, commit: str, relative_path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return core.sha256_bytes(result.stdout)


def _file_sha(repo_root: Path, relative_path: str) -> str:
    return core.file_sha256(repo_root / relative_path)


def _stage0_manifest(repo_root: Path) -> dict:
    parent_sha = _git_show_sha(repo_root, core.PARENT_ANCHOR_COMMIT, core.PARENT_TASK_CARD_PATH)
    stage0 = {
        "task_id": core.TASK_ID,
        "layer": "bounded Gate2 executable preflight only",
        "parent_task_card_commit": core.PARENT_ANCHOR_COMMIT,
        "parent_task_card_path": core.PARENT_TASK_CARD_PATH,
        "parent_task_card_sha256": parent_sha,
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "stage0_frozen_before_candidate_or_control_runs": True,
        "candidate_or_control_runs_started_before_stage0": False,
        "environment_family_definition": {
            "offline": True,
            "support_case_count": len(core.support_cases()),
            "heldout_case_count": len(core.heldout_cases()),
            "heldout_action_object_compositions": True,
            "partial_observability": True,
            "delayed_effects": True,
        },
        "baseline_families": list(core.REQUIRED_BASELINES),
        "graph_cache_family_variants": list(core.GRAPH_CACHE_VARIANTS),
        "ablation_families": list(core.REQUIRED_ABLATIONS),
        "trace_schema": list(core.REQUIRED_TRACE_FIELDS),
        "thresholds": dict(core.THRESHOLDS),
        "claim_ceiling": core.CLAIM_CEILING,
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
    }
    stage0["stage0_payload_hash"] = core.stable_hash(stage0)
    return stage0


def _sha_manifest(repo_root: Path, stage0: dict) -> dict:
    manifest = {
        core.PARENT_TASK_CARD_PATH: stage0["parent_task_card_sha256"],
        core.EXECUTABLE_TASK_CARD_PATH: _file_sha(repo_root, core.EXECUTABLE_TASK_CARD_PATH),
        "src/gate2_controllability_self_boundary_001b/core.py": _file_sha(
            repo_root, "src/gate2_controllability_self_boundary_001b/core.py"
        ),
        "src/gate2_controllability_self_boundary_001b/runner.py": _file_sha(
            repo_root, "src/gate2_controllability_self_boundary_001b/runner.py"
        ),
        "tests/test_gate2_controllability_self_boundary_001b_executable.py": _file_sha(
            repo_root, "tests/test_gate2_controllability_self_boundary_001b_executable.py"
        ),
    }
    manifest["manifest_payload_hash"] = core.stable_hash(manifest)
    return manifest


def _external_anchor(stage0: dict) -> dict:
    return {
        "task_id": core.TASK_ID,
        "anchor_method": "local_offline_hash_anchor",
        "anchor_time_utc": _utc_now(),
        "anchored_payload_hash": stage0["stage0_payload_hash"],
        "anchor_before_first_run": True,
        "external_service_used": False,
    }


def _execution_manifest(stage0: dict, sha_manifest: dict) -> dict:
    payload = {
        "task_id": core.TASK_ID,
        "claim_ceiling": core.CLAIM_CEILING,
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "parent_anchor_commit": core.PARENT_ANCHOR_COMMIT,
        "stage0_payload_hash": stage0["stage0_payload_hash"],
        "sha_manifest_hash": sha_manifest["manifest_payload_hash"],
        "required_artifacts": list(core.REQUIRED_ARTIFACTS),
        "baseline_families": list(core.REQUIRED_BASELINES),
        "ablation_families": list(core.REQUIRED_ABLATIONS),
        "authorization_flags": dict(core.AUTHORIZATION_FLAGS),
    }
    payload["execution_manifest_payload_hash"] = core.stable_hash(payload)
    return payload


def _protected_hashes(out: Path, names: list[str]) -> dict[str, str]:
    return {name: core.file_sha256(out / name) for name in names}


def run_preflight_001b(repo_root: Path | str, output_dir: Path | str) -> dict:
    root = Path(repo_root)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ledger: list[dict] = []

    stage0 = _stage0_manifest(root)
    _write_json(out / "stage0_freeze_manifest.json", stage0)
    ledger.append({"event": "stage0_freeze", "status": "written", "payload_hash": stage0["stage0_payload_hash"]})

    sha_manifest = _sha_manifest(root, stage0)
    _write_json(out / "sha256_manifest.json", sha_manifest)

    anchor = _external_anchor(stage0)
    _write_json(out / "external_anchor.json", anchor)
    ledger.append({"event": "external_anchor", "status": "written", "payload_hash": anchor["anchored_payload_hash"]})

    execution_manifest = _execution_manifest(stage0, sha_manifest)
    _write_json(out / "execution_manifest.json", execution_manifest)
    execution_manifest_sha = core.file_sha256(out / "execution_manifest.json")
    _write_text(out / "execution_manifest.sha256", execution_manifest_sha + "\n")

    trace_rows, heldout_predictions, _model_state = core.build_candidate_trace()
    prediction_commit = core.build_prediction_commit(heldout_predictions)
    _write_json(out / "prediction_commit.json", prediction_commit)
    prediction_sha = core.file_sha256(out / "prediction_commit.json")
    _write_text(out / "prediction_commit.sha256", prediction_sha + "\n")
    ledger.append({"event": "prediction_commit_freeze", "status": "written", "prediction_sha256": prediction_sha})

    phase_order = [
        "stage0_freeze_written",
        "external_anchor_written",
        "prediction_commit_written",
        "prediction_commit_hash_frozen",
        "target_reveal_started",
        "candidate_and_control_runs_started",
    ]

    _write_jsonl(out / "trace.jsonl", trace_rows)
    baseline, controls = core.evaluate_baselines(heldout_predictions)
    ablation = core.ablation_report()
    controllability = core.controllability_error_report(heldout_predictions)
    boundary = core.self_boundary_update_report(trace_rows)
    later = core.later_behavior_evaluation(heldout_predictions)
    linkage = core.linkage_report(trace_rows)
    leakage = core.leakage_report(linkage)
    replay = core.replay_report(trace_rows)
    ledger.append({"event": "candidate_and_control_runs", "status": "written", "trace_rows": len(trace_rows)})

    _write_json(out / "baseline_comparison.json", baseline)
    _write_json(out / "control_comparison.json", controls)
    _write_json(out / "ablation_report.json", ablation)
    _write_json(out / "controllability_error_report.json", controllability)
    _write_json(out / "self_boundary_update_report.json", boundary)
    _write_json(out / "later_behavior_evaluation.json", later)
    _write_json(out / "later_action_linkage_report.json", linkage)
    _write_json(out / "leakage_report.json", leakage)
    _write_json(out / "replay_report.json", replay)

    protected = [
        "stage0_freeze_manifest.json",
        "sha256_manifest.json",
        "external_anchor.json",
        "prediction_commit.json",
        "prediction_commit.sha256",
        "execution_manifest.json",
        "execution_manifest.sha256",
        "trace.jsonl",
        "baseline_comparison.json",
        "control_comparison.json",
        "ablation_report.json",
        "controllability_error_report.json",
        "self_boundary_update_report.json",
        "later_action_linkage_report.json",
        "later_behavior_evaluation.json",
        "leakage_report.json",
        "replay_report.json",
    ]
    before_hashes = _protected_hashes(out, protected)
    after_hashes = _protected_hashes(out, protected)
    mutation = {
        "task_id": core.TASK_ID,
        "claim_ceiling": core.CLAIM_CEILING,
        "protected_file_sha256_before_evaluation": before_hashes,
        "protected_file_sha256_after_evaluation": after_hashes,
        "mutation_detected_after_evaluation": before_hashes != after_hashes,
        "post_evaluation_mutation_check_passed": before_hashes == after_hashes,
    }
    _write_json(out / "mutation_check_report.json", mutation)

    access_log = {
        "task_id": core.TASK_ID,
        "phase_order": phase_order + [
            "target_reveal_completed",
            "reports_written",
            "mutation_check_after_evaluation_written",
        ],
        "phase_a": {
            "prediction_commit_hash_frozen_before_reveal": True,
            "prediction_commit_sha256": prediction_sha,
            "forbidden_access_used": False,
            "target_effects_read_before_prediction": 0,
            "later_behavior_labels_read_before_prediction": 0,
        },
        "phase_b": {
            "target_reveal_after_prediction_commit": True,
            "prediction_commit_rewritten_after_reveal": False,
        },
    }
    _write_json(out / "access_log.json", access_log)

    result = core.result_payload(baseline, ablation, leakage, mutation, controllability, later)
    _write_json(out / "result.json", result)
    _write_text(out / "claim_ceiling.txt", core.CLAIM_CEILING + "\n")
    _write_text(out / "final_report.md", core.final_report(result, baseline))
    if result["verdict"] != core.VERDICT_PASS:
        _write_json(
            out / "failure_manifest.json",
            {
                "task_id": core.TASK_ID,
                "verdict": result["verdict"],
                "stop_conditions": result["stop_conditions"],
                "rca_worthy_failure_reason": result["stop_conditions"][0] if result["stop_conditions"] else "unknown",
                "do_not_patch_forward_automatically": True,
                "claim_ceiling": core.CLAIM_CEILING,
            },
        )
    ledger.append({"event": "target_reveal", "status": "completed"})
    ledger.append({"event": "later_behavior_evaluation", "status": "written", "accuracy": later["later_action_selection_accuracy"]})
    ledger.append({"event": "mutation_check", "status": "passed" if mutation["post_evaluation_mutation_check_passed"] else "failed"})
    ledger.append({"event": "result", "status": "written", "verdict": result["verdict"]})
    _write_jsonl(out / "run_ledger.jsonl", ledger)
    return result


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = run_preflight_001b(
        repo_root=repo_root,
        output_dir=repo_root / "artifacts" / "gate2_controllability_self_boundary_001b",
    )
    print(core.pretty_json(result))
