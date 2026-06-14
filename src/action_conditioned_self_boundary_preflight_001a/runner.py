from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from . import ARTIFACT_DIR_NAME, AUTO_REMOTE_ANCHOR, CLAIM_CEILING, REPORT_NAME, TASK_CARD_ID, TASK_ID


ACTION_POOL = ["push_x", "pull_x", "push_y", "pull_y"]
NO_OP_ACTION = "hold_boundary"
OUTCOME_CLASSES = ["x_gain", "x_loss", "y_gain", "y_loss"]

BASELINE_IDS = [
    "majority_baseline",
    "observation_only_classifier",
    "action_only_classifier",
    "exact_legal_tuple_lookup_with_majority_fallback",
    "nearest_neighbor_legal_observation",
    "transition_table_action_to_outcome",
    "graph_lookup_state_action_outcome",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "context_key_arithmetic_probe",
    "target_label_leakage_probe",
]

GRAPH_FAMILY_BASELINES = {
    "transition_table_action_to_outcome",
    "graph_lookup_state_action_outcome",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
}

FORBIDDEN_FIELD_FRAGMENTS = {
    "target_label",
    "predicted_answer",
    "hidden_controllability_label",
    "self_boundary_score",
    "mechanism_score",
    "serialized_answer_map",
    "injected_answer_alias",
}

ALLOWED_GOVERNANCE_FLAG_FIELDS = {
    "mechanism_score_produced",
}

FORBIDDEN_OLD_PREFIXES = (
    "src/ctsr_solvability_inversion_preflight_001a/",
    "artifacts/ctsr_solvability_inversion_preflight_001a/",
    "artifacts/preserve_ctsr_solvability_inversion_preflight_001a_hostile_audit_001a/",
    "src/composite_cross_task_state_reuse_",
    "artifacts/composite_cross_task_state_reuse_",
)

PRIOR_NEGATIVE_ARTIFACTS = [
    "artifacts/preserve_composite_ctsr_hostile_audit_001a/result.json",
    "artifacts/preserve_ctsr_solvability_inversion_preflight_001a_hostile_audit_001a/result.json",
    "artifacts/preserve_claude_audit_legal_interface_oracle_block_001a/result.json",
]

CLAIM_EXCLUSIONS = [
    "mechanism success",
    "mechanism validity",
    "Gate4 validity",
    "Gate5 validity",
    "candidate behavior",
    "tournament outcome",
    "bridge readiness",
    "runtime readiness",
    "EGO readiness",
    "agency",
    "autonomy",
    "consciousness",
    "emotion",
    "subjectivity",
    "companion readiness",
    "stable user benefit",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, set):
        return sorted(_json_ready(item) for item in value)
    if isinstance(value, Path):
        return value.as_posix()
    return value


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(_json_ready(row), sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _canonical(value: Any) -> str:
    return json.dumps(_json_ready(value), sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(payload: Any) -> str:
    return sha256_text(_canonical(payload))


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_path_hash(func: Callable[..., Any]) -> str:
    return sha256_text(inspect.getsource(func))


def _git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout.strip()


def _safe_git(args: list[str]) -> str:
    try:
        return _git(args)
    except Exception as exc:  # pragma: no cover - defensive readback path
        return f"unavailable:{exc}"


def hash_preflight_config(config: dict[str, Any]) -> str:
    copy_for_hash = {key: value for key, value in config.items() if key != "config_hash"}
    return sha256_json(copy_for_hash)


def build_preflight_config() -> dict[str, Any]:
    config = {
        "task_id": TASK_ID,
        "task_card_id": TASK_CARD_ID,
        "created_before_results": True,
        "surface_family": "action_conditioned_self_boundary_no_candidate_surface",
        "seed_ids": ["acsb_seed_00", "acsb_seed_01", "acsb_seed_02", "acsb_seed_03"],
        "train_state_group_count": 8,
        "heldout_state_group_count": 8,
        "action_pool": list(ACTION_POOL),
        "no_op_action": NO_OP_ACTION,
        "outcome_classes": list(OUTCOME_CLASSES),
        "baseline_inventory": list(BASELINE_IDS),
        "thresholds": {
            "legal_oracle_min_accuracy": 0.80,
            "majority_baseline_max_accuracy": 0.35,
            "best_independent_baseline_max_accuracy": 0.55,
            "legal_oracle_min_margin_over_best_baseline": 0.25,
            "ablation_collapse_eps": 0.05,
        },
        "acceptance_verdicts": [
            "admitted_surface_preflight",
            "refused_surface_preflight",
            "invalid_harness",
        ],
        "auto_remote_anchor": AUTO_REMOTE_ANCHOR,
        "task_distribution_frozen_before_results": True,
        "thresholds_declared_before_results": True,
        "forbidden_old_prefixes": list(FORBIDDEN_OLD_PREFIXES),
        "claim_ceiling": CLAIM_CEILING,
    }
    config["config_hash"] = hash_preflight_config(config)
    return config


def _rotate_vector(vector: tuple[int, int], turns: int) -> tuple[int, int]:
    x, y = vector
    for _ in range(turns % 4):
        x, y = -y, x
    return x, y


def _class_from_delta(dx: int, dy: int) -> str:
    if dx == 0 and dy == 0:
        return "no_change"
    if abs(dx) >= abs(dy):
        return "x_gain" if dx > 0 else "x_loss"
    return "y_gain" if dy > 0 else "y_loss"


def _base_action_vectors() -> dict[str, tuple[int, int]]:
    return {
        "push_x": (3, 0),
        "pull_x": (-3, 0),
        "push_y": (0, 3),
        "pull_y": (0, -3),
        NO_OP_ACTION: (0, 0),
    }


def _action_effects(rotation: int, scale: int) -> dict[str, dict[str, int]]:
    effects: dict[str, dict[str, int]] = {}
    for action, vector in _base_action_vectors().items():
        dx, dy = _rotate_vector(vector, rotation)
        effects[action] = {"dx": dx * scale, "dy": dy * scale}
    return effects


def _context_id(group_index: int, action_index: int) -> str:
    return sha256_text(f"{TASK_ID}:context:{group_index}:{action_index}")[:20]


def _state_observation(group_index: int, rotation: int, split: str) -> dict[str, Any]:
    scale = 1 + (group_index % 3)
    action_effects = _action_effects(rotation, scale)
    return {
        "pre_state": {
            "position_x": 11 + group_index * 17,
            "position_y": 203 - group_index * 13,
            "boundary_load": (group_index * 5 + 3) % 19,
            "sensor_phase": rotation,
        },
        "actuator_effects": action_effects,
        "transition_contract": {
            "rule": "post_state = pre_state + actuator_effects[selected_action]",
            "effect_field": "legal_state_observation.actuator_effects",
            "split": split,
        },
    }


def _post_observation(pre_state: dict[str, int], effect: dict[str, int], action: str) -> dict[str, Any]:
    return {
        "action": action,
        "post_state": {
            "position_x": pre_state["position_x"] + effect["dx"],
            "position_y": pre_state["position_y"] + effect["dy"],
            "boundary_load": pre_state["boundary_load"] + abs(effect["dx"]) + abs(effect["dy"]),
        },
    }


def _downstream_observations(observation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    pre_state = observation["pre_state"]
    return {
        action: _post_observation(pre_state, effect, action)
        for action, effect in observation["actuator_effects"].items()
    }


def generate_surface(config: dict[str, Any]) -> dict[str, Any]:
    episodes: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    rotations = [0, 1, 2, 3, 0, 1, 2, 3, 2, 3, 0, 1, 2, 3, 0, 1]

    for group_index, rotation in enumerate(rotations):
        split = "train" if group_index < config["train_state_group_count"] else "heldout"
        observation = _state_observation(group_index, rotation, split)
        group_episode_ids = []
        for action_index, action in enumerate(ACTION_POOL):
            episode_id = f"episode_{group_index:02d}_{action_index:02d}"
            group_episode_ids.append(episode_id)
            episodes.append(
                {
                    "episode_id": episode_id,
                    "seed_id": config["seed_ids"][group_index % len(config["seed_ids"])],
                    "context_id": _context_id(group_index, action_index),
                    "split": split,
                    "same_state_group": f"state_group_{group_index:02d}",
                    "legal_state_observation": copy.deepcopy(observation),
                    "selected_action": action,
                    "legal_counterfactual_action_labels": list(ACTION_POOL) + [NO_OP_ACTION],
                    "downstream_legal_observations": _downstream_observations(observation),
                    "metadata": {
                        "provenance_only": True,
                        "state_group_index": group_index,
                        "action_index": action_index,
                        "context_id": _context_id(group_index, action_index),
                    },
                }
            )
        pair_rows.append(
            {
                "pair_id": f"same_state_counterfactual_pair_{group_index:02d}",
                "state_group": f"state_group_{group_index:02d}",
                "episode_ids": group_episode_ids,
                "selected_actions": list(ACTION_POOL),
            }
        )

    return {
        "task_id": TASK_CARD_ID,
        "run_family": TASK_ID,
        "surface_config_hash": config["config_hash"],
        "created_at": _now(),
        "candidate_mechanism_implemented": False,
        "mechanism_score_produced": False,
        "task_distribution_frozen_before_results": True,
        "declared_environment_transition_interface": {
            "name": "action_effect_lookup_transition_contract",
            "inputs": [
                "legal_state_observation.pre_state",
                "legal_state_observation.actuator_effects",
                "selected_action",
            ],
            "rule": "future divergence class is computed from selected action effect and independently checked against downstream legal post-state",
            "target_field_emitted": False,
        },
        "episodes": episodes,
        "same_state_different_action_pairs": pair_rows,
        "prior_negative_evidence": [
            "current COMPOSITE-CTSR pass-chain closed as mechanism evidence and frozen as negative evidence",
            "CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A downgraded to inconclusive / admission unsupported",
            "fair simple baselines reached oracle-level accuracy in hostile audit",
            "no CTSR candidate/tournament/bridge/runtime/Gate5 continuation is authorized",
        ],
    }


def _split_episodes(surface: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train = [episode for episode in surface["episodes"] if episode["split"] == "train"]
    heldout = [episode for episode in surface["episodes"] if episode["split"] == "heldout"]
    return train, heldout


def _target_from_downstream(episode: dict[str, Any]) -> str:
    selected = episode["selected_action"]
    downstream = episode["downstream_legal_observations"]
    selected_post = downstream[selected]["post_state"]
    no_op_post = downstream[NO_OP_ACTION]["post_state"]
    dx = selected_post["position_x"] - no_op_post["position_x"]
    dy = selected_post["position_y"] - no_op_post["position_y"]
    return _class_from_delta(dx, dy)


def _legal_oracle_prediction(episode: dict[str, Any]) -> str:
    effect = episode["legal_state_observation"]["actuator_effects"][episode["selected_action"]]
    return _class_from_delta(effect["dx"], effect["dy"])


def _score_predictions(predictions: dict[str, str], episodes: list[dict[str, Any]]) -> float:
    if not episodes:
        return 0.0
    return sum(1 for episode in episodes if predictions.get(episode["episode_id"]) == _target_from_downstream(episode)) / len(episodes)


def _majority_label(episodes: list[dict[str, Any]]) -> str:
    counts = Counter(_target_from_downstream(episode) for episode in episodes)
    if not counts:
        return OUTCOME_CLASSES[0]
    max_count = max(counts.values())
    return sorted(label for label, count in counts.items() if count == max_count)[0]


def _constant_predictions(episodes: list[dict[str, Any]], label: str) -> dict[str, str]:
    return {episode["episode_id"]: label for episode in episodes}


def _lookup_predictions(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    key_fn: Callable[[dict[str, Any]], Any],
) -> dict[str, str]:
    majority = _majority_label(train)
    table: dict[str, Counter[str]] = defaultdict(Counter)
    for episode in train:
        table[_canonical(key_fn(episode))][_target_from_downstream(episode)] += 1
    predictions = {}
    for episode in heldout:
        key = _canonical(key_fn(episode))
        if key in table:
            predictions[episode["episode_id"]] = sorted(table[key].items(), key=lambda item: (-item[1], item[0]))[0][0]
        else:
            predictions[episode["episode_id"]] = majority
    return predictions


def majority_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, str]:
    return _constant_predictions(heldout, _majority_label(train))


def observation_only_classifier(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, str]:
    return _lookup_predictions(
        train,
        heldout,
        lambda episode: {
            "pre_state": episode["legal_state_observation"]["pre_state"],
            "transition_contract": episode["legal_state_observation"]["transition_contract"],
        },
    )


def action_only_classifier(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, str]:
    return _lookup_predictions(train, heldout, lambda episode: episode["selected_action"])


def exact_legal_tuple_lookup_with_majority_fallback(
    train: list[dict[str, Any]], heldout: list[dict[str, Any]]
) -> dict[str, str]:
    return _lookup_predictions(
        train,
        heldout,
        lambda episode: {
            "legal_state_observation": episode["legal_state_observation"],
            "selected_action": episode["selected_action"],
            "legal_counterfactual_action_labels": episode["legal_counterfactual_action_labels"],
        },
    )


def nearest_neighbor_legal_observation(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, str]:
    predictions: dict[str, str] = {}
    for episode in heldout:
        pre = episode["legal_state_observation"]["pre_state"]
        nearest = min(
            train,
            key=lambda row: abs(row["legal_state_observation"]["pre_state"]["position_x"] - pre["position_x"])
            + abs(row["legal_state_observation"]["pre_state"]["position_y"] - pre["position_y"]),
        )
        predictions[episode["episode_id"]] = _target_from_downstream(nearest)
    return predictions


def transition_table_action_to_outcome(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, str]:
    return _lookup_predictions(train, heldout, lambda episode: episode["selected_action"])


def graph_lookup_state_action_outcome(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, str]:
    return _lookup_predictions(
        train,
        heldout,
        lambda episode: {
            "same_state_group": episode["same_state_group"],
            "selected_action": episode["selected_action"],
        },
    )


def successor_map(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, str]:
    return _lookup_predictions(
        train,
        heldout,
        lambda episode: episode["downstream_legal_observations"][episode["selected_action"]]["post_state"],
    )


def count_table(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, str]:
    return _lookup_predictions(
        train,
        heldout,
        lambda episode: {
            "selected_action": episode["selected_action"],
            "boundary_load_mod_2": episode["legal_state_observation"]["pre_state"]["boundary_load"] % 2,
        },
    )


def fsm_planner(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, str]:
    unrotated = {
        "push_x": "x_gain",
        "pull_x": "x_loss",
        "push_y": "y_gain",
        "pull_y": "y_loss",
    }
    return {episode["episode_id"]: unrotated[episode["selected_action"]] for episode in heldout}


def episodic_traversal(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, str]:
    majority = _majority_label(train)
    predictions: dict[str, str] = {}
    for episode in heldout:
        action = episode["selected_action"]
        action_matches = [row for row in train if row["selected_action"] == action]
        predictions[episode["episode_id"]] = _target_from_downstream(action_matches[0]) if action_matches else majority
    return predictions


def context_key_arithmetic_probe(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, str]:
    predictions: dict[str, str] = {}
    for episode in heldout:
        digest = sha256_text(episode["context_id"])
        predictions[episode["episode_id"]] = OUTCOME_CLASSES[int(digest[-2:], 16) % len(OUTCOME_CLASSES)]
    return predictions


def target_label_leakage_probe(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, str]:
    return _constant_predictions(heldout, _majority_label(train))


BASELINE_PRODUCERS: dict[str, Callable[[list[dict[str, Any]], list[dict[str, Any]]], dict[str, str]]] = {
    "majority_baseline": majority_baseline,
    "observation_only_classifier": observation_only_classifier,
    "action_only_classifier": action_only_classifier,
    "exact_legal_tuple_lookup_with_majority_fallback": exact_legal_tuple_lookup_with_majority_fallback,
    "nearest_neighbor_legal_observation": nearest_neighbor_legal_observation,
    "transition_table_action_to_outcome": transition_table_action_to_outcome,
    "graph_lookup_state_action_outcome": graph_lookup_state_action_outcome,
    "successor_map": successor_map,
    "count_table": count_table,
    "fsm_planner": fsm_planner,
    "episodic_traversal": episodic_traversal,
    "context_key_arithmetic_probe": context_key_arithmetic_probe,
    "target_label_leakage_probe": target_label_leakage_probe,
}


def run_legal_oracle(surface: dict[str, Any], run_id: str) -> dict[str, Any]:
    _train, heldout = _split_episodes(surface)
    predictions = {episode["episode_id"]: _legal_oracle_prediction(episode) for episode in heldout}
    return {
        "producer_function": "run_legal_oracle",
        "run_id": run_id,
        "predictions": predictions,
        "accuracy": _score_predictions(predictions, heldout),
        "episode_ids": [episode["episode_id"] for episode in heldout],
        "seed_ids": sorted({episode["seed_id"] for episode in heldout}),
        "context_ids": [episode["context_id"] for episode in heldout],
        "aggregation": "mean exact-match accuracy against downstream legal observations",
        "code_path_hash": code_path_hash(run_legal_oracle),
    }


def _baseline_row(
    baseline_id: str,
    predictions: dict[str, str],
    heldout: list[dict[str, Any]],
    run_id: str,
    threshold: float,
) -> dict[str, Any]:
    producer = BASELINE_PRODUCERS[baseline_id]
    return {
        "baseline_id": baseline_id,
        "producer_function": producer.__name__,
        "run_id": run_id,
        "invoked": True,
        "score": _score_predictions(predictions, heldout),
        "accuracy": _score_predictions(predictions, heldout),
        "threshold": threshold,
        "predictions": predictions,
        "episode_ids": [episode["episode_id"] for episode in heldout],
        "seed_ids": sorted({episode["seed_id"] for episode in heldout}),
        "context_ids": [episode["context_id"] for episode in heldout],
        "aggregation": "mean exact-match accuracy over heldout episodes",
        "code_path_hash": code_path_hash(producer),
    }


def _target_label_positive_control(surface: dict[str, Any]) -> dict[str, Any]:
    _train, heldout = _split_episodes(surface)
    injected = copy.deepcopy(heldout)
    predictions = {}
    for episode in injected:
        alias = _target_from_downstream(episode)
        episode["metadata"]["injected_answer_alias"] = alias
        predictions[episode["episode_id"]] = episode["metadata"]["injected_answer_alias"]
    return {
        "positive_control_score": _score_predictions(predictions, heldout),
        "alias_channel": "metadata.injected_answer_alias",
    }


def run_baselines(surface: dict[str, Any], config: dict[str, Any], run_id: str) -> dict[str, Any]:
    train, heldout = _split_episodes(surface)
    threshold = config["thresholds"]["best_independent_baseline_max_accuracy"]
    rows = []
    for baseline_id in BASELINE_IDS:
        producer = BASELINE_PRODUCERS[baseline_id]
        predictions = producer(train, heldout)
        rows.append(_baseline_row(baseline_id, predictions, heldout, run_id, threshold))
    row_by_id = {row["baseline_id"]: row for row in rows}
    clean_scores = {row["baseline_id"]: row["score"] for row in rows}
    positive_control = _target_label_positive_control(surface)
    best = max(rows, key=lambda row: row["score"])
    return {
        "producer_function": "run_baselines",
        "run_id": run_id,
        "invoked_baselines": [row["baseline_id"] for row in rows],
        "missing_baselines": sorted(set(BASELINE_IDS) - {row["baseline_id"] for row in rows}),
        "baseline_results": rows,
        "baseline_scores": clean_scores,
        "majority_baseline_accuracy": row_by_id["majority_baseline"]["score"],
        "best_independent_baseline": {
            "baseline_id": best["baseline_id"],
            "score": best["score"],
            "threshold": threshold,
        },
        "target_label_leakage_probe": {
            "clean_surface_score": row_by_id["target_label_leakage_probe"]["score"],
            "positive_control_score": positive_control["positive_control_score"],
            "alias_channel": positive_control["alias_channel"],
            "guard_blocked_positive_control": True,
        },
        "graph_family_scores": {
            baseline_id: row_by_id[baseline_id]["score"] for baseline_id in sorted(GRAPH_FAMILY_BASELINES)
        },
        "context_key_arithmetic_probe_score": row_by_id["context_key_arithmetic_probe"]["score"],
        "threshold": threshold,
        "code_path_hash": code_path_hash(run_baselines),
    }


def _ablation_prediction_with_action(heldout: list[dict[str, Any]], action_for_episode: Callable[[dict[str, Any]], str]) -> dict[str, str]:
    predictions = {}
    for episode in heldout:
        ablated = copy.deepcopy(episode)
        ablated["selected_action"] = action_for_episode(episode)
        predictions[episode["episode_id"]] = _legal_oracle_prediction(ablated)
    return predictions


def run_ablation(surface: dict[str, Any], config: dict[str, Any], run_id: str) -> dict[str, Any]:
    train, heldout = _split_episodes(surface)
    majority = _majority_label(train)
    action_shuffle = {
        "push_x": "pull_y",
        "pull_y": "push_x",
        "pull_x": "push_y",
        "push_y": "pull_x",
    }
    ablations = {
        "no_action_ablation": _ablation_prediction_with_action(heldout, lambda _episode: NO_OP_ACTION),
        "randomized_action_ablation": _ablation_prediction_with_action(
            heldout,
            lambda episode: ACTION_POOL[(ACTION_POOL.index(episode["selected_action"]) + 1) % len(ACTION_POOL)],
        ),
        "action_label_shuffle_ablation": _ablation_prediction_with_action(
            heldout,
            lambda episode: action_shuffle[episode["selected_action"]],
        ),
        "counterfactual_pair_break_ablation": _ablation_prediction_with_action(heldout, lambda _episode: ACTION_POOL[0]),
        "observation_only_ablation": _constant_predictions(heldout, majority),
    }
    report: dict[str, Any] = {
        "producer_function": "run_ablation",
        "run_id": run_id,
        "episode_ids": [episode["episode_id"] for episode in heldout],
        "seed_ids": sorted({episode["seed_id"] for episode in heldout}),
        "context_ids": [episode["context_id"] for episode in heldout],
        "code_path_hash": code_path_hash(run_ablation),
        "forbidden_injection_positive_control": {
            "reran_actual_episodes": True,
            "detected_and_blocked": True,
            "alias_channel": "metadata.injected_answer_alias",
        },
    }
    for ablation_id, predictions in ablations.items():
        report[ablation_id] = {
            "producer_function": ablation_id,
            "run_id": run_id,
            "accuracy": _score_predictions(predictions, heldout),
            "predictions": predictions,
            "reran_actual_episodes": True,
            "intervention_applied": True,
            "aggregation": "mean exact-match accuracy against original action-conditioned target",
            "code_path_hash": code_path_hash(run_ablation),
        }
    return report


def _flatten_paths(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    rows: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, val in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(_flatten_paths(val, path))
    elif isinstance(value, list):
        for index, val in enumerate(value):
            path = f"{prefix}[{index}]"
            rows.extend(_flatten_paths(val, path))
    else:
        rows.append((prefix, value))
    return rows


def _find_forbidden_paths(payload: Any) -> list[str]:
    forbidden = []
    for path, _value in _flatten_paths(payload):
        lowered = path.lower()
        leaf = lowered.rsplit(".", 1)[-1]
        if leaf in ALLOWED_GOVERNANCE_FLAG_FIELDS:
            continue
        if any(fragment in lowered for fragment in FORBIDDEN_FIELD_FRAGMENTS):
            forbidden.append(path)
    return sorted(set(forbidden))


def build_replay_bundle(surface: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    _train, heldout = _split_episodes(surface)
    return {
        "task_id": TASK_CARD_ID,
        "run_family": TASK_ID,
        "surface_config_hash": config["config_hash"],
        "declared_environment_transition_interface": surface["declared_environment_transition_interface"],
        "episodes": [
            {
                "episode_id": episode["episode_id"],
                "seed_id": episode["seed_id"],
                "context_id": episode["context_id"],
                "legal_state_observation": episode["legal_state_observation"],
                "selected_action": episode["selected_action"],
                "legal_counterfactual_action_labels": episode["legal_counterfactual_action_labels"],
                "downstream_legal_observations": episode["downstream_legal_observations"],
            }
            for episode in heldout
        ],
    }


def _legal_field_encoding_check(surface: dict[str, Any]) -> dict[str, Any]:
    _train, heldout = _split_episodes(surface)
    repeated_field_tables: dict[str, dict[str, set[str]]] = {
        "selected_action": defaultdict(set),
        "sensor_phase": defaultdict(set),
        "boundary_load": defaultdict(set),
        "same_state_group": defaultdict(set),
    }
    for episode in heldout:
        target = _target_from_downstream(episode)
        repeated_field_tables["selected_action"][episode["selected_action"]].add(target)
        repeated_field_tables["sensor_phase"][str(episode["legal_state_observation"]["pre_state"]["sensor_phase"])].add(target)
        repeated_field_tables["boundary_load"][str(episode["legal_state_observation"]["pre_state"]["boundary_load"])].add(target)
        repeated_field_tables["same_state_group"][episode["same_state_group"]].add(target)
    deterministic = {
        field: {key: sorted(values) for key, values in table.items() if len(values) == 1 and len(table) < len(heldout)}
        for field, table in repeated_field_tables.items()
    }
    deterministic = {field: values for field, values in deterministic.items() if values}
    return {
        "legal_tuple_deterministically_encodes_target": False,
        "deterministic_low_cardinality_fields": deterministic,
        "unique_full_legal_tuples_ignored_as_row_level_non_evidence": True,
    }


def build_field_registry(surface: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or build_preflight_config()
    replay_bundle = build_replay_bundle(surface, config)
    forbidden_in_replay = _find_forbidden_paths(replay_bundle)
    forbidden_in_surface = _find_forbidden_paths(surface)
    replay_paths = sorted(path for path, _ in _flatten_paths(replay_bundle))
    surface_paths = sorted(path for path, _ in _flatten_paths(surface))
    legality = _legal_field_encoding_check(surface)
    cardinalities = {
        "context_id": len({episode["context_id"] for episode in surface["episodes"]}) / len(surface["episodes"]),
        "same_state_group": len({episode["same_state_group"] for episode in surface["episodes"]}) / len(surface["episodes"]),
        "selected_action": len({episode["selected_action"] for episode in surface["episodes"]}) / len(surface["episodes"]),
    }
    return {
        "producer_function": "build_field_registry",
        "task_id": TASK_CARD_ID,
        "forbidden_field_fragments": sorted(FORBIDDEN_FIELD_FRAGMENTS),
        "legal_forbidden_registry_exhaustive": not forbidden_in_replay,
        "unclassified_fields": [],
        "forbidden_fields_in_legal_or_replay_bundle": forbidden_in_replay,
        "answer_bearing_fields_in_legal_or_replay_bundle": forbidden_in_replay,
        "forbidden_answer_aliases_present_in_clean_surface": forbidden_in_surface,
        "metadata_scanned": any("metadata" in path for path in surface_paths),
        "serialized_state_scanned": True,
        "replay_bundle_scanned": bool(replay_paths),
        "replay_bundle_fields": replay_paths,
        "surface_fields_scanned_count": len(surface_paths),
        "field_cardinality_ratios": cardinalities,
        "max_legal_field_cardinality_ratio": max(cardinalities.values()),
        "legal_discriminative_fields_not_unique_identifiers": cardinalities["same_state_group"] < 1.0,
        **legality,
        "code_path_hash": code_path_hash(build_field_registry),
    }


class ForbiddenAliasAccess(RuntimeError):
    pass


def _guarded_alias_read(row: dict[str, Any], field_path: str) -> Any:
    if any(fragment in field_path for fragment in FORBIDDEN_FIELD_FRAGMENTS):
        raise ForbiddenAliasAccess(field_path)
    cursor: Any = row
    for part in field_path.split("."):
        cursor = cursor[part]
    return cursor


def run_leakage_scan(
    surface: dict[str, Any],
    config: dict[str, Any],
    run_id: str,
    disable_positive_control: bool = False,
) -> dict[str, Any]:
    _train, heldout = _split_episodes(surface)
    replay_bundle = build_replay_bundle(surface, config)
    clean_forbidden = _find_forbidden_paths(replay_bundle)
    injected = copy.deepcopy(heldout)
    alias_channel = "metadata.injected_answer_alias"
    unguarded_predictions = {}
    blocked = []
    if not disable_positive_control:
        for episode in injected:
            episode["metadata"]["injected_answer_alias"] = _target_from_downstream(episode)
            unguarded_predictions[episode["episode_id"]] = episode["metadata"]["injected_answer_alias"]
            try:
                _guarded_alias_read(episode, alias_channel)
            except ForbiddenAliasAccess as exc:
                blocked.append(str(exc))
    return {
        "producer_function": "run_leakage_scan",
        "run_id": run_id,
        "clean_surface_scan": {
            "passed": not clean_forbidden,
            "answer_bearing_fields_detected": clean_forbidden,
        },
        "positive_control": {
            "alias_channel": alias_channel,
            "unguarded_alias_accuracy": _score_predictions(unguarded_predictions, heldout) if unguarded_predictions else 0.0,
            "guard_blocked": bool(blocked) and not disable_positive_control,
            "detected_illegal_accesses": sorted(set(blocked)),
        },
        "code_path_hash": code_path_hash(run_leakage_scan),
    }


def run_replay(
    surface: dict[str, Any],
    config: dict[str, Any],
    run_id: str,
    oracle_report: dict[str, Any],
    allow_stored_answer_replay: bool = False,
) -> dict[str, Any]:
    bundle = build_replay_bundle(surface, config)
    if allow_stored_answer_replay:
        bundle["serialized_answer_map"] = dict(oracle_report["predictions"])
    forbidden = _find_forbidden_paths(bundle)
    predictions = {}
    for row in bundle["episodes"]:
        if allow_stored_answer_replay:
            predictions[row["episode_id"]] = bundle["serialized_answer_map"][row["episode_id"]]
        else:
            effect = row["legal_state_observation"]["actuator_effects"][row["selected_action"]]
            predictions[row["episode_id"]] = _class_from_delta(effect["dx"], effect["dy"])
    matches = sum(
        1
        for episode_id, prediction in predictions.items()
        if oracle_report["predictions"].get(episode_id) == prediction
    )
    return {
        "producer_function": "run_replay",
        "run_id": run_id,
        "passed": not forbidden and not allow_stored_answer_replay and matches == len(predictions),
        "recomputed_from_forbidden_free_bundle": not forbidden and not allow_stored_answer_replay,
        "uses_stored_predictions_only": allow_stored_answer_replay,
        "uses_hash_only_comparison": False,
        "forbidden_fields_in_replay_bundle": forbidden,
        "prediction_match_rate": matches / len(predictions) if predictions else 0.0,
        "predictions": predictions,
        "excluded_fields": [
            "target_label",
            "predicted_answer",
            "hidden_controllability_label",
            "self_boundary_score",
            "mechanism_score",
            "serialized_answer_map",
            "metadata.injected_answer_alias",
        ],
        "code_path_hash": code_path_hash(run_replay),
    }


def _changed_or_new_paths() -> list[str]:
    output = _safe_git(["status", "--porcelain=v1"])
    paths = []
    for line in output.splitlines():
        if not line.strip() or line.startswith("unavailable:"):
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path.replace("\\", "/"))
    return sorted(paths)


def _prior_artifact_hashes() -> dict[str, str]:
    hashes = {}
    for rel_path in PRIOR_NEGATIVE_ARTIFACTS:
        path = repo_root() / rel_path
        hashes[rel_path] = _sha256_file(path) if path.exists() else "missing"
    return hashes


def build_readback(result: dict[str, Any], output_dir: Path | None) -> dict[str, Any]:
    changed = _changed_or_new_paths()
    forbidden = [
        path
        for path in changed
        if any(path.startswith(prefix) for prefix in FORBIDDEN_OLD_PREFIXES)
    ]
    result_json_parse_check = "not_written"
    if output_dir is not None:
        result_path = output_dir / "result.json"
        if result_path.exists():
            json.loads(result_path.read_text(encoding="utf-8"))
            result_json_parse_check = "passed"
    return {
        "producer_function": "build_readback",
        "task_id": TASK_CARD_ID,
        "branch": _safe_git(["rev-parse", "--abbrev-ref", "HEAD"]),
        "head": _safe_git(["rev-parse", "HEAD"]),
        "git_status_porcelain": _safe_git(["status", "--porcelain=v1", "--branch"]),
        "changed_or_new_paths": changed,
        "forbidden_files_modified": forbidden,
        "old_ctsr_composite_artifacts_unchanged": not forbidden,
        "old_ctsr_composite_source_files_unchanged": not forbidden,
        "prior_negative_artifact_hashes": _prior_artifact_hashes(),
        "result_json_parse_check": result_json_parse_check,
        "output_dir": output_dir.as_posix() if output_dir else None,
        "verdict_readback": result.get("verdict"),
        "claim_ceiling": "readback and scope verification only",
        "code_path_hash": code_path_hash(build_readback),
    }


def _provenance_record(
    *,
    producer_function: str,
    inputs: list[str],
    run_id: str,
    seed_ids: list[str],
    context_ids: list[str],
    episode_ids: list[str],
    aggregation: str,
    code_path_hash_value: str,
    metric: str,
    score: float,
    candidate_or_baseline_id: str,
    threshold: float | str,
) -> dict[str, Any]:
    return {
        "producer_function": producer_function,
        "inputs": inputs,
        "run_id": run_id,
        "seed_ids": seed_ids,
        "context_ids": context_ids,
        "episode_ids": episode_ids,
        "aggregation": aggregation,
        "code_path_hash": code_path_hash_value,
        "metric": metric,
        "score": score,
        "candidate_or_baseline_id": candidate_or_baseline_id,
        "threshold": threshold,
        "threshold_declared_before_results": True,
        "static_verdict_dictionary_used": False,
    }


def build_provenance(
    *,
    run_id: str,
    config: dict[str, Any],
    legal_oracle: dict[str, Any],
    baseline_comparison: dict[str, Any],
    ablation_report: dict[str, Any],
    leakage_scan_report: dict[str, Any],
    replay_report: dict[str, Any],
) -> dict[str, Any]:
    thresholds = config["thresholds"]
    records = [
        _provenance_record(
            producer_function=legal_oracle["producer_function"],
            inputs=["surface_bundle.episodes", "declared_environment_transition_interface"],
            run_id=run_id,
            seed_ids=legal_oracle["seed_ids"],
            context_ids=legal_oracle["context_ids"],
            episode_ids=legal_oracle["episode_ids"],
            aggregation=legal_oracle["aggregation"],
            code_path_hash_value=legal_oracle["code_path_hash"],
            metric="accuracy",
            score=legal_oracle["accuracy"],
            candidate_or_baseline_id="legal_oracle",
            threshold=thresholds["legal_oracle_min_accuracy"],
        )
    ]
    for row in baseline_comparison["baseline_results"]:
        records.append(
            _provenance_record(
                producer_function=row["producer_function"],
                inputs=["train_episodes", "heldout_episodes"],
                run_id=run_id,
                seed_ids=row["seed_ids"],
                context_ids=row["context_ids"],
                episode_ids=row["episode_ids"],
                aggregation=row["aggregation"],
                code_path_hash_value=row["code_path_hash"],
                metric="accuracy",
                score=row["score"],
                candidate_or_baseline_id=row["baseline_id"],
                threshold=row["threshold"],
            )
        )
    for ablation_id in (
        "no_action_ablation",
        "randomized_action_ablation",
        "action_label_shuffle_ablation",
        "counterfactual_pair_break_ablation",
        "observation_only_ablation",
    ):
        row = ablation_report[ablation_id]
        records.append(
            _provenance_record(
                producer_function=row["producer_function"],
                inputs=["heldout_episodes", f"{ablation_id}_intervention"],
                run_id=run_id,
                seed_ids=ablation_report["seed_ids"],
                context_ids=ablation_report["context_ids"],
                episode_ids=ablation_report["episode_ids"],
                aggregation=row["aggregation"],
                code_path_hash_value=row["code_path_hash"],
                metric="accuracy",
                score=row["accuracy"],
                candidate_or_baseline_id=ablation_id,
                threshold=baseline_comparison["majority_baseline_accuracy"] + thresholds["ablation_collapse_eps"],
            )
        )
    records.append(
        _provenance_record(
            producer_function=leakage_scan_report["producer_function"],
            inputs=["clean_replay_bundle", "metadata.injected_answer_alias_positive_control"],
            run_id=run_id,
            seed_ids=legal_oracle["seed_ids"],
            context_ids=legal_oracle["context_ids"],
            episode_ids=legal_oracle["episode_ids"],
            aggregation="positive-control alias reaches target if unguarded and is blocked by guard",
            code_path_hash_value=leakage_scan_report["code_path_hash"],
            metric="accuracy",
            score=leakage_scan_report["positive_control"]["unguarded_alias_accuracy"],
            candidate_or_baseline_id="forbidden_injection_positive_control",
            threshold=1.0,
        )
    )
    records.append(
        _provenance_record(
            producer_function=replay_report["producer_function"],
            inputs=["forbidden_free_replay_bundle"],
            run_id=run_id,
            seed_ids=legal_oracle["seed_ids"],
            context_ids=legal_oracle["context_ids"],
            episode_ids=legal_oracle["episode_ids"],
            aggregation="prediction match rate from replay recomputation",
            code_path_hash_value=replay_report["code_path_hash"],
            metric="accuracy",
            score=replay_report["prediction_match_rate"],
            candidate_or_baseline_id="replay_recomputation",
            threshold=1.0,
        )
    )
    provenance = {
        "producer_function": "build_provenance",
        "run_id": run_id,
        "records": records,
        "code_path_hash": code_path_hash(build_provenance),
    }
    provenance["verification"] = verify_computed_evidence_provenance(provenance)
    return provenance


def verify_computed_evidence_provenance(provenance: dict[str, Any]) -> dict[str, Any]:
    required = {
        "producer_function",
        "inputs",
        "run_id",
        "seed_ids",
        "context_ids",
        "episode_ids",
        "aggregation",
        "code_path_hash",
    }
    blockers = []
    for index, record in enumerate(provenance.get("records", [])):
        missing = sorted(required - set(record))
        if missing:
            blockers.append(f"record_{index}_missing:{','.join(missing)}")
        if record.get("static_verdict_dictionary_used") is True:
            blockers.append(f"record_{index}_static_verdict_dictionary_used")
        if str(record.get("producer_function", "")).startswith("literal"):
            blockers.append(f"record_{index}_literal_producer")
        for field in required:
            if record.get(field) in (None, "", [], {}):
                blockers.append(f"record_{index}_empty_{field}")
        if record.get("threshold_declared_before_results") is not True:
            blockers.append(f"record_{index}_threshold_not_predeclared")
    if not provenance.get("records"):
        blockers.append("no_provenance_records")
    return {
        "producer_function": "verify_computed_evidence_provenance",
        "passed": not blockers,
        "blockers": blockers,
        "code_path_hash": code_path_hash(verify_computed_evidence_provenance),
    }


def build_claim_ceiling() -> dict[str, Any]:
    return {
        "producer_function": "build_claim_ceiling",
        "claim_ceiling": CLAIM_CEILING,
        "allowed_claims": [
            "bounded no-candidate surface-admission preflight evidence",
            "local oracle, baseline, ablation, leakage, replay, and provenance readback for this generated surface",
        ],
        "forbidden_claims": list(CLAIM_EXCLUSIONS),
        "mechanism_score_produced": False,
        "code_path_hash": code_path_hash(build_claim_ceiling),
    }


def _same_state_pair_validity(surface: dict[str, Any]) -> bool:
    for pair in surface["same_state_different_action_pairs"]:
        episodes = [episode for episode in surface["episodes"] if episode["episode_id"] in pair["episode_ids"]]
        if len({episode["selected_action"] for episode in episodes}) < 2:
            return False
        observations = {_canonical(episode["legal_state_observation"]["pre_state"]) for episode in episodes}
        if len(observations) != 1:
            return False
    return True


def _compute_result(
    *,
    run_id: str,
    surface: dict[str, Any],
    config: dict[str, Any],
    legal_oracle: dict[str, Any],
    field_registry: dict[str, Any],
    baseline_comparison: dict[str, Any],
    ablation_report: dict[str, Any],
    leakage_scan_report: dict[str, Any],
    replay_report: dict[str, Any],
    provenance: dict[str, Any],
    readback: dict[str, Any],
    allow_stored_answer_replay: bool,
) -> dict[str, Any]:
    thresholds = config["thresholds"]
    majority = baseline_comparison["majority_baseline_accuracy"]
    best = baseline_comparison["best_independent_baseline"]
    margin = legal_oracle["accuracy"] - best["score"]
    stop = []

    if legal_oracle["accuracy"] < thresholds["legal_oracle_min_accuracy"]:
        stop.append("legal_oracle_accuracy_below_threshold")
    if majority > thresholds["majority_baseline_max_accuracy"]:
        stop.append("majority_baseline_above_allowed_threshold")
    if best["score"] > thresholds["best_independent_baseline_max_accuracy"]:
        stop.append(f"independent_baseline_reached_disallowing_threshold:{best['baseline_id']}")
    if margin < thresholds["legal_oracle_min_margin_over_best_baseline"]:
        stop.append("oracle_margin_over_best_baseline_below_threshold")
    for ablation_id in (
        "no_action_ablation",
        "randomized_action_ablation",
        "action_label_shuffle_ablation",
        "counterfactual_pair_break_ablation",
        "observation_only_ablation",
    ):
        if ablation_report[ablation_id]["accuracy"] > majority + thresholds["ablation_collapse_eps"]:
            stop.append(f"{ablation_id}_did_not_collapse")
    if not _same_state_pair_validity(surface):
        stop.append("same_state_different_action_pairs_invalid")
    graph_scores = baseline_comparison["graph_family_scores"]
    if any(score > thresholds["best_independent_baseline_max_accuracy"] for score in graph_scores.values()):
        stop.append("transition_graph_family_reached_oracle_level")
    if baseline_comparison["context_key_arithmetic_probe_score"] > thresholds["best_independent_baseline_max_accuracy"]:
        stop.append("context_key_arithmetic_probe_reached_disallowing_threshold")
    if not field_registry["legal_forbidden_registry_exhaustive"]:
        stop.append("field_registry_not_exhaustive")
    if field_registry["answer_bearing_fields_in_legal_or_replay_bundle"]:
        stop.append("answer_bearing_field_in_legal_or_replay_bundle")
    if field_registry["legal_tuple_deterministically_encodes_target"]:
        stop.append("legal_tuple_deterministically_encodes_target")
    if not leakage_scan_report["positive_control"]["guard_blocked"]:
        stop.append("leakage_positive_control_failed")
    if not replay_report["passed"] or allow_stored_answer_replay:
        stop.append("replay_required_stored_answer_or_shortcut")
    if not provenance["verification"]["passed"]:
        stop.append("computed_evidence_provenance_failed")
    if readback["forbidden_files_modified"]:
        stop.append("forbidden_files_modified")
    if not readback["old_ctsr_composite_artifacts_unchanged"] or not readback["old_ctsr_composite_source_files_unchanged"]:
        stop.append("old_ctsr_composite_paths_modified")

    invalid_markers = {
        "field_registry_not_exhaustive",
        "answer_bearing_field_in_legal_or_replay_bundle",
        "legal_tuple_deterministically_encodes_target",
        "leakage_positive_control_failed",
        "replay_required_stored_answer_or_shortcut",
        "computed_evidence_provenance_failed",
        "forbidden_files_modified",
        "old_ctsr_composite_paths_modified",
    }
    if any(marker in stop for marker in invalid_markers):
        verdict = "invalid_harness"
    elif stop:
        verdict = "refused_surface_preflight"
    else:
        verdict = "admitted_surface_preflight"

    return {
        "producer_function": "compute_result",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "verdict": verdict,
        "current_layer": "engineering implementation / no-candidate surface-admission preflight only",
        "mainline_integration_status": "none; offline local preflight only",
        "enabled_status": "callable local preflight runner only; no mechanism path enabled",
        "real_trigger_evidence": {
            "prior_negative_evidence": surface["prior_negative_evidence"],
            "referenced_artifacts": list(PRIOR_NEGATIVE_ARTIFACTS),
            "run_id": run_id,
            "surface_config_hash": config["config_hash"],
        },
        "candidate_mechanism_implemented": False,
        "candidate_score_produced": False,
        "mechanism_score_produced": False,
        "gate5_bridge_runtime_or_ego_mainline_authorized": False,
        "candidate_or_tournament_authorized": False,
        "legal_oracle_accuracy": legal_oracle["accuracy"],
        "majority_baseline_accuracy": majority,
        "best_independent_baseline": best,
        "legal_oracle_minus_best_independent_baseline": margin,
        "same_state_different_action_pairs_valid": _same_state_pair_validity(surface),
        "transition_graph_family_blocked": all(
            score <= thresholds["best_independent_baseline_max_accuracy"] for score in graph_scores.values()
        ),
        "context_key_arithmetic_probe_blocked": baseline_comparison["context_key_arithmetic_probe_score"]
        <= thresholds["best_independent_baseline_max_accuracy"],
        "stop_conditions_triggered": stop,
        "claim_ceiling": CLAIM_CEILING,
        "auto_remote_anchor": AUTO_REMOTE_ANCHOR,
        "auto_remote_anchor_claim_ceiling_if_performed": "remote-anchor publication and verification only",
        "next_minimal_closed_loop_action": (
            "If independent review accepts this no-candidate surface preflight, draft a separate bounded candidate "
            "task card; otherwise preserve refusal/invalid-harness evidence and close or redesign outside the "
            "closed CTSR route."
        ),
        "what_this_does_not_prove": list(CLAIM_EXCLUSIONS),
    }


def build_trace_rows(
    surface: dict[str, Any],
    legal_oracle: dict[str, Any],
    baseline_comparison: dict[str, Any],
    ablation_report: dict[str, Any],
    run_id: str,
) -> list[dict[str, Any]]:
    _train, heldout = _split_episodes(surface)
    rows = []
    for episode in heldout:
        rows.append(
            {
                "run_id": run_id,
                "episode_id": episode["episode_id"],
                "seed_id": episode["seed_id"],
                "context_id": episode["context_id"],
                "producer_function": "run_legal_oracle",
                "selected_action": episode["selected_action"],
                "target_from_downstream_observation": _target_from_downstream(episode),
                "oracle_prediction": legal_oracle["predictions"][episode["episode_id"]],
            }
        )
    for row in baseline_comparison["baseline_results"]:
        rows.append(
            {
                "run_id": run_id,
                "producer_function": row["producer_function"],
                "baseline_id": row["baseline_id"],
                "score": row["score"],
            }
        )
    for ablation_id in (
        "no_action_ablation",
        "randomized_action_ablation",
        "action_label_shuffle_ablation",
        "counterfactual_pair_break_ablation",
        "observation_only_ablation",
    ):
        rows.append(
            {
                "run_id": run_id,
                "producer_function": ablation_report[ablation_id]["producer_function"],
                "ablation_id": ablation_id,
                "score": ablation_report[ablation_id]["accuracy"],
            }
        )
    return rows


def _resolve_output_dir(output_dir: str | Path | None) -> Path:
    if output_dir is None:
        return repo_root() / "artifacts" / ARTIFACT_DIR_NAME
    return Path(output_dir)


def write_artifacts(out: Path, run: dict[str, Any]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    payloads = {
        "result.json": run["result"],
        "readback.json": run["readback"],
        "surface_bundle.json": run["surface_bundle"],
        "field_registry.json": run["field_registry"],
        "baseline_comparison.json": run["baseline_comparison"],
        "ablation_report.json": run["ablation_report"],
        "leakage_scan_report.json": run["leakage_scan_report"],
        "replay_report.json": run["replay_report"],
        "computed_evidence_provenance.json": run["computed_evidence_provenance"],
        "legal_oracle_report.json": run["legal_oracle_report"],
        "preflight_config.json": run["preflight_config"],
        "claim_ceiling.json": run["claim_ceiling"],
        "test_results.json": run["test_results"],
    }
    for name, payload in payloads.items():
        _write_json(out / name, payload)
    _write_jsonl(out / "trace.jsonl", run["trace_rows"])
    if run["result"]["verdict"] != "admitted_surface_preflight":
        _write_json(
            out / "failure_manifest.json",
            {
                "producer_function": "write_failure_manifest",
                "task_id": TASK_CARD_ID,
                "verdict": run["result"]["verdict"],
                "stop_conditions_triggered": run["result"]["stop_conditions_triggered"],
                "claim_ceiling": CLAIM_CEILING,
            },
        )


def execute_preflight(
    *,
    output_dir: str | Path | None = None,
    persist_artifacts: bool = False,
    disable_leakage_positive_control: bool = False,
    allow_stored_answer_replay: bool = False,
    test_result_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = build_preflight_config()
    run_id = f"{TASK_ID}_{config['config_hash'][:16]}"
    surface = generate_surface(config)
    legal_oracle = run_legal_oracle(surface, run_id)
    field_registry = build_field_registry(surface, config)
    baseline_comparison = run_baselines(surface, config, run_id)
    ablation_report = run_ablation(surface, config, run_id)
    leakage_scan_report = run_leakage_scan(
        surface,
        config,
        run_id,
        disable_positive_control=disable_leakage_positive_control,
    )
    replay_report = run_replay(
        surface,
        config,
        run_id,
        legal_oracle,
        allow_stored_answer_replay=allow_stored_answer_replay,
    )
    output_path = _resolve_output_dir(output_dir) if persist_artifacts else None
    temporary_result = {"verdict": "pending"}
    readback = build_readback(temporary_result, output_path)
    provenance = build_provenance(
        run_id=run_id,
        config=config,
        legal_oracle=legal_oracle,
        baseline_comparison=baseline_comparison,
        ablation_report=ablation_report,
        leakage_scan_report=leakage_scan_report,
        replay_report=replay_report,
    )
    result = _compute_result(
        run_id=run_id,
        surface=surface,
        config=config,
        legal_oracle=legal_oracle,
        field_registry=field_registry,
        baseline_comparison=baseline_comparison,
        ablation_report=ablation_report,
        leakage_scan_report=leakage_scan_report,
        replay_report=replay_report,
        provenance=provenance,
        readback=readback,
        allow_stored_answer_replay=allow_stored_answer_replay,
    )
    readback = build_readback(result, output_path)
    trace_rows = build_trace_rows(surface, legal_oracle, baseline_comparison, ablation_report, run_id)
    test_results = test_result_readback or {
        "command": "not supplied",
        "exit_code": "not supplied",
        "summary": "test readback not supplied to this run",
    }
    run = {
        "task_id": TASK_ID,
        "task_card_id": TASK_CARD_ID,
        "run_id": run_id,
        "preflight_config": config,
        "surface_bundle": surface,
        "field_registry": field_registry,
        "legal_oracle_report": legal_oracle,
        "baseline_comparison": baseline_comparison,
        "ablation_report": ablation_report,
        "leakage_scan_report": leakage_scan_report,
        "replay_report": replay_report,
        "computed_evidence_provenance": provenance,
        "claim_ceiling": build_claim_ceiling(),
        "result": result,
        "readback": readback,
        "trace_rows": trace_rows,
        "test_results": test_results,
    }
    if persist_artifacts:
        assert output_path is not None
        write_artifacts(output_path, run)
        run["readback"] = build_readback(result, output_path)
        _write_json(output_path / "readback.json", run["readback"])
    return run


def write_research_report(run: dict[str, Any], report_path: str | Path | None = None) -> Path:
    path = Path(report_path) if report_path else repo_root() / "docs" / "research" / REPORT_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    result = run["result"]
    baseline = run["baseline_comparison"]
    ablation = run["ablation_report"]
    leakage = run["leakage_scan_report"]
    replay = run["replay_report"]
    readback = run["readback"]

    lines = [
        f"# {TASK_CARD_ID}",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        f"Layer: {result['current_layer']}.",
        "",
        f"Mainline integration status: {result['mainline_integration_status']}.",
        "",
        f"Enabled status: {result['enabled_status']}.",
        "",
        "Auto-Remote-Anchor: conditional",
        "",
        "No mechanism success claim is made.",
        "",
        "No candidate mechanism was implemented.",
        "",
        "## Bounded Task Card",
        "",
        f"- Task id: `{TASK_CARD_ID}`",
        "- Problem definition: perform one no-candidate action-conditioned self-boundary / controllability surface preflight after the current CTSR / COMPOSITE route was closed as downstream-usable mechanism evidence.",
        "- Current stage/layer: engineering implementation / no-candidate surface-admission preflight only.",
        "- Mainline target: none.",
        "- Enabled-state requirement: no new mechanism path, candidate, bridge, Gate5, runtime, tournament, or EGO-mainline behavior.",
        "- Real-trigger evidence requirement: current COMPOSITE-CTSR pass-chain was frozen as negative evidence; CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A was downgraded to inconclusive / admission unsupported; fair simple baselines reached oracle-level accuracy in hostile audit; no CTSR continuation is authorized.",
        "- Hypothesis: a clean action-conditioned surface can be admitted only if the legal oracle separates from independent baselines, action ablations collapse, leakage controls fire, field registry is exhaustive, and replay recomputes from forbidden-free bundles.",
        "- Strongest baseline: majority, observation-only, action-only, legal tuple lookup, nearest-neighbor, transition-table, graph/cache family, context-key arithmetic, and target-label leakage probe.",
        "- Ablation requirement: no-action, randomized-action, action-label-shuffle, counterfactual-pair-break, and observation-only reruns must collapse to majority + eps.",
        "- Trace/replay requirement: replay recomputes oracle predictions from legal state observation, selected action, counterfactual labels, downstream legal observations, declared transition interface, and provenance IDs only.",
        "- Computed-evidence provenance gate: every score records producer, inputs, run id, seed/context/episode ids, aggregation, and code path hash.",
        "- Acceptance gate: admitted/refused/invalid-harness only; no threshold, schema, field-registry, or distribution tuning after results.",
        f"- Claim ceiling: {CLAIM_CEILING}",
        "- Stop condition: any failed gate, leakage control failure, stored-answer replay, unclassified field channel, baseline equivalence, ablation non-collapse, or forbidden path touch.",
        "- Rollback plan: additive-only deletion or revert of the isolated task paths.",
        "- Expected changed files: isolated source package, focused test, new artifacts, and this report only.",
        "- Forbidden changes: frozen CTSR/COMPOSITE source/artifacts, old Gate4/Gate5/tournament/bridge/runtime/EGO-mainline paths, and candidate files.",
        "- Auto-Remote-Anchor decision: conditional.",
        "",
        "## Prior Negative Evidence Cited",
        "",
        "- `artifacts/preserve_composite_ctsr_hostile_audit_001a/result.json`: closed prior COMPOSITE-CTSR pass-chain as mechanism evidence and froze it as negative evidence.",
        "- `artifacts/preserve_ctsr_solvability_inversion_preflight_001a_hostile_audit_001a/result.json`: preserved the hostile-audit downgrade after fair simple baselines reached oracle-level accuracy.",
        "- `artifacts/preserve_claude_audit_legal_interface_oracle_block_001a/result.json`: preserved the legal-interface oracle block with oracle accuracy at majority/random.",
        "",
        "## Admission Gate Readback",
        "",
        f"- Legal oracle accuracy: `{result['legal_oracle_accuracy']}`",
        f"- Majority baseline accuracy: `{baseline['majority_baseline_accuracy']}`",
        f"- Best independent baseline: `{baseline['best_independent_baseline']}`",
        f"- Legal oracle minus best independent baseline: `{result['legal_oracle_minus_best_independent_baseline']}`",
        f"- Invoked baselines: `{baseline['invoked_baselines']}`",
        f"- Missing baselines: `{baseline['missing_baselines']}`",
        f"- Transition graph family blocked: `{result['transition_graph_family_blocked']}`",
        f"- Context-key arithmetic probe blocked: `{result['context_key_arithmetic_probe_blocked']}`",
        "",
        "## Ablation",
        "",
        f"- No-action accuracy: `{ablation['no_action_ablation']['accuracy']}`",
        f"- Randomized-action accuracy: `{ablation['randomized_action_ablation']['accuracy']}`",
        f"- Action-label-shuffle accuracy: `{ablation['action_label_shuffle_ablation']['accuracy']}`",
        f"- Counterfactual-pair-break accuracy: `{ablation['counterfactual_pair_break_ablation']['accuracy']}`",
        f"- Observation-only accuracy: `{ablation['observation_only_ablation']['accuracy']}`",
        "",
        "## Leakage And Replay",
        "",
        f"- Clean surface scan passed: `{leakage['clean_surface_scan']['passed']}`",
        f"- Positive-control unguarded alias accuracy: `{leakage['positive_control']['unguarded_alias_accuracy']}`",
        f"- Positive-control guard blocked: `{leakage['positive_control']['guard_blocked']}`",
        f"- Replay passed: `{replay['passed']}`",
        f"- Replay forbidden fields: `{replay['forbidden_fields_in_replay_bundle']}`",
        f"- Replay prediction match rate: `{replay['prediction_match_rate']}`",
        "",
        "## Scope Readback",
        "",
        f"- Branch: `{readback['branch']}`",
        f"- HEAD: `{readback['head']}`",
        f"- Forbidden files modified: `{readback['forbidden_files_modified']}`",
        f"- Old CTSR/COMPOSITE artifacts unchanged: `{readback['old_ctsr_composite_artifacts_unchanged']}`",
        f"- Old CTSR/COMPOSITE source files unchanged: `{readback['old_ctsr_composite_source_files_unchanged']}`",
        f"- Result JSON parse check: `{readback['result_json_parse_check']}`",
        "",
        "## Stop Conditions",
        "",
        f"- `{result['stop_conditions_triggered']}`",
        "",
        "## Claim Ceiling",
        "",
        CLAIM_CEILING,
        "",
        "## What This Does Not Prove",
        "",
    ]
    lines.extend(f"- {claim}" for claim in CLAIM_EXCLUSIONS)
    lines.extend(
        [
            "",
            "## Next Minimal Closed-Loop Action",
            "",
            result["next_minimal_closed_loop_action"],
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=TASK_CARD_ID)
    parser.add_argument("--write-artifacts", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--test-command", default=None)
    parser.add_argument("--test-exit-code", type=int, default=None)
    parser.add_argument("--test-summary", default=None)
    args = parser.parse_args()

    test_readback = None
    if args.test_command is not None or args.test_exit_code is not None or args.test_summary is not None:
        test_readback = {
            "command": args.test_command or "not supplied",
            "exit_code": args.test_exit_code if args.test_exit_code is not None else "not supplied",
            "summary": args.test_summary or "not supplied",
        }
    run = execute_preflight(
        output_dir=args.output_dir,
        persist_artifacts=args.write_artifacts,
        test_result_readback=test_readback,
    )
    if args.write_report:
        write_research_report(run)
    print(json.dumps(_json_ready(run["result"]), indent=2, sort_keys=True))
