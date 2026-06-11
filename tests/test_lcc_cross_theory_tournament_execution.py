import json
from pathlib import Path

from theory_lab.lcc_cross_theory_tournament import run_tournament


def test_cross_theory_tournament_runs_and_allows_collapse(tmp_path: Path) -> None:
    out = tmp_path / "xte"
    result = run_tournament(out)

    assert result["verdict"] == "lcc_collapses_into_causal_model_based_control"
    assert result["theory_support"] == "not_yet"
    assert result["bottom_intelligence_principle"] == "not_claimed"
    assert result["general_lcc_agent"] == "not_authorized"
    assert result["ego_migration"] == "no_go"
    assert result["cycle_011"] == "not_authorized"
    assert result["stop_conditions"] == []

    decision = json.loads((out / "XTE-011" / "cross_theory_tournament_result.json").read_text())
    assert decision["verdict"] == result["verdict"]
    assert "LCC_v0 is better treated as an operational evidence discipline" in decision["maximum_claim"]


def test_competitors_are_complete_and_oracle_is_diagnostic_only(tmp_path: Path) -> None:
    out = tmp_path / "xte"
    run_tournament(out)
    audit = json.loads((out / "XTE-002" / "competitor_scope_audit.json").read_text())

    expected = {
        "T1_LCC_v0",
        "T2_ModelBasedRL_WorldModelPlanner",
        "T3_CausalModelBasedControl",
        "T4_ActiveInference_EFE_Controller",
        "T5_Empowerment_ControllabilityPlanner",
        "T6_PredictiveProcessing_Control",
        "T7_MetaRL_RecurrentPolicy",
        "T8_ProgramSearch_Planner",
        "T9_StrongHeuristic_SafetyControl",
        "T10_OracleDiagnosticUpperBound",
    }
    assert set(audit["competitors"]) == expected
    assert audit["oracle"]["diagnostic_only"] is True
    assert audit["oracle"]["valid_competitor"] is False
    assert audit["stop_conditions"] == []


def test_holdout_coverage_and_freeze_integrity(tmp_path: Path) -> None:
    out = tmp_path / "xte"
    run_tournament(out)

    freeze = json.loads((out / "XTE-004" / "competitor_freeze_manifest.json").read_text())
    holdout = json.loads((out / "XTE-005" / "blind_holdout_manifest.json").read_text())

    assert freeze["freeze_hash_stable"] is True
    assert freeze["code_changes_after_freeze"] is False
    assert holdout["generated_after_freeze"] is True
    assert holdout["instance_count"] >= 200
    assert len(holdout["families"]) >= 10
    assert len(holdout["hybrid_families"]) >= 4
    assert holdout["negative_controls_represented"] is True
    assert holdout["metadata_hidden_from_competitors"] is True


def test_metrics_equivalence_and_independent_scoring(tmp_path: Path) -> None:
    out = tmp_path / "xte"
    run_tournament(out)

    metrics = json.loads((out / "XTE-007" / "metrics_results.json").read_text())
    independent = json.loads((out / "XTE-009" / "independent_metrics.json").read_text())
    diff = json.loads((out / "XTE-009" / "primary_vs_independent_diff.json").read_text())

    assert metrics["equivalence"]["T3_CausalModelBasedControl"]["overall"] == "tie"
    assert metrics["equivalence"]["T3_CausalModelBasedControl"]["collapse_candidate"] is True
    assert metrics["equivalence"]["T2_ModelBasedRL_WorldModelPlanner"]["overall"] in {"loss", "tie"}
    assert independent["verdict"] == "independent_scoring_match"
    assert diff["max_abs_diff"] == 0.0


def test_redteam_gates_are_shared_and_clean(tmp_path: Path) -> None:
    out = tmp_path / "xte"
    run_tournament(out)

    gates = json.loads((out / "XTE-008" / "redteam_gate_results.json").read_text())
    non_oracle = [name for name in gates["competitors"] if name != "T10_OracleDiagnosticUpperBound"]

    assert gates["verdict"] == "shared_gates_passed"
    for name in non_oracle:
        assert gates["competitors"][name]["shared_gates_applied"] is True
        assert gates["competitors"][name]["forbidden_input_leaks"] == []
        assert gates["competitors"][name]["behavior_only_replay"] == "pass"
    assert gates["oracle"]["diagnostic_only"] is True


def test_required_artifacts_exist(tmp_path: Path) -> None:
    out = tmp_path / "xte"
    run_tournament(out)

    required = [
        "XTE-000/STATUS.md",
        "XTE-000/contract_freeze_manifest.json",
        "XTE-001/runtime_schema_report.md",
        "XTE-001/leak_scan_report.md",
        "XTE-002/competitor_implementation_report.md",
        "XTE-002/competitor_scope_audit.json",
        "XTE-003/task_generator_report.md",
        "XTE-003/task_family_manifest.json",
        "XTE-004/competitor_freeze_manifest.json",
        "XTE-004/freeze_integrity_report.md",
        "XTE-005/blind_holdout_manifest.json",
        "XTE-005/holdout_generation_report.md",
        "XTE-006/traces.jsonl",
        "XTE-006/raw_results.json",
        "XTE-006/per_competitor_metrics.json",
        "XTE-006/per_family_metrics.json",
        "XTE-007/metrics_report.md",
        "XTE-007/metrics_results.json",
        "XTE-007/equivalence_matrix.csv",
        "XTE-008/redteam_gate_report.md",
        "XTE-008/redteam_gate_results.json",
        "XTE-009/independent_scoring_report.md",
        "XTE-009/independent_metrics.json",
        "XTE-009/primary_vs_independent_diff.json",
        "XTE-010/replication_results.json",
        "XTE-010/statistical_replication_report.md",
        "XTE-011/CROSS_THEORY_TOURNAMENT_RESULT.md",
        "XTE-011/cross_theory_tournament_result.json",
    ]

    for rel in required:
        assert (out / rel).is_file(), rel
