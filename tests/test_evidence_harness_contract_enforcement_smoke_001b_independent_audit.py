import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EVIDENCE-HARNESS-CONTRACT-ENFORCEMENT-SMOKE-001B-INDEPENDENT-AUDIT"
TASK_DOC = ROOT / "docs" / "codex" / "tasks" / f"{TASK_ID}.md"
ARTIFACT_DIR = (
    ROOT
    / "artifacts"
    / "evidence_harness_contract_enforcement_smoke_001b_independent_audit"
)
CLAIM_CEILING = "bounded independent audit of evidence-harness enforcement smoke only"
STARTING_HEAD = "5b4cdbeedb380aafa8da9ead827e1b40b04d8153"
BRANCH = "codex/meta-theory-scaffold"

REQUIRED_ARTIFACTS = {
    "audited_enforcer_inventory.json",
    "adversarial_fixture_manifest.json",
    "black_box_invocation_report.json",
    "bypass_attempt_report.json",
    "static_denylist_audit_report.json",
    "source_pattern_audit_report.json",
    "test_quality_audit_report.json",
    "contract_coverage_gap_report.json",
    "adversarial_result_matrix.json",
    "result.json",
    "claim_ceiling.txt",
    "execution_manifest.json",
    "json_parse_verification.json",
}

ADVERSARIAL_FIXTURES = {
    "renamed_pass_fields_fixture",
    "result_json_leakage_fixture",
    "soft_claim_language_fixture",
    "baseline_shadow_fixture",
    "ablation_label_only_fixture",
    "hash_only_replay_fixture",
    "whitelist_bypass_fixture",
}


def _runner():
    from evidence_harness_contract_enforcement_smoke_001b_independent_audit import runner

    return runner


def _read_json(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def test_run_audit_writes_required_outputs_and_bounded_result(tmp_path):
    runner = _runner()
    out = tmp_path / "audit_artifacts"

    result = runner.run_audit(repo_root=ROOT, output_dir=out)

    assert result["task_id"] == TASK_ID
    assert result["layer"] == "engineering implementation + evidence-harness audit"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["starting_head"] == STARTING_HEAD
    assert result["audited_commit"] == STARTING_HEAD
    assert result["branch"] == BRANCH
    assert result["adversarial_fixture_count"] == len(ADVERSARIAL_FIXTURES)
    assert result["adversarial_fixtures_rejected_or_blocked_count"] == len(
        ADVERSARIAL_FIXTURES
    )
    assert result["adversarial_fixture_failures"] == []
    assert result["negative_control_class"] == "governance_anchor_only"
    assert result["static_denylist_only"] is False
    assert result["verdict"] in {
        "independent_audit_passed_bounded_enforcer_no_obvious_bypass",
        "independent_audit_failed_bypass_detected",
        "independent_audit_blocked_insufficient_visibility",
    }
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

    for path in out.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))


def test_generated_fixture_matrix_invokes_001a_enforcer_for_each_fixture():
    matrix = _read_json("adversarial_result_matrix.json")
    invocation = _read_json("black_box_invocation_report.json")
    manifest = _read_json("adversarial_fixture_manifest.json")

    assert set(manifest["adversarial_fixture_ids"]) == ADVERSARIAL_FIXTURES
    assert manifest["negative_control_fixture_id"] == "governance_anchor_negative_control"
    assert len(invocation["invocations"]) == len(ADVERSARIAL_FIXTURES) + 1
    assert invocation["enforcer_producer_function"] == "evaluate_bundle"
    assert invocation["enforcer_source_path"] == (
        "src/evidence_harness_contract_enforcement_smoke_001a/runner.py"
    )

    by_id = {row["fixture_id"]: row for row in matrix["rows"]}
    assert set(by_id) == ADVERSARIAL_FIXTURES | {"governance_anchor_negative_control"}

    for fixture_id in ADVERSARIAL_FIXTURES:
        row = by_id[fixture_id]
        assert row["actual_class"] in {
            "rejected_false_pass_risk",
            "blocked_pending_audit",
        }
        assert row["actual_class"] != "admissible_downstream_evidence"
        assert row["accepted_incorrectly"] is False
        assert row["black_box_callable_invoked"] is True
        assert row["result_depended_on_task_id"] is False
        assert row["rule_ids_invoked"]

    assert by_id["governance_anchor_negative_control"]["actual_class"] == (
        "governance_anchor_only"
    )
    assert any(
        by_id[fixture_id]["actual_class"] == "blocked_pending_audit"
        for fixture_id in ADVERSARIAL_FIXTURES
    )


def test_static_denylist_and_source_pattern_audits_are_not_self_attested():
    static_report = _read_json("static_denylist_audit_report.json")
    source_report = _read_json("source_pattern_audit_report.json")

    assert static_report["static_denylist_only"] is False
    assert static_report["decision_depends_only_on_task_id"] is False
    assert static_report["decision_depends_only_on_commit_hash"] is False
    assert static_report["decision_depends_only_on_file_path"] is False
    assert static_report["task_id_control_actual_class"] == "blocked_pending_audit"
    assert static_report["known_static_references_present"] is True
    assert "evaluate_bundle" in static_report["audited_callable"]

    assert source_report["source_file"] == (
        "src/evidence_harness_contract_enforcement_smoke_001a/runner.py"
    )
    assert source_report["uses_json_key_value_pattern_scan"] is True
    assert source_report["scans_general_string_values_for_claims"] is False
    assert source_report["renamed_field_gap"] is True
    assert source_report["baseline_invocation_gap"] is True
    assert source_report["hash_only_replay_gap"] in {True, False}
    assert source_report["claim_ceiling"] == CLAIM_CEILING


def test_001a_test_quality_audit_records_coverage_and_gaps():
    quality = _read_json("test_quality_audit_report.json")
    gaps = _read_json("contract_coverage_gap_report.json")

    checks = quality["checks"]
    assert checks["callable_enforcer_invocation"]["covered"] is True
    assert checks["synthetic_positive_control"]["covered"] is True
    assert checks["real_gate4_001b_rejection_path"]["covered"] is True
    assert checks["scope_negative_control"]["covered"] is True
    assert checks["failure_path_when_positive_controls_absent"]["covered"] is False
    assert checks["failure_path_when_static_denylist_only_logic_is_used"]["covered"] in {
        False,
        "partial",
    }
    assert quality["test_quality_risk"] in {"low", "medium", "high"}
    assert quality["mostly_asserts_final_verdict_only"] is False

    assert gaps["contract_coverage_gaps"]
    assert "renamed_or_semantic_claims_default_to_blocked_visibility" in {
        gap["gap_id"] for gap in gaps["contract_coverage_gaps"]
    }


def test_task_doc_and_generated_artifacts_preserve_non_authorization():
    result = _read_json("result.json")
    verification = _read_json("json_parse_verification.json")
    doc = TASK_DOC.read_text(encoding="utf-8")

    assert TASK_ID in doc
    assert CLAIM_CEILING in doc
    assert "This is not a Gate repair task." in doc
    assert "do not modify the 001A enforcer source" in doc
    assert "downstream_entry_authorized`: false" in doc

    assert verification["parse_status"] == "all_required_json_parsed"
    assert set(REQUIRED_ARTIFACTS - {"claim_ceiling.txt"}).issubset(
        set(verification["parsed_json_files"])
    )
    assert result["json_parse_verification"]["status"] == "all_required_json_parsed"
    assert result["what_this_does_not_prove"]
    assert "Gate4 001C authorization" in result["what_this_does_not_prove"]
