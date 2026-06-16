from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
from pathlib import Path
from typing import Any

from . import (
    CLAIM_CEILING,
    CURRENT_LAYER,
    EQUIVALENCE_BAND,
    SEEDS,
    START_COMMIT,
    START_TAG,
    TASK_ID,
    WHAT_THIS_DOES_NOT_PROVE,
    classify_b3_delta,
    episode_ids,
    provenance_for,
    sha256_text,
    write_json,
)
from . import baselines, candidate, coupling, detectors, generator, leakage_scanner, replay, source_boundary


REQUIRED_ARTIFACTS = [
    "result.json",
    "readback.json",
    "validation.json",
    "run_manifest.json",
    "source_boundary.json",
    "source_pin.json",
    "distribution_manifest.json",
    "novelty_report.json",
    "factorization_report.json",
    "baseline_matrix.json",
    "strongest_baseline_selection.json",
    "candidate_results.json",
    "baseline_results.json",
    "b3_classification.json",
    "multi_seed_stability.json",
    "detector_failability.json",
    "leakage_scan.json",
    "leakage_literal_audit.json",
    "solvability_preflight.json",
    "candidate_truth_decoupling.json",
    "ablation_results.json",
    "replay_results.json",
    "provenance_rows.jsonl",
    "forbidden_scope_scan.txt",
    "claim_ceiling.txt",
]

ALLOWED_PREFIXES = (
    "src/acp_bv_distribution_harness_001b/",
    "tests/test_acp_bv_distribution_harness_001b.py",
    "tests/test_acp_bv_detector_failability_001b.py",
    "tests/test_acp_bv_leakage_scanner_001b.py",
    "tests/test_acp_bv_replay_001b.py",
    "tests/test_acp_bv_source_boundary_001b.py",
    "artifacts/acp_bv_distribution_harness_001b_execution_001a/",
    "artifacts/acp_bv_001b_collapse_closure_001a/",
)


def _prepare_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        for child in output_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _score_candidate_for_dataset(dataset: dict[str, Any]) -> dict[str, Any]:
    state = candidate.fit_candidate(dataset["train"])
    outputs = candidate.run_candidate(state, dataset["heldout"])
    score = baselines.score_outputs(dataset["heldout"], outputs)
    return {"seed": dataset["seed"], "serialized_state": state, "outputs": outputs, "score": score}


def _multi_seed_stability(candidate_scores: dict[int, float], strongest_by_seed: dict[int, float]) -> dict[str, Any]:
    rows = []
    deltas = []
    for seed in SEEDS:
        delta = round(candidate_scores[seed] - strongest_by_seed[seed], 6)
        deltas.append(delta)
        rows.append(
            {
                "seed": seed,
                "candidate_score": candidate_scores[seed],
                "strongest_fair_baseline_score": strongest_by_seed[seed],
                "delta": delta,
                "b3_classification": classify_b3_delta(delta),
            }
        )
    mean_delta = round(statistics.fmean(deltas), 6)
    median_delta = round(statistics.median(deltas), 6)
    dispersion = round(statistics.pstdev(deltas), 6)
    ci_lower = round(mean_delta - dispersion, 6)
    return {
        "producer_function": "_multi_seed_stability",
        "seeds": list(SEEDS),
        "seed_count": len(SEEDS),
        "per_seed": rows,
        "mean_delta": mean_delta,
        "median_delta": median_delta,
        "dispersion_pstdev": dispersion,
        "bootstrap_ci_or_equivalent": {"method": "mean_minus_population_stdev", "lower": ci_lower, "upper": round(mean_delta + dispersion, 6)},
        "outside_equivalence_seed_count": sum(1 for row in rows if row["b3_classification"] != "baseline_equivalent"),
        "any_seed_baseline_equivalent": any(row["b3_classification"] == "baseline_equivalent" for row in rows),
        "ci_lower_exits_equivalence_band": ci_lower > EQUIVALENCE_BAND,
    }


def _ablation_results(
    *,
    datasets: list[dict[str, Any]],
    serialized_state_by_seed: dict[int, dict[str, Any]],
    run_id: str,
    output_artifact_path: Path,
) -> dict[str, Any]:
    rows = []
    for ablation_id, mutator in {
        "remove_action_conditioning": lambda state: {
            **state,
            "boundary_model": {**state["boundary_model"], "action_deltas": {key: 0 for key in state["boundary_model"]["action_deltas"]}},
            "viability_model": {**state["viability_model"], "action_deltas": {key: 0 for key in state["viability_model"]["action_deltas"]}},
        },
        "replace_boundary_state": lambda state: {
            **state,
            "boundary_model": {**state["boundary_model"], "weights": {key: 0 for key in state["boundary_model"]["weights"]}},
        },
        "replace_viability_state": lambda state: {
            **state,
            "viability_model": {**state["viability_model"], "positive_residues": []},
        },
        "shuffle_phase_weight": lambda state: {
            **state,
            "boundary_model": {**state["boundary_model"], "weights": {**state["boundary_model"]["weights"], "phase_code": 0}},
        },
    }.items():
        scores = []
        for dataset in datasets:
            seed = dataset["seed"]
            mutated = mutator(serialized_state_by_seed[seed])
            outputs = candidate.run_candidate(mutated, dataset["heldout"])
            scores.append(baselines.score_outputs(dataset["heldout"], outputs))
        rows.append(
            {
                "ablation_id": ablation_id,
                "episodes_rerun": True,
                "score": round(sum(scores) / len(scores), 6),
                "effect_size": round(1.0 - (sum(scores) / len(scores)), 6),
                "regenerated_trace_path": output_artifact_path.as_posix(),
                "provenance": provenance_for(
                    _ablation_results,
                    inputs={"ablation_id": ablation_id, "seed_count": len(datasets)},
                    run_id=f"{run_id}-{ablation_id}",
                    seed="multi_seed",
                    context_episode_ids=[str(dataset["seed"]) for dataset in datasets],
                    aggregation_method="rerun_candidate_predictions_under_intervention",
                    output_artifact_path=output_artifact_path,
                ),
            }
        )
    return {
        "producer_function": "_ablation_results",
        "ablations": rows,
        "all_rerun": all(row["episodes_rerun"] for row in rows),
        "report_field_editing_used": False,
    }


def _forbidden_scope_scan(repo_root: Path) -> tuple[str, bool]:
    status = subprocess.run(
        ["git", "status", "--porcelain=v1", "-uall"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    violations = []
    for line in status:
        path = line[3:].replace("\\", "/")
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        if not path:
            continue
        if not any(path.startswith(prefix) or path == prefix for prefix in ALLOWED_PREFIXES):
            violations.append(path)
    text = "forbidden_scope_violation=false\n"
    if violations:
        text = "forbidden_scope_violation=true\n" + "\n".join(violations) + "\n"
    return text, not violations


def _collect_provenance(payloads: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            if {"producer_function", "run_id", "aggregation_method", "code_path_hash"}.issubset(value):
                rows.append(value)
            for nested in value.values():
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    for payload in payloads:
        walk(payload)
    return rows


def _closure_dir_for(output_dir: Path) -> Path:
    return output_dir.parent / "acp_bv_001b_collapse_closure_001a"


def _terminal_triggers(
    *,
    distribution_manifest: dict[str, Any],
    novelty_report: dict[str, Any],
    baseline_matrix: dict[str, Any],
    factorization: dict[str, Any],
    decoupling: dict[str, Any],
    solvability: dict[str, Any],
    detector_report: dict[str, Any],
) -> list[dict[str, str]]:
    triggers = []
    if decoupling["verdict"] == "blocked_by_candidate_truth_coupling":
        triggers.append({"collapse_family": "candidate_truth_coupling", "verdict": "blocked_by_candidate_truth_coupling"})
    if baseline_matrix["blocked_by_baseline_equivalence"]:
        triggers.append({"collapse_family": "baseline_equivalence", "verdict": "blocked_by_baseline_equivalence"})
    if factorization["blocked_by_factorized_lookup_equivalence"]:
        triggers.append({"collapse_family": "factorized_lookup_equivalence", "verdict": "blocked_by_factorized_lookup_equivalence"})
    if solvability["leaking_oracle_solvability_detected"]:
        triggers.append({"collapse_family": "leaking_oracle_invalidity", "verdict": "blocked_by_leaking_oracle_invalidity"})
    if novelty_report["verdict"] == "blocked_by_insufficient_heldout_novelty":
        triggers.append({"collapse_family": "non_discriminative_distribution", "verdict": "blocked_by_insufficient_heldout_novelty"})
    if distribution_manifest["maximum_lookup_complete_heldout_ratio"] > 0.75:
        triggers.append({"collapse_family": "lookup_complete_distribution", "verdict": "blocked_by_lookup_complete_distribution"})
    if detector_report["blocking_verdict"] == "blocked_by_non_fail_able_detector":
        triggers.append({"collapse_family": "non_fail_able_detector", "verdict": "blocked_by_non_fail_able_detector"})
    return triggers


def _write_collapse_closure(
    *,
    closure_dir: Path,
    triggers: list[dict[str, str]],
    decoupling: dict[str, Any],
    baseline_matrix: dict[str, Any],
    detector_report: dict[str, Any],
    solvability: dict[str, Any],
    factorization: dict[str, Any],
) -> dict[str, Any]:
    primary = triggers[0]
    payload = {
        "task_id": "acp_bv_001b_collapse_closure_001a",
        "terminal": True,
        "collapse_family": primary["collapse_family"],
        "primary_verdict": primary["verdict"],
        "co_triggers": [trigger["verdict"] for trigger in triggers[1:]],
        "coupling_report": decoupling,
        "baseline_equivalence": {
            "blocked_by_baseline_equivalence": baseline_matrix["blocked_by_baseline_equivalence"],
            "strongest_baseline": baseline_matrix["strongest_baseline"],
        },
        "detector_failability": {
            "all_actual_flips_match_predeclared": detector_report["all_actual_flips_match_predeclared"],
            "all_controls_discriminated": detector_report["all_controls_discriminated"],
            "blocking_verdict": detector_report["blocking_verdict"],
        },
        "leakage_report": solvability,
        "factorization_report": factorization,
        "evidence_hashes": {
            "coupling": decoupling.get("evidence_hash"),
            "solvability": solvability.get("evidence_hash"),
            "detector_control_hash": sha256_text(json.dumps(detector_report["controls"], sort_keys=True)),
            "factorization_hash": sha256_text(json.dumps(factorization, sort_keys=True)),
        },
        "claim_ceiling": "local ACP-BV 001B harness collapse closure only",
        "what_this_does_not_prove": (
            "Does not prove ACP-BV validity, mechanism validity, Gate validity, mainline effect, "
            "agency, consciousness, emotion, autonomy, stable user benefit, or EGO readiness."
        ),
    }
    write_json(closure_dir / "result.json", payload)
    return payload


def run_harness(
    *,
    repo_root: Path,
    output_dir: Path,
    run_id: str = "acp-bv-distribution-harness-001b-execution-001a",
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    _prepare_output_dir(output_dir)

    datasets = [generator.generate_distribution(seed=seed, heldout_count=128) for seed in SEEDS]
    distribution_manifest = generator.combined_distribution_manifest(datasets)
    novelty_report = {
        "producer_function": "novelty_report",
        "per_seed": distribution_manifest["per_seed"],
        "verdict": "novelty_floor_passed" if distribution_manifest["all_constraints_satisfied"] else "blocked_by_insufficient_heldout_novelty",
    }

    candidate_results = [_score_candidate_for_dataset(dataset) for dataset in datasets]
    candidate_scores = {int(row["seed"]): row["score"] for row in candidate_results}
    serialized_state_by_seed = {int(row["seed"]): row["serialized_state"] for row in candidate_results}
    candidate_outputs_by_seed = {int(row["seed"]): row["outputs"] for row in candidate_results}
    baseline_matrix = baselines.run_baseline_matrix(
        datasets=datasets,
        candidate_scores_by_seed=candidate_scores,
        run_id=f"{run_id}-baselines",
        output_artifact_path=output_dir / "baseline_matrix.json",
    )
    strongest_by_seed = {}
    for seed_row in baseline_matrix["per_seed"]:
        strongest_by_seed[seed_row["seed"]] = max(row["score"] for row in seed_row["baselines"])
    stability = _multi_seed_stability(candidate_scores, strongest_by_seed)
    b3 = {
        "producer_function": "b3_classification",
        "equivalence_band_abs_delta_lte": EQUIVALENCE_BAND,
        "per_seed": stability["per_seed"],
        "aggregate_classification": classify_b3_delta(
            round(
                sum(candidate_scores.values()) / len(candidate_scores)
                - baseline_matrix["strongest_baseline"]["score"],
                6,
            )
        ),
    }

    first = candidate_results[0]
    replay_report = replay.recompute_candidate_outputs(
        serialized_state=first["serialized_state"],
        episodes=datasets[0]["heldout"],
        candidate_outputs=first["outputs"],
        run_id=f"{run_id}-replay",
        output_artifact_path=output_dir / "replay_results.json",
    )
    leakage_report = leakage_scanner.run_leakage_positive_controls(
        run_id=f"{run_id}-leakage",
        output_artifact_path=output_dir / "leakage_scan.json",
    )
    leakage_audit = leakage_scanner.audit_scanner_literals(
        leakage_report["runtime_generated_identifiers"],
        output_artifact_path=output_dir / "leakage_literal_audit.json",
    )
    detector_report = detectors.run_detector_failability_controls(
        run_id=f"{run_id}-detectors",
        output_artifact_path=output_dir / "detector_failability.json",
        repo_root=repo_root,
    )
    source_pin = source_boundary.create_source_pin(
        repo_root=repo_root,
        run_id=f"{run_id}-source-pin",
        output_artifact_path=output_dir / "source_pin.json",
    )
    tamper_control = source_boundary.run_tamper_after_anchor_control(source_pin, repo_root=repo_root)
    source_boundary_report = {
        "producer_function": "source_boundary_report",
        "source_boundary_verdict": "source_boundary_pass" if source_pin["verification"]["passed"] else "blocked_by_source_boundary_failure",
        "self_declared_repo_source_owned_accepted": False,
        "tamper_after_anchor_control": tamper_control,
        "source_pin_verification": source_pin["verification"],
    }
    decoupling = coupling.detect_candidate_truth_coupling(
        predict_fn=candidate.predict,
        fit_fn=candidate.fit_candidate,
        truth_fn=generator.truth_for,
        datasets=datasets,
        seed=SEEDS[0],
        run_id=f"{run_id}-candidate-truth-coupling",
        output_artifact_path=output_dir / "candidate_truth_decoupling.json",
    )
    solvability = leakage_scanner.run_solvability_preflight(
        datasets=datasets,
        run_id=f"{run_id}-solvability",
        output_artifact_path=output_dir / "solvability_preflight.json",
    )
    ablation_report = _ablation_results(
        datasets=datasets,
        serialized_state_by_seed=serialized_state_by_seed,
        run_id=f"{run_id}-ablations",
        output_artifact_path=output_dir / "ablation_results.json",
    )
    factorization = baselines.factorization_report(datasets, candidate_outputs_by_seed=candidate_outputs_by_seed)
    strongest_selection = {
        "producer_function": "strongest_baseline_selection",
        "selection_rule": baseline_matrix["strongest_baseline_selection_rule"],
        "strongest_baseline": baseline_matrix["strongest_baseline"],
    }
    baseline_results = {
        "producer_function": "baseline_results",
        "baseline_output_samples": baseline_matrix["baseline_output_samples"],
    }
    candidate_results_artifact = {
        "producer_function": "candidate_results",
        "candidate_score_by_seed": candidate_scores,
        "candidate_score": round(sum(candidate_scores.values()) / len(candidate_scores), 6),
        "serialized_state_by_seed": serialized_state_by_seed,
        "output_samples_by_seed": {row["seed"]: row["outputs"][:5] for row in candidate_results},
    }
    forbidden_scope_text, scope_ok = _forbidden_scope_scan(repo_root)
    (output_dir / "forbidden_scope_scan.txt").write_text(forbidden_scope_text, encoding="utf-8")

    terminal_triggers = _terminal_triggers(
        distribution_manifest=distribution_manifest,
        novelty_report=novelty_report,
        baseline_matrix=baseline_matrix,
        factorization=factorization,
        decoupling=decoupling,
        solvability=solvability,
        detector_report=detector_report,
    )
    closure_payload = None
    if terminal_triggers:
        closure_payload = _write_collapse_closure(
            closure_dir=_closure_dir_for(output_dir),
            triggers=terminal_triggers,
            decoupling=decoupling,
            baseline_matrix=baseline_matrix,
            detector_report=detector_report,
            solvability=solvability,
            factorization=factorization,
        )

    verdict = "acp_bv_001b_local_harness_execution_001a_ready_for_independent_audit"
    blocker = None
    if terminal_triggers:
        verdict = terminal_triggers[0]["verdict"]
    elif not detector_report["all_actual_flips_match_predeclared"] or not detector_report["all_controls_discriminated"]:
        verdict = "blocked_by_non_fail_able_detector"
    elif not leakage_report["validation"]["passed"] or not leakage_audit["no_runtime_identifier_in_source_literals"]:
        verdict = "blocked_by_whitelist_leakage_scanner"
    elif replay_report["verdict"] != "replay_recomputed":
        verdict = "blocked_by_replay_recomputation_failure"
    elif source_boundary_report["source_boundary_verdict"] != "source_boundary_pass":
        verdict = "blocked_by_source_boundary_failure"
    elif not scope_ok:
        verdict = "blocked_by_forbidden_file_change"
    if verdict.startswith("blocked_by_"):
        blocker = verdict

    validation = {
        "producer_function": "validation",
        "all_required_artifacts_present": True,
        "all_required_baselines_run": baseline_matrix["all_required_baselines_ran"],
        "detector_failability_passed": detector_report["all_actual_flips_match_predeclared"]
        and detector_report["all_controls_discriminated"],
        "leakage_runtime_variants_passed": leakage_report["validation"]["passed"],
        "leakage_literal_audit_passed": leakage_audit["no_runtime_identifier_in_source_literals"]
        and leakage_audit["no_runtime_identifier_in_source_text"],
        "replay_recomputed": replay_report["verdict"] == "replay_recomputed",
        "source_boundary_passed": source_boundary_report["source_boundary_verdict"] == "source_boundary_pass",
        "no_static_verdict_dictionary": True,
        "no_forbidden_scope_paths_changed": scope_ok,
        "auto_remote_anchor": {"decision": "forbidden", "performed": False},
        "blocking_verdict": blocker,
        "terminal_collapse": bool(terminal_triggers),
        "closure_artifact": (_closure_dir_for(output_dir) / "result.json").as_posix() if terminal_triggers else None,
    }
    result = {
        "task_id": TASK_ID,
        "verdict": verdict,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": "none",
        "enabled_status": "local CLI / local pytest / local artifact generation only",
        "real_trigger_evidence": {
            "run_id": run_id,
            "required_start_commit": START_COMMIT,
            "required_start_tag": START_TAG,
            "callable_runner": "acp_bv_distribution_harness_001b.runner.run_harness",
            "artifact_dir": output_dir.as_posix(),
        },
        "real_gate_target_applied": False,
        "safe_to_wire_mainline": False,
        "candidate_score": candidate_results_artifact["candidate_score"],
        "strongest_baseline": baseline_matrix["strongest_baseline"],
        "terminal_collapse": bool(terminal_triggers),
        "collapse_closure_artifact": (_closure_dir_for(output_dir) / "result.json").as_posix() if terminal_triggers else None,
        "claim_ceiling": CLAIM_CEILING,
        "what_this_does_not_prove": WHAT_THIS_DOES_NOT_PROVE,
        "next_minimal_closed_loop_action": (
            "Send execution artifacts, traces, replay outputs, detector fail-ability outputs, "
            "leakage literal audit, baseline matrix, and source-boundary evidence to Claude for independent hostile audit."
        ),
    }
    readback = {
        "task_id": TASK_ID,
        "verdict": verdict,
        "current_layer": CURRENT_LAYER,
        "mainline_integration_status": "none",
        "enabled_status": result["enabled_status"],
        "real_trigger_evidence": result["real_trigger_evidence"],
        "git_head_at_execution": _git(repo_root, "rev-parse", "HEAD"),
        "artifact_dir": output_dir.as_posix(),
        "collapse_closure_artifact": (_closure_dir_for(output_dir) / "result.json").as_posix() if terminal_triggers else None,
        "claim_ceiling": CLAIM_CEILING,
        "what_this_does_not_prove": WHAT_THIS_DOES_NOT_PROVE,
    }
    run_manifest = {
        "task_id": TASK_ID,
        "run_id": run_id,
        "command": (
            "$env:PYTHONPATH='src'; python -m acp_bv_distribution_harness_001b.runner "
            f"--output-dir {output_dir.as_posix()} --run-id {run_id}"
        ),
        "seeds": list(SEEDS),
        "required_artifacts": REQUIRED_ARTIFACTS,
        "real_gate_target_applied": False,
        "auto_remote_anchor": {"decision": "forbidden", "performed": False},
        "claim_ceiling": CLAIM_CEILING,
    }

    artifacts = {
        "result.json": result,
        "readback.json": readback,
        "validation.json": validation,
        "run_manifest.json": run_manifest,
        "source_boundary.json": source_boundary_report,
        "source_pin.json": source_pin,
        "distribution_manifest.json": distribution_manifest,
        "novelty_report.json": novelty_report,
        "factorization_report.json": factorization,
        "baseline_matrix.json": baseline_matrix,
        "strongest_baseline_selection.json": strongest_selection,
        "candidate_results.json": candidate_results_artifact,
        "baseline_results.json": baseline_results,
        "b3_classification.json": b3,
        "multi_seed_stability.json": stability,
        "detector_failability.json": detector_report,
        "leakage_scan.json": leakage_report,
        "leakage_literal_audit.json": leakage_audit,
        "solvability_preflight.json": solvability,
        "candidate_truth_decoupling.json": decoupling,
        "ablation_results.json": ablation_report,
        "replay_results.json": replay_report,
    }
    for name, payload in artifacts.items():
        write_json(output_dir / name, payload)
    provenance_rows = _collect_provenance(list(artifacts.values()))
    with (output_dir / "provenance_rows.jsonl").open("w", encoding="utf-8") as handle:
        for row in provenance_rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    (output_dir / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    validation["all_required_artifacts_present"] = all((output_dir / name).exists() for name in REQUIRED_ARTIFACTS)
    write_json(output_dir / "validation.json", validation)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/acp_bv_distribution_harness_001b_execution_001a")
    parser.add_argument("--run-id", default="acp-bv-distribution-harness-001b-execution-001a")
    args = parser.parse_args()
    result = run_harness(repo_root=Path.cwd(), output_dir=Path(args.output_dir), run_id=args.run_id)
    print(result["verdict"])
    return 0 if not str(result["verdict"]).startswith("blocked_by_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
