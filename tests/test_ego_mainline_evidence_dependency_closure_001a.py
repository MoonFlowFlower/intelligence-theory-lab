import copy
import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EGO-MAINLINE-EVIDENCE-DEPENDENCY-CLOSURE-001A"
ARTIFACT_DIR = ROOT / "artifacts" / "ego_mainline_evidence_dependency_closure_001a"
DOC = ROOT / "docs" / "codex" / "tasks" / f"{TASK_ID}.md"
ROUTING_ANCHOR = "4edf5cff7f89cf2cf1c6dbb15a478bbada0432aa"
ROUTING_REMOTE_TAG = "remote-anchor-post-admission-routing-001a-4edf5c"
ADMISSION_ANCHOR = "98e51a46cd7f28f60b1851c616d4351c1cd6272f"
ADMISSION_REMOTE_TAG = "remote-anchor-bounded-admission-execution-001a-98e51a4"

REQUIRED_ARTIFACTS = {
    "result.json",
    "anchor_readback.json",
    "input_artifact_inventory.json",
    "test_suite_observation.json",
    "known_failure_classification.json",
    "dependency_closure_matrix.json",
    "satisfied_dependencies.json",
    "missing_dependencies.json",
    "stale_or_conflicting_dependencies.json",
    "known_blockers.json",
    "blocker_severity_matrix.json",
    "route_permission_matrix.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_scan_report.json",
    "replay_report.json",
    "computed_evidence_provenance.json",
    "closure_state.json",
    "claim_ceiling.txt",
    "future_task_recommendation.txt",
    "required_repair_tasks.json",
    "rollback_plan.txt",
}

DEPENDENCY_CATEGORIES = {
    "anchor_integrity",
    "routing_boundary_integrity",
    "admission_execution_integrity",
    "artifact_inventory_continuity",
    "old_artifact_non_mutation",
    "test_suite_status",
    "known_failure_classification",
    "provenance_gate_continuity",
    "replay_gate_continuity",
    "leakage_gate_continuity",
    "baseline_independence_continuity",
    "ablation_intervention_continuity",
    "theory_coverage_or_canonicalization_dependencies",
    "Gate0_Gate1_Gate2_Gate3_dependency_state",
    "Gate4_preflight_prerequisites",
    "bridge_runtime_prerequisites",
    "EGO_runtime_prerequisites",
    "downstream_non_authorization_preservation",
}

ROUTE_CLASSES = {
    "evidence_dependency_closure_complete",
    "bounded_repair_task_required",
    "known_failure_triage_required",
    "Gate4_preflight_task_card_drafting_allowed_future_only",
    "theory_canonicalization_or_coverage_closure_required",
    "bridge_runtime_preflight_blocked",
    "EGO_runtime_implementation_blocked",
    "product_or_companion_behavior_work_blocked",
    "no_go_until_dependency_gap_closed",
}

ABLATION_IDS = {
    "remove_remote_routing_tag_verification",
    "remove_admission_execution_anchor_verification",
    "remove_full_pytest_observation",
    "remove_known_three_failure_classification",
    "remove_artifact_inventory",
    "remove_old_artifact_non_mutation_evidence",
    "remove_claim_ceiling",
    "remove_blocked_route_matrix",
    "substitute_failing_routing_verdict",
    "substitute_unverified_routing_commit",
    "substitute_positive_control_unauthorized_readiness_claim",
    "substitute_clean_targeted_result_while_full_suite_failures_remain",
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
    return importlib.import_module("ego_mainline_evidence_dependency_closure_001a.runner")


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_materialized_required_outputs_exist_parse_and_have_provenance():
    runner = _runner()

    assert DOC.exists()
    assert ARTIFACT_DIR.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == runner.CLAIM_CEILING
    assert (ARTIFACT_DIR / "future_task_recommendation.txt").read_text(encoding="utf-8").strip()
    assert (ARTIFACT_DIR / "rollback_plan.txt").read_text(encoding="utf-8").strip()

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


def test_required_routing_and_admission_anchors_resolve_exactly():
    anchor = _read_json(ARTIFACT_DIR / "anchor_readback.json")

    assert anchor["routing_commit"] == ROUTING_ANCHOR
    assert anchor["routing_commit_resolved_hash"] == ROUTING_ANCHOR
    assert anchor["routing_remote_tag"] == ROUTING_REMOTE_TAG
    assert anchor["routing_remote_tag_resolved_hash"] == ROUTING_ANCHOR
    assert anchor["routing_anchor_verified"] is True
    assert anchor["admission_commit"] == ADMISSION_ANCHOR
    assert anchor["admission_commit_resolved_hash"] == ADMISSION_ANCHOR
    assert anchor["admission_remote_tag"] == ADMISSION_REMOTE_TAG
    assert anchor["admission_remote_tag_resolved_hash"] == ADMISSION_ANCHOR
    assert anchor["admission_anchor_verified"] is True
    assert anchor["prior_routing_verdict"] == "post_admission_routing_001a_pass_with_bounded_next_task"
    assert anchor["prior_routing_recommendation"] == "evidence_dependency_closure"
    assert anchor["prior_routing_claim_ceiling"] == "bounded post-admission routing evidence at governance layer only"


def test_result_classifies_blockers_without_downstream_authorization():
    runner = _runner()
    result = _read_json(ARTIFACT_DIR / "result.json")
    routes = _read_json(ARTIFACT_DIR / "route_permission_matrix.json")
    flags = result["downstream_non_authorization_flags"]

    assert result["verdict"] == runner.VERDICT_PASS_WITH_BLOCKERS
    assert result["recommended_next_task_class"] in {"known_failure_triage_required", "bounded_repair_task_required"}
    assert result["claim_ceiling"] == runner.CLAIM_CEILING
    assert result["evidence_dependency_closure_complete"] is False
    assert result["known_blockers_present"] is True
    assert set(flags) == NON_AUTHORIZATION_FLAGS
    assert all(value is False for value in flags.values())
    assert set(routes["route_permissions"]) == ROUTE_CLASSES
    assert routes["route_permissions"]["bounded_repair_task_required"]["permission"] == "allowed_bounded"
    assert routes["route_permissions"]["known_failure_triage_required"]["permission"] == "allowed_bounded"
    assert routes["route_permissions"]["Gate4_preflight_task_card_drafting_allowed_future_only"]["permission"] == "blocked_current_future_only"
    assert routes["route_permissions"]["bridge_runtime_preflight_blocked"]["permission"] == "blocked"
    assert routes["route_permissions"]["EGO_runtime_implementation_blocked"]["permission"] == "blocked"
    assert routes["route_permissions"]["product_or_companion_behavior_work_blocked"]["permission"] == "blocked"


def test_dependency_matrix_tracks_satisfied_missing_and_blocked_categories():
    matrix = _read_json(ARTIFACT_DIR / "dependency_closure_matrix.json")
    missing = _read_json(ARTIFACT_DIR / "missing_dependencies.json")
    satisfied = _read_json(ARTIFACT_DIR / "satisfied_dependencies.json")
    stale = _read_json(ARTIFACT_DIR / "stale_or_conflicting_dependencies.json")
    blockers = _read_json(ARTIFACT_DIR / "known_blockers.json")

    assert set(matrix["dependencies"]) == DEPENDENCY_CATEGORIES
    assert matrix["all_required_categories_evaluated"] is True
    assert satisfied["satisfied_dependencies"]["anchor_integrity"]["status"] == "satisfied"
    assert satisfied["satisfied_dependencies"]["known_failure_classification"]["status"] == "satisfied"
    assert missing["missing_dependencies"]["test_suite_status"]["status"] == "missing_or_blocked"
    assert missing["missing_dependencies"]["Gate4_preflight_prerequisites"]["status"] == "missing_or_blocked"
    assert missing["missing_dependencies"]["bridge_runtime_prerequisites"]["status"] == "missing_or_blocked"
    assert missing["missing_dependencies"]["EGO_runtime_prerequisites"]["status"] == "missing_or_blocked"
    assert stale["stale_or_conflicting_dependencies"]["prior_dirty_state_failure"]["status"] == "resolved_in_clean_bounded_observation"
    assert len(blockers["known_blockers"]) == 2
    assert {row["current_status"] for row in blockers["known_blockers"]} == {"still_failing_in_bounded_observation"}


def test_test_suite_observation_records_targeted_pass_and_known_failures_without_full_suite_rerun():
    observation = _read_json(ARTIFACT_DIR / "test_suite_observation.json")
    known = _read_json(ARTIFACT_DIR / "known_failure_classification.json")
    rows = {row["nodeid"]: row for row in known["known_failure_classifications"]}

    assert observation["targeted_routing_test"]["exit_code"] == 0
    assert observation["targeted_routing_test"]["passed"] is True
    assert observation["known_failure_probe"]["exit_code"] != 0
    assert observation["known_failure_probe"]["summary"]["failed"] == 2
    assert observation["known_failure_probe"]["summary"]["passed"] == 1
    assert observation["full_pytest_observation"]["mode"] == "bounded_not_rerun"
    assert "old artifact" in observation["full_pytest_observation"]["reason"].lower()
    assert known["all_known_three_accounted_for"] is True
    assert known["still_failing_count"] == 2
    assert known["resolved_in_clean_bounded_observation_count"] == 1
    assert rows[
        "tests/test_ego_mainline_post_admission_routing_001a.py::test_callable_candidate_rejects_corrupted_governance_inputs_without_authorizing_downstream"
    ]["current_status"] == "resolved_in_clean_bounded_observation"


def test_baselines_are_independent_callable_and_candidate_is_stricter_than_naive():
    baseline = _read_json(ARTIFACT_DIR / "baseline_comparison.json")

    assert baseline["baselines_invoked"] == [
        "naive_clean_targeted_test_baseline",
        "full_suite_strict_baseline",
        "claim_ceiling_baseline",
    ]
    naive = baseline["baseline_results"]["naive_clean_targeted_test_baseline"]
    strict = baseline["baseline_results"]["full_suite_strict_baseline"]
    ceiling = baseline["baseline_results"]["claim_ceiling_baseline"]

    assert naive["producer_function"] == "naive_clean_targeted_test_baseline"
    assert naive["unsafe_advancement_tendency"] is True
    assert strict["producer_function"] == "full_suite_strict_baseline"
    assert strict["blocks_downstream_advancement"] is True
    assert ceiling["producer_function"] == "claim_ceiling_baseline"
    assert ceiling["blocks_downstream_authorization"] is True
    assert baseline["candidate_stricter_than_naive"] is True
    assert baseline["candidate_exceeds_claim_ceiling_baseline"] is False
    assert baseline["candidate_looser_than_full_suite_strict_only_for_classification"] is True
    assert "targeted_only_over_route_blocked" in baseline["computed_reason_codes"]
    assert "full_suite_strict_blocks_advancement_candidate_only_classifies" in baseline["computed_reason_codes"]


def test_ablation_report_recomputes_candidate_under_required_interventions():
    ablation = _read_json(ARTIFACT_DIR / "ablation_report.json")
    rows = {row["ablation_id"]: row for row in ablation["ablations"]}

    assert set(rows) == ABLATION_IDS
    assert ablation["all_ablations_reran_candidate"] is True
    assert ablation["no_ablation_authorized_forbidden_downstream"] is True
    assert ablation["all_required_degradations_observed"] is True
    for ablation_id, row in rows.items():
        assert row["producer_function"] == "run_ablation_suite"
        assert row["candidate_rerun"] is True
        assert row["forbidden_downstream_authorized"] is False
        assert row["route_confidence_after"] <= row["route_confidence_before"]
        assert row["recommended_next_task_class_after"] in {
            "known_failure_triage_required",
            "bounded_repair_task_required",
            "no_go_until_dependency_gap_closed",
        }
        assert row["reason_codes_added"], ablation_id


def test_leakage_scanner_detects_positive_control_but_allows_restraint_language():
    runner = _runner()
    report = _read_json(ARTIFACT_DIR / "leakage_scan_report.json")

    assert report["positive_control_detected"] is True
    assert report["generated_artifact_unauthorized_positive_hits"] == []
    assert report["scan_invocation_count"] >= len(REQUIRED_ARTIFACTS)

    positive = runner.scan_text_for_unauthorized_claims("EGO ready", source_path="positive_control.txt")
    assert any(hit["is_unauthorized_positive_claim"] for hit in positive)

    restraint = runner.scan_text_for_unauthorized_claims(
        "This task does not claim EGO readiness, bridge readiness, or runtime authorization.",
        source_path="restraint.txt",
    )
    assert not [hit for hit in restraint if hit["is_unauthorized_positive_claim"]]


def test_replay_recomputes_closure_from_serialized_state_and_matches_reason_codes():
    runner = _runner()
    state = _read_json(ARTIFACT_DIR / "closure_state.json")
    result = _read_json(ARTIFACT_DIR / "result.json")
    replay = _read_json(ARTIFACT_DIR / "replay_report.json")

    recomputed = runner.replay_closure_from_state(state["serialized_state"], state["observation"])

    assert replay["replay_function"] == "replay_closure_from_state"
    assert replay["recomputed_from_serialized_state_and_observation"] is True
    assert replay["replay_matches_original_decision"] is True
    assert replay["replay_only_compares_hashes_or_stored_verdict_strings"] is False
    assert recomputed["recommended_next_task_class"] == result["recommended_next_task_class"]
    assert recomputed["computed_reason_codes"] == result["computed_reason_codes"]
    assert recomputed["route_permission_matrix"]["route_permissions"] == result["route_permission_matrix"]["route_permissions"]


def test_callable_candidate_rejects_corrupted_inputs_without_authorizing_downstream():
    runner = _runner()
    state = runner.build_closure_state(repo_root=ROOT, output_dir=ARTIFACT_DIR, execute_tests=False, verify_remote=False)
    clean = runner.compute_candidate_closure(state["candidate_closure_inputs"], state["closure_parameters"])

    assert clean["recommended_next_task_class"] in {"known_failure_triage_required", "bounded_repair_task_required"}

    for intervention in [
        runner.intervention_remove_claim_ceiling,
        runner.intervention_remove_blocked_route_matrix,
        runner.intervention_substitute_unverified_routing_commit,
        runner.intervention_substitute_positive_control_unauthorized_readiness_claim,
    ]:
        mutated = copy.deepcopy(state)
        intervention(mutated)
        routed = runner.compute_candidate_closure(mutated["candidate_closure_inputs"], mutated["closure_parameters"])
        assert routed["recommended_next_task_class"] in {
            "known_failure_triage_required",
            "bounded_repair_task_required",
            "no_go_until_dependency_gap_closed",
        }
        assert all(value is False for value in routed["downstream_non_authorization_flags"].values())
        assert routed["route_permission_matrix"]["route_permissions"]["bridge_runtime_preflight_blocked"]["permission"] == "blocked"
        assert routed["route_permission_matrix"]["route_permissions"]["EGO_runtime_implementation_blocked"]["permission"] == "blocked"


def test_protected_old_artifacts_were_not_modified():
    runner = _runner()
    result = _read_json(ARTIFACT_DIR / "result.json")

    assert result["old_artifacts_modified"] is False
    assert result["protected_old_artifact_hashes_before"] == result["protected_old_artifact_hashes_after"]
    assert runner.hash_protected_old_artifacts(ROOT) == result["protected_old_artifact_hashes_after"]
