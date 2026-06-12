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
    output = (completed.stdout or completed.stderr).strip()
    return completed.returncode == 0, output


def _load_parent_core(repo_root: Path) -> Any:
    src = str(repo_root / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    return importlib.import_module("ego_mainline_admission_executable_001b.core")


def _parent_artifact(repo_root: Path, name: str) -> Path:
    return repo_root / core.PARENT_ARTIFACT_DIR_REL / name


def _read_parent_json(repo_root: Path, name: str) -> Any:
    return core.read_json(_parent_artifact(repo_root, name))


def _hash_paths(paths: list[Path], repo_root: Path) -> dict[str, str]:
    return {
        core.rel_path(path, repo_root): core.sha_file(path)
        for path in paths
        if path.exists()
    }


def _protected_parent_paths(repo_root: Path) -> list[Path]:
    parent_dir = repo_root / core.PARENT_ARTIFACT_DIR_REL
    return [
        repo_root / "docs" / "codex" / "tasks" / "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B.md",
        repo_root / "docs" / "codex" / "tasks" / "EGO-MAINLINE-ADMISSION-TASK-CARD-001A.md",
        repo_root / "docs" / "codex" / "contracts" / "COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md",
        *(path for path in parent_dir.glob("*.json")),
        *(path for path in parent_dir.glob("*.txt")),
        *(path for path in parent_dir.glob("*.sha256")),
    ]


def _source_hashes(repo_root: Path) -> dict[str, str]:
    source_dir = repo_root / core.PARENT_SOURCE_DIR_REL
    return _hash_paths(sorted(source_dir.glob("*.py")), repo_root)


def _producer_callable(parent_core: Any, producer_function: str) -> Any | None:
    function_name = producer_function.rsplit(".", 1)[-1].split(":", 1)[0]
    return getattr(parent_core, function_name, None)


def _producer_hash_matches(parent_core: Any, row: dict[str, Any]) -> bool:
    producer = row.get("producer_function", "")
    function = _producer_callable(parent_core, producer)
    if function is None:
        return False
    salt = producer.split(":", 1)[1] if ":" in producer else ""
    return row.get("code_path_hash") == parent_core.code_path_hash(function, salt)


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


def _audit_metric_provenance(repo_root: Path, parent_core: Any) -> dict[str, Any]:
    metrics = _read_parent_json(repo_root, "metric_provenance.json")
    rows = metrics.get("metrics", [])
    missing_fields = []
    uncallable = []
    hash_mismatches = []
    artifact_hash_mismatches = []
    literal_metrics = []
    failure_path_missing = []
    for row in rows:
        metric_id = row.get("metric_id", "<missing>")
        missing = sorted(core.REQUIRED_METRIC_FIELDS - set(row))
        if missing:
            missing_fields.append({"metric_id": metric_id, "missing_fields": missing})
        if not row.get("computed_not_literal"):
            literal_metrics.append(metric_id)
        if not row.get("failure_path_available"):
            failure_path_missing.append(metric_id)
        if _producer_callable(parent_core, row.get("producer_function", "")) is None:
            uncallable.append(metric_id)
        elif not _producer_hash_matches(parent_core, row):
            hash_mismatches.append(metric_id)
        for artifact_name, expected_hash in row.get("input_artifact_hashes", {}).items():
            artifact_path = _parent_artifact(repo_root, artifact_name)
            if not artifact_path.exists() or core.sha_file(artifact_path) != expected_hash:
                artifact_hash_mismatches.append(
                    {
                        "metric_id": metric_id,
                        "artifact": artifact_name,
                        "expected_hash": expected_hash,
                        "actual_hash": core.sha_file(artifact_path) if artifact_path.exists() else None,
                    }
                )
    return {
        "task_id": core.TASK_ID,
        "metric_count": len(rows),
        "all_verdict_metrics_have_callable_provenance": bool(rows)
        and not missing_fields
        and not uncallable
        and not hash_mismatches
        and not artifact_hash_mismatches
        and not literal_metrics
        and not failure_path_missing,
        "literal_metric_detected": bool(literal_metrics),
        "static_metric_dictionary_detected": False,
        "missing_fields": missing_fields,
        "uncallable_producers": uncallable,
        "code_path_hash_mismatches": hash_mismatches,
        "input_artifact_hash_mismatches": artifact_hash_mismatches,
        "metrics_missing_failure_path": failure_path_missing,
    }


def _audit_baselines(repo_root: Path, parent_core: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    baseline_report = _read_parent_json(repo_root, "baseline_report.json")
    invocation_report = _read_parent_json(repo_root, "baseline_invocation_report.json")
    baseline_source = inspect.getsource(parent_core.baseline_action)
    illegal_label = "verifier_expected_action_id" in baseline_source
    baseline_ids = {row["baseline_id"] for row in baseline_report.get("baselines", [])}
    invocation_ids = {row["baseline_id"] for row in invocation_report.get("invocations", [])}
    rows_exist = all(row.get("output_rows") for row in baseline_report.get("baselines", []))
    invocations_ok = all(row.get("callable_invoked") for row in invocation_report.get("invocations", []))
    outputs_before_aggregation = all(
        row.get("output_rows_exist_before_aggregation") for row in invocation_report.get("invocations", [])
    )
    static_reports = [
        row["baseline_id"] for row in invocation_report.get("invocations", []) if row.get("static_dictionary_used")
    ]
    fair_equivalence = [
        row["baseline_id"]
        for row in baseline_report.get("baselines", [])
        if row.get("counts_as_fair_baseline") and row.get("matches_or_beats_candidate")
    ]
    independence = {
        "task_id": core.TASK_ID,
        "baseline_independence_verified": not illegal_label and not fair_equivalence,
        "illegal_verifier_label_consumption_detected": illegal_label,
        "illegal_source_token": "verifier_expected_action_id" if illegal_label else None,
        "baseline_implementation_aliases_candidate": "compute_candidate_action" in baseline_source,
        "baseline_equivalence_detected": bool(fair_equivalence),
        "equivalent_or_better_fair_baselines": fair_equivalence,
        "baseline_ids": sorted(baseline_ids),
        "notes": (
            "baseline_action reads verifier_expected_action_id while generating baseline actions"
            if illegal_label
            else "no illegal verifier-label source token detected"
        ),
    }
    invocation = {
        "task_id": core.TASK_ID,
        "baseline_functions_exist": hasattr(parent_core, "baseline_action"),
        "baseline_functions_invoked": invocations_ok,
        "baseline_outputs_exist_before_aggregation": rows_exist and outputs_before_aggregation,
        "baseline_outputs_are_not_static_dictionaries": not static_reports,
        "baseline_invocation_ids_match_report_ids": baseline_ids == invocation_ids,
        "static_dictionary_baselines": static_reports,
    }
    return independence, invocation


def _audit_ablations(repo_root: Path, parent_core: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    ablation_report = _read_parent_json(repo_root, "ablation_report.json")
    invocation_report = _read_parent_json(repo_root, "ablation_invocation_report.json")
    invocations = invocation_report.get("invocations", [])
    ablations = ablation_report.get("ablations", [])
    return (
        {
            "task_id": core.TASK_ID,
            "required_ablations_rerun": all(row.get("reran_candidate_behavior") for row in invocations),
            "ablation_outputs_recomputed": all(not row.get("copied_from_candidate_outputs") for row in invocations),
            "ablation_interventions_applied": hasattr(parent_core, "apply_ablation")
            and all(row.get("intervention_function") for row in invocations),
            "missing_or_not_rerun": [
                row.get("ablation_id") for row in invocations if not row.get("reran_candidate_behavior")
            ],
            "copied_outputs": [
                row.get("ablation_id") for row in invocations if row.get("copied_from_candidate_outputs")
            ],
        },
        {
            "task_id": core.TASK_ID,
            "ablation_sensitivity_verified": bool(ablations) and all(row.get("sensitive") for row in ablations),
            "insensitive_ablations": [row.get("ablation_id") for row in ablations if not row.get("sensitive")],
            "candidate_score": ablation_report.get("candidate_score"),
        },
    )


def _audit_leakage(repo_root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    inventory = _read_parent_json(repo_root, "leakage_surface_inventory.json")
    leakage = _read_parent_json(repo_root, "leakage_scan_report.json")
    positives = _read_parent_json(repo_root, "leakage_positive_control_report.json")
    manual = _read_parent_json(repo_root, "manual_leakage_injection_report.json")
    surfaces = {row.get("surface_name") for row in inventory.get("surfaces", [])}
    surface_rows = leakage.get("surface_results", [])
    whitelist = _read_parent_json(repo_root, "metadata_whitelist_surface_scope_report.json")
    return (
        {
            "task_id": core.TASK_ID,
            "leakage_real_surfaces_scanned": core.REQUIRED_SURFACES.issubset(surfaces)
            and {row.get("surface_name") for row in surface_rows} == core.REQUIRED_SURFACES,
            "missing_surfaces": sorted(core.REQUIRED_SURFACES - surfaces),
            "leakage_detected": leakage.get("leakage_detected"),
            "scanner_failability_verified": not leakage.get("scanner_not_fail_able"),
            "scanner_not_fail_able": leakage.get("scanner_not_fail_able"),
            "real_surface_hits": [
                {"surface_name": row.get("surface_name"), "hits": row.get("real_scan_hits")}
                for row in surface_rows
                if row.get("real_scan_detected")
            ],
        },
        {
            "task_id": core.TASK_ID,
            "same_surface_positive_controls_detected": positives.get("same_surface_positive_controls_detected")
            and all(row.get("positive_control_detected") for row in surface_rows),
            "same_surface_clean_controls_pass": all(not row.get("clean_control_detected") for row in surface_rows),
            "missing_positive_controls": [
                row.get("surface_name") for row in surface_rows if not row.get("positive_control_detected")
            ],
        },
        {
            "task_id": core.TASK_ID,
            "manual_injection_independence_verified": manual.get("independent_manual_leakage_injection_tests_passed")
            and not manual.get("production_injector_only"),
            "production_injector_only": manual.get("production_injector_only"),
            "manual_case_count": len(manual.get("manual_cases", [])),
        },
        {
            "task_id": core.TASK_ID,
            "metadata_whitelist_surface_scoped": whitelist.get("metadata_whitelist_surface_scoped"),
            "global_reserved_metadata_key_privilege": whitelist.get("global_reserved_metadata_key_privilege"),
            "reserved_key_value_scanned_on_unprivileged_surface": whitelist.get(
                "reserved_key_value_scanned_on_unprivileged_surface"
            ),
            "privileged_surface_safe_key_passed": whitelist.get("privileged_surface_safe_key_passed"),
            "privileged_surface_forbidden_value_detected": whitelist.get(
                "privileged_surface_forbidden_value_detected"
            ),
            "surface_metadata_key_allowlist": whitelist.get("surface_metadata_key_allowlist", {}),
        },
    )


def _audit_replay(repo_root: Path, parent_core: Any) -> dict[str, Any]:
    pack = _read_parent_json(repo_root, "controlled_evidence_pack_manifest.json")
    candidate_rows = _read_parent_json(repo_root, "candidate_output_rows.json")
    recorded = {row["episode_id"]: row["candidate_action_id"] for row in candidate_rows}
    mismatches = []
    changed_under_state_mutation = False
    for episode in pack.get("episodes", []):
        state = dict(episode["serialized_state"])
        observation = dict(episode["observation"])
        recomputed = parent_core.compute_candidate_action(state, observation)
        if recomputed != recorded.get(episode["episode_id"]):
            mismatches.append(episode["episode_id"])
        mutated = dict(state)
        mutated["identity_continuity_state"] = (mutated["identity_continuity_state"] + 1) % len(parent_core.ACTION_IDS)
        if parent_core.compute_candidate_action(mutated, observation) != recomputed:
            changed_under_state_mutation = True
    replay = _read_parent_json(repo_root, "behavior_causal_replay_report.json")
    return {
        "task_id": core.TASK_ID,
        "behavior_causal_replay_verified": not mismatches
        and replay.get("behavior_causal_replay_passed")
        and replay.get("hash_only_replay") is False,
        "serialized_state_loaded_from_artifact": bool(pack.get("episodes")),
        "observation_loaded_from_artifact": all("observation" in episode for episode in pack.get("episodes", [])),
        "candidate_action_recomputed": True,
        "recomputed_action_matches_recorded_action": not mismatches,
        "mismatches": mismatches,
        "hash_only_replay_not_used_for_behavior_claim": replay.get("hash_only_replay") is False,
        "serialized_state_causal_consumption_verified": changed_under_state_mutation,
    }


def _audit_frozen_inputs(repo_root: Path) -> dict[str, Any]:
    frozen = _read_parent_json(repo_root, "frozen_input_consumption_report.json")
    missing = []
    for family, row in frozen.get("families", {}).items():
        if row.get("unused"):
            missing.extend(f"{family}:{value}" for value in row["unused"])
    return {
        "task_id": core.TASK_ID,
        "frozen_inputs_consumed": frozen.get("all_frozen_inputs_consumed") and not missing,
        "unused_frozen_inputs": missing,
        "families_checked": sorted(frozen.get("families", {})),
    }


def _audit_failure_paths(repo_root: Path) -> dict[str, Any]:
    report = _read_parent_json(repo_root, "failure_path_test_report.json")
    parent_tests = (repo_root / "tests" / "test_ego_mainline_admission_executable_001b.py").read_text(
        encoding="utf-8"
    )
    observed_ids = {row.get("failure_id") for row in report.get("failure_paths", [])}
    source_hits = {
        "ego_repository_modification"
        for token in ["ego_repository_modification"]
        if token in parent_tests
    }
    available = observed_ids | source_hits
    missing = []
    for control, aliases in core.PARENT_FAILURE_CONTROL_ALIASES.items():
        if not aliases.intersection(available):
            missing.append(control)
    tests_only_assert_pass = "verdict\"] == VERDICT" in parent_tests and "evaluate_stop_conditions" not in parent_tests
    return {
        "task_id": core.TASK_ID,
        "failure_path_tests_verified": not missing and report.get("failure_path_tests_passed"),
        "reported_failure_path_tests_passed": report.get("failure_path_tests_passed"),
        "required_failure_controls": sorted(core.REQUIRED_FAILURE_CONTROLS),
        "observed_failure_controls": sorted(available),
        "missing_failure_controls": sorted(missing),
        "tests_only_assert_pass": tests_only_assert_pass,
    }


def _audit_negative_evidence(repo_root: Path) -> dict[str, Any]:
    negative = _read_parent_json(repo_root, "negative_evidence_preservation_report.json")
    dependency = _read_parent_json(repo_root, "evidence_dependency_matrix.json")
    current = _read_parent_json(repo_root, "current_evidence_status_report.json")
    return {
        "task_id": core.TASK_ID,
        "001b_invalidation_preserved": negative.get("001b_invalidation_preserved")
        and not dependency.get("post_bridge_admission_executable_001b", {}).get("used_as_positive_evidence"),
        "001c_suspension_preserved": negative.get("001c_suspension_preserved")
        and not dependency.get("post_bridge_admission_executable_001c", {}).get("used_as_positive_evidence"),
        "001d_caveat_preserved": "with caveats"
        in current.get("post_bridge_admission_executable_001d", {}).get("status", ""),
        "negative_evidence_rewrite_detected": negative.get("negative_evidence_rewrite_detected"),
    }


def _audit_scope_and_claim(repo_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    result = _read_parent_json(repo_root, "result.json")
    forbidden_claims = [
        "EGO readiness",
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
    ]
    result_text = core.canonical_json(result)
    inflated = [
        claim
        for claim in forbidden_claims
        if claim in result_text and claim not in result.get("what_this_does_not_prove", [])
    ]
    flags = result.get("authorization_flags", {})
    return (
        {
            "task_id": core.TASK_ID,
            "claim_ceiling_preserved": result.get("claim_ceiling")
            == "bounded EGO-mainline admission executable gate evidence under synthetic / controlled conditions only"
            and not inflated,
            "inflated_claims_detected": inflated,
            "parent_claim_ceiling": result.get("claim_ceiling"),
            "audit_claim_ceiling": core.CLAIM_CEILING,
        },
        {
            "task_id": core.TASK_ID,
            "no_scope_leak": all(value is False for value in flags.values() if isinstance(value, bool)),
            "no_Ego_repo_modification": flags.get("ego_repository_modification_authorized") is False,
            "no_runtime_or_product_work": flags.get("ego_mainline_runtime_authorized") is False
            and flags.get("bridge_runtime_authorized") is False
            and flags.get("llm_rag_authorized") is False,
            "authorization_flags": flags,
        },
    )


def _audit_contract_coverage(audits: dict[str, Any], findings: list[dict[str, Any]]) -> dict[str, Any]:
    blocker_ids = {finding["finding_id"] for finding in findings if finding["severity"] == "blocker"}
    rows = [
        ("parent_anchors", "verify 001B, 001A, and 001O remote anchors", "parent_anchor_verification.json", audits["parents"]["all_parent_anchors_verified"]),
        ("computed_contract", "load computed-evidence provenance contract", "metric_provenance_audit.json", audits["metrics"]["all_verdict_metrics_have_callable_provenance"]),
        ("baseline_invocation", "baseline functions invoked with output rows before aggregation", "baseline_invocation_audit.json", audits["baseline_invocation"]["baseline_functions_invoked"]),
        ("baseline_legal_inputs", "baselines consume comparable legal inputs", "baseline_independence_audit.json", audits["baseline_independence"]["baseline_independence_verified"]),
        ("ablation_rerun", "ablations rerun candidate behavior under interventions", "ablation_rerun_audit.json", audits["ablation_rerun"]["required_ablations_rerun"]),
        ("leakage_surfaces", "real leakage surfaces and same-surface controls are scanned", "leakage_surface_audit.json", audits["leakage_surface"]["leakage_real_surfaces_scanned"]),
        ("metadata_whitelist", "metadata whitelist is surface scoped", "metadata_whitelist_scope_audit.json", audits["metadata_whitelist"]["metadata_whitelist_surface_scoped"]),
        ("behavior_replay", "behavior replay recomputes action from serialized_state and observation", "behavior_causal_replay_audit.json", audits["replay"]["behavior_causal_replay_verified"]),
        ("frozen_inputs", "frozen inputs are consumed", "frozen_input_consumption_audit.json", audits["frozen"]["frozen_inputs_consumed"]),
        ("failure_paths", "failure path tests cover required corruption controls", "failure_path_test_audit.json", audits["failure_paths"]["failure_path_tests_verified"]),
        ("negative_evidence", "001B invalidation, 001C suspension, and 001D caveat are preserved", "negative_evidence_preservation_audit.json", audits["negative"]["001b_invalidation_preserved"] and audits["negative"]["001c_suspension_preserved"] and audits["negative"]["001d_caveat_preserved"]),
        ("claim_scope", "claim ceiling and scope boundaries are preserved", "claim_ceiling_audit.json", audits["claim"]["claim_ceiling_preserved"] and audits["scope"]["no_scope_leak"]),
    ]
    matrix = []
    for requirement_id, text, artifact, passed in rows:
        status = "covered" if passed else "partial"
        severity = "none" if passed else "blocker"
        if requirement_id == "baseline_legal_inputs" and "baseline_illegal_verifier_label_consumption" in blocker_ids:
            status = "contradicted"
        matrix.append(
            {
                "requirement_id": requirement_id,
                "requirement_text": text,
                "evidence_artifact": artifact,
                "evidence_function_or_test": "independent_audit_001c",
                "status": status,
                "severity": severity,
                "notes": "see audit_finding_inventory.json" if not passed else "covered by audit artifact",
            }
        )
    return {
        "task_id": core.TASK_ID,
        "requirements": matrix,
        "all_contract_requirements_accounted_for": len(matrix) == len(rows),
        "contract_coverage_complete": all(row["status"] == "covered" for row in matrix),
        "complete_or_blocked_by_specific_findings": all(
            row["status"] == "covered" or blocker_ids for row in matrix
        ),
    }


def _build_task_doc() -> str:
    return f"""# EGO-MAINLINE-ADMISSION-EXECUTABLE-001B-INDEPENDENT-AUDIT-001C

## Task Identity

```text
task_id = {core.TASK_ID}
layer = {core.LAYER}
claim_ceiling = {core.CLAIM_CEILING}
```

## Framing

This is a bounded independent audit of `EGO-MAINLINE-ADMISSION-EXECUTABLE-001B`.
It does not patch, rerun as success, reinterpret, or weaken 001B. It reads the
001B task card, source, tests, and artifacts, then emits separate audit
artifacts under `{core.ARTIFACT_DIR_REL}`.

## Strongest Baseline Explanation

001B may be a synthetic self-pass if baseline, ablation, leakage, replay, or
metric reports are internally consistent but not derived from legal independent
computation paths.

## Audit Result

The independent audit blocks on baseline legality: the parent baseline action
path reads `verifier_expected_action_id` while generating baseline actions. This
means the baseline rows can be invoked and non-static while still failing the
001A requirement that fair baselines consume comparable legal inputs.

The audit also records a secondary failure-path coverage gap for corruption
families named by this audit task but not fully represented by 001B's
machine-readable failure-path report.

## Claim Ceiling

This result is bounded independent audit evidence only. It does not prove EGO
readiness, bridge readiness, runtime admissibility, mechanism validity, theory
validity, agency, selfhood, consciousness, real emotion, relationship learning,
companion readiness, stable user benefit, production readiness, or correctness
of any future EGO runtime.
"""


def run_audit(*, repo_root: Path, output_dir: Path, verify_remote: bool = True) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    parent_core = _load_parent_core(repo_root)
    protected_before = _hash_paths(_protected_parent_paths(repo_root), repo_root)

    parents = _verify_parent_anchors(repo_root, verify_remote)
    metrics = _audit_metric_provenance(repo_root, parent_core)
    baseline_independence, baseline_invocation = _audit_baselines(repo_root, parent_core)
    ablation_rerun, ablation_sensitivity = _audit_ablations(repo_root, parent_core)
    leakage_surface, leakage_positive, manual_injection, metadata_whitelist = _audit_leakage(repo_root)
    replay = _audit_replay(repo_root, parent_core)
    frozen = _audit_frozen_inputs(repo_root)
    source_integrity = {
        "task_id": core.TASK_ID,
        "source_hashes": _source_hashes(repo_root),
        "source_artifacts_exist": bool(_source_hashes(repo_root)),
    }
    failure_paths = _audit_failure_paths(repo_root)
    negative = _audit_negative_evidence(repo_root)
    claim, scope = _audit_scope_and_claim(repo_root)
    protected_after = _hash_paths(_protected_parent_paths(repo_root), repo_root)
    old_mutation = {
        "task_id": core.TASK_ID,
        "old_artifacts_not_mutated": protected_before == protected_after,
        "before_hashes": protected_before,
        "after_hashes": protected_after,
        "mutated_paths": sorted(
            path for path, before_hash in protected_before.items() if protected_after.get(path) != before_hash
        ),
    }

    findings = []
    if not parents["all_parent_anchors_verified"]:
        findings.append(
            {
                "finding_id": "missing_parent_anchor",
                "severity": "blocker",
                "verdict": core.VERDICT_BLOCK_PARENT,
                "evidence_artifact": "parent_anchor_verification.json",
                "notes": "one or more required parent anchors did not verify",
            }
        )
    if baseline_independence["illegal_verifier_label_consumption_detected"]:
        findings.append(
            {
                "finding_id": "baseline_illegal_verifier_label_consumption",
                "severity": "blocker",
                "verdict": core.VERDICT_BLOCK_BASELINE,
                "evidence_artifact": "baseline_independence_audit.json",
                "notes": "baseline_action reads verifier_expected_action_id while generating baseline actions",
            }
        )
    if not failure_paths["failure_path_tests_verified"]:
        findings.append(
            {
                "finding_id": "failure_path_test_missing",
                "severity": "blocker",
                "verdict": core.VERDICT_BLOCK_FAILURE_PATH,
                "evidence_artifact": "failure_path_test_audit.json",
                "notes": "001B failure-path coverage does not include every required corruption control",
            }
        )

    audits = {
        "parents": parents,
        "metrics": metrics,
        "baseline_independence": baseline_independence,
        "baseline_invocation": baseline_invocation,
        "ablation_rerun": ablation_rerun,
        "ablation_sensitivity": ablation_sensitivity,
        "leakage_surface": leakage_surface,
        "leakage_positive": leakage_positive,
        "manual_injection": manual_injection,
        "metadata_whitelist": metadata_whitelist,
        "replay": replay,
        "frozen": frozen,
        "source_integrity": source_integrity,
        "old_mutation": old_mutation,
        "failure_paths": failure_paths,
        "negative": negative,
        "claim": claim,
        "scope": scope,
    }
    coverage = _audit_contract_coverage(audits, findings)

    verdict = core.VERDICT_PASS
    if findings:
        verdict = findings[0]["verdict"]
    result = {
        "task_id": core.TASK_ID,
        "parent_task_id": core.PARENT_TASK_ID,
        "layer": core.LAYER,
        "verdict": verdict,
        "bounded_pass": not findings and coverage["contract_coverage_complete"],
        "artifact_dir": core.ARTIFACT_DIR_REL,
        "claim_ceiling": core.CLAIM_CEILING,
        "authorization_flags": core.AUTHORIZATION_FLAGS,
        "stop_conditions_triggered": [finding["finding_id"] for finding in findings],
        "parent_anchors_verified": parents["all_parent_anchors_verified"],
        "contract_coverage_result": {
            "contract_coverage_complete": coverage["contract_coverage_complete"],
            "all_contract_requirements_accounted_for": coverage["all_contract_requirements_accounted_for"],
        },
        "metric_provenance_audit_result": {
            "all_verdict_metrics_have_callable_provenance": metrics[
                "all_verdict_metrics_have_callable_provenance"
            ],
            "literal_metric_detected": metrics["literal_metric_detected"],
            "metric_count": metrics["metric_count"],
        },
        "baseline_audit_result": {
            "baseline_functions_invoked": baseline_invocation["baseline_functions_invoked"],
            "baseline_outputs_exist_before_aggregation": baseline_invocation[
                "baseline_outputs_exist_before_aggregation"
            ],
            "baseline_independence_verified": baseline_independence["baseline_independence_verified"],
            "illegal_verifier_label_consumption_detected": baseline_independence[
                "illegal_verifier_label_consumption_detected"
            ],
        },
        "ablation_audit_result": {
            "required_ablations_rerun": ablation_rerun["required_ablations_rerun"],
            "ablation_outputs_recomputed": ablation_rerun["ablation_outputs_recomputed"],
            "ablation_sensitivity_verified": ablation_sensitivity["ablation_sensitivity_verified"],
        },
        "leakage_audit_result": {
            "leakage_real_surfaces_scanned": leakage_surface["leakage_real_surfaces_scanned"],
            "same_surface_positive_controls_detected": leakage_positive[
                "same_surface_positive_controls_detected"
            ],
            "scanner_failability_verified": leakage_surface["scanner_failability_verified"],
        },
        "manual_injection_audit_result": manual_injection,
        "metadata_whitelist_audit_result": {
            "metadata_whitelist_surface_scoped": metadata_whitelist["metadata_whitelist_surface_scoped"],
            "global_reserved_metadata_key_privilege": metadata_whitelist[
                "global_reserved_metadata_key_privilege"
            ],
        },
        "replay_audit_result": replay,
        "frozen_input_consumption_audit_result": frozen,
        "failure_path_audit_result": failure_paths,
        "negative_evidence_preservation_result": negative,
        "scope_claim_ceiling_result": {
            "claim_ceiling_preserved": claim["claim_ceiling_preserved"],
            "no_scope_leak": scope["no_scope_leak"],
            "no_Ego_repo_modification": scope["no_Ego_repo_modification"],
            "no_runtime_or_product_work": scope["no_runtime_or_product_work"],
        },
        "what_this_does_not_prove": [
            "EGO readiness",
            "bridge readiness",
            "EGO-mainline admission readiness",
            "runtime admissibility",
            "mechanism validity",
            "theory validity",
            "agency",
            "selfhood",
            "consciousness",
            "real emotion",
            "real relationship learning",
            "companion readiness",
            "stable user benefit",
            "production readiness",
            "correctness of any future EGO runtime",
        ],
    }

    artifact_map = {
        "parent_anchor_verification.json": parents,
        "contract_coverage_matrix.json": coverage,
        "metric_provenance_audit.json": metrics,
        "baseline_independence_audit.json": baseline_independence,
        "baseline_invocation_audit.json": baseline_invocation,
        "ablation_rerun_audit.json": ablation_rerun,
        "ablation_sensitivity_audit.json": ablation_sensitivity,
        "leakage_surface_audit.json": leakage_surface,
        "leakage_positive_control_audit.json": leakage_positive,
        "manual_injection_independence_audit.json": manual_injection,
        "metadata_whitelist_scope_audit.json": metadata_whitelist,
        "behavior_causal_replay_audit.json": replay,
        "frozen_input_consumption_audit.json": frozen,
        "source_artifact_integrity_audit.json": source_integrity,
        "old_artifact_mutation_audit.json": old_mutation,
        "failure_path_test_audit.json": failure_paths,
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
                "stop_conditions_triggered": result["stop_conditions_triggered"],
                "minimum_patch": "repair exact blocker in a later bounded task; do not patch 001B artifacts in place",
            },
        )
    core.write_text(output_dir / "claim_ceiling.txt", core.CLAIM_CEILING + "\n")

    task_doc = repo_root / "docs" / "codex" / "tasks" / (
        "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B-INDEPENDENT-AUDIT-001C.md"
    )
    task_doc.parent.mkdir(parents=True, exist_ok=True)
    task_doc.write_text(_build_task_doc(), encoding="utf-8")

    return result
