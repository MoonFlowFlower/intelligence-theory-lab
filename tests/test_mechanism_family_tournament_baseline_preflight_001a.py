import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_DIR = "mechanism_family_tournament_baseline_preflight_001a"
ARTIFACT_DIR = ROOT / "artifacts" / TASK_DIR
REPORT_PATH = ROOT / "docs" / "research" / "MECHANISM-FAMILY-TOURNAMENT-BASELINE-PREFLIGHT-001A.md"

EXPECTED_HEAD = "0a59b39f30ec548d5f5513b6a27f4fd307df5381"
EXPECTED_ENTRY_ANCHOR = "remote-anchor-mechanism-family-tournament-entry-criteria-001a-0a59b39"
EXPECTED_FAMILY_IDS = {
    "causal_world_model_control",
    "jepa_like_latent_prediction",
    "replay_consolidation_adaptation",
    "self_boundary_controllability_model",
    "viability_value_gated_prediction_action_loop",
    "social_latent_inference_without_partner_id_lookup",
}
REQUIRED_ARTIFACTS = {
    "result.json",
    "source_pin_readback.json",
    "inherited_registry_readback.json",
    "baseline_score_matrix.json",
    "family_decisions.json",
    "survivors.json",
    "closed_families.json",
    "needs_redesign.json",
    "closed_family_inheritance.json",
    "positive_control_results.json",
    "provenance_manifest.json",
    "baseline_run_manifest.json",
    "surface_ablation_results.json",
    "forbidden_action_guard.json",
    "future_tournament_eligibility.json",
}


def _runner():
    return importlib.import_module("mechanism_family_tournament_baseline_preflight_001a.runner")


def test_inherited_registry_and_source_pins_are_read_from_repo_artifacts(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path / TASK_DIR, persist_artifacts=False)
    source_pin = run["source_pin_readback"]
    registry = run["inherited_registry_readback"]
    closed = run["closed_family_inheritance"]

    assert source_pin["expected_starting_head"] == EXPECTED_HEAD
    assert source_pin["entry_criteria_remote_anchor_tag"] == EXPECTED_ENTRY_ANCHOR
    assert source_pin["entry_criteria_remote_anchor_hash"] == EXPECTED_HEAD
    assert source_pin["entry_criteria_local_or_ancestor_verified"] is True
    assert source_pin["entry_criteria_remote_anchor_verified"] is True
    assert source_pin["branch"] == "codex/meta-theory-scaffold"
    ahead_behind = source_pin["upstream_ahead_behind_at_start"].split()
    assert len(ahead_behind) == 2
    assert all(value.isdigit() for value in ahead_behind)

    assert set(registry["family_ids"]) == EXPECTED_FAMILY_IDS
    assert registry["family_count"] == 6
    assert registry["baseline_row_count"] == 37
    assert registry["ablation_row_count"] == 6
    assert registry["transfer_counterfactual_row_count"] == 6
    assert registry["inherited_validator_final_verdict"] == "pass"
    assert registry["malformed_positive_control_failed_as_expected"] is True

    closure = closed["current_generated_gate4_partner_id_lookup_family_closure"]
    assert closure["best_faithful_baseline"] == "partner_id_lookup_baseline"
    assert closure["score"] == 1.0
    assert closure["threshold"] == 0.8
    assert closure["same_family_repair_allowed"] is False


def test_missing_thresholds_and_targets_emit_needs_redesign_without_survivors(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path / TASK_DIR, persist_artifacts=False)

    decisions = {row["family_id"]: row for row in run["family_decisions"]["decisions"]}
    assert set(decisions) == EXPECTED_FAMILY_IDS
    assert run["survivors"]["families"] == []
    assert run["closed_families"]["families"] == []
    assert {row["family_id"] for row in run["needs_redesign"]["families"]} == EXPECTED_FAMILY_IDS
    assert run["future_tournament_eligibility"]["eligible_for_future_tournament_execution_card"] is False

    for family_id, decision in decisions.items():
        assert decision["decision"] == "needs_redesign"
        assert "missing_threshold" in decision["reasons"]
        assert "missing_callable_target" in decision["reasons"]
        assert decision["threshold"] is None
        assert decision["best_faithful_cheap_baseline"]["score"] is None

    score_rows = run["baseline_score_matrix"]["rows"]
    assert len(score_rows) == 37
    assert {row["family_id"] for row in score_rows} == EXPECTED_FAMILY_IDS
    assert all(row["producer_function"] == "run_declared_baseline_preflight_row" for row in score_rows)
    assert all(row["callable_invoked"] is True for row in score_rows)
    assert all(row["score"] is None for row in score_rows)
    assert all(row["decision_contribution"] == "needs_redesign_missing_threshold_or_callable_target" for row in score_rows)


def test_positive_controls_fail_expected_and_distinguish_leakage_from_faithful_baseline(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path / TASK_DIR, persist_artifacts=False)
    controls = {row["control_id"]: row for row in run["positive_control_results"]["controls"]}

    assert run["positive_control_results"]["all_matched"] is True
    assert set(controls) == {
        "target_leak_fixture",
        "partner_id_lookup_fixture",
        "table_lookup_solvable_fixture",
        "static_formula_solvable_fixture",
        "missing_threshold_fixture",
        "missing_callable_target_fixture",
    }
    assert controls["target_leak_fixture"]["observed_block_reason"] == "target_leak_detected"
    assert controls["target_leak_fixture"]["faithful_or_leakage_detector"] == "leakage_detector"
    assert controls["partner_id_lookup_fixture"]["observed_block_reason"] == "partner_id_lookup_shortcut_detected"
    assert controls["partner_id_lookup_fixture"]["faithful_or_leakage_detector"] == "faithful_cheap_baseline"
    assert controls["table_lookup_solvable_fixture"]["observed_block_reason"] == "faithful_table_lookup_reaches_threshold"
    assert controls["static_formula_solvable_fixture"]["observed_block_reason"] == "static_formula_shortcut_detected"
    assert controls["missing_threshold_fixture"]["observed_block_reason"] == "missing_threshold"
    assert controls["missing_callable_target_fixture"]["observed_block_reason"] == "missing_callable_target"
    assert all(row["matched"] is True for row in controls.values())
    assert all(row["positive_control_input_fixture_path"] for row in controls.values())

    failed = runner.execute_preflight(
        output_dir=tmp_path / "failed_positive",
        persist_artifacts=False,
        force_positive_control_mismatch="target_leak_fixture",
    )
    assert failed["result"]["verdict"] == (
        "mechanism_family_tournament_baseline_preflight_001a_blocked_by_non_fail_able_baseline_or_positive_control_failure"
    )
    assert "positive_control_mismatch:target_leak_fixture" in failed["result"]["stop_conditions_triggered"]


def test_recompute_serialized_positive_control_scores_and_surface_ablation(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path / TASK_DIR, persist_artifacts=False)
    scored_controls = [
        row
        for row in run["positive_control_results"]["controls"]
        if row["score_record"] is not None
    ]

    assert scored_controls
    for row in scored_controls:
        recomputed = runner.recompute_baseline_score(row["score_record"]["serialized_input"])
        assert recomputed["score"] == row["score_record"]["score"]
        assert recomputed["raw_predictions"] == row["score_record"]["raw_predictions"]

    ablations = {row["control_id"]: row for row in run["surface_ablation_results"]["ablations"]}
    assert ablations["partner_id_lookup_fixture"]["original_score"] == 1.0
    assert ablations["partner_id_lookup_fixture"]["masked_score"] < 1.0
    assert ablations["partner_id_lookup_fixture"]["score_collapses"] is True
    assert ablations["table_lookup_solvable_fixture"]["score_collapses"] is True
    assert ablations["static_formula_solvable_fixture"]["score_collapses"] is True


def test_artifacts_report_and_forbidden_guard_are_written_and_parse(tmp_path):
    runner = _runner()

    output_dir = tmp_path / TASK_DIR
    report_path = tmp_path / "MECHANISM-FAMILY-TOURNAMENT-BASELINE-PREFLIGHT-001A.md"
    run = runner.execute_preflight(output_dir=output_dir, persist_artifacts=True)
    written_report = runner.write_research_report(run, report_path=report_path)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in output_dir.iterdir()})
    for path in output_dir.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    assert written_report == report_path

    report_text = written_report.read_text(encoding="utf-8")
    assert "Verdict: `mechanism_family_tournament_baseline_preflight_001a_all_families_closed_or_needs_redesign`" in report_text
    assert "This task created no candidate code" in report_text
    assert "no mechanism-validity evidence" in report_text

    guard = run["forbidden_action_guard"]
    assert guard["candidate_code_created"] is False
    assert guard["tournament_execution_attempted"] is False
    assert guard["gate4_replacement_card_created"] is False
    assert guard["runtime_or_mainline_path_created"] is False
    assert guard["forbidden_files_modified"] == []
    assert run["result"]["remote_anchor_performed"] is False


def test_static_literal_scores_are_rejected_by_provenance_verifier(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path / TASK_DIR, persist_artifacts=False)
    assert runner.verify_provenance_manifest(run["provenance_manifest"])["passed"] is True

    static = json.loads(json.dumps(run["provenance_manifest"]))
    static["baseline_score_records"][0]["producer_function"] = "literal_static_report"
    static["baseline_score_records"][0]["score"] = 1.0
    static["baseline_score_records"][0]["static_score_injection"] = True

    verification = runner.verify_provenance_manifest(static)
    assert verification["passed"] is False
    assert "static_score_injection" in verification["blocking_reasons"]
