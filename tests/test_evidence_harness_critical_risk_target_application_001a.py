import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EVIDENCE-HARNESS-CRITICAL-RISK-TARGET-APPLICATION-001A"
TASK_DOC = ROOT / "docs" / "codex" / "tasks" / f"{TASK_ID}.md"
ARTIFACT_DIR = ROOT / "artifacts" / "evidence_harness_critical_risk_target_application_001a"
CLAIM_CEILING = (
    "bounded conservative application of evidence-harness enforcement to historical "
    "critical-risk targets only"
)
STARTING_HEAD = "69aa22dc83b60444a2e759135990435c4dcfa79b"

REQUIRED_TARGETS = {
    "ego_mainline_gate4_preflight_001b",
    "gate2_controllability_self_boundary_001b",
    "gate3_viability_functional_affect_001b",
    "gate4_social_latent_inference_001b",
    "gate4_social_representational_gap_preflight_001b",
    "r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b",
    "r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b",
    "representational_gap_preflight",
    "representational_gap_preflight_001b",
    "gate1_replay_consolidation_001c",
    "process_intervention_hard_distribution_001b",
    "process_intervention_hard_distribution_001b_trace_replay_rca_001a",
}

REQUIRED_ARTIFACTS = {
    "target_inventory.json",
    "target_input_bundle_manifest.json",
    "enforcer_invocation_report.json",
    "target_classification_matrix.json",
    "computed_provenance_report.json",
    "static_dependency_audit_report.json",
    "downstream_quarantine_matrix.json",
    "historical_false_pass_contamination_report.json",
    "semantic_gap_impact_report.json",
    "result.json",
    "claim_ceiling.txt",
    "execution_manifest.json",
    "json_parse_verification.json",
}

ALLOWED_CLASSES = {
    "rejected_false_pass_risk",
    "blocked_pending_audit",
    "insufficient_visibility",
    "governance_reference_only",
    "quarantined_from_downstream_use",
}


def _runner():
    from evidence_harness_critical_risk_target_application_001a import runner

    return runner


def _read_json(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def test_run_application_writes_required_bounded_outputs(tmp_path):
    runner = _runner()
    out = tmp_path / "critical_risk_application"

    result = runner.run_application(repo_root=ROOT, output_dir=out)

    assert result["task_id"] == TASK_ID
    assert result["starting_head"] == STARTING_HEAD
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["target_count"] == len(REQUIRED_TARGETS)
    assert result["evaluated_or_insufficient_visibility_count"] == len(REQUIRED_TARGETS)
    assert result["admissible_downstream_evidence_count"] == 0
    assert result["target_classification_failures"] == []
    assert result["semantic_gap_limitations_propagated"] is True
    assert result["static_denylist_only"] is False
    assert all(
        result[key] is False
        for key in [
            "downstream_entry_authorized",
            "gate4_001c_authorized",
            "gate5_authorized",
            "admission_authorized",
            "runtime_authorized",
            "bridge_authorized",
        ]
    )
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in out.iterdir()})
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING

    for path in out.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))


def test_artifact_matrix_classifies_every_required_target_without_positive_admission():
    matrix = _read_json("target_classification_matrix.json")
    inventory = _read_json("target_inventory.json")
    bundle_manifest = _read_json("target_input_bundle_manifest.json")
    invocation = _read_json("enforcer_invocation_report.json")

    rows = matrix["rows"]
    by_id = {row["target_id"]: row for row in rows}
    assert set(by_id) == REQUIRED_TARGETS
    assert set(inventory["required_target_ids"]) == REQUIRED_TARGETS
    assert set(bundle_manifest["targets"]) == REQUIRED_TARGETS
    assert invocation["enforcer_producer_function"] == "evaluate_bundle"
    assert invocation["invocation_count"] == len(REQUIRED_TARGETS)

    for target_id, row in by_id.items():
        assert row["classification"] in ALLOWED_CLASSES
        assert row["classification"] != "admissible_downstream_evidence"
        assert row["downstream_admissibility_result"] == "quarantined_from_downstream_use"
        assert row["callable_enforcer_invoked"] is True
        assert row["producer_function"] == "classify_target"
        assert row["run_id"]
        assert row["source_code_hash"]
        assert row["aggregation_rule"]
        assert row["static_denylist_was_involved"] is False
        assert row["result_depended_on_task_id"] is False
        assert row["score_baseline_ablation_replay_evidence_status"] in {
            "self_reported_or_partial_callable_visibility",
            "insufficient_visibility",
        }
        assert bundle_manifest["targets"][target_id]["input_artifacts"] or row[
            "classification"
        ] == "insufficient_visibility"


def test_computed_provenance_and_static_dependency_reports_are_real_computation():
    provenance = _read_json("computed_provenance_report.json")
    static_report = _read_json("static_dependency_audit_report.json")

    assert provenance["producer_function"] == "run_application"
    assert provenance["classification_producer_function"] == "classify_target"
    assert provenance["target_count"] == len(REQUIRED_TARGETS)
    assert provenance["computed_not_literal"] is True
    assert provenance["hard_coded_target_verdicts_used"] is False
    assert provenance["input_artifact_count"] >= len(REQUIRED_TARGETS)
    assert all(
        entry["producer_function"] == "classify_target"
        and entry["input_artifacts"]
        and entry["run_id"]
        and entry["source_code_hash"]
        for entry in provenance["target_provenance"]
        if entry["classification"] != "insufficient_visibility"
    )

    assert static_report["static_denylist_only"] is False
    assert static_report["targets_with_task_id_dependency"] == []
    assert static_report["targets_with_static_hash_dependency"] == []
    assert static_report["targets_with_static_path_dependency"] == []
    assert static_report["control_method"] == "retask input bundle and compare class/categories"


def test_semantic_gap_and_downstream_quarantine_are_propagated():
    semantic = _read_json("semantic_gap_impact_report.json")
    quarantine = _read_json("downstream_quarantine_matrix.json")
    contamination = _read_json("historical_false_pass_contamination_report.json")
    result = _read_json("result.json")

    assert semantic["semantic_gap_limitations_propagated"] is True
    assert {
        "renamed_or_semantic_claims_default_to_blocked_visibility",
        "baseline_callable_absence_not_detected_without_pass_shaped_fields",
    }.issubset({gap["gap_id"] for gap in semantic["inherited_001b_gap_ids"]})
    assert semantic["claim_ceiling"] == CLAIM_CEILING

    assert set(quarantine["targets"]) == REQUIRED_TARGETS
    assert all(row["downstream_entry_authorized"] is False for row in quarantine["rows"])
    assert all(
        row["downstream_admissibility_result"] == "quarantined_from_downstream_use"
        for row in quarantine["rows"]
    )
    assert contamination["prior_triage_source"] == (
        "artifacts/cross_gate_score_credibility_triage_001a"
    )
    assert contamination["target_count"] == len(REQUIRED_TARGETS)
    assert result["what_this_does_not_prove"]


def test_missing_target_input_failure_path_is_insufficient_visibility():
    runner = _runner()

    row = runner.classify_target(
        repo_root=ROOT,
        target={"target_id": "missing_target_for_failure_path", "path_aliases": []},
        run_id="test-run",
        prior_risk={"risk_class": "critical_risk_false_pass_pattern_detected"},
    )

    assert row["classification"] == "insufficient_visibility"
    assert row["callable_enforcer_invoked"] is False
    assert row["downstream_admissibility_result"] == "quarantined_from_downstream_use"
    assert row["input_artifacts"] == []
    assert "no_input_artifacts_visible" in row["classification_reasons"]


def test_task_doc_preserves_scope_and_claim_ceiling():
    doc = TASK_DOC.read_text(encoding="utf-8")

    assert TASK_ID in doc
    assert CLAIM_CEILING in doc
    assert "Not Gate repair." in doc
    assert "Not mechanism validation." in doc
    assert "Forbidden classification: `admissible_downstream_evidence`" in doc
