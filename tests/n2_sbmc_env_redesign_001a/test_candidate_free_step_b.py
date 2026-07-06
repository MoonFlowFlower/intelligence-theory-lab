from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


REQUIRED_BASELINES = {
    "per_user_lookup_nn",
    "graph_closure",
    "value_aware_embedding_outlier",
    "frequency_marginal",
    "structural_anomaly",
    "semantic_anomaly_provenance",
    "provenance_hash_chain",
    "predict_all",
    "predict_none",
    "majority",
}

REQUIRED_ARTIFACTS = {
    "step_a_preregistration.json",
    "result.json",
    "trace.jsonl",
    "baseline_comparison.json",
    "ablation_report.json",
    "replay_report.json",
    "leakage_report.json",
    "computed_evidence_provenance.json",
    "failure_manifest.json",
    "claim_ceiling.txt",
}


def _runner():
    from n2_sbmc_env_redesign_001a import runner

    return runner


def test_candidate_free_step_b_closes_on_graph_closure_baseline_equivalence(tmp_path):
    runner = _runner()

    run = runner.run_harness(output_dir=tmp_path / "run", persist_artifacts=False)
    result = run["result"]
    comparison = run["baseline_comparison"]

    assert result["verdict"] == "headroom_reachable_by_graph_closure"
    assert result["closure_type_recommended"] == "BASELINE_EQUIVALENCE"
    assert result["candidate_mechanism_run"] is False
    assert result["mechanism_experiment_run"] is False
    assert result["mainline_integration_status"] == "none"
    assert result["ideal_macro_f1"] >= 0.99
    assert comparison["strongest_fair_baseline"]["baseline_id"] == "graph_closure"
    assert comparison["strongest_fair_baseline"]["macro_f1"] >= result["ideal_macro_f1"] - result["equivalence_band"]
    assert set(comparison["baseline_ids"]) == REQUIRED_BASELINES
    assert comparison["missing_baseline_ids"] == []
    assert comparison["strongest_fair_is_max_over_full_battery"] is True
    assert comparison["per_user_lookup_broken"] is True
    collapsed = {row["producer_id"]: row["macro_f1"] for row in comparison["results"]}
    assert collapsed["semantic_anomaly_provenance"] <= result["blind_floor_max_macro_f1"]
    assert collapsed["provenance_hash_chain"] <= result["blind_floor_max_macro_f1"]


def test_leakage_replay_ablation_and_provenance_controls_are_callable_and_fail_able(tmp_path):
    runner = _runner()

    run = runner.run_harness(output_dir=tmp_path / "run", persist_artifacts=False)

    assert run["leakage_report"]["positive_control_fires"] is True
    assert run["leakage_report"]["clean_scan_passed"] is True
    assert run["replay_report"]["passed"] is True
    assert run["replay_report"]["uses_hash_only_comparison"] is False
    assert run["replay_report"]["uses_stored_outputs_only"] is False
    assert run["ablation_report"]["passed"] is True
    assert run["ablation_report"]["no_covered_observations"]["graph_closure_degraded"] is True
    assert run["ablation_report"]["wrong_relation_table"]["graph_closure_degraded"] is True
    assert run["ablation_report"]["sparse_coverage_control"]["passed"] is True
    assert runner.verify_provenance(run["computed_evidence_provenance"])["passed"] is True

    missing = runner.run_harness(
        output_dir=tmp_path / "missing",
        persist_artifacts=False,
        disabled_baselines=("graph_closure",),
    )
    assert missing["result"]["verdict"] == "blocked_missing_required_baseline"
    assert "missing_required_baseline:graph_closure" in missing["failure_manifest"]["blocking_reasons"]

    leaked = runner.run_harness(
        output_dir=tmp_path / "leak",
        persist_artifacts=False,
        disable_leakage_positive_control=True,
    )
    assert leaked["result"]["verdict"] == "blocked_leakage_positive_control_failure"
    assert "theta_canary_positive_control_not_detected" in leaked["failure_manifest"]["blocking_reasons"]

    replay_failed = runner.run_harness(
        output_dir=tmp_path / "replay",
        persist_artifacts=False,
        tamper_replay=True,
    )
    assert replay_failed["result"]["verdict"] == "blocked_replay_recompute_failure"
    assert "replay_recompute_mismatch" in replay_failed["failure_manifest"]["blocking_reasons"]


def test_persisted_artifacts_parse_and_preserve_claim_ceiling(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"

    run = runner.run_harness(output_dir=out, persist_artifacts=True)

    assert REQUIRED_ARTIFACTS <= {path.name for path in out.iterdir()}
    for name in REQUIRED_ARTIFACTS - {"trace.jsonl", "claim_ceiling.txt"}:
        json.loads((out / name).read_text(encoding="utf-8"))

    trace_lines = (out / "trace.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(trace_lines) == run["result"]["trace_row_count"]
    assert all("theta_AUDIT_ONLY" in json.loads(line) for line in trace_lines)
    assert all(json.loads(line)["candidate_decision"] is None for line in trace_lines)

    claim = (out / "claim_ceiling.txt").read_text(encoding="utf-8")
    assert "candidate-free N2/SBMC environment-preflight evidence" in claim
    assert "no mechanism validity" in claim
    assert "no EGO readiness" in claim


def test_route_state_payloads_validate_as_baseline_equivalence_closure():
    runner = _runner()
    from route_state_machine_001a import validator

    run = runner.run_harness(output_dir=Path("unused"), persist_artifacts=False)
    payloads = runner.build_route_state_payloads(run["result"])

    route_result = validator.validate_route_payload(
        route_id="N2-SBMC-ENV-REDESIGN-001A",
        state_payload=payloads["state"],
        closure_payload=payloads["closure"],
        changed_files=[],
        authorized_paths=[],
    )

    assert route_result["verdict"] == "pass"
    assert payloads["state"]["current_state"] == "CLOSURE_REVIEW_REQUIRED"
    assert payloads["closure"]["closure_type"] == "BASELINE_EQUIVALENCE"
    assert payloads["closure"]["theory_pressure_authorized"] is False
    assert payloads["closure"]["mechanism_evidence_authorized"] is False
