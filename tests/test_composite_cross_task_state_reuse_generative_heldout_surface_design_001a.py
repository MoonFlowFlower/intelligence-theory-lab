import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_DIR = "composite_cross_task_state_reuse_generative_heldout_surface_design_001a"
TASK_CARD_ID = "COMPOSITE-CROSS-TASK-STATE-REUSE-GENERATIVE-HELDOUT-SURFACE-DESIGN-001A"
REPORT_NAME = "COMPOSITE-CROSS-TASK-STATE-REUSE-GENERATIVE-HELDOUT-SURFACE-DESIGN-001A.md"
G0_ROUTE_ANCHOR = "f3c261cb711a0e674f17f4290c4e71b371055e01"
G0_RECONCILIATION_ANCHOR = "bbb4d0d414162eaa334a6b3e97679d84e504fc9c"

REQUIRED_ARTIFACTS = {
    "result.json",
    "inherited_boundary_readback.json",
    "surface_protocol.json",
    "valid_generated_surface_fixture.json",
    "invalid_positive_controls.json",
    "baseline_preregistration.json",
    "future_acceptance_gate.json",
    "claim_ceiling.json",
}

REQUIRED_VALIDATORS = {
    "anti_lookup_generative_heldout_compliance",
    "support_disjoint_train_heldout_split",
    "identity_key_permutation",
    "target_leakage",
    "static_formula_solvability",
    "table_exact_lookup_solvability",
    "nearest_neighbor_retrieval_shortcut",
    "trace_order_shortcut",
    "counterfactual_pair_validity",
    "generator_provenance_completeness",
    "baseline_preregistration_completeness",
    "future_replay_recomputation_requirement",
    "future_ablation_requirement",
    "forbidden_action_guard",
}

REQUIRED_BASELINES = {
    "exact_lookup",
    "train_row_table_lookup",
    "nearest_neighbor_retrieval",
    "identity_key_lookup",
    "trace_order_lookup",
    "static_formula_decoder_visible_fields",
    "independent_per_task_optimal_ensemble_no_shared_latent_state",
    "shared_latent_state_without_cross_task_prediction_error_to_action_transfer",
    "multi_task_representation_learning",
    "pomdp_shared_belief_state_update_plus_control",
    "rnn_meta_rl_hidden_state_controller",
    "dyna_q_prioritized_sweeping",
    "mpc_world_model_planner",
    "causal_bandit",
    "oracle_feature_sharing_without_disputed_update_channel",
}

EXPECTED_CONTROL_REASONS = {
    "exact_lookup_surface": "exact_lookup_reaches_threshold",
    "table_lookup_surface": "table_lookup_reaches_threshold",
    "identity_key_surface": "identity_key_lookup_reaches_threshold",
    "trace_order_surface": "trace_order_lookup_reaches_threshold",
    "static_formula_surface": "static_formula_solves_task_b",
    "target_leak_surface": "target_leakage_detected",
    "missing_generator_provenance_surface": "missing_generator_provenance",
    "missing_counterfactual_pairs_surface": "missing_counterfactual_pairs",
    "overlapping_train_heldout_support_surface": "overlapping_train_heldout_support",
    "independent_ensemble_solvable_surface": "independent_ensemble_solves_without_shared_update",
    "shared_latent_no_transfer_solvable_surface": "shared_latent_no_transfer_solves_task_b",
    "visible_feature_only_task_b_surface": "task_b_visible_features_sufficient",
    "stored_answer_replay_surface": "stored_answer_replay_path_present",
    "hidden_label_exposure_surface": "hidden_label_exposure_detected",
}


def _runner():
    module_path = SRC / TASK_DIR / "runner.py"
    assert module_path.exists(), "runner module not implemented"
    return importlib.import_module(f"{TASK_DIR}.runner")


def test_valid_generated_fixture_passes_validators_and_records_serialized_provenance():
    runner = _runner()

    fixture = runner.generate_valid_surface_fixture(seed=runner.DEFAULT_SEED)
    validation = runner.validate_surface(fixture)

    assert validation["valid"] is True
    assert validation["blocking_reasons"] == []
    assert set(validation["validator_results"]) == REQUIRED_VALIDATORS
    assert all(row["passed"] is True for row in validation["validator_results"].values())
    assert set(fixture["task_family_ids"]) >= {
        "self_boundary_controllability",
        "replay_consolidation",
    }
    assert fixture["cross_task_prediction_error_event_ids"]
    assert fixture["shared_state_update_event_ids"]
    assert fixture["task_b_action_dependency_ids"]
    assert fixture["future_replay_requirement"]["recompute_from_serialized_state_and_observation"] is True
    assert fixture["future_replay_requirement"]["stored_answer_replay_allowed"] is False
    assert fixture["future_ablation_requirement"]["remove_cross_task_update_channel"] is True

    provenance = fixture["provenance"]
    for field in [
        "generator_function",
        "seed",
        "latent_parameter_ids",
        "train_ids",
        "heldout_ids",
        "task_family_ids",
        "support_signatures",
        "counterfactual_pair_ids",
        "prediction_error_event_ids",
        "shared_state_update_event_ids",
        "task_b_action_dependency_ids",
        "target_resolver_path",
        "code_path_hash",
        "baseline_preregistration_list",
    ]:
        assert provenance[field], field
    assert provenance["generator_function"].endswith("generate_valid_surface_fixture")
    assert set(provenance["baseline_preregistration_list"]) == REQUIRED_BASELINES


def test_all_positive_controls_fail_for_expected_reasons():
    runner = _runner()

    controls = runner.run_positive_controls()

    assert set(controls["control_results"]) == set(EXPECTED_CONTROL_REASONS)
    assert controls["all_positive_controls_failed"] is True
    for control_id, expected_reason in EXPECTED_CONTROL_REASONS.items():
        row = controls["control_results"][control_id]
        assert row["failed_as_expected"] is True
        assert row["expected_block_reason"] == expected_reason
        assert expected_reason in row["observed_blocking_reasons"]


def test_baseline_preregistration_is_complete_and_denies_forbidden_access():
    runner = _runner()

    preregistration = runner.build_baseline_preregistration()

    assert set(preregistration["baseline_ids"]) == REQUIRED_BASELINES
    assert preregistration["registered_before_candidate_code"] is True
    assert preregistration["candidate_code_created"] is False
    for row in preregistration["baselines"]:
        assert row["baseline_id"] in REQUIRED_BASELINES
        assert row["producer_function"]
        assert row["code_path_hash"]
        assert row["observation_access"] == "fair_visible_observation_access"
        assert row["hidden_target_labels_access"] is False
        assert row["answer_keys_access"] is False
        assert row["row_ids_access"] is False
        assert row["partner_or_context_ids_access"] is False
        assert row["trace_order_access"] is False
        if row["receives_disputed_cross_task_update_channel"]:
            assert row["independence_classification"] == "not_independent"
        else:
            assert row["independence_classification"] == "independent_baseline"


def test_execution_writes_required_artifacts_and_research_report(tmp_path):
    runner = _runner()

    output_dir = tmp_path / TASK_DIR
    report_path = tmp_path / REPORT_NAME
    run = runner.execute_design(output_dir=output_dir, persist_artifacts=True)
    written_report = runner.write_research_report(run, report_path=report_path)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in output_dir.glob("*.json")})
    for path in output_dir.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

    inherited = run["inherited_boundary_readback"]
    assert inherited["g0_route_spec_anchor"] == G0_ROUTE_ANCHOR
    assert inherited["g0_anchor_status_reconciliation_anchor"] == G0_RECONCILIATION_ANCHOR
    assert inherited["g0_survival_claim"] == "spec-level only"
    assert inherited["candidate_status_inherited"] is False
    assert inherited["harness_status_inherited"] is False
    assert inherited["tournament_status_inherited"] is False
    assert inherited["gate4_status_inherited"] is False
    assert inherited["runtime_status_inherited"] is False
    assert inherited["bridge_or_admission_status_inherited"] is False
    assert inherited["ego_mainline_status_inherited"] is False

    result = run["result"]
    assert result["verdict"] == "composite_cross_task_state_reuse_generative_heldout_surface_design_001a_pass"
    assert result["current_layer"] == "engineering-governance / anti-lookup generative heldout surface design only"
    assert result["mainline_integration_status"] == "not integrated"
    assert result["enabled_status"].startswith("no runtime")
    assert "Callable generator and validators" in result["real_trigger_evidence"]
    assert result["candidate_code_created"] is False
    assert result["candidate_score_produced"] is False
    assert result["harness_or_tournament_execution_created"] is False
    assert result["gate4_replacement_design_created"] is False
    assert result["runtime_or_mainline_path_created"] is False
    assert result["bridge_or_admission_path_created"] is False
    assert result["stop_conditions_triggered"] == []

    report_text = written_report.read_text(encoding="utf-8")
    assert "Verdict: `composite_cross_task_state_reuse_generative_heldout_surface_design_001a_pass`" in report_text
    assert "Surface-design / protocol-governance only" in report_text
    assert "No candidate model, harness, tournament, Gate4 replacement, runtime, bridge/admission, EGO-mainline" in report_text


def test_future_acceptance_gate_claim_ceiling_and_forbidden_actions_are_bounded():
    runner = _runner()

    run = runner.execute_design(output_dir=None, persist_artifacts=False)
    gate = run["future_acceptance_gate"]
    ceiling = run["claim_ceiling"]
    guard = run["forbidden_action_guard"]

    assert gate["accept_only_if_valid_generated_fixture_passes"] is True
    assert gate["accept_only_if_all_positive_controls_fail"] is True
    assert gate["candidate_implementation_authorized"] is False
    assert gate["harness_or_tournament_execution_authorized"] is False
    assert gate["gate4_replacement_design_authorized"] is False
    assert gate["runtime_bridge_admission_or_ego_mainline_authorized"] is False
    assert gate["future_replay_must_recompute_task_b_action"] is True
    assert gate["future_ablation_must_remove_cross_task_update_channel"] is True

    for claim in [
        "mechanism validity",
        "Gate4 validity",
        "candidate behavior",
        "tournament outcome",
        "runtime readiness",
        "bridge/admission readiness",
        "agency",
        "subjectivity",
        "consciousness",
        "emotion",
        "autonomy",
        "companion readiness",
        "EGO readiness",
    ]:
        assert claim in ceiling["forbidden_claims"]

    assert guard["candidate_code_created"] is False
    assert guard["candidate_score_produced"] is False
    assert guard["harness_or_tournament_execution_created"] is False
    assert guard["gate4_replacement_design_created"] is False
    assert guard["runtime_or_mainline_path_created"] is False
    assert guard["bridge_or_admission_path_created"] is False
    assert guard["llm_rag_ui_companion_path_created"] is False


def test_blocked_verdict_when_positive_control_is_forced_to_pass():
    runner = _runner()

    run = runner.execute_design(
        output_dir=None,
        persist_artifacts=False,
        force_positive_control_pass="target_leak_surface",
    )

    assert run["result"]["verdict"] == (
        "composite_cross_task_state_reuse_generative_heldout_surface_design_001a_blocked_by_positive_control_failure"
    )
    assert "positive_control_mismatch:target_leak_surface" in run["result"]["stop_conditions_triggered"]
