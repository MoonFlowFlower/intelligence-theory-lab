import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from same_agent_bridge_001b.runner import run_preflight_001b  # noqa: E402


TASK_ID = "SAME-AGENT-BRIDGE-EXECUTABLE-PREFLIGHT-001B"
VERDICT = "same_agent_bridge_001b_bounded_preflight_pass"
CLAIM_CEILING = "bounded same-agent bridge executable preflight evidence only"
ARTIFACT_DIR = ROOT / "artifacts" / "same_agent_bridge_001b"
TASK_CARD = ROOT / "docs" / "codex" / "tasks" / "SAME-AGENT-BRIDGE-EXECUTABLE-PREFLIGHT-001B.md"
PARENT_TASK_CARD = ROOT / "docs" / "codex" / "tasks" / "SAME-AGENT-BRIDGE-TASK-CARD-001A.md"

REQUIRED_STAGE0_FIELDS = {
    "task_card_hash",
    "bridge_environment_family",
    "bridge_boundary_definition",
    "canonical_agent_state_schema",
    "serialization_format",
    "allowed_persistence_manifest",
    "forbidden_persistence_manifest",
    "reset_boundary_definition",
    "memory_carryover_boundary_definition",
    "identity_continuity_metric",
    "state_lineage_hash_contract",
    "replay_contract",
    "leakage_controls",
    "baseline_implementation_signatures",
    "ablation_implementation_signatures",
    "metric_formulas",
    "equivalence_thresholds",
    "heldout_split",
    "seed_schedule",
    "artifact_schema",
    "rollback_policy",
    "claim_ceiling",
    "external_anchor",
}

REQUIRED_ARTIFACTS = {
    "stage0_freeze_manifest.json",
    "execution_manifest.json",
    "execution_manifest.sha256",
    "run_ledger.jsonl",
    "bridge_environment_manifest.json",
    "canonical_agent_state_schema.json",
    "allowed_persistence_manifest.json",
    "forbidden_persistence_manifest.json",
    "trace.jsonl",
    "serialized_state_trace.jsonl",
    "shared_state_trace.jsonl",
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
    "bridge_state_metadata",
    "identity_continuity_state",
    "memory_carryover_state",
    "reset_boundary_state",
}

REQUIRED_BASELINES = {
    "fresh-agent baseline with no carryover",
    "snapshot-reload baseline without active state update",
    "transcript retrieval",
    "summary retrieval",
    "state-table lookup",
    "identity-token lookup",
    "memory-key lookup",
    "static profile table",
    "partner/profile table",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "bounded-order window model order-1",
    "bounded-order window model order-2",
    "shuffled-history same-loss control",
    "behavior-only imitation",
    "stitched-output baseline with no single shared state",
    "frozen-state bridge baseline",
    "oracle bridge-state control as upper-bound/leakage only",
    "trace-only replay as hygiene only",
    "random policy",
}

REQUIRED_ABLATIONS = {
    "remove bridge state",
    "reset all memory at bridge",
    "freeze post-bridge learning",
    "corrupt serialized state",
    "replace serialized state with wrong episode state",
    "remove replay/consolidation carryover",
    "remove self-boundary carryover",
    "remove viability carryover",
    "remove social-latent carryover",
    "remove identity_continuity_state",
    "invert bridge mapping",
    "perturb post-bridge environment",
    "delayed post-bridge effect",
    "partial observability",
    "heldout bridge-context compositions",
    "counterfactual bridge contrast",
    "replace history before bridge",
    "learning freeze",
    "disable action",
}

REQUIRED_TRACE_FIELDS = {
    "bridge_run_id",
    "episode_id",
    "pre_bridge_step_id",
    "post_bridge_step_id",
    "bridge_boundary_id",
    "pre_bridge_agent_state_hash",
    "serialized_agent_state_hash",
    "post_bridge_agent_state_hash",
    "identity_continuity_state_before",
    "identity_continuity_state_after",
    "memory_carryover_state_before",
    "memory_carryover_state_after",
    "reset_boundary_state",
    "allowed_persistence_manifest_hash",
    "forbidden_persistence_manifest_hash",
    "observation_hash",
    "action_id",
    "predicted_outcome",
    "observed_outcome",
    "prediction_error",
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
    "predicted_partner_response",
    "observed_partner_response",
    "social_prediction_error",
    "social_latent_state_before",
    "social_latent_state_after",
    "interaction_policy_before",
    "interaction_policy_after",
    "later_action_eval_id",
    "gate0_to_gate1_linkage_key",
    "gate1_to_gate2_linkage_key",
    "gate2_to_gate3_linkage_key",
    "gate3_to_gate4_linkage_key",
    "gate4_to_bridge_linkage_key",
    "bridge_to_later_behavior_linkage_key",
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
    assert result["artifact_dir"] == "artifacts/same_agent_bridge_001b"
    assert all(value is False for value in result["authorization_flags"].values())
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    assert (tmp_path / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING
    assert not (tmp_path / "failure_manifest.json").exists()


def test_stage0_freeze_happens_before_bridge_run_and_fills_required_contract(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    stage0 = _read_json(tmp_path / "stage0_freeze_manifest.json")
    manifest = _read_json(tmp_path / "execution_manifest.json")

    assert stage0["stage0_frozen_before_bridge_run"] is True
    assert stage0["bridge_run_started_before_stage0"] is False
    assert REQUIRED_STAGE0_FIELDS.issubset(stage0["frozen_fields"])
    assert set(stage0["canonical_agent_state_schema"]["required_fields"]) == REQUIRED_SHARED_STATE_FIELDS
    assert set(stage0["required_baselines"]) == REQUIRED_BASELINES
    assert set(stage0["required_ablations"]) == REQUIRED_ABLATIONS
    assert stage0["single_canonical_serialized_shared_state_required"] is True
    assert stage0["hidden_profile_tables_forbidden"] is True
    assert stage0["old_artifact_mutation_is_failure"] is True
    assert stage0["claim_ceiling"] == CLAIM_CEILING
    assert _file_sha(tmp_path / "execution_manifest.json") == (
        tmp_path / "execution_manifest.sha256"
    ).read_text(encoding="utf-8").strip()
    assert manifest["freeze_manifest_hash"] == _file_sha(tmp_path / "stage0_freeze_manifest.json")


def test_trace_rows_show_one_serialized_shared_state_crossing_bridge_boundary(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    rows = _read_jsonl(tmp_path / "trace.jsonl")
    serialized_rows = _read_jsonl(tmp_path / "serialized_state_trace.jsonl")
    shared_rows = _read_jsonl(tmp_path / "shared_state_trace.jsonl")

    assert len(rows) >= 8
    assert len(rows) == len(serialized_rows) == len(shared_rows)
    assert rows[0]["previous_trace_hash"] == "GENESIS"
    assert {row["bridge_run_id"] for row in rows} == {"same_agent_bridge_001b_run"}
    assert {row["bridge_boundary_id"] for row in rows} == {"canonical_bridge_boundary_v1"}

    for row in rows:
        assert REQUIRED_TRACE_FIELDS.issubset(row)
        assert row["current_trace_hash"] == _trace_hash(row)
        assert row["pre_bridge_agent_state_hash"] == row["serialized_agent_state_hash"]
        assert row["serialized_agent_state_hash"] != row["post_bridge_agent_state_hash"]
        assert row["identity_continuity_state_before"] != row["identity_continuity_state_after"]
        assert row["memory_carryover_state_before"] != row["memory_carryover_state_after"]
        assert row["social_latent_state_before"] != row["social_latent_state_after"]
        assert row["interaction_policy_before"] != row["interaction_policy_after"]
        assert row["access_log"]["forbidden_access_used"] is False
        assert row["mutation_check_after_eval"]["post_eval_mutation_detected"] is False

    for previous, current in zip(rows, rows[1:]):
        assert current["previous_trace_hash"] == previous["current_trace_hash"]

    for row in serialized_rows:
        assert row["serialization_format"] == "canonical-json-sha256-v1"
        assert set(row["serialized_state"]["shared_state"]) == REQUIRED_SHARED_STATE_FIELDS
        assert row["serialized_agent_state_hash"] == _canonical_sha(row["serialized_state"])
        assert row["uses_single_canonical_serialized_shared_state"] is True
        assert row["hidden_profile_table_detected"] is False
        assert row["transcript_index_detected"] is False
        assert row["summary_index_detected"] is False
        assert row["second_hidden_policy_layer_detected"] is False

    for row in shared_rows:
        assert set(row["shared_state_before"]) == REQUIRED_SHARED_STATE_FIELDS
        assert set(row["shared_state_after"]) == REQUIRED_SHARED_STATE_FIELDS
        assert row["shared_state_hash_before"] == _canonical_sha(row["shared_state_before"])
        assert row["shared_state_hash_after"] == _canonical_sha(row["shared_state_after"])
        assert row["shared_state_hash_before"] != row["shared_state_hash_after"]


def test_linkage_keys_are_deterministic_label_free_collision_free_and_complete(tmp_path):
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
                row["gate4_to_bridge_linkage_key"],
                row["bridge_to_later_behavior_linkage_key"],
            ]
        )

    assert report["deterministic"] is True
    assert report["label_free"] is True
    assert report["collision_free"] is True
    assert report["collision_count"] == 0
    assert report["all_required_linkages_present"] is True
    assert len(all_keys) == len(set(all_keys))
    assert set(report["linkage_keys"]) == set(all_keys)
    serialized_inputs = json.dumps(report["linkage_derivation_inputs"]).lower()
    for forbidden in report["forbidden_label_tokens"]:
        assert forbidden not in serialized_inputs


def test_baseline_comparison_includes_required_controls_and_blocks_equivalence(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    report = _read_json(tmp_path / "baseline_comparison.json")
    baselines = {row["baseline_name"]: row for row in report["baselines"]}

    assert set(baselines) == REQUIRED_BASELINES
    assert report["candidate"]["bridge_continuity_score"] == 1.0
    assert report["baseline_gate_passed"] is True
    assert report["best_fair_baseline"]["bridge_continuity_score"] < report["acceptance_threshold"]
    assert baselines["stitched-output baseline with no single shared state"][
        "uses_single_canonical_serialized_shared_state"
    ] is False
    assert baselines["frozen-state bridge baseline"]["updates_under_post_bridge_observations"] is False
    assert baselines["oracle bridge-state control as upper-bound/leakage only"][
        "counts_as_fair_baseline"
    ] is False
    assert baselines["trace-only replay as hygiene only"]["counts_as_fair_baseline"] is False


def test_required_ablations_are_sensitive_and_map_to_bridge_failure_surfaces(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    report = _read_json(tmp_path / "ablation_report.json")
    ablations = {row["ablation_name"]: row for row in report["ablations"]}

    assert set(ablations) == REQUIRED_ABLATIONS
    assert report["ablation_gate_passed"] is True
    assert all(row["sensitive"] for row in ablations.values())
    assert all(row["bridge_continuity_score"] < report["candidate_score"] for row in ablations.values())
    assert ablations["remove bridge state"]["failure_surface"] == "bridge_state_metadata"
    assert ablations["remove identity_continuity_state"]["failure_surface"] == "identity_continuity_state"
    assert ablations["freeze post-bridge learning"]["failure_surface"] == "post_bridge_update"
    assert ablations["disable action"]["later_behavior_degraded"] is True


def test_leakage_replay_state_replay_and_mutation_reports_pass(tmp_path):
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
    assert leakage["future_observation_leakage_detected"] is False
    assert leakage["identity_token_lookup_leakage_detected"] is False
    assert replay["replay_integrity_passed"] is True
    assert replay["trace_hash_chain_replayed"] is True
    assert replay["state_replay_passed"] is True
    assert replay["serialized_state_hash_chain_replayed"] is True
    assert mutation["post_evaluation_mutation_check_passed"] is True
    assert old_mutation["old_artifact_mutation_detected"] is False
    assert old_mutation["mutated_old_artifacts"] == []
    assert before_hashes == after_hashes


def test_result_preserves_claim_ceiling_and_anti_sycophancy_boundaries(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    result = _read_json(tmp_path / "result.json")
    audit = result["anti_sycophancy_audit"]
    ledger = _read_jsonl(tmp_path / "run_ledger.jsonl")

    assert result["verdict"] == VERDICT
    assert result["bounded_pass"] is True
    assert result["layer"] == "bounded same-agent bridge executable preflight only"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["stop_conditions_triggered"] == []
    assert result["forbidden_claims_absent"] is True
    assert audit["strongest_baseline_explanation"]
    assert audit["strongest_reason_task_may_be_invalid"]
    assert audit["result_that_would_falsify_current_framing"]
    assert audit["evidence_that_would_still_be_insufficient"]
    assert audit["tests_mechanism_or_behavioral_resemblance"] == (
        "tests bounded same-agent bridge executable-preflight behavior under a "
        "synthetic state-transfer contract, not mechanism validity"
    )
    assert {row["event"] for row in ledger} >= {
        "protected_old_artifact_hashes_before",
        "stage0_freeze_manifest_written",
        "bridge_trace_written",
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
