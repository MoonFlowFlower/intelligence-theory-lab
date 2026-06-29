from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

ALLOWED_VERDICTS = {
    "smoke_run_completed_replay_passed",
    "smoke_run_completed_replay_failed",
    "official_run_completed_replay_passed",
    "official_run_completed_replay_failed",
    "baseline_saturated_environment_needs_redesign",
    "oracle_no_headroom_benchmark_invalid",
    "invalid_due_graph_cache_leakage",
    "oracle_headroom_unresolved",
    "benchmark_objective_contract_invalid",
    "candidate_evidence_unknown",
    "discriminative_generator_smoke_ready",
    "still_baseline_saturated_environment_needs_redesign",
    "replay_failed_evidence_invalid",
    "audit_failed_evidence_invalid",
    "candidate_tuning_violation",
    "artifact_preservation_violation",
    "heldout_split_invalid",
    "candidate_factorial_signal_detected",
    "candidate_factorial_no_signal",
    "candidate_factorial_baseline_saturated",
    "candidate_factorial_ablation_noncausal",
}


def derive_report_verdict(
    manifest: Dict[str, Any],
    replay_report: Dict[str, Any],
    baseline_scores: Dict[str, Any],
    oracle_headroom_report: Dict[str, Any] | None = None,
    graph_cache_audit: Dict[str, Any] | None = None,
    generator_spec: Dict[str, Any] | None = None,
    graph_cache_saturation_report: Dict[str, Any] | None = None,
    candidate_source_hash_check: Dict[str, Any] | None = None,
) -> str:
    run_label = "smoke" if manifest.get("smoke") else "official"
    generator_enabled = bool(manifest.get("task_family_generator_001c_enabled") or generator_spec)
    if replay_report.get("verdict") == "replay_failed_evidence_invalid":
        if generator_enabled:
            return "replay_failed_evidence_invalid"
        return f"{run_label}_run_completed_replay_failed"
    if graph_cache_audit and graph_cache_audit.get("verdict") != "graph_cache_access_contract_ok":
        if generator_enabled:
            return "audit_failed_evidence_invalid"
        return "invalid_due_graph_cache_leakage"
    if candidate_source_hash_check and candidate_source_hash_check.get("verdict") != "candidate_source_unchanged":
        return "candidate_tuning_violation"
    if oracle_headroom_report and not oracle_headroom_report.get("aggregate", {}).get("oracle_upper_bound_valid", False):
        if generator_enabled:
            return "oracle_no_headroom_benchmark_invalid"
        return "oracle_headroom_unresolved"
    if generator_spec and generator_spec.get("heldout_overlap_with_smoke"):
        return "heldout_split_invalid"
    if graph_cache_saturation_report and graph_cache_saturation_report.get("too_many_saturated"):
        return "still_baseline_saturated_environment_needs_redesign"
    if generator_enabled:
        return "discriminative_generator_smoke_ready"
    if _oracle_has_no_headroom(baseline_scores):
        return "oracle_no_headroom_benchmark_invalid"
    if _baseline_saturated(baseline_scores):
        return "baseline_saturated_environment_needs_redesign"
    if replay_report.get("verdict") == "replay_succeeded":
        return f"{run_label}_run_completed_replay_passed"
    return "candidate_evidence_unknown"


def write_report(
    path: str | Path,
    manifest: Dict[str, Any],
    replay_report: Dict[str, Any],
    baseline_scores: Dict[str, Any],
    oracle_headroom_report: Dict[str, Any] | None = None,
    graph_cache_audit: Dict[str, Any] | None = None,
    generator_spec: Dict[str, Any] | None = None,
    graph_cache_saturation_report: Dict[str, Any] | None = None,
    candidate_source_hash_check: Dict[str, Any] | None = None,
) -> str:
    verdict = derive_report_verdict(
        manifest,
        replay_report,
        baseline_scores,
        oracle_headroom_report,
        graph_cache_audit,
        generator_spec,
        graph_cache_saturation_report,
        candidate_source_hash_check,
    )
    title = "ITL-DEV-BENCH-001C Report" if manifest.get("task_family_generator_001c_enabled") else "ITL-DEV-BENCH-001A Report"
    lines = [
        f"# {title}",
        "",
        f"Verdict: {verdict}",
        "Verdict source: itl_devbench.eval.report.derive_report_verdict",
        "Metric source: metrics.json",
        "Replay source: replay_report.json",
        "",
        "Scope: benchmark generator, oracle headroom, replay, and baseline discrimination scaffold.",
        "Claim ceiling: benchmark-discrimination repair only; candidate evidence unknown.",
        "",
        f"Run id: {manifest.get('run_id')}",
        f"Config hash: {manifest.get('config_hash')}",
        f"Metrics hash: {manifest.get('metrics_hash')}",
        f"Replay verdict: {replay_report.get('verdict')}",
        f"Oracle headroom aggregate valid: {oracle_headroom_report.get('aggregate', {}).get('oracle_upper_bound_valid') if oracle_headroom_report else 'not_available'}",
        f"Graph-cache audit verdict: {graph_cache_audit.get('verdict') if graph_cache_audit else 'not_available'}",
        f"Candidate source hash check: {candidate_source_hash_check.get('verdict') if candidate_source_hash_check else 'not_available'}",
        f"Graph-cache saturation verdict: {graph_cache_saturation_report.get('verdict') if graph_cache_saturation_report else 'not_available'}",
        f"Held-out overlap count: {len(generator_spec.get('heldout_overlap_with_smoke', [])) if generator_spec else 'not_available'}",
        "",
        "Baseline and candidate aggregates are stored in baseline_scores.json.",
        "By-stage baseline aggregates are stored in baseline_scores_by_stage.json.",
        "By-family baseline aggregates are stored in baseline_scores_by_family.json when 001C is enabled.",
        "By-dimension baseline aggregates are stored in baseline_scores_by_dimension.json when 001C is enabled.",
        "Family discrimination metrics are stored in family_metric_summary.json when 001C is enabled.",
        "Graph-cache saturation checks are stored in graph_cache_saturation_report.json when 001C is enabled.",
        "Oracle headroom checks are stored in oracle_headroom_report.json.",
        "Graph-cache access audit is stored in leakage_audit_graph_cache.json.",
        "Machine-readable metrics are stored in metrics.json.",
        "Evidence unknown beyond this bounded offline scaffold.",
    ]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return verdict


def _oracle_has_no_headroom(baseline_scores: Dict[str, Any]) -> bool:
    oracle = next((row for row in baseline_scores.get("scores", []) if row["agent_id"] == "oracle"), None)
    if oracle is None:
        return False
    non_oracles = [row for row in baseline_scores.get("scores", []) if row["agent_id"] != "oracle"]
    if not non_oracles:
        return False
    best_non_oracle = max(row["mean_total_reward"] for row in non_oracles)
    return float(oracle["mean_total_reward"]) <= float(best_non_oracle)


def _baseline_saturated(baseline_scores: Dict[str, Any]) -> bool:
    candidates = [row for row in baseline_scores.get("scores", []) if row["agent_kind"] == "candidate"]
    baselines = [row for row in baseline_scores.get("scores", []) if row["agent_kind"] == "baseline"]
    if not candidates or not baselines:
        return False
    return max(row["mean_total_reward"] for row in baselines) >= max(row["mean_total_reward"] for row in candidates)
