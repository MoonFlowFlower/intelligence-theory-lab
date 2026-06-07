import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "CMBC_COMPANION_PARAMETRIC_ACTION_EXPANSION_006_CONTRACT.md"
ARTIFACT_DIR = ROOT / "artifacts" / "cmbc_companion_parametric_action_expansion_006_contract"

REQUIRED_ARTIFACTS = {
    "PARAMETRIC_ACTION_EXPANSION_006_STATUS.md",
    "parametric_action_expansion_006_contract.json",
    "expanded_baseline_contract_006.md",
    "evidence_preservation_006.md",
    "anti_fake_expansion_006.md",
    "boundary_scan_report.md",
    "risk_register_006.md",
    "contract_manifest.json",
}


def load_json(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def test_006_contract_files_exist():
    assert DOC.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})


def test_006_manifest_is_contract_only_and_preserves_boundaries():
    manifest = load_json("contract_manifest.json")

    assert manifest["contract_id"] == "CMBC-COMPANION-PARAMETRIC-ACTION-EXPANSION-006-CONTRACT"
    assert manifest["verdict"] == "parametric_action_expansion_006_contract_ready"
    assert manifest["authorized_scope"] == "contract_only"
    assert manifest["execution_authorized"] is False
    assert manifest["implementation_authorized"] is False
    assert manifest["selector_patch_authorized"] is False
    assert manifest["threshold_change_authorized"] is False
    assert manifest["rag_baseline_weakening_authorized"] is False
    assert manifest["fixed_action_handles_20_authorized"] is False
    assert manifest["ego_migration"] == "no_go"
    assert manifest["real_companion_implementation"] == "not_authorized"
    assert manifest["proactive_messages"] == "not_authorized"
    assert manifest["llm_action_selection"] is False
    assert manifest["recommended_next_task"] == (
        "CMBC-COMPANION-PARAMETRIC-ACTION-EXPANSION-006-EXECUTE"
    )
    assert manifest["recommended_next_task_authorized"] is False


def test_006_reuses_005_interface_and_requires_true_variable_n_expansion():
    contract = load_json("parametric_action_expansion_006_contract.json")

    assert contract["source_contracts"]["candidate_option_schema_ref"] == (
        "artifacts/cmbc_companion_parametric_action_interface_005_contract/candidate_option.schema.json"
    )
    assert contract["source_contracts"]["shadow_005_result_ref"] == (
        "artifacts/cmbc_companion_parametric_action_interface_005_shadow/shadow_result.json"
    )
    assert contract["source_contracts"]["free_input_003_reexecute_ref"] == (
        "artifacts/cmbc_companion_free_input_live_lab_003_reexecute/free_input_live_lab_003_reexecute_result.json"
    )

    expansion = contract["expanded_action_space"]
    assert expansion["candidate_option_count_min"] == 20
    assert expansion["candidate_option_count_max"] == 50
    assert expansion["variable_n_required"] is True
    assert expansion["fixed_twenty_action_table_forbidden"] is True
    assert expansion["fixed_action_handles_20_forbidden"] is True
    assert expansion["no_n_specific_branches"] is True
    assert expansion["forbidden_branch_patterns"] == ["if N == 7", "if N == 20"]


def test_006_future_execution_gates_match_predeclared_thresholds():
    contract = load_json("parametric_action_expansion_006_contract.json")
    gates = contract["minimum_future_execution_gates"]

    assert gates["candidate_option_count_min"] == 20
    assert gates["candidate_option_count_max"] == 50
    assert gates["semantic_label_visible_to_selector"] is False
    assert gates["public_action_name_visible_to_selector"] is False
    assert gates["rendered_text_visible_to_selector"] is False
    assert gates["natural_language_description_visible_to_selector"] is False
    assert gates["label_permutation_change_rate"] == 0.0
    assert gates["effect_swap_change_rate_min"] == 0.8
    assert gates["rag_causal_probe_match_rate_max"] == 0.5
    assert gates["strong_heuristic_causal_probe_match_rate_max"] == 0.5
    assert gates["expanded_contextual_heuristic_causal_probe_match_rate_max"] == 0.5
    assert gates["expanded_action_frequency_match_rate_max"] == 0.5
    assert gates["expanded_action_nearest_neighbor_match_rate_max"] == 0.5
    assert gates["behavior_only_replay_match_rate"] == 1.0
    assert gates["renderer_action_change_rate"] == 0.0
    assert gates["action_distribution_entropy_reported"] is True
    assert gates["dominant_action_rate_reported"] is True


def test_006_requires_probe_coverage_and_same_option_baselines():
    contract = load_json("parametric_action_expansion_006_contract.json")

    assert set(contract["required_probe_types"]) == {
        "label_permutation_invariance",
        "effect_swap_sensitivity",
        "same_text_different_causal_history",
        "supporting_prior_deletion",
        "outcome_perturbation",
        "feedback_admission_single_contradiction",
        "feedback_admission_repeated_feedback",
        "later_correction_context_narrowing",
        "renderer_adversarial_isolation",
        "behavior_only_replay_full_n_distribution",
    }
    assert contract["frozen_data_sources"]["reuse_frozen_20_turn_transcript"] is True
    assert contract["frozen_data_sources"]["reuse_stable_outcome_ledger"] is True
    assert contract["frozen_data_sources"]["reuse_003b_probe_pack"] is True
    assert contract["frozen_data_sources"]["new_data_requires_human_review"] is True

    baselines = contract["expanded_baselines"]
    assert baselines["receive_same_anonymous_candidate_options"] is True
    assert baselines["baseline_outputs_visible_to_selector"] is False
    assert baselines["required_baselines"] == [
        "RAGSummaryMemoryBaseline",
        "StrongHumanLikeHeuristicBaseline",
        "ExpandedContextualHeuristicBaseline",
        "ExpandedActionFrequencyBaseline",
        "ExpandedActionNearestNeighborBaseline",
    ]


def test_006_evidence_preservation_and_allowed_verdicts_are_strict():
    manifest = load_json("contract_manifest.json")
    contract = load_json("parametric_action_expansion_006_contract.json")
    doc = DOC.read_text(encoding="utf-8")

    assert contract["evidence_preservation"]["preserve_003_as"] == (
        "small-action-set free-input causal-probe evidence only"
    )
    assert contract["evidence_preservation"]["preserve_005_shadow_as"] == (
        "N=7 shadow compatibility evidence only"
    )
    assert contract["evidence_preservation"]["rewrite_003_or_005_as_expanded_evidence"] is False
    assert "003 remains small-action-set evidence" in doc
    assert "005 shadow remains N=7 compatibility evidence" in doc
    assert manifest["allowed_verdicts"] == [
        "parametric_action_expansion_006_contract_ready",
        "contract_incomplete",
        "fixed_twenty_action_table_detected",
        "semantic_leak_risk_unresolved",
        "expanded_baseline_contract_incomplete",
        "replay_contract_incomplete",
        "evidence_preservation_failed",
        "boundary_violation",
    ]


def test_006_boundary_scan_blocks_selector_label_renderer_and_oracle_leaks():
    contract = load_json("parametric_action_expansion_006_contract.json")
    boundary = (ARTIFACT_DIR / "boundary_scan_report.md").read_text(encoding="utf-8")

    forbidden_selector_fields = set(contract["selector_input_forbidden_fields"])
    assert {
        "semantic_action_labels",
        "public_action_names",
        "natural_language_descriptions",
        "action_family_names",
        "renderer_text",
        "oracle_effects",
        "evaluator_metrics",
        "baseline_outputs",
    }.issubset(forbidden_selector_fields)
    assert "boundary_violation = false" in boundary
    assert "selector_patch_authorized = false" in boundary
    assert "fixed ACTION_HANDLES = 20 authorized = false" in boundary
