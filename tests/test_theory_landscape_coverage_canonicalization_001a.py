import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from theory_landscape_coverage_canonicalization_001a.runner import (  # noqa: E402
    EXPECTED_COMMIT,
    EXPECTED_REMOTE_TAG,
    KNOWN_BLOCKED_TRACE_HASH,
    REQUIRED_GRAPH_CHALLENGERS,
    canonicalize_coverage_001a,
    compute_trace_artifact_provenance_entry,
    load_inputs,
    run_ablation_failure_checks,
    run_baseline_validation,
    validate_canonical_outputs,
)


ARTIFACT_DIR = ROOT / "artifacts" / "theory_landscape_coverage_canonicalization_001a"
DOC = ROOT / "docs" / "research" / "THEORY-LANDSCAPE-COVERAGE-CANONICALIZATION-001A.md"
SOURCE_DOC = ROOT / "docs" / "research" / "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001D.md"
SOURCE_ARTIFACT_DIR = ROOT / "artifacts" / "theory_landscape_coverage_precanonical_closure_patch_001b"

EXPECTED_ARTIFACTS = {
    "canonical_theory_coverage_matrix.json",
    "canonical_family_accounting.json",
    "canonical_internal_evidence_lineage.json",
    "canonical_authorization_flags.json",
    "canonical_claim_ceiling.txt",
    "source_to_canonical_trace.json",
    "canonicalization_provenance.json",
    "baseline_validation_report.json",
    "ablation_failure_report.json",
    "schema_validation_report.json",
    "hyperon_non_adoption_guard.json",
    "admission_reference_guard.json",
    "result.json",
}

FORBIDDEN_CLAIMS = {
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
    "real emotion",
    "real relationship learning",
    "subjective experience",
    "stable user benefit",
    "future EGO runtime correctness",
}

SOURCE_FILES = {
    SOURCE_DOC,
    SOURCE_ARTIFACT_DIR / "source_pin_readback.json",
    SOURCE_ARTIFACT_DIR / "delta_manifest.json",
    SOURCE_ARTIFACT_DIR / "closure_caveat_resolution_matrix.json",
    SOURCE_ARTIFACT_DIR / "schema_safety_check.json",
    SOURCE_ARTIFACT_DIR / "claim_ceiling.txt",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_001a_run_emits_required_artifacts_and_doc(tmp_path):
    result = canonicalize_coverage_001a(repo_root=ROOT, output_dir=tmp_path)

    assert result["task_id"] == "THEORY-LANDSCAPE-COVERAGE-CANONICALIZATION-001A"
    assert result["commit_hash"] == EXPECTED_COMMIT
    assert result["remote_tag"] == EXPECTED_REMOTE_TAG
    assert result["verdict"] == "theory_landscape_coverage_canonicalization_001a_pass"
    assert result["claim_ceiling"] == "bounded repo-canonicalization evidence for already source-pinned theory coverage only"
    assert result["implementation_authorized"] is False
    assert EXPECTED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    assert DOC.exists()

    for artifact_name in EXPECTED_ARTIFACTS - {"canonical_claim_ceiling.txt"}:
        parsed = _read_json(tmp_path / artifact_name)
        assert parsed


def test_source_commit_tag_and_source_artifact_references_match_required_anchor(tmp_path):
    canonicalize_coverage_001a(repo_root=ROOT, output_dir=tmp_path)
    provenance = _read_json(tmp_path / "canonicalization_provenance.json")
    result = _read_json(tmp_path / "result.json")

    assert provenance["source_commit"] == EXPECTED_COMMIT
    assert provenance["remote_tag"] == EXPECTED_REMOTE_TAG
    assert provenance["source_tag_resolved_commit"] == EXPECTED_COMMIT
    assert result["commit_hash"] == EXPECTED_COMMIT
    assert result["remote_tag"] == EXPECTED_REMOTE_TAG
    assert set(provenance["required_input_artifacts"]) == {
        "docs/research/THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001D.md",
        "artifacts/theory_landscape_coverage_precanonical_closure_patch_001b/source_pin_readback.json",
        "artifacts/theory_landscape_coverage_precanonical_closure_patch_001b/delta_manifest.json",
        "artifacts/theory_landscape_coverage_precanonical_closure_patch_001b/closure_caveat_resolution_matrix.json",
        "artifacts/theory_landscape_coverage_precanonical_closure_patch_001b/schema_safety_check.json",
        "artifacts/theory_landscape_coverage_precanonical_closure_patch_001b/claim_ceiling.txt",
    }


def test_canonical_matrix_family_accounting_hyperon_and_authorization_flags(tmp_path):
    canonicalize_coverage_001a(repo_root=ROOT, output_dir=tmp_path)

    matrix = _read_json(tmp_path / "canonical_theory_coverage_matrix.json")
    family = _read_json(tmp_path / "canonical_family_accounting.json")
    auth = _read_json(tmp_path / "canonical_authorization_flags.json")
    hyperon = _read_json(tmp_path / "hyperon_non_adoption_guard.json")

    rows = matrix["rows"]
    hyperon_rows = [row for row in rows if row["candidate_id"] == "hyperon_metta_atomspace"]

    assert matrix["row_count"] == 45
    assert len(rows) == 45
    assert family["item_count"] == 30
    assert len(family["family_accounting"]) == 30
    assert set(family["graph_substrate_challenger_family"]) == set(REQUIRED_GRAPH_CHALLENGERS)
    assert len(hyperon_rows) == 1
    assert hyperon["canonical_hyperon_row_count"] == 1
    assert hyperon["hyperon_not_adopted"] is True
    assert hyperon["hyperon_not_implementation_authorized"] is True
    assert hyperon["hyperon_not_runtime_authorized"] is True
    assert hyperon["hyperon_not_ego_mainline_dependency"] is True
    assert hyperon_rows[0]["selected_as_architecture"] is False
    assert hyperon_rows[0]["implementation_authorized"] is False
    assert hyperon_rows[0]["runtime_authorized"] is False
    assert hyperon_rows[0]["ego_mainline_authorized"] is False
    assert all(row["implementation_authorized"] is False for row in rows)
    assert all(item["implementation_authorized"] is False for item in family["family_accounting"])
    assert all(value is False for value in auth["non_authorization_flags"].values())


def test_admission_reference_guard_and_claim_ceiling_forbid_inflated_claims(tmp_path):
    canonicalize_coverage_001a(repo_root=ROOT, output_dir=tmp_path)

    admission = _read_json(tmp_path / "admission_reference_guard.json")
    result = _read_json(tmp_path / "result.json")
    claim_ceiling = (tmp_path / "canonical_claim_ceiling.txt").read_text(encoding="utf-8")

    assert admission["reference"] == "EGO-MAINLINE-READINESS-AUDIT-001B"
    assert admission["committed_audit_reference_only"] is True
    assert admission["actionability_revalidation_required"] is True
    assert admission["runtime_authorized"] is False
    assert admission["implementation_authorized"] is False
    assert admission["downstream_positive_evidence"] is False
    assert set(FORBIDDEN_CLAIMS).issubset(set(result["forbidden_claims"]))

    for forbidden in FORBIDDEN_CLAIMS:
        assert forbidden in claim_ceiling
    assert "No architecture selection" in claim_ceiling
    assert "implementation authorization = false" in claim_ceiling


def test_callable_baseline_validator_is_invoked_and_agrees(tmp_path):
    inputs = load_inputs(ROOT)
    canonicalize_coverage_001a(repo_root=ROOT, output_dir=tmp_path)

    report = run_baseline_validation(inputs, tmp_path)
    persisted = _read_json(tmp_path / "baseline_validation_report.json")

    assert report["baseline_validator_invoked"] is True
    assert persisted["baseline_validator_invoked"] is True
    assert report["baseline_validator"] != "primary_canonicalizer"
    assert report["passed"] is True
    assert report["checks"]["row_count"]["observed"] == 45
    assert report["checks"]["family_accounting_count"]["observed"] == 30
    assert set(report["checks"]["graph_challenger_family"]["observed"]) == set(REQUIRED_GRAPH_CHALLENGERS)
    assert report["checks"]["hyperon_single_row"]["passed"] is True
    assert report["checks"]["all_implementation_authorized_false"]["passed"] is True
    assert report["provenance"]["producer_function"]
    assert report["provenance"]["code_path_hash"]


def test_ablation_validators_fail_on_real_mutated_inputs(tmp_path):
    inputs = load_inputs(ROOT)
    canonicalize_coverage_001a(repo_root=ROOT, output_dir=tmp_path)

    report = run_ablation_failure_checks(inputs, tmp_path)
    persisted = _read_json(tmp_path / "ablation_failure_report.json")

    expected = {
        "remove_graph_challenger_family_item",
        "change_hyperon_adoption_flag_true",
        "change_any_implementation_authorized_true",
        "drop_source_pin_remote_anchor_reference",
        "reduce_45_row_matrix_to_partial_matrix",
        "remove_claim_ceiling",
    }
    assert set(report["ablations"]) == expected
    assert persisted["ablation_validators_invoked"] is True
    assert report["all_negative_controls_failed"] is True
    assert all(row["validator_invoked"] for row in report["ablations"].values())
    assert all(row["expected_failure_observed"] for row in report["ablations"].values())
    assert all(row["mutated_input_hash"] != row["original_input_hash"] for row in report["ablations"].values())


def test_source_to_canonical_trace_covers_every_canonical_artifact_with_provenance(tmp_path):
    canonicalize_coverage_001a(repo_root=ROOT, output_dir=tmp_path)
    trace = _read_json(tmp_path / "source_to_canonical_trace.json")

    trace_artifacts = {row["canonical_artifact"] for row in trace["trace_rows"]}
    assert EXPECTED_ARTIFACTS - {"source_to_canonical_trace.json"} <= trace_artifacts
    assert trace["trace_complete"] is True

    required_fields = {
        "canonical_artifact",
        "canonical_field",
        "source_artifact",
        "source_field_or_section",
        "producer_function",
        "input_artifact_hash",
        "output_artifact_hash",
        "run_id",
        "code_path_hash",
        "aggregation_rule",
        "validation_rule",
    }
    for row in trace["trace_rows"]:
        assert required_fields.issubset(row)
        assert row["producer_function"]
        assert row["input_artifact_hash"]
        assert row["output_artifact_hash"]
        assert row["run_id"]
        assert row["code_path_hash"]
        assert row["aggregation_rule"]
        assert row["validation_rule"]


def test_schema_validation_requires_computed_paths_not_literal_pass_labels(tmp_path):
    canonicalize_coverage_001a(repo_root=ROOT, output_dir=tmp_path)

    schema = _read_json(tmp_path / "schema_validation_report.json")
    provenance = _read_json(tmp_path / "canonicalization_provenance.json")
    result = _read_json(tmp_path / "result.json")

    assert schema["passed"] is True
    assert schema["baseline_validator_invoked"] is True
    assert schema["ablation_validators_invoked"] is True
    assert schema["computed_evidence_provenance_gate"]["passed"] is True
    assert schema["computed_evidence_provenance_gate"]["literal_only_assertions_detected"] is False
    assert provenance["producer_function"] == "canonicalize_coverage_001a"
    assert provenance["baseline_validator_function"] == "run_baseline_validation"
    assert provenance["ablation_validator_function"] == "run_ablation_failure_checks"
    assert provenance["code_path_hash"]
    assert result["baseline_validator_invoked"] is True
    assert result["ablation_validators_invoked"] is True


def test_canonicalization_provenance_records_trace_artifact_hash_from_callable_path(tmp_path):
    canonicalize_coverage_001a(repo_root=ROOT, output_dir=tmp_path)

    provenance = _read_json(tmp_path / "canonicalization_provenance.json")
    entry = provenance["trace_artifact_provenance"]["source_to_canonical_trace.json"]
    actual_trace_hash = _file_sha(tmp_path / "source_to_canonical_trace.json")
    recomputed_entry = compute_trace_artifact_provenance_entry(tmp_path)

    assert entry["artifact_name"] == "source_to_canonical_trace.json"
    assert entry["output_artifact_hash"] == actual_trace_hash
    assert recomputed_entry["output_artifact_hash"] == actual_trace_hash
    assert entry["producer_function"]
    assert entry["producer_function"] == recomputed_entry["producer_function"]
    assert entry["artifact_producer_function"] == "_build_trace"
    assert entry["run_id"]
    assert entry["code_path_hash"]
    assert entry["aggregation_rule"]
    assert entry["validation_rule"]
    assert entry["proof_source"] == "computed_sha256_from_trace_artifact_bytes"
    assert entry["known_blocked_hash_consistency_check"]["known_hash"] == KNOWN_BLOCKED_TRACE_HASH
    assert entry["known_blocked_hash_consistency_check"]["used_as_proof"] is False


def test_no_old_source_artifacts_are_mutated(tmp_path):
    before = {path: _file_sha(path) for path in SOURCE_FILES}

    canonicalize_coverage_001a(repo_root=ROOT, output_dir=tmp_path)

    after = {path: _file_sha(path) for path in SOURCE_FILES}
    result = _read_json(tmp_path / "result.json")

    assert after == before
    assert result["old_source_artifacts_modified"] is False
    assert result["old_source_artifact_hashes_before"] == {
        str(path.relative_to(ROOT)).replace("\\", "/"): digest for path, digest in before.items()
    }
    assert result["old_source_artifact_hashes_after"] == {
        str(path.relative_to(ROOT)).replace("\\", "/"): digest for path, digest in after.items()
    }


def test_validate_canonical_outputs_rejects_missing_trace_coverage(tmp_path):
    canonicalize_coverage_001a(repo_root=ROOT, output_dir=tmp_path)
    trace_path = tmp_path / "source_to_canonical_trace.json"
    trace = _read_json(trace_path)
    trace["trace_rows"] = trace["trace_rows"][:-1]
    trace_path.write_text(json.dumps(trace, indent=2), encoding="utf-8")

    report = validate_canonical_outputs(tmp_path)

    assert report["passed"] is False
    assert "source_to_canonical_trace_incomplete" in report["failures"]
