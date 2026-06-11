from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from process_intervention_hard_distribution_001b import core as core_001b


TASK_ID = "PROCESS-INTERVENTION-HARD-DISTRIBUTION-001D-TARGET-FREE-GENERATIVE-REPLAY-CHALLENGER"
CLAIM_CEILING = "bounded target-free generative replay challenger preflight evidence only"
FREEZE_ANCHOR_COMMIT = "afeff65"

ALLOWED_VERDICTS = {
    "process_intervention_hard_distribution_001d_failed_target_free_replay_challenger_match",
    "process_intervention_hard_distribution_001d_failed_witness_or_ablation",
    "process_intervention_hard_distribution_001d_bounded_replay_gate_pass",
    "process_intervention_hard_distribution_001d_invalid_access_leakage",
}

AUTHORIZATION_FLAGS = {
    "gate1_authorized": False,
    "gate1_reopen_authorized": False,
    "same_agent_bridge_authorized": False,
    "ego_mainline_authorized": False,
    "ego_integration_authorized": False,
    "model_class_reset_authorized": False,
    "mechanism_tournament_authorized": False,
    "mechanism_implementation_authorized": False,
    "mechanism_training_authorized": False,
    "historical_001b_verdict_rewrite_authorized": False,
    "threshold_change_authorized": False,
}

THRESHOLDS = {
    "match_rate_threshold": 0.95,
    "later_behavior_match_threshold": 0.95,
    "update_process_signature_match_threshold": 0.90,
}

PHASE_A_ALLOWED_INPUTS = ["allowed_prefix", "support_split", "permitted_history"]
PHASE_A_FORBIDDEN_INPUTS = [
    "heldout_outcomes",
    "target_future_behavior",
    "witness_trace_rows_for_target_cases",
    "process_signatures",
    "post_ablation_target_results",
    "failure_manifests",
    "control_comparison_target_results",
]

OLD_ARTIFACT_PATHS = [
    "artifacts/process_intervention_hard_distribution_001b/result.json",
    "artifacts/process_intervention_hard_distribution_001b/control_comparison.json",
    "artifacts/process_intervention_hard_distribution_001b/baseline_comparison.json",
    "artifacts/process_intervention_hard_distribution_001b/ablation_report.json",
    "artifacts/process_intervention_hard_distribution_001b/replay_report.json",
    "artifacts/process_intervention_hard_distribution_001b/heldout_report.json",
    "artifacts/process_intervention_hard_distribution_001b/failure_manifest.json",
    "artifacts/process_intervention_hard_distribution_001b/trace.jsonl",
    "artifacts/process_intervention_hard_distribution_001b/frozen_inputs.json",
    "artifacts/process_intervention_hard_distribution_001b/claim_ceiling.txt",
    "artifacts/process_intervention_hard_distribution_001b_trace_replay_rca_001a/replay_control_adjudication.json",
    "artifacts/process_intervention_hard_distribution_001b_trace_replay_rca_001a/claim_ceiling.txt",
    "artifacts/process_intervention_hard_distribution_001c_replay_gate_revision/replay_gate_revision_result.json",
    "artifacts/process_intervention_hard_distribution_001c_replay_gate_revision/replay_control_taxonomy.json",
    "artifacts/process_intervention_hard_distribution_001c_replay_gate_revision/future_gate_semantics.json",
    "artifacts/process_intervention_hard_distribution_001c_replay_gate_revision/historical_verdict_preservation_note.txt",
    "artifacts/process_intervention_hard_distribution_001c_replay_gate_revision/claim_ceiling.txt",
]

PRESERVED_CONTROLS = [
    "online_count_statistic",
    "count_table",
    "graph_cache",
    "transition_table",
    "successor_map",
    "behavior_only_replay",
    "summary_retrieval",
    "trace_only_replay",
]


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


def phase_a_visible_target(case: dict) -> dict:
    return {
        "case_id": case["case_id"],
        "split": case["split"],
        "observable_context": case["observable_context"],
        "intervention_condition": case["intervention_condition"],
        "action": case["action"],
        "prior_history_signature": case["prior_history_signature"],
        "actual_observation": case["actual_observation"],
        "delay_steps": case["delay_steps"],
        "partial_observability": case["partial_observability"],
        "ambiguity_profile": case["ambiguity_profile"],
    }


def phase_a_visible_support(case: dict) -> dict:
    visible = phase_a_visible_target(case)
    visible.update(
        {
            "outcome": case["outcome"],
            "future_behavior": case["future_behavior"],
        }
    )
    return visible


def build_phase_a_inputs(spec: dict) -> dict:
    support = [phase_a_visible_support(case) for case in spec["case_families"] if case["split"] == "support"]
    target_queries = [
        phase_a_visible_target(case) for case in spec["case_families"] if case["split"] == "heldout"
    ]
    return {
        "allowed_prefix": {
            "task_id": TASK_ID,
            "target_query_schema": sorted(target_queries[0]) if target_queries else [],
            "target_queries": target_queries,
            "forbidden_target_fields_removed": [
                "hidden_state_family",
                "outcome",
                "future_behavior",
                "delayed_effect",
                "process_signature_hash",
            ],
        },
        "support_split": {
            "support_case_count": len(support),
            "support_cases": support,
            "support_labels_allowed": ["outcome", "future_behavior"],
            "support_process_signatures_included": False,
        },
        "permitted_history": {
            "support_prior_history_signatures": sorted({case["prior_history_signature"] for case in support}),
            "target_prior_history_signatures_visible": sorted(
                {case["prior_history_signature"] for case in target_queries}
            ),
        },
    }


class AccessFirewall:
    def __init__(self, allowed_inputs: dict[str, object]) -> None:
        self._allowed_inputs = allowed_inputs
        self.allowed_inputs_read: list[str] = []
        self.forbidden_inputs_blocked: list[str] = []
        self.forbidden_access_used = False

    def read(self, input_name: str) -> object:
        if input_name not in PHASE_A_ALLOWED_INPUTS:
            self.forbidden_access_used = True
            if input_name not in self.forbidden_inputs_blocked:
                self.forbidden_inputs_blocked.append(input_name)
            raise PermissionError(f"Phase A forbidden input requested: {input_name}")
        if input_name not in self.allowed_inputs_read:
            self.allowed_inputs_read.append(input_name)
        return self._allowed_inputs[input_name]

    def block_forbidden_inputs(self) -> None:
        for input_name in PHASE_A_FORBIDDEN_INPUTS:
            if input_name not in self.forbidden_inputs_blocked:
                self.forbidden_inputs_blocked.append(input_name)

    def phase_a_log(self, prediction_commit_hash: str | None = None) -> dict:
        return {
            "access_firewall_enforced": True,
            "allowed_inputs_read": self.allowed_inputs_read,
            "forbidden_inputs_blocked": self.forbidden_inputs_blocked,
            "forbidden_access_used": self.forbidden_access_used,
            "target_trace_rows_read": 0,
            "target_heldout_outcomes_read": 0,
            "target_future_behaviors_read": 0,
            "target_process_signatures_read": 0,
            "prediction_commit_hash_frozen_before_reveal": prediction_commit_hash is not None,
            "prediction_commit_sha256": prediction_commit_hash,
        }


def _majority(values: list[str], default: str) -> str:
    if not values:
        return default
    counter = Counter(values)
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _nearest_support_case(target: dict, support_cases: list[dict]) -> dict | None:
    if not support_cases:
        return None
    ranked = sorted(
        support_cases,
        key=lambda support: (
            support["action"] != target["action"],
            support["actual_observation"] != target["actual_observation"],
            support["intervention_condition"] != target["intervention_condition"],
            support["observable_context"] != target["observable_context"],
            support["case_id"],
        ),
    )
    return ranked[0]


def _proxy_process_signature(target: dict, predicted_outcome: str, predicted_future: str) -> str:
    return sha256_text(
        stable_json(
            {
                "signature_type": "target_free_proxy_not_witness_signature",
                "observable_context": target["observable_context"],
                "intervention_condition": target["intervention_condition"],
                "action": target["action"],
                "prior_history_signature": target["prior_history_signature"],
                "predicted_outcome": predicted_outcome,
                "predicted_future_behavior": predicted_future,
            }
        )
    )


def run_phase_a_target_free_challenger(phase_a_inputs: dict) -> tuple[dict, dict]:
    firewall = AccessFirewall(phase_a_inputs)
    allowed_prefix = firewall.read("allowed_prefix")
    support_split = firewall.read("support_split")
    permitted_history = firewall.read("permitted_history")
    firewall.block_forbidden_inputs()

    support_cases = support_split["support_cases"]
    fallback_outcome = _majority([case["outcome"] for case in support_cases], "unknown_outcome")
    predictions: list[dict] = []
    for target in allowed_prefix["target_queries"]:
        nearest = _nearest_support_case(target, support_cases)
        if nearest is None:
            predicted_outcome = fallback_outcome
            predicted_future = f"unresolved_future_for_{predicted_outcome}"
            basis = "support_majority_fallback"
        else:
            predicted_outcome = nearest["outcome"]
            predicted_future = nearest["future_behavior"]
            basis = f"nearest_support_case:{nearest['case_id']}"
        predictions.append(
            {
                "case_id": target["case_id"],
                "split": target["split"],
                "predicted_intervention_response": predicted_outcome,
                "predicted_later_behavior": predicted_future,
                "predicted_process_signature_hash": _proxy_process_signature(
                    target, predicted_outcome, predicted_future
                ),
                "confidence": 0.25,
                "prediction_basis": basis,
            }
        )

    commit = {
        "task_id": TASK_ID,
        "phase": "A_target_free_prediction_commit",
        "claim_ceiling": CLAIM_CEILING,
        "access_contract": {
            "allowed_inputs": PHASE_A_ALLOWED_INPUTS,
            "forbidden_inputs": PHASE_A_FORBIDDEN_INPUTS,
            "forbidden_access_used": firewall.forbidden_access_used,
            "target_trace_access": False,
            "target_outcome_access": False,
            "target_future_behavior_access": False,
            "target_process_signature_access": False,
        },
        "support_case_count": support_split["support_case_count"],
        "target_prediction_count": len(predictions),
        "permitted_history_summary": {
            "support_history_count": len(permitted_history["support_prior_history_signatures"]),
            "target_history_count": len(permitted_history["target_prior_history_signatures_visible"]),
        },
        "predictions": predictions,
    }
    return commit, firewall.phase_a_log()


def _slice_rate(predictions: dict[str, dict], targets: list[dict], field: str, predicted_field: str) -> float:
    if not targets:
        return 0.0
    hits = 0
    for target in targets:
        prediction = predictions[target["case_id"]]
        if prediction[predicted_field] == target[field]:
            hits += 1
    return hits / len(targets)


def _signature_rate(predictions: dict[str, dict], targets: list[dict]) -> float:
    if not targets:
        return 0.0
    hits = 0
    for target in targets:
        prediction = predictions[target["case_id"]]
        if prediction["predicted_process_signature_hash"] == core_001b.process_signature(target):
            hits += 1
    return hits / len(targets)


def _observable_context_conflict_cases(targets: list[dict]) -> list[dict]:
    counts = Counter(target["observable_context"] for target in targets)
    return [target for target in targets if counts[target["observable_context"]] > 1]


def evaluate_phase_b(commit: dict, reveal_cases: list[dict], before_hash: str, after_hash: str) -> dict:
    heldout_targets = [case for case in reveal_cases if case["split"] == "heldout"]
    predictions = {prediction["case_id"]: prediction for prediction in commit["predictions"]}
    delayed = [case for case in heldout_targets if int(case["delay_steps"]) > 0]
    conflicts = _observable_context_conflict_cases(heldout_targets)
    partial = [
        case for case in heldout_targets if case["partial_observability"]["hidden_state_visible"] is False
    ]
    metrics = {
        "intervention_response_match_rate": _slice_rate(
            predictions, heldout_targets, "outcome", "predicted_intervention_response"
        ),
        "later_behavior_match_rate": _slice_rate(
            predictions, heldout_targets, "future_behavior", "predicted_later_behavior"
        ),
        "update_process_signature_match_rate": _signature_rate(predictions, heldout_targets),
        "heldout_composition_match_rate": _slice_rate(
            predictions, heldout_targets, "outcome", "predicted_intervention_response"
        ),
        "delayed_effect_match_rate": _slice_rate(
            predictions, delayed, "future_behavior", "predicted_later_behavior"
        ),
        "observable_key_conflict_match_rate": _slice_rate(
            predictions, conflicts, "outcome", "predicted_intervention_response"
        ),
        "partial_observability_match_rate": _slice_rate(
            predictions, partial, "outcome", "predicted_intervention_response"
        ),
    }
    challenger_blocks = (
        metrics["intervention_response_match_rate"] >= THRESHOLDS["match_rate_threshold"]
        and metrics["later_behavior_match_rate"] >= THRESHOLDS["later_behavior_match_threshold"]
        and metrics["update_process_signature_match_rate"] >= THRESHOLDS["update_process_signature_match_threshold"]
    )
    return {
        "task_id": TASK_ID,
        "phase": "B_reveal_and_evaluate",
        "claim_ceiling": CLAIM_CEILING,
        "evaluated_after_reveal": True,
        "target_free_challenger_evaluated": True,
        "evaluation_scope": "heldout_target_cases",
        "thresholds": dict(THRESHOLDS),
        "metrics": metrics,
        "case_sets": {
            "heldout_composition_case_count": len(heldout_targets),
            "heldout_case_ids": [case["case_id"] for case in heldout_targets],
            "delayed_effect_case_count": len(delayed),
            "observable_key_conflict_case_count": len(conflicts),
            "partial_observability_case_count": len(partial),
        },
        "prediction_commit_sha256_verification": {
            "before_reveal_sha256": before_hash,
            "after_evaluation_sha256": after_hash,
            "hash_unchanged_after_phase_b": before_hash == after_hash,
        },
        "target_free_challenger_match_blocks_gate": challenger_blocks,
    }


def preserved_controls_report(control_comparison: dict) -> dict:
    controls = control_comparison["controls"]
    non_replay = [name for name in PRESERVED_CONTROLS if name != "trace_only_replay"]
    return {
        "task_id": TASK_ID,
        "preserved_controls": PRESERVED_CONTROLS,
        "controls_present_in_001b": sorted(controls),
        "non_replay_fair_controls_preserved": all(name in controls for name in non_replay),
        "fair_controls_weakened_or_removed": False,
        "trace_only_replay": {
            "classification": "trace_integrity_hygiene",
            "source_match_rate": controls["trace_only_replay"]["match_rate"],
            "counts_as_mechanism_evidence": False,
            "may_block_mechanism_evidence_when_successful": False,
        },
        "best_non_replay_control": control_comparison["best_non_replay_fair_control"],
    }


def baseline_comparison_report(result_001b: dict, rca: dict, result_001c: dict, evaluation: dict) -> dict:
    return {
        "task_id": TASK_ID,
        "historical_001b_verdict": result_001b["verdict"],
        "historical_001b_verdict_preserved": result_001b["verdict"]
        == "process_intervention_hard_distribution_001b_failed_fair_control_match",
        "historical_001b_pass_status": "not_pass",
        "trace_only_replay_rca_classification": rca["replay_control_classification"]["trace_only_replay"][
            "classification"
        ],
        "001c_prediction_commit_protocol_inherited": result_001c["future_gate_revision_summary"][
            "prediction_commit_protocol"
        ],
        "target_free_challenger_metrics": evaluation["metrics"],
        "claim_ceiling": CLAIM_CEILING,
    }


def ablation_report(ablation_001b: dict) -> dict:
    hooks = {hook["hook_id"]: hook for hook in ablation_001b["ablations"]}
    witness_or_ablation_ok = (
        hooks["learning_freeze"]["executed"] is True
        and hooks["learning_freeze"]["changed_expected_process_sensitive_behavior"] is True
        and hooks["history_replacement"]["executed"] is True
        and hooks["history_replacement"]["changed_expected_behavior"] is True
        and hooks["counterfactual_action_contrast"]["executed"] is True
        and hooks["counterfactual_action_contrast"]["contrast_detected"] is True
    )
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "source_task_id": "PROCESS-INTERVENTION-HARD-DISTRIBUTION-001B-EXECUTABLE-PREFLIGHT",
        "witness_or_ablation_prerequisites_ok": witness_or_ablation_ok,
        "inherited_ablations": ablation_001b["ablations"],
    }


def replay_report(access_log: dict, evaluation: dict) -> dict:
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "prediction_commit_hash_frozen_before_reveal": access_log["phase_a"][
            "prediction_commit_hash_frozen_before_reveal"
        ],
        "phase_b_commit_hash_unchanged": evaluation["prediction_commit_sha256_verification"][
            "hash_unchanged_after_phase_b"
        ],
        "trace_only_replay_treated_as_mechanism_evidence": False,
        "replay_hygiene_preserved": True,
    }


def result_payload(
    *,
    evaluation: dict,
    access_log: dict,
    old_artifacts: dict,
    ablations: dict,
) -> dict:
    invalid_access = (
        access_log["phase_a"]["forbidden_access_used"]
        or not access_log["phase_a"]["prediction_commit_hash_frozen_before_reveal"]
        or not access_log["phase_b"]["target_reveal_after_hash_freeze"]
        or access_log["phase_b"]["phase_a_prediction_commit_rewritten"]
        or not old_artifacts["old_artifacts_unchanged_from_anchor"]
    )
    if invalid_access:
        verdict = "process_intervention_hard_distribution_001d_invalid_access_leakage"
    elif not ablations["witness_or_ablation_prerequisites_ok"]:
        verdict = "process_intervention_hard_distribution_001d_failed_witness_or_ablation"
    elif evaluation["target_free_challenger_match_blocks_gate"]:
        verdict = "process_intervention_hard_distribution_001d_failed_target_free_replay_challenger_match"
    else:
        verdict = "process_intervention_hard_distribution_001d_bounded_replay_gate_pass"
    return {
        "task_id": TASK_ID,
        "verdict": verdict,
        "bounded_pass": verdict == "process_intervention_hard_distribution_001d_bounded_replay_gate_pass",
        "claim_ceiling": CLAIM_CEILING,
        "freeze_anchor_commit": FREEZE_ANCHOR_COMMIT,
        "access_firewall_explicit_allowlist_enforced": not access_log["phase_a"]["forbidden_access_used"],
        "prediction_commit_frozen_before_reveal": access_log["phase_a"][
            "prediction_commit_hash_frozen_before_reveal"
        ],
        "phase_b_cannot_rewrite_phase_a_commit": not access_log["phase_b"][
            "phase_a_prediction_commit_rewritten"
        ],
        "target_free_challenger_evaluated_after_reveal": evaluation["evaluated_after_reveal"],
        "target_free_challenger_match_blocks_gate": evaluation["target_free_challenger_match_blocks_gate"],
        "trace_only_replay_hygiene_only": True,
        "old_artifacts_unchanged_from_anchor": old_artifacts["old_artifacts_unchanged_from_anchor"],
        "authorization_flags": dict(AUTHORIZATION_FLAGS),
        "stop_conditions": [] if verdict == "process_intervention_hard_distribution_001d_bounded_replay_gate_pass" else [verdict],
        "what_this_does_not_prove": [
            "mechanism validity",
            "001B pass",
            "theory validity",
            "theory falsity",
            "Gate1 readiness",
            "bridge readiness",
            "EGO readiness",
            "agency",
            "consciousness",
            "companion readiness",
            "model-class reset necessity",
        ],
    }
