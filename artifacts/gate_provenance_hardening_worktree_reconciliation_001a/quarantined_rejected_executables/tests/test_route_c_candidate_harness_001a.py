import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "ROUTE-C-CANDIDATE-HARNESS-IMPLEMENTATION-ACTIVATION-001A"
CLAIM_CEILING = "bounded local candidate harness implementation and computed-evidence generation only"

REQUIRED_ARTIFACTS = {
    "access_parity_report.json",
    "truth_seed_disjointness_report.json",
    "margin_failing_negative_control.json",
    "saturation_failing_negative_control.json",
    "co_forged_anchor_positive_control.json",
    "clean_anchor_control.json",
    "leakage_positive_controls.json",
    "replay_recomputation_report.json",
    "ablation_rerun_report.json",
    "source_pin_readback_report.json",
    "source_pin_truncation_positive_control.json",
    "provenance_rows.jsonl",
    "final_report.md",
    "result.json",
    "claim_ceiling.txt",
    "baseline_comparison.json",
    "trace.jsonl",
    "failure_manifest.json",
}

PASSIVE_BASELINES = {
    "positional_first_k",
    "mean",
    "variance",
    "correlation",
    "pca_subspace",
    "cross_episode",
    "supervised",
    "legal_field_membership",
}

FAIR_INTERVENTIONAL_BASELINES = {
    "random",
    "greedy_info_gain",
    "exhaustive_legal_query",
    "bayesian_likelihood",
    "lookup_imitation",
    "direct_objective_optimizer",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
}

GRAPH_CACHE_CHALLENGERS = {
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
}

ABLATIONS = {
    "remove_mechanism_specific_state",
    "remove_interventional_access",
    "remove_update_path",
    "remove_replay_state",
    "remove_candidate_memory_cache",
    "remove_self_boundary_specific_feature",
    "shuffle_target_labels",
    "swap_twin_pairs_passive_distribution_constant",
    "remove_candidate_only_fields",
    "replace_candidate_policy_with_strongest_fair_baseline_policy",
}

LEAKAGE_CONTROLS = {
    "passive_value_level_leakage",
    "schema_name_key_leakage",
    "order_leakage",
    "action_api_leakage",
    "serialized_state_leakage",
    "result_json_leakage",
    "candidate_only_field_leakage",
    "train_heldout_contamination",
    "truth_seed_contamination",
    "unused_frozen_seed",
    "source_pin_aliasing_or_forged_anchor_leakage",
}

PROVENANCE_FIELDS = {
    "producer_function",
    "inputs",
    "run_id",
    "seed",
    "context_id",
    "episode_id",
    "aggregation",
    "code_path_hash",
    "recompute_command",
    "output_artifact",
    "role",
    "source_path",
    "source_pinned_input_artifact_hash",
}


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _run(tmp_path: Path):
    from route_c_candidate_harness_001a import runner

    out = tmp_path / "route_c_candidate_harness_001a"
    result = runner.run_harness(repo_root=ROOT, output_dir=out, run_id="pytest-route-c-001a")
    return result, out


def test_runner_writes_required_artifacts_and_preserves_claim_ceiling(tmp_path):
    result, out = _run(tmp_path)

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == "close_or_downgrade"
    assert result["terminal_reason"] == "strongest_fair_baseline_saturated_candidate"
    assert result["current_layer"] == "engineering implementation / bounded local Route C candidate harness"
    assert result["mainline_integration_status"] == "none"
    assert result["enabled_status"] == "local CLI/test harness only"
    assert result["real_trigger_evidence"]["local_cli_entrypoint"] == "python -m route_c_candidate_harness_001a"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["harness_success_claimed"] is False
    assert result["safe_to_wire_mainline"] is False
    assert result["safe_to_claim_mechanism_validity"] is False
    assert result["auto_remote_anchor"] == "forbidden"

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in out.iterdir() if path.is_file()})
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING
    assert "No Route C mechanism validity claim" in (out / "final_report.md").read_text(encoding="utf-8")

    failure_manifest = _load_json(out / "failure_manifest.json")
    assert failure_manifest["verdict"] == "close_or_downgrade"
    assert failure_manifest["derived_from_result"] is True
    assert result["verdict_consistency_check"]["matches_recomputed_verdict"] is True
    assert "strongest_fair_baseline_saturated_candidate" in failure_manifest["stop_conditions_triggered"]


def test_baselines_access_parity_margin_and_saturation_controls_are_callable(tmp_path):
    result, out = _run(tmp_path)

    baseline = _load_json(out / "baseline_comparison.json")
    assert {row["baseline_id"] for row in baseline["passive_baselines"]} == PASSIVE_BASELINES
    assert {row["baseline_id"] for row in baseline["fair_interventional_baselines"]} == FAIR_INTERVENTIONAL_BASELINES
    assert GRAPH_CACHE_CHALLENGERS.issubset(
        {row["baseline_id"] for row in baseline["fair_interventional_baselines"] if row["family"] == "graph_cache"}
    )
    assert all(row["callable_invoked"] is True for row in baseline["passive_baselines"])
    assert all(row["callable_invoked"] is True for row in baseline["fair_interventional_baselines"])
    assert baseline["obs_only_family_max"]["score"] == max(row["score"] for row in baseline["passive_baselines"])
    assert baseline["fair_interventional_family_max"]["score"] == max(
        row["score"] for row in baseline["fair_interventional_baselines"]
    )
    assert result["candidate_score"] == baseline["candidate_score"]
    assert baseline["fair_interventional_family_max"]["score"] == result["candidate_score"]
    assert baseline["saturation_decision"]["verdict"] == "close_or_downgrade"
    assert baseline["predeclaration"]["predeclaration_hash"]
    assert baseline["predeclaration"]["minimum_seed_count"] >= 5
    assert baseline["candidate_advantage"]["mean_delta_vs_strongest_fair"] == 0.0
    assert baseline["candidate_advantage"]["clears_frozen_margin_and_noise_floor"] is False

    access = _load_json(out / "access_parity_report.json")
    assert access["verdict"] == "access_parity_passed"
    assert access["strongest_fair_baseline"] == baseline["fair_interventional_family_max"]["baseline_id"]
    assert access["strongest_fair_baseline"] == "exhaustive_legal_query"
    assert access["saturation_judgment_consumed_access_parity"] is True
    assert access["computed_from_access_traces"] is True
    assert access["candidate_access_trace"]["query_count"] == access["strongest_fair_access_trace"]["query_count"]
    assert access["negative_control"]["verdict"] == "access_parity_failed"
    assert all(item["parity"] is True for item in access["dimensions"])
    assert access["feature_impoverishment_used_as_parity"] is False

    margin_control = _load_json(out / "margin_failing_negative_control.json")
    assert margin_control["same_callable_margin_gate_used"] is True
    assert margin_control["verdict"] == "close_or_downgrade"

    saturation_control = _load_json(out / "saturation_failing_negative_control.json")
    assert saturation_control["same_callable_saturation_gate_used"] is True
    assert saturation_control["verdict"] == "close_or_downgrade"
    assert saturation_control["saturated_case"]["verdict"] == "close_or_downgrade"
    assert saturation_control["not_saturated_case"]["verdict"] == "not_saturated"
    assert saturation_control["not_saturated_case"]["margin_verdict"] == "candidate_margin_cleared"
    assert saturation_control["access_parity_report_sha256"] == access["report_sha256"]
    assert set(saturation_control["graph_cache_challengers_included"]) == GRAPH_CACHE_CHALLENGERS
    assert saturation_control["access_parity_report_consumed"] is True


def test_replay_ablation_leakage_seed_source_pin_and_provenance_controls(tmp_path):
    from route_c_candidate_harness_001a import runner

    _, out = _run(tmp_path)

    truth_seed = _load_json(out / "truth_seed_disjointness_report.json")
    assert truth_seed["verdict"] == "truth_seed_disjointness_passed"
    assert truth_seed["sets_are_pairwise_disjoint"] is True
    assert truth_seed["candidate_visible_truth_seed"] is False

    replay = _load_json(out / "replay_recomputation_report.json")
    assert replay["verdict"] == "replay_recomputed"
    assert replay["behavior_recomputed_from_serialized_state_and_legal_history"] is True
    assert replay["stored_hash_only_used"] is False
    assert replay["controls"]["corrupted_state"]["verdict"] == "fail_closed"
    assert replay["controls"]["missing_observation"]["verdict"] == "fail_closed"
    assert replay["controls"]["forbidden_truth_field_read"]["verdict"] == "fail_closed"

    ablation = _load_json(out / "ablation_rerun_report.json")
    assert {row["ablation_id"] for row in ablation["ablations"]} == ABLATIONS
    assert all(row["real_episode_rerun"] is True for row in ablation["ablations"])
    assert all(row["report_editing_used"] is False for row in ablation["ablations"])

    leakage = _load_json(out / "leakage_positive_controls.json")
    assert {row["control_id"] for row in leakage["positive_controls"]} == LEAKAGE_CONTROLS
    assert all(row["detected"] is True for row in leakage["positive_controls"])
    assert leakage["real_artifact_scan"]["detected"] is False
    assert leakage["clean_negative_control"]["detected"] is False
    assert leakage["verdict"] == "leakage_positive_controls_detected"

    co_forged = _load_json(out / "co_forged_anchor_positive_control.json")
    assert co_forged["verdict"] == "fail_closed"
    assert set(co_forged["attacks_exercised"]) >= {
        "input",
        "value",
        "basis",
        "source_artifact_reference",
        "source_artifact_hash",
        "alias_path",
    }

    clean_anchor = _load_json(out / "clean_anchor_control.json")
    assert clean_anchor["verdict"] == "clean_anchor_admitted"
    assert clean_anchor["source_artifact_pre_run_frozen"] is True

    readback = _load_json(out / "source_pin_readback_report.json")
    assert readback["verdict"] == "source_pin_readback_completed"
    assert readback["authoritative_reader"] == "pathlib_direct_binary_read"
    assert readback["comparison_reader"]
    assert all(item["sha256"] for item in readback["critical_source_pins"])
    assert all(item["prefix_truncation_detected"] is False for item in readback["critical_source_pins"])
    assert all(item["expected_size"] == item["observed_size"] for item in readback["critical_source_pins"])
    assert all(item["conflict_status"] == "no_conflict" for item in readback["critical_source_pins"])
    assert all(item["producer_function"] == "build_source_pin_readback_report" for item in readback["critical_source_pins"])
    assert all(item["comparison_signal_available"] is True for item in readback["critical_source_pins"])
    assert all(item["comparison_read_source"] != "self_comparison" for item in readback["critical_source_pins"])
    assert all(item["comparison_sha256"] == item["sha256"] for item in readback["critical_source_pins"])
    assert all(item["recompute_command"] for item in readback["critical_source_pins"])
    clean_source_pin_gate = runner.derive_verdict_from_gates(
        baseline_comparison=_load_json(out / "baseline_comparison.json"),
        access_parity_report=_load_json(out / "access_parity_report.json"),
        source_pin_readback=readback,
    )
    assert clean_source_pin_gate["verdict"] == "close_or_downgrade"

    truncation_control = _load_json(out / "source_pin_truncation_positive_control.json")
    assert truncation_control["same_source_pin_gate_callable_used"] is True
    assert truncation_control["source_pin_gate_fail_closed"] is True
    assert truncation_control["derived_verdict"]["verdict"] == "invalid"
    assert truncation_control["derived_verdict"]["terminal_reason"] == "source_pin_readback_conflict"
    assert truncation_control["readback_report"]["verdict"] == "source_pin_readback_conflict_fail_closed"
    assert any(
        item["prefix_truncation_detected"] is True
        and item["conflict_status"] == "bounded_prefix_truncation_detected"
        for item in truncation_control["readback_report"]["critical_source_pins"]
    )

    rows = _load_jsonl(out / "provenance_rows.jsonl")
    assert rows
    assert all(PROVENANCE_FIELDS.issubset(row) for row in rows)
    assert {
        "candidate",
        "passive baseline",
        "fair interventional baseline",
        "control",
        "gate",
        "ablation",
        "replay",
        "leakage",
    }.issubset({row["role"] for row in rows})
    assert all(row["code_path_hash"] for row in rows)
    assert all(row["source_pinned_input_artifact_hash"] for row in rows)


def test_local_cli_runs_end_to_end(tmp_path):
    out = tmp_path / "cli_artifacts"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "route_c_candidate_harness_001a",
            "--output-dir",
            str(out),
            "--run-id",
            "pytest-cli-route-c-001a",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "close_or_downgrade" in completed.stdout
    assert _load_json(out / "result.json")["real_trigger_evidence"]["run_id"] == "pytest-cli-route-c-001a"


def test_result_verdict_flips_when_fair_baselines_are_below_candidate(monkeypatch, tmp_path):
    from route_c_candidate_harness_001a import runner

    def weak_fair_baseline(name, episode):
        legal_history = [
            {"action": "query_membership", "item_id": item_id, "membership": False}
            for item_id in episode["legal_action_space"]
        ]
        return set(), legal_history

    monkeypatch.setattr(runner, "fair_interventional_prediction", weak_fair_baseline)

    out = tmp_path / "route_c_candidate_harness_001a"
    result = runner.run_harness(repo_root=ROOT, output_dir=out, run_id="pytest-route-c-verdict-flip")
    baseline = _load_json(out / "baseline_comparison.json")
    failure_manifest = _load_json(out / "failure_manifest.json")

    assert baseline["margin_decision"]["verdict"] == "candidate_margin_cleared"
    assert baseline["saturation_decision"]["verdict"] == "not_saturated"
    assert failure_manifest["stop_conditions_triggered"] == []
    assert result["verdict"] == "candidate_margin_cleared"
    assert result["terminal_reason"] == "candidate_margin_cleared_and_not_saturated"
    assert result["verdict_consistency_check"]["matches_recomputed_verdict"] is True


def test_access_parity_violation_fails_closed(tmp_path):
    from route_c_candidate_harness_001a import runner

    candidate_trace = runner.access_trace_from_policy_result(
        policy_id="candidate",
        policy_result={
            "legal_history": [
                {"action": "query_membership", "item_id": 0, "membership": True},
                {"action": "query_membership", "item_id": 1, "membership": False},
            ],
            "serialized_state": {"queried_items": [0, 1], "positive_items": [0], "query_budget_used": 2},
        },
        episode={
            "observations": [{"item_id": 0}, {"item_id": 1}],
            "legal_action_space": [0, 1],
            "query_budget": 2,
        },
    )
    baseline_trace = dict(candidate_trace)
    baseline_trace["query_count"] = 1
    baseline_trace["query_budget_used"] = 1

    report = runner.compute_access_parity_report(
        candidate_trace=candidate_trace,
        strongest_fair_trace=baseline_trace,
        strongest_fair_baseline="negative_control",
        repo_root=ROOT,
        output_dir=tmp_path,
        run_id="pytest-access-negative",
        code_hash="0" * 64,
        source_hash="1" * 64,
    )

    assert report["verdict"] == "access_parity_failed"
    assert any(item["parity"] is False for item in report["dimensions"])
    assert report["negative_control"]["verdict"] == "access_parity_failed"


def test_source_pin_readback_detects_truncated_prefix(tmp_path):
    from route_c_candidate_harness_001a import runner

    source = tmp_path / "source.txt"
    source.write_text("line-1\nline-2\nline-3\n", encoding="utf-8")
    truncated = b"line-1\n"

    pin = runner.read_file_pin(
        source,
        repo_root=tmp_path,
        expected_bytes=source.read_bytes(),
        shell_read_bytes=truncated,
        shell_read_path=tmp_path / "truncated_mount" / "source.txt",
    )

    assert pin["prefix_truncation_detected"] is True
    assert pin["expected_size"] > pin["shell_read"]["observed_size"]
    assert pin["shell_read"]["is_prefix_of_authoritative"] is True
    assert pin["conflict_status"] == "bounded_prefix_truncation_detected"


def test_source_pin_report_rejects_self_comparison_for_critical_pin(tmp_path):
    from route_c_candidate_harness_001a import runner

    source = tmp_path / "source.txt"
    source.write_text("line-1\nline-2\nline-3\n", encoding="utf-8")

    report = runner.build_source_pin_readback_report(tmp_path, tmp_path / "out", [source])
    pin = report["critical_source_pins"][0]

    assert report["verdict"] == "source_pin_readback_completed"
    assert pin["comparison_signal_available"] is True
    assert pin["comparison_read_source"] != "self_comparison"
    assert pin["comparison_sha256"] == pin["sha256"]
