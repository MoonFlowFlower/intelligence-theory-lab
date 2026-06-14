import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_DIR = "mechanism_family_tournament_executable_surface_contract_001a"
EXPECTED_FAMILY_IDS = {
    "causal_world_model_control",
    "jepa_like_latent_prediction",
    "replay_consolidation_adaptation",
    "self_boundary_controllability_model",
    "viability_value_gated_prediction_action_loop",
    "social_latent_inference_without_partner_id_lookup",
}
REQUIRED_CONTRACT_FIELDS = {
    "family_id",
    "observation_schema",
    "allowed_input_fields",
    "forbidden_target_derived_fields",
    "target_resolver",
    "metric_function",
    "numeric_threshold",
    "threshold_rationale",
    "cheap_baseline_attack_surface",
    "leakage_detector_list",
    "positive_control_malformed_fixture",
    "minimum_baseline_preflight_eligibility",
}
REQUIRED_ARTIFACTS = {
    "result.json",
    "source_pin_readback.json",
    "family_surface_contract.json",
    "surface_validation_results.json",
    "positive_control_malformed_fixture.json",
    "positive_control_results.json",
    "forbidden_action_guard.json",
    "baseline_preflight_rerun_authorization.json",
}


def _runner():
    return importlib.import_module(
        "mechanism_family_tournament_executable_surface_contract_001a.runner"
    )


def test_all_six_families_have_callable_surfaces_numeric_thresholds_and_eligibility(tmp_path):
    runner = _runner()

    run = runner.execute_contract_validation(
        output_dir=tmp_path / TASK_DIR,
        persist_artifacts=False,
    )

    contract = run["family_surface_contract"]
    families = {row["family_id"]: row for row in contract["families"]}
    validation_rows = {
        row["family_id"]: row
        for row in run["surface_validation_results"]["family_validation"]
    }

    assert set(families) == EXPECTED_FAMILY_IDS
    assert set(validation_rows) == EXPECTED_FAMILY_IDS

    for family_id, family in families.items():
        assert REQUIRED_CONTRACT_FIELDS.issubset(family)
        assert isinstance(family["observation_schema"], dict)
        assert set(family["allowed_input_fields"]).issubset(family["observation_schema"])
        assert set(family["allowed_input_fields"]).isdisjoint(
            family["forbidden_target_derived_fields"]
        )
        assert isinstance(family["numeric_threshold"], (int, float))
        assert 0 < family["numeric_threshold"] < 1
        assert family["threshold_rationale"]
        assert family["cheap_baseline_attack_surface"]
        assert family["leakage_detector_list"]
        assert family["positive_control_malformed_fixture"]["family_id"] == family_id
        assert family["minimum_baseline_preflight_eligibility"] is True

        validation = validation_rows[family_id]
        assert validation["target_resolver_callable"] is True
        assert validation["metric_function_callable"] is True
        assert validation["sample_target_resolved"] is True
        assert validation["metric_smoke_check_passed"] is True
        assert validation["minimum_baseline_preflight_eligibility"] is True
        assert validation["blocking_missing_fields"] == []

    result = run["result"]
    assert result["verdict"] == "mechanism_family_tournament_executable_surface_contract_001a_pass"
    assert result["baseline_preflight_executable_family_count"] == 6
    assert result["blocked_family_ids"] == []
    assert result["candidate_code_created"] is False
    assert result["tournament_execution_attempted"] is False


def test_positive_controls_fail_and_do_not_create_candidate_or_tournament_surface(tmp_path):
    runner = _runner()

    run = runner.execute_contract_validation(
        output_dir=tmp_path / TASK_DIR,
        persist_artifacts=False,
    )
    controls = run["positive_control_results"]

    assert controls["all_failed_as_expected"] is True
    assert {row["family_id"] for row in controls["controls"]} == EXPECTED_FAMILY_IDS
    for row in controls["controls"]:
        assert row["expected_failure_reason"] == "forbidden_target_derived_field_visible"
        assert row["observed_failure_reason"] == "forbidden_target_derived_field_visible"
        assert row["failed_as_expected"] is True

    guard = run["forbidden_action_guard"]
    assert guard["candidate_code_created"] is False
    assert guard["candidate_score_produced"] is False
    assert guard["tournament_execution_attempted"] is False
    assert guard["gate4_replacement_design_created"] is False
    assert guard["runtime_or_mainline_path_created"] is False
    assert guard["llm_rag_ui_companion_path_created"] is False


def test_artifacts_report_authorize_only_separate_baseline_preflight_rerun(tmp_path):
    runner = _runner()

    output_dir = tmp_path / TASK_DIR
    report_path = tmp_path / "MECHANISM-FAMILY-TOURNAMENT-EXECUTABLE-SURFACE-CONTRACT-001A.md"
    run = runner.execute_contract_validation(output_dir=output_dir, persist_artifacts=True)
    written_report = runner.write_research_report(run, report_path=report_path)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in output_dir.iterdir()})
    for path in output_dir.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

    authorization = run["baseline_preflight_rerun_authorization"]
    assert authorization["rerun_authorized"] is True
    assert authorization["authorized_scope"] == "separate no-candidate baseline-preflight rerun only"
    assert authorization["candidate_code_authorized"] is False
    assert authorization["tournament_execution_authorized"] is False
    assert authorization["gate4_replacement_authorized"] is False

    report_text = written_report.read_text(encoding="utf-8")
    assert "Verdict: `mechanism_family_tournament_executable_surface_contract_001a_pass`" in report_text
    assert "Baseline preflight rerun authorized: `True`" in report_text
    assert "candidate code remains unauthorized" in report_text
    assert "no mechanism-validity evidence" in report_text
