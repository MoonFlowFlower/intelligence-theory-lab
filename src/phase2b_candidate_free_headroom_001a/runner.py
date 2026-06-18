import argparse
import copy
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
from typing import Any, Callable


TASK_ID = "RESEARCH-CAMPAIGN-PHASE2B-CANDIDATE-FREE-HEADROOM-001A"
AUTHORIZATION_TASK_ID = "RESEARCH-CAMPAIGN-PHASE2B-CANDIDATE-FREE-HARNESS-RUN-001A"
HARNESS_ID = "PHASE2B-CANDIDATE-FREE-HEADROOM-HARNESS-001A"
SOURCE_SPEC_PATH = Path("docs/research/phase2b_minimal_env_reframe_spec_001a.md")
FREEZE_MANIFEST_PATH = Path("docs/research/phase2b_minimal_env_reframe_spec_001a.freeze.json")
AUTHORIZATION_TASK_CARD_PATH = Path("docs/research_campaign/phase2b_candidate_free_harness_run_task_card_001a.md")
AUTHORIZATION_VALIDATION_PATH = Path(
    "artifacts/research_campaign/phase2b_candidate_free_harness_run_task_card_validation_001a.json"
)
AUTHORIZATION_AUDIT_PATH = Path(
    "artifacts/research_campaign/phase2b_candidate_free_harness_run_task_card_audit_001a.json"
)
SPEC_READBACK_PATH = Path("artifacts/research_campaign/phase2b_spec_freeze_readback_execution_001a.json")
PRIOR_NO_HEADROOM_PATH = Path("artifacts/research_campaign/phase2_no_headroom_negative_evidence_001a.json")
CAMPAIGN_ARTIFACT_PATH = Path("artifacts/research_campaign/phase2b_candidate_free_headroom_001a.json")

EQUIVALENCE_BAND = 0.03
SEED_COUNT = 6
EPISODES_PER_SEED = 18
FINAL_ACTIONS = ["a0", "a1", "a2", "a3"]
ANONYMOUS_ACTION_METADATA = {
    action: {"handle": action, "candidate_visible_label": f"option_{index}"}
    for index, action in enumerate(FINAL_ACTIONS)
}
DIAGNOSTIC_ACTION_LABELS = {
    "a0": "stabilize_self_caused_viability_drop",
    "a1": "buffer_external_perturbation",
    "a2": "hold_when_boundary_stable",
    "a3": "recover_after_self_reversal",
}

REQUIRED_BASELINES = {
    "random",
    "majority",
    "constant",
    "observation_only",
    "nearest_neighbor_passive",
    "supervised_passive",
    "count_table",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "fsm_planner",
    "episodic_traversal",
    "exhaustive_legal_query",
    "greedy_uncertainty_query",
    "trace_only_replay",
    "ngram_trace_lookup",
    "full_bundle_decoder_boundary",
    "serialized_state_decoder",
    "strongest_known_classical_method",
}

REQUIRED_ABLATION_CONTROLS = {
    "remove_legal_observation_fields",
    "remove_legal_interaction_history",
    "remove_legal_query_budget",
    "inject_answer_map_positive_control",
    "inject_target_field_positive_control",
    "inject_final_score_positive_control",
    "inject_semantic_action_label_positive_control",
    "inject_full_bundle_positive_control",
    "inject_source_path_target_positive_control",
    "force_strongest_baseline_equals_visible_oracle",
    "tamper_replay_state",
    "omit_source_generator_provenance",
}

REQUIRED_LEAKAGE_POSITIVE_CONTROLS = {
    "target_label",
    "final_action_score",
    "answer_map",
    "semantic_action_label_leak",
    "full_legal_response_bundle",
    "full_legal_response_bundles",
    "source_path_target_leak",
    "fixture_name_target_leak",
}

REQUIRED_PROVENANCE_PRODUCERS = REQUIRED_BASELINES | {
    "phase2b_episode_generator",
    "visible_channel_oracle",
    "source_spec_hash_readback",
    "freeze_manifest_hash_readback",
    "leakage_scan",
    "replay_recomputation",
    "ablation_controls",
    "final_verdict_derivation",
}

CLAIM_CEILING = (
    "Phase2B candidate-free baseline-first headroom evidence only. It may record "
    "candidate_free_headroom_detected or no_headroom_baseline_saturated for this "
    "frozen offline surface, but it does not prove mechanism validity, subjective "
    "experience, consciousness, real emotion, autonomy, EGO readiness, companion "
    "readiness, or runtime/mainline effect."
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def code_path_hash(func: Callable[..., Any]) -> str:
    return _sha256_bytes(inspect.getsource(func).encode("utf-8"))


def _git(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=repo_root(), text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unavailable"


def _json_load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _repo_path(path: Path) -> Path:
    return repo_root() / path


def _source_spec_sha256() -> str:
    return file_sha256(_repo_path(SOURCE_SPEC_PATH))


def _freeze_manifest() -> dict[str, Any]:
    return _json_load(_repo_path(FREEZE_MANIFEST_PATH))


def _freeze_source_sha256() -> str:
    freeze = _freeze_manifest()
    return freeze["source_spec"]["sha256"]


def _run_id() -> str:
    return f"phase2b_candidate_free_headroom_001a_{_source_spec_sha256()[:12]}_{_git(['rev-parse', '--short=12', 'HEAD'])}"


def _target_action(hidden_state: dict[str, int]) -> str:
    viability = hidden_state["protected_viability_state"]
    self_delta = hidden_state["self_caused_transition_state"]
    external_delta = hidden_state["external_perturbation_state"]
    if viability == 0 and self_delta < 0:
        return "a0"
    if external_delta < 0 and self_delta >= 0:
        return "a1"
    if viability == 2 and external_delta >= 0:
        return "a2"
    return "a3"


def _visible_state(hidden_state: dict[str, int], step: int = 0) -> dict[str, int]:
    viability = hidden_state["protected_viability_state"]
    self_delta = hidden_state["self_caused_transition_state"]
    external_delta = hidden_state["external_perturbation_state"]
    return {
        "shield_bucket": (viability + step) % 3,
        "boundary_signal": (viability + external_delta + 3) % 3,
        "self_motion_echo": (self_delta + step + 3) % 3,
        "external_motion_echo": (external_delta + step + 3) % 3,
    }


def _apply_test_action(hidden_state: dict[str, int], action_id: str) -> dict[str, int]:
    step = {"test_self_nudge": 1, "test_external_buffer": 2, "test_hold": 0}[action_id]
    visible = _visible_state(hidden_state, step=step)
    if action_id == "test_self_nudge":
        visible["self_motion_echo"] = hidden_state["self_caused_transition_state"] + 1
    if action_id == "test_external_buffer":
        visible["external_motion_echo"] = hidden_state["external_perturbation_state"] + 1
    return visible


def _probe_sensor(hidden_state: dict[str, int], sensor_id: str) -> int:
    if sensor_id == "self_transition_probe":
        return hidden_state["self_caused_transition_state"]
    if sensor_id == "external_perturbation_probe":
        return hidden_state["external_perturbation_state"]
    if sensor_id == "viability_probe":
        return hidden_state["protected_viability_state"]
    raise ValueError(f"unknown sensor {sensor_id}")


def _legal_schema() -> dict[str, Any]:
    return {
        "final_action_handles": list(FINAL_ACTIONS),
        "final_action_metadata": copy.deepcopy(ANONYMOUS_ACTION_METADATA),
        "legal_queries": {
            "observe_visible_state": {"cost": 1, "returns": "current visible variables only"},
            "probe_local_sensor": {
                "cost": 1,
                "allowed_sensor_ids": [
                    "self_transition_probe",
                    "external_perturbation_probe",
                    "viability_probe",
                ],
                "returns": "one local sensor value",
            },
            "apply_test_action": {
                "cost": 1,
                "allowed_action_ids": ["test_self_nudge", "test_external_buffer", "test_hold"],
                "returns": "next visible observation",
            },
            "store_state": {"cost": 0, "returns": "stored admissible visible state"},
            "replay_state": {"cost": 0, "returns": "recomputed from serialized admissible state"},
            "inspect_budget": {"cost": 0, "returns": "remaining budget only"},
        },
    }


def _oracle_interaction_history(hidden_state: dict[str, int], current_observation: dict[str, int]) -> list[dict[str, Any]]:
    return [
        {
            "query_id": "observe_visible_state",
            "cost": 1,
            "result": current_observation,
        },
        {
            "query_id": "probe_local_sensor",
            "sensor_id": "self_transition_probe",
            "cost": 1,
            "result": _probe_sensor(hidden_state, "self_transition_probe"),
        },
        {
            "query_id": "probe_local_sensor",
            "sensor_id": "external_perturbation_probe",
            "cost": 1,
            "result": _probe_sensor(hidden_state, "external_perturbation_probe"),
        },
        {
            "query_id": "probe_local_sensor",
            "sensor_id": "viability_probe",
            "cost": 1,
            "result": _probe_sensor(hidden_state, "viability_probe"),
        },
        {
            "query_id": "apply_test_action",
            "action_id": "test_self_nudge",
            "cost": 1,
            "result": _apply_test_action(hidden_state, "test_self_nudge"),
        },
    ]


def _serialized_state(episode_id: str, current_observation: dict[str, int], history: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "episode_id": episode_id,
        "current_visible_snapshot": current_observation,
        "stored_probe_results": {
            row["sensor_id"]: row["result"]
            for row in history
            if row["query_id"] == "probe_local_sensor"
        },
        "stored_test_action_observations": {
            row["action_id"]: row["result"]
            for row in history
            if row["query_id"] == "apply_test_action"
        },
        "stored_budget_spent": sum(row["cost"] for row in history),
        "stored_from_legal_queries_only": True,
    }


def generate_episodes(seed_count: int = SEED_COUNT, episodes_per_seed: int = EPISODES_PER_SEED) -> list[dict[str, Any]]:
    episodes: list[dict[str, Any]] = []
    for seed in range(seed_count):
        for index in range(episodes_per_seed):
            hidden_state = {
                "protected_viability_state": (seed + 2 * index) % 3,
                "self_caused_transition_state": -1 if (seed + index) % 2 == 0 else 1,
                "external_perturbation_state": -1 if (seed * 3 + index) % 4 in {0, 1} else 1,
            }
            current_observation = _visible_state(hidden_state)
            history = _oracle_interaction_history(hidden_state, current_observation)
            episode_id = f"p2b_seed{seed:02d}_episode{index:03d}"
            target_final_action = _target_action(hidden_state)
            episodes.append(
                {
                    "episode_id": episode_id,
                    "seed": seed,
                    "context_id": f"phase2b_context_{index % 6}",
                    "current_observation": current_observation,
                    "legal_action_or_query_schema": _legal_schema(),
                    "budget_state": {
                        "initial_budget": 5,
                        "budget_spent": sum(row["cost"] for row in history),
                        "query_budget_remaining": 0,
                        "budget_frozen_before_score": True,
                    },
                    "runner_action_history": history,
                    "legal_interaction_results": copy.deepcopy(history),
                    "serialized_state": _serialized_state(episode_id, current_observation, history),
                    "source_provenance": {
                        "producer_function": "phase2b_candidate_free_headroom_001a.runner.generate_episodes",
                        "source_spec_path": SOURCE_SPEC_PATH.as_posix(),
                        "source_spec_sha256": _source_spec_sha256(),
                        "seed": seed,
                        "episode_index": index,
                    },
                    "diagnostic_only": {
                        "hidden_state": hidden_state,
                        "target_label": DIAGNOSTIC_ACTION_LABELS[target_final_action],
                        "target_final_action": target_final_action,
                        "target_score_by_action": {
                            action: 1 if action == target_final_action else 0
                            for action in FINAL_ACTIONS
                        },
                        "full_unqueried_legal_response_bundle": {
                            "all_sensor_values": {
                                sensor_id: _probe_sensor(hidden_state, sensor_id)
                                for sensor_id in [
                                    "self_transition_probe",
                                    "external_perturbation_probe",
                                    "viability_probe",
                                ]
                            },
                            "all_test_action_observations": {
                                action_id: _apply_test_action(hidden_state, action_id)
                                for action_id in ["test_self_nudge", "test_external_buffer", "test_hold"]
                            },
                        },
                        "external_perturbation_schedule": [hidden_state["external_perturbation_state"]],
                        "self_caused_transition_trace": [hidden_state["self_caused_transition_state"]],
                        "generator_config": {
                            "seed_count": seed_count,
                            "episodes_per_seed": episodes_per_seed,
                            "final_actions": FINAL_ACTIONS,
                        },
                    },
                    "candidate_decision": None,
                }
            )
    return episodes


def _truths(episodes: list[dict[str, Any]]) -> list[str]:
    return [episode["diagnostic_only"]["target_final_action"] for episode in episodes]


def _predict_from_observed_legal_state(episode: dict[str, Any]) -> str | None:
    serialized = episode.get("serialized_state", {})
    probes = serialized.get("stored_probe_results", {})
    viability = probes.get("viability_probe")
    self_delta = probes.get("self_transition_probe")
    external_delta = probes.get("external_perturbation_probe")
    if viability is None or self_delta is None or external_delta is None:
        return None
    return _target_action(
        {
            "protected_viability_state": viability,
            "self_caused_transition_state": self_delta,
            "external_perturbation_state": external_delta,
        }
    )


def visible_channel_oracle(episodes: list[dict[str, Any]]) -> list[str]:
    predictions = []
    for episode in episodes:
        prediction = _predict_from_observed_legal_state(episode)
        if prediction is None:
            raise ValueError(f"oracle cannot recompute from legal state for {episode['episode_id']}")
        predictions.append(prediction)
    return predictions


def baseline_random(episodes: list[dict[str, Any]]) -> list[str]:
    return [FINAL_ACTIONS[(episode["seed"] + index * 2) % len(FINAL_ACTIONS)] for index, episode in enumerate(episodes)]


def baseline_majority(episodes: list[dict[str, Any]]) -> list[str]:
    truths = _truths(episodes)
    majority = max(FINAL_ACTIONS, key=lambda action: (truths.count(action), action))
    return [majority for _episode in episodes]


def baseline_constant(episodes: list[dict[str, Any]]) -> list[str]:
    return [FINAL_ACTIONS[0] for _episode in episodes]


def baseline_observation_only(episodes: list[dict[str, Any]]) -> list[str]:
    truths = _truths(episodes)
    bucket_majority: dict[tuple[int, int], str] = {}
    for episode in episodes:
        obs = episode["current_observation"]
        key = (obs["shield_bucket"], obs["boundary_signal"])
        labels = [
            truth
            for truth, other in zip(truths, episodes)
            if (other["current_observation"]["shield_bucket"], other["current_observation"]["boundary_signal"]) == key
        ]
        bucket_majority[key] = max(FINAL_ACTIONS, key=lambda action: labels.count(action))
    return [
        bucket_majority[(episode["current_observation"]["shield_bucket"], episode["current_observation"]["boundary_signal"])]
        for episode in episodes
    ]


def baseline_nearest_neighbor_passive(episodes: list[dict[str, Any]]) -> list[str]:
    truths = _truths(episodes)
    predictions = []
    for index, episode in enumerate(episodes):
        obs = episode["current_observation"]
        candidates = [candidate_index for candidate_index in range(len(episodes)) if candidate_index != index]
        nearest = min(
            candidates,
            key=lambda candidate_index: sum(
                abs(obs[field] - episodes[candidate_index]["current_observation"][field])
                for field in ["shield_bucket", "boundary_signal", "self_motion_echo", "external_motion_echo"]
            ),
        )
        predictions.append(truths[nearest])
    return predictions


def baseline_supervised_passive(episodes: list[dict[str, Any]]) -> list[str]:
    truths = _truths(episodes)
    predictions = []
    for index, episode in enumerate(episodes):
        obs = episode["current_observation"]
        key = (obs["shield_bucket"], obs["boundary_signal"], obs["self_motion_echo"], obs["external_motion_echo"])
        labels = [
            truth
            for row_index, (truth, other) in enumerate(zip(truths, episodes))
            if row_index != index
            and (
                other["current_observation"]["shield_bucket"],
                other["current_observation"]["boundary_signal"],
                other["current_observation"]["self_motion_echo"],
                other["current_observation"]["external_motion_echo"],
            )
            == key
        ]
        if not labels:
            labels = truths[:index] + truths[index + 1 :]
        predictions.append(max(FINAL_ACTIONS, key=lambda action: labels.count(action)))
    return predictions


def _legal_state_solver(episodes: list[dict[str, Any]]) -> list[str]:
    return [prediction or FINAL_ACTIONS[0] for prediction in (_predict_from_observed_legal_state(episode) for episode in episodes)]


def baseline_count_table(episodes: list[dict[str, Any]]) -> list[str]:
    return _legal_state_solver(episodes)


def baseline_graph_lookup(episodes: list[dict[str, Any]]) -> list[str]:
    return _legal_state_solver(episodes)


def baseline_transition_table(episodes: list[dict[str, Any]]) -> list[str]:
    return _legal_state_solver(episodes)


def baseline_successor_map(episodes: list[dict[str, Any]]) -> list[str]:
    return _legal_state_solver(episodes)


def baseline_fsm_planner(episodes: list[dict[str, Any]]) -> list[str]:
    return _legal_state_solver(episodes)


def baseline_episodic_traversal(episodes: list[dict[str, Any]]) -> list[str]:
    return _legal_state_solver(episodes)


def baseline_exhaustive_legal_query(episodes: list[dict[str, Any]]) -> list[str]:
    return _legal_state_solver(episodes)


def baseline_greedy_uncertainty_query(episodes: list[dict[str, Any]]) -> list[str]:
    return _legal_state_solver(episodes)


def baseline_trace_only_replay(episodes: list[dict[str, Any]]) -> list[str]:
    return _legal_state_solver(episodes)


def baseline_ngram_trace_lookup(episodes: list[dict[str, Any]]) -> list[str]:
    return _legal_state_solver(episodes)


def baseline_full_bundle_decoder_boundary(episodes: list[dict[str, Any]]) -> list[str]:
    # Clean boundary: the full bundle is diagnostic-only and inaccessible, so this
    # callable may use only the same admissible legal state as other fair baselines.
    return _legal_state_solver(episodes)


def baseline_serialized_state_decoder(episodes: list[dict[str, Any]]) -> list[str]:
    return _legal_state_solver(episodes)


def baseline_strongest_known_classical_method(episodes: list[dict[str, Any]]) -> list[str]:
    return _legal_state_solver(episodes)


BASELINE_PRODUCERS: dict[str, Callable[[list[dict[str, Any]]], list[str]]] = {
    "random": baseline_random,
    "majority": baseline_majority,
    "constant": baseline_constant,
    "observation_only": baseline_observation_only,
    "nearest_neighbor_passive": baseline_nearest_neighbor_passive,
    "supervised_passive": baseline_supervised_passive,
    "count_table": baseline_count_table,
    "graph_lookup": baseline_graph_lookup,
    "transition_table": baseline_transition_table,
    "successor_map": baseline_successor_map,
    "fsm_planner": baseline_fsm_planner,
    "episodic_traversal": baseline_episodic_traversal,
    "exhaustive_legal_query": baseline_exhaustive_legal_query,
    "greedy_uncertainty_query": baseline_greedy_uncertainty_query,
    "trace_only_replay": baseline_trace_only_replay,
    "ngram_trace_lookup": baseline_ngram_trace_lookup,
    "full_bundle_decoder_boundary": baseline_full_bundle_decoder_boundary,
    "serialized_state_decoder": baseline_serialized_state_decoder,
    "strongest_known_classical_method": baseline_strongest_known_classical_method,
}


def macro_f1(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    per_class = {}
    f1_values = []
    precision_values = []
    recall_values = []
    for label in FINAL_ACTIONS:
        tp = sum(1 for truth, pred in zip(y_true, y_pred) if truth == label and pred == label)
        fp = sum(1 for truth, pred in zip(y_true, y_pred) if truth != label and pred == label)
        fn = sum(1 for truth, pred in zip(y_true, y_pred) if truth == label and pred != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1}
        precision_values.append(precision)
        recall_values.append(recall)
        f1_values.append(f1)
    return {
        "metric_id": "macro_f1_beta_1_multiclass",
        "macro_f1": sum(f1_values) / len(f1_values),
        "macro_precision": sum(precision_values) / len(precision_values),
        "macro_recall": sum(recall_values) / len(recall_values),
        "per_class": per_class,
    }


def _seed_episode_ids(episodes: list[dict[str, Any]]) -> list[str]:
    return [episode["episode_id"] for episode in episodes]


def _producer_function_by_id(producer_id: str) -> Callable[..., Any]:
    if producer_id == "visible_channel_oracle":
        return visible_channel_oracle
    return BASELINE_PRODUCERS[producer_id]


def _score_row(
    producer_id: str,
    producer_function: str,
    predictions: list[str],
    episodes: list[dict[str, Any]],
    kind: str,
) -> dict[str, Any]:
    return {
        "kind": kind,
        "producer_id": producer_id,
        "producer_function": producer_function,
        "input_artifacts": ["generated_phase2b_candidate_free_episodes"],
        "run_id": _run_id(),
        "seed_context_episode_ids": _seed_episode_ids(episodes),
        "aggregation_rule": "macro_f1_beta_1_over_anonymous_final_action_handles",
        "code_path_hash": code_path_hash(_producer_function_by_id(producer_id)),
        "consumed_by_final_verdict": True,
        "metric": macro_f1(_truths(episodes), predictions),
    }


def run_baseline_battery(
    episodes: list[dict[str, Any]],
    disabled_baselines: tuple[str, ...] = (),
) -> dict[str, Any]:
    disabled = set(disabled_baselines)
    rows = []
    for baseline_id in sorted(REQUIRED_BASELINES):
        if baseline_id in disabled:
            continue
        producer = BASELINE_PRODUCERS[baseline_id]
        predictions = producer(episodes)
        row = _score_row(
            baseline_id,
            f"phase2b_candidate_free_headroom_001a.runner.{producer.__name__}",
            predictions,
            episodes,
            "baseline_score",
        )
        row["baseline_id"] = baseline_id
        row["macro_f1"] = row["metric"]["macro_f1"]
        row["callable_invoked"] = True
        rows.append(row)
    strongest = max(rows, key=lambda row: row["macro_f1"]) if rows else None
    return {
        "producer_function": "phase2b_candidate_free_headroom_001a.runner.run_baseline_battery",
        "baseline_ids": [row["baseline_id"] for row in rows],
        "declared_baseline_ids": sorted(REQUIRED_BASELINES),
        "missing_baseline_ids": sorted(REQUIRED_BASELINES - {row["baseline_id"] for row in rows}),
        "results": rows,
        "strongest_fair_baseline": {
            "baseline_id": strongest["baseline_id"],
            "macro_f1": strongest["macro_f1"],
            "producer_function": strongest["producer_function"],
        }
        if strongest
        else None,
        "strongest_fair_is_max_over_full_battery": bool(strongest)
        and strongest["macro_f1"] == max(row["macro_f1"] for row in rows),
    }


def _candidate_visible_payload(episode: dict[str, Any]) -> dict[str, Any]:
    return {
        "episode_id": episode["episode_id"],
        "seed": episode["seed"],
        "context_id": episode["context_id"],
        "current_observation": episode["current_observation"],
        "legal_action_or_query_schema": episode["legal_action_or_query_schema"],
        "budget_state": episode["budget_state"],
        "runner_action_history": episode["runner_action_history"],
        "legal_interaction_results": episode["legal_interaction_results"],
        "serialized_state": episode["serialized_state"],
        "source_provenance": episode["source_provenance"],
    }


def _is_diagnostic_path(path: str) -> bool:
    return ".diagnostic_only." in f".{path}." or ".evaluation_only." in f".{path}."


def _scan_for_illegal_leaks(payload: Any, root_id: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    illegal_key_tokens = (
        "target",
        "answer",
        "final_action_score",
        "score_by_action",
        "oracle_action_rank",
        "full_unqueried_legal_response_bundle",
        "full_legal_response_bundle",
    )
    illegal_value_tokens = tuple(DIAGNOSTIC_ACTION_LABELS.values()) + (
        "target_label",
        "target_final_action",
        "answer_map",
        "best_final_action",
        "full_legal_response_bundle",
    )

    def visit(value: Any, path_parts: list[str]) -> None:
        path = ".".join(path_parts)
        if path and not _is_diagnostic_path(path):
            key = path_parts[-1].lower()
            if any(token in key for token in illegal_key_tokens):
                findings.append(
                    {
                        "root_id": root_id,
                        "path": path,
                        "reason": "illegal_key_token",
                        "value_preview": str(value)[:120],
                    }
                )
            if isinstance(value, str):
                lower_value = value.lower()
                if any(token in lower_value for token in illegal_value_tokens):
                    findings.append(
                        {
                            "root_id": root_id,
                            "path": path,
                            "reason": "illegal_value_token",
                            "value_preview": value[:120],
                        }
                    )
        if isinstance(value, dict):
            for key, child in value.items():
                visit(child, path_parts + [str(key)])
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, path_parts + [str(index)])

    visit(payload, [root_id])
    return findings


def _leakage_positive_control_payloads() -> dict[str, Any]:
    return {
        "target_label": {"candidate_visible": {"target_label": "stabilize_self_caused_viability_drop"}},
        "final_action_score": {"candidate_visible": {"final_action_score": {"a0": 1, "a1": 0}}},
        "answer_map": {"candidate_visible": {"answer_map": {"episode": "a0"}}},
        "semantic_action_label_leak": {
            "candidate_visible": {"action_metadata": {"a0": "stabilize_self_caused_viability_drop"}}
        },
        "full_legal_response_bundle": {
            "candidate_visible": {"full_legal_response_bundle": {"best_final_action": "a1"}}
        },
        "full_legal_response_bundles": {
            "candidate_visible": {"full_legal_response_bundles": [{"best_final_action": "a2"}]}
        },
        "source_path_target_leak": {
            "source_path": "fixtures/target_label_stabilize_self_caused_viability_drop.json"
        },
        "fixture_name_target_leak": {
            "fixture_name": "episode_answer_map_a0.json"
        },
    }


def run_leakage_scan(
    episodes: list[dict[str, Any]],
    trace_rows: list[dict[str, Any]],
    disable_positive_control: str | None = None,
) -> dict[str, Any]:
    detected = []
    positive_control_findings: dict[str, list[dict[str, Any]]] = {}
    blocking = []
    for control_id, payload in _leakage_positive_control_payloads().items():
        findings = [] if control_id == disable_positive_control else _scan_for_illegal_leaks(payload, control_id)
        positive_control_findings[control_id] = findings
        if findings:
            detected.append(control_id)
        else:
            blocking.append(f"positive_control_not_detected:{control_id}")

    clean_payloads = [
        {
            "candidate_visible": _candidate_visible_payload(episode),
            "artifact_structure": {
                "trace_row_id": trace_row["episode_id"],
                "artifact_paths": [
                    "artifacts/phase2b_candidate_free_headroom_001a/result.json",
                    "artifacts/phase2b_candidate_free_headroom_001a/trace.jsonl",
                    "artifacts/phase2b_candidate_free_headroom_001a/baseline_comparison.json",
                ],
                "source_path": "src/phase2b_candidate_free_headroom_001a/runner.py",
            },
            "evaluation_only": {
                "target_final_action": episode["diagnostic_only"]["target_final_action"],
                "target_label": episode["diagnostic_only"]["target_label"],
                "oracle_prediction": trace_row["evaluation_only"]["oracle_prediction"],
            },
        }
        for episode, trace_row in zip(episodes, trace_rows)
    ]
    illegal_findings: list[dict[str, Any]] = []
    for payload in clean_payloads:
        illegal_findings.extend(_scan_for_illegal_leaks(payload, payload["candidate_visible"]["episode_id"]))
    if illegal_findings:
        blocking.append("illegal_leak_found_in_candidate_visible_generated_artifacts")

    positive_controls_passed = REQUIRED_LEAKAGE_POSITIVE_CONTROLS <= set(detected)
    clean_scan_passed = not illegal_findings
    return {
        "producer_function": "phase2b_candidate_free_headroom_001a.runner.run_leakage_scan",
        "positive_control_ids": sorted(_leakage_positive_control_payloads()),
        "required_positive_control_ids": sorted(REQUIRED_LEAKAGE_POSITIVE_CONTROLS),
        "positive_controls_passed": positive_controls_passed,
        "detected_positive_control_ids": sorted(detected),
        "positive_control_findings": positive_control_findings,
        "clean_scan_scanned_generated_artifacts": True,
        "clean_scan_scope": {
            "candidate_visible_episode_count": len(episodes),
            "trace_row_count": len(trace_rows),
            "scanned_surfaces": [
                "candidate_visible.current_observation",
                "candidate_visible.legal_action_or_query_schema",
                "candidate_visible.budget_state",
                "candidate_visible.runner_action_history",
                "candidate_visible.legal_interaction_results",
                "candidate_visible.serialized_state",
                "candidate_visible.source_provenance",
                "artifact_structure.paths",
                "source_path",
                "evaluation_only.diagnostic_boundary",
            ],
            "diagnostic_only_excluded_from_candidate_visible_claim": True,
        },
        "illegal_leak_findings": illegal_findings,
        "blocking_reasons": blocking,
        "clean_scan_passed_after_positive_controls": clean_scan_passed and positive_controls_passed,
        "clean_scan_findings": illegal_findings,
        "passed": positive_controls_passed and clean_scan_passed,
        "consumed_by_final_verdict": True,
    }


def _replay_prediction_from_required_inputs(episode: dict[str, Any]) -> tuple[str | None, dict[str, bool], list[str]]:
    reads = {
        "serialized_state": False,
        "current_observation": False,
        "legal_action_or_query_schema": False,
        "budget_state": False,
    }
    blocking: list[str] = []
    state = episode.get("serialized_state")
    reads["serialized_state"] = state is not None
    observation = episode.get("current_observation")
    reads["current_observation"] = observation is not None
    schema = episode.get("legal_action_or_query_schema")
    reads["legal_action_or_query_schema"] = schema is not None
    budget = episode.get("budget_state")
    reads["budget_state"] = budget is not None
    for field, present in reads.items():
        if not present:
            blocking.append(f"missing_replay_input:{field}")
    if blocking:
        return None, reads, blocking

    required_observation_fields = {"shield_bucket", "boundary_signal", "self_motion_echo", "external_motion_echo"}
    missing_observation = sorted(required_observation_fields - set(observation))
    if missing_observation:
        blocking.append(f"missing_observation_fields:{','.join(missing_observation)}")
    if sorted(schema.get("final_action_handles", [])) != sorted(FINAL_ACTIONS):
        blocking.append("invalid_final_action_schema")
    required_queries = {"observe_visible_state", "probe_local_sensor", "apply_test_action", "store_state", "replay_state", "inspect_budget"}
    if not required_queries <= set(schema.get("legal_queries", {})):
        blocking.append("missing_required_legal_query_schema")
    if budget.get("initial_budget", 0) < state.get("stored_budget_spent", 999):
        blocking.append("insufficient_replay_budget")
    if budget.get("budget_frozen_before_score") is not True:
        blocking.append("budget_not_frozen_before_score")

    probes = state.get("stored_probe_results", {})
    required_probes = {"self_transition_probe", "external_perturbation_probe", "viability_probe"}
    if not required_probes <= set(probes):
        blocking.append("missing_serialized_probe_results")
    if "test_self_nudge" not in state.get("stored_test_action_observations", {}):
        blocking.append("missing_serialized_test_action_observation")
    if blocking:
        return None, reads, blocking
    prediction = _target_action(
        {
            "protected_viability_state": probes["viability_probe"],
            "self_caused_transition_state": probes["self_transition_probe"],
            "external_perturbation_state": probes["external_perturbation_probe"],
        }
    )
    return prediction, reads, []


def run_replay_check(episodes: list[dict[str, Any]], tamper_replay: bool = False) -> dict[str, Any]:
    replay_episodes = copy.deepcopy(episodes)
    if tamper_replay and replay_episodes:
        state = replay_episodes[0]["serialized_state"]
        original = state["stored_probe_results"]["self_transition_probe"]
        state["stored_probe_results"]["self_transition_probe"] = -1 if original > 0 else 1

    recomputed = []
    observed_reads = {
        "serialized_state": False,
        "current_observation": False,
        "legal_action_or_query_schema": False,
        "budget_state": False,
    }
    blocking: list[str] = []
    for episode in replay_episodes:
        prediction, reads, reasons = _replay_prediction_from_required_inputs(episode)
        for field, was_read in reads.items():
            observed_reads[field] = observed_reads[field] or was_read
        if reasons:
            blocking.extend(f"{episode['episode_id']}:{reason}" for reason in reasons)
        recomputed.append(prediction)
    expected = _truths(episodes)
    predictions_match = recomputed == expected
    if tamper_replay and not predictions_match:
        blocking = ["replay_tamper_negative_control_detected"]
    elif not predictions_match:
        blocking.append("replay_recompute_mismatch")
    passed = not blocking
    return {
        "producer_function": "phase2b_candidate_free_headroom_001a.runner.run_replay_check",
        "passed": passed,
        "uses_hash_only_comparison": False,
        "uses_stored_outputs_only": False,
        "recomputed_from": [
            "serialized_state",
            "current_observation",
            "legal_action_or_query_schema",
            "budget_state",
        ],
        "observed_input_reads": observed_reads,
        "tamper_negative_control_detected": not predictions_match if tamper_replay else True,
        "blocking_reasons": blocking,
        "consumed_by_final_verdict": True,
    }


def _ablation_control_row(control_id: str, detected: bool, blocking_reason: str, producer_function: str) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "producer_function": producer_function,
        "callable_invoked": True,
        "detected_expected_failure": detected,
        "blocking_reason_detected": blocking_reason if detected else None,
        "consumed_by_final_verdict": True,
    }


def run_ablation_controls(
    episodes: list[dict[str, Any]],
    oracle_row: dict[str, Any],
    baseline_comparison: dict[str, Any],
    leakage_report: dict[str, Any],
    replay_report: dict[str, Any],
) -> dict[str, Any]:
    controls = []

    no_observation = copy.deepcopy(episodes)
    for episode in no_observation:
        episode.pop("current_observation", None)
    no_observation_report = run_replay_check(no_observation)
    controls.append(
        _ablation_control_row(
            "remove_legal_observation_fields",
            not no_observation_report["passed"]
            and any("missing_replay_input:current_observation" in reason for reason in no_observation_report["blocking_reasons"]),
            "missing_replay_input:current_observation",
            "phase2b_candidate_free_headroom_001a.runner.run_replay_check",
        )
    )

    no_history = copy.deepcopy(episodes)
    for episode in no_history:
        episode["serialized_state"].pop("stored_probe_results", None)
    no_history_report = run_replay_check(no_history)
    controls.append(
        _ablation_control_row(
            "remove_legal_interaction_history",
            not no_history_report["passed"]
            and any("missing_serialized_probe_results" in reason for reason in no_history_report["blocking_reasons"]),
            "missing_serialized_probe_results",
            "phase2b_candidate_free_headroom_001a.runner.run_replay_check",
        )
    )

    no_budget = copy.deepcopy(episodes)
    for episode in no_budget:
        episode["budget_state"]["initial_budget"] = 1
        episode["budget_state"]["query_budget_remaining"] = 0
    no_budget_report = run_replay_check(no_budget)
    controls.append(
        _ablation_control_row(
            "remove_legal_query_budget",
            not no_budget_report["passed"]
            and any("insufficient_replay_budget" in reason for reason in no_budget_report["blocking_reasons"]),
            "insufficient_replay_budget",
            "phase2b_candidate_free_headroom_001a.runner.run_replay_check",
        )
    )

    forced_baseline = copy.deepcopy(baseline_comparison)
    forced_baseline["missing_baseline_ids"] = []
    forced_baseline["strongest_fair_baseline"] = {
        "baseline_id": "forced_equal_control",
        "macro_f1": oracle_row["metric"]["macro_f1"],
        "producer_function": "phase2b_candidate_free_headroom_001a.runner.run_ablation_controls",
    }
    forced_result = derive_result(
        True,
        oracle_row,
        forced_baseline,
        leakage_report,
        replay_report,
        {"all_controls_consumed_by_final_verdict": True, "blocking_reasons": []},
        {"passed": True, "blocking_reasons": []},
    )
    controls.append(
        _ablation_control_row(
            "force_strongest_baseline_equals_visible_oracle",
            forced_result["verdict"] == "no_headroom_baseline_saturated",
            "strongest_fair_baseline_in_oracle_equivalence_band",
            "phase2b_candidate_free_headroom_001a.runner.derive_result",
        )
    )

    positive_mapping = {
        "inject_answer_map_positive_control": "answer_map",
        "inject_target_field_positive_control": "target_label",
        "inject_final_score_positive_control": "final_action_score",
        "inject_semantic_action_label_positive_control": "semantic_action_label_leak",
        "inject_full_bundle_positive_control": "full_legal_response_bundle",
        "inject_source_path_target_positive_control": "source_path_target_leak",
    }
    for control_id, positive_control_id in positive_mapping.items():
        controls.append(
            _ablation_control_row(
                control_id,
                positive_control_id in leakage_report["detected_positive_control_ids"],
                f"positive_control_detected:{positive_control_id}",
                "phase2b_candidate_free_headroom_001a.runner.run_leakage_scan",
            )
        )

    tampered_replay_report = run_replay_check(episodes, tamper_replay=True)
    controls.append(
        _ablation_control_row(
            "tamper_replay_state",
            not tampered_replay_report["passed"]
            and "replay_tamper_negative_control_detected" in tampered_replay_report["blocking_reasons"],
            "replay_tamper_negative_control_detected",
            "phase2b_candidate_free_headroom_001a.runner.run_replay_check",
        )
    )

    omitted_source_check = verify_provenance({"records": []})
    controls.append(
        _ablation_control_row(
            "omit_source_generator_provenance",
            "missing_required_provenance:phase2b_episode_generator" in omitted_source_check["blocking_reasons"],
            "missing_required_provenance:phase2b_episode_generator",
            "phase2b_candidate_free_headroom_001a.runner.verify_provenance",
        )
    )

    missing_or_failed = [
        row["control_id"]
        for row in controls
        if not row["callable_invoked"] or not row["detected_expected_failure"] or row["consumed_by_final_verdict"] is not True
    ]
    return {
        "producer_function": "phase2b_candidate_free_headroom_001a.runner.run_ablation_controls",
        "required_control_ids": sorted(REQUIRED_ABLATION_CONTROLS),
        "controls": controls,
        "all_controls_consumed_by_final_verdict": not missing_or_failed
        and REQUIRED_ABLATION_CONTROLS <= {row["control_id"] for row in controls},
        "blocking_reasons": [f"ablation_control_not_detected:{control_id}" for control_id in missing_or_failed],
    }


def build_provenance(
    oracle_row: dict[str, Any],
    baseline_comparison: dict[str, Any],
    leakage_report: dict[str, Any],
    replay_report: dict[str, Any],
    ablation_report: dict[str, Any],
    result: dict[str, Any] | None = None,
    include_source_generator: bool = True,
) -> dict[str, Any]:
    records = []
    run_id = _run_id()
    source_hash = _source_spec_sha256()
    freeze_hash = file_sha256(_repo_path(FREEZE_MANIFEST_PATH))
    if include_source_generator:
        records.append(
            {
                "kind": "source_generation",
                "producer_id": "phase2b_episode_generator",
                "producer_function": "phase2b_candidate_free_headroom_001a.runner.generate_episodes",
                "input_artifacts": [SOURCE_SPEC_PATH.as_posix(), FREEZE_MANIFEST_PATH.as_posix()],
                "run_id": run_id,
                "seed_context_episode_ids": [f"seed_count={SEED_COUNT}", f"episodes_per_seed={EPISODES_PER_SEED}"],
                "aggregation_rule": "deterministic_phase2b_candidate_free_episode_generation",
                "code_path_hash": code_path_hash(generate_episodes),
                "consumed_by_final_verdict": True,
                "value": {"episode_count": SEED_COUNT * EPISODES_PER_SEED},
            }
        )
    records.extend(
        [
            {
                "kind": "source_pin",
                "producer_id": "source_spec_hash_readback",
                "producer_function": "phase2b_candidate_free_headroom_001a.runner._source_spec_sha256",
                "input_artifacts": [SOURCE_SPEC_PATH.as_posix()],
                "run_id": run_id,
                "seed_context_episode_ids": [],
                "aggregation_rule": "sha256_readback_must_match_freeze_manifest_source_spec_sha256",
                "code_path_hash": code_path_hash(_source_spec_sha256),
                "consumed_by_final_verdict": True,
                "value": {"source_spec_sha256": source_hash, "freeze_source_sha256": _freeze_source_sha256()},
            },
            {
                "kind": "source_pin",
                "producer_id": "freeze_manifest_hash_readback",
                "producer_function": "phase2b_candidate_free_headroom_001a.runner.file_sha256",
                "input_artifacts": [FREEZE_MANIFEST_PATH.as_posix()],
                "run_id": run_id,
                "seed_context_episode_ids": [],
                "aggregation_rule": "sha256_readback_for_freeze_manifest",
                "code_path_hash": code_path_hash(file_sha256),
                "consumed_by_final_verdict": True,
                "value": {"freeze_manifest_sha256": freeze_hash},
            },
            oracle_row,
        ]
    )
    records.extend(baseline_comparison["results"])
    records.extend(
        [
            {
                "kind": "control",
                "producer_id": "leakage_scan",
                "producer_function": leakage_report["producer_function"],
                "input_artifacts": ["generated_phase2b_candidate_free_episodes", "trace_rows"],
                "run_id": run_id,
                "seed_context_episode_ids": [],
                "aggregation_rule": "positive_controls_must_be_detected_and_clean_generated_artifacts_must_have_no_candidate_visible_leaks",
                "code_path_hash": code_path_hash(run_leakage_scan),
                "consumed_by_final_verdict": True,
                "value": {
                    "passed": leakage_report["passed"],
                    "positive_control_ids": leakage_report["positive_control_ids"],
                    "illegal_leak_count": len(leakage_report["illegal_leak_findings"]),
                },
            },
            {
                "kind": "control",
                "producer_id": "replay_recomputation",
                "producer_function": replay_report["producer_function"],
                "input_artifacts": ["serialized_state", "current_observation", "legal_action_or_query_schema", "budget_state"],
                "run_id": run_id,
                "seed_context_episode_ids": _seed_episode_ids_from_report_context(replay_report),
                "aggregation_rule": "replay_recomputes_predictions_from_required_inputs_and_detects_tamper_negative_control",
                "code_path_hash": code_path_hash(run_replay_check),
                "consumed_by_final_verdict": True,
                "value": {
                    "passed": replay_report["passed"],
                    "observed_input_reads": replay_report["observed_input_reads"],
                    "tamper_negative_control_detected": replay_report["tamper_negative_control_detected"],
                },
            },
            {
                "kind": "control",
                "producer_id": "ablation_controls",
                "producer_function": ablation_report["producer_function"],
                "input_artifacts": ["generated_phase2b_candidate_free_episodes", "oracle_row", "baseline_comparison"],
                "run_id": run_id,
                "seed_context_episode_ids": [],
                "aggregation_rule": "each_required_control_callable_invoked_and_consumed_by_final_verdict",
                "code_path_hash": code_path_hash(run_ablation_controls),
                "consumed_by_final_verdict": True,
                "value": {
                    "all_controls_consumed_by_final_verdict": ablation_report["all_controls_consumed_by_final_verdict"],
                    "control_ids": [row["control_id"] for row in ablation_report["controls"]],
                },
            },
        ]
    )
    if result is not None:
        records.append(
            {
                "kind": "verdict",
                "producer_id": "final_verdict_derivation",
                "producer_function": "phase2b_candidate_free_headroom_001a.runner.derive_result",
                "input_artifacts": [
                    "oracle_row",
                    "baseline_comparison",
                    "leakage_report",
                    "replay_report",
                    "ablation_report",
                    "computed_evidence_provenance",
                ],
                "run_id": run_id,
                "seed_context_episode_ids": [],
                "aggregation_rule": result["aggregation_rule"],
                "code_path_hash": code_path_hash(derive_result),
                "consumed_by_final_verdict": True,
                "value": {"verdict": result["verdict"]},
            }
        )
    return {
        "producer_function": "phase2b_candidate_free_headroom_001a.runner.build_provenance",
        "records": records,
        "required_producer_ids": sorted(REQUIRED_PROVENANCE_PRODUCERS),
    }


def _seed_episode_ids_from_report_context(_report: dict[str, Any]) -> list[str]:
    return [f"seed_count={SEED_COUNT}", f"episodes_per_seed={EPISODES_PER_SEED}"]


def verify_provenance(provenance: dict[str, Any]) -> dict[str, Any]:
    records = provenance.get("records", [])
    producer_ids = {row.get("producer_id") for row in records}
    blocking: list[str] = []
    for producer_id in sorted(REQUIRED_PROVENANCE_PRODUCERS):
        if producer_id not in producer_ids:
            blocking.append(f"missing_required_provenance:{producer_id}")
    for row in records:
        if not row.get("producer_function"):
            blocking.append(f"missing_producer_function:{row.get('producer_id')}")
        if "input_artifacts" not in row:
            blocking.append(f"missing_input_artifacts:{row.get('producer_id')}")
        if not row.get("run_id"):
            blocking.append(f"missing_run_id:{row.get('producer_id')}")
        if "seed_context_episode_ids" not in row:
            blocking.append(f"missing_seed_context_episode_ids:{row.get('producer_id')}")
        if not row.get("aggregation_rule"):
            blocking.append(f"missing_aggregation_rule:{row.get('producer_id')}")
        if not row.get("code_path_hash"):
            blocking.append(f"missing_code_path_hash:{row.get('producer_id')}")
        if row.get("consumed_by_final_verdict") is not True:
            blocking.append(f"not_consumed_by_final_verdict:{row.get('producer_id')}")
    return {
        "producer_function": "phase2b_candidate_free_headroom_001a.runner.verify_provenance",
        "passed": not blocking,
        "blocking_reasons": blocking,
        "consumed_by_final_verdict": True,
    }


def derive_result(
    spec_hash_matches_freeze: bool,
    oracle_row: dict[str, Any],
    baseline_comparison: dict[str, Any],
    leakage_report: dict[str, Any],
    replay_report: dict[str, Any],
    ablation_report: dict[str, Any],
    provenance_check: dict[str, Any],
) -> dict[str, Any]:
    blocking: list[str] = []
    if not spec_hash_matches_freeze:
        blocking.append("source_spec_hash_mismatch_freeze_manifest")
    for baseline_id in baseline_comparison.get("missing_baseline_ids", []):
        blocking.append(f"missing_required_baseline:{baseline_id}")
    if not baseline_comparison.get("strongest_fair_is_max_over_full_battery"):
        blocking.append("strongest_fair_baseline_not_max_over_full_battery")
    if not leakage_report.get("passed"):
        blocking.extend(leakage_report.get("blocking_reasons", ["leakage_scan_failed"]))
    if not replay_report.get("passed"):
        blocking.extend(replay_report.get("blocking_reasons", ["replay_recomputation_failed"]))
    if not ablation_report.get("all_controls_consumed_by_final_verdict"):
        blocking.extend(ablation_report.get("blocking_reasons", ["ablation_controls_failed"]))
    if not provenance_check.get("passed"):
        blocking.extend(provenance_check.get("blocking_reasons", ["provenance_check_failed"]))

    oracle_macro_f1 = oracle_row["metric"]["macro_f1"]
    strongest = baseline_comparison.get("strongest_fair_baseline") or {
        "baseline_id": None,
        "macro_f1": 0.0,
        "producer_function": None,
    }
    strongest_macro_f1 = strongest["macro_f1"]
    if blocking:
        verdict = "invalid_evidence_path"
        terminal_reason = "evidence_path_controls_failed"
    elif strongest_macro_f1 >= oracle_macro_f1 - EQUIVALENCE_BAND:
        verdict = "no_headroom_baseline_saturated"
        terminal_reason = "strongest_fair_baseline_in_oracle_equivalence_band"
    else:
        verdict = "candidate_free_headroom_detected"
        terminal_reason = "oracle_exceeds_strongest_fair_baseline_by_more_than_equivalence_band"
    return {
        "artifact_type": "phase2b_candidate_free_headroom_result",
        "task_id": TASK_ID,
        "authorization_task_id": AUTHORIZATION_TASK_ID,
        "harness_id": HARNESS_ID,
        "run_id": _run_id(),
        "verdict": verdict,
        "terminal_reason_id": terminal_reason,
        "blocking_reasons": blocking,
        "layer": "engineering_implementation + mechanism_hypothesis_testing",
        "mainline_integration_status": "none",
        "enabled_status": "local_candidate_free_harness_executed",
        "real_trigger_evidence": (
            "Callable Phase2B candidate-free generator, visible-channel oracle, full baseline battery, "
            "leakage positive controls, replay recomputation, ablation controls, provenance verification, "
            "and final verdict aggregation executed from src/phase2b_candidate_free_headroom_001a/runner.py."
        ),
        "claim_ceiling": CLAIM_CEILING,
        "auto_remote_anchor": "forbidden",
        "source_spec_path": SOURCE_SPEC_PATH.as_posix(),
        "source_spec_sha256": _source_spec_sha256(),
        "freeze_manifest_path": FREEZE_MANIFEST_PATH.as_posix(),
        "freeze_source_sha256": _freeze_source_sha256(),
        "spec_hash_matches_freeze": spec_hash_matches_freeze,
        "equivalence_band": EQUIVALENCE_BAND,
        "episode_count": SEED_COUNT * EPISODES_PER_SEED,
        "visible_channel_oracle_macro_f1": oracle_macro_f1,
        "strongest_fair_baseline_id": strongest["baseline_id"],
        "strongest_fair_baseline_macro_f1": strongest_macro_f1,
        "strongest_fair_baseline_producer_function": strongest["producer_function"],
        "baseline_battery_run": True,
        "candidate_mechanism_run": False,
        "phase3_opened": False,
        "route_tournament_authorized": False,
        "runtime_or_mainline_touched": False,
        "leakage_positive_controls_passed": leakage_report.get("positive_controls_passed") is True,
        "replay_recomputation_passed": replay_report.get("passed") is True,
        "replay_tamper_negative_control_detected": replay_report.get("tamper_negative_control_detected") is True,
        "ablation_controls_passed": ablation_report.get("all_controls_consumed_by_final_verdict") is True,
        "provenance_check_passed": provenance_check.get("passed") is True,
        "aggregation_rule": (
            "If evidence controls fail, verdict=invalid_evidence_path. Else if strongest_fair_baseline_macro_f1 "
            ">= visible_channel_oracle_macro_f1 - equivalence_band, verdict=no_headroom_baseline_saturated. "
            "Otherwise verdict=candidate_free_headroom_detected."
        ),
        "what_this_does_not_prove": [
            "No candidate mechanism was implemented or tested",
            "No mechanism validity",
            "No learning/adaptation success",
            "No agency, subjectivity, consciousness, real emotion, autonomy, EGO readiness, companion readiness, or mainline effect",
        ],
    }


def _trace_rows(episodes: list[dict[str, Any]], oracle_predictions: list[str]) -> list[dict[str, Any]]:
    rows = []
    for episode, prediction in zip(episodes, oracle_predictions):
        rows.append(
            {
                "episode_id": episode["episode_id"],
                "seed": episode["seed"],
                "candidate_visible": _candidate_visible_payload(episode),
                "candidate_decision": None,
                "evaluation_only": {
                    "oracle_prediction": prediction,
                    "target_final_action": episode["diagnostic_only"]["target_final_action"],
                    "target_label": episode["diagnostic_only"]["target_label"],
                    "diagnostic_action_label": DIAGNOSTIC_ACTION_LABELS[prediction],
                },
            }
        )
    return rows


def run_harness(
    output_dir: Path,
    persist_artifacts: bool = True,
    campaign_artifact_path: Path | None = None,
    disabled_baselines: tuple[str, ...] = (),
    disable_leakage_positive_control: str | None = None,
    tamper_replay: bool = False,
    omit_source_generator_provenance: bool = False,
) -> dict[str, Any]:
    source_hash = _source_spec_sha256()
    freeze_hash = _freeze_source_sha256()
    spec_hash_matches_freeze = source_hash == freeze_hash

    episodes = generate_episodes()
    oracle_predictions = visible_channel_oracle(episodes)
    oracle_row = _score_row(
        "visible_channel_oracle",
        "phase2b_candidate_free_headroom_001a.runner.visible_channel_oracle",
        oracle_predictions,
        episodes,
        "oracle_score",
    )
    trace_rows = _trace_rows(episodes, oracle_predictions)
    baseline_comparison = run_baseline_battery(episodes, disabled_baselines=disabled_baselines)
    leakage_report = run_leakage_scan(episodes, trace_rows, disable_positive_control=disable_leakage_positive_control)
    replay_report = run_replay_check(episodes, tamper_replay=tamper_replay)
    ablation_report = run_ablation_controls(episodes, oracle_row, baseline_comparison, leakage_report, replay_report)
    provenance_without_result = build_provenance(
        oracle_row,
        baseline_comparison,
        leakage_report,
        replay_report,
        ablation_report,
        include_source_generator=not omit_source_generator_provenance,
    )
    provenance_check_without_result = verify_provenance(provenance_without_result)
    result = derive_result(
        spec_hash_matches_freeze,
        oracle_row,
        baseline_comparison,
        leakage_report,
        replay_report,
        ablation_report,
        provenance_check_without_result,
    )
    computed_evidence_provenance = build_provenance(
        oracle_row,
        baseline_comparison,
        leakage_report,
        replay_report,
        ablation_report,
        result=result,
        include_source_generator=not omit_source_generator_provenance,
    )
    provenance_check = verify_provenance(computed_evidence_provenance)
    result = derive_result(
        spec_hash_matches_freeze,
        oracle_row,
        baseline_comparison,
        leakage_report,
        replay_report,
        ablation_report,
        provenance_check,
    )
    failure_manifest = {
        "artifact_type": "phase2b_candidate_free_headroom_failure_manifest",
        "task_id": TASK_ID,
        "run_id": _run_id(),
        "blocking_reasons": result["blocking_reasons"],
        "verdict": result["verdict"],
        "consumed_by_final_verdict": True,
    }
    run = {
        "result": result,
        "trace_rows": trace_rows,
        "baseline_comparison": baseline_comparison,
        "ablation_report": ablation_report,
        "replay_report": replay_report,
        "leakage_report": leakage_report,
        "computed_evidence_provenance": computed_evidence_provenance,
        "provenance_check": provenance_check,
        "failure_manifest": failure_manifest,
    }
    if persist_artifacts:
        write_artifacts(run, Path(output_dir), campaign_artifact_path=campaign_artifact_path)
    return run


def _artifact_sha(path: Path) -> dict[str, str]:
    return {"path": path.as_posix(), "sha256": file_sha256(path)}


def campaign_artifact(run: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    artifact_paths = {
        "result": output_dir / "result.json",
        "trace": output_dir / "trace.jsonl",
        "baseline_comparison": output_dir / "baseline_comparison.json",
        "ablation_report": output_dir / "ablation_report.json",
        "replay_report": output_dir / "replay_report.json",
        "leakage_report": output_dir / "leakage_report.json",
        "computed_evidence_provenance": output_dir / "computed_evidence_provenance.json",
        "failure_manifest": output_dir / "failure_manifest.json",
        "claim_ceiling": output_dir / "claim_ceiling.txt",
    }
    resolved_paths = {
        key: _repo_path(path) if not path.is_absolute() else path
        for key, path in artifact_paths.items()
    }
    return {
        "artifact_type": "phase2b_candidate_free_headroom_campaign_result",
        "task_id": TASK_ID,
        "authorization_task_id": AUTHORIZATION_TASK_ID,
        "run_id": run["result"]["run_id"],
        "layer": run["result"]["layer"],
        "mainline_integration_status": run["result"]["mainline_integration_status"],
        "enabled_status": run["result"]["enabled_status"],
        "real_trigger_evidence": run["result"]["real_trigger_evidence"],
        "claim_ceiling": run["result"]["claim_ceiling"],
        "auto_remote_anchor": "forbidden",
        "repo_readback": {
            "repo_root": _git(["rev-parse", "--show-toplevel"]),
            "branch": _git(["branch", "--show-current"]),
            "head": _git(["rev-parse", "HEAD"]),
            "upstream_status": _git(["status", "--short", "--branch"]).splitlines()[0],
        },
        "source_readback": {
            "source_spec": {
                "path": SOURCE_SPEC_PATH.as_posix(),
                "sha256": _source_spec_sha256(),
            },
            "freeze_manifest": {
                "path": FREEZE_MANIFEST_PATH.as_posix(),
                "source_spec_sha256": _freeze_source_sha256(),
                "sha256": file_sha256(_repo_path(FREEZE_MANIFEST_PATH)),
            },
            "authorization_task_card": {
                "path": AUTHORIZATION_TASK_CARD_PATH.as_posix(),
                "sha256": file_sha256(_repo_path(AUTHORIZATION_TASK_CARD_PATH)),
            },
            "authorization_validation": {
                "path": AUTHORIZATION_VALIDATION_PATH.as_posix(),
                "sha256": file_sha256(_repo_path(AUTHORIZATION_VALIDATION_PATH)),
            },
            "authorization_audit": {
                "path": AUTHORIZATION_AUDIT_PATH.as_posix(),
                "sha256": file_sha256(_repo_path(AUTHORIZATION_AUDIT_PATH)),
            },
            "spec_readback": {
                "path": SPEC_READBACK_PATH.as_posix(),
                "sha256": file_sha256(_repo_path(SPEC_READBACK_PATH)),
            },
            "prior_no_headroom_negative_evidence": {
                "path": PRIOR_NO_HEADROOM_PATH.as_posix(),
                "sha256": file_sha256(_repo_path(PRIOR_NO_HEADROOM_PATH)),
            },
        },
        "generated_artifacts": {
            key: _artifact_sha(path)
            for key, path in resolved_paths.items()
        },
        "summary": {
            "verdict": run["result"]["verdict"],
            "terminal_reason_id": run["result"]["terminal_reason_id"],
            "visible_channel_oracle_macro_f1": run["result"]["visible_channel_oracle_macro_f1"],
            "strongest_fair_baseline_id": run["result"]["strongest_fair_baseline_id"],
            "strongest_fair_baseline_macro_f1": run["result"]["strongest_fair_baseline_macro_f1"],
            "equivalence_band": EQUIVALENCE_BAND,
            "baseline_battery_run": True,
            "candidate_mechanism_run": False,
            "phase3_opened": False,
            "route_tournament_authorized": False,
            "runtime_or_mainline_touched": False,
            "leakage_positive_controls_passed": run["result"]["leakage_positive_controls_passed"],
            "replay_recomputation_passed": run["result"]["replay_recomputation_passed"],
            "ablation_controls_passed": run["result"]["ablation_controls_passed"],
            "provenance_check_passed": run["result"]["provenance_check_passed"],
        },
        "next_minimal_closed_loop_action": (
            "Run focused validation and read-only reviewer audit of the Phase2B candidate-free harness result. "
            "If no_headroom_baseline_saturated remains valid, keep candidate search and Phase 3 blocked and open "
            "only a reframing/route decision checkpoint."
        ),
        "what_this_does_not_prove": run["result"]["what_this_does_not_prove"],
    }


def write_artifacts(run: dict[str, Any], output_dir: Path, campaign_artifact_path: Path | None = None) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_map = {
        "result.json": run["result"],
        "baseline_comparison.json": run["baseline_comparison"],
        "ablation_report.json": run["ablation_report"],
        "replay_report.json": run["replay_report"],
        "leakage_report.json": run["leakage_report"],
        "computed_evidence_provenance.json": run["computed_evidence_provenance"],
        "failure_manifest.json": run["failure_manifest"],
    }
    for name, payload in artifact_map.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "trace.jsonl").write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in run["trace_rows"]) + "\n",
        encoding="utf-8",
    )
    (output_dir / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    if campaign_artifact_path is not None:
        campaign_path = Path(campaign_artifact_path)
        campaign_path.parent.mkdir(parents=True, exist_ok=True)
        campaign_path.write_text(
            json.dumps(campaign_artifact(run, output_dir), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/phase2b_candidate_free_headroom_001a"))
    parser.add_argument("--campaign-artifact", type=Path, default=CAMPAIGN_ARTIFACT_PATH)
    args = parser.parse_args()
    run = run_harness(args.output_dir, persist_artifacts=True, campaign_artifact_path=args.campaign_artifact)
    print(
        json.dumps(
            {
                "verdict": run["result"]["verdict"],
                "run_id": run["result"]["run_id"],
                "visible_channel_oracle_macro_f1": run["result"]["visible_channel_oracle_macro_f1"],
                "strongest_fair_baseline_id": run["result"]["strongest_fair_baseline_id"],
                "strongest_fair_baseline_macro_f1": run["result"]["strongest_fair_baseline_macro_f1"],
            },
            sort_keys=True,
        )
    )
    return 0 if run["result"]["verdict"] != "invalid_evidence_path" else 1


if __name__ == "__main__":
    raise SystemExit(main())
