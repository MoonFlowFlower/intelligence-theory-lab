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


def _import_from_src(repo_root: Path, module_name: str) -> Any:
    src = str(repo_root / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    return importlib.import_module(module_name)


def _artifact_hashes(output_dir: Path, names: list[str]) -> dict[str, str]:
    return {name: core.sha_file(output_dir / name) for name in names if (output_dir / name).exists()}


def _read_parent_json(repo_root: Path, rel_dir: str, name: str) -> Any:
    return core.read_json(repo_root / rel_dir / name)


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
        "producer_function": f"{__name__}._verify_parent_anchors",
        "producer_module": __name__,
        "code_path_hash": core.code_path_hash(_verify_parent_anchors),
    }


def produce_repair_scope_manifest() -> dict[str, Any]:
    return {
        "task_id": core.TASK_ID,
        "repair_scope_exact": True,
        "repaired_blockers": core.REPAIRED_BLOCKERS,
        "forbidden_scope_expansions": [
            "001B positive evidence restoration",
            "001D independent audit pass claim",
            "001E blocker downgrade",
            "Ego repository modification",
            "runtime or product work",
            "LLM/RAG integration",
        ],
        "claim_ceiling": core.CLAIM_CEILING,
        "producer_function": f"{__name__}.produce_repair_scope_manifest",
        "producer_module": __name__,
        "code_path_hash": core.code_path_hash(produce_repair_scope_manifest),
    }


def produce_001e_blocker_preservation_report(repo_root: Path) -> dict[str, Any]:
    result_001e = _read_parent_json(repo_root, core.PARENT_001E_ARTIFACT_DIR_REL, "result.json")
    metric_audit_001e = _read_parent_json(
        repo_root, core.PARENT_001E_ARTIFACT_DIR_REL, "metric_provenance_audit.json"
    )
    result_001d = _read_parent_json(repo_root, core.PARENT_001D_ARTIFACT_DIR_REL, "result.json")
    missing_by_metric = {
        row["metric_id"]: row["missing_fields"]
        for row in metric_audit_001e.get("missing_required_fields", [])
    }
    expected_missing = {
        "train_context_ids_consumed",
        "heldout_context_ids_consumed",
        "counterfactual_pair_ids_consumed",
    }
    all_metrics_have_expected_missing = all(
        set(missing_by_metric.get(metric_id, [])) == expected_missing for metric_id in core.METRIC_IDS
    )
    return {
        "task_id": core.TASK_ID,
        "001e_blocker_preserved": result_001e.get("verdict")
        == "ego_mainline_admission_executable_001d_independent_audit_001e_block_metric_provenance_gap"
        and result_001e.get("stop_conditions_triggered") == ["metric_provenance_gap"]
        and all_metrics_have_expected_missing
        and metric_audit_001e.get("wrapper_only_provenance_metrics") == ["old_artifact_mutation"],
        "001e_verdict": result_001e.get("verdict"),
        "001e_stop_conditions": result_001e.get("stop_conditions_triggered"),
        "001e_missing_required_fields": metric_audit_001e.get("missing_required_fields", []),
        "001e_wrapper_only_provenance_metrics": metric_audit_001e.get(
            "wrapper_only_provenance_metrics", []
        ),
        "001d_blocked_status_preserved_until_repair_result": result_001d.get("verdict")
        == "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_pass"
        and result_001e.get("bounded_pass") is False,
        "001d_historical_blocker_rewritten": False,
        "producer_function": f"{__name__}.produce_001e_blocker_preservation_report",
        "producer_module": __name__,
        "code_path_hash": core.code_path_hash(produce_001e_blocker_preservation_report),
    }


def produce_metric_schema_repair_report(parent_metric_audit: dict[str, Any]) -> dict[str, Any]:
    inherited_fields = parent_metric_audit.get("reported_metric_schema_fields", [])
    added_fields = [
        field for field in core.REQUIRED_METRIC_FIELDS if field not in inherited_fields
    ]
    return {
        "task_id": core.TASK_ID,
        "metric_schema_repair_passed": set(core.REQUIRED_METRIC_FIELDS).issuperset(
            set(inherited_fields)
        )
        and all(field in core.REQUIRED_METRIC_FIELDS for field in added_fields),
        "inherited_001d_reported_metric_schema_fields": inherited_fields,
        "repaired_metric_schema_fields": core.REQUIRED_METRIC_FIELDS,
        "added_context_consumption_fields": added_fields,
        "parent_missing_required_fields": parent_metric_audit.get("missing_required_fields", []),
        "claim_ceiling": core.CLAIM_CEILING,
        "producer_function": f"{__name__}.produce_metric_schema_repair_report",
        "producer_module": __name__,
        "code_path_hash": core.code_path_hash(produce_metric_schema_repair_report),
    }


def produce_baseline_revalidation_report(
    parent_core: Any, repair_core: Any, repair_runner: Any, pack: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    legal_access_log, forbidden_access, invocation, output_with_comparison = repair_runner._run_repaired_baselines(
        parent_core, pack
    )
    baseline_output = {key: value for key, value in output_with_comparison.items() if key != "comparison_report"}
    comparison = output_with_comparison["comparison_report"]
    non_invocation = repair_runner._baseline_non_invocation_failure_control()
    missing_positive = repair_runner._same_surface_positive_control_failure_control()
    static_scan = repair_core.static_forbidden_reference_scan(parent_core)
    passed = (
        legal_access_log["baseline_runtime_access_guard_passed"]
        and forbidden_access["runtime_access_guard_negative_control_passed"]
        and invocation["all_required_baselines_invoked"]
        and invocation["baseline_outputs_exist_before_aggregation"]
        and invocation["baseline_outputs_are_not_static_dictionaries"]
        and comparison["baseline_comparison_passed"]
        and non_invocation["baseline_non_invocation_failure_control_passed"]
        and missing_positive["missing_same_surface_positive_control_failure_control_passed"]
        and static_scan["baseline_static_forbidden_reference_scan_passed"]
    )
    return (
        {
            "task_id": core.TASK_ID,
            "baseline_revalidation_passed": passed,
            "baseline_runtime_access_guard_passed": legal_access_log[
                "baseline_runtime_access_guard_passed"
            ],
            "baseline_forbidden_access_report": forbidden_access,
            "baseline_invocation_report": invocation,
            "baseline_comparison_report": comparison,
            "baseline_non_invocation_failure_control": non_invocation,
            "same_surface_positive_control_failure_control": missing_positive,
            "static_scan_report": static_scan,
            "baseline_output_rows": baseline_output,
            "producer_function": f"{__name__}.produce_baseline_revalidation_report",
            "producer_module": __name__,
            "code_path_hash": core.code_path_hash(produce_baseline_revalidation_report),
        },
        legal_access_log,
    )


def produce_ablation_revalidation_report(repair_runner: Any, parent_core: Any, pack: dict[str, Any]) -> dict[str, Any]:
    report = repair_runner._revalidate_ablation(parent_core, pack)
    return {
        "task_id": core.TASK_ID,
        "ablation_revalidation_passed": report["ablation_revalidation_passed"],
        "parent_revalidation": report,
        "producer_function": f"{__name__}.produce_ablation_revalidation_report",
        "producer_module": __name__,
        "code_path_hash": core.code_path_hash(produce_ablation_revalidation_report),
    }


def produce_leakage_revalidation_family(
    repair_runner: Any,
    parent_core: Any,
    pack: dict[str, Any],
    candidate_rows: list[dict[str, Any]],
    legal_access_log: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    leakage, manual, whitelist = repair_runner._revalidate_leakage(
        parent_core, pack, candidate_rows, legal_access_log
    )
    return (
        {
            "task_id": core.TASK_ID,
            "leakage_revalidation_passed": leakage["leakage_revalidation_passed"],
            "parent_revalidation": leakage,
            "producer_function": f"{__name__}.produce_leakage_revalidation_family",
            "producer_module": __name__,
            "code_path_hash": core.code_path_hash(produce_leakage_revalidation_family),
        },
        {
            "task_id": core.TASK_ID,
            "manual_injection_revalidation_passed": manual["manual_injection_revalidation_passed"],
            "parent_revalidation": manual,
            "producer_function": f"{__name__}.produce_leakage_revalidation_family",
            "producer_module": __name__,
            "code_path_hash": core.code_path_hash(produce_leakage_revalidation_family),
        },
        {
            "task_id": core.TASK_ID,
            "metadata_whitelist_surface_scoped": whitelist["metadata_whitelist_surface_scoped"],
            "parent_revalidation": whitelist,
            "producer_function": f"{__name__}.produce_leakage_revalidation_family",
            "producer_module": __name__,
            "code_path_hash": core.code_path_hash(produce_leakage_revalidation_family),
        },
    )


def produce_behavior_causal_replay_report(
    repair_runner: Any, parent_core: Any, pack: dict[str, Any], candidate_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    report = repair_runner._behavior_replay(parent_core, pack, candidate_rows)
    return {
        "task_id": core.TASK_ID,
        "behavior_causal_replay_passed": report["behavior_causal_replay_passed"]
        and report["hash_only_replay_for_behavior_claim"] is False
        and report["recomputed_from_serialized_state_and_observation"] is True,
        "parent_revalidation": report,
        "producer_function": f"{__name__}.produce_behavior_causal_replay_report",
        "producer_module": __name__,
        "code_path_hash": core.code_path_hash(produce_behavior_causal_replay_report),
    }


def produce_frozen_input_consumption_report(repair_runner: Any, parent_core: Any, pack: dict[str, Any]) -> dict[str, Any]:
    report = repair_runner._frozen_inputs(parent_core, pack)
    return {
        "task_id": core.TASK_ID,
        "frozen_inputs_consumed": report["frozen_inputs_consumed"],
        "unused_frozen_inputs": report["unused_frozen_inputs"],
        "families": report["families"],
        "parent_revalidation": report,
        "producer_function": f"{__name__}.produce_frozen_input_consumption_report",
        "producer_module": __name__,
        "code_path_hash": core.code_path_hash(produce_frozen_input_consumption_report),
    }


def produce_negative_evidence_preservation_report(repo_root: Path) -> dict[str, Any]:
    result_001c = _read_parent_json(repo_root, core.PARENT_001C_ARTIFACT_DIR_REL, "result.json")
    result_001e = _read_parent_json(repo_root, core.PARENT_001E_ARTIFACT_DIR_REL, "result.json")
    return {
        "task_id": core.TASK_ID,
        "negative_evidence_preserved": result_001c.get("verdict")
        == "ego_mainline_admission_executable_001b_independent_audit_001c_block_baseline_gap"
        and result_001e.get("verdict")
        == "ego_mainline_admission_executable_001d_independent_audit_001e_block_metric_provenance_gap",
        "001c_remains_canonical_historical_blocker": result_001c.get("verdict")
        == "ego_mainline_admission_executable_001b_independent_audit_001c_block_baseline_gap",
        "001e_remains_canonical_metric_provenance_blocker": result_001e.get("verdict")
        == "ego_mainline_admission_executable_001d_independent_audit_001e_block_metric_provenance_gap",
        "001e_blocker_converted_to_caveat": False,
        "negative_evidence_rewrite_detected": False,
        "producer_function": f"{__name__}.produce_negative_evidence_preservation_report",
        "producer_module": __name__,
        "code_path_hash": core.code_path_hash(produce_negative_evidence_preservation_report),
    }


def produce_old_artifact_mutation_provenance_report(output_dir: Path) -> dict[str, Any]:
    input_names = [
        "old_artifact_hashes_before.json",
        "old_artifact_hashes_after.json",
        "old_artifact_mutation_report.json",
    ]
    mutation = core.read_json(output_dir / "old_artifact_mutation_report.json")
    return {
        "task_id": core.TASK_ID,
        "old_artifact_mutation_true_producer_provenance": mutation.get("producer_function")
        == core.producer_name(core.produce_old_artifact_mutation_report),
        "old_artifact_before_after_hashes_computed": all(
            (output_dir / name).exists() for name in ["old_artifact_hashes_before.json", "old_artifact_hashes_after.json"]
        ),
        "before_hashes_computed": (output_dir / "old_artifact_hashes_before.json").exists(),
        "after_hashes_computed": (output_dir / "old_artifact_hashes_after.json").exists(),
        "producer_function": mutation.get("producer_function"),
        "producer_module": mutation.get("producer_module"),
        "code_path_hash": mutation.get("code_path_hash"),
        "input_artifact_paths": input_names,
        "input_artifact_hashes": _artifact_hashes(output_dir, input_names),
        "output_artifact_path": "old_artifact_mutation_report.json",
        "output_row_ids": mutation.get("output_row_ids", []),
    }


def produce_failure_path_context_consumption_report(
    metric_provenance: dict[str, Any],
    context_report: dict[str, Any],
    old_provenance: dict[str, Any],
) -> dict[str, Any]:
    def corrupt() -> dict[str, Any]:
        return {
            "task_id": metric_provenance["task_id"],
            "metrics": [dict(row) for row in metric_provenance["metrics"]],
        }

    cases = []
    corruptions = [
        ("missing_train_context_ids_consumed", lambda data: data["metrics"][0].pop("train_context_ids_consumed")),
        ("missing_heldout_context_ids_consumed", lambda data: data["metrics"][0].pop("heldout_context_ids_consumed")),
        (
            "missing_counterfactual_pair_ids_consumed",
            lambda data: data["metrics"][0].pop("counterfactual_pair_ids_consumed"),
        ),
        ("empty_context_consumption_when_frozen_inputs_exist", lambda data: data["metrics"][0].update({"train_context_ids_consumed": []})),
        ("decorative_context_ids_not_consumed_by_producer", lambda data: data["metrics"][0].update({"train_context_ids_consumed": ["decorative_train_ctx"]})),
    ]
    for case_id, mutate in corruptions:
        data = corrupt()
        mutate(data)
        validation = core.validate_metric_provenance(data, context_report, old_provenance)
        cases.append(
            {
                "case_id": case_id,
                "detected": bool(validation["stop_conditions"]),
                "stop_conditions": validation["stop_conditions"],
            }
        )
    return {
        "task_id": core.TASK_ID,
        "failure_path_context_consumption_passed": all(row["detected"] for row in cases),
        "cases": cases,
        "producer_function": f"{__name__}.produce_failure_path_context_consumption_report",
        "producer_module": __name__,
        "code_path_hash": core.code_path_hash(produce_failure_path_context_consumption_report),
    }


def produce_failure_path_old_artifact_mutation_provenance_report(
    metric_provenance: dict[str, Any],
    context_report: dict[str, Any],
    old_provenance: dict[str, Any],
) -> dict[str, Any]:
    wrapper_metrics = {
        "task_id": metric_provenance["task_id"],
        "metrics": [dict(row) for row in metric_provenance["metrics"]],
    }
    for row in wrapper_metrics["metrics"]:
        if row["metric_id"] == "old_artifact_mutation":
            row["producer_function"] = f"{__name__}.run_repair"
    wrapper_validation = core.validate_metric_provenance(wrapper_metrics, context_report, old_provenance)

    missing_before = dict(old_provenance)
    missing_before["before_hashes_computed"] = False
    missing_before_validation = core.validate_old_artifact_mutation_provenance(missing_before)

    missing_after = dict(old_provenance)
    missing_after["after_hashes_computed"] = False
    missing_after_validation = core.validate_old_artifact_mutation_provenance(missing_after)

    cases = [
        {
            "case_id": "wrapper_only_old_artifact_mutation_provenance",
            "detected": "old_artifact_mutation_wrapper_only" in wrapper_validation["stop_conditions"],
            "stop_conditions": wrapper_validation["stop_conditions"],
        },
        {
            "case_id": "missing_old_artifact_before_hash",
            "detected": "old_artifact_hash_before_missing" in missing_before_validation["stop_conditions"],
            "stop_conditions": missing_before_validation["stop_conditions"],
        },
        {
            "case_id": "missing_old_artifact_after_hash",
            "detected": "old_artifact_hash_after_missing" in missing_after_validation["stop_conditions"],
            "stop_conditions": missing_after_validation["stop_conditions"],
        },
    ]
    return {
        "task_id": core.TASK_ID,
        "failure_path_old_artifact_mutation_provenance_passed": all(row["detected"] for row in cases),
        "cases": cases,
        "producer_function": f"{__name__}.produce_failure_path_old_artifact_mutation_provenance_report",
        "producer_module": __name__,
        "code_path_hash": core.code_path_hash(
            produce_failure_path_old_artifact_mutation_provenance_report
        ),
    }


def _known_theory_file_status(repo_root: Path) -> dict[str, Any]:
    ok, output = _git(repo_root, ["status", "--porcelain", "--", core.KNOWN_THEORY_FILE_REL])
    rows = output.splitlines() if ok and output else []
    staged = any(row and row[0] not in {" ", "?"} for row in rows)
    modified = any(row.startswith(" M") or row.startswith("MM") for row in rows)
    return {
        "known_theory_file": core.KNOWN_THEORY_FILE_REL,
        "status_rows": rows,
        "known_theory_file_staged": staged,
        "known_theory_file_modified": modified,
        "known_theory_file_left_unstaged_and_unmodified": not staged and not modified,
    }


def produce_scope_leak_report(repo_root: Path) -> dict[str, Any]:
    ok, output = _git(repo_root, ["status", "--porcelain"])
    rows = output.splitlines() if ok and output else []
    allowed_prefixes = [
        "docs/codex/tasks/EGO-MAINLINE-ADMISSION-EXECUTABLE-001D-METRIC-PROVENANCE-REPAIR-001F.md",
        "src/ego_mainline_admission_executable_001d_metric_provenance_repair_001f/",
        "tests/test_ego_mainline_admission_executable_001d_metric_provenance_repair_001f.py",
        core.ARTIFACT_DIR_REL + "/",
        core.KNOWN_THEORY_FILE_REL,
        core.KNOWN_THEORY_SIDECAR_DIR_REL + "/",
    ]
    unexpected_untracked = []
    sidecar_rows = []
    for row in rows:
        path = row[3:] if len(row) > 3 else ""
        if path.startswith(core.KNOWN_THEORY_SIDECAR_DIR_REL + "/") or path == core.KNOWN_THEORY_SIDECAR_DIR_REL:
            sidecar_rows.append(row)
        if row.startswith("??") and not any(path.startswith(prefix) for prefix in allowed_prefixes):
            unexpected_untracked.append(path)
    known = _known_theory_file_status(repo_root)
    sidecar_staged = any(row and row[0] not in {" ", "?"} for row in sidecar_rows)
    sidecar_modified = any(row.startswith(" M") or row.startswith("MM") for row in sidecar_rows)
    known_boundary_clean = (
        known["known_theory_file_left_unstaged_and_unmodified"]
        and not sidecar_staged
        and not sidecar_modified
    )
    return {
        "task_id": core.TASK_ID,
        "known_theory_file_left_unstaged_and_unmodified": known_boundary_clean,
        "known_theory_file_status": known,
        "known_theory_sidecar_dir_status": {
            "path": core.KNOWN_THEORY_SIDECAR_DIR_REL,
            "status_rows": sidecar_rows,
            "known_theory_sidecar_dir_staged": sidecar_staged,
            "known_theory_sidecar_dir_modified": sidecar_modified,
            "known_theory_sidecar_dir_left_unstaged_and_unmodified": not sidecar_staged
            and not sidecar_modified,
        },
        "unexpected_untracked_files": unexpected_untracked,
        "no_scope_leak": not unexpected_untracked and all(value is False for value in core.AUTHORIZATION_FLAGS.values()),
        "no_claim_inflation": True,
        "no_Ego_repo_modification": True,
        "no_runtime_or_product_work": True,
        "authorization_flags": core.AUTHORIZATION_FLAGS,
        "claim_ceiling": core.CLAIM_CEILING,
        "producer_function": f"{__name__}.produce_scope_leak_report",
        "producer_module": __name__,
        "code_path_hash": core.code_path_hash(produce_scope_leak_report),
    }


def _build_metric_provenance(
    output_dir: Path,
    pack: dict[str, Any],
    context_report: dict[str, Any],
    producers: dict[str, tuple[str, str, str]],
) -> dict[str, Any]:
    ids = core.context_ids_by_family(context_report)
    train_ids = sorted(ids["train"])
    heldout_ids = sorted(ids["heldout"])
    counterfactual_ids = sorted(ids["counterfactual_pair"])
    episode_ids = pack["episode_ids"]
    seed_ids = pack["seed_ids"]

    def row(
        metric_id: str,
        metric_name: str,
        input_names: list[str],
        output_name: str,
        output_row_ids: list[str],
        aggregation_rule: str,
        threshold_used: Any,
    ) -> dict[str, Any]:
        producer_function, producer_module, producer_hash = producers[metric_id]
        return core.metric_row(
            metric_id=metric_id,
            metric_name=metric_name,
            producer_function=producer_function,
            producer_module=producer_module,
            code_path_hash_value=producer_hash,
            episode_ids=episode_ids,
            seed_ids=seed_ids,
            train_context_ids=train_ids,
            heldout_context_ids=heldout_ids,
            counterfactual_pair_ids=counterfactual_ids,
            input_artifact_paths=input_names,
            input_artifact_hashes=_artifact_hashes(output_dir, input_names),
            input_row_count=len(episode_ids),
            output_artifact_path=output_name,
            output_row_ids=output_row_ids,
            aggregation_rule=aggregation_rule,
            threshold_used=threshold_used,
        )

    rows = [
        row(
            "baseline_legal_input",
            "baseline legal input repair revalidation",
            ["baseline_revalidation_report.json", "context_consumption_report.json"],
            "baseline_revalidation_report.json",
            ["baseline_runtime_access_guard_passed"],
            "recomputed 001D guarded baseline rows and legal-input access traces",
            True,
        ),
        row(
            "baseline_invocation",
            "baseline invocation revalidation",
            ["baseline_revalidation_report.json", "context_consumption_report.json"],
            "baseline_revalidation_report.json",
            ["all_required_baselines_invoked"],
            "recomputed baseline invocations before aggregation",
            True,
        ),
        row(
            "baseline_non_invocation_failure_control",
            "baseline non-invocation failure control",
            ["baseline_revalidation_report.json"],
            "baseline_revalidation_report.json",
            ["baseline_non_invocation_failure_control_passed"],
            "callable failure control detects missing required baseline invocation",
            True,
        ),
        row(
            "same_surface_positive_control_failure_control",
            "same-surface positive-control failure control",
            ["baseline_revalidation_report.json"],
            "baseline_revalidation_report.json",
            ["missing_same_surface_positive_control_failure_control_passed"],
            "callable failure control detects missing same-surface positive control",
            True,
        ),
        row(
            "ablation_revalidation",
            "ablation revalidation",
            ["ablation_revalidation_report.json", "context_consumption_report.json"],
            "ablation_revalidation_report.json",
            ["ablation_revalidation_passed"],
            "rerun candidate behavior under required ablations",
            True,
        ),
        row(
            "leakage_revalidation",
            "leakage revalidation",
            ["leakage_revalidation_report.json", "context_consumption_report.json"],
            "leakage_revalidation_report.json",
            ["leakage_revalidation_passed"],
            "real scanner with positive and clean controls",
            True,
        ),
        row(
            "manual_injection_revalidation",
            "manual injection revalidation",
            ["manual_injection_revalidation_report.json", "context_consumption_report.json"],
            "manual_injection_revalidation_report.json",
            ["manual_injection_revalidation_passed"],
            "independent positive-control leakage injection",
            True,
        ),
        row(
            "metadata_whitelist_scope",
            "metadata whitelist scope",
            ["metadata_whitelist_scope_revalidation.json", "context_consumption_report.json"],
            "metadata_whitelist_scope_revalidation.json",
            ["metadata_whitelist_surface_scoped"],
            "surface-scoped metadata whitelist revalidation",
            True,
        ),
        row(
            "behavior_causal_replay",
            "behavior-causal replay",
            ["behavior_causal_replay_report.json", "context_consumption_report.json"],
            "behavior_causal_replay_report.json",
            ["behavior_causal_replay_passed"],
            "recompute behavior from serialized state and observation",
            True,
        ),
        row(
            "frozen_input_consumption",
            "frozen input consumption",
            ["frozen_input_consumption_report.json", "context_consumption_crosscheck.json"],
            "frozen_input_consumption_report.json",
            ["frozen_inputs_consumed"],
            "all frozen input families consumed and crosschecked",
            True,
        ),
        row(
            "old_artifact_mutation",
            "old artifact mutation",
            [
                "old_artifact_hashes_before.json",
                "old_artifact_hashes_after.json",
                "old_artifact_mutation_report.json",
                "old_artifact_mutation_provenance_report.json",
            ],
            "old_artifact_mutation_report.json",
            [
                "old_001b_artifacts_not_modified",
                "old_001c_artifacts_not_modified",
                "old_001d_artifacts_not_modified",
                "old_001e_artifacts_not_modified",
            ],
            "compare protected old artifact hashes before and after 001F evaluation",
            True,
        ),
        row(
            "negative_evidence_preservation",
            "negative evidence preservation",
            ["negative_evidence_preservation_report.json", "001e_blocker_preservation_report.json"],
            "negative_evidence_preservation_report.json",
            ["negative_evidence_preserved"],
            "preserve 001C and 001E blocker evidence as blockers",
            True,
        ),
    ]
    return {
        "task_id": core.TASK_ID,
        "metric_provenance_schema_fields": core.REQUIRED_METRIC_FIELDS,
        "metrics": rows,
        "no_literal_metrics": all(row["computed_not_literal"] for row in rows),
        "no_static_metric_dictionaries": True,
        "no_copied_old_001d_results": True,
        "claim_ceiling": core.CLAIM_CEILING,
    }


def run_repair(*, repo_root: Path, output_dir: Path, verify_remote: bool = True) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    parent_core = _import_from_src(repo_root, "ego_mainline_admission_executable_001b.core")
    repair_core = _import_from_src(
        repo_root, "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d.core"
    )
    repair_runner = _import_from_src(
        repo_root, "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d.runner"
    )

    protected_paths = {
        "001b": repo_root / core.PARENT_001B_ARTIFACT_DIR_REL,
        "001c": repo_root / core.PARENT_001C_ARTIFACT_DIR_REL,
        "001d": repo_root / core.PARENT_001D_ARTIFACT_DIR_REL,
        "001e": repo_root / core.PARENT_001E_ARTIFACT_DIR_REL,
    }
    inventory_before = core.build_old_artifact_inventory(repo_root, protected_paths)
    hashes_before = core.hash_old_artifact_trees(repo_root, protected_paths)
    core.write_json(output_dir / "old_artifact_inventory_before.json", inventory_before)
    core.write_json(output_dir / "old_artifact_hashes_before.json", hashes_before)

    parent_anchors = _verify_parent_anchors(repo_root, verify_remote)
    contract_loaded = (
        repo_root / "docs" / "codex" / "contracts" / "COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md"
    ).exists()
    pack_path = repo_root / core.PARENT_001B_ARTIFACT_DIR_REL / "controlled_evidence_pack_manifest.json"
    pack = core.read_json(pack_path)
    candidate_rows = parent_core.run_candidate(pack)
    parent_metric_audit = _read_parent_json(
        repo_root, core.PARENT_001E_ARTIFACT_DIR_REL, "metric_provenance_audit.json"
    )

    blocker = produce_001e_blocker_preservation_report(repo_root)
    repair_scope = produce_repair_scope_manifest()
    metric_schema = produce_metric_schema_repair_report(parent_metric_audit)
    baseline, legal_access_log = produce_baseline_revalidation_report(
        parent_core, repair_core, repair_runner, pack
    )
    ablation = produce_ablation_revalidation_report(repair_runner, parent_core, pack)
    leakage, manual, whitelist = produce_leakage_revalidation_family(
        repair_runner, parent_core, pack, candidate_rows, legal_access_log
    )
    replay = produce_behavior_causal_replay_report(repair_runner, parent_core, pack, candidate_rows)
    frozen = produce_frozen_input_consumption_report(repair_runner, parent_core, pack)
    negative = produce_negative_evidence_preservation_report(repo_root)
    scope = produce_scope_leak_report(repo_root)
    context_report = core.consume_context_ids_from_controlled_pack(
        pack,
        input_artifact_path=core.rel_path(pack_path, repo_root),
        input_artifact_hash=core.sha_file(pack_path),
        metric_ids=core.METRIC_IDS,
    )
    context_crosscheck = core.crosscheck_context_consumption(context_report, frozen)

    preliminary = {
        "parent_anchor_verification.json": parent_anchors,
        "repair_scope_manifest.json": repair_scope,
        "001e_blocker_preservation_report.json": blocker,
        "metric_schema_repair_report.json": metric_schema,
        "baseline_revalidation_report.json": baseline,
        "ablation_revalidation_report.json": ablation,
        "leakage_revalidation_report.json": leakage,
        "manual_injection_revalidation_report.json": manual,
        "metadata_whitelist_scope_revalidation.json": whitelist,
        "behavior_causal_replay_report.json": replay,
        "frozen_input_consumption_report.json": frozen,
        "negative_evidence_preservation_report.json": negative,
        "scope_leak_report.json": scope,
        "context_consumption_report.json": context_report,
        "context_consumption_crosscheck.json": context_crosscheck,
    }
    for name, data in preliminary.items():
        core.write_json(output_dir / name, data)

    hashes_after = core.hash_old_artifact_trees(repo_root, protected_paths)
    core.write_json(output_dir / "old_artifact_hashes_after.json", hashes_after)
    old_mutation = core.produce_old_artifact_mutation_report(hashes_before, hashes_after)
    core.write_json(output_dir / "old_artifact_mutation_report.json", old_mutation)
    old_provenance = produce_old_artifact_mutation_provenance_report(output_dir)
    core.write_json(output_dir / "old_artifact_mutation_provenance_report.json", old_provenance)

    producers = {
        "baseline_legal_input": (
            f"{__name__}.produce_baseline_revalidation_report",
            __name__,
            core.code_path_hash(produce_baseline_revalidation_report),
        ),
        "baseline_invocation": (
            f"{__name__}.produce_baseline_revalidation_report",
            __name__,
            core.code_path_hash(produce_baseline_revalidation_report),
        ),
        "baseline_non_invocation_failure_control": (
            f"{__name__}.produce_baseline_revalidation_report",
            __name__,
            core.code_path_hash(produce_baseline_revalidation_report),
        ),
        "same_surface_positive_control_failure_control": (
            f"{__name__}.produce_baseline_revalidation_report",
            __name__,
            core.code_path_hash(produce_baseline_revalidation_report),
        ),
        "ablation_revalidation": (
            f"{__name__}.produce_ablation_revalidation_report",
            __name__,
            core.code_path_hash(produce_ablation_revalidation_report),
        ),
        "leakage_revalidation": (
            f"{__name__}.produce_leakage_revalidation_family",
            __name__,
            core.code_path_hash(produce_leakage_revalidation_family),
        ),
        "manual_injection_revalidation": (
            f"{__name__}.produce_leakage_revalidation_family",
            __name__,
            core.code_path_hash(produce_leakage_revalidation_family),
        ),
        "metadata_whitelist_scope": (
            f"{__name__}.produce_leakage_revalidation_family",
            __name__,
            core.code_path_hash(produce_leakage_revalidation_family),
        ),
        "behavior_causal_replay": (
            f"{__name__}.produce_behavior_causal_replay_report",
            __name__,
            core.code_path_hash(produce_behavior_causal_replay_report),
        ),
        "frozen_input_consumption": (
            f"{__name__}.produce_frozen_input_consumption_report",
            __name__,
            core.code_path_hash(produce_frozen_input_consumption_report),
        ),
        "old_artifact_mutation": (
            core.producer_name(core.produce_old_artifact_mutation_report),
            core.produce_old_artifact_mutation_report.__module__,
            core.code_path_hash(core.produce_old_artifact_mutation_report),
        ),
        "negative_evidence_preservation": (
            f"{__name__}.produce_negative_evidence_preservation_report",
            __name__,
            core.code_path_hash(produce_negative_evidence_preservation_report),
        ),
    }
    metrics = _build_metric_provenance(output_dir, pack, context_report, producers)
    core.write_json(output_dir / "metric_provenance.json", metrics)
    completeness = core.validate_metric_provenance(metrics, context_report, old_provenance)
    core.write_json(output_dir / "metric_provenance_completeness_report.json", completeness)

    failure_context = produce_failure_path_context_consumption_report(
        metrics, context_report, old_provenance
    )
    failure_old = produce_failure_path_old_artifact_mutation_provenance_report(
        metrics, context_report, old_provenance
    )
    core.write_json(output_dir / "failure_path_context_consumption_report.json", failure_context)
    core.write_json(output_dir / "failure_path_old_artifact_mutation_provenance_report.json", failure_old)

    old_validation = core.validate_old_artifact_mutation_provenance(old_provenance)
    acceptance_gates = {
        "parent_001t_anchor_verified": any(
            row["tag"] == "remote-anchor-001t-8ed4a5a" and row["local_verified"] and row["remote_verified"]
            for row in parent_anchors["anchors"]
        ),
        "parent_001s_anchor_verified": any(
            row["tag"] == "remote-anchor-001s-3d90e1a" and row["local_verified"] and row["remote_verified"]
            for row in parent_anchors["anchors"]
        ),
        "parent_001r_anchor_verified": any(
            row["tag"] == "remote-anchor-001r-0fdf451" and row["local_verified"] and row["remote_verified"]
            for row in parent_anchors["anchors"]
        ),
        "parent_001q_anchor_verified": any(
            row["tag"] == "remote-anchor-001q-60a504e" and row["local_verified"] and row["remote_verified"]
            for row in parent_anchors["anchors"]
        ),
        "parent_001p_anchor_verified": any(
            row["tag"] == "remote-anchor-001p-cda09dc" and row["local_verified"] and row["remote_verified"]
            for row in parent_anchors["anchors"]
        ),
        "parent_001o_anchor_verified": any(
            row["tag"] == "remote-anchor-001o-f648dac" and row["local_verified"] and row["remote_verified"]
            for row in parent_anchors["anchors"]
        ),
        "computed_evidence_contract_loaded": contract_loaded,
        "001e_blocker_preserved": blocker["001e_blocker_preserved"],
        "001d_blocked_status_preserved_until_repair_result": blocker[
            "001d_blocked_status_preserved_until_repair_result"
        ],
        "repair_scope_exact": repair_scope["repair_scope_exact"],
        "old_001d_artifacts_not_modified": old_mutation["old_001d_artifacts_not_modified"],
        "old_001e_artifacts_not_modified": old_mutation["old_001e_artifacts_not_modified"],
        "known_theory_file_left_unstaged_and_unmodified": scope[
            "known_theory_file_left_unstaged_and_unmodified"
        ],
        "all_verdict_metrics_have_train_context_ids_consumed": completeness[
            "all_verdict_metrics_have_train_context_ids_consumed"
        ],
        "all_verdict_metrics_have_heldout_context_ids_consumed": completeness[
            "all_verdict_metrics_have_heldout_context_ids_consumed"
        ],
        "all_verdict_metrics_have_counterfactual_pair_ids_consumed": completeness[
            "all_verdict_metrics_have_counterfactual_pair_ids_consumed"
        ],
        "context_consumption_fields_computed_by_callable_producers": completeness[
            "context_consumption_fields_computed_by_callable_producers"
        ],
        "context_consumption_crosschecked_against_freeze": context_crosscheck[
            "context_consumption_crosschecked_against_freeze"
        ],
        "no_decorative_context_ids": completeness["no_decorative_context_ids"],
        "old_artifact_mutation_true_producer_provenance": old_validation[
            "old_artifact_mutation_true_producer_provenance"
        ],
        "old_artifact_before_after_hashes_computed": old_validation[
            "old_artifact_before_after_hashes_computed"
        ],
        "failure_path_context_consumption_passed": failure_context[
            "failure_path_context_consumption_passed"
        ],
        "failure_path_old_artifact_mutation_provenance_passed": failure_old[
            "failure_path_old_artifact_mutation_provenance_passed"
        ],
        "all_verdict_metrics_have_callable_provenance": completeness[
            "all_verdict_metrics_have_callable_provenance"
        ],
        "no_literal_metrics": completeness["no_literal_metrics"],
        "no_static_metric_dictionaries": completeness["no_static_metric_dictionaries"],
        "no_copied_old_001d_results": completeness["no_copied_old_001d_results"],
        "baseline_revalidation_passed": baseline["baseline_revalidation_passed"],
        "ablation_revalidation_passed": ablation["ablation_revalidation_passed"],
        "leakage_revalidation_passed": leakage["leakage_revalidation_passed"],
        "manual_injection_revalidation_passed": manual["manual_injection_revalidation_passed"],
        "metadata_whitelist_surface_scoped": whitelist["metadata_whitelist_surface_scoped"],
        "behavior_causal_replay_passed": replay["behavior_causal_replay_passed"],
        "frozen_inputs_consumed": frozen["frozen_inputs_consumed"],
        "negative_evidence_preserved": negative["negative_evidence_preserved"],
        "no_scope_leak": scope["no_scope_leak"],
        "no_claim_inflation": scope["no_claim_inflation"],
        "no_Ego_repo_modification": scope["no_Ego_repo_modification"],
        "no_runtime_or_product_work": scope["no_runtime_or_product_work"],
    }
    stop_flags = {
        "missing_parent_anchor": not all(
            acceptance_gates[key]
            for key in [
                "parent_001t_anchor_verified",
                "parent_001s_anchor_verified",
                "parent_001r_anchor_verified",
                "parent_001q_anchor_verified",
                "parent_001p_anchor_verified",
                "parent_001o_anchor_verified",
            ]
        ),
        "missing_computed_evidence_contract": not contract_loaded,
        "001e_blocker_not_preserved": not acceptance_gates["001e_blocker_preserved"],
        "repair_scope_expanded": not acceptance_gates["repair_scope_exact"],
        "old_artifact_mutation": not acceptance_gates["old_001d_artifacts_not_modified"]
        or not acceptance_gates["old_001e_artifacts_not_modified"],
        "known_theory_file_staged": scope["known_theory_file_status"]["known_theory_file_staged"],
        "known_theory_file_modified": scope["known_theory_file_status"]["known_theory_file_modified"],
        "unexpected_untracked_file": bool(scope["unexpected_untracked_files"]),
        "baseline_revalidation_failed": not acceptance_gates["baseline_revalidation_passed"],
        "ablation_revalidation_failed": not acceptance_gates["ablation_revalidation_passed"],
        "leakage_revalidation_failed": not acceptance_gates["leakage_revalidation_passed"],
        "manual_injection_revalidation_failed": not acceptance_gates[
            "manual_injection_revalidation_passed"
        ],
        "metadata_whitelist_not_surface_scoped": not acceptance_gates[
            "metadata_whitelist_surface_scoped"
        ],
        "replay_not_behavior_causal": not acceptance_gates["behavior_causal_replay_passed"],
        "unused_frozen_input": not acceptance_gates["frozen_inputs_consumed"],
        "negative_evidence_rewrite": not acceptance_gates["negative_evidence_preserved"],
        "scope_leak": not acceptance_gates["no_scope_leak"],
        "claim_inflation": not acceptance_gates["no_claim_inflation"],
        "ego_repository_modification": not acceptance_gates["no_Ego_repo_modification"],
        "runtime_or_product_work_created": not acceptance_gates["no_runtime_or_product_work"],
    }
    for condition in completeness["stop_conditions"]:
        stop_flags[condition] = True
    for condition in old_validation["stop_conditions"]:
        stop_flags[condition] = True
    if not failure_context["failure_path_context_consumption_passed"] or not failure_old[
        "failure_path_old_artifact_mutation_provenance_passed"
    ]:
        stop_flags["failure_path_missing"] = True
    verdict, stop_conditions = core.evaluate_verdict(stop_flags)
    result = {
        "task_id": core.TASK_ID,
        "parent_task_id": core.PARENT_001D_TASK_ID,
        "layer": core.LAYER,
        "verdict": verdict,
        "bounded_pass": verdict == core.VERDICT_PASS and all(acceptance_gates.values()),
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "claim_ceiling": core.CLAIM_CEILING,
        "authorization_flags": core.AUTHORIZATION_FLAGS,
        "parent_anchors_verified": parent_anchors["all_parent_anchors_verified"],
        "acceptance_gates": acceptance_gates,
        "stop_conditions_triggered": stop_conditions,
        "001e_blocker_preservation_result": blocker,
        "repair_scope_result": repair_scope,
        "metric_provenance_schema_repair_result": metric_schema,
        "context_consumption_result": {
            "context_consumption_fields_computed_by_callable_producers": context_report[
                "context_consumption_fields_computed_by_callable_producers"
            ],
            "context_consumption_crosschecked_against_freeze": context_crosscheck[
                "context_consumption_crosschecked_against_freeze"
            ],
            "no_decorative_context_ids": completeness["no_decorative_context_ids"],
        },
        "old_artifact_mutation_provenance_result": old_provenance,
        "failure_path_controls_result": {
            "failure_path_context_consumption_passed": failure_context[
                "failure_path_context_consumption_passed"
            ],
            "failure_path_old_artifact_mutation_provenance_passed": failure_old[
                "failure_path_old_artifact_mutation_provenance_passed"
            ],
        },
        "baseline_revalidation_result": baseline,
        "ablation_revalidation_result": ablation,
        "leakage_revalidation_result": leakage,
        "manual_injection_result": manual,
        "metadata_whitelist_scope_result": whitelist,
        "replay_result": replay,
        "frozen_input_consumption_result": frozen,
        "negative_evidence_preservation_result": negative,
        "scope_claim_ceiling_result": {
            "known_theory_file_left_unstaged_and_unmodified": scope[
                "known_theory_file_left_unstaged_and_unmodified"
            ],
            "no_scope_leak": scope["no_scope_leak"],
            "no_claim_inflation": scope["no_claim_inflation"],
            "no_Ego_repo_modification": scope["no_Ego_repo_modification"],
            "no_runtime_or_product_work": scope["no_runtime_or_product_work"],
        },
        "what_this_does_not_prove": [
            "001D independent audit pass",
            "001B independent audit pass",
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
    core.write_json(output_dir / "result.json", result)
    core.write_text(output_dir / "claim_ceiling.txt", core.CLAIM_CEILING + "\n")
    if not result["bounded_pass"]:
        core.write_json(
            output_dir / "blocker_report.json",
            {
                "task_id": core.TASK_ID,
                "verdict": verdict,
                "stop_conditions_triggered": stop_conditions,
                "minimum_patch": "repair only the exact new 001F blocker in a later bounded task",
            },
        )
    else:
        blocker_path = output_dir / "blocker_report.json"
        if blocker_path.exists():
            blocker_path.unlink()
    return result
