import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _snapshot(config):
    from route_c_preflight_001a import core, provenance

    return provenance.build_threshold_snapshot(config=config, config_type=core.Config)


def _full_failure_controls() -> dict:
    return {k: True for k in ("premise", "schema_alias", "interventional_headroom", "leakage", "replay", "provenance", "verdict")}


# --------------------------------------------------------------------------- #
# Regression: contamination guard + clean-surface chance + schema detection
# --------------------------------------------------------------------------- #
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
    for attacker in panel["obs_only"]["attackers"]:
        assert attacker["aggregate_score"]["value"] <= config.premise_threshold, attacker["attacker"]
    assert panel["obs_only"]["family_max"]["value"] <= config.premise_threshold


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


# --------------------------------------------------------------------------- #
# 1. baseline family actually reads passive handle_values
# --------------------------------------------------------------------------- #
def test_baseline_family_reads_passive_handle_values():
    from route_c_preflight_001a import core, leakage

    config = core.default_config(n_passive=16, interventions_per_channel=2)
    bundle = core.build_episode_bundle(seeds=range(300, 320), config=config, run_id="pytest-reads")
    injected = leakage.inject_observation_value_decodable_self_set(bundle)
    legal_clean = [e["legal"] for e in bundle["episodes"]]
    legal_leak = [e["legal"] for e in injected["episodes"]]

    truth = {e["episode_id"]: set(e["truth_self_handles"]) for e in bundle["episodes"]}

    # A value attacker decodes S from leaked VALUES; the positional no-op does not.
    mean_leak = core.passive_mean_attacker(legal_leak, config=config)
    mean_clean = core.passive_mean_attacker(legal_clean, config=config)
    pos_leak = core.positional_first_k_attacker(legal_leak, config=config)
    pos_clean = core.positional_first_k_attacker(legal_clean, config=config)

    def hit_rate(preds, legals):
        hits = sum(len(set(p) & truth[le["episode_id"]]) for p, le in zip(preds, legals))
        return hits / (len(legals) * config.k_self)

    assert hit_rate(mean_leak, legal_leak) == pytest.approx(1.0)
    assert hit_rate(mean_clean, legal_clean) <= config.premise_threshold
    # Positional ignores values entirely -> identical predictions clean vs leaked.
    assert pos_leak == pos_clean


# --------------------------------------------------------------------------- #
# 2 + 6. value-level decodable control blocks via the premise gate
# --------------------------------------------------------------------------- #
def test_value_level_observation_decodable_control_blocks():
    from route_c_preflight_001a import core, leakage

    config = core.default_config(n_passive=16, interventions_per_channel=2)
    bundle = core.build_episode_bundle(seeds=range(400, 420), config=config, run_id="pytest-l9")
    injected = leakage.inject_observation_value_decodable_self_set(bundle)
    panel = core.run_baseline_panel(injected, run_id="pytest-l9-panel")
    gate = core.non_identifiability_premise_gate(panel, config=config)

    value_level_names = {n for n, _f, vl, _w in core.PASSIVE_ATTACKER_FAMILY if vl}
    assert gate["verdict"] == "blocked_by_observation_decodable_self_set"
    assert panel["obs_only"]["family_max"]["value"] == pytest.approx(1.0)
    assert panel["obs_only"]["family_max_attacker"] in value_level_names
    # The key/name scanner stays silent -> this is a value leak, not a token leak.
    assert leakage.scan_bundle_for_leakage(injected)["verdict"] == "clean"


def test_observation_decodable_variant_forces_blocked_via_leakage_runner():
    from route_c_preflight_001a import core, leakage

    config = core.default_config(n_passive=12, interventions_per_channel=2)
    bundle = core.build_episode_bundle(seeds=range(420, 436), config=config, run_id="pytest-l9-run")
    report = leakage.run_leakage_positive_controls(bundle=bundle, config=config, run_id="pytest-l9-run")
    l9 = report["control_results"]["L9"]
    assert l9["fired"] is True
    assert l9["gate_verdict"] == "blocked_by_observation_decodable_self_set"
    assert l9["decoded_by_value_level_attacker"] is True


# --------------------------------------------------------------------------- #
# 3. old positional guess cannot pass as a capable baseline
# --------------------------------------------------------------------------- #
def test_old_positional_guess_cannot_pass_as_capable_baseline():
    from route_c_preflight_001a import core, leakage

    config = core.default_config(n_passive=16, interventions_per_channel=2)
    bundle = core.build_episode_bundle(seeds=range(440, 460), config=config, run_id="pytest-pos")
    injected = leakage.inject_observation_value_decodable_self_set(bundle)
    legal_leak = [e["legal"] for e in injected["episodes"]]
    truth = {e["episode_id"]: set(e["truth_self_handles"]) for e in bundle["episodes"]}

    pos = core.positional_first_k_attacker(legal_leak, config=config)
    pos_rate = sum(len(set(p) & truth[le["episode_id"]]) for p, le in zip(pos, legal_leak)) / (len(legal_leak) * config.k_self)
    # Positional stays at/under chance on a value leak it cannot see ...
    assert pos_rate <= config.premise_threshold
    # ... while the capable family decodes it.
    panel = core.run_baseline_panel(injected, run_id="pytest-pos-panel")
    assert panel["obs_only"]["family_max"]["value"] > config.premise_threshold


# --------------------------------------------------------------------------- #
# 4. premise gate uses the family max, not a weak individual attacker
# --------------------------------------------------------------------------- #
def test_obs_only_family_max_is_used_by_premise_gate():
    from route_c_preflight_001a import core, leakage

    config = core.default_config(n_passive=16, interventions_per_channel=2)
    bundle = core.build_episode_bundle(seeds=range(460, 480), config=config, run_id="pytest-fmax")
    injected = leakage.inject_observation_value_decodable_self_set(bundle)
    panel = core.run_baseline_panel(injected, run_id="pytest-fmax-panel")
    gate = core.non_identifiability_premise_gate(panel, config=config)

    family_max = panel["obs_only"]["family_max"]["value"]
    weakest = min(a["aggregate_score"]["value"] for a in panel["obs_only"]["attackers"])
    assert gate["value"] == pytest.approx(family_max)
    assert family_max > weakest  # the gate did not use a weak attacker
    assert gate["verdict"] == "blocked_by_observation_decodable_self_set"


# --------------------------------------------------------------------------- #
# 5. canonical clean surface is not blocked by the value-leak control artifact
# --------------------------------------------------------------------------- #
def test_canonical_clean_surface_not_blocked_by_value_leak_control_artifact():
    from route_c_preflight_001a import core, leakage

    config = core.default_config(n_passive=24, interventions_per_channel=4)
    bundle = core.build_episode_bundle(seeds=range(500, 540), config=config, run_id="pytest-canon")
    # The control is applied to a COPY; canonical must remain non-identifiable.
    _injected = leakage.inject_observation_value_decodable_self_set(bundle)
    panel = core.run_baseline_panel(bundle, run_id="pytest-canon-panel")
    gate = core.non_identifiability_premise_gate(panel, config=config)
    assert gate["verdict"] == "non_identifiability_present"
    assert panel["obs_only"]["family_max"]["value"] <= config.premise_threshold


# --------------------------------------------------------------------------- #
# 7. zero-gain still forces blocked_by_no_interventional_headroom
# --------------------------------------------------------------------------- #
def test_no_headroom_control_still_forces_blocked():
    from route_c_preflight_001a import core

    config = core.default_config(gain=0.0, n_passive=20, interventions_per_channel=8)
    bundle = core.build_episode_bundle(seeds=range(560, 592), config=config, run_id="pytest-g0")
    panel = core.run_baseline_panel(bundle, run_id="pytest-g0-panel")
    oracle = core.run_interventional_oracle(bundle, run_id="pytest-g0-oracle")
    gate = core.interventional_headroom_gate(
        obs_score=panel["obs_only"]["family_max"]["value"],
        oracle_score=oracle["aggregate_score"]["value"],
        config=config,
    )
    assert gate["verdict"] == "blocked_by_no_interventional_headroom"


def test_interventional_oracle_gets_headroom_on_clean_generator():
    from route_c_preflight_001a import core

    config = core.default_config(n_passive=32, interventions_per_channel=12)
    bundle = core.build_episode_bundle(seeds=range(800, 832), config=config, run_id="pytest-hr")
    panel = core.run_baseline_panel(bundle, run_id="pytest-hr-panel")
    oracle = core.run_interventional_oracle(bundle, run_id="pytest-hr-oracle")
    gate = core.interventional_headroom_gate(
        obs_score=panel["obs_only"]["family_max"]["value"],
        oracle_score=oracle["aggregate_score"]["value"],
        config=config,
    )
    assert gate["verdict"] == "interventional_headroom_present"
    assert gate["value"] > config.headroom_band


# --------------------------------------------------------------------------- #
# 8. provenance includes all material producers
# --------------------------------------------------------------------------- #
def test_provenance_includes_all_material_producers(tmp_path):
    from route_c_preflight_001a import runner

    out = tmp_path / "prov"
    result = runner.run_preflight(repo_root=ROOT, output_dir=out, run_id="pytest-prov", seeds=range(900, 924))
    rows = [json.loads(line) for line in (out / "provenance_rows.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    producers = {row["producer_function"] for row in rows}
    subsystems = {row["subsystem"] for row in rows}

    expected_producers = {
        "route_c_preflight_001a.core.passive_mean_attacker",
        "route_c_preflight_001a.core.passive_variance_attacker",
        "route_c_preflight_001a.core.passive_correlation_attacker",
        "route_c_preflight_001a.core.passive_pca_subspace_attacker",
        "route_c_preflight_001a.core.passive_cross_episode_attacker",
        "route_c_preflight_001a.core.supervised_passive_feature_attacker",
        "route_c_preflight_001a.core.positional_first_k_attacker",
        "route_c_preflight_001a.core.legal_field_membership_attacker",
        "route_c_preflight_001a.core.obs_only_family_max",
        "route_c_preflight_001a.core.schema_only_attacker",
        "route_c_preflight_001a.core.name_order_attacker",
        "route_c_preflight_001a.core.run_interventional_oracle",
        "route_c_preflight_001a.core.non_identifiability_premise_gate",
        "route_c_preflight_001a.core.interventional_headroom_gate",
        "route_c_preflight_001a.leakage.run_leakage_positive_controls",
        "route_c_preflight_001a.replay.replay_oracle_predictions",
        "route_c_preflight_001a.provenance.validate_provenance_rows",
        "route_c_preflight_001a.runner._select_verdict",
    }
    assert expected_producers <= producers, expected_producers - producers
    assert {"premise", "schema_alias", "interventional_headroom", "leakage", "replay", "provenance", "verdict"} <= subsystems
    assert result["provenance_validation_result"]["verdict"] == "provenance_valid"
    # every row carries a real code_path_hash
    assert all(row.get("code_path_hash") for row in rows)


# --------------------------------------------------------------------------- #
# 9. leakage and replay carry code_path_hashes resolvable to real source
# --------------------------------------------------------------------------- #
def test_leakage_and_replay_have_code_path_hashes():
    from route_c_preflight_001a import core, leakage, provenance, replay

    config = core.default_config(n_passive=12, interventions_per_channel=6)
    snap = _snapshot(config)
    bundle = core.build_episode_bundle(seeds=range(1000, 1012), config=config, run_id="pytest-cph")
    lk = leakage.run_leakage_positive_controls(bundle=bundle, config=config, run_id="pytest-cph-lk", threshold_snapshot_hash=snap["snapshot_hash"])
    oracle = core.run_interventional_oracle(bundle, run_id="pytest-cph-or", threshold_snapshot_hash=snap["snapshot_hash"])
    rp = replay.replay_oracle_predictions(
        serialized_state=oracle["serialized_state"], intervention_rows=oracle["legal_intervention_rows"],
        stored_predictions=oracle["predictions"], run_id="pytest-cph-rp", threshold_snapshot_hash=snap["snapshot_hash"],
    )
    for rec in (lk["provenance_record"], rp["provenance_record"]):
        assert rec["code_path_hash"]
        fn = provenance.resolve_producer(rec["producer_function"])
        assert fn is not None
        assert provenance.code_path_hash(fn) == rec["code_path_hash"]


# --------------------------------------------------------------------------- #
# 10. hardcoded True attestations are not accepted
# --------------------------------------------------------------------------- #
def test_hardcoded_true_attestations_are_not_accepted():
    from route_c_preflight_001a import core, provenance

    config = core.default_config()
    snap = _snapshot(config)
    good = provenance.aggregate_score_record(
        scores=[0.5, 0.5], producer_function=provenance.aggregate_score_record,
        inputs={"x": 1}, run_id="r", episode_ids=["e"], threshold_used=config.premise_threshold,
        threshold_snapshot_hash=snap["snapshot_hash"], subsystem="premise",
    )
    assert provenance.validate_provenance_rows([good], threshold_snapshot=snap, failure_controls=_full_failure_controls())["verdict"] == "provenance_valid"

    # Hardcode the attestation True but break the source hash -> must be rejected.
    forged = dict(good)
    forged["code_path_hash"] = "0" * 64
    forged["computed_not_literal"] = True
    res = provenance.validate_provenance_rows([forged], threshold_snapshot=snap, failure_controls=_full_failure_controls())
    assert res["verdict"] == "blocked_by_provenance_gap"
    reasons = {f["reason"] for f in res["failures"]}
    assert "not_computed_or_source_hash_mismatch" in reasons
    assert any("disagrees_with_computed" in r for r in reasons)


def test_provenance_blocks_when_failure_control_absent():
    from route_c_preflight_001a import core, provenance

    config = core.default_config()
    snap = _snapshot(config)
    rec = provenance.aggregate_score_record(
        scores=[0.4], producer_function=provenance.aggregate_score_record, inputs={}, run_id="r",
        episode_ids=["e"], threshold_used=config.premise_threshold, threshold_snapshot_hash=snap["snapshot_hash"], subsystem="premise",
    )
    fc = _full_failure_controls()
    fc["premise"] = False  # the premise failure control did not fire this run
    res = provenance.validate_provenance_rows([rec], threshold_snapshot=snap, failure_controls=fc)
    assert res["verdict"] == "blocked_by_provenance_gap"
    assert any(f["reason"] == "failure_path_unavailable" for f in res["failures"])


# --------------------------------------------------------------------------- #
# 11 + 12. replay fails when intervention rows / serialized state corrupted
# --------------------------------------------------------------------------- #
def test_replay_fails_when_intervention_rows_corrupted():
    from route_c_preflight_001a import core, replay

    config = core.default_config(n_passive=8, interventions_per_channel=8)
    bundle = core.build_episode_bundle(seeds=range(1200, 1208), config=config, run_id="pytest-rc")
    oracle = core.run_interventional_oracle(bundle, run_id="pytest-rc-or")
    corrupted = replay._corrupt_rows(oracle["legal_intervention_rows"], oracle["predictions"])
    rep = replay.replay_oracle_predictions(
        serialized_state=oracle["serialized_state"], intervention_rows=corrupted,
        stored_predictions=oracle["predictions"], run_id="pytest-rc-rp",
    )
    assert rep["verdict"] != "replay_recomputed"
    assert rep["clean_matches"] is False


def test_replay_fails_when_serialized_state_corrupted():
    from route_c_preflight_001a import core, replay

    config = core.default_config(n_passive=8, interventions_per_channel=8)
    bundle = core.build_episode_bundle(seeds=range(1210, 1218), config=config, run_id="pytest-rs")
    oracle = core.run_interventional_oracle(bundle, run_id="pytest-rs-or")
    corrupted_state = replay._corrupt_state(oracle["serialized_state"])
    rep = replay.replay_oracle_predictions(
        serialized_state=corrupted_state, intervention_rows=oracle["legal_intervention_rows"],
        stored_predictions=oracle["predictions"], run_id="pytest-rs-rp",
    )
    assert rep["verdict"] != "replay_recomputed"


def test_replay_recomputes_clean_and_all_tamper_controls_flip():
    from route_c_preflight_001a import core, replay

    config = core.default_config(n_passive=16, interventions_per_channel=8)
    bundle = core.build_episode_bundle(seeds=range(1220, 1230), config=config, run_id="pytest-rg")
    oracle = core.run_interventional_oracle(bundle, run_id="pytest-rg-or")
    rep = replay.replay_oracle_predictions(
        serialized_state=oracle["serialized_state"], intervention_rows=oracle["legal_intervention_rows"],
        stored_predictions=oracle["predictions"], run_id="pytest-rg-rp",
    )
    nc = rep["negative_control"]
    assert rep["verdict"] == "replay_recomputed"
    assert nc["corrupt_intervention_log_changes_behavior"] is True
    assert nc["removed_intervention_rows_changes_behavior"] is True
    assert nc["corrupt_serialized_state_changes_behavior"] is True
    assert nc["recompute_ignores_stored_predictions"] is True
    assert nc["stored_hash_tamper_accepted"] is False


# --------------------------------------------------------------------------- #
# 13 + 14. candidate absent + no forbidden paths touched
# --------------------------------------------------------------------------- #
def test_candidate_implementation_absent():
    package = ROOT / "src" / "route_c_preflight_001a"
    assert not (package / "candidate.py").exists()
    names = {p.name for p in package.glob("*.py")}
    assert names == {"__init__.py", "__main__.py", "core.py", "leakage.py", "provenance.py", "replay.py", "runner.py"}


def test_no_gate_mainline_runtime_bridge_scheduler_admission_product_paths_touched():
    from route_c_preflight_001a import runner

    assert runner.find_forbidden_status_paths(
        [
            "?? src/route_c_preflight_001a/core.py",
            "?? tests/route_c_preflight_001a/test_route_c_preflight_001a.py",
            "?? artifacts/route_c_preflight_001a/result.json",
        ]
    ) == []
    for forbidden in (
        " M src/ego_mainline_admission_execution_001a/runner.py",
        " M src/acsb_core.py",
        " M src/acolb_a.py",
    ):
        assert runner.find_forbidden_status_paths([forbidden])


# --------------------------------------------------------------------------- #
# Runner integration: writes artifacts, preserves ceiling/blockers/hashes
# --------------------------------------------------------------------------- #
def test_result_writer_preserves_claim_ceiling_blockers_and_parent_hashes(tmp_path):
    from route_c_preflight_001a import runner

    out = tmp_path / "route_c"
    result = runner.run_preflight(repo_root=ROOT, output_dir=out, run_id="pytest-runner", seeds=range(1300, 1332))
    written = _load_json(out / "result.json")
    assert result["verdict"] in runner.ALLOWED_VERDICTS
    assert written["claim_ceiling"] == runner.CLAIM_CEILING
    assert written["blockers"] == result["blockers"]
    assert written["parent_doc_hashes"]["blueprint_sha256"]
    assert written["parent_negative_audit"]["blocking_verdict"] == "blocked_by_observation_baseline_underpowered"
    assert (out / "trace.jsonl").exists()
    assert (out / "provenance_rows.jsonl").exists()
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == runner.CLAIM_CEILING


def test_failure_manifest_emitted_on_block(tmp_path):
    from route_c_preflight_001a import core, runner

    out = tmp_path / "blocked"
    result = runner.run_preflight(
        repo_root=ROOT, output_dir=out, run_id="pytest-blocked",
        config=core.default_config(gain=0.0, n_passive=16, interventions_per_channel=4), seeds=range(1400, 1416),
    )
    manifest = _load_json(out / "failure_manifest.json")
    assert result["verdict"] == "blocked_by_no_interventional_headroom"
    assert "blocked_by_no_interventional_headroom" in manifest["stop_conditions"]
