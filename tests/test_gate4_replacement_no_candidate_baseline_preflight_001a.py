import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "gate4_replacement_no_candidate_baseline_preflight_001a"
ARTIFACT_DIR = ROOT / "artifacts" / TASK_ID
REPORT_PATH = ROOT / "docs" / "research" / "GATE4-REPLACEMENT-NO-CANDIDATE-BASELINE-PREFLIGHT-001A.md"

REQUIRED_BASELINES = {
    "partner_id_lookup_baseline",
    "preference_table_baseline",
    "retrieval_baseline",
    "imitation_frequency_baseline",
    "order_k_history_baseline_k1",
    "order_k_history_baseline_k2",
    "static_majority_marginal_baseline",
    "generator_proxy_baseline",
    "oracle_shape_rule_baseline",
    "shuffled_linkage_control",
    "counterfactual_pair_baseline",
    "serialized_state_decoder",
    "full_bundle_decoder",
    "ngram_trace_lookup",
    "pair_count_frequency_baseline",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "query_capable_imitation_baseline",
}

REQUIRED_ARTIFACTS = {
    "result.json",
    "source_pin_readback.json",
    "preflight_config_locked_before_results.json",
    "preflight_config_hash_readback.json",
    "baseline_inventory.json",
    "baseline_results.json",
    "best_faithful_baseline.json",
    "threshold_invalidation_report.json",
    "leakage_scan_results.json",
    "leakage_positive_control_results.json",
    "replay_recomputation_results.json",
    "replay_corruption_results.json",
    "structural_control_results.json",
    "computed_evidence_provenance.json",
    "unused_input_blocker_scan.json",
    "no_candidate_code_scan.json",
    "forbidden_path_scan.json",
    "test_results.json",
    "claim_ceiling.json",
    "routing_recommendation.json",
    "negative_evidence_report.json",
    "blocker_readback.json",
}


def _runner():
    return importlib.import_module("gate4_replacement_no_candidate_baseline_preflight_001a.runner")


def test_preflight_config_is_hash_locked_before_results_and_threshold_edits_block(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path / TASK_ID, persist_artifacts=False)
    config = run["preflight_config_locked_before_results"]
    readback = run["preflight_config_hash_readback"]

    assert config["created_before_results"] is True
    assert config["task_family_proposal_id"] == "GATE4-REPLACEMENT-NO-CANDIDATE-BASELINE-PREFLIGHT-001A"
    assert set(config["baseline_inventory"]) == REQUIRED_BASELINES
    assert config["predeclared_invalidation_threshold"] == 0.8
    assert readback["config_hash_unchanged_after_results"] is True
    assert readback["config_hash"] == config["config_hash"]

    blocked = runner.execute_preflight(
        output_dir=tmp_path / "edited",
        persist_artifacts=False,
        mutate_threshold_after_results=True,
    )
    assert blocked["result"]["verdict"] == "no_candidate_baseline_preflight_blocked_by_provenance_failure_001a"
    assert "threshold_changed_after_results" in blocked["result"]["stop_conditions_triggered"]


def test_all_declared_baselines_are_callable_invoked_and_cheap_baseline_blocks(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path / TASK_ID, persist_artifacts=False)
    baseline_results = run["baseline_results"]
    best = run["best_faithful_baseline"]
    result = run["result"]

    assert set(baseline_results["invoked_baselines"]) == REQUIRED_BASELINES
    assert baseline_results["declared_count"] == len(REQUIRED_BASELINES)
    assert baseline_results["run_count"] == len(REQUIRED_BASELINES)
    assert all(row["callable_invoked"] for row in baseline_results["results"])
    assert all(row["score"] is not None for row in baseline_results["results"])
    assert best["baseline_id"] == "partner_id_lookup_baseline"
    assert best["score"] >= run["preflight_config_locked_before_results"]["predeclared_invalidation_threshold"]
    assert result["verdict"] == "no_candidate_baseline_preflight_blocked_by_cheap_baseline_001a"
    assert result["candidate_code_created"] is False
    assert result["candidate_score_produced"] is False
    assert result["gate4_validity_claimed"] is False


def test_missing_declared_baseline_and_unused_condition_block(tmp_path):
    runner = _runner()

    missing = runner.execute_preflight(
        output_dir=tmp_path / "missing",
        persist_artifacts=False,
        disabled_baselines=("graph_lookup",),
    )
    assert missing["result"]["verdict"] == "no_candidate_baseline_preflight_blocked_by_provenance_failure_001a"
    assert "unused_declared_baseline:graph_lookup" in missing["unused_input_blocker_scan"]["blocking_reasons"]

    unused = runner.execute_preflight(
        output_dir=tmp_path / "unused",
        persist_artifacts=False,
        skip_structural_control="corrupt_observation",
    )
    assert unused["result"]["verdict"] == "no_candidate_baseline_preflight_blocked_by_provenance_failure_001a"
    assert "unused_structural_control:corrupt_observation" in unused["unused_input_blocker_scan"]["blocking_reasons"]


def test_leakage_scanner_uses_positive_controls_before_clean_scan_is_trusted(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path / TASK_ID, persist_artifacts=False)
    positive = run["leakage_positive_control_results"]
    clean = run["leakage_scan_results"]

    assert positive["passed"] is True
    assert set(positive["detected_control_ids"]) == set(runner.LEAKAGE_CONTROL_IDS)
    assert clean["clean_bundle_scan_computed"] is True
    assert clean["clean_scan_trusted_after_positive_controls"] is True
    assert clean["verdict"] == "clean_no_literal_target_leak_detected"

    failed = runner.execute_preflight(
        output_dir=tmp_path / "failed_positive",
        persist_artifacts=False,
        disable_leakage_positive_control="injected_visible_label_leak",
    )
    assert failed["result"]["verdict"] == "no_candidate_baseline_preflight_blocked_by_leakage_001a"
    assert "positive_control_not_detected:injected_visible_label_leak" in failed["leakage_positive_control_results"]["blocking_reasons"]


def test_replay_recomputes_baseline_behavior_and_corruption_controls_fail(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path / TASK_ID, persist_artifacts=False)
    replay = run["replay_recomputation_results"]
    corruption = run["replay_corruption_results"]

    assert replay["passed"] is True
    assert replay["uses_stored_predictions_only"] is False
    assert replay["uses_hash_only_comparison"] is False
    assert set(replay["baseline_ids_recomputed"]) == REQUIRED_BASELINES
    assert corruption["state_corruption_failed_or_changed"] is True
    assert corruption["observation_corruption_failed_or_changed"] is True
    assert corruption["linkage_corruption_failed_or_changed"] is True

    shortcut = runner.execute_preflight(
        output_dir=tmp_path / "shortcut",
        persist_artifacts=False,
        allow_stored_prediction_replay=True,
    )
    assert shortcut["result"]["verdict"] == "no_candidate_baseline_preflight_blocked_by_replay_failure_001a"
    assert shortcut["replay_recomputation_results"]["uses_stored_predictions_only"] is True


def test_computed_provenance_rejects_static_scores_and_covers_every_score(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path / TASK_ID, persist_artifacts=False)
    provenance = run["computed_evidence_provenance"]

    assert runner.verify_computed_evidence_provenance(provenance)["passed"] is True
    score_records = [row for row in provenance["records"] if row["metric"] == "accuracy"]
    assert {row["candidate_or_baseline_id"] for row in score_records} >= REQUIRED_BASELINES
    for row in provenance["records"]:
        for field in runner.REQUIRED_PROVENANCE_FIELDS:
            assert field in row
            assert row[field] not in (None, "", [], {})

    static = json.loads(json.dumps(provenance))
    static["records"][0]["static_score_injection"] = True
    static["records"][0]["producer_function"] = "literal_static_report"
    assert runner.verify_computed_evidence_provenance(static)["passed"] is False


def test_candidate_absence_and_forbidden_path_scans_are_computed(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path / TASK_ID, persist_artifacts=False)

    assert run["no_candidate_code_scan"]["passed"] is True
    assert run["no_candidate_code_scan"]["candidate_entrypoints_found"] == []
    assert run["no_candidate_code_scan"]["candidate_scores_found"] == []
    assert run["forbidden_path_scan"]["passed"] is True
    assert run["forbidden_path_scan"]["forbidden_paths_touched"] == []
    assert run["result"]["mainline_integration_status"] == "not_mainline_integrated"
    assert run["result"]["enabled_status"] == "local_callable_preflight_runner_only"


def test_artifacts_and_research_report_are_written_and_parse(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(
        output_dir=ARTIFACT_DIR,
        persist_artifacts=True,
        test_result_readback={
            "command": "python -m pytest tests/test_gate4_replacement_no_candidate_baseline_preflight_001a.py -q",
            "exit_code": 0,
            "summary": "placeholder overwritten by final run",
        },
    )
    report_path = runner.write_research_report(run, report_path=REPORT_PATH)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    for path in ARTIFACT_DIR.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    report_text = report_path.read_text(encoding="utf-8")
    assert "No Gate4 validity claim is made." in report_text
    assert "Auto-Remote-Anchor: conditional" in report_text
    assert "not mainline-integrated" in report_text
