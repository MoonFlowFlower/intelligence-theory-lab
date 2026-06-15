import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "ACP-BV-EXECUTABLE-HARNESS-001A"
ARTIFACT_NAMES = {
    "result.json",
    "source_pins.json",
    "boundary_report.json",
    "boundary_negative_controls.json",
    "leakage_report.json",
    "baseline_matrix.json",
    "ablation_report.json",
    "replay_report.json",
    "counterfactual_controls.json",
    "clean_dirty_lookup_controls.json",
    "run_manifest.json",
    "readback.json",
    "claim_ceiling.txt",
}
BASELINES = {
    "graph_cache_transition_table",
    "graph_cache_successor_map",
    "graph_cache_count_table",
    "episodic_traversal_baseline",
    "fsm_planner_baseline",
    "graph_lookup_baseline",
    "observation_only_baseline",
    "action_independent_baseline",
    "static_action_baseline",
    "replay_hash_only_baseline",
    "candidate_self_consistency_baseline",
    "lookup_table_memorization_blocker",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_callable(path: Path, function_name: str):
    spec = importlib.util.spec_from_file_location(f"candidate_control_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return getattr(module, function_name)


def _runner():
    from acp_bv_harness_001a import runner

    return runner


def _run(tmp_path: Path) -> tuple[dict, Path]:
    out = tmp_path / "acp_bv_executable_harness_001a"
    result = _runner().run_harness(repo_root=ROOT, output_dir=out, run_id="pytest-acp-bv-001a")
    return result, out


def test_source_boundary_verifier_derives_ownership_and_source_pin_blocks_tamper(tmp_path):
    from acp_bv_harness_001a import boundary, environment, source_pins

    manifest_path = tmp_path / "source_pins.json"
    manifest = source_pins.create_source_pin_manifest(
        repo_root=ROOT,
        run_id="pytest-source-pin",
        output_path=manifest_path,
    )

    clean = boundary.verify_callable_source_boundary(
        environment.generate_episodes,
        repo_root=ROOT,
        candidate_writable_roots=[tmp_path / "candidate"],
        candidate_artifact_roots=[tmp_path / "candidate_artifacts"],
    )
    assert clean["boundary_verdict"] == "source_boundary_pass"
    assert clean["repo_source_owned_derived"] is True
    assert clean["candidate_inaccessible_derived"] is True
    assert clean["repo_source_root_match"] is True
    assert clean["candidate_writable_root_match"] is False

    candidate_dir = tmp_path / "candidate_artifacts"
    candidate_dir.mkdir()
    candidate_file = candidate_dir / "candidate_truth.py"
    candidate_file.write_text(
        "def forged_truth(*args, **kwargs):\n"
        "    return {'boundary': 'candidate-authored', 'viability': 1.0}\n",
        encoding="utf-8",
    )
    forged_truth = _load_callable(candidate_file, "forged_truth")
    forged = boundary.verify_callable_source_boundary(
        forged_truth,
        repo_root=ROOT,
        candidate_writable_roots=[candidate_dir],
        candidate_artifact_roots=[candidate_dir],
        influence={"candidate_policy_map": {"truth_generator": "forged_truth"}},
    )

    assert forged["boundary_verdict"] == "source_boundary_blocked"
    assert forged["repo_source_owned_derived"] is False
    assert forged["candidate_inaccessible_derived"] is False
    assert forged["candidate_artifact_root_match"] is True
    assert forged["candidate_policy_map_influence_detected"] is True
    assert "candidate_policy_map_influence" in forged["block_reasons"]

    assert source_pins.verify_source_pin_manifest(manifest, repo_root=ROOT)["passed"] is True
    tampered = dict(manifest)
    tampered["verifier_source_hash"] = "0" * 64
    tampered_check = source_pins.verify_source_pin_manifest(tampered, repo_root=ROOT)
    assert tampered_check["passed"] is False
    assert tampered_check["block_reason"] == "blocked_by_unpinned_boundary_verifier"


def test_runner_writes_required_artifacts_and_control_reports_are_fail_able(tmp_path):
    result, out = _run(tmp_path)

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == "acp_bv_executable_harness_001a_implemented_with_fail_able_controls"
    assert result["current_layer"] == (
        "engineering implementation / bounded offline ACP-BV harness implementation and control evidence only"
    )
    assert result["mainline_integration_status"] == "none"
    assert result["enabled_status"] == "local offline CLI/test runner only"
    assert result["real_gate_target_applied"] is False
    assert result["claim_ceiling"] == (
        "offline_harness_implemented_with_fail_able_controls_under_this_task_distribution"
    )
    assert ARTIFACT_NAMES == {path.name for path in out.iterdir() if path.is_file()}

    for artifact in ARTIFACT_NAMES - {"claim_ceiling.txt"}:
        _load_json(out / artifact)
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == result["claim_ceiling"]

    boundary_controls = _load_json(out / "boundary_negative_controls.json")
    assert boundary_controls["all_required_controls_passed"] is True
    assert {
        control["control_id"] for control in boundary_controls["controls"]
    } >= {
        "candidate_accessible_truth_generator_rejected",
        "policy_map_influenced_generator_rejected",
        "valid_hash_wrong_owner_rejected",
        "path_escape_or_generated_code_rejected",
        "same_process_monkeypatch_rejected_or_ineffective",
    }
    assert all(control["actual_verdict"] == "blocked" for control in boundary_controls["controls"])

    clean_dirty_lookup = _load_json(out / "clean_dirty_lookup_controls.json")
    assert clean_dirty_lookup["clean_control"]["verdict"] == "clean_control_passed"
    assert clean_dirty_lookup["dirty_control"]["verdict"] == "dirty_control_blocked"
    assert clean_dirty_lookup["lookup_memorization_control"]["verdict"] in {
        "lookup_memorization_blocked",
        "lookup_memorization_classified",
    }
    assert clean_dirty_lookup["self_reported_boolean_load_bearing"] is False

    leakage = _load_json(out / "leakage_report.json")
    assert leakage["clean_case"]["verdict"] == "clean"
    assert leakage["dirty_case"]["verdict"] == "blocked"
    assert leakage["randomized_dirty_cases_detected"] >= 3
    assert leakage["fixed_field_name_only_scanner"] is False

    counterfactual = _load_json(out / "counterfactual_controls.json")
    assert counterfactual["harness_selected_counterfactual_action_queries"] is True
    assert counterfactual["fixed_action_set_alone"] is False
    assert counterfactual["easy_action_payload_classification"] == "blocked_by_action_difficulty"


def test_baselines_ablations_replay_and_provenance_are_callable_computed(tmp_path):
    result, out = _run(tmp_path)

    baseline_matrix = _load_json(out / "baseline_matrix.json")
    assert {row["baseline_id"] for row in baseline_matrix["baselines"]} == BASELINES
    assert baseline_matrix["strongest_baseline"]["baseline_id"] in BASELINES
    assert baseline_matrix["strongest_baseline_comparison"]["delta"] >= 0.05
    assert (
        baseline_matrix["strongest_baseline_comparison"]["classification"]
        == "mechanism_relevant_effect_candidate"
    )
    assert baseline_matrix["baseline_equivalent_is_pass"] is False
    assert baseline_matrix["thresholds"] == {
        "equivalence_lt": 0.02,
        "inconclusive_gte": 0.02,
        "inconclusive_lt": 0.05,
        "mechanism_relevant_effect_gte": 0.05,
    }
    assert all(row["provenance"]["producer_function"] for row in baseline_matrix["baselines"])
    assert all(row["provenance"]["source_hash"] for row in baseline_matrix["baselines"])
    assert all(row["provenance"]["run_id"] for row in baseline_matrix["baselines"])

    replay = _load_json(out / "replay_report.json")
    assert replay["verdict"] == "replay_recomputed"
    assert replay["behavior_recomputed"] is True
    assert replay["used_serialized_state"] is True
    assert replay["used_observation"] is True
    assert replay["repo_owned_truth_source_used"] is True
    assert replay["hash_only_positive_control"]["verdict"] == "blocked_by_replay_hash_only"
    assert replay["provenance"]["producer_function"] == "recompute_replay_from_state_observation"

    ablation = _load_json(out / "ablation_report.json")
    assert len(ablation["ablations"]) >= 4
    assert ablation["report_field_editing_used"] is False
    assert all(row["episodes_rerun"] is True for row in ablation["ablations"])
    assert all(row["regenerated_trace_path"] for row in ablation["ablations"])
    assert all(row["effect_size"] >= 0 for row in ablation["ablations"])
    assert all(row["provenance"]["producer_function"] for row in ablation["ablations"])

    source_pins = _load_json(out / "source_pins.json")
    required_roles = {
        "scorer",
        "environment_generator",
        "held_out_truth_generator",
        "counterfactual_truth_generator",
        "leakage_scanner",
        "graph_cache_challengers",
        "replay_recomputation",
        "ablation_runner",
        "baseline_runner",
        "metric_aggregator",
        "difficulty_source",
        "difficulty_normalizer",
        "boundary_verifier",
    }
    assert required_roles.issubset(set(source_pins["load_bearing_callables"]))
    assert source_pins["manifest_verification_at_scoring"]["passed"] is True

    assert result["baseline_result"]["classification"] == "mechanism_relevant_effect_candidate"
    assert result["ablation_result"]["all_rerun"] is True
    assert result["replay_result"]["hash_only_rejected"] is True


def test_runtime_mutation_control_rejects_same_process_truth_substitution(tmp_path):
    from acp_bv_harness_001a import controls, source_pins

    manifest_path = tmp_path / "source_pins.json"
    manifest = source_pins.create_source_pin_manifest(
        repo_root=ROOT,
        run_id="pytest-runtime-mutation",
        output_path=manifest_path,
    )

    report = controls.run_runtime_mutation_control(
        repo_root=ROOT,
        output_dir=tmp_path,
        source_pin_manifest=manifest,
        run_id="pytest-runtime-mutation",
    )

    assert report["control_id"] == "same_process_monkeypatch_rejected_or_ineffective"
    assert report["actual_verdict"] == "blocked"
    assert report["candidate_side_same_process_substitution_attempted"] is True
    assert report["scoring_allowed_after_mutation"] is False
    assert report["block_reason"] == "blocked_by_runtime_mutation_or_temporal_boundary_gap"


def test_readback_records_no_mainline_effect_and_forbidden_claim_scan(tmp_path):
    _, out = _run(tmp_path)

    readback = _load_json(out / "readback.json")
    result = _load_json(out / "result.json")
    manifest = _load_json(out / "run_manifest.json")

    assert readback["mainline_integration_status"] == "none"
    assert readback["enabled_status"] == "local offline CLI/test runner only"
    assert readback["real_trigger_evidence"]["start_commit"] == (
        "a699449bd42f0f67fc8cb2b5484e507a800e659c"
    )
    assert readback["real_trigger_evidence"]["claude_targeted_reaudit_verdict"] == (
        "accept_for_harness_implementation_task_with_required_bindings"
    )
    assert readback["what_this_does_not_prove"]
    assert result["claim_scan"]["claim_ceiling_passed"] is True
    assert result["claim_scan"]["forbidden_claim_scan_passed"] is True
    assert result["safe_to_apply_to_real_gate_target"] is False
    assert result["safe_to_wire_mainline"] is False
    assert manifest["auto_remote_anchor"]["decision"] == "conditional"
    assert manifest["auto_remote_anchor"]["performed_by_runner"] is False
