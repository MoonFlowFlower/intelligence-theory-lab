import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "CMBC_COMPANION_PARAMETRIC_ACTION_INTERFACE_005_CONTRACT.md"
ARTIFACT_DIR = ROOT / "artifacts" / "cmbc_companion_parametric_action_interface_005_contract"

REQUIRED_ARTIFACTS = {
    "PARAMETRIC_ACTION_INTERFACE_005_STATUS.md",
    "candidate_option.schema.json",
    "parametric_selector_input.schema.json",
    "prediction_before_action_per_option.schema.json",
    "action_distribution_over_options.schema.json",
    "parametric_replay_trace.schema.json",
    "shadow_7_action_adapter_contract.md",
    "expanded_baseline_contract.md",
    "renderer_adapter_contract.md",
    "evidence_preservation_contract.md",
    "risk_register_005.md",
    "contract_manifest.json",
}

FORBIDDEN_SELECTOR_FIELDS = {
    "semantic_action_label",
    "semantic_action_labels",
    "semantic_action_family",
    "action_family_name",
    "action_family_names",
    "public_action_name",
    "public_action_names",
    "natural_language_description",
    "natural_language_descriptions",
    "rendered_text",
    "renderer_text",
    "hidden_future_state",
    "oracle_effect",
    "oracle_effects",
    "oracle_action_to_effect_table",
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


def test_parametric_action_interface_005_required_files_exist():
    assert DOC.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})


def test_parametric_action_interface_005_manifest_is_contract_only():
    manifest = load_json("contract_manifest.json")

    assert manifest["contract_id"] == "CMBC-COMPANION-PARAMETRIC-ACTION-INTERFACE-005-CONTRACT"
    assert manifest["verdict"] == "parametric_action_interface_contract_ready"
    assert manifest["authorized_scope"] == "contract_only"
    assert manifest["execution_authorized"] is False
    assert manifest["implementation_authorized"] is False
    assert manifest["selector_patch_authorized"] is False
    assert manifest["action_handles_patch_authorized"] is False
    assert manifest["threshold_change_authorized"] is False
    assert manifest["rag_baseline_weakening_authorized"] is False
    assert manifest["ego_migration"] == "no_go"
    assert manifest["real_companion_implementation"] == "not_authorized"
    assert manifest["proactive_messages"] == "not_authorized"
    assert manifest["llm_action_selection"] is False
    assert manifest["recommended_next_task"] == (
        "CMBC-COMPANION-PARAMETRIC-ACTION-INTERFACE-005-SHADOW-IMPLEMENT"
    )
    assert manifest["recommended_next_task_authorized"] is False


def test_candidate_option_schema_excludes_semantic_oracle_and_renderer_fields():
    schema = load_json("candidate_option.schema.json")

    assert schema["title"] == "CandidateOption"
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {
        "option_id",
        "allowed_observation_features",
        "predicted_effect_vector",
        "uncertainty",
        "prior_support_refs",
        "cost_risk_budget_features",
    }
    keys = set(flatten_keys(schema))
    assert keys.isdisjoint(FORBIDDEN_SELECTOR_FIELDS)
    assert "act_0" not in json.dumps(schema)
    assert "ACTION_HANDLES" not in json.dumps(schema)


def test_parametric_selector_input_supports_variable_n_without_fixed_action_ids():
    schema = load_json("parametric_selector_input.schema.json")
    candidate_options = schema["properties"]["candidate_options"]

    assert candidate_options["type"] == "array"
    assert candidate_options["minItems"] == 1
    assert "maxItems" not in candidate_options
    assert candidate_options["items"]["$ref"] == "candidate_option.schema.json"
    assert schema["properties"]["variable_n_contract"]["properties"]["supports_n_7"]["const"] is True
    assert schema["properties"]["variable_n_contract"]["properties"]["supports_n_gte_20"]["const"] is True
    assert "ACTION_HANDLES" not in json.dumps(schema)
    assert "act_0" not in json.dumps(schema)


def test_prediction_distribution_and_replay_schemas_are_option_keyed_and_replayable():
    prediction = load_json("prediction_before_action_per_option.schema.json")
    distribution = load_json("action_distribution_over_options.schema.json")
    replay = load_json("parametric_replay_trace.schema.json")

    assert prediction["properties"]["predictions"]["items"]["required"] == [
        "option_id",
        "predicted_effect_vector",
        "uncertainty",
        "prior_support_refs",
    ]
    assert distribution["properties"]["distribution"]["items"]["required"] == [
        "option_id",
        "probability",
        "rank",
    ]
    assert replay["properties"]["replay_rule"]["const"] == (
        "reconstruct selected_action by max probability over full option distribution"
    )
    assert replay["properties"]["candidate_options"]["items"]["$ref"] == "candidate_option.schema.json"
    assert replay["properties"]["action_distribution"]["$ref"] == (
        "action_distribution_over_options.schema.json"
    )


def test_005_contract_preserves_003_evidence_and_defines_future_paths():
    manifest = load_json("contract_manifest.json")
    doc = DOC.read_text(encoding="utf-8")

    assert manifest["n7_shadow_adapter_defined"] is True
    assert manifest["n_gte_20_future_execution_path_defined"] is True
    assert manifest["evidence_preservation_003"] == "preserve_as_small_action_set_bounded_evidence"
    assert manifest["claim_ceiling"] == (
        "parametric action interface contract readiness only; no implementation or execution evidence"
    )
    assert "Do not rewrite 003 as parametric evidence" in doc
    assert "ACTION_HANDLES = 20" in doc
    assert "boundary_violation" in manifest["allowed_verdicts"]


def test_005_expanded_baseline_and_renderer_contracts_are_shared_io_and_post_selection():
    baseline_doc = (ARTIFACT_DIR / "expanded_baseline_contract.md").read_text(encoding="utf-8")
    renderer_doc = (ARTIFACT_DIR / "renderer_adapter_contract.md").read_text(encoding="utf-8")
    preservation_doc = (ARTIFACT_DIR / "evidence_preservation_contract.md").read_text(encoding="utf-8")

    assert "same ParametricSelectorInput.candidate_options" in baseline_doc
    assert "baseline outputs are forbidden selector inputs" in baseline_doc
    assert "strictly post-selection" in renderer_doc
    assert "rendered text is never selector input" in renderer_doc
    assert "003 remains bounded small-action-set evidence" in preservation_doc
    assert "No selector patch is authorized" in preservation_doc
