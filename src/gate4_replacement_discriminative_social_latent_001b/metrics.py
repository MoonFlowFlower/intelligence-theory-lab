from __future__ import annotations

from collections import defaultdict
from typing import Any

from .baselines import ORDINARY_BASELINES


PASS_VERDICT = "gate4_replacement_discriminative_social_latent_implementation_001b_pass"
NEGATIVE_VERDICT = "gate4_replacement_discriminative_social_latent_implementation_001b_negative_evidence"


def summarize_candidate(candidate_rows: list[dict[str, Any]]) -> dict[str, Any]:
    per_split = {}
    per_seed = {}
    for split in sorted({row["split_family"] for row in candidate_rows}):
        rows = [row for row in candidate_rows if row["split_family"] == split]
        per_split[split] = sum(row["score"] for row in rows) / len(rows)
    for seed in sorted({row["seed_id"] for row in candidate_rows}):
        rows = [row for row in candidate_rows if row["seed_id"] == seed]
        per_seed[seed] = sum(row["score"] for row in rows) / len(rows)
    return {
        "producer_function": "summarize_candidate",
        "score": sum(row["score"] for row in candidate_rows) / len(candidate_rows),
        "per_split": per_split,
        "per_seed": per_seed,
        "rows": candidate_rows,
    }


def select_strongest_baselines(baseline_results: dict[str, Any]) -> dict[str, Any]:
    ordinary = {key: value for key, value in baseline_results.items() if key in ORDINARY_BASELINES}
    aggregate_id, aggregate = max(ordinary.items(), key=lambda item: item[1]["score"])
    split_rows = {}
    split_names = sorted({split for result in ordinary.values() for split in result["per_split"]})
    for split in split_names:
        baseline_id, result = max(ordinary.items(), key=lambda item: item[1]["per_split"].get(split, -1.0))
        split_rows[split] = {"baseline_id": baseline_id, "score": result["per_split"][split]}
    return {
        "producer_function": "select_strongest_baselines",
        "aggregate": {
            "baseline_id": aggregate_id,
            "score": aggregate["score"],
            "computed_from_scores": {"baseline_id": aggregate_id, "score": aggregate["score"]},
        },
        "per_split": split_rows,
    }


def compute_margins(candidate_summary: dict[str, Any], strongest: dict[str, Any]) -> dict[str, Any]:
    per_split = {
        split: candidate_summary["per_split"][split] - strongest["per_split"][split]["score"]
        for split in candidate_summary["per_split"]
    }
    return {
        "producer_function": "compute_margins",
        "aggregate_margin": candidate_summary["score"] - strongest["aggregate"]["score"],
        "per_split_margins": per_split,
    }


def seed_margins(candidate_rows: list[dict[str, Any]], baseline_results: dict[str, Any]) -> dict[str, float]:
    margins = {}
    by_seed: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in candidate_rows:
        by_seed[row["seed_id"]].append(row)
    for seed, rows in by_seed.items():
        candidate_score = sum(row["score"] for row in rows) / len(rows)
        baseline_seed_scores = []
        for baseline_id in ORDINARY_BASELINES:
            if baseline_id not in baseline_results:
                continue
            base_rows = [
                row
                for row in baseline_results[baseline_id]["rows"]
                if row["seed_id"] == seed
            ]
            baseline_seed_scores.append(sum(row["score"] for row in base_rows) / len(base_rows))
        margins[seed] = candidate_score - max(baseline_seed_scores)
    return margins


def active_query_seed_margins(candidate_rows: list[dict[str, Any]], baseline_results: dict[str, Any]) -> dict[str, float]:
    active_rows = [row for row in candidate_rows if row["split_family"] == "active_query_required_episodes"]
    margins = {}
    for seed in sorted({row["seed_id"] for row in active_rows}):
        c_rows = [row for row in active_rows if row["seed_id"] == seed]
        candidate_score = sum(row["score"] for row in c_rows) / len(c_rows)
        baseline_seed_scores = []
        for baseline_id in ORDINARY_BASELINES:
            if baseline_id not in baseline_results:
                continue
            b_rows = [
                row
                for row in baseline_results[baseline_id]["rows"]
                if row["seed_id"] == seed and row["split_family"] == "active_query_required_episodes"
            ]
            baseline_seed_scores.append(sum(row["score"] for row in b_rows) / len(b_rows))
        margins[seed] = candidate_score - max(baseline_seed_scores)
    return margins


def evaluate_thresholds(
    *,
    candidate_score: float,
    strongest_baseline_score: float,
    oracle_score: float,
    per_split_margins: dict[str, float],
    seed_margins: dict[str, float],
    active_query_seed_margins: dict[str, float],
    ablation_drops: dict[str, float],
    oracle_positive_control_passed: bool,
    budget_parity_passed: bool,
    leakage_passed: bool,
    replay_passed: bool,
    provenance_passed: bool,
    baseline_independence_passed: bool,
    split_coverage_passed: bool,
) -> dict[str, Any]:
    blocking = []
    if not oracle_positive_control_passed or oracle_score <= strongest_baseline_score:
        return {
            "producer_function": "evaluate_thresholds",
            "verdict": "harness_invalid_oracle_positive_control_failure",
            "positive_evidence_allowed": False,
            "blocking_reasons": ["oracle_positive_control_failed"],
        }
    if candidate_score <= strongest_baseline_score:
        blocking.append("candidate_tied_or_below_strongest_non_oracle_baseline")
    if candidate_score - strongest_baseline_score < 0.15:
        blocking.append("aggregate_margin_below_threshold")
    if any(margin < 0.10 for margin in per_split_margins.values()):
        blocking.append("critical_split_margin_below_threshold")
    if len(seed_margins) < 5 or sum(1 for value in seed_margins.values() if value >= 0.15) < 4:
        blocking.append("repeated_seed_rule_failed")
    if any(value < 0.0 for value in active_query_seed_margins.values()):
        blocking.append("active_query_seed_below_strongest_baseline")
    if ablation_drops.get("no_active_query", 0.0) < 0.20:
        blocking.append("no_active_query_drop_below_threshold")
    if ablation_drops.get("shuffled_feedback", 0.0) < 0.20:
        blocking.append("shuffled_feedback_drop_below_threshold")
    if ablation_drops.get("counterfactual_transition", 0.0) < 0.15:
        blocking.append("counterfactual_transition_drop_below_threshold")
    gate_checks = {
        "budget_parity_failed": budget_parity_passed,
        "leakage_failed": leakage_passed,
        "replay_failed": replay_passed,
        "computed_provenance_failed": provenance_passed,
        "baseline_independence_failed": baseline_independence_passed,
        "split_coverage_failed": split_coverage_passed,
    }
    blocking.extend(reason for reason, passed in gate_checks.items() if not passed)
    verdict = PASS_VERDICT if not blocking else NEGATIVE_VERDICT
    return {
        "producer_function": "evaluate_thresholds",
        "verdict": verdict,
        "positive_evidence_allowed": not blocking,
        "blocking_reasons": blocking,
        "candidate_score": candidate_score,
        "strongest_baseline_score": strongest_baseline_score,
        "oracle_score": oracle_score,
        "aggregate_margin": candidate_score - strongest_baseline_score,
        "per_split_margins": per_split_margins,
        "repeated_seed_result": {
            "seed_margins": seed_margins,
            "passing_seed_count": sum(1 for value in seed_margins.values() if value >= 0.15),
            "rule": "at least 5 seeds, at least 4/5 aggregate margin pass, no active-query seed below baseline",
        },
    }
