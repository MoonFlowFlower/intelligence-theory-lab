import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")


def _read_json(path):
    return json.loads(_read_text(path))


def test_theory_reset_001a_required_outputs_exist():
    required = [
        "docs/THEORY-RESET-NEW-PROBLEM-DEFINITION-001A.md",
        "docs/theory_reset_001a/problem_definition_contract.md",
        "docs/theory_reset_001a/failed_framing_audit.md",
        "docs/theory_reset_001a/control_family_carryforward.md",
        "docs/theory_reset_001a/candidate_framing_matrix.md",
        "docs/theory_reset_001a/claim_ceiling.md",
        "artifacts/theory_reset_001a/theory_reset_result.json",
        "artifacts/theory_reset_001a/candidate_framing_matrix.json",
        "artifacts/theory_reset_001a/lineage_inputs_manifest.json",
        "artifacts/theory_reset_001a/verdict_manifest.json",
    ]

    for relative_path in required:
        assert (ROOT / relative_path).exists(), relative_path


def test_theory_reset_001a_verdict_and_authorization_boundaries():
    result = _read_json("artifacts/theory_reset_001a/theory_reset_result.json")
    verdict = _read_json("artifacts/theory_reset_001a/verdict_manifest.json")

    assert result["task_id"] == "THEORY-RESET-NEW-PROBLEM-DEFINITION-001A"
    assert result["final_verdict"] == "theory_reset_001a_problem_definition_bounded_pass"
    assert result["strongest_allowed_claim_ceiling"] == "bounded successor problem-definition evidence only"
    assert result["next_allowed_task_if_any"] == "NEW-PROBLEM-PREFLIGHT-001A task-card drafting"
    assert result["no_model_class_reset_authorized"] is True
    assert result["no_Gate1_reopen_authorized"] is True
    assert result["no_same_agent_bridge_authorized"] is True
    assert result["no_EGO_integration_authorized"] is True
    assert result["does_not_rescue_001A_or_001B"] is True
    assert result["not_output_only"] is True
    assert result["cheap_control_family_carryforward_complete"] is True
    assert result["trace_replay_contract_defined"] is True
    assert result["intervention_or_process_probe_defined"] is True
    assert result["strongest_objection_documented"] is True
    assert result["anti_hardcoding_audit_passed"] is True
    assert result["stop_conditions_encountered"] == []

    assert verdict["model_class_reset_authorized"] is False
    assert verdict["gate1_reopen_authorized"] is False
    assert verdict["same_agent_bridge_authorized"] is False
    assert verdict["ego_integration_authorized"] is False


def test_theory_reset_001a_lineage_inputs_and_candidate_matrix():
    lineage = _read_json("artifacts/theory_reset_001a/lineage_inputs_manifest.json")
    matrix = _read_json("artifacts/theory_reset_001a/candidate_framing_matrix.json")

    required_inputs = {
        "Gate0_001C_closeout_claim_ceiling",
        "Gate1_failed_graph_cache_collapse_closeout",
        "Candidate_A_closeout",
        "Candidate_B_residue_closeout",
        "same_agent_bridge_blocked_status",
        "REPRESENTATIONAL_GAP_PREFLIGHT_001A_independent_audit_closeout",
        "REPRESENTATIONAL_GAP_PREFLIGHT_001B_final_report",
        "REPRESENTATIONAL_GAP_PREFLIGHT_001B_expressivity_proof",
        "REPRESENTATIONAL_GAP_PREFLIGHT_001B_claim_ceiling",
    }
    assert required_inputs.issubset(set(lineage["inputs"]))
    assert all(item["status"] == "available" for item in lineage["inputs"].values())

    assert set(matrix["families"]) == {"F1", "F2", "F3", "F4", "F5", "F6"}
    assert matrix["families"]["F1"]["verdict"] == "reject_or_demote"
    assert matrix["families"]["F2"]["verdict"] == "survives_as_primary_candidate"
    assert matrix["families"]["F3"]["verdict"] == "survives_as_supporting_constraint"
    assert matrix["families"]["F6"]["verdict"] == "reject_for_now"


def test_theory_reset_001a_main_document_required_sections_and_forbidden_scope():
    text = _read_text("docs/THEORY-RESET-NEW-PROBLEM-DEFINITION-001A.md")
    required_sections = [
        "current_layer",
        "parent_lineage_summary",
        "wrong_problem_definition",
        "most_likely_wrong_abstraction",
        "strongest_objection",
        "cheap_control_lessons",
        "candidate_successor_framings",
        "rejected_framings",
        "surviving_candidate_problem_definition_if_any",
        "trace_replay_requirements",
        "future_preflight_requirements",
        "claim_ceiling",
        "stop_conditions",
        "rollback_plan",
        "next_allowed_task",
    ]
    for section in required_sections:
        assert section in text

    required_phrases = [
        "The proposed framing may still be wrong because cheap controls may match not only outputs but also traces if the trace schema is too shallow.",
        "process-level state change under intervention",
        "NEW-PROBLEM-PREFLIGHT-001A task-card drafting",
        "MODEL_CLASS_RESET = not_authorized",
        "same_agent_bridge = blocked",
        "EGO_integration = not_authorized",
    ]
    for phrase in required_phrases:
        assert phrase in text

    forbidden_phrases = [
        "model_class_reset_authorized = true",
        "Gate1_reopen_authorized = true",
        "same_agent_bridge_authorized = true",
        "ego_integration_authorized = true",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in text
