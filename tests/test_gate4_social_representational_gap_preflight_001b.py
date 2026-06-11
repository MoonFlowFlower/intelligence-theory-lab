import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gate4_social_representational_gap_preflight_001b.runner import run_preflight_001b  # noqa: E402


TASK_ID = "GATE4-SOCIAL-REPRESENTATIONAL-GAP-PREFLIGHT-EXECUTABLE-001B"
VERDICT = "gate4_social_rep_gap_001b_bounded_pass"
CLAIM_CEILING = "bounded Gate4 social representational-gap preflight evidence only"
ARTIFACT_DIR = ROOT / "artifacts" / "gate4_social_representational_gap_preflight_001b"
TASK_CARD = ROOT / "docs" / "GATE4-SOCIAL-REPRESENTATIONAL-GAP-PREFLIGHT-EXECUTABLE-001B.md"
PARENT_TASK_CARD = ROOT / "docs" / "GATE4-SOCIAL-REPRESENTATIONAL-GAP-PREFLIGHT-001A.md"

REQUIRED_ARTIFACTS = {
    "stage0_freeze_manifest.json",
    "execution_manifest.json",
    "execution_manifest.sha256",
    "run_ledger.jsonl",
    "synthetic_partner_distribution.json",
    "train_support_split.json",
    "heldout_split.json",
    "candidate_result.json",
    "challenger_results.json",
    "baseline_comparison.json",
    "bounded_window_model_report.json",
    "shuffled_history_control_report.json",
    "static_profile_control_report.json",
    "graph_cache_control_report.json",
    "retrieval_control_report.json",
    "leakage_report.json",
    "ablation_report.json",
    "replay_integrity_report.json",
    "mutation_check_report.json",
    "remote_anchor_verification_report.json",
    "result.json",
    "claim_ceiling.txt",
}

REQUIRED_REMOTE_ANCHORS = {
    "remote-anchor-001a-6b362e0": "6b362e0f2fe002dcc15d1d23ea5be0849af64d2c",
    "remote-anchor-001a-7046d6f": "7046d6fdf69e90154e6a0abe9a6ec6e6eda88051",
    "remote-anchor-001a-3f36ca0": "3f36ca020adeebdc3ccbd2343b1208c4fedb2f64",
    "remote-anchor-001a-693c215": "693c21567cabb07c426f2d671b30a1709b592703",
    "remote-anchor-001a-724bde8": "724bde81d9a8b7647764e4b747c4ef87c4de948f",
}

REQUIRED_CHALLENGERS = {
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "bounded_order_window_order_1",
    "bounded_order_window_order_2",
    "shuffled_history_same_loss_control",
    "static_per_partner_profile_table",
    "partner_id_lookup",
    "preference_table_lookup",
    "transcript_retrieval",
    "summary_retrieval",
    "behavior_only_imitation",
    "frozen_social_latent_model",
    "oracle_partner_social_label_upper_bound",
    "trace_only_replay_hygiene",
}

REQUIRED_DISTRIBUTION_PROPERTIES = {
    "synthetic_scripted_partner_process_only",
    "no_human_users",
    "no_persistent_personal_profile",
    "hidden_partner_state_transitions",
    "same_visible_partner_context_keys_with_different_hidden_social_dynamics",
    "delayed_partner_response_effects",
    "partial_observability",
    "heldout_partner_context_action_compositions",
    "counterfactual_interaction_contrasts",
    "partner_policy_perturbations",
    "history_replacement_hooks",
    "learning_freeze_hooks",
    "leakage_controls_for_partner_labels",
    "leakage_controls_for_fixture_names",
    "leakage_controls_for_split_ids",
    "leakage_controls_for_filenames",
    "leakage_controls_for_artifact_paths",
    "leakage_controls_for_oracle_labels",
    "leakage_controls_for_future_partner_responses",
}

REQUIRED_ABLATIONS = {
    "remove_history_beyond_order_1",
    "remove_history_beyond_order_2",
    "shuffle_history_same_loss",
    "replace_history_with_same_visible_partner_context_keys",
    "replace_history_with_different_hidden_social_dynamics",
    "remove_partner_state_update",
    "freeze_candidate_learning",
    "freeze_social_latent_state",
    "permute_partner_ids",
    "permute_preference_table_keys",
    "delete_transcript_memory",
    "delete_summary_memory",
    "delete_or_mask_partner_policy_labels",
    "perturb_partner_policy",
    "counterfactual_action_replacement",
    "counterfactual_partner_response_replacement",
}

FORBIDDEN_AUTHORIZATION_FLAGS = {
    "gate4_mechanism_execution_authorized",
    "same_agent_bridge_authorized",
    "ego_mainline_authorized",
    "companion_behavior_authorized",
    "relationship_learning_authorized",
    "user_model_authorized",
    "llm_rag_authorized",
    "emotion_system_authorized",
    "product_demo_authorized",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_001b_run_emits_required_artifacts_under_scoped_path(tmp_path):
    assert TASK_CARD.exists()
    assert PARENT_TASK_CARD.exists()

    result = run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == VERDICT
    assert result["bounded_pass"] is True
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["artifact_dir"] == "artifacts/gate4_social_representational_gap_preflight_001b"
    assert all(result["authorization_flags"][flag] is False for flag in FORBIDDEN_AUTHORIZATION_FLAGS)
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    assert (tmp_path / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING
    assert not (tmp_path / "failure_manifest.json").exists()


def test_remote_anchor_verification_uses_expected_tags_and_hashes(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    report = _read_json(tmp_path / "remote_anchor_verification_report.json")
    by_tag = {row["tag"]: row for row in report["anchors"]}

    assert report["remote_anchor_verification_pass"] is True
    assert by_tag.keys() == REQUIRED_REMOTE_ANCHORS.keys()
    for tag, expected_hash in REQUIRED_REMOTE_ANCHORS.items():
        assert by_tag[tag]["expected_hash"] == expected_hash
        assert by_tag[tag]["remote_hash"] == expected_hash
        assert by_tag[tag]["match"] is True


def test_stage0_freeze_manifest_records_contract_and_parent_evidence(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    stage0 = _read_json(tmp_path / "stage0_freeze_manifest.json")
    execution_manifest = _read_json(tmp_path / "execution_manifest.json")

    assert stage0["task_id"] == TASK_ID
    assert stage0["stage0_frozen_before_candidate_or_control_runs"] is True
    assert stage0["candidate_or_control_runs_started_before_stage0"] is False
    assert stage0["remote_anchor_verification_required"] is True
    assert stage0["parent_anchors"] == {
        "exec_001_graph_cache_collapse": "d7ffc393",
        "residue_001a_shuffled_same_loss_order2_window": "495300cb",
        "gate1_replay_consolidation_lineage_closeout": "307da77",
        "gate1_replay_consolidation_executable_preflight": "6b362e0",
        "gate2_controllability_self_boundary_executable_preflight": "7046d6f",
        "gate3_viability_functional_affect_executable_preflight": "3f36ca0",
        "gate0_gate1_gate2_gate3_canonical_micro_agent_integration": "693c215",
        "gate4_social_representational_gap_task_card": "724bde8",
    }
    assert set(stage0["required_challenger_families"]) == REQUIRED_CHALLENGERS
    assert set(stage0["required_distribution_properties"]) == REQUIRED_DISTRIBUTION_PROPERTIES
    assert set(stage0["required_ablations"]) == REQUIRED_ABLATIONS
    assert stage0["claim_ceiling"] == CLAIM_CEILING
    assert _file_sha(tmp_path / "execution_manifest.json") == (
        tmp_path / "execution_manifest.sha256"
    ).read_text(encoding="utf-8").strip()
    assert execution_manifest["freeze_manifest_hash"] == _file_sha(
        tmp_path / "stage0_freeze_manifest.json"
    )


def test_distribution_has_synthetic_hidden_dynamics_and_heldout_compositions(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    distribution = _read_json(tmp_path / "synthetic_partner_distribution.json")
    train = _read_json(tmp_path / "train_support_split.json")
    heldout = _read_json(tmp_path / "heldout_split.json")

    assert distribution["terminology_firewall"]["synthetic_partner_process_only"] is True
    assert distribution["terminology_firewall"]["no_real_world_participants"] is True
    assert set(distribution["properties_satisfied"]) == REQUIRED_DISTRIBUTION_PROPERTIES
    assert distribution["same_visible_keys_different_hidden_dynamics_verified"] is True
    assert distribution["delayed_partner_response_effects_verified"] is True
    assert distribution["partial_observability_verified"] is True
    assert distribution["counterfactual_interaction_contrasts_verified"] is True
    assert distribution["partner_policy_perturbations_verified"] is True
    assert train["split_name"] == "train_support"
    assert heldout["split_name"] == "heldout_partner_context_action_compositions"
    assert train["case_count"] > 0
    assert heldout["case_count"] > 0
    assert heldout["exact_history_overlap_with_train"] == 0


def test_candidate_beats_all_fair_challengers_while_oracle_and_replay_are_excluded(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    candidate = _read_json(tmp_path / "candidate_result.json")
    challengers = _read_json(tmp_path / "challenger_results.json")
    baseline = _read_json(tmp_path / "baseline_comparison.json")
    rows = {row["challenger_family"]: row for row in challengers["challengers"]}

    assert candidate["candidate_name"] == "ordered_latent_state_preflight_witness"
    assert candidate["uses_only_allowed_history"] is True
    assert candidate["is_gate4_social_latent_runtime"] is False
    assert candidate["heldout_accuracy"] == 1.0
    assert rows.keys() == REQUIRED_CHALLENGERS
    assert challengers["all_required_challenger_families_present"] is True
    assert challengers["challenger_competence_pass"] is True
    assert baseline["baseline_gate_passed"] is True
    assert baseline["best_fair_challenger_score"] < candidate["heldout_accuracy"]
    for name, row in rows.items():
        if name in {"oracle_partner_social_label_upper_bound", "trace_only_replay_hygiene"}:
            assert row["counts_as_positive_gap_evidence"] is False
            assert row["role"] in {"upper_bound_leakage_probe_only", "hygiene_only"}
        else:
            assert row["counts_as_fair_challenger"] is True
            assert row["heldout_accuracy"] < candidate["heldout_accuracy"]
            assert row["matches_or_beats_candidate"] is False


def test_required_challenger_family_reports_preserve_specific_failure_surfaces(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    bounded_window = _read_json(tmp_path / "bounded_window_model_report.json")
    shuffled = _read_json(tmp_path / "shuffled_history_control_report.json")
    static_profile = _read_json(tmp_path / "static_profile_control_report.json")
    graph_cache = _read_json(tmp_path / "graph_cache_control_report.json")
    retrieval = _read_json(tmp_path / "retrieval_control_report.json")

    assert bounded_window["order_1"]["solved"] is False
    assert bounded_window["order_2"]["solved"] is False
    assert bounded_window["bounded_order_window_gap_verified"] is True
    assert shuffled["shuffled_history_same_loss_control"]["solved"] is False
    assert static_profile["static_per_partner_profile_table"]["solved"] is False
    assert static_profile["partner_id_lookup"]["solved"] is False
    assert static_profile["preference_table_lookup"]["solved"] is False
    assert set(graph_cache["graph_cache_family"].keys()) == {
        "graph_lookup",
        "transition_table",
        "successor_map",
        "count_table",
        "fsm_planner",
        "episodic_traversal",
    }
    assert all(row["solved"] is False for row in graph_cache["graph_cache_family"].values())
    assert retrieval["transcript_retrieval"]["solved"] is False
    assert retrieval["summary_retrieval"]["solved"] is False


def test_leakage_ablation_replay_and_mutation_reports_pass_without_scope_leak(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    leakage = _read_json(tmp_path / "leakage_report.json")
    ablation = _read_json(tmp_path / "ablation_report.json")
    replay = _read_json(tmp_path / "replay_integrity_report.json")
    mutation = _read_json(tmp_path / "mutation_check_report.json")
    ablations = {row["ablation_name"]: row for row in ablation["ablations"]}

    assert leakage["leakage_gate_passed"] is True
    assert leakage["partner_labels_leaked"] is False
    assert leakage["fixture_name_leakage_detected"] is False
    assert leakage["future_partner_response_leakage_detected"] is False
    assert leakage["oracle_control_used_only_as_upper_bound"] is True
    assert set(ablations) == REQUIRED_ABLATIONS
    assert ablation["ablation_gate_passed"] is True
    assert all(row["sensitive"] for row in ablations.values())
    assert replay["replay_integrity_passed"] is True
    assert replay["trace_only_replay_hygiene_only"] is True
    assert replay["trace_only_replay_used_as_positive_evidence"] is False
    assert mutation["mutation_check_passed"] is True
    assert mutation["scope_leak_detected"] is False
    assert mutation["modified_paths_outside_allowed_scope"] == []


def test_result_preserves_claim_ceiling_and_anti_hardcoding_audit(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    result = _read_json(tmp_path / "result.json")
    audit = result["anti_sycophancy_audit"]
    ledger = _read_jsonl(tmp_path / "run_ledger.jsonl")

    assert result["verdict"] == VERDICT
    assert result["bounded_pass"] is True
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["stop_conditions_triggered"] == []
    assert result["failure_reasons"] == []
    assert result["forbidden_claims_absent"] is True
    assert audit["strongest_baseline_explanation"]
    assert audit["strongest_reason_task_may_be_invalid"]
    assert audit["result_that_would_falsify_current_framing"]
    assert audit["evidence_that_would_still_be_insufficient"]
    assert audit["tests_mechanism_or_behavioral_resemblance"] == (
        "tests a bounded social representational-gap substrate, not Gate4 "
        "mechanism execution or behavioral resemblance"
    )
    assert {row["event"] for row in ledger} >= {
        "stage0_freeze_manifest_written",
        "remote_anchor_verification_completed",
        "candidate_and_challengers_evaluated",
        "mutation_check_after_evaluation",
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
