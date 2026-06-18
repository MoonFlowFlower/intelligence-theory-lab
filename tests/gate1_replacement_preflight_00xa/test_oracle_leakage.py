import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_answer_key_only_oracle_headroom_rejects():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context()
    context["oracle"]["visible_channel_oracle"]["metric"]["macro_f1"] = 0.55
    context["oracle"]["answer_key_oracle"]["metric"]["macro_f1"] = 1.0
    for row in context["baseline_rows_by_id"].values():
        if row["baseline_id"] in context["fair_baseline_ids"]:
            row["metric"]["macro_f1"] = 0.55

    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "rejected_answer_key_oracle_gap"
    assert verdict["terminal_reason_id"] == "headroom_is_answer_key_only"


def test_leakage_positive_control_detection_is_fail_able_and_consumed():
    from gate1_replacement_preflight_00xa.leakage import run_leakage_controls
    from gate1_replacement_preflight_00xa.spec_loader import build_candidate_free_surface_bundle

    bundle = build_candidate_free_surface_bundle(run_id="pytest-leakage", seeds=range(4001, 4017))
    result = run_leakage_controls(bundle, run_id="pytest-leakage")

    assert result["clean_scan"]["detected"] == []
    assert result["positive_control"]["injected_scan"]["detected"]
    assert result["positive_control"]["removed_scan"]["detected"] == []
    assert result["positive_control"]["consumed_by_final_verdict"] is True
    assert result["positive_control"]["detected_id"]


def test_missing_leakage_positive_control_blocks_admissibility():
    from gate1_replacement_preflight_00xa.verdict import derive_final_verdict, minimal_valid_context

    context = minimal_valid_context()
    context["leakage"]["positive_control"]["detected_id"] = None
    context["leakage"]["positive_control"]["consumed_by_final_verdict"] = False

    verdict = derive_final_verdict(context)

    assert verdict["final_verdict"] == "blocked_missing_partial_inferability_demonstration"
    assert verdict["terminal_reason_id"] == "leakage_positive_control_absent_or_unconsumed"


def test_hash_only_replay_is_rejected_when_replay_applicable():
    from gate1_replacement_preflight_00xa.replay import validate_replay_result

    result = validate_replay_result(
        {
            "applicability": "applicable_serialized_state",
            "mode": "stored_hash_compare",
            "hash_only": True,
            "recomputed_from_serialized_state": False,
            "recomputed_from_observation": False,
            "consumed_by_final_verdict": True,
        }
    )

    assert result["valid"] is False
    assert "hash_only_replay_forbidden" in result["errors"]
