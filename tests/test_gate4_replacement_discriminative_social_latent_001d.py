import copy
import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "gate4_replacement_discriminative_social_latent_001d"
ARTIFACT_DIR = ROOT / "artifacts" / TASK_ID

REQUIRED_ARTIFACTS = {
    "result.json",
    "source_pin_readback.json",
    "candidate_report.json",
    "baseline_report.json",
    "strongest_baseline_report.json",
    "feedback_recoverability_report.json",
    "leakage_report.json",
    "leakage_positive_control_report.json",
    "ablation_report.json",
    "replay_report.json",
    "provenance_report.json",
    "non_mutation_guard.json",
    "trace_records.jsonl",
}

MANDATORY_BASELINES = {
    "observation_only_decoder_challenger",
    "feedback_aware_decoder_challenger",
    "query_and_follow_feedback",
    "direct_stated_preference_copier",
    "feedback_token_lookup",
    "history_order_cache",
    "stream_keyed_count_table",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "oracle_label_positive_control",
    "leakage_positive_control",
}

MANDATORY_ABLATIONS = {
    "no_query",
    "no_feedback",
    "shuffled_feedback",
    "counterfactual_feedback",
    "noisy_feedback",
    "partial_feedback",
    "feedback_token_deletion",
    "feedback_order_permutation",
    "state_corruption",
    "legal_history_removal",
    "observation_only_mode",
}


def _module():
    return importlib.import_module("gate4_replacement_discriminative_social_latent_001d.core")


def test_source_pin_readback_records_sealed_boundary_and_preserves_parent_evidence():
    core = _module()

    report = core.build_source_pin_readback(run_id="unit-test")

    assert report["starting_head"] == core.STARTING_BOUNDARY
    assert report["parent_boundary"] == core.STARTING_BOUNDARY
    assert report["parent_tag"]
    assert report["working_tree_index_status"]["old_001b_paths_modified"] is False
    assert report["working_tree_index_status"]["old_001c_paths_modified"] is False
    assert report["working_tree_index_status"]["forbidden_paths_modified"] is False
    assert report["required_parent_evidence"]["001b_blocked_routing_commit"] == core.PARENT_001B_COMMIT
    assert report["required_parent_evidence"]["001c_blocked_candidate_commit"] == core.PARENT_001C_COMMIT
    assert report["required_parent_evidence"]["preserved_claude_001c_audit_exists"] is True
    assert report["required_parent_evidence"]["draft_001d_repair_card_exists"] is True


def test_scanner_scans_actual_feedback_state_and_positive_controls_on_real_paths():
    core = _module()

    run = core.execute_bounded_run(output_dir=None, persist_artifacts=False)
    clean = run["leakage_report"]
    positive = run["leakage_positive_control_report"]

    assert clean["verdict"] == "clean"
    assert clean["scanned_paths"] == [
        "observation",
        "legal_history",
        "feedback_history",
        "query_action",
        "serialized_state_before_update",
        "serialized_state_after_update",
        "final_prediction",
    ]
    assert clean["feedback_history_records_scanned"] == len(run["trace_records"])
    assert positive["feedback_path_positive_control"]["verdict"] == "blocked_by_leakage_scan"
    assert positive["serialized_state_positive_control"]["verdict"] == "blocked_by_leakage_scan"
    assert positive["observation_positive_control"]["verdict"] == "blocked_by_leakage_scan"

    contaminated = core.build_candidate_visible_bundle(
        [core.inject_feedback_leak(run["trace_records"][0], "direct_response")]
    )
    scan = core.scan_candidate_visible_bundle(contaminated)
    assert scan["verdict"] == "blocked_by_leakage_scan"
    assert "direct_action_token_feedback" in scan["detected_categories"]


def test_baselines_are_invoked_independent_and_query_capable_baseline_does_not_tie():
    core = _module()

    run = core.execute_bounded_run(output_dir=None, persist_artifacts=False)
    report = run["baseline_report"]
    invocation = core.verify_baseline_invocations(report)

    assert invocation["passed"] is True
    assert MANDATORY_BASELINES.issubset(set(report["baseline_ids"]))
    assert report["independence_check"]["passed"] is True
    assert all(not row["shares_candidate_update"] for row in report["independence_check"]["rows"])
    assert report["scores"]["query_and_follow_feedback"] < run["candidate_report"]["score"]
    assert report["scores"]["feedback_token_lookup"] < run["candidate_report"]["score"]
    assert run["strongest_baseline_report"]["strongest_ordinary"]["score"] == max(
        score
        for baseline_id, score in report["scores"].items()
        if baseline_id not in core.POSITIVE_CONTROL_BASELINES
        and baseline_id not in core.QUERY_CAPABLE_BASELINES
    )
    assert run["strongest_baseline_report"]["strongest_query_capable"]["baseline_id"] == "query_and_follow_feedback"


def test_recoverability_ceiling_and_single_feedback_token_controls_are_enforced():
    core = _module()

    run = core.execute_bounded_run(output_dir=None, persist_artifacts=False)
    report = run["feedback_recoverability_report"]
    single_token = run["candidate_report"]["single_feedback_token_control"]

    assert report["passed"] is True
    assert report["predeclared_recoverability_ceiling"] == core.RECOVERABILITY_CEILING
    assert report["strongest_recoverability_score"] <= core.RECOVERABILITY_CEILING
    assert report["surfaces"]["feedback_history_only"]["score"] <= core.RECOVERABILITY_CEILING
    assert report["surfaces"]["full_candidate_visible_bundle"]["score"] <= core.RECOVERABILITY_CEILING
    assert single_token["candidate_single_token_score"] <= single_token["single_token_ceiling"]
    assert single_token["single_feedback_token_can_determine_target"] is False

    leaked = core.build_feedback_recoverability_report(
        run["episodes"],
        run["trace_records"],
        inject_direct_feedback_answer=True,
    )
    assert leaked["passed"] is False
    assert "recoverability_above_ceiling" in leaked["blocking_reasons"]


def test_ablation_replay_and_provenance_are_computed_not_static():
    core = _module()

    run = core.execute_bounded_run(output_dir=None, persist_artifacts=False)
    ablation = run["ablation_report"]
    replay = run["replay_report"]
    provenance = run["provenance_report"]

    assert set(ablation["interventions"]) == MANDATORY_ABLATIONS
    assert all(row["rerun_performed"] is True for row in ablation["interventions"].values())
    assert ablation["passed"] is True
    assert ablation["distinguishes_multi_step_integration_from_copying"] is True
    assert ablation["distinguishes_feedback_as_answer_shortcut"] is True

    assert replay["passed"] is True
    assert replay["candidate_query_recomputed"] is True
    assert replay["feedback_processing_recomputed"] is True
    assert replay["state_update_recomputed"] is True
    assert replay["final_prediction_recomputed"] is True
    assert replay["corruption_controls"]["feedback_corruption"]["passed"] is False
    assert replay["corruption_controls"]["serialized_state_corruption"]["passed"] is False

    assert core.verify_provenance(provenance)["passed"] is True
    injected = json.loads(json.dumps(provenance))
    injected["records"][0]["producer_function"] = "static_json_literal"
    injected["records"][0]["static_score_injection"] = True
    assert core.verify_provenance(injected)["passed"] is False


def test_acceptance_gate_blocks_missing_baseline_and_downstream_authorization():
    core = _module()

    run = core.execute_bounded_run(output_dir=None, persist_artifacts=False)
    accepted = core.evaluate_acceptance_gate(run)
    missing = copy.deepcopy(run)
    missing["baseline_report"]["invoked_baselines"].remove("query_and_follow_feedback")
    missing["baseline_report"]["scores"].pop("query_and_follow_feedback")
    unauthorized = copy.deepcopy(run)
    unauthorized["result"]["downstream_authorization_flags"]["gate5_authorized"] = True

    assert accepted["passed"] is True
    assert core.evaluate_acceptance_gate(missing)["passed"] is False
    assert "missing_baseline_invocation:query_and_follow_feedback" in core.evaluate_acceptance_gate(missing)["blocking_reasons"]
    assert core.evaluate_acceptance_gate(unauthorized)["passed"] is False
    assert "downstream_authorization_flag_true" in core.evaluate_acceptance_gate(unauthorized)["blocking_reasons"]


def test_runner_writes_required_artifacts_and_preserves_old_evidence(tmp_path):
    core = _module()

    out = tmp_path / TASK_ID
    before = core.hash_protected_boundaries(ROOT)
    run = core.execute_bounded_run(output_dir=out, persist_artifacts=True)
    after = core.hash_protected_boundaries(ROOT)

    assert before == after
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in out.iterdir()})
    assert run["result"]["verdict"] == core.PASS_VERDICT
    assert run["result"]["inherits_001b_negative_evidence"] is True
    assert run["result"]["inherits_001c_negative_evidence"] is True
    assert run["result"]["downstream_authorization_flags_all_false"] is True
    assert run["non_mutation_guard"]["old_001b_modified"] is False
    assert run["non_mutation_guard"]["old_001c_modified"] is False
    assert run["non_mutation_guard"]["forbidden_paths_modified"] is False

    for name in REQUIRED_ARTIFACTS - {"trace_records.jsonl"}:
        json.loads((out / name).read_text(encoding="utf-8"))
    traces = [json.loads(line) for line in (out / "trace_records.jsonl").read_text(encoding="utf-8").splitlines()]
    assert traces


def test_materialized_repo_artifacts_parse_after_main_run():
    core = _module()

    core.execute_bounded_run(output_dir=ARTIFACT_DIR, persist_artifacts=True)

    for name in REQUIRED_ARTIFACTS - {"trace_records.jsonl"}:
        json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))
    result = json.loads((ARTIFACT_DIR / "result.json").read_text(encoding="utf-8"))
    assert result["claim_ceiling"] == core.CLAIM_CEILING
    assert result["safe_to_enter_gate5"] is False
    assert result["safe_to_enter_admission"] is False
    assert result["safe_to_enter_bridge"] is False
    assert result["safe_to_enter_runtime"] is False
    assert result["safe_to_enter_ego_mainline"] is False
