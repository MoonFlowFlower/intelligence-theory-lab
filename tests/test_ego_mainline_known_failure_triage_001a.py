import copy
import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EGO-MAINLINE-KNOWN-FAILURE-TRIAGE-001A"
ARTIFACT_DIR = ROOT / "artifacts" / "ego_mainline_known_failure_triage_001a"
DOC = ROOT / "docs" / "codex" / "tasks" / f"{TASK_ID}.md"

DEPENDENCY_CLOSURE_ANCHOR = "01973a538fad9c33ca2c6119a0f2c6b384602f34"
DEPENDENCY_CLOSURE_REMOTE_TAG = "remote-anchor-evidence-dependency-closure-001a-01973a"
ROUTING_ANCHOR = "4edf5cff7f89cf2cf1c6dbb15a478bbada0432aa"
ROUTING_REMOTE_TAG = "remote-anchor-post-admission-routing-001a-4edf5c"
ADMISSION_ANCHOR = "98e51a46cd7f28f60b1851c616d4351c1cd6272f"
ADMISSION_REMOTE_TAG = "remote-anchor-bounded-admission-execution-001a-98e51a4"

FAILED_NODE_IDS = {
    "tests/test_ego_mainline_admission_canonical_coverage_reference_001a.py::test_temp_run_uses_same_validators_without_remote_dependency",
    "tests/test_ego_mainline_admission_task_card_alignment_001a.py::test_temp_run_uses_same_validators",
    "tests/test_ego_mainline_evidence_dependency_closure_001a.py::test_callable_candidate_rejects_corrupted_inputs_without_authorizing_downstream",
    "tests/test_ego_mainline_post_admission_routing_001a.py::test_callable_candidate_rejects_corrupted_governance_inputs_without_authorizing_downstream",
}

REQUIRED_ARTIFACTS = {
    "result.json",
    "anchor_readback.json",
    "input_artifact_inventory.json",
    "test_suite_observation.json",
    "full_pytest_failure_report.json",
    "isolated_rerun_report.json",
    "failure_reproducibility_matrix.json",
    "failure_cause_classification.json",
    "failure_discrepancy_explanation.json",
    "old_artifact_side_effect_matrix.json",
    "blocker_severity_matrix.json",
    "downstream_route_impact_matrix.json",
    "required_repair_tasks.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_scan_report.json",
    "replay_report.json",
    "computed_evidence_provenance.json",
    "triage_state.json",
    "claim_ceiling.txt",
    "future_task_recommendation.txt",
    "rollback_plan.txt",
}

BASELINES = {
    "naive_targeted_tests_green_baseline",
    "naive_unrelated_old_failure_baseline",
    "strict_full_suite_failure_baseline",
    "claim_ceiling_baseline",
}

ABLATED_INPUTS = {
    "remove_full_pytest_observation",
    "remove_exact_failed_node_ids",
    "remove_isolated_rerun_results",
    "remove_traceback_text",
    "remove_before_after_hash_inventory",
    "remove_side_effect_report",
    "remove_prior_dependency_closure_classification",
    "remove_claim_ceiling",
    "remove_route_permission_matrix",
    "substitute_clean_targeted_only_observation_while_full_suite_failures_remain",
    "substitute_failure_caused_by_new_001a_files",
    "substitute_failure_that_mutates_old_sealed_artifacts",
    "substitute_positive_control_unauthorized_readiness_claim",
}

NON_AUTHORIZATION_FLAGS = {
    "runtime_authorized",
    "bridge_runtime_authorized",
    "gate4_execution_authorized",
    "implementation_authorized",
    "mechanism_validity_authorized",
    "theory_validity_authorized",
    "architecture_correctness_authorized",
    "agency_authorized",
    "selfhood_authorized",
    "consciousness_authorized",
    "emotion_authorized",
    "relationship_learning_authorized",
    "stable_user_benefit_authorized",
}


def _runner():
    return importlib.import_module("ego_mainline_known_failure_triage_001a.runner")


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_materialized_outputs_exist_parse_and_have_provenance():
    runner = _runner()

    assert DOC.exists()
    assert ARTIFACT_DIR.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == runner.CLAIM_CEILING

    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt", "future_task_recommendation.txt", "rollback_plan.txt"}:
        payload = _read_json(ARTIFACT_DIR / name)
        meta = payload.get("computed_evidence_provenance")
        assert isinstance(payload, dict)
        assert meta
        assert meta["producer_function"]
        assert meta["input_artifacts"]
        assert meta["run_id"]
        assert meta["seed_context_episode_ids"]
        assert meta["aggregation_rule"]
        assert meta["code_path_hash"]
        assert meta["output_artifact_path"].endswith(name)
        assert meta["output_artifact_hash"]


def test_anchor_readback_verifies_all_required_local_and_remote_refs():
    anchor = _read_json(ARTIFACT_DIR / "anchor_readback.json")

    assert anchor["dependency_closure_commit_resolved_hash"] == DEPENDENCY_CLOSURE_ANCHOR
    assert anchor["dependency_closure_remote_tag"] == DEPENDENCY_CLOSURE_REMOTE_TAG
    assert anchor["dependency_closure_remote_tag_resolved_hash"] == DEPENDENCY_CLOSURE_ANCHOR
    assert anchor["routing_commit_resolved_hash"] == ROUTING_ANCHOR
    assert anchor["routing_remote_tag"] == ROUTING_REMOTE_TAG
    assert anchor["routing_remote_tag_resolved_hash"] == ROUTING_ANCHOR
    assert anchor["admission_commit_resolved_hash"] == ADMISSION_ANCHOR
    assert anchor["admission_remote_tag"] == ADMISSION_REMOTE_TAG
    assert anchor["admission_remote_tag_resolved_hash"] == ADMISSION_ANCHOR
    assert anchor["all_required_anchors_verified"] is True


def test_full_pytest_and_isolated_reruns_are_recorded_with_exact_failed_node_ids():
    full = _read_json(ARTIFACT_DIR / "full_pytest_failure_report.json")
    isolated = _read_json(ARTIFACT_DIR / "isolated_rerun_report.json")
    observation = _read_json(ARTIFACT_DIR / "test_suite_observation.json")

    assert full["full_pytest_observation"]["exit_code"] == 1
    assert full["full_pytest_observation"]["summary"]["failed"] == 4
    assert full["full_pytest_observation"]["summary"]["passed"] == 664
    assert set(full["exact_failed_node_ids"]) == FAILED_NODE_IDS
    assert set(isolated["isolated_reruns"]) == FAILED_NODE_IDS
    assert observation["targeted_routing_test"]["summary"]["passed"] == 9
    assert observation["targeted_dependency_closure_test"]["summary"]["passed"] == 11
    assert observation["targeted_routing_test"]["exit_code"] == 0
    assert observation["targeted_dependency_closure_test"]["exit_code"] == 0


def test_failure_classification_explains_reproducibility_and_discrepancy():
    reproducibility = _read_json(ARTIFACT_DIR / "failure_reproducibility_matrix.json")
    causes = _read_json(ARTIFACT_DIR / "failure_cause_classification.json")
    discrepancy = _read_json(ARTIFACT_DIR / "failure_discrepancy_explanation.json")

    rows = reproducibility["failure_reproducibility_matrix"]
    assert set(rows) == FAILED_NODE_IDS
    assert rows[
        "tests/test_ego_mainline_admission_canonical_coverage_reference_001a.py::test_temp_run_uses_same_validators_without_remote_dependency"
    ]["reproducibility_category"] == "reproducible_current_failure"
    assert rows[
        "tests/test_ego_mainline_admission_task_card_alignment_001a.py::test_temp_run_uses_same_validators"
    ]["reproducibility_category"] == "reproducible_current_failure"
    assert rows[
        "tests/test_ego_mainline_evidence_dependency_closure_001a.py::test_callable_candidate_rejects_corrupted_inputs_without_authorizing_downstream"
    ]["reproducibility_category"] == "old_artifact_mutation_failure"
    assert rows[
        "tests/test_ego_mainline_post_admission_routing_001a.py::test_callable_candidate_rejects_corrupted_governance_inputs_without_authorizing_downstream"
    ]["reproducibility_category"] == "old_artifact_mutation_failure"

    assert causes["all_failures_classified"] is True
    assert "redundancy_contract_failure" in causes["failure_cause_classification"][
        "tests/test_ego_mainline_admission_task_card_alignment_001a.py::test_temp_run_uses_same_validators"
    ]["failure_categories"]
    assert discrepancy["discrepancy_explained"] is True
    assert discrepancy["prior_full_pytest_failed_count"] == 3
    assert discrepancy["current_full_pytest_failed_count"] == 4
    assert discrepancy["current_persistent_blocker_count_after_side_effect_restore"] == 2


def test_old_artifact_side_effect_is_recorded_and_restored():
    side_effect = _read_json(ARTIFACT_DIR / "old_artifact_side_effect_matrix.json")

    assert side_effect["old_artifact_side_effect_detected"] is True
    assert side_effect["old_artifact_side_effect_restored"] is True
    assert side_effect["final_tracked_state_clean_after_restore"] is True
    assert side_effect["side_effect_rows"][0]["path"] == (
        "artifacts/ego_mainline_admission_executable_001d_metric_provenance_repair_001f/scope_leak_report.json"
    )
    assert side_effect["side_effect_rows"][0]["mutation_class"] == "old_artifact_mutation_failure"


def test_blocker_severity_and_route_impact_remain_downstream_blocking_only():
    severity = _read_json(ARTIFACT_DIR / "blocker_severity_matrix.json")
    route = _read_json(ARTIFACT_DIR / "downstream_route_impact_matrix.json")
    result = _read_json(ARTIFACT_DIR / "result.json")

    assert severity["highest_blocker_severity"] == "blocks_Gate4_task_card_drafting"
    assert severity["blocker_counts_by_severity"]["blocks_Gate4_task_card_drafting"] == 2
    assert severity["blocker_counts_by_severity"]["repo_hygiene_blocker"] == 2
    assert route["downstream_route_impact_matrix"]["Gate4_task_card_drafting"]["status"] == "blocked_current"
    assert route["downstream_route_impact_matrix"]["Gate4_execution"]["status"] == "blocked"
    assert route["downstream_route_impact_matrix"]["bridge_runtime"]["status"] == "blocked"
    assert route["downstream_route_impact_matrix"]["EGO_runtime_implementation"]["status"] == "blocked"
    assert result["recommended_next_bounded_task"] == "bounded_old_artifact_side_effect_guard_and_redundancy_contract_repair_task"
    assert all(value is False for value in result["non_authorization_flags"].values())


def test_baselines_are_invoked_and_candidate_is_safer_than_unsafe_baselines():
    baseline = _read_json(ARTIFACT_DIR / "baseline_comparison.json")

    assert set(baseline["baselines_invoked"]) == BASELINES
    assert baseline["candidate_stricter_than_targeted_green_baseline"] is True
    assert baseline["candidate_stricter_than_unrelated_old_failure_baseline"] is True
    assert baseline["candidate_looser_than_strict_full_suite_only_for_triage"] is True
    assert baseline["candidate_exceeds_claim_ceiling_baseline"] is False
    assert baseline["baseline_results"]["strict_full_suite_failure_baseline"]["blocks_downstream_advancement"] is True
    assert baseline["baseline_results"]["claim_ceiling_baseline"]["blocks_downstream_authorization"] is True


def test_ablation_report_reruns_candidate_under_required_interventions():
    ablation = _read_json(ARTIFACT_DIR / "ablation_report.json")
    rows = {row["ablation_id"]: row for row in ablation["ablations"]}

    assert set(rows) == ABLATED_INPUTS
    assert ablation["all_ablations_reran_candidate"] is True
    assert ablation["no_ablation_authorized_forbidden_downstream"] is True
    assert ablation["all_required_degradations_observed"] is True
    for ablation_id, row in rows.items():
        assert row["candidate_rerun"] is True
        assert row["forbidden_downstream_authorized"] is False
        assert row["reason_codes_added"], ablation_id


def test_leakage_scanner_detects_positive_control_but_allows_restraint_language():
    runner = _runner()
    report = _read_json(ARTIFACT_DIR / "leakage_scan_report.json")

    assert report["positive_control_detected"] is True
    assert report["generated_artifact_unauthorized_positive_hits"] == []

    positive = runner.scan_text_for_unauthorized_claims("EGO ready", source_path="positive_control.txt")
    assert any(hit["is_unauthorized_positive_claim"] for hit in positive)
    restraint = runner.scan_text_for_unauthorized_claims(
        "No EGO readiness, bridge readiness, runtime readiness, Gate4 readiness, or implementation authorization is claimed.",
        source_path="restraint.txt",
    )
    assert not [hit for hit in restraint if hit["is_unauthorized_positive_claim"]]


def test_replay_recomputes_triage_from_serialized_state_and_observation():
    runner = _runner()
    state = _read_json(ARTIFACT_DIR / "triage_state.json")
    result = _read_json(ARTIFACT_DIR / "result.json")
    replay = _read_json(ARTIFACT_DIR / "replay_report.json")

    recomputed = runner.replay_triage_from_state(state["serialized_state"], state["observation"])

    assert replay["replay_function"] == "replay_triage_from_state"
    assert replay["recomputed_from_serialized_state_and_observation"] is True
    assert replay["replay_matches_original_decision"] is True
    assert replay["replay_only_compares_hashes_or_stored_verdict_strings"] is False
    assert recomputed["triage_verdict"] == result["triage_verdict"]
    assert recomputed["exact_failed_node_ids"] == result["exact_failed_node_ids"]
    assert recomputed["computed_reason_codes"] == result["computed_reason_codes"]
    assert recomputed["blocker_severity_matrix"] == result["blocker_severity_matrix"]
    assert recomputed["downstream_route_impact_matrix"] == result["downstream_route_impact_matrix"]


def test_callable_candidate_rejects_corrupted_inputs_without_authorizing_downstream():
    runner = _runner()
    state = runner.build_triage_state(repo_root=ROOT, output_dir=ARTIFACT_DIR, verify_remote=False)
    clean = runner.compute_candidate_triage(state["candidate_triage_inputs"], state["triage_parameters"])

    assert clean["triage_verdict"] == runner.VERDICT_PASS_WITH_BLOCKERS

    for intervention in [
        runner.intervention_remove_claim_ceiling,
        runner.intervention_remove_full_pytest_observation,
        runner.intervention_substitute_failure_caused_by_new_001a_files,
        runner.intervention_substitute_positive_control_unauthorized_readiness_claim,
    ]:
        mutated = copy.deepcopy(state)
        intervention(mutated)
        triaged = runner.compute_candidate_triage(mutated["candidate_triage_inputs"], mutated["triage_parameters"])
        assert all(value is False for value in triaged["non_authorization_flags"].values())
        assert triaged["downstream_route_impact_matrix"]["Gate4_execution"]["status"] == "blocked"
        assert triaged["downstream_route_impact_matrix"]["bridge_runtime"]["status"] == "blocked"
        assert triaged["downstream_route_impact_matrix"]["EGO_runtime_implementation"]["status"] == "blocked"
