import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-TEMPLATE-001A"
TASK_SLUG = "future_surface_admission_authorization_template_001a"
HARDENING_TASK_ID = "SURFACE-ADMISSION-CONTRACT-HARDENING-001A"
ENFORCEMENT_TASK_ID = "SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A"
PARENT_COMMIT = "22d8a09eb6747152f4d072d52c71f2725add87b1"
PARENT_BRANCH = "codex/meta-theory-scaffold"
PARENT_TAG = "remote-anchor-surface-admission-contract-enforcement-001a-22d8a09"
CLAIM_CEILING = "surface-admission authorization hygiene only"
REQUIRED_ACCEPTANCE = {f"A{index}" for index in range(1, 21)}
REQUIRED_FILES = {
    "result.json",
    "readback.json",
    "authorization_manifest_template.json",
    "hostile_control_report.json",
    "ablation_report.json",
    "authorization_trace.jsonl",
    "json_parse_verification.json",
    "claim_ceiling.txt",
}
REQUIRED_HOSTILES = {
    "superficial_contract_mention_without_checker_invocation",
    "checker_invocation_without_readback",
    "hardening_dependency_only_missing_enforcement",
    "enforcement_dependency_only_missing_hardening",
    "wrong_enforcement_verdict",
    "corrupt_or_missing_readback",
    "missing_g13_g14_requirement",
    "missing_anti_blacklist_requirement",
    "missing_reason_control_requirement",
    "old_invalid_surface_cited_as_mechanism_evidence",
    "mechanism_score_before_admission",
    "candidate_gate5_bridge_runtime_tournament_mainline_scope",
    "readiness_inflation_language",
    "false_full_suite_pass_claim",
}
REQUIRED_ABLATIONS = {
    "remove_hardening_dependency",
    "remove_enforcement_dependency",
    "remove_checker_invocation_field",
    "remove_checker_readback_field",
    "remove_old_invalid_surface_citation_ban",
    "remove_no_mechanism_score_rule",
    "remove_no_candidate_runtime_mainline_scope_rule",
    "remove_claim_ceiling_field",
    "corrupt_parent_commit_reference",
    "corrupt_parent_tag_reference",
    "corrupt_enforcement_verdict",
    "corrupt_readback_hash_or_status",
}


def _validator():
    from future_surface_admission_authorization_template_001a import validator

    return validator


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _copy_enforcement_artifacts(tmp_path: Path) -> tuple[Path, Path]:
    result_path = tmp_path / "result.json"
    readback_path = tmp_path / "readback.json"
    _write_json(
        result_path,
        _load_json(ROOT / "artifacts" / "surface_admission_contract_enforcement_001a" / "result.json"),
    )
    _write_json(
        readback_path,
        _load_json(ROOT / "artifacts" / "surface_admission_contract_enforcement_001a" / "readback.json"),
    )
    return result_path, readback_path


def test_parent_boundary_and_enforcement_artifacts_are_verified_from_readback():
    validator = _validator()

    report = validator.validate_enforcement_artifacts(ROOT)

    assert report["passed"] is True
    assert report["parent_boundary"]["commit"] == PARENT_COMMIT
    assert report["parent_boundary"]["branch"] == PARENT_BRANCH
    assert report["parent_boundary"]["tag"] == PARENT_TAG
    assert report["enforcement_result"]["verdict"] == "contract_enforcement_pass"
    assert report["acceptance_gates"]["failed"] == []
    assert report["acceptance_gates"]["passed_count"] >= 18
    assert report["synthetic_controls"]["all_controls_blocked"] is True
    assert report["required_control_checks"]["g13_g14"]["passed"] is True
    assert report["required_control_checks"]["anti_blacklist"]["passed"] is True
    assert report["required_control_checks"]["reason_control"]["passed"] is True
    assert report["readback_hash"]
    assert report["claim_ceiling"] == CLAIM_CEILING

    invoked = {entry["producer_function"] for entry in report["invocation_log"]}
    assert {
        "parse_enforcement_result",
        "parse_enforcement_readback",
        "check_parent_boundary_reference",
        "check_enforcement_acceptance_gates",
        "check_hostile_controls_from_enforcement_readback",
        "check_g13_g14_anti_blacklist_reason_controls",
    }.issubset(invoked)


def test_valid_manifest_template_authorizes_only_governance_scope():
    validator = _validator()
    enforcement = validator.validate_enforcement_artifacts(ROOT)
    template = validator.build_authorization_manifest_template(ROOT)
    manifest = copy.deepcopy(template["example_authorized_manifest"])

    decision = validator.validate_authorization_manifest(manifest, template, enforcement)

    assert decision["authorization_decision"] == "authorized"
    assert decision["reasons_fired"] == []
    assert decision["hardening_dependency_required"] is True
    assert decision["enforcement_dependency_required"] is True
    assert decision["checker_invocation_required"] is True
    assert decision["checker_readback_required"] is True
    assert decision["no_mechanism_score"] is True
    assert decision["no_candidate_runtime_mainline"] is True
    assert decision["old_invalid_surface_evidence_ban"] is True
    assert decision["claim_ceiling"] == CLAIM_CEILING
    assert decision["producer_function"] == "validate_authorization_manifest"

    invoked = {entry["producer_function"] for entry in decision["invocation_log"]}
    assert {
        "check_manifest_dependencies",
        "check_checker_invocation_and_readback",
        "check_scope_bans",
        "check_old_invalid_surface_ban",
        "check_claim_ceiling",
    }.issubset(invoked)


def test_authorization_decision_ignores_stored_verdict_strings():
    validator = _validator()
    enforcement = validator.validate_enforcement_artifacts(ROOT)
    template = validator.build_authorization_manifest_template(ROOT)
    manifest = copy.deepcopy(template["example_authorized_manifest"])
    manifest["stored_authorization_decision"] = "authorized"
    del manifest["dependencies"][0]

    decision = validator.validate_authorization_manifest(manifest, template, enforcement)

    assert decision["authorization_decision"] == "blocked"
    assert "missing_hardening_dependency" in decision["reasons_fired"]
    assert decision["stored_verdict_trusted"] is False


def test_required_hostile_controls_are_blocked_by_callable_validation():
    validator = _validator()
    enforcement = validator.validate_enforcement_artifacts(ROOT)
    template = validator.build_authorization_manifest_template(ROOT)

    report = validator.build_hostile_control_report(ROOT, template, enforcement)

    control_ids = {control["control_id"] for control in report["controls"]}
    assert REQUIRED_HOSTILES.issubset(control_ids)
    assert report["all_controls_blocked"] is True
    assert report["blocked_control_count"] == len(report["controls"])
    assert report["producer_function"] == "build_hostile_control_report"
    assert report["claim_ceiling"] == CLAIM_CEILING

    for control in report["controls"]:
        assert control["blocked"] is True, control["control_id"]
        assert control["producer_function"] in {
            "validate_authorization_manifest",
            "validate_enforcement_artifacts",
        }
        assert control["reasons_fired"], control["control_id"]


def test_required_ablations_are_blocked_by_callable_validation():
    validator = _validator()
    enforcement = validator.validate_enforcement_artifacts(ROOT)
    template = validator.build_authorization_manifest_template(ROOT)

    report = validator.build_ablation_report(ROOT, template, enforcement)

    ablation_ids = {ablation["ablation_id"] for ablation in report["ablations"]}
    assert REQUIRED_ABLATIONS.issubset(ablation_ids)
    assert report["all_ablations_blocked"] is True
    assert report["blocked_ablation_count"] == len(report["ablations"])
    assert report["producer_function"] == "build_ablation_report"
    assert report["claim_ceiling"] == CLAIM_CEILING

    for ablation in report["ablations"]:
        assert ablation["blocked"] is True, ablation["ablation_id"]
        assert ablation["producer_function"] in {
            "validate_authorization_manifest",
            "validate_enforcement_artifacts",
        }
        assert ablation["reasons_fired"], ablation["ablation_id"]


def test_mutated_enforcement_readback_blocks_authorization(tmp_path):
    validator = _validator()
    result_path, readback_path = _copy_enforcement_artifacts(tmp_path)

    readback = _load_json(readback_path)
    readback["synthetic_controls"]["all_controls_blocked"] = False
    for control in readback["synthetic_controls"]["controls"]:
        if control["control_id"] == "missing_g13_g14_controls":
            control["blocked"] = False
            control["reasons_fired"] = []
    _write_json(readback_path, readback)

    report = validator.validate_enforcement_artifacts(
        ROOT,
        result_path=result_path,
        readback_path=readback_path,
    )

    assert report["passed"] is False
    assert "missing_g13_g14_control_not_blocked" in report["reasons_fired"]


def test_run_authorization_template_emits_required_parseable_artifacts(tmp_path):
    validator = _validator()
    out = tmp_path / TASK_SLUG

    result = validator.run_authorization_template(ROOT, output_dir=out)

    assert result["verdict"] == "future_surface_admission_authorization_template_001a_pass"
    assert result["current_layer"] == "engineering-governance / future task authorization template / surface-admission precondition enforcement"
    assert result["mainline_integration_status"] == "none; offline governance template/checker only"
    assert result["enabled_status"] == "local offline template validator only"
    assert result["real_trigger_evidence"] == "template manifest plus enforcement readback, hostile controls, and ablation controls"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["mechanism_score_produced"] is False
    assert result["candidate_or_surface_designed"] is False
    assert result["new_mechanism_surface_designed"] is False
    assert result["auto_remote_anchor"]["decision"] == "conditional"
    assert result["auto_remote_anchor"]["permitted_now"] is True
    assert REQUIRED_FILES == {path.name for path in out.iterdir()}
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING

    for path in out.glob("*.json"):
        _load_json(path)

    readback = _load_json(out / "readback.json")
    hostile = _load_json(out / "hostile_control_report.json")
    ablation = _load_json(out / "ablation_report.json")
    verification = _load_json(out / "json_parse_verification.json")
    trace_lines = [
        json.loads(line)
        for line in (out / "authorization_trace.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert set(readback["acceptance_gates"]["passed"]) == REQUIRED_ACCEPTANCE
    assert readback["acceptance_gates"]["failed"] == []
    assert readback["result_json_parse"]["parse_status"] == "parsed"
    assert readback["readback_json_parse"]["parse_status"] == "created_and_parsed"
    assert hostile["all_controls_blocked"] is True
    assert ablation["all_ablations_blocked"] is True
    assert verification["parse_status"] == "all_required_json_parsed"
    assert verification["no_mechanism_score"] is True
    assert trace_lines
    assert {entry["event"] for entry in trace_lines}.issuperset(
        {
            "file_read",
            "check_invoked",
            "hostile_control_evaluated",
            "ablation_control_evaluated",
            "final_authorization_decision",
        }
    )
    final = [entry for entry in trace_lines if entry["event"] == "final_authorization_decision"][0]
    assert final["producer_function"] == "validate_authorization_manifest"
    assert final["manifest_hash"]
    assert final["template_hash"]
    assert final["code_path_hash"]
    assert final["parent_boundary_reference"]["commit"] == PARENT_COMMIT


def test_contract_document_keeps_future_authorization_as_governance_only():
    contract = ROOT / "docs" / "research" / "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-TEMPLATE-001A.md"
    text = contract.read_text(encoding="utf-8")

    assert TASK_ID in text
    assert "Auto-Remote-Anchor: conditional" in text
    assert HARDENING_TASK_ID in text
    assert ENFORCEMENT_TASK_ID in text
    assert "mechanism_score" in text
    assert "No Gate5, bridge, runtime, tournament, candidate, or EGO-mainline path is authorized." in text
    assert "old invalid COMPOSITE / CTSR / ACTION-CONDITIONED surfaces" in text
    assert "surface-admission authorization hygiene only" in text
