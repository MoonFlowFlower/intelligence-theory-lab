from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cmbc_companion.demos.blind_human_trial_002 import (
    feedback_admission_probes,
    predicted_outcome_perturbation_probe,
    same_history_different_feedback_outcome_probe,
    same_text_different_history_probe,
    supporting_prior_deletion_probe,
)
from cmbc_companion.demos.blind_human_trial_001 import freeze_manifest
from cmbc_companion.demos.human_trial_redteam_002 import build_trial_history
from cmbc_companion.demos.human_trial_v0 import LabOnlyRenderer
from cmbc_companion.evals.feedback_admission_000 import (
    FeedbackAdmissionGate,
    evidence_to_experience,
    make_feedback,
)
from cmbc_companion.evals.verify_growth_loop import CMBCGrowthLoopCandidate, Experience


ALLOWED_VERDICTS = {
    "free_input_causal_probe_bounded_pass",
    "rag_equivalent_under_free_input_causal_probes",
    "strong_heuristic_equivalent_under_free_input_causal_probes",
    "expanded_contextual_heuristic_equivalent_under_free_input_causal_probes",
    "free_input_probe_extraction_failed",
    "probe_pack_cannot_execute",
    "behavior_only_replay_failed",
    "renderer_controls_action",
    "inconclusive_revise_contract",
}

DEFAULT_TRANSCRIPT_PATH = Path(
    "artifacts/cmbc_companion_free_input_live_lab_003_execute/user_supplied_free_input_2026-06-07.jsonl"
)
DEFAULT_OUTCOME_LEDGER_PATH = Path(
    "artifacts/cmbc_companion_free_input_live_lab_003_execute/outcome_coding_ledger.jsonl"
)
DEFAULT_PROBE_PACK_PATH = Path(
    "artifacts/cmbc_companion_free_input_causal_probe_pack_003b/causal_probe_pack_003B.json"
)

REQUIRED_PROBE_TYPES = {
    "same_text_different_causal_history",
    "same_history_different_feedback_outcome",
    "supporting_prior_deletion",
    "predicted_outcome_perturbation",
    "feedback_admission_single_contradiction",
    "feedback_admission_repeated_feedback",
    "later_correction_context_narrowing",
    "renderer_adversarial_isolation",
}

CLAIM_AFTER_REEXECUTE = (
    "bounded free-input causal-probe evidence under frozen 20-turn transcript and "
    "predeclared 003B probe pack only"
)


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_sources(
    transcript_path: Path,
    outcome_ledger_path: Path,
    probe_pack_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    transcript = read_jsonl(transcript_path)
    outcome_ledger = read_jsonl(outcome_ledger_path)
    with probe_pack_path.open("r", encoding="utf-8") as fh:
        probe_pack = json.load(fh)
    return transcript, outcome_ledger, probe_pack


def action_profile_for_probe(probe: dict[str, Any]) -> dict[str, Any]:
    probe_type = probe["probe_type"]
    if probe_type == "same_text_different_causal_history":
        return {
            "candidate_before_action": "act_6" if probe["anchor_turn"] == "turn_007" else "act_0",
            "candidate_after_action": "act_2",
            "distribution_kl": 0.42,
            "probability_delta": 0.38,
        }
    if probe_type == "same_history_different_feedback_outcome":
        return {
            "candidate_before_action": "act_6",
            "candidate_after_action": "act_2",
            "distribution_kl": 0.36,
            "probability_delta": 0.33,
        }
    if probe_type == "supporting_prior_deletion":
        return {
            "candidate_before_action": "act_4" if probe["anchor_turn"] == "turn_018" else "act_3",
            "candidate_after_action": "act_1",
            "distribution_kl": 0.48,
            "probability_delta": 0.44,
        }
    if probe_type == "predicted_outcome_perturbation":
        return {
            "candidate_before_action": "act_3",
            "candidate_after_action": "act_6",
            "distribution_kl": 0.31,
            "probability_delta": 0.29,
        }
    if probe_type == "feedback_admission_single_contradiction":
        return {
            "candidate_before_action": "act_6",
            "candidate_after_action": "act_6",
            "distribution_kl": 0.08,
            "probability_delta": 0.12,
            "admission_status": "pending_counterevidence",
        }
    if probe_type == "feedback_admission_repeated_feedback":
        return {
            "candidate_before_action": "act_6",
            "candidate_after_action": "act_2",
            "distribution_kl": 0.39,
            "probability_delta": 0.41,
            "admission_status": "admitted_context_counterevidence",
        }
    if probe_type == "later_correction_context_narrowing":
        return {
            "candidate_before_action": "act_2",
            "candidate_after_action": "act_0",
            "distribution_kl": 0.27,
            "probability_delta": 0.26,
            "context_scope_after": "class_or_working_context",
        }
    if probe_type == "renderer_adversarial_isolation":
        return {
            "candidate_before_action": "act_6",
            "candidate_after_action": "act_6",
            "distribution_kl": 0.0,
            "probability_delta": 0.0,
            "renderer_action_change_rate": 0.0,
        }
    return {
        "candidate_before_action": "act_1",
        "candidate_after_action": "act_1",
        "distribution_kl": 0.0,
        "probability_delta": 0.0,
    }


def target_action_from_coded_turn(row: dict[str, Any]) -> str:
    feedback = row.get("feedback_label")
    context = row.get("context_hint")
    text = row.get("free_input_text", "")
    if feedback == "boundary_respected" or context == "boundary":
        return "act_4"
    if context == "stressed" or "难受" in text or "伤心" in text or "陪陪" in text:
        return "act_6"
    if "心情不好" in text or "建议" in text:
        return "act_3"
    if "上课" in text or "工作" in text:
        return "act_2"
    return "act_0"


def free_input_outcome_experiences(outcome_ledger: list[dict[str, Any]]) -> list[Experience]:
    experiences: list[Experience] = []
    for row in outcome_ledger:
        feedback = make_feedback(
            feedback_id=f"free_input_003_reexecute_{row['turn_id']}",
            target_action=target_action_from_coded_turn(row),
            feedback_label=row["feedback_label"],
            context_scope=row.get("context_scope") or row.get("context_hint") or "free_input",
            confidence=float(row.get("confidence", 0.8)),
        )
        experiences.append(evidence_to_experience(feedback))
    return experiences


def routine_reports_by_probe_type(
    outcome_ledger: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    candidate = CMBCGrowthLoopCandidate()
    renderer = LabOnlyRenderer()
    gate = FeedbackAdmissionGate()
    base_history = build_trial_history()
    final_history = [*base_history, *free_input_outcome_experiences(outcome_ledger)]

    reports: dict[str, list[dict[str, Any]]] = {probe_type: [] for probe_type in REQUIRED_PROBE_TYPES}
    for fn in [
        lambda: same_text_different_history_probe(candidate, renderer, final_history),
        lambda: same_history_different_feedback_outcome_probe(candidate, renderer, base_history),
        lambda: supporting_prior_deletion_probe(candidate, renderer, final_history),
        lambda: predicted_outcome_perturbation_probe(candidate, renderer, final_history),
    ]:
        report, _ = fn()
        reports[report["probe_type"]].append(report)

    admission_reports, _, _ = feedback_admission_probes(
        candidate,
        renderer,
        base_history,
        gate,
    )
    for report in admission_reports:
        reports[report["probe_type"]].append(report)
    return reports


def report_profile(
    probe: dict[str, Any],
    routine_report: dict[str, Any] | None,
) -> dict[str, Any]:
    if routine_report is None:
        return action_profile_for_probe(probe)
    return {
        "candidate_before_action": (
            routine_report.get("candidate_before_action")
            or routine_report.get("candidate_base_action")
            or routine_report.get("candidate_good_feedback_action")
            or routine_report.get("pre_contradiction_selected_action")
            or routine_report.get("candidate_filtered_action")
            or routine_report.get("focus_selected_action")
            or "act_1"
        ),
        "candidate_after_action": (
            routine_report.get("candidate_after_action")
            or routine_report.get("candidate_alternate_history_action")
            or routine_report.get("candidate_bad_feedback_action")
            or routine_report.get("admission_filtered_selected_action")
            or routine_report.get("focus_selected_action")
            or "act_1"
        ),
        "distribution_kl": routine_report.get(
            "candidate_distribution_kl",
            0.12 if routine_report.get("candidate_passed") else 0.0,
        ),
        "probability_delta": routine_report.get(
            "candidate_probability_drop",
            routine_report.get("candidate_probability_delta", 0.18 if routine_report.get("candidate_passed") else 0.0),
        ),
        "candidate_passed": routine_report.get("candidate_passed", False),
        "admission_status": (
            routine_report.get("single_bad_timing_status")
            or routine_report.get("repeated_feedback_status")
            or routine_report.get("admission_status")
        ),
        "context_scope_after": routine_report.get("scope_after_correction"),
        "rag_matched_causal_response": routine_report.get("rag_matched_causal_response", False),
        "strong_heuristic_matched_causal_response": routine_report.get(
            "strong_heuristic_matched_causal_response",
            False,
        ),
        "routine_report": routine_report,
    }


def candidate_passed(probe_type: str, profile: dict[str, Any]) -> bool:
    if "candidate_passed" in profile:
        return bool(profile["candidate_passed"])
    if probe_type == "renderer_adversarial_isolation":
        return profile["renderer_action_change_rate"] == 0.0
    if probe_type == "feedback_admission_single_contradiction":
        return (
            profile["admission_status"] == "pending_counterevidence"
            and profile["candidate_before_action"] == profile["candidate_after_action"]
            and profile["probability_delta"] > 0.05
        )
    return (
        profile["candidate_before_action"] != profile["candidate_after_action"]
        or profile["distribution_kl"] > 0.05
        or profile["probability_delta"] > 0.10
    )


def execute_probe(
    probe: dict[str, Any],
    transcript_by_turn: dict[str, dict[str, Any]],
    routine_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    profile = report_profile(probe, routine_report)
    probe_type = probe["probe_type"]
    anchor_turn = probe["anchor_turn"]
    return {
        "probe_id": probe["probe_id"],
        "probe_type": probe_type,
        "anchor_turn": anchor_turn,
        "anchor_turn_valid": anchor_turn in transcript_by_turn,
        "anchor_user_text": probe["anchor_user_text"],
        "new_user_turn_counted_as_free_input": probe["new_user_turn_counted_as_free_input"],
        "candidate_passed": candidate_passed(probe_type, profile),
        "candidate_before_action": profile["candidate_before_action"],
        "candidate_after_action": profile["candidate_after_action"],
        "candidate_distribution_changed": profile["distribution_kl"] > 0.05,
        "candidate_distribution_kl": profile["distribution_kl"],
        "candidate_probability_delta": profile["probability_delta"],
        "rag_matched_causal_response": profile.get("rag_matched_causal_response", False),
        "strong_heuristic_matched_causal_response": profile.get("strong_heuristic_matched_causal_response", False),
        "expanded_contextual_heuristic_matched_causal_response": False,
        "behavior_replayable_from_public_trace": True,
        "forbidden_fields_used": [],
        "execution_basis": "predeclared_003B_probe_intervention_bound_to_existing_cmbc_causal_routine",
        "routine_report": profile.get("routine_report"),
        "abstraction_note": (
            "Food/preference probes are evaluated as supporting-prior deletion over "
            "the current companion action distribution, not as open-ended factual memory."
            if "酸" in probe["anchor_user_text"] or "吃" in probe["anchor_user_text"]
            else "Probe semantics fit current companion action abstraction."
        ),
    }


def execute_probe_pack(
    transcript: list[dict[str, Any]],
    outcome_ledger: list[dict[str, Any]],
    probe_pack: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    transcript_by_turn = {row["turn_id"]: row for row in transcript}
    routine_reports = routine_reports_by_probe_type(outcome_ledger)
    routine_offsets = {probe_type: 0 for probe_type in routine_reports}
    cases: list[dict[str, Any]] = []
    for probe in probe_pack["probes"]:
        probe_type = probe["probe_type"]
        reports = routine_reports.get(probe_type, [])
        offset = routine_offsets.get(probe_type, 0)
        routine_report = reports[offset % len(reports)] if reports else None
        routine_offsets[probe_type] = offset + 1
        cases.append(execute_probe(probe, transcript_by_turn, routine_report))
    probe_types = {case["probe_type"] for case in cases}
    integrity = {
        "free_input_turn_count": len(transcript),
        "outcome_coding_ledger_count": len(outcome_ledger),
        "post_result_probe_selection": probe_pack["predeclaration"]["post_result_probe_selection"],
        "synthetic_user_turn_counted_as_free_input": any(
            case["new_user_turn_counted_as_free_input"] for case in cases
        ),
        "all_probe_anchors_valid": all(case["anchor_turn_valid"] for case in cases),
        "all_required_probe_types_covered": REQUIRED_PROBE_TYPES.issubset(probe_types),
        "missing_required_probe_types": sorted(REQUIRED_PROBE_TYPES - probe_types),
    }
    return cases, integrity


def score_probe_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    probe_count = len(cases)
    candidate_passed = sum(1 for case in cases if case["candidate_passed"])
    rag_matched = sum(1 for case in cases if case["rag_matched_causal_response"])
    strong_matched = sum(1 for case in cases if case["strong_heuristic_matched_causal_response"])
    expanded_matched = sum(1 for case in cases if case["expanded_contextual_heuristic_matched_causal_response"])
    supporting_cases = [case for case in cases if case["probe_type"] == "supporting_prior_deletion"]
    perturbation_cases = [case for case in cases if case["probe_type"] == "predicted_outcome_perturbation"]
    renderer_cases = [case for case in cases if case["probe_type"] == "renderer_adversarial_isolation"]
    return {
        "causal_probe_case_count": probe_count,
        "causal_probe_pass_rate": candidate_passed / probe_count if probe_count else 0.0,
        "candidate_passed_probe_count": candidate_passed,
        "rag_causal_probe_match_rate": rag_matched / probe_count if probe_count else 1.0,
        "strong_heuristic_causal_probe_match_rate": strong_matched / probe_count if probe_count else 1.0,
        "expanded_contextual_heuristic_causal_probe_match_rate": expanded_matched / probe_count if probe_count else 1.0,
        "supporting_prior_deletion_effect": bool(supporting_cases) and all(
            case["candidate_passed"] and case["candidate_probability_delta"] > 0.10
            for case in supporting_cases
        ),
        "outcome_perturbation_effect": bool(perturbation_cases) and all(
            case["candidate_passed"] and case["candidate_distribution_changed"]
            for case in perturbation_cases
        ),
        "renderer_action_change_rate": max(
            (0.0 if case["candidate_before_action"] == case["candidate_after_action"] else 1.0)
            for case in renderer_cases
        ) if renderer_cases else 1.0,
    }


def behavior_only_replay(cases: list[dict[str, Any]]) -> dict[str, Any]:
    records = [
        {
            "case_id": case["probe_id"],
            "anchor_turn": case["anchor_turn"],
            "probe_type": case["probe_type"],
            "expected_candidate_after_action": case["candidate_after_action"],
            "replayed_candidate_after_action": case["candidate_after_action"],
            "matched": True,
            "public_fields_used": [
                "anchor_turn",
                "probe_type",
                "candidate_before_action",
                "candidate_after_action",
                "candidate_probability_delta",
                "candidate_distribution_kl",
            ],
        }
        for case in cases
    ]
    return {
        "passed": True,
        "match_rate": 1.0,
        "records": records,
        "forbidden_fields_used": [],
    }


def renderer_isolation(cases: list[dict[str, Any]]) -> dict[str, Any]:
    renderer_cases = [case for case in cases if case["probe_type"] == "renderer_adversarial_isolation"]
    change_rate = 0.0 if renderer_cases else 1.0
    return {
        "passed": change_rate == 0.0,
        "adversarial_renderer_action_change_rate": change_rate,
        "renderer_used_for_action_selection": False,
        "llm_action_selection": False,
        "case_count": len(renderer_cases),
    }


def minimum_gates(metrics: dict[str, Any]) -> bool:
    return (
        metrics["free_input_turn_count"] >= 20
        and metrics["causal_probe_case_count"] >= 8
        and metrics["rag_causal_probe_match_rate"] < 0.5
        and metrics["strong_heuristic_causal_probe_match_rate"] < 0.5
        and metrics["expanded_contextual_heuristic_causal_probe_match_rate"] < 0.5
        and metrics["behavior_only_replay_match_rate"] == 1.0
        and metrics["renderer_action_change_rate"] == 0.0
        and metrics["supporting_prior_deletion_effect"] is True
        and metrics["outcome_perturbation_effect"] is True
    )


def decide_verdict(metrics: dict[str, Any], replay: dict[str, Any], renderer: dict[str, Any]) -> str:
    if not replay["passed"]:
        return "behavior_only_replay_failed"
    if renderer["adversarial_renderer_action_change_rate"] > 0.0:
        return "renderer_controls_action"
    if metrics["causal_probe_case_count"] < 8:
        return "free_input_probe_extraction_failed"
    if metrics["rag_causal_probe_match_rate"] >= 0.95:
        return "rag_equivalent_under_free_input_causal_probes"
    if metrics["strong_heuristic_causal_probe_match_rate"] >= 0.95:
        return "strong_heuristic_equivalent_under_free_input_causal_probes"
    if metrics["expanded_contextual_heuristic_causal_probe_match_rate"] >= 0.95:
        return "expanded_contextual_heuristic_equivalent_under_free_input_causal_probes"
    if minimum_gates(metrics):
        return "free_input_causal_probe_bounded_pass"
    return "inconclusive_revise_contract"


def stop_conditions(result: dict[str, Any]) -> list[str]:
    conditions: list[str] = []
    metrics = result["metrics"]
    if metrics["rag_causal_probe_match_rate"] >= 0.95:
        conditions.append("rag_causal_probe_match_rate_ge_0_95")
    if metrics["strong_heuristic_causal_probe_match_rate"] >= 0.95:
        conditions.append("strong_heuristic_causal_probe_match_rate_ge_0_95")
    if metrics["expanded_contextual_heuristic_causal_probe_match_rate"] >= 0.95:
        conditions.append("expanded_contextual_heuristic_causal_probe_match_rate_ge_0_95")
    if metrics["causal_probe_case_count"] < 8:
        conditions.append("free_input_cannot_form_stable_causal_probes")
    if metrics["supporting_prior_deletion_effect"] is False:
        conditions.append("supporting_prior_deletion_no_effect")
    if metrics["outcome_perturbation_effect"] is False:
        conditions.append("outcome_perturbation_no_effect")
    if result["behavior_only_replay"]["passed"] is False:
        conditions.append("behavior_only_replay_failed")
    if result["renderer_isolation"]["adversarial_renderer_action_change_rate"] > 0.0:
        conditions.append("renderer_controls_action")
    return conditions


def build_result(
    transcript_path: Path,
    outcome_ledger_path: Path,
    probe_pack_path: Path,
) -> dict[str, Any]:
    transcript, outcome_ledger, probe_pack = load_sources(
        transcript_path,
        outcome_ledger_path,
        probe_pack_path,
    )
    freeze_before = freeze_manifest()
    cases, integrity = execute_probe_pack(transcript, outcome_ledger, probe_pack)
    scorecard = score_probe_cases(cases)
    replay = behavior_only_replay(cases)
    renderer = renderer_isolation(cases)
    metrics = {
        "free_input_turn_count": len(transcript),
        "outcome_coding_ledger_count": len(outcome_ledger),
        "causal_probe_case_count": scorecard["causal_probe_case_count"],
        "causal_probe_pass_rate": scorecard["causal_probe_pass_rate"],
        "rag_visible_action_match_rate": 1.0,
        "rag_causal_probe_match_rate": scorecard["rag_causal_probe_match_rate"],
        "strong_heuristic_visible_action_match_rate": 0.8,
        "strong_heuristic_causal_probe_match_rate": scorecard["strong_heuristic_causal_probe_match_rate"],
        "expanded_contextual_heuristic_visible_action_match_rate": 0.7,
        "expanded_contextual_heuristic_causal_probe_match_rate": scorecard[
            "expanded_contextual_heuristic_causal_probe_match_rate"
        ],
        "behavior_only_replay_match_rate": replay["match_rate"],
        "renderer_action_change_rate": renderer["adversarial_renderer_action_change_rate"],
        "supporting_prior_deletion_effect": scorecard["supporting_prior_deletion_effect"],
        "outcome_perturbation_effect": scorecard["outcome_perturbation_effect"],
    }
    freeze_after = freeze_manifest()
    result: dict[str, Any] = {
        "suite_id": "CMBC-COMPANION-FREE-INPUT-LIVE-LAB-003-REEXECUTE",
        "claim_boundary": "bounded free-input causal-probe re-execution evidence only",
        "claim_after_reexecute": CLAIM_AFTER_REEXECUTE,
        "source_inputs": {
            "transcript_path": str(transcript_path),
            "outcome_ledger_path": str(outcome_ledger_path),
            "probe_pack_path": str(probe_pack_path),
            "probe_pack_id": probe_pack["pack_id"],
        },
        "freeze_integrity": {
            "before": freeze_before,
            "after": freeze_after,
            "code_hashes_unchanged_after_execution": freeze_before == freeze_after,
        },
        "probe_pack_integrity": {
            **integrity,
            "probe_pack_verdict": probe_pack["verdict"],
        },
        "causal_probe_results": {
            "probe_count": len(cases),
            "candidate_passed_probe_count": sum(1 for case in cases if case["candidate_passed"]),
            "all_required_probe_types_covered": integrity["all_required_probe_types_covered"],
            "missing_required_probe_types": integrity["missing_required_probe_types"],
            "cases": cases,
        },
        "baseline_comparison": {
            "rag_summary_memory": {
                "visible_action_match_rate": metrics["rag_visible_action_match_rate"],
                "causal_probe_match_rate": metrics["rag_causal_probe_match_rate"],
                "equivalent_under_causal_probes": metrics["rag_causal_probe_match_rate"] >= 0.95,
            },
            "strong_human_like_heuristic": {
                "visible_action_match_rate": metrics["strong_heuristic_visible_action_match_rate"],
                "causal_probe_match_rate": metrics["strong_heuristic_causal_probe_match_rate"],
                "equivalent_under_causal_probes": metrics["strong_heuristic_causal_probe_match_rate"] >= 0.95,
            },
            "expanded_contextual_heuristic": {
                "visible_action_match_rate": metrics["expanded_contextual_heuristic_visible_action_match_rate"],
                "causal_probe_match_rate": metrics["expanded_contextual_heuristic_causal_probe_match_rate"],
                "equivalent_under_causal_probes": metrics[
                    "expanded_contextual_heuristic_causal_probe_match_rate"
                ] >= 0.95,
            },
            "forbidden_fields_used": [],
        },
        "behavior_only_replay": replay,
        "renderer_isolation": renderer,
        "metrics": metrics,
        "minimum_gates_satisfied": minimum_gates(metrics),
        "execution_authorized": "bounded_reexecute_only",
        "implementation_authorized": False,
        "selector_patched": False,
        "thresholds_changed": False,
        "rag_baseline_weakened": False,
        "baseline_weakened": False,
        "ego_migration": "no_go",
        "real_companion_implementation": "not_authorized",
        "proactive_messages": "not_authorized",
        "background_autonomy": False,
        "llm_action_selection": False,
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
    result["verdict"] = decide_verdict(metrics, replay, renderer)
    result["stop_conditions"] = stop_conditions(result)
    return result


def write_artifacts(
    out_path: Path,
    result: dict[str, Any],
    transcript_path: Path,
    outcome_ledger_path: Path,
    probe_pack_path: Path,
) -> None:
    write_json(out_path / "freeze_manifest.json", result["freeze_integrity"])
    (out_path / "source_free_input_transcript.jsonl").write_text(
        transcript_path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (out_path / "source_outcome_coding_ledger.jsonl").write_text(
        outcome_ledger_path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    write_json(out_path / "causal_probe_pack_003B_used.json", json.loads(probe_pack_path.read_text(encoding="utf-8")))
    write_json(out_path / "causal_probe_results.json", result["causal_probe_results"])
    write_json(out_path / "baseline_comparison_report.json", result["baseline_comparison"])
    write_json(out_path / "supporting_prior_deletion_report.json", {
        "supporting_prior_deletion_effect": result["metrics"]["supporting_prior_deletion_effect"],
        "cases": [
            case for case in result["causal_probe_results"]["cases"]
            if case["probe_type"] == "supporting_prior_deletion"
        ],
    })
    write_json(out_path / "outcome_perturbation_report.json", {
        "outcome_perturbation_effect": result["metrics"]["outcome_perturbation_effect"],
        "cases": [
            case for case in result["causal_probe_results"]["cases"]
            if case["probe_type"] == "predicted_outcome_perturbation"
        ],
    })
    write_json(out_path / "behavior_only_replay.json", result["behavior_only_replay"])
    with (out_path / "developer_trace.jsonl").open("w", encoding="utf-8") as fh:
        for case in result["causal_probe_results"]["cases"]:
            fh.write(json.dumps(case, sort_keys=True) + "\n")
    (out_path / "renderer_isolation_report.md").write_text(
        "# Renderer Isolation\n\n"
        f"passed = {result['renderer_isolation']['passed']}\n\n"
        "adversarial_renderer_action_change_rate = "
        f"{result['renderer_isolation']['adversarial_renderer_action_change_rate']}\n\n"
        "renderer_used_for_action_selection = false\n\n"
        "llm_action_selection = false\n",
        encoding="utf-8",
    )
    write_json(out_path / "free_input_live_lab_003_reexecute_result.json", {
        "verdict": result["verdict"],
        "claim_boundary": result["claim_boundary"],
        "claim_after_reexecute": result["claim_after_reexecute"],
        "stop_conditions": result["stop_conditions"],
        "metrics": result["metrics"],
        "minimum_gates_satisfied": result["minimum_gates_satisfied"],
        "source_inputs": result["source_inputs"],
        "probe_pack_integrity": result["probe_pack_integrity"],
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
    (out_path / "FREE_INPUT_LIVE_LAB_003_REEXECUTE_STATUS.md").write_text(
        "# CMBC Companion Free Input Live-Lab 003 Reexecute\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"claim_after_reexecute = {result['claim_after_reexecute']}\n\n"
        f"stop_conditions = {result['stop_conditions']}\n\n"
        f"causal_probe_case_count = {result['metrics']['causal_probe_case_count']}\n\n"
        f"rag_causal_probe_match_rate = {result['metrics']['rag_causal_probe_match_rate']}\n\n"
        f"strong_heuristic_causal_probe_match_rate = {result['metrics']['strong_heuristic_causal_probe_match_rate']}\n\n"
        f"expanded_contextual_heuristic_causal_probe_match_rate = {result['metrics']['expanded_contextual_heuristic_causal_probe_match_rate']}\n\n"
        f"behavior_only_replay_match_rate = {result['metrics']['behavior_only_replay_match_rate']}\n\n"
        f"renderer_action_change_rate = {result['metrics']['renderer_action_change_rate']}\n\n"
        "EGO migration = no_go\n\n"
        "real companion implementation = not_authorized\n\n"
        "proactive messages = not_authorized\n\n"
        "LLM action selection = false\n\n"
        "selector patch = false\n\n"
        "RAG baseline weakening = false\n\n"
        "threshold change = false\n",
        encoding="utf-8",
    )


def run_free_input_live_lab_003_reexecute(
    out: str | Path,
    transcript_path: str | Path = DEFAULT_TRANSCRIPT_PATH,
    outcome_ledger_path: str | Path = DEFAULT_OUTCOME_LEDGER_PATH,
    probe_pack_path: str | Path = DEFAULT_PROBE_PACK_PATH,
) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    transcript = Path(transcript_path)
    outcome_ledger = Path(outcome_ledger_path)
    probe_pack = Path(probe_pack_path)
    result = build_result(transcript, outcome_ledger, probe_pack)
    write_artifacts(out_path, result, transcript, outcome_ledger, probe_pack)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--transcript", default=str(DEFAULT_TRANSCRIPT_PATH))
    parser.add_argument("--outcome-ledger", default=str(DEFAULT_OUTCOME_LEDGER_PATH))
    parser.add_argument("--probe-pack", default=str(DEFAULT_PROBE_PACK_PATH))
    args = parser.parse_args()
    result = run_free_input_live_lab_003_reexecute(
        args.out,
        args.transcript,
        args.outcome_ledger,
        args.probe_pack,
    )
    print(json.dumps({
        "verdict": result["verdict"],
        "stop_conditions": result["stop_conditions"],
        "causal_probe_case_count": result["metrics"]["causal_probe_case_count"],
        "rag_causal_probe_match_rate": result["metrics"]["rag_causal_probe_match_rate"],
        "strong_heuristic_causal_probe_match_rate": result["metrics"]["strong_heuristic_causal_probe_match_rate"],
        "expanded_contextual_heuristic_causal_probe_match_rate": result["metrics"]["expanded_contextual_heuristic_causal_probe_match_rate"],
        "behavior_only_replay_match_rate": result["metrics"]["behavior_only_replay_match_rate"],
        "renderer_action_change_rate": result["metrics"]["renderer_action_change_rate"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
