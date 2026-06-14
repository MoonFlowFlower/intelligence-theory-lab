import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001B"
TASK_SLUG = "next_surface_admission_manifest_instantiation_001b"
CLAIM_CEILING = "surface-admission authorization hygiene only"
PROPOSED_DIRECTION = (
    "Minimal non-candidate surface-admission preflight for a future "
    "mechanism-family direction"
)
GAP_REPAIR_TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001A"
REQUIRED_FILES = {
    "manifest.json",
    "validator_readback.json",
    "trace.json",
    "trace.jsonl",
    "ablation_results.json",
    "negative_controls.json",
    "result.json",
    "claim_ceiling.txt",
}


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_runner():
    runner_path = ROOT / "artifacts" / TASK_SLUG / "run_manifest_instantiation_001b.py"
    assert runner_path.exists()
    spec = importlib.util.spec_from_file_location("run_manifest_instantiation_001b", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_runner_preserves_validator_gap_dependency_ablation_blocker(tmp_path):
    runner = _load_runner()
    output_dir = tmp_path / TASK_SLUG

    result = runner.run(ROOT, output_dir=output_dir)

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == "blocked_validator_gap_repair_dependency_ablation_authorized"
    assert result["decision"] == "later_task_card_drafting_not_authorized"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["mechanism_execution"] is False
    assert result["mainline_integration"] is False
    assert result["enabled_status"] == "local offline validator invocation only"
    assert result["producer_function"] == "validate_authorization_manifest"
    assert "validator_returned_unexpected_authorization_for_validator_gap_repair_dependency_ablation" in result[
        "stop_conditions_triggered"
    ]
    assert result["auto_remote_anchor"]["permitted"] is False
    assert result["auto_remote_anchor"]["decision"] == "conditional_not_completed"

    assert REQUIRED_FILES == {path.name for path in output_dir.iterdir()}
    assert (output_dir / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING

    manifest = _load_json(output_dir / "manifest.json")
    readback = _load_json(output_dir / "validator_readback.json")
    negative_controls = _load_json(output_dir / "negative_controls.json")
    ablations = _load_json(output_dir / "ablation_results.json")
    trace = _load_json(output_dir / "trace.json")
    trace_jsonl = [
        json.loads(line)
        for line in (output_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert manifest["task_id"] == TASK_ID
    assert manifest["proposed_surface_admission_direction"] == PROPOSED_DIRECTION
    assert manifest["scope"]["later_task_card_only"] is True
    assert manifest["scope"]["execution_scope_opened"] is False
    assert {dependency["task_id"] for dependency in manifest["dependencies"]}.issuperset(
        {
            "SURFACE-ADMISSION-CONTRACT-HARDENING-001A",
            "SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A",
            "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-TEMPLATE-001A",
            GAP_REPAIR_TASK_ID,
        }
    )

    assert readback["validator_decision"]["authorization_decision"] == "authorized"
    assert readback["validator_decision"]["reasons_fired"] == []
    assert readback["manifest_hash"] == result["manifest_hash"]
    assert readback["validator_code_path_hash"] == result["validator_code_path_hash"]
    assert readback["producer_function"] == "validate_authorization_manifest"

    assert negative_controls["all_controls_blocked"] is True
    control_ids = {control["control_id"] for control in negative_controls["controls"]}
    assert {
        "missing_concrete_proposed_direction",
        "gate5_proposed_direction",
        "bridge_runtime_tournament_ego_mainline_proposed_direction",
        "old_invalid_surfaces_cited_as_mechanism_evidence",
        "mechanism_score_before_admission",
        "validator_repair_treated_as_mechanism_execution_authorization",
    }.issubset(control_ids)
    assert all(control["blocked"] for control in negative_controls["controls"])

    ablation_by_id = {ablation["ablation_id"]: ablation for ablation in ablations["ablations"]}
    assert ablations["all_required_ablations_blocked"] is False
    assert ablation_by_id["remove_validator_gap_repair_dependency"]["blocked"] is False
    assert (
        ablation_by_id["remove_validator_gap_repair_dependency"]["validator_decision"]
        == "authorized"
    )
    assert ablation_by_id["remove_validator_gap_repair_dependency"]["unexpected_authorization"] is True
    assert ablation_by_id["remove_concrete_proposed_direction"]["blocked"] is True
    assert ablation_by_id["remove_later_task_card_only_scope_lock"]["blocked"] is True
    assert ablation_by_id["remove_no_mechanism_score_clause"]["blocked"] is True
    assert ablation_by_id["remove_invalid_evidence_ban"]["blocked"] is True
    assert ablation_by_id["open_forbidden_scope"]["blocked"] is True

    assert trace["events"][0]["event"] == "manifest_instantiated"
    assert any(event["event"] == "validator_invoked" for event in trace["events"])
    assert any(event["event"] == "stop_condition_triggered" for event in trace["events"])
    assert trace["jsonl_trace_path"].endswith("trace.jsonl")
    assert {entry["event"] for entry in trace_jsonl}.issuperset(
        {
            "manifest_instantiated",
            "validator_invoked",
            "negative_control_invoked",
            "ablation_invoked",
            "stop_condition_triggered",
        }
    )


def test_default_artifacts_and_report_record_blocker_boundary():
    artifact_dir = ROOT / "artifacts" / TASK_SLUG
    report_path = ROOT / "docs" / "research" / f"{TASK_ID}.md"

    assert REQUIRED_FILES.issubset({path.name for path in artifact_dir.iterdir()})
    assert report_path.exists()

    result = _load_json(artifact_dir / "result.json")
    manifest = _load_json(artifact_dir / "manifest.json")
    ablations = _load_json(artifact_dir / "ablation_results.json")
    report = report_path.read_text(encoding="utf-8")

    assert result["verdict"] == "blocked_validator_gap_repair_dependency_ablation_authorized"
    assert result["decision"] == "later_task_card_drafting_not_authorized"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["what_this_does_not_prove"]
    assert manifest["proposed_surface_admission_direction"] == PROPOSED_DIRECTION
    assert any(
        ablation["ablation_id"] == "remove_validator_gap_repair_dependency"
        and ablation["unexpected_authorization"] is True
        for ablation in ablations["ablations"]
    )
    assert "Validator gap blocker" in report
    assert "later concrete surface-admission task card may not be drafted" in report
    assert CLAIM_CEILING in report
