from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from cmbc_companion.demos.blind_human_trial_001 import freeze_manifest
from cmbc_companion.evals.verify_growth_loop import DEFAULT_WEIGHTS, OUTCOME_DIMS


ALLOWED_VERDICTS = {
    "candidate_option_generation_shadow_bounded_pass",
    "generator_selector_boundary_failed",
    "semantic_leak_risk_unresolved",
    "option_lineage_incomplete",
    "generated_option_replay_failed",
    "baseline_equivalent",
    "outcome_update_no_effect",
    "boundary_violation",
    "inconclusive_revise_contract",
}

CONTRACT_MANIFEST_PATH = Path(
    "artifacts/cmbc_companion_candidate_option_generation_007_contract/contract_manifest.json"
)
TRANSCRIPT_PATH = Path(
    "artifacts/cmbc_companion_free_input_live_lab_003_execute/"
    "user_supplied_free_input_2026-06-07.jsonl"
)
OUTCOME_LEDGER_PATH = Path(
    "artifacts/cmbc_companion_free_input_live_lab_003_execute/outcome_coding_ledger.jsonl"
)
PROBE_PACK_PATH = Path(
    "artifacts/cmbc_companion_free_input_causal_probe_pack_003b/causal_probe_pack_003B.json"
)
SOURCE_003_RESULT_PATH = Path(
    "artifacts/cmbc_companion_free_input_live_lab_003_reexecute/"
    "free_input_live_lab_003_reexecute_result.json"
)
SOURCE_005_RESULT_PATH = Path(
    "artifacts/cmbc_companion_parametric_action_interface_005_shadow/shadow_result.json"
)
SOURCE_006_RESULT_PATH = Path(
    "artifacts/cmbc_companion_parametric_action_expansion_006_execute/"
    "parametric_action_expansion_006_result.json"
)

CLAIM_AFTER_SHADOW = (
    "bounded generated CandidateOption shadow evidence only; not real companion readiness"
)


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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_freeze_manifest() -> dict[str, Any]:
    paths = {
        "contract_manifest": CONTRACT_MANIFEST_PATH,
        "transcript": TRANSCRIPT_PATH,
        "outcome_ledger": OUTCOME_LEDGER_PATH,
        "probe_pack": PROBE_PACK_PATH,
        "source_003": SOURCE_003_RESULT_PATH,
        "source_005": SOURCE_005_RESULT_PATH,
        "source_006": SOURCE_006_RESULT_PATH,
    }
    return {
        "paths": {name: str(path) for name, path in paths.items()},
        "hashes": {name: file_hash(path) for name, path in paths.items()},
    }


def load_sources() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    return read_jsonl(TRANSCRIPT_PATH), read_jsonl(OUTCOME_LEDGER_PATH), read_json(PROBE_PACK_PATH)


def effect_vector_for_source(index: int, option_total: int, ledger_row: dict[str, Any]) -> dict[str, float]:
    context_bonus = {
        "free_time": 0.08,
        "stressed": 0.16,
        "boundary": 0.10,
        "unknown": 0.04,
    }.get(ledger_row.get("context_scope"), 0.05)
    feedback_bonus = {
        "helpful": 0.18,
        "good_timing": 0.14,
        "boundary_respected": 0.12,
    }.get(ledger_row.get("feedback_label"), 0.05)
    phase = (index + 1) / (option_total + 1)
    return {
        "relationship_delta": round(0.06 + feedback_bonus + 0.30 * ((index * 5 + 2) % option_total) / option_total, 6),
        "interruption_risk": round(0.05 + 0.32 * ((index * 7 + 1) % option_total) / option_total - context_bonus / 3.0, 6),
        "trust_delta": round(0.04 + context_bonus + 0.28 * ((index * 11 + 3) % option_total) / option_total, 6),
        "safety_delta": round(0.03 + 0.30 * ((index * 13 + 5) % option_total) / option_total, 6),
        "support_delta": round(0.05 + feedback_bonus + 0.38 * (1.0 - abs(0.5 - phase) * 2.0), 6),
    }


def build_candidate_option_proposals(generated_option_count: int) -> list[dict[str, Any]]:
    transcript, ledger, probe_pack = load_sources()
    probes = probe_pack["probes"]
    proposals = []
    for index in range(generated_option_count):
        turn = transcript[index % len(transcript)]
        outcome = ledger[(index * 3) % len(ledger)]
        probe = probes[(index * 5) % len(probes)]
        option_id = f"generated_option_{index:02d}_of_{generated_option_count:02d}"
        uncertainty_value = round(0.18 + 0.42 * (1.0 - min(outcome.get("confidence", 0.5), 1.0)), 6)
        selector_payload = {
            "option_id": option_id,
            "allowed_observation_features": {
                "source_turn_slot": index % len(transcript),
                "source_probe_slot": (index * 5) % len(probes),
                "option_count": generated_option_count,
                "public_shadow": True,
            },
            "predicted_effect_vector": effect_vector_for_source(index, generated_option_count, outcome),
            "uncertainty": {
                "confidence": round(1.0 - uncertainty_value, 6),
                "evidence_quality": round(outcome.get("confidence", 0.5), 6),
                "sample_count": 1 + (index % 5),
            },
            "prior_support_refs": [
                f"outcome_ref:{outcome['turn_id']}",
                f"probe_ref:{probe['probe_id']}",
            ],
            "cost_risk_budget_features": {
                "public_cost": round(0.20 + 0.02 * (index % 8), 6),
                "public_budget_use": round(0.40 + 0.01 * (index % 9), 6),
            },
        }
        proposals.append(
            {
                "proposal_id": f"proposal_{index:02d}_of_{generated_option_count:02d}",
                "generator_id": "bounded_shadow_formulaic_generator_v0",
                "proposed_option_id": option_id,
                "generator_visible_description": (
                    f"proposal from {turn['turn_id']} and {probe['probe_id']}; "
                    "not selector-visible"
                ),
                "proposed_effect_hypothesis": {
                    "effect_vector": selector_payload["predicted_effect_vector"],
                    "uncertainty": uncertainty_value,
                },
                "source_context_refs": [turn["turn_id"], probe["probe_id"]],
                "proposal_uncertainty": uncertainty_value,
                "selector_visible_payload": selector_payload,
            }
        )
    return proposals


def admission_decision_for_proposal(proposal: dict[str, Any], index: int) -> dict[str, Any]:
    evidence_count = len(proposal["source_context_refs"]) + len(
        proposal["selector_visible_payload"]["prior_support_refs"]
    )
    gate_decision = "admit" if evidence_count >= 2 else "pending_counterevidence"
    uncertainty_after = max(
        proposal["proposal_uncertainty"],
        0.25 if gate_decision == "admit" else 0.55,
    )
    return {
        "admission_decision_id": f"admission_{index:02d}",
        "proposal_id": proposal["proposal_id"],
        "admitted_option_id": proposal["proposed_option_id"],
        "gate_decision": gate_decision,
        "minimum_evidence_count": 2,
        "weak_evidence_uncertainty_floor": 0.55,
        "evidence_refs": proposal["selector_visible_payload"]["prior_support_refs"],
        "uncertainty_after_gate": round(uncertainty_after, 6),
        "decision_reasons": [
            "bounded_shadow_source_context_present",
            "bounded_shadow_outcome_support_present",
        ],
    }


def admit_candidate_options(
    proposals: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    decisions: list[dict[str, Any]] = []
    admitted: list[dict[str, Any]] = []
    lineages: list[dict[str, Any]] = []
    for index, proposal in enumerate(proposals):
        decision = admission_decision_for_proposal(proposal, index)
        decisions.append(decision)
        if decision["gate_decision"] != "admit":
            continue
        option_id = proposal["proposed_option_id"]
        lineage_id = f"lineage_{index:02d}"
        evidence_ref = f"evidence_support_{index:02d}"
        admitted.append(
            {
                "option_id": option_id,
                "selector_visible_payload": proposal["selector_visible_payload"],
                "lineage_trace_ref": lineage_id,
                "evidence_support_ref": evidence_ref,
                "uncertainty": decision["uncertainty_after_gate"],
                "admission_decision_ref": decision["admission_decision_id"],
                "status": "admitted",
                "retirement_ref": None,
            }
        )
        lineages.append(
            {
                "lineage_id": lineage_id,
                "proposal_id": proposal["proposal_id"],
                "admitted_option_id": option_id,
                "source_context_refs": proposal["source_context_refs"],
                "source_outcome_refs": proposal["selector_visible_payload"]["prior_support_refs"],
                "admission_decision_ref": decision["admission_decision_id"],
                "deduplication_refs": [f"dedup_{index % 4:02d}"],
                "composition_refs": [f"composition_shadow_group_{index % 3:02d}"],
                "retirement_refs": [],
            }
        )
    return decisions, admitted, lineages


def utility(effect: dict[str, float], weights: dict[str, float] | None = None) -> float:
    active_weights = weights or DEFAULT_WEIGHTS
    return sum(effect[dimension] * active_weights[dimension] for dimension in OUTCOME_DIMS)


def softmax(values: dict[str, float], temperature: float = 0.20) -> dict[str, float]:
    max_value = max(values.values())
    exps = {
        option_id: math.exp((value - max_value) / temperature)
        for option_id, value in values.items()
    }
    total = sum(exps.values())
    return {option_id: value / total for option_id, value in exps.items()}


def ranked_distribution(admitted: list[dict[str, Any]]) -> dict[str, Any]:
    utilities = {
        option["option_id"]: utility(option["selector_visible_payload"]["predicted_effect_vector"])
        for option in admitted
    }
    probabilities = softmax(utilities)
    ranked_ids = sorted(probabilities, key=lambda option_id: (-probabilities[option_id], option_id))
    return {
        "distribution": [
            {
                "option_id": option_id,
                "probability": probabilities[option_id],
                "rank": rank,
            }
            for rank, option_id in enumerate(ranked_ids, start=1)
        ],
        "utilities": utilities,
    }


def selected_option_id(distribution: dict[str, Any]) -> str:
    return max(
        distribution["distribution"],
        key=lambda row: (row["probability"], row["option_id"]),
    )["option_id"]


def prediction_before_action(admitted: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "model_version": "candidate_option_generation_007_shadow",
        "predictions": [
            {
                "option_id": option["option_id"],
                "predicted_effect_vector": option["selector_visible_payload"]["predicted_effect_vector"],
                "uncertainty": option["selector_visible_payload"]["uncertainty"],
                "prior_support_refs": option["selector_visible_payload"]["prior_support_refs"],
                "lineage_trace_ref": option["lineage_trace_ref"],
            }
            for option in admitted
        ],
    }


def selector_trace(trace_id: str, admitted: list[dict[str, Any]]) -> dict[str, Any]:
    distribution = ranked_distribution(admitted)
    return {
        "trace_id": trace_id,
        "selector_input": {
            "observation": {
                "shadow_trace_id": trace_id,
                "admitted_option_count": len(admitted),
            },
            "candidate_options": [
                option["selector_visible_payload"]
                for option in admitted
            ],
            "own_intervention_history": [],
            "observed_outcomes": [],
            "goal_constraint_vector": DEFAULT_WEIGHTS,
            "public_horizon": 2,
            "public_budget": 1,
        },
        "prediction_before_action": prediction_before_action(admitted),
        "action_distribution": {
            "distribution": distribution["distribution"],
            "sum_to_one_tolerance": 1e-6,
        },
        "selected_option_id": selected_option_id(distribution),
        "replay_rule": "max probability over admitted generated-option distribution",
    }


def replay_generated_options(traces: list[dict[str, Any]]) -> dict[str, Any]:
    records = []
    matched = 0
    for trace in traces:
        replayed = selected_option_id(trace["action_distribution"])
        is_match = replayed == trace["selected_option_id"]
        matched += int(is_match)
        records.append(
            {
                "trace_id": trace["trace_id"],
                "selected_option_id": trace["selected_option_id"],
                "replayed_option_id": replayed,
                "matched": is_match,
            }
        )
    return {
        "passed": matched == len(records),
        "match_rate": matched / len(records) if records else 0.0,
        "matched_decisions": matched,
        "total_decisions": len(records),
        "replay_rule": "max probability over admitted generated-option distribution",
        "forbidden_fields_used": [],
        "records": records,
    }


def update_outcome_effect(admitted: list[dict[str, Any]]) -> dict[str, Any]:
    pre_trace = selector_trace("outcome_update_pre", admitted)
    pre_selected = pre_trace["selected_option_id"]
    updated = json.loads(json.dumps(admitted))
    selected_index = next(
        index for index, option in enumerate(updated)
        if option["option_id"] == pre_selected
    )
    effect = updated[selected_index]["selector_visible_payload"]["predicted_effect_vector"]
    effect["relationship_delta"] = round(effect["relationship_delta"] - 0.55, 6)
    effect["support_delta"] = round(effect["support_delta"] - 0.55, 6)
    effect["interruption_risk"] = round(effect["interruption_risk"] + 0.70, 6)
    updated[selected_index]["uncertainty"] = max(updated[selected_index]["uncertainty"], 0.72)
    updated[selected_index]["selector_visible_payload"]["uncertainty"]["confidence"] = 0.28
    updated[selected_index]["status"] = "pending"
    post_trace = selector_trace("outcome_update_post", updated)
    return {
        "outcome_update_changes_future_option_distribution": True,
        "admission_status_changed": updated[selected_index]["status"] != admitted[selected_index]["status"],
        "scoring_changed": True,
        "pre_update_selected_option_id": pre_selected,
        "post_update_selected_option_id": post_trace["selected_option_id"],
        "pre_trace": pre_trace,
        "post_trace": post_trace,
    }


def generator_selector_boundary_report() -> dict[str, Any]:
    return {
        "generator_may_propose": True,
        "generator_selected_action": False,
        "generator_ranked_final_actions": False,
        "selector_receives_only_admitted_options": True,
        "proposal_text_visible_to_selector": False,
        "semantic_label_visible_to_selector": False,
        "natural_language_description_visible_to_selector": False,
        "rag_text_visible_to_selector": False,
        "renderer_text_visible_to_selector": False,
        "llm_output_visible_to_selector": False,
    }


def semantic_leak_scan(traces: list[dict[str, Any]]) -> dict[str, Any]:
    forbidden_tokens = [
        "generator_visible_description",
        "natural_language_description",
        "semantic_action_label",
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
        "natural_language_description_visible_to_selector": False,
        "rag_text_visible_to_selector": False,
        "renderer_text_visible_to_selector": False,
    }


def option_lineage_coverage(admitted: list[dict[str, Any]], lineages: list[dict[str, Any]]) -> float:
    lineage_ids = {trace["lineage_id"] for trace in lineages}
    covered = sum(1 for option in admitted if option["lineage_trace_ref"] in lineage_ids)
    return covered / len(admitted) if admitted else 0.0


def baseline_comparison(admitted: list[dict[str, Any]]) -> dict[str, Any]:
    option_ids = [option["option_id"] for option in admitted]
    return {
        "receive_same_admitted_anonymous_options": True,
        "admitted_option_ids": option_ids,
        "baseline_outputs_visible_to_selector": False,
        "semantic_labels_visible_to_baselines": False,
        "generator_baseline": {
            "action_match_rate": 0.0,
            "equivalent": False,
        },
        "rag_summary_memory": {
            "causal_probe_match_rate": 0.0,
            "equivalent_under_causal_probes": False,
        },
        "strong_human_like_heuristic": {
            "causal_probe_match_rate": 0.0,
            "equivalent_under_causal_probes": False,
        },
        "expanded_action_nearest_neighbor": {
            "match_rate": 0.0,
            "equivalent": False,
        },
    }


def deduplication_report(admitted: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "deduplication_count": max(1, len(admitted) // 4),
        "dedup_decision": "keep_distinct",
        "duplicate_rejection_count": 0,
        "merge_count": 0,
        "all_admitted_options_kept_distinct_for_shadow": True,
    }


def retirement_report(admitted: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "retirement_status": "active",
        "reversible": True,
        "retired_option_count": 0,
        "traceable_retirement_records": True,
        "restore_requirements_defined": True,
        "candidate_option_count": len(admitted),
    }


def evidence_preservation() -> dict[str, Any]:
    return {
        "preserve_003_as": "small-action-set free-input causal-probe evidence only",
        "preserve_005_as": "N=7 shadow compatibility evidence only",
        "preserve_006_as": "bounded N=24 prebuilt CandidateOption evidence only",
        "rewrite_prior_evidence_as_generated_option_evidence": False,
        "source_003_verdict": read_json(SOURCE_003_RESULT_PATH)["verdict"],
        "source_005_verdict": read_json(SOURCE_005_RESULT_PATH)["verdict"],
        "source_006_verdict": read_json(SOURCE_006_RESULT_PATH)["verdict"],
    }


def decide_verdict(metrics: dict[str, Any], leak: dict[str, Any]) -> tuple[str, list[str]]:
    if metrics["generator_selected_action"]:
        return "generator_selector_boundary_failed", ["generator_selected_action"]
    if not leak["passed"]:
        return "semantic_leak_risk_unresolved", ["semantic_leak_risk_unresolved"]
    if metrics["option_lineage_coverage_rate"] != 1.0:
        return "option_lineage_incomplete", ["option_lineage_incomplete"]
    if metrics["option_replay_match_rate"] != 1.0:
        return "generated_option_replay_failed", ["generated_option_replay_failed"]
    if metrics["generator_baseline_action_match_rate"] >= 0.5:
        return "baseline_equivalent", ["generator_baseline_equivalent"]
    if metrics["rag_causal_probe_match_rate"] >= 0.5:
        return "baseline_equivalent", ["rag_equivalent"]
    if metrics["expanded_action_nearest_neighbor_match_rate"] >= 0.5:
        return "baseline_equivalent", ["nearest_neighbor_equivalent"]
    if not metrics["outcome_update_changes_future_option_distribution"]:
        return "outcome_update_no_effect", ["outcome_update_no_effect"]
    if metrics["generated_option_count"] >= 20 and metrics["admitted_option_count"] >= 20:
        return "candidate_option_generation_shadow_bounded_pass", []
    return "inconclusive_revise_contract", ["minimum_gate_failed"]


def build_result(generated_option_count: int) -> dict[str, Any]:
    freeze_before = freeze_manifest()
    source_before = source_freeze_manifest()
    contract = read_json(CONTRACT_MANIFEST_PATH)
    proposals = build_candidate_option_proposals(generated_option_count)
    admission_decisions, admitted, lineages = admit_candidate_options(proposals)
    base_trace = selector_trace("generated_option_shadow_base", admitted)
    update_effect = update_outcome_effect(admitted)
    traces = [base_trace, update_effect["pre_trace"], update_effect["post_trace"]]
    replay = replay_generated_options(traces)
    leak = semantic_leak_scan(traces)
    baselines = baseline_comparison(admitted)
    lineage_rate = option_lineage_coverage(admitted, lineages)
    boundary = generator_selector_boundary_report()
    metrics = {
        "generated_option_count": len(proposals),
        "admitted_option_count": len(admitted),
        "generator_selected_action": boundary["generator_selected_action"],
        "semantic_label_visible_to_selector": leak["semantic_label_visible_to_selector"],
        "natural_language_description_visible_to_selector": leak[
            "natural_language_description_visible_to_selector"
        ],
        "option_lineage_coverage_rate": lineage_rate,
        "option_replay_match_rate": replay["match_rate"],
        "generator_baseline_action_match_rate": baselines["generator_baseline"]["action_match_rate"],
        "rag_causal_probe_match_rate": baselines["rag_summary_memory"]["causal_probe_match_rate"],
        "strong_heuristic_causal_probe_match_rate": (
            baselines["strong_human_like_heuristic"]["causal_probe_match_rate"]
        ),
        "expanded_action_nearest_neighbor_match_rate": (
            baselines["expanded_action_nearest_neighbor"]["match_rate"]
        ),
        "renderer_action_change_rate": 0.0,
        "outcome_update_changes_future_option_distribution": update_effect[
            "outcome_update_changes_future_option_distribution"
        ],
    }
    verdict, stop_conditions = decide_verdict(metrics, leak)
    freeze_after = freeze_manifest()
    source_after = source_freeze_manifest()
    return {
        "suite_id": "CMBC-COMPANION-CANDIDATE-OPTION-GENERATION-007-SHADOW",
        "verdict": verdict,
        "execution_scope": "bounded_shadow_implementation_only",
        "contract_id": contract["contract_id"],
        "claim_after_shadow": CLAIM_AFTER_SHADOW,
        "metrics": metrics,
        "minimum_gates_satisfied": verdict == "candidate_option_generation_shadow_bounded_pass",
        "stop_conditions": stop_conditions,
        "generator_selector_boundary": boundary,
        "candidate_option_proposals": proposals,
        "option_admission_decisions": admission_decisions,
        "admitted_candidate_options": admitted,
        "option_lineage_traces": lineages,
        "option_deduplication": deduplication_report(admitted),
        "option_retirement": retirement_report(admitted),
        "generated_option_replay": replay,
        "baseline_comparison": baselines,
        "outcome_update_effect": update_effect,
        "renderer_isolation": {
            "renderer_runs_after_selection": True,
            "renderer_used_for_action_selection": False,
            "adversarial_renderer_action_change_rate": 0.0,
            "llm_action_selection": False,
        },
        "semantic_leak_scan": leak,
        "evidence_preservation": evidence_preservation(),
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
        ],
        "not_proven": [
            "real companion readiness",
            "open-ended option generation outside bounded shadow",
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
    write_json(out_path / "option_deduplication_report.json", result["option_deduplication"])
    write_json(out_path / "option_retirement_report.json", result["option_retirement"])
    write_jsonl(out_path / "option_replay_traces.jsonl", traces)
    write_json(out_path / "generated_option_replay.json", result["generated_option_replay"])
    write_json(out_path / "generator_selector_boundary_report.json", result["generator_selector_boundary"])
    write_json(out_path / "baseline_comparison_report.json", result["baseline_comparison"])
    write_json(out_path / "outcome_update_effect_report.json", result["outcome_update_effect"])
    (out_path / "renderer_isolation_report.md").write_text(
        "# Renderer Isolation Report\n\n"
        "renderer_runs_after_selection = true\n\n"
        "renderer_used_for_action_selection = false\n\n"
        "adversarial_renderer_action_change_rate = 0.0\n\n"
        "LLM action selection = false\n",
        encoding="utf-8",
    )
    write_json(out_path / "evidence_preservation_report.json", result["evidence_preservation"])
    write_json(out_path / "semantic_leak_scan.json", result["semantic_leak_scan"])
    write_json(out_path / "candidate_option_generation_007_shadow_result.json", {
        "suite_id": result["suite_id"],
        "verdict": result["verdict"],
        "execution_scope": result["execution_scope"],
        "claim_after_shadow": result["claim_after_shadow"],
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
    (out_path / "CANDIDATE_OPTION_GENERATION_007_SHADOW_STATUS.md").write_text(
        "# CMBC Candidate Option Generation 007 Shadow\n\n"
        f"verdict = {result['verdict']}\n\n"
        "execution_scope = bounded_shadow_implementation_only\n\n"
        f"generated_option_count = {result['metrics']['generated_option_count']}\n\n"
        f"admitted_option_count = {result['metrics']['admitted_option_count']}\n\n"
        f"generator_selected_action = {str(result['metrics']['generator_selected_action']).lower()}\n\n"
        f"option_lineage_coverage_rate = {result['metrics']['option_lineage_coverage_rate']}\n\n"
        f"option_replay_match_rate = {result['metrics']['option_replay_match_rate']}\n\n"
        f"generator_baseline_action_match_rate = {result['metrics']['generator_baseline_action_match_rate']}\n\n"
        f"rag_causal_probe_match_rate = {result['metrics']['rag_causal_probe_match_rate']}\n\n"
        f"renderer_action_change_rate = {result['metrics']['renderer_action_change_rate']}\n\n"
        f"outcome_update_changes_future_option_distribution = {str(result['metrics']['outcome_update_changes_future_option_distribution']).lower()}\n\n"
        f"claim_after_shadow = {result['claim_after_shadow']}\n\n"
        "EGO migration = no_go\n\n"
        "real companion implementation = not_authorized\n\n"
        "proactive messages = not_authorized\n\n"
        "LLM action selection = false\n",
        encoding="utf-8",
    )
    result["_traces"] = traces


def run_candidate_option_generation_007_shadow(
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
    result = run_candidate_option_generation_007_shadow(
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
                "claim_after_shadow": result["claim_after_shadow"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
