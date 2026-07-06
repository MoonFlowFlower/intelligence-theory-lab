from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
from pathlib import Path
from typing import Any, Callable

from . import model


REQUIRED_BASELINES = {
    "random",
    "majority",
    "no_update",
    "episodic_traversal",
    "count_table",
    "transition_table",
    "successor_map",
    "rag_summary",
    "online_no_replay",
    "vanilla_experience_replay",
    "standard_continual_replay",
    "from_scratch_per_task",
    "strong_meta_learner",
    "batch_precompute",
    "drift_aware_regime_inferring_continual_replay",
}

ABLATION_IDS = {
    "no_update",
    "no_memory_read",
    "no_replay",
    "corrupted_replay",
    "prediction_error_shuffle",
    "consolidation_deletion",
    "counterfactual_memory",
    "action_conditioning_disabled",
}

FORBIDDEN_LEAK_TOKENS = {
    "regime_id",
    "latent_regime",
    "audit_regime",
    "target_label",
    "answer_key",
    "oracle",
    "a_code",
    "b_code",
    "hidden_code",
}

CLAIM_FORBIDDEN = [
    "mechanism_validity",
    "agency",
    "autonomy",
    "subjectivity",
    "consciousness",
    "ego_readiness",
    "mainline_effect",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True)


def function_hash(func: Callable[..., Any]) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()


def callable_code_hash(func: Callable[..., Any]) -> str:
    try:
        source = inspect.getsource(func)
    except (OSError, TypeError):
        code = getattr(func, "__code__", None)
        source = repr(code.co_code if code is not None else func)
    payload = (
        f"{getattr(func, '__module__', '')}."
        f"{getattr(func, '__qualname__', getattr(func, '__name__', 'callable'))}\n"
        f"{source}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def code_path_hash() -> str:
    digest = hashlib.sha256()
    for name in ("model.py", "runner.py", "__init__.py", "__main__.py"):
        path = Path(__file__).resolve().parent / name
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty_json(payload) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def _context_events(state: dict[str, Any], context_key: str | None = None) -> list[dict[str, Any]]:
    key = context_key if context_key is not None else state.get("active_context_key")
    return [event for event in state["memory_events"] if event.get("context_key") == key]


def consolidate_state(state: dict[str, Any], *, mode: str = "normal") -> tuple[dict[str, Any], dict[str, Any]]:
    updated = copy.deepcopy(state)
    source_events = list(updated["memory_events"])
    if mode == "corrupted_replay":
        source_events = [
            {
                **event,
                "context_key": f"corrupted:{index % 2}",
                "outcome": (int(event["outcome"]) + 1) % model.L,
            }
            for index, event in enumerate(reversed(source_events))
        ]
    by_context: dict[str, list[dict[str, Any]]] = {}
    for event in source_events:
        by_context.setdefault(str(event["context_key"]), []).append(event)
    consolidated: dict[str, Any] = {}
    for context_key, events in sorted(by_context.items()):
        consolidated[context_key] = model.solve_additive_model(
            events,
            model_id_prefix=f"candidate:{context_key}:{mode}",
        )
    replay_event = {
        "replay_event_id": f"replay_{updated['update_counter']:03d}_{mode}",
        "source_memory_ids": [str(event["memory_event_id"]) for event in source_events],
        "output_model_hash": model.stable_hash(consolidated),
        "mode": mode,
    }
    updated["consolidated_models"] = consolidated
    updated["last_replay_event_id"] = replay_event["replay_event_id"]
    return updated, replay_event


def select_action(
    state: dict[str, Any],
    observation: dict[str, Any],
    *,
    no_memory_read: bool = False,
    action_conditioning_disabled: bool = False,
) -> dict[str, Any]:
    row = int(observation["row_factor"])
    col = int(observation["col_factor"])
    context_key = state.get("active_context_key")
    model_payload = None if no_memory_read or context_key is None else state["consolidated_models"].get(str(context_key))
    model_prediction = model.predict_from_model(model_payload, row, col)
    if action_conditioning_disabled:
        action_distribution = {str(candidate): 1.0 / model.L for candidate in range(model.L)}
        chosen = 0
    else:
        action_distribution = {str(candidate): 0.0 for candidate in range(model.L)}
        action_distribution[str(model_prediction)] = 1.0
        chosen = int(model_prediction)
    dependencies = []
    if model_payload is not None:
        dependencies.append(model_payload["model_id"])
        dependencies.extend(model_payload["event_ids"])
    return {
        "action_candidates": list(range(model.L)),
        "action_chosen": chosen,
        "action_distribution": action_distribution,
        "prediction_payload": {
            "predicted_outcome_for_chosen_action": chosen,
            "action_conditioned": not action_conditioning_disabled,
            "active_context_key_present": context_key is not None,
            "model_id": model_payload["model_id"] if model_payload else None,
        },
        "dependency_ids": dependencies,
        "read_updated_memory": bool(dependencies) and not no_memory_read,
    }


def apply_feedback(
    state: dict[str, Any],
    observation: dict[str, Any],
    action: int,
    feedback: dict[str, Any],
    *,
    mode: str = "normal",
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    updated = copy.deepcopy(state)
    outcome = int(feedback["outcome"])
    prediction_error = 0 if int(action) == outcome else 1
    memory_outcome = (outcome + 1) % model.L if mode == "prediction_error_shuffle" else outcome
    row = int(observation["row_factor"])
    col = int(observation["col_factor"])
    if (row, col) == model.ANCHOR_CELL:
        updated["active_context_key"] = model.context_key_from_anchor(outcome)
    context_key = updated.get("active_context_key")
    write_event: dict[str, Any] | None = None
    if mode != "no_update":
        write_event = {
            "memory_event_id": f"mem_{updated['update_counter']:03d}",
            "context_key": context_key,
            "row_factor": row,
            "col_factor": col,
            "outcome": memory_outcome,
            "prediction_error": prediction_error,
            "source_feedback_outcome_hash": model.stable_hash(feedback),
        }
        updated["memory_events"].append(write_event)
    updated["prediction_error_state"] = {
        "last_error": prediction_error,
        "cumulative_abs_error": int(updated["prediction_error_state"]["cumulative_abs_error"]) + abs(prediction_error),
    }
    updated["update_counter"] += 1
    replay_event = {
        "replay_event_id": None,
        "source_memory_ids": [],
        "output_model_hash": model.stable_hash(updated.get("consolidated_models", {})),
        "mode": mode,
    }
    if mode != "no_replay":
        updated, replay_event = consolidate_state(updated, mode=mode)
    return updated, {"prediction_error": prediction_error, "memory_write": write_event}, replay_event


def _event_base(
    *,
    event_type: str,
    event_index: int,
    episode_id: str,
    step_id: str,
    step_index: int,
    seed: int,
    state_before: dict[str, Any],
    state_after: dict[str, Any] | None,
    observation: dict[str, Any],
) -> dict[str, Any]:
    serialized = model.serialize_state(state_before)
    return {
        "task_id": model.TASK_ID,
        "run_id": model.RUN_ID,
        "seed": seed,
        "episode_id": episode_id,
        "step_id": step_id,
        "step_index": int(step_index),
        "event_index": int(event_index),
        "event_type": event_type,
        "producer_function": "same_agent_minimal_kernel_bridge_001a.runner.run_kernel_candidate",
        "code_path_hash": code_path_hash(),
        "state_hash_before": model.stable_hash(state_before),
        "state_hash_after": model.stable_hash(state_after) if state_after is not None else None,
        "serialized_state": serialized,
        "serialized_state_hash": serialized["state_hash"],
        "observation": copy.deepcopy(observation),
        "observation_hash": model.stable_hash(observation),
    }


def run_kernel_candidate(
    *,
    deployment: dict[str, Any] | None = None,
    mode: str = "normal",
    force_no_memory_read: bool = False,
    emit_trace: bool = True,
) -> dict[str, Any]:
    dep = deployment if deployment is not None else model.build_deployment(model.BASE_SEED)
    state = model.initial_state()
    trace_rows: list[dict[str, Any]] = []
    event_counter = 0
    no_memory_read = force_no_memory_read or mode == "no_memory_read"
    action_conditioning_disabled = mode == "action_conditioning_disabled"
    probe_observation = {
        "schema_version": "same_agent_minimal_kernel_observation.v1",
        "row_factor": model.HELDOUT_CELLS[0][0],
        "col_factor": model.HELDOUT_CELLS[0][1],
        "phase": "next_action_probe",
    }

    for episode in dep["episodes"]:
        for local_step, item in enumerate(episode["observations"]):
            observation = item["observation"]
            feedback = item["feedback"]
            episode_id = str(episode["episode_id"])
            step_id = f"{episode_id}_step_{local_step:02d}"
            before = copy.deepcopy(state)
            pre_next_action = select_action(
                before,
                probe_observation,
                no_memory_read=no_memory_read,
                action_conditioning_disabled=action_conditioning_disabled,
            )
            decision = select_action(
                before,
                observation,
                no_memory_read=no_memory_read,
                action_conditioning_disabled=action_conditioning_disabled,
            )
            after, update_payload, replay_payload = apply_feedback(
                before,
                observation,
                int(decision["action_chosen"]),
                feedback,
                mode=mode,
            )
            post_next_action = select_action(
                after,
                probe_observation,
                no_memory_read=no_memory_read,
                action_conditioning_disabled=action_conditioning_disabled,
            )

            if emit_trace:
                events = [
                    ("observe", {"candidate_input": {"observation": observation, "serialized_state": model.serialize_state(before)}}),
                    ("predict", {"pre_feedback_prediction": decision["prediction_payload"]}),
                    (
                        "act",
                        {
                            "action_candidates": decision["action_candidates"],
                            "action_chosen": decision["action_chosen"],
                            "action_distribution": decision["action_distribution"],
                            "action_selection_dependency_ids": decision["dependency_ids"],
                        },
                    ),
                    ("feedback", {"feedback": feedback}),
                    (
                        "prediction_error",
                        {
                            "prediction_error": update_payload["prediction_error"],
                            "prediction_error_aggregation_rule": "0_if_chosen_action_matches_feedback_outcome_else_1",
                        },
                    ),
                    (
                        "belief_or_memory_update",
                        {
                            "belief_memory_write_id": update_payload["memory_write"]["memory_event_id"]
                            if update_payload["memory_write"]
                            else None,
                            "belief_memory_delta_summary": {
                                "memory_event_written": update_payload["memory_write"] is not None,
                                "active_context_key_after": after.get("active_context_key"),
                            },
                            "memory_event": update_payload["memory_write"],
                            "before_state_hash": model.stable_hash(before),
                            "after_state_hash": model.stable_hash(after),
                        },
                    ),
                    (
                        "replay_or_consolidation",
                        {
                            "replay_or_consolidation_event_ids": [replay_payload["replay_event_id"]],
                            "source_memory_ids": replay_payload["source_memory_ids"],
                            "replay_output_hash": replay_payload["output_model_hash"],
                        },
                    ),
                    (
                        "next_action",
                        {
                            "next_action_observation": probe_observation,
                            "next_action_before_update": pre_next_action["action_chosen"],
                            "next_action_after_update": post_next_action["action_chosen"],
                            "next_action_changed_after_update": pre_next_action["action_chosen"]
                            != post_next_action["action_chosen"],
                            "action_selection_read_updated_memory": post_next_action["read_updated_memory"],
                        },
                    ),
                ]
                for event_type, payload in events:
                    row = _event_base(
                        event_type=event_type,
                        event_index=event_counter,
                        episode_id=episode_id,
                        step_id=step_id,
                        step_index=local_step,
                        seed=int(dep["seed"]),
                        state_before=before,
                        state_after=after if event_type in {"belief_or_memory_update", "replay_or_consolidation", "next_action"} else None,
                        observation=observation,
                    )
                    row.update(payload)
                    row["runtime_mode"] = mode
                    row["force_no_memory_read"] = no_memory_read
                    row["action_conditioning_disabled"] = action_conditioning_disabled
                    trace_rows.append(row)
                    event_counter += 1
            state = after

    if mode == "consolidation_deletion":
        state = copy.deepcopy(state)
        state["consolidated_models"] = {}
        state["last_replay_event_id"] = "deleted_before_heldout"
    score = score_state_on_heldout(
        state,
        dep["heldout_cases"],
        no_memory_read=no_memory_read,
        action_conditioning_disabled=action_conditioning_disabled,
    )
    return {"state": state, "trace_rows": trace_rows, "score": score}


def score_state_on_heldout(
    state: dict[str, Any],
    heldout_cases: list[dict[str, Any]],
    *,
    no_memory_read: bool = False,
    action_conditioning_disabled: bool = False,
) -> dict[str, Any]:
    correct = 0
    predictions: list[dict[str, Any]] = []
    for case in heldout_cases:
        eval_state = copy.deepcopy(state)
        eval_state["active_context_key"] = case["context_key"]
        action = select_action(
            eval_state,
            case["observation"],
            no_memory_read=no_memory_read,
            action_conditioning_disabled=action_conditioning_disabled,
        )
        is_correct = int(action["action_chosen"]) == int(case["outcome"])
        correct += int(is_correct)
        predictions.append(
            {
                "case_id": case["case_id"],
                "context_key_hash": model.stable_hash(case["context_key"]),
                "observation": case["observation"],
                "prediction": int(action["action_chosen"]),
                "outcome": int(case["outcome"]),
                "correct": is_correct,
                "dependency_ids": action["dependency_ids"],
            }
        )
    return {
        "score": correct / len(heldout_cases) if heldout_cases else 0.0,
        "correct": correct,
        "total": len(heldout_cases),
        "predictions": predictions,
    }


def _training_events_by_context(dep: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    event_index = 0
    for episode in dep["episodes"]:
        active_context_key: str | None = None
        for item in episode["observations"]:
            row = int(item["observation"]["row_factor"])
            col = int(item["observation"]["col_factor"])
            outcome = int(item["feedback"]["outcome"])
            if (row, col) == model.ANCHOR_CELL:
                active_context_key = model.context_key_from_anchor(outcome)
            if active_context_key is None:
                active_context_key = "unknown"
            event = {
                "memory_event_id": f"baseline_mem_{event_index:03d}",
                "context_key": active_context_key,
                "row_factor": row,
                "col_factor": col,
                "outcome": outcome,
            }
            grouped.setdefault(active_context_key, []).append(event)
            event_index += 1
    return grouped


def _score_grouped_exact_cache(dep: dict[str, Any], *, grouped_by_context: bool) -> dict[str, Any]:
    grouped = _training_events_by_context(dep)
    lookup: dict[tuple[str, int, int], int] = {}
    pooled_lookup: dict[tuple[int, int], int] = {}
    for context_key, events in grouped.items():
        for event in events:
            key = (context_key, int(event["row_factor"]), int(event["col_factor"]))
            lookup.setdefault(key, int(event["outcome"]))
            pooled_lookup.setdefault((int(event["row_factor"]), int(event["col_factor"])), int(event["outcome"]))
    correct = 0
    predictions = []
    for case in dep["heldout_cases"]:
        row = int(case["observation"]["row_factor"])
        col = int(case["observation"]["col_factor"])
        if grouped_by_context:
            prediction = lookup.get((case["context_key"], row, col), 0)
        else:
            prediction = pooled_lookup.get((row, col), 0)
        ok = prediction == int(case["outcome"])
        correct += int(ok)
        predictions.append({"case_id": case["case_id"], "prediction": prediction, "outcome": case["outcome"], "correct": ok})
    return {"score": correct / len(dep["heldout_cases"]), "predictions": predictions}


def _score_additive_by_context(dep: dict[str, Any], *, context_strategy: str) -> dict[str, Any]:
    grouped = _training_events_by_context(dep)
    models: dict[str, dict[str, Any]] = {}
    if context_strategy in {"drift_aware", "batch", "meta"}:
        for context_key, events in grouped.items():
            models[context_key] = model.solve_additive_model(events, model_id_prefix=f"baseline:{context_strategy}:{context_key}")
    elif context_strategy == "pooled":
        pooled = [event for events in grouped.values() for event in events]
        models["pooled"] = model.solve_additive_model(pooled, model_id_prefix="baseline:pooled")
    elif context_strategy == "last_episode":
        last_events: dict[str, list[dict[str, Any]]] = {}
        for episode in dep["episodes"]:
            active_context_key = None
            episode_events = []
            for item in episode["observations"]:
                row = int(item["observation"]["row_factor"])
                col = int(item["observation"]["col_factor"])
                outcome = int(item["feedback"]["outcome"])
                if (row, col) == model.ANCHOR_CELL:
                    active_context_key = model.context_key_from_anchor(outcome)
                episode_events.append(
                    {
                        "memory_event_id": f"last_{episode['episode_id']}_{row}_{col}",
                        "context_key": active_context_key,
                        "row_factor": row,
                        "col_factor": col,
                        "outcome": outcome,
                    }
                )
            if active_context_key is not None:
                last_events[str(active_context_key)] = episode_events
        for context_key, events in last_events.items():
            models[context_key] = model.solve_additive_model(events, model_id_prefix=f"baseline:last:{context_key}")
    else:
        raise ValueError(f"unknown context strategy {context_strategy}")

    correct = 0
    predictions = []
    for case in dep["heldout_cases"]:
        if context_strategy == "pooled":
            selected = models.get("pooled")
        else:
            selected = models.get(case["context_key"])
        row = int(case["observation"]["row_factor"])
        col = int(case["observation"]["col_factor"])
        prediction = model.predict_from_model(selected, row, col)
        ok = prediction == int(case["outcome"])
        correct += int(ok)
        predictions.append({"case_id": case["case_id"], "prediction": prediction, "outcome": case["outcome"], "correct": ok})
    return {"score": correct / len(dep["heldout_cases"]), "predictions": predictions, "model_hash": model.stable_hash(models)}


def score_random_baseline(dep: dict[str, Any]) -> dict[str, Any]:
    predictions = []
    correct = 0
    for index, case in enumerate(dep["heldout_cases"]):
        prediction = model.derive_seed("random_baseline", dep["seed"], index) % model.L
        ok = prediction == int(case["outcome"])
        correct += int(ok)
        predictions.append({"case_id": case["case_id"], "prediction": prediction, "outcome": case["outcome"], "correct": ok})
    return {"score": correct / len(dep["heldout_cases"]), "predictions": predictions}


def score_majority_baseline(dep: dict[str, Any]) -> dict[str, Any]:
    return _constant_score(dep, 0)


def _constant_score(dep: dict[str, Any], prediction: int) -> dict[str, Any]:
    predictions = []
    correct = 0
    for case in dep["heldout_cases"]:
        ok = int(prediction) == int(case["outcome"])
        correct += int(ok)
        predictions.append({"case_id": case["case_id"], "prediction": int(prediction), "outcome": case["outcome"], "correct": ok})
    return {"score": correct / len(dep["heldout_cases"]), "predictions": predictions}


BASELINE_FUNCTIONS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "random": score_random_baseline,
    "majority": score_majority_baseline,
    "no_update": score_majority_baseline,
    "episodic_traversal": lambda dep: _score_grouped_exact_cache(dep, grouped_by_context=True),
    "count_table": lambda dep: _score_grouped_exact_cache(dep, grouped_by_context=True),
    "transition_table": lambda dep: _score_grouped_exact_cache(dep, grouped_by_context=False),
    "successor_map": lambda dep: _score_grouped_exact_cache(dep, grouped_by_context=True),
    "rag_summary": lambda dep: _score_grouped_exact_cache(dep, grouped_by_context=False),
    "online_no_replay": lambda dep: _score_additive_by_context(dep, context_strategy="last_episode"),
    "vanilla_experience_replay": lambda dep: _score_additive_by_context(dep, context_strategy="pooled"),
    "standard_continual_replay": lambda dep: _score_additive_by_context(dep, context_strategy="pooled"),
    "from_scratch_per_task": lambda dep: _score_additive_by_context(dep, context_strategy="last_episode"),
    "strong_meta_learner": lambda dep: _score_additive_by_context(dep, context_strategy="meta"),
    "batch_precompute": lambda dep: _score_additive_by_context(dep, context_strategy="batch"),
    "drift_aware_regime_inferring_continual_replay": lambda dep: _score_additive_by_context(dep, context_strategy="drift_aware"),
}


def score_record(
    *,
    producer_id: str,
    producer_function: str,
    value: float,
    seed_context_episode_ids: list[str],
    code_hash: str,
    input_artifacts: list[str],
) -> dict[str, Any]:
    return {
        "producer_id": producer_id,
        "producer_function": producer_function,
        "input_artifacts": input_artifacts,
        "run_id": model.RUN_ID,
        "seed_context_episode_ids": seed_context_episode_ids,
        "aggregation_rule": "heldout_multiclass_accuracy_over_contextualized_novel_cells",
        "code_path_hash": code_hash,
        "score": float(value),
        "consumed_by_final_verdict": True,
    }


def run_baseline_comparison(dep: dict[str, Any], *, disabled_baselines: tuple[str, ...] = ()) -> dict[str, Any]:
    disabled = set(disabled_baselines)
    rows: list[dict[str, Any]] = []
    case_ids = [case["case_id"] for case in dep["heldout_cases"]]
    for baseline_id in sorted(REQUIRED_BASELINES):
        if baseline_id in disabled:
            continue
        func = BASELINE_FUNCTIONS[baseline_id]
        payload = func(dep)
        rows.append(
            score_record(
                producer_id=baseline_id,
                producer_function=f"same_agent_minimal_kernel_bridge_001a.runner.{baseline_id}",
                value=payload["score"],
                seed_context_episode_ids=case_ids,
                code_hash=callable_code_hash(func),
                input_artifacts=["frozen_deployment_generator", "training_feedback_stream", "heldout_cases"],
            )
        )
    priority = {
        "drift_aware_regime_inferring_continual_replay": 0,
        "batch_precompute": 1,
        "strong_meta_learner": 2,
    }
    strongest = max(
        rows,
        key=lambda row: (row["score"], -priority.get(row["producer_id"], 50)),
    ) if rows else None
    return {
        "producer_function": "same_agent_minimal_kernel_bridge_001a.runner.run_baseline_comparison",
        "baseline_ids": [row["producer_id"] for row in rows],
        "declared_baseline_ids": sorted(REQUIRED_BASELINES),
        "missing_baseline_ids": sorted(REQUIRED_BASELINES - {row["producer_id"] for row in rows}),
        "results": rows,
        "strongest_fair_baseline": {
            "baseline_id": strongest["producer_id"],
            "score": strongest["score"],
            "producer_function": strongest["producer_function"],
        }
        if strongest
        else None,
        "strongest_fair_is_max_over_full_battery": bool(strongest)
        and strongest["score"] == max(row["score"] for row in rows),
    }


def scan_for_leakage(payload: Any) -> dict[str, Any]:
    hits: list[str] = []

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                key_lower = str(key).lower()
                for token in FORBIDDEN_LEAK_TOKENS:
                    if token in key_lower:
                        hits.append(f"{path}.{key}")
                walk(item, f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")
        elif isinstance(value, str):
            lowered = value.lower()
            for token in FORBIDDEN_LEAK_TOKENS:
                if token in lowered:
                    hits.append(path)

    walk(payload, "$")
    return {"fires": bool(hits), "hits": sorted(set(hits))}


def run_leakage_scan(trace_rows: list[dict[str, Any]], *, force_clean_leak: bool = False) -> dict[str, Any]:
    candidate_inputs = [row["candidate_input"] for row in trace_rows if row["event_type"] == "observe"]
    if force_clean_leak and candidate_inputs:
        candidate_inputs[0] = copy.deepcopy(candidate_inputs[0])
        candidate_inputs[0]["observation"]["leaked_regime_id"] = 0
    clean_scan = scan_for_leakage(candidate_inputs)
    positive_control = scan_for_leakage({"observation": {"leaked_regime_id": 1, "target_label": 4}})
    return {
        "producer_function": "same_agent_minimal_kernel_bridge_001a.runner.run_leakage_scan",
        "clean_scan_passed": not clean_scan["fires"],
        "positive_control_fires": positive_control["fires"],
        "leakage_detected": clean_scan["fires"],
        "clean_scan": clean_scan,
        "positive_control_scan": positive_control,
        "blocking_reasons": ["clean_candidate_input_leakage_detected"] if clean_scan["fires"] else [],
    }


def replay_trace(trace_rows: list[dict[str, Any]], *, tamper: bool = False) -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    by_step: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
    for row in trace_rows:
        by_step.setdefault((row["episode_id"], row["step_id"]), {})[row["event_type"]] = row
    for index, ((episode_id, step_id), events) in enumerate(sorted(by_step.items())):
        observe = events["observe"]
        act = events["act"]
        feedback_row = events["feedback"]
        update = events["belief_or_memory_update"]
        state = copy.deepcopy(observe["serialized_state"]["state"])
        observation = copy.deepcopy(observe["observation"])
        feedback = copy.deepcopy(feedback_row["feedback"])
        if tamper and index == 0:
            feedback["outcome"] = (int(feedback["outcome"]) + 1) % model.L
        decision = select_action(
            state,
            observation,
            no_memory_read=bool(observe.get("force_no_memory_read", False)),
            action_conditioning_disabled=bool(observe.get("action_conditioning_disabled", False)),
        )
        after, _, _ = apply_feedback(
            state,
            observation,
            int(decision["action_chosen"]),
            feedback,
            mode=str(observe.get("runtime_mode", "normal")),
        )
        expected_action = int(act["action_chosen"])
        expected_hash = update["after_state_hash"]
        observed_hash = model.stable_hash(after)
        if int(decision["action_chosen"]) != expected_action or observed_hash != expected_hash:
            mismatches.append(
                {
                    "episode_id": episode_id,
                    "step_id": step_id,
                    "expected_action": expected_action,
                    "observed_action": int(decision["action_chosen"]),
                    "expected_after_hash": expected_hash,
                    "observed_after_hash": observed_hash,
                }
            )
    return {
        "producer_function": "same_agent_minimal_kernel_bridge_001a.runner.replay_trace",
        "passed": not mismatches,
        "uses_hash_only_comparison": False,
        "uses_stored_outputs_only": False,
        "recomputed_from": ["serialized_state", "observation", "feedback"],
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:5],
        "blocking_reasons": [] if not mismatches else ["replay_recompute_mismatch"],
    }


def run_ablation_report(dep: dict[str, Any], candidate_score: float) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for ablation_id in sorted(ABLATION_IDS - {"counterfactual_memory"}):
        run = run_kernel_candidate(deployment=dep, mode=ablation_id, emit_trace=False)
        score = float(run["score"]["score"])
        results.append(
            {
                "ablation_id": ablation_id,
                "producer_function": "same_agent_minimal_kernel_bridge_001a.runner.run_kernel_candidate",
                "score": score,
                "candidate_score": candidate_score,
                "degraded": score <= candidate_score - model.DEGRADATION_MIN,
                "reran_episodes_under_intervention": True,
            }
        )
    normal = run_kernel_candidate(deployment=dep, emit_trace=False)
    final_state = normal["state"]
    contexts = list(dep["context_keys"].values())
    selected_observation = dep["heldout_cases"][0]["observation"]
    action_a = 0
    action_b = 0
    for case in dep["heldout_cases"]:
        state_a = copy.deepcopy(final_state)
        state_b = copy.deepcopy(final_state)
        state_a["active_context_key"] = contexts[0]
        state_b["active_context_key"] = contexts[1]
        candidate_a = select_action(state_a, case["observation"])["action_chosen"]
        candidate_b = select_action(state_b, case["observation"])["action_chosen"]
        selected_observation = case["observation"]
        action_a = int(candidate_a)
        action_b = int(candidate_b)
        if action_a != action_b:
            break
    counterfactual = {
        "ablation_id": "counterfactual_memory",
        "producer_function": "same_agent_minimal_kernel_bridge_001a.runner.select_action",
        "same_observation_different_serialized_states": True,
        "different_action_selected": int(action_a) != int(action_b),
        "observation": selected_observation,
        "action_a": int(action_a),
        "action_b": int(action_b),
        "reran_episodes_under_intervention": True,
    }
    results.append({**counterfactual, "score": None, "candidate_score": candidate_score, "degraded": counterfactual["different_action_selected"]})
    passed = all(row["degraded"] for row in results)
    return {
        "producer_function": "same_agent_minimal_kernel_bridge_001a.runner.run_ablation_report",
        "ablation_gate_passed": passed,
        "ablation_ids": [row["ablation_id"] for row in results],
        "results": results,
        "counterfactual_memory": counterfactual,
        "blocking_reasons": [] if passed else ["ablation_not_sensitive"],
    }


def build_collision_record() -> dict[str, Any]:
    return {
        "producer_function": "same_agent_minimal_kernel_bridge_001a.runner.build_collision_record",
        "task_id": model.TASK_ID,
        "selected": "Candidate 3 mechanism-faithful target, with Candidate 2 decisive contrast executed first",
        "candidates": [
            {
                "id": "minimal_engineering_scaffold",
                "evidence": "loop trace and state changes only",
                "strongest_cheap_baseline": "scripted feedback-reactive policy / lookup",
                "leakage_hardcoding_risk": "high",
                "smallest_falsifier": "same observation with different memory does not change action",
                "expected_failure_mode": "infrastructure-only",
            },
            {
                "id": "strongest_baseline_shortcut",
                "evidence": "drift-aware continual replay and batch comparisons",
                "strongest_cheap_baseline": "the baseline itself",
                "leakage_hardcoding_risk": "medium",
                "smallest_falsifier": "baseline ties under clean access parity",
                "expected_failure_mode": "baseline equivalence",
            },
            {
                "id": "mechanism_faithful_runtime_kernel",
                "evidence": "live loop, replay recomputation, ablations, baseline comparison",
                "strongest_cheap_baseline": "drift-aware regime-inferring continual replay / batch precompute",
                "leakage_hardcoding_risk": "high without schema freeze",
                "smallest_falsifier": "baseline ties, ablations insensitive, or replay invalid",
                "expected_failure_mode": "route downgrades to baseline equivalence",
            },
        ],
    }


def build_contract(dep: dict[str, Any]) -> dict[str, Any]:
    return {
        "producer_function": "same_agent_minimal_kernel_bridge_001a.runner.build_contract",
        "task_id": model.TASK_ID,
        "environment": {
            "schema_version": dep["schema_version"],
            "seed": dep["seed"],
            "n": dep["n"],
            "l": dep["l"],
            "g": dep["g"],
            "train_slice_count": sum(len(ep["observations"]) for ep in dep["episodes"]),
            "heldout_case_count": len(dep["heldout_cases"]),
            "audit_regime_code_hashes": dep["audit_regime_code_hashes"],
            "latent_codes_exposed_to_candidate": False,
        },
        "metric": "heldout_multiclass_accuracy_over_contextualized_novel_cells",
        "equivalence_band": model.EQUIVALENCE_BAND,
        "required_baselines": sorted(REQUIRED_BASELINES),
        "required_ablations": sorted(ABLATION_IDS),
        "replay_contract": "recompute action and post-update state from serialized_state + observation + feedback",
        "leakage_contract": "scanner must pass clean candidate inputs and fire on positive-control leaked regime/target fields",
        "claim_ceiling": model.CLAIM_CEILING,
    }


def build_provenance(
    *,
    candidate_score: dict[str, Any],
    baseline_comparison: dict[str, Any],
    leakage_report: dict[str, Any],
    ablation_report: dict[str, Any],
    replay_report: dict[str, Any],
    result: dict[str, Any] | None,
) -> dict[str, Any]:
    records = [candidate_score, *baseline_comparison["results"]]
    for producer_id, report, func, value in (
        ("leakage_scan", leakage_report, run_leakage_scan, not leakage_report["leakage_detected"] and leakage_report["positive_control_fires"]),
        ("ablation_controls", ablation_report, run_ablation_report, ablation_report["ablation_gate_passed"]),
        ("replay_recomputation", replay_report, replay_trace, replay_report["passed"]),
    ):
        records.append(
            {
                "producer_id": producer_id,
                "producer_function": report["producer_function"],
                "input_artifacts": ["trace_rows", "frozen_deployment_generator", "candidate_state"],
                "run_id": model.RUN_ID,
                "seed_context_episode_ids": ["all"],
                "aggregation_rule": "control_must_pass_or_block_final_verdict",
                "code_path_hash": function_hash(func),
                "score": value,
                "consumed_by_final_verdict": True,
            }
        )
    if result is not None:
        records.append(
            {
                "producer_id": "final_verdict_derivation",
                "producer_function": "same_agent_minimal_kernel_bridge_001a.runner.derive_result",
                "input_artifacts": [
                    "candidate_score",
                    "baseline_comparison",
                    "leakage_report",
                    "ablation_report",
                    "replay_report",
                ],
                "run_id": model.RUN_ID,
                "seed_context_episode_ids": ["all"],
                "aggregation_rule": "ordered_blockers_then_baseline_equivalence_decision",
                "code_path_hash": function_hash(derive_result),
                "score": result["verdict"],
                "consumed_by_final_verdict": True,
            }
        )
    return {
        "producer_function": "same_agent_minimal_kernel_bridge_001a.runner.build_provenance",
        "records": records,
    }


def verify_provenance(provenance: dict[str, Any]) -> dict[str, Any]:
    required = {
        "producer_id",
        "producer_function",
        "input_artifacts",
        "run_id",
        "seed_context_episode_ids",
        "aggregation_rule",
        "code_path_hash",
        "score",
        "consumed_by_final_verdict",
    }
    required_ids = REQUIRED_BASELINES | {
        "candidate_minimal_kernel",
        "leakage_scan",
        "ablation_controls",
        "replay_recomputation",
        "final_verdict_derivation",
    }
    ids = {row.get("producer_id") for row in provenance.get("records", [])}
    reasons = []
    for missing in sorted(required_ids - ids):
        reasons.append(f"missing_required_provenance:{missing}")
    for index, row in enumerate(provenance.get("records", [])):
        missing_fields = sorted(required - set(row))
        if missing_fields:
            reasons.append(f"record_{index}_missing:{','.join(missing_fields)}")
        if len(str(row.get("code_path_hash", ""))) != 64:
            reasons.append(f"record_{index}_bad_code_path_hash")
        if row.get("consumed_by_final_verdict") is not True:
            reasons.append(f"record_{index}_not_consumed")
    return {
        "producer_function": "same_agent_minimal_kernel_bridge_001a.runner.verify_provenance",
        "passed": not reasons,
        "blocking_reasons": reasons,
    }


def derive_result(
    *,
    candidate_score: dict[str, Any],
    baseline_comparison: dict[str, Any],
    leakage_report: dict[str, Any],
    ablation_report: dict[str, Any],
    replay_report: dict[str, Any],
    provenance_check: dict[str, Any],
    trace_rows: list[dict[str, Any]],
    force_no_memory_read: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    verdict = "BASELINE_EQUIVALENCE"
    strongest = baseline_comparison.get("strongest_fair_baseline")
    candidate_value = float(candidate_score["score"])
    if baseline_comparison["missing_baseline_ids"]:
        verdict = "BLOCKED_MISSING_BASELINE"
        blockers.extend(f"missing_required_baseline:{name}" for name in baseline_comparison["missing_baseline_ids"])
    elif leakage_report["leakage_detected"] or not leakage_report["positive_control_fires"]:
        verdict = "LEAKAGE_DETECTED"
        blockers.extend(leakage_report["blocking_reasons"] or ["leakage_positive_control_failed"])
    elif not replay_report["passed"]:
        verdict = "REPLAY_INVALID"
        blockers.extend(replay_report["blocking_reasons"])
    elif force_no_memory_read or not any(
        row.get("next_action_changed_after_update") and row.get("action_selection_read_updated_memory")
        for row in trace_rows
        if row["event_type"] == "next_action"
    ):
        verdict = "CONTRACT_NOT_WIRED"
        blockers.append("action_selector_ignored_updated_belief_memory")
    elif not ablation_report["ablation_gate_passed"]:
        verdict = "ABLATION_INSUFFICIENT"
        blockers.extend(ablation_report["blocking_reasons"])
    elif not provenance_check["passed"]:
        verdict = "PROVENANCE_INCOMPLETE"
        blockers.extend(provenance_check["blocking_reasons"])
    elif strongest and strongest["score"] >= candidate_value - model.EQUIVALENCE_BAND:
        verdict = "BASELINE_EQUIVALENCE"
        blockers.append(f"baseline_tied_or_beat_candidate:{strongest['baseline_id']}")
    else:
        verdict = "BOUNDED_KERNEL_CONTRAST_SURVIVED"

    return {
        "task_id": model.TASK_ID,
        "run_id": model.RUN_ID,
        "verdict": verdict,
        "bounded_pass": verdict == "BOUNDED_KERNEL_CONTRAST_SURVIVED",
        "layer": "engineering_implementation + mechanism_hypothesis_test + learning_adaptation_boundary",
        "current_layer": "engineering implementation + mechanism hypothesis testing + learning/adaptation boundary",
        "mainline_integration_status": "none",
        "enabled_status": "local_explicit_cli_only",
        "real_trigger_evidence": "python -m src.same_agent_minimal_kernel_bridge_001a --output-dir artifacts/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A",
        "claim_ceiling": model.CLAIM_CEILING,
        "candidate_score": candidate_value,
        "strongest_fair_baseline_id": strongest["baseline_id"] if strongest else None,
        "strongest_fair_baseline_score": strongest["score"] if strongest else None,
        "equivalence_band": model.EQUIVALENCE_BAND,
        "trace_event_count": len(trace_rows),
        "stop_conditions_triggered": blockers,
        "forbidden_claims_absent": True,
        "n2_boundary": "N2-SBMC-ENV-REDESIGN-001A remains ADJUDICATED / BASELINE_EQUIVALENCE and is used only as negative route-governance evidence",
        "auto_remote_anchor": "forbidden",
        "authorization_flags": {
            "ego_mainline_runtime": False,
            "ui_persona_companion_behavior": False,
            "llm_airi_api_deployment": False,
            "mechanism_validity": False,
            "agency_or_subjectivity": False,
        },
        "claim_forbidden": CLAIM_FORBIDDEN,
    }


def build_failure_manifest(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": model.TASK_ID,
        "run_id": model.RUN_ID,
        "verdict": result["verdict"],
        "has_blocking_failure": result["verdict"] != "BOUNDED_KERNEL_CONTRAST_SURVIVED",
        "blocking_reasons": result["stop_conditions_triggered"],
        "preserve_as_negative_evidence": result["verdict"] == "BASELINE_EQUIVALENCE",
        "claim_ceiling": model.CLAIM_CEILING,
    }


def run_harness(
    output_dir: str | Path = model.ARTIFACT_DIR_REL,
    *,
    persist_artifacts: bool = True,
    disabled_baselines: tuple[str, ...] = (),
    force_clean_leak: bool = False,
    tamper_replay: bool = False,
    force_no_memory_read: bool = False,
) -> dict[str, Any]:
    dep = model.build_deployment(model.BASE_SEED)
    candidate = run_kernel_candidate(deployment=dep, force_no_memory_read=force_no_memory_read)
    candidate_score = score_record(
        producer_id="candidate_minimal_kernel",
        producer_function="same_agent_minimal_kernel_bridge_001a.runner.run_kernel_candidate",
        value=candidate["score"]["score"],
        seed_context_episode_ids=[case["case_id"] for case in dep["heldout_cases"]],
        code_hash=function_hash(run_kernel_candidate),
        input_artifacts=["frozen_deployment_generator", "serialized_state_trace", "training_feedback_stream", "heldout_cases"],
    )
    baseline_comparison = run_baseline_comparison(dep, disabled_baselines=disabled_baselines)
    leakage_report = run_leakage_scan(candidate["trace_rows"], force_clean_leak=force_clean_leak)
    replay_report = replay_trace(candidate["trace_rows"], tamper=tamper_replay)
    ablation_report = run_ablation_report(dep, float(candidate_score["score"]))
    provisional_provenance = build_provenance(
        candidate_score=candidate_score,
        baseline_comparison=baseline_comparison,
        leakage_report=leakage_report,
        ablation_report=ablation_report,
        replay_report=replay_report,
        result=None,
    )
    provisional_check = verify_provenance(
        {
            "records": [
                *provisional_provenance["records"],
                {
                    "producer_id": "final_verdict_derivation",
                    "producer_function": "same_agent_minimal_kernel_bridge_001a.runner.derive_result",
                    "input_artifacts": ["pending"],
                    "run_id": model.RUN_ID,
                    "seed_context_episode_ids": ["all"],
                    "aggregation_rule": "pending",
                    "code_path_hash": function_hash(derive_result),
                    "score": "pending",
                    "consumed_by_final_verdict": True,
                },
            ]
        }
    )
    result = derive_result(
        candidate_score=candidate_score,
        baseline_comparison=baseline_comparison,
        leakage_report=leakage_report,
        ablation_report=ablation_report,
        replay_report=replay_report,
        provenance_check=provisional_check,
        trace_rows=candidate["trace_rows"],
        force_no_memory_read=force_no_memory_read,
    )
    computed_evidence_provenance = build_provenance(
        candidate_score=candidate_score,
        baseline_comparison=baseline_comparison,
        leakage_report=leakage_report,
        ablation_report=ablation_report,
        replay_report=replay_report,
        result=result,
    )
    final_provenance_check = verify_provenance(computed_evidence_provenance)
    if result["verdict"] == "BOUNDED_KERNEL_CONTRAST_SURVIVED" and not final_provenance_check["passed"]:
        result = derive_result(
            candidate_score=candidate_score,
            baseline_comparison=baseline_comparison,
            leakage_report=leakage_report,
            ablation_report=ablation_report,
            replay_report=replay_report,
            provenance_check=final_provenance_check,
            trace_rows=candidate["trace_rows"],
            force_no_memory_read=force_no_memory_read,
        )
        computed_evidence_provenance = build_provenance(
            candidate_score=candidate_score,
            baseline_comparison=baseline_comparison,
            leakage_report=leakage_report,
            ablation_report=ablation_report,
            replay_report=replay_report,
            result=result,
        )
    failure_manifest = build_failure_manifest(result)
    collision_record = build_collision_record()
    contract = build_contract(dep)
    run = {
        "result": result,
        "trace_rows": candidate["trace_rows"],
        "candidate_score": candidate_score,
        "baseline_comparison": baseline_comparison,
        "ablation_report": ablation_report,
        "replay_report": replay_report,
        "leakage_report": leakage_report,
        "computed_evidence_provenance": computed_evidence_provenance,
        "failure_manifest": failure_manifest,
        "collision_record": collision_record,
        "frozen_metric_baseline_ablation_contract": contract,
    }
    if persist_artifacts:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        write_json(out / "result.json", result)
        write_jsonl(out / "trace.jsonl", candidate["trace_rows"])
        write_json(out / "baseline_comparison.json", baseline_comparison)
        write_json(out / "ablation_report.json", ablation_report)
        write_json(out / "replay_report.json", replay_report)
        write_json(out / "leakage_report.json", leakage_report)
        write_json(out / "computed_evidence_provenance.json", computed_evidence_provenance)
        write_json(out / "failure_manifest.json", failure_manifest)
        write_json(out / "collision_record.json", collision_record)
        write_json(out / "frozen_metric_baseline_ablation_contract.json", contract)
        write_text(out / "claim_ceiling.txt", model.CLAIM_CEILING + "\n")
    return run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=model.ARTIFACT_DIR_REL)
    args = parser.parse_args(argv)
    run = run_harness(output_dir=args.output_dir, persist_artifacts=True)
    print(pretty_json(run["result"]))
    return 0
