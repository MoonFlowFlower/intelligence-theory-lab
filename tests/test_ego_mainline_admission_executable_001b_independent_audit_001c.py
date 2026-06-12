import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B-INDEPENDENT-AUDIT-001C"
VERDICT_BLOCK_BASELINE = (
    "ego_mainline_admission_executable_001b_independent_audit_001c_block_baseline_gap"
)
ARTIFACT_DIR = ROOT / "artifacts" / "ego_mainline_admission_executable_001b_independent_audit_001c"

REQUIRED_ARTIFACTS = {
    "result.json",
    "parent_anchor_verification.json",
    "contract_coverage_matrix.json",
    "metric_provenance_audit.json",
    "baseline_independence_audit.json",
    "baseline_invocation_audit.json",
    "ablation_rerun_audit.json",
    "ablation_sensitivity_audit.json",
    "leakage_surface_audit.json",
    "leakage_positive_control_audit.json",
    "manual_injection_independence_audit.json",
    "metadata_whitelist_scope_audit.json",
    "behavior_causal_replay_audit.json",
    "frozen_input_consumption_audit.json",
    "source_artifact_integrity_audit.json",
    "old_artifact_mutation_audit.json",
    "failure_path_test_audit.json",
    "negative_evidence_preservation_audit.json",
    "claim_ceiling_audit.json",
    "scope_leak_audit.json",
    "audit_finding_inventory.json",
    "blocker_report.json",
    "claim_ceiling.txt",
}


def _module():
    return importlib.import_module(
        "ego_mainline_admission_executable_001b_independent_audit_001c.runner"
    )


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_independent_audit_detects_baseline_verifier_label_consumption(tmp_path):
    runner = _module()
    out = tmp_path / "audit"

    result = runner.run_audit(repo_root=ROOT, output_dir=out, verify_remote=False)
    baseline = _read_json(out / "baseline_independence_audit.json")
    findings = _read_json(out / "audit_finding_inventory.json")

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == VERDICT_BLOCK_BASELINE
    assert result["bounded_pass"] is False
    assert "baseline_illegal_verifier_label_consumption" in result["stop_conditions_triggered"]
    assert baseline["baseline_independence_verified"] is False
    assert baseline["illegal_verifier_label_consumption_detected"] is True
    assert any(
        finding["finding_id"] == "baseline_illegal_verifier_label_consumption"
        and finding["severity"] == "blocker"
        for finding in findings["findings"]
    )


def test_audit_emits_required_artifacts_and_preserves_parent_boundaries(tmp_path):
    runner = _module()
    out = tmp_path / "audit"

    result = runner.run_audit(repo_root=ROOT, output_dir=out, verify_remote=False)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in out.iterdir()})
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == result["claim_ceiling"]
    assert result["authorization_flags"]["ego_repository_modification_authorized"] is False
    assert result["authorization_flags"]["ego_mainline_runtime_authorized"] is False
    assert result["authorization_flags"]["llm_rag_authorized"] is False
    assert result["claim_ceiling"] == (
        "bounded independent audit evidence for EGO-MAINLINE-ADMISSION-EXECUTABLE-001B "
        "under synthetic / controlled conditions only"
    )


def test_contract_metric_replay_and_failure_path_audits_are_machine_readable(tmp_path):
    runner = _module()
    out = tmp_path / "audit"

    result = runner.run_audit(repo_root=ROOT, output_dir=out, verify_remote=False)
    coverage = _read_json(out / "contract_coverage_matrix.json")
    metrics = _read_json(out / "metric_provenance_audit.json")
    replay = _read_json(out / "behavior_causal_replay_audit.json")
    failure_paths = _read_json(out / "failure_path_test_audit.json")

    assert coverage["all_contract_requirements_accounted_for"] is True
    assert coverage["complete_or_blocked_by_specific_findings"] is True
    assert metrics["all_verdict_metrics_have_callable_provenance"] is True
    assert metrics["literal_metric_detected"] is False
    assert replay["behavior_causal_replay_verified"] is True
    assert replay["serialized_state_causal_consumption_verified"] is True
    assert failure_paths["failure_path_tests_verified"] is False
    assert "baseline_non_invocation" in failure_paths["missing_failure_controls"]
    assert "missing_same_surface_positive_control" in failure_paths["missing_failure_controls"]
    assert failure_paths["tests_only_assert_pass"] is False
    assert result["metric_provenance_audit_result"]["all_verdict_metrics_have_callable_provenance"] is True


def test_written_artifact_run_uses_allowed_directory():
    runner = _module()

    result = runner.run_audit(repo_root=ROOT, output_dir=ARTIFACT_DIR, verify_remote=True)

    assert result["artifact_dir"] == "artifacts/ego_mainline_admission_executable_001b_independent_audit_001c"
    assert (ARTIFACT_DIR / "result.json").exists()
    assert _read_json(ARTIFACT_DIR / "result.json")["verdict"] == VERDICT_BLOCK_BASELINE
