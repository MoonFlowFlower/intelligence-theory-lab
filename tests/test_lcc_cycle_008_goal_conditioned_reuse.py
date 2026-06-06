import json

from theory_lab.lcc_cycle_008_goal_conditioned_reuse import run_cycle_008


def test_cycle_008_survives_goal_conditioned_reuse_contract(tmp_path):
    result = run_cycle_008(tmp_path)

    assert result["cycle_verdict"] == "lcc_contract_strengthened_goal_conditioned_reuse_bounded"
    assert result["stopped_at"] is None
    assert result["stop_conditions_triggered"] == []
    assert result["claim_boundary"] == "bounded goal-conditioned counterfactual model reuse contract only"


def test_goal_switch_fixed_effects_and_replay(tmp_path):
    result = run_cycle_008(tmp_path)
    goal_switch = result["tasks"]["LCC-C8-002"]

    assert goal_switch["verdict"] == "goal_switch_fixed_effects_passed"
    assert goal_switch["goal_switch_action_change_rate"] >= 0.80
    assert goal_switch["effect_model_reuse_rate"] >= 0.80
    assert goal_switch["task_label_invariance_rate"] >= 0.80
    assert goal_switch["goal_label_permutation_change_rate"] <= 0.05
    assert goal_switch["goal_vector_perturbation_action_change_rate"] >= 0.80
    assert goal_switch["behavior_only_replay"]["passed"] is True
    assert goal_switch["baselines"]["TaskLabelPolicy"]["equivalent"] is False
    assert goal_switch["baselines"]["GoalLookupTablePolicy"]["equivalent"] is False
    assert goal_switch["baselines"]["NearestNeighborTaskPolicy"]["equivalent"] is False


def test_constraint_composition_tradeoff_and_reuse(tmp_path):
    result = run_cycle_008(tmp_path)
    constraint = result["tasks"]["LCC-C8-003"]
    composition = result["tasks"]["LCC-C8-004"]
    tradeoff = result["tasks"]["LCC-C8-005"]
    reuse = result["tasks"]["LCC-C8-006"]

    assert constraint["verdict"] == "constraint_reweighting_passed"
    assert constraint["constraint_reweighting_action_change_rate"] >= 0.70
    assert constraint["constraint_violation_rate"] <= 0.20
    assert constraint["constraint_label_permutation_change_rate"] <= 0.05
    assert constraint["effect_model_reuse_rate"] >= 0.80

    assert composition["verdict"] == "novel_goal_composition_passed"
    assert composition["novel_goal_composition_success_rate"] >= 0.75
    assert composition["goal_lookup_gap"] >= 0.25
    assert composition["nearest_neighbor_task_gap"] >= 0.25
    assert composition["effect_model_reuse_rate"] >= 0.80
    assert composition["label_permutation_change_rate"] <= 0.05
    assert composition["baselines"]["GoalLookupTablePolicy"]["equivalent"] is False
    assert composition["baselines"]["NearestNeighborTaskPolicy"]["equivalent"] is False

    assert tradeoff["verdict"] == "conflicting_goal_tradeoff_passed"
    assert tradeoff["weight_sensitive_tradeoff_rate"] >= 0.70
    assert tradeoff["constraint_respecting_tradeoff_rate"] >= 0.75
    assert tradeoff["goal_weight_perturbation_action_change_rate"] >= 0.70
    assert tradeoff["baselines"]["FixedPriorityPolicy"]["equivalent"] is False
    assert tradeoff["baselines"]["RewardTablePolicy"]["equivalent"] is False

    assert reuse["verdict"] == "model_reuse_vs_relearning_passed"
    assert reuse["zero_shot_goal_switch_success_rate"] >= 0.75
    assert reuse["relearning_cost_after_goal_switch"] <= 0.25
    assert reuse["old_goal_recovery_success"] >= 0.80
    assert reuse["task_specific_policy_gap"] >= 0.25
    assert reuse["baselines"]["TaskSpecificPolicy"]["equivalent"] is False
    assert reuse["baselines"]["RetrainFromScratchPolicy"]["equivalent"] is False


def test_cycle_008_ablation_and_strong_baselines_are_not_equivalent(tmp_path):
    result = run_cycle_008(tmp_path)
    ablation = result["tasks"]["LCC-C8-007"]
    baselines = result["tasks"]["LCC-C8-008"]

    assert ablation["verdict"] == "goal_conditioned_ablation_necessity_passed"
    for ablation_name in [
        "NoGoalVectorPolicy",
        "NoConstraintVectorPolicy",
        "NoEffectModelReusePolicy",
        "TaskLabelOnlyPolicy",
        "GoalLookupOnlyPolicy",
        "NoCounterfactualQueryPolicy",
        "FixedPriorityOnlyPolicy",
    ]:
        assert ablation["ablations"][ablation_name]["equivalent"] is False

    assert baselines["verdict"] == "strong_goal_conditioned_baselines_not_equivalent"
    for baseline_name in [
        "SingleGoalPolicy",
        "TaskLabelPolicy",
        "GoalLookupTablePolicy",
        "NearestNeighborTaskPolicy",
        "FixedConstraintPolicy",
        "StaticSafetyTableBaseline",
        "DominantGoalPolicy",
        "FixedPriorityPolicy",
        "RewardTablePolicy",
        "TaskSpecificPolicy",
    ]:
        assert baselines["baselines"][baseline_name]["equivalent"] is False
    assert baselines["oracle_goal_planner_diagnostic_upper_bound"]["diagnostic_only"] is True
    assert baselines["oracle_goal_planner_diagnostic_upper_bound"]["valid_competitor"] is False


def test_replay_provenance_and_required_cycle_008_artifacts(tmp_path):
    result = run_cycle_008(tmp_path)
    provenance = result["tasks"]["LCC-C8-009"]

    assert provenance["verdict"] == "goal_conditioned_replay_and_provenance_passed"
    assert provenance["behavior_only_replay"]["passed"] is True
    assert provenance["agent_identity_mutation"]["passed"] is True
    assert provenance["forged_self_report_injection"]["passed"] is True
    assert provenance["scenario_label_mutation"]["passed"] is True
    assert provenance["metric_provenance_scan"]["passed"] is True
    assert provenance["hidden_state_leak_scan"]["passed"] is True
    assert provenance["action_label_use_scan"]["passed"] is True
    assert provenance["task_id_leak_scan"]["passed"] is True
    assert provenance["goal_id_leak_scan"]["passed"] is True
    assert provenance["semantic_goal_label_leak_scan"]["passed"] is True
    assert provenance["reward_table_leak_scan"]["passed"] is True
    assert provenance["oracle_plan_leak_scan"]["passed"] is True
    assert provenance["transition_table_leak_scan"]["passed"] is True

    required = [
        "LCC-C8-000/STATUS.md",
        "LCC-C8-000/cycle_007_freeze_manifest.json",
        "LCC-C8-001/goal_conditioned_testbed_report.md",
        "LCC-C8-001/goal_conditioned_config.json",
        "LCC-C8-001/leak_scan_report.md",
        "LCC-C8-002/goal_switch_fixed_effects_report.md",
        "LCC-C8-002/goal_switch_fixed_effects_results.json",
        "LCC-C8-002/traces.jsonl",
        "LCC-C8-002/behavior_only_replay.json",
        "LCC-C8-003/constraint_reweighting_report.md",
        "LCC-C8-003/constraint_reweighting_results.json",
        "LCC-C8-004/novel_goal_composition_report.md",
        "LCC-C8-004/novel_goal_composition_results.json",
        "LCC-C8-005/conflicting_goal_tradeoff_report.md",
        "LCC-C8-005/conflicting_goal_tradeoff_results.json",
        "LCC-C8-006/model_reuse_vs_relearning_report.md",
        "LCC-C8-006/model_reuse_vs_relearning_results.json",
        "LCC-C8-007/cycle_008_ablation_report.md",
        "LCC-C8-007/cycle_008_ablation_results.json",
        "LCC-C8-008/cycle_008_strong_baseline_report.md",
        "LCC-C8-008/cycle_008_baseline_equivalence.json",
        "LCC-C8-009/behavior_only_replay.json",
        "LCC-C8-009/provenance_audit_report.md",
        "LCC-C8-009/identity_mutation_report.md",
        "CYCLE_008_DECISION.md",
        "cycle_008_decision.json",
    ]
    for rel_path in required:
        assert (tmp_path / rel_path).exists(), rel_path

    decision = json.loads((tmp_path / "cycle_008_decision.json").read_text(encoding="utf-8"))
    assert decision["verdict"] == "lcc_contract_strengthened_goal_conditioned_reuse_bounded"
    assert decision["theory_support"] == "not_yet"
    assert decision["general_lcc_agent"] == "not_authorized"
    assert decision["ego_migration"] == "no_go"
    assert decision["autonomous_theory_search"] == "not_authorized"
    assert decision["next_step"] == "human_review_required_before_cycle_009_or_stronger_claim"
    assert all(gate["passed"] for gate in decision["required_gates"].values())
