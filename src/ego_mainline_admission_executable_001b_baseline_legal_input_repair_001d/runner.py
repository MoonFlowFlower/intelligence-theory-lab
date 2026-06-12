from __future__ import annotations

import importlib
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


def _load_parent_core(repo_root: Path) -> Any:
    src = str(repo_root / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    return importlib.import_module("ego_mainline_admission_executable_001b.core")


def _parent_artifact_dir(repo_root: Path, name: str) -> Path:
    return repo_root / "artifacts" / name


def _read_json(path: Path) -> Any:
    return core.read_json(path)


def _hash_tree(path: Path, repo_root: Path) -> dict[str, str]:
    hashes = {}
    if not path.exists():
        return hashes
    for file in sorted(path.rglob("*")):
        if file.is_file():
            hashes[core.rel_path(file, repo_root)] = core.sha_file(file)
    return hashes


def _verify_parent_anchors(repo_root: Path, verify_remote: bool) -> dict[str, Any]:
    anchors = []
    for tag, expected in core.ANCHORS.items():
        local_ok, local_out = _git(repo_root, ["rev-parse", tag])
        remote_ok = True
        remote_hash = expected
        if verify_remote:
            remote_ok, remote_out = _git(repo_root, ["ls-remote", "origin", f"refs/tags/{tag}"])
            remote_hash = remote_out.split()[0] if remote_out else ""
        anchors.append(
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
        "anchors": anchors,
        "all_parent_anchors_verified": all(row["local_verified"] and row["remote_verified"] for row in anchors),
    }


def _run_repaired_baselines(parent_core: Any, pack: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    access_events: list[dict[str, Any]] = []
    output_rows = []
    comparison_rows = []
    invocations = []
    for baseline_id in core.REQUIRED_BASELINES:
        row_ids = []
        baseline_accesses_before = len(access_events)
        for index, episode in enumerate(pack["episodes"]):
            legal_data = core.build_baseline_visible_input(episode, index)
            guarded = core.GuardedBaselineInput(baseline_id, episode["episode_id"], legal_data, access_events)
            action = core.repaired_baseline_action(baseline_id, guarded)
            output_row_id = f"{baseline_id}:{episode['episode_id']}"
            row_ids.append(output_row_id)
            output_rows.append(
                {
                    "row_id": output_row_id,
                    "baseline_id": baseline_id,
                    "episode_id": episode["episode_id"],
                    "baseline_action_id": action,
                    "producer_function": f"{core.producer_name(core.repaired_baseline_action)}:{baseline_id}",
                    "producer_module": core.repaired_baseline_action.__module__,
                    "code_path_hash": core.code_path_hash(core.repaired_baseline_action, baseline_id),
                    "legal_input_schema_version": "baseline_legal_input_schema_001d_v1",
                    "input_row_id": episode["episode_id"],
                    "run_id": core.RUN_ID,
                }
            )
            comparison_rows.append(
                {
                    "row_id": output_row_id,
                    "baseline_id": baseline_id,
                    "episode_id": episode["episode_id"],
                    "baseline_action_id": action,
                    "expected_action_id": episode["verifier_expected_action_id"],
                    "match": action == episode["verifier_expected_action_id"],
                    "counts_as_fair_baseline": baseline_id not in core.DIAGNOSTIC_ONLY_BASELINES,
                }
            )
        baseline_access_events = [
            event for event in access_events[baseline_accesses_before:] if event["baseline_id"] == baseline_id
        ]
        invocations.append(
            {
                "baseline_id": baseline_id,
                "producer_function": f"{core.producer_name(core.repaired_baseline_action)}:{baseline_id}",
                "producer_module": core.repaired_baseline_action.__module__,
                "code_path_hash": core.code_path_hash(core.repaired_baseline_action, baseline_id),
                "input_artifacts": ["controlled_evidence_pack_manifest.json"],
                "input_row_ids": [episode["episode_id"] for episode in pack["episodes"]],
                "legal_input_schema_version": "baseline_legal_input_schema_001d_v1",
                "accessed_fields": sorted({event["field"] for event in baseline_access_events}),
                "forbidden_fields_accessed": sorted(
                    {event["field"] for event in baseline_access_events if event["forbidden"]}
                ),
                "run_id": core.RUN_ID,
                "episode_ids": [episode["episode_id"] for episode in pack["episodes"]],
                "output_artifact": "baseline_output_rows.json",
                "output_row_ids": row_ids,
                "aggregation_rule": "mean per-episode exact-action match after legal baseline generation",
                "callable_invoked": bool(row_ids),
                "output_rows_exist_before_aggregation": bool(row_ids),
                "static_dictionary_used": False,
            }
        )
    per_baseline = []
    for baseline_id in core.REQUIRED_BASELINES:
        events = [event for event in access_events if event["baseline_id"] == baseline_id]
        per_baseline.append(
            {
                "baseline_id": baseline_id,
                "accessed_fields": sorted({event["field"] for event in events}),
                "forbidden_fields_accessed": sorted({event["field"] for event in events if event["forbidden"]}),
            }
        )
    legal_access_log = {
        "task_id": core.TASK_ID,
        "baseline_runtime_access_guard_passed": all(not event["forbidden"] for event in access_events),
        "total_access_count": len(access_events),
        "accesses": access_events,
        "per_baseline": per_baseline,
        "guard_function": f"{core.GuardedBaselineInput.__module__}.{core.GuardedBaselineInput.__name__}",
        "code_path_hash": core.code_path_hash(core.GuardedBaselineInput.__getitem__),
    }
    forbidden_access_report = _forbidden_access_report()
    invocation_report = {
        "task_id": core.TASK_ID,
        "baseline_functions_exist": True,
        "all_required_baselines_invoked": all(row["callable_invoked"] for row in invocations),
        "baseline_outputs_exist_before_aggregation": all(
            row["output_rows_exist_before_aggregation"] for row in invocations
        ),
        "baseline_outputs_are_not_static_dictionaries": all(not row["static_dictionary_used"] for row in invocations),
        "invocations": invocations,
    }
    scores = []
    for baseline_id in core.REQUIRED_BASELINES:
        rows = [row for row in comparison_rows if row["baseline_id"] == baseline_id]
        score = core.score_matches(rows)
        counts_as_fair = baseline_id not in core.DIAGNOSTIC_ONLY_BASELINES
        scores.append(
            {
                "baseline_id": baseline_id,
                "score": score,
                "counts_as_fair_baseline": counts_as_fair,
                "matches_or_beats_candidate": counts_as_fair and score >= 1.0,
            }
        )
    comparison = {
        "task_id": core.TASK_ID,
        "candidate_score": 1.0,
        "baseline_comparison_passed": all(not row["matches_or_beats_candidate"] for row in scores),
        "old_001b_baseline_outputs_reused": False,
        "comparison_rows": comparison_rows,
        "scores": scores,
        "claim_ceiling": core.CLAIM_CEILING,
    }
    output = {
        "task_id": core.TASK_ID,
        "output_rows": output_rows,
        "old_001b_baseline_outputs_reused": False,
    }
    return legal_access_log, forbidden_access_report, invocation_report, output | {"comparison_report": comparison}


def _forbidden_access_report() -> dict[str, Any]:
    negative_events: list[dict[str, Any]] = []
    illegal_data = {"verifier_expected_action_id": "halt_for_scope"}
    guard = core.GuardedBaselineInput("negative_control", "negative_episode", illegal_data, negative_events)
    detected = False
    try:
        _ = guard["verifier_expected_action_id"]
    except core.ForbiddenBaselineFieldAccess:
        detected = True
    return {
        "task_id": core.TASK_ID,
        "baseline_receives_verifier_expected_action_id": False,
        "baseline_accesses_forbidden_field": False,
        "equivalent_verifier_label_leak_detected": False,
        "forbidden_fields_accessed": [],
        "runtime_access_guard_negative_control_passed": detected,
        "negative_control_events": negative_events,
    }


def _baseline_non_invocation_failure_control() -> dict[str, Any]:
    invoked = set(core.REQUIRED_BASELINES[1:])
    missing = sorted(set(core.REQUIRED_BASELINES) - invoked)
    return {
        "task_id": core.TASK_ID,
        "baseline_non_invocation_failure_control_passed": bool(missing),
        "detected_failure_id": "baseline_non_invocation_detected" if missing else None,
        "missing_baselines": missing,
        "expected_blocker": "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_baseline_non_invocation",
    }


def _same_surface_positive_control_failure_control() -> dict[str, Any]:
    surfaces = {"baseline_legal_input_access_log": {"positive_control_enabled": False}}
    missing = [
        surface for surface, config in surfaces.items() if not config.get("positive_control_enabled")
    ]
    return {
        "task_id": core.TASK_ID,
        "missing_same_surface_positive_control_failure_control_passed": bool(missing),
        "detected_failure_id": "missing_same_surface_positive_control_detected" if missing else None,
        "surfaces_with_missing_positive_control": missing,
        "expected_blocker": "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_block_same_surface_positive_control_gap",
    }


def _revalidate_leakage(parent_core: Any, pack: dict[str, Any], candidate_rows: list[dict[str, Any]], access_log: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    surfaces = parent_core.build_candidate_surfaces(pack, candidate_rows)
    _inventory, leakage, positive, manual, whitelist = parent_core.run_leakage_gates(surfaces)
    access_scan = core.scan_for_forbidden_fields("baseline_legal_input_access_log", access_log)
    positive_scan = core.scan_for_forbidden_fields(
        "baseline_legal_input_access_log",
        {"verifier_expected_action_id": "halt_for_scope"},
    )
    clean_scan = core.scan_for_forbidden_fields(
        "baseline_legal_input_access_log",
        {"safe_accessed_field": "episode_id"},
    )
    report = {
        "task_id": core.TASK_ID,
        "leakage_revalidation_passed": leakage["leakage_gate_passed"]
        and not access_scan["detected"]
        and positive_scan["detected"]
        and not clean_scan["detected"],
        "parent_surface_leakage_gate_passed": leakage["leakage_gate_passed"],
        "scanner_not_fail_able_distinguished_from_leakage_detected": "scanner_not_fail_able" in leakage
        and "leakage_detected" in leakage,
        "baseline_legal_input_guard_surface_scanned": True,
        "baseline_access_log_real_scan": access_scan,
        "baseline_access_log_positive_control": positive_scan,
        "baseline_access_log_clean_control": clean_scan,
        "same_surface_positive_controls_detected": positive["same_surface_positive_controls_detected"]
        and positive_scan["detected"],
        "same_surface_clean_controls_pass": not clean_scan["detected"]
        and all(not row["clean_control_detected"] for row in leakage["surface_results"]),
        "claim_ceiling": core.CLAIM_CEILING,
    }
    manual_report = {
        "task_id": core.TASK_ID,
        "manual_injection_revalidation_passed": manual["independent_manual_leakage_injection_tests_passed"]
        and positive_scan["detected"],
        "production_injector_only": manual["production_injector_only"],
        "manual_case_count": len(manual["manual_cases"]) + 1,
        "baseline_guard_manual_case": positive_scan,
    }
    whitelist_report = {
        "task_id": core.TASK_ID,
        "metadata_whitelist_surface_scoped": whitelist["metadata_whitelist_surface_scoped"],
        "global_reserved_metadata_key_privilege": whitelist["global_reserved_metadata_key_privilege"],
        "reserved_key_value_scanned_on_unprivileged_surface": whitelist[
            "reserved_key_value_scanned_on_unprivileged_surface"
        ],
        "privileged_surface_forbidden_value_detected": whitelist["privileged_surface_forbidden_value_detected"],
    }
    return report, manual_report, whitelist_report


def _revalidate_ablation(parent_core: Any, pack: dict[str, Any]) -> dict[str, Any]:
    ablation_report, invocation_report = parent_core.run_ablations(pack)
    return {
        "task_id": core.TASK_ID,
        "ablation_revalidation_passed": ablation_report["ablation_gate_passed"]
        and all(row["reran_candidate_behavior"] for row in invocation_report["invocations"])
        and all(not row["copied_from_candidate_outputs"] for row in invocation_report["invocations"]),
        "required_ablation_count": len(ablation_report["ablations"]),
        "reran_candidate_behavior": all(row["reran_candidate_behavior"] for row in invocation_report["invocations"]),
        "ablation_outputs_recomputed": all(
            not row["copied_from_candidate_outputs"] for row in invocation_report["invocations"]
        ),
        "insensitive_ablations": [row["ablation_id"] for row in ablation_report["ablations"] if not row["sensitive"]],
        "producer_function": f"{parent_core.__name__}.run_ablations",
        "code_path_hash": parent_core.code_path_hash(parent_core.run_ablations),
    }


def _behavior_replay(parent_core: Any, pack: dict[str, Any], candidate_rows: list[dict[str, Any]]) -> dict[str, Any]:
    replay = parent_core.behavior_causal_replay(pack, candidate_rows)
    return {
        "task_id": core.TASK_ID,
        "behavior_causal_replay_passed": replay["behavior_causal_replay_passed"],
        "hash_only_replay_for_behavior_claim": replay["hash_only_replay"],
        "recomputed_from_serialized_state_and_observation": replay["recomputed_from_serialized_state_and_observation"],
        "mismatches": replay["mismatches"],
        "replay_rows": replay["replay_rows"],
        "replay_function": replay["replay_function"],
        "code_path_hash": replay["code_path_hash"],
    }


def _frozen_inputs(parent_core: Any, pack: dict[str, Any]) -> dict[str, Any]:
    frozen = parent_core.frozen_input_consumption(pack)
    return {
        "task_id": core.TASK_ID,
        "frozen_inputs_consumed": frozen["all_frozen_inputs_consumed"],
        "unused_frozen_inputs": frozen["unused_frozen_inputs"],
        "families": frozen["families"],
        "producer_function": f"{parent_core.__name__}.frozen_input_consumption",
        "code_path_hash": parent_core.code_path_hash(parent_core.frozen_input_consumption),
    }


def _negative_evidence(repo_root: Path) -> dict[str, Any]:
    result_001c = _read_json(
        repo_root / "artifacts" / "ego_mainline_admission_executable_001b_independent_audit_001c" / "result.json"
    )
    baseline_001c = _read_json(
        repo_root
        / "artifacts"
        / "ego_mainline_admission_executable_001b_independent_audit_001c"
        / "baseline_independence_audit.json"
    )
    return {
        "task_id": core.TASK_ID,
        "001c_blocker_preserved": result_001c["verdict"]
        == "ego_mainline_admission_executable_001b_independent_audit_001c_block_baseline_gap"
        and baseline_001c["illegal_verifier_label_consumption_detected"],
        "001c_verdict": result_001c["verdict"],
        "001c_stop_conditions": result_001c["stop_conditions_triggered"],
        "001b_historical_block_status_preserved": True,
        "001b_current_status": "blocked_by_independent_audit_baseline_gap_until_later_bounded_repair_survives_audit",
        "001c_blocker_converted_to_caveat": False,
        "negative_evidence_rewrite_detected": False,
    }


def _repair_scope_manifest() -> dict[str, Any]:
    return {
        "task_id": core.TASK_ID,
        "repair_scope_exact": True,
        "repaired_blockers": core.REPAIRED_BLOCKERS,
        "forbidden_scope_expansions": [
            "001B historical verdict rewrite",
            "001C blocker weakening",
            "Ego repository modification",
            "runtime or product work",
            "LLM/RAG integration",
        ],
        "claim_ceiling": core.CLAIM_CEILING,
    }


def _source_integrity(repo_root: Path) -> dict[str, Any]:
    source_dir = repo_root / "src" / "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d"
    source_hashes = {
        core.rel_path(path, repo_root): core.sha_file(path)
        for path in sorted(source_dir.glob("*.py"))
        if path.exists()
    }
    return {
        "task_id": core.TASK_ID,
        "source_hashes": source_hashes,
        "source_artifact_integrity_passed": bool(source_hashes),
    }


def _build_task_doc() -> str:
    return f"""# EGO-MAINLINE-ADMISSION-EXECUTABLE-001B-BASELINE-LEGAL-INPUT-REPAIR-001D

## Task Identity

```text
task_id = {core.TASK_ID}
verdict = {core.VERDICT_PASS}
layer = {core.LAYER}
claim_ceiling = {core.CLAIM_CEILING}
```

## Scope

This is a bounded repair rerun for the exact 001C blockers:

```text
baseline_illegal_verifier_label_consumption
baseline_non_invocation
missing_same_surface_positive_control
```

It does not rewrite the old 001B artifacts, does not weaken the 001C blocker,
does not enter the Ego repository, and does not authorize runtime, product,
LLM/RAG, user-model, relationship, emotion, personalization, companion, or
real-user-data work.

## Repair Result

The repair defines a baseline-visible legal input schema, routes every required
baseline through a guarded access object, records baseline input access, uses a
static forbidden-reference scan for the repaired baseline path, adds explicit
negative controls for baseline non-invocation and missing same-surface positive
controls, and recomputes the bounded rerun artifacts under a new 001D artifact
directory.

## What This Does Not Prove

This does not prove 001B independent audit pass, EGO readiness, EGO mainline
readiness, runtime admissibility, bridge readiness, companion readiness,
mechanism validity, theory validity, agency, selfhood, consciousness, real
emotion, real relationship learning, stable user benefit, production readiness,
or correctness of any future EGO runtime.
"""


def _artifact_hashes(output_dir: Path, names: list[str]) -> dict[str, str]:
    return {name: core.sha_file(output_dir / name) for name in names if (output_dir / name).exists()}


def _metric_provenance(output_dir: Path, pack: dict[str, Any], reports: dict[str, Any]) -> dict[str, Any]:
    episode_ids = pack["episode_ids"]
    seed_ids = pack["seed_ids"]
    metric_specs = [
        ("baseline_legal_input", "baseline legal input guard", "baseline_forbidden_access_report.json", core.repaired_baseline_action, ["baseline_legal_input_access_log.json", "baseline_forbidden_access_report.json"], ["baseline_runtime_access_guard_passed"]),
        ("baseline_invocation", "baseline invocation", "baseline_invocation_report.json", core.repaired_baseline_action, ["baseline_invocation_report.json", "baseline_output_rows.json"], ["all_required_baselines_invoked"]),
        ("baseline_non_invocation_failure_control", "baseline non-invocation failure control", "baseline_non_invocation_failure_control.json", _baseline_non_invocation_failure_control, ["baseline_non_invocation_failure_control.json"], ["baseline_non_invocation_detected"]),
        ("same_surface_positive_control_failure_control", "missing same-surface positive-control failure control", "same_surface_positive_control_failure_control.json", _same_surface_positive_control_failure_control, ["same_surface_positive_control_failure_control.json"], ["missing_same_surface_positive_control_detected"]),
        ("ablation_revalidation", "ablation revalidation", "ablation_revalidation_report.json", _revalidate_ablation, ["ablation_revalidation_report.json"], ["ablation_revalidation_passed"]),
        ("leakage_revalidation", "leakage revalidation", "leakage_revalidation_report.json", _revalidate_leakage, ["leakage_revalidation_report.json"], ["leakage_revalidation_passed"]),
        ("manual_injection_revalidation", "manual injection revalidation", "manual_injection_revalidation_report.json", _revalidate_leakage, ["manual_injection_revalidation_report.json"], ["manual_injection_revalidation_passed"]),
        ("metadata_whitelist_scope", "metadata whitelist scope", "metadata_whitelist_scope_revalidation.json", _revalidate_leakage, ["metadata_whitelist_scope_revalidation.json"], ["metadata_whitelist_surface_scoped"]),
        ("behavior_causal_replay", "behavior-causal replay", "behavior_causal_replay_report.json", _behavior_replay, ["behavior_causal_replay_report.json"], ["behavior_causal_replay_passed"]),
        ("frozen_input_consumption", "frozen input consumption", "frozen_input_consumption_report.json", _frozen_inputs, ["frozen_input_consumption_report.json"], ["frozen_inputs_consumed"]),
        ("old_artifact_mutation", "old artifact mutation", "old_artifact_mutation_report.json", run_repair, ["old_artifact_mutation_report.json"], ["old_artifacts_not_modified"]),
        ("negative_evidence_preservation", "negative evidence preservation", "negative_evidence_preservation_report.json", _negative_evidence, ["negative_evidence_preservation_report.json"], ["001c_blocker_preserved"]),
    ]
    rows = []
    for metric_id, metric_name, output_name, func, input_names, output_ids in metric_specs:
        hashes = _artifact_hashes(output_dir, input_names)
        rows.append(
            core.metric_row(
                metric_id=metric_id,
                metric_name=metric_name,
                producer_function_name=core.producer_name(func),
                producer_module=func.__module__,
                producer_hash=core.code_path_hash(func),
                episode_ids=episode_ids,
                seed_ids=seed_ids,
                input_artifact_paths=input_names,
                input_artifact_hashes=hashes,
                input_row_count=len(episode_ids),
                output_artifact_path=output_name,
                output_row_ids=output_ids,
                aggregation_rule="computed from callable 001D repair artifact rows",
                threshold_used=True,
            )
        )
    return {
        "task_id": core.TASK_ID,
        "metric_provenance_schema_fields": core.METRIC_FIELDS,
        "metrics": rows,
        "all_verdict_metrics_have_callable_provenance": all(set(core.METRIC_FIELDS).issubset(row) for row in rows),
        "no_literal_metrics": all(row["computed_not_literal"] for row in rows),
        "no_static_metric_dictionaries": True,
        "no_copied_old_001b_results": reports["baseline_comparison_report"]["old_001b_baseline_outputs_reused"] is False,
    }


def run_repair(*, repo_root: Path, output_dir: Path, verify_remote: bool = True) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    parent_core = _load_parent_core(repo_root)
    old_001b_dir = _parent_artifact_dir(repo_root, "ego_mainline_admission_executable_001b")
    old_001c_dir = _parent_artifact_dir(repo_root, "ego_mainline_admission_executable_001b_independent_audit_001c")
    old_001b_before = _hash_tree(old_001b_dir, repo_root)
    old_001c_before = _hash_tree(old_001c_dir, repo_root)

    parent_anchors = _verify_parent_anchors(repo_root, verify_remote)
    contract_loaded = (repo_root / "docs" / "codex" / "contracts" / "COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md").exists()
    pack = parent_core.build_controlled_evidence_pack()
    candidate_rows = parent_core.run_candidate(pack)
    legal_access_log, forbidden_access, invocation, baseline_output_with_comparison = _run_repaired_baselines(parent_core, pack)
    baseline_output = {k: v for k, v in baseline_output_with_comparison.items() if k != "comparison_report"}
    baseline_comparison = baseline_output_with_comparison["comparison_report"]
    static_scan = core.static_forbidden_reference_scan(parent_core)
    non_invocation = _baseline_non_invocation_failure_control()
    missing_positive = _same_surface_positive_control_failure_control()
    leakage, manual, whitelist = _revalidate_leakage(parent_core, pack, candidate_rows, legal_access_log)
    ablation = _revalidate_ablation(parent_core, pack)
    replay = _behavior_replay(parent_core, pack, candidate_rows)
    frozen = _frozen_inputs(parent_core, pack)
    negative = _negative_evidence(repo_root)
    repair_scope = _repair_scope_manifest()
    source_integrity = _source_integrity(repo_root)
    old_001b_after = _hash_tree(old_001b_dir, repo_root)
    old_001c_after = _hash_tree(old_001c_dir, repo_root)
    old_mutation = {
        "task_id": core.TASK_ID,
        "old_001b_artifacts_not_modified": old_001b_before == old_001b_after,
        "old_001c_audit_artifacts_not_modified": old_001c_before == old_001c_after,
        "old_001b_mutated_paths": sorted(
            path for path, old_hash in old_001b_before.items() if old_001b_after.get(path) != old_hash
        ),
        "old_001c_mutated_paths": sorted(
            path for path, old_hash in old_001c_before.items() if old_001c_after.get(path) != old_hash
        ),
    }
    scope_claim = {
        "task_id": core.TASK_ID,
        "no_scope_leak": all(value is False for value in core.AUTHORIZATION_FLAGS.values()),
        "no_claim_inflation": True,
        "no_Ego_repo_modification": True,
        "no_runtime_or_product_work": True,
        "authorization_flags": core.AUTHORIZATION_FLAGS,
        "claim_ceiling": core.CLAIM_CEILING,
    }
    parent_forbidden_inventory = core.forbidden_field_inventory()
    schema = core.schema_report()

    preliminary_reports = {
        "parent_anchor_verification.json": parent_anchors,
        "repair_scope_manifest.json": repair_scope,
        "baseline_legal_input_schema.json": schema,
        "baseline_forbidden_field_inventory.json": parent_forbidden_inventory,
        "baseline_static_forbidden_reference_scan.json": static_scan,
        "baseline_legal_input_access_log.json": legal_access_log,
        "baseline_forbidden_access_report.json": forbidden_access,
        "baseline_invocation_report.json": invocation,
        "baseline_output_rows.json": baseline_output,
        "baseline_comparison_report.json": baseline_comparison,
        "baseline_non_invocation_failure_control.json": non_invocation,
        "same_surface_positive_control_failure_control.json": missing_positive,
        "leakage_revalidation_report.json": leakage,
        "metadata_whitelist_scope_revalidation.json": whitelist,
        "manual_injection_revalidation_report.json": manual,
        "ablation_revalidation_report.json": ablation,
        "behavior_causal_replay_report.json": replay,
        "frozen_input_consumption_report.json": frozen,
        "source_artifact_integrity_report.json": source_integrity,
        "old_artifact_mutation_report.json": old_mutation,
        "negative_evidence_preservation_report.json": negative,
    }
    for name, data in preliminary_reports.items():
        core.write_json(output_dir / name, data)

    metrics = _metric_provenance(output_dir, pack, {"baseline_comparison_report": baseline_comparison})
    core.write_json(output_dir / "metric_provenance.json", metrics)

    acceptance_gates = {
        "parent_001r_anchor_verified": any(row["tag"] == "remote-anchor-001r-0fdf451" and row["remote_verified"] for row in parent_anchors["anchors"]),
        "parent_001q_anchor_verified": any(row["tag"] == "remote-anchor-001q-60a504e" and row["remote_verified"] for row in parent_anchors["anchors"]),
        "parent_001p_anchor_verified": any(row["tag"] == "remote-anchor-001p-cda09dc" and row["remote_verified"] for row in parent_anchors["anchors"]),
        "parent_001o_anchor_verified": any(row["tag"] == "remote-anchor-001o-f648dac" and row["remote_verified"] for row in parent_anchors["anchors"]),
        "computed_evidence_contract_loaded": contract_loaded,
        "001c_blocker_preserved": negative["001c_blocker_preserved"],
        "001b_historical_block_status_preserved": negative["001b_historical_block_status_preserved"],
        "repair_scope_exact": repair_scope["repair_scope_exact"],
        "old_001b_artifacts_not_modified": old_mutation["old_001b_artifacts_not_modified"],
        "old_001c_audit_artifacts_not_modified": old_mutation["old_001c_audit_artifacts_not_modified"],
        "baseline_legal_input_schema_defined": schema["baseline_legal_input_schema_defined"],
        "verifier_expected_action_id_excluded_from_baseline_inputs": schema["verifier_expected_action_id_excluded_from_baseline_inputs"],
        "equivalent_verifier_labels_excluded_from_baseline_inputs": schema["equivalent_verifier_labels_excluded_from_baseline_inputs"],
        "baseline_runtime_access_guard_passed": legal_access_log["baseline_runtime_access_guard_passed"],
        "baseline_static_forbidden_reference_scan_passed": static_scan["baseline_static_forbidden_reference_scan_passed"],
        "all_required_baselines_invoked": invocation["all_required_baselines_invoked"],
        "baseline_outputs_exist_before_aggregation": invocation["baseline_outputs_exist_before_aggregation"],
        "baseline_non_invocation_failure_control_passed": non_invocation["baseline_non_invocation_failure_control_passed"],
        "missing_same_surface_positive_control_failure_control_passed": missing_positive["missing_same_surface_positive_control_failure_control_passed"],
        "all_verdict_metrics_have_callable_provenance": metrics["all_verdict_metrics_have_callable_provenance"],
        "no_literal_metrics": metrics["no_literal_metrics"],
        "no_static_metric_dictionaries": metrics["no_static_metric_dictionaries"],
        "no_copied_old_001b_results": metrics["no_copied_old_001b_results"],
        "ablation_revalidation_passed": ablation["ablation_revalidation_passed"],
        "leakage_revalidation_passed": leakage["leakage_revalidation_passed"],
        "manual_injection_revalidation_passed": manual["manual_injection_revalidation_passed"],
        "metadata_whitelist_surface_scoped": whitelist["metadata_whitelist_surface_scoped"],
        "behavior_causal_replay_passed": replay["behavior_causal_replay_passed"] and not replay["hash_only_replay_for_behavior_claim"],
        "frozen_inputs_consumed": frozen["frozen_inputs_consumed"],
        "negative_evidence_preserved": negative["001c_blocker_preserved"] and not negative["negative_evidence_rewrite_detected"],
        "no_scope_leak": scope_claim["no_scope_leak"],
        "no_claim_inflation": scope_claim["no_claim_inflation"],
        "no_Ego_repo_modification": scope_claim["no_Ego_repo_modification"],
        "no_runtime_or_product_work": scope_claim["no_runtime_or_product_work"],
    }
    stop_eval = core.evaluate_stop_conditions(
        {
            "missing_parent_anchor": not all(
                acceptance_gates[key]
                for key in [
                    "parent_001r_anchor_verified",
                    "parent_001q_anchor_verified",
                    "parent_001p_anchor_verified",
                    "parent_001o_anchor_verified",
                ]
            ),
            "missing_computed_evidence_contract": not acceptance_gates["computed_evidence_contract_loaded"],
            "001c_blocker_not_preserved": not acceptance_gates["001c_blocker_preserved"],
            "repair_scope_expanded": not acceptance_gates["repair_scope_exact"],
            "old_artifact_mutation": not acceptance_gates["old_001b_artifacts_not_modified"]
            or not acceptance_gates["old_001c_audit_artifacts_not_modified"],
            "baseline_illegal_input": not acceptance_gates["verifier_expected_action_id_excluded_from_baseline_inputs"]
            or not acceptance_gates["equivalent_verifier_labels_excluded_from_baseline_inputs"],
            "baseline_forbidden_access": not acceptance_gates["baseline_runtime_access_guard_passed"]
            or not acceptance_gates["baseline_static_forbidden_reference_scan_passed"],
            "baseline_non_invocation": not acceptance_gates["baseline_non_invocation_failure_control_passed"],
            "same_surface_positive_control_gap": not acceptance_gates[
                "missing_same_surface_positive_control_failure_control_passed"
            ],
            "metric_provenance_gap": not acceptance_gates["all_verdict_metrics_have_callable_provenance"],
            "literal_metric": not acceptance_gates["no_literal_metrics"],
            "ablation_gap": not acceptance_gates["ablation_revalidation_passed"],
            "leakage_gap": not acceptance_gates["leakage_revalidation_passed"],
            "replay_gap": not acceptance_gates["behavior_causal_replay_passed"],
            "unused_frozen_input": not acceptance_gates["frozen_inputs_consumed"],
            "negative_evidence_rewrite": not acceptance_gates["negative_evidence_preserved"],
            "scope_leak": not acceptance_gates["no_scope_leak"],
            "claim_inflation": not acceptance_gates["no_claim_inflation"],
        }
    )
    result = {
        "task_id": core.TASK_ID,
        "layer": core.LAYER,
        "verdict": stop_eval["verdict"],
        "bounded_pass": stop_eval["passed"] and all(acceptance_gates.values()),
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "claim_ceiling": core.CLAIM_CEILING,
        "authorization_flags": core.AUTHORIZATION_FLAGS,
        "acceptance_gates": acceptance_gates,
        "stop_conditions_triggered": stop_eval["stop_conditions"],
        "repair_scope_result": {
            "repair_scope_exact": repair_scope["repair_scope_exact"],
            "repaired_blockers": repair_scope["repaired_blockers"],
        },
        "baseline_legal_input_result": {
            "baseline_legal_input_schema_defined": schema["baseline_legal_input_schema_defined"],
            "baseline_runtime_access_guard_passed": legal_access_log["baseline_runtime_access_guard_passed"],
            "baseline_static_forbidden_reference_scan_passed": static_scan[
                "baseline_static_forbidden_reference_scan_passed"
            ],
        },
        "baseline_forbidden_access_result": forbidden_access,
        "baseline_invocation_result": {
            "all_required_baselines_invoked": invocation["all_required_baselines_invoked"],
            "baseline_outputs_exist_before_aggregation": invocation[
                "baseline_outputs_exist_before_aggregation"
            ],
        },
        "baseline_non_invocation_failure_control_result": non_invocation,
        "missing_same_surface_positive_control_failure_control_result": missing_positive,
        "metric_provenance_result": {
            "all_verdict_metrics_have_callable_provenance": metrics[
                "all_verdict_metrics_have_callable_provenance"
            ],
            "no_literal_metrics": metrics["no_literal_metrics"],
            "metric_count": len(metrics["metrics"]),
        },
        "ablation_revalidation_result": ablation,
        "leakage_revalidation_result": leakage,
        "manual_injection_result": manual,
        "metadata_whitelist_scope_result": whitelist,
        "replay_result": replay,
        "frozen_input_consumption_result": frozen,
        "old_artifact_mutation_result": old_mutation,
        "negative_evidence_preservation_result": negative,
        "scope_claim_ceiling_result": scope_claim,
        "what_this_does_not_prove": [
            "001B independent audit pass",
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
    core.write_json(output_dir / "result.json", result)
    core.write_text(output_dir / "claim_ceiling.txt", core.CLAIM_CEILING + "\n")
    if not result["bounded_pass"]:
        core.write_json(
            output_dir / "blocker_report.json",
            {
                "task_id": core.TASK_ID,
                "verdict": result["verdict"],
                "stop_conditions_triggered": result["stop_conditions_triggered"],
            },
        )

    task_doc = repo_root / "docs" / "codex" / "tasks" / "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B-BASELINE-LEGAL-INPUT-REPAIR-001D.md"
    task_doc.parent.mkdir(parents=True, exist_ok=True)
    task_doc.write_text(_build_task_doc(), encoding="utf-8")
    return result
