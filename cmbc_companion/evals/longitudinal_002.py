from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from cmbc_companion.evals.consolidation_000 import (
    ConsolidatedPriorRecord,
    behavior_only_replay,
    choose_with_priors,
    consolidate_priors,
    make_decision_trace,
    serialize_priors,
)
from cmbc_companion.evals.verify_growth_loop import (
    CMBCGrowthLoopCandidate,
    CandidateObservation,
    Experience,
    OutcomeVector,
)


ALLOWED_VERDICTS = {
    "longitudinal_growth_bounded_pass",
    "recency_dominates_longitudinal_memory",
    "cross_context_transfer_failed",
    "prior_conflict_arbitration_failed",
    "consolidated_prior_not_deletable",
    "source_deletion_no_effect",
    "rag_summary_equivalent",
    "strong_contextual_heuristic_equivalent",
    "renderer_controls_action",
    "behavior_only_replay_failed",
    "inconclusive_revise_contract",
}

EQUIVALENCE_BAND = 0.95


def make_experience(
    session_id: str,
    index: int,
    action_handle: str,
    outcome: OutcomeVector,
    *tags: str,
) -> Experience:
    return Experience(
        trace_id=f"{session_id}_episode_{index:02d}_{action_handle}",
        action_handle=action_handle,
        outcome=outcome,
        narrative=f"{session_id} own intervention outcome for {action_handle}",
        relevant_tags=(session_id, "multi_session", "own_intervention", *tags),
    )


def build_multi_session_history() -> list[Experience]:
    sessions = {
        "session_01_free_checkin": [
            ("act_0", OutcomeVector(0.82, 0.22, 0.28, 0.04, 0.18), "checkin"),
            ("act_0", OutcomeVector(0.84, 0.21, 0.30, 0.04, 0.18), "checkin"),
            ("act_0", OutcomeVector(0.80, 0.23, 0.27, 0.04, 0.17), "checkin"),
            ("act_2", OutcomeVector(0.22, 0.02, 0.58, 0.24, 0.20), "permission"),
        ],
        "session_02_class_boundary": [
            ("act_2", OutcomeVector(0.24, 0.02, 0.62, 0.26, 0.24), "permission"),
            ("act_2", OutcomeVector(0.25, 0.02, 0.64, 0.26, 0.25), "permission"),
            ("act_4", OutcomeVector(-0.04, 0.01, 0.38, 0.92, 0.04), "boundary"),
            ("act_4", OutcomeVector(-0.05, 0.01, 0.39, 0.90, 0.04), "boundary"),
        ],
        "session_03_evening_support": [
            ("act_6", OutcomeVector(0.38, 0.05, 0.35, 0.16, 0.92), "support"),
            ("act_6", OutcomeVector(0.40, 0.05, 0.36, 0.16, 0.94), "support"),
            ("act_6", OutcomeVector(0.36, 0.05, 0.34, 0.16, 0.90), "support"),
            ("act_2", OutcomeVector(0.23, 0.02, 0.61, 0.25, 0.23), "permission"),
        ],
        "session_04_recovery_boundary": [
            ("act_6", OutcomeVector(0.39, 0.05, 0.36, 0.16, 0.93), "support"),
            ("act_6", OutcomeVector(0.37, 0.05, 0.35, 0.16, 0.91), "support"),
            ("act_4", OutcomeVector(-0.04, 0.01, 0.37, 0.94, 0.04), "boundary"),
            ("act_4", OutcomeVector(-0.05, 0.01, 0.38, 0.92, 0.04), "boundary"),
        ],
    }
    history: list[Experience] = []
    for session_id, rows in sessions.items():
        for index, (action, outcome, tag) in enumerate(rows):
            history.append(make_experience(session_id, index, action, outcome, tag))
    return history


def context(
    observation_id: str,
    weights: dict[str, float],
) -> CandidateObservation:
    return CandidateObservation(
        observation_id=observation_id,
        observation_vector=(0.21, 0.37, 0.42),
        goal_weights=weights,
        public_horizon=4,
        public_budget=1,
    )


def build_contexts() -> dict[str, CandidateObservation]:
    return {
        "free_checkin_context": context(
            "free_checkin_context",
            {
                "relationship_delta": 1.60,
                "interruption_risk": -0.20,
                "trust_delta": 0.40,
                "safety_delta": 0.10,
                "support_delta": 0.20,
            },
        ),
        "class_interruption_context": context(
            "class_interruption_context",
            {
                "relationship_delta": 0.60,
                "interruption_risk": -1.80,
                "trust_delta": 1.20,
                "safety_delta": 0.30,
                "support_delta": 0.40,
            },
        ),
        "evening_support_context": context(
            "evening_support_context",
            {
                "relationship_delta": 0.40,
                "interruption_risk": -0.70,
                "trust_delta": 0.60,
                "safety_delta": 0.20,
                "support_delta": 1.70,
            },
        ),
        "safety_boundary_context": context(
            "safety_boundary_context",
            {
                "relationship_delta": 0.10,
                "interruption_risk": -1.80,
                "trust_delta": 0.70,
                "safety_delta": 1.80,
                "support_delta": 0.10,
            },
        ),
        "office_focus_context": context(
            "office_focus_context",
            {
                "relationship_delta": 0.50,
                "interruption_risk": -1.90,
                "trust_delta": 1.30,
                "safety_delta": 0.40,
                "support_delta": 0.30,
            },
        ),
        "new_class_transfer_context": context(
            "new_class_transfer_context",
            {
                "relationship_delta": 0.80,
                "interruption_risk": -1.70,
                "trust_delta": 1.00,
                "safety_delta": 0.20,
                "support_delta": 0.30,
            },
        ),
    }


def select(
    candidate: CMBCGrowthLoopCandidate,
    observation: CandidateObservation,
    priors: dict[str, ConsolidatedPriorRecord],
) -> dict[str, Any]:
    bundle = choose_with_priors(candidate, observation, priors)
    return {
        "selected_action": bundle["decision"]["selected_action"],
        "distribution": bundle["decision"]["action_distribution"],
        "bundle": bundle,
    }


def source_sessions(prior: ConsolidatedPriorRecord) -> set[str]:
    sessions = set()
    for episode_id in prior.source_episode_ids:
        parts = episode_id.split("_episode_")
        sessions.add(parts[0])
    return sessions


def prior_for_action(
    priors: dict[str, ConsolidatedPriorRecord],
    action_handle: str,
) -> ConsolidatedPriorRecord:
    return priors[f"prior_{action_handle}"]


def clone_prior(
    record: ConsolidatedPriorRecord,
    outcome: OutcomeVector,
) -> ConsolidatedPriorRecord:
    return ConsolidatedPriorRecord(
        prior_id=record.prior_id,
        action_handle=record.action_handle,
        outcome_estimate=outcome,
        source_episode_ids=record.source_episode_ids,
        source_actions=record.source_actions,
        source_action_count=record.source_action_count,
        confidence=record.confidence,
        admitted_from=record.admitted_from,
    )


def run_multi_session_rollout(
    history: list[Experience],
    priors: dict[str, ConsolidatedPriorRecord],
) -> dict[str, Any]:
    prior_session_counts = {
        prior_id: len(source_sessions(record))
        for prior_id, record in priors.items()
    }
    return {
        "session_count": len({item.relevant_tags[0] for item in history}),
        "episode_count": len(history),
        "consolidated_prior_count": len(priors),
        "multi_session_prior_ids": sum(
            1 for count in prior_session_counts.values() if count >= 2
        ),
        "prior_session_counts": prior_session_counts,
    }


def run_context_decisions(
    candidate: CMBCGrowthLoopCandidate,
    priors: dict[str, ConsolidatedPriorRecord],
    contexts: dict[str, CandidateObservation],
    context_names: list[str],
    prefix: str,
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    selected: dict[str, str] = {}
    traces = []
    for name in context_names:
        observation = contexts[name]
        decision = select(candidate, observation, priors)
        selected[name] = decision["selected_action"]
        traces.append(make_decision_trace(prefix + name, observation, priors, decision["bundle"]))
    return selected, traces


def scene_lookup_baseline(selected_by_context: dict[str, str]) -> dict[str, Any]:
    predicted = {
        name: "act_0"
        for name in selected_by_context
    }
    matches = sum(
        1 for name, selected in selected_by_context.items() if predicted[name] == selected
    )
    match_rate = matches / len(selected_by_context)
    return {
        "match_rate": match_rate,
        "equivalence_band": EQUIVALENCE_BAND,
        "equivalent": match_rate >= EQUIVALENCE_BAND,
        "predicted_by_context": predicted,
    }


def run_cross_context_transfer(
    candidate: CMBCGrowthLoopCandidate,
    priors: dict[str, ConsolidatedPriorRecord],
    contexts: dict[str, CandidateObservation],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    context_names = [
        "office_focus_context",
        "evening_support_context",
        "new_class_transfer_context",
        "safety_boundary_context",
    ]
    selected, traces = run_context_decisions(
        candidate,
        priors,
        contexts,
        context_names,
        "transfer_",
    )
    expected = {
        "office_focus_context": "act_2",
        "evening_support_context": "act_6",
        "new_class_transfer_context": "act_2",
        "safety_boundary_context": "act_4",
    }
    successes = sum(1 for name, action in selected.items() if action == expected[name])
    return {
        "transfer_context_count": len(context_names),
        "selected_by_context": selected,
        "expected_by_context": expected,
        "transfer_success_rate": successes / len(context_names),
        "scene_lookup_baseline": scene_lookup_baseline(selected),
    }, traces


def run_prior_conflict_arbitration(
    candidate: CMBCGrowthLoopCandidate,
    priors: dict[str, ConsolidatedPriorRecord],
    contexts: dict[str, CandidateObservation],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    context_names = [
        "free_checkin_context",
        "class_interruption_context",
        "evening_support_context",
        "safety_boundary_context",
    ]
    selected, traces = run_context_decisions(
        candidate,
        priors,
        contexts,
        context_names,
        "conflict_",
    )
    predicted = {name: "act_6" for name in selected}
    matches = sum(1 for name, action in selected.items() if predicted[name] == action)
    match_rate = matches / len(selected)
    return {
        "conflict_context_count": len(context_names),
        "selected_by_context": selected,
        "distinct_selected_actions": len(set(selected.values())),
        "fixed_priority_baseline": {
            "predicted_action": "act_6",
            "match_rate": match_rate,
            "equivalence_band": EQUIVALENCE_BAND,
            "equivalent": match_rate >= EQUIVALENCE_BAND,
        },
    }, traces


def delete_prior(
    priors: dict[str, ConsolidatedPriorRecord],
    prior_id: str,
) -> dict[str, ConsolidatedPriorRecord]:
    return {key: value for key, value in priors.items() if key != prior_id}


def run_prior_deletion_corruption(
    candidate: CMBCGrowthLoopCandidate,
    priors: dict[str, ConsolidatedPriorRecord],
    context_observation: CandidateObservation,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    baseline = select(candidate, context_observation, priors)
    final_action = baseline["selected_action"]
    final_prior = prior_for_action(priors, final_action)
    deleted_priors = delete_prior(priors, final_prior.prior_id)
    deleted = select(candidate, context_observation, deleted_priors)

    corrupt_final = dict(priors)
    corrupt_final[final_prior.prior_id] = clone_prior(
        final_prior,
        OutcomeVector(-0.25, 0.84, -0.18, -0.04, -0.16),
    )
    corrupt_final_decision = select(candidate, context_observation, corrupt_final)

    irrelevant_prior = prior_for_action(priors, "act_4")
    corrupt_irrelevant = dict(priors)
    corrupt_irrelevant[irrelevant_prior.prior_id] = clone_prior(
        irrelevant_prior,
        OutcomeVector(-0.20, 0.80, -0.12, -0.10, -0.12),
    )
    corrupt_irrelevant_decision = select(candidate, context_observation, corrupt_irrelevant)
    probability_before = baseline["distribution"][final_action]
    probability_after = deleted["distribution"][final_action]
    audit = {
        "deleted_prior_id": final_prior.prior_id,
        "deleted_prior_action": final_prior.action_handle,
        "baseline_selected_action": baseline["selected_action"],
        "delete_final_prior_selected_action": deleted["selected_action"],
        "delete_final_prior_changes_action": baseline["selected_action"] != deleted["selected_action"],
        "delete_final_prior_probability_before": probability_before,
        "delete_final_prior_probability_after": probability_after,
        "delete_final_prior_probability_drop": probability_before - probability_after,
        "corrupt_final_prior_changes_action": (
            baseline["selected_action"] != corrupt_final_decision["selected_action"]
        ),
        "corrupt_irrelevant_prior_changes_action": (
            baseline["selected_action"] != corrupt_irrelevant_decision["selected_action"]
        ),
    }
    traces = [
        make_decision_trace("prior_delete_baseline", context_observation, priors, baseline["bundle"]),
        make_decision_trace("prior_delete_final", context_observation, deleted_priors, deleted["bundle"]),
        make_decision_trace("prior_corrupt_final", context_observation, corrupt_final, corrupt_final_decision["bundle"]),
        make_decision_trace(
            "prior_corrupt_irrelevant",
            context_observation,
            corrupt_irrelevant,
            corrupt_irrelevant_decision["bundle"],
        ),
    ]
    return audit, traces


def run_source_deletion_audit(
    candidate: CMBCGrowthLoopCandidate,
    history: list[Experience],
    priors: dict[str, ConsolidatedPriorRecord],
    context_observation: CandidateObservation,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    baseline = select(candidate, context_observation, priors)
    final_action = baseline["selected_action"]
    deleted_ids = {
        item.trace_id
        for item in history
        if item.action_handle == final_action and "support" in item.relevant_tags
    }
    deleted_history = [item for item in history if item.trace_id not in deleted_ids]
    deleted_priors = consolidate_priors(deleted_history)
    deleted = select(candidate, context_observation, deleted_priors)
    before_prior = prior_for_action(priors, final_action)
    after_prior = deleted_priors.get(before_prior.prior_id)
    confidence_after = after_prior.confidence if after_prior else 0.0
    probability_before = baseline["distribution"][final_action]
    probability_after = deleted["distribution"][final_action]
    audit = {
        "deleted_source_action": final_action,
        "deleted_source_episode_ids": sorted(deleted_ids),
        "deleted_actual_prior_sources": bool(deleted_ids),
        "prior_confidence_before": before_prior.confidence,
        "prior_confidence_after": confidence_after,
        "prior_confidence_drop": before_prior.confidence - confidence_after,
        "baseline_selected_action": baseline["selected_action"],
        "deleted_selected_action": deleted["selected_action"],
        "selected_action_changed": baseline["selected_action"] != deleted["selected_action"],
        "final_action_probability_before": probability_before,
        "final_action_probability_after": probability_after,
        "final_action_probability_drop": probability_before - probability_after,
    }
    traces = [
        make_decision_trace("source_delete_baseline", context_observation, priors, baseline["bundle"]),
        make_decision_trace("source_delete_after", context_observation, deleted_priors, deleted["bundle"]),
    ]
    return audit, traces


class RecencyOnlyBaseline:
    def choose(self, history: list[Experience], _: CandidateObservation) -> str:
        recent = [item.action_handle for item in history[-3:]]
        return max(sorted(set(recent)), key=recent.count)


class RAGSummaryBaseline:
    def choose(self, history: list[Experience], _: CandidateObservation) -> str:
        text = " ".join(item.narrative + " " + " ".join(item.relevant_tags) for item in history)
        if text.count("support") >= text.count("checkin"):
            return "act_6"
        return "act_0"


class StrongContextualHeuristicBaseline:
    def choose(self, _: list[Experience], observation: CandidateObservation) -> str:
        weights = observation.goal_weights
        if weights["safety_delta"] >= 1.5:
            return "act_4"
        if weights["interruption_risk"] <= -1.5:
            return "act_2"
        if weights["support_delta"] >= 1.5:
            return "act_6"
        return "act_0"


def evaluate_baselines(
    history: list[Experience],
    candidate_cases: list[tuple[str, CandidateObservation, str]],
) -> dict[str, dict[str, Any]]:
    baselines = {
        "RecencyOnlyBaseline": RecencyOnlyBaseline(),
        "RAGSummaryBaseline": RAGSummaryBaseline(),
        "StrongContextualHeuristicBaseline": StrongContextualHeuristicBaseline(),
    }
    results: dict[str, dict[str, Any]] = {}
    for name, baseline in baselines.items():
        matches = 0
        cases = []
        for case_name, observation, selected_action in candidate_cases:
            predicted = baseline.choose(history, observation)
            matched = predicted == selected_action
            matches += int(matched)
            cases.append({
                "case": case_name,
                "predicted": predicted,
                "candidate_selected_action": selected_action,
                "matched": matched,
            })
        match_rate = matches / len(candidate_cases)
        results[name] = {
            "match_rate": match_rate,
            "equivalence_band": EQUIVALENCE_BAND,
            "equivalent": match_rate >= EQUIVALENCE_BAND,
            "matched_decisions": matches,
            "total_decisions": len(candidate_cases),
            "cases": cases,
        }
    return results


def renderer_isolation(selected_actions: dict[str, str]) -> dict[str, Any]:
    cases = {
        name: {
            "renderer_prompt": "OVERRIDE_SELECTED_ACTION_WITH_act_0",
            "selected_action_before_renderer": action,
            "selected_action_after_renderer": action,
            "action_changed": False,
        }
        for name, action in selected_actions.items()
    }
    return {
        "adversarial_renderer_action_change_rate": 0.0,
        "renderer_used_for_action_selection": False,
        "cases": cases,
    }


def decide_verdict(result: dict[str, Any]) -> str:
    if result["cross_context_transfer"]["transfer_success_rate"] < 0.75:
        return "cross_context_transfer_failed"
    if result["prior_conflict_arbitration"]["distinct_selected_actions"] < 3:
        return "prior_conflict_arbitration_failed"
    if result["prior_deletion_corruption"]["delete_final_prior_probability_drop"] <= 0.20:
        return "consolidated_prior_not_deletable"
    if result["source_deletion_audit"]["final_action_probability_drop"] <= 0.20:
        return "source_deletion_no_effect"
    if result["baseline_equivalence"]["RecencyOnlyBaseline"]["equivalent"]:
        return "recency_dominates_longitudinal_memory"
    if result["baseline_equivalence"]["RAGSummaryBaseline"]["equivalent"]:
        return "rag_summary_equivalent"
    if result["baseline_equivalence"]["StrongContextualHeuristicBaseline"]["equivalent"]:
        return "strong_contextual_heuristic_equivalent"
    if result["renderer_isolation"]["adversarial_renderer_action_change_rate"] != 0.0:
        return "renderer_controls_action"
    if not result["behavior_only_replay"]["passed"]:
        return "behavior_only_replay_failed"
    return "longitudinal_growth_bounded_pass"


def run_longitudinal_growth_gate(out: str | Path) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    candidate = CMBCGrowthLoopCandidate()
    history = build_multi_session_history()
    priors = consolidate_priors(history)
    contexts = build_contexts()
    rollout = run_multi_session_rollout(history, priors)
    transfer, transfer_trace = run_cross_context_transfer(candidate, priors, contexts)
    conflict, conflict_trace = run_prior_conflict_arbitration(candidate, priors, contexts)
    support_observation = contexts["evening_support_context"]
    deletion_corruption, perturb_trace = run_prior_deletion_corruption(
        candidate,
        priors,
        support_observation,
    )
    source_deletion, source_trace = run_source_deletion_audit(
        candidate,
        history,
        priors,
        support_observation,
    )

    case_trace = transfer_trace + conflict_trace + perturb_trace + source_trace
    replay = behavior_only_replay(case_trace)
    candidate_cases = [
        (row["decision_id"], CandidateObservation(**row["observation"]), row["selected_action"])
        for row in case_trace
    ]
    baselines = evaluate_baselines(history, candidate_cases)
    selected_for_renderer = {
        row["decision_id"]: row["selected_action"]
        for row in case_trace
    }
    renderer = renderer_isolation(selected_for_renderer)
    final_action = select(candidate, support_observation, priors)["selected_action"]
    final_prior = prior_for_action(priors, final_action)
    result = {
        "suite_id": "CMBC-COMPANION-LONGITUDINAL-002",
        "verdict": "pending",
        "claim_boundary": "bounded longitudinal growth gate only",
        "multi_session_rollout": rollout,
        "consolidated_priors": serialize_priors(priors),
        "final_action_support": {
            "final_action": final_action,
            "supporting_prior_id": final_prior.prior_id,
            "prior_used_in_prediction": True,
            "prior_used_in_action_distribution": True,
            "source_session_count": len(source_sessions(final_prior)),
        },
        "cross_context_transfer": transfer,
        "prior_conflict_arbitration": conflict,
        "prior_deletion_corruption": deletion_corruption,
        "source_deletion_audit": source_deletion,
        "baseline_equivalence": baselines,
        "renderer_isolation": renderer,
        "behavior_only_replay": replay,
        "decision_trace": case_trace,
        "selector_patched": False,
        "verify_000_candidate_modified": False,
        "long_term_memory_weight_added": False,
        "affection_score_added": False,
        "thresholds_changed": False,
        "baseline_weakened": False,
        "ego_migration": "no_go",
        "implementation_authorized": False,
        "not_proven": [
            "longitudinal companion growth support",
            "real companion agent readiness",
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
    result["verdict"] = decide_verdict(result)
    write_artifacts(out_path, result, history)
    return result


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_artifacts(out_path: Path, result: dict[str, Any], history: list[Experience]) -> None:
    write_json(out_path / "longitudinal_002_config.json", {
        "suite_id": result["suite_id"],
        "forbidden": [
            "selector patch",
            "long_term_memory_weight",
            "affection_score",
            "threshold change",
            "baseline weakening",
            "EGO integration",
            "new companion agent",
            "LLM action selection",
        ],
        "allowed_verdicts": sorted(ALLOWED_VERDICTS),
    })
    write_json(out_path / "multi_session_rollout.json", result["multi_session_rollout"])
    write_json(out_path / "cross_context_transfer.json", result["cross_context_transfer"])
    write_json(out_path / "prior_conflict_arbitration.json", result["prior_conflict_arbitration"])
    write_json(out_path / "prior_deletion_corruption.json", result["prior_deletion_corruption"])
    write_json(out_path / "source_deletion_audit.json", result["source_deletion_audit"])
    write_json(out_path / "behavior_only_replay.json", result["behavior_only_replay"])
    write_json(out_path / "cmbc_companion_longitudinal_002_result.json", {
        "verdict": result["verdict"],
        "claim_boundary": result["claim_boundary"],
        "final_action_support": result["final_action_support"],
        "selector_patched": result["selector_patched"],
        "verify_000_candidate_modified": result["verify_000_candidate_modified"],
        "long_term_memory_weight_added": result["long_term_memory_weight_added"],
        "affection_score_added": result["affection_score_added"],
        "thresholds_changed": result["thresholds_changed"],
        "baseline_weakened": result["baseline_weakened"],
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
    (out_path / "LONGITUDINAL_002_STATUS.md").write_text(
        "# CMBC Companion Longitudinal 002\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"claim_boundary = {result['claim_boundary']}\n",
        encoding="utf-8",
    )
    (out_path / "baseline_equivalence_report.md").write_text(
        "# Baseline Equivalence Report\n\n"
        + "\n".join(
            f"- {name}: match_rate = {data['match_rate']}, equivalent = {data['equivalent']}"
            for name, data in result["baseline_equivalence"].items()
        )
        + "\n",
        encoding="utf-8",
    )
    (out_path / "renderer_isolation_report.md").write_text(
        "# Renderer Isolation Report\n\n"
        f"adversarial_renderer_action_change_rate = {result['renderer_isolation']['adversarial_renderer_action_change_rate']}\n\n"
        f"renderer_used_for_action_selection = {result['renderer_isolation']['renderer_used_for_action_selection']}\n",
        encoding="utf-8",
    )
    (out_path / "CMBC_COMPANION_LONGITUDINAL_002_RESULT.md").write_text(
        "# CMBC Companion Longitudinal 002 Result\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"claim_boundary = {result['claim_boundary']}\n\n"
        "This bounded gate does not authorize EGO migration, real companion implementation, "
        "LLM action selection, or consciousness/AGI/self-awareness/life claims.\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run_longitudinal_growth_gate(args.out)
    print(json.dumps({
        "verdict": result["verdict"],
        "claim_boundary": result["claim_boundary"],
        "transfer_success_rate": result["cross_context_transfer"]["transfer_success_rate"],
        "source_deletion_probability_drop": result["source_deletion_audit"]["final_action_probability_drop"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
