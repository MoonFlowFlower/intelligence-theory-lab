import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

ARTIFACT_DIR = ROOT / "artifacts" / "gate4_001c_failure_preserving_repair_001c"

REQUIRED_ARTIFACTS = {
    "config.json",
    "run_manifest.json",
    "episode_schema.json",
    "episodes_train.jsonl",
    "episodes_heldout.jsonl",
    "counterfactual_pairs.jsonl",
    "candidate_trace.jsonl",
    "baseline_trace.jsonl",
    "ablation_trace.jsonl",
    "replay_report.json",
    "leakage_scan_report.json",
    "harness_challenger_input_bundle.json",
    "harness_challenger_report.json",
    "metric_provenance.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "protected_artifact_hashes_before.json",
    "protected_artifact_hashes_after.json",
    "protected_artifact_mutation_report.json",
    "result.json",
    "claim_ceiling.txt",
    "preflight_anchor_readback.json",
    "output_bundle_manifest.json",
    "failure_taxonomy.json",
    "authorization_matrix.json",
}

REQUIRED_BASELINES = {
    "frozen_state_baseline",
    "order2_history_baseline",
    "partner_id_table_baseline",
    "context_only_baseline",
    "preference_table_baseline",
    "retrieval_imitation_baseline",
    "trace_only_hygiene_baseline",
    "oracle_label_positive_control",
}

REQUIRED_ABLATIONS = {
    "no_state_update_ablation",
    "shuffled_feedback_ablation",
    "partner_identity_masked_ablation",
    "context_shift_removed_ablation",
    "counterfactual_pair_swapped_ablation",
    "serialized_state_zeroed_before_action_ablation",
}

PROVENANCE_FIELDS = {
    "producer_function",
    "producer_module",
    "code_path_hash",
    "input_artifacts",
    "input_artifact_hashes",
    "run_id",
    "seed",
    "episode_ids",
    "train_context_ids",
    "heldout_context_ids",
    "counterfactual_pair_ids",
    "aggregation_rule",
    "threshold_rule",
    "created_at_utc",
}


def _load_json(name: str):
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def _load_jsonl(name: str):
    return [
        json.loads(line)
        for line in (ARTIFACT_DIR / name).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_missing_baseline_positive_control_fails_with_taxonomy_verdict():
    from gate4_001c_failure_preserving_repair_001c import core

    report = core.check_baseline_invocations({"frozen_state_baseline"})

    assert report["passed"] is False
    assert report["verdict"] == "failed_missing_independent_baseline"
    assert "oracle_label_positive_control" in report["missing_baselines"]


def test_non_behavioral_replay_positive_control_fails_with_taxonomy_verdict():
    from gate4_001c_failure_preserving_repair_001c import core

    report = core.check_replay_contract(
        {
            "behavioral_recomputation": False,
            "hash_only_replay": True,
            "stored_actions_reused": True,
            "exact_match_rate": 1.0,
        }
    )

    assert report["passed"] is False
    assert report["verdict"] == "failed_replay_not_behavioral_recomputation"


def test_leakage_missed_positive_control_fails_with_taxonomy_verdict():
    from gate4_001c_failure_preserving_repair_001c import core

    cases = core.build_leakage_control_cases()
    cases[0]["content"] = "clean text without the sentinel"
    report = core.run_leakage_scan_cases(cases)

    assert report["passed"] is False
    assert report["verdict"] == "failed_leakage_scanner_not_fail_able"
    assert report["positive_control_detection_rate"] < 1.0


def test_metric_without_callable_provenance_fails_with_taxonomy_verdict():
    from gate4_001c_failure_preserving_repair_001c import core

    report = core.validate_metric_provenance_records(
        [{"metric_id": "bad_metric", "value": 0.5, "producer_function": "literal"}]
    )

    assert report["passed"] is False
    assert report["verdict"] == "failed_metric_without_callable_provenance"
    assert report["missing_fields"]["bad_metric"]


def test_required_artifact_files_exist_and_parse():
    missing = sorted(name for name in REQUIRED_ARTIFACTS if not (ARTIFACT_DIR / name).exists())
    assert missing == []

    for path in ARTIFACT_DIR.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

    for path in ARTIFACT_DIR.glob("*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                json.loads(line)

    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip()


def test_prerequisite_anchor_readback_artifact_records_exact_matches():
    readback = _load_json("preflight_anchor_readback.json")

    assert readback["starting_status"] == "## codex/meta-theory-scaffold"
    assert readback["starting_head"] == "43284ae960d08a2a3f8094f16b76e519ef451899"
    assert readback["verdict"] == "anchors_exact_match"
    assert readback["all_exact_matches"] is True
    assert all(item["exit_code"] == 0 for item in readback["checks"])
    assert all(item["exact_match"] is True for item in readback["checks"])


def test_episode_contract_counts_schema_and_counterfactual_pairs():
    schema = _load_json("episode_schema.json")
    train = _load_jsonl("episodes_train.jsonl")
    heldout = _load_jsonl("episodes_heldout.jsonl")
    pairs = _load_jsonl("counterfactual_pairs.jsonl")

    required_fields = set(schema["required_fields"])
    assert len(train) >= 800
    assert len(heldout) >= 800
    assert all(required_fields.issubset(record) for record in train + heldout)
    assert all(record["ground_truth_latent_label_access_allowed"] is False for record in train + heldout)
    assert all(record["train_or_heldout"] == "train" for record in train)
    assert all(record["train_or_heldout"] == "heldout" for record in heldout)
    assert len(pairs) == len(heldout)

    pair_by_source = {pair["source_episode_id"]: pair for pair in pairs}
    heldout_by_id = {record["episode_id"]: record for record in heldout}
    assert set(pair_by_source) == set(heldout_by_id)
    for episode_id, pair in pair_by_source.items():
        source = heldout_by_id[episode_id]
        target = heldout_by_id[pair["paired_episode_id"]]
        assert source["seed"] == target["seed"]
        assert source["context_id"] == target["context_id"]
        assert source["partner_id"] != target["partner_id"]
        assert source["ground_truth_latent_label"] != target["ground_truth_latent_label"]
        assert pair["matched_surface_observation_length"] is True


def test_candidate_and_all_baselines_were_invoked_on_same_heldout_set():
    result = _load_json("result.json")
    comparison = _load_json("baseline_comparison.json")
    baseline_trace = _load_jsonl("baseline_trace.jsonl")

    invoked = set(comparison["invoked_baselines"])
    assert REQUIRED_BASELINES == invoked
    assert comparison["missing_baselines"] == []
    assert comparison["same_heldout_episode_set"] is True
    assert {record["baseline_id"] for record in baseline_trace} == REQUIRED_BASELINES
    assert comparison["oracle_label_positive_control"]["competitor_baseline"] is False
    assert comparison["best_non_oracle_baseline"]["baseline_id"] != "oracle_label_positive_control"
    assert (
        result["candidate_score"]["value"]
        - comparison["best_non_oracle_baseline"]["score"]["value"]
        >= result["thresholds"]["candidate_margin_over_best_non_oracle_baseline"]
    )
    assert all(row["candidate_beats_best_baseline"] for row in result["per_context_scores"].values())
    assert all(row["candidate_beats_best_baseline"] for row in result["per_seed_scores"].values())


def test_all_ablations_were_invoked_as_real_reruns():
    report = _load_json("ablation_report.json")
    trace = _load_jsonl("ablation_trace.jsonl")

    assert set(report["invoked_ablations"]) == REQUIRED_ABLATIONS
    assert report["missing_ablations"] == []
    assert {record["ablation_id"] for record in trace} == REQUIRED_ABLATIONS
    for ablation in report["ablations"]:
        assert ablation["real_rerun"] is True
        assert ablation["post_hoc_filter"] is False
        assert ablation["run_id"] != report["candidate_run_id"]
        assert ablation["intervention_applied"] is True
        assert ablation["score"]["provenance"]["producer_function"]


def test_replay_recomputed_behavior_and_did_not_reuse_hashes_or_stored_actions():
    report = _load_json("replay_report.json")

    assert report["behavioral_recomputation"] is True
    assert report["hash_only_replay"] is False
    assert report["stored_actions_reused"] is False
    assert report["stored_verdicts_reused"] is False
    assert report["exact_match_rate"]["value"] == 1.0
    assert report["verdict"] == "replay_behavioral_recomputation_passed"
    assert PROVENANCE_FIELDS.issubset(report["exact_match_rate"]["provenance"])


def test_leakage_scanner_positive_controls_and_exclusions():
    report = _load_json("leakage_scan_report.json")

    required_classes = {
        "normal_included_path",
        "whitelist_looking_path",
        "allowlist_looking_path",
        "trusted_prefix_looking_path",
        "excluded_looking_path",
    }
    assert required_classes.issubset(set(report["positive_control_path_classes"]))
    assert report["positive_control_detection_rate"]["value"] == 1.0
    assert report["unconditional_clean_report"] is False
    assert report["broad_exemption_used"] is False
    for item in report["scanned_items"]:
        if item["path_class"] == "excluded_looking_path":
            assert item["status"] == "not_scanned"
            assert item["status"] != "clean"
            assert item["reason"]


def test_harness_protected_provenance_thresholds_authorization_and_contamination_guards():
    result = _load_json("result.json")
    harness = _load_json("harness_challenger_report.json")
    mutation = _load_json("protected_artifact_mutation_report.json")
    provenance = _load_json("metric_provenance.json")
    taxonomy = _load_json("failure_taxonomy.json")
    authorization = _load_json("authorization_matrix.json")
    manifest = _load_json("run_manifest.json")

    assert harness["producer_function"] == "evaluate_bundle"
    assert harness["admissibility_class"] != "rejected_false_pass_risk"
    assert harness["detected_pattern_categories"] == []
    assert mutation["mutation_violation_count"]["value"] == 0
    assert mutation["verdict"] == "protected_artifacts_unchanged"
    assert result["metric_provenance_result"]["passed"] is True
    assert provenance["validation"]["passed"] is True
    assert all(PROVENANCE_FIELDS.issubset(record) for record in provenance["records"])
    assert result["thresholds_predeclared"] is True
    assert result["thresholds_changed_after_execution_began"] is False
    assert set(taxonomy["future_verdicts"]).issuperset(
        {
            "passed_bounded_gate4_001c_execution_preflight",
            "failed_missing_independent_baseline",
            "failed_replay_not_behavioral_recomputation",
            "failed_leakage_scanner_not_fail_able",
            "failed_metric_without_callable_provenance",
            "failed_provisional_commit_contamination",
        }
    )
    assert all(value is False for value in authorization["authorization_flags"].values())
    assert result["provisional_commit_contamination"]["used"] is False
    assert manifest["provisional_commit"] == "d7b5b7a33cc68cbe7e3ca0960b99e0082e1ac728"
    assert manifest["provisional_commit_use"] == {
        "restored": False,
        "read": False,
        "copied": False,
        "imported": False,
        "cherry_picked": False,
        "merged": False,
        "used": False,
    }
