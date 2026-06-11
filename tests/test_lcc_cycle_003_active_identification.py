import json

from theory_lab.lcc_cycle_003_active_id import run_cycle_003


def test_cycle_003_survives_active_causal_identification_redteam(tmp_path):
    result = run_cycle_003(tmp_path)

    assert result["cycle_verdict"] == "lcc_contract_strengthened_active_identification_bounded"
    assert result["stopped_at"] is None
    assert result["stop_conditions_triggered"] == []
    assert result["claim_boundary"] == "bounded active causal identification contract only"


def test_active_diagnostic_intervention_split(tmp_path):
    result = run_cycle_003(tmp_path)
    active = result["tasks"]["LCC-C3-002"]

    assert active["verdict"] == "active_diagnostic_intervention_passed"
    assert active["diagnostic_action_rate_when_ambiguous"] >= 0.80
    assert active["diagnostic_action_rate_when_certain"] <= 0.20
    assert active["posterior_uncertainty_reduction"] > active["baselines"]["PassiveLearnerPolicy"]["posterior_uncertainty_reduction"]
    assert active["post_diagnostic_control_success"] > active["baselines"]["PassiveLearnerPolicy"]["control_success"]
    assert active["label_permutation_change_rate"] <= 0.05
    assert active["effect_swap_change_rate"] >= 0.80
    assert active["behavior_only_replay"]["passed"] is True


def test_tradeoff_correlation_and_transfer_gates(tmp_path):
    result = run_cycle_003(tmp_path)
    tradeoff = result["tasks"]["LCC-C3-003"]
    confounded = result["tasks"]["LCC-C3-004"]
    transfer = result["tasks"]["LCC-C3-005"]

    assert tradeoff["verdict"] == "exploration_control_tradeoff_passed"
    assert tradeoff["ambiguous_high_stakes"]["diagnostic_selected"] is True
    assert tradeoff["ambiguous_low_stakes"]["diagnostic_selected"] is False
    assert tradeoff["certain_high_stakes"]["diagnostic_selected"] is False
    assert tradeoff["misleading_reward_context"]["reward_chasing_equivalent"] is False
    assert tradeoff["uncertainty_in_control_loop"] is True

    assert confounded["verdict"] == "confounded_passive_correlation_passed"
    assert confounded["candidate_tests_own_intervention_rate"] >= 0.80
    assert confounded["policy_follows_intervention_effect_rate"] >= 0.80
    assert confounded["passive_correlation_policy_equivalent"] is False

    assert transfer["verdict"] == "post_identification_transfer_passed"
    assert transfer["heldout_transfer_success"] >= 0.85
    assert transfer["label_permutation_change_rate"] <= 0.05
    assert transfer["effect_swap_change_rate"] >= 0.80
    assert transfer["posterior_reuse_without_rediagnosis"] >= 0.80


def test_ablation_and_strong_baselines_are_not_equivalent(tmp_path):
    result = run_cycle_003(tmp_path)
    ablation = result["tasks"]["LCC-C3-006"]
    baselines = result["tasks"]["LCC-C3-007"]

    assert ablation["verdict"] == "ablation_necessity_passed"
    for ablation_name in [
        "NoUncertaintyPolicy",
        "NoInterventionHistoryPolicy",
        "NoPosteriorUpdatePolicy",
        "NoCounterfactualQueryPolicy",
        "PassiveOnlyTrainingPolicy",
    ]:
        assert ablation["ablations"][ablation_name]["equivalent"] is False

    assert baselines["verdict"] == "strong_baselines_not_equivalent"
    for baseline in [
        "PassiveLearnerPolicy",
        "GreedyImmediateValuePolicy",
        "RandomDiagnosticPolicy",
        "NearestNeighborTracePolicy",
        "ContextualHeuristicBaseline",
        "StaticDiagnosticTableBaseline",
    ]:
        assert baselines["baselines"][baseline]["equivalent"] is False
    assert baselines["oracle_diagnostic_upper_bound"]["diagnostic_only"] is True


def test_replay_provenance_and_required_artifacts(tmp_path):
    result = run_cycle_003(tmp_path)
    provenance = result["tasks"]["LCC-C3-008"]

    assert provenance["verdict"] == "replay_and_provenance_passed"
    assert provenance["behavior_only_replay"]["passed"] is True
    assert provenance["agent_identity_mutation"]["passed"] is True
    assert provenance["forged_self_report_injection"]["passed"] is True
    assert provenance["scenario_label_mutation"]["passed"] is True
    assert provenance["metric_provenance_scan"]["passed"] is True
    assert provenance["hidden_state_leak_scan"]["passed"] is True
    assert provenance["action_label_use_scan"]["passed"] is True
    assert provenance["hypothesis_id_leak_scan"]["passed"] is True

    required = [
        "LCC-C3-000/STATUS.md",
        "LCC-C3-000/cycle_002_freeze_manifest.json",
        "LCC-C3-001/ambiguous_hypothesis_testbed_report.md",
        "LCC-C3-001/ambiguous_hypothesis_config.json",
        "LCC-C3-001/leak_scan_report.md",
        "LCC-C3-002/active_diagnostic_intervention_report.md",
        "LCC-C3-002/active_diagnostic_intervention_results.json",
        "LCC-C3-002/traces.jsonl",
        "LCC-C3-002/behavior_only_replay.json",
        "LCC-C3-003/exploration_control_tradeoff_report.md",
        "LCC-C3-003/exploration_control_tradeoff_results.json",
        "LCC-C3-004/confounded_passive_correlation_report.md",
        "LCC-C3-004/confounded_passive_correlation_results.json",
        "LCC-C3-005/post_identification_transfer_report.md",
        "LCC-C3-005/post_identification_transfer_results.json",
        "LCC-C3-006/cycle_003_ablation_report.md",
        "LCC-C3-006/cycle_003_ablation_results.json",
        "LCC-C3-007/cycle_003_strong_baseline_report.md",
        "LCC-C3-007/cycle_003_baseline_equivalence.json",
        "LCC-C3-008/behavior_only_replay.json",
        "LCC-C3-008/provenance_audit_report.md",
        "LCC-C3-008/identity_mutation_report.md",
        "CYCLE_003_DECISION.md",
        "cycle_003_decision.json",
    ]
    for rel_path in required:
        assert (tmp_path / rel_path).exists(), rel_path

    decision = json.loads((tmp_path / "cycle_003_decision.json").read_text(encoding="utf-8"))
    assert decision["verdict"] == "lcc_contract_strengthened_active_identification_bounded"
    assert decision["theory_support"] == "not_yet"
    assert all(gate["passed"] for gate in decision["required_gates"].values())
