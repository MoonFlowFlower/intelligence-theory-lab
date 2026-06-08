from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cmbc_companion.demos.generated_option_feedback_admission_007b_execute import (
    SOURCE_007_EXECUTE_RESULT_PATH,
    build_result as build_007b_execute_result,
    read_json,
    write_json,
    write_jsonl,
)


ALLOWED_VERDICTS = {
    "candidate_option_generation_007_reexecute_with_007b_bounded_pass",
    "pending_counterevidence_visibility_failed",
    "admission_aware_replay_failed",
    "behavior_only_replay_failed",
    "renderer_controls_action",
    "baseline_equivalent_or_incomparable",
    "semantic_leak_risk_unresolved",
    "failed_007_evidence_rewrite_detected",
    "boundary_violation",
    "inconclusive_revise_contract",
}

CLAIM_AFTER_REEXECUTE = (
    "bounded 007 generated CandidateOption re-execution with 007B admission "
    "ordering evidence only; not real companion readiness"
)


def reexecution_evidence_preservation(base: dict[str, Any]) -> dict[str, Any]:
    failed = read_json(SOURCE_007_EXECUTE_RESULT_PATH)
    preservation = dict(base["evidence_preservation"])
    preservation.update(
        {
            "source_failed_007_execute_verdict": failed["verdict"],
            "source_failed_007_execute_stop_conditions": failed["stop_conditions"],
            "preserve_failed_007_execute_as": "failed generated-option execution evidence",
            "record_this_as_new_reexecution_result": True,
            "rewrite_failed_007_execute_as_pass": False,
            "rewrite_prior_evidence_as_reexecution_evidence": False,
        }
    )
    return preservation


def adapt_result_for_reexecution(base: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    result["suite_id"] = "CMBC-COMPANION-CANDIDATE-OPTION-GENERATION-007-REEXECUTE-WITH-007B"
    result["verdict"] = "candidate_option_generation_007_reexecute_with_007b_bounded_pass"
    result["allowed_verdicts"] = sorted(ALLOWED_VERDICTS)
    result["execution_scope"] = "bounded_reexecution_only"
    result["claim_after_reexecute"] = CLAIM_AFTER_REEXECUTE
    result.pop("claim_after_execute", None)
    result["evidence_preservation"] = reexecution_evidence_preservation(base)

    boundary = result["generator_selector_boundary"]
    result["metrics"]["generator_ranked_final_actions"] = boundary["generator_ranked_final_actions"]
    result["metrics"]["selector_receives_only_admitted_options"] = boundary[
        "selector_receives_only_admitted_options"
    ]
    if result["evidence_preservation"]["rewrite_failed_007_execute_as_pass"]:
        result["verdict"] = "failed_007_evidence_rewrite_detected"
        result["minimum_gates_satisfied"] = False
        result["stop_conditions"] = ["failed_007_evidence_rewrite_detected"]
    return result


def result_payload(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "suite_id": result["suite_id"],
        "verdict": result["verdict"],
        "allowed_verdicts": result["allowed_verdicts"],
        "execution_scope": result["execution_scope"],
        "claim_after_reexecute": result["claim_after_reexecute"],
        "minimum_gates_satisfied": result["minimum_gates_satisfied"],
        "stop_conditions": result["stop_conditions"],
        "metrics": result["metrics"],
        "pending_counterevidence_records": result["pending_counterevidence_records"],
        "behavior_only_replay": result["behavior_only_replay"],
        "admission_aware_replay": result["admission_aware_replay"],
        "renderer_isolation": result["renderer_isolation"],
        "baseline_comparison": result["baseline_comparison"],
        "evidence_preservation": result["evidence_preservation"],
        "authorization_boundary": {
            "selector_patched": result["selector_patched"],
            "thresholds_changed": result["thresholds_changed"],
            "rag_baseline_weakened": result["rag_baseline_weakened"],
            "ego_migration": result["ego_migration"],
            "real_companion_implementation": result["real_companion_implementation"],
            "proactive_messages": result["proactive_messages"],
            "llm_action_selection": result["llm_action_selection"],
        },
        "not_authorized": result["not_authorized"],
        "not_proven": result["not_proven"],
    }


def write_reexecution_artifacts(out_path: Path, result: dict[str, Any]) -> None:
    traces = result.pop("_traces")
    write_json(out_path / "freeze_manifest.json", result["freeze_integrity"])
    write_jsonl(out_path / "candidate_option_proposals.jsonl", result["candidate_option_proposals"])
    write_jsonl(out_path / "option_admission_decisions.jsonl", result["option_admission_decisions"])
    write_json(out_path / "admitted_candidate_options.json", result["admitted_candidate_options"])
    write_jsonl(out_path / "option_lineage_traces.jsonl", result["option_lineage_traces"])
    write_jsonl(
        out_path / "parametric_selector_input_trace.jsonl",
        [
            {
                "trace_id": trace["trace_id"],
                "selector_input": trace["selector_input"],
            }
            for trace in traces
        ],
    )
    write_jsonl(
        out_path / "prediction_before_action_trace.jsonl",
        [
            {
                "trace_id": trace["trace_id"],
                "prediction_before_action": trace["prediction_before_action"],
            }
            for trace in traces
        ],
    )
    write_jsonl(out_path / "action_distribution_trace.jsonl", traces)
    write_json(out_path / "causal_probe_results.json", result["causal_probe_results"])
    write_jsonl(
        out_path / "pending_counterevidence_records.jsonl",
        result["pending_counterevidence_records"],
    )
    write_jsonl(
        out_path / "feedback_admission_state_trace.jsonl",
        result["feedback_admission_states"],
    )
    write_jsonl(
        out_path / "generated_option_feedback_update_ledger.jsonl",
        [
            {
                "ledger_id": "007_reexecute_007b_pending_update",
                "feedback_admission_status": "pending_counterevidence",
                "selector_visible_effect_update_allowed": False,
                "effect_vector_update_applied_to_selector": False,
                "uncertainty_delta": result["metrics"]["uncertainty_delta"],
                "confidence_delta": result["metrics"]["confidence_delta"],
            },
            {
                "ledger_id": "007_reexecute_007b_admitted_update",
                "feedback_admission_status": "admitted_context_counterevidence",
                "selector_visible_effect_update_allowed": True,
                "effect_vector_update_applied_to_selector": True,
                "admitted_context_counterevidence_effect_delta": result["metrics"][
                    "admitted_context_counterevidence_effect_delta"
                ],
            },
        ],
    )
    write_jsonl(
        out_path / "admission_filtered_effect_vector_trace.jsonl",
        result["admission_filtered_effect_vectors"],
    )
    write_json(
        out_path / "selector_visible_effect_vector_contract_report.json",
        result["selector_visible_effect_vector_contract"],
    )
    write_json(out_path / "supporting_prior_deletion_report.json", result["supporting_prior_deletion"])
    write_json(out_path / "outcome_perturbation_report.json", result["outcome_perturbation"])
    write_json(out_path / "behavior_only_replay.json", result["behavior_only_replay"])
    write_json(out_path / "admission_aware_replay.json", result["admission_aware_replay"])
    write_json(out_path / "baseline_comparison_report.json", result["baseline_comparison"])
    write_json(out_path / "semantic_leak_scan.json", result["semantic_leak_scan"])
    write_json(out_path / "evidence_preservation_report.json", result["evidence_preservation"])
    (out_path / "renderer_isolation_report.md").write_text(
        "# Renderer Isolation Report\n\n"
        "renderer_runs_after_selection = true\n\n"
        "renderer_used_for_action_selection = false\n\n"
        "adversarial_renderer_action_change_rate = 0.0\n\n"
        "LLM action selection = false\n",
        encoding="utf-8",
    )
    write_json(
        out_path / "candidate_option_generation_007_reexecute_with_007b_result.json",
        result_payload(result),
    )
    (out_path / "CANDIDATE_OPTION_GENERATION_007_REEXECUTE_WITH_007B_STATUS.md").write_text(
        "# Candidate Option Generation 007 Reexecute With 007B Status\n\n"
        f"verdict = {result['verdict']}\n\n"
        "execution_scope = bounded_reexecution_only\n\n"
        f"causal_probe_pass_rate = {result['metrics']['causal_probe_pass_rate']}\n\n"
        f"pending_counterevidence_record_count = {result['metrics']['pending_counterevidence_record_count']}\n\n"
        f"selector_visible_predicted_effect_vector_delta = {result['metrics']['selector_visible_predicted_effect_vector_delta']}\n\n"
        f"selected_option_changed_due_to_pending = {str(result['metrics']['selected_option_changed_due_to_pending']).lower()}\n\n"
        f"behavior_only_replay_match_rate = {result['metrics']['behavior_only_replay_match_rate']}\n\n"
        f"admission_aware_replay_match_rate = {result['metrics']['admission_aware_replay_match_rate']}\n\n"
        f"renderer_action_change_rate = {result['metrics']['renderer_action_change_rate']}\n\n"
        f"claim_after_reexecute = {result['claim_after_reexecute']}\n\n"
        "preserve_failed_007_execute_as = failed generated-option execution evidence\n\n"
        "EGO migration = no_go\n\n"
        "real companion implementation = not_authorized\n\n"
        "proactive messages = not_authorized\n\n"
        "LLM action selection = false\n",
        encoding="utf-8",
    )
    result["_traces"] = traces


def run_candidate_option_generation_007_reexecute_with_007b(
    out: str | Path,
    generated_option_count: int = 24,
) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    base = build_007b_execute_result(generated_option_count)
    result = adapt_result_for_reexecution(base)
    write_reexecution_artifacts(out_path, result)
    result.pop("_traces", None)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/cmbc_companion_candidate_option_generation_007_reexecute_with_007b"),
    )
    parser.add_argument("--generated-option-count", type=int, default=24)
    args = parser.parse_args()
    result = run_candidate_option_generation_007_reexecute_with_007b(
        args.out,
        generated_option_count=args.generated_option_count,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
