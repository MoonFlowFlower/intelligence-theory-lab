import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "gate4_replacement_discriminative_social_latent_001c"
ARTIFACT_DIR = ROOT / "artifacts" / TASK_ID

MANDATORY_SPLITS = {
    "seen_partner_unseen_context",
    "unseen_partner_seen_context",
    "unseen_partner_unseen_context",
    "unseen_preference_transition",
    "counterfactual_intervention",
    "active_query_required_episodes",
    "heldout_episodes_with_remapped_ids",
}

REQUIRED_ARTIFACTS = {
    "result.json",
    "source_pin_readback.json",
    "candidate_results.json",
    "baseline_results.json",
    "observation_only_decoder_results.json",
    "observation_target_independence_report.json",
    "active_query_causal_report.json",
    "ablation_results.json",
    "replay_recomputation_report.json",
    "budget_parity_report.json",
    "leakage_report.json",
    "leakage_positive_control_report.json",
    "computed_evidence_provenance.json",
    "split_coverage_report.json",
    "trace_records.jsonl",
    "non_mutation_guard.json",
    "threshold_evaluation.json",
    "repair_delta_from_001b.json",
}


def _module():
    return importlib.import_module("gate4_replacement_discriminative_social_latent_001c.core")


def test_observations_remove_baseline_hint_and_pass_target_independence_with_positive_controls():
    core = _module()

    manifest, episodes = core.generate_episode_records()
    report = core.observation_target_independence_check(episodes)

    assert set(manifest["split_families"]) == MANDATORY_SPLITS
    assert report["passed"] is True
    assert report["max_observation_only_recoverability"] <= report["allowed_recoverability_ceiling"]
    assert report["deterministic_or_near_deterministic_features"] == []
    assert report["positive_controls"]["direct_target_label"]["detected"] is True
    assert report["positive_controls"]["cyclic_baseline_hint"]["detected"] is True

    for episode in episodes:
        observation = episode.observation.to_json_dict()
        assert "baseline_hint" not in observation["prompt_features"]
        assert "target_action" not in json.dumps(observation)


def test_observation_only_decoder_challenger_is_invoked_and_blocks_deliberate_leakage():
    core = _module()

    _, episodes = core.generate_episode_records()
    decoder = core.run_observation_only_decoder_challengers(episodes)
    leaked = core.run_observation_only_decoder_challengers(core.inject_deliberate_observation_leakage(episodes))

    assert decoder["passed"] is True
    assert decoder["strongest_decoder_score"] <= decoder["allowed_score_ceiling"]
    assert "hint_inverter_regression_control" in decoder["decoder_ids"]
    assert set(decoder["split_invocations"]) == MANDATORY_SPLITS
    assert leaked["passed"] is False
    assert leaked["strongest_decoder_id"] in {"target_label_lookup", "hint_inverter_regression_control"}
    assert "observation_only_decoder_reached_candidate_level" in leaked["blocking_reasons"]


def test_candidate_wins_only_through_feedback_path_and_collapses_under_controls():
    core = _module()

    run = core.execute_bounded_run(output_dir=None, persist_artifacts=False)
    result = run["result"]
    ablation = run["ablation_results"]
    causal = run["active_query_causal_report"]

    assert result["candidate_score"] == 1.0
    assert result["strongest_observation_only_decoder_score"] <= 0.35
    assert result["candidate_observation_only_margin"] >= 0.50
    assert result["verdict"] == core.PASS_VERDICT

    for intervention in ["no_active_query", "shuffled_feedback", "counterfactual_feedback", "corrupted_feedback"]:
        row = ablation["interventions"][intervention]
        assert row["rerun_performed"] is True
        assert row["post_hoc_score_edit"] is False
        assert row["score"] < 0.50

    assert causal["passed"] is True
    assert causal["computed_flags"]["active_query_selected_from_policy"] is True
    assert causal["computed_flags"]["feedback_changed_state"] is True
    assert causal["computed_flags"]["final_action_changed_under_feedback_controls"] is True


def test_budget_parity_classification_is_computed_and_fails_organic_disparity():
    core = _module()

    run = core.execute_bounded_run(output_dir=None, persist_artifacts=False)
    report = run["budget_parity_report"]
    verification = core.verify_budget_parity(report)
    disparity = core.compute_budget_parity_report(run, inject_unexplained_disparity=True)

    assert verification["passed"] is True
    assert "equal" in {row["classification"] for row in report["rows"]}
    assert "oracle_expected_disparity" in {row["classification"] for row in report["rows"]}
    assert core.verify_budget_parity(disparity)["passed"] is False
    assert "unexplained_disparity" in core.verify_budget_parity(disparity)["blocking_classifications"]


def test_replay_corruption_recomputes_and_reports_recomputed_fields():
    core = _module()

    run = core.execute_bounded_run(output_dir=None, persist_artifacts=False)
    report = run["replay_recomputation_report"]
    corrupted = core.recompute_trace_record(run["trace_records"][0], corrupt_state=True)

    assert report["passed"] is True
    assert report["failure_controls"]["corrupted_state"]["passed"] is False
    assert corrupted["state_update_recomputed"] is True
    assert corrupted["action_recomputed"] is True
    assert corrupted["recomputed_action"]
    assert corrupted["recomputed_state_after_update"]
    assert corrupted["failure_reason"] == "corrupted_state_recomputed_mismatch"


def test_provenance_binds_real_producer_hashes_and_rejects_static_injection():
    core = _module()

    run = core.execute_bounded_run(output_dir=None, persist_artifacts=False)
    report = run["computed_evidence_provenance"]
    families = {row["result_family"] for row in report["records"]}
    injected = json.loads(json.dumps(report))
    injected["records"][0]["producer_function"] = "static_json_literal"
    injected["records"][0]["static_score_injection"] = True

    assert core.REQUIRED_PROVENANCE_FAMILIES.issubset(families)
    assert core.verify_provenance(report)["passed"] is True
    assert all(row["code_path_hash"] == core.code_path_hash(core.resolve_producer(row["producer_function"])) for row in report["records"])
    assert core.verify_provenance(injected)["passed"] is False


def test_leakage_scan_uses_unsanitized_bundle_and_detects_controls():
    core = _module()

    _, episodes = core.generate_episode_records()
    clean = core.scan_raw_evidence_bundle(core.build_raw_observation_bundle(episodes))
    positive = core.build_leakage_positive_control_report()
    negative = core.build_leakage_negative_control_report()

    assert clean["scanned_unsanitized_evidence"] is True
    assert clean["pre_scrubbed_before_scan"] is False
    assert clean["verdict"] == "clean"
    assert positive["positive_control_detected"] is True
    assert positive["verdict"] == "blocked_by_leakage_scan"
    assert negative["verdict"] == "clean"


def test_threshold_gate_blocks_observation_decoder_tie_and_oracle_failure():
    core = _module()

    tie = core.evaluate_thresholds(
        candidate_score=1.0,
        strongest_ordinary_score=0.25,
        strongest_observation_only_score=1.0,
        oracle_score=1.0,
        per_split_margins={split: 0.75 for split in MANDATORY_SPLITS},
        observation_independence_passed=True,
        observation_decoder_passed=False,
        active_query_passed=True,
        ablation_passed=True,
        replay_passed=True,
        budget_passed=True,
        leakage_passed=True,
        provenance_passed=True,
        split_coverage_passed=True,
        non_mutation_passed=True,
    )
    oracle = core.evaluate_thresholds(
        candidate_score=1.0,
        strongest_ordinary_score=0.25,
        strongest_observation_only_score=0.25,
        oracle_score=0.20,
        per_split_margins={split: 0.75 for split in MANDATORY_SPLITS},
        observation_independence_passed=True,
        observation_decoder_passed=True,
        active_query_passed=True,
        ablation_passed=True,
        replay_passed=True,
        budget_passed=True,
        leakage_passed=True,
        provenance_passed=True,
        split_coverage_passed=True,
        non_mutation_passed=True,
    )

    assert tie["positive_evidence_allowed"] is False
    assert "observation_only_decoder_reached_candidate_level" in tie["blocking_reasons"]
    assert oracle["verdict"] == "harness_invalid_oracle_positive_control_failure"


def test_runner_writes_required_artifacts_and_preserves_sealed_boundaries(tmp_path):
    core = _module()

    out = tmp_path / TASK_ID
    before = core.hash_protected_boundaries(ROOT)
    run = core.execute_bounded_run(output_dir=out, persist_artifacts=True)
    after = core.hash_protected_boundaries(ROOT)

    assert before == after
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in out.iterdir()})
    assert run["result"]["inherits_001b_negative_evidence"] is True
    assert run["result"]["downstream_authorization_flags_all_false"] is True
    assert run["non_mutation_guard"]["old_001b_and_old_gate4_001c_modified"] is False

    for path in out.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))


def test_materialized_repo_artifacts_parse_after_main_run():
    core = _module()

    core.execute_bounded_run(output_dir=ARTIFACT_DIR, persist_artifacts=True)

    for name in REQUIRED_ARTIFACTS - {"trace_records.jsonl"}:
        json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))
    traces = [
        json.loads(line)
        for line in (ARTIFACT_DIR / "trace_records.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert traces
    assert json.loads((ARTIFACT_DIR / "result.json").read_text(encoding="utf-8"))["claim_ceiling"] == core.CLAIM_CEILING
