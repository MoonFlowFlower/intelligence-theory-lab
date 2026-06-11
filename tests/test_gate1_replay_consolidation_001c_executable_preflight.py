import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gate1_replay_consolidation_001c.runner import run_preflight_001c


ARTIFACT_DIR = ROOT / "artifacts" / "gate1_replay_consolidation_001c_executable_preflight"
TASK_ID = "GATE1-REPLAY-CONSOLIDATION-001C-EXECUTABLE-PREFLIGHT"
CLAIM_CEILING = "bounded Gate1 replay/consolidation executable preflight evidence only"
VERDICT = "gate1_replay_consolidation_001c_bounded_preflight_pass"
BASE_TASK_CARD_ANCHOR = "b813651"
AMENDMENT_ANCHOR = "5734dc8"

REQUIRED_ARTIFACTS = {
    "replay_event_log.json",
    "consolidation_trace.json",
    "state_hash_chain.json",
    "replay_behavior_linkage_table.json",
    "linkage_key_collision_report.json",
    "later_behavior_evaluation.json",
    "mutation_check_report.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "result.json",
    "claim_ceiling.txt",
    "execution_manifest.json",
    "execution_manifest.sha256",
    "access_log.json",
    "run_ledger.jsonl",
}
REQUIRED_BASELINES = {
    "retrieval / summary retrieval",
    "behavior-only replay",
    "trace-only replay as hygiene only",
    "online count/statistic controls",
    "transition table / successor map / graph cache controls",
    "target-free generative replay challenger",
    "frozen-history control",
    "no-consolidation control",
    "shuffled-replay control",
    "corrupted-replay control",
}
REQUIRED_ABLATIONS = {
    "learning freeze",
    "history replacement",
    "consolidation disabled",
    "replay order shuffled",
    "replay content corrupted",
    "heldout composition",
    "delayed-effect cases",
    "observable-key conflict cases",
    "partial-observability cases",
    "counterfactual action contrast",
}
FORBIDDEN_LINKAGE_INPUTS = {
    "heldout_outcome",
    "target_heldout_outcome",
    "future_behavior_label",
    "target_future_behavior_label",
    "witness_result",
    "witness_match_result",
    "post_evaluation_metric",
    "post_evaluation_metrics",
}
ALLOWED_VERDICTS = {
    "gate1_replay_consolidation_001c_bounded_preflight_pass",
    "gate1_replay_consolidation_001c_failed_baseline_match",
    "gate1_replay_consolidation_001c_failed_ablation",
    "gate1_replay_consolidation_001c_failed_trace_linkage",
    "gate1_replay_consolidation_001c_invalid_leakage",
    "gate1_replay_consolidation_001c_invalid_artifact_mutation",
}
PROTECTED_ANCHORS = {
    BASE_TASK_CARD_ANCHOR: [
        "docs/codex/tasks/GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A.md",
        "artifacts/gate1_replay_consolidation_task_card_001a/task_card_result.json",
    ],
    "4e3e9f2": [
        "artifacts/gate1_replay_consolidation_task_card_001b_independent_audit/independent_audit_result.json",
        "artifacts/gate1_replay_consolidation_task_card_001b_independent_audit/audit_matrix.json",
    ],
    AMENDMENT_ANCHOR: [
        "artifacts/gate1_task_card_001a_amendment_001_trace_replay_contract_patch/amendment_result.json",
        "artifacts/gate1_task_card_001a_amendment_001_trace_replay_contract_patch/trace_replay_contract_patch.json",
        "artifacts/gate1_task_card_001a_amendment_001_trace_replay_contract_patch/linkage_key_contract.json",
    ],
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha(obj: dict) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _linkage_key(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def _normalized_sha256_text(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def _git_show_text_sha(commit: str, relative_path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"],
        cwd=ROOT,
        capture_output=True,
        check=True,
        encoding="utf-8",
    )
    return _normalized_sha256_text(result.stdout)


def test_001c_runner_emits_required_artifacts_and_bounded_result(tmp_path):
    result = run_preflight_001c(repo_root=ROOT, output_dir=tmp_path)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    assert result["task_id"] == TASK_ID
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == VERDICT
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["effective_contract"] == {
        "gate1_task_card_001a_commit": BASE_TASK_CARD_ANCHOR,
        "amendment_001_commit": AMENDMENT_ANCHOR,
    }
    assert result["gate1_execution_layer"] == "bounded executable preflight only"
    assert all(value is False for value in result["authorization_flags"].values())
    assert (tmp_path / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING


def test_manifest_is_frozen_before_later_behavior_evaluation_and_not_mutated(tmp_path):
    run_preflight_001c(repo_root=ROOT, output_dir=tmp_path)

    manifest = _read_json(tmp_path / "execution_manifest.json")
    access_log = _read_json(tmp_path / "access_log.json")
    evaluation = _read_json(tmp_path / "later_behavior_evaluation.json")
    mutation = _read_json(tmp_path / "mutation_check_report.json")

    expected_manifest_hash = _canonical_sha(manifest)
    assert (tmp_path / "execution_manifest.sha256").read_text(encoding="utf-8").strip() == expected_manifest_hash
    assert access_log["phase_order"] == [
        "execution_manifest_written",
        "execution_manifest_hash_frozen",
        "replay_and_consolidation_traces_written",
        "manifest_hash_verified_before_later_behavior_evaluation",
        "later_behavior_evaluation_written",
        "mutation_check_after_later_behavior_evaluation_written",
    ]
    assert evaluation["manifest_sha256_verified_before_evaluation"] == expected_manifest_hash
    assert mutation["manifest_sha256_before_later_behavior_evaluation"] == expected_manifest_hash
    assert mutation["manifest_sha256_after_later_behavior_evaluation"] == expected_manifest_hash
    assert mutation["mutation_detected_after_later_behavior_evaluation"] is False
    assert mutation["post_evaluation_mutation_check_passed"] is True


def test_replay_trace_has_state_boundaries_and_deterministic_label_free_linkage(tmp_path):
    run_preflight_001c(repo_root=ROOT, output_dir=tmp_path)

    replay_log = _read_json(tmp_path / "replay_event_log.json")
    consolidation = _read_json(tmp_path / "consolidation_trace.json")
    state_chain = _read_json(tmp_path / "state_hash_chain.json")
    linkage = _read_json(tmp_path / "replay_behavior_linkage_table.json")
    collision = _read_json(tmp_path / "linkage_key_collision_report.json")
    manifest = _read_json(tmp_path / "execution_manifest.json")

    replay_by_id = {row["replay_event_id"]: row for row in replay_log["events"]}
    consolidation_by_id = {row["consolidation_event_id"]: row for row in consolidation["events"]}
    assert replay_log["all_events_have_state_hash_before_replay"] is True
    assert replay_log["all_events_have_state_hash_after_replay"] is True
    assert replay_log["all_events_have_linkage_key"] is True
    assert state_chain["hash_chain_valid"] is True
    assert collision["collision_count"] == 0
    assert collision["linkage_key_uniqueness_check_passed"] is True

    for row in linkage["rows"]:
        replay = replay_by_id[row["replay_event_id"]]
        cons = consolidation_by_id[row["consolidation_event_id"]]
        assert replay["state_hash_before_replay"]
        assert replay["state_hash_after_replay"]
        assert replay["state_hash_before_replay"] != replay["state_hash_after_replay"]
        assert cons["consolidation_state_hash_before"]
        assert cons["consolidation_state_hash_after"]
        assert cons["consolidation_state_hash_before"] == replay["state_hash_after_replay"]
        assert cons["consolidation_state_hash_before"] != cons["consolidation_state_hash_after"]
        assert row["key_material_fields"] == manifest["linkage_key_derivation_rule"]["allowed_formula_inputs"]
        assert not (set(row["key_material_fields"]) & FORBIDDEN_LINKAGE_INPUTS)
        assert row["forbidden_key_material_absent"] is True
        assert row["replay_to_behavior_linkage_key"] == _linkage_key(
            manifest["gate1_run_id"],
            row["target_case_id"],
            row["replay_event_id"],
            row["consolidation_event_id"],
            row["later_behavior_eval_id"],
        )


def test_baselines_are_complete_and_trace_only_replay_is_hygiene_only(tmp_path):
    run_preflight_001c(repo_root=ROOT, output_dir=tmp_path)

    baseline = _read_json(tmp_path / "baseline_comparison.json")
    by_name = {item["baseline_name"]: item for item in baseline["baselines"]}

    assert set(by_name) == REQUIRED_BASELINES
    assert baseline["any_baseline_equivalent_to_candidate"] is False
    assert baseline["baseline_match_blocks_gate"] is False
    for name, record in by_name.items():
        assert record["executed"] is True
        if name == "trace-only replay as hygiene only":
            assert record["classification"] == "trace_integrity_hygiene"
            assert record["counts_as_mechanism_evidence"] is False
            assert record["match_rate"] == 1.0
        else:
            assert record["counts_as_mechanism_evidence"] is False
            assert record["match_rate"] < baseline["equivalence_threshold"]


def test_required_ablations_are_complete_and_process_sensitive(tmp_path):
    run_preflight_001c(repo_root=ROOT, output_dir=tmp_path)

    report = _read_json(tmp_path / "ablation_report.json")
    by_name = {item["ablation_name"]: item for item in report["ablations"]}

    assert set(by_name) == REQUIRED_ABLATIONS
    assert report["all_required_ablations_executed"] is True
    assert report["ablation_gate_passed"] is True
    for record in by_name.values():
        assert record["executed"] is True
        assert record["changed_expected_later_behavior"] is True
        assert record["process_sensitive_trace_changed"] is True


def test_committed_001c_artifacts_exist_and_old_anchors_are_not_mutated():
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    result = _read_json(ARTIFACT_DIR / "result.json")
    assert result["verdict"] == VERDICT
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["historical_001b_reclassified_as_pass"] is False
    assert result["trace_only_replay_treated_as_mechanism_evidence"] is False

    for commit, relative_paths in PROTECTED_ANCHORS.items():
        for relative_path in relative_paths:
            current = _normalized_sha256_text((ROOT / relative_path).read_text(encoding="utf-8"))
            assert current == _git_show_text_sha(commit, relative_path)
