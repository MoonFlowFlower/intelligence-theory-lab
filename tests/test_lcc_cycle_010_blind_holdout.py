import json

from theory_lab.lcc_cycle_010_blind_holdout import run_cycle_010


def test_cycle_010_survives_blind_holdout_contract(tmp_path):
    result = run_cycle_010(tmp_path)

    assert result["cycle_verdict"] == "lcc_contract_strengthened_blind_holdout_bounded"
    assert result["stopped_at"] is None
    assert result["stop_conditions_triggered"] == []
    assert result["claim_boundary"] == "bounded blind holdout independent replication contract only"


def test_candidate_freeze_dsl_and_blind_holdout_generation(tmp_path):
    result = run_cycle_010(tmp_path)
    freeze = result["tasks"]["LCC-C10-001"]
    dsl = result["tasks"]["LCC-C10-002"]

    assert freeze["verdict"] == "candidate_freeze_scope_lock_passed"
    assert freeze["candidate_freezable"] is True
    assert freeze["static_scan"]["candidate_control_forbidden_hits"] == []
    assert freeze["static_scan"]["selector_dispatch_branch_count"] == 0
    assert freeze["freeze_manifest"]["candidate_hashes"]
    assert freeze["freeze_manifest"]["scope_lock_active"] is True

    assert dsl["verdict"] == "blind_holdout_generated_after_freeze"
    assert dsl["generated_after_freeze"] is True
    assert dsl["instance_count"] >= 200
    assert dsl["template_count"] >= 8
    assert dsl["hybrid_template_count"] >= 4
    assert dsl["fresh_seed_count"] >= 8
    assert dsl["dsl_exposes_task_family_to_candidate"] is False
    assert dsl["generator_uses_semantic_labels"] is False
    assert dsl["holdout_too_close_to_prior_cycles"] is False


def test_blind_holdout_baselines_independent_scoring_and_replication(tmp_path):
    result = run_cycle_010(tmp_path)
    holdout = result["tasks"]["LCC-C10-003"]
    baselines = result["tasks"]["LCC-C10-004"]
    scoring = result["tasks"]["LCC-C10-005"]
    replication = result["tasks"]["LCC-C10-006"]

    assert holdout["verdict"] == "blind_holdout_evaluation_passed"
    assert holdout["overall_success_rate"] >= 0.75
    assert holdout["min_template_success_rate"] >= 0.55
    assert holdout["label_permutation_change_rate"] <= 0.05
    assert holdout["effect_swap_change_rate"] >= 0.75
    assert holdout["behavior_only_replay"]["passed"] is True
    assert holdout["behavior_only_replay_match"] is True
    assert holdout["metadata_mutation_action_change_rate"] <= 0.01

    assert baselines["verdict"] == "generic_baseline_tournament_passed"
    assert baselines["baseline_equivalence_rate"] == 0.0
    assert baselines["candidate_beats_non_oracle_count"] >= 7
    assert baselines["model_based_mpc_gap"] >= -0.05
    assert baselines["empowerment_gap"] >= -0.05
    for baseline_name, payload in baselines["candidate_vs_each_baseline_win_rate"].items():
        if baseline_name != "OracleUnifiedDiagnosticUpperBound":
            assert payload["equivalent"] is False, baseline_name

    assert scoring["verdict"] == "independent_scoring_replication_passed"
    assert scoring["independent_behavior_replay_match"] is True
    assert scoring["primary_vs_independent_diff"]["max_abs_diff"] <= 0.000001
    assert scoring["identity_mutation_changes_metrics"] is False
    assert scoring["forged_self_report_fields_ignored"] is True

    assert replication["verdict"] == "statistical_robustness_passed"
    assert replication["initial_success_rate"] >= 0.75
    assert replication["replication_success_rate"] >= 0.70
    assert abs(replication["initial_success_rate"] - replication["replication_success_rate"]) <= 0.10
    assert replication["min_replication_template_success_rate"] >= 0.50
    assert replication["freeze_integrity"]["candidate_hash_unchanged"] is True


def test_blind_holdout_ablation_negative_controls_and_artifacts(tmp_path):
    result = run_cycle_010(tmp_path)
    ablation = result["tasks"]["LCC-C10-007"]
    negative = result["tasks"]["LCC-C10-008"]

    assert ablation["verdict"] == "blind_holdout_ablation_necessity_passed"
    for ablation_name in [
        "NoEffectModelPolicy",
        "NoInterventionUpdatePolicy",
        "NoCounterfactualQueryPolicy",
        "NoUncertaintyPolicy",
        "NoRepresentationLearningPolicy",
        "NoGoalConditioningPolicy",
        "NoRelationalBindingPolicy",
        "NoReplanningPolicy",
        "OpenLoopOnlyPolicy",
    ]:
        assert ablation["ablations"][ablation_name]["equivalent"] is False

    assert negative["verdict"] == "negative_control_trap_suite_passed"
    assert negative["hallucinated_effect_rate"] == 0.0
    assert negative["false_confidence_rate"] <= 0.05
    assert negative["endless_diagnostic_loop_rate"] == 0.0
    assert negative["impossible_goal_overclaim_rate"] == 0.0

    required = [
        "LCC-C10-000/STATUS.md",
        "LCC-C10-000/cycle_009_freeze_manifest.json",
        "LCC-C10-001/candidate_freeze_manifest.json",
        "LCC-C10-001/scope_lock_report.md",
        "LCC-C10-002/contract_dsl_spec.md",
        "LCC-C10-002/blind_holdout_generator_report.md",
        "LCC-C10-002/blind_holdout_manifest.json",
        "LCC-C10-003/blind_holdout_evaluation_report.md",
        "LCC-C10-003/blind_holdout_results.json",
        "LCC-C10-003/traces.jsonl",
        "LCC-C10-003/behavior_only_replay.json",
        "LCC-C10-004/generic_baseline_tournament_report.md",
        "LCC-C10-004/generic_baseline_tournament_results.json",
        "LCC-C10-005/independent_scoring_report.md",
        "LCC-C10-005/independent_metrics.json",
        "LCC-C10-005/primary_vs_independent_diff.json",
        "LCC-C10-006/statistical_robustness_report.md",
        "LCC-C10-006/replication_results.json",
        "LCC-C10-006/freeze_integrity_report.md",
        "LCC-C10-007/blind_holdout_ablation_report.md",
        "LCC-C10-007/blind_holdout_ablation_results.json",
        "LCC-C10-008/negative_control_report.md",
        "LCC-C10-008/negative_control_results.json",
        "CYCLE_010_DECISION.md",
        "cycle_010_decision.json",
    ]
    for rel_path in required:
        assert (tmp_path / rel_path).exists(), rel_path

    decision = json.loads((tmp_path / "cycle_010_decision.json").read_text(encoding="utf-8"))
    assert decision["verdict"] == "lcc_contract_strengthened_blind_holdout_bounded"
    assert decision["theory_support"] == "not_yet"
    assert decision["general_lcc_agent"] == "not_authorized"
    assert decision["ego_migration"] == "no_go"
    assert decision["autonomous_theory_search"] == "not_authorized"
    assert decision["next_step"] == "human_review_required_before_cycle_011_or_stronger_claim"
    assert all(gate["passed"] for gate in decision["required_gates"].values())
