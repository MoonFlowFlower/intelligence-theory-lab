import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_passive_baseline_rejects_intervention_contamination():
    from route_c_preflight_001a import core

    config = core.default_config(n_passive=8, interventions_per_channel=2)
    episode = core.sample_episode(seed=1701, config=config)
    legal = core.legal_view_for_episode(episode, include_interventions=True)

    with pytest.raises(ValueError, match="obs_only_baseline_received_intervention_data"):
        core.obs_only_baseline([legal], run_id="pytest-contamination")


def test_clean_non_leaking_surface_has_chance_passive_attackers():
    from route_c_preflight_001a import core, leakage

    config = core.default_config(n_passive=24, interventions_per_channel=4)
    bundle = core.build_episode_bundle(seeds=range(100, 180), config=config, run_id="pytest-clean")
    panel = core.run_baseline_panel(bundle, run_id="pytest-clean-panel")
    gate = core.non_identifiability_premise_gate(panel, config=config)
    scan = leakage.scan_bundle_for_leakage(bundle)

    assert scan["verdict"] == "clean"
    assert gate["verdict"] == "non_identifiability_present"
    assert panel["obs_only"]["aggregate_score"]["value"] <= config.premise_threshold
    assert panel["schema_only"]["aggregate_score"]["value"] <= config.premise_threshold
    assert panel["name_order"]["aggregate_score"]["value"] <= config.premise_threshold


def test_schema_name_order_positive_controls_are_detected():
    from route_c_preflight_001a import core, leakage

    config = core.default_config(n_passive=12, interventions_per_channel=2)
    bundle = core.build_episode_bundle(seeds=range(30, 46), config=config, run_id="pytest-leak")
    l2 = leakage.inject_unpermuted_channel_ids(bundle)
    l3 = leakage.inject_action_label_alias(bundle)
    l7 = leakage.inject_schema_only_attack(bundle)

    assert "identity-not-permuted" in leakage.scan_bundle_for_leakage(l2)["detected_classes"]
    assert "action-label-alias" in leakage.scan_bundle_for_leakage(l3)["detected_classes"]
    assert "schema-only-positive-control" in leakage.scan_bundle_for_leakage(l7)["detected_classes"]


def test_hidden_self_set_injection_blocks_observation_decodable_surface():
    from route_c_preflight_001a import core, leakage

    config = core.default_config(n_passive=12, interventions_per_channel=2)
    clean = core.build_episode_bundle(seeds=range(200, 216), config=config, run_id="pytest-l1")
    injected = leakage.inject_hidden_self_set_as_legal_field(clean)
    panel = core.run_baseline_panel(injected, run_id="pytest-l1-panel")
    gate = core.non_identifiability_premise_gate(panel, config=config)
    scan = leakage.scan_bundle_for_leakage(injected)

    assert "self-set-in-legal" in scan["detected_classes"]
    assert gate["verdict"] == "blocked_by_observation_decodable_self_set"
    assert panel["obs_only"]["aggregate_score"]["value"] == pytest.approx(1.0)


def test_no_headroom_intervention_surface_blocks():
    from route_c_preflight_001a import core

    config = core.default_config(gain=0.0, n_passive=20, interventions_per_channel=8)
    bundle = core.build_episode_bundle(seeds=range(500, 532), config=config, run_id="pytest-no-headroom")
    panel = core.run_baseline_panel(bundle, run_id="pytest-no-headroom-panel")
    oracle = core.run_interventional_oracle(bundle, run_id="pytest-no-headroom-oracle")
    gate = core.interventional_headroom_gate(
        obs_score=panel["obs_only"]["aggregate_score"]["value"],
        oracle_score=oracle["aggregate_score"]["value"],
        config=config,
    )

    assert gate["verdict"] == "blocked_by_no_interventional_headroom"
    assert oracle["aggregate_score"]["value"] <= config.premise_threshold


def test_interventional_oracle_gets_headroom_only_from_randomized_interventions():
    from route_c_preflight_001a import core

    config = core.default_config(n_passive=32, interventions_per_channel=12)
    bundle = core.build_episode_bundle(seeds=range(800, 832), config=config, run_id="pytest-headroom")
    panel = core.run_baseline_panel(bundle, run_id="pytest-headroom-panel")
    oracle = core.run_interventional_oracle(bundle, run_id="pytest-headroom-oracle")
    gate = core.interventional_headroom_gate(
        obs_score=panel["obs_only"]["aggregate_score"]["value"],
        oracle_score=oracle["aggregate_score"]["value"],
        config=config,
    )

    assert oracle["used_randomized_interventions"] is True
    assert oracle["baseline_accessed_intervention_data"] is False
    assert gate["verdict"] == "interventional_headroom_present"
    assert gate["value"] > config.headroom_band


def test_all_leakage_controls_fire_and_clean_case_is_not_blocked():
    from route_c_preflight_001a import core, leakage

    config = core.default_config(n_passive=12, interventions_per_channel=4)
    bundle = core.build_episode_bundle(seeds=range(900, 916), config=config, run_id="pytest-controls")
    report = leakage.run_leakage_positive_controls(bundle=bundle, config=config, run_id="pytest-controls")

    assert report["clean_case"]["verdict"] == "clean"
    assert report["all_controls_fired"] is True
    assert set(report["control_results"]) == {"L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8"}
    assert all(row["fired"] is True for row in report["control_results"].values())


def test_malformed_provenance_blocks():
    from route_c_preflight_001a import provenance

    good = provenance.score_record(
        value=0.5,
        producer_function=provenance.score_record,
        inputs={"source": "pytest"},
        run_id="pytest-provenance",
        seed=1,
        episode_ids=["ep-1"],
        aggregation="unit_test",
        threshold_used=0.6,
    )
    malformed = dict(good)
    malformed.pop("code_path_hash")

    assert provenance.validate_provenance_rows([good])["verdict"] == "provenance_valid"
    assert provenance.validate_provenance_rows([malformed])["verdict"] == "blocked_by_provenance_gap"


def test_replay_recomputes_from_serialized_state_and_intervention_log():
    from route_c_preflight_001a import core, replay

    config = core.default_config(n_passive=16, interventions_per_channel=8)
    bundle = core.build_episode_bundle(seeds=range(1200, 1210), config=config, run_id="pytest-replay")
    oracle = core.run_interventional_oracle(bundle, run_id="pytest-replay-oracle")
    report = replay.replay_oracle_predictions(
        serialized_state=oracle["serialized_state"],
        intervention_rows=oracle["legal_intervention_rows"],
        stored_predictions=oracle["predictions"],
        run_id="pytest-replay-report",
    )

    assert report["verdict"] == "replay_recomputed"
    assert report["hash_only"] is False
    assert report["used_serialized_state"] is True
    assert report["used_intervention_rows"] is True
    assert report["negative_control"]["stored_hash_tamper_accepted"] is False
    assert report["negative_control"]["corrupt_intervention_log_changes_behavior"] is True


def test_result_writer_preserves_claim_ceiling_blockers_and_parent_hashes(tmp_path):
    from route_c_preflight_001a import runner

    out = tmp_path / "route_c"
    result = runner.run_preflight(
        repo_root=ROOT,
        output_dir=out,
        run_id="pytest-runner",
        seeds=range(1300, 1332),
    )

    written = _load_json(out / "result.json")
    assert result["verdict"] in runner.ALLOWED_VERDICTS
    assert written["claim_ceiling"] == runner.CLAIM_CEILING
    assert written["blockers"] == result["blockers"]
    assert written["parent_doc_hashes"]["blueprint_sha256"]
    assert written["parent_doc_hashes"]["task_card_sha256"]
    assert (out / "trace.jsonl").exists()
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == runner.CLAIM_CEILING


def test_failure_manifest_emitted_on_block(tmp_path):
    from route_c_preflight_001a import core, runner

    out = tmp_path / "blocked"
    result = runner.run_preflight(
        repo_root=ROOT,
        output_dir=out,
        run_id="pytest-blocked",
        config=core.default_config(gain=0.0, n_passive=16, interventions_per_channel=4),
        seeds=range(1400, 1416),
    )

    manifest = _load_json(out / "failure_manifest.json")
    assert result["verdict"] == "blocked_by_no_interventional_headroom"
    assert manifest["verdict"] == "blocked_by_no_interventional_headroom"
    assert "blocked_by_no_interventional_headroom" in manifest["stop_conditions"]


def test_no_candidate_or_forbidden_path_implementation_exists():
    from route_c_preflight_001a import runner

    package = ROOT / "src" / "route_c_preflight_001a"
    assert not (package / "candidate.py").exists()
    assert runner.find_forbidden_status_paths(
        [
            "?? src/route_c_preflight_001a/core.py",
            "?? tests/route_c_preflight_001a/test_route_c_preflight_001a.py",
            "?? artifacts/route_c_preflight_001a/result.json",
        ]
    ) == []
    assert runner.find_forbidden_status_paths([" M src/ego_mainline_admission_execution_001a/runner.py"]) == [
        "src/ego_mainline_admission_execution_001a/runner.py"
    ]
