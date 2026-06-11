import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from negative_evidence_admission_gate_001a import evaluate_successor_task


SUPPORT_DOCS = [
    "docs/process_intervention_preflight_001a/amendment_001.md",
    "docs/process_intervention_preflight_001a/real_control_implementation_contract.md",
    "docs/process_intervention_preflight_001a/trace_commitment_contract.md",
    "docs/process_intervention_preflight_001a/match_metric_contract.md",
    "docs/process_intervention_preflight_001a/update_path_contract.md",
    "docs/process_intervention_preflight_001a/separation_statistic_contract.md",
    "docs/process_intervention_preflight_001a/state_accounting_contract.md",
    "docs/process_intervention_preflight_001a/resource_budget_contract.md",
    "docs/process_intervention_preflight_001a/environment_intervention_instantiation_contract.md",
    "docs/process_intervention_preflight_001a/memory_key_fidelity_contract.md",
    "docs/process_intervention_preflight_001a/behavior_probe_contract.md",
    "docs/process_intervention_preflight_001a/stage0_freeze_anchor_contract.md",
]

ARTIFACTS = [
    "artifacts/process_intervention_preflight_001a_amendment_001/amendment_result.json",
    "artifacts/process_intervention_preflight_001a_amendment_001/amendment_matrix.json",
    "artifacts/process_intervention_preflight_001a_amendment_001/blocking_gate_status.json",
    "artifacts/process_intervention_preflight_001a_amendment_001/nonblocking_gate_status.json",
    "artifacts/process_intervention_preflight_001a_amendment_001/verdict_manifest.json",
]


def _read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _read_json(relative_path: str) -> dict:
    return json.loads(_read_text(relative_path))


def test_required_amendment_support_outputs_exist_and_parse():
    for relative_path in SUPPORT_DOCS + ARTIFACTS:
        assert (ROOT / relative_path).exists(), relative_path

    for relative_path in ARTIFACTS:
        _read_json(relative_path)


def test_a1_real_controls_contract_closes_name_only_channel():
    text = _read_text(
        "docs/process_intervention_preflight_001a/real_control_implementation_contract.md"
    )

    for phrase in [
        "actual implementations or real closed-form decision procedures",
        "Name-only controls are invalid",
        "Hardcoded competence attestations",
        "Hardcoded fairness attestations",
        "intervention_labeled_graph_cache",
        "causal_table",
        "graph_lookup",
        "transition_table",
        "successor_map",
        "count_table",
        "fsm_planner",
        "episodic_traversal",
        "online_graph_lookup",
        "online_transition_table",
        "online_successor_map",
        "online_count_table",
        "online_fsm_planner",
        "online_episodic_traversal",
        "solve_criterion",
        "failure_verdict_if_it_matches",
    ]:
        assert phrase in text


def test_a2_to_a5_hard_gate_contracts_are_operationalized():
    trace = _read_text("docs/process_intervention_preflight_001a/trace_commitment_contract.md")
    metrics = _read_text("docs/process_intervention_preflight_001a/match_metric_contract.md")
    update = _read_text("docs/process_intervention_preflight_001a/update_path_contract.md")
    separation = _read_text(
        "docs/process_intervention_preflight_001a/separation_statistic_contract.md"
    )

    for phrase in [
        "step-interleaved",
        "append-only",
        "hash-chained",
        "committed before verifier outcome",
        "previous_trace_hash",
        "current_trace_hash",
    ]:
        assert phrase in trace

    for phrase in [
        "intervention_response_match",
        "internal_update_trace_match",
        "later_behavior_change_match",
        "equivalence_band",
        "threshold",
        "No post-hoc metric selection",
        "solve = reproduce and match the primary separation statistic",
    ]:
        assert phrase in metrics

    for phrase in [
        "allowed_update_path",
        "step level",
        "state_before_update is reproducible",
        "Schema inspection alone is invalid replay",
        "no forbidden access appears in access_manifest",
    ]:
        assert phrase in update

    for phrase in [
        "resource_normalized_heldout_composition_update_divergence",
        "prediction_error_causal_use_profile",
        "deletion_sensitivity_profile",
        "not output accuracy alone",
        "If the best fair online cheap control matches",
    ]:
        assert phrase in separation


def test_a6_to_a11_stage0_contracts_exist_and_reject_false_passes():
    joined = "\n".join(
        _read_text(path)
        for path in [
            "docs/process_intervention_preflight_001a/state_accounting_contract.md",
            "docs/process_intervention_preflight_001a/resource_budget_contract.md",
            "docs/process_intervention_preflight_001a/environment_intervention_instantiation_contract.md",
            "docs/process_intervention_preflight_001a/memory_key_fidelity_contract.md",
            "docs/process_intervention_preflight_001a/behavior_probe_contract.md",
            "docs/process_intervention_preflight_001a/stage0_freeze_anchor_contract.md",
        ]
    )

    for phrase in [
        "Trace fields are write-only audit outputs",
        "state_budget = 16 KiB",
        "starves it",
        "intervention_labeled_graph_cache may key on `intervention_condition`",
        "retrieval_hits are reproducible",
        "future_action_distribution_shift",
        "future_policy_choice_change",
        "freeze_commit_or_tag",
        "sha256_manifest",
        "candidate system must not self-attest acceptance",
        "Verdict-string tests are not acceptance evidence",
    ]:
        assert phrase in joined


def test_amendment_matrix_closes_a1_to_a11_without_remaining_blockers():
    matrix = _read_json(
        "artifacts/process_intervention_preflight_001a_amendment_001/amendment_matrix.json"
    )
    blocking = _read_json(
        "artifacts/process_intervention_preflight_001a_amendment_001/blocking_gate_status.json"
    )
    result = _read_json(
        "artifacts/process_intervention_preflight_001a_amendment_001/amendment_result.json"
    )

    assert {row["audit_amendment_id"] for row in matrix["rows"]} == {
        f"A{i}" for i in range(1, 12)
    }
    assert all(row["status"] == "closed" for row in matrix["rows"])
    assert blocking["remaining_blockers"] == []
    assert result["semantic_audit_pass_current"] is True
    assert result["forbidden_scope"]["old_experiments_rerun"] is False
    assert result["forbidden_scope"]["old_artifacts_repaired"] is False
    assert result["forbidden_scope"]["fable_or_model_poisoning_audit_created"] is False
    assert result["forbidden_scope"]["lexical_gate_treated_as_mechanism_evidence"] is False


def test_001b_task_card_passes_negative_evidence_admission_and_keeps_boundary():
    card = _read_text(
        "docs/codex/tasks/PROCESS-INTERVENTION-PREFLIGHT-001B-EXECUTABLE-PREFLIGHT-TASK-CARD.md"
    )
    gate = evaluate_successor_task(card)

    assert gate["passed"] is True
    assert gate["failure_ids"] == []

    for phrase in [
        "superseded_by_independent_audit",
        "representational_gap_001b_failed_count_or_statistic_control_solved",
        "PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-CANONICAL-ERRATA-001A",
        "process_intervention_001a_independent_audit_pass_with_caveats is not executable authorization",
        "verdict-string tests are not acceptance evidence",
        "gate1_preflight_failed_graph_cache_collapse",
        "provenance, diff, and mechanism evidence",
        "execution_authorized_by_this_draft = false",
        "mechanism_implementation_authorized = false",
    ]:
        assert phrase in card


def test_no_forbidden_process_intervention_implementation_paths_created():
    forbidden_paths = [
        "src/process_intervention_preflight_001a",
        "src/process_intervention_mechanism",
    ]

    for relative_path in forbidden_paths:
        assert not (ROOT / relative_path).exists(), relative_path
