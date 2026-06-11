import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

from representational_gap_preflight_001b.runner import run_preflight_001b


def _anchor_provider(payload_hash):
    return {
        "anchor_method": "unit_test_stub_external_time_anchor",
        "anchored_payload_hash": payload_hash,
        "external_utc": "2026-06-11T00:00:00Z",
        "verification_status": "verified",
    }


def test_001b_returns_failure_when_fair_full_history_controls_solve(tmp_path):
    task_card = Path(__file__).parents[1] / "docs" / "REPRESENTATIONAL-GAP-PREFLIGHT-001B.md"

    result = run_preflight_001b(
        output_dir=tmp_path,
        task_card_path=task_card,
        anchor_provider=_anchor_provider,
    )

    assert result["task_id"] == "REPRESENTATIONAL-GAP-PREFLIGHT-001B"
    assert result["verdict"] == "representational_gap_001b_failed_count_or_statistic_control_solved"
    assert result["stage0_anchor_pass"] is True
    assert result["verifier_ran"] is True
    assert result["training_performed"] is False
    assert result["model_class_reset_authorized"] is False
    assert result["same_agent_bridge_status"] == "not_authorized"
    assert result["gate1_reopen_status"] == "not_authorized"
    assert result["ego_integration_status"] == "not_authorized"
    assert result["next_allowed_task"] == "theory_reset_or_new_problem_definition"

    assert result["bounded_window_gap_verified"] is True
    assert result["full_history_count_statistic_controls_solved"] is True
    assert result["full_history_count_statistic_controls_fail_fairly"] is False
    assert result["finite_state_automaton_controls_solved"] is True
    assert result["graph_cache_controls_solved"] is True
    assert result["knn_episodic_controls_solved"] is True
    assert result["summary_controls_solved"] is True
    assert result["positive_witness_exists"] is True
    assert result["not_trivial_horizon_gap"] is False

    required = {
        "task_manifest.json",
        "stage0_freeze_anchor.json",
        "hypothesis_registry.json",
        "environment_contract.json",
        "target_rule_contract.json",
        "access_contract.json",
        "control_family_contracts.json",
        "witness_family_contracts.json",
        "champion_challenger_matrix.json",
        "control_competence_report.json",
        "expressivity_proof.md",
        "verifier_results.json",
        "control_disabled_by_construction_audit.json",
        "lookup_triviality_audit.json",
        "trivial_horizon_gap_audit.json",
        "failure_taxonomy_report.json",
        "claim_ceiling.md",
        "decision_ledger.json",
        "final_report.md",
        "result.json",
    }
    assert required.issubset({p.name for p in tmp_path.iterdir()})

    stage0 = json.loads((tmp_path / "stage0_freeze_anchor.json").read_text())
    assert stage0["stage0_order"]["freeze_payload_before_anchor"] is True
    assert stage0["stage0_order"]["anchor_verified_before_verifier"] is True
    assert stage0["stage0_order"]["verifier_started_before_anchor"] is False


def test_001b_verifier_records_real_solving_controls_and_matrix(tmp_path):
    run_preflight_001b(
        output_dir=tmp_path,
        task_card_path=Path(__file__),
        anchor_provider=_anchor_provider,
    )

    verifier = json.loads((tmp_path / "verifier_results.json").read_text())

    assert verifier["bounded_window_controls"]["K4"]["solves_target"] is False
    assert verifier["bounded_window_controls"]["K4"]["gap_verified"] is True
    assert verifier["full_history_count_statistic_controls"]["parity_or_modular_statistic"]["solves_target"] is True
    assert verifier["full_history_count_statistic_controls"]["full_history_pair_count"]["solves_target"] is True
    assert verifier["finite_state_automaton_controls"]["capacity_2"]["solves_target"] is True
    assert verifier["graph_cache_controls"]["history_graph_cache"]["solves_target"] is True
    assert verifier["knn_episodic_controls"]["episodic_exact_match"]["solves_target"] is True
    assert verifier["summary_controls"]["minimal_sufficient_statistic_search"]["solves_target"] is True
    assert verifier["positive_witness"]["one_bit_xor_witness"]["solves_target"] is True
    assert verifier["positive_witness"]["one_bit_xor_witness"]["uses_only_allowed_access"] is True
    assert verifier["oracle_leakage_controls"]["target_label_oracle"]["admissible_baseline"] is False

    competence = json.loads((tmp_path / "control_competence_report.json").read_text())
    assert competence["hardcoded_attestation_detected"] is False
    assert all(item["executed_real_code_or_proof"] for item in competence["controls"].values())

    matrix = json.loads((tmp_path / "champion_challenger_matrix.json").read_text())
    expected_rows = {
        "bounded_window_K1",
        "bounded_window_K2",
        "bounded_window_K3",
        "bounded_window_K4",
        "full_history_count",
        "full_history_n_gram_count",
        "minimal_summary_statistic",
        "finite_state_automaton_2",
        "finite_state_automaton_4",
        "finite_state_automaton_8",
        "finite_state_automaton_16",
        "transition_graph_cache",
        "history_graph_cache",
        "successor_map_cache",
        "episodic_retrieval",
        "nearest_neighbor_retrieval",
        "positive_witness",
        "oracle_controls",
    }
    assert expected_rows.issubset(set(matrix["rows"]))
    assert matrix["rows"]["full_history_count"]["solves_target"] is True
    assert matrix["rows"]["positive_witness"]["solves_target"] is True


def test_001b_stage0_anchor_failure_stops_before_verifier(tmp_path):
    result = run_preflight_001b(
        output_dir=tmp_path,
        task_card_path=Path(__file__),
        anchor_provider=lambda _payload_hash: {
            "anchor_method": "unit_test_failed_anchor",
            "verification_status": "failed",
        },
    )

    assert result["verdict"] == "representational_gap_001b_failed_stage0_anchor"
    assert result["claim_ceiling"] == "no 001B representational-gap evidence"
    assert result["verifier_ran"] is False
    assert not (tmp_path / "verifier_results.json").exists()
