import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A"
TASK_SLUG = "surface_admission_contract_enforcement_001a"
HARDENING_TASK_ID = "SURFACE-ADMISSION-CONTRACT-HARDENING-001A"
HARDENING_SLUG = "surface_admission_contract_hardening_001a"
HARDENING_TAG = (
    "remote-anchor-surface-admission-contract-hardening-001a-"
    "verdict-enum-reconciliation-001a-915d4c5"
)
CLAIM_CEILING = "engineering-governance / task-authorization hygiene only"
REQUIRED_GATES = {f"G{index}" for index in range(1, 15)}
REQUIRED_ACCEPTANCE = {f"E{index}" for index in range(1, 19)}


def _validator():
    from surface_admission_contract_enforcement_001a import validator

    return validator


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _copy_hardening_artifacts(tmp_path: Path) -> tuple[Path, Path]:
    result_path = tmp_path / "result.json"
    readback_path = tmp_path / "readback.json"
    _write_json(
        result_path,
        _load_json(ROOT / "artifacts" / HARDENING_SLUG / "result.json"),
    )
    _write_json(
        readback_path,
        _load_json(ROOT / "artifacts" / HARDENING_SLUG / "readback.json"),
    )
    return result_path, readback_path


def test_hardening_artifacts_are_parsed_and_required_readback_controls_are_verified():
    validator = _validator()

    report = validator.validate_hardening_artifacts(ROOT)

    assert report["passed"] is True
    assert report["hardening_result"]["verdict"] == "contract_hardened_pass"
    assert set(report["gate_readback"]["present_passed_gates"]) == REQUIRED_GATES
    assert report["gate_readback"]["missing_or_failed_gates"] == []
    assert report["anti_blacklist"]["passed"] is True
    assert report["reason_specific_controls"]["passed"] is True
    assert report["scope_guards"]["no_mechanism_score"] is True
    assert report["scope_guards"]["no_candidate"] is True
    assert report["scope_guards"]["no_new_mechanism_surface"] is True
    assert report["referenced_anchor"]["local_tag_hash"]
    assert report["referenced_anchor"]["tag"] == HARDENING_TAG
    assert report["claim_ceiling"] == CLAIM_CEILING

    invoked = {entry["producer_function"] for entry in report["invocation_log"]}
    assert {
        "parse_hardening_result",
        "parse_hardening_readback",
        "check_hardening_verdict",
        "check_g1_g14_readback",
        "check_anti_blacklist_readback",
        "check_reason_specific_controls",
        "check_no_mechanism_surface",
    }.issubset(invoked)


def test_hardening_artifact_mutations_block_authorization(tmp_path):
    validator = _validator()
    result_path, readback_path = _copy_hardening_artifacts(tmp_path)

    wrong_result = _load_json(result_path)
    wrong_result["verdict"] = "contract_refused"
    _write_json(result_path, wrong_result)

    wrong_verdict = validator.validate_hardening_artifacts(
        ROOT,
        result_path=result_path,
        readback_path=readback_path,
    )
    assert wrong_verdict["passed"] is False
    assert "hardening_verdict_not_contract_hardened_pass" in wrong_verdict["reasons_fired"]

    result_path, readback_path = _copy_hardening_artifacts(tmp_path / "missing_controls")
    readback = _load_json(readback_path)
    del readback["gates"]["G13"]
    del readback["gates"]["G14"]
    _write_json(readback_path, readback)

    missing_gates = validator.validate_hardening_artifacts(
        ROOT,
        result_path=result_path,
        readback_path=readback_path,
    )
    assert missing_gates["passed"] is False
    assert "missing_or_failed_g1_g14_readback" in missing_gates["reasons_fired"]

    result_path, readback_path = _copy_hardening_artifacts(tmp_path / "corrupt_readback")
    readback_path.write_text("{not json", encoding="utf-8")
    corrupt = validator.validate_hardening_artifacts(
        ROOT,
        result_path=result_path,
        readback_path=readback_path,
    )
    assert corrupt["passed"] is False
    assert "hardening_readback_parse_failed" in corrupt["reasons_fired"]


def test_manifest_checker_authorizes_only_parseable_artifact_backed_future_tasks():
    validator = _validator()
    hardening = validator.validate_hardening_artifacts(ROOT)
    manifest = validator.build_valid_future_manifest(ROOT)

    decision = validator.validate_future_manifest(manifest, hardening)

    assert decision["authorization_decision"] == "authorized"
    assert decision["reasons_fired"] == []
    assert decision["claim_ceiling"] == CLAIM_CEILING
    assert decision["no_candidate"] is True
    assert decision["no_runtime"] is True
    assert decision["no_mainline"] is True
    assert decision["no_mechanism_score"] is True

    invoked = {entry["producer_function"] for entry in decision["invocation_log"]}
    assert {
        "check_hardened_contract_dependency",
        "check_validator_readback_precondition",
        "check_false_full_suite_claim",
        "check_no_mechanism_score_request",
        "check_no_candidate_runtime_mainline",
        "check_preserved_invalid_surface_citations",
    }.issubset(invoked)


def test_manifest_checker_rejects_required_hostile_bypass_patterns():
    validator = _validator()
    hardening = validator.validate_hardening_artifacts(ROOT)
    valid = validator.build_valid_future_manifest(ROOT)

    cases = {
        "superficial_mention_only": (
            {
                "task_id": "SURFACE-ADMISSION-FUTURE-SUPERFICIAL",
                "summary": f"Mentions {HARDENING_TASK_ID} but provides no parseable dependency.",
            },
            "missing_hardened_contract_dependency",
        ),
        "plain_text_dependency_only": (
            {
                **copy.deepcopy(valid),
                "hardened_contract_dependency": f"depends on {HARDENING_TASK_ID}",
            },
            "missing_hardened_contract_dependency",
        ),
        "missing_validator_precondition": (
            {
                **copy.deepcopy(valid),
                "pre_execution_requirements": [],
            },
            "missing_hardened_validator_or_readback_precondition",
        ),
        "creates_candidate_behavior": (
            {
                **copy.deepcopy(valid),
                "scope": {**valid["scope"], "creates_candidate_behavior": True},
            },
            "candidate_behavior_requested",
        ),
        "opens_gate5_bridge_runtime_or_mainline": (
            {
                **copy.deepcopy(valid),
                "scope": {
                    **valid["scope"],
                    "opens_gate5": True,
                    "opens_bridge": True,
                    "opens_runtime": True,
                    "opens_ego_mainline": True,
                },
            },
            "gate5_bridge_runtime_or_mainline_requested",
        ),
        "requests_mechanism_score": (
            {
                **copy.deepcopy(valid),
                "outputs_requested": valid["outputs_requested"] + ["mechanism_score"],
            },
            "mechanism_score_requested_or_produced",
        ),
        "false_full_suite_pass": (
            {
                **copy.deepcopy(valid),
                "test_evidence": {
                    "focused_tests_passed": True,
                    "full_pytest_status": "timed_out_after_120s",
                    "claims_full_suite_pass": True,
                },
            },
            "false_full_suite_pass_claim",
        ),
        "old_invalid_surfaces_as_mechanism_evidence": (
            {
                **copy.deepcopy(valid),
                "evidence_citations": [
                    {
                        "artifact_id": "COMPOSITE-CROSS-TASK-STATE-REUSE-SURFACE-DISCRIMINATIVENESS-PREFLIGHT-001A",
                        "claim": "mechanism evidence",
                    },
                    {
                        "artifact_id": "CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A",
                        "claim": "mechanism evidence",
                    },
                    {
                        "artifact_id": "ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A",
                        "claim": "mechanism evidence",
                    },
                ],
            },
            "old_invalid_surface_cited_as_mechanism_evidence",
        ),
        "hardening_claimed_as_gate_or_readiness": (
            {
                **copy.deepcopy(valid),
                "claims": [
                    "Gate4 validity",
                    "Gate5 validity",
                    "mechanism validity",
                    "mainline readiness",
                ],
            },
            "claim_ceiling_inflation",
        ),
    }

    for case_name, (manifest, expected_reason) in cases.items():
        decision = validator.validate_future_manifest(manifest, hardening)
        assert decision["authorization_decision"] == "blocked", case_name
        assert expected_reason in decision["reasons_fired"], case_name


def test_enforcement_run_emits_parseable_artifacts_and_blocks_all_synthetic_controls(tmp_path):
    validator = _validator()
    out = tmp_path / TASK_SLUG

    result = validator.run_enforcement(ROOT, output_dir=out)

    required_files = {
        "result.json",
        "readback.json",
        "enforcement_report.json",
        "synthetic_control_report.json",
        "enforcement_trace.jsonl",
        "json_parse_verification.json",
        "claim_ceiling.txt",
    }
    assert result["verdict"] == "contract_enforcement_pass"
    assert result["current_layer"] == "engineering-governance / contract enforcement / no mechanism surface"
    assert result["mainline_integration_status"] == "none; offline local checker and artifact contract only"
    assert result["enabled_status"] == "local checker / artifact contract only"
    assert result["real_trigger_evidence"] == "read-only hardening artifact/readback plus synthetic future-manifest bypass controls"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["mechanism_score_produced"] is False
    assert result["candidate_or_surface_designed"] is False
    assert result["new_mechanism_surface_designed"] is False
    assert result["auto_remote_anchor"]["decision"] == "conditional"
    assert result["auto_remote_anchor"]["permitted_now"] is True
    assert required_files == {path.name for path in out.iterdir()}
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING

    for path in out.glob("*.json"):
        _load_json(path)

    readback = _load_json(out / "readback.json")
    controls = _load_json(out / "synthetic_control_report.json")
    verification = _load_json(out / "json_parse_verification.json")
    trace_lines = [
        json.loads(line)
        for line in (out / "enforcement_trace.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert set(readback["acceptance_gates"]["passed"]) == REQUIRED_ACCEPTANCE
    assert readback["acceptance_gates"]["failed"] == []
    assert readback["result_json_parse"]["parse_status"] == "parsed"
    assert readback["readback_json_parse"]["parse_status"] == "created_and_parsed"
    assert all(control["blocked"] is True for control in controls["controls"])
    assert "superficial_contract_mention_only" in {
        control["control_id"] for control in controls["controls"]
    }
    assert verification["parse_status"] == "all_required_json_parsed"
    assert verification["no_mechanism_score"] is True
    assert trace_lines
    assert {entry["event"] for entry in trace_lines}.issuperset(
        {"file_read", "check_invoked", "synthetic_control_evaluated"}
    )


def test_contract_document_keeps_enforcement_as_governance_only():
    contract = ROOT / "docs" / "research" / "SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A.md"
    text = contract.read_text(encoding="utf-8")

    assert TASK_ID in text
    assert "Auto-Remote-Anchor: conditional" in text
    assert "contract_enforcement_pass" in text
    assert "contract_enforcement_refused" in text
    assert "invalid_enforcement_harness" in text
    assert "No Gate5, bridge, runtime, tournament, candidate, or EGO-mainline path is authorized." in text
    assert "mechanism validity" in text
    assert "task-authorization hygiene only" in text
