import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "gate4_route2_g0_spec_baseline_equivalence_001a"
REPORT_NAME = "GATE4-ROUTE2-G0-SPEC-BASELINE-EQUIVALENCE-001A.md"
ARTIFACT_DIR = ROOT / "artifacts" / TASK_ID
REQUIRED_ARTIFACTS = {
    "result.json",
    "baseline_equivalence_matrix.json",
    "route2_candidate_step_spec.json",
    "positive_controls.json",
    "non_equivalence_requirements.json",
    "future_surface_requirements.json",
    "claim_ceiling.json",
}
REQUIRED_BASELINES = {
    "dyna_q",
    "prioritized_sweeping",
    "pomdp_belief_control",
    "causal_bandit",
    "model_predictive_control",
    "retrieval_table_lookup",
    "static_rule_formula_decoder",
    "independent_module_ensemble",
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


def test_current_repo_route2_spec_blocks_as_underspecified_without_candidate_execution(tmp_path):
    runner = _runner()

    run = runner.execute_adjudication(output_dir=tmp_path / TASK_ID, persist_artifacts=False)
    result = run["result"]
    candidate_spec = run["route2_candidate_step_spec"]
    matrix = run["baseline_equivalence_matrix"]

    assert candidate_spec["spec_status"] == "no_concrete_route2_candidate_step_found"
    assert result["verdict"] == "gate4_route2_g0_spec_baseline_equivalence_001a_route2_blocked_by_underspecification"
    assert result["current_layer"] == "engineering-governance / route-spec baseline-equivalence preflight only"
    assert result["mainline_integration_status"] == "not integrated"
    assert result["enabled_status"].startswith("no runtime")
    assert "Callable spec-level adjudicators" in result["real_trigger_evidence"]
    assert result["route2_survives_spec_level_only"] is False
    assert result["candidate_code_created"] is False
    assert result["candidate_score_produced"] is False
    assert result["tournament_execution_attempted"] is False
    assert result["gate4_replacement_design_created"] is False
    assert result["runtime_or_mainline_path_created"] is False
    assert result["bridge_or_admission_path_created"] is False
    assert result["llm_rag_ui_companion_path_created"] is False
    assert "route2_candidate_step_spec_underspecified" in result["stop_conditions_triggered"]
    assert set(matrix["candidate_spec_rows"]) == REQUIRED_BASELINES
    assert all(row["classification"] == "underspecified" for row in matrix["candidate_spec_rows"].values())


def test_positive_controls_are_rejected_by_callable_adjudicators():
    runner = _runner()

    run = runner.execute_adjudication(output_dir=None, persist_artifacts=False)
    controls = run["positive_controls"]

    expected = {
        "dyna_q_rename_control": "dyna_q",
        "prioritized_sweeping_rename_control": "prioritized_sweeping",
        "pomdp_belief_control": "pomdp_belief_control",
        "causal_bandit_control": "causal_bandit",
        "mpc_control": "model_predictive_control",
        "retrieval_control": "retrieval_table_lookup",
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
        if expected_family != "label_renaming":
            assert row["baseline_rows"][expected_family]["classification"] in {
                "equivalent",
                "subset_of_baseline",
                "baseline_subsumes_spec",
            }
    assert controls["all_positive_controls_rejected"] is True


def test_label_renaming_replay_self_viability_and_social_terms_cannot_survive():
    runner = _runner()

    spec = runner.build_label_renaming_positive_control()
    adjudication = runner.adjudicate_route2_spec(spec)

    assert adjudication["survives"] is False
    assert adjudication["verdict"] == "gate4_route2_g0_spec_baseline_equivalence_001a_route2_blocked_by_underspecification"
    assert "label_terms_without_computation_change" in adjudication["blocking_reasons"]
    assert adjudication["required_observable_present"] is False


def test_retrieval_table_id_and_trace_order_spec_cannot_survive():
    runner = _runner()

    spec = runner.build_retrieval_positive_control()
    adjudication = runner.adjudicate_route2_spec(spec)

    assert adjudication["survives"] is False
    assert adjudication["verdict"] == "gate4_route2_g0_spec_baseline_equivalence_001a_route2_closed_by_baseline_equivalence"
    assert adjudication["baseline_rows"]["retrieval_table_lookup"]["classification"] in {
        "equivalent",
        "subset_of_baseline",
        "baseline_subsumes_spec",
    }
    assert "forbidden_lookup_or_identity_shortcut" in adjudication["blocking_reasons"]


def test_specs_missing_cross_context_ablation_leakage_or_replay_requirements_cannot_survive():
    runner = _runner()

    no_cross_context = runner.build_minimal_route2_like_spec()
    no_cross_context["prediction_error_update_effect"] = "updates only the same context action preference"
    no_cross_context["cross_context_action_selection_observable"] = ""
    no_cross_context_result = runner.adjudicate_route2_spec(no_cross_context)
    assert no_cross_context_result["survives"] is False
    assert "missing_cross_context_action_selection_observable" in no_cross_context_result["blocking_reasons"]

    no_ablation = runner.build_minimal_route2_like_spec()
    no_ablation["required_ablation"] = ""
    no_ablation_result = runner.adjudicate_route2_spec(no_ablation)
    assert no_ablation_result["survives"] is False
    assert "missing_required_ablation" in no_ablation_result["blocking_reasons"]

    no_leakage = runner.build_minimal_route2_like_spec()
    no_leakage["leakage_check"] = {"forbidden_fields": ["target_field"]}
    no_leakage_result = runner.adjudicate_route2_spec(no_leakage)
    assert no_leakage_result["survives"] is False
    assert "missing_leakage_check_terms" in no_leakage_result["blocking_reasons"]

    no_replay = runner.build_minimal_route2_like_spec()
    no_replay["replay_recomputation_requirement"] = "stored answer replay is acceptable"
    no_replay_result = runner.adjudicate_route2_spec(no_replay)
    assert no_replay_result["survives"] is False
    assert "missing_replay_recomputation_requirement" in no_replay_result["blocking_reasons"]


def test_minimal_non_equivalence_fixture_survives_spec_level_only_without_authorizing_candidate_work():
    runner = _runner()

    spec = runner.build_minimal_route2_like_spec()
    adjudication = runner.adjudicate_route2_spec(spec)

    assert adjudication["survives"] is True
    assert adjudication["verdict"] == "gate4_route2_g0_spec_baseline_equivalence_001a_route2_survives_spec_level_only"
    assert adjudication["required_observable_present"] is True
    assert all(
        row["classification"] == "non_equivalent_with_required_observable"
        for row in adjudication["baseline_rows"].values()
    )
    assert adjudication["candidate_code_executed"] is False
    assert adjudication["candidate_score_produced"] is False
    assert adjudication["next_allowed_action"] == "separate_future_anti_lookup_generative_heldout_surface_design_task_only"


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
    assert "Verdict: `gate4_route2_g0_spec_baseline_equivalence_001a_route2_blocked_by_underspecification`" in report_text
    assert "stream-keyed count-table" in report_text
    assert "No candidate model, harness, tournament, Gate4 replacement, runtime, bridge, admission, LLM/RAG/UI, or companion path is authorized." in report_text


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
