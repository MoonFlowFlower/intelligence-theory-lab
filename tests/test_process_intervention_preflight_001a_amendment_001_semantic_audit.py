import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = (
    ROOT
    / "artifacts"
    / "process_intervention_preflight_001a_amendment_001_independent_semantic_audit"
)

REQUIRED_ARTIFACTS = {
    "semantic_audit_result.json",
    "semantic_audit_matrix.json",
    "false_pass_channel_findings.jsonl",
    "source_citation_map.json",
    "final_report.md",
    "claim_ceiling.txt",
}

EXPECTED_A_KEYS = {f"A{i}" for i in range(1, 12)}
EXPECTED_FALSE_PASS_CHANNELS = {
    "name_only_controls",
    "hardcoded_competence_or_fairness",
    "undefined_match_metric",
    "per_intervention_instantiation_missing",
    "graph_cache_intervention_label_ambiguity",
    "resource_budget_ambiguity",
    "self_attested_acceptance",
    "verdict_string_tests",
}


def _read_json(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def test_semantic_audit_required_outputs_exist_and_parse():
    for artifact_name in REQUIRED_ARTIFACTS:
        assert (ARTIFACT_DIR / artifact_name).exists(), artifact_name

    _read_json("semantic_audit_result.json")
    _read_json("semantic_audit_matrix.json")
    _read_json("source_citation_map.json")

    line_count = 0
    for line in (ARTIFACT_DIR / "false_pass_channel_findings.jsonl").read_text(
        encoding="utf-8"
    ).splitlines():
        line_count += 1
        json.loads(line)
    assert line_count >= len(EXPECTED_FALSE_PASS_CHANNELS)


def test_semantic_audit_result_blocks_current_missing_support_artifacts():
    result = _read_json("semantic_audit_result.json")

    assert result["task_id"] == (
        "PROCESS-INTERVENTION-PREFLIGHT-001A-AMENDMENT-001-"
        "INDEPENDENT-SEMANTIC-AUDIT"
    )
    assert result["verdict"] == "semantic_audit_blocked_missing_amendment_support_artifacts"
    assert result["semantic_pass"] is False
    assert "missing_amendment_support_artifacts" in result["stop_conditions"]
    assert result["missing_support_artifact_count"] >= 18
    assert result["claim_ceiling"] == (
        "bounded independent semantic audit of AMENDMENT-001 executable false-pass closure only"
    )
    assert result["old_artifacts_modified"] is False
    assert result["experiments_rerun"] is False
    assert result["old_artifact_repair_attempted"] is False
    assert result["new_theory_introduced"] is False
    assert result["fable_causality_claimed"] is False


def test_semantic_audit_matrix_covers_a1_to_a11_and_false_pass_channels():
    matrix = _read_json("semantic_audit_matrix.json")

    assert set(matrix["amendment_checks"]) == EXPECTED_A_KEYS
    assert EXPECTED_FALSE_PASS_CHANNELS.issubset(set(matrix["false_pass_channels"]))

    assert matrix["amendment_checks"]["A1"]["semantic_status"] in {
        "blocked_missing_support_artifacts",
        "open",
    }
    assert matrix["amendment_checks"]["A3"]["semantic_status"] in {
        "blocked_missing_support_artifacts",
        "open",
    }
    assert matrix["false_pass_channels"]["undefined_match_metric"]["status"] != "closed"
    assert matrix["false_pass_channels"]["self_attested_acceptance"]["status"] != "closed"


def test_semantic_audit_report_keeps_lexical_gate_bounded():
    report = (ARTIFACT_DIR / "final_report.md").read_text(encoding="utf-8")

    assert "lexical admission pass is not mechanism evidence" in report
    assert "not executable implementation authorization" in report
    assert "not proof that AMENDMENT-001 closes executable false-pass channels" in report
    assert "semantic_audit_blocked_missing_amendment_support_artifacts" in report


def test_semantic_audit_does_not_mutate_amendment_or_old_artifacts():
    citation_map = _read_json("source_citation_map.json")
    result = _read_json("semantic_audit_result.json")

    assert result["amendment_modified_by_this_audit"] is False
    assert result["protected_001c_files_modified_by_this_audit"] is False
    assert result["old_artifacts_modified"] is False
    assert citation_map["source_files_read"]
    assert all("snippet" in entry for entry in citation_map["citations"])
