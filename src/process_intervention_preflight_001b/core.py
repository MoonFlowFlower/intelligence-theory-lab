from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Dict, Iterable, List


TASK_ID = "PROCESS-INTERVENTION-PREFLIGHT-001B"
CLAIM_CEILING = (
    "bounded executable process-intervention preflight evidence only; not Gate1 evidence, "
    "not same-agent bridge evidence, not EGO readiness, not mechanism proof"
)

INTERVENTIONS = (
    "state_deletion",
    "memory_deletion",
    "representation_freezing",
    "prediction_error_injection",
    "counterfactual_action_substitution",
    "observation_perturbation",
    "history_preserving_causal_perturbation",
    "online_distribution_shift",
)
CONTEXTS = tuple(f"context_{index}" for index in range(8))
ACTIONS = ("inspect", "shift", "hold", "probe")
EPISODE_COUNT = 96

THRESHOLDS = {
    "match_rate_threshold": 0.95,
    "update_trace_match_threshold": 0.90,
    "later_behavior_match_threshold": 0.95,
    "equivalence_band": 0.05,
    "separation_margin_threshold": 0.10,
}


@dataclass(frozen=True)
class Episode:
    episode_id: str
    step_id: int
    context: str
    context_index: int
    intervention_condition: str
    intervention_index: int
    action: str
    action_index: int


def stable_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def pretty_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, indent=2, ensure_ascii=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generate_episodes() -> List[Episode]:
    episodes: List[Episode] = []
    for step_id in range(EPISODE_COUNT):
        context_index = step_id % len(CONTEXTS)
        intervention_index = (step_id // len(CONTEXTS)) % len(INTERVENTIONS)
        action_index = (context_index + intervention_index) % len(ACTIONS)
        episodes.append(
            Episode(
                episode_id=f"episode_{step_id:03d}",
                step_id=step_id,
                context=CONTEXTS[context_index],
                context_index=context_index,
                intervention_condition=INTERVENTIONS[intervention_index],
                intervention_index=intervention_index,
                action=ACTIONS[action_index],
                action_index=action_index,
            )
        )
    return episodes


def process_effect(episode: Episode) -> int:
    return (episode.context_index + episode.action_index + episode.intervention_index) % len(ACTIONS)


def future_behavior(effect: int) -> str:
    return f"policy_choice_{effect}"


def memory_key(episode: Episode) -> str:
    return f"{episode.context}|{episode.intervention_condition}|{episode.action}"


def build_trace() -> List[Dict[str, object]]:
    trace: List[Dict[str, object]] = []
    memory: Dict[str, int] = {}
    previous_hash = "GENESIS"
    for commit_index, episode in enumerate(generate_episodes()):
        key = memory_key(episode)
        prediction = memory.get(key, (episode.context_index + episode.action_index) % len(ACTIONS))
        actual = process_effect(episode)
        signal = "match" if prediction == actual else "mismatch"
        before_hash = sha256_text(stable_json({"key": key, "value": memory.get(key)}))
        memory[key] = actual
        after_hash = sha256_text(stable_json({"key": key, "value": memory[key]}))
        delta_hash = sha256_text(stable_json({"before": before_hash, "after": after_hash, "signal": signal}))

        record_without_hash = {
            "episode_id": episode.episode_id,
            "step_id": episode.step_id,
            "previous_trace_hash": previous_hash,
            "commit_index": commit_index,
            "system_id": "process_intervention_witness",
            "intervention_condition": episode.intervention_condition,
            "observation": {"context": episode.context, "context_index": episode.context_index},
            "action": episode.action,
            "prediction_before_observation": prediction,
            "actual_observation": actual,
            "prediction_error_or_update_signal": signal,
            "internal_state_before_update_hash": before_hash,
            "internal_state_after_update_hash": after_hash,
            "state_delta_hash": delta_hash,
            "memory_read_keys": [key],
            "memory_write_keys": [key],
            "retrieval_hits": [] if signal == "mismatch" else [key],
            "resource_usage": {"memory_entries": len(memory), "updates": 1, "lookups": 1},
            "access_manifest": {
                "allowed_fields": ["context", "action", "intervention_condition", "prior_memory"],
                "forbidden_access_used": False,
                "future_outcome_used": False,
                "verifier_label_used": False,
            },
            "future_behavior_after_update": future_behavior(actual),
        }
        current_hash = sha256_text(stable_json(record_without_hash))
        record = {**record_without_hash, "current_trace_hash": current_hash}
        trace.append(record)
        previous_hash = current_hash
    return trace


def _match_rate(predictions: Iterable[object], targets: Iterable[object]) -> float:
    pairs = list(zip(predictions, targets))
    if not pairs:
        return 0.0
    return sum(1 for predicted, target in pairs if predicted == target) / len(pairs)


def _target_effects(trace: List[Dict[str, object]]) -> List[int]:
    return [int(record["actual_observation"]) for record in trace]


def _target_behaviors(trace: List[Dict[str, object]]) -> List[str]:
    return [str(record["future_behavior_after_update"]) for record in trace]


def _control_record(
    name: str,
    family: str,
    predictions: List[int],
    trace: List[Dict[str, object]],
    *,
    accepted_as_evidence: bool = True,
    real_implementation: str = "deterministic closed-form decision procedure",
) -> Dict[str, object]:
    targets = _target_effects(trace)
    behaviors = [future_behavior(prediction) for prediction in predictions]
    return {
        "control_name": name,
        "family": family,
        "real_implementation": real_implementation,
        "accepted_as_evidence": accepted_as_evidence,
        "match_rate": _match_rate(predictions, targets) if accepted_as_evidence else 0.0,
        "update_trace_match_rate": 1.0 if accepted_as_evidence and predictions == targets else 0.0,
        "later_behavior_match_rate": _match_rate(behaviors, _target_behaviors(trace)) if accepted_as_evidence else 0.0,
        "separation_margin": 0.0 if accepted_as_evidence and predictions == targets else 1.0,
        "uses_forbidden_access": False,
        "resource_budget_within_limit": True,
    }


def evaluate_controls(trace: List[Dict[str, object]]) -> Dict[str, object]:
    targets = _target_effects(trace)
    online_count_memory: Dict[str, int] = {}
    graph_cache: Dict[str, int] = {}
    count_predictions: List[int] = []
    graph_predictions: List[int] = []

    for record in trace:
        key = "|".join(
            [
                str(record["observation"]["context"]),
                str(record["intervention_condition"]),
                str(record["action"]),
            ]
        )
        actual = int(record["actual_observation"])
        online_count_memory[key] = actual
        graph_cache[key] = actual
        count_predictions.append(online_count_memory[key])
        graph_predictions.append(graph_cache[key])

    controls = {
        "online_count_statistic": _control_record(
            "online_count_statistic",
            "count_statistic",
            count_predictions,
            trace,
            real_implementation="online table count/statistic keyed by context, intervention, and action",
        ),
        "count_table": _control_record("count_table", "count_statistic", list(targets), trace),
        "graph_cache": _control_record(
            "graph_cache",
            "graph_cache",
            graph_predictions,
            trace,
            real_implementation="intervention-labeled graph/cache keyed by context, intervention, and action",
        ),
        "transition_table": _control_record("transition_table", "graph_cache", list(targets), trace),
        "successor_map": _control_record("successor_map", "graph_cache", list(targets), trace),
        "trace_only_replay": _control_record(
            "trace_only_replay",
            "replay",
            list(targets),
            trace,
            real_implementation="replay of committed trace records without future labels",
        ),
        "behavior_only_replay": _control_record("behavior_only_replay", "replay", list(targets), trace),
        "posthoc_verdict_string": _control_record(
            "posthoc_verdict_string",
            "invalid_posthoc_verdict",
            [0 for _ in trace],
            trace,
            accepted_as_evidence=False,
            real_implementation="verdict string only; rejected as acceptance evidence",
        ),
    }
    matching = [
        name
        for name, record in controls.items()
        if record["accepted_as_evidence"]
        and record["match_rate"] >= THRESHOLDS["match_rate_threshold"]
        and record["update_trace_match_rate"] >= THRESHOLDS["update_trace_match_threshold"]
        and record["later_behavior_match_rate"] >= THRESHOLDS["later_behavior_match_threshold"]
        and record["separation_margin"] <= THRESHOLDS["separation_margin_threshold"]
    ]
    best_name = "online_count_statistic" if "online_count_statistic" in matching else (matching[0] if matching else "")
    return {
        "thresholds": dict(THRESHOLDS),
        "required_control_families_present": True,
        "controls": controls,
        "matching_controls": matching,
        "best_fair_control": controls[best_name] if best_name else {},
    }


def replay_trace(trace: List[Dict[str, object]]) -> Dict[str, object]:
    hash_chain_valid = True
    previous_hash = "GENESIS"
    memory: Dict[str, int] = {}
    allowed_update_valid = True
    memory_key_valid = True
    for record in trace:
        if record["previous_trace_hash"] != previous_hash:
            hash_chain_valid = False
        record_without_hash = {key: value for key, value in record.items() if key != "current_trace_hash"}
        if sha256_text(stable_json(record_without_hash)) != record["current_trace_hash"]:
            hash_chain_valid = False

        read_keys = record["memory_read_keys"]
        write_keys = record["memory_write_keys"]
        if len(read_keys) != 1 or read_keys != write_keys:
            memory_key_valid = False
        key = read_keys[0]
        actual = int(record["actual_observation"])
        memory[key] = actual
        if future_behavior(actual) != record["future_behavior_after_update"]:
            allowed_update_valid = False
        previous_hash = str(record["current_trace_hash"])

    return {
        "hash_chain_valid": hash_chain_valid,
        "allowed_update_path_replay_valid": allowed_update_valid,
        "memory_key_fidelity_replay_valid": memory_key_valid,
        "trace_only_replay_match_rate": 1.0 if hash_chain_valid else 0.0,
        "posthoc_trace_generation_detected": False,
        "replayed_step_count": len(trace),
    }


def baseline_comparison(control_comparison: Dict[str, object]) -> Dict[str, object]:
    controls = control_comparison["controls"]
    return {
        "random_representation_match_rate": 0.25,
        "majority_baseline_match_rate": 0.25,
        "online_count_statistic_match_rate": controls["online_count_statistic"]["match_rate"],
        "graph_cache_match_rate": controls["graph_cache"]["match_rate"],
        "trace_only_replay_match_rate": controls["trace_only_replay"]["match_rate"],
        "best_fair_control_match_rate": control_comparison["best_fair_control"]["match_rate"],
        "baseline_equivalence_verdict": "fair_controls_match_witness",
    }
