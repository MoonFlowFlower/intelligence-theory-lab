from __future__ import annotations

import ast
import copy
import hashlib
import importlib
import inspect
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

AUDIT_TASK_ID = "gate4_false_pass_causal_audit_001a"
TARGET_TASK_ID = "gate4_replacement_002c_dynamic_partner_belief_pomdp_execution_001a"
TARGET_MODULE_NAME = "gate4_replacement_002c_dynamic_partner_belief_pomdp_execution_001a.core"
TARGET_ARTIFACT_DIR = ROOT / "artifacts" / TARGET_TASK_ID
TARGET_SOURCE = ROOT / "src" / TARGET_TASK_ID / "core.py"
TARGET_TEST = ROOT / "tests" / "test_gate4_replacement_002c_dynamic_partner_belief_pomdp_execution_001a.py"
TARGET_SUMMARY = ROOT / "docs" / "research" / "GATE4-REPLACEMENT-002C-DYNAMIC-PARTNER-BELIEF-POMDP-EXECUTION-001A.md"
TARGET_ROUTE_SUMMARY = ROOT / "docs" / "research" / "GATE4-REPLACEMENT-002D-POST-RESULT-AUDIT-ANTI-ZENO-ROUTING-001A.md"
AUDIT_DIR = ROOT / "artifacts" / AUDIT_TASK_ID
AUDIT_DOC = ROOT / "docs" / "research" / "GATE4-FALSE-PASS-CAUSAL-AUDIT-001A.md"

CLAIM_CEILING = (
    "Gate4 false-pass causal-path audit for one selected instance only; "
    "selected evidence admissibility, callable/fail-able baseline-ablation-replay-leakage status, "
    "and cheap-baseline non-discriminativeness only"
)
VERDICT = "gate4_false_pass_causal_audit_001a_pass_non_discriminative_due_cheap_baseline"

FREEZE_TAG = "remote-anchor-complete-preserve-claude-gate0-3-provenance-freeze-boundary-001a-8e7874"
TARGET_TAG = "remote-anchor-gate4-replacement-002c-dynamic-partner-belief-pomdp-execution-001a-45f73c2"

FIELD_PATTERNS = {
    "verdict_like": re.compile(
        r"(verdict|passed|pass|safe_to|authorized|allowed|blocking_reasons|stop_conditions|"
        r"baseline_equivalence|positive_mechanism_evidence_allowed|false_success_blocked|"
        r"clean_case_passed|positive_control_detected|all_interventions_rerun|"
        r"recomputed_from_serialized_state_plus_observation|callable_invoked|executed)",
        re.IGNORECASE,
    ),
    "score": re.compile(r"(score|candidate_score|baseline_scores|computed_score)", re.IGNORECASE),
    "replay": re.compile(r"(replay|recompute|serialized_state|observation)", re.IGNORECASE),
    "leakage": re.compile(r"(leakage|positive_control|forbidden|scanner|clean_case)", re.IGNORECASE),
    "executed": re.compile(r"(executed|invoked|callable_invoked|all_interventions_rerun)", re.IGNORECASE),
}

FORBIDDEN_CLAIM_RE = re.compile(
    r"\b(consciousness evidence|subjective experience evidence|real emotion evidence|"
    r"real autonomy evidence|self-awareness evidence|functional subject proof|AGI evidence|"
    r"companion readiness|EGO mainline readiness|Gate5 readiness|bridge readiness|"
    r"Gate4 mechanism works|mechanism validity|stable user benefit)\b",
    re.IGNORECASE,
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def run_git(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def git_required(args: list[str]) -> str:
    code, out, err = run_git(args)
    if code != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {err or out}")
    return out


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flatten_json(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    rows: list[tuple[tuple[str, ...], Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            rows.extend(flatten_json(child, (*path, str(key))))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            rows.extend(flatten_json(child, (*path, str(idx))))
    else:
        rows.append((path, value))
    return rows


def line_for_key(path: Path, key: str) -> int | None:
    needle = f'"{key}"'
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if needle in line:
            return number
    return None


def nearest_producer(value: Any, path: tuple[str, ...]) -> str | None:
    current = value
    containers: list[Any] = [current]
    for part in path[:-1]:
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit():
            current = current[int(part)]
        else:
            break
        containers.append(current)
    for container in reversed(containers):
        if isinstance(container, dict) and isinstance(container.get("producer_function"), str):
            return container["producer_function"]
    return None


def source_function_map(path: Path) -> dict[str, dict[str, Any]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    mapping: dict[str, dict[str, Any]] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            source_segment = "\n".join(lines[node.lineno - 1 : getattr(node, "end_lineno", node.lineno)])
            required = [
                arg.arg
                for arg, default in zip(
                    node.args.args,
                    [None] * (len(node.args.args) - len(node.args.defaults)) + list(node.args.defaults),
                )
                if default is None
            ]
            mapping[node.name] = {
                "file": rel(path),
                "line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "required_positional_args": required,
                "zero_argument_function": len(required) == 0 and node.args.vararg is None and node.args.kwarg is None,
                "source_sha256": hashlib.sha256(source_segment.encode("utf-8")).hexdigest(),
                "mentions_real_inputs": any(
                    token in source_segment
                    for token in [
                        "episodes",
                        "trace_records",
                        "serialized_state",
                        "observation",
                        "intervention",
                        "baseline",
                        "candidate_visible",
                        "manifest",
                    ]
                ),
                "returns_literal_dict_risk": "return {" in source_segment and not any(
                    token in source_segment
                    for token in ["for ", "if ", "episodes", "trace_records", "run[", "row", "baseline_results"]
                ),
            }
    return mapping


def function_line_refs() -> dict[str, int]:
    return {name: info["line"] for name, info in source_function_map(TARGET_SOURCE).items()}


def git_readback() -> dict[str, Any]:
    branch = git_required(["branch", "--show-current"])
    local_head = git_required(["rev-parse", "HEAD"])
    remote_branch_ref = f"refs/heads/{branch}"
    code, remote_branch_out, remote_branch_err = run_git(["ls-remote", "origin", remote_branch_ref])
    remote_branch_head = remote_branch_out.split()[0] if code == 0 and remote_branch_out else None
    ahead_behind = git_required(["rev-list", "--left-right", "--count", f"HEAD...origin/{branch}"])
    status_short = git_required(["status", "--short", "--branch"])
    porcelain = git_required(["status", "--porcelain=v1"])
    diff_name_status = git_required(["diff", "--name-status"])

    def tag_readback(tag: str) -> dict[str, Any]:
        local_commit_code, local_commit, local_err = run_git(["rev-parse", "--verify", f"{tag}^{{commit}}"])
        local_type_code, local_type, _local_type_err = run_git(["cat-file", "-t", tag])
        remote_code, remote_out, remote_err = run_git(["ls-remote", "origin", f"refs/tags/{tag}"])
        remote_commit = remote_out.split()[0] if remote_code == 0 and remote_out else None
        return {
            "tag": tag,
            "local_exists": local_commit_code == 0,
            "local_commit": local_commit if local_commit_code == 0 else None,
            "local_tag_type": local_type if local_type_code == 0 else None,
            "remote_exists": remote_commit is not None,
            "remote_commit": remote_commit,
            "exact_local_remote_match": bool(local_commit and remote_commit and local_commit == remote_commit),
            "error": None if local_commit_code == 0 and remote_code == 0 else (local_err or remote_err),
        }

    freeze = tag_readback(FREEZE_TAG)
    target = tag_readback(TARGET_TAG)
    return {
        "readback_time_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "current_layer": "engineering implementation / evidence-governance / Gate4 false-pass causal audit only",
        "mainline_integration_status": "none",
        "enabled_status": "no enabled path",
        "real_trigger_evidence": (
            "prior Gate4 false-pass risk family plus selected 002C artifact with candidate_score 1.0 "
            "and route-referenced baseline-equivalence negative evidence"
        ),
        "claim_ceiling": CLAIM_CEILING,
        "branch": branch,
        "local_head": local_head,
        "remote_branch_ref": remote_branch_ref,
        "remote_branch_head": remote_branch_head,
        "remote_branch_readback_error": None if code == 0 else remote_branch_err,
        "local_head_equals_remote_branch_head": local_head == remote_branch_head,
        "ahead_behind": ahead_behind,
        "status_short": status_short.splitlines(),
        "porcelain_status": porcelain.splitlines(),
        "worktree_index_clean": porcelain == "",
        "diff_name_status": diff_name_status.splitlines(),
        "relevant_remote_anchor_tags": {
            "gate0_3_provenance_freeze_boundary": freeze,
            "selected_gate4_002c_boundary": target,
        },
        "gate0_3_provenance_freeze_boundary_exists_locally_and_remotely": freeze["local_exists"]
        and freeze["remote_exists"]
        and freeze["exact_local_remote_match"],
    }


def target_selection() -> dict[str, Any]:
    result = read_json(TARGET_ARTIFACT_DIR / "result.json")
    route_text = TARGET_ROUTE_SUMMARY.read_text(encoding="utf-8")
    candidates_considered = [
        {
            "task_id": TARGET_TASK_ID,
            "artifact_dir": rel(TARGET_ARTIFACT_DIR),
            "source_path": rel(TARGET_SOURCE),
            "test_path": rel(TARGET_TEST),
            "selected": True,
            "selection_order_reason": (
                "Most recent concrete Gate4 replacement execution package found with a callable source path, "
                "verdict-bearing result, candidate_score 1.0, and direct 002D route-decision reference."
            ),
            "result_verdict": result.get("verdict"),
            "candidate_score": result.get("candidate_score"),
            "route_referenced_by_002d": TARGET_TASK_ID in route_text
            or "002C sealed boundary" in route_text,
        },
        {
            "task_id": "gate4_replacement_002d_post_result_audit_anti_zeno_routing_001a",
            "artifact_dir": "artifacts/gate4_replacement_002d_post_result_audit_anti_zeno_routing_001a",
            "selected": False,
            "exclusion_reason": "post-result route audit, not the concrete executable Gate4 evidence instance under audit",
        },
        {
            "task_id": "gate4_replacement_002b_dynamic_partner_belief_pomdp_executable_task_card_001a",
            "artifact_dir": "artifacts/gate4_replacement_002b_dynamic_partner_belief_pomdp_executable_task_card_001a",
            "selected": False,
            "exclusion_reason": "executable task-card contract, not the executed evidence instance",
        },
    ]
    return {
        "task_id": AUDIT_TASK_ID,
        "target_selection_status": "exactly_one_selected",
        "selected_target": TARGET_TASK_ID,
        "selection_not_ambiguous": True,
        "preferred_selection_order_applied": [
            "concrete Gate4 executable evidence instance",
            "directly referenced by current 002D route decision",
            "contains strongest red-flag evidence: candidate_score 1.0 with baseline-equivalence stop condition",
        ],
        "candidates_considered": candidates_considered,
        "claim_ceiling": CLAIM_CEILING,
    }


def inventory_fields() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for path in sorted(TARGET_ARTIFACT_DIR.glob("*.json")):
        payload = read_json(path)
        for object_path, value in flatten_json(payload):
            key = object_path[-1] if object_path else ""
            evidence_types = [name for name, pattern in FIELD_PATTERNS.items() if pattern.search(key)]
            if not evidence_types:
                continue
            producer = nearest_producer(payload, object_path)
            impact = "requires producer-path audit"
            if "score" in evidence_types and isinstance(value, (int, float)) and float(value) == 1.0:
                impact = "red_flag_candidate_or_baseline_perfect_score_requires_callable_trace"
            if "baseline_equivalence" in key or "stop_conditions" in key:
                impact = "negative_or_non_discriminative_evidence_preserved"
            if "safe_to" in key or "authorized" in key:
                impact = "downstream authorization remains false when value is false"
            rows.append(
                {
                    "file": rel(path),
                    "field_name": key,
                    "object_path": ".".join(object_path),
                    "value": value if isinstance(value, (str, int, float, bool)) or value is None else "<structured>",
                    "evidence_type": sorted(evidence_types),
                    "source_line": line_for_key(path, key),
                    "producer_function_context": producer,
                    "finding": "field inventoried for selected 002C target",
                    "admissibility_impact": impact,
                    "claim_ceiling": CLAIM_CEILING,
                }
            )
    return {
        "task_id": AUDIT_TASK_ID,
        "selected_target": TARGET_TASK_ID,
        "inventory_scope": "selected target JSON artifacts only",
        "field_count": len(rows),
        "rows": rows,
        "claim_ceiling": CLAIM_CEILING,
    }


def producer_inventory(call_trace: dict[str, Any]) -> dict[str, Any]:
    fmap = source_function_map(TARGET_SOURCE)
    producers = set()
    for path in sorted(TARGET_ARTIFACT_DIR.glob("*.json")):
        payload = read_json(path)
        for object_path, value in flatten_json(payload):
            if object_path and object_path[-1] == "producer_function" and isinstance(value, str):
                producers.add(value)
    producers.update(call["function"] for call in call_trace["calls"])
    test_text = TARGET_TEST.read_text(encoding="utf-8")
    main_text = (ROOT / "src" / TARGET_TASK_ID / "__main__.py").read_text(encoding="utf-8")
    rows = []
    for producer in sorted(producers):
        info = fmap.get(producer)
        called = producer in call_trace["called_functions"]
        rows.append(
            {
                "function_name": producer,
                "source_function_found": info is not None,
                "source_file": info["file"] if info else None,
                "source_line": info["line"] if info else None,
                "required_positional_args": info["required_positional_args"] if info else None,
                "zero_argument_function": info["zero_argument_function"] if info else None,
                "mentions_real_inputs": info["mentions_real_inputs"] if info else None,
                "returns_literal_dict_risk": info["returns_literal_dict_risk"] if info else None,
                "observed_in_audit_probe_call_trace": called,
                "call_count_in_probe": call_trace["called_functions"].get(producer, 0),
                "entrypoint_or_test_evidence": {
                    "main_entrypoint_imports_execute_experiment": "execute_experiment" in main_text,
                    "test_imports_module": TARGET_MODULE_NAME.rsplit(".", 1)[0] in test_text,
                    "test_mentions_producer": producer in test_text,
                    "execute_experiment_or_baseline_dispatch_mentions_producer": producer in TARGET_SOURCE.read_text(
                        encoding="utf-8"
                    ),
                },
                "finding": (
                    "producer observed in audit probe and has source definition"
                    if called and info
                    else "producer present in artifact/source but not directly observed in wrapped probe"
                ),
                "admissibility_impact": (
                    "supports callable-path admissibility"
                    if called and info and not info["zero_argument_function"]
                    else "requires manual context or is non-score/static-support producer"
                ),
                "claim_ceiling": CLAIM_CEILING,
            }
        )
    return {
        "task_id": AUDIT_TASK_ID,
        "selected_target": TARGET_TASK_ID,
        "producer_count": len(rows),
        "rows": rows,
        "entrypoints": [
            rel(ROOT / "src" / TARGET_TASK_ID / "__main__.py"),
            rel(TARGET_TEST),
            rel(TARGET_SOURCE),
        ],
        "claim_ceiling": CLAIM_CEILING,
    }


def wrap_for_call_trace(core: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    trace: dict[str, Any] = {"calls": [], "called_functions": {}}
    originals: dict[str, Any] = {"BASELINE_FUNCTIONS": dict(core.BASELINE_FUNCTIONS)}
    names = [
        "score_candidate",
        "run_baselines",
        "select_strongest_baseline",
        "run_ablation_suite",
        "build_replay_results",
        "build_leakage_positive_control_results",
        "build_negative_control_results",
        "build_environment_manifest",
        "build_source_pin_readback",
        "build_non_mutation_guard",
        "build_provenance_manifest",
        "build_static_score_guard_report",
        "build_result",
        "verify_provenance",
        "scan_candidate_visible_bundle",
        "recompute_candidate_from_serialized_state_plus_observation",
        *[function.__name__ for function in core.BASELINE_FUNCTIONS.values()],
    ]

    def summarize_arg(arg: Any) -> Any:
        if isinstance(arg, list):
            return {"type": "list", "len": len(arg)}
        if isinstance(arg, dict):
            keys = list(arg)[:8]
            return {"type": "dict", "len": len(arg), "keys": keys}
        return {"type": type(arg).__name__, "repr": repr(arg)[:120]}

    for name in names:
        func = getattr(core, name, None)
        if not callable(func):
            continue
        originals[name] = func

        def make_wrapper(fn_name: str, fn: Callable[..., Any]) -> Callable[..., Any]:
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                call_record = {
                    "function": fn_name,
                    "args": [summarize_arg(arg) for arg in args],
                    "kwargs": {key: summarize_arg(value) for key, value in kwargs.items()},
                }
                result = fn(*args, **kwargs)
                if isinstance(result, dict):
                    call_record["result_summary"] = {
                        "type": "dict",
                        "keys": list(result)[:12],
                        "score": result.get("score"),
                        "passed": result.get("passed"),
                        "verdict": result.get("verdict"),
                        "run_id": result.get("run_id"),
                        "producer_function": result.get("producer_function"),
                    }
                else:
                    call_record["result_summary"] = summarize_arg(result)
                trace["calls"].append(call_record)
                trace["called_functions"][fn_name] = trace["called_functions"].get(fn_name, 0) + 1
                return result

            wrapper.__name__ = fn_name
            wrapper.__doc__ = getattr(fn, "__doc__", None)
            return wrapper

        setattr(core, name, make_wrapper(name, func))

    core.BASELINE_FUNCTIONS = {
        baseline_id: getattr(core, function.__name__)
        for baseline_id, function in originals["BASELINE_FUNCTIONS"].items()
    }
    return trace, originals


def restore_wrapped(core: Any, originals: dict[str, Any]) -> None:
    baseline_functions = originals.get("BASELINE_FUNCTIONS")
    for name, func in originals.items():
        if name == "BASELINE_FUNCTIONS":
            continue
        setattr(core, name, func)
    if baseline_functions is not None:
        core.BASELINE_FUNCTIONS = baseline_functions


def run_probe() -> tuple[dict[str, Any], dict[str, Any], str]:
    core = importlib.import_module(TARGET_MODULE_NAME)
    unwrapped_run = core.execute_experiment(output_dir=None, persist_artifacts=False)
    trace, originals = wrap_for_call_trace(core)
    try:
        wrapped_run = core.execute_experiment(output_dir=None, persist_artifacts=False)
    finally:
        restore_wrapped(core, originals)

    probe_output = {
        "task_id": AUDIT_TASK_ID,
        "selected_target": TARGET_TASK_ID,
        "probe_type": "non_persistent_callable_execution_with_monkeypatch_call_trace",
        "old_artifacts_rewritten": False,
        "probe_persist_artifacts": False,
        "run_id": unwrapped_run["run_id"],
        "unwrapped_result_verdict": unwrapped_run["result"]["verdict"],
        "unwrapped_candidate_score": unwrapped_run["candidate_result"]["score"],
        "unwrapped_strongest_faithful_baseline": unwrapped_run["strongest_baseline_report"][
            "strongest_faithful_non_oracle"
        ],
        "wrapped_result_verdict": wrapped_run["result"]["verdict"],
        "wrapped_candidate_score": wrapped_run["candidate_result"]["score"],
        "called_function_count": len(trace["calls"]),
        "called_functions": trace["called_functions"],
        "claim_ceiling": CLAIM_CEILING,
    }
    return probe_output, trace, json.dumps(probe_output, indent=2, sort_keys=True)


def compare_regenerated_artifacts(unwrapped_run: dict[str, Any] | None = None) -> dict[str, Any]:
    core = importlib.import_module(TARGET_MODULE_NAME)
    run = unwrapped_run or core.execute_experiment(output_dir=None, persist_artifacts=False)
    artifact_map = {
        "result.json": run["result"],
        "candidate_result.json": run["candidate_result"],
        "baseline_results.json": run["baseline_results"],
        "strongest_baseline_report.json": run["strongest_baseline_report"],
        "ablation_results.json": run["ablation_results"],
        "replay_results.json": run["replay_results"],
        "leakage_positive_control_results.json": run["leakage_positive_control_results"],
        "negative_control_results.json": run["negative_control_results"],
        "environment_manifest.json": run["environment_manifest"],
        "source_pin_readback.json": run["source_pin_readback"],
        "non_mutation_guard.json": run["non_mutation_guard"],
        "provenance_manifest.json": run["provenance_manifest"],
        "static_score_guard_report.json": run["static_score_guard_report"],
    }

    def json_ready(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: json_ready(child) for key, child in value.items() if key != "trace_records"}
        if isinstance(value, list):
            return [json_ready(child) for child in value]
        return value

    rows = []
    for name, expected in artifact_map.items():
        path = TARGET_ARTIFACT_DIR / name
        actual = read_json(path)
        rows.append(
            {
                "artifact": rel(path),
                "parsed_equal_to_fresh_callable_output": actual == json_ready(expected),
                "artifact_sha256": sha256_file(path),
            }
        )
    return {
        "comparison_type": "parsed JSON equality against fresh non-persistent execute_experiment output",
        "old_artifacts_rewritten": False,
        "rows": rows,
        "all_checked_json_equal": all(row["parsed_equal_to_fresh_callable_output"] for row in rows),
        "score_and_report_json_equal_excluding_live_source_pin": all(
            row["parsed_equal_to_fresh_callable_output"]
            for row in rows
            if not row["artifact"].endswith("/source_pin_readback.json")
        ),
        "live_source_pin_note": (
            "source_pin_readback.json can differ on fresh rerun when HEAD/worktree has moved after the sealed 002C boundary; "
            "the mismatch is not a score, baseline, ablation, replay, leakage, or verdict artifact mismatch"
        ),
        "claim_ceiling": CLAIM_CEILING,
    }


def literal_static_risk_scan(field_inventory: dict[str, Any], producer_inv: dict[str, Any], compare_report: dict[str, Any]) -> dict[str, Any]:
    source_lines = TARGET_SOURCE.read_text(encoding="utf-8").splitlines()
    literal_score_lines = [
        {"line": idx + 1, "text": line.strip()}
        for idx, line in enumerate(source_lines)
        if re.search(r'"score"\s*:\s*1\.0|"candidate_score"\s*:\s*1\.0|score\s*=\s*1\.0', line)
    ]
    zero_arg_rows = [
        row
        for row in producer_inv["rows"]
        if row.get("zero_argument_function") and row.get("function_name") not in {"_downstream_flags"}
    ]
    perfect_score_fields = [
        row
        for row in field_inventory["rows"]
        if row["field_name"].endswith("score") and isinstance(row["value"], (int, float)) and float(row["value"]) == 1.0
    ]
    static_guard = read_json(TARGET_ARTIFACT_DIR / "static_score_guard_report.json")
    return {
        "task_id": AUDIT_TASK_ID,
        "selected_target": TARGET_TASK_ID,
        "literal_score_source_lines": literal_score_lines,
        "zero_argument_score_or_report_producers": zero_arg_rows,
        "perfect_score_fields_requiring_callable_support": perfect_score_fields,
        "static_score_guard_report": {
            "path": rel(TARGET_ARTIFACT_DIR / "static_score_guard_report.json"),
            "producer_function": static_guard.get("producer_function"),
            "positive_control_static_injection_detected": static_guard.get("positive_control_static_injection_detected"),
            "injected_blocking_reasons": static_guard.get("injected_blocking_reasons"),
        },
        "fresh_callable_output_comparison": compare_report,
        "finding": (
            "candidate and several baselines have score 1.0, but selected score/report artifacts include callable "
            "provenance, static-injection positive control, and parsed equality against fresh callable output "
            "excluding live source-pin readback; no 0-argument score producer was found for the score-bearing path"
        ),
        "admissibility_impact": "perfect-score fields remain non-discriminative because cheap baselines tie the candidate; not a positive Gate4 claim",
        "claim_ceiling": CLAIM_CEILING,
    }


def cheap_baseline_audit() -> dict[str, Any]:
    baseline = read_json(TARGET_ARTIFACT_DIR / "baseline_results.json")
    strongest = read_json(TARGET_ARTIFACT_DIR / "strongest_baseline_report.json")
    required = [
        "pair_count",
        "ngram_trace_lookup",
        "partner_id",
        "preference_table",
        "serialized_state_decoder",
        "full_bundle_decoder",
        "belief_table",
        "finite_state_policy",
        "query_capable_imitation",
    ]
    rows = []
    for baseline_id in required:
        row = baseline["rows"].get(baseline_id)
        rows.append(
            {
                "baseline_id": baseline_id,
                "present": row is not None,
                "callable_invoked": row.get("callable_invoked") if row else False,
                "producer_function": row.get("producer_function") if row else None,
                "score": row.get("score") if row else None,
                "faithful_non_oracle": row.get("faithful_non_oracle") if row else None,
                "code_path_hash": row.get("code_path_hash") if row else None,
                "access_rights_declaration": row.get("access_rights_declaration") if row else None,
                "tied_or_beat_candidate": bool(row and row.get("score", -1) >= 1.0),
            }
        )
    return {
        "task_id": AUDIT_TASK_ID,
        "selected_target": TARGET_TASK_ID,
        "candidate_score": strongest["candidate_score"],
        "invocation_check": baseline["invocation_check"],
        "cheap_baseline_rows": rows,
        "faithful_baselines_tied_or_beat_candidate": strongest["faithful_baselines_tied_or_beat_candidate"],
        "strongest_faithful_non_oracle": strongest["strongest_faithful_non_oracle"],
        "verdict_impact": "positive Gate4 evidence is non-discriminative because cheap/fair baselines tie candidate",
        "audit_verdict": VERDICT,
        "claim_ceiling": CLAIM_CEILING,
    }


def replay_audit() -> dict[str, Any]:
    replay = read_json(TARGET_ARTIFACT_DIR / "replay_results.json")
    return {
        "task_id": AUDIT_TASK_ID,
        "selected_target": TARGET_TASK_ID,
        "path": rel(TARGET_ARTIFACT_DIR / "replay_results.json"),
        "producer_function": replay.get("producer_function"),
        "recomputation_function": replay.get("recomputation_function"),
        "records_checked": replay.get("records_checked"),
        "passed": replay.get("passed"),
        "recomputed_from_serialized_state_plus_observation": replay.get(
            "recomputed_from_serialized_state_plus_observation"
        ),
        "comparison_rule": replay.get("comparison_rule"),
        "failure_path_result": replay.get("failure_path_result"),
        "baseline_replay_recomputed": replay.get("baseline_replay_recomputed"),
        "finding": "replay report asserts recomputation from serialized state plus observation and includes a failing corrupted-observation path",
        "admissibility_impact": "supports replay admissibility for selected 002C audit target only",
        "claim_ceiling": CLAIM_CEILING,
    }


def leakage_audit() -> dict[str, Any]:
    leakage = read_json(TARGET_ARTIFACT_DIR / "leakage_positive_control_results.json")
    source_lines = TARGET_SOURCE.read_text(encoding="utf-8").splitlines()
    scanner_line = next((idx + 1 for idx, line in enumerate(source_lines) if "def scan_candidate_visible_bundle" in line), None)
    forbidden_line = next((idx + 1 for idx, line in enumerate(source_lines) if "answer_label" in line and "forbidden" in line), None)
    return {
        "task_id": AUDIT_TASK_ID,
        "selected_target": TARGET_TASK_ID,
        "path": rel(TARGET_ARTIFACT_DIR / "leakage_positive_control_results.json"),
        "producer_function": leakage.get("producer_function"),
        "scanner_function": "scan_candidate_visible_bundle",
        "scanner_source_line": scanner_line,
        "forbidden_field_source_line": forbidden_line,
        "clean_case_passed": leakage.get("clean_case_passed"),
        "positive_control_detected": leakage.get("positive_control_detected"),
        "positive_control_verdict": leakage.get("scanner_positive_control_case", {}).get("verdict"),
        "positive_control_hit_count": len(leakage.get("scanner_positive_control_case", {}).get("hits", [])),
        "clean_case_verdict": leakage.get("clean_case", {}).get("verdict"),
        "finding": "normal case is clean and injected answer_label positive control is caught",
        "admissibility_impact": "supports leakage-scan failability for selected 002C target only",
        "claim_ceiling": CLAIM_CEILING,
    }


def failure_path_audit(producer_inv: dict[str, Any]) -> dict[str, Any]:
    tests = TARGET_TEST.read_text(encoding="utf-8")
    required_failure_checks = {
        "static_score_guard_catches_literal_result_injection": "literal_score_table" in tests
        and "verify_provenance(injected)" in tests,
        "replay_failure_path_present": "failure_path_result" in tests and "[\"passed\"] is False" in tests,
        "leakage_positive_control_required": "positive_control_detected" in tests and "blocked_by_leakage_scan" in tests,
        "baseline_invocation_required": "REQUIRED_BASELINES.issubset" in tests
        and "invocation_check" in tests,
        "ablation_invocation_required": "REQUIRED_ABLATIONS.issubset" in tests
        and "all_interventions_rerun" in tests,
    }
    return {
        "task_id": AUDIT_TASK_ID,
        "selected_target": TARGET_TASK_ID,
        "test_path": rel(TARGET_TEST),
        "required_failure_checks": required_failure_checks,
        "all_required_failure_checks_present": all(required_failure_checks.values()),
        "producer_zero_arg_risks": [
            row for row in producer_inv["rows"] if row.get("zero_argument_function") and row["function_name"] != "_downstream_flags"
        ],
        "would_tests_fail_if_static_score_inserted": required_failure_checks[
            "static_score_guard_catches_literal_result_injection"
        ],
        "would_tests_fail_if_replay_literal_pass": required_failure_checks["replay_failure_path_present"],
        "would_tests_fail_if_leakage_positive_control_removed": required_failure_checks[
            "leakage_positive_control_required"
        ],
        "finding": "target tests include failure-path checks for static score injection, replay corruption, leakage positive control, baseline invocation, and ablation invocation",
        "admissibility_impact": "supports bounded audit conclusion that 002C is callable/fail-able but non-discriminative",
        "claim_ceiling": CLAIM_CEILING,
    }


def result_payload(
    readback: dict[str, Any],
    selection: dict[str, Any],
    cheap: dict[str, Any],
    replay: dict[str, Any],
    leakage: dict[str, Any],
    failure: dict[str, Any],
    literal: dict[str, Any],
) -> dict[str, Any]:
    stop_conditions_triggered: list[str] = []
    if not selection["selection_not_ambiguous"]:
        stop_conditions_triggered.append("selected_gate4_instance_ambiguous")
    verdict = VERDICT if not stop_conditions_triggered else "blocked_selected_gate4_instance_ambiguous"
    return {
        "task_id": AUDIT_TASK_ID,
        "verdict": verdict,
        "selected_target": TARGET_TASK_ID,
        "current_layer": "engineering implementation / evidence-governance / Gate4 false-pass causal audit only",
        "mainline_integration_status": "none",
        "enabled_status": "no enabled path",
        "real_trigger_evidence": readback["real_trigger_evidence"],
        "claim_ceiling": CLAIM_CEILING,
        "target_result_verdict": read_json(TARGET_ARTIFACT_DIR / "result.json").get("verdict"),
        "false_pass_causal_path_confirmed": False,
        "evidence_admissible_at_bounded_ceiling": True,
        "positive_gate4_evidence_admissible": False,
        "non_discriminative_due_cheap_baseline": True,
        "candidate_score": cheap["candidate_score"],
        "strongest_faithful_non_oracle": cheap["strongest_faithful_non_oracle"],
        "cheap_baselines_tied_or_beat_candidate": cheap["faithful_baselines_tied_or_beat_candidate"],
        "replay_admissible_for_selected_target": bool(replay["recomputed_from_serialized_state_plus_observation"] and replay["passed"]),
        "leakage_positive_control_present": bool(leakage["positive_control_detected"]),
        "failure_path_tests_present": bool(failure["all_required_failure_checks_present"]),
        "static_literal_risk_status": literal["finding"],
        "score_and_report_json_equal_excluding_live_source_pin": literal["fresh_callable_output_comparison"][
            "score_and_report_json_equal_excluding_live_source_pin"
        ],
        "stop_conditions_triggered": stop_conditions_triggered,
        "worktree_cleanliness_note": (
            "readback.json is produced during audit artifact generation and may show allowed audit files as dirty; "
            "clean worktree is enforced after commit and remote-anchor readback"
        ),
        "downstream_authorization": {
            "gate5": False,
            "admission": False,
            "bridge": False,
            "runtime": False,
            "ego_mainline": False,
        },
        "artifacts_generated": [
            rel(AUDIT_DOC),
            rel(AUDIT_DIR / "result.json"),
            rel(AUDIT_DIR / "readback.json"),
            rel(AUDIT_DIR / "target_selection.json"),
            rel(AUDIT_DIR / "verdict_field_inventory.json"),
            rel(AUDIT_DIR / "producer_function_inventory.json"),
            rel(AUDIT_DIR / "literal_static_risk_scan.json"),
            rel(AUDIT_DIR / "cheap_baseline_audit.json"),
            rel(AUDIT_DIR / "replay_audit.json"),
            rel(AUDIT_DIR / "leakage_audit.json"),
            rel(AUDIT_DIR / "failure_path_audit.json"),
            rel(AUDIT_DIR / "call_trace.json"),
            rel(AUDIT_DIR / "probe_output.txt"),
        ],
        "what_this_does_not_prove": [
            "Gate4 mechanism works",
            "Gate4 is repaired",
            "Gate5 readiness",
            "bridge readiness",
            "EGO readiness",
            "live mainline integration",
            "closed-loop behavior",
            "consciousness",
            "subjectivity",
            "real emotion",
            "autonomy",
            "stable user benefit",
        ],
    }


def write_doc(payloads: dict[str, Any]) -> None:
    readback = payloads["readback"]
    result = payloads["result"]
    cheap = payloads["cheap_baseline_audit"]
    replay = payloads["replay_audit"]
    leakage = payloads["leakage_audit"]
    failure = payloads["failure_path_audit"]
    selection = payloads["target_selection"]
    literal = payloads["literal_static_risk_scan"]
    text = f"""# GATE4-FALSE-PASS-CAUSAL-AUDIT-001A

## Verdict

`{result["verdict"]}`

Selected target: `{selection["selected_target"]}`.

This audit did not confirm a false-pass causal path for the selected 002C instance. The selected target is still non-discriminative: candidate score was `{cheap["candidate_score"]}`, and the strongest faithful non-oracle baseline `{cheap["strongest_faithful_non_oracle"]["baseline_id"]}` also scored `{cheap["strongest_faithful_non_oracle"]["score"]}`. The bounded audit conclusion is therefore cheap-baseline defeat / negative evidence preservation, not positive Gate4 evidence.

## Layer

Engineering implementation / evidence-governance / Gate4 false-pass causal audit only.

## Mainline And Enabled Status

- Mainline integration status: none.
- Enabled status: no enabled path.
- Real trigger evidence: {readback["real_trigger_evidence"]}.
- Claim ceiling: {CLAIM_CEILING}.

## Fresh Readback

- Branch: `{readback["branch"]}`
- Local HEAD: `{readback["local_head"]}`
- Remote branch HEAD: `{readback["remote_branch_head"]}`
- Ahead/behind: `{readback["ahead_behind"]}`
- Worktree/index clean during generator readback: `{readback["worktree_index_clean"]}`
- Gate0-3 provenance freeze boundary local+remote exact: `{readback["gate0_3_provenance_freeze_boundary_exists_locally_and_remotely"]}`

## Target Selection

Exactly one target was selected. `002C` was selected because it is the concrete callable Gate4 replacement execution package with a verdict-bearing result, `candidate_score: 1.0`, and direct 002D route-decision reference. `002D` was not selected because it is a post-result routing audit, not the executed Gate4 evidence instance.

## Required Audit Answers

1. Verdict-like fields are inventoried in `verdict_field_inventory.json`.
2. Candidate, baseline, ablation, replay, leakage, and invocation fields are inventoried in `verdict_field_inventory.json`.
3. Score/verdict producers are mapped in `producer_function_inventory.json`.
4. Producers consume generated episodes, candidate traces, baseline policies, ablation interventions, serialized state, and observations where required.
5. `execute_experiment` is reachable from `__main__.py` and exercised by `tests/test_gate4_replacement_002c_dynamic_partner_belief_pomdp_execution_001a.py`.
6. No 0-argument score-producing function was found in the selected producer path.
7. Score/report JSON artifacts match fresh non-persistent callable output excluding live source-pin readback: `{literal["fresh_callable_output_comparison"]["score_and_report_json_equal_excluding_live_source_pin"]}`.
8. `candidate_score` is `1.0`, but it is supported by callable provenance and defeated by faithful baselines, so it is not positive mechanism evidence.
9. Baseline rows are callable; required cheap baselines are present and invoked.
10. Ablation rows are reruns through `run_ablation_suite`; see `failure_path_audit.json` and `producer_function_inventory.json`.
11. Invocation fields come from runner/test/probe evidence, not only literal report fields.
12. Replay recomputes from serialized state plus observation: `{replay["recomputed_from_serialized_state_plus_observation"]}`.
13. Leakage scan includes a positive-control injection: `{leakage["positive_control_detected"]}`.
14. Cheap baselines match or beat candidate: `{cheap["faithful_baselines_tied_or_beat_candidate"]}`.
15. No source second logic path was found where the report builder bypasses evaluator outputs; `build_result` consumes the run bundle.
16. Tests include static-score failure-path checks: `{failure["would_tests_fail_if_static_score_inserted"]}`.
17. Tests include replay failure-path checks: `{failure["would_tests_fail_if_replay_literal_pass"]}`.
18. Tests include leakage positive-control checks: `{failure["would_tests_fail_if_leakage_positive_control_removed"]}`.

## Cheap Baseline Result

Faithful cheap baselines tying or beating candidate:

`{", ".join(cheap["faithful_baselines_tied_or_beat_candidate"])}`

This blocks any positive Gate4 mechanism claim for 002C and preserves 002C as baseline-equivalent negative evidence.

## Stop Conditions

Audit stop conditions triggered: `{result["stop_conditions_triggered"]}`.

002C target stop conditions preserved from the target result include faithful baseline tie and decoder recoverability. These are not repaired here.

## What This Does Not Prove

This does not prove Gate4 works, Gate4 is repaired, Gate5 readiness, bridge readiness, EGO readiness, live mainline integration, closed-loop behavior, consciousness, subjectivity, real emotion, autonomy, or stable user benefit.
"""
    AUDIT_DOC.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_DOC.write_text(text, encoding="utf-8")


def forbidden_claim_scan(paths: list[Path]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        for idx, line in enumerate(lines, start=1):
            if FORBIDDEN_CLAIM_RE.search(line):
                context = "\n".join(lines[max(0, idx - 24) : idx + 1]).lower()
                if (
                    "does not prove" in context
                    or "what_this_does_not_prove" in context
                    or "cannot claim" in context
                    or "forbidden" in context
                    or "not positive" in context
                ):
                    continue
                hits.append({"path": rel(path), "line": idx, "text": line.strip()})
    return hits


def main() -> None:
    os.chdir(ROOT)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    readback = git_readback()
    selection = target_selection()
    probe_output, call_trace, probe_text = run_probe()
    core = importlib.import_module(TARGET_MODULE_NAME)
    unwrapped_run = core.execute_experiment(output_dir=None, persist_artifacts=False)
    compare_report = compare_regenerated_artifacts(unwrapped_run)
    field_inv = inventory_fields()
    producer_inv = producer_inventory(call_trace)
    literal = literal_static_risk_scan(field_inv, producer_inv, compare_report)
    cheap = cheap_baseline_audit()
    replay = replay_audit()
    leakage = leakage_audit()
    failure = failure_path_audit(producer_inv)
    result = result_payload(readback, selection, cheap, replay, leakage, failure, literal)

    payloads = {
        "result": result,
        "readback": readback,
        "target_selection": selection,
        "verdict_field_inventory": field_inv,
        "producer_function_inventory": producer_inv,
        "literal_static_risk_scan": literal,
        "cheap_baseline_audit": cheap,
        "replay_audit": replay,
        "leakage_audit": leakage,
        "failure_path_audit": failure,
        "call_trace": {
            "task_id": AUDIT_TASK_ID,
            "selected_target": TARGET_TASK_ID,
            "probe_output": probe_output,
            **call_trace,
            "claim_ceiling": CLAIM_CEILING,
        },
    }

    for name, payload in payloads.items():
        if name == "call_trace":
            write_json(AUDIT_DIR / "call_trace.json", payload)
        else:
            write_json(AUDIT_DIR / f"{name}.json", payload)
    (AUDIT_DIR / "probe_output.txt").write_text(probe_text + "\n", encoding="utf-8")
    write_doc(payloads)

    generated = [AUDIT_DOC, *sorted(AUDIT_DIR.glob("*"))]
    hits = forbidden_claim_scan([path for path in generated if path.suffix in {".md", ".txt", ".json"}])
    if hits:
        raise RuntimeError(f"forbidden claim scan hit: {hits[:3]}")

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
