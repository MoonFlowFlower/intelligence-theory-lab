import copy
import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EGO-MAINLINE-ADMISSION-TASK-CARD-ALIGNMENT-001A"
ARTIFACT_DIR = ROOT / "artifacts" / "ego_mainline_admission_task_card_alignment_001a"
DOC = ROOT / "docs" / "codex" / "tasks" / f"{TASK_ID}.md"

REQUIRED_ARTIFACTS = {
    "result.json",
    "existing_admission_task_card_search_report.json",
    "parent_evidence_boundary_manifest.json",
    "evidence_usage_contract.json",
    "actionability_revalidation_matrix.json",
    "computed_evidence_gate_contract.json",
    "negative_evidence_handling_contract.json",
    "authorization_guard.json",
    "schema_duplication_guard.json",
    "post_bridge_boundary_resolution_report.json",
    "source_trace_report.json",
    "claim_ceiling.txt",
}

REQUIRED_CLAIMS = {
    "EGO readiness",
    "bridge readiness",
    "mechanism validity",
    "theory validity",
    "architecture correctness",
    "agency",
    "selfhood",
    "consciousness",
    "emotion",
    "relationship learning",
    "stable user benefit",
    "future runtime correctness",
}


def _runner():
    return importlib.import_module("ego_mainline_admission_task_card_alignment_001a.runner")


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _walk(value, path="$"):
    rows = [(path, value)]
    if isinstance(value, dict):
        for key, item in value.items():
            rows.extend(_walk(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(_walk(item, f"{path}[{index}]"))
    return rows


def test_materialized_required_files_and_artifacts_exist_and_parse():
    assert DOC.exists()
    assert ARTIFACT_DIR.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt"}:
        assert isinstance(_read_json(ARTIFACT_DIR / name), dict)
    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == _runner().CLAIM_CEILING


def test_parent_boundaries_and_post_bridge_resolution_are_exact():
    runner = _runner()
    manifest = _read_json(ARTIFACT_DIR / "parent_evidence_boundary_manifest.json")
    post_bridge = _read_json(ARTIFACT_DIR / "post_bridge_boundary_resolution_report.json")

    boundaries = {row["boundary_id"]: row for row in manifest["parent_boundaries"]}
    assert boundaries["admission_coverage_reference"]["commit"] == runner.ADMISSION_COVERAGE_REFERENCE_COMMIT
    assert boundaries["admission_coverage_reference"]["tag"] == runner.ADMISSION_COVERAGE_REFERENCE_TAG
    assert boundaries["canonical_coverage_repair"]["commit"] == runner.CANONICAL_COVERAGE_REPAIR_COMMIT
    assert boundaries["canonical_coverage_repair"]["tag"] == runner.CANONICAL_COVERAGE_REPAIR_TAG
    assert boundaries["compression_source_boundary"]["commit"] == runner.COMPRESSION_SOURCE_COMMIT
    assert boundaries["compression_source_boundary"]["tag"] == runner.COMPRESSION_SOURCE_TAG
    assert boundaries["prior_readiness_audit"]["commit"] == runner.PRIOR_READINESS_AUDIT_COMMIT
    assert boundaries["prior_readiness_audit"]["runtime_authorized"] is False
    assert boundaries["post_bridge_admission_executable_001d"]["artifact_path"] == "artifacts/post_bridge_admission_executable_001d/result.json"
    assert boundaries["post_bridge_admission_executable_001d"]["commit"] == "c2f6c5184a119202dd0a7efc23d3bfe3317af890"
    assert boundaries["post_bridge_admission_executable_001d"]["verdict"] == "post_bridge_admission_executable_001d_pass"
    assert post_bridge["resolved"] is True
    assert post_bridge["blocked_reason"] is None
    assert post_bridge["treat_as_mechanism_proof"] is False


def test_existing_contract_search_and_schema_duplication_policy():
    search = _read_json(ARTIFACT_DIR / "existing_admission_task_card_search_report.json")
    schema_guard = _read_json(ARTIFACT_DIR / "schema_duplication_guard.json")
    result = _read_json(ARTIFACT_DIR / "result.json")

    assert search["search_executed"] is True
    assert search["complete_equivalent_contract_found"] is False
    assert search["partial_contract_found"] is True
    assert "docs/codex/tasks/EGO-MAINLINE-ADMISSION-TASK-CARD-001A.md" in search["partial_contract_paths"]
    assert schema_guard["alignment_document_mode"] == "amendment_to_existing_admission_task_card_001a"
    assert schema_guard["duplicate_schema_created"] is False
    assert result["verdict"] == _runner().VERDICT_PASS


def test_authorization_actionability_hyperon_and_matrix_guards():
    auth = _read_json(ARTIFACT_DIR / "authorization_guard.json")
    evidence = _read_json(ARTIFACT_DIR / "evidence_usage_contract.json")
    actionability = _read_json(ARTIFACT_DIR / "actionability_revalidation_matrix.json")
    schema_guard = _read_json(ARTIFACT_DIR / "schema_duplication_guard.json")

    for field in _runner().AUTHORIZATION_FALSE_FIELDS:
        assert auth["authorization_flags"][field] is False
        assert evidence["authorization_flags"][field] is False
    assert auth["actionability_revalidation_required"] is True
    assert evidence["hyperon_adopted"] is False
    assert actionability["actionability_revalidation_required"] is True
    assert all(row["required"] is True for row in actionability["revalidation_rows"])
    assert schema_guard["matrix_duplication_allowed"] is False
    assert schema_guard["copied_45_row_matrix_detected"] is False

    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt"}:
        payload = _read_json(ARTIFACT_DIR / name)
        for path, value in _walk(payload):
            assert not (
                isinstance(value, list)
                and len(value) == 45
                and all(isinstance(item, dict) and "candidate_id" in item for item in value)
            ), f"copied 45-row matrix detected at {name}:{path}"


def test_computed_gate_negative_evidence_and_claim_ceiling_are_preserved():
    computed = _read_json(ARTIFACT_DIR / "computed_evidence_gate_contract.json")
    negative = _read_json(ARTIFACT_DIR / "negative_evidence_handling_contract.json")
    result = _read_json(ARTIFACT_DIR / "result.json")

    assert computed["computed_evidence_gate_required_for_future_execution"] is True
    assert computed["static_or_literal_verdicts_allowed"] is False
    assert computed["required_metadata_fields"]
    statuses = {row["task_id"]: row for row in negative["negative_evidence_rows"]}
    assert statuses["POST-BRIDGE-ADMISSION-EXECUTABLE-001B"]["positive_evidence_allowed"] is False
    assert statuses["POST-BRIDGE-ADMISSION-EXECUTABLE-001C"]["positive_evidence_allowed"] is False
    assert statuses["POST-BRIDGE-ADMISSION-EXECUTABLE-001D"]["mechanism_proof_allowed"] is False
    assert set(result["what_this_does_not_prove"]).issuperset(REQUIRED_CLAIMS)


def test_negative_controls_fail_through_callable_validators():
    result = _read_json(ARTIFACT_DIR / "result.json")
    controls = {row["mutation_id"]: row for row in result["negative_controls"]["controls"]}
    expected = {
        "implementation_authorized_true",
        "runtime_authorized_true",
        "admission_reference_removed",
        "canonical_repair_removed",
        "actionability_revalidation_removed",
        "prior_readiness_audit_runtime_authorized",
        "post_bridge_001d_as_mechanism_proof",
        "hyperon_adopted_true",
        "matrix_duplication_allowed_true",
        "computed_evidence_gate_removed",
        "negative_evidence_handling_removed",
    }
    assert set(controls) == expected
    assert result["negative_controls"]["all_negative_controls_failed"] is True
    for row in controls.values():
        assert row["validation_failed"] is True
        assert row["failing_validators"]


def test_source_trace_covers_new_artifacts_and_metadata_exists():
    trace = _read_json(ARTIFACT_DIR / "source_trace_report.json")
    traced = {Path(row["artifact"]).name for row in trace["trace_rows"]}
    assert REQUIRED_ARTIFACTS.issubset(traced)
    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt"}:
        rows = [row for row in trace["trace_rows"] if Path(row["artifact"]).name == name]
        boundaries = {row["referenced_boundary"] for row in rows}
        assert "admission_coverage_reference" in boundaries
        assert "canonical_coverage_repair" in boundaries
        assert "post_bridge_admission_executable_001d" in boundaries
        payload = _read_json(ARTIFACT_DIR / name)
        meta = payload.get("computed_evidence_provenance")
        assert meta
        assert meta["producer_function"]
        assert meta["input_artifacts"]
        assert meta["run_id"]
        assert meta["code_path_hash"]
        assert meta["aggregation_rule"]
        assert meta["validation_rule"]
        assert meta["output_artifact_hash"]


def test_callable_validators_reject_mutated_contracts():
    runner = _runner()
    contract = _read_json(ARTIFACT_DIR / "evidence_usage_contract.json")
    post_bridge = _read_json(ARTIFACT_DIR / "post_bridge_boundary_resolution_report.json")
    clean = runner.validate_alignment_contract(contract, post_bridge)
    assert all(row["passed"] for row in clean)

    mutated = copy.deepcopy(contract)
    mutated["authorization_flags"]["implementation_authorized"] = True
    failed = runner.validate_alignment_contract(mutated, post_bridge)
    assert any(row["validator"] == "validate_authorization_guards" and not row["passed"] for row in failed)

    mutated = copy.deepcopy(contract)
    mutated["computed_evidence_gate_required_for_future_execution"] = False
    failed = runner.validate_alignment_contract(mutated, post_bridge)
    assert any(row["validator"] == "validate_computed_evidence_gate" and not row["passed"] for row in failed)


def test_no_sealed_or_parent_artifacts_modified():
    result = _read_json(ARTIFACT_DIR / "result.json")
    assert result["protected_parent_artifacts_modified"] is False
    assert result["protected_parent_hashes_before"] == result["protected_parent_hashes_after"]
    current_hashes = _runner().hash_protected_inputs(ROOT)
    assert current_hashes == result["protected_parent_hashes_after"]


def test_temp_run_uses_same_validators(tmp_path):
    runner = _runner()
    out = tmp_path / "alignment"
    result = runner.run_alignment_contract(repo_root=ROOT, output_dir=out)
    assert result["verdict"] == runner.VERDICT_PASS
    assert result["all_validators_passed"] is True
    assert result["negative_controls"]["all_negative_controls_failed"] is True
    assert _read_json(out / "parent_evidence_boundary_manifest.json")["parent_boundaries"][0]["commit"] == runner.ADMISSION_COVERAGE_REFERENCE_COMMIT
