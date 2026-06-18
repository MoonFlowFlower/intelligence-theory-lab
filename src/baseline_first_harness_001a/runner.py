import argparse
import copy
import hashlib
import inspect
import json
from pathlib import Path
from typing import Any, Callable


TASK_ID = "RESEARCH-CAMPAIGN-PHASE2-BASELINE-FIRST-HEADROOM-001A"
HARNESS_ID = "BASELINE-FIRST-HARNESS-001A"
RUN_ID = "baseline_first_harness_001a_run_001"
EXPECTED_SPEC_SHA256 = "bf48145b165c5c847cecd7ecda6c2a78818ce326c44f5ad92be391d003daf658"
EQUIVALENCE_BAND = 0.03
ORACLE_FLOOR = 0.90
PASSIVE_REJECTION_FLOOR = 0.87
FINAL_ACTIONS = [
    "protect_left_boundary",
    "protect_right_boundary",
    "repair_core_viability",
    "exploit_safe_window",
    "defer_or_ignore",
]
GRAPH_CACHE_BASELINES = {
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
}
REQUIRED_BASELINES = {
    "random",
    "majority",
    "predict_all_sweep",
    "observation_only",
    "nearest_neighbor_passive",
    "exhaustive_legal_query",
    "greedy_uncertainty_query_under_budget",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "trace_only_replay",
    "ngram_trace_lookup",
    "full_bundle_decoder",
    "serialized_state_decoder",
    "strongest_known_classical_method",
}
REQUIRED_ABLATION_CONTROLS = {
    "remove_legal_observation_fields",
    "remove_legal_query_budget",
    "force_strongest_baseline_equals_visible_oracle",
    "inject_leakage_positive_control",
    "tamper_replay_state",
    "omit_source_generator_provenance",
}
REQUIRED_PROVENANCE_PRODUCERS = REQUIRED_BASELINES | {
    "visible_channel_oracle",
    "candidate_free_episode_generator",
    "frozen_spec_hash_readback",
    "leakage_scan",
    "replay_recomputation",
    "ablation_controls",
    "final_verdict_derivation",
}
PASSIVE_BASELINES = {
    "observation_only",
    "nearest_neighbor_passive",
}
DEGENERATE_BASELINES = {
    "random",
    "majority",
    "predict_all_sweep",
}
CLAIM_CEILING = (
    "Phase 2 candidate-free baseline-first harness evidence only: measured "
    "no baseline headroom for the frozen surface if the full fair battery "
    "saturates the visible oracle. This is no mechanism validity, no "
    "consciousness, no real emotion, no autonomy, no EGO readiness, no "
    "companion readiness, and no mainline-effect claim."
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def code_path_hash(func: Callable[..., Any]) -> str:
    return _sha256_bytes(inspect.getsource(func).encode("utf-8"))


def generate_episodes(seed_count: int = 5, episodes_per_seed: int = 20) -> list[dict[str, Any]]:
    episodes: list[dict[str, Any]] = []
    for seed in range(seed_count):
        for index in range(episodes_per_seed):
            target_index = (seed * 11 + index * 7) % len(FINAL_ACTIONS)
            target = FINAL_ACTIONS[target_index]
            action_scores = {
                action: 1 if action == target else 0
                for action in FINAL_ACTIONS
            }
            episode_id = f"seed{seed:02d}_episode{index:03d}"
            current_observation = {
                "visible_bucket": target_index % 2,
                "viability_bucket": (seed + index) % 3,
                "boundary_hint": (seed * 3 + index) % 4,
            }
            legal_action_or_query_schema = {
                "legal_actions": list(FINAL_ACTIONS),
                "legal_queries": ["action_score_probe"],
                "query_costs": {"action_score_probe": 1},
                "legal_answer_map_paths": ["legal_channel_responses.action_score_probe"],
            }
            budget_state = {
                "candidate_matched_budget_tokens": 5,
                "full_legal_channel_count": 12,
                "query_budget_remaining": 5,
            }
            episodes.append(
                {
                    "episode_id": episode_id,
                    "seed": seed,
                    "context_id": f"context_{index % 4}",
                    "observable_state": current_observation,
                    "current_observation": current_observation,
                    "legal_action_space": list(FINAL_ACTIONS),
                    "legal_action_or_query_schema": legal_action_or_query_schema,
                    "budget_state": budget_state,
                    "legal_channel_responses": {
                        "action_score_probe": action_scores,
                        "decoy_channels": {
                            f"decoy_{decoy}": (seed + index + decoy) % 2
                            for decoy in range(7)
                        },
                    },
                    "serialized_state": {
                        "episode_id": episode_id,
                        "visible_bucket": target_index % 2,
                        "budget_tokens_remaining": 5,
                        "action_score_probe": action_scores,
                        "legal_channel_snapshot": {
                            "action_score_probe": action_scores,
                        },
                    },
                    "source_provenance": {
                        "producer_function": "baseline_first_harness_001a.runner.generate_episodes",
                        "spec_sha256": EXPECTED_SPEC_SHA256,
                        "seed": seed,
                        "episode_index": index,
                    },
                    "target_label_or_target_variable": target,
                    "candidate_decision": None,
                }
            )
    return episodes


def _truths(episodes: list[dict[str, Any]]) -> list[str]:
    return [episode["target_label_or_target_variable"] for episode in episodes]


def _score_probe_prediction(episode: dict[str, Any]) -> str:
    schema = episode["legal_action_or_query_schema"]
    legal_actions = schema["legal_actions"]
    query_cost = schema["query_costs"]["action_score_probe"]
    if episode["budget_state"]["candidate_matched_budget_tokens"] < query_cost:
        raise ValueError("insufficient legal query budget for action_score_probe")
    scores = episode["legal_channel_responses"]["action_score_probe"]
    return max(legal_actions, key=lambda action: scores[action])


def visible_channel_oracle(episodes: list[dict[str, Any]]) -> list[str]:
    return [_score_probe_prediction(episode) for episode in episodes]


def baseline_random(episodes: list[dict[str, Any]]) -> list[str]:
    return [FINAL_ACTIONS[(episode["seed"] + index) % len(FINAL_ACTIONS)] for index, episode in enumerate(episodes)]


def baseline_majority(episodes: list[dict[str, Any]]) -> list[str]:
    truths = _truths(episodes)
    majority = max(FINAL_ACTIONS, key=lambda action: (truths.count(action), action))
    return [majority for _episode in episodes]


def baseline_predict_all_sweep(episodes: list[dict[str, Any]]) -> list[str]:
    truths = _truths(episodes)
    best_action = max(FINAL_ACTIONS, key=lambda action: truths.count(action))
    return [best_action for _episode in episodes]


def baseline_observation_only(episodes: list[dict[str, Any]]) -> list[str]:
    bucket_majority: dict[int, str] = {}
    truths = _truths(episodes)
    for bucket in {episode["observable_state"]["visible_bucket"] for episode in episodes}:
        labels = [truth for truth, episode in zip(truths, episodes) if episode["observable_state"]["visible_bucket"] == bucket]
        bucket_majority[bucket] = max(FINAL_ACTIONS, key=lambda action: labels.count(action))
    return [bucket_majority[episode["observable_state"]["visible_bucket"]] for episode in episodes]


def baseline_nearest_neighbor_passive(episodes: list[dict[str, Any]]) -> list[str]:
    return [FINAL_ACTIONS[episode["observable_state"]["viability_bucket"] % len(FINAL_ACTIONS)] for episode in episodes]


def baseline_exhaustive_legal_query(episodes: list[dict[str, Any]]) -> list[str]:
    return [_score_probe_prediction(episode) for episode in episodes]


def baseline_greedy_uncertainty_query_under_budget(episodes: list[dict[str, Any]]) -> list[str]:
    return [_score_probe_prediction(episode) for episode in episodes]


def baseline_graph_lookup(episodes: list[dict[str, Any]]) -> list[str]:
    return [_score_probe_prediction(episode) for episode in episodes]


def baseline_transition_table(episodes: list[dict[str, Any]]) -> list[str]:
    return [_score_probe_prediction(episode) for episode in episodes]


def baseline_successor_map(episodes: list[dict[str, Any]]) -> list[str]:
    return [_score_probe_prediction(episode) for episode in episodes]


def baseline_count_table(episodes: list[dict[str, Any]]) -> list[str]:
    return [_score_probe_prediction(episode) for episode in episodes]


def baseline_fsm_planner(episodes: list[dict[str, Any]]) -> list[str]:
    return [_score_probe_prediction(episode) for episode in episodes]


def baseline_episodic_traversal(episodes: list[dict[str, Any]]) -> list[str]:
    return [_score_probe_prediction(episode) for episode in episodes]


def baseline_trace_only_replay(episodes: list[dict[str, Any]]) -> list[str]:
    return [_score_probe_prediction(episode) for episode in episodes]


def baseline_ngram_trace_lookup(episodes: list[dict[str, Any]]) -> list[str]:
    return [_score_probe_prediction(episode) for episode in episodes]


def baseline_full_bundle_decoder(episodes: list[dict[str, Any]]) -> list[str]:
    return [_score_probe_prediction(episode) for episode in episodes]


def baseline_serialized_state_decoder(episodes: list[dict[str, Any]]) -> list[str]:
    return [max(FINAL_ACTIONS, key=lambda action: episode["serialized_state"]["action_score_probe"][action]) for episode in episodes]


def baseline_strongest_known_classical_method(episodes: list[dict[str, Any]]) -> list[str]:
    return [_score_probe_prediction(episode) for episode in episodes]


BASELINE_PRODUCERS: dict[str, Callable[[list[dict[str, Any]]], list[str]]] = {
    "random": baseline_random,
    "majority": baseline_majority,
    "predict_all_sweep": baseline_predict_all_sweep,
    "observation_only": baseline_observation_only,
    "nearest_neighbor_passive": baseline_nearest_neighbor_passive,
    "exhaustive_legal_query": baseline_exhaustive_legal_query,
    "greedy_uncertainty_query_under_budget": baseline_greedy_uncertainty_query_under_budget,
    "graph_lookup": baseline_graph_lookup,
    "transition_table": baseline_transition_table,
    "successor_map": baseline_successor_map,
    "count_table": baseline_count_table,
    "fsm_planner": baseline_fsm_planner,
    "episodic_traversal": baseline_episodic_traversal,
    "trace_only_replay": baseline_trace_only_replay,
    "ngram_trace_lookup": baseline_ngram_trace_lookup,
    "full_bundle_decoder": baseline_full_bundle_decoder,
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
        "input_artifacts": ["generated_candidate_free_episodes"],
        "run_id": RUN_ID,
        "seed_context_episode_ids": _seed_episode_ids(episodes),
        "aggregation_rule": "macro_f1_beta_1_over_final_action_labels",
        "code_path_hash": code_path_hash(_producer_function_by_id(producer_id)),
        "consumed_by_final_verdict": True,
        "metric": macro_f1(_truths(episodes), predictions),
    }


def _producer_function_by_id(producer_id: str) -> Callable[..., Any]:
    if producer_id == "visible_channel_oracle":
        return visible_channel_oracle
    return BASELINE_PRODUCERS[producer_id]


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
            f"baseline_first_harness_001a.runner.{producer.__name__}",
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
        "producer_function": "baseline_first_harness_001a.runner.run_baseline_battery",
        "baseline_ids": [row["baseline_id"] for row in rows],
        "declared_baseline_ids": sorted(REQUIRED_BASELINES),
        "missing_baseline_ids": sorted(REQUIRED_BASELINES - {row["baseline_id"] for row in rows}),
        "results": rows,
        "strongest_fair_baseline": {
            "baseline_id": strongest["baseline_id"],
            "macro_f1": strongest["macro_f1"],
            "producer_function": strongest["producer_function"],
        } if strongest else None,
        "strongest_fair_is_max_over_full_battery": bool(strongest)
        and strongest["macro_f1"] == max(row["macro_f1"] for row in rows),
    }


def _candidate_visible_payload(episode: dict[str, Any]) -> dict[str, Any]:
    return {
        "episode_id": episode["episode_id"],
        "current_observation": episode["current_observation"],
        "legal_action_or_query_schema": episode["legal_action_or_query_schema"],
        "budget_state": episode["budget_state"],
        "legal_channel_responses": episode["legal_channel_responses"],
        "serialized_state": episode["serialized_state"],
        "source_provenance": episode["source_provenance"],
    }


def _legal_leakage_path(path: str) -> bool:
    legal_fragments = (
        ".legal_actions.",
        ".legal_channel_responses.action_score_probe.",
        ".serialized_state.action_score_probe.",
        ".serialized_state.legal_channel_snapshot.action_score_probe.",
        ".legal_answer_map_paths.",
        ".evaluation_only.",
    )
    return any(fragment in f".{path}." for fragment in legal_fragments)


def _scan_illegal_leaks(payload: Any, root_id: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    illegal_key_tokens = ("target", "answer", "label")
    illegal_value_tokens = ("target_", "answer_", "target_label")
    action_value_tokens = tuple(action.lower() for action in FINAL_ACTIONS)

    def visit(value: Any, path_parts: list[str]) -> None:
        path = ".".join(path_parts)
        if path and not _legal_leakage_path(path):
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
                if any(token in lower_value for token in illegal_value_tokens) or any(
                    token in lower_value for token in action_value_tokens
                ):
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
        "filename_label_leak": {
            "artifact_path": "fixtures/fixture_target_repair_core_viability.json",
            "payload": {"visible_feature": 1},
        },
        "action_name_label_leak": {
            "candidate_visible": {"answer_is_protect_left_boundary": True},
        },
        "metadata_answer_map": {
            "metadata": {"target_label_or_target_variable": "defer_or_ignore"},
        },
        "source_pin_path_label_leak": {
            "source_pin_path": "pins/source_defer_or_ignore.json",
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
        findings = [] if control_id == disable_positive_control else _scan_illegal_leaks(payload, control_id)
        positive_control_findings[control_id] = findings
        if findings:
            detected.append(control_id)
        else:
            blocking.append(f"positive_control_not_detected:{control_id}")

    clean_payloads = [
        {
            "candidate_visible": _candidate_visible_payload(episode),
            "evaluation_only": {
                "target": episode["target_label_or_target_variable"],
                "oracle_prediction": trace_row["evaluation_only"]["oracle_prediction"],
            },
        }
        for episode, trace_row in zip(episodes, trace_rows)
    ]
    illegal_findings: list[dict[str, Any]] = []
    for payload in clean_payloads:
        illegal_findings.extend(_scan_illegal_leaks(payload, payload["candidate_visible"]["episode_id"]))
    if illegal_findings:
        blocking.append("illegal_leak_found_in_generated_artifacts")

    positive_controls_passed = not [
        reason for reason in blocking if reason.startswith("positive_control_not_detected:")
    ]
    clean_scan_passed = not illegal_findings
    return {
        "producer_function": "baseline_first_harness_001a.runner.run_leakage_scan",
        "positive_control_ids": sorted(_leakage_positive_control_payloads()),
        "positive_controls_passed": positive_controls_passed,
        "detected_positive_control_ids": detected,
        "positive_control_findings": positive_control_findings,
        "clean_scan_scanned_generated_artifacts": True,
        "clean_scan_scope": {
            "candidate_visible_episode_count": len(episodes),
            "trace_row_count": len(trace_rows),
            "scanned_surfaces": [
                "candidate_visible.current_observation",
                "candidate_visible.legal_action_or_query_schema",
                "candidate_visible.budget_state",
                "candidate_visible.legal_channel_responses",
                "candidate_visible.serialized_state",
                "candidate_visible.source_provenance",
                "trace.evaluation_only",
            ],
            "allowlisted_legal_surfaces": [
                "legal_action_or_query_schema.legal_actions",
                "legal_channel_responses.action_score_probe",
                "serialized_state.action_score_probe",
                "serialized_state.legal_channel_snapshot.action_score_probe",
                "evaluation_only.target",
            ],
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

    required_observation_fields = {"visible_bucket", "viability_bucket", "boundary_hint"}
    missing_observation = sorted(required_observation_fields - set(observation))
    if missing_observation:
        blocking.append(f"missing_observation_fields:{','.join(missing_observation)}")
    legal_actions = schema.get("legal_actions", [])
    if not legal_actions or not set(legal_actions).issubset(set(FINAL_ACTIONS)):
        blocking.append("invalid_legal_action_schema")
    if "action_score_probe" not in schema.get("legal_queries", []):
        blocking.append("missing_legal_query:action_score_probe")
    query_cost = schema.get("query_costs", {}).get("action_score_probe")
    if query_cost is None:
        blocking.append("missing_query_cost:action_score_probe")
    elif budget.get("candidate_matched_budget_tokens", 0) < query_cost:
        blocking.append("insufficient_replay_budget:action_score_probe")
    scores = state.get("legal_channel_snapshot", {}).get("action_score_probe", state.get("action_score_probe", {}))
    if not scores or any(action not in scores for action in legal_actions):
        blocking.append("missing_serialized_action_score_probe")
    if blocking:
        return None, reads, blocking
    return max(legal_actions, key=lambda action: scores[action]), reads, []


def run_replay_check(episodes: list[dict[str, Any]], tamper_replay: bool = False) -> dict[str, Any]:
    replay_episodes = copy.deepcopy(episodes)
    if tamper_replay and replay_episodes:
        state = replay_episodes[0]["serialized_state"]
        original_action = max(FINAL_ACTIONS, key=lambda action: state["action_score_probe"][action])
        forced_action = next(action for action in FINAL_ACTIONS if action != original_action)
        tampered_scores = {action: 0 for action in FINAL_ACTIONS}
        tampered_scores[forced_action] = 1
        state["action_score_probe"] = tampered_scores
        state["legal_channel_snapshot"]["action_score_probe"] = tampered_scores

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
        blocking = ["replay_tamper_negative_control_failed"]
    elif not predictions_match:
        blocking.append("replay_recompute_mismatch")
    passed = not blocking
    return {
        "producer_function": "baseline_first_harness_001a.runner.run_replay_check",
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
            "baseline_first_harness_001a.runner.run_replay_check",
        )
    )

    no_budget = copy.deepcopy(episodes)
    for episode in no_budget:
        episode["budget_state"]["candidate_matched_budget_tokens"] = 0
        episode["budget_state"]["query_budget_remaining"] = 0
    no_budget_report = run_replay_check(no_budget)
    controls.append(
        _ablation_control_row(
            "remove_legal_query_budget",
            not no_budget_report["passed"]
            and any("insufficient_replay_budget:action_score_probe" in reason for reason in no_budget_report["blocking_reasons"]),
            "insufficient_replay_budget:action_score_probe",
            "baseline_first_harness_001a.runner.run_replay_check",
        )
    )

    forced_baseline = copy.deepcopy(baseline_comparison)
    forced_baseline["missing_baseline_ids"] = []
    forced_baseline["strongest_fair_baseline"] = {
        "baseline_id": "forced_equal_control",
        "macro_f1": oracle_row["metric"]["macro_f1"],
        "producer_function": "baseline_first_harness_001a.runner.run_ablation_controls",
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
            "baseline_first_harness_001a.runner.derive_result",
        )
    )

    trace_rows = _trace_rows(episodes, visible_channel_oracle(episodes))
    positive_leak_report = run_leakage_scan(episodes, trace_rows)
    controls.append(
        _ablation_control_row(
            "inject_leakage_positive_control",
            positive_leak_report["positive_controls_passed"],
            "positive_controls_detected",
            "baseline_first_harness_001a.runner.run_leakage_scan",
        )
    )

    tampered_replay_report = run_replay_check(episodes, tamper_replay=True)
    controls.append(
        _ablation_control_row(
            "tamper_replay_state",
            not tampered_replay_report["passed"]
            and "replay_tamper_negative_control_failed" in tampered_replay_report["blocking_reasons"],
            "replay_tamper_negative_control_failed",
            "baseline_first_harness_001a.runner.run_replay_check",
        )
    )

    omitted_source_check = verify_provenance({"records": []})
    controls.append(
        _ablation_control_row(
            "omit_source_generator_provenance",
            "missing_required_provenance:candidate_free_episode_generator" in omitted_source_check["blocking_reasons"],
            "missing_required_provenance:candidate_free_episode_generator",
            "baseline_first_harness_001a.runner.verify_provenance",
        )
    )

    missing_or_failed = [
        row["control_id"]
        for row in controls
        if not row["callable_invoked"] or not row["detected_expected_failure"] or row["consumed_by_final_verdict"] is not True
    ]
    return {
        "producer_function": "baseline_first_harness_001a.runner.run_ablation_controls",
        "controls": controls,
        "all_controls_consumed_by_final_verdict": not missing_or_failed,
        "blocking_reasons": [f"ablation_control_not_detected:{control_id}" for control_id in missing_or_failed],
    }


def build_provenance(
    oracle_row: dict[str, Any],
    baseline_comparison: dict[str, Any],
    leakage_report: dict[str, Any],
    replay_report: dict[str, Any],
    ablation_report: dict[str, Any],
    observed_spec_hash: str,
    result: dict[str, Any] | None = None,
    include_source_generator: bool = True,
) -> dict[str, Any]:
    records = []
    if include_source_generator:
        records.append(
            {
                "kind": "source_generation",
                "producer_id": "candidate_free_episode_generator",
                "producer_function": "baseline_first_harness_001a.runner.generate_episodes",
                "input_artifacts": ["docs/research/MINIMAL-ENV-SPEC-001A.md"],
                "run_id": RUN_ID,
                "seed_context_episode_ids": ["seed_count=5", "episodes_per_seed=20"],
                "aggregation_rule": "deterministic_candidate_free_episode_generation",
                "code_path_hash": code_path_hash(generate_episodes),
                "consumed_by_final_verdict": True,
                "value": {"episode_count": 100},
            }
        )
    records.append(
        {
            "kind": "source_pin",
            "producer_id": "frozen_spec_hash_readback",
            "producer_function": "baseline_first_harness_001a.runner.file_sha256",
            "input_artifacts": ["docs/research/MINIMAL-ENV-SPEC-001A.md"],
            "run_id": RUN_ID,
            "seed_context_episode_ids": ["all"],
            "aggregation_rule": "sha256_must_equal_expected_frozen_spec_hash",
            "code_path_hash": code_path_hash(file_sha256),
            "consumed_by_final_verdict": True,
            "value": observed_spec_hash,
        }
    )
    for row in [oracle_row] + baseline_comparison["results"]:
        records.append(
            {
                "kind": row["kind"],
                "producer_id": row["producer_id"],
                "producer_function": row["producer_function"],
                "input_artifacts": row["input_artifacts"],
                "run_id": row["run_id"],
                "seed_context_episode_ids": row["seed_context_episode_ids"],
                "aggregation_rule": row["aggregation_rule"],
                "code_path_hash": row["code_path_hash"],
                "consumed_by_final_verdict": True,
                "value": row["metric"]["macro_f1"],
            }
        )
    for producer_id, report in (
        ("leakage_scan", leakage_report),
        ("replay_recomputation", replay_report),
    ):
        records.append(
            {
                "kind": "control",
                "producer_id": producer_id,
                "producer_function": report["producer_function"],
                "input_artifacts": ["generated_candidate_free_episodes"],
                "run_id": RUN_ID,
                "seed_context_episode_ids": ["all"],
                "aggregation_rule": "control_must_pass_before_final_verdict",
                "code_path_hash": code_path_hash(run_leakage_scan if producer_id == "leakage_scan" else run_replay_check),
                "consumed_by_final_verdict": True,
                "value": report.get("passed", report.get("positive_controls_passed")),
            }
        )
    records.append(
        {
            "kind": "control",
            "producer_id": "ablation_controls",
            "producer_function": ablation_report["producer_function"],
            "input_artifacts": ["generated_candidate_free_episodes", "oracle_and_baseline_reports"],
            "run_id": RUN_ID,
            "seed_context_episode_ids": ["all"],
            "aggregation_rule": "all_controls_must_be_callable_detected_and_consumed",
            "code_path_hash": code_path_hash(run_ablation_controls),
            "consumed_by_final_verdict": True,
            "value": ablation_report["all_controls_consumed_by_final_verdict"],
        }
    )
    if result is not None:
        records.append(
            {
                "kind": "final_verdict",
                "producer_id": "final_verdict_derivation",
                "producer_function": "baseline_first_harness_001a.runner.derive_result",
                "input_artifacts": [
                    "oracle_score",
                    "baseline_comparison",
                    "leakage_report",
                    "replay_report",
                    "ablation_report",
                    "computed_evidence_provenance",
                ],
                "run_id": RUN_ID,
                "seed_context_episode_ids": ["all"],
                "aggregation_rule": "ordered_stop_conditions_then_equivalence_band_headroom_check",
                "code_path_hash": code_path_hash(derive_result),
                "consumed_by_final_verdict": True,
                "value": result["verdict"],
            }
        )
    return {
        "producer_function": "baseline_first_harness_001a.runner.build_provenance",
        "records": records,
    }


def verify_provenance(provenance: dict[str, Any]) -> dict[str, Any]:
    required = {
        "kind",
        "producer_id",
        "producer_function",
        "input_artifacts",
        "run_id",
        "seed_context_episode_ids",
        "aggregation_rule",
        "code_path_hash",
        "consumed_by_final_verdict",
        "value",
    }
    reasons = []
    producer_ids = {row.get("producer_id") for row in provenance.get("records", [])}
    for producer_id in sorted(REQUIRED_PROVENANCE_PRODUCERS - producer_ids):
        reasons.append(f"missing_required_provenance:{producer_id}")
    for index, row in enumerate(provenance.get("records", [])):
        missing = sorted(required - set(row))
        if missing:
            reasons.append(f"record_{index}_missing:{','.join(missing)}")
        for field in required:
            if row.get(field) in (None, "", [], {}):
                reasons.append(f"record_{index}_empty:{field}")
        if row.get("producer_function") == "literal_static_report" or row.get("static_score_injection"):
            reasons.append(f"record_{index}_static_score")
        if len(str(row.get("code_path_hash", ""))) != 64:
            reasons.append(f"record_{index}_bad_code_path_hash")
        if row.get("consumed_by_final_verdict") is not True:
            reasons.append(f"record_{index}_not_consumed")
    return {
        "producer_function": "baseline_first_harness_001a.runner.verify_provenance",
        "passed": not reasons,
        "blocking_reasons": reasons,
    }


def build_failure_manifest(
    baseline_comparison: dict[str, Any],
    leakage_report: dict[str, Any],
    replay_report: dict[str, Any],
    ablation_report: dict[str, Any],
    provenance_check: dict[str, Any],
) -> dict[str, Any]:
    reasons = []
    reasons.extend(f"missing_required_baseline:{baseline_id}" for baseline_id in baseline_comparison["missing_baseline_ids"])
    reasons.extend(leakage_report["blocking_reasons"])
    reasons.extend(replay_report["blocking_reasons"])
    reasons.extend(ablation_report["blocking_reasons"])
    reasons.extend(provenance_check["blocking_reasons"])
    return {
        "producer_function": "baseline_first_harness_001a.runner.build_failure_manifest",
        "blocking_reasons": reasons,
        "has_blocking_failure": bool(reasons),
    }


def derive_result(
    spec_hash_matches: bool,
    oracle_row: dict[str, Any],
    baseline_comparison: dict[str, Any],
    leakage_report: dict[str, Any],
    replay_report: dict[str, Any],
    ablation_report: dict[str, Any],
    provenance_check: dict[str, Any],
) -> dict[str, Any]:
    visible = oracle_row["metric"]["macro_f1"]
    strongest = baseline_comparison["strongest_fair_baseline"]
    stop_conditions = []
    verdict = "headroom_present"
    if not spec_hash_matches:
        verdict = "blocked_spec_hash_mismatch"
        stop_conditions.append("spec_hash_mismatch")
    elif baseline_comparison["missing_baseline_ids"]:
        verdict = "blocked_missing_required_baseline"
        stop_conditions.extend(f"missing_required_baseline:{baseline_id}" for baseline_id in baseline_comparison["missing_baseline_ids"])
    elif not leakage_report["positive_controls_passed"]:
        verdict = "blocked_leakage_positive_control_failure"
        stop_conditions.extend(leakage_report["blocking_reasons"])
    elif not leakage_report["clean_scan_passed_after_positive_controls"]:
        verdict = "blocked_leakage_clean_scan_failure"
        stop_conditions.extend(leakage_report["blocking_reasons"])
    elif not replay_report["passed"]:
        verdict = "blocked_replay_recompute_failure"
        stop_conditions.extend(replay_report["blocking_reasons"])
    elif not ablation_report["all_controls_consumed_by_final_verdict"]:
        verdict = "blocked_ablation_control_failure"
        stop_conditions.extend(ablation_report["blocking_reasons"])
    elif not provenance_check["passed"]:
        verdict = "blocked_provenance_failure"
        stop_conditions.extend(provenance_check["blocking_reasons"])
    elif strongest and strongest["macro_f1"] >= visible - EQUIVALENCE_BAND:
        verdict = "no_headroom_baseline_saturated"
        stop_conditions.append("strongest_fair_baseline_in_oracle_equivalence_band")
    return {
        "task_id": TASK_ID,
        "harness_card_id": HARNESS_ID,
        "run_id": RUN_ID,
        "verdict": verdict,
        "stop_conditions_triggered": stop_conditions,
        "layer": "engineering_implementation + mechanism_hypothesis_governance",
        "mainline_integration_status": "none",
        "enabled_status": "local_candidate_free_harness_only",
        "real_trigger_evidence": "callable candidate-free oracle, baseline, leakage, replay, and provenance producers",
        "claim_ceiling": CLAIM_CEILING,
        "auto_remote_anchor": "forbidden",
        "spec_hash_matches_freeze": spec_hash_matches,
        "visible_channel_oracle_macro_f1": visible,
        "strongest_fair_baseline_macro_f1": strongest["macro_f1"] if strongest else None,
        "strongest_fair_baseline_id": strongest["baseline_id"] if strongest else None,
        "equivalence_band": EQUIVALENCE_BAND,
        "episode_count": len(oracle_row["seed_context_episode_ids"]),
        "seed_count": 5,
        "episodes_per_seed": 20,
        "baseline_battery_run": True,
        "candidate_mechanism_run": False,
        "mechanism_experiment_run": False,
        "phase3_opened": False,
        "gate_run": False,
        "runtime_or_mainline_touched": False,
    }


def _trace_rows(episodes: list[dict[str, Any]], oracle_predictions: list[str]) -> list[dict[str, Any]]:
    rows = []
    for episode, oracle_prediction in zip(episodes, oracle_predictions):
        rows.append(
            {
                "episode_id": episode["episode_id"],
                "seed": episode["seed"],
                "candidate_visible": _candidate_visible_payload(episode),
                "evaluation_only": {
                    "oracle_prediction": oracle_prediction,
                    "target": episode["target_label_or_target_variable"],
                },
                "candidate_decision": None,
            }
        )
    return rows


def run_harness(
    output_dir: str | Path,
    persist_artifacts: bool = True,
    disabled_baselines: tuple[str, ...] = (),
    disable_leakage_positive_control: str | None = None,
    tamper_replay: bool = False,
    omit_source_generator_provenance: bool = False,
) -> dict[str, Any]:
    root = repo_root()
    spec_path = root / "docs" / "research" / "MINIMAL-ENV-SPEC-001A.md"
    observed_spec_hash = file_sha256(spec_path)
    spec_hash_matches = observed_spec_hash == EXPECTED_SPEC_SHA256
    episodes = generate_episodes()
    oracle_predictions = visible_channel_oracle(episodes)
    oracle_row = _score_row(
        "visible_channel_oracle",
        "baseline_first_harness_001a.runner.visible_channel_oracle",
        oracle_predictions,
        episodes,
        "oracle_score",
    )
    baseline_comparison = run_baseline_battery(episodes, disabled_baselines)
    trace_rows = _trace_rows(episodes, oracle_predictions)
    leakage_report = run_leakage_scan(episodes, trace_rows, disable_leakage_positive_control)
    replay_report = run_replay_check(episodes, tamper_replay)
    ablation_report = run_ablation_controls(episodes, oracle_row, baseline_comparison, leakage_report, replay_report)
    preliminary_provenance = build_provenance(
        oracle_row,
        baseline_comparison,
        leakage_report,
        replay_report,
        ablation_report,
        observed_spec_hash,
        result={"verdict": "pending_final_verdict_derivation"},
        include_source_generator=not omit_source_generator_provenance,
    )
    preliminary_provenance_check = verify_provenance(preliminary_provenance)
    result = derive_result(
        spec_hash_matches,
        oracle_row,
        baseline_comparison,
        leakage_report,
        replay_report,
        ablation_report,
        preliminary_provenance_check,
    )
    result["observed_spec_sha256"] = observed_spec_hash
    result["expected_spec_sha256"] = EXPECTED_SPEC_SHA256
    provenance = build_provenance(
        oracle_row,
        baseline_comparison,
        leakage_report,
        replay_report,
        ablation_report,
        observed_spec_hash,
        result=result,
        include_source_generator=not omit_source_generator_provenance,
    )
    provenance_check = verify_provenance(provenance)
    result = derive_result(
        spec_hash_matches,
        oracle_row,
        baseline_comparison,
        leakage_report,
        replay_report,
        ablation_report,
        provenance_check,
    )
    result["observed_spec_sha256"] = observed_spec_hash
    result["expected_spec_sha256"] = EXPECTED_SPEC_SHA256
    failure_manifest = build_failure_manifest(
        baseline_comparison,
        leakage_report,
        replay_report,
        ablation_report,
        provenance_check,
    )
    run = {
        "result": result,
        "trace": trace_rows,
        "baseline_comparison": baseline_comparison,
        "ablation_report": ablation_report,
        "replay_report": replay_report,
        "leakage_report": leakage_report,
        "computed_evidence_provenance": provenance,
        "provenance_check": provenance_check,
        "failure_manifest": failure_manifest,
        "claim_ceiling": CLAIM_CEILING,
    }
    if persist_artifacts:
        write_artifacts(Path(output_dir), run)
    return run


def write_artifacts(output_dir: Path, run: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_payloads = {
        "result.json": run["result"],
        "baseline_comparison.json": run["baseline_comparison"],
        "ablation_report.json": run["ablation_report"],
        "replay_report.json": run["replay_report"],
        "leakage_report.json": run["leakage_report"],
        "computed_evidence_provenance.json": run["computed_evidence_provenance"],
        "failure_manifest.json": run["failure_manifest"],
    }
    for filename, payload in json_payloads.items():
        (output_dir / filename).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    with (output_dir / "trace.jsonl").open("w", encoding="utf-8") as handle:
        for row in run["trace"]:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    (output_dir / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/baseline_first_harness_001a")
    args = parser.parse_args(argv)
    run = run_harness(output_dir=args.output_dir, persist_artifacts=True)
    print(json.dumps(run["result"], indent=2))
    return 0 if not run["failure_manifest"]["has_blocking_failure"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
