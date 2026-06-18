import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


REQUIRED_BASELINES = {
    "random",
    "majority",
    "observation_only",
    "lookup",
    "count_table",
    "transition_table",
    "graph_cache",
    "successor_map",
    "nearest_neighbor",
    "fsm_planner",
    "episodic_traversal",
    "trace_only_replay",
    "exhaustive_legal_query",
}

REQUIRED_ABLATIONS = {
    "memory_deletion",
    "latent_rule_swap",
    "heldout_task_family_transfer",
    "partial_observation_ablation",
    "exploration_budget_ablation",
    "cross_episode_reset",
    "source_memory_deletion",
    "spurious_token_injection_removal",
    "observation_field_masking",
}

REQUIRED_REPLAY_INPUTS = {
    "serialized_state",
    "current_observation",
    "legal_action_or_query_schema",
    "budget_state",
    "latent_belief_or_memory_state",
}

REQUIRED_ARTIFACTS = {
    "result.json",
    "trace.jsonl",
    "baseline_comparison.json",
    "ablation_report.json",
    "replay_report.json",
    "leakage_report.json",
    "failure_manifest.json",
}


def _runner():
    from phase2c_hidden_latent_harness_001a import runner

    return runner


def test_surface_generation_preserves_hidden_latent_and_heldout_boundaries():
    runner = _runner()

    surface = runner.generate_surface(seed=17, train_family_count=2, heldout_family_count=2, episodes_per_family=3)

    assert surface["producer_function"] == "phase2c_hidden_latent_harness_001a.runner.generate_surface"
    assert surface["run_id"] == runner.RUN_ID
    assert surface["train_seed_range"] and surface["heldout_seed_range"]
    assert set(surface["train_task_family_ids"]).isdisjoint(surface["heldout_task_family_ids"])
    assert len(surface["episodes"]) == 12
    assert {episode["split"] for episode in surface["episodes"]} == {"train", "heldout"}

    for episode in surface["episodes"]:
        visible = runner.candidate_visible_episode(episode)
        visible_text = json.dumps(visible, sort_keys=True).lower()
        assert episode["hidden_rule_id"].lower() not in visible_text
        assert episode["task_family_id"].lower() not in visible_text
        assert "hidden_rule" not in visible_text
        assert "target_action" not in visible_text
        assert "answer_map" not in visible_text
        assert "serialized_state" not in visible
        assert set(visible) == {
            "episode_id",
            "split",
            "current_observation",
            "legal_action_or_query_schema",
            "budget_state",
            "anonymous_family_bucket",
        }


def test_baseline_battery_records_required_callable_provenance():
    runner = _runner()
    surface = runner.generate_surface(seed=23, train_family_count=2, heldout_family_count=2, episodes_per_family=2)

    report = runner.run_baseline_battery(surface)

    assert set(report["baseline_ids"]) == REQUIRED_BASELINES
    assert report["missing_baseline_ids"] == []
    assert report["access_boundary"] == "candidate_visible_plus_budget_only"
    assert report["strongest_fair_is_max_over_full_battery"] is True
    assert all(row["callable_invoked"] is True for row in report["results"])
    for row in report["results"]:
        assert row["producer_function"].startswith("phase2c_hidden_latent_harness_001a.runner.")
        assert row["input_artifacts"] == ["generated_phase2c_hidden_latent_surface"]
        assert row["run_id"] == runner.RUN_ID
        assert row["seed_context_episode_ids"]
        assert row["aggregation_rule"] == "macro_accuracy_over_hidden_latent_final_actions"
        assert len(row["code_path_hash"]) == 64

    missing = runner.run_baseline_battery(surface, disabled_baselines=("graph_cache",))
    assert "graph_cache" in missing["missing_baseline_ids"]


def test_leakage_scan_uses_positive_controls_and_rejects_hidden_answer_fields():
    runner = _runner()
    surface = runner.generate_surface(seed=31, train_family_count=1, heldout_family_count=1, episodes_per_family=2)
    clean_payloads = [runner.candidate_visible_episode(episode) for episode in surface["episodes"]]

    report = runner.run_leakage_scan(clean_payloads)

    assert report["positive_controls_passed"] is True
    assert set(report["detected_positive_control_ids"]) == set(report["positive_control_ids"])
    assert report["clean_scan_passed_after_positive_controls"] is True
    assert report["illegal_leak_findings"] == []

    leaked = runner.run_leakage_scan(
        clean_payloads,
        extra_payloads=[{"candidate_visible": {"target_action": "action_0"}}],
    )
    assert leaked["clean_scan_passed_after_positive_controls"] is False
    assert any(finding["reason"] == "illegal_key_token" for finding in leaked["illegal_leak_findings"])


def test_replay_recomputes_from_required_inputs_and_fails_on_tamper_or_omission():
    runner = _runner()
    surface = runner.generate_surface(seed=41, train_family_count=1, heldout_family_count=1, episodes_per_family=2)
    episode = surface["episodes"][0]
    visible = runner.candidate_visible_episode(episode)
    replay_state = runner.serialized_replay_state(episode)
    memory_state = runner.initial_memory_state(episode)

    replay = runner.replay_recompute(
        serialized_state=replay_state,
        current_observation=visible["current_observation"],
        legal_action_or_query_schema=visible["legal_action_or_query_schema"],
        budget_state=visible["budget_state"],
        latent_belief_or_memory_state=memory_state,
    )

    assert replay["passed"] is True
    assert replay["prediction"] == runner.oracle_policy(episode)["action"]
    assert replay["observed_input_reads"] == {key: True for key in REQUIRED_REPLAY_INPUTS}
    assert replay["uses_hash_only_comparison"] is False
    assert replay["uses_stored_outputs_only"] is False

    for omitted in REQUIRED_REPLAY_INPUTS:
        omitted_report = runner.run_replay_check(surface, omit_input=omitted)
        assert omitted_report["passed"] is False
        assert f"missing_replay_input:{omitted}" in omitted_report["blocking_reasons"]

    tampered = runner.run_replay_check(surface, tamper_memory=True)
    assert tampered["passed"] is False
    assert "replay_tamper_negative_control_detected" in tampered["blocking_reasons"]


def test_ablation_contract_artifacts_and_provenance_are_frozen_without_execution(tmp_path):
    runner = _runner()
    surface = runner.generate_surface(seed=53, train_family_count=1, heldout_family_count=1, episodes_per_family=2)
    baseline_report = runner.run_baseline_battery(surface)
    leakage_report = runner.run_leakage_scan([runner.candidate_visible_episode(row) for row in surface["episodes"]])
    replay_report = runner.run_replay_check(surface)
    ablation_report = runner.build_ablation_plan(surface)

    assert {row["control_id"] for row in ablation_report["controls"]} == REQUIRED_ABLATIONS
    assert all(row["callable_invoked"] is True for row in ablation_report["controls"])
    assert all(row["detected_expected_failure"] is True for row in ablation_report["controls"])
    assert ablation_report["stored_score_mutation_used"] is False

    assert set(runner.DEFAULT_OUTPUT_FILES) == REQUIRED_ARTIFACTS
    assert runner.RUNNER_COMMAND == (
        "python -m phase2c_hidden_latent_harness_001a.runner "
        "--output-dir artifacts/phase2c_hidden_latent_harness_001a"
    )
    assert not (tmp_path / "artifacts").exists()

    provenance = runner.build_provenance(surface, baseline_report, leakage_report, replay_report, ablation_report)
    provenance_check = runner.verify_provenance(provenance)
    assert provenance_check["passed"] is True
    assert all(row["consumed_by_final_verdict"] is True for row in provenance["records"])

    missing = runner.verify_provenance({"records": provenance["records"][1:]})
    assert missing["passed"] is False
    assert "missing_required_provenance:surface_generation" in missing["blocking_reasons"]
