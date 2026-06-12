import hashlib
import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


TASK_ID = "POST-BRIDGE-ADMISSION-EXECUTABLE-001C"
VERDICT = "post_bridge_admission_executable_001c_pass"
CLAIM_CEILING = "bounded post-bridge admission evidence under computed-evidence provenance contract only"
ARTIFACT_DIR = ROOT / "artifacts" / "post_bridge_admission_executable_001c"
CONTRACT_PATH = ROOT / "docs" / "codex" / "contracts" / "COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md"
TASK_CARD = ROOT / "docs" / "codex" / "tasks" / "POST-BRIDGE-ADMISSION-EXECUTABLE-001C.md"


REQUIRED_ARTIFACTS = {
    "stage0_freeze_manifest.json",
    "execution_manifest.json",
    "execution_manifest.sha256",
    "run_ledger.jsonl",
    "distribution_manifest.json",
    "serialized_state_provenance.jsonl",
    "metric_provenance.jsonl",
    "baseline_invocation_log.jsonl",
    "ablation_invocation_log.jsonl",
    "leakage_scanner_invocation_log.jsonl",
    "contrast_pair_consumption_log.jsonl",
    "frozen_input_consumption_report.json",
    "trace.jsonl",
    "observation_seed_manifest.json",
    "serialized_state_snapshots.jsonl",
    "candidate_action_replay_report.json",
    "behavior_causal_replay_report.json",
    "trace_hash_replay_report.json",
    "state_hash_replay_report.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "contrast_report.json",
    "leakage_report.json",
    "mutation_check_report.json",
    "protected_artifact_inventory_before.json",
    "protected_artifact_hashes_before.json",
    "protected_artifact_hashes_after.json",
    "tracked_old_artifact_mutation_report.json",
    "computed_evidence_provenance_report.json",
    "result.json",
    "claim_ceiling.txt",
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


def _modules():
    core = importlib.import_module("post_bridge_admission_executable_001c.core")
    runner = importlib.import_module("post_bridge_admission_executable_001c.runner")
    return core, runner


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_001c_run_emits_required_artifacts_and_cites_contract(tmp_path):
    core, runner = _modules()

    result = runner.run_admission_001c(
        repo_root=ROOT,
        output_dir=tmp_path,
        enforce_clean_worktree=False,
    )

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == VERDICT
    assert result["bounded_pass"] is True
    assert result["artifact_dir"] == "artifacts/post_bridge_admission_executable_001c"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    assert not (tmp_path / "failure_manifest.json").exists()
    assert (tmp_path / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING
    assert core.CONTRACT_PATH == "docs/codex/contracts/COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md"
    assert "COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A" in TASK_CARD.read_text(encoding="utf-8")


def test_stage0_freeze_covers_parent_anchors_contract_agents_and_registries(tmp_path):
    core, runner = _modules()
    runner.run_admission_001c(repo_root=ROOT, output_dir=tmp_path, enforce_clean_worktree=False)

    stage0 = _read_json(tmp_path / "stage0_freeze_manifest.json")
    distribution = _read_json(tmp_path / "distribution_manifest.json")
    manifest = _read_json(tmp_path / "execution_manifest.json")

    assert stage0["stage0_freeze_before_any_executable_run"] is True
    assert stage0["executable_run_started_before_stage0"] is False
    assert stage0["canonical_clean_worktree_required"] is True
    assert stage0["clean_worktree_before_stage0"]["enforced"] is False
    assert stage0["parent_remote_anchor_verification"]["verified"] is True
    assert stage0["redteam_failure_admission_verification"]["verified"] is True
    assert stage0["computed_evidence_contract"]["path"] == core.CONTRACT_PATH
    assert stage0["computed_evidence_contract"]["hash"] == _file_sha(CONTRACT_PATH)
    assert stage0["agents_instruction_hash"] == _file_sha(ROOT / "AGENTS.md")
    assert set(stage0["baseline_implementation_registry"]) == set(core.REQUIRED_BASELINES)
    assert set(stage0["ablation_intervention_registry"]) == set(core.REQUIRED_ABLATIONS)
    assert set(stage0["leakage_scanner_registry"]) == set(core.REQUIRED_LEAKAGE_SCANNERS)
    assert set(stage0["replay_function_registry"]) >= {
        "replay_candidate_actions_from_serialized_state",
        "behavior_causal_replay",
    }
    assert set(stage0["frozen_contract_items"]) >= {
        "task_card_hash",
        "computed_evidence_contract_hash",
        "agents_instruction_hash",
        "thresholds",
        "metrics",
        "baseline_implementation_registry",
        "ablation_intervention_registry",
        "leakage_scanner_registry",
        "replay_functions",
        "distribution_manifest_hash",
        "seed_families",
        "train_contexts",
        "heldout_contexts",
        "counterfactual_pairs",
        "cross_agent_state_swap_pairs",
        "duplicate_identity_token_contrast_pairs",
        "artifact_schema",
        "stop_conditions",
        "rollback_plan",
        "claim_ceiling",
    }
    assert _file_sha(tmp_path / "execution_manifest.json") == (
        tmp_path / "execution_manifest.sha256"
    ).read_text(encoding="utf-8").strip()
    assert manifest["stage0_freeze_manifest_hash"] == _file_sha(tmp_path / "stage0_freeze_manifest.json")

    assert distribution["actual_counts"]["train_contexts"] >= 24
    assert distribution["actual_counts"]["heldout_bridge_contexts"] >= 48
    assert distribution["actual_counts"]["counterfactual_state_pairs"] >= 16
    assert distribution["actual_counts"]["cross_agent_state_swap_pairs"] >= 16
    assert distribution["actual_counts"]["duplicate_identity_token_contrasts"] >= 16
    assert distribution["actual_counts"]["independent_seed_families"] >= 4


def test_frozen_inputs_are_consumed_by_callable_paths(tmp_path):
    core, runner = _modules()
    runner.run_admission_001c(repo_root=ROOT, output_dir=tmp_path, enforce_clean_worktree=False)

    report = _read_json(tmp_path / "frozen_input_consumption_report.json")
    distribution = _read_json(tmp_path / "distribution_manifest.json")

    assert report["verdict"] == "all_frozen_inputs_consumed"
    assert report["unused_frozen_inputs"] == []
    assert set(report["ablation_ids_consumed"]) == set(core.REQUIRED_ABLATIONS)
    assert set(report["seed_family_ids_consumed"]) == {
        row["family_id"] for row in distribution["seed_families"]
    }
    assert set(report["train_context_ids_consumed"]) == {
        row["context_id"] for row in distribution["train_contexts"]
    }
    assert set(report["heldout_context_ids_consumed"]) == {
        row["heldout_context_id"] for row in distribution["heldout_bridge_contexts"]
    }
    assert set(report["counterfactual_pair_ids_consumed"]) == {
        row["pair_id"] for row in distribution["counterfactual_state_pairs"]
    }
    assert set(report["cross_agent_state_swap_pair_ids_consumed"]) == {
        row["pair_id"] for row in distribution["cross_agent_state_swap_pairs"]
    }
    assert set(report["duplicate_identity_token_contrast_ids_consumed"]) == {
        row["contrast_id"] for row in distribution["duplicate_identity_token_contrasts"]
    }


def test_metric_provenance_rows_are_complete_and_non_literal(tmp_path):
    _core, runner = _modules()
    runner.run_admission_001c(repo_root=ROOT, output_dir=tmp_path, enforce_clean_worktree=False)

    rows = _read_jsonl(tmp_path / "metric_provenance.jsonl")
    report = _read_json(tmp_path / "computed_evidence_provenance_report.json")
    result = _read_json(tmp_path / "result.json")

    assert rows
    assert report["computed_evidence_provenance_gate_passed"] is True
    assert report["literal_or_static_metric_detected"] is False
    assert report["missing_metric_provenance"] == []
    assert set(result["verdict_bearing_metric_ids"]).issubset({row["metric_id"] for row in rows})
    for row in rows:
        assert REQUIRED_METRIC_FIELDS.issubset(row)
        assert row["producer_function"]
        assert row["producer_module"].startswith("post_bridge_admission_executable_001c")
        assert len(row["code_path_hash"]) == 64
        assert row["computed_not_literal"] is True
        assert row["failure_path_available"] is True
        assert row["threshold_frozen_before_run"] is True
        assert row["input_artifact_paths"]
        assert set(row["input_artifact_paths"]) == set(row["input_artifact_hashes"])
        assert row["input_row_count"] > 0
        assert row["output_artifact_path"]
        assert row["output_row_ids"]


def test_baselines_are_callable_invoked_and_scores_come_from_outputs(tmp_path):
    core, runner = _modules()
    runner.run_admission_001c(repo_root=ROOT, output_dir=tmp_path, enforce_clean_worktree=False)

    report = _read_json(tmp_path / "baseline_comparison.json")
    invocations = _read_jsonl(tmp_path / "baseline_invocation_log.jsonl")
    names = {row["baseline_name"] for row in invocations}

    assert set(core.REQUIRED_BASELINES) == names
    assert report["baseline_gate_passed"] is True
    assert report["best_fair_baseline"]["score"] < report["thresholds"]["fair_baseline_must_be_below"]
    assert report["candidate"]["candidate_score"] == 1.0
    assert report["candidate"]["score_source"] == "computed_from_candidate_outputs"
    assert all(row["invoked"] for row in invocations)
    assert all(row["computed_from_outputs"] for row in invocations)
    assert all(row["per_episode_outputs"] for row in invocations)
    assert all(len(row["code_path_hash"]) == 64 for row in invocations)
    assert any(row["score"] != report["candidate"]["candidate_score"] for row in invocations)


def test_ablation_interventions_rerun_candidate_and_change_state_hashes(tmp_path):
    core, runner = _modules()
    runner.run_admission_001c(repo_root=ROOT, output_dir=tmp_path, enforce_clean_worktree=False)

    report = _read_json(tmp_path / "ablation_report.json")
    invocations = _read_jsonl(tmp_path / "ablation_invocation_log.jsonl")

    assert set(core.REQUIRED_ABLATIONS) == {row["ablation_name"] for row in invocations}
    assert report["ablation_gate_passed"] is True
    assert all(row["invoked"] for row in invocations)
    assert all(row["reran_candidate_behavior"] for row in invocations)
    assert all(row["intervention_applied"] for row in invocations)
    assert all(row["pre_intervention_state_hash"] != row["post_intervention_state_hash"] for row in invocations)
    assert all(row["score"] < report["thresholds"]["required_ablation_must_be_below"] for row in invocations)
    assert all(len(row["code_path_hash"]) == 64 for row in invocations)


def test_contrasts_consume_prefrozen_pairs_and_compute_deltas(tmp_path):
    core, runner = _modules()
    runner.run_admission_001c(repo_root=ROOT, output_dir=tmp_path, enforce_clean_worktree=False)

    report = _read_json(tmp_path / "contrast_report.json")
    log = _read_jsonl(tmp_path / "contrast_pair_consumption_log.jsonl")

    assert set(core.REQUIRED_CONTRASTS) == {row["contrast_name"] for row in log}
    assert report["contrast_gate_passed"] is True
    assert all(row["pair_ids_consumed"] for row in log)
    assert all(row["reran_candidate_behavior"] for row in log)
    assert all(row["computed_delta_from_outputs"] for row in log)
    assert report["identity_token_alone_explains_behavior"] is False
    assert report["memory_key_alone_explains_behavior"] is False


def test_leakage_scanners_have_positive_and_clean_controls(tmp_path):
    core, runner = _modules()
    runner.run_admission_001c(repo_root=ROOT, output_dir=tmp_path, enforce_clean_worktree=False)

    report = _read_json(tmp_path / "leakage_report.json")
    log = _read_jsonl(tmp_path / "leakage_scanner_invocation_log.jsonl")

    assert set(core.REQUIRED_LEAKAGE_SCANNERS) == {row["scanner_name"] for row in log}
    assert report["leakage_gate_passed"] is True
    assert all(row["scanner_function"] for row in log)
    assert all(len(row["code_path_hash"]) == 64 for row in log)
    assert all(row["positive_control"]["detected"] for row in log)
    assert all(row["clean_control"]["detected"] is False for row in log)
    assert all(row["real_scan"]["detected"] is False for row in log)


def test_behavior_replay_recomputes_candidate_action_from_serialized_state_and_observation(tmp_path):
    core, runner = _modules()
    runner.run_admission_001c(repo_root=ROOT, output_dir=tmp_path, enforce_clean_worktree=False)

    behavior = _read_json(tmp_path / "behavior_causal_replay_report.json")
    candidate = _read_json(tmp_path / "candidate_action_replay_report.json")
    snapshots = _read_jsonl(tmp_path / "serialized_state_snapshots.jsonl")
    observations = _read_jsonl(tmp_path / "observation_seed_manifest.json")
    observation_by_episode = {row["episode_id"]: row["observation"] for row in observations}

    assert behavior["behavior_causal_replay_passed"] is True
    assert behavior["hash_only_replay"] is False
    assert behavior["recomputed_from_serialized_state_and_observation"] is True
    assert candidate["candidate_action_replay_passed"] is True
    assert candidate["deserializer_function"].endswith("deserialize_state")
    assert candidate["candidate_action_function"].endswith("candidate_action_from_serialized_state")

    first = snapshots[0]
    recomputed = core.candidate_action_from_serialized_state(
        first["serialized_state"],
        observation_by_episode[first["episode_id"]],
    )
    assert recomputed == first["candidate_action_id"]


def test_failure_paths_emit_specific_blocker_verdicts():
    core, _runner = _modules()

    assert core.evaluate_computed_evidence_gate(
        metric_rows=[],
        baseline_invocations=[],
        ablation_invocations=[],
        leakage_invocations=[],
        replay_report={"behavior_causal_replay_passed": True, "hash_only_replay": False},
        consumption_report={"unused_frozen_inputs": []},
    )["verdict"] == "post_bridge_admission_executable_001c_failed_missing_metric_provenance"

    assert core.evaluate_computed_evidence_gate(
        metric_rows=[{"metric_id": "m", "computed_not_literal": False}],
        baseline_invocations=[{"baseline_name": name, "invoked": True, "computed_from_outputs": True} for name in core.REQUIRED_BASELINES],
        ablation_invocations=[{"ablation_name": name, "invoked": True, "reran_candidate_behavior": True} for name in core.REQUIRED_ABLATIONS],
        leakage_invocations=[
            {
                "scanner_name": name,
                "positive_control": {"detected": True},
                "real_scan": {"detected": False},
            }
            for name in core.REQUIRED_LEAKAGE_SCANNERS
        ],
        replay_report={"behavior_causal_replay_passed": True, "hash_only_replay": False},
        consumption_report={"unused_frozen_inputs": []},
    )["verdict"] == "post_bridge_admission_executable_001c_failed_literal_metric_detected"

    assert core.evaluate_computed_evidence_gate(
        metric_rows=[{"metric_id": "m", "computed_not_literal": True}],
        baseline_invocations=[],
        ablation_invocations=[{"ablation_name": name, "invoked": True, "reran_candidate_behavior": True} for name in core.REQUIRED_ABLATIONS],
        leakage_invocations=[
            {
                "scanner_name": name,
                "positive_control": {"detected": True},
                "real_scan": {"detected": False},
            }
            for name in core.REQUIRED_LEAKAGE_SCANNERS
        ],
        replay_report={"behavior_causal_replay_passed": True, "hash_only_replay": False},
        consumption_report={"unused_frozen_inputs": []},
    )["verdict"] == "post_bridge_admission_executable_001c_failed_baseline_invocation_missing"

    assert core.evaluate_computed_evidence_gate(
        metric_rows=[{"metric_id": "m", "computed_not_literal": True}],
        baseline_invocations=[{"baseline_name": name, "invoked": True, "computed_from_outputs": True} for name in core.REQUIRED_BASELINES],
        ablation_invocations=[{"ablation_name": name, "invoked": True, "reran_candidate_behavior": True} for name in core.REQUIRED_ABLATIONS],
        leakage_invocations=[
            {
                "scanner_name": name,
                "positive_control": {"detected": True},
                "real_scan": {"detected": False},
            }
            for name in core.REQUIRED_LEAKAGE_SCANNERS
        ],
        replay_report={"behavior_causal_replay_passed": False, "hash_only_replay": True},
        consumption_report={"unused_frozen_inputs": []},
    )["verdict"] == "post_bridge_admission_executable_001c_failed_replay_not_behavior_causal"
