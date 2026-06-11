import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "pi_hd_admission_001"

CLAIM_CEILING = "bounded Gate1 task-card drafting admission only"
VERDICT = "pi_hd_admission_001_gate1_drafting_admitted"
REQUIRED_ARTIFACTS = {
    "admission_result.json",
    "evidence_matrix.json",
    "blocker_checklist.json",
    "gate1_drafting_authorization.json",
    "claim_ceiling.txt",
    "PI-HD-ADMISSION-001.md",
}
ALLOWED_VERDICTS = {
    "pi_hd_admission_001_gate1_drafting_admitted",
    "pi_hd_admission_001_blocked_by_witness_check_failure",
    "pi_hd_admission_001_blocked_by_replay_or_leakage",
    "pi_hd_admission_001_blocked_by_control_equivalence",
    "pi_hd_admission_001_invalid_artifact_mutation",
    "pi_hd_admission_001_insufficient_evidence",
}


def _read_json(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def test_admission_artifacts_exist_parse_and_are_bounded():
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    result = _read_json("admission_result.json")

    assert result["task_id"] == "PI-HD-ADMISSION-001"
    assert result["layer"] == "bounded Gate1 task-card drafting admission decision only"
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == VERDICT
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING
    assert result["gate1_task_card_drafting_admitted"] is True
    assert result["gate1_execution_authorized"] is False
    assert result["gate1_implementation_authorized"] is False


def test_required_checks_all_pass_without_rewriting_historical_evidence():
    matrix = _read_json("evidence_matrix.json")
    checks = {item["check_id"]: item for item in matrix["required_checks"]}

    assert checks["001b_historical_verdict_remains_failed"]["passed"] is True
    assert checks["001b_historical_verdict_remains_failed"]["evidence_value"] == (
        "process_intervention_hard_distribution_001b_failed_fair_control_match"
    )
    assert checks["001d_did_not_rewrite_001b"]["passed"] is True
    assert checks["old_artifacts_match_anchors"]["passed"] is True
    assert checks["phase_a_target_free_allowlist_firewall"]["passed"] is True
    assert checks["prediction_commit_frozen_before_reveal_unchanged_after_evaluation"]["passed"] is True
    assert checks["challenger_metrics_zero_not_witness_performance"]["passed"] is True
    assert checks["trace_only_replay_hygiene_only"]["passed"] is True
    assert checks["non_replay_controls_non_equivalent"]["passed"] is True
    assert checks["witness_ablation_heldout_process_checks_sufficient_under_current_gate"]["passed"] is True
    assert checks["authorization_limited_to_gate1_task_card_drafting"]["passed"] is True


def test_blocker_checklist_has_no_blockers_and_preserves_claim_limits():
    blockers = _read_json("blocker_checklist.json")

    assert blockers["verdict"] == VERDICT
    assert blockers["blocking_items"] == []
    assert blockers["stop_conditions_triggered"] == []
    for item in blockers["checks"]:
        assert item["status"] == "clear"
    assert blockers["claim_ceiling"] == CLAIM_CEILING
    assert blockers["what_this_does_not_authorize"] == [
        "Gate1 execution",
        "Gate1 implementation",
        "001B pass reclassification",
        "001E",
        "new replay taxonomy",
        "new baselines",
        "same-agent bridge",
        "EGO mainline",
        "mechanism tournament",
    ]


def test_gate1_drafting_authorization_is_narrow_and_machine_readable():
    authorization = _read_json("gate1_drafting_authorization.json")

    assert authorization["authorization_scope"] == "Gate1 task-card drafting only"
    assert authorization["gate1_task_card_drafting_authorized"] is True
    assert authorization["gate1_execution_authorized"] is False
    assert authorization["gate1_implementation_authorized"] is False
    assert authorization["same_agent_bridge_authorized"] is False
    assert authorization["ego_mainline_authorized"] is False
    assert authorization["mechanism_tournament_authorized"] is False
    assert authorization["allowed_next_artifact"] == "Gate1 task card draft"
    assert authorization["must_preserve_claim_ceiling"] == CLAIM_CEILING


def test_markdown_report_states_admission_without_claim_inflation():
    text = (ARTIFACT_DIR / "PI-HD-ADMISSION-001.md").read_text(encoding="utf-8")

    assert "# PI-HD-ADMISSION-001" in text
    assert VERDICT in text
    assert "Gate1 task-card drafting only" in text
    assert "does not authorize Gate1 execution" in text
    assert "001D challenger metrics are not witness performance metrics" in text
    assert CLAIM_CEILING in text
