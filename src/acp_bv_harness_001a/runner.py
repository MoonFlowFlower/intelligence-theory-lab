from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Any, Callable

from . import (
    CLAIM_CEILING,
    CLAUDE_TARGETED_REAUDIT_VERDICT,
    CURRENT_LAYER,
    START_COMMIT,
    START_TAG,
    TASK_ID,
)
from . import ablations, baselines, boundary, controls, difficulty, environment, leakage, replay, scoring, source_pins
from .common import git_readback, relpath, stable_run_command, write_json


def load_bearing_callable_registry() -> dict[str, Callable[..., Any]]:
    return {
        "scorer": scoring.score_prediction_rows,
        "environment_generator": environment.generate_episodes,
        "held_out_truth_generator": environment.held_out_truth_generator,
        "counterfactual_truth_generator": environment.counterfactual_truth_generator,
        "leakage_scanner": leakage.scan_candidate_bundle_for_leakage,
        "graph_cache_challengers": baselines.graph_cache_transition_table,
        "replay_recomputation": replay.recompute_replay_from_state_observation,
        "ablation_runner": ablations.run_ablation_reruns,
        "baseline_runner": baselines.run_baseline_matrix,
        "metric_aggregator": scoring.metric_aggregator,
        "difficulty_source": difficulty.difficulty_source,
        "difficulty_normalizer": difficulty.difficulty_normalizer,
        "boundary_verifier": boundary.verify_callable_source_boundary,
    }


def _prepare_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        for child in output_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)


def _boundary_report(
    *,
    repo_root: Path,
    output_dir: Path,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    checks = boundary.verify_many(
        load_bearing_callable_registry(),
        repo_root=repo_root,
        candidate_writable_roots=[output_dir / "candidate_controls"],
        candidate_artifact_roots=[output_dir / "candidate_controls"],
        expected_hashes=source_pins.expected_hashes_by_role(manifest),
    )
    return {
        "producer_function": "_boundary_report",
        "boundary_verdict": "all_load_bearing_callables_boundary_verified"
        if checks["all_passed"]
        else "blocked_by_unverified_difficulty_source",
        "checks": checks["checks"],
        "difficulty_source_boundary_verified": checks["checks"]["difficulty_source"]["boundary_verdict"] == "source_boundary_pass",
        "difficulty_normalizer_boundary_verified": checks["checks"]["difficulty_normalizer"]["boundary_verdict"] == "source_boundary_pass",
        "self_declared_ownership_accepted": False,
    }


def run_harness(
    *,
    repo_root: Path,
    output_dir: Path,
    run_id: str = "acp-bv-executable-harness-001a",
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    _prepare_output_dir(output_dir)

    manifest = source_pins.create_source_pin_manifest(
        repo_root=repo_root,
        run_id=run_id,
        output_path=output_dir / "source_pins.json",
        load_bearing_callables=load_bearing_callable_registry(),
    )
    manifest_check = source_pins.verify_source_pin_manifest(manifest, repo_root=repo_root)
    manifest["manifest_verification_at_scoring"] = manifest_check
    write_json(output_dir / "source_pins.json", manifest)

    clean_bundle = environment.build_clean_candidate_bundle()
    score_result = scoring.score_candidate_bundle(
        clean_bundle,
        repo_root=repo_root,
        output_artifact_path=output_dir / "result.json",
        run_id=f"{run_id}-candidate-score",
        source_pin_manifest=manifest,
        candidate_writable_roots=[output_dir / "candidate_controls"],
        candidate_artifact_roots=[output_dir / "candidate_controls"],
    )
    if score_result.get("blocked"):
        verdict = score_result["block_reason"]
        candidate_score = 0.0
    else:
        verdict = "acp_bv_executable_harness_001a_implemented_with_fail_able_controls"
        candidate_score = score_result["score"]

    boundary_report = _boundary_report(repo_root=repo_root, output_dir=output_dir, manifest=manifest)
    boundary_negative_controls = controls.run_boundary_negative_controls(
        repo_root=repo_root,
        output_dir=output_dir,
        source_pin_manifest=manifest,
        run_id=f"{run_id}-boundary",
    )
    clean_dirty_lookup_controls = controls.run_clean_dirty_lookup_controls(
        repo_root=repo_root,
        output_dir=output_dir,
        run_id=f"{run_id}-clean-dirty-lookup",
    )
    counterfactual_controls = controls.run_counterfactual_controls(
        repo_root=repo_root,
        output_dir=output_dir,
        run_id=f"{run_id}-counterfactual",
    )
    leakage_report = leakage.run_leakage_controls(
        clean_bundle,
        repo_root=repo_root,
        output_artifact_path=output_dir / "leakage_report.json",
        run_id=f"{run_id}-leakage",
    )
    baseline_matrix = baselines.run_baseline_matrix(
        repo_root=repo_root,
        output_artifact_path=output_dir / "baseline_matrix.json",
        run_id=f"{run_id}-baseline",
        candidate_score=candidate_score,
    )
    ablation_report = ablations.run_ablation_reruns(
        clean_bundle,
        repo_root=repo_root,
        output_dir=output_dir,
        output_artifact_path=output_dir / "ablation_report.json",
        run_id=f"{run_id}-ablation",
        before_metric=candidate_score,
    )
    replay_report = replay.recompute_replay_from_state_observation(
        clean_bundle,
        repo_root=repo_root,
        output_artifact_path=output_dir / "replay_report.json",
        run_id=f"{run_id}-replay",
    )

    claim_scan = controls.scan_claim_ceiling_and_forbidden_claims(
        [
            {"claim_ceiling": CLAIM_CEILING},
            baseline_matrix,
            ablation_report,
            replay_report,
            leakage_report,
            boundary_negative_controls,
        ]
    )
    all_acceptance = all(
        [
            verdict == "acp_bv_executable_harness_001a_implemented_with_fail_able_controls",
            manifest_check["passed"],
            boundary_report["boundary_verdict"] == "all_load_bearing_callables_boundary_verified",
            boundary_negative_controls["all_required_controls_passed"],
            leakage_report["all_controls_passed"],
            clean_dirty_lookup_controls["clean_control"]["verdict"] == "clean_control_passed",
            clean_dirty_lookup_controls["dirty_control"]["verdict"] == "dirty_control_blocked",
            counterfactual_controls["harness_selected_counterfactual_action_queries"],
            baseline_matrix["strongest_baseline_comparison"]["classification"] == "mechanism_relevant_effect_candidate",
            ablation_report["all_rerun"],
            replay_report["verdict"] == "replay_recomputed",
            replay_report["hash_only_positive_control"]["verdict"] == "blocked_by_replay_hash_only",
            claim_scan["claim_ceiling_passed"],
            claim_scan["forbidden_claim_scan_passed"],
        ]
    )
    if not all_acceptance and verdict == "acp_bv_executable_harness_001a_implemented_with_fail_able_controls":
        verdict = "blocked_by_test_failure"

    result = {
        "task_id": TASK_ID,
        "verdict": verdict,
        "acceptance_gate_passed": all_acceptance,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": "none",
        "enabled_status": "local offline CLI/test runner only",
        "real_trigger_evidence": {
            "start_commit": START_COMMIT,
            "start_tag": START_TAG,
            "prior_codex_verdict": "acp_bv_harness_card_r1_revision_ready_for_independent_reaudit",
            "claude_targeted_reaudit_verdict": CLAUDE_TARGETED_REAUDIT_VERDICT,
        },
        "real_gate_target_applied": False,
        "safe_to_apply_to_real_gate_target": False,
        "safe_to_wire_mainline": False,
        "candidate_score": candidate_score,
        "baseline_result": baseline_matrix["strongest_baseline_comparison"],
        "ablation_result": {"all_rerun": ablation_report["all_rerun"]},
        "replay_result": {"hash_only_rejected": True, "behavior_recomputed": replay_report["behavior_recomputed"]},
        "leakage_result": {"dirty_detected": leakage_report["all_controls_passed"]},
        "boundary_negative_control_result": {
            "all_required_controls_passed": boundary_negative_controls["all_required_controls_passed"]
        },
        "runtime_mutation_control_result": next(
            control
            for control in boundary_negative_controls["controls"]
            if control["control_id"] == "same_process_monkeypatch_rejected_or_ineffective"
        ),
        "claim_scan": claim_scan,
        "claim_ceiling": CLAIM_CEILING,
        "what_this_does_not_prove": claim_scan["what_this_does_not_prove"],
        "next_minimal_closed_loop_action": (
            "Send the implementation result and artifacts to Claude for independent hostile "
            "implementation audit before any real Gate target use."
        ),
    }
    readback = {
        "task_id": TASK_ID,
        "verdict": verdict,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": "none",
        "enabled_status": "local offline CLI/test runner only",
        "real_trigger_evidence": result["real_trigger_evidence"],
        "current_git_readback": git_readback(repo_root),
        "artifact_dir": relpath(output_dir, repo_root),
        "claim_ceiling": CLAIM_CEILING,
        "what_this_does_not_prove": result["what_this_does_not_prove"],
    }
    run_manifest = {
        "task_id": TASK_ID,
        "run_id": run_id,
        "command": stable_run_command("acp_bv_harness_001a.runner", output_dir, run_id),
        "artifact_dir": relpath(output_dir, repo_root),
        "required_artifacts": [
            "result.json",
            "source_pins.json",
            "boundary_report.json",
            "boundary_negative_controls.json",
            "leakage_report.json",
            "baseline_matrix.json",
            "ablation_report.json",
            "replay_report.json",
            "counterfactual_controls.json",
            "clean_dirty_lookup_controls.json",
            "run_manifest.json",
            "readback.json",
            "claim_ceiling.txt",
        ],
        "auto_remote_anchor": {
            "decision": "conditional",
            "performed_by_runner": False,
        },
        "no_mainline_target": True,
        "claim_ceiling": CLAIM_CEILING,
    }

    write_json(output_dir / "boundary_report.json", boundary_report)
    write_json(output_dir / "boundary_negative_controls.json", boundary_negative_controls)
    write_json(output_dir / "leakage_report.json", leakage_report)
    write_json(output_dir / "baseline_matrix.json", baseline_matrix)
    write_json(output_dir / "ablation_report.json", ablation_report)
    write_json(output_dir / "replay_report.json", replay_report)
    write_json(output_dir / "counterfactual_controls.json", counterfactual_controls)
    write_json(output_dir / "clean_dirty_lookup_controls.json", clean_dirty_lookup_controls)
    write_json(output_dir / "run_manifest.json", run_manifest)
    write_json(output_dir / "readback.json", readback)
    write_json(output_dir / "result.json", result)
    (output_dir / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/acp_bv_executable_harness_001a")
    parser.add_argument("--run-id", default="acp-bv-executable-harness-001a")
    args = parser.parse_args()
    result = run_harness(repo_root=Path.cwd(), output_dir=Path(args.output_dir), run_id=args.run_id)
    print(result["verdict"])
    return 0 if result["acceptance_gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
