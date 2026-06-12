import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "codex" / "contracts" / "COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md"
ARTIFACT_DIR = ROOT / "artifacts" / "computed_evidence_provenance_contract_001a"

REQUIRED_SECTIONS = [
    "## 1. Task Identity",
    "## 2. Scope and Non-Authorization Flags",
    "## 3. Problem Definition",
    "## 4. Failure Mode Addressed",
    "## 5. Computed-Evidence Provenance Rule",
    "## 6. Required Metric Provenance Schema",
    "## 7. Baseline Implementation Requirements",
    "## 8. Ablation Implementation Requirements",
    "## 9. Contrast Implementation Requirements",
    "## 10. Leakage Scanner Requirements",
    "## 11. Replay and Behavior-Causal Replay Requirements",
    "## 12. Frozen Input Consumption Requirements",
    "## 13. Candidate Serialized-State Causal Path Requirements",
    "## 14. Test Requirements",
    "## 15. Forbidden Anti-Patterns",
    "## 16. Required Blocker Verdicts for Future Executable Tasks",
    "## 17. Adoption Rule for Future Executable Task Cards",
    "## 18. Claim Ceiling",
    "## 19. What This Standard Cannot Prove",
]

REQUIRED_METRIC_FIELDS = {
    "metric_id",
    "metric_name",
    "producer_function",
    "producer_module",
    "code_path_hash",
    "run_id",
    "episode_ids",
    "seed_ids",
    "train_context_ids_consumed",
    "heldout_context_ids_consumed",
    "counterfactual_pair_ids_consumed",
    "input_artifact_paths",
    "input_artifact_hashes",
    "input_row_count",
    "output_artifact_path",
    "output_row_ids",
    "aggregation_rule",
    "threshold_used",
    "threshold_frozen_before_run",
    "computed_not_literal",
    "failure_path_available",
}

REQUIRED_BLOCKERS = {
    "failed_computed_evidence_provenance",
    "failed_literal_metric_detected",
    "failed_static_baseline_detected",
    "failed_ablation_not_rerun",
    "failed_unconditional_leakage_clean",
    "failed_replay_not_behavior_causal",
    "failed_unused_frozen_input",
    "failed_candidate_not_using_serialized_state",
    "failed_missing_metric_provenance",
    "failed_positive_control_missing",
    "failed_baseline_invocation_missing",
    "failed_ablation_invocation_missing",
    "failed_claim_inflation",
    "failed_scope_leak",
}

FALSE_POSITIVE_PATTERNS = {
    "constants_as_metrics",
    "static_baseline_dictionaries",
    "static_ablation_dictionaries",
    "unconditional_leakage_clean_reports",
    "hash_only_replay",
    "unused_frozen_inputs",
    "candidate_behavior_not_consuming_serialized_state",
    "tests_that_assert_pass_rather_than_computation_path",
}

EXPECTED_ARTIFACTS = {
    "result.json",
    "requirement_matrix.json",
    "anti_pattern_matrix.json",
    "adoption_instructions.json",
    "claim_ceiling.txt",
}


def _read_json(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def test_contract_contains_required_sections_in_order():
    text = DOC.read_text(encoding="utf-8")
    offsets = []

    for section in REQUIRED_SECTIONS:
        assert section in text
        offsets.append(text.index(section))

    assert offsets == sorted(offsets)


def test_metric_schema_and_blocker_verdicts_are_machine_represented():
    text = DOC.read_text(encoding="utf-8")
    matrix = _read_json("requirement_matrix.json")
    adoption = _read_json("adoption_instructions.json")

    assert set(matrix["metric_provenance_required_fields"]) == REQUIRED_METRIC_FIELDS
    assert set(matrix["required_blocker_verdicts"]) == REQUIRED_BLOCKERS
    assert set(adoption["required_blocker_verdicts"]) == REQUIRED_BLOCKERS

    for field in REQUIRED_METRIC_FIELDS:
        assert field in text

    for blocker in REQUIRED_BLOCKERS:
        assert blocker in text


def test_contract_blocks_001b_false_positive_pattern():
    result = _read_json("result.json")
    anti_pattern = _read_json("anti_pattern_matrix.json")
    text = DOC.read_text(encoding="utf-8")

    assert set(result["blocks_001b_false_positive_pattern"]) == FALSE_POSITIVE_PATTERNS
    assert all(result["blocks_001b_false_positive_pattern"].values())

    anti_pattern_ids = {row["anti_pattern_id"] for row in anti_pattern["anti_patterns"]}
    assert FALSE_POSITIVE_PATTERNS - {"tests_that_assert_pass_rather_than_computation_path"} <= anti_pattern_ids

    required_terms = [
        "literal constants",
        "static dictionaries",
        "unconditional clean reports",
        "hash replay without behavior recomputation",
        "unused frozen seed families",
        "baseline names without callable baseline implementations",
        "tests that merely assert pass",
        "deserialize it through the same public path used by candidate behavior",
    ]
    for term in required_terms:
        assert term in text


def test_adoption_rule_blocks_future_executable_tasks_without_citation():
    adoption = _read_json("adoption_instructions.json")
    text = DOC.read_text(encoding="utf-8")

    assert adoption["must_cite"] == "COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A"
    assert adoption["block_if_missing_citation"] is True
    assert adoption["legacy_negative_evidence_preservation_exception"] is True
    assert "must cite" in text
    assert "block before execution" in text


def test_scope_flags_claim_ceiling_and_artifact_set_are_bounded():
    result = _read_json("result.json")
    claim_ceiling = (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip()

    assert EXPECTED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    assert result["verdict"] == "computed_evidence_provenance_contract_001a_created"
    assert result["claim_ceiling"] == "bounded repo-standard contract evidence only"
    assert claim_ceiling == result["claim_ceiling"]
    assert result["old_artifacts_modified"] is False
    assert result["experiments_rerun"] is False
    assert result["metric_count"] == 0
    assert all(value is False for value in result["authorization_flags"].values())
