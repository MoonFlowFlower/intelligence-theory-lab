import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from evidence_admission_verifier_001a.core import verify_bundle
from test_evidence_admission_verifier_001a import (
    _producer_path,
    _sha256_file,
    _write_clean_bundle,
    callable_digest_metric,
)


FORGED_BUNDLE = (
    ROOT
    / "artifacts"
    / "evidence_admission_verifier_001a_real_bundle_calibration_001a"
    / "fixtures"
    / "forged_provenance_positive_control"
)

NOT_CALLABLE = "not callable"


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _clean_bundle(tmp_path: Path, name: str = "clean") -> Path:
    bundle = tmp_path / name
    _write_clean_bundle(bundle)
    return bundle


def _mutate_metric_rows(bundle: Path, mutate) -> None:
    path = bundle / "metric_provenance.jsonl"
    rows = _read_jsonl(path)
    mutate(rows)
    _write_jsonl(path, rows)


def _mutate_invocation_rows(bundle: Path, mutate) -> None:
    path = bundle / "invocation_ledger.jsonl"
    rows = _read_jsonl(path)
    mutate(rows)
    _write_jsonl(path, rows)


def _set_producer(bundle: Path, producer: str) -> None:
    module = producer.split(":", 1)[0] if ":" in producer else producer

    def metric_mutation(rows: list[dict]) -> None:
        for row in rows:
            row["producer_function"] = producer
            row["producer_module"] = module

    def invocation_mutation(rows: list[dict]) -> None:
        for row in rows:
            row["producer_function"] = producer

    _mutate_metric_rows(bundle, metric_mutation)
    _mutate_invocation_rows(bundle, invocation_mutation)


def _assert_blocks_for(bundle: Path, expected_reason: str) -> dict:
    decision = verify_bundle(bundle, run_id=f"repair-test-{bundle.name}")
    assert decision["canonical_decision"] != "admitted_for_citation"
    assert decision["admitted_for_citation"] is False
    assert expected_reason in decision["block_reason_ids"]
    reason = next(
        item
        for item in decision["block_reason_matrix"]["reasons"]
        if item["reason_id"] == expected_reason
    )
    assert reason["computed"] is True
    assert decision["verdict_text_used"] is False
    return decision


def test_valid_callable_fixture_records_executable_provenance_checks(tmp_path):
    bundle = _clean_bundle(tmp_path)

    decision = verify_bundle(bundle, run_id="repair-test-valid")

    assert decision["canonical_decision"] == "admitted_for_citation"
    assert decision["admitted_for_citation"] is True
    checks = decision["callable_provenance_checks"]
    assert len(checks) >= 5
    assert {check["producer_function"] for check in checks} == {_producer_path(callable_digest_metric)}
    assert all(check["producer_callable_invoked"] is True for check in checks)
    assert all(check["computed_input_hashes"] for check in checks)
    assert all(check["resolved_code_hash"] == check["declared_code_path_hash"].removeprefix("sha256:") for check in checks)
    assert all(check["recomputed_output_digest"] == check["declared_output_digest"].removeprefix("sha256:") for check in checks)


def test_preserved_forged_provenance_positive_control_blocks():
    assert FORGED_BUNDLE.exists()

    decision = _assert_blocks_for(FORGED_BUNDLE, "unsupported_producer_function_format")

    assert decision["decision_basis"] == "computed_bundle_evidence"
    assert decision["block_reason_matrix"]["blocking"] is True


def test_non_importable_producer_blocks(tmp_path):
    bundle = _clean_bundle(tmp_path, "non_importable")
    _set_producer(bundle, "missing_fixture_module:missing_function")

    _assert_blocks_for(bundle, "producer_function_import_failed")


def test_importable_non_callable_producer_blocks(tmp_path):
    bundle = _clean_bundle(tmp_path, "non_callable")
    _set_producer(bundle, f"{__name__}:NOT_CALLABLE")

    _assert_blocks_for(bundle, "producer_function_not_callable")


def test_wrong_code_hash_blocks(tmp_path):
    bundle = _clean_bundle(tmp_path, "wrong_code_hash")

    def mutation(rows: list[dict]) -> None:
        rows[0]["code_path_hash"] = "sha256:" + ("0" * 64)

    _mutate_metric_rows(bundle, mutation)

    _assert_blocks_for(bundle, "code_path_hash_mismatch")


def test_wrong_input_hash_blocks(tmp_path):
    bundle = _clean_bundle(tmp_path, "wrong_input_hash")

    def mutation(rows: list[dict]) -> None:
        rows[0]["input_artifact_hashes"]["inputs/episodes.jsonl"] = "sha256:" + ("1" * 64)

    _mutate_metric_rows(bundle, mutation)

    _assert_blocks_for(bundle, "input_artifact_hash_mismatch")


def test_wrong_output_digest_blocks_even_if_report_claims_pass(tmp_path):
    bundle = _clean_bundle(tmp_path, "wrong_output_digest")

    def mutation(rows: list[dict]) -> None:
        rows[0]["expected_output_digest"] = "sha256:" + ("2" * 64)

    _mutate_metric_rows(bundle, mutation)
    (bundle / "result.json").write_text(
        json.dumps({"verdict": "admitted_for_citation", "admitted_for_citation": True}) + "\n",
        encoding="utf-8",
    )
    (bundle / "report.md").write_text("pass and ready for citation\n", encoding="utf-8")

    _assert_blocks_for(bundle, "output_digest_mismatch")


def test_unsupported_aggregation_rule_blocks(tmp_path):
    bundle = _clean_bundle(tmp_path, "bad_aggregation")

    def mutation(rows: list[dict]) -> None:
        rows[0]["aggregation_rule"] = "row_shape_only_mean"

    _mutate_metric_rows(bundle, mutation)

    _assert_blocks_for(bundle, "unsupported_aggregation_rule")


def test_duplicate_run_id_blocks(tmp_path):
    bundle = _clean_bundle(tmp_path, "duplicate_run_id")

    def mutation(rows: list[dict]) -> None:
        rows[1]["run_id"] = rows[0]["run_id"]

    _mutate_metric_rows(bundle, mutation)

    _assert_blocks_for(bundle, "duplicate_metric_run_id")


def test_missing_producer_function_blocks(tmp_path):
    bundle = _clean_bundle(tmp_path, "missing_producer")

    def mutation(rows: list[dict]) -> None:
        del rows[0]["producer_function"]

    _mutate_metric_rows(bundle, mutation)

    _assert_blocks_for(bundle, "metric_provenance_missing_required_fields")


def test_missing_recompute_contract_blocks(tmp_path):
    bundle = _clean_bundle(tmp_path, "missing_contract")

    def mutation(rows: list[dict]) -> None:
        del rows[0]["recompute_contract"]

    _mutate_metric_rows(bundle, mutation)

    _assert_blocks_for(bundle, "missing_recompute_contract")


def test_source_hash_helper_uses_current_test_source():
    source_path = Path(__file__)
    assert len(_sha256_file(source_path)) == 64
