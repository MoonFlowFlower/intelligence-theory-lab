from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict

from itl_devbench.core.hashing import sha256_file, sha256_json
from itl_devbench.eval.audit import audit_manifest
from itl_devbench.eval.run_matrix import REQUIRED_BASELINES, REQUIRED_MINIMAL_LOOP_VARIANTS, load_config, run_benchmark

ALLOWED_001D_VERDICTS = {
    "candidate_factorial_signal_detected",
    "candidate_factorial_no_signal",
    "candidate_factorial_baseline_saturated",
    "candidate_factorial_ablation_noncausal",
    "replay_failed_evidence_invalid",
    "audit_failed_evidence_invalid",
    "candidate_tuning_violation",
}

PROTECTED_SOURCE_PATHS = [
    "src/itl_devbench/agents/minimal_loop.py",
    "src/itl_devbench/envs/developmental_grid.py",
    "src/itl_devbench/envs/task_family_generator.py",
    "src/itl_devbench/envs/families.py",
    "src/itl_devbench/agents/random_policy.py",
    "src/itl_devbench/agents/obs_only_policy.py",
    "src/itl_devbench/agents/generic_fsm.py",
    "src/itl_devbench/agents/graph_cache.py",
    "src/itl_devbench/agents/oracle.py",
]


def run_candidate_factorial(
    config: Dict[str, Any],
    smoke: bool = True,
    output_root: str | Path = Path("artifacts") / "ITL-DEV-BENCH-001A",
    command_line: list[str] | None = None,
    reference_manifest: str | Path = Path("artifacts")
    / "ITL-DEV-BENCH-001A"
    / "RUN_20260629T161147Z"
    / "manifest.json",
) -> Path:
    config = dict(config)
    config["task_id"] = "ITL-DEV-BENCH-001D"
    generator_cfg = dict(config.get("task_family_generator_001c", {}))
    generator_cfg["enabled"] = True
    config["task_family_generator_001c"] = generator_cfg

    reference_manifest_path = Path(reference_manifest)
    reference = json.loads(reference_manifest_path.read_text(encoding="utf-8")) if reference_manifest_path.exists() else {}
    protected_before = _protected_hashes_from_reference(reference)

    run_dir = run_benchmark(config=config, smoke=smoke, output_root=output_root, command_line=command_line or sys.argv)
    metrics = _read_json(run_dir / "metrics.json")
    baseline_scores_by_family = _read_json(run_dir / "baseline_scores_by_family.json")
    baseline_scores_by_dimension = _read_json(run_dir / "baseline_scores_by_dimension.json")
    family_summary = _read_json(run_dir / "family_metric_summary.json")
    replay_report = _read_json(run_dir / "replay_report.json")
    audit_report = _read_json(run_dir / "audit_report.json")

    candidate_scores = compute_candidate_factorial_scores_by_family(metrics, baseline_scores_by_family)
    interactions = compute_candidate_factorial_interactions(candidate_scores)
    baseline_comparison = compute_baseline_comparison_by_family(candidate_scores, family_summary)
    source_check = compute_source_hash_check_001d(protected_before)
    verdict = derive_candidate_factorial_verdict(
        replay_report,
        audit_report,
        source_check,
        baseline_comparison,
        interactions,
    )

    candidate_scores_path = run_dir / "candidate_factorial_scores_by_family.json"
    interactions_path = run_dir / "candidate_factorial_interactions.json"
    baseline_comparison_path = run_dir / "baseline_comparison_by_family.json"
    source_check_path = run_dir / "source_hash_check_001d.json"
    _write_json(candidate_scores_path, candidate_scores)
    _write_json(interactions_path, interactions)
    _write_json(baseline_comparison_path, baseline_comparison)
    _write_json(source_check_path, source_check)

    manifest_path = run_dir / "manifest.json"
    manifest = _read_json(manifest_path)
    manifest.update(
        {
            "task_id": "ITL-DEV-BENCH-001D",
            "candidate_factorial_scores_by_family_path": "candidate_factorial_scores_by_family.json",
            "candidate_factorial_interactions_path": "candidate_factorial_interactions.json",
            "baseline_comparison_by_family_path": "baseline_comparison_by_family.json",
            "source_hash_check_001d_path": "source_hash_check_001d.json",
            "baseline_scores_by_dimension_path": "baseline_scores_by_dimension.json",
            "candidate_factorial_verdict_source": "itl_devbench.eval.candidate_factorial.derive_candidate_factorial_verdict",
            "reference_001c_manifest_path": str(reference_manifest_path),
            "report_verdict": verdict,
        }
    )
    _write_json(manifest_path, manifest)
    write_candidate_factorial_report(run_dir / "report.md", manifest, replay_report, audit_report, source_check, baseline_comparison, interactions)
    audit_report = audit_manifest(manifest_path)
    if audit_report.get("verdict") != "audit_succeeded":
        verdict = derive_candidate_factorial_verdict(
            replay_report,
            audit_report,
            source_check,
            baseline_comparison,
            interactions,
        )
        manifest["report_verdict"] = verdict
        _write_json(manifest_path, manifest)
        write_candidate_factorial_report(
            run_dir / "report.md",
            manifest,
            replay_report,
            audit_report,
            source_check,
            baseline_comparison,
            interactions,
        )
        audit_report = audit_manifest(manifest_path)
    if audit_report.get("verdict") == "audit_succeeded":
        final_verdict = derive_candidate_factorial_verdict(
            replay_report,
            audit_report,
            source_check,
            baseline_comparison,
            interactions,
        )
        if manifest.get("report_verdict") != final_verdict:
            manifest["report_verdict"] = final_verdict
            _write_json(manifest_path, manifest)
            write_candidate_factorial_report(
                run_dir / "report.md",
                manifest,
                replay_report,
                audit_report,
                source_check,
                baseline_comparison,
                interactions,
            )
            audit_report = audit_manifest(manifest_path)

    _refresh_latest(run_dir, Path(output_root) / "latest")
    return run_dir


def compute_candidate_factorial_scores_by_family(
    metrics: Dict[str, Any],
    baseline_scores_by_family: Dict[str, Any],
) -> Dict[str, Any]:
    rows_by_family: dict[str, list[Dict[str, Any]]] = {}
    for row in baseline_scores_by_family.get("scores", []):
        rows_by_family.setdefault(str(row["family_id"]), []).append(row)

    families = []
    for family_id, rows in sorted(rows_by_family.items()):
        variant_scores = {
            str(row["variant"]): float(row["mean_total_reward"])
            for row in rows
            if row["agent_id"] == "minimal_loop"
        }
        families.append(
            {
                "producer_function": "itl_devbench.eval.candidate_factorial.compute_candidate_factorial_scores_by_family",
                "family_id": family_id,
                "variant_scores": variant_scores,
                "variant_episode_counts": {
                    str(row["variant"]): int(row["episode_count"])
                    for row in rows
                    if row["agent_id"] == "minimal_loop"
                },
                "all_required_variants_present": set(variant_scores) == set(REQUIRED_MINIMAL_LOOP_VARIANTS),
            }
        )

    aggregate_scores = {
        variant: _mean(
            row["variant_scores"][variant]
            for row in families
            if variant in row["variant_scores"]
        )
        for variant in REQUIRED_MINIMAL_LOOP_VARIANTS
    }
    result = {
        "producer_function": "itl_devbench.eval.candidate_factorial.compute_candidate_factorial_scores_by_family",
        "input_artifacts": list(metrics.get("input_artifacts", [])) + ["baseline_scores_by_family.json"],
        "families": families,
        "aggregate": {
            "variant_scores": aggregate_scores,
            "all_required_variants_present": all(row["all_required_variants_present"] for row in families),
        },
        "code_path_hash": sha256_file(Path(__file__)),
    }
    result["report_hash"] = sha256_json(result)
    return result


def compute_candidate_factorial_interactions(candidate_scores: Dict[str, Any]) -> Dict[str, Any]:
    by_family = []
    for row in candidate_scores.get("families", []):
        scores = {str(key): float(value) for key, value in row.get("variant_scores", {}).items()}
        interaction = _interaction_row(str(row["family_id"]), scores)
        by_family.append(interaction)

    interaction_keys = [
        "pe_marginal_under_memory_planning",
        "memory_marginal_under_pe_planning",
        "planner_read_marginal_under_pe_memory",
        "three_way_closure_gain",
    ]
    aggregate_row = {
        key: _mean(row[key] for row in by_family)
        for key in interaction_keys
    }
    result = {
        "producer_function": "itl_devbench.eval.candidate_factorial.compute_candidate_factorial_interactions",
        "by_family": by_family,
        "aggregate": {
            **{f"{key}_mean": value for key, value in aggregate_row.items()},
            "positive_three_way_family_count": sum(1 for row in by_family if row["three_way_closure_gain"] > 0.0),
            "positive_any_marginal_family_count": sum(
                1
                for row in by_family
                if max(
                    row["pe_marginal_under_memory_planning"],
                    row["memory_marginal_under_pe_planning"],
                    row["planner_read_marginal_under_pe_memory"],
                )
                > 0.0
            ),
        },
        "code_path_hash": sha256_file(Path(__file__)),
    }
    result["report_hash"] = sha256_json(result)
    return result


def compute_baseline_comparison_by_family(
    candidate_scores: Dict[str, Any],
    family_metric_summary: Dict[str, Any],
) -> Dict[str, Any]:
    family_summary = {row["family_id"]: row for row in family_metric_summary.get("families", [])}
    rows = []
    for candidate_row in candidate_scores.get("families", []):
        family_id = candidate_row["family_id"]
        summary = family_summary.get(family_id, {})
        variant_scores = candidate_row["variant_scores"]
        best_variant = max(variant_scores, key=lambda variant: variant_scores[variant])
        best_candidate_score = float(variant_scores[best_variant])
        baselines = {
            "random_policy": summary.get("random_score"),
            "obs_only_policy": summary.get("obs_only_score"),
            "generic_fsm": summary.get("generic_fsm_score"),
            "graph_cache": summary.get("graph_cache_score"),
        }
        best_baseline_name, best_baseline_score = _best_named_score(baselines)
        oracle_score = summary.get("oracle_score")
        baseline_saturated = best_baseline_score is not None and best_baseline_score >= best_candidate_score
        rows.append(
            {
                "producer_function": "itl_devbench.eval.candidate_factorial.compute_baseline_comparison_by_family",
                "family_id": family_id,
                "best_candidate_variant": best_variant,
                "best_candidate_score": best_candidate_score,
                "best_baseline": best_baseline_name,
                "best_baseline_score": best_baseline_score,
                "oracle_score": oracle_score,
                "candidate_gap_to_oracle": None if oracle_score is None else float(oracle_score) - best_candidate_score,
                "baseline_saturated": baseline_saturated,
                "baseline_scores": baselines,
            }
        )
    aggregate = {
        "baseline_saturated_family_count": sum(1 for row in rows if row["baseline_saturated"]),
        "family_count": len(rows),
    }
    aggregate["baseline_saturated"] = aggregate["baseline_saturated_family_count"] > 0
    result = {
        "producer_function": "itl_devbench.eval.candidate_factorial.compute_baseline_comparison_by_family",
        "families": rows,
        "aggregate": aggregate,
        "code_path_hash": sha256_file(Path(__file__)),
    }
    result["report_hash"] = sha256_json(result)
    return result


def compute_source_hash_check_001d(protected_before: Dict[str, str]) -> Dict[str, Any]:
    protected_after = {path: sha256_file(path) for path in PROTECTED_SOURCE_PATHS}
    comparisons = {
        path: {
            "before_sha256": protected_before.get(path),
            "after_sha256": protected_after.get(path),
            "unchanged": protected_before.get(path) == protected_after.get(path),
        }
        for path in PROTECTED_SOURCE_PATHS
    }
    eval_hashes = {
        str(path.as_posix()): sha256_file(path)
        for path in sorted((Path("src") / "itl_devbench" / "eval").glob("*.py"))
    }
    candidate_unchanged = comparisons["src/itl_devbench/agents/minimal_loop.py"]["unchanged"]
    protected_unchanged = all(item["unchanged"] for item in comparisons.values())
    return {
        "producer_function": "itl_devbench.eval.candidate_factorial.compute_source_hash_check_001d",
        "protected_sources": comparisons,
        "eval_source_hashes": eval_hashes,
        "candidate_source_unchanged": candidate_unchanged,
        "protected_sources_unchanged": protected_unchanged,
        "verdict": "candidate_source_unchanged" if candidate_unchanged and protected_unchanged else "candidate_tuning_violation",
        "code_path_hash": sha256_file(Path(__file__)),
    }


def derive_candidate_factorial_verdict(
    replay_report: Dict[str, Any],
    audit_report: Dict[str, Any],
    source_check: Dict[str, Any],
    baseline_comparison: Dict[str, Any],
    interactions: Dict[str, Any],
) -> str:
    if replay_report.get("verdict") == "replay_failed_evidence_invalid":
        return "replay_failed_evidence_invalid"
    if audit_report.get("verdict") not in {None, "audit_succeeded"}:
        return "audit_failed_evidence_invalid"
    if not source_check.get("candidate_source_unchanged") or source_check.get("protected_sources_unchanged") is False:
        return "candidate_tuning_violation"
    if baseline_comparison.get("aggregate", {}).get("baseline_saturated"):
        return "candidate_factorial_baseline_saturated"
    aggregate = interactions.get("aggregate", {})
    if int(aggregate.get("positive_three_way_family_count", 0)) > 0:
        return "candidate_factorial_signal_detected"
    if float(aggregate.get("three_way_closure_gain_mean", 0.0)) < 0.0:
        return "candidate_factorial_ablation_noncausal"
    return "candidate_factorial_no_signal"


def write_candidate_factorial_report(
    path: str | Path,
    manifest: Dict[str, Any],
    replay_report: Dict[str, Any],
    audit_report: Dict[str, Any],
    source_check: Dict[str, Any],
    baseline_comparison: Dict[str, Any],
    interactions: Dict[str, Any],
) -> None:
    verdict = manifest.get("report_verdict")
    lines = [
        "# ITL-DEV-BENCH-001D Report",
        "",
        f"Verdict: {verdict}",
        "Verdict source: itl_devbench.eval.candidate_factorial.derive_candidate_factorial_verdict",
        "Metric source: metrics.json",
        "Replay source: replay_report.json",
        "",
        "Scope: frozen candidate factorial evaluation under the 001C trace/replay contract.",
        "Claim ceiling: candidate factorial evidence only under the specified offline contract.",
        "",
        f"Run id: {manifest.get('run_id')}",
        f"Config hash: {manifest.get('config_hash')}",
        f"Metrics hash: {manifest.get('metrics_hash')}",
        f"Replay verdict: {replay_report.get('verdict')}",
        f"Audit verdict: {audit_report.get('verdict')}",
        f"Source hash check: {source_check.get('verdict')}",
        f"Baseline saturated families: {baseline_comparison.get('aggregate', {}).get('baseline_saturated_family_count')}",
        f"Positive three-way families: {interactions.get('aggregate', {}).get('positive_three_way_family_count')}",
        "",
        "Candidate factorial scores are stored in candidate_factorial_scores_by_family.json.",
        "Candidate factorial interactions are stored in candidate_factorial_interactions.json.",
        "Baseline comparisons are stored in baseline_comparison_by_family.json.",
        "By-dimension baseline aggregates are stored in baseline_scores_by_dimension.json.",
        "Oracle headroom checks are stored in oracle_headroom_report.json.",
        "Graph-cache access audit is stored in leakage_audit_graph_cache.json.",
        "Machine-readable metrics are stored in metrics.json.",
        "Evidence unknown beyond this bounded offline evaluation.",
    ]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _interaction_row(family_id: str, scores: Dict[str, float]) -> Dict[str, Any]:
    return {"family_id": family_id, **_interaction_values(scores)}


def _interaction_values(scores: Dict[str, float]) -> Dict[str, float]:
    required = ["011", "101", "110", "111"]
    missing = [variant for variant in required if variant not in scores]
    if missing:
        raise ValueError(f"missing_required_interaction_variants:{missing}")
    return {
        "pe_marginal_under_memory_planning": scores["111"] - scores["011"],
        "memory_marginal_under_pe_planning": scores["111"] - scores["101"],
        "planner_read_marginal_under_pe_memory": scores["111"] - scores["110"],
        "three_way_closure_gain": scores["111"] - max(scores["110"], scores["101"], scores["011"]),
    }


def _protected_hashes_from_reference(reference: Dict[str, Any]) -> Dict[str, str]:
    source_hashes = reference.get("source_file_hashes", {})
    if source_hashes:
        return {path: str(source_hashes.get(path, "")) for path in PROTECTED_SOURCE_PATHS}
    return {path: sha256_file(path) for path in PROTECTED_SOURCE_PATHS}


def _best_named_score(scores: Dict[str, Any]) -> tuple[str | None, float | None]:
    available = {name: float(value) for name, value in scores.items() if value is not None}
    if not available:
        return None, None
    name = max(available, key=lambda key: available[key])
    return name, available[name]


def _mean(values: Any) -> float:
    materialized = list(values)
    return sum(float(value) for value in materialized) / len(materialized) if materialized else 0.0


def _read_json(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: Dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _refresh_latest(run_dir: Path, latest_dir: Path) -> None:
    if latest_dir.exists():
        shutil.rmtree(latest_dir)
    shutil.copytree(run_dir, latest_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--reference-manifest", default=str(Path("artifacts") / "ITL-DEV-BENCH-001A" / "RUN_20260629T161147Z" / "manifest.json"))
    args = parser.parse_args(argv)
    run_dir = run_candidate_factorial(
        config=load_config(args.config),
        smoke=args.smoke,
        command_line=sys.argv,
        reference_manifest=args.reference_manifest,
    )
    manifest = _read_json(run_dir / "manifest.json")
    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "manifest_path": str(run_dir / "manifest.json"),
                "trace_path": str(run_dir / manifest["trace_path"]),
                "replay_report_path": str(run_dir / manifest["replay_report_path"]),
                "audit_report_path": str(run_dir / manifest["audit_report_path"]),
                "candidate_factorial_scores_by_family_path": str(run_dir / manifest["candidate_factorial_scores_by_family_path"]),
                "candidate_factorial_interactions_path": str(run_dir / manifest["candidate_factorial_interactions_path"]),
                "baseline_comparison_by_family_path": str(run_dir / manifest["baseline_comparison_by_family_path"]),
                "report_path": str(run_dir / manifest["report_path"]),
                "report_verdict": manifest.get("report_verdict"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
