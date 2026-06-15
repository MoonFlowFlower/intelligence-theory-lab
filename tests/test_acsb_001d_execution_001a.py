import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "ACSB-001D-BOUNDED-CODEX-EXECUTION-001A"
TASK_SLUG = "acsb_001d_execution_001a"
SOURCE_CARD_COMMIT = "45d7c1a0650cab4a963be51f723ad306db50e77b"
SOURCE_CARD_TAG = "remote-anchor-acsb-001d-card-minor-revision-r1-r5-001a-45d7c1a"
ROUTE_DECISION_COMMIT = "fb0129aebe760d25bf4051328cdbf9ed14095694"
ROUTE_DECISION_TAG = "remote-anchor-acsb-post-001c-route-decision-001a-fb0129a"

REQUIRED_BASELINES = {
    "single_observation_decoder",
    "label_only_decoder",
    "value_signature_decoder",
    "probe_observation_only_learned_model",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "action_effect_frequency_no_boundary_state",
    "fitted_linear_no_boundary_learner",
    "fitted_sequence_no_boundary_learner",
    "fitted_pure_python_mlp_no_boundary_learner",
    "embedding_nearest_neighbor_no_boundary_learner",
    "fair_capacity_disabled_reference",
    "oracle_leakage_positive_control",
}

REQUIRED_ABLATIONS = {
    "disable_persistence",
    "freeze_boundary_update",
    "reset_state_before_probe",
    "remove_action_conditioned_contingency",
    "remove_no_action_counterfactual",
    "shuffle_action_effect_linkage_preserve_marginals",
    "replace_boundary_state_with_recency_state",
    "remove_boundary_memory_from_legal_state",
}

REQUIRED_RIGGED_CAPACITY_CONTROLS = {
    "separate_selector_formula",
    "stale_prior_return",
    "constant_wrong_answer",
    "decoy_by_construction_selector",
    "random_fallback",
    "hardcoded_wrong_channel",
    "discarded_non_disabled_legal_evidence",
    "disable_persistence_ablation_path_divergence",
}

REQUIRED_LEAKAGE_CONTROLS = {
    "explicit_target_action_output_field",
    "oracle_boundary_label",
    "benign_answer_alias",
    "hidden_id_mapping_to_answer",
    "future_outcome_leakage",
    "constant_count_signature_encoding",
    "rank_contrast_one_hot_encoding",
    "hidden_deterministic_order",
    "filename_fixture_context_id_leakage",
}

REQUIRED_ARTIFACTS = {
    "result.json",
    "git_readback.json",
    "provenance.json",
    "score_report.json",
    "baseline_report.json",
    "ablation_report.json",
    "leakage_report.json",
    "row_enumerability_report.json",
    "rigged_capacity_controls_report.json",
    "callable_diff_report.json",
    "replay_report.json",
    "test_report.json",
    "claim_ceiling.txt",
    "readback.json",
}

REQUIRED_PROVENANCE_FIELDS = {
    "producer_function",
    "inputs",
    "run_id",
    "seed",
    "context_ids",
    "episode_ids",
    "aggregation",
    "code_path_hash",
    "source_card_commit",
    "canonical_anchor_verification_source",
}


def _runner():
    return importlib.import_module("acsb_001d_execution_001a.runner")


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_start_boundary_git_health_and_card_thresholds_are_extracted():
    runner = _runner()

    config = runner.build_execution_config(ROOT)
    git_health = runner.probe_git_health(ROOT, config)
    source_card = runner.extract_source_card_contract(ROOT)

    assert config["task_id"] == TASK_ID
    assert config["layer"] == "engineering implementation / isolated ACSB-001D execution evidence only"
    assert config["mainline_target"] == "none"
    assert config["enabled_status"] == "local isolated 001D runner/harness only"
    assert config["claim_ceiling"] == "bounded isolated ACSB-001D execution evidence only"
    assert config["auto_remote_anchor"] == "conditional"
    assert config["source_card_commit"] == SOURCE_CARD_COMMIT
    assert config["source_card_tag"] == SOURCE_CARD_TAG
    assert config["route_decision_commit"] == ROUTE_DECISION_COMMIT
    assert config["route_decision_tag"] == ROUTE_DECISION_TAG

    assert source_card["thresholds"] == {
        "epsilon_tie": 0.05,
        "minimum_survival_margin": 0.15,
        "reference_minimum_score": 0.80,
        "boundary_memory_causal_flip_floor": 0.25,
    }
    assert set(source_card["required_challenger_families"]) == REQUIRED_BASELINES
    assert set(source_card["required_ablations"]) == REQUIRED_ABLATIONS
    assert source_card["missing_or_ambiguous_thresholds"] == []

    assert git_health["git_index_parseable"] is True
    assert git_health["required_commit_objects_exist"] is True
    assert git_health["required_refs_or_tags_exist"] is True
    assert git_health["audited_worktree_files_equal_committed_blobs"] is True
    assert git_health["canonical_anchor_verification_source"] == "mount_local_repo"
    assert git_health["source_card_tag_commit"] == SOURCE_CARD_COMMIT
    assert git_health["route_decision_tag_commit"] == ROUTE_DECISION_COMMIT


def test_same_callable_capacity_reference_and_rigged_controls_are_fail_able():
    runner = _runner()

    run = runner.execute_challenge(ROOT, persist_artifacts=False)
    callable_diff = run["callable_diff_report"]
    rigged = run["rigged_capacity_controls_report"]

    assert callable_diff["passed"] is True
    assert callable_diff["full_reference_core_callable"] == callable_diff["capacity_disabled_core_callable"]
    assert callable_diff["capacity_disabled_path"] == callable_diff["disable_persistence_ablation_path"]
    assert callable_diff["declared_flag_diff"] == {
        "boundary_memory_read_enabled": [True, False],
        "boundary_memory_write_enabled": [True, False],
        "persistence_enabled": [True, False],
    }
    assert callable_diff["callable_diff_hash_used_as_sole_rig_control"] is False
    assert callable_diff["behavioral_negative_controls_passed"] is True

    assert set(rigged["positive_controls"]) == REQUIRED_RIGGED_CAPACITY_CONTROLS
    assert rigged["all_positive_controls_fired"] is True
    for mode, record in rigged["positive_controls"].items():
        assert record["blocked"] is True, mode
        assert record["expected_blocking_verdict"] == record["verdict"]

    separate = runner.build_rigged_capacity_mutant("separate_selector_formula")
    assert runner.scan_capacity_disabled_reference(separate)["verdict"] == (
        "blocked_by_capacity_reference_not_same_callable_family_001d"
    )
    stale = runner.build_rigged_capacity_mutant("stale_prior_return")
    assert runner.scan_capacity_disabled_reference(stale)["verdict"] == (
        "blocked_by_rigged_capacity_disabled_reference_001d"
    )


def test_dataset_split_leakage_and_row_enumerability_controls_fire():
    runner = _runner()

    config = runner.build_execution_config(ROOT)
    dataset = runner.generate_dataset(config)
    leakage = runner.run_leakage_scan(dataset, config)
    row_enum = runner.run_row_enumerability_scan(dataset, config)

    train_keys = {tuple(row["row_key_without_split"]) for row in dataset["train"]}
    heldout_keys = {tuple(row["row_key_without_split"]) for row in dataset["heldout"]}
    assert train_keys.isdisjoint(heldout_keys)
    assert row_enum["producer_function"] == "run_row_enumerability_scan"
    assert row_enum["clean_split"]["blocked"] is False
    assert row_enum["clean_split"]["heldout_exact_overlap_count"] == 0
    assert row_enum["clean_split"]["nearest_neighbor_enumerator_score"] <= (
        row_enum["clean_split"]["majority_score"] + config["thresholds"]["epsilon_tie"]
    )
    assert row_enum["positive_control"]["blocked"] is True
    assert row_enum["positive_control"]["verdict"] == "blocked_by_row_enumerable_heldout_001d"

    assert leakage["producer_function"] == "run_leakage_scan"
    assert leakage["clean_legal_input"]["blocked"] is False
    assert set(leakage["positive_controls"]) == REQUIRED_LEAKAGE_CONTROLS
    assert leakage["positive_controls_blocked"] == leakage["positive_controls_total"]
    for mode, record in leakage["positive_controls"].items():
        assert record["blocked"] is True, mode


def test_baselines_ablations_replay_and_provenance_are_callable():
    runner = _runner()

    run = runner.execute_challenge(ROOT, persist_artifacts=False)
    result = run["result"]
    scores = run["score_report"]
    baselines = run["baseline_report"]
    ablations = run["ablation_report"]
    replay = run["replay_report"]
    provenance = run["provenance"]

    assert result["verdict"] == "acsb_001d_execution_001a_bounded_negative_evidence"
    assert result["mainline_integration_status"] == "none"
    assert result["enabled_status"] == "local isolated 001D runner/harness only"
    assert result["001e_created_or_authorized"] is False
    assert result["forbidden_paths_touched"] == []

    assert scores["candidate_or_reference_score"]["score"] == 1.0
    assert scores["strongest_baseline_score"]["score"] == 1.0
    assert scores["capacity_disabled_score"]["score"] == 1.0
    assert scores["tested_reference_margin"] == 0.0
    assert scores["thresholds"]["minimum_survival_margin"] == 0.15

    assert set(baselines["invoked_baselines"]) == REQUIRED_BASELINES
    assert baselines["missing_required_challenger_families"] == []
    assert baselines["strongest_baseline"]["baseline_name"] in {
        "fitted_linear_no_boundary_learner",
        "fitted_pure_python_mlp_no_boundary_learner",
        "fitted_sequence_no_boundary_learner",
    }
    for name, record in baselines["baseline_scores"].items():
        assert record["producer_function"] == name
        assert record["score_source"] == "callable_computation"
        if name in baselines["learned_baselines"]:
            assert record["feature_parity"] == "same_legal_features_minus_boundary_memory"
            assert record["feature_impoverished"] is False

    assert set(ablations["invoked_ablations"]) == REQUIRED_ABLATIONS
    assert ablations["missing_ablations"] == []
    for name, record in ablations["ablation_scores"].items():
        assert record["producer_function"] == name
        assert record["reran_episodes_under_intervention"] is True
        assert record["score_source"] == "callable_computation"
        assert record["constant_output_stub"] is False
        assert record["unique_prediction_count"] > 1

    assert replay["producer_function"] == "run_replay"
    assert replay["passed"] is True
    assert replay["recomputed_from_serialized_state_and_observation"] is True
    assert replay["uses_stored_hashes_only"] is False
    assert replay["uses_stored_verdicts"] is False
    assert replay["missing_required_state_blocks_replay"] is True
    assert "full_reference" in replay["recomputed_paths"]
    assert REQUIRED_ABLATIONS.issubset(set(replay["recomputed_paths"]))

    verification = runner.verify_computed_evidence_provenance(provenance)
    assert verification["passed"] is True
    assert verification["static_score_records_detected"] == []
    for record in provenance["score_records"]:
        assert REQUIRED_PROVENANCE_FIELDS.issubset(record)
        assert record["score_source"] == "callable_computation"
        assert record["static_literal_score"] is False
        assert record["report_only_score"] is False
        assert record["frozen_seed_consumed"] is True
        assert record["train_contexts_consumed"] is True
        assert record["heldout_contexts_consumed"] is True
        assert record["counterfactual_pairs_consumed"] is True


def test_failure_paths_block_instead_of_returning_clean_reports():
    runner = _runner()

    assert runner.execute_challenge(
        ROOT,
        persist_artifacts=False,
        disable_leakage_positive_controls=True,
    )["result"]["verdict"] == "blocked_by_leakage_positive_control_not_firing_001d"
    assert runner.execute_challenge(
        ROOT,
        persist_artifacts=False,
        disable_row_positive_control=True,
    )["result"]["verdict"] == "blocked_by_row_enumerability_positive_control_not_firing_001d"
    assert runner.execute_challenge(
        ROOT,
        persist_artifacts=False,
        skip_git_health_probe=True,
    )["result"]["verdict"] == "blocked_by_missing_git_health_probe_001d"

    provenance = runner.execute_challenge(ROOT, persist_artifacts=False)["provenance"]
    static = json.loads(json.dumps(provenance))
    static["score_records"][0]["producer_function"] = "literal_score_report"
    static["score_records"][0]["score_source"] = "literal"
    static["score_records"][0]["static_literal_score"] = True
    assert runner.verify_computed_evidence_provenance(static)["verdict"] == (
        "blocked_by_static_literal_score_producer_001d"
    )

    forbidden = runner.detect_forbidden_path_mutations(
        [
            "src/acsb_001d_execution_001a/runner.py",
            "tests/test_acsb_001d_execution_001a.py",
            "docs/research/ACSB-001D-BOUNDED-CODEX-EXECUTION-001A.md",
            "artifacts/acsb_001d_execution_001a/result.json",
            "docs/research/SAME_AGENT_BRIDGE_PROTOCOL_001.md",
            "docs/research/ACSB-001E-NOT-ALLOWED.md",
        ]
    )
    assert forbidden["passed"] is False
    assert "docs/research/SAME_AGENT_BRIDGE_PROTOCOL_001.md" in forbidden["forbidden_paths_touched"]
    assert "docs/research/ACSB-001E-NOT-ALLOWED.md" in forbidden["forbidden_paths_touched"]
    assert forbidden["001e_created_or_authorized"] is True


def test_artifacts_are_written_parseable_and_isolated(tmp_path):
    runner = _runner()

    run = runner.execute_challenge(ROOT, output_dir=tmp_path, persist_artifacts=True)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt"}:
        _read_json(tmp_path / name)

    result = _read_json(tmp_path / "result.json")
    readback = _read_json(tmp_path / "readback.json")
    test_report = _read_json(tmp_path / "test_report.json")

    assert result["verdict"] == run["result"]["verdict"]
    assert result["codex_execution_authorized_scope"] == TASK_ID
    assert result["forbidden_paths_touched"] == []
    assert result["001e_created_or_authorized"] is False
    assert result["mainline_integration_status"] == "none"
    assert result["computed_evidence_provenance_status"] == "passed"
    assert readback["required_artifacts_present"] is True
    assert readback["json_parse_status"] == "all_required_json_parsed"
    assert readback["implementation_remained_isolated"] is True
    assert test_report["producer_function"] == "build_test_report"
    assert "pending_final_pytest_run" in test_report["summary"]

    assert (tmp_path / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == (
        "bounded isolated ACSB-001D execution evidence only; no ACSB general validity or "
        "invalidity, no mechanism validity, no Gate validity, no agency, autonomy, "
        "consciousness, emotion, subjectivity, runtime readiness, EGO readiness, stable user "
        "benefit, companion/product readiness, or mainline effect claim."
    )
