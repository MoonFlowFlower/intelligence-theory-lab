import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "CMBC_COMPANION_LONGITUDINAL_GENERATED_OPTIONS_008_CONTRACT.md"
ARTIFACT_DIR = ROOT / "artifacts" / "cmbc_companion_longitudinal_generated_options_008_contract"

REQUIRED_ARTIFACTS = {
    "LONGITUDINAL_GENERATED_OPTIONS_008_CONTRACT_STATUS.md",
    "longitudinal_generated_options_008_contract.json",
    "longitudinal_case_matrix_008.json",
    "multi_session_lifecycle_contract_008.md",
    "feedback_inheritance_contract_008.md",
    "lineage_deletion_perturbation_contract_008.md",
    "generated_option_baseline_contract_008.md",
    "replay_renderer_contract_008.md",
    "evidence_preservation_008.md",
    "stop_conditions_008.md",
    "risk_register_008.md",
    "contract_manifest.json",
}


def load_json(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def test_008_contract_files_exist():
    assert DOC.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})


def test_008_manifest_is_contract_only_and_preserves_authorization_boundary():
    manifest = load_json("contract_manifest.json")

    assert manifest["contract_id"] == "CMBC-COMPANION-LONGITUDINAL-GENERATED-OPTIONS-008-CONTRACT"
    assert manifest["verdict"] == "longitudinal_generated_options_008_contract_ready"
    assert manifest["authorized_scope"] == "contract_only"
    assert manifest["execution_authorized"] is False
    assert manifest["implementation_authorized"] is False
    assert manifest["selector_patch_authorized"] is False
    assert manifest["threshold_change_authorized"] is False
    assert manifest["rag_baseline_weakening_authorized"] is False
    assert manifest["ego_migration"] == "no_go"
    assert manifest["real_companion_implementation"] == "not_authorized"
    assert manifest["proactive_messages"] == "not_authorized"
    assert manifest["llm_action_selection"] is False
    assert manifest["recommended_next_task"] == (
        "CMBC-COMPANION-LONGITUDINAL-GENERATED-OPTIONS-008-EXECUTE"
    )
    assert manifest["recommended_next_task_authorized"] is False


def test_008_contract_requires_multisession_generated_option_lifecycle():
    contract = load_json("longitudinal_generated_options_008_contract.json")

    assert contract["source_evidence"]["source_007_redteam_execute_verdict"] == (
        "generated_option_007_redteam_bounded_pass"
    )
    assert contract["source_evidence"]["source_007_redteam_execute_ref"] == (
        "artifacts/cmbc_companion_candidate_option_generation_007_redteam_execute/"
        "candidate_option_generation_007_redteam_execute_result.json"
    )

    lifecycle = contract["multi_session_lifecycle"]
    assert lifecycle["session_count_min"] == 4
    assert lifecycle["total_turn_count_min"] == 24
    assert lifecycle["generated_option_count_cumulative_min"] == 20
    assert lifecycle["admitted_option_count_current_min"] == 20
    assert lifecycle["requires_creation"] is True
    assert lifecycle["requires_deduplication"] is True
    assert lifecycle["requires_composition"] is True
    assert lifecycle["requires_retirement"] is True
    assert lifecycle["requires_retirement_reversibility"] is True
    assert lifecycle["requires_feedback_inheritance"] is True
    assert lifecycle["requires_source_deletion"] is True
    assert lifecycle["requires_outcome_perturbation"] is True


def test_008_future_gates_cover_lifecycle_feedback_replay_and_baselines():
    gates = load_json("longitudinal_generated_options_008_contract.json")[
        "minimum_future_execution_gates"
    ]

    assert gates["session_count_min"] == 4
    assert gates["total_turn_count_min"] == 24
    assert gates["generated_option_count_cumulative_min"] == 20
    assert gates["admitted_option_count_current_min"] == 20
    assert gates["option_creation_event_count_min"] >= 4
    assert gates["option_retirement_event_count_min"] >= 2
    assert gates["option_lineage_coverage_rate"] == 1.0
    assert gates["feedback_inheritance_coverage_rate"] == 1.0
    assert gates["context_scoped_feedback_admission_rate"] == 1.0
    assert gates["near_duplicate_bypass_rate"] == 0.0
    assert gates["retired_option_selected_rate"] == 0.0
    assert gates["retired_option_reactivation_traceable"] is True
    assert gates["source_deletion_effect"] is True
    assert gates["outcome_perturbation_effect"] is True
    assert gates["rag_longitudinal_match_rate_max"] == 0.5
    assert gates["expanded_nearest_neighbor_longitudinal_match_rate_max"] == 0.5
    assert gates["frequency_longitudinal_match_rate_max"] == 0.5
    assert gates["recency_longitudinal_match_rate_max"] == 0.5
    assert gates["behavior_only_replay_match_rate"] == 1.0
    assert gates["admission_aware_replay_match_rate"] == 1.0
    assert gates["option_lifecycle_replay_match_rate"] == 1.0
    assert gates["renderer_action_change_rate"] == 0.0


def test_008_case_matrix_covers_required_focus_without_execution():
    matrix = load_json("longitudinal_case_matrix_008.json")

    assert matrix["contract_id"] == "CMBC-COMPANION-LONGITUDINAL-GENERATED-OPTIONS-008-CONTRACT"
    assert matrix["case_count_minimum"] == 30
    assert len(matrix["families"]) == 10
    assert {family["family_id"] for family in matrix["families"]} == {
        "multi_session_option_lifecycle",
        "option_creation_retirement_reactivation",
        "lineage_source_deletion",
        "feedback_inheritance_across_generated_options",
        "near_duplicate_prevention_over_time",
        "repeated_context_scoped_feedback_admission",
        "generated_option_composition",
        "longitudinal_baseline_resistance",
        "behavior_admission_lifecycle_replay",
        "renderer_adversarial_isolation",
    }
    assert all(family["minimum_cases"] >= 3 for family in matrix["families"])


def test_008_evidence_preservation_and_allowed_verdicts_are_strict():
    manifest = load_json("contract_manifest.json")
    contract = load_json("longitudinal_generated_options_008_contract.json")
    doc = DOC.read_text(encoding="utf-8")

    assert contract["evidence_preservation"]["preserve_003_as"] == (
        "small-action-set free-input causal-probe evidence only"
    )
    assert contract["evidence_preservation"]["preserve_005_as"] == (
        "N=7 parametric shadow compatibility evidence only"
    )
    assert contract["evidence_preservation"]["preserve_006_as"] == (
        "bounded N=24 prebuilt CandidateOption evidence only"
    )
    assert contract["evidence_preservation"]["preserve_failed_007_execute_as"] == (
        "failed generated-option execution evidence"
    )
    assert contract["evidence_preservation"]["rewrite_prior_evidence_as_008_evidence"] is False
    assert "003 / 005 / 006 / 007 evidence is not rewritten" in doc
    assert manifest["allowed_verdicts"] == [
        "longitudinal_generated_options_008_contract_ready",
        "contract_incomplete",
        "longitudinal_lifecycle_contract_incomplete",
        "feedback_inheritance_contract_incomplete",
        "source_deletion_contract_incomplete",
        "dedup_retirement_contract_incomplete",
        "baseline_contract_incomplete",
        "replay_contract_incomplete",
        "semantic_leak_risk_unresolved",
        "evidence_preservation_failed",
        "boundary_violation",
    ]


def test_008_selector_visible_boundary_blocks_semantic_renderer_and_oracle_leaks():
    contract = load_json("longitudinal_generated_options_008_contract.json")
    stop_conditions = (ARTIFACT_DIR / "stop_conditions_008.md").read_text(encoding="utf-8")

    forbidden_selector_fields = set(contract["selector_input_forbidden_fields"])
    assert {
        "semantic_action_labels",
        "public_action_names",
        "action_family_names",
        "natural_language_descriptions",
        "generator_prompts_or_rationales",
        "RAG_text_or_memory_summaries",
        "renderer_text",
        "LLM_output",
        "hidden_future_state",
        "oracle_effects",
        "evaluator_metrics",
        "baseline_outputs",
    }.issubset(forbidden_selector_fields)
    assert "selector_patch_authorized = false" in stop_conditions
    assert "threshold_change_authorized = false" in stop_conditions
    assert "EGO migration = no_go" in stop_conditions
