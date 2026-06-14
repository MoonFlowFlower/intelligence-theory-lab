import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001C"
TASK_SLUG = "next_surface_admission_manifest_instantiation_001c"
CLAIM_CEILING = "surface-admission authorization hygiene only"
PROPOSED_DIRECTION = (
    "Minimal non-candidate surface-admission preflight for a future "
    "mechanism-family direction"
)
PARENT_BLOCKER_TASK = "NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001B"
PARENT_REPAIR_TASK = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001B"
EXPECTED_FILES = {
    "manifest.json",
    "validator_readback.json",
    "trace.json",
    "trace.jsonl",
    "ablation_results.json",
    "negative_controls.json",
    "dependency_structure_controls.json",
    "result.json",
    "claim_ceiling.txt",
}


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_runner():
    runner_path = ROOT / "artifacts" / TASK_SLUG / "run_manifest_instantiation_001c.py"
    assert runner_path.exists()
    spec = importlib.util.spec_from_file_location("run_manifest_instantiation_001c", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_runner_preserves_001c_validator_gap_blocker_without_validator_edits(tmp_path):
    runner = _load_runner()
    output_dir = tmp_path / TASK_SLUG

    result = runner.run(ROOT, output_dir=output_dir, write_report=False)

    assert result["task_id"] == TASK_ID
    assert result["producer_function"] == "validate_authorization_manifest"
    assert result["parent_blocker_task"] == PARENT_BLOCKER_TASK
    assert result["parent_repair_task"] == PARENT_REPAIR_TASK
    assert result["parent_repair_commit"] == "5a5442d318620f97ee3029a2a6898cffbf465f2d"
    assert result["parent_repair_tag"] == (
        "remote-anchor-future-surface-admission-authorization-validator-gap-repair-001b-5a5442d"
    )
    assert result["verdict"] == "blocked_validator_gap_repair_001b_dependency_not_enforced"
    assert result["decision"] == "later_surface_admission_task_card_may_not_be_drafted"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["mechanism_execution"] is False
    assert result["mainline_integration"] is False
    assert result["enabled_status"] == "local offline validator invocation only"
    assert result["validator_authorization_decision"] == "authorized"
    assert result["negative_controls_all_blocked"] is True
    assert result["ablation_controls_all_blocked"] is False
    assert result["dependency_structure_controls_all_blocked"] is False
    assert result["stop_conditions_triggered"] == [
        "validator_returned_unexpected_authorization_for_validator_gap_repair_001b_dependency_ablation",
        "validator_returned_unexpected_authorization_for_validator_gap_repair_001b_dependency_structure_controls",
    ]
    assert result["auto_remote_anchor"]["permitted"] is False

    assert EXPECTED_FILES == {path.name for path in output_dir.iterdir()}
    assert (output_dir / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING

    manifest = _load_json(output_dir / "manifest.json")
    readback = _load_json(output_dir / "validator_readback.json")
    negative_controls = _load_json(output_dir / "negative_controls.json")
    ablations = _load_json(output_dir / "ablation_results.json")
    dependency_controls = _load_json(output_dir / "dependency_structure_controls.json")
    trace = _load_json(output_dir / "trace.json")

    dependency_ids = {dependency["task_id"] for dependency in manifest["dependencies"]}
    assert manifest["task_id"] == TASK_ID
    assert manifest["proposed_surface_admission_direction"] == PROPOSED_DIRECTION
    assert manifest["scope_lock"] == "later_task_card_drafting_only"
    assert manifest["scope"]["later_task_card_only"] is True
    assert manifest["scope"]["execution_scope_opened"] is False
    assert manifest["parent_blocker_task"] == PARENT_BLOCKER_TASK
    assert manifest["parent_repair_task"] == PARENT_REPAIR_TASK
    assert {
        "SURFACE-ADMISSION-CONTRACT-HARDENING-001A",
        "SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A",
        "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-TEMPLATE-001A",
        "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001A",
        PARENT_BLOCKER_TASK,
        PARENT_REPAIR_TASK,
    }.issubset(dependency_ids)
    assert all(
        surface in manifest["invalid_evidence_ban"]["banned_as_mechanism_evidence"]
        for surface in [
            "COMPOSITE-CTSR pass-chain",
            "CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A",
            "ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A",
        ]
    )

    assert readback["validator_decision"]["authorization_decision"] == "authorized"
    assert readback["validator_decision"]["reasons_fired"] == []
    assert readback["manifest_hash"] == result["manifest_hash"]
    assert readback["actual_validator_code_path_hash"] == result["actual_validator_code_path_hash"]
    assert readback["producer_function"] == "validate_authorization_manifest"

    assert negative_controls["blocked_control_count"] == 6
    assert len(negative_controls["controls"]) == 6
    assert negative_controls["all_controls_blocked"] is True
    assert all(control["blocked"] for control in negative_controls["controls"])

    ablation_by_id = {ablation["ablation_id"]: ablation for ablation in ablations["ablations"]}
    assert ablations["blocked_ablation_count"] == 9
    assert len(ablations["ablations"]) == 10
    assert ablation_by_id["remove_validator_gap_repair_001b_dependency"]["blocked"] is False
    assert (
        ablation_by_id["remove_validator_gap_repair_001b_dependency"]["validator_decision"]
        == "authorized"
    )
    assert (
        ablation_by_id["remove_validator_gap_repair_001b_dependency"]["unexpected_authorization"]
        is True
    )
    assert ablation_by_id["remove_validator_gap_repair_001a_dependency"]["blocked"] is True

    assert dependency_controls["blocked_control_count"] == 0
    assert len(dependency_controls["controls"]) == 4
    assert dependency_controls["all_controls_blocked"] is False
    assert {
        control["control_id"]
        for control in dependency_controls["controls"]
        if control["unexpected_authorization"]
    } == {
        "validator_gap_repair_001b_dependency_alias",
        "validator_gap_repair_001b_dependency_free_text_only",
        "validator_gap_repair_001b_dependency_non_enforced_metadata_only",
        "validator_gap_repair_001b_replaced_with_001a_only",
    }

    assert trace["events"][0]["event"] == "manifest_instantiated"
    assert any(event["event"] == "validator_invoked" for event in trace["events"])
    assert any(event["event"] == "dependency_structure_control_invoked" for event in trace["events"])
    assert any(event["event"] == "stop_condition_triggered" for event in trace["events"])


def test_default_artifacts_and_report_preserve_001c_blocker_boundary():
    artifact_dir = ROOT / "artifacts" / TASK_SLUG
    report_path = ROOT / "docs" / "research" / f"{TASK_ID}.md"

    assert EXPECTED_FILES.issubset({path.name for path in artifact_dir.iterdir()})
    assert report_path.exists()

    result = _load_json(artifact_dir / "result.json")
    manifest = _load_json(artifact_dir / "manifest.json")
    ablations = _load_json(artifact_dir / "ablation_results.json")
    dependency_controls = _load_json(artifact_dir / "dependency_structure_controls.json")
    report = report_path.read_text(encoding="utf-8")

    assert result["verdict"] == "blocked_validator_gap_repair_001b_dependency_not_enforced"
    assert result["decision"] == "later_surface_admission_task_card_may_not_be_drafted"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["what_this_does_not_prove"]
    assert manifest["proposed_surface_admission_direction"] == PROPOSED_DIRECTION
    assert any(
        ablation["ablation_id"] == "remove_validator_gap_repair_001b_dependency"
        and ablation["unexpected_authorization"] is True
        for ablation in ablations["ablations"]
    )
    assert any(control["unexpected_authorization"] for control in dependency_controls["controls"])
    assert "Validator gap blocker" in report
    assert "later concrete surface-admission task card may not be drafted" in report
    assert CLAIM_CEILING in report
