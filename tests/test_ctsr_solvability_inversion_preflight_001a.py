import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "ctsr_solvability_inversion_preflight_001a"
TASK_CARD_ID = "CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A"
ARTIFACT_DIR = ROOT / "artifacts" / TASK_ID
REPORT_PATH = ROOT / "docs" / "research" / "CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A.md"

REQUIRED_BASELINES = {
    "majority_baseline",
    "exact_legal_tuple_lookup_with_majority_fallback",
    "nearest_neighbor_legal_observation",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "observation_only_posthoc_classifier",
}

REQUIRED_ARTIFACTS = {
    "result.json",
    "readback.json",
    "surface_bundle.json",
    "field_registry.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_scan_report.json",
    "replay_report.json",
    "computed_evidence_provenance.json",
    "trace.jsonl",
    "claim_ceiling.json",
}

PROVENANCE_FIELDS = {
    "producer_function",
    "inputs",
    "run_id",
    "seed_ids",
    "context_ids",
    "episode_ids",
    "aggregation",
    "code_path_hash",
}


def _runner():
    module_path = SRC / TASK_ID / "runner.py"
    assert module_path.exists(), "runner module not implemented"
    return importlib.import_module(f"{TASK_ID}.runner")


def test_config_is_predeclared_and_surface_has_no_answer_bearing_fields():
    runner = _runner()

    config = runner.build_preflight_config()
    surface = runner.generate_surface(config)
    registry = runner.build_field_registry(surface)

    assert config["task_card_id"] == TASK_CARD_ID
    assert config["created_before_results"] is True
    assert config["thresholds"] == {
        "legal_oracle_min_accuracy": 0.8,
        "majority_baseline_max_accuracy": 0.3,
        "best_graph_lookup_observation_max_accuracy": 0.5,
        "legal_oracle_min_margin_over_best_baseline": 0.25,
        "carry_ablation_eps": 0.05,
    }
    assert config["masked_fallback_action"] in runner.ACTION_POOL
    assert set(config["baseline_inventory"]) == REQUIRED_BASELINES
    assert config["config_hash"] == runner.hash_preflight_config(config)

    assert registry["producer_function"] == "build_field_registry"
    assert registry["legal_forbidden_registry_exhaustive"] is True
    assert registry["unclassified_fields"] == []
    assert registry["answer_bearing_fields_in_legal_or_replay_bundle"] == []
    assert registry["forbidden_answer_aliases_present_in_clean_surface"] == []
    assert registry["serialized_state_after_present_in_replay_bundle"] is False
    assert registry["latent_action_binding_present_in_replay_bundle"] is False
    assert registry["max_legal_field_cardinality_ratio"] < 1.0
    assert registry["legal_discriminative_fields_not_unique_identifiers"] is True


def test_admitted_surface_preflight_gates_and_no_candidate_boundary():
    runner = _runner()

    run = runner.execute_preflight(persist_artifacts=False)
    result = run["result"]
    baselines = run["baseline_comparison"]
    ablation = run["ablation_report"]

    assert result["verdict"] == "admitted_surface_preflight"
    assert result["current_layer"] == "engineering implementation / no-candidate surface-admission preflight only"
    assert result["mainline_integration_status"] == "none; offline local preflight only"
    assert result["enabled_status"] == "callable local preflight runner only; no mechanism path enabled"
    assert result["candidate_mechanism_implemented"] is False
    assert result["candidate_score_produced"] is False
    assert result["mechanism_score_produced"] is False
    assert result["gate5_bridge_runtime_or_ego_mainline_authorized"] is False

    assert result["legal_oracle_accuracy"] >= 0.8
    assert baselines["majority_baseline_accuracy"] <= 0.3
    assert baselines["best_graph_cache_or_lookup_or_observation_baseline"]["score"] <= 0.5
    assert result["legal_oracle_minus_best_independent_baseline"] >= 0.25
    assert set(baselines["invoked_baselines"]) == REQUIRED_BASELINES
    assert baselines["missing_baselines"] == []

    eps = run["preflight_config"]["thresholds"]["carry_ablation_eps"]
    majority = baselines["majority_baseline_accuracy"]
    assert ablation["no_carry_ablation"]["accuracy"] <= majority + eps
    assert ablation["randomized_carry_ablation"]["accuracy"] <= majority + eps
    assert ablation["masking_fallback_in_action_pool"]["passed"] is True
    assert ablation["masking_fallback_in_action_pool"]["fallback_action"] in runner.ACTION_POOL
    assert ablation["episodes_rerun_actual"] is True


def test_leakage_positive_control_alias_fires_and_clean_surface_stays_clean():
    runner = _runner()

    run = runner.execute_preflight(persist_artifacts=False)
    leakage = run["leakage_scan_report"]

    assert leakage["producer_function"] == "run_leakage_scan"
    assert leakage["clean_surface_scan"]["passed"] is True
    assert leakage["clean_surface_scan"]["answer_bearing_fields_detected"] == []
    assert leakage["positive_control"]["alias_channel"] == "serialized_state_after.latent_action_binding"
    assert leakage["positive_control"]["unguarded_alias_accuracy"] == 1.0
    assert leakage["positive_control"]["guard_blocked"] is True
    assert leakage["positive_control"]["detected_illegal_accesses"] == [
        "serialized_state_after.latent_action_binding"
    ]

    failed = runner.execute_preflight(
        persist_artifacts=False,
        disable_leakage_positive_control=True,
    )
    assert failed["result"]["verdict"] == "invalid_harness"
    assert "leakage_positive_control_failed" in failed["result"]["stop_conditions_triggered"]


def test_replay_recomputes_from_forbidden_free_bundle_and_rejects_stored_answers():
    runner = _runner()

    run = runner.execute_preflight(persist_artifacts=False)
    replay = run["replay_report"]

    assert replay["producer_function"] == "run_replay"
    assert replay["passed"] is True
    assert replay["recomputed_from_forbidden_free_bundle"] is True
    assert replay["uses_stored_predictions_only"] is False
    assert replay["uses_hash_only_comparison"] is False
    assert replay["forbidden_fields_in_replay_bundle"] == []
    assert replay["excluded_fields"] >= [
        "target_action",
        "post_update_action",
        "hidden.task_b_target_action",
        "serialized_state_after.latent_action_binding",
    ]
    assert replay["prediction_match_rate"] == 1.0

    shortcut = runner.execute_preflight(
        persist_artifacts=False,
        allow_stored_answer_replay=True,
    )
    assert shortcut["result"]["verdict"] == "invalid_harness"
    assert "replay_required_stored_answer_or_shortcut" in shortcut["result"]["stop_conditions_triggered"]


def test_computed_provenance_covers_scores_and_rejects_static_literals():
    runner = _runner()

    run = runner.execute_preflight(persist_artifacts=False)
    provenance = run["computed_evidence_provenance"]

    assert runner.verify_computed_evidence_provenance(provenance)["passed"] is True
    score_records = [record for record in provenance["records"] if record["metric"] == "accuracy"]
    assert {record["candidate_or_baseline_id"] for record in score_records} >= REQUIRED_BASELINES | {
        "legal_oracle",
        "no_carry_ablation",
        "randomized_carry_ablation",
    }
    for record in provenance["records"]:
        assert PROVENANCE_FIELDS.issubset(record)
        for field in PROVENANCE_FIELDS:
            assert record[field] not in (None, "", [], {})
        assert record["static_verdict_dictionary_used"] is False

    static = json.loads(json.dumps(provenance))
    static["records"][0]["producer_function"] = "literal_static_report"
    static["records"][0]["static_verdict_dictionary_used"] = True
    assert runner.verify_computed_evidence_provenance(static)["passed"] is False


def test_artifacts_report_and_readback_are_written_and_parse():
    runner = _runner()

    run = runner.execute_preflight(
        output_dir=ARTIFACT_DIR,
        persist_artifacts=True,
        test_result_readback={
            "command": "python -m pytest tests/test_ctsr_solvability_inversion_preflight_001a.py -q",
            "exit_code": 0,
            "summary": "placeholder overwritten by final run",
        },
    )
    report_path = runner.write_research_report(run, report_path=REPORT_PATH)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    for path in ARTIFACT_DIR.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    trace_lines = (ARTIFACT_DIR / "trace.jsonl").read_text(encoding="utf-8").splitlines()
    assert trace_lines
    assert all(json.loads(line)["run_id"] == run["run_id"] for line in trace_lines)

    readback = json.loads((ARTIFACT_DIR / "readback.json").read_text(encoding="utf-8"))
    assert readback["old_frozen_artifacts_unchanged"] is True
    assert readback["old_source_files_unchanged"] is True
    assert readback["result_json_parse_check"] == "passed"
    assert readback["forbidden_files_modified"] == []

    report_text = report_path.read_text(encoding="utf-8")
    assert "Auto-Remote-Anchor: conditional" in report_text
    assert "No mechanism success claim is made." in report_text
    assert "No candidate mechanism was implemented." in report_text
