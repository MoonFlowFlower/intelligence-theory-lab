import json

from theory_lab.lcc_cycle_007_relational_compositional import run_cycle_007


def test_cycle_007_survives_relational_compositional_contract(tmp_path):
    result = run_cycle_007(tmp_path)

    assert result["cycle_verdict"] == "lcc_contract_strengthened_relational_compositional_bounded"
    assert result["stopped_at"] is None
    assert result["stop_conditions_triggered"] == []
    assert result["claim_boundary"] == "bounded relational compositional counterfactual transfer contract only"


def test_entity_permutation_role_sensitivity_and_replay(tmp_path):
    result = run_cycle_007(tmp_path)
    role = result["tasks"]["LCC-C7-002"]

    assert role["verdict"] == "entity_permutation_role_sensitivity_passed"
    assert role["entity_permutation_behavior_change_rate"] <= 0.10
    assert role["role_swap_behavior_change_rate"] >= 0.80
    assert role["visual_feature_shortcut_rate"] <= 0.20
    assert role["label_permutation_change_rate"] <= 0.05
    assert role["effect_swap_change_rate"] >= 0.80
    assert role["behavior_only_replay"]["passed"] is True
    assert role["baselines"]["EntityIDPolicy"]["equivalent"] is False
    assert role["baselines"]["VisualFeaturePolicy"]["equivalent"] is False


def test_cardinality_composition_tool_chain_and_relational_perturbation(tmp_path):
    result = run_cycle_007(tmp_path)
    cardinality = result["tasks"]["LCC-C7-003"]
    composition = result["tasks"]["LCC-C7-004"]
    tool_chain = result["tasks"]["LCC-C7-005"]
    perturbation = result["tasks"]["LCC-C7-006"]

    assert cardinality["verdict"] == "variable_cardinality_distractor_passed"
    assert cardinality["variable_cardinality_success_rate"] >= 0.80
    assert cardinality["distractor_invariance_rate"] >= 0.80
    assert cardinality["irrelevant_entity_removal_invariance"] >= 0.80
    assert cardinality["fixed_slot_baseline_gap"] >= 0.25
    assert cardinality["baselines"]["FixedSlotPolicy"]["equivalent"] is False
    assert cardinality["baselines"]["RawNearestNeighborGraphPolicy"]["equivalent"] is False

    assert composition["verdict"] == "compositional_relation_transfer_passed"
    assert composition["novel_composition_success_rate"] >= 0.75
    assert composition["single_schema_baseline_gap"] >= 0.25
    assert composition["nearest_neighbor_graph_gap"] >= 0.25
    assert composition["label_permutation_change_rate"] <= 0.05
    assert composition["effect_swap_change_rate"] >= 0.80

    assert tool_chain["verdict"] == "tool_mediated_chain_passed"
    assert tool_chain["tool_chain_success_rate"] >= 0.80
    assert tool_chain["direct_effect_trap_avoidance"] >= 0.80
    assert tool_chain["role_swapped_tool_success"] >= 0.80
    assert tool_chain["distractor_tool_robustness"] >= 0.80

    assert perturbation["verdict"] == "relational_counterfactual_perturbation_passed"
    assert perturbation["relation_edge_perturbation_action_change_rate"] >= 0.70
    assert perturbation["nuisance_feature_perturbation_action_change_rate"] <= 0.20
    assert perturbation["role_embedding_swap_rank_flip_rate"] >= 0.70
    assert perturbation["entity_id_swap_rank_flip_rate"] <= 0.20
    assert perturbation["relation_uncertainty_diagnostic_rate"] >= 0.70


def test_ablation_and_strong_relational_baselines_are_not_equivalent(tmp_path):
    result = run_cycle_007(tmp_path)
    ablation = result["tasks"]["LCC-C7-007"]
    baselines = result["tasks"]["LCC-C7-008"]

    assert ablation["verdict"] == "relational_ablation_necessity_passed"
    for ablation_name in [
        "NoRelationalEncoderPolicy",
        "EntityIDOnlyPolicy",
        "NoRoleBindingPolicy",
        "NoRelationCompositionPolicy",
        "NoInterventionHistoryPolicy",
        "NoCounterfactualQueryPolicy",
        "RawObservationOnlyPolicy",
    ]:
        assert ablation["ablations"][ablation_name]["equivalent"] is False

    assert baselines["verdict"] == "strong_relational_baselines_not_equivalent"
    for baseline in [
        "EntityIDPolicy",
        "VisualFeaturePolicy",
        "FixedSlotPolicy",
        "RawNearestNeighborGraphPolicy",
        "GraphNearestNeighborPolicy",
        "SequenceLookupPolicy",
        "ToolNameHeuristicPolicy",
        "ContextualGraphHeuristicBaseline",
    ]:
        assert baselines["baselines"][baseline]["equivalent"] is False
    assert baselines["relational_oracle_diagnostic_upper_bound"]["diagnostic_only"] is True


def test_replay_provenance_and_required_cycle_007_artifacts(tmp_path):
    result = run_cycle_007(tmp_path)
    provenance = result["tasks"]["LCC-C7-009"]

    assert provenance["verdict"] == "replay_and_provenance_passed"
    assert provenance["behavior_only_replay"]["passed"] is True
    assert provenance["agent_identity_mutation"]["passed"] is True
    assert provenance["forged_self_report_injection"]["passed"] is True
    assert provenance["scenario_label_mutation"]["passed"] is True
    assert provenance["metric_provenance_scan"]["passed"] is True
    assert provenance["hidden_state_leak_scan"]["passed"] is True
    assert provenance["action_label_use_scan"]["passed"] is True
    assert provenance["entity_id_shortcut_scan"]["passed"] is True
    assert provenance["object_name_leak_scan"]["passed"] is True
    assert provenance["role_label_leak_scan"]["passed"] is True
    assert provenance["causal_graph_leak_scan"]["passed"] is True
    assert provenance["oracle_relation_schema_leak_scan"]["passed"] is True
    assert provenance["transition_table_leak_scan"]["passed"] is True
    assert provenance["plan_table_leak_scan"]["passed"] is True

    required = [
        "LCC-C7-000/STATUS.md",
        "LCC-C7-000/cycle_006_freeze_manifest.json",
        "LCC-C7-001/relational_testbed_report.md",
        "LCC-C7-001/relational_testbed_config.json",
        "LCC-C7-001/leak_scan_report.md",
        "LCC-C7-002/entity_permutation_role_sensitivity_report.md",
        "LCC-C7-002/entity_permutation_role_sensitivity_results.json",
        "LCC-C7-002/traces.jsonl",
        "LCC-C7-002/behavior_only_replay.json",
        "LCC-C7-003/variable_cardinality_distractor_report.md",
        "LCC-C7-003/variable_cardinality_distractor_results.json",
        "LCC-C7-004/compositional_relation_transfer_report.md",
        "LCC-C7-004/compositional_relation_transfer_results.json",
        "LCC-C7-005/tool_mediated_chain_report.md",
        "LCC-C7-005/tool_mediated_chain_results.json",
        "LCC-C7-006/relational_counterfactual_perturbation_report.md",
        "LCC-C7-006/relational_counterfactual_perturbation_results.json",
        "LCC-C7-007/cycle_007_ablation_report.md",
        "LCC-C7-007/cycle_007_ablation_results.json",
        "LCC-C7-008/cycle_007_strong_baseline_report.md",
        "LCC-C7-008/cycle_007_baseline_equivalence.json",
        "LCC-C7-009/behavior_only_replay.json",
        "LCC-C7-009/provenance_audit_report.md",
        "LCC-C7-009/identity_mutation_report.md",
        "CYCLE_007_DECISION.md",
        "cycle_007_decision.json",
    ]
    for rel_path in required:
        assert (tmp_path / rel_path).exists(), rel_path

    decision = json.loads((tmp_path / "cycle_007_decision.json").read_text(encoding="utf-8"))
    assert decision["verdict"] == "lcc_contract_strengthened_relational_compositional_bounded"
    assert decision["theory_support"] == "not_yet"
    assert decision["general_lcc_agent"] == "not_authorized"
    assert decision["ego_migration"] == "no_go"
    assert all(gate["passed"] for gate in decision["required_gates"].values())
