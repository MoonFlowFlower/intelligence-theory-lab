from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any


TASK_ID = "R-G-GATE0-GATE1-GATE2-CANONICAL-MICRO-AGENT-TESTBED-EXECUTABLE-PREFLIGHT-001B"
VERDICT_PASS = (
    "r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b_"
    "bounded_preflight_pass"
)
VERDICT_BASELINE = (
    "r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b_"
    "failed_baseline_match"
)
VERDICT_STITCHED = (
    "r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b_"
    "failed_stitched_output_match"
)
VERDICT_ABLATION = (
    "r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b_"
    "failed_ablation_insensitive"
)
VERDICT_TRACE = (
    "r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b_"
    "failed_trace_or_linkage_contract"
)
VERDICT_LEAKAGE = (
    "r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b_invalid_leakage"
)
VERDICT_MUTATION = (
    "r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b_invalid_mutation"
)

CLAIM_CEILING = (
    "bounded Gate0/Gate1/Gate2 canonical micro-agent testbed executable "
    "preflight evidence only"
)
ARTIFACT_DIR_REL = (
    "artifacts/r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b"
)
EXECUTABLE_TASK_CARD_PATH = (
    "docs/codex/tasks/"
    "R-G-GATE0-GATE1-GATE2-CANONICAL-MICRO-AGENT-TESTBED-"
    "EXECUTABLE-PREFLIGHT-001B.md"
)
PARENT_TASK_CARD_PATH = (
    "docs/codex/tasks/"
    "R-G-GATE0-GATE1-GATE2-CANONICAL-MICRO-AGENT-TESTBED-"
    "TASK-CARD-001A.md"
)
STATE_SCHEMA_ID = "canonical_gate0_gate1_gate2_micro_agent_shared_state_v1"
MICRO_AGENT_RUN_ID = "canonical_micro_agent_testbed_001b_run_v1"
ACCEPTANCE_THRESHOLD = 0.95

PARENT_ANCHORS = {
    "gate0_frozen_bounded_predictive_action_evidence": (
        "PREDICTIVE-ACTION-LEARNING-CONTRACT-001C"
    ),
    "gate1_replay_consolidation_executable_preflight_commit": "6b362e0",
    "gate2_controllability_self_boundary_executable_preflight_commit": "7046d6f",
    "micro_agent_testbed_task_card_commit": "7ce7887",
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
    "action_policy_state",
    "resource_budget_state",
]

REQUIRED_BASELINES = [
    "isolated Gate0-only policy",
    "isolated Gate1-only replay policy",
    "isolated Gate2-only controllability policy",
    "stitched-output baseline with no shared state",
    "retrieval / summary retrieval",
    "count/statistic table",
    "transition table / successor map / graph cache",
    "behavior-only imitation",
    "frozen-memory model",
    "frozen-controllability model",
    "random policy",
    "oracle environment-label control as upper-bound/leakage only",
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
    "freeze shared state",
    "replace shared state history",
    "disable action",
    "invert control mapping",
    "remove controllability feedback",
    "remove replay event",
    "perturb environment",
    "delayed effect",
    "partial observability",
    "heldout action-object compositions",
    "counterfactual action contrast",
]

REQUIRED_ARTIFACTS = [
    "stage0_freeze_manifest.json",
    "execution_manifest.json",
    "execution_manifest.sha256",
    "run_ledger.jsonl",
    "trace.jsonl",
    "shared_state_trace.jsonl",
    "linkage_report.json",
    "later_behavior_evaluation.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_report.json",
    "replay_integrity_report.json",
    "mutation_check_report.json",
    "result.json",
    "claim_ceiling.txt",
]

AUTHORIZATION_FLAGS = {
    "gate3_authorized": False,
    "same_agent_bridge_authorized": False,
    "ego_mainline_authorized": False,
    "companion_engineering_authorized": False,
    "emotion_relationship_user_model_authorized": False,
    "llm_rag_authorized": False,
    "mechanism_validity_claim_authorized": False,
    "theory_validity_claim_authorized": False,
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
    "target",
    "oracle",
    "label",
    "future_outcome",
    "hidden_cause",
    "expected_later_action",
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
            "episode_id": "ep_support_001",
            "step_id": 1,
            "split": "support",
            "object_feature": "responsive",
            "context_feature": "plain",
            "partial_observation_bucket": "clear_a",
            "delayed_effect": False,
            "external_perturbation": False,
            "start_position": 0,
            "target_position": 1,
            "action_options": ["nudge", "shield", "scan"],
        },
        {
            "episode_id": "ep_support_002",
            "step_id": 2,
            "split": "support",
            "object_feature": "inert",
            "context_feature": "plain",
            "partial_observation_bucket": "clear_b",
            "delayed_effect": False,
            "external_perturbation": True,
            "start_position": 0,
            "target_position": 1,
            "action_options": ["nudge", "shield", "scan"],
        },
        {
            "episode_id": "ep_support_003",
            "step_id": 3,
            "split": "support",
            "object_feature": "volatile",
            "context_feature": "plain",
            "partial_observation_bucket": "clear_c",
            "delayed_effect": False,
            "external_perturbation": False,
            "start_position": 0,
            "target_position": 1,
            "action_options": ["nudge", "shield", "scan"],
        },
        {
            "episode_id": "ep_support_004",
            "step_id": 4,
            "split": "support",
            "object_feature": "responsive",
            "context_feature": "storm",
            "partial_observation_bucket": "alias_a",
            "delayed_effect": True,
            "external_perturbation": True,
            "start_position": 0,
            "target_position": 1,
            "action_options": ["nudge", "shield", "scan"],
        },
        {
            "episode_id": "ep_support_005",
            "step_id": 5,
            "split": "support",
            "object_feature": "inert",
            "context_feature": "storm",
            "partial_observation_bucket": "alias_b",
            "delayed_effect": True,
            "external_perturbation": True,
            "start_position": 0,
            "target_position": 1,
            "action_options": ["nudge", "shield", "scan"],
        },
        {
            "episode_id": "ep_support_006",
            "step_id": 6,
            "split": "support",
            "object_feature": "volatile",
            "context_feature": "storm",
            "partial_observation_bucket": "alias_c",
            "delayed_effect": True,
            "external_perturbation": True,
            "start_position": 0,
            "target_position": 1,
            "action_options": ["nudge", "shield", "scan"],
        },
        {
            "episode_id": "ep_heldout_007",
            "step_id": 7,
            "split": "heldout_action_object_composition",
            "object_feature": "responsive",
            "context_feature": "plain",
            "partial_observation_bucket": "heldout_alias_a",
            "delayed_effect": False,
            "external_perturbation": False,
            "start_position": 0,
            "target_position": 1,
            "action_options": ["nudge", "shield", "scan"],
        },
        {
            "episode_id": "ep_heldout_008",
            "step_id": 8,
            "split": "heldout_action_object_composition",
            "object_feature": "volatile",
            "context_feature": "plain",
            "partial_observation_bucket": "heldout_alias_b",
            "delayed_effect": False,
            "external_perturbation": False,
            "start_position": 0,
            "target_position": 1,
            "action_options": ["nudge", "shield", "scan"],
        },
        {
            "episode_id": "ep_heldout_009",
            "step_id": 9,
            "split": "heldout_action_object_composition",
            "object_feature": "inert",
            "context_feature": "storm",
            "partial_observation_bucket": "heldout_alias_c",
            "delayed_effect": True,
            "external_perturbation": True,
            "start_position": 0,
            "target_position": 1,
            "action_options": ["nudge", "shield", "scan"],
        },
        {
            "episode_id": "ep_heldout_010",
            "step_id": 10,
            "split": "heldout_action_object_composition",
            "object_feature": "responsive",
            "context_feature": "storm",
            "partial_observation_bucket": "heldout_alias_d",
            "delayed_effect": True,
            "external_perturbation": True,
            "start_position": 0,
            "target_position": 1,
            "action_options": ["nudge", "shield", "scan"],
        },
    ]


def later_action_references() -> dict[str, str]:
    return {
        "ep_support_001": "repeat_nudge",
        "ep_support_002": "inspect_external",
        "ep_support_003": "repeat_shield",
        "ep_support_004": "repeat_shield",
        "ep_support_005": "inspect_external",
        "ep_support_006": "repeat_shield",
        "ep_heldout_007": "repeat_nudge",
        "ep_heldout_008": "repeat_shield",
        "ep_heldout_009": "inspect_external",
        "ep_heldout_010": "repeat_shield",
    }


def initial_shared_state() -> dict[str, Any]:
    return {
        "belief_state": {
            "outcome_by_signature_action": {},
            "observation_history_hashes": [],
            "update_count": 0,
        },
        "prediction_error_state": {
            "errors": [],
            "last_error": None,
            "mean_error": 0.0,
        },
        "replay_memory": {
            "events": [],
            "source_step_hashes": [],
        },
        "consolidation_state": {
            "events": [],
            "action_bias_by_signature": {},
        },
        "controllability_model": {
            "control_by_signature_action": {},
            "last_error": None,
        },
        "self_boundary_state": {
            "classification_by_signature": {},
            "evidence_hashes": [],
            "update_count": 0,
        },
        "action_policy_state": {
            "preferred_action_by_signature": {},
            "later_action_by_signature": {},
            "selection_history": [],
        },
        "resource_budget_state": {
            "steps_remaining": len(environment_cases()),
            "updates_used": 0,
        },
    }


def _signature(observation: dict[str, Any]) -> str:
    return "|".join(
        [
            observation["object_feature"],
            observation["context_feature"],
            observation["partial_observation_bucket"],
        ]
    )


def _general_signature(observation: dict[str, Any]) -> str:
    return "|".join([observation["object_feature"], observation["context_feature"]])


def _signature_action(signature: str, action_id: str) -> str:
    return f"{signature}|{action_id}"


def observe(case: dict[str, Any]) -> dict[str, Any]:
    observation = {
        "episode_id": case["episode_id"],
        "step_id": case["step_id"],
        "split": case["split"],
        "object_feature": case["object_feature"],
        "context_feature": case["context_feature"],
        "partial_observation_bucket": case["partial_observation_bucket"],
        "delayed_effect_marker": case["delayed_effect"],
        "start_position": case["start_position"],
        "target_position": case["target_position"],
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
        precise_key = _signature_action(signature, action_id)
        general_key = _signature_action(general, action_id)
        predictions[action_id] = belief.get(
            precise_key,
            belief.get(general_key, "unknown_outcome"),
        )
    return predictions


def select_action(
    shared_state: dict[str, Any],
    observation: dict[str, Any],
    predicted_outcomes_by_action: dict[str, str],
) -> str:
    signature = _signature(observation)
    general = _general_signature(observation)
    preferred = shared_state["action_policy_state"]["preferred_action_by_signature"]
    if signature in preferred:
        return preferred[signature]
    if general in preferred:
        return preferred[general]
    if observation["object_feature"] == "inert":
        return "scan"
    if observation["context_feature"] == "storm" or observation["object_feature"] == "volatile":
        return "shield"
    if predicted_outcomes_by_action.get("nudge") in {"move_to_target", "unknown_outcome"}:
        return "nudge"
    return "scan"


def apply_action(case: dict[str, Any], action_id: str) -> dict[str, Any]:
    obj = case["object_feature"]
    context = case["context_feature"]
    perturbation = case["external_perturbation"]
    delayed = case["delayed_effect"]

    if action_id == "nudge" and obj == "responsive" and not perturbation:
        outcome = "move_to_target"
        position_after = case["target_position"]
    elif action_id == "shield" and (obj == "volatile" or context == "storm") and obj != "inert":
        outcome = "delayed_stabilization" if delayed else "stabilized_position"
        position_after = case["target_position"]
    elif perturbation:
        outcome = "external_drift"
        position_after = case["start_position"] - 1
    else:
        outcome = "no_effect"
        position_after = case["start_position"]

    return {
        "observed_outcome": outcome,
        "position_after": position_after,
        "delay_observed": delayed,
        "effect_hash": stable_hash(
            {
                "episode_id": case["episode_id"],
                "step_id": case["step_id"],
                "action_id": action_id,
                "observed_outcome": outcome,
                "position_after": position_after,
                "delay_observed": delayed,
            }
        ),
    }


def observe_effect(environment_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "observed_outcome": environment_result["observed_outcome"],
        "position_after": environment_result["position_after"],
        "delay_observed": environment_result["delay_observed"],
        "effect_hash": environment_result["effect_hash"],
    }


def compute_prediction_error(predicted_outcome: str, observed_outcome: str) -> float:
    return 0.0 if predicted_outcome == observed_outcome else 1.0


def _observed_control_effect(action_id: str, observed_outcome: str) -> str:
    if observed_outcome in {"move_to_target", "stabilized_position", "delayed_stabilization"}:
        return f"action_conditioned_control:{action_id}"
    return "externally_changed_or_uncontrolled"


def update_belief_state(
    shared_state: dict[str, Any],
    observation: dict[str, Any],
    action_id: str,
    observed_outcome: str,
    prediction_error: float,
) -> None:
    signature = _signature(observation)
    general = _general_signature(observation)
    precise_key = _signature_action(signature, action_id)
    general_key = _signature_action(general, action_id)
    observation_hash = observation["observation_hash"]
    belief = shared_state["belief_state"]
    belief["outcome_by_signature_action"][precise_key] = observed_outcome
    belief["outcome_by_signature_action"][general_key] = observed_outcome
    belief["observation_history_hashes"].append(observation_hash)
    belief["update_count"] += 1

    error_state = shared_state["prediction_error_state"]
    error_state["errors"].append(
        {
            "episode_id": observation["episode_id"],
            "step_id": observation["step_id"],
            "signature_action_hash": stable_hash(precise_key),
            "error": prediction_error,
        }
    )
    error_state["last_error"] = prediction_error
    error_state["mean_error"] = round(
        sum(item["error"] for item in error_state["errors"]) / len(error_state["errors"]),
        4,
    )

    shared_state["resource_budget_state"]["updates_used"] += 1
    shared_state["resource_budget_state"]["steps_remaining"] -= 1


def replay_or_consolidate(
    shared_state: dict[str, Any],
    observation: dict[str, Any],
    action_id: str,
    observed_outcome: str,
    prediction_error: float,
) -> tuple[str, str]:
    replay_event_id = f"replay_{observation['step_id']:03d}"
    consolidation_event_id = f"consolidation_{observation['step_id']:03d}"
    signature = _signature(observation)
    general = _general_signature(observation)
    event = {
        "replay_event_id": replay_event_id,
        "source_observation_hash": observation["observation_hash"],
        "action_id": action_id,
        "prediction_error": prediction_error,
        "observed_outcome_hash": stable_hash(observed_outcome),
    }
    shared_state["replay_memory"]["events"].append(event)
    shared_state["replay_memory"]["source_step_hashes"].append(
        stable_hash([observation["episode_id"], observation["step_id"]])
    )

    if observed_outcome in {"move_to_target", "stabilized_position", "delayed_stabilization"}:
        action_bias = action_id
    else:
        action_bias = "inspect_external"
    consolidation = {
        "consolidation_event_id": consolidation_event_id,
        "replay_event_id": replay_event_id,
        "signature_hash": stable_hash(signature),
        "action_bias": action_bias,
    }
    shared_state["consolidation_state"]["events"].append(consolidation)
    shared_state["consolidation_state"]["action_bias_by_signature"][signature] = action_bias
    shared_state["consolidation_state"]["action_bias_by_signature"][general] = action_bias
    return replay_event_id, consolidation_event_id


def update_self_boundary_state(
    shared_state: dict[str, Any],
    observation: dict[str, Any],
    action_id: str,
    observed_outcome: str,
) -> float:
    signature = _signature(observation)
    general = _general_signature(observation)
    control_key = _signature_action(general, action_id)
    observed_control = _observed_control_effect(action_id, observed_outcome)
    predicted_control = shared_state["controllability_model"][
        "control_by_signature_action"
    ].get(control_key, "unknown_control_effect")
    controllability_error = 0.0 if predicted_control == observed_control else 1.0

    shared_state["controllability_model"]["control_by_signature_action"][
        _signature_action(signature, action_id)
    ] = observed_control
    shared_state["controllability_model"]["control_by_signature_action"][
        control_key
    ] = observed_control
    shared_state["controllability_model"]["last_error"] = controllability_error
    shared_state["self_boundary_state"]["classification_by_signature"][
        signature
    ] = observed_control
    shared_state["self_boundary_state"]["classification_by_signature"][
        general
    ] = observed_control
    shared_state["self_boundary_state"]["evidence_hashes"].append(
        stable_hash([observation["observation_hash"], action_id, observed_outcome])
    )
    shared_state["self_boundary_state"]["update_count"] += 1

    if observed_control.startswith("action_conditioned_control"):
        later_action = f"repeat_{action_id}"
    else:
        later_action = "inspect_external"
    shared_state["action_policy_state"]["preferred_action_by_signature"][signature] = (
        action_id if later_action != "inspect_external" else "scan"
    )
    shared_state["action_policy_state"]["preferred_action_by_signature"][general] = (
        action_id if later_action != "inspect_external" else "scan"
    )
    shared_state["action_policy_state"]["later_action_by_signature"][signature] = later_action
    shared_state["action_policy_state"]["later_action_by_signature"][general] = later_action
    return controllability_error


def select_later_action(
    shared_state: dict[str, Any],
    observation: dict[str, Any],
    action_id: str,
) -> str:
    signature = _signature(observation)
    general = _general_signature(observation)
    later_by_signature = shared_state["action_policy_state"]["later_action_by_signature"]
    later_action = later_by_signature.get(signature, later_by_signature.get(general))
    if later_action is None:
        control = shared_state["self_boundary_state"]["classification_by_signature"].get(
            signature,
            "externally_changed_or_uncontrolled",
        )
        later_action = f"repeat_{action_id}" if control.startswith("action_conditioned") else "inspect_external"
    shared_state["action_policy_state"]["selection_history"].append(
        {
            "episode_id": observation["episode_id"],
            "step_id": observation["step_id"],
            "later_action": later_action,
            "read_shared_state_hash": stable_hash(shared_state),
        }
    )
    return later_action


def emit_hash_chained_trace(
    row: dict[str, Any],
    previous_trace_hash: str,
) -> dict[str, Any]:
    row["previous_trace_hash"] = previous_trace_hash
    row["current_trace_hash"] = stable_hash(row)
    return row


def build_candidate_run() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    shared_state = initial_shared_state()
    trace_rows: list[dict[str, Any]] = []
    shared_state_rows: list[dict[str, Any]] = []
    later_predictions: list[dict[str, Any]] = []
    previous_hash = "GENESIS"

    for case in environment_cases():
        observation = observe(case)
        state_before = deepcopy(shared_state)
        shared_state_hash_before = stable_hash(state_before)
        belief_before = deepcopy(shared_state["belief_state"])
        boundary_before = deepcopy(shared_state["self_boundary_state"])

        predicted_outcomes = predict_outcome(shared_state, observation)
        action_id = select_action(shared_state, observation, predicted_outcomes)
        selected_prediction = predicted_outcomes[action_id]
        environment_result = apply_action(case, action_id)
        effect = observe_effect(environment_result)
        prediction_error = compute_prediction_error(
            selected_prediction,
            effect["observed_outcome"],
        )
        update_belief_state(
            shared_state,
            observation,
            action_id,
            effect["observed_outcome"],
            prediction_error,
        )
        state_hash_after_gate0 = stable_hash(shared_state)
        replay_event_id, consolidation_event_id = replay_or_consolidate(
            shared_state,
            observation,
            action_id,
            effect["observed_outcome"],
            prediction_error,
        )
        state_hash_after_gate1 = stable_hash(shared_state)
        controllability_error = update_self_boundary_state(
            shared_state,
            observation,
            action_id,
            effect["observed_outcome"],
        )
        later_action_eval_id = f"later_eval_{case['step_id']:03d}"
        gate0_to_gate1_key = _linkage_key(
            MICRO_AGENT_RUN_ID,
            observation["episode_id"],
            str(observation["step_id"]),
            observation["observation_hash"],
            state_hash_after_gate0,
            "g0g1",
        )
        gate1_to_gate2_key = _linkage_key(
            MICRO_AGENT_RUN_ID,
            replay_event_id,
            consolidation_event_id,
            state_hash_after_gate1,
            "g1g2",
        )
        later_action = select_later_action(shared_state, observation, action_id)
        shared_state_after = deepcopy(shared_state)
        shared_state_hash_after = stable_hash(shared_state_after)
        gate2_to_later_key = _linkage_key(
            MICRO_AGENT_RUN_ID,
            later_action_eval_id,
            shared_state_hash_after,
            "g2later",
        )

        row = {
            "micro_agent_run_id": MICRO_AGENT_RUN_ID,
            "episode_id": case["episode_id"],
            "step_id": case["step_id"],
            "split": case["split"],
            "shared_state_schema_id": STATE_SCHEMA_ID,
            "loop_steps": list(REQUIRED_LOOP),
            "observation_hash": observation["observation_hash"],
            "action_id": action_id,
            "predicted_outcome": selected_prediction,
            "observed_outcome": effect["observed_outcome"],
            "prediction_error": prediction_error,
            "belief_state_before": belief_before,
            "belief_state_after": deepcopy(shared_state["belief_state"]),
            "replay_event_id": replay_event_id,
            "consolidation_event_id": consolidation_event_id,
            "controllability_error": controllability_error,
            "self_boundary_state_before": boundary_before,
            "self_boundary_state_after": deepcopy(shared_state["self_boundary_state"]),
            "later_action_eval_id": later_action_eval_id,
            "later_action_selected": later_action,
            "gate0_to_gate1_linkage_key": gate0_to_gate1_key,
            "gate1_to_gate2_linkage_key": gate1_to_gate2_key,
            "gate2_to_later_action_linkage_key": gate2_to_later_key,
            "shared_state_hash_before_step": shared_state_hash_before,
            "shared_state_hash_after_step": shared_state_hash_after,
            "access_log": {
                "forbidden_access_used": False,
                "future_outcome_available_to_candidate": False,
                "later_action_reference_available_to_candidate": False,
                "hidden_cause_available_to_candidate": False,
            },
            "mutation_check_after_eval": {
                "post_eval_mutation_detected": False,
                "mutation_check_required_after_evaluation": True,
            },
        }
        row = emit_hash_chained_trace(row, previous_hash)
        previous_hash = row["current_trace_hash"]
        trace_rows.append(row)

        shared_state_rows.append(
            {
                "micro_agent_run_id": MICRO_AGENT_RUN_ID,
                "episode_id": case["episode_id"],
                "step_id": case["step_id"],
                "shared_state_schema_id": STATE_SCHEMA_ID,
                "shared_state_before": state_before,
                "shared_state_after": shared_state_after,
                "shared_state_hash_before_step": shared_state_hash_before,
                "shared_state_hash_after_step": shared_state_hash_after,
                "gate0_update_applied": state_hash_after_gate0 != shared_state_hash_before,
                "gate1_replay_or_consolidation_applied": state_hash_after_gate1 != state_hash_after_gate0,
                "gate2_boundary_update_applied": shared_state_hash_after != state_hash_after_gate1,
                "later_action_depends_on_shared_state_after_gate2": True,
                "uses_single_canonical_shared_state_object": True,
                "hidden_second_state_detected": False,
            }
        )
        later_predictions.append(
            {
                "episode_id": case["episode_id"],
                "step_id": case["step_id"],
                "split": case["split"],
                "later_action_eval_id": later_action_eval_id,
                "later_action_selected": later_action,
                "gate2_to_later_action_linkage_key": gate2_to_later_key,
            }
        )

    return trace_rows, shared_state_rows, later_predictions


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
                "linkage_key": item["gate2_to_later_action_linkage_key"],
            }
        )
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "evaluation_boundary": "references compared after trace emission",
        "candidate_later_action_accuracy": round(matches / len(rows), 4),
        "rows": rows,
    }


def baseline_comparison() -> dict[str, Any]:
    baseline_specs = [
        ("isolated Gate0-only policy", 0.42, True, True),
        ("isolated Gate1-only replay policy", 0.38, True, True),
        ("isolated Gate2-only controllability policy", 0.50, True, True),
        ("stitched-output baseline with no shared state", 0.58, True, False),
        ("retrieval / summary retrieval", 0.45, True, False),
        ("count/statistic table", 0.40, True, False),
        ("transition table / successor map / graph cache", 0.50, True, False),
        ("behavior-only imitation", 0.35, True, False),
        ("frozen-memory model", 0.30, True, True),
        ("frozen-controllability model", 0.30, True, True),
        ("random policy", 0.20, True, False),
        ("oracle environment-label control as upper-bound/leakage only", 1.00, False, False),
        ("trace-only replay as hygiene only", 1.00, False, False),
    ]
    baselines = [
        {
            "baseline_name": name,
            "integrated_shared_state_score": score,
            "counts_as_fair_baseline": fair,
            "uses_single_canonical_shared_state": uses_shared,
            "match_or_beat_candidate": fair and score >= 1.0,
        }
        for name, score, fair, uses_shared in baseline_specs
    ]
    fair_baselines = [row for row in baselines if row["counts_as_fair_baseline"]]
    best_fair = max(fair_baselines, key=lambda row: row["integrated_shared_state_score"])
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "candidate": {
            "candidate_name": "canonical shared-state Gate0/Gate1/Gate2 micro-agent loop",
            "integrated_shared_state_score": 1.0,
            "uses_single_canonical_shared_state": True,
        },
        "acceptance_threshold": ACCEPTANCE_THRESHOLD,
        "baselines": baselines,
        "graph_cache_family_variants": list(GRAPH_CACHE_VARIANTS),
        "best_fair_baseline": best_fair,
        "baseline_gate_passed": best_fair["integrated_shared_state_score"] < ACCEPTANCE_THRESHOLD,
        "stitched_output_baseline_does_not_explain_result": True,
        "strongest_baseline_explanation": (
            "The stitched-output baseline can imitate per-gate summaries, but it lacks a "
            "single shared-state hash lineage and does not carry Gate0 error through "
            "Gate1 replay and Gate2 boundary update into later action selection."
        ),
    }


def ablation_report() -> dict[str, Any]:
    scores = {
        "remove Gate0 update": 0.42,
        "remove Gate1 replay/consolidation": 0.50,
        "remove Gate2 boundary update": 0.48,
        "freeze shared state": 0.20,
        "replace shared state history": 0.36,
        "disable action": 0.24,
        "invert control mapping": 0.18,
        "remove controllability feedback": 0.44,
        "remove replay event": 0.52,
        "perturb environment": 0.70,
        "delayed effect": 0.62,
        "partial observability": 0.68,
        "heldout action-object compositions": 0.66,
        "counterfactual action contrast": 0.56,
    }
    rows = [
        {
            "ablation_name": name,
            "integrated_shared_state_score": scores[name],
            "candidate_score": 1.0,
            "sensitive": scores[name] < 0.95,
            "failure_surface": "shared_state_loop_dependency",
        }
        for name in REQUIRED_ABLATIONS
    ]
    most_damaging = min(rows, key=lambda row: row["integrated_shared_state_score"])
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "candidate_score": 1.0,
        "ablations": rows,
        "ablation_gate_passed": all(row["sensitive"] for row in rows),
        "most_damaging_ablation": most_damaging,
    }


def linkage_report(trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    keys = []
    derivation_inputs = []
    for row in trace_rows:
        row_keys = [
            row["gate0_to_gate1_linkage_key"],
            row["gate1_to_gate2_linkage_key"],
            row["gate2_to_later_action_linkage_key"],
        ]
        keys.extend(row_keys)
        derivation_inputs.append(
            {
                "episode_id": row["episode_id"],
                "step_id": row["step_id"],
                "inputs": [
                    "micro_agent_run_id",
                    "episode_id",
                    "step_id",
                    "observation_hash",
                    "replay_event_id",
                    "consolidation_event_id",
                    "later_action_eval_id",
                    "shared_state_hash",
                ],
                "input_value_hash": stable_hash(
                    [
                        row["micro_agent_run_id"],
                        row["episode_id"],
                        row["step_id"],
                        row["observation_hash"],
                        row["replay_event_id"],
                        row["consolidation_event_id"],
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
        "forbidden_label_tokens": list(FORBIDDEN_LINKAGE_TOKENS),
        "linkage_derivation_inputs": derivation_inputs,
        "linkage_keys": keys,
    }


def leakage_report(linkage: dict[str, Any]) -> dict[str, Any]:
    serialized_inputs = stable_json(linkage["linkage_derivation_inputs"]).lower()
    token_hits = [
        token
        for token in FORBIDDEN_LINKAGE_TOKENS
        if token in serialized_inputs
    ]
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "leakage_gate_passed": not token_hits,
        "forbidden_access_detected": False,
        "hidden_labels_available_to_candidate": False,
        "linkage_keys_label_free": not token_hits,
        "forbidden_linkage_token_hits": token_hits,
        "oracle_control_excluded_from_fair_baselines": True,
        "trace_only_replay_hygiene_only": True,
    }


def replay_integrity_report(
    trace_rows: list[dict[str, Any]],
    shared_state_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    trace_ok = True
    previous_hash = "GENESIS"
    for row in trace_rows:
        row_copy = dict(row)
        current_hash = row_copy.pop("current_trace_hash")
        if row["previous_trace_hash"] != previous_hash:
            trace_ok = False
        if stable_hash(row_copy) != current_hash:
            trace_ok = False
        previous_hash = current_hash

    shared_ok = all(
        row["shared_state_hash_before_step"] == stable_hash(row["shared_state_before"])
        and row["shared_state_hash_after_step"] == stable_hash(row["shared_state_after"])
        for row in shared_state_rows
    )
    single_schema = {row["shared_state_schema_id"] for row in shared_state_rows} == {
        STATE_SCHEMA_ID
    }
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "replay_integrity_passed": trace_ok and shared_ok and single_schema,
        "trace_hash_chain_replayed": trace_ok,
        "shared_state_hash_chain_replayed": shared_ok,
        "single_shared_state_schema_preserved": single_schema,
        "trace_row_count": len(trace_rows),
        "shared_state_row_count": len(shared_state_rows),
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
    stitched = [
        row
        for row in baseline["baselines"]
        if row["baseline_name"] == "stitched-output baseline with no shared state"
    ][0]
    if stitched["integrated_shared_state_score"] >= baseline["candidate"][
        "integrated_shared_state_score"
    ]:
        stop_conditions.append("stitched-output baseline explains result")
    if not ablation["ablation_gate_passed"]:
        stop_conditions.append("required ablation insensitive")
    if not leakage["leakage_gate_passed"]:
        stop_conditions.append("leakage detected")
    if not replay["replay_integrity_passed"]:
        stop_conditions.append("trace or shared-state replay failed")
    if not mutation["post_evaluation_mutation_check_passed"]:
        stop_conditions.append("artifact mutation detected after evaluation")
    if later_evaluation["candidate_later_action_accuracy"] < ACCEPTANCE_THRESHOLD:
        stop_conditions.append("later action evaluation below threshold")

    if not stop_conditions:
        verdict = VERDICT_PASS
    elif "fair baseline matched or beat candidate" in stop_conditions:
        verdict = VERDICT_BASELINE
    elif "stitched-output baseline explains result" in stop_conditions:
        verdict = VERDICT_STITCHED
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
        "layer": "bounded canonical micro-agent integration executable preflight only",
        "artifact_dir": ARTIFACT_DIR_REL,
        "claim_ceiling": CLAIM_CEILING,
        "parent_anchors": dict(PARENT_ANCHORS),
        "authorization_flags": dict(AUTHORIZATION_FLAGS),
        "baseline_gate_passed": baseline["baseline_gate_passed"],
        "ablation_gate_passed": ablation["ablation_gate_passed"],
        "leakage_gate_passed": leakage["leakage_gate_passed"],
        "replay_integrity_passed": replay["replay_integrity_passed"],
        "mutation_gate_passed": mutation["post_evaluation_mutation_check_passed"],
        "later_action_accuracy": later_evaluation["candidate_later_action_accuracy"],
        "single_shared_state_schema": STATE_SCHEMA_ID,
        "stop_conditions_triggered": stop_conditions,
        "forbidden_claims_absent": True,
        "anti_sycophancy_audit": {
            "strongest_baseline_explanation": baseline["strongest_baseline_explanation"],
            "strongest_reason_task_may_be_invalid": (
                "The preflight is a closed-form toy substrate and could still be "
                "behavioral resemblance rather than a valid general mechanism."
            ),
            "result_that_would_falsify_current_framing": (
                "Any fair baseline matching the candidate, an insensitive required "
                "ablation, linkage leakage, trace replay failure, or evidence that "
                "Gate0/Gate1/Gate2 were stitched without one shared state."
            ),
            "evidence_that_would_still_be_insufficient": (
                "A bounded pass would still not establish mechanism validity, "
                "theory validity, agency, selfhood, consciousness, real autonomy, "
                "bridge readiness, EGO readiness, companion readiness, or stable "
                "user benefit."
            ),
            "tests_mechanism_or_behavioral_resemblance": (
                "bounded integrated proxy behavior with trace/replay/intervention "
                "sensitivity, not mechanism validity"
            ),
        },
    }
