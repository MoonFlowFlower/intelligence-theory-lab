import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

ARTIFACT_DIR = ROOT / "artifacts" / "gate4_001c_execution_repair_rerun_001e"

REQUIRED_FILES = {
    "result.json",
    "output_bundle_manifest.json",
    "computed_provenance.json",
    "harness_report.json",
    "harness_positive_control_report.json",
    "leakage_scan_report.json",
    "leakage_positive_control_report.json",
    "baseline_report.json",
    "count_table_challenger_report.json",
    "retrieval_normalization_report.json",
    "ablation_semantic_binding_report.json",
    "replay_full_state_report.json",
    "negative_evidence_policy_application.json",
    "protected_artifact_guard.json",
    "test_report.json",
    "claim_ceiling.txt",
}

ALLOWED_VERDICTS = {
    "gate4_001c_execution_repair_rerun_001e_passed_bounded_preflight",
    "blocked_by_evidence_harness_challenger",
    "blocked_by_leakage_scan",
    "blocked_by_count_table_challenger_equivalence",
    "blocked_by_retrieval_baseline_degeneration",
    "blocked_by_ablation_semantic_mismatch",
    "blocked_by_replay_full_state_failure",
    "blocked_by_protected_artifact_mutation",
    "blocked_by_computed_provenance_gap",
    "blocked_by_precheck_failure",
}

PROVENANCE_FIELDS = {
    "producer_function",
    "input_artifacts",
    "run_id",
    "seed_ids",
    "context_ids",
    "partner_ids",
    "episode_ids",
    "aggregation_rule",
    "code_path_hash",
}


def load_json(name):
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def test_harness_input_uses_real_manifest_paths_not_governance_stub(tmp_path):
    from gate4_001c_execution_repair_rerun_001e import runner

    artifact = tmp_path / "result.json"
    artifact.write_text('{"verdict":"blocked_by_count_table_challenger_equivalence"}\n', encoding="utf-8")
    manifest = {
        "artifacts": {
            "result": {"path": artifact.as_posix(), "sha256": runner.sha256_file(artifact)},
        }
    }

    bundle = runner.build_harness_input_bundle(manifest, tmp_path)

    assert bundle["real_output_bundle"] is True
    assert bundle.get("governance_anchor_only") is not True
    assert bundle["path_payloads"][0]["path"] == artifact.as_posix()
    assert bundle["path_payloads"][0]["sha256"] == runner.sha256_file(artifact)


def test_harness_real_bundle_rejection_is_blocking():
    from gate4_001c_execution_repair_rerun_001e import runner

    verdict = runner.choose_final_verdict(
        precheck_passed=True,
        harness_report={"admissibility_class": "rejected_false_pass_risk"},
        leakage_report={"verdict": "leakage_real_bundle_scan_passed"},
        count_table_report={"candidate_advantage_collapsed": False},
        retrieval_report={"degeneration_unresolved": False},
        ablation_report={"semantic_binding_passed": True},
        replay_report={"full_state_replay_passed": True},
        protected_report={"verdict": "protected_artifacts_unchanged"},
        provenance_report={"passed": True},
    )

    assert verdict == "blocked_by_evidence_harness_challenger"


def test_harness_positive_control_must_be_rejected():
    from gate4_001c_execution_repair_rerun_001e import runner

    bad_report = {"admissibility_class": "blocked_pending_audit", "detected_pattern_categories": []}
    good_report = {
        "admissibility_class": "rejected_false_pass_risk",
        "detected_pattern_categories": ["pass_shaped_result_fields"],
    }

    assert runner.harness_positive_control_rejected(bad_report) is False
    assert runner.harness_positive_control_rejected(good_report) is True


def test_leakage_scanner_uses_bundle_argument_and_scans_real_paths(tmp_path):
    from gate4_001c_execution_repair_rerun_001e import runner

    clean = tmp_path / "clean.json"
    leak = tmp_path / "leak.json"
    clean.write_text('{"claim":"bounded"}\n', encoding="utf-8")
    leak.write_text(json.dumps({"claim": "EGO_" + "MAINLINE_READY"}) + "\n", encoding="utf-8")
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "artifacts": {
                    "clean": {"path": clean.as_posix(), "sha256": runner.sha256_file(clean)},
                    "leak": {"path": leak.as_posix(), "sha256": runner.sha256_file(leak)},
                }
            }
        ),
        encoding="utf-8",
    )

    report = runner.scan_leakage_bundle(manifest_path, tmp_path)

    assert report["supplied_bundle_argument"] == manifest_path.as_posix()
    assert report["parsed_bundle_path"] == manifest_path.resolve().as_posix()
    assert {item["path"] for item in report["scanned_files"]} == {clean.as_posix(), leak.as_posix()}
    assert report["real_bundle_scan_performed"] is True
    assert report["synthetic_controls_used_as_substitute"] is False
    assert report["verdict"] == "blocked_by_leakage_scan"


def test_leakage_synthetic_only_scan_is_not_accepted():
    from gate4_001c_execution_repair_rerun_001e import runner

    report = runner.build_synthetic_only_leakage_report()

    assert report["real_bundle_scan_performed"] is False
    assert report["synthetic_controls_used_as_substitute"] is True
    assert report["verdict"] == "blocked_by_leakage_scan"


def test_stream_keyed_count_table_equivalence_is_detected():
    from gate4_001c_execution_repair_rerun_001e import runner

    train, heldout, candidate_predictions = runner.build_count_table_equivalence_fixture()
    report = runner.stream_keyed_count_table_challenger(train, heldout, candidate_predictions)

    assert report["challenger_id"] == "stream_keyed_count_table_challenger"
    assert report["minimum_key"] == ["seed", "context_id", "partner_id"]
    assert report["candidate_advantage_collapsed"] is True
    assert report["challenger_score"] >= report["candidate_score"]
    assert report["verdict"] == "blocked_by_count_table_challenger_equivalence"


def test_retrieval_normalization_repairs_phase_token_mismatch():
    from gate4_001c_execution_repair_rerun_001e import runner

    train, heldout = runner.build_retrieval_phase_mismatch_fixture()
    report = runner.evaluate_retrieval_normalization(train, heldout)

    assert report["phase_token_handling_rule"] == "remove train_or_heldout phase token from observable_prefix"
    assert report["before"]["degenerate_prediction"] is True
    assert report["after"]["degenerate_prediction"] is False
    assert report["after"]["score"] > report["before"]["score"]
    assert report["degeneration_unresolved"] is False


def test_ablation_semantic_mismatch_blocks_positive_interpretation():
    from gate4_001c_execution_repair_rerun_001e import runner

    report = runner.validate_ablation_semantic_bindings(
        [
            {
                "ablation_name": "shuffled_feedback_ablation",
                "actual_intervention_hook": "invert_reward",
                "expected_causal_channel": "feedback_order",
                "affected_state_variables": ["feedback_history"],
            }
        ]
    )

    assert report["semantic_binding_passed"] is False
    assert report["verdict"] == "blocked_by_ablation_semantic_mismatch"


def test_replay_action_only_validation_is_rejected():
    from gate4_001c_execution_repair_rerun_001e import runner

    report = runner.validate_replay_report(
        {
            "action_recomputed": True,
            "state_update_recomputed": False,
            "hash_only_replay": False,
            "stored_action_only": False,
        }
    )

    assert report["full_state_replay_passed"] is False
    assert report["verdict"] == "blocked_by_replay_full_state_failure"


def test_replay_hash_only_validation_is_rejected():
    from gate4_001c_execution_repair_rerun_001e import runner

    report = runner.validate_replay_report(
        {
            "action_recomputed": True,
            "state_update_recomputed": True,
            "hash_only_replay": True,
            "stored_action_only": False,
        }
    )

    assert report["full_state_replay_passed"] is False
    assert report["verdict"] == "blocked_by_replay_full_state_failure"


def test_protected_artifact_mutation_is_detected():
    from gate4_001c_execution_repair_rerun_001e import runner

    before = {"files": {"artifacts/gate4_001c_failure_preserving_repair_001c/result.json": "a"}}
    after = {"files": {"artifacts/gate4_001c_failure_preserving_repair_001c/result.json": "b"}}

    report = runner.compare_protected_artifacts(before, after)

    assert report["mutation_violation_count"] == 1
    assert report["verdict"] == "blocked_by_protected_artifact_mutation"


def test_required_artifacts_exist_parse_and_preserve_claim_ceiling():
    missing = sorted(name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists())
    assert missing == []

    for path in ARTIFACT_DIR.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

    result = load_json("result.json")
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["starting_head"] == "31881e4defae968bc4bdebc6e3903c0b01970d26"
    assert result["claim_ceiling"].startswith("Bounded Gate4 001C execution-repair / rerun")
    assert result["authorizations"]["gate5_authorized"] is False
    assert result["authorizations"]["admission_authorized"] is False
    assert result["authorizations"]["runtime_authorized"] is False
    assert result["authorizations"]["bridge_authorized"] is False
    assert result["authorizations"]["ego_mainline_authorized"] is False
    assert "No Gate4 validity" in (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8")


def test_output_bundle_manifest_lists_required_real_artifact_classes():
    manifest = load_json("output_bundle_manifest.json")
    required_classes = {
        "result",
        "replay",
        "baselines",
        "challengers",
        "ablations",
        "leakage_scan",
        "harness_output",
        "tests",
        "traces",
        "provenance",
    }

    assert required_classes.issubset(set(manifest["artifacts"]))
    for item in manifest["artifacts"].values():
        assert item["path"]
        assert item["sha256"]
        assert (ROOT / item["path"]).exists() or Path(item["path"]).exists()


def test_real_bundle_harness_and_leakage_reports_record_scope():
    harness = load_json("harness_report.json")
    leakage = load_json("leakage_scan_report.json")
    manifest = load_json("output_bundle_manifest.json")

    assert harness["harness_input_bundle_path"].endswith("harness_input_bundle.json")
    assert harness["harness_input_bundle_digest"]
    assert set(harness["exact_file_list_passed_to_harness"]).issubset(
        {item["path"] for item in manifest["artifacts"].values()}
    )
    assert harness["real_bundle_evaluation_result"]["producer_function"] == "evaluate_bundle"
    assert harness["positive_control_rejection_result"] is True
    assert leakage["real_bundle_scan_performed"] is True
    assert leakage["supplied_bundle_argument"].endswith("output_bundle_manifest.json")
    assert leakage["scanner_rules"]
    assert leakage["synthetic_positive_control_result"]["detected"] is True


def test_count_table_collapse_retrieval_ablation_and_replay_reports_are_computed():
    count_table = load_json("count_table_challenger_report.json")
    retrieval = load_json("retrieval_normalization_report.json")
    ablation = load_json("ablation_semantic_binding_report.json")
    replay = load_json("replay_full_state_report.json")

    assert count_table["producer_function"] == "stream_keyed_count_table_challenger"
    assert count_table["candidate_advantage_collapsed"] is True
    assert count_table["challenger_score"] >= count_table["candidate_score"]
    assert retrieval["independent_callable_baseline_path"].endswith("evaluate_retrieval_normalization")
    assert retrieval["phase_token_handling_rule"]
    assert ablation["semantic_binding_passed"] is True
    assert all(item["proof_name_matches_intervention"] for item in ablation["ablations"])
    assert replay["action_recomputed"] is True
    assert replay["state_update_recomputed"] is True
    assert replay["negative_control"]["verdict"] == "blocked_by_replay_full_state_failure"


def test_computed_provenance_covers_reported_scores_and_negative_policy():
    provenance = load_json("computed_provenance.json")
    policy = load_json("negative_evidence_policy_application.json")

    assert provenance["passed"] is True
    assert provenance["records"]
    for record in provenance["records"]:
        assert PROVENANCE_FIELDS.issubset(record)
        assert record["input_artifacts"]
        assert record["code_path_hash"]

    assert policy["prior_execution_commit"] == "bbbb66c85f51d7b2b0176e5c575aa5fe64e29ece"
    assert policy["classification"] == "anchored_independently_audited_failed_false_pass_snapshot"
    assert policy["used_as_positive_gate4_support"] is False
    assert policy["reinterpreted_as_pass"] is False
