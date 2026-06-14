import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001B"
PARENT_TASK_ID = "NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001B"
PARENT_SLUG = "next_surface_admission_manifest_instantiation_001b"
GAP_REPAIR_TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001A"
CLAIM_CEILING = "surface-admission authorization hygiene only"


def _validator():
    from future_surface_admission_authorization_template_001a import validator

    return validator


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _parent_manifest_artifact():
    return _load_json(ROOT / "artifacts" / PARENT_SLUG / "manifest.json")


def _parent_manifest_for_repaired_validator():
    validator = _validator()
    manifest = _parent_manifest_artifact()
    manifest["authorization_validator"]["code_path_hash"] = validator._source_hash()
    validator._refresh_manifest_hash(manifest)
    return manifest


def _decision_for(manifest):
    validator = _validator()
    template = validator.build_authorization_manifest_template(ROOT)
    enforcement = validator.validate_enforcement_artifacts(ROOT)
    return validator.validate_authorization_manifest(manifest, template, enforcement)


def _refresh(manifest):
    validator = _validator()
    validator._refresh_manifest_hash(manifest)
    return manifest


def _without_gap_dependency():
    manifest = _parent_manifest_for_repaired_validator()
    manifest["dependencies"] = [
        dependency
        for dependency in manifest["dependencies"]
        if dependency.get("task_id") != GAP_REPAIR_TASK_ID
    ]
    return _refresh(manifest)


def test_parent_001b_manifest_remains_authorized_with_full_dependency_chain():
    decision = _decision_for(_parent_manifest_for_repaired_validator())

    assert decision["authorization_decision"] == "authorized"
    assert decision["reasons_fired"] == []
    assert decision["validator_gap_repair_dependency_required"] is True
    assert decision["claim_ceiling"] == CLAIM_CEILING


def test_repaired_validator_blocks_observed_remove_gap_repair_dependency_ablation():
    decision = _decision_for(_without_gap_dependency())

    assert decision["authorization_decision"] == "blocked"
    assert "missing_validator_gap_repair_dependency" in decision["reasons_fired"]
    assert decision["validator_gap_repair_dependency_required"] is False


def test_repaired_validator_requires_structural_dependency_not_free_text():
    manifest = _without_gap_dependency()
    manifest["notes"] = (
        "This manifest mentions "
        "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001A "
        "in narrative only."
    )
    manifest["evidence_citations"].append(
        {
            "artifact_id": GAP_REPAIR_TASK_ID,
            "claim": "sealed validator gap-repair dependency only",
        }
    )
    _refresh(manifest)

    decision = _decision_for(manifest)

    assert decision["authorization_decision"] == "blocked"
    assert "missing_validator_gap_repair_dependency" in decision["reasons_fired"]


def test_repaired_validator_blocks_alias_and_non_enforced_gap_dependency_entries():
    manifest = _parent_manifest_for_repaired_validator()
    for dependency in manifest["dependencies"]:
        if dependency.get("task_id") == GAP_REPAIR_TASK_ID:
            dependency["task_id"] = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001A-ALIAS"
    _refresh(manifest)
    alias_decision = _decision_for(manifest)

    manifest = _parent_manifest_for_repaired_validator()
    for dependency in manifest["dependencies"]:
        if dependency.get("task_id") == GAP_REPAIR_TASK_ID:
            dependency["required"] = False
    _refresh(manifest)
    non_enforced_decision = _decision_for(manifest)

    assert alias_decision["authorization_decision"] == "blocked"
    assert "missing_validator_gap_repair_dependency" in alias_decision["reasons_fired"]
    assert non_enforced_decision["authorization_decision"] == "blocked"
    assert "missing_validator_gap_repair_dependency" in non_enforced_decision["reasons_fired"]


def test_repaired_validator_blocks_mutated_gap_dependency_contract_fields():
    manifest = _parent_manifest_for_repaired_validator()
    for dependency in manifest["dependencies"]:
        if dependency.get("task_id") == GAP_REPAIR_TASK_ID:
            dependency["required_verdict"] = "wrong_verdict"
    _refresh(manifest)
    wrong_verdict = _decision_for(manifest)

    manifest = _parent_manifest_for_repaired_validator()
    for dependency in manifest["dependencies"]:
        if dependency.get("task_id") == GAP_REPAIR_TASK_ID:
            dependency["dependency_type"] = "narrative_reference_only"
    _refresh(manifest)
    wrong_type = _decision_for(manifest)

    manifest = _parent_manifest_for_repaired_validator()
    for dependency in manifest["dependencies"]:
        if dependency.get("task_id") == GAP_REPAIR_TASK_ID:
            dependency["artifact_id"] = "future_surface_admission_authorization_template_001a"
    _refresh(manifest)
    wrong_artifact = _decision_for(manifest)

    assert wrong_verdict["authorization_decision"] == "blocked"
    assert "validator_gap_repair_dependency_mismatch" in wrong_verdict["reasons_fired"]
    assert wrong_type["authorization_decision"] == "blocked"
    assert "validator_gap_repair_dependency_mismatch" in wrong_type["reasons_fired"]
    assert wrong_artifact["authorization_decision"] == "blocked"
    assert "validator_gap_repair_dependency_mismatch" in wrong_artifact["reasons_fired"]


def test_repair_runner_emits_gap_closure_artifacts(tmp_path):
    runner_path = (
        ROOT
        / "artifacts"
        / "future_surface_admission_authorization_validator_gap_repair_001b"
        / "run_validator_gap_repair_001b.py"
    )
    assert runner_path.exists()

    import importlib.util

    spec = importlib.util.spec_from_file_location("run_validator_gap_repair_001b", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    out = tmp_path / "repair_001b"
    result = module.run(ROOT, output_dir=out, write_report=False)

    assert result["task_id"] == TASK_ID
    assert result["producer_function"] == "validate_authorization_manifest"
    assert result["parent_blocker_task"] == PARENT_TASK_ID
    assert result["observed_gap"] == "remove_validator_gap_repair_dependency_authorized"
    assert result["repair_result"] == "closed"
    assert result["verdict"] == "future_surface_admission_authorization_validator_gap_repair_001b_pass"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["mechanism_execution"] is False
    assert result["mainline_integration"] is False
    assert result["negative_controls_all_blocked"] is True
    assert result["ablation_controls_all_blocked"] is True
    assert result["before_after_gap_contrast"]["before"]["validator_decision"] == "authorized"
    assert result["before_after_gap_contrast"]["after"]["validator_decision"] == "blocked"

    expected_files = {
        "result.json",
        "readback.json",
        "trace.json",
        "ablation_results.json",
        "negative_controls.json",
        "before_after_gap_contrast.json",
        "claim_ceiling.txt",
    }
    assert expected_files == {path.name for path in out.iterdir()}

    ablations = _load_json(out / "ablation_results.json")
    negatives = _load_json(out / "negative_controls.json")
    readback = _load_json(out / "readback.json")
    trace = _load_json(out / "trace.json")

    assert ablations["blocked_ablation_count"] == 9
    assert len(ablations["ablations"]) == 9
    assert negatives["blocked_control_count"] == 6
    assert len(negatives["controls"]) == 6
    assert readback["producer_function"] == "validate_authorization_manifest"
    assert readback["serialized_manifest"]["task_id"] == PARENT_TASK_ID
    assert trace["events"]
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING
