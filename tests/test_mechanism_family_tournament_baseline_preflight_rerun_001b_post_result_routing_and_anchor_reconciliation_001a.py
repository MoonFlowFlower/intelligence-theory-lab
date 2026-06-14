import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "MECHANISM-FAMILY-TOURNAMENT-BASELINE-PREFLIGHT-RERUN-001B-POST-RESULT-ROUTING-AND-ANCHOR-RECONCILIATION-001A"
TASK_DIR = ROOT / "artifacts" / "mechanism_family_tournament_baseline_preflight_rerun_001b_post_result_routing_and_anchor_reconciliation_001a"
ORIGINAL_DIR = ROOT / "artifacts" / "mechanism_family_tournament_baseline_preflight_rerun_001b"
REPORT = ROOT / "docs" / "research" / f"{TASK_ID}.md"
ORIGINAL_REPORT = ROOT / "docs" / "research" / "MECHANISM-FAMILY-TOURNAMENT-BASELINE-PREFLIGHT-RERUN-001B.md"
TARGET_COMMIT = "25bdc91280b428ff1eb8029ac7c30c9cf9c924c6"
TARGET_TAG = "remote-anchor-mechanism-family-tournament-baseline-preflight-rerun-001b-25bdc91"
EXPECTED_FAMILY_IDS = [
    "causal_world_model_control",
    "jepa_like_latent_prediction",
    "replay_consolidation_adaptation",
    "self_boundary_controllability_model",
    "viability_value_gated_prediction_action_loop",
    "social_latent_inference_without_partner_id_lookup",
]


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_anchor_readback_reconciles_original_false_fields_without_rewriting_001b():
    anchor = _load(TASK_DIR / "anchor_status_readback.json")
    conflict = _load(TASK_DIR / "original_artifact_conflict_readback.json")
    result = _load(TASK_DIR / "result.json")
    original_result = _load(ORIGINAL_DIR / "result.json")
    original_report_text = ORIGINAL_REPORT.read_text(encoding="utf-8")

    assert anchor["task_id"] == TASK_ID
    assert anchor["tag_name"] == TARGET_TAG
    assert anchor["target_commit"] == TARGET_COMMIT
    assert anchor["local_head_hash"] == TARGET_COMMIT
    assert anchor["remote_branch_hash"] == TARGET_COMMIT
    assert anchor["local_tag_hash"] == TARGET_COMMIT
    assert anchor["remote_tag_hash"] == TARGET_COMMIT
    assert anchor["local_tag_type"] == "commit"
    assert anchor["exact_match"] is True
    assert anchor["ahead_behind"] == {"ahead": 0, "behind": 0, "raw": "0\t0"}
    assert anchor["clean_worktree"] is True
    assert anchor["remote_anchor_created_by_this_task"] is False
    assert anchor["remote_anchor_verified_by_this_task"] is True

    assert original_result["remote_anchor_performed"] is False
    assert "- Remote anchor performed: `False`" in original_report_text
    assert conflict["original_result_remote_anchor_performed"] is False
    assert conflict["original_report_remote_anchor_performed"] is False
    assert conflict["original_artifacts_rewritten"] is False
    assert conflict["do_not_rewrite_original_evidence"] is True
    assert "generated before the post-result anchor readback" in conflict["reconciliation_statement"]

    assert result["anchor_status_conflict_reconciled"] is True
    assert result["original_001b_negative_evidence_preserved"] is True
    assert result["original_artifacts_rewritten"] is False
    assert result["tag_exists_and_exact_match_verified"] is True


def test_route_decision_keeps_all_current_surfaces_closed_and_blocks_same_surface_repair():
    route = _load(TASK_DIR / "route_decision.json")
    result = _load(TASK_DIR / "result.json")
    original_closed = _load(ORIGINAL_DIR / "closed_families.json")
    original_survivors = _load(ORIGINAL_DIR / "survivors.json")
    original_future = _load(ORIGINAL_DIR / "future_tournament_eligibility.json")

    assert route["task_id"] == TASK_ID
    assert route["current_six_surfaces_closed"] is True
    assert route["closed_surface_count"] == 6
    assert route["survivor_count"] == 0
    assert route["survivors"] == []
    assert route["future_tournament_eligibility"] is False
    assert route["candidate_implementation_authorized"] is False
    assert route["tournament_execution_authorized"] is False
    assert route["gate4_replacement_design_authorized"] is False
    assert route["same_surface_repair_blocked"] is True
    assert "anti-lookup generative heldout structure" in route["future_revival_requirement"]

    closed_by_id = {row["family_id"]: row for row in route["closed_surfaces"]}
    original_by_id = {row["family_id"]: row for row in original_closed["families"]}
    assert list(closed_by_id) == EXPECTED_FAMILY_IDS
    assert set(original_by_id) == set(EXPECTED_FAMILY_IDS)
    for family_id, row in closed_by_id.items():
        original_baseline = original_by_id[family_id]["best_faithful_cheap_baseline"]
        assert row["baseline_id"] == "exact_lookup"
        assert row["score"] == 1.0
        assert row["threshold"] == 0.8
        assert row["decision"] == "closed_by_faithful_cheap_baseline"
        assert original_baseline["baseline_id"] == row["baseline_id"]
        assert original_baseline["score"] == row["score"]
        assert original_baseline["threshold"] == row["threshold"]

    assert original_survivors["survivor_count"] == 0
    assert original_survivors["families"] == []
    assert original_future["eligible_for_future_tournament_execution_card"] is False
    assert original_future["tournament_execution_authorized"] is False

    assert result["six_current_surfaces_remain_closed"] is True
    assert result["same_surface_repair_blocked"] is True
    assert result["future_tournament_eligibility"] is False
    assert result["candidate_implementation_authorized"] is False
    assert result["gate4_replacement_design_authorized"] is False
    assert result["mechanism_validity_claimed"] is False


def test_report_and_artifacts_keep_claim_ceiling_and_forbidden_boundaries():
    report_text = REPORT.read_text(encoding="utf-8")
    result = _load(TASK_DIR / "result.json")

    assert "Claim ceiling: negative-evidence routing and anchor-status reconciliation only." in report_text
    assert "Original negative evidence" in report_text
    assert "Same-surface repair blocked: `true`" in report_text
    assert "no mechanism-validity claim" in report_text
    assert "Auto-Remote-Anchor decision: forbidden for this 001A amendment" in report_text

    assert result["candidate_code_created"] is False
    assert result["tournament_execution_attempted"] is False
    assert result["gate4_repair_or_rerun_attempted"] is False
    assert result["runtime_or_mainline_path_created"] is False
    assert result["stop_conditions_triggered"] == []
    assert "mechanism validity" in result["what_this_does_not_prove"]
