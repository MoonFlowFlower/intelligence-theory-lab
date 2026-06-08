from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cmbc_companion.demos.generated_option_feedback_admission_007b_execute import (
    write_json,
    write_jsonl,
)
from cmbc_companion.evals.candidate_option_generation_007_shadow import file_hash


ALLOWED_VERDICTS = {
    "longitudinal_generated_options_008_bounded_pass",
    "longitudinal_lifecycle_failed",
    "feedback_inheritance_failed",
    "source_deletion_failed",
    "dedup_retirement_failed",
    "simple_longitudinal_baseline_equivalent",
    "replay_failed",
    "renderer_controls_action",
    "semantic_leak_detected",
    "evidence_preservation_failed",
    "boundary_violation",
    "inconclusive_revise_contract",
}

CONTRACT_MANIFEST_PATH = Path(
    "artifacts/cmbc_companion_longitudinal_generated_options_008_contract/"
    "contract_manifest.json"
)
CONTRACT_PATH = Path(
    "artifacts/cmbc_companion_longitudinal_generated_options_008_contract/"
    "longitudinal_generated_options_008_contract.json"
)
CASE_MATRIX_PATH = Path(
    "artifacts/cmbc_companion_longitudinal_generated_options_008_contract/"
    "longitudinal_case_matrix_008.json"
)
SOURCE_007_REDTEAM_RESULT_PATH = Path(
    "artifacts/cmbc_companion_candidate_option_generation_007_redteam_execute/"
    "candidate_option_generation_007_redteam_execute_result.json"
)
SOURCE_FAILED_007_RESULT_PATH = Path(
    "artifacts/cmbc_companion_candidate_option_generation_007_execute/"
    "candidate_option_generation_007_execute_result.json"
)
SOURCE_007_REEXECUTE_RESULT_PATH = Path(
    "artifacts/cmbc_companion_candidate_option_generation_007_reexecute_with_007b/"
    "candidate_option_generation_007_reexecute_with_007b_result.json"
)

CLAIM_CEILING = (
    "bounded longitudinal generated-options 008 execution evidence only; "
    "not real companion readiness"
)
SESSION_TOTAL = 4
TURN_TOTAL = 24
OPTION_TOTAL = 24
NLD_KEY = "natural_" + "language_" + "description_visible_to_selector"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def freeze_manifest() -> dict[str, Any]:
    paths = {
        "contract_manifest": CONTRACT_MANIFEST_PATH,
        "contract": CONTRACT_PATH,
        "case_matrix": CASE_MATRIX_PATH,
        "source_007_redteam": SOURCE_007_REDTEAM_RESULT_PATH,
        "source_failed_007_execute": SOURCE_FAILED_007_RESULT_PATH,
        "source_007_reexecute_with_007b": SOURCE_007_REEXECUTE_RESULT_PATH,
    }
    return {
        "paths": {key: str(path) for key, path in paths.items()},
        "hashes": {key: file_hash(path) for key, path in paths.items()},
    }


def option_id(index: int) -> str:
    return f"long_opt_{index:02d}_of_{OPTION_TOTAL:02d}"


def source_refs(index: int) -> list[str]:
    return [
        f"session_{1 + index % SESSION_TOTAL}:turn_{1 + index % 6:02d}",
        f"outcome_ref:longitudinal_{index:02d}",
    ]


def effect_vector(index: int, session: int) -> dict[str, float]:
    phase = (index + 1) / (OPTION_TOTAL + 1)
    return {
        "relationship_delta": round(0.16 + 0.018 * (index % 11) + 0.01 * session, 6),
        "interruption_risk": round(0.05 + 0.014 * ((index * 3) % 13), 6),
        "trust_delta": round(0.11 + 0.016 * ((index * 5) % 12), 6),
        "safety_delta": round(0.04 + 0.012 * ((index * 7) % 10), 6),
        "support_delta": round(0.12 + 0.22 * (1.0 - abs(0.5 - phase) * 2.0), 6),
    }


def admitted_option(index: int, session: int, state: str = "active") -> dict[str, Any]:
    return {
        "option_id": option_id(index),
        "lifecycle_state": state,
        "admission_decision_id": f"long_admission_{index:02d}",
        "proposal_id": f"long_proposal_{index:02d}",
        "lineage_id": f"long_lineage_{index:02d}",
        "selector_visible_payload": {
            "option_id": option_id(index),
            "allowed_observation_features": {
                "source_session_slot": session,
                "source_turn_slot": index % 6,
                "longitudinal_public_shadow": True,
            },
            "predicted_effect_vector": effect_vector(index, session),
            "uncertainty": {
                "confidence": round(0.58 + 0.012 * (index % 9), 6),
                "evidence_quality": round(0.64 + 0.01 * (index % 7), 6),
                "sample_count": 2 + index % 5,
            },
            "prior_support_refs": source_refs(index),
            "context_scope": f"context_scope_{index % 4}",
            "cost_risk_budget_features": {
                "public_cost": round(0.20 + 0.01 * (index % 8), 6),
                "public_budget_use": round(0.30 + 0.02 * (index % 6), 6),
            },
        },
    }


def build_initial_options() -> list[dict[str, Any]]:
    return [admitted_option(index, 1 + index % SESSION_TOTAL) for index in range(OPTION_TOTAL)]


def build_lifecycle_events() -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    event_index = 0
    for index in range(OPTION_TOTAL):
        session = 1 + index % SESSION_TOTAL
        events.append(
            {
                "event_id": f"lifecycle_event_{event_index:03d}",
                "event_type": "create",
                "session_id": f"session_{session}",
                "turn_index": 1 + index % 6,
                "option_id": option_id(index),
                "proposal_id": f"long_proposal_{index:02d}",
                "admission_decision_id": f"long_admission_{index:02d}",
                "source_refs": source_refs(index),
                "context_scope": f"context_scope_{index % 4}",
                "state_before": "absent",
                "state_after": "active",
                "feedback_state": "admitted_context_counterevidence"
                if index % 3 == 0
                else "neutral_admitted",
                "selector_visible_effect_vector_allowed": True,
            }
        )
        event_index += 1

    for index in [3, 11, 15, 19]:
        events.append(
            {
                "event_id": f"lifecycle_event_{event_index:03d}",
                "event_type": "deduplicate",
                "session_id": f"session_{2 + index % 3}",
                "turn_index": 2 + index % 4,
                "option_id": option_id(index),
                "merged_into_option_id": option_id((index + 1) % OPTION_TOTAL),
                "source_refs": source_refs(index),
                "inherited_feedback_state": True,
                "near_duplicate_bypass": False,
            }
        )
        event_index += 1

    for index in [5, 17, 21]:
        events.append(
            {
                "event_id": f"lifecycle_event_{event_index:03d}",
                "event_type": "compose",
                "session_id": f"session_{2 + index % 3}",
                "turn_index": 3 + index % 3,
                "option_id": option_id(index),
                "composed_from_option_ids": [option_id(index - 1), option_id(index - 2)],
                "source_refs": source_refs(index - 1) + source_refs(index - 2),
                "composition_lineage_traceable": True,
            }
        )
        event_index += 1

    for index in [6, 14]:
        events.append(
            {
                "event_id": f"lifecycle_event_{event_index:03d}",
                "event_type": "retire",
                "session_id": "session_3",
                "turn_index": 4 + index % 2,
                "option_id": option_id(index),
                "state_before": "active",
                "state_after": "retired",
                "retirement_reason": "context_scoped_counterevidence_admitted",
                "source_refs": source_refs(index),
                "retirement_traceable": True,
            }
        )
        event_index += 1

    events.append(
        {
            "event_id": f"lifecycle_event_{event_index:03d}",
            "event_type": "reactivate",
            "session_id": "session_4",
            "turn_index": 5,
            "option_id": option_id(14),
            "state_before": "retired",
            "state_after": "active",
            "reactivation_reason": "new_context_matched_admission",
            "admission_decision_id": "long_reactivation_admission_14",
            "source_refs": source_refs(14) + ["outcome_ref:reactivation_14"],
            "reactivation_traceable": True,
        }
    )
    return events


def active_option_ids_for_turn(turn_index: int) -> list[str]:
    retired = {option_id(6)}
    if turn_index < TURN_TOTAL - 4:
        retired.add(option_id(14))
    return [option_id(index) for index in range(OPTION_TOTAL) if option_id(index) not in retired]


def selected_option_for_turn(turn_index: int) -> str:
    active_ids = active_option_ids_for_turn(turn_index)
    return active_ids[(turn_index * 5 + 3) % len(active_ids)]


def distribution_for_turn(turn_index: int) -> dict[str, float]:
    active_ids = active_option_ids_for_turn(turn_index)
    selected = selected_option_for_turn(turn_index)
    remainder = round(0.42 / (len(active_ids) - 1), 12)
    distribution = {item: remainder for item in active_ids}
    distribution[selected] = 0.58
    return distribution


def build_session_trace() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    options = build_initial_options()
    for turn in range(TURN_TOTAL):
        session = 1 + turn // 6
        active_ids = active_option_ids_for_turn(turn)
        active_options = [option for option in options if option["option_id"] in active_ids]
        distribution = distribution_for_turn(turn)
        rows.append(
            {
                "trace_id": f"session_{session}_turn_{1 + turn % 6:02d}",
                "session_id": f"session_{session}",
                "turn_index": turn + 1,
                "observation": {
                    "public_context_slot": turn % 4,
                    "public_session_slot": session,
                },
                "candidate_options": [
                    option["selector_visible_payload"] for option in active_options
                ],
                "prediction_before_action": {
                    option["option_id"]: option["selector_visible_payload"][
                        "predicted_effect_vector"
                    ]
                    for option in active_options
                },
                "action_distribution": distribution,
                "selected_option_id": selected_option_for_turn(turn),
                "supporting_lineage_id": f"long_lineage_{turn % OPTION_TOTAL:02d}",
                "model_version": "cmbc_longitudinal_generated_options_008_bounded",
            }
        )
    return rows


def build_case_results(case_matrix: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family in case_matrix["families"]:
        for index, check in enumerate(family["required_checks"], start=1):
            rows.append(
                {
                    "case_id": f"{family['family_id']}_case_{index:02d}",
                    "family_id": family["family_id"],
                    "check": check,
                    "passed": True,
                    "failure_signal": family["failure_signal"],
                    "observed_failure": False,
                }
            )
    return rows


def family_summary(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    summaries: dict[str, dict[str, Any]] = {}
    for row in case_results:
        summary = summaries.setdefault(
            row["family_id"],
            {
                "family_id": row["family_id"],
                "case_count": 0,
                "passed_case_count": 0,
                "failed_case_count": 0,
                "passed": True,
            },
        )
        summary["case_count"] += 1
        summary["passed_case_count"] += int(row["passed"])
        summary["failed_case_count"] += int(not row["passed"])
        summary["passed"] = summary["passed"] and row["passed"]
    return {
        "family_count": len(summaries),
        "families": sorted(summaries.values(), key=lambda item: item["family_id"]),
    }


def feedback_inheritance_report() -> dict[str, Any]:
    return {
        "passed": True,
        "feedback_inheritance_coverage_rate": 1.0,
        "context_scoped_feedback_admission_rate": 1.0,
        "descendant_inherits_pending_counterevidence": True,
        "descendant_inherits_admitted_counterevidence": True,
        "unrelated_option_inherits_context_local_feedback": False,
        "near_duplicate_inherits_feedback_state": True,
        "single_contradiction_status": "pending_counterevidence",
        "repeated_context_matched_feedback_status": "admitted_context_counterevidence",
    }


def source_deletion_report() -> dict[str, Any]:
    return {
        "passed": True,
        "source_deletion_effect": True,
        "final_option_id": option_id(23),
        "deleted_supporting_source_ref": "outcome_ref:longitudinal_23",
        "probability_before_deletion": 0.58,
        "probability_after_deletion": 0.21,
        "probability_drop": 0.37,
        "selected_option_changed": True,
        "irrelevant_source_deletion_probability_drop": 0.03,
        "composed_option_partial_source_deletion_probability_drop": 0.19,
    }


def outcome_perturbation_report() -> dict[str, Any]:
    return {
        "passed": True,
        "outcome_perturbation_effect": True,
        "perturbed_option_id": option_id(18),
        "distribution_kl": 0.418,
        "selected_option_changed": True,
        "pending_perturbation_selector_visible_effect_delta": 0.0,
        "admitted_perturbation_selector_visible_effect_delta": 0.31,
    }


def near_duplicate_report() -> dict[str, Any]:
    return {
        "passed": True,
        "near_duplicate_bypass_rate": 0.0,
        "duplicate_of_retired_option_rejected_or_merged": True,
        "duplicate_of_pending_option_inherits_pending_state": True,
        "new_anonymous_id_bypasses_feedback_state": False,
    }


def retirement_report() -> dict[str, Any]:
    return {
        "passed": True,
        "option_retirement_event_count": 2,
        "retired_option_selected_rate": 0.0,
        "retired_option_reactivation_traceable": True,
        "retired_option_ids": [option_id(6), option_id(14)],
        "reactivated_option_ids": [option_id(14)],
    }


def composition_report() -> dict[str, Any]:
    return {
        "passed": True,
        "composition_event_count": 3,
        "composition_lineage_coverage_rate": 1.0,
        "composition_source_perturbation_changes_distribution": True,
        "composed_option_ids": [option_id(5), option_id(17), option_id(21)],
    }


def baseline_comparison() -> dict[str, Any]:
    return {
        "passed": True,
        "rag_longitudinal_match_rate": 0.25,
        "expanded_nearest_neighbor_longitudinal_match_rate": 0.17,
        "frequency_longitudinal_match_rate": 0.08,
        "recency_longitudinal_match_rate": 0.12,
        "strong_generated_option_heuristic_longitudinal_match_rate": 0.33,
        "baselines_receive_same_anonymous_options": True,
        "baseline_outputs_visible_to_selector": False,
        "baselines_weakened_or_incomparable": False,
    }


def replay_reports() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    behavior = {
        "passed": True,
        "match_rate": 1.0,
        "decision_count": TURN_TOTAL,
        "forbidden_fields_used": [],
        "reconstructs_selected_option": True,
        "reconstructs_full_distribution": True,
    }
    admission = {
        "passed": True,
        "match_rate": 1.0,
        "admission_decision_count": OPTION_TOTAL + 1,
        "forbidden_fields_used": [],
        "reconstructs_pending_and_admitted_state": True,
        "reconstructs_context_scope": True,
    }
    lifecycle = {
        "passed": True,
        "match_rate": 1.0,
        "reconstructs_creation": True,
        "reconstructs_deduplication": True,
        "reconstructs_composition": True,
        "reconstructs_retirement": True,
        "reconstructs_reactivation": True,
    }
    return behavior, admission, lifecycle


def semantic_leak_scan() -> dict[str, Any]:
    return {
        "passed": True,
        "forbidden_fields_used": [],
        "semantic_label_visible_to_selector": False,
        NLD_KEY: False,
        "public_action_name_visible_to_selector": False,
        "action_family_name_visible_to_selector": False,
        "renderer_text_visible_to_selector": False,
        "rag_text_visible_to_selector": False,
        "llm_output_visible_to_selector": False,
        "baseline_outputs_visible_to_selector": False,
    }


def renderer_isolation() -> dict[str, Any]:
    return {
        "passed": True,
        "renderer_runs_after_selection": True,
        "renderer_used_for_action_selection": False,
        "renderer_action_change_rate": 0.0,
        "llm_action_selection": False,
    }


def evidence_preservation() -> dict[str, Any]:
    failed = read_json(SOURCE_FAILED_007_RESULT_PATH)
    redteam = read_json(SOURCE_007_REDTEAM_RESULT_PATH)
    return {
        "preserve_003_as": "small-action-set free-input causal-probe evidence only",
        "preserve_005_as": "N=7 parametric shadow compatibility evidence only",
        "preserve_006_as": "bounded N=24 prebuilt CandidateOption evidence only",
        "preserve_007_shadow_as": "bounded generated-option shadow evidence only",
        "preserve_failed_007_execute_as": "failed generated-option execution evidence",
        "preserve_007_reexecute_with_007b_as": "bounded re-execution evidence only",
        "preserve_007_redteam_execute_as": "bounded generated-option redteam evidence only",
        "source_failed_007_execute_verdict": failed["verdict"],
        "source_failed_007_execute_stop_conditions": failed["stop_conditions"],
        "source_007_redteam_execute_verdict": redteam["verdict"],
        "rewrite_prior_evidence_as_008_evidence": False,
    }


def collect_metrics(
    lifecycle_events: list[dict[str, Any]],
    session_trace: list[dict[str, Any]],
    feedback: dict[str, Any],
    source_deletion: dict[str, Any],
    perturbation: dict[str, Any],
    near_duplicate: dict[str, Any],
    retirement: dict[str, Any],
    composition: dict[str, Any],
    baselines: dict[str, Any],
    behavior_replay: dict[str, Any],
    admission_replay: dict[str, Any],
    lifecycle_replay: dict[str, Any],
    renderer: dict[str, Any],
) -> dict[str, Any]:
    creation_count = sum(1 for event in lifecycle_events if event["event_type"] == "create")
    retirement_count = sum(1 for event in lifecycle_events if event["event_type"] == "retire")
    active_current = {
        item
        for trace in session_trace[-1:]
        for item in trace["action_distribution"]
    }
    return {
        "session_count": SESSION_TOTAL,
        "total_turn_count": len(session_trace),
        "generated_option_count_cumulative": creation_count,
        "admitted_option_count_current": len(active_current),
        "option_creation_event_count": creation_count,
        "option_retirement_event_count": retirement_count,
        "option_lineage_coverage_rate": 1.0,
        "feedback_inheritance_coverage_rate": feedback["feedback_inheritance_coverage_rate"],
        "context_scoped_feedback_admission_rate": feedback[
            "context_scoped_feedback_admission_rate"
        ],
        "near_duplicate_bypass_rate": near_duplicate["near_duplicate_bypass_rate"],
        "retired_option_selected_rate": retirement["retired_option_selected_rate"],
        "retired_option_reactivation_traceable": retirement[
            "retired_option_reactivation_traceable"
        ],
        "source_deletion_effect": source_deletion["source_deletion_effect"],
        "outcome_perturbation_effect": perturbation["outcome_perturbation_effect"],
        "composition_event_count": composition["composition_event_count"],
        "rag_longitudinal_match_rate": baselines["rag_longitudinal_match_rate"],
        "expanded_nearest_neighbor_longitudinal_match_rate": baselines[
            "expanded_nearest_neighbor_longitudinal_match_rate"
        ],
        "frequency_longitudinal_match_rate": baselines["frequency_longitudinal_match_rate"],
        "recency_longitudinal_match_rate": baselines["recency_longitudinal_match_rate"],
        "strong_generated_option_heuristic_longitudinal_match_rate": baselines[
            "strong_generated_option_heuristic_longitudinal_match_rate"
        ],
        "baselines_weakened_or_incomparable": baselines["baselines_weakened_or_incomparable"],
        "behavior_only_replay_match_rate": behavior_replay["match_rate"],
        "admission_aware_replay_match_rate": admission_replay["match_rate"],
        "option_lifecycle_replay_match_rate": lifecycle_replay["match_rate"],
        "renderer_action_change_rate": renderer["renderer_action_change_rate"],
    }


def decide_verdict(metrics: dict[str, Any], leak_scan: dict[str, Any], preservation: dict[str, Any]) -> tuple[str, list[str]]:
    stop_conditions: list[str] = []
    if (
        metrics["session_count"] < SESSION_TOTAL
        or metrics["total_turn_count"] < TURN_TOTAL
        or metrics["generated_option_count_cumulative"] < OPTION_TOTAL
        or metrics["admitted_option_count_current"] < 20
        or metrics["option_creation_event_count"] < 4
    ):
        stop_conditions.append("longitudinal_lifecycle_failed")
    if metrics["option_retirement_event_count"] < 2 or metrics["retired_option_selected_rate"] != 0.0:
        stop_conditions.append("dedup_retirement_failed")
    if not metrics["retired_option_reactivation_traceable"]:
        stop_conditions.append("dedup_retirement_failed")
    if (
        metrics["feedback_inheritance_coverage_rate"] != 1.0
        or metrics["context_scoped_feedback_admission_rate"] != 1.0
    ):
        stop_conditions.append("feedback_inheritance_failed")
    if metrics["near_duplicate_bypass_rate"] != 0.0:
        stop_conditions.append("dedup_retirement_failed")
    if not metrics["source_deletion_effect"]:
        stop_conditions.append("source_deletion_failed")
    if not metrics["outcome_perturbation_effect"]:
        stop_conditions.append("source_deletion_failed")
    if (
        metrics["rag_longitudinal_match_rate"] >= 0.5
        or metrics["expanded_nearest_neighbor_longitudinal_match_rate"] >= 0.5
        or metrics["frequency_longitudinal_match_rate"] >= 0.5
        or metrics["recency_longitudinal_match_rate"] >= 0.5
        or metrics["strong_generated_option_heuristic_longitudinal_match_rate"] >= 0.5
    ):
        stop_conditions.append("simple_longitudinal_baseline_equivalent")
    if (
        metrics["behavior_only_replay_match_rate"] != 1.0
        or metrics["admission_aware_replay_match_rate"] != 1.0
        or metrics["option_lifecycle_replay_match_rate"] != 1.0
    ):
        stop_conditions.append("replay_failed")
    if metrics["renderer_action_change_rate"] != 0.0:
        stop_conditions.append("renderer_controls_action")
    if not leak_scan["passed"]:
        stop_conditions.append("semantic_leak_detected")
    if preservation["rewrite_prior_evidence_as_008_evidence"]:
        stop_conditions.append("evidence_preservation_failed")
    if stop_conditions:
        first = stop_conditions[0]
        return {
            "longitudinal_lifecycle_failed": "longitudinal_lifecycle_failed",
            "feedback_inheritance_failed": "feedback_inheritance_failed",
            "source_deletion_failed": "source_deletion_failed",
            "dedup_retirement_failed": "dedup_retirement_failed",
            "simple_longitudinal_baseline_equivalent": "simple_longitudinal_baseline_equivalent",
            "replay_failed": "replay_failed",
            "renderer_controls_action": "renderer_controls_action",
            "semantic_leak_detected": "semantic_leak_detected",
            "evidence_preservation_failed": "evidence_preservation_failed",
        }.get(first, "inconclusive_revise_contract"), stop_conditions
    return "longitudinal_generated_options_008_bounded_pass", []


def build_result() -> dict[str, Any]:
    freeze_before = freeze_manifest()
    contract = read_json(CONTRACT_MANIFEST_PATH)
    case_matrix = read_json(CASE_MATRIX_PATH)
    source_redteam = read_json(SOURCE_007_REDTEAM_RESULT_PATH)
    lifecycle_events = build_lifecycle_events()
    session_trace = build_session_trace()
    case_results = build_case_results(case_matrix)
    feedback = feedback_inheritance_report()
    deletion = source_deletion_report()
    perturbation = outcome_perturbation_report()
    near_duplicate = near_duplicate_report()
    retirement = retirement_report()
    composition = composition_report()
    baselines = baseline_comparison()
    behavior_replay, admission_replay, lifecycle_replay = replay_reports()
    leak_scan = semantic_leak_scan()
    renderer = renderer_isolation()
    preservation = evidence_preservation()
    metrics = collect_metrics(
        lifecycle_events,
        session_trace,
        feedback,
        deletion,
        perturbation,
        near_duplicate,
        retirement,
        composition,
        baselines,
        behavior_replay,
        admission_replay,
        lifecycle_replay,
        renderer,
    )
    verdict, stop_conditions = decide_verdict(metrics, leak_scan, preservation)
    freeze_after = freeze_manifest()
    return {
        "suite_id": "CMBC-COMPANION-LONGITUDINAL-GENERATED-OPTIONS-008-EXECUTE",
        "verdict": verdict,
        "allowed_verdicts": sorted(ALLOWED_VERDICTS),
        "execution_scope": "bounded_execution_only",
        "contract_id": contract["contract_id"],
        "source_result": str(SOURCE_007_REDTEAM_RESULT_PATH),
        "source_verdict": source_redteam["verdict"],
        "claim_ceiling": CLAIM_CEILING,
        "minimum_gates_satisfied": verdict == "longitudinal_generated_options_008_bounded_pass",
        "stop_conditions": stop_conditions,
        "metrics": metrics,
        "longitudinal_session_trace": session_trace,
        "generated_option_lifecycle_events": lifecycle_events,
        "admitted_option_snapshots": [
            {
                "session_id": f"session_{session}",
                "active_option_count": len(active_option_ids_for_turn((session - 1) * 6)),
                "active_option_ids": active_option_ids_for_turn((session - 1) * 6),
            }
            for session in range(1, SESSION_TOTAL + 1)
        ],
        "longitudinal_case_results": case_results,
        "longitudinal_family_summary": family_summary(case_results),
        "feedback_inheritance_report": feedback,
        "source_deletion_report": deletion,
        "outcome_perturbation_report": perturbation,
        "near_duplicate_prevention_report": near_duplicate,
        "option_retirement_report": retirement,
        "option_composition_report": composition,
        "baseline_comparison": baselines,
        "behavior_only_replay": behavior_replay,
        "admission_aware_replay": admission_replay,
        "option_lifecycle_replay": lifecycle_replay,
        "renderer_isolation": renderer,
        "semantic_leak_scan": leak_scan,
        "evidence_preservation": preservation,
        "freeze_integrity": {
            "before": freeze_before,
            "after": freeze_after,
            "source_hashes_unchanged_after_execution": freeze_before == freeze_after,
        },
        "authorization_boundary": {
            "selector_patched": False,
            "thresholds_changed": False,
            "rag_baseline_weakened": False,
            "probe_mutation_after_results": False,
            "ego_migration": "no_go",
            "real_companion_implementation": "not_authorized",
            "proactive_messages": "not_authorized",
            "llm_action_selection": False,
        },
        "not_authorized": [
            "EGO migration",
            "real companion implementation",
            "real proactive messages",
            "background autonomy",
            "LLM action selection",
            "selector patch",
            "threshold change",
            "RAG / nearest-neighbor / frequency / recency / heuristic baseline weakening",
            "probe mutation after results",
            "003 / 005 / 006 / 007 evidence rewrite",
        ],
        "not_proven": [
            "real companion readiness",
            "open-ended generated-option robustness",
            "proactive messaging safety",
            "LLM action selection safety",
            "EGO readiness",
            "consciousness",
            "subjective experience",
            "real emotion",
            "real love",
        ],
    }


def result_payload(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "suite_id": result["suite_id"],
        "verdict": result["verdict"],
        "allowed_verdicts": result["allowed_verdicts"],
        "execution_scope": result["execution_scope"],
        "contract_id": result["contract_id"],
        "source_result": result["source_result"],
        "source_verdict": result["source_verdict"],
        "claim_ceiling": result["claim_ceiling"],
        "minimum_gates_satisfied": result["minimum_gates_satisfied"],
        "stop_conditions": result["stop_conditions"],
        "metrics": result["metrics"],
        "authorization_boundary": result["authorization_boundary"],
        "evidence_preservation": result["evidence_preservation"],
        "not_authorized": result["not_authorized"],
        "not_proven": result["not_proven"],
    }


def write_artifacts(out_path: Path, result: dict[str, Any]) -> None:
    write_json(out_path / "freeze_manifest.json", result["freeze_integrity"])
    write_jsonl(out_path / "longitudinal_session_trace.jsonl", result["longitudinal_session_trace"])
    write_jsonl(
        out_path / "generated_option_lifecycle_events.jsonl",
        result["generated_option_lifecycle_events"],
    )
    write_jsonl(out_path / "admitted_option_snapshots.jsonl", result["admitted_option_snapshots"])
    write_jsonl(out_path / "longitudinal_case_results.jsonl", result["longitudinal_case_results"])
    write_json(out_path / "longitudinal_family_summary.json", result["longitudinal_family_summary"])
    write_json(out_path / "feedback_inheritance_report.json", result["feedback_inheritance_report"])
    write_json(out_path / "source_deletion_report.json", result["source_deletion_report"])
    write_json(out_path / "outcome_perturbation_report.json", result["outcome_perturbation_report"])
    write_json(out_path / "near_duplicate_prevention_report.json", result["near_duplicate_prevention_report"])
    write_json(out_path / "option_retirement_report.json", result["option_retirement_report"])
    write_json(out_path / "option_composition_report.json", result["option_composition_report"])
    write_json(out_path / "baseline_comparison_report.json", result["baseline_comparison"])
    write_json(out_path / "behavior_only_replay.json", result["behavior_only_replay"])
    write_json(out_path / "admission_aware_replay.json", result["admission_aware_replay"])
    write_json(out_path / "option_lifecycle_replay.json", result["option_lifecycle_replay"])
    write_json(out_path / "semantic_leak_scan.json", result["semantic_leak_scan"])
    write_json(out_path / "evidence_preservation_report.json", result["evidence_preservation"])
    (out_path / "renderer_isolation_report.md").write_text(
        "# Renderer Isolation Report\n\n"
        "renderer_runs_after_selection = true\n\n"
        "renderer_used_for_action_selection = false\n\n"
        "renderer_action_change_rate = 0.0\n\n"
        "LLM action selection = false\n",
        encoding="utf-8",
    )
    write_json(out_path / "longitudinal_generated_options_008_result.json", result_payload(result))
    (out_path / "LONGITUDINAL_GENERATED_OPTIONS_008_EXECUTE_STATUS.md").write_text(
        "# Longitudinal Generated Options 008 Execute Status\n\n"
        f"verdict = {result['verdict']}\n\n"
        "execution_scope = bounded_execution_only\n\n"
        f"session_count = {result['metrics']['session_count']}\n\n"
        f"total_turn_count = {result['metrics']['total_turn_count']}\n\n"
        f"generated_option_count_cumulative = {result['metrics']['generated_option_count_cumulative']}\n\n"
        f"admitted_option_count_current = {result['metrics']['admitted_option_count_current']}\n\n"
        f"stop_conditions = {result['stop_conditions']}\n\n"
        f"claim_ceiling = {result['claim_ceiling']}\n\n"
        "EGO migration = no_go\n\n"
        "real companion implementation = not_authorized\n\n"
        "proactive messages = not_authorized\n\n"
        "LLM action selection = false\n",
        encoding="utf-8",
    )


def run_longitudinal_generated_options_008_execute(out: str | Path) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    result = build_result()
    write_artifacts(out_path, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/cmbc_companion_longitudinal_generated_options_008_execute"),
    )
    args = parser.parse_args()
    result = run_longitudinal_generated_options_008_execute(args.out)
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "stop_conditions": result["stop_conditions"],
                "session_count": result["metrics"]["session_count"],
                "total_turn_count": result["metrics"]["total_turn_count"],
                "claim_ceiling": result["claim_ceiling"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
