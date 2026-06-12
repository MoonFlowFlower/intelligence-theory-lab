import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B"
VERDICT = "ego_mainline_admission_executable_001b_bounded_contract_gate_pass"
CLAIM_CEILING = (
    "bounded EGO-mainline admission executable gate evidence under synthetic / "
    "controlled conditions only"
)
ARTIFACT_DIR = ROOT / "artifacts" / "ego_mainline_admission_executable_001b"
TASK_CARD = ROOT / "docs" / "codex" / "tasks" / "EGO-MAINLINE-ADMISSION-EXECUTABLE-001B.md"
PARENT_CONTRACT = ROOT / "docs" / "codex" / "tasks" / "EGO-MAINLINE-ADMISSION-TASK-CARD-001A.md"
COMPUTED_CONTRACT = ROOT / "docs" / "codex" / "contracts" / "COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md"


REQUIRED_ARTIFACTS = {
    "result.json",
    "parent_anchor_verification.json",
    "contract_requirement_evaluation.json",
    "evidence_dependency_matrix.json",
    "negative_evidence_preservation_report.json",
    "current_evidence_status_report.json",
    "stage0_freeze_manifest.json",
    "execution_manifest.json",
    "execution_manifest.sha256",
    "protected_artifact_inventory_before.json",
    "protected_artifact_hashes_before.json",
    "protected_artifact_hashes_after.json",
    "tracked_old_artifact_mutation_report.json",
    "mutation_check_report.json",
    "source_code_path_hashes.json",
    "controlled_evidence_pack_manifest.json",
    "candidate_trace.json",
    "candidate_output_rows.json",
    "baseline_report.json",
    "baseline_invocation_report.json",
    "ablation_report.json",
    "ablation_invocation_report.json",
    "leakage_surface_inventory.json",
    "leakage_scan_report.json",
    "leakage_positive_control_report.json",
    "manual_leakage_injection_report.json",
    "metadata_whitelist_surface_scope_report.json",
    "behavior_causal_replay_report.json",
    "hash_integrity_replay_report.json",
    "frozen_input_consumption_report.json",
    "metric_provenance.json",
    "failure_path_test_report.json",
    "claim_ceiling.txt",
}

REQUIRED_BASELINES = {
    "random_policy",
    "majority_or_no_action",
    "observation_only",
    "fresh_agent_no_carryover",
    "snapshot_reload",
    "stitched_output",
    "state_table_lookup",
    "identity_token_lookup",
    "memory_key_lookup",
    "summary_retrieval",
    "transcript_retrieval",
    "nearest_neighbor_lookup",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "bounded_order_window_model_order_1",
    "bounded_order_window_model_order_2",
    "shuffled_history_same_loss_control",
    "behavior_imitation",
    "frozen_state_carryover",
    "oracle_upper_bound_leakage_diagnostic_only",
    "trace_only_replay_integrity_only",
}

REQUIRED_ABLATIONS = {
    "reset_all_memory",
    "corrupt_serialized_state",
    "replace_serialized_state",
    "remove_replay_carryover",
    "remove_self_boundary_carryover",
    "remove_viability_carryover",
    "remove_social_latent_carryover",
    "remove_identity_continuity_state",
    "remove_memory_carryover_state",
    "time_shift_state",
    "cross_agent_state_swap",
    "duplicate_identity_token_contrast",
    "freeze_post_bridge_learning",
    "remove_post_bridge_observation_update",
    "disable_action",
    "invert_bridge_mapping",
}

REQUIRED_SURFACES = {
    "candidate_inputs",
    "trace_rows",
    "observation_rows",
    "serialized_state_snapshots",
    "serialized_state_provenance_rows",
    "metric_provenance_rows",
    "artifact_path_inventory",
    "fixture_names",
    "labels",
    "verifier_only_fields",
    "future_observations",
    "future_partner_responses",
    "later_action_labels",
    "post_hoc_metrics",
    "test_only_schema_paths",
    "renderer_visible_behavior_where_applicable",
}

REQUIRED_METRIC_FIELDS = {
    "metric_id",
    "metric_name",
    "producer_function",
    "producer_module",
    "code_path_hash",
    "run_id",
    "episode_ids",
    "seed_ids",
    "train_context_ids_consumed",
    "heldout_context_ids_consumed",
    "counterfactual_pair_ids_consumed",
    "input_artifact_paths",
    "input_artifact_hashes",
    "input_row_count",
    "output_artifact_path",
    "output_row_ids",
    "aggregation_rule",
    "threshold_used",
    "threshold_frozen_before_run",
    "computed_not_literal",
    "failure_path_available",
}

EXPECTED_FAILURE_PATHS = {
    "literal_metric_detected": "ego_mainline_admission_executable_001b_block_literal_metric_detected",
    "static_baseline_dictionary_detected": "ego_mainline_admission_executable_001b_block_baseline_invocation_missing",
    "ablation_not_rerun": "ego_mainline_admission_executable_001b_block_ablation_not_rerun",
    "ablation_output_copied": "ego_mainline_admission_executable_001b_block_ablation_not_rerun",
    "scanner_not_fail_able": "ego_mainline_admission_executable_001b_block_scanner_not_fail_able",
    "manual_injection_test_missing": "ego_mainline_admission_executable_001b_block_scanner_not_fail_able",
    "metadata_whitelist_not_surface_scoped": "ego_mainline_admission_executable_001b_block_metadata_whitelist_not_surface_scoped",
    "hash_only_replay_for_behavior_claim": "ego_mainline_admission_executable_001b_block_replay_not_behavior_causal",
    "unused_frozen_input": "ego_mainline_admission_executable_001b_block_unused_frozen_input",
    "001b_positive_evidence_leak": "ego_mainline_admission_executable_001b_block_001b_positive_evidence_leak",
    "001c_positive_evidence_leak": "ego_mainline_admission_executable_001b_block_001c_positive_evidence_leak",
    "001d_caveat_missing": "ego_mainline_admission_executable_001b_block_001d_caveat_missing",
    "scope_leak": "ego_mainline_admission_executable_001b_block_scope_leak",
    "claim_inflation": "ego_mainline_admission_executable_001b_block_claim_inflation",
}


def _modules():
    core = importlib.import_module("ego_mainline_admission_executable_001b.core")
    runner = importlib.import_module("ego_mainline_admission_executable_001b.runner")
    return core, runner


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def run_001b(tmp_path_factory):
    core, runner = _modules()
    out = tmp_path_factory.mktemp("ego_mainline_admission_001b")
    result = runner.run_admission_001b(
        repo_root=ROOT,
        output_dir=out,
        enforce_clean_worktree=False,
        verify_remote=False,
    )
    return core, out, result


def test_run_emits_required_artifacts_and_task_card(run_001b):
    core, out, result = run_001b

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == VERDICT
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["artifact_dir"] == "artifacts/ego_mainline_admission_executable_001b"
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in out.iterdir()})
    assert not (out / "blocker_report.json").exists()
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING
    assert TASK_CARD.exists()
    assert TASK_ID in TASK_CARD.read_text(encoding="utf-8")
    assert core.CONTRACT_PATH == "docs/codex/contracts/COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md"


def test_parent_anchors_contract_and_negative_evidence_are_preserved(run_001b):
    _core, out, result = run_001b
    parents = _read_json(out / "parent_anchor_verification.json")
    requirements = _read_json(out / "contract_requirement_evaluation.json")
    dependencies = _read_json(out / "evidence_dependency_matrix.json")
    negative = _read_json(out / "negative_evidence_preservation_report.json")
    current = _read_json(out / "current_evidence_status_report.json")

    assert parents["target_commit"] == "cda09dce5d8412beea88e9b2108ea41c1ce260bd"
    assert parents["anchors"]["remote-anchor-001p-cda09dc"]["local_verified"] is True
    assert parents["anchors"]["remote-anchor-001o-f648dac"]["local_verified"] is True
    assert requirements["computed_evidence_contract_loaded"] is True
    assert requirements["contract_path"] == str(COMPUTED_CONTRACT.relative_to(ROOT)).replace("\\", "/")
    assert requirements["task_card_path"] == str(PARENT_CONTRACT.relative_to(ROOT)).replace("\\", "/")
    assert requirements["001d_caveat_preserved"] is True
    assert dependencies["post_bridge_admission_executable_001b"]["used_as_positive_evidence"] is False
    assert dependencies["post_bridge_admission_executable_001c"]["used_as_positive_evidence"] is False
    assert negative["001b_invalidation_preserved"] is True
    assert negative["001c_suspension_preserved"] is True
    assert current["post_bridge_admission_executable_001d"]["status"] == "current bounded post-bridge positive candidate with caveats"
    assert result["authorization_flags"]["ego_mainline_runtime_authorized"] is False


def test_candidate_behavior_replay_and_metric_provenance_are_computed(run_001b):
    _core, out, result = run_001b
    candidate_rows = _read_json(out / "candidate_output_rows.json")
    replay = _read_json(out / "behavior_causal_replay_report.json")
    metrics = _read_json(out / "metric_provenance.json")
    candidate_metric = next(row for row in metrics["metrics"] if row["metric_id"] == "candidate_score")

    assert candidate_rows
    assert all(row["computed_from_serialized_state_and_observation"] for row in candidate_rows)
    assert replay["behavior_causal_replay_passed"] is True
    assert replay["hash_only_replay"] is False
    assert replay["recomputed_from_serialized_state_and_observation"] is True
    assert candidate_metric["producer_function"].endswith("behavior_causal_replay")
    assert candidate_metric["computed_not_literal"] is True
    assert candidate_metric["failure_path_available"] is True
    assert REQUIRED_METRIC_FIELDS.issubset(candidate_metric)
    assert all(REQUIRED_METRIC_FIELDS.issubset(row) for row in metrics["metrics"])
    assert result["acceptance_gates"]["all_verdict_metrics_have_provenance"] is True
    assert result["acceptance_gates"]["no_literal_metrics"] is True


def test_all_required_baselines_are_callable_invoked_and_aggregated_from_outputs(run_001b):
    _core, out, result = run_001b
    baseline = _read_json(out / "baseline_report.json")
    invocations = _read_json(out / "baseline_invocation_report.json")

    assert baseline["baseline_gate_passed"] is True
    assert {row["baseline_id"] for row in baseline["baselines"]} == REQUIRED_BASELINES
    assert {row["baseline_id"] for row in invocations["invocations"]} == REQUIRED_BASELINES
    assert all(row["callable_invoked"] for row in invocations["invocations"])
    assert all(row["output_rows_exist_before_aggregation"] for row in invocations["invocations"])
    assert all(row["static_dictionary_used"] is False for row in invocations["invocations"])
    assert all(row["score"] < baseline["candidate_score"] for row in baseline["baselines"] if row["counts_as_fair_baseline"])
    assert result["acceptance_gates"]["all_required_baselines_invoked"] is True
    assert result["acceptance_gates"]["baseline_outputs_exist_before_aggregation"] is True


def test_all_required_ablations_rerun_candidate_behavior_and_are_not_copied(run_001b):
    _core, out, result = run_001b
    ablation = _read_json(out / "ablation_report.json")
    invocations = _read_json(out / "ablation_invocation_report.json")

    assert ablation["ablation_gate_passed"] is True
    assert {row["ablation_id"] for row in ablation["ablations"]} == REQUIRED_ABLATIONS
    assert {row["ablation_id"] for row in invocations["invocations"]} == REQUIRED_ABLATIONS
    assert all(row["reran_candidate_behavior"] for row in invocations["invocations"])
    assert all(row["copied_from_candidate_outputs"] is False for row in invocations["invocations"])
    assert all(row["sensitive"] for row in ablation["ablations"])
    assert result["acceptance_gates"]["all_required_ablations_rerun"] is True
    assert result["acceptance_gates"]["ablation_outputs_recomputed"] is True


def test_leakage_controls_manual_injection_and_surface_scoped_metadata(run_001b):
    _core, out, result = run_001b
    inventory = _read_json(out / "leakage_surface_inventory.json")
    leakage = _read_json(out / "leakage_scan_report.json")
    positives = _read_json(out / "leakage_positive_control_report.json")
    manual = _read_json(out / "manual_leakage_injection_report.json")
    whitelist = _read_json(out / "metadata_whitelist_surface_scope_report.json")

    assert {row["surface_name"] for row in inventory["surfaces"]} == REQUIRED_SURFACES
    assert leakage["leakage_gate_passed"] is True
    assert leakage["leakage_detected"] is False
    assert leakage["scanner_not_fail_able"] is False
    assert {row["surface_name"] for row in leakage["surface_results"]} == REQUIRED_SURFACES
    assert all(row["real_scan_detected"] is False for row in leakage["surface_results"])
    assert all(row["positive_control_detected"] is True for row in leakage["surface_results"])
    assert all(row["clean_control_detected"] is False for row in leakage["surface_results"])
    assert positives["same_surface_positive_controls_detected"] is True
    assert manual["independent_manual_leakage_injection_tests_passed"] is True
    assert manual["production_injector_only"] is False
    assert whitelist["metadata_whitelist_surface_scoped"] is True
    assert whitelist["global_reserved_metadata_key_privilege"] is False
    assert whitelist["reserved_key_value_scanned_on_unprivileged_surface"] is True
    assert result["acceptance_gates"]["same_surface_positive_controls_detected"] is True
    assert result["acceptance_gates"]["independent_manual_leakage_injection_tests_passed"] is True
    assert result["acceptance_gates"]["metadata_whitelist_surface_scoped"] is True


def test_frozen_inputs_are_all_consumed_by_callable_paths(run_001b):
    _core, out, result = run_001b
    frozen = _read_json(out / "frozen_input_consumption_report.json")

    assert frozen["all_frozen_inputs_consumed"] is True
    assert frozen["unused_frozen_inputs"] == []
    for family in [
        "seed_ids",
        "train_context_ids",
        "heldout_context_ids",
        "counterfactual_pair_ids",
        "cross_agent_swap_pair_ids",
        "duplicate_identity_token_contrast_ids",
        "ablation_definition_ids",
    ]:
        assert frozen["families"][family]["declared"]
        assert set(frozen["families"][family]["declared"]) <= set(frozen["families"][family]["consumed"])
    assert result["acceptance_gates"]["all_frozen_inputs_consumed"] is True


def test_source_artifact_integrity_and_old_artifact_mutation_checks_pass(run_001b):
    _core, out, result = run_001b
    source_hashes = _read_json(out / "source_code_path_hashes.json")
    mutation = _read_json(out / "mutation_check_report.json")
    old = _read_json(out / "tracked_old_artifact_mutation_report.json")
    protected_before = _read_json(out / "protected_artifact_hashes_before.json")
    protected_after = _read_json(out / "protected_artifact_hashes_after.json")
    manifest_hash = (out / "execution_manifest.sha256").read_text(encoding="utf-8").strip()

    assert source_hashes["source_hashes"]
    assert mutation["source_artifact_integrity_passed"] is True
    assert old["old_artifacts_not_mutated"] is True
    assert protected_before["hashes"] == protected_after["hashes"]
    assert _sha(out / "execution_manifest.json") == manifest_hash
    assert result["acceptance_gates"]["source_artifact_integrity_passed"] is True
    assert result["acceptance_gates"]["old_artifacts_not_mutated"] is True


def test_failure_path_report_proves_gate_can_fail_for_required_controls(run_001b):
    _core, out, result = run_001b
    report = _read_json(out / "failure_path_test_report.json")

    observed = {row["failure_id"]: row for row in report["failure_paths"]}
    assert set(observed) == set(EXPECTED_FAILURE_PATHS)
    for failure_id, expected_verdict in EXPECTED_FAILURE_PATHS.items():
        row = observed[failure_id]
        assert row["observed_verdict"] == expected_verdict
        assert row["expected_verdict"] == expected_verdict
        assert row["passed"] is True
    assert report["failure_path_tests_passed"] is True
    assert result["acceptance_gates"]["failure_path_tests_passed"] is True


def test_hash_only_replay_and_leakage_failure_modes_are_distinguished(run_001b):
    core, out, _result = run_001b
    failure_report = _read_json(out / "failure_path_test_report.json")
    by_id = {row["failure_id"]: row for row in failure_report["failure_paths"]}

    leakage = core.evaluate_stop_conditions({"leakage_detected": True})
    scanner = core.evaluate_stop_conditions({"scanner_not_fail_able": True})
    replay = core.evaluate_stop_conditions({"hash_only_replay_for_behavior_claim": True})

    assert leakage["verdict"] == "ego_mainline_admission_executable_001b_block_leakage_detected"
    assert scanner["verdict"] == "ego_mainline_admission_executable_001b_block_scanner_not_fail_able"
    assert replay["verdict"] == "ego_mainline_admission_executable_001b_block_replay_not_behavior_causal"
    assert by_id["hash_only_replay_for_behavior_claim"]["observed_verdict"] == replay["verdict"]


def test_scope_flags_block_runtime_product_and_ego_repo_work(run_001b):
    core, _out, result = run_001b

    assert result["authorization_flags"]["ego_repository_modification_authorized"] is False
    assert result["authorization_flags"]["ego_mainline_runtime_authorized"] is False
    assert result["authorization_flags"]["bridge_runtime_authorized"] is False
    assert result["authorization_flags"]["llm_rag_authorized"] is False
    assert result["authorization_flags"]["user_memory_authorized"] is False
    assert result["acceptance_gates"]["no_Ego_repo_modification"] is True
    assert result["acceptance_gates"]["no_runtime_or_product_work"] is True

    scope = core.evaluate_stop_conditions({"ego_repository_modification": True})
    claim = core.evaluate_stop_conditions({"claim_inflation": True})
    assert scope["verdict"] == "ego_mainline_admission_executable_001b_block_scope_leak"
    assert claim["verdict"] == "ego_mainline_admission_executable_001b_block_claim_inflation"
