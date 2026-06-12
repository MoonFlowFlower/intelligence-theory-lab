import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from theory_landscape_coverage_canonicalization_001a.runner import (  # noqa: E402
    CLAIM_CEILING,
    KNOWN_BLOCKED_TRACE_HASH,
    REQUIRED_GRAPH_CHALLENGERS,
    repair_canonicalization_provenance_001b,
)


CANONICAL_DIR = ROOT / "artifacts" / "theory_landscape_coverage_canonicalization_001a"
REPAIR_DIR = (
    ROOT / "artifacts" / "theory_landscape_coverage_canonicalization_provenance_repair_001b"
)
DOC = (
    ROOT
    / "docs"
    / "research"
    / "THEORY-LANDSCAPE-COVERAGE-CANONICALIZATION-PROVENANCE-REPAIR-001B.md"
)
SOURCE_FILES = {
    ROOT / "docs/research/THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001D.md",
    ROOT / "artifacts/theory_landscape_coverage_precanonical_closure_patch_001b/source_pin_readback.json",
    ROOT / "artifacts/theory_landscape_coverage_precanonical_closure_patch_001b/delta_manifest.json",
    ROOT / "artifacts/theory_landscape_coverage_precanonical_closure_patch_001b/closure_caveat_resolution_matrix.json",
    ROOT / "artifacts/theory_landscape_coverage_precanonical_closure_patch_001b/schema_safety_check.json",
    ROOT / "artifacts/theory_landscape_coverage_precanonical_closure_patch_001b/claim_ceiling.txt",
    ROOT / "docs/research/PHASE-ONE-THEORY-LANDSCAPE-COVERAGE-AUDIT.md",
}
EXPECTED_REPAIR_ARTIFACTS = {
    "blocker_report.json",
    "old_artifact_hashes_before.json",
    "repaired_artifact_hashes_after.json",
    "provenance_repair_delta.json",
    "trace_artifact_provenance_entry.json",
    "repair_validation_report.json",
    "result.json",
    "claim_ceiling.txt",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _copy_canonical_dir(tmp_path: Path) -> Path:
    copied = tmp_path / "canonical"
    shutil.copytree(CANONICAL_DIR, copied)
    provenance_path = copied / "canonicalization_provenance.json"
    provenance = _read_json(provenance_path)
    provenance.pop("trace_artifact_provenance", None)
    provenance.pop("provenance_repair_note", None)
    provenance["canonical_artifact_provenance"] = [
        row
        for row in provenance.get("canonical_artifact_provenance", [])
        if row.get("artifact_name") != "source_to_canonical_trace.json"
    ]
    if not provenance["canonical_artifact_provenance"]:
        provenance.pop("canonical_artifact_provenance", None)
    provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return copied


def test_repair_adds_trace_artifact_provenance_and_required_repair_artifacts(tmp_path):
    before_source_hashes = {path: _file_sha(path) for path in SOURCE_FILES if path.exists()}
    canonical_copy = _copy_canonical_dir(tmp_path)

    result = repair_canonicalization_provenance_001b(
        repo_root=ROOT, canonical_dir=canonical_copy, repair_dir=tmp_path / "repair"
    )

    provenance = _read_json(canonical_copy / "canonicalization_provenance.json")
    entry = provenance["trace_artifact_provenance"]["source_to_canonical_trace.json"]
    actual_trace_hash = _file_sha(canonical_copy / "source_to_canonical_trace.json")
    repair_entry = _read_json(tmp_path / "repair" / "trace_artifact_provenance_entry.json")

    assert result["task_id"] == "THEORY-LANDSCAPE-COVERAGE-CANONICALIZATION-PROVENANCE-REPAIR-001B"
    assert result["verdict"] == "theory_landscape_coverage_canonicalization_provenance_repair_001b_pass"
    assert EXPECTED_REPAIR_ARTIFACTS.issubset({path.name for path in (tmp_path / "repair").iterdir()})
    assert entry == repair_entry
    assert entry["artifact_name"] == "source_to_canonical_trace.json"
    assert entry["output_artifact_hash"] == actual_trace_hash
    assert entry["producer_function"]
    assert entry["input_artifacts"] or entry["generation_input_references"]
    assert entry["run_id"]
    assert entry["code_path_hash"]
    assert entry["aggregation_rule"]
    assert entry["validation_rule"]
    assert entry["known_blocked_hash_consistency_check"]["known_hash"] == KNOWN_BLOCKED_TRACE_HASH
    assert entry["known_blocked_hash_consistency_check"]["computed_hash"] == actual_trace_hash
    assert entry["known_blocked_hash_consistency_check"]["used_as_proof"] is False
    assert {path: _file_sha(path) for path in SOURCE_FILES if path.exists()} == before_source_hashes


def test_repair_artifacts_record_before_after_hashes_and_invariant_preservation(tmp_path):
    canonical_copy = _copy_canonical_dir(tmp_path)

    repair_canonicalization_provenance_001b(
        repo_root=ROOT, canonical_dir=canonical_copy, repair_dir=tmp_path / "repair"
    )

    before = _read_json(tmp_path / "repair" / "old_artifact_hashes_before.json")
    after = _read_json(tmp_path / "repair" / "repaired_artifact_hashes_after.json")
    delta = _read_json(tmp_path / "repair" / "provenance_repair_delta.json")
    validation = _read_json(tmp_path / "repair" / "repair_validation_report.json")
    result = _read_json(tmp_path / "repair" / "result.json")

    assert before["source_artifact_hashes_before"] == after["source_artifact_hashes_after"]
    assert delta["canonicalization_provenance_hash_before"] != delta["canonicalization_provenance_hash_after"]
    assert delta["source_to_canonical_trace_hash_before"] == delta["source_to_canonical_trace_hash_after"]
    assert delta["trace_artifact_hash_computed_by_callable_code"] is True
    assert delta["known_blocked_hash_used_as_proof"] is False
    assert validation["passed"] is True
    assert validation["source_artifacts_modified"] is False
    assert validation["canonical_claim_ceiling_unchanged"] is True
    assert result["old_source_artifacts_modified"] is False
    assert result["implementation_authorized"] is False


def test_repair_preserves_canonicalization_invariants_and_claim_ceiling(tmp_path):
    canonical_copy = _copy_canonical_dir(tmp_path)

    repair_canonicalization_provenance_001b(
        repo_root=ROOT, canonical_dir=canonical_copy, repair_dir=tmp_path / "repair"
    )

    matrix = _read_json(canonical_copy / "canonical_theory_coverage_matrix.json")
    family = _read_json(canonical_copy / "canonical_family_accounting.json")
    auth = _read_json(canonical_copy / "canonical_authorization_flags.json")
    hyperon = _read_json(canonical_copy / "hyperon_non_adoption_guard.json")
    admission = _read_json(canonical_copy / "admission_reference_guard.json")
    claim_ceiling = (canonical_copy / "canonical_claim_ceiling.txt").read_text(encoding="utf-8")
    rows = matrix["rows"]
    hyperon_rows = [row for row in rows if "hyperon" in row["candidate_id"]]

    assert matrix["row_count"] == 45
    assert len(rows) == 45
    assert family["item_count"] == 30
    assert len(family["family_accounting"]) == 30
    assert set(family["graph_substrate_challenger_family"]) == set(REQUIRED_GRAPH_CHALLENGERS)
    assert len(hyperon_rows) == 1
    assert hyperon["canonical_hyperon_row_count"] == 1
    assert hyperon["hyperon_not_adopted"] is True
    assert hyperon["hyperon_not_runtime_authorized"] is True
    assert hyperon["hyperon_not_implementation_authorized"] is True
    assert hyperon["hyperon_not_ego_mainline_dependency"] is True
    assert all(row["implementation_authorized"] is False for row in rows)
    assert all(item["implementation_authorized"] is False for item in family["family_accounting"])
    assert all(value is False for value in auth["non_authorization_flags"].values())
    assert admission["committed_audit_reference_only"] is True
    assert admission["actionability_revalidation_required"] is True
    assert claim_ceiling.startswith(CLAIM_CEILING)


def test_materialized_repair_doc_and_artifacts_exist_after_repair():
    assert DOC.exists()
    assert EXPECTED_REPAIR_ARTIFACTS.issubset({path.name for path in REPAIR_DIR.iterdir()})
    result = _read_json(REPAIR_DIR / "result.json")
    entry = _read_json(REPAIR_DIR / "trace_artifact_provenance_entry.json")
    actual_trace_hash = _file_sha(CANONICAL_DIR / "source_to_canonical_trace.json")

    assert result["verdict"] == "theory_landscape_coverage_canonicalization_provenance_repair_001b_pass"
    assert entry["output_artifact_hash"] == actual_trace_hash
    assert (REPAIR_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == (
        "bounded provenance repair for repo-canonicalized theory coverage only"
    )
