import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gate3_viability_functional_affect_001b.runner import run_preflight_001b  # noqa: E402


TASK_ID = "GATE3-VIABILITY-FUNCTIONAL-AFFECT-EXECUTABLE-PREFLIGHT-001B"
VERDICT = "gate3_viability_functional_affect_001b_bounded_preflight_pass"
CLAIM_CEILING = "bounded Gate3 viability / functional-affect executable preflight evidence only"
ARTIFACT_DIR = ROOT / "artifacts" / "gate3_viability_functional_affect_001b"
TASK_CARD = (
    ROOT
    / "docs"
    / "codex"
    / "tasks"
    / "GATE3-VIABILITY-FUNCTIONAL-AFFECT-EXECUTABLE-PREFLIGHT-001B.md"
)
PARENT_TASK_CARD = (
    ROOT
    / "docs"
    / "codex"
    / "tasks"
    / "GATE3-VIABILITY-FUNCTIONAL-AFFECT-TASK-CARD-001A.md"
)

REQUIRED_ARTIFACTS = {
    "stage0_freeze_manifest.json",
    "execution_manifest.json",
    "execution_manifest.sha256",
    "run_ledger.jsonl",
    "trace.jsonl",
    "shared_state_trace.jsonl",
    "viability_state_trace.jsonl",
    "linkage_report.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_report.json",
    "replay_integrity_report.json",
    "mutation_check_report.json",
    "result.json",
    "claim_ceiling.txt",
}

REQUIRED_LOOP = [
    "observe",
    "predict_outcome",
    "select_action",
    "apply_action",
    "observe_effect",
    "compute_prediction_error",
    "update_belief_state",
    "replay_or_consolidate",
    "update_self_boundary_state",
    "predict_viability_delta",
    "observe_viability_delta",
    "compute_viability_error",
    "update_viability_state",
    "update_action_priority",
    "select_later_action",
    "emit_hash_chained_trace",
]

REQUIRED_STATE_FIELDS = {
    "belief_state",
    "prediction_error_state",
    "replay_memory",
    "consolidation_state",
    "controllability_model",
    "self_boundary_state",
    "viability_state",
    "viability_model",
    "action_priority_state",
    "recovery_policy_state",
    "resource_budget_state",
}

REQUIRED_BASELINES = {
    "reward-table lookup",
    "threshold-reflex policy",
    "hardcoded avoider / recovery rule",
    "frozen-viability model",
    "retrieval / summary retrieval",
    "count/statistic table",
    "transition table / successor map / graph cache",
    "behavior-only imitation",
    "isolated Gate0/Gate1/Gate2 policy without viability state",
    "stitched-output baseline with no shared viability state",
    "random policy",
    "oracle viability-label control as upper-bound/leakage only",
    "trace-only replay as hygiene only",
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
    "remove viability state",
    "freeze viability state",
    "invert viability signal",
    "remove viability feedback",
    "delay viability effect",
    "perturb resource budget",
    "perturb external threat / damage-like channel",
    "perturb recovery channel",
    "history replacement",
    "learning freeze",
    "disable action",
    "remove Gate2 self-boundary input to viability update",
    "remove Gate1 replay input to viability update",
    "heldout action-object-viability compositions",
    "counterfactual action contrast",
}

REQUIRED_TRACE_FIELDS = {
    "gate3_run_id",
    "episode_id",
    "step_id",
    "observation_hash",
    "action_id",
    "predicted_outcome",
    "observed_outcome",
    "prediction_error",
    "belief_state_before",
    "belief_state_after",
    "replay_event_id",
    "consolidation_event_id",
    "controllability_error",
    "self_boundary_state_before",
    "self_boundary_state_after",
    "predicted_viability_delta",
    "observed_viability_delta",
    "viability_error",
    "viability_state_before",
    "viability_state_after",
    "action_priority_before",
    "action_priority_after",
    "recovery_policy_state",
    "later_action_eval_id",
    "gate0_to_gate1_linkage_key",
    "gate1_to_gate2_linkage_key",
    "gate2_to_gate3_linkage_key",
    "gate3_to_later_action_linkage_key",
    "shared_state_hash_before_step",
    "shared_state_hash_after_step",
    "previous_trace_hash",
    "current_trace_hash",
    "access_log",
    "mutation_check_after_eval",
}

FORBIDDEN_CLAIMS = {
    "real emotion",
    "subjective experience",
    "pleasure",
    "pain",
    "agency",
    "selfhood",
    "consciousness",
    "real autonomy",
    "mechanism validity",
    "theory validity",
    "bridge readiness",
    "ego readiness",
    "companion readiness",
    "stable user benefit",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _canonical_sha(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _trace_hash(row: dict) -> str:
    row_without_hash = dict(row)
    row_without_hash.pop("current_trace_hash")
    return _canonical_sha(row_without_hash)


def test_001b_run_emits_required_artifacts_under_correct_path(tmp_path):
    assert TASK_CARD.exists()
    assert PARENT_TASK_CARD.exists()

    result = run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == VERDICT
    assert result["bounded_pass"] is True
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["artifact_dir"] == "artifacts/gate3_viability_functional_affect_001b"
    assert all(value is False for value in result["authorization_flags"].values())
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    assert (tmp_path / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING
    assert not (tmp_path / "failure_manifest.json").exists()


def test_stage0_freeze_manifest_anchors_parent_commits_and_contract(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    stage0 = _read_json(tmp_path / "stage0_freeze_manifest.json")
    execution_manifest = _read_json(tmp_path / "execution_manifest.json")

    assert stage0["task_id"] == TASK_ID
    assert stage0["stage0_frozen_before_candidate_or_control_runs"] is True
    assert stage0["candidate_or_control_runs_started_before_stage0"] is False
    assert stage0["parent_anchors"] == {
        "gate0_frozen_bounded_predictive_action_evidence": "PREDICTIVE-ACTION-LEARNING-CONTRACT-001C",
        "gate1_replay_consolidation_executable_preflight_commit": "6b362e0",
        "gate2_controllability_self_boundary_executable_preflight_commit": "7046d6f",
        "canonical_micro_agent_testbed_executable_preflight_commit": "1b23e46",
        "gate3_task_card_commit": "19f65b4",
    }
    assert stage0["required_loop"] == REQUIRED_LOOP
    assert set(stage0["required_shared_state_fields"]) == REQUIRED_STATE_FIELDS
    assert set(stage0["required_baselines"]) == REQUIRED_BASELINES
    assert set(stage0["required_ablations"]) == REQUIRED_ABLATIONS
    assert "viability" in stage0["shared_state_schema_id"]
    assert stage0["predeclared_viability_to_priority_link_required"] is True
    assert "001a" not in stage0["artifact_dir"].lower()
    assert (
        _file_sha(tmp_path / "execution_manifest.json")
        == (tmp_path / "execution_manifest.sha256").read_text(encoding="utf-8").strip()
    )
    assert execution_manifest["freeze_manifest_hash"] == _file_sha(
        tmp_path / "stage0_freeze_manifest.json"
    )


def test_trace_rows_have_required_gate3_fields_and_hash_chain(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    rows = _read_jsonl(tmp_path / "trace.jsonl")
    assert len(rows) >= 8
    assert rows[0]["previous_trace_hash"] == "GENESIS"
    assert len({row["shared_state_schema_id"] for row in rows}) == 1
    assert len({row["gate3_run_id"] for row in rows}) == 1

    for row in rows:
        assert REQUIRED_TRACE_FIELDS.issubset(row)
        assert row["loop_steps"] == REQUIRED_LOOP
        assert row["current_trace_hash"] == _trace_hash(row)
        assert row["shared_state_hash_before_step"]
        assert row["shared_state_hash_after_step"]
        assert row["shared_state_hash_before_step"] != row["shared_state_hash_after_step"]
        assert row["viability_state_before"] != row["viability_state_after"]
        assert row["action_priority_before"] != row["action_priority_after"]
        assert row["viability_error"] >= 0
        assert row["later_action_depends_on_action_priority_after"] is True
        assert row["access_log"]["forbidden_access_used"] is False
        assert row["access_log"]["oracle_viability_label_available_to_candidate"] is False
        assert row["mutation_check_after_eval"]["post_eval_mutation_detected"] is False

    for previous, current in zip(rows, rows[1:]):
        assert current["previous_trace_hash"] == previous["current_trace_hash"]


def test_shared_and_viability_state_traces_preserve_single_schema_and_priority_effect(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    shared_rows = _read_jsonl(tmp_path / "shared_state_trace.jsonl")
    viability_rows = _read_jsonl(tmp_path / "viability_state_trace.jsonl")
    assert len(shared_rows) >= 8
    assert len(shared_rows) == len(viability_rows)
    assert {row["shared_state_schema_id"] for row in shared_rows} == {
        "canonical_gate3_viability_functional_affect_shared_state_v1"
    }

    for row in shared_rows:
        assert REQUIRED_STATE_FIELDS.issubset(row["shared_state_before"])
        assert REQUIRED_STATE_FIELDS.issubset(row["shared_state_after"])
        assert row["shared_state_hash_before_step"] == _canonical_sha(row["shared_state_before"])
        assert row["shared_state_hash_after_step"] == _canonical_sha(row["shared_state_after"])
        assert row["uses_single_canonical_shared_state_object"] is True
        assert row["hidden_second_state_detected"] is False
        assert row["gate3_viability_update_applied"] is True
        assert row["action_priority_effect_applied"] is True

    for row in viability_rows:
        assert row["viability_state_before"] != row["viability_state_after"]
        assert row["action_priority_before"] != row["action_priority_after"]
        assert row["gate3_to_later_action_linkage_key"]
        assert row["viability_error_to_priority_update_linked"] is True


def test_linkage_keys_are_deterministic_label_free_collision_free_and_gate3_linked(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    trace_rows = _read_jsonl(tmp_path / "trace.jsonl")
    report = _read_json(tmp_path / "linkage_report.json")
    all_keys = []
    for row in trace_rows:
        all_keys.extend(
            [
                row["gate0_to_gate1_linkage_key"],
                row["gate1_to_gate2_linkage_key"],
                row["gate2_to_gate3_linkage_key"],
                row["gate3_to_later_action_linkage_key"],
            ]
        )

    assert report["deterministic"] is True
    assert report["label_free"] is True
    assert report["collision_free"] is True
    assert report["collision_count"] == 0
    assert report["gate2_to_gate3_linkage_present"] is True
    assert report["gate3_to_later_action_linkage_present"] is True
    assert report["viability_error_to_action_priority_link_predeclared"] is True
    assert len(all_keys) == len(set(all_keys))
    assert set(report["linkage_keys"]) == set(all_keys)
    serialized_inputs = json.dumps(report["linkage_derivation_inputs"]).lower()
    for forbidden in report["forbidden_label_tokens"]:
        assert forbidden not in serialized_inputs


def test_baseline_comparison_includes_required_families_and_excludes_oracle_controls(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    report = _read_json(tmp_path / "baseline_comparison.json")
    baselines = {row["baseline_name"]: row for row in report["baselines"]}

    assert set(baselines) == REQUIRED_BASELINES
    assert set(report["graph_cache_family_variants"]) == REQUIRED_GRAPH_CACHE_VARIANTS
    assert report["candidate"]["viability_to_later_action_score"] == 1.0
    assert report["candidate"]["viability_error_to_priority_linked"] is True
    assert report["acceptance_threshold"] == 0.95
    assert report["baseline_gate_passed"] is True
    assert report["best_fair_baseline"]["viability_to_later_action_score"] < report["acceptance_threshold"]
    assert baselines["reward-table lookup"]["same_visible_features_as_candidate"] is True
    assert baselines["threshold-reflex policy"]["same_visible_features_as_candidate"] is True
    assert baselines["hardcoded avoider / recovery rule"]["obvious_heuristic_family_allowed"] is True
    assert baselines["oracle viability-label control as upper-bound/leakage only"][
        "counts_as_fair_baseline"
    ] is False
    assert baselines["trace-only replay as hygiene only"]["counts_as_fair_baseline"] is False
    assert baselines["stitched-output baseline with no shared viability state"][
        "uses_single_canonical_shared_state"
    ] is False
    assert report["stitched_output_baseline_does_not_explain_result"] is True


def test_required_ablations_are_all_sensitive(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    report = _read_json(tmp_path / "ablation_report.json")
    ablations = {row["ablation_name"]: row for row in report["ablations"]}

    assert set(ablations) == REQUIRED_ABLATIONS
    assert report["ablation_gate_passed"] is True
    assert all(row["sensitive"] for row in ablations.values())
    assert all(row["viability_to_later_action_score"] < report["candidate_score"] for row in ablations.values())
    assert ablations["remove viability state"]["action_priority_effect_removed"] is True
    assert ablations["freeze viability state"]["action_priority_effect_removed"] is True
    assert ablations["remove Gate2 self-boundary input to viability update"]["sensitive"] is True
    assert ablations["remove Gate1 replay input to viability update"]["sensitive"] is True


def test_leakage_replay_and_mutation_reports_pass(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    leakage = _read_json(tmp_path / "leakage_report.json")
    replay = _read_json(tmp_path / "replay_integrity_report.json")
    mutation = _read_json(tmp_path / "mutation_check_report.json")

    assert leakage["leakage_gate_passed"] is True
    assert leakage["forbidden_access_detected"] is False
    assert leakage["oracle_viability_labels_available_to_candidate"] is False
    assert leakage["linkage_keys_label_free"] is True
    assert leakage["artifact_path_leakage_detected"] is False
    assert replay["replay_integrity_passed"] is True
    assert replay["trace_hash_chain_replayed"] is True
    assert replay["shared_state_hash_chain_replayed"] is True
    assert replay["viability_state_trace_replayed"] is True
    assert replay["single_shared_state_schema_preserved"] is True
    assert mutation["post_evaluation_mutation_check_passed"] is True
    assert mutation["mutation_detected_after_evaluation"] is False
    assert mutation["mutated_artifacts"] == []


def test_result_preserves_claim_ceiling_and_anti_sycophancy_audit(tmp_path):
    run_preflight_001b(repo_root=ROOT, output_dir=tmp_path)

    result = _read_json(tmp_path / "result.json")
    audit = result["anti_sycophancy_audit"]

    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["verdict"] == VERDICT
    assert result["layer"] == "bounded Gate3 viability / functional-affect executable preflight only"
    assert result["viability_to_action_priority_gate_passed"] is True
    assert result["forbidden_claims_absent"] is True
    assert result["stop_conditions_triggered"] == []
    assert audit["strongest_baseline_explanation"]
    assert audit["strongest_reason_task_may_be_invalid"]
    assert audit["result_that_would_falsify_current_framing"]
    assert audit["evidence_that_would_still_be_insufficient"]
    assert audit["tests_mechanism_or_behavioral_resemblance"] == (
        "bounded viability / functional-affect proxy behavior with trace/replay/"
        "intervention sensitivity, not real emotion or mechanism validity"
    )
    serialized = json.dumps(result).lower()
    for forbidden in FORBIDDEN_CLAIMS:
        assert f"proves {forbidden}" not in serialized


def test_default_run_writes_committed_artifact_directory():
    result = run_preflight_001b(repo_root=ROOT)

    assert result["artifact_dir"] == "artifacts/gate3_viability_functional_affect_001b"
    assert ARTIFACT_DIR.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    assert _read_json(ARTIFACT_DIR / "result.json")["verdict"] == VERDICT
