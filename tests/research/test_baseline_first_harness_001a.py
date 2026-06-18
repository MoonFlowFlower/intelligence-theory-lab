import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_RESEARCH = ROOT / "scripts" / "research"
if str(SCRIPTS_RESEARCH) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_RESEARCH))


REQUIRED_SPEC_SHA256 = "bf48145b165c5c847cecd7ecda6c2a78818ce326c44f5ad92be391d003daf658"
SPEC_PATH = ROOT / "docs" / "research" / "MINIMAL-ENV-SPEC-001A.md"
FREEZE_PATH = ROOT / "docs" / "research" / "MINIMAL-ENV-SPEC-001A.freeze.json"


def test_live_harness_writes_required_artifacts_and_rejects_baseline_saturated(tmp_path):
    from baseline_battery_001a import MANDATORY_BASELINE_PRODUCERS
    from baseline_first_harness_001a import REQUIRED_ARTIFACT_FILENAMES, run_harness

    result = run_harness(
        spec_path=SPEC_PATH,
        freeze_path=FREEZE_PATH,
        required_spec_sha256=REQUIRED_SPEC_SHA256,
        out_dir=tmp_path,
        run_id="pytest-baseline-first-harness-001a",
    )

    assert result["final_verdict"] == "rejected_no_headroom_baseline_saturated"
    assert result["current_layer"] == "engineering-governance / Phase-0 candidate-free environment-headroom harness"
    assert result["mainline_integration_status"] == "none"
    assert result["enabled_status"] == "no runtime/mainline/admission/bridge path enabled"
    assert sorted(path.name for path in tmp_path.iterdir()) == sorted(REQUIRED_ARTIFACT_FILENAMES)

    verdict = json.loads((tmp_path / "final_verdict.json").read_text(encoding="utf-8"))
    summary = json.loads((tmp_path / "score_summary.json").read_text(encoding="utf-8"))
    registry = json.loads((tmp_path / "baseline_registry.json").read_text(encoding="utf-8"))
    evidence_rows = [
        json.loads(line)
        for line in (tmp_path / "evidence_table.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert verdict["final_verdict"] == "rejected_no_headroom_baseline_saturated"
    assert verdict["produced_by_callable_verdict"] is True
    assert summary["visible_channel_oracle_score"] == summary["strongest_fair_baseline_score"]
    assert summary["strongest_fair_baseline_producer"] == "budget_limited_belief_state_planner"
    assert registry["strongest_fair_baseline_score"] == summary["strongest_fair_baseline_score"]
    assert {row["result_name"] for row in registry["producers"]} == set(MANDATORY_BASELINE_PRODUCERS)
    assert all(row["consumed_by_final_verdict"] for row in registry["producers"])
    assert all(row["consumed_by_final_verdict"] for row in evidence_rows)
    assert summary["visible_channel_oracle_budget_faithfulness_result"] == "passed"
    assert summary["strategy_class_alignment_result"] == "passed"
    assert summary["leakage_positive_control_result"] == "passed"
    assert summary["replay_recomputation_result"] == "passed"
    assert summary["generator_source_provenance_result"] == "passed"


def test_spec_hash_mismatch_stops_before_baselines(tmp_path):
    from baseline_first_harness_001a import run_harness

    spec = tmp_path / "mutated.md"
    freeze = tmp_path / "freeze.json"
    spec.write_text("mutated spec\n", encoding="utf-8")
    shutil.copyfile(FREEZE_PATH, freeze)

    result = run_harness(
        spec_path=spec,
        freeze_path=freeze,
        required_spec_sha256=REQUIRED_SPEC_SHA256,
        out_dir=tmp_path / "out",
        run_id="pytest-hash-mismatch",
    )

    assert result["final_verdict"] == "blocked_env_spec_mutated_or_unfrozen"
    assert not (tmp_path / "out" / "evidence_table.jsonl").exists()


def test_missing_freeze_blocks_pending_canonical_readback(tmp_path):
    from baseline_first_harness_001a import run_harness

    result = run_harness(
        spec_path=SPEC_PATH,
        freeze_path=tmp_path / "missing.freeze.json",
        required_spec_sha256=REQUIRED_SPEC_SHA256,
        out_dir=tmp_path / "out",
        run_id="pytest-missing-freeze",
    )

    assert result["final_verdict"] == "blocked_pending_canonical_readback"
    assert result["terminal_reason_id"] == "freeze_readback_missing"


def test_missing_generator_provenance_blocks_before_scores():
    from baseline_first_harness_001a import minimal_verdict_context, produce_baseline_first_harness_001a_r1_verdict

    context = minimal_verdict_context()
    for row in context["evidence_table"]:
        if row["result_name"] == "generator_source_provenance_result":
            row["value"] = "missing"

    verdict = produce_baseline_first_harness_001a_r1_verdict(context["evidence_table"], context["thresholds"])

    assert verdict["final_verdict"] == "blocked_generator_provenance_missing"


def test_missing_or_unconsumed_baseline_blocks_battery():
    from baseline_first_harness_001a import minimal_verdict_context, produce_baseline_first_harness_001a_r1_verdict

    missing = minimal_verdict_context()
    missing["evidence_table"] = [
        row for row in missing["evidence_table"] if row["result_name"] != "greedy_information_gain_or_uncertainty_planner_under_budget"
    ]
    assert produce_baseline_first_harness_001a_r1_verdict(missing["evidence_table"], missing["thresholds"])["final_verdict"] == (
        "blocked_baseline_battery_incomplete"
    )

    unconsumed = minimal_verdict_context()
    for row in unconsumed["evidence_table"]:
        if row["result_name"] == "count_table":
            row["consumed_by_final_verdict"] = False
    assert produce_baseline_first_harness_001a_r1_verdict(unconsumed["evidence_table"], unconsumed["thresholds"])["final_verdict"] == (
        "blocked_baseline_battery_incomplete"
    )


def test_b1_blocks_hidden_field_access_budget_excess_and_replay_hash_only():
    from baseline_first_harness_001a import minimal_verdict_context, produce_baseline_first_harness_001a_r1_verdict

    hidden_access = minimal_verdict_context()
    hidden_access["oracle_budget_report"]["result"] = "failed"
    hidden_access["oracle_budget_report"]["failure_reason"] = "oracle_read_forbidden_field:hidden_state"
    assert produce_baseline_first_harness_001a_r1_verdict(hidden_access["evidence_table"], hidden_access["thresholds"])["final_verdict"] == (
        "blocked_oracle_not_budget_faithful"
    )

    budget_excess = minimal_verdict_context()
    budget_excess["oracle_budget_report"]["result"] = "failed"
    budget_excess["oracle_budget_report"]["failure_reason"] = "query_budget_exceeded"
    assert produce_baseline_first_harness_001a_r1_verdict(budget_excess["evidence_table"], budget_excess["thresholds"])["final_verdict"] == (
        "blocked_oracle_not_budget_faithful"
    )

    replay_hash_only = minimal_verdict_context()
    replay_hash_only["replay_report"]["result"] = "failed"
    replay_hash_only["replay_report"]["failure_reason"] = "stored_prediction_or_hash_only"
    assert produce_baseline_first_harness_001a_r1_verdict(replay_hash_only["evidence_table"], replay_hash_only["thresholds"])["final_verdict"] == (
        "blocked_replay_recompute_failure"
    )


def test_leakage_positive_control_failure_blocks():
    from baseline_first_harness_001a import minimal_verdict_context, produce_baseline_first_harness_001a_r1_verdict

    context = minimal_verdict_context()
    context["leakage_report"]["positive_control"]["detected"] = False

    verdict = produce_baseline_first_harness_001a_r1_verdict(context["evidence_table"], context["thresholds"])

    assert verdict["final_verdict"] == "blocked_leakage_control_failure"


def test_strategy_class_mismatch_blocks():
    from baseline_first_harness_001a import minimal_verdict_context, produce_baseline_first_harness_001a_r1_verdict

    context = minimal_verdict_context()
    context["strategy_class_alignment_report"]["result"] = "failed"
    context["strategy_class_alignment_report"]["same_information_boundary"] = False

    verdict = produce_baseline_first_harness_001a_r1_verdict(context["evidence_table"], context["thresholds"])

    assert verdict["final_verdict"] == "blocked_strategy_class_mismatch"


def test_handwritten_final_verdict_disagreement_blocks():
    from baseline_first_harness_001a import minimal_verdict_context, validate_handwritten_verdict_matches_callable

    context = minimal_verdict_context()

    result = validate_handwritten_verdict_matches_callable(
        handwritten_verdict="headroom_confirmed_for_route_contract_drafting_only",
        evidence_table=context["evidence_table"],
        frozen_thresholds=context["thresholds"],
    )

    assert result["final_verdict"] == "blocked_pending_canonical_readback"
    assert result["terminal_reason_id"] == "handwritten_final_verdict_disagrees_with_callable"


def test_self_check_exercises_required_failure_paths():
    from baseline_first_harness_001a import REQUIRED_SELF_CHECK_IDS, run_self_check

    result = run_self_check()

    assert result["self_check_status"] == "passed"
    assert {row["check_id"] for row in result["checks"]} == set(REQUIRED_SELF_CHECK_IDS)
    assert all(row["passed"] for row in result["checks"])
