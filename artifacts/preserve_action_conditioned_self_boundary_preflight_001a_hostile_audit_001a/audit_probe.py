"""Read-only preservation probe for ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A.

This script parses frozen artifacts and reproduces invalid-harness preservation
metrics. It does not import or execute the frozen preflight runner.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ORIGINAL_ARTIFACT_DIR = ROOT / "artifacts" / "action_conditioned_self_boundary_preflight_001a"
NO_OP_ACTION = "hold_boundary"
ALLOWED_GOVERNANCE_FLAG_FIELDS = {"mechanism_score_produced"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def class_from_delta(dx: int, dy: int) -> str:
    if dx > 0:
        return "x_gain"
    if dx < 0:
        return "x_loss"
    if dy > 0:
        return "y_gain"
    if dy < 0:
        return "y_loss"
    return "no_change"


def target_delta(episode: dict[str, Any]) -> dict[str, int]:
    selected = episode["selected_action"]
    downstream = episode["downstream_legal_observations"]
    selected_post = downstream[selected]["post_state"]
    no_op_post = downstream[NO_OP_ACTION]["post_state"]
    return {
        "dx": selected_post["position_x"] - no_op_post["position_x"],
        "dy": selected_post["position_y"] - no_op_post["position_y"],
    }


def target_from_downstream(episode: dict[str, Any]) -> str:
    delta = target_delta(episode)
    return class_from_delta(delta["dx"], delta["dy"])


def selected_effect(episode: dict[str, Any], action: str | None = None) -> dict[str, int]:
    selected = action or episode["selected_action"]
    return episode["legal_state_observation"]["actuator_effects"][selected]


def oracle_from_effect(episode: dict[str, Any]) -> str:
    effect = selected_effect(episode)
    return class_from_delta(effect["dx"], effect["dy"])


def score(predictions: dict[str, str], episodes: list[dict[str, Any]]) -> float:
    if not episodes:
        return 0.0
    correct = sum(
        1 for episode in episodes if predictions[episode["episode_id"]] == target_from_downstream(episode)
    )
    return correct / len(episodes)


def table_predictions(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    key_fn,
) -> tuple[dict[str, str], int, int, int]:
    tables: dict[Any, Counter[str]] = defaultdict(Counter)
    for episode in train:
        tables[key_fn(episode)][target_from_downstream(episode)] += 1

    majority = Counter(target_from_downstream(episode) for episode in train).most_common(1)[0][0]
    predictions: dict[str, str] = {}
    covered = 0
    for episode in heldout:
        key = key_fn(episode)
        if key in tables:
            covered += 1
            predictions[episode["episode_id"]] = tables[key].most_common(1)[0][0]
        else:
            predictions[episode["episode_id"]] = majority
    return predictions, covered, len(heldout), len(tables)


def flatten_paths(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    rows: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, val in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(flatten_paths(val, path))
    elif isinstance(value, list):
        for index, val in enumerate(value):
            path = f"{prefix}[{index}]"
            rows.extend(flatten_paths(val, path))
    else:
        rows.append((prefix, value))
    return rows


def path_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def protected_hashes() -> dict[str, str]:
    paths = [
        "src/action_conditioned_self_boundary_preflight_001a/__init__.py",
        "src/action_conditioned_self_boundary_preflight_001a/__main__.py",
        "src/action_conditioned_self_boundary_preflight_001a/runner.py",
        "tests/test_action_conditioned_self_boundary_preflight_001a.py",
        "docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A.md",
    ]
    paths.extend(
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in sorted(ORIGINAL_ARTIFACT_DIR.glob("*"))
        if path.is_file()
    )
    return {path: sha256_file(ROOT / path) for path in sorted(paths)}


def main() -> None:
    surface = load_json(ORIGINAL_ARTIFACT_DIR / "surface_bundle.json")
    result = load_json(ORIGINAL_ARTIFACT_DIR / "result.json")
    baseline = load_json(ORIGINAL_ARTIFACT_DIR / "baseline_comparison.json")
    field_registry = load_json(ORIGINAL_ARTIFACT_DIR / "field_registry.json")
    leakage = load_json(ORIGINAL_ARTIFACT_DIR / "leakage_scan_report.json")
    replay = load_json(ORIGINAL_ARTIFACT_DIR / "replay_report.json")

    train = [episode for episode in surface["episodes"] if episode["split"] == "train"]
    heldout = [episode for episode in surface["episodes"] if episode["split"] == "heldout"]

    effect_vector_predictions = {episode["episode_id"]: oracle_from_effect(episode) for episode in heldout}
    sensor_phase_action_predictions, sensor_phase_action_covered, sensor_phase_action_total, sensor_phase_action_keys = (
        table_predictions(
            train,
            heldout,
            lambda episode: (
                episode["legal_state_observation"]["pre_state"]["sensor_phase"],
                episode["selected_action"],
            ),
        )
    )
    sensor_phase_index_predictions, sensor_phase_index_covered, sensor_phase_index_total, sensor_phase_index_keys = (
        table_predictions(
            train,
            heldout,
            lambda episode: (
                episode["legal_state_observation"]["pre_state"]["sensor_phase"],
                episode["metadata"]["action_index"],
            ),
        )
    )

    injected = deepcopy(surface)
    benign_predictions: dict[str, str] = {}
    for episode in injected["episodes"]:
        episode["legal_state_observation"]["controllability_outlook"] = target_from_downstream(episode)
    for episode in [row for row in injected["episodes"] if row["split"] == "heldout"]:
        benign_predictions[episode["episode_id"]] = episode["legal_state_observation"]["controllability_outlook"]

    forbidden_fragments = set(field_registry["forbidden_field_fragments"])
    benign_forbidden_paths = []
    for path, _value in flatten_paths(injected):
        leaf = path.lower().rsplit(".", 1)[-1]
        if leaf in ALLOWED_GOVERNANCE_FLAG_FIELDS:
            continue
        if any(fragment in path.lower() for fragment in forbidden_fragments):
            benign_forbidden_paths.append(path)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for episode in surface["episodes"]:
        grouped[episode["same_state_group"]].append(episode)

    pre_state_equal = True
    context_ids_vary = True
    action_index_determines_target = True
    for rows in grouped.values():
        pre_states = {path_key(episode["legal_state_observation"]["pre_state"]) for episode in rows}
        pre_state_equal = pre_state_equal and len(pre_states) == 1
        context_ids_vary = context_ids_vary and len({episode["context_id"] for episode in rows}) > 1
        index_targets: dict[int, set[str]] = defaultdict(set)
        for episode in rows:
            index_targets[episode["metadata"]["action_index"]].add(target_from_downstream(episode))
        action_index_determines_target = action_index_determines_target and all(
            len(targets) == 1 for targets in index_targets.values()
        )

    effect_vector_accuracy = score(effect_vector_predictions, heldout)
    sensor_phase_action_accuracy = score(sensor_phase_action_predictions, heldout)
    sensor_phase_index_accuracy = score(sensor_phase_index_predictions, heldout)
    fair_best = max(
        result["best_independent_baseline"]["score"],
        effect_vector_accuracy,
        sensor_phase_action_accuracy,
        sensor_phase_index_accuracy,
    )

    output = {
        "source": "read-only parse of frozen action-conditioned source artifacts",
        "runner_imported": False,
        "runner_executed": False,
        "original_task_id": result["task_id"],
        "original_verdict": result["verdict"],
        "preserved_audit_verdict": "invalid_harness",
        "legal_oracle_accuracy": result["legal_oracle_accuracy"],
        "reported_best_independent_baseline": result["best_independent_baseline"],
        "reported_margin": result["legal_oracle_minus_best_independent_baseline"],
        "oracle_equals_target_all_episodes": all(
            oracle_from_effect(episode) == target_from_downstream(episode)
            for episode in surface["episodes"]
        ),
        "no_op_effect_zero_all_episodes": all(
            selected_effect(episode, NO_OP_ACTION) == {"dx": 0, "dy": 0}
            for episode in surface["episodes"]
        ),
        "target_delta_equals_selected_effect_all_episodes": all(
            target_delta(episode) == selected_effect(episode)
            for episode in surface["episodes"]
        ),
        "effect_vector_lookup_accuracy": effect_vector_accuracy,
        "sensor_phase_x_selected_action_accuracy": sensor_phase_action_accuracy,
        "sensor_phase_x_selected_action_heldout_key_coverage": (
            f"{sensor_phase_action_covered}/{sensor_phase_action_total}"
        ),
        "sensor_phase_x_selected_action_train_keys": sensor_phase_action_keys,
        "sensor_phase_x_action_index_accuracy": sensor_phase_index_accuracy,
        "sensor_phase_x_action_index_heldout_key_coverage": (
            f"{sensor_phase_index_covered}/{sensor_phase_index_total}"
        ),
        "sensor_phase_x_action_index_train_keys": sensor_phase_index_keys,
        "margin_if_fair_baseline_included": result["legal_oracle_accuracy"] - fair_best,
        "same_state_group_pre_state_equal": pre_state_equal,
        "same_state_group_context_ids_vary": context_ids_vary,
        "same_state_group_action_index_determines_target": action_index_determines_target,
        "field_registry_legal_tuple_deterministically_encodes_target": field_registry[
            "legal_tuple_deterministically_encodes_target"
        ],
        "field_registry_answer_bearing_fields": field_registry[
            "answer_bearing_fields_in_legal_or_replay_bundle"
        ],
        "field_registry_forbidden_registry_exhaustive": field_registry[
            "legal_forbidden_registry_exhaustive"
        ],
        "clean_leakage_scan_passed": leakage["clean_surface_scan"]["passed"],
        "name_fragment_positive_control_guard_blocked": leakage["positive_control"]["guard_blocked"],
        "benign_named_answer_alias_path": "legal_state_observation.controllability_outlook",
        "benign_named_answer_alias_forbidden_paths": sorted(set(benign_forbidden_paths)),
        "benign_named_answer_alias_scan_passed": len(benign_forbidden_paths) == 0,
        "benign_named_answer_alias_accuracy": score(benign_predictions, heldout),
        "replay_passed": replay["passed"],
        "replay_prediction_match_rate": replay["prediction_match_rate"],
        "replay_recomputed_from_forbidden_free_bundle": replay[
            "recomputed_from_forbidden_free_bundle"
        ],
        "invoked_baselines": baseline["invoked_baselines"],
        "protected_file_hashes": protected_hashes(),
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
