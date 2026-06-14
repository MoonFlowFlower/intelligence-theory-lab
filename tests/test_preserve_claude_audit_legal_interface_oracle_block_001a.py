import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_DIR = "preserve_claude_audit_legal_interface_oracle_block_001a"
TASK_CARD_ID = "PRESERVE-CLAUDE-AUDIT-LEGAL-INTERFACE-ORACLE-BLOCK-001A"
REPORT_NAME = "PRESERVE-CLAUDE-AUDIT-LEGAL-INTERFACE-ORACLE-BLOCK-001A.md"

REQUIRED_ARTIFACTS = {
    "result.json",
    "legal_interface_oracle_report.json",
    "field_access_audit.json",
    "claude_audit_preservation.json",
    "downgrade_routing_record.json",
    "source_boundary_readback.json",
    "claim_ceiling.json",
    "forbidden_action_guard.json",
}


def _runner():
    module_path = SRC / TASK_DIR / "runner.py"
    assert module_path.exists(), "runner module not implemented"
    return importlib.import_module(f"{TASK_DIR}.runner")


def test_legal_interface_oracle_uses_only_allowed_fields_and_matches_majority_random_floor():
    runner = _runner()

    batch = runner.load_current_multi_seed_surface()
    oracle = runner.run_legal_interface_oracle(batch, run_id="unit_oracle_001")

    assert oracle["task_id"] == TASK_CARD_ID
    assert oracle["producer_function"] == "run_legal_interface_oracle"
    assert oracle["train_case_count"] == 80
    assert oracle["heldout_case_count"] == 80
    assert oracle["action_space"] == [
        "consolidate_trace",
        "defer_action",
        "inspect_boundary",
        "replan_memory",
    ]
    assert oracle["oracle_accuracy"] == 0.25
    assert oracle["majority_baseline_accuracy"] == 0.25
    assert oracle["oracle_minus_majority_delta"] == 0.0
    assert oracle["random_floor_accuracy"] == 0.25
    assert oracle["heldout_tuple_overlap_with_train_count"] == 0
    assert oracle["heldout_tuple_count"] == 80
    assert oracle["heldout_unique_tuple_count"] == 80
    assert oracle["train_tuple_conflict_count"] == 0
    assert oracle["surface_solvability_status"] == "legal_interface_random_or_inconclusive"
    assert oracle["recommended_route"] == "block_route_by_surface_or_baseline_failure"

    allowed = set(runner.ALLOWED_OBSERVATION_FIELDS)
    forbidden = set(runner.FORBIDDEN_PREDICTION_FIELDS)
    assert set(oracle["field_access_audit"]["prediction_fields_accessed"]) == allowed
    assert set(oracle["field_access_audit"]["forbidden_fields_checked"]) == forbidden
    assert oracle["field_access_audit"]["forbidden_prediction_fields_accessed"] == []
    assert oracle["prediction_input_policy"] == "declared_legal_observation_fields_only"
    assert oracle["ground_truth_policy"] == "scoring_only_recompute_from_serialized_state_after_plus_observation"


def test_oracle_positive_control_blocks_forbidden_answer_alias_access():
    runner = _runner()
    batch = runner.load_current_multi_seed_surface()

    audit = runner.build_field_access_audit(batch, include_positive_controls=True)

    assert audit["baseline_access_violations"] == {}
    assert audit["positive_controls"]["hidden_target_alias"]["blocked"] is True
    assert audit["positive_controls"]["hidden_target_alias"]["illegal_accesses"] == ["hidden.task_b_target_action"]
    assert audit["positive_controls"]["stored_answer_alias"]["blocked"] is True
    assert audit["positive_controls"]["stored_answer_alias"]["illegal_accesses"] == ["task_b.post_update_action"]
    assert audit["positive_controls"]["serialized_state_answer_alias"]["blocked"] is True
    assert audit["positive_controls"]["serialized_state_answer_alias"]["illegal_accesses"] == [
        "shared_state_update.serialized_state_after"
    ]


def test_claude_audit_is_preserved_as_negative_evidence_and_routes_to_block():
    runner = _runner()
    audit_text = (
        "Verdict: block_route_by_surface_or_baseline_failure\n"
        "legal interface oracle accuracy = 0.25 and majority = 0.25\n"
        "downgrade current surface robustness evidence to inconclusive\n"
    )

    preservation = runner.preserve_claude_audit(
        audit_text=audit_text,
        source_path="unit://claude-audit",
    )
    routing = runner.build_downgrade_routing_record(preservation, oracle_report={
        "oracle_accuracy": 0.25,
        "majority_baseline_accuracy": 0.25,
        "surface_solvability_status": "legal_interface_random_or_inconclusive",
    })

    assert preservation["producer_function"] == "preserve_claude_audit"
    assert preservation["negative_evidence_preserved"] is True
    assert preservation["source_sha256"]
    assert preservation["audit_text"] == audit_text
    assert preservation["audit_verdict"] == "block_route_by_surface_or_baseline_failure"
    assert preservation["candidate_admissibility_authorized"] is False

    assert routing["route"] == "block_route_by_surface_or_baseline_failure"
    assert routing["current_surface_robustness_evidence_status"] == "downgraded_to_inconclusive"
    assert routing["candidate_admissibility_design_authorized"] is False
    assert routing["generator_repair_performed"] is False
    assert routing["previous_artifacts_modified"] is False


def test_execute_writes_artifacts_report_and_forbids_downstream_paths(tmp_path):
    runner = _runner()
    output_dir = tmp_path / TASK_DIR
    report_path = tmp_path / REPORT_NAME

    run = runner.execute(output_dir=output_dir, persist_artifacts=True)
    written_report = runner.write_research_report(run, report_path=report_path)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in output_dir.glob("*.json")})
    for path in output_dir.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

    result = run["result"]
    assert result["task_id"] == TASK_CARD_ID
    assert result["verdict"] == "block_route_by_surface_or_baseline_failure"
    assert result["current_layer"] == "engineering implementation / evidence-governance / legal-interface oracle block only"
    assert result["mainline_integration_status"] == "not integrated"
    assert result["enabled_status"] == "callable local legal-interface oracle only"
    assert result["claim_ceiling"] == "Legal-interface solvability oracle and negative-evidence preservation only."
    assert result["current_surface_robustness_evidence_status"] == "downgraded_to_inconclusive"
    assert "legal_interface_oracle_random_or_inconclusive" in result["stop_conditions_triggered"]
    assert result["candidate_admissibility_design_authorized"] is False
    assert result["generator_repair_performed"] is False
    assert result["previous_artifacts_modified"] is False
    assert result["tournament_run"] is False
    assert result["gate4_runtime_bridge_admission_or_ego_mainline_entered"] is False

    guard = run["forbidden_action_guard"]
    assert guard["forbidden_files_modified"] == []
    assert guard["candidate_or_tournament_or_gate4_paths_created"] is False
    assert guard["runtime_bridge_admission_or_ego_mainline_paths_created"] is False
    assert guard["llm_rag_ui_companion_paths_created"] is False

    report_text = written_report.read_text(encoding="utf-8")
    assert "block_route_by_surface_or_baseline_failure" in report_text
    assert "downgraded_to_inconclusive" in report_text
    assert "Legal-interface solvability oracle and negative-evidence preservation only" in report_text
