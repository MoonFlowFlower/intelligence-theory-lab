import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "action_conditioned_self_boundary_preflight_001a"
TASK_CARD_ID = "ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A"
ARTIFACT_DIR = ROOT / "artifacts" / TASK_ID
REPORT_PATH = ROOT / "docs" / "research" / f"{TASK_CARD_ID}.md"

REQUIRED_BASELINES = {
    "majority_baseline",
    "observation_only_classifier",
    "action_only_classifier",
    "exact_legal_tuple_lookup_with_majority_fallback",
    "nearest_neighbor_legal_observation",
    "transition_table_action_to_outcome",
    "graph_lookup_state_action_outcome",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "context_key_arithmetic_probe",
    "target_label_leakage_probe",
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
    "legal_oracle_report.json",
    "preflight_config.json",
    "claim_ceiling.json",
    "test_results.json",
    "trace.jsonl",
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


def test_config_task_card_boundary_and_surface_registry_are_predeclared():
    runner = _runner()

    config = runner.build_preflight_config()
    surface = runner.generate_surface(config)
    registry = runner.build_field_registry(surface, config)

    assert config["task_card_id"] == TASK_CARD_ID
    assert config["created_before_results"] is True
    assert config["thresholds"] == {
        "legal_oracle_min_accuracy": 0.80,
        "majority_baseline_max_accuracy": 0.35,
        "best_independent_baseline_max_accuracy": 0.55,
        "legal_oracle_min_margin_over_best_baseline": 0.25,
        "ablation_collapse_eps": 0.05,
    }
    assert set(config["baseline_inventory"]) == REQUIRED_BASELINES
    assert config["config_hash"] == runner.hash_preflight_config(config)

    assert surface["candidate_mechanism_implemented"] is False
    assert surface["mechanism_score_produced"] is False
    assert surface["task_distribution_frozen_before_results"] is True
    assert surface["same_state_different_action_pairs"]
    assert all(
        not pair["pair_id"].endswith(pair["episode_ids"][0])
        for pair in surface["same_state_different_action_pairs"]
    )

    assert registry["producer_function"] == "build_field_registry"
    assert registry["legal_forbidden_registry_exhaustive"] is True
    assert registry["unclassified_fields"] == []
    assert registry["forbidden_fields_in_legal_or_replay_bundle"] == []
    assert registry["answer_bearing_fields_in_legal_or_replay_bundle"] == []
    assert registry["forbidden_answer_aliases_present_in_clean_surface"] == []
    assert registry["metadata_scanned"] is True
    assert registry["serialized_state_scanned"] is True
    assert registry["replay_bundle_scanned"] is True
    assert registry["legal_tuple_deterministically_encodes_target"] is False


def test_admitted_surface_preflight_gates_without_candidate_or_mainline_path():
    runner = _runner()

    run = runner.execute_preflight(persist_artifacts=False)
    result = run["result"]
    baselines = run["baseline_comparison"]
    ablations = run["ablation_report"]

    assert result["verdict"] == "admitted_surface_preflight"
    assert result["current_layer"] == "engineering implementation / no-candidate surface-admission preflight only"
    assert result["mainline_integration_status"] == "none; offline local preflight only"
    assert result["enabled_status"] == "callable local preflight runner only; no mechanism path enabled"
    assert result["candidate_mechanism_implemented"] is False
    assert result["candidate_score_produced"] is False
    assert result["mechanism_score_produced"] is False
    assert result["gate5_bridge_runtime_or_ego_mainline_authorized"] is False

    assert result["legal_oracle_accuracy"] >= 0.80
    assert baselines["majority_baseline_accuracy"] <= 0.35
    assert baselines["best_independent_baseline"]["score"] <= 0.55
    assert result["legal_oracle_minus_best_independent_baseline"] >= 0.25
    assert set(baselines["invoked_baselines"]) == REQUIRED_BASELINES
    assert baselines["missing_baselines"] == []
    assert baselines["target_label_leakage_probe"]["clean_surface_score"] <= 0.35
    assert baselines["target_label_leakage_probe"]["positive_control_score"] == 1.0
    assert baselines["target_label_leakage_probe"]["guard_blocked_positive_control"] is True

    eps = run["preflight_config"]["thresholds"]["ablation_collapse_eps"]
    majority = baselines["majority_baseline_accuracy"]
    for ablation_id in (
        "no_action_ablation",
        "randomized_action_ablation",
        "action_label_shuffle_ablation",
        "counterfactual_pair_break_ablation",
        "observation_only_ablation",
    ):
        assert ablations[ablation_id]["reran_actual_episodes"] is True
        assert ablations[ablation_id]["accuracy"] <= majority + eps

    assert result["same_state_different_action_pairs_valid"] is True
    assert result["transition_graph_family_blocked"] is True
    assert result["context_key_arithmetic_probe_blocked"] is True


def test_leakage_positive_control_alias_fires_and_can_invalidate_harness():
    runner = _runner()

    run = runner.execute_preflight(persist_artifacts=False)
    leakage = run["leakage_scan_report"]

    assert leakage["producer_function"] == "run_leakage_scan"
    assert leakage["clean_surface_scan"]["passed"] is True
    assert leakage["clean_surface_scan"]["answer_bearing_fields_detected"] == []
    assert leakage["positive_control"]["alias_channel"] == "metadata.injected_answer_alias"
    assert leakage["positive_control"]["unguarded_alias_accuracy"] == 1.0
    assert leakage["positive_control"]["guard_blocked"] is True

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
    assert replay["prediction_match_rate"] == 1.0
    assert set(replay["excluded_fields"]) >= {
        "target_label",
        "hidden_controllability_label",
        "self_boundary_score",
        "serialized_answer_map",
        "metadata.injected_answer_alias",
    }

    shortcut = runner.execute_preflight(
        persist_artifacts=False,
        allow_stored_answer_replay=True,
    )
    assert shortcut["result"]["verdict"] == "invalid_harness"
    assert "replay_required_stored_answer_or_shortcut" in shortcut["result"]["stop_conditions_triggered"]


def test_provenance_covers_scores_and_rejects_static_verdict_records():
    runner = _runner()

    run = runner.execute_preflight(persist_artifacts=False)
    provenance = run["computed_evidence_provenance"]

    assert runner.verify_computed_evidence_provenance(provenance)["passed"] is True
    score_records = [record for record in provenance["records"] if record["metric"] == "accuracy"]
    assert {record["candidate_or_baseline_id"] for record in score_records} >= REQUIRED_BASELINES | {
        "legal_oracle",
        "no_action_ablation",
        "randomized_action_ablation",
        "action_label_shuffle_ablation",
        "counterfactual_pair_break_ablation",
        "observation_only_ablation",
    }

    for record in provenance["records"]:
        assert PROVENANCE_FIELDS.issubset(record)
        for field in PROVENANCE_FIELDS:
            assert record[field] not in (None, "", [], {})
        assert record["static_verdict_dictionary_used"] is False
        assert record["threshold_declared_before_results"] is True

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
            "command": "python -m pytest tests/test_action_conditioned_self_boundary_preflight_001a.py -q",
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

    result = json.loads((ARTIFACT_DIR / "result.json").read_text(encoding="utf-8"))
    readback = json.loads((ARTIFACT_DIR / "readback.json").read_text(encoding="utf-8"))
    assert result["verdict"] in {
        "admitted_surface_preflight",
        "refused_surface_preflight",
        "invalid_harness",
    }
    assert readback["result_json_parse_check"] == "passed"
    assert readback["old_ctsr_composite_artifacts_unchanged"] is True
    assert readback["old_ctsr_composite_source_files_unchanged"] is True
    assert readback["forbidden_files_modified"] == []

    report_text = report_path.read_text(encoding="utf-8")
    assert "Auto-Remote-Anchor: conditional" in report_text
    assert "No mechanism success claim is made." in report_text
    assert "No candidate mechanism was implemented." in report_text
    assert "fair simple baselines reached oracle-level accuracy" in report_text
