import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")


def _read_json(path):
    return json.loads(_read_text(path))


def test_new_problem_preflight_001a_required_outputs_exist():
    required = [
        "docs/NEW-PROBLEM-PREFLIGHT-001A.md",
        "docs/new_problem_preflight_001a/proxy_contract.md",
        "docs/new_problem_preflight_001a/candidate_proxy_matrix.md",
        "docs/new_problem_preflight_001a/intervention_contract.md",
        "docs/new_problem_preflight_001a/trace_replay_contract.md",
        "docs/new_problem_preflight_001a/control_adversary_contract.md",
        "docs/new_problem_preflight_001a/resource_contract.md",
        "docs/new_problem_preflight_001a/value_state_boundary.md",
        "docs/new_problem_preflight_001a/collapse_audit.md",
        "docs/new_problem_preflight_001a/claim_ceiling.md",
        "artifacts/new_problem_preflight_001a/proxy_contract_result.json",
        "artifacts/new_problem_preflight_001a/candidate_proxy_matrix.json",
        "artifacts/new_problem_preflight_001a/collapse_audit.json",
        "artifacts/new_problem_preflight_001a/verdict_manifest.json",
    ]

    for relative_path in required:
        assert (ROOT / relative_path).exists(), relative_path


def test_new_problem_preflight_001a_verdict_and_boundaries():
    result = _read_json("artifacts/new_problem_preflight_001a/proxy_contract_result.json")
    verdict = _read_json("artifacts/new_problem_preflight_001a/verdict_manifest.json")

    assert result["task_id"] == "NEW-PROBLEM-PREFLIGHT-001A"
    assert result["final_verdict"] == "new_problem_preflight_001a_proxy_contract_bounded_pass"
    assert result["strongest_allowed_claim_ceiling"] == "bounded process/intervention proxy-contract evidence only"
    assert result["next_allowed_task_if_any"] in {
        "PROCESS-INTERVENTION-PREFLIGHT-001A task-card drafting",
        "NEW-PROBLEM-PREFLIGHT-001B executable-preflight task-card drafting",
    }
    assert result["not_output_level_proxy"] is True
    assert result["primary_axis_process_intervention"] is True
    assert result["online_adaptation_as_constraint"] is True
    assert result["causal_intervention_as_constraint"] is True
    assert result["resource_contract_symmetric"] is True
    assert result["value_state_not_primary"] is True
    assert result["non_affective_value_boundary_defined"] is True
    assert result["mandatory_controls_carried_forward"] is True
    assert result["trace_replay_contract_defined"] is True
    assert result["intervention_contract_defined"] is True
    assert result["state_delta_metric_contract_defined"] is True
    assert result["future_behavior_effect_required"] is True
    assert result["collapse_audit_completed"] is True
    assert result["anti_hardcoding_audit_completed"] is True
    assert result["claim_ceiling_enforced"] is True
    assert result["no_mechanism_implementation"] is True
    assert result["no_training"] is True
    assert result["no_model_class_reset"] is True
    assert result["no_Gate1_reopen"] is True
    assert result["no_same_agent_bridge"] is True
    assert result["no_EGO_integration"] is True
    assert result["stop_conditions_encountered"] == []

    assert verdict["mechanism_implementation_authorized"] is False
    assert verdict["mechanism_training_authorized"] is False
    assert verdict["agent_training_authorized"] is False
    assert verdict["model_class_reset_authorized"] is False
    assert verdict["gate1_reopen_authorized"] is False
    assert verdict["same_agent_bridge_authorized"] is False
    assert verdict["ego_integration_authorized"] is False


def test_new_problem_preflight_001a_candidate_matrix_and_collapse_audit():
    matrix = _read_json("artifacts/new_problem_preflight_001a/candidate_proxy_matrix.json")
    collapse = _read_json("artifacts/new_problem_preflight_001a/collapse_audit.json")

    assert set(matrix["candidates"]) == {"P1", "P2", "P3", "P4", "P5"}
    assert matrix["candidates"]["P1"]["verdict"] == "survives_as_primary_proxy_contract"
    assert matrix["candidates"]["P2"]["verdict"] == "survives_as_supporting_constraint"
    assert matrix["candidates"]["P3"]["verdict"] == "survives_as_supporting_constraint"
    assert matrix["candidates"]["P4"]["verdict"] == "constraint_only"
    assert matrix["candidates"]["P5"]["verdict"] == "boundary_note_only"

    required_questions = {
        "full_history_count_statistic_controls",
        "online_count_statistic_controls",
        "fsm_automaton_controls",
        "graph_cache_controls",
        "online_graph_cache_controls",
        "knn_episodic_retrieval_controls",
        "summary_statistic_controls",
        "causal_table_controls",
        "trace_only_replay",
        "behavior_only_replay",
        "random_representation",
        "shuffled_outcomes",
        "deletion_no_future_behavior_effect",
        "counterfactual_action_no_update_path_change",
        "posthoc_trace_generation",
        "resource_asymmetry",
    }
    assert required_questions.issubset(set(collapse["audit_questions"]))
    assert collapse["overall_collapse_audit_verdict"] == "survives_contract_only_with_mandatory_future_failure_gates"
    assert collapse["implementation_authorized"] is False


def test_new_problem_preflight_001a_contract_docs_have_required_boundaries():
    docs = [
        "docs/new_problem_preflight_001a/proxy_contract.md",
        "docs/new_problem_preflight_001a/intervention_contract.md",
        "docs/new_problem_preflight_001a/trace_replay_contract.md",
        "docs/new_problem_preflight_001a/control_adversary_contract.md",
        "docs/new_problem_preflight_001a/resource_contract.md",
        "docs/new_problem_preflight_001a/value_state_boundary.md",
        "docs/new_problem_preflight_001a/collapse_audit.md",
        "docs/new_problem_preflight_001a/claim_ceiling.md",
    ]
    text = "\n".join(_read_text(path) for path in docs)

    required_phrases = [
        "primary_axis = process / intervention",
        "future_behavior_effect_required = true",
        "trace-only replay cannot reproduce both trace and future behavior",
        "witness and controls must receive comparable resource budgets",
        "value_state = deferred",
        "emotion = forbidden",
        "full-history count/statistic controls",
        "graph/cache trace-generator controls",
        "MODEL_CLASS_RESET = not_authorized",
        "same_agent_bridge = blocked",
        "EGO_integration = not_authorized",
    ]
    for phrase in required_phrases:
        assert phrase in text

    forbidden_phrases = [
        "model_class_reset_authorized = true",
        "same_agent_bridge_authorized = true",
        "ego_integration_authorized = true",
        "mechanism_training_authorized = true",
        "mechanism_implementation_authorized = true",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in text


def test_new_problem_preflight_001a_no_implementation_paths_created():
    forbidden_paths = [
        "src/process_intervention_mechanism",
        "src/new_mechanism",
        "src/new_problem_preflight_001a",
    ]

    for relative_path in forbidden_paths:
        assert not (ROOT / relative_path).exists(), relative_path
