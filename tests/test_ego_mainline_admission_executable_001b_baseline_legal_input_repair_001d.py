import hashlib
import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B-BASELINE-LEGAL-INPUT-REPAIR-001D"
VERDICT_PASS = "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d_pass"
CLAIM_CEILING = (
    "bounded baseline-legal-input repair evidence for "
    "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B under synthetic / controlled conditions only"
)
ARTIFACT_DIR = ROOT / "artifacts" / "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d"

REQUIRED_ARTIFACTS = {
    "result.json",
    "parent_anchor_verification.json",
    "repair_scope_manifest.json",
    "baseline_legal_input_schema.json",
    "baseline_forbidden_field_inventory.json",
    "baseline_static_forbidden_reference_scan.json",
    "baseline_legal_input_access_log.json",
    "baseline_forbidden_access_report.json",
    "baseline_invocation_report.json",
    "baseline_output_rows.json",
    "baseline_comparison_report.json",
    "baseline_non_invocation_failure_control.json",
    "same_surface_positive_control_failure_control.json",
    "leakage_revalidation_report.json",
    "metadata_whitelist_scope_revalidation.json",
    "manual_injection_revalidation_report.json",
    "ablation_revalidation_report.json",
    "behavior_causal_replay_report.json",
    "frozen_input_consumption_report.json",
    "metric_provenance.json",
    "source_artifact_integrity_report.json",
    "old_artifact_mutation_report.json",
    "negative_evidence_preservation_report.json",
    "claim_ceiling.txt",
}

FORBIDDEN_FIELDS = {
    "verifier_expected_action_id",
    "expected_action_id",
    "gold_action",
    "label",
    "later_action_label",
    "future_observation",
    "future_partner_response",
    "post_hoc_metric",
    "verifier_only_field",
    "test_only_schema_path",
    "answer_key",
    "oracle_action",
}


def _module():
    return importlib.import_module(
        "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d.runner"
    )


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _hash_tree(path: Path) -> dict[str, str]:
    hashes = {}
    for file in sorted(path.rglob("*")):
        if file.is_file():
            hashes[str(file.relative_to(path)).replace("\\", "/")] = hashlib.sha256(file.read_bytes()).hexdigest()
    return hashes


def test_repair_run_passes_exact_scope_and_preserves_parent_blockers(tmp_path):
    runner = _module()
    out = tmp_path / "repair"

    result = runner.run_repair(repo_root=ROOT, output_dir=out, verify_remote=False)
    negative = _read_json(out / "negative_evidence_preservation_report.json")
    scope = _read_json(out / "repair_scope_manifest.json")

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == VERDICT_PASS
    assert result["bounded_pass"] is True
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["stop_conditions_triggered"] == []
    assert negative["001c_blocker_preserved"] is True
    assert negative["001b_historical_block_status_preserved"] is True
    assert negative["001c_verdict"] == "ego_mainline_admission_executable_001b_independent_audit_001c_block_baseline_gap"
    assert scope["repair_scope_exact"] is True
    assert scope["repaired_blockers"] == [
        "baseline_illegal_verifier_label_consumption",
        "baseline_non_invocation",
        "missing_same_surface_positive_control",
    ]


def test_baseline_schema_guard_blocks_forbidden_fields_and_logs_legal_access(tmp_path):
    runner = _module()
    out = tmp_path / "repair"

    result = runner.run_repair(repo_root=ROOT, output_dir=out, verify_remote=False)
    schema = _read_json(out / "baseline_legal_input_schema.json")
    access_log = _read_json(out / "baseline_legal_input_access_log.json")
    forbidden_report = _read_json(out / "baseline_forbidden_access_report.json")
    static_scan = _read_json(out / "baseline_static_forbidden_reference_scan.json")

    assert set(schema["forbidden_fields"]) >= FORBIDDEN_FIELDS
    assert not set(schema["allowed_fields"]).intersection(FORBIDDEN_FIELDS)
    assert "verifier_expected_action_id" not in schema["allowed_fields"]
    assert access_log["baseline_runtime_access_guard_passed"] is True
    assert access_log["total_access_count"] > 0
    assert all(not row["forbidden"] for row in access_log["accesses"])
    assert all("verifier_expected_action_id" not in row["accessed_fields"] for row in access_log["per_baseline"])
    assert forbidden_report["baseline_receives_verifier_expected_action_id"] is False
    assert forbidden_report["baseline_accesses_forbidden_field"] is False
    assert forbidden_report["equivalent_verifier_label_leak_detected"] is False
    assert static_scan["baseline_static_forbidden_reference_scan_passed"] is True
    assert static_scan["forbidden_references"] == []
    assert result["baseline_legal_input_result"]["baseline_runtime_access_guard_passed"] is True


def test_baselines_are_invoked_outputs_exist_and_failure_controls_can_fail(tmp_path):
    runner = _module()
    out = tmp_path / "repair"

    result = runner.run_repair(repo_root=ROOT, output_dir=out, verify_remote=False)
    invocation = _read_json(out / "baseline_invocation_report.json")
    rows = _read_json(out / "baseline_output_rows.json")
    comparison = _read_json(out / "baseline_comparison_report.json")
    non_invocation = _read_json(out / "baseline_non_invocation_failure_control.json")
    missing_positive = _read_json(out / "same_surface_positive_control_failure_control.json")

    assert invocation["all_required_baselines_invoked"] is True
    assert invocation["baseline_outputs_exist_before_aggregation"] is True
    assert invocation["baseline_outputs_are_not_static_dictionaries"] is True
    assert rows["output_rows"]
    assert all("expected_action_id" not in row for row in rows["output_rows"])
    assert comparison["baseline_comparison_passed"] is True
    assert comparison["old_001b_baseline_outputs_reused"] is False
    assert non_invocation["baseline_non_invocation_failure_control_passed"] is True
    assert non_invocation["detected_failure_id"] == "baseline_non_invocation_detected"
    assert missing_positive["missing_same_surface_positive_control_failure_control_passed"] is True
    assert missing_positive["detected_failure_id"] == "missing_same_surface_positive_control_detected"
    assert result["baseline_invocation_result"]["all_required_baselines_invoked"] is True


def test_recomputed_revalidations_metric_provenance_and_scope_controls(tmp_path):
    runner = _module()
    out = tmp_path / "repair"

    result = runner.run_repair(repo_root=ROOT, output_dir=out, verify_remote=False)
    metrics = _read_json(out / "metric_provenance.json")
    ablation = _read_json(out / "ablation_revalidation_report.json")
    leakage = _read_json(out / "leakage_revalidation_report.json")
    manual = _read_json(out / "manual_injection_revalidation_report.json")
    whitelist = _read_json(out / "metadata_whitelist_scope_revalidation.json")
    replay = _read_json(out / "behavior_causal_replay_report.json")
    frozen = _read_json(out / "frozen_input_consumption_report.json")

    assert metrics["all_verdict_metrics_have_callable_provenance"] is True
    assert metrics["no_literal_metrics"] is True
    assert metrics["no_static_metric_dictionaries"] is True
    assert metrics["no_copied_old_001b_results"] is True
    assert ablation["ablation_revalidation_passed"] is True
    assert ablation["reran_candidate_behavior"] is True
    assert leakage["leakage_revalidation_passed"] is True
    assert leakage["baseline_legal_input_guard_surface_scanned"] is True
    assert manual["manual_injection_revalidation_passed"] is True
    assert manual["production_injector_only"] is False
    assert whitelist["metadata_whitelist_surface_scoped"] is True
    assert replay["behavior_causal_replay_passed"] is True
    assert replay["hash_only_replay_for_behavior_claim"] is False
    assert frozen["frozen_inputs_consumed"] is True
    assert result["scope_claim_ceiling_result"]["no_scope_leak"] is True
    assert result["scope_claim_ceiling_result"]["no_claim_inflation"] is True
    assert result["scope_claim_ceiling_result"]["no_Ego_repo_modification"] is True


def test_old_001b_and_001c_artifacts_are_not_modified(tmp_path):
    runner = _module()
    old_001b = ROOT / "artifacts" / "ego_mainline_admission_executable_001b"
    old_001c = ROOT / "artifacts" / "ego_mainline_admission_executable_001b_independent_audit_001c"
    before_001b = _hash_tree(old_001b)
    before_001c = _hash_tree(old_001c)

    out = tmp_path / "repair"
    result = runner.run_repair(repo_root=ROOT, output_dir=out, verify_remote=False)
    mutation = _read_json(out / "old_artifact_mutation_report.json")

    assert _hash_tree(old_001b) == before_001b
    assert _hash_tree(old_001c) == before_001c
    assert mutation["old_001b_artifacts_not_modified"] is True
    assert mutation["old_001c_audit_artifacts_not_modified"] is True
    assert result["old_artifact_mutation_result"]["old_001b_artifacts_not_modified"] is True


def test_materialized_artifact_directory_contains_required_json_and_claim_ceiling():
    runner = _module()

    result = runner.run_repair(repo_root=ROOT, output_dir=ARTIFACT_DIR, verify_remote=True)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING
    assert _read_json(ARTIFACT_DIR / "result.json")["verdict"] == VERDICT_PASS
    assert result["artifact_dir"] == "artifacts/ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d"
