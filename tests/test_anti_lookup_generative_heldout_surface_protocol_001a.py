import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_DIR = "anti_lookup_generative_heldout_surface_protocol_001a"
TASK_CARD_ID = "ANTI-LOOKUP-GENERATIVE-HELDOUT-SURFACE-PROTOCOL-001A"
REPORT_NAME = "ANTI-LOOKUP-GENERATIVE-HELDOUT-SURFACE-PROTOCOL-001A.md"
REQUIRED_START_HEAD = "8b762605a10f780676591c2d745279bad3d0804c"
RERUN_COMMIT = "25bdc91280b428ff1eb8029ac7c30c9cf9c924c6"
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
    "protocol.json",
    "inherited_negative_evidence_readback.json",
    "surface_requirements.json",
    "forbidden_shortcut_taxonomy.json",
    "validator_positive_controls.json",
    "example_valid_surface_fixture.json",
    "example_invalid_lookup_surface_fixture.json",
    "baseline_preregistration_template.json",
    "future_surface_acceptance_gate.json",
    "claim_ceiling.json",
}
REQUIRED_BASELINES = {
    "exact_lookup",
    "train_row_table_lookup",
    "nearest_neighbor_retrieval",
    "trace_order_lookup",
    "identity_key_lookup",
    "static_decoder",
    "static_formula",
}
EXPECTED_CONTROL_REASONS = {
    "invalid_exact_lookup_surface": "exact_lookup_reaches_threshold",
    "invalid_table_lookup_surface": "table_lookup_reaches_threshold",
    "invalid_identity_key_surface": "identity_key_lookup_reaches_threshold",
    "invalid_static_formula_surface": "static_formula_reaches_threshold",
    "invalid_target_leak_surface": "target_leak_detected",
    "invalid_missing_generator_provenance_surface": "missing_generator_provenance",
    "invalid_no_counterfactual_pairs_surface": "missing_counterfactual_pairs",
    "invalid_overlapping_support_surface": "overlapping_train_heldout_support",
    "invalid_hidden_baseline_access_surface": "baseline_access_not_equivalent",
}


def _runner():
    module_path = SRC / TASK_DIR / "runner.py"
    assert module_path.exists(), "runner module not implemented"
    return importlib.import_module(f"{TASK_DIR}.runner")


def test_inherited_negative_evidence_readback_preserves_001b_closure_and_routing(tmp_path):
    runner = _runner()

    run = runner.execute_protocol(output_dir=tmp_path / TASK_DIR, persist_artifacts=False)
    inherited = run["inherited_negative_evidence_readback"]

    assert inherited["task_id"] == TASK_CARD_ID
    assert inherited["required_start_head"] == REQUIRED_START_HEAD
    assert inherited["required_start_head_is_current_or_ancestor"] is True
    assert inherited["baseline_preflight_rerun_boundary"]["commit"] == RERUN_COMMIT
    assert inherited["baseline_preflight_rerun_boundary"]["closed_surface_count"] == 6
    assert inherited["baseline_preflight_rerun_boundary"]["survivor_count"] == 0
    assert inherited["baseline_preflight_rerun_boundary"]["future_tournament_eligibility"] is False
    assert inherited["baseline_preflight_rerun_boundary"]["current_surfaces_remain_closed"] is True

    closed_by_id = {
        row["family_id"]: row
        for row in inherited["baseline_preflight_rerun_boundary"]["closed_surfaces"]
    }
    assert set(closed_by_id) == EXPECTED_FAMILY_IDS
    for row in closed_by_id.values():
        assert row["baseline_id"] == "exact_lookup"
        assert row["score"] == 1.0
        assert row["threshold"] == 0.8
        assert row["decision"] == "closed_by_faithful_cheap_baseline"

    routing = inherited["post_result_routing_reconciliation_boundary"]
    assert routing["commit"] == REQUIRED_START_HEAD
    assert routing["anchor_conflict_reconciled"] is True
    assert routing["same_surface_repair_blocked"] is True
    assert routing["candidate_implementation_authorized"] is False
    assert routing["tournament_execution_authorized"] is False
    assert routing["gate4_replacement_design_authorized"] is False

    result = run["result"]
    assert result["six_current_surfaces_remain_closed"] is True
    assert result["same_surface_repair_blocked"] is True
    assert result["candidate_code_created"] is False
    assert result["tournament_execution_attempted"] is False


def test_validator_accepts_generative_heldout_fixture_and_rejects_positive_controls():
    runner = _runner()

    valid = runner.build_example_valid_surface_fixture()
    valid_result = runner.validate_surface_protocol(valid)

    assert valid_result["valid"] is True
    assert valid_result["blocking_reasons"] == []
    assert valid_result["claim_ceiling"] == runner.CLAIM_CEILING
    assert set(valid_result["baseline_scores"]) >= REQUIRED_BASELINES
    assert all(
        row["score"] < row["threshold"]
        for row in valid_result["baseline_scores"].values()
        if row["baseline_id"] in REQUIRED_BASELINES
    )
    assert valid_result["support_disjoint_heldout_contexts"] is True
    assert valid_result["counterfactual_pair_requirements_met"] is True
    assert valid_result["callable_target_resolver_present"] is True
    assert valid_result["targets_visible_in_observation"] is False

    controls = runner.build_validator_positive_control_fixtures()
    assert set(controls) == set(EXPECTED_CONTROL_REASONS)
    for control_id, expected_reason in EXPECTED_CONTROL_REASONS.items():
        observed = runner.validate_surface_protocol(controls[control_id])
        assert observed["valid"] is False
        assert expected_reason in observed["blocking_reasons"]
        assert observed["expected_block_reason"] == expected_reason


def test_protocol_execution_writes_required_artifacts_and_report(tmp_path):
    runner = _runner()

    output_dir = tmp_path / TASK_DIR
    report_path = tmp_path / REPORT_NAME
    run = runner.execute_protocol(output_dir=output_dir, persist_artifacts=True)
    written_report = runner.write_research_report(run, report_path=report_path)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in output_dir.glob("*.json")})
    for path in output_dir.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

    result = run["result"]
    assert result["verdict"] == "anti_lookup_generative_heldout_surface_protocol_001a_pass"
    assert result["current_layer"] == "engineering-governance / anti-lookup generative heldout surface protocol design only"
    assert result["mainline_integration_status"] == "not integrated"
    assert result["enabled_status"].startswith("no runtime")
    assert result["real_trigger_evidence"].startswith("Callable validator")
    assert result["claim_ceiling"] == runner.CLAIM_CEILING
    assert result["stop_conditions_triggered"] == []

    preregistration = run["baseline_preregistration_template"]
    assert REQUIRED_BASELINES.issubset(set(preregistration["required_cheap_baselines"]))
    assert preregistration["candidate_code_must_not_exist_before_preregistration"] is True

    report_text = written_report.read_text(encoding="utf-8")
    assert "Verdict: `anti_lookup_generative_heldout_surface_protocol_001a_pass`" in report_text
    assert "all six current surfaces remain closed" in report_text
    assert "same-surface repair remains blocked" in report_text
    assert "does not prove mechanism validity" in report_text


def test_future_acceptance_gate_forbids_reopening_candidates_tournaments_and_runtime_paths(tmp_path):
    runner = _runner()

    run = runner.execute_protocol(output_dir=tmp_path / TASK_DIR, persist_artifacts=False)
    gate = run["future_surface_acceptance_gate"]
    guard = run["forbidden_action_guard"]

    assert gate["close_surface_if_any_faithful_cheap_baseline_reaches_threshold"] is True
    assert gate["do_not_weaken_baselines_after_result"] is True
    assert gate["same_surface_repair_requires_separate_redesign_boundary"] is True
    assert gate["candidate_authorization_requires_valid_protocol_pass"] is True
    assert gate["tournament_execution_authorized_by_this_protocol"] is False
    assert gate["gate4_replacement_authorized_by_this_protocol"] is False
    assert gate["runtime_or_ego_mainline_authorized_by_this_protocol"] is False

    assert guard["candidate_code_created"] is False
    assert guard["candidate_score_produced"] is False
    assert guard["tournament_execution_attempted"] is False
    assert guard["gate4_replacement_design_created"] is False
    assert guard["gate4_repair_or_rerun_attempted"] is False
    assert guard["runtime_or_mainline_path_created"] is False
    assert guard["bridge_or_admission_path_created"] is False
    assert guard["llm_rag_ui_companion_path_created"] is False
    assert guard["forbidden_files_modified"] == []


def test_blocked_result_when_positive_control_does_not_fail(tmp_path):
    runner = _runner()

    run = runner.execute_protocol(
        output_dir=tmp_path / "forced_positive_failure",
        persist_artifacts=False,
        force_positive_control_pass="invalid_target_leak_surface",
    )

    assert run["result"]["verdict"] == (
        "anti_lookup_generative_heldout_surface_protocol_001a_blocked_by_positive_control_failure"
    )
    assert "positive_control_mismatch:invalid_target_leak_surface" in run["result"]["stop_conditions_triggered"]
