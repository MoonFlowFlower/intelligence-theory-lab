from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import inspect
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from . import (
    ARTIFACT_DIR_NAME,
    AUTO_REMOTE_ANCHOR,
    BRANCH,
    CLAIM_CEILING,
    G0_RECONCILIATION_ANCHOR,
    G0_RECONCILIATION_TAG,
    G0_ROUTE_SPEC_ANCHOR,
    G0_ROUTE_TAG,
    REPORT_NAME,
    TASK_CARD_ID,
    TASK_ID,
)


DEFAULT_SEED = 61001
VALIDATOR_THRESHOLD = 0.8
MODULE_PATH = str(Path("src") / TASK_ID / "runner.py").replace("\\", "/")
TARGET_RESOLVER_PATH = f"{TASK_ID}.runner.resolve_task_b_target_action"
TASK_FAMILIES = [
    "self_boundary_controllability",
    "replay_consolidation",
    "viability_value_gated_prediction_action",
    "social_latent_inference",
]
REQUIRED_BASELINES = [
    "exact_lookup",
    "train_row_table_lookup",
    "nearest_neighbor_retrieval",
    "identity_key_lookup",
    "trace_order_lookup",
    "static_formula_decoder_visible_fields",
    "independent_per_task_optimal_ensemble_no_shared_latent_state",
    "shared_latent_state_without_cross_task_prediction_error_to_action_transfer",
    "multi_task_representation_learning",
    "pomdp_shared_belief_state_update_plus_control",
    "rnn_meta_rl_hidden_state_controller",
    "dyna_q_prioritized_sweeping",
    "mpc_world_model_planner",
    "causal_bandit",
    "oracle_feature_sharing_without_disputed_update_channel",
]
REQUIRED_PROVENANCE_FIELDS = [
    "generator_function",
    "seed",
    "latent_parameter_ids",
    "train_ids",
    "heldout_ids",
    "task_family_ids",
    "support_signatures",
    "counterfactual_pair_ids",
    "prediction_error_event_ids",
    "shared_state_update_event_ids",
    "task_b_action_dependency_ids",
    "target_resolver_path",
    "code_path_hash",
    "baseline_preregistration_list",
]
VALIDATOR_IDS = [
    "anti_lookup_generative_heldout_compliance",
    "support_disjoint_train_heldout_split",
    "identity_key_permutation",
    "target_leakage",
    "static_formula_solvability",
    "table_exact_lookup_solvability",
    "nearest_neighbor_retrieval_shortcut",
    "trace_order_shortcut",
    "counterfactual_pair_validity",
    "generator_provenance_completeness",
    "baseline_preregistration_completeness",
    "future_replay_recomputation_requirement",
    "future_ablation_requirement",
    "forbidden_action_guard",
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
EXPECTED_CONTROL_REASONS = {
    "exact_lookup_surface": "exact_lookup_reaches_threshold",
    "table_lookup_surface": "table_lookup_reaches_threshold",
    "identity_key_surface": "identity_key_lookup_reaches_threshold",
    "trace_order_surface": "trace_order_lookup_reaches_threshold",
    "static_formula_surface": "static_formula_solves_task_b",
    "target_leak_surface": "target_leakage_detected",
    "missing_generator_provenance_surface": "missing_generator_provenance",
    "missing_counterfactual_pairs_surface": "missing_counterfactual_pairs",
    "overlapping_train_heldout_support_surface": "overlapping_train_heldout_support",
    "independent_ensemble_solvable_surface": "independent_ensemble_solves_without_shared_update",
    "shared_latent_no_transfer_solvable_surface": "shared_latent_no_transfer_solves_task_b",
    "visible_feature_only_task_b_surface": "task_b_visible_features_sufficient",
    "stored_answer_replay_surface": "stored_answer_replay_path_present",
    "hidden_label_exposure_surface": "hidden_label_exposure_detected",
}
LOOKUP_BLOCK_REASONS = {
    "exact_lookup_reaches_threshold",
    "table_lookup_reaches_threshold",
    "nearest_neighbor_retrieval_reaches_threshold",
    "identity_key_lookup_reaches_threshold",
    "trace_order_lookup_reaches_threshold",
    "static_formula_solves_task_b",
    "independent_ensemble_solves_without_shared_update",
    "shared_latent_no_transfer_solves_task_b",
    "task_b_visible_features_sufficient",
}
TARGET_LEAK_TERMS = ("target", "answer", "label")


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


def _resolve_function(dotted_path: str) -> Callable[..., Any]:
    module_name, function_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


def resolve_task_b_target_action(record: dict[str, Any]) -> str:
    return str(record["hidden"]["task_b_target_action"])


def recompute_task_b_action_from_serialized_state(
    serialized_state: dict[str, Any], observation: dict[str, Any]
) -> str:
    if not serialized_state.get("shared_update_applied"):
        return str(observation.get("pre_update_default_action", "hold"))
    binding = serialized_state.get("latent_action_binding", {})
    return str(binding.get(observation.get("latent_binding_probe"), observation.get("fallback_action", "hold")))


def _record(
    *,
    split: str,
    index: int,
    support_signature: str,
    context_handle: str,
    partner_handle: str,
    latent_parameter_id: str,
    task_family_id: str,
    superficial_signature: str,
    target_action: str,
    pre_update_action: str,
    post_update_action: str,
    local_visible_cue: str,
    counterfactual_combo_id: str,
) -> dict[str, Any]:
    record_id = f"{split}:episode:{index}"
    prediction_error_event_id = f"pe:{split}:{index}"
    update_event_id = f"update:{split}:{index}"
    action_dependency_id = f"task_b_dep:{split}:{index}"
    latent_binding_probe = f"probe:{latent_parameter_id}:{index}"
    return {
        "record_id": record_id,
        "split": split,
        "support_signature": support_signature,
        "context_handle": context_handle,
        "partner_handle": partner_handle,
        "latent_parameter_id": latent_parameter_id,
        "counterfactual_combo_id": counterfactual_combo_id,
        "task_family_id": task_family_id,
        "task_a": {
            "observation": {
                "visible_event_class": f"task_a_surface_{superficial_signature}",
                "predicted_outcome": "expected_stable_response",
                "observed_outcome": "unexpected_shift_response",
                "prediction_signal": f"signal_{index % 2}",
            },
            "prediction_error_event_id": prediction_error_event_id,
            "prediction_error_under_pre_update_state": True,
        },
        "shared_state_update": {
            "update_event_id": update_event_id,
            "channel": "hidden_cross_task_prediction_error_update_channel",
            "serialized_state_before": {
                "shared_update_applied": False,
                "latent_action_binding": {},
            },
            "serialized_state_after": {
                "shared_update_applied": True,
                "latent_action_binding": {latent_binding_probe: post_update_action},
            },
            "caused_by_task_a_prediction_error_event_id": prediction_error_event_id,
        },
        "task_b": {
            "observation": {
                "superficial_signature": superficial_signature,
                "local_visible_cue": local_visible_cue,
                "latent_binding_probe": latent_binding_probe,
                "pre_update_default_action": pre_update_action,
                "fallback_action": "hold",
            },
            "pre_update_action": pre_update_action,
            "post_update_action": post_update_action,
            "action_dependency_id": action_dependency_id,
            "action_depends_on_shared_state_update": True,
            "visible_features_alone_sufficient": False,
        },
        "hidden": {
            "generator_latent_state_id": "hidden_composite_state_v1",
            "task_a_latent_target": f"task_a_error_for_{latent_parameter_id}",
            "task_b_target_action": target_action,
            "shared_update_required_for_task_b_action": True,
        },
    }


def generate_valid_surface_fixture(seed: int = DEFAULT_SEED) -> dict[str, Any]:
    train = [
        _record(
            split="train",
            index=0,
            support_signature="train_support_alpha",
            context_handle="train_context_alpha",
            partner_handle="train_partner_alpha",
            latent_parameter_id="latent_train_alpha",
            task_family_id="self_boundary_controllability",
            superficial_signature="same_surface_x",
            target_action="inspect_boundary",
            pre_update_action="hold",
            post_update_action="inspect_boundary",
            local_visible_cue="cue_shared",
            counterfactual_combo_id="train_combo_alpha",
        ),
        _record(
            split="train",
            index=1,
            support_signature="train_support_beta",
            context_handle="train_context_beta",
            partner_handle="train_partner_beta",
            latent_parameter_id="latent_train_beta",
            task_family_id="self_boundary_controllability",
            superficial_signature="same_surface_x",
            target_action="consolidate_trace",
            pre_update_action="hold",
            post_update_action="consolidate_trace",
            local_visible_cue="cue_shared",
            counterfactual_combo_id="train_combo_beta",
        ),
        _record(
            split="train",
            index=2,
            support_signature="train_support_gamma",
            context_handle="train_context_gamma",
            partner_handle="train_partner_gamma",
            latent_parameter_id="latent_train_gamma",
            task_family_id="replay_consolidation",
            superficial_signature="surface_variant_gamma",
            target_action="defer_action",
            pre_update_action="hold",
            post_update_action="defer_action",
            local_visible_cue="cue_gamma",
            counterfactual_combo_id="train_combo_gamma",
        ),
        _record(
            split="train",
            index=3,
            support_signature="train_support_delta",
            context_handle="train_context_delta",
            partner_handle="train_partner_delta",
            latent_parameter_id="latent_train_gamma",
            task_family_id="replay_consolidation",
            superficial_signature="surface_variant_delta",
            target_action="defer_action",
            pre_update_action="hold",
            post_update_action="defer_action",
            local_visible_cue="cue_delta",
            counterfactual_combo_id="train_combo_delta",
        ),
    ]
    heldout = [
        _record(
            split="heldout",
            index=0,
            support_signature="heldout_support_eta",
            context_handle="heldout_context_eta",
            partner_handle="heldout_partner_eta",
            latent_parameter_id="latent_heldout_eta",
            task_family_id="viability_value_gated_prediction_action",
            superficial_signature="heldout_surface_eta",
            target_action="replan_memory",
            pre_update_action="hold",
            post_update_action="replan_memory",
            local_visible_cue="cue_heldout_a",
            counterfactual_combo_id="heldout_combo_eta",
        ),
        _record(
            split="heldout",
            index=1,
            support_signature="heldout_support_theta",
            context_handle="heldout_context_theta",
            partner_handle="heldout_partner_theta",
            latent_parameter_id="latent_heldout_theta",
            task_family_id="social_latent_inference",
            superficial_signature="heldout_surface_theta",
            target_action="inspect_boundary",
            pre_update_action="hold",
            post_update_action="inspect_boundary",
            local_visible_cue="cue_heldout_b",
            counterfactual_combo_id="heldout_combo_theta",
        ),
        _record(
            split="heldout",
            index=2,
            support_signature="heldout_support_iota",
            context_handle="heldout_context_iota",
            partner_handle="heldout_partner_iota",
            latent_parameter_id="latent_heldout_iota",
            task_family_id="viability_value_gated_prediction_action",
            superficial_signature="heldout_surface_iota",
            target_action="consolidate_trace",
            pre_update_action="hold",
            post_update_action="consolidate_trace",
            local_visible_cue="cue_heldout_c",
            counterfactual_combo_id="heldout_combo_iota",
        ),
        _record(
            split="heldout",
            index=3,
            support_signature="heldout_support_kappa",
            context_handle="heldout_context_kappa",
            partner_handle="heldout_partner_kappa",
            latent_parameter_id="latent_heldout_kappa",
            task_family_id="social_latent_inference",
            superficial_signature="heldout_surface_kappa",
            target_action="defer_action",
            pre_update_action="hold",
            post_update_action="defer_action",
            local_visible_cue="cue_heldout_d",
            counterfactual_combo_id="heldout_combo_kappa",
        ),
    ]
    counterfactual_pairs = [
        {
            "pair_id": "cf_same_surface_latent_changes_train_0_1",
            "pair_type": "same_superficial_features_latent_structure_changes",
            "record_ids": ["train:episode:0", "train:episode:1"],
            "held_constant": ["task_b.observation.superficial_signature", "task_b.observation.local_visible_cue"],
            "changed": ["latent_parameter_id", "hidden.task_b_target_action"],
        },
        {
            "pair_id": "cf_surface_changes_latent_stable_train_2_3",
            "pair_type": "superficial_features_change_latent_structure_stable",
            "record_ids": ["train:episode:2", "train:episode:3"],
            "held_constant": ["latent_parameter_id", "hidden.task_b_target_action"],
            "changed": ["task_b.observation.superficial_signature", "task_b.observation.local_visible_cue"],
        },
    ]
    records = {"train": train, "heldout": heldout}
    prediction_error_event_ids = [row["task_a"]["prediction_error_event_id"] for row in train + heldout]
    shared_state_update_event_ids = [row["shared_state_update"]["update_event_id"] for row in train + heldout]
    task_b_action_dependency_ids = [row["task_b"]["action_dependency_id"] for row in train + heldout]
    support_signatures = {
        "train": [row["support_signature"] for row in train],
        "heldout": [row["support_signature"] for row in heldout],
    }
    baseline_preregistration = build_baseline_preregistration()
    provenance = {
        "generator_function": f"{TASK_ID}.runner.generate_valid_surface_fixture",
        "seed": seed,
        "latent_parameter_ids": {
            "train": [row["latent_parameter_id"] for row in train],
            "heldout": [row["latent_parameter_id"] for row in heldout],
        },
        "train_ids": [row["record_id"] for row in train],
        "heldout_ids": [row["record_id"] for row in heldout],
        "task_family_ids": list(TASK_FAMILIES),
        "support_signatures": support_signatures,
        "counterfactual_pair_ids": [row["pair_id"] for row in counterfactual_pairs],
        "prediction_error_event_ids": prediction_error_event_ids,
        "shared_state_update_event_ids": shared_state_update_event_ids,
        "task_b_action_dependency_ids": task_b_action_dependency_ids,
        "target_resolver_path": TARGET_RESOLVER_PATH,
        "code_path_hash": code_path_hash(generate_valid_surface_fixture),
        "baseline_preregistration_list": baseline_preregistration["baseline_ids"],
    }
    return {
        "surface_id": "composite_cross_task_state_reuse_valid_generated_surface_001a",
        "surface_kind": "generated_surface_design_fixture_only",
        "generated_by_callable": True,
        "design_only": True,
        "threshold": VALIDATOR_THRESHOLD,
        "task_family_ids": list(TASK_FAMILIES),
        "latent_generator": {
            "hidden_latent_state_id": "hidden_composite_state_v1",
            "controls_task_a_target_structure": True,
            "controls_task_b_target_structure": True,
            "shared_across_task_a_and_task_b": True,
        },
        "split_policy": {
            "support_disjoint_required": True,
            "latent_parameterization_disjoint_required": True,
            "context_support_disjoint_required": True,
            "identity_permutation_required": True,
            "counterfactual_combination_disjoint_required": True,
        },
        "records": records,
        "counterfactual_pairs": counterfactual_pairs,
        "cross_task_prediction_error_event_ids": prediction_error_event_ids,
        "shared_state_update_event_ids": shared_state_update_event_ids,
        "task_b_action_dependency_ids": task_b_action_dependency_ids,
        "baseline_access": {
            "observation_access": "fair_visible_observation_access",
            "hidden_target_labels_access": False,
            "answer_keys_access": False,
            "row_ids_access": False,
            "partner_or_context_ids_access": False,
            "trace_order_access": False,
            "disputed_cross_task_update_channel_access": False,
        },
        "baseline_preregistration": baseline_preregistration["baseline_ids"],
        "future_replay_requirement": {
            "recompute_from_serialized_state_and_observation": True,
            "serialized_state_required": True,
            "new_observation_required": True,
            "stored_answer_replay_allowed": False,
            "stored_hash_replay_allowed": False,
            "recompute_function_path": f"{TASK_ID}.runner.recompute_task_b_action_from_serialized_state",
        },
        "future_ablation_requirement": {
            "remove_cross_task_update_channel": True,
            "task_b_support_disjoint_action_change_must_collapse": True,
            "preserve_local_per_task_behavior_where_possible": True,
        },
        "shortcut_flags": {
            "independent_ensemble_solves_without_shared_update": False,
            "shared_latent_no_transfer_solves_task_b": False,
            "task_b_visible_features_sufficient": False,
            "stored_answer_replay_path_present": False,
            "hidden_label_exposure_detected": False,
        },
        "provenance": provenance,
        "claim_ceiling": CLAIM_CEILING,
    }


def _all_records(surface: dict[str, Any]) -> list[dict[str, Any]]:
    records = surface.get("records", {})
    return list(records.get("train", [])) + list(records.get("heldout", []))


def _split_records(surface: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records = surface.get("records", {})
    return list(records.get("train", [])), list(records.get("heldout", []))


def _targets(records: list[dict[str, Any]], resolver_path: str | None = None) -> list[str]:
    resolver = _resolve_function(resolver_path or TARGET_RESOLVER_PATH)
    return [str(resolver(record)) for record in records]


def _majority_target(train: list[dict[str, Any]]) -> str:
    if not train:
        return ""
    counts = Counter(_targets(train))
    return sorted(counts, key=lambda key: (-counts[key], key))[0]


def _accuracy(predictions: list[str], targets: list[str]) -> float:
    if not targets:
        return 0.0
    return sum(1 for prediction, target in zip(predictions, targets) if prediction == target) / len(targets)


def _visible_observation(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_a_observation": record.get("task_a", {}).get("observation", {}),
        "task_b_observation": record.get("task_b", {}).get("observation", {}),
    }


def _table_key(record: dict[str, Any], index: int) -> str:
    observation = record.get("task_b", {}).get("observation", {})
    return str(observation.get("table_key", record.get("support_signature", f"support:{index}")))


def _identity_key(record: dict[str, Any], index: int) -> str:
    observation = record.get("task_b", {}).get("observation", {})
    if "identity_key" in observation:
        return str(observation["identity_key"])
    return str(record.get("partner_handle") or record.get("context_handle") or f"identity:{index}")


def _retrieval_key(record: dict[str, Any], index: int) -> str:
    observation = record.get("task_b", {}).get("observation", {})
    return str(observation.get("retrieval_key", _table_key(record, index)))


def _static_formula_key(record: dict[str, Any], index: int) -> str:
    observation = record.get("task_b", {}).get("observation", {})
    return str(
        observation.get(
            "static_formula_key",
            observation.get("local_visible_cue", f"formula_missing:{index}"),
        )
    )


def _score_mapping_baseline(
    surface: dict[str, Any],
    key_func: Callable[[dict[str, Any], int], str],
    *,
    baseline_id: str,
    producer_function: str,
) -> dict[str, Any]:
    train, heldout = _split_records(surface)
    train_targets = _targets(train)
    heldout_targets = _targets(heldout)
    fallback = _majority_target(train)
    mapping = {key_func(record, index): target for index, (record, target) in enumerate(zip(train, train_targets))}
    predictions = [mapping.get(key_func(record, index), fallback) for index, record in enumerate(heldout)]
    score = _accuracy(predictions, heldout_targets)
    return {
        "baseline_id": baseline_id,
        "producer_function": producer_function,
        "module_path": MODULE_PATH,
        "code_path_hash": code_path_hash(_score_mapping_baseline),
        "score": score,
        "threshold": float(surface.get("threshold", VALIDATOR_THRESHOLD)),
        "reaches_threshold": score >= float(surface.get("threshold", VALIDATOR_THRESHOLD)),
        "predictions": predictions,
        "targets": heldout_targets,
        "aggregation_rule": "mean exact-match accuracy over heldout Task B target actions",
        "input_record_ids": {
            "train": [row.get("record_id") for row in train],
            "heldout": [row.get("record_id") for row in heldout],
        },
    }


def compute_shortcut_scores(surface: dict[str, Any]) -> dict[str, dict[str, Any]]:
    exact = _score_mapping_baseline(
        surface,
        lambda record, _index: _canonical(_visible_observation(record)),
        baseline_id="exact_lookup",
        producer_function="run_exact_lookup_validator",
    )
    table = _score_mapping_baseline(
        surface,
        _table_key,
        baseline_id="train_row_table_lookup",
        producer_function="run_train_row_table_lookup_validator",
    )
    retrieval = _score_mapping_baseline(
        surface,
        _retrieval_key,
        baseline_id="nearest_neighbor_retrieval",
        producer_function="run_nearest_neighbor_retrieval_validator",
    )
    identity = _score_mapping_baseline(
        surface,
        _identity_key,
        baseline_id="identity_key_lookup",
        producer_function="run_identity_key_lookup_validator",
    )
    trace = _score_mapping_baseline(
        surface,
        lambda _record, index: str(index),
        baseline_id="trace_order_lookup",
        producer_function="run_trace_order_lookup_validator",
    )
    static = _score_mapping_baseline(
        surface,
        _static_formula_key,
        baseline_id="static_formula_decoder_visible_fields",
        producer_function="run_static_formula_validator",
    )
    direct_static_predictions = [
        str(record.get("task_b", {}).get("observation", {}).get("static_formula_action", ""))
        for record in _split_records(surface)[1]
    ]
    targets = _targets(_split_records(surface)[1])
    direct_static_score = _accuracy(direct_static_predictions, targets)
    if direct_static_score > static["score"]:
        static["score"] = direct_static_score
        static["predictions"] = direct_static_predictions
        static["reaches_threshold"] = direct_static_score >= static["threshold"]
    return {
        "exact_lookup": exact,
        "train_row_table_lookup": table,
        "nearest_neighbor_retrieval": retrieval,
        "identity_key_lookup": identity,
        "trace_order_lookup": trace,
        "static_formula_decoder_visible_fields": static,
    }


def _validator_row(validator_id: str, failures: list[str], **extra: Any) -> dict[str, Any]:
    return {
        "validator_id": validator_id,
        "producer_function": validator_id,
        "module_path": MODULE_PATH,
        "code_path_hash": code_path_hash(_validator_row),
        "passed": not failures,
        "blocking_reasons": sorted(set(failures)),
        **extra,
    }


def _set_disjoint(left: list[Any], right: list[Any]) -> bool:
    return set(left).isdisjoint(set(right))


def _support_disjoint_failures(surface: dict[str, Any]) -> list[str]:
    train, heldout = _split_records(surface)
    checks = {
        "support": _set_disjoint([row.get("support_signature") for row in train], [row.get("support_signature") for row in heldout]),
        "latent_parameterization": _set_disjoint(
            [row.get("latent_parameter_id") for row in train],
            [row.get("latent_parameter_id") for row in heldout],
        ),
        "context_handle": _set_disjoint([row.get("context_handle") for row in train], [row.get("context_handle") for row in heldout]),
        "partner_handle": _set_disjoint([row.get("partner_handle") for row in train], [row.get("partner_handle") for row in heldout]),
        "counterfactual_combo": _set_disjoint(
            [row.get("counterfactual_combo_id") for row in train],
            [row.get("counterfactual_combo_id") for row in heldout],
        ),
    }
    failures = [f"overlapping_train_heldout_{name}" for name, passed in checks.items() if not passed]
    if "overlapping_train_heldout_support" in failures:
        return failures
    return failures


def _identity_failures(surface: dict[str, Any]) -> list[str]:
    train, heldout = _split_records(surface)
    train_keys = [_identity_key(row, index) for index, row in enumerate(train)]
    heldout_keys = [_identity_key(row, index) for index, row in enumerate(heldout)]
    return [] if _set_disjoint(train_keys, heldout_keys) else ["identity_key_lookup_reaches_threshold"]


def _target_leak_failures(surface: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if surface.get("baseline_access", {}).get("hidden_target_labels_access"):
        failures.append("hidden_label_exposure_detected")
    if surface.get("shortcut_flags", {}).get("hidden_label_exposure_detected"):
        failures.append("hidden_label_exposure_detected")
    for record in _all_records(surface):
        target = resolve_task_b_target_action(record)

        def walk(value: Any, path: str = "") -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    key_path = f"{path}.{key}" if path else str(key)
                    if any(term in str(key).lower() for term in TARGET_LEAK_TERMS):
                        failures.append("target_leakage_detected")
                    walk(child, key_path)
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, f"{path}[{index}]")
            elif target and str(value) == target and "pre_update_default_action" not in path:
                failures.append("target_leakage_detected")

        walk(_visible_observation(record))
    return sorted(set(failures))


def _counterfactual_failures(surface: dict[str, Any]) -> list[str]:
    pairs = surface.get("counterfactual_pairs", [])
    if not pairs:
        return ["missing_counterfactual_pairs"]
    by_id = {row.get("record_id"): row for row in _all_records(surface)}
    seen_types = {row.get("pair_type") for row in pairs}
    failures: list[str] = []
    if "same_superficial_features_latent_structure_changes" not in seen_types:
        failures.append("missing_same_surface_latent_change_pair")
    if "superficial_features_change_latent_structure_stable" not in seen_types:
        failures.append("missing_surface_change_latent_stable_pair")
    for pair in pairs:
        rows = [by_id.get(record_id) for record_id in pair.get("record_ids", [])]
        if len(rows) < 2 or any(row is None for row in rows):
            failures.append("counterfactual_pair_record_missing")
            continue
        concrete_rows = [row for row in rows if row is not None]
        surfaces = {row["task_b"]["observation"]["superficial_signature"] for row in concrete_rows}
        latents = {row["latent_parameter_id"] for row in concrete_rows}
        targets = {row["hidden"]["task_b_target_action"] for row in concrete_rows}
        if pair.get("pair_type") == "same_superficial_features_latent_structure_changes":
            if len(surfaces) != 1 or (len(latents) == 1 and len(targets) == 1):
                failures.append("invalid_same_surface_latent_change_pair")
        if pair.get("pair_type") == "superficial_features_change_latent_structure_stable":
            if len(surfaces) < 2 or len(latents) != 1 or len(targets) != 1:
                failures.append("invalid_surface_change_latent_stable_pair")
    return sorted(set(failures))


def _provenance_failures(surface: dict[str, Any]) -> list[str]:
    provenance = surface.get("provenance")
    if not isinstance(provenance, dict):
        return ["missing_generator_provenance"]
    missing = [field for field in REQUIRED_PROVENANCE_FIELDS if not provenance.get(field)]
    if missing:
        return ["missing_generator_provenance", *[f"missing_provenance_field:{field}" for field in missing]]
    if surface.get("generated_by_callable") is not True:
        return ["surface_not_generated_by_callable"]
    if provenance.get("code_path_hash") != code_path_hash(generate_valid_surface_fixture):
        return ["generator_code_path_hash_mismatch"]
    return []


def _baseline_preregistration_failures(surface: dict[str, Any]) -> list[str]:
    registered = set(surface.get("baseline_preregistration", []))
    required = set(REQUIRED_BASELINES)
    if registered != required:
        return ["missing_baseline_preregistration"]
    return []


def _future_replay_failures(surface: dict[str, Any]) -> list[str]:
    replay = surface.get("future_replay_requirement", {})
    failures: list[str] = []
    if replay.get("recompute_from_serialized_state_and_observation") is not True:
        failures.append("future_replay_recomputation_missing")
    if replay.get("serialized_state_required") is not True or replay.get("new_observation_required") is not True:
        failures.append("future_replay_inputs_missing")
    if replay.get("stored_answer_replay_allowed") is not False or replay.get("stored_hash_replay_allowed") is not False:
        failures.append("stored_answer_replay_path_present")
    if surface.get("shortcut_flags", {}).get("stored_answer_replay_path_present"):
        failures.append("stored_answer_replay_path_present")
    return sorted(set(failures))


def _future_ablation_failures(surface: dict[str, Any]) -> list[str]:
    ablation = surface.get("future_ablation_requirement", {})
    if (
        ablation.get("remove_cross_task_update_channel") is True
        and ablation.get("task_b_support_disjoint_action_change_must_collapse") is True
    ):
        return []
    return ["future_ablation_requirement_missing"]


def _anti_lookup_failures(surface: dict[str, Any], shortcut_scores: dict[str, dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    latent = surface.get("latent_generator", {})
    if not (
        latent.get("controls_task_a_target_structure")
        and latent.get("controls_task_b_target_structure")
        and latent.get("shared_across_task_a_and_task_b")
    ):
        failures.append("missing_generative_latent_state")
    if not surface.get("cross_task_prediction_error_event_ids"):
        failures.append("missing_cross_task_prediction_error_event")
    if not surface.get("shared_state_update_event_ids"):
        failures.append("missing_shared_state_update")
    if not surface.get("task_b_action_dependency_ids"):
        failures.append("missing_task_b_action_dependency")
    for record in _all_records(surface):
        if record.get("task_a", {}).get("prediction_error_under_pre_update_state") is not True:
            failures.append("missing_task_a_prediction_error")
        if record.get("task_b", {}).get("action_depends_on_shared_state_update") is not True:
            failures.append("missing_cross_task_observable")
        if record.get("task_b", {}).get("visible_features_alone_sufficient") is True:
            failures.append("task_b_visible_features_sufficient")
        hidden = record.get("hidden", {})
        if hidden.get("shared_update_required_for_task_b_action") is not True:
            failures.append("missing_cross_task_observable")
    for score in shortcut_scores.values():
        if score["reaches_threshold"]:
            reason = {
                "exact_lookup": "exact_lookup_reaches_threshold",
                "train_row_table_lookup": "table_lookup_reaches_threshold",
                "nearest_neighbor_retrieval": "nearest_neighbor_retrieval_reaches_threshold",
                "identity_key_lookup": "identity_key_lookup_reaches_threshold",
                "trace_order_lookup": "trace_order_lookup_reaches_threshold",
                "static_formula_decoder_visible_fields": "static_formula_solves_task_b",
            }[score["baseline_id"]]
            failures.append(reason)
    flags = surface.get("shortcut_flags", {})
    for flag, reason in [
        ("independent_ensemble_solves_without_shared_update", "independent_ensemble_solves_without_shared_update"),
        ("shared_latent_no_transfer_solves_task_b", "shared_latent_no_transfer_solves_task_b"),
        ("task_b_visible_features_sufficient", "task_b_visible_features_sufficient"),
    ]:
        if flags.get(flag):
            failures.append(reason)
    return sorted(set(failures))


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
        "harness_or_tournament_execution_created": False,
        "gate4_replacement_design_created": False,
        "runtime_or_mainline_path_created": False,
        "bridge_or_admission_path_created": False,
        "llm_rag_ui_companion_path_created": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def validate_surface(surface: dict[str, Any]) -> dict[str, Any]:
    shortcut_scores = compute_shortcut_scores(surface)
    support_failures = _support_disjoint_failures(surface)
    identity_failures = _identity_failures(surface)
    leakage_failures = _target_leak_failures(surface)
    static_failures = (
        ["static_formula_solves_task_b"]
        if shortcut_scores["static_formula_decoder_visible_fields"]["reaches_threshold"]
        else []
    )
    lookup_failures = []
    for score_id, reason in [
        ("exact_lookup", "exact_lookup_reaches_threshold"),
        ("train_row_table_lookup", "table_lookup_reaches_threshold"),
    ]:
        if shortcut_scores[score_id]["reaches_threshold"]:
            lookup_failures.append(reason)
    retrieval_failures = (
        ["nearest_neighbor_retrieval_reaches_threshold"]
        if shortcut_scores["nearest_neighbor_retrieval"]["reaches_threshold"]
        else []
    )
    trace_failures = (
        ["trace_order_lookup_reaches_threshold"]
        if shortcut_scores["trace_order_lookup"]["reaches_threshold"]
        else []
    )
    counterfactual_failures = _counterfactual_failures(surface)
    provenance_failures = _provenance_failures(surface)
    preregistration_failures = _baseline_preregistration_failures(surface)
    replay_failures = _future_replay_failures(surface)
    ablation_failures = _future_ablation_failures(surface)
    forbidden_guard = build_forbidden_action_guard()
    forbidden_failures = ["forbidden_files_modified"] if forbidden_guard["forbidden_files_modified"] else []
    anti_lookup_failures = _anti_lookup_failures(surface, shortcut_scores)

    validator_results = {
        "anti_lookup_generative_heldout_compliance": _validator_row(
            "anti_lookup_generative_heldout_compliance",
            anti_lookup_failures,
            shortcut_score_ids=sorted(shortcut_scores),
        ),
        "support_disjoint_train_heldout_split": _validator_row(
            "support_disjoint_train_heldout_split",
            support_failures,
        ),
        "identity_key_permutation": _validator_row("identity_key_permutation", identity_failures),
        "target_leakage": _validator_row("target_leakage", leakage_failures),
        "static_formula_solvability": _validator_row("static_formula_solvability", static_failures),
        "table_exact_lookup_solvability": _validator_row("table_exact_lookup_solvability", lookup_failures),
        "nearest_neighbor_retrieval_shortcut": _validator_row(
            "nearest_neighbor_retrieval_shortcut",
            retrieval_failures,
        ),
        "trace_order_shortcut": _validator_row("trace_order_shortcut", trace_failures),
        "counterfactual_pair_validity": _validator_row("counterfactual_pair_validity", counterfactual_failures),
        "generator_provenance_completeness": _validator_row(
            "generator_provenance_completeness",
            provenance_failures,
        ),
        "baseline_preregistration_completeness": _validator_row(
            "baseline_preregistration_completeness",
            preregistration_failures,
        ),
        "future_replay_recomputation_requirement": _validator_row(
            "future_replay_recomputation_requirement",
            replay_failures,
        ),
        "future_ablation_requirement": _validator_row("future_ablation_requirement", ablation_failures),
        "forbidden_action_guard": _validator_row("forbidden_action_guard", forbidden_failures),
    }
    blocking_reasons: list[str] = []
    for row in validator_results.values():
        blocking_reasons.extend(row["blocking_reasons"])
    return {
        "producer_function": "validate_surface",
        "task_id": TASK_CARD_ID,
        "valid": not blocking_reasons,
        "blocking_reasons": sorted(set(blocking_reasons)),
        "validator_results": validator_results,
        "shortcut_scores": shortcut_scores,
        "forbidden_action_guard": forbidden_guard,
        "claim_ceiling": CLAIM_CEILING,
    }


def _mutate_records(surface: dict[str, Any], mutator: Callable[[dict[str, Any], int], None]) -> dict[str, Any]:
    clone = copy.deepcopy(surface)
    for index, record in enumerate(_all_records(clone)):
        mutator(record, index)
    return clone


def build_invalid_positive_control_surfaces() -> dict[str, dict[str, Any]]:
    base = generate_valid_surface_fixture()
    controls: dict[str, dict[str, Any]] = {}

    exact = copy.deepcopy(base)
    train = exact["records"]["train"]
    heldout = exact["records"]["heldout"]
    for index, record in enumerate(heldout):
        source = train[index % len(train)]
        record["task_a"]["observation"] = copy.deepcopy(source["task_a"]["observation"])
        record["task_b"]["observation"] = copy.deepcopy(source["task_b"]["observation"])
        record["hidden"]["task_b_target_action"] = source["hidden"]["task_b_target_action"]
    controls["exact_lookup_surface"] = exact

    def table_mutator(record: dict[str, Any], index: int) -> None:
        target = resolve_task_b_target_action(record)
        record["task_b"]["observation"]["table_key"] = f"table_key_{index % 4}"
        record["hidden"]["task_b_target_action"] = ["inspect_boundary", "consolidate_trace", "defer_action", "defer_action"][index % 4]
        record["task_b"]["post_update_action"] = record["hidden"]["task_b_target_action"]
        record["task_b"]["observation"]["latent_binding_probe"] = f"table_probe_{index % 4}"
        record["shared_state_update"]["serialized_state_after"]["latent_action_binding"] = {
            record["task_b"]["observation"]["latent_binding_probe"]: record["hidden"]["task_b_target_action"]
        }
        if target == "":
            record["hidden"]["task_b_target_action"] = "inspect_boundary"

    controls["table_lookup_surface"] = _mutate_records(base, table_mutator)

    identity = copy.deepcopy(base)
    for index, record in enumerate(_all_records(identity)):
        record["task_b"]["observation"]["identity_key"] = f"identity_key_{index % 4}"
        record["hidden"]["task_b_target_action"] = ["inspect_boundary", "consolidate_trace", "defer_action", "defer_action"][index % 4]
    controls["identity_key_surface"] = identity

    trace = copy.deepcopy(base)
    for index, record in enumerate(trace["records"]["heldout"]):
        record["hidden"]["task_b_target_action"] = trace["records"]["train"][index]["hidden"]["task_b_target_action"]
    controls["trace_order_surface"] = trace

    static = copy.deepcopy(base)
    for record in _all_records(static):
        target = resolve_task_b_target_action(record)
        record["task_b"]["observation"]["static_formula_action"] = target
        record["task_b"]["observation"]["static_formula_key"] = f"formula_direct_{target}"
    controls["static_formula_surface"] = static

    leak = copy.deepcopy(base)
    for record in _all_records(leak):
        record["task_b"]["observation"]["target_action"] = resolve_task_b_target_action(record)
    controls["target_leak_surface"] = leak

    missing_provenance = copy.deepcopy(base)
    missing_provenance.pop("provenance", None)
    controls["missing_generator_provenance_surface"] = missing_provenance

    missing_pairs = copy.deepcopy(base)
    missing_pairs["counterfactual_pairs"] = []
    controls["missing_counterfactual_pairs_surface"] = missing_pairs

    overlap = copy.deepcopy(base)
    overlap["records"]["heldout"][0]["support_signature"] = overlap["records"]["train"][0]["support_signature"]
    controls["overlapping_train_heldout_support_surface"] = overlap

    independent = copy.deepcopy(base)
    independent["shortcut_flags"]["independent_ensemble_solves_without_shared_update"] = True
    controls["independent_ensemble_solvable_surface"] = independent

    no_transfer = copy.deepcopy(base)
    no_transfer["shortcut_flags"]["shared_latent_no_transfer_solves_task_b"] = True
    controls["shared_latent_no_transfer_solvable_surface"] = no_transfer

    visible_only = copy.deepcopy(base)
    visible_only["shortcut_flags"]["task_b_visible_features_sufficient"] = True
    for record in _all_records(visible_only):
        record["task_b"]["visible_features_alone_sufficient"] = True
    controls["visible_feature_only_task_b_surface"] = visible_only

    stored = copy.deepcopy(base)
    stored["shortcut_flags"]["stored_answer_replay_path_present"] = True
    stored["future_replay_requirement"]["stored_answer_replay_allowed"] = True
    stored["stored_answer_replay_map"] = {
        record["record_id"]: resolve_task_b_target_action(record) for record in stored["records"]["heldout"]
    }
    controls["stored_answer_replay_surface"] = stored

    hidden_label = copy.deepcopy(base)
    hidden_label["baseline_access"]["hidden_target_labels_access"] = True
    hidden_label["shortcut_flags"]["hidden_label_exposure_detected"] = True
    controls["hidden_label_exposure_surface"] = hidden_label
    return controls


def run_positive_controls(force_positive_control_pass: str | None = None) -> dict[str, Any]:
    controls = build_invalid_positive_control_surfaces()
    rows: dict[str, dict[str, Any]] = {}
    for control_id, surface in controls.items():
        validation = validate_surface(surface)
        expected_reason = EXPECTED_CONTROL_REASONS[control_id]
        failed = not validation["valid"] and expected_reason in validation["blocking_reasons"]
        if force_positive_control_pass == control_id:
            failed = False
            validation["blocking_reasons"] = [
                reason for reason in validation["blocking_reasons"] if reason != expected_reason
            ]
        rows[control_id] = {
            "control_id": control_id,
            "producer_function": "run_positive_controls",
            "expected_block_reason": expected_reason,
            "observed_valid": validation["valid"],
            "observed_blocking_reasons": validation["blocking_reasons"],
            "failed_as_expected": failed,
            "validator_code_path_hash": code_path_hash(validate_surface),
        }
    return {
        "producer_function": "run_positive_controls",
        "task_id": TASK_CARD_ID,
        "control_results": rows,
        "all_positive_controls_failed": all(row["failed_as_expected"] for row in rows.values()),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_baseline_preregistration() -> dict[str, Any]:
    baseline_rows = []
    no_disputed_access = {
        "observation_access": "fair_visible_observation_access",
        "hidden_target_labels_access": False,
        "answer_keys_access": False,
        "row_ids_access": False,
        "partner_or_context_ids_access": False,
        "trace_order_access": False,
    }
    not_independent = {
        "pomdp_shared_belief_state_update_plus_control",
        "rnn_meta_rl_hidden_state_controller",
    }
    for baseline_id in REQUIRED_BASELINES:
        receives_update = baseline_id in not_independent
        baseline_rows.append(
            {
                "baseline_id": baseline_id,
                "producer_function": f"future_baselines.{baseline_id}",
                "code_path_hash": code_path_hash(build_baseline_preregistration),
                **no_disputed_access,
                "receives_disputed_cross_task_update_channel": receives_update,
                "independence_classification": "not_independent" if receives_update else "independent_baseline",
                "admissibility_rule": (
                    "fair visible observations only; no hidden targets, answer keys, row IDs, partner/context IDs, "
                    "trace order, or disputed update channel unless explicitly classified not independent"
                ),
            }
        )
    return {
        "producer_function": "build_baseline_preregistration",
        "task_id": TASK_CARD_ID,
        "baseline_ids": list(REQUIRED_BASELINES),
        "baselines": baseline_rows,
        "registered_before_candidate_code": True,
        "candidate_code_created": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_inherited_boundary_readback() -> dict[str, Any]:
    remote = _read_remote_refs(
        f"refs/tags/{G0_ROUTE_TAG}",
        f"refs/tags/{G0_RECONCILIATION_TAG}",
        f"refs/heads/{BRANCH}",
    )
    local_route_tag = _safe_git(["rev-parse", G0_ROUTE_TAG])
    local_reconciliation_tag = _safe_git(["rev-parse", G0_RECONCILIATION_TAG])
    current_head = _safe_git(["rev-parse", "HEAD"])
    remote_route_tag = remote.get(f"refs/tags/{G0_ROUTE_TAG}", "")
    remote_reconciliation_tag = remote.get(f"refs/tags/{G0_RECONCILIATION_TAG}", "")
    remote_branch = remote.get(f"refs/heads/{BRANCH}", "")
    route_verified = local_route_tag == G0_ROUTE_SPEC_ANCHOR and remote_route_tag == G0_ROUTE_SPEC_ANCHOR
    reconciliation_is_ancestor = _is_ancestor(G0_RECONCILIATION_ANCHOR, current_head)
    reconciliation_verified = (
        local_reconciliation_tag == G0_RECONCILIATION_ANCHOR
        and remote_reconciliation_tag == G0_RECONCILIATION_ANCHOR
        and reconciliation_is_ancestor
    )
    return {
        "producer_function": "build_inherited_boundary_readback",
        "task_id": TASK_CARD_ID,
        "g0_route_spec_anchor": G0_ROUTE_SPEC_ANCHOR,
        "g0_anchor_status_reconciliation_anchor": G0_RECONCILIATION_ANCHOR,
        "g0_survival_claim": "spec-level only",
        "local_route_tag_hash": local_route_tag,
        "remote_route_tag_hash": remote_route_tag,
        "local_reconciliation_tag_hash": local_reconciliation_tag,
        "remote_reconciliation_tag_hash": remote_reconciliation_tag,
        "current_head": current_head,
        "remote_branch_hash": remote_branch,
        "route_anchor_exact_match": route_verified,
        "reconciliation_anchor_exact_match": reconciliation_verified,
        "reconciliation_anchor_is_ancestor_of_head": reconciliation_is_ancestor,
        "inherited_boundaries_verified": route_verified and reconciliation_verified,
        "candidate_status_inherited": False,
        "harness_status_inherited": False,
        "tournament_status_inherited": False,
        "gate4_status_inherited": False,
        "runtime_status_inherited": False,
        "bridge_or_admission_status_inherited": False,
        "ego_mainline_status_inherited": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_surface_protocol() -> dict[str, Any]:
    return {
        "producer_function": "build_surface_protocol",
        "task_id": TASK_CARD_ID,
        "surface_design_only": True,
        "minimum_task_family_count": 2,
        "allowed_task_families": list(TASK_FAMILIES),
        "composite_observable": (
            "Task A prediction error updates shared internal state; the updated state changes Task B "
            "support-disjoint action selection without target, lookup, identity, trace-order, or stored-answer leakage."
        ),
        "validator_ids": list(VALIDATOR_IDS),
        "required_positive_controls": sorted(EXPECTED_CONTROL_REASONS),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_future_acceptance_gate() -> dict[str, Any]:
    return {
        "producer_function": "build_future_acceptance_gate",
        "task_id": TASK_CARD_ID,
        "accept_only_if_inherited_boundary_readback_preserved": True,
        "accept_only_if_valid_generated_fixture_passes": True,
        "accept_only_if_all_positive_controls_fail": True,
        "accept_only_if_baseline_preregistration_complete": True,
        "future_replay_must_recompute_task_b_action": True,
        "future_ablation_must_remove_cross_task_update_channel": True,
        "candidate_implementation_authorized": False,
        "harness_or_tournament_execution_authorized": False,
        "gate4_replacement_design_authorized": False,
        "runtime_bridge_admission_or_ego_mainline_authorized": False,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_claim_ceiling() -> dict[str, Any]:
    return {
        "producer_function": "build_claim_ceiling",
        "task_id": TASK_CARD_ID,
        "claim_ceiling": CLAIM_CEILING,
        "allowed_claims": [
            "surface-design package exists",
            "callable validators execute on generated fixture",
            "positive controls fail under the validators",
            "future baseline, replay, and ablation requirements are preregistered",
        ],
        "forbidden_claims": list(CLAIM_EXCLUSIONS),
    }


def compute_result(
    *,
    inherited: dict[str, Any],
    valid_validation: dict[str, Any],
    positive_controls: dict[str, Any],
    forbidden_guard: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    stop_conditions: list[str] = []
    if not inherited["inherited_boundaries_verified"]:
        stop_conditions.append("inherited_boundary_readback_failure")
    if not valid_validation["valid"]:
        reasons = set(valid_validation["blocking_reasons"])
        if reasons & LOOKUP_BLOCK_REASONS:
            stop_conditions.append("valid_fixture_lookup_solvable")
        if "missing_cross_task_observable" in reasons or "missing_task_b_action_dependency" in reasons:
            stop_conditions.append("missing_cross_task_observable")
        if "missing_generator_provenance" in reasons:
            stop_conditions.append("missing_provenance")
        if not stop_conditions:
            stop_conditions.append("valid_fixture_invalid")
    for control_id, row in positive_controls["control_results"].items():
        if not row["failed_as_expected"]:
            stop_conditions.append(f"positive_control_mismatch:{control_id}")
    if forbidden_guard["forbidden_files_modified"]:
        stop_conditions.append("forbidden_files_modified")
    for key in [
        "candidate_code_created",
        "candidate_score_produced",
        "harness_or_tournament_execution_created",
        "gate4_replacement_design_created",
        "runtime_or_mainline_path_created",
        "bridge_or_admission_path_created",
        "llm_rag_ui_companion_path_created",
    ]:
        if forbidden_guard[key]:
            stop_conditions.append(key)

    if any(item.startswith("positive_control_mismatch:") for item in stop_conditions):
        verdict = "composite_cross_task_state_reuse_generative_heldout_surface_design_001a_blocked_by_positive_control_failure"
    elif "valid_fixture_lookup_solvable" in stop_conditions:
        verdict = "composite_cross_task_state_reuse_generative_heldout_surface_design_001a_blocked_by_valid_fixture_lookup_solvable"
    elif "missing_cross_task_observable" in stop_conditions:
        verdict = "composite_cross_task_state_reuse_generative_heldout_surface_design_001a_blocked_by_missing_cross_task_observable"
    elif "missing_provenance" in stop_conditions:
        verdict = "composite_cross_task_state_reuse_generative_heldout_surface_design_001a_blocked_by_missing_provenance"
    elif any(
        condition
        in {
            "forbidden_files_modified",
            "candidate_code_created",
            "candidate_score_produced",
            "harness_or_tournament_execution_created",
            "gate4_replacement_design_created",
            "runtime_or_mainline_path_created",
            "bridge_or_admission_path_created",
            "llm_rag_ui_companion_path_created",
        }
        for condition in stop_conditions
    ):
        verdict = "composite_cross_task_state_reuse_generative_heldout_surface_design_001a_blocked_by_forbidden_action"
    elif "inherited_boundary_readback_failure" in stop_conditions:
        verdict = "composite_cross_task_state_reuse_generative_heldout_surface_design_001a_blocked_by_missing_provenance"
    elif stop_conditions:
        verdict = "composite_cross_task_state_reuse_generative_heldout_surface_design_001a_blocked_by_missing_cross_task_observable"
    else:
        verdict = "composite_cross_task_state_reuse_generative_heldout_surface_design_001a_pass"

    return {
        "producer_function": "compute_result",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "verdict": verdict,
        "current_layer": "engineering-governance / anti-lookup generative heldout surface design only",
        "mainline_integration_status": "not integrated",
        "enabled_status": (
            "no runtime, no bridge/admission, no Gate4 replacement, no candidate implementation, "
            "no tournament execution, no trigger path"
        ),
        "real_trigger_evidence": (
            "Callable generator and validators executed on one generated valid fixture and fourteen invalid "
            "positive-control surfaces; parent boundary anchors were read back from git."
        ),
        "claim_ceiling": CLAIM_CEILING,
        "stop_conditions_triggered": sorted(set(stop_conditions)),
        "candidate_code_created": forbidden_guard["candidate_code_created"],
        "candidate_score_produced": forbidden_guard["candidate_score_produced"],
        "harness_or_tournament_execution_created": forbidden_guard["harness_or_tournament_execution_created"],
        "gate4_replacement_design_created": forbidden_guard["gate4_replacement_design_created"],
        "runtime_or_mainline_path_created": forbidden_guard["runtime_or_mainline_path_created"],
        "bridge_or_admission_path_created": forbidden_guard["bridge_or_admission_path_created"],
        "llm_rag_ui_companion_path_created": forbidden_guard["llm_rag_ui_companion_path_created"],
        "auto_remote_anchor": AUTO_REMOTE_ANCHOR,
        "remote_anchor_performed": False,
        "next_minimal_closed_loop_action": (
            "After independent review, use this surface-design boundary as input to a separate bounded task for "
            "future executable surface generation or candidate evaluation; do not infer mechanism validity from it."
        ),
        "what_this_does_not_prove": list(CLAIM_EXCLUSIONS),
    }


def _resolve_output_dir(output_dir: str | Path | None) -> Path:
    if output_dir is None:
        return repo_root() / "artifacts" / ARTIFACT_DIR_NAME
    path = Path(output_dir)
    return path if path.is_absolute() else repo_root() / path


def execute_design(
    output_dir: str | Path | None = None,
    *,
    persist_artifacts: bool = True,
    force_positive_control_pass: str | None = None,
    test_result_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    run_id = f"{TASK_ID}_{_now().replace('-', '').replace(':', '').replace('Z', 'Z')}"
    inherited = build_inherited_boundary_readback()
    protocol = build_surface_protocol()
    valid_fixture = generate_valid_surface_fixture()
    valid_validation = validate_surface(valid_fixture)
    positive_controls = run_positive_controls(force_positive_control_pass=force_positive_control_pass)
    preregistration = build_baseline_preregistration()
    future_gate = build_future_acceptance_gate()
    claim_ceiling = build_claim_ceiling()
    forbidden_guard = build_forbidden_action_guard()
    result = compute_result(
        inherited=inherited,
        valid_validation=valid_validation,
        positive_controls=positive_controls,
        forbidden_guard=forbidden_guard,
        run_id=run_id,
    )
    if test_result_readback is not None:
        result["test_result_readback"] = test_result_readback
    run = {
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "result": result,
        "inherited_boundary_readback": inherited,
        "surface_protocol": protocol,
        "valid_generated_surface_fixture": valid_fixture,
        "valid_generated_surface_validation": valid_validation,
        "invalid_positive_controls": positive_controls,
        "baseline_preregistration": preregistration,
        "future_acceptance_gate": future_gate,
        "claim_ceiling": claim_ceiling,
        "forbidden_action_guard": forbidden_guard,
    }
    if persist_artifacts:
        write_artifacts(_resolve_output_dir(output_dir), run)
    return run


def write_artifacts(out: Path, run: dict[str, Any]) -> None:
    artifact_map = {
        "result.json": run["result"],
        "inherited_boundary_readback.json": run["inherited_boundary_readback"],
        "surface_protocol.json": run["surface_protocol"],
        "valid_generated_surface_fixture.json": run["valid_generated_surface_fixture"],
        "invalid_positive_controls.json": run["invalid_positive_controls"],
        "baseline_preregistration.json": run["baseline_preregistration"],
        "future_acceptance_gate.json": run["future_acceptance_gate"],
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
    inherited = run["inherited_boundary_readback"]
    controls = run["invalid_positive_controls"]["control_results"]
    lines = [
        "# COMPOSITE-CROSS-TASK-STATE-REUSE-GENERATIVE-HELDOUT-SURFACE-DESIGN-001A",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        "Layer: engineering-governance / anti-lookup generative heldout surface design only.",
        "",
        "Mainline integration status: not integrated.",
        "",
        "Enabled status: no runtime, no bridge/admission, no Gate4 replacement, no candidate implementation, no tournament execution, no trigger path.",
        "",
        f"Claim ceiling: {CLAIM_CEILING}",
        "",
        "Auto-Remote-Anchor: conditional.",
        "",
        "## Bounded Audit",
        "",
        "- Real objective: create a generated surface-design boundary for a later test of cross-task prediction-error state reuse under support-disjoint heldout conditions.",
        "- Strongest baseline explanation: lookup, table, identity, trace-order, visible static formula, independent per-task ensemble, or shared-latent/no-transfer shortcuts could reproduce behavior without the disputed update channel.",
        "- Strongest invalidity reason: a generated fixture that passes by labels, IDs, row order, static visible fields, stored answers, or hidden-label exposure would not increase discriminative mechanism evidence.",
        "- Falsifier: valid fixture lookup solvability, failed positive controls, missing provenance, missing cross-task observable, forbidden path creation, or parent-boundary readback failure.",
        "- Evidence still insufficient: this is not candidate behavior, tournament evidence, Gate4 evidence, runtime evidence, or bridge/admission evidence.",
        "- Mechanism-vs-resemblance classification: this is protocol-governance for a future fail-able surface, not mechanism validation.",
        "",
        "## Bounded Task Card",
        "",
        f"- Task id: `{TASK_CARD_ID}`",
        "- Problem definition: the composite route survived G0 only at spec level and needs an anti-lookup generative heldout surface contract before candidate implementation, harness, tournament, or Gate4 replacement design.",
        "- Current stage/layer: engineering-governance / anti-lookup generative heldout surface design only.",
        "- Mainline target: none; not integrated.",
        "- Enabled-state requirement: no runtime, bridge/admission, Gate4 replacement, candidate implementation, tournament execution, or trigger path.",
        "- Real-trigger evidence requirement: callable generator and validators must execute on a valid fixture and positive-control surfaces.",
        "- Hypothesis: Task A prediction error updates a shared hidden state, and that update changes Task B support-disjoint action selection without lookup or target leakage.",
        "- Strongest baseline: exact lookup, table lookup, nearest-neighbor retrieval, identity-key lookup, trace-order lookup, static formula decoder, independent per-task ensemble, shared-latent/no-transfer, multi-task representation learning, POMDP/shared belief control, RNN/meta-RL, Dyna-Q/prioritized sweeping, MPC/world-model planner, causal bandit, and oracle feature-sharing without the disputed update channel.",
        "- Ablation requirement: removing the cross-task update channel must collapse the Task B support-disjoint action-selection change while preserving local per-task behavior where possible.",
        "- Trace/replay requirement: future replay must recompute Task B action from serialized_state + new observation, not stored answers or stored hashes.",
        "- Computed-evidence provenance gate: generated fixtures record generator function, seed, latent parameter IDs, train/heldout IDs, task family IDs, support signatures, counterfactual pair IDs, prediction-error event IDs, shared-state update IDs, Task B dependency IDs, target resolver path, code path hash, and baseline preregistration.",
        "- Acceptance gate: inherited boundary readback preserved, valid fixture passes, all positive controls fail, baselines preregistered, future replay and ablation explicit, forbidden paths absent, tests pass.",
        f"- Claim ceiling: {CLAIM_CEILING}",
        "- Stop condition: parent-boundary mismatch, positive-control failure, lookup-solvable valid fixture, missing cross-task observable, missing provenance, forbidden action, or claim inflation.",
        "- Rollback plan: remove only isolated 001A source, test, report, and artifact paths.",
        "- Expected changed files: isolated source package, focused test, report, and artifact directory for this task.",
        "- Forbidden changes: candidate model code, candidate score, harness, tournament execution, Gate4 replacement design, runtime, bridge/admission, EGO-mainline, LLM/RAG/UI/companion paths.",
        "- Auto-Remote-Anchor decision: conditional.",
        "",
        "## Inherited Boundary Readback",
        "",
        f"- G0 route-spec anchor: `{inherited['g0_route_spec_anchor']}`",
        f"- G0 anchor-status reconciliation anchor: `{inherited['g0_anchor_status_reconciliation_anchor']}`",
        f"- G0 survival claim inherited: `{inherited['g0_survival_claim']}`",
        f"- Route anchor exact match: `{inherited['route_anchor_exact_match']}`",
        f"- Reconciliation anchor exact match: `{inherited['reconciliation_anchor_exact_match']}`",
        "- No candidate, harness, tournament, Gate4, runtime, bridge/admission, or EGO-mainline status is inherited.",
        "",
        "## Validator Positive Controls",
        "",
    ]
    for control_id in sorted(controls):
        row = controls[control_id]
        lines.append(
            f"- `{control_id}` expected `{row['expected_block_reason']}` observed `{row['observed_blocking_reasons']}` failed as expected `{row['failed_as_expected']}`."
        )
    lines.extend(
        [
            "",
            "## Baseline Preregistration",
            "",
            "- Baselines are preregistered before candidate code and receive fair visible observation access only.",
            "- Hidden target labels, answer keys, row IDs, partner/context IDs, trace order, and disputed update-channel access are denied unless a baseline is explicitly classified not independent.",
            "",
            "## Future Replay And Ablation",
            "",
            "- Replay recomputation requirement: future candidates must recompute Task B action from serialized_state + new observation.",
            "- Stored-answer replay and stored-hash replay are forbidden.",
            "- Required ablation: remove the cross-task prediction-error update channel and require the support-disjoint Task B action-selection change to collapse.",
            "",
            "## Forbidden-Action Guard",
            "",
            f"- Candidate code created: `{run['forbidden_action_guard']['candidate_code_created']}`",
            f"- Candidate score produced: `{run['forbidden_action_guard']['candidate_score_produced']}`",
            f"- Harness or tournament execution created: `{run['forbidden_action_guard']['harness_or_tournament_execution_created']}`",
            f"- Gate4 replacement design created: `{run['forbidden_action_guard']['gate4_replacement_design_created']}`",
            f"- Runtime/mainline path created: `{run['forbidden_action_guard']['runtime_or_mainline_path_created']}`",
            f"- Bridge/admission path created: `{run['forbidden_action_guard']['bridge_or_admission_path_created']}`",
            f"- LLM/RAG/UI/companion path created: `{run['forbidden_action_guard']['llm_rag_ui_companion_path_created']}`",
            f"- Forbidden files modified: `{run['forbidden_action_guard']['forbidden_files_modified']}`",
            "- No candidate model, harness, tournament, Gate4 replacement, runtime, bridge/admission, EGO-mainline, LLM/RAG/UI, or companion path is authorized.",
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
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--test-command", default=None)
    parser.add_argument("--test-exit-code", default=None)
    parser.add_argument("--test-summary", default=None)
    args = parser.parse_args()
    test_readback = None
    if args.test_command is not None:
        test_readback = {
            "command": args.test_command,
            "exit_code": int(args.test_exit_code) if args.test_exit_code is not None else None,
            "summary": args.test_summary or "",
        }
    run = execute_design(
        output_dir=args.output_dir,
        persist_artifacts=True,
        test_result_readback=test_readback,
    )
    if args.write_report:
        write_research_report(run)
    print(json.dumps(run["result"], indent=2, sort_keys=True))
