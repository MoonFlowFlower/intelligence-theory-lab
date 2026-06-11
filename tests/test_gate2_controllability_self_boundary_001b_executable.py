import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gate2_controllability_self_boundary_001b.runner import run_preflight_001b


TASK_ID = "GATE2-CONTROLLABILITY-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001B"
PARENT_ANCHOR_COMMIT = "76a20d9"
CLAIM_CEILING = "bounded Gate2 controllability / self-boundary executable preflight evidence only"
ARTIFACT_DIR = ROOT / "artifacts" / "gate2_controllability_self_boundary_001b"
FORBIDDEN_001A_ARTIFACT_DIR = ROOT / "artifacts" / "gate2_controllability_self_boundary_001a"
TASK_CARD = (
    ROOT
    / "docs"
    / "codex"
    / "tasks"
    / "GATE2-CONTROLLABILITY-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001B.md"
)

REQUIRED_ARTIFACTS = {
    "stage0_freeze_manifest.json",
    "sha256_manifest.json",
    "external_anchor.json",
    "prediction_commit.json",
    "prediction_commit.sha256",
    "access_log.json",
    "trace.jsonl",
    "controllability_error_report.json",
    "self_boundary_update_report.json",
    "later_action_linkage_report.json",
    "later_behavior_evaluation.json",
    "leakage_report.json",
    "baseline_comparison.json",
    "control_comparison.json",
    "ablation_report.json",
    "replay_report.json",
    "mutation_check_report.json",
    "result.json",
    "claim_ceiling.txt",
    "execution_manifest.json",
    "execution_manifest.sha256",
    "run_ledger.jsonl",
    "final_report.md",
}

ALLOWED_VERDICTS = {
    "gate2_controllability_self_boundary_001b_bounded_preflight_pass",
    "gate2_controllability_self_boundary_001b_failed_baseline_match",
    "gate2_controllability_self_boundary_001b_failed_ablation_insensitive",
    "gate2_controllability_self_boundary_001b_failed_trace_contract",
    "gate2_controllability_self_boundary_001b_invalid_leakage",
    "gate2_controllability_self_boundary_001b_invalid_mutation",
    "gate2_controllability_self_boundary_001b_failed_stage0_freeze",
}

REQUIRED_BASELINES = {
    "retrieval / summary retrieval",
    "identity-tag lookup",
    "actor-id table",
    "action-outcome count table",
    "transition table / successor map / graph cache",
    "behavior-only imitation",
    "trace-only replay as hygiene only",
    "frozen-controllability model",
    "random-action policy",
    "oracle environment-label control",
}

REQUIRED_GRAPH_CACHE_VARIANTS = {
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
}

REQUIRED_ABLATIONS = {
    "action disabled",
    "control mapping inverted",
    "controllability feedback removed",
    "history replacement",
    "learning freeze",
    "environment perturbation",
    "delayed controllability effect",
    "partial observability",
    "heldout action-object compositions",
    "counterfactual action contrast",
}

REQUIRED_TRACE_FIELDS = {
    "action_id",
    "predicted_control_effect",
    "observed_effect",
    "controllability_error",
    "self_boundary_state_before",
    "self_boundary_state_after",
    "state_hash_before_action",
    "state_hash_after_action",
    "later_action_eval_id",
    "action_to_later_behavior_linkage_key",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_show_sha(relative_path: str, commit: str = PARENT_ANCHOR_COMMIT) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return hashlib.sha256(result.stdout).hexdigest()


def test_001b_run_emits_required_artifacts_under_correct_path(tmp_path):
    assert TASK_CARD.exists()

    result = run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    assert result["task_id"] == TASK_ID
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == "gate2_controllability_self_boundary_001b_bounded_preflight_pass"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["artifact_dir"] == "artifacts/gate2_controllability_self_boundary_001b"
    assert result["bounded_pass"] is True
    assert all(value is False for value in result["authorization_flags"].values())
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    assert (tmp_path / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING
    assert not (tmp_path / "failure_manifest.json").exists()


def test_stage0_freeze_uses_parent_001a_anchor_and_correct_artifact_path(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    stage0 = _read_json(tmp_path / "stage0_freeze_manifest.json")
    sha_manifest = _read_json(tmp_path / "sha256_manifest.json")
    anchor = _read_json(tmp_path / "external_anchor.json")

    parent_path = "docs/codex/tasks/GATE2-CONTROLLABILITY-SELF-BOUNDARY-TASK-CARD-001A.md"
    assert stage0["parent_task_card_commit"] == PARENT_ANCHOR_COMMIT
    assert stage0["parent_task_card_path"] == parent_path
    assert stage0["parent_task_card_sha256"] == _git_show_sha(parent_path)
    assert stage0["artifact_dir"] == "artifacts/gate2_controllability_self_boundary_001b"
    assert "gate2_controllability_self_boundary_001a" not in json.dumps(stage0)
    assert stage0["stage0_frozen_before_candidate_or_control_runs"] is True
    assert stage0["candidate_or_control_runs_started_before_stage0"] is False
    assert anchor["anchor_before_first_run"] is True
    assert sha_manifest[parent_path] == stage0["parent_task_card_sha256"]


def test_prediction_commit_is_frozen_before_reveal_and_access_is_allowlisted(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    commit = _read_json(tmp_path / "prediction_commit.json")
    access = _read_json(tmp_path / "access_log.json")
    commit_sha = (tmp_path / "prediction_commit.sha256").read_text(encoding="utf-8").strip()

    assert _sha256(tmp_path / "prediction_commit.json") == commit_sha
    assert commit["phase"] == "A_prediction_commit_before_reveal"
    assert commit["target_prediction_count"] == 6
    assert access["phase_order"][:4] == [
        "stage0_freeze_written",
        "external_anchor_written",
        "prediction_commit_written",
        "prediction_commit_hash_frozen",
    ]
    assert access["phase_a"]["prediction_commit_hash_frozen_before_reveal"] is True
    assert access["phase_a"]["forbidden_access_used"] is False
    assert access["phase_a"]["target_effects_read_before_prediction"] == 0
    assert access["phase_a"]["later_behavior_labels_read_before_prediction"] == 0
    assert access["phase_b"]["target_reveal_after_prediction_commit"] is True
    assert access["phase_b"]["prediction_commit_rewritten_after_reveal"] is False


def test_trace_contains_required_gate2_fields_and_hash_chain(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    rows = _read_jsonl(tmp_path / "trace.jsonl")
    assert len(rows) == 18
    assert rows[0]["previous_trace_hash"] == "GENESIS"
    for previous, current in zip(rows, rows[1:]):
        assert current["previous_trace_hash"] == previous["current_trace_hash"]
    for row in rows:
        assert REQUIRED_TRACE_FIELDS.issubset(row)
        assert row["state_hash_before_action"]
        assert row["state_hash_after_action"]
        assert row["state_hash_before_action"] != row["state_hash_after_action"]
        assert row["self_boundary_state_before"] != row["self_boundary_state_after"]
        assert row["access_manifest"]["later_action_eval_id_available_to_candidate"] is False
        assert row["access_manifest"]["forbidden_access_used"] is False


def test_linkage_keys_are_label_free_collision_free_and_mutation_checked(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    linkage = _read_json(tmp_path / "later_action_linkage_report.json")
    leakage = _read_json(tmp_path / "leakage_report.json")
    mutation = _read_json(tmp_path / "mutation_check_report.json")

    assert linkage["collision_count"] == 0
    assert linkage["linkage_key_collision_free"] is True
    assert linkage["label_free_key_material"] is True
    assert linkage["forbidden_key_material_detected"] is False
    assert leakage["leakage_detected"] is False
    assert leakage["linkage_keys_label_free"] is True
    assert leakage["oracle_labels_visible_to_candidate"] is False
    assert leakage["later_action_eval_id_leaked_before_eval"] is False
    assert mutation["post_evaluation_mutation_check_passed"] is True
    assert mutation["mutation_detected_after_evaluation"] is False


def test_baselines_are_executed_and_no_fair_baseline_matches_or_beats(tmp_path):
    result = run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)
    baseline = _read_json(tmp_path / "baseline_comparison.json")
    controls = _read_json(tmp_path / "control_comparison.json")

    assert set(baseline["baseline_names"]) == REQUIRED_BASELINES
    assert set(baseline["graph_cache_family_variants"]) == REQUIRED_GRAPH_CACHE_VARIANTS
    assert baseline["fair_baseline_match_blocks_gate"] is False
    assert baseline["trace_only_replay"]["classification"] == "trace_integrity_hygiene"
    assert baseline["trace_only_replay"]["counts_as_mechanism_evidence"] is False
    assert baseline["oracle_environment_label_control"]["classification"] == "oracle_leakage_upper_bound"
    assert baseline["oracle_environment_label_control"]["counts_as_fair_baseline"] is False
    assert baseline["best_fair_baseline"]["match_rate"] < baseline["thresholds"]["match_rate_threshold"]
    for control in controls["controls"]:
        if control["classification"] == "fair_control":
            assert control["matches_candidate"] is False
            assert control["match_rate"] < controls["thresholds"]["match_rate_threshold"]
    assert result["baseline_gate_passed"] is True


def test_all_required_ablations_are_sensitive(tmp_path):
    result = run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)
    ablation = _read_json(tmp_path / "ablation_report.json")

    assert set(ablation["ablation_names"]) == REQUIRED_ABLATIONS
    assert ablation["all_required_ablations_executed"] is True
    assert ablation["ablation_gate_passed"] is True
    for row in ablation["ablations"]:
        assert row["executed"] is True
        assert row["controllability_prediction_changed"] is True
        assert row["self_boundary_update_changed"] is True
        assert row["later_action_selection_changed"] is True
    assert result["ablation_gate_passed"] is True


def test_candidate_reports_bounded_controllability_and_later_behavior_linkage(tmp_path):
    result = run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)
    controllability = _read_json(tmp_path / "controllability_error_report.json")
    boundary = _read_json(tmp_path / "self_boundary_update_report.json")
    later = _read_json(tmp_path / "later_behavior_evaluation.json")

    assert controllability["heldout_controllability_prediction_accuracy"] >= 0.95
    assert controllability["mean_controllability_error"] == 0.0
    assert boundary["self_boundary_updates_present"] is True
    assert boundary["external_events_not_classified_as_self_caused"] is True
    assert later["later_action_selection_accuracy"] >= 0.95
    assert later["action_to_later_behavior_linkage_validity"] == 1.0
    assert result["candidate_proxy_evidence"]["state_update_alone_used_as_evidence"] is False
    assert result["candidate_proxy_evidence"]["later_behavior_linkage_required"] is True


def test_execution_manifest_hash_and_replay_report_are_valid(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    manifest_hash = (tmp_path / "execution_manifest.sha256").read_text(encoding="utf-8").strip()
    replay = _read_json(tmp_path / "replay_report.json")
    ledger = _read_jsonl(tmp_path / "run_ledger.jsonl")

    assert _sha256(tmp_path / "execution_manifest.json") == manifest_hash
    assert replay["hash_chain_valid"] is True
    assert replay["required_trace_fields_present"] is True
    assert replay["replay_reproduces_metrics"] is True
    assert replay["trace_only_replay_treated_as_mechanism_evidence"] is False
    assert [row["event"] for row in ledger][:4] == [
        "stage0_freeze",
        "external_anchor",
        "prediction_commit_freeze",
        "candidate_and_control_runs",
    ]


def test_committed_001b_artifacts_exist_after_main_run():
    result_path = ARTIFACT_DIR / "result.json"
    assert result_path.exists(), "run python -m gate2_controllability_self_boundary_001b first"

    result = _read_json(result_path)
    assert result["verdict"] == "gate2_controllability_self_boundary_001b_bounded_preflight_pass"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    assert not FORBIDDEN_001A_ARTIFACT_DIR.exists()
