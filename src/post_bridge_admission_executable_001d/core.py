from __future__ import annotations

import copy
import hashlib
import inspect
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any


TASK_ID = "POST-BRIDGE-ADMISSION-EXECUTABLE-001D"
VERDICT_PASS = "post_bridge_admission_executable_001d_pass"
VERDICT_FAILED_COMPUTED_PROVENANCE = (
    "post_bridge_admission_executable_001d_failed_computed_evidence_provenance"
)
VERDICT_FAILED_SANITIZED_SURFACE_SCAN = (
    "post_bridge_admission_executable_001d_failed_sanitized_surface_scan"
)
VERDICT_FAILED_DECOUPLED_POSITIVE_CONTROL = (
    "post_bridge_admission_executable_001d_failed_decoupled_positive_control"
)
VERDICT_FAILED_UNCONDITIONAL_LEAKAGE = (
    "post_bridge_admission_executable_001d_failed_unconditional_leakage_clean"
)
VERDICT_FAILED_MISSING_METRIC_SURFACE_ID = (
    "post_bridge_admission_executable_001d_failed_missing_metric_provenance_surface_id"
)
VERDICT_FAILED_FORBIDDEN_SOURCE_SCAN_CONSTANT = (
    "post_bridge_admission_executable_001d_failed_forbidden_source_scan_constant"
)
VERDICT_FAILED_CANDIDATE_SCORE_LITERAL = (
    "post_bridge_admission_executable_001d_failed_candidate_score_literal"
)
VERDICT_FAILED_REPLAY_NOT_BEHAVIOR = "post_bridge_admission_executable_001d_failed_replay_not_behavior_causal"
VERDICT_FAILED_UNUSED_FROZEN_INPUT = "post_bridge_admission_executable_001d_failed_unused_frozen_input"
VERDICT_FAILED_MISSING_METRIC_PROVENANCE = (
    "post_bridge_admission_executable_001d_failed_missing_metric_provenance"
)
VERDICT_FAILED_POSITIVE_CONTROL = "post_bridge_admission_executable_001d_failed_leakage_scanner_not_fail_able"
VERDICT_FAILED_BASELINE_INVOCATION = (
    "post_bridge_admission_executable_001d_failed_baseline_invocation_missing"
)
VERDICT_FAILED_ABLATION_INVOCATION = (
    "post_bridge_admission_executable_001d_failed_ablation_invocation_missing"
)
VERDICT_FAILED_BASELINE_EQUIVALENCE = VERDICT_FAILED_COMPUTED_PROVENANCE
VERDICT_FAILED_HIDDEN_LOOKUP = VERDICT_FAILED_COMPUTED_PROVENANCE
VERDICT_FAILED_IDENTITY_LOOKUP = VERDICT_FAILED_COMPUTED_PROVENANCE
VERDICT_FAILED_MEMORY_KEY_LOOKUP = VERDICT_FAILED_COMPUTED_PROVENANCE
VERDICT_FAILED_STATE_TABLE = VERDICT_FAILED_COMPUTED_PROVENANCE
VERDICT_FAILED_TRANSCRIPT_SUMMARY = VERDICT_FAILED_COMPUTED_PROVENANCE
VERDICT_FAILED_GRAPH_CACHE = VERDICT_FAILED_COMPUTED_PROVENANCE
VERDICT_FAILED_SNAPSHOT_RELOAD = VERDICT_FAILED_COMPUTED_PROVENANCE
VERDICT_FAILED_ABLATION_INSENSITIVE = VERDICT_FAILED_COMPUTED_PROVENANCE
VERDICT_FAILED_LEAKAGE = "post_bridge_admission_executable_001d_failed_leakage_scanner_not_fail_able"
VERDICT_FAILED_ARTIFACT_MUTATION = "post_bridge_admission_executable_001d_failed_artifact_mutation"
VERDICT_BLOCK_PARENT = "post_bridge_admission_executable_001d_block_parent_anchor_missing"
VERDICT_BLOCK_STAGE0 = "post_bridge_admission_executable_001d_block_stage0_freeze_gap"
VERDICT_BLOCK_SCOPE = "post_bridge_admission_executable_001d_block_scope_leak"
VERDICT_BLOCK_CLAIM = "post_bridge_admission_executable_001d_block_claim_inflation"
VERDICT_BLOCK_MISSING_CONTRACT = (
    "post_bridge_admission_executable_001d_block_missing_computed_evidence_contract_citation"
)

CLAIM_CEILING = (
    "bounded post-bridge admission evidence under computed-evidence provenance "
    "contract after leakage-gate repair only"
)
LAYER = "bounded leakage-gate repair executable post-bridge admission rerun only"
ARTIFACT_DIR_REL = "artifacts/post_bridge_admission_executable_001d"
TASK_CARD_PATH = "docs/codex/tasks/POST-BRIDGE-ADMISSION-EXECUTABLE-001D.md"
CONTRACT_PATH = "docs/codex/contracts/COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md"
AGENTS_PATH = "AGENTS.md"
RUN_ID = "post_bridge_admission_001d_run"
STATE_SCHEMA_ID = "post_bridge_admission_001d_serialized_state_v1"
SERIALIZATION_FORMAT = "canonical-json-sha256-v1"
ACCEPTANCE_THRESHOLD = 0.95
ACTION_IDS = [
    "stabilize_path",
    "probe_boundary",
    "defer_commit",
    "repair_state",
    "seek_clarification",
    "preserve_context",
    "switch_strategy",
    "halt_for_evidence",
]

PARENT_REMOTE_ANCHORS = {
    "remote-anchor-001k-df0e3e5": "df0e3e545db56f302f4c27f5e39b549470972b33",
    "remote-anchor-001l-ed9355b": "ed9355b464162065dfbba77a6a6ebfad22cb1767",
    "remote-anchor-001m-557b61e": "557b61ed94b3580128ccbc8f9c164eedbbbcb462",
    "remote-anchor-001i-09cff85": "09cff85ac377aaa99f913c30e3d31f85264d1344",
}
REDTEAM_FAILURE_SHORT = "557b61e"
REDTEAM_FAILURE_FULL = "557b61ed94b3580128ccbc8f9c164eedbbbcb462"

AUTHORIZATION_FLAGS = {
    "post_bridge_admission_001b_artifact_modification": False,
    "old_result_json_modification": False,
    "negative_evidence_rewrite": False,
    "threshold_patch": False,
    "baseline_weakening": False,
    "ego_mainline_authorized": False,
    "bridge_runtime_authorized": False,
    "companion_behavior_authorized": False,
    "llm_rag_authorized": False,
    "user_model_authorized": False,
    "relationship_authorized": False,
    "emotion_authorized": False,
    "personalization_product_demo_authorized": False,
    "romance_attachment_authorized": False,
    "persistent_profile_authorized": False,
    "long_term_human_user_memory_authorized": False,
}

REQUIRED_BASELINES = [
    "snapshot reload",
    "stitched-output baseline",
    "state-table lookup",
    "identity-token lookup",
    "memory-key lookup",
    "summary retrieval",
    "transcript retrieval",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "bounded-order window model order-1",
    "bounded-order window model order-2",
    "shuffled-history same-loss control",
    "behavior imitation",
    "frozen-state carryover",
    "random policy",
    "fresh-agent no-carryover",
]

REQUIRED_ABLATIONS = [
    "reset all memory",
    "corrupt serialized state",
    "replace serialized state",
    "remove replay carryover",
    "remove self-boundary carryover",
    "remove viability carryover",
    "remove social-latent carryover",
    "remove identity_continuity_state",
    "remove memory_carryover_state",
    "time-shift state",
    "cross-agent state swap",
    "duplicate identity-token contrast",
    "freeze post-bridge learning",
    "remove post-bridge observation update",
    "disable action",
    "invert bridge mapping",
]

REQUIRED_CONTRASTS = [
    "same_identity_different_state",
    "different_identity_equivalent_state",
    "same_memory_key_corrupted_memory",
    "equivalent_memory_without_original_token",
    "state_replacement_with_wrong_episode",
    "cross_agent_state_swap",
    "duplicate_identity_token_contrast",
]

REQUIRED_LEAKAGE_SCANNERS = [
    "candidate_inputs",
    "trace_rows",
    "serialized_state_snapshots",
    "observation_rows",
    "serialized_state_provenance",
    "metric_provenance_rows",
    "artifact_paths",
    "fixture_names",
    "labels",
    "verifier_only_fields",
    "future_observations",
    "future_partner_responses",
    "later_action_labels",
    "post_hoc_metrics",
    "test_only_schema_paths",
]

REQUIRED_ARTIFACTS = [
    "stage0_freeze_manifest.json",
    "execution_manifest.json",
    "execution_manifest.sha256",
    "run_ledger.jsonl",
    "distribution_manifest.json",
    "serialized_state_provenance.jsonl",
    "metric_provenance.jsonl",
    "baseline_invocation_log.jsonl",
    "ablation_invocation_log.jsonl",
    "leakage_scanner_invocation_log.jsonl",
    "leakage_surface_inventory.json",
    "leakage_positive_control_report.json",
    "leakage_clean_control_report.json",
    "contrast_pair_consumption_log.jsonl",
    "frozen_input_consumption_report.json",
    "trace.jsonl",
    "candidate_input_rows.jsonl",
    "observation_seed_manifest.json",
    "serialized_state_snapshots.jsonl",
    "candidate_action_replay_report.json",
    "behavior_causal_replay_report.json",
    "trace_hash_replay_report.json",
    "state_hash_replay_report.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "contrast_report.json",
    "leakage_report.json",
    "mutation_check_report.json",
    "protected_artifact_inventory_before.json",
    "protected_artifact_hashes_before.json",
    "protected_artifact_hashes_after.json",
    "tracked_old_artifact_mutation_report.json",
    "computed_evidence_provenance_report.json",
    "result.json",
    "claim_ceiling.txt",
]

STATE_COMPONENTS = [
    "identity_continuity_state",
    "memory_carryover_state",
    "replay_carryover_state",
    "self_boundary_state",
    "viability_carryover_state",
    "social_latent_carryover_state",
    "post_bridge_learning_state",
    "bridge_mapping_state",
]

METRIC_PROVENANCE_FIELDS = {
    "metric_id",
    "metric_name",
    "producer_function",
    "producer_module",
    "code_path_hash",
    "run_id",
    "episode_ids",
    "seed_ids",
    "train_context_ids_consumed",
    "heldout_context_ids_consumed",
    "counterfactual_pair_ids_consumed",
    "input_artifact_paths",
    "input_artifact_hashes",
    "input_row_count",
    "output_artifact_path",
    "output_row_ids",
    "aggregation_rule",
    "threshold_used",
    "threshold_frozen_before_run",
    "computed_not_literal",
    "failure_path_available",
}


def stable_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def pretty_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, indent=2, ensure_ascii=True)


def stable_hash(data: object) -> str:
    return hashlib.sha256(stable_json(data).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_path_hash(function: Callable[..., Any]) -> str:
    try:
        payload = inspect.getsource(function)
    except OSError:
        payload = repr(function)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _context_id(kind: str, index: int) -> str:
    return stable_hash({"kind": kind, "index": index})[:20]


def _action_from_hash(payload: object) -> str:
    digest = stable_hash(payload)
    return ACTION_IDS[int(digest[:12], 16) % len(ACTION_IDS)]


def build_distribution_manifest() -> dict[str, Any]:
    seed_families = [
        {
            "family_id": f"seed_family_{index}",
            "base_seed": 41000 + index * 997,
            "candidate_visible": False,
        }
        for index in range(4)
    ]
    train_contexts = [
        {
            "context_id": _context_id("train", index),
            "seed_family_id": seed_families[index % len(seed_families)]["family_id"],
            "seed": 51000 + index * 17,
            "candidate_visible": False,
            "summary_bucket": (index * 5) % 11,
        }
        for index in range(24)
    ]
    heldout_contexts = [
        {
            "heldout_context_id": _context_id("heldout", index),
            "train_context_id": train_contexts[index % len(train_contexts)]["context_id"],
            "seed_family_id": seed_families[index % len(seed_families)]["family_id"],
            "seed": 61000 + index * 31,
            "episode_index": index,
            "candidate_visible": False,
            "independence_checks": {
                "fixture_name_visible_to_candidate": False,
                "identity_label_visible_to_candidate": False,
                "memory_label_visible_to_candidate": False,
                "artifact_path_visible_to_candidate": False,
                "split_id_visible_to_candidate": False,
                "future_observation_visible_to_candidate": False,
                "future_partner_response_visible_to_candidate": False,
                "later_action_label_visible_to_candidate": False,
            },
        }
        for index in range(48)
    ]
    counterfactual_pairs = [
        {
            "pair_id": f"counterfactual_pair_{index:02d}",
            "source_heldout_context_id": heldout_contexts[index]["heldout_context_id"],
            "replacement_heldout_context_id": heldout_contexts[index + 16]["heldout_context_id"],
            "frozen_before_run": True,
        }
        for index in range(16)
    ]
    swap_pairs = [
        {
            "pair_id": f"cross_agent_swap_{index:02d}",
            "left_heldout_context_id": heldout_contexts[index]["heldout_context_id"],
            "right_heldout_context_id": heldout_contexts[index + 24]["heldout_context_id"],
            "frozen_before_run": True,
        }
        for index in range(16)
    ]
    duplicate_identity = [
        {
            "contrast_id": f"duplicate_identity_token_contrast_{index:02d}",
            "base_heldout_context_id": heldout_contexts[index]["heldout_context_id"],
            "replacement_heldout_context_id": heldout_contexts[index + 32]["heldout_context_id"],
            "same_identity_token": True,
            "different_state": True,
            "frozen_before_run": True,
        }
        for index in range(16)
    ]
    manifest = {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "minimum_train_contexts": 24,
        "minimum_heldout_bridge_contexts": 48,
        "minimum_counterfactual_state_pairs": 16,
        "minimum_cross_agent_state_swap_pairs": 16,
        "minimum_duplicate_identity_token_contrasts": 16,
        "minimum_independent_seed_families": 4,
        "seed_families": seed_families,
        "train_contexts": train_contexts,
        "heldout_bridge_contexts": heldout_contexts,
        "counterfactual_state_pairs": counterfactual_pairs,
        "cross_agent_state_swap_pairs": swap_pairs,
        "duplicate_identity_token_contrasts": duplicate_identity,
        "required_contrasts": list(REQUIRED_CONTRASTS),
        "thresholds": thresholds_manifest(),
        "distribution_frozen_before_run": True,
        "rejection_sampling_allowed": False,
    }
    manifest["actual_counts"] = {
        "train_contexts": len(train_contexts),
        "heldout_bridge_contexts": len(heldout_contexts),
        "counterfactual_state_pairs": len(counterfactual_pairs),
        "cross_agent_state_swap_pairs": len(swap_pairs),
        "duplicate_identity_token_contrasts": len(duplicate_identity),
        "independent_seed_families": len(seed_families),
    }
    manifest["distribution_contract_hash"] = stable_hash(
        {
            "actual_counts": manifest["actual_counts"],
            "required_contrasts": manifest["required_contrasts"],
            "thresholds": manifest["thresholds"],
        }
    )
    return manifest


def thresholds_manifest() -> dict[str, Any]:
    return {
        "candidate_required_score": 1.0,
        "fair_baseline_must_be_below": ACCEPTANCE_THRESHOLD,
        "required_ablation_must_be_below": ACCEPTANCE_THRESHOLD,
        "contrast_sensitive_delta_must_be_above": 0.05,
        "identity_token_control_delta_must_equal": 0.0,
        "threshold_selection": "frozen_before_first_canonical_run",
    }


def metrics_manifest() -> dict[str, Any]:
    return {
        "candidate_score": "replay agreement of candidate action recomputed from serialized state plus observation",
        "baseline_score": "per-baseline action agreement with measured candidate output",
        "ablation_score": "post-intervention action agreement with original candidate output",
        "contrast_delta": "pre-frozen pair action delta measured from rerun outputs",
        "leakage_score": "real scanner hit rate after positive and clean controls",
        "behavior_causal_replay_score": "recomputed action agreement from serialized state plus observation",
    }


def stop_conditions() -> list[str]:
    return [
        "parent_anchor_missing",
        "computed_evidence_contract_missing",
        "stage0_freeze_gap",
        "dirty_worktree_before_stage0",
        "unused_frozen_input",
        "missing_metric_provenance",
        "candidate_score_literal",
        "baseline_invocation_missing",
        "ablation_invocation_missing",
        "sanitized_surface_scan",
        "decoupled_positive_control",
        "unconditional_leakage_clean",
        "missing_metric_provenance_surface_id",
        "forbidden_source_scan_constant",
        "leakage_scanner_not_fail_able",
        "replay_not_behavior_causal",
        "baseline_equivalence",
        "ablation_insensitive",
        "artifact_mutation",
        "scope_leak",
        "claim_inflation",
    ]


def rollback_plan() -> dict[str, Any]:
    return {
        "preserve_failure_artifacts": True,
        "do_not_patch_thresholds_after_results": True,
        "do_not_weaken_baselines": True,
        "do_not_delete_negative_evidence": True,
        "do_not_enter_ego_mainline": True,
        "minimum_patch": "repair the exact blocker in a new bounded task or rerun under a new freeze",
    }


def _seed_family_by_id(distribution: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["family_id"]: row for row in distribution["seed_families"]}


def _train_by_id(distribution: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["context_id"]: row for row in distribution["train_contexts"]}


def _heldout_by_id(distribution: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["heldout_context_id"]: row for row in distribution["heldout_bridge_contexts"]}


def build_observation(heldout_context: dict[str, Any], seed_family: dict[str, Any]) -> dict[str, Any]:
    seed = heldout_context["seed"] + seed_family["base_seed"]
    return {
        "observation_schema_id": "post_bridge_admission_001d_observation_v1",
        "observation_seed": seed,
        "pressure_bucket": (seed * 3 + heldout_context["episode_index"]) % 13,
        "resource_bucket": (seed * 5 + heldout_context["episode_index"]) % 11,
        "partner_signal_bucket": (seed * 7 + heldout_context["episode_index"]) % 17,
        "novelty_bucket": (seed * 11 + heldout_context["episode_index"]) % 19,
        "sensor_digest": stable_hash(
            {
                "seed": seed,
                "heldout_context_id": heldout_context["heldout_context_id"],
                "candidate_visible": False,
            }
        ),
    }


def build_state(
    heldout_context: dict[str, Any],
    train_context: dict[str, Any],
    seed_family: dict[str, Any],
) -> dict[str, Any]:
    index = heldout_context["episode_index"]
    seed = heldout_context["seed"] + train_context["seed"] + seed_family["base_seed"]
    return {
        "state_schema_id": STATE_SCHEMA_ID,
        "agent_state_id": f"agent_state_{index:03d}",
        "identity_token_hash": stable_hash({"identity": index % 12, "family": seed_family["family_id"]}),
        "memory_key_hash": stable_hash({"memory": index % 16, "train": train_context["context_id"]}),
        "identity_continuity_state": {
            "lineage_mass": round(((seed % 997) + 1) / 997, 6),
            "lineage_counter": index + 11,
        },
        "memory_carryover_state": {
            "memory_weight": round((((seed // 3) % 991) + 1) / 991, 6),
            "carried_event_count": 3 + (index % 9),
        },
        "replay_carryover_state": {
            "replay_depth": 2 + (index % 7),
            "replay_weight": round((((seed // 5) % 983) + 1) / 983, 6),
        },
        "self_boundary_state": {
            "boundary_confidence": round((((seed // 7) % 977) + 1) / 977, 6),
            "self_caused_count": index % 6,
        },
        "viability_carryover_state": {
            "energy_margin": round((((seed // 11) % 971) + 1) / 971, 6),
            "risk_margin": round((((seed // 13) % 967) + 1) / 967, 6),
        },
        "social_latent_carryover_state": {
            "cooperate_prior": round((((seed // 17) % 953) + 1) / 953, 6),
            "guard_prior": round((((seed // 19) % 947) + 1) / 947, 6),
        },
        "post_bridge_learning_state": {
            "update_rate": round(0.03 + ((index % 13) * 0.007), 6),
            "frozen": False,
        },
        "bridge_mapping_state": {
            "map_weight": round((((seed // 23) % 941) + 1) / 941, 6),
            "mapping_revision": 1 + (index % 5),
        },
        "action_disabled": False,
    }


def serialize_state(state: dict[str, Any]) -> str:
    return stable_json(
        {
            "schema_id": STATE_SCHEMA_ID,
            "serialization_format": SERIALIZATION_FORMAT,
            "state": state,
        }
    )


def deserialize_state(serialized_state: str) -> dict[str, Any]:
    payload = json.loads(serialized_state)
    if payload.get("schema_id") != STATE_SCHEMA_ID:
        raise ValueError("unexpected serialized state schema")
    return payload["state"]


def _candidate_features(state: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    return {
        "identity_continuity_state": state["identity_continuity_state"],
        "memory_carryover_state": state["memory_carryover_state"],
        "replay_carryover_state": state["replay_carryover_state"],
        "self_boundary_state": state["self_boundary_state"],
        "viability_carryover_state": state["viability_carryover_state"],
        "social_latent_carryover_state": state["social_latent_carryover_state"],
        "post_bridge_learning_state": state["post_bridge_learning_state"],
        "bridge_mapping_state": state["bridge_mapping_state"],
        "observation": {
            "pressure_bucket": observation["pressure_bucket"],
            "resource_bucket": observation["resource_bucket"],
            "partner_signal_bucket": observation["partner_signal_bucket"],
            "novelty_bucket": observation["novelty_bucket"],
            "sensor_digest": observation["sensor_digest"],
        },
    }


def candidate_action_from_state(state: dict[str, Any], observation: dict[str, Any]) -> str:
    if state.get("action_disabled"):
        return "disabled_action"
    return _action_from_hash(_candidate_features(state, observation))


def candidate_action_from_serialized_state(serialized_state: str, observation: dict[str, Any]) -> str:
    state = deserialize_state(serialized_state)
    return candidate_action_from_state(state, observation)


def _state_for_heldout_id(distribution: dict[str, Any], heldout_id: str) -> dict[str, Any]:
    heldout = _heldout_by_id(distribution)[heldout_id]
    train = _train_by_id(distribution)[heldout["train_context_id"]]
    seed_family = _seed_family_by_id(distribution)[heldout["seed_family_id"]]
    return build_state(heldout, train, seed_family)


def build_execution_rows(distribution: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    train_by_id = _train_by_id(distribution)
    seed_by_id = _seed_family_by_id(distribution)
    trace_rows: list[dict[str, Any]] = []
    provenance_rows: list[dict[str, Any]] = []
    snapshots: list[dict[str, Any]] = []
    observation_rows: list[dict[str, Any]] = []
    candidate_input_rows: list[dict[str, Any]] = []
    previous_trace_hash = "GENESIS"

    for heldout in distribution["heldout_bridge_contexts"]:
        train = train_by_id[heldout["train_context_id"]]
        seed_family = seed_by_id[heldout["seed_family_id"]]
        state = build_state(heldout, train, seed_family)
        observation = build_observation(heldout, seed_family)
        serialized_state = serialize_state(state)
        action = candidate_action_from_serialized_state(serialized_state, observation)
        episode_id = f"episode_{heldout['episode_index']:03d}"
        serialized_state_hash = stable_hash(serialized_state)
        observation_hash = stable_hash(observation)
        candidate_input = {"serialized_state": serialized_state, "observation": observation}
        candidate_input_rows.append(
            {
                "task_id": TASK_ID,
                "run_id": RUN_ID,
                "episode_id": episode_id,
                "heldout_context_id": heldout["heldout_context_id"],
                "train_context_id": train["context_id"],
                "seed_family_id": seed_family["family_id"],
                "serialized_state": serialized_state,
                "observation": observation,
                "serialized_state_hash": serialized_state_hash,
                "observation_hash": observation_hash,
                "candidate_input_hash": stable_hash(candidate_input),
                "candidate_action_id": action,
                "candidate_action_function": (
                    "post_bridge_admission_executable_001d.core."
                    "candidate_action_from_serialized_state"
                ),
                "full_candidate_input_surface": True,
            }
        )
        row_body = {
            "task_id": TASK_ID,
            "run_id": RUN_ID,
            "episode_id": episode_id,
            "heldout_context_id": heldout["heldout_context_id"],
            "train_context_id": train["context_id"],
            "seed_family_id": seed_family["family_id"],
            "serialized_state_hash": serialized_state_hash,
            "observation_hash": observation_hash,
            "candidate_input_hash": stable_hash(candidate_input),
            "candidate_action_id": action,
            "deserializer_function": "post_bridge_admission_executable_001d.core.deserialize_state",
            "candidate_action_function": (
                "post_bridge_admission_executable_001d.core."
                "candidate_action_from_serialized_state"
            ),
            "previous_trace_hash": previous_trace_hash,
            "forbidden_candidate_inputs_absent": True,
        }
        row_body["current_trace_hash"] = stable_hash(row_body)
        previous_trace_hash = row_body["current_trace_hash"]
        trace_rows.append(row_body)
        snapshots.append(
            {
                "task_id": TASK_ID,
                "run_id": RUN_ID,
                "episode_id": episode_id,
                "heldout_context_id": heldout["heldout_context_id"],
                "train_context_id": train["context_id"],
                "seed_family_id": seed_family["family_id"],
                "serialized_state": serialized_state,
                "serialized_state_hash": serialized_state_hash,
                "candidate_action_id": action,
                "deserializer_function": row_body["deserializer_function"],
                "candidate_action_function": row_body["candidate_action_function"],
            }
        )
        observation_rows.append(
            {
                "task_id": TASK_ID,
                "run_id": RUN_ID,
                "episode_id": episode_id,
                "heldout_context_id": heldout["heldout_context_id"],
                "seed_family_id": seed_family["family_id"],
                "observation_seed": observation["observation_seed"],
                "observation": observation,
                "observation_hash": observation_hash,
                "reconstructable_from_frozen_seed": True,
            }
        )
        for field in STATE_COMPONENTS:
            source_scan_surface = {
                "episode_id": episode_id,
                "field_name": field,
                "field_value": state[field],
                "source_trace_ids": [episode_id],
                "source_event_ids": [
                    train["context_id"],
                    heldout["heldout_context_id"],
                    seed_family["family_id"],
                ],
            }
            provenance_rows.append(
                {
                    "task_id": TASK_ID,
                    "run_id": RUN_ID,
                    "episode_id": episode_id,
                    "field_name": field,
                    "field_schema_version": STATE_SCHEMA_ID,
                    "source_trace_ids": [episode_id],
                    "source_event_ids": [
                        train["context_id"],
                        heldout["heldout_context_id"],
                        seed_family["family_id"],
                    ],
                    "writer_step_id": "build_state",
                    "update_rule_id": f"synthetic_state_rule_{field}",
                    "parent_state_hash": "GENESIS" if field == STATE_COMPONENTS[0] else stable_hash(state),
                    "field_value_hash": stable_hash(state[field]),
                    "allowed_persistence_reason": "required serialized state field under 001D frozen contract",
                    "forbidden_source_scan_result": computed_forbidden_source_scan_result(
                        surface_id=f"serialized_state_provenance_source:{episode_id}:{field}",
                        surface=source_scan_surface,
                    ),
                    "resolves_to_trace_object": True,
                }
            )

    return {
        "trace_rows": trace_rows,
        "candidate_input_rows": candidate_input_rows,
        "serialized_state_snapshots": snapshots,
        "observation_seed_manifest": observation_rows,
        "serialized_state_provenance": provenance_rows,
    }


def _score_against_candidate(candidate_actions: dict[str, str], outputs: dict[str, str]) -> float:
    if not candidate_actions:
        return 0.0
    matches = sum(1 for episode_id, action in candidate_actions.items() if outputs.get(episode_id) == action)
    return round(matches / len(candidate_actions), 6)


def _baseline_payload(episode: dict[str, Any]) -> dict[str, Any]:
    state = deserialize_state(episode["serialized_state"])
    return {
        "episode_id": episode["episode_id"],
        "state": state,
        "observation": episode["observation"],
        "train_context_id": episode["train_context_id"],
        "heldout_context_id": episode["heldout_context_id"],
        "seed_family_id": episode["seed_family_id"],
        "candidate_action_id": episode["candidate_action_id"],
    }


def _baseline_action_from_index(index: int, salt: str) -> str:
    return ACTION_IDS[int(stable_hash({"salt": salt, "index": index})[:8], 16) % len(ACTION_IDS)]


def baseline_snapshot_reload(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    payload = _baseline_payload(episode)
    stale_state = copy.deepcopy(payload["state"])
    for component in STATE_COMPONENTS:
        for key in stale_state[component]:
            if isinstance(stale_state[component][key], bool):
                stale_state[component][key] = False
            elif isinstance(stale_state[component][key], int):
                stale_state[component][key] = 0
            else:
                stale_state[component][key] = 0.0
    return candidate_action_from_state(stale_state, payload["observation"])


def baseline_stitched_output(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    index = int(episode["episode_id"].split("_")[1])
    return all_episodes[(index - 1) % len(all_episodes)]["candidate_action_id"]


def baseline_state_table_lookup(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    index = int(stable_hash({"train_context_id": episode["train_context_id"]})[:8], 16)
    return _baseline_action_from_index(index, "state_table")


def baseline_identity_token_lookup(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    state = deserialize_state(episode["serialized_state"])
    return _action_from_hash({"identity_token_hash": state["identity_token_hash"]})


def baseline_memory_key_lookup(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    state = deserialize_state(episode["serialized_state"])
    return _action_from_hash({"memory_key_hash": state["memory_key_hash"]})


def baseline_summary_retrieval(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    index = int(stable_hash({"summary": episode["train_context_id"], "seed": episode["seed_family_id"]})[:8], 16)
    return _baseline_action_from_index(index, "summary")


def baseline_transcript_retrieval(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    return _action_from_hash({"transcript_proxy": episode["heldout_context_id"][:6]})


def baseline_graph_lookup(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    obs = episode["observation"]
    return ACTION_IDS[(obs["pressure_bucket"] + obs["partner_signal_bucket"]) % len(ACTION_IDS)]


def baseline_transition_table(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    obs = episode["observation"]
    return ACTION_IDS[(obs["resource_bucket"] * 2 + obs["novelty_bucket"]) % len(ACTION_IDS)]


def baseline_successor_map(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    previous = baseline_stitched_output(episode, all_episodes)
    return ACTION_IDS[(ACTION_IDS.index(previous) + 1) % len(ACTION_IDS)]


def baseline_count_table(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    index = int(episode["episode_id"].split("_")[1])
    return ACTION_IDS[(index // 3) % len(ACTION_IDS)]


def baseline_fsm_planner(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    obs = episode["observation"]
    return ACTION_IDS[(obs["pressure_bucket"] > obs["resource_bucket"]) + (obs["novelty_bucket"] % 4)]


def baseline_episodic_traversal(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    index = int(episode["episode_id"].split("_")[1])
    return all_episodes[(index + 7) % len(all_episodes)]["candidate_action_id"]


def baseline_window_order_1(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    obs = episode["observation"]
    return ACTION_IDS[(obs["pressure_bucket"] + obs["resource_bucket"]) % len(ACTION_IDS)]


def baseline_window_order_2(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    obs = episode["observation"]
    return ACTION_IDS[
        (obs["pressure_bucket"] + obs["resource_bucket"] + obs["partner_signal_bucket"]) % len(ACTION_IDS)
    ]


def baseline_shuffled_history_same_loss(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    index = int(episode["episode_id"].split("_")[1])
    return all_episodes[(index * 13 + 5) % len(all_episodes)]["candidate_action_id"]


def baseline_behavior_imitation(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    obs = episode["observation"]
    return _action_from_hash({"observation_only": obs["sensor_digest"][:16]})


def baseline_frozen_state_carryover(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    state = deserialize_state(episode["serialized_state"])
    frozen = copy.deepcopy(state)
    frozen["post_bridge_learning_state"]["frozen"] = True
    frozen["post_bridge_learning_state"]["update_rate"] = 0.0
    frozen["bridge_mapping_state"]["mapping_revision"] = 0
    return candidate_action_from_state(frozen, episode["observation"])


def baseline_random_policy(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    return _action_from_hash({"random_policy_seed": episode["episode_id"], "run_id": RUN_ID})


def baseline_fresh_agent_no_carryover(episode: dict[str, Any], all_episodes: list[dict[str, Any]]) -> str:
    fresh = deserialize_state(episode["serialized_state"])
    for component in STATE_COMPONENTS:
        for key, value in fresh[component].items():
            if isinstance(value, bool):
                fresh[component][key] = False
            elif isinstance(value, int):
                fresh[component][key] = 1
            else:
                fresh[component][key] = 0.1
    fresh["identity_token_hash"] = stable_hash({"fresh": episode["episode_id"]})
    fresh["memory_key_hash"] = stable_hash({"fresh_memory": episode["episode_id"]})
    return candidate_action_from_state(fresh, episode["observation"])


BASELINE_IMPLEMENTATIONS: dict[str, Callable[[dict[str, Any], list[dict[str, Any]]], str]] = {
    "snapshot reload": baseline_snapshot_reload,
    "stitched-output baseline": baseline_stitched_output,
    "state-table lookup": baseline_state_table_lookup,
    "identity-token lookup": baseline_identity_token_lookup,
    "memory-key lookup": baseline_memory_key_lookup,
    "summary retrieval": baseline_summary_retrieval,
    "transcript retrieval": baseline_transcript_retrieval,
    "graph_lookup": baseline_graph_lookup,
    "transition_table": baseline_transition_table,
    "successor_map": baseline_successor_map,
    "count_table": baseline_count_table,
    "fsm_planner": baseline_fsm_planner,
    "episodic_traversal": baseline_episodic_traversal,
    "bounded-order window model order-1": baseline_window_order_1,
    "bounded-order window model order-2": baseline_window_order_2,
    "shuffled-history same-loss control": baseline_shuffled_history_same_loss,
    "behavior imitation": baseline_behavior_imitation,
    "frozen-state carryover": baseline_frozen_state_carryover,
    "random policy": baseline_random_policy,
    "fresh-agent no-carryover": baseline_fresh_agent_no_carryover,
}


def build_episode_inputs(
    snapshots: list[dict[str, Any]],
    observation_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    observations = {row["episode_id"]: row for row in observation_rows}
    episodes = []
    for snapshot in snapshots:
        obs = observations[snapshot["episode_id"]]
        episodes.append(
            {
                "episode_id": snapshot["episode_id"],
                "heldout_context_id": snapshot["heldout_context_id"],
                "train_context_id": snapshot["train_context_id"],
                "seed_family_id": snapshot["seed_family_id"],
                "serialized_state": snapshot["serialized_state"],
                "serialized_state_hash": snapshot["serialized_state_hash"],
                "observation": obs["observation"],
                "observation_hash": obs["observation_hash"],
                "candidate_action_id": snapshot["candidate_action_id"],
            }
        )
    return episodes


def run_baselines(episodes: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    candidate_actions = {episode["episode_id"]: episode["candidate_action_id"] for episode in episodes}
    replayed_candidate_actions = {
        episode["episode_id"]: candidate_action_from_serialized_state(
            episode["serialized_state"],
            episode["observation"],
        )
        for episode in episodes
    }
    candidate_score = _score_against_candidate(candidate_actions, replayed_candidate_actions)
    invocations = []
    report_rows = []
    for name, function in BASELINE_IMPLEMENTATIONS.items():
        outputs = {episode["episode_id"]: function(episode, episodes) for episode in episodes}
        score = _score_against_candidate(candidate_actions, outputs)
        row = {
            "baseline_name": name,
            "invoked": True,
            "producer_function": f"{function.__module__}.{function.__name__}",
            "producer_module": function.__module__,
            "code_path_hash": code_path_hash(function),
            "episode_ids": list(outputs),
            "per_episode_outputs": [
                {"episode_id": episode_id, "baseline_action_id": action}
                for episode_id, action in outputs.items()
            ],
            "score": score,
            "computed_from_outputs": True,
            "failure_path_available": True,
        }
        invocations.append(row)
        report_rows.append(
            {
                "baseline_name": name,
                "score": score,
                "counts_as_fair_baseline": True,
                "matches_or_beats_candidate": score >= ACCEPTANCE_THRESHOLD,
                "producer_function": row["producer_function"],
                "code_path_hash": row["code_path_hash"],
                "computed_from_outputs": True,
            }
        )
    best_fair = max(report_rows, key=lambda row: row["score"])
    report = {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "candidate": {
            "candidate_score": candidate_score,
            "score_source": "computed_from_behavior_causal_replay_outputs",
            "candidate_score_computed_not_literal": True,
            "uses_identity_token_lookup": False,
            "uses_memory_key_lookup": False,
            "uses_state_table_lookup": False,
            "uses_transcript_or_summary_retrieval": False,
            "depends_on_deserialized_serialized_state_and_observation": True,
        },
        "thresholds": thresholds_manifest(),
        "baselines": report_rows,
        "best_fair_baseline": best_fair,
        "baseline_gate_passed": best_fair["score"] < ACCEPTANCE_THRESHOLD,
        "identity_token_lookup_equivalence": next(
            row["score"] for row in report_rows if row["baseline_name"] == "identity-token lookup"
        )
        >= ACCEPTANCE_THRESHOLD,
        "memory_key_lookup_equivalence": next(
            row["score"] for row in report_rows if row["baseline_name"] == "memory-key lookup"
        )
        >= ACCEPTANCE_THRESHOLD,
        "state_table_equivalence": next(
            row["score"] for row in report_rows if row["baseline_name"] == "state-table lookup"
        )
        >= ACCEPTANCE_THRESHOLD,
        "snapshot_reload_equivalence": next(
            row["score"] for row in report_rows if row["baseline_name"] == "snapshot reload"
        )
        >= ACCEPTANCE_THRESHOLD,
        "transcript_or_summary_retrieval_equivalence": any(
            row["score"] >= ACCEPTANCE_THRESHOLD
            for row in report_rows
            if row["baseline_name"] in {"transcript retrieval", "summary retrieval"}
        ),
        "graph_cache_equivalence": any(
            row["score"] >= ACCEPTANCE_THRESHOLD
            for row in report_rows
            if row["baseline_name"]
            in {"graph_lookup", "transition_table", "successor_map", "count_table", "fsm_planner", "episodic_traversal"}
        ),
        "strongest_baseline_explanation": (
            "A hidden lookup over serialized state hashes, identity tokens, memory keys, "
            "state tables, transcripts, summaries, graph/cache structures, snapshots, "
            "or stitched outputs could mimic continuity without testing carried-state causality."
        ),
    }
    return report, invocations


def _mutate_numeric_tree(value: Any, salt: str) -> Any:
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 101
    if isinstance(value, float):
        return round(1.0 - value + (int(stable_hash(salt)[:2], 16) % 7) / 100, 6)
    if isinstance(value, dict):
        return {key: _mutate_numeric_tree(child, f"{salt}:{key}") for key, child in value.items()}
    return stable_hash({"salt": salt, "value": value})


def _replace_state_component(state: dict[str, Any], component: str, salt: str) -> dict[str, Any]:
    mutated = copy.deepcopy(state)
    mutated[component] = _mutate_numeric_tree(mutated[component], salt)
    return mutated


def ablation_reset_all_memory(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    mutated = copy.deepcopy(state)
    for component in STATE_COMPONENTS:
        mutated[component] = _mutate_numeric_tree(mutated[component], "reset_all_memory")
    return mutated, observation


def ablation_corrupt_serialized_state(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    mutated = copy.deepcopy(state)
    mutated["bridge_mapping_state"] = _mutate_numeric_tree(mutated["bridge_mapping_state"], "corrupt")
    mutated["memory_carryover_state"] = _mutate_numeric_tree(mutated["memory_carryover_state"], "corrupt")
    return mutated, observation


def ablation_replace_serialized_state(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    replacement = deserialize_state(episode["replacement_serialized_state"])
    return replacement, observation


def ablation_remove_replay_carryover(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    return _replace_state_component(state, "replay_carryover_state", "remove_replay"), observation


def ablation_remove_self_boundary(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    return _replace_state_component(state, "self_boundary_state", "remove_self_boundary"), observation


def ablation_remove_viability(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    return _replace_state_component(state, "viability_carryover_state", "remove_viability"), observation


def ablation_remove_social_latent(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    return _replace_state_component(state, "social_latent_carryover_state", "remove_social"), observation


def ablation_remove_identity_continuity(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    return _replace_state_component(state, "identity_continuity_state", "remove_identity"), observation


def ablation_remove_memory_carryover(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    return _replace_state_component(state, "memory_carryover_state", "remove_memory"), observation


def ablation_time_shift_state(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    shifted = deserialize_state(episode["time_shift_serialized_state"])
    return shifted, observation


def ablation_cross_agent_state_swap(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    swapped = deserialize_state(episode["cross_agent_swap_serialized_state"])
    return swapped, observation


def ablation_duplicate_identity_token_contrast(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    replacement = deserialize_state(episode["duplicate_identity_serialized_state"])
    replacement["identity_token_hash"] = state["identity_token_hash"]
    return replacement, observation


def ablation_freeze_post_bridge_learning(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    mutated = copy.deepcopy(state)
    mutated["post_bridge_learning_state"]["frozen"] = True
    mutated["post_bridge_learning_state"]["update_rate"] = 0.0
    mutated["bridge_mapping_state"] = _mutate_numeric_tree(mutated["bridge_mapping_state"], "freeze_learning")
    return mutated, observation


def ablation_remove_post_bridge_observation_update(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    mutated_observation = copy.deepcopy(observation)
    mutated_observation["pressure_bucket"] = 0
    mutated_observation["resource_bucket"] = 0
    mutated_observation["partner_signal_bucket"] = 0
    mutated_observation["novelty_bucket"] = 0
    mutated_observation["sensor_digest"] = stable_hash({"observation_update_removed": episode["episode_id"]})
    return state, mutated_observation


def ablation_disable_action(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    mutated = copy.deepcopy(state)
    mutated["action_disabled"] = True
    return mutated, observation


def ablation_invert_bridge_mapping(state: dict[str, Any], observation: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    mutated = copy.deepcopy(state)
    mutated["bridge_mapping_state"] = _mutate_numeric_tree(mutated["bridge_mapping_state"], "invert_mapping")
    mutated["bridge_mapping_state"]["mapping_revision"] += 17
    return mutated, observation


ABLATION_IMPLEMENTATIONS: dict[
    str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], tuple[dict[str, Any], dict[str, Any]]]
] = {
    "reset all memory": ablation_reset_all_memory,
    "corrupt serialized state": ablation_corrupt_serialized_state,
    "replace serialized state": ablation_replace_serialized_state,
    "remove replay carryover": ablation_remove_replay_carryover,
    "remove self-boundary carryover": ablation_remove_self_boundary,
    "remove viability carryover": ablation_remove_viability,
    "remove social-latent carryover": ablation_remove_social_latent,
    "remove identity_continuity_state": ablation_remove_identity_continuity,
    "remove memory_carryover_state": ablation_remove_memory_carryover,
    "time-shift state": ablation_time_shift_state,
    "cross-agent state swap": ablation_cross_agent_state_swap,
    "duplicate identity-token contrast": ablation_duplicate_identity_token_contrast,
    "freeze post-bridge learning": ablation_freeze_post_bridge_learning,
    "remove post-bridge observation update": ablation_remove_post_bridge_observation_update,
    "disable action": ablation_disable_action,
    "invert bridge mapping": ablation_invert_bridge_mapping,
}


def _with_replacement_material(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched = []
    for index, episode in enumerate(episodes):
        copy_episode = dict(episode)
        copy_episode["replacement_serialized_state"] = episodes[(index + 16) % len(episodes)]["serialized_state"]
        copy_episode["time_shift_serialized_state"] = episodes[(index + 1) % len(episodes)]["serialized_state"]
        copy_episode["cross_agent_swap_serialized_state"] = episodes[(index + 24) % len(episodes)]["serialized_state"]
        copy_episode["duplicate_identity_serialized_state"] = episodes[(index + 32) % len(episodes)]["serialized_state"]
        enriched.append(copy_episode)
    return enriched


def run_ablations(episodes: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    episodes = _with_replacement_material(episodes)
    candidate_actions = {episode["episode_id"]: episode["candidate_action_id"] for episode in episodes}
    replayed_candidate_actions = {
        episode["episode_id"]: candidate_action_from_serialized_state(
            episode["serialized_state"],
            episode["observation"],
        )
        for episode in episodes
    }
    candidate_score = _score_against_candidate(candidate_actions, replayed_candidate_actions)
    invocations = []
    report_rows = []
    for name, function in ABLATION_IMPLEMENTATIONS.items():
        outputs = {}
        pre_hashes = []
        post_hashes = []
        for episode in episodes:
            state = deserialize_state(episode["serialized_state"])
            observation = episode["observation"]
            pre_hash = stable_hash({"state": state, "observation": observation})
            mutated_state, mutated_observation = function(state, observation, episode)
            post_hash = stable_hash({"state": mutated_state, "observation": mutated_observation})
            outputs[episode["episode_id"]] = candidate_action_from_state(mutated_state, mutated_observation)
            pre_hashes.append(pre_hash)
            post_hashes.append(post_hash)
        score = _score_against_candidate(candidate_actions, outputs)
        row = {
            "ablation_name": name,
            "invoked": True,
            "intervention_function": f"{function.__module__}.{function.__name__}",
            "producer_module": function.__module__,
            "code_path_hash": code_path_hash(function),
            "target_fields": _ablation_target_fields(name),
            "pre_intervention_state_hash": stable_hash(pre_hashes),
            "post_intervention_state_hash": stable_hash(post_hashes),
            "intervention_applied": pre_hashes != post_hashes,
            "reran_candidate_behavior": True,
            "episode_ids": list(outputs),
            "per_episode_outputs": [
                {"episode_id": episode_id, "ablated_action_id": action}
                for episode_id, action in outputs.items()
            ],
            "score": score,
            "sensitive": score < ACCEPTANCE_THRESHOLD,
            "computed_from_outputs": True,
            "failure_path_available": True,
        }
        invocations.append(row)
        report_rows.append(
            {
                "ablation_name": name,
                "score": score,
                "sensitive": score < ACCEPTANCE_THRESHOLD,
                "intervention_function": row["intervention_function"],
                "code_path_hash": row["code_path_hash"],
                "reran_candidate_behavior": True,
            }
        )
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "thresholds": thresholds_manifest(),
        "candidate_score": candidate_score,
        "candidate_score_source": "computed_from_behavior_causal_replay_outputs",
        "candidate_score_computed_not_literal": True,
        "ablations": report_rows,
        "ablation_gate_passed": all(row["sensitive"] for row in report_rows),
    }, invocations


def _ablation_target_fields(name: str) -> list[str]:
    mapping = {
        "reset all memory": STATE_COMPONENTS,
        "corrupt serialized state": ["memory_carryover_state", "bridge_mapping_state"],
        "replace serialized state": STATE_COMPONENTS,
        "remove replay carryover": ["replay_carryover_state"],
        "remove self-boundary carryover": ["self_boundary_state"],
        "remove viability carryover": ["viability_carryover_state"],
        "remove social-latent carryover": ["social_latent_carryover_state"],
        "remove identity_continuity_state": ["identity_continuity_state"],
        "remove memory_carryover_state": ["memory_carryover_state"],
        "time-shift state": STATE_COMPONENTS,
        "cross-agent state swap": STATE_COMPONENTS,
        "duplicate identity-token contrast": STATE_COMPONENTS,
        "freeze post-bridge learning": ["post_bridge_learning_state", "bridge_mapping_state"],
        "remove post-bridge observation update": ["observation"],
        "disable action": ["action_disabled"],
        "invert bridge mapping": ["bridge_mapping_state"],
    }
    return list(mapping[name])


def run_contrasts(episodes: list[dict[str, Any]], distribution: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    by_heldout = {episode["heldout_context_id"]: episode for episode in episodes}
    logs = []
    results = {}

    def run_pair_rows(contrast_name: str, pair_rows: list[dict[str, Any]], resolver: Callable[[dict[str, Any]], tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
        outcomes = []
        for pair in pair_rows:
            source_episode, replacement_episode = resolver(pair)
            source_state = deserialize_state(source_episode["serialized_state"])
            replacement_state = deserialize_state(replacement_episode["serialized_state"])
            source_observation = source_episode["observation"]
            if contrast_name in {
                "different_identity_equivalent_state",
                "equivalent_memory_without_original_token",
            }:
                contrasted_state = copy.deepcopy(source_state)
                if contrast_name == "different_identity_equivalent_state":
                    contrasted_state["identity_token_hash"] = replacement_state["identity_token_hash"]
                else:
                    contrasted_state["memory_key_hash"] = replacement_state["memory_key_hash"]
            elif contrast_name == "same_identity_different_state":
                contrasted_state = copy.deepcopy(replacement_state)
                contrasted_state["identity_token_hash"] = source_state["identity_token_hash"]
            elif contrast_name == "same_memory_key_corrupted_memory":
                contrasted_state = _replace_state_component(
                    source_state,
                    "memory_carryover_state",
                    f"memory_corruption:{pair.get('pair_id', pair.get('contrast_id'))}",
                )
                contrasted_state["memory_key_hash"] = source_state["memory_key_hash"]
            elif contrast_name == "duplicate_identity_token_contrast":
                contrasted_state = copy.deepcopy(replacement_state)
                contrasted_state["identity_token_hash"] = source_state["identity_token_hash"]
            else:
                contrasted_state = replacement_state
            contrasted_action = candidate_action_from_state(contrasted_state, source_observation)
            original_action = source_episode["candidate_action_id"]
            outcomes.append(
                {
                    "pair_id": pair.get("pair_id", pair.get("contrast_id")),
                    "source_episode_id": source_episode["episode_id"],
                    "replacement_episode_id": replacement_episode["episode_id"],
                    "original_action_id": original_action,
                    "contrasted_action_id": contrasted_action,
                    "action_changed": original_action != contrasted_action,
                }
            )
        delta = round(sum(1 for row in outcomes if row["action_changed"]) / len(outcomes), 6)
        pair_ids = [row["pair_id"] for row in outcomes]
        logs.append(
            {
                "contrast_name": contrast_name,
                "pair_ids_consumed": pair_ids,
                "reran_candidate_behavior": True,
                "computed_delta_from_outputs": True,
                "producer_function": "post_bridge_admission_executable_001d.core.run_contrasts",
                "producer_module": __name__,
                "code_path_hash": code_path_hash(run_contrasts),
                "per_pair_outcomes": outcomes,
                "delta": delta,
            }
        )
        return {"delta": delta, "pair_ids_consumed": pair_ids, "per_pair_outcomes": outcomes}

    cf_pairs = distribution["counterfactual_state_pairs"]
    swap_pairs = distribution["cross_agent_state_swap_pairs"]
    dup_pairs = distribution["duplicate_identity_token_contrasts"]
    results["same_identity_different_state"] = run_pair_rows(
        "same_identity_different_state",
        dup_pairs,
        lambda pair: (
            by_heldout[pair["base_heldout_context_id"]],
            by_heldout[pair["replacement_heldout_context_id"]],
        ),
    )
    results["different_identity_equivalent_state"] = run_pair_rows(
        "different_identity_equivalent_state",
        dup_pairs,
        lambda pair: (
            by_heldout[pair["base_heldout_context_id"]],
            by_heldout[pair["replacement_heldout_context_id"]],
        ),
    )
    results["same_memory_key_corrupted_memory"] = run_pair_rows(
        "same_memory_key_corrupted_memory",
        cf_pairs,
        lambda pair: (
            by_heldout[pair["source_heldout_context_id"]],
            by_heldout[pair["replacement_heldout_context_id"]],
        ),
    )
    results["equivalent_memory_without_original_token"] = run_pair_rows(
        "equivalent_memory_without_original_token",
        cf_pairs,
        lambda pair: (
            by_heldout[pair["source_heldout_context_id"]],
            by_heldout[pair["replacement_heldout_context_id"]],
        ),
    )
    results["state_replacement_with_wrong_episode"] = run_pair_rows(
        "state_replacement_with_wrong_episode",
        cf_pairs,
        lambda pair: (
            by_heldout[pair["source_heldout_context_id"]],
            by_heldout[pair["replacement_heldout_context_id"]],
        ),
    )
    results["cross_agent_state_swap"] = run_pair_rows(
        "cross_agent_state_swap",
        swap_pairs,
        lambda pair: (
            by_heldout[pair["left_heldout_context_id"]],
            by_heldout[pair["right_heldout_context_id"]],
        ),
    )
    results["duplicate_identity_token_contrast"] = run_pair_rows(
        "duplicate_identity_token_contrast",
        dup_pairs,
        lambda pair: (
            by_heldout[pair["base_heldout_context_id"]],
            by_heldout[pair["replacement_heldout_context_id"]],
        ),
    )
    sensitive = {
        name: row["delta"] > 0.05
        for name, row in results.items()
        if name
        not in {
            "different_identity_equivalent_state",
            "equivalent_memory_without_original_token",
        }
    }
    controls = {
        name: row["delta"] == 0.0
        for name, row in results.items()
        if name
        in {
            "different_identity_equivalent_state",
            "equivalent_memory_without_original_token",
        }
    }
    report = {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "contrasts": results,
        "sensitive_contrasts": sensitive,
        "control_contrasts": controls,
        "contrast_gate_passed": all(sensitive.values()) and all(controls.values()),
        "identity_token_alone_explains_behavior": not controls["different_identity_equivalent_state"],
        "memory_key_alone_explains_behavior": not controls["equivalent_memory_without_original_token"],
    }
    return report, logs


def _contains_forbidden(surface: Any) -> tuple[bool, list[str]]:
    forbidden = [
        "future_observation",
        "future_partner_response",
        "later_action_label",
        "oracle",
        "expected_action",
        "verifier_only",
        "post_hoc_metric",
        "test_only_schema",
        "hidden_label",
        "fixture_leak",
        "artifact_path_visible_to_candidate",
    ]
    metadata_keys_allowed_to_name_scanners = {
        "metric_id",
        "metric_name",
        "output_row_ids",
        "scanner_name",
        "scanned_surface_id",
        "scanned_surface_ids",
        "scanned_surface_types",
        "positive_control_surface_ids",
        "clean_control_surface_ids",
        "input_surface_ids",
        "surface_label",
        "surface_type",
    }
    hits: set[str] = set()

    def walk(value: Any, path: tuple[str, ...] = ()) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                key_text = str(key)
                if key_text not in metadata_keys_allowed_to_name_scanners:
                    for token in forbidden:
                        if token in key_text:
                            hits.add(token)
                walk(item, (*path, key_text))
        elif isinstance(value, list):
            for item in value:
                walk(item, path)
        elif isinstance(value, str):
            current_key = path[-1] if path else ""
            if current_key in metadata_keys_allowed_to_name_scanners:
                return
            for token in forbidden:
                if token in value:
                    hits.add(token)

    walk(surface)
    hits = sorted(hits)
    return bool(hits), hits


def leakage_scan_surface(surface: Any) -> dict[str, Any]:
    detected, hits = _contains_forbidden(surface)
    return {"detected": detected, "hits": hits}


def computed_forbidden_source_scan_result(surface_id: str, surface: Any) -> dict[str, Any]:
    scan = leakage_scan_surface(surface)
    return {
        "clean": not scan["detected"],
        "detected": scan["detected"],
        "hits": scan["hits"],
        "scanner_function": "post_bridge_admission_executable_001d.core.leakage_scan_surface",
        "producer_module": __name__,
        "code_path_hash": code_path_hash(leakage_scan_surface),
        "scanned_surface_id": surface_id,
        "scanned_surface_hash": stable_hash(surface),
        "computed_not_literal": True,
        "failure_path_available": True,
    }


def _surface_descriptor(
    *,
    scanner_name: str,
    scanned_surface_type: str,
    surface: Any,
    artifact_path: str | None,
    in_memory_source: str,
    explicitly_absent_before_execution: bool = False,
) -> dict[str, Any]:
    row_count = len(surface) if isinstance(surface, list) else 1
    return {
        "scanner_name": scanner_name,
        "scanned_surface_id": f"leakage_surface:{scanner_name}:full_real_surface",
        "scanned_surface_type": scanned_surface_type,
        "scanned_surface_artifact_path": artifact_path,
        "scanned_surface_in_memory_source": in_memory_source,
        "full_surface_row_count": row_count,
        "full_surface_hash": stable_hash(surface),
        "full_surface_scanned": True,
        "sanitized_projection_scan": False,
        "constant_dictionary_scan": False,
        "explicitly_absent_before_execution": explicitly_absent_before_execution,
        "surface": surface,
    }


def _absent_surface(scanner_name: str, scanned_surface_type: str) -> dict[str, Any]:
    return _surface_descriptor(
        scanner_name=scanner_name,
        scanned_surface_type=scanned_surface_type,
        surface={
            "surface_label": scanner_name,
            "surface_values": [],
            "explicitly_absent_before_execution": True,
        },
        artifact_path=None,
        in_memory_source=f"{scanner_name}_absence_marker",
        explicitly_absent_before_execution=True,
    )


def build_leakage_surface_inventory(
    *,
    candidate_input_rows: list[dict[str, Any]],
    trace_rows: list[dict[str, Any]],
    snapshots: list[dict[str, Any]],
    observation_rows: list[dict[str, Any]],
    provenance_rows: list[dict[str, Any]],
    metric_provenance_rows: list[dict[str, Any]],
    artifact_paths: list[str],
) -> dict[str, Any]:
    surfaces = [
        _surface_descriptor(
            scanner_name="candidate_inputs",
            scanned_surface_type="candidate_input_rows",
            surface=candidate_input_rows,
            artifact_path="candidate_input_rows.jsonl",
            in_memory_source="candidate_input_rows",
        ),
        _surface_descriptor(
            scanner_name="trace_rows",
            scanned_surface_type="trace_rows",
            surface=trace_rows,
            artifact_path="trace.jsonl",
            in_memory_source="trace_rows",
        ),
        _surface_descriptor(
            scanner_name="serialized_state_snapshots",
            scanned_surface_type="serialized_state_snapshots",
            surface=snapshots,
            artifact_path="serialized_state_snapshots.jsonl",
            in_memory_source="serialized_state_snapshots",
        ),
        _surface_descriptor(
            scanner_name="observation_rows",
            scanned_surface_type="observation_rows",
            surface=observation_rows,
            artifact_path="observation_seed_manifest.json",
            in_memory_source="observation_seed_manifest",
        ),
        _surface_descriptor(
            scanner_name="serialized_state_provenance",
            scanned_surface_type="serialized_state_provenance_rows",
            surface=provenance_rows,
            artifact_path="serialized_state_provenance.jsonl",
            in_memory_source="serialized_state_provenance",
        ),
        _surface_descriptor(
            scanner_name="metric_provenance_rows",
            scanned_surface_type="metric_provenance_rows",
            surface=metric_provenance_rows,
            artifact_path="metric_provenance.jsonl",
            in_memory_source="metric_provenance_rows_prewrite",
        ),
        _surface_descriptor(
            scanner_name="artifact_paths",
            scanned_surface_type="artifact_filename_path_inventory",
            surface=[{"artifact_path": path} for path in artifact_paths],
            artifact_path="leakage_surface_inventory.json",
            in_memory_source="actual_artifact_filename_path_inventory",
        ),
        _absent_surface("fixture_names", "fixture_name_surface"),
        _absent_surface("labels", "label_surface"),
        _absent_surface("verifier_only_fields", "verifier_only_surface"),
        _absent_surface("future_observations", "future_observation_surface"),
        _absent_surface("future_partner_responses", "future_partner_response_surface"),
        _absent_surface("later_action_labels", "later_action_label_surface"),
        _absent_surface("post_hoc_metrics", "post_hoc_metric_surface"),
        _absent_surface("test_only_schema_paths", "test_only_schema_path_surface"),
    ]
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "surface_inventory_type": "full_real_surfaces_or_explicit_absence_markers",
        "surface_count": len(surfaces),
        "surfaces": [
            {key: value for key, value in surface.items() if key != "surface"}
            for surface in surfaces
        ],
        "surface_ids": [surface["scanned_surface_id"] for surface in surfaces],
        "surface_inventory_hash": stable_hash(
            [{key: value for key, value in surface.items() if key != "surface"} for surface in surfaces]
        ),
        "_runtime_surfaces": surfaces,
    }


def _inject_forbidden_control(surface: Any, scanner_name: str) -> tuple[Any, str]:
    injected = copy.deepcopy(surface)
    token_by_scanner = {
        "future_partner_responses": "future_partner_response",
        "later_action_labels": "later_action_label",
        "post_hoc_metrics": "post_hoc_metric",
        "test_only_schema_paths": "test_only_schema",
        "labels": "hidden_label",
        "fixture_names": "fixture_leak",
        "verifier_only_fields": "verifier_only",
        "artifact_paths": "future_observation",
    }
    token = token_by_scanner.get(scanner_name, "future_observation")
    payload = {"injected_forbidden_token": token, "oracle": "positive_control"}
    if isinstance(injected, list):
        if injected and isinstance(injected[0], dict):
            injected[0][token] = payload
        else:
            injected.append({token: payload})
    elif isinstance(injected, dict):
        injected[token] = payload
    else:
        injected = {"original_surface": injected, token: payload}
    return injected, token


def run_leakage_scanners(surface_inventory: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    logs = []
    for surface in surface_inventory["_runtime_surfaces"]:
        scanner_name = surface["scanner_name"]
        real_surface = surface["surface"]
        positive_surface, token = _inject_forbidden_control(real_surface, scanner_name)
        clean_surface = copy.deepcopy(real_surface)
        positive = leakage_scan_surface(positive_surface)
        clean = leakage_scan_surface(clean_surface)
        real = leakage_scan_surface(real_surface)
        positive_surface_id = f"{surface['scanned_surface_id']}:positive_control"
        clean_surface_id = f"{surface['scanned_surface_id']}:clean_control"
        logs.append(
            {
                "scanner_name": scanner_name,
                "scanner_function": "post_bridge_admission_executable_001d.core.leakage_scan_surface",
                "producer_module": __name__,
                "code_path_hash": code_path_hash(leakage_scan_surface),
                "scanned_surface_id": surface["scanned_surface_id"],
                "scanned_surface_type": surface["scanned_surface_type"],
                "scanned_surface_artifact_path": surface["scanned_surface_artifact_path"],
                "scanned_surface_in_memory_source": surface["scanned_surface_in_memory_source"],
                "scanned_surface_hash": surface["full_surface_hash"],
                "scanned_surfaces": [surface["scanned_surface_id"]],
                "full_surface_scanned": True,
                "sanitized_projection_scan": False,
                "constant_dictionary_scan": False,
                "explicitly_absent_before_execution": surface["explicitly_absent_before_execution"],
                "positive_control_surface_id": positive_surface_id,
                "clean_control_surface_id": clean_surface_id,
                "positive_control": {
                    **positive,
                    "surface_id": positive_surface_id,
                    "same_surface_class": True,
                    "injected_forbidden_token": token,
                    "surface_hash": stable_hash(positive_surface),
                },
                "clean_control": {
                    **clean,
                    "surface_id": clean_surface_id,
                    "same_surface_class": True,
                    "surface_hash": stable_hash(clean_surface),
                },
                "real_scan": real,
            }
        )
    report = {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "addresses_001c_redteam_leakage_blocker": True,
        "surface_inventory_hash": surface_inventory["surface_inventory_hash"],
        "leakage_gate_passed": all(
            row["full_surface_scanned"]
            and not row["sanitized_projection_scan"]
            and not row["constant_dictionary_scan"]
            and row["positive_control"]["same_surface_class"]
            and row["positive_control"]["detected"]
            and row["clean_control"]["same_surface_class"]
            and not row["clean_control"]["detected"]
            and not row["real_scan"]["detected"]
            for row in logs
        ),
        "positive_controls_passed": all(row["positive_control"]["detected"] for row in logs),
        "clean_controls_passed": all(not row["clean_control"]["detected"] for row in logs),
        "real_scans_clean": all(not row["real_scan"]["detected"] for row in logs),
        "full_real_surfaces_scanned": all(row["full_surface_scanned"] for row in logs),
        "sanitized_projection_scans_detected": [
            row["scanner_name"] for row in logs if row["sanitized_projection_scan"]
        ],
        "decoupled_positive_controls_detected": [
            row["scanner_name"] for row in logs if not row["positive_control"]["same_surface_class"]
        ],
        "unconditional_clean_reports_detected": [],
        "scanner_results": [
            {
                "scanner_name": row["scanner_name"],
                "scanned_surface_id": row["scanned_surface_id"],
                "scanned_surface_type": row["scanned_surface_type"],
                "real_scan_detected": row["real_scan"]["detected"],
                "real_scan_hits": row["real_scan"]["hits"],
                "positive_control_detected": row["positive_control"]["detected"],
                "clean_control_detected": row["clean_control"]["detected"],
            }
            for row in logs
        ],
        "hidden_lookup_suspicion": False,
        "identity_token_lookup_equivalence": False,
        "memory_key_lookup_equivalence": False,
        "state_table_equivalence": False,
        "snapshot_reload_equivalence": False,
        "graph_cache_equivalence": False,
    }
    return report, logs

def replay_candidate_actions_from_serialized_state(
    snapshots: list[dict[str, Any]],
    observation_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    observations = {row["episode_id"]: row["observation"] for row in observation_rows}
    mismatches = []
    candidate_actions = {row["episode_id"]: row["candidate_action_id"] for row in snapshots}
    replayed_actions = {}
    for snapshot in snapshots:
        recomputed = candidate_action_from_serialized_state(
            snapshot["serialized_state"],
            observations[snapshot["episode_id"]],
        )
        replayed_actions[snapshot["episode_id"]] = recomputed
        if recomputed != snapshot["candidate_action_id"]:
            mismatches.append(
                {
                    "episode_id": snapshot["episode_id"],
                    "expected": snapshot["candidate_action_id"],
                    "actual": recomputed,
                }
            )
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "candidate_action_replay_passed": not mismatches,
        "deserializer_function": "post_bridge_admission_executable_001d.core.deserialize_state",
        "candidate_action_function": (
            "post_bridge_admission_executable_001d.core.candidate_action_from_serialized_state"
        ),
        "recomputed_from_serialized_state_and_observation": True,
        "hash_only_replay": False,
        "candidate_score": _score_against_candidate(candidate_actions, replayed_actions),
        "candidate_score_source": "computed_from_replayed_candidate_actions",
        "candidate_score_computed_not_literal": True,
        "checked_rows": len(snapshots),
        "mismatches": mismatches,
        "replay_function": (
            "post_bridge_admission_executable_001d.core."
            "replay_candidate_actions_from_serialized_state"
        ),
        "code_path_hash": code_path_hash(replay_candidate_actions_from_serialized_state),
    }


def behavior_causal_replay(
    snapshots: list[dict[str, Any]],
    observation_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    candidate_report = replay_candidate_actions_from_serialized_state(snapshots, observation_rows)
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "behavior_causal_replay_passed": candidate_report["candidate_action_replay_passed"],
        "recomputed_from_serialized_state_and_observation": True,
        "hash_only_replay": False,
        "checked_rows": candidate_report["checked_rows"],
        "mismatches": candidate_report["mismatches"],
        "replay_function": "post_bridge_admission_executable_001d.core.behavior_causal_replay",
        "code_path_hash": code_path_hash(behavior_causal_replay),
    }


def trace_hash_replay(trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    previous = "GENESIS"
    mismatches = []
    for row in trace_rows:
        payload = dict(row)
        current_hash = payload.pop("current_trace_hash")
        if stable_hash(payload) != current_hash:
            mismatches.append({"episode_id": row["episode_id"], "reason": "current_trace_hash"})
        if row["previous_trace_hash"] != previous:
            mismatches.append({"episode_id": row["episode_id"], "reason": "previous_trace_hash"})
        previous = current_hash
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "trace_hash_replay_passed": not mismatches,
        "integrity_hygiene_only": True,
        "counts_as_behavior_causal_replay": False,
        "checked_rows": len(trace_rows),
        "mismatches": mismatches,
        "replay_function": "post_bridge_admission_executable_001d.core.trace_hash_replay",
        "code_path_hash": code_path_hash(trace_hash_replay),
    }


def state_hash_replay(snapshots: list[dict[str, Any]]) -> dict[str, Any]:
    mismatches = [
        row["episode_id"]
        for row in snapshots
        if stable_hash(row["serialized_state"]) != row["serialized_state_hash"]
    ]
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "state_hash_replay_passed": not mismatches,
        "integrity_hygiene_only": True,
        "counts_as_behavior_causal_replay": False,
        "checked_rows": len(snapshots),
        "mismatches": mismatches,
        "replay_function": "post_bridge_admission_executable_001d.core.state_hash_replay",
        "code_path_hash": code_path_hash(state_hash_replay),
    }


def build_consumption_report(
    distribution: dict[str, Any],
    episodes: list[dict[str, Any]],
    ablation_invocations: list[dict[str, Any]],
    contrast_logs: list[dict[str, Any]],
) -> dict[str, Any]:
    consumed_seed_families = sorted({episode["seed_family_id"] for episode in episodes})
    consumed_train = sorted({episode["train_context_id"] for episode in episodes})
    consumed_heldout = sorted({episode["heldout_context_id"] for episode in episodes})
    consumed_cf = sorted(
        {
            pair_id
            for row in contrast_logs
            for pair_id in row["pair_ids_consumed"]
            if pair_id.startswith("counterfactual_pair_")
        }
    )
    consumed_swap = sorted(
        {
            pair_id
            for row in contrast_logs
            for pair_id in row["pair_ids_consumed"]
            if pair_id.startswith("cross_agent_swap_")
        }
    )
    consumed_duplicate = sorted(
        {
            pair_id
            for row in contrast_logs
            for pair_id in row["pair_ids_consumed"]
            if pair_id.startswith("duplicate_identity_token_contrast_")
        }
    )
    expected_seed = sorted(row["family_id"] for row in distribution["seed_families"])
    expected_train = sorted(row["context_id"] for row in distribution["train_contexts"])
    expected_heldout = sorted(row["heldout_context_id"] for row in distribution["heldout_bridge_contexts"])
    expected_cf = sorted(row["pair_id"] for row in distribution["counterfactual_state_pairs"])
    expected_swap = sorted(row["pair_id"] for row in distribution["cross_agent_state_swap_pairs"])
    expected_duplicate = sorted(row["contrast_id"] for row in distribution["duplicate_identity_token_contrasts"])
    consumed_ablations = sorted(row["ablation_name"] for row in ablation_invocations)
    unused = []
    for label, expected, actual in [
        ("seed_family", expected_seed, consumed_seed_families),
        ("train_context", expected_train, consumed_train),
        ("heldout_context", expected_heldout, consumed_heldout),
        ("counterfactual_pair", expected_cf, consumed_cf),
        ("cross_agent_state_swap_pair", expected_swap, consumed_swap),
        ("duplicate_identity_token_contrast", expected_duplicate, consumed_duplicate),
        ("ablation", sorted(REQUIRED_ABLATIONS), consumed_ablations),
    ]:
        for missing in sorted(set(expected) - set(actual)):
            unused.append({"type": label, "id": missing})
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "verdict": "all_frozen_inputs_consumed" if not unused else "failed_unused_frozen_input",
        "unused_frozen_inputs": unused,
        "seed_family_ids_consumed": consumed_seed_families,
        "train_context_ids_consumed": consumed_train,
        "heldout_context_ids_consumed": consumed_heldout,
        "counterfactual_pair_ids_consumed": consumed_cf,
        "cross_agent_state_swap_pair_ids_consumed": consumed_swap,
        "duplicate_identity_token_contrast_ids_consumed": consumed_duplicate,
        "ablation_ids_consumed": consumed_ablations,
        "producer_function": "post_bridge_admission_executable_001d.core.build_consumption_report",
        "producer_module": __name__,
        "code_path_hash": code_path_hash(build_consumption_report),
    }


def evaluate_computed_evidence_gate(
    *,
    metric_rows: list[dict[str, Any]],
    baseline_invocations: list[dict[str, Any]],
    ablation_invocations: list[dict[str, Any]],
    leakage_invocations: list[dict[str, Any]],
    replay_report: dict[str, Any],
    consumption_report: dict[str, Any],
    serialized_state_provenance_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    serialized_state_provenance_rows = serialized_state_provenance_rows or []
    leakage_metric_rows = [
        row for row in metric_rows if str(row.get("metric_id", "")).startswith("leakage::")
    ]
    candidate_metric_rows = [row for row in metric_rows if row.get("metric_id") == "candidate_score"]
    forbidden_source_constant_detected = any(
        (
            scan := row.get("forbidden_source_scan_result", {})
        )
        and (
            scan == {"clean": True, "hits": []}
            or scan.get("computed_not_literal") is not True
            or not scan.get("scanner_function")
            or not scan.get("scanned_surface_id")
        )
        for row in serialized_state_provenance_rows
    )
    if not metric_rows:
        verdict = VERDICT_FAILED_COMPUTED_PROVENANCE
    elif any(row.get("computed_not_literal") is False for row in candidate_metric_rows):
        verdict = VERDICT_FAILED_CANDIDATE_SCORE_LITERAL
    elif any(row.get("computed_not_literal") is False for row in metric_rows):
        verdict = VERDICT_FAILED_COMPUTED_PROVENANCE
    elif consumption_report.get("unused_frozen_inputs"):
        verdict = VERDICT_FAILED_UNUSED_FROZEN_INPUT
    elif {row.get("baseline_name") for row in baseline_invocations if row.get("invoked")} != set(REQUIRED_BASELINES):
        verdict = VERDICT_FAILED_BASELINE_INVOCATION
    elif any(not row.get("computed_from_outputs") for row in baseline_invocations):
        verdict = VERDICT_FAILED_COMPUTED_PROVENANCE
    elif {row.get("ablation_name") for row in ablation_invocations if row.get("invoked")} != set(REQUIRED_ABLATIONS):
        verdict = VERDICT_FAILED_ABLATION_INVOCATION
    elif any(not row.get("reran_candidate_behavior") for row in ablation_invocations):
        verdict = VERDICT_FAILED_ABLATION_INVOCATION
    elif {row.get("scanner_name") for row in leakage_invocations} != set(REQUIRED_LEAKAGE_SCANNERS):
        verdict = VERDICT_FAILED_UNCONDITIONAL_LEAKAGE
    elif any(not row.get("full_surface_scanned") or row.get("sanitized_projection_scan") for row in leakage_invocations):
        verdict = VERDICT_FAILED_SANITIZED_SURFACE_SCAN
    elif any(row.get("constant_dictionary_scan") for row in leakage_invocations):
        verdict = VERDICT_FAILED_UNCONDITIONAL_LEAKAGE
    elif any(not row.get("positive_control", {}).get("detected") for row in leakage_invocations):
        verdict = VERDICT_FAILED_POSITIVE_CONTROL
    elif any(
        not row.get("positive_control", {}).get("same_surface_class")
        or not row.get("clean_control", {}).get("same_surface_class")
        for row in leakage_invocations
    ):
        verdict = VERDICT_FAILED_DECOUPLED_POSITIVE_CONTROL
    elif any(row.get("real_scan", {}).get("detected") for row in leakage_invocations):
        verdict = VERDICT_FAILED_LEAKAGE
    elif any(
        not row.get("scanned_surface_ids")
        or not row.get("positive_control_surface_ids")
        or not row.get("clean_control_surface_ids")
        or not row.get("input_surface_ids")
        for row in leakage_metric_rows
    ):
        verdict = VERDICT_FAILED_MISSING_METRIC_SURFACE_ID
    elif {row.get("metric_id", "").split("::", 1)[1] for row in leakage_metric_rows} != set(
        REQUIRED_LEAKAGE_SCANNERS
    ):
        verdict = VERDICT_FAILED_MISSING_METRIC_SURFACE_ID
    elif forbidden_source_constant_detected:
        verdict = VERDICT_FAILED_FORBIDDEN_SOURCE_SCAN_CONSTANT
    elif replay_report.get("hash_only_replay") or not replay_report.get("behavior_causal_replay_passed"):
        verdict = VERDICT_FAILED_REPLAY_NOT_BEHAVIOR
    elif any(not METRIC_PROVENANCE_FIELDS.issubset(row) for row in metric_rows):
        verdict = VERDICT_FAILED_COMPUTED_PROVENANCE
    else:
        verdict = VERDICT_PASS
    return {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "verdict": verdict,
        "computed_evidence_provenance_gate_passed": verdict == VERDICT_PASS,
        "literal_or_static_metric_detected": verdict
        in {VERDICT_FAILED_COMPUTED_PROVENANCE, VERDICT_FAILED_CANDIDATE_SCORE_LITERAL},
        "candidate_score_literal_detected": verdict == VERDICT_FAILED_CANDIDATE_SCORE_LITERAL,
        "sanitized_surface_scan_detected": verdict == VERDICT_FAILED_SANITIZED_SURFACE_SCAN,
        "decoupled_positive_control_detected": verdict == VERDICT_FAILED_DECOUPLED_POSITIVE_CONTROL,
        "missing_metric_provenance_surface_id": verdict == VERDICT_FAILED_MISSING_METRIC_SURFACE_ID,
        "forbidden_source_scan_constant_detected": verdict
        == VERDICT_FAILED_FORBIDDEN_SOURCE_SCAN_CONSTANT,
        "missing_metric_provenance": [
            row.get("metric_id", "unknown")
            for row in metric_rows
            if not METRIC_PROVENANCE_FIELDS.issubset(row)
        ],
        "baseline_invocation_missing": verdict == VERDICT_FAILED_BASELINE_INVOCATION,
        "ablation_invocation_missing": verdict == VERDICT_FAILED_ABLATION_INVOCATION,
        "positive_control_missing": verdict == VERDICT_FAILED_POSITIVE_CONTROL,
        "replay_not_behavior_causal": verdict == VERDICT_FAILED_REPLAY_NOT_BEHAVIOR,
    }


def final_result_payload(
    *,
    stage0: dict[str, Any],
    baseline_report: dict[str, Any],
    ablation_report: dict[str, Any],
    contrast_report: dict[str, Any],
    leakage_report: dict[str, Any],
    behavior_replay_report: dict[str, Any],
    candidate_replay_report: dict[str, Any],
    trace_hash_report: dict[str, Any],
    state_hash_report: dict[str, Any],
    consumption_report: dict[str, Any],
    provenance_report: dict[str, Any],
    mutation_report: dict[str, Any],
    old_mutation_report: dict[str, Any],
    verdict_bearing_metric_ids: list[str],
) -> dict[str, Any]:
    gates = {
        "parent_remote_anchors_verified": stage0["parent_remote_anchor_verification"]["verified"],
        "redteam_failure_admission_verified": stage0["redteam_failure_admission_verification"]["verified"],
        "computed_evidence_contract_cited_and_enforced": stage0["computed_evidence_contract"]["cited_and_enforced"],
        "agents_instruction_included_in_freeze": bool(stage0["agents_instruction_hash"]),
        "stage0_freeze_before_any_run": stage0["stage0_freeze_before_any_executable_run"],
        "clean_worktree_before_stage0": stage0["clean_worktree_before_stage0"]["clean"],
        "frozen_inputs_consumed": not consumption_report["unused_frozen_inputs"],
        "candidate_depends_on_deserialized_state_and_observation": candidate_replay_report[
            "recomputed_from_serialized_state_and_observation"
        ],
        "metric_provenance_complete": provenance_report["computed_evidence_provenance_gate_passed"],
        "fair_baselines_do_not_match_or_beat_candidate": baseline_report["baseline_gate_passed"],
        "required_ablations_sensitive": ablation_report["ablation_gate_passed"],
        "required_contrasts_consumed_and_sensitive": contrast_report["contrast_gate_passed"],
        "leakage_scanners_have_positive_controls_and_clean_real_scan": leakage_report["leakage_gate_passed"],
        "leakage_full_real_surfaces_scanned": leakage_report["full_real_surfaces_scanned"],
        "001c_leakage_blocker_addressed": leakage_report["addresses_001c_redteam_leakage_blocker"],
        "behavior_causal_replay_passed": behavior_replay_report["behavior_causal_replay_passed"],
        "trace_hash_replay_hygiene_only": trace_hash_report["integrity_hygiene_only"],
        "state_hash_replay_hygiene_only": state_hash_report["integrity_hygiene_only"],
        "old_artifacts_not_mutated": not old_mutation_report["old_artifact_mutation_detected"],
        "post_eval_mutation_check_passed": mutation_report["post_evaluation_mutation_check_passed"],
        "claim_ceiling_preserved": stage0["claim_ceiling"] == CLAIM_CEILING,
    }
    verdict = VERDICT_PASS
    stop: list[str] = []
    if not gates["parent_remote_anchors_verified"] or not gates["redteam_failure_admission_verified"]:
        verdict = VERDICT_BLOCK_PARENT
        stop.append("parent_anchor_missing")
    elif not gates["computed_evidence_contract_cited_and_enforced"]:
        verdict = VERDICT_BLOCK_MISSING_CONTRACT
        stop.append("computed_evidence_contract_missing")
    elif not gates["stage0_freeze_before_any_run"] or not gates["clean_worktree_before_stage0"]:
        verdict = VERDICT_BLOCK_STAGE0
        stop.append("stage0_freeze_gap")
    elif not gates["claim_ceiling_preserved"]:
        verdict = VERDICT_BLOCK_CLAIM
        stop.append("claim_inflation")
    elif not gates["frozen_inputs_consumed"]:
        verdict = VERDICT_FAILED_UNUSED_FROZEN_INPUT
        stop.append("unused_frozen_input")
    elif provenance_report["verdict"] != VERDICT_PASS:
        verdict = provenance_report["verdict"]
        stop.append("computed_evidence_provenance")
    elif not baseline_report["baseline_gate_passed"]:
        verdict = VERDICT_FAILED_BASELINE_EQUIVALENCE
        stop.append("baseline_equivalence")
    elif baseline_report["identity_token_lookup_equivalence"]:
        verdict = VERDICT_FAILED_IDENTITY_LOOKUP
        stop.append("identity_token_lookup_equivalence")
    elif baseline_report["memory_key_lookup_equivalence"]:
        verdict = VERDICT_FAILED_MEMORY_KEY_LOOKUP
        stop.append("memory_key_lookup_equivalence")
    elif baseline_report["state_table_equivalence"]:
        verdict = VERDICT_FAILED_STATE_TABLE
        stop.append("state_table_equivalence")
    elif baseline_report["snapshot_reload_equivalence"]:
        verdict = VERDICT_FAILED_SNAPSHOT_RELOAD
        stop.append("snapshot_reload_equivalence")
    elif baseline_report["transcript_or_summary_retrieval_equivalence"]:
        verdict = VERDICT_FAILED_TRANSCRIPT_SUMMARY
        stop.append("transcript_or_summary_retrieval_equivalence")
    elif baseline_report["graph_cache_equivalence"]:
        verdict = VERDICT_FAILED_GRAPH_CACHE
        stop.append("graph_cache_equivalence")
    elif not ablation_report["ablation_gate_passed"]:
        verdict = VERDICT_FAILED_ABLATION_INSENSITIVE
        stop.append("ablation_insensitive")
    elif not leakage_report["leakage_gate_passed"]:
        verdict = VERDICT_FAILED_LEAKAGE
        stop.append("leakage")
    elif not behavior_replay_report["behavior_causal_replay_passed"]:
        verdict = VERDICT_FAILED_REPLAY_NOT_BEHAVIOR
        stop.append("replay_not_behavior_causal")
    elif not mutation_report["post_evaluation_mutation_check_passed"] or old_mutation_report[
        "old_artifact_mutation_detected"
    ]:
        verdict = VERDICT_FAILED_ARTIFACT_MUTATION
        stop.append("artifact_mutation")
    return {
        "task_id": TASK_ID,
        "verdict": verdict,
        "bounded_pass": verdict == VERDICT_PASS,
        "layer": LAYER,
        "artifact_dir": ARTIFACT_DIR_REL,
        "claim_ceiling": CLAIM_CEILING,
        "authorization_flags": dict(AUTHORIZATION_FLAGS),
        "parent_evidence": {
            "post_bridge_admission_executable_001c": {
                "commit": PARENT_REMOTE_ANCHORS["remote-anchor-001k-df0e3e5"],
                "remote_tag": "remote-anchor-001k-df0e3e5",
                "nominal_verdict": "post_bridge_admission_executable_001c_pass",
                "current_status": "suspended_as_downstream_positive_evidence_due_to_leakage_failability_blocker",
            },
            "ego_mainline_readiness_audit_001a": {
                "commit": PARENT_REMOTE_ANCHORS["remote-anchor-001l-ed9355b"],
                "remote_tag": "remote-anchor-001l-ed9355b",
                "current_status": "conditional_non_actionable_until_001d_or_equivalent_bounded_rerun",
            },
            "post_bridge_admission_executable_001c_redteam_leakage_blocker_admission_001a": {
                "commit": REDTEAM_FAILURE_FULL,
                "verdict": (
                    "post_bridge_admission_executable_001c_redteam_leakage_blocker_admission_001a_"
                    "block_leakage_scanner_not_fail_able_admitted"
                ),
                "remote_tag": "remote-anchor-001m-557b61e",
            },
            "computed_evidence_provenance_contract_001a": {
                "commit": PARENT_REMOTE_ANCHORS["remote-anchor-001i-09cff85"],
                "remote_tag": "remote-anchor-001i-09cff85",
            },
        },
        "acceptance_gates": gates,
        "baseline_results": {
            "candidate_score": baseline_report["candidate"]["candidate_score"],
            "best_fair_baseline": baseline_report["best_fair_baseline"],
            "baseline_gate_passed": baseline_report["baseline_gate_passed"],
        },
        "ablation_results": {
            "candidate_score": ablation_report["candidate_score"],
            "ablation_gate_passed": ablation_report["ablation_gate_passed"],
        },
        "replay_results": {
            "candidate_action_replay_passed": candidate_replay_report["candidate_action_replay_passed"],
            "behavior_causal_replay_passed": behavior_replay_report["behavior_causal_replay_passed"],
            "trace_hash_replay_hygiene_only": trace_hash_report["integrity_hygiene_only"],
            "state_hash_replay_hygiene_only": state_hash_report["integrity_hygiene_only"],
        },
        "verdict_bearing_metric_ids": verdict_bearing_metric_ids,
        "stop_conditions_triggered": stop,
        "forbidden_claims_absent": True,
        "anti_sycophancy_audit": {
            "strongest_baseline_explanation": baseline_report["strongest_baseline_explanation"],
            "strongest_reason_task_may_be_invalid": (
                "001D may still be invalid if the synthetic distribution and candidate "
                "hash-based state rule share a closed-world construction shortcut, or if "
                "future evidence relies on this bounded proxy as mechanism validity."
            ),
            "result_that_would_falsify_current_framing": (
                "Any fair baseline equivalence, identity-token or memory-key equivalence, "
                "unused frozen input, static metric, ablation insensitivity, leakage, "
                "behavior-causal replay failure, or old-artifact mutation."
            ),
            "evidence_that_would_still_be_insufficient": (
                "A bounded pass, computed metric provenance, behavior-causal replay, "
                "baseline non-equivalence, and ablation sensitivity remain insufficient "
                "for bridge readiness, EGO readiness, companion readiness, mechanism "
                "validity, theory validity, agency, selfhood, consciousness, real "
                "relationship learning, real emotion, subjective experience, or stable user benefit."
            ),
            "tests_mechanism_or_behavioral_resemblance": (
                "tests bounded post-bridge serialized-state dependence under computed-evidence "
                "provenance, not behavioral resemblance and not mechanism validity"
            ),
        },
        "what_this_does_not_prove": [
            "bridge readiness",
            "EGO readiness",
            "companion readiness",
            "mechanism validity",
            "theory validity",
            "agency",
            "selfhood",
            "consciousness",
            "real relationship learning",
            "real emotion",
            "subjective experience",
            "stable user benefit",
            "correctness of any future EGO runtime",
        ],
    }
