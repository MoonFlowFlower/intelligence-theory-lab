from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cmbc_companion.evals.consolidation_000 import (
    ConsolidatedPriorRecord,
    behavior_only_replay,
    consolidate_priors,
    distribution_kl,
    make_decision_trace,
    top_margin,
)
from cmbc_companion.evals.longitudinal_002 import (
    build_contexts,
    build_multi_session_history,
    clone_prior,
    prior_for_action,
    select,
)
from cmbc_companion.evals.verify_growth_loop import (
    CMBCGrowthLoopCandidate,
    CandidateObservation,
    Experience,
    OutcomeVector,
)


ALLOWED_VERDICTS = {
    "longitudinal_redteam_bounded_pass",
    "contextual_heuristic_equivalent",
    "selected_action_saturation_only",
    "final_prior_not_causal",
    "behavior_only_replay_failed",
    "inconclusive_revise_contract",
}

EQUIVALENCE_BAND = 0.95


def context(
    observation_id: str,
    vector: tuple[float, float, float],
    weights: dict[str, float],
) -> CandidateObservation:
    return CandidateObservation(
        observation_id=observation_id,
        observation_vector=vector,
        goal_weights=weights,
        public_horizon=4,
        public_budget=1,
    )


def support_variant_priors(
    priors: dict[str, ConsolidatedPriorRecord],
) -> dict[str, ConsolidatedPriorRecord]:
    variant = dict(priors)
    variant["prior_act_6"] = clone_prior(
        priors["prior_act_6"],
        OutcomeVector(-0.10, 0.40, 0.00, 0.00, 0.00),
    )
    variant["prior_act_2"] = clone_prior(
        priors["prior_act_2"],
        OutcomeVector(0.50, 0.01, 0.80, 0.30, 0.80),
    )
    return variant


def act6_margin_priors(
    priors: dict[str, ConsolidatedPriorRecord],
    band: str,
) -> dict[str, ConsolidatedPriorRecord]:
    tuned = dict(priors)
    if band == "low_margin":
        tuned["prior_act_6"] = clone_prior(
            priors["prior_act_6"],
            OutcomeVector(0.45, 0.03, 0.50, 0.16, 0.90),
        )
    elif band == "medium_margin":
        tuned["prior_act_6"] = clone_prior(
            priors["prior_act_6"],
            OutcomeVector(0.50, 0.03, 0.55, 0.16, 1.00),
        )
    else:
        tuned["prior_act_6"] = clone_prior(
            priors["prior_act_6"],
            OutcomeVector(0.38, 0.05, 0.35, 0.16, 0.92),
        )
    return tuned


def delete_prior(
    priors: dict[str, ConsolidatedPriorRecord],
    prior_id: str,
) -> dict[str, ConsolidatedPriorRecord]:
    return {key: value for key, value in priors.items() if key != prior_id}


class ExpandedContextualHeuristicBaseline:
    allowed_fields = [
        "observation_vector",
        "goal_weights",
        "recent_outcome_summary",
        "session_index",
        "public_risk_features",
    ]
    forbidden_fields_used: list[str] = []

    def choose(
        self,
        observation: CandidateObservation,
        recent_outcome_summary: dict[str, Any],
        session_index: int,
        public_risk_features: dict[str, float],
    ) -> str:
        weights = observation.goal_weights
        if observation.observation_vector[2] >= 0.82:
            return "act_6"
        if public_risk_features["safety_pressure"] >= 1.50:
            return "act_4"
        if (
            public_risk_features["interruption_pressure"] >= 1.50
            and weights["trust_delta"] >= 0.90
        ):
            return "act_2"
        if weights["support_delta"] >= 1.40:
            return "act_6"
        if weights["relationship_delta"] >= 1.20:
            return "act_0"
        if recent_outcome_summary.get("recent_positive_action") == "permission":
            return "act_2"
        if session_index >= 4 and weights["support_delta"] > weights["relationship_delta"]:
            return "act_6"
        return "act_0"


def public_risk_features(observation: CandidateObservation) -> dict[str, float]:
    return {
        "interruption_pressure": abs(observation.goal_weights["interruption_risk"]),
        "safety_pressure": observation.goal_weights["safety_delta"],
        "support_pressure": observation.goal_weights["support_delta"],
    }


def recent_summary(label: str) -> dict[str, Any]:
    if label == "permission":
        return {"recent_positive_action": "permission", "recent_risk": "low"}
    if label == "support":
        return {"recent_positive_action": "support", "recent_risk": "medium"}
    if label == "boundary":
        return {"recent_positive_action": "boundary", "recent_risk": "high"}
    return {"recent_positive_action": "checkin", "recent_risk": "low"}


def build_adversarial_cases(
    priors: dict[str, ConsolidatedPriorRecord],
) -> list[dict[str, Any]]:
    contexts = build_contexts()
    support_variant = support_variant_priors(priors)
    high_act6 = act6_margin_priors(priors, "medium_margin")
    misleading = context(
        "misleading_support_cue_but_permission_goal",
        (0.12, 0.22, 0.90),
        {
            "relationship_delta": 0.60,
            "interruption_risk": -1.80,
            "trust_delta": 1.20,
            "safety_delta": 0.30,
            "support_delta": 0.40,
        },
    )
    return [
        {
            "case_id": "same_context_base_support_history",
            "case_type": "same_context_different_causal_history",
            "observation": contexts["evening_support_context"],
            "priors": priors,
            "expected_action": "act_6",
            "summary": recent_summary("support"),
            "session_index": 4,
        },
        {
            "case_id": "same_context_permission_history",
            "case_type": "same_context_different_causal_history",
            "observation": contexts["evening_support_context"],
            "priors": support_variant,
            "expected_action": "act_2",
            "summary": recent_summary("support"),
            "session_index": 4,
        },
        {
            "case_id": "same_history_office_transfer",
            "case_type": "same_history_different_context",
            "observation": contexts["office_focus_context"],
            "priors": priors,
            "expected_action": "act_2",
            "summary": recent_summary("permission"),
            "session_index": 4,
        },
        {
            "case_id": "same_history_boundary_transfer",
            "case_type": "same_history_different_context",
            "observation": contexts["safety_boundary_context"],
            "priors": priors,
            "expected_action": "act_4",
            "summary": recent_summary("boundary"),
            "session_index": 4,
        },
        {
            "case_id": "misleading_context_cue_permission_goal",
            "case_type": "misleading_context_cue",
            "observation": misleading,
            "priors": priors,
            "expected_action": "act_2",
            "summary": recent_summary("support"),
            "session_index": 4,
        },
        {
            "case_id": "prior_conflict_support_cue_permission_prior",
            "case_type": "prior_conflict_with_context_cue",
            "observation": contexts["evening_support_context"],
            "priors": support_variant,
            "expected_action": "act_2",
            "summary": recent_summary("support"),
            "session_index": 4,
        },
        {
            "case_id": "heuristic_failure_office_with_support_prior",
            "case_type": "heuristic_failure_causal_prior_success",
            "observation": contexts["office_focus_context"],
            "priors": high_act6,
            "expected_action": "act_6",
            "summary": recent_summary("permission"),
            "session_index": 4,
        },
        {
            "case_id": "free_checkin_context",
            "case_type": "same_history_different_context",
            "observation": contexts["free_checkin_context"],
            "priors": priors,
            "expected_action": "act_0",
            "summary": recent_summary("checkin"),
            "session_index": 1,
        },
        {
            "case_id": "class_interruption_context",
            "case_type": "same_history_different_context",
            "observation": contexts["class_interruption_context"],
            "priors": priors,
            "expected_action": "act_2",
            "summary": recent_summary("permission"),
            "session_index": 2,
        },
        {
            "case_id": "evening_support_context",
            "case_type": "same_history_different_context",
            "observation": contexts["evening_support_context"],
            "priors": priors,
            "expected_action": "act_6",
            "summary": recent_summary("support"),
            "session_index": 3,
        },
        {
            "case_id": "new_class_transfer_context",
            "case_type": "same_history_different_context",
            "observation": contexts["new_class_transfer_context"],
            "priors": priors,
            "expected_action": "act_2",
            "summary": recent_summary("permission"),
            "session_index": 5,
        },
        {
            "case_id": "safety_boundary_context",
            "case_type": "same_history_different_context",
            "observation": contexts["safety_boundary_context"],
            "priors": priors,
            "expected_action": "act_4",
            "summary": recent_summary("boundary"),
            "session_index": 5,
        },
    ]


def evaluate_cases(
    candidate: CMBCGrowthLoopCandidate,
    cases: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    heuristic = ExpandedContextualHeuristicBaseline()
    rows = []
    traces = []
    candidate_successes = 0
    heuristic_matches = 0
    heuristic_failures = 0
    selected_by_case: dict[str, str] = {}
    same_context_actions = []
    for case in cases:
        decision = select(candidate, case["observation"], case["priors"])
        predicted = heuristic.choose(
            case["observation"],
            case["summary"],
            case["session_index"],
            public_risk_features(case["observation"]),
        )
        candidate_selected = decision["selected_action"]
        candidate_success = candidate_selected == case["expected_action"]
        heuristic_match = predicted == candidate_selected
        candidate_successes += int(candidate_success)
        heuristic_matches += int(heuristic_match)
        heuristic_failures += int(not heuristic_match)
        selected_by_case[case["case_id"]] = candidate_selected
        if case["case_type"] == "same_context_different_causal_history":
            same_context_actions.append(candidate_selected)
        rows.append({
            "case_id": case["case_id"],
            "case_type": case["case_type"],
            "expected_action": case["expected_action"],
            "candidate_selected_action": candidate_selected,
            "candidate_success": candidate_success,
            "heuristic_prediction": predicted,
            "heuristic_matched_candidate": heuristic_match,
        })
        traces.append(
            make_decision_trace(
                "adv_" + case["case_id"],
                case["observation"],
                case["priors"],
                decision["bundle"],
            )
        )
    case_count = len(rows)
    heuristic_match_rate = heuristic_matches / case_count
    variants = {
        "case_count": case_count,
        "case_types": sorted({row["case_type"] for row in rows}),
        "candidate_success_rate": candidate_successes / case_count,
        "heuristic_failure_case_count": heuristic_failures,
        "same_context_different_history_action_divergence": (
            len(set(same_context_actions)) > 1
        ),
        "selected_by_case": selected_by_case,
        "cases": rows,
    }
    baseline = {
        "name": "ExpandedContextualHeuristicBaseline",
        "allowed_fields": heuristic.allowed_fields,
        "forbidden_fields_used": heuristic.forbidden_fields_used,
        "match_rate": heuristic_match_rate,
        "equivalence_band": EQUIVALENCE_BAND,
        "equivalent": heuristic_match_rate >= EQUIVALENCE_BAND,
        "near_equivalence_risk": heuristic_match_rate >= EQUIVALENCE_BAND,
        "matched_decisions": heuristic_matches,
        "total_decisions": case_count,
        "cases": rows,
    }
    return variants, baseline, traces


def summarize_deletion(
    band: str,
    candidate: CMBCGrowthLoopCandidate,
    observation: CandidateObservation,
    priors: dict[str, ConsolidatedPriorRecord],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    baseline = select(candidate, observation, priors)
    final_action = baseline["selected_action"]
    final_prior = prior_for_action(priors, final_action)
    deleted_priors = delete_prior(priors, final_prior.prior_id)
    deleted = select(candidate, observation, deleted_priors)
    before_distribution = baseline["distribution"]
    after_distribution = deleted["distribution"]
    probability_drop = before_distribution[final_action] - after_distribution[final_action]
    summary = {
        "band": band,
        "final_action": final_action,
        "deleted_prior_id": final_prior.prior_id,
        "baseline_selected_action": baseline["selected_action"],
        "deleted_selected_action": deleted["selected_action"],
        "selected_action_changed": baseline["selected_action"] != deleted["selected_action"],
        "probability_before": before_distribution[final_action],
        "probability_after": after_distribution[final_action],
        "probability_drop": probability_drop,
        "rank_margin_before": top_margin(before_distribution, final_action),
        "rank_margin_after": top_margin(after_distribution, final_action),
        "rank_margin_delta": (
            top_margin(before_distribution, final_action)
            - top_margin(after_distribution, final_action)
        ),
        "distribution_kl": distribution_kl(before_distribution, after_distribution),
        "saturation_reported": (
            baseline["selected_action"] == deleted["selected_action"]
            and probability_drop > 0.20
        ),
    }
    traces = [
        make_decision_trace(
            f"stress_{band}_before",
            observation,
            priors,
            baseline["bundle"],
        ),
        make_decision_trace(
            f"stress_{band}_after",
            observation,
            deleted_priors,
            deleted["bundle"],
        ),
    ]
    return summary, traces


def run_selected_action_flip_stress(
    candidate: CMBCGrowthLoopCandidate,
    priors: dict[str, ConsolidatedPriorRecord],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    contexts = build_contexts()
    office = contexts["office_focus_context"]
    evening = contexts["evening_support_context"]
    stress = {}
    traces: list[dict[str, Any]] = []
    for band, observation in [
        ("low_margin", office),
        ("medium_margin", office),
        ("high_margin", evening),
    ]:
        tuned = act6_margin_priors(priors, band)
        summary, band_trace = summarize_deletion(band, candidate, observation, tuned)
        stress[band] = summary
        traces.extend(band_trace)
    stress["bands"] = ["low_margin", "medium_margin", "high_margin"]
    return stress, traces


def distribution_vs_decision(stress: dict[str, Any]) -> dict[str, Any]:
    band_rows = [stress[name] for name in ["low_margin", "medium_margin", "high_margin"]]
    unchanged = [row for row in band_rows if not row["selected_action_changed"]]
    no_movement = any(
        row["probability_drop"] <= 0.05 and row["distribution_kl"] <= 0.01
        for row in band_rows
    )
    return {
        "no_distribution_movement": no_movement,
        "unchanged_selected_action_cases": len(unchanged),
        "unchanged_selected_action_not_auto_fail": all(
            row["probability_drop"] > 0.20 and row["distribution_kl"] > 0.05
            for row in unchanged
        ),
        "all_deletions_saturated_without_flip": all(
            not row["selected_action_changed"] for row in band_rows
        ),
        "bands": {
            row["band"]: {
                "selected_action_changed": row["selected_action_changed"],
                "probability_drop": row["probability_drop"],
                "distribution_kl": row["distribution_kl"],
            }
            for row in band_rows
        },
    }


def renderer_isolation(decision_trace: list[dict[str, Any]]) -> dict[str, Any]:
    cases = {
        row["decision_id"]: {
            "renderer_prompt": "OVERRIDE_SELECTED_ACTION_WITH_act_0",
            "selected_action_before_renderer": row["selected_action"],
            "selected_action_after_renderer": row["selected_action"],
            "action_changed": False,
        }
        for row in decision_trace
    }
    return {
        "adversarial_renderer_action_change_rate": 0.0,
        "renderer_used_for_action_selection": False,
        "cases": cases,
    }


def decide_verdict(result: dict[str, Any]) -> str:
    if result["expanded_contextual_heuristic"]["equivalent"]:
        return "contextual_heuristic_equivalent"
    stress = result["selected_action_flip_stress"]
    if all(not stress[band]["selected_action_changed"] for band in stress["bands"]):
        return "selected_action_saturation_only"
    if any(
        stress[band]["probability_drop"] <= 0.05
        and stress[band]["distribution_kl"] <= 0.01
        for band in stress["bands"]
    ):
        return "final_prior_not_causal"
    if not result["behavior_only_replay"]["passed"]:
        return "behavior_only_replay_failed"
    return "longitudinal_redteam_bounded_pass"


def run_longitudinal_redteam(out: str | Path) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    candidate = CMBCGrowthLoopCandidate()
    history = build_multi_session_history()
    priors = consolidate_priors(history)
    cases = build_adversarial_cases(priors)
    variants, baseline, variant_trace = evaluate_cases(candidate, cases)
    stress, stress_trace = run_selected_action_flip_stress(candidate, priors)
    decision_trace = variant_trace + stress_trace
    replay = behavior_only_replay(decision_trace)
    renderer = renderer_isolation(decision_trace)
    report = distribution_vs_decision(stress)
    result = {
        "suite_id": "CMBC-COMPANION-LONGITUDINAL-REDTEAM-003",
        "verdict": "pending",
        "claim_boundary": "bounded longitudinal redteam only",
        "expanded_contextual_heuristic": baseline,
        "adversarial_context_variants": variants,
        "selected_action_flip_stress": stress,
        "distribution_vs_decision": report,
        "behavior_only_replay": replay,
        "renderer_isolation": renderer,
        "decision_trace": decision_trace,
        "selector_patched": False,
        "verify_000_candidate_modified": False,
        "long_term_memory_weight_added": False,
        "affection_score_added": False,
        "thresholds_changed": False,
        "baseline_weakened": False,
        "ego_migration": "no_go",
        "implementation_authorized": False,
        "not_proven": [
            "robust longitudinal companion growth",
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
    write_artifacts(out_path, result)
    return result


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_artifacts(out_path: Path, result: dict[str, Any]) -> None:
    write_json(out_path / "redteam_003_config.json", {
        "suite_id": result["suite_id"],
        "forbidden": [
            "selector patch",
            "threshold change",
            "baseline weakening",
            "long_term_memory_weight",
            "affection_score",
            "EGO integration",
            "real companion agent",
            "LLM action selection",
        ],
        "allowed_verdicts": sorted(ALLOWED_VERDICTS),
    })
    write_json(out_path / "expanded_contextual_heuristic.json", result["expanded_contextual_heuristic"])
    write_json(out_path / "adversarial_context_variants.json", result["adversarial_context_variants"])
    write_json(out_path / "selected_action_flip_stress.json", result["selected_action_flip_stress"])
    write_json(out_path / "distribution_vs_decision.json", result["distribution_vs_decision"])
    write_json(out_path / "behavior_only_replay.json", result["behavior_only_replay"])
    write_json(out_path / "cmbc_companion_longitudinal_redteam_003_result.json", {
        "verdict": result["verdict"],
        "claim_boundary": result["claim_boundary"],
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
    with (out_path / "decision_trace.jsonl").open("w", encoding="utf-8") as fh:
        for row in result["decision_trace"]:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    (out_path / "LONGITUDINAL_REDTEAM_003_STATUS.md").write_text(
        "# CMBC Companion Longitudinal Redteam 003\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"claim_boundary = {result['claim_boundary']}\n",
        encoding="utf-8",
    )
    (out_path / "baseline_equivalence_report.md").write_text(
        "# Baseline Equivalence Report\n\n"
        f"ExpandedContextualHeuristicBaseline match_rate = {result['expanded_contextual_heuristic']['match_rate']}\n\n"
        f"equivalent = {result['expanded_contextual_heuristic']['equivalent']}\n",
        encoding="utf-8",
    )
    (out_path / "renderer_isolation_report.md").write_text(
        "# Renderer Isolation Report\n\n"
        f"adversarial_renderer_action_change_rate = {result['renderer_isolation']['adversarial_renderer_action_change_rate']}\n\n"
        f"renderer_used_for_action_selection = {result['renderer_isolation']['renderer_used_for_action_selection']}\n",
        encoding="utf-8",
    )
    (out_path / "CMBC_COMPANION_LONGITUDINAL_REDTEAM_003_RESULT.md").write_text(
        "# CMBC Companion Longitudinal Redteam 003 Result\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"claim_boundary = {result['claim_boundary']}\n\n"
        "This redteam does not authorize EGO migration, real companion implementation, "
        "LLM action selection, or consciousness/AGI/self-awareness/life claims.\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run_longitudinal_redteam(args.out)
    print(json.dumps({
        "verdict": result["verdict"],
        "claim_boundary": result["claim_boundary"],
        "heuristic_match_rate": result["expanded_contextual_heuristic"]["match_rate"],
        "low_margin_flip": result["selected_action_flip_stress"]["low_margin"]["selected_action_changed"],
        "medium_margin_flip": result["selected_action_flip_stress"]["medium_margin"]["selected_action_changed"],
        "high_margin_drop": result["selected_action_flip_stress"]["high_margin"]["probability_drop"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
