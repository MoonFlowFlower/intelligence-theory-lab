import hashlib
import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EGO-MAINLINE-OLD-ARTIFACT-SIDE-EFFECT-GUARD-AND-REDUNDANCY-CONTRACT-REPAIR-001A"
ARTIFACT_DIR = ROOT / "artifacts" / "ego_mainline_old_artifact_side_effect_guard_and_redundancy_contract_repair_001a"
SIDE_EFFECT_ARTIFACT = (
    ROOT
    / "artifacts"
    / "ego_mainline_admission_executable_001d_metric_provenance_repair_001f"
    / "scope_leak_report.json"
)


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repair_runner():
    return importlib.import_module(
        "ego_mainline_old_artifact_side_effect_guard_and_redundancy_contract_repair_001a.runner"
    )


def test_temp_runs_reach_shared_validator_contracts_without_downstream_readback_block(tmp_path):
    reference = importlib.import_module("ego_mainline_admission_canonical_coverage_reference_001a.runner")
    alignment = importlib.import_module("ego_mainline_admission_task_card_alignment_001a.runner")

    ref_out = tmp_path / "reference"
    align_out = tmp_path / "alignment"
    ref_result = reference.run_reference_contract(repo_root=ROOT, output_dir=ref_out, verify_remote=False)
    align_result = alignment.run_alignment_contract(repo_root=ROOT, output_dir=align_out)

    assert ref_result["verdict"] == reference.VERDICT_PASS
    assert align_result["verdict"] == alignment.VERDICT_PASS
    assert ref_result["all_validators_passed"] is True
    assert align_result["all_validators_passed"] is True

    ref_names = [row["validator"] for row in ref_result["validators"]]
    align_names = [row["validator"] for row in align_result["validators"]]
    assert ref_names == [row["validator"] for row in reference.validate_reference_contract(_read_json(ref_out / "reference_contract.json"), reference._load_canonical_inputs(ROOT))]
    assert align_names == [row["validator"] for row in alignment.validate_alignment_contract(_read_json(align_out / "evidence_usage_contract.json"), _read_json(align_out / "post_bridge_boundary_resolution_report.json"))]


def test_old_artifact_side_effect_runner_uses_temp_output_and_preserves_scope_report(tmp_path):
    runner = importlib.import_module("ego_mainline_admission_executable_001d_metric_provenance_repair_001f.runner")
    before = _sha(SIDE_EFFECT_ARTIFACT)
    out = tmp_path / "repair_001f"

    result = runner.run_repair(repo_root=ROOT, output_dir=out, verify_remote=False)

    assert result["verdict"] == "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_pass"
    assert (out / "scope_leak_report.json").exists()
    assert _sha(SIDE_EFFECT_ARTIFACT) == before


def test_repair_runner_generates_computed_evidence_without_downstream_authorization(tmp_path):
    runner = _repair_runner()
    out = tmp_path / "repair_001a"

    result = runner.run_repair(repo_root=ROOT, output_dir=out, verify_remote=False, execute_full_pytest=False)

    assert result["task_id"] == TASK_ID
    assert result["verdict"] in {
        runner.VERDICT_PASS_WITH_RESIDUAL_BLOCKERS_CLASSIFIED,
        runner.VERDICT_BLOCKED_FULL_SUITE_NOT_OBSERVED,
        runner.VERDICT_PASS_FULL_SUITE_GREEN,
    }
    assert result["claim_ceiling"] == runner.CLAIM_CEILING
    assert result["old_artifact_side_effect_guard_result"]["old_sealed_artifacts_unchanged"] is True
    assert result["temp_run_vs_canonical_validator_equivalence"]["equivalent"] is True
    assert result["leakage_result"]["positive_control_detected"] is True
    assert result["replay_result"]["recomputed_from_serialized_state_and_observation"] is True
    assert result["replay_result"]["replay_matches_original_decision"] is True
    assert all(value is False for value in result["downstream_route_impact_after_repair"]["non_authorization_flags"].values())

    required = {
        "result.json",
        "anchor_readback.json",
        "before_repair_failure_reproduction.json",
        "repair_change_inventory.json",
        "shared_validator_contract_evidence.json",
        "temp_run_validator_equivalence_report.json",
        "old_artifact_write_guard_report.json",
        "side_effect_prevention_report.json",
        "before_after_hash_comparison.json",
        "isolated_rerun_report.json",
        "targeted_suite_report.json",
        "full_pytest_report.json",
        "residual_failure_classification.json",
        "downstream_route_impact_matrix.json",
        "baseline_comparison.json",
        "ablation_report.json",
        "leakage_scan_report.json",
        "replay_report.json",
        "computed_evidence_provenance.json",
        "repair_state.json",
        "claim_ceiling.txt",
        "future_task_recommendation.txt",
        "rollback_plan.txt",
    }
    assert required.issubset({path.name for path in out.iterdir()})

    provenance = _read_json(out / "computed_evidence_provenance.json")
    assert provenance["all_reported_values_have_callable_provenance"] is True
    assert provenance["static_literal_or_unconditional_pass_detected"] is False
