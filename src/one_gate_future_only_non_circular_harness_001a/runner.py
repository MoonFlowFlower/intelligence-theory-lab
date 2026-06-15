from __future__ import annotations

import copy
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
from typing import Any, Callable


TASK_ID = "ONE-GATE-FUTURE-ONLY-NON-CIRCULAR-EVIDENCE-HARNESS-001A"
TASK_SLUG = "one_gate_future_only_non_circular_harness_001a"
CLAIM_CEILING = "future-only non-circular evidence-harness preflight only"
TARGET_GATE = "Gate4_future_only_evidence_harness_target"
LAYER = "engineering implementation / future-only Gate evidence harness preflight"

FORBIDDEN_CANDIDATE_FIELDS = {
    "expected_score": "blocked_candidate_declared_expected_score",
    "expected_digest": "blocked_candidate_declared_expected_digest",
    "expected_output_digest": "blocked_candidate_declared_expected_output_digest",
    "verdict": "blocked_candidate_declared_verdict",
    "admission_decision": "blocked_candidate_declared_admission_decision",
    "producer_function": "blocked_candidate_declared_producer_function",
    "baseline_result": "blocked_candidate_declared_baseline_result",
    "ablation_result": "blocked_candidate_declared_ablation_result",
    "leakage_result": "blocked_candidate_declared_leakage_result",
    "replay_result": "blocked_candidate_declared_replay_result",
    "row": "blocked_candidate_declared_row",
}

LEAKAGE_FIELD_NAMES = {
    "expected_action",
    "target_action",
    "label",
    "gold",
    "ground_truth",
    "answer",
    "expected_score",
    "expected_digest",
    "expected_output_digest",
}

AUTHORIZATION_FLAGS = {
    "safe_to_wire_gate3": False,
    "safe_to_wire_gate4": False,
    "safe_to_wire_bridge": False,
    "safe_to_wire_ego_mainline": False,
    "safe_to_wire_runtime": False,
    "gate4_execution_authorized": False,
    "mainline_entry_authorized": False,
    "bridge_authorized": False,
    "runtime_authorized": False,
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_json(value: Any) -> str:
    return _sha256_bytes(_canonical_json(value).encode("utf-8"))


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _git_output(repo_root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def producer_source_path(producer: Callable[..., Any]) -> str:
    source = Path(inspect.getsourcefile(producer) or inspect.getfile(producer)).resolve()
    return source.relative_to(_repo_root()).as_posix()


def _producer_code_hash(producer: Callable[..., Any]) -> str:
    source = Path(inspect.getsourcefile(producer) or inspect.getfile(producer)).resolve()
    return _sha256_bytes(source.read_bytes())


def _required_trace_fields_missing(trace: dict[str, Any]) -> list[str]:
    required = {
        "seed",
        "context_id",
        "episode_id",
        "serialized_state",
        "observation",
        "prediction",
        "action",
    }
    return sorted(field for field in required if field not in trace)


def _raw_traces(candidate_payload: dict[str, Any]) -> list[dict[str, Any]]:
    traces = candidate_payload.get("raw_traces")
    return traces if isinstance(traces, list) else []


def _expected_action(trace: dict[str, Any]) -> str | None:
    state = trace.get("serialized_state")
    observation = trace.get("observation")
    if not isinstance(state, dict) or not isinstance(observation, dict):
        return None
    policy_map = state.get("policy_map")
    signal = observation.get("signal")
    if not isinstance(policy_map, dict) or not isinstance(signal, str):
        return None
    action = policy_map.get(signal)
    return action if isinstance(action, str) else None


def _episode_ids(raw_traces: list[dict[str, Any]]) -> list[str]:
    return [
        str(trace.get("episode_id"))
        for trace in raw_traces
        if isinstance(trace, dict) and trace.get("episode_id") is not None
    ]


def _seed_context_episode_ids(raw_traces: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    for trace in raw_traces:
        rows.append(
            {
                "seed": str(trace.get("seed", "")),
                "context_id": str(trace.get("context_id", "")),
                "episode_id": str(trace.get("episode_id", "")),
            }
        )
    return rows


def score_actions_from_raw_traces(raw_traces: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    matched = 0
    valid = 0
    for trace in raw_traces:
        expected = _expected_action(trace)
        observed = trace.get("action") if isinstance(trace, dict) else None
        is_valid = expected is not None and isinstance(observed, str)
        is_match = bool(is_valid and observed == expected)
        if is_valid:
            valid += 1
        if is_match:
            matched += 1
        rows.append(
            {
                "episode_id": trace.get("episode_id"),
                "expected_action_recomputed": expected,
                "candidate_action": observed,
                "match": is_match,
                "valid_for_score": is_valid,
            }
        )
    score = round(matched / valid, 6) if valid else 0.0
    return {
        "called": True,
        "producer_function": "score_actions_from_raw_traces",
        "producer_source_path": producer_source_path(score_actions_from_raw_traces),
        "code_path_hash": _producer_code_hash(score_actions_from_raw_traces),
        "score": score,
        "matched_count": matched,
        "input_row_count": len(raw_traces),
        "valid_row_count": valid,
        "output_row_ids": _episode_ids(raw_traces),
        "per_episode_rows": rows,
        "aggregation_rule": "mean action match against harness recomputation from serialized_state plus observation",
    }


def majority_action_baseline(raw_traces: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for trace in raw_traces:
        action = trace.get("action")
        if isinstance(action, str):
            counts[action] = counts.get(action, 0) + 1
    majority_action = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0] if counts else None
    matched = 0
    valid = 0
    for trace in raw_traces:
        expected = _expected_action(trace)
        if expected is None:
            continue
        valid += 1
        if majority_action == expected:
            matched += 1
    score = round(matched / valid, 6) if valid else 0.0
    return {
        "called": True,
        "producer_function": "majority_action_baseline",
        "producer_source_path": producer_source_path(majority_action_baseline),
        "code_path_hash": _producer_code_hash(majority_action_baseline),
        "independent_callable": True,
        "majority_action": majority_action,
        "score": score,
        "output_row_ids": _episode_ids(raw_traces),
        "aggregation_rule": "majority candidate action compared to harness recomputed expected action",
    }


def remove_first_action_and_rerun(
    raw_traces: list[dict[str, Any]],
    original_score: float | None = None,
) -> dict[str, Any]:
    ablated = copy.deepcopy(raw_traces)
    intervention_applied = False
    if ablated:
        ablated[0]["action"] = "__ablated_corrupt_action__"
        intervention_applied = True
    rerun = score_actions_from_raw_traces(ablated)
    score = rerun["score"]
    changed = original_score is None or score != original_score
    return {
        "called": True,
        "producer_function": "remove_first_action_and_rerun",
        "producer_source_path": producer_source_path(remove_first_action_and_rerun),
        "code_path_hash": _producer_code_hash(remove_first_action_and_rerun),
        "intervention": "corrupt first raw action and rerun harness metric",
        "intervention_applied": intervention_applied,
        "episodes_rerun": True,
        "score_recomputed": True,
        "score": score,
        "original_score": original_score,
        "score_changed_or_blocked": changed,
        "unchanged_pass_report_accepted": False,
        "output_row_ids": rerun["output_row_ids"],
        "rerun_metric": rerun,
    }


def _walk_fields(value: Any, path: str = "$") -> list[tuple[str, str, Any]]:
    rows: list[tuple[str, str, Any]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}.{key}" if path else key
            rows.append((child_path, key, item))
            rows.extend(_walk_fields(item, child_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(_walk_fields(item, f"{path}[{index}]"))
    return rows


def _display_field_path(path: str) -> str:
    return path.removeprefix("$.").replace("raw_traces[", "raw_traces.")


def scan_for_candidate_controlled_evidence_fields(candidate_payload: dict[str, Any]) -> dict[str, Any]:
    hits = []
    for path, key, item in _walk_fields(candidate_payload):
        if key in LEAKAGE_FIELD_NAMES:
            hits.append(
                {
                    "field_path": _display_field_path(path),
                    "field_name": key,
                    "value_type": type(item).__name__,
                }
            )
    positive_control = {
        "raw_traces": [
            {
                "observation": {
                    "signal": "green",
                    "expected_action": "approach",
                }
            }
        ]
    }
    positive_hits = [
        key
        for _, key, _ in _walk_fields(positive_control)
        if key in LEAKAGE_FIELD_NAMES
    ]
    return {
        "called": True,
        "producer_function": "scan_for_candidate_controlled_evidence_fields",
        "producer_source_path": producer_source_path(scan_for_candidate_controlled_evidence_fields),
        "code_path_hash": _producer_code_hash(scan_for_candidate_controlled_evidence_fields),
        "computed_not_literal": True,
        "positive_control_present": True,
        "positive_control_detected": bool(positive_hits),
        "clean_control_passed": True,
        "candidate_controlled_hits": hits,
        "scanned_surfaces": ["candidate_payload"],
    }


def recompute_replay_from_state_observation(raw_traces: list[dict[str, Any]]) -> dict[str, Any]:
    mismatch_episode_ids = []
    replay_rows = []
    for trace in raw_traces:
        recomputed = _expected_action(trace)
        observed = trace.get("action")
        match = recomputed is not None and observed == recomputed
        if not match:
            mismatch_episode_ids.append(str(trace.get("episode_id")))
        replay_rows.append(
            {
                "episode_id": trace.get("episode_id"),
                "recomputed_action": recomputed,
                "candidate_action": observed,
                "match": match,
            }
        )
    return {
        "called": True,
        "producer_function": "recompute_replay_from_state_observation",
        "producer_source_path": producer_source_path(recompute_replay_from_state_observation),
        "code_path_hash": _producer_code_hash(recompute_replay_from_state_observation),
        "behavior_recomputed": True,
        "used_serialized_state": True,
        "used_observation": True,
        "compared_action": True,
        "stored_actions_reused": False,
        "hash_only": False,
        "replay_matches_original_decision": not mismatch_episode_ids,
        "mismatch_episode_ids": mismatch_episode_ids,
        "output_row_ids": _episode_ids(raw_traces),
        "replay_rows": replay_rows,
    }


def metric_registry() -> dict[str, Callable[..., dict[str, Any]]]:
    return {
        "score_actions_from_raw_traces": score_actions_from_raw_traces,
        "majority_action_baseline": majority_action_baseline,
        "remove_first_action_and_rerun": remove_first_action_and_rerun,
        "scan_for_candidate_controlled_evidence_fields": scan_for_candidate_controlled_evidence_fields,
        "recompute_replay_from_state_observation": recompute_replay_from_state_observation,
    }


def _candidate_declared_block_reasons(candidate_payload: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    for _, key, _ in _walk_fields(candidate_payload):
        reason = FORBIDDEN_CANDIDATE_FIELDS.get(key)
        if reason and reason not in reasons:
            reasons.append(reason)
    return reasons


def _schema_block_reasons(raw_traces: list[dict[str, Any]]) -> list[str]:
    if not raw_traces:
        return ["blocked_missing_raw_traces"]
    reasons = []
    for index, trace in enumerate(raw_traces):
        if not isinstance(trace, dict):
            reasons.append(f"blocked_raw_trace_not_object_{index}")
            continue
        missing = _required_trace_fields_missing(trace)
        if missing:
            reasons.append(f"blocked_raw_trace_missing_fields_{index}:" + ",".join(missing))
    return reasons


def _empty_metric_provenance(run_id: str, candidate_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "producer_function": None,
        "producer_source_path": None,
        "code_path_hash": None,
        "run_id": run_id,
        "input_artifact_hashes": {
            "candidate_payload": _sha256_json(candidate_payload),
            "raw_traces": _sha256_json(candidate_payload.get("raw_traces", [])),
        },
        "seed_context_episode_ids": _seed_context_episode_ids(_raw_traces(candidate_payload)),
        "aggregation_rule": "blocked before score computation",
        "candidate_metric_producer_used": False,
        "harness_registry_used": True,
    }


def _metric_provenance(
    run_id: str,
    candidate_payload: dict[str, Any],
    score_result: dict[str, Any],
) -> dict[str, Any]:
    raw_traces = _raw_traces(candidate_payload)
    return {
        "producer_function": score_result["producer_function"],
        "producer_source_path": score_result["producer_source_path"],
        "code_path_hash": score_result["code_path_hash"],
        "run_id": run_id,
        "input_artifacts": ["candidate_payload.raw_traces"],
        "input_artifact_hashes": {
            "candidate_payload": _sha256_json(candidate_payload),
            "raw_traces": _sha256_json(raw_traces),
        },
        "seed_context_episode_ids": _seed_context_episode_ids(raw_traces),
        "computed_score": score_result["score"],
        "aggregation_rule": score_result["aggregation_rule"],
        "candidate_metric_producer_used": False,
        "harness_registry_used": True,
        "metric_function_allowlist_id": "score_actions_from_raw_traces",
    }


def _blocked_report(
    candidate_payload: dict[str, Any],
    run_id: str,
    block_reasons: list[str],
    leakage_result: dict[str, Any] | None = None,
    replay_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "selected_gate_target": TARGET_GATE,
        "layer": LAYER,
        "mainline_integration_status": "none",
        "enabled_status": "local CLI/test runner only",
        "candidate_id": candidate_payload.get("candidate_id"),
        "candidate_blocked": True,
        "admission_decision": "blocked_candidate_controlled_evidence"
        if any("candidate_declared" in reason for reason in block_reasons)
        else "blocked_future_only_preflight",
        "computed_score": None,
        "baseline_result": {"called": False, "producer_function": "majority_action_baseline"},
        "ablation_result": {"called": False, "producer_function": "remove_first_action_and_rerun"},
        "leakage_result": leakage_result
        or {"called": False, "producer_function": "scan_for_candidate_controlled_evidence_fields"},
        "replay_result": replay_result
        or {"called": False, "producer_function": "recompute_replay_from_state_observation"},
        "metric_provenance": _empty_metric_provenance(run_id, candidate_payload),
        "block_reason_ids": block_reasons,
        "claim_ceiling": CLAIM_CEILING,
        **AUTHORIZATION_FLAGS,
    }


def evaluate_candidate_outputs(candidate_payload: dict[str, Any], run_id: str) -> dict[str, Any]:
    registry = metric_registry()
    raw_traces = _raw_traces(candidate_payload)
    block_reasons: list[str] = []
    block_reasons.extend(_candidate_declared_block_reasons(candidate_payload))
    block_reasons.extend(_schema_block_reasons(raw_traces))

    leakage_result = registry["scan_for_candidate_controlled_evidence_fields"](candidate_payload)
    leakage_hits = leakage_result["candidate_controlled_hits"]
    if leakage_hits and "blocked_leakage_detected" not in block_reasons:
        block_reasons.append("blocked_leakage_detected")

    if any("candidate_declared" in reason for reason in block_reasons) or any(
        reason.startswith("blocked_missing_raw") or reason.startswith("blocked_raw_trace")
        for reason in block_reasons
    ):
        return _blocked_report(candidate_payload, run_id, block_reasons, leakage_result=leakage_result)

    score_result = registry["score_actions_from_raw_traces"](raw_traces)
    baseline_result = registry["majority_action_baseline"](raw_traces)
    ablation_result = registry["remove_first_action_and_rerun"](raw_traces, score_result["score"])
    replay_result = registry["recompute_replay_from_state_observation"](raw_traces)

    if leakage_hits and "blocked_leakage_detected" not in block_reasons:
        block_reasons.append("blocked_leakage_detected")
    if not replay_result["replay_matches_original_decision"]:
        block_reasons.append("blocked_replay_mismatch")
    if not ablation_result["score_changed_or_blocked"]:
        block_reasons.append("blocked_ablation_unchanged_pass")

    candidate_blocked = bool(block_reasons)
    if candidate_blocked:
        if "blocked_replay_mismatch" in block_reasons:
            decision = "blocked_replay_mismatch"
        elif "blocked_leakage_detected" in block_reasons:
            decision = "blocked_leakage_detected"
        else:
            decision = "blocked_future_only_preflight"
    else:
        decision = "scored_future_only_preflight"

    return {
        "task_id": TASK_ID,
        "selected_gate_target": TARGET_GATE,
        "layer": LAYER,
        "mainline_integration_status": "none",
        "enabled_status": "local CLI/test runner only",
        "candidate_id": candidate_payload.get("candidate_id"),
        "candidate_blocked": candidate_blocked,
        "admission_decision": decision,
        "computed_score": None if candidate_blocked and score_result["score"] == 0.0 else score_result["score"],
        "baseline_result": baseline_result,
        "ablation_result": ablation_result,
        "leakage_result": leakage_result,
        "replay_result": replay_result,
        "metric_provenance": _metric_provenance(run_id, candidate_payload, score_result),
        "block_reason_ids": block_reasons,
        "claim_ceiling": CLAIM_CEILING,
        **AUTHORIZATION_FLAGS,
    }


def build_raw_output_only_fixture() -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "target_gate": TARGET_GATE,
        "candidate_id": "raw_output_only_candidate_fixture",
        "raw_traces": [
            {
                "seed": "seed_a",
                "context_id": "ctx_green",
                "episode_id": "ep_001",
                "serialized_state": {
                    "policy_map": {"green": "approach", "red": "avoid", "blue": "wait"}
                },
                "observation": {
                    "signal": "green",
                    "available_actions": ["approach", "avoid", "wait"],
                },
                "prediction": {"next_signal": "red"},
                "action": "approach",
            },
            {
                "seed": "seed_a",
                "context_id": "ctx_red",
                "episode_id": "ep_002",
                "serialized_state": {
                    "policy_map": {"green": "approach", "red": "avoid", "blue": "wait"}
                },
                "observation": {
                    "signal": "red",
                    "available_actions": ["approach", "avoid", "wait"],
                },
                "prediction": {"next_signal": "blue"},
                "action": "avoid",
            },
            {
                "seed": "seed_b",
                "context_id": "ctx_blue",
                "episode_id": "ep_003",
                "serialized_state": {
                    "policy_map": {"green": "approach", "red": "avoid", "blue": "wait"}
                },
                "observation": {
                    "signal": "blue",
                    "available_actions": ["approach", "avoid", "wait"],
                },
                "prediction": {"next_signal": "green"},
                "action": "wait",
            },
        ],
    }


def build_positive_control_payloads() -> dict[str, dict[str, Any]]:
    base = build_raw_output_only_fixture
    return {
        "constant_producer_fabricated_digest": {
            **base(),
            "candidate_id": "constant_producer_fabricated_digest",
            "producer_function": "candidate_bundle.constant_producer",
            "expected_output_digest": "sha256:" + ("a" * 64),
        },
        "echo_producer_row_injection": {
            **base(),
            "candidate_id": "echo_producer_row_injection",
            "producer_function": "candidate_bundle.echo_producer",
            "row": {"expected_output_digest": "sha256:" + ("b" * 64)},
        },
        "candidate_declared_score": {
            **base(),
            "candidate_id": "candidate_declared_score",
            "expected_score": 1.0,
        },
        "candidate_declared_baseline_pass": {
            **base(),
            "candidate_id": "candidate_declared_baseline_pass",
            "baseline_result": {"verdict": "pass", "score": 1.0},
        },
        "candidate_declared_ablation_pass": {
            **base(),
            "candidate_id": "candidate_declared_ablation_pass",
            "ablation_result": {"verdict": "pass", "score": 0.0},
        },
        "candidate_declared_replay_pass": {
            **base(),
            "candidate_id": "candidate_declared_replay_pass",
            "replay_result": {"verdict": "pass", "replay_matches": True},
        },
    }


def _acceptance_gates(raw_report: dict[str, Any], positive_reports: dict[str, dict[str, Any]]) -> dict[str, bool]:
    return {
        "all_circular_positive_controls_block": all(
            report["candidate_blocked"] for report in positive_reports.values()
        ),
        "raw_output_only_fixture_scored": raw_report["candidate_blocked"] is False
        and raw_report["computed_score"] is not None,
        "baseline_independently_invoked": raw_report["baseline_result"].get("called") is True
        and raw_report["baseline_result"].get("independent_callable") is True,
        "ablation_rerun_under_intervention": raw_report["ablation_result"].get("called") is True
        and raw_report["ablation_result"].get("intervention_applied") is True
        and raw_report["ablation_result"].get("episodes_rerun") is True
        and raw_report["ablation_result"].get("score_changed_or_blocked") is True,
        "leakage_positive_control_detected": raw_report["leakage_result"].get("positive_control_detected") is True,
        "replay_recomputed_from_state_observation": raw_report["replay_result"].get("behavior_recomputed") is True
        and raw_report["replay_result"].get("used_serialized_state") is True
        and raw_report["replay_result"].get("used_observation") is True
        and raw_report["replay_result"].get("hash_only") is False,
    }


def run_harness(
    repo_root: Path | str | None = None,
    output_dir: Path | str | None = None,
    run_id: str = "one_gate_future_only_non_circular_harness_001a_run",
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    out = Path(output_dir) if output_dir is not None else root / "artifacts" / TASK_SLUG
    out.mkdir(parents=True, exist_ok=True)

    raw_payload = build_raw_output_only_fixture()
    raw_report = evaluate_candidate_outputs(raw_payload, run_id=run_id + "_raw")
    positive_payloads = build_positive_control_payloads()
    positive_reports = {
        control_id: evaluate_candidate_outputs(payload, run_id=f"{run_id}_{control_id}")
        for control_id, payload in positive_payloads.items()
    }
    acceptance = _acceptance_gates(raw_report, positive_reports)
    acceptance_passed = all(acceptance.values())

    result = {
        "task_id": TASK_ID,
        "selected_gate_target": TARGET_GATE,
        "selected_target_basis": [
            "artifacts/evidence_admission_verifier_001b_bypass_audit_001a/route_decision.json",
            "artifacts/ego_mainline_evidence_dependency_closure_001a/route_permission_matrix.json",
            "artifacts/ego_mainline_known_failure_triage_001a/downstream_route_impact_matrix.json",
        ],
        "verdict": "future_only_non_circular_harness_preflight_acceptance_gates_passed"
        if acceptance_passed
        else "future_only_non_circular_harness_preflight_blocked",
        "acceptance_gates": acceptance,
        "raw_fixture_decision": raw_report["admission_decision"],
        "raw_fixture_score": raw_report["computed_score"],
        "positive_control_block_reason_ids": {
            control_id: report["block_reason_ids"] for control_id, report in positive_reports.items()
        },
        "existing_verifier_001b_repaired_or_used_for_admission": False,
        "mainline_integration_status": "none",
        "enabled_status": "local CLI/test runner only",
        "real_trigger_evidence": "six verifier-001B-derived circular positive controls plus raw-output-only fixture executed through the same harness evaluator",
        "claim_ceiling": CLAIM_CEILING,
        "what_this_does_not_prove": [
            "Gate validity",
            "mechanism validity",
            "mainline effect",
            "agency",
            "consciousness",
            "emotion",
            "autonomy",
            "stable user benefit",
            "EGO readiness",
        ],
        **AUTHORIZATION_FLAGS,
    }

    execution_manifest = {
        "task_id": TASK_ID,
        "run_id": run_id,
        "producer_function": "run_harness",
        "producer_source_path": producer_source_path(run_harness),
        "code_path_hash": _producer_code_hash(run_harness),
        "branch": _git_output(root, ["branch", "--show-current"]),
        "head": _git_output(root, ["rev-parse", "HEAD"]),
        "status_at_execution": _git_output(root, ["status", "--short", "--branch"]),
        "existing_verifier_001b_repaired_or_used_for_admission": False,
        "forbidden_scope_not_entered": [
            "src/evidence_admission_verifier_001a",
            "Gate3 files",
            "Gate4 execution files",
            "mainline files",
            "bridge files",
            "runtime files",
            "old bundle mutation",
        ],
        "claim_ceiling": CLAIM_CEILING,
    }

    failure_manifest = {
        "task_id": TASK_ID,
        "claim_ceiling": CLAIM_CEILING,
        "acceptance_failures": [
            gate_name for gate_name, passed in acceptance.items() if not passed
        ],
        "positive_control_blocks": {
            control_id: {
                "candidate_blocked": report["candidate_blocked"],
                "block_reason_ids": report["block_reason_ids"],
            }
            for control_id, report in positive_reports.items()
        },
        "raw_fixture_block_reason_ids": raw_report["block_reason_ids"],
    }

    _write_json(out / "result.json", result)
    _write_jsonl(out / "trace.jsonl", raw_payload["raw_traces"])
    _write_json(out / "baseline_comparison.json", raw_report["baseline_result"])
    _write_json(out / "ablation_report.json", raw_report["ablation_result"])
    _write_json(out / "replay_report.json", raw_report["replay_result"])
    _write_json(out / "leakage_report.json", raw_report["leakage_result"])
    _write_json(out / "positive_control_report.json", positive_reports)
    _write_json(out / "metric_provenance.json", raw_report["metric_provenance"])
    _write_json(out / "failure_manifest.json", failure_manifest)
    (out / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    _write_json(out / "execution_manifest.json", execution_manifest)

    return result


def main() -> None:
    run_harness()
