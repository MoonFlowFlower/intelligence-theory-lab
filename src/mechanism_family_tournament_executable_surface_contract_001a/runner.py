from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import (
    ARTIFACT_DIR_NAME,
    AUTO_REMOTE_ANCHOR,
    CLAIM_CEILING,
    INHERITED_HEAD_ANCHOR,
    INHERITED_TASK_CARD_ID,
    REPORT_NAME,
    TASK_CARD_ID,
    TASK_ID,
)
from .surfaces import SurfaceContractViolation


BRANCH = "codex/meta-theory-scaffold"
SURFACE_MODULE = "mechanism_family_tournament_executable_surface_contract_001a.surfaces"
ARTIFACT_INPUTS = [
    Path("docs/research/MECHANISM-FAMILY-TOURNAMENT-BASELINE-PREFLIGHT-001A.md"),
    Path("artifacts/mechanism_family_tournament_baseline_preflight_001a/needs_redesign.json"),
    Path("artifacts/mechanism_family_tournament_entry_criteria_001a/candidate_family_registry.json"),
    Path("artifacts/mechanism_family_tournament_entry_criteria_001a/family_baseline_matrix.json"),
    Path("artifacts/mechanism_family_tournament_entry_criteria_001a/family_transfer_counterfactual_matrix.json"),
]
REQUIRED_CONTRACT_FIELDS = [
    "family_id",
    "observation_schema",
    "allowed_input_fields",
    "forbidden_target_derived_fields",
    "target_resolver",
    "metric_function",
    "numeric_threshold",
    "threshold_rationale",
    "cheap_baseline_attack_surface",
    "leakage_detector_list",
    "positive_control_malformed_fixture",
    "minimum_baseline_preflight_eligibility",
]
EXPECTED_FAMILY_IDS = [
    "causal_world_model_control",
    "jepa_like_latent_prediction",
    "replay_consolidation_adaptation",
    "self_boundary_controllability_model",
    "viability_value_gated_prediction_action_loop",
    "social_latent_inference_without_partner_id_lookup",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return completed.stdout.strip()
    except Exception:
        return ""


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


def _load_json(path: Path) -> Any:
    return json.loads((repo_root() / path).read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_path_hash() -> str:
    paths = [
        repo_root() / "src" / TASK_ID / "__init__.py",
        repo_root() / "src" / TASK_ID / "surfaces.py",
        repo_root() / "src" / TASK_ID / "runner.py",
    ]
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _function_path(name: str) -> str:
    return f"{SURFACE_MODULE}.{name}"


def _resolve_function(dotted_path: str) -> Any:
    module_name, function_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


def _family_contracts() -> list[dict[str, Any]]:
    return [
        {
            "family_id": "causal_world_model_control",
            "observation_schema": {
                "state_features": "object with non-target state descriptors",
                "action": "string action handle",
                "intervention": "string intervention handle",
                "previous_transition_summary": "string or object without outcome labels",
            },
            "allowed_input_fields": [
                "state_features",
                "action",
                "intervention",
                "previous_transition_summary",
            ],
            "forbidden_target_derived_fields": [
                "target",
                "target_label",
                "intervention_consequence_class",
                "consequence_label",
                "state_action_answer_key",
                "transition_target",
            ],
            "target_resolver": _function_path("resolve_causal_world_model_control_target"),
            "metric_function": _function_path("exact_match_accuracy"),
            "numeric_threshold": 0.8,
            "threshold_rationale": "Cheap-baseline invalidation threshold for exact-match heldout intervention consequences; reuses the prior no-candidate 0.8 kill threshold before any candidate result exists.",
            "cheap_baseline_attack_surface": [
                "state_action_lookup_table",
                "model_free_action_frequency_baseline",
                "oracle_visible_feature_shortcut",
                "nearest_neighbor_transition_retrieval",
                "ngram_trajectory_lookup",
            ],
            "leakage_detector_list": [
                "forbidden_visible_target_field_scanner",
                "state_action_answer_key_scanner",
                "context_or_row_index_target_scanner",
                "static_transition_formula_scanner",
            ],
            "sample_valid_record": {
                "observation": {
                    "state_features": {"zone": "s1", "load": "medium"},
                    "action": "redirect_flow",
                    "intervention": "valve_shift",
                    "previous_transition_summary": "no direct outcome labels",
                },
                "target_source": {"intervention_consequence_class": "stabilizes"},
            },
        },
        {
            "family_id": "jepa_like_latent_prediction",
            "observation_schema": {
                "current_observation_features": "object with visible non-target features",
                "masked_future_boundary": "string boundary marker without answer key",
                "transition_context": "string context handle without target label",
                "perturbation_handle": "string perturbation handle",
            },
            "allowed_input_fields": [
                "current_observation_features",
                "masked_future_boundary",
                "transition_context",
                "perturbation_handle",
            ],
            "forbidden_target_derived_fields": [
                "target",
                "target_label",
                "future_transition_class",
                "future_state_id",
                "latent_answer_key",
                "transition_label",
            ],
            "target_resolver": _function_path("resolve_jepa_like_latent_prediction_target"),
            "metric_function": _function_path("exact_match_accuracy"),
            "numeric_threshold": 0.8,
            "threshold_rationale": "Cheap-baseline invalidation threshold for heldout transition-class discrimination; set before candidate code and high enough to close retrieval or decoder-solvable surfaces.",
            "cheap_baseline_attack_surface": [
                "frozen_random_or_pretrained_encoder_baseline",
                "nearest_neighbor_latent_retrieval",
                "supervised_target_shortcut",
                "bag_of_observation_feature_baseline",
                "trace_only_decoder_baseline",
            ],
            "leakage_detector_list": [
                "latent_answer_key_scanner",
                "trace_index_target_scanner",
                "filename_target_label_scanner",
                "decoder_visible_bundle_scanner",
            ],
            "sample_valid_record": {
                "observation": {
                    "current_observation_features": {"shape": "paired", "phase": "pre"},
                    "masked_future_boundary": "future_window_a",
                    "transition_context": "composition_split_02",
                    "perturbation_handle": "swap_dynamics",
                },
                "target_source": {"future_transition_class": "relation_preserved"},
            },
        },
        {
            "family_id": "replay_consolidation_adaptation",
            "observation_schema": {
                "serialized_state_hash": "string hash of pre-replay state",
                "replay_event_summary": "object without stored answers",
                "heldout_observation": "object for recomputation",
                "replay_order_marker": "string non-answer order marker",
            },
            "allowed_input_fields": [
                "serialized_state_hash",
                "replay_event_summary",
                "heldout_observation",
                "replay_order_marker",
            ],
            "forbidden_target_derived_fields": [
                "target",
                "target_label",
                "post_replay_behavior_class",
                "stored_answer_hash",
                "replay_answer_key",
                "episode_target",
            ],
            "target_resolver": _function_path("resolve_replay_consolidation_adaptation_target"),
            "metric_function": _function_path("exact_match_accuracy"),
            "numeric_threshold": 0.8,
            "threshold_rationale": "Cheap-baseline invalidation threshold for post-replay behavior class under recomputation; closes cache or stored-answer surfaces before candidate work.",
            "cheap_baseline_attack_surface": [
                "no_replay",
                "shuffled_replay",
                "cache_replay",
                "stored_answer_replay",
                "retrieval_over_previous_traces",
                "hash_comparison_replay",
            ],
            "leakage_detector_list": [
                "stored_answer_hash_scanner",
                "replay_buffer_target_scanner",
                "episode_id_answer_key_scanner",
                "hash_only_replay_scanner",
            ],
            "sample_valid_record": {
                "observation": {
                    "serialized_state_hash": "statehash001",
                    "replay_event_summary": {"events": ["e1", "e2"], "labels": []},
                    "heldout_observation": {"probe": "new_context"},
                    "replay_order_marker": "causal_order_a",
                },
                "target_source": {"post_replay_behavior_class": "updates_response"},
            },
        },
        {
            "family_id": "self_boundary_controllability_model",
            "observation_schema": {
                "variable_handle": "opaque variable handle",
                "intervention_attempt": "string intervention handle",
                "observed_delta": "object with non-label delta values",
                "feedback_window": "string feedback interval",
            },
            "allowed_input_fields": [
                "variable_handle",
                "intervention_attempt",
                "observed_delta",
                "feedback_window",
            ],
            "forbidden_target_derived_fields": [
                "target",
                "target_label",
                "controllability_attribution_class",
                "self_other_label",
                "role_label",
                "boundary_answer_key",
            ],
            "target_resolver": _function_path("resolve_self_boundary_controllability_model_target"),
            "metric_function": _function_path("exact_match_accuracy"),
            "numeric_threshold": 0.8,
            "threshold_rationale": "Cheap-baseline invalidation threshold for heldout controllability attribution; blocks static role, name, and partition shortcuts before mechanism testing.",
            "cheap_baseline_attack_surface": [
                "variable_name_heuristic",
                "intervention_lookup_table",
                "state_delta_frequency_baseline",
                "oracle_controllability_label_baseline",
                "fixed_self_other_partition_baseline",
            ],
            "leakage_detector_list": [
                "role_label_scanner",
                "semantic_variable_name_scanner",
                "fixed_position_mask_scanner",
                "generator_role_field_scanner",
            ],
            "sample_valid_record": {
                "observation": {
                    "variable_handle": "var_17",
                    "intervention_attempt": "nudge_plus",
                    "observed_delta": {"magnitude": "partial", "direction": "up"},
                    "feedback_window": "window_b",
                },
                "target_source": {"controllability_attribution_class": "self_caused_partial"},
            },
        },
        {
            "family_id": "viability_value_gated_prediction_action_loop",
            "observation_schema": {
                "state_features": "object with non-answer state descriptors",
                "action_options": "list of opaque action handles",
                "prediction_error_signal": "numeric or bucketed error signal",
                "viability_pressure_signal": "numeric or bucketed non-label pressure",
                "delayed_consequence_context": "string context handle",
            },
            "allowed_input_fields": [
                "state_features",
                "action_options",
                "prediction_error_signal",
                "viability_pressure_signal",
                "delayed_consequence_context",
            ],
            "forbidden_target_derived_fields": [
                "target",
                "target_label",
                "delayed_viability_action_class",
                "viability_label",
                "risk_label",
                "reward_answer_key",
            ],
            "target_resolver": _function_path("resolve_viability_value_gated_prediction_action_loop_target"),
            "metric_function": _function_path("exact_match_accuracy"),
            "numeric_threshold": 0.8,
            "threshold_rationale": "Cheap-baseline invalidation threshold for delayed consequence action class; blocks static reward, myopic, and risk-label shortcuts before candidate work.",
            "cheap_baseline_attack_surface": [
                "static_reward_lookup",
                "myopic_greedy_policy",
                "fixed_risk_avoidance_heuristic",
                "action_frequency_baseline",
                "oracle_viability_label_shortcut",
                "state_action_reward_triple_table",
            ],
            "leakage_detector_list": [
                "immediate_reward_target_scanner",
                "fixed_risk_label_scanner",
                "state_action_reward_answer_key_scanner",
                "oracle_viability_label_scanner",
            ],
            "sample_valid_record": {
                "observation": {
                    "state_features": {"resource": "low", "volatility": "high"},
                    "action_options": ["probe", "preserve", "spend"],
                    "prediction_error_signal": "large",
                    "viability_pressure_signal": "conserve",
                    "delayed_consequence_context": "lagged_effect_split",
                },
                "target_source": {"delayed_viability_action_class": "preserve"},
            },
        },
        {
            "family_id": "social_latent_inference_without_partner_id_lookup",
            "observation_schema": {
                "interaction_observation": "object with non-identity interaction cues",
                "feedback_signal": "string or object feedback cue",
                "history_summary_without_identity": "object with identity-free dynamics",
                "identity_permutation_epoch": "string permutation boundary marker",
            },
            "allowed_input_fields": [
                "interaction_observation",
                "feedback_signal",
                "history_summary_without_identity",
                "identity_permutation_epoch",
            ],
            "forbidden_target_derived_fields": [
                "target",
                "target_label",
                "latent_response_class",
                "partner_id",
                "partner_key",
                "anonymized_partner_key",
                "profile_id",
                "preference_table",
                "social_answer_key",
            ],
            "target_resolver": _function_path(
                "resolve_social_latent_inference_without_partner_id_lookup_target"
            ),
            "metric_function": _function_path("exact_match_accuracy"),
            "numeric_threshold": 0.8,
            "threshold_rationale": "Cheap-baseline invalidation threshold for identity-permuted heldout response class; preserves the prior partner-ID negative evidence and blocks identity/profile lookup.",
            "cheap_baseline_attack_surface": [
                "partner_id_lookup",
                "anonymized_partner_key_lookup",
                "preference_table_reconstruction",
                "prior_trace_retrieval",
                "order_k_partner_history",
                "profile_table_baseline",
                "ngram_trace_lookup",
                "query_conditioned_imitation",
                "graph_cache_baseline",
                "full_bundle_decoder",
            ],
            "leakage_detector_list": [
                "partner_id_visible_field_scanner",
                "anonymized_partner_key_scanner",
                "preference_table_scanner",
                "profile_or_context_id_scanner",
                "full_bundle_decoder_positive_control",
            ],
            "sample_valid_record": {
                "observation": {
                    "interaction_observation": {"turn": "challenge", "affordance": "clarify"},
                    "feedback_signal": "partner_policy_shift_visible_only_as_feedback",
                    "history_summary_without_identity": {"recent": ["ask", "revise"]},
                    "identity_permutation_epoch": "perm_epoch_03",
                },
                "target_source": {"latent_response_class": "ask_constraint_question"},
            },
        },
    ]


def _with_positive_controls(families: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched = []
    for family in families:
        item = json.loads(json.dumps(family))
        forbidden_field = next(
            field
            for field in item["forbidden_target_derived_fields"]
            if field not in {"target", "target_label"}
        )
        malformed = json.loads(json.dumps(item["sample_valid_record"]))
        malformed["observation"][forbidden_field] = "VISIBLE_TARGET_LEAK_POSITIVE_CONTROL"
        item["positive_control_malformed_fixture"] = {
            "family_id": item["family_id"],
            "malformation": "forbidden_target_derived_field_visible",
            "injected_field": forbidden_field,
            "record": malformed,
        }
        item["minimum_baseline_preflight_eligibility"] = True
        enriched.append(item)
    return enriched


def build_family_surface_contract() -> dict[str, Any]:
    families = _with_positive_controls(_family_contracts())
    return {
        "task_id": TASK_CARD_ID,
        "inherited_task_id": INHERITED_TASK_CARD_ID,
        "inherited_head_anchor": INHERITED_HEAD_ANCHOR,
        "process_mode": "engineering-governance / executable surface contract repair only",
        "families": families,
        "candidate_code_authorized": False,
        "candidate_score_authorized": False,
        "baseline_preflight_rerun_authorized_if_validation_passes": True,
        "tournament_execution_authorized": False,
        "gate4_replacement_authorized": False,
        "runtime_or_mainline_authorized": False,
        "auto_remote_anchor": AUTO_REMOTE_ANCHOR,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_source_pin_readback() -> dict[str, Any]:
    current_head = _git(["rev-parse", "HEAD"])
    branch = _git(["branch", "--show-current"])
    status = _git(["status", "--short", "--branch"])
    ancestor_check = subprocess.run(
        ["git", "merge-base", "--is-ancestor", INHERITED_HEAD_ANCHOR, "HEAD"],
        cwd=repo_root(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).returncode == 0
    source_pin_boundary_ok = current_head == INHERITED_HEAD_ANCHOR or ancestor_check
    return {
        "producer_function": "build_source_pin_readback",
        "task_id": TASK_CARD_ID,
        "branch": branch,
        "expected_branch": BRANCH,
        "current_head": current_head,
        "inherited_head_anchor": INHERITED_HEAD_ANCHOR,
        "current_head_matches_inherited_anchor": current_head == INHERITED_HEAD_ANCHOR,
        "inherited_head_anchor_is_ancestor_of_current_head": ancestor_check,
        "source_pin_boundary_ok": source_pin_boundary_ok,
        "git_status_short_branch": status,
        "source_inputs": [
            {
                "path": str(path).replace("\\", "/"),
                "sha256": sha256_file(repo_root() / path),
            }
            for path in ARTIFACT_INPUTS
            if (repo_root() / path).exists()
        ],
        "claim_ceiling": "source-pin and inherited-gap readback only",
    }


def validate_family_surface(family: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_CONTRACT_FIELDS if field not in family]
    target_callable = False
    metric_callable = False
    sample_target_resolved = False
    metric_smoke_check_passed = False
    resolver_error = None
    metric_error = None
    sample_target = None
    metric_smoke_value = None
    try:
        resolver = _resolve_function(family["target_resolver"])
        target_callable = callable(resolver)
        sample_target = resolver(family["sample_valid_record"])
        sample_target_resolved = isinstance(sample_target, str) and bool(sample_target)
    except Exception as exc:
        resolver_error = getattr(exc, "reason", str(exc))
    try:
        metric = _resolve_function(family["metric_function"])
        metric_callable = callable(metric)
        if sample_target is not None:
            metric_smoke_value = metric([sample_target], [sample_target])
            metric_smoke_check_passed = metric_smoke_value == 1.0
    except Exception as exc:
        metric_error = getattr(exc, "reason", str(exc))

    threshold = family.get("numeric_threshold")
    threshold_is_numeric = isinstance(threshold, (int, float)) and 0 < threshold < 1
    allowed_fields_ok = set(family.get("allowed_input_fields", [])).issubset(
        set(family.get("observation_schema", {}).keys())
    )
    visible_forbidden_disjoint = set(family.get("allowed_input_fields", [])).isdisjoint(
        set(family.get("forbidden_target_derived_fields", []))
    )
    eligible = (
        not missing
        and target_callable
        and metric_callable
        and sample_target_resolved
        and metric_smoke_check_passed
        and threshold_is_numeric
        and bool(family.get("threshold_rationale"))
        and bool(family.get("cheap_baseline_attack_surface"))
        and bool(family.get("leakage_detector_list"))
        and allowed_fields_ok
        and visible_forbidden_disjoint
        and family.get("minimum_baseline_preflight_eligibility") is True
    )
    blocking = []
    if missing:
        blocking.extend(f"missing_field:{field}" for field in missing)
    if not target_callable:
        blocking.append("target_resolver_not_callable")
    if not metric_callable:
        blocking.append("metric_function_not_callable")
    if not sample_target_resolved:
        blocking.append("sample_target_not_resolved")
    if not metric_smoke_check_passed:
        blocking.append("metric_smoke_check_failed")
    if not threshold_is_numeric:
        blocking.append("threshold_not_numeric")
    if not allowed_fields_ok:
        blocking.append("allowed_fields_not_subset_of_observation_schema")
    if not visible_forbidden_disjoint:
        blocking.append("allowed_fields_overlap_forbidden_fields")
    return {
        "family_id": family["family_id"],
        "target_resolver": family["target_resolver"],
        "metric_function": family["metric_function"],
        "target_resolver_callable": target_callable,
        "metric_function_callable": metric_callable,
        "sample_target_resolved": sample_target_resolved,
        "sample_target": sample_target,
        "metric_smoke_check_passed": metric_smoke_check_passed,
        "metric_smoke_value": metric_smoke_value,
        "threshold": threshold,
        "threshold_is_numeric": threshold_is_numeric,
        "minimum_baseline_preflight_eligibility": eligible,
        "blocking_missing_fields": missing,
        "blocking_reasons": blocking,
        "resolver_error": resolver_error,
        "metric_error": metric_error,
    }


def build_surface_validation_results(contract: dict[str, Any]) -> dict[str, Any]:
    rows = [validate_family_surface(family) for family in contract["families"]]
    return {
        "producer_function": "build_surface_validation_results",
        "task_id": TASK_CARD_ID,
        "family_validation": rows,
        "baseline_preflight_executable_family_ids": [
            row["family_id"] for row in rows if row["minimum_baseline_preflight_eligibility"]
        ],
        "blocked_family_ids": [
            row["family_id"] for row in rows if not row["minimum_baseline_preflight_eligibility"]
        ],
        "all_family_surfaces_callable": all(
            row["target_resolver_callable"] and row["metric_function_callable"] for row in rows
        ),
        "all_thresholds_numeric": all(row["threshold_is_numeric"] for row in rows),
        "code_path_hash": code_path_hash(),
        "claim_ceiling": "callability and schema eligibility only; no candidate score or tournament execution",
    }


def build_positive_control_fixture(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": TASK_CARD_ID,
        "fixture_type": "malformed forbidden-visible-target positive controls",
        "fixtures": [
            family["positive_control_malformed_fixture"] for family in contract["families"]
        ],
        "expected_failure_reason": "forbidden_target_derived_field_visible",
    }


def run_positive_controls(contract: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for family in contract["families"]:
        fixture = family["positive_control_malformed_fixture"]
        expected = fixture["malformation"]
        observed = None
        failed = False
        try:
            resolver = _resolve_function(family["target_resolver"])
            resolver(fixture["record"])
            observed = "positive_control_unexpectedly_resolved"
        except SurfaceContractViolation as exc:
            observed = exc.reason
            failed = exc.reason == expected
        except Exception as exc:
            observed = str(exc)
        rows.append(
            {
                "family_id": family["family_id"],
                "target_resolver": family["target_resolver"],
                "positive_control_fixture_id": f"{family['family_id']}:forbidden_visible_target",
                "injected_field": fixture["injected_field"],
                "expected_failure_reason": expected,
                "observed_failure_reason": observed,
                "failed_as_expected": failed,
            }
        )
    return {
        "producer_function": "run_positive_controls",
        "task_id": TASK_CARD_ID,
        "controls": rows,
        "all_failed_as_expected": all(row["failed_as_expected"] for row in rows),
        "claim_ceiling": "malformed-fixture validation only; no baseline or candidate execution",
    }


def build_forbidden_action_guard() -> dict[str, Any]:
    return {
        "producer_function": "build_forbidden_action_guard",
        "task_id": TASK_CARD_ID,
        "candidate_code_created": False,
        "candidate_score_produced": False,
        "tournament_execution_attempted": False,
        "gate4_replacement_design_created": False,
        "gate4_repair_or_rerun_attempted": False,
        "runtime_or_mainline_path_created": False,
        "llm_rag_ui_companion_path_created": False,
        "auto_remote_anchor_performed": False,
        "guard_basis": "This package defines target resolvers, a metric function, contract validation, artifacts, and a report only.",
        "claim_ceiling": CLAIM_CEILING,
    }


def build_baseline_preflight_rerun_authorization(
    surface_validation: dict[str, Any],
    positive_controls: dict[str, Any],
    forbidden_guard: dict[str, Any],
) -> dict[str, Any]:
    all_executable = len(surface_validation["baseline_preflight_executable_family_ids"]) == 6
    authorized = (
        all_executable
        and positive_controls["all_failed_as_expected"]
        and not forbidden_guard["candidate_code_created"]
        and not forbidden_guard["tournament_execution_attempted"]
    )
    return {
        "producer_function": "build_baseline_preflight_rerun_authorization",
        "task_id": TASK_CARD_ID,
        "rerun_authorized": authorized,
        "authorized_scope": "separate no-candidate baseline-preflight rerun only",
        "requires_separate_execution_task": True,
        "candidate_code_authorized": False,
        "candidate_score_authorized": False,
        "tournament_execution_authorized": False,
        "gate4_replacement_authorized": False,
        "runtime_or_mainline_authorized": False,
        "auto_remote_anchor_authorized": False,
        "rationale": (
            "All six family target surfaces are callable, thresholds are numeric, "
            "and malformed positive controls fail. This permits a future separate "
            "baseline-preflight rerun over this contract, not candidate or tournament execution."
        )
        if authorized
        else "One or more contract eligibility checks failed; rerun is not authorized.",
        "claim_ceiling": CLAIM_CEILING,
    }


def compute_result(
    *,
    source_pin: dict[str, Any],
    surface_validation: dict[str, Any],
    positive_controls: dict[str, Any],
    forbidden_guard: dict[str, Any],
    rerun_authorization: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    stop_conditions = []
    if source_pin["branch"] != BRANCH:
        stop_conditions.append("branch_mismatch")
    if not source_pin["source_pin_boundary_ok"]:
        stop_conditions.append("inherited_head_anchor_not_current_or_ancestor")
    if len(surface_validation["baseline_preflight_executable_family_ids"]) != 6:
        stop_conditions.append("not_all_families_baseline_preflight_executable")
    if not positive_controls["all_failed_as_expected"]:
        stop_conditions.append("positive_control_failure")
    for key in [
        "candidate_code_created",
        "candidate_score_produced",
        "tournament_execution_attempted",
        "gate4_replacement_design_created",
        "runtime_or_mainline_path_created",
        "llm_rag_ui_companion_path_created",
    ]:
        if forbidden_guard[key]:
            stop_conditions.append(key)
    verdict = (
        "mechanism_family_tournament_executable_surface_contract_001a_pass"
        if not stop_conditions
        else "mechanism_family_tournament_executable_surface_contract_001a_blocked"
    )
    return {
        "producer_function": "compute_result",
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "verdict": verdict,
        "current_layer": "engineering-governance / executable tournament-surface contract repair only",
        "mainline_integration_status": "not integrated",
        "enabled_status": "no runtime, no Gate4 replacement, no candidate, no tournament execution, no trigger path",
        "real_trigger_evidence": "Inherited baseline preflight placed all six families in needs_redesign because thresholds and callable target surfaces were missing.",
        "claim_ceiling": CLAIM_CEILING,
        "baseline_preflight_executable_family_count": len(
            surface_validation["baseline_preflight_executable_family_ids"]
        ),
        "baseline_preflight_executable_family_ids": surface_validation[
            "baseline_preflight_executable_family_ids"
        ],
        "blocked_family_ids": surface_validation["blocked_family_ids"],
        "positive_controls_failed_as_expected": positive_controls["all_failed_as_expected"],
        "baseline_preflight_rerun_authorized": rerun_authorization["rerun_authorized"],
        "candidate_code_created": forbidden_guard["candidate_code_created"],
        "candidate_score_produced": forbidden_guard["candidate_score_produced"],
        "tournament_execution_attempted": forbidden_guard["tournament_execution_attempted"],
        "gate4_replacement_design_created": forbidden_guard["gate4_replacement_design_created"],
        "runtime_or_mainline_path_created": forbidden_guard["runtime_or_mainline_path_created"],
        "stop_conditions_triggered": sorted(set(stop_conditions)),
        "remote_anchor_policy": AUTO_REMOTE_ANCHOR,
        "remote_anchor_performed": False,
        "next_minimal_closed_loop_action": (
            "Run a separately scoped no-candidate baseline-preflight rerun that consumes this "
            "surface contract, or block if a reviewer rejects the repaired surfaces."
        ),
        "what_this_does_not_prove": [
            "candidate model behavior",
            "candidate score",
            "tournament execution",
            "Gate4 replacement validity",
            "mechanism validity",
            "social understanding",
            "agency",
            "subjectivity",
            "consciousness",
            "emotion",
            "autonomy",
            "runtime readiness",
            "bridge/admission readiness",
            "companion readiness",
            "EGO readiness",
        ],
    }


def _resolve_output_dir(output_dir: str | Path | None) -> Path:
    if output_dir is None:
        return repo_root() / "artifacts" / ARTIFACT_DIR_NAME
    path = Path(output_dir)
    return path if path.is_absolute() else repo_root() / path


def execute_contract_validation(
    output_dir: str | Path | None = None,
    *,
    persist_artifacts: bool = True,
) -> dict[str, Any]:
    out = _resolve_output_dir(output_dir)
    run_id = f"{TASK_ID}_{_now().replace('-', '').replace(':', '').replace('Z', 'Z')}"
    source_pin = build_source_pin_readback()
    contract = build_family_surface_contract()
    surface_validation = build_surface_validation_results(contract)
    malformed_fixture = build_positive_control_fixture(contract)
    positive_controls = run_positive_controls(contract)
    forbidden_guard = build_forbidden_action_guard()
    rerun_authorization = build_baseline_preflight_rerun_authorization(
        surface_validation=surface_validation,
        positive_controls=positive_controls,
        forbidden_guard=forbidden_guard,
    )
    result = compute_result(
        source_pin=source_pin,
        surface_validation=surface_validation,
        positive_controls=positive_controls,
        forbidden_guard=forbidden_guard,
        rerun_authorization=rerun_authorization,
        run_id=run_id,
    )
    run = {
        "task_id": TASK_CARD_ID,
        "run_id": run_id,
        "result": result,
        "source_pin_readback": source_pin,
        "family_surface_contract": contract,
        "surface_validation_results": surface_validation,
        "positive_control_malformed_fixture": malformed_fixture,
        "positive_control_results": positive_controls,
        "forbidden_action_guard": forbidden_guard,
        "baseline_preflight_rerun_authorization": rerun_authorization,
    }
    if persist_artifacts:
        write_artifacts(out, run)
    return run


def write_artifacts(out: Path, run: dict[str, Any]) -> None:
    artifact_map = {
        "result.json": run["result"],
        "source_pin_readback.json": run["source_pin_readback"],
        "family_surface_contract.json": run["family_surface_contract"],
        "surface_validation_results.json": run["surface_validation_results"],
        "positive_control_malformed_fixture.json": run["positive_control_malformed_fixture"],
        "positive_control_results.json": run["positive_control_results"],
        "forbidden_action_guard.json": run["forbidden_action_guard"],
        "baseline_preflight_rerun_authorization.json": run["baseline_preflight_rerun_authorization"],
    }
    for name, payload in artifact_map.items():
        _write_json(out / name, payload)


def write_research_report(run: dict[str, Any], report_path: str | Path | None = None) -> Path:
    path = Path(report_path) if report_path is not None else repo_root() / "docs" / "research" / REPORT_NAME
    if not path.is_absolute():
        path = repo_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    result = run["result"]
    source = run["source_pin_readback"]
    authorization = run["baseline_preflight_rerun_authorization"]
    lines = [
        "# MECHANISM-FAMILY-TOURNAMENT-EXECUTABLE-SURFACE-CONTRACT-001A",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        "Layer: engineering-governance / executable tournament-surface contract repair only.",
        "",
        "Mainline integration status: not integrated.",
        "",
        "Enabled status: no runtime, no Gate4 replacement, no candidate, no tournament execution, no trigger path.",
        "",
        f"Claim ceiling: {CLAIM_CEILING}",
        "",
        "Auto-Remote-Anchor: forbidden.",
        "",
        "## Bounded Task Card",
        "",
        f"- Task id: `{TASK_CARD_ID}`",
        "- Problem definition: inherited six-family registry could not enter baseline preflight because numeric thresholds and callable target surfaces were missing.",
        "- Current stage/layer: engineering-governance executable-surface contract repair only.",
        "- Mainline target: none; not integrated.",
        "- Enabled-state requirement: no runtime, no candidate, no tournament, no Gate4 replacement, and no trigger path.",
        "- Real-trigger evidence requirement: cite inherited baseline-preflight `needs_redesign` outcome and validate callable surfaces here.",
        "- Hypothesis: adding explicit target resolvers, metrics, thresholds, leakage detectors, and malformed positive controls is sufficient to authorize a future no-candidate baseline-preflight rerun.",
        "- Strongest baseline: cheap lookup, retrieval, static formula, identity/profile, graph/cache, and full-bundle decoder surfaces may still close a family in the future rerun.",
        "- Ablation requirement: not executed here; inherited per-family ablation requirements remain future execution requirements.",
        "- Trace/replay requirement: target resolution and validation artifacts must record callable provenance; no replay or candidate trace is produced here.",
        "- Computed-evidence provenance gate: validation results are produced by callable `execute_contract_validation`, target resolver functions, metric function, positive-control checks, and code path hash.",
        "- Acceptance gate: all six families have required fields, numeric thresholds, callable target resolvers, callable metric function, failing positive controls, and no forbidden side effects.",
        f"- Claim ceiling: {CLAIM_CEILING}",
        "- Stop condition: any candidate code, candidate score, tournament execution, Gate4 repair/rerun, runtime/mainline path, nonnumeric threshold, missing callable target, or nonfailing positive control.",
        "- Rollback plan: remove this task's isolated src/test/doc/artifact paths if unauthorized scope appears; do not alter inherited preflight artifacts.",
        "- Expected changed files: isolated 001A source package, focused test, this research report, and artifacts under `artifacts/mechanism_family_tournament_executable_surface_contract_001a/`.",
        "- Forbidden changes: candidate model code, candidate score, tournament execution, Gate4 replacement design, Gate4 repair/rerun, bridge/admission/runtime/EGO-mainline, LLM/RAG/UI/companion path.",
        "- Auto-Remote-Anchor decision: forbidden.",
        "",
        "## Source Pin Readback",
        "",
        f"- Branch: `{source['branch']}`",
        f"- Current HEAD: `{source['current_head']}`",
        f"- Inherited HEAD / anchor: `{source['inherited_head_anchor']}`",
        f"- Current HEAD matches inherited anchor: `{source['current_head_matches_inherited_anchor']}`",
        f"- Inherited anchor is ancestor of current HEAD: `{source['inherited_head_anchor_is_ancestor_of_current_head']}`",
        f"- Source-pin boundary ok: `{source['source_pin_boundary_ok']}`",
        "",
        "## Family Surface Table",
        "",
        "| family ID | target resolver | metric | threshold | eligibility |",
        "|---|---|---|---:|---|",
    ]
    validation_by_family = {
        row["family_id"]: row for row in run["surface_validation_results"]["family_validation"]
    }
    for family in run["family_surface_contract"]["families"]:
        validation = validation_by_family[family["family_id"]]
        lines.append(
            f"| `{family['family_id']}` | `{family['target_resolver']}` | `{family['metric_function']}` | `{family['numeric_threshold']}` | `{validation['minimum_baseline_preflight_eligibility']}` |"
        )
    lines.extend(
        [
            "",
            "## Positive Controls",
            "",
        ]
    )
    for row in run["positive_control_results"]["controls"]:
        lines.append(
            f"- `{row['family_id']}` injected `{row['injected_field']}` expected `{row['expected_failure_reason']}` observed `{row['observed_failure_reason']}` failed as expected `{row['failed_as_expected']}`."
        )
    lines.extend(
        [
            "",
            "## Rerun Authorization",
            "",
            f"- Baseline preflight rerun authorized: `{authorization['rerun_authorized']}`",
            f"- Authorized scope: `{authorization['authorized_scope']}`",
            f"- Candidate code authorized: `{authorization['candidate_code_authorized']}`",
            f"- Tournament execution authorized: `{authorization['tournament_execution_authorized']}`",
            f"- Gate4 replacement authorized: `{authorization['gate4_replacement_authorized']}`",
            "",
            "A rerun is authorized only as a separate no-candidate baseline-preflight rerun that consumes this contract. This task did not run that preflight, did not produce a candidate score, and candidate code remains unauthorized.",
            "",
            "## Forbidden-Action Guard",
            "",
            f"- Candidate code created: `{run['forbidden_action_guard']['candidate_code_created']}`",
            f"- Candidate score produced: `{run['forbidden_action_guard']['candidate_score_produced']}`",
            f"- Tournament execution attempted: `{run['forbidden_action_guard']['tournament_execution_attempted']}`",
            f"- Gate4 replacement design created: `{run['forbidden_action_guard']['gate4_replacement_design_created']}`",
            f"- Runtime/mainline path created: `{run['forbidden_action_guard']['runtime_or_mainline_path_created']}`",
            f"- LLM/RAG/UI/companion path created: `{run['forbidden_action_guard']['llm_rag_ui_companion_path_created']}`",
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
            "This is no mechanism-validity evidence.",
            "",
            *[f"- {item}" for item in result["what_this_does_not_prove"]],
            "",
            "## Next Minimal Closed-Loop Action",
            "",
            result["next_minimal_closed_loop_action"],
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    run = execute_contract_validation(output_dir=args.output_dir, persist_artifacts=True)
    if args.write_report:
        write_research_report(run)
    print(json.dumps(run["result"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
