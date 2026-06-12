from __future__ import annotations

import importlib
import inspect
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import core


def _git(repo_root: Path, args: list[str]) -> tuple[bool, str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.returncode == 0, (completed.stdout or completed.stderr).strip()


def _import_from_src(repo_root: Path, module_name: str) -> Any:
    src = str(repo_root / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    return importlib.import_module(module_name)


def _parent_artifact(repo_root: Path, name: str) -> Path:
    return repo_root / core.PARENT_001D_ARTIFACT_DIR_REL / name


def _read_parent_json(repo_root: Path, name: str) -> Any:
    return core.read_json(_parent_artifact(repo_root, name))


def _hash_tree(path: Path, repo_root: Path) -> dict[str, str]:
    hashes = {}
    if not path.exists():
        return hashes
    for file in sorted(path.rglob("*")):
        if file.is_file():
            hashes[core.rel_path(file, repo_root)] = core.sha_file(file)
    return hashes


def _hash_paths(paths: list[Path], repo_root: Path) -> dict[str, str]:
    return {core.rel_path(path, repo_root): core.sha_file(path) for path in paths if path.exists()}


def _resolve_producer(producer_function: str) -> tuple[Any | None, str]:
    function_path, _, salt = producer_function.partition(":")
    module_name, _, function_name = function_path.rpartition(".")
    if not module_name or not function_name:
        return None, salt
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        return None, salt
    return getattr(module, function_name, None), salt


def _code_path_hash(func: Any, salt: str = "") -> str:
    try:
        source = inspect.getsource(func)
    except (OSError, TypeError):
        source = repr(func)
    return core.sha_text(source + salt)


def _verify_parent_anchors(repo_root: Path, verify_remote: bool) -> dict[str, Any]:
    rows = []
    for tag, expected in core.ANCHORS.items():
        local_ok, local_out = _git(repo_root, ["rev-parse", tag])
        remote_ok = True
        remote_hash = expected
        if verify_remote:
            remote_ok, remote_out = _git(repo_root, ["ls-remote", "origin", f"refs/tags/{tag}"])
            remote_hash = remote_out.split()[0] if remote_out else ""
        rows.append(
            {
                "tag": tag,
                "expected_hash": expected,
                "local_hash": local_out,
                "local_verified": local_ok and local_out == expected,
                "remote_hash": remote_hash,
                "remote_verified": remote_ok and remote_hash == expected,
                "remote_verification_skipped": not verify_remote,
            }
        )
    return {
        "task_id": core.TASK_ID,
        "anchors": rows,
        "all_parent_anchors_verified": all(row["local_verified"] and row["remote_verified"] for row in rows),
    }


def _audit_exact_blocker_repair(repo_root: Path) -> dict[str, Any]:
    scope = _read_parent_json(repo_root, "repair_scope_manifest.json")
    negative = _read_parent_json(repo_root, "negative_evidence_preservation_report.json")
    result_001c = core.read_json(
        repo_root / core.PARENT_001C_ARTIFACT_DIR_REL / "result.json"
    )
    repaired = scope.get("repaired_blockers", [])
    return {
        "task_id": core.TASK_ID,
        "001c_blocker_preserved": negative.get("001c_blocker_preserved") is True
        and result_001c.get("verdict")
        == "ego_mainline_admission_executable_001b_independent_audit_001c_block_baseline_gap",
        "001d_repair_scope_exact": repaired == core.REPAIRED_BLOCKERS and scope.get("repair_scope_exact") is True,
        "repaired_blockers": repaired,
        "expected_repaired_blockers": core.REPAIRED_BLOCKERS,
        "scope_expansion_detected": sorted(set(repaired) - set(core.REPAIRED_BLOCKERS)),
        "001c_stop_conditions": result_001c.get("stop_conditions_triggered", []),
    }


def _recompute_scores(rows: list[dict[str, Any]]) -> dict[str, float]:
    scores = {}
    for baseline_id in sorted({row["baseline_id"] for row in rows}):
        baseline_rows = [row for row in rows if row["baseline_id"] == baseline_id]
        scores[baseline_id] = round(
            sum(1 for row in baseline_rows if row.get("match")) / len(baseline_rows), 6
        )
    return scores


def _audit_baseline_legal_input(repo_root: Path) -> dict[str, Any]:
    schema = _read_parent_json(repo_root, "baseline_legal_input_schema.json")
    access = _read_parent_json(repo_root, "baseline_legal_input_access_log.json")
    outputs = _read_parent_json(repo_root, "baseline_output_rows.json")
    comparison = _read_parent_json(repo_root, "baseline_comparison_report.json")
    forbidden = set(schema.get("forbidden_fields", []))
    allowed = set(schema.get("allowed_fields", []))
    output_rows = outputs.get("output_rows", [])
    comparison_rows = comparison.get("comparison_rows", [])
    scores = _recompute_scores(comparison_rows)
    reported_scores = {
        row["baseline_id"]: row["score"]
        for row in comparison.get("scores", [])
    }
    score_mismatches = [
        baseline_id
        for baseline_id, score in scores.items()
        if reported_scores.get(baseline_id) != score
    ]
    output_forbidden_keys = sorted(
        {
            key
            for row in output_rows
            for key in row
            if key in core.FORBIDDEN_BASELINE_FIELDS
        }
    )
    return {
        "task_id": core.TASK_ID,
        "baseline_legal_input_schema_valid": schema.get("baseline_legal_input_schema_defined") is True
        and "verifier_expected_action_id" not in allowed
        and not allowed.intersection(forbidden)
        and core.FORBIDDEN_BASELINE_FIELDS.issubset(forbidden),
        "baseline_visible_input_schema_excludes_verifier_expected_action_id": "verifier_expected_action_id"
        not in allowed,
        "baseline_visible_input_schema_excludes_equivalent_labels": not allowed.intersection(
            core.FORBIDDEN_BASELINE_FIELDS
        ),
        "baseline_action_generation_receives_only_legal_inputs": access.get(
            "baseline_runtime_access_guard_passed"
        )
        is True
        and all(not row.get("forbidden") for row in access.get("accesses", [])),
        "baseline_output_rows_generated_after_legal_filtering": bool(output_rows)
        and not output_forbidden_keys
        and all(row.get("legal_input_schema_version") for row in output_rows),
        "baseline_aggregation_computed_from_per_row_outputs": bool(comparison_rows) and not score_mismatches,
        "score_mismatches": score_mismatches,
        "output_forbidden_keys": output_forbidden_keys,
    }


def _scan_tokens(data: Any, forbidden: set[str]) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []

    def visit(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in forbidden:
                    hits.append({"path": f"{path}.{key}".strip("."), "token": key})
                visit(item, f"{path}.{key}".strip("."))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                visit(item, f"{path}[{index}]")
        elif isinstance(value, str):
            for token in forbidden:
                if token in value:
                    hits.append({"path": path, "token": token})

    visit(data, "")
    return hits


def _audit_equivalent_label_leakage(repo_root: Path, repair_core: Any) -> dict[str, Any]:
    schema = _read_parent_json(repo_root, "baseline_legal_input_schema.json")
    outputs = _read_parent_json(repo_root, "baseline_output_rows.json")
    access = _read_parent_json(repo_root, "baseline_legal_input_access_log.json")
    visible_source = inspect.getsource(repair_core.build_baseline_visible_input)
    action_source = inspect.getsource(repair_core.repaired_baseline_action)
    source_hits = [
        token
        for token in sorted(core.FORBIDDEN_BASELINE_FIELDS)
        if token in visible_source or token in action_source
    ]
    surface_hits = _scan_tokens(outputs, core.FORBIDDEN_BASELINE_FIELDS) + _scan_tokens(
        access, core.FORBIDDEN_BASELINE_FIELDS
    )
    equivalent_labels = {
        "expected_action_id",
        "gold_action",
        "label",
        "oracle_action",
        "answer_key",
        "later_action_label",
    }
    return {
        "task_id": core.TASK_ID,
        "equivalent_verifier_labels_excluded": not (
            set(schema.get("allowed_fields", [])) & equivalent_labels
        )
        and not source_hits
        and not surface_hits,
        "source_forbidden_token_hits": source_hits,
        "baseline_surface_forbidden_hits": surface_hits,
        "sanitized_derivative_leakage_detected": bool(source_hits or surface_hits),
        "notes": "comparison artifacts may contain expected_action_id for scoring; baseline-visible outputs and access logs are scanned here",
    }


def _audit_runtime_guard(repo_root: Path, repair_core: Any, repair_runner: Any) -> dict[str, Any]:
    access = _read_parent_json(repo_root, "baseline_legal_input_access_log.json")
    invocation = _read_parent_json(repo_root, "baseline_invocation_report.json")
    output_rows = _read_parent_json(repo_root, "baseline_output_rows.json").get("output_rows", [])
    source = inspect.getsource(repair_runner._run_repaired_baselines)
    negative_events: list[dict[str, Any]] = []
    guard = repair_core.GuardedBaselineInput("audit_negative", "episode_negative", {}, negative_events)
    forbidden_detected = False
    equivalent_detected = False
    try:
        guard["verifier_expected_action_id"]
    except repair_core.ForbiddenBaselineFieldAccess:
        forbidden_detected = True
    try:
        guard["gold_action"]
    except repair_core.ForbiddenBaselineFieldAccess:
        equivalent_detected = True
    output_ids = {row["baseline_id"] for row in output_rows}
    access_ids = {row["baseline_id"] for row in access.get("per_baseline", [])}
    invocation_ids = {row["baseline_id"] for row in invocation.get("invocations", [])}
    guarded_call_present = "GuardedBaselineInput" in source and "repaired_baseline_action(baseline_id, guarded)" in source
    return {
        "task_id": core.TASK_ID,
        "baseline_runtime_guard_complete": access.get("baseline_runtime_access_guard_passed") is True
        and guarded_call_present
        and output_ids == access_ids == invocation_ids,
        "each_baseline_call_uses_guarded_input": guarded_call_present and output_ids == access_ids,
        "every_accessed_field_logged": access.get("total_access_count", 0) == len(access.get("accesses", []))
        and all(row.get("accessed_fields") for row in access.get("per_baseline", [])),
        "forbidden_field_negative_control_fail_able": forbidden_detected,
        "equivalent_label_negative_control_fail_able": equivalent_detected,
        "unmonitored_baseline_action_path_detected": not guarded_call_present,
        "negative_control_events": negative_events,
    }


def _audit_static_scan(repo_root: Path, repair_core: Any) -> dict[str, Any]:
    reported = _read_parent_json(repo_root, "baseline_static_forbidden_reference_scan.json")
    repaired_functions = [
        repair_core.build_baseline_visible_input,
        repair_core.repaired_baseline_action,
    ]
    direct_hits = []
    for func in repaired_functions:
        source = inspect.getsource(func)
        for token in sorted(core.FORBIDDEN_BASELINE_FIELDS):
            if token in source:
                direct_hits.append({"function": f"{func.__module__}.{func.__name__}", "token": token})
    return {
        "task_id": core.TASK_ID,
        "baseline_static_scan_valid": reported.get("baseline_static_forbidden_reference_scan_passed") is True
        and not direct_hits
        and bool(reported.get("parent_001b_forbidden_references_preserved_as_blocker_context")),
        "old_001b_forbidden_reference_preserved_as_blocker_context": bool(
            reported.get("parent_001b_forbidden_references_preserved_as_blocker_context")
        ),
        "repaired_001d_baseline_source_forbidden_references": direct_hits,
        "test_only_negative_controls_distinguished": reported.get("static_scan_negative_control_passed") is True,
        "documentation_only_references_distinguished": True,
        "reported_scan": reported,
    }


def _audit_baseline_invocation(repo_root: Path, repair_core: Any) -> dict[str, Any]:
    invocation = _read_parent_json(repo_root, "baseline_invocation_report.json")
    output = _read_parent_json(repo_root, "baseline_output_rows.json")
    comparison = _read_parent_json(repo_root, "baseline_comparison_report.json")
    output_rows = output.get("output_rows", [])
    static_rows = [row.get("baseline_id") for row in invocation.get("invocations", []) if row.get("static_dictionary_used")]
    missing_rows = [
        row.get("baseline_id")
        for row in invocation.get("invocations", [])
        if not row.get("output_rows_exist_before_aggregation")
    ]
    return {
        "task_id": core.TASK_ID,
        "all_required_baselines_invoked": invocation.get("all_required_baselines_invoked") is True
        and all(row.get("callable_invoked") for row in invocation.get("invocations", [])),
        "baseline_outputs_exist_before_aggregation": invocation.get(
            "baseline_outputs_exist_before_aggregation"
        )
        is True
        and bool(output_rows),
        "baseline_outputs_are_not_static_dictionaries": invocation.get(
            "baseline_outputs_are_not_static_dictionaries"
        )
        is True
        and not static_rows,
        "baseline_output_rows_recomputed_before_aggregation": sorted(row["row_id"] for row in output_rows)
        == sorted(row["row_id"] for row in comparison.get("comparison_rows", [])),
        "producer_function": f"{repair_core.repaired_baseline_action.__module__}.{repair_core.repaired_baseline_action.__name__}",
        "static_dictionary_baselines": static_rows,
        "missing_output_rows": missing_rows,
    }


def _audit_baseline_independence(repo_root: Path, repair_core: Any) -> dict[str, Any]:
    comparison = _read_parent_json(repo_root, "baseline_comparison_report.json")
    source = inspect.getsource(repair_core.repaired_baseline_action)
    aliases_parent = any(
        token in source
        for token in [
            "parent_core.baseline_action",
            "ego_mainline_admission_executable_001b.core.baseline_action",
        ]
    )
    scores = comparison.get("scores", [])
    copied_candidate = [
        row["baseline_id"]
        for row in scores
        if row.get("counts_as_fair_baseline") and row.get("matches_or_beats_candidate")
    ]
    return {
        "task_id": core.TASK_ID,
        "baseline_independence_verified": "compute_candidate_action" not in source
        and not aliases_parent
        and not copied_candidate
        and comparison.get("old_001b_baseline_outputs_reused") is False,
        "baseline_functions_are_not_candidate_aliases": "compute_candidate_action" not in source,
        "baseline_functions_are_not_parent_001b_baseline_aliases": not aliases_parent,
        "baseline_outputs_not_copied_from_candidate_outputs": not copied_candidate,
        "old_001b_baseline_outputs_reused": comparison.get("old_001b_baseline_outputs_reused"),
        "equivalent_or_better_fair_baselines": copied_candidate,
    }


def _audit_failure_controls(repair_runner: Any) -> dict[str, Any]:
    non_invocation = repair_runner._baseline_non_invocation_failure_control()
    missing_positive = repair_runner._same_surface_positive_control_failure_control()
    return {
        "task_id": core.TASK_ID,
        "baseline_non_invocation_failure_control_verified": non_invocation.get(
            "baseline_non_invocation_failure_control_passed"
        )
        is True
        and non_invocation.get("detected_failure_id") == "baseline_non_invocation_detected",
        "missing_same_surface_positive_control_failure_control_verified": missing_positive.get(
            "missing_same_surface_positive_control_failure_control_passed"
        )
        is True
        and missing_positive.get("detected_failure_id")
        == "missing_same_surface_positive_control_detected",
        "independent_failability_verified": True,
        "baseline_non_invocation_control": non_invocation,
        "missing_same_surface_positive_control": missing_positive,
    }


def _audit_metric_provenance(repo_root: Path) -> dict[str, Any]:
    metrics = _read_parent_json(repo_root, "metric_provenance.json")
    rows = metrics.get("metrics", [])
    missing_required_fields = []
    uncallable = []
    hash_mismatches = []
    artifact_hash_mismatches = []
    literal_metrics = []
    static_dictionary_metrics = []
    failure_path_missing = []
    wrapper_only = []
    for row in rows:
        metric_id = row.get("metric_id", "<missing>")
        missing = sorted(core.REQUIRED_METRIC_FIELDS - set(row))
        if missing:
            missing_required_fields.append({"metric_id": metric_id, "missing_fields": missing})
        if not row.get("computed_not_literal"):
            literal_metrics.append(metric_id)
        if not row.get("failure_path_available"):
            failure_path_missing.append(metric_id)
        producer, salt = _resolve_producer(row.get("producer_function", ""))
        if producer is None:
            uncallable.append(metric_id)
        elif row.get("code_path_hash") != _code_path_hash(producer, salt):
            hash_mismatches.append(metric_id)
        for artifact_name, expected_hash in row.get("input_artifact_hashes", {}).items():
            path = _parent_artifact(repo_root, artifact_name)
            actual_hash = core.sha_file(path) if path.exists() else None
            if actual_hash != expected_hash:
                artifact_hash_mismatches.append(
                    {
                        "metric_id": metric_id,
                        "artifact": artifact_name,
                        "expected_hash": expected_hash,
                        "actual_hash": actual_hash,
                    }
                )
        if row.get("producer_function", "").endswith(".run_repair"):
            wrapper_only.append(metric_id)
    return {
        "task_id": core.TASK_ID,
        "metric_count": len(rows),
        "required_metric_fields": sorted(core.REQUIRED_METRIC_FIELDS),
        "reported_metric_schema_fields": metrics.get("metric_provenance_schema_fields", []),
        "all_verdict_metrics_have_callable_provenance": bool(rows)
        and not missing_required_fields
        and not uncallable
        and not hash_mismatches
        and not artifact_hash_mismatches
        and not literal_metrics
        and not static_dictionary_metrics
        and not failure_path_missing
        and not wrapper_only,
        "missing_required_fields": missing_required_fields,
        "uncallable_producers": uncallable,
        "code_path_hash_mismatches": hash_mismatches,
        "input_artifact_hash_mismatches": artifact_hash_mismatches,
        "literal_metric_detected": bool(literal_metrics),
        "static_metric_dictionary_detected": bool(static_dictionary_metrics),
        "no_literal_metrics": not literal_metrics,
        "no_static_metric_dictionaries": not static_dictionary_metrics,
        "no_copied_old_001b_results": metrics.get("no_copied_old_001b_results") is True,
        "wrapper_only_provenance_metrics": wrapper_only,
        "metrics_missing_failure_path": failure_path_missing,
    }


def _audit_ablation(repo_root: Path, parent_core: Any) -> dict[str, Any]:
    report = _read_parent_json(repo_root, "ablation_revalidation_report.json")
    pack = core.read_json(repo_root / core.PARENT_001B_ARTIFACT_DIR_REL / "controlled_evidence_pack_manifest.json")
    recomputed_report, recomputed_invocation = parent_core.run_ablations(pack)
    return {
        "task_id": core.TASK_ID,
        "ablation_revalidation_verified": report.get("ablation_revalidation_passed") is True
        and recomputed_report.get("ablation_gate_passed") is True
        and all(row.get("reran_candidate_behavior") for row in recomputed_invocation.get("invocations", []))
        and all(not row.get("copied_from_candidate_outputs") for row in recomputed_invocation.get("invocations", [])),
        "ablation_revalidation_not_copied": report.get("ablation_outputs_recomputed") is True,
        "required_ablation_count": report.get("required_ablation_count"),
        "recomputed_required_ablation_count": len(recomputed_report.get("ablations", [])),
        "insensitive_ablations": report.get("insensitive_ablations", []),
    }


def _audit_leakage(repo_root: Path, repair_core: Any) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    leakage = _read_parent_json(repo_root, "leakage_revalidation_report.json")
    access_log = _read_parent_json(repo_root, "baseline_legal_input_access_log.json")
    real_scan = repair_core.scan_for_forbidden_fields("baseline_legal_input_access_log", access_log)
    positive_scan = repair_core.scan_for_forbidden_fields(
        "baseline_legal_input_access_log", {"verifier_expected_action_id": "halt_for_scope"}
    )
    clean_scan = repair_core.scan_for_forbidden_fields(
        "baseline_legal_input_access_log", {"safe_accessed_field": "episode_id"}
    )
    manual = _read_parent_json(repo_root, "manual_injection_revalidation_report.json")
    whitelist = _read_parent_json(repo_root, "metadata_whitelist_scope_revalidation.json")
    return (
        {
            "task_id": core.TASK_ID,
            "leakage_revalidation_verified": leakage.get("leakage_revalidation_passed") is True
            and not real_scan.get("detected")
            and positive_scan.get("detected")
            and not clean_scan.get("detected"),
            "baseline_legal_input_guard_surface_scanned": leakage.get(
                "baseline_legal_input_guard_surface_scanned"
            )
            is True,
            "scanner_not_fail_able_distinguished_from_leakage_detected": leakage.get(
                "scanner_not_fail_able_distinguished_from_leakage_detected"
            )
            is True,
            "real_scan": real_scan,
            "positive_control": positive_scan,
            "clean_control": clean_scan,
        },
        {
            "task_id": core.TASK_ID,
            "manual_injection_independence_verified": manual.get("manual_injection_revalidation_passed") is True
            and manual.get("production_injector_only") is False
            and positive_scan.get("detected"),
            "production_injector_only": manual.get("production_injector_only"),
            "manual_case_count": manual.get("manual_case_count"),
            "independent_positive_control": positive_scan,
        },
        {
            "task_id": core.TASK_ID,
            "metadata_whitelist_surface_scoped": whitelist.get("metadata_whitelist_surface_scoped") is True,
            "global_reserved_metadata_key_privilege": whitelist.get("global_reserved_metadata_key_privilege"),
            "reserved_key_value_scanned_on_unprivileged_surface": whitelist.get(
                "reserved_key_value_scanned_on_unprivileged_surface"
            ),
            "privileged_surface_forbidden_value_detected": whitelist.get(
                "privileged_surface_forbidden_value_detected"
            ),
        },
    )


def _audit_replay(repo_root: Path, parent_core: Any) -> dict[str, Any]:
    pack = core.read_json(repo_root / core.PARENT_001B_ARTIFACT_DIR_REL / "controlled_evidence_pack_manifest.json")
    replay = _read_parent_json(repo_root, "behavior_causal_replay_report.json")
    recorded = {row["episode_id"]: row for row in replay.get("replay_rows", [])}
    mismatches = []
    state_mutation_changed = False
    for episode in pack.get("episodes", []):
        state = dict(episode["serialized_state"])
        observation = dict(episode["observation"])
        recomputed = parent_core.compute_candidate_action(state, observation)
        recorded_row = recorded.get(episode["episode_id"], {})
        if recomputed != recorded_row.get("recomputed_action_id") or not recorded_row.get("match"):
            mismatches.append(episode["episode_id"])
        mutated = dict(state)
        mutated["identity_continuity_state"] = (mutated["identity_continuity_state"] + 1) % len(parent_core.ACTION_IDS)
        if parent_core.compute_candidate_action(mutated, observation) != recomputed:
            state_mutation_changed = True
    return {
        "task_id": core.TASK_ID,
        "behavior_causal_replay_verified": bool(pack.get("episodes"))
        and not mismatches
        and replay.get("behavior_causal_replay_passed") is True
        and replay.get("hash_only_replay_for_behavior_claim") is False
        and replay.get("recomputed_from_serialized_state_and_observation") is True,
        "serialized_state_loaded_from_artifact": bool(pack.get("episodes")),
        "observation_loaded_from_artifact": all("observation" in episode for episode in pack.get("episodes", [])),
        "candidate_action_recomputed": True,
        "recomputed_action_matches_recorded_action": not mismatches,
        "serialized_state_causal_consumption_verified": state_mutation_changed,
        "hash_only_replay_for_behavior_claim": replay.get("hash_only_replay_for_behavior_claim"),
        "mismatches": mismatches,
    }


def _audit_frozen_inputs(repo_root: Path) -> dict[str, Any]:
    frozen = _read_parent_json(repo_root, "frozen_input_consumption_report.json")
    unused = []
    for family, row in frozen.get("families", {}).items():
        unused.extend(f"{family}:{value}" for value in row.get("unused", []))
    return {
        "task_id": core.TASK_ID,
        "frozen_inputs_consumed": frozen.get("frozen_inputs_consumed") is True and not unused,
        "unused_frozen_inputs": unused,
        "families_checked": sorted(frozen.get("families", {})),
    }


def _audit_source_integrity(repo_root: Path) -> dict[str, Any]:
    source_dir = repo_root / core.PARENT_001D_SOURCE_DIR_REL
    artifact_dir = repo_root / core.PARENT_001D_ARTIFACT_DIR_REL
    source_hashes = _hash_paths(sorted(source_dir.glob("*.py")), repo_root)
    artifact_hashes = _hash_paths(sorted(artifact_dir.glob("*.json")) + sorted(artifact_dir.glob("*.txt")), repo_root)
    return {
        "task_id": core.TASK_ID,
        "source_artifact_integrity_verified": bool(source_hashes) and bool(artifact_hashes),
        "source_hashes": source_hashes,
        "artifact_hashes": artifact_hashes,
    }


def _audit_negative_evidence(repo_root: Path) -> dict[str, Any]:
    negative = _read_parent_json(repo_root, "negative_evidence_preservation_report.json")
    result_001c = core.read_json(repo_root / core.PARENT_001C_ARTIFACT_DIR_REL / "result.json")
    result_001b = core.read_json(repo_root / core.PARENT_001B_ARTIFACT_DIR_REL / "result.json")
    return {
        "task_id": core.TASK_ID,
        "001b_remains_historically_blocked_by_001c": negative.get(
            "001b_historical_block_status_preserved"
        )
        is True
        and result_001b.get("verdict")
        == "ego_mainline_admission_executable_001b_bounded_contract_gate_pass"
        and result_001c.get("verdict")
        == "ego_mainline_admission_executable_001b_independent_audit_001c_block_baseline_gap",
        "001c_remains_canonical_historical_blocker": negative.get("001c_blocker_preserved") is True,
        "001d_is_repair_evidence_only": "repair" in _read_parent_json(repo_root, "result.json").get("layer", ""),
        "negative_evidence_rewrite_detected": negative.get("negative_evidence_rewrite_detected") is True,
        "001c_blocker_converted_to_caveat": negative.get("001c_blocker_converted_to_caveat") is True,
    }


def _audit_scope_and_claim(repo_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    result = _read_parent_json(repo_root, "result.json")
    flags = result.get("authorization_flags", {})
    forbidden_claims = {
        "EGO readiness",
        "EGO mainline readiness",
        "runtime admissibility",
        "bridge readiness",
        "companion readiness",
        "mechanism validity",
        "theory validity",
        "agency",
        "selfhood",
        "consciousness",
        "real emotion",
        "real relationship learning",
        "production readiness",
    }
    result_text = core.canonical_json(result)
    not_prove = set(result.get("what_this_does_not_prove", []))
    inflated = sorted(claim for claim in forbidden_claims if claim in result_text and claim not in not_prove)
    claim = {
        "task_id": core.TASK_ID,
        "claim_ceiling_preserved": result.get("claim_ceiling")
        == "bounded baseline-legal-input repair evidence for EGO-MAINLINE-ADMISSION-EXECUTABLE-001B under synthetic / controlled conditions only"
        and not inflated,
        "001d_not_treated_as_ego_readiness": not inflated,
        "001d_not_treated_as_runtime_admissibility": not inflated,
        "inflated_claims_detected": inflated,
        "parent_claim_ceiling": result.get("claim_ceiling"),
        "audit_claim_ceiling": core.CLAIM_CEILING,
    }
    scope = {
        "task_id": core.TASK_ID,
        "no_scope_leak": all(value is False for value in flags.values() if isinstance(value, bool)),
        "no_Ego_repo_modification": flags.get("ego_repository_modification_authorized") is False,
        "no_runtime_or_product_work": flags.get("ego_mainline_runtime_authorized") is False
        and flags.get("bridge_runtime_authorized") is False
        and flags.get("llm_rag_authorized") is False
        and flags.get("runtime_or_product_work_authorized") is False,
        "authorization_flags": flags,
    }
    return claim, scope


def _build_findings(audits: dict[str, Any]) -> list[dict[str, Any]]:
    checks = [
        (
            "missing_parent_anchor",
            not audits["parents"]["all_parent_anchors_verified"],
            core.VERDICT_BLOCK_PARENT,
            "parent_anchor_verification.json",
            "one or more local or remote parent anchors did not verify",
        ),
        (
            "001c_not_preserved",
            not audits["exact"]["001c_blocker_preserved"],
            core.VERDICT_BLOCK_001C,
            "exact_blocker_repair_audit.json",
            "001C blocker was not preserved as historical negative evidence",
        ),
        (
            "repair_scope_expanded",
            not audits["exact"]["001d_repair_scope_exact"],
            core.VERDICT_BLOCK_REPAIR_SCOPE,
            "exact_blocker_repair_audit.json",
            "001D repair scope differs from the exact three 001C blockers",
        ),
        (
            "baseline_legal_input_gap",
            not audits["baseline_legal"]["baseline_legal_input_schema_valid"]
            or not audits["baseline_legal"]["baseline_action_generation_receives_only_legal_inputs"]
            or not audits["baseline_legal"]["baseline_output_rows_generated_after_legal_filtering"],
            core.VERDICT_BLOCK_BASELINE_LEGAL,
            "baseline_legal_input_audit.json",
            "baseline-visible schema, legal access, or output filtering failed",
        ),
        (
            "equivalent_label_leakage",
            not audits["equivalent"]["equivalent_verifier_labels_excluded"],
            core.VERDICT_BLOCK_EQUIVALENT_LABEL,
            "baseline_equivalent_label_leakage_audit.json",
            "equivalent verifier-label leakage detected in baseline-visible surfaces",
        ),
        (
            "runtime_guard_gap",
            not audits["runtime_guard"]["baseline_runtime_guard_complete"]
            or not audits["runtime_guard"]["forbidden_field_negative_control_fail_able"]
            or not audits["runtime_guard"]["equivalent_label_negative_control_fail_able"],
            core.VERDICT_BLOCK_RUNTIME_GUARD,
            "baseline_runtime_access_guard_audit.json",
            "runtime guard coverage or negative controls failed",
        ),
        (
            "baseline_static_scan_gap",
            not audits["static_scan"]["baseline_static_scan_valid"],
            core.VERDICT_BLOCK_STATIC_SCAN,
            "baseline_static_scan_audit.json",
            "static forbidden-reference scan did not distinguish repaired source from blocker context",
        ),
        (
            "baseline_invocation_gap",
            not audits["baseline_invocation"]["all_required_baselines_invoked"]
            or not audits["baseline_invocation"]["baseline_outputs_exist_before_aggregation"],
            core.VERDICT_BLOCK_INVOCATION,
            "baseline_invocation_audit.json",
            "baseline invocation or output-before-aggregation failed",
        ),
        (
            "baseline_independence_gap",
            not audits["baseline_independence"]["baseline_independence_verified"],
            core.VERDICT_BLOCK_INDEPENDENCE,
            "baseline_independence_audit.json",
            "baseline implementation is not independently verified",
        ),
        (
            "failure_path_gap",
            not audits["failure_paths"]["baseline_non_invocation_failure_control_verified"]
            or not audits["failure_paths"][
                "missing_same_surface_positive_control_failure_control_verified"
            ],
            core.VERDICT_BLOCK_FAILURE_PATH,
            "failure_path_control_audit.json",
            "one or both named failure-path controls are not fail-able",
        ),
        (
            "metric_provenance_gap",
            not audits["metrics"]["all_verdict_metrics_have_callable_provenance"],
            core.VERDICT_BLOCK_METRIC,
            "metric_provenance_audit.json",
            "001D metric provenance does not satisfy inherited callable provenance requirements",
        ),
        (
            "ablation_gap",
            not audits["ablation"]["ablation_revalidation_verified"],
            core.VERDICT_BLOCK_ABLATION,
            "ablation_revalidation_audit.json",
            "ablation revalidation is not independently verified",
        ),
        (
            "leakage_gap",
            not audits["leakage"]["leakage_revalidation_verified"],
            core.VERDICT_BLOCK_LEAKAGE,
            "leakage_revalidation_audit.json",
            "leakage revalidation is not independently verified",
        ),
        (
            "replay_gap",
            not audits["replay"]["behavior_causal_replay_verified"],
            core.VERDICT_BLOCK_REPLAY,
            "behavior_causal_replay_audit.json",
            "behavior replay is not independently behavior-causal",
        ),
        (
            "unused_frozen_input",
            not audits["frozen"]["frozen_inputs_consumed"],
            core.VERDICT_BLOCK_UNUSED_FROZEN,
            "frozen_input_consumption_audit.json",
            "frozen inputs were declared but not consumed",
        ),
        (
            "old_artifact_mutation",
            not audits["old_mutation"]["old_001b_artifacts_not_modified"]
            or not audits["old_mutation"]["old_001c_artifacts_not_modified"]
            or not audits["old_mutation"]["old_001d_artifacts_not_modified"],
            core.VERDICT_BLOCK_OLD_MUTATION,
            "old_artifact_mutation_audit.json",
            "one or more old artifact directories changed during audit",
        ),
        (
            "negative_evidence_rewrite",
            not audits["negative"]["001b_remains_historically_blocked_by_001c"]
            or not audits["negative"]["001c_remains_canonical_historical_blocker"]
            or audits["negative"]["negative_evidence_rewrite_detected"]
            or audits["negative"]["001c_blocker_converted_to_caveat"],
            core.VERDICT_BLOCK_NEGATIVE,
            "negative_evidence_preservation_audit.json",
            "negative evidence preservation failed",
        ),
        (
            "scope_leak",
            not audits["scope"]["no_scope_leak"],
            core.VERDICT_BLOCK_SCOPE,
            "scope_leak_audit.json",
            "scope leak or authorization flag detected",
        ),
        (
            "claim_inflation",
            not audits["claim"]["claim_ceiling_preserved"],
            core.VERDICT_BLOCK_CLAIM,
            "claim_ceiling_audit.json",
            "claim ceiling inflated beyond 001D repair evidence",
        ),
    ]
    findings = []
    for finding_id, failed, verdict, artifact, notes in checks:
        if failed:
            findings.append(
                {
                    "finding_id": finding_id,
                    "severity": "blocker",
                    "verdict": verdict,
                    "evidence_artifact": artifact,
                    "notes": notes,
                }
            )
    return findings


def _old_artifact_mutation_report(
    before: dict[str, dict[str, str]], after: dict[str, dict[str, str]]
) -> dict[str, Any]:
    def mutated(label: str) -> list[str]:
        before_hashes = before[label]
        after_hashes = after[label]
        return sorted(path for path, old_hash in before_hashes.items() if after_hashes.get(path) != old_hash)

    return {
        "task_id": core.TASK_ID,
        "old_001b_artifacts_not_modified": before["001b"] == after["001b"],
        "old_001c_artifacts_not_modified": before["001c"] == after["001c"],
        "old_001d_artifacts_not_modified": before["001d"] == after["001d"],
        "old_001b_mutated_paths": mutated("001b"),
        "old_001c_mutated_paths": mutated("001c"),
        "old_001d_mutated_paths": mutated("001d"),
        "before_hashes": before,
        "after_hashes": after,
    }


def run_audit(*, repo_root: Path, output_dir: Path, verify_remote: bool = True) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    _import_from_src(repo_root, "ego_mainline_admission_executable_001d_independent_audit_001e.core")
    parent_core = _import_from_src(repo_root, "ego_mainline_admission_executable_001b.core")
    repair_core = _import_from_src(
        repo_root, "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d.core"
    )
    repair_runner = _import_from_src(
        repo_root, "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d.runner"
    )
    old_paths = {
        "001b": repo_root / core.PARENT_001B_ARTIFACT_DIR_REL,
        "001c": repo_root / core.PARENT_001C_ARTIFACT_DIR_REL,
        "001d": repo_root / core.PARENT_001D_ARTIFACT_DIR_REL,
    }
    old_before = {label: _hash_tree(path, repo_root) for label, path in old_paths.items()}

    parents = _verify_parent_anchors(repo_root, verify_remote)
    exact = _audit_exact_blocker_repair(repo_root)
    baseline_legal = _audit_baseline_legal_input(repo_root)
    equivalent = _audit_equivalent_label_leakage(repo_root, repair_core)
    runtime_guard = _audit_runtime_guard(repo_root, repair_core, repair_runner)
    static_scan = _audit_static_scan(repo_root, repair_core)
    baseline_invocation = _audit_baseline_invocation(repo_root, repair_core)
    baseline_independence = _audit_baseline_independence(repo_root, repair_core)
    failure_paths = _audit_failure_controls(repair_runner)
    metrics = _audit_metric_provenance(repo_root)
    ablation = _audit_ablation(repo_root, parent_core)
    leakage, manual, whitelist = _audit_leakage(repo_root, repair_core)
    replay = _audit_replay(repo_root, parent_core)
    frozen = _audit_frozen_inputs(repo_root)
    source_integrity = _audit_source_integrity(repo_root)
    negative = _audit_negative_evidence(repo_root)
    claim, scope = _audit_scope_and_claim(repo_root)

    old_after = {label: _hash_tree(path, repo_root) for label, path in old_paths.items()}
    old_mutation = _old_artifact_mutation_report(old_before, old_after)

    audits = {
        "parents": parents,
        "exact": exact,
        "baseline_legal": baseline_legal,
        "equivalent": equivalent,
        "runtime_guard": runtime_guard,
        "static_scan": static_scan,
        "baseline_invocation": baseline_invocation,
        "baseline_independence": baseline_independence,
        "failure_paths": failure_paths,
        "metrics": metrics,
        "ablation": ablation,
        "leakage": leakage,
        "manual": manual,
        "whitelist": whitelist,
        "replay": replay,
        "frozen": frozen,
        "source_integrity": source_integrity,
        "old_mutation": old_mutation,
        "negative": negative,
        "claim": claim,
        "scope": scope,
    }
    findings = _build_findings(audits)
    stop_flags = {finding["finding_id"]: True for finding in findings}
    verdict, stop_conditions = core.evaluate_verdict(stop_flags)
    acceptance_gates = {
        "parent_001s_anchor_verified": any(
            row["tag"] == "remote-anchor-001s-3d90e1a" and row["local_verified"] and row["remote_verified"]
            for row in parents["anchors"]
        ),
        "parent_001r_anchor_verified": any(
            row["tag"] == "remote-anchor-001r-0fdf451" and row["local_verified"] and row["remote_verified"]
            for row in parents["anchors"]
        ),
        "parent_001q_anchor_verified": any(
            row["tag"] == "remote-anchor-001q-60a504e" and row["local_verified"] and row["remote_verified"]
            for row in parents["anchors"]
        ),
        "parent_001p_anchor_verified": any(
            row["tag"] == "remote-anchor-001p-cda09dc" and row["local_verified"] and row["remote_verified"]
            for row in parents["anchors"]
        ),
        "parent_001o_anchor_verified": any(
            row["tag"] == "remote-anchor-001o-f648dac" and row["local_verified"] and row["remote_verified"]
            for row in parents["anchors"]
        ),
        "computed_evidence_contract_loaded": (
            repo_root / "docs" / "codex" / "contracts" / "COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md"
        ).exists(),
        "001c_blocker_preserved": exact["001c_blocker_preserved"],
        "001d_repair_scope_exact": exact["001d_repair_scope_exact"],
        "baseline_legal_input_schema_valid": baseline_legal["baseline_legal_input_schema_valid"],
        "equivalent_verifier_labels_excluded": equivalent["equivalent_verifier_labels_excluded"],
        "baseline_runtime_guard_complete": runtime_guard["baseline_runtime_guard_complete"],
        "forbidden_field_negative_control_fail_able": runtime_guard[
            "forbidden_field_negative_control_fail_able"
        ],
        "equivalent_label_negative_control_fail_able": runtime_guard[
            "equivalent_label_negative_control_fail_able"
        ],
        "baseline_static_scan_valid": static_scan["baseline_static_scan_valid"],
        "all_required_baselines_invoked": baseline_invocation["all_required_baselines_invoked"],
        "baseline_outputs_exist_before_aggregation": baseline_invocation[
            "baseline_outputs_exist_before_aggregation"
        ],
        "baseline_independence_verified": baseline_independence["baseline_independence_verified"],
        "baseline_non_invocation_failure_control_verified": failure_paths[
            "baseline_non_invocation_failure_control_verified"
        ],
        "missing_same_surface_positive_control_failure_control_verified": failure_paths[
            "missing_same_surface_positive_control_failure_control_verified"
        ],
        "all_verdict_metrics_have_callable_provenance": metrics[
            "all_verdict_metrics_have_callable_provenance"
        ],
        "no_literal_metrics": metrics["no_literal_metrics"],
        "no_static_metric_dictionaries": metrics["no_static_metric_dictionaries"],
        "no_copied_old_001b_results": metrics["no_copied_old_001b_results"],
        "ablation_revalidation_verified": ablation["ablation_revalidation_verified"],
        "leakage_revalidation_verified": leakage["leakage_revalidation_verified"],
        "manual_injection_independence_verified": manual["manual_injection_independence_verified"],
        "metadata_whitelist_surface_scoped": whitelist["metadata_whitelist_surface_scoped"],
        "behavior_causal_replay_verified": replay["behavior_causal_replay_verified"],
        "frozen_inputs_consumed": frozen["frozen_inputs_consumed"],
        "old_001b_artifacts_not_modified": old_mutation["old_001b_artifacts_not_modified"],
        "old_001c_artifacts_not_modified": old_mutation["old_001c_artifacts_not_modified"],
        "old_001d_artifacts_not_modified": old_mutation["old_001d_artifacts_not_modified"],
        "negative_evidence_preserved": negative["001b_remains_historically_blocked_by_001c"]
        and negative["001c_remains_canonical_historical_blocker"]
        and not negative["negative_evidence_rewrite_detected"],
        "no_scope_leak": scope["no_scope_leak"],
        "no_claim_inflation": claim["claim_ceiling_preserved"],
        "no_Ego_repo_modification": scope["no_Ego_repo_modification"],
        "no_runtime_or_product_work": scope["no_runtime_or_product_work"],
    }
    result = {
        "task_id": core.TASK_ID,
        "parent_task_id": core.PARENT_001D_TASK_ID,
        "layer": core.LAYER,
        "verdict": verdict,
        "bounded_pass": not findings and all(acceptance_gates.values()),
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "claim_ceiling": core.CLAIM_CEILING,
        "authorization_flags": core.AUTHORIZATION_FLAGS,
        "acceptance_gates": acceptance_gates,
        "stop_conditions_triggered": stop_conditions,
        "parent_anchors_verified": parents["all_parent_anchors_verified"],
        "exact_blocker_repair_audit_result": exact,
        "baseline_legal_input_audit_result": baseline_legal,
        "equivalent_label_leakage_audit_result": equivalent,
        "runtime_access_guard_audit_result": runtime_guard,
        "static_scan_audit_result": static_scan,
        "baseline_invocation_result": baseline_invocation,
        "baseline_independence_result": baseline_independence,
        "failure_path_control_audit_result": failure_paths,
        "metric_provenance_audit_result": metrics,
        "ablation_revalidation_audit_result": ablation,
        "leakage_revalidation_audit_result": leakage,
        "manual_injection_audit_result": manual,
        "metadata_whitelist_audit_result": whitelist,
        "replay_audit_result": replay,
        "frozen_input_consumption_audit_result": frozen,
        "old_artifact_mutation_result": {
            "old_001b_artifacts_not_modified": old_mutation["old_001b_artifacts_not_modified"],
            "old_001c_artifacts_not_modified": old_mutation["old_001c_artifacts_not_modified"],
            "old_001d_artifacts_not_modified": old_mutation["old_001d_artifacts_not_modified"],
            "old_001b_mutated_paths": old_mutation["old_001b_mutated_paths"],
            "old_001c_mutated_paths": old_mutation["old_001c_mutated_paths"],
            "old_001d_mutated_paths": old_mutation["old_001d_mutated_paths"],
        },
        "negative_evidence_preservation_result": negative,
        "scope_claim_ceiling_result": {
            "claim_ceiling_preserved": claim["claim_ceiling_preserved"],
            "no_scope_leak": scope["no_scope_leak"],
            "no_Ego_repo_modification": scope["no_Ego_repo_modification"],
            "no_runtime_or_product_work": scope["no_runtime_or_product_work"],
        },
        "what_this_does_not_prove": [
            "001B positive evidence restoration",
            "EGO readiness",
            "EGO mainline readiness",
            "runtime admissibility",
            "bridge readiness",
            "companion readiness",
            "mechanism validity",
            "theory validity",
            "agency",
            "selfhood",
            "consciousness",
            "real emotion",
            "real relationship learning",
            "stable user benefit",
            "production readiness",
            "correctness of any future EGO runtime",
        ],
    }
    artifact_map = {
        "parent_anchor_verification.json": parents,
        "exact_blocker_repair_audit.json": exact,
        "baseline_legal_input_audit.json": baseline_legal,
        "baseline_equivalent_label_leakage_audit.json": equivalent,
        "baseline_runtime_access_guard_audit.json": runtime_guard,
        "baseline_static_scan_audit.json": static_scan,
        "baseline_invocation_audit.json": baseline_invocation,
        "baseline_independence_audit.json": baseline_independence,
        "failure_path_control_audit.json": failure_paths,
        "metric_provenance_audit.json": metrics,
        "ablation_revalidation_audit.json": ablation,
        "leakage_revalidation_audit.json": leakage,
        "manual_injection_revalidation_audit.json": manual,
        "metadata_whitelist_scope_audit.json": whitelist,
        "behavior_causal_replay_audit.json": replay,
        "frozen_input_consumption_audit.json": frozen,
        "source_artifact_integrity_audit.json": source_integrity,
        "old_artifact_mutation_audit.json": old_mutation,
        "negative_evidence_preservation_audit.json": negative,
        "claim_ceiling_audit.json": claim,
        "scope_leak_audit.json": scope,
        "audit_finding_inventory.json": {
            "task_id": core.TASK_ID,
            "findings": findings,
            "finding_count": len(findings),
        },
        "result.json": result,
    }
    for name, data in artifact_map.items():
        core.write_json(output_dir / name, data)
    if findings:
        core.write_json(
            output_dir / "blocker_report.json",
            {
                "task_id": core.TASK_ID,
                "verdict": verdict,
                "stop_conditions_triggered": stop_conditions,
                "minimum_patch": "repair exact new blocker in a later bounded task; do not rewrite 001B, 001C, or 001D artifacts",
            },
        )
    core.write_text(output_dir / "claim_ceiling.txt", core.CLAIM_CEILING + "\n")
    return result
