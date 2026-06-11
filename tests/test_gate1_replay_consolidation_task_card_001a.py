import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "gate1_replay_consolidation_task_card_001a"
TASK_CARD = ROOT / "docs" / "codex" / "tasks" / "GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A.md"

TASK_ID = "GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A"
LAYER = "bounded Gate1 task-card drafting only"
CLAIM_CEILING = "bounded Gate1 replay/consolidation task-card readiness only"
VERDICT = "gate1_replay_consolidation_task_card_001a_bounded_pass"
FREEZE_ANCHOR = "6a83b9d"

REQUIRED_ARTIFACTS = {
    "task_card_result.json",
    "validation_matrix.json",
    "source_evidence_manifest.json",
    "claim_ceiling.txt",
    "GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A.md",
}
REQUIRED_SECTIONS = [
    "Problem definition",
    "Current stage",
    "Hypothesis",
    "Baseline families",
    "Ablations",
    "Trace / replay requirement",
    "Access and leakage controls",
    "Acceptance gate",
    "Claim ceiling",
    "Stop conditions",
    "Rollback plan",
    "Non-claims",
]
REQUIRED_BASELINES = {
    "retrieval / summary retrieval",
    "behavior-only replay",
    "trace-only replay as hygiene only",
    "online count/statistic controls",
    "transition table / successor map / graph cache controls",
    "target-free generative replay challenger",
    "frozen-history control",
    "no-consolidation control",
    "shuffled-replay control",
    "corrupted-replay control",
}
REQUIRED_ABLATIONS = {
    "learning freeze",
    "history replacement",
    "consolidation disabled",
    "replay order shuffled",
    "replay content corrupted",
    "heldout composition",
    "delayed-effect cases",
    "observable-key conflict cases",
    "partial-observability cases",
    "counterfactual action contrast",
}
ALLOWED_VERDICTS = {
    "gate1_replay_consolidation_task_card_001a_bounded_pass",
    "gate1_replay_consolidation_task_card_001a_failed_scope_leak",
    "gate1_replay_consolidation_task_card_001a_failed_missing_baselines",
    "gate1_replay_consolidation_task_card_001a_failed_missing_ablations",
    "gate1_replay_consolidation_task_card_001a_failed_claim_inflation",
    "gate1_replay_consolidation_task_card_001a_invalid_artifact_mutation",
}
NON_CLAIMS = {
    "Gate1 pass",
    "mechanism validity",
    "theory validity",
    "bridge readiness",
    "EGO readiness",
    "agency",
    "consciousness",
    "emotion",
    "companion readiness",
    "stable user benefit",
}


def _read_json(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def test_task_card_artifacts_exist_parse_and_are_bounded():
    assert TASK_CARD.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})

    result = _read_json("task_card_result.json")
    assert result["task_id"] == TASK_ID
    assert result["layer"] == LAYER
    assert result["verdict"] in ALLOWED_VERDICTS
    assert result["verdict"] == VERDICT
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["freeze_anchor"] == {
        "artifact": "PI-HD-ADMISSION-001",
        "commit": FREEZE_ANCHOR,
    }
    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING


def test_task_card_contains_required_sections_baselines_ablations_and_verdicts():
    result = _read_json("task_card_result.json")
    task_card_text = TASK_CARD.read_text(encoding="utf-8")
    artifact_card_text = (ARTIFACT_DIR / "GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A.md").read_text(
        encoding="utf-8"
    )

    assert artifact_card_text == task_card_text
    for section in REQUIRED_SECTIONS:
        assert f"## {section}" in task_card_text
        assert section in result["required_sections"]

    assert set(result["baseline_families"]) == REQUIRED_BASELINES
    assert set(result["ablations"]) == REQUIRED_ABLATIONS
    assert set(result["allowed_verdicts"]) == ALLOWED_VERDICTS


def test_access_controls_authorize_no_execution_or_old_artifact_mutation():
    result = _read_json("task_card_result.json")
    source_manifest = _read_json("source_evidence_manifest.json")

    assert result["gate1_task_card_drafted"] is True
    assert all(value is False for value in result["authorization_flags"].values())
    assert source_manifest["pi_hd_admission_anchor_commit"] == FREEZE_ANCHOR
    assert source_manifest["allowed_upstream_evidence_source"] == (
        "admitted process-intervention hard-distribution lineage only"
    )
    assert source_manifest["old_artifacts_modified"] is False
    assert source_manifest["gate1_execution_performed"] is False
    assert source_manifest["gate1_runtime_implemented"] is False
    assert source_manifest["new_mechanism_code_added"] is False
    assert source_manifest["historical_001b_reclassified_as_pass"] is False


def test_trace_only_replay_is_hygiene_only_and_not_mechanism_evidence():
    matrix = _read_json("validation_matrix.json")
    checks = {item["check_id"]: item for item in matrix["checks"]}

    assert checks["trace_only_replay_hygiene_only"]["passed"] is True
    assert checks["trace_only_replay_hygiene_only"]["counts_as_mechanism_evidence"] is False
    assert checks["trace_only_replay_hygiene_only"]["may_block_trace_integrity"] is True
    assert checks["required_baselines_complete"]["passed"] is True
    assert set(checks["required_baselines_complete"]["observed"]) == REQUIRED_BASELINES
    assert checks["required_ablations_complete"]["passed"] is True
    assert set(checks["required_ablations_complete"]["observed"]) == REQUIRED_ABLATIONS
    assert checks["claim_ceiling_bounded"]["passed"] is True
    assert checks["scope_did_not_expand"]["passed"] is True


def test_acceptance_gate_is_falsifiable_and_non_claims_are_explicit():
    result = _read_json("task_card_result.json")
    matrix = _read_json("validation_matrix.json")
    task_card_text = TASK_CARD.read_text(encoding="utf-8")

    assert matrix["acceptance_gate_status"] == "bounded_pass"
    assert matrix["verdict"] == VERDICT
    assert set(result["non_claims"]) == NON_CLAIMS
    assert result["acceptance_gate"]["falsifiable_gate1_execution_plan_defined"] is True
    assert result["acceptance_gate"]["artifact_requirements_defined"] is True
    assert result["acceptance_gate"]["leakage_controls_defined"] is True
    assert result["acceptance_gate"]["stop_conditions_defined"] is True
    assert result["acceptance_gate"]["rollback_plan_defined"] is True
    for non_claim in NON_CLAIMS:
        assert non_claim in task_card_text
