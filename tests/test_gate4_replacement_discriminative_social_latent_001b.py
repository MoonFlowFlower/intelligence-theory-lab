import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "gate4_replacement_discriminative_social_latent_001b"
ARTIFACT_DIR = ROOT / "artifacts" / TASK_ID
OLD_001C_ARTIFACT_DIRS = [
    ROOT / "artifacts" / "gate4_001c_execution_repair_rerun_001e",
    ROOT / "artifacts" / "gate4_001c_negative_evidence_routing_record_001a",
]

MANDATORY_SPLITS = {
    "seen_partner_unseen_context",
    "unseen_partner_seen_context",
    "unseen_partner_unseen_context",
    "unseen_preference_transition",
    "counterfactual_intervention",
    "active_query_required_episodes",
    "heldout_episodes_with_remapped_ids",
}

MANDATORY_BASELINES = {
    "stream_keyed_count_table",
    "normalized_retrieval",
    "nearest_neighbor_lookup",
    "context_partner_table",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "no_state_ablation",
    "no_feedback_ablation",
    "no_action_ablation",
    "oracle_label_positive_control",
}

PROVENANCE_FAMILIES = {
    "candidate score",
    "ordinary baseline score",
    "oracle positive-control score",
    "ablation score",
    "active-query causal contrast score",
    "budget parity result",
    "leakage scan result",
    "replay recomputation result",
    "split coverage result",
    "threshold pass/fail result",
    "aggregate contrast result",
    "per-split contrast result",
}


def _module(name):
    return importlib.import_module(f"gate4_replacement_discriminative_social_latent_001b.{name}")


def _read_json(name):
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def test_schemas_serialize_and_reject_forbidden_decision_fields():
    schemas = _module("schemas")

    observation = schemas.Observation(
        observable_partner="partner_alias_01",
        observable_context="context_alias_01",
        prompt_features={"tone": "direct", "topic": "planning"},
        legal_history=[{"action": "ask_preference", "feedback": "likes_direct"}],
    )
    payload = observation.to_json_dict()

    assert payload["observable_partner"] == "partner_alias_01"
    assert schemas.Observation.from_json_dict(payload).to_json_dict() == payload

    for forbidden in schemas.FORBIDDEN_DECISION_FIELDS:
        bad_payload = dict(payload)
        bad_payload[forbidden] = "leak"
        try:
            schemas.Observation.from_json_dict(bad_payload)
        except ValueError as exc:
            assert forbidden in str(exc)
        else:
            raise AssertionError(f"forbidden decision field accepted: {forbidden}")


def test_all_mandatory_splits_seeds_contexts_counterfactuals_and_remapped_ids_are_used():
    episodes = _module("episodes")

    manifest, episode_records = episodes.generate_episode_records()
    coverage = episodes.compute_split_coverage(manifest, episode_records)

    assert set(manifest["split_families"]) == MANDATORY_SPLITS
    assert set(coverage["used_split_families"]) == MANDATORY_SPLITS
    assert len(manifest["frozen_seed_ids"]) >= 5
    assert coverage["unused_frozen_seed_ids"] == []
    assert coverage["unused_train_context_ids"] == []
    assert coverage["unused_heldout_context_ids"] == []
    assert coverage["unused_counterfactual_pair_ids"] == []
    assert coverage["unused_remapped_episode_ids"] == []
    assert coverage["positive_evidence_allowed"] is True


def test_unused_material_blocks_positive_evidence():
    episodes = _module("episodes")

    manifest, episode_records = episodes.generate_episode_records()
    reduced = [row for row in episode_records if row.seed_id != manifest["frozen_seed_ids"][-1]]
    coverage = episodes.compute_split_coverage(manifest, reduced)

    assert coverage["positive_evidence_allowed"] is False
    assert manifest["frozen_seed_ids"][-1] in coverage["unused_frozen_seed_ids"]


def test_every_mandatory_baseline_is_invoked_per_split_and_disabling_one_fails_harness():
    runner = _module("runner")
    baselines = _module("baselines")

    run = runner.execute_bounded_run(output_dir=None, disabled_baselines=(), persist_artifacts=False)
    invocation = baselines.verify_baseline_invocations(run["baseline_results"], MANDATORY_BASELINES, MANDATORY_SPLITS)
    assert invocation["passed"] is True

    disabled = runner.execute_bounded_run(
        output_dir=None,
        disabled_baselines=("graph_lookup",),
        persist_artifacts=False,
    )
    assert disabled["result"]["verdict"] == "blocked_baseline_independence_failure"
    assert "graph_lookup" in disabled["result"]["stop_conditions_triggered"]


def test_baselines_are_independent_and_strongest_baseline_is_selected_by_metric():
    runner = _module("runner")
    baselines = _module("baselines")

    run = runner.execute_bounded_run(output_dir=None, persist_artifacts=False)
    independence = baselines.verify_baseline_independence()
    strongest = run["strongest_baseline_selection"]

    assert independence["passed"] is True
    assert all(row["shares_candidate_policy"] is False for row in independence["baseline_rows"])
    assert all(row["shares_candidate_update"] is False for row in independence["baseline_rows"])
    assert strongest["aggregate"]["baseline_id"] == strongest["aggregate"]["computed_from_scores"]["baseline_id"]
    assert strongest["aggregate"]["score"] == strongest["aggregate"]["computed_from_scores"]["score"]


def test_candidate_baseline_tie_blocks_positive_evidence():
    metrics = _module("metrics")

    verdict = metrics.evaluate_thresholds(
        candidate_score=0.80,
        strongest_baseline_score=0.80,
        oracle_score=1.0,
        per_split_margins={split: 0.10 for split in MANDATORY_SPLITS},
        seed_margins={f"seed_{idx}": 0.20 for idx in range(5)},
        active_query_seed_margins={f"seed_{idx}": 0.20 for idx in range(5)},
        ablation_drops={
            "no_active_query": 0.25,
            "shuffled_feedback": 0.25,
            "counterfactual_transition": 0.20,
        },
        oracle_positive_control_passed=True,
        budget_parity_passed=True,
        leakage_passed=True,
        replay_passed=True,
        provenance_passed=True,
        baseline_independence_passed=True,
        split_coverage_passed=True,
    )

    assert verdict["positive_evidence_allowed"] is False
    assert verdict["verdict"] == "gate4_replacement_discriminative_social_latent_implementation_001b_negative_evidence"
    assert "candidate_tied_or_below_strongest_non_oracle_baseline" in verdict["blocking_reasons"]


def test_oracle_positive_control_failure_invalidates_harness():
    metrics = _module("metrics")

    verdict = metrics.evaluate_thresholds(
        candidate_score=0.95,
        strongest_baseline_score=0.70,
        oracle_score=0.69,
        per_split_margins={split: 0.25 for split in MANDATORY_SPLITS},
        seed_margins={f"seed_{idx}": 0.25 for idx in range(5)},
        active_query_seed_margins={f"seed_{idx}": 0.25 for idx in range(5)},
        ablation_drops={
            "no_active_query": 0.25,
            "shuffled_feedback": 0.25,
            "counterfactual_transition": 0.20,
        },
        oracle_positive_control_passed=False,
        budget_parity_passed=True,
        leakage_passed=True,
        replay_passed=True,
        provenance_passed=True,
        baseline_independence_passed=True,
        split_coverage_passed=True,
    )

    assert verdict["verdict"] == "harness_invalid_oracle_positive_control_failure"
    assert verdict["positive_evidence_allowed"] is False


def test_ablation_scores_are_real_reruns_not_post_hoc_score_edits():
    runner = _module("runner")

    run = runner.execute_bounded_run(output_dir=None, persist_artifacts=False)
    ablation = run["ablation_results"]

    for intervention in ["no_active_query", "shuffled_feedback", "counterfactual_transition"]:
        row = ablation["interventions"][intervention]
        assert row["rerun_performed"] is True
        assert row["post_hoc_score_edit"] is False
        assert row["episode_run_ids"] != ablation["candidate_episode_run_ids"]

    assert ablation["drops"]["no_active_query"] >= 0.20
    assert ablation["drops"]["shuffled_feedback"] >= 0.20
    assert ablation["drops"]["counterfactual_transition"] >= 0.15


def test_leakage_scanner_flags_positive_control_and_never_reports_unconditional_clean(tmp_path):
    leakage = _module("leakage")

    clean_bundle = tmp_path / "clean"
    clean_bundle.mkdir()
    (clean_bundle / "result.json").write_text('{"claim":"bounded offline evidence"}\n', encoding="utf-8")
    contaminated_bundle = tmp_path / "contaminated"
    contaminated_bundle.mkdir()
    (contaminated_bundle / "result.json").write_text(
        json.dumps(
            {
                "seed": "seed_0",
                "phase_token": "train",
                "oracle_latent_label": "likes_direct",
                "answer_key": "direct_response",
                "future_outcome": "success",
                "split_label": "heldout",
                "bundle_path": contaminated_bundle.as_posix(),
            }
        ),
        encoding="utf-8",
    )

    clean = leakage.scan_bundle(clean_bundle)
    contaminated = leakage.scan_bundle(contaminated_bundle)

    assert clean["verdict"] == "clean"
    assert clean["unconditional_clean_report"] is False
    assert contaminated["verdict"] == "blocked_by_leakage_scan"
    assert contaminated["detected_categories"]
    assert contaminated["positive_control_detected"] is True
    assert all(row["status"] != "clean" for row in contaminated["excluded_paths"])


def test_replay_recomputes_action_and_state_update_and_detects_corruption():
    runner = _module("runner")
    replay = _module("replay")

    run = runner.execute_bounded_run(output_dir=None, persist_artifacts=False)
    report = run["replay_recomputation_report"]

    assert report["action_recomputed"] is True
    assert report["state_update_recomputed"] is True
    assert report["uses_stored_action_values"] is False
    assert report["uses_hash_only_comparison"] is False
    assert report["failure_controls"]["corrupted_state"]["passed"] is False
    assert report["failure_controls"]["corrupted_feedback"]["passed"] is False

    trace = run["trace_records"][0]
    corrupted = replay.recompute_trace_record(trace, corrupt_state=True)
    assert corrupted["passed"] is False
    assert corrupted["failure_reason"] == "corrupted_state_detected"


def test_budget_parity_is_callable_artifact_linked_and_blocks_unjustified_or_unknown_difference():
    runner = _module("runner")
    budget = _module("budget_parity")

    run = runner.execute_bounded_run(output_dir=None, persist_artifacts=False)
    report = budget.compute_budget_parity_report(run)
    verification = budget.verify_budget_parity(report)

    assert report["producer_function"].endswith("compute_budget_parity_report")
    assert report["linked_to_scored_run_artifacts"] is True
    assert verification["passed"] is True

    report["rows"][0]["classification"] = "unknown"
    failed = budget.verify_budget_parity(report)
    assert failed["passed"] is False
    assert "unknown" in failed["blocking_classifications"]


def test_provenance_exists_for_every_result_family_and_rejects_static_score_injection():
    runner = _module("runner")
    provenance = _module("provenance")

    run = runner.execute_bounded_run(output_dir=None, persist_artifacts=False)
    report = run["computed_evidence_provenance"]

    assert {row["result_family"] for row in report["records"]} == PROVENANCE_FAMILIES
    assert provenance.verify_provenance(report)["passed"] is True

    injected = json.loads(json.dumps(report))
    injected["records"][0]["producer_function"] = "static_json_literal"
    injected["records"][0]["static_score_injection"] = True
    failed = provenance.verify_provenance(injected)
    assert failed["passed"] is False
    assert "static_score_injection" in failed["blocking_reasons"]


def test_runner_writes_required_artifacts_only_under_allowed_artifact_directory(tmp_path):
    runner = _module("runner")

    out = tmp_path / TASK_ID
    run = runner.execute_bounded_run(output_dir=out, persist_artifacts=True)

    required = {
        "result.json",
        "run_manifest.json",
        "split_manifest.json",
        "episode_manifest.json",
        "trace_records.jsonl",
        "candidate_results.json",
        "baseline_results.json",
        "strongest_baseline_selection.json",
        "ablation_results.json",
        "active_query_causal_report.json",
        "budget_parity_report.json",
        "leakage_scan_report.json",
        "leakage_positive_control_report.json",
        "replay_recomputation_report.json",
        "computed_evidence_provenance.json",
        "threshold_report.json",
        "failure_taxonomy.json",
        "non_mutation_guard.json",
        "claim_ceiling.txt",
    }

    assert required.issubset({path.name for path in out.iterdir()})
    assert run["result"]["downstream_authorization_flags_all_false"] is True
    for path in out.rglob("*"):
        if path.is_file():
            assert out in path.parents


def test_materialized_artifacts_parse_and_old_gate4_001c_artifacts_not_modified():
    runner = _module("runner")

    before = runner.hash_old_gate4_001c_artifacts(ROOT)
    runner.execute_bounded_run(output_dir=ARTIFACT_DIR, persist_artifacts=True)
    after = runner.hash_old_gate4_001c_artifacts(ROOT)

    assert before == after
    assert _read_json("non_mutation_guard.json")["old_gate4_001c_artifacts_modified"] is False
    for path in ARTIFACT_DIR.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

