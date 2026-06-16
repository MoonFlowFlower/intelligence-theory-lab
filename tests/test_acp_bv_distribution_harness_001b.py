import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

REQUIRED_ARTIFACTS = {
    "result.json",
    "readback.json",
    "validation.json",
    "run_manifest.json",
    "source_boundary.json",
    "source_pin.json",
    "distribution_manifest.json",
    "novelty_report.json",
    "factorization_report.json",
    "baseline_matrix.json",
    "strongest_baseline_selection.json",
    "candidate_results.json",
    "baseline_results.json",
    "b3_classification.json",
    "multi_seed_stability.json",
    "detector_failability.json",
    "leakage_scan.json",
    "leakage_literal_audit.json",
    "solvability_preflight.json",
    "candidate_truth_decoupling.json",
    "ablation_results.json",
    "replay_results.json",
    "provenance_rows.jsonl",
    "forbidden_scope_scan.txt",
    "claim_ceiling.txt",
}

BASELINES = {
    "parametric_modular_linear_baseline",
    "full_access_lookup_baseline",
    "exact_key_memory_baseline",
    "factorized_lookup_baseline",
    "per_component_lookup_baseline",
    "partial_key_lookup_baseline",
    "topology_only_baseline",
    "risk_only_baseline",
    "signal_action_baseline",
    "action_conditioned_nearest_neighbor_baseline",
    "transition_table_graph_cache_baseline",
    "successor_map_graph_cache_baseline",
    "count_table_graph_cache_baseline",
    "episodic_traversal_graph_cache_baseline",
    "fsm_planner_graph_cache_baseline",
    "query_capable_imitation_baseline",
    "catch_all_fair_memory_lookup_hook",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _score_rows(episodes, rows):
    from acp_bv_distribution_harness_001b import baselines

    return baselines.score_outputs(episodes, rows)


def test_generator_satisfies_required_multi_seed_distribution_constraints():
    from acp_bv_distribution_harness_001b import generator

    dataset = generator.generate_distribution(seed=1009, heldout_count=128)
    manifest = generator.distribution_manifest(dataset)

    assert manifest["heldout_count"] >= 128
    assert manifest["unseen_heldout_ratio"] >= 0.40
    assert manifest["unseen_heldout_count"] >= 52
    assert manifest["lookup_complete_heldout_ratio"] <= 0.75
    assert set(manifest["factorization_families"]) == {
        "signal_family",
        "topology_family",
        "risk_family",
        "phase_family",
    }
    assert all(
        ratio >= 0.25
        for ratio in manifest["unseen_component_ratio_by_family"].values()
    )
    assert all(
        "target" not in "".join(episode["observation"].keys()).lower()
        for episode in dataset["heldout"]
    )


def test_runner_writes_required_artifacts_from_callable_execution(tmp_path):
    from acp_bv_distribution_harness_001b import runner

    out = tmp_path / "acp_bv_distribution_harness_001b_execution_001a"
    result = runner.run_harness(repo_root=ROOT, output_dir=out, run_id="pytest-acp-bv-001b")
    closure = out.parent / "acp_bv_001b_collapse_closure_001a" / "result.json"

    assert result["verdict"] == "blocked_by_candidate_truth_coupling"
    assert result["mainline_integration_status"] == "none"
    assert result["enabled_status"] == "local CLI / local pytest / local artifact generation only"
    assert result["real_gate_target_applied"] is False
    assert result["safe_to_wire_mainline"] is False
    assert result["claim_ceiling"] == "ACP-BV 001B local harness implementation and computed-evidence artifact generation only"

    assert REQUIRED_ARTIFACTS == {path.name for path in out.iterdir() if path.is_file()}
    for artifact in REQUIRED_ARTIFACTS - {"claim_ceiling.txt", "forbidden_scope_scan.txt", "provenance_rows.jsonl"}:
        _load_json(out / artifact)
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == result["claim_ceiling"]
    assert (out / "provenance_rows.jsonl").read_text(encoding="utf-8").strip()
    assert closure.exists()
    closure_payload = _load_json(closure)
    assert closure_payload["terminal"] is True
    assert closure_payload["collapse_family"] == "candidate_truth_coupling"
    assert closure_payload["coupling_report"]["verdict"] == "blocked_by_candidate_truth_coupling"

    baseline_matrix = _load_json(out / "baseline_matrix.json")
    assert {row["baseline_id"] for row in baseline_matrix["baselines"]} == BASELINES
    assert baseline_matrix["strongest_baseline_selection_rule"] == "deterministic_argmax_score_preserve_most_damaging_tie"
    assert baseline_matrix["strongest_baseline"]["baseline_id"] == "parametric_modular_linear_baseline"
    assert baseline_matrix["blocked_by_baseline_equivalence"] is True
    assert all(row["provenance"]["producer_function"] for row in baseline_matrix["baselines"])
    assert all(row["provenance"]["code_path_hash"] for row in baseline_matrix["baselines"])

    stability = _load_json(out / "multi_seed_stability.json")
    assert stability["seed_count"] == 5
    assert stability["seeds"] == [1009, 2027, 3037, 4049, 5051]
    assert stability["any_seed_baseline_equivalent"] is True


def test_runner_records_validation_and_scope_as_local_only(tmp_path):
    from acp_bv_distribution_harness_001b import runner

    out = tmp_path / "run"
    runner.run_harness(repo_root=ROOT, output_dir=out, run_id="pytest-scope")

    validation = _load_json(out / "validation.json")
    readback = _load_json(out / "readback.json")
    manifest = _load_json(out / "run_manifest.json")

    assert validation["all_required_artifacts_present"] is True
    assert validation["no_static_verdict_dictionary"] is True
    assert validation["no_forbidden_scope_paths_changed"] is True
    assert validation["auto_remote_anchor"]["decision"] == "forbidden"
    assert readback["current_layer"] == "engineering implementation / local ACP-BV 001B harness execution only"
    assert readback["what_this_does_not_prove"]
    assert "PYTHONPATH" in manifest["command"]
    assert "python -m acp_bv_distribution_harness_001b.runner" in manifest["command"]
    assert manifest["real_gate_target_applied"] is False


def test_coupling_detector_catches_oracle_candidate_and_not_data_dependent_learner():
    from acp_bv_distribution_harness_001b import candidate, coupling, generator

    datasets = [generator.generate_distribution(seed=1009)]
    report = coupling.detect_candidate_truth_coupling(
        predict_fn=candidate.predict,
        fit_fn=candidate.fit_candidate,
        truth_fn=generator.truth_for,
        datasets=datasets,
        seed=1009,
    )

    assert report["verdict"] == "blocked_by_candidate_truth_coupling"
    assert report["agreement_rate_extrapolation"] == 1.0
    assert report["training_response"]["predictions_invariant_to_training"] is True
    assert report["trigger_A_oracle_match"] is True
    assert report["trigger_B_training_invariance"] is True
    assert report["evidence_hash"]

    def fit_majority(train):
        counts = {}
        for episode in train:
            action = episode["chosen_action"]
            value = tuple(episode["truth_by_action"][action].items())
            counts[(action, value)] = counts.get((action, value), 0) + 1
        by_action = {}
        for (action, value), count in sorted(counts.items(), key=lambda row: (-row[1], str(row[0]))):
            by_action.setdefault(action, dict(value))
        fallback = {"boundary_state": -1, "viability_state": -1}
        return {"by_action": by_action, "fallback": fallback}

    def predict_majority(state, observation, action):
        return state["by_action"].get(action, state["fallback"])

    clean = coupling.detect_candidate_truth_coupling(
        predict_fn=predict_majority,
        fit_fn=fit_majority,
        truth_fn=generator.truth_for,
        datasets=datasets,
        seed=1009,
    )

    assert clean["verdict"] == "candidate_truth_not_coupled"
    assert clean["training_response"]["predictions_invariant_to_training"] is False


def test_parametric_baseline_is_registered_degenerate_on_empty_and_ignores_counterfactual_labels():
    from copy import deepcopy

    from acp_bv_distribution_harness_001b import baselines, candidate, generator

    dataset = generator.generate_distribution(seed=1009)
    assert "parametric_modular_linear_baseline" in baselines.BASELINE_FUNCTIONS

    candidate_state = candidate.fit_candidate(dataset["train"])
    candidate_rows = candidate.run_candidate(candidate_state, dataset["heldout"])
    candidate_score = _score_rows(dataset["heldout"], candidate_rows)

    fitted_rows = baselines.parametric_modular_linear_baseline(dataset["train"], dataset["heldout"])
    fitted_score = _score_rows(dataset["heldout"], fitted_rows)
    assert abs(candidate_score - fitted_score) <= 0.02

    empty_rows = baselines.parametric_modular_linear_baseline([], dataset["heldout"])
    empty_score = _score_rows(dataset["heldout"], empty_rows)
    assert empty_score <= 0.35

    poisoned_train = deepcopy(dataset["train"])
    for episode in poisoned_train:
        chosen = episode["chosen_action"]
        for action in episode["truth_by_action"]:
            if action != chosen:
                episode["truth_by_action"][action] = {"boundary_state": 999, "viability_state": 999}
    poisoned_rows = baselines.parametric_modular_linear_baseline(poisoned_train, dataset["heldout"])
    assert poisoned_rows == fitted_rows


def test_detector_paths_are_not_hard_coded_false_or_self_declared_metadata_trust():
    coupling_source = (SRC / "acp_bv_distribution_harness_001b" / "coupling.py").read_text(encoding="utf-8")
    runner_source = (SRC / "acp_bv_distribution_harness_001b" / "runner.py").read_text(encoding="utf-8")
    baselines_source = (SRC / "acp_bv_distribution_harness_001b" / "baselines.py").read_text(encoding="utf-8")
    detectors_source = (SRC / "acp_bv_distribution_harness_001b" / "detectors.py").read_text(encoding="utf-8")

    assert "candidate_authored_truth" not in coupling_source
    assert "uses_hidden_truth_labels" not in coupling_source
    assert "uses_future_observations" not in coupling_source
    assert '"leaking_oracle_solvability_detected": False' not in runner_source
    assert '"blocked_by_factorized_lookup_equivalence": False' not in baselines_source
    assert "actual_verdict_before=before" not in detectors_source
    assert "actual_verdict_after=after" not in detectors_source
