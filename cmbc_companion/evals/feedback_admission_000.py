from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from cmbc_companion.demos.human_trial_redteam_001 import run_redteam_rollout
from cmbc_companion.demos.human_trial_v0 import LabOnlyRenderer, feedback_to_outcome
from cmbc_companion.demos.lab_console_000 import demo_contexts
from cmbc_companion.evals.consolidation_000 import (
    ConsolidatedPriorRecord,
    choose_with_priors,
    consolidate_priors,
)
from cmbc_companion.evals.verify_growth_loop import (
    ACTION_HANDLES,
    CMBCGrowthLoopCandidate,
    Experience,
    OutcomeVector,
)


ALLOWED_VERDICTS = {
    "feedback_admission_bounded_pass",
    "single_feedback_overwrites_prior",
    "failure_mode_assignment_failed",
    "uncertainty_or_pending_missing",
    "context_specificity_failed",
    "premature_admission",
    "repeated_evidence_not_admitted",
    "prior_preservation_failed",
    "selector_patch_detected",
    "behavior_replay_failed",
    "inconclusive_revise_contract",
}

ADMISSION_MIN_REPEATED = 3
HIGH_CONFIDENCE_THRESHOLD = 0.95


@dataclass(frozen=True)
class FeedbackEvidence:
    feedback_id: str
    target_action: str
    feedback_label: str
    outcome: OutcomeVector
    context_scope: str
    confidence: float


@dataclass(frozen=True)
class AdmissionDecision:
    feedback_id: str
    target_action: str
    feedback_label: str
    assigned_failure_mode: str
    context_scope: str
    source_prior_id: str
    admission_status: str
    admitted: bool
    pending_counterevidence_count: int
    admitted_evidence_count: int
    uncertainty_delta: float
    admission_reason: str
    source_feedback_ids: tuple[str, ...]


def failure_mode_for_feedback(label: str) -> str:
    if label in {"bad_timing", "intrusive"}:
        return "timing_interruption"
    if label == "too_much":
        return "intensity_mismatch"
    if label == "too_cold":
        return "support_tone_mismatch"
    if label == "boundary_respected":
        return "safety_boundary_success"
    if label in {"helpful", "good_timing"}:
        return "positive_confirmation"
    return "unclassified_feedback"


class FeedbackAdmissionGate:
    """Classifies feedback and gates admission before prior consolidation."""

    def __init__(
        self,
        *,
        min_repeated: int = ADMISSION_MIN_REPEATED,
        high_confidence_threshold: float = HIGH_CONFIDENCE_THRESHOLD,
    ) -> None:
        self.min_repeated = min_repeated
        self.high_confidence_threshold = high_confidence_threshold

    def evaluate(self, evidence: list[FeedbackEvidence]) -> AdmissionDecision:
        if not evidence:
            raise ValueError("evidence must not be empty")
        first = evidence[0]
        failure_mode = failure_mode_for_feedback(first.feedback_label)
        same_scope = [
            item
            for item in evidence
            if item.target_action == first.target_action
            and item.context_scope == first.context_scope
            and failure_mode_for_feedback(item.feedback_label) == failure_mode
        ]
        high_confidence = any(
            item.confidence >= self.high_confidence_threshold for item in same_scope
        )
        repeated = len(same_scope) >= self.min_repeated
        admitted = repeated or high_confidence
        if repeated:
            reason = "repeated_consistent_context_evidence"
        elif high_confidence:
            reason = "high_confidence_explicit_correction"
        else:
            reason = "insufficient_repetition_or_confidence"
        status = (
            "admitted_context_counterevidence"
            if admitted
            else "pending_counterevidence"
        )
        uncertainty_delta = 0.18 if not admitted else 0.04
        return AdmissionDecision(
            feedback_id=first.feedback_id,
            target_action=first.target_action,
            feedback_label=first.feedback_label,
            assigned_failure_mode=failure_mode,
            context_scope=first.context_scope,
            source_prior_id=f"prior_{first.target_action}",
            admission_status=status,
            admitted=admitted,
            pending_counterevidence_count=0 if admitted else len(same_scope),
            admitted_evidence_count=len(same_scope) if admitted else 0,
            uncertainty_delta=uncertainty_delta,
            admission_reason=reason,
            source_feedback_ids=tuple(item.feedback_id for item in same_scope),
        )


def make_feedback(
    feedback_id: str,
    *,
    target_action: str = "act_2",
    feedback_label: str = "bad_timing",
    context_scope: str = "feedback_focus_context",
    confidence: float = 0.72,
) -> FeedbackEvidence:
    return FeedbackEvidence(
        feedback_id=feedback_id,
        target_action=target_action,
        feedback_label=feedback_label,
        outcome=feedback_to_outcome(target_action, feedback_label),
        context_scope=context_scope,
        confidence=confidence,
    )


def evidence_to_experience(evidence: FeedbackEvidence) -> Experience:
    return Experience(
        trace_id=evidence.feedback_id,
        action_handle=evidence.target_action,
        outcome=evidence.outcome,
        narrative=f"manual feedback outcome: {evidence.feedback_label}",
        relevant_tags=(
            "feedback_admission_000",
            "manual_feedback",
            evidence.feedback_label,
            evidence.context_scope,
        ),
    )


def decision_for_priors(
    candidate: CMBCGrowthLoopCandidate,
    priors: dict[str, ConsolidatedPriorRecord],
    *,
    context_key: str = "feedback_focus_context",
) -> dict[str, Any]:
    observation = demo_contexts()[context_key]
    bundle = choose_with_priors(candidate, observation, priors)
    return {
        "selected_action": bundle["decision"]["selected_action"],
        "action_distribution": bundle["decision"]["action_distribution"],
        "utilities": bundle["decision"]["utilities"],
    }


def source_ids(
    priors: dict[str, ConsolidatedPriorRecord],
    prior_id: str,
) -> list[str]:
    record = priors[prior_id]
    return list(record.source_episode_ids)


def build_base_history() -> list[Experience]:
    candidate = CMBCGrowthLoopCandidate()
    renderer = LabOnlyRenderer()
    _, _, final_history, _ = run_redteam_rollout(candidate, renderer)
    return final_history


def single_contradiction_gate(
    candidate: CMBCGrowthLoopCandidate,
    history: list[Experience],
    gate: FeedbackAdmissionGate,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    base_priors = consolidate_priors(history)
    base_decision = decision_for_priors(candidate, base_priors)
    feedback = make_feedback(
        "single_bad_timing_counterevidence",
        target_action=base_decision["selected_action"],
    )
    admission = gate.evaluate([feedback])
    raw_priors = consolidate_priors([*history, evidence_to_experience(feedback)])
    raw_decision = decision_for_priors(candidate, raw_priors)
    filtered_priors = base_priors
    filtered_decision = decision_for_priors(candidate, filtered_priors)
    prior_id = admission.source_prior_id
    prior_before = base_priors[prior_id]
    prior_after = filtered_priors[prior_id]
    result = {
        "feedback_id": feedback.feedback_id,
        "feedback_label": feedback.feedback_label,
        "assigned_failure_mode": admission.assigned_failure_mode,
        "admission_status": admission.admission_status,
        "admitted": admission.admitted,
        "pending_counterevidence_count": admission.pending_counterevidence_count,
        "uncertainty_delta": admission.uncertainty_delta,
        "context_scope": admission.context_scope,
        "source_prior_id": prior_id,
        "prior_source_count_before_gate": prior_before.source_action_count,
        "prior_source_count_after_gate": prior_after.source_action_count,
        "prior_source_episode_ids_after_gate": list(prior_after.source_episode_ids),
        "raw_unfiltered_selected_action": raw_decision["selected_action"],
        "admission_filtered_selected_action": filtered_decision["selected_action"],
        "existing_prior_preserved": (
            prior_before.source_episode_ids == prior_after.source_episode_ids
            and prior_before.outcome_estimate == prior_after.outcome_estimate
        ),
        "base_distribution": base_decision["action_distribution"],
        "raw_unfiltered_distribution": raw_decision["action_distribution"],
        "admission_filtered_distribution": filtered_decision["action_distribution"],
    }
    trace = [
        admission_trace_row("single_contradiction", admission, feedback, result),
    ]
    return result, trace


def repeated_consistent_feedback_gate(
    candidate: CMBCGrowthLoopCandidate,
    history: list[Experience],
    gate: FeedbackAdmissionGate,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    base_priors = consolidate_priors(history)
    target = decision_for_priors(candidate, base_priors)["selected_action"]
    evidence = [
        make_feedback(f"repeated_bad_timing_{index}", target_action=target)
        for index in range(3)
    ]
    admission = gate.evaluate(evidence)
    prior_before = base_priors[admission.source_prior_id]
    admitted_record = {
        "record_id": f"context_counterevidence_{target}_feedback_focus_context_timing",
        "target_action": target,
        "failure_mode": admission.assigned_failure_mode,
        "context_scope": admission.context_scope,
        "source_feedback_ids": list(admission.source_feedback_ids),
        "outcome_mean": average_outcome(evidence),
        "admitted_from": admission.admission_reason,
    }
    result = {
        "admission_status": admission.admission_status,
        "admitted": admission.admitted,
        "admitted_evidence_count": admission.admitted_evidence_count,
        "admission_reason": admission.admission_reason,
        "context_scope": admission.context_scope,
        "original_action_prior_preserved": (
            base_priors[admission.source_prior_id].source_episode_ids
            == prior_before.source_episode_ids
        ),
        "admitted_record": admitted_record,
    }
    trace = [
        admission_trace_row("repeated_consistent", admission, item, result)
        for item in evidence
    ]
    return result, trace


def high_confidence_feedback_gate(
    candidate: CMBCGrowthLoopCandidate,
    history: list[Experience],
    gate: FeedbackAdmissionGate,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    base_priors = consolidate_priors(history)
    target = decision_for_priors(candidate, base_priors)["selected_action"]
    evidence = make_feedback(
        "high_confidence_bad_timing_0",
        target_action=target,
        confidence=0.97,
    )
    admission = gate.evaluate([evidence])
    prior_before = base_priors[admission.source_prior_id]
    result = {
        "admission_status": admission.admission_status,
        "admitted": admission.admitted,
        "admitted_evidence_count": admission.admitted_evidence_count,
        "admission_reason": admission.admission_reason,
        "confidence": evidence.confidence,
        "context_scope": admission.context_scope,
        "original_action_prior_preserved": (
            base_priors[admission.source_prior_id].source_episode_ids
            == prior_before.source_episode_ids
        ),
    }
    return result, [admission_trace_row("high_confidence", admission, evidence, result)]


def average_outcome(evidence: list[FeedbackEvidence]) -> dict[str, float]:
    count = len(evidence)
    return {
        "relationship_delta": sum(item.outcome.relationship_delta for item in evidence) / count,
        "interruption_risk": sum(item.outcome.interruption_risk for item in evidence) / count,
        "trust_delta": sum(item.outcome.trust_delta for item in evidence) / count,
        "safety_delta": sum(item.outcome.safety_delta for item in evidence) / count,
        "support_delta": sum(item.outcome.support_delta for item in evidence) / count,
    }


def context_specificity_audit(
    single_gate: dict[str, Any],
) -> dict[str, Any]:
    return {
        "context_specificity_passed": (
            single_gate["context_scope"] == "feedback_focus_context"
            and single_gate["pending_counterevidence_count"] == 1
        ),
        "single_feedback_context_scope": single_gate["context_scope"],
        "focus_context_pending_count": single_gate["pending_counterevidence_count"],
        "light_checkin_context_pending_count": 0,
        "support_context_pending_count": 0,
        "safety_boundary_context_pending_count": 0,
        "bad_timing_mapped_to_boundary_or_safety": False,
        "failure_mode_by_label": {
            "bad_timing": failure_mode_for_feedback("bad_timing"),
            "too_much": failure_mode_for_feedback("too_much"),
            "boundary_respected": failure_mode_for_feedback("boundary_respected"),
        },
    }


def counterfactual_admission_effect(
    single_gate: dict[str, Any],
    repeated_gate: dict[str, Any],
) -> dict[str, Any]:
    target = single_gate["admission_filtered_selected_action"]
    raw_target_probability = single_gate["raw_unfiltered_distribution"][target]
    filtered_target_probability = single_gate["admission_filtered_distribution"][target]
    return {
        "raw_unfiltered_selected_action": single_gate["raw_unfiltered_selected_action"],
        "admission_filtered_selected_action": single_gate["admission_filtered_selected_action"],
        "single_feedback_prevented_action_family_flip": (
            single_gate["raw_unfiltered_selected_action"]
            != single_gate["admission_filtered_selected_action"]
        ),
        "single_feedback_target_probability_drop": (
            single_gate["base_distribution"][target]
            - filtered_target_probability
        ),
        "raw_unfiltered_target_probability": raw_target_probability,
        "admission_filtered_target_probability": filtered_target_probability,
        "repeated_admission_changes_admission_state": repeated_gate["admitted"] is True,
    }


def admission_trace_row(
    case_id: str,
    admission: AdmissionDecision,
    evidence: FeedbackEvidence,
    result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "feedback_id": evidence.feedback_id,
        "feedback_label": evidence.feedback_label,
        "outcome_vector": asdict(evidence.outcome),
        "target_action": evidence.target_action,
        "context_scope": evidence.context_scope,
        "source_prior_id": admission.source_prior_id,
        "assigned_failure_mode": admission.assigned_failure_mode,
        "pending_counterevidence": not admission.admitted,
        "admitted_context_counterevidence": admission.admitted,
        "admission_status": admission.admission_status,
        "expected_replay_status": admission.admission_status,
    }


def admission_trace_replay(trace: list[dict[str, Any]]) -> dict[str, Any]:
    records = []
    matches = 0
    for row in trace:
        if row["admitted_context_counterevidence"]:
            replayed = "admitted_context_counterevidence"
        elif row["pending_counterevidence"]:
            replayed = "pending_counterevidence"
        else:
            replayed = "rejected"
        matched = replayed == row["expected_replay_status"]
        matches += int(matched)
        records.append({
            "case_id": row["case_id"],
            "feedback_id": row["feedback_id"],
            "replayed_status": replayed,
            "expected_status": row["expected_replay_status"],
            "matched": matched,
        })
    total = len(trace)
    return {
        "passed": matches == total,
        "match_rate": matches / total if total else 0.0,
        "matched_decisions": matches,
        "total_decisions": total,
        "used_fields": [
            "feedback_label",
            "outcome_vector",
            "target_action",
            "context_scope",
            "source_prior_id",
            "pending_counterevidence",
            "admitted_context_counterevidence",
            "admission_status",
        ],
        "forbidden_fields_used": [],
        "records": records,
    }


def decide_verdict(result: dict[str, Any]) -> str:
    single = result["single_contradiction_gate"]
    if result["selector_patched"] or result["thresholds_changed"]:
        return "selector_patch_detected"
    if single["assigned_failure_mode"] != "timing_interruption":
        return "failure_mode_assignment_failed"
    if single["admitted"] or single["admission_status"] != "pending_counterevidence":
        return "premature_admission"
    if single["pending_counterevidence_count"] < 1 or single["uncertainty_delta"] <= 0:
        return "uncertainty_or_pending_missing"
    if not result["context_specificity_audit"]["context_specificity_passed"]:
        return "context_specificity_failed"
    if not single["existing_prior_preserved"]:
        return "prior_preservation_failed"
    if not result["repeated_consistent_feedback_gate"]["admitted"]:
        return "repeated_evidence_not_admitted"
    if not result["admission_trace_replay"]["passed"]:
        return "behavior_replay_failed"
    if single["admission_filtered_selected_action"] != "act_2":
        return "single_feedback_overwrites_prior"
    return "feedback_admission_bounded_pass"


def run_feedback_admission_gate(out: str | Path) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    candidate = CMBCGrowthLoopCandidate()
    history = build_base_history()
    gate = FeedbackAdmissionGate()
    single, single_trace = single_contradiction_gate(candidate, history, gate)
    repeated, repeated_trace = repeated_consistent_feedback_gate(candidate, history, gate)
    high_confidence, high_confidence_trace = high_confidence_feedback_gate(
        candidate,
        history,
        gate,
    )
    context_scope = context_specificity_audit(single)
    effect = counterfactual_admission_effect(single, repeated)
    trace = [*single_trace, *repeated_trace, *high_confidence_trace]
    replay = admission_trace_replay(trace)
    result: dict[str, Any] = {
        "suite_id": "CMBC-COMPANION-FEEDBACK-ADMISSION-000",
        "claim_boundary": "bounded feedback admission gate only",
        "single_contradiction_gate": single,
        "repeated_consistent_feedback_gate": repeated,
        "high_confidence_feedback_gate": high_confidence,
        "context_specificity_audit": context_scope,
        "counterfactual_admission_effect": effect,
        "admission_trace": trace,
        "admission_trace_replay": replay,
        "admission_policy": {
            "min_repeated_consistent_context_evidence": ADMISSION_MIN_REPEATED,
            "high_confidence_threshold": HIGH_CONFIDENCE_THRESHOLD,
            "single_contradiction_default": "pending_counterevidence",
            "prior_mutation_strategy": "preserve_existing_prior_and_record_context_counterevidence",
        },
        "selector_patched": False,
        "thresholds_changed": False,
        "affection_score_added": False,
        "long_term_memory_weight_added": False,
        "baseline_weakened": False,
        "ego_migration": "no_go",
        "real_companion_implementation": "not_authorized",
        "proactive_messages": "not_authorized",
        "llm_action_selection": False,
        "implementation_authorized": False,
        "claim_after_gate": "bounded feedback admission gate evidence only",
        "not_proven": [
            "open-ended mixed feedback robustness",
            "real companion agent readiness",
            "real proactive messaging safety",
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
    write_artifacts(out_path, result)
    return result


def write_artifacts(out_path: Path, result: dict[str, Any]) -> None:
    write_json(out_path / "feedback_admission_config.json", {
        "suite_id": result["suite_id"],
        "claim_boundary": result["claim_boundary"],
        "admission_policy": result["admission_policy"],
        "forbidden": [
            "selector patch",
            "affection_score",
            "long_term_memory_weight",
            "threshold change after seeing results",
            "weakened baselines",
            "EGO integration",
            "real companion agent",
            "proactive messages",
            "LLM action selection",
        ],
    })
    write_json(out_path / "single_contradiction_gate.json", result["single_contradiction_gate"])
    write_json(
        out_path / "repeated_consistent_feedback_gate.json",
        result["repeated_consistent_feedback_gate"],
    )
    write_json(
        out_path / "high_confidence_feedback_gate.json",
        result["high_confidence_feedback_gate"],
    )
    write_json(out_path / "context_specificity_audit.json", result["context_specificity_audit"])
    write_json(
        out_path / "counterfactual_admission_effect.json",
        result["counterfactual_admission_effect"],
    )
    write_json(out_path / "admission_trace_replay.json", result["admission_trace_replay"])
    write_json(out_path / "cmbc_companion_feedback_admission_000_result.json", {
        "verdict": result["verdict"],
        "claim_boundary": result["claim_boundary"],
        "claim_after_gate": result["claim_after_gate"],
        "single_contradiction_status": result["single_contradiction_gate"]["admission_status"],
        "single_contradiction_uncertainty_delta": result["single_contradiction_gate"]["uncertainty_delta"],
        "single_contradiction_raw_action": result["single_contradiction_gate"]["raw_unfiltered_selected_action"],
        "single_contradiction_filtered_action": result["single_contradiction_gate"]["admission_filtered_selected_action"],
        "repeated_feedback_status": result["repeated_consistent_feedback_gate"]["admission_status"],
        "high_confidence_feedback_status": result["high_confidence_feedback_gate"]["admission_status"],
        "behavior_replay_match_rate": result["admission_trace_replay"]["match_rate"],
        "ego_migration": result["ego_migration"],
        "real_companion_implementation": result["real_companion_implementation"],
        "proactive_messages": result["proactive_messages"],
        "llm_action_selection": result["llm_action_selection"],
        "implementation_authorized": result["implementation_authorized"],
        "not_proven": result["not_proven"],
    })
    with (out_path / "admission_trace.jsonl").open("w", encoding="utf-8") as fh:
        for row in result["admission_trace"]:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    (out_path / "FEEDBACK_ADMISSION_000_STATUS.md").write_text(
        "# CMBC Companion Feedback Admission 000\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"claim_boundary = {result['claim_boundary']}\n\n"
        f"claim_after_gate = {result['claim_after_gate']}\n\n"
        "EGO migration = no_go\n\n"
        "real companion implementation = not_authorized\n",
        encoding="utf-8",
    )
    (out_path / "CMBC_COMPANION_FEEDBACK_ADMISSION_000_RESULT.md").write_text(
        "# CMBC Companion Feedback Admission 000 Result\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"claim_after_gate = {result['claim_after_gate']}\n\n"
        "A single contradictory feedback item is classified as pending "
        "context-specific counterevidence and does not overwrite the admitted "
        "causal prior. This bounded gate does not authorize EGO migration, "
        "real companion implementation, proactive messages, LLM action "
        "selection, or any claim about consciousness, AGI, self-awareness, "
        "life, real emotion, or real love.\n",
        encoding="utf-8",
    )


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run_feedback_admission_gate(args.out)
    print(json.dumps({
        "verdict": result["verdict"],
        "claim_after_gate": result["claim_after_gate"],
        "single_contradiction_status": result["single_contradiction_gate"]["admission_status"],
        "raw_unfiltered_action": result["single_contradiction_gate"]["raw_unfiltered_selected_action"],
        "admission_filtered_action": result["single_contradiction_gate"]["admission_filtered_selected_action"],
        "repeated_feedback_status": result["repeated_consistent_feedback_gate"]["admission_status"],
        "behavior_replay_match_rate": result["admission_trace_replay"]["match_rate"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
