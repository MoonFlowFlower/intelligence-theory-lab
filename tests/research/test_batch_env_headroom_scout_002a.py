import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_RESEARCH = ROOT / "scripts" / "research"
if str(SCRIPTS_RESEARCH) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_RESEARCH))


REQUIRED_SKETCH_FIELDS = {
    "sketch_id",
    "target_rule",
    "visible_channel_boundary",
    "legal_query_budget",
    "oracle_definition",
    "expected_strongest_cheap_baseline",
    "direct_decode_risk",
    "graph_cache_lookup_risk",
    "passive_decoder_risk",
    "metric_degeneracy_risk",
    "replay_requirement",
    "leakage_controls",
    "claim_ceiling",
    "stop_condition",
}


ALLOWED_MICRO_PROBE_VERDICTS = {
    "reject_no_headroom_likely",
    "reject_direct_decode",
    "reject_graph_cache_saturated",
    "reject_passive_decodable",
    "reject_metric_degenerate",
    "blocked_oracle_not_budget_faithful",
    "promote_to_full_harness_candidate",
}


def test_static_registry_covers_required_fields_and_rejects_known_kill_cases():
    from batch_env_headroom_scout_002a import build_sketch_registry, run_static_kill_scan

    sketches = build_sketch_registry()
    scan = run_static_kill_scan(sketches)

    assert 12 <= len(sketches) <= 24
    assert all(REQUIRED_SKETCH_FIELDS.issubset(sketch) for sketch in sketches)
    assert scan["stage"] == "stage_1_static_kill_scan"
    assert scan["survivor_count"] > 0
    assert scan["rejected_count"] + scan["survivor_count"] == len(sketches)

    by_id = {row["sketch_id"]: row for row in scan["results"]}
    assert by_id["legal_bundle_linear_sum"]["static_verdict"] == "rejected_static_kill"
    assert "legal_query_can_read_all_target_components" in by_id["legal_bundle_linear_sum"]["kill_reasons"]
    assert by_id["answer_key_oracle_surface"]["static_verdict"] == "rejected_static_kill"
    assert "oracle_needs_hidden_state_answer_key_or_future_labels" in by_id["answer_key_oracle_surface"]["kill_reasons"]
    assert by_id["context_id_lookup_surface"]["static_verdict"] == "rejected_static_kill"
    assert "visible_fields_leak_target" in by_id["context_id_lookup_surface"]["kill_reasons"]


def test_micro_probe_runs_only_static_survivors_and_uses_allowed_verdicts(tmp_path):
    from batch_env_headroom_scout_002a import run_batch_scout

    result = run_batch_scout(out_dir=tmp_path, run_id="pytest-batch-env-headroom-scout")
    survivors = {row["sketch_id"] for row in result["static_kill_scan"]["results"] if row["static_verdict"] == "survived_static_kill"}
    probed = {row["sketch_id"] for row in result["micro_probe_results"]["results"]}

    assert probed == survivors
    assert result["micro_probe_results"]["stage"] == "stage_2_micro_probe_only_for_survivors"
    assert {row["micro_probe_verdict"] for row in result["micro_probe_results"]["results"]} <= ALLOWED_MICRO_PROBE_VERDICTS
    assert "headroom_confirmed" not in json.dumps(result["micro_probe_results"])
    assert "candidate_authorized" not in json.dumps(result["micro_probe_results"])
    assert "route_tournament_authorized" not in json.dumps(result["micro_probe_results"])


def test_promotions_are_limited_and_task_cards_do_not_authorize_candidates(tmp_path):
    from batch_env_headroom_scout_002a import run_batch_scout

    result = run_batch_scout(out_dir=tmp_path, run_id="pytest-batch-env-headroom-scout")
    promoted = result["promoted_full_harness_candidates"]["promoted"]

    assert 1 <= len(promoted) <= 2
    assert all(row["micro_probe_verdict"] == "promote_to_full_harness_candidate" for row in promoted)
    assert all(row["preliminary_gap"] >= 0.08 for row in promoted)
    assert all(row["candidate_authorized"] is False for row in promoted)
    assert all(row["route_tournament_authorized"] is False for row in promoted)
    assert all(row["auto_remote_anchor"] == "forbidden" for row in promoted)

    task_cards = result["promoted_full_harness_candidates"]["full_baseline_first_harness_task_cards"]
    assert len(task_cards) == len(promoted)
    for card in task_cards:
        assert card["auto_remote_anchor"] == "forbidden"
        assert card["candidate_implementation_authorized"] is False
        assert card["route_tournament_authorized"] is False
        assert "No headroom confirmation" in card["claim_ceiling"]
        assert "budget_limited_belief_state_planner" in card["baseline_requirements"]
        assert "graph_lookup" in card["baseline_requirements"]


def test_required_artifacts_are_written_with_prior_negative_evidence_and_claim_ceiling(tmp_path):
    from batch_env_headroom_scout_002a import REQUIRED_ARTIFACT_FILENAMES, run_batch_scout

    result = run_batch_scout(out_dir=tmp_path, run_id="pytest-batch-env-headroom-scout")

    assert sorted(path.name for path in tmp_path.iterdir() if path.is_file()) == sorted(
        REQUIRED_ARTIFACT_FILENAMES + result["promoted_task_card_filenames"]
    )
    registry = json.loads((tmp_path / "sketch_registry.json").read_text(encoding="utf-8"))
    final_report = (tmp_path / "final_report.md").read_text(encoding="utf-8")

    assert registry["task_id"] == "BATCH-ENV-HEADROOM-SCOUT-002A"
    assert registry["current_layer"] == "engineering-governance / Phase-0 environment portfolio scouting"
    assert registry["mainline_integration_status"] == "none"
    assert registry["enabled_status"] == "no runtime/mainline/admission/bridge path enabled"
    assert "BASELINE-FIRST-HARNESS-001A-R1" in final_report
    assert "rejected_no_headroom_baseline_saturated" in final_report
    assert "candidate-free environment portfolio scouting only" in final_report
    assert "No headroom confirmation" in final_report


def test_static_and_probe_failure_paths_are_not_promoted(tmp_path):
    from batch_env_headroom_scout_002a import run_batch_scout

    result = run_batch_scout(out_dir=tmp_path, run_id="pytest-batch-env-headroom-scout")
    rejected = {row["sketch_id"]: row for row in result["rejected_sketches"]["rejected"]}
    promoted_ids = {row["sketch_id"] for row in result["promoted_full_harness_candidates"]["promoted"]}

    assert "legal_bundle_linear_sum" in rejected
    assert "passive_alias_probe" in rejected
    assert rejected["passive_alias_probe"]["rejection_stage"] == "micro_probe"
    assert rejected["passive_alias_probe"]["micro_probe_verdict"] == "reject_passive_decodable"
    assert "pairwise_graph_collision_probe" in rejected
    assert rejected["pairwise_graph_collision_probe"]["micro_probe_verdict"] == "reject_graph_cache_saturated"
    assert promoted_ids.isdisjoint(rejected)
