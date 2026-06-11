import json

from cmbc_companion.evals.verify_growth_loop import run_verification


def test_same_context_different_history_changes_action_distribution(tmp_path):
    result = run_verification(tmp_path, seeds=(101,))

    metrics = result["metrics"]
    assert result["verdict"] == "cmbc_companion_growth_loop_bounded_pass"
    assert metrics["same_context_history_divergence_rate"] == 1.0
    assert result["gates"]["same_context_different_history"]["passed"] is True


def test_relevant_deletion_regresses_behavior(tmp_path):
    result = run_verification(tmp_path, seeds=(101,))

    metrics = result["metrics"]
    assert metrics["relevant_deletion_regression"] > 0.15
    assert result["gates"]["relevant_deletion"]["passed"] is True


def test_irrelevant_deletion_does_not_regress_behavior(tmp_path):
    result = run_verification(tmp_path, seeds=(101,))

    metrics = result["metrics"]
    assert metrics["irrelevant_deletion_non_regression"] >= 0.95
    assert result["gates"]["irrelevant_deletion"]["passed"] is True


def test_relationship_outcome_perturbation_changes_action_distribution(tmp_path):
    result = run_verification(tmp_path, seeds=(101,))

    metrics = result["metrics"]
    assert metrics["relationship_outcome_perturbation_sensitivity"] == 1.0
    assert result["gates"]["relationship_outcome_perturbation"]["passed"] is True


def test_interruption_risk_perturbation_changes_action_distribution(tmp_path):
    result = run_verification(tmp_path, seeds=(101,))

    metrics = result["metrics"]
    assert metrics["interruption_risk_perturbation_sensitivity"] == 1.0
    assert result["gates"]["interruption_risk_perturbation"]["passed"] is True


def test_renderer_cannot_change_selected_action(tmp_path):
    result = run_verification(tmp_path, seeds=(101,))

    metrics = result["metrics"]
    assert metrics["renderer_action_invariance"] == 1.0
    assert result["gates"]["renderer_isolation"]["passed"] is True


def test_behavior_only_replay_reconstructs_decision(tmp_path):
    result = run_verification(tmp_path, seeds=(101,))

    replay = result["behavior_only_replay"]
    assert replay["passed"] is True
    assert replay["match_rate"] == 1.0
    assert replay["used_fields"] == [
        "observation",
        "anonymous_candidate_actions",
        "prediction_before_action",
        "action_distribution",
        "selected_action",
        "model_version",
    ]


def test_action_label_permutation_invariant(tmp_path):
    result = run_verification(tmp_path, seeds=(101,))

    metrics = result["metrics"]
    assert metrics["label_permutation_invariance"] == 1.0
    assert result["gates"]["label_permutation"]["passed"] is True


def test_effect_swap_sensitive(tmp_path):
    result = run_verification(tmp_path, seeds=(101,))

    metrics = result["metrics"]
    assert metrics["effect_swap_sensitivity"] == 1.0
    assert result["gates"]["effect_swap"]["passed"] is True


def test_strong_heuristic_not_equivalent_or_reports_equivalence(tmp_path):
    result = run_verification(tmp_path, seeds=(101,))

    challenger = result["challengers"]["StrongHeuristic"]
    if challenger["equivalent"]:
        assert result["verdict"] == "heuristic_equivalent"
    else:
        assert challenger["match_rate"] < challenger["equivalence_band"]


def test_rag_memory_not_equivalent_or_reports_equivalence(tmp_path):
    result = run_verification(tmp_path, seeds=(101,))

    challenger = result["challengers"]["RAGMemoryPrompt"]
    if challenger["equivalent"]:
        assert result["verdict"] == "rag_memory_equivalent"
    else:
        assert challenger["match_rate"] < challenger["equivalence_band"]


def test_active_inference_proxy_not_equivalent_or_reports_collapse(tmp_path):
    result = run_verification(tmp_path, seeds=(101,))

    challenger = result["challengers"]["ActiveInferenceEmpowermentProxy"]
    if challenger["equivalent"]:
        assert result["verdict"] == "collapses_into_active_inference_or_empowerment_proxy"
    else:
        assert challenger["match_rate"] < challenger["equivalence_band"]


def test_required_artifacts_are_written(tmp_path):
    result = run_verification(tmp_path, seeds=(101, 102, 103))

    required = {
        "VERIFY_STATUS.md",
        "verification_config.json",
        "traces.jsonl",
        "behavior_only_replay.json",
        "metrics.json",
        "deletion_report.md",
        "perturbation_report.md",
        "renderer_isolation_report.md",
        "challenger_report.md",
        "anti_shortcut_scan.md",
        "CMBC_COMPANION_VERIFY_RESULT.md",
        "cmbc_companion_verify_result.json",
    }
    assert required.issubset({path.name for path in tmp_path.iterdir()})

    with (tmp_path / "cmbc_companion_verify_result.json").open("r", encoding="utf-8") as fh:
        verdict = json.load(fh)
    assert verdict["verdict"] == result["verdict"]
    assert verdict["claim_boundary"] == "bounded companion growth-loop verification only"

