import importlib
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EGO-MAINLINE-GATE4-PREFLIGHT-EXECUTABLE-001B"
TASK_SLUG = "ego_mainline_gate4_preflight_executable_001b"
VERDICT = "ego_mainline_gate4_preflight_executable_001b_bounded_pass"
CLAIM_CEILING = "bounded Gate4 executable preflight evidence over synthetic partner-process proxy only"
BLOCKED_VERDICT = "gate4_preflight_executable_001b_blocked_contract_discovery_required"
ARTIFACT_DIR = ROOT / "artifacts" / TASK_SLUG
TASK_CARD = ROOT / "docs" / "codex" / "tasks" / f"{TASK_ID}.md"
SOURCE_CARD = ROOT / "docs" / "codex" / "tasks" / "EGO-MAINLINE-GATE4-PREFLIGHT-TASK-CARD-001A.md"
SEALED_TAG = "remote-anchor-post-repair-gate4-task-card-001a-fe22693"
SEALED_COMMIT = "fe2269313c0f45b18ef8fadcb45f4af7e1d8b9a7"

REQUIRED_ARTIFACTS = {
    "anchor_verification.json",
    "source_contract_readback.json",
    "execution_manifest.json",
    "run_ledger.jsonl",
    "synthetic_partner_processes.json",
    "episode_manifest.json",
    "candidate_trace.jsonl",
    "candidate_state_snapshots.jsonl",
    "candidate_metric_report.json",
    "baseline_invocation_report.json",
    "baseline_metric_report.json",
    "contrast_report.json",
    "ablation_report.json",
    "leakage_scan_report.json",
    "leakage_positive_control_report.json",
    "replay_trace.jsonl",
    "replay_recomputation_report.json",
    "old_artifact_inventory_before.json",
    "old_artifact_inventory_after.json",
    "old_artifact_hash_comparison.json",
    "old_artifact_mutation_report.json",
    "computed_evidence_provenance_report.json",
    "claim_ceiling.txt",
    "result.json",
}

REQUIRED_BASELINES = {
    "partner-ID lookup",
    "static per-partner profile table",
    "preference-table lookup",
    "transcript retrieval",
    "summary retrieval",
    "bounded-order window model order-1",
    "bounded-order window model order-2",
    "shuffled-history same-loss control",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "behavior-only imitation",
    "fixed social script / persona policy",
    "frozen social-latent model",
    "Gate0/Gate1/Gate2/Gate3 policy without social_latent_state",
    "stitched-output baseline with no shared social state",
    "random policy",
    "oracle partner/social-label control as upper-bound/leakage only",
    "trace-only replay as hygiene only",
}

REQUIRED_ABLATIONS = {
    "remove social_latent_state",
    "freeze social_latent_state",
    "replace social history",
    "remove social_prediction_error",
    "invert partner response mapping",
    "remove interaction feedback",
    "remove Gate1 replay input to social update",
    "remove Gate2 self-boundary input to social update",
    "remove Gate3 viability/action-priority input to interaction policy",
    "freeze shared state",
    "disable action",
    "delayed partner response",
    "partial observability",
    "heldout partner-context-action compositions",
    "counterfactual interaction contrast",
    "perturb partner policy",
    "perturb social feedback channel",
    "learning freeze",
}

REQUIRED_PROVENANCE_KEYS = {
    "producer_function",
    "input_artifacts",
    "run_id",
    "seed_context_episode_ids",
    "aggregation_rule",
    "code_path_hash",
    "output_artifact_path",
}

POSITIVE_CONTROLS = {
    "unauthorized readiness claim",
    "oracle partner label leak",
    "partner-ID shortcut leak",
    "future-response leak",
    "hidden policy leak",
}


def _runner():
    try:
        return importlib.import_module("ego_mainline_gate4_preflight_executable_001b.runner")
    except ModuleNotFoundError as exc:
        pytest.fail(f"missing executable module for {TASK_ID}: {exc}")


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _assert_provenance(row: dict):
    assert REQUIRED_PROVENANCE_KEYS.issubset(row)
    assert row["producer_function"]
    assert row["input_artifacts"]
    assert row["run_id"]
    assert row["seed_context_episode_ids"]
    assert row["aggregation_rule"]
    assert len(row["code_path_hash"]) == 64
    assert row["output_artifact_path"]


def test_task_card_exists_and_preserves_bounded_executable_contract():
    assert TASK_CARD.exists()
    text = TASK_CARD.read_text(encoding="utf-8")

    assert TASK_ID in text
    assert "Bounded Gate4 executable preflight only" in text
    assert "Do not implement EGO runtime" in text
    assert SOURCE_CARD.relative_to(ROOT).as_posix() in text
    assert CLAIM_CEILING in text
    for name in REQUIRED_ARTIFACTS:
        assert name in text


def test_runner_emits_all_required_artifacts_with_provenance(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"

    result = runner.run_preflight_001b(repo_root=ROOT, output_dir=out, verify_remote=False)

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == VERDICT
    assert result["bounded_pass"] is True
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["artifact_dir"] == f"artifacts/{TASK_SLUG}"
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in out.iterdir()})
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING

    json_artifacts = {
        name
        for name in REQUIRED_ARTIFACTS
        if name.endswith(".json") and name not in {"claim_ceiling.txt", "run_ledger.jsonl"}
    }
    for name in json_artifacts:
        payload = _read_json(out / name)
        assert "computed_evidence_provenance" in payload, name
        _assert_provenance(payload["computed_evidence_provenance"])

    provenance = _read_json(out / "computed_evidence_provenance_report.json")
    assert provenance["all_required_artifact_provenance_present"] is True
    assert provenance["all_scores_have_metric_provenance"] is True
    assert provenance["no_literal_verdict_only_reports"] is True
    assert provenance["baseline_call_paths_verified"] is True
    assert provenance["ablation_call_paths_verified"] is True
    assert provenance["leakage_scanner_call_paths_verified"] is True
    assert provenance["replay_call_paths_verified"] is True


def test_anchor_and_source_readback_allow_execution_without_inventing_semantics(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    runner.run_preflight_001b(repo_root=ROOT, output_dir=out, verify_remote=False)

    anchor = _read_json(out / "anchor_verification.json")
    source = _read_json(out / "source_contract_readback.json")

    assert anchor["current_branch"] == "codex/meta-theory-scaffold"
    assert anchor["sealed_tag"] == SEALED_TAG
    assert anchor["expected_commit"] == SEALED_COMMIT
    assert anchor["remote_tag_resolved_hash"] == SEALED_COMMIT
    assert anchor["anchor_verified"] is True
    assert source["source_task_card_path"] == SOURCE_CARD.relative_to(ROOT).as_posix()
    assert source["source_task_card_present"] is True
    assert source["source_contract_bounded"] is True
    assert source["separate_authorization_required_by_source"] is True
    assert source["current_task_supplies_separate_bounded_authorization"] is True
    assert source["gate4_semantics_invented"] is False
    assert source["source_contract_readback_result"] == "source_contract_readback_bounded_executable"
    assert set(source["inherited_negative_evidence"]) >= {
        "graph_cache_collapse_family",
        "shuffled_same_loss_collapse",
        "order2_window_model_negative_pattern",
        "representational_gap_count_statistic_control_solved",
    }


def test_candidate_trace_preserves_one_shared_state_and_recomputable_social_update(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    runner.run_preflight_001b(repo_root=ROOT, output_dir=out, verify_remote=False)

    trace_rows = _read_jsonl(out / "candidate_trace.jsonl")
    snapshots = _read_jsonl(out / "candidate_state_snapshots.jsonl")
    metric = _read_json(out / "candidate_metric_report.json")

    assert len(trace_rows) >= 10
    assert len(snapshots) == len(trace_rows)
    assert len({row["shared_state_schema_id"] for row in trace_rows}) == 1
    assert len({row["run_id"] for row in trace_rows}) == 1
    assert trace_rows[0]["previous_trace_hash"] == "GENESIS"
    for previous, current in zip(trace_rows, trace_rows[1:]):
        assert current["previous_trace_hash"] == previous["current_trace_hash"]

    for row in trace_rows:
        assert row["synthetic_scripted_partner_process_only"] is True
        assert row["real_user_data_used"] is False
        assert row["uses_one_canonical_shared_state"] is True
        assert row["oracle_label_accessed"] is False
        assert row["future_response_accessed_before_prediction"] is False
        assert row["partner_identity_shortcut_accessed"] is False
        assert row["serialized_state_before"]
        assert row["observation"]
        assert row["candidate_action"] == row["recomputed_candidate_action"]
        assert row["social_prediction_error"] == row["recomputed_social_prediction_error"]
        assert row["social_latent_state_before"] != row["social_latent_state_after"]
        assert row["interaction_policy_before"] != row["interaction_policy_after"]
        assert row["gate0_to_gate1_linkage_key"]
        assert row["gate1_to_gate2_linkage_key"]
        assert row["gate2_to_gate3_linkage_key"]
        assert row["gate3_to_gate4_linkage_key"]
        assert row["gate4_to_later_action_linkage_key"]

    for snapshot in snapshots:
        state = snapshot["shared_state_after"]
        assert {
            "belief_state",
            "replay_memory",
            "self_boundary_state",
            "viability_state",
            "action_priority_state",
            "social_latent_state",
            "partner_model_state",
            "social_prediction_error_state",
            "interaction_policy_state",
        }.issubset(state)
        assert snapshot["profile_table_present"] is False
        assert snapshot["transcript_index_present"] is False
        assert snapshot["second_logic_path_present"] is False

    assert metric["candidate_score"] == pytest.approx(1.0)
    assert metric["candidate_metric_computed_by_callable_path"] is True
    _assert_provenance(metric["candidate_score_provenance"])


def test_required_baselines_are_callable_invoked_and_do_not_beat_candidate(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    runner.run_preflight_001b(repo_root=ROOT, output_dir=out, verify_remote=False)

    invocation = _read_json(out / "baseline_invocation_report.json")
    metrics = _read_json(out / "baseline_metric_report.json")
    baselines = {row["baseline_name"]: row for row in invocation["baseline_invocations"]}
    scores = {row["baseline_name"]: row for row in metrics["baseline_metrics"]}

    assert set(baselines) == REQUIRED_BASELINES
    assert set(scores) == REQUIRED_BASELINES
    assert invocation["all_required_baselines_callable"] is True
    assert invocation["all_required_baselines_invoked"] is True
    assert metrics["baseline_gate_passed"] is True
    assert metrics["candidate_score"] == pytest.approx(1.0)
    assert metrics["best_fair_baseline"]["score"] < metrics["candidate_score"]

    for name, row in baselines.items():
        assert row["callable_implementation"] is True, name
        assert row["invocation_count"] >= 1, name
        assert row["producer_function"], name
        assert row["static_dictionary_metric"] is False, name
        assert row["literal_verdict_only"] is False, name
    for name, row in scores.items():
        assert row["score_computed_by_callable"] is True, name
        _assert_provenance(row["score_provenance"])

    assert scores["oracle partner/social-label control as upper-bound/leakage only"][
        "counts_as_fair_baseline"
    ] is False
    assert scores["trace-only replay as hygiene only"]["counts_as_fair_baseline"] is False
    assert scores["stitched-output baseline with no shared social state"][
        "uses_one_canonical_shared_state"
    ] is False
    assert scores["Gate0/Gate1/Gate2/Gate3 policy without social_latent_state"][
        "uses_social_latent_state"
    ] is False


def test_required_ablations_rerun_real_interventions_and_degrade(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    runner.run_preflight_001b(repo_root=ROOT, output_dir=out, verify_remote=False)

    report = _read_json(out / "ablation_report.json")
    ablations = {row["ablation_name"]: row for row in report["ablations"]}

    assert set(ablations) == REQUIRED_ABLATIONS
    assert report["ablation_gate_passed"] is True
    assert report["all_ablations_reran_candidate"] is True
    assert report["candidate_score"] == pytest.approx(1.0)

    for name, row in ablations.items():
        assert row["real_intervention"] is True, name
        assert row["rerun_count"] >= 1, name
        assert row["score"] < report["candidate_score"], name
        assert row["degradation"] > 0, name
        assert row["static_report_only"] is False, name
        _assert_provenance(row["score_provenance"])

    assert ablations["remove social_prediction_error"]["failure_surface"] == "social_latent_state_update"
    assert ablations["remove Gate3 viability/action-priority input to interaction policy"][
        "failure_surface"
    ] == "interaction_policy_update"
    assert ablations["freeze shared state"]["failure_surface"] == "canonical_shared_state"


def test_leakage_scanner_detects_positive_controls_and_cleans_real_artifacts(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    runner.run_preflight_001b(repo_root=ROOT, output_dir=out, verify_remote=False)

    scan = _read_json(out / "leakage_scan_report.json")
    controls = _read_json(out / "leakage_positive_control_report.json")

    assert controls["all_positive_controls_detected"] is True
    assert set(controls["positive_controls_detected"]) == POSITIVE_CONTROLS
    assert scan["leakage_gate_passed"] is True
    assert scan["real_generated_artifacts_unauthorized_positive_hits"] == []
    assert scan["scanned_surface_count"] >= 8
    assert set(scan["scanned_surface_types"]) >= {
        "generated_markdown",
        "generated_json",
        "generated_text",
        "observations",
        "linkage_keys",
        "artifact_paths",
        "serialized_states",
        "trace_events",
    }

    direct_hits = runner.scan_payload_for_leakage(
        "Gate4 ready. oracle partner label leak through partner-ID P7 and future_response=accept; hidden policy=H1",
        source_path="positive_control.txt",
        surface_type="generated_text",
    )
    assert {hit["control_name"] for hit in direct_hits} >= POSITIVE_CONTROLS


def test_replay_recomputes_behavior_and_route_from_serialized_state_plus_observation(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    runner.run_preflight_001b(repo_root=ROOT, output_dir=out, verify_remote=False)

    trace = _read_jsonl(out / "candidate_trace.jsonl")
    replay_trace = _read_jsonl(out / "replay_trace.jsonl")
    report = _read_json(out / "replay_recomputation_report.json")

    assert len(replay_trace) == len(trace)
    assert report["replay_gate_passed"] is True
    assert report["recomputed_from_serialized_state_plus_observation"] is True
    assert report["hash_only_replay"] is False
    assert report["candidate_action_recomputed"] is True
    assert report["social_latent_state_recomputed"] is True
    assert report["prediction_error_recomputed"] is True
    assert report["route_verdict_recomputed"] is True
    assert report["state_update_to_later_behavior_linkage_recomputed"] is True

    for original, replayed in zip(trace, replay_trace):
        assert replayed["episode_id"] == original["episode_id"]
        assert replayed["recomputed_candidate_action"] == original["candidate_action"]
        assert replayed["recomputed_social_prediction_error"] == original["social_prediction_error"]
        assert replayed["recomputed_social_latent_state_after"] == original["social_latent_state_after"]
        assert replayed["recomputed_gate4_route_decision"] == original["gate4_route_decision"]
        assert replayed["recomputed_later_action"] == original["later_action"]


def test_old_artifact_guard_hashes_prior_sealed_artifacts_and_detects_no_mutation(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    runner.run_preflight_001b(repo_root=ROOT, output_dir=out, verify_remote=False)

    before = _read_json(out / "old_artifact_inventory_before.json")
    after = _read_json(out / "old_artifact_inventory_after.json")
    comparison = _read_json(out / "old_artifact_hash_comparison.json")
    mutation = _read_json(out / "old_artifact_mutation_report.json")

    assert before["old_sealed_artifact_count"] > 0
    assert after["old_sealed_artifact_count"] == before["old_sealed_artifact_count"]
    assert comparison["old_artifact_hashes_before"] == comparison["old_artifact_hashes_after"]
    assert comparison["old_artifact_mutation_detected"] is False
    assert mutation["old_artifact_mutation_detected"] is False
    assert mutation["mutated_old_artifacts"] == []
    assert mutation["unexpected_old_artifact_mutation_is_hard_failure"] is True


def test_result_aggregates_failures_without_claim_inflation(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    result = runner.run_preflight_001b(repo_root=ROOT, output_dir=out, verify_remote=False)

    artifact_result = _read_json(out / "result.json")
    assert artifact_result == result
    assert result["bounded_pass"] is True
    assert result["verdict"] == VERDICT
    assert result["layer"] == "engineering implementation + mechanism hypothesis testing"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["stop_conditions_triggered"] == []
    assert result["forbidden_claims_absent"] is True
    assert result["candidate_summary"]["uses_synthetic_scripted_partner_processes"] is True
    assert result["baseline_result"]["baseline_gate_passed"] is True
    assert result["ablation_result"]["ablation_gate_passed"] is True
    assert result["leakage_result"]["leakage_gate_passed"] is True
    assert result["replay_result"]["replay_gate_passed"] is True
    assert result["old_artifact_mutation_result"]["old_artifact_mutation_detected"] is False
    assert result["anti_sycophancy_audit"]["strongest_baseline_explanation"]
    assert result["anti_sycophancy_audit"]["strongest_reason_this_task_may_be_invalid"]
    assert result["anti_sycophancy_audit"]["what_result_would_falsify_current_framing"]
    assert result["anti_sycophancy_audit"]["what_evidence_would_still_be_insufficient"]
    assert result["anti_sycophancy_audit"]["tests_mechanism_or_behavioral_resemblance"] == (
        "testing a bounded mechanism proxy, not producing behavioral resemblance"
    )


def test_failure_path_blocks_when_fair_baseline_matches_candidate(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"
    runner.run_preflight_001b(repo_root=ROOT, output_dir=out, verify_remote=False)

    candidate = _read_json(out / "candidate_metric_report.json")
    baseline = _read_json(out / "baseline_metric_report.json")
    baseline["baseline_metrics"][0]["score"] = candidate["candidate_score"]
    baseline["baseline_metrics"][0]["matches_or_beats_candidate"] = True

    failed = runner.aggregate_result_from_reports(
        anchor=_read_json(out / "anchor_verification.json"),
        source=_read_json(out / "source_contract_readback.json"),
        candidate=candidate,
        baseline=baseline,
        ablation=_read_json(out / "ablation_report.json"),
        leakage=_read_json(out / "leakage_scan_report.json"),
        replay=_read_json(out / "replay_recomputation_report.json"),
        old_mutation=_read_json(out / "old_artifact_mutation_report.json"),
    )

    assert failed["bounded_pass"] is False
    assert failed["verdict"] == "ego_mainline_gate4_preflight_executable_001b_failed_baseline_solved"
    assert "fair baseline matched or beat candidate" in failed["stop_conditions_triggered"]


def test_contract_discovery_blocked_when_source_card_missing(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"

    result = runner.run_preflight_001b(
        repo_root=ROOT,
        output_dir=out,
        verify_remote=False,
        source_task_card_path=Path("docs/codex/tasks/DOES-NOT-EXIST.md"),
    )

    assert result["bounded_pass"] is False
    assert result["verdict"] == BLOCKED_VERDICT
    assert "source task card missing or insufficient" in result["stop_conditions_triggered"]
    assert (out / "result.json").exists()
    assert _read_json(out / "source_contract_readback.json")["source_task_card_present"] is False


def test_committed_artifact_directory_contains_bounded_result_after_execution():
    result = _read_json(ARTIFACT_DIR / "result.json")

    assert ARTIFACT_DIR.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    assert result["task_id"] == TASK_ID
    assert result["verdict"] == VERDICT
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["bounded_pass"] is True
