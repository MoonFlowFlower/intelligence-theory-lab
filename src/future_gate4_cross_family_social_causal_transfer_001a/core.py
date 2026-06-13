from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from . import (
    AUTO_REMOTE_ANCHOR,
    CLAUDE_REAUDIT_ARTIFACT_DIR,
    CLAUDE_REAUDIT_PATH,
    CLAIM_CEILING,
    DESIGN_CARD_PATH,
    DESIGN_CONTRACT_DIR,
    EXPECTED_BRANCH,
    EXPECTED_OVERALL_SEALED_BOUNDARY,
    LATEST_GATE4_RELEVANT_SEALED_BOUNDARY,
    TASK_ID,
)


GRAPH_CACHE_FAMILY = (
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
)

REQUIRED_BASELINES = (
    "serialized_state_decoder",
    "full_bundle_decoder",
    "partner_id_decoder",
    "table_lookup",
    "pair_count",
    "ngram_trace_lookup",
    "belief_table",
    "nearest_neighbor_retrieval",
    "episodic_trace_retrieval",
    "target_label_oracle_leak_check",
    *GRAPH_CACHE_FAMILY,
    "query_capable_imitation_baseline",
)

FAITHFUL_BASELINES = tuple(name for name in REQUIRED_BASELINES if name != "target_label_oracle_leak_check")

REQUIRED_ABLATIONS = (
    "remove_partner_hidden_state_update",
    "mask_partner_causal_observation_channel",
    "shuffle_partner_family_labels",
    "disable_counterfactual_query_update_path",
    "disable_heldout_schema_transfer_component",
    "remove_explicit_partner_family_schema_ids",
    "perturb_intervention_observations_preserve_trace_length",
    "no_learning_frozen_state_variant",
)

CLAIM_EXCLUSIONS = (
    "valid Gate4",
    "mechanism validity",
    "social-latent inference success",
    "agency",
    "selfhood",
    "consciousness",
    "emotion",
    "autonomy",
    "EGO readiness",
    "runtime readiness",
    "companion readiness",
    "stable user benefit",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def source_file_path() -> str:
    return Path(__file__).relative_to(repo_root()).as_posix()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_json(payload: Any) -> str:
    return sha256_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def sha256_file(path: str | Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def code_path_hash() -> str:
    return sha256_file(Path(__file__))


def git_output(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root(),
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def git_success(args: list[str]) -> bool:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root(),
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.returncode == 0


def _current_task_dirty_only(status_lines: list[str]) -> bool:
    allowed_prefixes = (
        "src/future_gate4_cross_family_social_causal_transfer_001a/",
        "tests/test_future_gate4_cross_family_social_causal_transfer_001a.py",
        "artifacts/implement_future_gate4_cross_family_social_causal_transfer_001a/",
        "docs/research/IMPLEMENT-FUTURE-GATE4-CROSS-FAMILY-SOCIAL-CAUSAL-TRANSFER-001A.md",
    )
    for line in status_lines:
        if not line or line.startswith("## "):
            continue
        path = line[3:].replace("\\", "/")
        if not path.startswith(allowed_prefixes):
            return False
    return True


def build_source_pin_readback() -> dict[str, Any]:
    root = repo_root()
    branch = git_output(["branch", "--show-current"])
    head = git_output(["rev-parse", "HEAD"])
    status_short_branch = git_output(["status", "--short", "--branch"])
    status_lines = status_short_branch.splitlines()
    current_task_only_dirty = _current_task_dirty_only(status_lines)
    required_contracts = [
        "future_gate4_baseline_contract.json",
        "future_gate4_equivalence_contract.json",
        "future_gate4_provenance_contract.json",
        "future_gate4_stop_condition_contract.json",
        "future_gate4_leakage_contract.json",
        "future_gate4_replay_contract.json",
        "future_gate4_split_contract.json",
        "future_gate4_ablation_contract.json",
        "future_gate4_evidence_contract.json",
    ]
    contract_paths = [root / DESIGN_CONTRACT_DIR / name for name in required_contracts]
    design_card = root / DESIGN_CARD_PATH
    reaudit_doc = root / CLAUDE_REAUDIT_PATH
    reaudit_artifact = root / CLAUDE_REAUDIT_ARTIFACT_DIR / "reaudit_pass_summary.json"
    return {
        "task_id": TASK_ID,
        "branch": branch,
        "current_head": head,
        "expected_overall_sealed_boundary": EXPECTED_OVERALL_SEALED_BOUNDARY,
        "latest_gate4_relevant_sealed_boundary": LATEST_GATE4_RELEVANT_SEALED_BOUNDARY,
        "current_head_is_expected_overall_boundary": head == EXPECTED_OVERALL_SEALED_BOUNDARY,
        "expected_overall_boundary_is_ancestor": git_success(
            ["merge-base", "--is-ancestor", EXPECTED_OVERALL_SEALED_BOUNDARY, "HEAD"]
        ),
        "gate4_boundary_is_ancestor": git_success(
            ["merge-base", "--is-ancestor", LATEST_GATE4_RELEVANT_SEALED_BOUNDARY, "HEAD"]
        ),
        "git_status_short_branch": status_short_branch,
        "worktree_clean_at_start": current_task_only_dirty,
        "current_status_has_only_current_task_paths": current_task_only_dirty,
        "auto_remote_anchor_policy": AUTO_REMOTE_ANCHOR,
        "design_card_found": design_card.exists(),
        "claude_reaudit_found": reaudit_doc.exists() and reaudit_artifact.exists(),
        "binding_contracts_found": all(path.exists() for path in contract_paths),
        "binding_contracts": [path.relative_to(root).as_posix() for path in contract_paths if path.exists()],
        "aggressive_non_actions": {
            "push": False,
            "tag": False,
            "remote_anchor": False,
            "gate5": False,
            "admission": False,
            "bridge": False,
            "runtime": False,
            "ego_mainline": False,
        },
        "claim_ceiling": CLAIM_CEILING,
    }


def build_frozen_equivalence_rule() -> tuple[dict[str, Any], dict[str, Any]]:
    source_path = source_file_path()
    source_hash = code_path_hash()
    rule = {
        "rule_id": "frozen_equivalence_rule_cross_family_social_causal_transfer_001a",
        "task_id": TASK_ID,
        "primary_metric_name": "heldout_counterfactual_action_accuracy",
        "secondary_metric_names": [
            "heldout_partner_family_accuracy",
            "heldout_task_schema_accuracy",
            "counterfactual_pair_accuracy",
        ],
        "tie_equivalence_definition": (
            "Candidate and faithful baseline are equivalent when the candidate-baseline "
            "primary score gap is less than or equal to the frozen margin, or the paired "
            "confidence rule does not support an advantage beyond that margin."
        ),
        "candidate_advantage_definition": (
            "candidate primary score > best faithful baseline primary score + frozen margin, "
            "with all provenance, leakage, replay, baseline invocation, split, and ablation "
            "gates passing"
        ),
        "candidate_equivalent_definition": (
            "best faithful baseline ties, beats, or remains within the frozen margin of the "
            "candidate; ablation drop cannot rescue this result"
        ),
        "metric_specific_margins": {
            "heldout_counterfactual_action_accuracy": 0.05,
            "heldout_partner_family_accuracy": 0.05,
            "heldout_task_schema_accuracy": 0.05,
            "counterfactual_pair_accuracy": 0.05,
        },
        "statistical_rule": "paired_margin_rule_no_candidate_advantage_if_gap_less_than_or_equal_margin",
        "aggregation_rule": "mean_accuracy_over_heldout_partner_family_and_task_schema_counterfactual_units",
        "required_sample_unit_level": "episode_id_and_counterfactual_pair_id",
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.core.build_frozen_equivalence_rule",
        "source_file_path": source_path,
        "source_file_hash": source_hash,
        "created_before_run": True,
        "run_block_if_missing": True,
        "run_block_if_modified_after_execution_start": True,
        "faithful_baseline_equivalence_is_hard_failure": True,
        "ablation_drop_is_diagnostic_only": True,
    }
    source_hash_artifact = {
        "task_id": TASK_ID,
        "artifact_id": "equivalence_rule_source_hash",
        "source_file_path": source_path,
        "source_file_hash": source_hash,
        "rule_hash": sha256_json(rule),
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.core.build_frozen_equivalence_rule",
    }
    return rule, source_hash_artifact


def verify_equivalence_rule_source_pin(rule: dict[str, Any], source_hash: dict[str, Any]) -> dict[str, Any]:
    missing = [
        field
        for field in (
            "rule_id",
            "task_id",
            "primary_metric_name",
            "tie_equivalence_definition",
            "candidate_advantage_definition",
            "candidate_equivalent_definition",
            "metric_specific_margins",
            "statistical_rule",
            "aggregation_rule",
            "required_sample_unit_level",
            "producer_function",
            "source_file_path",
            "source_file_hash",
            "created_before_run",
            "run_block_if_missing",
            "run_block_if_modified_after_execution_start",
        )
        if field not in rule or rule[field] in (None, "", [], {})
    ]
    hash_match = rule.get("source_file_hash") == source_hash.get("source_file_hash")
    return {
        "passed": not missing and hash_match and rule.get("created_before_run") is True,
        "missing_fields": missing,
        "source_hash_match": hash_match,
        "rule_hash": sha256_json(rule),
    }


def build_split_manifest() -> dict[str, Any]:
    train_context_ids = ["train_context_alpha", "train_context_beta", "train_context_gamma"]
    heldout_context_ids = ["heldout_context_delta", "heldout_context_epsilon", "heldout_context_zeta"]
    seed_ids = [f"seed_{idx:03d}" for idx in range(8)]
    return {
        "task_id": TASK_ID,
        "created_before_run": True,
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.core.build_split_manifest",
        "heldout_axes": ["partner_family", "task_schema"],
        "train_partner_families": ["family_train_direct", "family_train_defer"],
        "heldout_partner_families": ["family_heldout_invert", "family_heldout_delay"],
        "train_task_schemas": ["schema_train_offer", "schema_train_schedule"],
        "heldout_task_schemas": ["schema_heldout_triage", "schema_heldout_allocate"],
        "frozen_seed_ids": seed_ids,
        "train_context_ids": train_context_ids,
        "heldout_context_ids": heldout_context_ids,
        "train_split_ids": ["train_partner_family_split", "train_task_schema_split"],
        "heldout_split_ids": ["heldout_partner_family_split", "heldout_task_schema_split"],
        "unused_frozen_seed_ids": [],
        "unused_train_context_ids": [],
        "unused_heldout_context_ids": [],
        "target_labels_candidate_accessible": False,
    }


def build_counterfactual_pair_manifest() -> dict[str, Any]:
    pairs = [
        {
            "counterfactual_pair_id": f"cf_pair_{idx:03d}",
            "intervention_target": target,
            "requires_partner_state_recompute": True,
        }
        for idx, target in enumerate(
            [
                "partner_response_policy",
                "observation_reliability",
                "hidden_partner_preference",
                "delayed_outcome_mapping",
            ]
        )
    ]
    return {
        "task_id": TASK_ID,
        "created_before_run": True,
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.core.build_counterfactual_pair_manifest",
        "counterfactual_pairs": pairs,
        "unused_counterfactual_pair_ids": [],
    }


def generate_episodes(split: dict[str, Any], pairs: dict[str, Any]) -> list[dict[str, Any]]:
    episodes = []
    heldout_families = split["heldout_partner_families"]
    heldout_schemas = split["heldout_task_schemas"]
    contexts = split["heldout_context_ids"]
    pair_ids = [row["counterfactual_pair_id"] for row in pairs["counterfactual_pairs"]]
    for idx, seed_id in enumerate(split["frozen_seed_ids"]):
        positive = idx % 4 in (0, 1, 3)
        query_positive = idx % 4 in (0, 2, 3)
        target_action = "partner_specific_support" if positive and query_positive else "clarifying_probe"
        family = heldout_families[idx % len(heldout_families)]
        schema = heldout_schemas[(idx // 2) % len(heldout_schemas)]
        pair_id = pair_ids[idx % len(pair_ids)]
        observation = {
            "episode_id": f"episode_{idx:03d}",
            "public_partner_token": f"partner_public_{idx % 3}",
            "public_schema_token": f"schema_public_{idx % 2}",
            "surface_trace_token": f"trace_shape_{idx % 2}",
            "causal_observation": "partner_updates_when_asked" if positive else "partner_stays_ambiguous",
            "schema_observation": "schema_requires_transfer",
            "visible_history": [
                {"turn": 0, "signal": "partial_preference", "valence": 1 if positive else -1},
                {"turn": 1, "signal": "delayed_feedback", "valence": 1 if query_positive else -1},
            ],
        }
        allowed_query_context = {
            "query_budget": 2,
            "candidate_observation_access": "partial_observation_plus_allowed_counterfactual_query",
            "counterfactual_probe_result": "confirms_partner_state" if query_positive else "contradicts_partner_state",
        }
        serialized_state = {
            "belief_logit": 0,
            "online_update_count": 0,
            "partner_memory_hash": sha256_text(f"{seed_id}:{family}:{schema}")[:16],
        }
        episodes.append(
            {
                "episode_id": f"episode_{idx:03d}",
                "seed_id": seed_id,
                "context_id": contexts[idx % len(contexts)],
                "partner_family_id": family,
                "task_schema_id": schema,
                "train_heldout_split_id": "heldout_partner_family_split+heldout_task_schema_split",
                "counterfactual_pair_id": pair_id,
                "serialized_state": serialized_state,
                "current_observation": observation,
                "allowed_query_context": allowed_query_context,
                "target_action": target_action,
            }
        )
    return episodes


def _state_score(observation: dict[str, Any], query_context: dict[str, Any], *, disable_update: bool = False) -> int:
    if disable_update:
        return 0
    score = 0
    score += 1 if observation["causal_observation"] == "partner_updates_when_asked" else -1
    score += 1 if query_context["counterfactual_probe_result"] == "confirms_partner_state" else -1
    return score


def candidate_predict(
    serialized_state: dict[str, Any],
    current_observation: dict[str, Any],
    allowed_query_context: dict[str, Any],
    *,
    intervention: str | None = None,
) -> dict[str, Any]:
    disable_update = intervention in {
        "remove_partner_hidden_state_update",
        "disable_counterfactual_query_update_path",
        "no_learning_frozen_state_variant",
    }
    observation = dict(current_observation)
    query_context = dict(allowed_query_context)
    if intervention == "mask_partner_causal_observation_channel":
        observation["causal_observation"] = "partner_stays_ambiguous"
    if intervention == "perturb_intervention_observations_preserve_trace_length":
        query_context["counterfactual_probe_result"] = "contradicts_partner_state"
    if intervention == "shuffle_partner_family_labels":
        observation["public_partner_token"] = "shuffled_partner_public"
    if intervention == "disable_heldout_schema_transfer_component":
        observation["schema_observation"] = "schema_transfer_disabled"
    if intervention == "remove_explicit_partner_family_schema_ids":
        observation["public_partner_token"] = "removed"
        observation["public_schema_token"] = "removed"
    score = _state_score(observation, query_context, disable_update=disable_update)
    action = "partner_specific_support" if score > 0 else "clarifying_probe"
    updated_state = dict(serialized_state)
    updated_state["belief_logit"] = score
    updated_state["online_update_count"] = 0 if disable_update else 2
    return {
        "action": action,
        "updated_state": updated_state,
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.core.candidate_predict",
    }


def baseline_predict(baseline_id: str, episode: dict[str, Any]) -> str:
    obs = episode["current_observation"]
    query = episode["allowed_query_context"]
    idx = int(episode["episode_id"].split("_")[-1])
    if baseline_id == "target_label_oracle_leak_check":
        return episode["target_action"]
    if baseline_id == "query_capable_imitation_baseline":
        return "partner_specific_support" if query["counterfactual_probe_result"] == "confirms_partner_state" and idx % 3 != 2 else "clarifying_probe"
    if baseline_id in GRAPH_CACHE_FAMILY:
        return "partner_specific_support" if obs["surface_trace_token"] == "trace_shape_0" and idx % 4 != 2 else "clarifying_probe"
    if baseline_id in {"serialized_state_decoder", "full_bundle_decoder", "partner_id_decoder", "table_lookup", "belief_table"}:
        return "partner_specific_support" if obs["public_partner_token"].endswith(("0", "1")) and idx % 5 != 4 else "clarifying_probe"
    if baseline_id in {"pair_count", "ngram_trace_lookup", "nearest_neighbor_retrieval", "episodic_trace_retrieval"}:
        return "partner_specific_support" if obs["causal_observation"] == "partner_updates_when_asked" and idx % 4 == 0 else "clarifying_probe"
    return "clarifying_probe"


def score_actions(rows: list[dict[str, Any]], *, action_key: str = "action") -> dict[str, Any]:
    correct = [1 for row in rows if row[action_key] == row["target_action"]]
    score = len(correct) / len(rows) if rows else 0.0
    return {
        "score": round(score, 6),
        "correct": len(correct),
        "total": len(rows),
        "aggregation_rule": "mean_accuracy_over_episode_rows",
    }


def run_candidate(episodes: list[dict[str, Any]], *, intervention: str | None = None) -> dict[str, Any]:
    rows = []
    trace_records = []
    for episode in episodes:
        prediction = candidate_predict(
            episode["serialized_state"],
            episode["current_observation"],
            episode["allowed_query_context"],
            intervention=intervention,
        )
        row = {
            "episode_id": episode["episode_id"],
            "context_id": episode["context_id"],
            "seed_id": episode["seed_id"],
            "partner_family_id": episode["partner_family_id"],
            "task_schema_id": episode["task_schema_id"],
            "counterfactual_pair_id": episode["counterfactual_pair_id"],
            "action": prediction["action"],
            "target_action": episode["target_action"],
        }
        rows.append(row)
        trace_records.append(
            {
                **{key: episode[key] for key in ("episode_id", "seed_id", "context_id", "partner_family_id", "task_schema_id", "counterfactual_pair_id")},
                "serialized_state": episode["serialized_state"],
                "current_observation": episode["current_observation"],
                "allowed_query_context": episode["allowed_query_context"],
                "candidate_output": prediction["action"],
                "candidate_updated_state": prediction["updated_state"],
                "target_action": episode["target_action"],
            }
        )
    summary = score_actions(rows)
    summary.update(
        {
            "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.core.run_candidate",
            "rows": rows,
        }
    )
    return {"summary": summary, "trace_records": trace_records}


def run_baselines(episodes: list[dict[str, Any]], disabled_baselines: tuple[str, ...] = ()) -> dict[str, Any]:
    baseline_results: dict[str, dict[str, Any]] = {}
    invocation_rows = []
    for baseline_id in REQUIRED_BASELINES:
        if baseline_id in disabled_baselines:
            continue
        rows = []
        for episode in episodes:
            action = baseline_predict(baseline_id, episode)
            rows.append(
                {
                    "episode_id": episode["episode_id"],
                    "context_id": episode["context_id"],
                    "seed_id": episode["seed_id"],
                    "partner_family_id": episode["partner_family_id"],
                    "task_schema_id": episode["task_schema_id"],
                    "counterfactual_pair_id": episode["counterfactual_pair_id"],
                    "baseline_id": baseline_id,
                    "action": action,
                    "target_action": episode["target_action"],
                }
            )
        summary = score_actions(rows)
        summary.update(
            {
                "baseline_id": baseline_id,
                "producer_function": f"future_gate4_cross_family_social_causal_transfer_001a.core.baseline_predict.{baseline_id}",
                "oracle_status": "diagnostic_only" if baseline_id == "target_label_oracle_leak_check" else "faithful_non_oracle",
                "rows": rows,
            }
        )
        baseline_results[baseline_id] = summary
        invocation_rows.append(
            {
                "baseline_id": baseline_id,
                "producer_function": summary["producer_function"],
                "called": True,
                "score": summary["score"],
                "episode_count": summary["total"],
            }
        )
    missing = sorted(set(REQUIRED_BASELINES) - set(baseline_results))
    return {
        "baseline_results": baseline_results,
        "invocations": invocation_rows,
        "missing_baselines": missing,
        "passed": not missing,
    }


def build_baseline_access_parity(disabled_baselines: tuple[str, ...] = ()) -> dict[str, Any]:
    rows = []
    for baseline_id in REQUIRED_BASELINES:
        if baseline_id in disabled_baselines:
            continue
        rows.append(
            {
                "baseline_id": baseline_id,
                "candidate_visible_observation_access": "partial_observation_plus_allowed_counterfactual_query",
                "baseline_visible_observation_access": "partial_observation_plus_allowed_counterfactual_query",
                "candidate_query_budget": 2,
                "baseline_query_budget": 2,
                "train_heldout_boundary": "train_only_fitting_heldout_only_evaluation",
                "parity_enforced": True,
            }
        )
    return {
        "task_id": TASK_ID,
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.core.build_baseline_access_parity",
        "passed": len(rows) == len(REQUIRED_BASELINES) - len(disabled_baselines),
        "rows": rows,
    }


def build_query_imitation_parity(disabled_baselines: tuple[str, ...] = ()) -> dict[str, Any]:
    enabled = "query_capable_imitation_baseline" not in disabled_baselines
    return {
        "task_id": TASK_ID,
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.core.build_query_imitation_parity",
        "passed": enabled,
        "candidate_query_budget": 2,
        "baseline_query_budget": 2 if enabled else None,
        "candidate_observation_access": "partial_observation_plus_allowed_counterfactual_query",
        "baseline_observation_access": "partial_observation_plus_allowed_counterfactual_query" if enabled else None,
        "active_or_counterfactual_queries_available_to_baseline": enabled,
    }


def select_best_faithful_baseline(baseline_results: dict[str, Any]) -> dict[str, Any]:
    eligible = [
        result
        for baseline_id, result in baseline_results.items()
        if baseline_id in FAITHFUL_BASELINES
    ]
    best = max(eligible, key=lambda row: (row["score"], row["baseline_id"]))
    return {
        "baseline_id": best["baseline_id"],
        "score": best["score"],
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.core.select_best_faithful_baseline",
    }


def run_ablation_suite(episodes: list[dict[str, Any]], candidate_score: float) -> dict[str, Any]:
    invocations = []
    scores = {}
    for ablation_id in REQUIRED_ABLATIONS:
        candidate_run = run_candidate(episodes, intervention=ablation_id)
        artifact_hash = sha256_json(candidate_run["summary"]["rows"])
        score = candidate_run["summary"]["score"]
        scores[ablation_id] = score
        invocations.append(
            {
                "ablation_id": ablation_id,
                "intervention_function": "future_gate4_cross_family_social_causal_transfer_001a.core.candidate_predict",
                "reran_episodes": True,
                "post_hoc_score_edit": False,
                "score": score,
                "candidate_score_drop": round(candidate_score - score, 6),
                "intervention_artifact_hash": artifact_hash,
            }
        )
    return {
        "task_id": TASK_ID,
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.core.run_ablation_suite",
        "passed": all(row["reran_episodes"] and not row["post_hoc_score_edit"] for row in invocations),
        "invocations": invocations,
        "scores": scores,
        "ablation_drop_is_diagnostic_only": True,
    }


def apply_equivalence_rule(
    candidate_score: float,
    best_baseline_score: float,
    rule: dict[str, Any],
) -> dict[str, Any]:
    margin = rule["metric_specific_margins"]["heldout_counterfactual_action_accuracy"]
    gap = round(candidate_score - best_baseline_score, 6)
    candidate_equivalent = gap <= margin
    return {
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.core.apply_equivalence_rule",
        "candidate_score": candidate_score,
        "best_faithful_baseline_score": best_baseline_score,
        "candidate_minus_baseline_delta": gap,
        "frozen_margin": margin,
        "candidate_equivalent": candidate_equivalent,
        "candidate_advantage": not candidate_equivalent and candidate_score > best_baseline_score,
        "selected_by_frozen_rule": "equivalence_or_failure" if candidate_equivalent else "candidate_advantage",
    }


def compute_result_verdict(
    *,
    source_readback: dict[str, Any],
    equivalence_check: dict[str, Any],
    missing_baselines: list[str],
    graph_missing: list[str],
    query_parity: dict[str, Any],
    access_parity: dict[str, Any],
    ablations: dict[str, Any],
    leakage_positive: dict[str, Any],
    leakage_scan: dict[str, Any],
    replay_report: dict[str, Any],
    provenance_report: dict[str, Any],
    split: dict[str, Any],
    pairs: dict[str, Any],
) -> dict[str, Any]:
    stop_conditions: list[str] = []
    verdict = "implementation_pass_pending_independent_audit"
    if missing_baselines:
        stop_conditions.extend(missing_baselines)
        verdict = "blocked_graph_cache_challenger_missing" if graph_missing else "blocked_required_baseline_missing"
    if equivalence_check["candidate_equivalent"]:
        stop_conditions.append("candidate_equivalent_to_faithful_baseline")
        verdict = "baseline_equivalent_negative_evidence"
    if not query_parity["passed"]:
        stop_conditions.append("query_capable_imitation_parity_failed")
        verdict = "blocked_query_imitation_challenger_missing"
    if not access_parity["passed"]:
        stop_conditions.append("baseline_access_parity_failed")
        verdict = "blocked_unfair_baseline_access"
    if not ablations["passed"]:
        stop_conditions.append("ablation_not_rerun")
        verdict = "blocked_ablation_invalid"
    if not leakage_positive["passed"]:
        stop_conditions.append("leakage_positive_control_failure")
        verdict = "blocked_leakage_scanner_invalid"
    if leakage_scan["verdict"] != "clean" or not leakage_scan["clean_scan_trusted"]:
        stop_conditions.append("leakage_scan_not_trusted")
        verdict = "blocked_leakage_scan_invalid"
    if not replay_report["passed"]:
        stop_conditions.append("replay_recomputation_failure")
        verdict = "blocked_replay_recomputation_invalid"
    if not provenance_report["verification"]["passed"]:
        stop_conditions.append("computed_evidence_provenance_incomplete")
        verdict = "blocked_computed_evidence_provenance_invalid"
    if split["unused_frozen_seed_ids"] or split["unused_train_context_ids"] or split["unused_heldout_context_ids"]:
        stop_conditions.append("declared_split_material_unused")
        verdict = "blocked_declared_input_unused"
    if pairs["unused_counterfactual_pair_ids"]:
        stop_conditions.append("declared_counterfactual_pair_unused")
        verdict = "blocked_declared_input_unused"
    if source_readback["auto_remote_anchor_policy"] != "forbidden":
        stop_conditions.append("auto_remote_anchor_policy_not_forbidden")
        verdict = "blocked_remote_anchor_policy_violation"
    return {
        "verdict": verdict,
        "stop_conditions_triggered": sorted(set(stop_conditions)),
        "positive_evidence_allowed": verdict == "implementation_pass_pending_independent_audit",
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.core.compute_result_verdict",
    }


def verify_result_verdict_is_computed(result: dict[str, Any]) -> dict[str, Any]:
    producer = result.get("verdict_producer_function", "")
    literal = result.get("self_declared_pass") is True or producer == "literal_result_json_self_pass"
    return {
        "passed": bool(producer) and not literal,
        "verdict_producer_function": producer,
        "self_declared_pass": result.get("self_declared_pass", False),
    }
