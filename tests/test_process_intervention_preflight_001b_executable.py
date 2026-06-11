import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from negative_evidence_admission_gate_001a import evaluate_successor_task
from process_intervention_preflight_001b.runner import run_preflight_001b


TASK_CARD = (
    ROOT
    / "docs"
    / "codex"
    / "tasks"
    / "PROCESS-INTERVENTION-PREFLIGHT-001B-EXECUTABLE-PREFLIGHT-TASK-CARD.md"
)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_001b_admission_gate_passes_before_executable_run():
    result = evaluate_successor_task(TASK_CARD.read_text(encoding="utf-8"))

    assert result["passed"] is True
    assert result["failure_ids"] == []
    assert "missing_001a_supersession" in result["checked_rules"]
    assert "missing_001b_fair_control_failure" in result["checked_rules"]
    assert "gate1_replay_pass_ignores_graph_cache_collapse" in result["checked_rules"]


def test_001b_run_fails_cleanly_when_fair_controls_match(tmp_path):
    result = run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    assert result["task_id"] == "PROCESS-INTERVENTION-PREFLIGHT-001B"
    assert result["verdict"] == "process_intervention_preflight_001b_failed_control_separation_statistic_match"
    assert result["bounded_pass"] is False
    assert result["negative_evidence_recorded"] is True
    assert result["mechanism_evidence_claimed"] is False
    assert result["support_pack_or_semantic_audit_treated_as_mechanism_evidence"] is False
    assert result["gate1_evidence_claimed"] is False
    assert result["same_agent_bridge_evidence_claimed"] is False
    assert result["ego_readiness_claimed"] is False
    assert result["old_experiments_rerun"] is False
    assert result["old_artifacts_repaired"] is False
    assert result["fable_or_poisoning_line_expanded"] is False
    assert result["next_allowed_task"] == "record_negative_evidence_or_simplify_process_intervention_framing"

    assert "fair_count_statistic_control_matched" in result["stop_conditions"]
    assert "fair_graph_cache_control_matched" in result["stop_conditions"]
    assert "trace_only_replay_matched" in result["stop_conditions"]
    assert result["thresholds"]["match_rate_threshold"] == 0.95
    assert result["thresholds"]["separation_margin_threshold"] == 0.1
    assert result["best_fair_control"]["control_name"] == "online_count_statistic"
    assert result["best_fair_control"]["separation_margin"] == 0.0


def test_001b_artifacts_use_support_pack_as_frozen_input(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    required = {
        "admission_gate_result.json",
        "stage0_freeze_manifest.json",
        "sha256_manifest.json",
        "external_anchor.json",
        "frozen_inputs.json",
        "run_config.json",
        "trace.jsonl",
        "replay_report.json",
        "control_comparison.json",
        "baseline_comparison.json",
        "failure_manifest.json",
        "result.json",
        "claim_ceiling.txt",
        "final_report.md",
        "run_ledger.jsonl",
    }
    assert required.issubset({path.name for path in tmp_path.iterdir()})

    frozen = _read_json(tmp_path / "frozen_inputs.json")
    assert frozen["support_pack_task_id"] == "PROCESS-INTERVENTION-PREFLIGHT-001A-AMENDMENT-001-SUPPORT-PACK-001"
    assert frozen["support_pack_result"]["verdict"] == "support_pack_001_ready_for_single_semantic_audit_rerun"
    assert frozen["semantic_audit_rerun_result"]["verdict"] == (
        "semantic_audit_pass_support_pack_executable_readiness_only"
    )
    assert frozen["semantic_audit_rerun_is_mechanism_evidence"] is False

    stage0 = _read_json(tmp_path / "stage0_freeze_manifest.json")
    assert stage0["freeze_before_first_run"] is True
    assert stage0["support_contracts_frozen"] is True
    assert len(stage0["support_contract_hashes"]) >= 11
    assert stage0["negative_evidence_admission"]["passed"] is True

    sha_manifest = _read_json(tmp_path / "sha256_manifest.json")
    assert "docs/codex/tasks/PROCESS-INTERVENTION-PREFLIGHT-001B-EXECUTABLE-PREFLIGHT-TASK-CARD.md" in sha_manifest
    assert "artifacts/process_intervention_preflight_001a_amendment_001_support_pack_001/support_pack_result.json" in sha_manifest


def test_001b_controls_trace_replay_and_verdict_string_rejection(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    trace = _read_jsonl(tmp_path / "trace.jsonl")
    assert len(trace) == 96
    assert trace[0]["previous_trace_hash"] == "GENESIS"
    for previous, current in zip(trace, trace[1:]):
        assert current["previous_trace_hash"] == previous["current_trace_hash"]
        assert current["commit_index"] == previous["commit_index"] + 1
        assert current["prediction_error_or_update_signal"] in {"match", "mismatch"}
        assert current["access_manifest"]["forbidden_access_used"] is False

    replay = _read_json(tmp_path / "replay_report.json")
    assert replay["hash_chain_valid"] is True
    assert replay["allowed_update_path_replay_valid"] is True
    assert replay["memory_key_fidelity_replay_valid"] is True
    assert replay["trace_only_replay_match_rate"] == 1.0
    assert replay["posthoc_trace_generation_detected"] is False

    controls = _read_json(tmp_path / "control_comparison.json")
    assert controls["required_control_families_present"] is True
    assert controls["controls"]["online_count_statistic"]["match_rate"] == 1.0
    assert controls["controls"]["graph_cache"]["match_rate"] == 1.0
    assert controls["controls"]["transition_table"]["match_rate"] == 1.0
    assert controls["controls"]["successor_map"]["match_rate"] == 1.0
    assert controls["controls"]["trace_only_replay"]["match_rate"] == 1.0
    assert controls["controls"]["posthoc_verdict_string"]["accepted_as_evidence"] is False
    assert controls["controls"]["posthoc_verdict_string"]["match_rate"] == 0.0

    failure = _read_json(tmp_path / "failure_manifest.json")
    assert failure["failure_type"] == "fair_controls_matched_process_intervention"
    assert "process_intervention_preflight_001b_failed_control_separation_statistic_match" in failure["verdict"]
    assert failure["do_not_patch_into_pass"] is True


def test_001b_support_contract_insufficiency_is_classified_not_meta_audited(tmp_path):
    result = run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    assert result["support_contract_classification"] == {
        "blocking": [],
        "nonblocking": [],
        "backlog": [],
    }
    assert result["new_meta_audit_created"] is False
    assert result["nonblocking_caveats_spawned_new_tasks"] is False


def test_001b_committed_artifact_run_records_clean_negative_evidence():
    artifact_dir = ROOT / "artifacts" / "process_intervention_preflight_001b"
    result_path = artifact_dir / "result.json"

    assert result_path.exists(), "run python -m process_intervention_preflight_001b first"
    result = _read_json(result_path)
    controls = _read_json(artifact_dir / "control_comparison.json")
    failure = _read_json(artifact_dir / "failure_manifest.json")

    assert result["verdict"] == "process_intervention_preflight_001b_failed_control_separation_statistic_match"
    assert result["bounded_pass"] is False
    assert result["negative_evidence_recorded"] is True
    assert result["negative_evidence_admission"]["passed"] is True
    assert result["negative_evidence_admission"]["failure_ids"] == []
    assert result["best_fair_control"]["control_name"] == "online_count_statistic"
    assert controls["controls"]["online_count_statistic"]["match_rate"] == 1.0
    assert controls["controls"]["graph_cache"]["match_rate"] == 1.0
    assert controls["controls"]["trace_only_replay"]["match_rate"] == 1.0
    assert controls["controls"]["posthoc_verdict_string"]["accepted_as_evidence"] is False
    assert failure["do_not_patch_into_pass"] is True
