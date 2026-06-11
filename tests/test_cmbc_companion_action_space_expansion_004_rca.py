import json

from cmbc_companion.evals.action_space_expansion_004_rca import (
    ALLOWED_VERDICTS,
    run_action_space_expansion_004_rca,
)


REQUIRED_ARTIFACTS = {
    "ACTION_SPACE_EXPANSION_004_RCA_STATUS.md",
    "static_action_handle_dependency_audit.json",
    "selector_parametricity_audit.md",
    "replay_dependency_audit.json",
    "renderer_dependency_audit.md",
    "baseline_dependency_audit.md",
    "minimal_parametric_interface_proposal.md",
    "risk_register.md",
    "RCA_RESULT.json",
}


def test_action_space_expansion_004_rca_confirms_static_selector_bottleneck(tmp_path):
    result = run_action_space_expansion_004_rca(tmp_path)

    assert result["suite_id"] == "CMBC-COMPANION-ACTION-SPACE-EXPANSION-004-RCA"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "selector_static_action_handle_bottleneck_confirmed"
    assert result["source_failure"]["verdict"] == "small_action_set_only"
    assert result["source_failure"]["requested_candidate_action_count"] == 20
    assert result["source_failure"]["selector_visible_candidate_action_count"] == 7

    selector = result["selector_parametricity"]
    assert selector["selector_uses_static_action_handles"] is True
    assert selector["accepts_candidate_options_parameter"] is False
    assert selector["can_score_arbitrary_options"] is False
    assert selector["fit_effect_model_static_by_action"] is True
    assert selector["prediction_before_action_static_handles"] is True

    assert result["next_recommended_task"] == (
        "CMBC-COMPANION-PARAMETRIC-ACTION-INTERFACE-005-CONTRACT"
    )
    assert "small 7-action anonymous action set" in result["claim_after_rca"]


def test_action_space_expansion_004_rca_maps_dependency_surface(tmp_path):
    result = run_action_space_expansion_004_rca(tmp_path)

    audit = result["static_action_handle_dependency_audit"]
    assert audit["dependency_count"] >= 10
    assert any(
        item["symbol"] == "ACTION_HANDLES"
        and item["path"].endswith("verify_growth_loop.py")
        and item["classification"] == "primary_selector_bottleneck"
        for item in audit["dependencies"]
    )
    assert any(
        item["symbol"] == "PUBLIC_ACTION_NAMES"
        and item["classification"] == "post_selection_renderer_dependency"
        for item in audit["dependencies"]
    )

    replay = result["replay_dependency"]
    assert replay["replay_contract_blocks_expansion"] is False
    assert replay["upstream_trace_producer_uses_static_handles"] is True
    assert replay["behavior_only_replay_can_remain_parametric_if_trace_contains_distribution"] is True

    renderer = result["renderer_dependency"]
    assert renderer["renderer_static_dependency_blocks_expansion"] is False
    assert renderer["renderer_runs_after_selection"] is True
    assert renderer["requires_parametric_post_selection_renderer_adapter"] is True

    baselines = result["baseline_dependency"]
    assert baselines["baseline_contract_blocks_expansion"] is False
    assert baselines["existing_baselines_use_fixed_action_ids"] is True
    assert baselines["expanded_baseline_contract_required_before_execution"] is True


def test_action_space_expansion_004_rca_preserves_no_patch_boundaries_and_artifacts(tmp_path):
    result = run_action_space_expansion_004_rca(tmp_path)

    assert result["selector_patched"] is False
    assert result["action_handles_added"] is False
    assert result["thresholds_changed"] is False
    assert result["rag_baseline_weakened"] is False
    assert result["ego_migration"] == "no_go"
    assert result["real_companion_implementation"] == "not_authorized"
    assert result["proactive_messages"] == "not_authorized"
    assert result["llm_action_selection"] is False

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    with (tmp_path / "RCA_RESULT.json").open("r", encoding="utf-8") as fh:
        persisted = json.load(fh)
    assert persisted["verdict"] == result["verdict"]
    assert persisted["selector_patched"] is False
    assert persisted["action_handles_added"] is False
