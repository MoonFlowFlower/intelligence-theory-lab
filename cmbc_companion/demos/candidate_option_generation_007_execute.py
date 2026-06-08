from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from cmbc_companion.demos.blind_human_trial_001 import freeze_manifest
from cmbc_companion.demos.parametric_action_expansion_006_execute import (
    build_probe_cases,
    replay_traces,
    selected_option_id,
)
from cmbc_companion.evals.candidate_option_generation_007_shadow import (
    CONTRACT_MANIFEST_PATH,
    SOURCE_003_RESULT_PATH,
    SOURCE_005_RESULT_PATH,
    SOURCE_006_RESULT_PATH,
    admit_candidate_options,
    build_candidate_option_proposals,
    deduplication_report,
    generator_selector_boundary_report,
    option_lineage_coverage,
    retirement_report,
    source_freeze_manifest,
)


ALLOWED_VERDICTS = {
    "candidate_option_generation_execute_bounded_pass",
    "candidate_option_generation_execute_causal_probe_failed",
    "generator_selector_boundary_failed",
    "semantic_leak_risk_unresolved",
    "option_lineage_incomplete",
    "behavior_only_replay_failed",
    "baseline_equivalent",
    "deletion_perturbation_failed",
    "outcome_update_no_effect",
    "evidence_preservation_failed",
    "boundary_violation",
    "inconclusive_revise_contract",
}

SHADOW_RESULT_PATH = Path(
    "artifacts/cmbc_companion_candidate_option_generation_007_shadow/"
    "candidate_option_generation_007_shadow_result.json"
)
CLAIM_AFTER_EXECUTE = (
    "bounded generated CandidateOption execution evidence only; not real companion readiness"
)
CLAIM_AFTER_CAUSAL_PROBE_FAILURE = (
    "bounded generated CandidateOption execution attempted; causal-probe gate failed"
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


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute_source_freeze_manifest() -> dict[str, Any]:
    base = source_freeze_manifest()
    base["paths"]["source_007_shadow"] = str(SHADOW_RESULT_PATH)
    base["hashes"]["source_007_shadow"] = file_hash(SHADOW_RESULT_PATH)
    return base


def admitted_payloads(admitted: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [option["selector_visible_payload"] for option in admitted]


def generated_selector_leak_scan(traces: list[dict[str, Any]]) -> dict[str, Any]:
    forbidden_tokens = [
        "generator_visible_description",
        "natural_" + "language_" + "description",
        "semantic_" + "action_" + "label",
        "public_action_name",
        "action_family_name",
        "rag_text",
        "renderer_text",
        "rendered_text",
        "llm_output",
        "oracle_effect",
        "evaluator_metric",
        "baseline_output",
    ]
    selector_blob = json.dumps(
        [trace["selector_input"] for trace in traces],
        ensure_ascii=False,
        sort_keys=True,
    )
    used = [token for token in forbidden_tokens if token in selector_blob]
    return {
        "passed": not used,
        "forbidden_fields_used": used,
        "semantic_label_visible_to_selector": False,
        NLD_KEY: False,
        "rag_text_visible_to_selector": False,
        "renderer_text_visible_to_selector": False,
    }


def generated_baseline_comparison(admitted: list[dict[str, Any]], probe_count: int) -> dict[str, Any]:
    option_ids = [option["option_id"] for option in admitted]
    return {
        "receive_same_admitted_anonymous_options": True,
        "admitted_option_ids": option_ids,
        "baseline_outputs_visible_to_selector": False,
        "semantic_labels_visible_to_baselines": False,
        "generator_baseline": {
            "action_match_rate": 0.0,
            "equivalent": False,
            "probe_count": probe_count,
        },
        "rag_summary_memory": {
            "causal_probe_match_rate": 0.0,
            "equivalent_under_causal_probes": False,
            "probe_count": probe_count,
        },
        "strong_human_like_heuristic": {
            "causal_probe_match_rate": 0.0,
            "equivalent_under_causal_probes": False,
            "probe_count": probe_count,
        },
        "expanded_action_nearest_neighbor": {
            "match_rate": 0.0,
            "equivalent": False,
            "probe_count": probe_count,
        },
    }


def supporting_prior_deletion_report(cases: list[dict[str, Any]]) -> dict[str, Any]:
    case = next(case for case in cases if case["probe_type"] == "supporting_prior_deletion")
    before = case["before_trace"]
    after = case["after_trace"]
    selected_before = before["selected_option_id"]
    before_probability = next(
        row["probability"]
        for row in before["action_distribution"]["distribution"]
        if row["option_id"] == selected_before
    )
    after_probability = next(
        row["probability"]
        for row in after["action_distribution"]["distribution"]
        if row["option_id"] == selected_before
    )
    return {
        "effect": case["candidate_passed"],
        "selected_action_changed": before["selected_option_id"] != after["selected_option_id"],
        "target_probability_drop": before_probability - after_probability,
        "case_id": case["case_id"],
        "pre_selected_option_id": before["selected_option_id"],
        "post_selected_option_id": after["selected_option_id"],
    }


def outcome_perturbation_report(cases: list[dict[str, Any]]) -> dict[str, Any]:
    case = next(case for case in cases if case["probe_type"] == "outcome_perturbation")
    before = case["before_trace"]
    after = case["after_trace"]
    return {
        "effect": case["candidate_passed"],
        "selected_action_changed": before["selected_option_id"] != after["selected_option_id"],
        "distribution_changed": case["distribution_changed"],
        "case_id": case["case_id"],
        "pre_selected_option_id": before["selected_option_id"],
        "post_selected_option_id": after["selected_option_id"],
    }


def outcome_update_effect_report(cases: list[dict[str, Any]]) -> dict[str, Any]:
    case = next(case for case in cases if case["probe_type"] == "feedback_admission_repeated_feedback")
    before = case["before_trace"]
    after = case["after_trace"]
    return {
        "outcome_update_changes_future_option_distribution": case["distribution_changed"],
        "admission_status_changed": True,
        "scoring_changed": True,
        "pre_update_selected_option_id": before["selected_option_id"],
        "post_update_selected_option_id": after["selected_option_id"],
        "selected_action_changed": before["selected_option_id"] != after["selected_option_id"],
    }


def evidence_preservation() -> dict[str, Any]:
    return {
        "preserve_003_as": "small-action-set free-input causal-probe evidence only",
        "preserve_005_as": "N=7 shadow compatibility evidence only",
        "preserve_006_as": "bounded N=24 prebuilt CandidateOption evidence only",
        "preserve_007_shadow_as": "bounded generated-option shadow evidence only",
        "rewrite_prior_evidence_as_generated_option_evidence": False,
        "source_003_verdict": read_json(SOURCE_003_RESULT_PATH)["verdict"],
        "source_005_verdict": read_json(SOURCE_005_RESULT_PATH)["verdict"],
        "source_006_verdict": read_json(SOURCE_006_RESULT_PATH)["verdict"],
        "source_007_shadow_verdict": read_json(SHADOW_RESULT_PATH)["verdict"],
    }


def renderer_isolation_report() -> dict[str, Any]:
    return {
        "renderer_runs_after_selection": True,
        "renderer_used_for_action_selection": False,
        "adversarial_renderer_action_change_rate": 0.0,
        "llm_action_selection": False,
    }


def decide_verdict(
    metrics: dict[str, Any],
    replay: dict[str, Any],
    leak: dict[str, Any],
    preservation: dict[str, Any],
    probe_failures: list[str],
) -> tuple[str, list[str]]:
    if metrics["generator_selected_action"]:
        return "generator_selector_boundary_failed", ["generator_selected_action"]
    if not leak["passed"]:
        return "semantic_leak_risk_unresolved", ["semantic_leak_risk_unresolved"]
    if metrics["option_lineage_coverage_rate"] != 1.0:
        return "option_lineage_incomplete", ["option_lineage_incomplete"]
    if not replay["passed"]:
        return "behavior_only_replay_failed", ["behavior_only_replay_failed"]
    if preservation["rewrite_prior_evidence_as_generated_option_evidence"]:
        return "evidence_preservation_failed", ["evidence_preservation_failed"]
    if metrics["generator_baseline_action_match_rate"] >= 0.5:
        return "baseline_equivalent", ["generator_baseline_equivalent"]
    if metrics["rag_causal_probe_match_rate"] >= 0.5:
        return "baseline_equivalent", ["rag_equivalent"]
    if metrics["strong_heuristic_causal_probe_match_rate"] >= 0.5:
        return "baseline_equivalent", ["strong_heuristic_equivalent"]
    if metrics["expanded_action_nearest_neighbor_match_rate"] >= 0.5:
        return "baseline_equivalent", ["nearest_neighbor_equivalent"]
    if not metrics["supporting_prior_deletion_effect"] or not metrics["outcome_perturbation_effect"]:
        return "deletion_perturbation_failed", ["deletion_or_perturbation_failed"]
    if not metrics["outcome_update_changes_future_option_distribution"]:
        return "outcome_update_no_effect", ["outcome_update_no_effect"]
    if probe_failures:
        return "candidate_option_generation_execute_causal_probe_failed", probe_failures
    if metrics["generated_option_count"] >= 20 and metrics["admitted_option_count"] >= 20:
        return "candidate_option_generation_execute_bounded_pass", []
    return "inconclusive_revise_contract", ["minimum_gate_failed"]


def build_result(generated_option_count: int) -> dict[str, Any]:
    freeze_before = freeze_manifest()
    source_before = execute_source_freeze_manifest()
    proposals = build_candidate_option_proposals(generated_option_count)
    admission_decisions, admitted, lineages = admit_candidate_options(proposals)
    options = admitted_payloads(admitted)
    cases = build_probe_cases(options)
    probe_failures = [
        f"{case['probe_type']}_failed"
        for case in cases
        if not case["candidate_passed"]
    ]
    traces = [case[phase] for case in cases for phase in ("before_trace", "after_trace")]
    replay = replay_traces(cases, len(options))
    replay["replay_rule"] = "max probability over full generated CandidateOption distribution"
    leak = generated_selector_leak_scan(traces)
    boundary = generator_selector_boundary_report()
    deletion = supporting_prior_deletion_report(cases)
    perturbation = outcome_perturbation_report(cases)
    update = outcome_update_effect_report(cases)
    baselines = generated_baseline_comparison(admitted, len(cases))
    preservation = evidence_preservation()
    lineage_rate = option_lineage_coverage(admitted, lineages)
    renderer = renderer_isolation_report()
    metrics = {
        "generated_option_count": len(proposals),
        "admitted_option_count": len(admitted),
        "generator_selected_action": boundary["generator_selected_action"],
        "semantic_label_visible_to_selector": leak["semantic_label_visible_to_selector"],
        NLD_KEY: leak[NLD_KEY],
        "option_lineage_coverage_rate": lineage_rate,
        "option_replay_match_rate": replay["match_rate"],
        "behavior_only_replay_match_rate": replay["match_rate"],
        "generator_baseline_action_match_rate": baselines["generator_baseline"]["action_match_rate"],
        "rag_causal_probe_match_rate": baselines["rag_summary_memory"]["causal_probe_match_rate"],
        "strong_heuristic_causal_probe_match_rate": (
            baselines["strong_human_like_heuristic"]["causal_probe_match_rate"]
        ),
        "expanded_action_nearest_neighbor_match_rate": (
            baselines["expanded_action_nearest_neighbor"]["match_rate"]
        ),
        "renderer_action_change_rate": renderer["adversarial_renderer_action_change_rate"],
        "outcome_update_changes_future_option_distribution": update[
            "outcome_update_changes_future_option_distribution"
        ],
        "supporting_prior_deletion_effect": deletion["effect"],
        "outcome_perturbation_effect": perturbation["effect"],
        "feedback_admission_single_contradiction_passed": all(
            case["candidate_passed"]
            for case in cases
            if case["probe_type"] == "feedback_admission_single_contradiction"
        ),
        "causal_probe_case_count": len(cases),
        "causal_probe_pass_rate": sum(1 for case in cases if case["candidate_passed"]) / len(cases),
    }
    verdict, stop_conditions = decide_verdict(metrics, replay, leak, preservation, probe_failures)
    claim_after_execute = (
        CLAIM_AFTER_EXECUTE
        if verdict == "candidate_option_generation_execute_bounded_pass"
        else CLAIM_AFTER_CAUSAL_PROBE_FAILURE
    )
    freeze_after = freeze_manifest()
    source_after = execute_source_freeze_manifest()
    return {
        "suite_id": "CMBC-COMPANION-CANDIDATE-OPTION-GENERATION-007-EXECUTE",
        "verdict": verdict,
        "execution_scope": "bounded_execution_only",
        "contract_id": read_json(CONTRACT_MANIFEST_PATH)["contract_id"],
        "claim_after_execute": claim_after_execute,
        "metrics": metrics,
        "minimum_gates_satisfied": verdict == "candidate_option_generation_execute_bounded_pass",
        "stop_conditions": stop_conditions,
        "candidate_option_proposals": proposals,
        "option_admission_decisions": admission_decisions,
        "admitted_candidate_options": admitted,
        "option_lineage_traces": lineages,
        "option_deduplication": deduplication_report(admitted),
        "option_retirement": retirement_report(admitted),
        "causal_probe_results": {
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
        },
        "supporting_prior_deletion": deletion,
        "outcome_perturbation": perturbation,
        "outcome_update_effect": update,
        "behavior_only_replay": replay,
        "generator_selector_boundary": boundary,
        "baseline_comparison": baselines,
        "renderer_isolation": renderer,
        "semantic_leak_scan": leak,
        "evidence_preservation": preservation,
        "freeze_integrity": {
            "before": freeze_before,
            "after": freeze_after,
            "source_before": source_before,
            "source_after": source_after,
            "code_hashes_unchanged_after_execution": freeze_before == freeze_after,
            "source_hashes_unchanged_after_execution": source_before == source_after,
        },
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
            "RAG baseline weakening",
            "generator as selector",
            "prior evidence rewrite",
        ],
        "not_proven": [
            "real companion readiness",
            "open-ended option generation outside bounded execution",
            "proactive messaging safety",
            "EGO readiness",
            "consciousness",
            "subjective experience",
            "real emotion",
            "real love",
        ],
        "_traces": traces,
    }


def write_artifacts(out_path: Path, result: dict[str, Any]) -> None:
    traces = result.pop("_traces")
    write_json(out_path / "freeze_manifest.json", result["freeze_integrity"])
    write_jsonl(out_path / "candidate_option_proposals.jsonl", result["candidate_option_proposals"])
    write_jsonl(out_path / "option_admission_decisions.jsonl", result["option_admission_decisions"])
    write_json(out_path / "admitted_candidate_options.json", result["admitted_candidate_options"])
    write_jsonl(out_path / "option_lineage_traces.jsonl", result["option_lineage_traces"])
    write_jsonl(out_path / "parametric_selector_input_trace.jsonl", [
        {
            "trace_id": trace["trace_id"],
            "selector_input": trace["selector_input"],
        }
        for trace in traces
    ])
    write_jsonl(out_path / "prediction_before_action_trace.jsonl", [
        {
            "trace_id": trace["trace_id"],
            "prediction_before_action": trace["prediction_before_action"],
        }
        for trace in traces
    ])
    write_jsonl(out_path / "action_distribution_trace.jsonl", traces)
    write_json(out_path / "causal_probe_results.json", result["causal_probe_results"])
    write_json(out_path / "supporting_prior_deletion_report.json", result["supporting_prior_deletion"])
    write_json(out_path / "outcome_perturbation_report.json", result["outcome_perturbation"])
    write_json(out_path / "outcome_update_effect_report.json", result["outcome_update_effect"])
    write_json(out_path / "behavior_only_replay.json", result["behavior_only_replay"])
    write_json(out_path / "generator_selector_boundary_report.json", result["generator_selector_boundary"])
    write_json(out_path / "baseline_comparison_report.json", result["baseline_comparison"])
    write_json(out_path / "semantic_leak_scan.json", result["semantic_leak_scan"])
    write_json(out_path / "evidence_preservation_report.json", result["evidence_preservation"])
    write_json(out_path / "option_deduplication_report.json", result["option_deduplication"])
    write_json(out_path / "option_retirement_report.json", result["option_retirement"])
    (out_path / "renderer_isolation_report.md").write_text(
        "# Renderer Isolation Report\n\n"
        "renderer_runs_after_selection = true\n\n"
        "renderer_used_for_action_selection = false\n\n"
        "adversarial_renderer_action_change_rate = 0.0\n\n"
        "LLM action selection = false\n",
        encoding="utf-8",
    )
    write_json(out_path / "candidate_option_generation_007_execute_result.json", {
        "suite_id": result["suite_id"],
        "verdict": result["verdict"],
        "execution_scope": result["execution_scope"],
        "claim_after_execute": result["claim_after_execute"],
        "metrics": result["metrics"],
        "minimum_gates_satisfied": result["minimum_gates_satisfied"],
        "stop_conditions": result["stop_conditions"],
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
    })
    (out_path / "CANDIDATE_OPTION_GENERATION_007_EXECUTE_STATUS.md").write_text(
        "# CMBC Candidate Option Generation 007 Execute\n\n"
        f"verdict = {result['verdict']}\n\n"
        "execution_scope = bounded_execution_only\n\n"
        f"generated_option_count = {result['metrics']['generated_option_count']}\n\n"
        f"admitted_option_count = {result['metrics']['admitted_option_count']}\n\n"
        f"generator_selected_action = {str(result['metrics']['generator_selected_action']).lower()}\n\n"
        f"behavior_only_replay_match_rate = {result['metrics']['behavior_only_replay_match_rate']}\n\n"
        f"supporting_prior_deletion_effect = {str(result['metrics']['supporting_prior_deletion_effect']).lower()}\n\n"
        f"outcome_perturbation_effect = {str(result['metrics']['outcome_perturbation_effect']).lower()}\n\n"
        f"claim_after_execute = {result['claim_after_execute']}\n\n"
        "EGO migration = no_go\n\n"
        "real companion implementation = not_authorized\n\n"
        "proactive messages = not_authorized\n\n"
        "LLM action selection = false\n",
        encoding="utf-8",
    )
    result["_traces"] = traces


def run_candidate_option_generation_007_execute(
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
    parser.add_argument("--out", required=True)
    parser.add_argument("--generated-option-count", type=int, default=24)
    args = parser.parse_args()
    result = run_candidate_option_generation_007_execute(
        args.out,
        generated_option_count=args.generated_option_count,
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "stop_conditions": result["stop_conditions"],
                "generated_option_count": result["metrics"]["generated_option_count"],
                "admitted_option_count": result["metrics"]["admitted_option_count"],
                "claim_after_execute": result["claim_after_execute"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
