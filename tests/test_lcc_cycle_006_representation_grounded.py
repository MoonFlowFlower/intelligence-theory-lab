import json

from theory_lab.lcc_cycle_006_representation_grounded import run_cycle_006


def test_cycle_006_survives_representation_grounded_contract(tmp_path):
    result = run_cycle_006(tmp_path)

    assert result["cycle_verdict"] == "lcc_contract_strengthened_representation_grounded_bounded"
    assert result["stopped_at"] is None
    assert result["stop_conditions_triggered"] == []
    assert result["claim_boundary"] == "bounded representation-grounded counterfactual controllability contract only"


def test_nuisance_invariance_causal_sensitivity_and_replay(tmp_path):
    result = run_cycle_006(tmp_path)
    nuisance = result["tasks"]["LCC-C6-002"]

    assert nuisance["verdict"] == "nuisance_invariance_causal_sensitivity_passed"
    assert nuisance["nuisance_swap_behavior_change_rate"] <= 0.10
    assert nuisance["causal_swap_behavior_change_rate"] >= 0.80
    assert nuisance["heldout_spurious_token_failure_rate"] <= 0.20
    assert nuisance["label_permutation_change_rate"] <= 0.05
    assert nuisance["effect_swap_change_rate"] >= 0.80
    assert nuisance["behavior_only_replay"]["passed"] is True
    assert nuisance["baselines"]["RawNearestNeighborPolicy"]["equivalent"] is False
    assert nuisance["baselines"]["StaticVisualTokenPolicy"]["equivalent"] is False


def test_alias_disambiguation_representation_perturbation_and_transfer(tmp_path):
    result = run_cycle_006(tmp_path)
    aliasing = result["tasks"]["LCC-C6-003"]
    perturbation = result["tasks"]["LCC-C6-004"]
    transfer = result["tasks"]["LCC-C6-005"]

    assert aliasing["verdict"] == "aliased_observation_disambiguation_passed"
    assert aliasing["history_dependent_disambiguation_success"] >= 0.80
    assert aliasing["diagnostic_disambiguation_success"] >= 0.80
    assert aliasing["observation_only_baseline_gap"] >= 0.25
    assert aliasing["label_permutation_change_rate"] <= 0.05
    assert aliasing["effect_swap_change_rate"] >= 0.80
    assert aliasing["baselines"]["ObservationOnlyPolicy"]["equivalent"] is False
    assert aliasing["baselines"]["HistoryBlindPolicy"]["equivalent"] is False

    assert perturbation["verdict"] == "representation_perturbation_passed"
    assert perturbation["causal_latent_perturbation_action_change_rate"] >= 0.70
    assert perturbation["nuisance_latent_perturbation_action_change_rate"] <= 0.20
    assert perturbation["causal_embedding_swap_rank_flip_rate"] >= 0.70
    assert perturbation["nuisance_embedding_swap_rank_flip_rate"] <= 0.20
    assert perturbation["uncertainty_sensitive_diagnostic_rate"] >= 0.70

    assert transfer["verdict"] == "cross_nuisance_transfer_passed"
    assert transfer["cross_renderer_success_rate"] >= 0.80
    assert transfer["raw_nearest_neighbor_gap"] >= 0.25
    assert transfer["visual_token_baseline_gap"] >= 0.25
    assert transfer["label_permutation_change_rate"] <= 0.05
    assert transfer["effect_swap_change_rate"] >= 0.80


def test_ablation_and_strong_representation_baselines_are_not_equivalent(tmp_path):
    result = run_cycle_006(tmp_path)
    ablation = result["tasks"]["LCC-C6-006"]
    baselines = result["tasks"]["LCC-C6-007"]

    assert ablation["verdict"] == "representation_ablation_necessity_passed"
    for ablation_name in [
        "NoLearnedEncoderPolicy",
        "NoHistoryPolicy",
        "NoInterventionHistoryPolicy",
        "NoCausalRepresentationPolicy",
        "NuisanceOnlyRepresentationPolicy",
        "RawObservationOnlyPolicy",
        "NoCounterfactualQueryPolicy",
    ]:
        assert ablation["ablations"][ablation_name]["equivalent"] is False

    assert baselines["verdict"] == "strong_representation_baselines_not_equivalent"
    for baseline in [
        "RawNearestNeighborPolicy",
        "StaticVisualTokenPolicy",
        "NuisanceHeuristicPolicy",
        "ObservationOnlyPolicy",
        "HistoryBlindPolicy",
        "RendererSpecificPolicy",
        "ContextualHeuristicBaseline",
    ]:
        assert baselines["baselines"][baseline]["equivalent"] is False
    assert baselines["causal_oracle_diagnostic_upper_bound"]["diagnostic_only"] is True


def test_replay_provenance_and_required_cycle_006_artifacts(tmp_path):
    result = run_cycle_006(tmp_path)
    provenance = result["tasks"]["LCC-C6-008"]

    assert provenance["verdict"] == "replay_and_provenance_passed"
    assert provenance["behavior_only_replay"]["passed"] is True
    assert provenance["agent_identity_mutation"]["passed"] is True
    assert provenance["forged_self_report_injection"]["passed"] is True
    assert provenance["scenario_label_mutation"]["passed"] is True
    assert provenance["metric_provenance_scan"]["passed"] is True
    assert provenance["hidden_state_leak_scan"]["passed"] is True
    assert provenance["action_label_use_scan"]["passed"] is True
    assert provenance["causal_latent_leak_scan"]["passed"] is True
    assert provenance["nuisance_latent_leak_scan"]["passed"] is True
    assert provenance["feature_mask_leak_scan"]["passed"] is True
    assert provenance["renderer_id_shortcut_scan"]["passed"] is True
    assert provenance["transition_table_leak_scan"]["passed"] is True

    required = [
        "LCC-C6-000/STATUS.md",
        "LCC-C6-000/cycle_005_freeze_manifest.json",
        "LCC-C6-001/raw_observation_testbed_report.md",
        "LCC-C6-001/raw_observation_testbed_config.json",
        "LCC-C6-001/leak_scan_report.md",
        "LCC-C6-002/nuisance_vs_causal_report.md",
        "LCC-C6-002/nuisance_vs_causal_results.json",
        "LCC-C6-002/traces.jsonl",
        "LCC-C6-002/behavior_only_replay.json",
        "LCC-C6-003/aliased_observation_report.md",
        "LCC-C6-003/aliased_observation_results.json",
        "LCC-C6-004/representation_perturbation_report.md",
        "LCC-C6-004/representation_perturbation_results.json",
        "LCC-C6-005/cross_nuisance_transfer_report.md",
        "LCC-C6-005/cross_nuisance_transfer_results.json",
        "LCC-C6-006/cycle_006_ablation_report.md",
        "LCC-C6-006/cycle_006_ablation_results.json",
        "LCC-C6-007/cycle_006_strong_baseline_report.md",
        "LCC-C6-007/cycle_006_baseline_equivalence.json",
        "LCC-C6-008/behavior_only_replay.json",
        "LCC-C6-008/provenance_audit_report.md",
        "LCC-C6-008/identity_mutation_report.md",
        "CYCLE_006_DECISION.md",
        "cycle_006_decision.json",
    ]
    for rel_path in required:
        assert (tmp_path / rel_path).exists(), rel_path

    decision = json.loads((tmp_path / "cycle_006_decision.json").read_text(encoding="utf-8"))
    assert decision["verdict"] == "lcc_contract_strengthened_representation_grounded_bounded"
    assert decision["theory_support"] == "not_yet"
    assert decision["general_lcc_agent"] == "not_authorized"
    assert decision["ego_migration"] == "no_go"
    assert all(gate["passed"] for gate in decision["required_gates"].values())
