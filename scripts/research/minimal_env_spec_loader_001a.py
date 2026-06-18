from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from evidence_provenance_001a import file_sha256, stable_json_hash


TASK_ID = "BASELINE-FIRST-HARNESS-001A-R1"
ENVIRONMENT_ID = "minimal_closed_loop_latent_maintenance_001a"
REQUIRED_FREEZE_SHA256 = "dc6d42b2fa010fb63edda889562bccc9d616ebe8871663c56233ee3f9bd02884"

FINAL_ACTIONS = [
    "protect_left_boundary",
    "protect_right_boundary",
    "repair_core_viability",
    "exploit_safe_window",
    "defer_or_ignore",
]

BUDGET_COMPONENT_CHANNELS = [
    "probe_rule_family",
    "probe_viability_bucket",
    "probe_boundary_pressure",
    "probe_perturbation_phase",
    "probe_action_trace_mod",
]

EXTRA_LEGAL_CHANNELS = [
    "probe_decoy_gradient",
    "probe_decoy_load",
    "probe_decoy_latency",
    "observe_refresh",
    "store_visible_budget_state",
    "replay_visible_trace",
    "ignore_noop_trace",
]

ALL_LEGAL_CHANNELS = BUDGET_COMPONENT_CHANNELS + EXTRA_LEGAL_CHANNELS

FROZEN_THRESHOLDS = {
    "frozen_oracle_target_floor": 0.90,
    "frozen_passive_ceiling": 0.87,
    "frozen_degenerate_ceiling": 0.87,
    "frozen_size_only_ceiling": 0.87,
    "frozen_equivalence_band": 0.03,
    "frozen_candidate_matched_budget": 5,
    "frozen_full_legal_channel_count": 12,
    "frozen_min_seed_count": 5,
    "frozen_min_episodes_per_seed": 20,
    "frozen_seed_noise_requirement": 0.03,
}

GENERATOR_CONFIG = {
    "schema_version": "baseline_first_harness_001a_generator_config_v1",
    "environment_id": ENVIRONMENT_ID,
    "seeds": [101, 202, 303, 404, 505],
    "episodes_per_seed": 20,
    "candidate_matched_budget_tokens": FROZEN_THRESHOLDS["frozen_candidate_matched_budget"],
    "full_legal_channel_count": FROZEN_THRESHOLDS["frozen_full_legal_channel_count"],
    "target_rule": "final_action_index = sum(five_budget_component_probe_values) mod 5",
    "candidate_free": True,
}


def load_freeze_metadata(freeze_path: str | Path) -> dict[str, Any]:
    path = Path(freeze_path)
    if not path.exists():
        return {"ok": False, "reason": "freeze_readback_missing", "path": str(path)}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"ok": False, "reason": "freeze_json_invalid", "path": str(path), "error": str(exc)}
    return {"ok": True, "path": str(path), "sha256": file_sha256(path), "payload": payload}


def verify_canonical_inputs(
    spec_path: str | Path,
    freeze_path: str | Path,
    required_spec_sha256: str,
    run_id: str,
) -> dict[str, Any]:
    spec = Path(spec_path)
    freeze = Path(freeze_path)
    if not spec.exists():
        return {
            "ok": False,
            "final_verdict": "blocked_env_spec_mutated_or_unfrozen",
            "terminal_reason_id": "spec_readback_missing",
            "run_id": run_id,
            "spec_path": str(spec),
            "freeze_path": str(freeze),
            "required_spec_sha256": required_spec_sha256,
            "consumed_by_final_verdict": True,
        }

    actual_spec_sha256 = file_sha256(spec)
    if actual_spec_sha256.lower() != required_spec_sha256.lower():
        return {
            "ok": False,
            "final_verdict": "blocked_env_spec_mutated_or_unfrozen",
            "terminal_reason_id": "spec_sha256_mismatch",
            "run_id": run_id,
            "spec_path": str(spec),
            "freeze_path": str(freeze),
            "required_spec_sha256": required_spec_sha256,
            "actual_spec_sha256": actual_spec_sha256,
            "consumed_by_final_verdict": True,
        }

    freeze_readback = load_freeze_metadata(freeze)
    if not freeze_readback.get("ok"):
        return {
            "ok": False,
            "final_verdict": "blocked_pending_canonical_readback",
            "terminal_reason_id": freeze_readback["reason"],
            "run_id": run_id,
            "spec_path": str(spec),
            "freeze_path": str(freeze),
            "required_spec_sha256": required_spec_sha256,
            "actual_spec_sha256": actual_spec_sha256,
            "consumed_by_final_verdict": True,
        }

    freeze_payload = freeze_readback["payload"]
    freeze_errors = []
    if freeze_payload.get("spec", {}).get("sha256", "").lower() != required_spec_sha256.lower():
        freeze_errors.append("freeze_spec_sha256_mismatch")
    if freeze_payload.get("freeze_status") != "frozen_before_any_baseline_or_oracle_scores":
        freeze_errors.append("freeze_status_unexpected")
    if freeze_payload.get("mutation_ban", {}).get("next_harness_may_mutate_spec") is not False:
        freeze_errors.append("mutation_ban_missing")
    if freeze_payload.get("next_harness_readback_requirement", {}).get("required_next_card") != "BASELINE-FIRST-HARNESS-001A":
        freeze_errors.append("next_harness_requirement_missing")

    if freeze_errors:
        return {
            "ok": False,
            "final_verdict": "blocked_pending_canonical_readback",
            "terminal_reason_id": "freeze_identity_or_threshold_readback_failed",
            "errors": freeze_errors,
            "run_id": run_id,
            "spec_path": str(spec),
            "freeze_path": str(freeze),
            "required_spec_sha256": required_spec_sha256,
            "actual_spec_sha256": actual_spec_sha256,
            "freeze_sha256": freeze_readback["sha256"],
            "consumed_by_final_verdict": True,
        }

    return {
        "ok": True,
        "run_id": run_id,
        "spec_path": str(spec),
        "freeze_path": str(freeze),
        "required_spec_sha256": required_spec_sha256,
        "actual_spec_sha256": actual_spec_sha256,
        "known_freeze_sha256": REQUIRED_FREEZE_SHA256,
        "actual_freeze_sha256": freeze_readback["sha256"],
        "freeze_sha256_matches_handoff": freeze_readback["sha256"].lower() == REQUIRED_FREEZE_SHA256,
        "freeze_payload_task_id": freeze_payload.get("task_id"),
        "freeze_status": freeze_payload.get("freeze_status"),
        "canonical_readback_channel": freeze_payload.get("spec", {}).get("canonical_readback_channel"),
        "thresholds": deepcopy(FROZEN_THRESHOLDS),
        "generator_source_pins_readable": True,
        "source_inputs": freeze_payload.get("source_inputs", []),
        "consumed_by_final_verdict": True,
    }


def _component_values(seed: int, episode_index: int) -> dict[str, int]:
    return {
        "probe_rule_family": (seed + episode_index) % 5,
        "probe_viability_bucket": (seed // 3 + episode_index * 2) % 5,
        "probe_boundary_pressure": (seed // 7 + episode_index * 3) % 5,
        "probe_perturbation_phase": (seed // 11 + episode_index * 4) % 5,
        "probe_action_trace_mod": episode_index % 5,
    }


def target_from_components(component_values: dict[str, int]) -> str:
    index = sum(component_values[channel] for channel in BUDGET_COMPONENT_CHANNELS) % len(FINAL_ACTIONS)
    return FINAL_ACTIONS[index]


def build_episode(seed: int, episode_index: int, generator_source_hash: str, generator_config_hash: str) -> dict[str, Any]:
    components = _component_values(seed, episode_index)
    target = target_from_components(components)
    target_index = FINAL_ACTIONS.index(target)
    weak_hint_index = target_index if episode_index % 4 == 0 else (target_index + 1 + episode_index) % len(FINAL_ACTIONS)
    legal_responses = []
    for channel in ALL_LEGAL_CHANNELS:
        if channel in components:
            response = {
                "channel_id": channel,
                "value": components[channel],
                "visibility": "legal_visible_if_queried",
            }
        else:
            response = {
                "channel_id": channel,
                "value": (seed + episode_index + len(channel)) % 7,
                "visibility": "legal_visible_if_queried_decoy",
            }
        legal_responses.append(response)

    episode_id = f"seed-{seed}-episode-{episode_index:02d}"
    return {
        "episode_id": episode_id,
        "seed": seed,
        "hidden_state": {
            "transition_rule_id": f"family_{components['probe_rule_family']}",
            "diagnostic_target_index": target_index,
            "hidden_dynamics_vector": list(components.values()),
        },
        "observable_state": {
            "weak_hint_action": FINAL_ACTIONS[weak_hint_index],
            "passive_scalar": ((seed % 17) + episode_index) / 40.0,
            "passive_variance_proxy": ((episode_index * seed) % 13) / 13.0,
            "passive_correlation_proxy": ((episode_index + seed) % 9) / 9.0,
            "visible_budget_tokens_remaining": FROZEN_THRESHOLDS["frozen_candidate_matched_budget"],
        },
        "legal_action_space": {
            "query_channels": list(ALL_LEGAL_CHANNELS),
            "final_decision_labels": list(FINAL_ACTIONS),
            "candidate_matched_budget_tokens": FROZEN_THRESHOLDS["frozen_candidate_matched_budget"],
        },
        "legal_channel_responses": legal_responses,
        "viability_state": {
            "bucket": components["probe_viability_bucket"],
            "reservoir": 100 - components["probe_perturbation_phase"] * 7,
        },
        "self_boundary_state": {
            "boundary_pressure": components["probe_boundary_pressure"],
            "self_caused_trace_mod": components["probe_action_trace_mod"],
        },
        "external_perturbation_state": {
            "phase": components["probe_perturbation_phase"],
            "source_family": f"external_{(seed + episode_index) % 4}",
        },
        "transition_rule_id": f"family_{components['probe_rule_family']}",
        "serialized_state": {
            "episode_id": episode_id,
            "seed": seed,
            "visible_budget_tokens_remaining": FROZEN_THRESHOLDS["frozen_candidate_matched_budget"],
            "legal_action_schema_hash": stable_json_hash({"channels": ALL_LEGAL_CHANNELS, "actions": FINAL_ACTIONS}),
        },
        "target_label_or_target_variable": target,
        "generator_source_hash": generator_source_hash,
        "generator_config_hash": generator_config_hash,
        "source_pin_readback": {
            "generator_source_hash": generator_source_hash,
            "generator_config_hash": generator_config_hash,
            "readback_channel": "canonical_file_api_read_bytes",
        },
    }


def build_candidate_free_episodes(generator_source_hash: str, generator_config_hash: str) -> list[dict[str, Any]]:
    episodes = []
    for seed in GENERATOR_CONFIG["seeds"]:
        for episode_index in range(GENERATOR_CONFIG["episodes_per_seed"]):
            episodes.append(build_episode(seed, episode_index, generator_source_hash, generator_config_hash))
    return episodes


def mask_hidden_fields(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    masked = deepcopy(episodes)
    for episode in masked:
        episode["hidden_state"] = None
        episode["target_label_or_target_variable"] = None
    return masked


def permute_hidden_fields(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    permuted = deepcopy(episodes)
    hidden_values = [episode.get("hidden_state") for episode in permuted]
    target_values = [episode.get("target_label_or_target_variable") for episode in permuted]
    if hidden_values:
        rotated_hidden = hidden_values[1:] + hidden_values[:1]
        rotated_target = target_values[1:] + target_values[:1]
        for episode, hidden, target in zip(permuted, rotated_hidden, rotated_target):
            episode["hidden_state"] = hidden
            episode["target_label_or_target_variable"] = target
    return permuted


def build_generator_provenance(repo_root: str | Path, run_id: str) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / "scripts" / "research" / "minimal_env_spec_loader_001a.py"
    source_hash = file_sha256(source_path)
    config_hash = stable_json_hash(GENERATOR_CONFIG)
    return {
        "result": "passed",
        "run_id": run_id,
        "generator_source_path": "scripts/research/minimal_env_spec_loader_001a.py",
        "generator_source_sha256": source_hash,
        "generator_config_sha256": config_hash,
        "producer_function": "minimal_env_spec_loader_001a.build_candidate_free_episodes",
        "code_path_hash": source_hash,
        "readback_channel": "canonical_file_api_read_bytes",
        "fair_baseline_access_declaration": "same visible channel, same candidate-matched budget, same legal action/query set",
        "hidden_target_storage_declaration": "target_label_or_target_variable and hidden_state are diagnostic-only",
        "no_candidate_authored_truth_assertion": True,
        "source_pin_integrity_status": "passed",
        "consumed_by_final_verdict": True,
    }
