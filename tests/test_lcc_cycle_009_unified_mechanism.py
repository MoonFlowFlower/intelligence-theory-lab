import json

from theory_lab.lcc_cycle_009_unified_mechanism import run_cycle_009


def test_cycle_009_survives_unified_mechanism_contract(tmp_path):
    result = run_cycle_009(tmp_path)

    assert result["cycle_verdict"] == "lcc_contract_strengthened_unified_mechanism_bounded"
    assert result["stopped_at"] is None
    assert result["stop_conditions_triggered"] == []
    assert result["claim_boundary"] == "bounded unified mechanism anti-specialization contract only"


def test_unified_interface_static_scan_and_mixed_suite(tmp_path):
    result = run_cycle_009(tmp_path)
    interface = result["tasks"]["LCC-C9-001"]
    mixed = result["tasks"]["LCC-C9-002"]

    assert interface["verdict"] == "unified_interface_contract_passed"
    assert interface["one_candidate_interface"] is True
    assert interface["one_selector_path"] is True
    assert interface["one_effect_prediction_path"] is True
    assert interface["one_update_path"] is True
    assert interface["static_scan"]["candidate_control_forbidden_hits"] == []
    assert interface["static_scan"]["selector_dispatch_branch_count"] == 0
    assert interface["task_family_visible_to_candidate"] is False

    assert mixed["verdict"] == "mixed_prior_family_suite_passed"
    assert mixed["overall_family_pass_rate"] >= 0.80
    assert mixed["min_family_pass_rate"] >= 0.60
    assert mixed["label_permutation_change_rate"] <= 0.05
    assert mixed["effect_swap_change_rate"] >= 0.80
    assert mixed["behavior_only_replay"]["passed"] is True
    assert mixed["behavior_only_replay_match"] is True
    for family, payload in mixed["family_results"].items():
        assert payload["pass_rate"] >= 0.60, family
        assert payload["action_distribution_causality"] >= 0.60, family


def test_hybrid_metadata_ablation_and_strong_baselines(tmp_path):
    result = run_cycle_009(tmp_path)
    hybrid = result["tasks"]["LCC-C9-003"]
    metadata = result["tasks"]["LCC-C9-004"]
    ablation = result["tasks"]["LCC-C9-005"]
    baselines = result["tasks"]["LCC-C9-006"]

    assert hybrid["verdict"] == "hybrid_holdout_contracts_passed"
    assert hybrid["hybrid_success_rate"] >= 0.70
    assert hybrid["specialist_ensemble_gap"] >= 0.15
    assert hybrid["nearest_neighbor_gap"] >= 0.15
    assert hybrid["static_recipe_gap"] >= 0.15
    assert hybrid["label_permutation_change_rate"] <= 0.05
    assert hybrid["effect_swap_change_rate"] >= 0.80
    assert hybrid["baselines"]["PerContractSpecialistEnsemble"]["equivalent"] is False
    assert hybrid["baselines"]["NearestNeighborTracePolicy"]["equivalent"] is False
    assert hybrid["baselines"]["StaticRecipeTableBaseline"]["equivalent"] is False

    assert metadata["verdict"] == "metadata_mutation_invariance_passed"
    assert metadata["metadata_mutation_action_change_rate"] == 0.0
    assert metadata["contract_id_mutation_action_change_rate"] == 0.0
    assert metadata["forged_metadata_affects_behavior"] is False
    assert metadata["recommended_action_ignored"] is True

    assert ablation["verdict"] == "unified_mechanism_ablation_necessity_passed"
    for ablation_name in [
        "NoEffectModelPolicy",
        "NoInterventionUpdatePolicy",
        "NoCounterfactualQueryPolicy",
        "NoUncertaintyPolicy",
        "NoRepresentationLearningPolicy",
        "NoGoalConditioningPolicy",
        "NoRelationalBindingPolicy",
        "OpenLoopOnlyPolicy",
    ]:
        assert ablation["ablations"][ablation_name]["equivalent"] is False

    assert baselines["verdict"] == "strong_unified_baselines_not_equivalent"
    for baseline_name in [
        "PerContractSpecialistEnsemble",
        "NearestNeighborTracePolicy",
        "ContextualHeuristicBaseline",
        "StaticRecipeTableBaseline",
        "TaskFamilyClassifierPolicy",
        "GoalLookupTablePolicy",
        "SequenceLookupPolicy",
        "GraphNearestNeighborPolicy",
    ]:
        assert baselines["baselines"][baseline_name]["equivalent"] is False
    assert baselines["oracle_unified_diagnostic_upper_bound"]["diagnostic_only"] is True
    assert baselines["oracle_unified_diagnostic_upper_bound"]["valid_competitor"] is False


def test_replay_provenance_and_required_cycle_009_artifacts(tmp_path):
    result = run_cycle_009(tmp_path)
    provenance = result["tasks"]["LCC-C9-007"]

    assert provenance["verdict"] == "unified_replay_and_provenance_passed"
    assert provenance["behavior_only_replay"]["passed"] is True
    assert provenance["agent_identity_mutation"]["passed"] is True
    assert provenance["forged_self_report_injection"]["passed"] is True
    assert provenance["scenario_label_mutation"]["passed"] is True
    assert provenance["contract_id_mutation"]["passed"] is True
    assert provenance["task_family_mutation"]["passed"] is True
    assert provenance["metric_provenance_scan"]["passed"] is True
    assert provenance["hidden_state_leak_scan"]["passed"] is True
    assert provenance["action_label_use_scan"]["passed"] is True
    assert provenance["goal_id_leak_scan"]["passed"] is True
    assert provenance["entity_id_shortcut_scan"]["passed"] is True
    assert provenance["object_name_leak_scan"]["passed"] is True
    assert provenance["causal_graph_leak_scan"]["passed"] is True
    assert provenance["transition_table_leak_scan"]["passed"] is True
    assert provenance["plan_table_leak_scan"]["passed"] is True

    required = [
        "LCC-C9-000/STATUS.md",
        "LCC-C9-000/cycle_008_freeze_manifest.json",
        "LCC-C9-001/unified_interface_contract.md",
        "LCC-C9-001/unified_interface_schema.json",
        "LCC-C9-001/specialization_static_scan_report.md",
        "LCC-C9-002/mixed_family_suite_report.md",
        "LCC-C9-002/mixed_family_suite_results.json",
        "LCC-C9-002/traces.jsonl",
        "LCC-C9-002/behavior_only_replay.json",
        "LCC-C9-003/hybrid_holdout_contract_report.md",
        "LCC-C9-003/hybrid_holdout_contract_results.json",
        "LCC-C9-004/metadata_mutation_report.md",
        "LCC-C9-004/metadata_mutation_results.json",
        "LCC-C9-005/cycle_009_ablation_report.md",
        "LCC-C9-005/cycle_009_ablation_results.json",
        "LCC-C9-006/cycle_009_strong_baseline_report.md",
        "LCC-C9-006/cycle_009_baseline_equivalence.json",
        "LCC-C9-007/behavior_only_replay.json",
        "LCC-C9-007/provenance_audit_report.md",
        "LCC-C9-007/identity_mutation_report.md",
        "CYCLE_009_DECISION.md",
        "cycle_009_decision.json",
    ]
    for rel_path in required:
        assert (tmp_path / rel_path).exists(), rel_path

    decision = json.loads((tmp_path / "cycle_009_decision.json").read_text(encoding="utf-8"))
    assert decision["verdict"] == "lcc_contract_strengthened_unified_mechanism_bounded"
    assert decision["theory_support"] == "not_yet"
    assert decision["general_lcc_agent"] == "not_authorized"
    assert decision["ego_migration"] == "no_go"
    assert decision["autonomous_theory_search"] == "not_authorized"
    assert decision["next_step"] == "human_review_required_before_cycle_010_or_stronger_claim"
    assert all(gate["passed"] for gate in decision["required_gates"].values())
