import copy
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001C"
SOURCE_001C_TASK_ID = "NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001C"
SOURCE_001C_SLUG = "next_surface_admission_manifest_instantiation_001c"
REQUIRED_001B_TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001B"
REQUIRED_001A_TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001A"
CLAIM_CEILING = "surface-admission authorization hygiene only"
RUNNER_SLUG = "future_surface_admission_authorization_validator_gap_repair_001c"
EXPECTED_RUNNER_FILES = {
    "ablation_results.json",
    "baseline_evidence.json",
    "claim_ceiling.txt",
    "dependency_structure_controls.json",
    "positive_controls.json",
    "readback.json",
    "replay_report.json",
    "result.json",
    "trace.json",
    "trace.jsonl",
}


def _validator():
    from future_surface_admission_authorization_template_001a import validator

    return validator


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_runner():
    runner_path = ROOT / "artifacts" / RUNNER_SLUG / "run_validator_gap_repair_001c.py"
    assert runner_path.exists()
    spec = importlib.util.spec_from_file_location("run_validator_gap_repair_001c", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _source_manifest_hash() -> str:
    validator = _validator()
    manifest = _load_json(ROOT / "artifacts" / SOURCE_001C_SLUG / "manifest.json")
    return validator._manifest_integrity_hash(manifest)


def _source_manifest_for_current_validator() -> dict:
    validator = _validator()
    manifest = _load_json(ROOT / "artifacts" / SOURCE_001C_SLUG / "manifest.json")
    manifest["authorization_validator"]["code_path_hash"] = validator._source_hash()
    validator._refresh_manifest_hash(manifest)
    return manifest


def _decision_for(manifest: dict) -> dict:
    validator = _validator()
    template = validator.build_authorization_manifest_template(ROOT)
    enforcement = validator.validate_enforcement_artifacts(ROOT)
    return validator.validate_authorization_manifest(manifest, template, enforcement)


def _refresh(manifest: dict) -> dict:
    validator = _validator()
    validator._refresh_manifest_hash(manifest)
    return manifest


def _without_001b_dependency() -> dict:
    manifest = _source_manifest_for_current_validator()
    manifest["dependencies"] = [
        dependency
        for dependency in manifest["dependencies"]
        if dependency.get("task_id") != REQUIRED_001B_TASK_ID
    ]
    return _refresh(manifest)


def _with_001b_dependency_replaced_by_alias() -> dict:
    manifest = _source_manifest_for_current_validator()
    for dependency in manifest["dependencies"]:
        if dependency.get("task_id") == REQUIRED_001B_TASK_ID:
            dependency["task_id"] = f"{REQUIRED_001B_TASK_ID}-ALIAS"
    return _refresh(manifest)


def _with_001b_dependency_in_narrative_only() -> dict:
    manifest = _without_001b_dependency()
    manifest["notes"] = (
        "Narrative-only reference to "
        "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001B."
    )
    return _refresh(manifest)


def _with_001b_dependency_in_metadata_only() -> dict:
    manifest = _without_001b_dependency()
    manifest["non_enforced_metadata"] = {
        "task_id": REQUIRED_001B_TASK_ID,
        "dependency_type": "sealed_validator_gap_repair_boundary",
        "required": True,
    }
    return _refresh(manifest)


def _with_001a_only_replacement() -> dict:
    manifest = _without_001b_dependency()
    assert any(
        dependency.get("task_id") == REQUIRED_001A_TASK_ID
        for dependency in manifest["dependencies"]
    )
    return _refresh(manifest)


def test_repair_001c_blocks_missing_validator_gap_repair_001b_dependency():
    assert _source_manifest_hash() == (
        "870b1eb33fdf3351d2beb31c98d102bb8ab7360fc92fb65d4cdfd130023c7dce"
    )

    valid_decision = _decision_for(_source_manifest_for_current_validator())
    ablated_decision = _decision_for(_without_001b_dependency())

    assert valid_decision["manifest_task_id"] == SOURCE_001C_TASK_ID
    assert valid_decision["authorization_decision"] == "authorized"
    assert ablated_decision["authorization_decision"] == "blocked"
    assert "missing_validator_gap_repair_dependency" in ablated_decision["reasons_fired"]
    assert REQUIRED_001B_TASK_ID in ablated_decision["required_validator_gap_repair_task_ids"]
    assert ablated_decision["validator_gap_repair_001b_dependency_required"] is False
    assert ablated_decision["claim_ceiling"] == CLAIM_CEILING


def test_repair_001c_blocks_dependency_structure_bypasses_for_001b():
    controls = {
        "alias_only": _with_001b_dependency_replaced_by_alias(),
        "narrative_only": _with_001b_dependency_in_narrative_only(),
        "metadata_only": _with_001b_dependency_in_metadata_only(),
        "001a_only_replacement": _with_001a_only_replacement(),
    }

    decisions = {control_id: _decision_for(manifest) for control_id, manifest in controls.items()}

    assert decisions
    for control_id, decision in decisions.items():
        assert decision["authorization_decision"] == "blocked", control_id
        assert "missing_validator_gap_repair_dependency" in decision["reasons_fired"], control_id
        assert decision["validator_gap_repair_001b_dependency_required"] is False, control_id
        assert decision["claim_ceiling"] == CLAIM_CEILING


def test_repair_001c_runner_emits_callable_evidence_and_replay(tmp_path):
    runner = _load_runner()
    output_dir = tmp_path / RUNNER_SLUG

    result = runner.run(ROOT, output_dir=output_dir, write_report=False)

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == "future_surface_admission_authorization_validator_gap_repair_001c_pass"
    assert result["current_layer"] == "engineering-governance / authorization-validator gap repair only"
    assert result["mainline_integration_status"] == "none"
    assert result["enabled_status"] == "local offline validator and tests only"
    assert result["source_001c_manifest_hash"] == (
        "870b1eb33fdf3351d2beb31c98d102bb8ab7360fc92fb65d4cdfd130023c7dce"
    )
    assert result["before_validator_code_path_hash"] == (
        "67f7c2e08a9ec95176bbaf9c98c2c88a8e1a13e06355cff3211dd7ffb1cebb01"
    )
    assert result["after_validator_code_path_hash"] == _validator()._source_hash()
    assert result["valid_manifest_authorized"] is True
    assert result["negative_controls_blocked_count"] == 6
    assert result["negative_controls_all_blocked"] is True
    assert result["ablation_controls_blocked_count"] == 10
    assert result["ablation_controls_all_blocked"] is True
    assert result["dependency_structure_controls_blocked_count"] == 4
    assert result["dependency_structure_controls_all_blocked"] is True
    assert result["positive_controls_all_passed"] is True
    assert result["replay_recomputation"]["all_recomputed_outcomes_match"] is True
    assert result["stop_conditions_triggered"] == []
    assert result["auto_remote_anchor"]["decision"] == "conditional_pending_commit_gate"
    assert result["claim_ceiling"] == CLAIM_CEILING

    assert EXPECTED_RUNNER_FILES.issubset({path.name for path in output_dir.iterdir()})
    assert (output_dir / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING

    baseline = _load_json(output_dir / "baseline_evidence.json")
    ablations = _load_json(output_dir / "ablation_results.json")
    dependency_controls = _load_json(output_dir / "dependency_structure_controls.json")
    positive_controls = _load_json(output_dir / "positive_controls.json")
    replay = _load_json(output_dir / "replay_report.json")
    trace_rows = [
        json.loads(line)
        for line in (output_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert baseline["pre_repair"]["validator_code_path_hash"] == result["before_validator_code_path_hash"]
    assert baseline["pre_repair"]["ablation_controls_blocked_count"] == 9
    assert baseline["pre_repair"]["dependency_structure_controls_blocked_count"] == 0
    assert baseline["pre_repair"]["unexpected_authorized_ablations"] == [
        "remove_validator_gap_repair_001b_dependency"
    ]
    assert ablations["blocked_ablation_count"] == 10
    assert len(ablations["ablations"]) == 10
    assert dependency_controls["blocked_control_count"] == 4
    assert len(dependency_controls["controls"]) == 4
    assert positive_controls["all_positive_controls_passed"] is True
    assert replay["all_recomputed_outcomes_match"] is True
    assert all("serialized_manifest" in row for row in trace_rows)
