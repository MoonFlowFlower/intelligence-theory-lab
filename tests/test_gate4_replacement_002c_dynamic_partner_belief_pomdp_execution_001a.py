import copy
import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "gate4_replacement_002c_dynamic_partner_belief_pomdp_execution_001a"
ARTIFACT_DIR = ROOT / "artifacts" / TASK_ID

REQUIRED_ARTIFACTS = {
    "result.json",
    "environment_manifest.json",
    "candidate_result.json",
    "baseline_results.json",
    "strongest_baseline_report.json",
    "ablation_results.json",
    "replay_results.json",
    "leakage_positive_control_results.json",
    "negative_control_results.json",
    "provenance_manifest.json",
    "static_score_guard_report.json",
    "non_mutation_guard.json",
    "source_pin_readback.json",
    "claim_ceiling.txt",
}

REQUIRED_BASELINES = {
    "random_control",
    "pair_count",
    "ngram_trace_lookup",
    "partner_id",
    "preference_table",
    "full_bundle_decoder",
    "serialized_state_decoder",
    "finite_state_policy",
    "query_capable_imitation",
    "belief_table",
    "oracle_access_upper_bound",
    "ablated_candidate_social_latent_disabled",
    "non_social_world_model",
}

REQUIRED_ABLATIONS = {
    "disable_social_latent_update",
    "freeze_other_state_after_initial_observation",
    "shuffle_partner_observation_history",
    "remove_partner_policy_shift",
    "swap_partner_latent_dynamics",
    "mask_partner_id_and_explicit_labels",
    "inject_target_leakage_positive_control",
    "remove_social_signal_negative_control",
}


def _module():
    return importlib.import_module(
        "gate4_replacement_002c_dynamic_partner_belief_pomdp_execution_001a.core"
    )


def test_candidate_and_all_required_baselines_are_callable_and_invoked():
    core = _module()

    run = core.execute_experiment(output_dir=None, persist_artifacts=False)
    baseline_results = run["baseline_results"]

    assert run["candidate_result"]["callable_invoked"] is True
    assert run["candidate_result"]["producer_function"] == "score_candidate"
    assert REQUIRED_BASELINES.issubset(set(baseline_results["invoked_baselines"]))
    assert set(core.BASELINE_FUNCTIONS) == REQUIRED_BASELINES
    assert baseline_results["invocation_check"]["passed"] is True
    assert baseline_results["rows"]["random_control"]["score"] < run["candidate_result"]["score"]
    for baseline_id in REQUIRED_BASELINES:
        row = baseline_results["rows"][baseline_id]
        assert row["callable_invoked"] is True
        assert row["producer_function"].startswith("baseline_")
        assert row["access_rights_declaration"]
        assert row["failure_mode_ruled_out"]
        assert row["code_path_hash"]


def test_strong_faithful_baseline_tie_is_preserved_as_negative_evidence():
    core = _module()

    run = core.execute_experiment(output_dir=None, persist_artifacts=False)
    result = run["result"]
    strongest = run["strongest_baseline_report"]

    assert strongest["strongest_faithful_non_oracle"]["baseline_id"] in {
        "belief_table",
        "serialized_state_decoder",
        "full_bundle_decoder",
    }
    assert strongest["strongest_faithful_non_oracle"]["score"] >= run["candidate_result"]["score"]
    assert result["verdict"] == "gate4_replacement_002c_baseline_equivalent_negative_evidence"
    assert result["positive_mechanism_evidence_allowed"] is False
    assert "faithful_baseline_tied_or_beat_candidate" in result["stop_conditions_triggered"]
    assert result["safe_to_enter_gate5"] is False
    assert result["safe_to_enter_admission"] is False
    assert result["safe_to_enter_bridge"] is False
    assert result["safe_to_enter_runtime"] is False
    assert result["safe_to_enter_ego_mainline"] is False


def test_controls_ablations_replay_and_provenance_are_computed_paths():
    core = _module()

    run = core.execute_experiment(output_dir=None, persist_artifacts=False)
    ablations = run["ablation_results"]
    replay = run["replay_results"]
    leakage = run["leakage_positive_control_results"]
    negative = run["negative_control_results"]
    provenance = run["provenance_manifest"]

    assert REQUIRED_ABLATIONS.issubset(set(ablations["interventions"]))
    assert ablations["all_interventions_rerun"] is True
    assert ablations["interventions"]["disable_social_latent_update"]["run_id"] != run["candidate_result"]["run_id"]
    assert ablations["interventions"]["disable_social_latent_update"]["candidate_score"] < run["candidate_result"]["score"]
    assert leakage["positive_control_detected"] is True
    assert leakage["scanner_positive_control_case"]["verdict"] == "blocked_by_leakage_scan"
    assert negative["false_success_blocked"] is True
    assert negative["score"] < run["candidate_result"]["score"]
    assert replay["passed"] is True
    assert replay["recomputed_from_serialized_state_plus_observation"] is True
    assert replay["failure_path_result"]["passed"] is False
    assert core.verify_provenance(provenance)["passed"] is True


def test_static_score_guard_catches_literal_result_injection():
    core = _module()

    run = core.execute_experiment(output_dir=None, persist_artifacts=False)
    guard = run["static_score_guard_report"]

    assert guard["positive_control_static_injection_detected"] is True
    injected = copy.deepcopy(run["provenance_manifest"])
    injected["records"][0]["static_score_injection"] = True
    injected["records"][0]["producer_function"] = "literal_score_table"
    assert core.verify_provenance(injected)["passed"] is False


def test_source_boundary_and_prior_artifacts_are_pinned_without_mutation():
    core = _module()

    before = core.hash_protected_boundaries(ROOT)
    run = core.execute_experiment(output_dir=None, persist_artifacts=False)
    after = core.hash_protected_boundaries(ROOT)
    source = run["source_pin_readback"]

    assert before == after
    assert source["sealed_boundary"] == core.SEALED_BOUNDARY
    assert source["local_required_tag"] == core.SEALED_BOUNDARY
    assert source["remote_required_tag"] == core.SEALED_BOUNDARY
    assert source["sealed_anchor_integrity_verified"] is True
    assert run["non_mutation_guard"]["passed"] is True
    assert run["non_mutation_guard"]["changed_protected_paths"] == []


def test_materialized_artifacts_and_research_summary_parse():
    core = _module()

    core.execute_experiment(output_dir=ARTIFACT_DIR, persist_artifacts=True)

    names = {path.name for path in ARTIFACT_DIR.iterdir()}
    assert REQUIRED_ARTIFACTS.issubset(names)
    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt"}:
        json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))
    assert "bounded executable evidence inside the 002C toy" in (
        ARTIFACT_DIR / "claim_ceiling.txt"
    ).read_text(encoding="utf-8")
    summary = ROOT / "docs" / "research" / "GATE4-REPLACEMENT-002C-DYNAMIC-PARTNER-BELIEF-POMDP-EXECUTION-001A.md"
    assert summary.exists()
    text = summary.read_text(encoding="utf-8")
    assert "baseline-equivalent negative evidence" in text
    assert "What This Does Not Prove" in text
