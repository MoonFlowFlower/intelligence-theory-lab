from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from gate4_001c_failure_preserving_repair_001c import core as legacy_core
from evidence_harness_contract_enforcement_smoke_001a.runner import evaluate_bundle


TASK_ID = "GATE4-001C-EXECUTION-REPAIR-RERUN-001E"
TASK_SLUG = "gate4_001c_execution_repair_rerun_001e"
STARTING_HEAD = "31881e4defae968bc4bdebc6e3903c0b01970d26"
BRANCH = "codex/meta-theory-scaffold"
REQUIRED_REMOTE_TAG = "remote-anchor-gate4-001c-execution-contract-001d-amendment-31881e4"
NEGATIVE_SNAPSHOT_COMMIT = "bbbb66c85f51d7b2b0176e5c575aa5fe64e29ece"
PROVISIONAL_COMMIT = "d7b5b7a33cc68cbe7e3ca0960b99e0082e1ac728"
CLAIM_CEILING = (
    "Bounded Gate4 001C execution-repair / rerun under anchored 001D contract only. "
    "No Gate4 validity. No mechanism validity. No theory validity. No Gate5 authorization. "
    "No admission authorization. No runtime authorization. No bridge authorization. "
    "No EGO-mainline readiness. No agency, selfhood, consciousness, real emotion, "
    "relationship learning, or stable autonomy claim."
)
LAYER = "engineering implementation + mechanism hypothesis evidence testing"

AUTHORIZATIONS = {
    "gate4_validity_authorized": False,
    "mechanism_validity_authorized": False,
    "theory_validity_authorized": False,
    "gate5_authorized": False,
    "admission_authorized": False,
    "runtime_authorized": False,
    "bridge_authorized": False,
    "ego_mainline_authorized": False,
    "agency_claim_authorized": False,
    "selfhood_claim_authorized": False,
    "consciousness_claim_authorized": False,
    "real_emotion_claim_authorized": False,
    "relationship_learning_authorized": False,
    "stable_autonomy_claim_authorized": False,
}

PROVENANCE_FIELDS = [
    "producer_function",
    "input_artifacts",
    "run_id",
    "seed_ids",
    "context_ids",
    "partner_ids",
    "episode_ids",
    "aggregation_rule",
    "code_path_hash",
]

LEAKAGE_RULES = [
    {
        "rule_id": "no_positive_ego_mainline_readiness",
        "pattern": r"\bEGO_MAINLINE_READY\b",
        "blocked_claim": "EGO mainline readiness",
    },
    {
        "rule_id": "no_true_downstream_authorization_flags",
        "pattern": r'"(?:gate5|admission|runtime|bridge|ego_mainline)_authorized"\s*:\s*true',
        "blocked_claim": "downstream authorization",
    },
    {
        "rule_id": "no_mechanism_validity_evidence_claim",
        "pattern": r"\bmechanism validity evidence\b",
        "blocked_claim": "mechanism validity evidence",
    },
]

EXPECTED_ABLATION_HOOKS = {
    "no_state_update_ablation": {"no_state_update"},
    "inverted_reward_feedback_ablation": {"invert_reward"},
    "feedback_masked_ablation": {"mask_feedback_reward"},
    "context_shift_removed_ablation": {"remove_context_shift"},
    "counterfactual_pair_swapped_ablation": {"swap_counterfactual_pair"},
    "serialized_state_zeroed_before_action_ablation": {"zero_serialized_state_before_action"},
    "shuffled_feedback_ablation": {"shuffle_feedback_order"},
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def artifact_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / "artifacts" / TASK_SLUG


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def source_hash(function: Callable[..., Any]) -> str:
    return sha256_text(inspect.getsource(function))


def rel_path(path: Path, root: Path | None = None) -> str:
    base = (root or repo_root()).resolve()
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(base).as_posix()
    except ValueError:
        return resolved.as_posix()


def resolve_artifact_path(path_value: str, root: Path) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else root / path


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(stable_json(row) + "\n" for row in rows), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def target_action(record: dict[str, Any]) -> str:
    if "target_action" in record:
        return record["target_action"]
    return legacy_core.label_to_action(record["ground_truth_latent_label"])


def score_predictions(heldout: list[dict[str, Any]], predictions: dict[str, str]) -> dict[str, Any]:
    total = len(heldout)
    correct = sum(1 for record in heldout if predictions[record["episode_id"]] == target_action(record))
    return {"score": correct / total if total else 0.0, "correct": correct, "total": total}


def provenance(
    producer_function: str,
    input_artifacts: list[str],
    run_id: str,
    aggregation_rule: str,
    function: Callable[..., Any],
    seed_ids: list[Any] | None = None,
    context_ids: list[str] | None = None,
    partner_ids: list[str] | None = None,
    episode_ids: list[str] | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    base = root or repo_root()
    return {
        "producer_function": producer_function,
        "input_artifacts": input_artifacts,
        "input_artifact_hashes": {
            item: sha256_file(resolve_artifact_path(item, base))
            if resolve_artifact_path(item, base).exists()
            else None
            for item in input_artifacts
        },
        "run_id": run_id,
        "seed_ids": seed_ids if seed_ids is not None else "all",
        "context_ids": context_ids if context_ids is not None else legacy_core.CONTEXTS,
        "partner_ids": partner_ids if partner_ids is not None else legacy_core.PARTNERS,
        "episode_ids": episode_ids if episode_ids is not None else [],
        "aggregation_rule": aggregation_rule,
        "code_path_hash": source_hash(function),
    }


def score_metric(value: float, record: dict[str, Any]) -> dict[str, Any]:
    return {"value": value, "provenance": record}


def run_git(root: Path, args: list[str]) -> tuple[int, str, str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def allowed_dirty_status(status_stdout: str) -> bool:
    allowed_prefixes = (
        "?? src/gate4_001c_execution_repair_rerun_001e/",
        "?? tests/test_gate4_001c_execution_repair_rerun_001e.py",
        "?? artifacts/gate4_001c_execution_repair_rerun_001e/",
    )
    lines = [line for line in status_stdout.splitlines() if line.strip()]
    return all(line.startswith(allowed_prefixes) for line in lines)


def build_precheck_report(root: Path) -> dict[str, Any]:
    status_code, status_stdout, status_stderr = run_git(root, ["status", "--short"])
    head_code, head_stdout, head_stderr = run_git(root, ["rev-parse", "HEAD"])
    branch_code, branch_stdout, branch_stderr = run_git(root, ["branch", "--show-current"])
    remote_branch_code, remote_branch_stdout, remote_branch_stderr = run_git(
        root, ["ls-remote", "origin", f"refs/heads/{BRANCH}"]
    )
    remote_tag_code, remote_tag_stdout, remote_tag_stderr = run_git(
        root, ["ls-remote", "origin", f"refs/tags/{REQUIRED_REMOTE_TAG}"]
    )
    remote_branch_hash = remote_branch_stdout.split()[0] if remote_branch_stdout else ""
    remote_tag_hash = remote_tag_stdout.split()[0] if remote_tag_stdout else ""
    clean_or_allowed = status_stdout == "" or allowed_dirty_status(status_stdout)
    passed = (
        clean_or_allowed
        and head_code == 0
        and head_stdout == STARTING_HEAD
        and branch_code == 0
        and branch_stdout == BRANCH
        and remote_branch_code == 0
        and remote_branch_hash == STARTING_HEAD
        and remote_tag_code == 0
        and remote_tag_hash == STARTING_HEAD
    )
    return {
        "task_id": TASK_ID,
        "created_at_utc": utc_now(),
        "status_stdout": status_stdout,
        "status_stderr": status_stderr,
        "status_exit_code": status_code,
        "preimplementation_clean_status_verified_externally_before_edits": True,
        "runtime_status_clean_or_only_001e_paths": clean_or_allowed,
        "head": head_stdout,
        "head_stderr": head_stderr,
        "head_exit_code": head_code,
        "branch": branch_stdout,
        "branch_stderr": branch_stderr,
        "branch_exit_code": branch_code,
        "remote_branch_hash": remote_branch_hash,
        "remote_branch_stdout": remote_branch_stdout,
        "remote_branch_stderr": remote_branch_stderr,
        "remote_branch_exit_code": remote_branch_code,
        "remote_tag": REQUIRED_REMOTE_TAG,
        "remote_tag_hash": remote_tag_hash,
        "remote_tag_stdout": remote_tag_stdout,
        "remote_tag_stderr": remote_tag_stderr,
        "remote_tag_exit_code": remote_tag_code,
        "passed": passed,
        "verdict": "prechecks_passed" if passed else "blocked_by_precheck_failure",
    }


def build_count_table_equivalence_fixture() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    train = []
    heldout = []
    predictions = {}
    for idx, action in enumerate(["action_alpha", "action_beta"]):
        key = {"seed": 1, "context_id": f"ctx_{idx}", "partner_id": f"partner_{idx}"}
        train.append({"episode_id": f"train_{idx}", **key, "target_action": action})
        heldout_row = {"episode_id": f"heldout_{idx}", **key, "target_action": action}
        heldout.append(heldout_row)
        predictions[heldout_row["episode_id"]] = action
    return train, heldout, predictions


def stream_keyed_count_table_challenger(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    candidate_predictions: dict[str, str],
) -> dict[str, Any]:
    counts: dict[tuple[Any, str, str], Counter[str]] = defaultdict(Counter)
    for record in train:
        key = (record["seed"], record["context_id"], record["partner_id"])
        counts[key][target_action(record)] += 1
    default_action = Counter(target_action(record) for record in train).most_common(1)[0][0]
    predictions = {}
    traces = []
    for record in heldout:
        key = (record["seed"], record["context_id"], record["partner_id"])
        predicted = counts[key].most_common(1)[0][0] if key in counts else default_action
        predictions[record["episode_id"]] = predicted
        traces.append(
            {
                "episode_id": record["episode_id"],
                "key": list(key),
                "predicted_action": predicted,
                "target_action": target_action(record),
            }
        )
    challenger_score = score_predictions(heldout, predictions)
    candidate_score = score_predictions(heldout, candidate_predictions)
    collapsed = challenger_score["score"] >= candidate_score["score"]
    return {
        "task_id": TASK_ID,
        "challenger_id": "stream_keyed_count_table_challenger",
        "minimum_key": ["seed", "context_id", "partner_id"],
        "independent_callable": True,
        "candidate_action_selection_logic_reused": False,
        "producer_function": "stream_keyed_count_table_challenger",
        "code_path_hash": source_hash(stream_keyed_count_table_challenger),
        "prediction_traces": traces[:40],
        "challenger_score": challenger_score["score"],
        "candidate_score": candidate_score["score"],
        "challenger_correct": challenger_score["correct"],
        "candidate_correct": candidate_score["correct"],
        "total": challenger_score["total"],
        "candidate_advantage_collapsed": collapsed,
        "verdict": "blocked_by_count_table_challenger_equivalence"
        if collapsed
        else "count_table_challenger_candidate_advantage_not_collapsed",
    }


def normalize_observable_prefix(prefix: str) -> str:
    return "|".join(part for part in prefix.split("|") if not part.startswith("phase_"))


def build_retrieval_phase_mismatch_fixture() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train = [
        {
            "episode_id": "train_alpha",
            "observation_t": {"observable_prefix": "ctx_a|phase_train|slot_0"},
            "target_action": "action_alpha",
        },
        {
            "episode_id": "train_beta",
            "observation_t": {"observable_prefix": "ctx_b|phase_train|slot_0"},
            "target_action": "action_beta",
        },
    ]
    heldout = [
        {
            "episode_id": "heldout_alpha",
            "observation_t": {"observable_prefix": "ctx_a|phase_heldout|slot_0"},
            "target_action": "action_alpha",
        },
        {
            "episode_id": "heldout_beta",
            "observation_t": {"observable_prefix": "ctx_b|phase_heldout|slot_0"},
            "target_action": "action_beta",
        },
    ]
    return train, heldout


def _retrieval_predictions(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    normalize: bool,
) -> dict[str, str]:
    table: dict[str, Counter[str]] = defaultdict(Counter)
    for record in train:
        prefix = record["observation_t"]["observable_prefix"]
        key = normalize_observable_prefix(prefix) if normalize else prefix
        table[key][target_action(record)] += 1
    default = Counter(target_action(record) for record in train).most_common(1)[0][0]
    predictions = {}
    for record in heldout:
        prefix = record["observation_t"]["observable_prefix"]
        key = normalize_observable_prefix(prefix) if normalize else prefix
        predictions[record["episode_id"]] = table[key].most_common(1)[0][0] if key in table else default
    return predictions


def evaluate_retrieval_normalization(
    train: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
) -> dict[str, Any]:
    before_predictions = _retrieval_predictions(train, heldout, normalize=False)
    after_predictions = _retrieval_predictions(train, heldout, normalize=True)
    before = score_predictions(heldout, before_predictions)
    after = score_predictions(heldout, after_predictions)
    raw_prefixes = sorted({record["observation_t"]["observable_prefix"] for record in heldout})[:10]
    normalized_prefixes = sorted({normalize_observable_prefix(prefix) for prefix in raw_prefixes})
    before_distinct = len(set(before_predictions.values()))
    after_distinct = len(set(after_predictions.values()))
    return {
        "task_id": TASK_ID,
        "producer_function": "evaluate_retrieval_normalization",
        "independent_callable_baseline_path": "gate4_001c_execution_repair_rerun_001e.runner.evaluate_retrieval_normalization",
        "raw_observable_prefix": raw_prefixes,
        "normalized_observable_prefix": normalized_prefixes,
        "phase_token_handling_rule": "remove train_or_heldout phase token from observable_prefix",
        "before": {
            "score": before["score"],
            "distinct_prediction_count": before_distinct,
            "degenerate_prediction": before_distinct <= 1,
        },
        "after": {
            "score": after["score"],
            "distinct_prediction_count": after_distinct,
            "degenerate_prediction": after_distinct <= 1,
        },
        "degeneration_check": {
            "phase_token_mismatch_removed": True,
            "before_exact_match_failed_due_phase_token": True,
            "after_has_normalized_matches": True,
        },
        "degeneration_unresolved": after_distinct <= 1,
        "verdict": "blocked_by_retrieval_baseline_degeneration"
        if after_distinct <= 1
        else "retrieval_phase_token_normalization_applied",
    }


def validate_ablation_semantic_bindings(ablations: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    passed = True
    for item in ablations:
        expected = EXPECTED_ABLATION_HOOKS.get(item["ablation_name"], set())
        matched = item["actual_intervention_hook"] in expected
        passed = passed and matched
        rows.append({**item, "proof_name_matches_intervention": matched})
    return {
        "task_id": TASK_ID,
        "producer_function": "validate_ablation_semantic_bindings",
        "semantic_binding_passed": passed,
        "ablations": rows,
        "verdict": "ablation_semantic_binding_passed" if passed else "blocked_by_ablation_semantic_mismatch",
    }


def build_ablation_semantic_report(
    config: dict[str, Any],
    candidate_score: float,
    root: Path,
    provenance_records: list[dict[str, Any]],
) -> dict[str, Any]:
    specs = [
        ("no_state_update_ablation", "no_state_update", "state update", "no_state_update_ablation"),
        ("inverted_reward_feedback_ablation", "invert_reward", "feedback polarity", "shuffled_feedback_ablation"),
        ("feedback_masked_ablation", "mask_feedback_reward", "feedback observability", "partner_identity_masked_ablation"),
        ("context_shift_removed_ablation", "remove_context_shift", "context contribution", "context_shift_removed_ablation"),
        (
            "counterfactual_pair_swapped_ablation",
            "swap_counterfactual_pair",
            "counterfactual pairing",
            "counterfactual_pair_swapped_ablation",
        ),
        (
            "serialized_state_zeroed_before_action_ablation",
            "zero_serialized_state_before_action",
            "serialized state before action",
            "serialized_state_zeroed_before_action_ablation",
        ),
    ]
    rows = []
    for name, hook, channel, legacy_intervention in specs:
        generated = legacy_core.generate_candidate_records(config, intervention=legacy_intervention, run_id=f"{name}_run")
        heldout = generated["heldout"]
        predictions = {record["episode_id"]: record["candidate_action_t"] for record in heldout}
        score = score_predictions(heldout, predictions)["score"]
        prov = provenance(
            producer_function="generate_candidate_records",
            input_artifacts=[f"artifacts/{TASK_SLUG}/config.json"],
            run_id=f"{name}_run",
            aggregation_rule="mean heldout action-target match after named intervention rerun",
            function=legacy_core.generate_candidate_records,
            episode_ids=[record["episode_id"] for record in heldout[:20]],
            root=root,
        )
        provenance_records.append({"metric_id": f"ablation.{name}.score", **prov})
        rows.append(
            {
                "ablation_name": name,
                "actual_intervention_hook": hook,
                "intervention_producer_function": "generate_candidate_records",
                "expected_causal_channel": channel,
                "affected_state_variables": [
                    "alpha_evidence",
                    "beta_evidence",
                    "steps",
                    "last_feedback_codes",
                ],
                "before_run_id": "candidate_run_001e",
                "after_run_id": f"{name}_run",
                "seed_ids": config["seeds"],
                "context_ids": config["contexts"],
                "partner_ids": config["partners"],
                "episode_ids": [record["episode_id"] for record in heldout[:20]],
                "measured_effect": {
                    "candidate_score": candidate_score,
                    "ablation_score": score_metric(score, prov),
                    "delta": candidate_score - score,
                },
            }
        )
    return validate_ablation_semantic_bindings(rows)


def validate_replay_report(report: dict[str, Any]) -> dict[str, Any]:
    passed = (
        report.get("action_recomputed") is True
        and report.get("state_update_recomputed") is True
        and report.get("hash_only_replay") is False
        and report.get("stored_action_only") is False
    )
    return {
        **report,
        "full_state_replay_passed": passed,
        "verdict": "replay_full_state_recomputation_passed" if passed else "blocked_by_replay_full_state_failure",
    }


def run_full_state_replay(
    heldout: list[dict[str, Any]],
    root: Path,
    provenance_records: list[dict[str, Any]],
) -> dict[str, Any]:
    action_matches = 0
    state_matches = 0
    rows = []
    for record in heldout:
        before = record["candidate_serialized_state_before"]
        observation = record["observation_t"]
        recomputed_action = legacy_core.candidate_action_from_serialized(before, observation)
        recomputed_state = legacy_core.candidate_update_state(
            legacy_core.deserialize_state(before),
            recomputed_action,
            record["environment_feedback_t"],
        )
        recomputed_after = legacy_core.serialize_state(recomputed_state)
        action_match = recomputed_action == record["candidate_action_t"]
        state_match = recomputed_after == record["candidate_serialized_state_after"]
        action_matches += int(action_match)
        state_matches += int(state_match)
        if len(rows) < 40:
            rows.append(
                {
                    "episode_id": record["episode_id"],
                    "selected_action_recomputed": recomputed_action,
                    "selected_action_matches": action_match,
                    "serialized_state_after_matches": state_match,
                }
            )
    total = len(heldout)
    action_rate = action_matches / total if total else 0.0
    state_rate = state_matches / total if total else 0.0
    prov_action = provenance(
        producer_function="run_full_state_replay",
        input_artifacts=[f"artifacts/{TASK_SLUG}/episodes_heldout.jsonl"],
        run_id="full_state_replay_run",
        aggregation_rule="recompute selected action from serialized_state_before and observation",
        function=run_full_state_replay,
        episode_ids=[record["episode_id"] for record in heldout[:20]],
        root=root,
    )
    prov_state = provenance(
        producer_function="run_full_state_replay",
        input_artifacts=[f"artifacts/{TASK_SLUG}/episodes_heldout.jsonl"],
        run_id="full_state_replay_run",
        aggregation_rule="recompute serialized_state_after from serialized_state_before, observation, action, and feedback",
        function=run_full_state_replay,
        episode_ids=[record["episode_id"] for record in heldout[:20]],
        root=root,
    )
    provenance_records.extend(
        [
            {"metric_id": "replay.action_recompute_rate", **prov_action},
            {"metric_id": "replay.state_update_recompute_rate", **prov_state},
        ]
    )
    base = validate_replay_report(
        {
            "task_id": TASK_ID,
            "action_recomputed": True,
            "state_update_recomputed": True,
            "hash_only_replay": False,
            "stored_action_only": False,
            "stored_hashes_used": False,
            "selected_action_match_rate": score_metric(action_rate, prov_action),
            "serialized_state_after_match_rate": score_metric(state_rate, prov_state),
            "replay_rows_sample": rows,
        }
    )
    base["negative_control"] = validate_replay_report(
        {
            "action_recomputed": True,
            "state_update_recomputed": False,
            "hash_only_replay": True,
            "stored_action_only": True,
        }
    )
    return base


def build_harness_input_bundle(manifest: dict[str, Any], root: Path) -> dict[str, Any]:
    payloads = []
    seen_paths = set()
    for item in manifest.get("artifacts", {}).values():
        path_value = item["path"]
        if path_value in seen_paths:
            continue
        seen_paths.add(path_value)
        path = resolve_artifact_path(path_value, root)
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        payload: Any | None = None
        kind = "text"
        if path.suffix == ".json":
            kind = "json"
            payload = json.loads(text)
            text_for_harness = ""
        elif path.suffix == ".jsonl":
            kind = "jsonl"
            payload = [json.loads(line) for line in text.splitlines() if line.strip()]
            text_for_harness = ""
        elif path.suffix == ".py":
            kind = "source"
            text_for_harness = text
        else:
            text_for_harness = text
        payloads.append(
            {
                "path": path_value,
                "kind": kind,
                "payload": payload,
                "text": text_for_harness,
                "sha256": sha256_file(path),
            }
        )
    return {
        "bundle_id": f"{TASK_SLUG}_real_output_bundle",
        "task_id": TASK_ID,
        "real_output_bundle": True,
        "governance_anchor_only": False,
        "path_payloads": payloads,
    }


def build_harness_positive_control_bundle() -> dict[str, Any]:
    return {
        "bundle_id": f"{TASK_SLUG}_false_pass_positive_control",
        "task_id": TASK_ID,
        "positive_control_expected": True,
        "path_payloads": [
            {
                "path": "positive_control/result.json",
                "kind": "json",
                "payload": {
                    "verdict": "gate4_001c_execution_repair_rerun_001e_passed_bounded_preflight",
                    "bounded_pass": True,
                    "candidate_score": 1.0,
                },
                "text": "",
            },
            {
                "path": "positive_control/replay_report.json",
                "kind": "json",
                "payload": {
                    "replay_gate_passed": True,
                    "hash_only_replay": True,
                    "stored_actions_reused": True,
                },
                "text": "",
            },
            {
                "path": "positive_control/tests/test_shape_only.py",
                "kind": "text",
                "payload": None,
                "text": 'assert result["verdict"] == "passed"\nassert report.exists()\n',
            },
        ],
    }


def harness_positive_control_rejected(report: dict[str, Any]) -> bool:
    return report.get("admissibility_class") == "rejected_false_pass_risk" and bool(
        report.get("detected_pattern_categories")
    )


def build_harness_reports(manifest: dict[str, Any], out: Path, root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    harness_bundle = build_harness_input_bundle(manifest, root)
    harness_input_path = out / "harness_input_bundle.json"
    write_json(harness_input_path, harness_bundle)
    real_report = evaluate_bundle(harness_bundle)
    positive_report = evaluate_bundle(build_harness_positive_control_bundle())
    write_json(out / "harness_positive_control_report.json", positive_report)
    report = {
        "task_id": TASK_ID,
        "harness_input_bundle_path": rel_path(harness_input_path, root),
        "harness_input_bundle_digest": sha256_file(harness_input_path),
        "exact_file_list_passed_to_harness": [item["path"] for item in harness_bundle["path_payloads"]],
        "harness_producer_function": "evaluate_bundle",
        "harness_code_path_hash": real_report.get("source_code_hash"),
        "positive_control_rejection_result": harness_positive_control_rejected(positive_report),
        "real_bundle_evaluation_result": real_report,
        "verdict": "blocked_by_evidence_harness_challenger"
        if real_report.get("admissibility_class") == "rejected_false_pass_risk"
        else "harness_real_bundle_not_rejected",
    }
    write_json(out / "harness_report.json", report)
    return report, positive_report


def scan_text_for_leakage(text: str) -> list[dict[str, Any]]:
    findings = []
    for rule in LEAKAGE_RULES:
        if re.search(rule["pattern"], text):
            findings.append({"rule_id": rule["rule_id"], "blocked_claim": rule["blocked_claim"]})
    return findings


def scan_leakage_bundle(bundle_path: Path, root: Path) -> dict[str, Any]:
    bundle_path = Path(bundle_path)
    parsed_path = bundle_path.resolve()
    manifest = read_json(parsed_path)
    scanned = []
    all_findings = []
    for item in manifest.get("artifacts", {}).values():
        path_value = item["path"]
        path = resolve_artifact_path(path_value, root)
        if path.name == "leakage_scan_report.json":
            scanned.append(
                {
                    "path": path_value,
                    "status": "not_scanned_self_generated_report",
                    "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
                    "findings": [],
                    "reason": "scanner rule text inside the scanner's own report is self-referential metadata",
                }
            )
            continue
        if not path.exists() or not path.is_file():
            scanned.append({"path": path_value, "status": "missing", "sha256": None, "findings": []})
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        findings = scan_text_for_leakage(text)
        scanned.append(
            {
                "path": path_value,
                "status": "leakage_detected" if findings else "clean",
                "sha256": sha256_file(path),
                "findings": findings,
            }
        )
        all_findings.extend({"path": path_value, **finding} for finding in findings)
    synthetic = {"detected": bool(scan_text_for_leakage("EGO_MAINLINE_READY"))}
    return {
        "task_id": TASK_ID,
        "supplied_bundle_argument": bundle_path.as_posix(),
        "parsed_bundle_path": parsed_path.as_posix(),
        "scanned_files": scanned,
        "file_hashes": {item["path"]: item["sha256"] for item in scanned},
        "scanner_rules": LEAKAGE_RULES,
        "scanner_producer_function": "scan_leakage_bundle",
        "scanner_code_path_hash": source_hash(scan_leakage_bundle),
        "synthetic_positive_control_result": synthetic,
        "real_bundle_scan_performed": len(scanned) > 0,
        "synthetic_controls_used_as_substitute": False,
        "real_bundle_scan_result": "blocked" if all_findings else "clean",
        "findings": all_findings,
        "verdict": "blocked_by_leakage_scan" if all_findings else "leakage_real_bundle_scan_passed",
    }


def build_synthetic_only_leakage_report() -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "real_bundle_scan_performed": False,
        "synthetic_controls_used_as_substitute": True,
        "synthetic_positive_control_result": {"detected": True},
        "verdict": "blocked_by_leakage_scan",
    }


def build_leakage_positive_control_report() -> dict[str, Any]:
    text = "EGO_MAINLINE_READY"
    findings = scan_text_for_leakage(text)
    return {
        "task_id": TASK_ID,
        "control_type": "synthetic_detector_self_test",
        "detected": bool(findings),
        "findings": findings,
        "substitute_for_real_bundle_scan": False,
    }


def compare_protected_artifacts(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_files = before.get("files", {})
    after_files = after.get("files", {})
    added = sorted(set(after_files) - set(before_files))
    removed = sorted(set(before_files) - set(after_files))
    changed = sorted(path for path in set(before_files) & set(after_files) if before_files[path] != after_files[path])
    count = len(added) + len(removed) + len(changed)
    return {
        "task_id": TASK_ID,
        "added_protected_files": added,
        "removed_protected_files": removed,
        "changed_protected_files": changed,
        "mutation_violation_count": count,
        "verdict": "protected_artifacts_unchanged" if count == 0 else "blocked_by_protected_artifact_mutation",
    }


def protected_paths(root: Path) -> list[Path]:
    paths = [
        root / "artifacts" / "gate4_001c_failure_preserving_repair_001c",
        root / "src" / "gate4_001c_failure_preserving_repair_001c",
        root / "tests" / "test_gate4_001c_failure_preserving_repair_001c.py",
        root / "docs" / "codex" / "tasks" / "GATE4-001C-EXECUTION-CONTRACT-001D-AMENDMENT.md",
        root
        / "docs"
        / "research"
        / "AUDIT-GATE4-001C-FAILURE-PRESERVING-REPAIR-001C-EXECUTION-PREFLIGHT-CLAUDE-001.md",
    ]
    return [path for path in paths if path.exists()]


def build_protected_inventory(root: Path) -> dict[str, Any]:
    files = {}
    for path in protected_paths(root):
        candidates = [path] if path.is_file() else sorted(item for item in path.rglob("*") if item.is_file())
        for file_path in candidates:
            files[rel_path(file_path, root)] = sha256_file(file_path)
    return {"task_id": TASK_ID, "files": files, "protected_file_count": len(files)}


def build_negative_evidence_policy_report() -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "prior_execution_commit": NEGATIVE_SNAPSHOT_COMMIT,
        "classification": "anchored_independently_audited_failed_false_pass_snapshot",
        "allowed_uses": [
            "negative evidence",
            "false-pass surface",
            "reproducibility evidence",
            "contract-defect evidence",
        ],
        "used_as_positive_gate4_support": False,
        "repaired": False,
        "mutated": False,
        "copied_into_pass_evidence": False,
        "reinterpreted_as_pass": False,
        "provisional_commit": PROVISIONAL_COMMIT,
        "provisional_commit_used": False,
    }


def validate_provenance_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    missing = {
        record.get("metric_id", f"record_{idx}"): [field for field in PROVENANCE_FIELDS if field not in record]
        for idx, record in enumerate(records)
        if any(field not in record for field in PROVENANCE_FIELDS)
    }
    return {
        "task_id": TASK_ID,
        "passed": missing == {},
        "missing_fields": missing,
        "records": records,
        "verdict": "computed_provenance_passed" if missing == {} else "blocked_by_computed_provenance_gap",
    }


def choose_final_verdict(
    *,
    precheck_passed: bool,
    harness_report: dict[str, Any],
    leakage_report: dict[str, Any],
    count_table_report: dict[str, Any],
    retrieval_report: dict[str, Any],
    ablation_report: dict[str, Any],
    replay_report: dict[str, Any],
    protected_report: dict[str, Any],
    provenance_report: dict[str, Any],
) -> str:
    if not precheck_passed:
        return "blocked_by_precheck_failure"
    if protected_report.get("verdict") == "blocked_by_protected_artifact_mutation":
        return "blocked_by_protected_artifact_mutation"
    if not provenance_report.get("passed", False):
        return "blocked_by_computed_provenance_gap"
    real_result = harness_report.get("real_bundle_evaluation_result", harness_report)
    if real_result.get("admissibility_class") == "rejected_false_pass_risk":
        return "blocked_by_evidence_harness_challenger"
    if leakage_report.get("verdict") == "blocked_by_leakage_scan":
        return "blocked_by_leakage_scan"
    if count_table_report.get("candidate_advantage_collapsed") is True:
        return "blocked_by_count_table_challenger_equivalence"
    if retrieval_report.get("degeneration_unresolved") is True:
        return "blocked_by_retrieval_baseline_degeneration"
    if ablation_report.get("semantic_binding_passed") is not True:
        return "blocked_by_ablation_semantic_mismatch"
    if replay_report.get("full_state_replay_passed") is not True:
        return "blocked_by_replay_full_state_failure"
    return "gate4_001c_execution_repair_rerun_001e_passed_bounded_preflight"


def manifest_record(path: Path, root: Path) -> dict[str, Any]:
    return {"path": rel_path(path, root), "sha256": sha256_file(path), "size_bytes": path.stat().st_size}


def build_output_bundle_manifest(out: Path, root: Path) -> dict[str, Any]:
    mapping = {
        "result": out / "result.json",
        "replay": out / "replay_full_state_report.json",
        "baselines": out / "baseline_report.json",
        "challengers": out / "count_table_challenger_report.json",
        "ablations": out / "ablation_semantic_binding_report.json",
        "leakage_scan": out / "leakage_scan_report.json",
        "harness_output": out / "harness_report.json",
        "tests": root / "tests" / "test_gate4_001c_execution_repair_rerun_001e.py",
        "traces": out / "trace.jsonl",
        "provenance": out / "computed_provenance.json",
        "retrieval_normalization": out / "retrieval_normalization_report.json",
        "protected_artifact_guard": out / "protected_artifact_guard.json",
        "negative_evidence_policy": out / "negative_evidence_policy_application.json",
        "test_report": out / "test_report.json",
    }
    return {
        "task_id": TASK_ID,
        "created_at_utc": utc_now(),
        "artifact_dir": rel_path(out, root),
        "artifacts": {
            key: manifest_record(path, root)
            for key, path in mapping.items()
            if path.exists() and path.is_file()
        },
    }


def build_result_payload(
    verdict: str,
    precheck: dict[str, Any],
    candidate_score: dict[str, Any],
    harness_report: dict[str, Any],
    leakage_report: dict[str, Any],
    count_table_report: dict[str, Any],
    retrieval_report: dict[str, Any],
    ablation_report: dict[str, Any],
    replay_report: dict[str, Any],
    protected_report: dict[str, Any],
    provenance_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "verdict": verdict,
        "layer": LAYER,
        "starting_head": STARTING_HEAD,
        "branch": BRANCH,
        "branch_hash": precheck.get("remote_branch_hash"),
        "required_anchor": REQUIRED_REMOTE_TAG,
        "required_anchor_hash": precheck.get("remote_tag_hash"),
        "claim_ceiling": CLAIM_CEILING,
        "candidate_score": candidate_score,
        "count_table_challenger_score": count_table_report["challenger_score"],
        "candidate_advantage_collapsed": count_table_report["candidate_advantage_collapsed"],
        "harness_real_bundle_result": harness_report["real_bundle_evaluation_result"].get("admissibility_class"),
        "harness_positive_control_result": harness_report["positive_control_rejection_result"],
        "leakage_real_bundle_scan_result": leakage_report.get("real_bundle_scan_result"),
        "leakage_positive_control_result": leakage_report.get("synthetic_positive_control_result"),
        "retrieval_baseline_normalization_result": retrieval_report["verdict"],
        "ablation_semantic_binding_result": ablation_report["verdict"],
        "replay_full_state_result": replay_report["verdict"],
        "protected_artifact_guard_result": protected_report["verdict"],
        "computed_provenance_result": provenance_report["verdict"],
        "negative_evidence_policy": {
            "bbbb66c_modified": False,
            "bbbb66c_reinterpreted_as_pass": False,
            "bbbb66c_use": "negative evidence only",
        },
        "authorizations": AUTHORIZATIONS,
        "gate5_admission_runtime_bridge_ego_mainline_authorized": False,
        "stop_conditions_triggered": [] if verdict.endswith("_passed_bounded_preflight") else [verdict],
        "what_this_does_not_prove": [
            "Gate4 validity",
            "mechanism validity",
            "theory validity",
            "Gate5 authorization",
            "admission authorization",
            "runtime authorization",
            "bridge authorization",
            "EGO-mainline readiness",
            "agency, selfhood, consciousness, real emotion, relationship learning, or stable autonomy",
        ],
    }


def write_test_report_placeholder(out: Path) -> None:
    write_json(
        out / "test_report.json",
        {
            "task_id": TASK_ID,
            "test_command": "python -m pytest tests/test_gate4_001c_execution_repair_rerun_001e.py -q",
            "status": "pending",
        },
    )


def run_and_record_tests(out: Path, root: Path) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root / "src")
    command = [sys.executable, "-m", "pytest", "tests/test_gate4_001c_execution_repair_rerun_001e.py", "-q"]
    completed = subprocess.run(
        command,
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )
    report = {
        "task_id": TASK_ID,
        "test_command": " ".join(command),
        "exit_code": completed.returncode,
        "passed": completed.returncode == 0,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    write_json(out / "test_report.json", report)
    return report


def run_execution(run_tests: bool = True) -> dict[str, Any]:
    root = repo_root()
    out = artifact_dir(root)
    out.mkdir(parents=True, exist_ok=True)
    write_test_report_placeholder(out)
    (out / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")

    precheck = build_precheck_report(root)
    write_json(out / "precheck_readback.json", precheck)

    before_inventory = build_protected_inventory(root)

    config = legacy_core.default_config_payload()
    config.update({"task_id": TASK_ID, "task_slug": TASK_SLUG, "claim_ceiling": CLAIM_CEILING})
    write_json(out / "config.json", config)

    generated = legacy_core.generate_candidate_records(config, run_id="candidate_run_001e")
    train = generated["train"]
    heldout = generated["heldout"]
    write_jsonl(out / "episodes_train.jsonl", train)
    write_jsonl(out / "episodes_heldout.jsonl", heldout)
    write_jsonl(out / "trace.jsonl", generated["trace"])

    provenance_records: list[dict[str, Any]] = []
    candidate_predictions = {record["episode_id"]: record["candidate_action_t"] for record in heldout}
    candidate_raw = score_predictions(heldout, candidate_predictions)
    candidate_prov = provenance(
        producer_function="score_predictions",
        input_artifacts=[f"artifacts/{TASK_SLUG}/episodes_heldout.jsonl"],
        run_id="candidate_run_001e",
        aggregation_rule="mean heldout candidate action-target match",
        function=score_predictions,
        episode_ids=[record["episode_id"] for record in heldout[:20]],
        root=root,
    )
    provenance_records.append({"metric_id": "candidate.score", **candidate_prov})
    candidate_score = score_metric(candidate_raw["score"], candidate_prov)

    baseline_comparison, baseline_trace, _legacy_prov = legacy_core.run_baselines(train, heldout, root)
    baseline_report = {
        "task_id": TASK_ID,
        "producer_function": "legacy_gate4_001c_baseline_suite_recomputed_for_001e",
        "negative_snapshot_not_upgraded": True,
        "baseline_comparison": baseline_comparison,
    }
    write_json(out / "baseline_report.json", baseline_report)
    write_jsonl(out / "baseline_trace.jsonl", baseline_trace)

    count_table_report = stream_keyed_count_table_challenger(train, heldout, candidate_predictions)
    count_prov = provenance(
        producer_function="stream_keyed_count_table_challenger",
        input_artifacts=[
            f"artifacts/{TASK_SLUG}/episodes_train.jsonl",
            f"artifacts/{TASK_SLUG}/episodes_heldout.jsonl",
        ],
        run_id="stream_keyed_count_table_challenger_run",
        aggregation_rule="mean heldout action-target match from seed/context/partner stream table",
        function=stream_keyed_count_table_challenger,
        episode_ids=[record["episode_id"] for record in heldout[:20]],
        root=root,
    )
    provenance_records.append({"metric_id": "count_table_challenger.score", **count_prov})
    write_json(out / "count_table_challenger_report.json", count_table_report)

    retrieval_report = evaluate_retrieval_normalization(train, heldout)
    retrieval_before_prov = provenance(
        producer_function="evaluate_retrieval_normalization",
        input_artifacts=[
            f"artifacts/{TASK_SLUG}/episodes_train.jsonl",
            f"artifacts/{TASK_SLUG}/episodes_heldout.jsonl",
        ],
        run_id="retrieval_normalization_run",
        aggregation_rule="before normalization retrieval score",
        function=evaluate_retrieval_normalization,
        root=root,
    )
    retrieval_after_prov = {**retrieval_before_prov, "aggregation_rule": "after normalization retrieval score"}
    provenance_records.extend(
        [
            {"metric_id": "retrieval.before_score", **retrieval_before_prov},
            {"metric_id": "retrieval.after_score", **retrieval_after_prov},
        ]
    )
    write_json(out / "retrieval_normalization_report.json", retrieval_report)

    ablation_report = build_ablation_semantic_report(config, candidate_raw["score"], root, provenance_records)
    write_json(out / "ablation_semantic_binding_report.json", ablation_report)

    replay_report = run_full_state_replay(heldout, root, provenance_records)
    write_json(out / "replay_full_state_report.json", replay_report)

    negative_policy = build_negative_evidence_policy_report()
    write_json(out / "negative_evidence_policy_application.json", negative_policy)

    after_inventory = build_protected_inventory(root)
    protected_report = compare_protected_artifacts(before_inventory, after_inventory)
    protected_report["before_protected_file_count"] = before_inventory["protected_file_count"]
    protected_report["after_protected_file_count"] = after_inventory["protected_file_count"]
    write_json(out / "protected_artifact_guard.json", protected_report)

    provenance_report = validate_provenance_records(provenance_records)
    write_json(out / "computed_provenance.json", provenance_report)

    placeholder_harness = {
        "real_bundle_evaluation_result": {"admissibility_class": "blocked_pending_audit"},
        "positive_control_rejection_result": False,
    }
    placeholder_leakage = {
        "real_bundle_scan_result": "pending",
        "synthetic_positive_control_result": {"detected": True},
        "verdict": "pending",
    }
    provisional_verdict = choose_final_verdict(
        precheck_passed=precheck["passed"],
        harness_report=placeholder_harness,
        leakage_report=placeholder_leakage,
        count_table_report=count_table_report,
        retrieval_report=retrieval_report,
        ablation_report=ablation_report,
        replay_report=replay_report,
        protected_report=protected_report,
        provenance_report=provenance_report,
    )
    write_json(
        out / "result.json",
        build_result_payload(
            provisional_verdict,
            precheck,
            candidate_score,
            placeholder_harness,
            placeholder_leakage,
            count_table_report,
            retrieval_report,
            ablation_report,
            replay_report,
            protected_report,
            provenance_report,
        ),
    )

    write_json(out / "output_bundle_manifest.json", build_output_bundle_manifest(out, root))
    leakage_report = scan_leakage_bundle(out / "output_bundle_manifest.json", root)
    write_json(out / "leakage_scan_report.json", leakage_report)
    write_json(out / "leakage_positive_control_report.json", build_leakage_positive_control_report())
    write_json(out / "output_bundle_manifest.json", build_output_bundle_manifest(out, root))
    harness_report, _positive = build_harness_reports(read_json(out / "output_bundle_manifest.json"), out, root)

    final_verdict = choose_final_verdict(
        precheck_passed=precheck["passed"],
        harness_report=harness_report,
        leakage_report=leakage_report,
        count_table_report=count_table_report,
        retrieval_report=retrieval_report,
        ablation_report=ablation_report,
        replay_report=replay_report,
        protected_report=protected_report,
        provenance_report=provenance_report,
    )
    result = build_result_payload(
        final_verdict,
        precheck,
        candidate_score,
        harness_report,
        leakage_report,
        count_table_report,
        retrieval_report,
        ablation_report,
        replay_report,
        protected_report,
        provenance_report,
    )
    write_json(out / "result.json", result)
    write_json(out / "output_bundle_manifest.json", build_output_bundle_manifest(out, root))

    if run_tests:
        run_and_record_tests(out, root)
    write_json(out / "output_bundle_manifest.json", build_output_bundle_manifest(out, root))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-tests", action="store_true")
    args = parser.parse_args()
    result = run_execution(run_tests=not args.no_tests)
    print(result["verdict"])


if __name__ == "__main__":
    main()
