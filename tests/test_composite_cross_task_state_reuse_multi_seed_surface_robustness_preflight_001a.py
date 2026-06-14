import importlib
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_DIR = "composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a"
TASK_CARD_ID = "COMPOSITE-CROSS-TASK-STATE-REUSE-MULTI-SEED-SURFACE-ROBUSTNESS-PREFLIGHT-001A"
REPORT_NAME = "COMPOSITE-CROSS-TASK-STATE-REUSE-MULTI-SEED-SURFACE-ROBUSTNESS-PREFLIGHT-001A.md"

REQUIRED_ARTIFACTS = {
    "result.json",
    "fixture_batch_manifest.json",
    "baseline_probe_results.json",
    "update_masking_results.json",
    "field_access_audit.json",
    "positive_control_results.json",
    "source_boundary_readback.json",
    "claim_ceiling.json",
}

REQUIRED_BASELINES = {
    "independent_per_task_optimal_ensemble_no_shared_latent",
    "shared_latent_no_cross_task_transfer",
    "visible_feature_only_task_b_decoder",
    "static_formula_visible_field_decoder",
    "nearest_neighbor_or_table_lookup_probe",
    "identity_or_trace_order_probe",
}

PROVENANCE_FIELDS = {
    "producer_function",
    "input_fixture_id",
    "seed",
    "run_id",
    "baseline_name",
    "allowed_observation_fields",
    "forbidden_fields_checked",
    "field_access_audit_result",
    "computed_predictions",
    "per_fixture_score",
    "aggregate_score",
    "aggregation_method",
    "code_path_hash",
}


def _runner():
    module_path = SRC / TASK_DIR / "runner.py"
    assert module_path.exists(), "runner module not implemented"
    return importlib.import_module(f"{TASK_DIR}.runner")


def test_fixture_batch_generates_valid_diverse_multi_seed_surfaces_from_callable_generator():
    runner = _runner()

    batch = runner.generate_fixture_batch(fixture_count=12, seeds=[71001, 71002, 71003, 71004, 71005, 71006])

    assert batch["task_id"] == TASK_CARD_ID
    assert batch["producer_function"] == "generate_fixture_batch"
    assert batch["fixture_count"] == 12
    assert len(batch["seeds"]) >= 6
    assert len(batch["fixtures"]) == 12
    assert set(batch["task_family_pairings"]) >= {
        "self_boundary_controllability->viability_value_gated_prediction_action",
        "replay_consolidation->social_latent_inference",
    }

    structure_hashes = [row["fixture_structure_hash"] for row in batch["fixture_summaries"]]
    assert len(set(structure_hashes)) == len(structure_hashes)
    assert batch["near_duplicate_original_count"] == 0
    assert batch["valid_fixture_count"] == 12

    for summary in batch["fixture_summaries"]:
        assert summary["generated_from_existing_surface_generator"] is True
        assert summary["validator_passed"] is True
        assert summary["validator_blocking_reasons"] == []
        assert summary["seed"] in batch["seeds"]
        assert summary["latent_parameter_ids"]["train"]
        assert summary["latent_parameter_ids"]["heldout"]
        assert summary["task_family_ids"]
        assert summary["support_signatures"]["train"]
        assert summary["support_signatures"]["heldout"]
        assert summary["train_heldout_split_signatures"]
        assert summary["counterfactual_pair_ids"]
        assert summary["prediction_error_event_ids"]
        assert summary["shared_state_update_event_ids"]
        assert summary["task_b_action_dependency_ids"]
        assert summary["target_action_distribution"]
        assert summary["heldout_action_entropy_bits"] >= 1.5
        assert summary["action_distribution_degenerate"] is False


def test_required_baselines_execute_on_every_fixture_with_complete_aggregate_provenance():
    runner = _runner()
    batch = runner.generate_fixture_batch(fixture_count=12, seeds=[72001, 72002, 72003, 72004, 72005, 72006])

    probes = runner.run_baseline_probes(batch, run_id="unit_run_001")

    assert set(probes["baseline_names"]) == REQUIRED_BASELINES
    assert probes["fixture_count"] == 12
    assert set(probes["aggregate_results_by_name"]) == REQUIRED_BASELINES
    assert probes["aggregate_method"] == "mean per-fixture heldout accuracy"

    for baseline_name in REQUIRED_BASELINES:
        aggregate = probes["aggregate_results_by_name"][baseline_name]
        rows = [row for row in probes["per_fixture_results"] if row["baseline_name"] == baseline_name]
        assert len(rows) == 12
        assert math.isclose(
            aggregate["aggregate_score"],
            sum(row["per_fixture_score"] for row in rows) / len(rows),
        )
        assert aggregate["aggregate_score"] < runner.SOLVE_THRESHOLD
        assert aggregate["solves_aggregate"] is False
        assert aggregate["individual_solve_fixture_ids"] == []

        for row in rows:
            assert PROVENANCE_FIELDS.issubset(row)
            assert row["run_id"] == "unit_run_001"
            assert row["baseline_name"] == baseline_name
            assert row["producer_function"].endswith(baseline_name)
            assert row["allowed_observation_fields"]
            assert row["forbidden_fields_checked"]
            assert row["field_access_audit_result"]["violations"] == []
            assert row["computed_predictions"]
            assert row["aggregation_method"] == "heldout_accuracy"
            assert row["code_path_hash"]
            assert row["static_verdict_dictionary_used"] is False
            assert row["metadata_only"] is False


def test_update_masking_and_replay_recompute_task_b_actions_from_serialized_state():
    runner = _runner()
    batch = runner.generate_fixture_batch(fixture_count=12, seeds=[73001, 73002, 73003, 73004, 73005, 73006])

    masking = runner.run_update_masking(batch, run_id="unit_run_002")
    replay = runner.run_replay_recomputation(batch, run_id="unit_run_002")

    assert masking["fixture_count"] == 12
    assert masking["meaningful_effect_fixture_count"] == 12
    assert masking["aggregate_masking_effect_rate"] == 1.0
    for row in masking["per_fixture_results"]:
        assert row["candidate_ablation"] is False
        assert row["masked_task_b_actions"] != row["preserved_task_b_actions"]
        assert row["changed_action_count"] == row["heldout_case_count"]

    assert replay["fixture_count"] == 12
    assert replay["stored_answer_replay_used"] is False
    assert replay["all_expected_actions_recomputed"] is True
    for row in replay["per_fixture_results"]:
        assert row["producer_function"] == "run_replay_recomputation"
        assert row["input_fixture_id"]
        assert row["recomputed_from"] == "serialized_state_after + task_b.observation"
        assert row["stored_answer_fields_read"] == []
        assert row["mismatches"] == []


def test_field_access_and_positive_controls_block_illegal_or_degenerate_paths():
    runner = _runner()
    batch = runner.generate_fixture_batch(fixture_count=12, seeds=[74001, 74002, 74003, 74004, 74005, 74006])
    probes = runner.run_baseline_probes(batch, run_id="unit_run_003")

    audit = runner.build_field_access_audit(batch, probes, include_positive_controls=True)
    controls = runner.run_positive_controls()

    assert audit["baseline_access_violations"] == {}
    assert audit["positive_controls"]["illegal_field_access"]["blocked"] is True
    assert audit["positive_controls"]["illegal_field_access"]["illegal_accesses"] == ["hidden.task_b_target_action"]
    assert audit["positive_controls"]["stored_answer_replay_attempt"]["blocked"] is True
    assert audit["positive_controls"]["stored_answer_replay_attempt"]["illegal_accesses"] == ["task_b.post_update_action"]

    assert controls["all_positive_controls_failed"] is True
    assert controls["control_results"]["visible_feature_only_degenerate_fixture"]["failed_as_expected"] is True
    assert "task_b_visible_features_sufficient" in controls["control_results"][
        "visible_feature_only_degenerate_fixture"
    ]["observed_blocking_reasons"]
    assert controls["control_results"]["overlapping_support_fixture"]["failed_as_expected"] is True
    assert "overlapping_train_heldout_support" in controls["control_results"][
        "overlapping_support_fixture"
    ]["observed_blocking_reasons"]


def test_result_blocks_duplicate_or_degenerate_fixture_batches_without_weakening_baselines():
    runner = _runner()
    batch = runner.generate_fixture_batch(fixture_count=12, seeds=[75001, 75002, 75003, 75004, 75005, 75006])
    duplicate_batch = dict(batch)
    duplicate_batch["near_duplicate_original_count"] = 12
    duplicate_batch["fixture_summaries"] = [
        {**summary, "action_distribution_degenerate": True, "heldout_action_entropy_bits": 0.0}
        for summary in batch["fixture_summaries"]
    ]
    probes = runner.run_baseline_probes(batch, run_id="unit_run_004")
    masking = runner.run_update_masking(batch, run_id="unit_run_004")
    audit = runner.build_field_access_audit(batch, probes, include_positive_controls=True)
    controls = runner.run_positive_controls()
    source = runner.build_source_boundary_readback()
    guard = runner.build_forbidden_action_guard()

    result = runner.compute_result(
        fixture_batch_manifest=duplicate_batch,
        baseline_probe_results=probes,
        update_masking_results=masking,
        field_access_audit=audit,
        positive_control_results=controls,
        source_boundary_readback=source,
        forbidden_action_guard=guard,
        run_id="unit_run_004",
    )

    assert result["verdict"] == (
        "composite_cross_task_state_reuse_multi_seed_surface_robustness_preflight_001a_blocked_by_degenerate_action_distribution"
    )
    assert "near_duplicate_generated_fixtures" in result["stop_conditions_triggered"]
    assert "degenerate_action_distribution" in result["stop_conditions_triggered"]
    assert result["candidate_score_produced"] is False


def test_execute_preflight_writes_required_artifacts_report_and_claim_ceiling(tmp_path):
    runner = _runner()
    output_dir = tmp_path / TASK_DIR
    report_path = tmp_path / REPORT_NAME

    run = runner.execute_preflight(
        output_dir=output_dir,
        persist_artifacts=True,
        fixture_count=12,
        seeds=[76001, 76002, 76003, 76004, 76005, 76006],
    )
    written_report = runner.write_research_report(run, report_path=report_path)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in output_dir.glob("*.json")})
    for path in output_dir.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

    result = run["result"]
    assert result["task_id"] == TASK_CARD_ID
    assert result["current_layer"] == (
        "engineering implementation / evidence-governance / no-candidate multi-seed surface robustness preflight only"
    )
    assert result["mainline_integration_status"] == "not integrated"
    assert result["enabled_status"] == "callable local robustness runner only"
    assert "multiple fresh fixtures" in result["real_trigger_evidence"]
    assert result["candidate_code_created"] is False
    assert result["candidate_score_produced"] is False
    assert result["tournament_or_gate4_path_created"] is False
    assert result["runtime_bridge_admission_or_ego_mainline_path_created"] is False
    assert result["llm_rag_ui_companion_path_created"] is False

    ceiling = run["claim_ceiling"]
    assert ceiling["claim_ceiling"] == "No-candidate multi-seed surface-robustness preflight only."
    for forbidden_claim in [
        "mechanism validity",
        "Gate4 validity",
        "candidate behavior",
        "tournament outcome",
        "runtime readiness",
        "bridge/admission readiness",
        "agency",
        "subjectivity",
        "consciousness",
        "emotion",
        "autonomy",
        "companion readiness",
        "EGO readiness",
    ]:
        assert forbidden_claim in ceiling["forbidden_claims"]

    report_text = written_report.read_text(encoding="utf-8")
    assert "No-candidate multi-seed surface-robustness preflight only" in report_text
    assert "No mechanism validity" in report_text
    assert "Auto-Remote-Anchor: conditional" in report_text
