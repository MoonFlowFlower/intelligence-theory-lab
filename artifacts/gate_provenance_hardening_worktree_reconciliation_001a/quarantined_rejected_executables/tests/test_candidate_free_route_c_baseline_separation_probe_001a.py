import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "CANDIDATE-FREE-ROUTE-C-BASELINE-SEPARATION-PROBE-001A"
ARTIFACT_DIR_NAME = "candidate_free_route_c_baseline_separation_probe_001a"
CLAIM_CEILING = (
    "Candidate-free route-governance existence probe only; no Route C mechanism validity, "
    "no hidden-self-set inference, no self-boundary evidence, no candidate success, no Gate pass, "
    "no mainline/runtime/live effect, no agency, autonomy, consciousness, emotion, stable user "
    "benefit, or EGO readiness."
)

REQUIRED_BASELINES = {
    "random",
    "greedy_info_gain",
    "exhaustive_legal_query",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
    "lookup_imitation",
    "direct_objective_optimizer",
    "amortized_least_squares",
    "mean",
    "variance",
    "correlation",
    "pca_subspace",
    "cross_episode",
    "supervised",
    "legal_field_membership",
    "positional_first_k",
}

PASSIVE_FAMILY = {
    "mean",
    "variance",
    "correlation",
    "pca_subspace",
    "cross_episode",
    "supervised",
    "legal_field_membership",
    "positional_first_k",
}

GRAPH_CACHE_FAMILY = {
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
}

REQUIRED_ARTIFACTS = {
    "result.json",
    "trace.jsonl",
    "baseline_comparison.json",
    "ablation_report.json",
    "replay_report.json",
    "leakage_scan.json",
    "source_pin_readback_report.json",
    "invalid_bundle_positive_control.json",
    "provenance_rows.jsonl",
    "claim_ceiling.txt",
    "readback.json",
}

PROVENANCE_FIELDS = {
    "producer_function",
    "inputs",
    "run_id",
    "seed",
    "episode_ids",
    "aggregation",
    "code_path_hash",
}


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _run_probe(tmp_path: Path):
    from candidate_free_route_c_baseline_separation_probe_001a import runner

    out = tmp_path / ARTIFACT_DIR_NAME
    result = runner.run_probe(repo_root=ROOT, output_dir=out, run_id="pytest-candidate-free-route-c")
    return result, out


def test_probe_writes_required_artifacts_and_candidate_free_route_verdict(tmp_path):
    result, out = _run_probe(tmp_path)

    assert result["task_id"] == TASK_ID
    assert result["decision_rule_verdict"] == "separation_exists_route_c_may_repromote_one_surface"
    assert result["current_layer"] == "engineering-governance / candidate-free baseline-separation existence probe"
    assert result["mainline_integration_status"] == "none"
    assert result["enabled_status"] == "local CLI/pytest only"
    assert result["real_trigger_evidence"]["executed_actual_toy_episodes"] is True
    assert result["real_trigger_evidence"]["oracle_callable_invoked"] is True
    assert result["real_trigger_evidence"]["baseline_callables_invoked"] == sorted(REQUIRED_BASELINES)
    assert result["real_trigger_evidence"]["local_cli_entrypoint"] == (
        "PYTHONPATH=src python -m candidate_free_route_c_baseline_separation_probe_001a"
    )
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["auto_remote_anchor"] == "forbidden"
    assert result["candidate_implemented"] is False
    assert result["gate_run"] is False
    assert result["safe_to_claim_mechanism_validity"] is False
    assert result["safe_to_wire_mainline"] is False
    assert result["next_minimal_closed_loop_action"] == (
        "Draft exactly one new Route C surface preflight gated on this candidate-free separation proof."
    )

    written = {path.name for path in out.iterdir() if path.is_file()}
    assert REQUIRED_ARTIFACTS.issubset(written)
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING

    readback = _load_json(out / "readback.json")
    assert readback["decision_rule_verdict"] == result["decision_rule_verdict"]
    assert readback["what_this_does_not_prove"] == result["what_this_does_not_prove"]
    assert "Route C mechanism validity" in readback["what_this_does_not_prove"]


def test_full_baseline_panel_runs_below_ceiling_while_oracle_reaches_ceiling(tmp_path):
    result, out = _run_probe(tmp_path)
    baseline = _load_json(out / "baseline_comparison.json")

    config = baseline["tested_configurations"][0]
    assert config["config_id"] == "route_c_candidate_free_sparse_hidden_set_v1"
    assert config["query_budget"] < config["legal_action_space_size"]
    assert config["oracle_score"] == 1.0
    assert config["strongest_fair_baseline"]["score"] < 1.0
    assert config["delta_oracle_vs_strongest_fair"] > 0.0
    assert config["passive_family_max"]["score"] < 1.0
    assert config["decision_gate"]["separation_exists"] is True

    rows = config["baseline_scores"]
    assert {row["baseline_id"] for row in rows} == REQUIRED_BASELINES
    assert all(row["callable_invoked"] is True for row in rows)
    assert all(row["score"] < 1.0 for row in rows)
    assert all(row["oracle_privileged_access_used"] is False for row in rows)
    assert max(row["score"] for row in rows if row["family"] == "passive") == config["passive_family_max"]["score"]
    assert max(row["score"] for row in rows) == config["strongest_fair_baseline"]["score"]
    assert {row["baseline_id"] for row in rows if row["family"] == "passive"} == PASSIVE_FAMILY
    assert GRAPH_CACHE_FAMILY.issubset({row["baseline_id"] for row in rows if row["family"] == "graph_cache"})

    named = {row["baseline_id"]: row for row in rows}
    assert named["random"]["score"] < 1.0
    assert named["exhaustive_legal_query"]["score"] < 1.0
    assert named["lookup_imitation"]["score"] < 1.0
    assert named["direct_objective_optimizer"]["score"] < 1.0
    assert named["amortized_least_squares"]["score"] < 1.0
    assert result["strongest_fair_baseline"] == config["strongest_fair_baseline"]


def test_provenance_leakage_positive_control_source_pin_and_replay_are_computed(tmp_path):
    _, out = _run_probe(tmp_path)

    provenance = _load_jsonl(out / "provenance_rows.jsonl")
    producers = {row["producer_function"] for row in provenance}
    assert "oracle.privileged_exact_solver" in producers
    assert {f"baseline.{baseline_id}" for baseline_id in REQUIRED_BASELINES}.issubset(producers)
    assert all(PROVENANCE_FIELDS.issubset(row) for row in provenance)
    assert all(row["score_source"] == "computed_from_episode_execution" for row in provenance)
    assert all(row["literal_or_static_score_used"] is False for row in provenance)
    assert all(row["code_path_hash"] for row in provenance)

    leakage = _load_json(out / "leakage_scan.json")
    assert leakage["verdict"] == "leakage_scan_passed"
    assert leakage["clean_bundle"]["detected"] is False
    assert leakage["positive_control"]["control_id"] == "oracle_field_in_legal_observation"
    assert leakage["positive_control"]["detected"] is True
    assert leakage["positive_control"]["blocked_bundle"] is True

    invalid = _load_json(out / "invalid_bundle_positive_control.json")
    assert invalid["verdict"] == "probe_invalid_repair_required"
    assert invalid["blocked"] is True
    assert invalid["reason"] == "privileged_oracle_field_visible_to_non_oracle_baseline"

    source_pin = _load_json(out / "source_pin_readback_report.json")
    assert source_pin["verdict"] == "source_pin_readback_passed"
    assert source_pin["authoritative_reader"] == "pathlib_direct_binary_read"
    assert source_pin["comparison_reader"] == "inspect_getsource"
    assert source_pin["dual_channel_match"] is True
    assert source_pin["positive_control"]["verdict"] == "source_pin_conflict_blocked"

    replay = _load_json(out / "replay_report.json")
    assert replay["verdict"] == "replay_recomputed"
    assert replay["stored_hash_only_used"] is False
    assert replay["recomputed_from_serialized_state_and_observation"] is True
    assert replay["score_delta_vs_original"] == 0.0
    assert replay["positive_control"]["verdict"] == "replay_mismatch_blocked"


def test_ablation_preserves_negative_saturation_control_and_cli_entrypoint(tmp_path):
    result, out = _run_probe(tmp_path)

    ablation = _load_json(out / "ablation_report.json")
    assert ablation["verdict"] == "ablation_controls_recorded"
    assert ablation["full_budget_saturation_control"]["query_budget_equals_action_space"] is True
    assert ablation["full_budget_saturation_control"]["exhaustive_legal_query_score"] == 1.0
    assert ablation["full_budget_saturation_control"]["preserved_as_negative_evidence"] is True
    assert ablation["zero_budget_control"]["strongest_fair_baseline_score"] < 1.0
    assert ablation["real_episode_rerun"] is True
    assert ablation["report_editing_used"] is False

    trace_rows = _load_jsonl(out / "trace.jsonl")
    assert trace_rows
    assert all("episode_id" in row for row in trace_rows)
    assert any(row["record_type"] == "oracle_prediction" for row in trace_rows)
    assert any(row["record_type"] == "baseline_prediction" for row in trace_rows)
    assert all(row["candidate_id"] is None for row in trace_rows)

    cli_out = tmp_path / "cli_artifacts"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "candidate_free_route_c_baseline_separation_probe_001a",
            "--output-dir",
            str(cli_out),
            "--run-id",
            "pytest-cli-route-c-probe",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )
    cli_result = json.loads(completed.stdout)
    assert cli_result["decision_rule_verdict"] == result["decision_rule_verdict"]
    assert (cli_out / "result.json").is_file()
