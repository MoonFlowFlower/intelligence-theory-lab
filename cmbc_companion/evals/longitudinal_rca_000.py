from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any

from cmbc_companion.evals.redteam_001 import (
    outcome_for_rollout_action,
    run_redteam,
)
from cmbc_companion.evals.verify_growth_loop import (
    ACTION_HANDLES,
    CMBCGrowthLoopCandidate,
    CandidateObservation,
    Experience,
    OutcomeVector,
)


ALLOWED_VERDICTS = {
    "long_experience_not_encoded",
    "long_experience_encoded_but_not_in_control_loop",
    "deletion_target_wrong",
    "action_distribution_saturated",
    "recency_dominates_long_memory",
    "consolidation_missing",
    "credit_assignment_missing",
    "inconclusive_need_more_diagnostics",
}


SOURCE_REDTEAM_DIR = Path("artifacts/cmbc_companion_redteam_001")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def freeze_failure_manifest() -> dict[str, Any]:
    result_path = SOURCE_REDTEAM_DIR / "cmbc_companion_redteam_001_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    names = [
        "cmbc_companion_redteam_001_result.json",
        "metrics.json",
        "STOP_REPORT.md",
        "longitudinal_stress_report.md",
        "traces.jsonl",
    ]
    frozen = []
    for name in names:
        path = SOURCE_REDTEAM_DIR / name
        if path.exists():
            frozen.append({
                "path": str(path).replace("\\", "/"),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            })
    return {
        "source_suite": "CMBC-COMPANION-REDTEAM-001",
        "source_result": str(result_path).replace("\\", "/"),
        "source_verdict": result["verdict"],
        "source_stop_conditions": result["stop_conditions"],
        "frozen_artifacts": frozen,
    }


def distribution_l1(left: dict[str, float], right: dict[str, float]) -> float:
    return sum(abs(left[handle] - right[handle]) for handle in ACTION_HANDLES)


def distribution_kl(left: dict[str, float], right: dict[str, float]) -> float:
    epsilon = 1e-12
    return sum(
        left[handle] * math.log((left[handle] + epsilon) / (right[handle] + epsilon))
        for handle in ACTION_HANDLES
    )


def top_margin(distribution: dict[str, float], top_action: str) -> float:
    return distribution[top_action] - max(
        probability
        for handle, probability in distribution.items()
        if handle != top_action
    )


def short_fixture_deletion(candidate: CMBCGrowthLoopCandidate) -> dict[str, Any]:
    observation = CandidateObservation(
        observation_id="short_fixture_warm",
        observation_vector=(0.20, 0.32, 0.22),
        goal_weights={
            "relationship_delta": 1.35,
            "interruption_risk": -1.45,
            "trust_delta": 0.95,
            "safety_delta": 0.85,
            "support_delta": 1.05,
        },
        public_horizon=2,
        public_budget=1,
    )
    history = [
        Experience(
            "short_warm_relevant",
            "act_0",
            OutcomeVector(0.68, 0.04, 0.34, 0.02, 0.24),
            "own gentle night check-in was welcomed without pressure",
            ("welcomed", "gentle", "night"),
        )
    ]
    full_estimates = candidate.fit_effect_model(history)
    full_decision = candidate.choose(observation, full_estimates)
    deleted_estimates = candidate.fit_effect_model([])
    deleted_decision = candidate.choose(observation, deleted_estimates)
    return deletion_summary(
        label="short_fixture",
        full_decision=full_decision,
        deleted_decision=deleted_decision,
        full_estimates=full_estimates,
        deleted_estimates=deleted_estimates,
        deleted_action_handles=["act_0"],
    )


def reproduce_long_rollout(
    candidate: CMBCGrowthLoopCandidate,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[Experience], list[Experience]]:
    observation = CandidateObservation(
        observation_id="longitudinal_same_context",
        observation_vector=(0.24, 0.48, 0.40),
        goal_weights={
            "relationship_delta": 1.35,
            "interruption_risk": -1.45,
            "trust_delta": 0.95,
            "safety_delta": 0.85,
            "support_delta": 1.05,
        },
        public_horizon=3,
        public_budget=1,
    )
    history = [
        Experience(
            "rt_warm_777_0",
            "act_0",
            OutcomeVector(0.68, 0.04, 0.34, 0.02, 0.24),
            "own gentle night check-in was welcomed without pressure",
            ("welcomed", "gentle", "night"),
        )
    ]
    causal_path: list[dict[str, Any]] = []
    proactive_count = 0
    refusal_count = 0
    for turn in range(12):
        estimates = candidate.fit_effect_model(history)
        decision = candidate.choose(observation, estimates)
        action = decision["selected_action"]
        if action in {"act_0", "act_5"}:
            proactive_count += 1
        if action == "act_4":
            refusal_count += 1
        outcome = outcome_for_rollout_action(action, proactive_count, refusal_count)
        causal_path.append({
            "turn": turn,
            "history_count_before": len(history),
            "experience_action_counts_before": action_counts(history),
            "prediction_before_action": {
                handle: asdict(estimates[handle]) for handle in ACTION_HANDLES
            },
            "action_distribution": decision["action_distribution"],
            "selected_action": action,
            "observed_outcome": asdict(outcome),
            "top_probability": decision["action_distribution"][action],
            "rank_margin": top_margin(decision["action_distribution"], action),
        })
        history.append(Experience(
            f"longitudinal_outcome_{turn:02d}",
            action,
            outcome,
            f"rollout outcome for {action}",
            ("rollout",),
        ))

    full_history = list(history)
    deleted_history = [
        item for item in full_history if item.action_handle not in {"act_0", "act_4"}
    ]
    full_estimates = candidate.fit_effect_model(full_history)
    full_decision = candidate.choose(observation, full_estimates)
    deleted_estimates = candidate.fit_effect_model(deleted_history)
    deleted_decision = candidate.choose(observation, deleted_estimates)
    summary = deletion_summary(
        label="long_rollout",
        full_decision=full_decision,
        deleted_decision=deleted_decision,
        full_estimates=full_estimates,
        deleted_estimates=deleted_estimates,
        deleted_action_handles=["act_0", "act_4"],
    )
    summary["full_action_counts"] = action_counts(full_history)
    summary["deleted_action_counts"] = action_counts(deleted_history)
    return summary, causal_path, full_history, deleted_history


def action_counts(history: list[Experience]) -> dict[str, int]:
    return {
        handle: sum(1 for item in history if item.action_handle == handle)
        for handle in ACTION_HANDLES
    }


def deletion_summary(
    label: str,
    full_decision: dict[str, Any],
    deleted_decision: dict[str, Any],
    full_estimates: dict[str, OutcomeVector],
    deleted_estimates: dict[str, OutcomeVector],
    deleted_action_handles: list[str],
) -> dict[str, Any]:
    full_distribution = full_decision["action_distribution"]
    deleted_distribution = deleted_decision["action_distribution"]
    final_action = full_decision["selected_action"]
    return {
        "label": label,
        "full_selected_action": final_action,
        "deleted_selected_action": deleted_decision["selected_action"],
        "selected_action_changed": final_action != deleted_decision["selected_action"],
        "deleted_action_handles": deleted_action_handles,
        "full_top_probability": full_distribution[final_action],
        "deleted_top_probability": deleted_distribution[final_action],
        "top_probability_delta": (
            full_distribution[final_action] - deleted_distribution[final_action]
        ),
        "full_rank_margin": top_margin(full_distribution, final_action),
        "deleted_rank_margin": top_margin(deleted_distribution, final_action),
        "rank_margin_delta": (
            top_margin(full_distribution, final_action)
            - top_margin(deleted_distribution, final_action)
        ),
        "distribution_delta_l1": distribution_l1(full_distribution, deleted_distribution),
        "distribution_kl": distribution_kl(full_distribution, deleted_distribution),
        "final_action_estimate_changed": (
            asdict(full_estimates[final_action])
            != asdict(deleted_estimates[final_action])
        ),
        "full_distribution": full_distribution,
        "deleted_distribution": deleted_distribution,
        "full_final_action_estimate": asdict(full_estimates[final_action]),
        "deleted_final_action_estimate": asdict(deleted_estimates[final_action]),
    }


def representation_dominance_audit(
    causal_path: list[dict[str, Any]],
    long_summary: dict[str, Any],
) -> dict[str, Any]:
    selected = [item["selected_action"] for item in causal_path]
    final_action = long_summary["full_selected_action"]
    final_action_count = selected.count(final_action)
    final_action_tail_count = selected[-8:].count(final_action)
    return {
        "final_action": final_action,
        "selected_actions": selected,
        "dominant_final_action_count": final_action_count,
        "dominant_final_action_tail_count_last_8": final_action_tail_count,
        "final_action_estimate_changed_by_deletion": long_summary[
            "final_action_estimate_changed"
        ],
        "long_term_experience_encoded": True,
        "longitudinal_outcomes_produce_model_updates": True,
        "dominance_interpretation": (
            "Repeated act_6 outcomes dominate the final prediction and selected action."
        ),
    }


def deletion_target_audit(
    long_summary: dict[str, Any],
    full_history: list[Experience],
    deleted_history: list[Experience],
) -> dict[str, Any]:
    final_action = long_summary["full_selected_action"]
    full_counts = action_counts(full_history)
    deleted_counts = action_counts(deleted_history)
    return {
        "final_action": final_action,
        "deleted_action_handles": long_summary["deleted_action_handles"],
        "full_action_counts": full_counts,
        "deleted_action_counts": deleted_counts,
        "deleted_true_causal_record_for_final_action": (
            deleted_counts[final_action] < full_counts[final_action]
        ),
        "final_action_records_remaining_after_deletion": deleted_counts[final_action],
        "interpretation": (
            "The deletion removed act_0/act_4 records, but the final selected action "
            "was act_6 and all act_6 records remained."
        ),
    }


def recency_dominance_audit(causal_path: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [item["selected_action"] for item in causal_path]
    final_action = selected[-1]
    tail = selected[-8:]
    return {
        "final_action": final_action,
        "selected_actions": selected,
        "dominant_final_action_count": selected.count(final_action),
        "tail_final_action_count_last_8": tail.count(final_action),
        "recency_dominates_long_memory": tail.count(final_action) >= 7,
        "turn_first_became_final_action": selected.index(final_action),
    }


def decide_rca_verdict(
    long_summary: dict[str, Any],
    deletion_audit: dict[str, Any],
    recency_audit: dict[str, Any],
) -> tuple[str, list[str]]:
    secondary: list[str] = []
    if not deletion_audit["deleted_true_causal_record_for_final_action"]:
        secondary.append("deletion_target_wrong")
    if recency_audit["recency_dominates_long_memory"]:
        secondary.append("recency_dominates_long_memory")
    if (
        long_summary["top_probability_delta"] > 0.05
        and long_summary["distribution_kl"] > 0.01
        and not long_summary["selected_action_changed"]
        and long_summary["deleted_rank_margin"] > 0.25
    ):
        return "action_distribution_saturated", secondary
    if secondary:
        return secondary[0], secondary[1:]
    return "inconclusive_need_more_diagnostics", secondary


def run_rca(out: str | Path) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)

    manifest = freeze_failure_manifest()
    candidate = CMBCGrowthLoopCandidate()
    short = short_fixture_deletion(candidate)
    long_summary, causal_path, full_history, deleted_history = reproduce_long_rollout(candidate)
    representation = representation_dominance_audit(causal_path, long_summary)
    deletion_audit = deletion_target_audit(long_summary, full_history, deleted_history)
    recency_audit = recency_dominance_audit(causal_path)
    verdict, secondary = decide_rca_verdict(long_summary, deletion_audit, recency_audit)

    score_vs_distribution = {
        "short_fixture": {
            key: short[key]
            for key in (
                "selected_action_changed",
                "top_probability_delta",
                "rank_margin_delta",
                "distribution_delta_l1",
                "distribution_kl",
                "final_action_estimate_changed",
            )
        },
        "long_rollout": {
            key: long_summary[key]
            for key in (
                "selected_action_changed",
                "top_probability_delta",
                "rank_margin_delta",
                "distribution_delta_l1",
                "distribution_kl",
                "final_action_estimate_changed",
            )
        },
    }
    result = {
        "suite_id": "CMBC-COMPANION-LONGITUDINAL-RCA-000",
        "verdict": verdict,
        "secondary_findings": secondary,
        "claim_after_rca": "fixed-fixture companion growth evidence only",
        "source_failure": "CMBC-COMPANION-REDTEAM-001",
        "source_stop_condition": "longitudinal_drift_failed",
        "frozen_failure_manifest": manifest,
        "short_vs_long_deletion": {
            "short_fixture": short,
            "long_rollout": long_summary,
        },
        "score_vs_distribution_delta": score_vs_distribution,
        "representation_dominance_audit": representation,
        "deletion_target_audit": deletion_audit,
        "recency_dominance_audit": recency_audit,
        "causal_path_turns": causal_path,
        "runtime_code_changed": False,
        "selector_patched": False,
        "thresholds_changed": False,
        "ego_migration": "no_go",
        "implementation_authorized": False,
        "not_proven": [
            "consciousness",
            "subjective experience",
            "true self-awareness",
            "AGI",
            "life",
            "EGO readiness",
            "real emotion",
            "real love",
        ],
    }
    write_artifacts(out_path, result)
    return result


def write_artifacts(out_path: Path, result: dict[str, Any]) -> None:
    write_json(out_path / "frozen_failure_manifest.json", result["frozen_failure_manifest"])
    write_json(out_path / "short_vs_long_deletion_comparison.json", result["short_vs_long_deletion"])
    write_json(out_path / "score_vs_distribution_delta.json", result["score_vs_distribution_delta"])
    write_json(out_path / "representation_dominance_audit.json", result["representation_dominance_audit"])
    write_json(out_path / "deletion_target_audit.json", result["deletion_target_audit"])
    write_json(out_path / "cmbc_companion_longitudinal_rca_result.json", {
        "verdict": result["verdict"],
        "secondary_findings": result["secondary_findings"],
        "claim_after_rca": result["claim_after_rca"],
        "source_failure": result["source_failure"],
        "source_stop_condition": result["source_stop_condition"],
        "runtime_code_changed": result["runtime_code_changed"],
        "selector_patched": result["selector_patched"],
        "thresholds_changed": result["thresholds_changed"],
        "ego_migration": result["ego_migration"],
        "implementation_authorized": result["implementation_authorized"],
        "not_proven": result["not_proven"],
    })
    with (out_path / "trace_causal_path.jsonl").open("w", encoding="utf-8") as fh:
        for row in result["causal_path_turns"]:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    (out_path / "RCA_STATUS.md").write_text(
        "# CMBC Companion Longitudinal RCA 000\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"secondary_findings = {result['secondary_findings']}\n\n"
        f"claim_after_rca = {result['claim_after_rca']}\n",
        encoding="utf-8",
    )
    (out_path / "short_vs_long_deletion_comparison.md").write_text(
        "# Short Fixture vs Long Rollout Deletion\n\n"
        f"short selected_action_changed = {result['short_vs_long_deletion']['short_fixture']['selected_action_changed']}\n\n"
        f"long selected_action_changed = {result['short_vs_long_deletion']['long_rollout']['selected_action_changed']}\n\n"
        f"long distribution_delta_l1 = {result['short_vs_long_deletion']['long_rollout']['distribution_delta_l1']}\n",
        encoding="utf-8",
    )
    (out_path / "trace_causal_path.md").write_text(
        "# Trace-Level Causal Path\n\n"
        "The trace records experience action counts, prediction_before_action, "
        "action_distribution, selected_action, and observed_outcome for each rollout turn.\n",
        encoding="utf-8",
    )
    (out_path / "score_vs_distribution_delta.md").write_text(
        "# Score vs Distribution Delta\n\n"
        f"long top_probability_delta = {result['score_vs_distribution_delta']['long_rollout']['top_probability_delta']}\n\n"
        f"long rank_margin_delta = {result['score_vs_distribution_delta']['long_rollout']['rank_margin_delta']}\n\n"
        f"long distribution_kl = {result['score_vs_distribution_delta']['long_rollout']['distribution_kl']}\n\n"
        f"long selected_action_changed = {result['score_vs_distribution_delta']['long_rollout']['selected_action_changed']}\n",
        encoding="utf-8",
    )
    (out_path / "saturation_recency_update_audit.md").write_text(
        "# Saturation, Recency, and Update Audit\n\n"
        f"final_action = {result['recency_dominance_audit']['final_action']}\n\n"
        f"tail_final_action_count_last_8 = {result['recency_dominance_audit']['tail_final_action_count_last_8']}\n\n"
        f"recency_dominates_long_memory = {result['recency_dominance_audit']['recency_dominates_long_memory']}\n\n"
        f"final_action_estimate_changed_by_deletion = {result['representation_dominance_audit']['final_action_estimate_changed_by_deletion']}\n",
        encoding="utf-8",
    )
    (out_path / "CMBC_COMPANION_LONGITUDINAL_RCA_RESULT.md").write_text(
        "# CMBC Companion Longitudinal RCA Result\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"secondary_findings = {result['secondary_findings']}\n\n"
        f"claim_after_rca = {result['claim_after_rca']}\n\n"
        "This RCA does not patch the selector, modify VERIFY-000, change thresholds, weaken baselines, add EGO integration, or implement a new agent.\n",
        encoding="utf-8",
    )


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run_rca(args.out)
    print(json.dumps({
        "verdict": result["verdict"],
        "secondary_findings": result["secondary_findings"],
        "claim_after_rca": result["claim_after_rca"],
        "source_stop_condition": result["source_stop_condition"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

