import inspect
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "ONE-GATE-FUTURE-ONLY-NON-CIRCULAR-EVIDENCE-HARNESS-001A"
CLAIM_CEILING = "future-only non-circular evidence-harness preflight only"
TARGET_GATE = "Gate4_future_only_evidence_harness_target"


def _runner():
    from one_gate_future_only_non_circular_harness_001a import runner

    return runner


def _raw_fixture() -> dict:
    return {
        "task_id": TASK_ID,
        "target_gate": TARGET_GATE,
        "candidate_id": "raw_output_only_candidate_fixture",
        "raw_traces": [
            {
                "seed": "seed_a",
                "context_id": "ctx_green",
                "episode_id": "ep_001",
                "serialized_state": {
                    "policy_map": {
                        "green": "approach",
                        "red": "avoid",
                        "blue": "wait",
                    }
                },
                "observation": {
                    "signal": "green",
                    "available_actions": ["approach", "avoid", "wait"],
                },
                "prediction": {"next_signal": "red"},
                "action": "approach",
            },
            {
                "seed": "seed_a",
                "context_id": "ctx_red",
                "episode_id": "ep_002",
                "serialized_state": {
                    "policy_map": {
                        "green": "approach",
                        "red": "avoid",
                        "blue": "wait",
                    }
                },
                "observation": {
                    "signal": "red",
                    "available_actions": ["approach", "avoid", "wait"],
                },
                "prediction": {"next_signal": "blue"},
                "action": "avoid",
            },
            {
                "seed": "seed_b",
                "context_id": "ctx_blue",
                "episode_id": "ep_003",
                "serialized_state": {
                    "policy_map": {
                        "green": "approach",
                        "red": "avoid",
                        "blue": "wait",
                    }
                },
                "observation": {
                    "signal": "blue",
                    "available_actions": ["approach", "avoid", "wait"],
                },
                "prediction": {"next_signal": "green"},
                "action": "wait",
            },
        ],
    }


def _control_payload(control_id: str, extra: dict) -> dict:
    payload = _raw_fixture()
    payload["candidate_id"] = control_id
    payload.update(extra)
    return payload


def test_raw_output_only_fixture_is_scored_by_harness_owned_registry():
    runner = _runner()

    report = runner.evaluate_candidate_outputs(_raw_fixture(), run_id="test-raw-fixture")

    assert report["task_id"] == TASK_ID
    assert report["selected_gate_target"] == TARGET_GATE
    assert report["admission_decision"] == "scored_future_only_preflight"
    assert report["candidate_blocked"] is False
    assert report["computed_score"] == 1.0
    assert report["baseline_result"]["producer_function"] == "majority_action_baseline"
    assert report["baseline_result"]["called"] is True
    assert report["baseline_result"]["score"] < report["computed_score"]
    assert report["ablation_result"]["producer_function"] == "remove_first_action_and_rerun"
    assert report["ablation_result"]["called"] is True
    assert report["ablation_result"]["score"] < report["computed_score"]
    assert report["replay_result"]["producer_function"] == "recompute_replay_from_state_observation"
    assert report["replay_result"]["used_serialized_state"] is True
    assert report["replay_result"]["used_observation"] is True
    assert report["replay_result"]["hash_only"] is False
    assert report["leakage_result"]["producer_function"] == "scan_for_candidate_controlled_evidence_fields"
    assert report["leakage_result"]["positive_control_detected"] is True
    assert report["metric_provenance"]["producer_function"] == "score_actions_from_raw_traces"
    assert report["metric_provenance"]["producer_source_path"].startswith(
        "src/one_gate_future_only_non_circular_harness_001a/"
    )
    assert report["metric_provenance"]["run_id"] == "test-raw-fixture"
    assert report["metric_provenance"]["input_artifact_hashes"]
    assert report["metric_provenance"]["seed_context_episode_ids"] == [
        {"seed": "seed_a", "context_id": "ctx_green", "episode_id": "ep_001"},
        {"seed": "seed_a", "context_id": "ctx_red", "episode_id": "ep_002"},
        {"seed": "seed_b", "context_id": "ctx_blue", "episode_id": "ep_003"},
    ]
    assert report["mainline_integration_status"] == "none"
    assert report["enabled_status"] == "local CLI/test runner only"
    assert report["claim_ceiling"] == CLAIM_CEILING


def test_registry_metric_producers_are_harness_owned_and_receive_no_row_argument():
    runner = _runner()

    registry = runner.metric_registry()

    assert set(registry) == {
        "score_actions_from_raw_traces",
        "majority_action_baseline",
        "remove_first_action_and_rerun",
        "scan_for_candidate_controlled_evidence_fields",
        "recompute_replay_from_state_observation",
    }
    for producer_name, producer in registry.items():
        signature = inspect.signature(producer)
        assert "row" not in signature.parameters
        source_path = runner.producer_source_path(producer)
        assert source_path.startswith("src/one_gate_future_only_non_circular_harness_001a/")
        assert "artifacts/" not in source_path
        assert "forged_bundles/" not in source_path


def test_all_verifier_001b_circular_positive_controls_block():
    runner = _runner()
    controls = {
        "constant_producer_fabricated_digest": _control_payload(
            "constant_producer_fabricated_digest",
            {
                "producer_function": "candidate_bundle.constant_producer",
                "expected_output_digest": "sha256:" + ("a" * 64),
            },
        ),
        "echo_producer_row_injection": _control_payload(
            "echo_producer_row_injection",
            {
                "producer_function": "candidate_bundle.echo_producer",
                "row": {"expected_output_digest": "sha256:" + ("b" * 64)},
            },
        ),
        "candidate_declared_score": _control_payload(
            "candidate_declared_score",
            {"expected_score": 1.0},
        ),
        "candidate_declared_baseline_pass": _control_payload(
            "candidate_declared_baseline_pass",
            {"baseline_result": {"verdict": "pass", "score": 1.0}},
        ),
        "candidate_declared_ablation_pass": _control_payload(
            "candidate_declared_ablation_pass",
            {"ablation_result": {"verdict": "pass", "score": 0.0}},
        ),
        "candidate_declared_replay_pass": _control_payload(
            "candidate_declared_replay_pass",
            {"replay_result": {"verdict": "pass", "replay_matches": True}},
        ),
    }

    reports = {
        control_id: runner.evaluate_candidate_outputs(payload, run_id=f"test-{control_id}")
        for control_id, payload in controls.items()
    }

    assert set(reports) == set(controls)
    for report in reports.values():
        assert report["candidate_blocked"] is True
        assert report["admission_decision"] == "blocked_candidate_controlled_evidence"
        assert report["computed_score"] is None
        assert report["metric_provenance"]["candidate_metric_producer_used"] is False

    assert "blocked_candidate_declared_producer_function" in reports[
        "constant_producer_fabricated_digest"
    ]["block_reason_ids"]
    assert "blocked_candidate_declared_expected_output_digest" in reports[
        "constant_producer_fabricated_digest"
    ]["block_reason_ids"]
    assert "blocked_candidate_declared_row" in reports["echo_producer_row_injection"][
        "block_reason_ids"
    ]
    assert "blocked_candidate_declared_expected_score" in reports[
        "candidate_declared_score"
    ]["block_reason_ids"]
    assert "blocked_candidate_declared_baseline_result" in reports[
        "candidate_declared_baseline_pass"
    ]["block_reason_ids"]
    assert "blocked_candidate_declared_ablation_result" in reports[
        "candidate_declared_ablation_pass"
    ]["block_reason_ids"]
    assert "blocked_candidate_declared_replay_result" in reports[
        "candidate_declared_replay_pass"
    ]["block_reason_ids"]


def test_ablation_corrupts_raw_input_and_rerun_cannot_report_unchanged_pass():
    runner = _runner()

    report = runner.evaluate_candidate_outputs(_raw_fixture(), run_id="test-ablation")
    ablation = report["ablation_result"]

    assert ablation["intervention_applied"] is True
    assert ablation["episodes_rerun"] is True
    assert ablation["score_recomputed"] is True
    assert ablation["score_changed_or_blocked"] is True
    assert ablation["unchanged_pass_report_accepted"] is False
    assert ablation["score"] != report["computed_score"]


def test_leakage_scanner_positive_control_detects_candidate_controlled_expected_value():
    runner = _runner()
    payload = _raw_fixture()
    payload["raw_traces"][0]["observation"]["expected_action"] = "approach"

    report = runner.evaluate_candidate_outputs(payload, run_id="test-leakage")

    assert report["candidate_blocked"] is True
    assert "blocked_leakage_detected" in report["block_reason_ids"]
    assert report["leakage_result"]["called"] is True
    assert report["leakage_result"]["positive_control_detected"] is True
    assert any(
        hit["field_path"].endswith("observation.expected_action")
        for hit in report["leakage_result"]["candidate_controlled_hits"]
    )


def test_replay_recomputes_action_from_state_and_observation_not_stored_hash():
    runner = _runner()
    payload = _raw_fixture()
    payload["raw_traces"][1]["action"] = "approach"

    report = runner.evaluate_candidate_outputs(payload, run_id="test-replay-mismatch")

    assert report["candidate_blocked"] is True
    assert "blocked_replay_mismatch" in report["block_reason_ids"]
    assert report["replay_result"]["called"] is True
    assert report["replay_result"]["behavior_recomputed"] is True
    assert report["replay_result"]["used_serialized_state"] is True
    assert report["replay_result"]["used_observation"] is True
    assert report["replay_result"]["stored_actions_reused"] is False
    assert report["replay_result"]["hash_only"] is False
    assert report["replay_result"]["mismatch_episode_ids"] == ["ep_002"]


def test_run_harness_writes_artifacts_without_using_verifier_001b(tmp_path):
    runner = _runner()
    out = tmp_path / "artifacts"

    result = runner.run_harness(repo_root=ROOT, output_dir=out, run_id="test-artifacts")

    expected_files = {
        "result.json",
        "trace.jsonl",
        "baseline_comparison.json",
        "ablation_report.json",
        "replay_report.json",
        "leakage_report.json",
        "positive_control_report.json",
        "metric_provenance.json",
        "failure_manifest.json",
        "claim_ceiling.txt",
        "execution_manifest.json",
    }
    assert {path.name for path in out.iterdir()} == expected_files
    assert result["task_id"] == TASK_ID
    assert result["selected_gate_target"] == TARGET_GATE
    assert result["acceptance_gates"]["all_circular_positive_controls_block"] is True
    assert result["acceptance_gates"]["raw_output_only_fixture_scored"] is True
    assert result["acceptance_gates"]["baseline_independently_invoked"] is True
    assert result["acceptance_gates"]["ablation_rerun_under_intervention"] is True
    assert result["acceptance_gates"]["leakage_positive_control_detected"] is True
    assert result["acceptance_gates"]["replay_recomputed_from_state_observation"] is True
    assert result["existing_verifier_001b_repaired_or_used_for_admission"] is False
    assert result["safe_to_wire_gate4"] is False
    assert result["safe_to_wire_ego_mainline"] is False
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING

    for path in out.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    assert all(line.strip() for line in (out / "trace.jsonl").read_text(encoding="utf-8").splitlines())

    provenance = json.loads((out / "metric_provenance.json").read_text(encoding="utf-8"))
    assert provenance["producer_function"] == "score_actions_from_raw_traces"
    assert provenance["candidate_metric_producer_used"] is False
    assert provenance["producer_source_path"].startswith(
        "src/one_gate_future_only_non_circular_harness_001a/"
    )
