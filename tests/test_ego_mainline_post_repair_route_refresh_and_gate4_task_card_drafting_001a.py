import copy
import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EGO-MAINLINE-POST-REPAIR-ROUTE-REFRESH-AND-GATE4-PREFLIGHT-TASK-CARD-DRAFTING-001A"
ARTIFACT_DIR = ROOT / "artifacts" / "ego_mainline_post_repair_route_refresh_and_gate4_task_card_drafting_001a"
DOC = ROOT / "docs" / "codex" / "tasks" / f"{TASK_ID}.md"
GATE4_DOC = ROOT / "docs" / "codex" / "tasks" / "EGO-MAINLINE-GATE4-PREFLIGHT-TASK-CARD-001A.md"

ANCHORS = {
    "repair": "b9fe4f60774cfd2321b3fe5d166123ff96b5f224",
    "known_failure_triage": "c9bee968069f9d218c0c45a37efba092e4535156",
    "dependency_closure": "01973a538fad9c33ca2c6119a0f2c6b384602f34",
    "post_admission_routing": "4edf5cff7f89cf2cf1c6dbb15a478bbada0432aa",
    "admission_execution": "98e51a46cd7f28f60b1851c616d4351c1cd6272f",
}

REQUIRED_ARTIFACTS = {
    "result.json",
    "anchor_readback.json",
    "input_artifact_inventory.json",
    "prior_repair_evidence_summary.json",
    "prior_triage_evidence_summary.json",
    "prior_dependency_closure_summary.json",
    "prior_routing_summary.json",
    "current_test_status_matrix.json",
    "full_pytest_report.json",
    "old_artifact_guard_status.json",
    "blocker_resolution_matrix.json",
    "residual_blocker_matrix.json",
    "route_permission_matrix_after_repair.json",
    "gate4_contract_source_matrix.json",
    "gate4_task_card_generation_decision.json",
    "gate4_prerequisite_matrix.json",
    "downstream_non_authorization_flags.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_scan_report.json",
    "replay_report.json",
    "computed_evidence_provenance.json",
    "combined_state.json",
    "claim_ceiling.txt",
    "future_task_recommendation.txt",
    "rollback_plan.txt",
}

BASELINES = {
    "naive_full_suite_green_baseline",
    "stale_pre_repair_matrix_baseline",
    "strict_anchor_full_suite_guard_baseline",
    "claim_ceiling_baseline",
    "gate_contract_source_baseline",
}

ABLATIONS = {
    "remove_repair_remote_tag_verification",
    "remove_full_pytest_observation",
    "substitute_full_pytest_failure",
    "remove_old_artifact_guard_hash_observation",
    "remove_repair_result_artifact",
    "remove_known_failure_triage_classification",
    "remove_previous_dependency_closure_matrix",
    "remove_claim_ceiling",
    "substitute_stale_pre_repair_route_matrix_as_current",
    "substitute_targeted_green_full_pytest_fails",
    "remove_gate0_gate3_source_evidence",
    "remove_gate4_source_references",
    "substitute_ambiguous_gate4_contract",
    "substitute_positive_control_unauthorized_readiness_claim",
    "make_gate4_generator_attempt_to_authorize_execution",
}

NON_AUTHORIZATION_FLAGS = {
    "gate4_execution_authorized",
    "runtime_authorized",
    "bridge_runtime_authorized",
    "ego_runtime_implementation_authorized",
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
    return importlib.import_module(
        "ego_mainline_post_repair_route_refresh_and_gate4_task_card_drafting_001a.runner"
    )


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_runner_generates_required_outputs_with_callable_provenance(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"

    result = runner.run_post_repair_route_refresh(
        repo_root=ROOT,
        output_dir=out,
        verify_remote=False,
        execute_targeted_tests=False,
        execute_full_pytest=False,
        test_observation_override=runner.build_green_test_observation(),
        write_task_card=False,
    )

    assert DOC.exists()
    assert result["task_id"] == TASK_ID
    assert result["verdict"] == runner.VERDICT_PASS_GATE4_TASK_CARD_DRAFTED
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in out.iterdir()})
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == runner.CLAIM_CEILING
    assert (out / "future_task_recommendation.txt").read_text(encoding="utf-8").strip()
    assert (out / "rollback_plan.txt").read_text(encoding="utf-8").strip()

    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt", "future_task_recommendation.txt", "rollback_plan.txt"}:
        payload = _read_json(out / name)
        meta = payload["computed_evidence_provenance"]
        assert meta["producer_function"]
        assert meta["input_artifacts"]
        assert meta["run_id"]
        assert meta["seed_context_episode_ids"]
        assert meta["aggregation_rule"]
        assert meta["code_path_hash"]
        assert meta["output_artifact_path"].endswith(name)
        assert meta["output_artifact_hash"]


def test_anchor_readback_resolves_all_required_commits_exactly(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    runner.run_post_repair_route_refresh(
        repo_root=ROOT,
        output_dir=out,
        verify_remote=False,
        execute_targeted_tests=False,
        execute_full_pytest=False,
        test_observation_override=runner.build_green_test_observation(),
        write_task_card=False,
    )
    anchor = _read_json(out / "anchor_readback.json")

    for key, expected in ANCHORS.items():
        assert anchor["anchors"][key]["commit"] == expected
        assert anchor["anchors"][key]["commit_resolved_hash"] == expected
        assert anchor["anchors"][key]["remote_tag_resolved_hash"] == expected
        assert anchor["anchors"][key]["anchor_verified"] is True
    assert anchor["all_required_anchors_verified"] is True


def test_route_refresh_allows_only_gate4_task_card_drafting_and_blocks_downstream(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    result = runner.run_post_repair_route_refresh(
        repo_root=ROOT,
        output_dir=out,
        verify_remote=False,
        execute_targeted_tests=False,
        execute_full_pytest=False,
        test_observation_override=runner.build_green_test_observation(),
        write_task_card=False,
    )
    routes = _read_json(out / "route_permission_matrix_after_repair.json")
    flags = _read_json(out / "downstream_non_authorization_flags.json")

    assert result["post_repair_route_refresh_verdict"] == "Gate4_preflight_task_card_drafting_allowed_next"
    assert result["gate4_task_card_drafting_permission"] is True
    assert routes["route_permissions"]["Gate4_preflight_task_card_drafting_allowed_next"]["permission"] == "allowed_bounded_planning"
    assert routes["route_permissions"]["Gate4_execution_blocked"]["permission"] == "blocked"
    assert routes["route_permissions"]["bridge_runtime_preflight_blocked"]["permission"] == "blocked"
    assert routes["route_permissions"]["EGO_runtime_implementation_blocked"]["permission"] == "blocked"
    assert routes["route_permissions"]["product_or_companion_behavior_work_blocked"]["permission"] == "blocked"
    assert set(flags["downstream_non_authorization_flags"]) == NON_AUTHORIZATION_FLAGS
    assert flags["all_downstream_authorizations_false"] is True
    assert all(value is False for value in flags["downstream_non_authorization_flags"].values())


def test_gate4_source_is_derived_and_task_card_generation_decision_is_bounded(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    runner.run_post_repair_route_refresh(
        repo_root=ROOT,
        output_dir=out,
        verify_remote=False,
        execute_targeted_tests=False,
        execute_full_pytest=False,
        test_observation_override=runner.build_green_test_observation(),
        write_task_card=False,
    )
    source = _read_json(out / "gate4_contract_source_matrix.json")
    decision = _read_json(out / "gate4_task_card_generation_decision.json")
    prereq = _read_json(out / "gate4_prerequisite_matrix.json")

    assert source["gate4_contract_source_sufficient"] is True
    assert source["gate4_semantics_invented"] is False
    assert source["gate4_source_paths"]
    assert decision["generated_gate4_task_card_path"] == GATE4_DOC.relative_to(ROOT).as_posix()
    assert decision["gate4_execution_performed"] is False
    assert decision["generation_allowed"] is True
    assert decision["claim_ceiling"] == "bounded Gate4 preflight task-card drafting only"
    assert prereq["all_prerequisites_satisfied_for_drafting"] is True


def test_baselines_are_independent_callable_and_candidate_preserves_claim_ceiling(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    runner.run_post_repair_route_refresh(
        repo_root=ROOT,
        output_dir=out,
        verify_remote=False,
        execute_targeted_tests=False,
        execute_full_pytest=False,
        test_observation_override=runner.build_green_test_observation(),
        write_task_card=False,
    )
    baseline = _read_json(out / "baseline_comparison.json")

    assert set(baseline["baselines_invoked"]) == BASELINES
    for name in BASELINES:
        assert baseline["baseline_results"][name]["producer_function"] == name
    assert baseline["candidate_decision"]["gate4_task_card_drafting_permission"] is True
    assert baseline["candidate_decision_looser_than_strict_baseline"] is False
    assert baseline["candidate_preserves_claim_ceiling"] is True
    assert "claim_ceiling_blocks_execution_and_stronger_claims" in baseline["computed_reason_codes"]


def test_ablation_report_recomputes_route_and_generation_under_interventions(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    runner.run_post_repair_route_refresh(
        repo_root=ROOT,
        output_dir=out,
        verify_remote=False,
        execute_targeted_tests=False,
        execute_full_pytest=False,
        test_observation_override=runner.build_green_test_observation(),
        write_task_card=False,
    )
    report = _read_json(out / "ablation_report.json")
    rows = {row["ablation_id"]: row for row in report["ablations"]}

    assert set(rows) == ABLATIONS
    assert report["all_ablations_reran_route_refresh"] is True
    assert report["all_ablations_reran_gate4_generation"] is True
    assert report["no_ablation_authorized_forbidden_downstream"] is True
    assert report["all_required_degradations_observed"] is True
    for ablation_id, row in rows.items():
        assert row["producer_function"] == "run_ablation_suite"
        assert row["route_refresh_rerun"] is True
        assert row["gate4_generation_rerun"] is True
        assert row["forbidden_downstream_authorized"] is False
        assert row["resulting_route_class"] in {
            "Gate4_preflight_task_card_drafting_allowed_next",
            "Gate4_preflight_task_card_drafting_blocked_missing_gate4_contract",
            "Gate4_preflight_task_card_drafting_blocked_residual_governance_failure",
            "no_go_concrete_blocker",
        }
        assert row["reason_codes_added"], ablation_id


def test_leakage_scanner_detects_positive_control_and_allows_restraint_language(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    runner.run_post_repair_route_refresh(
        repo_root=ROOT,
        output_dir=out,
        verify_remote=False,
        execute_targeted_tests=False,
        execute_full_pytest=False,
        test_observation_override=runner.build_green_test_observation(),
        write_task_card=False,
    )
    report = _read_json(out / "leakage_scan_report.json")

    assert report["positive_control_detected"] is True
    assert report["generated_artifact_unauthorized_positive_hits"] == []
    assert report["scan_invocation_count"] >= len(REQUIRED_ARTIFACTS)

    positive = runner.scan_text_for_unauthorized_claims("Gate4 ready", source_path="positive_control.txt")
    assert any(hit["is_unauthorized_positive_claim"] for hit in positive)
    restraint = runner.scan_text_for_unauthorized_claims(
        "Gate4 execution remains blocked. This does not prove EGO readiness or consciousness.",
        source_path="restraint.txt",
    )
    assert not [hit for hit in restraint if hit["is_unauthorized_positive_claim"]]


def test_replay_recomputes_route_and_gate4_generation_from_serialized_state(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    runner.run_post_repair_route_refresh(
        repo_root=ROOT,
        output_dir=out,
        verify_remote=False,
        execute_targeted_tests=False,
        execute_full_pytest=False,
        test_observation_override=runner.build_green_test_observation(),
        write_task_card=False,
    )
    state = _read_json(out / "combined_state.json")
    result = _read_json(out / "result.json")
    replay = _read_json(out / "replay_report.json")

    recomputed = runner.replay_from_combined_state(state["serialized_state"], state["observation"])

    assert replay["replay_function"] == "replay_from_combined_state"
    assert replay["recomputed_from_serialized_state_and_observation"] is True
    assert replay["replay_matches_original_decision"] is True
    assert replay["replay_only_compares_hashes_or_stored_verdict_strings"] is False
    assert recomputed["route_refresh"]["post_repair_route_refresh_verdict"] == result["post_repair_route_refresh_verdict"]
    assert recomputed["gate4_generation_decision"]["generated_gate4_task_card_path"] == result["generated_gate4_task_card_path"]
    assert recomputed["reason_codes"] == result["computed_reason_codes"]


def test_candidate_rejects_corrupted_inputs_without_authorizing_downstream(tmp_path):
    runner = _runner()
    state = runner.build_combined_state(
        repo_root=ROOT,
        output_dir=tmp_path / "artifacts",
        verify_remote=False,
        execute_targeted_tests=False,
        execute_full_pytest=False,
        test_observation_override=runner.build_green_test_observation(),
    )
    clean = runner.compute_route_refresh(state["route_refresh_inputs"], state["route_refresh_parameters"])
    assert clean["post_repair_route_refresh_verdict"] == "Gate4_preflight_task_card_drafting_allowed_next"

    for intervention in [
        runner.intervention_remove_claim_ceiling,
        runner.intervention_remove_gate4_source_references,
        runner.intervention_substitute_full_pytest_failure,
        runner.intervention_make_gate4_generator_attempt_to_authorize_execution,
    ]:
        mutated = copy.deepcopy(state)
        intervention(mutated)
        routed = runner.compute_route_refresh(mutated["route_refresh_inputs"], mutated["route_refresh_parameters"])
        decision = runner.compute_gate4_generation_decision(mutated, routed)
        assert all(value is False for value in routed["downstream_non_authorization_flags"].values())
        assert decision["gate4_execution_performed"] is False
        assert decision["gate4_execution_authorized"] is False


def test_old_artifact_guard_hashes_remain_unchanged(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    runner.run_post_repair_route_refresh(
        repo_root=ROOT,
        output_dir=out,
        verify_remote=False,
        execute_targeted_tests=False,
        execute_full_pytest=False,
        test_observation_override=runner.build_green_test_observation(),
        write_task_card=False,
    )
    guard = _read_json(out / "old_artifact_guard_status.json")
    result = _read_json(out / "result.json")

    assert guard["old_sealed_artifacts_unchanged"] is True
    assert guard["old_artifact_mutation_detected"] is False
    assert guard["protected_old_artifact_hashes_before"] == guard["protected_old_artifact_hashes_after"]
    assert result["old_artifact_guard_status"]["old_sealed_artifacts_unchanged"] is True
