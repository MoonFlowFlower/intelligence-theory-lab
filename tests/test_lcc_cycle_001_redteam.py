import json

from theory_lab.lcc_cycle_001_redteam import run_cycle_001


def test_cycle_001_strengthens_bounded_contract(tmp_path):
    result = run_cycle_001(tmp_path)

    assert result["cycle_verdict"] == "lcc_contract_strengthened_bounded"
    assert result["stopped_at"] is None
    assert result["stop_conditions_triggered"] == []
    assert result["claim_boundary"] == "bounded contract redteam only"


def test_scaled_label_effect_decoupling_passes(tmp_path):
    result = run_cycle_001(tmp_path)
    scale = result["tasks"]["LCC-RT-001"]

    assert scale["verdict"] == "scale_label_effect_passed"
    assert scale["action_counts"] == [3, 5, 8]
    assert all(count >= 50 for count in scale["state_counts"].values())
    assert scale["overall"]["label_permutation_change_rate"] <= 0.05
    assert scale["overall"]["effect_swap_change_rate"] >= 0.80
    assert scale["behavior_only_replay"]["passed"] is True


def test_learned_model_does_not_require_explicit_table(tmp_path):
    result = run_cycle_001(tmp_path)
    learned = result["tasks"]["LCC-RT-002"]

    assert learned["verdict"] == "learned_effect_model_passed"
    assert learned["learned_policy"]["label_permutation_change_rate"] <= 0.05
    assert learned["learned_policy"]["effect_swap_change_rate"] >= 0.80
    assert learned["learned_policy"]["heldout_best_action_match_rate"] >= 0.80
    assert learned["effect_table_policy"]["diagnostic_only"] is True


def test_stronger_baselines_are_not_equivalent(tmp_path):
    result = run_cycle_001(tmp_path)
    baselines = result["tasks"]["LCC-RT-003"]

    assert baselines["verdict"] == "strong_baselines_not_equivalent"
    for baseline in [
        "ActionLabelHeuristicBaseline",
        "StaticSafetyTableBaseline",
        "ContextualHeuristicBaseline",
        "NearestNeighborTracePolicy",
    ]:
        assert baselines["baselines"][baseline]["equivalent"] is False
    assert baselines["effect_table_policy"]["diagnostic_only"] is True


def test_counterfactual_model_perturbation_changes_distribution(tmp_path):
    result = run_cycle_001(tmp_path)
    perturb = result["tasks"]["LCC-RT-004"]

    assert perturb["verdict"] == "model_perturbation_passed"
    assert perturb["action_distribution_change_rate"] >= 0.80
    assert perturb["rank_flip_rate"] >= 0.80
    assert perturb["label_dependence_detected"] is False


def test_heldout_mechanism_world_passes(tmp_path):
    result = run_cycle_001(tmp_path)
    heldout = result["tasks"]["LCC-RT-005"]

    assert heldout["verdict"] == "heldout_mechanism_passed"
    assert heldout["world"] == "latent_actuator_world"
    assert heldout["label_permutation_change_rate"] <= 0.05
    assert heldout["effect_swap_change_rate"] >= 0.80
    assert heldout["behavior_only_replay"]["passed"] is True


def test_required_artifacts_exist(tmp_path):
    run_cycle_001(tmp_path)
    required = [
        "LCC-RT-000/STATUS.md",
        "LCC-RT-000/cycle_000_freeze_manifest.json",
        "LCC-RT-001/label_effect_scale_report.md",
        "LCC-RT-001/label_effect_scale_results.json",
        "LCC-RT-001/traces.jsonl",
        "LCC-RT-001/behavior_only_replay.json",
        "LCC-RT-002/learned_vs_table_effect_report.md",
        "LCC-RT-002/learned_effect_metrics.json",
        "LCC-RT-003/strong_baseline_equivalence_report.md",
        "LCC-RT-003/baseline_equivalence_results.json",
        "LCC-RT-004/counterfactual_model_perturbation_report.md",
        "LCC-RT-004/counterfactual_model_perturbation.json",
        "LCC-RT-005/heldout_mechanism_world_report.md",
        "LCC-RT-005/heldout_mechanism_world_results.json",
        "LCC-RT-006/CYCLE_001_DECISION.md",
        "LCC-RT-006/cycle_001_decision.json",
    ]

    for rel_path in required:
        assert (tmp_path / rel_path).exists(), rel_path

    with (tmp_path / "LCC-RT-006/cycle_001_decision.json").open(
        "r", encoding="utf-8"
    ) as fh:
        decision = json.load(fh)
    assert decision["verdict"] == "lcc_contract_strengthened_bounded"
    assert decision["cannot_prove"]
    assert all(gate["passed"] for gate in decision["required_gates"].values())
