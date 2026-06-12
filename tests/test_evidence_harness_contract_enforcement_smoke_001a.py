import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EVIDENCE-HARNESS-CONTRACT-ENFORCEMENT-SMOKE-001A"
ARTIFACT_DIR = ROOT / "artifacts" / "evidence_harness_contract_enforcement_smoke_001a"
CLAIM_CEILING = "bounded evidence-harness contract enforcement smoke only"
TARGET_HEAD = "b11424652c791fd9153322db77d959c3c0cdacac"

REQUIRED_ARTIFACTS = {
    "contract_input_inventory.json",
    "known_false_pass_input_inventory.json",
    "synthetic_positive_control_fixtures.json",
    "enforcement_rule_manifest.json",
    "gate4_001b_enforcement_report.json",
    "positive_control_enforcement_report.json",
    "negative_control_or_scope_control_report.json",
    "rejection_reason_matrix.json",
    "result.json",
    "claim_ceiling.txt",
    "execution_manifest.json",
    "json_parse_verification.json",
}


def _runner():
    from evidence_harness_contract_enforcement_smoke_001a import runner

    return runner


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_positive_control_fixture_rejected_by_detected_patterns_not_denylist():
    runner = _runner()
    bundle = runner.build_synthetic_positive_control_bundle()

    report = runner.evaluate_bundle(bundle)

    assert report["admissibility_class"] == "rejected_false_pass_risk"
    assert report["positive_controls_detected"] is True
    assert report["static_denylist_only"] is False
    assert "synthetic_false_pass_fixture" in report["inspected_paths"]
    assert len(report["rejection_reasons"]) >= 4
    assert {
        "pass_shaped_result_fields",
        "static_score_or_perfect_score_literal",
        "unconditional_verified_or_real_intervention_true",
        "hash_or_stored_value_replay_shortcut",
        "leakage_scan_gap_or_broad_whitelist",
        "output_shape_only_test_assertion",
    }.issubset(set(report["detected_pattern_categories"]))
    assert report["producer_function"] == "evaluate_bundle"
    assert report["rule_ids_invoked"]


def test_gate4_001b_real_bundle_is_not_admissible_and_not_static_denylist():
    runner = _runner()
    bundle = runner.build_gate4_001b_inventory(ROOT)

    report = runner.evaluate_bundle(bundle)

    assert report["admissibility_class"] in {
        "rejected_false_pass_risk",
        "blocked_pending_audit",
    }
    assert report["admissibility_class"] != "admissible_downstream_evidence"
    assert report["static_denylist_only"] is False
    assert len(report["detected_pattern_categories"]) >= 2
    assert any(path.endswith("result.json") for path in report["inspected_paths"])
    assert any(path.endswith("tests/test_ego_mainline_gate4_preflight_executable_001b.py") for path in report["inspected_paths"])
    assert not any(reason["rule_id"] == "static_task_id_denylist" for reason in report["rejection_reasons"])


def test_gate4_task_id_without_detected_features_does_not_reject_by_denylist():
    runner = _runner()
    bundle = {
        "bundle_id": "gate4_task_id_scope_control",
        "task_id": "EGO-MAINLINE-GATE4-PREFLIGHT-EXECUTABLE-001B",
        "path_payloads": [
            {
                "path": "synthetic/minimal_metadata.json",
                "kind": "json",
                "payload": {"task_id": "EGO-MAINLINE-GATE4-PREFLIGHT-EXECUTABLE-001B"},
            }
        ],
    }

    report = runner.evaluate_bundle(bundle)

    assert report["admissibility_class"] == "blocked_pending_audit"
    assert report["static_denylist_only"] is False
    assert report["detected_pattern_categories"] == []


def test_governance_anchor_scope_control_classifies_differently_from_false_pass():
    runner = _runner()

    false_pass = runner.evaluate_bundle(runner.build_synthetic_positive_control_bundle())
    scope_control = runner.evaluate_bundle(runner.build_governance_anchor_scope_control_bundle())

    assert false_pass["admissibility_class"] == "rejected_false_pass_risk"
    assert scope_control["admissibility_class"] == "governance_anchor_only"
    assert scope_control["admissibility_class"] != false_pass["admissibility_class"]
    assert scope_control["detected_pattern_categories"] == []
    assert scope_control["positive_controls_detected"] is False


def test_run_smoke_writes_required_artifacts_and_false_authorization_flags(tmp_path):
    runner = _runner()
    out = tmp_path / "smoke_artifacts"

    result = runner.run_smoke(repo_root=ROOT, output_dir=out)

    assert result["task_id"] == TASK_ID
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["starting_head"] == TARGET_HEAD
    assert result["contract_anchor_commit"] == TARGET_HEAD
    assert result["gate4_001b_admissibility_class"] in {
        "rejected_false_pass_risk",
        "blocked_pending_audit",
    }
    assert result["gate4_001b_admissibility_class"] != "admissible_downstream_evidence"
    assert result["positive_control_detected"] is True
    assert result["static_denylist_only"] is False
    assert result["negative_or_scope_control_class"] == "governance_anchor_only"
    assert result["downstream_entry_authorized"] is False
    assert result["gate4_001c_authorized"] is False
    assert result["gate5_authorized"] is False
    assert result["admission_authorized"] is False
    assert result["runtime_authorized"] is False
    assert result["bridge_authorized"] is False
    assert REQUIRED_ARTIFACTS == {path.name for path in out.iterdir()}
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING

    for path in out.glob("*.json"):
        _load_json(path)

    gate4 = _load_json(out / "gate4_001b_enforcement_report.json")
    positive = _load_json(out / "positive_control_enforcement_report.json")
    scope = _load_json(out / "negative_control_or_scope_control_report.json")
    verification = _load_json(out / "json_parse_verification.json")

    assert gate4["static_denylist_only"] is False
    assert positive["positive_controls_detected"] is True
    assert scope["admissibility_class"] == "governance_anchor_only"
    assert verification["parse_status"] == "all_required_json_parsed"
