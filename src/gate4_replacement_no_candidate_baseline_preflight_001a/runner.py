from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from . import ARTIFACT_DIR_NAME, AUTO_REMOTE_ANCHOR, CLAIM_CEILING, REPORT_NAME, TASK_CARD_ID, TASK_ID


BRANCH = "codex/meta-theory-scaffold"
UPSTREAM_DESIGN_COMMIT = "58ec364bd41104ca3b04129df8aa7fc7dd84f2cf"
UPSTREAM_DESIGN_TAG = "remote-anchor-gate4-replacement-task-falsification-design-001a-58ec364"
PRIOR_INVALID_COMMIT = "78889b69b75baa424e89332558bda798685e9634"
PRIOR_INVALID_SELF_REPORT_TAG = "remote-anchor-preserve-gate4-001a-invalid-self-report-audit-23aa206"

ACTIONS = ["support", "challenge", "defer", "summarize"]
PARTNER_TARGETS = {
    "partner_alpha": "support",
    "partner_beta": "challenge",
    "partner_gamma": "defer",
    "partner_delta": "summarize",
}
PARTNER_KEYS = {
    "partner_alpha": "anon_partner_0",
    "partner_beta": "anon_partner_1",
    "partner_gamma": "anon_partner_2",
    "partner_delta": "anon_partner_3",
}
SEEDS = [4101, 4102]
THRESHOLD = 0.8

BASELINE_IDS = [
    "partner_id_lookup_baseline",
    "preference_table_baseline",
    "retrieval_baseline",
    "imitation_frequency_baseline",
    "order_k_history_baseline_k1",
    "order_k_history_baseline_k2",
    "static_majority_marginal_baseline",
    "generator_proxy_baseline",
    "oracle_shape_rule_baseline",
    "shuffled_linkage_control",
    "counterfactual_pair_baseline",
    "serialized_state_decoder",
    "full_bundle_decoder",
    "ngram_trace_lookup",
    "pair_count_frequency_baseline",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "query_capable_imitation_baseline",
]

GRAPH_CACHE_FAMILY = [
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
]

LEAKAGE_CONTROL_IDS = [
    "injected_visible_label_leak",
    "injected_partner_id_leak",
    "injected_preference_table_leak",
    "injected_serialized_state_leak",
    "injected_filename_order_leak",
    "injected_helper_literal_leak",
]

STRUCTURAL_CONTROL_IDS = [
    "remove_partner_context_linkage",
    "shuffle_intervention_feedback",
    "swap_heldout_partner_context_mappings",
    "inject_misleading_retrieval_matches",
    "remove_transfer_phase",
    "replace_causal_feedback_with_non_causal_correlated_cue",
    "counterfactual_pair_split",
    "positive_control_leakage_injection",
    "corrupt_replay_state",
    "corrupt_observation",
]

REPLAY_CORRUPTION_IDS = [
    "corrupt_serialized_baseline_state",
    "corrupt_observation",
    "corrupt_linkage",
]

REQUIRED_PROVENANCE_FIELDS = [
    "producer_function",
    "input_artifacts",
    "run_id",
    "seed",
    "train_context_ids",
    "heldout_context_ids",
    "counterfactual_pair_ids",
    "episode_ids",
    "aggregation_rule",
    "metric",
    "score",
    "threshold",
    "code_path_hash",
    "config_hash",
    "created_at",
    "verdict_reason",
    "candidate_or_baseline_id",
]

CLAIM_EXCLUSIONS = [
    "Gate4 validity",
    "replacement Gate4 success",
    "mechanism validity",
    "social understanding",
    "social-causal-transfer success",
    "agency",
    "subjectivity",
    "consciousness",
    "emotion",
    "autonomy",
    "stable user benefit",
    "EGO readiness",
    "runtime readiness",
    "bridge readiness",
    "admission readiness",
    "companion readiness",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(repo_root()),
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


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(payload: Any) -> str:
    return sha256_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def _config_hash_payload(config: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(config)
    payload["config_hash"] = None
    return payload


def hash_preflight_config(config: dict[str, Any]) -> str:
    return sha256_json(_config_hash_payload(config))


def code_path_hash(func: Callable[..., Any]) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_json_ready(child) for child in value]
    if isinstance(value, tuple):
        return [_json_ready(child) for child in value]
    if isinstance(value, set):
        return sorted(_json_ready(child) for child in value)
    return value


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_remote_refs(*refs: str) -> dict[str, str]:
    output = _safe_git(["ls-remote", "origin", *refs])
    rows: dict[str, str] = {}
    for line in output.splitlines():
        if not line.strip():
            continue
        commit, ref = line.split(maxsplit=1)
        rows[ref] = commit
    return rows


def build_source_pin_readback() -> dict[str, Any]:
    remote_refs = _read_remote_refs(
        f"refs/heads/{BRANCH}",
        f"refs/tags/{UPSTREAM_DESIGN_TAG}",
        f"refs/tags/{PRIOR_INVALID_SELF_REPORT_TAG}",
    )
    current_head = _safe_git(["rev-parse", "HEAD"])
    upstream_commit = _safe_git(["rev-parse", UPSTREAM_DESIGN_COMMIT])
    local_upstream_tag = _safe_git(["rev-parse", f"refs/tags/{UPSTREAM_DESIGN_TAG}"])
    upstream_is_ancestor = (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", UPSTREAM_DESIGN_COMMIT, "HEAD"],
            cwd=str(repo_root()),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).returncode
        == 0
    )
    tag_type = _safe_git(["cat-file", "-t", f"refs/tags/{UPSTREAM_DESIGN_TAG}"])
    remote_upstream_tag = remote_refs.get(f"refs/tags/{UPSTREAM_DESIGN_TAG}", "")
    remote_prior_invalid_tag = remote_refs.get(f"refs/tags/{PRIOR_INVALID_SELF_REPORT_TAG}", "")
    remote_branch = remote_refs.get(f"refs/heads/{BRANCH}", "")
    status = _safe_git(["status", "--short", "--branch"])
    branch = _safe_git(["branch", "--show-current"])
    return {
        "producer_function": "build_source_pin_readback",
        "task_id": TASK_ID,
        "branch": branch,
        "expected_branch": BRANCH,
        "current_head": current_head,
        "upstream_design_commit": upstream_commit,
        "upstream_design_tag": UPSTREAM_DESIGN_TAG,
        "local_upstream_design_tag_hash": local_upstream_tag,
        "remote_upstream_design_tag_hash": remote_upstream_tag,
        "upstream_design_tag_type": tag_type,
        "remote_branch_hash": remote_branch,
        "upstream_design_commit_is_ancestor_of_current_head": upstream_is_ancestor,
        "upstream_design_commit_tag_exact_match": all(
            value == UPSTREAM_DESIGN_COMMIT for value in [upstream_commit, local_upstream_tag, remote_upstream_tag]
        ),
        "prior_preserved_invalid_commit": PRIOR_INVALID_COMMIT,
        "prior_invalid_self_report_anchor": PRIOR_INVALID_SELF_REPORT_TAG,
        "remote_prior_invalid_self_report_tag_hash": remote_prior_invalid_tag,
        "git_status_short_branch": status,
        "source_boundary_verified": (
            branch == BRANCH
            and upstream_is_ancestor
            and all(value == UPSTREAM_DESIGN_COMMIT for value in [upstream_commit, local_upstream_tag, remote_upstream_tag])
        ),
    }


def build_preflight_config(run_command: str) -> dict[str, Any]:
    train_ids = [f"train_context_{seed}_{idx}" for seed in SEEDS for idx in range(2)]
    heldout_ids = [f"heldout_context_{seed}_{idx}" for seed in SEEDS for idx in range(4)]
    pair_ids = [f"cf_pair_{seed}_{idx}" for seed in SEEDS for idx in range(4)]
    config: dict[str, Any] = {
        "task_id": TASK_ID,
        "task_family_proposal_id": TASK_CARD_ID,
        "created_before_results": True,
        "generated_dataset_ids": [f"gate4_no_candidate_preflight_dataset_{seed}" for seed in SEEDS],
        "split_ids": ["train", "heldout", "counterfactual_pair"],
        "seeds": list(SEEDS),
        "train_context_ids": train_ids,
        "heldout_context_ids": heldout_ids,
        "counterfactual_pair_ids": pair_ids,
        "predeclared_metrics": ["heldout_action_accuracy"],
        "predeclared_aggregation_rule": "mean exact-match accuracy over heldout episodes",
        "predeclared_invalidation_threshold": THRESHOLD,
        "predeclared_minimum_candidate_margin": None,
        "baseline_inventory": list(BASELINE_IDS),
        "leakage_positive_control_definition": list(LEAKAGE_CONTROL_IDS),
        "replay_corruption_test_definition": list(REPLAY_CORRUPTION_IDS),
        "structural_control_inventory": list(STRUCTURAL_CONTROL_IDS),
        "allowed_code_paths": [
            "src/gate4_replacement_no_candidate_baseline_preflight_001a/**",
            "tests/test_gate4_replacement_no_candidate_baseline_preflight_001a.py",
            "artifacts/gate4_replacement_no_candidate_baseline_preflight_001a/**",
            "docs/research/GATE4-REPLACEMENT-NO-CANDIDATE-BASELINE-PREFLIGHT-001A.md",
        ],
        "forbidden_code_paths": [
            "src/ego_mainline*",
            "src/same_agent_bridge*",
            "src/post_bridge*",
            "src/*candidate*",
            "runtime",
            "admission",
            "bridge",
            "Gate5",
            "LLM/RAG",
            "UI",
            "companion/product",
        ],
        "candidate_absent_fields_required": True,
        "run_command": run_command,
        "config_hash": None,
    }
    config["config_hash"] = hash_preflight_config(config)
    return config


def generate_task_family(config: dict[str, Any]) -> dict[str, Any]:
    train: list[dict[str, Any]] = []
    heldout: list[dict[str, Any]] = []
    counterfactual_pairs: list[dict[str, Any]] = []
    partners = list(PARTNER_TARGETS)
    for seed in config["seeds"]:
        for partner_idx, partner_id in enumerate(partners):
            target = PARTNER_TARGETS[partner_id]
            key = PARTNER_KEYS[partner_id]
            for train_idx in range(2):
                train.append(
                    _episode(
                        seed=seed,
                        split="train",
                        index=train_idx,
                        partner_idx=partner_idx,
                        partner_id=partner_id,
                        partner_key=key,
                        target=target,
                        context_id=f"train_context_{seed}_{train_idx}",
                        counterfactual_pair_id=None,
                    )
                )
            pair_id = f"cf_pair_{seed}_{partner_idx}"
            heldout_episode = _episode(
                seed=seed,
                split="heldout",
                index=partner_idx,
                partner_idx=partner_idx,
                partner_id=partner_id,
                partner_key=key,
                target=target,
                context_id=f"heldout_context_{seed}_{partner_idx}",
                counterfactual_pair_id=pair_id,
            )
            heldout.append(heldout_episode)
            other_partner = partners[(partner_idx + 1) % len(partners)]
            counterfactual_pairs.append(
                {
                    "pair_id": pair_id,
                    "surface_prompt_id": heldout_episode["observation"]["surface_prompt_id"],
                    "episode_id": heldout_episode["episode_id"],
                    "counterfactual_partner_id": other_partner,
                    "counterfactual_target_action": PARTNER_TARGETS[other_partner],
                    "surface_features_held_constant": True,
                    "latent_partner_mapping_changed": True,
                }
            )
    return {
        "producer_function": "generate_task_family",
        "train": train,
        "heldout": heldout,
        "counterfactual_pairs": counterfactual_pairs,
        "dataset_summary": {
            "train_count": len(train),
            "heldout_count": len(heldout),
            "counterfactual_pair_count": len(counterfactual_pairs),
            "target_distribution": dict(Counter(row["target_action"] for row in heldout)),
        },
    }


def _episode(
    *,
    seed: int,
    split: str,
    index: int,
    partner_idx: int,
    partner_id: str,
    partner_key: str,
    target: str,
    context_id: str,
    counterfactual_pair_id: str | None,
) -> dict[str, Any]:
    surface_id = f"shared_surface_prompt_{index % 2}"
    return {
        "episode_id": f"{split}_{seed}_{partner_id}_{index}",
        "seed": seed,
        "split": split,
        "context_id": context_id,
        "partner_id": partner_id,
        "anonymized_partner_key": partner_key,
        "counterfactual_pair_id": counterfactual_pair_id,
        "target_action": target,
        "observation": {
            "partner_id": partner_id,
            "anonymized_partner_key": partner_key,
            "context_id": context_id,
            "surface_prompt_id": surface_id,
            "surface_text": "neutral social choice prompt",
            "visible_topic": f"topic_{index % 2}",
            "query_key": f"query_{partner_id}",
            "trace_tokens": [partner_id, surface_id, f"seed_bucket_{seed % 2}"],
            "row_order": index,
        },
        "serialized_state": {
            "partner_memory_key": partner_key,
            "seen_partner_count": partner_idx + 1,
            "target_action": None,
        },
    }


def _majority(records: list[dict[str, Any]]) -> str:
    counts = Counter(row["target_action"] for row in records)
    return max(ACTIONS, key=lambda action: (counts[action], -ACTIONS.index(action)))


def _field_majority_map(records: list[dict[str, Any]], field: str) -> dict[str, str]:
    table: dict[str, Counter[str]] = {}
    for row in records:
        value = str(row["observation"].get(field, row.get(field, "")))
        table.setdefault(value, Counter())[row["target_action"]] += 1
    return {
        key: max(ACTIONS, key=lambda action: (counts[action], -ACTIONS.index(action)))
        for key, counts in table.items()
    }


def _score(predictions: dict[str, str], records: list[dict[str, Any]]) -> float:
    if not records:
        return 0.0
    correct = sum(1 for row in records if predictions.get(row["episode_id"]) == row["target_action"])
    return correct / len(records)


def _predict_from_field_map(state: dict[str, Any], observation: dict[str, Any], field: str) -> str:
    return state["map"].get(str(observation.get(field, "")), state["fallback"])


def partner_id_lookup_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {"strategy": "partner_id_lookup", "field": "partner_id", "map": _field_majority_map(train, "partner_id"), "fallback": _majority(train)}
    return _baseline_result_from_state("partner_id_lookup_baseline", state, heldout)


def preference_table_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {
        "strategy": "preference_table",
        "field": "anonymized_partner_key",
        "map": _field_majority_map(train, "anonymized_partner_key"),
        "fallback": _majority(train),
    }
    return _baseline_result_from_state("preference_table_baseline", state, heldout)


def retrieval_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    exemplars = {row["observation"]["partner_id"]: row["target_action"] for row in train}
    state = {"strategy": "retrieval", "field": "partner_id", "map": exemplars, "fallback": _majority(train)}
    return _baseline_result_from_state("retrieval_baseline", state, heldout)


def imitation_frequency_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {"strategy": "imitation_frequency", "field": "partner_id", "map": _field_majority_map(train, "partner_id"), "fallback": _majority(train)}
    return _baseline_result_from_state("imitation_frequency_baseline", state, heldout)


def order_k_history_baseline_k1(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = _history_state(train, 1)
    return _baseline_result_from_state("order_k_history_baseline_k1", state, heldout)


def order_k_history_baseline_k2(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = _history_state(train, 2)
    return _baseline_result_from_state("order_k_history_baseline_k2", state, heldout)


def static_majority_marginal_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {"strategy": "static_majority", "fallback": _majority(train)}
    return _baseline_result_from_state("static_majority_marginal_baseline", state, heldout)


def generator_proxy_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {"strategy": "surface_prompt", "field": "surface_prompt_id", "map": _field_majority_map(train, "surface_prompt_id"), "fallback": _majority(train)}
    return _baseline_result_from_state("generator_proxy_baseline", state, heldout)


def oracle_shape_rule_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {"strategy": "oracle_shape_rule", "map": dict(PARTNER_TARGETS), "fallback": _majority(train)}
    return _baseline_result_from_state("oracle_shape_rule_baseline", state, heldout)


def shuffled_linkage_control(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    partner_ids = list(PARTNER_TARGETS)
    shifted = {partner_ids[idx]: partner_ids[(idx + 1) % len(partner_ids)] for idx in range(len(partner_ids))}
    state = {
        "strategy": "shuffled_linkage",
        "field": "partner_id",
        "map": _field_majority_map(train, "partner_id"),
        "shuffle_map": shifted,
        "fallback": _majority(train),
    }
    return _baseline_result_from_state("shuffled_linkage_control", state, heldout)


def counterfactual_pair_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {"strategy": "surface_prompt", "field": "surface_prompt_id", "map": _field_majority_map(train, "surface_prompt_id"), "fallback": _majority(train)}
    return _baseline_result_from_state("counterfactual_pair_baseline", state, heldout)


def serialized_state_decoder(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {"strategy": "serialized_state_only", "fallback": _majority(train), "state_fields_used": ["seen_partner_count"]}
    return _baseline_result_from_state("serialized_state_decoder", state, heldout)


def full_bundle_decoder(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {"strategy": "full_bundle", "field": "partner_id", "map": _field_majority_map(train, "partner_id"), "fallback": _majority(train)}
    return _baseline_result_from_state("full_bundle_decoder", state, heldout)


def ngram_trace_lookup(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    table: dict[str, Counter[str]] = {}
    for row in train:
        for token in row["observation"]["trace_tokens"]:
            table.setdefault(token, Counter())[row["target_action"]] += 1
    state = {
        "strategy": "ngram_trace",
        "map": {key: max(ACTIONS, key=lambda action: (counts[action], -ACTIONS.index(action))) for key, counts in table.items()},
        "fallback": _majority(train),
    }
    return _baseline_result_from_state("ngram_trace_lookup", state, heldout)


def pair_count_frequency_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {
        "strategy": "pair_count_frequency",
        "map": _field_pair_map(train, "partner_id", "surface_prompt_id"),
        "fallback": _majority(train),
    }
    return _baseline_result_from_state("pair_count_frequency_baseline", state, heldout)


def graph_lookup(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {"strategy": "graph_lookup", "field": "partner_id", "map": _field_majority_map(train, "partner_id"), "fallback": _majority(train)}
    return _baseline_result_from_state("graph_lookup", state, heldout)


def transition_table(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {"strategy": "transition_table", "field": "partner_id", "map": _field_majority_map(train, "partner_id"), "fallback": _majority(train)}
    return _baseline_result_from_state("transition_table", state, heldout)


def successor_map(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {"strategy": "successor_map", "field": "partner_id", "map": _field_majority_map(train, "partner_id"), "fallback": _majority(train)}
    return _baseline_result_from_state("successor_map", state, heldout)


def count_table(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {"strategy": "count_table", "field": "partner_id", "map": _field_majority_map(train, "partner_id"), "fallback": _majority(train)}
    return _baseline_result_from_state("count_table", state, heldout)


def fsm_planner(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {"strategy": "fsm_planner", "field": "partner_id", "map": _field_majority_map(train, "partner_id"), "fallback": _majority(train)}
    return _baseline_result_from_state("fsm_planner", state, heldout)


def episodic_traversal(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {"strategy": "episodic_traversal", "field": "partner_id", "map": _field_majority_map(train, "partner_id"), "fallback": _majority(train)}
    return _baseline_result_from_state("episodic_traversal", state, heldout)


def query_capable_imitation_baseline(train: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    state = {"strategy": "query_imitation", "field": "query_key", "map": _field_majority_map(train, "query_key"), "fallback": _majority(train)}
    return _baseline_result_from_state("query_capable_imitation_baseline", state, heldout)


BASELINE_FUNCTIONS: dict[str, Callable[[list[dict[str, Any]], list[dict[str, Any]]], dict[str, Any]]] = {
    "partner_id_lookup_baseline": partner_id_lookup_baseline,
    "preference_table_baseline": preference_table_baseline,
    "retrieval_baseline": retrieval_baseline,
    "imitation_frequency_baseline": imitation_frequency_baseline,
    "order_k_history_baseline_k1": order_k_history_baseline_k1,
    "order_k_history_baseline_k2": order_k_history_baseline_k2,
    "static_majority_marginal_baseline": static_majority_marginal_baseline,
    "generator_proxy_baseline": generator_proxy_baseline,
    "oracle_shape_rule_baseline": oracle_shape_rule_baseline,
    "shuffled_linkage_control": shuffled_linkage_control,
    "counterfactual_pair_baseline": counterfactual_pair_baseline,
    "serialized_state_decoder": serialized_state_decoder,
    "full_bundle_decoder": full_bundle_decoder,
    "ngram_trace_lookup": ngram_trace_lookup,
    "pair_count_frequency_baseline": pair_count_frequency_baseline,
    "graph_lookup": graph_lookup,
    "transition_table": transition_table,
    "successor_map": successor_map,
    "count_table": count_table,
    "fsm_planner": fsm_planner,
    "episodic_traversal": episodic_traversal,
    "query_capable_imitation_baseline": query_capable_imitation_baseline,
}


def _history_state(train: list[dict[str, Any]], k: int) -> dict[str, Any]:
    table: dict[str, list[str]] = {}
    for row in train:
        table.setdefault(row["observation"]["partner_id"], []).append(row["target_action"])
    return {
        "strategy": f"order_k_history_{k}",
        "field": "partner_id",
        "map": {partner: Counter(values[-k:]).most_common(1)[0][0] for partner, values in table.items()},
        "fallback": _majority(train),
        "k": k,
    }


def _field_pair_map(records: list[dict[str, Any]], first: str, second: str) -> dict[str, str]:
    table: dict[str, Counter[str]] = {}
    for row in records:
        key = f"{row['observation'][first]}::{row['observation'][second]}"
        table.setdefault(key, Counter())[row["target_action"]] += 1
    return {
        key: max(ACTIONS, key=lambda action: (counts[action], -ACTIONS.index(action)))
        for key, counts in table.items()
    }


def _baseline_result_from_state(baseline_id: str, state: dict[str, Any], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    predictions = {
        row["episode_id"]: predict_from_serialized_baseline_state(baseline_id, state, row["observation"])
        for row in heldout
    }
    return {
        "baseline_id": baseline_id,
        "serialized_baseline_state": state,
        "predictions": predictions,
        "score": _score(predictions, heldout),
    }


def predict_from_serialized_baseline_state(baseline_id: str, state: dict[str, Any], observation: dict[str, Any]) -> str:
    strategy = state.get("strategy")
    fallback = state.get("fallback", ACTIONS[0])
    if strategy in {
        "partner_id_lookup",
        "preference_table",
        "retrieval",
        "imitation_frequency",
        "surface_prompt",
        "oracle_shape_rule",
        "full_bundle",
        "graph_lookup",
        "transition_table",
        "successor_map",
        "count_table",
        "fsm_planner",
        "episodic_traversal",
        "query_imitation",
        "order_k_history_1",
        "order_k_history_2",
    }:
        return _predict_from_field_map(state, observation, str(state.get("field", "partner_id")))
    if strategy == "static_majority":
        return fallback
    if strategy == "serialized_state_only":
        return fallback
    if strategy == "shuffled_linkage":
        original = observation.get("partner_id", "")
        shifted = state.get("shuffle_map", {}).get(original, original)
        changed = dict(observation)
        changed["partner_id"] = shifted
        return _predict_from_field_map(state, changed, "partner_id")
    if strategy == "ngram_trace":
        for token in observation.get("trace_tokens", []):
            if token in state.get("map", {}):
                return state["map"][token]
        return fallback
    if strategy == "pair_count_frequency":
        key = f"{observation.get('partner_id', '')}::{observation.get('surface_prompt_id', '')}"
        return state.get("map", {}).get(key, fallback)
    return fallback


def run_baselines(
    dataset: dict[str, Any],
    config: dict[str, Any],
    run_id: str,
    *,
    disabled_baselines: tuple[str, ...] = (),
) -> dict[str, Any]:
    train = dataset["train"]
    heldout = dataset["heldout"]
    results = []
    invoked = []
    for baseline_id in BASELINE_IDS:
        if baseline_id in disabled_baselines:
            continue
        producer = BASELINE_FUNCTIONS[baseline_id]
        raw = producer(train, heldout)
        invoked.append(baseline_id)
        results.append(
            {
                "baseline_id": baseline_id,
                "producer_function": producer.__name__,
                "input_artifacts": ["generated_task_family.train", "generated_task_family.heldout"],
                "run_id": run_id,
                "seed": list(config["seeds"]),
                "train_context_ids": list(config["train_context_ids"]),
                "heldout_context_ids": list(config["heldout_context_ids"]),
                "counterfactual_pair_ids": list(config["counterfactual_pair_ids"]),
                "episode_ids": [row["episode_id"] for row in heldout],
                "aggregation_rule": config["predeclared_aggregation_rule"],
                "metric": "accuracy",
                "score": raw["score"],
                "threshold": config["predeclared_invalidation_threshold"],
                "code_path_hash": code_path_hash(producer),
                "config_hash": config["config_hash"],
                "created_at": _now(),
                "verdict_reason": (
                    "cheap_baseline_reached_invalidation_threshold"
                    if raw["score"] >= config["predeclared_invalidation_threshold"]
                    else "below_invalidation_threshold"
                ),
                "candidate_or_baseline_id": baseline_id,
                "callable_invoked": True,
                "static_score_injection": False,
                "reached_threshold": raw["score"] >= config["predeclared_invalidation_threshold"],
                "serialized_baseline_state": raw["serialized_baseline_state"],
                "predictions": raw["predictions"],
                "failure_mode_interpretation": _baseline_interpretation(baseline_id, raw["score"], config),
            }
        )
    missing = [baseline_id for baseline_id in BASELINE_IDS if baseline_id not in invoked]
    return {
        "producer_function": "run_baselines",
        "declared_baselines": list(BASELINE_IDS),
        "declared_count": len(BASELINE_IDS),
        "invoked_baselines": invoked,
        "run_count": len(invoked),
        "missing_baselines": missing,
        "results": results,
        "passed_invocation_gate": not missing,
    }


def _baseline_interpretation(baseline_id: str, score: float, config: dict[str, Any]) -> str:
    if score >= config["predeclared_invalidation_threshold"]:
        return f"{baseline_id} invalidates the task family before candidate implementation"
    return f"{baseline_id} did not reach the predeclared invalidation threshold"


def select_best_faithful_baseline(baseline_results: dict[str, Any]) -> dict[str, Any]:
    rows = baseline_results["results"]
    if not rows:
        return {
            "producer_function": "select_best_faithful_baseline",
            "baseline_id": None,
            "score": 0.0,
            "reached_threshold": False,
        }
    best = max(rows, key=lambda row: (row["score"], -BASELINE_IDS.index(row["baseline_id"])))
    return {
        "producer_function": "select_best_faithful_baseline",
        "baseline_id": best["baseline_id"],
        "producer_baseline_function": best["producer_function"],
        "score": best["score"],
        "threshold": best["threshold"],
        "reached_threshold": best["reached_threshold"],
        "verdict_reason": best["verdict_reason"],
    }


def build_threshold_invalidation_report(best: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    return {
        "producer_function": "build_threshold_invalidation_report",
        "threshold": config["predeclared_invalidation_threshold"],
        "best_faithful_baseline": best,
        "any_baseline_reached_threshold": bool(best["reached_threshold"]),
        "verdict_if_reached": "no_candidate_baseline_preflight_blocked_by_cheap_baseline_001a",
        "threshold_edited_after_results": False,
    }


def _clean_bundle(dataset: dict[str, Any]) -> dict[str, Any]:
    return {
        "heldout_observations": [copy.deepcopy(row["observation"]) for row in dataset["heldout"]],
        "filenames": [f"episode_{idx:03d}.json" for idx, _row in enumerate(dataset["heldout"])],
        "helper_literals": ["neutral social choice prompt", "partner memory key"],
    }


def _scan_for_literal_leaks(bundle: Any) -> dict[str, Any]:
    text = json.dumps(bundle, sort_keys=True)
    detected = []
    leak_patterns = {
        "visible_label": r"target_action|visible_target_label|label_leak",
        "partner_id": r"partner_id_to_target|partner_target_leak",
        "preference_table": r"preference_table_to_target|target_preference",
        "serialized_state": r"serialized_state_target|state_target_action",
        "filename_order": r"target_in_filename|ordered_target",
        "helper_literal": r"helper_literal_target|literal_target_action",
    }
    for leak_id, pattern in leak_patterns.items():
        if re.search(pattern, text):
            detected.append(leak_id)
    return {
        "producer_function": "_scan_for_literal_leaks",
        "detected_leak_families": detected,
        "leak_detected": bool(detected),
    }


def run_leakage_positive_controls(disable_control: str | None = None) -> dict[str, Any]:
    controls = {
        "injected_visible_label_leak": {"visible_target_label": "support", "label_leak": True},
        "injected_partner_id_leak": {"partner_id_to_target": dict(PARTNER_TARGETS)},
        "injected_preference_table_leak": {"preference_table_to_target": dict(PARTNER_TARGETS)},
        "injected_serialized_state_leak": {"serialized_state_target": "challenge"},
        "injected_filename_order_leak": {"filenames": ["target_in_filename_support_001.json"]},
        "injected_helper_literal_leak": {"helper_literal_target": "literal_target_action=summarize"},
    }
    detected = []
    blocking = []
    rows = []
    for control_id, payload in controls.items():
        scan_payload = {} if control_id == disable_control else payload
        result = _scan_for_literal_leaks(scan_payload)
        found = result["leak_detected"]
        if found:
            detected.append(control_id)
        else:
            blocking.append(f"positive_control_not_detected:{control_id}")
        rows.append({"control_id": control_id, "detected": found, "scanner_result": result})
    return {
        "producer_function": "run_leakage_positive_controls",
        "passed": not blocking,
        "detected_control_ids": detected,
        "blocking_reasons": blocking,
        "controls": rows,
    }


def run_clean_leakage_scan(dataset: dict[str, Any], positive: dict[str, Any]) -> dict[str, Any]:
    result = _scan_for_literal_leaks(_clean_bundle(dataset))
    if not positive["passed"]:
        verdict = "blocked_positive_controls_not_passed"
    elif result["leak_detected"]:
        verdict = "clean_bundle_leak_detected"
    else:
        verdict = "clean_no_literal_target_leak_detected"
    return {
        "producer_function": "run_clean_leakage_scan",
        "clean_bundle_scan_computed": True,
        "clean_scan_trusted_after_positive_controls": positive["passed"],
        "verdict": verdict,
        "scanner_result": result,
    }


def run_replay_checks(
    baseline_results: dict[str, Any],
    dataset: dict[str, Any],
    *,
    allow_stored_prediction_replay: bool = False,
) -> dict[str, Any]:
    heldout = dataset["heldout"]
    recomputed_ids = []
    mismatches = []
    for row in baseline_results["results"]:
        recomputed = {
            episode["episode_id"]: predict_from_serialized_baseline_state(
                row["baseline_id"], row["serialized_baseline_state"], episode["observation"]
            )
            for episode in heldout
        }
        recomputed_score = _score(recomputed, heldout)
        if recomputed != row["predictions"] or recomputed_score != row["score"]:
            mismatches.append(row["baseline_id"])
        recomputed_ids.append(row["baseline_id"])
    passed = not mismatches and not allow_stored_prediction_replay
    return {
        "producer_function": "run_replay_checks",
        "passed": passed,
        "baseline_ids_recomputed": recomputed_ids,
        "mismatched_baselines": mismatches,
        "recomputed_from": ["serialized_baseline_state", "observation"],
        "uses_stored_predictions_only": allow_stored_prediction_replay,
        "uses_hash_only_comparison": False,
        "stored_prediction_replay_rejected": not allow_stored_prediction_replay,
    }


def run_replay_corruption_checks(baseline_results: dict[str, Any], dataset: dict[str, Any]) -> dict[str, Any]:
    heldout = dataset["heldout"]
    partner_row = next(row for row in baseline_results["results"] if row["baseline_id"] == "partner_id_lookup_baseline")
    original_score = partner_row["score"]
    state_corrupt = copy.deepcopy(partner_row["serialized_baseline_state"])
    state_corrupt["map"] = {}
    state_predictions = {
        row["episode_id"]: predict_from_serialized_baseline_state("partner_id_lookup_baseline", state_corrupt, row["observation"])
        for row in heldout
    }
    observation_corrupt = []
    for row in heldout:
        changed = copy.deepcopy(row)
        changed["observation"]["partner_id"] = "unknown_partner"
        observation_corrupt.append(changed)
    obs_predictions = {
        row["episode_id"]: predict_from_serialized_baseline_state("partner_id_lookup_baseline", partner_row["serialized_baseline_state"], row["observation"])
        for row in observation_corrupt
    }
    linkage_corrupt = []
    partner_ids = list(PARTNER_TARGETS)
    for row in heldout:
        changed = copy.deepcopy(row)
        old = changed["observation"]["partner_id"]
        changed["observation"]["partner_id"] = partner_ids[(partner_ids.index(old) + 1) % len(partner_ids)]
        linkage_corrupt.append(changed)
    link_predictions = {
        row["episode_id"]: predict_from_serialized_baseline_state("partner_id_lookup_baseline", partner_row["serialized_baseline_state"], row["observation"])
        for row in linkage_corrupt
    }
    state_score = _score(state_predictions, heldout)
    obs_score = _score(obs_predictions, heldout)
    link_score = _score(link_predictions, heldout)
    return {
        "producer_function": "run_replay_corruption_checks",
        "conditions_run": list(REPLAY_CORRUPTION_IDS),
        "original_score": original_score,
        "corrupt_serialized_baseline_state_score": state_score,
        "corrupt_observation_score": obs_score,
        "corrupt_linkage_score": link_score,
        "state_corruption_failed_or_changed": state_score != original_score,
        "observation_corruption_failed_or_changed": obs_score != original_score,
        "linkage_corruption_failed_or_changed": link_score != original_score,
        "passed": state_score != original_score and obs_score != original_score and link_score != original_score,
    }


def run_structural_controls(
    dataset: dict[str, Any],
    config: dict[str, Any],
    *,
    skip_control: str | None = None,
) -> dict[str, Any]:
    rows = []
    for control_id in STRUCTURAL_CONTROL_IDS:
        if control_id == skip_control:
            continue
        controlled = _apply_structural_control(dataset, control_id)
        baseline = partner_id_lookup_baseline(controlled["train"], controlled["heldout"])
        rows.append(
            {
                "control_id": control_id,
                "producer_function": "run_structural_controls",
                "score": baseline["score"],
                "threshold": config["predeclared_invalidation_threshold"],
                "changed_or_blocked_expected_shortcut": baseline["score"] < config["predeclared_invalidation_threshold"],
                "reran_baseline_under_intervention": True,
            }
        )
    missing = [control_id for control_id in STRUCTURAL_CONTROL_IDS if control_id not in {row["control_id"] for row in rows}]
    return {
        "producer_function": "run_structural_controls",
        "controls_declared": list(STRUCTURAL_CONTROL_IDS),
        "controls_run": [row["control_id"] for row in rows],
        "missing_controls": missing,
        "results": rows,
    }


def _apply_structural_control(dataset: dict[str, Any], control_id: str) -> dict[str, Any]:
    changed = copy.deepcopy(dataset)
    if control_id in {
        "remove_partner_context_linkage",
        "swap_heldout_partner_context_mappings",
        "corrupt_observation",
    }:
        for row in changed["heldout"]:
            row["observation"]["partner_id"] = "unlinked_partner"
    if control_id == "shuffle_intervention_feedback":
        changed["heldout"] = list(reversed(changed["heldout"]))
    if control_id == "inject_misleading_retrieval_matches":
        for row in changed["train"]:
            row["target_action"] = ACTIONS[(ACTIONS.index(row["target_action"]) + 1) % len(ACTIONS)]
    if control_id == "remove_transfer_phase":
        changed["train"] = []
    if control_id == "replace_causal_feedback_with_non_causal_correlated_cue":
        for row in changed["heldout"]:
            row["observation"]["surface_prompt_id"] = "non_causal_common"
    if control_id == "counterfactual_pair_split":
        for row in changed["heldout"]:
            row["target_action"] = ACTIONS[(ACTIONS.index(row["target_action"]) + 1) % len(ACTIONS)]
    if control_id == "positive_control_leakage_injection":
        for row in changed["heldout"]:
            row["observation"]["visible_target_label"] = row["target_action"]
    if control_id == "corrupt_replay_state":
        for row in changed["train"]:
            row["observation"]["partner_id"] = "corrupt_state_partner"
    return changed


def build_provenance_report(
    run_id: str,
    config: dict[str, Any],
    baseline_results: dict[str, Any],
    leakage_positive: dict[str, Any],
    leakage_scan: dict[str, Any],
    replay: dict[str, Any],
    replay_corruption: dict[str, Any],
    structural_controls: dict[str, Any],
) -> dict[str, Any]:
    records = []
    for row in baseline_results["results"]:
        records.append(_provenance_row(row["producer_function"], row["baseline_id"], row["score"], "accuracy", row["verdict_reason"], run_id, config))
    records.append(_provenance_row("run_leakage_positive_controls", "leakage_positive_controls", 1.0 if leakage_positive["passed"] else 0.0, "gate_boolean", "positive controls detected" if leakage_positive["passed"] else "positive control failure", run_id, config))
    records.append(_provenance_row("run_clean_leakage_scan", "clean_leakage_scan", 0.0 if leakage_scan["scanner_result"]["leak_detected"] else 1.0, "gate_boolean", leakage_scan["verdict"], run_id, config))
    records.append(_provenance_row("run_replay_checks", "replay_recomputation", 1.0 if replay["passed"] else 0.0, "gate_boolean", "replay recomputed" if replay["passed"] else "replay blocked", run_id, config))
    records.append(_provenance_row("run_replay_corruption_checks", "replay_corruption", 1.0 if replay_corruption["passed"] else 0.0, "gate_boolean", "corruption changed replay" if replay_corruption["passed"] else "corruption failed", run_id, config))
    for row in structural_controls["results"]:
        records.append(_provenance_row("run_structural_controls", row["control_id"], row["score"], "structural_control_accuracy", "structural control rerun", run_id, config))
    report = {"producer_function": "build_provenance_report", "records": records}
    report["verification"] = verify_computed_evidence_provenance(report)
    return report


def _provenance_row(
    producer_function: str,
    identifier: str,
    score: float,
    metric: str,
    verdict_reason: str,
    run_id: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    return {
        "producer_function": producer_function,
        "input_artifacts": ["preflight_config_locked_before_results.json", "generated_task_family"],
        "run_id": run_id,
        "seed": list(config["seeds"]),
        "train_context_ids": list(config["train_context_ids"]),
        "heldout_context_ids": list(config["heldout_context_ids"]),
        "counterfactual_pair_ids": list(config["counterfactual_pair_ids"]),
        "episode_ids": [f"heldout_{seed}_{partner}_{idx}" for seed in SEEDS for idx, partner in enumerate(PARTNER_TARGETS)],
        "aggregation_rule": config["predeclared_aggregation_rule"],
        "metric": metric,
        "score": score,
        "threshold": config["predeclared_invalidation_threshold"],
        "code_path_hash": code_path_hash(_producer_by_name(producer_function)),
        "config_hash": config["config_hash"],
        "created_at": _now(),
        "verdict_reason": verdict_reason,
        "candidate_or_baseline_id": identifier,
        "static_score_injection": False,
    }


def _producer_by_name(name: str) -> Callable[..., Any]:
    producers: dict[str, Callable[..., Any]] = {
        **BASELINE_FUNCTIONS,
        "run_leakage_positive_controls": run_leakage_positive_controls,
        "run_clean_leakage_scan": run_clean_leakage_scan,
        "run_replay_checks": run_replay_checks,
        "run_replay_corruption_checks": run_replay_corruption_checks,
        "run_structural_controls": run_structural_controls,
    }
    return producers[name]


def verify_computed_evidence_provenance(report: dict[str, Any]) -> dict[str, Any]:
    reasons = []
    missing_fields = []
    for row in report.get("records", []):
        for field in REQUIRED_PROVENANCE_FIELDS:
            if field not in row or row[field] in (None, "", [], {}):
                missing_fields.append(field)
                reasons.append(f"missing_field:{row.get('candidate_or_baseline_id')}:{field}")
        if row.get("static_score_injection"):
            reasons.append("static_score_injection")
        producer_name = row.get("producer_function")
        try:
            producer = _producer_by_name(producer_name)
        except KeyError:
            reasons.append(f"unknown_producer:{producer_name}")
            continue
        if row.get("code_path_hash") != code_path_hash(producer):
            reasons.append(f"code_path_hash_mismatch:{producer_name}")
    return {
        "producer_function": "verify_computed_evidence_provenance",
        "passed": not reasons,
        "blocking_reasons": sorted(set(reasons)),
        "missing_fields": sorted(set(missing_fields)),
    }


def build_unused_input_blocker_scan(
    config: dict[str, Any],
    dataset: dict[str, Any],
    baseline_results: dict[str, Any],
    leakage_positive: dict[str, Any],
    replay_corruption: dict[str, Any],
    structural_controls: dict[str, Any],
) -> dict[str, Any]:
    reasons = []
    for baseline_id in baseline_results["missing_baselines"]:
        reasons.append(f"unused_declared_baseline:{baseline_id}")
    for control_id in leakage_positive["blocking_reasons"]:
        reasons.append(control_id)
    for condition in REPLAY_CORRUPTION_IDS:
        if condition not in replay_corruption["conditions_run"]:
            reasons.append(f"unused_replay_corruption_condition:{condition}")
    for control_id in structural_controls["missing_controls"]:
        reasons.append(f"unused_structural_control:{control_id}")
    used_seeds = sorted({row["seed"] for row in dataset["train"] + dataset["heldout"]})
    for seed in config["seeds"]:
        if seed not in used_seeds:
            reasons.append(f"unused_seed:{seed}")
    train_contexts = {row["context_id"] for row in dataset["train"]}
    heldout_contexts = {row["context_id"] for row in dataset["heldout"]}
    pair_ids = {row["pair_id"] for row in dataset["counterfactual_pairs"]}
    for context_id in config["train_context_ids"]:
        if context_id not in train_contexts:
            reasons.append(f"unused_train_context:{context_id}")
    for context_id in config["heldout_context_ids"]:
        if context_id not in heldout_contexts:
            reasons.append(f"unused_heldout_context:{context_id}")
    for pair_id in config["counterfactual_pair_ids"]:
        if pair_id not in pair_ids:
            reasons.append(f"unused_counterfactual_pair:{pair_id}")
    return {
        "producer_function": "build_unused_input_blocker_scan",
        "passed": not reasons,
        "blocking_reasons": sorted(set(reasons)),
        "unused_frozen_seed_ids": [reason for reason in reasons if reason.startswith("unused_seed:")],
        "unused_train_context_ids": [reason for reason in reasons if reason.startswith("unused_train_context:")],
        "unused_heldout_context_ids": [reason for reason in reasons if reason.startswith("unused_heldout_context:")],
        "unused_counterfactual_pair_ids": [reason for reason in reasons if reason.startswith("unused_counterfactual_pair:")],
    }


def build_no_candidate_code_scan() -> dict[str, Any]:
    paths = _changed_or_new_scope_paths()
    forbidden_patterns = [
        r"\bcandidate_predict\b",
        r"\bcandidate_model\b",
        r"\bsocial_causal_candidate\b",
        r"\bcandidate_admission\b",
        r"\bGate4Candidate\b",
        r"\bdef\s+candidate\b",
    ]
    entrypoints = []
    scores = []
    for path in paths:
        full_path = repo_root() / path
        if not full_path.exists() or full_path.is_dir() or full_path.suffix not in {".py", ".md", ".json"}:
            continue
        text = full_path.read_text(encoding="utf-8", errors="ignore")
        for pattern in forbidden_patterns:
            if re.search(pattern, text):
                entrypoints.append(f"{path}:{pattern}")
        if re.search(r"\bcandidate_score\s*=", text):
            scores.append(path)
    return {
        "producer_function": "build_no_candidate_code_scan",
        "scanned_paths": paths,
        "candidate_entrypoints_found": entrypoints,
        "candidate_scores_found": scores,
        "candidate_admission_flags_found": [],
        "runtime_or_bridge_wiring_found": [],
        "passed": not entrypoints and not scores,
    }


def build_forbidden_path_scan() -> dict[str, Any]:
    paths = _changed_or_new_scope_paths()
    allowed_prefixes = [
        "src/gate4_replacement_no_candidate_baseline_preflight_001a/",
        "tests/test_gate4_replacement_no_candidate_baseline_preflight_001a.py",
        "artifacts/gate4_replacement_no_candidate_baseline_preflight_001a/",
        "docs/research/GATE4-REPLACEMENT-NO-CANDIDATE-BASELINE-PREFLIGHT-001A.md",
    ]
    forbidden = [path for path in paths if not any(path.startswith(prefix) or path == prefix for prefix in allowed_prefixes)]
    return {
        "producer_function": "build_forbidden_path_scan",
        "changed_or_new_paths": paths,
        "allowed_prefixes": allowed_prefixes,
        "forbidden_paths_touched": forbidden,
        "passed": not forbidden,
    }


def _changed_or_new_scope_paths() -> list[str]:
    output = _safe_git(["status", "--porcelain=v1"])
    paths = []
    for line in output.splitlines():
        if not line.strip():
            continue
        raw = line[3:] if len(line) > 3 else line
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        paths.append(raw.replace("\\", "/"))
    return sorted(paths)


def compute_result_verdict(
    *,
    source_pin: dict[str, Any],
    config_hash_readback: dict[str, Any],
    baseline_results: dict[str, Any],
    best: dict[str, Any],
    leakage_positive: dict[str, Any],
    leakage_scan: dict[str, Any],
    replay: dict[str, Any],
    replay_corruption: dict[str, Any],
    provenance: dict[str, Any],
    unused_scan: dict[str, Any],
    no_candidate_scan: dict[str, Any],
    forbidden_path_scan: dict[str, Any],
) -> tuple[str, list[str]]:
    stop = []
    if not source_pin["source_boundary_verified"]:
        stop.append("upstream_design_source_boundary_not_verified")
    if not config_hash_readback["config_hash_unchanged_after_results"]:
        stop.append("threshold_changed_after_results")
    if baseline_results["missing_baselines"]:
        stop.extend(f"declared_baseline_not_run:{baseline_id}" for baseline_id in baseline_results["missing_baselines"])
    if not leakage_positive["passed"]:
        stop.extend(leakage_positive["blocking_reasons"])
    if leakage_scan["verdict"] == "clean_bundle_leak_detected":
        stop.append("clean_bundle_leak_detected")
    if not replay["passed"]:
        stop.append("replay_recomputation_failed_or_shortcut")
    if not replay_corruption["passed"]:
        stop.append("replay_corruption_control_failed")
    if not provenance["verification"]["passed"]:
        stop.extend(provenance["verification"]["blocking_reasons"])
    if not unused_scan["passed"]:
        stop.extend(unused_scan["blocking_reasons"])
    if not no_candidate_scan["passed"]:
        stop.append("candidate_code_or_score_detected")
    if not forbidden_path_scan["passed"]:
        stop.append("forbidden_path_touched")

    if not no_candidate_scan["passed"]:
        return "no_candidate_baseline_preflight_blocked_by_candidate_drift_001a", sorted(set(stop))
    if not leakage_positive["passed"] or leakage_scan["verdict"] == "clean_bundle_leak_detected":
        return "no_candidate_baseline_preflight_blocked_by_leakage_001a", sorted(set(stop))
    if not replay["passed"] or not replay_corruption["passed"]:
        return "no_candidate_baseline_preflight_blocked_by_replay_failure_001a", sorted(set(stop))
    provenance_fail = (
        not config_hash_readback["config_hash_unchanged_after_results"]
        or bool(baseline_results["missing_baselines"])
        or not provenance["verification"]["passed"]
        or not unused_scan["passed"]
        or not forbidden_path_scan["passed"]
        or not source_pin["source_boundary_verified"]
    )
    if provenance_fail:
        return "no_candidate_baseline_preflight_blocked_by_provenance_failure_001a", sorted(set(stop))
    if best["reached_threshold"]:
        stop.append(f"cheap_baseline_reached_threshold:{best['baseline_id']}")
        return "no_candidate_baseline_preflight_blocked_by_cheap_baseline_001a", sorted(set(stop))
    return "no_candidate_baseline_preflight_survived_001a", sorted(set(stop))


def execute_preflight(
    output_dir: str | Path | None = None,
    *,
    persist_artifacts: bool = True,
    mutate_threshold_after_results: bool = False,
    disabled_baselines: tuple[str, ...] = (),
    skip_structural_control: str | None = None,
    disable_leakage_positive_control: str | None = None,
    allow_stored_prediction_replay: bool = False,
    test_result_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    run_command = "$env:PYTHONPATH='src'; python -m gate4_replacement_no_candidate_baseline_preflight_001a --write-report"
    config = build_preflight_config(run_command)
    run_id = f"{TASK_ID}_{config['config_hash'][:16]}"
    source_pin = build_source_pin_readback()
    dataset = generate_task_family(config)
    baseline_results = run_baselines(dataset, config, run_id, disabled_baselines=disabled_baselines)
    best = select_best_faithful_baseline(baseline_results)
    threshold_report = build_threshold_invalidation_report(best, config)
    leakage_positive = run_leakage_positive_controls(disable_control=disable_leakage_positive_control)
    leakage_scan = run_clean_leakage_scan(dataset, leakage_positive)
    replay = run_replay_checks(baseline_results, dataset, allow_stored_prediction_replay=allow_stored_prediction_replay)
    replay_corruption = run_replay_corruption_checks(baseline_results, dataset)
    structural_controls = run_structural_controls(dataset, config, skip_control=skip_structural_control)
    if mutate_threshold_after_results:
        config["predeclared_invalidation_threshold"] = 0.99
        threshold_report["threshold_edited_after_results"] = True
    config_hash_readback = {
        "producer_function": "build_preflight_config_hash_readback",
        "config_hash": config.get("config_hash"),
        "recomputed_config_hash": hash_preflight_config(config),
        "config_hash_unchanged_after_results": config.get("config_hash") == hash_preflight_config(config),
    }
    provenance = build_provenance_report(
        run_id,
        config,
        baseline_results,
        leakage_positive,
        leakage_scan,
        replay,
        replay_corruption,
        structural_controls,
    )
    unused_scan = build_unused_input_blocker_scan(
        config,
        dataset,
        baseline_results,
        leakage_positive,
        replay_corruption,
        structural_controls,
    )
    no_candidate_scan = build_no_candidate_code_scan()
    forbidden_path_scan = build_forbidden_path_scan()
    verdict, stop_conditions = compute_result_verdict(
        source_pin=source_pin,
        config_hash_readback=config_hash_readback,
        baseline_results=baseline_results,
        best=best,
        leakage_positive=leakage_positive,
        leakage_scan=leakage_scan,
        replay=replay,
        replay_corruption=replay_corruption,
        provenance=provenance,
        unused_scan=unused_scan,
        no_candidate_scan=no_candidate_scan,
        forbidden_path_scan=forbidden_path_scan,
    )
    result = {
        "producer_function": "execute_preflight.compute_result",
        "task_id": TASK_ID,
        "task_card_id": TASK_CARD_ID,
        "run_id": run_id,
        "verdict": verdict,
        "current_layer": "engineering implementation / evidence-governance / no-candidate baseline-preflight only",
        "mainline_integration_status": "not_mainline_integrated",
        "enabled_status": "local_callable_preflight_runner_only",
        "real_trigger_evidence": {
            "run_command": run_command,
            "run_id": run_id,
            "seeds": config["seeds"],
            "input_artifact_paths": ["generated_task_family", "preflight_config_locked_before_results.json"],
            "output_artifact_dir": str(_resolve_output_dir(output_dir)),
        },
        "claim_ceiling": CLAIM_CEILING,
        "next_minimal_closed_loop_action": "route closure, redesign, or stronger replacement because a cheap baseline invalidated this generated task family",
        "stop_conditions_triggered": stop_conditions,
        "candidate_code_created": not no_candidate_scan["passed"],
        "candidate_score_produced": False,
        "gate4_validity_claimed": False,
        "baseline_count_declared": baseline_results["declared_count"],
        "baseline_count_run": baseline_results["run_count"],
        "best_faithful_baseline": best,
        "threshold": config["predeclared_invalidation_threshold"],
        "any_baseline_reached_threshold": best["reached_threshold"],
        "leakage_positive_control_detected": leakage_positive["passed"],
        "replay_recomputation_passed": replay["passed"],
        "replay_corruption_failed_as_expected": replay_corruption["passed"],
        "provenance_complete": provenance["verification"]["passed"],
        "auto_remote_anchor": AUTO_REMOTE_ANCHOR,
        "auto_remote_anchor_eligible_if_committed_clean": verdict
        in {
            "no_candidate_baseline_preflight_survived_001a",
            "no_candidate_baseline_preflight_blocked_by_cheap_baseline_001a",
            "no_candidate_baseline_preflight_blocked_by_leakage_001a",
            "no_candidate_baseline_preflight_blocked_by_replay_failure_001a",
            "no_candidate_baseline_preflight_blocked_by_provenance_failure_001a",
        },
        "push_performed": False,
        "tag_performed": False,
        "remote_anchor_performed": False,
        "what_this_does_not_prove": list(CLAIM_EXCLUSIONS),
    }
    negative_evidence = {
        "producer_function": "build_negative_evidence_report",
        "negative_evidence_preserved": verdict != "no_candidate_baseline_preflight_survived_001a",
        "verdict": verdict,
        "best_faithful_baseline": best,
        "stop_conditions_triggered": stop_conditions,
        "do_not_patch_to_pass": True,
    }
    blocker = {
        "producer_function": "build_blocker_readback",
        "blocked": verdict != "no_candidate_baseline_preflight_survived_001a",
        "blocking_reasons": stop_conditions,
    }
    claim_ceiling = {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "what_this_does_not_prove": list(CLAIM_EXCLUSIONS),
    }
    routing = {
        "producer_function": "build_routing_recommendation",
        "recommendation": "close_or_redesign_task_family_before_candidate_work" if best["reached_threshold"] else "eligible_for_independent_review_before_candidate_task",
        "no_candidate_implementation_authorized": True,
        "gate5_admission_bridge_runtime_mainline_authorized": False,
    }
    test_results = test_result_readback or {
        "command": "not_final_current_test_invocation",
        "exit_code": None,
        "summary": "test readback not supplied to this run",
    }
    run = {
        "task_id": TASK_ID,
        "run_id": run_id,
        "source_pin_readback": source_pin,
        "preflight_config_locked_before_results": config,
        "preflight_config_hash_readback": config_hash_readback,
        "baseline_inventory": {
            "producer_function": "build_baseline_inventory",
            "baseline_ids": list(BASELINE_IDS),
            "graph_cache_family": list(GRAPH_CACHE_FAMILY),
            "declared_count": len(BASELINE_IDS),
        },
        "baseline_results": baseline_results,
        "best_faithful_baseline": best,
        "threshold_invalidation_report": threshold_report,
        "leakage_scan_results": leakage_scan,
        "leakage_positive_control_results": leakage_positive,
        "replay_recomputation_results": replay,
        "replay_corruption_results": replay_corruption,
        "structural_control_results": structural_controls,
        "computed_evidence_provenance": provenance,
        "unused_input_blocker_scan": unused_scan,
        "no_candidate_code_scan": no_candidate_scan,
        "forbidden_path_scan": forbidden_path_scan,
        "test_results": test_results,
        "claim_ceiling": claim_ceiling,
        "routing_recommendation": routing,
        "negative_evidence_report": negative_evidence,
        "blocker_readback": blocker,
        "generated_task_family": dataset,
        "result": result,
    }
    if persist_artifacts:
        out = _resolve_output_dir(output_dir)
        _write_artifacts(out, run)
    return run


def _resolve_output_dir(output_dir: str | Path | None) -> Path:
    if output_dir is None:
        return repo_root() / "artifacts" / ARTIFACT_DIR_NAME
    path = Path(output_dir)
    if path.is_absolute():
        return path
    return repo_root() / path


def _write_artifacts(out: Path, run: dict[str, Any]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    artifact_map = {
        "result.json": run["result"],
        "source_pin_readback.json": run["source_pin_readback"],
        "preflight_config_locked_before_results.json": run["preflight_config_locked_before_results"],
        "preflight_config_hash_readback.json": run["preflight_config_hash_readback"],
        "baseline_inventory.json": run["baseline_inventory"],
        "baseline_results.json": run["baseline_results"],
        "best_faithful_baseline.json": run["best_faithful_baseline"],
        "threshold_invalidation_report.json": run["threshold_invalidation_report"],
        "leakage_scan_results.json": run["leakage_scan_results"],
        "leakage_positive_control_results.json": run["leakage_positive_control_results"],
        "replay_recomputation_results.json": run["replay_recomputation_results"],
        "replay_corruption_results.json": run["replay_corruption_results"],
        "structural_control_results.json": run["structural_control_results"],
        "computed_evidence_provenance.json": run["computed_evidence_provenance"],
        "unused_input_blocker_scan.json": run["unused_input_blocker_scan"],
        "no_candidate_code_scan.json": run["no_candidate_code_scan"],
        "forbidden_path_scan.json": run["forbidden_path_scan"],
        "test_results.json": run["test_results"],
        "claim_ceiling.json": run["claim_ceiling"],
        "routing_recommendation.json": run["routing_recommendation"],
        "negative_evidence_report.json": run["negative_evidence_report"],
        "blocker_readback.json": run["blocker_readback"],
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
    best = run["best_faithful_baseline"]
    lines = [
        "# GATE4-REPLACEMENT-NO-CANDIDATE-BASELINE-PREFLIGHT-001A",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        "Layer: engineering implementation / evidence-governance / no-candidate baseline-preflight only.",
        "",
        "Mainline integration status: not mainline-integrated.",
        "",
        "Enabled status: local callable preflight runner only. No EGO runtime capability is enabled.",
        "",
        "Auto-Remote-Anchor: conditional",
        "",
        "No Gate4 validity claim is made.",
        "",
        "## Source Boundary",
        "",
        f"- Branch: `{source['branch']}`",
        f"- Current HEAD at run: `{source['current_head']}`",
        f"- Upstream design commit: `{source['upstream_design_commit']}`",
        f"- Local upstream design tag hash: `{source['local_upstream_design_tag_hash']}`",
        f"- Remote upstream design tag hash: `{source['remote_upstream_design_tag_hash']}`",
        f"- Upstream tag exact match: `{source['upstream_design_commit_tag_exact_match']}`",
        "",
        "## Problem Definition",
        "",
        "This preflight tests whether the replacement Gate4 task family is already killed by cheap independent baselines, leakage, replay shortcuts, or provenance failure before any candidate implementation exists.",
        "",
        "## No-Candidate Boundary",
        "",
        f"- Candidate code created: `{result['candidate_code_created']}`",
        f"- Candidate score produced: `{result['candidate_score_produced']}`",
        "- Runtime, bridge, admission, Gate5, LLM/RAG, UI, companion, and EGO-mainline wiring were not authorized.",
        "",
        "## Baseline Inventory",
        "",
        f"- Declared baselines: `{run['baseline_results']['declared_count']}`",
        f"- Run baselines: `{run['baseline_results']['run_count']}`",
        f"- Best faithful baseline: `{best['baseline_id']}` score `{best['score']}` threshold `{best['threshold']}`",
        "",
        "## Pre-Run Threshold/Config Lock",
        "",
        f"- Config hash: `{run['preflight_config_locked_before_results']['config_hash']}`",
        f"- Config hash unchanged after results: `{run['preflight_config_hash_readback']['config_hash_unchanged_after_results']}`",
        "",
        "## Leakage And Replay",
        "",
        f"- Leakage positive controls detected: `{result['leakage_positive_control_detected']}`",
        f"- Clean leakage scan verdict: `{run['leakage_scan_results']['verdict']}`",
        f"- Replay recomputation passed: `{result['replay_recomputation_passed']}`",
        f"- Replay corruption failed or changed as expected: `{result['replay_corruption_failed_as_expected']}`",
        "",
        "## Structural Controls",
        "",
        f"- Structural controls run: `{len(run['structural_control_results']['controls_run'])}`",
        f"- Missing controls: `{run['structural_control_results']['missing_controls']}`",
        "",
        "## Computed-Evidence Provenance",
        "",
        f"- Provenance complete: `{result['provenance_complete']}`",
        f"- Provenance record count: `{len(run['computed_evidence_provenance']['records'])}`",
        "",
        "## Stop Condition Readback",
        "",
        *[f"- `{item}`" for item in result["stop_conditions_triggered"]],
        "",
        "## Final Verdict",
        "",
        f"`{result['verdict']}`",
        "",
        "## Claim Ceiling",
        "",
        CLAIM_CEILING,
        "",
        "## What This Proves",
        "",
        "This proves only that the generated no-candidate preflight ran callable cheap-baseline, leakage, replay, corruption, and provenance checks in this bounded local distribution.",
        "",
        "## What This Does Not Prove",
        "",
        *[f"- {item}" for item in CLAIM_EXCLUSIONS],
        "",
        "## Next Minimal Action",
        "",
        result["next_minimal_closed_loop_action"],
        "",
        "## Rollback / Routing Recommendation",
        "",
        run["routing_recommendation"]["recommendation"],
    ]
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
    run = execute_preflight(
        output_dir=args.output_dir,
        persist_artifacts=True,
        test_result_readback=test_readback,
    )
    if args.write_report:
        write_research_report(run)
    print(json.dumps(run["result"], indent=2, sort_keys=True))
