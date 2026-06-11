import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.path.join(str(ROOT), "src"))

from negative_evidence_admission_gate_001a import evaluate_successor_task


ARTIFACT_DIR = ROOT / "artifacts" / "negative_evidence_admission_gate_001a"
ALL_RULE_IDS = {
    "missing_001a_supersession",
    "missing_001b_fair_control_failure",
    "missing_001c_canonical_errata",
    "process_intervention_draft_pass_treated_as_executable",
    "verdict_string_tests_treated_as_acceptance",
    "gate1_replay_pass_ignores_graph_cache_collapse",
    "fable_causality_without_provenance_diff_mechanism",
}


def _read_fixture(name: str) -> str:
    return (ARTIFACT_DIR / name).read_text(encoding="utf-8")


def test_bad_successor_task_fails_all_known_false_confidence_rules():
    result = evaluate_successor_task(_read_fixture("bad_successor_task.txt"))

    assert result["task_id"] == "NEGATIVE-EVIDENCE-ADMISSION-GATE-001A"
    assert result["passed"] is False
    assert set(result["failure_ids"]) == ALL_RULE_IDS
    assert result["claim_ceiling"] == (
        "bounded successor-task admission guard against known false-confidence risks"
    )


def test_properly_cited_successor_task_passes():
    result = evaluate_successor_task(_read_fixture("properly_cited_successor_task.txt"))

    assert result["passed"] is True
    assert result["failure_ids"] == []
    assert set(result["checked_rules"]) == ALL_RULE_IDS


def test_result_artifact_matches_gate_output():
    artifact = json.loads((ARTIFACT_DIR / "result.json").read_text(encoding="utf-8"))

    bad_result = evaluate_successor_task(_read_fixture("bad_successor_task.txt"))
    proper_result = evaluate_successor_task(_read_fixture("properly_cited_successor_task.txt"))

    assert artifact["task_id"] == "NEGATIVE-EVIDENCE-ADMISSION-GATE-001A"
    assert artifact["bad_successor_task_result"] == bad_result
    assert artifact["properly_cited_successor_task_result"] == proper_result


def test_no_old_artifact_rewrite_authorized():
    artifact = json.loads((ARTIFACT_DIR / "result.json").read_text(encoding="utf-8"))

    assert artifact["old_artifacts_modified"] is False
    assert artifact["experiments_rerun"] is False
    assert artifact["new_theory_introduced"] is False
    assert artifact["claim_ceiling"] == (
        "bounded successor-task admission guard against known false-confidence risks"
    )
