import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ego_mainline_admission_canonical_coverage_reference_001a import runner  # noqa: E402


ARTIFACT_DIR = ROOT / "artifacts" / "ego_mainline_admission_canonical_coverage_reference_001a"
DOC = ROOT / "docs" / "research" / "EGO-MAINLINE-ADMISSION-CANONICAL-COVERAGE-REFERENCE-001A.md"
REQUIRED_ARTIFACTS = {
    "result.json",
    "reference_contract.json",
    "sealed_input_anchor_manifest.json",
    "downstream_usage_matrix.json",
    "forbidden_claims_matrix.json",
    "implementation_authorization_guard.json",
    "hyperon_non_adoption_guard.json",
    "admission_actionability_revalidation_guard.json",
    "duplication_prevention_report.json",
    "existing_reference_search_report.json",
    "source_trace_report.json",
    "claim_ceiling.txt",
}
REQUIRED_FORBIDDEN = {
    "EGO readiness",
    "AGI readiness",
    "bridge readiness",
    "companion readiness",
    "mechanism validity",
    "theory validity",
    "architecture correctness",
    "agency",
    "selfhood",
    "consciousness",
    "subjective experience",
    "real emotion",
    "real relationship learning",
    "stable user benefit",
    "future EGO runtime correctness",
}


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


def test_materialized_required_artifacts_exist_and_json_parse():
    assert DOC.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})

    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt"}:
        payload = _read_json(ARTIFACT_DIR / name)
        assert isinstance(payload, dict)

    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == runner.CLAIM_CEILING


def test_reference_contract_records_required_anchors_and_prior_audit_reference_only():
    contract = _read_json(ARTIFACT_DIR / "reference_contract.json")
    manifest = _read_json(ARTIFACT_DIR / "sealed_input_anchor_manifest.json")

    assert contract["sealed_coverage_commit"] == runner.SEALED_COVERAGE_COMMIT
    assert contract["sealed_coverage_remote_tag"] == runner.SEALED_COVERAGE_REMOTE_TAG
    assert contract["underlying_source_commit"] == runner.UNDERLYING_SOURCE_COMMIT
    assert contract["underlying_source_remote_tag"] == runner.UNDERLYING_SOURCE_REMOTE_TAG
    assert contract["prior_admission_audit_commit"] == runner.PRIOR_ADMISSION_AUDIT_COMMIT
    assert "reference only" in contract["prior_admission_audit_status"]
    assert "runtime" in " ".join(contract["prior_admission_audit_does_not_authorize"])
    assert manifest["sealed_coverage_anchor"]["remote_verified"] is True
    assert manifest["underlying_source_anchor"]["remote_verified"] is True
    assert manifest["prior_admission_audit"]["reference_only"] is True
    assert manifest["prior_admission_audit"]["runtime_authorized"] is False


def test_authorization_guards_and_actionability_revalidation_are_false_or_required():
    contract = _read_json(ARTIFACT_DIR / "reference_contract.json")
    implementation = _read_json(ARTIFACT_DIR / "implementation_authorization_guard.json")
    admission = _read_json(ARTIFACT_DIR / "admission_actionability_revalidation_guard.json")

    assert contract["implementation_authorized"] is False
    assert contract["runtime_authorized"] is False
    assert contract["bridge_authorized"] is False
    assert contract["companion_authorized"] is False
    assert contract["architecture_adopted"] is False
    assert contract["hyperon_adopted"] is False
    assert contract["actionability_revalidation_required"] is True
    assert contract["matrix_duplication_allowed"] is False
    assert implementation["all_authorization_guards_passed"] is True
    assert admission["committed_audit_reference_only"] is True
    assert admission["canonical_admission_reference_only"] is True
    assert admission["actionability_revalidation_required"] is True


def test_hyperon_non_adoption_and_forbidden_claims_matrix():
    hyperon = _read_json(ARTIFACT_DIR / "hyperon_non_adoption_guard.json")
    forbidden = _read_json(ARTIFACT_DIR / "forbidden_claims_matrix.json")

    assert hyperon["canonical_hyperon_row_count"] == 1
    assert hyperon["hyperon_adopted"] is False
    assert hyperon["hyperon_implementation_authorized"] is False
    assert hyperon["hyperon_runtime_authorized"] is False
    assert hyperon["hyperon_ego_mainline_dependency"] is False
    assert hyperon["hyperon_not_adopted"] is True
    blocked_claims = {row["claim"] for row in forbidden["forbidden_claims"] if row["blocked"] is True}
    assert REQUIRED_FORBIDDEN.issubset(blocked_claims)


def test_no_new_artifact_copies_the_45_row_canonical_matrix():
    duplication = _read_json(ARTIFACT_DIR / "duplication_prevention_report.json")
    assert duplication["matrix_duplication_allowed"] is False
    assert duplication["copied_45_row_matrix_detected"] is False

    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt"}:
        payload = _read_json(ARTIFACT_DIR / name)
        for path, value in _walk(payload):
            assert not (
                isinstance(value, list)
                and len(value) == 45
                and all(isinstance(item, dict) and "candidate_id" in item for item in value)
            ), f"copied 45-row matrix detected at {name}:{path}"


def test_existing_reference_search_found_no_equivalent_contract():
    search = _read_json(ARTIFACT_DIR / "existing_reference_search_report.json")
    result = _read_json(ARTIFACT_DIR / "result.json")

    assert search["equivalent_reference_contract_found"] is False
    assert search["equivalent_reference_contracts"] == []
    assert result["existing_reference_contract_found"] is False
    assert result["verdict"] == runner.VERDICT_PASS


def test_ablation_controls_fail_through_callable_validators():
    result = _read_json(ARTIFACT_DIR / "result.json")
    ablations = result["ablation_negative_controls"]

    assert ablations["all_negative_controls_failed"] is True
    expected = {
        "implementation_authorized_true": "validate_authorization_guards",
        "runtime_authorized_true": "validate_authorization_guards",
        "hyperon_adopted_true": "validate_hyperon_non_adoption",
        "sealed_coverage_commit_removed": "validate_sealed_anchor_reference",
        "sealed_remote_tag_removed": "validate_sealed_anchor_reference",
        "matrix_duplication_allowed_true": "validate_no_matrix_duplication",
        "actionability_revalidation_removed": "validate_actionability_revalidation_required",
        "forbidden_claim_list_removed": "validate_claim_ceiling",
    }
    observed = {row["mutation_id"]: row for row in ablations["negative_controls"]}
    assert set(observed) == set(expected)
    for mutation_id, validator in expected.items():
        assert observed[mutation_id]["validation_failed"] is True
        assert validator in observed[mutation_id]["failing_validators"]


def test_source_trace_covers_every_new_reference_artifact():
    trace = _read_json(ARTIFACT_DIR / "source_trace_report.json")
    traced = {Path(row["artifact"]).name for row in trace["trace_rows"]}

    assert REQUIRED_ARTIFACTS.issubset(traced)
    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt"}:
        rows = [row for row in trace["trace_rows"] if Path(row["artifact"]).name == name]
        boundaries = {row["referenced_boundary"] for row in rows}
        assert "sealed_coverage_repair" in boundaries
        assert "underlying_source_coverage_compression" in boundaries
        assert "prior_admission_audit" in boundaries
        assert all(row["producer_function"] for row in rows)
        assert all(row["run_id"] for row in rows)
        assert all(row["code_path_hash"] for row in rows)
        assert all(row["validation_rule"] for row in rows)
        assert all(row["output_artifact_hash"] for row in rows)


def test_computed_evidence_metadata_exists_for_json_artifacts():
    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt"}:
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
    contract = _read_json(ARTIFACT_DIR / "reference_contract.json")
    canonical = runner._load_canonical_inputs(ROOT)

    clean = runner.validate_reference_contract(contract, canonical)
    assert all(row["passed"] for row in clean)

    mutated = copy.deepcopy(contract)
    mutated["implementation_authorized"] = True
    failed = runner.validate_reference_contract(mutated, canonical)
    assert any(
        row["validator"] == "validate_authorization_guards" and row["passed"] is False
        for row in failed
    )

    mutated = copy.deepcopy(contract)
    mutated["forbidden_downstream_use"] = []
    failed = runner.validate_reference_contract(mutated, canonical)
    assert any(row["validator"] == "validate_claim_ceiling" and row["passed"] is False for row in failed)


def test_no_sealed_source_or_canonical_artifact_was_modified():
    result = _read_json(ARTIFACT_DIR / "result.json")

    assert result["sealed_source_or_canonical_artifacts_modified"] is False
    assert result["protected_input_hashes_before"] == result["protected_input_hashes_after"]

    current_hashes = runner._hash_paths(ROOT, runner.PROTECTED_INPUTS)
    assert current_hashes == result["protected_input_hashes_after"]


def test_temp_run_uses_same_validators_without_remote_dependency(tmp_path):
    out = tmp_path / "reference"
    result = runner.run_reference_contract(repo_root=ROOT, output_dir=out, verify_remote=False)

    assert result["verdict"] == runner.VERDICT_PASS
    assert result["all_validators_passed"] is True
    assert result["ablation_negative_controls"]["all_negative_controls_failed"] is True
    assert _read_json(out / "reference_contract.json")["sealed_coverage_commit"] == runner.SEALED_COVERAGE_COMMIT
