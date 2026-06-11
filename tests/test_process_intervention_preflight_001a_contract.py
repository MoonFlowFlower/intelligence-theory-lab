import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")


def _read_json(path):
    return json.loads(_read_text(path))


def test_process_intervention_preflight_001a_required_outputs_exist():
    required = [
        "docs/PROCESS-INTERVENTION-PREFLIGHT-001A.md",
        "docs/process_intervention_preflight_001a/problem_contract.md",
        "docs/process_intervention_preflight_001a/intervention_contract.md",
        "docs/process_intervention_preflight_001a/trace_replay_contract.md",
        "docs/process_intervention_preflight_001a/control_adversary_contract.md",
        "docs/process_intervention_preflight_001a/resource_contract.md",
        "docs/process_intervention_preflight_001a/collapse_audit.md",
        "docs/process_intervention_preflight_001a/claim_ceiling.md",
        "artifacts/process_intervention_preflight_001a/verdict_manifest.json",
        "artifacts/process_intervention_preflight_001a/contract_summary.json",
    ]

    for relative_path in required:
        assert (ROOT / relative_path).exists(), relative_path


def test_process_intervention_preflight_001a_main_sections_and_gate():
    text = _read_text("docs/PROCESS-INTERVENTION-PREFLIGHT-001A.md")
    required_sections = [
        "current_layer",
        "parent_lineage_summary",
        "wrong_proxy_to_avoid",
        "correct_problem_definition",
        "future_environment_requirements",
        "intervention_contract",
        "online_update_contract",
        "trace_replay_contract",
        "state_delta_metric_contract",
        "future_behavior_effect_metric",
        "cheap_control_adversaries",
        "oracle_leakage_probes",
        "resource_contract",
        "ablation_contract",
        "anti_hardcoding_audit",
        "trace_theater_audit",
        "acceptance_gate",
        "failure_verdicts",
        "claim_ceiling",
        "stop_conditions",
        "rollback_plan",
        "next_allowed_task",
    ]
    for section in required_sections:
        assert section in text

    required_phrases = [
        "intervention response",
        "internal update trace",
        "later behavior change",
        "graph/cache trace generator",
        "trace-only replay",
        "behavior-only replay",
        "resource_contract_symmetric = true",
        "value_state_boundary_non_affective = true",
        "process_intervention_preflight_001a_task_card_bounded_pass",
    ]
    for phrase in required_phrases:
        assert phrase in text


def test_process_intervention_preflight_001a_manifest_boundaries():
    verdict = _read_json("artifacts/process_intervention_preflight_001a/verdict_manifest.json")
    summary = _read_json("artifacts/process_intervention_preflight_001a/contract_summary.json")

    assert verdict["task_id"] == "PROCESS-INTERVENTION-PREFLIGHT-001A"
    assert verdict["final_verdict"] == "process_intervention_preflight_001a_task_card_bounded_pass"
    assert verdict["strongest_allowed_claim_ceiling"] == (
        "bounded process/intervention executable-preflight task-card evidence only"
    )
    assert verdict["next_allowed_task_if_any"] == (
        "PROCESS-INTERVENTION-PREFLIGHT-001A independent audit or future executable-preflight authorization review"
    )
    assert verdict["mechanism_implementation_authorized"] is False
    assert verdict["mechanism_training_authorized"] is False
    assert verdict["agent_training_authorized"] is False
    assert verdict["model_class_reset_authorized"] is False
    assert verdict["gate1_reopen_authorized"] is False
    assert verdict["same_agent_bridge_authorized"] is False
    assert verdict["ego_integration_authorized"] is False
    assert verdict["stop_conditions_encountered"] == []

    for field in [
        "no_mechanism_implementation",
        "no_training",
        "problem_is_not_output_level",
        "intervention_response_required",
        "internal_update_trace_required",
        "later_behavior_change_required",
        "trace_theater_failure_gate_defined",
        "fair_online_controls_required",
        "graph_cache_trace_generator_required",
        "trace_only_replay_required",
        "behavior_only_replay_required",
        "random_representation_control_required",
        "shuffled_outcome_control_required",
        "resource_contract_symmetric",
        "value_state_boundary_non_affective",
        "claim_ceiling_enforced",
    ]:
        assert summary["acceptance_gate"][field] is True, field


def test_process_intervention_preflight_001a_contract_docs_cover_controls_and_interventions():
    text = "\n".join(
        _read_text(path)
        for path in [
            "docs/process_intervention_preflight_001a/problem_contract.md",
            "docs/process_intervention_preflight_001a/intervention_contract.md",
            "docs/process_intervention_preflight_001a/trace_replay_contract.md",
            "docs/process_intervention_preflight_001a/control_adversary_contract.md",
            "docs/process_intervention_preflight_001a/resource_contract.md",
            "docs/process_intervention_preflight_001a/collapse_audit.md",
            "docs/process_intervention_preflight_001a/claim_ceiling.md",
        ]
    )

    for phrase in [
        "state deletion",
        "memory deletion",
        "representation freezing",
        "prediction-error injection",
        "counterfactual action substitution",
        "observation perturbation",
        "history-preserving causal perturbation",
        "online distribution shift",
        "full-history count/statistic",
        "online graph/cache",
        "online kNN",
        "causal table",
        "random representation",
        "shuffled outcome",
        "oracle/leakage probes",
        "witness and controls receive comparable resource budgets",
        "value-state language leaks into emotion/subjectivity",
    ]:
        assert phrase in text


def test_process_intervention_preflight_001a_no_forbidden_implementation_paths():
    forbidden_paths = [
        "src/process_intervention_mechanism",
        "src/new_mechanism",
        "src/process_intervention_preflight_001a",
    ]

    for relative_path in forbidden_paths:
        assert not (ROOT / relative_path).exists(), relative_path
