import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "action_conditioned_self_boundary_executable_preflight_001a"
TASK_CARD_ID = "ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001A"
ARTIFACT_DIR = ROOT / "artifacts" / TASK_ID
REPORT_PATH = ROOT / "docs" / "research" / f"{TASK_CARD_ID}.md"

REQUIRED_ARTIFACTS = {
    "result.json",
    "summary.md",
    "episodes.json",
    "scores.json",
    "baselines.json",
    "ablations.json",
    "leakage_scan.json",
    "replay.json",
    "provenance.json",
    "claim_ceiling.txt",
    "git_readback.json",
}

REQUIRED_BASELINES = {
    "transition_table_baseline",
    "fsm_baseline",
    "graph_cache_episodic_traversal_baseline",
    "action_effect_frequency_without_boundary_state_baseline",
    "recency_or_last_effect_baseline",
    "majority_baseline",
    "random_baseline",
    "oracle_leakage_positive_control_baseline",
}

REQUIRED_ABLATIONS = {
    "freeze_boundary_update",
    "remove_action_conditioned_contingency",
    "remove_no_action_counterfactual",
    "shuffle_action_effect_linkage",
    "replace_boundary_state_with_recency_state",
    "reset_state_before_probe",
}

FORBIDDEN_LEGAL_KEYS = {
    "target_action",
    "target_output",
    "oracle_boundary_label",
    "legal_answer",
    "answer_alias",
    "hidden_answer_id",
    "future_outcome",
    "evaluator_only",
    "precomputed_verdict",
    "precomputed_score",
    "pass_fail",
    "manifest_completeness",
    "validator_cleanliness",
    "expected_measurable_object",
}

PROVENANCE_FIELDS = {
    "producer_function",
    "input_hash",
    "run_id",
    "seed",
    "context_ids",
    "episode_ids",
    "aggregation_rule",
    "code_path_hash",
    "reference_path_name",
    "leakage_scanner_path",
    "replay_path",
    "source_artifact_hash",
}


def _runner():
    return importlib.import_module(f"{TASK_ID}.runner")


def _walk_keys(value, prefix=""):
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            yield path
            yield from _walk_keys(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_keys(child, f"{prefix}[{index}]")


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_episode_generation_is_deterministic_and_legal_inputs_exclude_forbidden_fields():
    runner = _runner()

    config = runner.build_preflight_config()
    first = runner.generate_episodes(config)
    second = runner.generate_episodes(config)

    assert config["task_card_id"] == TASK_CARD_ID
    assert config["mainline_integration_target"] == "none"
    assert config["auto_remote_anchor"] == "conditional"
    assert first == second
    assert len(first) >= 24

    for episode in first:
        legal = runner.legal_input_for_episode(episode)
        legal_key_suffixes = {path.split(".")[-1] for path in _walk_keys(legal)}
        assert legal_key_suffixes.isdisjoint(FORBIDDEN_LEGAL_KEYS)
        assert '"target_channel"' not in json.dumps(legal, sort_keys=True)
        assert "expected_measurable_object" not in legal
        assert episode["train_context_id"] != episode["heldout_probe_context_id"]
        assert episode["serialized_prior_boundary_state"]["update_rate"] == 1.0
        assert episode["forbidden_fields_excluded_from_reference_and_baselines"] == sorted(
            FORBIDDEN_LEGAL_KEYS
        )


def test_reference_baselines_and_ablations_execute_with_failability_margins():
    runner = _runner()

    run = runner.execute_preflight(persist_artifacts=False)
    result = run["result"]
    scores = run["scores"]
    baselines = run["baselines"]
    ablations = run["ablations"]

    assert result["verdict"] == "action_conditioned_self_boundary_executable_preflight_001a_surface_discriminative"
    assert result["current_layer"] == "engineering implementation / offline executable preflight only"
    assert result["mainline_integration_status"] == "none"
    assert result["enabled_status"] == "local module entrypoint, local pytest tests, local artifact generation only"
    assert result["real_trigger_evidence"] == "callable local execution produced artifacts"
    assert result["claim_ceiling"] == "offline executable surface-preflight evidence only"
    assert result["mechanism_validity_claimed"] is False
    assert result["gate_bridge_runtime_or_ego_mainline_enabled"] is False
    assert result["stop_conditions_triggered"] == []

    assert scores["reference_path"]["score"] == 1.0
    assert scores["strongest_non_oracle_baseline"]["score"] <= 0.80
    assert (
        scores["reference_path"]["score"]
        - scores["strongest_non_oracle_baseline"]["score"]
        >= 0.20
    )
    assert scores["oracle_leakage_positive_control_baseline"]["score"] >= 0.95

    assert set(baselines["baseline_scores"]) == REQUIRED_BASELINES
    assert set(baselines["invoked_baselines"]) == REQUIRED_BASELINES
    assert baselines["missing_baselines"] == []
    for baseline_name in REQUIRED_BASELINES:
        assert baselines["baseline_scores"][baseline_name]["producer_function"] == baseline_name
    assert (
        baselines["baseline_scores"]["oracle_leakage_positive_control_baseline"]["received_answer_bearing_fields"]
        is True
    )

    assert set(ablations["ablation_scores"]) == REQUIRED_ABLATIONS
    for ablation_name in REQUIRED_ABLATIONS:
        record = ablations["ablation_scores"][ablation_name]
        assert record["producer_function"] == ablation_name
        assert record["reran_behavior"] is True
    for core_ablation in (
        "freeze_boundary_update",
        "remove_action_conditioned_contingency",
        "shuffle_action_effect_linkage",
        "reset_state_before_probe",
    ):
        assert ablations["ablation_scores"][core_ablation]["degradation_from_reference"] >= 0.20


def test_leakage_scanner_blocks_cleanly_and_positive_controls_are_required():
    runner = _runner()

    run = runner.execute_preflight(persist_artifacts=False)
    leakage = run["leakage_scan"]

    assert leakage["producer_function"] == "run_leakage_scan"
    assert leakage["normal_legal_input"]["blocked"] is False
    assert leakage["normal_legal_input"]["detected_paths"] == []
    assert leakage["positive_controls_blocked"] == 6
    assert leakage["positive_controls_total"] == 6
    assert {control["control_id"] for control in leakage["positive_controls"]} == {
        "explicit_target_action_output",
        "oracle_boundary_label",
        "benign_answer_alias",
        "hidden_id_answer_map",
        "future_outcome",
        "stored_verdict_score",
    }
    assert all(control["blocked"] for control in leakage["positive_controls"])

    blocked = runner.execute_preflight(
        persist_artifacts=False,
        disable_leakage_positive_controls=True,
    )
    assert blocked["result"]["verdict"] == "blocked_by_leakage_positive_control_failure_001a"
    assert "leakage_positive_control_failure" in blocked["result"]["stop_conditions_triggered"]


def test_replay_recomputes_from_state_observation_and_detects_meaningful_mutations():
    runner = _runner()

    run = runner.execute_preflight(persist_artifacts=False)
    replay = run["replay"]

    assert replay["producer_function"] == "run_replay"
    assert replay["passed"] is True
    assert replay["exact_recomputation_match"] is True
    assert replay["uses_stored_hashes_only"] is False
    assert replay["uses_stored_verdicts"] is False
    assert replay["state_mutation_changed_behavior"] is True
    assert replay["observation_mutation_changed_behavior"] is True
    assert replay["metadata_mutation_preserved_behavior"] is True
    assert replay["missing_required_legal_input_failed"] is True
    assert replay["recomputed_paths"] >= {
        "boundary_update_reference_path",
        "transition_table_baseline",
        "freeze_boundary_update",
    }


def test_provenance_covers_every_score_and_rejects_static_or_report_shaped_evidence():
    runner = _runner()

    run = runner.execute_preflight(persist_artifacts=False)
    provenance = run["provenance"]
    verification = runner.verify_computed_evidence_provenance(provenance)

    assert verification["passed"] is True
    assert verification["static_score_records_detected"] == []
    assert verification["report_shaped_records_detected"] == []
    score_names = {record["score_name"] for record in provenance["score_records"]}
    assert "reference_path" in score_names
    assert REQUIRED_BASELINES.issubset(score_names)
    assert REQUIRED_ABLATIONS.issubset(score_names)

    for record in provenance["score_records"]:
        assert PROVENANCE_FIELDS.issubset(record)
        assert record["score_source"] == "callable_computation"
        assert record["static_literal_score"] is False
        assert record["report_only_score"] is False
        assert record["manifest_completeness_score"] is False
        assert record["validator_cleanliness_score"] is False
        assert record["input_hash"]
        assert record["code_path_hash"]

    static = json.loads(json.dumps(provenance))
    static["score_records"][0]["score_source"] = "literal"
    static["score_records"][0]["static_literal_score"] = True
    assert runner.verify_computed_evidence_provenance(static)["passed"] is False


def test_artifacts_report_and_claim_scan_are_written_and_parse(tmp_path):
    runner = _runner()

    run = runner.execute_preflight(output_dir=tmp_path, persist_artifacts=True)
    report_path = runner.write_research_report(run, report_path=tmp_path / "report.md")

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    for name in REQUIRED_ARTIFACTS - {"summary.md", "claim_ceiling.txt"}:
        _read_json(tmp_path / name)

    result = _read_json(tmp_path / "result.json")
    git_readback = _read_json(tmp_path / "git_readback.json")
    assert result["forbidden_positive_claim_scan"]["passed"] is True
    assert result["changed_file_allowlist"]["passed"] is True
    assert git_readback["branch"] == "codex/meta-theory-scaffold"
    assert git_readback["session_start_readback"]["worktree_status"] == "clean"
    assert git_readback["worktree_status_at_artifact_generation"] in {"clean", "dirty"}
    assert git_readback["source_artifact_sha256"] == run["source_artifact_hash"]

    report_text = report_path.read_text(encoding="utf-8")
    assert "Auto-Remote-Anchor: conditional" in report_text
    assert "No mechanism validity is claimed." in report_text
    assert "No Gate4, Gate5, bridge, runtime, tournament, companion, product, or EGO-mainline path is enabled." in report_text
    assert "PRESERVE-ACTION-CONDITIONED-SELF-BOUNDARY-PREFLIGHT-001A-HOSTILE-AUDIT-001A" in report_text
