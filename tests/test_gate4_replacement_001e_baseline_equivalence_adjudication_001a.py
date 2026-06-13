import copy
import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "gate4_replacement_001e_baseline_equivalence_adjudication_001a"
ARTIFACT_DIR = ROOT / "artifacts" / TASK_ID

REQUIRED_ARTIFACTS = {
    "result.json",
    "source_pin_readback.json",
    "baseline_equivalence_report.json",
    "recoverability_adjudication_report.json",
    "decoder_probe_report.json",
    "trace_probe_report.json",
    "provenance_report.json",
    "non_mutation_guard.json",
    "claim_ceiling.txt",
}

REQUIRED_BASELINES = {
    "pair_count_table",
    "full_candidate_visible_bundle_decoder",
    "serialized_state_after_update_decoder",
    "feedback_history_only_strongest_decoder",
    "observation_plus_feedback_strongest_decoder",
    "query_action_plus_feedback_strongest_decoder",
    "legal_history_plus_feedback_strongest_decoder",
    "count_table",
    "graph_lookup",
    "transition_table",
    "successor_map",
    "fsm_planner",
    "episodic_traversal",
}


def _module():
    return importlib.import_module("gate4_replacement_001e_baseline_equivalence_adjudication_001a.core")


def test_pair_count_table_and_field_decoders_are_invoked_and_tie_candidate():
    core = _module()

    run = core.execute_adjudication(output_dir=None, persist_artifacts=False)
    baseline_report = run["baseline_equivalence_report"]
    decoder_report = run["decoder_probe_report"]

    assert run["candidate_score_readback"] == 1.0
    assert REQUIRED_BASELINES.issubset(set(baseline_report["invoked_baselines"]))
    assert baseline_report["scores"]["pair_count_table"] == run["candidate_score_readback"]
    assert baseline_report["scores"]["full_candidate_visible_bundle_decoder"] == run["candidate_score_readback"]
    assert baseline_report["scores"]["serialized_state_after_update_decoder"] == run["candidate_score_readback"]
    assert baseline_report["strongest_faithful_baseline"]["score"] == run["candidate_score_readback"]
    assert baseline_report["baseline_equivalence"] is True
    assert baseline_report["verdict"] == "baseline_equivalence_preserved_negative_evidence"
    assert decoder_report["probes"]["feedback_history_only_strongest_decoder"]["score"] == 1.0
    assert decoder_report["probes"]["observation_only_control"]["score"] == 0.25


def test_recoverability_interventions_use_actual_trace_material():
    core = _module()

    run = core.execute_adjudication(output_dir=None, persist_artifacts=False)
    report = run["recoverability_adjudication_report"]

    assert set(report["interventions"]) >= {
        "single_token_feedback_only",
        "full_two_token_feedback",
        "shuffled_feedback_pair",
        "counterfactual_feedback_pair",
        "serialized_state_field_removal",
        "feedback_history_removal",
        "observation_only_control",
    }
    assert report["interventions"]["single_token_feedback_only"]["pair_count_table_score"] == 0.5
    assert report["interventions"]["full_two_token_feedback"]["pair_count_table_score"] == 1.0
    assert report["interventions"]["shuffled_feedback_pair"]["pair_count_table_score"] == 1.0
    assert report["interventions"]["counterfactual_feedback_pair"]["pair_count_table_score"] == 0.0
    assert report["interventions"]["serialized_state_field_removal"]["serialized_state_after_update_decoder_score"] == 0.25
    assert report["interventions"]["feedback_history_removal"]["pair_count_table_score"] == 0.25
    assert report["candidate_advantage_survives_faithful_baselines"] is False
    assert report["stop_condition_triggered"] == "pair_count_table_tied_candidate"


def test_trace_probe_recomputes_from_visible_state_and_detects_corruption():
    core = _module()

    run = core.execute_adjudication(output_dir=None, persist_artifacts=False)
    report = run["trace_probe_report"]

    assert report["records_checked"] == 56
    assert report["serialized_state_replay_score"] == 1.0
    assert report["feedback_pair_replay_score"] == 1.0
    assert report["recomputed_from_serialized_state"] is True
    assert report["recomputed_from_feedback_history"] is True
    assert report["corruption_controls"]["removed_serialized_state_score"] == 0.25
    assert report["corruption_controls"]["removed_feedback_history_score"] == 0.25


def test_provenance_blocks_missing_baseline_invocation_and_static_score_injection():
    core = _module()

    run = core.execute_adjudication(output_dir=None, persist_artifacts=False)
    assert core.verify_required_baseline_invocations(run["baseline_equivalence_report"])["passed"] is True
    assert core.verify_provenance(run["provenance_report"])["passed"] is True

    missing = copy.deepcopy(run["baseline_equivalence_report"])
    missing["invoked_baselines"].remove("pair_count_table")
    assert core.verify_required_baseline_invocations(missing)["passed"] is False

    injected = copy.deepcopy(run["provenance_report"])
    injected["records"][0]["static_score_injection"] = True
    injected["records"][0]["producer_function"] = "static_json_literal"
    assert core.verify_provenance(injected)["passed"] is False


def test_source_boundary_non_mutation_and_downstream_flags_stay_false(tmp_path):
    core = _module()

    before = core.hash_protected_boundaries(ROOT)
    run = core.execute_adjudication(output_dir=tmp_path / TASK_ID, persist_artifacts=True)
    after = core.hash_protected_boundaries(ROOT)
    result = run["result"]

    assert before == after
    assert run["source_pin_readback"]["source_boundary_verified"] is True
    assert run["source_pin_readback"]["local_head"] == core.STARTING_BOUNDARY
    assert run["source_pin_readback"]["local_required_tag"] == core.STARTING_BOUNDARY
    assert run["source_pin_readback"]["remote_required_tag"] == core.STARTING_BOUNDARY
    assert run["non_mutation_guard"]["passed"] is True
    assert result["verdict"] == "baseline_equivalence_preserved_negative_evidence"
    assert result["positive_mechanism_evidence_allowed"] is False
    assert result["downstream_authorization_flags_all_false"] is True
    assert all(value is False for value in result["downstream_authorization_flags"].values())
    assert result["safe_to_enter_gate5"] is False
    assert result["safe_to_enter_admission"] is False
    assert result["safe_to_enter_bridge"] is False
    assert result["safe_to_enter_runtime"] is False
    assert result["safe_to_enter_ego_mainline"] is False


def test_materialized_artifacts_parse_after_main_run():
    core = _module()

    core.execute_adjudication(output_dir=ARTIFACT_DIR, persist_artifacts=True)

    names = {path.name for path in ARTIFACT_DIR.iterdir()}
    assert REQUIRED_ARTIFACTS.issubset(names)
    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt"}:
        json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))
    assert "bounded 001D toy harness" in (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8")
