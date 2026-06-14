import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_DIR = "mechanism_family_tournament_baseline_preflight_rerun_001b"
REPORT_NAME = "MECHANISM-FAMILY-TOURNAMENT-BASELINE-PREFLIGHT-RERUN-001B.md"
PARENT_COMMIT = "614b3414e0a9417ebca65096e067f6c003addfa5"
PARENT_TAG = "remote-anchor-mechanism-family-tournament-executable-surface-contract-001a-614b341"
EXPECTED_FAMILY_IDS = {
    "causal_world_model_control",
    "jepa_like_latent_prediction",
    "replay_consolidation_adaptation",
    "self_boundary_controllability_model",
    "viability_value_gated_prediction_action_loop",
    "social_latent_inference_without_partner_id_lookup",
}
REQUIRED_BASELINE_CATEGORIES = {
    "exact_lookup_baseline",
    "table_memorization_baseline",
    "nearest_neighbor_retrieval_baseline",
    "static_decoder_baseline",
    "static_formula_rule_baseline",
}
REQUIRED_ARTIFACTS = {
    "result.json",
    "parent_anchor_readback.json",
    "contract_readback.json",
    "baseline_score_matrix.json",
    "family_decisions.json",
    "survivors.json",
    "closed_families.json",
    "needs_redesign.json",
    "positive_control_results.json",
    "provenance_manifest.json",
    "leakage_scan_results.json",
    "future_tournament_eligibility.json",
    "forbidden_action_guard.json",
}


def _runner():
    return importlib.import_module(
        "mechanism_family_tournament_baseline_preflight_rerun_001b.runner"
    )


def test_parent_anchor_readback_and_contract_are_loaded_from_artifact(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path / TASK_DIR, persist_artifacts=False)

    parent = run["parent_anchor_readback"]
    assert parent["parent_commit"] == PARENT_COMMIT
    assert parent["parent_tag"] == PARENT_TAG
    assert parent["local_parent_commit_hash"] == PARENT_COMMIT
    assert parent["local_tag_hash"] == PARENT_COMMIT
    assert parent["remote_tag_hash"] == PARENT_COMMIT
    assert parent["local_tag_type"] == "commit"
    assert parent["parent_tag_exact_match"] is True
    assert parent["parent_commit_is_ancestor_of_current_head"] is True

    contract = run["contract_readback"]
    assert contract["loaded_from_artifact"] is True
    assert contract["source_path"] == (
        "artifacts/mechanism_family_tournament_executable_surface_contract_001a/"
        "family_surface_contract.json"
    )
    assert contract["family_count"] == 6
    assert set(contract["family_ids"]) == EXPECTED_FAMILY_IDS
    assert contract["contract_task_id"] == "MECHANISM-FAMILY-TOURNAMENT-EXECUTABLE-SURFACE-CONTRACT-001A"
    assert contract["candidate_code_authorized"] is False
    assert contract["tournament_execution_authorized"] is False


def test_contract_callables_thresholds_and_baseline_runner_coverage(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path / TASK_DIR, persist_artifacts=False)
    contract_rows = {row["family_id"]: row for row in run["contract_readback"]["family_validation"]}
    baseline_rows_by_family = {}
    for row in run["baseline_score_matrix"]["rows"]:
        baseline_rows_by_family.setdefault(row["family_id"], []).append(row)

    assert set(contract_rows) == EXPECTED_FAMILY_IDS
    assert set(baseline_rows_by_family) == EXPECTED_FAMILY_IDS
    for family_id, validation in contract_rows.items():
        assert validation["target_resolver_callable"] is True
        assert validation["metric_function_callable"] is True
        assert validation["numeric_threshold_exists"] is True
        assert validation["sample_target_resolved"] is True
        assert validation["metric_smoke_check_passed"] is True
        assert validation["blocking_reasons"] == []

        family_categories = {row["baseline_category"] for row in baseline_rows_by_family[family_id]}
        assert REQUIRED_BASELINE_CATEGORIES.issubset(family_categories)
        assert any(
            row["faithful_or_leakage_detector"] == "faithful_cheap_baseline"
            for row in baseline_rows_by_family[family_id]
        )


def test_baseline_scores_are_callable_recomputable_and_close_all_families(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path / TASK_DIR, persist_artifacts=False)
    score_rows = run["baseline_score_matrix"]["rows"]

    assert score_rows
    for row in score_rows:
        assert row["producer_function"] == "run_callable_baseline_score"
        assert row["module_path"] == "src/mechanism_family_tournament_baseline_preflight_rerun_001b/runner.py"
        assert row["code_path_hash"]
        assert row["run_id"] == run["run_id"]
        assert row["seed"] == 1002
        assert row["record_ids"]
        assert row["context_ids"] == [row["family_id"]]
        assert isinstance(row["raw_predictions"], list)
        assert isinstance(row["targets"], list)
        assert isinstance(row["score"], float)
        recomputed = runner.recompute_baseline_score(row["serialized_input"])
        assert recomputed["score"] == row["score"]
        assert recomputed["raw_predictions"] == row["raw_predictions"]
        assert recomputed["targets"] == row["targets"]

    decisions = {row["family_id"]: row for row in run["family_decisions"]["decisions"]}
    assert set(decisions) == EXPECTED_FAMILY_IDS
    assert all(
        row["decision"] == "closed_by_faithful_cheap_baseline"
        for row in decisions.values()
    )
    assert run["closed_families"]["families"]
    assert run["survivors"]["families"] == []
    assert run["needs_redesign"]["families"] == []
    assert run["future_tournament_eligibility"]["eligible_for_future_tournament_execution_card"] is False
    assert run["result"]["verdict"] == (
        "mechanism_family_tournament_baseline_preflight_rerun_001b_all_closed_or_needs_redesign"
    )


def test_positive_controls_leakage_scan_and_provenance_block_failures(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path / TASK_DIR, persist_artifacts=False)
    controls = {row["control_id"]: row for row in run["positive_control_results"]["controls"]}
    assert set(controls) == {
        "target_leak",
        "partner_id_lookup",
        "table_lookup",
        "static_formula",
        "missing_threshold",
        "missing_callable_target",
    }
    assert run["positive_control_results"]["all_failed_as_expected"] is True
    assert controls["target_leak"]["observed_block_reason"] == "target_leak_detected"
    assert controls["partner_id_lookup"]["observed_block_reason"] == "partner_id_lookup_shortcut_detected"
    assert controls["table_lookup"]["observed_block_reason"] == "faithful_table_lookup_reaches_threshold"
    assert controls["static_formula"]["observed_block_reason"] == "static_formula_shortcut_detected"
    assert controls["missing_threshold"]["observed_block_reason"] == "missing_threshold"
    assert controls["missing_callable_target"]["observed_block_reason"] == "missing_callable_target"
    assert all(row["failed_as_expected"] is True for row in controls.values())

    leakage = run["leakage_scan_results"]
    assert leakage["positive_control_detected"] is True
    assert leakage["clean_contract_records_passed"] is True

    assert runner.verify_provenance_manifest(run["provenance_manifest"])["passed"] is True
    static = json.loads(json.dumps(run["provenance_manifest"]))
    static["baseline_score_records"][0]["producer_function"] = "literal_static_report"
    static["baseline_score_records"][0]["static_score_injection"] = True
    verification = runner.verify_provenance_manifest(static)
    assert verification["passed"] is False
    assert "static_score_injection" in verification["blocking_reasons"]

    failed = runner.execute_preflight(
        output_dir=tmp_path / "failed_positive",
        persist_artifacts=False,
        force_positive_control_mismatch="target_leak",
    )
    assert failed["result"]["verdict"] == (
        "mechanism_family_tournament_baseline_preflight_rerun_001b_blocked_by_contract_or_positive_control_failure"
    )
    assert "positive_control_mismatch:target_leak" in failed["result"]["stop_conditions_triggered"]


def test_artifacts_report_forbidden_guard_and_future_eligibility(tmp_path):
    runner = _runner()

    output_dir = tmp_path / TASK_DIR
    report_path = tmp_path / REPORT_NAME
    run = runner.execute_preflight(output_dir=output_dir, persist_artifacts=True)
    written_report = runner.write_research_report(run, report_path=report_path)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in output_dir.glob("*.json")})
    for path in output_dir.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    assert written_report == report_path
    report_text = report_path.read_text(encoding="utf-8")
    assert "Verdict: `mechanism_family_tournament_baseline_preflight_rerun_001b_all_closed_or_needs_redesign`" in report_text
    assert "no-candidate baseline-preflight evidence only" in report_text
    assert "no mechanism-validity evidence" in report_text

    guard = run["forbidden_action_guard"]
    assert guard["candidate_code_created"] is False
    assert guard["candidate_score_produced"] is False
    assert guard["tournament_execution_attempted"] is False
    assert guard["gate4_repair_or_rerun_attempted"] is False
    assert guard["runtime_or_mainline_path_created"] is False
    assert guard["forbidden_files_modified"] == []
    assert run["result"]["remote_anchor_performed"] is False

    assert runner.evaluate_future_tournament_eligibility(1)["eligible_for_future_tournament_execution_card"] is False
    assert runner.evaluate_future_tournament_eligibility(2)["eligible_for_future_tournament_execution_card"] is True
