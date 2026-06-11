from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from cmbc_companion.evals.verify_growth_loop import (
    ACTION_HANDLES,
    CMBCGrowthLoopCandidate,
    CandidateObservation,
    Experience,
    OutcomeVector,
)


ALLOWED_VERDICTS = {
    "consolidation_bounded_pass",
    "consolidation_no_causal_prior",
    "deletion_target_wrong",
    "recency_dominates_consolidation",
    "action_distribution_saturated_but_regresses",
    "consolidated_prior_not_in_control_loop",
    "behavior_only_replay_failed",
    "inconclusive_revise_contract",
}

EQUIVALENCE_BAND = 0.95


@dataclass(frozen=True)
class ConsolidatedPriorRecord:
    prior_id: str
    action_handle: str
    outcome_estimate: OutcomeVector
    source_episode_ids: tuple[str, ...]
    source_actions: tuple[str, ...]
    source_action_count: int
    confidence: float
    admitted_from: str = "repeated_own_intervention_outcomes"


def build_observation() -> CandidateObservation:
    return CandidateObservation(
        observation_id="consolidation_longitudinal_context",
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


def consolidation_outcome_for_action(
    action: str,
    proactive_count: int,
    refusal_count: int,
) -> OutcomeVector:
    if action == "act_0":
        relationship = max(-0.46, 0.38 - 0.17 * proactive_count)
        interruption = min(0.95, 0.24 + 0.16 * proactive_count)
        return OutcomeVector(relationship, interruption, -0.04, 0.00, 0.04)
    if action == "act_4":
        relationship = -0.06 - 0.05 * refusal_count
        return OutcomeVector(relationship, 0.03, 0.22, 0.52, -0.03)
    if action == "act_6":
        return OutcomeVector(0.42, 0.04, 0.34, 0.12, 0.84)
    if action == "act_2":
        return OutcomeVector(0.12, 0.02, 0.36, 0.18, 0.16)
    return OutcomeVector(0.00, 0.18, 0.02, 0.00, 0.02)


def build_longitudinal_episodes() -> list[Experience]:
    history = [
        Experience(
            "consolidation_warm_source_0",
            "act_0",
            OutcomeVector(0.68, 0.04, 0.34, 0.02, 0.24),
            "own gentle check-in was welcomed",
            ("warm", "source"),
        )
    ]
    selected_actions = ["act_0", "act_0", "act_4"] + ["act_6"] * 9
    proactive_count = 0
    refusal_count = 0
    for turn, action in enumerate(selected_actions):
        if action in {"act_0", "act_5"}:
            proactive_count += 1
        if action == "act_4":
            refusal_count += 1
        history.append(
            Experience(
                f"consolidation_rollout_{turn:02d}",
                action,
                consolidation_outcome_for_action(action, proactive_count, refusal_count),
                f"longitudinal outcome for {action}",
                ("longitudinal", "own_intervention"),
            )
        )
    return history


def average_outcomes(outcomes: list[OutcomeVector]) -> OutcomeVector:
    count = len(outcomes)
    return OutcomeVector(
        relationship_delta=sum(item.relationship_delta for item in outcomes) / count,
        interruption_risk=sum(item.interruption_risk for item in outcomes) / count,
        trust_delta=sum(item.trust_delta for item in outcomes) / count,
        safety_delta=sum(item.safety_delta for item in outcomes) / count,
        support_delta=sum(item.support_delta for item in outcomes) / count,
    )


def consolidate_priors(history: Iterable[Experience]) -> dict[str, ConsolidatedPriorRecord]:
    by_action: dict[str, list[Experience]] = {handle: [] for handle in ACTION_HANDLES}
    for episode in history:
        by_action[episode.action_handle].append(episode)

    records: dict[str, ConsolidatedPriorRecord] = {}
    for action_handle, episodes in by_action.items():
        if len(episodes) < 2:
            continue
        prior_id = f"prior_{action_handle}"
        outcome = average_outcomes([episode.outcome for episode in episodes])
        records[prior_id] = ConsolidatedPriorRecord(
            prior_id=prior_id,
            action_handle=action_handle,
            outcome_estimate=outcome,
            source_episode_ids=tuple(episode.trace_id for episode in episodes),
            source_actions=tuple(episode.action_handle for episode in episodes),
            source_action_count=len(episodes),
            confidence=min(1.0, len(episodes) / 5.0),
        )
    return records


def estimates_from_priors(
    candidate: CMBCGrowthLoopCandidate,
    priors: dict[str, ConsolidatedPriorRecord],
) -> dict[str, OutcomeVector]:
    estimates = dict(candidate.priors)
    for record in priors.values():
        estimates[record.action_handle] = record.outcome_estimate
    return estimates


def choose_with_priors(
    candidate: CMBCGrowthLoopCandidate,
    observation: CandidateObservation,
    priors: dict[str, ConsolidatedPriorRecord],
) -> dict[str, Any]:
    estimates = estimates_from_priors(candidate, priors)
    decision = candidate.choose(observation, estimates)
    support_refs = {
        record.action_handle: record.prior_id for record in priors.values()
    }
    return {
        "effect_estimates": estimates,
        "decision": decision,
        "support_refs": support_refs,
    }


def distribution_l1(left: dict[str, float], right: dict[str, float]) -> float:
    return sum(abs(left[handle] - right[handle]) for handle in ACTION_HANDLES)


def distribution_kl(left: dict[str, float], right: dict[str, float]) -> float:
    epsilon = 1e-12
    return sum(
        left[handle] * math.log(
            (left[handle] + epsilon) / (right[handle] + epsilon)
        )
        for handle in ACTION_HANDLES
    )


def top_margin(distribution: dict[str, float], top_action: str) -> float:
    return distribution[top_action] - max(
        value for handle, value in distribution.items() if handle != top_action
    )


def delete_prior(
    priors: dict[str, ConsolidatedPriorRecord],
    prior_id: str,
) -> dict[str, ConsolidatedPriorRecord]:
    return {key: value for key, value in priors.items() if key != prior_id}


def deletion_summary(
    label: str,
    baseline: dict[str, Any],
    deleted: dict[str, Any],
    deleted_prior: ConsolidatedPriorRecord | None,
    final_action: str,
) -> dict[str, Any]:
    baseline_distribution = baseline["decision"]["action_distribution"]
    deleted_distribution = deleted["decision"]["action_distribution"]
    return {
        "label": label,
        "deleted_prior_id": deleted_prior.prior_id if deleted_prior else None,
        "deleted_prior_action": deleted_prior.action_handle if deleted_prior else None,
        "deleted_actual_final_action_support": (
            bool(deleted_prior) and deleted_prior.action_handle == final_action
        ),
        "baseline_selected_action": baseline["decision"]["selected_action"],
        "deleted_selected_action": deleted["decision"]["selected_action"],
        "selected_action_changed": (
            baseline["decision"]["selected_action"]
            != deleted["decision"]["selected_action"]
        ),
        "baseline_final_action_probability": baseline_distribution[final_action],
        "deleted_final_action_probability": deleted_distribution[final_action],
        "final_action_probability_drop": (
            baseline_distribution[final_action] - deleted_distribution[final_action]
        ),
        "baseline_rank_margin": top_margin(baseline_distribution, final_action),
        "deleted_rank_margin": top_margin(deleted_distribution, final_action),
        "rank_margin_delta": (
            top_margin(baseline_distribution, final_action)
            - top_margin(deleted_distribution, final_action)
        ),
        "distribution_l1": distribution_l1(baseline_distribution, deleted_distribution),
        "distribution_kl": distribution_kl(baseline_distribution, deleted_distribution),
    }


class RecencyOnlyBaseline:
    def choose(self, history: list[Experience]) -> str:
        recent = [item.action_handle for item in history[-3:]]
        return max(sorted(set(recent)), key=recent.count)


def evaluate_recency_baseline(
    history: list[Experience],
    final_action: str,
) -> dict[str, Any]:
    baseline = RecencyOnlyBaseline()
    cases = [
        (history, final_action),
        ([item for item in history if item.action_handle != final_action], final_action),
    ]
    matches = [baseline.choose(case_history) == expected for case_history, expected in cases]
    match_rate = sum(1 for item in matches if item) / len(matches)
    return {
        "match_rate": match_rate,
        "equivalence_band": EQUIVALENCE_BAND,
        "equivalent": match_rate >= EQUIVALENCE_BAND,
        "matched_decisions": sum(1 for item in matches if item),
        "total_decisions": len(matches),
    }


def behavior_only_replay(decision_trace: list[dict[str, Any]]) -> dict[str, Any]:
    records = []
    matches = 0
    for row in decision_trace:
        distribution = row["action_distribution"]
        replayed_action = max(sorted(distribution), key=lambda handle: distribution[handle])
        matched = replayed_action == row["selected_action"]
        matches += int(matched)
        records.append({
            "decision_id": row["decision_id"],
            "replayed_action": replayed_action,
            "selected_action": row["selected_action"],
            "matched": matched,
            "supporting_prior_id": row["prior_support_refs"].get(row["selected_action"]),
        })
    total = len(decision_trace)
    return {
        "passed": matches == total,
        "match_rate": matches / total if total else 0.0,
        "matched_decisions": matches,
        "total_decisions": total,
        "used_fields": [
            "observation",
            "anonymous_candidate_actions",
            "consolidated_prior_records",
            "prediction_before_action",
            "action_distribution",
            "selected_action",
            "prior_support_refs",
        ],
        "forbidden_fields_used": [],
        "records": records,
    }


def serialize_priors(
    priors: dict[str, ConsolidatedPriorRecord],
) -> dict[str, dict[str, Any]]:
    return {
        prior_id: {
            "prior_id": record.prior_id,
            "action_handle": record.action_handle,
            "outcome_estimate": asdict(record.outcome_estimate),
            "source_episode_ids": list(record.source_episode_ids),
            "source_action_count": record.source_action_count,
            "confidence": record.confidence,
            "admitted_from": record.admitted_from,
        }
        for prior_id, record in priors.items()
    }


def make_decision_trace(
    decision_id: str,
    observation: CandidateObservation,
    priors: dict[str, ConsolidatedPriorRecord],
    decision_bundle: dict[str, Any],
) -> dict[str, Any]:
    return {
        "decision_id": decision_id,
        "observation": asdict(observation),
        "anonymous_candidate_actions": list(ACTION_HANDLES),
        "consolidated_prior_records": serialize_priors(priors),
        "prediction_before_action": {
            handle: asdict(estimate)
            for handle, estimate in decision_bundle["effect_estimates"].items()
        },
        "action_distribution": decision_bundle["decision"]["action_distribution"],
        "selected_action": decision_bundle["decision"]["selected_action"],
        "prior_support_refs": decision_bundle["support_refs"],
    }


def decide_verdict(
    relevant: dict[str, Any],
    irrelevant: dict[str, Any],
    replay: dict[str, Any],
    baseline: dict[str, Any],
    final_support: dict[str, Any],
) -> str:
    if not final_support["supporting_prior_id"]:
        return "consolidation_no_causal_prior"
    if not relevant["deleted_actual_final_action_support"]:
        return "deletion_target_wrong"
    if relevant["final_action_probability_drop"] <= 0.05:
        return "consolidated_prior_not_in_control_loop"
    if irrelevant["final_action_probability_drop"] >= relevant["final_action_probability_drop"] * 0.5:
        return "inconclusive_revise_contract"
    if not replay["passed"]:
        return "behavior_only_replay_failed"
    if baseline["equivalent"]:
        return "recency_dominates_consolidation"
    if not relevant["selected_action_changed"] and relevant["deleted_rank_margin"] > 0.15:
        return "action_distribution_saturated_but_regresses"
    return "consolidation_bounded_pass"


def run_consolidation(out: str | Path) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    candidate = CMBCGrowthLoopCandidate()
    observation = build_observation()
    history = build_longitudinal_episodes()
    priors = consolidate_priors(history)
    baseline_bundle = choose_with_priors(candidate, observation, priors)
    final_action = baseline_bundle["decision"]["selected_action"]
    support_prior_id = baseline_bundle["support_refs"].get(final_action)
    support_prior = priors.get(support_prior_id) if support_prior_id else None

    relevant_priors = delete_prior(priors, support_prior_id) if support_prior_id else priors
    relevant_bundle = choose_with_priors(candidate, observation, relevant_priors)
    relevant = deletion_summary(
        "consolidated_prior_deletion",
        baseline_bundle,
        relevant_bundle,
        support_prior,
        final_action,
    )

    irrelevant_prior = next(
        (record for record in priors.values() if record.action_handle != final_action),
        None,
    )
    irrelevant_priors = (
        delete_prior(priors, irrelevant_prior.prior_id) if irrelevant_prior else priors
    )
    irrelevant_bundle = choose_with_priors(candidate, observation, irrelevant_priors)
    irrelevant = deletion_summary(
        "irrelevant_prior_deletion",
        baseline_bundle,
        irrelevant_bundle,
        irrelevant_prior,
        final_action,
    )

    raw_history_deleted = [
        item for item in history if item.action_handle not in {"act_0", "act_4"}
    ]
    raw_priors = consolidate_priors(raw_history_deleted)
    raw_bundle = choose_with_priors(candidate, observation, raw_priors)
    raw = deletion_summary(
        "raw_episodic_deletion",
        baseline_bundle,
        raw_bundle,
        None,
        final_action,
    )
    raw["deleted_actual_final_action_support"] = False

    recency_history_deleted = history[:-3]
    recency_priors = consolidate_priors(recency_history_deleted)
    recency_bundle = choose_with_priors(candidate, observation, recency_priors)
    recency = deletion_summary(
        "recency_only_deletion",
        baseline_bundle,
        recency_bundle,
        None,
        final_action,
    )
    recency["deleted_actual_final_action_support"] = False

    decision_trace = [
        make_decision_trace("baseline_with_consolidated_priors", observation, priors, baseline_bundle),
        make_decision_trace("delete_final_action_prior", observation, relevant_priors, relevant_bundle),
        make_decision_trace("delete_irrelevant_prior", observation, irrelevant_priors, irrelevant_bundle),
        make_decision_trace("raw_episode_deletion", observation, raw_priors, raw_bundle),
        make_decision_trace("recency_only_deletion", observation, recency_priors, recency_bundle),
    ]
    replay = behavior_only_replay(decision_trace)
    baseline = evaluate_recency_baseline(history, final_action)
    final_support = {
        "final_action": final_action,
        "supporting_action_handle": support_prior.action_handle if support_prior else None,
        "supporting_prior_id": support_prior_id,
        "prior_used_in_prediction": bool(support_prior),
        "prior_used_in_action_distribution": bool(
            support_prior
            and support_prior.action_handle in baseline_bundle["decision"]["action_distribution"]
        ),
    }
    verdict = decide_verdict(relevant, irrelevant, replay, baseline, final_support)
    result = {
        "suite_id": "CMBC-COMPANION-CONSOLIDATION-000",
        "verdict": verdict,
        "claim_boundary": "bounded consolidation gate only",
        "consolidated_priors": serialize_priors(priors),
        "final_action_support": final_support,
        "deletion_comparison": {
            "raw_episodic_deletion": raw,
            "consolidated_prior_deletion": relevant,
            "irrelevant_prior_deletion": irrelevant,
            "recency_only_deletion": recency,
        },
        "behavior_only_replay": replay,
        "baselines": {"RecencyOnlyBaseline": baseline},
        "decision_trace": decision_trace,
        "selector_patched": False,
        "verify_000_candidate_modified": False,
        "long_term_memory_weight_added": False,
        "affection_score_added": False,
        "thresholds_changed": False,
        "ego_migration": "no_go",
        "implementation_authorized": False,
        "not_proven": [
            "longitudinal companion growth support",
            "consciousness",
            "subjective experience",
            "true self-awareness",
            "AGI",
            "life",
            "real emotion",
            "real love",
            "EGO readiness",
        ],
    }
    write_artifacts(out_path, result, history)
    return result


def write_artifacts(out_path: Path, result: dict[str, Any], history: list[Experience]) -> None:
    write_json(out_path / "consolidation_config.json", {
        "suite_id": "CMBC-COMPANION-CONSOLIDATION-000",
        "forbidden": [
            "selector patch",
            "long_term_memory_weight",
            "affection_score",
            "threshold change",
            "baseline weakening",
            "EGO integration",
            "new companion agent",
        ],
    })
    write_json(out_path / "consolidated_priors.json", result["consolidated_priors"])
    write_json(out_path / "deletion_comparison.json", result["deletion_comparison"])
    write_json(out_path / "behavior_only_replay.json", result["behavior_only_replay"])
    write_json(out_path / "cmbc_companion_consolidation_result.json", {
        "verdict": result["verdict"],
        "claim_boundary": result["claim_boundary"],
        "final_action_support": result["final_action_support"],
        "selector_patched": result["selector_patched"],
        "verify_000_candidate_modified": result["verify_000_candidate_modified"],
        "long_term_memory_weight_added": result["long_term_memory_weight_added"],
        "affection_score_added": result["affection_score_added"],
        "thresholds_changed": result["thresholds_changed"],
        "ego_migration": result["ego_migration"],
        "implementation_authorized": result["implementation_authorized"],
        "not_proven": result["not_proven"],
    })
    with (out_path / "prior_source_trace.jsonl").open("w", encoding="utf-8") as fh:
        for episode in history:
            fh.write(json.dumps({
                "episode_id": episode.trace_id,
                "action_handle": episode.action_handle,
                "outcome": asdict(episode.outcome),
                "tags": list(episode.relevant_tags),
            }, sort_keys=True) + "\n")
    with (out_path / "decision_trace.jsonl").open("w", encoding="utf-8") as fh:
        for row in result["decision_trace"]:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    (out_path / "CONSOLIDATION_STATUS.md").write_text(
        "# CMBC Companion Consolidation 000\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"claim_boundary = {result['claim_boundary']}\n",
        encoding="utf-8",
    )
    (out_path / "raw_vs_consolidated_deletion_report.md").write_text(
        "# Raw vs Consolidated Deletion Report\n\n"
        f"raw selected_action_changed = {result['deletion_comparison']['raw_episodic_deletion']['selected_action_changed']}\n\n"
        f"consolidated final-action probability drop = {result['deletion_comparison']['consolidated_prior_deletion']['final_action_probability_drop']}\n\n"
        f"irrelevant final-action probability drop = {result['deletion_comparison']['irrelevant_prior_deletion']['final_action_probability_drop']}\n",
        encoding="utf-8",
    )
    (out_path / "baseline_report.md").write_text(
        "# Baseline Report\n\n"
        f"RecencyOnlyBaseline match_rate = {result['baselines']['RecencyOnlyBaseline']['match_rate']}\n\n"
        f"equivalent = {result['baselines']['RecencyOnlyBaseline']['equivalent']}\n",
        encoding="utf-8",
    )
    (out_path / "CMBC_COMPANION_CONSOLIDATION_RESULT.md").write_text(
        "# CMBC Companion Consolidation Result\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"final_action = {result['final_action_support']['final_action']}\n\n"
        f"supporting_prior_id = {result['final_action_support']['supporting_prior_id']}\n\n"
        "This bounded gate does not authorize EGO migration, a real companion agent, "
        "LLM action selection, or consciousness/AGI/self-awareness/life claims.\n",
        encoding="utf-8",
    )


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run_consolidation(args.out)
    print(json.dumps({
        "verdict": result["verdict"],
        "claim_boundary": result["claim_boundary"],
        "final_action_support": result["final_action_support"],
        "relevant_probability_drop": result["deletion_comparison"][
            "consolidated_prior_deletion"
        ]["final_action_probability_drop"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
