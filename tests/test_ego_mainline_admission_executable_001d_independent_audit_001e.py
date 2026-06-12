import hashlib
import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001D-INDEPENDENT-AUDIT-001E"
VERDICT_BLOCK_METRIC_PROVENANCE = (
    "ego_mainline_admission_executable_001d_independent_audit_001e_block_metric_provenance_gap"
)
CLAIM_CEILING = (
    "bounded independent audit evidence for 001D baseline-legal-input repair "
    "under synthetic / controlled conditions only"
)
ARTIFACT_DIR = ROOT / "artifacts" / "ego_mainline_admission_executable_001d_independent_audit_001e"

REQUIRED_ARTIFACTS = {
    "result.json",
    "parent_anchor_verification.json",
    "exact_blocker_repair_audit.json",
    "baseline_legal_input_audit.json",
    "baseline_equivalent_label_leakage_audit.json",
    "baseline_runtime_access_guard_audit.json",
    "baseline_static_scan_audit.json",
    "baseline_invocation_audit.json",
    "baseline_independence_audit.json",
    "failure_path_control_audit.json",
    "metric_provenance_audit.json",
    "ablation_revalidation_audit.json",
    "leakage_revalidation_audit.json",
    "manual_injection_revalidation_audit.json",
    "metadata_whitelist_scope_audit.json",
    "behavior_causal_replay_audit.json",
    "frozen_input_consumption_audit.json",
    "source_artifact_integrity_audit.json",
    "old_artifact_mutation_audit.json",
    "negative_evidence_preservation_audit.json",
    "claim_ceiling_audit.json",
    "scope_leak_audit.json",
    "audit_finding_inventory.json",
    "blocker_report.json",
    "claim_ceiling.txt",
}


def _module():
    return importlib.import_module(
        "ego_mainline_admission_executable_001d_independent_audit_001e.runner"
    )


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _hash_tree(path: Path) -> dict[str, str]:
    hashes = {}
    for file in sorted(path.rglob("*")):
        if file.is_file():
            hashes[str(file.relative_to(path)).replace("\\", "/")] = hashlib.sha256(file.read_bytes()).hexdigest()
    return hashes


def test_independent_audit_blocks_on_inherited_metric_provenance_gap(tmp_path):
    runner = _module()
    out = tmp_path / "audit"

    result = runner.run_audit(repo_root=ROOT, output_dir=out, verify_remote=False)
    metrics = _read_json(out / "metric_provenance_audit.json")
    findings = _read_json(out / "audit_finding_inventory.json")

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == VERDICT_BLOCK_METRIC_PROVENANCE
    assert result["bounded_pass"] is False
    assert "metric_provenance_gap" in result["stop_conditions_triggered"]
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert metrics["all_verdict_metrics_have_callable_provenance"] is False
    assert metrics["missing_required_fields"]
    assert any(
        finding["finding_id"] == "metric_provenance_gap"
        and finding["severity"] == "blocker"
        for finding in findings["findings"]
    )


def test_baseline_repair_dimensions_are_independently_audited(tmp_path):
    runner = _module()
    out = tmp_path / "audit"

    result = runner.run_audit(repo_root=ROOT, output_dir=out, verify_remote=False)
    exact = _read_json(out / "exact_blocker_repair_audit.json")
    legal = _read_json(out / "baseline_legal_input_audit.json")
    equivalent = _read_json(out / "baseline_equivalent_label_leakage_audit.json")
    guard = _read_json(out / "baseline_runtime_access_guard_audit.json")
    static_scan = _read_json(out / "baseline_static_scan_audit.json")
    invocation = _read_json(out / "baseline_invocation_audit.json")
    independence = _read_json(out / "baseline_independence_audit.json")

    assert exact["001d_repair_scope_exact"] is True
    assert exact["001c_blocker_preserved"] is True
    assert legal["baseline_legal_input_schema_valid"] is True
    assert legal["baseline_output_rows_generated_after_legal_filtering"] is True
    assert equivalent["equivalent_verifier_labels_excluded"] is True
    assert equivalent["sanitized_derivative_leakage_detected"] is False
    assert guard["baseline_runtime_guard_complete"] is True
    assert guard["forbidden_field_negative_control_fail_able"] is True
    assert guard["equivalent_label_negative_control_fail_able"] is True
    assert static_scan["baseline_static_scan_valid"] is True
    assert invocation["all_required_baselines_invoked"] is True
    assert invocation["baseline_outputs_exist_before_aggregation"] is True
    assert independence["baseline_independence_verified"] is True
    assert result["baseline_legal_input_audit_result"]["baseline_legal_input_schema_valid"] is True


def test_failure_path_revalidation_and_mutation_audits_are_machine_readable(tmp_path):
    runner = _module()
    old_001b = ROOT / "artifacts" / "ego_mainline_admission_executable_001b"
    old_001c = ROOT / "artifacts" / "ego_mainline_admission_executable_001b_independent_audit_001c"
    old_001d = ROOT / "artifacts" / "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d"
    before = {
        "001b": _hash_tree(old_001b),
        "001c": _hash_tree(old_001c),
        "001d": _hash_tree(old_001d),
    }
    out = tmp_path / "audit"

    result = runner.run_audit(repo_root=ROOT, output_dir=out, verify_remote=False)
    failure = _read_json(out / "failure_path_control_audit.json")
    ablation = _read_json(out / "ablation_revalidation_audit.json")
    leakage = _read_json(out / "leakage_revalidation_audit.json")
    manual = _read_json(out / "manual_injection_revalidation_audit.json")
    whitelist = _read_json(out / "metadata_whitelist_scope_audit.json")
    replay = _read_json(out / "behavior_causal_replay_audit.json")
    frozen = _read_json(out / "frozen_input_consumption_audit.json")
    mutation = _read_json(out / "old_artifact_mutation_audit.json")

    assert failure["baseline_non_invocation_failure_control_verified"] is True
    assert failure["missing_same_surface_positive_control_failure_control_verified"] is True
    assert ablation["ablation_revalidation_verified"] is True
    assert leakage["leakage_revalidation_verified"] is True
    assert manual["manual_injection_independence_verified"] is True
    assert whitelist["metadata_whitelist_surface_scoped"] is True
    assert replay["behavior_causal_replay_verified"] is True
    assert frozen["frozen_inputs_consumed"] is True
    assert mutation["old_001b_artifacts_not_modified"] is True
    assert mutation["old_001c_artifacts_not_modified"] is True
    assert mutation["old_001d_artifacts_not_modified"] is True
    assert _hash_tree(old_001b) == before["001b"]
    assert _hash_tree(old_001c) == before["001c"]
    assert _hash_tree(old_001d) == before["001d"]
    assert result["old_artifact_mutation_result"]["old_001d_artifacts_not_modified"] is True


def test_materialized_audit_directory_contains_required_artifacts_and_boundaries():
    runner = _module()

    result = runner.run_audit(repo_root=ROOT, output_dir=ARTIFACT_DIR, verify_remote=True)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING
    assert _read_json(ARTIFACT_DIR / "result.json")["verdict"] == VERDICT_BLOCK_METRIC_PROVENANCE
    assert result["artifact_dir"] == "artifacts/ego_mainline_admission_executable_001d_independent_audit_001e"
    assert result["parent_anchors_verified"] is True
    assert result["scope_claim_ceiling_result"]["no_Ego_repo_modification"] is True
    assert result["scope_claim_ceiling_result"]["no_runtime_or_product_work"] is True
