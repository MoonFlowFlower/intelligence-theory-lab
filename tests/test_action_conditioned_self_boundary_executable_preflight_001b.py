import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "ACTION-CONDITIONED-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001B-LEARNED-BASELINE-SCALING-CHALLENGE"
TASK_SLUG = "action_conditioned_self_boundary_executable_preflight_001b"
ARTIFACT_DIR = ROOT / "artifacts" / TASK_SLUG
REPORT_PATH = ROOT / "docs" / "research" / f"{TASK_ID}.md"

REQUIRED_PROBES = {
    "small_reproduction",
    "combinatorial_heldout",
    "noisy_decoy_intervention",
}

REQUIRED_LEARNED_BASELINES = {
    "learned_feature_mlp_without_boundary_state",
    "sequence_model_without_boundary_update",
    "embedding_knn_or_episodic_retrieval_baseline",
}

REQUIRED_FINITE_BASELINES = {
    "transition_table_baseline",
    "fsm_baseline",
    "graph_cache_episodic_traversal_baseline",
    "action_effect_frequency_without_boundary_state_baseline",
    "recency_or_last_effect_baseline",
    "majority_baseline",
    "random_baseline",
}

REQUIRED_NON_ORACLE_BASELINES = REQUIRED_FINITE_BASELINES | REQUIRED_LEARNED_BASELINES | {
    "capacity_matched_boundary_disabled_reference",
}

REQUIRED_ABLATIONS = {
    "freeze_boundary_update",
    "remove_action_conditioned_contingency",
    "remove_no_action_counterfactual",
    "shuffle_action_effect_linkage",
    "replace_boundary_state_with_recency_state",
    "reset_state_before_probe",
}

REQUIRED_ARTIFACTS = {
    "result.json",
    "summary.md",
    "episodes.json",
    "trace.jsonl",
    "scores.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "leakage_scan.json",
    "replay_report.json",
    "provenance.json",
    "failure_manifest.json",
    "claim_ceiling.txt",
    "git_readback.json",
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
    "baseline_path_name",
    "ablation_path_name",
    "leakage_scanner_path",
    "replay_path",
    "source_001a_runner_hash",
    "source_001a_result_hash",
}


def _runner():
    return importlib.import_module(
        "action_conditioned_self_boundary_executable_preflight_001a.learned_scaling_001b"
    )


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _walk_keys(value, prefix=""):
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            yield path
            yield from _walk_keys(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_keys(child, f"{prefix}[{index}]")


def test_config_and_scaling_probe_generation_preserve_001b_bounds():
    runner = _runner()

    config = runner.build_challenge_config()
    episodes_by_probe = runner.generate_scaling_probe_episodes(config)

    assert config["task_card_id"] == TASK_ID
    assert config["mainline_integration_target"] == "none"
    assert config["auto_remote_anchor"] == "conditional"
    assert config["claim_ceiling"] == "offline learned-baseline/scaling challenge evidence only"
    assert config["source_001a"]["runner_sha256"]
    assert config["source_001a"]["result_sha256"]
    assert config["canonical_001a_boundary"]["commit"] == "4b7a5b467e1c56b392766e4fc60f75129c9e1842"
    assert config["thresholds"]["reference_margin_over_strongest_non_oracle_baseline_min"] == 0.15
    assert config["thresholds"]["capacity_disabled_degradation_min"] == 0.20
    assert set(config["probe_settings"]) == REQUIRED_PROBES
    assert set(episodes_by_probe) == REQUIRED_PROBES

    for probe_name, episodes in episodes_by_probe.items():
        assert len(episodes) >= 16
        train_contexts = {episode["train_context_id"] for episode in episodes}
        heldout_contexts = {episode["heldout_probe_context_id"] for episode in episodes}
        assert train_contexts.isdisjoint(heldout_contexts)
        assert all(episode["probe_setting"] == probe_name for episode in episodes)
        if probe_name == "combinatorial_heldout":
            assert all(episode["row_enumerable_from_training"] is False for episode in episodes)

        for episode in episodes:
            legal = runner.legal_input_for_episode_001b(episode)
            legal_keys = {path.split(".")[-1] for path in _walk_keys(legal)}
            assert legal_keys.isdisjoint(runner.FORBIDDEN_LEGAL_KEYS)
            assert "target_channel" not in json.dumps(legal, sort_keys=True)
            assert "expected_measurable_object" not in legal


def test_learned_baselines_scaling_and_capacity_challenge_are_callable_and_failably_scored():
    runner = _runner()

    run = runner.execute_challenge(persist_artifacts=False)
    result = run["result"]
    scores = run["scores"]
    baselines = run["baseline_comparison"]

    assert result["verdict"] in runner.ALLOWED_VERDICTS
    assert result["verdict"] == (
        "action_conditioned_self_boundary_executable_preflight_001b_survives_learned_baseline_scaling_challenge"
    )
    assert result["current_layer"] == "engineering implementation / offline executable learned-baseline and scaling challenge only"
    assert result["mainline_integration_status"] == "none"
    assert result["enabled_status"] == "local offline module, tests, and artifact generation only"
    assert result["real_trigger_evidence"] == "callable local 001B execution produced artifacts"
    assert result["claim_ceiling"] == "offline learned-baseline/scaling challenge evidence only"
    assert result["mechanism_validity_claimed"] is False
    assert result["gate_bridge_runtime_or_ego_mainline_enabled"] is False

    assert set(baselines["invoked_learned_no_boundary_baselines"]) == REQUIRED_LEARNED_BASELINES
    assert set(baselines["invoked_finite_baselines"]) == REQUIRED_FINITE_BASELINES
    assert set(baselines["invoked_non_oracle_baselines"]) == REQUIRED_NON_ORACLE_BASELINES
    assert baselines["missing_learned_no_boundary_baselines"] == []
    assert baselines["missing_finite_baselines"] == []
    assert baselines["missing_non_oracle_baselines"] == []

    for probe_name in REQUIRED_PROBES:
        probe_scores = scores["by_probe_setting"][probe_name]
        reference_score = probe_scores["reference_path"]["score"]
        strongest_finite = probe_scores["strongest_finite_baseline"]
        strongest_non_oracle = probe_scores["strongest_non_oracle_baseline"]
        strongest_learned = probe_scores["strongest_learned_no_boundary_baseline"]
        capacity_score = probe_scores["baseline_scores"]["capacity_matched_boundary_disabled_reference"]["score"]

        assert reference_score == 1.0
        assert strongest_finite["baseline_name"] in REQUIRED_FINITE_BASELINES
        assert reference_score - strongest_finite["score"] >= 0.15
        assert reference_score - strongest_non_oracle["score"] >= 0.15
        assert strongest_learned["score"] < reference_score
        assert reference_score - capacity_score >= 0.20

        for baseline_name in REQUIRED_NON_ORACLE_BASELINES:
            record = probe_scores["baseline_scores"][baseline_name]
            assert record["producer_function"] == baseline_name
            assert record["score_source"] == "callable_computation"
            assert record["maintains_explicit_boundary_update"] is False


def test_ablations_leakage_replay_and_provenance_are_computed_not_report_shaped():
    runner = _runner()

    run = runner.execute_challenge(persist_artifacts=False)
    scores = run["scores"]
    ablations = run["ablation_report"]
    leakage = run["leakage_scan"]
    replay = run["replay_report"]
    provenance = run["provenance"]
    verification = runner.verify_computed_evidence_provenance_001b(provenance)

    assert set(ablations["invoked_ablations"]) == REQUIRED_ABLATIONS
    assert ablations["missing_ablations"] == []
    for probe_name in REQUIRED_PROBES:
        reference_score = scores["by_probe_setting"][probe_name]["reference_path"]["score"]
        for ablation_name in REQUIRED_ABLATIONS:
            record = ablations["by_probe_setting"][probe_name]["ablation_scores"][ablation_name]
            assert record["producer_function"] == ablation_name
            assert record["reran_behavior"] is True
            assert record["degradation_from_reference"] == round(reference_score - record["score"], 6)
        for core_ablation in (
            "freeze_boundary_update",
            "remove_action_conditioned_contingency",
            "shuffle_action_effect_linkage",
            "reset_state_before_probe",
        ):
            assert (
                ablations["by_probe_setting"][probe_name]["ablation_scores"][core_ablation][
                    "degradation_from_reference"
                ]
                >= 0.20
            )

    assert leakage["producer_function"] == "run_leakage_scan_001b"
    assert leakage["normal_legal_input"]["blocked"] is False
    assert leakage["positive_controls_blocked"] == leakage["positive_controls_total"] == 6
    assert leakage["learned_contaminated_positive_control"]["score"] == 1.0
    assert leakage["learned_contaminated_positive_control"]["exploited_contamination"] is True
    assert leakage["clean_legal_input_excludes_contaminated_fields"] is True

    blocked = runner.execute_challenge(
        persist_artifacts=False,
        disable_leakage_positive_controls=True,
    )
    assert blocked["result"]["verdict"] == "blocked_by_leakage_positive_control_failure_001b"
    assert "leakage_positive_control_failure" in blocked["result"]["stop_conditions_triggered"]

    assert replay["producer_function"] == "run_replay_001b"
    assert replay["passed"] is True
    assert replay["uses_stored_hashes_only"] is False
    assert replay["uses_stored_verdicts"] is False
    assert replay["exact_recomputation_passed"] is True
    assert replay["observation_mutation_changed_behavior"] is True
    assert replay["metadata_mutation_preserved_behavior"] is True
    assert replay["missing_required_legal_input_failed"] is True
    assert {
        "boundary_update_reference_path",
        *REQUIRED_LEARNED_BASELINES,
        "capacity_matched_boundary_disabled_reference",
        *REQUIRED_ABLATIONS,
    }.issubset(set(replay["recomputed_paths"]))

    assert verification["passed"] is True
    assert verification["static_score_records_detected"] == []
    assert verification["report_shaped_records_detected"] == []
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
    assert runner.verify_computed_evidence_provenance_001b(static)["passed"] is False


def test_artifacts_report_claim_scan_and_allowlist_are_written_and_parse(tmp_path):
    runner = _runner()

    run = runner.execute_challenge(output_dir=tmp_path, persist_artifacts=True)
    report_path = runner.write_research_report_001b(run, report_path=tmp_path / "report.md")

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in tmp_path.iterdir()})
    for name in REQUIRED_ARTIFACTS - {"summary.md", "claim_ceiling.txt", "trace.jsonl"}:
        _read_json(tmp_path / name)

    trace_lines = (tmp_path / "trace.jsonl").read_text(encoding="utf-8").splitlines()
    assert trace_lines
    for line in trace_lines:
        json.loads(line)

    result = _read_json(tmp_path / "result.json")
    git_readback = _read_json(tmp_path / "git_readback.json")
    assert result["forbidden_positive_claim_scan"]["passed"] is True
    assert result["changed_file_allowlist"]["passed"] is True
    assert git_readback["source_001a"]["runner_sha256"] == run["config"]["source_001a"]["runner_sha256"]
    assert git_readback["source_001a"]["result_sha256"] == run["config"]["source_001a"]["result_sha256"]
    assert isinstance(git_readback["diff_name_status"], list)
    assert git_readback["worktree_status_at_artifact_generation"] in {"clean", "dirty"}

    report_text = report_path.read_text(encoding="utf-8")
    assert "Auto-Remote-Anchor: conditional" in report_text
    assert "No mechanism validity is claimed." in report_text
    assert "No Gate4, Gate5, bridge, runtime, tournament, companion, product, or EGO-mainline path is enabled." in report_text
    assert "learned_feature_mlp_without_boundary_state" in report_text
