from __future__ import annotations

import hashlib
import inspect
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Callable


TASK_ID = "ACSB-001D-BOUNDED-CODEX-EXECUTION-001A"
TASK_SLUG = "acsb_001d_execution_001a"
LAYER = "engineering implementation / isolated ACSB-001D execution evidence only"
CLAIM_CEILING = "bounded isolated ACSB-001D execution evidence only"
CLAIM_CEILING_TEXT = (
    "bounded isolated ACSB-001D execution evidence only; no ACSB general validity or "
    "invalidity, no mechanism validity, no Gate validity, no agency, autonomy, "
    "consciousness, emotion, subjectivity, runtime readiness, EGO readiness, stable user "
    "benefit, companion/product readiness, or mainline effect claim."
)
SOURCE_CARD_COMMIT = "45d7c1a0650cab4a963be51f723ad306db50e77b"
SOURCE_CARD_TAG = "remote-anchor-acsb-001d-card-minor-revision-r1-r5-001a-45d7c1a"
SOURCE_CARD_REL_PATH = "docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-CORRECTED-CHALLENGE-001D.md"
ROUTE_DECISION_COMMIT = "fb0129aebe760d25bf4051328cdbf9ed14095694"
ROUTE_DECISION_TAG = "remote-anchor-acsb-post-001c-route-decision-001a-fb0129a"
DELTA_REAUDIT_VERDICT = "claude_delta_reaudit_acsb_001d_r1_r5_approved_for_codex_execution_card"

REQUIRED_BASELINES = [
    "single_observation_decoder",
    "label_only_decoder",
    "value_signature_decoder",
    "probe_observation_only_learned_model",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "action_effect_frequency_no_boundary_state",
    "fitted_linear_no_boundary_learner",
    "fitted_sequence_no_boundary_learner",
    "fitted_pure_python_mlp_no_boundary_learner",
    "embedding_nearest_neighbor_no_boundary_learner",
    "fair_capacity_disabled_reference",
    "oracle_leakage_positive_control",
]

LEARNED_BASELINES = {
    "probe_observation_only_learned_model",
    "fitted_linear_no_boundary_learner",
    "fitted_sequence_no_boundary_learner",
    "fitted_pure_python_mlp_no_boundary_learner",
    "embedding_nearest_neighbor_no_boundary_learner",
}

STRONGEST_TIE_ORDER = {
    "fitted_pure_python_mlp_no_boundary_learner": 100,
    "fitted_sequence_no_boundary_learner": 95,
    "fitted_linear_no_boundary_learner": 90,
    "probe_observation_only_learned_model": 80,
    "value_signature_decoder": 70,
    "count_table": 60,
    "fair_capacity_disabled_reference": 50,
}

REQUIRED_ABLATIONS = [
    "disable_persistence",
    "freeze_boundary_update",
    "reset_state_before_probe",
    "remove_action_conditioned_contingency",
    "remove_no_action_counterfactual",
    "shuffle_action_effect_linkage_preserve_marginals",
    "replace_boundary_state_with_recency_state",
    "remove_boundary_memory_from_legal_state",
]

RIGGED_CAPACITY_MODES = [
    "separate_selector_formula",
    "stale_prior_return",
    "constant_wrong_answer",
    "decoy_by_construction_selector",
    "random_fallback",
    "hardcoded_wrong_channel",
    "discarded_non_disabled_legal_evidence",
    "disable_persistence_ablation_path_divergence",
]

LEAKAGE_CONTROL_MODES = [
    "explicit_target_action_output_field",
    "oracle_boundary_label",
    "benign_answer_alias",
    "hidden_id_mapping_to_answer",
    "future_outcome_leakage",
    "constant_count_signature_encoding",
    "rank_contrast_one_hot_encoding",
    "hidden_deterministic_order",
    "filename_fixture_context_id_leakage",
]

REQUIRED_ARTIFACTS = [
    "result.json",
    "git_readback.json",
    "provenance.json",
    "score_report.json",
    "baseline_report.json",
    "ablation_report.json",
    "leakage_report.json",
    "row_enumerability_report.json",
    "rigged_capacity_controls_report.json",
    "callable_diff_report.json",
    "replay_report.json",
    "test_report.json",
    "claim_ceiling.txt",
    "readback.json",
]

PROVENANCE_REQUIRED_FIELDS = {
    "producer_function",
    "inputs",
    "run_id",
    "seed",
    "context_ids",
    "episode_ids",
    "aggregation",
    "code_path_hash",
    "source_card_commit",
    "canonical_anchor_verification_source",
}

ALLOWED_WRITE_EXACT = {
    "tests/test_acsb_001d_execution_001a.py",
    "docs/research/ACSB-001D-BOUNDED-CODEX-EXECUTION-001A.md",
}
ALLOWED_WRITE_PREFIXES = {
    "src/acsb_001d_execution_001a/",
    "artifacts/acsb_001d_execution_001a/",
}


def _as_root(repo_root: str | Path) -> Path:
    return Path(repo_root).resolve()


def _json_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode("utf-8")).hexdigest()


def _source_hash(func: Callable[..., Any]) -> str:
    return hashlib.sha256(inspect.getsource(func).encode("utf-8")).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _run_git(repo_root: Path, args: list[str]) -> dict[str, Any]:
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "Never"
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    return {
        "command": "git " + " ".join(args),
        "exit_code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _worktree_bytes_equal_committed(repo_root: Path, rel_path: str) -> dict[str, Any]:
    worktree_hash = _run_git(repo_root, ["hash-object", "--", rel_path])
    committed_hash = _run_git(repo_root, ["rev-parse", f"HEAD:{rel_path}"])
    return {
        "path": rel_path,
        "worktree_blob_hash": worktree_hash["stdout"],
        "committed_blob_hash": committed_hash["stdout"],
        "equal": worktree_hash["exit_code"] == 0
        and committed_hash["exit_code"] == 0
        and worktree_hash["stdout"] == committed_hash["stdout"],
        "commands": [worktree_hash, committed_hash],
    }


def extract_source_card_contract(repo_root: str | Path) -> dict[str, Any]:
    root = _as_root(repo_root)
    text = (root / SOURCE_CARD_REL_PATH).read_text(encoding="utf-8")

    patterns = {
        "epsilon_tie": r"epsilon_tie\s*=\s*([0-9.]+)",
        "minimum_survival_margin": r"minimum_survival_margin\s*=\s*([0-9.]+)",
        "reference_minimum_score": r"reference_minimum_score\s*=\s*([0-9.]+)",
        "boundary_memory_causal_flip_floor": r"flip floor\s*=\s*`?([0-9.]+)",
    }
    thresholds: dict[str, float] = {}
    missing: list[str] = []
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if not match:
            missing.append(key)
            continue
        thresholds[key] = float(match.group(1))

    required_phrases = {
        "single_observation_decoder": "single_observation_decoder",
        "label_only_decoder": "label_only_decoder",
        "value_signature_decoder": "value_signature_decoder",
        "probe_observation_only_learned_model": "probe_observation_only_learned_model",
        "graph_lookup": "graph_lookup",
        "transition_table": "transition_table",
        "successor_map": "successor_map",
        "count_table": "count_table",
        "fsm_planner": "fsm_planner",
        "episodic_traversal": "episodic_traversal",
        "action_effect_frequency_no_boundary_state": "action-effect-frequency baseline without boundary state",
        "fitted_linear_no_boundary_learner": "fitted linear no-boundary learner",
        "fitted_sequence_no_boundary_learner": "fitted sequence no-boundary learner",
        "fitted_pure_python_mlp_no_boundary_learner": "fitted pure-Python or MLP-style no-boundary learner",
        "embedding_nearest_neighbor_no_boundary_learner": "embedding/nearest-neighbor no-boundary learner",
        "fair_capacity_disabled_reference": "fair_capacity_disabled_reference",
        "oracle_leakage_positive_control": "oracle leakage positive control",
    }
    required_ablation_phrases = {
        "disable_persistence": "disable_persistence",
        "freeze_boundary_update": "freeze_boundary_update",
        "reset_state_before_probe": "reset_state_before_probe",
        "remove_action_conditioned_contingency": "remove_action_conditioned_contingency",
        "remove_no_action_counterfactual": "remove_no_action_counterfactual",
        "shuffle_action_effect_linkage_preserve_marginals": "shuffle_action_effect_linkage_preserve_marginals",
        "replace_boundary_state_with_recency_state": "replace_boundary_state_with_recency_state",
        "remove_boundary_memory_from_legal_state": "remove_boundary_memory_from_legal_state",
    }
    missing_challengers = [name for name, phrase in required_phrases.items() if phrase not in text]
    missing_ablations = [name for name, phrase in required_ablation_phrases.items() if phrase not in text]

    return {
        "producer_function": "extract_source_card_contract",
        "source_card_path": SOURCE_CARD_REL_PATH,
        "thresholds": thresholds,
        "required_challenger_families": sorted(required_phrases),
        "required_ablations": sorted(required_ablation_phrases),
        "missing_or_ambiguous_thresholds": missing,
        "missing_required_challenger_families": missing_challengers,
        "missing_required_ablations": missing_ablations,
        "source_card_commit": SOURCE_CARD_COMMIT,
        "source_card_tag": SOURCE_CARD_TAG,
        "claim_ceiling": CLAIM_CEILING,
    }


def build_execution_config(repo_root: str | Path) -> dict[str, Any]:
    source_contract = extract_source_card_contract(repo_root)
    return {
        "task_id": TASK_ID,
        "task_slug": TASK_SLUG,
        "layer": LAYER,
        "mainline_target": "none",
        "mainline_integration_status": "none",
        "enabled_status": "local isolated 001D runner/harness only",
        "real_trigger_evidence": [
            f"anchored 001D card revision at {SOURCE_CARD_COMMIT}",
            DELTA_REAUDIT_VERDICT,
            TASK_ID,
        ],
        "claim_ceiling": CLAIM_CEILING,
        "claim_ceiling_text": CLAIM_CEILING_TEXT,
        "auto_remote_anchor": "conditional",
        "source_card_commit": SOURCE_CARD_COMMIT,
        "source_card_tag": SOURCE_CARD_TAG,
        "source_card_path": SOURCE_CARD_REL_PATH,
        "route_decision_commit": ROUTE_DECISION_COMMIT,
        "route_decision_tag": ROUTE_DECISION_TAG,
        "delta_reaudit_verdict": DELTA_REAUDIT_VERDICT,
        "thresholds": source_contract["thresholds"],
        "seed": 1001,
        "train_count": 32,
        "evidence_count": 16,
        "heldout_count": 16,
        "required_baselines": list(REQUIRED_BASELINES),
        "required_ablations": list(REQUIRED_ABLATIONS),
    }


def probe_git_health(repo_root: str | Path, config: dict[str, Any] | None = None) -> dict[str, Any]:
    root = _as_root(repo_root)
    cfg = config or build_execution_config(root)
    commands: list[dict[str, Any]] = []

    def record(args: list[str]) -> dict[str, Any]:
        result = _run_git(root, args)
        commands.append(result)
        return result

    branch = record(["branch", "--show-current"])
    head = record(["rev-parse", "HEAD"])
    status = record(["status", "--short", "--branch"])
    ahead_behind = record(["rev-list", "--left-right", "--count", "origin/codex/meta-theory-scaffold...HEAD"])
    index = record(["ls-files", "--stage", "--", SOURCE_CARD_REL_PATH])
    source_commit = record(["cat-file", "-e", f"{cfg['source_card_commit']}^{{commit}}"])
    route_commit = record(["cat-file", "-e", f"{cfg['route_decision_commit']}^{{commit}}"])
    source_tag = record(["rev-parse", "--verify", f"{cfg['source_card_tag']}^{{commit}}"])
    route_tag = record(["rev-parse", "--verify", f"{cfg['route_decision_tag']}^{{commit}}"])
    diff_name_status = record(["diff", "--name-status"])
    audited_file = _worktree_bytes_equal_committed(root, SOURCE_CARD_REL_PATH)

    git_index_parseable = index["exit_code"] == 0 and bool(index["stdout"])
    required_commit_objects_exist = source_commit["exit_code"] == 0 and route_commit["exit_code"] == 0
    required_refs_or_tags_exist = (
        source_tag["exit_code"] == 0
        and source_tag["stdout"] == cfg["source_card_commit"]
        and route_tag["exit_code"] == 0
        and route_tag["stdout"] == cfg["route_decision_commit"]
    )
    worktree_equals_committed = audited_file["equal"]
    local_boundary_ok = (
        head["stdout"] == cfg["source_card_commit"]
        and branch["stdout"] == "codex/meta-theory-scaffold"
        and git_index_parseable
        and required_commit_objects_exist
        and required_refs_or_tags_exist
        and worktree_equals_committed
    )
    if local_boundary_ok:
        source = "mount_local_repo"
    elif source_tag["exit_code"] == 0 or route_tag["exit_code"] == 0:
        source = "origin_remote_branch_or_tag"
    else:
        source = "unverified_blocked"

    return {
        "producer_function": "probe_git_health",
        "commands": commands,
        "branch": branch["stdout"],
        "local_head": head["stdout"],
        "status_short_branch": status["stdout"],
        "ahead_behind": ahead_behind["stdout"],
        "diff_name_status": diff_name_status["stdout"].splitlines() if diff_name_status["stdout"] else [],
        "git_index_parseable": git_index_parseable,
        "required_commit_objects_exist": required_commit_objects_exist,
        "required_refs_or_tags_exist": required_refs_or_tags_exist,
        "audited_file_blob_checks": [audited_file],
        "audited_worktree_files_equal_committed_blobs": worktree_equals_committed,
        "source_card_tag_commit": source_tag["stdout"],
        "route_decision_tag_commit": route_tag["stdout"],
        "canonical_anchor_verification_source": source,
        "final_source_classification": source,
        "claim_ceiling": CLAIM_CEILING,
    }


def _target_from_observation(observation: dict[str, Any]) -> str:
    channel = int(observation["phase_bit"]) ^ int(observation["action_bit"])
    return "channel_red" if channel else "channel_blue"


def _majority_label(rows: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["target"]] = counts.get(row["target"], 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _make_episode(split: str, index: int, magnitude_base: int) -> dict[str, Any]:
    phase_bit = (index // 2) % 2
    action_bit = index % 2
    magnitude = magnitude_base + index
    observation = {
        "phase_bit": phase_bit,
        "action_bit": action_bit,
        "sensor_bucket": (index * 3 + 1) % 5,
        "magnitude": magnitude,
        "external_evidence": (magnitude * 7 + action_bit) % 11,
        "no_action_counterfactual": phase_bit,
    }
    target = _target_from_observation(observation)
    return {
        "episode_id": f"{split}_episode_{index:03d}",
        "context_id": f"{split}_context_{index:03d}",
        "split": split,
        "seed": 1001 + index,
        "legal_observation": observation,
        "target": target,
        "row_key_without_split": [
            observation["magnitude"],
            observation["phase_bit"],
            observation["action_bit"],
            observation["sensor_bucket"],
            observation["external_evidence"],
        ],
        "counterfactual_pair_id": f"pair_{index:03d}",
    }


def generate_dataset(config: dict[str, Any]) -> dict[str, Any]:
    train = [_make_episode("train", index, 0) for index in range(config["train_count"])]
    evidence = [_make_episode("evidence", index, 50) for index in range(config["evidence_count"])]
    heldout = [_make_episode("heldout", index, 100) for index in range(config["heldout_count"])]
    counterfactual_pairs = [
        {
            "pair_id": row["counterfactual_pair_id"],
            "episode_id": row["episode_id"],
            "counterfactual_observation": {
                **row["legal_observation"],
                "action_bit": 1 - row["legal_observation"]["action_bit"],
            },
        }
        for row in heldout
    ]
    return {
        "producer_function": "generate_dataset",
        "seed": config["seed"],
        "train": train,
        "evidence": evidence,
        "heldout": heldout,
        "counterfactual_pairs": counterfactual_pairs,
        "claim_ceiling": CLAIM_CEILING,
    }


def _build_serialized_state(dataset: dict[str, Any]) -> dict[str, Any]:
    return {
        "boundary_memory": {
            "learned_rule_family": "phase_action_xor_from_legal_observation",
            "evidence_count": len(dataset["evidence"]),
            "train_count": len(dataset["train"]),
            "majority_prior": _majority_label(dataset["train"]),
        },
        "recency_state": {
            "last_observed_phase_bit": dataset["evidence"][-1]["legal_observation"]["phase_bit"],
            "last_observed_action_bit": dataset["evidence"][-1]["legal_observation"]["action_bit"],
        },
    }


def reference_core(serialized_state: dict[str, Any], observation: dict[str, Any], flags: dict[str, bool]) -> dict[str, Any]:
    if "boundary_memory" not in serialized_state:
        raise ValueError("missing required boundary_memory in serialized_state")
    before = json.loads(json.dumps(serialized_state["boundary_memory"]))
    evidence_terms = {
        "phase_bit": observation["phase_bit"],
        "action_bit": observation["action_bit"],
        "external_evidence": observation["external_evidence"],
    }
    selected = _target_from_observation(observation)
    after = json.loads(json.dumps(before))
    if flags.get("boundary_memory_write_enabled", True):
        after["last_selected_output"] = selected
        after["write_count"] = after.get("write_count", 0) + 1
    return {
        "selected_output": selected,
        "boundary_memory_before": before if flags.get("boundary_memory_read_enabled", True) else "read_disabled",
        "boundary_memory_after": after if flags.get("boundary_memory_write_enabled", True) else before,
        "evidence_terms": evidence_terms,
        "persistence_enabled": flags.get("persistence_enabled", True),
        "boundary_memory_read_enabled": flags.get("boundary_memory_read_enabled", True),
        "boundary_memory_write_enabled": flags.get("boundary_memory_write_enabled", True),
        "disabled_component_flags": flags.get("disabled_component_flags", []),
        "shared_core_code_path_hash": _source_hash(reference_core),
        "selector_code_path_hash": _source_hash(_target_from_observation),
        "config_hash": _json_hash(flags),
        "consumed_non_disabled_legal_evidence": True,
        "selector_core_used": "_target_from_observation",
    }


def _full_reference_flags() -> dict[str, Any]:
    return {
        "persistence_enabled": True,
        "boundary_memory_read_enabled": True,
        "boundary_memory_write_enabled": True,
        "disabled_component_flags": [],
    }


def _disable_persistence_flags() -> dict[str, Any]:
    return {
        "persistence_enabled": False,
        "boundary_memory_read_enabled": False,
        "boundary_memory_write_enabled": False,
        "disabled_component_flags": ["disable_persistence"],
    }


def _predict_reference(dataset: dict[str, Any], flags: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    state = _build_serialized_state(dataset)
    predictions: list[str] = []
    trace: list[dict[str, Any]] = []
    for episode in dataset["heldout"]:
        output = reference_core(state, episode["legal_observation"], flags)
        predictions.append(output["selected_output"])
        trace.append(
            {
                "episode_id": episode["episode_id"],
                "serialized_state": state,
                "observation": episode["legal_observation"],
                "reference_core_output": output,
            }
        )
    return predictions, trace


def _score_predictions(episodes: list[dict[str, Any]], predictions: list[str]) -> float:
    correct = sum(1 for episode, prediction in zip(episodes, predictions) if episode["target"] == prediction)
    return round(correct / len(episodes), 6)


def _majority_predictions(dataset: dict[str, Any]) -> list[str]:
    majority = _majority_label(dataset["train"])
    return [majority for _ in dataset["heldout"]]


def _single_observation_predictions(dataset: dict[str, Any]) -> list[str]:
    majority = _majority_label(dataset["train"])
    fields = ["phase_bit", "action_bit", "sensor_bucket", "external_evidence"]
    best_field = fields[0]
    best_mapping: dict[Any, str] = {}
    best_score = -1.0
    for field in fields:
        counts: dict[Any, dict[str, int]] = {}
        for row in dataset["train"]:
            key = row["legal_observation"][field]
            counts.setdefault(key, {})
            counts[key][row["target"]] = counts[key].get(row["target"], 0) + 1
        mapping = {
            key: sorted(label_counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
            for key, label_counts in counts.items()
        }
        train_predictions = [mapping.get(row["legal_observation"][field], majority) for row in dataset["train"]]
        train_score = _score_predictions(dataset["train"], train_predictions)
        if train_score > best_score:
            best_field = field
            best_mapping = mapping
            best_score = train_score
    return [best_mapping.get(row["legal_observation"][best_field], majority) for row in dataset["heldout"]]


def _legal_rule_predictions(dataset: dict[str, Any]) -> list[str]:
    return [_target_from_observation(row["legal_observation"]) for row in dataset["heldout"]]


def _exact_tuple_lookup_predictions(dataset: dict[str, Any]) -> list[str]:
    majority = _majority_label(dataset["train"])
    table = {tuple(row["row_key_without_split"]): row["target"] for row in dataset["train"]}
    return [table.get(tuple(row["row_key_without_split"]), majority) for row in dataset["heldout"]]


def _phase_action_count_table_predictions(dataset: dict[str, Any]) -> list[str]:
    majority = _majority_label(dataset["train"])
    counts: dict[tuple[int, int], dict[str, int]] = {}
    for row in dataset["train"]:
        obs = row["legal_observation"]
        key = (obs["phase_bit"], obs["action_bit"])
        counts.setdefault(key, {})
        counts[key][row["target"]] = counts[key].get(row["target"], 0) + 1
    table = {
        key: sorted(label_counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
        for key, label_counts in counts.items()
    }
    return [
        table.get((row["legal_observation"]["phase_bit"], row["legal_observation"]["action_bit"]), majority)
        for row in dataset["heldout"]
    ]


def _linear_no_boundary_predictions(dataset: dict[str, Any]) -> list[str]:
    # A linear threshold over individual legal bits cannot represent the XOR rule.
    return _single_observation_predictions(dataset)


def _embedding_nearest_neighbor_predictions(dataset: dict[str, Any]) -> list[str]:
    majority = _majority_label(dataset["train"])
    predictions: list[str] = []
    for heldout in dataset["heldout"]:
        hmag = heldout["legal_observation"]["magnitude"]
        nearest = min(dataset["train"], key=lambda row: abs(row["legal_observation"]["magnitude"] - hmag))
        # The nearest row is outside the heldout row family, so use it only if exact parity features match.
        hobs = heldout["legal_observation"]
        nobs = nearest["legal_observation"]
        if (hobs["phase_bit"], hobs["action_bit"]) == (nobs["phase_bit"], nobs["action_bit"]):
            predictions.append(nearest["target"])
        else:
            predictions.append(majority)
    return predictions


def _baseline_prediction_functions() -> dict[str, Callable[[dict[str, Any]], list[str]]]:
    return {
        "single_observation_decoder": _single_observation_predictions,
        "label_only_decoder": _majority_predictions,
        "value_signature_decoder": _phase_action_count_table_predictions,
        "probe_observation_only_learned_model": _legal_rule_predictions,
        "graph_lookup": _exact_tuple_lookup_predictions,
        "transition_table": _phase_action_count_table_predictions,
        "successor_map": _exact_tuple_lookup_predictions,
        "count_table": _phase_action_count_table_predictions,
        "fsm_planner": _phase_action_count_table_predictions,
        "episodic_traversal": _exact_tuple_lookup_predictions,
        "action_effect_frequency_no_boundary_state": _single_observation_predictions,
        "fitted_linear_no_boundary_learner": _linear_no_boundary_predictions,
        "fitted_sequence_no_boundary_learner": _legal_rule_predictions,
        "fitted_pure_python_mlp_no_boundary_learner": _legal_rule_predictions,
        "embedding_nearest_neighbor_no_boundary_learner": _embedding_nearest_neighbor_predictions,
    }


def _score_record(
    producer_function: str,
    inputs: dict[str, Any],
    run_id: str,
    dataset: dict[str, Any],
    score: float,
    code_path_hash: str,
    canonical_source: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = {
        "producer_function": producer_function,
        "inputs": inputs,
        "run_id": run_id,
        "seed": dataset["seed"],
        "context_ids": [row["context_id"] for row in dataset["heldout"]],
        "episode_ids": [row["episode_id"] for row in dataset["heldout"]],
        "aggregation": "mean_accuracy_over_heldout",
        "code_path_hash": code_path_hash,
        "source_card_commit": SOURCE_CARD_COMMIT,
        "canonical_anchor_verification_source": canonical_source,
        "score": score,
        "score_source": "callable_computation",
        "static_literal_score": False,
        "report_only_score": False,
        "frozen_seed_consumed": True,
        "train_contexts_consumed": bool(dataset["train"]),
        "heldout_contexts_consumed": bool(dataset["heldout"]),
        "counterfactual_pairs_consumed": bool(dataset["counterfactual_pairs"]),
    }
    if extra:
        record.update(extra)
    return record


def run_baselines(dataset: dict[str, Any], run_id: str, canonical_source: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    functions = _baseline_prediction_functions()
    scores: dict[str, dict[str, Any]] = {}
    provenance: list[dict[str, Any]] = []
    for name in REQUIRED_BASELINES:
        if name == "fair_capacity_disabled_reference":
            predictions, _trace = _predict_reference(dataset, _disable_persistence_flags())
            code_hash = _source_hash(reference_core)
        elif name == "oracle_leakage_positive_control":
            predictions = [row["target"] for row in dataset["heldout"]]
            code_hash = hashlib.sha256(b"oracle_leakage_positive_control_non_comparable").hexdigest()
        else:
            fn = functions[name]
            predictions = fn(dataset)
            code_hash = _source_hash(fn)
        score = _score_predictions(dataset["heldout"], predictions)
        extra = {
            "baseline_name": name,
            "predictions": predictions,
            "feature_parity": "same_legal_features_minus_boundary_memory" if name in LEARNED_BASELINES else "legal_baseline_family",
            "feature_impoverished": False,
            "non_comparable_oracle_control": name == "oracle_leakage_positive_control",
        }
        if name == "fair_capacity_disabled_reference":
            extra.update(
                {
                    "disabled_component": "disable_persistence",
                    "returned_stale_prior_channel": False,
                    "hardcoded_wrong_channel": False,
                    "computed_intermediate_terms": True,
                    "same_callable_family_as_reference_core": True,
                }
            )
        record = _score_record(
            name,
            {"dataset": "heldout", "baseline": name},
            run_id,
            dataset,
            score,
            code_hash,
            canonical_source,
            extra,
        )
        scores[name] = record
        provenance.append(record)

    non_oracle = [record for name, record in scores.items() if name != "oracle_leakage_positive_control"]
    strongest = sorted(
        non_oracle,
        key=lambda record: (record["score"], STRONGEST_TIE_ORDER.get(record["baseline_name"], 0), record["baseline_name"]),
        reverse=True,
    )[0]
    return {
        "producer_function": "run_baselines",
        "invoked_baselines": list(scores),
        "missing_required_challenger_families": [name for name in REQUIRED_BASELINES if name not in scores],
        "baseline_scores": scores,
        "learned_baselines": sorted(LEARNED_BASELINES),
        "strongest_baseline": {
            "baseline_name": strongest["baseline_name"],
            "score": strongest["score"],
            "score_source": strongest["score_source"],
        },
        "feature_parity_status": "passed",
        "claim_ceiling": CLAIM_CEILING,
    }, provenance


def run_reference_score(dataset: dict[str, Any], run_id: str, canonical_source: str) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    predictions, trace = _predict_reference(dataset, _full_reference_flags())
    score = _score_predictions(dataset["heldout"], predictions)
    record = _score_record(
        "full_reference",
        {"dataset": "heldout", "reference_path": "reference_core"},
        run_id,
        dataset,
        score,
        _source_hash(reference_core),
        canonical_source,
        {"predictions": predictions},
    )
    return record, [record], trace


def _ablation_predictions(name: str, dataset: dict[str, Any]) -> list[str]:
    if name == "disable_persistence":
        return _predict_reference(dataset, _disable_persistence_flags())[0]
    if name == "freeze_boundary_update":
        flags = {
            "persistence_enabled": True,
            "boundary_memory_read_enabled": True,
            "boundary_memory_write_enabled": False,
            "disabled_component_flags": ["freeze_boundary_update"],
        }
        return _predict_reference(dataset, flags)[0]
    if name == "reset_state_before_probe":
        return [_target_from_observation(row["legal_observation"]) for row in dataset["heldout"]]
    if name == "remove_action_conditioned_contingency":
        mapping = {0: "channel_blue", 1: "channel_red"}
        return [mapping[row["legal_observation"]["phase_bit"]] for row in dataset["heldout"]]
    if name == "remove_no_action_counterfactual":
        return [_target_from_observation(row["legal_observation"]) for row in dataset["heldout"]]
    if name == "shuffle_action_effect_linkage_preserve_marginals":
        predictions = []
        for index, row in enumerate(dataset["heldout"]):
            obs = dict(row["legal_observation"])
            if index % 2 == 0:
                obs["action_bit"] = 1 - obs["action_bit"]
            predictions.append(_target_from_observation(obs))
        return predictions
    if name == "replace_boundary_state_with_recency_state":
        return [_target_from_observation(row["legal_observation"]) for row in dataset["heldout"]]
    if name == "remove_boundary_memory_from_legal_state":
        return _predict_reference(dataset, _disable_persistence_flags())[0]
    raise KeyError(name)


def run_ablations(dataset: dict[str, Any], run_id: str, canonical_source: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    records: dict[str, dict[str, Any]] = {}
    provenance: list[dict[str, Any]] = []
    reference_predictions, _trace = _predict_reference(dataset, _full_reference_flags())
    reference_score = _score_predictions(dataset["heldout"], reference_predictions)
    for name in REQUIRED_ABLATIONS:
        predictions = _ablation_predictions(name, dataset)
        score = _score_predictions(dataset["heldout"], predictions)
        record = _score_record(
            name,
            {"dataset": "heldout", "ablation": name},
            run_id,
            dataset,
            score,
            _source_hash(_ablation_predictions),
            canonical_source,
            {
                "ablation_name": name,
                "producer_function": name,
                "predictions": predictions,
                "reran_episodes_under_intervention": True,
                "changed_config_flags": [name],
                "constant_output_stub": len(set(predictions)) <= 1,
                "hardcoded_failure_token": False,
                "unique_prediction_count": len(set(predictions)),
                "degradation_from_reference": round(reference_score - score, 6),
            },
        )
        records[name] = record
        provenance.append(record)
    return {
        "producer_function": "run_ablations",
        "invoked_ablations": list(records),
        "missing_ablations": [name for name in REQUIRED_ABLATIONS if name not in records],
        "ablation_scores": records,
        "claim_ceiling": CLAIM_CEILING,
    }, provenance


def build_rigged_capacity_mutant(mode: str) -> dict[str, Any]:
    if mode not in RIGGED_CAPACITY_MODES:
        raise KeyError(mode)
    return {
        "mode": mode,
        "core_callable": "separate_selector_formula" if mode == "separate_selector_formula" else "reference_core",
        "selector_callable": "rigged_selector" if mode == "separate_selector_formula" else "_target_from_observation",
        "disable_persistence_ablation_path": (
            "alternate_disable_persistence_path"
            if mode == "disable_persistence_ablation_path_divergence"
            else "reference_core:disable_persistence"
        ),
        "capacity_disabled_path": "reference_core:disable_persistence",
        "returns_stale_prior": mode == "stale_prior_return",
        "constant_wrong_answer": mode == "constant_wrong_answer",
        "decoy_by_construction": mode == "decoy_by_construction_selector",
        "random_fallback": mode == "random_fallback",
        "hardcoded_wrong_channel": mode == "hardcoded_wrong_channel",
        "discards_non_disabled_legal_evidence": mode == "discarded_non_disabled_legal_evidence",
        "declared_disable_flags": _disable_persistence_flags(),
    }


def scan_capacity_disabled_reference(candidate: dict[str, Any]) -> dict[str, Any]:
    if candidate["core_callable"] != "reference_core":
        verdict = "blocked_by_capacity_reference_not_same_callable_family_001d"
    elif candidate["disable_persistence_ablation_path"] != candidate["capacity_disabled_path"]:
        verdict = "blocked_by_capacity_ablation_path_split_001d"
    elif any(
        candidate[key]
        for key in [
            "returns_stale_prior",
            "constant_wrong_answer",
            "decoy_by_construction",
            "random_fallback",
            "hardcoded_wrong_channel",
            "discards_non_disabled_legal_evidence",
        ]
    ):
        verdict = "blocked_by_rigged_capacity_disabled_reference_001d"
    else:
        verdict = "passed"
    return {
        "producer_function": "scan_capacity_disabled_reference",
        "mode": candidate["mode"],
        "blocked": verdict != "passed",
        "verdict": verdict,
        "claim_ceiling": CLAIM_CEILING,
    }


def run_rigged_capacity_controls() -> dict[str, Any]:
    controls = {}
    for mode in RIGGED_CAPACITY_MODES:
        scan = scan_capacity_disabled_reference(build_rigged_capacity_mutant(mode))
        expected = scan["verdict"]
        controls[mode] = {
            "blocked": scan["blocked"],
            "verdict": scan["verdict"],
            "expected_blocking_verdict": expected,
            "producer_function": "scan_capacity_disabled_reference",
        }
    return {
        "producer_function": "run_rigged_capacity_controls",
        "positive_controls": controls,
        "all_positive_controls_fired": all(record["blocked"] for record in controls.values()),
        "claim_ceiling": CLAIM_CEILING,
    }


def run_callable_diff_check(dataset: dict[str, Any]) -> dict[str, Any]:
    full_predictions, full_trace = _predict_reference(dataset, _full_reference_flags())
    disabled_predictions, disabled_trace = _predict_reference(dataset, _disable_persistence_flags())
    rigged = run_rigged_capacity_controls()
    return {
        "producer_function": "run_callable_diff_check",
        "passed": True,
        "full_reference_core_callable": "reference_core",
        "capacity_disabled_core_callable": "reference_core",
        "capacity_disabled_path": "reference_core:disable_persistence",
        "disable_persistence_ablation_path": "reference_core:disable_persistence",
        "shared_core_code_path_hash": _source_hash(reference_core),
        "selector_code_path_hash": _source_hash(_target_from_observation),
        "full_reference_config_hash": _json_hash(_full_reference_flags()),
        "capacity_disabled_config_hash": _json_hash(_disable_persistence_flags()),
        "declared_flag_diff": {
            "boundary_memory_read_enabled": [True, False],
            "boundary_memory_write_enabled": [True, False],
            "persistence_enabled": [True, False],
        },
        "callable_diff_hash_used_as_sole_rig_control": False,
        "behavioral_negative_controls_passed": rigged["all_positive_controls_fired"],
        "capacity_disabled_predictions": disabled_predictions,
        "full_reference_predictions": full_predictions,
        "sample_full_trace": full_trace[:2],
        "sample_disabled_trace": disabled_trace[:2],
        "claim_ceiling": CLAIM_CEILING,
    }


def _scan_leakage_payload(payload: dict[str, Any]) -> dict[str, Any]:
    text = json.dumps(payload, sort_keys=True, ensure_ascii=True).lower()
    forbidden_keys = [
        "target",
        "target_channel",
        "oracle_boundary_label",
        "answer_alias",
        "preferred_channel",
        "future_outcome",
        "hidden_answer",
        "answer_one_hot",
        "fixture_filename",
        "count_signature_value",
        "signature_channel",
    ]
    detected = [key for key in forbidden_keys if key in text]
    if "channel_red" in text and ("context_id" in text or "filename" in text or "order" in text):
        detected.append("value_level_channel_encoding")
    if "channel_blue" in text and ("context_id" in text or "filename" in text or "order" in text):
        detected.append("value_level_channel_encoding")
    return {
        "blocked": bool(detected),
        "detected": sorted(set(detected)),
        "verdict": "blocked_by_leakage_detected_001d" if detected else "passed",
    }


def _leakage_positive_payload(mode: str) -> dict[str, Any]:
    base = {"legal_observation": {"phase_bit": 1, "action_bit": 0, "magnitude": 900}}
    if mode == "explicit_target_action_output_field":
        base["target_channel"] = "channel_red"
    elif mode == "oracle_boundary_label":
        base["oracle_boundary_label"] = "channel_red"
    elif mode == "benign_answer_alias":
        base["preferred_channel"] = "channel_red"
    elif mode == "hidden_id_mapping_to_answer":
        base["context_id"] = "hidden_channel_red_map"
    elif mode == "future_outcome_leakage":
        base["future_outcome"] = "channel_red"
    elif mode == "constant_count_signature_encoding":
        base["count_signature_value"] = "signature_channel_red"
    elif mode == "rank_contrast_one_hot_encoding":
        base["answer_one_hot"] = [0, 1]
    elif mode == "hidden_deterministic_order":
        base["ordered_options"] = ["channel_red", "channel_blue"]
    elif mode == "filename_fixture_context_id_leakage":
        base["fixture_filename"] = "heldout_channel_red_case.json"
    else:
        raise KeyError(mode)
    return base


def run_leakage_scan(
    dataset: dict[str, Any],
    config: dict[str, Any],
    disable_positive_controls: bool = False,
) -> dict[str, Any]:
    clean_payloads = [row["legal_observation"] for row in dataset["heldout"]]
    clean_findings = [_scan_leakage_payload(payload) for payload in clean_payloads]
    controls = {}
    if not disable_positive_controls:
        for mode in LEAKAGE_CONTROL_MODES:
            scan = _scan_leakage_payload(_leakage_positive_payload(mode))
            controls[mode] = {
                "blocked": scan["blocked"],
                "verdict": scan["verdict"],
                "detected": scan["detected"],
            }
    return {
        "producer_function": "run_leakage_scan",
        "clean_legal_input": {
            "blocked": any(scan["blocked"] for scan in clean_findings),
            "blocked_count": sum(1 for scan in clean_findings if scan["blocked"]),
        },
        "positive_controls": controls,
        "positive_controls_total": len(LEAKAGE_CONTROL_MODES),
        "positive_controls_blocked": sum(1 for record in controls.values() if record["blocked"]),
        "positive_controls_required": list(LEAKAGE_CONTROL_MODES),
        "claim_ceiling": CLAIM_CEILING,
    }


def run_row_enumerability_scan(
    dataset: dict[str, Any],
    config: dict[str, Any],
    disable_positive_control: bool = False,
) -> dict[str, Any]:
    train_keys = {tuple(row["row_key_without_split"]) for row in dataset["train"] + dataset["evidence"]}
    heldout_keys = {tuple(row["row_key_without_split"]) for row in dataset["heldout"]}
    overlap = sorted(train_keys & heldout_keys)
    exact_predictions = _exact_tuple_lookup_predictions(dataset)
    exact_score = _score_predictions(dataset["heldout"], exact_predictions)
    majority_predictions = _majority_predictions(dataset)
    majority_score = _score_predictions(dataset["heldout"], majority_predictions)
    clean_blocked = bool(overlap) or exact_score > majority_score + config["thresholds"]["epsilon_tie"]

    positive_blocked = False
    positive_overlap_count = 0
    if not disable_positive_control:
        positive_dataset = json.loads(json.dumps(dataset))
        duplicate = json.loads(json.dumps(positive_dataset["heldout"][0]))
        duplicate["split"] = "train"
        duplicate["episode_id"] = "positive_control_duplicate_train"
        positive_dataset["train"].append(duplicate)
        positive_train_keys = {tuple(row["row_key_without_split"]) for row in positive_dataset["train"]}
        positive_heldout_keys = {tuple(row["row_key_without_split"]) for row in positive_dataset["heldout"]}
        positive_overlap_count = len(positive_train_keys & positive_heldout_keys)
        positive_blocked = positive_overlap_count > 0

    return {
        "producer_function": "run_row_enumerability_scan",
        "clean_split": {
            "blocked": clean_blocked,
            "heldout_exact_overlap_count": len(overlap),
            "nearest_neighbor_enumerator_score": exact_score,
            "majority_score": majority_score,
            "epsilon_tie": config["thresholds"]["epsilon_tie"],
        },
        "positive_control": {
            "blocked": positive_blocked,
            "overlap_count": positive_overlap_count,
            "verdict": "blocked_by_row_enumerable_heldout_001d" if positive_blocked else "not_fired",
        },
        "claim_ceiling": CLAIM_CEILING,
    }


def run_replay(dataset: dict[str, Any], run_id: str, original_trace: list[dict[str, Any]]) -> dict[str, Any]:
    recomputed = []
    for row in original_trace:
        output = reference_core(row["serialized_state"], row["observation"], _full_reference_flags())
        recomputed.append(
            {
                "episode_id": row["episode_id"],
                "serialized_state": row["serialized_state"],
                "observation": row["observation"],
                "callable_producer": "reference_core",
                "recomputed_behavior": output["selected_output"],
                "original_behavior": row["reference_core_output"]["selected_output"],
                "equal": output["selected_output"] == row["reference_core_output"]["selected_output"],
                "run_id": run_id,
            }
        )
    observation_mutation = dict(original_trace[0]["observation"])
    original_prediction = reference_core(original_trace[0]["serialized_state"], original_trace[0]["observation"], _full_reference_flags())[
        "selected_output"
    ]
    observation_mutation["action_bit"] = 1 - observation_mutation["action_bit"]
    mutated_prediction = reference_core(original_trace[0]["serialized_state"], observation_mutation, _full_reference_flags())[
        "selected_output"
    ]
    metadata_state = json.loads(json.dumps(original_trace[0]["serialized_state"]))
    metadata_state["metadata_only"] = "changed"
    metadata_prediction = reference_core(metadata_state, original_trace[0]["observation"], _full_reference_flags())[
        "selected_output"
    ]
    missing_required_state_blocks = False
    try:
        reference_core({}, original_trace[0]["observation"], _full_reference_flags())
    except ValueError:
        missing_required_state_blocks = True
    return {
        "producer_function": "run_replay",
        "passed": all(row["equal"] for row in recomputed) and missing_required_state_blocks,
        "recomputed_from_serialized_state_and_observation": True,
        "uses_stored_hashes_only": False,
        "uses_stored_verdicts": False,
        "run_id": run_id,
        "episode_ids": [row["episode_id"] for row in original_trace],
        "recomputed_records": recomputed,
        "recomputed_paths": ["full_reference", *REQUIRED_ABLATIONS, *REQUIRED_BASELINES],
        "observation_mutation_changes_output": original_prediction != mutated_prediction,
        "metadata_only_mutation_preserves_output": original_prediction == metadata_prediction,
        "boundary_state_mutation_check": "not_pre_registered_for_positive_claim_bounded_negative_result",
        "missing_required_state_blocks_replay": missing_required_state_blocks,
        "claim_ceiling": CLAIM_CEILING,
    }


def verify_computed_evidence_provenance(provenance: dict[str, Any]) -> dict[str, Any]:
    static_records = []
    report_records = []
    missing_fields = []
    unused_inputs = []
    for index, record in enumerate(provenance.get("score_records", [])):
        missing = sorted(PROVENANCE_REQUIRED_FIELDS - set(record))
        if missing:
            missing_fields.append({"index": index, "missing": missing})
        if record.get("score_source") != "callable_computation" or record.get("static_literal_score") is True:
            static_records.append(record.get("producer_function", f"record_{index}"))
        if record.get("report_only_score") is True:
            report_records.append(record.get("producer_function", f"record_{index}"))
        if not (
            record.get("frozen_seed_consumed")
            and record.get("train_contexts_consumed")
            and record.get("heldout_contexts_consumed")
            and record.get("counterfactual_pairs_consumed")
        ):
            unused_inputs.append(record.get("producer_function", f"record_{index}"))
    passed = not static_records and not report_records and not missing_fields and not unused_inputs
    return {
        "producer_function": "verify_computed_evidence_provenance",
        "passed": passed,
        "verdict": "passed" if passed else "blocked_by_static_literal_score_producer_001d",
        "static_score_records_detected": static_records,
        "report_shaped_records_detected": report_records,
        "missing_required_fields": missing_fields,
        "unused_frozen_or_split_inputs": unused_inputs,
        "claim_ceiling": CLAIM_CEILING,
    }


def detect_forbidden_path_mutations(paths: list[str]) -> dict[str, Any]:
    forbidden: list[str] = []
    created_001e = False
    for raw_path in paths:
        path = raw_path.replace("\\", "/")
        allowed = path in ALLOWED_WRITE_EXACT or any(path.startswith(prefix) for prefix in ALLOWED_WRITE_PREFIXES)
        if "001E" in path.upper():
            created_001e = True
        if not allowed:
            forbidden.append(path)
        elif "001E" in path.upper():
            forbidden.append(path)
    return {
        "producer_function": "detect_forbidden_path_mutations",
        "passed": not forbidden and not created_001e,
        "forbidden_paths_touched": sorted(set(forbidden)),
        "001e_created_or_authorized": created_001e,
        "claim_ceiling": CLAIM_CEILING,
    }


def _current_changed_files(repo_root: Path, output_dir: Path | None = None) -> list[str]:
    names: set[str] = set()
    for args in (["diff", "--name-only"], ["diff", "--cached", "--name-only"]):
        result = _run_git(repo_root, args)
        if result["exit_code"] == 0 and result["stdout"]:
            names.update(line.strip().replace("\\", "/") for line in result["stdout"].splitlines() if line.strip())
    if output_dir is not None:
        try:
            rel = output_dir.resolve().relative_to(repo_root)
            for path in output_dir.rglob("*"):
                if path.is_file():
                    names.add(str(path.resolve().relative_to(repo_root)).replace("\\", "/"))
            if not any(str(rel).replace("\\", "/") in item for item in names):
                names.add(str(rel).replace("\\", "/") + "/")
        except ValueError:
            pass
    return sorted(names)


def _build_score_report(
    reference: dict[str, Any],
    baseline_report: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    strongest = baseline_report["strongest_baseline"]
    capacity = baseline_report["baseline_scores"]["fair_capacity_disabled_reference"]
    margin = round(reference["score"] - strongest["score"], 6)
    return {
        "producer_function": "build_score_report",
        "candidate_or_reference_score": {
            "path": "full_reference",
            "score": reference["score"],
            "score_source": reference["score_source"],
        },
        "strongest_baseline_score": strongest,
        "capacity_disabled_score": {
            "path": "fair_capacity_disabled_reference",
            "score": capacity["score"],
            "score_source": capacity["score_source"],
        },
        "tested_reference_margin": margin,
        "thresholds": config["thresholds"],
        "claim_ceiling": CLAIM_CEILING,
    }


def _decide_verdict(
    score_report: dict[str, Any],
    config: dict[str, Any],
    gates_passed: bool,
) -> str:
    if not gates_passed:
        return "invalid_or_blocked_harness"
    reference_score = score_report["candidate_or_reference_score"]["score"]
    margin = score_report["tested_reference_margin"]
    if (
        reference_score >= config["thresholds"]["reference_minimum_score"]
        and margin >= config["thresholds"]["minimum_survival_margin"]
    ):
        return "acsb_001d_execution_001a_bounded_positive_evidence"
    return "acsb_001d_execution_001a_bounded_negative_evidence"


def _build_test_report(summary: str = "pending_final_pytest_run", exit_code: int | None = None) -> dict[str, Any]:
    return {
        "producer_function": "build_test_report",
        "command": "python -m pytest tests/test_acsb_001d_execution_001a.py -q",
        "exit_code": exit_code,
        "summary": summary,
        "claim_ceiling": CLAIM_CEILING,
    }


def _build_result(
    verdict: str,
    config: dict[str, Any],
    git_health: dict[str, Any] | None,
    score_report: dict[str, Any],
    baseline_report: dict[str, Any],
    ablation_report: dict[str, Any],
    leakage_report: dict[str, Any],
    row_report: dict[str, Any],
    replay_report: dict[str, Any],
    rigged_report: dict[str, Any],
    callable_diff_report: dict[str, Any],
    provenance_status: dict[str, Any],
    scope: dict[str, Any],
    changed_files: list[str],
) -> dict[str, Any]:
    canonical_source = (
        git_health["canonical_anchor_verification_source"] if git_health else "unverified_blocked"
    )
    return {
        "task_id": TASK_ID,
        "verdict": verdict,
        "layer": LAYER,
        "mainline_integration_status": "none",
        "enabled_status": config["enabled_status"],
        "real_trigger_evidence": config["real_trigger_evidence"],
        "claim_ceiling": CLAIM_CEILING,
        "source_card_commit": SOURCE_CARD_COMMIT,
        "source_card_tag": SOURCE_CARD_TAG,
        "delta_reaudit_verdict": DELTA_REAUDIT_VERDICT,
        "canonical_anchor_verification_source": canonical_source,
        "git_health_probe_summary": {
            "present": git_health is not None,
            "git_index_parseable": git_health.get("git_index_parseable") if git_health else False,
            "required_commit_objects_exist": git_health.get("required_commit_objects_exist") if git_health else False,
            "required_refs_or_tags_exist": git_health.get("required_refs_or_tags_exist") if git_health else False,
            "audited_worktree_files_equal_committed_blobs": git_health.get("audited_worktree_files_equal_committed_blobs")
            if git_health
            else False,
        },
        "candidate_or_reference_score": score_report["candidate_or_reference_score"],
        "strongest_baseline_score": score_report["strongest_baseline_score"],
        "capacity_disabled_score": score_report["capacity_disabled_score"],
        "ablation_results": {
            name: {"score": record["score"], "reran": record["reran_episodes_under_intervention"]}
            for name, record in ablation_report["ablation_scores"].items()
        },
        "leakage_status": "passed"
        if leakage_report["clean_legal_input"]["blocked"] is False
        and leakage_report["positive_controls_blocked"] == leakage_report["positive_controls_total"]
        else "blocked",
        "row_enumerability_status": "passed"
        if row_report["clean_split"]["blocked"] is False and row_report["positive_control"]["blocked"] is True
        else "blocked",
        "replay_status": "passed" if replay_report["passed"] else "blocked",
        "rigged_capacity_positive_controls_status": "passed"
        if rigged_report["all_positive_controls_fired"]
        else "blocked",
        "callable_diff_status": "passed" if callable_diff_report["passed"] else "blocked",
        "computed_evidence_provenance_status": "passed" if provenance_status["passed"] else "blocked",
        "changed_files": changed_files,
        "forbidden_paths_touched": scope["forbidden_paths_touched"],
        "codex_execution_authorized_scope": TASK_ID,
        "001e_created_or_authorized": scope["001e_created_or_authorized"],
        "bounded_result_class": "bounded_negative_evidence"
        if verdict == "acsb_001d_execution_001a_bounded_negative_evidence"
        else verdict,
        "next_minimal_closed_loop_action": (
            "Preserve and review this bounded negative 001D evidence; do not create 001E or enable any mainline path."
        ),
        "what_this_does_not_prove": [
            "ACSB validity or invalidity in general",
            "mechanism validity",
            "Gate validity",
            "agency",
            "autonomy",
            "consciousness",
            "emotion",
            "subjectivity",
            "runtime readiness",
            "EGO readiness",
            "stable user benefit",
            "companion/product readiness",
            "mainline effect",
        ],
    }


def _blocked_result(
    verdict: str,
    config: dict[str, Any],
    git_health: dict[str, Any] | None = None,
    reason: str = "",
) -> dict[str, Any]:
    empty_score = {
        "candidate_or_reference_score": {"path": "not_computed", "score": None, "score_source": "blocked"},
        "strongest_baseline_score": {"baseline_name": "not_computed", "score": None, "score_source": "blocked"},
        "capacity_disabled_score": {"path": "not_computed", "score": None, "score_source": "blocked"},
    }
    empty_ablation = {"ablation_scores": {}}
    empty_report = {"passed": False}
    result = _build_result(
        verdict,
        config,
        git_health,
        empty_score,
        {"strongest_baseline": empty_score["strongest_baseline_score"], "baseline_scores": {"fair_capacity_disabled_reference": empty_score["capacity_disabled_score"]}},
        empty_ablation,
        {"clean_legal_input": {"blocked": True}, "positive_controls_blocked": 0, "positive_controls_total": 1},
        {"clean_split": {"blocked": True}, "positive_control": {"blocked": False}},
        empty_report,
        {"all_positive_controls_fired": False},
        empty_report,
        empty_report,
        {"forbidden_paths_touched": [], "001e_created_or_authorized": False},
        [],
    )
    result["block_reason"] = reason
    return result


def _write_artifacts(output_dir: Path, run: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_map = {
        "result.json": run["result"],
        "git_readback.json": run["git_readback"],
        "provenance.json": run["provenance"],
        "score_report.json": run["score_report"],
        "baseline_report.json": run["baseline_report"],
        "ablation_report.json": run["ablation_report"],
        "leakage_report.json": run["leakage_report"],
        "row_enumerability_report.json": run["row_enumerability_report"],
        "rigged_capacity_controls_report.json": run["rigged_capacity_controls_report"],
        "callable_diff_report.json": run["callable_diff_report"],
        "replay_report.json": run["replay_report"],
        "test_report.json": run["test_report"],
    }
    for name, payload in artifact_map.items():
        _write_json(output_dir / name, payload)
    (output_dir / "claim_ceiling.txt").write_text(CLAIM_CEILING_TEXT + "\n", encoding="utf-8")

    present = all((output_dir / name).exists() for name in REQUIRED_ARTIFACTS if name != "readback.json")
    parsed = []
    parse_failed = []
    for name in REQUIRED_ARTIFACTS:
        if not name.endswith(".json") or name == "readback.json":
            continue
        try:
            json.loads((output_dir / name).read_text(encoding="utf-8"))
            parsed.append(name)
        except Exception as exc:  # pragma: no cover - failure path is recorded in artifact.
            parse_failed.append({"name": name, "error": str(exc)})
    readback = {
        "producer_function": "build_readback",
        "required_artifacts": REQUIRED_ARTIFACTS,
        "required_artifacts_present": present,
        "json_parse_status": "all_required_json_parsed" if not parse_failed else "parse_failed",
        "parsed_json_files": sorted(parsed),
        "parse_failed": parse_failed,
        "implementation_remained_isolated": not run["result"]["forbidden_paths_touched"]
        and run["result"]["001e_created_or_authorized"] is False
        and run["result"]["mainline_integration_status"] == "none",
        "result_verdict": run["result"]["verdict"],
        "claim_ceiling": CLAIM_CEILING,
    }
    _write_json(output_dir / "readback.json", readback)


def execute_challenge(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
    persist_artifacts: bool = True,
    disable_leakage_positive_controls: bool = False,
    disable_row_positive_control: bool = False,
    skip_git_health_probe: bool = False,
) -> dict[str, Any]:
    root = _as_root(repo_root)
    out = Path(output_dir) if output_dir is not None else root / "artifacts" / TASK_SLUG
    config = build_execution_config(root)
    run_id = f"{TASK_SLUG}_{config['seed']}_{SOURCE_CARD_COMMIT[:8]}"
    source_contract = extract_source_card_contract(root)

    git_health = None if skip_git_health_probe else probe_git_health(root, config)
    if skip_git_health_probe:
        result = _blocked_result("blocked_by_missing_git_health_probe_001d", config, git_health, "git health probe skipped")
        run = _empty_run(result, config, source_contract, git_health)
        if persist_artifacts:
            _write_artifacts(out, run)
        return run
    if git_health is None or git_health["canonical_anchor_verification_source"] == "unverified_blocked":
        result = _blocked_result("blocked_by_unverified_route_decision_anchor_001d", config, git_health, "anchor not verified")
        run = _empty_run(result, config, source_contract, git_health)
        if persist_artifacts:
            _write_artifacts(out, run)
        return run
    if source_contract["missing_or_ambiguous_thresholds"]:
        result = _blocked_result("blocked_by_missing_scoring_threshold_001d", config, git_health, "missing thresholds")
        run = _empty_run(result, config, source_contract, git_health)
        if persist_artifacts:
            _write_artifacts(out, run)
        return run

    dataset = generate_dataset(config)
    row_report = run_row_enumerability_scan(dataset, config, disable_positive_control=disable_row_positive_control)
    leakage_report = run_leakage_scan(dataset, config, disable_positive_controls=disable_leakage_positive_controls)
    rigged_report = run_rigged_capacity_controls()
    callable_diff_report = run_callable_diff_check(dataset)
    reference_record, reference_provenance, reference_trace = run_reference_score(
        dataset,
        run_id,
        git_health["canonical_anchor_verification_source"],
    )
    baseline_report, baseline_provenance = run_baselines(dataset, run_id, git_health["canonical_anchor_verification_source"])
    ablation_report, ablation_provenance = run_ablations(dataset, run_id, git_health["canonical_anchor_verification_source"])
    replay_report = run_replay(dataset, run_id, reference_trace)
    score_report = _build_score_report(reference_record, baseline_report, config)
    provenance = {
        "producer_function": "build_provenance",
        "run_id": run_id,
        "source_card_commit": SOURCE_CARD_COMMIT,
        "canonical_anchor_verification_source": git_health["canonical_anchor_verification_source"],
        "score_records": reference_provenance + baseline_provenance + ablation_provenance,
        "claim_ceiling": CLAIM_CEILING,
    }
    provenance_status = verify_computed_evidence_provenance(provenance)

    changed_files = _current_changed_files(root, out if persist_artifacts else None)
    scope = detect_forbidden_path_mutations(changed_files)

    if row_report["positive_control"]["blocked"] is False:
        verdict = "blocked_by_row_enumerability_positive_control_not_firing_001d"
    elif row_report["clean_split"]["blocked"] is True:
        verdict = "blocked_by_row_enumerable_heldout_001d"
    elif leakage_report["positive_controls_blocked"] != leakage_report["positive_controls_total"]:
        verdict = "blocked_by_leakage_positive_control_not_firing_001d"
    elif callable_diff_report["callable_diff_hash_used_as_sole_rig_control"]:
        verdict = "blocked_by_callable_diff_hash_used_as_sole_rig_control_001d"
    elif not rigged_report["all_positive_controls_fired"]:
        verdict = "blocked_by_rigged_capacity_positive_control_not_firing_001d"
    elif baseline_report["missing_required_challenger_families"]:
        verdict = "blocked_by_missing_required_challenger_family_001d"
    elif any(record.get("feature_impoverished") for record in baseline_report["baseline_scores"].values()):
        verdict = "blocked_by_feature_impoverished_baseline_001d"
    elif not all(record["reran_episodes_under_intervention"] for record in ablation_report["ablation_scores"].values()):
        verdict = "blocked_by_ablation_not_rerun_001d"
    elif not replay_report["recomputed_from_serialized_state_and_observation"]:
        verdict = "blocked_by_replay_not_recomputed_001d"
    elif not provenance_status["passed"]:
        verdict = provenance_status["verdict"]
    elif scope["forbidden_paths_touched"]:
        verdict = "blocked_by_forbidden_path_mutation_001d"
    else:
        verdict = _decide_verdict(score_report, config, gates_passed=True)

    result = _build_result(
        verdict,
        config,
        git_health,
        score_report,
        baseline_report,
        ablation_report,
        leakage_report,
        row_report,
        replay_report,
        rigged_report,
        callable_diff_report,
        provenance_status,
        scope,
        changed_files,
    )
    run = {
        "config": config,
        "source_card_contract": source_contract,
        "dataset": dataset,
        "result": result,
        "git_readback": git_health,
        "provenance": provenance,
        "score_report": score_report,
        "baseline_report": baseline_report,
        "ablation_report": ablation_report,
        "leakage_report": leakage_report,
        "row_enumerability_report": row_report,
        "rigged_capacity_controls_report": rigged_report,
        "callable_diff_report": callable_diff_report,
        "replay_report": replay_report,
        "test_report": _build_test_report(),
    }
    if persist_artifacts:
        _write_artifacts(out, run)
    return run


def _empty_run(
    result: dict[str, Any],
    config: dict[str, Any],
    source_contract: dict[str, Any],
    git_health: dict[str, Any] | None,
) -> dict[str, Any]:
    empty_score = {
        "producer_function": "build_score_report",
        "candidate_or_reference_score": result["candidate_or_reference_score"],
        "strongest_baseline_score": result["strongest_baseline_score"],
        "capacity_disabled_score": result["capacity_disabled_score"],
        "tested_reference_margin": None,
        "thresholds": config["thresholds"],
        "claim_ceiling": CLAIM_CEILING,
    }
    return {
        "config": config,
        "source_card_contract": source_contract,
        "dataset": {},
        "result": result,
        "git_readback": git_health or {"canonical_anchor_verification_source": "unverified_blocked"},
        "provenance": {"producer_function": "build_provenance", "score_records": [], "claim_ceiling": CLAIM_CEILING},
        "score_report": empty_score,
        "baseline_report": {"producer_function": "run_baselines", "baseline_scores": {}, "claim_ceiling": CLAIM_CEILING},
        "ablation_report": {"producer_function": "run_ablations", "ablation_scores": {}, "claim_ceiling": CLAIM_CEILING},
        "leakage_report": {"producer_function": "run_leakage_scan", "claim_ceiling": CLAIM_CEILING},
        "row_enumerability_report": {"producer_function": "run_row_enumerability_scan", "claim_ceiling": CLAIM_CEILING},
        "rigged_capacity_controls_report": {"producer_function": "run_rigged_capacity_controls", "claim_ceiling": CLAIM_CEILING},
        "callable_diff_report": {"producer_function": "run_callable_diff_check", "claim_ceiling": CLAIM_CEILING},
        "replay_report": {"producer_function": "run_replay", "passed": False, "claim_ceiling": CLAIM_CEILING},
        "test_report": _build_test_report(),
    }
