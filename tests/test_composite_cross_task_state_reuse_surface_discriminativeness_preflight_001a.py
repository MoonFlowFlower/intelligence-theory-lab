import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_DIR = "composite_cross_task_state_reuse_surface_discriminativeness_preflight_001a"
TASK_CARD_ID = "COMPOSITE-CROSS-TASK-STATE-REUSE-SURFACE-DISCRIMINATIVENESS-PREFLIGHT-001A"
PARENT_ANCHOR = "00e1e747849b0a76c423726d00bbd79b94df0198"
FIXTURE_PATH = (
    ROOT
    / "artifacts"
    / "composite_cross_task_state_reuse_generative_heldout_surface_design_001a"
    / "valid_generated_surface_fixture.json"
)
REPORT_NAME = "COMPOSITE-CROSS-TASK-STATE-REUSE-SURFACE-DISCRIMINATIVENESS-PREFLIGHT-001A.md"

REQUIRED_BASELINES = {
    "independent_per_task_optimal_ensemble_no_shared_latent",
    "shared_latent_no_cross_task_transfer",
}
OPTIONAL_BASELINES = {
    "visible_feature_only_task_b_decoder",
    "trace_order_or_id_sanitized_retrieval_probe",
    "static_formula_visible_field_decoder",
}
REQUIRED_ARTIFACTS = {
    "result.json",
    "baseline_probe_results.json",
    "field_access_audit.json",
    "source_boundary_readback.json",
    "claim_ceiling.json",
}
PROVENANCE_FIELDS = {
    "producer_function",
    "input_fixture_path",
    "run_id",
    "seed",
    "baseline_name",
    "allowed_observation_fields",
    "forbidden_fields_checked",
    "computed_predictions",
    "aggregation_method",
    "code_path_hash",
}


def _runner():
    module_path = SRC / TASK_DIR / "runner.py"
    assert module_path.exists(), "runner module not implemented"
    return importlib.import_module(f"{TASK_DIR}.runner")


def test_required_baseline_probes_execute_from_existing_fixture_with_provenance():
    runner = _runner()

    probe_run = runner.run_baseline_probes(fixture_path=FIXTURE_PATH)

    assert probe_run["task_id"] == TASK_CARD_ID
    assert probe_run["input_fixture_path"].endswith(
        "artifacts/composite_cross_task_state_reuse_generative_heldout_surface_design_001a/valid_generated_surface_fixture.json"
    )
    assert probe_run["fixture_seed"] == 61001
    assert set(probe_run["baseline_results_by_name"]) >= REQUIRED_BASELINES | OPTIONAL_BASELINES

    for baseline_name in REQUIRED_BASELINES:
        row = probe_run["baseline_results_by_name"][baseline_name]
        assert PROVENANCE_FIELDS.issubset(row)
        assert row["producer_function"].endswith(baseline_name)
        assert row["input_fixture_path"] == probe_run["input_fixture_path"]
        assert row["run_id"] == probe_run["run_id"]
        assert row["seed"] == 61001
        assert row["baseline_name"] == baseline_name
        assert row["allowed_observation_fields"]
        assert row["forbidden_fields_checked"]
        assert row["computed_predictions"]
        assert row["aggregation_method"] == "heldout_accuracy"
        assert row["code_path_hash"]
        assert row["field_access_violations"] == []
        assert row["metadata_only"] is False
        assert row["static_verdict_dictionary_used"] is False


def test_dangerous_baselines_do_not_solve_and_masked_update_collapses_task_b_change():
    runner = _runner()

    probe_run = runner.run_baseline_probes(fixture_path=FIXTURE_PATH)
    independent = probe_run["baseline_results_by_name"][
        "independent_per_task_optimal_ensemble_no_shared_latent"
    ]
    shared_no_transfer = probe_run["baseline_results_by_name"]["shared_latent_no_cross_task_transfer"]
    ablation = probe_run["ablation_dependency_check"]

    assert independent["executed"] is True
    assert independent["solves_fixture"] is False
    assert independent["heldout_accuracy"] < probe_run["solve_threshold"]
    assert shared_no_transfer["executed"] is True
    assert shared_no_transfer["solves_fixture"] is False
    assert shared_no_transfer["heldout_accuracy"] < probe_run["solve_threshold"]

    assert ablation["producer_function"] == "build_cross_task_update_dependency_check"
    assert ablation["candidate_ablation"] is False
    assert ablation["preserved_update_dependency"]["task_b_actions"]
    assert ablation["masked_update_dependency"]["task_b_actions"]
    assert ablation["masked_update_dependency"]["task_b_actions"] != ablation["preserved_update_dependency"][
        "task_b_actions"
    ]
    assert ablation["cross_task_update_dependency_required"] is True


def test_field_access_audit_positive_control_blocks_forbidden_fields():
    runner = _runner()

    audit = runner.build_field_access_audit(fixture_path=FIXTURE_PATH, include_positive_control=True)

    assert audit["producer_function"] == "build_field_access_audit"
    assert audit["positive_control"]["blocked"] is True
    assert audit["positive_control"]["illegal_accesses"]
    assert "hidden.task_b_target_action" in audit["positive_control"]["illegal_accesses"]
    assert audit["baseline_access_violations"] == {}


def test_static_verdict_and_metadata_only_outputs_are_rejected():
    runner = _runner()

    static_audit = runner.detect_static_verdict_or_metadata_only(
        {
            "baseline_name": "independent_per_task_optimal_ensemble_no_shared_latent",
            "verdict": "pass",
            "computed_predictions": [],
        }
    )

    assert static_audit["blocked"] is True
    assert "missing_computed_predictions" in static_audit["blocking_reasons"]
    assert "static_verdict_without_metrics" in static_audit["blocking_reasons"]


def test_execute_preflight_writes_required_artifacts_report_and_source_boundary(tmp_path):
    runner = _runner()

    output_dir = tmp_path / TASK_DIR
    report_path = tmp_path / REPORT_NAME
    run = runner.execute_preflight(output_dir=output_dir, persist_artifacts=True)
    written_report = runner.write_research_report(run, report_path=report_path)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in output_dir.glob("*.json")})
    for path in output_dir.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

    source = run["source_boundary_readback"]
    assert source["expected_parent_anchor"] == PARENT_ANCHOR
    assert source["local_parent_tag_hash"] == PARENT_ANCHOR
    assert source["remote_parent_tag_hash"] == PARENT_ANCHOR
    assert source["parent_anchor_exact_match"] is True
    assert source["parent_anchor_is_ancestor_of_head"] is True

    result = run["result"]
    assert run["baseline_probe_results"]["run_id"] == run["run_id"]
    for row in run["baseline_probe_results"]["baseline_results"]:
        assert row["run_id"] == run["run_id"]
    assert result["verdict"] == "composite_cross_task_state_reuse_surface_discriminativeness_preflight_001a_pass"
    assert result["current_layer"] == "engineering implementation / evidence-governance / no-candidate surface-discriminativeness preflight only"
    assert result["mainline_integration_status"] == "not integrated"
    assert result["enabled_status"] == "callable local preflight runner only"
    assert "Callable baseline probes executed" in result["real_trigger_evidence"]
    assert result["candidate_code_created"] is False
    assert result["candidate_score_produced"] is False
    assert result["tournament_or_gate4_path_created"] is False
    assert result["runtime_bridge_admission_or_ego_mainline_path_created"] is False
    assert result["llm_rag_ui_companion_path_created"] is False
    assert result["stop_conditions_triggered"] == []

    report_text = written_report.read_text(encoding="utf-8")
    assert "No-candidate surface-discriminativeness preflight only" in report_text
    assert "independent_per_task_optimal_ensemble_no_shared_latent" in report_text
    assert "shared_latent_no_cross_task_transfer" in report_text
    assert "No mechanism validity" in report_text


def test_execute_preflight_uses_single_run_id_when_clock_ticks(monkeypatch):
    runner = _runner()
    ticks = iter(["2026-06-14T05:00:00Z", "2026-06-14T05:00:01Z"])

    monkeypatch.setattr(runner, "_now", lambda: next(ticks))

    run = runner.execute_preflight(output_dir=None, persist_artifacts=False)

    assert run["baseline_probe_results"]["run_id"] == run["run_id"]
    for row in run["baseline_probe_results"]["baseline_results"]:
        assert row["run_id"] == run["run_id"]


def test_no_candidate_score_or_runtime_paths_are_created():
    runner = _runner()

    run = runner.execute_preflight(output_dir=None, persist_artifacts=False)
    guard = run["forbidden_action_guard"]
    ceiling = run["claim_ceiling"]

    assert guard["candidate_code_created"] is False
    assert guard["candidate_score_produced"] is False
    assert guard["candidate_harness_created"] is False
    assert guard["tournament_or_gate4_path_created"] is False
    assert guard["runtime_bridge_admission_or_ego_mainline_path_created"] is False
    assert guard["llm_rag_ui_companion_path_created"] is False
    assert guard["forbidden_files_modified"] == []

    assert ceiling["claim_ceiling"] == "No-candidate surface-discriminativeness preflight only."
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
