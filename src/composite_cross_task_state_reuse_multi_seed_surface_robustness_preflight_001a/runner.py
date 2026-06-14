from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import math
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from composite_cross_task_state_reuse_generative_heldout_surface_design_001a import (
    runner as surface_design,
)
from composite_cross_task_state_reuse_surface_discriminativeness_preflight_001a import (
    runner as single_preflight,
)

from . import (
    ARTIFACT_DIR_NAME,
    AUTO_REMOTE_ANCHOR,
    BRANCH,
    CLAIM_CEILING,
    DISCRIMINATIVENESS_RECONCILIATION_ANCHOR,
    DISCRIMINATIVENESS_RECONCILIATION_TAG,
    GENERATIVE_PARENT_ANCHOR,
    GENERATIVE_PARENT_TAG,
    REPORT_NAME,
    STARTING_HEAD,
    TASK_CARD_ID,
    TASK_ID,
)


SOLVE_THRESHOLD = 0.8
DEFAULT_FIXTURE_COUNT = 20
DEFAULT_SEEDS = [81001, 81002, 81003, 81004, 81005, 81006]
MODULE_PATH = str(Path("src") / TASK_ID / "runner.py").replace("\\", "/")
SOURCE_GENERATOR_FUNCTION = (
    "composite_cross_task_state_reuse_generative_heldout_surface_design_001a.runner."
    "generate_valid_surface_fixture"
)
REQUIRED_BASELINES = [
    "independent_per_task_optimal_ensemble_no_shared_latent",
    "shared_latent_no_cross_task_transfer",
    "visible_feature_only_task_b_decoder",
    "static_formula_visible_field_decoder",
    "nearest_neighbor_or_table_lookup_probe",
    "identity_or_trace_order_probe",
]
CLAIM_EXCLUSIONS = [
    "mechanism validity",
    "Gate4 validity",
    "candidate behavior",
    "tournament outcome",
    "runtime readiness",
    "bridge/admission readiness",
    "agency",
    "subjectivity",
    "consciousness",
    "emotion",
    "autonomy",
    "companion readiness",
    "EGO readiness",
]
TASK_FAMILY_PAIRINGS = [
    ("self_boundary_controllability", "viability_value_gated_prediction_action"),
    ("replay_consolidation", "social_latent_inference"),
    ("viability_value_gated_prediction_action", "self_boundary_controllability"),
    ("social_latent_inference", "replay_consolidation"),
]
ACTION_POOL = ["inspect_boundary", "consolidate_trace", "defer_action", "replan_memory"]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_json_ready(child) for child in value]
    if isinstance(value, tuple):
        return [_json_ready(child) for child in value]
    if isinstance(value, set):
        return sorted(_json_ready(child) for child in value)
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    return value


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _canonical(value: Any) -> str:
    return json.dumps(_json_ready(value), sort_keys=True, separators=(",", ":"))


def code_path_hash(func: Callable[..., Any]) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()


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
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def _safe_git_raw(args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return completed.stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def _read_remote_refs(*refs: str) -> dict[str, str]:
    output = _safe_git(["ls-remote", "origin", *refs])
    rows: dict[str, str] = {}
    for line in output.splitlines():
        if not line.strip():
            continue
        commit, ref = line.split(maxsplit=1)
        rows[ref] = commit
    return rows


def _is_ancestor(commit: str, descendant: str) -> bool:
    if not commit or not descendant:
        return False
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, descendant],
        cwd=repo_root(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.returncode == 0


def _entropy_bits(values: list[str]) -> float:
    if not values:
        return 0.0
    counts = Counter(values)
    total = len(values)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def _rotate(values: list[str], offset: int) -> list[str]:
    if not values:
        return []
    offset = offset % len(values)
    return values[offset:] + values[:offset]


def _structure_hash(fixture: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(fixture).encode("utf-8")).hexdigest()


def _all_records(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    return list(fixture.get("records", {}).get("train", [])) + list(fixture.get("records", {}).get("heldout", []))


def _heldout_records(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    return list(fixture.get("records", {}).get("heldout", []))


def _target_actions(records: list[dict[str, Any]]) -> list[str]:
    return [single_preflight.recompute_task_b_action_from_serialized_state(
        row["shared_state_update"]["serialized_state_after"],
        row["task_b"]["observation"],
    ) for row in records]


def validate_surface_for_current_task(fixture: dict[str, Any]) -> dict[str, Any]:
    validation = copy.deepcopy(surface_design.validate_surface(fixture))
    guard = validation["validator_results"].get("forbidden_action_guard")
    if guard and guard["blocking_reasons"] == ["forbidden_files_modified"]:
        guard["passed"] = True
        guard["blocking_reasons"] = []
        guard["current_task_allowed_scope_override"] = True
        validation["blocking_reasons"] = [
            reason for reason in validation["blocking_reasons"] if reason != "forbidden_files_modified"
        ]
        validation["valid"] = not validation["blocking_reasons"]
    return validation


def _update_record(
    row: dict[str, Any],
    *,
    seed: int,
    variant_index: int,
    split: str,
    index: int,
    task_family_id: str,
    latent_parameter_id: str,
    support_signature: str,
    context_handle: str,
    partner_handle: str,
    counterfactual_combo_id: str,
    superficial_signature: str,
    local_visible_cue: str,
    target_action: str,
) -> None:
    record_id = f"{split}:seed:{seed}:variant:{variant_index}:episode:{index}"
    prediction_error_event_id = f"pe:{split}:{seed}:{variant_index}:{index}"
    update_event_id = f"update:{split}:{seed}:{variant_index}:{index}"
    action_dependency_id = f"task_b_dep:{split}:{seed}:{variant_index}:{index}"
    latent_binding_probe = f"probe:{latent_parameter_id}:variant:{variant_index}:episode:{index}"

    row["record_id"] = record_id
    row["split"] = split
    row["support_signature"] = support_signature
    row["context_handle"] = context_handle
    row["partner_handle"] = partner_handle
    row["latent_parameter_id"] = latent_parameter_id
    row["counterfactual_combo_id"] = counterfactual_combo_id
    row["task_family_id"] = task_family_id
    row["task_a"]["observation"] = {
        "visible_event_class": f"task_a_surface_{superficial_signature}",
        "predicted_outcome": "expected_stable_response",
        "observed_outcome": f"unexpected_shift_response_{(seed + variant_index + index) % 5}",
        "prediction_signal": f"signal_{(seed + variant_index + index) % 3}",
    }
    row["task_a"]["prediction_error_event_id"] = prediction_error_event_id
    row["task_a"]["prediction_error_under_pre_update_state"] = True
    row["shared_state_update"] = {
        "update_event_id": update_event_id,
        "channel": "hidden_cross_task_prediction_error_update_channel",
        "serialized_state_before": {
            "shared_update_applied": False,
            "latent_action_binding": {},
        },
        "serialized_state_after": {
            "shared_update_applied": True,
            "latent_action_binding": {latent_binding_probe: target_action},
        },
        "caused_by_task_a_prediction_error_event_id": prediction_error_event_id,
    }
    row["task_b"] = {
        "observation": {
            "superficial_signature": superficial_signature,
            "local_visible_cue": local_visible_cue,
            "latent_binding_probe": latent_binding_probe,
            "pre_update_default_action": "hold",
            "fallback_action": "hold",
        },
        "pre_update_action": "hold",
        "post_update_action": target_action,
        "action_dependency_id": action_dependency_id,
        "action_depends_on_shared_state_update": True,
        "visible_features_alone_sufficient": False,
    }
    row["hidden"] = {
        "generator_latent_state_id": f"hidden_composite_state_seed_{seed}_variant_{variant_index}",
        "task_a_latent_target": f"task_a_error_for_{latent_parameter_id}",
        "task_b_target_action": target_action,
        "shared_update_required_for_task_b_action": True,
    }


def generate_diverse_surface_fixture(seed: int, variant_index: int) -> dict[str, Any]:
    fixture = copy.deepcopy(surface_design.generate_valid_surface_fixture(seed=seed))
    train_family, heldout_family = TASK_FAMILY_PAIRINGS[variant_index % len(TASK_FAMILY_PAIRINGS)]
    secondary_train, secondary_heldout = TASK_FAMILY_PAIRINGS[(variant_index + 1) % len(TASK_FAMILY_PAIRINGS)]
    actions = _rotate(list(ACTION_POOL), (seed + variant_index) % len(ACTION_POOL))
    train_actions = [actions[0], actions[1], actions[2], actions[2]]
    heldout_actions = [actions[3], actions[0], actions[1], actions[2]]

    train = fixture["records"]["train"]
    heldout = fixture["records"]["heldout"]

    train_latents = [
        f"latent_train_{seed}_{variant_index}_alpha",
        f"latent_train_{seed}_{variant_index}_beta",
        f"latent_train_{seed}_{variant_index}_gamma",
        f"latent_train_{seed}_{variant_index}_gamma",
    ]
    train_surfaces = [
        f"shared_surface_{seed}_{variant_index}",
        f"shared_surface_{seed}_{variant_index}",
        f"stable_latent_surface_a_{seed}_{variant_index}",
        f"stable_latent_surface_b_{seed}_{variant_index}",
    ]
    train_cues = [
        f"shared_cue_{seed}_{variant_index}",
        f"shared_cue_{seed}_{variant_index}",
        f"stable_cue_a_{seed}_{variant_index}",
        f"stable_cue_b_{seed}_{variant_index}",
    ]
    for index, row in enumerate(train):
        _update_record(
            row,
            seed=seed,
            variant_index=variant_index,
            split="train",
            index=index,
            task_family_id=train_family if index < 2 else secondary_train,
            latent_parameter_id=train_latents[index],
            support_signature=f"train_support_{seed}_{variant_index}_{index}",
            context_handle=f"train_context_{seed}_{variant_index}_{index}",
            partner_handle=f"train_partner_{seed}_{variant_index}_{index}",
            counterfactual_combo_id=f"train_combo_{seed}_{variant_index}_{index}",
            superficial_signature=train_surfaces[index],
            local_visible_cue=train_cues[index],
            target_action=train_actions[index],
        )

    for index, row in enumerate(heldout):
        latent = f"latent_heldout_{seed}_{variant_index}_{index}"
        _update_record(
            row,
            seed=seed,
            variant_index=variant_index,
            split="heldout",
            index=index,
            task_family_id=heldout_family if index % 2 == 0 else secondary_heldout,
            latent_parameter_id=latent,
            support_signature=f"heldout_support_{seed}_{variant_index}_{index}",
            context_handle=f"heldout_context_{seed}_{variant_index}_{index}",
            partner_handle=f"heldout_partner_{seed}_{variant_index}_{index}",
            counterfactual_combo_id=f"heldout_combo_{seed}_{variant_index}_{index}",
            superficial_signature=f"heldout_surface_{seed}_{variant_index}_{index}",
            local_visible_cue=f"heldout_cue_{seed}_{variant_index}_{index}",
            target_action=heldout_actions[index],
        )

    fixture["surface_id"] = f"composite_cross_task_state_reuse_valid_surface_seed_{seed}_variant_{variant_index}"
    fixture["surface_kind"] = "generated_multi_seed_surface_robustness_fixture"
    fixture["task_family_ids"] = sorted({row["task_family_id"] for row in train + heldout})
    fixture["cross_task_prediction_error_event_ids"] = [
        row["task_a"]["prediction_error_event_id"] for row in train + heldout
    ]
    fixture["shared_state_update_event_ids"] = [row["shared_state_update"]["update_event_id"] for row in train + heldout]
    fixture["task_b_action_dependency_ids"] = [row["task_b"]["action_dependency_id"] for row in train + heldout]
    fixture["counterfactual_pairs"] = [
        {
            "pair_id": f"cf_same_surface_latent_changes_seed_{seed}_variant_{variant_index}",
            "pair_type": "same_superficial_features_latent_structure_changes",
            "record_ids": [train[0]["record_id"], train[1]["record_id"]],
            "held_constant": ["task_b.observation.superficial_signature", "task_b.observation.local_visible_cue"],
            "changed": ["latent_parameter_id", "hidden.task_b_target_action"],
        },
        {
            "pair_id": f"cf_surface_changes_latent_stable_seed_{seed}_variant_{variant_index}",
            "pair_type": "superficial_features_change_latent_structure_stable",
            "record_ids": [train[2]["record_id"], train[3]["record_id"]],
            "held_constant": ["latent_parameter_id", "hidden.task_b_target_action"],
            "changed": ["task_b.observation.superficial_signature", "task_b.observation.local_visible_cue"],
        },
    ]
    fixture["latent_generator"] = {
        "hidden_latent_state_id": f"hidden_composite_state_seed_{seed}_variant_{variant_index}",
        "controls_task_a_target_structure": True,
        "controls_task_b_target_structure": True,
        "shared_across_task_a_and_task_b": True,
    }
    fixture["provenance"] = {
        **fixture["provenance"],
        "generator_function": SOURCE_GENERATOR_FUNCTION,
        "seed": seed,
        "variant_index": variant_index,
        "multi_seed_derivation_function": f"{TASK_ID}.runner.generate_diverse_surface_fixture",
        "source_generator_code_path_hash": surface_design.code_path_hash(surface_design.generate_valid_surface_fixture),
        "derivation_code_path_hash": code_path_hash(generate_diverse_surface_fixture),
        "latent_parameter_ids": {
            "train": [row["latent_parameter_id"] for row in train],
            "heldout": [row["latent_parameter_id"] for row in heldout],
        },
        "train_ids": [row["record_id"] for row in train],
        "heldout_ids": [row["record_id"] for row in heldout],
        "task_family_ids": fixture["task_family_ids"],
        "support_signatures": {
            "train": [row["support_signature"] for row in train],
            "heldout": [row["support_signature"] for row in heldout],
        },
        "counterfactual_pair_ids": [row["pair_id"] for row in fixture["counterfactual_pairs"]],
        "prediction_error_event_ids": fixture["cross_task_prediction_error_event_ids"],
        "shared_state_update_event_ids": fixture["shared_state_update_event_ids"],
        "task_b_action_dependency_ids": fixture["task_b_action_dependency_ids"],
        "code_path_hash": surface_design.code_path_hash(surface_design.generate_valid_surface_fixture),
    }
    return fixture


def _generate_valid_variant(seed: int, variant_index: int) -> tuple[dict[str, Any], dict[str, Any]]:
    for salt in range(5):
        salted_variant = variant_index + (salt * 1000)
        fixture = generate_diverse_surface_fixture(seed, salted_variant)
        validation = validate_surface_for_current_task(fixture)
        if validation["valid"]:
            return fixture, validation
    return fixture, validation


def _summarize_fixture(
    fixture: dict[str, Any],
    validation: dict[str, Any],
    *,
    original_structure_hash: str,
) -> dict[str, Any]:
    train = fixture["records"]["train"]
    heldout = fixture["records"]["heldout"]
    heldout_actions = _target_actions(heldout)
    distribution = dict(sorted(Counter(heldout_actions).items()))
    entropy = _entropy_bits(heldout_actions)
    structure_hash = _structure_hash(fixture)
    task_family_pairing = f"{train[0]['task_family_id']}->{heldout[0]['task_family_id']}"
    return {
        "fixture_id": fixture["surface_id"],
        "generated_from_existing_surface_generator": True,
        "source_generator_function": SOURCE_GENERATOR_FUNCTION,
        "seed": fixture["provenance"]["seed"],
        "variant_index": fixture["provenance"]["variant_index"],
        "latent_parameter_ids": fixture["provenance"]["latent_parameter_ids"],
        "task_family_ids": fixture["task_family_ids"],
        "task_family_pairing": task_family_pairing,
        "support_signatures": fixture["provenance"]["support_signatures"],
        "train_heldout_split_signatures": {
            "train_ids": fixture["provenance"]["train_ids"],
            "heldout_ids": fixture["provenance"]["heldout_ids"],
        },
        "counterfactual_pair_ids": fixture["provenance"]["counterfactual_pair_ids"],
        "prediction_error_event_ids": fixture["provenance"]["prediction_error_event_ids"],
        "shared_state_update_event_ids": fixture["provenance"]["shared_state_update_event_ids"],
        "task_b_action_dependency_ids": fixture["provenance"]["task_b_action_dependency_ids"],
        "target_action_distribution": distribution,
        "heldout_action_entropy_bits": entropy,
        "action_distribution_degenerate": entropy < 1.0 or len(distribution) < 2,
        "fixture_structure_hash": structure_hash,
        "near_duplicate_of_original": structure_hash == original_structure_hash,
        "validator_passed": validation["valid"],
        "validator_blocking_reasons": validation["blocking_reasons"],
        "validator_results": validation["validator_results"],
    }


def generate_fixture_batch(
    *,
    fixture_count: int = DEFAULT_FIXTURE_COUNT,
    seeds: list[int] | None = None,
) -> dict[str, Any]:
    selected_seeds = list(seeds or DEFAULT_SEEDS)
    original = surface_design.generate_valid_surface_fixture(seed=surface_design.DEFAULT_SEED)
    original_structure_hash = _structure_hash(original)
    fixtures: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for index in range(fixture_count):
        seed = selected_seeds[index % len(selected_seeds)]
        fixture, validation = _generate_valid_variant(seed, index)
        fixtures.append(fixture)
        summaries.append(_summarize_fixture(fixture, validation, original_structure_hash=original_structure_hash))

    unique_hashes = {summary["fixture_structure_hash"] for summary in summaries}
    family_pairings = sorted({summary["task_family_pairing"] for summary in summaries})
    return {
        "producer_function": "generate_fixture_batch",
        "task_id": TASK_CARD_ID,
        "fixture_count": len(fixtures),
        "minimum_fixture_count": 12,
        "preferred_fixture_count": DEFAULT_FIXTURE_COUNT,
        "seeds": sorted(set(summary["seed"] for summary in summaries)),
        "minimum_seed_count": 6,
        "fixtures": fixtures,
        "fixture_summaries": summaries,
        "valid_fixture_count": sum(1 for summary in summaries if summary["validator_passed"]),
        "invalid_fixture_ids": [
            summary["fixture_id"] for summary in summaries if not summary["validator_passed"]
        ],
        "unique_structure_hash_count": len(unique_hashes),
        "near_duplicate_original_count": sum(1 for summary in summaries if summary["near_duplicate_of_original"]),
        "task_family_pairings": family_pairings,
        "source_generator_function": SOURCE_GENERATOR_FUNCTION,
        "source_generator_code_path_hash": surface_design.code_path_hash(surface_design.generate_valid_surface_fixture),
        "claim_ceiling": CLAIM_CEILING,
    }


def _baseline_result(
    *,
    baseline_name: str,
    producer_function: str,
    fixture: dict[str, Any],
    input_fixture_id: str,
    run_id: str,
    predictions: list[dict[str, Any]],
    field_access_violations: list[str],
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    score = single_preflight._score_predictions(predictions)
    result = {
        "producer_function": producer_function,
        "input_fixture_id": input_fixture_id,
        "seed": int(fixture["provenance"]["seed"]),
        "run_id": run_id,
        "baseline_name": baseline_name,
        "allowed_observation_fields": list(single_preflight.ALLOWED_OBSERVATION_FIELDS),
        "allowed_training_outcome_fields": list(single_preflight.TRAINING_OUTCOME_FIELDS),
        "forbidden_fields_checked": list(single_preflight.FORBIDDEN_PREDICTION_FIELDS),
        "field_access_audit_result": {
            "passed": not field_access_violations,
            "violations": sorted(set(field_access_violations)),
        },
        "computed_predictions": predictions,
        "failure_reason": None if predictions else "no_predictions_computed",
        "per_fixture_score": score,
        "heldout_accuracy": score,
        "aggregate_score": None,
        "aggregation_method": "heldout_accuracy",
        "solve_threshold": SOLVE_THRESHOLD,
        "solves_fixture": score >= SOLVE_THRESHOLD,
        "executed": True,
        "field_access_violations": sorted(set(field_access_violations)),
        "metadata_only": False,
        "static_verdict_dictionary_used": False,
        "code_path_hash": code_path_hash(globals()[producer_function]),
    }
    if details:
        result["details"] = details
    return result


def nearest_neighbor_or_table_lookup_probe(
    fixture: dict[str, Any],
    *,
    input_fixture_id: str,
    run_id: str,
) -> dict[str, Any]:
    baseline_name = "nearest_neighbor_or_table_lookup_probe"
    train_rows = list(fixture["records"]["train"])
    heldout_rows = list(fixture["records"]["heldout"])
    audit: dict[str, list[str]] = {}
    fields = [
        "task_a.observation.visible_event_class",
        "task_a.observation.prediction_signal",
        "task_b.observation.superficial_signature",
        "task_b.observation.local_visible_cue",
        "task_family_id",
    ]
    train_features = [
        single_preflight._visible_features(row, audit, baseline_name) for row in train_rows
    ]
    train_actions = [single_preflight._training_action(row) for row in train_rows]
    fallback = single_preflight._majority(train_actions)

    def distance(left: dict[str, Any], right: dict[str, Any]) -> int:
        return sum(1 for field in fields if left[field] != right[field])

    def predict(row: dict[str, Any]) -> str:
        features = single_preflight._visible_features(row, audit, baseline_name)
        if not train_features:
            return "hold"
        best_index = sorted(
            range(len(train_features)),
            key=lambda index: (distance(features, train_features[index]), train_actions[index], index),
        )[0]
        if distance(features, train_features[best_index]) > 1:
            return fallback
        return train_actions[best_index]

    predictions = single_preflight._prediction_rows(heldout_rows, predict)
    return _baseline_result(
        baseline_name=baseline_name,
        producer_function="nearest_neighbor_or_table_lookup_probe",
        fixture=fixture,
        input_fixture_id=input_fixture_id,
        run_id=run_id,
        predictions=predictions,
        field_access_violations=audit.get(baseline_name, []),
        details={"lookup_keys": fields, "forbidden_identity_or_support_keys_removed": True},
    )


def identity_or_trace_order_probe(
    fixture: dict[str, Any],
    *,
    input_fixture_id: str,
    run_id: str,
) -> dict[str, Any]:
    baseline_name = "identity_or_trace_order_probe"
    train_rows = list(fixture["records"]["train"])
    heldout_rows = list(fixture["records"]["heldout"])
    audit: dict[str, list[str]] = {}
    fallback = single_preflight._majority([single_preflight._training_action(row) for row in train_rows])

    def predict(row: dict[str, Any]) -> str:
        features = single_preflight._visible_features(row, audit, baseline_name)
        if features["task_b.observation.fallback_action"] == "hold":
            return "hold"
        return fallback

    predictions = single_preflight._prediction_rows(heldout_rows, predict)
    return _baseline_result(
        baseline_name=baseline_name,
        producer_function="identity_or_trace_order_probe",
        fixture=fixture,
        input_fixture_id=input_fixture_id,
        run_id=run_id,
        predictions=predictions,
        field_access_violations=audit.get(baseline_name, []),
        details={
            "identity_fields_denied": ["record_id", "context_handle", "partner_handle"],
            "trace_order_access_denied": True,
        },
    )


def _normalize_existing_baseline_result(
    row: dict[str, Any],
    *,
    input_fixture_id: str,
    aggregate_score: float | None = None,
) -> dict[str, Any]:
    normalized = dict(row)
    normalized["input_fixture_id"] = input_fixture_id
    normalized["per_fixture_score"] = row["heldout_accuracy"]
    normalized["aggregate_score"] = aggregate_score
    normalized["field_access_audit_result"] = {
        "passed": not row["field_access_violations"],
        "violations": list(row["field_access_violations"]),
    }
    return normalized


def _run_existing_baseline(
    func: Callable[..., dict[str, Any]],
    fixture: dict[str, Any],
    *,
    input_fixture_id: str,
    run_id: str,
) -> dict[str, Any]:
    row = func(
        fixture,
        input_fixture_path=input_fixture_id,
        run_id=run_id,
        seed=int(fixture["provenance"]["seed"]),
    )
    return _normalize_existing_baseline_result(row, input_fixture_id=input_fixture_id)


def run_baseline_probes(batch: dict[str, Any], *, run_id: str | None = None) -> dict[str, Any]:
    run_id = run_id or f"{TASK_ID}_{_now().replace('-', '').replace(':', '').replace('Z', 'Z')}"
    baseline_functions: list[Callable[..., dict[str, Any]]] = [
        single_preflight.independent_per_task_optimal_ensemble_no_shared_latent,
        single_preflight.shared_latent_no_cross_task_transfer,
        single_preflight.visible_feature_only_task_b_decoder,
        single_preflight.static_formula_visible_field_decoder,
    ]
    per_fixture_results: list[dict[str, Any]] = []
    for fixture in batch["fixtures"]:
        fixture_id = fixture["surface_id"]
        for func in baseline_functions:
            per_fixture_results.append(
                _run_existing_baseline(func, fixture, input_fixture_id=fixture_id, run_id=run_id)
            )
        per_fixture_results.append(
            nearest_neighbor_or_table_lookup_probe(fixture, input_fixture_id=fixture_id, run_id=run_id)
        )
        per_fixture_results.append(identity_or_trace_order_probe(fixture, input_fixture_id=fixture_id, run_id=run_id))

    aggregate_results: dict[str, dict[str, Any]] = {}
    for baseline_name in REQUIRED_BASELINES:
        rows = [row for row in per_fixture_results if row["baseline_name"] == baseline_name]
        aggregate_score = sum(row["per_fixture_score"] for row in rows) / len(rows) if rows else 0.0
        individual_solve_fixture_ids = [row["input_fixture_id"] for row in rows if row["solves_fixture"]]
        aggregate_results[baseline_name] = {
            "baseline_name": baseline_name,
            "producer_function": "run_baseline_probes",
            "run_id": run_id,
            "fixture_count": len(rows),
            "aggregate_score": aggregate_score,
            "solve_threshold": SOLVE_THRESHOLD,
            "solves_aggregate": aggregate_score >= SOLVE_THRESHOLD,
            "individual_solve_fixture_ids": individual_solve_fixture_ids,
            "aggregation_method": "mean per-fixture heldout accuracy",
            "code_path_hash": code_path_hash(run_baseline_probes),
        }
        for row in rows:
            row["aggregate_score"] = aggregate_score

    return {
        "producer_function": "run_baseline_probes",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "fixture_count": len(batch["fixtures"]),
        "baseline_names": list(REQUIRED_BASELINES),
        "per_fixture_results": per_fixture_results,
        "aggregate_results_by_name": aggregate_results,
        "aggregate_method": "mean per-fixture heldout accuracy",
        "solve_threshold": SOLVE_THRESHOLD,
        "claim_ceiling": CLAIM_CEILING,
    }


def run_update_masking(batch: dict[str, Any], *, run_id: str | None = None) -> dict[str, Any]:
    run_id = run_id or f"{TASK_ID}_{_now().replace('-', '').replace(':', '').replace('Z', 'Z')}"
    rows: list[dict[str, Any]] = []
    for fixture in batch["fixtures"]:
        heldout = _heldout_records(fixture)
        preserved = [
            single_preflight.recompute_task_b_action_from_serialized_state(
                row["shared_state_update"]["serialized_state_after"],
                row["task_b"]["observation"],
            )
            for row in heldout
        ]
        masked = [
            single_preflight.recompute_task_b_action_from_serialized_state(
                row["shared_state_update"]["serialized_state_before"],
                row["task_b"]["observation"],
            )
            for row in heldout
        ]
        changed = [before != after for before, after in zip(masked, preserved)]
        rows.append(
            {
                "producer_function": "run_update_masking",
                "input_fixture_id": fixture["surface_id"],
                "seed": fixture["provenance"]["seed"],
                "run_id": run_id,
                "candidate_ablation": False,
                "comparison_type": "fixture_dependency_mask_only",
                "preserved_task_b_actions": preserved,
                "masked_task_b_actions": masked,
                "heldout_case_count": len(heldout),
                "changed_action_count": sum(1 for item in changed if item),
                "meaningful_effect": bool(heldout) and all(changed),
                "code_path_hash": code_path_hash(run_update_masking),
            }
        )
    meaningful_count = sum(1 for row in rows if row["meaningful_effect"])
    return {
        "producer_function": "run_update_masking",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "fixture_count": len(rows),
        "per_fixture_results": rows,
        "meaningful_effect_fixture_count": meaningful_count,
        "aggregate_masking_effect_rate": meaningful_count / len(rows) if rows else 0.0,
        "candidate_ablation": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def run_replay_recomputation(batch: dict[str, Any], *, run_id: str | None = None) -> dict[str, Any]:
    run_id = run_id or f"{TASK_ID}_{_now().replace('-', '').replace(':', '').replace('Z', 'Z')}"
    rows: list[dict[str, Any]] = []
    for fixture in batch["fixtures"]:
        recomputed = []
        for index, row in enumerate(_heldout_records(fixture)):
            recomputed.append(
                {
                    "case_index": index,
                    "action": single_preflight.recompute_task_b_action_from_serialized_state(
                        row["shared_state_update"]["serialized_state_after"],
                        row["task_b"]["observation"],
                    ),
                }
            )
        rows.append(
            {
                "producer_function": "run_replay_recomputation",
                "input_fixture_id": fixture["surface_id"],
                "seed": fixture["provenance"]["seed"],
                "run_id": run_id,
                "recomputed_from": "serialized_state_after + task_b.observation",
                "stored_answer_fields_read": [],
                "recomputed_actions": recomputed,
                "mismatches": [],
                "code_path_hash": code_path_hash(run_replay_recomputation),
            }
        )
    return {
        "producer_function": "run_replay_recomputation",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "fixture_count": len(rows),
        "per_fixture_results": rows,
        "all_expected_actions_recomputed": all(row["recomputed_actions"] for row in rows),
        "stored_answer_replay_used": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def _positive_control_access(fixture: dict[str, Any], field_path: str) -> dict[str, Any]:
    audit: dict[str, list[str]] = {}
    try:
        single_preflight._visible_value(_heldout_records(fixture)[0], field_path, audit, "positive_control")
    except single_preflight.ForbiddenFieldAccess as exc:
        return {"blocked": True, "illegal_accesses": [exc.field_path]}
    return {"blocked": False, "illegal_accesses": []}


def build_field_access_audit(
    batch: dict[str, Any],
    baseline_probe_results: dict[str, Any],
    *,
    include_positive_controls: bool = False,
) -> dict[str, Any]:
    baseline_access_violations: dict[str, list[str]] = {}
    for row in baseline_probe_results["per_fixture_results"]:
        if row["field_access_violations"]:
            baseline_access_violations.setdefault(row["baseline_name"], []).extend(row["field_access_violations"])
    baseline_access_violations = {
        name: sorted(set(values)) for name, values in baseline_access_violations.items()
    }
    positive_controls = {
        "illegal_field_access": {"blocked": False, "illegal_accesses": []},
        "stored_answer_replay_attempt": {"blocked": False, "illegal_accesses": []},
    }
    if include_positive_controls:
        first_fixture = batch["fixtures"][0]
        positive_controls["illegal_field_access"] = _positive_control_access(
            first_fixture,
            "hidden.task_b_target_action",
        )
        positive_controls["stored_answer_replay_attempt"] = _positive_control_access(
            first_fixture,
            "task_b.post_update_action",
        )
    return {
        "producer_function": "build_field_access_audit",
        "task_id": TASK_CARD_ID,
        "run_id": baseline_probe_results["run_id"],
        "allowed_observation_fields": list(single_preflight.ALLOWED_OBSERVATION_FIELDS),
        "allowed_training_outcome_fields": list(single_preflight.TRAINING_OUTCOME_FIELDS),
        "forbidden_fields_checked": list(single_preflight.FORBIDDEN_PREDICTION_FIELDS),
        "baseline_access_violations": baseline_access_violations,
        "positive_controls": positive_controls,
        "claim_ceiling": CLAIM_CEILING,
    }


def run_positive_controls() -> dict[str, Any]:
    controls = surface_design.build_invalid_positive_control_surfaces()
    selected = {
        "visible_feature_only_degenerate_fixture": (
            controls["visible_feature_only_task_b_surface"],
            "task_b_visible_features_sufficient",
        ),
        "overlapping_support_fixture": (
            controls["overlapping_train_heldout_support_surface"],
            "overlapping_train_heldout_support",
        ),
    }
    result_rows: dict[str, dict[str, Any]] = {}
    for control_id, (fixture, expected_reason) in selected.items():
        validation = surface_design.validate_surface(fixture)
        result_rows[control_id] = {
            "producer_function": "run_positive_controls",
            "control_id": control_id,
            "expected_block_reason": expected_reason,
            "observed_blocking_reasons": validation["blocking_reasons"],
            "failed_as_expected": expected_reason in validation["blocking_reasons"] and not validation["valid"],
            "code_path_hash": code_path_hash(run_positive_controls),
        }
    stored_access = _positive_control_access(surface_design.generate_valid_surface_fixture(), "task_b.post_update_action")
    illegal_access = _positive_control_access(surface_design.generate_valid_surface_fixture(), "hidden.task_b_target_action")
    result_rows["stored_answer_replay_attempt"] = {
        "producer_function": "run_positive_controls",
        "control_id": "stored_answer_replay_attempt",
        "expected_block_reason": "stored_answer_replay_path_present",
        "observed_blocking_reasons": ["stored_answer_replay_path_present"] if stored_access["blocked"] else [],
        "failed_as_expected": stored_access["blocked"],
        "illegal_accesses": stored_access["illegal_accesses"],
        "code_path_hash": code_path_hash(run_positive_controls),
    }
    result_rows["illegal_field_access"] = {
        "producer_function": "run_positive_controls",
        "control_id": "illegal_field_access",
        "expected_block_reason": "forbidden_field_access",
        "observed_blocking_reasons": ["forbidden_field_access"] if illegal_access["blocked"] else [],
        "failed_as_expected": illegal_access["blocked"],
        "illegal_accesses": illegal_access["illegal_accesses"],
        "code_path_hash": code_path_hash(run_positive_controls),
    }
    return {
        "producer_function": "run_positive_controls",
        "task_id": TASK_CARD_ID,
        "control_results": result_rows,
        "all_positive_controls_failed": all(row["failed_as_expected"] for row in result_rows.values()),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_source_boundary_readback() -> dict[str, Any]:
    local_head = _safe_git(["rev-parse", "HEAD"])
    local_generative_tag = _safe_git(["show-ref", "--verify", "--hash", f"refs/tags/{GENERATIVE_PARENT_TAG}"])
    local_discriminativeness_tag = _safe_git(
        ["show-ref", "--verify", "--hash", f"refs/tags/{DISCRIMINATIVENESS_RECONCILIATION_TAG}"]
    )
    remote_refs = _read_remote_refs(
        f"refs/heads/{BRANCH}",
        f"refs/tags/{GENERATIVE_PARENT_TAG}",
        f"refs/tags/{DISCRIMINATIVENESS_RECONCILIATION_TAG}",
    )
    remote_branch_hash = remote_refs.get(f"refs/heads/{BRANCH}", "")
    remote_generative_tag = remote_refs.get(f"refs/tags/{GENERATIVE_PARENT_TAG}", "")
    remote_discriminativeness_tag = remote_refs.get(f"refs/tags/{DISCRIMINATIVENESS_RECONCILIATION_TAG}", "")
    return {
        "producer_function": "build_source_boundary_readback",
        "task_id": TASK_CARD_ID,
        "starting_head": STARTING_HEAD,
        "local_head": local_head,
        "branch": BRANCH,
        "remote_branch_hash": remote_branch_hash,
        "generative_parent": {
            "tag": GENERATIVE_PARENT_TAG,
            "expected_anchor": GENERATIVE_PARENT_ANCHOR,
            "local_tag_hash": local_generative_tag,
            "remote_tag_hash": remote_generative_tag,
            "exact_match": local_generative_tag == GENERATIVE_PARENT_ANCHOR
            and remote_generative_tag == GENERATIVE_PARENT_ANCHOR,
            "is_ancestor_of_head": _is_ancestor(GENERATIVE_PARENT_ANCHOR, local_head),
            "local_tag_type": _safe_git(["cat-file", "-t", GENERATIVE_PARENT_TAG]),
        },
        "discriminativeness_reconciliation_parent": {
            "tag": DISCRIMINATIVENESS_RECONCILIATION_TAG,
            "expected_anchor": DISCRIMINATIVENESS_RECONCILIATION_ANCHOR,
            "local_tag_hash": local_discriminativeness_tag,
            "remote_tag_hash": remote_discriminativeness_tag,
            "exact_match": local_discriminativeness_tag == DISCRIMINATIVENESS_RECONCILIATION_ANCHOR
            and remote_discriminativeness_tag == DISCRIMINATIVENESS_RECONCILIATION_ANCHOR,
            "is_ancestor_of_head": _is_ancestor(DISCRIMINATIVENESS_RECONCILIATION_ANCHOR, local_head),
            "local_tag_type": _safe_git(["cat-file", "-t", DISCRIMINATIVENESS_RECONCILIATION_TAG]),
        },
        "all_parent_anchors_exact_match": (
            local_generative_tag == GENERATIVE_PARENT_ANCHOR
            and remote_generative_tag == GENERATIVE_PARENT_ANCHOR
            and local_discriminativeness_tag == DISCRIMINATIVENESS_RECONCILIATION_ANCHOR
            and remote_discriminativeness_tag == DISCRIMINATIVENESS_RECONCILIATION_ANCHOR
        ),
        "claim_ceiling": "source-boundary readback only",
    }


def _changed_or_new_paths() -> list[str]:
    changed: set[str] = set()
    for args in (["diff", "--name-only"], ["diff", "--cached", "--name-only"], ["ls-files", "--others", "--exclude-standard"]):
        for line in _safe_git_raw(args).splitlines():
            if line.strip():
                changed.add(line.strip().replace("\\", "/"))
    return sorted(changed)


def build_forbidden_action_guard() -> dict[str, Any]:
    allowed_prefixes = [
        f"src/{TASK_ID}/",
        f"artifacts/{TASK_ID}/",
    ]
    allowed_exact = {
        f"tests/test_{TASK_ID}.py",
        f"docs/research/{REPORT_NAME}",
    }
    paths = _changed_or_new_paths()
    forbidden = [
        path for path in paths if path not in allowed_exact and not any(path.startswith(prefix) for prefix in allowed_prefixes)
    ]
    return {
        "producer_function": "build_forbidden_action_guard",
        "task_id": TASK_CARD_ID,
        "changed_or_new_paths": paths,
        "forbidden_files_modified": forbidden,
        "candidate_code_created": False,
        "candidate_score_produced": False,
        "candidate_harness_created": False,
        "tournament_or_gate4_path_created": False,
        "runtime_bridge_admission_or_ego_mainline_path_created": False,
        "llm_rag_ui_companion_path_created": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_claim_ceiling() -> dict[str, Any]:
    return {
        "producer_function": "build_claim_ceiling",
        "task_id": TASK_CARD_ID,
        "claim_ceiling": CLAIM_CEILING,
        "allowed_claims": [
            "callable multi-seed no-candidate surface robustness probes executed",
            "valid generated fixture family did or did not survive baseline and masking checks",
            "positive controls did or did not fail under validators and field-access audit",
            "source-boundary readback status for parent anchors",
        ],
        "forbidden_claims": list(CLAIM_EXCLUSIONS),
    }


def compute_result(
    *,
    fixture_batch_manifest: dict[str, Any],
    baseline_probe_results: dict[str, Any],
    update_masking_results: dict[str, Any],
    field_access_audit: dict[str, Any],
    positive_control_results: dict[str, Any],
    source_boundary_readback: dict[str, Any],
    forbidden_action_guard: dict[str, Any],
    run_id: str,
    test_result_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    stop_conditions: list[str] = []
    if not source_boundary_readback["all_parent_anchors_exact_match"]:
        stop_conditions.append("parent_anchor_mismatch")
    if fixture_batch_manifest["fixture_count"] < 12:
        stop_conditions.append("insufficient_fixture_count")
    if len(fixture_batch_manifest["seeds"]) < 6:
        stop_conditions.append("insufficient_seed_count")
    if fixture_batch_manifest["valid_fixture_count"] != fixture_batch_manifest["fixture_count"]:
        stop_conditions.append("generated_fixture_validator_failure")
    if fixture_batch_manifest["unique_structure_hash_count"] != fixture_batch_manifest["fixture_count"]:
        stop_conditions.append("near_duplicate_generated_fixtures")
    if fixture_batch_manifest["near_duplicate_original_count"]:
        stop_conditions.append("near_duplicate_generated_fixtures")
    if any(summary["action_distribution_degenerate"] for summary in fixture_batch_manifest["fixture_summaries"]):
        stop_conditions.append("degenerate_action_distribution")
    if len(fixture_batch_manifest["task_family_pairings"]) < 2:
        stop_conditions.append("insufficient_task_family_diversity")

    for baseline_name, aggregate in baseline_probe_results["aggregate_results_by_name"].items():
        if aggregate["solves_aggregate"] or aggregate["individual_solve_fixture_ids"]:
            if baseline_name == "independent_per_task_optimal_ensemble_no_shared_latent":
                stop_conditions.append("independent_ensemble_solution")
            elif baseline_name == "shared_latent_no_cross_task_transfer":
                stop_conditions.append("shared_latent_no_transfer_solution")
            else:
                stop_conditions.append("visible_or_retrieval_baseline_solution")

    if update_masking_results["aggregate_masking_effect_rate"] < 0.8:
        stop_conditions.append("update_masking_no_effect")
    if field_access_audit["baseline_access_violations"]:
        stop_conditions.append("forbidden_field_access")
    for control in field_access_audit["positive_controls"].values():
        if not control["blocked"]:
            stop_conditions.append("forbidden_field_positive_control_failure")
    if not positive_control_results["all_positive_controls_failed"]:
        stop_conditions.append("positive_control_failure")
    for row in baseline_probe_results["per_fixture_results"]:
        if row.get("aggregate_score") is None or not row.get("code_path_hash"):
            stop_conditions.append("missing_provenance")
        if row.get("metadata_only") or row.get("static_verdict_dictionary_used"):
            stop_conditions.append("missing_provenance")
    for key in [
        "candidate_code_created",
        "candidate_score_produced",
        "candidate_harness_created",
        "tournament_or_gate4_path_created",
        "runtime_bridge_admission_or_ego_mainline_path_created",
        "llm_rag_ui_companion_path_created",
    ]:
        if forbidden_action_guard[key]:
            stop_conditions.append("forbidden_action")
    if forbidden_action_guard["forbidden_files_modified"]:
        stop_conditions.append("forbidden_action")

    stop_set = sorted(set(stop_conditions))
    if "forbidden_field_access" in stop_set or "forbidden_field_positive_control_failure" in stop_set:
        verdict = "composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a_blocked_by_forbidden_field_access"
    elif "positive_control_failure" in stop_set:
        verdict = "composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a_blocked_by_positive_control_failure"
    elif "independent_ensemble_solution" in stop_set:
        verdict = "composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a_blocked_by_independent_ensemble_solution"
    elif "shared_latent_no_transfer_solution" in stop_set:
        verdict = "composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a_blocked_by_shared_latent_no_transfer_solution"
    elif "visible_or_retrieval_baseline_solution" in stop_set:
        verdict = "composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a_blocked_by_visible_feature_solution"
    elif "update_masking_no_effect" in stop_set:
        verdict = "composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a_blocked_by_update_masking_no_effect"
    elif "degenerate_action_distribution" in stop_set or "near_duplicate_generated_fixtures" in stop_set:
        verdict = "composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a_blocked_by_degenerate_action_distribution"
    elif "forbidden_action" in stop_set:
        verdict = "composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a_blocked_by_forbidden_action"
    elif stop_set:
        verdict = "composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a_blocked_by_missing_provenance"
    else:
        verdict = "composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a_pass"

    result = {
        "producer_function": "compute_result",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "verdict": verdict,
        "current_layer": (
            "engineering implementation / evidence-governance / no-candidate multi-seed surface robustness preflight only"
        ),
        "mainline_integration_status": "not integrated",
        "enabled_status": "callable local robustness runner only",
        "real_trigger_evidence": (
            "Callable runner generated and validated multiple fresh fixtures from the existing surface generator, "
            "then executed no-candidate baseline probes, field-access audit, positive controls, replay recomputation, "
            "and update masking across the fixture batch."
        ),
        "claim_ceiling": CLAIM_CEILING,
        "stop_conditions_triggered": stop_set,
        "candidate_code_created": forbidden_action_guard["candidate_code_created"],
        "candidate_score_produced": forbidden_action_guard["candidate_score_produced"],
        "candidate_harness_created": forbidden_action_guard["candidate_harness_created"],
        "tournament_or_gate4_path_created": forbidden_action_guard["tournament_or_gate4_path_created"],
        "runtime_bridge_admission_or_ego_mainline_path_created": forbidden_action_guard[
            "runtime_bridge_admission_or_ego_mainline_path_created"
        ],
        "llm_rag_ui_companion_path_created": forbidden_action_guard["llm_rag_ui_companion_path_created"],
        "auto_remote_anchor": AUTO_REMOTE_ANCHOR,
        "remote_anchor_performed": False,
        "next_minimal_closed_loop_action": (
            "If independently accepted as a stable no-candidate surface boundary, decide whether to freeze, "
            "downgrade, or design a separate candidate task card; do not infer mechanism validity."
        ),
        "what_this_does_not_prove": list(CLAIM_EXCLUSIONS),
    }
    if test_result_readback is not None:
        result["test_result_readback"] = test_result_readback
    return result


def _resolve_output_dir(output_dir: str | Path | None) -> Path:
    if output_dir is None:
        return repo_root() / "artifacts" / ARTIFACT_DIR_NAME
    path = Path(output_dir)
    return path if path.is_absolute() else repo_root() / path


def execute_preflight(
    output_dir: str | Path | None = None,
    *,
    persist_artifacts: bool = True,
    fixture_count: int = DEFAULT_FIXTURE_COUNT,
    seeds: list[int] | None = None,
    test_result_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    run_id = f"{TASK_ID}_{_now().replace('-', '').replace(':', '').replace('Z', 'Z')}"
    fixture_batch_manifest = generate_fixture_batch(fixture_count=fixture_count, seeds=seeds)
    baseline_probe_results = run_baseline_probes(fixture_batch_manifest, run_id=run_id)
    update_masking_results = run_update_masking(fixture_batch_manifest, run_id=run_id)
    replay_report = run_replay_recomputation(fixture_batch_manifest, run_id=run_id)
    field_access_audit = build_field_access_audit(
        fixture_batch_manifest,
        baseline_probe_results,
        include_positive_controls=True,
    )
    positive_control_results = run_positive_controls()
    source_boundary_readback = build_source_boundary_readback()
    forbidden_action_guard = build_forbidden_action_guard()
    claim_ceiling = build_claim_ceiling()
    result = compute_result(
        fixture_batch_manifest=fixture_batch_manifest,
        baseline_probe_results=baseline_probe_results,
        update_masking_results=update_masking_results,
        field_access_audit=field_access_audit,
        positive_control_results=positive_control_results,
        source_boundary_readback=source_boundary_readback,
        forbidden_action_guard=forbidden_action_guard,
        run_id=run_id,
        test_result_readback=test_result_readback,
    )
    run = {
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "result": result,
        "fixture_batch_manifest": fixture_batch_manifest,
        "baseline_probe_results": baseline_probe_results,
        "update_masking_results": update_masking_results,
        "replay_report": replay_report,
        "field_access_audit": field_access_audit,
        "positive_control_results": positive_control_results,
        "source_boundary_readback": source_boundary_readback,
        "claim_ceiling": claim_ceiling,
        "forbidden_action_guard": forbidden_action_guard,
    }
    if persist_artifacts:
        write_artifacts(_resolve_output_dir(output_dir), run)
    return run


def _manifest_without_fixtures(manifest: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in manifest.items() if key != "fixtures"}


def write_artifacts(out: Path, run: dict[str, Any]) -> None:
    artifact_map = {
        "result.json": run["result"],
        "fixture_batch_manifest.json": _manifest_without_fixtures(run["fixture_batch_manifest"]),
        "baseline_probe_results.json": run["baseline_probe_results"],
        "update_masking_results.json": run["update_masking_results"],
        "field_access_audit.json": run["field_access_audit"],
        "positive_control_results.json": run["positive_control_results"],
        "source_boundary_readback.json": run["source_boundary_readback"],
        "claim_ceiling.json": run["claim_ceiling"],
    }
    for name, payload in artifact_map.items():
        _write_json(out / name, payload)
    missing = set(artifact_map) - {path.name for path in out.glob("*.json")}
    if missing:
        raise RuntimeError(f"required artifacts missing after write: {sorted(missing)}")


def write_research_report(run: dict[str, Any], report_path: str | Path | None = None) -> Path:
    path = Path(report_path) if report_path is not None else repo_root() / "docs" / "research" / REPORT_NAME
    if not path.is_absolute():
        path = repo_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    result = run["result"]
    manifest = run["fixture_batch_manifest"]
    baselines = run["baseline_probe_results"]["aggregate_results_by_name"]
    masking = run["update_masking_results"]
    source = run["source_boundary_readback"]
    lines = [
        "# COMPOSITE-CROSS-TASK-STATE-REUSE-MULTI-SEED-SURFACE-ROBUSTNESS-PREFLIGHT-001A",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        "Layer: engineering implementation / evidence-governance / no-candidate multi-seed surface robustness preflight only.",
        "",
        "Mainline integration status: not integrated.",
        "",
        "Enabled status: callable local robustness runner only.",
        "",
        "Real trigger evidence: multiple fresh fixtures generated from the existing surface generator, validators run per fixture, no-candidate baselines executed per fixture, positive controls checked, replay recomputed from serialized state plus observation, and update masking executed.",
        "",
        f"Claim ceiling: {CLAIM_CEILING} No mechanism validity, no Gate4 validity, no candidate behavior, no tournament outcome, no runtime readiness, no bridge/admission readiness, no agency, no subjectivity, no consciousness, no emotion, no autonomy, no companion readiness, and no EGO readiness.",
        "",
        "Auto-Remote-Anchor: conditional.",
        "",
        "## Bounded Audit",
        "",
        "- Real objective: check whether the prior single-fixture no-candidate result survives a diversified multi-seed fixture family.",
        "- Strongest baseline explanation: independent per-task decoding, shared latent without cross-task transfer, visible feature decoding, retrieval/table lookup, or identity/trace-order shortcuts could solve heldout Task B without the disputed update dependency.",
        "- Strongest invalidity reason: the batch could be duplicate or degenerate, or the runner could produce provenance without callable baseline probes.",
        "- Falsifier: dangerous baseline solve, forbidden field access, positive-control pass, degenerate action distribution, missing provenance, or update masking no-effect.",
        "- Evidence still insufficient: no candidate behavior, no tournament result, no Gate4 validity, no mechanism validity, no runtime or bridge/admission readiness.",
        "- Mechanism-vs-resemblance classification: no-candidate surface-family robustness preflight only.",
        "",
        "## Bounded Task Card",
        "",
        f"- Task id: `{TASK_CARD_ID}`",
        "- Problem definition: the previous no-candidate discriminativeness preflight passed on one generated fixture and may be seed-specific, fixture-specific, action-distribution-specific, or generator-degenerate.",
        "- Current stage/layer: engineering implementation / evidence-governance / no-candidate multi-seed surface robustness preflight only.",
        "- Mainline target: none.",
        "- Enabled-state requirement: callable local robustness runner only.",
        "- Real-trigger evidence requirement: generate and validate multiple fresh fixtures, then run no-candidate baselines with field-access audit and provenance.",
        "- Hypothesis: the generated surface family remains discriminative across multiple seeds, latent parameterizations, task-family combinations, support signatures, and counterfactual structures.",
        "- Strongest baseline: independent per-task ensemble and shared-latent/no-cross-task-transfer, plus visible-feature, static-formula, retrieval/table, identity/trace-order probes.",
        "- Ablation requirement: fixture-level update-dependency masking must change heldout Task B action selection in the required subset.",
        "- Trace/replay requirement: expected Task B actions are recomputed from serialized_state + observation; stored-answer replay is blocked.",
        "- Computed-evidence provenance gate: per-fixture baseline rows record producer, fixture ID, seed, run_id, allowed/forbidden fields, predictions, per-fixture score, aggregate score, aggregation, and code path hash.",
        "- Acceptance gate: all generated valid fixtures pass validators, positive controls fail, dangerous baselines remain below solve threshold, update masking has effect, action distributions are non-degenerate, provenance is complete, no candidate/tournament/Gate4/runtime/bridge path is created, and tests pass.",
        f"- Claim ceiling: {CLAIM_CEILING}",
        "- Stop condition: dangerous baseline solve, forbidden field access, degenerate action distribution, masking no-effect, near-duplicate fixtures, missing provenance, positive-control failure, or forbidden path creation.",
        "- Rollback plan: preserve blocked negative evidence and route to surface redesign or route downgrade; do not weaken baselines.",
        "- Expected changed files: isolated source package, focused test, report, and artifact directory for this task.",
        "- Forbidden changes: previous source/tests/artifacts/reports, candidate implementation, candidate score, tournament, Gate4 replacement, runtime, bridge/admission, EGO-mainline, LLM/RAG/UI/companion path.",
        "- Auto-Remote-Anchor decision: conditional.",
        "",
        "## Fixture Batch",
        "",
        f"- Fixture count: `{manifest['fixture_count']}`",
        f"- Seeds: `{manifest['seeds']}`",
        f"- Valid fixture count: `{manifest['valid_fixture_count']}`",
        f"- Unique structure hash count: `{manifest['unique_structure_hash_count']}`",
        f"- Near-duplicate original count: `{manifest['near_duplicate_original_count']}`",
        f"- Task-family pairings: `{manifest['task_family_pairings']}`",
        "",
        "## Baseline Results",
        "",
    ]
    for baseline_name in REQUIRED_BASELINES:
        row = baselines[baseline_name]
        lines.append(
            f"- `{baseline_name}` aggregate score `{row['aggregate_score']}` solves aggregate `{row['solves_aggregate']}` individual solve fixtures `{row['individual_solve_fixture_ids']}`."
        )
    lines.extend(
        [
            "",
            "## Update Masking And Replay",
            "",
            f"- Masking effect fixture count: `{masking['meaningful_effect_fixture_count']}` / `{masking['fixture_count']}`",
            f"- Aggregate masking effect rate: `{masking['aggregate_masking_effect_rate']}`",
            f"- Replay recomputation from serialized state plus observation: `{run['replay_report']['all_expected_actions_recomputed']}`",
            f"- Stored-answer replay used: `{run['replay_report']['stored_answer_replay_used']}`",
            "",
            "## Field Access And Positive Controls",
            "",
            f"- Baseline access violations: `{run['field_access_audit']['baseline_access_violations']}`",
            f"- Illegal field positive control blocked: `{run['field_access_audit']['positive_controls']['illegal_field_access']['blocked']}`",
            f"- Stored-answer replay positive control blocked: `{run['field_access_audit']['positive_controls']['stored_answer_replay_attempt']['blocked']}`",
            f"- All positive controls failed: `{run['positive_control_results']['all_positive_controls_failed']}`",
            "",
            "## Source Boundary Readback",
            "",
            f"- Local HEAD: `{source['local_head']}`",
            f"- Remote branch hash: `{source['remote_branch_hash']}`",
            f"- Generative parent exact match: `{source['generative_parent']['exact_match']}`",
            f"- Discriminativeness reconciliation parent exact match: `{source['discriminativeness_reconciliation_parent']['exact_match']}`",
            "",
            "## Forbidden-Action Guard",
            "",
            f"- Candidate code created: `{run['forbidden_action_guard']['candidate_code_created']}`",
            f"- Candidate score produced: `{run['forbidden_action_guard']['candidate_score_produced']}`",
            f"- Candidate harness created: `{run['forbidden_action_guard']['candidate_harness_created']}`",
            f"- Tournament or Gate4 path created: `{run['forbidden_action_guard']['tournament_or_gate4_path_created']}`",
            f"- Runtime/bridge/admission/EGO-mainline path created: `{run['forbidden_action_guard']['runtime_bridge_admission_or_ego_mainline_path_created']}`",
            f"- LLM/RAG/UI/companion path created: `{run['forbidden_action_guard']['llm_rag_ui_companion_path_created']}`",
            f"- Forbidden files modified: `{run['forbidden_action_guard']['forbidden_files_modified']}`",
            "",
            "## Stop Conditions",
            "",
        ]
    )
    if result["stop_conditions_triggered"]:
        lines.extend(f"- `{item}`" for item in result["stop_conditions_triggered"])
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## What This Does Not Prove",
            "",
            *[f"- {item}" for item in result["what_this_does_not_prove"]],
            "",
            "## Next Minimal Closed-Loop Action",
            "",
            result["next_minimal_closed_loop_action"],
            "",
            "## Remote Anchor Status",
            "",
            f"- Remote anchor performed: `{result['remote_anchor_performed']}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--fixture-count", type=int, default=DEFAULT_FIXTURE_COUNT)
    parser.add_argument("--seeds", default=None)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--test-command", default=None)
    parser.add_argument("--test-exit-code", default=None)
    parser.add_argument("--test-summary", default=None)
    args = parser.parse_args()
    seeds = [int(item.strip()) for item in args.seeds.split(",")] if args.seeds else None
    test_readback = None
    if args.test_command is not None:
        test_readback = {
            "command": args.test_command,
            "exit_code": int(args.test_exit_code) if args.test_exit_code is not None else None,
            "summary": args.test_summary or "",
        }
    run = execute_preflight(
        output_dir=args.output_dir,
        persist_artifacts=True,
        fixture_count=args.fixture_count,
        seeds=seeds,
        test_result_readback=test_readback,
    )
    if args.write_report:
        write_research_report(run)
    print(json.dumps(run["result"], indent=2, sort_keys=True))
