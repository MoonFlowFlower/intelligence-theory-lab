import json

from theory_lab.lcc_cycle_002_experiential import run_cycle_002


def test_cycle_002_survives_experiential_counterfactual_redteam(tmp_path):
    result = run_cycle_002(tmp_path)

    assert result["cycle_verdict"] == "lcc_contract_strengthened_experiential_bounded"
    assert result["stopped_at"] is None
    assert result["stop_conditions_triggered"] == []
    assert result["claim_boundary"] == "bounded experiential counterfactual contract only"


def test_candidate_uses_intervention_over_passive_correlation(tmp_path):
    result = run_cycle_002(tmp_path)
    split = result["tasks"]["LCC-C2-002"]

    assert split["verdict"] == "intervention_split_passed"
    assert split["candidate"]["intervention_alignment_rate"] >= 0.90
    assert split["candidate"]["passive_correlation_alignment_rate"] <= 0.20
    assert split["candidate"]["label_permutation_change_rate"] <= 0.05
    assert split["candidate"]["effect_swap_change_rate"] >= 0.80
    assert split["behavior_only_replay"]["passed"] is True
    assert split["baselines"]["PassiveCorrelationPolicy"]["equivalent"] is False
    assert split["baselines"]["NearestNeighborTracePolicy"]["equivalent"] is False


def test_delayed_stochastic_and_state_dependent_gates_pass(tmp_path):
    result = run_cycle_002(tmp_path)
    delayed = result["tasks"]["LCC-C2-003"]
    stochastic = result["tasks"]["LCC-C2-004"]
    state_dep = result["tasks"]["LCC-C2-005"]

    assert delayed["verdict"] == "delayed_effect_learning_passed"
    assert delayed["delay_lengths"] == [2, 3, 5]
    assert delayed["effect_swap_change_rate"] >= 0.80
    assert delayed["label_permutation_change_rate"] <= 0.05

    assert stochastic["verdict"] == "stochastic_controllability_passed"
    assert stochastic["reliable_effect_preference_when_viability_at_risk"] >= 0.90
    assert stochastic["uncertainty_sensitive_action_distribution"] >= 0.80
    assert stochastic["mean_only_policy_equivalent"] is False

    assert state_dep["verdict"] == "state_dependent_generalization_passed"
    assert state_dep["heldout_context_match_rate"] >= 0.85
    assert state_dep["same_label_different_effect_divergence"] >= 0.80
    assert state_dep["counterfactual_context_perturbation_change_rate"] >= 0.80


def test_strong_baselines_and_provenance_do_not_match(tmp_path):
    result = run_cycle_002(tmp_path)
    baselines = result["tasks"]["LCC-C2-006"]
    provenance = result["tasks"]["LCC-C2-007"]

    assert baselines["verdict"] == "strong_baselines_not_equivalent"
    for baseline in [
        "ActionLabelHeuristicBaseline",
        "StaticSafetyTableBaseline",
        "ContextualHeuristicBaseline",
        "NearestNeighborTracePolicy",
        "PassiveCorrelationPolicy",
        "GlobalActionEffectPolicy",
    ]:
        assert baselines["baselines"][baseline]["equivalent"] is False
    assert baselines["effect_table_policy"]["diagnostic_only"] is True

    assert provenance["verdict"] == "replay_and_provenance_passed"
    assert provenance["behavior_only_replay"]["passed"] is True
    assert provenance["agent_identity_mutation"]["passed"] is True
    assert provenance["forged_self_report_injection"]["passed"] is True
    assert provenance["scenario_label_mutation"]["passed"] is True
    assert provenance["metric_provenance_scan"]["passed"] is True
    assert provenance["hidden_state_leak_scan"]["passed"] is True


def test_required_cycle_002_artifacts_exist(tmp_path):
    run_cycle_002(tmp_path)
    required = [
        "LCC-C2-000/STATUS.md",
        "LCC-C2-000/cycle_001_freeze_manifest.json",
        "LCC-C2-001/experiential_testbed_report.md",
        "LCC-C2-001/experiential_testbed_config.json",
        "LCC-C2-001/leak_scan_report.md",
        "LCC-C2-002/passive_vs_intervention_report.md",
        "LCC-C2-002/passive_vs_intervention_results.json",
        "LCC-C2-003/delayed_effect_report.md",
        "LCC-C2-003/delayed_effect_results.json",
        "LCC-C2-004/stochastic_controllability_report.md",
        "LCC-C2-004/stochastic_controllability_results.json",
        "LCC-C2-005/state_dependent_effect_report.md",
        "LCC-C2-005/state_dependent_effect_results.json",
        "LCC-C2-006/cycle_002_strong_baseline_report.md",
        "LCC-C2-006/cycle_002_baseline_equivalence.json",
        "LCC-C2-007/behavior_only_replay.json",
        "LCC-C2-007/provenance_audit_report.md",
        "LCC-C2-007/identity_mutation_report.md",
        "CYCLE_002_DECISION.md",
        "cycle_002_decision.json",
    ]

    for rel_path in required:
        assert (tmp_path / rel_path).exists(), rel_path

    decision = json.loads((tmp_path / "cycle_002_decision.json").read_text(encoding="utf-8"))
    assert decision["verdict"] == "lcc_contract_strengthened_experiential_bounded"
    assert all(gate["passed"] for gate in decision["required_gates"].values())
    assert decision["theory_support"] == "not_yet"
