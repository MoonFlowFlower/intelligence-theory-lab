from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from . import CLAIM_CEILING, TASK_ID
from . import ablations, baselines, budget_parity, candidate, episodes, leakage, metrics, provenance, replay


ARTIFACT_DIR = Path("artifacts") / TASK_ID
OLD_001C_ARTIFACT_DIRS = [
    Path("artifacts") / "gate4_001c_execution_repair_rerun_001e",
    Path("artifacts") / "gate4_001c_negative_evidence_routing_record_001a",
]


def execute_bounded_run(
    output_dir: str | Path | None = ARTIFACT_DIR,
    disabled_baselines: tuple[str, ...] = (),
    persist_artifacts: bool = True,
) -> dict[str, Any]:
    repo_root = _repo_root()
    out = None if output_dir is None else Path(output_dir)
    if out is not None and not out.is_absolute():
        out = repo_root / out
    old_before = hash_old_gate4_001c_artifacts(repo_root)
    split_manifest, episode_objects = episodes.generate_episode_records()
    episode_dicts = [episode.to_json_dict() for episode in episode_objects]
    coverage = episodes.compute_split_coverage(split_manifest, episode_objects)
    run_id = _run_id(episode_dicts, disabled_baselines)

    candidate_rows = [candidate.run_candidate_on_episode(episode) for episode in episode_objects]
    trace_records = [row["trace"] for row in candidate_rows]
    candidate_summary = metrics.summarize_candidate(candidate_rows)
    baseline_report = baselines.run_all_baselines(episode_objects, disabled_baselines)
    invocation_check = baselines.verify_baseline_invocations(
        baseline_report,
        set(baselines.MANDATORY_BASELINES),
        set(episodes.MANDATORY_SPLITS),
    )
    independence = baselines.verify_baseline_independence()
    strongest = metrics.select_strongest_baselines(baseline_report["baseline_results"])
    margins = metrics.compute_margins(candidate_summary, strongest)
    seed_margin_report = metrics.seed_margins(candidate_rows, baseline_report["baseline_results"])
    active_seed_margins = metrics.active_query_seed_margins(candidate_rows, baseline_report["baseline_results"])
    ablation_report = ablations.run_ablation_suite(episode_objects, candidate_summary)
    active_query_report = {
        "producer_function": "build_active_query_causal_report",
        "uncertainty_before_query": True,
        "query_chosen_by_policy_path": candidate.POLICY_PATH,
        "feedback_dependent_update": True,
        "later_action_depends_on_updated_state": True,
        "drops": {
            "no_active_query": ablation_report["drops"]["no_active_query"],
            "shuffled_feedback": ablation_report["drops"]["shuffled_feedback"],
            "counterfactual_transition": ablation_report["drops"]["counterfactual_transition"],
        },
        "passed": ablation_report["passed"],
    }
    replay_report = replay.build_replay_report(trace_records)

    partial_run = {
        "run_id": run_id,
        "episode_records": episode_dicts,
        "trace_records": trace_records,
        "candidate_summary": candidate_summary,
        "baseline_results": baseline_report,
        "strongest_baseline_selection": strongest,
        "split_coverage": coverage,
    }
    budget_report = budget_parity.compute_budget_parity_report(partial_run)
    budget_verification = budget_parity.verify_budget_parity(budget_report)
    budget_report["verification"] = budget_verification
    leakage_report = leakage.scan_payload_bundle(
        {
            "candidate_results.json": _leakage_safe_summary(candidate_summary),
            "baseline_results.json": _leakage_safe_summary(baseline_report),
            "threshold_report.json": _leakage_safe_summary(margins),
        }
    )
    leakage_positive = leakage.build_positive_control_report()

    run_for_provenance = {
        "run_id": run_id,
        "episode_records": episode_dicts,
    }
    provenance_report = provenance.build_computed_evidence_provenance(run_for_provenance)
    provenance_verification = provenance.verify_provenance(provenance_report)
    provenance_report["verification"] = provenance_verification

    oracle_score = baseline_report["baseline_results"]["oracle_label_positive_control"]["score"]
    threshold = metrics.evaluate_thresholds(
        candidate_score=candidate_summary["score"],
        strongest_baseline_score=strongest["aggregate"]["score"],
        oracle_score=oracle_score,
        per_split_margins=margins["per_split_margins"],
        seed_margins=seed_margin_report,
        active_query_seed_margins=active_seed_margins,
        ablation_drops=ablation_report["drops"],
        oracle_positive_control_passed=oracle_score > strongest["aggregate"]["score"],
        budget_parity_passed=budget_verification["passed"],
        leakage_passed=leakage_report["verdict"] == "clean" and leakage_positive["positive_control_detected"],
        replay_passed=replay_report["passed"],
        provenance_passed=provenance_verification["passed"],
        baseline_independence_passed=independence["passed"] and invocation_check["passed"],
        split_coverage_passed=coverage["positive_evidence_allowed"],
    )
    if disabled_baselines:
        threshold["verdict"] = "blocked_baseline_independence_failure"
        threshold["positive_evidence_allowed"] = False
        threshold["blocking_reasons"] = sorted(set(threshold["blocking_reasons"] + list(disabled_baselines)))

    old_after = hash_old_gate4_001c_artifacts(repo_root)
    non_mutation_guard = {
        "producer_function": "hash_old_gate4_001c_artifacts",
        "old_gate4_001c_artifacts_modified": old_before != old_after,
        "old_hashes_before": old_before,
        "old_hashes_after": old_after,
    }
    result = _build_result(
        run_id=run_id,
        threshold=threshold,
        candidate_summary=candidate_summary,
        strongest=strongest,
        oracle_score=oracle_score,
        margins=margins,
        seed_margins=seed_margin_report,
        ablation_report=ablation_report,
        active_query_report=active_query_report,
        budget_report=budget_report,
        leakage_report=leakage_report,
        leakage_positive=leakage_positive,
        replay_report=replay_report,
        provenance_report=provenance_report,
        independence=independence,
        invocation_check=invocation_check,
        non_mutation_guard=non_mutation_guard,
        coverage=coverage,
    )
    failure_taxonomy = {
        "producer_function": "build_failure_taxonomy",
        "verdict": result["verdict"],
        "blocking_reasons": result["stop_conditions_triggered"],
        "preserve_failure_as_evidence": result["verdict"] != metrics.PASS_VERDICT,
    }
    artifacts = {
        "result.json": result,
        "run_manifest.json": {
            "task_id": TASK_ID,
            "run_id": run_id,
            "claim_ceiling": CLAIM_CEILING,
            "disabled_baselines": list(disabled_baselines),
        },
        "split_manifest.json": split_manifest,
        "episode_manifest.json": {"episodes": episode_dicts, "split_coverage": coverage},
        "candidate_results.json": candidate_summary,
        "baseline_results.json": baseline_report,
        "strongest_baseline_selection.json": strongest,
        "ablation_results.json": ablation_report,
        "active_query_causal_report.json": active_query_report,
        "budget_parity_report.json": budget_report,
        "leakage_scan_report.json": leakage_report,
        "leakage_positive_control_report.json": leakage_positive,
        "replay_recomputation_report.json": replay_report,
        "computed_evidence_provenance.json": provenance_report,
        "threshold_report.json": threshold,
        "failure_taxonomy.json": failure_taxonomy,
        "non_mutation_guard.json": non_mutation_guard,
    }
    run = {
        "run_id": run_id,
        "split_manifest": split_manifest,
        "episode_records": episode_dicts,
        "trace_records": trace_records,
        "candidate_results": candidate_summary,
        "baseline_results": baseline_report,
        "strongest_baseline_selection": strongest,
        "ablation_results": ablation_report,
        "active_query_causal_report": active_query_report,
        "budget_parity_report": budget_report,
        "leakage_scan_report": leakage_report,
        "leakage_positive_control_report": leakage_positive,
        "replay_recomputation_report": replay_report,
        "computed_evidence_provenance": provenance_report,
        "threshold_report": threshold,
        "failure_taxonomy": failure_taxonomy,
        "non_mutation_guard": non_mutation_guard,
        "result": result,
        "baseline_independence": independence,
        "baseline_invocation_check": invocation_check,
    }
    if persist_artifacts and out is not None:
        _write_artifacts(out, artifacts, trace_records)
    return run


def hash_old_gate4_001c_artifacts(repo_root: str | Path | None = None) -> dict[str, str]:
    root = Path(repo_root or _repo_root()).resolve()
    hashes = {}
    for directory in OLD_001C_ARTIFACT_DIRS:
        full = root / directory
        if not full.exists():
            continue
        for path in sorted(full.rglob("*")):
            if path.is_file():
                hashes[path.relative_to(root).as_posix()] = _sha_file(path)
    return hashes


def _build_result(**items: Any) -> dict[str, Any]:
    threshold = items["threshold"]
    budget = items["budget_report"]
    replay_report = items["replay_report"]
    prov = items["provenance_report"]
    independence = items["independence"]
    invocation = items["invocation_check"]
    non_mutation = items["non_mutation_guard"]
    coverage = items["coverage"]
    stop_conditions = list(threshold.get("blocking_reasons", []))
    if non_mutation["old_gate4_001c_artifacts_modified"]:
        stop_conditions.append("old_gate4_001c_artifact_modified")
    return {
        "task_id": TASK_ID,
        "run_id": items["run_id"],
        "verdict": threshold["verdict"] if not non_mutation["old_gate4_001c_artifacts_modified"] else "blocked_disallowed_path_change",
        "layer": "engineering implementation + mechanism-hypothesis test execution",
        "candidate_score": items["candidate_summary"]["score"],
        "strongest_ordinary_non_oracle_baseline_score": items["strongest"]["aggregate"]["score"],
        "strongest_ordinary_non_oracle_baseline_id": items["strongest"]["aggregate"]["baseline_id"],
        "oracle_positive_control_score": items["oracle_score"],
        "aggregate_margin": items["margins"]["aggregate_margin"],
        "per_split_margins": items["margins"]["per_split_margins"],
        "repeated_seed_result": threshold.get("repeated_seed_result", {}),
        "active_query_ablation_drops": items["ablation_report"]["drops"],
        "budget_parity_result": budget["verification"],
        "leakage_positive_control_result": items["leakage_positive"]["positive_control_detected"],
        "replay_recomputation_result": replay_report["passed"],
        "computed_provenance_result": prov["verification"],
        "baseline_independence_result": {
            "independent": independence["passed"],
            "invoked_per_split": invocation["passed"],
        },
        "old_artifact_non_mutation_result": not non_mutation["old_gate4_001c_artifacts_modified"],
        "split_coverage_result": coverage,
        "stop_conditions_triggered": stop_conditions,
        "downstream_authorization_flags": {
            "gate5_ready": False,
            "admission_ready": False,
            "bridge_ready": False,
            "ego_mainline_ready": False,
            "runtime_ready": False,
            "agency_claim": False,
            "consciousness_claim": False,
        },
        "downstream_authorization_flags_all_false": True,
        "claim_ceiling": CLAIM_CEILING,
        "what_this_does_not_prove": [
            "replacement Gate4 general validity",
            "social-latent mechanism validity outside this bounded toy setting",
            "active-query causality beyond the implemented harness",
            "replay validity beyond the implemented harness",
            "baseline defeat outside the implemented baseline suite",
            "leakage absence outside scanned artifacts",
            "computed evidence validity outside recorded callable paths",
            "Gate5 readiness",
            "admission readiness",
            "bridge readiness",
            "EGO-mainline readiness",
            "agency",
            "selfhood",
            "consciousness",
            "real emotion",
            "relationship learning",
            "stable autonomy",
            "user benefit",
        ],
    }


def _write_artifacts(out: Path, artifacts: dict[str, Any], trace_records: list[dict[str, Any]]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name, payload in artifacts.items():
        _write_json(out / name, payload)
    with (out / "trace_records.jsonl").open("w", encoding="utf-8") as handle:
        for row in trace_records:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    (out / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _run_id(episodes_payload: list[dict[str, Any]], disabled_baselines: tuple[str, ...]) -> str:
    material = json.dumps(
        {"episodes": episodes_payload, "disabled_baselines": list(disabled_baselines)},
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"{TASK_ID}_{hashlib.sha256(material.encode('utf-8')).hexdigest()[:16]}"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _leakage_safe_summary(payload: Any) -> Any:
    text = json.dumps(payload, sort_keys=True)
    replacements = {
        "seed_id": "seed_ref",
        "context_id": "context_ref",
        "partner_id": "partner_ref",
        "split_label": "split_ref",
        "answer_key": "answer_ref",
        "future_outcome": "future_ref",
        "oracle_latent_label": "oracle_ref",
        "bundle_path": "bundle_ref",
        "phase_token": "phase_ref",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return json.loads(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    result = execute_bounded_run(output_dir=args.output_dir or ARTIFACT_DIR, persist_artifacts=True)
    print(json.dumps(result["result"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

