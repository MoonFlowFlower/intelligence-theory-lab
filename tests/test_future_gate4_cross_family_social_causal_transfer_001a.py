import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "implement_future_gate4_cross_family_social_causal_transfer_001a"
ARTIFACT_DIR = ROOT / "artifacts" / TASK_ID

REQUIRED_BASELINES = {
    "serialized_state_decoder",
    "full_bundle_decoder",
    "partner_id_decoder",
    "table_lookup",
    "pair_count",
    "ngram_trace_lookup",
    "belief_table",
    "nearest_neighbor_retrieval",
    "episodic_trace_retrieval",
    "target_label_oracle_leak_check",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "query_capable_imitation_baseline",
}

GRAPH_CACHE_FAMILY = {
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
}

REQUIRED_ABLATIONS = {
    "remove_partner_hidden_state_update",
    "mask_partner_causal_observation_channel",
    "shuffle_partner_family_labels",
    "disable_counterfactual_query_update_path",
    "disable_heldout_schema_transfer_component",
    "remove_explicit_partner_family_schema_ids",
    "perturb_intervention_observations_preserve_trace_length",
    "no_learning_frozen_state_variant",
}

REQUIRED_ARTIFACTS = {
    "result.json",
    "source_pin_readback.json",
    "frozen_equivalence_rule.json",
    "equivalence_rule_source_hash.json",
    "baseline_access_parity.json",
    "baseline_invocation_log.json",
    "graph_cache_family_invocation_log.json",
    "query_capable_imitation_parity.json",
    "ablation_invocation_log.json",
    "leakage_positive_controls.json",
    "leakage_scan_report.json",
    "replay_recomputation_report.json",
    "computed_evidence_provenance.json",
    "train_heldout_split_manifest.json",
    "counterfactual_pair_manifest.json",
    "test_result_readback.json",
    "claim_ceiling.json",
    "trace.jsonl",
    "baseline_comparison.json",
    "ablation_report.json",
    "replay_report.json",
}


def _module(name):
    return importlib.import_module(f"future_gate4_cross_family_social_causal_transfer_001a.{name}")


def _read_json(name):
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def test_preflight_reads_required_boundaries_and_forbids_auto_remote_anchor():
    runner = _module("runner")

    readback = runner.build_source_pin_readback()

    assert readback["branch"] == "codex/meta-theory-scaffold"
    assert readback["expected_overall_sealed_boundary"] == "79928e2c5f770326a1d0d370186814f4a0b2d104"
    assert readback["current_head_is_expected_overall_boundary"] is True
    assert readback["gate4_boundary_is_ancestor"] is True
    assert isinstance(readback["worktree_clean_at_start"], bool)
    assert readback["git_status_short_branch"].startswith("## codex/meta-theory-scaffold")
    assert readback["auto_remote_anchor_policy"] == "forbidden"
    assert readback["design_card_found"] is True
    assert readback["claude_reaudit_found"] is True
    assert readback["binding_contracts_found"] is True


def test_equivalence_rule_must_be_frozen_source_pinned_and_unchanged_before_scoring(tmp_path):
    runner = _module("runner")
    core = _module("core")

    blocked = runner.execute_harness(output_dir=tmp_path / "missing", persist_artifacts=False, freeze_rule=False)
    assert blocked["result"]["verdict"] == "blocked_equivalence_rule_missing"
    assert "equivalence_rule_missing_before_run" in blocked["result"]["stop_conditions_triggered"]

    run = runner.execute_harness(output_dir=tmp_path / "valid", persist_artifacts=False)
    rule = run["frozen_equivalence_rule"]
    source_hash = run["equivalence_rule_source_hash"]

    assert rule["created_before_run"] is True
    assert rule["run_block_if_missing"] is True
    assert rule["run_block_if_modified_after_execution_start"] is True
    assert rule["candidate_advantage_definition"]
    assert rule["candidate_equivalent_definition"]
    assert source_hash["source_file_hash"] == rule["source_file_hash"]
    assert core.verify_equivalence_rule_source_pin(rule, source_hash)["passed"] is True

    modified = runner.execute_harness(
        output_dir=tmp_path / "modified",
        persist_artifacts=False,
        mutate_equivalence_rule_after_start=True,
    )
    assert modified["result"]["verdict"] == "blocked_posthoc_equivalence_rule_change"
    assert "equivalence_rule_modified_after_execution_start" in modified["result"]["stop_conditions_triggered"]


def test_all_required_baselines_graph_cache_members_and_query_imitation_are_invoked(tmp_path):
    runner = _module("runner")

    run = runner.execute_harness(output_dir=tmp_path, persist_artifacts=False)

    invoked = {row["baseline_id"] for row in run["baseline_invocation_log"]["invocations"]}
    assert REQUIRED_BASELINES.issubset(invoked)
    assert {row["baseline_id"] for row in run["graph_cache_family_invocation_log"]["invocations"]} == GRAPH_CACHE_FAMILY
    assert run["baseline_access_parity"]["passed"] is True
    assert run["query_capable_imitation_parity"]["passed"] is True
    assert run["query_capable_imitation_parity"]["candidate_query_budget"] == run["query_capable_imitation_parity"]["baseline_query_budget"]
    assert run["query_capable_imitation_parity"]["candidate_observation_access"] == run["query_capable_imitation_parity"]["baseline_observation_access"]

    blocked = runner.execute_harness(
        output_dir=tmp_path / "disabled",
        persist_artifacts=False,
        disabled_baselines=("graph_lookup",),
    )
    assert blocked["result"]["verdict"] == "blocked_graph_cache_challenger_missing"
    assert "graph_lookup" in blocked["result"]["missing_baselines"]


def test_ablations_rerun_episodes_under_real_interventions(tmp_path):
    runner = _module("runner")

    run = runner.execute_harness(output_dir=tmp_path, persist_artifacts=False)
    invocation = run["ablation_invocation_log"]

    assert {row["ablation_id"] for row in invocation["invocations"]} == REQUIRED_ABLATIONS
    assert invocation["passed"] is True
    for row in invocation["invocations"]:
        assert row["reran_episodes"] is True
        assert row["post_hoc_score_edit"] is False
        assert row["intervention_artifact_hash"]


def test_leakage_scanners_detect_positive_controls_before_clean_scan_is_trusted(tmp_path):
    runner = _module("runner")
    leakage = _module("leakage")

    positive = leakage.run_positive_control_suite()
    assert positive["passed"] is True
    assert set(positive["detected_control_ids"]) == set(leakage.POSITIVE_CONTROL_IDS)

    clean_without_positive = leakage.scan_clean_bundle({"observation": "safe"}, positive_controls_passed=False)
    assert clean_without_positive["verdict"] == "blocked_positive_controls_not_run"
    assert clean_without_positive["clean_scan_trusted"] is False

    run = runner.execute_harness(output_dir=tmp_path, persist_artifacts=False)
    assert run["leakage_positive_controls"]["passed"] is True
    assert run["leakage_scan_report"]["verdict"] == "clean"
    assert run["leakage_scan_report"]["clean_scan_trusted"] is True


def test_replay_recomputes_from_serialized_state_observation_and_query_context(tmp_path):
    runner = _module("runner")
    replay = _module("replay")

    run = runner.execute_harness(output_dir=tmp_path, persist_artifacts=False)
    report = run["replay_recomputation_report"]

    assert report["passed"] is True
    assert report["recomputed_from"] == ["serialized_state", "current_observation", "allowed_query_context", "seed_episode_context_ids"]
    assert report["uses_stored_candidate_output"] is False
    assert report["uses_stored_baseline_output"] is False
    assert report["uses_hash_only_comparison"] is False
    assert report["candidate_callable_path"].endswith("candidate_predict")
    assert GRAPH_CACHE_FAMILY.issubset(set(report["baseline_callable_paths"]))

    corrupted = replay.recompute_replay_record(run["trace_records"][0], corrupt_serialized_state=True)
    assert corrupted["passed"] is False
    assert corrupted["failure_reason"] == "serialized_state_recompute_mismatch"


def test_computed_evidence_provenance_required_for_every_score(tmp_path):
    runner = _module("runner")
    provenance = _module("provenance")

    run = runner.execute_harness(output_dir=tmp_path, persist_artifacts=False)
    report = run["computed_evidence_provenance"]

    assert provenance.verify_computed_evidence_provenance(report)["passed"] is True
    for record in report["records"]:
        for field in provenance.REQUIRED_SCORE_PROVENANCE_FIELDS:
            assert field in record
            assert record[field] not in (None, "", [], {})

    missing = json.loads(json.dumps(report))
    del missing["records"][0]["producer_function"]
    failed = provenance.verify_computed_evidence_provenance(missing)
    assert failed["passed"] is False
    assert "producer_function" in failed["missing_fields"]


def test_result_json_cannot_self_declare_pass_and_baseline_equivalence_fails(tmp_path):
    runner = _module("runner")
    core = _module("core")

    run = runner.execute_harness(output_dir=tmp_path, persist_artifacts=False)
    verdict_audit = core.verify_result_verdict_is_computed(run["result"])
    assert verdict_audit["passed"] is True
    assert run["result"]["verdict"] == "implementation_pass_pending_independent_audit"

    self_declared = dict(run["result"])
    self_declared["verdict_producer_function"] = "literal_result_json_self_pass"
    self_declared["self_declared_pass"] = True
    assert core.verify_result_verdict_is_computed(self_declared)["passed"] is False

    tied = runner.execute_harness(output_dir=tmp_path / "tie", persist_artifacts=False, force_best_baseline_tie=True)
    assert tied["result"]["verdict"] == "baseline_equivalent_negative_evidence"
    assert tied["result"]["candidate_equivalent"] is True


def test_train_heldout_splits_counterfactual_pairs_and_no_remote_actions_are_recorded(tmp_path):
    runner = _module("runner")

    run = runner.execute_harness(output_dir=tmp_path, persist_artifacts=False)
    split = run["train_heldout_split_manifest"]
    pairs = run["counterfactual_pair_manifest"]

    assert split["created_before_run"] is True
    assert set(split["heldout_axes"]) == {"partner_family", "task_schema"}
    assert split["unused_frozen_seed_ids"] == []
    assert split["unused_train_context_ids"] == []
    assert split["unused_heldout_context_ids"] == []
    assert pairs["unused_counterfactual_pair_ids"] == []
    assert run["result"]["auto_remote_anchor"] == "forbidden"
    assert run["result"]["push_performed"] is False
    assert run["result"]["tag_performed"] is False


def test_runner_writes_required_artifacts_and_research_report(tmp_path):
    runner = _module("runner")

    out = tmp_path / TASK_ID
    run = runner.execute_harness(output_dir=out, persist_artifacts=True)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in out.iterdir()})
    assert not (out / "blocked_readback.json").exists()
    assert run["result"]["claim_ceiling"] == run["claim_ceiling"]["claim_ceiling"]
    for path in out.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

    report_path = runner.write_research_report(run, docs_dir=tmp_path)
    report_text = report_path.read_text(encoding="utf-8")
    assert "No valid Gate4 claim" in report_text
    assert "Auto-Remote-Anchor: forbidden" in report_text
