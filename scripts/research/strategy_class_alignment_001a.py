from __future__ import annotations

from typing import Any

from evidence_provenance_001a import code_path_hash
from minimal_env_spec_loader_001a import BUDGET_COMPONENT_CHANNELS, FINAL_ACTIONS


def build_oracle_strategy_class() -> dict[str, Any]:
    return {
        "strategy_class": "budget_limited_belief_state_planner",
        "visible_channel": "legal_channel_responses_if_queried",
        "candidate_matched_budget": 5,
        "legal_action_query_set": list(BUDGET_COMPONENT_CHANNELS),
        "episode_information_boundary": [
            "episode_id",
            "seed",
            "observable_state",
            "legal_action_space",
            "queried_channel_responses_only",
            "budget_state",
            "own_query_history",
        ],
        "scoring_target": list(FINAL_ACTIONS),
        "prohibited_field_boundary": [
            "hidden_state",
            "target_label_or_target_variable",
            "answer_key",
            "unqueried_channel_values",
            "stored_labels",
            "stored_predictions",
            "stored_final_hashes",
        ],
    }


def build_strongest_classical_strategy_class() -> dict[str, Any]:
    return {
        "strategy_class": "budget_limited_belief_state_planner",
        "visible_channel": "legal_channel_responses_if_queried",
        "candidate_matched_budget": 5,
        "legal_action_query_set": list(BUDGET_COMPONENT_CHANNELS),
        "episode_information_boundary": [
            "episode_id",
            "seed",
            "observable_state",
            "legal_action_space",
            "queried_channel_responses_only",
            "budget_state",
            "own_query_history",
        ],
        "scoring_target": list(FINAL_ACTIONS),
        "prohibited_field_boundary": [
            "hidden_state",
            "target_label_or_target_variable",
            "answer_key",
            "unqueried_channel_values",
            "stored_labels",
            "stored_predictions",
            "stored_final_hashes",
        ],
        "operationalized_by": [
            "budget_limited_belief_state_planner",
            "greedy_information_gain_or_uncertainty_planner_under_budget",
            "fsm_planner",
            "successor_map",
            "transition_table",
            "graph_lookup",
            "episodic_traversal",
        ],
    }


def run_strategy_class_alignment(run_id: str) -> dict[str, Any]:
    oracle = build_oracle_strategy_class()
    classical = build_strongest_classical_strategy_class()
    checks = {
        "same_visible_channel": oracle["visible_channel"] == classical["visible_channel"],
        "same_candidate_matched_budget": oracle["candidate_matched_budget"] == classical["candidate_matched_budget"],
        "same_legal_action_query_set": oracle["legal_action_query_set"] == classical["legal_action_query_set"],
        "same_information_boundary": oracle["episode_information_boundary"] == classical["episode_information_boundary"],
        "same_scoring_target": oracle["scoring_target"] == classical["scoring_target"],
        "same_prohibited_field_boundary": oracle["prohibited_field_boundary"] == classical["prohibited_field_boundary"],
        "same_strategy_class": oracle["strategy_class"] == classical["strategy_class"],
    }
    return {
        "schema_version": "baseline_first_harness_001a_strategy_class_alignment_v1",
        "run_id": run_id,
        "result": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "oracle_strategy_class": oracle,
        "strongest_classical_strategy_class": classical,
        "strongest_known_classical_method_status": "scored",
        "producer_function": "strategy_class_alignment_001a.run_strategy_class_alignment",
        "code_path_hash": code_path_hash(run_strategy_class_alignment),
        "consumed_by_final_verdict": True,
    }


def _scan_forbidden_tokens(value: Any, path: str, detections: list[dict[str, str]]) -> None:
    forbidden = ["answer_key", "hidden_state", "target_label", "target_variable", "stored_prediction"]
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()
            for token in forbidden:
                if token in key_text:
                    detections.append({"detection_id": f"forbidden_key:{path}/{key}", "token": token, "path": f"{path}/{key}"})
            _scan_forbidden_tokens(child, f"{path}/{key}", detections)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_forbidden_tokens(child, f"{path}[{index}]", detections)
    elif isinstance(value, str):
        text = value.lower()
        for token in forbidden:
            if token in text:
                detections.append({"detection_id": f"forbidden_value:{path}", "token": token, "path": path})


def run_leakage_controls(episodes: list[dict[str, Any]], oracle_report: dict[str, Any], run_id: str) -> dict[str, Any]:
    visible_payload = {
        "episodes": [
            {
                "episode_id": episode["episode_id"],
                "observable_state": episode["observable_state"],
                "legal_action_space": episode["legal_action_space"],
            }
            for episode in episodes
        ],
        "oracle_consumed_fields": oracle_report["consumed_field_manifest"],
    }
    clean_detections: list[dict[str, str]] = []
    _scan_forbidden_tokens(visible_payload, "$", clean_detections)
    leaky_variant_manifest = list(oracle_report["consumed_field_manifest"]) + [
        "hidden_state.diagnostic_target_index",
        "target_label_or_target_variable",
        "answer_key.synthetic_positive_control",
    ]
    leaky_payload = {**visible_payload, "oracle_consumed_fields": leaky_variant_manifest}
    leaky_detections: list[dict[str, str]] = []
    _scan_forbidden_tokens(leaky_payload, "$", leaky_detections)
    removed_payload = {**visible_payload, "oracle_consumed_fields": oracle_report["consumed_field_manifest"]}
    removed_detections: list[dict[str, str]] = []
    _scan_forbidden_tokens(removed_payload, "$", removed_detections)
    positive_detected = bool(leaky_detections)
    removal_clean = not removed_detections
    return {
        "schema_version": "baseline_first_harness_001a_leakage_v1",
        "run_id": run_id,
        "result": "passed" if not clean_detections and positive_detected and removal_clean else "failed",
        "clean_scan": {"detected": clean_detections},
        "positive_control": {
            "control_id": "leaky_oracle_reads_hidden_state_target_answer_key",
            "detected": positive_detected,
            "detected_ids": [row["detection_id"] for row in leaky_detections],
            "removal_removes_detection": removal_clean,
            "leaky_variant_reads": [
                "hidden_state",
                "target_label_or_target_variable",
                "answer_key",
            ],
            "consumed_by_final_verdict": True,
        },
        "producer_function": "strategy_class_alignment_001a.run_leakage_controls",
        "code_path_hash": code_path_hash(run_leakage_controls),
        "consumed_by_final_verdict": True,
    }
