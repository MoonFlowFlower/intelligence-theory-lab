import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from post_bridge_admission_executable_001b.runner import run_admission_001b  # noqa: E402


TASK_ID = "POST-BRIDGE-ADMISSION-EXECUTABLE-001B"
VERDICT = "post_bridge_admission_executable_001b_pass"
CLAIM_CEILING = "bounded post-bridge admission evidence under the frozen contract only"
ARTIFACT_DIR = ROOT / "artifacts" / "post_bridge_admission_executable_001b"
TASK_CARD = ROOT / "docs" / "codex" / "tasks" / "POST-BRIDGE-ADMISSION-EXECUTABLE-001B.md"
PARENT_TASK_CARD = ROOT / "docs" / "codex" / "tasks" / "POST-BRIDGE-ADMISSION-TASK-CARD-001A.md"
PARENT_CONTRACT_HASH = "9e39feeae8c6974110832e6902bd28614d2d3b19"

REMOTE_ANCHORS = {
    "remote-anchor-001f-59ad222": "59ad22246823da107b9df4beb977fdfa34b7f986",
    "remote-anchor-001g-797fced": "797fced1f1409897d7c02bef5ebfb51a92533a3a",
}

REQUIRED_ARTIFACTS = {
    "stage0_freeze_manifest.json",
    "execution_manifest.json",
    "execution_manifest.sha256",
    "run_ledger.jsonl",
    "distribution_manifest.json",
    "serialized_state_provenance.jsonl",
    "trace.jsonl",
    "state_replay_report.json",
    "serialized_state_replay_report.json",
    "provenance_replay_report.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_report.json",
    "mutation_check_report.json",
    "protected_artifact_inventory_before.json",
    "protected_artifact_hashes_before.json",
    "protected_artifact_hashes_after.json",
    "tracked_old_artifact_mutation_report.json",
    "result.json",
    "claim_ceiling.txt",
}

REQUIRED_STAGE0_FREEZE_KEYS = {
    "task_card_hash",
    "thresholds",
    "metrics",
    "required_baselines",
    "required_ablations",
    "distribution_manifest_hash",
    "seed_families",
    "artifact_schema",
    "stop_conditions",
    "rollback_policy",
    "claim_ceiling",
}

REQUIRED_BASELINES = {
    "snapshot reload",
    "stitched-output baseline",
    "state-table lookup",
    "identity-token lookup",
    "memory-key lookup",
    "summary retrieval",
    "transcript retrieval",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "bounded-order window model order-1",
    "bounded-order window model order-2",
    "shuffled-history same-loss control",
    "behavior imitation",
    "frozen-state carryover",
    "oracle control as upper-bound/leakage only",
    "trace-only replay as hygiene only",
    "random policy",
    "fresh-agent no-carryover",
}

REQUIRED_ABLATIONS = {
    "reset all memory",
    "corrupt serialized state",
    "replace serialized state",
    "remove replay carryover",
    "remove self-boundary carryover",
    "remove viability carryover",
    "remove social-latent carryover",
    "remove identity_continuity_state",
    "remove memory_carryover_state",
    "time-shift state",
    "cross-agent state swap",
    "duplicate identity-token contrast",
    "freeze post-bridge learning",
    "remove post-bridge observation update",
    "disable action",
    "invert bridge mapping",
}

REQUIRED_CONTRASTS = {
    "same_identity_different_state",
    "different_identity_equivalent_state",
    "same_memory_key_corrupted_memory",
    "equivalent_memory_without_original_token",
    "state_replacement_with_wrong_episode",
    "cross_agent_state_swap",
    "duplicate_identity_token_contrast",
}

REQUIRED_LEAKAGE_CHECKS = {
    "hidden bridge labels",
    "identity labels",
    "memory labels",
    "split IDs",
    "fixture names",
    "artifact paths",
    "filenames",
    "future observations",
    "future partner responses",
    "later-action labels",
    "post-hoc metrics",
    "verifier-only state",
    "renderer-visible behavior",
    "test-only schema paths",
}

REQUIRED_TRACE_FIELDS = {
    "admission_run_id",
    "episode_id",
    "bridge_context_id",
    "heldout_context_id",
    "identity_token_hash",
    "memory_key_hash",
    "pre_bridge_state_hash",
    "serialized_state_hash",
    "post_bridge_state_hash",
    "counterfactual_state_hash",
    "identity_continuity_state",
    "memory_carryover_state",
    "state_field_provenance_hash",
    "post_bridge_observation_hash",
    "candidate_action_id",
    "baseline_action_id",
    "predicted_later_behavior",
    "observed_later_behavior",
    "state_replacement_delta",
    "token_equivalence_delta",
    "memory_carryover_delta",
    "trace_replay_hash",
    "state_replay_hash",
    "previous_trace_hash",
    "current_trace_hash",
    "leakage_scan_result",
    "mutation_check_after_eval",
}

REQUIRED_PROVENANCE_FIELDS = {
    "field_name",
    "field_schema_version",
    "source_trace_ids",
    "source_event_ids",
    "writer_step_id",
    "update_rule_id",
    "parent_state_hash",
    "field_value_hash",
    "allowed_persistence_reason",
    "forbidden_source_scan_result",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _canonical_sha(obj: object) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _trace_hash(row: dict) -> str:
    copy = dict(row)
    copy.pop("current_trace_hash")
    return _canonical_sha(copy)


def test_001b_run_emits_required_artifacts_under_scoped_path(tmp_path):
    assert TASK_CARD.exists()
    assert PARENT_TASK_CARD.exists()

    result = run_admission_001b(repo_root=ROOT, output_dir=tmp_path)

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == VERDICT
    assert result["bounded_pass"] is True
    assert result["artifact_dir"] == "artifacts/post_bridge_admission_executable_001b"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert all(value is False for value in result["authorization_flags"].values())
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    assert not (tmp_path / "failure_manifest.json").exists()
    assert (tmp_path / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING


def test_stage0_freeze_verifies_parent_anchors_contract_and_distribution(tmp_path):
    run_admission_001b(repo_root=ROOT, output_dir=tmp_path)

    stage0 = _read_json(tmp_path / "stage0_freeze_manifest.json")
    manifest = _read_json(tmp_path / "execution_manifest.json")
    distribution = _read_json(tmp_path / "distribution_manifest.json")

    assert stage0["stage0_freeze_before_any_executable_run"] is True
    assert stage0["executable_run_started_before_stage0"] is False
    assert set(stage0["frozen_contract_items"]) >= REQUIRED_STAGE0_FREEZE_KEYS
    assert stage0["parent_contract_verification"]["rev_parse_output"] == PARENT_CONTRACT_HASH
    assert stage0["parent_contract_verification"]["verified"] is True
    assert stage0["parent_remote_anchor_verification"]["verified"] is True
    assert stage0["parent_remote_anchor_verification"]["expected_hashes"] == REMOTE_ANCHORS
    assert stage0["parent_remote_anchor_verification"]["actual_hashes"] == REMOTE_ANCHORS
    assert stage0["distribution_manifest_hash"] == _file_sha(tmp_path / "distribution_manifest.json")
    assert stage0["claim_ceiling"] == CLAIM_CEILING

    assert distribution["minimum_train_contexts"] == 24
    assert distribution["minimum_heldout_bridge_contexts"] == 48
    assert distribution["minimum_counterfactual_state_pairs"] == 16
    assert distribution["minimum_cross_agent_state_swap_pairs"] == 16
    assert distribution["minimum_duplicate_identity_token_contrasts"] == 16
    assert distribution["minimum_independent_seed_families"] == 4
    assert distribution["actual_counts"]["train_contexts"] >= 24
    assert distribution["actual_counts"]["heldout_bridge_contexts"] >= 48
    assert distribution["actual_counts"]["counterfactual_state_pairs"] >= 16
    assert distribution["actual_counts"]["cross_agent_state_swap_pairs"] >= 16
    assert distribution["actual_counts"]["duplicate_identity_token_contrasts"] >= 16
    assert distribution["heldout_contexts_independent"] is True
    assert set(distribution["required_contrasts"]) == REQUIRED_CONTRASTS

    assert _file_sha(tmp_path / "execution_manifest.json") == (
        tmp_path / "execution_manifest.sha256"
    ).read_text(encoding="utf-8").strip()
    assert manifest["stage0_freeze_manifest_hash"] == _file_sha(
        tmp_path / "stage0_freeze_manifest.json"
    )


def test_trace_rows_and_serialized_state_provenance_are_replayable(tmp_path):
    run_admission_001b(repo_root=ROOT, output_dir=tmp_path)

    rows = _read_jsonl(tmp_path / "trace.jsonl")
    provenance_rows = _read_jsonl(tmp_path / "serialized_state_provenance.jsonl")
    state_replay = _read_json(tmp_path / "state_replay_report.json")
    serialized_replay = _read_json(tmp_path / "serialized_state_replay_report.json")
    provenance_replay = _read_json(tmp_path / "provenance_replay_report.json")

    assert len(rows) >= 48
    assert rows[0]["previous_trace_hash"] == "GENESIS"
    assert {row["admission_run_id"] for row in rows} == {"post_bridge_admission_001b_run"}
    assert len({row["heldout_context_id"] for row in rows}) >= 48
    assert len({row["serialized_state_hash"] for row in rows}) >= 16

    for row in rows:
        assert REQUIRED_TRACE_FIELDS.issubset(row)
        assert row["current_trace_hash"] == _trace_hash(row)
        assert row["trace_replay_hash"] == _canonical_sha(
            {
                "candidate_action_id": row["candidate_action_id"],
                "observed_later_behavior": row["observed_later_behavior"],
                "serialized_state_hash": row["serialized_state_hash"],
            }
        )
        assert row["state_replay_hash"] == row["post_bridge_state_hash"]
        assert row["leakage_scan_result"]["clean"] is True
        assert row["mutation_check_after_eval"]["post_eval_mutation_detected"] is False

    for previous, current in zip(rows, rows[1:]):
        assert current["previous_trace_hash"] == previous["current_trace_hash"]

    assert provenance_rows
    for row in provenance_rows:
        assert REQUIRED_PROVENANCE_FIELDS.issubset(row)
        assert row["forbidden_source_scan_result"]["clean"] is True
        assert row["field_value_hash"]
        assert row["allowed_persistence_reason"] == "canonical serialized state field required by frozen contract"

    assert state_replay["state_replay_passed"] is True
    assert serialized_replay["serialized_state_replay_passed"] is True
    assert provenance_replay["provenance_replay_passed"] is True


def test_required_baselines_do_not_match_candidate_and_diagnostics_are_not_fair(tmp_path):
    run_admission_001b(repo_root=ROOT, output_dir=tmp_path)

    report = _read_json(tmp_path / "baseline_comparison.json")
    baselines = {row["baseline_name"]: row for row in report["baselines"]}

    assert set(baselines) == REQUIRED_BASELINES
    assert report["candidate"]["post_bridge_admission_score"] == 1.0
    assert report["candidate"]["depends_on_carried_serialized_state"] is True
    assert report["baseline_gate_passed"] is True
    assert report["best_fair_baseline"]["post_bridge_admission_score"] < report["acceptance_threshold"]
    assert baselines["identity-token lookup"]["lookup_equivalence_detected"] is False
    assert baselines["memory-key lookup"]["lookup_equivalence_detected"] is False
    assert baselines["state-table lookup"]["lookup_equivalence_detected"] is False
    assert baselines["snapshot reload"]["snapshot_reload_equivalence_detected"] is False
    assert baselines["stitched-output baseline"]["stitched_output_equivalence_detected"] is False
    assert baselines["oracle control as upper-bound/leakage only"]["counts_as_fair_baseline"] is False
    assert baselines["trace-only replay as hygiene only"]["counts_as_fair_baseline"] is False


def test_required_ablations_contrasts_and_leakage_checks_pass(tmp_path):
    run_admission_001b(repo_root=ROOT, output_dir=tmp_path)

    ablation = _read_json(tmp_path / "ablation_report.json")
    leakage = _read_json(tmp_path / "leakage_report.json")
    ablations = {row["ablation_name"]: row for row in ablation["ablations"]}

    assert set(ablations) == REQUIRED_ABLATIONS
    assert ablation["ablation_gate_passed"] is True
    assert all(row["sensitive"] for row in ablations.values())
    assert all(row["post_bridge_admission_score"] < ablation["candidate_score"] for row in ablations.values())
    assert ablation["contrast_results"]["same_identity_different_state"]["sensitive"] is True
    assert ablation["contrast_results"]["different_identity_equivalent_state"]["control_passed"] is True
    assert ablation["contrast_results"]["same_memory_key_corrupted_memory"]["sensitive"] is True
    assert ablation["contrast_results"]["equivalent_memory_without_original_token"]["control_passed"] is True
    assert ablation["contrast_results"]["cross_agent_state_swap"]["sensitive"] is True
    assert ablation["contrast_results"]["duplicate_identity_token_contrast"]["control_passed"] is True

    assert leakage["leakage_gate_passed"] is True
    assert set(leakage["checks"]) == REQUIRED_LEAKAGE_CHECKS
    assert all(row["status"] == "clean" for row in leakage["check_results"])
    assert leakage["hidden_lookup_suspicion"] is False
    assert leakage["identity_token_lookup_equivalence"] is False
    assert leakage["memory_key_lookup_equivalence"] is False
    assert leakage["transcript_or_summary_retrieval_equivalence"] is False
    assert leakage["graph_cache_equivalence"] is False


def test_result_preserves_claim_ceiling_scope_and_old_artifact_immutability(tmp_path):
    run_admission_001b(repo_root=ROOT, output_dir=tmp_path)

    result = _read_json(tmp_path / "result.json")
    mutation = _read_json(tmp_path / "mutation_check_report.json")
    old_mutation = _read_json(tmp_path / "tracked_old_artifact_mutation_report.json")
    before_hashes = _read_json(tmp_path / "protected_artifact_hashes_before.json")
    after_hashes = _read_json(tmp_path / "protected_artifact_hashes_after.json")
    ledger = _read_jsonl(tmp_path / "run_ledger.jsonl")
    audit = result["anti_sycophancy_audit"]

    assert result["verdict"] == VERDICT
    assert result["bounded_pass"] is True
    assert result["layer"] == "bounded executable post-bridge admission test only"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["stop_conditions_triggered"] == []
    assert result["forbidden_claims_absent"] is True
    assert result["acceptance_gates"]["parent_remote_anchors_verified"] is True
    assert result["acceptance_gates"]["candidate_depends_on_carried_state"] is True
    assert result["acceptance_gates"]["fair_baselines_do_not_match_or_beat_candidate"] is True
    assert result["acceptance_gates"]["required_ablations_sensitive"] is True
    assert result["acceptance_gates"]["leakage_report_clean"] is True
    assert result["acceptance_gates"]["old_artifacts_not_mutated"] is True
    assert mutation["post_evaluation_mutation_check_passed"] is True
    assert old_mutation["old_artifact_mutation_detected"] is False
    assert before_hashes == after_hashes
    assert audit["strongest_baseline_explanation"]
    assert audit["strongest_reason_task_may_be_invalid"]
    assert audit["result_that_would_falsify_current_framing"]
    assert audit["evidence_that_would_still_be_insufficient"]
    assert audit["tests_mechanism_or_behavioral_resemblance"] == (
        "tests bounded post-bridge admission state-dependence evidence under a frozen "
        "synthetic contract, not mechanism validity"
    )
    assert {row["event"] for row in ledger} >= {
        "protected_old_artifact_hashes_before",
        "distribution_manifest_frozen",
        "stage0_freeze_manifest_written",
        "execution_manifest_frozen",
        "admission_trace_written",
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
