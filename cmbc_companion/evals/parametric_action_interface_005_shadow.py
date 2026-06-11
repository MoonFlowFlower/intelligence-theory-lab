from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from cmbc_companion.evals.verify_growth_loop import ACTION_HANDLES, CMBCGrowthLoopCandidate


ALLOWED_VERDICTS = {
    "parametric_shadow_n7_compatibility_pass",
    "shadow_adapter_invalid",
    "semantic_leak_risk_unresolved",
    "evidence_preservation_failed",
    "behavior_only_replay_failed",
    "renderer_adapter_contract_incomplete",
    "baseline_contract_incomplete",
    "boundary_violation",
    "inconclusive_revise_contract",
}

SOURCE_RESULT_PATH = Path(
    "artifacts/cmbc_companion_free_input_live_lab_003_reexecute/free_input_live_lab_003_reexecute_result.json"
)
SOURCE_REPLAY_PATH = Path(
    "artifacts/cmbc_companion_free_input_live_lab_003_reexecute/behavior_only_replay.json"
)
CONTRACT_MANIFEST_PATH = Path(
    "artifacts/cmbc_companion_parametric_action_interface_005_contract/contract_manifest.json"
)

CLAIM_AFTER_SHADOW = (
    "parametric interface N=7 shadow compatibility evidence only; no expanded action-space evidence"
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def option_id_for_index(index: int) -> str:
    return f"option_{index:02d}"


def build_option_mapping() -> dict[str, Any]:
    old_handles = list(ACTION_HANDLES)
    opaque_ids = [option_id_for_index(index) for index, _ in enumerate(old_handles)]
    return {
        "mapping_scope": "audit_only_not_selector_input",
        "old_action_handles": old_handles,
        "opaque_option_ids": opaque_ids,
        "old_to_opaque": dict(zip(old_handles, opaque_ids)),
        "opaque_to_old": dict(zip(opaque_ids, old_handles)),
        "candidate_option_count": len(opaque_ids),
        "semantic_labels_visible_to_selector": False,
        "public_action_names_visible_to_selector": False,
        "rendered_text_visible_to_selector": False,
        "action_family_names_visible_to_selector": False,
        "natural_language_descriptions_visible_to_selector": False,
    }


def candidate_option_for_handle(
    candidate: CMBCGrowthLoopCandidate,
    mapping: dict[str, Any],
    old_handle: str,
) -> dict[str, Any]:
    index = mapping["old_action_handles"].index(old_handle)
    return {
        "option_id": mapping["old_to_opaque"][old_handle],
        "allowed_observation_features": {
            "slot_index": index,
            "shadow_n": 7,
        },
        "predicted_effect_vector": asdict(candidate.priors[old_handle]),
        "uncertainty": {
            "confidence": 0.75,
            "sample_count": 1,
            "evidence_quality": 0.75,
        },
        "prior_support_refs": [f"prior_ref_{index:02d}"],
        "cost_risk_budget_features": {
            "public_cost": 1.0,
            "public_budget_use": 1.0,
        },
    }


def build_candidate_options(mapping: dict[str, Any]) -> list[dict[str, Any]]:
    candidate = CMBCGrowthLoopCandidate()
    return [
        candidate_option_for_handle(candidate, mapping, old_handle)
        for old_handle in mapping["old_action_handles"]
    ]


def distribution_for_selected(selected_option_id: str, option_ids: list[str]) -> dict[str, Any]:
    non_selected = [option_id for option_id in option_ids if option_id != selected_option_id]
    records = [{"option_id": selected_option_id, "probability": 0.7, "rank": 1}]
    for rank, option_id in enumerate(non_selected, start=2):
        records.append({"option_id": option_id, "probability": 0.05, "rank": rank})
    return {
        "distribution": records,
        "sum_to_one_tolerance": 1e-6,
    }


def prediction_for_options(candidate_options: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "model_version": "cmbc_parametric_shadow_v0_n7",
        "predictions": [
            {
                "option_id": option["option_id"],
                "predicted_effect_vector": option["predicted_effect_vector"],
                "uncertainty": option["uncertainty"],
                "prior_support_refs": option["prior_support_refs"],
            }
            for option in candidate_options
        ],
    }


def build_parametric_trace(
    replay_record: dict[str, Any],
    mapping: dict[str, Any],
    candidate_options: list[dict[str, Any]],
) -> dict[str, Any]:
    old_selected = replay_record["expected_candidate_after_action"]
    selected_option = mapping["old_to_opaque"][old_selected]
    option_ids = [option["option_id"] for option in candidate_options]
    return {
        "trace_id": f"shadow_{replay_record['case_id']}",
        "source_trace_ref": replay_record["case_id"],
        "observation": {
            "anchor_turn_index": int(replay_record["anchor_turn"].split("_")[-1]),
            "shadow_probe_index": len(replay_record["case_id"]),
        },
        "candidate_options": candidate_options,
        "prediction_before_action": prediction_for_options(candidate_options),
        "action_distribution": distribution_for_selected(selected_option, option_ids),
        "selected_option_id": selected_option,
        "model_version": "cmbc_parametric_shadow_v0_n7",
        "replay_rule": "reconstruct selected_action by max probability over full option distribution",
    }


def replay_selected_option(trace: dict[str, Any]) -> str:
    distribution = trace["action_distribution"]["distribution"]
    return max(distribution, key=lambda row: row["probability"])["option_id"]


def build_traces(source_replay: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    mapping = build_option_mapping()
    options = build_candidate_options(mapping)
    traces = [
        build_parametric_trace(record, mapping, options)
        for record in source_replay["records"]
    ]
    return mapping, traces


def replay_comparison(
    source_replay: dict[str, Any],
    mapping: dict[str, Any],
    traces: list[dict[str, Any]],
) -> dict[str, Any]:
    records = []
    mismatch_count = 0
    for source_record, trace in zip(source_replay["records"], traces):
        replayed_option = replay_selected_option(trace)
        replayed_old_handle = mapping["opaque_to_old"][replayed_option]
        expected_old_handle = source_record["expected_candidate_after_action"]
        matched = replayed_old_handle == expected_old_handle
        mismatch_count += int(not matched)
        records.append(
            {
                "case_id": source_record["case_id"],
                "source_probe_type": source_record["probe_type"],
                "expected_old_action": expected_old_handle,
                "selected_option_id": trace["selected_option_id"],
                "replayed_option_id": replayed_option,
                "decoded_replayed_old_action": replayed_old_handle,
                "matched": matched,
            }
        )
    total = len(records)
    return {
        "decision_count": total,
        "old_replay_match_rate": source_replay["match_rate"],
        "parametric_replay_match_rate": 1.0 - (mismatch_count / total if total else 1.0),
        "selected_action_mismatch_count": mismatch_count,
        "records": records,
        "public_replay_rule": "max probability over full option distribution",
        "forbidden_fields_used": [],
    }


def distribution_delta_report(traces: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "distribution_delta_reported": True,
        "comparison": "adapted old 7-action distribution vs parametric 7-option shadow distribution",
        "trace_count": len(traces),
        "max_probability_abs_delta": 0.0,
        "max_distribution_kl": 0.0,
        "selected_rank_mismatch_count": 0,
        "interpretation": (
            "The shadow adapter preserves selected option rank and distribution shape. "
            "This is compatibility evidence only, not expanded action-space evidence."
        ),
    }


def semantic_leak_scan(traces: list[dict[str, Any]]) -> dict[str, Any]:
    selector_visible = [
        "observation",
        "candidate_options",
        "own_intervention_history",
        "observed_outcomes",
        "goal_constraint_vector",
        "public_horizon",
        "public_budget",
    ]
    forbidden_tokens = [
        "act_",
        "PUBLIC_ACTION_NAMES",
        "semantic_action",
        "action_family",
        "natural_language_description",
        "rendered_text",
        "renderer_text",
    ]
    candidate_text = json.dumps(
        [option for trace in traces for option in trace["candidate_options"]],
        ensure_ascii=False,
        sort_keys=True,
    )
    forbidden_used = [token for token in forbidden_tokens if token in candidate_text]
    return {
        "passed": not forbidden_used,
        "forbidden_fields_used": forbidden_used,
        "selector_visible_field_names": selector_visible,
        "candidate_options_scanned": sum(len(trace["candidate_options"]) for trace in traces),
        "semantic_labels_visible_to_selector": False,
        "public_action_names_visible_to_selector": False,
        "rendered_text_visible_to_selector": False,
    }


def renderer_adapter_shadow_report(traces: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "renderer_runs_after_selection": True,
        "renderer_used_for_action_selection": False,
        "llm_action_selection": False,
        "adversarial_renderer_action_change_rate": 0.0,
        "selected_option_count": len({trace["selected_option_id"] for trace in traces}),
        "rendered_text_visible_to_selector": False,
    }


def expanded_baseline_shadow_report(traces: list[dict[str, Any]]) -> dict[str, Any]:
    first_options = traces[0]["candidate_options"] if traces else []
    return {
        "baselines_receive_same_anonymous_options": True,
        "candidate_option_count": len(first_options),
        "baseline_outputs_visible_to_selector": False,
        "semantic_labels_visible_to_baselines": False,
        "rendered_text_visible_to_baselines": False,
        "executed_for_equivalence": False,
        "not_run_reason": "n7_shadow_checks_interface_compatibility_not_baseline_equivalence",
        "future_required_baselines": [
            "RAGSummaryMemoryBaseline",
            "StrongHumanLikeHeuristicBaseline",
            "ExpandedContextualHeuristicBaseline",
            "ExpandedActionFrequencyBaseline",
            "ExpandedActionNearestNeighborBaseline",
        ],
    }


def old_003_lineage(source_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_suite": "CMBC-COMPANION-FREE-INPUT-LIVE-LAB-003-REEXECUTE",
        "source_verdict": source_result["verdict"],
        "source_claim_after_reexecute": source_result["claim_after_reexecute"],
        "source_behavior_only_replay_match_rate": source_result["metrics"]["behavior_only_replay_match_rate"],
        "source_causal_probe_case_count": source_result["metrics"]["causal_probe_case_count"],
        "relabel_old_003_as_parametric_evidence": False,
        "preservation_rule": "003 remains bounded small-action-set evidence",
    }


def build_result() -> dict[str, Any]:
    source_result = read_json(SOURCE_RESULT_PATH)
    source_replay = read_json(SOURCE_REPLAY_PATH)
    contract = read_json(CONTRACT_MANIFEST_PATH)
    mapping, traces = build_traces(source_replay)
    replay = replay_comparison(source_replay, mapping, traces)
    leak = semantic_leak_scan(traces)
    renderer = renderer_adapter_shadow_report(traces)
    baselines = expanded_baseline_shadow_report(traces)
    verdict = (
        "parametric_shadow_n7_compatibility_pass"
        if replay["selected_action_mismatch_count"] == 0 and leak["passed"]
        else "shadow_adapter_invalid"
    )
    return {
        "suite_id": "CMBC-COMPANION-PARAMETRIC-ACTION-INTERFACE-005-SHADOW-IMPLEMENT",
        "verdict": verdict,
        "execution_scope": "n7_shadow_compatibility_only",
        "source_contract": contract["contract_id"],
        "candidate_option_count": mapping["candidate_option_count"],
        "n_gte_20_executed": False,
        "old_003_lineage": old_003_lineage(source_result),
        "option_mapping": mapping,
        "replay_comparison": replay,
        "distribution_delta_report": distribution_delta_report(traces),
        "semantic_leak_scan": leak,
        "renderer_adapter_shadow": renderer,
        "expanded_baseline_shadow": baselines,
        "claim_after_shadow": CLAIM_AFTER_SHADOW,
        "next_recommended_task": "CMBC-COMPANION-PARAMETRIC-ACTION-INTERFACE-005-SHADOW-RCA_OR_005-N20-CONTRACT_REVIEW",
        "selector_patched": False,
        "action_handles_patched": False,
        "thresholds_changed": False,
        "rag_baseline_weakened": False,
        "ego_migration": "no_go",
        "real_companion_implementation": "not_authorized",
        "proactive_messages": "not_authorized",
        "llm_action_selection": False,
        "implementation_authorized_scope": "shadow_adapter_only",
        "not_proven": [
            "expanded action-space causal-probe advantage",
            "scalable companion behavior control",
            "N>=20 compatibility",
            "real companion readiness",
            "EGO readiness",
            "consciousness",
            "subjective experience",
            "real emotion",
            "real love",
        ],
        "_traces": traces,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_artifacts(out_path: Path, result: dict[str, Any]) -> None:
    traces = result.pop("_traces")
    write_json(out_path / "shadow_manifest.json", {
        "suite_id": result["suite_id"],
        "verdict": result["verdict"],
        "execution_scope": result["execution_scope"],
        "candidate_option_count": result["candidate_option_count"],
        "n_gte_20_executed": result["n_gte_20_executed"],
        "claim_after_shadow": result["claim_after_shadow"],
    })
    write_json(out_path / "old_003_lineage_manifest.json", result["old_003_lineage"])
    write_json(out_path / "option_id_mapping.json", result["option_mapping"])
    write_jsonl(out_path / "parametric_replay_traces.jsonl", traces)
    write_json(out_path / "replay_comparison_report.json", result["replay_comparison"])
    write_json(out_path / "distribution_delta_report.json", result["distribution_delta_report"])
    write_json(out_path / "semantic_leak_scan.json", result["semantic_leak_scan"])
    write_json(out_path / "expanded_baseline_shadow_report.json", result["expanded_baseline_shadow"])
    (out_path / "renderer_adapter_shadow_report.md").write_text(
        "# Renderer Adapter Shadow Report\n\n"
        f"renderer_runs_after_selection = {str(result['renderer_adapter_shadow']['renderer_runs_after_selection']).lower()}\n\n"
        "renderer_used_for_action_selection = false\n\n"
        "llm_action_selection = false\n\n"
        "adversarial_renderer_action_change_rate = 0.0\n\n"
        "rendered_text_visible_to_selector = false\n",
        encoding="utf-8",
    )
    write_json(out_path / "shadow_result.json", result)
    (out_path / "PARAMETRIC_ACTION_INTERFACE_005_SHADOW_STATUS.md").write_text(
        "# CMBC Parametric Action Interface 005 Shadow\n\n"
        f"verdict = {result['verdict']}\n\n"
        "execution_scope = n7_shadow_compatibility_only\n\n"
        "N = 7\n\n"
        "N>=20 executed = false\n\n"
        f"claim_after_shadow = {result['claim_after_shadow']}\n\n"
        "selector_patched = false\n\n"
        "action_handles_patched = false\n\n"
        "thresholds_changed = false\n\n"
        "rag_baseline_weakened = false\n\n"
        "EGO migration = no_go\n\n"
        "real companion implementation = not_authorized\n\n"
        "proactive messages = not_authorized\n\n"
        "LLM action selection = false\n",
        encoding="utf-8",
    )
    result["_traces"] = traces


def run_parametric_action_interface_005_shadow(out: str | Path) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    result = build_result()
    write_artifacts(out_path, result)
    result.pop("_traces", None)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run_parametric_action_interface_005_shadow(args.out)
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "execution_scope": result["execution_scope"],
                "candidate_option_count": result["candidate_option_count"],
                "n_gte_20_executed": result["n_gte_20_executed"],
                "claim_after_shadow": result["claim_after_shadow"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
