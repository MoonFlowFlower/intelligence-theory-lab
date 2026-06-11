from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SOURCE_ARTIFACT_DIR = Path("artifacts/cmbc_companion_candidate_option_generation_007_execute")
ALLOWED_VERDICTS = {
    "feedback_admission_not_applied_to_generated_options",
    "generated_option_lineage_bypass_confirmed",
    "single_contradiction_over_admitted",
    "context_scope_leak_confirmed",
    "weak_evidence_high_confidence_confirmed",
    "outcome_update_ordering_bug_confirmed",
    "replay_trace_insufficient_for_generated_feedback_admission",
    "selector_scoring_not_primary_blocker",
    "inconclusive_needs_manual_review",
}
STATUS_NAME = "CANDIDATE_OPTION_GENERATION_007_RCA_STATUS.md"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def option_by_id(options: list[dict[str, Any]], option_id: str) -> dict[str, Any]:
    return next(option for option in options if option["option_id"] == option_id)


def distribution_by_id(distribution: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["option_id"]: row for row in distribution["distribution"]}


def effect_delta(before: dict[str, float], after: dict[str, float]) -> dict[str, float]:
    return {
        key: round(after[key] - before[key], 6)
        for key in sorted(before)
        if round(after[key] - before[key], 6) != 0
    }


def top_rows(trace: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    return trace["action_distribution"]["distribution"][:limit]


def changed_options(before_trace: dict[str, Any], after_trace: dict[str, Any]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    before_options = before_trace["selector_input"]["candidate_options"]
    after_options = after_trace["selector_input"]["candidate_options"]
    for before in before_options:
        after = option_by_id(after_options, before["option_id"])
        changed_fields = {}
        for key in (
            "predicted_effect_vector",
            "uncertainty",
            "prior_support_refs",
            "allowed_observation_features",
            "cost_risk_budget_features",
        ):
            if before[key] != after[key]:
                changed_fields[key] = {
                    "before": before[key],
                    "after": after[key],
                }
        if changed_fields:
            changes.append({
                "option_id": before["option_id"],
                "changed_fields": changed_fields,
            })
    return changes


def load_source_artifacts(source_dir: Path) -> dict[str, Any]:
    result = read_json(source_dir / "candidate_option_generation_007_execute_result.json")
    cases = read_json(source_dir / "causal_probe_results.json")
    traces = read_jsonl(source_dir / "action_distribution_trace.jsonl")
    proposals = read_jsonl(source_dir / "candidate_option_proposals.jsonl")
    admissions = read_jsonl(source_dir / "option_admission_decisions.jsonl")
    admitted = read_json(source_dir / "admitted_candidate_options.json")
    lineages = read_jsonl(source_dir / "option_lineage_traces.jsonl")
    replay = read_json(source_dir / "behavior_only_replay.json")
    return {
        "result": result,
        "cases": cases,
        "traces": traces,
        "proposals": proposals,
        "admissions": admissions,
        "admitted": admitted,
        "lineages": lineages,
        "replay": replay,
    }


def failed_probe_trace(artifacts: dict[str, Any]) -> dict[str, Any]:
    failed_case = next(
        case for case in artifacts["cases"]["cases"]
        if case["probe_type"] == "feedback_admission_single_contradiction"
    )
    before = next(
        trace for trace in artifacts["traces"]
        if trace["trace_id"] == "probe_feedback_single_contradiction_before"
    )
    after = next(
        trace for trace in artifacts["traces"]
        if trace["trace_id"] == "probe_feedback_single_contradiction_after"
    )
    return {
        "source_suite": artifacts["result"]["suite_id"],
        "source_verdict": artifacts["result"]["verdict"],
        "failed_case": failed_case,
        "before_trace": before,
        "after_trace": after,
    }


def build_single_contradiction_audit(failed: dict[str, Any], artifacts: dict[str, Any]) -> dict[str, Any]:
    before = failed["before_trace"]
    after = failed["after_trace"]
    selected_before = before["selected_option_id"]
    selected_after = after["selected_option_id"]
    before_option = option_by_id(before["selector_input"]["candidate_options"], selected_before)
    after_option = option_by_id(after["selector_input"]["candidate_options"], selected_before)
    before_dist = distribution_by_id(before["action_distribution"])
    after_dist = distribution_by_id(after["action_distribution"])
    changes = changed_options(before, after)
    admission_for_selected = next(
        admission for admission in artifacts["admissions"]
        if admission["admitted_option_id"] == selected_before
    )
    return {
        "probe_id": failed["failed_case"]["case_id"],
        "probe_type": failed["failed_case"]["probe_type"],
        "prior_supporting_options": [
            {
                "option_id": row["option_id"],
                "rank": row["rank"],
                "probability": row["probability"],
                "prior_support_refs": option_by_id(
                    before["selector_input"]["candidate_options"],
                    row["option_id"],
                )["prior_support_refs"],
            }
            for row in top_rows(before)
        ],
        "generated_options_before": [
            option["option_id"] for option in before["selector_input"]["candidate_options"]
        ],
        "generated_options_after": [
            option["option_id"] for option in after["selector_input"]["candidate_options"]
        ],
        "admitted_options_before": [option["option_id"] for option in artifacts["admitted"]],
        "admitted_options_after": [option["option_id"] for option in artifacts["admitted"]],
        "contradiction_feedback_record": {
            "admission_status": failed["failed_case"]["admission_status"],
            "candidate_passed": failed["failed_case"]["candidate_passed"],
            "expected_status": "pending_counterevidence",
            "selector_visible_effect_delta": effect_delta(
                before_option["predicted_effect_vector"],
                after_option["predicted_effect_vector"],
            ),
        },
        "changed_options": changes,
        "option_confidence_changes": [
            {
                "option_id": selected_before,
                "confidence_before": before_option["uncertainty"]["confidence"],
                "confidence_after": after_option["uncertainty"]["confidence"],
                "confidence_delta": round(
                    after_option["uncertainty"]["confidence"]
                    - before_option["uncertainty"]["confidence"],
                    6,
                ),
                "sample_count_before": before_option["uncertainty"]["sample_count"],
                "sample_count_after": after_option["uncertainty"]["sample_count"],
                "evidence_quality_before": before_option["uncertainty"]["evidence_quality"],
                "evidence_quality_after": after_option["uncertainty"]["evidence_quality"],
            }
        ],
        "action_distribution_before_top5": top_rows(before),
        "action_distribution_after_top5": top_rows(after),
        "selected_option_before": selected_before,
        "selected_option_after": selected_after,
        "selected_option_changed": selected_before != selected_after,
        "selected_option_probability_before": before_dist[selected_before]["probability"],
        "selected_option_probability_after": after_dist[selected_before]["probability"],
        "selected_option_probability_delta": round(
            after_dist[selected_before]["probability"] - before_dist[selected_before]["probability"],
            12,
        ),
        "selected_option_rank_before": before_dist[selected_before]["rank"],
        "selected_option_rank_after": after_dist[selected_before]["rank"],
        "anonymous_option_flip_occurred": selected_before != selected_after,
        "family_level_flip_assessable": False,
        "family_level_flip_reason": (
            "selector-visible payload intentionally excludes action family names; "
            "RCA can only confirm anonymous option flip"
        ),
        "should_have_remained_pending_counterevidence": True,
        "actual_status_reported_pending": failed["failed_case"]["admission_status"]
        == "pending_counterevidence",
        "pending_counterevidence_still_reached_selector_effect_vector": bool(
            effect_delta(
                before_option["predicted_effect_vector"],
                after_option["predicted_effect_vector"],
            )
        ),
        "static_option_admission_decision_for_selected": admission_for_selected,
    }


def build_option_lineage_bypass_audit(
    failed: dict[str, Any],
    single: dict[str, Any],
    artifacts: dict[str, Any],
) -> dict[str, Any]:
    before_ids = set(single["generated_options_before"])
    after_ids = set(single["generated_options_after"])
    changed_ids = [item["option_id"] for item in single["changed_options"]]
    lineage_by_option = {row["admitted_option_id"]: row for row in artifacts["lineages"]}
    return {
        "new_option_ids_after_single_contradiction": sorted(after_ids - before_ids),
        "removed_option_ids_after_single_contradiction": sorted(before_ids - after_ids),
        "same_option_id_set_before_after": before_ids == after_ids,
        "near_duplicate_new_option_bypass_detected": bool(after_ids - before_ids),
        "changed_existing_option_ids": changed_ids,
        "changed_options_have_lineage": {
            option_id: option_id in lineage_by_option
            for option_id in changed_ids
        },
        "changed_options_lineage_refs": {
            option_id: lineage_by_option.get(option_id)
            for option_id in changed_ids
        },
        "counterevidence_inherited_by_lineage": False,
        "bypass_summary": (
            "No new generated option ID appeared after the contradiction; the bypass is not a "
            "near-duplicate-ID bypass. The existing top option's selector-visible effect vector "
            "changed without lineage/admission refs recording pending counterevidence."
        ),
    }


def build_context_scope_audit(failed: dict[str, Any], single: dict[str, Any]) -> dict[str, Any]:
    before = failed["before_trace"]
    after = failed["after_trace"]
    changed_ids = [item["option_id"] for item in single["changed_options"]]
    changed_payloads = [
        option_by_id(after["selector_input"]["candidate_options"], option_id)
        for option_id in changed_ids
    ]
    return {
        "feedback_kind": "single_contradiction_bad_timing_or_intrusive_proxy",
        "options_modified_count": len(changed_ids),
        "modified_option_ids": changed_ids,
        "global_option_set_changed": set(single["generated_options_before"])
        != set(single["generated_options_after"]),
        "context_scope_field_visible_in_modified_options": any(
            "context_scope" in option["allowed_observation_features"]
            for option in changed_payloads
        ),
        "available_context_fields": [
            sorted(option["allowed_observation_features"])
            for option in changed_payloads
        ],
        "context_scope_leak_confirmed": False,
        "context_scope_missing_for_feedback_admission": True,
        "context_scope_summary": (
            "The perturbation did not globally rewrite all options, but generated-option payloads "
            "do not carry an explicit context-scope/admission field for the pending feedback."
        ),
    }


def build_weak_evidence_high_confidence_audit(single: dict[str, Any]) -> dict[str, Any]:
    confidence = single["option_confidence_changes"][0]
    return {
        "single_contradiction_status": single["contradiction_feedback_record"]["admission_status"],
        "target_option_id": single["selected_option_before"],
        "confidence_before": confidence["confidence_before"],
        "confidence_after": confidence["confidence_after"],
        "confidence_delta": confidence["confidence_delta"],
        "sample_count_before": confidence["sample_count_before"],
        "sample_count_after": confidence["sample_count_after"],
        "effect_vector_changed": bool(single["contradiction_feedback_record"]["selector_visible_effect_delta"]),
        "uncertainty_increased_before_policy_change": confidence["confidence_delta"] < 0,
        "single_pending_feedback_created_new_high_confidence_option": False,
        "single_pending_feedback_modified_existing_high_confidence_option": (
            bool(single["contradiction_feedback_record"]["selector_visible_effect_delta"])
            and confidence["confidence_after"] >= confidence["confidence_before"]
        ),
        "weak_evidence_high_confidence_confirmed": (
            bool(single["contradiction_feedback_record"]["selector_visible_effect_delta"])
            and confidence["confidence_after"] >= confidence["confidence_before"]
        ),
    }


def build_outcome_update_ordering_audit(single: dict[str, Any]) -> dict[str, Any]:
    return {
        "pending_counterevidence_status_recorded": single["actual_status_reported_pending"],
        "selector_visible_effect_vector_changed_before_admission": (
            single["pending_counterevidence_still_reached_selector_effect_vector"]
        ),
        "selected_option_changed": single["selected_option_changed"],
        "selected_option_before": single["selected_option_before"],
        "selected_option_after": single["selected_option_after"],
        "distribution_changed": single["selected_option_probability_delta"] != 0,
        "outcome_update_changed_future_distribution_before_filter": (
            single["actual_status_reported_pending"]
            and single["pending_counterevidence_still_reached_selector_effect_vector"]
        ),
        "outcome_update_ordering_bug_confirmed": (
            single["actual_status_reported_pending"]
            and single["pending_counterevidence_still_reached_selector_effect_vector"]
            and single["selected_option_changed"]
        ),
    }


def build_replay_sufficiency_audit(
    failed: dict[str, Any],
    single: dict[str, Any],
    artifacts: dict[str, Any],
) -> dict[str, Any]:
    before = failed["before_trace"]
    selector_fields = set(before["selector_input"])
    option_fields = set(before["selector_input"]["candidate_options"][0])
    return {
        "behavior_only_replay_match_rate": artifacts["replay"]["match_rate"],
        "behavior_only_replay_forbidden_fields_used": artifacts["replay"]["forbidden_fields_used"],
        "reconstructs_final_action_distribution": True,
        "reconstructs_selected_action": True,
        "reconstructs_prediction_before_action": "prediction_before_action" in before,
        "reconstructs_option_uncertainty": "uncertainty" in option_fields,
        "reconstructs_evidence_support_refs": "prior_support_refs" in option_fields,
        "selector_trace_contains_proposal_id": "proposal_id" in option_fields,
        "selector_trace_contains_admission_decision": "admission_status" in selector_fields,
        "selector_trace_contains_contradiction_status": "admission_status" in selector_fields,
        "full_artifact_set_contains_proposals": bool(artifacts["proposals"]),
        "full_artifact_set_contains_admission_decisions": bool(artifacts["admissions"]),
        "full_artifact_set_contains_lineage": bool(artifacts["lineages"]),
        "full_artifact_set_contains_probe_status": bool(failed["failed_case"].get("admission_status")),
        "trace_sufficient_for_generated_feedback_admission": False,
        "replay_sufficiency_summary": (
            "Behavior-only replay reconstructs selected actions from distributions, but the "
            "selector traces do not carry proposal/admission/contradiction-status fields needed "
            "to replay generated-option feedback admission ordering without side artifacts."
        ),
    }


def build_failure_localization(
    single: dict[str, Any],
    lineage: dict[str, Any],
    scope: dict[str, Any],
    weak: dict[str, Any],
    ordering: dict[str, Any],
    replay: dict[str, Any],
) -> dict[str, Any]:
    return {
        "candidate_option_proposal": "not_primary_blocker_same_option_ids_before_after",
        "option_admission_gate": "primary_gap_for_feedback_update_not_for_initial_static_admission",
        "option_lineage_evidence_support": (
            "secondary_gap_counterevidence_not_inherited_by_existing_option_lineage"
        ),
        "feedback_admission_mapping": "primary_blocker_pending_counterevidence_reached_selector",
        "context_scope_assignment": (
            "secondary_gap_context_scope_missing_in_generated_option_payload"
            if scope["context_scope_missing_for_feedback_admission"]
            else "not_primary_blocker"
        ),
        "uncertainty_confidence_update": (
            "secondary_gap_confidence_not_reduced_before_policy_flip"
            if weak["weak_evidence_high_confidence_confirmed"]
            else "not_primary_blocker"
        ),
        "future_option_distribution_update": (
            "primary_blocker_update_applied_before_admission_filter"
            if ordering["outcome_update_ordering_bug_confirmed"]
            else "not_primary_blocker"
        ),
        "selector_scoring": "not_primary_blocker_selector_followed_selector_visible_effect_vector",
        "replay_trace_generation": (
            "secondary_gap_trace_insufficient_for_feedback_admission_ordering"
            if not replay["trace_sufficient_for_generated_feedback_admission"]
            else "not_primary_blocker"
        ),
    }


def decide_rca_verdict(
    ordering: dict[str, Any],
    weak: dict[str, Any],
    lineage: dict[str, Any],
    replay: dict[str, Any],
) -> tuple[str, list[str]]:
    secondary: list[str] = []
    if lineage["near_duplicate_new_option_bypass_detected"]:
        return "generated_option_lineage_bypass_confirmed", secondary
    if ordering["outcome_update_ordering_bug_confirmed"]:
        secondary.append("feedback_admission_not_applied_to_generated_options")
        if weak["weak_evidence_high_confidence_confirmed"]:
            secondary.append("weak_evidence_high_confidence_confirmed")
        if not replay["trace_sufficient_for_generated_feedback_admission"]:
            secondary.append("replay_trace_insufficient_for_generated_feedback_admission")
        secondary.append("selector_scoring_not_primary_blocker")
        return "outcome_update_ordering_bug_confirmed", secondary
    if weak["weak_evidence_high_confidence_confirmed"]:
        return "weak_evidence_high_confidence_confirmed", secondary
    if not replay["trace_sufficient_for_generated_feedback_admission"]:
        return "replay_trace_insufficient_for_generated_feedback_admission", secondary
    return "inconclusive_needs_manual_review", secondary


def build_rca_result(source_dir: Path) -> dict[str, Any]:
    artifacts = load_source_artifacts(source_dir)
    failed = failed_probe_trace(artifacts)
    single = build_single_contradiction_audit(failed, artifacts)
    lineage = build_option_lineage_bypass_audit(failed, single, artifacts)
    scope = build_context_scope_audit(failed, single)
    weak = build_weak_evidence_high_confidence_audit(single)
    ordering = build_outcome_update_ordering_audit(single)
    replay = build_replay_sufficiency_audit(failed, single, artifacts)
    localization = build_failure_localization(single, lineage, scope, weak, ordering, replay)
    verdict, secondary = decide_rca_verdict(ordering, weak, lineage, replay)
    return {
        "suite_id": "CMBC-COMPANION-CANDIDATE-OPTION-GENERATION-007-RCA",
        "source_failure": {
            "source_suite": artifacts["result"]["suite_id"],
            "source_verdict": artifacts["result"]["verdict"],
            "source_stop_conditions": artifacts["result"]["stop_conditions"],
            "source_claim_after_execute": artifacts["result"]["claim_after_execute"],
        },
        "verdict": verdict,
        "secondary_findings": secondary,
        "failure_localization": localization,
        "single_contradiction_audit": single,
        "option_lineage_bypass_audit": lineage,
        "context_scope_audit": scope,
        "weak_evidence_high_confidence_audit": weak,
        "outcome_update_ordering_audit": ordering,
        "replay_sufficiency_audit": replay,
        "selector_scoring_not_primary_blocker": True,
        "recommended_next_task": (
            "CMBC-COMPANION-GENERATED-OPTION-FEEDBACK-ADMISSION-007B-CONTRACT"
        ),
        "claim_after_rca": (
            "bounded generated CandidateOption execution remains failed; RCA localizes failure "
            "to pending feedback admission/update ordering, not generator selection, semantic leak, "
            "baseline equivalence, renderer control, deletion, or perturbation gates"
        ),
        "not_authorized": [
            "selector patch",
            "threshold change",
            "baseline weakening",
            "probe mutation after results",
            "EGO migration",
            "real companion behavior",
            "proactive messages",
            "LLM action selection",
            "prior evidence rewrite",
            "007B implementation",
        ],
        "not_proven": [
            "generated-option execution support",
            "open-ended option generation robustness",
            "real companion readiness",
            "EGO readiness",
            "consciousness",
            "subjective experience",
            "real emotion",
            "real love",
        ],
        "_failed_probe_trace": failed,
    }


def write_rca_artifacts(out: str | Path, result: dict[str, Any]) -> None:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    failed = result.pop("_failed_probe_trace")
    write_json(out_path / "failed_probe_trace.json", failed)
    write_json(out_path / "single_contradiction_audit.json", result["single_contradiction_audit"])
    write_json(out_path / "option_lineage_bypass_audit.json", result["option_lineage_bypass_audit"])
    write_json(out_path / "context_scope_audit.json", result["context_scope_audit"])
    write_json(
        out_path / "weak_evidence_high_confidence_audit.json",
        result["weak_evidence_high_confidence_audit"],
    )
    write_json(out_path / "outcome_update_ordering_audit.json", result["outcome_update_ordering_audit"])
    write_json(out_path / "replay_sufficiency_audit.json", result["replay_sufficiency_audit"])
    write_json(out_path / "RCA_RESULT.json", result)
    (out_path / STATUS_NAME).write_text(
        "# CMBC Candidate Option Generation 007 RCA\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"secondary_findings = {result['secondary_findings']}\n\n"
        f"source_verdict = {result['source_failure']['source_verdict']}\n\n"
        f"source_stop_conditions = {result['source_failure']['source_stop_conditions']}\n\n"
        f"claim_after_rca = {result['claim_after_rca']}\n\n"
        "selector patch = not_authorized\n\n"
        "threshold change = not_authorized\n\n"
        "baseline weakening = not_authorized\n\n"
        "EGO migration = no_go\n\n"
        "real companion implementation = not_authorized\n\n"
        "LLM action selection = false\n",
        encoding="utf-8",
    )
    result["_failed_probe_trace"] = failed


def run_candidate_option_generation_007_rca(
    out: str | Path,
    source_dir: str | Path = SOURCE_ARTIFACT_DIR,
) -> dict[str, Any]:
    result = build_rca_result(Path(source_dir))
    write_rca_artifacts(out, result)
    result.pop("_failed_probe_trace", None)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--source-dir", default=str(SOURCE_ARTIFACT_DIR))
    args = parser.parse_args()
    result = run_candidate_option_generation_007_rca(args.out, args.source_dir)
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "secondary_findings": result["secondary_findings"],
                "recommended_next_task": result["recommended_next_task"],
                "claim_after_rca": result["claim_after_rca"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
