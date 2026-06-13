import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


TASK_ID = "MECHANISM-SEARCH-PROCESS-POLICY-ENFORCEMENT-SMOKE-001B"
ARTIFACT_DIR = Path(__file__).resolve().parent
REPO_ROOT = ARTIFACT_DIR.parent.parent
SCHEMA_PATH = ARTIFACT_DIR / "policy_fixture_schema.json"
FIXTURES_DIR = ARTIFACT_DIR / "fixtures"
RESULTS_PATH = ARTIFACT_DIR / "policy_enforcement_results.json"

SAFE_MAINLINE_CLAIMS = {"none", "not_mainline_integrated", "not mainline-integrated"}
SAFE_ENABLED_CLAIMS = {"none", "no_runtime_or_trigger_enabled", "not_enabled"}
ALLOWED_REMOTE_BOUNDARY_REASONS = {
    "none",
    "route_boundary",
    "boundary_worthy_negative_evidence",
    "stable_downstream_cited_policy_boundary",
    "upstream_anchor_verification"
}
INFLATED_CLAIM_TERMS = {
    "gate4 validity",
    "replacement gate4 success",
    "mechanism validity",
    "social understanding",
    "intelligence",
    "agency",
    "subjectivity",
    "consciousness",
    "emotion",
    "autonomy",
    "runtime readiness",
    "bridge readiness",
    "admission readiness",
    "companion readiness",
    "user benefit",
    "ego readiness",
    "mainline readiness"
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_path(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current_head():
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def sorted_unique(values):
    return sorted(set(values))


def has_inflated_claim_ceiling(claim_ceiling):
    if not isinstance(claim_ceiling, str) or not claim_ceiling.strip():
        return True
    lowered = claim_ceiling.lower()
    return any(term in lowered for term in INFLATED_CLAIM_TERMS)


def required_field_failures(fixture, required_fields):
    failures = []
    for field in required_fields:
        if field not in fixture:
            if field == "process_mode":
                failures.append("missing_process_mode")
            elif field == "claim_ceiling":
                failures.append("claim_ceiling_missing_or_inflated")
            else:
                raise ValueError(f"{fixture.get('fixture_id', '<unknown>')} missing required field: {field}")
    return failures


def evaluate_fixture_policy_rules(fixture, schema):
    reasons = required_field_failures(fixture, schema["required_fields"])
    process_mode = fixture.get("process_mode")
    claim_ceiling = fixture.get("claim_ceiling")

    if process_mode not in schema["process_mode_enum"]:
        reasons.append("missing_process_mode")

    if has_inflated_claim_ceiling(claim_ceiling):
        reasons.append("claim_ceiling_missing_or_inflated")

    if process_mode == "discovery_mode":
        mainline_claim = str(fixture.get("mainline_integration_claim", "")).lower()
        enabled_claim = str(fixture.get("enabled_status_claim", "")).lower()
        target_claim = str(fixture.get("target_mechanism_claim", "")).lower()
        if (
            mainline_claim not in SAFE_MAINLINE_CLAIMS
            or enabled_claim not in SAFE_ENABLED_CLAIMS
            or fixture.get("runtime_or_trigger_enabled") is True
            or target_claim not in {"none", "no_mechanism_claim"}
        ):
            reasons.append("discovery_claim_inflation")

    if process_mode == "admission_mode":
        if fixture.get("computed_evidence_provenance_present") is not True:
            reasons.append("admission_missing_computed_evidence")
        if fixture.get("independent_callable_baselines_present") is not True:
            reasons.append("admission_missing_callable_baselines")
        if fixture.get("real_ablations_present") is not True:
            reasons.append("admission_missing_real_ablation")

    if fixture.get("leakage_positive_control_present") is not True:
        reasons.append("leakage_positive_control_missing")

    if (
        fixture.get("replay_recomputes_from_serialized_state") is not True
        or fixture.get("replay_compares_only_stored_hash") is True
    ):
        reasons.append("replay_recomputation_missing")

    baseline_score = fixture.get("best_faithful_baseline_score")
    threshold = fixture.get("task_threshold")
    if isinstance(baseline_score, (int, float)) and isinstance(threshold, (int, float)):
        if baseline_score >= threshold and fixture.get("same_family_repair_requested") is True:
            reasons.append("cheap_baseline_closure_violated")
        if baseline_score >= threshold and fixture.get("cited_closed_family_negative_evidence") is not True:
            reasons.append("closed_family_negative_evidence_not_cited")

    if (
        fixture.get("target_source_type") == "static_label_formula"
        and fixture.get("target_mechanism_claim") not in {"none", "no_mechanism_claim"}
    ):
        reasons.append("static_label_formula_mechanism_claim")

    if fixture.get("llm_used_in_evaluation_time_scoring") is True:
        reasons.append("llm_eval_time_scoring_forbidden")

    if fixture.get("candidate_code_created") is True and fixture.get("baseline_preflight_completed") is not True:
        reasons.append("candidate_before_baseline_preflight")

    if (
        fixture.get("remote_anchor_requested") is True
        and fixture.get("remote_anchor_boundary_reason") not in ALLOWED_REMOTE_BOUNDARY_REASONS
    ):
        reasons.append("remote_anchor_non_boundary")

    return sorted_unique(reasons)


def fixture_result(fixture_path, fixture, schema):
    observed_reasons = evaluate_fixture_policy_rules(fixture, schema)
    observed_verdict = "block" if observed_reasons else "pass"
    expected_reasons = sorted(fixture["expected_block_reasons"])
    return {
        "fixture_id": fixture["fixture_id"],
        "fixture_path": str(fixture_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "producer_function": "evaluate_fixture_policy_rules",
        "static_verdict_dictionary_used": False,
        "expected_verdict": fixture["expected_verdict"],
        "observed_verdict": observed_verdict,
        "expected_block_reasons": expected_reasons,
        "observed_block_reasons": observed_reasons,
        "expected_block_reasons_matched": expected_reasons == observed_reasons,
        "passed_expectation": fixture["expected_verdict"] == observed_verdict,
    }


def input_record(path):
    return {
        "path": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "sha256": sha256_path(path)
    }


def run_validation():
    schema = read_json(SCHEMA_PATH)
    fixture_paths = sorted(FIXTURES_DIR.glob("*.json"))
    fixtures = [read_json(path) for path in fixture_paths]

    expected_verdicts = {fixture["expected_verdict"] for fixture in fixtures}
    if not expected_verdicts <= set(schema["expected_verdict_enum"]):
        raise ValueError(f"unexpected fixture expected verdicts: {sorted(expected_verdicts)}")

    fixture_results = [
        fixture_result(path, fixture, schema)
        for path, fixture in zip(fixture_paths, fixtures)
    ]

    expected_pass_count = sum(1 for item in fixture_results if item["expected_verdict"] == "pass")
    expected_block_count = sum(1 for item in fixture_results if item["expected_verdict"] == "block")
    observed_pass_count = sum(1 for item in fixture_results if item["observed_verdict"] == "pass")
    observed_block_count = sum(1 for item in fixture_results if item["observed_verdict"] == "block")
    invalid_fixtures_failed_as_expected = all(
        item["observed_verdict"] == "block" and item["passed_expectation"]
        for item in fixture_results
        if item["expected_verdict"] == "block"
    )
    valid_fixture_passed_as_expected = all(
        item["observed_verdict"] == "pass" and item["passed_expectation"]
        for item in fixture_results
        if item["expected_verdict"] == "pass"
    )
    all_expected_block_reasons_matched = all(
        item["expected_block_reasons_matched"] for item in fixture_results
    )

    final_pass = (
        expected_pass_count >= schema["minimum_fixture_counts"]["valid"]
        and expected_block_count >= schema["minimum_fixture_counts"]["invalid"]
        and invalid_fixtures_failed_as_expected
        and valid_fixture_passed_as_expected
        and all_expected_block_reasons_matched
    )
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    run_id = f"mechanism_search_process_policy_enforcement_smoke_001b_{generated_at.replace('-', '').replace(':', '')}"
    inputs = [input_record(SCHEMA_PATH)] + [input_record(path) for path in fixture_paths]

    return {
        "producer_function": "run_validation",
        "script_path": str(Path(__file__).resolve().relative_to(REPO_ROOT)).replace("\\", "/"),
        "inputs": inputs,
        "run_id": run_id,
        "current_head": current_head(),
        "code_path_hash": sha256_path(Path(__file__).resolve()),
        "generated_at_utc": generated_at,
        "total_fixtures": len(fixture_results),
        "expected_pass_count": expected_pass_count,
        "expected_block_count": expected_block_count,
        "observed_pass_count": observed_pass_count,
        "observed_block_count": observed_block_count,
        "invalid_fixtures_failed_as_expected": invalid_fixtures_failed_as_expected,
        "valid_fixture_passed_as_expected": valid_fixture_passed_as_expected,
        "all_expected_block_reasons_matched": all_expected_block_reasons_matched,
        "fixture_results": fixture_results,
        "final_verdict": "pass" if final_pass else "fail"
    }


def main():
    results = run_validation()
    RESULTS_PATH.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "final_verdict": results["final_verdict"],
        "total_fixtures": results["total_fixtures"],
        "observed_pass_count": results["observed_pass_count"],
        "observed_block_count": results["observed_block_count"]
    }, indent=2, sort_keys=True))
    return 0 if results["final_verdict"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
