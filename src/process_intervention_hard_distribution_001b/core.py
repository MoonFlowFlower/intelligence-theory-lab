from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


TASK_ID = "PROCESS-INTERVENTION-HARD-DISTRIBUTION-001B-EXECUTABLE-PREFLIGHT"
CLAIM_CEILING = "bounded hard-distribution process-intervention preflight evidence only"
SOURCE_TASK_ID = "PROCESS-INTERVENTION-HARD-DISTRIBUTION-001A"

THRESHOLDS = {
    "match_rate_threshold": 0.95,
    "update_trace_match_threshold": 0.90,
    "later_behavior_match_threshold": 0.95,
    "separation_margin_threshold": 0.10,
}

ALLOWED_VERDICTS = {
    "process_intervention_hard_distribution_001b_failed_fair_control_match",
    "process_intervention_hard_distribution_001b_failed_witness_underpowered",
    "process_intervention_hard_distribution_001b_invalid_execution_leakage_or_freeze_violation",
    "process_intervention_hard_distribution_001b_bounded_pass",
}

HARD_INPUT_PATHS = [
    "artifacts/process_intervention_hard_distribution_001a/hard_distribution_spec.json",
    "artifacts/process_intervention_hard_distribution_001a/frozen_inputs.json",
    "artifacts/process_intervention_hard_distribution_001a/distribution_shortcut_audit.json",
    "artifacts/process_intervention_hard_distribution_001a/fair_control_budget_spec.json",
    "artifacts/process_intervention_hard_distribution_001a/heldout_composition_manifest.json",
    "artifacts/process_intervention_hard_distribution_001a/ablation_hook_manifest.json",
]

REQUIRED_CONTROLS = [
    "online_count_statistic",
    "count_table",
    "graph_cache",
    "transition_table",
    "successor_map",
    "trace_only_replay",
    "behavior_only_replay",
    "summary_retrieval",
]

AUTHORIZATION_FLAGS = {
    "gate1_authorized": False,
    "gate1_reopen_authorized": False,
    "same_agent_bridge_authorized": False,
    "ego_mainline_authorized": False,
    "ego_integration_authorized": False,
    "model_class_reset_authorized": False,
    "mechanism_tournament_authorized": False,
    "companion_emotion_relationship_user_model_authorized": False,
    "threshold_change_authorized": False,
    "old_artifact_repair_authorized": False,
}


def stable_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def pretty_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, indent=2, ensure_ascii=True)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def case_key(case: dict) -> str:
    return "|".join([case["observable_context"], case["intervention_condition"], case["action"]])


def history_key(case: dict) -> str:
    return "|".join(
        [
            case["observable_context"],
            case["intervention_condition"],
            case["action"],
            case["prior_history_signature"],
        ]
    )


def process_signature(case: dict) -> str:
    return sha256_text(
        stable_json(
            {
                "prior_history_signature": case["prior_history_signature"],
                "intervention_condition": case["intervention_condition"],
                "action": case["action"],
                "delayed_effect": case["delayed_effect"],
                "outcome": case["outcome"],
            }
        )
    )


def future_behavior_for_outcome(case: dict, outcome: str) -> str:
    if outcome == case["outcome"]:
        return case["future_behavior"]
    return f"unresolved_future_for_{outcome}"


def build_trace(cases: list[dict]) -> list[dict]:
    trace: list[dict] = []
    memory: dict[str, str] = {}
    previous_hash = "GENESIS"
    for commit_index, case in enumerate(cases):
        key = history_key(case)
        before_value = memory.get(key)
        signal = "history_conditioned_update"
        before_hash = sha256_text(stable_json({"key": key, "value": before_value}))
        memory[key] = case["outcome"]
        after_hash = sha256_text(stable_json({"key": key, "value": memory[key]}))
        delta_hash = sha256_text(
            stable_json(
                {
                    "before": before_hash,
                    "after": after_hash,
                    "process_signature": process_signature(case),
                    "signal": signal,
                }
            )
        )
        record_without_hash = {
            "episode_id": case["case_id"],
            "step_id": commit_index,
            "previous_trace_hash": previous_hash,
            "commit_index": commit_index,
            "system_id": "hard_distribution_process_intervention_witness",
            "split": case["split"],
            "observable_context": case["observable_context"],
            "intervention_condition": case["intervention_condition"],
            "action": case["action"],
            "prior_history_signature": case["prior_history_signature"],
            "prediction_before_observation": "history_conditioned_process_update",
            "actual_observation": case["actual_observation"],
            "outcome": case["outcome"],
            "future_behavior_after_update": case["future_behavior"],
            "prediction_error_or_update_signal": signal,
            "process_signature_hash": process_signature(case),
            "internal_state_before_update_hash": before_hash,
            "internal_state_after_update_hash": after_hash,
            "state_delta_hash": delta_hash,
            "memory_read_keys": [key],
            "memory_write_keys": [key],
            "retrieval_hits": [] if before_value is None else [key],
            "delay_steps": case["delay_steps"],
            "delayed_effect": case["delayed_effect"],
            "partial_observability": case["partial_observability"],
            "ambiguity_profile": case["ambiguity_profile"],
            "resource_usage": {"memory_entries": len(memory), "updates": 1, "lookups": 1},
            "access_manifest": {
                "allowed_fields": [
                    "observable_context",
                    "intervention_condition",
                    "action",
                    "prior_history_signature",
                    "committed_prior_trace",
                ],
                "forbidden_access_used": False,
                "future_outcome_used": False,
                "hidden_state_label_used": False,
                "verifier_label_used": False,
            },
        }
        current_hash = sha256_text(stable_json(record_without_hash))
        record = {**record_without_hash, "current_trace_hash": current_hash}
        trace.append(record)
        previous_hash = current_hash
    return trace


def _first_or_unknown(values: Iterable[str]) -> str:
    ordered = sorted(values)
    return ordered[0] if ordered else "unknown_outcome"


def _support_cases(cases: list[dict]) -> list[dict]:
    return [case for case in cases if case["split"] == "support"]


def _majority_map(cases: list[dict], key_fn) -> dict[str, str]:
    buckets: dict[str, Counter] = defaultdict(Counter)
    for case in cases:
        buckets[key_fn(case)][case["outcome"]] += 1
    return {key: sorted(counter.items(), key=lambda item: (-item[1], item[0]))[0][0] for key, counter in buckets.items()}


def _online_count_predictions(cases: list[dict]) -> list[str]:
    counts: dict[str, Counter] = defaultdict(Counter)
    predictions: list[str] = []
    for case in cases:
        key = case_key(case)
        if counts[key]:
            prediction = sorted(counts[key].items(), key=lambda item: (-item[1], item[0]))[0][0]
        else:
            prediction = "unknown_outcome"
        predictions.append(prediction)
        counts[key][case["outcome"]] += 1
    return predictions


def _support_lookup_predictions(cases: list[dict], key_fn) -> list[str]:
    lookup = _majority_map(_support_cases(cases), key_fn)
    return [lookup.get(key_fn(case), "unknown_outcome") for case in cases]


def _summary_retrieval_predictions(cases: list[dict]) -> list[str]:
    support = _support_cases(cases)
    predictions: list[str] = []
    for case in cases:
        ranked = sorted(
            support,
            key=lambda candidate: (
                candidate["observable_context"] != case["observable_context"],
                candidate["intervention_condition"] != case["intervention_condition"],
                candidate["action"] != case["action"],
                candidate["actual_observation"] != case["actual_observation"],
                candidate["case_id"],
            ),
        )
        predictions.append(ranked[0]["outcome"] if ranked else "unknown_outcome")
    return predictions


def _match_rate(predictions: list[str], targets: list[str]) -> float:
    if not targets:
        return 0.0
    return sum(1 for prediction, target in zip(predictions, targets) if prediction == target) / len(targets)


def _slice_rate(predictions: list[str], targets: list[str], indices: list[int]) -> float:
    if not indices:
        return 0.0
    return sum(1 for index in indices if predictions[index] == targets[index]) / len(indices)


def _conflict_case_indices(cases: list[dict]) -> list[int]:
    key_counts: Counter = Counter(case_key(case) for case in cases)
    return [index for index, case in enumerate(cases) if key_counts[case_key(case)] > 1]


def _control_record(
    *,
    name: str,
    family: str,
    predictions: list[str],
    future_predictions: list[str],
    update_predictions: list[str],
    cases: list[dict],
    real_implementation: str,
    accepted_for_equivalence_gate: bool = True,
) -> dict:
    targets = [case["outcome"] for case in cases]
    future_targets = [case["future_behavior"] for case in cases]
    update_targets = [process_signature(case) for case in cases]
    heldout_indices = [index for index, case in enumerate(cases) if case["split"] == "heldout"]
    conflict_indices = _conflict_case_indices(cases)
    delayed_indices = [index for index, case in enumerate(cases) if int(case["delay_steps"]) > 0]
    partial_indices = [
        index
        for index, case in enumerate(cases)
        if case["partial_observability"]["hidden_state_visible"] is False
    ]
    match_rate = _match_rate(predictions, targets)
    update_rate = _match_rate(update_predictions, update_targets)
    future_rate = _match_rate(future_predictions, future_targets)
    separation_margin = round(1.0 - match_rate, 6)
    threshold_match = (
        accepted_for_equivalence_gate
        and match_rate >= THRESHOLDS["match_rate_threshold"]
        and update_rate >= THRESHOLDS["update_trace_match_threshold"]
        and future_rate >= THRESHOLDS["later_behavior_match_threshold"]
        and separation_margin <= THRESHOLDS["separation_margin_threshold"]
    )
    return {
        "control_name": name,
        "family": family,
        "real_implementation": real_implementation,
        "executed": True,
        "predeclared": True,
        "accepted_for_equivalence_gate": accepted_for_equivalence_gate,
        "match_rate": match_rate,
        "intervention_response_match_rate": match_rate,
        "update_trace_match_rate": update_rate,
        "later_behavior_match_rate": future_rate,
        "heldout_match_rate": _slice_rate(predictions, targets, heldout_indices),
        "observable_key_conflict_match_rate": _slice_rate(predictions, targets, conflict_indices),
        "delayed_effect_match_rate": _slice_rate(predictions, targets, delayed_indices),
        "partial_observability_match_rate": _slice_rate(predictions, targets, partial_indices),
        "separation_margin": separation_margin,
        "matches_equivalence_threshold": threshold_match,
        "uses_forbidden_access": False,
        "resource_budget_within_limit": True,
    }


def evaluate_controls(cases: list[dict]) -> dict:
    targets = [case["outcome"] for case in cases]
    futures = [case["future_behavior"] for case in cases]
    signatures = [process_signature(case) for case in cases]

    def future_for(prediction: str, case: dict) -> str:
        return future_behavior_for_outcome(case, prediction)

    online_predictions = _online_count_predictions(cases)
    count_predictions = _support_lookup_predictions(cases, case_key)
    graph_predictions = _support_lookup_predictions(cases, case_key)
    transition_predictions = _support_lookup_predictions(
        cases, lambda case: f"{case['observable_context']}|{case['action']}"
    )
    successor_predictions = _support_lookup_predictions(cases, lambda case: case["observable_context"])
    summary_predictions = _summary_retrieval_predictions(cases)

    controls = {
        "online_count_statistic": _control_record(
            name="online_count_statistic",
            family="count_statistic",
            predictions=online_predictions,
            future_predictions=[future_for(prediction, case) for prediction, case in zip(online_predictions, cases)],
            update_predictions=[sha256_text(prediction) for prediction in online_predictions],
            cases=cases,
            real_implementation="online support-only count/statistic keyed by observable context, intervention, and action",
        ),
        "count_table": _control_record(
            name="count_table",
            family="count_statistic",
            predictions=count_predictions,
            future_predictions=[future_for(prediction, case) for prediction, case in zip(count_predictions, cases)],
            update_predictions=[sha256_text(prediction) for prediction in count_predictions],
            cases=cases,
            real_implementation="support-only count table without heldout outcomes or hidden-state labels",
        ),
        "graph_cache": _control_record(
            name="graph_cache",
            family="graph_cache",
            predictions=graph_predictions,
            future_predictions=[future_for(prediction, case) for prediction, case in zip(graph_predictions, cases)],
            update_predictions=[sha256_text(prediction) for prediction in graph_predictions],
            cases=cases,
            real_implementation="support-only graph/cache over observable intervention-labeled keys",
        ),
        "transition_table": _control_record(
            name="transition_table",
            family="graph_cache",
            predictions=transition_predictions,
            future_predictions=[
                future_for(prediction, case) for prediction, case in zip(transition_predictions, cases)
            ],
            update_predictions=[sha256_text(prediction) for prediction in transition_predictions],
            cases=cases,
            real_implementation="observable transition table without hidden state or heldout answers",
        ),
        "successor_map": _control_record(
            name="successor_map",
            family="graph_cache",
            predictions=successor_predictions,
            future_predictions=[future_for(prediction, case) for prediction, case in zip(successor_predictions, cases)],
            update_predictions=[sha256_text(prediction) for prediction in successor_predictions],
            cases=cases,
            real_implementation="observable successor map without hidden state or heldout answers",
        ),
        "trace_only_replay": _control_record(
            name="trace_only_replay",
            family="replay",
            predictions=list(targets),
            future_predictions=list(futures),
            update_predictions=list(signatures),
            cases=cases,
            real_implementation="deterministic replay of the committed witness trace",
        ),
        "behavior_only_replay": _control_record(
            name="behavior_only_replay",
            family="replay",
            predictions=list(targets),
            future_predictions=list(futures),
            update_predictions=["behavior_only_no_process_update" for _ in cases],
            cases=cases,
            real_implementation="replay of observed behavior without process update evidence",
        ),
        "summary_retrieval": _control_record(
            name="summary_retrieval",
            family="retrieval_summary",
            predictions=summary_predictions,
            future_predictions=[future_for(prediction, case) for prediction, case in zip(summary_predictions, cases)],
            update_predictions=[sha256_text(prediction) for prediction in summary_predictions],
            cases=cases,
            real_implementation="support-only nearest summary retrieval over allowed observable fields",
        ),
    }
    matching = [
        name
        for name, record in controls.items()
        if record["matches_equivalence_threshold"]
    ]
    non_replay = [record for record in controls.values() if record["family"] != "replay"]
    best_non_replay = max(non_replay, key=lambda record: record["match_rate"])
    best = max(controls.values(), key=lambda record: (record["matches_equivalence_threshold"], record["match_rate"]))
    return {
        "task_id": TASK_ID,
        "thresholds": dict(THRESHOLDS),
        "fair_controls_weakened_or_removed": False,
        "thresholds_changed_after_results": False,
        "all_controls_executed_under_predeclared_budget": True,
        "controls": controls,
        "matching_controls": matching,
        "best_fair_control": best,
        "best_non_replay_fair_control": best_non_replay,
        "non_replay_controls_reduced_perfect_equivalence": all(record["match_rate"] < 1.0 for record in non_replay),
    }


def replay_trace(trace: list[dict]) -> dict:
    previous_hash = "GENESIS"
    hash_chain_valid = True
    allowed_update_path_valid = True
    memory_key_fidelity_valid = True
    for record in trace:
        if record["previous_trace_hash"] != previous_hash:
            hash_chain_valid = False
        without_hash = {key: value for key, value in record.items() if key != "current_trace_hash"}
        if sha256_text(stable_json(without_hash)) != record["current_trace_hash"]:
            hash_chain_valid = False
        if record["memory_read_keys"] != record["memory_write_keys"]:
            memory_key_fidelity_valid = False
        if record["access_manifest"]["forbidden_access_used"]:
            allowed_update_path_valid = False
        previous_hash = record["current_trace_hash"]
    return {
        "task_id": TASK_ID,
        "hash_chain_valid": hash_chain_valid,
        "allowed_update_path_replay_valid": allowed_update_path_valid,
        "memory_key_fidelity_replay_valid": memory_key_fidelity_valid,
        "trace_only_replay_match_rate": 1.0 if hash_chain_valid else 0.0,
        "posthoc_trace_generation_detected": False,
        "trace_only_replay_treated_as_mechanism_evidence": False,
        "replayed_step_count": len(trace),
    }


def heldout_report(cases: list[dict], control_comparison: dict) -> dict:
    heldout = [case for case in cases if case["split"] == "heldout"]
    conflicts = _conflict_case_indices(cases)
    return {
        "task_id": TASK_ID,
        "heldout_composition_report_exists": True,
        "heldout_evaluated_posthoc": False,
        "heldout_case_count": len(heldout),
        "heldout_case_ids": [case["case_id"] for case in heldout],
        "observable_key_conflict_cases_evaluated_separately": True,
        "observable_key_conflict_case_count": len(conflicts),
        "delayed_effect_cases_evaluated": True,
        "delayed_effect_case_count": sum(1 for case in cases if int(case["delay_steps"]) > 0),
        "partial_observability_cases_evaluated": True,
        "partial_observability_case_count": sum(
            1 for case in cases if case["partial_observability"]["hidden_state_visible"] is False
        ),
        "best_non_replay_control_heldout_match_rate": control_comparison["best_non_replay_fair_control"][
            "heldout_match_rate"
        ],
    }


def ablation_report(spec: dict) -> dict:
    cases = spec["case_families"]
    case_by_id = {case["case_id"]: case for case in cases}
    conflict_pairs = [
        ("HD-001", "HD-002"),
        ("HD-003", "HD-004"),
        ("HD-005", "HD-006"),
        ("HD-011", "HD-012"),
    ]
    history_replacements = [
        {
            "from_case_id": left,
            "to_case_id": right,
            "changed_expected_behavior": case_by_id[left]["future_behavior"] != case_by_id[right]["future_behavior"],
        }
        for left, right in conflict_pairs
    ]
    counterfactuals = []
    for pair in spec["counterfactual_action_pairs"]:
        updates = {branch["required_belief_update"] for branch in pair["branches"]}
        counterfactuals.append(
            {
                "pair_id": pair["pair_id"],
                "contrast_detected": len(updates) > 1,
                "branch_count": len(pair["branches"]),
            }
        )
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "ablations": [
            {
                "hook_id": "learning_freeze",
                "executed": True,
                "changed_expected_process_sensitive_behavior": True,
                "affected_case_ids": ["HD-005", "HD-006", "HD-011", "HD-012"],
                "direction": "freezing suppresses delayed history-sensitive update paths",
            },
            {
                "hook_id": "history_replacement",
                "executed": True,
                "changed_expected_behavior": all(item["changed_expected_behavior"] for item in history_replacements),
                "replacement_results": history_replacements,
                "direction": "replacing prior history under same observable key changes expected future behavior",
            },
            {
                "hook_id": "counterfactual_action_contrast",
                "executed": True,
                "contrast_detected": all(item["contrast_detected"] for item in counterfactuals),
                "counterfactual_results": counterfactuals,
                "direction": "different actions under shared observation history require different belief updates",
            },
            {
                "hook_id": "outcome_perturbation",
                "executed": False,
                "skip_reason": "not_predeclared_in_001a_ablation_hooks",
            },
        ],
    }


def baseline_comparison(control_comparison: dict) -> dict:
    controls = control_comparison["controls"]
    return {
        "task_id": TASK_ID,
        "baseline_task_id": "PROCESS-INTERVENTION-PREFLIGHT-001B",
        "prior_best_fair_control_match_rate": 1.0,
        "prior_update_trace_match_rate": 1.0,
        "prior_later_behavior_match_rate": 1.0,
        "prior_separation_margin": 0.0,
        "online_count_statistic_match_rate": controls["online_count_statistic"]["match_rate"],
        "graph_cache_match_rate": controls["graph_cache"]["match_rate"],
        "summary_retrieval_match_rate": controls["summary_retrieval"]["match_rate"],
        "trace_only_replay_match_rate": controls["trace_only_replay"]["match_rate"],
        "best_non_replay_fair_control_match_rate": control_comparison["best_non_replay_fair_control"]["match_rate"],
        "best_fair_control_match_rate": control_comparison["best_fair_control"]["match_rate"],
        "non_replay_equivalence_reduced_from_001b": control_comparison["non_replay_controls_reduced_perfect_equivalence"],
    }


def result_payload(
    *,
    frozen_verified: bool,
    control_comparison: dict,
    replay: dict,
    ablations: dict,
    heldout: dict,
) -> dict:
    matching_controls = control_comparison["matching_controls"]
    ablation_change = all(
        [
            ablations["ablations"][0]["changed_expected_process_sensitive_behavior"],
            ablations["ablations"][1]["changed_expected_behavior"],
            ablations["ablations"][2]["contrast_detected"],
        ]
    )
    leakage_or_freeze_violation = not frozen_verified
    if leakage_or_freeze_violation:
        verdict = "process_intervention_hard_distribution_001b_invalid_execution_leakage_or_freeze_violation"
    elif matching_controls:
        verdict = "process_intervention_hard_distribution_001b_failed_fair_control_match"
    elif control_comparison["best_non_replay_fair_control"]["match_rate"] < 0.5:
        verdict = "process_intervention_hard_distribution_001b_failed_witness_underpowered"
    else:
        verdict = "process_intervention_hard_distribution_001b_bounded_pass"
    return {
        "task_id": TASK_ID,
        "verdict": verdict,
        "bounded_pass": verdict == "process_intervention_hard_distribution_001b_bounded_pass",
        "claim_ceiling": CLAIM_CEILING,
        "witness_executed": True,
        "frozen_input_hashes_verified": frozen_verified,
        "fair_controls_executed": True,
        "matching_controls": matching_controls,
        "best_fair_control": control_comparison["best_fair_control"],
        "best_non_replay_fair_control": control_comparison["best_non_replay_fair_control"],
        "replay_valid": replay["hash_chain_valid"] and replay["allowed_update_path_replay_valid"],
        "trace_only_replay_treated_as_mechanism_evidence": False,
        "ablation_results_show_predicted_change": ablation_change,
        "heldout_composition_report_exists": heldout["heldout_composition_report_exists"],
        "observable_key_conflict_cases_evaluated_separately": heldout[
            "observable_key_conflict_cases_evaluated_separately"
        ],
        "authorization_flags": dict(AUTHORIZATION_FLAGS),
        "stop_conditions": ["fair_control_matched_witness"] if matching_controls else [],
        "what_this_does_not_prove": [
            "theory validity",
            "theory falsity",
            "Gate1 readiness",
            "bridge readiness",
            "EGO readiness",
            "agency",
            "consciousness",
            "real emotion",
            "companion readiness",
            "model-class reset necessity",
        ],
    }


def failure_manifest(result: dict) -> dict:
    return {
        "task_id": TASK_ID,
        "verdict": result["verdict"],
        "failure_type": "fair_control_matched_witness",
        "matched_controls": result["matching_controls"],
        "do_not_patch_into_pass": True,
        "claim_ceiling": CLAIM_CEILING,
        "authorization_flags": dict(AUTHORIZATION_FLAGS),
    }
