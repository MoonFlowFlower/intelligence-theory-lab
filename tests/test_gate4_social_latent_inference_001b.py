import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gate4_social_latent_inference_001b.runner import run_preflight_001b  # noqa: E402


TASK_ID = "GATE4-SOCIAL-LATENT-INFERENCE-EXECUTABLE-PREFLIGHT-001B"
VERDICT = "gate4_social_latent_inference_001b_bounded_pass"
CLAIM_CEILING = "bounded Gate4 social-latent inference executable preflight evidence only"
ARTIFACT_DIR = ROOT / "artifacts" / "gate4_social_latent_inference_001b"
TASK_CARD = ROOT / "docs" / "GATE4-SOCIAL-LATENT-INFERENCE-EXECUTABLE-PREFLIGHT-001B.md"
PARENT_TASK_CARD = ROOT / "docs" / "GATE4-SOCIAL-LATENT-INFERENCE-TASK-CARD-001A.md"

REQUIRED_ARTIFACTS = {
    "stage0_freeze_manifest.json",
    "execution_manifest.json",
    "execution_manifest.sha256",
    "run_ledger.jsonl",
    "synthetic_partner_distribution.json",
    "trace.jsonl",
    "shared_state_trace.jsonl",
    "social_latent_state_trace.jsonl",
    "linkage_report.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_report.json",
    "replay_integrity_report.json",
    "mutation_check_report.json",
    "protected_artifact_inventory_before.json",
    "protected_artifact_hashes_before.json",
    "protected_artifact_hashes_after.json",
    "tracked_old_artifact_mutation_report.json",
    "result.json",
    "claim_ceiling.txt",
}

REQUIRED_LOOP = [
    "observe",
    "observe_social_context",
    "predict_outcome",
    "predict_partner_response",
    "select_action",
    "apply_action",
    "observe_effect",
    "observe_partner_response",
    "compute_prediction_error",
    "compute_social_prediction_error",
    "update_belief_state",
    "replay_or_consolidate",
    "update_self_boundary_state",
    "predict_viability_delta",
    "observe_viability_delta",
    "compute_viability_error",
    "update_viability_state",
    "update_social_latent_state",
    "update_action_priority",
    "update_interaction_policy",
    "select_later_action",
    "emit_hash_chained_trace",
]

REQUIRED_SHARED_STATE_FIELDS = {
    "belief_state",
    "prediction_error_state",
    "replay_memory",
    "consolidation_state",
    "controllability_model",
    "self_boundary_state",
    "viability_state",
    "viability_model",
    "action_priority_state",
    "recovery_policy_state",
    "resource_budget_state",
    "social_latent_state",
    "partner_model_state",
    "social_prediction_error_state",
    "interaction_policy_state",
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
    "fixed social script/persona policy",
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

REQUIRED_TRACE_FIELDS = {
    "gate4_run_id",
    "episode_id",
    "step_id",
    "observation_hash",
    "social_context_hash",
    "action_id",
    "predicted_outcome",
    "observed_outcome",
    "prediction_error",
    "predicted_partner_response",
    "observed_partner_response",
    "social_prediction_error",
    "belief_state_before",
    "belief_state_after",
    "replay_event_id",
    "consolidation_event_id",
    "controllability_error",
    "self_boundary_state_before",
    "self_boundary_state_after",
    "predicted_viability_delta",
    "observed_viability_delta",
    "viability_error",
    "viability_state_before",
    "viability_state_after",
    "social_latent_state_before",
    "social_latent_state_after",
    "partner_model_state",
    "action_priority_before",
    "action_priority_after",
    "interaction_policy_before",
    "interaction_policy_after",
    "later_action_eval_id",
    "gate0_to_gate1_linkage_key",
    "gate1_to_gate2_linkage_key",
    "gate2_to_gate3_linkage_key",
    "gate3_to_gate4_linkage_key",
    "gate4_to_later_action_linkage_key",
    "shared_state_hash_before_step",
    "shared_state_hash_after_step",
    "previous_trace_hash",
    "current_trace_hash",
    "access_log",
    "mutation_check_after_eval",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _canonical_sha(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _trace_hash(row: dict) -> str:
    row_without_hash = dict(row)
    row_without_hash.pop("current_trace_hash")
    return _canonical_sha(row_without_hash)


def test_001b_run_emits_required_artifacts_under_scoped_path(tmp_path):
    assert TASK_CARD.exists()
    assert PARENT_TASK_CARD.exists()

    result = run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == VERDICT
    assert result["bounded_pass"] is True
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["artifact_dir"] == "artifacts/gate4_social_latent_inference_001b"
    assert all(value is False for value in result["authorization_flags"].values())
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    assert (tmp_path / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING
    assert not (tmp_path / "failure_manifest.json").exists()


def test_stage0_freeze_manifest_records_required_contract(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    stage0 = _read_json(tmp_path / "stage0_freeze_manifest.json")
    manifest = _read_json(tmp_path / "execution_manifest.json")

    assert stage0["stage0_frozen_before_candidate_or_control_runs"] is True
    assert stage0["candidate_or_control_runs_started_before_stage0"] is False
    assert stage0["required_loop"] == REQUIRED_LOOP
    assert set(stage0["required_shared_state_fields"]) == REQUIRED_SHARED_STATE_FIELDS
    assert set(stage0["required_baselines"]) == REQUIRED_BASELINES
    assert set(stage0["required_ablations"]) == REQUIRED_ABLATIONS
    assert stage0["single_canonical_shared_state_required"] is True
    assert stage0["separate_social_tables_forbidden"] is True
    assert stage0["old_artifact_mutation_is_failure"] is True
    assert stage0["claim_ceiling"] == CLAIM_CEILING
    assert _file_sha(tmp_path / "execution_manifest.json") == (
        tmp_path / "execution_manifest.sha256"
    ).read_text(encoding="utf-8").strip()
    assert manifest["freeze_manifest_hash"] == _file_sha(tmp_path / "stage0_freeze_manifest.json")


def test_trace_rows_extend_gate0_to_gate3_loop_with_social_latent_chain(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    rows = _read_jsonl(tmp_path / "trace.jsonl")
    assert len(rows) >= 8
    assert rows[0]["previous_trace_hash"] == "GENESIS"

    for row in rows:
        assert REQUIRED_TRACE_FIELDS.issubset(row)
        assert row["loop_steps"] == REQUIRED_LOOP
        assert row["current_trace_hash"] == _trace_hash(row)
        assert row["shared_state_hash_before_step"] != row["shared_state_hash_after_step"]
        assert row["belief_state_before"] != row["belief_state_after"]
        assert row["self_boundary_state_before"] != row["self_boundary_state_after"]
        assert row["viability_state_before"] != row["viability_state_after"]
        assert row["social_latent_state_before"] != row["social_latent_state_after"]
        assert row["interaction_policy_before"] != row["interaction_policy_after"]
        assert row["social_prediction_error_to_social_latent_update_linked"] is True
        assert row["social_latent_update_to_interaction_policy_linked"] is True
        assert row["interaction_policy_to_later_action_linked"] is True
        assert row["access_log"]["forbidden_access_used"] is False
        assert row["mutation_check_after_eval"]["post_eval_mutation_detected"] is False

    for previous, current in zip(rows, rows[1:]):
        assert current["previous_trace_hash"] == previous["current_trace_hash"]


def test_shared_and_social_state_traces_preserve_one_canonical_schema(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    shared_rows = _read_jsonl(tmp_path / "shared_state_trace.jsonl")
    social_rows = _read_jsonl(tmp_path / "social_latent_state_trace.jsonl")
    assert len(shared_rows) == len(social_rows) >= 8

    for row in shared_rows:
        assert REQUIRED_SHARED_STATE_FIELDS.issubset(row["shared_state_before"])
        assert REQUIRED_SHARED_STATE_FIELDS.issubset(row["shared_state_after"])
        assert row["shared_state_hash_before_step"] == _canonical_sha(row["shared_state_before"])
        assert row["shared_state_hash_after_step"] == _canonical_sha(row["shared_state_after"])
        assert row["uses_single_canonical_shared_state_object"] is True
        assert row["separate_user_profile_table_detected"] is False
        assert row["partner_profile_table_detected"] is False
        assert row["preference_table_detected"] is False
        assert row["transcript_index_detected"] is False
        assert row["hidden_social_policy_layer_detected"] is False
        assert row["second_logic_path_detected"] is False

    for row in social_rows:
        assert row["social_latent_state_before"] != row["social_latent_state_after"]
        assert row["interaction_policy_before"] != row["interaction_policy_after"]
        assert row["social_prediction_error_used"] is True
        assert row["gate1_replay_input_used"] is True
        assert row["gate2_self_boundary_input_used"] is True
        assert row["gate3_viability_input_used"] is True


def test_linkage_report_is_label_free_and_complete(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    rows = _read_jsonl(tmp_path / "trace.jsonl")
    report = _read_json(tmp_path / "linkage_report.json")
    all_keys = []
    for row in rows:
        all_keys.extend(
            [
                row["gate0_to_gate1_linkage_key"],
                row["gate1_to_gate2_linkage_key"],
                row["gate2_to_gate3_linkage_key"],
                row["gate3_to_gate4_linkage_key"],
                row["gate4_to_later_action_linkage_key"],
            ]
        )

    assert report["deterministic"] is True
    assert report["label_free"] is True
    assert report["collision_free"] is True
    assert report["gate0_to_gate1_linkage_present"] is True
    assert report["gate1_to_gate2_linkage_present"] is True
    assert report["gate2_to_gate3_linkage_present"] is True
    assert report["gate3_to_gate4_linkage_present"] is True
    assert report["gate4_to_later_action_linkage_present"] is True
    assert report["social_prediction_error_to_social_latent_update_present"] is True
    assert report["social_latent_update_to_interaction_policy_present"] is True
    assert report["interaction_policy_update_to_later_action_present"] is True
    assert len(all_keys) == len(set(all_keys))
    assert set(report["linkage_keys"]) == set(all_keys)
    serialized_inputs = json.dumps(report["linkage_derivation_inputs"]).lower()
    for forbidden in report["forbidden_label_tokens"]:
        assert forbidden not in serialized_inputs


def test_baseline_comparison_includes_required_controls_and_excludes_oracle_replay(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    report = _read_json(tmp_path / "baseline_comparison.json")
    baselines = {row["baseline_name"]: row for row in report["baselines"]}

    assert set(baselines) == REQUIRED_BASELINES
    assert report["candidate"]["score"] == 1.0
    assert report["baseline_gate_passed"] is True
    assert report["best_fair_baseline"]["score"] < report["acceptance_threshold"]
    assert baselines["stitched-output baseline with no shared social state"][
        "uses_single_canonical_shared_state"
    ] is False
    assert baselines["Gate0/Gate1/Gate2/Gate3 policy without social_latent_state"][
        "uses_social_latent_state"
    ] is False
    assert baselines["oracle partner/social-label control as upper-bound/leakage only"][
        "counts_as_fair_baseline"
    ] is False
    assert baselines["trace-only replay as hygiene only"]["counts_as_fair_baseline"] is False


def test_required_ablations_are_sensitive_and_map_to_specific_failure_surfaces(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    report = _read_json(tmp_path / "ablation_report.json")
    ablations = {row["ablation_name"]: row for row in report["ablations"]}

    assert set(ablations) == REQUIRED_ABLATIONS
    assert report["ablation_gate_passed"] is True
    assert all(row["sensitive"] for row in ablations.values())
    assert all(row["score"] < report["candidate_score"] for row in ablations.values())
    assert ablations["remove social_prediction_error"]["failure_surface"] == "social_latent_state_update"
    assert ablations["remove Gate3 viability/action-priority input to interaction policy"][
        "failure_surface"
    ] == "interaction_policy_update"
    assert ablations["freeze shared state"]["failure_surface"] == "canonical_shared_state"


def test_leakage_replay_mutation_and_old_artifact_checks_pass(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    leakage = _read_json(tmp_path / "leakage_report.json")
    replay = _read_json(tmp_path / "replay_integrity_report.json")
    mutation = _read_json(tmp_path / "mutation_check_report.json")
    old_mutation = _read_json(tmp_path / "tracked_old_artifact_mutation_report.json")
    before_hashes = _read_json(tmp_path / "protected_artifact_hashes_before.json")
    after_hashes = _read_json(tmp_path / "protected_artifact_hashes_after.json")

    assert leakage["leakage_gate_passed"] is True
    assert leakage["forbidden_access_detected"] is False
    assert leakage["oracle_labels_available_to_candidate"] is False
    assert leakage["future_partner_response_leakage_detected"] is False
    assert replay["replay_integrity_passed"] is True
    assert replay["trace_hash_chain_replayed"] is True
    assert replay["shared_state_hash_chain_replayed"] is True
    assert replay["social_latent_state_trace_replayed"] is True
    assert mutation["post_evaluation_mutation_check_passed"] is True
    assert old_mutation["old_artifact_mutation_detected"] is False
    assert old_mutation["mutated_old_artifacts"] == []
    assert before_hashes == after_hashes


def test_result_preserves_claim_ceiling_and_stop_conditions(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    result = _read_json(tmp_path / "result.json")
    audit = result["anti_sycophancy_audit"]
    ledger = _read_jsonl(tmp_path / "run_ledger.jsonl")

    assert result["verdict"] == VERDICT
    assert result["bounded_pass"] is True
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["stop_conditions_triggered"] == []
    assert result["forbidden_claims_absent"] is True
    assert audit["strongest_baseline_explanation"]
    assert audit["strongest_reason_task_may_be_invalid"]
    assert audit["result_that_would_falsify_current_framing"]
    assert audit["evidence_that_would_still_be_insufficient"]
    assert audit["tests_mechanism_or_behavioral_resemblance"] == (
        "tests a bounded social-latent inference proxy in a scripted social process, "
        "not real-world social modeling or product behavior"
    )
    assert {row["event"] for row in ledger} >= {
        "protected_old_artifact_hashes_before",
        "stage0_freeze_manifest_written",
        "candidate_social_latent_trace_written",
        "old_artifact_hermeticity_check",
        "result_written",
    }


def test_committed_artifact_directory_contains_bounded_result_without_failure_manifest():
    result = _read_json(ARTIFACT_DIR / "result.json")

    assert ARTIFACT_DIR.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    assert result["task_id"] == TASK_ID
    assert result["verdict"] == VERDICT
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert not (ARTIFACT_DIR / "failure_manifest.json").exists()
