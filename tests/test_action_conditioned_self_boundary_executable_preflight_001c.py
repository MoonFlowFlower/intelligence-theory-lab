import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = (
    "ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001C-"
    "TRUE-LEARNED-FAIR-CAPACITY-CHALLENGE"
)
TASK_SLUG = "action_conditioned_self_boundary_executable_preflight_001c"
PARENT_AUDIT_SHA256 = "dfa3c3c0de34e3aacf3934d90693165b4a611c510b4cb2db0261d36e476e0c5a"

REQUIRED_BASELINES = {
    "transition_table_baseline",
    "fsm_baseline",
    "graph_cache_episodic_traversal_baseline",
    "action_effect_frequency_baseline",
    "random_baseline",
    "majority_baseline",
    "fitted_linear_no_boundary_model",
    "fitted_sequence_no_boundary_model",
    "fair_capacity_boundary_disabled_reference",
}

REQUIRED_ABLATIONS = {
    "freeze_boundary_update",
    "remove_action_conditioned_contingency",
    "remove_no_action_external_comparison",
    "shuffle_action_effect_linkage",
    "reset_state_before_probe",
    "boundary_update_noise_intervention",
}

REQUIRED_ARTIFACTS = {
    "result.json",
    "trace.jsonl",
    "baseline_comparison.json",
    "ablation_report.json",
    "replay_report.json",
    "leakage_scan.json",
    "learner_validity_controls.json",
    "provenance.json",
    "source_boundary_readback.json",
    "failure_manifest.json",
    "claim_ceiling.txt",
    "summary.md",
}

REQUIRED_PROVENANCE_FIELDS = {
    "producer_function",
    "input_hash",
    "run_id",
    "seed",
    "train_split_ids",
    "heldout_split_ids",
    "episode_ids",
    "aggregation_method",
    "code_path_hash",
    "model_class",
    "parameter_update_count",
    "baseline_path_name",
    "ablation_path_name",
    "leakage_scanner_path",
    "replay_path",
}


def _runner():
    return importlib.import_module(
        "action_conditioned_self_boundary_executable_preflight_001c.runner"
    )


def test_config_parent_boundary_and_generalization_split_are_real():
    runner = _runner()

    config = runner.build_challenge_config(ROOT)
    dataset = runner.generate_challenge_dataset(config)
    split = dataset["split_audit"]

    assert config["task_card_id"] == TASK_ID
    assert config["current_layer"] == (
        "engineering implementation / offline executable replacement challenge only"
    )
    assert config["mainline_integration_target"] == "none"
    assert config["enabled_status"] == "local offline module, tests, and artifact generation only"
    assert config["claim_ceiling"] == "offline executable replacement-challenge evidence only"
    assert config["auto_remote_anchor"] == "conditional"

    readback = config["source_boundary_readback"]
    assert readback["local_head"] == "bdf0b8cde59d8be9c8283d0af3f20799d4f36f7f"
    assert readback["branch"] == "codex/meta-theory-scaffold"
    assert readback["worktree_clean"] is True
    assert readback["local_tag_hash"] == readback["local_head"]
    assert readback["remote_branch_hash"] == readback["local_head"]
    assert readback["remote_tag_hash"] == readback["local_head"]
    assert readback["exact_parent_boundary_match"] is True
    assert readback["parent_hostile_audit_sha256"].lower() == PARENT_AUDIT_SHA256

    assert split["row_enumerable_from_train"] is False
    assert split["hidden_id_maps_to_target"] is False
    assert split["target_is_fixed_index_rule"] is False
    assert split["decoy_correlation_differs_between_train_and_heldout"] is True
    assert split["intervention_mapping_differs_under_rule_family"] is True
    assert split["ood_heldout_intervention_family_count"] >= 1
    assert split["target_entropy_bits"] >= 1.95
    assert split["majority_baseline_score"] <= 0.34

    train_combos = {tuple(row["combo_key"]) for row in dataset["train_examples"]}
    heldout_combos = {tuple(row["combo_key"]) for row in dataset["heldout_episodes"]}
    assert train_combos.isdisjoint(heldout_combos)

    for episode in dataset["heldout_episodes"]:
        legal = runner.legal_input_for_episode_001c(episode)
        serialized = json.dumps(legal, sort_keys=True)
        assert "target_channel" not in serialized
        assert "oracle_boundary_label" not in serialized
        assert "future_outcome" not in serialized


def test_learned_baselines_are_fitted_and_guarded_against_dummy_learning():
    runner = _runner()

    run = runner.execute_challenge(ROOT, persist_artifacts=False)
    result = run["result"]
    baselines = run["baseline_comparison"]
    controls = run["learner_validity_controls"]

    assert result["verdict"] == "blocked_by_fitted_no_boundary_learned_baseline_001c"
    assert "fitted_no_boundary_learned_baseline_matched_or_exceeded_reference" in result[
        "stop_conditions_triggered"
    ]
    assert result["mechanism_validity_claimed"] is False
    assert result["gate_bridge_runtime_or_ego_mainline_enabled"] is False

    assert set(baselines["invoked_baselines"]) == REQUIRED_BASELINES
    assert baselines["missing_baselines"] == []
    learned = baselines["learned_baseline_training"]
    for name in ("fitted_linear_no_boundary_model", "fitted_sequence_no_boundary_model"):
        record = learned[name]
        assert record["fit_called"] is True
        assert record["parameter_update_count"] > 0
        assert record["train_split_ids"]
        assert record["heldout_split_ids"]
        assert record["uses_explicit_boundary_state"] is False
        assert record["uses_answer_labels_at_inference"] is False

    assert controls["zero_update_guard"]["passed"] is True
    assert controls["constant_predictor_guard"]["passed"] is True
    assert controls["fit_removed_mutation_test"]["passed"] is True
    assert controls["learner_can_fit_leakage_positive_control"]["score"] >= 0.95
    assert controls["learner_can_fit_leakage_positive_control"]["exploited_contamination"] is True
    removed = controls["learner_fails_or_drops_when_discriminative_legal_features_removed"]
    assert removed["effect_marked"] is True
    assert removed["score_drop"] >= 0.20


def test_baselines_fair_capacity_and_ablations_are_callable_not_constant_stubs():
    runner = _runner()

    run = runner.execute_challenge(ROOT, persist_artifacts=False)
    scores = run["scores"]
    baselines = run["baseline_comparison"]
    ablations = run["ablation_report"]

    assert scores["reference_path"]["score"] == 1.0
    assert baselines["strongest_baseline"]["baseline_name"] in {
        "fitted_linear_no_boundary_model",
        "fitted_sequence_no_boundary_model",
        "fitted_knn_embedding_no_boundary_model",
    }
    assert baselines["strongest_baseline"]["score"] >= scores["reference_path"]["score"]
    assert baselines["fitted_learned_baseline_scores"]["fitted_linear_no_boundary_model"] >= 1.0

    fair = baselines["baseline_scores"]["fair_capacity_boundary_disabled_reference"]
    assert fair["score_source"] == "callable_computation"
    assert fair["disabled_component"] == "explicit_action_conditioned_boundary_update_persistence"
    assert fair["computed_intermediate_terms"] is True
    assert fair["returned_stale_prior_channel"] is False
    assert fair["hardcoded_wrong_channel"] is False

    assert set(ablations["invoked_ablations"]) == REQUIRED_ABLATIONS
    assert ablations["missing_ablations"] == []
    for name, record in ablations["ablation_scores"].items():
        assert record["producer_function"] == name
        assert record["score_source"] == "callable_computation"
        assert record["reran_behavior"] is True
        assert record["constant_output_stub"] is False
        assert record["hardcoded_failure_token"] is False
        assert record["unique_prediction_count"] > 1
        assert record["degradation_from_reference"] == round(
            scores["reference_path"]["score"] - record["score"], 6
        )

    for core_name in REQUIRED_ABLATIONS:
        assert ablations["ablation_scores"][core_name]["degradation_from_reference"] >= 0.20


def test_leakage_replay_provenance_and_artifact_generation_are_fail_able(tmp_path):
    runner = _runner()

    run = runner.execute_challenge(ROOT, output_dir=tmp_path, persist_artifacts=True)
    leakage = run["leakage_scan"]
    replay = run["replay_report"]
    provenance = run["provenance"]
    verification = runner.verify_computed_evidence_provenance_001c(provenance)

    assert leakage["producer_function"] == "run_leakage_scan_001c"
    assert leakage["normal_legal_input"]["blocked"] is False
    assert leakage["positive_controls_blocked"] == leakage["positive_controls_total"] == 6

    blocked = runner.execute_challenge(
        ROOT,
        persist_artifacts=False,
        disable_leakage_positive_controls=True,
    )
    assert blocked["result"]["verdict"] == "blocked_by_leakage_positive_control_failure_001c"

    assert replay["producer_function"] == "run_replay_001c"
    assert replay["passed"] is True
    assert replay["uses_stored_verdicts"] is False
    assert replay["uses_stored_scores"] is False
    assert replay["recomputed_from_serialized_state_and_observation"] is True
    assert {
        "boundary_update_reference_path",
        "fitted_linear_no_boundary_model",
        "fitted_sequence_no_boundary_model",
        "fair_capacity_boundary_disabled_reference",
        *REQUIRED_ABLATIONS,
    }.issubset(set(replay["recomputed_paths"]))

    assert verification["passed"] is True
    assert verification["static_score_records_detected"] == []
    assert verification["report_shaped_records_detected"] == []
    for record in provenance["score_records"]:
        assert REQUIRED_PROVENANCE_FIELDS.issubset(record)
        assert record["score_source"] == "callable_computation"
        assert record["static_literal_score"] is False
        assert record["report_only_score"] is False

    generated = {path.name for path in tmp_path.iterdir()}
    assert REQUIRED_ARTIFACTS.issubset(generated)
    for name in REQUIRED_ARTIFACTS - {"trace.jsonl", "claim_ceiling.txt", "summary.md"}:
        json.loads((tmp_path / name).read_text(encoding="utf-8"))
    assert (tmp_path / "trace.jsonl").read_text(encoding="utf-8").strip()
    assert "offline executable replacement-challenge evidence only" in (
        tmp_path / "claim_ceiling.txt"
    ).read_text(encoding="utf-8")
