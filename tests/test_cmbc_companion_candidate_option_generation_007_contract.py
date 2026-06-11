import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "CMBC_COMPANION_CANDIDATE_OPTION_GENERATION_007_CONTRACT.md"
ARTIFACT_DIR = ROOT / "artifacts" / "cmbc_companion_candidate_option_generation_007_contract"

REQUIRED_ARTIFACTS = {
    "CANDIDATE_OPTION_GENERATION_007_STATUS.md",
    "candidate_option_generation_007_contract.json",
    "candidate_option_proposal.schema.json",
    "option_admission_gate.schema.json",
    "admitted_candidate_option.schema.json",
    "option_lineage_trace.schema.json",
    "option_deduplication_report.schema.json",
    "option_retirement_report.schema.json",
    "option_composition_contract.md",
    "generator_selector_separation_contract.md",
    "option_evidence_support_contract.md",
    "replay_contract_for_generated_options.md",
    "baseline_contract_for_generated_options.md",
    "boundary_scan_report.md",
    "risk_register_007.md",
    "contract_manifest.json",
}

FORBIDDEN_SELECTOR_FIELDS = {
    "semantic_action_label",
    "semantic_action_labels",
    "public_action_name",
    "public_action_names",
    "natural_language_description",
    "natural_language_descriptions",
    "action_family_name",
    "action_family_names",
    "renderer_text",
    "rendered_text",
    "generator_prompt",
    "generator_rationale",
    "rag_text",
    "llm_output",
    "oracle_effect",
    "oracle_effects",
    "evaluator_metric",
    "evaluator_metrics",
    "baseline_output",
    "baseline_outputs",
}


def load_json(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def flatten_keys(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield key
            yield from flatten_keys(nested)
    elif isinstance(value, list):
        for item in value:
            yield from flatten_keys(item)


def test_007_contract_files_exist():
    assert DOC.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})


def test_007_manifest_is_contract_only_and_preserves_boundaries():
    manifest = load_json("contract_manifest.json")

    assert manifest["contract_id"] == "CMBC-COMPANION-CANDIDATE-OPTION-GENERATION-007-CONTRACT"
    assert manifest["verdict"] == "candidate_option_generation_contract_ready"
    assert manifest["authorized_scope"] == "contract_only"
    assert manifest["execution_authorized"] is False
    assert manifest["implementation_authorized"] is False
    assert manifest["generator_implementation_authorized"] is False
    assert manifest["selector_patch_authorized"] is False
    assert manifest["threshold_change_authorized"] is False
    assert manifest["rag_baseline_weakening_authorized"] is False
    assert manifest["ego_migration"] == "no_go"
    assert manifest["real_companion_implementation"] == "not_authorized"
    assert manifest["proactive_messages"] == "not_authorized"
    assert manifest["llm_action_selection"] is False
    assert manifest["recommended_next_task"] == "CMBC-COMPANION-CANDIDATE-OPTION-GENERATION-007-SHADOW"
    assert manifest["recommended_next_task_authorized"] is False


def test_007_contract_declares_all_required_objects_and_future_gates():
    contract = load_json("candidate_option_generation_007_contract.json")

    assert set(contract["required_contract_objects"]) == {
        "CandidateOptionProposal",
        "OptionAdmissionGate",
        "AdmittedCandidateOption",
        "OptionLineageTrace",
        "OptionDeduplicationReport",
        "OptionRetirementReport",
        "OptionCompositionContract",
        "GeneratorSelectorSeparationContract",
        "OptionEvidenceSupportContract",
        "ReplayContractForGeneratedOptions",
        "BaselineContractForGeneratedOptions",
    }
    gates = contract["minimum_future_execution_gates"]
    assert gates["generated_option_count_min"] == 20
    assert gates["admitted_option_count_min"] == 20
    assert gates["generator_selected_action"] is False
    assert gates["semantic_label_visible_to_selector"] is False
    assert gates["natural_language_description_visible_to_selector"] is False
    assert gates["option_lineage_coverage_rate"] == 1.0
    assert gates["option_replay_match_rate"] == 1.0
    assert gates["generator_baseline_action_match_rate_max"] == 0.5
    assert gates["rag_causal_probe_match_rate_max"] == 0.5
    assert gates["expanded_action_nearest_neighbor_match_rate_max"] == 0.5
    assert gates["renderer_action_change_rate"] == 0.0
    assert gates["outcome_update_changes_future_option_distribution"] is True


def test_007_proposal_schema_separates_generator_text_from_selector_visible_fields():
    proposal = load_json("candidate_option_proposal.schema.json")
    admitted = load_json("admitted_candidate_option.schema.json")

    assert proposal["title"] == "CandidateOptionProposal"
    assert proposal["additionalProperties"] is False
    assert set(proposal["required"]) == {
        "proposal_id",
        "generator_id",
        "proposed_option_id",
        "generator_visible_description",
        "proposed_effect_hypothesis",
        "source_context_refs",
        "proposal_uncertainty",
        "selector_visible_payload",
    }
    payload = proposal["properties"]["selector_visible_payload"]
    assert payload["additionalProperties"] is False
    payload_keys = set(flatten_keys(payload))
    assert payload_keys.isdisjoint(FORBIDDEN_SELECTOR_FIELDS)

    assert admitted["title"] == "AdmittedCandidateOption"
    assert admitted["additionalProperties"] is False
    assert "lineage_trace_ref" in admitted["required"]
    assert "evidence_support_ref" in admitted["required"]
    assert "uncertainty" in admitted["required"]
    admitted_keys = set(flatten_keys(admitted))
    assert admitted_keys.isdisjoint(FORBIDDEN_SELECTOR_FIELDS)


def test_007_admission_lineage_dedup_retirement_schemas_are_auditable():
    admission = load_json("option_admission_gate.schema.json")
    lineage = load_json("option_lineage_trace.schema.json")
    dedup = load_json("option_deduplication_report.schema.json")
    retirement = load_json("option_retirement_report.schema.json")

    assert admission["properties"]["gate_decision"]["enum"] == [
        "admit",
        "pending_counterevidence",
        "reject",
        "retire",
    ]
    assert "minimum_evidence_count" in admission["properties"]
    assert "weak_evidence_uncertainty_floor" in admission["properties"]

    assert set(lineage["required"]) == {
        "lineage_id",
        "proposal_id",
        "admitted_option_id",
        "source_context_refs",
        "source_outcome_refs",
        "admission_decision_ref",
        "deduplication_refs",
        "composition_refs",
        "retirement_refs",
    }
    assert dedup["properties"]["dedup_decision"]["enum"] == ["merge", "keep_distinct", "reject_duplicate"]
    assert retirement["properties"]["retirement_status"]["enum"] == [
        "active",
        "retired",
        "reversible_retired",
    ]
    assert retirement["properties"]["reversible"]["const"] is True


def test_007_generator_selector_separation_replay_and_baseline_docs_are_strict():
    separation = (ARTIFACT_DIR / "generator_selector_separation_contract.md").read_text(encoding="utf-8")
    replay = (ARTIFACT_DIR / "replay_contract_for_generated_options.md").read_text(encoding="utf-8")
    baselines = (ARTIFACT_DIR / "baseline_contract_for_generated_options.md").read_text(encoding="utf-8")
    evidence = (ARTIFACT_DIR / "option_evidence_support_contract.md").read_text(encoding="utf-8")

    assert "Generator may propose options but cannot select actions" in separation
    assert "Selector receives only admitted anonymous CandidateOptions" in separation
    assert "natural-language descriptions are forbidden selector-visible fields" in separation
    assert "semantic labels are forbidden selector-visible fields" in separation
    assert "option set and full option distribution" in replay
    assert "RAG / heuristic / generator baselines receive equivalent allowed inputs" in baselines
    assert "Every admitted option must have lineage and evidence support" in evidence
    assert "weak evidence must increase uncertainty" in evidence


def test_007_allowed_verdicts_and_boundary_scan_are_complete():
    manifest = load_json("contract_manifest.json")
    boundary = (ARTIFACT_DIR / "boundary_scan_report.md").read_text(encoding="utf-8")

    assert manifest["allowed_verdicts"] == [
        "candidate_option_generation_contract_ready",
        "generator_selector_boundary_incomplete",
        "semantic_leak_risk_unresolved",
        "option_lineage_contract_incomplete",
        "generated_option_replay_contract_incomplete",
        "baseline_contract_incomplete",
        "boundary_violation",
    ]
    assert "boundary_violation = false" in boundary
    assert "generator_selected_action = false" in boundary
    assert "generator_implementation_authorized = false" in boundary
    assert "LLM action selection = false" in boundary
    assert "EGO migration = no_go" in boundary
