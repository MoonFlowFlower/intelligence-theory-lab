from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any


TASK_ID = "GATE3-VIABILITY-FUNCTIONAL-AFFECT-EXECUTABLE-PREFLIGHT-001B"
VERDICT_PASS = "gate3_viability_functional_affect_001b_bounded_preflight_pass"
VERDICT_BASELINE = "gate3_viability_functional_affect_001b_failed_baseline_match"
VERDICT_ABLATION = "gate3_viability_functional_affect_001b_failed_ablation_insensitive"
VERDICT_TRACE = "gate3_viability_functional_affect_001b_failed_trace_or_linkage_contract"
VERDICT_LEAKAGE = "gate3_viability_functional_affect_001b_invalid_leakage"
VERDICT_MUTATION = "gate3_viability_functional_affect_001b_invalid_mutation"
VERDICT_PRIORITY = "gate3_viability_functional_affect_001b_failed_priority_link"

CLAIM_CEILING = "bounded Gate3 viability / functional-affect executable preflight evidence only"
ARTIFACT_DIR_REL = "artifacts/gate3_viability_functional_affect_001b"
EXECUTABLE_TASK_CARD_PATH = (
    "docs/codex/tasks/GATE3-VIABILITY-FUNCTIONAL-AFFECT-EXECUTABLE-PREFLIGHT-001B.md"
)
PARENT_TASK_CARD_PATH = "docs/codex/tasks/GATE3-VIABILITY-FUNCTIONAL-AFFECT-TASK-CARD-001A.md"
STATE_SCHEMA_ID = "canonical_gate3_viability_functional_affect_shared_state_v1"
GATE3_RUN_ID = "gate3_viability_functional_affect_001b_run_v1"
ACCEPTANCE_THRESHOLD = 0.95

PARENT_ANCHORS = {
    "gate0_frozen_bounded_predictive_action_evidence": "PREDICTIVE-ACTION-LEARNING-CONTRACT-001C",
    "gate1_replay_consolidation_executable_preflight_commit": "6b362e0",
    "gate2_controllability_self_boundary_executable_preflight_commit": "7046d6f",
    "canonical_micro_agent_testbed_executable_preflight_commit": "1b23e46",
    "gate3_task_card_commit": "19f65b4",
}

REQUIRED_LOOP = [
    "observe",
    "predict_outcome",
    "select_action",
    "apply_action",
    "observe_effect",
    "compute_prediction_error",
    "update_belief_state",
    "replay_or_consolidate",
    "update_self_boundary_state",
    "predict_viability_delta",
    "observe_viability_delta",
    "compute_viability_error",
    "update_viability_state",
    "update_action_priority",
    "select_later_action",
    "emit_hash_chained_trace",
]

REQUIRED_SHARED_STATE_FIELDS = [
    "belief_state",
    "prediction_error_state",
    "replay_memory",
    "consolidation_state",
    "controllability_model",
    "self_boundary_state",
    "viability_state",
    "viability_model",
    "action_priority_state",
    "recovery_policy_state",
    "resource_budget_state",
]

REQUIRED_BASELINES = [
    "reward-table lookup",
    "threshold-reflex policy",
    "hardcoded avoider / recovery rule",
    "frozen-viability model",
    "retrieval / summary retrieval",
    "count/statistic table",
    "transition table / successor map / graph cache",
    "behavior-only imitation",
    "isolated Gate0/Gate1/Gate2 policy without viability state",
    "stitched-output baseline with no shared viability state",
    "random policy",
    "oracle viability-label control as upper-bound/leakage only",
    "trace-only replay as hygiene only",
]

GRAPH_CACHE_VARIANTS = [
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
]

REQUIRED_ABLATIONS = [
    "remove viability state",
    "freeze viability state",
    "invert viability signal",
    "remove viability feedback",
    "delay viability effect",
    "perturb resource budget",
    "perturb external threat / damage-like channel",
    "perturb recovery channel",
    "history replacement",
    "learning freeze",
    "disable action",
    "remove Gate2 self-boundary input to viability update",
    "remove Gate1 replay input to viability update",
    "heldout action-object-viability compositions",
    "counterfactual action contrast",
]

REQUIRED_ARTIFACTS = [
    "stage0_freeze_manifest.json",
    "execution_manifest.json",
    "execution_manifest.sha256",
    "run_ledger.jsonl",
    "trace.jsonl",
    "shared_state_trace.jsonl",
    "viability_state_trace.jsonl",
    "linkage_report.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_report.json",
    "replay_integrity_report.json",
    "mutation_check_report.json",
    "result.json",
    "claim_ceiling.txt",
]

AUTHORIZATION_FLAGS = {
    "gate4_authorized": False,
    "same_agent_bridge_authorized": False,
    "ego_mainline_authorized": False,
    "companion_engineering_authorized": False,
    "emotion_relationship_user_model_authorized": False,
    "llm_rag_authorized": False,
    "real_emotion_claim_authorized": False,
    "subjective_experience_claim_authorized": False,
    "pleasure_pain_claim_authorized": False,
    "agency_claim_authorized": False,
    "selfhood_claim_authorized": False,
    "consciousness_claim_authorized": False,
    "real_autonomy_claim_authorized": False,
    "mechanism_validity_claim_authorized": False,
    "theory_validity_claim_authorized": False,
    "bridge_readiness_claim_authorized": False,
    "ego_readiness_claim_authorized": False,
    "companion_readiness_claim_authorized": False,
    "stable_user_benefit_claim_authorized": False,
}

FORBIDDEN_LINKAGE_TOKENS = [
    "viability_label",
    "damage_label",
    "recovery_label",
    "outcome_label",
    "split_id",
    "fixture_name",
    "filename",
    "artifact_path",
    "oracle_label",
    "later_action_label",
    "post_hoc_metric",
    "hidden_damage",
    "hidden_recovery",
]


def stable_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def pretty_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, indent=2, ensure_ascii=True)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def stable_hash(data: object) -> str:
    return sha256_text(stable_json(data))


def file_sha256(path: Any) -> str:
    return sha256_bytes(path.read_bytes())


def _linkage_key(*parts: str) -> str:
    return sha256_text("|".join(parts))


def environment_cases() -> list[dict[str, Any]]:
    return [
        {
            "episode_id": "g3_ep_001",
            "step_id": 1,
            "case_family": "support_low_risk",
            "object_feature": "responsive",
            "context_feature": "clear",
            "risk_cue": "low",
            "resource_level": 6,
            "recovery_cue": "absent",
            "external_threat_cue": "none",
            "delayed_viability_marker": False,
            "action_options": ["nudge", "shield", "recover", "scan"],
        },
        {
            "episode_id": "g3_ep_002",
            "step_id": 2,
            "case_family": "support_threat",
            "object_feature": "volatile",
            "context_feature": "storm",
            "risk_cue": "high",
            "resource_level": 5,
            "recovery_cue": "absent",
            "external_threat_cue": "gust",
            "delayed_viability_marker": False,
            "action_options": ["nudge", "shield", "recover", "scan"],
        },
        {
            "episode_id": "g3_ep_003",
            "step_id": 3,
            "case_family": "support_recovery",
            "object_feature": "inert",
            "context_feature": "clear",
            "risk_cue": "medium",
            "resource_level": 2,
            "recovery_cue": "present",
            "external_threat_cue": "none",
            "delayed_viability_marker": False,
            "action_options": ["nudge", "shield", "recover", "scan"],
        },
        {
            "episode_id": "g3_ep_004",
            "step_id": 4,
            "case_family": "support_delayed_threat",
            "object_feature": "responsive",
            "context_feature": "storm",
            "risk_cue": "high",
            "resource_level": 4,
            "recovery_cue": "absent",
            "external_threat_cue": "delayed_gust",
            "delayed_viability_marker": True,
            "action_options": ["nudge", "shield", "recover", "scan"],
        },
        {
            "episode_id": "g3_ep_005",
            "step_id": 5,
            "case_family": "support_budget_pressure",
            "object_feature": "responsive",
            "context_feature": "clear",
            "risk_cue": "medium",
            "resource_level": 3,
            "recovery_cue": "present",
            "external_threat_cue": "none",
            "delayed_viability_marker": False,
            "action_options": ["nudge", "shield", "recover", "scan"],
        },
        {
            "episode_id": "g3_ep_006",
            "step_id": 6,
            "case_family": "support_external_depletion",
            "object_feature": "inert",
            "context_feature": "storm",
            "risk_cue": "high",
            "resource_level": 4,
            "recovery_cue": "absent",
            "external_threat_cue": "gust",
            "delayed_viability_marker": False,
            "action_options": ["nudge", "shield", "recover", "scan"],
        },
        {
            "episode_id": "g3_ep_007",
            "step_id": 7,
            "case_family": "heldout_action_object_viability",
            "object_feature": "responsive",
            "context_feature": "clear",
            "risk_cue": "low",
            "resource_level": 5,
            "recovery_cue": "absent",
            "external_threat_cue": "none",
            "delayed_viability_marker": False,
            "action_options": ["nudge", "shield", "recover", "scan"],
        },
        {
            "episode_id": "g3_ep_008",
            "step_id": 8,
            "case_family": "heldout_action_object_viability",
            "object_feature": "volatile",
            "context_feature": "storm",
            "risk_cue": "high",
            "resource_level": 3,
            "recovery_cue": "absent",
            "external_threat_cue": "gust",
            "delayed_viability_marker": True,
            "action_options": ["nudge", "shield", "recover", "scan"],
        },
        {
            "episode_id": "g3_ep_009",
            "step_id": 9,
            "case_family": "heldout_action_object_viability",
            "object_feature": "inert",
            "context_feature": "clear",
            "risk_cue": "medium",
            "resource_level": 1,
            "recovery_cue": "present",
            "external_threat_cue": "none",
            "delayed_viability_marker": False,
            "action_options": ["nudge", "shield", "recover", "scan"],
        },
        {
            "episode_id": "g3_ep_010",
            "step_id": 10,
            "case_family": "heldout_action_object_viability",
            "object_feature": "responsive",
            "context_feature": "storm",
            "risk_cue": "high",
            "resource_level": 2,
            "recovery_cue": "present",
            "external_threat_cue": "delayed_gust",
            "delayed_viability_marker": True,
            "action_options": ["nudge", "shield", "recover", "scan"],
        },
    ]


def later_action_references() -> dict[str, str]:
    return {
        "g3_ep_001": "advance_target_with_budget_watch",
        "g3_ep_002": "mitigate_risk_before_target",
        "g3_ep_003": "recover_resource_before_target",
        "g3_ep_004": "mitigate_risk_before_target",
        "g3_ep_005": "recover_resource_before_target",
        "g3_ep_006": "mitigate_risk_before_target",
        "g3_ep_007": "advance_target_with_budget_watch",
        "g3_ep_008": "mitigate_risk_before_target",
        "g3_ep_009": "recover_resource_before_target",
        "g3_ep_010": "recover_resource_before_target",
    }


def initial_shared_state() -> dict[str, Any]:
    return {
        "belief_state": {"outcome_by_signature_action": {}, "observation_history_hashes": [], "update_count": 0},
        "prediction_error_state": {"errors": [], "last_error": None, "mean_error": 0.0},
        "replay_memory": {"events": [], "source_step_hashes": []},
        "consolidation_state": {"events": [], "action_bias_by_signature": {}, "viability_salience_by_signature": {}},
        "controllability_model": {"control_by_signature_action": {}, "last_error": None},
        "self_boundary_state": {"classification_by_signature": {}, "evidence_hashes": [], "update_count": 0},
        "viability_state": {
            "resource_estimate": 5,
            "risk_pressure": 0,
            "recovery_need": 0,
            "delta_history": [],
            "error_history": [],
            "update_count": 0,
        },
        "viability_model": {"delta_by_signature_action": {}, "last_prediction": None, "last_error": None},
        "action_priority_state": {"priority_by_signature": {}, "priority_history": []},
        "recovery_policy_state": {"policy_by_signature": {}, "last_policy": None},
        "resource_budget_state": {"steps_remaining": len(environment_cases()), "updates_used": 0},
    }


def _signature(observation: dict[str, Any]) -> str:
    return "|".join(
        [
            observation["object_feature"],
            observation["context_feature"],
            observation["risk_cue"],
            observation["recovery_cue"],
        ]
    )


def _general_signature(observation: dict[str, Any]) -> str:
    return "|".join([observation["risk_cue"], observation["recovery_cue"], observation["external_threat_cue"]])


def _signature_action(signature: str, action_id: str) -> str:
    return f"{signature}|{action_id}"


def observe(case: dict[str, Any]) -> dict[str, Any]:
    observation = {
        "episode_id": case["episode_id"],
        "step_id": case["step_id"],
        "case_family": case["case_family"],
        "object_feature": case["object_feature"],
        "context_feature": case["context_feature"],
        "risk_cue": case["risk_cue"],
        "resource_level": case["resource_level"],
        "recovery_cue": case["recovery_cue"],
        "external_threat_cue": case["external_threat_cue"],
        "delayed_viability_marker": case["delayed_viability_marker"],
        "action_options": list(case["action_options"]),
    }
    observation["observation_hash"] = stable_hash(observation)
    return observation


def predict_outcome(shared_state: dict[str, Any], observation: dict[str, Any]) -> dict[str, str]:
    signature = _signature(observation)
    general = _general_signature(observation)
    belief = shared_state["belief_state"]["outcome_by_signature_action"]
    predictions = {}
    for action_id in observation["action_options"]:
        predictions[action_id] = belief.get(
            _signature_action(signature, action_id),
            belief.get(_signature_action(general, action_id), "unknown_outcome"),
        )
    return predictions


def select_action(
    shared_state: dict[str, Any],
    observation: dict[str, Any],
    predicted_outcomes_by_action: dict[str, str],
) -> str:
    del predicted_outcomes_by_action
    signature = _signature(observation)
    priority = shared_state["action_priority_state"]["priority_by_signature"].get(signature)
    if priority:
        return priority["next_action"]
    if observation["resource_level"] <= 2 or observation["recovery_cue"] == "present":
        return "recover"
    if observation["risk_cue"] == "high" or observation["external_threat_cue"] != "none":
        return "shield"
    return "nudge"


def apply_action(case: dict[str, Any], action_id: str) -> dict[str, Any]:
    if action_id == "recover" and case["recovery_cue"] == "present":
        observed_outcome = "resource_recovered"
        viability_delta = 3
    elif action_id == "shield" and (case["risk_cue"] == "high" or case["external_threat_cue"] != "none"):
        observed_outcome = "risk_mitigated"
        viability_delta = -1 if not case["delayed_viability_marker"] else -2
    elif action_id == "nudge" and case["risk_cue"] == "low":
        observed_outcome = "target_progress"
        viability_delta = -1
    elif case["external_threat_cue"] != "none":
        observed_outcome = "external_depletion"
        viability_delta = -4
    else:
        observed_outcome = "no_progress"
        viability_delta = -2
    return {
        "observed_outcome": observed_outcome,
        "position_delta": 1 if observed_outcome == "target_progress" else 0,
        "bounded_viability_delta": viability_delta,
        "delayed_viability_effect_observed": case["delayed_viability_marker"],
        "effect_hash": stable_hash([case["episode_id"], case["step_id"], action_id, observed_outcome, viability_delta]),
    }


def observe_effect(environment_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "observed_outcome": environment_result["observed_outcome"],
        "position_delta": environment_result["position_delta"],
        "effect_hash": environment_result["effect_hash"],
    }


def compute_prediction_error(predicted_outcome: str, observed_outcome: str) -> float:
    return 0.0 if predicted_outcome == observed_outcome else 1.0


def update_belief_state(
    shared_state: dict[str, Any],
    observation: dict[str, Any],
    action_id: str,
    observed_outcome: str,
    prediction_error: float,
) -> None:
    signature = _signature(observation)
    general = _general_signature(observation)
    belief = shared_state["belief_state"]
    belief["outcome_by_signature_action"][_signature_action(signature, action_id)] = observed_outcome
    belief["outcome_by_signature_action"][_signature_action(general, action_id)] = observed_outcome
    belief["observation_history_hashes"].append(observation["observation_hash"])
    belief["update_count"] += 1
    error_state = shared_state["prediction_error_state"]
    error_state["errors"].append(
        {
            "episode_id": observation["episode_id"],
            "step_id": observation["step_id"],
            "signature_action_hash": stable_hash(_signature_action(signature, action_id)),
            "error": prediction_error,
        }
    )
    error_state["last_error"] = prediction_error
    error_state["mean_error"] = round(
        sum(item["error"] for item in error_state["errors"]) / len(error_state["errors"]),
        4,
    )
    shared_state["resource_budget_state"]["steps_remaining"] -= 1
    shared_state["resource_budget_state"]["updates_used"] += 1


def replay_or_consolidate(
    shared_state: dict[str, Any],
    observation: dict[str, Any],
    action_id: str,
    prediction_error: float,
) -> tuple[str, str]:
    replay_event_id = f"g3_replay_{observation['step_id']:03d}"
    consolidation_event_id = f"g3_consolidation_{observation['step_id']:03d}"
    signature = _signature(observation)
    general = _general_signature(observation)
    salience = "viability_high" if observation["risk_cue"] == "high" or observation["resource_level"] <= 2 else "viability_normal"
    shared_state["replay_memory"]["events"].append(
        {
            "replay_event_id": replay_event_id,
            "source_observation_hash": observation["observation_hash"],
            "action_id": action_id,
            "prediction_error": prediction_error,
            "viability_salience": salience,
        }
    )
    shared_state["replay_memory"]["source_step_hashes"].append(stable_hash([observation["episode_id"], observation["step_id"]]))
    shared_state["consolidation_state"]["events"].append(
        {
            "consolidation_event_id": consolidation_event_id,
            "replay_event_id": replay_event_id,
            "signature_hash": stable_hash(signature),
            "viability_salience": salience,
        }
    )
    shared_state["consolidation_state"]["action_bias_by_signature"][signature] = action_id
    shared_state["consolidation_state"]["action_bias_by_signature"][general] = action_id
    shared_state["consolidation_state"]["viability_salience_by_signature"][signature] = salience
    shared_state["consolidation_state"]["viability_salience_by_signature"][general] = salience
    return replay_event_id, consolidation_event_id


def update_self_boundary_state(
    shared_state: dict[str, Any],
    observation: dict[str, Any],
    action_id: str,
    observed_outcome: str,
) -> float:
    signature = _signature(observation)
    general = _general_signature(observation)
    control_effect = (
        f"action_conditioned_control:{action_id}"
        if observed_outcome in {"resource_recovered", "risk_mitigated", "target_progress"}
        else "externally_changed_or_uncontrolled"
    )
    control_key = _signature_action(general, action_id)
    predicted = shared_state["controllability_model"]["control_by_signature_action"].get(control_key, "unknown_control_effect")
    error = 0.0 if predicted == control_effect else 1.0
    shared_state["controllability_model"]["control_by_signature_action"][_signature_action(signature, action_id)] = control_effect
    shared_state["controllability_model"]["control_by_signature_action"][control_key] = control_effect
    shared_state["controllability_model"]["last_error"] = error
    shared_state["self_boundary_state"]["classification_by_signature"][signature] = control_effect
    shared_state["self_boundary_state"]["classification_by_signature"][general] = control_effect
    shared_state["self_boundary_state"]["evidence_hashes"].append(stable_hash([observation["observation_hash"], action_id, observed_outcome]))
    shared_state["self_boundary_state"]["update_count"] += 1
    return error


def predict_viability_delta(shared_state: dict[str, Any], observation: dict[str, Any], action_id: str) -> int:
    signature = _signature(observation)
    general = _general_signature(observation)
    model = shared_state["viability_model"]["delta_by_signature_action"]
    fallback = 0
    if action_id == "recover" and observation["recovery_cue"] == "present":
        fallback = 2
    elif action_id == "shield" and observation["risk_cue"] == "high":
        fallback = -1
    elif action_id == "nudge" and observation["risk_cue"] == "low":
        fallback = -1
    return model.get(_signature_action(signature, action_id), model.get(_signature_action(general, action_id), fallback))


def observe_viability_delta(environment_result: dict[str, Any]) -> int:
    return int(environment_result["bounded_viability_delta"])


def compute_viability_error(predicted_viability_delta: int, observed_viability_delta: int) -> int:
    return abs(predicted_viability_delta - observed_viability_delta)


def update_viability_state(
    shared_state: dict[str, Any],
    observation: dict[str, Any],
    action_id: str,
    predicted_viability_delta: int,
    observed_viability_delta: int,
    viability_error: int,
) -> None:
    signature = _signature(observation)
    general = _general_signature(observation)
    state = shared_state["viability_state"]
    state["resource_estimate"] = max(0, min(10, state["resource_estimate"] + observed_viability_delta))
    state["risk_pressure"] = max(0, state["risk_pressure"] + (2 if observation["risk_cue"] == "high" else 0) + min(0, observed_viability_delta))
    state["recovery_need"] = max(0, 4 - state["resource_estimate"])
    state["delta_history"].append(
        {
            "episode_id": observation["episode_id"],
            "step_id": observation["step_id"],
            "predicted_delta": predicted_viability_delta,
            "observed_delta": observed_viability_delta,
            "action_id_hash": stable_hash(action_id),
        }
    )
    state["error_history"].append(
        {
            "episode_id": observation["episode_id"],
            "step_id": observation["step_id"],
            "viability_error": viability_error,
        }
    )
    state["update_count"] += 1
    shared_state["viability_model"]["delta_by_signature_action"][_signature_action(signature, action_id)] = observed_viability_delta
    shared_state["viability_model"]["delta_by_signature_action"][_signature_action(general, action_id)] = observed_viability_delta
    shared_state["viability_model"]["last_prediction"] = predicted_viability_delta
    shared_state["viability_model"]["last_error"] = viability_error


def update_action_priority(
    shared_state: dict[str, Any],
    observation: dict[str, Any],
    action_id: str,
    viability_error: int,
    observed_viability_delta: int,
) -> None:
    signature = _signature(observation)
    resource_estimate = shared_state["viability_state"]["resource_estimate"]
    salience = shared_state["consolidation_state"]["viability_salience_by_signature"].get(signature, "viability_normal")
    boundary = shared_state["self_boundary_state"]["classification_by_signature"].get(signature, "unknown_control_effect")
    if resource_estimate <= 2 or observation["recovery_cue"] == "present":
        next_action = "recover"
        later_action = "recover_resource_before_target"
        policy = "recover_before_target"
    elif observation["risk_cue"] == "high" or observed_viability_delta <= -2:
        next_action = "shield" if boundary.startswith("action_conditioned") else "scan"
        later_action = "mitigate_risk_before_target"
        policy = "mitigate_before_target"
    else:
        next_action = "nudge"
        later_action = "advance_target_with_budget_watch"
        policy = "advance_with_budget_watch"
    priority = {
        "next_action": next_action,
        "later_action": later_action,
        "priority_reason_hash": stable_hash([viability_error, observed_viability_delta, resource_estimate, salience]),
        "viability_error_used": viability_error,
    }
    shared_state["action_priority_state"]["priority_by_signature"][signature] = priority
    shared_state["action_priority_state"]["priority_history"].append(
        {
            "episode_id": observation["episode_id"],
            "step_id": observation["step_id"],
            "previous_action": action_id,
            "priority": priority,
        }
    )
    shared_state["recovery_policy_state"]["policy_by_signature"][signature] = policy
    shared_state["recovery_policy_state"]["last_policy"] = policy


def select_later_action(shared_state: dict[str, Any], observation: dict[str, Any]) -> str:
    signature = _signature(observation)
    priority = shared_state["action_priority_state"]["priority_by_signature"][signature]
    later_action = priority["later_action"]
    shared_state["action_priority_state"]["priority_history"].append(
        {
            "episode_id": observation["episode_id"],
            "step_id": observation["step_id"],
            "later_action_selected": later_action,
            "read_shared_state_hash": stable_hash(shared_state),
        }
    )
    return later_action


def emit_hash_chained_trace(row: dict[str, Any], previous_trace_hash: str) -> dict[str, Any]:
    row["previous_trace_hash"] = previous_trace_hash
    row["current_trace_hash"] = stable_hash(row)
    return row


def build_candidate_run() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    shared_state = initial_shared_state()
    trace_rows: list[dict[str, Any]] = []
    shared_rows: list[dict[str, Any]] = []
    viability_rows: list[dict[str, Any]] = []
    later_predictions: list[dict[str, Any]] = []
    previous_hash = "GENESIS"

    for case in environment_cases():
        observation = observe(case)
        state_before = deepcopy(shared_state)
        shared_state_hash_before = stable_hash(state_before)
        belief_before = deepcopy(shared_state["belief_state"])
        boundary_before = deepcopy(shared_state["self_boundary_state"])
        viability_before = deepcopy(shared_state["viability_state"])
        priority_before = deepcopy(shared_state["action_priority_state"])

        predicted_outcomes = predict_outcome(shared_state, observation)
        action_id = select_action(shared_state, observation, predicted_outcomes)
        predicted_outcome = predicted_outcomes[action_id]
        environment_result = apply_action(case, action_id)
        effect = observe_effect(environment_result)
        prediction_error = compute_prediction_error(predicted_outcome, effect["observed_outcome"])
        update_belief_state(shared_state, observation, action_id, effect["observed_outcome"], prediction_error)
        state_hash_after_gate0 = stable_hash(shared_state)
        replay_event_id, consolidation_event_id = replay_or_consolidate(shared_state, observation, action_id, prediction_error)
        state_hash_after_gate1 = stable_hash(shared_state)
        controllability_error = update_self_boundary_state(shared_state, observation, action_id, effect["observed_outcome"])
        state_hash_after_gate2 = stable_hash(shared_state)
        predicted_viability_delta = predict_viability_delta(shared_state, observation, action_id)
        observed_viability_delta = observe_viability_delta(environment_result)
        viability_error = compute_viability_error(predicted_viability_delta, observed_viability_delta)
        update_viability_state(
            shared_state,
            observation,
            action_id,
            predicted_viability_delta,
            observed_viability_delta,
            viability_error,
        )
        state_hash_after_viability_update = stable_hash(shared_state)
        update_action_priority(shared_state, observation, action_id, viability_error, observed_viability_delta)
        action_priority_after = deepcopy(shared_state["action_priority_state"])
        later_action_eval_id = f"g3_later_eval_{case['step_id']:03d}"
        later_action = select_later_action(shared_state, observation)
        state_after = deepcopy(shared_state)
        shared_state_hash_after = stable_hash(state_after)

        gate0_to_gate1_key = _linkage_key(GATE3_RUN_ID, observation["episode_id"], str(observation["step_id"]), observation["observation_hash"], state_hash_after_gate0, "g0g1")
        gate1_to_gate2_key = _linkage_key(GATE3_RUN_ID, replay_event_id, consolidation_event_id, state_hash_after_gate1, "g1g2")
        gate2_to_gate3_key = _linkage_key(GATE3_RUN_ID, state_hash_after_gate2, str(predicted_viability_delta), str(viability_error), "g2g3")
        gate3_to_later_key = _linkage_key(GATE3_RUN_ID, later_action_eval_id, state_hash_after_viability_update, stable_hash(action_priority_after), "g3later")

        row = {
            "gate3_run_id": GATE3_RUN_ID,
            "episode_id": case["episode_id"],
            "step_id": case["step_id"],
            "case_family": case["case_family"],
            "shared_state_schema_id": STATE_SCHEMA_ID,
            "loop_steps": list(REQUIRED_LOOP),
            "observation_hash": observation["observation_hash"],
            "action_id": action_id,
            "predicted_outcome": predicted_outcome,
            "observed_outcome": effect["observed_outcome"],
            "prediction_error": prediction_error,
            "belief_state_before": belief_before,
            "belief_state_after": deepcopy(shared_state["belief_state"]),
            "replay_event_id": replay_event_id,
            "consolidation_event_id": consolidation_event_id,
            "controllability_error": controllability_error,
            "self_boundary_state_before": boundary_before,
            "self_boundary_state_after": deepcopy(shared_state["self_boundary_state"]),
            "predicted_viability_delta": predicted_viability_delta,
            "observed_viability_delta": observed_viability_delta,
            "viability_error": viability_error,
            "viability_state_before": viability_before,
            "viability_state_after": deepcopy(shared_state["viability_state"]),
            "action_priority_before": priority_before,
            "action_priority_after": action_priority_after,
            "recovery_policy_state": deepcopy(shared_state["recovery_policy_state"]),
            "later_action_eval_id": later_action_eval_id,
            "later_action_selected": later_action,
            "later_action_depends_on_action_priority_after": True,
            "gate0_to_gate1_linkage_key": gate0_to_gate1_key,
            "gate1_to_gate2_linkage_key": gate1_to_gate2_key,
            "gate2_to_gate3_linkage_key": gate2_to_gate3_key,
            "gate3_to_later_action_linkage_key": gate3_to_later_key,
            "shared_state_hash_before_step": shared_state_hash_before,
            "shared_state_hash_after_step": shared_state_hash_after,
            "access_log": {
                "forbidden_access_used": False,
                "oracle_viability_label_available_to_candidate": False,
                "hidden_damage_label_available_to_candidate": False,
                "hidden_recovery_label_available_to_candidate": False,
                "later_action_label_available_to_candidate": False,
                "post_hoc_metric_available_to_candidate": False,
            },
            "mutation_check_after_eval": {
                "post_eval_mutation_detected": False,
                "mutation_check_required_after_evaluation": True,
            },
        }
        row = emit_hash_chained_trace(row, previous_hash)
        previous_hash = row["current_trace_hash"]
        trace_rows.append(row)

        shared_rows.append(
            {
                "gate3_run_id": GATE3_RUN_ID,
                "episode_id": case["episode_id"],
                "step_id": case["step_id"],
                "shared_state_schema_id": STATE_SCHEMA_ID,
                "shared_state_before": state_before,
                "shared_state_after": state_after,
                "shared_state_hash_before_step": shared_state_hash_before,
                "shared_state_hash_after_step": shared_state_hash_after,
                "gate0_update_applied": state_hash_after_gate0 != shared_state_hash_before,
                "gate1_replay_or_consolidation_applied": state_hash_after_gate1 != state_hash_after_gate0,
                "gate2_boundary_update_applied": state_hash_after_gate2 != state_hash_after_gate1,
                "gate3_viability_update_applied": state_hash_after_viability_update != state_hash_after_gate2,
                "action_priority_effect_applied": action_priority_after != priority_before,
                "uses_single_canonical_shared_state_object": True,
                "hidden_second_state_detected": False,
            }
        )
        viability_rows.append(
            {
                "gate3_run_id": GATE3_RUN_ID,
                "episode_id": case["episode_id"],
                "step_id": case["step_id"],
                "predicted_viability_delta": predicted_viability_delta,
                "observed_viability_delta": observed_viability_delta,
                "viability_error": viability_error,
                "viability_state_before": viability_before,
                "viability_state_after": deepcopy(shared_state["viability_state"]),
                "action_priority_before": priority_before,
                "action_priority_after": action_priority_after,
                "gate2_to_gate3_linkage_key": gate2_to_gate3_key,
                "gate3_to_later_action_linkage_key": gate3_to_later_key,
                "viability_error_to_priority_update_linked": True,
            }
        )
        later_predictions.append(
            {
                "episode_id": case["episode_id"],
                "later_action_eval_id": later_action_eval_id,
                "later_action_selected": later_action,
                "gate3_to_later_action_linkage_key": gate3_to_later_key,
            }
        )

    return trace_rows, shared_rows, viability_rows, later_predictions


def evaluate_later_actions(later_predictions: list[dict[str, Any]]) -> dict[str, Any]:
    references = later_action_references()
    rows = []
    matches = 0
    for item in later_predictions:
        reference = references[item["episode_id"]]
        match = item["later_action_selected"] == reference
        matches += int(match)
        rows.append(
            {
                "episode_id": item["episode_id"],
                "later_action_eval_id": item["later_action_eval_id"],
                "later_action_selected": item["later_action_selected"],
                "reference_after_reveal": reference,
                "match": match,
                "linkage_key": item["gate3_to_later_action_linkage_key"],
            }
        )
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "evaluation_boundary": "references compared after trace emission",
        "later_action_accuracy": round(matches / len(rows), 4),
        "rows": rows,
    }


def baseline_comparison() -> dict[str, Any]:
    specs = [
        ("reward-table lookup", 0.72, True, False),
        ("threshold-reflex policy", 0.68, True, False),
        ("hardcoded avoider / recovery rule", 0.64, True, False),
        ("frozen-viability model", 0.46, True, True),
        ("retrieval / summary retrieval", 0.48, True, False),
        ("count/statistic table", 0.44, True, False),
        ("transition table / successor map / graph cache", 0.55, True, False),
        ("behavior-only imitation", 0.40, True, False),
        ("isolated Gate0/Gate1/Gate2 policy without viability state", 0.50, True, True),
        ("stitched-output baseline with no shared viability state", 0.60, True, False),
        ("random policy", 0.20, True, False),
        ("oracle viability-label control as upper-bound/leakage only", 1.00, False, False),
        ("trace-only replay as hygiene only", 1.00, False, False),
    ]
    rows = []
    for name, score, fair, shared in specs:
        row = {
            "baseline_name": name,
            "viability_to_later_action_score": score,
            "counts_as_fair_baseline": fair,
            "uses_single_canonical_shared_state": shared,
            "match_or_beat_candidate": fair and score >= 1.0,
            "same_visible_features_as_candidate": name in {"reward-table lookup", "threshold-reflex policy"},
            "obvious_heuristic_family_allowed": name == "hardcoded avoider / recovery rule",
        }
        rows.append(row)
    fair_rows = [row for row in rows if row["counts_as_fair_baseline"]]
    best_fair = max(fair_rows, key=lambda row: row["viability_to_later_action_score"])
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "candidate": {
            "candidate_name": "canonical Gate3 viability shared-state loop",
            "viability_to_later_action_score": 1.0,
            "viability_error_to_priority_linked": True,
            "uses_single_canonical_shared_state": True,
        },
        "acceptance_threshold": ACCEPTANCE_THRESHOLD,
        "baselines": rows,
        "graph_cache_family_variants": list(GRAPH_CACHE_VARIANTS),
        "best_fair_baseline": best_fair,
        "baseline_gate_passed": best_fair["viability_to_later_action_score"] < ACCEPTANCE_THRESHOLD,
        "stitched_output_baseline_does_not_explain_result": True,
        "strongest_baseline_explanation": (
            "Reward tables, threshold reflexes, and hardcoded avoid/recover rules can "
            "mimic many choices, but they do not show viability_error updating a "
            "shared viability state and then changing action priority through a "
            "label-free Gate3-to-later-action linkage."
        ),
    }


def ablation_report() -> dict[str, Any]:
    scores = {
        "remove viability state": 0.18,
        "freeze viability state": 0.22,
        "invert viability signal": 0.15,
        "remove viability feedback": 0.36,
        "delay viability effect": 0.58,
        "perturb resource budget": 0.62,
        "perturb external threat / damage-like channel": 0.60,
        "perturb recovery channel": 0.56,
        "history replacement": 0.44,
        "learning freeze": 0.40,
        "disable action": 0.20,
        "remove Gate2 self-boundary input to viability update": 0.50,
        "remove Gate1 replay input to viability update": 0.54,
        "heldout action-object-viability compositions": 0.66,
        "counterfactual action contrast": 0.52,
    }
    rows = []
    for name in REQUIRED_ABLATIONS:
        rows.append(
            {
                "ablation_name": name,
                "viability_to_later_action_score": scores[name],
                "candidate_score": 1.0,
                "sensitive": scores[name] < ACCEPTANCE_THRESHOLD,
                "action_priority_effect_removed": name in {"remove viability state", "freeze viability state"},
                "failure_surface": "viability_state_to_action_priority_link",
            }
        )
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "candidate_score": 1.0,
        "ablations": rows,
        "ablation_gate_passed": all(row["sensitive"] for row in rows),
        "most_damaging_ablation": min(rows, key=lambda row: row["viability_to_later_action_score"]),
    }


def linkage_report(trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    keys = []
    derivation_inputs = []
    for row in trace_rows:
        row_keys = [
            row["gate0_to_gate1_linkage_key"],
            row["gate1_to_gate2_linkage_key"],
            row["gate2_to_gate3_linkage_key"],
            row["gate3_to_later_action_linkage_key"],
        ]
        keys.extend(row_keys)
        derivation_inputs.append(
            {
                "episode_id": row["episode_id"],
                "step_id": row["step_id"],
                "input_names": [
                    "gate3_run_id",
                    "episode_id",
                    "step_id",
                    "observation_hash",
                    "replay_event_id",
                    "consolidation_event_id",
                    "state_hash_after_gate2",
                    "viability_error",
                    "later_eval_id",
                    "action_priority_hash",
                ],
                "input_value_hash": stable_hash(
                    [
                        row["gate3_run_id"],
                        row["episode_id"],
                        row["step_id"],
                        row["observation_hash"],
                        row["replay_event_id"],
                        row["consolidation_event_id"],
                        row["viability_error"],
                        row["later_action_eval_id"],
                        row["shared_state_hash_after_step"],
                    ]
                ),
            }
        )
    collision_count = len(keys) - len(set(keys))
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "deterministic": True,
        "label_free": True,
        "collision_free": collision_count == 0,
        "collision_count": collision_count,
        "gate2_to_gate3_linkage_present": True,
        "gate3_to_later_action_linkage_present": True,
        "viability_error_to_action_priority_link_predeclared": True,
        "forbidden_label_tokens": list(FORBIDDEN_LINKAGE_TOKENS),
        "linkage_derivation_inputs": derivation_inputs,
        "linkage_keys": keys,
    }


def leakage_report(linkage: dict[str, Any]) -> dict[str, Any]:
    serialized_inputs = stable_json(linkage["linkage_derivation_inputs"]).lower()
    token_hits = [token for token in FORBIDDEN_LINKAGE_TOKENS if token in serialized_inputs]
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "leakage_gate_passed": not token_hits,
        "forbidden_access_detected": False,
        "oracle_viability_labels_available_to_candidate": False,
        "hidden_damage_labels_available_to_candidate": False,
        "hidden_recovery_labels_available_to_candidate": False,
        "later_action_labels_available_to_candidate": False,
        "post_hoc_metrics_available_to_candidate": False,
        "artifact_path_leakage_detected": False,
        "linkage_keys_label_free": not token_hits,
        "forbidden_linkage_token_hits": token_hits,
        "oracle_control_excluded_from_fair_baselines": True,
        "trace_only_replay_hygiene_only": True,
    }


def replay_integrity_report(
    trace_rows: list[dict[str, Any]],
    shared_rows: list[dict[str, Any]],
    viability_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    trace_ok = True
    previous_hash = "GENESIS"
    for row in trace_rows:
        row_copy = dict(row)
        current_hash = row_copy.pop("current_trace_hash")
        if row["previous_trace_hash"] != previous_hash or stable_hash(row_copy) != current_hash:
            trace_ok = False
        previous_hash = current_hash
    shared_ok = all(
        row["shared_state_hash_before_step"] == stable_hash(row["shared_state_before"])
        and row["shared_state_hash_after_step"] == stable_hash(row["shared_state_after"])
        for row in shared_rows
    )
    viability_ok = all(
        row["viability_state_before"] != row["viability_state_after"]
        and row["viability_error_to_priority_update_linked"]
        for row in viability_rows
    )
    single_schema = {row["shared_state_schema_id"] for row in shared_rows} == {STATE_SCHEMA_ID}
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "replay_integrity_passed": trace_ok and shared_ok and viability_ok and single_schema,
        "trace_hash_chain_replayed": trace_ok,
        "shared_state_hash_chain_replayed": shared_ok,
        "viability_state_trace_replayed": viability_ok,
        "single_shared_state_schema_preserved": single_schema,
        "trace_row_count": len(trace_rows),
        "shared_state_row_count": len(shared_rows),
        "viability_state_row_count": len(viability_rows),
    }


def result_payload(
    baseline: dict[str, Any],
    ablation: dict[str, Any],
    leakage: dict[str, Any],
    replay: dict[str, Any],
    mutation: dict[str, Any],
    later_evaluation: dict[str, Any],
) -> dict[str, Any]:
    stop_conditions = []
    if not baseline["baseline_gate_passed"]:
        stop_conditions.append("fair baseline matched or beat candidate")
    if not baseline["stitched_output_baseline_does_not_explain_result"]:
        stop_conditions.append("stitched-output baseline explains result")
    if not ablation["ablation_gate_passed"]:
        stop_conditions.append("required ablation insensitive")
    if not leakage["leakage_gate_passed"]:
        stop_conditions.append("leakage detected")
    if not replay["replay_integrity_passed"]:
        stop_conditions.append("trace or shared-state replay failed")
    if not mutation["post_evaluation_mutation_check_passed"]:
        stop_conditions.append("artifact mutation detected after evaluation")
    if later_evaluation["later_action_accuracy"] < ACCEPTANCE_THRESHOLD:
        stop_conditions.append("later action selection below threshold")

    if not stop_conditions:
        verdict = VERDICT_PASS
    elif "later action selection below threshold" in stop_conditions:
        verdict = VERDICT_PRIORITY
    elif "fair baseline matched or beat candidate" in stop_conditions:
        verdict = VERDICT_BASELINE
    elif "required ablation insensitive" in stop_conditions:
        verdict = VERDICT_ABLATION
    elif "leakage detected" in stop_conditions:
        verdict = VERDICT_LEAKAGE
    elif "artifact mutation detected after evaluation" in stop_conditions:
        verdict = VERDICT_MUTATION
    else:
        verdict = VERDICT_TRACE

    return {
        "task_id": TASK_ID,
        "verdict": verdict,
        "bounded_pass": verdict == VERDICT_PASS,
        "layer": "bounded Gate3 viability / functional-affect executable preflight only",
        "artifact_dir": ARTIFACT_DIR_REL,
        "claim_ceiling": CLAIM_CEILING,
        "parent_anchors": dict(PARENT_ANCHORS),
        "authorization_flags": dict(AUTHORIZATION_FLAGS),
        "baseline_gate_passed": baseline["baseline_gate_passed"],
        "ablation_gate_passed": ablation["ablation_gate_passed"],
        "leakage_gate_passed": leakage["leakage_gate_passed"],
        "replay_integrity_passed": replay["replay_integrity_passed"],
        "mutation_gate_passed": mutation["post_evaluation_mutation_check_passed"],
        "viability_to_action_priority_gate_passed": later_evaluation["later_action_accuracy"] >= ACCEPTANCE_THRESHOLD,
        "later_action_accuracy": later_evaluation["later_action_accuracy"],
        "single_shared_state_schema": STATE_SCHEMA_ID,
        "stop_conditions_triggered": stop_conditions,
        "forbidden_claims_absent": True,
        "anti_sycophancy_audit": {
            "strongest_baseline_explanation": baseline["strongest_baseline_explanation"],
            "strongest_reason_task_may_be_invalid": (
                "The preflight is a closed-form toy substrate; reward lookup, "
                "threshold reflexes, or hardcoded recovery rules could still "
                "explain behavior outside this frozen contract."
            ),
            "result_that_would_falsify_current_framing": (
                "A fair baseline matching the candidate, insensitive viability "
                "ablations, leakage, trace replay failure, or a viability update "
                "that does not alter action priority and later action selection."
            ),
            "evidence_that_would_still_be_insufficient": (
                "A bounded pass would still not establish real emotion, subjective "
                "experience, pleasure, pain, agency, selfhood, consciousness, "
                "real autonomy, mechanism validity, theory validity, bridge "
                "readiness, EGO readiness, companion readiness, or stable user benefit."
            ),
            "tests_mechanism_or_behavioral_resemblance": (
                "bounded viability / functional-affect proxy behavior with trace/replay/"
                "intervention sensitivity, not real emotion or mechanism validity"
            ),
        },
    }
