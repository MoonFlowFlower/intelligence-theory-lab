import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "process_intervention_hard_distribution_001c_replay_gate_revision"
TASK_CARD = (
    ROOT
    / "docs"
    / "codex"
    / "tasks"
    / "PROCESS-INTERVENTION-HARD-DISTRIBUTION-001C-REPLAY-GATE-REVISION.md"
)

REQUIRED_ARTIFACTS = {
    "replay_gate_revision_result.json",
    "replay_control_taxonomy.json",
    "future_gate_semantics.json",
    "historical_verdict_preservation_note.txt",
    "claim_ceiling.txt",
}

REQUIRED_FUTURE_CONTROLS = {
    "online_count_statistic",
    "count_table",
    "graph_cache",
    "transition_table",
    "successor_map",
    "summary_retrieval",
    "behavior_only_replay",
    "target_free_generative_replay_challenger",
}

REQUIRED_FUTURE_ABLATIONS = {
    "learning_freeze",
    "history_replacement",
    "counterfactual_action_contrast",
    "outcome_perturbation_if_predeclared",
    "heldout_composition_evaluation",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_001c_artifacts_exist_parse_and_are_bounded():
    assert TASK_CARD.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})

    result = _read_json(ARTIFACT_DIR / "replay_gate_revision_result.json")
    taxonomy = _read_json(ARTIFACT_DIR / "replay_control_taxonomy.json")
    semantics = _read_json(ARTIFACT_DIR / "future_gate_semantics.json")

    assert result["task_id"] == "PROCESS-INTERVENTION-HARD-DISTRIBUTION-001C-REPLAY-GATE-REVISION"
    assert result["layer"] == "bounded replay-gate taxonomy revision only"
    assert result["claim_ceiling"] == "bounded replay-gate taxonomy revision only"
    assert taxonomy["claim_ceiling"] == result["claim_ceiling"]
    assert semantics["claim_ceiling"] == result["claim_ceiling"]
    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == result["claim_ceiling"]
    assert all(value is False for value in result["authorization_flags"].values())


def test_replay_control_taxonomy_is_explicit_and_trace_replay_is_hygiene():
    taxonomy = _read_json(ARTIFACT_DIR / "replay_control_taxonomy.json")
    classes = taxonomy["taxonomy"]

    assert set(classes) == {
        "trace_integrity_hygiene",
        "behavioral_replay_baseline",
        "target_free_generative_replay_challenger",
    }

    trace = classes["trace_integrity_hygiene"]
    assert trace["examples"] == ["trace_only_replay"]
    assert trace["counts_as_independent_mechanism_challenger"] is False
    assert trace["counts_as_trace_replay_hygiene"] is True
    assert trace["access_rules"]["may_read_committed_target_trace_records"] is True
    assert trace["access_rules"]["may_use_target_trace_to_generate_predictions"] is False
    assert trace["access_rules"]["may_block_mechanism_evidence_when_successful"] is False
    assert trace["pass_fail_semantics"]["success"] == "trace_integrity_valid_not_mechanism_equivalence"

    behavior = classes["behavioral_replay_baseline"]
    assert behavior["examples"] == ["behavior_only_replay"]
    assert behavior["counts_as_independent_mechanism_challenger"] is False
    assert behavior["may_claim_update_process_equivalence"] is False
    assert behavior["pass_fail_semantics"]["match"] == "weak_behavioral_warning_not_update_process_equivalence"


def test_target_free_generative_replay_challenger_forbids_target_trace_access():
    taxonomy = _read_json(ARTIFACT_DIR / "replay_control_taxonomy.json")
    challenger = taxonomy["taxonomy"]["target_free_generative_replay_challenger"]
    access = challenger["access_rules"]

    assert challenger["counts_as_independent_mechanism_challenger"] is True
    assert challenger["can_block_mechanism_evidence_if_it_matches"] is True
    assert access["may_read_committed_target_trace_records_for_evaluated_examples"] is False
    assert access["may_read_target_heldout_outcomes_before_prediction"] is False
    assert access["may_read_target_future_behaviors_before_prediction"] is False
    assert access["may_read_target_process_signatures_before_prediction"] is False
    assert access["predictions_must_be_committed_before_target_reveal"] is True
    assert access["target_trace_access_allowed_only_after_prediction_for_scoring"] is True


def test_future_gate_semantics_preserve_controls_ablations_and_thresholds():
    semantics = _read_json(ARTIFACT_DIR / "future_gate_semantics.json")

    assert set(semantics["required_future_fair_controls"]) == REQUIRED_FUTURE_CONTROLS
    assert set(semantics["required_future_ablations"]) == REQUIRED_FUTURE_ABLATIONS
    assert semantics["fair_controls_weakened_or_removed"] is False
    assert semantics["trace_replay_hygiene_weakened"] is False
    assert semantics["thresholds_changed_post_hoc"] is False
    assert semantics["new_mechanism_implemented"] is False

    pass_fail = semantics["future_pass_fail_semantics"]
    assert pass_fail["trace_only_replay_failure"] == "invalid_trace_replay_hygiene"
    assert pass_fail["trace_only_replay_success"] == "does_not_block_mechanism_evidence"
    assert pass_fail["behavioral_replay_match"] == "weak_behavioral_warning_not_update_process_equivalence"
    assert pass_fail["target_free_generative_replay_challenger_match"] == "can_block_mechanism_evidence"


def test_historical_001b_verdict_and_artifacts_are_preserved():
    result = _read_json(ARTIFACT_DIR / "replay_gate_revision_result.json")
    note = (ARTIFACT_DIR / "historical_verdict_preservation_note.txt").read_text(encoding="utf-8")

    assert result["historical_001b_verdict"] == "process_intervention_hard_distribution_001b_failed_fair_control_match"
    assert result["historical_001b_verdict_preserved"] is True
    assert result["does_not_rewrite_001b_verdict"] is True
    assert result["does_not_reinterpret_001b_as_pass"] is True
    assert result["does_not_remove_trace_only_replay_from_historical_failure_reasoning"] is True
    assert result["trace_only_replay_removed_from_historical_failure_condition"] is False
    assert result["historical_001b_pass_status"] == "not_pass"
    assert "not reclassified as pass" in note
    assert "trace_only_replay remains part of the historical 001B failure reasoning" in note

    for relative_path, expected_hash in result["frozen_prior_artifact_sha256"].items():
        assert _sha256(ROOT / relative_path) == expected_hash


def test_acceptance_gate_and_claim_limits_are_machine_readable():
    result = _read_json(ARTIFACT_DIR / "replay_gate_revision_result.json")
    semantics = _read_json(ARTIFACT_DIR / "future_gate_semantics.json")

    assert result["revision_type"] == "future_evidence_contract_wording_only"
    assert result["historical_gate_rewrite_authorized"] is False
    assert result["mechanism_execution_authorized"] is False
    assert result["mechanism_training_authorized"] is False
    assert result["acceptance_gate_status"] == {
        "replay_control_taxonomy_explicit": True,
        "trace_only_replay_classified_as_hygiene": True,
        "future_generative_replay_challenger_target_free": True,
        "historical_001b_verdict_unchanged": True,
        "old_artifacts_unmodified": True,
        "future_gate_semantics_machine_readable": True,
        "authorization_flags_all_false": True,
        "claim_ceiling_bounded_replay_gate_taxonomy_revision_only": True,
    }

    assert semantics["conditional_future_gate_recommendation"]["authorization_granted_by_001c"] is False
    assert semantics["conditional_future_gate_recommendation"]["condition"] == (
        "Only a separately authorized future process-intervention gate may instantiate this taxonomy."
    )
    assert result["what_this_does_not_prove"] == [
        "mechanism validity",
        "001B pass",
        "theory validity",
        "theory falsity",
        "Gate1 readiness",
        "bridge readiness",
        "EGO readiness",
        "agency",
        "consciousness",
        "companion readiness",
        "model-class reset necessity",
    ]
