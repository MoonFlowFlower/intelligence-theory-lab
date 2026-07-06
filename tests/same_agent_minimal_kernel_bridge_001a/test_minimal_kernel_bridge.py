from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


TASK_ID = "SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A"
VERDICT_BASELINE_EQUIVALENCE = "BASELINE_EQUIVALENCE"
CLAIM_CEILING = (
    "bounded offline minimal runtime-kernel contrast evidence only; no mechanism "
    "validity, no agency, no autonomy, no subjectivity, no consciousness, no EGO "
    "readiness, and no mainline effect"
)

REQUIRED_ARTIFACTS = {
    "result.json",
    "trace.jsonl",
    "baseline_comparison.json",
    "ablation_report.json",
    "replay_report.json",
    "leakage_report.json",
    "computed_evidence_provenance.json",
    "failure_manifest.json",
    "claim_ceiling.txt",
    "collision_record.json",
    "frozen_metric_baseline_ablation_contract.json",
}

REQUIRED_BASELINES = {
    "random",
    "majority",
    "no_update",
    "episodic_traversal",
    "count_table",
    "transition_table",
    "successor_map",
    "rag_summary",
    "online_no_replay",
    "vanilla_experience_replay",
    "standard_continual_replay",
    "from_scratch_per_task",
    "strong_meta_learner",
    "batch_precompute",
    "drift_aware_regime_inferring_continual_replay",
}

REQUIRED_ABLATIONS = {
    "no_update",
    "no_memory_read",
    "no_replay",
    "corrupted_replay",
    "prediction_error_shuffle",
    "consolidation_deletion",
    "counterfactual_memory",
    "action_conditioning_disabled",
}

REQUIRED_SCORE_FIELDS = {
    "producer_function",
    "input_artifacts",
    "run_id",
    "seed_context_episode_ids",
    "aggregation_rule",
    "code_path_hash",
}


def _runner():
    from same_agent_minimal_kernel_bridge_001a import runner

    return runner


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_decisive_tiny_cpu_contrast_downgrades_when_drift_aware_baseline_ties(tmp_path):
    runner = _runner()

    run = runner.run_harness(output_dir=tmp_path / "run", persist_artifacts=False)
    result = run["result"]
    comparison = run["baseline_comparison"]

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == VERDICT_BASELINE_EQUIVALENCE
    assert result["bounded_pass"] is False
    assert result["mainline_integration_status"] == "none"
    assert result["enabled_status"] == "local_explicit_cli_only"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["candidate_score"] > 0.0
    assert comparison["missing_baseline_ids"] == []
    assert set(comparison["baseline_ids"]) == REQUIRED_BASELINES
    assert comparison["strongest_fair_baseline"]["baseline_id"] in {
        "drift_aware_regime_inferring_continual_replay",
        "batch_precompute",
        "strong_meta_learner",
    }
    assert comparison["strongest_fair_baseline"]["score"] >= result["candidate_score"] - result["equivalence_band"]
    assert any(
        "baseline_tied_or_beat_candidate" in reason
        for reason in result["stop_conditions_triggered"]
    )


def test_trace_records_ordered_live_loop_and_memory_dependent_next_action(tmp_path):
    runner = _runner()

    run = runner.run_harness(output_dir=tmp_path / "run", persist_artifacts=False)
    trace_rows = run["trace_rows"]
    replay = run["replay_report"]

    assert trace_rows
    first_step = [row for row in trace_rows if row["episode_id"] == "episode_00" and row["step_id"] == "episode_00_step_00"]
    assert [row["event_type"] for row in first_step] == [
        "observe",
        "predict",
        "act",
        "feedback",
        "prediction_error",
        "belief_or_memory_update",
        "replay_or_consolidation",
        "next_action",
    ]
    assert all(row["run_id"] == result_run_id(run) for row in first_step)
    next_action_rows = [row for row in trace_rows if row["event_type"] == "next_action"]
    assert any(row["next_action_changed_after_update"] for row in next_action_rows)
    assert all(row["action_selection_read_updated_memory"] for row in next_action_rows)
    assert replay["passed"] is True
    assert replay["uses_stored_outputs_only"] is False
    assert replay["uses_hash_only_comparison"] is False
    assert replay["recomputed_from"] == ["serialized_state", "observation", "feedback"]


def result_run_id(run: dict) -> str:
    return run["result"]["run_id"]


def test_leakage_ablation_replay_and_provenance_controls_are_computed_and_fail_able(tmp_path):
    runner = _runner()

    run = runner.run_harness(output_dir=tmp_path / "run", persist_artifacts=False)

    leakage = run["leakage_report"]
    ablation = run["ablation_report"]
    replay = run["replay_report"]
    provenance = run["computed_evidence_provenance"]

    assert leakage["clean_scan_passed"] is True
    assert leakage["positive_control_fires"] is True
    assert leakage["leakage_detected"] is False
    assert ablation["ablation_gate_passed"] is True
    assert set(ablation["ablation_ids"]) == REQUIRED_ABLATIONS
    assert all(row["reran_episodes_under_intervention"] for row in ablation["results"])
    assert ablation["counterfactual_memory"]["same_observation_different_serialized_states"] is True
    assert ablation["counterfactual_memory"]["different_action_selected"] is True
    assert replay["passed"] is True
    assert runner.verify_provenance(provenance)["passed"] is True

    for score in [run["candidate_score"], *run["baseline_comparison"]["results"]]:
        assert REQUIRED_SCORE_FIELDS <= set(score)
        assert score["code_path_hash"]
        assert score["seed_context_episode_ids"]
        assert score["consumed_by_final_verdict"] is True

    missing = runner.run_harness(
        output_dir=tmp_path / "missing",
        persist_artifacts=False,
        disabled_baselines=("drift_aware_regime_inferring_continual_replay",),
    )
    assert missing["result"]["verdict"] == "BLOCKED_MISSING_BASELINE"
    assert "missing_required_baseline:drift_aware_regime_inferring_continual_replay" in missing[
        "failure_manifest"
    ]["blocking_reasons"]

    leaked = runner.run_harness(output_dir=tmp_path / "leaked", persist_artifacts=False, force_clean_leak=True)
    assert leaked["result"]["verdict"] == "LEAKAGE_DETECTED"
    assert "clean_candidate_input_leakage_detected" in leaked["failure_manifest"]["blocking_reasons"]

    replay_failed = runner.run_harness(output_dir=tmp_path / "replay", persist_artifacts=False, tamper_replay=True)
    assert replay_failed["result"]["verdict"] == "REPLAY_INVALID"
    assert "replay_recompute_mismatch" in replay_failed["failure_manifest"]["blocking_reasons"]

    unwired = runner.run_harness(output_dir=tmp_path / "unwired", persist_artifacts=False, force_no_memory_read=True)
    assert unwired["result"]["verdict"] == "CONTRACT_NOT_WIRED"
    assert "action_selector_ignored_updated_belief_memory" in unwired["failure_manifest"]["blocking_reasons"]


def test_persisted_artifacts_parse_and_preserve_claim_ceiling(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"

    run = runner.run_harness(output_dir=out, persist_artifacts=True)

    assert REQUIRED_ARTIFACTS <= {path.name for path in out.iterdir()}
    assert not any(path.name not in REQUIRED_ARTIFACTS for path in out.iterdir())
    for artifact in REQUIRED_ARTIFACTS - {"trace.jsonl", "claim_ceiling.txt"}:
        json.loads((out / artifact).read_text(encoding="utf-8"))
    trace_rows = _read_jsonl(out / "trace.jsonl")
    result = _read_json(out / "result.json")
    failure_manifest = _read_json(out / "failure_manifest.json")

    assert len(trace_rows) == run["result"]["trace_event_count"]
    assert result["verdict"] == VERDICT_BASELINE_EQUIVALENCE
    assert failure_manifest["verdict"] == VERDICT_BASELINE_EQUIVALENCE
    assert failure_manifest["preserve_as_negative_evidence"] is True
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING
