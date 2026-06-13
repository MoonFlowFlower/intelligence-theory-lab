from __future__ import annotations

import json
from typing import Any

from . import TASK_ID


POSITIVE_CONTROL_IDS = (
    "target_label_in_serialized_state",
    "partner_family_id_in_candidate_observation",
    "heldout_schema_id_in_trace_metadata",
    "future_answer_action_in_replay_artifact",
    "result_field_leaked_into_input_bundle",
    "target_outcome_in_hash_filename_or_metadata",
    "predictive_train_heldout_split_key_exposed",
)

LEAKAGE_PATTERNS = {
    "target_label_in_serialized_state": ("target_label", "oracle_latent_label", "target_action"),
    "partner_family_id_in_candidate_observation": ("partner_family_id", "family_heldout", "family_train"),
    "heldout_schema_id_in_trace_metadata": ("heldout_schema_id", "schema_heldout"),
    "future_answer_action_in_replay_artifact": ("future_answer", "future_action", "answer_action"),
    "result_field_leaked_into_input_bundle": ("candidate_score", "baseline_score", "result_verdict"),
    "target_outcome_in_hash_filename_or_metadata": ("target_outcome", "answer_key", "label_hash"),
    "predictive_train_heldout_split_key_exposed": ("split_key_predictive", "heldout_target_split"),
}


def _flatten(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, default=str).lower()


def detect_leakage(payload: Any) -> dict[str, Any]:
    text = _flatten(payload)
    detected = []
    for control_id, patterns in LEAKAGE_PATTERNS.items():
        if any(pattern.lower() in text for pattern in patterns):
            detected.append(control_id)
    return {
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.leakage.detect_leakage",
        "detected_control_ids": sorted(set(detected)),
        "has_leakage": bool(detected),
    }

def run_positive_control_suite() -> dict[str, Any]:
    controls = {
        "target_label_in_serialized_state": {"serialized_state": {"target_label": "partner_specific_support"}},
        "partner_family_id_in_candidate_observation": {"observation": {"partner_family_id": "family_heldout_invert"}},
        "heldout_schema_id_in_trace_metadata": {"trace_metadata": {"heldout_schema_id": "schema_heldout_triage"}},
        "future_answer_action_in_replay_artifact": {"replay": {"future_answer": "clarifying_probe"}},
        "result_field_leaked_into_input_bundle": {"input_bundle": {"candidate_score": 1.0, "baseline_score": 0.1}},
        "target_outcome_in_hash_filename_or_metadata": {"path": "episode_target_outcome_partner_specific_support.json"},
        "predictive_train_heldout_split_key_exposed": {"metadata": {"split_key_predictive": "heldout_is_support"}},
    }
    rows = []
    detected = []
    for control_id, payload in controls.items():
        result = detect_leakage(payload)
        found = control_id in result["detected_control_ids"]
        rows.append(
            {
                "control_id": control_id,
                "detected": found,
                "detected_control_ids": result["detected_control_ids"],
            }
        )
        if found:
            detected.append(control_id)
    return {
        "task_id": TASK_ID,
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.leakage.run_positive_control_suite",
        "passed": set(detected) == set(POSITIVE_CONTROL_IDS),
        "positive_control_detected": set(detected) == set(POSITIVE_CONTROL_IDS),
        "detected_control_ids": sorted(detected),
        "rows": rows,
    }


def scan_clean_bundle(payload: Any, *, positive_controls_passed: bool) -> dict[str, Any]:
    if not positive_controls_passed:
        return {
            "task_id": TASK_ID,
            "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.leakage.scan_clean_bundle",
            "verdict": "blocked_positive_controls_not_run",
            "clean_scan_trusted": False,
            "detected_control_ids": [],
        }
    detection = detect_leakage(payload)
    return {
        "task_id": TASK_ID,
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.leakage.scan_clean_bundle",
        "verdict": "blocked_by_leakage_scan" if detection["has_leakage"] else "clean",
        "clean_scan_trusted": not detection["has_leakage"],
        "detected_control_ids": detection["detected_control_ids"],
        "scan_surfaces": [
            "generated_datasets",
            "serialized_states",
            "observation_bundles",
            "trace_artifacts",
            "provenance_files",
            "result_files",
            "replay_files",
            "source_generated_metadata",
            "filenames_and_path_keys",
        ],
    }
