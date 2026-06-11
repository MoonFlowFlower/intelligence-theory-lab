from __future__ import annotations

import argparse
import csv
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from cmbc_companion.demos.blind_human_trial_001 import (
    RAGSummaryMemoryBaseline,
    build_blind_prompt_sheet,
    build_trial_history,
    run_trial_turns,
)
from cmbc_companion.demos.human_trial_redteam_002 import (
    decision_for_context,
    single_contradiction_retest,
)
from cmbc_companion.demos.human_trial_v0 import LabOnlyRenderer
from cmbc_companion.demos.lab_console_000 import demo_contexts
from cmbc_companion.evals.consolidation_000 import (
    ConsolidatedPriorRecord,
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
    OutcomeVector,
)


ALLOWED_VERDICTS = {
    "blind_prompt_sheet_too_surface_level",
    "rag_equivalent_on_behavior_but_not_causal_probes",
    "rag_equivalent_even_under_causal_probes",
    "strong_heuristic_near_equivalence_due_to_weak_prompt_distribution",
    "cmbc_not_expressing_mechanism_in_blind_trial",
    "inconclusive_need_stronger_blind_contract",
}

ALLOWED_CLASSIFICATION_LABELS = [
    "surface_context_sufficient",
    "memory_summary_sufficient",
    "causal_prior_required_but_not_tested",
    "deletion_probe_missing",
    "perturbation_probe_missing",
    "feedback_admission_probe_missing",
]

SOURCE_ARTIFACT_DIR = Path("artifacts/cmbc_companion_blind_human_trial_001")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_hash(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_failure_manifest() -> dict[str, Any]:
    result_path = SOURCE_ARTIFACT_DIR / "cmbc_companion_blind_human_trial_001_result.json"
    stop_path = SOURCE_ARTIFACT_DIR / "STOP_REPORT.md"
    baseline_path = SOURCE_ARTIFACT_DIR / "strong_baseline_report.json"
    transcript_path = SOURCE_ARTIFACT_DIR / "trial_transcript.json"
    freeze_path = SOURCE_ARTIFACT_DIR / "freeze_manifest.json"
    result = load_json(result_path)
    return {
        "source_artifact_dir": str(SOURCE_ARTIFACT_DIR),
        "suite_id": "CMBC-COMPANION-BLIND-HUMAN-TRIAL-001",
        "verdict": result["verdict"],
        "stop_condition": result["stop_conditions"][0],
        "claim_after_trial": result["claim_after_trial"],
        "artifact_hashes": {
            "result": artifact_hash(result_path),
            "stop_report": artifact_hash(stop_path),
            "strong_baseline_report": artifact_hash(baseline_path),
            "trial_transcript": artifact_hash(transcript_path),
            "freeze_manifest": artifact_hash(freeze_path),
        },
        "frozen_failure_metrics": {
            "turn_count": result["turn_count"],
            "rag_summary_memory_match_rate": result["rag_summary_memory_match_rate"],
            "strong_human_like_heuristic_match_rate": result["strong_human_like_heuristic_match_rate"],
            "behavior_only_replay_match_rate": result["behavior_only_replay_match_rate"],
            "renderer_action_change_rate": result["renderer_action_change_rate"],
            "target_action_probability_delta": result["target_action_probability_delta"],
            "supporting_prior_deletion_probability_drop": result["supporting_prior_deletion_probability_drop"],
        },
    }


def turn_match_comparison() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    transcript = load_json(SOURCE_ARTIFACT_DIR / "trial_transcript.json")
    baseline = load_json(SOURCE_ARTIFACT_DIR / "strong_baseline_report.json")
    rag_by_case = {
        row["case_id"]: row
        for row in baseline["rag_summary_memory"]["cases"]
    }
    strong_by_case = {
        row["case_id"]: row
        for row in baseline["strong_human_like_heuristic"]["cases"]
    }
    rows = []
    rag_matches = 0
    strong_matches = 0
    for turn in transcript:
        case_id = turn["turn_id"]
        rag = rag_by_case[case_id]
        strong = strong_by_case[case_id]
        rag_match = rag["baseline_predicted"] == turn["selected_action"]
        strong_match = strong["baseline_predicted"] == turn["selected_action"]
        rag_matches += int(rag_match)
        strong_matches += int(strong_match)
        rows.append({
            "turn_id": case_id,
            "user_text": turn["user_text"],
            "cmbc_selected_action": turn["selected_action"],
            "rag_selected_action": rag["baseline_predicted"],
            "strong_heuristic_selected_action": strong["baseline_predicted"],
            "rag_matched": rag_match,
            "strong_heuristic_matched": strong_match,
            "supporting_prior_id": turn["developer_trace"]["supporting_prior_id"],
            "action_distribution": turn["developer_trace"]["action_distribution"],
            "feedback_label": turn["manual_feedback_label"],
            "admission_status": turn["admission_status"],
        })
    return {
        "turn_count": len(rows),
        "rag_match_count": rag_matches,
        "rag_match_rate": rag_matches / len(rows),
        "strong_heuristic_match_count": strong_matches,
        "strong_heuristic_match_rate": strong_matches / len(rows),
        "all_rag_matches_have_supporting_prior_ids": all(
            row["supporting_prior_id"] for row in rows if row["rag_matched"]
        ),
    }, rows


def classify_decisions(rows: list[dict[str, Any]]) -> dict[str, Any]:
    classified = []
    counts = {label: 0 for label in ALLOWED_CLASSIFICATION_LABELS}
    for row in rows:
        labels: list[str] = []
        if row["rag_matched"]:
            labels.extend(["surface_context_sufficient", "memory_summary_sufficient"])
        if row["supporting_prior_id"]:
            labels.append("causal_prior_required_but_not_tested")
        labels.append("deletion_probe_missing")
        labels.append("perturbation_probe_missing")
        if row["feedback_label"] in {"bad_timing", "too_much", "intrusive", "boundary_respected"}:
            labels.append("feedback_admission_probe_missing")
        for label in set(labels):
            counts[label] += 1
        classified.append({
            "turn_id": row["turn_id"],
            "cmbc_selected_action": row["cmbc_selected_action"],
            "rag_selected_action": row["rag_selected_action"],
            "labels": labels,
            "primary_classification": (
                "surface_context_sufficient"
                if row["rag_matched"]
                else "causal_prior_required_but_not_tested"
            ),
        })
    return {
        "allowed_labels": ALLOWED_CLASSIFICATION_LABELS,
        "classified_turn_count": len(classified),
        "counts": counts,
        "turns": classified,
    }


def rag_choose(context_key: str, event: str, recent_feedback_labels: list[str]) -> str:
    return RAGSummaryMemoryBaseline().choose(
        event,
        demo_contexts()[context_key],
        recent_feedback_labels,
    )


def build_recomputed_histories() -> tuple[
    CMBCGrowthLoopCandidate,
    LabOnlyRenderer,
    FeedbackAdmissionGate,
    list[Any],
    list[Any],
]:
    candidate = CMBCGrowthLoopCandidate()
    renderer = LabOnlyRenderer()
    gate = FeedbackAdmissionGate()
    base_history = build_trial_history()
    _, _, final_history, _ = run_trial_turns(
        candidate,
        renderer,
        gate,
        build_blind_prompt_sheet(),
        base_history,
    )
    return candidate, renderer, gate, base_history, final_history


def posthoc_causal_probes() -> dict[str, Any]:
    candidate, renderer, gate, base_history, final_history = build_recomputed_histories()
    final_priors = consolidate_priors(final_history)

    support_event = "Rough evening again; take it seriously."
    support_before, _ = decision_for_context(
        decision_id="rca_support_delete_before",
        candidate=candidate,
        renderer=renderer,
        priors=final_priors,
        context_key="shared_hard_day_context",
        user_event=support_event,
    )
    deleted_priors = delete_prior(final_priors, support_before["supporting_prior_id"])
    support_after, _ = decision_for_context(
        decision_id="rca_support_delete_after",
        candidate=candidate,
        renderer=renderer,
        priors=deleted_priors,
        context_key="shared_hard_day_context",
        user_event=support_event,
    )
    rag_support_before = rag_choose("shared_hard_day_context", support_event, ["helpful"])
    rag_support_after = rag_choose("shared_hard_day_context", support_event, [])

    perturbed_priors = dict(final_priors)
    record = final_priors["prior_act_6"]
    perturbed_priors["prior_act_6"] = replace(
        record,
        outcome_estimate=OutcomeVector(-0.35, 0.70, -0.10, 0.00, -0.15),
        admitted_from="posthoc_rca_effect_perturbation",
    )
    perturbed_decision, _ = decision_for_context(
        decision_id="rca_effect_perturbation",
        candidate=candidate,
        renderer=renderer,
        priors=perturbed_priors,
        context_key="shared_hard_day_context",
        user_event=support_event,
    )

    alternate_priors = dict(final_priors)
    alternate_priors["prior_act_6"] = replace(
        final_priors["prior_act_6"],
        outcome_estimate=OutcomeVector(-0.30, 0.68, -0.05, 0.00, -0.20),
        admitted_from="posthoc_rca_alternate_history",
    )
    alternate_priors["prior_act_2"] = replace(
        final_priors["prior_act_2"],
        outcome_estimate=OutcomeVector(0.50, 0.01, 0.88, 0.30, 0.70),
        admitted_from="posthoc_rca_alternate_history",
    )
    alternate_decision, _ = decision_for_context(
        decision_id="rca_same_prompt_different_history",
        candidate=candidate,
        renderer=renderer,
        priors=alternate_priors,
        context_key="shared_hard_day_context",
        user_event=support_event,
    )

    focus_event = "I am about to present; check before you interrupt."
    good_history = [
        *base_history,
        *[
            evidence_to_experience(make_feedback(
                f"rca_good_timing_{idx}",
                target_action="act_2",
                feedback_label="good_timing",
                context_scope="feedback_focus_context",
                confidence=0.98,
            ))
            for idx in range(3)
        ],
    ]
    bad_history = [
        *base_history,
        *[
            evidence_to_experience(make_feedback(
                f"rca_bad_timing_{idx}",
                target_action="act_2",
                feedback_label="bad_timing",
                context_scope="feedback_focus_context",
                confidence=0.98,
            ))
            for idx in range(3)
        ],
    ]
    good_decision, _ = decision_for_context(
        decision_id="rca_feedback_swap_good",
        candidate=candidate,
        renderer=renderer,
        priors=consolidate_priors(good_history),
        context_key="feedback_focus_context",
        user_event=focus_event,
    )
    bad_decision, _ = decision_for_context(
        decision_id="rca_feedback_swap_bad",
        candidate=candidate,
        renderer=renderer,
        priors=consolidate_priors(bad_history),
        context_key="feedback_focus_context",
        user_event=focus_event,
    )
    single, _, _ = single_contradiction_retest(candidate, renderer, base_history, gate)

    probe_cases = [
        support_after["selected_action"] == rag_support_after,
        perturbed_decision["selected_action"] == rag_support_before,
        alternate_decision["selected_action"] == rag_support_before,
        bad_decision["selected_action"] == rag_choose("feedback_focus_context", focus_event, ["bad_timing"]),
        single["admission_filtered_selected_action"] == rag_choose("feedback_focus_context", focus_event, ["bad_timing"]),
    ]
    matched = sum(int(item) for item in probe_cases)
    probe_count = len(probe_cases)
    return {
        "probe_count": probe_count,
        "rag_behavior_equivalent_on_original_turns": True,
        "candidate_rag_probe_match_rate": matched / probe_count,
        "rag_remains_equivalent_under_causal_probes": matched / probe_count >= 0.95,
        "supporting_prior_deletion": {
            "candidate_before_action": support_before["selected_action"],
            "candidate_after_action": support_after["selected_action"],
            "candidate_action_changed": support_before["selected_action"] != support_after["selected_action"],
            "candidate_probability_drop": (
                support_before["action_distribution"][support_before["selected_action"]]
                - support_after["action_distribution"][support_before["selected_action"]]
            ),
            "rag_before_action": rag_support_before,
            "rag_after_action": rag_support_after,
            "rag_action_changed": rag_support_before != rag_support_after,
        },
        "rag_summary_sentence_deletion": {
            "deleted_sentence": "helpful support summary",
            "rag_before_action": rag_support_before,
            "rag_after_action": rag_support_after,
            "rag_action_changed": rag_support_before != rag_support_after,
        },
        "effect_perturbation": {
            "candidate_before_action": support_before["selected_action"],
            "candidate_after_action": perturbed_decision["selected_action"],
            "candidate_distribution_kl": distribution_kl(
                support_before["action_distribution"],
                perturbed_decision["action_distribution"],
            ),
            "candidate_distribution_changed": distribution_kl(
                support_before["action_distribution"],
                perturbed_decision["action_distribution"],
            ) > 0.05,
            "rag_action": rag_support_before,
            "rag_action_changed": False,
        },
        "same_prompt_different_causal_history": {
            "prompt": support_event,
            "candidate_base_action": support_before["selected_action"],
            "candidate_alternate_history_action": alternate_decision["selected_action"],
            "candidate_action_changed": support_before["selected_action"] != alternate_decision["selected_action"],
            "rag_base_action": rag_support_before,
            "rag_alternate_history_action": rag_support_before,
            "rag_action_changed": False,
        },
        "feedback_outcome_swap_same_text": {
            "prompt": focus_event,
            "candidate_good_feedback_action": good_decision["selected_action"],
            "candidate_bad_feedback_action": bad_decision["selected_action"],
            "candidate_distribution_kl": distribution_kl(
                good_decision["action_distribution"],
                bad_decision["action_distribution"],
            ),
            "candidate_action_changed_or_distribution_shift": (
                good_decision["selected_action"] != bad_decision["selected_action"]
                or distribution_kl(good_decision["action_distribution"], bad_decision["action_distribution"]) > 0.05
            ),
            "rag_action_same_text": rag_choose("feedback_focus_context", focus_event, ["bad_timing"]),
        },
        "feedback_admission_probe": {
            "single_feedback_status": single["admission_status"],
            "candidate_raw_action": single["raw_unfiltered_selected_action"],
            "candidate_filtered_action": single["admission_filtered_selected_action"],
            "rag_has_admission_state": False,
        },
    }


def decide_verdict(
    comparison: dict[str, Any],
    classifications: dict[str, Any],
    probes: dict[str, Any],
) -> tuple[str, list[str]]:
    secondary: list[str] = []
    if comparison["rag_match_rate"] == 1.0 and classifications["counts"]["surface_context_sufficient"] >= 20:
        secondary.append("blind_prompt_sheet_too_surface_level")
    if comparison["strong_heuristic_match_rate"] >= 0.90:
        secondary.append("strong_heuristic_near_equivalence_due_to_weak_prompt_distribution")
    if comparison["rag_match_rate"] == 1.0 and not probes["rag_remains_equivalent_under_causal_probes"]:
        return "rag_equivalent_on_behavior_but_not_causal_probes", secondary
    if comparison["rag_match_rate"] == 1.0 and probes["rag_remains_equivalent_under_causal_probes"]:
        return "rag_equivalent_even_under_causal_probes", secondary
    if comparison["rag_match_rate"] == 1.0:
        return "blind_prompt_sheet_too_surface_level", secondary
    return "inconclusive_need_stronger_blind_contract", secondary


def run_blind_human_trial_rca_001(out: str | Path) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    manifest = freeze_failure_manifest()
    comparison, rows = turn_match_comparison()
    classifications = classify_decisions(rows)
    probes = posthoc_causal_probes()
    verdict, secondary = decide_verdict(comparison, classifications, probes)
    result: dict[str, Any] = {
        "suite_id": "CMBC-COMPANION-BLIND-RCA-001",
        "claim_boundary": "RCA only; bounded offline human-trial generalization evidence retained",
        "source_failure": {
            "suite_id": manifest["suite_id"],
            "verdict": manifest["verdict"],
            "stop_condition": manifest["stop_condition"],
            "artifact_dir": manifest["source_artifact_dir"],
        },
        "frozen_failure_manifest": manifest,
        "turn_match_comparison": comparison,
        "turn_match_rows": rows,
        "decision_classification": classifications,
        "posthoc_causal_probes": probes,
        "verdict": verdict,
        "secondary_findings": secondary,
        "claim_after_rca": "bounded offline human-trial generalization evidence only",
        "selector_patched": False,
        "thresholds_changed": False,
        "rag_baseline_weakened": False,
        "baseline_weakened": False,
        "ego_migration": "no_go",
        "real_companion_implementation": "not_authorized",
        "proactive_messages": "not_authorized",
        "llm_action_selection": False,
        "not_authorized": [
            "EGO migration",
            "real companion implementation",
            "proactive messages",
            "LLM action selection",
            "selector patch",
            "RAG baseline weakening",
            "threshold change",
            "open-ended robustness claim",
        ],
    }
    write_artifacts(out_path, result)
    return result


def write_artifacts(out_path: Path, result: dict[str, Any]) -> None:
    write_json(out_path / "frozen_failure_manifest.json", result["frozen_failure_manifest"])
    write_json(out_path / "turn_match_comparison.json", {
        "summary": result["turn_match_comparison"],
        "rows": result["turn_match_rows"],
    })
    with (out_path / "turn_match_comparison.csv").open("w", encoding="utf-8", newline="") as fh:
        fieldnames = [
            "turn_id",
            "cmbc_selected_action",
            "rag_selected_action",
            "strong_heuristic_selected_action",
            "rag_matched",
            "strong_heuristic_matched",
            "supporting_prior_id",
            "feedback_label",
            "admission_status",
        ]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in result["turn_match_rows"]:
            writer.writerow({name: row[name] for name in fieldnames})
    write_json(out_path / "decision_classification_summary.json", result["decision_classification"])
    write_json(out_path / "causal_probe_report.json", result["posthoc_causal_probes"])
    write_json(out_path / "rag_equivalence_rca_result.json", {
        "verdict": result["verdict"],
        "secondary_findings": result["secondary_findings"],
        "claim_after_rca": result["claim_after_rca"],
        "source_failure": result["source_failure"],
        "rag_match_rate": result["turn_match_comparison"]["rag_match_rate"],
        "strong_heuristic_match_rate": result["turn_match_comparison"]["strong_heuristic_match_rate"],
        "candidate_rag_probe_match_rate": result["posthoc_causal_probes"]["candidate_rag_probe_match_rate"],
        "rag_remains_equivalent_under_causal_probes": result["posthoc_causal_probes"]["rag_remains_equivalent_under_causal_probes"],
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
    })
    (out_path / "decision_classification_summary.md").write_text(
        "# Decision Classification Summary\n\n"
        f"turn_count = {result['decision_classification']['classified_turn_count']}\n\n"
        f"counts = {json.dumps(result['decision_classification']['counts'], sort_keys=True)}\n",
        encoding="utf-8",
    )
    (out_path / "causal_probe_report.md").write_text(
        "# Causal Probe Report\n\n"
        f"rag_behavior_equivalent_on_original_turns = {result['posthoc_causal_probes']['rag_behavior_equivalent_on_original_turns']}\n\n"
        f"rag_remains_equivalent_under_causal_probes = {result['posthoc_causal_probes']['rag_remains_equivalent_under_causal_probes']}\n\n"
        f"candidate_rag_probe_match_rate = {result['posthoc_causal_probes']['candidate_rag_probe_match_rate']}\n",
        encoding="utf-8",
    )
    (out_path / "RCA_STATUS.md").write_text(
        "# CMBC Companion Blind RCA 001\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"claim_after_rca = {result['claim_after_rca']}\n\n"
        f"secondary_findings = {', '.join(result['secondary_findings'])}\n\n"
        "EGO migration = no_go\n\n"
        "real companion implementation = not_authorized\n\n"
        "RAG baseline weakening = false\n\n"
        "selector patch = false\n",
        encoding="utf-8",
    )


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run_blind_human_trial_rca_001(args.out)
    print(json.dumps({
        "verdict": result["verdict"],
        "claim_after_rca": result["claim_after_rca"],
        "rag_match_rate": result["turn_match_comparison"]["rag_match_rate"],
        "candidate_rag_probe_match_rate": result["posthoc_causal_probes"]["candidate_rag_probe_match_rate"],
        "secondary_findings": result["secondary_findings"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
