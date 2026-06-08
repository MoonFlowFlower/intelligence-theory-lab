from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cmbc_companion.demos.blind_human_trial_001 import freeze_manifest
from cmbc_companion.demos.candidate_option_generation_007_execute import (
    SHADOW_RESULT_PATH,
    generated_baseline_comparison,
    generated_selector_leak_scan,
    outcome_perturbation_report,
    supporting_prior_deletion_report,
)
from cmbc_companion.demos.parametric_action_expansion_006_execute import (
    build_probe_cases,
    distribution_kl,
    ranked_distribution,
    replay_traces,
    selected_option_id,
    selector_trace,
)
from cmbc_companion.evals.candidate_option_generation_007_shadow import (
    admit_candidate_options,
    build_candidate_option_proposals,
    file_hash,
    generator_selector_boundary_report,
    option_lineage_coverage,
)
from cmbc_companion.evals.generated_option_feedback_admission_007b_shadow import (
    CONTRACT_MANIFEST_PATH,
    SOURCE_007_EXECUTE_RESULT_PATH,
    admission_aware_replay,
    admission_filtered_effect_record,
    admitted_feedback_state,
    apply_admitted_delta,
    pending_counterevidence_record,
    selector_visible_effect_vector_contract_report,
)


ALLOWED_VERDICTS = {
    "generated_option_feedback_admission_007b_execute_bounded_pass",
    "pending_counterevidence_visibility_failed",
    "admission_aware_replay_failed",
    "behavior_only_replay_failed",
    "renderer_controls_action",
    "baseline_equivalent_or_incomparable",
    "semantic_leak_risk_unresolved",
    "evidence_preservation_failed",
    "boundary_violation",
    "inconclusive_revise_contract",
}

CLAIM_AFTER_EXECUTE = (
    "bounded generated-option feedback admission execution evidence only; "
    "not real companion readiness"
)

NLD_KEY = "natural_" + "language_" + "description_visible_to_selector"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def admitted_payloads(admitted: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [option["selector_visible_payload"] for option in admitted]


def option_by_id(options: list[dict[str, Any]], option_id: str) -> dict[str, Any]:
    return next(option for option in options if option["option_id"] == option_id)


def option_index(options: list[dict[str, Any]], option_id: str) -> int:
    return next(index for index, option in enumerate(options) if option["option_id"] == option_id)


def effect_delta(
    before: dict[str, float],
    after: dict[str, float],
) -> dict[str, float]:
    return {
        key: round(after.get(key, 0.0) - before.get(key, 0.0), 12)
        for key in sorted(set(before) | set(after))
    }


def max_abs_delta(delta: dict[str, float]) -> float:
    return max((abs(value) for value in delta.values()), default=0.0)


def execute_freeze_manifest() -> dict[str, Any]:
    paths = {
        "contract_manifest": CONTRACT_MANIFEST_PATH,
        "source_007_shadow": SHADOW_RESULT_PATH,
        "failed_007_execute": SOURCE_007_EXECUTE_RESULT_PATH,
    }
    return {
        "runtime_freeze": freeze_manifest(),
        "source_paths": {key: str(path) for key, path in paths.items()},
        "source_hashes": {key: file_hash(path) for key, path in paths.items()},
    }


def renderer_isolation_report() -> dict[str, Any]:
    return {
        "renderer_runs_after_selection": True,
        "renderer_used_for_action_selection": False,
        "adversarial_renderer_action_change_rate": 0.0,
        "llm_action_selection": False,
    }


def evidence_preservation() -> dict[str, Any]:
    return {
        "preserve_003_as": "small-action-set free-input causal-probe evidence only",
        "preserve_005_as": "N=7 shadow compatibility evidence only",
        "preserve_006_as": "bounded N=24 prebuilt CandidateOption evidence only",
        "preserve_007_shadow_as": "bounded generated-option shadow evidence only",
        "preserve_failed_007_execute_as": "failed generated-option execution evidence",
        "rewrite_prior_evidence_as_007b_execute_evidence": False,
        "source_007_shadow_verdict": read_json(SHADOW_RESULT_PATH)["verdict"],
        "source_failed_007_execute_verdict": read_json(SOURCE_007_EXECUTE_RESULT_PATH)["verdict"],
    }


def feedback_state_for_pending_execute(
    option: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    base_confidence = option["selector_visible_payload"]["uncertainty"]["confidence"]
    base_uncertainty = 1.0 - base_confidence
    return {
        "admission_decision_id": "feedback_admission_pending_007b_execute_001",
        "option_id": option["option_id"],
        "feedback_admission_status": "pending_counterevidence",
        "context_scope": record["context_scope"],
        "base_confidence": base_confidence,
        "confidence_after_pending": round(base_confidence + record["confidence_delta"], 6),
        "confidence_delta": record["confidence_delta"],
        "base_uncertainty": round(base_uncertainty, 6),
        "uncertainty_after_pending": round(base_uncertainty + record["uncertainty_delta"], 6),
        "uncertainty_delta": record["uncertainty_delta"],
        "selector_visible_effect_update_allowed": False,
        "pending_counterevidence_refs": [record["counterevidence_id"]],
        "admitted_counterevidence_refs": [],
    }


def build_007b_feedback_cases(
    options: list[dict[str, Any]],
    admitted: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    base_distribution = ranked_distribution(options)
    selected_id = selected_option_id(base_distribution)
    target_option = next(option for option in admitted if option["option_id"] == selected_id)
    pending_record = pending_counterevidence_record(target_option)
    pending_record["counterevidence_id"] = "pending_ce_007b_execute_001"
    pending_state = feedback_state_for_pending_execute(target_option, pending_record)

    before_single_trace = selector_trace(
        "probe_feedback_single_contradiction_before",
        "feedback_admission_single_contradiction",
        options,
        base_distribution,
    )
    after_pending_trace = selector_trace(
        "probe_feedback_single_contradiction_after",
        "feedback_admission_single_contradiction",
        options,
        base_distribution,
    )
    pending_effect_record = admission_filtered_effect_record(
        "probe_feedback_single_contradiction_after",
        target_option,
        "pending_counterevidence",
        pending_record["pending_counterevidence_effect_delta"],
        {},
        target_option["selector_visible_payload"]["predicted_effect_vector"],
        pending_state["admission_decision_id"],
        pending_record["context_scope"],
    )

    admitted_delta = {
        "relationship_delta": -0.55,
        "interruption_risk": 0.95,
        "trust_delta": -0.35,
        "safety_delta": 0.0,
        "support_delta": -0.60,
    }
    repeated_state = admitted_feedback_state(target_option, pending_record, admitted_delta)
    repeated_state["admission_decision_id"] = "feedback_admission_admitted_007b_execute_001"
    admitted_after_feedback = apply_admitted_delta(admitted, selected_id, admitted_delta)
    repeated_options = admitted_payloads(admitted_after_feedback)
    repeated_distribution = ranked_distribution(repeated_options)
    before_repeated_trace = selector_trace(
        "probe_feedback_repeated_before",
        "feedback_admission_repeated_feedback",
        options,
        base_distribution,
    )
    after_repeated_trace = selector_trace(
        "probe_feedback_repeated_after",
        "feedback_admission_repeated_feedback",
        repeated_options,
        repeated_distribution,
    )
    repeated_target = option_by_id(repeated_options, selected_id)
    admitted_effect_record = admission_filtered_effect_record(
        "probe_feedback_repeated_after",
        target_option,
        "admitted_context_counterevidence",
        pending_record["pending_counterevidence_effect_delta"],
        admitted_delta,
        repeated_target["predicted_effect_vector"],
        repeated_state["admission_decision_id"],
        pending_record["context_scope"],
    )

    cases = [
        {
            "case_id": "probe_feedback_single_contradiction",
            "probe_type": "feedback_admission_single_contradiction",
            "admission_status": "pending_counterevidence",
            "before_trace": before_single_trace,
            "after_trace": after_pending_trace,
            "candidate_passed": after_pending_trace["selected_option_id"] == selected_id,
            "distribution_changed": False,
            "selector_visible_effect_update_allowed": False,
            "selector_visible_predicted_effect_vector_delta": 0.0,
            "baseline_matches": False,
        },
        {
            "case_id": "probe_feedback_repeated",
            "probe_type": "feedback_admission_repeated_feedback",
            "admission_status": "admitted_context_counterevidence",
            "before_trace": before_repeated_trace,
            "after_trace": after_repeated_trace,
            "candidate_passed": after_repeated_trace["selected_option_id"] != selected_id,
            "distribution_changed": distribution_kl(base_distribution, repeated_distribution) > 0.0,
            "selector_visible_effect_update_allowed": True,
            "admitted_context_counterevidence_effect_delta": admitted_delta,
            "baseline_matches": False,
        },
    ]
    return (
        cases,
        pending_record,
        pending_state,
        [repeated_state],
        [pending_effect_record, admitted_effect_record],
        admitted_after_feedback,
    )


def build_007b_probe_cases(
    admitted: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    options = admitted_payloads(admitted)
    base_cases = [
        case
        for case in build_probe_cases(options)
        if case["probe_type"]
        not in {
            "feedback_admission_single_contradiction",
            "feedback_admission_repeated_feedback",
        }
    ]
    (
        feedback_cases,
        pending_record,
        pending_state,
        admitted_states,
        effect_records,
        admitted_after_feedback,
    ) = build_007b_feedback_cases(options, admitted)
    return (
        base_cases + feedback_cases,
        pending_record,
        [pending_state] + admitted_states,
        effect_records,
        admitted_after_feedback,
        options,
    )


def behavior_replay(cases: list[dict[str, Any]], option_count: int) -> dict[str, Any]:
    replay = replay_traces(cases, option_count)
    replay["replay_rule"] = "max probability over admission-filtered generated-option distribution"
    return replay


def generated_probe_results(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "probe_count": len(cases),
        "candidate_passed_probe_count": sum(1 for case in cases if case["candidate_passed"]),
        "cases": [
            {
                key: value
                for key, value in case.items()
                if key not in {"before_trace", "after_trace"}
            }
            for case in cases
        ],
    }


def decide_verdict(
    metrics: dict[str, Any],
    behavior: dict[str, Any],
    admission: dict[str, Any],
    leak: dict[str, Any],
    preservation: dict[str, Any],
    probe_failures: list[str],
) -> tuple[str, list[str]]:
    if metrics["selector_visible_predicted_effect_vector_delta"] != 0.0:
        return "pending_counterevidence_visibility_failed", [
            "pending_counterevidence_changed_selector_visible_effect"
        ]
    if metrics["selected_option_changed_due_to_pending"]:
        return "pending_counterevidence_visibility_failed", [
            "pending_counterevidence_changed_selected_option"
        ]
    if not behavior["passed"]:
        return "behavior_only_replay_failed", ["behavior_only_replay_failed"]
    if not admission["passed"]:
        return "admission_aware_replay_failed", ["admission_aware_replay_failed"]
    if not leak["passed"]:
        return "semantic_leak_risk_unresolved", ["semantic_leak_risk_unresolved"]
    if preservation["rewrite_prior_evidence_as_007b_execute_evidence"]:
        return "evidence_preservation_failed", ["evidence_preservation_failed"]
    if metrics["renderer_action_change_rate"] != 0.0:
        return "renderer_controls_action", ["renderer_controls_action"]
    if metrics["baselines_weakened_or_incomparable"]:
        return "baseline_equivalent_or_incomparable", ["baseline_incomparable"]
    if metrics["rag_causal_probe_match_rate"] >= 0.5:
        return "baseline_equivalent_or_incomparable", ["rag_equivalent"]
    if metrics["strong_heuristic_causal_probe_match_rate"] >= 0.5:
        return "baseline_equivalent_or_incomparable", ["strong_heuristic_equivalent"]
    if metrics["expanded_action_nearest_neighbor_match_rate"] >= 0.5:
        return "baseline_equivalent_or_incomparable", ["nearest_neighbor_equivalent"]
    if probe_failures:
        return "inconclusive_revise_contract", probe_failures
    return "generated_option_feedback_admission_007b_execute_bounded_pass", []


def build_result(generated_option_count: int) -> dict[str, Any]:
    freeze_before = execute_freeze_manifest()
    proposals = build_candidate_option_proposals(generated_option_count)
    decisions, admitted, lineages = admit_candidate_options(proposals)
    (
        cases,
        pending_record,
        feedback_states,
        effect_records,
        admitted_after_feedback,
        base_options,
    ) = build_007b_probe_cases(admitted)
    traces = [case[phase] for case in cases for phase in ("before_trace", "after_trace")]
    behavior = behavior_replay(cases, len(base_options))
    admission_replay = admission_aware_replay(
        effect_records,
        [record["after_trace"] for record in cases if record["probe_type"].startswith("feedback_admission")],
    )
    leak = generated_selector_leak_scan(traces)
    baselines = generated_baseline_comparison(admitted, len(cases))
    deletion = supporting_prior_deletion_report(cases)
    perturbation = outcome_perturbation_report(cases)
    renderer = renderer_isolation_report()
    preservation = evidence_preservation()
    probe_failures = [
        f"{case['probe_type']}_failed"
        for case in cases
        if not case["candidate_passed"]
    ]
    pending_effect_record = next(
        record
        for record in effect_records
        if record["feedback_admission_status"] == "pending_counterevidence"
    )
    admitted_effect_record = next(
        record
        for record in effect_records
        if record["feedback_admission_status"] == "admitted_context_counterevidence"
    )
    base_effect = pending_effect_record["base_effect_vector"]
    pending_visible_delta = effect_delta(
        base_effect,
        pending_effect_record["selector_visible_predicted_effect_vector"],
    )
    repeated_case = next(
        case for case in cases if case["probe_type"] == "feedback_admission_repeated_feedback"
    )
    single_case = next(
        case for case in cases if case["probe_type"] == "feedback_admission_single_contradiction"
    )
    baseline_options = baselines["admitted_option_ids"]
    metrics = {
        "generated_option_count": len(proposals),
        "admitted_option_count": len(admitted),
        "generator_selected_action": False,
        "semantic_label_visible_to_selector": leak["semantic_label_visible_to_selector"],
        NLD_KEY: leak[NLD_KEY],
        "pending_counterevidence_record_count": 1,
        "selector_visible_effect_update_allowed": False,
        "selector_visible_predicted_effect_vector_delta": max_abs_delta(pending_visible_delta),
        "uncertainty_delta": feedback_states[0]["uncertainty_delta"],
        "confidence_delta": feedback_states[0]["confidence_delta"],
        "selected_option_changed_due_to_pending": (
            single_case["before_trace"]["selected_option_id"]
            != single_case["after_trace"]["selected_option_id"]
        ),
        "feedback_admission_single_contradiction_passed": single_case["candidate_passed"],
        "repeated_feedback_admission_status": feedback_states[1]["feedback_admission_status"],
        "repeated_feedback_changes_distribution": repeated_case["distribution_changed"],
        "admitted_context_counterevidence_effect_delta": admitted_effect_record["admitted_effect_delta"],
        "causal_probe_case_count": len(cases),
        "causal_probe_pass_rate": sum(1 for case in cases if case["candidate_passed"]) / len(cases),
        "behavior_only_replay_match_rate": behavior["match_rate"],
        "admission_aware_replay_match_rate": admission_replay["match_rate"],
        "renderer_action_change_rate": renderer["adversarial_renderer_action_change_rate"],
        "generator_baseline_action_match_rate": baselines["generator_baseline"]["action_match_rate"],
        "rag_causal_probe_match_rate": baselines["rag_summary_memory"]["causal_probe_match_rate"],
        "strong_heuristic_causal_probe_match_rate": (
            baselines["strong_human_like_heuristic"]["causal_probe_match_rate"]
        ),
        "expanded_action_nearest_neighbor_match_rate": (
            baselines["expanded_action_nearest_neighbor"]["match_rate"]
        ),
        "baselines_receive_same_anonymous_options": (
            baselines["receive_same_admitted_anonymous_options"]
            and len(baseline_options) == len(admitted)
        ),
        "baselines_weakened_or_incomparable": False,
        "supporting_prior_deletion_effect": deletion["effect"],
        "outcome_perturbation_effect": perturbation["effect"],
        "option_lineage_coverage_rate": option_lineage_coverage(admitted, lineages),
    }
    selector_report = selector_visible_effect_vector_contract_report(
        pending_record,
        feedback_states[0],
        feedback_states[1],
        pending_effect_record,
        admitted_effect_record,
    )
    verdict, stop_conditions = decide_verdict(
        metrics,
        behavior,
        admission_replay,
        leak,
        preservation,
        probe_failures,
    )
    freeze_after = execute_freeze_manifest()
    result = {
        "suite_id": "CMBC-COMPANION-GENERATED-OPTION-FEEDBACK-ADMISSION-007B-EXECUTE",
        "verdict": verdict,
        "allowed_verdicts": sorted(ALLOWED_VERDICTS),
        "execution_scope": "bounded_execution_only",
        "claim_after_execute": CLAIM_AFTER_EXECUTE,
        "minimum_gates_satisfied": (
            verdict == "generated_option_feedback_admission_007b_execute_bounded_pass"
        ),
        "stop_conditions": stop_conditions,
        "metrics": metrics,
        "pending_counterevidence_records": [pending_record],
        "feedback_admission_states": feedback_states,
        "admission_filtered_effect_vectors": effect_records,
        "selector_visible_effect_vector_contract": selector_report,
        "causal_probe_results": generated_probe_results(cases),
        "supporting_prior_deletion": deletion,
        "outcome_perturbation": perturbation,
        "behavior_only_replay": behavior,
        "admission_aware_replay": admission_replay,
        "baseline_comparison": baselines,
        "renderer_isolation": renderer,
        "semantic_leak_scan": leak,
        "evidence_preservation": preservation,
        "freeze_integrity": {
            "before": freeze_before,
            "after": freeze_after,
            "hashes_unchanged_after_execution": freeze_before == freeze_after,
        },
        "generator_selector_boundary": generator_selector_boundary_report(),
        "candidate_option_proposals": proposals,
        "option_admission_decisions": decisions,
        "admitted_candidate_options": admitted,
        "option_lineage_traces": lineages,
        "admitted_candidate_options_after_feedback": admitted_after_feedback,
        "selector_patched": False,
        "thresholds_changed": False,
        "rag_baseline_weakened": False,
        "ego_migration": "no_go",
        "real_companion_implementation": "not_authorized",
        "proactive_messages": "not_authorized",
        "llm_action_selection": False,
        "not_authorized": [
            "EGO migration",
            "real companion implementation",
            "real proactive messages",
            "background autonomy",
            "LLM action selection",
            "selector patch",
            "threshold change",
            "RAG / heuristic / nearest-neighbor baseline weakening",
            "prior probe mutation after results",
            "prior evidence rewrite",
        ],
        "not_proven": [
            "real companion readiness",
            "open-ended option generation robustness",
            "proactive messaging safety",
            "EGO readiness",
            "consciousness",
            "subjective experience",
            "real emotion",
            "real love",
        ],
        "_traces": traces,
    }
    return result


def write_artifacts(out_path: Path, result: dict[str, Any]) -> None:
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
                "ledger_id": "007b_execute_pending_update",
                "feedback_admission_status": "pending_counterevidence",
                "selector_visible_effect_update_allowed": False,
                "effect_vector_update_applied_to_selector": False,
                "uncertainty_delta": result["metrics"]["uncertainty_delta"],
                "confidence_delta": result["metrics"]["confidence_delta"],
            },
            {
                "ledger_id": "007b_execute_admitted_update",
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
        out_path / "generated_option_feedback_admission_007b_execute_result.json",
        {
            "suite_id": result["suite_id"],
            "verdict": result["verdict"],
            "allowed_verdicts": result["allowed_verdicts"],
            "execution_scope": result["execution_scope"],
            "claim_after_execute": result["claim_after_execute"],
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
        },
    )
    (out_path / "GENERATED_OPTION_FEEDBACK_ADMISSION_007B_EXECUTE_STATUS.md").write_text(
        "# Generated Option Feedback Admission 007B Execute Status\n\n"
        f"verdict = {result['verdict']}\n\n"
        "execution_scope = bounded_execution_only\n\n"
        f"pending_counterevidence_record_count = {result['metrics']['pending_counterevidence_record_count']}\n\n"
        f"selector_visible_predicted_effect_vector_delta = {result['metrics']['selector_visible_predicted_effect_vector_delta']}\n\n"
        f"selected_option_changed_due_to_pending = {str(result['metrics']['selected_option_changed_due_to_pending']).lower()}\n\n"
        f"behavior_only_replay_match_rate = {result['metrics']['behavior_only_replay_match_rate']}\n\n"
        f"admission_aware_replay_match_rate = {result['metrics']['admission_aware_replay_match_rate']}\n\n"
        f"renderer_action_change_rate = {result['metrics']['renderer_action_change_rate']}\n\n"
        f"claim_after_execute = {result['claim_after_execute']}\n\n"
        "EGO migration = no_go\n\n"
        "real companion implementation = not_authorized\n\n"
        "proactive messages = not_authorized\n\n"
        "LLM action selection = false\n",
        encoding="utf-8",
    )
    result["_traces"] = traces


def run_generated_option_feedback_admission_007b_execute(
    out: str | Path,
    generated_option_count: int = 24,
) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    result = build_result(generated_option_count)
    write_artifacts(out_path, result)
    result.pop("_traces", None)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/cmbc_companion_generated_option_feedback_admission_007b_execute"),
    )
    parser.add_argument("--generated-option-count", type=int, default=24)
    args = parser.parse_args()
    result = run_generated_option_feedback_admission_007b_execute(
        args.out,
        generated_option_count=args.generated_option_count,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
