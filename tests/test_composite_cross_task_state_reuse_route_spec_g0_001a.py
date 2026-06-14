import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "composite_cross_task_state_reuse_route_spec_g0_001a"
REPORT_NAME = "COMPOSITE-CROSS-TASK-STATE-REUSE-ROUTE-SPEC-G0-001A.md"
ARTIFACT_DIR = ROOT / "artifacts" / TASK_ID
REQUIRED_ARTIFACTS = {
    "result.json",
    "composite_route_spec.json",
    "baseline_equivalence_matrix.json",
    "positive_controls.json",
    "non_equivalence_requirements.json",
    "future_surface_requirements.json",
    "claim_ceiling.json",
}
REQUIRED_BASELINES = {
    "independent_per_task_optimal_ensemble",
    "shared_latent_no_cross_task_transfer",
    "multi_task_representation_learning",
    "pomdp_shared_belief_state_update_control",
    "dyna_q",
    "prioritized_sweeping",
    "mpc_world_model_planner",
    "meta_rl_recurrent_hidden_state_controller",
    "causal_bandit",
    "retrieval_nearest_neighbor_table_lookup",
    "static_rule_formula_decoder",
    "oracle_feature_sharing_no_update_channel",
}
ALLOWED_REJECTION_CLASSES = {
    "equivalent",
    "subset_of_baseline",
    "baseline_subsumes_spec",
    "not_distinguishable_from_baseline",
    "underspecified",
}


def _runner():
    module_path = SRC / TASK_ID / "runner.py"
    assert module_path.exists(), "runner module not implemented"
    return importlib.import_module(f"{TASK_ID}.runner")


def test_composite_route_spec_survives_spec_level_only_without_candidate_or_runtime():
    runner = _runner()

    run = runner.execute_adjudication(output_dir=None, persist_artifacts=False)
    result = run["result"]
    spec = run["composite_route_spec"]
    matrix = run["baseline_equivalence_matrix"]

    assert spec["spec_id"] == "composite_cross_task_state_reuse_route_spec_g0_001a_candidate_route_spec"
    assert result["verdict"] == "composite_cross_task_state_reuse_route_spec_g0_001a_survives_spec_level_only"
    assert result["current_layer"] == "engineering-governance / composite route-spec baseline-equivalence preflight only"
    assert result["mainline_integration_status"] == "not integrated"
    assert result["enabled_status"].startswith("no runtime")
    assert "Callable spec-level adjudicators" in result["real_trigger_evidence"]
    assert result["composite_route_survives_spec_level_only"] is True
    assert result["candidate_code_created"] is False
    assert result["candidate_score_produced"] is False
    assert result["tournament_execution_attempted"] is False
    assert result["gate4_replacement_design_created"] is False
    assert result["runtime_or_mainline_path_created"] is False
    assert result["bridge_or_admission_path_created"] is False
    assert result["llm_rag_ui_companion_path_created"] is False
    assert result["stop_conditions_triggered"] == []
    assert result["next_minimal_closed_loop_action"] == (
        "separate future task to design an anti-lookup generative heldout surface"
    )
    assert set(matrix["candidate_spec_rows"]) == REQUIRED_BASELINES
    assert all(
        row["classification"] == "non_equivalent_with_required_observable"
        for row in matrix["candidate_spec_rows"].values()
    )
    assert all(row["callable_invoked"] is True for row in matrix["candidate_spec_rows"].values())
    assert all(row["code_path_hash"] for row in matrix["candidate_spec_rows"].values())


def test_positive_controls_are_rejected_by_callable_adjudicators():
    runner = _runner()

    run = runner.execute_adjudication(output_dir=None, persist_artifacts=False)
    controls = run["positive_controls"]

    expected = {
        "independent_ensemble_rename_control": "independent_per_task_optimal_ensemble",
        "shared_label_only_control": "shared_label_only",
        "pomdp_belief_rename_control": "pomdp_shared_belief_state_update_control",
        "multi_task_representation_control": "multi_task_representation_learning",
        "meta_rl_rnn_hidden_state_control": "meta_rl_recurrent_hidden_state_controller",
        "replay_rename_control": "dyna_q",
        "retrieval_memory_control": "retrieval_nearest_neighbor_table_lookup",
        "label_renaming_novelty_control": "label_renaming",
    }
    assert set(controls["control_results"]) == set(expected)
    for control_id, expected_family in expected.items():
        row = controls["control_results"][control_id]
        assert row["survives"] is False
        assert row["expected_rejection_family"] == expected_family
        assert row["rejected_as_expected"] is True
        assert row["strongest_classification"] in ALLOWED_REJECTION_CLASSES
        assert row["required_observable_present"] is False
        assert row["candidate_code_executed"] is False
        if expected_family in REQUIRED_BASELINES:
            assert row["baseline_rows"][expected_family]["classification"] in {
                "equivalent",
                "subset_of_baseline",
                "baseline_subsumes_spec",
            }
    assert controls["all_positive_controls_rejected"] is True


def test_missing_non_equivalence_requirements_cannot_survive():
    runner = _runner()

    mutations = {
        "missing_shared_state": lambda spec: spec.update({"shared_state": ""}),
        "missing_cross_task_transfer": lambda spec: spec.update(
            {
                "prediction_error_update_effect": "updates only the source task local policy",
                "cross_task_action_selection_observable": "",
            }
        ),
        "missing_support_disjoint_condition": lambda spec: spec.update({"support_disjoint_condition": ""}),
        "missing_baseline_contrast": lambda spec: spec.update({"baseline_contrasts": {}}),
        "missing_ablation": lambda spec: spec.update({"required_ablation": ""}),
        "missing_leakage_check": lambda spec: spec.update({"leakage_check": {"forbidden_fields": ["target_field"]}}),
        "missing_replay_recomputation": lambda spec: spec.update(
            {"replay_recomputation_requirement": "stored answer replay is acceptable"}
        ),
    }

    for expected_reason, mutate in mutations.items():
        spec = runner.build_composite_route_spec()
        mutate(spec)
        adjudication = runner.adjudicate_composite_route_spec(spec)
        assert adjudication["survives"] is False, expected_reason
        assert expected_reason in adjudication["blocking_reasons"]


def test_controls_forbid_pomdp_rnn_replay_retrieval_and_label_renaming_as_survival_routes():
    runner = _runner()

    controls = [
        (runner.build_pomdp_belief_positive_control, "pomdp_shared_belief_state_update_control"),
        (runner.build_meta_rl_rnn_positive_control, "meta_rl_recurrent_hidden_state_controller"),
        (runner.build_replay_rename_positive_control, "dyna_q"),
        (runner.build_retrieval_positive_control, "retrieval_nearest_neighbor_table_lookup"),
        (runner.build_label_renaming_positive_control, "label_renaming"),
    ]
    for factory, expected_family in controls:
        adjudication = runner.adjudicate_composite_route_spec(factory())
        assert adjudication["survives"] is False
        assert adjudication["required_observable_present"] is False
        if expected_family in REQUIRED_BASELINES:
            assert adjudication["baseline_rows"][expected_family]["classification"] in {
                "equivalent",
                "subset_of_baseline",
                "baseline_subsumes_spec",
            }
        else:
            assert "label_terms_without_distinct_computation" in adjudication["blocking_reasons"]


def test_materialized_artifacts_and_research_report_parse(tmp_path):
    runner = _runner()

    output_dir = tmp_path / TASK_ID
    report_path = tmp_path / REPORT_NAME
    run = runner.execute_adjudication(output_dir=output_dir, persist_artifacts=True)
    written_report = runner.write_research_report(run, report_path=report_path)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in output_dir.glob("*.json")})
    for path in output_dir.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

    report_text = written_report.read_text(encoding="utf-8")
    assert "Verdict: `composite_cross_task_state_reuse_route_spec_g0_001a_survives_spec_level_only`" in report_text
    assert "Spec-level baseline-equivalence governance only" in report_text
    assert "anti-lookup generative heldout surface" in report_text
    assert (
        "No candidate model, harness, tournament, Gate4 replacement, runtime, bridge, admission, "
        "LLM/RAG/UI, or companion path is authorized."
    ) in report_text


def test_claim_ceiling_forbids_mechanism_gate4_agency_subjectivity_and_readiness_claims():
    runner = _runner()

    run = runner.execute_adjudication(output_dir=None, persist_artifacts=False)
    forbidden = set(run["claim_ceiling"]["forbidden_claims"])

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
        assert claim in forbidden
    assert run["result"]["claim_ceiling"] == runner.CLAIM_CEILING
    assert run["future_surface_requirements"]["candidate_implementation_authorized"] is False
    assert run["future_surface_requirements"]["gate4_replacement_authorized"] is False
    assert run["future_surface_requirements"]["future_surface_protocol"] == (
        "ANTI-LOOKUP-GENERATIVE-HELDOUT-SURFACE-PROTOCOL-001A"
    )
