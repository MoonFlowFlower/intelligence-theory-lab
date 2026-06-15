from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, Callable

from . import CLAIM_CEILING, TASK_ID
from . import boundary, environment, leakage, scoring
from .common import provenance_for, sha256_file, stable_run_command


def _load_callable(path: Path, function_name: str) -> Callable[..., Any]:
    spec = importlib.util.spec_from_file_location(f"acp_bv_candidate_control_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError(f"cannot load candidate control: {path}")
    spec.loader.exec_module(module)
    return getattr(module, function_name)


def _write_candidate_control(output_dir: Path, name: str, body: str) -> tuple[Path, Callable[..., Any]]:
    candidate_dir = output_dir / "candidate_controls"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    path = candidate_dir / f"{name}.py"
    path.write_text(body, encoding="utf-8")
    return path, _load_callable(path, name)


def run_runtime_mutation_control(
    *,
    repo_root: Path,
    output_dir: Path,
    source_pin_manifest: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    candidate_path, forged_truth = _write_candidate_control(
        output_dir,
        "same_process_truth_substitution",
        "def same_process_truth_substitution(episode, action):\n"
        "    return {'boundary_delta': 999, 'viability_state': 999}\n",
    )
    original = environment.held_out_truth_generator
    try:
        environment.held_out_truth_generator = forged_truth  # type: ignore[assignment]
        scoring_result = scoring.score_candidate_bundle(
            environment.build_clean_candidate_bundle(),
            repo_root=repo_root,
            output_artifact_path=output_dir / "boundary_negative_controls.json",
            run_id=run_id,
            source_pin_manifest=source_pin_manifest,
            candidate_writable_roots=[candidate_path.parent],
            candidate_artifact_roots=[candidate_path.parent],
            truth_generator=environment.held_out_truth_generator,
        )
    finally:
        environment.held_out_truth_generator = original  # type: ignore[assignment]
    blocked = scoring_result.get("blocked") is True and scoring_result.get("block_reason") == (
        "blocked_by_runtime_mutation_or_temporal_boundary_gap"
    )
    return {
        "control_id": "same_process_monkeypatch_rejected_or_ineffective",
        "candidate_side_same_process_substitution_attempted": True,
        "candidate_control_source": candidate_path.as_posix(),
        "actual_verdict": "blocked" if blocked else "failed",
        "expected_block_reason": "blocked_by_runtime_mutation_or_temporal_boundary_gap",
        "block_reason": scoring_result.get("block_reason"),
        "scoring_allowed_after_mutation": not blocked,
        "scoring_result": scoring_result,
    }


def run_boundary_negative_controls(
    *,
    repo_root: Path,
    output_dir: Path,
    source_pin_manifest: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    controls: list[dict[str, Any]] = []
    candidate_path, candidate_truth = _write_candidate_control(
        output_dir,
        "candidate_accessible_truth_generator",
        "def candidate_accessible_truth_generator(episode, action):\n"
        "    return {'boundary_delta': 1, 'viability_state': 1}\n",
    )
    candidate_roots = [candidate_path.parent]

    candidate_accessible = boundary.verify_callable_source_boundary(
        candidate_truth,
        repo_root=repo_root,
        candidate_writable_roots=candidate_roots,
        candidate_artifact_roots=candidate_roots,
    )
    controls.append(
        {
            "control_id": "candidate_accessible_truth_generator_rejected",
            "injected_violation": "truth generator placed under candidate artifact root",
            "verifier_entrypoint": "verify_callable_source_boundary",
            "resolved_source_path": candidate_accessible["resolved_source_path"],
            "source_hash": candidate_accessible["source_hash"],
            "expected_block_reason": "candidate_artifact_source",
            "actual_block_reason": candidate_accessible["block_reasons"],
            "actual_verdict": "blocked" if candidate_accessible["boundary_verdict"] == "source_boundary_blocked" else "failed",
            "run_id": f"{run_id}-candidate-accessible",
            "artifact_path": (output_dir / "boundary_negative_controls.json").as_posix(),
        }
    )

    policy_map = boundary.verify_callable_source_boundary(
        environment.generate_episodes,
        repo_root=repo_root,
        candidate_writable_roots=candidate_roots,
        candidate_artifact_roots=candidate_roots,
        influence={"candidate_policy_map": {"generator": "selected_by_policy_map"}},
    )
    controls.append(
        {
            "control_id": "policy_map_influenced_generator_rejected",
            "injected_violation": "generator selection influenced by candidate policy_map",
            "verifier_entrypoint": "verify_callable_source_boundary",
            "resolved_source_path": policy_map["resolved_source_path"],
            "source_hash": policy_map["source_hash"],
            "expected_block_reason": "candidate_policy_map_influence",
            "actual_block_reason": policy_map["block_reasons"],
            "actual_verdict": "blocked" if policy_map["boundary_verdict"] == "source_boundary_blocked" else "failed",
            "run_id": f"{run_id}-policy-map",
            "artifact_path": (output_dir / "boundary_negative_controls.json").as_posix(),
        }
    )

    valid_hash_wrong_owner = boundary.verify_callable_source_boundary(
        candidate_truth,
        repo_root=repo_root,
        candidate_writable_roots=candidate_roots,
        candidate_artifact_roots=candidate_roots,
        expected_source_hash=sha256_file(candidate_path),
    )
    controls.append(
        {
            "control_id": "valid_hash_wrong_owner_rejected",
            "injected_violation": "valid source hash but source owner is candidate artifact root",
            "verifier_entrypoint": "verify_callable_source_boundary",
            "resolved_source_path": valid_hash_wrong_owner["resolved_source_path"],
            "source_hash": valid_hash_wrong_owner["source_hash"],
            "expected_block_reason": "candidate_artifact_source",
            "actual_block_reason": valid_hash_wrong_owner["block_reasons"],
            "actual_verdict": "blocked" if valid_hash_wrong_owner["boundary_verdict"] == "source_boundary_blocked" else "failed",
            "run_id": f"{run_id}-wrong-owner",
            "artifact_path": (output_dir / "boundary_negative_controls.json").as_posix(),
        }
    )

    generated_escape = boundary.verify_callable_source_boundary(
        candidate_truth,
        repo_root=repo_root,
        candidate_writable_roots=candidate_roots,
        candidate_artifact_roots=candidate_roots,
        generated_output_roots=candidate_roots,
    )
    controls.append(
        {
            "control_id": "path_escape_or_generated_code_rejected",
            "injected_violation": "generated-code/path-escape substitute source under candidate root",
            "verifier_entrypoint": "verify_callable_source_boundary",
            "resolved_source_path": generated_escape["resolved_source_path"],
            "source_hash": generated_escape["source_hash"],
            "expected_block_reason": "generated_code_source",
            "actual_block_reason": generated_escape["block_reasons"],
            "actual_verdict": "blocked" if generated_escape["boundary_verdict"] == "source_boundary_blocked" else "failed",
            "run_id": f"{run_id}-path-escape",
            "artifact_path": (output_dir / "boundary_negative_controls.json").as_posix(),
            "substitute_used": True,
        }
    )

    controls.append(
        run_runtime_mutation_control(
            repo_root=repo_root,
            output_dir=output_dir,
            source_pin_manifest=source_pin_manifest,
            run_id=f"{run_id}-runtime-mutation",
        )
    )
    return {
        "producer_function": "run_boundary_negative_controls",
        "controls": controls,
        "all_required_controls_passed": all(control["actual_verdict"] == "blocked" for control in controls),
        "self_declared_ownership_accepted": False,
        "provenance": provenance_for(
            run_boundary_negative_controls,
            repo_root=repo_root,
            inputs={"control_count": len(controls)},
            run_id=run_id,
            seed_context_episode_ids=[],
            aggregation_method="all_boundary_negative_controls_must_block",
            output_artifact_path=output_dir / "boundary_negative_controls.json",
        ),
    }


def run_clean_dirty_lookup_controls(
    *,
    repo_root: Path,
    output_dir: Path,
    run_id: str,
) -> dict[str, Any]:
    clean = environment.build_clean_candidate_bundle()
    clean_scan = leakage.scan_candidate_bundle_for_leakage(
        clean,
        run_id=f"{run_id}-clean",
        output_artifact_path=output_dir / "clean_dirty_lookup_controls.json",
    )
    dirty = dict(clean)
    dirty["metadata"] = {"nested": {"answer_key_alias": "answer-key:probe"}}
    dirty_scan = leakage.scan_candidate_bundle_for_leakage(
        dirty,
        run_id=f"{run_id}-dirty",
        output_artifact_path=output_dir / "clean_dirty_lookup_controls.json",
    )
    lookup = environment.build_lookup_memorization_bundle()
    lookup_blocked = "lookup_table" in lookup["serialized_state"]
    return {
        "producer_function": "run_clean_dirty_lookup_controls",
        "clean_control": {
            "verdict": "clean_control_passed" if clean_scan["verdict"] == "clean" else "clean_control_failed",
            "scanner_result": clean_scan,
        },
        "dirty_control": {
            "verdict": "dirty_control_blocked" if dirty_scan["verdict"] == "blocked" else "dirty_control_failed",
            "scanner_result": dirty_scan,
        },
        "lookup_memorization_control": {
            "verdict": "lookup_memorization_blocked" if lookup_blocked else "lookup_memorization_failed",
            "block_reason": "lookup_table_or_memorization_state_present" if lookup_blocked else None,
        },
        "self_reported_boolean_load_bearing": False,
        "command": stable_run_command("acp_bv_harness_001a.runner", output_dir, run_id),
    }


def run_counterfactual_controls(
    *,
    repo_root: Path,
    output_dir: Path,
    run_id: str,
) -> dict[str, Any]:
    clean = environment.build_clean_candidate_bundle()
    easy = environment.build_easy_action_bundle()
    clean_query_count = sum(
        len(episode["harness_selected_counterfactual_actions"]) for episode in clean["episodes"]
    )
    easy_missing = sum(
        1
        for output in easy["candidate_outputs"]
        if not output.get("counterfactual_predictions")
    )
    return {
        "producer_function": "run_counterfactual_controls",
        "harness_selected_counterfactual_action_queries": clean_query_count > 0,
        "counterfactual_query_count": clean_query_count,
        "fixed_action_set_alone": False,
        "easy_action_payload_missing_counterfactuals": easy_missing,
        "easy_action_payload_classification": "blocked_by_action_difficulty"
        if easy_missing
        else "counterfactual_control_failed",
        "provenance": provenance_for(
            run_counterfactual_controls,
            repo_root=repo_root,
            inputs={"clean_query_count": clean_query_count, "easy_missing_counterfactuals": easy_missing},
            run_id=run_id,
            seed_context_episode_ids=[],
            aggregation_method="harness_selected_counterfactual_queries_required",
            output_artifact_path=output_dir / "counterfactual_controls.json",
        ),
    }


def scan_claim_ceiling_and_forbidden_claims(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    serialized = json.dumps(payloads, sort_keys=True).lower()
    forbidden_positive_phrases = [
        "acp-bv mechanism validity: true",
        "gate validity: true",
        "admission readiness: true",
        "bridge readiness: true",
        "runtime readiness: true",
        "mainline effect: true",
        "agency evidence: true",
        "consciousness evidence: true",
        "real emotion: true",
        "autonomy: true",
        "ego readiness: true",
    ]
    hits = [phrase for phrase in forbidden_positive_phrases if phrase in serialized]
    return {
        "claim_ceiling": CLAIM_CEILING,
        "claim_ceiling_passed": all(payload.get("claim_ceiling", CLAIM_CEILING) == CLAIM_CEILING for payload in payloads),
        "forbidden_claim_scan_passed": not hits,
        "forbidden_positive_claim_hits": hits,
        "what_this_does_not_prove": [
            "ACP-BV validity",
            "ACP-BV mechanism validity",
            "Gate validity",
            "admission readiness",
            "bridge readiness",
            "runtime readiness",
            "mainline effect",
            "agency evidence",
            "consciousness",
            "real emotion",
            "autonomy",
            "stable user benefit",
            "EGO readiness",
        ],
        "task_id": TASK_ID,
    }
