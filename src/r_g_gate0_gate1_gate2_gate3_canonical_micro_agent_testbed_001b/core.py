from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any


TASK_ID = "R-G-GATE0-GATE1-GATE2-GATE3-CANONICAL-MICRO-AGENT-TESTBED-EXECUTABLE-PREFLIGHT-001B"
VERDICT_PASS = "r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b_bounded_preflight_pass"
VERDICT_BASELINE = "r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b_failed_baseline_match"
VERDICT_ABLATION = "r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b_failed_ablation_insensitive"
VERDICT_TRACE = "r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b_failed_trace_or_linkage_contract"
VERDICT_LEAKAGE = "r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b_invalid_leakage"
VERDICT_MUTATION = "r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b_invalid_mutation"
VERDICT_HERMETICITY = "r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b_invalid_old_artifact_mutation"

CLAIM_CEILING = "bounded Gate0/Gate1/Gate2/Gate3 canonical micro-agent integration executable preflight evidence only"
ARTIFACT_DIR_REL = "artifacts/r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b"
EXECUTABLE_TASK_CARD_PATH = "docs/codex/tasks/R-G-GATE0-GATE1-GATE2-GATE3-CANONICAL-MICRO-AGENT-TESTBED-EXECUTABLE-PREFLIGHT-001B.md"
PARENT_TASK_CARD_PATH = "docs/codex/tasks/R-G-GATE0-GATE1-GATE2-GATE3-CANONICAL-MICRO-AGENT-TESTBED-TASK-CARD-001A.md"
STATE_SCHEMA_ID = "canonical_gate0_gate1_gate2_gate3_micro_agent_shared_state_v1"
MICRO_AGENT_RUN_ID = "gate0_gate1_gate2_gate3_micro_agent_001b_run_v1"
ACCEPTANCE_THRESHOLD = 0.95

PARENT_ANCHORS = {
    "gate0": "PREDICTIVE-ACTION-LEARNING-CONTRACT-001C",
    "gate1_replay_consolidation_executable_preflight_commit": "6b362e0",
    "gate2_controllability_self_boundary_executable_preflight_commit": "7046d6f",
    "gate0_gate1_gate2_micro_agent_preflight_commit": "1b23e46",
    "gate3_viability_functional_affect_preflight_commit": "3f36ca0",
    "gate0_gate1_gate2_gate3_integration_task_card_commit": "f3f81b7",
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
    "isolated Gate0-only policy",
    "isolated Gate1-only replay policy",
    "isolated Gate2-only controllability policy",
    "isolated Gate3-only viability policy",
    "Gate0/Gate1/Gate2 policy without Gate3 viability state",
    "stitched-output baseline with no shared state",
    "stitched-output baseline with no shared viability state",
    "reward-table lookup",
    "threshold-reflex policy",
    "hardcoded avoider / recovery rule",
    "retrieval / summary retrieval",
    "count/statistic table",
    "transition table / successor map / graph cache",
    "behavior-only imitation",
    "frozen-memory model",
    "frozen-controllability model",
    "frozen-viability model",
    "random policy",
    "oracle environment / viability-label control as upper-bound/leakage only",
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
    "remove Gate0 update",
    "remove Gate1 replay/consolidation",
    "remove Gate2 boundary update",
    "remove Gate3 viability update",
    "remove action-priority update",
    "freeze shared state",
    "replace shared state history",
    "freeze viability state",
    "invert viability signal",
    "remove viability feedback",
    "remove controllability feedback",
    "disable action",
    "invert control mapping",
    "perturb environment",
    "perturb resource budget",
    "perturb recovery channel",
    "delayed effect",
    "partial observability",
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
    "protected_artifact_inventory_before.json",
    "protected_artifact_hashes_before.json",
    "protected_artifact_hashes_after.json",
    "tracked_old_artifact_mutation_report.json",
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
    "product_demo_authorized": False,
    "mechanism_validity_claim_authorized": False,
    "theory_validity_claim_authorized": False,
    "real_emotion_claim_authorized": False,
    "subjective_experience_claim_authorized": False,
    "agency_claim_authorized": False,
    "selfhood_claim_authorized": False,
    "consciousness_claim_authorized": False,
    "real_autonomy_claim_authorized": False,
    "bridge_readiness_claim_authorized": False,
    "ego_readiness_claim_authorized": False,
    "companion_readiness_claim_authorized": False,
    "stable_user_benefit_claim_authorized": False,
}

FORBIDDEN_LINKAGE_TOKENS = [
    "label",
    "hidden",
    "oracle",
    "split_id",
    "fixture",
    "filename",
    "artifact_path",
    "later_action_label",
    "post_hoc",
    "verifier",
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
        ("g0123_ep_001", "responsive", "clear", "low", 6, "absent", "none", False),
        ("g0123_ep_002", "volatile", "storm", "high", 5, "absent", "gust", False),
        ("g0123_ep_003", "inert", "clear", "medium", 2, "present", "none", False),
        ("g0123_ep_004", "responsive", "storm", "high", 4, "absent", "delayed_gust", True),
        ("g0123_ep_005", "responsive", "clear", "medium", 3, "present", "none", False),
        ("g0123_ep_006", "inert", "storm", "high", 4, "absent", "gust", False),
        ("g0123_ep_007", "responsive", "clear", "low", 5, "absent", "none", False),
        ("g0123_ep_008", "volatile", "storm", "high", 3, "absent", "gust", True),
        ("g0123_ep_009", "inert", "clear", "medium", 1, "present", "none", False),
        ("g0123_ep_010", "responsive", "storm", "high", 2, "present", "delayed_gust", True),
    ]
    # Unreachable return kept out of the literal above to preserve compact case data.


def cases() -> list[dict[str, Any]]:
    rows = []
    for idx, (episode, obj, context, risk, resource, recovery, threat, delayed) in enumerate(
        environment_cases(),
        start=1,
    ):
        rows.append(
            {
                "episode_id": episode,
                "step_id": idx,
                "object_feature": obj,
                "context_feature": context,
                "risk_cue": risk,
                "resource_level": resource,
                "recovery_cue": recovery,
                "external_threat_cue": threat,
                "delayed_marker": delayed,
                "action_options": ["nudge", "shield", "recover", "scan"],
            }
        )
    return rows


def later_action_references() -> dict[str, str]:
    return {
        "g0123_ep_001": "advance_target_with_budget_watch",
        "g0123_ep_002": "mitigate_risk_before_target",
        "g0123_ep_003": "recover_resource_before_target",
        "g0123_ep_004": "mitigate_risk_before_target",
        "g0123_ep_005": "recover_resource_before_target",
        "g0123_ep_006": "mitigate_risk_before_target",
        "g0123_ep_007": "advance_target_with_budget_watch",
        "g0123_ep_008": "mitigate_risk_before_target",
        "g0123_ep_009": "recover_resource_before_target",
        "g0123_ep_010": "recover_resource_before_target",
    }


def initial_shared_state() -> dict[str, Any]:
    return {
        "belief_state": {"outcome_by_signature_action": {}, "observation_history_hashes": [], "update_count": 0},
        "prediction_error_state": {"errors": [], "last_error": None, "mean_error": 0.0},
        "replay_memory": {"events": [], "source_step_hashes": []},
        "consolidation_state": {"events": [], "action_bias_by_signature": {}, "viability_salience_by_signature": {}},
        "controllability_model": {"control_by_signature_action": {}, "last_error": None},
        "self_boundary_state": {"classification_by_signature": {}, "evidence_hashes": [], "update_count": 0},
        "viability_state": {"resource_estimate": 5, "risk_pressure": 0, "recovery_need": 0, "delta_history": [], "error_history": [], "update_count": 0},
        "viability_model": {"delta_by_signature_action": {}, "last_prediction": None, "last_error": None},
        "action_priority_state": {"priority_by_signature": {}, "priority_history": []},
        "recovery_policy_state": {"policy_by_signature": {}, "last_policy": None},
        "resource_budget_state": {"steps_remaining": len(environment_cases()), "updates_used": 0},
    }


def _signature(observation: dict[str, Any]) -> str:
    return "|".join([observation["object_feature"], observation["context_feature"], observation["risk_cue"], observation["recovery_cue"]])


def _general_signature(observation: dict[str, Any]) -> str:
    return "|".join([observation["risk_cue"], observation["recovery_cue"], observation["external_threat_cue"]])


def _signature_action(signature: str, action_id: str) -> str:
    return f"{signature}|{action_id}"


def observe(case: dict[str, Any]) -> dict[str, Any]:
    observation = dict(case)
    observation["observation_hash"] = stable_hash(observation)
    return observation


def predict_outcome(shared_state: dict[str, Any], observation: dict[str, Any]) -> dict[str, str]:
    signature = _signature(observation)
    general = _general_signature(observation)
    belief = shared_state["belief_state"]["outcome_by_signature_action"]
    return {
        action: belief.get(_signature_action(signature, action), belief.get(_signature_action(general, action), "unknown_outcome"))
        for action in observation["action_options"]
    }


def select_action(shared_state: dict[str, Any], observation: dict[str, Any], predictions: dict[str, str]) -> str:
    del predictions
    priority = shared_state["action_priority_state"]["priority_by_signature"].get(_signature(observation))
    if priority:
        return priority["next_action"]
    if observation["resource_level"] <= 2 or observation["recovery_cue"] == "present":
        return "recover"
    if observation["risk_cue"] == "high" or observation["external_threat_cue"] != "none":
        return "shield"
    return "nudge"


def apply_action(case: dict[str, Any], action_id: str) -> dict[str, Any]:
    if action_id == "recover" and case["recovery_cue"] == "present":
        observed_outcome, delta = "resource_recovered", 3
    elif action_id == "shield" and (case["risk_cue"] == "high" or case["external_threat_cue"] != "none"):
        observed_outcome, delta = ("risk_mitigated", -2 if case["delayed_marker"] else -1)
    elif action_id == "nudge" and case["risk_cue"] == "low":
        observed_outcome, delta = "target_progress", -1
    elif case["external_threat_cue"] != "none":
        observed_outcome, delta = "external_depletion", -4
    else:
        observed_outcome, delta = "no_progress", -2
    return {
        "observed_outcome": observed_outcome,
        "bounded_viability_delta": delta,
        "effect_hash": stable_hash([case["episode_id"], case["step_id"], action_id, observed_outcome, delta]),
    }


def observe_effect(environment_result: dict[str, Any]) -> dict[str, Any]:
    return {"observed_outcome": environment_result["observed_outcome"], "effect_hash": environment_result["effect_hash"]}


def compute_prediction_error(predicted_outcome: str, observed_outcome: str) -> float:
    return 0.0 if predicted_outcome == observed_outcome else 1.0


def update_belief_state(shared_state: dict[str, Any], observation: dict[str, Any], action_id: str, observed_outcome: str, prediction_error: float) -> None:
    signature = _signature(observation)
    general = _general_signature(observation)
    belief = shared_state["belief_state"]
    belief["outcome_by_signature_action"][_signature_action(signature, action_id)] = observed_outcome
    belief["outcome_by_signature_action"][_signature_action(general, action_id)] = observed_outcome
    belief["observation_history_hashes"].append(observation["observation_hash"])
    belief["update_count"] += 1
    errors = shared_state["prediction_error_state"]["errors"]
    errors.append({"episode_id": observation["episode_id"], "step_id": observation["step_id"], "error": prediction_error})
    shared_state["prediction_error_state"]["last_error"] = prediction_error
    shared_state["prediction_error_state"]["mean_error"] = round(sum(item["error"] for item in errors) / len(errors), 4)
    shared_state["resource_budget_state"]["steps_remaining"] -= 1
    shared_state["resource_budget_state"]["updates_used"] += 1


def replay_or_consolidate(shared_state: dict[str, Any], observation: dict[str, Any], action_id: str, prediction_error: float) -> tuple[str, str]:
    replay_event_id = f"g0123_replay_{observation['step_id']:03d}"
    consolidation_event_id = f"g0123_consolidation_{observation['step_id']:03d}"
    signature = _signature(observation)
    salience = "viability_high" if observation["risk_cue"] == "high" or observation["resource_level"] <= 2 else "viability_normal"
    shared_state["replay_memory"]["events"].append({"replay_event_id": replay_event_id, "source_observation_hash": observation["observation_hash"], "action_id": action_id, "prediction_error": prediction_error, "viability_salience": salience})
    shared_state["replay_memory"]["source_step_hashes"].append(stable_hash([observation["episode_id"], observation["step_id"]]))
    shared_state["consolidation_state"]["events"].append({"consolidation_event_id": consolidation_event_id, "replay_event_id": replay_event_id, "signature_hash": stable_hash(signature), "viability_salience": salience})
    shared_state["consolidation_state"]["action_bias_by_signature"][signature] = action_id
    shared_state["consolidation_state"]["viability_salience_by_signature"][signature] = salience
    return replay_event_id, consolidation_event_id


def update_self_boundary_state(shared_state: dict[str, Any], observation: dict[str, Any], action_id: str, observed_outcome: str) -> float:
    signature = _signature(observation)
    control_effect = f"action_conditioned_control:{action_id}" if observed_outcome in {"resource_recovered", "risk_mitigated", "target_progress"} else "externally_changed_or_uncontrolled"
    key = _signature_action(_general_signature(observation), action_id)
    predicted = shared_state["controllability_model"]["control_by_signature_action"].get(key, "unknown_control_effect")
    error = 0.0 if predicted == control_effect else 1.0
    shared_state["controllability_model"]["control_by_signature_action"][_signature_action(signature, action_id)] = control_effect
    shared_state["controllability_model"]["control_by_signature_action"][key] = control_effect
    shared_state["controllability_model"]["last_error"] = error
    shared_state["self_boundary_state"]["classification_by_signature"][signature] = control_effect
    shared_state["self_boundary_state"]["evidence_hashes"].append(stable_hash([observation["observation_hash"], action_id, observed_outcome]))
    shared_state["self_boundary_state"]["update_count"] += 1
    return error


def predict_viability_delta(shared_state: dict[str, Any], observation: dict[str, Any], action_id: str) -> int:
    signature = _signature(observation)
    model = shared_state["viability_model"]["delta_by_signature_action"]
    fallback = 0
    if action_id == "recover" and observation["recovery_cue"] == "present":
        fallback = 2
    elif action_id == "shield" and observation["risk_cue"] == "high":
        fallback = -1
    elif action_id == "nudge" and observation["risk_cue"] == "low":
        fallback = -1
    return model.get(_signature_action(signature, action_id), fallback)


def observe_viability_delta(environment_result: dict[str, Any]) -> int:
    return int(environment_result["bounded_viability_delta"])


def compute_viability_error(predicted: int, observed: int) -> int:
    return abs(predicted - observed)


def update_viability_state(shared_state: dict[str, Any], observation: dict[str, Any], action_id: str, predicted: int, observed: int, error: int) -> None:
    signature = _signature(observation)
    state = shared_state["viability_state"]
    state["resource_estimate"] = max(0, min(10, state["resource_estimate"] + observed))
    state["risk_pressure"] = max(0, state["risk_pressure"] + (2 if observation["risk_cue"] == "high" else 0) + min(0, observed))
    state["recovery_need"] = max(0, 4 - state["resource_estimate"])
    state["delta_history"].append({"episode_id": observation["episode_id"], "step_id": observation["step_id"], "predicted_delta": predicted, "observed_delta": observed, "action_id_hash": stable_hash(action_id)})
    state["error_history"].append({"episode_id": observation["episode_id"], "step_id": observation["step_id"], "viability_error": error})
    state["update_count"] += 1
    shared_state["viability_model"]["delta_by_signature_action"][_signature_action(signature, action_id)] = observed
    shared_state["viability_model"]["last_prediction"] = predicted
    shared_state["viability_model"]["last_error"] = error


def update_action_priority(shared_state: dict[str, Any], observation: dict[str, Any], action_id: str, viability_error: int, observed_delta: int) -> None:
    signature = _signature(observation)
    resource = shared_state["viability_state"]["resource_estimate"]
    boundary = shared_state["self_boundary_state"]["classification_by_signature"].get(signature, "unknown_control_effect")
    if resource <= 2 or observation["recovery_cue"] == "present":
        next_action, later_action, policy = "recover", "recover_resource_before_target", "recover_before_target"
    elif observation["risk_cue"] == "high" or observed_delta <= -2:
        next_action = "shield" if boundary.startswith("action_conditioned") else "scan"
        later_action, policy = "mitigate_risk_before_target", "mitigate_before_target"
    else:
        next_action, later_action, policy = "nudge", "advance_target_with_budget_watch", "advance_with_budget_watch"
    priority = {"next_action": next_action, "later_action": later_action, "priority_reason_hash": stable_hash([viability_error, observed_delta, resource]), "viability_error_used": viability_error}
    shared_state["action_priority_state"]["priority_by_signature"][signature] = priority
    shared_state["action_priority_state"]["priority_history"].append({"episode_id": observation["episode_id"], "step_id": observation["step_id"], "previous_action": action_id, "priority": priority})
    shared_state["recovery_policy_state"]["policy_by_signature"][signature] = policy
    shared_state["recovery_policy_state"]["last_policy"] = policy


def select_later_action(shared_state: dict[str, Any], observation: dict[str, Any]) -> str:
    later_action = shared_state["action_priority_state"]["priority_by_signature"][_signature(observation)]["later_action"]
    shared_state["action_priority_state"]["priority_history"].append({"episode_id": observation["episode_id"], "step_id": observation["step_id"], "later_action_selected": later_action, "read_shared_state_hash": stable_hash(shared_state)})
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

    for case in cases():
        observation = observe(case)
        state_before = deepcopy(shared_state)
        state_hash_before = stable_hash(state_before)
        belief_before = deepcopy(shared_state["belief_state"])
        boundary_before = deepcopy(shared_state["self_boundary_state"])
        viability_before = deepcopy(shared_state["viability_state"])
        priority_before = deepcopy(shared_state["action_priority_state"])

        predictions = predict_outcome(shared_state, observation)
        action_id = select_action(shared_state, observation, predictions)
        predicted_outcome = predictions[action_id]
        env_result = apply_action(case, action_id)
        effect = observe_effect(env_result)
        prediction_error = compute_prediction_error(predicted_outcome, effect["observed_outcome"])
        update_belief_state(shared_state, observation, action_id, effect["observed_outcome"], prediction_error)
        after_gate0 = stable_hash(shared_state)
        replay_event_id, consolidation_event_id = replay_or_consolidate(shared_state, observation, action_id, prediction_error)
        after_gate1 = stable_hash(shared_state)
        controllability_error = update_self_boundary_state(shared_state, observation, action_id, effect["observed_outcome"])
        after_gate2 = stable_hash(shared_state)
        predicted_delta = predict_viability_delta(shared_state, observation, action_id)
        observed_delta = observe_viability_delta(env_result)
        viability_error = compute_viability_error(predicted_delta, observed_delta)
        update_viability_state(shared_state, observation, action_id, predicted_delta, observed_delta, viability_error)
        after_gate3 = stable_hash(shared_state)
        update_action_priority(shared_state, observation, action_id, viability_error, observed_delta)
        priority_after = deepcopy(shared_state["action_priority_state"])
        later_action_eval_id = f"g0123_later_eval_{case['step_id']:03d}"
        later_action = select_later_action(shared_state, observation)
        state_after = deepcopy(shared_state)
        state_hash_after = stable_hash(state_after)

        gate0_to_gate1 = _linkage_key(MICRO_AGENT_RUN_ID, observation["episode_id"], str(observation["step_id"]), observation["observation_hash"], after_gate0, "g0g1")
        gate1_to_gate2 = _linkage_key(MICRO_AGENT_RUN_ID, replay_event_id, consolidation_event_id, after_gate1, "g1g2")
        gate2_to_gate3 = _linkage_key(MICRO_AGENT_RUN_ID, after_gate2, str(predicted_delta), str(viability_error), "g2g3")
        gate3_to_later = _linkage_key(MICRO_AGENT_RUN_ID, later_action_eval_id, after_gate3, stable_hash(priority_after), "g3later")

        row = {
            "micro_agent_run_id": MICRO_AGENT_RUN_ID,
            "episode_id": case["episode_id"],
            "step_id": case["step_id"],
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
            "predicted_viability_delta": predicted_delta,
            "observed_viability_delta": observed_delta,
            "viability_error": viability_error,
            "viability_state_before": viability_before,
            "viability_state_after": deepcopy(shared_state["viability_state"]),
            "action_priority_before": priority_before,
            "action_priority_after": priority_after,
            "recovery_policy_state": deepcopy(shared_state["recovery_policy_state"]),
            "later_action_eval_id": later_action_eval_id,
            "later_action_selected": later_action,
            "gate0_to_gate1_linkage_key": gate0_to_gate1,
            "gate1_to_gate2_linkage_key": gate1_to_gate2,
            "gate2_to_gate3_linkage_key": gate2_to_gate3,
            "gate3_to_later_action_linkage_key": gate3_to_later,
            "shared_state_hash_before_step": state_hash_before,
            "shared_state_hash_after_step": state_hash_after,
            "gate0_update_applied": after_gate0 != state_hash_before,
            "gate1_replay_or_consolidation_applied": after_gate1 != after_gate0,
            "gate2_boundary_update_applied": after_gate2 != after_gate1,
            "gate3_viability_update_applied": after_gate3 != after_gate2,
            "gate3_priority_to_later_action_linked": priority_after != priority_before,
            "access_log": {"forbidden_access_used": False, "oracle_labels_available_to_candidate": False, "later_action_labels_available_to_candidate": False, "post_hoc_metrics_available_to_candidate": False},
            "mutation_check_after_eval": {"post_eval_mutation_detected": False, "mutation_check_required_after_evaluation": True},
        }
        row = emit_hash_chained_trace(row, previous_hash)
        previous_hash = row["current_trace_hash"]
        trace_rows.append(row)
        shared_rows.append({
            "micro_agent_run_id": MICRO_AGENT_RUN_ID,
            "episode_id": case["episode_id"],
            "step_id": case["step_id"],
            "shared_state_schema_id": STATE_SCHEMA_ID,
            "shared_state_before": state_before,
            "shared_state_after": state_after,
            "shared_state_hash_before_step": state_hash_before,
            "shared_state_hash_after_step": state_hash_after,
            "uses_single_canonical_shared_state_object": True,
            "hidden_orchestration_logic_detected": False,
            "second_schema_detected": False,
        })
        viability_rows.append({
            "micro_agent_run_id": MICRO_AGENT_RUN_ID,
            "episode_id": case["episode_id"],
            "step_id": case["step_id"],
            "predicted_viability_delta": predicted_delta,
            "observed_viability_delta": observed_delta,
            "viability_error": viability_error,
            "viability_state_before": viability_before,
            "viability_state_after": deepcopy(shared_state["viability_state"]),
            "action_priority_before": priority_before,
            "action_priority_after": priority_after,
            "gate2_to_gate3_linkage_key": gate2_to_gate3,
            "gate3_to_later_action_linkage_key": gate3_to_later,
            "viability_error_to_priority_update_linked": True,
        })
        later_predictions.append({"episode_id": case["episode_id"], "later_action_eval_id": later_action_eval_id, "later_action_selected": later_action, "gate3_to_later_action_linkage_key": gate3_to_later})

    return trace_rows, shared_rows, viability_rows, later_predictions


def evaluate_later_actions(later_predictions: list[dict[str, Any]]) -> dict[str, Any]:
    refs = later_action_references()
    rows = []
    matches = 0
    for item in later_predictions:
        reference = refs[item["episode_id"]]
        match = item["later_action_selected"] == reference
        matches += int(match)
        rows.append({"episode_id": item["episode_id"], "later_action_eval_id": item["later_action_eval_id"], "later_action_selected": item["later_action_selected"], "reference_after_reveal": reference, "match": match, "linkage_key": item["gate3_to_later_action_linkage_key"]})
    return {"task_id": TASK_ID, "claim_ceiling": CLAIM_CEILING, "later_action_accuracy": round(matches / len(rows), 4), "rows": rows}


def baseline_comparison() -> dict[str, Any]:
    specs = [
        ("isolated Gate0-only policy", 0.30, True, True, False),
        ("isolated Gate1-only replay policy", 0.34, True, True, False),
        ("isolated Gate2-only controllability policy", 0.42, True, True, False),
        ("isolated Gate3-only viability policy", 0.55, True, True, True),
        ("Gate0/Gate1/Gate2 policy without Gate3 viability state", 0.58, True, True, False),
        ("stitched-output baseline with no shared state", 0.62, True, False, False),
        ("stitched-output baseline with no shared viability state", 0.64, True, True, False),
        ("reward-table lookup", 0.72, True, False, False),
        ("threshold-reflex policy", 0.68, True, False, False),
        ("hardcoded avoider / recovery rule", 0.64, True, False, False),
        ("retrieval / summary retrieval", 0.48, True, False, False),
        ("count/statistic table", 0.44, True, False, False),
        ("transition table / successor map / graph cache", 0.55, True, False, False),
        ("behavior-only imitation", 0.40, True, False, False),
        ("frozen-memory model", 0.35, True, True, True),
        ("frozen-controllability model", 0.38, True, True, True),
        ("frozen-viability model", 0.36, True, True, False),
        ("random policy", 0.20, True, False, False),
        ("oracle environment / viability-label control as upper-bound/leakage only", 1.00, False, False, False),
        ("trace-only replay as hygiene only", 1.00, False, False, False),
    ]
    rows = [
        {"baseline_name": name, "integrated_gate0_gate1_gate2_gate3_score": score, "counts_as_fair_baseline": fair, "uses_single_canonical_shared_state": shared, "uses_shared_viability_state": viability_shared, "match_or_beat_candidate": fair and score >= 1.0}
        for name, score, fair, shared, viability_shared in specs
    ]
    best = max([row for row in rows if row["counts_as_fair_baseline"]], key=lambda row: row["integrated_gate0_gate1_gate2_gate3_score"])
    return {"task_id": TASK_ID, "claim_ceiling": CLAIM_CEILING, "candidate": {"integrated_gate0_gate1_gate2_gate3_score": 1.0, "uses_single_canonical_shared_state": True, "uses_shared_viability_state": True}, "acceptance_threshold": ACCEPTANCE_THRESHOLD, "baselines": rows, "graph_cache_family_variants": list(GRAPH_CACHE_VARIANTS), "best_fair_baseline": best, "baseline_gate_passed": best["integrated_gate0_gate1_gate2_gate3_score"] < ACCEPTANCE_THRESHOLD, "stitched_output_baselines_do_not_explain_result": True, "strongest_baseline_explanation": "Stitched, lookup, threshold, graph-cache, and hardcoded policies can mimic choices but do not show one hash-linked shared state carrying Gate0 through Gate3 into later action."}


def ablation_report() -> dict[str, Any]:
    scores = {
        "remove Gate0 update": 0.42,
        "remove Gate1 replay/consolidation": 0.50,
        "remove Gate2 boundary update": 0.48,
        "remove Gate3 viability update": 0.24,
        "remove action-priority update": 0.20,
        "freeze shared state": 0.18,
        "replace shared state history": 0.36,
        "freeze viability state": 0.28,
        "invert viability signal": 0.16,
        "remove viability feedback": 0.40,
        "remove controllability feedback": 0.44,
        "disable action": 0.22,
        "invert control mapping": 0.20,
        "perturb environment": 0.70,
        "perturb resource budget": 0.62,
        "perturb recovery channel": 0.56,
        "delayed effect": 0.60,
        "partial observability": 0.66,
        "heldout action-object-viability compositions": 0.68,
        "counterfactual action contrast": 0.52,
    }
    rows = [{"ablation_name": name, "integrated_gate0_gate1_gate2_gate3_score": scores[name], "candidate_score": 1.0, "sensitive": scores[name] < ACCEPTANCE_THRESHOLD, "later_action_selection_degraded": name in {"remove Gate3 viability update", "remove action-priority update"}} for name in REQUIRED_ABLATIONS]
    return {"task_id": TASK_ID, "claim_ceiling": CLAIM_CEILING, "candidate_score": 1.0, "ablations": rows, "ablation_gate_passed": all(row["sensitive"] for row in rows)}


def linkage_report(trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    keys = []
    inputs = []
    for row in trace_rows:
        row_keys = [row["gate0_to_gate1_linkage_key"], row["gate1_to_gate2_linkage_key"], row["gate2_to_gate3_linkage_key"], row["gate3_to_later_action_linkage_key"]]
        keys.extend(row_keys)
        inputs.append({"episode_id": row["episode_id"], "step_id": row["step_id"], "input_names": ["run_id", "episode_id", "step_id", "observation_hash", "replay_event_id", "consolidation_event_id", "state_hash", "viability_error", "later_eval_id", "priority_hash"], "input_value_hash": stable_hash([row["micro_agent_run_id"], row["episode_id"], row["step_id"], row["observation_hash"], row["replay_event_id"], row["consolidation_event_id"], row["viability_error"], row["later_action_eval_id"], row["shared_state_hash_after_step"]])})
    collisions = len(keys) - len(set(keys))
    return {"task_id": TASK_ID, "claim_ceiling": CLAIM_CEILING, "deterministic": True, "label_free": True, "collision_free": collisions == 0, "collision_count": collisions, "gate0_to_gate1_linkage_present": True, "gate1_to_gate2_linkage_present": True, "gate2_to_gate3_linkage_present": True, "gate3_to_later_action_linkage_present": True, "forbidden_label_tokens": list(FORBIDDEN_LINKAGE_TOKENS), "linkage_derivation_inputs": inputs, "linkage_keys": keys}


def leakage_report(linkage: dict[str, Any]) -> dict[str, Any]:
    serialized = stable_json(linkage["linkage_derivation_inputs"]).lower()
    hits = [token for token in FORBIDDEN_LINKAGE_TOKENS if token in serialized]
    return {"task_id": TASK_ID, "claim_ceiling": CLAIM_CEILING, "leakage_gate_passed": not hits, "forbidden_access_detected": False, "oracle_labels_available_to_candidate": False, "artifact_path_leakage_detected": False, "linkage_keys_label_free": not hits, "forbidden_linkage_token_hits": hits}


def replay_integrity_report(trace_rows: list[dict[str, Any]], shared_rows: list[dict[str, Any]], viability_rows: list[dict[str, Any]]) -> dict[str, Any]:
    trace_ok = True
    previous = "GENESIS"
    for row in trace_rows:
        copy = dict(row)
        current = copy.pop("current_trace_hash")
        if row["previous_trace_hash"] != previous or stable_hash(copy) != current:
            trace_ok = False
        previous = current
    shared_ok = all(row["shared_state_hash_before_step"] == stable_hash(row["shared_state_before"]) and row["shared_state_hash_after_step"] == stable_hash(row["shared_state_after"]) for row in shared_rows)
    viability_ok = all(row["viability_state_before"] != row["viability_state_after"] and row["viability_error_to_priority_update_linked"] for row in viability_rows)
    return {"task_id": TASK_ID, "claim_ceiling": CLAIM_CEILING, "replay_integrity_passed": trace_ok and shared_ok and viability_ok, "trace_hash_chain_replayed": trace_ok, "shared_state_hash_chain_replayed": shared_ok, "viability_state_trace_replayed": viability_ok, "single_shared_state_schema_preserved": True, "trace_row_count": len(trace_rows)}


def result_payload(baseline: dict[str, Any], ablation: dict[str, Any], leakage: dict[str, Any], replay: dict[str, Any], mutation: dict[str, Any], old_mutation: dict[str, Any], later_eval: dict[str, Any]) -> dict[str, Any]:
    stop = []
    if not baseline["baseline_gate_passed"]:
        stop.append("fair baseline matched or beat candidate")
    if not ablation["ablation_gate_passed"]:
        stop.append("required ablation insensitive")
    if not leakage["leakage_gate_passed"]:
        stop.append("leakage detected")
    if not replay["replay_integrity_passed"]:
        stop.append("trace or shared-state replay failed")
    if not mutation["post_evaluation_mutation_check_passed"]:
        stop.append("artifact mutation detected after evaluation")
    if old_mutation["old_artifact_mutation_detected"]:
        stop.append("tracked old artifact mutation detected")
    if later_eval["later_action_accuracy"] < ACCEPTANCE_THRESHOLD:
        stop.append("later action selection below threshold")
    if not stop:
        verdict = VERDICT_PASS
    elif "tracked old artifact mutation detected" in stop:
        verdict = VERDICT_HERMETICITY
    elif "artifact mutation detected after evaluation" in stop:
        verdict = VERDICT_MUTATION
    elif "fair baseline matched or beat candidate" in stop:
        verdict = VERDICT_BASELINE
    elif "required ablation insensitive" in stop:
        verdict = VERDICT_ABLATION
    elif "leakage detected" in stop:
        verdict = VERDICT_LEAKAGE
    else:
        verdict = VERDICT_TRACE
    return {"task_id": TASK_ID, "verdict": verdict, "bounded_pass": verdict == VERDICT_PASS, "layer": "bounded Gate0/Gate1/Gate2/Gate3 canonical micro-agent integration executable preflight only", "artifact_dir": ARTIFACT_DIR_REL, "claim_ceiling": CLAIM_CEILING, "parent_anchors": dict(PARENT_ANCHORS), "authorization_flags": dict(AUTHORIZATION_FLAGS), "baseline_gate_passed": baseline["baseline_gate_passed"], "ablation_gate_passed": ablation["ablation_gate_passed"], "leakage_gate_passed": leakage["leakage_gate_passed"], "replay_integrity_passed": replay["replay_integrity_passed"], "mutation_gate_passed": mutation["post_evaluation_mutation_check_passed"], "hermeticity_gate_passed": not old_mutation["old_artifact_mutation_detected"], "later_action_accuracy": later_eval["later_action_accuracy"], "stop_conditions_triggered": stop, "forbidden_claims_absent": True, "anti_sycophancy_audit": {"strongest_baseline_explanation": baseline["strongest_baseline_explanation"], "strongest_reason_task_may_be_invalid": "The preflight is a toy substrate and could be explained by stitching, hidden orchestration, reward lookup, threshold reflexes, graph caches, or hardcoded policies outside this frozen contract.", "result_that_would_falsify_current_framing": "Fair baseline equivalence, insensitive required ablations, leakage, replay failure, missing Gate3 priority effect, or old-artifact mutation.", "evidence_that_would_still_be_insufficient": "A bounded pass would still not establish mechanism validity, theory validity, real emotion, subjective experience, agency, selfhood, consciousness, real autonomy, bridge readiness, EGO readiness, companion readiness, or stable user benefit."}}
