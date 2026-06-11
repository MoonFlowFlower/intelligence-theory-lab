import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

from representational_gap_preflight.runner import run_preflight


def _anchor_provider(payload_hash):
    return {
        "anchor_method": "unit_test_stub_external_time_anchor",
        "anchored_payload_hash": payload_hash,
        "external_utc": "2026-06-11T00:00:00Z",
        "verification_status": "verified",
    }


def test_preflight_generates_required_evidence_stack(tmp_path):
    task_card = Path(__file__).parents[1] / "docs" / "REPRESENTATIONAL-GAP-PREFLIGHT-001A.md"

    result = run_preflight(
        output_dir=tmp_path,
        task_card_path=task_card,
        anchor_provider=_anchor_provider,
    )

    assert result["task_id"] == "REPRESENTATIONAL-GAP-PREFLIGHT-001A"
    assert result["verdict"] == "representational_gap_preflight_bounded_pass"
    assert result["claim_ceiling"] == "bounded representational-gap preflight evidence"
    assert result["K_window_bound"] == 4
    assert result["training_performed"] is False
    assert result["gate1_reopen_status"] == "still_blocked"
    assert result["same_agent_bridge_status"] == "still_blocked_until_clean_local_model_class_survives"
    assert result["ego_integration_status"] == "not_authorized"
    assert result["stage0_anchor_pass"] is True
    assert result["bounded_order_window_gap_verified_for_K_le_4"] is True
    assert result["graph_cache_family_gap_verified"] is True
    assert result["positive_witness_model_exists"] is True
    assert result["witness_non_oracle_access_check_pass"] is True
    assert result["next_allowed_task"] == "MODEL-CLASS-RESET-PREFLIGHT-001A"

    required = {
        "hypothesis_registry.json",
        "environment_contract.json",
        "access_contract.json",
        "champion_challenger_matrix.json",
        "graph_cache_family_matrix.json",
        "expressivity_proof.md",
        "verifier_results.json",
        "control_competence_report.json",
        "witness_access_audit.json",
        "control_access_audit.json",
        "failure_taxonomy_report.json",
        "claim_ceiling.md",
        "decision_ledger.json",
        "final_report.md",
        "result.json",
        "stage0_freeze_anchor.json",
    }
    assert required.issubset({p.name for p in tmp_path.iterdir()})

    matrix = json.loads((tmp_path / "champion_challenger_matrix.json").read_text())
    assert set(matrix["challengers"]) == {
        "C0_random_baseline",
        "C1_majority_baseline",
        "C2_frequency_heuristic",
        "C3_count_table",
        "C4_transition_table",
        "C5_nearest_neighbor_trace_lookup",
        "C6_bounded_order_window_model_K1",
        "C7_bounded_order_window_model_K2",
        "C8_bounded_order_window_model_K3",
        "C9_bounded_order_window_model_K4",
        "C10_summary_memory_baseline",
    }
    assert set(matrix["witnesses"]) == {
        "W0_finite_latent_state_model_with_memory",
        "W1_automaton_or_state_machine_witness",
        "W2_factorized_rule_model_witness",
    }
    assert all(w["can_represent"] for w in matrix["witnesses"].values())

    graph_matrix = json.loads((tmp_path / "graph_cache_family_matrix.json").read_text())
    assert set(graph_matrix["graph_cache_family_challengers"]) == {
        "G0_graph_lookup",
        "G1_transition_table_graph_variant",
        "G2_successor_map",
        "G3_count_table_graph_variant",
        "G4_fsm_planner",
        "G5_episodic_traversal",
    }
    assert graph_matrix["treated_as_first_class_mandatory_challengers"] is True
    assert all(v["gap_verified"] for v in graph_matrix["results"].values())

    stage0 = json.loads((tmp_path / "stage0_freeze_anchor.json").read_text())
    assert stage0["stage0_order"]["freeze_payload_before_anchor"] is True
    assert stage0["stage0_order"]["anchor_verified_before_verifier"] is True
    assert stage0["stage0_order"]["verifier_started_before_anchor"] is False


def test_verifier_reports_required_gap_checks(tmp_path):
    run_preflight(
        output_dir=tmp_path,
        task_card_path=Path(__file__),
        anchor_provider=_anchor_provider,
    )

    verifier = json.loads((tmp_path / "verifier_results.json").read_text())

    window = verifier["bounded_order_window"]
    assert set(window) == {"1", "2", "3", "4"}
    for record in window.values():
        assert record["gap_proven"] is True
        left, right = record["conflict_examples"]
        assert left["window"] == right["window"]
        assert left["prediction_target"] != right["prediction_target"]

    assert verifier["count_table"]["gap_verified"] is True
    assert verifier["transition_table"]["gap_verified"] is True
    assert verifier["frequency_heuristic"]["gap_verified"] is True
    assert verifier["nearest_neighbor"]["gap_verified"] is True
    assert verifier["summary_memory"]["gap_verified"] is True
    assert verifier["graph_cache_family"]["gap_verified"] is True
    assert verifier["controls_disabled_by_construction"]["pass"] is True
    assert verifier["lookup_triviality_check"]["pass"] is True
    assert verifier["K_window_bound"] == 4
    assert verifier["K_expansion_attempted"] is False


def test_stage0_anchor_failure_stops_before_verifier(tmp_path):
    result = run_preflight(
        output_dir=tmp_path,
        task_card_path=Path(__file__),
        anchor_provider=lambda _payload_hash: {
            "anchor_method": "unit_test_failed_anchor",
            "verification_status": "failed",
        },
    )

    assert result["verdict"] == "representational_gap_failed_stage0_anchor"
    assert result["claim_ceiling"] == "no representational-gap evidence"
    assert result["verifier_ran"] is False
    assert not (tmp_path / "verifier_results.json").exists()
