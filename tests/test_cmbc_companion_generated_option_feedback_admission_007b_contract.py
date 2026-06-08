import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "CMBC_COMPANION_GENERATED_OPTION_FEEDBACK_ADMISSION_007B_CONTRACT.md"
ARTIFACT_DIR = ROOT / "artifacts" / "cmbc_companion_generated_option_feedback_admission_007b_contract"

REQUIRED_ARTIFACTS = {
    "GENERATED_OPTION_FEEDBACK_ADMISSION_007B_STATUS.md",
    "generated_option_feedback_admission_007B_contract.md",
    "pending_counterevidence.schema.json",
    "feedback_admission_state.schema.json",
    "admission_filtered_effect_vector.schema.json",
    "admission_aware_replay_trace.schema.json",
    "update_ordering_contract.md",
    "context_scope_contract.md",
    "uncertainty_update_contract.md",
    "evidence_preservation_contract.md",
    "stop_conditions.md",
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


def test_007b_contract_files_exist():
    assert DOC.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})


def test_007b_manifest_is_contract_only_and_preserves_boundaries():
    manifest = load_json("contract_manifest.json")

    assert manifest["contract_id"] == "CMBC-COMPANION-GENERATED-OPTION-FEEDBACK-ADMISSION-007B-CONTRACT"
    assert manifest["verdict"] == "generated_option_feedback_admission_007b_contract_ready"
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
    assert manifest["source_rca_verdict"] == "outcome_update_ordering_bug_confirmed"
    assert manifest["recommended_next_task"] == (
        "CMBC-COMPANION-GENERATED-OPTION-FEEDBACK-ADMISSION-007B-SHADOW"
    )
    assert manifest["recommended_next_task_authorized"] is False


def test_007b_contract_declares_required_objects_and_core_rules():
    manifest = load_json("contract_manifest.json")

    assert set(manifest["required_contract_objects"]) == {
        "PendingCounterevidenceRecord",
        "FeedbackAdmissionState",
        "GeneratedOptionFeedbackUpdateLedger",
        "ContextScopedFeedbackAdmission",
        "AdmissionFilteredEffectVector",
        "SelectorVisibleEffectVectorContract",
        "GeneratedOptionUncertaintyUpdateContract",
        "AdmissionAwareReplayTrace",
        "FeedbackAdmissionOrderingProof",
    }
    rules = manifest["core_rules"]
    assert "pending_counterevidence must not change selector-visible predicted_effect_vector" in rules
    assert "pending_counterevidence may change uncertainty / confidence / pending evidence state" in rules
    assert "admitted_context_counterevidence may change selector-visible predicted_effect_vector" in rules
    assert "selector must only see admission-filtered effect vectors" in rules
    assert "behavior-only replay and admission-aware replay must both be reported" in rules


def test_007b_pending_and_admission_state_schemas_block_visibility_leak():
    pending = load_json("pending_counterevidence.schema.json")
    state = load_json("feedback_admission_state.schema.json")

    assert pending["title"] == "PendingCounterevidenceRecord"
    assert pending["additionalProperties"] is False
    assert set(pending["required"]) == {
        "counterevidence_id",
        "option_id",
        "source_feedback_ref",
        "failure_mode",
        "context_scope",
        "status",
        "selector_visible_effect_update_allowed",
        "uncertainty_delta",
        "admission_requirements_remaining",
    }
    assert pending["properties"]["status"]["const"] == "pending_counterevidence"
    assert pending["properties"]["selector_visible_effect_update_allowed"]["const"] is False

    assert state["title"] == "FeedbackAdmissionState"
    assert state["additionalProperties"] is False
    assert state["properties"]["admission_status"]["enum"] == [
        "pending_counterevidence",
        "admitted_context_counterevidence",
        "rejected_counterevidence",
        "retired_counterevidence",
    ]
    assert state["properties"]["required_for_admission"]["properties"]["minimum_repeated_count"]["minimum"] == 2
    assert state["properties"]["selector_visible_effect_update_allowed"]["type"] == "boolean"


def test_007b_admission_filtered_effect_vector_schema_enforces_pending_no_effect_update():
    schema = load_json("admission_filtered_effect_vector.schema.json")

    assert schema["title"] == "AdmissionFilteredEffectVector"
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {
        "option_id",
        "base_effect_vector",
        "pending_counterevidence_effect_delta",
        "admitted_effect_delta",
        "selector_visible_predicted_effect_vector",
        "feedback_admission_status",
        "effect_vector_visibility_status",
        "ordering_proof_ref",
    }
    assert schema["properties"]["effect_vector_visibility_status"]["enum"] == [
        "base_only_pending_hidden",
        "admitted_delta_visible",
    ]
    keys = set(flatten_keys(schema))
    assert keys.isdisjoint(FORBIDDEN_SELECTOR_FIELDS)


def test_007b_admission_aware_replay_trace_contains_required_fields():
    trace = load_json("admission_aware_replay_trace.schema.json")

    assert trace["title"] == "AdmissionAwareReplayTrace"
    assert trace["additionalProperties"] is False
    assert set(trace["required"]) == {
        "trace_id",
        "proposal_id",
        "admission_decision_id",
        "feedback_admission_status",
        "context_scope",
        "effect_vector_visibility_status",
        "selector_visible_predicted_effect_vector",
        "action_distribution",
        "selected_option_id",
        "behavior_only_replay_match",
        "admission_aware_replay_match",
    }
    keys = set(flatten_keys(trace["properties"]["selector_visible_predicted_effect_vector"]))
    assert keys.isdisjoint(FORBIDDEN_SELECTOR_FIELDS)


def test_007b_update_ordering_context_uncertainty_docs_are_strict():
    update = (ARTIFACT_DIR / "update_ordering_contract.md").read_text(encoding="utf-8")
    context = (ARTIFACT_DIR / "context_scope_contract.md").read_text(encoding="utf-8")
    uncertainty = (ARTIFACT_DIR / "uncertainty_update_contract.md").read_text(encoding="utf-8")
    evidence = (ARTIFACT_DIR / "evidence_preservation_contract.md").read_text(encoding="utf-8")

    assert "pending_counterevidence MUST NOT modify selector-visible predicted_effect_vector" in update
    assert "admission-filtered effect vector" in update
    assert "context_scope must be explicit and traceable" in context
    assert "global feedback application is a stop condition" in context
    assert "pending feedback may reduce confidence or increase uncertainty" in uncertainty
    assert "single pending feedback cannot create a high-confidence selector-visible option" in uncertainty
    assert "003 remains small-action-set free-input causal-probe evidence only" in evidence
    assert "007-EXECUTE remains failed" in evidence


def test_007b_allowed_verdicts_stop_conditions_and_boundary_scan_are_complete():
    manifest = load_json("contract_manifest.json")
    stop = (ARTIFACT_DIR / "stop_conditions.md").read_text(encoding="utf-8")
    boundary = (ARTIFACT_DIR / "GENERATED_OPTION_FEEDBACK_ADMISSION_007B_STATUS.md").read_text(
        encoding="utf-8"
    )

    assert manifest["allowed_verdicts"] == [
        "generated_option_feedback_admission_007b_contract_ready",
        "contract_incomplete",
        "pending_counterevidence_visibility_unresolved",
        "context_scope_contract_incomplete",
        "admission_aware_replay_contract_incomplete",
        "uncertainty_update_contract_incomplete",
        "boundary_violation",
    ]
    assert "pending_counterevidence modifies selector-visible predicted_effect_vector" in stop
    assert "behavior-only replay or admission-aware replay missing" in stop
    assert "verdict = generated_option_feedback_admission_007b_contract_ready" in boundary
    assert "execution_authorized = false" in boundary
    assert "implementation_authorized = false" in boundary
    assert "EGO migration = no_go" in boundary
