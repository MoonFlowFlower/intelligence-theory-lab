import json

from theory_lab.lcc_cycle_005_nonstationary_revision import run_cycle_005


def test_cycle_005_survives_nonstationary_revision_contract(tmp_path):
    result = run_cycle_005(tmp_path)

    assert result["cycle_verdict"] == "lcc_contract_strengthened_nonstationary_revision_bounded"
    assert result["stopped_at"] is None
    assert result["stop_conditions_triggered"] == []
    assert result["claim_boundary"] == "bounded nonstationary causal effect revision contract only"


def test_prediction_error_invalidation_and_label_effect_split(tmp_path):
    result = run_cycle_005(tmp_path)
    invalidation = result["tasks"]["LCC-C5-002"]

    assert invalidation["verdict"] == "model_invalidation_passed"
    assert invalidation["prediction_error_spike_detected"] is True
    assert invalidation["confidence_reduction_after_mismatch"] >= 0.80
    assert invalidation["diagnostic_probe_rate_after_mismatch"] >= 0.70
    assert invalidation["unnecessary_probe_rate_in_stable_phase"] <= 0.20
    assert (
        invalidation["post_update_control_success"]
        > invalidation["baselines"]["StaticOldModelPolicy"]["post_update_control_success"]
    )
    assert invalidation["label_permutation_change_rate"] <= 0.05
    assert invalidation["effect_swap_change_rate"] >= 0.80
    assert invalidation["behavior_only_replay"]["passed"] is True


def test_safe_reidentification_context_revision_and_drift_switch(tmp_path):
    result = run_cycle_005(tmp_path)
    safe = result["tasks"]["LCC-C5-003"]
    context_revision = result["tasks"]["LCC-C5-004"]
    drift = result["tasks"]["LCC-C5-005"]

    assert safe["verdict"] == "safe_reidentification_passed"
    assert safe["safe_diagnostic_selection_rate"] >= 0.75
    assert safe["irreversible_trap_avoidance_rate"] >= 0.80
    assert safe["information_gain_after_probe"] >= 0.50
    assert safe["control_success_after_reidentification"] > safe["baselines"]["AlwaysSafePolicy"]["control_success_after_reidentification"]
    assert safe["diagnostic_overuse_after_model_identified"] <= 0.20

    assert context_revision["verdict"] == "context_specific_revision_passed"
    assert context_revision["context_specific_prediction_accuracy"] >= 0.80
    assert context_revision["old_context_recovery_success"] >= 0.80
    assert context_revision["new_context_control_success"] >= 0.80
    assert context_revision["relearning_cost_on_context_return"] <= 0.20
    assert context_revision["catastrophic_forgetting_rate"] <= 0.20
    assert context_revision["baselines"]["GlobalOverwriteModelPolicy"]["equivalent"] is False

    assert drift["verdict"] == "drift_vs_switch_passed"
    assert drift["drift_tracking_error"] <= 0.20
    assert drift["switch_detection_delay"] <= 2
    assert drift["overreaction_to_noise_rate"] <= 0.20
    assert drift["underreaction_to_true_change_rate"] <= 0.20
    assert drift["control_success_during_drift"] >= 0.80
    assert drift["control_success_after_switch"] >= 0.80


def test_reversal_trap_memory_ablation_and_strong_baselines(tmp_path):
    result = run_cycle_005(tmp_path)
    reversal = result["tasks"]["LCC-C5-006"]
    ablation = result["tasks"]["LCC-C5-007"]
    baselines = result["tasks"]["LCC-C5-008"]

    assert reversal["verdict"] == "reversal_trap_memory_passed"
    assert reversal["unsafe_habit_suppression"] >= 0.80
    assert reversal["trap_avoidance_after_reversal"] >= 0.80
    assert reversal["sequence_recovery_after_old_context_return"] >= 0.80
    assert reversal["false_avoidance_rate_when_old_context_safe"] <= 0.20

    assert ablation["verdict"] == "nonstationary_ablation_necessity_passed"
    for ablation_name in [
        "NoPredictionErrorInvalidationPolicy",
        "NoUncertaintyUpdatePolicy",
        "NoDiagnosticProbePolicy",
        "NoContextBeliefPolicy",
        "GlobalOverwriteOnlyPolicy",
        "NoCounterfactualQueryPolicy",
    ]:
        assert ablation["ablations"][ablation_name]["equivalent"] is False

    assert baselines["verdict"] == "strong_nonstationary_baselines_not_equivalent"
    for baseline in [
        "StaticOldModelPolicy",
        "AlwaysRediagnosePolicy",
        "GlobalOverwriteModelPolicy",
        "NearestNeighborTracePolicy",
        "FixedLearningRatePolicy",
        "AlwaysResetPolicy",
        "OldHabitPolicy",
        "ContextualHeuristicBaseline",
    ]:
        assert baselines["baselines"][baseline]["equivalent"] is False
    assert baselines["oracle_change_point_diagnostic_upper_bound"]["diagnostic_only"] is True


def test_replay_provenance_and_required_cycle_005_artifacts(tmp_path):
    result = run_cycle_005(tmp_path)
    provenance = result["tasks"]["LCC-C5-009"]

    assert provenance["verdict"] == "replay_and_provenance_passed"
    assert provenance["behavior_only_replay"]["passed"] is True
    assert provenance["agent_identity_mutation"]["passed"] is True
    assert provenance["forged_self_report_injection"]["passed"] is True
    assert provenance["scenario_label_mutation"]["passed"] is True
    assert provenance["metric_provenance_scan"]["passed"] is True
    assert provenance["hidden_state_leak_scan"]["passed"] is True
    assert provenance["action_label_use_scan"]["passed"] is True
    assert provenance["context_id_leak_scan"]["passed"] is True
    assert provenance["phase_switch_leak_scan"]["passed"] is True
    assert provenance["transition_table_leak_scan"]["passed"] is True
    assert provenance["plan_table_leak_scan"]["passed"] is True

    required = [
        "LCC-C5-000/STATUS.md",
        "LCC-C5-000/cycle_004_freeze_manifest.json",
        "LCC-C5-001/nonstationary_testbed_report.md",
        "LCC-C5-001/nonstationary_testbed_config.json",
        "LCC-C5-001/leak_scan_report.md",
        "LCC-C5-002/model_invalidation_report.md",
        "LCC-C5-002/model_invalidation_results.json",
        "LCC-C5-002/traces.jsonl",
        "LCC-C5-002/behavior_only_replay.json",
        "LCC-C5-003/safe_reidentification_report.md",
        "LCC-C5-003/safe_reidentification_results.json",
        "LCC-C5-004/context_specific_revision_report.md",
        "LCC-C5-004/context_specific_revision_results.json",
        "LCC-C5-005/drift_vs_switch_report.md",
        "LCC-C5-005/drift_vs_switch_results.json",
        "LCC-C5-006/reversal_trap_memory_report.md",
        "LCC-C5-006/reversal_trap_memory_results.json",
        "LCC-C5-007/cycle_005_ablation_report.md",
        "LCC-C5-007/cycle_005_ablation_results.json",
        "LCC-C5-008/cycle_005_strong_baseline_report.md",
        "LCC-C5-008/cycle_005_baseline_equivalence.json",
        "LCC-C5-009/behavior_only_replay.json",
        "LCC-C5-009/provenance_audit_report.md",
        "LCC-C5-009/identity_mutation_report.md",
        "CYCLE_005_DECISION.md",
        "cycle_005_decision.json",
    ]
    for rel_path in required:
        assert (tmp_path / rel_path).exists(), rel_path

    decision = json.loads((tmp_path / "cycle_005_decision.json").read_text(encoding="utf-8"))
    assert decision["verdict"] == "lcc_contract_strengthened_nonstationary_revision_bounded"
    assert decision["theory_support"] == "not_yet"
    assert decision["general_lcc_agent"] == "not_authorized"
    assert decision["ego_migration"] == "no_go"
    assert all(gate["passed"] for gate in decision["required_gates"].values())
