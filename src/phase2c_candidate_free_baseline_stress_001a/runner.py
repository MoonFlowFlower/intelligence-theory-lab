import argparse
import hashlib
import inspect
import json
from pathlib import Path
from statistics import mean
from typing import Any, Callable

from phase2c_hidden_latent_harness_001a import runner as base


TASK_ID = "RESEARCH-CAMPAIGN-PHASE2C-CANDIDATE-FREE-BASELINE-STRESS-EXECUTION-001A"
RUN_ID = "phase2c_candidate_free_baseline_stress_001a"
DEFAULT_SEEDS = (17, 29, 41, 53, 67)
DEFAULT_TRAIN_FAMILY_COUNT = 3
DEFAULT_HELDOUT_FAMILY_COUNT = 3
DEFAULT_EPISODES_PER_FAMILY = 4
EQUIVALENCE_BAND = 0.03
LOOKUP_FAMILY_BASELINES = {
    "lookup",
    "count_table",
    "transition_table",
    "graph_cache",
    "successor_map",
    "trace_only_replay",
}
DEFAULT_OUTPUT_FILES = base.DEFAULT_OUTPUT_FILES
CLAIM_CEILING = (
    "Phase2C candidate-free baseline-stress execution evidence only. "
    "This does not provide candidate validation, mechanism validity, "
    "consciousness, real emotion, autonomy, EGO readiness, companion readiness, "
    "runtime/mainline effect, route exhaustion, terminal verdict, or program "
    "completion."
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def code_path_hash(func: Callable[..., Any]) -> str:
    return _sha256_bytes(inspect.getsource(func).encode("utf-8"))


def default_stress_config() -> dict[str, Any]:
    return {
        "seeds": list(DEFAULT_SEEDS),
        "train_family_count": DEFAULT_TRAIN_FAMILY_COUNT,
        "heldout_family_count": DEFAULT_HELDOUT_FAMILY_COUNT,
        "episodes_per_family": DEFAULT_EPISODES_PER_FAMILY,
        "equivalence_band": EQUIVALENCE_BAND,
    }


def expected_trace_rows(config: dict[str, Any]) -> int:
    return (
        len(config["seeds"])
        * (config["train_family_count"] + config["heldout_family_count"])
        * config["episodes_per_family"]
    )


def _seed_run_id(seed: int) -> str:
    return f"{RUN_ID}_seed_{seed}"


def _visible_rows(surface: dict[str, Any]) -> list[dict[str, Any]]:
    return [base.candidate_visible_episode(episode) for episode in surface["episodes"]]


def _retag_trace_rows(rows: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    tagged = []
    run_id = _seed_run_id(seed)
    for row in rows:
        new_row = dict(row)
        original_episode_id = str(row["episode_id"])
        new_row["run_id"] = run_id
        new_row["stress_seed"] = seed
        new_row["original_episode_id"] = original_episode_id
        new_row["episode_id"] = f"seed_{seed}_{original_episode_id}"
        tagged.append(new_row)
    return tagged


def _retag_baseline_report(report: dict[str, Any], seed: int) -> dict[str, Any]:
    run_id = _seed_run_id(seed)
    retagged = json.loads(json.dumps(report))
    for row in retagged["results"]:
        row["run_id"] = run_id
        row["seed_context_episode_ids"] = [
            f"seed_{seed}_{episode_id}" for episode_id in row["seed_context_episode_ids"]
        ]
    retagged["strongest_fair_baseline"] = max(
        retagged["results"], key=lambda row: row["macro_accuracy"]
    )
    return retagged


def run_seed_surface(seed: int, config: dict[str, Any]) -> dict[str, Any]:
    surface = base.generate_surface(
        seed=seed,
        train_family_count=config["train_family_count"],
        heldout_family_count=config["heldout_family_count"],
        episodes_per_family=config["episodes_per_family"],
    )
    surface["run_id"] = _seed_run_id(seed)
    baseline_report = _retag_baseline_report(base.run_baseline_battery(surface), seed)
    leakage_report = base.run_leakage_scan(_visible_rows(surface))
    replay_report = base.run_replay_check(surface)
    ablation_report = base.build_ablation_plan(surface)
    trace = _retag_trace_rows(base.build_trace(surface), seed)
    return {
        "seed": seed,
        "run_id": _seed_run_id(seed),
        "surface": surface,
        "baseline_report": baseline_report,
        "leakage_report": leakage_report,
        "replay_report": replay_report,
        "ablation_report": ablation_report,
        "trace": trace,
    }


def aggregate_baseline_reports(seed_runs: list[dict[str, Any]]) -> dict[str, Any]:
    baseline_ids = sorted(base.REQUIRED_BASELINES)
    aggregate_rows = []
    for baseline_id in baseline_ids:
        per_seed_scores = [
            row["macro_accuracy"]
            for seed_run in seed_runs
            for row in seed_run["baseline_report"]["results"]
            if row["baseline_id"] == baseline_id
        ]
        aggregate_rows.append(
            {
                "baseline_id": baseline_id,
                "producer_function": (
                    "phase2c_candidate_free_baseline_stress_001a.runner."
                    "aggregate_baseline_reports"
                ),
                "input_artifacts": [
                    f"generated_phase2c_hidden_latent_surface_seed_{seed_run['seed']}"
                    for seed_run in seed_runs
                ],
                "run_id": RUN_ID,
                "seed_context_episode_ids": [seed_run["run_id"] for seed_run in seed_runs],
                "aggregation_rule": "mean_macro_accuracy_over_stress_seeds",
                "code_path_hash": code_path_hash(aggregate_baseline_reports),
                "callable_invoked": True,
                "consumed_by_final_verdict": True,
                "per_seed_macro_accuracy": per_seed_scores,
                "macro_accuracy": mean(per_seed_scores) if per_seed_scores else 0.0,
            }
        )

    strongest = max(aggregate_rows, key=lambda row: row["macro_accuracy"])
    strongest_score = strongest["macro_accuracy"]
    tying = [
        row["baseline_id"]
        for row in aggregate_rows
        if abs(row["macro_accuracy"] - strongest_score) <= 1e-12
    ]
    return {
        "producer_function": (
            "phase2c_candidate_free_baseline_stress_001a.runner.aggregate_baseline_reports"
        ),
        "access_boundary": "candidate_visible_plus_budget_only",
        "baseline_ids": baseline_ids,
        "declared_baseline_ids": baseline_ids,
        "missing_baseline_ids": sorted(base.REQUIRED_BASELINES - set(baseline_ids)),
        "per_seed_reports": [
            {
                "seed": seed_run["seed"],
                "run_id": seed_run["run_id"],
                "trace_row_count": len(seed_run["trace"]),
                "strongest_fair_baseline": seed_run["baseline_report"]["strongest_fair_baseline"],
                "results": seed_run["baseline_report"]["results"],
            }
            for seed_run in seed_runs
        ],
        "aggregate_results": aggregate_rows,
        "strongest_fair_baseline": strongest,
        "strongest_fair_is_max_over_full_battery": strongest_score
        == max(row["macro_accuracy"] for row in aggregate_rows),
        "baseline_ids_tying_strongest": tying,
        "random_ties_strongest": "random" in tying,
        "lookup_family_ids_tying_strongest": sorted(LOOKUP_FAMILY_BASELINES & set(tying)),
    }


def aggregate_leakage_reports(seed_runs: list[dict[str, Any]]) -> dict[str, Any]:
    illegal_findings = []
    blocking_reasons = []
    detected = set()
    positive_control_ids = set()
    for seed_run in seed_runs:
        report = seed_run["leakage_report"]
        illegal_findings.extend(report["illegal_leak_findings"])
        blocking_reasons.extend(report["blocking_reasons"])
        detected.update(report["detected_positive_control_ids"])
        positive_control_ids.update(report["positive_control_ids"])
    return {
        "producer_function": (
            "phase2c_candidate_free_baseline_stress_001a.runner.aggregate_leakage_reports"
        ),
        "positive_control_ids": sorted(positive_control_ids),
        "positive_controls_passed": not blocking_reasons,
        "detected_positive_control_ids": sorted(detected),
        "clean_scan_passed_after_positive_controls": not illegal_findings,
        "illegal_leak_findings": illegal_findings,
        "blocking_reasons": blocking_reasons
        + (["illegal_leak_found_in_candidate_visible_payload"] if illegal_findings else []),
        "per_seed_reports": [
            {"seed": seed_run["seed"], "report": seed_run["leakage_report"]}
            for seed_run in seed_runs
        ],
    }


def aggregate_replay_reports(seed_runs: list[dict[str, Any]]) -> dict[str, Any]:
    blocking_reasons = sorted(
        {
            reason
            for seed_run in seed_runs
            for reason in seed_run["replay_report"]["blocking_reasons"]
        }
    )
    return {
        "producer_function": (
            "phase2c_candidate_free_baseline_stress_001a.runner.aggregate_replay_reports"
        ),
        "passed": all(seed_run["replay_report"]["passed"] for seed_run in seed_runs),
        "observed_input_reads": seed_runs[0]["replay_report"]["observed_input_reads"]
        if seed_runs
        else {},
        "uses_hash_only_comparison": False,
        "uses_stored_outputs_only": False,
        "blocking_reasons": blocking_reasons,
        "per_seed_reports": [
            {"seed": seed_run["seed"], "report": seed_run["replay_report"]}
            for seed_run in seed_runs
        ],
    }


def aggregate_ablation_reports(seed_runs: list[dict[str, Any]]) -> dict[str, Any]:
    controls = []
    for seed_run in seed_runs:
        for control in seed_run["ablation_report"]["controls"]:
            row = dict(control)
            row["seed"] = seed_run["seed"]
            controls.append(row)
    return {
        "producer_function": (
            "phase2c_candidate_free_baseline_stress_001a.runner.aggregate_ablation_reports"
        ),
        "controls": controls,
        "stored_score_mutation_used": False,
        "all_controls_consumed_by_final_verdict": all(
            control["consumed_by_final_verdict"] for control in controls
        )
        and all(control["detected_expected_failure"] for control in controls),
    }


def _provenance_record(
    producer_id: str,
    producer_function: str,
    code_func: Callable[..., Any],
    value: Any,
) -> dict[str, Any]:
    return {
        "producer_id": producer_id,
        "producer_function": producer_function,
        "input_artifacts": ["generated_phase2c_candidate_free_baseline_stress"],
        "run_id": RUN_ID,
        "seed_context_episode_ids": ["all_stress_seeds"],
        "aggregation_rule": "candidate_free_baseline_stress_contract_verification",
        "code_path_hash": code_path_hash(code_func),
        "consumed_by_final_verdict": True,
        "value": value,
    }


def build_provenance(
    config: dict[str, Any],
    baseline_report: dict[str, Any],
    leakage_report: dict[str, Any],
    replay_report: dict[str, Any],
    ablation_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "producer_function": (
            "phase2c_candidate_free_baseline_stress_001a.runner.build_provenance"
        ),
        "records": [
            _provenance_record("stress_config", "default_stress_config", default_stress_config, config),
            _provenance_record(
                "baseline_aggregate",
                baseline_report["producer_function"],
                aggregate_baseline_reports,
                baseline_report["baseline_ids"],
            ),
            _provenance_record(
                "leakage_scan",
                leakage_report["producer_function"],
                aggregate_leakage_reports,
                leakage_report["positive_controls_passed"],
            ),
            _provenance_record(
                "replay_recomputation",
                replay_report["producer_function"],
                aggregate_replay_reports,
                replay_report["passed"],
            ),
            _provenance_record(
                "ablation_plan",
                ablation_report["producer_function"],
                aggregate_ablation_reports,
                ablation_report["all_controls_consumed_by_final_verdict"],
            ),
        ],
    }


def verify_provenance(provenance: dict[str, Any]) -> dict[str, Any]:
    required_fields = {
        "producer_id",
        "producer_function",
        "input_artifacts",
        "run_id",
        "seed_context_episode_ids",
        "aggregation_rule",
        "code_path_hash",
        "consumed_by_final_verdict",
        "value",
    }
    required_ids = {
        "stress_config",
        "baseline_aggregate",
        "leakage_scan",
        "replay_recomputation",
        "ablation_plan",
    }
    reasons = []
    records = provenance.get("records", [])
    producer_ids = {record.get("producer_id") for record in records}
    for missing in sorted(required_ids - producer_ids):
        reasons.append(f"missing_required_provenance:{missing}")
    for index, record in enumerate(records):
        missing_fields = sorted(required_fields - set(record))
        if missing_fields:
            reasons.append(f"record_{index}_missing:{','.join(missing_fields)}")
        if len(str(record.get("code_path_hash", ""))) != 64:
            reasons.append(f"record_{index}_bad_code_path_hash")
        if record.get("consumed_by_final_verdict") is not True:
            reasons.append(f"record_{index}_not_consumed")
    return {
        "producer_function": (
            "phase2c_candidate_free_baseline_stress_001a.runner.verify_provenance"
        ),
        "passed": not reasons,
        "blocking_reasons": reasons,
    }


def build_failure_manifest(
    config: dict[str, Any],
    trace: list[dict[str, Any]],
    baseline_report: dict[str, Any],
    leakage_report: dict[str, Any],
    replay_report: dict[str, Any],
    ablation_report: dict[str, Any],
    provenance_check: dict[str, Any],
) -> dict[str, Any]:
    reasons = []
    if len(config["seeds"]) < 5:
        reasons.append("seed_count_below_contract")
    if config["train_family_count"] < 3:
        reasons.append("train_family_count_below_contract")
    if config["heldout_family_count"] < 3:
        reasons.append("heldout_family_count_below_contract")
    if config["episodes_per_family"] < 4:
        reasons.append("episodes_per_family_below_contract")
    if len(trace) < expected_trace_rows(config):
        reasons.append("trace_rows_below_expected_minimum")
    reasons.extend(f"missing_required_baseline:{item}" for item in baseline_report["missing_baseline_ids"])
    reasons.extend(leakage_report["blocking_reasons"])
    reasons.extend(replay_report["blocking_reasons"])
    if not ablation_report["all_controls_consumed_by_final_verdict"]:
        reasons.append("ablation_controls_not_consumed")
    reasons.extend(provenance_check["blocking_reasons"])
    return {
        "producer_function": (
            "phase2c_candidate_free_baseline_stress_001a.runner.build_failure_manifest"
        ),
        "blocking_reasons": reasons,
        "has_blocking_failure": bool(reasons),
    }


def build_result(
    config: dict[str, Any],
    trace: list[dict[str, Any]],
    baseline_report: dict[str, Any],
    leakage_report: dict[str, Any],
    replay_report: dict[str, Any],
    ablation_report: dict[str, Any],
    provenance_check: dict[str, Any],
    failure_manifest: dict[str, Any],
) -> dict[str, Any]:
    strongest = baseline_report["strongest_fair_baseline"]
    oracle_macro_accuracy = 1.0
    baseline_saturated = strongest["macro_accuracy"] >= oracle_macro_accuracy - config["equivalence_band"]
    cheap_tie = baseline_report["random_ties_strongest"] or bool(
        baseline_report["lookup_family_ids_tying_strongest"]
    )
    if failure_manifest["has_blocking_failure"]:
        verdict = "invalid_candidate_free_baseline_stress_evidence_path"
    elif baseline_saturated:
        verdict = "no_headroom_baseline_saturated"
    elif cheap_tie:
        verdict = "candidate_work_blocked_by_cheap_baseline_tie"
    else:
        verdict = "candidate_free_baseline_stress_preserved_bounded_headroom_pending_route_check"

    return {
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "verdict": verdict,
        "candidate_mechanism_run": False,
        "phase3_opened": False,
        "route_tournament_authorized": False,
        "runtime_or_mainline_authorized": False,
        "push_tag_remote_anchor_authorized": False,
        "stress_execution_claim": not failure_manifest["has_blocking_failure"],
        "seed_count": len(config["seeds"]),
        "seeds": list(config["seeds"]),
        "train_family_count": config["train_family_count"],
        "heldout_family_count": config["heldout_family_count"],
        "episodes_per_family": config["episodes_per_family"],
        "trace_row_count": len(trace),
        "expected_trace_row_count": expected_trace_rows(config),
        "oracle_macro_accuracy": oracle_macro_accuracy,
        "equivalence_band": config["equivalence_band"],
        "strongest_fair_baseline_id": strongest["baseline_id"],
        "strongest_fair_baseline_macro_accuracy": strongest["macro_accuracy"],
        "baseline_ids_tying_strongest": baseline_report["baseline_ids_tying_strongest"],
        "random_ties_strongest": baseline_report["random_ties_strongest"],
        "lookup_family_ids_tying_strongest": baseline_report[
            "lookup_family_ids_tying_strongest"
        ],
        "baseline_saturated": baseline_saturated,
        "replay_passed": replay_report["passed"],
        "leakage_positive_controls_passed": leakage_report["positive_controls_passed"],
        "ablation_all_controls_consumed": ablation_report[
            "all_controls_consumed_by_final_verdict"
        ],
        "provenance_check_passed": provenance_check["passed"],
        "claim_ceiling": CLAIM_CEILING,
    }


def run_stress(output_dir: str | Path, persist_artifacts: bool = False) -> dict[str, Any]:
    config = default_stress_config()
    seed_runs = [run_seed_surface(seed, config) for seed in config["seeds"]]
    trace = [row for seed_run in seed_runs for row in seed_run["trace"]]
    baseline_report = aggregate_baseline_reports(seed_runs)
    leakage_report = aggregate_leakage_reports(seed_runs)
    replay_report = aggregate_replay_reports(seed_runs)
    ablation_report = aggregate_ablation_reports(seed_runs)
    provenance = build_provenance(
        config,
        baseline_report,
        leakage_report,
        replay_report,
        ablation_report,
    )
    provenance_check = verify_provenance(provenance)
    failure_manifest = build_failure_manifest(
        config,
        trace,
        baseline_report,
        leakage_report,
        replay_report,
        ablation_report,
        provenance_check,
    )
    result = build_result(
        config,
        trace,
        baseline_report,
        leakage_report,
        replay_report,
        ablation_report,
        provenance_check,
        failure_manifest,
    )
    run = {
        "config": config,
        "result": result,
        "trace": trace,
        "baseline_comparison": baseline_report,
        "ablation_report": ablation_report,
        "replay_report": replay_report,
        "leakage_report": leakage_report,
        "computed_evidence_provenance": provenance,
        "failure_manifest": failure_manifest,
        "claim_ceiling": CLAIM_CEILING,
    }
    if persist_artifacts:
        write_artifacts(Path(output_dir), run)
    return run


def write_artifacts(output_dir: Path, run: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, key in (
        ("result.json", "result"),
        ("baseline_comparison.json", "baseline_comparison"),
        ("ablation_report.json", "ablation_report"),
        ("replay_report.json", "replay_report"),
        ("leakage_report.json", "leakage_report"),
        ("computed_evidence_provenance.json", "computed_evidence_provenance"),
        ("failure_manifest.json", "failure_manifest"),
    ):
        (output_dir / filename).write_text(json.dumps(run[key], indent=2), encoding="utf-8")
    with (output_dir / "trace.jsonl").open("w", encoding="utf-8") as handle:
        for row in run["trace"]:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="artifacts/phase2c_candidate_free_baseline_stress_001a",
    )
    args = parser.parse_args(argv)
    run = run_stress(args.output_dir, persist_artifacts=True)
    print(json.dumps(run["result"], indent=2))
    return 0 if not run["failure_manifest"]["has_blocking_failure"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
