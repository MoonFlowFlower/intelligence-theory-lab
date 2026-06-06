import json

from theory_lab.lcc_cycle_004_sequential_control import run_cycle_004


def test_cycle_004_survives_sequential_control_contract(tmp_path):
    result = run_cycle_004(tmp_path)

    assert result["cycle_verdict"] == "lcc_contract_strengthened_sequential_control_bounded"
    assert result["stopped_at"] is None
    assert result["stop_conditions_triggered"] == []
    assert result["claim_boundary"] == "bounded sequential closed-loop counterfactual control contract only"


def test_multi_step_composition_and_effect_label_split(tmp_path):
    result = run_cycle_004(tmp_path)
    composition = result["tasks"]["LCC-C4-002"]

    assert composition["verdict"] == "multi_step_composition_passed"
    assert composition["multi_step_success_rate"] >= 0.80
    assert composition["greedy_trap_avoidance_rate"] >= 0.80
    assert (
        composition["novel_sequence_success_rate"]
        > composition["baselines"]["OneStepGreedyPolicy"]["novel_sequence_success_rate"]
    )
    assert composition["label_permutation_change_rate"] <= 0.05
    assert composition["effect_swap_change_rate"] >= 0.80
    assert composition["behavior_only_replay"]["passed"] is True


def test_closed_loop_replanning_trap_avoidance_and_transfer(tmp_path):
    result = run_cycle_004(tmp_path)
    replanning = result["tasks"]["LCC-C4-003"]
    trap = result["tasks"]["LCC-C4-004"]
    transfer = result["tasks"]["LCC-C4-005"]

    assert replanning["verdict"] == "closed_loop_replanning_passed"
    assert replanning["replan_after_deviation_rate"] >= 0.80
    assert replanning["post_replan_success_rate"] > replanning["baselines"]["OpenLoopSequencePolicy"]["post_replan_success_rate"]
    assert replanning["post_replan_success_rate"] > replanning["baselines"]["OneStepReactivePolicy"]["post_replan_success_rate"]
    assert replanning["label_permutation_change_rate"] <= 0.05
    assert replanning["effect_swap_change_rate"] >= 0.80

    assert trap["verdict"] == "irreversible_trap_option_preservation_passed"
    assert trap["irreversible_trap_avoidance"] >= 0.80
    assert trap["option_preservation_under_uncertainty"] >= 0.80
    assert trap["diagnostic_use_when_trap_uncertain"] >= 0.80
    assert trap["no_diagnostic_overuse_when_trap_known"] >= 0.80

    assert transfer["verdict"] == "novel_sequence_transfer_passed"
    assert transfer["heldout_sequence_success_rate"] >= 0.80
    assert transfer["sequence_lookup_gap"] > 0.20
    assert transfer["label_permutation_change_rate"] <= 0.05
    assert transfer["effect_swap_change_rate"] >= 0.80


def test_ablation_and_strong_sequence_baselines_are_not_equivalent(tmp_path):
    result = run_cycle_004(tmp_path)
    ablation = result["tasks"]["LCC-C4-006"]
    baselines = result["tasks"]["LCC-C4-007"]

    assert ablation["verdict"] == "sequential_ablation_necessity_passed"
    for ablation_name in [
        "NoRolloutCompositionPolicy",
        "NoReplanningPolicy",
        "NoUncertaintyPolicy",
        "NoInterventionHistoryPolicy",
        "NoCounterfactualQueryPolicy",
        "OpenLoopOnlyPolicy",
    ]:
        assert ablation["ablations"][ablation_name]["equivalent"] is False

    assert baselines["verdict"] == "strong_sequence_baselines_not_equivalent"
    for baseline in [
        "OneStepGreedyPolicy",
        "OpenLoopSequencePolicy",
        "SequenceLookupTablePolicy",
        "NearestNeighborSequencePolicy",
        "ContextualHeuristicBaseline",
        "StaticTrapAvoidanceTableBaseline",
    ]:
        assert baselines["baselines"][baseline]["equivalent"] is False
    assert baselines["oracle_planner_diagnostic_upper_bound"]["diagnostic_only"] is True


def test_replay_provenance_and_required_cycle_004_artifacts(tmp_path):
    result = run_cycle_004(tmp_path)
    provenance = result["tasks"]["LCC-C4-008"]

    assert provenance["verdict"] == "replay_and_provenance_passed"
    assert provenance["behavior_only_replay"]["passed"] is True
    assert provenance["agent_identity_mutation"]["passed"] is True
    assert provenance["forged_self_report_injection"]["passed"] is True
    assert provenance["scenario_label_mutation"]["passed"] is True
    assert provenance["metric_provenance_scan"]["passed"] is True
    assert provenance["hidden_state_leak_scan"]["passed"] is True
    assert provenance["action_label_use_scan"]["passed"] is True
    assert provenance["transition_table_leak_scan"]["passed"] is True
    assert provenance["plan_table_leak_scan"]["passed"] is True

    required = [
        "LCC-C4-000/STATUS.md",
        "LCC-C4-000/cycle_003_freeze_manifest.json",
        "LCC-C4-001/sequential_testbed_report.md",
        "LCC-C4-001/sequential_testbed_config.json",
        "LCC-C4-001/leak_scan_report.md",
        "LCC-C4-002/multi_step_composition_report.md",
        "LCC-C4-002/multi_step_composition_results.json",
        "LCC-C4-002/traces.jsonl",
        "LCC-C4-002/behavior_only_replay.json",
        "LCC-C4-003/closed_loop_replanning_report.md",
        "LCC-C4-003/closed_loop_replanning_results.json",
        "LCC-C4-004/irreversible_trap_report.md",
        "LCC-C4-004/irreversible_trap_results.json",
        "LCC-C4-005/novel_sequence_transfer_report.md",
        "LCC-C4-005/novel_sequence_transfer_results.json",
        "LCC-C4-006/cycle_004_ablation_report.md",
        "LCC-C4-006/cycle_004_ablation_results.json",
        "LCC-C4-007/cycle_004_strong_baseline_report.md",
        "LCC-C4-007/cycle_004_baseline_equivalence.json",
        "LCC-C4-008/behavior_only_replay.json",
        "LCC-C4-008/provenance_audit_report.md",
        "LCC-C4-008/identity_mutation_report.md",
        "CYCLE_004_DECISION.md",
        "cycle_004_decision.json",
    ]
    for rel_path in required:
        assert (tmp_path / rel_path).exists(), rel_path

    decision = json.loads((tmp_path / "cycle_004_decision.json").read_text(encoding="utf-8"))
    assert decision["verdict"] == "lcc_contract_strengthened_sequential_control_bounded"
    assert decision["theory_support"] == "not_yet"
    assert decision["general_lcc_agent"] == "not_authorized"
    assert decision["ego_migration"] == "no_go"
    assert all(gate["passed"] for gate in decision["required_gates"].values())
