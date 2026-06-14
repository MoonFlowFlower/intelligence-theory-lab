import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "SURFACE-ADMISSION-CONTRACT-HARDENING-001A"
TASK_SLUG = "surface_admission_contract_hardening_001a"
CLAIM_CEILING = "engineering-governance / evidence-hygiene only"

PRESERVED_CONTROL_PATHS = [
    ROOT / "artifacts" / "preserve_composite_ctsr_hostile_audit_001a" / "result.json",
    ROOT
    / "artifacts"
    / "preserve_ctsr_solvability_inversion_preflight_001a_hostile_audit_001a"
    / "result.json",
    ROOT
    / "artifacts"
    / "preserve_action_conditioned_self_boundary_preflight_001a_hostile_audit_001a"
    / "result.json",
]

REQUIRED_GATE_IDS = {f"G{index}" for index in range(1, 11)}
REQUIRED_CHALLENGERS = {
    "single_legal_field_lookup",
    "legal_tuple_lookup",
    "state_action_table",
    "action_index_context_key_arithmetic",
    "effect_vector_lookup",
    "nearest_neighbor_legal_observations",
}


def _validator():
    from surface_admission_contract_hardening_001a import validator

    return validator


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_preserved_negative_controls_exist_and_remain_read_only_inputs():
    for path in PRESERVED_CONTROL_PATHS:
        payload = _load_json(path)
        assert (
            payload.get("new_mechanism_score_produced") is False
            or payload.get("mechanism_score_produced") is False
        )
        assert "claim_ceiling" in payload
        assert path.exists()


def test_validator_blocks_all_preserved_false_positive_controls_without_task_id_denylist():
    validator = _validator()

    report = validator.validate_preserved_negative_controls(ROOT)

    assert report["task_id"] == TASK_ID
    assert report["verdict"] == "blocked_preserved_false_positive_surfaces"
    assert report["claim_ceiling"] == CLAIM_CEILING
    assert report["static_task_id_denylist_used"] is False
    assert report["mechanism_score_produced"] is False
    assert report["candidate_or_surface_designed"] is False
    assert report["blocked_control_count"] == 3
    assert {control["control_path"] for control in report["controls"]} == {
        str(path.relative_to(ROOT)).replace("\\", "/") for path in PRESERVED_CONTROL_PATHS
    }
    assert all(control["admission_decision"] == "blocked" for control in report["controls"])
    assert set(report["acceptance_gates"]["passed"]) == REQUIRED_GATE_IDS
    assert report["acceptance_gates"]["failed"] == []


def test_semantic_answer_encoding_and_benign_alias_are_detected_by_accuracy_not_name_only():
    validator = _validator()
    report = validator.validate_preserved_negative_control(
        PRESERVED_CONTROL_PATHS[2], repo_root=ROOT
    )

    finding_ids = {finding["gate_id"] for finding in report["findings"]}
    assert {"G2", "G7"}.issubset(finding_ids)

    semantic = [finding for finding in report["findings"] if finding["gate_id"] == "G2"]
    aliases = [finding for finding in report["findings"] if finding["gate_id"] == "G7"]

    assert any(finding["detector_method"] == "semantic_accuracy_probe" for finding in semantic)
    assert any("actuator_effects" in finding["evidence"] for finding in semantic)
    assert any("controllability_outlook" in finding["evidence"] for finding in aliases)
    assert all(finding["detector_method"] != "forbidden_name_fragment_scan_only" for finding in semantic + aliases)


def test_challenger_synthesis_covers_all_required_fair_baselines_and_oracle_equivalence():
    validator = _validator()

    report = validator.validate_preserved_negative_controls(ROOT)
    manifest = report["synthesized_challenger_manifest"]

    assert set(manifest["required_challengers"]) == REQUIRED_CHALLENGERS
    assert manifest["producer_function"] == "synthesize_required_challengers"
    assert manifest["challengers_are_legal_interface_only"] is True
    assert manifest["missing_required_challengers_in_validator"] == []

    controls_by_task = {control["preserved_task_id"]: control for control in report["controls"]}
    ctsr = controls_by_task["PRESERVE-CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A-HOSTILE-AUDIT-001A"]
    action = controls_by_task["PRESERVE-ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A-HOSTILE-AUDIT-001A"]

    assert ctsr["oracle_equivalent_legal_challengers_detected"] is True
    assert "action_index_context_key_arithmetic" in ctsr["matched_challengers"]
    assert "nearest_neighbor_legal_observations" in ctsr["matched_challengers"]
    assert action["oracle_equivalent_legal_challengers_detected"] is True
    assert "effect_vector_lookup" in action["matched_challengers"]
    assert "state_action_table" in action["matched_challengers"]


def test_evaluator_privilege_replay_tautology_proxy_leaks_and_static_pass_reports_are_refused():
    validator = _validator()

    preserved = validator.validate_preserved_negative_controls(ROOT)
    gate_map = preserved["acceptance_gates"]["evidence_by_gate"]

    assert gate_map["G4"]["passed"] is True
    assert any("oracle" in item.lower() for item in gate_map["G4"]["evidence"])
    assert gate_map["G6"]["passed"] is True
    assert any("replay" in item.lower() for item in gate_map["G6"]["evidence"])
    assert gate_map["G8"]["passed"] is True
    assert any("action_index" in item or "context" in item for item in gate_map["G8"]["evidence"])

    static_bundle = validator.build_static_pass_positive_control_bundle()
    static_report = validator.validate_surface_admission_bundle(static_bundle)

    assert static_report["admission_decision"] == "blocked"
    assert any(finding["gate_id"] == "G9" for finding in static_report["findings"])
    assert static_report["static_report_refused"] is True
    assert static_report["non_failable_claims_detected"] is True


def test_run_validator_writes_machine_readable_artifacts_without_mechanism_score(tmp_path):
    validator = _validator()
    out = tmp_path / TASK_SLUG

    result = validator.run_validator(repo_root=ROOT, output_dir=out)

    required_artifacts = {
        "result.json",
        "preserved_negative_control_report.json",
        "validator_rule_manifest.json",
        "synthesized_challenger_manifest.json",
        "static_pass_refusal_report.json",
        "protected_input_hashes.json",
        "json_parse_verification.json",
        "claim_ceiling.txt",
    }
    assert result["verdict"] == "blocked_preserved_false_positive_surfaces"
    assert result["mechanism_score_produced"] is False
    assert result["candidate_or_surface_designed"] is False
    assert result["auto_remote_anchor"]["decision"] == "conditional"
    assert result["auto_remote_anchor"]["permitted_now"] is True
    assert required_artifacts == {path.name for path in out.iterdir()}
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING

    for path in out.glob("*.json"):
        _load_json(path)

    verification = _load_json(out / "json_parse_verification.json")
    protected = _load_json(out / "protected_input_hashes.json")
    assert verification["parse_status"] == "all_required_json_parsed"
    assert verification["no_mechanism_score"] is True
    assert protected["preserved_inputs_modified"] is False
    assert set(protected["protected_input_paths"]) == {
        str(path.relative_to(ROOT)).replace("\\", "/") for path in PRESERVED_CONTROL_PATHS
    }


def test_contract_document_defines_future_surface_admission_gates():
    contract = ROOT / "docs" / "research" / "SURFACE-ADMISSION-CONTRACT-HARDENING-001A.md"
    text = contract.read_text(encoding="utf-8")

    assert "Auto-Remote-Anchor: conditional" in text
    assert "No mechanism candidate is implemented or scored" in text
    for gate_id in sorted(REQUIRED_GATE_IDS):
        assert f"{gate_id}." in text
    for challenger in sorted(REQUIRED_CHALLENGERS):
        assert challenger in text
