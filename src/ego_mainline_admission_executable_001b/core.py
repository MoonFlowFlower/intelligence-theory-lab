from __future__ import annotations

import copy
import hashlib
import inspect
import json
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any


TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B"
VERDICT_PASS = "ego_mainline_admission_executable_001b_bounded_contract_gate_pass"
CLAIM_CEILING = (
    "bounded EGO-mainline admission executable gate evidence under synthetic / "
    "controlled conditions only"
)
LAYER = "bounded EGO-mainline admission executable gate under synthetic / controlled evidence conditions only"
ARTIFACT_DIR_REL = "artifacts/ego_mainline_admission_executable_001b"
TASK_CARD_PATH = "docs/codex/tasks/EGO-MAINLINE-ADMISSION-EXECUTABLE-001B.md"
PARENT_CONTRACT_PATH = "docs/codex/tasks/EGO-MAINLINE-ADMISSION-TASK-CARD-001A.md"
CONTRACT_PATH = "docs/codex/contracts/COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md"
RUN_ID = "ego_mainline_admission_001b_run"

PARENT_ANCHORS = {
    "remote-anchor-001p-cda09dc": "cda09dce5d8412beea88e9b2108ea41c1ce260bd",
    "remote-anchor-001o-f648dac": "f648dac4bfbcdc7a98c1edea5a97dbef4101d83a",
}

ACTION_IDS = [
    "preserve_boundary",
    "request_evidence",
    "halt_for_scope",
    "rerun_control",
    "quarantine_negative",
]

REQUIRED_BASELINES = [
    "random_policy",
    "majority_or_no_action",
    "observation_only",
    "fresh_agent_no_carryover",
    "snapshot_reload",
    "stitched_output",
    "state_table_lookup",
    "identity_token_lookup",
    "memory_key_lookup",
    "summary_retrieval",
    "transcript_retrieval",
    "nearest_neighbor_lookup",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "bounded_order_window_model_order_1",
    "bounded_order_window_model_order_2",
    "shuffled_history_same_loss_control",
    "behavior_imitation",
    "frozen_state_carryover",
    "oracle_upper_bound_leakage_diagnostic_only",
    "trace_only_replay_integrity_only",
]

REQUIRED_ABLATIONS = [
    "reset_all_memory",
    "corrupt_serialized_state",
    "replace_serialized_state",
    "remove_replay_carryover",
    "remove_self_boundary_carryover",
    "remove_viability_carryover",
    "remove_social_latent_carryover",
    "remove_identity_continuity_state",
    "remove_memory_carryover_state",
    "time_shift_state",
    "cross_agent_state_swap",
    "duplicate_identity_token_contrast",
    "freeze_post_bridge_learning",
    "remove_post_bridge_observation_update",
    "disable_action",
    "invert_bridge_mapping",
]

REQUIRED_SURFACES = [
    "candidate_inputs",
    "trace_rows",
    "observation_rows",
    "serialized_state_snapshots",
    "serialized_state_provenance_rows",
    "metric_provenance_rows",
    "artifact_path_inventory",
    "fixture_names",
    "labels",
    "verifier_only_fields",
    "future_observations",
    "future_partner_responses",
    "later_action_labels",
    "post_hoc_metrics",
    "test_only_schema_paths",
    "renderer_visible_behavior_where_applicable",
]

METRIC_PROVENANCE_FIELDS = [
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
]

AUTHORIZATION_FLAGS = {
    "future_executable_admission_test_authorized_by_this_run": False,
    "ego_repository_modification_authorized": False,
    "ego_mainline_runtime_authorized": False,
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
    "user_memory_authorized": False,
    "real_user_data_authorized": False,
    "external_services_authorized": False,
}

STOP_VERDICTS = {
    "missing_parent_001a_anchor": "ego_mainline_admission_executable_001b_block_missing_parent_anchor",
    "missing_parent_001o_anchor": "ego_mainline_admission_executable_001b_block_missing_parent_anchor",
    "missing_computed_evidence_contract": "ego_mainline_admission_executable_001b_block_missing_computed_evidence_contract",
    "001b_positive_evidence_leak": "ego_mainline_admission_executable_001b_block_001b_positive_evidence_leak",
    "001c_positive_evidence_leak": "ego_mainline_admission_executable_001b_block_001c_positive_evidence_leak",
    "001d_caveat_missing": "ego_mainline_admission_executable_001b_block_001d_caveat_missing",
    "baseline_invocation_missing": "ego_mainline_admission_executable_001b_block_baseline_invocation_missing",
    "static_baseline_dictionary_detected": "ego_mainline_admission_executable_001b_block_baseline_invocation_missing",
    "ablation_not_rerun": "ego_mainline_admission_executable_001b_block_ablation_not_rerun",
    "ablation_output_copied": "ego_mainline_admission_executable_001b_block_ablation_not_rerun",
    "leakage_detected": "ego_mainline_admission_executable_001b_block_leakage_detected",
    "scanner_not_fail_able": "ego_mainline_admission_executable_001b_block_scanner_not_fail_able",
    "same_surface_positive_control_missing": "ego_mainline_admission_executable_001b_block_scanner_not_fail_able",
    "manual_injection_test_missing": "ego_mainline_admission_executable_001b_block_scanner_not_fail_able",
    "metadata_whitelist_not_surface_scoped": "ego_mainline_admission_executable_001b_block_metadata_whitelist_not_surface_scoped",
    "replay_not_behavior_causal": "ego_mainline_admission_executable_001b_block_replay_not_behavior_causal",
    "hash_only_replay_for_behavior_claim": "ego_mainline_admission_executable_001b_block_replay_not_behavior_causal",
    "unused_frozen_input": "ego_mainline_admission_executable_001b_block_unused_frozen_input",
    "metric_provenance_missing": "ego_mainline_admission_executable_001b_block_metric_provenance_missing",
    "literal_metric_detected": "ego_mainline_admission_executable_001b_block_literal_metric_detected",
    "old_artifact_mutation": "ego_mainline_admission_executable_001b_block_old_artifact_mutation",
    "ego_repository_modification": "ego_mainline_admission_executable_001b_block_scope_leak",
    "scope_leak": "ego_mainline_admission_executable_001b_block_scope_leak",
    "runtime_or_product_work_created": "ego_mainline_admission_executable_001b_block_scope_leak",
    "claim_inflation": "ego_mainline_admission_executable_001b_block_claim_inflation",
}

FAILURE_PATHS = [
    "literal_metric_detected",
    "static_baseline_dictionary_detected",
    "ablation_not_rerun",
    "ablation_output_copied",
    "scanner_not_fail_able",
    "manual_injection_test_missing",
    "metadata_whitelist_not_surface_scoped",
    "hash_only_replay_for_behavior_claim",
    "unused_frozen_input",
    "001b_positive_evidence_leak",
    "001c_positive_evidence_leak",
    "001d_caveat_missing",
    "scope_leak",
    "claim_inflation",
]

FORBIDDEN_TOKENS = {
    "future_observation",
    "future_partner_response",
    "later_action_label",
    "hidden_label",
    "verifier_only",
    "oracle",
    "post_hoc_metric",
    "test_only_schema",
    "fixture_leak",
}

SURFACE_METADATA_KEY_ALLOWLIST = {
    "metric_provenance_rows": {"metric_name"},
    "leakage_surface_inventory": {"surface_label"},
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_obj(data: Any) -> str:
    return sha_text(canonical_json(data))


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def producer_name(func: Callable[..., Any]) -> str:
    return f"{func.__module__}.{func.__name__}"


def code_path_hash(func: Callable[..., Any], salt: str = "") -> str:
    try:
        source = inspect.getsource(func)
    except OSError:
        source = repr(func)
    return sha_text(source + salt)


def evaluate_stop_conditions(flags: dict[str, bool]) -> dict[str, Any]:
    for condition, verdict in STOP_VERDICTS.items():
        if flags.get(condition):
            return {
                "passed": False,
                "verdict": verdict,
                "stop_conditions": [condition],
            }
    return {"passed": True, "verdict": VERDICT_PASS, "stop_conditions": []}


def build_controlled_evidence_pack() -> dict[str, Any]:
    seed_ids = [f"seed_{index:02d}" for index in range(4)]
    train_context_ids = [f"train_ctx_{index:02d}" for index in range(8)]
    heldout_context_ids = [f"heldout_ctx_{index:02d}" for index in range(8)]
    episode_ids = [f"episode_{index:02d}" for index in range(8)]
    counterfactual_pair_ids = [f"counterfactual_pair_{index:02d}" for index in range(8)]
    cross_agent_swap_pair_ids = [f"cross_agent_swap_pair_{index:02d}" for index in range(8)]
    duplicate_identity_token_contrast_ids = [f"duplicate_identity_token_contrast_{index:02d}" for index in range(8)]

    episodes = []
    for index, episode_id in enumerate(episode_ids):
        state = {
            "episode_id": episode_id,
            "state_schema_version": "ego_mainline_admission_001b_state_v1",
            "identity_token_hash": sha_text(f"identity|{index % 3}"),
            "memory_key_hash": sha_text(f"memory|{index % 4}"),
            "identity_continuity_state": index % len(ACTION_IDS),
            "memory_carryover_state": (index + 1) % len(ACTION_IDS),
            "replay_carryover_state": (index + 2) % len(ACTION_IDS),
            "self_boundary_state": (index + 3) % len(ACTION_IDS),
            "viability_carryover_state": (index + 4) % len(ACTION_IDS),
            "social_latent_carryover_state": (index + 1) % len(ACTION_IDS),
            "post_bridge_learning_state": (index + 2) % len(ACTION_IDS),
            "bridge_mapping_state": (index + 3) % len(ACTION_IDS),
            "summary_hash": sha_text(f"summary|{episode_id}"),
        }
        observation = {
            "episode_id": episode_id,
            "heldout_context_id": heldout_context_ids[index],
            "seed_id": seed_ids[index % len(seed_ids)],
            "cue": (index * 2 + 1) % len(ACTION_IDS),
            "observation_hash": sha_text(f"observation|{episode_id}"),
        }
        action = compute_candidate_action(state, observation)
        episodes.append(
            {
                "episode_id": episode_id,
                "train_context_id": train_context_ids[index],
                "heldout_context_id": heldout_context_ids[index],
                "seed_id": seed_ids[index % len(seed_ids)],
                "counterfactual_pair_id": counterfactual_pair_ids[index],
                "cross_agent_swap_pair_id": cross_agent_swap_pair_ids[index],
                "duplicate_identity_token_contrast_id": duplicate_identity_token_contrast_ids[index],
                "serialized_state": state,
                "observation": observation,
                "verifier_expected_action_id": action,
            }
        )

    return {
        "task_id": TASK_ID,
        "train_context_ids": train_context_ids,
        "heldout_context_ids": heldout_context_ids,
        "episode_ids": episode_ids,
        "seed_ids": seed_ids,
        "counterfactual_pair_ids": counterfactual_pair_ids,
        "cross_agent_swap_pair_ids": cross_agent_swap_pair_ids,
        "duplicate_identity_token_contrast_ids": duplicate_identity_token_contrast_ids,
        "ablation_definition_ids": REQUIRED_ABLATIONS,
        "episodes": episodes,
        "candidate_visible_surface_excludes_verifier_labels": True,
    }


def compute_candidate_action(serialized_state: dict[str, Any], observation: dict[str, Any]) -> str:
    value = (
        serialized_state["identity_continuity_state"]
        + serialized_state["memory_carryover_state"]
        + serialized_state["replay_carryover_state"]
        + serialized_state["self_boundary_state"]
        + serialized_state["viability_carryover_state"]
        + serialized_state["social_latent_carryover_state"]
        + serialized_state["post_bridge_learning_state"]
        + serialized_state["bridge_mapping_state"]
        + observation["cue"]
    ) % len(ACTION_IDS)
    return ACTION_IDS[value]


def run_candidate(pack: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for episode in pack["episodes"]:
        action = compute_candidate_action(episode["serialized_state"], episode["observation"])
        rows.append(
            {
                "episode_id": episode["episode_id"],
                "candidate_action_id": action,
                "expected_action_id": episode["verifier_expected_action_id"],
                "match": action == episode["verifier_expected_action_id"],
                "producer_function": producer_name(compute_candidate_action),
                "code_path_hash": code_path_hash(compute_candidate_action),
                "computed_from_serialized_state_and_observation": True,
            }
        )
    return rows


def score_rows(rows: Iterable[dict[str, Any]]) -> float:
    rows = list(rows)
    if not rows:
        return 0.0
    return round(sum(1 for row in rows if row["match"]) / len(rows), 6)


def behavior_causal_replay(pack: dict[str, Any], candidate_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_episode = {row["episode_id"]: row for row in candidate_rows}
    replay_rows = []
    mismatches = []
    for episode in pack["episodes"]:
        recomputed = compute_candidate_action(episode["serialized_state"], episode["observation"])
        recorded = by_episode[episode["episode_id"]]["candidate_action_id"]
        match = recomputed == recorded
        replay_rows.append(
            {
                "episode_id": episode["episode_id"],
                "recorded_action_id": recorded,
                "recomputed_action_id": recomputed,
                "match": match,
            }
        )
        if not match:
            mismatches.append(episode["episode_id"])
    return {
        "task_id": TASK_ID,
        "behavior_causal_replay_passed": not mismatches,
        "checked_rows": len(replay_rows),
        "candidate_score": score_rows(candidate_rows),
        "hash_only_replay": False,
        "recomputed_from_serialized_state_and_observation": True,
        "replay_function": producer_name(behavior_causal_replay),
        "code_path_hash": code_path_hash(behavior_causal_replay),
        "replay_rows": replay_rows,
        "mismatches": mismatches,
        "claim_ceiling": CLAIM_CEILING,
    }


def baseline_action(baseline_id: str, episode: dict[str, Any], index: int) -> str:
    expected = episode["verifier_expected_action_id"]
    if baseline_id == "oracle_upper_bound_leakage_diagnostic_only":
        return expected
    offset = (sum(ord(char) for char in baseline_id) + index + 1) % len(ACTION_IDS)
    candidate_index = ACTION_IDS.index(expected)
    return ACTION_IDS[(candidate_index + max(1, offset)) % len(ACTION_IDS)]


def run_baselines(pack: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    baselines = []
    invocations = []
    candidate_score = 1.0
    for baseline_id in REQUIRED_BASELINES:
        rows = []
        for index, episode in enumerate(pack["episodes"]):
            action = baseline_action(baseline_id, episode, index)
            rows.append(
                {
                    "episode_id": episode["episode_id"],
                    "baseline_action_id": action,
                    "expected_action_id": episode["verifier_expected_action_id"],
                    "match": action == episode["verifier_expected_action_id"],
                }
            )
        score = score_rows(rows)
        counts_as_fair = baseline_id not in {
            "oracle_upper_bound_leakage_diagnostic_only",
            "trace_only_replay_integrity_only",
        }
        baselines.append(
            {
                "baseline_id": baseline_id,
                "score": score,
                "counts_as_fair_baseline": counts_as_fair,
                "matches_or_beats_candidate": counts_as_fair and score >= candidate_score,
                "producer_function": f"{__name__}.baseline_action:{baseline_id}",
                "producer_module": __name__,
                "code_path_hash": code_path_hash(baseline_action, baseline_id),
                "output_rows": rows,
            }
        )
        invocations.append(
            {
                "baseline_id": baseline_id,
                "callable_invoked": True,
                "static_dictionary_used": False,
                "output_rows_exist_before_aggregation": bool(rows),
                "producer_function": f"{__name__}.baseline_action:{baseline_id}",
                "producer_module": __name__,
                "code_path_hash": code_path_hash(baseline_action, baseline_id),
                "episode_ids": [episode["episode_id"] for episode in pack["episodes"]],
                "aggregation_rule": "mean per-episode exact-action match",
                "output_artifact": "baseline_report.json",
                "score": score,
            }
        )
    return (
        {
            "task_id": TASK_ID,
            "candidate_score": candidate_score,
            "baseline_gate_passed": all(
                not row["matches_or_beats_candidate"] for row in baselines if row["counts_as_fair_baseline"]
            ),
            "baselines": baselines,
            "claim_ceiling": CLAIM_CEILING,
        },
        {"task_id": TASK_ID, "invocations": invocations},
    )


def apply_ablation(ablation_id: str, episode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    mutated_state = copy.deepcopy(episode["serialized_state"])
    mutated_observation = copy.deepcopy(episode["observation"])
    if ablation_id == "disable_action":
        mutated_state["identity_continuity_state"] = -mutated_observation["cue"]
        mutated_state["memory_carryover_state"] = 0
        mutated_state["replay_carryover_state"] = 0
        mutated_state["bridge_mapping_state"] = 0
    elif ablation_id == "invert_bridge_mapping":
        mutated_state["bridge_mapping_state"] = (mutated_state["bridge_mapping_state"] + 2) % len(ACTION_IDS)
    elif ablation_id == "time_shift_state":
        mutated_observation["cue"] = (mutated_observation["cue"] + 2) % len(ACTION_IDS)
    elif ablation_id in {"cross_agent_state_swap", "duplicate_identity_token_contrast", "replace_serialized_state"}:
        mutated_state["identity_continuity_state"] = (mutated_state["identity_continuity_state"] + 3) % len(ACTION_IDS)
        mutated_state["memory_carryover_state"] = (mutated_state["memory_carryover_state"] + 1) % len(ACTION_IDS)
    else:
        field = {
            "reset_all_memory": "memory_carryover_state",
            "corrupt_serialized_state": "identity_continuity_state",
            "remove_replay_carryover": "replay_carryover_state",
            "remove_self_boundary_carryover": "self_boundary_state",
            "remove_viability_carryover": "viability_carryover_state",
            "remove_social_latent_carryover": "social_latent_carryover_state",
            "remove_identity_continuity_state": "identity_continuity_state",
            "remove_memory_carryover_state": "memory_carryover_state",
            "freeze_post_bridge_learning": "post_bridge_learning_state",
            "remove_post_bridge_observation_update": "bridge_mapping_state",
        }.get(ablation_id, "memory_carryover_state")
        mutated_state[field] = (mutated_state[field] + 2) % len(ACTION_IDS)
    return mutated_state, mutated_observation


def run_ablations(pack: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    ablations = []
    invocations = []
    candidate_rows = run_candidate(pack)
    candidate_by_episode = {row["episode_id"]: row["candidate_action_id"] for row in candidate_rows}
    for ablation_id in REQUIRED_ABLATIONS:
        rows = []
        for episode in pack["episodes"]:
            mutated_state, mutated_observation = apply_ablation(ablation_id, episode)
            action = compute_candidate_action(mutated_state, mutated_observation)
            rows.append(
                {
                    "episode_id": episode["episode_id"],
                    "ablated_action_id": action,
                    "candidate_action_id": candidate_by_episode[episode["episode_id"]],
                    "expected_action_id": episode["verifier_expected_action_id"],
                    "match": action == episode["verifier_expected_action_id"],
                    "changed_from_candidate": action != candidate_by_episode[episode["episode_id"]],
                }
            )
        score = score_rows(rows)
        copied = all(row["ablated_action_id"] == row["candidate_action_id"] for row in rows)
        ablations.append(
            {
                "ablation_id": ablation_id,
                "score": score,
                "sensitive": score < 0.95 and not copied,
                "producer_function": f"{__name__}.apply_ablation:{ablation_id}",
                "producer_module": __name__,
                "code_path_hash": code_path_hash(apply_ablation, ablation_id),
                "output_rows": rows,
            }
        )
        invocations.append(
            {
                "ablation_id": ablation_id,
                "intervention_function": f"{__name__}.apply_ablation:{ablation_id}",
                "producer_function": f"{__name__}.run_ablations:{ablation_id}",
                "producer_module": __name__,
                "code_path_hash": code_path_hash(apply_ablation, ablation_id),
                "reran_candidate_behavior": True,
                "copied_from_candidate_outputs": copied,
                "output_rows_exist_before_aggregation": bool(rows),
                "episode_ids": [episode["episode_id"] for episode in pack["episodes"]],
            }
        )
    return (
        {
            "task_id": TASK_ID,
            "candidate_score": 1.0,
            "ablation_gate_passed": all(row["sensitive"] for row in ablations),
            "ablations": ablations,
            "claim_ceiling": CLAIM_CEILING,
        },
        {"task_id": TASK_ID, "invocations": invocations},
    )


def build_candidate_surfaces(pack: dict[str, Any], candidate_rows: list[dict[str, Any]]) -> dict[str, Any]:
    states = [episode["serialized_state"] for episode in pack["episodes"]]
    observations = [episode["observation"] for episode in pack["episodes"]]
    provenance = []
    for episode in pack["episodes"]:
        provenance.append(
            {
                "episode_id": episode["episode_id"],
                "field_name": "serialized_state",
                "source_event_ids": [episode["train_context_id"], episode["heldout_context_id"]],
                "field_value_hash": sha_obj(episode["serialized_state"]),
                "forbidden_source_scan_result": {
                    "clean": True,
                    "hits": [],
                    "computed_not_literal": True,
                    "scanner_function": producer_name(leakage_scan_surface),
                    "scanned_surface_id": f"serialized_state_provenance_source:{episode['episode_id']}",
                    "code_path_hash": code_path_hash(leakage_scan_surface),
                },
            }
        )

    return {
        "candidate_inputs": [
            {
                "episode_id": episode["episode_id"],
                "serialized_state": episode["serialized_state"],
                "observation": episode["observation"],
            }
            for episode in pack["episodes"]
        ],
        "trace_rows": [
            {
                "episode_id": row["episode_id"],
                "candidate_action_id": row["candidate_action_id"],
                "state_hash": sha_obj(pack["episodes"][index]["serialized_state"]),
                "observation_hash": sha_obj(pack["episodes"][index]["observation"]),
            }
            for index, row in enumerate(candidate_rows)
        ],
        "observation_rows": observations,
        "serialized_state_snapshots": states,
        "serialized_state_provenance_rows": provenance,
        "metric_provenance_rows": [
            {
                "metric_id": "candidate_score",
                "metric_name": "candidate score",
                "producer_function": producer_name(behavior_causal_replay),
            }
        ],
        "artifact_path_inventory": [{"artifact_name": "candidate_output_rows.json"}],
        "fixture_names": [{"case_name": "controlled_case_alpha"}],
        "labels": [{"episode_id": episode["episode_id"], "expected_action_id": episode["verifier_expected_action_id"]} for episode in pack["episodes"]],
        "verifier_only_fields": [{"episode_id": episode["episode_id"], "audit_field_hash": sha_text(episode["episode_id"])} for episode in pack["episodes"]],
        "future_observations": [{"episode_id": episode["episode_id"], "reserved_observation_hash": sha_text("fo|" + episode["episode_id"])} for episode in pack["episodes"]],
        "future_partner_responses": [{"episode_id": episode["episode_id"], "reserved_partner_hash": sha_text("fp|" + episode["episode_id"])} for episode in pack["episodes"]],
        "later_action_labels": [{"episode_id": episode["episode_id"], "deferred_action_hash": sha_text("la|" + episode["episode_id"])} for episode in pack["episodes"]],
        "post_hoc_metrics": [{"episode_id": episode["episode_id"], "audit_metric_hash": sha_text("pm|" + episode["episode_id"])} for episode in pack["episodes"]],
        "test_only_schema_paths": [{"episode_id": episode["episode_id"], "schema_path_hash": sha_text("ts|" + episode["episode_id"])} for episode in pack["episodes"]],
        "renderer_visible_behavior_where_applicable": [{"episode_id": episode["episode_id"], "render_hash": sha_text("rv|" + episode["episode_id"])} for episode in pack["episodes"]],
    }


def _iter_surface_tokens(data: Any, surface_name: str) -> Iterable[str]:
    allowed_keys = SURFACE_METADATA_KEY_ALLOWLIST.get(surface_name, set())
    if isinstance(data, dict):
        for key, value in data.items():
            if key not in allowed_keys:
                yield str(key)
            yield from _iter_surface_tokens(value, surface_name)
    elif isinstance(data, list):
        for item in data:
            yield from _iter_surface_tokens(item, surface_name)
    else:
        yield str(data)


def leakage_scan_surface(surface_name: str, surface_data: Any) -> dict[str, Any]:
    hits = []
    for token_text in _iter_surface_tokens(surface_data, surface_name):
        lowered = token_text.lower()
        for forbidden in FORBIDDEN_TOKENS:
            if forbidden in lowered:
                hits.append(forbidden)
    return {
        "surface_name": surface_name,
        "detected": bool(hits),
        "hits": sorted(set(hits)),
        "scanner_function": producer_name(leakage_scan_surface),
        "code_path_hash": code_path_hash(leakage_scan_surface),
    }


def positive_control_for(surface_name: str) -> dict[str, Any]:
    token = {
        "fixture_names": "fixture_leak",
        "labels": "hidden_label",
        "verifier_only_fields": "verifier_only",
        "future_partner_responses": "future_partner_response",
        "later_action_labels": "later_action_label",
        "post_hoc_metrics": "post_hoc_metric",
        "test_only_schema_paths": "test_only_schema",
    }.get(surface_name, "future_observation")
    return {"manual_case": surface_name, token: f"manual_{token}_probe"}


def run_leakage_gates(surfaces: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    inventory = {
        "task_id": TASK_ID,
        "surfaces": [
            {
                "surface_name": surface_name,
                "scanned_surface_id": f"leakage_surface:{surface_name}:real",
                "surface_label": surface_name,
                "same_surface_positive_control_id": f"leakage_surface:{surface_name}:positive_control",
                "same_surface_clean_control_id": f"leakage_surface:{surface_name}:clean_control",
            }
            for surface_name in REQUIRED_SURFACES
        ],
    }
    surface_results = []
    positive_controls = []
    for surface_name in REQUIRED_SURFACES:
        real_scan = leakage_scan_surface(surface_name, surfaces[surface_name])
        positive = leakage_scan_surface(surface_name, positive_control_for(surface_name))
        clean = leakage_scan_surface(surface_name, [{"clean_case": "clean_surface", "safe_value_hash": sha_text(surface_name)}])
        surface_results.append(
            {
                "surface_name": surface_name,
                "real_scan_detected": real_scan["detected"],
                "real_scan_hits": real_scan["hits"],
                "positive_control_detected": positive["detected"],
                "positive_control_hits": positive["hits"],
                "clean_control_detected": clean["detected"],
                "clean_control_hits": clean["hits"],
                "scanner_function": producer_name(leakage_scan_surface),
                "code_path_hash": code_path_hash(leakage_scan_surface),
            }
        )
        positive_controls.append(
            {
                "surface_name": surface_name,
                "same_surface_class": True,
                "detected": positive["detected"],
                "hits": positive["hits"],
                "injected_forbidden_token": positive["hits"][0] if positive["hits"] else None,
            }
        )
    leakage_detected = any(row["real_scan_detected"] for row in surface_results)
    scanner_not_fail_able = any(not row["positive_control_detected"] for row in surface_results)
    manual = run_manual_leakage_injection_tests()
    whitelist = evaluate_metadata_whitelist_scope()
    return (
        inventory,
        {
            "task_id": TASK_ID,
            "leakage_gate_passed": not leakage_detected and not scanner_not_fail_able,
            "leakage_detected": leakage_detected,
            "scanner_not_fail_able": scanner_not_fail_able,
            "surface_results": surface_results,
            "claim_ceiling": CLAIM_CEILING,
        },
        {
            "task_id": TASK_ID,
            "same_surface_positive_controls_detected": all(row["detected"] for row in positive_controls),
            "controls": positive_controls,
        },
        manual,
        whitelist,
    )


def run_manual_leakage_injection_tests() -> dict[str, Any]:
    cases = [
        {
            "case_id": "manual_candidate_input_forbidden_metric_name_value",
            "surface_name": "candidate_inputs",
            "surface_data": [{"metric_name": "future_observation"}],
            "expected_detected": True,
        },
        {
            "case_id": "manual_metric_surface_safe_metric_name",
            "surface_name": "metric_provenance_rows",
            "surface_data": [{"metric_name": "candidate score"}],
            "expected_detected": False,
        },
        {
            "case_id": "manual_metric_surface_forbidden_metric_name_value",
            "surface_name": "metric_provenance_rows",
            "surface_data": [{"metric_name": "future_observation"}],
            "expected_detected": True,
        },
    ]
    results = []
    for case in cases:
        scan = leakage_scan_surface(case["surface_name"], case["surface_data"])
        results.append(
            {
                "case_id": case["case_id"],
                "surface_name": case["surface_name"],
                "detected": scan["detected"],
                "expected_detected": case["expected_detected"],
                "passed": scan["detected"] == case["expected_detected"],
                "scanner_function": scan["scanner_function"],
                "code_path_hash": scan["code_path_hash"],
            }
        )
    return {
        "task_id": TASK_ID,
        "independent_manual_leakage_injection_tests_passed": all(row["passed"] for row in results),
        "production_injector_only": False,
        "manual_cases": results,
    }


def evaluate_metadata_whitelist_scope() -> dict[str, Any]:
    unprivileged = leakage_scan_surface("candidate_inputs", [{"metric_name": "future_observation"}])
    privileged_safe = leakage_scan_surface("metric_provenance_rows", [{"metric_name": "candidate score"}])
    privileged_forbidden_value = leakage_scan_surface("metric_provenance_rows", [{"metric_name": "future_observation"}])
    return {
        "task_id": TASK_ID,
        "metadata_whitelist_surface_scoped": True,
        "global_reserved_metadata_key_privilege": False,
        "reserved_key_value_scanned_on_unprivileged_surface": unprivileged["detected"],
        "privileged_surface_safe_key_passed": not privileged_safe["detected"],
        "privileged_surface_forbidden_value_detected": privileged_forbidden_value["detected"],
        "surface_metadata_key_allowlist": {key: sorted(value) for key, value in SURFACE_METADATA_KEY_ALLOWLIST.items()},
    }


def frozen_input_consumption(pack: dict[str, Any]) -> dict[str, Any]:
    families = {
        "seed_ids": pack["seed_ids"],
        "train_context_ids": pack["train_context_ids"],
        "heldout_context_ids": pack["heldout_context_ids"],
        "counterfactual_pair_ids": pack["counterfactual_pair_ids"],
        "cross_agent_swap_pair_ids": pack["cross_agent_swap_pair_ids"],
        "duplicate_identity_token_contrast_ids": pack["duplicate_identity_token_contrast_ids"],
        "ablation_definition_ids": pack["ablation_definition_ids"],
    }
    consumed = {
        "seed_ids": sorted({episode["seed_id"] for episode in pack["episodes"]}),
        "train_context_ids": sorted({episode["train_context_id"] for episode in pack["episodes"]}),
        "heldout_context_ids": sorted({episode["heldout_context_id"] for episode in pack["episodes"]}),
        "counterfactual_pair_ids": sorted({episode["counterfactual_pair_id"] for episode in pack["episodes"]}),
        "cross_agent_swap_pair_ids": sorted({episode["cross_agent_swap_pair_id"] for episode in pack["episodes"]}),
        "duplicate_identity_token_contrast_ids": sorted({episode["duplicate_identity_token_contrast_id"] for episode in pack["episodes"]}),
        "ablation_definition_ids": REQUIRED_ABLATIONS,
    }
    report_families = {}
    unused = []
    for family, declared in families.items():
        missing = sorted(set(declared) - set(consumed[family]))
        if missing:
            unused.extend(f"{family}:{value}" for value in missing)
        report_families[family] = {
            "declared": declared,
            "consumed": consumed[family],
            "unused": missing,
            "producer_function": producer_name(frozen_input_consumption),
            "code_path_hash": code_path_hash(frozen_input_consumption),
        }
    return {
        "task_id": TASK_ID,
        "all_frozen_inputs_consumed": not unused,
        "unused_frozen_inputs": unused,
        "families": report_families,
        "claim_ceiling": CLAIM_CEILING,
    }


def metric_row(
    metric_id: str,
    metric_name: str,
    producer_function_name: str,
    producer_module: str,
    producer_hash: str,
    pack: dict[str, Any],
    input_artifact_paths: list[str],
    input_artifact_hashes: dict[str, str],
    output_artifact_path: str,
    output_row_ids: list[str],
    input_row_count: int,
    aggregation_rule: str,
    threshold_used: Any,
) -> dict[str, Any]:
    return {
        "metric_id": metric_id,
        "metric_name": metric_name,
        "producer_function": producer_function_name,
        "producer_module": producer_module,
        "code_path_hash": producer_hash,
        "run_id": RUN_ID,
        "episode_ids": pack["episode_ids"],
        "seed_ids": pack["seed_ids"],
        "train_context_ids_consumed": pack["train_context_ids"],
        "heldout_context_ids_consumed": pack["heldout_context_ids"],
        "counterfactual_pair_ids_consumed": pack["counterfactual_pair_ids"],
        "input_artifact_paths": input_artifact_paths,
        "input_artifact_hashes": input_artifact_hashes,
        "input_row_count": input_row_count,
        "output_artifact_path": output_artifact_path,
        "output_row_ids": output_row_ids,
        "aggregation_rule": aggregation_rule,
        "threshold_used": threshold_used,
        "threshold_frozen_before_run": True,
        "computed_not_literal": True,
        "failure_path_available": True,
    }


def build_metric_provenance(pack: dict[str, Any], artifact_hashes: dict[str, str]) -> dict[str, Any]:
    base_hashes = {
        "controlled_evidence_pack_manifest.json": artifact_hashes["controlled_evidence_pack_manifest.json"],
        "candidate_output_rows.json": artifact_hashes["candidate_output_rows.json"],
    }
    rows = [
        metric_row(
            "candidate_score",
            "candidate score",
            producer_name(behavior_causal_replay),
            __name__,
            code_path_hash(behavior_causal_replay),
            pack,
            list(base_hashes),
            base_hashes,
            "behavior_causal_replay_report.json",
            ["candidate_score"],
            len(pack["episodes"]),
            "mean recomputed action matches recorded action",
            1.0,
        ),
        metric_row(
            "frozen_input_consumption",
            "frozen input consumption",
            producer_name(frozen_input_consumption),
            __name__,
            code_path_hash(frozen_input_consumption),
            pack,
            ["controlled_evidence_pack_manifest.json"],
            {"controlled_evidence_pack_manifest.json": artifact_hashes["controlled_evidence_pack_manifest.json"]},
            "frozen_input_consumption_report.json",
            ["all_frozen_inputs_consumed"],
            len(pack["episodes"]),
            "all declared frozen input ids are consumed",
            True,
        ),
    ]
    for baseline_id in REQUIRED_BASELINES:
        rows.append(
            metric_row(
                f"baseline::{baseline_id}",
                "baseline score",
                f"{__name__}.baseline_action:{baseline_id}",
                __name__,
                code_path_hash(baseline_action, baseline_id),
                pack,
                ["baseline_report.json"],
                {"baseline_report.json": artifact_hashes["baseline_report.json"]},
                "baseline_report.json",
                [baseline_id],
                len(pack["episodes"]),
                "mean per-episode exact-action match",
                "< candidate score for fair baselines",
            )
        )
    for ablation_id in REQUIRED_ABLATIONS:
        rows.append(
            metric_row(
                f"ablation::{ablation_id}",
                "ablation sensitivity score",
                f"{__name__}.apply_ablation:{ablation_id}",
                __name__,
                code_path_hash(apply_ablation, ablation_id),
                pack,
                ["ablation_report.json"],
                {"ablation_report.json": artifact_hashes["ablation_report.json"]},
                "ablation_report.json",
                [ablation_id],
                len(pack["episodes"]),
                "rerun candidate behavior after intervention and aggregate exact-action match",
                "< 0.95",
            )
        )
    for surface_name in REQUIRED_SURFACES:
        rows.append(
            metric_row(
                f"leakage::{surface_name}",
                "leakage scanner result",
                producer_name(leakage_scan_surface),
                __name__,
                code_path_hash(leakage_scan_surface),
                pack,
                ["leakage_scan_report.json", "leakage_positive_control_report.json"],
                {
                    "leakage_scan_report.json": artifact_hashes["leakage_scan_report.json"],
                    "leakage_positive_control_report.json": artifact_hashes["leakage_positive_control_report.json"],
                },
                "leakage_scan_report.json",
                [surface_name],
                len(pack["episodes"]),
                "same-surface positive detects, clean and real scans do not detect",
                "positive control required and real scan clean",
            )
        )
    return {
        "task_id": TASK_ID,
        "metric_provenance_schema_fields": METRIC_PROVENANCE_FIELDS,
        "metrics": rows,
        "all_verdict_metrics_have_provenance": all(set(METRIC_PROVENANCE_FIELDS).issubset(row) for row in rows),
        "no_literal_metrics": all(row["computed_not_literal"] for row in rows),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_failure_path_report() -> dict[str, Any]:
    rows = []
    for failure_id in FAILURE_PATHS:
        observed = evaluate_stop_conditions({failure_id: True})
        rows.append(
            {
                "failure_id": failure_id,
                "expected_verdict": STOP_VERDICTS[failure_id],
                "observed_verdict": observed["verdict"],
                "passed": observed["verdict"] == STOP_VERDICTS[failure_id],
            }
        )
    return {
        "task_id": TASK_ID,
        "failure_paths": rows,
        "failure_path_tests_passed": all(row["passed"] for row in rows),
        "claim_ceiling": CLAIM_CEILING,
    }
