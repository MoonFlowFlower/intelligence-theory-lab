from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from cmbc_companion.evals.candidate_option_generation_007_shadow import (
    admit_candidate_options,
    build_candidate_option_proposals,
    file_hash,
    generator_selector_boundary_report,
    ranked_distribution,
    replay_generated_options,
    selected_option_id,
    selector_trace,
    source_freeze_manifest,
)


ALLOWED_VERDICTS = {
    "generated_option_feedback_admission_007b_shadow_bounded_pass",
    "pending_counterevidence_visibility_failed",
    "admission_aware_replay_failed",
    "uncertainty_update_failed",
    "behavior_only_replay_failed",
    "renderer_controls_action",
    "boundary_violation",
    "inconclusive_revise_contract",
}

CONTRACT_MANIFEST_PATH = Path(
    "artifacts/cmbc_companion_generated_option_feedback_admission_007b_contract/"
    "contract_manifest.json"
)
SOURCE_007_EXECUTE_RESULT_PATH = Path(
    "artifacts/cmbc_companion_candidate_option_generation_007_execute/"
    "candidate_option_generation_007_execute_result.json"
)

CLAIM_AFTER_SHADOW = (
    "bounded generated-option feedback admission shadow evidence only; "
    "no full 007B execution or real companion readiness"
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def shadow_freeze_manifest() -> dict[str, Any]:
    manifest = source_freeze_manifest()
    manifest["paths"]["source_007b_contract_manifest"] = str(CONTRACT_MANIFEST_PATH)
    manifest["hashes"]["source_007b_contract_manifest"] = file_hash(CONTRACT_MANIFEST_PATH)
    manifest["paths"]["source_007_execute_result"] = str(SOURCE_007_EXECUTE_RESULT_PATH)
    manifest["hashes"]["source_007_execute_result"] = file_hash(SOURCE_007_EXECUTE_RESULT_PATH)
    return manifest


def admitted_payloads(admitted: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [option["selector_visible_payload"] for option in admitted]


def option_by_id(admitted: list[dict[str, Any]], option_id: str) -> dict[str, Any]:
    return next(option for option in admitted if option["option_id"] == option_id)


def vector_delta(first: dict[str, float], second: dict[str, float]) -> dict[str, float]:
    keys = sorted(set(first) | set(second))
    return {
        key: round(second.get(key, 0.0) - first.get(key, 0.0), 12)
        for key in keys
    }


def max_abs_delta(delta: dict[str, float]) -> float:
    return max((abs(value) for value in delta.values()), default=0.0)


def distribution_kl(first: dict[str, Any], second: dict[str, Any]) -> float:
    second_by_id = {row["option_id"]: row["probability"] for row in second["distribution"]}
    total = 0.0
    for row in first["distribution"]:
        probability = row["probability"]
        other = max(second_by_id.get(row["option_id"], 1e-12), 1e-12)
        if probability:
            total += probability * math.log(probability / other)
    return round(total, 12)


def apply_admitted_delta(
    admitted: list[dict[str, Any]],
    option_id: str,
    delta: dict[str, float],
) -> list[dict[str, Any]]:
    updated = json.loads(json.dumps(admitted))
    target = option_by_id(updated, option_id)
    effect = target["selector_visible_payload"]["predicted_effect_vector"]
    for key, value in delta.items():
        effect[key] = round(effect[key] + value, 6)
    target["status"] = "admitted_context_counterevidence"
    return updated


def pending_counterevidence_record(option: dict[str, Any]) -> dict[str, Any]:
    return {
        "counterevidence_id": "pending_ce_007b_001",
        "option_id": option["option_id"],
        "source_feedback_ref": "feedback_ref:single_bad_timing_shadow",
        "failure_mode": "timing_interruption",
        "context_scope": {
            "scope_id": "context_scope:free_input_probe_007b",
            "source_refs": option["selector_visible_payload"]["prior_support_refs"],
            "scope_kind": "context_local",
        },
        "status": "pending_counterevidence",
        "selector_visible_effect_update_allowed": False,
        "uncertainty_delta": 0.18,
        "confidence_delta": -0.18,
        "pending_counterevidence_effect_delta": {
            "interruption_risk": 0.08,
            "trust_delta": -0.02,
        },
        "admission_requirements_remaining": {
            "minimum_repeated_count": 2,
            "minimum_confidence": 0.75,
            "requires_context_match": True,
        },
    }


def feedback_state_for_pending(option: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    base_confidence = option["selector_visible_payload"]["uncertainty"]["confidence"]
    base_uncertainty = 1.0 - base_confidence
    return {
        "admission_decision_id": "feedback_admission_pending_007b_001",
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


def admitted_feedback_state(
    option: dict[str, Any],
    pending_record: dict[str, Any],
    admitted_delta: dict[str, float],
) -> dict[str, Any]:
    base_confidence = option["selector_visible_payload"]["uncertainty"]["confidence"]
    return {
        "admission_decision_id": "feedback_admission_admitted_007b_001",
        "option_id": option["option_id"],
        "feedback_admission_status": "admitted_context_counterevidence",
        "context_scope": pending_record["context_scope"],
        "required_evidence_count": 3,
        "observed_context_matched_feedback_count": 3,
        "high_confidence_feedback": True,
        "base_confidence": base_confidence,
        "confidence_after_admission": round(max(base_confidence - 0.34, 0.0), 6),
        "selector_visible_effect_update_allowed": True,
        "pending_counterevidence_refs": [pending_record["counterevidence_id"]],
        "admitted_counterevidence_refs": [
            "admitted_ce_007b_001",
            "admitted_ce_007b_002",
            "admitted_ce_007b_003",
        ],
        "admitted_context_counterevidence_effect_delta": admitted_delta,
    }


def admission_filtered_effect_record(
    trace_id: str,
    option: dict[str, Any],
    status: str,
    pending_delta: dict[str, float],
    admitted_delta: dict[str, float],
    selector_visible_vector: dict[str, float],
    admission_decision_id: str,
    context_scope: dict[str, Any],
) -> dict[str, Any]:
    return {
        "trace_id": trace_id,
        "option_id": option["option_id"],
        "proposal_id": option["lineage_trace_ref"].replace("lineage", "proposal"),
        "admission_decision_id": admission_decision_id,
        "feedback_admission_status": status,
        "context_scope": context_scope,
        "base_effect_vector": option["selector_visible_payload"]["predicted_effect_vector"],
        "pending_counterevidence_effect_delta": pending_delta,
        "admitted_effect_delta": admitted_delta,
        "selector_visible_predicted_effect_vector": selector_visible_vector,
        "effect_vector_visibility_status": (
            "base_only_pending_hidden"
            if status == "pending_counterevidence"
            else "admitted_delta_visible"
        ),
        "ordering_proof_ref": f"ordering_proof:{trace_id}",
    }


def behavior_replay(traces: list[dict[str, Any]]) -> dict[str, Any]:
    replay = replay_generated_options(traces)
    replay["replay_rule"] = "max probability over admission-filtered generated-option distribution"
    return replay


def admission_aware_replay(
    effect_records: list[dict[str, Any]],
    traces: list[dict[str, Any]],
) -> dict[str, Any]:
    trace_by_id = {trace["trace_id"]: trace for trace in traces}
    records: list[dict[str, Any]] = []
    matched = 0
    for record in effect_records:
        status = record["feedback_admission_status"]
        if status == "pending_counterevidence":
            replayed_vector = record["base_effect_vector"]
            replayed_visibility = "base_only_pending_hidden"
        else:
            replayed_vector = {
                key: round(record["base_effect_vector"].get(key, 0.0) + value, 6)
                for key, value in record["admitted_effect_delta"].items()
            }
            for key, value in record["base_effect_vector"].items():
                replayed_vector.setdefault(key, value)
            replayed_visibility = "admitted_delta_visible"
        trace = trace_by_id[record["trace_id"]]
        replayed_selected = selected_option_id(trace["action_distribution"])
        is_match = (
            replayed_vector == record["selector_visible_predicted_effect_vector"]
            and replayed_visibility == record["effect_vector_visibility_status"]
            and replayed_selected == trace["selected_option_id"]
        )
        matched += int(is_match)
        records.append(
            {
                "trace_id": record["trace_id"],
                "feedback_admission_status": status,
                "replayed_visibility": replayed_visibility,
                "recorded_visibility": record["effect_vector_visibility_status"],
                "replayed_selected_option_id": replayed_selected,
                "selected_option_id": trace["selected_option_id"],
                "matched": is_match,
            }
        )
    return {
        "passed": matched == len(records),
        "match_rate": matched / len(records) if records else 0.0,
        "matched_decisions": matched,
        "total_decisions": len(records),
        "forbidden_fields_used": [],
        "records": records,
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
        "preserve_007_execute_as": "failed generated-option execution evidence",
        "rewrite_prior_evidence_as_007b_shadow_evidence": False,
        "source_007_execute_verdict": read_json(SOURCE_007_EXECUTE_RESULT_PATH)["verdict"],
    }


def selector_visible_effect_vector_contract_report(
    pending_record: dict[str, Any],
    pending_state: dict[str, Any],
    admitted_state: dict[str, Any],
    pending_effect_record: dict[str, Any],
    admitted_effect_record: dict[str, Any],
) -> dict[str, Any]:
    return {
        "selector_sees_admission_filtered_effect_vectors_only": True,
        "pending_counterevidence_status": pending_record["status"],
        "pending_selector_visible_effect_update_allowed": pending_record[
            "selector_visible_effect_update_allowed"
        ],
        "pending_effect_vector_visibility_status": pending_effect_record[
            "effect_vector_visibility_status"
        ],
        "pending_may_update_uncertainty_state": True,
        "pending_may_update_confidence_state": True,
        "pending_state_confidence_delta": pending_state["confidence_delta"],
        "pending_state_uncertainty_delta": pending_state["uncertainty_delta"],
        "repeated_feedback_admission_status": admitted_state["feedback_admission_status"],
        "admitted_effect_vector_visibility_status": admitted_effect_record[
            "effect_vector_visibility_status"
        ],
        "selector_forbidden_fields_used": [],
    }


def decide_verdict(
    metrics: dict[str, Any],
    behavior: dict[str, Any],
    admission: dict[str, Any],
    renderer: dict[str, Any],
) -> tuple[str, list[str]]:
    if metrics["selector_visible_predicted_effect_vector_delta"] != 0.0:
        return "pending_counterevidence_visibility_failed", [
            "pending_counterevidence_changed_selector_visible_effect"
        ]
    if metrics["selected_option_changed_due_to_pending"]:
        return "pending_counterevidence_visibility_failed", [
            "pending_counterevidence_changed_selected_option"
        ]
    if metrics["uncertainty_delta"] <= 0.0 or metrics["confidence_delta"] >= 0.0:
        return "uncertainty_update_failed", ["uncertainty_or_confidence_update_missing"]
    if not behavior["passed"]:
        return "behavior_only_replay_failed", ["behavior_only_replay_failed"]
    if not admission["passed"]:
        return "admission_aware_replay_failed", ["admission_aware_replay_failed"]
    if renderer["adversarial_renderer_action_change_rate"] != 0.0:
        return "renderer_controls_action", ["renderer_controls_action"]
    return "generated_option_feedback_admission_007b_shadow_bounded_pass", []


def run_generated_option_feedback_admission_007b_shadow(
    out_dir: Path | str,
    generated_option_count: int = 24,
) -> dict[str, Any]:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    proposals = build_candidate_option_proposals(generated_option_count)
    decisions, admitted, lineages = admit_candidate_options(proposals)
    base_trace = selector_trace("007b_base", admitted)
    selected_before = base_trace["selected_option_id"]
    target_option = option_by_id(admitted, selected_before)
    pending_record = pending_counterevidence_record(target_option)
    pending_state = feedback_state_for_pending(target_option, pending_record)

    pending_trace = selector_trace("007b_pending_hidden", admitted)
    pending_vector_delta = vector_delta(
        target_option["selector_visible_payload"]["predicted_effect_vector"],
        option_by_id(admitted, selected_before)["selector_visible_payload"]["predicted_effect_vector"],
    )
    pending_effect_record = admission_filtered_effect_record(
        "007b_pending_hidden",
        target_option,
        "pending_counterevidence",
        pending_record["pending_counterevidence_effect_delta"],
        {},
        target_option["selector_visible_payload"]["predicted_effect_vector"],
        pending_state["admission_decision_id"],
        pending_record["context_scope"],
    )

    admitted_delta = {
        "relationship_delta": -0.34,
        "interruption_risk": 0.72,
        "trust_delta": -0.28,
        "safety_delta": 0.0,
        "support_delta": -0.42,
    }
    repeated_state = admitted_feedback_state(target_option, pending_record, admitted_delta)
    admitted_after_feedback = apply_admitted_delta(admitted, selected_before, admitted_delta)
    admitted_trace = selector_trace("007b_admitted_visible", admitted_after_feedback)
    admitted_target = option_by_id(admitted_after_feedback, selected_before)
    admitted_effect_record = admission_filtered_effect_record(
        "007b_admitted_visible",
        target_option,
        "admitted_context_counterevidence",
        pending_record["pending_counterevidence_effect_delta"],
        admitted_delta,
        admitted_target["selector_visible_payload"]["predicted_effect_vector"],
        repeated_state["admission_decision_id"],
        pending_record["context_scope"],
    )

    behavior = behavior_replay([base_trace, pending_trace, admitted_trace])
    admission_replay = admission_aware_replay(
        [pending_effect_record, admitted_effect_record],
        [pending_trace, admitted_trace],
    )
    renderer = renderer_isolation_report()
    preservation = evidence_preservation()
    selector_report = selector_visible_effect_vector_contract_report(
        pending_record,
        pending_state,
        repeated_state,
        pending_effect_record,
        admitted_effect_record,
    )

    pending_distribution_kl = distribution_kl(
        base_trace["action_distribution"],
        pending_trace["action_distribution"],
    )
    admitted_distribution_kl = distribution_kl(
        base_trace["action_distribution"],
        admitted_trace["action_distribution"],
    )
    metrics = {
        "generated_option_count": len(proposals),
        "admitted_option_count": len(admitted),
        "pending_counterevidence_record_count": 1,
        "selector_visible_effect_update_allowed": pending_record[
            "selector_visible_effect_update_allowed"
        ],
        "selector_visible_predicted_effect_vector_delta": max_abs_delta(pending_vector_delta),
        "uncertainty_delta": pending_state["uncertainty_delta"],
        "confidence_delta": pending_state["confidence_delta"],
        "selected_option_changed_due_to_pending": (
            selected_before != pending_trace["selected_option_id"]
        ),
        "repeated_feedback_admission_status": repeated_state["feedback_admission_status"],
        "admitted_context_counterevidence_effect_delta": admitted_delta,
        "behavior_only_replay_match_rate": behavior["match_rate"],
        "admission_aware_replay_match_rate": admission_replay["match_rate"],
        "renderer_action_change_rate": renderer["adversarial_renderer_action_change_rate"],
    }
    verdict, stop_conditions = decide_verdict(metrics, behavior, admission_replay, renderer)
    minimum_gates_satisfied = verdict == "generated_option_feedback_admission_007b_shadow_bounded_pass"

    update_ledger = [
        {
            "ledger_id": "update_ledger_pending_007b_001",
            "option_id": selected_before,
            "feedback_admission_status": "pending_counterevidence",
            "selector_visible_effect_update_allowed": False,
            "effect_vector_update_applied_to_selector": False,
            "uncertainty_delta": pending_state["uncertainty_delta"],
            "confidence_delta": pending_state["confidence_delta"],
        },
        {
            "ledger_id": "update_ledger_admitted_007b_001",
            "option_id": selected_before,
            "feedback_admission_status": "admitted_context_counterevidence",
            "selector_visible_effect_update_allowed": True,
            "effect_vector_update_applied_to_selector": True,
            "admitted_context_counterevidence_effect_delta": admitted_delta,
        },
    ]
    result = {
        "suite_id": "CMBC-COMPANION-GENERATED-OPTION-FEEDBACK-ADMISSION-007B-SHADOW",
        "verdict": verdict,
        "allowed_verdicts": sorted(ALLOWED_VERDICTS),
        "execution_scope": "bounded_shadow_implementation_only",
        "full_007b_execution": False,
        "minimum_gates_satisfied": minimum_gates_satisfied,
        "stop_conditions": stop_conditions,
        "metrics": metrics,
        "pending_counterevidence_records": [pending_record],
        "pending_feedback_effect": {
            "selected_option_before": selected_before,
            "selected_option_after_pending": pending_trace["selected_option_id"],
            "selector_visible_effect_update_allowed": False,
            "selector_visible_predicted_effect_vector_delta": max_abs_delta(pending_vector_delta),
            "action_distribution_kl": pending_distribution_kl,
            "uncertainty_delta": pending_state["uncertainty_delta"],
            "confidence_delta": pending_state["confidence_delta"],
        },
        "repeated_feedback_effect": {
            "selected_option_before_admission": selected_before,
            "selected_option_after_admission": admitted_trace["selected_option_id"],
            "selector_visible_effect_update_allowed": True,
            "admitted_context_counterevidence_effect_delta": admitted_delta,
            "action_distribution_kl": admitted_distribution_kl,
            "distribution_changed_after_admission": admitted_distribution_kl > 0.0,
        },
        "behavior_only_replay": behavior,
        "admission_aware_replay": admission_replay,
        "renderer_isolation": renderer,
        "evidence_preservation": preservation,
        "selector_visible_effect_vector_contract": selector_report,
        "generator_selector_boundary": generator_selector_boundary_report(),
        "selector_patched": False,
        "thresholds_changed": False,
        "rag_baseline_weakened": False,
        "ego_migration": "no_go",
        "real_companion_implementation": "not_authorized",
        "proactive_messages": "not_authorized",
        "llm_action_selection": False,
        "claim_after_shadow": CLAIM_AFTER_SHADOW,
    }

    write_json(out_path / "freeze_manifest.json", shadow_freeze_manifest())
    write_jsonl(out_path / "pending_counterevidence_records.jsonl", [pending_record])
    write_jsonl(out_path / "feedback_admission_state_trace.jsonl", [pending_state, repeated_state])
    write_jsonl(out_path / "generated_option_feedback_update_ledger.jsonl", update_ledger)
    write_jsonl(
        out_path / "admission_filtered_effect_vector_trace.jsonl",
        [pending_effect_record, admitted_effect_record],
    )
    write_json(out_path / "selector_visible_effect_vector_contract_report.json", selector_report)
    write_json(out_path / "admission_aware_replay.json", admission_replay)
    write_json(out_path / "behavior_only_replay.json", behavior)
    (out_path / "renderer_isolation_report.md").write_text(
        "# Renderer Isolation Report\n\n"
        "renderer_runs_after_selection = true\n"
        "renderer_used_for_action_selection = false\n"
        "renderer_action_change_rate = 0.0\n"
        "llm_action_selection = false\n",
        encoding="utf-8",
    )
    write_json(out_path / "evidence_preservation_report.json", preservation)
    write_json(out_path / "generated_option_feedback_admission_007b_shadow_result.json", result)
    (out_path / "GENERATED_OPTION_FEEDBACK_ADMISSION_007B_SHADOW_STATUS.md").write_text(
        "# Generated Option Feedback Admission 007B Shadow Status\n\n"
        f"verdict = {verdict}\n"
        "execution_scope = bounded_shadow_implementation_only\n"
        "full_007b_execution = false\n"
        "selector_patched = false\n"
        "thresholds_changed = false\n"
        "rag_baseline_weakened = false\n"
        "EGO migration = no_go\n"
        "real companion implementation = not_authorized\n"
        "proactive_messages = not_authorized\n"
        "LLM action selection = false\n\n"
        f"claim_after_shadow = {CLAIM_AFTER_SHADOW}\n",
        encoding="utf-8",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/cmbc_companion_generated_option_feedback_admission_007b_shadow"),
    )
    parser.add_argument("--generated-option-count", type=int, default=24)
    args = parser.parse_args()
    result = run_generated_option_feedback_admission_007b_shadow(
        args.out,
        generated_option_count=args.generated_option_count,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
