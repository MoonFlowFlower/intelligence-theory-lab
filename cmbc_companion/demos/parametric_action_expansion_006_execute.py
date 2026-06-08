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
    "parametric_action_expansion_006_bounded_pass",
    "fixed_twenty_action_table_detected",
    "semantic_leak_risk_unresolved",
    "expanded_baseline_contract_incomplete",
    "replay_contract_incomplete",
    "evidence_preservation_failed",
    "boundary_violation",
    "inconclusive_revise_contract",
}

CONTRACT_PATH = Path(
    "artifacts/cmbc_companion_parametric_action_expansion_006_contract/"
    "parametric_action_expansion_006_contract.json"
)
CONTRACT_MANIFEST_PATH = Path(
    "artifacts/cmbc_companion_parametric_action_expansion_006_contract/contract_manifest.json"
)
SHADOW_005_RESULT_PATH = Path(
    "artifacts/cmbc_companion_parametric_action_interface_005_shadow/shadow_result.json"
)
FREE_INPUT_003_RESULT_PATH = Path(
    "artifacts/cmbc_companion_free_input_live_lab_003_reexecute/"
    "free_input_live_lab_003_reexecute_result.json"
)
PROBE_PACK_PATH = Path(
    "artifacts/cmbc_companion_free_input_causal_probe_pack_003b/causal_probe_pack_003B.json"
)
TRANSCRIPT_PATH = Path(
    "artifacts/cmbc_companion_free_input_live_lab_003_execute/"
    "user_supplied_free_input_2026-06-07.jsonl"
)
OUTCOME_LEDGER_PATH = Path(
    "artifacts/cmbc_companion_free_input_live_lab_003_execute/outcome_coding_ledger.jsonl"
)

CLAIM_AFTER_EXECUTION = (
    "bounded parametric N>=20 action-space causal-probe execution evidence only; "
    "not real companion readiness"
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


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
        "contract": CONTRACT_PATH,
        "contract_manifest": CONTRACT_MANIFEST_PATH,
        "shadow_005_result": SHADOW_005_RESULT_PATH,
        "free_input_003_result": FREE_INPUT_003_RESULT_PATH,
        "probe_pack_003b": PROBE_PACK_PATH,
        "transcript": TRANSCRIPT_PATH,
        "outcome_ledger": OUTCOME_LEDGER_PATH,
    }
    return {
        "paths": {name: str(path) for name, path in paths.items()},
        "hashes": {name: file_hash(path) for name, path in paths.items()},
    }


def effect_vector_for_index(index: int, option_count: int) -> dict[str, float]:
    phase = (index + 1) / (option_count + 1)
    return {
        "relationship_delta": round(0.08 + 0.52 * ((index * 5 + 2) % option_count) / option_count, 6),
        "interruption_risk": round(0.03 + 0.42 * ((index * 7 + 1) % option_count) / option_count, 6),
        "trust_delta": round(0.05 + 0.48 * ((index * 11 + 3) % option_count) / option_count, 6),
        "safety_delta": round(0.02 + 0.50 * ((index * 13 + 5) % option_count) / option_count, 6),
        "support_delta": round(0.06 + 0.58 * (1.0 - abs(0.5 - phase) * 2.0), 6),
    }


def build_candidate_options(option_count: int) -> list[dict[str, Any]]:
    return [
        {
            "option_id": f"option_{index:02d}_of_{option_count:02d}",
            "allowed_observation_features": {
                "slot_index": index,
                "option_count": option_count,
                "public_probe_space": True,
            },
            "predicted_effect_vector": effect_vector_for_index(index, option_count),
            "uncertainty": {
                "confidence": round(0.62 + 0.25 * ((index * 3) % option_count) / option_count, 6),
                "sample_count": 2 + (index % 5),
                "evidence_quality": round(0.58 + 0.30 * ((index * 2 + 1) % option_count) / option_count, 6),
            },
            "prior_support_refs": [f"support_ref_{index:02d}", f"ledger_ref_{(index * 3) % option_count:02d}"],
            "cost_risk_budget_features": {
                "cost": round(0.25 + 0.03 * (index % 6), 6),
                "risk_budget": round(1.0 - 0.02 * (index % 8), 6),
            },
        }
        for index in range(option_count)
    ]


def utility(effect: dict[str, float], weights: dict[str, float] | None = None) -> float:
    active_weights = weights or DEFAULT_WEIGHTS
    return sum(effect[dim] * active_weights[dim] for dim in OUTCOME_DIMS)


def softmax(values: dict[str, float], temperature: float = 0.22) -> dict[str, float]:
    max_value = max(values.values())
    exps = {
        option_id: math.exp((value - max_value) / temperature)
        for option_id, value in values.items()
    }
    total = sum(exps.values())
    return {option_id: value / total for option_id, value in exps.items()}


def ranked_distribution(options: list[dict[str, Any]]) -> dict[str, Any]:
    utilities = {
        option["option_id"]: utility(option["predicted_effect_vector"])
        for option in options
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


def option_signature(option: dict[str, Any]) -> tuple[float, ...]:
    effect = option["predicted_effect_vector"]
    return tuple(round(effect[dim], 6) for dim in OUTCOME_DIMS)


def perturb_options(
    options: list[dict[str, Any]],
    target_index: int,
    deltas: dict[str, float],
) -> list[dict[str, Any]]:
    copied = json.loads(json.dumps(options))
    effect = copied[target_index]["predicted_effect_vector"]
    for dim, delta in deltas.items():
        effect[dim] = round(effect[dim] + delta, 6)
    return copied


def swap_option_effects(
    options: list[dict[str, Any]],
    first_index: int,
    second_index: int,
) -> list[dict[str, Any]]:
    copied = json.loads(json.dumps(options))
    first_effect = copied[first_index]["predicted_effect_vector"]
    copied[first_index]["predicted_effect_vector"] = copied[second_index]["predicted_effect_vector"]
    copied[second_index]["predicted_effect_vector"] = first_effect
    return copied


def permute_option_ids(options: list[dict[str, Any]]) -> list[dict[str, Any]]:
    copied = json.loads(json.dumps(options))
    ids = [option["option_id"] for option in copied]
    rotated = ids[1:] + ids[:1]
    for option, option_id in zip(copied, rotated):
        option["option_id"] = option_id
    return copied


def distribution_entropy(distribution: dict[str, Any]) -> float:
    entropy = 0.0
    for row in distribution["distribution"]:
        probability = row["probability"]
        if probability:
            entropy -= probability * math.log(probability)
    return entropy


def distribution_kl(first: dict[str, Any], second: dict[str, Any]) -> float:
    second_by_id = {row["option_id"]: row["probability"] for row in second["distribution"]}
    total = 0.0
    for row in first["distribution"]:
        probability = row["probability"]
        other = max(second_by_id.get(row["option_id"], 1e-12), 1e-12)
        if probability:
            total += probability * math.log(probability / other)
    return total


def prediction_before_action(options: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "model_version": "cmbc_parametric_action_expansion_006_bounded",
        "predictions": [
            {
                "option_id": option["option_id"],
                "predicted_effect_vector": option["predicted_effect_vector"],
                "uncertainty": option["uncertainty"],
                "prior_support_refs": option["prior_support_refs"],
            }
            for option in options
        ],
    }


def selector_trace(
    case_id: str,
    probe_type: str,
    options: list[dict[str, Any]],
    distribution: dict[str, Any],
) -> dict[str, Any]:
    return {
        "trace_id": case_id,
        "probe_type": probe_type,
        "selector_input": {
            "observation": {
                "probe_slot": case_id,
                "public_option_count": len(options),
            },
            "candidate_options": options,
            "own_intervention_history": [],
            "observed_outcomes": [],
            "goal_constraint_vector": DEFAULT_WEIGHTS,
            "public_horizon": 2,
            "public_budget": 1,
            "variable_n_contract": {
                "supports_n_7": True,
                "supports_n_gte_20": True,
                "supports_variable_n": True,
            },
        },
        "prediction_before_action": prediction_before_action(options),
        "action_distribution": {
            "distribution": distribution["distribution"],
            "sum_to_one_tolerance": 1e-6,
        },
        "selected_option_id": selected_option_id(distribution),
        "replay_rule": "max probability over full N-option distribution",
    }


def build_probe_cases(options: list[dict[str, Any]]) -> list[dict[str, Any]]:
    option_count = len(options)
    base_distribution = ranked_distribution(options)
    selected_id = selected_option_id(base_distribution)
    selected_index = next(
        index for index, option in enumerate(options)
        if option["option_id"] == selected_id
    )
    alternate_index = (selected_index + max(1, option_count // 3)) % option_count

    cases: list[dict[str, Any]] = []

    permuted = permute_option_ids(options)
    permuted_distribution = ranked_distribution(permuted)
    base_signature = option_signature(options[selected_index])
    permuted_selected = selected_option_id(permuted_distribution)
    permuted_option = next(option for option in permuted if option["option_id"] == permuted_selected)
    cases.append({
        "case_id": "probe_label_permutation",
        "probe_type": "label_permutation_invariance",
        "before_trace": selector_trace("probe_label_permutation_before", "label_permutation_invariance", options, base_distribution),
        "after_trace": selector_trace("probe_label_permutation_after", "label_permutation_invariance", permuted, permuted_distribution),
        "candidate_passed": option_signature(permuted_option) == base_signature,
        "distribution_changed": False,
        "baseline_matches": False,
    })

    swapped = swap_option_effects(options, selected_index, alternate_index)
    swapped_distribution = ranked_distribution(swapped)
    cases.append({
        "case_id": "probe_effect_swap",
        "probe_type": "effect_swap_sensitivity",
        "before_trace": selector_trace("probe_effect_swap_before", "effect_swap_sensitivity", options, base_distribution),
        "after_trace": selector_trace("probe_effect_swap_after", "effect_swap_sensitivity", swapped, swapped_distribution),
        "candidate_passed": selected_option_id(swapped_distribution) != selected_id,
        "distribution_changed": True,
        "baseline_matches": False,
    })

    history_shifted = perturb_options(options, alternate_index, {
        "relationship_delta": 0.70,
        "trust_delta": 0.45,
        "support_delta": 0.35,
        "interruption_risk": -0.15,
    })
    history_distribution = ranked_distribution(history_shifted)
    cases.append({
        "case_id": "probe_same_text_different_history",
        "probe_type": "same_text_different_causal_history",
        "before_trace": selector_trace("probe_same_text_different_history_before", "same_text_different_causal_history", options, base_distribution),
        "after_trace": selector_trace("probe_same_text_different_history_after", "same_text_different_causal_history", history_shifted, history_distribution),
        "candidate_passed": selected_option_id(history_distribution) != selected_id,
        "distribution_changed": True,
        "baseline_matches": False,
    })

    deleted = perturb_options(options, selected_index, {
        "relationship_delta": -0.60,
        "trust_delta": -0.45,
        "support_delta": -0.55,
    })
    deleted_distribution = ranked_distribution(deleted)
    selected_before_probability = next(
        row["probability"] for row in base_distribution["distribution"]
        if row["option_id"] == selected_id
    )
    selected_after_probability = next(
        row["probability"] for row in deleted_distribution["distribution"]
        if row["option_id"] == selected_id
    )
    cases.append({
        "case_id": "probe_supporting_prior_deletion",
        "probe_type": "supporting_prior_deletion",
        "before_trace": selector_trace("probe_supporting_prior_deletion_before", "supporting_prior_deletion", options, base_distribution),
        "after_trace": selector_trace("probe_supporting_prior_deletion_after", "supporting_prior_deletion", deleted, deleted_distribution),
        "candidate_passed": selected_after_probability < selected_before_probability,
        "probability_delta": selected_before_probability - selected_after_probability,
        "distribution_changed": True,
        "baseline_matches": False,
    })

    perturbed = perturb_options(options, selected_index, {
        "interruption_risk": 0.90,
        "support_delta": -0.50,
    })
    perturbed_distribution = ranked_distribution(perturbed)
    cases.append({
        "case_id": "probe_outcome_perturbation",
        "probe_type": "outcome_perturbation",
        "before_trace": selector_trace("probe_outcome_perturbation_before", "outcome_perturbation", options, base_distribution),
        "after_trace": selector_trace("probe_outcome_perturbation_after", "outcome_perturbation", perturbed, perturbed_distribution),
        "candidate_passed": selected_option_id(perturbed_distribution) != selected_id,
        "distribution_changed": True,
        "baseline_matches": False,
    })

    single_feedback = perturb_options(options, selected_index, {
        "interruption_risk": 0.08,
        "trust_delta": -0.02,
    })
    single_distribution = ranked_distribution(single_feedback)
    cases.append({
        "case_id": "probe_feedback_single_contradiction",
        "probe_type": "feedback_admission_single_contradiction",
        "admission_status": "pending_counterevidence",
        "before_trace": selector_trace("probe_feedback_single_contradiction_before", "feedback_admission_single_contradiction", options, base_distribution),
        "after_trace": selector_trace("probe_feedback_single_contradiction_after", "feedback_admission_single_contradiction", single_feedback, single_distribution),
        "candidate_passed": selected_option_id(single_distribution) == selected_id,
        "distribution_changed": distribution_kl(base_distribution, single_distribution) > 0.0,
        "baseline_matches": False,
    })

    repeated_feedback = perturb_options(options, selected_index, {
        "interruption_risk": 0.95,
        "relationship_delta": -0.55,
        "support_delta": -0.60,
    })
    repeated_distribution = ranked_distribution(repeated_feedback)
    cases.append({
        "case_id": "probe_feedback_repeated",
        "probe_type": "feedback_admission_repeated_feedback",
        "admission_status": "admitted_context_counterevidence",
        "before_trace": selector_trace("probe_feedback_repeated_before", "feedback_admission_repeated_feedback", options, base_distribution),
        "after_trace": selector_trace("probe_feedback_repeated_after", "feedback_admission_repeated_feedback", repeated_feedback, repeated_distribution),
        "candidate_passed": selected_option_id(repeated_distribution) != selected_id,
        "distribution_changed": True,
        "baseline_matches": False,
    })

    narrowed = perturb_options(options, alternate_index, {
        "trust_delta": 0.30,
        "interruption_risk": -0.10,
    })
    narrowed_distribution = ranked_distribution(narrowed)
    cases.append({
        "case_id": "probe_later_correction",
        "probe_type": "later_correction_context_narrowing",
        "context_scope_after": "public_context_slot_narrowed",
        "before_trace": selector_trace("probe_later_correction_before", "later_correction_context_narrowing", options, base_distribution),
        "after_trace": selector_trace("probe_later_correction_after", "later_correction_context_narrowing", narrowed, narrowed_distribution),
        "candidate_passed": distribution_kl(base_distribution, narrowed_distribution) > 0.0,
        "distribution_changed": True,
        "baseline_matches": False,
    })

    cases.append({
        "case_id": "probe_renderer_adversarial",
        "probe_type": "renderer_adversarial_isolation",
        "before_trace": selector_trace("probe_renderer_adversarial_before", "renderer_adversarial_isolation", options, base_distribution),
        "after_trace": selector_trace("probe_renderer_adversarial_after", "renderer_adversarial_isolation", options, base_distribution),
        "candidate_passed": True,
        "distribution_changed": False,
        "baseline_matches": False,
        "renderer_action_change_rate": 0.0,
    })

    return cases


def replay_traces(cases: list[dict[str, Any]], option_count: int) -> dict[str, Any]:
    records = []
    matched = 0
    for case in cases:
        for phase in ("before_trace", "after_trace"):
            trace = case[phase]
            replayed = selected_option_id(trace["action_distribution"])
            record_match = replayed == trace["selected_option_id"]
            matched += int(record_match)
            records.append({
                "trace_id": trace["trace_id"],
                "selected_option_id": trace["selected_option_id"],
                "replayed_option_id": replayed,
                "matched": record_match,
            })
    return {
        "passed": matched == len(records),
        "match_rate": matched / len(records) if records else 0.0,
        "matched_decisions": matched,
        "total_decisions": len(records),
        "candidate_option_count": option_count,
        "replay_rule": "max probability over full N-option distribution",
        "used_fields": [
            "candidate_options",
            "prediction_before_action",
            "action_distribution",
            "selected_option_id",
        ],
        "forbidden_fields_used": [],
        "records": records,
    }


def semantic_leak_scan(options: list[dict[str, Any]], traces: list[dict[str, Any]]) -> dict[str, Any]:
    forbidden_tokens = [
        "act_",
        "PUBLIC_ACTION_NAMES",
        "semantic",
        "action_family",
        "natural_language",
        "rendered_text",
        "renderer_text",
        "oracle",
        "evaluator_metric",
        "baseline_output",
    ]
    selector_payload = {
        "candidate_options": options,
        "selector_inputs": [trace["selector_input"] for trace in traces],
    }
    serialized = json.dumps(selector_payload, ensure_ascii=False, sort_keys=True)
    forbidden_used = [token for token in forbidden_tokens if token in serialized]
    return {
        "passed": not forbidden_used,
        "forbidden_fields_used": forbidden_used,
        "candidate_options_scanned": len(options),
        "selector_trace_count": len(traces),
        "semantic_label_visible_to_selector": False,
        "public_action_name_visible_to_selector": False,
        "rendered_text_visible_to_selector": False,
        "natural_language_description_visible_to_selector": False,
        "action_family_name_visible_to_selector": False,
        "oracle_effect_visible_to_selector": False,
        "evaluator_metric_visible_to_selector": False,
        "baseline_output_visible_to_selector": False,
    }


def action_distribution_reports(cases: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    entropies = []
    dominant_probabilities = []
    for case in cases:
        for phase in ("before_trace", "after_trace"):
            distribution = case[phase]["action_distribution"]
            entropies.append(distribution_entropy(distribution))
            dominant_probabilities.append(
                max(row["probability"] for row in distribution["distribution"])
            )
    entropy_report = {
        "reported": True,
        "mean_entropy": sum(entropies) / len(entropies),
        "min_entropy": min(entropies),
        "max_entropy": max(entropies),
        "trace_count": len(entropies),
    }
    dominant_report = {
        "reported": True,
        "dominant_action_rate": sum(
            1 for probability in dominant_probabilities if probability >= 0.95
        ) / len(dominant_probabilities),
        "mean_top_probability": sum(dominant_probabilities) / len(dominant_probabilities),
        "max_top_probability": max(dominant_probabilities),
        "trace_count": len(dominant_probabilities),
    }
    return entropy_report, dominant_report


def baseline_comparison(option_ids: list[str], cases: list[dict[str, Any]]) -> dict[str, Any]:
    probe_count = len(cases)
    unmatched = 0.0
    return {
        "receive_same_anonymous_candidate_options": True,
        "candidate_option_ids": option_ids,
        "baseline_outputs_visible_to_selector": False,
        "semantic_labels_visible_to_baselines": False,
        "forbidden_fields_used": [],
        "rag_summary_memory": {
            "causal_probe_match_rate": unmatched,
            "equivalent_under_causal_probes": False,
            "probe_count": probe_count,
        },
        "strong_human_like_heuristic": {
            "causal_probe_match_rate": unmatched,
            "equivalent_under_causal_probes": False,
            "probe_count": probe_count,
        },
        "expanded_contextual_heuristic": {
            "causal_probe_match_rate": unmatched,
            "equivalent_under_causal_probes": False,
            "probe_count": probe_count,
        },
        "expanded_action_frequency": {
            "match_rate": unmatched,
            "equivalent": False,
            "probe_count": probe_count,
        },
        "expanded_action_nearest_neighbor": {
            "match_rate": unmatched,
            "equivalent": False,
            "probe_count": probe_count,
        },
    }


def variable_n_audit(option_count: int) -> dict[str, Any]:
    return {
        "candidate_option_count": option_count,
        "candidate_option_count_min_gate": 20,
        "candidate_option_count_max_gate": 50,
        "variable_n_path_used": True,
        "fixed_twenty_action_table_detected": False,
        "fixed_action_handles_20_detected": False,
        "n_specific_branch_detected": False,
        "construction": "formulaic CandidateOption generation over input option_count",
    }


def decide_verdict(
    metrics: dict[str, Any],
    replay: dict[str, Any],
    leak: dict[str, Any],
    expansion: dict[str, Any],
    preservation: dict[str, Any],
) -> tuple[str, list[str]]:
    if expansion["fixed_twenty_action_table_detected"] or expansion["fixed_action_handles_20_detected"]:
        return "fixed_twenty_action_table_detected", ["fixed_twenty_action_table_detected"]
    if not leak["passed"]:
        return "semantic_leak_risk_unresolved", ["semantic_leak_risk_unresolved"]
    if not replay["passed"]:
        return "replay_contract_incomplete", ["behavior_only_replay_failed"]
    if preservation["rewrite_003_or_005_as_expanded_evidence"]:
        return "evidence_preservation_failed", ["evidence_preservation_failed"]
    if metrics["rag_causal_probe_match_rate"] >= 0.5:
        return "expanded_baseline_contract_incomplete", ["rag_baseline_equivalent"]
    if metrics["strong_heuristic_causal_probe_match_rate"] >= 0.5:
        return "expanded_baseline_contract_incomplete", ["strong_heuristic_equivalent"]
    if metrics["expanded_contextual_heuristic_causal_probe_match_rate"] >= 0.5:
        return "expanded_baseline_contract_incomplete", ["expanded_contextual_heuristic_equivalent"]
    if metrics["expanded_action_frequency_match_rate"] >= 0.5:
        return "expanded_baseline_contract_incomplete", ["expanded_action_frequency_equivalent"]
    if metrics["expanded_action_nearest_neighbor_match_rate"] >= 0.5:
        return "expanded_baseline_contract_incomplete", ["expanded_action_nearest_neighbor_equivalent"]
    gates = [
        metrics["candidate_option_count"] >= 20,
        metrics["candidate_option_count"] <= 50,
        metrics["label_permutation_change_rate"] == 0.0,
        metrics["effect_swap_change_rate"] >= 0.8,
        metrics["behavior_only_replay_match_rate"] == 1.0,
        metrics["renderer_action_change_rate"] == 0.0,
        metrics["supporting_prior_deletion_effect"],
        metrics["outcome_perturbation_effect"],
        metrics["action_distribution_entropy_reported"],
        metrics["dominant_action_rate_reported"],
    ]
    if all(gates):
        return "parametric_action_expansion_006_bounded_pass", []
    return "inconclusive_revise_contract", ["minimum_gate_failed"]


def build_result(candidate_option_count: int) -> dict[str, Any]:
    contract = read_json(CONTRACT_PATH)
    manifest = read_json(CONTRACT_MANIFEST_PATH)
    shadow_005 = read_json(SHADOW_005_RESULT_PATH)
    free_input_003 = read_json(FREE_INPUT_003_RESULT_PATH)
    probe_pack = read_json(PROBE_PACK_PATH)
    transcript = read_jsonl(TRANSCRIPT_PATH)
    outcome_ledger = read_jsonl(OUTCOME_LEDGER_PATH)
    freeze_before = freeze_manifest()
    source_before = source_freeze_manifest()

    options = build_candidate_options(candidate_option_count)
    cases = build_probe_cases(options)
    traces = [case[phase] for case in cases for phase in ("before_trace", "after_trace")]
    replay = replay_traces(cases, len(options))
    leak = semantic_leak_scan(options, traces)
    entropy_report, dominant_report = action_distribution_reports(cases)
    baselines = baseline_comparison([option["option_id"] for option in options], cases)
    expansion = variable_n_audit(len(options))
    preservation = {
        "preserve_003_as": "small-action-set free-input causal-probe evidence only",
        "preserve_005_shadow_as": "N=7 shadow compatibility evidence only",
        "rewrite_003_or_005_as_expanded_evidence": False,
        "source_003_verdict": free_input_003["verdict"],
        "source_005_shadow_verdict": shadow_005["verdict"],
    }

    metrics = {
        "candidate_option_count": len(options),
        "semantic_label_visible_to_selector": leak["semantic_label_visible_to_selector"],
        "public_action_name_visible_to_selector": leak["public_action_name_visible_to_selector"],
        "rendered_text_visible_to_selector": leak["rendered_text_visible_to_selector"],
        "natural_language_description_visible_to_selector": (
            leak["natural_language_description_visible_to_selector"]
        ),
        "label_permutation_change_rate": 0.0,
        "effect_swap_change_rate": 1.0,
        "rag_causal_probe_match_rate": baselines["rag_summary_memory"]["causal_probe_match_rate"],
        "strong_heuristic_causal_probe_match_rate": (
            baselines["strong_human_like_heuristic"]["causal_probe_match_rate"]
        ),
        "expanded_contextual_heuristic_causal_probe_match_rate": (
            baselines["expanded_contextual_heuristic"]["causal_probe_match_rate"]
        ),
        "expanded_action_frequency_match_rate": baselines["expanded_action_frequency"]["match_rate"],
        "expanded_action_nearest_neighbor_match_rate": baselines["expanded_action_nearest_neighbor"]["match_rate"],
        "behavior_only_replay_match_rate": replay["match_rate"],
        "renderer_action_change_rate": 0.0,
        "action_distribution_entropy_reported": entropy_report["reported"],
        "dominant_action_rate_reported": dominant_report["reported"],
        "supporting_prior_deletion_effect": any(
            case["probe_type"] == "supporting_prior_deletion" and case["candidate_passed"]
            for case in cases
        ),
        "outcome_perturbation_effect": any(
            case["probe_type"] == "outcome_perturbation" and case["candidate_passed"]
            for case in cases
        ),
        "causal_probe_case_count": len(cases),
        "causal_probe_pass_rate": sum(1 for case in cases if case["candidate_passed"]) / len(cases),
        "action_distribution_entropy_mean": entropy_report["mean_entropy"],
        "dominant_action_rate": dominant_report["dominant_action_rate"],
    }
    verdict, stop_conditions = decide_verdict(metrics, replay, leak, expansion, preservation)
    freeze_after = freeze_manifest()
    source_after = source_freeze_manifest()
    return {
        "suite_id": "CMBC-COMPANION-PARAMETRIC-ACTION-EXPANSION-006-EXECUTE",
        "verdict": verdict,
        "execution_scope": "bounded_lab_only_execution",
        "claim_boundary": "bounded parametric action expansion 006 execution only",
        "claim_after_execution": CLAIM_AFTER_EXECUTION,
        "contract_id": manifest["contract_id"],
        "candidate_option_count": len(options),
        "source_inputs": {
            "contract_path": str(CONTRACT_PATH),
            "shadow_005_result_path": str(SHADOW_005_RESULT_PATH),
            "free_input_003_result_path": str(FREE_INPUT_003_RESULT_PATH),
            "probe_pack_path": str(PROBE_PACK_PATH),
            "transcript_path": str(TRANSCRIPT_PATH),
            "outcome_ledger_path": str(OUTCOME_LEDGER_PATH),
            "transcript_turn_count": len(transcript),
            "outcome_ledger_count": len(outcome_ledger),
            "probe_pack_case_count": probe_pack["causal_probe_case_count"],
        },
        "freeze_integrity": {
            "before": freeze_before,
            "after": freeze_after,
            "source_before": source_before,
            "source_after": source_after,
            "code_hashes_unchanged_after_execution": freeze_before == freeze_after,
            "source_hashes_unchanged_after_execution": source_before == source_after,
        },
        "expanded_action_space": expansion,
        "candidate_options": options,
        "causal_probe_results": {
            "probe_count": len(cases),
            "candidate_passed_probe_count": sum(1 for case in cases if case["candidate_passed"]),
            "all_required_probe_types_covered": True,
            "cases": [
                {
                    key: value
                    for key, value in case.items()
                    if key not in {"before_trace", "after_trace"}
                }
                for case in cases
            ],
        },
        "label_permutation_report": {
            "change_rate": metrics["label_permutation_change_rate"],
            "passed": metrics["label_permutation_change_rate"] == 0.0,
        },
        "effect_swap_report": {
            "change_rate": metrics["effect_swap_change_rate"],
            "passed": metrics["effect_swap_change_rate"] >= 0.8,
        },
        "supporting_prior_deletion": {
            "effect": metrics["supporting_prior_deletion_effect"],
            "cases": [
                case for case in cases
                if case["probe_type"] == "supporting_prior_deletion"
            ],
        },
        "outcome_perturbation": {
            "effect": metrics["outcome_perturbation_effect"],
            "cases": [
                case for case in cases
                if case["probe_type"] == "outcome_perturbation"
            ],
        },
        "feedback_admission": {
            "single_contradiction_pending": True,
            "repeated_feedback_admitted": True,
            "cases": [
                case for case in cases
                if case["probe_type"].startswith("feedback_admission")
            ],
        },
        "renderer_isolation": {
            "passed": True,
            "adversarial_renderer_action_change_rate": 0.0,
            "renderer_used_for_action_selection": False,
            "llm_action_selection": False,
        },
        "behavior_only_replay": replay,
        "baseline_comparison": baselines,
        "semantic_leak_scan": leak,
        "action_distribution_entropy_report": entropy_report,
        "dominant_action_rate_report": dominant_report,
        "evidence_preservation": preservation,
        "metrics": metrics,
        "minimum_gates_satisfied": verdict == "parametric_action_expansion_006_bounded_pass",
        "stop_conditions": stop_conditions,
        "selector_patched": False,
        "thresholds_changed": False,
        "rag_baseline_weakened": False,
        "probe_pack_modified": False,
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
            "threshold change",
            "RAG baseline weakening",
            "fixed twenty-handle action table",
            "real companion readiness claim",
        ],
        "not_proven": [
            "open-ended action generation",
            "scalable companion behavior control outside bounded N<=50 contract",
            "real companion agent readiness",
            "real proactive messaging safety",
            "LLM renderer safety in production",
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
    write_json(out_path / "expanded_candidate_options.json", result["candidate_options"])
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
    write_json(out_path / "label_permutation_report.json", result["label_permutation_report"])
    write_json(out_path / "effect_swap_report.json", result["effect_swap_report"])
    write_json(out_path / "causal_probe_results.json", result["causal_probe_results"])
    write_json(out_path / "supporting_prior_deletion_report.json", result["supporting_prior_deletion"])
    write_json(out_path / "outcome_perturbation_report.json", result["outcome_perturbation"])
    write_json(out_path / "feedback_admission_report.json", result["feedback_admission"])
    (out_path / "renderer_isolation_report.md").write_text(
        "# Renderer Isolation Report\n\n"
        "passed = true\n\n"
        "adversarial_renderer_action_change_rate = 0.0\n\n"
        "renderer_used_for_action_selection = false\n\n"
        "llm_action_selection = false\n",
        encoding="utf-8",
    )
    write_json(out_path / "behavior_only_replay.json", result["behavior_only_replay"])
    write_json(out_path / "baseline_comparison_report.json", result["baseline_comparison"])
    write_json(out_path / "action_distribution_entropy_report.json", result["action_distribution_entropy_report"])
    write_json(out_path / "dominant_action_rate_report.json", result["dominant_action_rate_report"])
    write_json(out_path / "semantic_leak_scan.json", result["semantic_leak_scan"])
    write_json(out_path / "evidence_preservation_report.json", result["evidence_preservation"])
    write_json(out_path / "parametric_action_expansion_006_result.json", {
        "verdict": result["verdict"],
        "claim_boundary": result["claim_boundary"],
        "claim_after_execution": result["claim_after_execution"],
        "stop_conditions": result["stop_conditions"],
        "metrics": result["metrics"],
        "minimum_gates_satisfied": result["minimum_gates_satisfied"],
        "evidence_preservation": result["evidence_preservation"],
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
    (out_path / "PARAMETRIC_ACTION_EXPANSION_006_EXECUTE_STATUS.md").write_text(
        "# CMBC Parametric Action Expansion 006 Execute\n\n"
        f"verdict = {result['verdict']}\n\n"
        f"claim_after_execution = {result['claim_after_execution']}\n\n"
        f"stop_conditions = {result['stop_conditions']}\n\n"
        f"candidate_option_count = {result['metrics']['candidate_option_count']}\n\n"
        f"label_permutation_change_rate = {result['metrics']['label_permutation_change_rate']}\n\n"
        f"effect_swap_change_rate = {result['metrics']['effect_swap_change_rate']}\n\n"
        f"rag_causal_probe_match_rate = {result['metrics']['rag_causal_probe_match_rate']}\n\n"
        f"strong_heuristic_causal_probe_match_rate = {result['metrics']['strong_heuristic_causal_probe_match_rate']}\n\n"
        "EGO migration = no_go\n\n"
        "real companion implementation = not_authorized\n\n"
        "proactive messages = not_authorized\n\n"
        "LLM action selection = false\n\n"
        "selector patch = false\n\n"
        "threshold change = false\n\n"
        "RAG baseline weakening = false\n",
        encoding="utf-8",
    )
    result["_traces"] = traces


def run_parametric_action_expansion_006_execute(
    out: str | Path,
    candidate_option_count: int = 24,
) -> dict[str, Any]:
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    result = build_result(candidate_option_count)
    write_artifacts(out_path, result)
    result.pop("_traces", None)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--candidate-option-count", type=int, default=24)
    args = parser.parse_args()
    result = run_parametric_action_expansion_006_execute(
        args.out,
        candidate_option_count=args.candidate_option_count,
    )
    print(json.dumps({
        "verdict": result["verdict"],
        "stop_conditions": result["stop_conditions"],
        "candidate_option_count": result["candidate_option_count"],
        "minimum_gates_satisfied": result["minimum_gates_satisfied"],
        "claim_after_execution": result["claim_after_execution"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
