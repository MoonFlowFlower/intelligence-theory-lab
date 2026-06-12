import copy
import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EGO-MAINLINE-POST-ADMISSION-ROUTING-001A"
ARTIFACT_DIR = ROOT / "artifacts" / "ego_mainline_post_admission_routing_001a"
DOC = ROOT / "docs" / "codex" / "tasks" / f"{TASK_ID}.md"
REQUIRED_ANCHOR = "98e51a46cd7f28f60b1851c616d4351c1cd6272f"
REQUIRED_REMOTE_TAG = "remote-anchor-bounded-admission-execution-001a-98e51a4"

REQUIRED_ARTIFACTS = {
    "result.json",
    "anchor_readback.json",
    "input_artifact_inventory.json",
    "routing_state.json",
    "routing_decision_matrix.json",
    "allowed_routes.json",
    "blocked_routes.json",
    "missing_evidence_matrix.json",
    "downstream_non_authorization_flags.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_scan_report.json",
    "replay_report.json",
    "computed_evidence_provenance.json",
    "claim_ceiling.txt",
    "next_task_recommendation.txt",
    "rollback_plan.txt",
}

ROUTE_CLASSES = {
    "governance_boundary_continuation",
    "evidence_dependency_closure",
    "Gate4_preflight_task_card_drafting",
    "theory_canonicalization_or_coverage_closure",
    "bridge_runtime_preflight",
    "EGO_runtime_implementation",
    "product_or_companion_behavior_work",
    "no_go_until_missing_evidence_closed",
}

FORBIDDEN_ROUTE_CLASSES = {
    "Gate4_preflight_task_card_drafting",
    "bridge_runtime_preflight",
    "EGO_runtime_implementation",
    "product_or_companion_behavior_work",
}

ABLATED_INPUTS = {
    "remove_prior_verdict",
    "remove_claim_ceiling",
    "remove_remote_tag_verification",
    "remove_non_proven_list",
    "remove_repository_inventory",
    "remove_forbidden_authorization_list",
    "substitute_failing_prior_verdict",
    "substitute_unverified_remote_tag",
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
    return importlib.import_module("ego_mainline_post_admission_routing_001a.runner")


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_materialized_required_outputs_exist_parse_and_have_provenance():
    runner = _runner()

    assert DOC.exists()
    assert ARTIFACT_DIR.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == runner.CLAIM_CEILING
    assert (ARTIFACT_DIR / "next_task_recommendation.txt").read_text(encoding="utf-8").strip()
    assert (ARTIFACT_DIR / "rollback_plan.txt").read_text(encoding="utf-8").strip()

    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt", "next_task_recommendation.txt", "rollback_plan.txt"}:
        payload = _read_json(ARTIFACT_DIR / name)
        assert isinstance(payload, dict)
        meta = payload.get("computed_evidence_provenance")
        assert meta
        assert meta["producer_function"]
        assert meta["input_artifacts"]
        assert meta["run_id"]
        assert meta["seed_context_episode_ids"]
        assert meta["aggregation_rule"]
        assert meta["code_path_hash"]
        assert meta["output_artifact_path"].endswith(name)
        assert meta["output_artifact_hash"]


def test_required_anchor_and_remote_tag_resolve_exactly():
    anchor = _read_json(ARTIFACT_DIR / "anchor_readback.json")

    assert anchor["required_commit"] == REQUIRED_ANCHOR
    assert anchor["required_commit_resolved_hash"] == REQUIRED_ANCHOR
    assert anchor["required_commit_resolves_exactly"] is True
    assert anchor["remote_tag"] == REQUIRED_REMOTE_TAG
    assert anchor["remote_tag_resolved_hash"] == REQUIRED_ANCHOR
    assert anchor["remote_tag_resolves_exactly"] is True
    assert anchor["prior_verdict"] == "pass_bounded_admission_execution_001a"
    assert anchor["claim_ceiling"] == "bounded admission execution evidence at the governance layer only"


def test_candidate_recommends_only_bounded_next_task_and_blocks_downstream_routes():
    runner = _runner()
    result = _read_json(ARTIFACT_DIR / "result.json")
    allowed = _read_json(ARTIFACT_DIR / "allowed_routes.json")
    blocked = _read_json(ARTIFACT_DIR / "blocked_routes.json")
    flags = _read_json(ARTIFACT_DIR / "downstream_non_authorization_flags.json")

    assert result["verdict"] == runner.VERDICT_PASS
    assert result["recommended_next_task_class"] == "evidence_dependency_closure"
    assert result["claim_ceiling"] == runner.CLAIM_CEILING
    assert 0 < result["route_confidence"]["score"] <= runner.GOVERNANCE_CONFIDENCE_CAP
    assert set(result["route_classes_considered"]) == ROUTE_CLASSES
    assert set(allowed["allowed_next_routes"]).issuperset(
        {"governance_boundary_continuation", "evidence_dependency_closure"}
    )
    assert not (set(allowed["allowed_next_routes"]) & FORBIDDEN_ROUTE_CLASSES)
    assert FORBIDDEN_ROUTE_CLASSES.issubset(set(blocked["blocked_routes"]))
    assert set(flags["downstream_non_authorization_flags"]) == NON_AUTHORIZATION_FLAGS
    assert flags["all_downstream_authorizations_false"] is True
    assert all(value is False for value in flags["downstream_non_authorization_flags"].values())


def test_baselines_are_invoked_and_candidate_is_stricter_than_verdict_only_baseline():
    baseline = _read_json(ARTIFACT_DIR / "baseline_comparison.json")

    assert baseline["baselines_invoked"] == [
        "naive_pass_to_advance_baseline",
        "claim_ceiling_baseline",
    ]
    naive = baseline["baseline_results"]["naive_pass_to_advance_baseline"]
    ceiling = baseline["baseline_results"]["claim_ceiling_baseline"]
    candidate = baseline["candidate_result"]

    assert naive["producer_function"] == "naive_pass_to_advance_baseline"
    assert naive["over_routes_from_pass_to_advance"] is True
    assert set(naive["unsafe_advanced_routes"]).issuperset(FORBIDDEN_ROUTE_CLASSES)
    assert ceiling["producer_function"] == "claim_ceiling_baseline"
    assert set(ceiling["blocked_routes"]).issuperset(FORBIDDEN_ROUTE_CLASSES)
    assert candidate["recommended_next_task_class"] == "evidence_dependency_closure"
    assert baseline["candidate_stricter_than_naive"] is True
    assert baseline["candidate_exceeds_claim_ceiling_baseline"] is False
    assert "verdict_only_over_route_blocked" in baseline["computed_reason_codes"]
    assert "claim_ceiling_blocks_downstream_authorization" in baseline["computed_reason_codes"]


def test_ablation_report_recomputes_candidate_under_required_interventions():
    ablation = _read_json(ARTIFACT_DIR / "ablation_report.json")
    rows = {row["ablation_id"]: row for row in ablation["ablations"]}

    assert set(rows) == ABLATED_INPUTS
    assert ablation["all_ablations_reran_candidate"] is True
    assert ablation["no_ablation_authorized_forbidden_downstream"] is True
    assert ablation["all_required_degradations_observed"] is True
    for ablation_id, row in rows.items():
        assert row["producer_function"] == "run_ablation_suite"
        assert row["candidate_rerun"] is True
        assert row["forbidden_downstream_authorized"] is False
        assert row["route_confidence_after"] <= row["route_confidence_before"]
        assert row["recommended_next_task_class_after"] in {
            "evidence_dependency_closure",
            "no_go_until_missing_evidence_closed",
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


def test_replay_recomputes_route_from_serialized_state_and_matches_reason_codes():
    runner = _runner()
    state = _read_json(ARTIFACT_DIR / "routing_state.json")
    matrix = _read_json(ARTIFACT_DIR / "routing_decision_matrix.json")
    replay = _read_json(ARTIFACT_DIR / "replay_report.json")

    recomputed = runner.replay_routing_from_state(state["serialized_state"], state["observation"])

    assert replay["replay_function"] == "replay_routing_from_state"
    assert replay["recomputed_from_serialized_state_and_observation"] is True
    assert replay["replay_matches_original_decision"] is True
    assert recomputed["recommended_next_task_class"] == matrix["candidate_routing"]["recommended_next_task_class"]
    assert recomputed["computed_reason_codes"] == matrix["candidate_routing"]["computed_reason_codes"]


def test_callable_candidate_rejects_corrupted_governance_inputs_without_authorizing_downstream():
    runner = _runner()
    state = runner.build_routing_state(repo_root=ROOT, output_dir=ARTIFACT_DIR, verify_remote=False)
    clean = runner.compute_candidate_routing(state["candidate_routing_inputs"], state["routing_parameters"])
    assert clean["recommended_next_task_class"] == "evidence_dependency_closure"

    for intervention in [
        runner.intervention_remove_claim_ceiling,
        runner.intervention_remove_forbidden_authorization_list,
        runner.intervention_substitute_unverified_remote_tag,
        runner.intervention_substitute_positive_control_unauthorized_readiness_claim,
    ]:
        mutated = copy.deepcopy(state)
        intervention(mutated)
        routed = runner.compute_candidate_routing(mutated["candidate_routing_inputs"], mutated["routing_parameters"])
        assert routed["recommended_next_task_class"] in {
            "evidence_dependency_closure",
            "no_go_until_missing_evidence_closed",
        }
        assert not (set(routed["allowed_next_routes"]) & FORBIDDEN_ROUTE_CLASSES)
        assert all(value is False for value in routed["downstream_non_authorization_flags"].values())


def test_protected_old_admission_artifacts_were_not_modified():
    runner = _runner()
    result = _read_json(ARTIFACT_DIR / "result.json")

    assert result["old_artifacts_modified"] is False
    assert result["protected_old_artifact_hashes_before"] == result["protected_old_artifact_hashes_after"]
    assert runner.hash_protected_old_artifacts(ROOT) == result["protected_old_artifact_hashes_after"]
