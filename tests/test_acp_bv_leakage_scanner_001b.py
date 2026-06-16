import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

LEAKAGE_CLASSES = {
    "observation_name_leakage",
    "action_name_leakage",
    "filename_leakage",
    "fixture_name_leakage",
    "candidate_authored_alias_leakage",
    "future_observation_leakage",
    "hidden_truth_label_leakage",
    "answer_encoding_metadata_leakage",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_leakage_positive_controls_use_runtime_variants_and_literal_disjointness(tmp_path):
    from acp_bv_distribution_harness_001b import leakage_scanner

    report = leakage_scanner.run_leakage_positive_controls(
        run_id="pytest-leakage",
        output_artifact_path=tmp_path / "leakage_scan.json",
    )
    audit = leakage_scanner.audit_scanner_literals(
        report["runtime_generated_identifiers"],
        output_artifact_path=tmp_path / "literal_audit.json",
    )

    assert set(report["class_results"]) == LEAKAGE_CLASSES
    assert report["all_runtime_variants_detected"] is True
    assert report["all_classes_have_two_variants"] is True
    assert audit["no_runtime_identifier_in_source_literals"] is True
    assert audit["no_runtime_identifier_in_source_text"] is True
    assert all(
        row["runtime_or_heldout_variant_detected"]
        for row in report["class_results"].values()
    )
    assert all(
        len(row["variants"]) >= 2
        for row in report["class_results"].values()
    )


def test_leakage_scanner_blocks_when_runtime_variant_is_missing(tmp_path):
    from acp_bv_distribution_harness_001b import leakage_scanner

    report = leakage_scanner.run_leakage_positive_controls(
        run_id="pytest-leakage-missing-runtime",
        output_artifact_path=tmp_path / "leakage_scan.json",
    )
    first_class = next(iter(report["class_results"]))
    report["class_results"][first_class]["runtime_or_heldout_variant_detected"] = False

    validation = leakage_scanner.validate_leakage_positive_controls(report)

    assert validation["passed"] is False
    assert validation["blocking_verdict"] == "blocked_by_whitelist_leakage_scanner"


def test_runner_persists_leakage_reports(tmp_path):
    from acp_bv_distribution_harness_001b import runner

    out = tmp_path / "run"
    runner.run_harness(repo_root=ROOT, output_dir=out, run_id="pytest-leakage-runner")

    scan = _load_json(out / "leakage_scan.json")
    audit = _load_json(out / "leakage_literal_audit.json")

    assert scan["validation"]["passed"] is True
    assert audit["no_runtime_identifier_in_source_literals"] is True
    assert audit["no_runtime_identifier_in_source_text"] is True
