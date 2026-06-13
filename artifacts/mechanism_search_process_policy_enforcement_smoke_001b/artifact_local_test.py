import json
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = ARTIFACT_DIR / "policy_enforcement_results.json"
VALIDATOR_PATH = ARTIFACT_DIR / "validate_policy_enforcement_smoke.py"


def test_policy_enforcement_smoke_validator_generates_expected_results():
    subprocess.run([sys.executable, str(VALIDATOR_PATH)], cwd=ARTIFACT_DIR, check=True)

    assert RESULTS_PATH.exists()
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))

    assert results["invalid_fixtures_failed_as_expected"] is True
    assert results["valid_fixture_passed_as_expected"] is True
    assert results["all_expected_block_reasons_matched"] is True
    assert results["final_verdict"] == "pass"
    assert results["observed_pass_count"] == results["expected_pass_count"]
    assert results["observed_block_count"] == results["expected_block_count"]

    for fixture_result in results["fixture_results"]:
        assert fixture_result["producer_function"] == "evaluate_fixture_policy_rules"
        assert fixture_result["static_verdict_dictionary_used"] is False
        assert isinstance(fixture_result["observed_block_reasons"], list)
