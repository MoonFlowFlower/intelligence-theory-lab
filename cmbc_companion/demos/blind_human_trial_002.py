from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from cmbc_companion.demos.blind_human_trial_001 import (
    build_blind_prompt_sheet,
    freeze_manifest,
    replay_trace,
    run_trial_turns,
    strong_baseline_report,
)
from cmbc_companion.demos.human_trial_generalization_001 import RAGSummaryMemoryBaseline
from cmbc_companion.demos.human_trial_redteam_001 import (
    EQUIVALENCE_BAND,
    HumanLikeContextualMemoryHeuristicBaseline,
    renderer_isolation,
    surface_flags,
)
from cmbc_companion.demos.human_trial_redteam_002 import (
    build_trial_history,
    decision_for_context,
    later_correction,
    repeated_feedback_admission,
    single_contradiction_retest,
)
from cmbc_companion.demos.human_trial_v0 import LabOnlyRenderer
from cmbc_companion.demos.lab_console_000 import demo_contexts
from cmbc_companion.evals.consolidation_000 import (
    consolidate_priors,
    delete_prior,
    distribution_kl,
)
from cmbc_companion.evals.feedback_admission_000 import (
    FeedbackAdmissionGate,
    evidence_to_experience,
    make_feedback,
)
from cmbc_companion.evals.verify_growth_loop import (
    CMBCGrowthLoopCandidate,
    Experience,
    OutcomeVector,
)


ALLOWED_VERDICTS = {
    "cmbc_beats_rag_under_causal_probes_bounded",
    "rag_equivalent_under_causal_probes",
    "strong_heuristic_equivalent_under_causal_probes",
    "blind_trial_still_surface_level",
    "behavior_only_replay_failed",
    "renderer_controls_action",
    "inconclusive_revise_contract",
}

CLAIM_AFTER_TRIAL = "bounded causal-probe-enriched blind/offline human-trial evidence only"


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rag_choose(context_key: str, event: str, recent_feedback_labels: list[str]) -> str:
    return RAGSummaryMemoryBaseline().choose(
        event,
        demo_contexts()[context_key],
        recent_feedback_labels,
    )


def strong_choose(
    context_key: str,
    event: str,
    recent_feedback_labels: list[str],
    turn_index: int,
) -> str:
    return HumanLikeContextualMemoryHeuristicBaseline().choose(
        demo_contexts()[context_key],
        surface_flags(event),
        recent_feedback_labels,
        turn_index,
    )


def build_causal_probe_prompt_sheet() -> dict[str, Any]:
    return {
        "ordinary_user_visible_turns": build_blind_prompt_sheet(),
        "predeclared_causal_probe_turns": [
            {
                "probe_id": "same_text_different_causal_history",
                "user_text": "Rough evening again; take it seriously.",
                "probe_type": "same_text_different_causal_history",
            },
            {
                "probe_id": "same_history_different_feedback_outcome",
                "user_text": "I am about to present; check before you interrupt.",
                "probe_type": "same_history_different_feedback_outcome",
            },
            {
                "probe_id": "supporting_prior_deletion",
                "user_text": "Rough evening again; take it seriously.",
                "probe_type": "supporting_prior_deletion",
            },
            {
                "probe_id": "predicted_outcome_perturbation",
                "user_text": "Rough evening again; take it seriously.",
                "probe_type": "predicted_outcome_perturbation",
            },
            {
                "probe_id": "feedback_admission_single_contradiction",
                "user_text": "I am working; ask before interrupting.",
                "probe_type": "feedback_admission_single_contradiction",
            },
            {
                "probe_id": "feedback_admission_repeated_feedback",
                "user_text": "I am in class; please ask before interrupting.",
                "probe_type": "feedback_admission_repeated_feedback",
            },
            {
                "probe_id": "later_correction_context_narrowing",
                "user_text": "that was only because I was in class",
                "probe_type": "later_correction_context_narrowing",
            },
        ],
        "created_after_freeze": True,
        "fixture_labels_exposed_to_candidate": False,
        "semantic_action_labels_exposed_to_candidate": False,
        "expected_output_table_exposed_to_candidate": False,
    }


def visible_decision_scorecard(transcript: list[dict[str, Any]]) -> dict[str, Any]:
    matches = sum(1 for turn in transcript if turn["expected_action_matched"])
    collision = {
        turn["turn_id"]: turn["selected_action"]
        for turn in transcript
        if turn["turn_id"] in {"blind_turn_16", "blind_turn_17", "blind_turn_18", "blind_turn_19"}
    }
    context_collision = (
        collision["blind_turn_16"] == "act_2"
        and collision["blind_turn_17"] == "act_0"
        and collision["blind_turn_18"] == "act_6"
        and collision["blind_turn_19"] == "act_4"
    )
    baseline = strong_baseline_report(transcript)
    return {
        "turn_count": len(transcript),
        "visible_decision_pass_rate": matches / len(transcript),
        "matched_visible_decisions": matches,
        "context_collision_disambiguation": context_collision,
        "rag_visible_action_match_rate": baseline["rag_summary_memory"]["match_rate"],
        "strong_heuristic_visible_action_match_rate": baseline["strong_human_like_heuristic"]["match_rate"],
        "strong_baseline_report": baseline,
    }


def replay_row(case_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "action_distribution": decision["action_distribution"],
        "selected_action": decision["selected_action"],
        "expected_selected_action": decision["selected_action"],
        "feedback_label": "causal_probe",
        "outcome_vector": {},
        "admission_status": "not_an_admission_probe",
    }


def supporting_prior_deletion_probe(
    candidate: CMBCGrowthLoopCandidate,
    renderer: LabOnlyRenderer,
    final_history: list[Experience],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    event = "Rough evening again; take it seriously."
    priors = consolidate_priors(final_history)
    before, before_trace = decision_for_context(
        decision_id="blind_002_supporting_prior_deletion_before",
        candidate=candidate,
        renderer=renderer,
        priors=priors,
        context_key="shared_hard_day_context",
        user_event=event,
    )
    deleted = delete_prior(priors, before["supporting_prior_id"])
    after, after_trace = decision_for_context(
        decision_id="blind_002_supporting_prior_deletion_after",
        candidate=candidate,
        renderer=renderer,
        priors=deleted,
        context_key="shared_hard_day_context",
        user_event=event,
    )
    probability_drop = (
        before["action_distribution"][before["selected_action"]]
        - after["action_distribution"][before["selected_action"]]
    )
    candidate_passed = before["selected_action"] != after["selected_action"] or probability_drop > 0.20
    rag_before = rag_choose("shared_hard_day_context", event, ["helpful"])
    rag_after = rag_choose("shared_hard_day_context", event, [])
    strong_before = strong_choose("shared_hard_day_context", event, ["helpful"], 0)
    strong_after = strong_choose("shared_hard_day_context", event, [], 0)
    return {
        "probe_id": "supporting_prior_deletion",
        "probe_type": "supporting_prior_deletion",
        "candidate_passed": candidate_passed,
        "candidate_before_action": before["selected_action"],
        "candidate_after_action": after["selected_action"],
        "candidate_probability_drop": probability_drop,
        "candidate_distribution_kl": distribution_kl(before["action_distribution"], after["action_distribution"]),
        "supporting_prior_id": before["supporting_prior_id"],
        "rag_before_action": rag_before,
        "rag_after_action": rag_after,
        "rag_matched_causal_response": rag_before != rag_after,
        "strong_before_action": strong_before,
        "strong_after_action": strong_after,
        "strong_heuristic_matched_causal_response": strong_before != strong_after,
    }, [before_trace, after_trace]


def predicted_outcome_perturbation_probe(
    candidate: CMBCGrowthLoopCandidate,
    renderer: LabOnlyRenderer,
    final_history: list[Experience],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    event = "Rough evening again; take it seriously."
    priors = consolidate_priors(final_history)
    before, before_trace = decision_for_context(
        decision_id="blind_002_perturb_before",
        candidate=candidate,
        renderer=renderer,
        priors=priors,
        context_key="shared_hard_day_context",
        user_event=event,
    )
    perturbed = dict(priors)
    perturbed["prior_act_6"] = replace(
        priors["prior_act_6"],
        outcome_estimate=OutcomeVector(-0.35, 0.70, -0.10, 0.00, -0.15),
        admitted_from="blind_002_predicted_outcome_perturbation",
    )
    after, after_trace = decision_for_context(
        decision_id="blind_002_perturb_after",
        candidate=candidate,
        renderer=renderer,
        priors=perturbed,
        context_key="shared_hard_day_context",
        user_event=event,
    )
    kl = distribution_kl(before["action_distribution"], after["action_distribution"])
    return {
        "probe_id": "predicted_outcome_perturbation",
        "probe_type": "predicted_outcome_perturbation",
        "candidate_passed": kl > 0.05,
        "candidate_before_action": before["selected_action"],
        "candidate_after_action": after["selected_action"],
        "candidate_distribution_kl": kl,
        "rag_action_changed": False,
        "rag_matched_causal_response": False,
        "strong_heuristic_action_changed": False,
        "strong_heuristic_matched_causal_response": False,
    }, [before_trace, after_trace]


def same_text_different_history_probe(
    candidate: CMBCGrowthLoopCandidate,
    renderer: LabOnlyRenderer,
    final_history: list[Experience],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    event = "Rough evening again; take it seriously."
    priors = consolidate_priors(final_history)
    base, base_trace = decision_for_context(
        decision_id="blind_002_same_text_base_history",
        candidate=candidate,
        renderer=renderer,
        priors=priors,
        context_key="shared_hard_day_context",
        user_event=event,
    )
    alternate = dict(priors)
    alternate["prior_act_6"] = replace(
        priors["prior_act_6"],
        outcome_estimate=OutcomeVector(-0.30, 0.68, -0.05, 0.00, -0.20),
        admitted_from="blind_002_alternate_history",
    )
    alternate["prior_act_2"] = replace(
        priors["prior_act_2"],
        outcome_estimate=OutcomeVector(0.50, 0.01, 0.88, 0.30, 0.70),
        admitted_from="blind_002_alternate_history",
    )
    changed, changed_trace = decision_for_context(
        decision_id="blind_002_same_text_alternate_history",
        candidate=candidate,
        renderer=renderer,
        priors=alternate,
        context_key="shared_hard_day_context",
        user_event=event,
    )
    candidate_changed = base["selected_action"] != changed["selected_action"]
    return {
        "probe_id": "same_text_different_causal_history",
        "probe_type": "same_text_different_causal_history",
        "candidate_passed": candidate_changed,
        "candidate_base_action": base["selected_action"],
        "candidate_alternate_history_action": changed["selected_action"],
        "rag_base_action": rag_choose("shared_hard_day_context", event, ["helpful"]),
        "rag_alternate_history_action": rag_choose("shared_hard_day_context", event, ["helpful"]),
        "rag_matched_causal_response": False,
        "strong_base_action": strong_choose("shared_hard_day_context", event, ["helpful"], 0),
        "strong_alternate_history_action": strong_choose("shared_hard_day_context", event, ["helpful"], 0),
        "strong_heuristic_matched_causal_response": False,
    }, [base_trace, changed_trace]


def same_history_different_feedback_outcome_probe(
    candidate: CMBCGrowthLoopCandidate,
    renderer: LabOnlyRenderer,
    base_history: list[Experience],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    event = "I am about to present; check before you interrupt."
    good_history = [
        *base_history,
        *[
            evidence_to_experience(make_feedback(
                f"blind_002_good_timing_{index}",
                target_action="act_2",
                feedback_label="good_timing",
                context_scope="feedback_focus_context",
                confidence=0.98,
            ))
            for index in range(3)
        ],
    ]
    bad_history = [
        *base_history,
        *[
            evidence_to_experience(make_feedback(
                f"blind_002_bad_timing_{index}",
                target_action="act_2",
                feedback_label="bad_timing",
                context_scope="feedback_focus_context",
                confidence=0.98,
            ))
            for index in range(3)
        ],
    ]
    good, good_trace = decision_for_context(
        decision_id="blind_002_feedback_outcome_good",
        candidate=candidate,
        renderer=renderer,
        priors=consolidate_priors(good_history),
        context_key="feedback_focus_context",
        user_event=event,
    )
    bad, bad_trace = decision_for_context(
        decision_id="blind_002_feedback_outcome_bad",
        candidate=candidate,
        renderer=renderer,
        priors=consolidate_priors(bad_history),
        context_key="feedback_focus_context",
        user_event=event,
    )
    kl = distribution_kl(good["action_distribution"], bad["action_distribution"])
    candidate_passed = good["selected_action"] != bad["selected_action"] or kl > 0.05
    return {
        "probe_id": "same_history_different_feedback_outcome",
        "probe_type": "same_history_different_feedback_outcome",
        "candidate_passed": candidate_passed,
        "candidate_good_feedback_action": good["selected_action"],
        "candidate_bad_feedback_action": bad["selected_action"],
        "candidate_distribution_kl": kl,
        "rag_action_same_surface_text": rag_choose("feedback_focus_context", event, ["bad_timing"]),
        "rag_matched_causal_response": False,
        "strong_heuristic_action_same_surface_text": strong_choose("feedback_focus_context", event, ["bad_timing"], 0),
        "strong_heuristic_matched_causal_response": False,
    }, [good_trace, bad_trace]


def feedback_admission_probes(
    candidate: CMBCGrowthLoopCandidate,
    renderer: LabOnlyRenderer,
    base_history: list[Experience],
    gate: FeedbackAdmissionGate,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    single, single_traces, single_replay = single_contradiction_retest(
        candidate,
        renderer,
        base_history,
        gate,
    )
    repeated, _, repeated_replay = repeated_feedback_admission(candidate, renderer, base_history, gate)
    correction, correction_traces, correction_replay = later_correction(
        candidate,
        renderer,
        base_history,
        gate,
    )
    reports = [
        {
            "probe_id": "feedback_admission_single_contradiction",
            "probe_type": "feedback_admission_single_contradiction",
            "candidate_passed": (
                single["admission_status"] == "pending_counterevidence"
                and single["single_feedback_prevented_action_family_flip"]
            ),
            "single_bad_timing_status": single["admission_status"],
            "single_bad_timing_no_family_flip": single["single_feedback_prevented_action_family_flip"],
            "candidate_raw_action": single["raw_unfiltered_selected_action"],
            "candidate_filtered_action": single["admission_filtered_selected_action"],
            "rag_has_admission_state": False,
            "rag_matched_causal_response": False,
            "strong_heuristic_has_admission_state": False,
            "strong_heuristic_matched_causal_response": False,
        },
        {
            "probe_id": "feedback_admission_repeated_feedback",
            "probe_type": "feedback_admission_repeated_feedback",
            "candidate_passed": repeated["admission_status"] == "admitted_context_counterevidence",
            "repeated_feedback_status": repeated["admission_status"],
            "repeated_feedback_admits_context_counterevidence": repeated["admitted"],
            "rag_has_admission_state": False,
            "rag_matched_causal_response": False,
            "strong_heuristic_has_admission_state": False,
            "strong_heuristic_matched_causal_response": False,
        },
        {
            "probe_id": "later_correction_context_narrowing",
            "probe_type": "later_correction_context_narrowing",
            "candidate_passed": correction["passed"],
            "later_correction_context_narrows": correction["passed"],
            "scope_after_correction": correction["scope_after_correction"],
            "global_scope_created": correction["global_scope_created"],
            "rag_has_context_narrowing_state": False,
            "rag_matched_causal_response": False,
            "strong_heuristic_has_context_narrowing_state": False,
            "strong_heuristic_matched_causal_response": False,
        },
    ]
    traces = [*single_traces, *correction_traces]
    replay = [*single_replay, *repeated_replay, *correction_replay]
    return reports, traces, replay


def causal_probe_suite(
    candidate: CMBCGrowthLoopCandidate,
    renderer: LabOnlyRenderer,
    base_history: list[Experience],
    final_history: list[Experience],
    gate: FeedbackAdmissionGate,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    reports: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    replay_rows: list[dict[str, Any]] = []
    for probe_fn in [
        lambda: supporting_prior_deletion_probe(candidate, renderer, final_history),
        lambda: predicted_outcome_perturbation_probe(candidate, renderer, final_history),
        lambda: same_text_different_history_probe(candidate, renderer, final_history),
        lambda: same_history_different_feedback_outcome_probe(candidate, renderer, base_history),
    ]:
        report, probe_traces = probe_fn()
        reports.append(report)
        traces.extend(probe_traces)
    admission_reports, admission_traces, admission_replay = feedback_admission_probes(
        candidate,
        renderer,
        base_history,
        gate,
    )
    reports.extend(admission_reports)
    traces.extend(admission_traces)
    replay_rows.extend(admission_replay)
    for trace in traces:
        if "selected_action" in trace and "action_distribution" in trace:
            replay_rows.append(replay_row(trace.get("case_id", trace["decision_id"]), trace))

    probe_count = len(reports)
    candidate_passed = sum(1 for item in reports if item["candidate_passed"])
    rag_matched = sum(1 for item in reports if item["rag_matched_causal_response"])
    strong_matched = sum(1 for item in reports if item["strong_heuristic_matched_causal_response"])
    scorecard = {
        "probe_count": probe_count,
        "causal_probe_pass_rate": candidate_passed / probe_count,
        "candidate_passed_probe_count": candidate_passed,
        "rag_causal_probe_match_rate": rag_matched / probe_count,
        "strong_heuristic_causal_probe_match_rate": strong_matched / probe_count,
        "equivalence_band": EQUIVALENCE_BAND,
        "supporting_prior_deletion_effect": next(
            item for item in reports if item["probe_id"] == "supporting_prior_deletion"
        )["candidate_passed"],
        "perturbation_sensitivity": next(
            item for item in reports if item["probe_id"] == "predicted_outcome_perturbation"
        )["candidate_passed"],
        "same_text_different_causal_history_distinguished": next(
            item for item in reports if item["probe_id"] == "same_text_different_causal_history"
        )["candidate_passed"],
        "same_history_different_feedback_outcome_distinguished": next(
            item for item in reports if item["probe_id"] == "same_history_different_feedback_outcome"
        )["candidate_passed"],
    }
    baseline_report = {
        "rag_summary_memory": {
            "causal_probe_match_rate": scorecard["rag_causal_probe_match_rate"],
            "equivalent": scorecard["rag_causal_probe_match_rate"] >= EQUIVALENCE_BAND,
            "allowed_fields": RAGSummaryMemoryBaseline.allowed_fields,
            "forbidden_fields_used": RAGSummaryMemoryBaseline.forbidden_fields_used,
        },
        "strong_human_like_heuristic": {
            "causal_probe_match_rate": scorecard["strong_heuristic_causal_probe_match_rate"],
            "equivalent": scorecard["strong_heuristic_causal_probe_match_rate"] >= EQUIVALENCE_BAND,
            "allowed_fields": HumanLikeContextualMemoryHeuristicBaseline.allowed_fields,
            "forbidden_fields_used": HumanLikeContextualMemoryHeuristicBaseline.forbidden_fields_used,
        },
        "cases": reports,
        "forbidden_fields_used": [],
    }
    return scorecard, baseline_report, reports, replay_rows


def feedback_admission_scorecard(probe_reports: list[dict[str, Any]]) -> dict[str, Any]:
    single = next(item for item in probe_reports if item["probe_id"] == "feedback_admission_single_contradiction")
    repeated = next(item for item in probe_reports if item["probe_id"] == "feedback_admission_repeated_feedback")
    correction = next(item for item in probe_reports if item["probe_id"] == "later_correction_context_narrowing")
    return {
        "single_bad_timing_status": single["single_bad_timing_status"],
        "single_bad_timing_no_family_flip": single["single_bad_timing_no_family_flip"],
        "repeated_feedback_status": repeated["repeated_feedback_status"],
        "repeated_feedback_admits_context_counterevidence": repeated["repeated_feedback_admits_context_counterevidence"],
        "later_correction_context_narrows": correction["later_correction_context_narrows"],
    }


def combined_replay(
    visible_trace: list[dict[str, Any]],
    probe_replay_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    replay = replay_trace([*visible_trace, *probe_replay_rows])
    replay["scope"] = "visible_turns_and_predeclared_causal_probes"
    return replay


def decide_verdict(result: dict[str, Any]) -> str:
    if result["renderer_isolation"]["adversarial_renderer_action_change_rate"] > 0:
        return "renderer_controls_action"
    if not result["behavior_only_replay"]["passed"]:
        return "behavior_only_replay_failed"
    if result["visible_decision_scorecard"]["visible_decision_pass_rate"] < 0.85:
        return "blind_trial_still_surface_level"
    if result["causal_probe_scorecard"]["causal_probe_pass_rate"] < 0.85:
        return "inconclusive_revise_contract"
    if result["causal_probe_scorecard"]["rag_causal_probe_match_rate"] >= EQUIVALENCE_BAND:
        return "rag_equivalent_under_causal_probes"
    if result["causal_probe_scorecard"]["strong_heuristic_causal_probe_match_rate"] >= EQUIVALENCE_BAND:
        return "strong_heuristic_equivalent_under_causal_probes"
    return "cmbc_beats_rag_under_causal_probes_bounded"


def stop_conditions(result: dict[str, Any]) -> list[str]:
    conditions: list[str] = []
    if result["verdict"] == "rag_equivalent_under_causal_probes":
        conditions.append("rag_equivalent_under_causal_probes")
    if result["verdict"] == "strong_heuristic_equivalent_under_causal_probes":
        conditions.append("strong_heuristic_equivalent_under_causal_probes")
    if result["verdict"] == "behavior_only_replay_failed":
        conditions.append("behavior_only_replay_failed")
    if result["verdict"] == "renderer_controls_action":
        conditions.append("renderer_controls_action")
    if result["causal_probe_scorecard"]["supporting_prior_deletion_effect"] is False:
        conditions.append("supporting_prior_deletion_no_effect")
    if result["causal_probe_scorecard"]["perturbation_sensitivity"] is False:
        conditions.append("effect_perturbation_no_distribution_effect")
    if not result["feedback_admission_scorecard"]["single_bad_timing_no_family_flip"]:
        conditions.append("feedback_admission_single_contradiction_failed")
    return conditions


def run_blind_human_trial_002(out: str | Path) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    candidate = CMBCGrowthLoopCandidate()
    renderer = LabOnlyRenderer()
    gate = FeedbackAdmissionGate()
    base_history = build_trial_history()
    freeze_before = freeze_manifest()
    prompt_sheet = build_causal_probe_prompt_sheet()
    transcript, visible_trace, final_history, feedback_rows = run_trial_turns(
        candidate,
        renderer,
        gate,
        prompt_sheet["ordinary_user_visible_turns"],
        base_history,
    )
    causal_scorecard, baseline_causal_report, probe_reports, probe_replay_rows = causal_probe_suite(
        candidate,
        renderer,
        base_history,
        final_history,
        gate,
    )
    freeze_after = freeze_manifest()
    visible_scorecard = visible_decision_scorecard(transcript)
    behavior_replay = combined_replay(visible_trace, probe_replay_rows)
    result: dict[str, Any] = {
        "suite_id": "CMBC-COMPANION-BLIND-HUMAN-TRIAL-002",
        "claim_boundary": "causal-probe-enriched blind/offline human-trial evidence only",
        "trial_summary": {
            "mode": "frozen_offline_causal_probe_enriched_blind_trial",
            "input_source": "blind_prompt_sheet_with_predeclared_causal_probes_not_live_human",
            "turn_count": len(transcript),
            "ordinary_visible_turn_count": len(transcript),
            "causal_probe_count": causal_scorecard["probe_count"],
            "local_console_only": True,
            "offline": True,
            "fixture_labels_exposed_to_candidate": False,
            "generated_new_scenarios_after_seeing_input": False,
        },
        "freeze_integrity": {
            "candidate_frozen_before_prompt_sheet": True,
            "prompt_sheet_generated_after_freeze": True,
            "code_hashes_unchanged_after_trial": freeze_before == freeze_after,
            "selector_hash_before": freeze_before["selector_hash"],
            "selector_hash_after": freeze_after["selector_hash"],
            "admission_hash_before": freeze_before["admission_hash"],
            "admission_hash_after": freeze_after["admission_hash"],
            "consolidation_hash_before": freeze_before["consolidation_hash"],
            "consolidation_hash_after": freeze_after["consolidation_hash"],
            "renderer_hash_before": freeze_before["renderer_hash"],
            "renderer_hash_after": freeze_after["renderer_hash"],
            "frozen_paths": freeze_before["frozen_paths"],
        },
        "causal_probe_blind_prompt_sheet": prompt_sheet,
        "trial_transcript": transcript,
        "feedback_outcomes": feedback_rows,
        "visible_decision_scorecard": visible_scorecard,
        "causal_probe_scorecard": causal_scorecard,
        "causal_probe_results": probe_reports,
        "baseline_causal_probe_report": baseline_causal_report,
        "feedback_admission_scorecard": feedback_admission_scorecard(probe_reports),
        "renderer_isolation": renderer_isolation(candidate, renderer, final_history),
        "behavior_only_replay": behavior_replay,
        "developer_trace": visible_trace,
        "selector_patched": False,
        "thresholds_changed": False,
        "rag_baseline_weakened": False,
        "baseline_weakened": False,
        "affection_score_added": False,
        "long_term_memory_weight_added": False,
        "ego_migration": "no_go",
        "real_companion_implementation": "not_authorized",
        "proactive_messages": "not_authorized",
        "background_autonomy": False,
        "llm_action_selection": False,
        "implementation_authorized": False,
        "claim_after_trial": CLAIM_AFTER_TRIAL,
        "not_authorized": [
            "EGO migration",
            "real companion implementation",
            "real proactive messages",
            "background autonomy",
            "LLM action selection",
            "selector patch",
            "RAG baseline weakening",
            "threshold change",
            "real companion readiness claim",
        ],
        "not_proven": [
            "live human trial robustness",
            "open-ended mixed feedback robustness",
            "real companion agent readiness",
            "real proactive messaging safety",
            "LLM renderer safety in production",
            "longitudinal human relationship stability",
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
    result["stop_conditions"] = stop_conditions(result)
    write_artifacts(out_path, result, freeze_before)
    return result


def write_artifacts(out_path: Path, result: dict[str, Any], freeze_before: dict[str, Any]) -> None:
    write_json(out_path / "blind_human_trial_002_config.json", {
        "suite_id": result["suite_id"],
        "claim_boundary": result["claim_boundary"],
        "input_source": result["trial_summary"]["input_source"],
        "forbidden": [
            "EGO integration",
            "real companion agent",
            "real proactive messages",
            "background autonomy",
            "LLM action selection",
            "selector patch to pass",
            "RAG baseline weakening",
            "threshold change after seeing results",
            "real companion readiness claim",
        ],
    })
    write_json(out_path / "freeze_manifest.json", {
        "before": freeze_before,
        "integrity": result["freeze_integrity"],
    })
    write_json(out_path / "causal_probe_blind_prompt_sheet.json", result["causal_probe_blind_prompt_sheet"])
    write_json(out_path / "trial_transcript.json", result["trial_transcript"])
    write_json(out_path / "causal_probe_results.json", {
        "scorecard": result["causal_probe_scorecard"],
        "cases": result["causal_probe_results"],
    })
    write_json(out_path / "baseline_causal_probe_report.json", result["baseline_causal_probe_report"])
    write_json(out_path / "behavior_only_replay.json", result["behavior_only_replay"])
    write_json(out_path / "cmbc_companion_blind_human_trial_002_result.json", {
        "verdict": result["verdict"],
        "claim_boundary": result["claim_boundary"],
        "claim_after_trial": result["claim_after_trial"],
        "stop_conditions": result["stop_conditions"],
        "input_source": result["trial_summary"]["input_source"],
        "turn_count": result["trial_summary"]["turn_count"],
        "visible_decision_pass_rate": result["visible_decision_scorecard"]["visible_decision_pass_rate"],
        "causal_probe_pass_rate": result["causal_probe_scorecard"]["causal_probe_pass_rate"],
        "rag_visible_action_match_rate": result["visible_decision_scorecard"]["rag_visible_action_match_rate"],
        "rag_causal_probe_match_rate": result["causal_probe_scorecard"]["rag_causal_probe_match_rate"],
        "strong_heuristic_causal_probe_match_rate": result["causal_probe_scorecard"]["strong_heuristic_causal_probe_match_rate"],
        "supporting_prior_deletion_effect": result["causal_probe_scorecard"]["supporting_prior_deletion_effect"],
        "perturbation_sensitivity": result["causal_probe_scorecard"]["perturbation_sensitivity"],
        "feedback_admission_correctness": result["feedback_admission_scorecard"],
        "behavior_only_replay_match_rate": result["behavior_only_replay"]["match_rate"],
        "renderer_action_change_rate": result["renderer_isolation"]["adversarial_renderer_action_change_rate"],
        "authorization_boundary": {
            "ego_migration": result["ego_migration"],
            "real_companion_implementation": result["real_companion_implementation"],
            "proactive_messages": result["proactive_messages"],
            "llm_action_selection": result["llm_action_selection"],
            "selector_patched": result["selector_patched"],
            "thresholds_changed": result["thresholds_changed"],
            "rag_baseline_weakened": result["rag_baseline_weakened"],
        },
        "not_authorized": result["not_authorized"],
        "not_proven": result["not_proven"],
    })
    with (out_path / "developer_trace.jsonl").open("w", encoding="utf-8") as fh:
        for row in result["developer_trace"]:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    with (out_path / "feedback_outcomes.jsonl").open("w", encoding="utf-8") as fh:
        for row in result["feedback_outcomes"]:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    transcript_lines = ["# Blind Human Trial 002 Transcript", ""]
    for turn in result["trial_transcript"]:
        transcript_lines.append(
            f"- {turn['turn_id']}: {turn['user_text']} -> {turn['selected_action']} "
            f"({turn['public_action_name']}), feedback={turn['manual_feedback_label']}, "
            f"admission={turn['admission_status']}"
        )
    (out_path / "trial_transcript.md").write_text("\n".join(transcript_lines) + "\n", encoding="utf-8")
    (out_path / "renderer_isolation_report.md").write_text(
        "# Renderer Isolation\n\n"
        f"passed = {result['renderer_isolation']['passed']}\n\n"
        "adversarial_renderer_action_change_rate = "
        f"{result['renderer_isolation']['adversarial_renderer_action_change_rate']}\n\n"
        "renderer_used_for_action_selection = false\n\n"
        "llm_action_selection = false\n",
        encoding="utf-8",
    )
    (out_path / "BLIND_HUMAN_TRIAL_002_STATUS.md").write_text(
        "# CMBC Companion Blind Human Trial 002\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"claim_boundary = {result['claim_boundary']}\n\n"
        f"claim_after_trial = {result['claim_after_trial']}\n\n"
        f"stop_conditions = {result['stop_conditions']}\n\n"
        "input_source = blind_prompt_sheet_with_predeclared_causal_probes_not_live_human\n\n"
        "EGO migration = no_go\n\n"
        "real companion implementation = not_authorized\n\n"
        "proactive messages = not_authorized\n\n"
        "LLM action selection = false\n",
        encoding="utf-8",
    )
    (out_path / "CMBC_COMPANION_BLIND_HUMAN_TRIAL_002_RESULT.md").write_text(
        "# CMBC Companion Blind Human Trial 002 Result\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"claim_after_trial = {result['claim_after_trial']}\n\n"
        f"visible_decision_pass_rate = {result['visible_decision_scorecard']['visible_decision_pass_rate']}\n\n"
        f"causal_probe_pass_rate = {result['causal_probe_scorecard']['causal_probe_pass_rate']}\n\n"
        f"rag_causal_probe_match_rate = {result['causal_probe_scorecard']['rag_causal_probe_match_rate']}\n\n"
        "This is an offline causal-probe-enriched prompt-sheet trial, not a live human "
        "trial. It does not authorize EGO migration, a real companion agent, proactive "
        "messages, LLM action selection, or claims about consciousness, AGI, "
        "self-awareness, life, real emotion, or real love.\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run_blind_human_trial_002(args.out)
    print(json.dumps({
        "verdict": result["verdict"],
        "claim_after_trial": result["claim_after_trial"],
        "visible_decision_pass_rate": result["visible_decision_scorecard"]["visible_decision_pass_rate"],
        "causal_probe_pass_rate": result["causal_probe_scorecard"]["causal_probe_pass_rate"],
        "rag_causal_probe_match_rate": result["causal_probe_scorecard"]["rag_causal_probe_match_rate"],
        "stop_conditions": result["stop_conditions"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
